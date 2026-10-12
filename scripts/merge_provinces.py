"""Merge small provinces into a neighbour until HOI4 can draw every province border
(run by hand, after a build).

HOI4 draws at most 65,536 province borders (scripts/borders.py). Land outlined since
2026-09-29 is cut into ~150 px provinces, and by 2026-10-12 the map had 24,767
provinces and 73,231 borders: no province or state lines south of row ~1995. This
merges the smallest land provinces, one at a time, into a neighbour, until the borders
are down to TARGET:
  - only into a neighbour in the same state, so states, countries and regions stay as
    they are: the one it shares most boundary with, for that neighbour's size;
  - never across a river (rivers stay between provinces, see river_provinces.py), never
    two provinces that each hold a city dot (the build stops on that), and never into a
    province of more than MAX_SIZE px.
The merged province takes its neighbour's colour on the Provinces layer of
source/HOI4 Mod Map.pdn. Which provinces touch is read from that layer itself, not
from the build's province map, whose X-crossing fixes move single pixels (2026-10-12: a
merge of two provinces that touched only there came out in two pieces). The states,
kinds and rivers come from the last build (work/), which must match the .pdn: run
scripts/run_all.sh first.

    python3 scripts/merge_provinces.py [TARGET]      # default TARGET borders
"""
import heapq
import sys

import numpy as np
from scipy import ndimage as ndi
from skimage.measure import label

import pdn_tools as T
from borders import LIMIT, count

TARGET = 60_000  # under LIMIT with room for land not yet outlined (Solitas' 20 states)
MAX_SIZE = 400   # px: no merge makes a province bigger than this


def city_provinces(L, prov, kind):
    """Provinces holding a dot of the Cities layer (the nearest land province for a dot
    off the land, as read_layers.read_cities does)."""
    c = L.get("Necessary Cities", L.get("Cities"))
    out = set()
    if c is None:
        return out
    dots = label((c[..., 3] > 0) & (c[..., :3].max(-1) > 64), connectivity=2)
    land = kind[prov] == 1
    iy, ix = ndi.distance_transform_edt(~land, return_distances=False, return_indices=True)
    for sl in ndi.find_objects(dots):
        x, y = (sl[1].start + sl[1].stop - 1) // 2, (sl[0].start + sl[0].stop - 1) // 2
        out.add(int(prov[iy[y, x], ix[y, x]]))
    return out


def main():
    target = int(sys.argv[1]) if len(sys.argv) > 1 else TARGET
    p = np.load("work/provinces.npz")
    colors = p["colors"].astype(np.int64)
    ccode = (colors[:, 0] << 16) | (colors[:, 1] << 8) | colors[:, 2]
    names, L = T.load()
    layer = T.code(L["Provinces"][..., :3])
    ccode_u, prov = np.unique(layer, return_inverse=True)  # the layer's provinces, by colour
    prov = prov.reshape(layer.shape)
    if set(ccode_u.tolist()) != set(ccode.tolist()):
        sys.exit("work/ does not match the Provinces layer: run scripts/run_all.sh first")
    built = np.argsort(ccode)[np.searchsorted(np.sort(ccode), ccode_u)]  # layer -> build index
    kind = p["kind"][built]
    state = np.load("work/regions.npz")["state_of"][built]
    river = np.load("work/world.npz")["rivers"] < 254
    ccode = ccode_u
    H, W = prov.shape
    n = len(kind)
    n_pairs, n_borders = count(prov)
    print(f"{n} provinces, {n_borders} borders ({n_pairs} touching pairs); HOI4 draws {LIMIT}")
    if n_borders <= target:
        return

    # touching pairs and the boundary they share (the map wraps left to right)
    right = np.roll(prov, -1, axis=1)
    h, v = prov != right, prov[:-1] != prov[1:]
    a = np.r_[prov[h], prov[:-1][v]].astype(np.int64)
    b = np.r_[right[h], prov[1:][v]].astype(np.int64)
    keys, length = np.unique(np.minimum(a, b) * n + np.maximum(a, b), return_counts=True)
    nb = [dict() for _ in range(n)]
    for k, ln in zip(keys.tolist(), length.tolist()):
        i, j = divmod(k, n)
        nb[i][j] = nb[j][i] = ln
    # pairs a river runs between: a river pixel of one province beside the other
    ry, rx = np.nonzero(river)
    wet = set()
    for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        yy, xx = ry + dy, (rx + dx) % W
        ok = (yy >= 0) & (yy < H)
        i, j = prov[ry[ok], rx[ok]], prov[yy[ok], xx[ok]]
        d = i != j
        wet |= set(zip(np.minimum(i[d], j[d]).tolist(), np.maximum(i[d], j[d]).tolist()))
    city = np.zeros(n, bool)
    city[list(city_provinces(L, prov, kind))] = True

    size = np.bincount(prov.ravel(), minlength=n)
    parent = np.arange(n)
    heap = [(int(size[i]), i) for i in range(n) if kind[i] == 1 and state[i] >= 0]
    heapq.heapify(heap)
    pairs_now, goal = n_pairs, n_pairs - (n_borders - target)  # separate stretches stay as many
    merged = 0
    while pairs_now > goal and heap:
        s, i = heapq.heappop(heap)
        if parent[i] != i or s != size[i]:
            continue  # merged away, or grown since (pushed again with its new size)
        best, score = None, 0.0
        for j, ln in nb[i].items():
            if (kind[j] != 1 or state[j] != state[i] or (min(i, j), max(i, j)) in wet
                    or (city[i] and city[j]) or size[i] + size[j] > MAX_SIZE):
                continue
            sc = ln / np.sqrt(size[j])
            if sc > score:
                best, score = j, sc
        if best is None:
            continue
        j = best
        # i joins j: i's other borders become j's, or join j's own with the same province
        del nb[j][i]
        pairs_now -= 1
        for k, ln in nb[i].items():
            if k == j:
                continue
            del nb[k][i]
            if k in nb[j]:
                pairs_now -= 1
                nb[j][k] += ln
                nb[k][j] += ln
            else:
                nb[j][k] = nb[k][j] = ln
            if (min(i, k), max(i, k)) in wet:
                wet.add((min(j, k), max(j, k)))
        nb[i] = {}
        parent[i] = j
        size[j] += size[i]
        city[j] |= city[i]
        merged += 1
        heapq.heappush(heap, (int(size[j]), j))

    root = parent.copy()
    while (root != root[root]).any():
        root = root[root]
    new = ccode[root][prov]
    L["Provinces"][..., 0] = (new >> 16) & 255
    L["Provinces"][..., 1] = (new >> 8) & 255
    L["Provinces"][..., 2] = new & 255
    after = count(np.unique(new, return_inverse=True)[1].reshape(new.shape))[1]
    landsz = size[(root == np.arange(n)) & (kind == 1)]
    print(f"{merged} provinces merged into a neighbour: {n - merged} provinces, about {after} "
          f"borders before the build's X-crossing fixes; land provinces {landsz.mean():.0f} px on "
          f"average (largest {landsz.max()})")
    T.save(names, L)


if __name__ == "__main__":
    main()
