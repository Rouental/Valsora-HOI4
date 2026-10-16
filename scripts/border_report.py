"""Room under HOI4's province border limit, and what would make more (by hand, after a build).

    python3 scripts/border_report.py                 # where the borders come from, and the re-cut estimates
    python3 scripts/border_report.py --terrain map   # sizes from the map's own Terrain layer, not the terrain test
    python3 scripts/border_report.py --preview       # also dist/border_room_preview.png (the most desert, now and re-cut)
    python3 scripts/border_report.py --drawn-states  # what drawing their own states would cost the countries on cut ones

HOI4 draws at most 65,536 province borders (borders.py). This says where ours come from (land or water, continent,
pairs touching in more than one place) and estimates what re-cutting every state's provinces would give: one size
everywhere, a bigger size, and sizes by terrain like the base game's. Its median desert province is 4 x its median
plains one, mountains and marshes 1.8 x, jungle 1.6 x, forest 1.2 x (read from vanilla 1.19.3's provinces.bmp and
definition.csv, 2026-10-15: 13,413 provinces, 40,694 borders). Deep desert (over 40 px from other land) can also be one
large 'impassable' province.

The re-cut is a weighted k-means per state (cells sized by terrain), a quick stand-in for organic.py's cut: compare a
scenario with the first one (the same 190 px as now, re-cut the same way), not with today's count, which also has the
provinces split along rivers and the author's small drawn states. The terrain is the terrain test's
(work/terrain_test, not in the mod) until the Terrain layer is painted in earnest; then use --terrain map.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

import borders
from common import TERRAIN_TYPES

BASE = 190          # apply_outlines.PROVINCE_AREA
# the base game's median land province by terrain, over its median plains province (127 px)
VANILLA = {"plains": 1.0, "forest": 152 / 127, "jungle": 207 / 127, "desert": 516 / 127, "hills": 120 / 127,
           "mountain": 232 / 127, "marsh": 234 / 127, "urban": 100 / 127}
DEEP_DESERT = 40    # px from other land or water: 'impassable' desert
IMPASSABLE = 2500   # px per province there
TYPES = list(VANILLA)
COLOUR = {"plains": (190, 200, 120), "forest": (60, 120, 60), "jungle": (22, 92, 44), "desert": (232, 210, 150),
          "hills": (166, 134, 94), "mountain": (112, 96, 90), "marsh": (98, 156, 144), "urban": (200, 40, 40)}
TEST_TYPES = {"plains": "plains", "steppe": "plains", "forest": "forest", "taiga": "forest", "jungle": "jungle",
              "desert": "desert", "rocky": "desert", "hills": "hills", "mountain": "mountain", "snow": "mountain",
              "marsh": "marsh", "urban": "urban"}   # terrain_test.CLASSES, in its order
KIND = {0: "sea", 1: "land", 2: "lake"}


def stretches(prov):
    """every border as (province a, province b): borders.count's components, with their pairs"""
    H, W = prov.shape
    right = np.roll(prov, -1, axis=1)
    vy, vx = np.nonzero(prov != right)
    hy, hx = np.nonzero(prov[:-1] != prov[1:])
    a, b = np.r_[prov[vy, vx], prov[hy, hx]], np.r_[right[vy, vx], prov[hy + 1, hx]]
    pairs, pid = np.unique(np.minimum(a, b) * (1 << 24) + np.maximum(a, b), return_inverse=True)
    c1 = np.r_[vy * W + (vx + 1) % W, (hy + 1) * W + hx]
    c2 = np.r_[(vy + 1) * W + (vx + 1) % W, (hy + 1) * W + (hx + 1) % W]
    span = (H + 1) * W
    nodes, inv = np.unique(np.r_[pid * span + c1, pid * span + c2], return_inverse=True)
    m = len(c1)
    g = coo_matrix((np.ones(m, np.int8), (inv[:m], inv[m:])), shape=(len(nodes), len(nodes)))
    n, lab = connected_components(g, directed=False)
    pair_of = np.zeros(n, np.int64)
    pair_of[lab[inv[:m]]] = pid
    return pairs[pair_of] >> 24, pairs[pair_of] & ((1 << 24) - 1), len(pairs)


