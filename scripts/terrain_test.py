"""TEST, not used by the build: terrain for the whole map, from each continent's
real-world model.

The author (2026-10-12): "DO NOT ADD IT TO THE MOD YET: try generating terrain for the
map based on the continents present ... Usnistan is based on the Middle East and Africa,
with lots of jungle and desert. Orientalis is based on Asia. Nonscio is based on western
Europe. Araseos is based on Germany. Yastreovakia is based on eastern Europe and Russia.
Solitas is very loosely based on the New World. Aislada is based on Australia."

Nothing here feeds run_all.sh, the .pdn or the mod. It reads the current map (work/
from the last build) and writes work/terrain_test/ (terrain and relief arrays) and
dist/terrain_test_*.png (previews).

    python3 scripts/terrain_test.py      # ~2 min, deterministic

Each continent is worked on by itself, in its own frame:
  1. Relief (for this test only; the map's heightmap is still noise): land rises from
     the coast, with plateaus and basins from smooth noise, and hand-placed ranges and
     domes where the model puts them (the Alps between "France" and "Italy", the Urals,
     the Himalaya and Tibet at Ganden, the Ethiopian highlands by Mekele, the Great
     Dividing Range ...), and Rouental's own: the Duchy of the Mountains, Glacierre,
     Rochemont, Aureimontes.
  2. Climate: a "latitude" per pixel from the continent's model (Yastreovakia runs from
     the Arctic to the Black Sea steppe, Usnistan from the Mediterranean to the Congo),
     giving temperature (less with height) and a zonal rain belt (wet tropics, dry
     subtropics, wet mid-latitudes); the prevailing winds (trades from the east,
     westerlies from the west, monsoons where the model has them) carry the sea's
     moisture inland, losing it with distance and as rain on rising ground, so ranges
     cast rain shadows; and a few hand-placed wet and dry areas (the Gobi, the outback).
  3. Terrain, as terrain.bmp palette indices: desert, steppe / savanna and plains,
     forest (taiga in the cold), jungle, marsh (wet flat lowlands, deltas, boreal fens,
     Marais Verte), hills and mountains from the relief, urban at the cities, irrigated
     strips along the rivers that cross dry land.
  4. Each province's terrain in game is the type most of its pixels have (as the build
     reads the Terrain layer), so that is drawn too.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi
from skimage.draw import disk

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import CONTINENTS, TERRAIN_TYPES  # noqa: E402
from organic import fractal_noise  # noqa: E402
from usnistan_prototype import wiggle  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "work/terrain_test"
DIST = ROOT / "dist"
MARGIN = 40

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

# ---------------------------------------------------------------- the continents' models
# lat: (y1, latitude there, y2, latitude there), linear between, in game pixels; tilt:
# latitude added per px eastwards. Ranges: (polyline of (x, y), half-width, height);
# domes: ((x, y), sigma, height; negative for a basin); plateaus: flat-topped domes;
# winds: the prevailing winds' (weight, reach in px over land): "E" the trades (and
# polar easterlies), "W" the westerlies; oro: how much of its moisture the air rains
# out per unit of rising ground (deserts' ranges cast deep rain shadows, Europe's
# don't); monsoon: extra moist air from that side ("S", "N", "E", "W"), with its
# weight and the latitudes it reaches; blobs: ((x, y), sigma, rain factor) for wetter
# (> 1) or drier (< 1) areas; marsh: forced fens ((x, y), radius).
MODELS = {
    "nonscio": dict(  # western Europe: Scandinavia in the north to Iberia and Italy
        lat=(400, 62, 1550, 38), rise=14, plateau=10, rain=1.0,
        winds=dict(E=(1.0, 650), W=(1.0, 1100)), oro=0.008,
        ranges=[
            ([(185, 560), (200, 680), (232, 790)], 22, 70),        # the Cascades (Cascadia)
            ([(615, 930), (720, 965), (820, 945), (905, 905)], 26, 85),  # the Alps
            ([(385, 1062), (500, 1040), (622, 1052)], 18, 58),     # the Pyrenees
            ([(830, 985), (870, 1080), (902, 1180), (932, 1252)], 15, 46),  # the Apennines
            ([(1120, 640), (1190, 720), (1240, 820)], 18, 36),     # Kurikia's uplands
            ([(560, 1260), (640, 1300), (700, 1360)], 14, 30),     # Anglost's highlands
        ],
        domes=[((672, 850), 18, 48), ((660, 786), 8, 38), ((723, 829), 8, 26),
               ((588, 804), 10, 30),                               # Rouental's mountains
               ((960, 1000), 55, 18), ((430, 1150), 70, 22),       # Massif Central, Meseta
               ((1040, 1080), 70, -6)],                            # Fraxhemark's lowland
        plateaus=[],
        monsoon=[],
        blobs=[((430, 1150), 90, 0.62), ((820, 1270), 80, 0.8), ((230, 680), 90, 1.25)],
        marsh=[((650, 812), 9), ((741, 862), 6)],
    ),
    "araseos": dict(  # Germany: the northern plain, the central uplands, the Alps
        lat=(1330, 55, 2440, 47), rise=12, plateau=8, rain=1.08,
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
        monsoon=[("N", 0.85, 26), ("E", 0.5, 30)],
        blobs=[((1835, 1290), 70, 0.5)],
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
        blobs=[((3020, 1500), 260, 0.75), ((3000, 1960), 170, 1.35)],
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


def continent(c, model, world, cities, seed):
    land_full = world["cont"] == c
    ys, xs = np.nonzero(land_full)
    Y0, Y1 = max(ys.min() - MARGIN, 0), min(ys.max() + MARGIN + 1, land_full.shape[0])
    X0, X1 = max(xs.min() - MARGIN, 0), min(xs.max() + MARGIN + 1, land_full.shape[1])
    win = np.s_[Y0:Y1, X0:X1]
    land = land_full[win]
    H, W = land.shape
    river = world["rivers"][win] < 254
    notsea = world["kind"][win] != 0  # the air takes up moisture over the sea only

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
    h += 3 * noise([30, 10, 4], 2)
    ridged = (1 - np.abs(noise([45, 18, 7], 3))) ** 2
    for k, (pts, wid, hgt) in enumerate(model["ranges"]):
        path = wiggle([(p[1], p[0]) for p in pts], amp=18, corr=40, seed=seed * 10 + k,
                      shape=(H, W), off=(Y0, X0))
        m = np.zeros((H, W), bool)
        m[path[:, 0], path[:, 1]] = True
        d = ndi.distance_transform_edt(~m)
        warp = 1 + 0.35 * noise([25], 10 + k)
        h += hgt * np.exp(-(d / (wid * warp)) ** 2) * (0.45 + 0.75 * ridged)
    for k, ((cx, cy), sig, hgt) in enumerate(model["domes"]):
        r2 = ((gy - cy) ** 2 + (gx - cx) ** 2) / (2.0 * sig ** 2)
        shape = np.exp(-r2 * (1 + 0.4 * noise([sig], 30 + k)))
        h += hgt * shape * ((0.55 + 0.6 * ridged) if hgt > 0 else 1)
    for k, ((cx, cy), sig, hgt) in enumerate(model["plateaus"]):
        r = np.sqrt((gy - cy) ** 2 + (gx - cx) ** 2) / sig * (1 + 0.25 * noise([sig / 2], 50 + k))
        h += hgt * np.exp(-r ** 6) * (0.85 + 0.25 * ridged)
    hf = np.where(land, np.maximum(h, 96.0), 94.0)

    # ------------------------------------------------------------ 2. climate
    ya, la, yb, lb = model["lat"]
    lat = la + (gy - ya) * (lb - la) / (yb - ya) + model.get("tilt", 0) * (gx - X0)
    lat = lat + 3.5 * noise([90, 35], 4)
    alat = np.abs(lat)
    temp = 27 - 0.008 * alat ** 2 - 0.22 * np.maximum(hf - 100, 0)
    trades = 1 - ramp(alat, 26, 34)
    wester = ramp(alat, 30, 38) * (1 - 0.6 * ramp(alat, 60, 70))
    polar = 0.4 * ramp(alat, 62, 68)
    (we, le), (ww, lw) = model["winds"]["E"], model["winds"]["W"]
    sources = [("E", we * (trades + polar), le), ("W", ww * wester, lw)]
    for side, wgt, reach in model["monsoon"]:
        sources.append((side, wgt * (1 - ramp(alat, reach - 4, reach + 4)), 700))
    moist = np.zeros((H, W))
    oro = np.zeros((H, W))
    for side, wgt, length in sources:
        mm, oo = sweep(notsea, hf, side, length, model["oro"])
        moist = np.maximum(moist, wgt * mm)
        oro += wgt * oo
    oro = ndi.gaussian_filter(oro, 6) * 18
    zonal = (1.0 * np.exp(-(alat / 9.5) ** 2) + 0.62 * np.exp(-((alat - 47) / 16) ** 2)
             + 0.15 * np.exp(-((alat - 15) / 5) ** 2))
    mon = np.zeros((H, W))
    for side, wgt, reach in model["monsoon"]:  # monsoons rain where the zonal belt is dry
        mm, _ = sweep(notsea, hf, side, 520, model["oro"])
        mon = np.maximum(mon, 0.8 * wgt * mm * (1 - ramp(alat, reach - 4, reach + 4)))
    rain = zonal * (0.25 + 0.75 * moist) + mon
    rain = rain * (1 + 0.15 * noise([60], 5))
    rain += np.minimum(oro, 0.5) * np.clip(zonal * 2 + mon + 0.25, 0, 1)
    rain += 0.08 * np.exp(-dcoast / 20) * ((zonal + mon) > 0.15)
    for k, ((cx, cy), sig, f) in enumerate(model["blobs"]):  # ragged, not round
        r2 = ((gy - cy) ** 2 + (gx - cx) ** 2) / (2.0 * sig ** 2)
        g = np.exp(-r2 * (1 + 0.6 * noise([sig / 1.5, sig / 4], 70 + k)) ** 2)
        rain = rain * (1 + (f - 1) * g)
    rain = ndi.gaussian_filter(rain * model["rain"], 4)
    rain = np.where(land, np.clip(rain, 0, 1.6), 0)

    # ------------------------------------------------------------ 3. terrain
    rough = np.sqrt(np.maximum(ndi.uniform_filter(hf ** 2, 15) - ndi.uniform_filter(hf, 15) ** 2, 0))
    patch = noise([22, 8], 6)
    warm = np.maximum(temp, 0)
    dry_t = 0.04 + 0.010 * warm             # below this: desert (the cold need less rain)
    grass_t = 0.07 + 0.019 * warm           # below this: steppe / savanna
    ter = np.full((H, W), K["plains"], np.uint8)
    ter[rain < grass_t] = K["steppe"]
    ter[(rain < grass_t) & (temp < 9)] = K["plains"]        # cool grassland, not savanna
    ter[rain < dry_t] = K["desert"]
    ter[(rain < dry_t) & ((hf > 118) | (patch > 0.25))] = K["rocky"]
    ter[(rain < dry_t) & (temp < 3)] = K["plains"]           # cold and dry: tundra, not desert
    wet = rain >= grass_t
    ter[wet & (patch > 0.12) & (temp >= 2)] = K["forest"]    # farmland and woods
    ter[wet & (patch > -0.35) & (temp < 2)] = K["taiga"]
    ter[wet & (temp < -6) & (patch < 0.2)] = K["plains"]     # tundra
    jungle = wet & (temp > 21.5) & (rain > grass_t + 0.12 + 0.1 * patch)
    ter[jungle] = K["jungle"]
    ter[wet & (temp > 21.5) & ~jungle & (patch < -0.2)] = K["steppe"]
    # wet, flat lowlands: fens, deltas, lake and river shores; boreal bogs
    water = ~land
    dwater = ndi.distance_transform_edt(~(water | river))
    lowflat = (hf < 101.5) & (rough < 1.4)
    fen = lowflat & wet & (dwater < 10 + 8 * patch) & (patch > 0.3)
    bog = (hf < 104) & (temp < 3) & wet & (patch < -0.42) & (rough < 2)
    ter[land & (fen | bog)] = K["marsh"]
    for (cx, cy), rad in model["marsh"]:
        r = np.sqrt((gy - cy) ** 2 + (gx - cx) ** 2) / (rad * (1 + 0.6 * noise([rad / 2, rad / 5], 60)))
        ter[land & (r < 1)] = K["marsh"]
    ter[land & (temp < -4) & (hf < 103) & (patch > 0.3) & (rough < 2)] = K["marsh"]  # tundra bogs
    # relief wins over vegetation
    hilly = (hf >= 128) | (rough > 4.2)
    mount = (hf >= 152) | ((hf >= 140) & (rough > 5.5))
    ter[hilly & ~mount] = K["hills"]
    ter[mount] = K["mountain"]
    ter[mount & ((temp < -9) | (hf > 205))] = K["snow"]
    # rivers through dry land: green ribbons
    driver = ndi.distance_transform_edt(~river)
    ter[np.isin(ter, [K["desert"], K["rocky"], K["steppe"]]) & (driver <= 3)] = K["plains"]
    for cx, cy in cities:
        if Y0 <= cy < Y1 and X0 <= cx < X1 and land[cy - Y0, cx - X0]:
            rr, cc = disk((cy - Y0, cx - X0), 3.5, shape=(H, W))
            ter[rr, cc] = np.where(land[rr, cc], K["urban"], ter[rr, cc])
    return win, land, ter, hf, rain, temp


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
    terrain = np.full((Hm, Wm), 255, np.uint8)
    relief = np.where(kind == 0, 90.0, 94.0)
    for c, name in enumerate(CONTINENTS, 1):
        win, land, ter, hf, rain, temp = continent(c, MODELS[name], world, cities, c)
        terrain[win][land] = ter[land]
        relief[win][land] = hf[land]
        print(f"{name}: {land.sum()} px, rain {rain[land].mean():.2f}, "
              f"temperature {temp[land].min():.0f} to {temp[land].max():.0f}")
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
    psmall = Image.fromarray(np.clip(prgb, 0, 255).astype(np.uint8)).resize((Wm // s, Hm // s), Image.LANCZOS)
    rows = []
    for name in CONTINENTS:
        a, b = stats[name]
        rows.append(name.title() + ": " + ", ".join(f"{t} {100 * b[i]:.0f} %" for i, t in
                                                   sorted(enumerate(types), key=lambda q: -b[q[0]])
                                                   if b[i] >= 0.005))
    sheet(psmall, "Valsora: terrain test, by province (what the game would use)",
          "Each province takes the type most of its pixels have", [(TYPE_COLOUR[t], t) for t in types],
          DIST / "terrain_test_provinces.png", world, s, rows)

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
    print("wrote dist/terrain_test_map.png, dist/terrain_test_provinces.png, work/terrain_test/")


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
