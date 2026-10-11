"""Sea provinces and sea regions from the "Ocean Province Lines" layer of
source/HOI4 Mod Map.pdn: Merlo's hand-drawn sea borders (2026-10-12). Run by hand.

    python3 scripts/sea_provinces.py build
        The sea provinces from the lines: every area the lines enclose is a province.
        A line pixel stays in the province it is in while that province borders it, and
        otherwise joins the nearest, so unchanged lines give back the same provinces. An
        area over HOI4's size limit (a box of 1/8 of the map either way) is cut by
        wobbly lines (Merlo's method), which are drawn into the layer too. Each province
        keeps the colour and sea region of the old province it overlaps most; new ones
        get new blues. Sea regions are kept connected (across the wrap too).
    python3 scripts/sea_provinces.py seam
        Make the left/right wrap seamless, then as build. Every border that meets one
        edge of the map meets the other at the same row: two that nearly meet are bent
        to meet halfway, and one without a partner is continued across the wrap, unless
        it only marks a province that touches the edge for a few rows, which is pulled
        back from it. The lines along the edges are redrawn from the result. The two
        provinces facing each other across the wrap then share a sea region (the choice
        that keeps the regions' sizes most even).
    python3 scripts/sea_provinces.py names
        Name the sea regions "<ocean> <n>" in source/region_names.json, numbered west to
        east within each ocean (a region's ocean is its old name without the number).
    python3 scripts/sea_provinces.py check
        Report, changing nothing: provinces the lines would change, areas over the size
        limit, and borders or regions that don't meet across the wrap.

The .pdn is decoded to work/pdn_tools and saved over itself (pdn_tools.load / save).
"""
import json
import re
import sys
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi

from common import MAP_W as W, MAP_H as H
from pdn_tools import load, save, palette, code, OCEAN, CROSS

LINES = "Ocean Province Lines"
NAMES = Path("source/region_names.json")
MIN_AREA = 300                       # smaller areas between the lines go to a neighbour
# HOI4: a province's box must stay under 1/8 of the map each way (320 x 640 px). Areas
# within 3 px of that are cut, into parts with a margin (Merlo's) for border pixels
OVER_H, OVER_W = H / 8 - 3, W / 8 - 3
LIM_H, LIM_W = H / 8 - 9, W / 8 - 9
MIN_PART = 3500                      # the smallest piece an over-size area is cut into
GAP = 40       # seam: borders on the two edges more than 2 * GAP rows apart don't pair up
SHORT = 40     # seam: a province touching an edge for fewer rows is pulled back from it
TARGET = 9     # seam: the provinces per sea region the region choice aims for


# ------------------------------------------------------------------ provinces from lines

def areas(ocean, line, P):
    """Sea pixel -> area 1..n (0 elsewhere): the areas the lines enclose. Line pixels and
    slivers under MIN_AREA go to the area holding their current province (P, colour
    codes) if it is within 3 px, else to the nearest area."""
    lab, n = ndi.label(ocean & ~line, CROSS)
    size = np.bincount(lab.ravel(), minlength=n + 1)
    keep = np.nonzero(size >= MIN_AREA)[0]
    keep = keep[keep > 0]
    remap = np.zeros(n + 1, np.int64)
    remap[keep] = np.arange(1, len(keep) + 1)
    lab = remap[lab]
    n = len(keep)
    m = lab > 0
    pairs, cnt = np.unique(np.stack([lab[m], P[m]], 1), axis=0, return_counts=True)
    best = {}
    for (a, c), k in zip(pairs.tolist(), cnt.tolist()):
        if k > best.get(a, (0, 0))[0]:
            best[a] = (k, c)
    holder = {}
    for a, (k, c) in best.items():
        if k > holder.get(c, (0, 0))[0]:
            holder[c] = (k, a)
    ys, xs = np.nonzero(ocean & (lab == 0))
    cur = np.array([holder.get(c, (0, 0))[1] for c in P[ys, xs].tolist()], np.int64)
    ok = np.zeros(len(ys), bool)
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            ok |= lab[np.clip(ys + dy, 0, H - 1), np.clip(xs + dx, 0, W - 1)] == cur
    ok &= cur > 0
    iy, ix = ndi.distance_transform_edt(lab == 0, return_distances=False, return_indices=True)
    full = lab.copy()
    full[ys, xs] = np.where(ok, cur, lab[iy[ys, xs], ix[ys, xs]])
    full[~ocean] = 0
    return full, n


