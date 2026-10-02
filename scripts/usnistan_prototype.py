"""PROTOTYPE, not used by the build: a fully generated map of Usnistan.

The author asked (2026-10-02): "don't add it to the game yet, but could you try to fully
generate the map of, say, Usnistan ... very Africa / middle east inspired, with large
amounts of desert and jungle." This script is that experiment. It reads the current
build's coastline (work/world.npz, continent 6 = Usnistan) and generates everything
else procedurally, for Usnistan only. Nothing here feeds run_all.sh, the .pdn or the
mod; it writes work/usnistan/ (intermediates) and dist/usnistan_*.png (previews).

    python3 scripts/usnistan_prototype.py      # ~1-2 min, deterministic

Steps:
  1. Heightmap: a coastal plain rising inland, plateaus and basins from smooth noise,
     hand-placed mountain ranges and domes (positions in game pixels, shapes from
     noise), and valleys carved for the trunk rivers. Land is kept >= 96, water and the
     coastline are untouched.
  2. Climate: a zonal rainfall profile around a "climate equator" near the south of
     the main body (Mediterranean north -> Saharan belt -> Sahel -> jungle), plus moist
     air swept in from the east coast (and the west coast in the tropics and the
     Mediterranean north) that rains out on rising ground, so mountains cast rain
     shadows.
  3. Rivers: a priority flood from the coast gives every land pixel a downstream
     neighbour; rain is accumulated down that tree, the biggest flows become major
     rivers and the next ones minor rivers. rivers.trace turns them into rivers.bmp
     indices and rivers.problems must find nothing.
  4. Terrain (vanilla terrain.bmp palette indices): desert, savanna, plains, forest,
     jungle by rainfall; hills and mountains by height and roughness; irrigated plains
     along desert rivers; marsh in deltas and wet river lowlands; oases; urban cities.
  5. Provinces: seeds by Poisson-disk sampling with a target area per terrain (large in
     desert, small in fertile, jungle and river land), grown by organic.py's compact
     watershed over fractal noise with the rivers as walls, so rivers run between
     provinces. Then glued into the full map and checked with provinces.repair /
     provinces.validate (4-connected, >= 16 px, no 2x2 window with four provinces).
  6. Cities, countries (Dijkstra from capitals over the province graph, rivers and
     mountains cost extra so borders follow them), and states (k-means per country,
     made contiguous).
"""
import heapq
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra
from skimage.draw import line as skline, disk
from skimage.measure import label as sklabel
from skimage.morphology import skeletonize
from skimage.segmentation import watershed

sys.path.insert(0, str(Path(__file__).resolve().parent))
import provinces as PV  # noqa: E402
import rivers as RV  # noqa: E402
from common import CONTINENTS, MIN_PROVINCE, TERRAIN_TYPES  # noqa: E402
from organic import COMPACTNESS, NOISE, fractal_noise, _connected  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "work/usnistan"
DIST = ROOT / "dist"
CONT = CONTINENTS.index("usnistan") + 1  # continent id in world.npz / definition.csv (6)
MARGIN = 40

# ---------------------------------------------------------------- design (game pixels, (y, x))
Y_EQ, PX_PER_DEG = 1995, 22.0  # the continent's climate equator and scale of "latitude"

# mountain ranges: (polyline, half-width px, height added)
RANGES = [
    ([(1548, 2645), (1485, 2700), (1425, 2765), (1372, 2835)], 22, 85),   # "Atlas", north-west
    ([(1865, 2795), (1800, 2815), (1735, 2845)], 16, 32),                 # west coast line
    ([(2095, 3140), (2065, 3255), (2005, 3330)], 18, 38),                 # southern rim
    ([(1690, 2960), (1720, 3040)], 22, 30),                               # "Hoggar" ridge
]
# domes and basins: (centre, sigma px, height)
DOMES = [
    ((1870, 3430), 72, 80),    # eastern highlands ("Ethiopia")
    ((1705, 3020), 40, 62),    # central massif ("Ahaggar")
    ((1720, 3385), 34, 66),    # volcanic massif ("Tibesti")
    ((1260, 2760), 50, 22),    # northern island hills
    ((1990, 3020), 95, -9),    # the jungle basin ("Congo")
    ((1630, 3080), 45, -6),    # desert depression ("Qattara")
]
# trunk rivers: carved valleys, source -> mouth. A tributary names its parent and ends
# on it; a main river is extended to the nearest sea.
TRUNKS = [
    ("nile", None, [(1965, 3335), (1900, 3300), (1830, 3290), (1760, 3245), (1690, 3215),
                    (1615, 3185), (1550, 3165)]),
    ("congo", None, [(2045, 3225), (2005, 3150), (1965, 3065), (1950, 2965), (1935, 2880),
                     (1925, 2805)]),
    ("ubangi", "congo", [(1765, 2885), (1830, 2930), (1900, 2985), (1945, 3005)]),
    ("euphrates", None, [(1440, 2815), (1475, 2845), (1520, 2885), (1575, 2905), (1622, 2882),
                         (1645, 2852)]),
    ("tigris", "euphrates", [(1425, 2975), (1490, 2972), (1545, 2960), (1585, 2925)]),
    ("zambezi", None, [(1930, 3370), (1950, 3420), (1960, 3470), (1965, 3520)]),
]

# terrain classes: key -> (terrain.bmp palette index, label, preview colour,
# target province area in px)
CLASSES = {
    "plains":   (0, "Plains / farmland", (176, 200, 110), 300),
    "savanna":  (5, "Savanna (plains)", (214, 200, 128), 480),
    "forest":   (4, "Forest", (70, 135, 60), 340),
    "jungle":   (21, "Jungle", (24, 96, 48), 330),
    "desert":   (3, "Desert, sand", (240, 222, 168), 1500),
    "rocky":    (8, "Desert, rocky", (205, 172, 128), 1300),
    "hills":    (2, "Hills", (168, 136, 96), 520),
    "mountain": (6, "Mountains", (122, 104, 96), 700),
    "marsh":    (9, "Marsh", (100, 158, 146), 420),
    "urban":    (13, "Urban", (200, 40, 40), 200),
}
KEYS = list(CLASSES)
K = {k: i for i, k in enumerate(KEYS)}
for k, v in CLASSES.items():  # the index must be the HOI4 terrain type the class means
    assert TERRAIN_TYPES[v[0]] == {"savanna": "plains", "desert": "desert", "rocky": "desert"}.get(k, k), k

