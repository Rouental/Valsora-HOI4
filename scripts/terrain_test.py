"""TEST, not used by the build: terrain for the whole map, from each continent's
real-world model.

The author (2026-10-12): "DO NOT ADD IT TO THE MOD YET: try generating terrain for the
map based on the continents present ... Usnistan is based on the Middle East and Africa,
with lots of jungle and desert. Orientalis is based on Asia. Nonscio is based on western
Europe. Araseos is based on Germany. Yastreovakia is based on eastern Europe and Russia.
Solitas is very loosely based on the New World. Aislada is based on Australia." Then:
"Rouental and the Reibonnaise nations are in the Vale of Reibonne and are mostly
surrounded by mountains and hills, except the Reliette gap which is open plains. Try to
make the generated terrain logical, realistic, and consistent."

Nothing here feeds run_all.sh, the .pdn or the mod. It reads the current map (work/
from the last build) and writes work/terrain_test/ (terrain and relief arrays) and
dist/terrain_test_*.png (previews).

    python3 scripts/terrain_test.py      # ~1 min, deterministic

Each continent is worked on by itself, in its own frame:
  1. Relief (for this test only; the map's heightmap is still noise): land rises from
     the coast, with plateaus and basins from smooth noise, and ranges where the model
     puts them (the Alps, the Urals, the Himalaya and Tibet at Ganden, the Ethiopian
     highlands by Mekele, the Great Dividing Range ...), with peaks and passes along
     them and foothills either side. The Vale of Reibonne is the author's: a low floor,
     ringed by the ranges they drew on their fief map (source/vale_ranges.png) and by
     hills along the rest of its land border, open only at the Reliette gap. Every drawn
     river runs in a valley whose bed never rises downstream.
  2. Climate: a "latitude" per pixel from the continent's model (Yastreovakia runs from
     the Arctic to the Black Sea steppe, Usnistan from the Mediterranean to the Congo),
     giving temperature (less with height; western Europe's is milder) and a zonal rain
     belt (wet tropics, dry subtropics, wet mid-latitudes); the prevailing winds (trades
     from the east, westerlies from the west, monsoons where the model has them) carry
     the sea's moisture inland, losing it with distance and as rain on rising ground, so
     ranges cast rain shadows; a few hand-placed wet and dry areas (the Gobi, the
     outback); and more rain where rivers are drawn, since they need it.
  3. Terrain, as terrain.bmp palette indices: desert, steppe / savanna and plains,
     forest (taiga in the cold), jungle, hills and mountains from the relief, urban at
     the cities, irrigated strips along the rivers that cross dry land. Woods follow the
     land: farmland on low ground, along rivers and by the coast, woods on uplands and
     slopes and in a few large wooded regions, thinning out towards the steppe. Marsh
     only where water gathers: deltas, floodplains, lake shores, low wet coasts, boreal
     and tundra bogs, and Marais Verte.
  4. Each province's terrain in game is the type most of its pixels have (as the build
     reads the Terrain layer), so that is drawn too.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components, dijkstra
from skimage.draw import disk

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import CONTINENTS, COUNTRIES, TERRAIN_TYPES  # noqa: E402
from organic import fractal_noise  # noqa: E402
from usnistan_prototype import wiggle  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "work/terrain_test"
DIST = ROOT / "dist"
MARGIN = 40
DEBUG = {}  # the last continent's intermediate arrays, for tuning

# terrain classes: key -> (terrain.bmp palette index, label, preview colour)
CLASSES = {
    "plains":   (0, "Plains / farmland", (178, 196, 112)),
    "steppe":   (5, "Steppe / savanna (plains)", (218, 204, 134)),
    "forest":   (1, "Forest", (78, 136, 64)),
    "taiga":    (4, "Taiga, conifers (forest)", (46, 98, 70)),
    "jungle":   (21, "Jungle", (22, 92, 44)),
    "desert":   (3, "Desert, sand", (240, 222, 166)),
    "rocky":    (8, "Desert, rocky", (204, 170, 126)),
    "hills":    (2, "Hills", (166, 134, 94)),
    "mountain": (6, "Mountains", (120, 104, 96)),
    "snow":     (16, "Mountains, snow", (236, 236, 242)),
    "marsh":    (9, "Marsh", (98, 156, 144)),
    "urban":    (13, "Urban", (200, 40, 40)),
}
KEYS = list(CLASSES)
K = {k: i for i, k in enumerate(KEYS)}
for k, v in CLASSES.items():  # each index must be the HOI4 terrain type the class means
    assert TERRAIN_TYPES[v[0]] == {"steppe": "plains", "taiga": "forest", "rocky": "desert",
                                   "snow": "mountain"}.get(k, k), k
TYPE_COLOUR = {"plains": (190, 200, 120), "forest": (60, 120, 60), "jungle": (22, 92, 44),
               "desert": (232, 210, 150), "hills": (166, 134, 94), "mountain": (112, 96, 90),
               "marsh": (98, 156, 144), "urban": (200, 40, 40)}
SEA, LAKE, RIVER = (24, 46, 92), (70, 120, 200), (40, 90, 220)

# ---------------------------------------------------------------- the Vale of Reibonne
# The Reibonnaise nations' land. Its ranges are the ones the author drew on the Mountains
# layer of their fief map (Rouental_Map_TEMP_2.pdn, decoded in work/pdn_rmap), placed on
# the game map as in docs/ROUENTAL_FIEFS.md (FIEF_TO_GAME) and kept in
# source/vale_ranges.png: one colour per range, black elsewhere, its top-left pixel at
# VALE_ORIGIN on the game map.
REIBONNE = {"ROU", "SGN", "EVR", "HLR", "SGV", "LST", "LZC", "GDN"}
VALE_RANGES = {  # colour on the Mountains layer: (the author's name, height above the floor)
    (255, 0, 0): ("Osgrande Mountains", 62),
    (128, 128, 128): ("Bastionne Mountains", 66),
    (87, 0, 127): ("Nossine Mountains", 54),
    (0, 38, 255): ("Anarlaine Mountains", 54),
    (255, 216, 0): ("Hollier Mountains", 48),
    (76, 255, 0): ("Firime Highlands", 31),          # highlands: hills, not mountains
}
VALE_FILE = ROOT / "source/vale_ranges.png"
VALE_ORIGIN = (572, 747)
FIEF_TO_GAME = (0.0396, 572.1, 0.0379, 747.4)  # game x = a fx + b, y = c fy + d
RELIETTE_GAP = ((600, 824), 20, 34)  # open plains within the first radius, fading by the second
RIM = (26, 5)  # hills where the vale borders other land and no range was drawn: height, px

# ---------------------------------------------------------------- the continents' models
# lat: (y1, latitude there, y2, latitude there), linear between, in game pixels; tilt:
# latitude added per px eastwards; warm: degrees added (a warm current: western Europe).
# Ranges: (polyline of (x, y), half-width, height); domes: ((x, y), sigma, height;
# negative for a basin); plateaus: flat-topped domes; winds: the prevailing winds'
# (weight, reach in px over land): "E" the trades (and polar easterlies), "W" the
# westerlies; oro: how much of its moisture the air rains out per unit of rising ground
# (deserts' ranges cast deep rain shadows, Europe's don't); monsoon: extra moist air from
# that side ("S", "N", "E", "W"), with its weight, the latitudes it reaches and, if not
# 520, how far inland it rains (px); blobs:
# ((x, y), sigma, rain factor) for wetter (> 1) or drier (< 1) areas; marsh: forced fens
# ((x, y), radius); vale: the Vale of Reibonne is on this continent.
MODELS = {
    "nonscio": dict(  # western Europe: Scandinavia in the north to Iberia and Italy
        lat=(400, 62, 1550, 38), warm=3, rise=14, plateau=10, rain=1.0,
        winds=dict(E=(1.0, 650), W=(1.0, 1100)), oro=0.008,
        ranges=[
            ([(185, 560), (200, 680), (232, 790)], 22, 70),        # the Cascades (Cascadia)
            # the Alps: the Bastionne's southern end, down the bay's east shore to the Apennines
            ([(886, 866), (897, 912), (872, 958), (836, 990)], 18, 76),
            ([(385, 1062), (500, 1040), (622, 1052)], 18, 58),     # the Pyrenees
            ([(830, 985), (870, 1080), (902, 1180), (932, 1252)], 15, 46),  # the Apennines
            ([(1120, 640), (1190, 720), (1240, 820)], 18, 36),     # Kurikia's uplands
            ([(560, 1260), (640, 1300), (700, 1360)], 14, 30),     # Anglost's highlands
        ],
        domes=[((960, 1000), 55, 18), ((430, 1150), 70, 22),       # Massif Central, Meseta
               ((1040, 1080), 70, -6)],                            # Fraxhemark's lowland
        plateaus=[],
        monsoon=[],
        blobs=[((430, 1150), 90, 0.62), ((820, 1270), 80, 0.8), ((230, 680), 90, 1.25)],
        marsh=[((650, 812), 9)],                                   # Marais Verte
        vale=True,
    ),
    "araseos": dict(  # Germany: the northern plain, the central uplands, the Alps
        lat=(1330, 55, 2440, 47), warm=2, rise=12, plateau=8, rain=1.08,
        winds=dict(E=(1.0, 650), W=(1.0, 1100)), oro=0.008,
        ranges=[
            ([(560, 2185), (760, 2225), (960, 2205), (1160, 2150)], 28, 88),  # the Alps
            ([(690, 1885), (900, 1862)], 16, 32),                  # Thuringian Forest
            ([(345, 1890), (360, 1975), (385, 2060)], 18, 40),     # Black Forest
            ([(995, 1800), (1150, 1778)], 16, 30),                 # Ore Mountains
            ([(1320, 1880), (1360, 1980), (1330, 2080)], 18, 34),  # the eastern ranges
        ],
        domes=[((600, 1800), 35, 34), ((1100, 1910), 60, 20), ((250, 1700), 70, 12),
               ((820, 1760), 50, 16)],
        plateaus=[((800, 2120), 90, 14)],                          # the Bavarian plateau
        monsoon=[],
        blobs=[((260, 1460), 120, 1.1), ((1350, 2000), 120, 0.85)],
        marsh=[],
    ),
    "aislada": dict(  # Australia: tropical north, desert heart, Great Dividing Range
        lat=(1030, 10, 1425, 38), rise=10, plateau=8, rain=1.15,
        winds=dict(E=(1.0, 500), W=(1.0, 400)), oro=0.022,
        ranges=[([(2075, 1195), (1990, 1262), (1938, 1330), (1900, 1388)], 13, 36)],
        domes=[((1830, 1300), 50, 10)],
        plateaus=[],
        monsoon=[("N", 0.85, 20, 200), ("E", 0.5, 30, 110)],     # the Top End; the east coast
        blobs=[((1930, 1250), 65, 0.4)],                            # the outback, east of the rivers
        marsh=[],
    ),
    "solitas": dict(  # the New World, loosely: deserts west, jungle east, cordilleras
        lat=(1620, 25, 1980, 0), rise=12, plateau=10, rain=1.0,
        winds=dict(E=(1.0, 750), W=(1.0, 420)), oro=0.015,
        ranges=[
            ([(1500, 1690), (1555, 1795), (1600, 1905)], 22, 70),  # the western cordillera
            ([(1700, 1648), (1900, 1662), (2105, 1650)], 18, 46),  # the volcanic belt
            ([(1800, 1962), (1960, 1948), (2105, 1955)], 14, 38),  # the southern coast range
        ],
        domes=[((2250, 1800), 75, 24), ((1640, 1760), 70, 16)],
        plateaus=[((1600, 1780), 80, 16)],
        monsoon=[("E", 0.6, 30)],
        blobs=[((1600, 1770), 120, 0.55), ((2300, 1790), 110, 1.3), ((2450, 1730), 80, 1.3)],
        marsh=[],
    ),
    "yastreovakia": dict(  # eastern Europe and Russia: tundra and taiga to the steppe
        lat=(150, 72, 1150, 45), rise=10, plateau=9, rain=1.0,
        winds=dict(E=(1.0, 650), W=(1.0, 1500)), oro=0.008,
        ranges=[
            ([(2600, 160), (2585, 300), (2605, 470)], 20, 50),     # the Urals
            ([(2140, 600), (2250, 652), (2360, 640), (2410, 585)], 20, 56),  # the Carpathians
            ([(2455, 805), (2550, 790), (2650, 815)], 18, 74),     # the Caucasus
            ([(3300, 200), (3390, 340), (3350, 500)], 20, 54),     # the far eastern ranges
            ([(1880, 700), (1940, 800), (2000, 900)], 14, 36),     # the Dinaric coast
        ],
        domes=[((3050, 360), 110, 16), ((2550, 930), 60, 20)],
        plateaus=[],
        monsoon=[],
        blobs=[((2150, 800), 140, 0.72), ((2950, 450), 90, 1.15)],
        marsh=[((2900, 470), 30), ((2150, 560), 22)],
    ),
    "usnistan": dict(  # the Middle East and Africa: Mediterranean north, Sahara, Congo
        lat=(1152, 38.3, 1995, 0.0), rise=16, plateau=11, rain=1.0,
        winds=dict(E=(1.0, 650), W=(1.0, 420)), oro=0.022,
        ranges=[
            ([(2645, 1548), (2700, 1485), (2765, 1425), (2835, 1372)], 22, 85),  # the Atlas
            ([(2795, 1865), (2815, 1800), (2845, 1735)], 16, 32),  # the west coast line
            ([(3140, 2095), (3255, 2065), (3330, 2005)], 18, 38),  # the southern rim
            ([(2960, 1690), (3040, 1720)], 22, 30),                # the Hoggar ridge
        ],
        domes=[((3430, 1870), 72, 80), ((3020, 1705), 40, 62), ((3385, 1720), 34, 66),
               ((2760, 1260), 50, 22), ((3020, 1990), 95, -9), ((3080, 1630), 45, -6)],
        plateaus=[],
        monsoon=[("W", 0.9, 12)],
        blobs=[((3020, 1500), 260, 0.65), ((3000, 1960), 170, 1.35)],
        marsh=[],
    ),
    "orientalis": dict(  # Asia: taiga and the Gobi north, China, Tibet, the tropics south
        lat=(650, 55, 2370, 6), rise=12, plateau=12, rain=1.0,
        winds=dict(E=(1.0, 650), W=(0.35, 400)), oro=0.015,
        ranges=[
            ([(4335, 1832), (4430, 1882), (4525, 1888), (4625, 1852)], 20, 95),  # the Himalaya
            ([(4380, 1565), (4495, 1540), (4605, 1562)], 18, 58),  # the Kunlun
            ([(3880, 930), (3990, 900), (4120, 920)], 18, 56),     # the Altai
            ([(4300, 720), (4320, 850), (4290, 980)], 16, 40),     # the Greater Khingan
            ([(4560, 1600), (4590, 1700), (4610, 1790)], 14, 40),  # the Annamites
            ([(3800, 1560), (3790, 1760), (3810, 1960), (3790, 2140)], 16, 46),  # Chineasia's spine
            ([(4080, 1880), (4150, 2020), (4200, 2160)], 14, 38),  # Felter's ridge
            ([(4660, 1310), (4710, 1400), (4760, 1480)], 14, 40),  # Myehn's hills
        ],
        domes=[((4060, 1330), 45, 26), ((4250, 1470), 50, 30), ((4060, 1500), 50, 30),
               ((4330, 2040), 90, 20), ((4430, 1300), 70, 12)],
        plateaus=[((4480, 1760), 95, 55)],                          # Tibet, Ganden's
        monsoon=[("S", 0.95, 34), ("E", 0.65, 44)],
        blobs=[((3990, 1050), 170, 0.3), ((4500, 1440), 75, 0.6), ((4200, 1870), 80, 0.7),
               ((4650, 1200), 120, 1.3)],
        marsh=[],
    ),
}


def font(size, bold=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf"
                              % ("-Bold" if bold else ""), size)


def project_vale_ranges():
    """source/vale_ranges.png from the fief map's Mountains layer (work/pdn_rmap, decoded
    from Rouental_Map_TEMP_2.pdn with readpdn.py): a game pixel belongs to a range when
    40 % of its footprint is drawn, and takes the colour most of it shows; the names
    written on the ranges count as the range around them."""
    src = ROOT / "work/pdn_rmap"
    names = (src / "layers.txt").read_text(encoding="utf-8").splitlines()
    lay = np.load(src / f"layer{names.index('Mountains')}.npy", mmap_mode="r")
    fh, fw = lay.shape[:2]
    a, b, c, d = FIEF_TO_GAME
    gx = np.arange(VALE_ORIGIN[0], int(np.ceil(a * fw + b)))
    gy = np.arange(VALE_ORIGIN[1], int(np.ceil(c * fh + d)))
    sub = (np.arange(5) + 0.5) / 5                       # 5 x 5 samples per game pixel
    fx, fy = ((gx[:, None] + sub) - b) / a, ((gy[:, None] + sub) - d) / c
    inside = ((fy >= 0) & (fy < fh))[:, :, None, None] & ((fx >= 0) & (fx < fw))[None, None]
    s = np.asarray(lay[np.clip(fy.astype(int), 0, fh - 1).ravel()])
    s = s[:, np.clip(fx.astype(int), 0, fw - 1).ravel()].reshape(len(gy), 5, len(gx), 5, 4)
    cols = [np.array(col) for col in VALE_RANGES] + [np.array((255, 255, 255))]
    frac = np.stack([(inside & (s[..., 3] > 128) & (s[..., :3] == col).all(-1)).mean(axis=(1, 3))
                     for col in cols])
    drawn = frac.sum(0) >= 0.4
    named = frac[:-1].max(0) > 0
    iy, ix = ndi.distance_transform_edt(~named, return_distances=False, return_indices=True)
    best = frac[:-1].argmax(0)[iy, ix]
    out = np.zeros(best.shape + (3,), np.uint8)
    out[drawn] = np.array(list(VALE_RANGES), np.uint8)[best[drawn]]
    Image.fromarray(out).save(VALE_FILE)


def owner_map():
    """Each pixel's owner tag (None at sea), from the last build."""
    prov = np.load(ROOT / "work/provinces.npz")["prov"]
    state_of = np.load(ROOT / "work/regions.npz")["state_of"]
    owners = json.loads((ROOT / "work/regions.json").read_text(encoding="utf-8"))["owners"]
    tags = sorted(set(owners))
    code = np.array([tags.index(o) for o in owners] + [-1])  # state -1: no state
    return tags, code[state_of[prov]]


