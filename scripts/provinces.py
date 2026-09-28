"""Cut the world into placeholder square provinces.

Provinces are bricks: squares whose odd rows are shifted by half a square, so only
three provinces meet at any grid corner (four would be an "X-crossing", which HOI4
rejects). Land, sea and lakes each get their own brick size; a brick clipped by a
coastline becomes one province per 4-connected piece. Slivers are merged into the
neighbour they share the most border with, and the remaining X-crossings (where a
coastline or the map's wrap seam cuts a brick corner) are repaired a pixel at a time.

Output work/provinces.npz:
    prov  int32  province index per pixel, 0..N-1
    kind  uint8  per province: 0 sea, 1 land, 2 lake
    cont  uint8  per province: continent 1..7 (0 for water)
"""
import numpy as np
from scipy.ndimage import find_objects
from skimage.measure import label as sklabel

from common import (MAP_W, MAP_H, LAND_CELL, SEA_CELL, LAKE_CELL, MIN_PROVINCE, MIN_FRACTION,
                    MAX_BOX)

W, H = MAP_W, MAP_H


def brick_ids(s):
    """Brick index per pixel for bricks of size s. Odd rows are offset by s/2; their
    half bricks at the map edges are folded into the neighbouring brick, so no brick
    straddles the wrap seam."""
    y = np.arange(H)[:, None]
    x = np.arange(W)[None, :]
    r = y // s
    odd = (r % 2 == 1)
    c = np.where(odd, (x - s // 2) // s, x // s)
    n = W // s
    c = np.where(odd, np.clip(c, 0, n - 2), c)
    return (r * n + c).astype(np.int64)


def adjacency(lab, wrap=True):
    """Shared-border lengths between 4-adjacent labels: dict (a, b) -> count, a < b."""
    pairs = [(lab[:, :-1], lab[:, 1:]), (lab[:-1, :], lab[1:, :])]
    if wrap:
        pairs.append((lab[:, -1:], lab[:, :1]))
    codes = []
    n = int(lab.max()) + 1
    for a, b in pairs:
        m = a != b
        lo = np.minimum(a[m], b[m]).astype(np.int64)
        hi = np.maximum(a[m], b[m]).astype(np.int64)
        codes.append(lo * n + hi)
    codes = np.concatenate(codes)
    u, cnt = np.unique(codes, return_counts=True)
    return u // n, u % n, cnt


def merge_small(lab, kind, cont, cell_area):
    """Merge pieces smaller than MIN_FRACTION of their brick (and anything under
    MIN_PROVINCE) into the same-kind neighbour they share the longest border with,
    preferring the same continent. A piece only merges into a strictly larger one, so
    merges never form cycles; pieces with no such neighbour (small islands, small
    lakes) stay as they are. Merges never cross the wrap seam or grow a province
    past MAX_BOX of the map."""
    max_h, max_w = H * MAX_BOX, W * MAX_BOX
    while True:
        n = len(kind)
        size = np.bincount(lab.ravel(), minlength=n)
        boxes = [[s.start for s in sl] + [s.stop for s in sl] for sl in find_objects(lab + 1)]
        a, b, cnt = adjacency(lab, wrap=False)
        keep = kind[a] == kind[b]
        a, b, cnt = a[keep], b[keep], cnt[keep]
        same_cont = (kind[a] != 1) | (cont[a] == cont[b])
        small = size < np.maximum(MIN_PROVINCE, MIN_FRACTION * cell_area[kind])
        best = {}
        for x, y, c, sc in zip(a, b, cnt, same_cont):
            for s_, t in ((x, y), (y, x)):
                if small[s_] and (size[t], t) > (size[s_], s_):
                    score = (bool(sc), int(c), int(size[t]))
                    if s_ not in best or score > best[s_][0]:
                        best[s_] = (score, t)
        parent = np.arange(n)
        grown = {}
        merged = 0
        for s_ in sorted(best, key=lambda k: size[k]):
            t = best[s_][1]
            if t in best:  # target is itself moving this round; retry next round
                continue
            y0, x0, y1, x1 = grown.get(t, boxes[t])
            sy0, sx0, sy1, sx1 = boxes[s_]
            box = (min(y0, sy0), min(x0, sx0), max(y1, sy1), max(x1, sx1))
            if box[2] - box[0] >= max_h or box[3] - box[1] >= max_w:
                continue
            grown[t] = box
            parent[s_] = t
            merged += 1
        if not merged:
            break
        uniq, inv = np.unique(parent[lab], return_inverse=True)
        lab = inv.reshape(H, W)
        kind, cont = kind[uniq], cont[uniq]
    return lab, kind, cont


def crossings(lab):
    """Top-left coordinates of every 2x2 window (wrapping in x) holding 4 provinces."""
    a = lab[:-1, :]
    b = np.roll(lab, -1, axis=1)[:-1, :]
    c = lab[1:, :]
    d = np.roll(lab, -1, axis=1)[1:, :]
    m = (a != b) & (a != c) & (a != d) & (b != c) & (b != d) & (c != d)
    return np.argwhere(m)


RING = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]


def removable(lab, y, x, p):
    """True if pixel (y, x) can leave province p without splitting it (local test)."""
    member = []
    for dy, dx in RING:
        yy = y + dy
        member.append(0 <= yy < H and lab[yy, (x + dx) % W] == p)
    edges = [member[i] for i in (0, 2, 4, 6)]
    if sum(edges) <= 1:
        return True
    # all edge neighbours in p must lie in one cyclic run of p pixels around the ring
    runs = []
    start = None
    for i in range(16):
        if member[i % 8] and start is None:
            start = i
        if not member[i % 8] and start is not None:
            runs.append((start, i))
            start = None
    if all(member):
        return True
    edge_idx = [i for i in (0, 2, 4, 6) if member[i]]
    for s, e in runs:
        covered = {i % 8 for i in range(s, e)}
        if all(i in covered for i in edge_idx):
            return True
    return False


def window_ok(lab, y, x):
    """No X-crossing in the 2x2 window whose top-left is (y, x)."""
    if y < 0 or y >= H - 1:
        return True
    vals = {lab[y, x % W], lab[y, (x + 1) % W], lab[y + 1, x % W], lab[y + 1, (x + 1) % W]}
    return len(vals) < 4


def touches_other_water(lab, kind, p, k):
    """Would water of kind k at pixel p touch the other kind of water (sea vs lake)?"""
    y, x = p
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        yy = y + dy
        if 0 <= yy < H:
            kk = kind[lab[yy, (x + dx) % W]]
            if kk != 1 and kk != k:
                return True
    return False


def repair(lab, kind, cont, size):
    """Break every X-crossing by giving one pixel of the window to an in-window
    4-neighbour's province, preferring same kind/continent and never splitting or
    shrinking a province below MIN_PROVINCE, or carrying one across the seam."""
    total = 0
    for rnd in range(50):
        xs = crossings(lab)
        if len(xs) == 0:
            return lab, total
        fixed = 0
        for y, x in xs:
            px = [(y, x), (y, (x + 1) % W), (y + 1, x), (y + 1, (x + 1) % W)]
            if len({lab[p] for p in px}) < 4:  # already fixed by an earlier repair
                continue
            partners = {0: (1, 2), 1: (0, 3), 2: (0, 3), 3: (1, 2)}
            cands = []
            for i in range(4):
                for j in partners[i]:
                    p, q = px[i], px[j]
                    src, dst = lab[p], lab[q]
                    # seam: a province may not reach across x = 0 / W-1
                    if abs(p[1] - q[1]) > 1:
                        continue
                    pri = 0 if kind[src] == kind[dst] else 2
                    if kind[src] == 1 and kind[dst] == 1 and cont[src] != cont[dst]:
                        pri = 1
                    cands.append((pri, -size[dst], p, q))
            cands.sort(key=lambda t: (t[0], t[1]))
            for pri, _, p, q in cands:
                src, dst = lab[p], lab[q]
                if size[src] - 1 < MIN_PROVINCE or not removable(lab, p[0], p[1], src):
                    continue
                if kind[dst] != 1 and touches_other_water(lab, kind, p, kind[dst]):
                    continue
                lab[p] = dst
                py, pxx = p
                if all(window_ok(lab, wy, wx) for wy in (py - 1, py) for wx in (pxx - 1, pxx)):
                    size[src] -= 1
                    size[dst] += 1
                    fixed += 1
                    break
                lab[p] = src
        total += fixed
        if fixed == 0:
            break
    left = crossings(lab)
    if len(left):
        raise RuntimeError(f"{len(left)} X-crossings could not be repaired, e.g. {left[:5].tolist()}")
    return lab, total


def validate(lab, kind):
    """Every rule HOI4 enforces on provinces.bmp that we can check here."""
    problems = []
    n = len(kind)
    size = np.bincount(lab.ravel(), minlength=n)
    if (size == 0).any():
        problems.append(f"{(size == 0).sum()} empty province ids")
    if size.min() < MIN_PROVINCE:
        problems.append(f"{(size < MIN_PROVINCE).sum()} provinces under {MIN_PROVINCE} px")
    regions = int(sklabel(lab, background=-1, connectivity=1).max())
    if regions != n:
        problems.append(f"{regions - n} provinces are split into several pieces")
    for i, sl in enumerate(find_objects(lab + 1)):
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if h >= H * MAX_BOX or w >= W * MAX_BOX:
            problems.append(f"province {i} box {w}x{h} too large")
    xs = crossings(lab)
    if len(xs):
        problems.append(f"{len(xs)} X-crossings, first at {xs[0].tolist()}")
    a, b, _ = adjacency(lab)
    ka, kb = kind[a], kind[b]
    if ((ka == 0) & (kb == 2) | (ka == 2) & (kb == 0)).any():
        problems.append("a lake touches the sea")
    return problems


def main():
    w = np.load("work/world.npz")
    pix_kind, pix_cont = w["kind"], w["cont"]  # pixel kind: 0 ocean, 1 land, 2 lake
    key = np.zeros((H, W), np.int64)
    land = pix_kind == 1
    key[land] = 1 + brick_ids(LAND_CELL)[land] * 8 + pix_cont[land]
    base = int(key.max()) + 1
    sea = pix_kind == 0
    key[sea] = base + brick_ids(SEA_CELL)[sea]
    base = int(key.max()) + 1
    lake = pix_kind == 2
    key[lake] = base + brick_ids(LAKE_CELL)[lake]
    # connected pieces of equal key; no brick crosses the seam, so no wrap handling
    lab = sklabel(key, background=-1, connectivity=1) - 1
    n = int(lab.max()) + 1
    kind = np.zeros(n, np.uint8)
    cont = np.zeros(n, np.uint8)
    kind[lab.ravel()] = pix_kind.ravel()
    cont[lab.ravel()] = pix_cont.ravel()
    print(f"{n} raw pieces")
    cell_area = np.array([SEA_CELL ** 2, LAND_CELL ** 2, LAKE_CELL ** 2], float)
    lab, kind, cont = merge_small(lab, kind, cont, cell_area)
    n = int(lab.max()) + 1
    size = np.bincount(lab.ravel(), minlength=n)
    print(f"{n} provinces after merging slivers; smallest {size.min()} px")
    lab, fixed = repair(lab, kind, cont, size)
    print(f"repaired {fixed} X-crossings")
    problems = validate(lab, kind)
    if problems:
        raise SystemExit("province map invalid:\n  " + "\n  ".join(problems))
    np.savez_compressed("work/provinces.npz", prov=lab.astype(np.int32), kind=kind, cont=cont)
    for k, nm in enumerate(["sea", "land", "lake"]):
        print(f"  {nm}: {(kind == k).sum()} provinces")


if __name__ == "__main__":
    main()