N_CITIES, N_OASES = 22, 8
# one placeholder country per region: its capital is the best city site within
# CAPITAL_REACH px of the anchor (game pixels)
CAPITAL_ANCHORS = [
    (1300, 2700),   # the north-western islands (Mediterranean)
    (1560, 2900),   # the twin rivers (Mesopotamia)
    (1580, 3180),   # the desert river's delta (Egypt)
    (1960, 2850),   # the jungle river's mouth (Congo)
    (1850, 3470),   # the eastern highlands (Ethiopia)
    (2060, 3150),   # the southern coast (Guinea coast)
]
CAPITAL_REACH = 130
N_CAPITALS = len(CAPITAL_ANCHORS)
TOTAL_STATES = 48
COUNTRY_NAMES = ["Country A", "Country B", "Country C", "Country D", "Country E", "Country F"]
COUNTRY_COLOURS = [(196, 92, 72), (88, 140, 196), (226, 178, 70), (110, 168, 92),
                   (164, 104, 176), (72, 170, 168)]
SEA, LAKE_C, OTHER = (24, 46, 92), (70, 120, 200), (90, 90, 90)
RIVER_C = (40, 90, 220)


def font(size):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",):
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            pass
    return ImageFont.load_default()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    world = np.load(ROOT / "work/world.npz")
    pz = np.load(ROOT / "work/provinces.npz")
    usn_full = world["cont"] == CONT
    ys, xs = np.nonzero(usn_full)
    Y0, Y1 = max(ys.min() - MARGIN, 0), min(ys.max() + MARGIN + 1, usn_full.shape[0])
    X0, X1 = max(xs.min() - MARGIN, 0), min(xs.max() + MARGIN + 1, usn_full.shape[1])
    win = np.s_[Y0:Y1, X0:X1]
    land = usn_full[win]
    kindw = world["kind"][win]
    sea, lake = kindw == 0, kindw == 2
    other = (kindw == 1) & ~land
    H, W = land.shape
    print(f"Usnistan = continent {CONT}: {land.sum()} land px, crop y {Y0}-{Y1} x {X0}-{X1}")

    def c(p):  # game (y, x) -> crop
        return int(p[0]) - Y0, int(p[1]) - X0

    def noise(scales, seed):  # roughly -1..1
        n = fractal_noise((H, W), scales, seed)
        return (n - n[land].mean()) / (n[land].std() * 2.5 + 1e-9)

    yy, xx = np.mgrid[0:H, 0:W]
    lat = (Y_EQ - (yy + Y0)) / PX_PER_DEG
    lat = lat + 4 * noise([90, 35], 3)  # climate belts wander
    dcoast = ndi.distance_transform_edt(land)

    # ============================================================ 1. heightmap
    dsm = ndi.gaussian_filter(dcoast, 12)  # smoothed, or the medial axis shows as creases
    h = 97 + 16 * (1 - np.exp(-dsm / 110))
    h += 11 * noise([170, 70], 11) * np.clip(dcoast / 60, 0, 1)        # plateaus and basins
    h += 3 * noise([30, 10, 4], 12)                                       # small relief
    ridged = (1 - np.abs(noise([45, 18, 7], 13))) ** 2                   # sharp crests
    for pts, wid, hgt in RANGES:
        path = wiggle(pts, amp=10, corr=40, seed=int(pts[0][0] + pts[0][1]), shape=(H, W), off=(Y0, X0))
        m = np.zeros((H, W), bool)
        m[path[:, 0], path[:, 1]] = True
        d = ndi.distance_transform_edt(~m)
        warp = 1 + 0.35 * noise([25], int(pts[-1][0]))
        h += hgt * np.exp(-(d / (wid * warp)) ** 2) * (0.45 + 0.75 * ridged)
    for (cy, cx), sig, hgt in DOMES:
        cy, cx = c((cy, cx))
        r2 = ((yy - cy) ** 2 + (xx - cx) ** 2) / (2.0 * sig ** 2)
        shape = np.exp(-r2 * (1 + 0.4 * noise([sig], cy + cx)))
        h += hgt * shape * ((0.55 + 0.6 * ridged) if hgt > 0 else 1)
    # valleys for the trunk rivers: each falls steadily from source to mouth
    trunk_paths, trunk_parent, trunk_mask = {}, {}, np.zeros((H, W), bool)
    h_pre = h.copy()
    for name, parent, pts in TRUNKS:
        path = wiggle(pts, amp=12, corr=22, seed=len(name) * 7 + int(pts[0][1]), shape=(H, W),
                      off=(Y0, X0))
        if parent is None:  # extend to the sea
            dsea, (iy, ix) = ndi.distance_transform_edt(~sea, return_indices=True)
            ey, ex = path[-1]
            ext = connect(ey, ex, iy[ey, ex], ix[ey, ex])
            path = np.concatenate([path, ext[1:]])
        else:  # end on the parent river
            pp = trunk_paths[parent]
            ey, ex = path[-1]
            j = np.argmin((pp[:, 0] - ey) ** 2 + (pp[:, 1] - ex) ** 2)
            path = np.concatenate([path, connect(ey, ex, *pp[j])[1:]])
        wet = np.flatnonzero(~land[path[:, 0], path[:, 1]])
        if len(wet):  # the river ends where it first reaches water
            path = path[:wet[0]]
            parent = None
        assert len(path) > 20, f"{name} starts in water"
        trunk_parent[name] = parent
        trunk_paths[name] = path
        z0 = h[path[0][0], path[0][1]]
        z1 = 96.6 if parent is None else h[path[-1][0], path[-1][1]] + 0.3
        z0 = max(z0, z1 + 4)
        s = np.linspace(0, 1, len(path))
        prof = z1 + (z0 - z1) * (1 - s) ** 1.2
        # the floor stays below the land it crosses and never rises downstream, so the
        # flow routing below follows it all the way
        ground = ndi.minimum_filter1d(h[path[:, 0], path[:, 1]], 31)
        prof = np.minimum(prof, ground - 7)
        prof = np.minimum.accumulate(prof) - 0.01 * np.arange(len(path))
        prof = np.maximum(prof, z1 + 0.002 * (len(path) - np.arange(len(path))))
        pm = np.zeros((H, W), bool)
        pm[path[:, 0], path[:, 1]] = True
        trunk_mask |= pm
        idx_img = np.full((H, W), -1)
        idx_img[path[:, 0], path[:, 1]] = np.arange(len(path))
        d, (iy, ix) = ndi.distance_transform_edt(~pm, return_indices=True)
        t = prof[idx_img[iy, ix]]
        wv = 26.0
        near = (d < wv) & land
        h[near] = np.minimum(h[near], t[near] + np.maximum(h[near] - t[near], 0) * (d[near] / wv) ** 1.4)
    h = h_pre - ndi.gaussian_filter(h_pre - h, 2.0)  # soften the carved valleys
    height = np.where(land, np.clip(np.round(h), 96, 250), world["height"][win]).astype(np.uint8)
    hf = np.where(land, h, 94.0)

    # ============================================================ 2. climate
    def sweep(from_east, length):
        m = np.ones(H)
        res = np.zeros((H, W))
        oro = np.zeros((H, W))
        cols = range(W - 1, -1, -1) if from_east else range(W)
        prev = None
        for x in cols:
            col = land[:, x]
            m = np.where(col, m * np.exp(-1 / length), 1.0)
            if prev is not None:
                dh = np.where(col, np.maximum(hf[:, x] - hf[:, prev], 0), 0)
                loss = np.minimum(m, 0.022 * dh * m)
                oro[:, x] = loss
                m = m - loss
            res[:, x] = m
            prev = x
        return res, oro
    mE, oE = sweep(True, 650)
    mW, oW = sweep(False, 420)
    west_w = np.where(np.abs(lat) < 9, 0.9, 0.0) + 0.9 / (1 + np.exp(-(lat - 29) / 2))
    moist = np.maximum(mE, mW * west_w)
    oro = ndi.gaussian_filter(oE + oW * west_w, 6) * 18
    zonal = (1.05 * np.exp(-(lat / 8.5) ** 2) + 0.5 / (1 + np.exp(-(lat - 31) / 2.5))
             + 0.25 * np.exp(-((lat + 12) / 6) ** 2))
    rain = zonal * (0.25 + 0.75 * moist) * (1 + 0.15 * noise([60], 21))
    rain += np.minimum(oro, 0.5) * np.clip(zonal * 2 + 0.25, 0, 1)
    rain += 0.08 * np.exp(-dcoast / 20) * (zonal > 0.15)
    rain = ndi.gaussian_filter(rain, 4)
    rain = np.where(land, np.clip(rain, 0, 1.5), 0)

    # ============================================================ 3. rivers
    dem = hf + 1.5 * noise([12, 5, 2], 31) + 0.002 * dcoast
    parent, order = priority_flood(dem, land)
    # the trunks are forced to drain along their valleys (a cheaper spill elsewhere can
    # otherwise capture them), then the drainage order is rebuilt
    for name, _, pts in TRUNKS:
        path, par = trunk_paths[name], trunk_parent[name]
        flat_p = path[:, 0] * W + path[:, 1]
        assert np.abs(np.diff(path, axis=0)).max() <= 1, f"{name}: the path crosses water"
        last = len(path) - (1 if par else 0)
        for i in range(last):
            parent[flat_p[i]] = flat_p[i + 1] if i + 1 < len(path) else -1
        if par is None:
            parent[flat_p[-1]] = -1
    order = drainage_order(parent, land)
    acc = np.where(land, 0.03 + rain, 0)
    for name, parent_, pts in TRUNKS:  # springs: the trunks rise in wet uplands or lakes
        sy, sx = trunk_paths[name][0]
        acc[sy, sx] += 1600 if parent_ is None else 900
    acc = acc.ravel().astype(np.float64)
    for p in order[::-1]:
        q = parent[p]
        if q >= 0:
            acc[q] += acc[p]
    basin = np.full(H * W, -1, np.int64)
    for p in order:
        q = parent[p]
        basin[p] = p if q < 0 else basin[q]
    acc = acc.reshape(H, W)
    basin = basin.reshape(H, W)
    T_MINOR, T_MAJOR = 130.0, 1500.0
    drawn = land & (acc >= T_MINOR)
    water = ~land
    drawn = separate_basins(drawn, basin, acc, water)
    # side-by-side channels of one river (parallel flow lines on flats) are merged into
    # one line, or rivers.trace would make a river two pixels thick there
    ids = tidy(drawn, land)
    drawn = separate_basins(ids > 0, ids, ndi.maximum_filter(acc, 5), water)
    comp = sklabel(drawn, connectivity=2)
    sizes = np.bincount(comp.ravel())
    drawn &= sizes[comp] >= 18  # stubs are not worth a river
    major = drawn & ((ndi.maximum_filter(acc, 5) >= T_MAJOR)
                     | ndi.binary_dilation(trunk_mask, np.ones((5, 5), bool)))
    minor = drawn & ~major
    riv = RV.trace(major, minor, land)
    rprob = RV.problems(riv, land)
    river = riv != RV.NONE
    print(f"rivers: {river.sum()} px ({(riv[river] >= 7).sum()} major), "
          f"{len(np.unique(sklabel(river, connectivity=1))) - 1} systems, problems: {rprob or 'none'}")

    # ============================================================ 4. terrain
    rough = np.sqrt(np.maximum(ndi.uniform_filter(hf ** 2, 15) - ndi.uniform_filter(hf, 15) ** 2, 0))
    patch = noise([22, 8], 41)
    ter = np.full((H, W), K["plains"], np.uint8)
    ter[rain < 0.62] = K["plains"]
    ter[(rain >= 0.42) & (rain < 0.62) & (patch > 0.35)] = K["forest"]
    ter[rain < 0.42] = K["savanna"]
    ter[rain < 0.20] = K["desert"]
    ter[(rain < 0.20) & ((hf > 122) | (patch > 0.25))] = K["rocky"]
    ter[(rain >= 0.55)] = K["forest"]
    ter[(rain >= 0.60) & (np.abs(lat + 3 * patch) < 11)] = K["jungle"]
    ter[(rain >= 0.55) & (rain < 0.68) & (patch < -0.45)] = K["plains"]
    hilly = (hf >= 140) | (rough > 5.0)
    mount = (hf >= 165) | ((hf >= 150) & (rough > 6.0))
    jung = ter == K["jungle"]
    ter[hilly & ~(jung & (hf < 150))] = K["hills"]
    ter[mount] = K["mountain"]
    # rivers through dry land are green ribbons; deltas and wet lowlands are marsh
    dmaj = ndi.distance_transform_edt(~(riv >= 7) | ~river)
    dany = ndi.distance_transform_edt(~river)
    dry = np.isin(ter, [K["desert"], K["rocky"], K["savanna"]])
    ter[dry & (dmaj <= 4.5)] = K["plains"]
    ter[np.isin(ter, [K["desert"], K["rocky"]]) & (dany <= 2)] = K["savanna"]
    mouths = river & ndi.binary_dilation(sea, np.ones((3, 3), bool)) & (riv >= 7)
    dmouth = ndi.distance_transform_edt(~mouths)
    delta = (dmouth < 28 + 10 * patch) & (hf < 100.5) & ~mount
    swamp = (dany < 6 + 3 * patch) & (hf < 102) & (rain > 0.55) & (rough < 1.5) & (patch > 0.1)
    ter[land & (delta | swamp)] = K["marsh"]
    # oases: desert hollows away from rivers and coasts
    hollow = hf - ndi.uniform_filter(hf, 41)
    desertish = np.isin(ter, [K["desert"], K["rocky"]]) & (dany > 60) & (dcoast > 30)
    oases = pick(np.where(desertish, -hollow + 0.5 * noise([10], 51), -np.inf), N_OASES, 110)
    for (oy, ox) in oases:
        rr, cc = disk((oy, ox), 7, shape=(H, W))
        ter[rr, cc] = np.where(land[rr, cc], K["plains"], ter[rr, cc])

    # ============================================================ 5a. cities
    tk = ter
    score = (np.clip(rain, 0, 0.9) + 1.2 * (dmaj <= 3) + 0.4 * (dany <= 2)
             + 0.6 * (dcoast <= 4) + 1.2 * (dmouth < 15)
             - 0.8 * np.isin(tk, [K["desert"], K["rocky"]]) - 0.3 * (tk == K["jungle"])
             - 1.0 * (tk == K["mountain"]) - 0.4 * (tk == K["marsh"]) + 0.2 * noise([15], 61))
    ok = land & ~river & (dcoast >= 2)
    score = np.where(ok, score, -np.inf)
    capitals = []
    for ay, ax in CAPITAL_ANCHORS:
        ay, ax = c((ay, ax))
        near = np.full((H, W), -np.inf)
        rr, cc = disk((ay, ax), CAPITAL_REACH, shape=(H, W))
        near[rr, cc] = score[rr, cc]
        capitals += pick(near, 1, 1)
    s2 = score.copy()
    for (cy, cx) in capitals:
        rr, cc = disk((cy, cx), 95, shape=(H, W))
        s2[rr, cc] = -np.inf
    cities = capitals + pick(s2, N_CITIES - N_CAPITALS, 95)
    for (cy, cx) in cities:
        rr, cc = disk((cy, cx), 4.5, shape=(H, W))
        keep = land[rr, cc] & ~river[rr, cc]
        ter[rr[keep], cc[keep]] = K["urban"]
    ter = np.where(land, ter, 255).astype(np.uint8)

    # ============================================================ 5b. provinces
    area_px = np.array([CLASSES[k][3] for k in KEYS] + [1], float)[np.minimum(ter, len(KEYS))]
    area_px = np.where(dmaj <= 15, area_px * 0.7, area_px)
    logA = ndi.gaussian_filter(np.where(land, np.log(area_px), np.log(400)), 18)
    target = np.exp(logA)
    seeds = poisson_seeds(land & ~river, target, cities + oases, seed=71)
    # every piece of land the rivers cut off gets a seed of its own
    pieces = sklabel(land & ~river, connectivity=1)
    has = np.zeros(pieces.max() + 1, bool)
    has[pieces[tuple(np.array(seeds).T)]] = True
    for i, sl in enumerate(ndi.find_objects(pieces), 1):
        if sl is None or has[i]:
            continue
        m = pieces[sl] == i
        if m.sum() >= MIN_PROVINCE:
            d = ndi.distance_transform_edt(np.pad(m, 1))[1:-1, 1:-1]
            py, px = np.unravel_index(np.argmax(d), d.shape)
            seeds.append((py + sl[0].start, px + sl[1].start))
    spacing = np.sqrt(land.sum() / len(seeds) / 0.866)
    nz = fractal_noise((H, W), [max(1.5, f * spacing) for f in NOISE], 81)
    markers = np.zeros((H, W), np.int32)
    for j, (sy, sx) in enumerate(seeds, 1):
        markers[sy, sx] = j
    lab = watershed(nz, markers, mask=land & ~river, compactness=COMPACTNESS / spacing)
    miss = land & (lab == 0)  # river pixels and bits the flood missed: nearest province
    iy, ix = ndi.distance_transform_edt(lab == 0, return_distances=False, return_indices=True)
    lab[miss] = lab[iy[miss], ix[miss]]
    lab = _connected(lab, land)
    lab = split_pieces(lab, land)
    lab = merge_small(lab, land, np.maximum(40, 0.25 * target))

    # glue into the full map and apply HOI4's province rules
    prov_old, kind_old, cont_old = pz["prov"], pz["kind"], pz["cont"]
    old_ids = np.unique(prov_old[usn_full])
    assert (cont_old[old_ids] == CONT).all() and not np.isin(prov_old[~usn_full], old_ids).any()
    keep = np.ones(len(kind_old), bool)
    keep[old_ids] = False
    remap = np.cumsum(keep) - 1
    n_keep = int(keep.sum())
    full = remap[prov_old].astype(np.int64)
    nnew = int(lab.max())
    sub = full[win]
    sub[land] = n_keep + lab[land] - 1
    kind_all = np.concatenate([kind_old[keep], np.ones(nnew, np.uint8)])
    cont_all = np.concatenate([cont_old[keep], np.full(nnew, CONT, np.uint8)])
    before = full.copy()
    size = np.bincount(full.ravel(), minlength=len(kind_all))
    full, fixed = PV.repair(full, kind_all, cont_all, size)
    changed = full != before
    outside = int((changed & ~usn_full).sum())
    kind_px_changed = int((kind_all[full[changed]] != kind_all[before[changed]]).sum())
    vprob = PV.validate(full, kind_all)
    lab = np.where(land & (full[win] >= n_keep), full[win] - n_keep + 1, 0)
    print(f"provinces: {nnew} land; {fixed} X-crossings repaired ({outside} px outside "
          f"Usnistan, {kind_px_changed} changed land/water); province rules: {vprob or 'pass'}")
    pids = np.arange(1, nnew + 1)
    psize = np.bincount(lab.ravel(), minlength=nnew + 1)
    ptype = np.array([np.bincount(ter[lab == i], minlength=len(KEYS)).argmax() for i in pids])
    pcy = ndi.mean(yy, lab, pids)
    pcx = ndi.mean(xx, lab, pids)
    # rivers between provinces: a river pixel with a 4-neighbour in another province
    other_nb = np.zeros((H, W), bool)
    for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        sh = np.roll(lab, (dy, dx), (0, 1))
        other_nb |= (sh != lab) & (sh > 0)
    on_border = (river & other_nb).sum() / river.sum()

    # ============================================================ 6. countries and states
    a, b, cnt = PV.adjacency(np.where(land, lab, 0), wrap=False)
    m = (a > 0) & (b > 0)
    a, b, cnt = a[m] - 1, b[m] - 1, cnt[m]
    # per border: share of river pixels on it and its height
    rv_on = np.zeros(len(a))
    hb = np.zeros(len(a))
    key = {}
    for i, (u, v) in enumerate(zip(a, b)):
        key[(u, v)] = i
    pairs_r, pairs_h = border_stats(lab, river & (riv >= 7), hf)
    for (u, v), r in pairs_r.items():
        if (u, v) in key:
            rv_on[key[(u, v)]] = r
    for (u, v), z in pairs_h.items():
        if (u, v) in key:
            hb[key[(u, v)]] = z
    dist = np.hypot(pcy[a] - pcy[b], pcx[a] - pcx[b])
    cost = dist * (1 + 5 * np.minimum(rv_on * 3, 1) + np.clip((hb - 135) / 12, 0, 6))
    g = coo_matrix((np.concatenate([cost, cost]), (np.concatenate([a, b]), np.concatenate([b, a]))),
                   shape=(nnew, nnew)).tocsr()
    cap_prov = [lab[cy, cx] - 1 for (cy, cx) in capitals]
    dd, _, src = dijkstra(g, indices=cap_prov, min_only=True, return_predecessors=True)
    country = np.full(nnew, -1)
    reach = np.isfinite(dd)
    country[reach] = [cap_prov.index(s) for s in src[reach]]
    for i in np.nonzero(~reach)[0]:  # islands: the country of the nearest reached province
        j = np.argmin(np.where(reach, (pcy - pcy[i]) ** 2 + (pcx - pcx[i]) ** 2, np.inf))
        country[i] = country[j]
    state = make_states(country, psize, pcy, pcx, a, b, cnt, nnew)
    nstates = state.max() + 1

    # ============================================================ outputs
    vp = {}
    city_info = []
    for n, (cy, cx) in enumerate(cities):
        p = int(lab[cy, cx]) - 1
        cap = n < N_CAPITALS
        city_info.append(dict(n=n + 1, x=int(cx + X0), y=int(cy + Y0), province=p + 1,
                              state=int(state[p]) + 1, country=COUNTRY_NAMES[country[p]],
                              capital=bool(cap and country[p] == n), vp=10 if cap else 5))
        vp[p] = city_info[-1]["vp"]
    np.savez_compressed(OUT / "usnistan.npz", origin=np.array([Y0, X0]), land=land,
                        height=height, terrain_index=np.where(land, np.array(
                            [CLASSES[k][0] for k in KEYS] + [15], np.uint8)[np.minimum(ter, len(KEYS))], 15),
                        rivers=riv, provinces=lab, state_of=state, country_of=country,
                        rain=rain.astype(np.float32), flow=acc.astype(np.float32))
    shares_px = {k: float((ter[land] == K[k]).mean()) for k in KEYS}
    shares_prov = {k: float((ptype == K[k]).mean()) for k in KEYS}
    summary = dict(continent=CONT, land_px=int(land.sum()), provinces=nnew,
                   province_area_mean=float(psize[1:].mean()),
                   province_area_by_terrain={k: float(psize[1:][ptype == K[k]].mean())
                                             for k in KEYS if (ptype == K[k]).any()},
                   states=int(nstates), countries=N_CAPITALS,
                   river_px=int(river.sum()), major_river_px=int((riv[river] >= 7).sum()),
                   river_px_on_province_border=float(on_border),
                   river_problems=rprob, province_problems=vprob,
                   xcrossings_repaired=int(fixed), repair_px_outside_usnistan=outside,
                   terrain_share_px=shares_px, terrain_share_provinces=shares_prov,
                   cities=city_info, oases=[(int(x + X0), int(y + Y0)) for y, x in oases])
    (OUT / "summary.json").write_text(json.dumps(summary, indent=1))

    previews(dict(land=land, sea=sea, lake=lake, other=other, ter=ter, hf=hf, height=height,
                  wh=world["height"][win].astype(float), riv=riv, river=river, lab=lab,
                  ptype=ptype, psize=psize, country=country, state=state, cities=cities,
                  capitals=capitals, oases=oases, shares_px=shares_px, shares_prov=shares_prov,
                  Y0=Y0, X0=X0, summary=summary))
    print(json.dumps({k: v for k, v in summary.items() if k not in ("cities", "oases")}, indent=1))


