"""Turn rivers drawn as plain lines into HOI4's rivers.bmp format.

HOI4 wants every river one pixel wide, joined only edge to edge (never corner to
corner), with exactly one green source pixel per river system. A tributary ends in
a red "flow-in" pixel touching the river it joins. The author draws lines of any
colour on the "Major Rivers" and "Minor Rivers" layers, and this module works out
the rest:
  * each connected drawing is one river system. Its mouth is the end nearest to
    water, and it is extended to touch the water if it stops a few pixels short;
  * the main stem runs from the mouth to the farthest end, preferring major pixels;
    every side branch is a tributary, recursively;
  * diagonal steps get a corner pixel;
  * each pixel is major or minor after the layer it was drawn on (a river can change
    size along its course); major stretches widen from index 7 to 9 towards the mouth
    (HOI4 counts 7+ as large rivers), minor ones from 4 to 5 (small rivers).
"""
from collections import deque

import numpy as np
from scipy import ndimage as ndi
from skimage.morphology import skeletonize

NONE = 255
N4 = ((0, 1), (1, 0), (0, -1), (-1, 0))
N8 = N4 + ((1, 1), (1, -1), (-1, 1), (-1, -1))
MOUTH_REACH = 8  # a river ending this close to water is extended to reach it
MIN_BRANCH = 6   # shorter side branches are drawing slips, not tributaries