def terrain_types(source):
    """per pixel: index into TYPES (water -1), from the terrain test or the map's Terrain layer"""
    if source == "test":
        keys = list(TEST_TYPES)
        cls = np.load("work/terrain_test/terrain_class.npy")
        lut = np.array([TYPES.index(TEST_TYPES[k]) for k in keys] + [-1] * (256 - len(keys)))
        return lut[cls]
    idx = np.load("work/world.npz")["terrain"]
    lut = np.full(256, 0)
    for i, t in TERRAIN_TYPES.items():
        lut[i] = TYPES.index(t) if t in TYPES else -1
    return lut[idx]


def recut(prov, kind, states, ttype, factor, base=BASE, deep=None, seed=1, bases=None):
    """each state's land cut again into cells of base x factor[terrain] px (weighted k-means: a cell's weight is
    the square of 1/size, so cells come out about that size); water stays; bases, if given, is each state's own
    base size. -> (map, land provinces)"""
    rng = np.random.default_rng(seed)
    N = len(kind)
    state_of = np.full(N, -1, np.int64)
    for s, ps in enumerate(states):
        state_of[ps] = s
    smap = state_of[prov]
    ys, xs = np.nonzero(smap >= 0)
    st = smap[ys, xs]
    order = np.argsort(st, kind="stable")
    ys, xs, st = ys[order], xs[order], st[order]
    bounds = np.r_[0, np.cumsum(np.bincount(st, minlength=len(states)))]
    size = np.array([factor.get(t, 1.0) for t in TYPES])
    w = 1.0 / (size[np.maximum(ttype[ys, xs], 0)] * (base if bases is None else np.asarray(bases, float)[st]))
    if deep is not None:
        w = np.where(deep[ys, xs], 1.0 / IMPASSABLE, w)
    new, nid = prov.copy(), N
    for s in range(len(states)):
        a, b = bounds[s], bounds[s + 1]
        if b <= a:
            continue
        py, px, pw = ys[a:b].astype(float), xs[a:b].astype(float), w[a:b]
        k = min(b - a, max(1, int(round(pw.sum()))))
        lab = np.zeros(b - a, np.int64)
        if k > 1:
            ww = pw ** 2
            pick = rng.choice(b - a, size=k, replace=False, p=ww / ww.sum())
            cy, cx = py[pick].copy(), px[pick].copy()
            for _ in range(10):
                lab = ((py[:, None] - cy[None]) ** 2 + (px[:, None] - cx[None]) ** 2).argmin(1)
                sw = np.bincount(lab, ww, k)
                ok = sw > 0
                cy[ok] = np.bincount(lab, ww * py, k)[ok] / sw[ok]
                cx[ok] = np.bincount(lab, ww * px, k)[ok] / sw[ok]
            lab = ((py[:, None] - cy[None]) ** 2 + (px[:, None] - cx[None]) ** 2).argmin(1)
            lab = np.unique(lab, return_inverse=True)[1]
        new[ys[a:b], xs[a:b]] = nid + lab
        nid += lab.max() + 1
    return new, nid - N


def breakdown(prov, kind, cont, cont_names):
    pa, pb, npairs = stretches(prov)
    kinds = Counter(" - ".join(sorted((KIND[kind[x]], KIND[kind[y]]))) for x, y in zip(pa, pb))
    per = Counter()
    for x, y in zip(pa, pb):
        c = cont[x] if kind[x] == 1 else cont[y] if kind[y] == 1 else 0
        per[cont_names[c - 1] if c else "sea and lakes only"] += 1
    nbrs = {}
    for x, y in zip(pa, pb):
        nbrs.setdefault(x, set()).add(y)
        nbrs.setdefault(y, set()).add(x)
    islands = {p for p in range(len(kind)) if kind[p] == 1 and all(kind[q] != 1 for q in nbrs.get(p, ()))}
    area = np.bincount(prov.ravel(), minlength=len(kind))[kind == 1]
    return dict(borders=len(pa), pairs=npairs, kinds=dict(kinds), continents=dict(per),
                land=int((kind == 1).sum()), land_median=float(np.median(area)), small=int((area < 100).sum()),
                islands=len(islands), island_borders=sum(1 for x, y in zip(pa, pb) if x in islands or y in islands))


def outline(prov, box):
    y0, y1, x0, x1 = box
    p = prov[y0:y1, x0:x1]
    e = np.zeros(p.shape, bool)
    e[:, 1:] |= p[:, 1:] != p[:, :-1]
    e[1:, :] |= p[1:, :] != p[:-1, :]
    return e