# ---------------------------------------------------------------- helpers
def connect(y0, x0, y1, x1):
    rr, cc = skline(int(y0), int(x0), int(y1), int(x1))
    return np.stack([rr, cc], 1)


def wiggle(pts, amp, corr, seed, shape, off):
    """Densify a polyline (game coords) and displace it sideways by smooth noise,
    pinned at both ends; returns the 8-connected pixel path in crop coords."""
    P = np.array([(p[0] - off[0], p[1] - off[1]) for p in pts], float)
    dense = [P[0]]
    for p, q in zip(P[:-1], P[1:]):
        n = int(np.ceil(np.hypot(*(q - p))))
        dense += [p + (q - p) * t for t in np.arange(1, n + 1) / n]
    D = np.array(dense)
    t = np.gradient(D, axis=0)
    t /= np.linalg.norm(t, axis=1, keepdims=True) + 1e-9
    nrm = np.stack([t[:, 1], -t[:, 0]], 1)
    r = np.random.default_rng(seed).standard_normal(len(D) + 4 * corr)
    o = ndi.gaussian_filter1d(r, corr)[2 * corr:2 * corr + len(D)]
    o = o / (o.std() + 1e-9) * amp * np.sin(np.linspace(0, np.pi, len(D))) ** 0.5
    D = D + nrm * o[:, None]
    D = np.clip(np.round(D).astype(int), 0, np.array(shape) - 1)
    out = [D[0]]
    for q in D[1:]:
        seg = connect(out[-1][0], out[-1][1], q[0], q[1])[1:]
        out += list(seg)
    res, seen = [], {}
    for q in map(tuple, out):  # loop erasure: a path never visits a pixel twice
        if q in seen:
            for r in res[seen[q] + 1:]:
                del seen[r]
            del res[seen[q] + 1:]
            continue
        seen[q] = len(res)
        res.append(q)
    return np.array(res)


