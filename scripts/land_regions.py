"""Land strategic regions that follow the nations (2026-10-16, the author: "could you please regenerate them taking into
account the nations now on the map?"). By hand, after a build:

    python3 scripts/land_regions.py [--target PX] [--dry]

Until then the land regions were the placeholder build's: whole states bucketed on a 384 px grid, blind to borders.
Now each region is made of whole states and follows the nations:
  - a nation (its land on one continent) of more than 1.5 x TARGET px is cut into round(area / TARGET) regions of its
    own: centres placed by area-weighted k-means on its states, each state joining the centre nearest to it along the
    nation's own land (and short sea crossings to its islands);
  - a nation of 0.6 to 1.5 x TARGET is one region;
  - smaller nations are grouped with small neighbours (the longest shared border first, never past 1.25 x TARGET);
    a group still under 0.25 x TARGET joins the neighbouring region it shares most border with;
  - a lake joins the land region it borders most.
Sea regions (Merlo's) are left as they are. Writes the Strategic Regions layer of source/HOI4 Mod Map.pdn and
work/land_regions_preview.png; --dry writes only the preview. Rebuild afterwards, then run region_map.py: the
numbering changes.
"""
import sys
from collections import Counter, defaultdict

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

sys.path.insert(0, "scripts")
import json  # noqa: E402

from common import MAP_W as W, MAP_H as H  # noqa: E402

TARGET = 30000          # px of land a region aims at (the 80 grid regions averaged 46,575)
REACH = 40              # px of sea a nation's land reaches across to its islands (two coasts 80 px apart link)
SEED = 20261016


def args():
    a = sys.argv[1:]
    t = int(a[a.index("--target") + 1]) if "--target" in a else TARGET
    return t, "--dry" in a


def load():
    p = np.load("work/provinces.npz")
    r = np.load("work/regions.npz")
    j = json.load(open("work/regions.json"))
    return p["prov"], p["kind"], p["cont"], r["size"], r["centre"], r["state_of"], j