def window(sl, pad=2):
    return (slice(max(0, sl[0].start - pad), min(H, sl[0].stop + pad)),
            slice(max(0, sl[1].start - pad), min(W, sl[1].stop + pad)))


def connect(full):
    """Every area one 4-connected piece: other pieces join the area they border most."""
    for _ in range(8):
        changed = 0
        for a, sl in enumerate(ndi.find_objects(full), 1):
            if sl is None:
                continue
            win = window(sl)
            sub = full[win]
            lab, k = ndi.label(sub == a, CROSS)
            if k <= 1:
                continue
            sizes = np.bincount(lab.ravel())[1:]
            big = 1 + int(np.argmax(sizes))
            for j in range(1, k + 1):
                if j == big:
                    continue
                piece = lab == j
                ring = ndi.binary_dilation(piece, CROSS) & ~piece & (sub > 0) & (sub != a)
                if ring.any():
                    sub[piece] = np.bincount(sub[ring]).argmax()
                    changed += 1
        if not changed:
            return


def cut_big(full, ocean, line):
    """Cut the areas over the size limit into parts by wobbly borders (Merlo's method:
    k-means over the pixels, the borders shifted by smooth noise), and draw the cuts
    into the lines. Deterministic: the noise and each area's tries are seeded."""
    big = []
    for a, sl in enumerate(ndi.find_objects(full), 1):
        if sl is not None and (sl[0].stop - sl[0].start > OVER_H or sl[1].stop - sl[1].start > OVER_W):
            big.append((a, sl))
    if not big:
        return 0
    rng = np.random.default_rng(11)

    def noise(sig, amp):
        f = ndi.gaussian_filter(rng.standard_normal((H, W)), sig)
        return f / f.std() * amp
    ny, nx = noise(30, 14) + noise(8, 3), noise(30, 14) + noise(8, 3)
    nxt = int(full.max()) + 1
    parent = np.zeros(full.shape, np.int64)
    for a, sl in big:
        sub = full[sl]
        m = sub == a
        ys, xs = np.nonzero(m)
        h, w = m.shape
        first = int(ys[0] + sl[0].start) * W + int(xs[0] + sl[1].start)

        def fits(pm):
            py, px = np.nonzero(pm)
            return py.max() - py.min() + 1 <= LIM_H and px.max() - px.min() + 1 <= LIM_W
        done = False
        for kk in range(max(2, int(np.ceil(max(h / LIM_H, w / LIM_W)))), 12):
            for tr in range(25):
                r = np.random.default_rng(first * 100 + kk * 25 + tr)
                pts = np.stack([ys, xs], 1).astype(float)
                c = pts[r.choice(len(pts), kk, replace=False)]
                for _ in range(8):
                    lab = ((pts[:, None, :] - c[None]) ** 2).sum(2).argmin(1)
                    c = np.array([pts[lab == j].mean(0) if (lab == j).any() else c[j] for j in range(kk)])
                wp = np.stack([ys + ny[sl][ys, xs], xs + nx[sl][ys, xs]], 1)
                lab = ((wp[:, None, :] - c[None]) ** 2).sum(2).argmin(1)
                part = np.zeros(m.shape, np.int64)
                part[ys, xs] = lab + 1
                for j in range(1, kk + 1):
                    l2, k2 = ndi.label(part == j, CROSS)
                    if k2 > 1:
                        sz = np.bincount(l2.ravel())[1:]
                        part[(l2 > 0) & (l2 != 1 + sz.argmax())] = 0
                gap = (part == 0) & m
                if gap.any():
                    iy, ix = ndi.distance_transform_edt(part == 0, return_distances=False, return_indices=True)
                    part[gap] = part[iy[gap], ix[gap]]
                if min((part == j).sum() for j in range(1, kk + 1)) < MIN_PART:
                    continue
                if all(fits(part == j) for j in range(1, kk + 1)):
                    for j in range(2, kk + 1):
                        sub[part == j] = nxt
                        nxt += 1
                    parent[sl][m] = a
                    done = True
                    break
            if done:
                break
        if not done:
            sys.exit(f"could not cut the area at {first % W},{first // W} under the size limit")
    # the cuts: borders between parts of one area
    b = np.zeros(full.shape, bool)
    same = (parent[:, :-1] == parent[:, 1:]) & (parent[:, :-1] > 0)
    b[:, :-1] |= (full[:, :-1] != full[:, 1:]) & same
    same = (parent[:-1] == parent[1:]) & (parent[:-1] > 0)
    b[:-1] |= (full[:-1] != full[1:]) & same
    line |= ndi.binary_dilation(b, structure=np.ones((2, 2), bool)) & ocean
    return len(big)