def vale_masks(tags, owner):
    """The vale (the Reibonnaise nations' land) and the author's ranges (index into
    VALE_RANGES, -1 elsewhere), map-sized."""
    vale = np.isin(owner, [i for i, t in enumerate(tags) if t in REIBONNE])
    if not VALE_FILE.exists():
        project_vale_ranges()
    img = np.asarray(Image.open(VALE_FILE).convert("RGB"))
    ranges = np.full(owner.shape, -1, np.int8)
    x0, y0 = VALE_ORIGIN
    box = ranges[y0:y0 + img.shape[0], x0:x0 + img.shape[1]]
    for i, col in enumerate(VALE_RANGES):
        box[(img == col).all(-1)] = i
    return vale, ranges


def sweep(land, h, direction, length, loss_k=0.022):
    """Moist air coming in from one side: 1 at the sea, fading over land (and lakes,
    which don't refill it) and losing some as rain wherever the ground rises. Each line
    of pixels is swept on its own, so the result is blurred across the wind, or a lake
    or a range's end shows as a straight streak. Returns (moisture, orographic rain)."""
    flip = {"E": (False, True), "W": (False, False), "S": (True, True), "N": (True, False)}
    trans, rev = flip[direction]
    L, Hh = (land.T, h.T) if trans else (land, h)
    if rev:
        L, Hh = L[:, ::-1], Hh[:, ::-1]
    n_r, n_c = L.shape
    m = np.ones(n_r)
    res = np.zeros((n_r, n_c))
    oro = np.zeros((n_r, n_c))
    decay = np.exp(-1 / length)
    for x in range(n_c):
        col = L[:, x]
        m = np.where(col, m * decay, 1.0)
        if x:
            dh = np.where(col, np.maximum(Hh[:, x] - Hh[:, x - 1], 0), 0)
            loss = np.minimum(m, loss_k * dh * m)
            oro[:, x] = loss
            m = m - loss
        res[:, x] = m
    if rev:
        res, oro = res[:, ::-1], oro[:, ::-1]
    res = ndi.gaussian_filter1d(res, 14, axis=0)
    oro = ndi.gaussian_filter1d(oro, 14, axis=0)
    return (res.T, oro.T) if trans else (res, oro)


