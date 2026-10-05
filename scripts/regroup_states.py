"""Make the author's drawn state lines the states, one per enclosed area (run by hand).

The author, 2026-10-04: "for countries that I have defined the state borders of, do not
split any states that I have created ... unless I have left the state borders blank, just
use the ones I make." apply_outlines.py used to cut big drawn areas into ~650 px pieces;
this script undoes that wherever a country has state lines of its own:

  * an area enclosed by lines (Necessary Borders + Necessary States) is one state, if its
    country (the Countries layer's majority) has at least one state line inside it;
    countries with no inner lines (left blank) keep their states;
  * provinces are kept; one that a line crosses is split along it (pieces of 16+ px
    become provinces, smaller ones join a neighbour in the same state);
  * an island with no lines follows the state most of its old state went to;
  * each new state takes its country and strategic region by majority;
  * slivers under SLIVER px that lines close off join the neighbouring area of the same
    country they share most border with.

It rewrites Provinces, States, Countries and Strategic Regions in
source/HOI4 Mod Map.pdn (its own object graph is the template) and prints, per country,
how many states it had and has, and any two of the author's state names
(source/state_names.json) that now fall in one state.

    python3 scripts/regroup_states.py
"""
import json
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi
from skimage.measure import label as sklabel

from common import COUNTRIES, MAP_W as W, MAP_H as H, MIN_PROVINCE, PLACEHOLDERS
from writepdn import write_pdn

PDN = Path("source/HOI4 Mod Map.pdn")
WORK = Path("work/pdn_regroup")
OCEAN, LAKES = (8, 31, 130), (55, 90, 220)
LINE_LAYERS = ["Necessary Borders", "Necessary States"]
SLIVER = 40
# placeholder countries whose states the author has drawn (Aislada, 2026-10-04: one
# state per drawn region, not one per city)
DRAWN_PLACEHOLDERS = {"AIS"}
# countries whose only "state line" is a stray: Gaellia's west border forks where it
# meets the coast, closing off a bit of coast at (596, 2222) that went to Gaellia
NOT_DRAWN = {"GAE"}
MIN_LINE, MIN_AREA = 8, 150  # a state line: at least this long, between areas this big
CROSS = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])


def code(rgb):
    rgb = rgb.astype(np.int64)
    return (rgb[..., 0] << 16) | (rgb[..., 1] << 8) | rgb[..., 2]


def put(arr, codes, mask):
    arr[mask, 0] = codes[mask] >> 16
    arr[mask, 1] = (codes[mask] >> 8) & 255
    arr[mask, 2] = codes[mask] & 255


