"""Rivers onto province borders in one nation's land (run by hand, after a build).

The author, 2026-10-20 (of Rouental's fief states, which fief_states.py cut without the rivers): "Rivers need to go
along the borders of states and provinces. Provinces should be recut, or in cases like Lugunica and Karsten where
there is no room for a recut, move the river to follow the border instead." HOI4's river penalty applies only to a
river between the provinces of an attack.

Every stretch of the built river (work/world.npz) that runs inside one of the nation's provinces (its pixels touch no
other province) is one of:
  * cut: the stretch divides its province into parts big enough to be provinces (SPLIT_MIN px each, THICK px
    across somewhere), as a river through the middle of a state (Verdoyantres): the state's banks are cut into
    provinces again (river_provinces.py's way, at the state's own province size), the river between them;
  * move: what it cuts off is a sliver along the province's edge, or too small for a province (Lugunica, Karsten):
    the river is drawn again along the province's border (on its own pixels next to another province, or that
    province's next to it), the shortest way from the river before the stretch to the river after it (a few river
    pixels either side may go too), on the author's layer the stretch was drawn on ("Necessary Major Rivers" /
    "Necessary Minor Rivers");
  * give: a river the Gazetteer's facts draw (they win over the .pdn, so the river can't be moved here), or one with
    no clean way round (along a coast, two rivers meeting): the sliver it cuts off (up to GIVE_MAX px) joins the
    province on its other side, of the same nation, its state and region with it (the author's state lines follow);
  * left, and listed: a river's end inside a province (its source, or a tributary's end), two rivers meeting inside
    a province ("junction"), a move with no clean way round ("unroutable").
A single river pixel off a border at a bend is not a stretch: rivers.trace puts a corner on a province border when
one of its two choices is (2026-10-20).

    python3 scripts/river_borders.py TAG            # the plan: every stretch and what would be done with it
    python3 scripts/river_borders.py TAG --apply    # moves the rivers, gives the slivers, cuts the provinces
Then rebuild and run it again (a moved river is traced anew; what it still leaves off a border shows in the next
plan) until nothing is left to do. Then `--rekey`, after the last rebuild: the nation's Gazetteer province facts
(source/gazetteer/TAG.json) and its re-keying file (source/gazetteer/rekey/TAG.npz) follow the provinces as built. A
nation without a re-keying file (any but Rouental) needs `--from=MAP.pdn` the first time: the map whose provinces its
page names (the one the site was last published from).
"""
import heapq
import json
import sys
from collections import Counter, deque
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi
from skimage.measure import label

import gazetteer
import pdn_tools as T
from apply_outlines import Colours, organic_split
from common import COUNTRIES, MAP_H, MAP_W
from fief_states import boundary

CROSS = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool)
SQUARE = np.ones((3, 3), bool)
N4 = ((0, 1), (1, 0), (0, -1), (-1, 0))
SPLIT_MIN = 40      # each part of a cut province at least this many px
GAZ_SPLIT_MIN = 30  # for a Gazetteer river, which can't be moved here: the fief states' smallest province
THICK = 2.0         # and this far from its edge somewhere (a sliver along a border is thinner)
DETOUR = 3.0        # a moved river at most this many times as long as the stretch, + 8 px
REACH = 3           # river pixels either side of a stretch that may go with it when it moves
GIVE_MAX = 20       # a river that can't be moved (no way round, or two rivers meeting) gives away slivers this small
LINE_LAYERS = ("Necessary Major Rivers", "Necessary Minor Rivers")
PAD = 40


def border_of(P):
    """pixels with a 4-neighbour in another province"""
    b = np.zeros(P.shape, bool)
    b[:, 1:] |= P[:, 1:] != P[:, :-1]
    b[:, :-1] |= P[:, 1:] != P[:, :-1]
    b[1:] |= P[1:] != P[:-1]
    b[:-1] |= P[1:] != P[:-1]
    return b