def ramp(v, a, b):
    return np.clip((v - a) / (b - a), 0, 1)


def river_beds(river, water, h):
    """The height of each river pixel's bed, and its distance along the river from the
    mouth (the pixels touching water; for a river that reaches none, its end nearest
    the water). The bed rises upstream at most to halfway between a steady climb from
    the mouth and the ground beside it, and is never higher than any pixel upstream of
    it, so every river falls all the way to its mouth. Returns (ys, xs, bed, distance)."""
    ys, xs = np.nonzero(river)
    n = len(ys)
    idx = np.full(river.shape, -1)
    idx[ys, xs] = np.arange(n)
    a, b = [], []
    for dy, dx in ((0, 1), (1, 0)):  # rivers are edge-connected
        y2, x2 = ys + dy, xs + dx
        ok = (y2 < river.shape[0]) & (x2 < river.shape[1])
        j = idx[y2[ok], x2[ok]]
        a.append(np.nonzero(ok)[0][j >= 0])
        b.append(j[j >= 0])
    a, b = np.concatenate(a), np.concatenate(b)
    g = coo_matrix((np.ones(len(a)), (a, b)), shape=(n, n)).tocsr()
    near_water = ndi.binary_dilation(water, np.ones((3, 3), bool))[ys, xs]
    dwater = ndi.distance_transform_edt(~water)[ys, xs]
    _, comp = connected_components(g, directed=False)
    starts = set(np.nonzero(near_water)[0].tolist())
    for k in np.unique(comp):
        members = np.nonzero(comp == k)[0]
        if not near_water[members].any():
            starts.add(int(members[np.argmin(dwater[members])]))
    dist = dijkstra(g, directed=False, indices=sorted(starts), min_only=True)
    dist = np.where(np.isfinite(dist), dist, 0)
    ground = ndi.gaussian_filter(h, 3)[ys, xs]
    climb = 96.4 + 0.035 * dist
    bed = np.minimum(ground, climb + 0.5 * np.maximum(ground - climb, 0))
    nb = [[] for _ in range(n)]
    for i, j in zip(a.tolist(), b.tolist()):
        nb[i].append(j)
        nb[j].append(i)
    for i in np.argsort(-dist, kind="stable"):  # from the sources down
        for j in nb[i]:
            if dist[j] > dist[i]:
                bed[i] = min(bed[i], bed[j])
    return ys, xs, bed, dist