def main():
    subprocess.run([sys.executable, str(Path(__file__).parent / "readpdn.py"), str(PDN), str(WORK)],
                   check=True, stdout=subprocess.DEVNULL)
    names = (WORK / "layers.txt").read_text().splitlines()
    L = {nm: np.load(WORK / f"layer{k}.npy") for k, nm in enumerate(names)}
    terr = code(L["Terrain"][..., :3])
    land = (terr != code(np.array(OCEAN))) & (terr != code(np.array(LAKES)))
    lines = np.zeros((H, W), bool)
    for nm in LINE_LAYERS:
        lines |= L[nm][..., 3] > 0
    lines &= land
    K = np.where(L["Countries"][..., 3] > 0, code(L["Countries"][..., :3]), -1)
    S = np.where(L["States"][..., 3] > 0, code(L["States"][..., :3]), -1)
    P = code(L["Provinces"][..., :3])
    R = code(L["Strategic Regions"][..., :3])
    tag_of = {code(np.array(v[3])): v[0] for k, v in COUNTRIES.items()
              if k not in PLACEHOLDERS or v[0] in DRAWN_PLACEHOLDERS}

    # ------------------------------------------------ the drawn areas
    cells = sklabel(land & ~lines, connectivity=1)
    n = cells.max() + 1
    idx = ndi.distance_transform_edt(cells == 0, return_distances=False, return_indices=True)
    full = np.where(land & (cells == 0), cells[idx[0], idx[1]], cells)  # line pixels too
    size = np.bincount(full.ravel(), minlength=n)
    # each area's country: the majority of its real-country pixels
    country = np.full(n, -1, np.int64)
    real = np.isin(K, list(tag_of)) & land
    for c, k in Counter(zip(full[real].tolist(), K[real].tolist())).most_common()[::-1]:
        country[c[0]] = c[1]  # most common written last
    touch = np.zeros(n, bool)
    touch[np.unique(full[ndi.binary_dilation(lines, CROSS) & land])] = True
    touch[0] = False
    # countries with lines of their own inside: two of their areas meet across a line
    # (both areas a real size and sharing a real stretch of line, so a few pixels a line
    # happens to close off, or a line ending in the sea, don't count)
    shared = Counter()
    for a, b, on in ((full[:, 1:], full[:, :-1], lines[:, 1:] | lines[:, :-1]),
                     (full[1:], full[:-1], lines[1:] | lines[:-1])):
        m = (a != b) & (a > 0) & (b > 0) & on
        shared.update(zip(np.minimum(a[m], b[m]).tolist(), np.maximum(a[m], b[m]).tolist()))
    inner = set()
    for (x, y), k_ in shared.items():
        if k_ >= MIN_LINE and min(size[x], size[y]) >= MIN_AREA and country[x] >= 0 \
                and country[x] == country[y] and tag_of[int(country[x])] not in NOT_DRAWN:
            inner.add(int(country[x]))
    print("countries with their own state lines: " + ", ".join(sorted(tag_of[c] for c in inner)))
    # slivers the lines close off join their same-country neighbour
    area_of = np.arange(n)
    for c in np.nonzero(touch & (size < SLIVER) & np.isin(country, list(inner)))[0]:
        m = full == c
        ring = ndi.binary_dilation(m, CROSS) & ~m & land
        nb = Counter(v for v in full[ring].tolist() if v > 0 and country[v] == country[c] and size[v] >= SLIVER)
        if nb:
            area_of[c] = nb.most_common(1)[0][0]
    A = area_of[full]

    # ------------------------------------------------ new state of every pixel
    mine = land & np.isin(K, list(inner)) & (K == country[A]) & touch[full]
    new = np.full((H, W), -1, np.int64)   # new state number, -1 = unchanged
    new[mine] = A[mine]
    # islands without lines follow where most of their old state went
    go = defaultdict(Counter)
    for s_, a_ in zip(S[mine].tolist(), A[mine].tolist()):
        go[s_][a_] += 1
    isle = land & np.isin(K, list(inner)) & ~touch[full] & (S >= 0)
    for s_ in np.unique(S[isle]):
        if s_ in go:
            new[isle & (S == s_)] = go[s_].most_common(1)[0][0]
    changed = new >= 0

    # ------------------------------------------------ provinces crossed by a line
    split = merged = 0
    used = set(np.unique(P).tolist())
    rng = np.random.default_rng(20261004)
    ucol, pid = np.unique(P, return_inverse=True)
    pid = pid.reshape(P.shape)
    boxes = ndi.find_objects(pid + 1)
    for q in np.unique(pid[changed]):
        sl = boxes[q]
        sl = np.s_[max(sl[0].start - 2, 0):sl[0].stop + 2, max(sl[1].start - 2, 0):sl[1].stop + 2]
        Pw, Nw, Lw = P[sl], new[sl], land[sl]  # views: edits land in P and new
        pc = int(ucol[q])
        pm = (Pw == pc) & Lw
        sts = Counter(Nw[pm].tolist())
        if len(sts) <= 1:
            continue
        main_st = sts.most_common(1)[0][0]
        for st, _ in sts.most_common()[1:]:
            comp = sklabel(pm & (Nw == st), connectivity=1)
            for j, sz in enumerate(np.bincount(comp.ravel())[1:], 1):
                piece = comp == j
                if sz >= MIN_PROVINCE:
                    while True:
                        nc = int(rng.integers(1 << 20, 1 << 24))
                        if nc not in used:
                            used.add(nc)
                            break
                    Pw[piece] = nc
                    split += 1
                    continue
                ring = ndi.binary_dilation(piece, CROSS) & ~piece & Lw & (Nw == st)
                nb = Counter(v for v in Pw[ring].tolist() if v != pc)
                if nb:
                    Pw[piece] = nb.most_common(1)[0][0]
                    merged += 1
                else:  # nowhere to go: the line is ignored here
                    Nw[piece] = main_st
        # what stays of the province must be one piece
        rest = (Pw == pc) & Lw
        comp = sklabel(rest, connectivity=1)
        sizes = np.bincount(comp.ravel())[1:]
        for j in np.argsort(-sizes)[1:] + 1:
            piece = comp == j
            ring = ndi.binary_dilation(piece, CROSS) & ~piece & Lw & (Nw == Nw[piece][0])
            nb = Counter(v for v in Pw[ring].tolist() if v != pc)
            if nb:
                Pw[piece] = nb.most_common(1)[0][0]
                merged += 1
    print(f"provinces: {split} pieces cut off by state lines became provinces, {merged} scraps joined a neighbour")

    # ------------------------------------------------ states, countries, regions
    newS = S.copy()
    usedS = set(np.unique(S).tolist())
    before = Counter()
    sel = land & np.isin(K, list(inner)) & (S >= 0)
    first = {}
    for s_, k_ in Counter(zip(S[sel].tolist(), K[sel].tolist())).most_common():
        first.setdefault(s_, k_)  # each old state's main country
    for k_ in first.values():
        before[int(k_)] += 1
    print(f"  ({len(first)} old states in those countries)")
    after = Counter()
    sboxes = ndi.find_objects(np.where(changed, new + 1, 0))
    for a_ in np.unique(new[changed]):
        sl = sboxes[a_]
        m = new[sl] == a_
        while True:
            sc = int(rng.integers(1 << 20, 1 << 24))
            if sc not in usedS:
                usedS.add(sc)
                break
        Sw, Kw, Rw = newS[sl], K[sl], R[sl]
        Sw[m] = sc
        k_ = Counter(Kw[m].tolist()).most_common(1)[0][0]
        Kw[m] = k_
        Rw[m] = Counter(Rw[m].tolist()).most_common(1)[0][0]
        after[int(k_)] += 1
    for c in sorted(inner, key=lambda c: tag_of[c]):
        print(f"  {tag_of[c]}: {before[c]} states -> {after[c]}")
    # the author's state names: two in one state?
    names_px = json.loads(Path("source/state_names.json").read_text(encoding="utf-8"))
    by_state = defaultdict(list)
    for k_, nm in names_px.items():
        x, y = map(int, k_.split(","))
        by_state[int(newS[y, x])].append(nm)
    for v in by_state.values():
        if len(v) > 1:
            print(f"  NOTE: these named states are now one: {', '.join(v)}")

    put(L["Provinces"], P, np.ones((H, W), bool))
    put(L["States"], np.maximum(newS, 0), newS >= 0)
    put(L["Countries"], np.maximum(K, 0), K >= 0)
    put(L["Strategic Regions"], R, np.ones((H, W), bool))
    tmp = PDN.with_suffix(".tmp")
    write_pdn(PDN, tmp, [L[nm] for nm in names])
    shutil.move(tmp, PDN)
    print(f"wrote {PDN}")


if __name__ == "__main__":
    main()