def gazetteer_rivers(shape):
    """the pixels the Gazetteer's facts draw as rivers (gazetteer.rivers draws them before the trace)"""
    gaz = np.zeros(shape, bool)
    for f in gazetteer.load().values():
        for r in f.get("rivers", []):
            if r["kind"] == "erase":
                continue
            pts = gazetteer._unwrap(r["pts"])
            for a, b in zip(pts, pts[1:]):
                for x, y in gazetteer._line(a[0], a[1], b[0], b[1]):
                    if 0 <= y < shape[0]:
                        gaz[y, x % shape[1]] = True
    return gaz


class Map:
    def __init__(self, tag):
        self.names, self.L = T.load()
        L = self.L
        self.river = np.load("work/world.npz")["rivers"] < 254
        ter = T.code(L["Terrain"][..., :3])
        self.land = (ter != T.code(np.array(T.OCEAN))) & (ter != T.code(np.array(T.LAKES)))
        if (self.river & ~self.land).any():
            raise SystemExit("work/world.npz does not match the .pdn: run scripts/run_all.sh first")
        self.P = T.code(L["Provinces"][..., :3])
        self.St = np.where(L["States"][..., 3] > 0, T.code(L["States"][..., :3]), -1)
        self.C = T.code(L["Countries"][..., :3])
        col = [v[3] for v in COUNTRIES.values() if v[0] == tag]
        if not col:
            raise SystemExit(f"{tag}: not a country")
        c = col[0]
        self.mine = (self.C == (c[0] << 16 | c[1] << 8 | c[2])) & (L["Countries"][..., 3] > 0) & self.land
        self.gaz = gazetteer_rivers(self.P.shape)
        self.drawn = {nm: L[nm][..., 3] > 0 for nm in LINE_LAYERS}
        sn = json.load(open("source/state_names.json", encoding="utf-8"))
        self.name_of = {}
        for k, nm in sn.items():
            x, y = map(int, k.split(","))
            self.name_of.setdefault(int(self.St[y, x]), nm)
        # pixels that name a place (state names, the Gazetteer's keys, cities): a give never moves them
        self.keys = {tuple(map(int, k.split(","))) for k in sn}
        for f in gazetteer.load().values():
            for part in ("states", "provinces"):
                self.keys |= {gazetteer.xy(k) for k in (f.get(part) or {})}
            self.keys |= {(c["x"], c["y"]) for c in f.get("cities", []) if "x" in c}
        cities = L.get("Necessary Cities")
        if cities is not None:
            self.keys |= {(int(x), int(y)) for y, x in np.argwhere(cities[..., 3] > 0)}


def stretches(m):
    """the river's stretches inside one of the nation's provinces: (ys, xs, province). The river's pixels off a
    border, together when they touch corner to corner (a river along a diagonal border one pixel inside it is off
    the border every other pixel, the corners between on it), with the river pixels between them"""
    off = m.river & ~border_of(m.P) & m.mine
    lab, n = ndi.label(off, SQUARE)
    # a river pixel next to two pixels of a group (the corner between them) joins the group
    between = np.zeros(off.shape, np.int32)
    nb = [np.roll(lab, s, a) for s, a in ((1, 0), (-1, 0), (1, 1), (-1, 1))]
    for i in range(4):
        for j in range(i + 1, 4):
            same = (nb[i] > 0) & (nb[i] == nb[j])
            between = np.where(same & (between == 0), nb[i], between)
    lab = np.where(off, lab, np.where(m.river & ~off & (between > 0), between, 0))
    out = []
    for i, sl in enumerate(ndi.find_objects(lab), 1):
        ys, xs = np.nonzero(lab[sl] == i)
        ys, xs = ys + sl[0].start, xs + sl[1].start
        out.append((ys, xs, int(m.P[ys[0], xs[0]])))
    return out


def window(ys, xs, pad, shape):
    return np.s_[max(ys.min() - pad, 0):min(ys.max() + pad + 1, shape[0]),
                 max(xs.min() - pad, 0):min(xs.max() + pad + 1, shape[1])]