def continent(c, model, world, vale_all, cities, seed):
    land_full = world["cont"] == c
    ys, xs = np.nonzero(land_full)
    Y0, Y1 = max(ys.min() - MARGIN, 0), min(ys.max() + MARGIN + 1, land_full.shape[0])
    X0, X1 = max(xs.min() - MARGIN, 0), min(xs.max() + MARGIN + 1, land_full.shape[1])
    win = np.s_[Y0:Y1, X0:X1]
    land = land_full[win]
    H, W = land.shape
    kind = world["kind"][win]
    sea, lake = kind == 0, kind == 2
    water = sea | lake
    river = (world["rivers"][win] < 254) & land
    notsea = ~sea  # the air takes up moisture over the sea only

    def noise(scales, s):  # roughly -1..1 over the land
        n = fractal_noise((H, W), scales, seed * 100 + s)
        return (n - n[land].mean()) / (n[land].std() * 2.5 + 1e-9)

    yy, xx = np.mgrid[0:H, 0:W]
    gy, gx = yy + Y0, xx + X0
    dcoast = ndi.distance_transform_edt(land)

    # ------------------------------------------------------------ 1. relief
    dsm = ndi.gaussian_filter(dcoast, 12)
    h = 97 + model["rise"] * (1 - np.exp(-dsm / 110))
    h += model["plateau"] * noise([170, 70], 1) * np.clip(dcoast / 60, 0, 1)
    h += (3 + 0.12 * np.maximum(h - 100, 0)) * noise([30, 10, 4], 2)  # uplands more cut up
    ridged = (1 - np.abs(noise([45, 18, 7], 3))) ** 2
    vale = gap = None
    if model.get("vale"):
        vale = vale_all[0][win] & land
        vr = vale_all[1][win]
        # the vale's floor is low and gentle; the Reliette gap is low, open land both sides
        f = ndi.gaussian_filter(vale.astype(float), 5)
        h = h * (1 - f) + (97.6 + 0.3 * (h - 97)) * f
        (cx, cy), r_in, r_out = RELIETTE_GAP
        gap = np.clip((r_out - np.hypot(gx - cx, gy - cy)) / (r_out - r_in), 0, 1)
        h = h * (1 - gap) + (97.6 + 0.12 * (h - 97)) * gap
    for k, (pts, wid, hgt) in enumerate(model["ranges"]):
        path = wiggle([(p[1], p[0]) for p in pts], amp=18, corr=40, seed=seed * 10 + k,
                      shape=(H, W), off=(Y0, X0))
        m = np.zeros((H, W), bool)
        m[path[:, 0], path[:, 1]] = True
        d = ndi.distance_transform_edt(~m)
        warp = 1 + 0.35 * noise([25], 10 + k)
        along = 0.72 + 0.4 * noise([60, 22], 20 + k)        # peaks and passes along it
        h += hgt * along * (np.exp(-(d / (wid * warp)) ** 2) * (0.45 + 0.75 * ridged)
                            + 0.2 * np.exp(-(d / (2.8 * wid)) ** 2))  # and foothills
    for k, ((cx, cy), sig, hgt) in enumerate(model["domes"]):  # ragged, not round
        wy = gy + 0.5 * sig * noise([sig, sig / 3], 30 + k)
        wx = gx + 0.5 * sig * noise([sig, sig / 3], 40 + k)
        shape = np.exp(-((wy - cy) ** 2 + (wx - cx) ** 2) / (2.0 * sig ** 2))
        h += hgt * shape * ((0.55 + 0.6 * ridged) if hgt > 0 else 1)
    for k, ((cx, cy), sig, hgt) in enumerate(model["plateaus"]):
        r = np.sqrt((gy - cy) ** 2 + (gx - cx) ** 2) / sig * (1 + 0.25 * noise([sig / 2], 50 + k))
        h += hgt * np.exp(-r ** 6) * (0.85 + 0.25 * ridged)
    rise_v = np.zeros((H, W))
    if vale is not None:
        mod = 0.8 + 0.4 * ridged
        for i, (name, hgt) in enumerate(VALE_RANGES.values()):
            m = vr == i
            if not m.any():
                continue
            d_out = ndi.distance_transform_edt(~m)
            d_in = ndi.distance_transform_edt(m)
            crest = hgt * (1 + 0.14 * ramp(d_in, 0, 3)) * mod
            skirt = hgt * (0.75 * np.exp(-(d_out / 3.2) ** 2) + 0.12 * np.exp(-d_out / 6)) * mod
            rise_v += np.where(m, crest, skirt)
        # hills along the rest of the vale's land border, but not at the Reliette gap
        other = land & ~vale
        border = (vale & ndi.binary_dilation(other)) | (other & ndi.binary_dilation(vale))
        rim = (RIM[0] * np.exp(-(ndi.distance_transform_edt(~border) / RIM[1]) ** 2)
               * (0.75 + 0.5 * ridged) * (1 - gap))
        h += rise_v + np.maximum(rim - rise_v, 0)
    h_pre = h.copy()
    beds = None
    if river.any():  # every river in its valley
        ry, rx, bed, rdist = river_beds(river, water, h)
        zmap = np.zeros((H, W))
        zmap[ry, rx] = bed
        d, (iy, ix) = ndi.distance_transform_edt(~river, return_indices=True)
        z = zmap[iy, ix]
        h = np.where(land, z + (h - z) * (1 - np.exp(-d / 7)), h)
        beds = (ry, rx, bed, rdist)
    hf = np.where(land, np.maximum(h, 96.0), 94.0)

    # ------------------------------------------------------------ 2. climate
    ya, la, yb, lb = model["lat"]
    lat = la + (gy - ya) * (lb - la) / (yb - ya) + model.get("tilt", 0) * (gx - X0)
    lat = lat + 3.5 * noise([90, 35], 4)
    alat = np.abs(lat)
    temp = 27 + model.get("warm", 0) - 0.008 * alat ** 2 - 0.22 * np.maximum(hf - 100, 0)
    trades = 1 - ramp(alat, 26, 34)
    wester = ramp(alat, 27, 35) * (1 - 0.6 * ramp(alat, 60, 70))
    polar = 0.4 * ramp(alat, 62, 68)
    (we, le), (ww, lw) = model["winds"]["E"], model["winds"]["W"]
    sources = [("E", we * (trades + polar), le), ("W", ww * wester, lw)]
    for side, wgt, reach, *_ in model["monsoon"]:
        sources.append((side, wgt * (1 - ramp(alat, reach - 4, reach + 4)), 700))
    moist = np.zeros((H, W))
    oro = np.zeros((H, W))
    for side, wgt, length in sources:
        mm, oo = sweep(notsea, hf, side, length, model["oro"])
        moist = np.maximum(moist, wgt * mm)
        oro += wgt * oo
    oro = ndi.gaussian_filter(oro, 6) * 18
    mid_w = np.where(alat < 47, 20, 16)  # the westerlies' winter rain reaches the Mediterranean
    zonal = (1.0 * np.exp(-(alat / 9.5) ** 2) + 0.62 * np.exp(-((alat - 47) / mid_w) ** 2)
             + 0.15 * np.exp(-((alat - 15) / 5) ** 2))
    mon = np.zeros((H, W))
    for side, wgt, reach, *inland in model["monsoon"]:  # monsoons rain where the zonal belt is dry
        mm, _ = sweep(notsea, hf, side, (inland or [520])[0], model["oro"])
        mon = np.maximum(mon, 0.8 * wgt * mm * (1 - ramp(alat, reach - 4, reach + 4)))
    rain = zonal * (0.25 + 0.75 * moist) + mon
    rain = rain * (1 + 0.15 * noise([60], 5))
    rain += np.minimum(oro, 0.5) * np.clip(zonal * 2 + mon + 0.25, 0, 1)
    rain += 0.08 * np.exp(-dcoast / 20) * ((zonal + mon) > 0.15)
    for k, ((cx, cy), sig, f) in enumerate(model["blobs"]):  # ragged, not round
        r2 = ((gy - cy) ** 2 + (gx - cx) ** 2) / (2.0 * sig ** 2)
        g = np.exp(-r2 * (1 + 0.6 * noise([sig / 1.5, sig / 4], 70 + k)) ** 2)
        rain = rain * (1 + (f - 1) * g)
    rain += 4 * ndi.gaussian_filter(river.astype(float), 20)  # rivers were drawn where water is
    rain = ndi.gaussian_filter(rain * model["rain"], 4)
    rain = np.where(land, np.clip(rain, 0, 1.6), 0)

    # ------------------------------------------------------------ 3. terrain
    def local_std(a):
        return np.sqrt(np.maximum(ndi.uniform_filter(a ** 2, 9) - ndi.uniform_filter(a, 9) ** 2, 0))

    rough = local_std(np.where(land, h_pre, 94.0))  # valleys don't make hills
    patch = noise([22, 8], 6)        # small-scale variety
    region = noise([120, 45], 7)     # large-scale: wooded or open country, wet or dry ground
    warm = np.maximum(temp, 0)
    dry_t = 0.025 + 0.009 * warm            # below this: desert (the cold need less rain)
    grass_t = 0.04 + 0.021 * warm           # below this: steppe / savanna; taiga needs little
    wet = rain >= grass_t
    wetness = rain / grass_t - 1
    ter = np.full((H, W), K["plains"], np.uint8)
    ter[~wet] = K["steppe"]
    ter[~wet & (temp < 9)] = K["plains"]        # cool grassland, not savanna
    desert = rain < dry_t
    ter[desert] = K["desert"]
    ter[desert & ((hf > 116) | (rough > 2.5) | (patch > 0.3))] = K["rocky"]
    ter[desert & (temp < 3)] = K["plains"]       # cold and dry: tundra, not desert
    # woods: on uplands and slopes and in a few large wooded regions; farmland on low
    # ground, along rivers and by the coast; fewer where it is barely wet enough for trees
    slope = ndi.gaussian_filter(np.hypot(*np.gradient(hf)), 2)
    driver = ndi.distance_transform_edt(~river)
    lw = ndi.gaussian_filter(land.astype(float), 40)
    rel = hf - ndi.gaussian_filter(np.where(land, hf, 0), 40) / np.maximum(lw, 1e-3)  # above the land around
    woods = (0.55 * region + 0.4 * patch + 0.05 * np.clip(rel, -2.5, 14) + 0.3 * ramp(hf, 108, 132)
             + 0.4 * ramp(slope, 0.4, 1.6) - 0.4 * np.exp(-driver / 4) - 0.25 * np.exp(-dcoast / 8))
    need = -0.45 + 0.48 * ramp(temp, 0, 5) + 0.45 * (1 - ramp(wetness, 0, 0.8))
    DEBUG.update(woods=woods, need=need, wet=wet, temp=temp, rel=rel, region=region, patch=patch)
    forest = wet & (woods > need)
    ter[forest & (temp >= 2.5)] = K["forest"]
    ter[forest & (temp < 2.5)] = K["taiga"]
    ter[wet & (temp < -9) & (woods < need + 0.5)] = K["plains"]  # tundra
    # the tropics: rainforest where it is wet all year, savanna where barely wet enough,
    # dry forest and farmland between
    tropic = wet & (temp > 21.5)
    jungle = tropic & (rain > grass_t + 0.16 + 0.18 * patch + 0.15 * region)
    ter[jungle] = K["jungle"]
    ter[tropic & ~jungle & (rain < grass_t + 0.1 + 0.08 * patch) & (woods < need + 0.35)] = K["steppe"]
    # marsh: where water gathers on flat, low, wet ground
    flat = rough < 1.0
    wetc = wetness > 0.25
    dsea = ndi.distance_transform_edt(~sea)
    dlake = ndi.distance_transform_edt(~lake)
    mouth = river & (dsea <= 2)
    dmouth = ndi.distance_transform_edt(~mouth) if mouth.any() else np.full((H, W), 1e9)
    marsh = land & flat & wetc & (
        ((hf < 100.5) & (dmouth < 9 + 6 * patch))                      # deltas
        | ((hf < 100.5) & (driver < 3 + 3 * patch) & (region < -0.1))  # floodplains
        | ((hf < 101) & (dlake < 4 + 5 * patch) & (patch > 0))         # lake shores
        | ((hf < 99) & (dsea < 9) & (region < -0.45) & (patch > -0.1))  # low coasts
        | ((temp < 3) & (hf < 104) & (rel < -1.5) & (region < -0.1) & (patch > -0.2)))  # boreal bogs
    marsh |= land & flat & (temp < -4) & (hf < 103) & (rel < -1) & (patch > 0.2)  # tundra bogs
    for (cx, cy), rad in model["marsh"]:
        r = np.sqrt((gy - cy) ** 2 + (gx - cx) ** 2) / (rad * (1 + 0.6 * noise([rad / 2, rad / 5], 60)))
        marsh |= land & (r < 1)
    ter[marsh] = K["marsh"]
    # relief wins over vegetation
    hilly = (hf >= 122) | (rough > 2.5)
    mount = (hf >= 152) | ((hf >= 140) & (rough > 3.3))
    ter[hilly & ~mount] = K["hills"]
    ter[mount] = K["mountain"]
    ter[mount & ((temp < -10.5) | (hf > 205))] = K["snow"]
    # rivers through dry land, and lake shores in it: green ribbons and oases
    ter[np.isin(ter, [K["desert"], K["rocky"], K["steppe"]]) & ((driver <= 3) | (dlake <= 3))] = K["plains"]
    if gap is not None:  # the Reliette gap: open plains
        ter[land & (gap > 0.5) & (rise_v < 12)] = K["plains"]
    for cx, cy in cities:
        if Y0 <= cy < Y1 and X0 <= cx < X1 and land[cy - Y0, cx - X0]:
            rr, cc = disk((cy - Y0, cx - X0), 3.5, shape=(H, W))
            ter[rr, cc] = np.where(land[rr, cc], K["urban"], ter[rr, cc])
    return win, land, ter, hf, rain, temp, beds