def colours(full, P, ocean):
    """Area -> province colour: the old colour it overlaps most, each colour used once;
    the rest get new blues."""
    n = int(full.max())
    m = full > 0
    pairs, cnt = np.unique(np.stack([full[m], P[m]], 1), axis=0, return_counts=True)
    land = set(np.unique(P[~ocean]).tolist())
    col = np.zeros(n + 1, np.int64)
    taken = set()
    for k, a, c in sorted(zip(cnt.tolist(), pairs[:, 0].tolist(), pairs[:, 1].tolist()), reverse=True):
        if col[a] == 0 and c not in taken and c not in land:
            col[a] = c
            taken.add(c)
    new = [a for a in range(1, n + 1) if col[a] == 0 and (full == a).any()]
    for a, c in zip(new, palette(len(new), True, 31, set(np.unique(P).tolist()) | taken)):
        col[a] = c
    return col, len(new)


def neighbours(full):
    """Area -> neighbouring areas, across the wrap too."""
    nb = defaultdict(set)
    for a, b in ((full[:, :-1], full[:, 1:]), (full[:-1], full[1:]), (full[:, -1:], full[:, :1])):
        m = (a != b) & (a > 0) & (b > 0)
        for u, v in set(zip(a[m].tolist(), b[m].tolist())):
            nb[u].add(v)
            nb[v].add(u)
    return nb


def components(members, nb):
    members, out = set(members), []
    while members:
        s = members.pop()
        comp, stack = {s}, [s]
        while stack:
            for v in nb[stack.pop()]:
                if v in members:
                    members.discard(v)
                    comp.add(v)
                    stack.append(v)
        out.append(comp)
    return out


def regions(full, R, nb):
    """Area -> sea region colour: the region it overlaps most; then every region is made
    one connected group (stray groups join the neighbouring region they touch most)."""
    n = int(full.max())
    m = full > 0
    pairs, cnt = np.unique(np.stack([full[m], R[m]], 1), axis=0, return_counts=True)
    reg = np.zeros(n + 1, np.int64)
    best = np.zeros(n + 1, np.int64)
    for (a, r), k in zip(pairs.tolist(), cnt.tolist()):
        if k > best[a]:
            best[a], reg[a] = k, r
    size = np.bincount(full.ravel(), minlength=n + 1)
    for _ in range(10):
        fixed = 0
        for r in set(reg[1:].tolist()) - {0}:
            comps = components([a for a in range(1, n + 1) if reg[a] == r], nb)
            comps.sort(key=lambda c: -sum(size[a] for a in c))
            for comp in comps[1:]:
                votes = Counter(reg[v] for a in comp for v in nb[a] if reg[v] != r)
                if votes:
                    new = votes.most_common(1)[0][0]
                    for a in comp:
                        reg[a] = new
                    fixed += 1
        if not fixed:
            break
    return reg


