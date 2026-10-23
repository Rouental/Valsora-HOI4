"""Build suggestions made on the Gazetteer into source/HOI4 Mod Map.pdn (2026-10-18, the author: "a number of changes
have been made on the Gazetteer. Please add them to the mod"). A suggestion is drawn roughly on the page (a polygon,
source/gazetteer/<TAG>.json `suggest`), so PLAN says how each one is read:

  split   cut the state at a pixel along the drawing: its land inside is one state, the rest another; `names` name
          them by where they lie (north / south / west / east)
  merge   the nation's states with half their land or more inside the drawing become one state, named `name`;
          `pairs`: islands two by two instead, the nearest together (the author, 2026-10-18: "with the isles that
          Terreich wanted combined, put them into groups of two"); `sparse`: their provinces cut again at SPARSE_PX
          (each island one at least)
  new     the nation's land inside the drawing becomes a state of its own, named `name`
  drawn   the nation's states become the ones it drew, in the order it drew them, as the page shows them (each the
          nation's land inside its line that none drawn before holds; the land left over joins the drawn state it
          shares most border with), named by their labels
  province  the drawing's land becomes a province of its own, in the same state
  island  the drawing's land is cut free of the rest by a channel of sea, in the same state

New state lines cut the provinces they cross (pieces of MIN_PROVINCE px or more become provinces, scraps join a
neighbour in their state); each state lies in the strategic region most of its land was in. State names go to
source/state_names.json (the Gazetteer's own names, where a nation gave one, still win in the build).

    python3 scripts/apply_suggestions.py            # what each would do, nothing saved
    python3 scripts/apply_suggestions.py --apply    # saved; then rebuild
    --only=TAG[,TAG]                                # only those nations' (the rest of PLAN applied already)
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi
from skimage.measure import label as sklabel, points_in_poly

import pdn_tools as T
from apply_outlines import organic_split
from common import COUNTRIES, MIN_PROVINCE, MAP_W as W, MAP_H as H

SPARSE_PX = 600   # "very sparse" (2026-10-18, Terreich's islands): provinces about this big
NAMES = Path("source/state_names.json")
CROSS = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])

# 2026-10-18: the suggestions of the Gazetteer's export of that day, by nation and label (the import keeps no ids)
PLAN = [
    ("ROU", "Split Leclerc in Two", "split", dict(at=(679, 827), names={"north": "Bicêtre", "south": "Callentroix"})),
    ("ROU", "Split Kove in Two", "split", dict(at=(707, 842), names={"west": "Temerre", "east": "Kové"})),
    ("NPL", "It can stay part of the same state, but it's an island.", "island", {}),
    ("NPL", "Split the state into two provinces", "province", {}),
    ("TUP", "Reuenland-Thuringen", "merge", dict(name="Reuenland-Thuringen")),
    ("TUP", "The Triftsund-Inseln", "merge", dict(name="Triftsund-Inseln", sparse=True, pairs=True)),
    ("TUP", "Teuton", "merge", dict(name="Teuton", sparse=True, pairs=True)),
    ("TUP", "Rosenburg", "new", dict(name="Rosenburg")),
    ("TUP", "Terreichstadt", "new", dict(name="Terreichstadt")),
    ("UNG", None, "drawn", {}),
    # 2026-10-19: Ostaria's five states, drawn and named on its page (the ones above were applied on 2026-10-18)
    ("OST", None, "drawn", {}),
    # 2026-10-22: Zwintern's four states, drawn and named on its page (the author: "Some new leaders and borders for
    # Zwintern")
    ("ZWT", None, "drawn", {}),
    # 2026-10-23: Arovannea's 87 states, drawn and named on its page (the author: "Arovannea is okay to change now";
    # held on 2026-10-22: "still a WIP")
    ("AVN", None, "drawn", {}),
]


class Map:
    def __init__(self, L):
        self.L = L
        t = L["Terrain"][..., :3]
        self.sea = (t == T.OCEAN).all(-1)
        self.land = ~self.sea & ~(t == T.LAKES).all(-1)
        self.P = T.code(L["Provinces"][..., :3])
        self.S = np.where(L["States"][..., 3] > 0, T.code(L["States"][..., :3]), -1)
        self.R = T.code(L["Strategic Regions"][..., :3])
        self.K = T.code(L["Countries"][..., :3])
        self.fresh_s = iter(T.palette(400, False, 20261018, set(np.unique(self.S).tolist())))
        self.fresh_p = iter(T.palette(4000, False, 20261019, set(np.unique(self.P).tolist())))
        self.names = {}  # state colour -> name
        self.shapes = {}  # state colour -> the nation's land its drawing holds (drawn states)
        self.touched = np.zeros((H, W), bool)

    def nation(self, tag):
        r, g, b = next(v[3] for v in COUNTRIES.values() if v[0] == tag)
        return self.land & (self.K == ((r << 16) | (g << 8) | b))

    @staticmethod
    def polygon(pts):
        """the pixels whose centres the drawing holds (as the page's canvas fills it)"""
        p = np.array(pts, float)
        x0, y0 = max(int(p[:, 0].min()) - 1, 0), max(int(p[:, 1].min()) - 1, 0)
        x1, y1 = min(int(p[:, 0].max()) + 2, W), min(int(p[:, 1].max()) + 2, H)
        yy, xx = np.mgrid[y0:y1, x0:x1]
        inside = points_in_poly(np.c_[xx.ravel() + 0.5, yy.ravel() + 0.5], p).reshape(yy.shape)
        m = np.zeros((H, W), bool)
        m[y0:y1, x0:x1] = inside
        return m

    def set_state(self, mask, colour, region=None):
        if region is None:
            region = Counter(self.R[mask].tolist()).most_common(1)[0][0]
        self.S[mask] = colour
        self.R[mask] = region
        self.touched |= mask

    def tidy_provinces(self):
        """each province within one state and in one piece: pieces of MIN_PROVINCE px or more are provinces of their
        own, scraps join the neighbouring province of their state they share most border with (scraps next to
        scraps, until none is left)"""
        zone = ndi.binary_dilation(self.touched, iterations=2) & self.land
        scraps = []
        for pc in sorted(set(np.unique(self.P[zone]).tolist())):
            ys, xs = np.nonzero((self.P == pc) & self.land)
            sl = np.s_[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
            m = (self.P[sl] == pc) & self.land[sl]
            pieces = []
            for sc in set(np.unique(self.S[sl][m]).tolist()):
                comp = sklabel(m & (self.S[sl] == sc), connectivity=1)
                for q in range(1, comp.max() + 1):
                    py, px = np.nonzero(comp == q)
                    pieces.append((len(py), sc, py + sl[0].start, px + sl[1].start))
            pieces.sort(key=lambda t: -t[0])
            for n, sc, py, px in pieces[1:]:
                if n >= MIN_PROVINCE:
                    self.P[py, px] = next(self.fresh_p)
                else:
                    self.P[py, px] = -2  # to place
                    scraps.append((sc, py, px))
        # a state whose land is all scraps (a small one drawn across provinces: Arovannea's Citra and Tresean Cliffs,
        # 2026-10-23) keeps it: each piece one province, one under MIN_PROVINCE px grown to it from the states round it
        # (the author, 2026-10-23: "just add the minimum number of pixels necessary to make it work from the surrounding
        # states, while trying to keep the general shape of the state intact")
        whole = defaultdict(list)
        for sc, py, px in scraps:
            whole[sc].append((py, px))
        for sc, parts in whole.items():
            py, px = np.concatenate([p for p, _ in parts]), np.concatenate([q for _, q in parts])
            if len(py) != int(((self.S == sc) & self.land).sum()):
                continue
            m = np.zeros((H, W), bool)
            m[py, px] = True
            comp = sklabel(m, connectivity=1)
            made = np.zeros((H, W), bool)   # its land in provinces so far
            for q in sorted(range(1, comp.max() + 1), key=lambda q: -int((comp == q).sum())):
                piece = comp == q
                n = int(piece.sum())
                if n < MIN_PROVINCE and made.any():   # joined to its own province, if that takes fewer pixels
                    path = self.join(piece, sc, made, MIN_PROVINCE - n)
                    if path is not None:
                        y, x, to = path
                        self.P[piece] = to
                        made |= piece
                        made[y, x] = True
                        continue
                if n < MIN_PROVINCE:
                    piece = self.grow(piece, sc)
                cy, cx = np.nonzero(piece)
                if len(cy) >= MIN_PROVINCE:
                    self.P[cy, cx] = next(self.fresh_p)
                    made |= piece
        scraps = [(sc, py[k], px[k]) for sc, py, px in scraps for k in [self.P[py, px] == -2] if k.any()]
        for _ in range(20):
            left = []
            for sc, py, px in scraps:
                ny, nx = np.r_[py - 1, py + 1, py, py], np.r_[px, px, px - 1, px + 1] % W
                ok = (ny >= 0) & (ny < H)
                ny, nx = ny[ok], nx[ok]
                ok = self.land[ny, nx] & (self.P[ny, nx] >= 0)
                same = ok & (self.S[ny, nx] == sc)
                pick = same if same.any() else ok
                if not pick.any():
                    left.append((sc, py, px))
                    continue
                to = Counter(self.P[ny[pick], nx[pick]].tolist()).most_common(1)[0][0]
                if not same.any():  # a scrap that only touches another state goes with it
                    y1, x1 = ny[pick][0], nx[pick][0]
                    self.S[py, px], self.R[py, px] = self.S[y1, x1], self.R[y1, x1]
                    for nm in ("Countries",):
                        self.L[nm][py, px] = self.L[nm][y1, x1]
                self.P[py, px] = to
            if not left or len(left) == len(scraps):
                for sc, py, px in left:
                    self.P[py, px] = next(self.fresh_p)
                break
            scraps = left

    def grow(self, piece, sc):
        """the piece (a small drawn state's land) grown to MIN_PROVINCE px with as few pixels as it takes, one at a time
        from the land round it in the same country: first the state's own drawing (land a state drawn before it took),
        then the pixels touching it most, then the nearest its middle; never one that would leave its province under
        MIN_PROVINCE px or in two pieces. Returns the grown piece (as it was when nothing can be taken)"""
        piece = piece.copy()
        ys, xs = np.nonzero(piece)
        kc, rc = int(self.K[ys[0], xs[0]]), int(self.R[ys[0], xs[0]])
        shape = self.shapes.get(sc, np.zeros((H, W), bool))
        took = []
        while piece.sum() < MIN_PROVINCE:
            ys, xs = np.nonzero(piece)
            y0, y1, x0, x1 = max(ys.min() - 2, 0), min(ys.max() + 3, H), max(xs.min() - 2, 0), min(xs.max() + 3, W)
            sl = np.s_[y0:y1, x0:x1]
            pc = piece[sl]
            ring = (ndi.binary_dilation(pc, CROSS) & ~pc & self.land[sl] & (self.K[sl] == kc) & (self.P[sl] >= 0)
                    & (self.S[sl] != sc))
            nb = ndi.convolve(pc.astype(int), CROSS, mode="constant") - pc
            cy, cx = ys.mean() - y0, xs.mean() - x0
            cands = sorted(zip(*np.nonzero(ring)), key=lambda p: (not shape[sl][p], -nb[p], (p[0] - cy) ** 2 + (p[1] - cx) ** 2, p))
            for ly, lx in cands:
                y, x = ly + y0, lx + x0
                if not self.spare(y, x):
                    continue
                piece[y, x] = True
                self.P[y, x] = -2
                self.S[y, x], self.R[y, x] = sc, rc
                self.touched[y, x] = True
                took.append((x, y))
                break
            else:
                break
        if took:
            print(f"  {self.names.get(sc, sc)}: grown by {len(took)} px from the states round it, to {int(piece.sum())}")
        return piece

    def spare(self, y, x):
        """whether the pixel's province can give it up: MIN_PROVINCE px left, in one piece"""
        q = self.P[y, x]
        qy, qx = np.nonzero(self.P == q)
        if len(qy) - 1 < MIN_PROVINCE:
            return False
        qs = np.s_[qy.min():qy.max() + 1, qx.min():qx.max() + 1]
        rest = (self.P[qs] == q) & self.land[qs]
        rest[y - qy.min(), x - qx.min()] = False
        return sklabel(rest, connectivity=1).max() == 1

    def join(self, piece, sc, made, budget):
        """the fewest pixels (fewer than budget) of the land round the piece, in its country and not its state's, that
        join it to the state's provinces (made): taken into the state, the piece and they become part of the province
        they reach; (ys, xs, its colour), or None"""
        ys, xs = np.nonzero(piece)
        kc, rc = int(self.K[ys[0], xs[0]]), int(self.R[ys[0], xs[0]])
        r = budget + 1
        y0, y1, x0, x1 = max(ys.min() - r, 0), min(ys.max() + r + 1, H), max(xs.min() - r, 0), min(xs.max() + r + 1, W)
        sl = np.s_[y0:y1, x0:x1]
        goal = made[sl]
        step = self.land[sl] & (self.K[sl] == kc) & (self.P[sl] >= 0) & (self.S[sl] != sc)
        prev = {(int(a), int(b)): None for a, b in zip(ys - y0, xs - x0)}
        front, hit = list(prev), None
        for d in range(budget):
            nxt = []
            for a, b in front:
                for a2, b2 in ((a - 1, b), (a + 1, b), (a, b - 1), (a, b + 1)):
                    if not (0 <= a2 < y1 - y0 and 0 <= b2 < x1 - x0) or (a2, b2) in prev:
                        continue
                    if goal[a2, b2]:
                        hit = (a, b, a2, b2)
                        break
                    if step[a2, b2]:
                        prev[(a2, b2)] = (a, b)
                        nxt.append((a2, b2))
                if hit:
                    break
            if hit or not nxt:
                break
            front = nxt
        if hit is None:  # the piece may touch its province already (corner to corner it doesn't)
            return None
        path, node = [], (hit[0], hit[1])
        while prev[node] is not None:
            path.append(node)
            node = prev[node]
        if len(path) >= budget:
            return None
        for a, b in path:
            if not self.spare(a + y0, b + x0):
                return None
        to = int(self.P[hit[2] + y0, hit[3] + x0])
        py = np.array([a + y0 for a, _ in path], int)
        px = np.array([b + x0 for _, b in path], int)
        self.P[py, px] = to
        self.S[py, px], self.R[py, px] = sc, rc
        self.touched[py, px] = True
        print(f"  {self.names.get(sc, sc)}: a piece of {int(piece.sum())} px joined to its province by {len(path)} px")
        return py, px, to

    def recut(self, colour, size):
        """the state's provinces cut again at about `size` px, each island one at least"""
        m = (self.S == colour) & self.land
        comp = sklabel(m, connectivity=1)
        n = 0
        for q in range(1, comp.max() + 1):
            ys, xs = np.nonzero(comp == q)
            k = max(1, round(len(ys) / size))
            parts = organic_split(ys, xs, k, seed=int(colour) % 9973 + q)
            for j in range(k):
                self.P[ys[parts == j], xs[parts == j]] = next(self.fresh_p)
                n += 1
        self.touched |= m
        return n

    def save(self):
        for nm, arr in (("Provinces", self.P), ("States", self.S), ("Strategic Regions", self.R)):
            T.put(self.L[nm], arr, self.land)
        self.L["States"][self.land, 3] = 255
        self.draw_lines()

    def draw_lines(self):
        """the borders of the states the suggestions made or changed, on Necessary States in its own ink: the
        Gazetteer counts a nation's states as drawn (its map tools open) only where the lines part them
        (gazetteer.finals), and Rouental's and Terreich's closed when the first run left the lines off (2026-10-18)"""
        zone = ndi.binary_dilation(self.touched, iterations=2) & self.land
        S = np.where(self.land, self.S, -1)
        edge = np.zeros(S.shape, bool)
        edge[:, :-1] |= (S[:, :-1] != S[:, 1:]) & (S[:, :-1] >= 0) & (S[:, 1:] >= 0)
        edge[:-1, :] |= (S[:-1, :] != S[1:, :]) & (S[:-1, :] >= 0) & (S[1:, :] >= 0)
        NS = self.L["Necessary States"]
        had = NS[..., 3] > 0
        ink = np.median(NS[had][:, :3], axis=0).astype(np.uint8) if had.any() else np.zeros(3, np.uint8)
        new = edge & zone & ~had
        NS[new, :3] = ink
        NS[new, 3] = 255
        print(f"{int(new.sum())} px of the new state lines drawn on Necessary States")


def biggest(mask):
    comp = sklabel(mask, connectivity=1)
    if not comp.max():
        return mask
    return comp == (np.argmax(np.bincount(comp.ravel())[1:]) + 1)


def split(M, tag, sug, at, names):
    old = M.S[at[1], at[0]]
    state = (M.S == old) & M.land
    inside = biggest(state & M.polygon(sug["pts"]))
    rest = state & ~inside
    # what the drawing cut off from the rest of the old state returns to the new one, if it touches it
    comp = sklabel(rest, connectivity=1)
    keep = comp == (np.argmax(np.bincount(comp.ravel())[1:]) + 1)
    inside |= rest & ~keep
    rest = keep
    new = next(M.fresh_s)
    M.set_state(inside, new, region=M.R[at[1], at[0]])
    M.touched |= rest
    cy = [np.nonzero(x)[0].mean() for x in (inside, rest)]
    cx = [np.nonzero(x)[1].mean() for x in (inside, rest)]
    (a, b) = ("north", "south") if "north" in names else ("west", "east")
    first_inside = (cy[0] < cy[1]) if a == "north" else (cx[0] < cx[1])
    M.names[new] = names[a] if first_inside else names[b]
    M.names[old] = names[b] if first_inside else names[a]
    return f"{inside.sum()} px are {M.names[new]}, {rest.sum()} px {M.names[old]}"


def merge(M, tag, sug, name, sparse=False, pairs=False):
    mine = M.nation(tag)
    inside = mine & M.polygon(sug["pts"])
    area = Counter(M.S[mine].tolist())
    got = Counter(M.S[inside].tolist())
    states = sorted((s for s, n in got.items() if 2 * n >= area[s]), key=lambda s: -area[s])
    if not states:
        return "no state half inside: nothing done"
    m = np.isin(M.S, states) & mine
    groups = [m]
    if pairs:  # the islands two by two, the nearest pair first (an odd one out joins its nearest pair)
        comp = sklabel(m, connectivity=1)
        isl = [comp == q for q in range(1, comp.max() + 1)]
        far = [ndi.distance_transform_edt(~i) for i in isl]
        gap = lambda a, b: far[a][isl[b]].min()
        free, groups = list(range(len(isl))), []
        while len(free) > 1:
            a, b = min(((a, b) for a in free for b in free if a < b), key=lambda ab: gap(*ab))
            groups.append([a, b])
            free = [i for i in free if i not in (a, b)]
        if free:
            near = min(range(len(groups)), key=lambda g: min(gap(free[0], j) for j in groups[g])) if groups else None
            groups[near].append(free[0]) if near is not None else groups.append([free[0]])
        groups = [np.any([isl[i] for i in g], axis=0) for g in groups]
    out = []
    for k, g in enumerate(groups):
        colour = states[0] if k == 0 else next(M.fresh_s)
        M.set_state(g, colour)
        M.names[colour] = name
        n = f"{g.sum()} px"
        if sparse:
            n += f" in {M.recut(colour, SPARSE_PX)} provinces"
        out.append(n)
    return f"{len(states)} states are {len(groups)}: " + "; ".join(out)


def new(M, tag, sug, name):
    inside = biggest(M.nation(tag) & M.polygon(sug["pts"]))
    colour = next(M.fresh_s)
    M.set_state(inside, colour)
    M.names[colour] = name
    return f"{inside.sum()} px"


def drawn(M, tag, sugs):
    mine = M.nation(tag)
    taken = np.zeros((H, W), bool)
    made = []
    for sug in (s for s in sugs if s["type"] == "state"):  # in the order drawn (the import keeps it)
        drawing = mine & M.polygon(sug["pts"])
        m = drawing & ~taken
        if not m.any():
            continue
        taken |= m
        colour = next(M.fresh_s)
        made.append((colour, m))
        M.names[colour] = sug["label"]
        M.shapes[colour] = drawing
    # the land no drawing holds joins the drawn state it shares most border with
    left = mine & ~taken
    comp = sklabel(left, connectivity=1)
    owner = np.zeros((H, W), np.int64)
    for colour, m in made:
        owner[m] = colour
    for q in range(1, comp.max() + 1):
        pm = comp == q
        ring = ndi.binary_dilation(pm, CROSS) & ~pm & (owner > 0)
        nb = Counter(owner[ring].tolist())
        if nb:
            owner[pm] = nb.most_common(1)[0][0]
    for colour, _ in made:
        M.set_state(owner == colour, colour)
    lost = left & (owner == 0)
    return f"{len(made)} states, {left.sum()} px left over joined them" + (f" ({lost.sum()} px kept)" if lost.any() else "")


def province(M, tag, sug):
    m = M.nation(tag) & M.polygon(sug["pts"])
    m = biggest(m)
    if m.sum() < MIN_PROVINCE:
        return "too small: nothing done"
    M.P[m] = next(M.fresh_p)
    M.touched |= m
    return f"{m.sum()} px"


def island(M, tag, sug):
    """the land the drawing holds is cut free by a channel where it meets the rest (its neck becomes sea); an islet
    left under MIN_PROVINCE px grows into the sea the drawing holds, never next to the rest (not even corner to
    corner) and never shutting a bit of sea off, until it is a province"""
    mine = M.nation(tag)
    poly = M.polygon(sug["pts"])
    knob = biggest(mine & poly)
    rest = mine & ~knob
    neck = knob & ndi.binary_dilation(rest, CROSS)
    isle = knob & ~neck
    keep_off = ndi.binary_dilation(rest, np.ones((3, 3), bool)) | neck
    ys, xs = np.nonzero(knob)
    win = np.s_[ys.min() - 8:ys.max() + 9, xs.min() - 8:xs.max() + 9]
    seas = lambda extra: sklabel((M.sea | neck)[win] & ~extra[win], connectivity=1).max()
    grown = np.zeros((H, W), bool)
    base = seas(grown)
    cy, cx = [v.mean() for v in np.nonzero(isle)]
    while isle.sum() + grown.sum() < MIN_PROVINCE + 2:
        edge = ndi.binary_dilation(isle | grown, CROSS) & M.sea & poly & ~keep_off & ~(isle | grown)
        ys, xs = np.nonzero(edge)
        done = False
        for k in np.argsort((ys - cy) ** 2 + (xs - cx) ** 2):
            grown[ys[k], xs[k]] = True
            if seas(grown) <= base:
                done = True
                break
            grown[ys[k], xs[k]] = False
        if not done:
            break
    if grown.any():  # the new land is like the islet's own
        y0, x0 = [int(v[0]) for v in np.nonzero(isle)]
        for nm in ("Terrain", "Heightmap", "Continents", "States", "Countries", "Strategic Regions"):
            M.L[nm][grown] = M.L[nm][y0, x0]
        M.L["Rivers"][grown, 3] = 0
        M.land |= grown
        M.sea &= ~grown
        for arr in (M.S, M.R, M.K):
            arr[grown] = arr[y0, x0]
    M.P[isle | grown] = next(M.fresh_p)
    T.put(M.L["Provinces"], M.P, isle | grown)
    ys, xs = np.nonzero(knob | grown)
    T.to_sea(M.L, neck, M.sea, M.land, (ys.min() - 2, ys.max() + 3, xs.min() - 2, xs.max() + 3), 20261018)
    M.P = T.code(M.L["Provinces"][..., :3])
    M.S[neck] = -1
    M.touched |= isle | grown
    return (f"{neck.sum()} px of neck became sea; the island is {isle.sum()} px of land"
            + (f" and {grown.sum()} px won from the sea inside the drawing" if grown.any() else ""))

def main():
    names, L = T.load()
    M = Map(L)
    facts = {}
    only = next((a.split("=", 1)[1].split(",") for a in sys.argv if a.startswith("--only=")), None)
    for tag, sid, how, args in PLAN:
        if only and tag not in only:
            continue
        f = facts.setdefault(tag, json.loads(Path(f"source/gazetteer/{tag}.json").read_text(encoding="utf-8")))
        sugs = f.get("suggest", [])
        if how == "drawn":
            print(f"{tag} drawn: {drawn(M, tag, sugs)}")
            continue
        sug = next(s for s in sugs if s["label"] == sid)
        out = globals()[how](M, tag, sug, **args)
        print(f"{tag} {how} {sug['label']!r}: {out}")
    M.tidy_provinces()
    # the names, at the pixel deepest inside each named state; the old names inside them go
    sn = json.loads(NAMES.read_text(encoding="utf-8"))
    affected = set(M.names) | set(np.unique(M.S[M.touched]).tolist())
    for key in list(sn):
        x, y = map(int, key.split(","))
        if M.S[y, x] in affected and M.S[y, x] in M.names:
            print(f"  state_names.json: {sn[key]!r} at {key} gives way")
            del sn[key]
    for colour, nm in M.names.items():
        m = (M.S == colour) & M.land
        if not m.any():  # too small for a province (under MIN_PROVINCE px): its land went to a neighbour
            print(f"  {nm}: no land left, too small for a province: its land joined a neighbour, its name not kept")
            continue
        d = ndi.distance_transform_edt(m)
        y, x = np.unravel_index(int(np.argmax(d)), d.shape)
        sn[f"{x},{y}"] = nm
        print(f"  {nm}: {m.sum()} px, named at ({x}, {y})")
    if "--apply" in sys.argv:
        M.save()
        T.save(names, L)
        NAMES.write_text(json.dumps(sn, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"wrote {NAMES}")
    else:
        print("(nothing saved: --apply to save)")


if __name__ == "__main__":
    main()