def priority_flood(dem, land):
    """Downstream pixel (flat index, -1 = drains to water) for every land pixel, and
    the order pixels were reached (upstream pixels come later)."""
    H, W = dem.shape
    flat = dem.ravel()
    lnd = land.ravel()
    closed = ~lnd.copy()
    parent = np.full(H * W, -1, np.int64)
    edge = land & ndi.binary_dilation(~land, np.ones((3, 3), bool))
    heap = [(float(flat[p]), int(p)) for p in np.flatnonzero(edge)]
    heapq.heapify(heap)
    closed[np.flatnonzero(edge)] = True
    offs = (-W - 1, -W, -W + 1, -1, 1, W - 1, W, W + 1)
    order = []
    push, pop = heapq.heappush, heapq.heappop
    while heap:
        z, p = pop(heap)
        order.append(p)
        for o in offs:
            q = p + o
            if not closed[q]:
                closed[q] = True
                parent[q] = p
                zq = flat[q]
                push(heap, (zq if zq > z else z + 1e-4, q))
    return parent, np.array(order)


def tidy(drawn, land):
    """Close each river system's gaps of up to ~2 px and skeletonise it again; returns
    the system number per pixel (0 = no river)."""
    out = np.zeros(drawn.shape, np.int64)
    lab = sklabel(drawn, connectivity=2)
    for i, sl in enumerate(ndi.find_objects(lab), 1):
        sl2 = tuple(slice(max(s.start - 4, 0), s.stop + 4) for s in sl)
        m = np.pad(lab[sl2] == i, 4)
        m = ndi.binary_closing(m, np.ones((3, 3), bool), iterations=2)[4:-4, 4:-4]
        holes = ndi.binary_fill_holes(m) & ~m  # small rings the closing made
        hl, nh = ndi.label(holes)
        if nh:
            hs = np.bincount(hl.ravel())
            m |= (hl > 0) & (hs[hl] < 80)
        sk = skeletonize(m) & land[sl2]
        out[sl2][sk] = i
    return out


