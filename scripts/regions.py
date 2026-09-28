"""Group provinces into states and strategic regions, and pick anchor points.

States: land provinces bucketed by a STATE_CELL grid per continent, then split into
connected pieces. Pieces of fewer than MIN_STATE_PROVINCES (mostly small islands)
join the nearest state on the same continent if one is within ISLAND_REACH pixels,
so islands ride along with the coast they sit off.

Strategic regions: states bucketed by a REGION_CELL grid per continent, split into
connected groups; isolated island states join the nearest region on their
continent. Lakes go to the land region they border most. Sea provinces are bucketed
by SEA_REGION_CELL and split into connected groups (naval regions must be
contiguous); tiny sea groups merge into a neighbouring one.

Anchor point of a province: its pixel farthest from the province's edge, so
anything placed there (units, buildings, weather) sits inside it.

Writes work/regions.npz and work/regions.json.
"""
import json
from collections import defaultdict

import numpy as np
from scipy import ndimage as ndi

from common import (MAP_W, MAP_H, STATE_CELL, REGION_CELL, SEA_REGION_CELL,
                    MIN_STATE_PROVINCES, ISLAND_REACH, MIN_SEA_REGION_PROVINCES)
from provinces import adjacency

W, H = MAP_W, MAP_H


def anchors(lab, n):
    """Per province: the pixel farthest from its border (y, x) and its centroid."""
    edge = np.zeros((H, W), bool)
    edge[:, :-1] |= lab[:, :-1] != lab[:, 1:]
    edge[:, 1:] |= lab[:, :-1] != lab[:, 1:]
    edge[:-1, :] |= lab[:-1, :] != lab[1:, :]
    edge[1:, :] |= lab[:-1, :] != lab[1:, :]
    edge[:, 0] |= lab[:, 0] != lab[:, -1]
    edge[:, -1] |= lab[:, 0] != lab[:, -1]
    edge[0, :] = edge[-1, :] = True  # keep points off the top and bottom of the map
    d = ndi.distance_transform_edt(~edge)
    flat = lab.ravel()
    order = np.lexsort((-d.ravel(), flat))
    first = np.searchsorted(flat[order], np.arange(n))
    idx = order[first]
    ay, ax = np.divmod(idx, W)
    ys, xs = np.mgrid[0:H, 0:W]
    cnt = np.bincount(flat, minlength=n)
    cy = np.bincount(flat, ys.ravel(), minlength=n) / cnt
    cx = np.bincount(flat, xs.ravel(), minlength=n) / cnt
    return np.stack([ay, ax], 1), np.stack([cy, cx], 1), cnt


def components(members, nbrs):
    """Connected components of `members` under the neighbour sets `nbrs`."""
    members = set(members)
    out = []
    while members:
        s = members.pop()
        comp, stack = [s], [s]
        while stack:
            u = stack.pop()
            for v in nbrs[u]:
                if v in members:
                    members.remove(v)
                    comp.append(v)
                    stack.append(v)
        out.append(comp)
    return out


def group(items, key, nbrs):
    """Bucket items by key, then split every bucket into connected pieces."""
    buckets = defaultdict(list)
    for i in items:
        buckets[key(i)].append(i)
    out = []
    for k in sorted(buckets):
        out.extend(sorted(c) for c in components(buckets[k], nbrs))
    return out


def attach_small(groups, min_size, centre, cont, reach, nbrs_of_group):
    """Merge groups smaller than min_size into the nearest big group of the same
    continent (by centroid distance, within reach), preferring an adjacent one."""
    big = [g for g in groups if len(g) >= min_size]
    small = [g for g in groups if len(g) < min_size]
    if not big:
        return groups
    bc = np.array([np.mean([centre[i] for i in g], axis=0) for g in big])
    bcont = np.array([cont[g[0]] for g in big])
    for g in small:
        c = np.mean([centre[i] for i in g], axis=0)
        adj = nbrs_of_group(g)
        best, bestd = None, None
        for j, bg in enumerate(big):
            if bcont[j] != cont[g[0]]:
                continue
            dx = abs(bc[j][1] - c[1])
            dx = min(dx, W - dx)
            d = np.hypot(bc[j][0] - c[0], dx)
            if adj & set(bg):
                d = 0
            if bestd is None or d < bestd:
                best, bestd = j, d
        if best is not None and bestd <= reach:
            big[best] = big[best] + g
        else:
            big.append(g)
            bc = np.vstack([bc, c])
            bcont = np.append(bcont, cont[g[0]])
    return [sorted(g) for g in big]