# ------------------------------------------------------------------ the seam

def edge_runs(full, x):
    """[[first row, last row, area], ...] down the edge column x (sea only)."""
    runs = []
    for y, a in enumerate(full[:, x].tolist()):
        if a and runs and runs[-1][2] == a and runs[-1][1] == y - 1:
            runs[-1][1] = y
        elif a:
            runs.append([y, y, a])
    return runs


def breaks(runs):
    """[(row, index of the run above)]: where one area follows another down an edge."""
    return [(runs[i][1], i) for i in range(len(runs) - 1) if runs[i][1] + 1 == runs[i + 1][0]]


def match(a, b):
    """Pair up two sorted lists of rows: [(i, j)], least total distance, GAP per row left."""
    n, m = len(a), len(b)
    cost = np.zeros((n + 1, m + 1))
    cost[:, 0] = GAP * np.arange(n + 1)
    cost[0, :] = GAP * np.arange(m + 1)
    back = {}
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost[i, j], back[i, j] = min((cost[i - 1, j - 1] + abs(a[i - 1] - b[j - 1]), "m"),
                                         (cost[i - 1, j] + GAP, "a"), (cost[i, j - 1] + GAP, "b"))
    out, i, j = [], n, m
    while i and j:
        t = back[i, j]
        if t == "m":
            out.append((i - 1, j - 1))
        i, j = i - (t != "b"), j - (t != "a")
    return out[::-1]


def shift_border(full, x0, step, up, down, row, target, band):
    """Bend the border between areas `up` and `down` that meets the edge column x0 after
    row `row` so that it meets it after `target`, the change fading over `band` columns."""
    prev = row
    for d in range(band):
        u = d / band
        s = int(round((target - row) * (1 - (3 * u * u - 2 * u ** 3))))
        x = x0 + step * d
        col = full[:, x]
        ys = [y for y in range(max(0, prev - 20), min(H - 1, prev + 20)) if col[y] == up and col[y + 1] == down]
        if not ys:
            break
        yb = min(ys, key=lambda y: abs(y - prev))
        if s > 0:
            for y in range(yb + 1, min(H, yb + 1 + s)):
                if col[y] != down:
                    break
                col[y] = up
        elif s < 0:
            for y in range(yb, max(-1, yb + s), -1):
                if col[y] != up:
                    break
                col[y] = down
        prev = yb
        if s == 0:
            break
    return d


def pull_back(full, x0, step, run, up, down):
    """Take the province of `run` ([first, last, area]) away from the edge column x0. It
    reaches the edge by a neck (often just the pixels of a line drawn along the edge): the
    columns, from the edge in, where it stays under twice the height of its contact. Those
    pixels go to the areas above and below it, split at the contact's middle row."""
    y0, y1, a = run
    h = y1 - y0 + 1
    mid = (y0 + y1) // 2
    lo, hi = max(0, y0 - h - 10), min(H, y1 + h + 11)
    depth = 0
    for d in range(60):
        ys = np.nonzero(full[lo:hi, x0 + step * d] == a)[0]
        if d >= 2 and len(ys) and ys.max() - ys.min() + 1 > 2 * h:
            break
        depth = d + 1
    for d in range(depth):
        x = x0 + step * d
        for y in range(lo, hi):
            if full[y, x] == a:
                full[y, x] = up if y <= mid else down
    return depth