def classify(m, ys, xs, p):
    """(kind, details) for one stretch"""
    sl = window(ys, xs, PAD, m.P.shape)
    st = np.zeros(m.P[sl].shape, bool)
    st[ys - sl[0].start, xs - sl[1].start] = True
    rv = m.river[sl]
    pm = (m.P[sl] == p) & m.land[sl]
    anchors = ndi.binary_dilation(st, CROSS) & rv & ~st
    comps = label(pm & ~rv, connectivity=1)
    touch = [int(c) for c in np.unique(comps[ndi.binary_dilation(st, CROSS) & (comps > 0)])]
    sizes = {c: int((comps == c).sum()) for c in touch}
    thick = {c: float(ndi.distance_transform_edt(np.pad(comps == c, 1)).max()) for c in touch}
    na = int(label(anchors, connectivity=2).max())
    from_gaz = bool((ndi.binary_dilation(st, SQUARE, 2) & m.gaz[sl]).any())
    if len(ys) == 1:
        info = dict(sl=sl, st=st, anchors=anchors, n_anchors=na, gaz=from_gaz, sizes={}, thick={}, small=[])
        return ("corner-move" if na == 2 and not from_gaz else "corner"), info
    info = dict(sl=sl, st=st, comps=comps, sizes=sizes, thick=thick, anchors=anchors, n_anchors=na, gaz=from_gaz)
    if len(touch) < 2:
        info["small"] = []
        # a river's end inside the province; or, between two river pixels on a border, a river one pixel inside a
        # diagonal border, its corners on it: drawn again on the border
        return ("end" if na < 2 else "along a Gazetteer river" if from_gaz else "move"), info
    order = sorted(touch, key=lambda c: -sizes[c])
    least = GAZ_SPLIT_MIN if from_gaz else SPLIT_MIN
    if sizes[order[0]] >= least and any(sizes[c] >= least and thick[c] >= THICK for c in order[1:]):
        return "cut", info
    info["small"] = order[1:]
    if from_gaz:
        return "give", info
    if na != 2:
        return "junction", info
    return "move", info


def extension(rv, start, avoid, k):
    """river pixels from start along the river away from `avoid`, up to k steps, stopping at a junction: {px: steps}"""
    h, w = rv.shape
    out = {start: 0}
    dq = deque([start])
    while dq:
        u = dq.popleft()
        if out[u] >= k:
            continue
        nb = [(u[0] + dy, u[1] + dx) for dy, dx in N4]
        nb = [v for v in nb if 0 <= v[0] < h and 0 <= v[1] < w and rv[v] and not avoid[v]]
        if len(nb) > 2:
            continue
        for v in nb:
            if v not in out:
                out[v] = out[u] + 1
                dq.append(v)
    return out


def dropped_by(e, end):
    """the river pixels between `end` and the stretch, along the river (they go when the river leaves at `end`)"""
    out, q = [], end
    while e[q] > 0:
        q = next(v for v in ((q[0] + dy, q[1] + dx) for dy, dx in N4) if e.get(v) == e[q] - 1)
        out.append(q)
    return out


