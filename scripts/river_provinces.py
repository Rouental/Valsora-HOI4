"""Cut provinces along rivers, so rivers run between provinces (run by hand).

HOI4 applies a river's combat penalty only when the river lies between the two
provinces of an attack; a river through the middle of a province is scenery. So every
state a river crosses gets new provinces (~PROVINCE_AREA px, organic borders, as
apply_outlines.py cuts them): the state's land minus the river splits into the
separate banks, each bank is cut into provinces, and the river pixels join the
province beside them. States, countries and regions do not change.

The river pixels are the ones the build draws (work/world.npz from the last run of
run_all.sh), not the raw lines, so they sit exactly on the new borders. Rebuild first.

Only states where under ALIGNED of the river pixels lie on a province border are cut
(2026-10-06: Merlovich's and Hoalepa's rivers, drawn later, were 13-58 % on borders).

    python3 scripts/river_provinces.py        # edits source/HOI4 Mod Map.pdn in place
"""
import numpy as np
from scipy import ndimage as ndi
from skimage.measure import label

import pdn_tools as T
from apply_outlines import Colours, organic_split, PROVINCE_AREA
from common import MIN_PROVINCE

CROSS = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])
ALIGNED = 0.85  # a state is done when this share of its river pixels lies on a border


def main():
    names, L = T.load()
    world = np.load("work/world.npz")
    river = world["rivers"] < 254
    ter = T.code(L["Terrain"][..., :3])
    land = (ter != T.code(np.array(T.OCEAN))) & (ter != T.code(np.array(T.LAKES)))
    if (river & ~land).any() or river.shape != land.shape:
        raise SystemExit("work/world.npz does not match the .pdn: run scripts/run_all.sh first")
    P = T.code(L["Provinces"][..., :3])
    St = np.where(L["States"][..., 3] > 0, T.code(L["States"][..., :3]), -1)
    cols = Colours(P, 5)
    touched = np.unique(St[river & (St >= 0)])
    # states whose rivers already run along province borders are left alone (re-cutting
    # them would only reshuffle provinces): ALIGNED of their river pixels on a border
    border = np.zeros(P.shape, bool)
    for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        border |= np.roll(P, (dy, dx), (0, 1)) != P
    ok = [sc for sc in touched
          if (border & river & (St == sc)).sum() >= ALIGNED * (river & (St == sc)).sum()]
    print(f"{len(ok)} of {len(touched)} states crossed by rivers already have them on borders")
    touched = np.setdiff1d(touched, ok)
    old = new = 0
    for n, sc in enumerate(touched):
        ys, xs = np.nonzero((St == sc) & land)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        m = np.zeros((y1 - y0, x1 - x0), bool)
        m[ys - y0, xs - x0] = True
        rv = river[y0:y1, x0:x1] & m
        old += len(np.unique(P[y0:y1, x0:x1][m]))
        out = np.zeros(m.shape, np.int64)  # 0 = not yet given
        banks = label(m & ~rv, connectivity=1)
        for b in range(1, banks.max() + 1):
            by, bx = np.nonzero(banks == b)
            if len(by) < MIN_PROVINCE:
                continue  # a scrap: joins the province beside it, below
            k = max(1, round(len(by) / PROVINCE_AREA))
            parts = organic_split(by + y0, bx + x0, k, seed=int(sc) % 100000 + b)
            for q in range(k):
                if (parts == q).any():
                    out[by[parts == q], bx[parts == q]] = cols.new()
                    new += 1
        if not out.any():  # too small to split: one province, as before
            out[m] = cols.new()
            new += 1
        # river pixels and scraps take the nearest province (their neighbour)
        miss = m & (out == 0)
        idx = ndi.distance_transform_edt(out == 0, return_distances=False, return_indices=True)
        out[miss] = out[idx[0][miss], idx[1][miss]]
        # the nearest province may be across a diagonal: keep each one a single piece
        for c in np.unique(out[m]):
            comp = label(out == c, connectivity=1)
            if comp.max() > 1:
                keep = np.bincount(comp.ravel())[1:].argmax() + 1
                for j in range(1, comp.max() + 1):
                    if j != keep:
                        pm = comp == j
                        ring = ndi.binary_dilation(pm, CROSS) & ~pm & m & (out != c)
                        if ring.any():
                            v, cnt = np.unique(out[ring], return_counts=True)
                            out[pm] = v[cnt.argmax()]
        win = P[y0:y1, x0:x1]
        win[m] = out[m]
    # last, over every state touched: stray bits (a state pixel cut off by the river)
    # join the land province beside them, even across a state line
    ys, xs = np.nonzero(np.isin(St, touched) & land)
    sl = np.s_[max(ys.min() - 2, 0):ys.max() + 3, max(xs.min() - 2, 0):xs.max() + 3]
    win, wl = P[sl], land[sl]
    fixed = 0
    for c in np.unique(win[wl]):  # neighbours too: a province may straddle states
        ys, xs = np.nonzero((win == c) & wl)
        if ys.min() == 0 or xs.min() == 0 or ys.max() == win.shape[0] - 1 or xs.max() == win.shape[1] - 1:
            continue  # reaches past the window: can't be judged here
        box = np.s_[ys.min():ys.max() + 2, xs.min():xs.max() + 2]
        comp = np.zeros(win.shape, np.int32)
        comp[box] = label((win[box] == c) & wl[box], connectivity=1)
        sizes = np.bincount(comp.ravel())[1:]
        keep = sizes.argmax() + 1
        for j in range(1, len(sizes) + 1):
            if j == keep and sizes[j - 1] >= MIN_PROVINCE:
                continue
            pm = comp == j
            ring = ndi.binary_dilation(pm, CROSS) & ~pm & wl & (win != c)
            if ring.any():
                v, cnt = np.unique(win[ring], return_counts=True)
                win[pm] = v[cnt.argmax()]
                fixed += 1
    T.put(L["Provinces"], P, np.ones(P.shape, bool))
    print(f"{fixed} stray bits joined a neighbouring province")
    print(f"{len(touched)} states crossed by rivers: {old} provinces became {new}")
    T.save(names, L)


if __name__ == "__main__":
    main()