def border_slope(full, x0, step, up, down, row, span=15):
    """Rows the border between up and down drops per column, coming towards the edge."""
    prev, rows = row, [row]
    for d in range(1, span + 1):
        col = full[:, x0 + step * d]
        ys = [y for y in range(max(0, prev - 10), min(H - 1, prev + 10)) if col[y] == up and col[y + 1] == down]
        if not ys:
            break
        prev = min(ys, key=lambda y: abs(y - prev))
        rows.append(prev)
    if len(rows) < 4:
        return 0.0
    return float(np.clip((rows[0] - rows[-1]) / (len(rows) - 1), -0.6, 0.6))


def split_area(full, x0, step, row, slope, seed):
    """Cut the area at the edge pixel (row, x0) in two by a new border that leaves the
    edge between rows row and row + 1 and runs inwards (falling `slope` rows per column,
    easing off, with a little wobble) until the area is cut; the part above becomes a new
    area. Returns the columns used."""
    a = int(full[row, x0])
    wob = ndi.gaussian_filter1d(np.random.default_rng(seed).standard_normal(600), 8)
    wob = wob / wob.std() * 1.2
    cut = []
    iy = row + 1
    new = int(full.max()) + 1
    for d in range(600):
        x = x0 + step * d
        want = row + 1 + slope * 60 * (1 - np.exp(-d / 60)) + wob[d] - wob[0]
        iy = int(np.clip(round(want), iy - 1, iy + 1))
        if full[iy, x] != a:
            break
        cut.append((iy, x))
    ys, xs = np.nonzero(full == a)
    sl = (slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1))
    m = full[sl] == a
    for y, x in cut:
        m[y - sl[0].start, x - sl[1].start] = False
    lab, _ = ndi.label(m, CROSS)
    top = lab[row - sl[0].start, x0 - sl[1].start]
    if top == 0 or top == lab[min(row + 2, ys.max()) - sl[0].start, x0 - sl[1].start]:
        sys.exit(f"could not split the area at the edge row {row}")
    full[sl][lab == top] = new
    return len(cut)


def seam(full, ocean):
    """Make the province borders meet across the wrap; returns the columns changed on
    the left and right edges."""
    sides = ((0, 1), (W - 1, -1))
    used = [6, 6]
    for stage in ("pull back", "continue", "meet"):
        for _ in range(50):
            runs = [edge_runs(full, x) for x, _ in sides]
            brk = [breaks(r) for r in runs]
            pairs = match([b[0] for b in brk[0]], [b[0] for b in brk[1]])
            paired = [{i for i, _ in pairs}, {j for _, j in pairs}]
            todo = None
            if stage == "pull back":
                for s in (0, 1):
                    for k, (row, i) in enumerate(brk[s]):
                        if k in paired[s]:
                            continue
                        r = runs[s]
                        for ri in (i, i + 1):  # the run above or below this border
                            if r[ri][1] - r[ri][0] + 1 < SHORT and 0 < ri < len(r) - 1:
                                todo = (s, ri)
                                break
                        if todo:
                            break
                    if todo:
                        break
                if todo:
                    s, ri = todo
                    r = runs[s]
                    x0, step = sides[s]
                    print(f"seam: the province at rows {r[ri][0]}-{r[ri][1]} of the "
                          f"{'left' if s == 0 else 'right'} edge is pulled back from it")
                    used[s] = max(used[s], pull_back(full, x0, step, r[ri], r[ri - 1][2], r[ri + 1][2]) + 4)
                    connect(full)
                    continue
            elif stage == "continue":
                for s in (0, 1):
                    for k, (row, i) in enumerate(brk[s]):
                        if k not in paired[s]:
                            todo = (s, row, i)
                            break
                    if todo:
                        break
                if todo:
                    s, row, i = todo
                    x0, step = sides[s]
                    ox, ostep = sides[1 - s]
                    slope = border_slope(full, x0, step, runs[s][i][2], runs[s][i + 1][2], row)
                    print(f"seam: the border at row {row} of the {'left' if s == 0 else 'right'} edge "
                          f"is continued across the wrap")
                    used[1 - s] = max(used[1 - s], split_area(full, ox, ostep, row, slope, row) + 4)
                    connect(full)
                    continue
            else:
                for i, j in pairs:
                    rl, rr = brk[0][i][0], brk[1][j][0]
                    if rl == rr:
                        continue
                    t = (rl + rr) // 2
                    band = int(min(80, max(12, 3 * abs(rl - rr) + 8)))
                    for s, (row, ri) in ((0, brk[0][i]), (1, brk[1][j])):
                        if row != t:
                            x0, step = sides[s]
                            r = runs[s]
                            used[s] = max(used[s], shift_border(full, x0, step, r[ri][2], r[ri + 1][2], row, t, band) + 4)
                    print(f"seam: borders at rows {rl} (left) and {rr} (right) now meet at {t}")
                connect(full)
                runs = [edge_runs(full, x) for x, _ in sides]
                lb, rb = [b[0] for b in breaks(runs[0])], [b[0] for b in breaks(runs[1])]
                if lb != rb:
                    sys.exit(f"seam: the borders still don't meet: left {lb}, right {rb}")
            break
    return used


