"""Edits made directly to the layers of source/HOI4 Mod Map.pdn, run by hand.

    python3 scripts/pdn_tools.py navigable X,Y [X,Y ...]
        Turn the lakes containing these pixels into sea (Terrain layer), each in a new
        sea region of its own (Strategic Regions layer). HOI4 ships can use sea, not lakes.
    python3 scripts/pdn_tools.py recolour LAYER R,G,B=R,G,B [...]
        Swap exact colours on a layer, e.g. a country's colour on "Countries" after it
        changed in common.COUNTRIES (the build matches countries by exact colour).
    python3 scripts/pdn_tools.py give COUNTRY X,Y [X,Y ...]
        Give the whole states containing these pixels to COUNTRY (a common.COUNTRIES key),
        on the Countries layer.
    python3 scripts/pdn_tools.py sea_zones [CELL]
        Regroup all sea provinces into larger sea regions (about CELL px across, default
        1536), and recolour the Strategic Regions layer so sea regions are blues and land
        regions never are.

The .pdn is decoded to work/pdn_tools, edited, and saved over itself (its own object
graph is the template, so layer names, order and visibility are kept).
"""
import colorsys
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi

from common import MAP_W as W, MAP_H as H
from writepdn import write_pdn

PDN = Path("source/HOI4 Mod Map.pdn")
WORK = Path("work/pdn_tools")
OCEAN, LAKES = (8, 31, 130), (55, 90, 220)
CROSS = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])


def code(rgb):
    rgb = rgb.astype(np.int64)
    return (rgb[..., 0] << 16) | (rgb[..., 1] << 8) | rgb[..., 2]


def load():
    subprocess.run([sys.executable, str(Path(__file__).parent / "readpdn.py"), str(PDN), str(WORK)],
                   check=True, stdout=subprocess.DEVNULL)
    names = (WORK / "layers.txt").read_text().splitlines()
    return names, {nm: np.load(WORK / f"layer{k}.npy") for k, nm in enumerate(names)}


def save(names, L):
    tmp = PDN.with_suffix(".tmp")
    write_pdn(PDN, tmp, [L[nm] for nm in names])
    shutil.move(tmp, PDN)
    print(f"wrote {PDN}")


def put(layer, codes, mask):
    layer[mask, 0] = codes[mask] >> 16
    layer[mask, 1] = (codes[mask] >> 8) & 255
    layer[mask, 2] = codes[mask] & 255


def palette(n, blue, seed, used=()):
    """n distinct colours; blues (hue 0.53-0.70) or anything but blue."""
    rng = np.random.default_rng(seed)
    out, seen = [], set(used)
    while len(out) < n:
        if blue:
            h, s, v = rng.uniform(0.53, 0.70), rng.uniform(0.45, 0.95), rng.uniform(0.40, 0.95)
        else:
            h = rng.uniform(0.0, 0.78)
            h = h if h < 0.42 else h + 0.40  # skip cyans, blues and indigos (0.42-0.82)
            s, v = rng.uniform(0.35, 0.85), rng.uniform(0.55, 0.95)
        r, g, b = (round(c * 255) for c in colorsys.hsv_to_rgb(h % 1.0, s, v))
        c = (r << 16) | (g << 8) | b
        if c not in seen and c != 0:
            seen.add(c)
            out.append(c)
    return out


def navigable(names, L, seeds):
    T = code(L["Terrain"][..., :3])
    lake = T == code(np.array(LAKES))
    lab, _ = ndi.label(lake, CROSS)
    R = code(L["Strategic Regions"][..., :3])
    for x, y in seeds:
        i = lab[y, x]
        if i == 0:
            sys.exit(f"({x}, {y}) is not on a lake")
        m = lab == i
        L["Terrain"][m, :3] = OCEAN
        col = palette(1, True, x * 7919 + y, set(np.unique(R).tolist()))[0]
        put(L["Strategic Regions"], np.full(R.shape, col), m)
        print(f"lake at ({x}, {y}): {m.sum()} px is now sea, in its own sea region")