def drainage_order(parent, land):
    """Pixels ordered outlets first, every pixel after its downstream neighbour."""
    lp = np.flatnonzero(land.ravel())
    par = parent[lp]
    srt = np.argsort(par, kind="stable")
    keys = par[srt]
    kids = lp[srt]
    order = list(lp[par < 0])
    k = 0
    while k < len(order):
        p = order[k]
        a, b = np.searchsorted(keys, [p, p + 1])
        order.extend(kids[a:b].tolist())
        k += 1
    assert len(order) == len(lp), "drainage has a cycle"
    return np.array(order)


def separate_basins(drawn, basin, acc, water):
    """Rivers of different drainage basins must not touch (rivers.trace would read them as
    one system): where they do, the pixel with the smaller flow gives way."""
    drawn = drawn.copy()
    H, W = drawn.shape
    for _ in range(10):
        b = np.where(drawn, basin, -1)
        hi = ndi.maximum_filter(b, 3)
        lo = ndi.minimum_filter(np.where(drawn, basin, np.iinfo(np.int64).max), 3)
        clash = np.argwhere(drawn & (hi != lo))
        if not len(clash):
            break
        drop = []
        for y, x in clash:
            own = basin[y, x]
            foreign = [acc[y + dy, x + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                       if drawn[y + dy, x + dx] and basin[y + dy, x + dx] != own]
            if foreign and (max(foreign), 0) > (acc[y, x], 0):
                drop.append((y, x))
        for y, x in drop:
            drawn[y, x] = False
        # whatever a dropped pixel fed is now cut off from the sea: drop it too
        lab = sklabel(drawn, connectivity=2)
        coast = ndi.binary_dilation(water, np.ones((3, 3), bool))
        keep = np.unique(lab[drawn & coast])
        drawn &= np.isin(lab, keep[keep > 0])
    return drawn


def pick(score, n, radius):
    """Greedy: the n best pixels at least `radius` apart."""
    s = score.copy()
    out = []
    for _ in range(n):
        i = np.argmax(s)
        if not np.isfinite(s.flat[i]):
            break
        y, x = np.unravel_index(i, s.shape)
        out.append((int(y), int(x)))
        rr, cc = disk((y, x), radius, shape=s.shape)
        s[rr, cc] = -np.inf
    return out


def poisson_seeds(mask, target, fixed, seed):
    """Dart throwing with a varying radius: a seed blocks a disk sized for the target
    province area around it. `fixed` seeds (cities, oases) go first."""
    H, W = mask.shape
    blocked = ~mask
    r_of = 0.92 * np.sqrt(target / 0.866)
    out = []
    rng = np.random.default_rng(seed)
    cand = np.flatnonzero(mask)
    cand = list(fixed) + [divmod(int(i), W) for i in rng.permutation(cand)]
    for k, (y, x) in enumerate(cand):
        if blocked[y, x] and not (k < len(fixed) and mask[y, x]):
            continue
        out.append((y, x))
        r = r_of[y, x] if k >= len(fixed) else 0.7 * r_of[y, x]
        rr, cc = disk((y, x), r, shape=(H, W))
        blocked[rr, cc] = True
    return out


def split_pieces(lab, land):
    """A province still in several 4-connected pieces (an island part) becomes several."""
    nxt = lab.max() + 1
    for i, sl in enumerate(ndi.find_objects(lab), 1):
        if sl is None:
            continue
        comp, n = ndi.label(lab[sl] == i)
        if n > 1:
            big = np.bincount(comp.ravel())[1:].argmax() + 1
            for k in range(1, n + 1):
                if k != big:
                    lab[sl][comp == k] = nxt
                    nxt += 1
    return lab


def merge_small(lab, land, minsize):
    """Provinces under their minimum join the neighbour they share most border with;
    then ids are made contiguous from 1."""
    cross = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool)
    for _ in range(20):
        size = np.bincount(lab.ravel())
        changed = False
        for i, sl in enumerate(ndi.find_objects(lab), 1):
            if sl is None or size[i] == 0:
                continue
            sl2 = tuple(slice(max(s.start - 1, 0), s.stop + 1) for s in sl)
            pm = lab[sl2] == i
            ys, xs = np.nonzero(pm)
            if size[i] >= minsize[sl2][ys[0], xs[0]]:
                continue
            ring = ndi.binary_dilation(pm, cross) & ~pm & (lab[sl2] > 0)
            if not ring.any():
                continue
            v, cnt = np.unique(lab[sl2][ring], return_counts=True)
            t = v[cnt.argmax()]
            lab[sl2][pm] = t
            size[t] += size[i]
            size[i] = 0
            changed = True
        if not changed:
            break
    u, inv = np.unique(lab, return_inverse=True)
    return inv.reshape(lab.shape)  # 0 stays 0 (water), provinces 1..N