def route(m, info, p):
    """a new course for a moved stretch, or None: (new pixels, river pixels dropped), window coordinates.
    The course leaves the river at s (the pixel before the stretch, or up to REACH further back) and joins it again
    at g, touching it nowhere else; its pixels are on a province border: the province's own next to another
    province, or another province's next to it; never next to water, never two pixels thick."""
    sl, st, anchors = info["sl"], info["st"], info["anchors"]
    P, lnd = m.P[sl], m.land[sl]
    rv = m.river[sl] & ~st
    pm = (P == p) & lnd
    al, na = ndi.label(anchors, SQUARE)
    a1, a2 = (tuple(np.argwhere(al == k)[0]) for k in (1, 2))
    e1, e2 = extension(rv, a1, st, REACH), extension(rv, a2, st, REACH)
    if set(e1) & set(e2):
        info["why"] = "the river round it is a loop"
        return None
    ring = (pm & border_of(P)) | (ndi.binary_dilation(pm, CROSS) & ~pm & lnd)
    base = ring & lnd & ~ndi.binary_dilation(~lnd, CROSS) & ~rv     # the stretch's own pixels on a border may stay
    h, w = base.shape
    limit = DETOUR * st.sum() + 8
    best, why = None, "no way round along borders"
    for s, ds in e1.items():
        for g, dg in e2.items():
            drop = set(dropped_by(e1, s)) | set(dropped_by(e2, g))
            kept = rv.copy()
            for q in drop:
                kept[q] = False
            near = ndi.binary_dilation(kept, CROSS) & ~kept
            def nb(q):
                return [(q[0] + dy, q[1] + dx) for dy, dx in N4 if 0 <= q[0] + dy < h and 0 <= q[1] + dx < w]
            # a path pixel may touch the river only at s (the first) and g (the last)
            starts = [q for q in nb(s) if base[q] and [v for v in nb(q) if kept[v]] in ([s], [s, g], [g, s])]
            ends = {q for q in nb(g) if base[q] and set(v for v in nb(q) if kept[v]) <= {s, g}}
            inner = base & ~near
            prev, dq, found = {q: None for q in starts}, deque(starts), None
            while dq:
                u = dq.popleft()
                if u in ends and (u in starts or prev[u] is not None) and \
                        set(v for v in nb(u) if kept[v]) == ({g} if u not in starts or prev[u] else {s, g}):
                    found = u
                    break
                for v in nb(u):
                    if v not in prev and (inner[v] or v in ends):
                        prev[v] = u
                        dq.append(v)
            if found is None:
                continue
            path = [found]
            while prev[path[-1]] is not None:
                path.append(prev[path[-1]])
            path = path[::-1]
            if len(path) > limit:
                why = f"the way round is {len(path)} px"
                continue
            new = np.zeros(st.shape, bool)
            for q in path:
                new[q] = True
            after = kept | new
            if (after[:-1, :-1] & after[1:, :-1] & after[:-1, 1:] & after[1:, 1:]).any():
                why = "it would be two pixels thick"
                continue
            cost = len(path) + 0.5 * len(drop)
            if best is None or cost < best[0]:
                dmask = np.zeros(st.shape, bool)
                for q in drop:
                    dmask[q] = True
                best = (cost, new, dmask)
    if best is None:
        info["why"] = why
        return None
    return best[1], best[2]


def plan(m):
    rows = []
    for ys, xs, p in stretches(m):
        kind, info = classify(m, ys, xs, p)
        if kind == "corner-move":                 # a single pixel at a bend: moved only for a short way round
            r = route(m, info, p)
            if r is not None and r[0].sum() <= 3:
                kind = "move"
                info["new"], info["dropped"] = r
            else:
                kind = "corner"
        elif kind == "move":
            r = route(m, info, p)
            if r is None:
                kind = "unroutable"
            else:
                info["new"], info["dropped"] = r
        if kind in ("unroutable", "junction") and all(info["sizes"][c] <= GIVE_MAX for c in info.get("small", [])):
            kind = "give"                         # the border onto the river instead
        state = int(m.St[ys[0], xs[0]])
        rows.append(dict(kind=kind, ys=ys, xs=xs, p=p, state=state, name=m.name_of.get(state, "?"), info=info))
    return rows


def report(m, rows):
    r, on = m.river & m.mine, m.river & m.mine & border_of(m.P)
    print(f"river pixels in the nation's land: {r.sum()}, {on.sum()} on a province border "
          f"({100 * on.sum() / max(r.sum(), 1):.0f} %)")
    cnt = Counter(x["kind"] for x in rows)
    print("stretches:", dict(cnt), " their pixels:", {k: sum(len(x["ys"]) for x in rows if x["kind"] == k) for k in cnt})
    for x in sorted(rows, key=lambda x: (x["kind"], x["name"], x["xs"][0])):
        if x["kind"] == "corner":
            continue
        sz, th = x["info"].get("sizes", {}), x["info"].get("thick", {})
        parts = ", ".join(f"{sz[c]} px/{th[c]:.1f}" for c in sorted(sz, key=lambda c: -sz[c]))
        extra = ""
        if x["kind"] == "move":
            extra = f"  new course {int(x['info']['new'].sum())} px, {int(x['info']['dropped'].sum())} more dropped"
        if x["kind"] == "unroutable":
            extra = f"  ({x['info'].get('why', '?')})"
        print(f"  {x['kind']:10s} {x['name']:22s} {len(x['ys']):3d} px at ({x['xs'][0]},{x['ys'][0]})  parts {parts}"
              f"{extra}{'  (a Gazetteer river)' if x['info'].get('gaz') else ''}")