def redraw_lines(full, ocean, line, used):
    """The lines within `used` columns of each edge become the borders of the areas there
    (both sides of each border, as wide as Merlo's lines); outside, they stay as drawn."""
    band = np.zeros(full.shape, bool)
    band[:, :used[0]] = True
    band[:, W - used[1]:] = True
    e = np.zeros(full.shape, bool)
    h = (full[:, :-1] != full[:, 1:]) & (full[:, :-1] > 0) & (full[:, 1:] > 0)
    v = (full[:-1] != full[1:]) & (full[:-1] > 0) & (full[1:] > 0)
    e[:, :-1] |= h
    e[:, 1:] |= h
    e[:-1] |= v
    e[1:] |= v
    line[band] = (e & ocean)[band]


def pair_regions(full, reg, nb):
    """Put the two provinces facing each other across the wrap in one sea region: of the
    choices that keep every region connected, the one with the most even region sizes."""
    links = defaultdict(set)
    for a, b in zip(full[:, 0].tolist(), full[:, W - 1].tolist()):
        if a and b:
            links[a].add(b)
            links[b].add(a)
    groups = [g for g in components(list(links), links) if len({reg[a] for a in g}) > 1]
    if not groups:
        return reg, 0
    options = [sorted({reg[a] for a in g}) for g in groups]
    best = None
    combos = product(*options) if np.prod([len(o) for o in options]) <= 1 << 16 else [tuple(o[0] for o in options)]
    for combo in combos:
        trial = reg.copy()
        for g, r in zip(groups, combo):
            for a in g:
                trial[a] = r
        touched = {reg[a] for g in groups for a in g}
        c = Counter(trial[1:].tolist())
        if any(c[r] == 0 for r in touched):
            continue
        if any(len(components([a for a in range(1, len(trial)) if trial[a] == r], nb)) > 1 for r in touched):
            continue
        score = sum((c[r] - TARGET) ** 2 for r in touched)
        if best is None or score < best[0]:
            best = (score, trial)
    if best is None:
        sys.exit("seam: no way to pair the regions across the wrap keeps them all connected")
    moved = int((best[1] != reg).sum())
    return best[1], moved


# ------------------------------------------------------------------ commands