def border_stats(lab, river, hf):
    """Per pair of adjacent provinces (0-based, a < b): share of border pixel pairs
    touching a river pixel, and mean height along the border."""
    rs, hs, ns = {}, {}, {}
    for A, B, RA, RB, HA, HB in (
            (lab[:, :-1], lab[:, 1:], river[:, :-1], river[:, 1:], hf[:, :-1], hf[:, 1:]),
            (lab[:-1, :], lab[1:, :], river[:-1, :], river[1:, :], hf[:-1, :], hf[1:, :])):
        m = (A != B) & (A > 0) & (B > 0)
        u = np.minimum(A[m], B[m]) - 1
        v = np.maximum(A[m], B[m]) - 1
        r = (RA[m] | RB[m]).astype(float)
        z = (HA[m] + HB[m]) / 2
        code = u.astype(np.int64) * 10_000_000 + v
        cu, inv = np.unique(code, return_inverse=True)
        sr = np.bincount(inv, r)
        sz = np.bincount(inv, z)
        sn = np.bincount(inv)
        for k, cc in enumerate(cu):
            key = (int(cc // 10_000_000), int(cc % 10_000_000))
            rs[key] = rs.get(key, 0) + sr[k]
            hs[key] = hs.get(key, 0) + sz[k]
            ns[key] = ns.get(key, 0) + sn[k]
    return ({k: rs[k] / ns[k] for k in ns}, {k: hs[k] / ns[k] for k in ns})


def make_states(country, psize, pcy, pcx, a, b, cnt, n):
    """k-means of province centres within each country, then every state made one
    connected piece (an island piece stays only if it has 3+ provinces)."""
    tot_area, tot_n = psize[1:].sum(), n
    state = np.full(n, -1)
    nxt = 0
    rng = np.random.default_rng(91)
    for cid in range(country.max() + 1):
        idx = np.nonzero(country == cid)[0]
        if len(idx) == 0:
            continue
        share = 0.5 * psize[1:][idx].sum() / tot_area + 0.5 * len(idx) / tot_n
        k = int(max(1, min(len(idx), round(TOTAL_STATES * share))))
        P = np.stack([pcy[idx], pcx[idx]], 1)
        cen = [P[rng.integers(len(P))]]
        for _ in range(k - 1):  # k-means++ (deterministic rng)
            d2 = np.min(((P[:, None] - np.array(cen)[None]) ** 2).sum(-1), 1)
            cen.append(P[rng.choice(len(P), p=d2 / d2.sum())])
        cen = np.array(cen)
        for _ in range(40):
            asg = np.argmin(((P[:, None] - cen[None]) ** 2).sum(-1), 1)
            cen = np.array([P[asg == j].mean(0) if (asg == j).any() else cen[j] for j in range(k)])
        state[idx] = nxt + asg
        nxt += k
    nbrs = [[] for _ in range(n)]
    for u, v, c in zip(a, b, cnt):
        nbrs[u].append((v, c))
        nbrs[v].append((u, c))
    for _ in range(10):
        changed = False
        for s in range(state.max() + 1):
            mem = set(np.nonzero(state == s)[0].tolist())
            if not mem:
                continue
            parts, seen = [], set()
            for p0 in mem:
                if p0 in seen:
                    continue
                part, stack = [], [p0]
                seen.add(p0)
                while stack:
                    p = stack.pop()
                    part.append(p)
                    for q, _ in nbrs[p]:
                        if q in mem and q not in seen:
                            seen.add(q)
                            stack.append(q)
                parts.append(part)
            if len(parts) == 1:
                continue
            parts.sort(key=len, reverse=True)
            for part in parts[1:]:
                border = {}
                for p in part:
                    for q, c in nbrs[p]:
                        if state[q] != s:
                            w = c * (3 if country[q] == country[p] else 1)
                            border[state[q]] = border.get(state[q], 0) + w
                if border:
                    state[part] = max(border, key=border.get)
                    changed = True
                elif len(part) >= 3:
                    state[part] = state.max() + 1
                    changed = True
                # a lone islet with no land neighbour stays with its state
        if not changed:
            break
    _, state = np.unique(state, return_inverse=True)
    return state


# ---------------------------------------------------------------- previews
def base_rgb(d):
    img = np.zeros(d["land"].shape + (3,), np.uint8)
    img[:] = SEA
    img[d["lake"]] = LAKE_C
    img[d["other"]] = OTHER
    return img


def draw_rivers(img, riv, thick_major=False):
    r = riv != RV.NONE
    if thick_major:  # preview only: major rivers drawn 3 px wide
        img[ndi.binary_dilation(r & (riv >= 7))] = (20, 40, 170)
    col = np.where((riv >= 7)[..., None], np.array((20, 40, 170)), np.array(RIVER_C))
    img[r] = col[r]
    return img


def panel(img, title, rows, subtitle=None, swatch_w=26):
    """Image plus a legend column on the right. rows: (colour or None, text)."""
    f, fb = font(15), font(20)
    lw = 330
    out = Image.new("RGB", (img.width + lw, max(img.height, 60 + 26 * len(rows))), (245, 242, 236))
    out.paste(img, (0, 0))
    d = ImageDraw.Draw(out)
    x = img.width + 14
    d.text((x, 12), title, fill=(20, 20, 20), font=fb)
    y = 44
    if subtitle:
        for line in subtitle.split("\n"):
            d.text((x, y), line, fill=(70, 70, 70), font=font(13))
            y += 18
        y += 8
    for col, text in rows:
        if col is not None:
            d.rectangle([x, y + 2, x + swatch_w, y + 18], fill=tuple(int(v) for v in col),
                        outline=(60, 60, 60))
            d.text((x + swatch_w + 8, y + 1), text, fill=(20, 20, 20), font=f)
        else:
            d.text((x, y + 1), text, fill=(20, 20, 20), font=f)
        y += 24
    return out


def borders(lab, scale):
    big = np.kron(lab, np.ones((scale, scale), lab.dtype))
    e = np.zeros(big.shape, bool)
    e[:, 1:] |= big[:, 1:] != big[:, :-1]
    e[1:, :] |= big[1:, :] != big[:-1, :]
    return big, e


def previews(d):
    land, ter, riv, river = d["land"], d["ter"], d["riv"], d["river"]
    pal = np.array([CLASSES[k][2] for k in KEYS] + [(0, 0, 0)], np.uint8)
    cap = f"Usnistan prototype (continent {CONT}): not in the game"

    # terrain
    img = base_rgb(d)
    img[land] = pal[np.minimum(ter[land], len(KEYS))]
    img = draw_rivers(img, riv)
    rows = [(CLASSES[k][2], f"{CLASSES[k][1]}  [{CLASSES[k][0]}]  {100 * d['shares_px'][k]:.1f}%")
            for k in KEYS]
    rows += [(None, ""), (RIVER_C, "River (minor / major darker)"), (LAKE_C, "Lake"),
             (OTHER, "Other continents")]
    im = Image.fromarray(img)
    dr = ImageDraw.Draw(im)
    for (oy, ox) in d["oases"]:
        dr.ellipse([ox - 9, oy - 9, ox + 9, oy + 9], outline=(20, 120, 40), width=2)
    rows.append(((255, 255, 255), "circled: oases"))
    panel(im, "Terrain", rows, f"{cap}\n[n] = vanilla terrain.bmp index\n% = share of land pixels"
          ).save(DIST / "usnistan_terrain.png")

    # relief
    z = np.where(land | d["other"], d["hf"], np.minimum(d["wh"], 94.0))
    gy, gx = np.gradient(z * 1.2)
    lx, ly, lz = -0.6, -0.6, 0.53
    shade = (-gx * lx - gy * ly + lz) / np.sqrt(gx ** 2 + gy ** 2 + 1)
    shade = np.clip(0.55 + 0.55 * shade, 0.25, 1.2)
    stops = [(96, (90, 140, 80)), (110, (170, 180, 110)), (130, (210, 190, 130)),
             (155, (170, 130, 90)), (185, (130, 110, 100)), (230, (245, 245, 245))]
    hh = d["hf"]
    tint = np.zeros(land.shape + (3,))
    for ch in range(3):
        tint[..., ch] = np.interp(hh, [s[0] for s in stops], [s[1][ch] for s in stops])
    img = base_rgb(d).astype(float)
    img[land] = tint[land] * shade[land, None]
    img = np.clip(img, 0, 255).astype(np.uint8)
    img = draw_rivers(img, riv, thick_major=True)
    rows = [(s[1], f"height {s[0]}") for s in stops] + [(None, ""), (RIVER_C, "River"),
                                                         ((20, 40, 170), "Major river (drawn wider here)")]
    s = d["summary"]
    panel(Image.fromarray(img), "Relief and rivers", rows,
          f"{cap}\nheightmap.bmp values (water plane 95)\n{s['river_px']} river px, "
          f"{s['major_river_px']} major\nrivers.problems: {'none' if not s['river_problems'] else 'FAIL'}"
          ).save(DIST / "usnistan_relief.png")

    # provinces (2x)
    S = 2
    lab = d["lab"]
    rng = np.random.default_rng(5)
    jit = rng.uniform(0.8, 1.12, (lab.max() + 1, 1))
    pcol = np.vstack([[0, 0, 0], pal[np.minimum(d["ptype"], len(KEYS))]]).astype(float) * jit
    pcol = np.clip(pcol, 0, 255).astype(np.uint8)
    img = base_rgb(d)
    img[land] = pcol[lab[land]]
    big = np.kron(img, np.ones((S, S, 1), np.uint8))
    _, e = borders(lab, S)
    landb = np.kron(land, np.ones((S, S), bool))
    big[e & landb] = (40, 34, 30)
    rb = np.kron(river, np.ones((S, S), bool))
    big[rb] = (25, 70, 230)
    counts = np.bincount(d["ptype"], minlength=len(KEYS))
    rows = [(CLASSES[k][2], f"{CLASSES[k][1]}: {counts[K[k]]} prov, "
             f"~{s['province_area_by_terrain'].get(k, 0):.0f} px") for k in KEYS if counts[K[k]]]
    rows += [(None, ""), ((25, 70, 230), "River"),
             (None, f"{s['provinces']} provinces, mean {s['province_area_mean']:.0f} px"),
             (None, f"{100 * s['river_px_on_province_border']:.0f}% of river px on a border"),
             (None, f"province rules: {'pass' if not s['province_problems'] else 'FAIL'}")]
    panel(Image.fromarray(big), "Provinces", rows,
          f"{cap}\ncoloured by majority terrain (2x zoom)").save(DIST / "usnistan_provinces.png")

    # political (2x)
    state, country = d["state"], d["country"]
    ccol = np.array(COUNTRY_COLOURS, float)
    sj = np.random.default_rng(8).uniform(0.86, 1.1, (state.max() + 1, 1))
    pc = np.clip(ccol[country] * sj[state], 0, 255).astype(np.uint8)
    img = base_rgb(d)
    img[land] = np.vstack([[0, 0, 0], pc])[lab[land]]
    big = np.kron(img, np.ones((S, S, 1), np.uint8))
    slab = np.where(land, np.concatenate([[-1], state])[lab], -1)
    clab = np.where(land, np.concatenate([[-1], country])[lab], -1)
    _, es = borders(slab, S)
    _, ec = borders(clab, S)
    ec = ndi.binary_dilation(ec, np.ones((2, 2), bool))
    big[rb] = (60, 110, 230)
    big[es & landb] = (70, 60, 50)
    big[ec & landb] = (15, 10, 10)
    im = Image.fromarray(big)
    dr = ImageDraw.Draw(im)
    fs = font(18)
    for info in d["summary"]["cities"]:
        y, x = (info["y"] - d["Y0"]) * S, (info["x"] - d["X0"]) * S
        if info["capital"]:
            star(dr, x, y, 13)
        else:
            dr.ellipse([x - 6, y - 6, x + 6, y + 6], fill=(255, 255, 255), outline=(0, 0, 0), width=2)
        dr.text((x + 12, y - 10), str(info["n"]), fill=(0, 0, 0), font=fs, stroke_width=3,
                stroke_fill=(255, 255, 255))
    rows = []
    for cid, name in enumerate(COUNTRY_NAMES):
        ps = np.nonzero(country == cid)[0]
        rows.append((COUNTRY_COLOURS[cid], f"{name}: {len(np.unique(state[ps]))} states, {len(ps)} prov"))
    rows += [(None, ""), (None, "star: capital (VP 10)"), (None, "dot: city (VP 5)"),
             (None, "thin lines: state borders"), (None, "thick lines: country borders")]
    panel(im, "States and countries", rows,
          f"{cap}\n{s['states']} states, {len(COUNTRY_NAMES)} placeholder countries\n"
          "numbers: cities, see work/usnistan/summary.json").save(DIST / "usnistan_political.png")


def star(dr, x, y, r):
    pts = []
    for k in range(10):
        ang = -np.pi / 2 + k * np.pi / 5
        rr = r if k % 2 == 0 else r * 0.45
        pts.append((x + rr * np.cos(ang), y + rr * np.sin(ang)))
    dr.polygon(pts, fill=(255, 220, 40), outline=(0, 0, 0))


if __name__ == "__main__":
    main()