# ------------------------------------------------------------------------------------------------- applying

def apply_move(m, x):
    """the stretch's river drawn again on its new course, on the author's line layer"""
    info = x["info"]
    sl, st, new, dropped = info["sl"], info["st"], info["new"], info["dropped"]
    removed = st | dropped
    near = ndi.binary_dilation(removed, SQUARE)
    kept = m.river[sl] & ~removed
    counts = {nm: int((m.drawn[nm][sl] & near).sum()) for nm in LINE_LAYERS}
    layer = max(LINE_LAYERS, key=lambda nm: counts[nm])
    before = {nm: m.drawn[nm][sl].copy() for nm in LINE_LAYERS}
    saved = {nm: m.L[nm][sl].copy() for nm in LINE_LAYERS}
    for nm in LINE_LAYERS:
        a = m.L[nm][sl]
        a[near & ~kept & before[nm], 3] = 0
    # the new course, and the kept river round it, so the line runs on unbroken
    draw = new | (kept & ndi.binary_dilation(removed | new, SQUARE, 3))
    a = m.L[layer][sl]
    ys, xs = np.nonzero(m.drawn[layer])
    colour = m.L[layer][ys[0], xs[0], :3] if len(ys) else np.array([0, 0, 255], np.uint8)
    a[draw, :3] = colour
    a[draw, 3] = 255
    for nm in LINE_LAYERS:
        m.drawn[nm][sl] = m.L[nm][sl][..., 3] > 0
    # one drawing still: the lines round the window join up as before
    allb = before[LINE_LAYERS[0]] | before[LINE_LAYERS[1]]
    alla = m.drawn[LINE_LAYERS[0]][sl] | m.drawn[LINE_LAYERS[1]][sl]
    nb, na = ndi.label(allb, SQUARE)[1], ndi.label(alla, SQUARE)[1]
    if na > nb:                                   # it would break the line in two: left for the next run
        for nm in LINE_LAYERS:
            m.L[nm][sl] = saved[nm]
            m.drawn[nm][sl] = saved[nm][..., 3] > 0
        print(f"  not moved: {x['name']} at ({x['xs'][0]},{x['ys'][0]}) (it would break the line in two)")
        return False
    return True


def apply_give(m, x, cols):
    """the slivers a Gazetteer river cuts off join the province across them (same nation)"""
    info = x["info"]
    sl, comps = info["sl"], info["comps"]
    P, St = m.P[sl], m.St[sl]
    mine = m.mine[sl]
    moved = 0
    keep = np.zeros(P.shape, bool)                # pixels that name a place: never moved
    for k in m.keys:
        x0, y0 = k
        if sl[0].start <= y0 < sl[0].stop and sl[1].start <= x0 < sl[1].stop:
            keep[y0 - sl[0].start, x0 - sl[1].start] = True
    for c in info["small"]:
        part = comps == c
        if (part & keep).any():
            continue
        ring = ndi.binary_dilation(part, CROSS) & ~part & mine & ~m.river[sl] & (P != x["p"])
        if not ring.any():
            continue
        v, n = np.unique(P[ring], return_counts=True)
        q = int(v[n.argmax()])
        src = np.argwhere((P == q) & ring)[0]
        for nm in ("Provinces", "States", "Strategic Regions", "Countries"):
            lay = m.L[nm][sl]
            lay[part] = lay[src[0], src[1]]
        P[part] = q
        St[part] = St[src[0], src[1]]
        moved += int(part.sum())
    return moved