def links(prov, kind, state_of, adjacency):
    """state graph: land borders (px) and short sea crossings (weighted a quarter), as {(s, t): weight}"""
    w = Counter()
    for a, b, c in adjacency:
        sa, sb = state_of[a], state_of[b]
        if sa >= 0 and sb >= 0 and sa != sb and kind[a] == 1 and kind[b] == 1:
            w[min(sa, sb), max(sa, sb)] += c
    land = kind[prov] == 1
    dist, (iy, ix) = ndi.distance_transform_edt(~land, return_indices=True)
    near = np.where(land | (dist <= REACH), prov[iy, ix], -1)
    del dist, iy, ix
    for a, b, wa, wb in [(near[:, :-1], near[:, 1:], land[:, :-1], land[:, 1:]),
                         (near[:-1, :], near[1:, :], land[:-1, :], land[1:, :])]:
        m = (a >= 0) & (b >= 0) & (a != b) & ~(wa & wb)
        sa, sb = state_of[a[m]], state_of[b[m]]
        ok = (sa >= 0) & (sb >= 0) & (sa != sb)
        lo, hi = np.minimum(sa[ok], sb[ok]), np.maximum(sa[ok], sb[ok])
        u, cnt = np.unique(lo.astype(np.int64) * 100000 + hi, return_counts=True)
        for code, c in zip(u.tolist(), cnt.tolist()):
            w[code // 100000, code % 100000] += c / 4
    g = defaultdict(dict)
    for (s, t), c in w.items():
        g[s][t] = g[t][s] = c
    return g


def kmeans(xy, wt, k, rng):
    """area-weighted k-means on state centres, k-means++ start; returns the centres"""
    c = [xy[rng.choice(len(xy), p=wt / wt.sum())]]
    for _ in range(1, k):
        d = np.min([((xy - q) ** 2).sum(1) for q in c], 0) * wt
        c.append(xy[rng.choice(len(xy), p=d / d.sum())] if d.sum() else xy[rng.integers(len(xy))])
    c = np.array(c, float)
    for _ in range(30):
        lab = np.argmin(((xy[:, None] - c[None]) ** 2).sum(-1), 1)
        for i in range(k):
            if (lab == i).any():
                c[i] = (xy[lab == i] * wt[lab == i, None]).sum(0) / wt[lab == i].sum()
    return c


def split(units, xy, area, graph, k, rng):
    """cut a nation's states into k regions: each grows from the state nearest a k-means centre, along the nation's own
    land and short crossings (geodesic Voronoi); states it can't reach take the nearest centre"""
    import heapq
    idx = {s: i for i, s in enumerate(units)}
    cen = kmeans(xy, area.astype(float), k, rng)
    seeds = [int(np.argmin(((xy - c) ** 2).sum(1))) for c in cen]
    seeds = list(dict.fromkeys(seeds))
    best = {}
    heap = [(0.0, r, units[s]) for r, s in enumerate(seeds)]
    while heap:
        d, r, s = heapq.heappop(heap)
        if s in best:
            continue
        best[s] = r
        for t in graph.get(s, {}):
            if t in idx and t not in best:
                heapq.heappush(heap, (d + float(np.hypot(*(xy[idx[s]] - xy[idx[t]]))), r, t))
    sxy = xy[seeds]
    return {s: best.get(s, int(np.argmin(((sxy - xy[idx[s]]) ** 2).sum(1)))) for s in units}


def main():
    target, dry = args()
    prov, kind, cont, size, centre, state_of, j = load()
    states, owners = j["states"], j["owners"]
    ns = len(states)
    graph = links(prov, kind, state_of, j["adjacency"])
    s_area = np.array([size[g].sum() for g in states], float)
    s_xy = np.array([(centre[g] * size[g, None]).sum(0) / size[g].sum() for g in states])[:, ::-1]   # (x, y)
    s_cont = [Counter({int(cont[p]): int(size[p]) for p in g}).most_common(1)[0][0] for g in states]

    parts = defaultdict(list)                     # (tag, continent) -> states
    for s in range(ns):
        parts[owners[s], s_cont[s]].append(s)
    rng = np.random.default_rng(SEED)
    region = np.full(ns, -1)
    nreg = 0
    small = []
    for key in sorted(parts):
        u = parts[key]
        a = s_area[u].sum()
        if a > 1.5 * target:
            k = round(a / target)
            for s, r in split(u, s_xy[u], s_area[u], graph, k, rng).items():
                region[s] = nreg + r
            nreg += k
        elif a >= 0.6 * target:
            region[u] = nreg
            nreg += 1
        else:
            small.append(u)
    # small nations: grouped with small neighbours, the longest border first
    group = {}
    members = {}
    for i, u in enumerate(small):
        g = nreg + i
        members[g] = list(u)
        region[u] = g
    nreg += len(small)

    def area_of(g):
        return s_area[members[g]].sum() if g in members else s_area[region == g].sum()

    def borders(g):
        b = Counter()
        for s in (members[g] if g in members else np.nonzero(region == g)[0]):
            for t, c in graph.get(int(s), {}).items():
                if region[t] != g and s_cont[t] == s_cont[int(s)]:
                    b[int(region[t])] += c
        return b

    done = set()
    while True:
        open_ = sorted((g for g in members if g not in done and area_of(g) < 0.6 * target), key=area_of)
        if not open_:
            break
        g = open_[0]
        cand = [(c, -area_of(h), h) for h, c in borders(g).items()
                if h in members and area_of(g) + area_of(h) <= 1.25 * target]
        if not cand:
            done.add(g)
            continue
        h = max(cand)[2]
        region[members[g]] = h
        members[h] += members.pop(g)
    joined = 0
    for g in sorted(members, key=area_of):
        if g in members and area_of(g) < 0.25 * target:
            b = borders(g)
            if b:
                h = b.most_common(1)[0][0]
                region[members[g]] = h
                if h in members:
                    members[h] += members[g]
                del members[g]
                joined += 1
    # what is still under 0.1 x TARGET (islands with no neighbour within reach) joins the region nearest to it on its
    # continent (state centre to state centre)
    for r in sorted(set(region.tolist()), key=lambda r: s_area[region == r].sum()):
        mine = np.nonzero(region == r)[0]
        if not len(mine) or s_area[mine].sum() >= 0.1 * target:
            continue
        c = Counter(s_cont[s] for s in mine).most_common(1)[0][0]
        other = np.array([s for s in range(ns) if region[s] != r and s_cont[s] == c])
        if not len(other):
            continue
        d = ((s_xy[other][:, None] - s_xy[mine][None]) ** 2).sum(-1).min(1)
        region[mine] = region[other[int(np.argmin(d))]]
        joined += 1
    # renumber: continent by continent, north to south
    used = sorted(set(region.tolist()))
    cy = {r: (Counter(s_cont[s] for s in np.nonzero(region == r)[0]).most_common(1)[0][0],
              s_xy[region == r][:, 1].mean() // 420, s_xy[region == r][:, 0].mean()) for r in used}
    order = {r: i for i, r in enumerate(sorted(used, key=cy.get))}
    region = np.array([order[r] for r in region])
    n = len(used)

    # provinces: land by state; a lake joins the land region it borders most
    p_reg = np.full(len(kind), -1)
    land_p = np.nonzero((kind == 1) & (state_of >= 0))[0]
    p_reg[land_p] = region[state_of[land_p]]
    lake_b = defaultdict(Counter)
    for a, b, c in j["adjacency"]:
        for x, y in ((a, b), (b, a)):
            if kind[x] == 2 and p_reg[y] >= 0:
                lake_b[x][int(p_reg[y])] += c
    for x in np.nonzero(kind == 2)[0]:
        p_reg[x] = lake_b[x].most_common(1)[0][0]
    missing = np.nonzero((kind != 0) & (p_reg < 0))[0]
    assert not len(missing), f"provinces with no region: {missing[:10]}"

    # report
    ra = np.bincount(region, s_area, n)
    mixed = sum(len({owners[s] for s in np.nonzero(region == r)[0]}) > 1 for r in range(n))
    print(f"{n} land regions (target {target} px): {int(ra.min())} to {int(ra.max())} px, median {int(np.median(ra))}; "
          f"{mixed} hold more than one nation; {joined} small groups joined a neighbouring region")
    tag_regions = defaultdict(set)
    for s in range(ns):
        tag_regions[owners[s]].add(int(region[s]))
    big = sorted(((len(v), t) for t, v in tag_regions.items()), reverse=True)[:12]
    print("most regions:", ", ".join(f"{t} {k}" for k, t in big))
    for t in ("ROU", "GDN", "LST", "EVR", "HLR", "SGV", "LZC", "SGN"):
        if t in tag_regions:
            print(f"  {t}: region(s) {sorted(tag_regions[t])}")

    # colours: land regions never blue (the sea's), distinct from the sea regions on the layer
    sys.argv = sys.argv[:1]
    from pdn_tools import load as pdn_load, save as pdn_save, palette, code, put
    names, L = pdn_load()
    R = L["Strategic Regions"]
    rc = code(R[..., :3])
    sea_cols = set(np.unique(rc[kind[prov] == 0]).tolist())
    cols = np.array(palette(n, False, SEED, sea_cols), np.int64)
    pix = p_reg[prov]
    m = pix >= 0
    newc = np.where(m, cols[np.maximum(pix, 0)], rc)
    prev = Image.fromarray(np.stack([(newc >> 16) & 255, (newc >> 8) & 255, newc & 255], -1).astype(np.uint8))
    # borders of regions and nations, for the eye
    rb = np.zeros((H, W), bool)
    rb[:, 1:] |= pix[:, 1:] != pix[:, :-1]
    rb[1:] |= pix[1:] != pix[:-1]
    owner_px = np.full(len(kind), -1)
    tags = {t: i for i, t in enumerate(sorted(set(owners)))}
    owner_px[land_p] = [tags[owners[s]] for s in state_of[land_p]]
    op = owner_px[prov]
    nb = np.zeros((H, W), bool)
    nb[:, 1:] |= (op[:, 1:] != op[:, :-1]) & (op[:, 1:] >= 0) & (op[:, :-1] >= 0)
    nb[1:] |= (op[1:] != op[:-1]) & (op[1:] >= 0) & (op[:-1] >= 0)
    arr = np.asarray(prev).copy()
    arr[nb] = (250, 250, 250)
    arr[rb & m] = (20, 20, 20)
    Image.fromarray(arr).resize((W // 2, H // 2), Image.LANCZOS).save("work/land_regions_preview.png")
    print("wrote work/land_regions_preview.png")
    if dry:
        return
    put(R, newc, m)
    R[m, 3] = 255
    pdn_save(names, L)


if __name__ == "__main__":
    main()