def sea_zones(names, L, cell):
    T = code(L["Terrain"][..., :3])
    sea = T == code(np.array(OCEAN))
    P = code(L["Provinces"][..., :3])
    R = code(L["Strategic Regions"][..., :3])
    pcols, plab = np.unique(P, return_inverse=True)
    plab = plab.reshape(H, W)
    n = len(pcols)
    size = np.bincount(plab.ravel(), minlength=n)
    seasz = np.bincount(plab.ravel(), weights=sea.ravel(), minlength=n)
    is_sea = seasz * 2 > size
    cy, cx = (np.bincount(plab.ravel(), weights=g.ravel(), minlength=n) / size
              for g in np.mgrid[0:H, 0:W])
    # which provinces touch (sea-sea only)
    nbrs = defaultdict(Counter)
    for a, b in ((plab[:, :-1], plab[:, 1:]), (plab[:-1], plab[1:]), (plab[:, -1], plab[:, 0])):
        d = (a != b) & is_sea[a] & is_sea[b]
        for u, v in zip(a[d].tolist(), b[d].tolist()):
            nbrs[u][v] += 1
            nbrs[v][u] += 1
    seas = np.nonzero(is_sea)[0]
    # bucket by a coarse grid, then split buckets into connected pieces
    bucket = {int(p): (int(cy[p] // (cell / 2)), int(cx[p] // cell)) for p in seas}
    region = {}
    groups = []
    for p in seas:
        p = int(p)
        if p in region:
            continue
        stack, g = [p], []
        region[p] = len(groups)
        while stack:
            u = stack.pop()
            g.append(u)
            for v in nbrs[u]:
                if v not in region and bucket[v] == bucket[p]:
                    region[v] = len(groups)
                    stack.append(v)
        groups.append(g)
    # small pieces join the neighbouring piece they share most coast with
    area = [sum(size[u] for u in g) for g in groups]
    for k in sorted(range(len(groups)), key=lambda k: area[k]):
        if area[k] >= cell * cell / 8 or not groups[k]:
            continue
        border = Counter()
        for u in groups[k]:
            for v, c in nbrs[u].items():
                if region[v] != k:
                    border[region[v]] += c
        if border:
            t = border.most_common(1)[0][0]
            for u in groups[k]:
                region[u] = t
            groups[t] += groups[k]
            area[t] += area[k]
            groups[k], area[k] = [], 0
    live = [k for k in range(len(groups)) if groups[k]]
    blues = palette(len(live), True, 11)
    newcol = np.zeros(n, np.int64)
    for k, c in zip(live, blues):
        newcol[groups[k]] = c
    # land regions: same regions, new non-blue colours
    land_cols = np.unique(R[~sea])
    reds = palette(len(land_cols), False, 12, set(blues))
    remap = dict(zip(land_cols.tolist(), reds))
    out = np.where(sea, newcol[plab], 0)
    lv = np.vectorize(remap.get, otypes=[np.int64])(R[~sea])
    out[~sea] = lv
    put(L["Strategic Regions"], out, np.ones((H, W), bool))
    print(f"{len(live)} sea regions (were {len(np.unique(R[sea]))}), {len(land_cols)} land regions recoloured")


def give(names, L, country, seeds):
    from common import COUNTRIES
    St = code(L["States"][..., :3])
    painted = L["States"][..., 3] > 0
    for x, y in seeds:
        m = painted & (St == St[y, x])
        L["Countries"][m, :3] = COUNTRIES[country][3]
        L["Countries"][m, 3] = 255
        print(f"state at ({x}, {y}): {m.sum()} px -> {country}")


def recolour(names, L, layer, pairs):
    C = code(L[layer][..., :3])
    painted = L[layer][..., 3] > 0
    for old, new in pairs:
        m = painted & (C == code(np.array(old)))
        L[layer][m, :3] = new
        print(f"{layer}: {old} -> {new}, {m.sum()} px")


def main():
    cmd = sys.argv[1]
    names, L = load()
    if cmd == "navigable":
        navigable(names, L, [tuple(int(v) for v in a.split(",")) for a in sys.argv[2:]])
    elif cmd == "recolour":
        pairs = [tuple(tuple(int(v) for v in side.split(",")) for side in a.split("="))
                 for a in sys.argv[3:]]
        recolour(names, L, sys.argv[2], pairs)
    elif cmd == "give":
        give(names, L, sys.argv[2], [tuple(int(v) for v in a.split(",")) for a in sys.argv[3:]])
    elif cmd == "sea_zones":
        sea_zones(names, L, int(sys.argv[2]) if len(sys.argv) > 2 else 1536)
    else:
        sys.exit(__doc__)
    save(names, L)


if __name__ == "__main__":
    main()