def state_lines(m):
    """the author's state lines (Necessary States) drawn again over the nation's land from its states, as
    fief_states.py draws them, once a give moved a state border"""
    ys, xs = np.nonzero(m.mine)
    sl = np.s_[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    ns, mine = m.L["Necessary States"][sl], m.mine[sl]
    ns[mine, 3] = 0
    ns[boundary(m.St[sl], mine)] = (0, 0, 0, 255)


def recut_state(m, sc, cols):
    """a state's banks cut into provinces again, at the state's own province size; returns (old, new) counts"""
    ys, xs = np.nonzero((m.St == sc) & m.land)
    sl = np.s_[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    y0, x0 = ys.min(), xs.min()
    msk = np.zeros((ys.max() - y0 + 1, xs.max() - x0 + 1), bool)
    msk[ys - y0, xs - x0] = True
    P = m.P[sl]
    rv = m.river[sl] & msk
    old = len(np.unique(P[msk]))
    target = min(max(msk.sum() / old, 80), 190)
    out = np.zeros(msk.shape, np.int64)
    banks = label(msk & ~rv, connectivity=1)
    new = 0
    for b in range(1, banks.max() + 1):
        by, bx = np.nonzero(banks == b)
        if len(by) < GAZ_SPLIT_MIN:
            continue                                # a scrap: joins the province beside it, below
        k = max(1, round(len(by) / target))
        parts = organic_split(by + y0, bx + x0, k, seed=int(sc) % 100000 + b)
        for q in range(k):
            if (parts == q).any():
                out[by[parts == q], bx[parts == q]] = cols.new()
                new += 1
    if not out.any():
        return old, old
    miss = msk & (out == 0)
    idx = ndi.distance_transform_edt(out == 0, return_distances=False, return_indices=True)
    out[miss] = out[idx[0][miss], idx[1][miss]]
    # each province one piece (the nearest province may be across a diagonal)
    for c in np.unique(out[msk]):
        comp = label(out == c, connectivity=1)
        if comp.max() > 1:
            keep = np.bincount(comp.ravel())[1:].argmax() + 1
            for j in range(1, comp.max() + 1):
                if j != keep:
                    pm = comp == j
                    ring = ndi.binary_dilation(pm, CROSS) & ~pm & msk & (out != c)
                    if ring.any():
                        v, cnt = np.unique(out[ring], return_counts=True)
                        out[pm] = v[cnt.argmax()]
    P[msk] = out[msk]
    T.put(m.L["Provinces"][sl], out, msk)
    return old, len(np.unique(out[msk]))


def repair(m):
    """every province of the nation one 4-connected piece: a stray piece (left when a sliver went) joins the
    province it shares most border with, with its state and region"""
    ys, xs = np.nonzero(m.mine)
    sl = np.s_[max(ys.min() - 2, 0):ys.max() + 3, max(xs.min() - 2, 0):xs.max() + 3]
    P, mine, lnd = m.P[sl], m.mine[sl], m.land[sl]
    fixed = 0
    for c in np.unique(P[mine]):
        cm = (P == c) & lnd
        comp, n = ndi.label(cm, CROSS)
        if n < 2:
            continue
        sizes = np.bincount(comp.ravel())[1:]
        for j in np.argsort(-sizes)[1:] + 1:
            pm = comp == j
            ring = ndi.binary_dilation(pm, CROSS) & ~pm & lnd & (P != c)
            if not ring.any():
                continue
            v, cnt = np.unique(P[ring], return_counts=True)
            q = int(v[cnt.argmax()])
            src = np.argwhere((P == q) & ring)[0]
            for nm in ("Provinces", "States", "Strategic Regions", "Countries"):
                lay = m.L[nm][sl]
                lay[pm] = lay[src[0], src[1]]
            P[pm] = q
            m.St[sl][pm] = m.St[sl][src[0], src[1]]
            fixed += 1
    return fixed


def apply(m, rows):
    cols = Colours(m.P, 7)
    cut_states = {x["state"] for x in rows if x["kind"] == "cut"}
    done = Counter()
    busy = np.zeros(m.P.shape, bool)              # where this run moved a river: a stretch beside it waits
    for x in rows:
        if x["state"] in cut_states:
            continue
        if x["kind"] == "move":
            sl = x["info"]["sl"]
            here = ndi.binary_dilation(x["info"]["st"] | x["info"]["new"] | x["info"]["dropped"], SQUARE, 4)
            if (busy[sl] & here).any():
                done["waits for the next run"] += 1
                continue
            if apply_move(m, x):
                busy[sl] |= here
                done["moved"] += 1
        elif x["kind"] == "give":
            if apply_give(m, x, cols):
                done["given"] += 1
    for sc in sorted(cut_states):
        old, new = recut_state(m, sc, cols)
        done["cut"] += 1
        print(f"  cut {m.name_of.get(sc, sc)}: {old} provinces -> {new}")
    done["stray pieces joined a neighbour"] = repair(m)
    if done["given"] or done["stray pieces joined a neighbour"]:
        state_lines(m)
    print("applied:", dict(done))
    T.save(m.names, m.L)


# ------------------------------------------------------------------------------------------------- Gazetteer keys

def first_layout(tag, pdn):
    """a re-keying file's start for a nation that has none (2026-10-29: Arovannea, whose page names its provinces as
    the map of 10-23-3 had them): the old layout from that map (pdn: its Provinces and States layers, the nation's
    land on its Countries layer), the new one from the last build"""
    import subprocess
    from regions import anchors
    tmp = Path("work/rekey_from")
    subprocess.run([sys.executable, str(Path(__file__).parent / "readpdn.py"), str(pdn), str(tmp)], check=True,
                   stdout=subprocess.DEVNULL)
    names = (tmp / "layers.txt").read_text().splitlines()
    lay = lambda nm: np.load(tmp / f"layer{names.index(nm)}.npy")
    pr = np.load("work/provinces.npz")["prov"]
    reg = np.load("work/regions.npz")
    rj = json.load(open("work/regions.json"))
    owners, states, anchor, size = rj["owners"], rj["states"], reg["anchor"], reg["size"]
    st = reg["state_of"]
    mine_new = np.isin(st[pr], [s for s, o in enumerate(owners) if o == tag])
    colour = next(v[3] for v in COUNTRIES.values() if v[0] == tag)
    K = T.code(lay("Countries")[..., :3])
    mine_old = (lay("Countries")[..., 3] > 0) & (K == ((colour[0] << 16) | (colour[1] << 8) | colour[2]))
    ys, xs = np.nonzero(mine_new | mine_old)
    X0, Y0 = max(xs.min() - PAD, 0), max(ys.min() - PAD, 0)
    X1, Y1 = min(xs.max() + 1 + PAD, MAP_W), min(ys.max() + 1 + PAD, MAP_H)
    sl = np.s_[Y0:Y1, X0:X1]

    def relabel(codes, mask):
        u, inv = np.unique(np.where(mask, codes, -1), return_inverse=True)
        out = inv.reshape(codes.shape).astype(np.int32)
        return out if u[0] == -1 else out + 1  # 0 outside the nation's land

    Pold = T.code(lay("Provinces")[..., :3])
    old_p_full = relabel(Pold, mine_old)
    old_p = old_p_full[sl]
    old_s = relabel(T.code(lay("States")[..., :3])[sl], mine_old[sl])
    u_old, lab_old = np.unique(Pold, return_inverse=True)
    lab_old = lab_old.reshape(Pold.shape)
    a_old = anchors(lab_old, len(u_old))[0]       # the keys the page gave the old provinces
    lab_old = lab_old.ravel()
    pids, first = np.unique(old_p_full, return_index=True)
    okeys = np.array([gazetteer.anchor_key(a_old, int(lab_old[i])) for p, i in zip(pids, first) if p > 0])
    new_s = np.where(mine_new[sl], st[pr][sl] + 1, 0).astype(np.int32)
    sids = np.unique(new_s[new_s > 0])
    skeys = np.array([gazetteer.anchor_key(anchor, max(states[s - 1], key=lambda i: (size[i], -i))) for s in sids])
    print(f"{tag}: the old layout from {pdn}: {len(okeys)} provinces, {int(old_s.max())} states; "
          f"the new {len(np.unique(pr[sl][mine_new[sl]]))} provinces, {len(sids)} states")
    return dict(box=np.array([X0, Y0, X1, Y1]), old_states=old_s, old_provinces=old_p, states=new_s,
                provinces=old_p, state_ids=sids.astype(np.int32), state_keys=skeys,
                province_ids=pids[pids > 0].astype(np.int32), province_keys=okeys)


def rekey(tag, start=None):
    """the nation's Gazetteer province facts and its re-keying file onto the provinces as built (work/provinces.npz);
    a nation without a re-keying file starts one from `start`, the map whose provinces its page's facts name"""
    from regions import anchors
    f = gazetteer.DIR / "rekey" / f"{tag}.npz"
    if f.exists():
        z = dict(np.load(f))
    elif start:
        z = first_layout(tag, start)
        f.parent.mkdir(parents=True, exist_ok=True)
    else:
        raise SystemExit(f"{f} missing: --rekey --from=MAP.pdn, the map whose provinces {tag}'s page names")
    X0, Y0, X1, Y1 = (int(v) for v in z["box"])
    pr = np.load("work/provinces.npz")["prov"]
    n = int(pr.max()) + 1
    anchor = anchors(pr, n)[0]
    box = pr[Y0:Y1, X0:X1]
    inside = z["provinces"] > 0                    # the nation's land as the file has it
    ids, cnt = np.unique(box[inside], return_counts=True)
    ids = ids[2 * cnt > np.bincount(box.ravel(), minlength=n)[ids]]  # a neighbour's province a pixel over: not ours
    newp = np.where(inside, box + 1, 0).astype(np.int32)
    keys = np.array([gazetteer.anchor_key(anchor, int(i)) for i in ids])
    # the facts: each built province takes those of the old province most of it lies on
    path = gazetteer.DIR / f"{tag}.json"
    facts = json.load(open(path, encoding="utf-8"))
    oldp = z["provinces"]
    old_key = dict(zip(z["province_ids"].tolist(), z["province_keys"].tolist()))
    by_old = {}
    for k, v in (facts.get("provinces") or {}).items():
        x, y = gazetteer.xy(k)
        if X0 <= x < X1 and Y0 <= y < Y1 and oldp[y - Y0, x - X0] > 0:
            by_old.setdefault(int(oldp[y - Y0, x - X0]), {}).update(v)
    out = {k: v for k, v in (facts.get("provinces") or {}).items()
           if not (X0 <= gazetteer.xy(k)[0] < X1 and Y0 <= gazetteer.xy(k)[1] < Y1 and oldp[gazetteer.xy(k)[1] - Y0,
                                                                                         gazetteer.xy(k)[0] - X0] > 0)}
    for i, k in zip(ids.tolist(), keys.tolist()):
        c = Counter(oldp[(box == i) & inside].tolist()).most_common(1)[0][0]
        share = {kk: vv for kk, vv in by_old.get(c, {}).items() if kk != "hub"}
        if share:
            out[k] = share
    # and what the page will show once published from this build wins (each old key on the province round it now),
    # as the next import would have it (gazetteer.rekey): a supply hub stays one, not one on every piece of its province
    out = gazetteer.page_wins(facts.get("provinces") or {}, out, *gazetteer.page_places()["provinces"])
    print(f"{tag}: {len(facts.get('provinces') or {})} province facts -> {len(out)} "
          f"({len(old_key)} provinces in the re-keying file -> {len(ids)})")
    facts["provinces"] = out
    if facts.get("borders"):
        facts["borders"] = gazetteer.rekey_borders(facts["borders"], oldp, X0, Y0, f"{tag}'s ")
    path.write_text(json.dumps(facts, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    z["provinces"], z["province_ids"], z["province_keys"] = newp, (ids + 1).astype(np.int32), keys
    np.savez_compressed(f, **z)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        raise SystemExit(__doc__)
    tag = args[0]
    if "--rekey" in sys.argv:
        rekey(tag, next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--from=")), None))
        return
    m = Map(tag)
    rows = plan(m)
    report(m, rows)
    if "--apply" in sys.argv:
        apply(m, rows)


if __name__ == "__main__":
    main()