def run(seamless):
    names, L = load()
    if LINES not in L:
        sys.exit(f'the map has no "{LINES}" layer')
    ocean = code(L["Terrain"][..., :3]) == code(np.array(OCEAN))
    P = code(L["Provinces"][..., :3])
    R = code(L["Strategic Regions"][..., :3])
    line = L[LINES][..., 3] > 0
    full, n = areas(ocean, line, P)
    connect(full)
    if seamless:
        used = seam(full, ocean)
        redraw_lines(full, ocean, line, used)
    cuts = cut_big(full, ocean, line)
    connect(full)
    col, new = colours(full, P, ocean)
    nb = neighbours(full)
    reg = regions(full, R, nb)
    moved = 0
    if seamless:
        reg, moved = pair_regions(full, reg, nb)
    m = full > 0
    before = int((P[m] != col[full][m]).sum())
    for layer, codes in (("Provinces", col[full]), ("Strategic Regions", reg[full])):
        L[layer][m, 0] = codes[m] >> 16
        L[layer][m, 1] = (codes[m] >> 8) & 255
        L[layer][m, 2] = codes[m] & 255
        L[layer][m, 3] = 255
    L[LINES][...] = 0
    L[LINES][line] = (255, 0, 0, 255)
    print(f"{len(set(col[1:].tolist()) - {0})} sea provinces ({new} new, {cuts} areas cut to the size "
          f"limit); {before} sea pixels changed province; {moved} provinces changed sea region "
          f"to meet across the wrap; {len(set(reg[1:].tolist()) - {0})} sea regions")
    save(names, L)


def name_regions():
    names, L = load()
    ocean = code(L["Terrain"][..., :3]) == code(np.array(OCEAN))
    R = code(L["Strategic Regions"][..., :3])
    old = json.loads(NAMES.read_text(encoding="utf-8"))
    ys, xs = np.nonzero(ocean)
    r = R[ys, xs]
    sea = {}
    for c in np.unique(r).tolist():
        nm = old.get("%06x" % c)
        if nm is None:
            sys.exit(f"sea region {c:06x} has no name in {NAMES}")
        sel = r == c
        ang = xs[sel] / W * 2 * np.pi
        x = (np.arctan2(np.sin(ang).mean(), np.cos(ang).mean()) % (2 * np.pi)) / (2 * np.pi) * W
        sea[c] = (re.sub(r" \d+$", "", nm), x)
    out = {}
    for oc in sorted({o for o, _ in sea.values()}):
        rs = sorted((x, c) for c, (o, x) in sea.items() if o == oc)
        for k, (x, c) in enumerate(rs, 1):
            out["%06x" % c] = oc if len(rs) == 1 else f"{oc} {k}"
    changed = sum(old.get(k) != v for k, v in out.items())
    NAMES.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(out)} sea regions named, {changed} names changed: "
          + ", ".join(f"{o} {sum(1 for v in out.values() if v.startswith(o))}" for o in sorted({o for o, _ in sea.values()})))


def check():
    names, L = load()
    if LINES not in L:
        sys.exit(f'the map has no "{LINES}" layer')
    ocean = code(L["Terrain"][..., :3]) == code(np.array(OCEAN))
    P = code(L["Provinces"][..., :3])
    R = code(L["Strategic Regions"][..., :3])
    full, n = areas(ocean, L[LINES][..., 3] > 0, P)
    connect(full)
    col, new = colours(full, P, ocean)
    m = full > 0
    print(f"{n} areas between the lines; {int((P[m] != col[full][m]).sum())} sea pixels would change "
          f"province ({new} new provinces)")
    big = [sl for sl in ndi.find_objects(full) if sl is not None and
           (sl[0].stop - sl[0].start > OVER_H or sl[1].stop - sl[1].start > OVER_W)]
    print(f"{len(big)} areas over the size limit")
    lb = [b[0] for b in breaks(edge_runs(full, 0))]
    rb = [b[0] for b in breaks(edge_runs(full, W - 1))]
    print("borders at the left edge: ", lb)
    print("borders at the right edge:", rb)
    print("seamless" if lb == rb else "the borders don't all meet across the wrap")
    Rl, Rr = R[:, 0], R[:, W - 1]
    both = ocean[:, 0] & ocean[:, W - 1]
    print(f"rows where the sea region is the same on both edges: {100 * (Rl == Rr)[both].mean():.1f} %")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd in ("build", "seam"):
        run(cmd == "seam")
    elif cmd == "names":
        name_regions()
    elif cmd == "check":
        check()
    else:
        sys.exit(__doc__)