def preview(prov, new, kind, ttype, out, size=(400, 600), scale=2):
    """the 400 x 600 px window with the most desert, now and re-cut by terrain, over the terrain's colours"""
    land = kind[prov] == 1
    des = (ttype == TYPES.index("desert")).astype(float)
    score = ndi.uniform_filter(des, size, mode="constant")
    cy, cx = np.unravel_index(np.argmax(score), score.shape)
    H, W = prov.shape
    y0 = int(np.clip(cy - size[0] // 2, 0, H - size[0]))
    x0 = int(np.clip(cx - size[1] // 2, 0, W - size[1]))
    box = (y0, y0 + size[0], x0, x0 + size[1])
    y1, x1 = box[1], box[3]
    pal = np.array([COLOUR[t] for t in TYPES] + [(40, 62, 84)], np.uint8)
    base = pal[np.where(ttype[y0:y1, x0:x1] < 0, len(TYPES), ttype[y0:y1, x0:x1])]
    base[~land[y0:y1, x0:x1]] = (40, 62, 84)
    panels = []
    for m in (prov, new):
        img = base.copy()
        e = outline(m, box) & land[y0:y1, x0:x1]
        img[e] = (34, 30, 28)
        panels.append(Image.fromarray(img).resize(((x1 - x0) * scale, (y1 - y0) * scale), Image.NEAREST))
    w, h = panels[0].size
    pad, top = 24, 56
    cv = Image.new("RGB", (pad * 3 + 2 * w, top + h + pad), (32, 34, 37))
    d = ImageDraw.Draw(cv)
    try:
        f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except OSError:
        f = ImageFont.load_default()
    for i, (p, t) in enumerate(zip(panels, ("now: about 190 px provinces everywhere",
                                            "re-cut with the base game's sizes by terrain"))):
        cv.paste(p, (pad + i * (w + pad), top))
        d.text((pad + i * (w + pad), 20), t, fill=(225, 225, 225), font=f)
    cv.save(out)


def restate(states, owners, tags, target, centre, size, seed=1):
    """the states of the countries in tags each split into states of about target px (k-means on their provinces'
    centres, weighted by size): the author's drawn states, at that density, standing in for apply_outlines.py's cut.
    Larger targets than a state's own size leave it whole. -> (states, which of them are the countries')"""
    rng = np.random.default_rng(seed)
    out, mine = [], []
    for s, g in enumerate(states):
        g = np.asarray(g)
        area = size[g].sum()
        k = int(round(area / target))
        if owners[s] not in tags or k < 2 or len(g) < 2:
            out.append(list(g))
            mine.append(owners[s] in tags)
            continue
        k = min(k, len(g))
        c, w = centre[g].astype(float), size[g].astype(float)
        cc = c[rng.choice(len(g), size=k, replace=False, p=w / w.sum())]
        for _ in range(12):
            lab = ((c[:, None] - cc[None]) ** 2).sum(2).argmin(1)
            for j in range(k):
                m = lab == j
                if m.any():
                    cc[j] = np.average(c[m], axis=0, weights=w[m])
        lab = ((c[:, None] - cc[None]) ** 2).sum(2).argmin(1)
        for j in np.unique(lab):
            out.append(list(g[lab == j]))
            mine.append(True)
    return out, mine


def drawn_states(prov, kind):
    """what drawing their own states would cost the countries whose states are still apply_outlines.py's cut
    (gazetteer.finals), at Rouental's density and lighter ones: every scenario re-cut the same way as the first"""
    import gazetteer
    rj = json.load(open("work/regions.json"))
    states, owners = rj["states"], rj["owners"]
    reg = np.load("work/regions.npz")
    centre, size = reg["centre"], reg["size"]
    fin = gazetteer.finals()
    cut = {t for t, v in fin.items() if not v}
    area = Counter()
    count = Counter()
    provs = Counter()
    for s, g in enumerate(states):
        area[owners[s]] += int(size[g].sum())
        count[owners[s]] += 1
        provs[owners[s]] += len(g)
    rou_state = area["ROU"] / count["ROU"]
    rou_prov = area["ROU"] / provs["ROU"]
    cut_area = sum(area[t] for t in cut)
    print(f"{len(cut)} countries on cut states: {cut_area:,} px of land, {sum(count[t] for t in cut):,} states "
          f"({cut_area / sum(count[t] for t in cut):.0f} px), {sum(provs[t] for t in cut):,} provinces; Rouental: states "
          f"{rou_state:.0f} px, provinces {rou_prov:.0f} px")
    flat = np.zeros(prov.shape, np.int8)
    runs = [("today's states, 190 px provinces (the comparison)", None, BASE),
            (f"states like Rouental's ({rou_state:.0f} px), 190 px provinces", rou_state, BASE),
            (f"states like Rouental's, provinces like Rouental's ({rou_prov:.0f} px)", rou_state, rou_prov),
            ("states of 800 px, 190 px provinces", 800, BASE),
            ("states of 800 px, provinces 220 px", 800, 220)]
    terrain = Path("work/terrain_test/terrain_class.npy").exists()
    if terrain:      # the terrain test's terrain, standing in for the Terrain layer
        runs.append(("states and provinces like Rouental's, sized by terrain", rou_state, rou_prov))
    result = []
    for name, target, pbase in runs:
        st, mine = (states, [owners[s] in cut for s in range(len(states))]) if target is None else \
            restate(states, owners, cut, target, centre, size)
        bases = [pbase if m else BASE for m in mine]
        by_terrain = "terrain" in name
        m, n = recut(prov, kind, st, terrain_types("test") if by_terrain else flat, VANILLA if by_terrain else {}, BASE,
                     None, bases=bases)
        b = borders.count(m)[1]
        result.append(dict(name=name, states=len(st), land=n, borders=b))
        print(f"  {name:62s} {len(st):6,} states {n:7,} land provinces {b:7,} borders ({b - result[0]['borders']:+,})")
    return result


def main():
    if "--drawn-states" in sys.argv:
        z = np.load("work/provinces.npz")
        res = drawn_states(z["prov"].astype(np.int64), z["kind"])
        Path("work/border_report_states.json").write_text(json.dumps(res, indent=1, default=int))
        return
    source = "map" if "--terrain" in sys.argv and sys.argv[sys.argv.index("--terrain") + 1] == "map" else "test"
    z = np.load("work/provinces.npz")
    prov, kind, cont = z["prov"].astype(np.int64), z["kind"], z["cont"]
    states = json.load(open("work/regions.json"))["states"]
    cont_names = re.findall(r"^\t(\w+)$", Path("build/valsora_test/map/continent.txt").read_text(encoding="utf-8-sig"),
                            re.M)
    now = breakdown(prov, kind, cont, cont_names)
    print(f"{now['borders']} borders now, {borders.LIMIT - now['borders']} below HOI4's {borders.LIMIT} "
          f"({now['pairs']} touching pairs: {now['borders'] - now['pairs']} touch in more than one place)")
    print("  by kind:", ", ".join(f"{k} {v}" for k, v in sorted(now["kinds"].items(), key=lambda t: -t[1])))
    print("  by continent:", ", ".join(f"{k} {v}" for k, v in sorted(now["continents"].items(), key=lambda t: -t[1])))
    print(f"  {now['land']} land provinces (median {now['land_median']:.0f} px; {now['small']} under 100 px), "
          f"{now['islands']} of them islands alone in the water ({now['island_borders']} borders)")
    ttype = terrain_types(source)
    deep = ndi.distance_transform_edt(ttype == TYPES.index("desert")) > DEEP_DESERT
    runs = [("the same 190 px everywhere (the comparison)", {}, BASE, None),
            ("sizes by terrain like the base game's", VANILLA, BASE, None),
            (f"... and deep desert {IMPASSABLE:,} px provinces ('impassable')", VANILLA, BASE, deep),
            ("220 px everywhere", {}, 220, None),
            ("250 px everywhere", {}, 250, None)]
    print(f"re-cut estimates (terrain: {'the terrain test' if source == 'test' else 'the Terrain layer'}):")
    result = []
    for name, factor, base, dp in runs:
        m, n = recut(prov, kind, states, ttype, factor, base, dp)
        b = borders.count(m)[1]
        result.append(dict(name=name, land=n, borders=b))
        if "--preview" in sys.argv and factor is VANILLA and dp is None:
            preview(prov, m, kind, ttype, "dist/border_room_preview.png")
        print(f"  {name:52s} {n:6d} land provinces, {b:6d} borders ({b - result[0]['borders']:+d})")
    Path("work/border_report.json").write_text(json.dumps(dict(now=now, scenarios=result), indent=1, default=int))


if __name__ == "__main__":
    main()