def trace(major, minor, land):
    """major, minor, land: HxW bool. Returns HxW uint8 rivers.bmp indices, NONE elsewhere."""
    h, w = land.shape
    drawn = (major | minor) & land
    skel = skeletonize(drawn)
    is_major = ndi.distance_transform_edt(~major) <= ndi.distance_transform_edt(~minor)
    water_dist, water_idx = ndi.distance_transform_edt(land, return_indices=True)
    out = np.full((h, w), NONE, np.uint8)
    placed = np.zeros((h, w), bool)
    lab, n = ndi.label(skel, np.ones((3, 3)))
    pixels = [[] for _ in range(n + 1)]
    for y, x in zip(*np.nonzero(skel)):
        pixels[lab[y, x]].append((int(y), int(x)))

    def nb8(p):
        y, x = p
        return [(y + dy, x + dx) for dy, dx in N8
                if 0 <= y + dy < h and 0 <= x + dx < w and skel[y + dy, x + dx]]

    def touches(p, own):
        """p is orthogonally next to a placed pixel that isn't in `own`."""
        y, x = p
        return any(0 <= y + dy < h and 0 <= x + dx < w and placed[y + dy, x + dx]
                   and (y + dy, x + dx) not in own for dy, dx in N4)

    def makes_block(p, extra):
        """Would p complete a 2x2 square of river pixels?"""
        ex = set(extra)

        def r(q):
            return 0 <= q[0] < h and 0 <= q[1] < w and (placed[q] or q in ex or q == p)
        y, x = p
        return any(all(r((y + a, x + b)) for a, b in ((0, 0), (dy, 0), (0, dx), (dy, dx)))
                   for dy in (-1, 1) for dx in (-1, 1))

    def orthogonal(path):
        """Insert a corner pixel at every diagonal step (land, not yet a river)."""
        res = [path[0]]
        for q in path[1:]:
            p = res[-1]
            if p[0] != q[0] and p[1] != q[1]:
                for c in ((p[0], q[1]), (q[0], p[1])):
                    if land[c] and not placed[c] and c not in res:
                        res.append(c)
                        break
            res.append(q)
        # shortcut loops and U-turns: if a pixel touches a later one edge to edge, the
        # pixels between only make the river thick
        k = 0
        while k < len(res) - 2:
            for j in range(min(len(res) - 1, k + 8), k + 1, -1):
                if abs(res[k][0] - res[j][0]) + abs(res[k][1] - res[j][1]) == 1:
                    del res[k + 1:j]
                    break
            k += 1
        return res

    def paint(path, marker_first, marker_last):
        """path runs upstream -> downstream; each pixel's size is the layer it was drawn on."""
        m = len(path)
        for k, p in enumerate(path):
            f = k / max(m - 1, 1)
            out[p] = (7 + min(int(f * 3), 2)) if is_major[p] else (4 + min(int(f * 2), 1))
            placed[p] = True
        if marker_first is not None:
            out[path[0]] = marker_first
        if marker_last is not None:
            out[path[-1]] = marker_last

    def link_up(trib):
        """A tributary that stops just short of its river: join it by the shortest clean
        path (up to 6 new pixels), from its end or up to 4 pixels back up it."""
        for back in range(min(5, len(trib) - 1)):
            base = trib[:len(trib) - back]
            prev = {base[-1]: None}
            dq = deque([(base[-1], 0)])
            while dq:
                q, d = dq.popleft()
                if d >= 6:
                    continue
                for dy, dx in N4:
                    c = (q[0] + dy, q[1] + dx)
                    if not (0 <= c[0] < h and 0 <= c[1] < w) or c in prev or c in base:
                        continue
                    if not land[c] or placed[c]:
                        continue
                    path, r = [c], q
                    while r != base[-1]:
                        path.append(r)
                        r = prev[r]
                    path.reverse()
                    if makes_block(c, base + path[:-1]):
                        continue
                    prev[c] = q
                    if touches(c, set(base) | set(path)):
                        return base + path
                    dq.append((c, d + 1))
        return trib

    for comp in range(1, n + 1):
        pts = pixels[comp]
        if len(pts) < 2:
            continue
        ends = [p for p in pts if len(nb8(p)) == 1] or pts
        mouth = min(ends, key=lambda p: water_dist[p])
        # tree by breadth-first search from the mouth
        parent = {mouth: None}
        order = [mouth]
        dq = deque([mouth])
        while dq:
            u = dq.popleft()
            for v in nb8(u):
                if v not in parent:
                    parent[v] = u
                    order.append(v)
                    dq.append(v)
        children = {p: [] for p in parent}
        for v, u in parent.items():
            if u is not None:
                children[u].append(v)
        # best leaf under every pixel: most major pixels, then longest
        best = {}
        for u in reversed(order):
            score = (int(is_major[u]), 1)
            if children[u]:
                cs = max((best[c] for c in children[u]), key=lambda t: t[0])
                best[u] = ((cs[0][0] + score[0], cs[0][1] + 1), cs[1])
            else:
                best[u] = (score, u)

        def path_down(leaf, stop):
            """Pixels from leaf down to (not including) stop."""
            res, p = [], leaf
            while p is not None and p != stop:
                res.append(p)
                p = parent[p]
            return res

        # main stem, extended to the water if it stops just short
        raw = path_down(best[mouth][1], None)
        stem = list(raw)
        if 0 < water_dist[mouth] - 1 <= MOUTH_REACH:
            wy, wx = water_idx[0][mouth], water_idx[1][mouth]
            y, x = mouth
            k = int(max(abs(wy - y), abs(wx - x)))
            ext = []
            for t in range(1, k + 1):
                q = (round(y + (wy - y) * t / k), round(x + (wx - x) * t / k))
                if not land[q]:
                    break
                if (not ext or q != ext[-1]) and q not in stem:
                    ext.append(q)
            stem = stem + ext
        stem = orthogonal(stem)
        paint(stem, 0, None)
        on_path = set(raw) | set(stem)
        # tributaries: every side branch off a painted river, nearest the mouth first
        queue = deque([raw])  # drawn (skeleton) paths, to find the branches off them
        while queue:
            river = queue.popleft()

            raw_set = set(river)
            for p0 in reversed(river):  # from the mouth up
                if p0 not in parent:
                    continue
                # a corner pixel added to the parent river may be where a branch joins:
                # its other children are branches too, joining at the corner
                joins = []
                for c in children[p0]:
                    if c in raw_set:
                        continue
                    if c in on_path:
                        joins += [(c, cc) for cc in children[c] if cc not in on_path]
                    else:
                        joins.append((p0, c))
                for p, c in joins:
                    raw_trib = path_down(best[c][1], p)
                    trib = raw_trib + [p]
                    trib = orthogonal(trib)[:-1]  # the join pixel belongs to the parent
                    # stop at the first pixel that touches another river: it is the red one
                    for k, q in enumerate(trib):
                        if touches(q, set(trib)):
                            trib = trib[:k + 1]
                            break
                    if len(trib) >= 2 and makes_block(trib[-1], trib):
                        trib = trib[:-1]  # joining there would make the river 2 px thick
                    if trib and not touches(trib[-1], set(trib)):
                        trib = link_up(trib)
                    if len(trib) < MIN_BRANCH or not touches(trib[-1], set(trib)):
                        continue  # loops and specks in the drawing, not real branches
                    paint(trib, None, 1)
                    on_path |= set(raw_trib) | set(trib)
                    queue.append(raw_trib)
    return out


def problems(riv, land):
    """HOI4's river rules, as a list of messages with (x, y) positions."""
    out = []
    r = riv != NONE
    if (r & ~land).any():
        ys, xs = np.nonzero(r & ~land)
        out.append(f"river pixels on water at ({xs[0]}, {ys[0]})")
    block = r[:-1, :-1] & r[1:, :-1] & r[:-1, 1:] & r[1:, 1:]
    if block.any():
        ys, xs = np.nonzero(block)
        out.append(f"river more than one pixel thick at ({xs[0]}, {ys[0]})")
    l4, n4 = ndi.label(r)
    l8, n8 = ndi.label(r, np.ones((3, 3)))
    if n4 != n8:
        diag = [i for i in range(1, n8 + 1) if len(np.unique(l4[l8 == i])) > 1]
        ys, xs = np.nonzero(l8 == diag[0])
        out.append(f"{len(diag)} rivers have a corner-to-corner step, e.g. near ({xs[0]}, {ys[0]})")
    greens = np.bincount(l4[riv == 0], minlength=n4 + 1)
    for i in range(1, n4 + 1):
        if greens[i] != 1:
            ys, xs = np.nonzero(l4 == i)
            out.append(f"a river has {greens[i]} green source pixels (needs exactly 1), "
                       f"near ({xs[0]}, {ys[0]})")
    return out