def hillshade(hf):
    gy, gx = np.gradient(ndi.gaussian_filter(hf, 1.2))
    nx, ny, nz = -gx * 0.9, -gy * 0.9, np.ones_like(hf)
    n = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
    light = np.array([-0.6, -0.6, 0.55])
    light /= np.linalg.norm(light)
    return (nx * light[0] + ny * light[1] + nz * light[2]) / n


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    world = np.load(ROOT / "work/world.npz")
    kind = world["kind"]
    Hm, Wm = kind.shape
    cities = [tuple(map(int, k.split(","))) for k in
              json.loads((ROOT / "source/city_names.json").read_text(encoding="utf-8"))]
    tags, owner = owner_map()
    vale_all = vale_masks(tags, owner)
    terrain = np.full((Hm, Wm), 255, np.uint8)
    relief = np.where(kind == 0, 90.0, 94.0)
    for c, name in enumerate(CONTINENTS, 1):
        win, land, ter, hf, rain, temp, beds = continent(c, MODELS[name], world, vale_all, cities, c)
        terrain[win][land] = ter[land]
        relief[win][land] = hf[land]
        msg = ""
        if beds is not None:
            ry, rx, bed, rdist = beds
            msg = f", {len(ry)} river px, beds {bed.min():.1f} to {bed.max():.1f}"
        print(f"{name}: {land.sum()} px, rain {rain[land].mean():.2f}, "
              f"temperature {temp[land].min():.0f} to {temp[land].max():.0f}{msg}")
    land_all = kind == 1
    miss = land_all & (terrain == 255)
    if miss.any():  # land on no continent: the nearest terrain
        iy, ix = ndi.distance_transform_edt(terrain == 255, return_distances=False,
                                            return_indices=True)
        terrain[miss] = terrain[iy[miss], ix[miss]]
    np.save(OUT / "terrain_class.npy", terrain)
    np.save(OUT / "relief.npy", relief.astype(np.float32))
    idx = np.array([CLASSES[k][0] for k in KEYS] + [15], np.uint8)
    np.save(OUT / "terrain_index.npy", np.where(land_all, idx[np.minimum(terrain, len(KEYS))],
                                                 np.where(kind == 2, 14, 15)).astype(np.uint8))

    # ------------------------------------------------------------ each province's type
    prov = np.load(ROOT / "work/provinces.npz")["prov"]
    types = sorted(TYPE_COLOUR)
    ctype = np.array([types.index(TERRAIN_TYPES[CLASSES[k][0]]) for k in KEYS])
    tmap = np.where(land_all, ctype[np.minimum(terrain, len(KEYS) - 1)], -1)
    n = prov.max() + 1
    counts = np.zeros((n, len(types)), np.int64)
    np.add.at(counts, (prov[land_all], tmap[land_all]), 1)
    ptype = counts.argmax(1)
    pland = counts.sum(1) > 0

    # ------------------------------------------------------------ statistics
    cont = world["cont"]
    stats = {}
    for c, name in enumerate(CONTINENTS, 1):
        m = cont == c
        px = np.bincount(tmap[m & land_all], minlength=len(types))
        ps = np.unique(prov[m & land_all])
        pv = np.bincount(ptype[ps], minlength=len(types))
        stats[name] = (px / max(px.sum(), 1), pv / max(pv.sum(), 1))
    vale = vale_all[0] & (cont == CONTINENTS.index("nonscio") + 1)  # not Rouental's islets
    pv = np.bincount(ptype[np.unique(prov[vale])], minlength=len(types))
    stats["vale of reibonne"] = (np.bincount(tmap[vale], minlength=len(types)) / vale.sum(),
                                 pv / pv.sum())
    (OUT / "stats.json").write_text(json.dumps(
        {k: {"pixels": dict(zip(types, map(float, a))), "provinces": dict(zip(types, map(float, b)))}
         for k, (a, b) in stats.items()}, indent=1))

    # ------------------------------------------------------------ previews
    s = 2
    pal = np.array([CLASSES[k][2] for k in KEYS], float)
    rgb = np.zeros((Hm, Wm, 3))
    rgb[land_all] = pal[terrain[land_all]]
    shade = hillshade(relief)
    rgb[land_all] *= np.clip(0.72 + 0.42 * shade[land_all], 0.45, 1.15)[:, None]
    rgb[kind == 0] = SEA
    rgb[kind == 2] = LAKE
    rgb[world["rivers"] < 254] = RIVER
    big = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))
    small = big.resize((Wm // s, Hm // s), Image.LANCZOS)
    legend = [(CLASSES[k][2], f"{CLASSES[k][1]}  [{CLASSES[k][0]}]") for k in KEYS]
    sheet(small, "Valsora: terrain test (not in the mod)",
          "Generated from each continent's real-world model; hill shading from the test's own relief",
          legend, DIST / "terrain_test_map.png", world, s)

    prgb = np.zeros((Hm, Wm, 3))
    tcol = np.array([TYPE_COLOUR[t] for t in types], float)
    pt = np.where(pland, ptype, 0)
    prgb[land_all] = tcol[pt[prov[land_all]]]
    edge = np.zeros((Hm, Wm), bool)
    edge[:-1] |= prov[:-1] != prov[1:]
    edge[:, :-1] |= prov[:, :-1] != prov[:, 1:]
    prgb[edge & land_all] *= 0.82
    prgb[kind == 0] = SEA
    prgb[kind == 2] = LAKE
    pbig = Image.fromarray(np.clip(prgb, 0, 255).astype(np.uint8))
    psmall = pbig.resize((Wm // s, Hm // s), Image.LANCZOS)
    rows = []
    for name in CONTINENTS:
        a, b = stats[name]
        rows.append(name.title() + ": " + ", ".join(f"{t} {100 * b[i]:.0f} %" for i, t in
                                                   sorted(enumerate(types), key=lambda q: -b[q[0]])
                                                   if b[i] >= 0.005))
    sheet(psmall, "Valsora: terrain test, by province (what the game would use)",
          "Each province takes the type most of its pixels have", [(TYPE_COLOUR[t], t) for t in types],
          DIST / "terrain_test_provinces.png", world, s, rows)
    vale_sheet(big, pbig, tags, owner, vale_all, stats["vale of reibonne"], types,
               DIST / "terrain_test_vale.png")

    for name, (x0, y0, x1, y1) in {"usnistan": (2380, 1130, 3720, 2450),
                                    "orientalis": (3440, 630, 5090, 2390),
                                    "nonscio": (0, 380, 1640, 1580),
                                    "araseos": (80, 1300, 1700, 2460),
                                    "yastreovakia": (1390, 90, 3560, 1180),
                                    "solitas_aislada": (1420, 1010, 2640, 2040)}.items():
        crop = big.crop((x0, y0, x1, y1))
        f = max(1, int(np.ceil(max(x1 - x0, y1 - y0) / 1700)))
        crop = crop.resize(((x1 - x0) // f, (y1 - y0) // f), Image.LANCZOS)
        crop.save(OUT / f"zoom_{name}.png")
    print("wrote dist/terrain_test_map.png, dist/terrain_test_provinces.png, "
          "dist/terrain_test_vale.png, work/terrain_test/")


def vale_sheet(big, pbig, tags, owner, vale_all, vstats, types, out):
    """The Vale of Reibonne up close, by pixel and by province, with the countries'
    borders, the author's ranges and the Reliette gap named."""
    x0, y0, x1, y1 = 548, 712, 932, 940
    s = 3
    names = {v[0]: v[1] for v in COUNTRIES.values()}
    own = owner[y0:y1, x0:x1]
    line = np.zeros(own.shape, bool)
    line[:-1] |= (own[:-1] != own[1:]) & (own[:-1] >= 0) & (own[1:] >= 0)
    line[:, :-1] |= (own[:, :-1] != own[:, 1:]) & (own[:, :-1] >= 0) & (own[:, 1:] >= 0)
    line = np.kron(line, np.ones((s, s), bool))
    vr = vale_all[1][y0:y1, x0:x1]
    labels = []
    for i, (name, _) in enumerate(VALE_RANGES.values()):
        yy, xx = np.nonzero(vr == i)
        if len(yy):
            k = np.argmin((yy - yy.mean()) ** 2 + (xx - xx.mean()) ** 2)
            labels.append((name, xx[k], yy[k], font(17, True)))
    (gx, gy), _, _ = RELIETTE_GAP
    labels.append(("Reliette gap", gx - x0, gy - y0, font(17, True)))
    for t in sorted(set(own[own >= 0].tolist())):
        lab, n = ndi.label(own == t)
        if not n:
            continue
        big_part = np.argmax(ndi.sum(own == t, lab, range(1, n + 1))) + 1
        yy, xx = np.nonzero(lab == big_part)
        if len(yy) > 150:
            k = np.argmin((yy - np.median(yy)) ** 2 + (xx - np.median(xx)) ** 2)
            x, y = xx[k], yy[k]
            while any(abs(x - lx) < 30 and abs(y - ly) < 7 for _, lx, ly, _ in labels):
                y += 7  # clear of the range names
            labels.append((names.get(tags[t], tags[t]), x, y, font(13)))
    panels = []
    for img in (big, pbig):
        a = np.asarray(img.crop((x0, y0, x1, y1)).resize(((x1 - x0) * s, (y1 - y0) * s),
                                                          Image.NEAREST)).copy()
        a[line] = (a[line] * 0.35).astype(np.uint8)
        p = Image.fromarray(a)
        d = ImageDraw.Draw(p)
        for text, x, y, f in labels:
            d.text((x * s, y * s), text, font=f, fill=(255, 255, 255), anchor="mm",
                   stroke_width=3, stroke_fill=(0, 0, 0))
        panels.append(p)
    pw, ph = panels[0].size
    head = 70
    canvas = Image.new("RGB", (pw, 2 * ph + 3 * head), (24, 26, 30))
    d = ImageDraw.Draw(canvas)
    a, b = vstats
    for k, (p, title) in enumerate(zip(panels, (
            "The Vale of Reibonne: terrain test (not in the mod), by pixel",
            "The same, by province (each takes the type most of its pixels have)"))):
        y = k * (ph + head)
        d.text((20, y + 14), title, font=font(22, True), fill=(240, 220, 160))
        sub = ("Ranges as the author drew them on the fief map; hills along the rest of the "
               "vale's land border; the Reliette gap open plains" if k == 0 else
               "Reibonnaise provinces: " + ", ".join(
                   f"{t} {100 * b[i]:.0f} %" for i, t in sorted(enumerate(types), key=lambda q: -b[q[0]])
                   if b[i] >= 0.005))
        d.text((20, y + 44), sub, font=font(15), fill=(180, 180, 180))
        canvas.paste(p, (0, y + head))
    y = 2 * (ph + head) + 8
    legend = [(CLASSES[k][2], CLASSES[k][1]) for k in KEYS]
    colw = (pw - 40) // 4
    for i, (col, label) in enumerate(legend):
        cx, cy = 20 + (i % 4) * colw, y + (i // 4) * 20
        d.rectangle([cx, cy + 3, cx + 22, cy + 15], fill=tuple(col), outline=(0, 0, 0))
        d.text((cx + 30, cy + 1), label, font=font(14), fill=(230, 230, 230))
    canvas = canvas.crop((0, 0, pw, y + 3 * 20 + 10))
    canvas.save(out, optimize=True)


def sheet(img, title, subtitle, legend, out, world, s, rows=()):
    pad, lh = 24, 22
    leg_cols = 4
    leg_rows = -(-len(legend) // leg_cols)
    extra = 90 + leg_rows * lh + len(rows) * 20 + (12 if rows else 0)
    canvas = Image.new("RGB", (img.width, img.height + extra), (24, 26, 30))
    canvas.paste(img, (0, 0))
    d = ImageDraw.Draw(canvas)
    cont = world["cont"]
    for c, name in enumerate(CONTINENTS, 1):
        ys, xs = np.nonzero(cont[::8, ::8] == c)
        if len(ys):
            d.text((int(np.median(xs)) * 8 // s, int(np.median(ys)) * 8 // s), name.title(),
                   font=font(22, True), fill=(255, 255, 255), anchor="mm",
                   stroke_width=3, stroke_fill=(0, 0, 0))
    y = img.height + 14
    d.text((pad, y), title, font=font(24, True), fill=(240, 220, 160))
    d.text((pad, y + 32), subtitle, font=font(15), fill=(170, 170, 170))
    y += 62
    colw = (img.width - 2 * pad) // leg_cols
    for i, (col, label) in enumerate(legend):
        cx, cy = pad + (i % leg_cols) * colw, y + (i // leg_cols) * lh
        d.rectangle([cx, cy + 3, cx + 26, cy + 17], fill=tuple(int(v) for v in col), outline=(0, 0, 0))
        d.text((cx + 34, cy + 2), label, font=font(15), fill=(230, 230, 230))
    y += leg_rows * lh + 12
    for r in rows:
        d.text((pad, y), r, font=font(15), fill=(200, 200, 200))
        y += 20
    canvas.save(out, optimize=True)


if __name__ == "__main__":
    main()