def main():
    p = np.load("work/provinces.npz")
    lab, kind, cont = p["prov"], p["kind"], p["cont"]
    n = len(kind)
    anchor, centre, size = anchors(lab, n)
    a, b, cnt = adjacency(lab, wrap=True)
    nbrs = defaultdict(set)
    border = {}
    for x, y, c in zip(a, b, cnt):
        nbrs[x].add(y)
        nbrs[y].add(x)
        border[(x, y)] = border[(y, x)] = c
    land = [i for i in range(n) if kind[i] == 1]
    sea = [i for i in range(n) if kind[i] == 0]
    lakes = [i for i in range(n) if kind[i] == 2]
    land_nbrs = {i: {j for j in nbrs[i] if kind[j] == 1 and cont[j] == cont[i]} for i in land}

    # --- states
    def cell(i, size_):
        y, x = centre[i]
        return (int(cont[i]), int(y // size_), int(x // size_))

    states = group(land, lambda i: cell(i, STATE_CELL), land_nbrs)

    def nb_provs(g):
        s = set()
        for i in g:
            s |= land_nbrs[i]
        return s - set(g)

    states = attach_small(states, MIN_STATE_PROVINCES, centre, cont, ISLAND_REACH, nb_provs)
    state_of = np.full(n, -1)
    for s, g in enumerate(states):
        state_of[g] = s

    # --- land strategic regions (built from whole states)
    s_centre = np.array([np.average([centre[i] for i in g], axis=0, weights=[size[i] for i in g])
                         for g in states])
    s_cont = [int(cont[g[0]]) for g in states]
    s_nbrs = defaultdict(set)
    for s, g in enumerate(states):
        for i in g:
            for j in land_nbrs[i]:
                if state_of[j] != s:
                    s_nbrs[s].add(int(state_of[j]))
    lregions = group(range(len(states)),
                     lambda s: (s_cont[s], int(s_centre[s][0] // REGION_CELL),
                                int(s_centre[s][1] // REGION_CELL)), s_nbrs)

    def nb_states(g):
        out = set()
        for s in g:
            out |= s_nbrs[s]
        return out - set(g)

    lregions = attach_small(lregions, 2, s_centre, s_cont, REGION_CELL * 1.5, nb_states)

    # --- sea strategic regions
    sea_nbrs = {i: {j for j in nbrs[i] if kind[j] == 0} for i in sea}
    sregions = group(sea, lambda i: (int(centre[i][0] // SEA_REGION_CELL),
                                     int(centre[i][1] // SEA_REGION_CELL)), sea_nbrs)
    # merge tiny sea groups into the adjacent group they share most border with
    changed = True
    while changed:
        changed = False
        reg_of = {i: r for r, g in enumerate(sregions) for i in g}
        for r, g in enumerate(sregions):
            if len(g) >= MIN_SEA_REGION_PROVINCES:
                continue
            score = defaultdict(int)
            for i in g:
                for j in sea_nbrs[i]:
                    if reg_of[j] != r:
                        score[reg_of[j]] += border[(i, j)]
            if score:
                t = max(score, key=score.get)
                sregions[t] = sorted(sregions[t] + g)
                sregions[r] = []
                changed = True
                break
        sregions = [g for g in sregions if g]

    # --- assemble regions: land regions (provinces of their states + lakes), then sea
    regions = []
    region_of = np.full(n, -1)
    for g in lregions:
        provs = sorted(i for s in g for i in states[s])
        regions.append(dict(kind="land", states=sorted(g), provinces=provs))
    for g in sregions:
        regions.append(dict(kind="sea", states=[], provinces=sorted(g)))
    for r, reg in enumerate(regions):
        region_of[reg["provinces"]] = r
    for i in lakes:
        score = defaultdict(int)
        for j in nbrs[i]:
            if kind[j] == 1:
                score[region_of[j]] += border[(i, j)]
            elif kind[j] == 2 and region_of[j] >= 0:
                score[region_of[j]] += 1
        if not score:  # a lake ringed only by other lakes: take any lake-neighbour's later
            continue
        r = max(score, key=score.get)
        regions[r]["provinces"].append(i)
        region_of[i] = r
    for i in lakes:  # second pass for lakes that only touched other lakes
        if region_of[i] < 0:
            r = next(region_of[j] for j in nbrs[i] if region_of[j] >= 0)
            regions[r]["provinces"].append(i)
            region_of[i] = r
    for reg in regions:
        reg["provinces"].sort()
    assert (region_of >= 0).all(), "province without a strategic region"
    for s, g in enumerate(states):
        assert len({int(region_of[i]) for i in g}) == 1, f"state {s} spans regions"

    print(f"{len(states)} states, {len(lregions)} land regions, {len(sregions)} sea regions")
    sizes = [len(g) for g in states]
    print(f"  provinces per state: min {min(sizes)}, median {int(np.median(sizes))}, max {max(sizes)}")
    np.savez_compressed("work/regions.npz", anchor=anchor, centre=centre, size=size,
                        state_of=state_of, region_of=region_of)
    json.dump(dict(states=[[int(i) for i in g] for g in states],
                   regions=[dict(kind=r["kind"], states=[int(s) for s in r["states"]],
                                 provinces=[int(i) for i in r["provinces"]]) for r in regions],
                   adjacency=[[int(x), int(y), int(c)] for x, y, c in zip(a, b, cnt)]),
              open("work/regions.json", "w"))


if __name__ == "__main__":
    main()
