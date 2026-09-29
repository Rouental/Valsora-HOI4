"""Turn outlines drawn on "HOI4 Mod Map.pdn" into provinces, states and countries.

The author draws 1-px lines on two layers:
    Borders              country borders
    Necessary Provinces  borders inside a country that must be province borders
Every patch of land enclosed by those lines becomes a province (patches over
SPLIT_AREA px are cut into several). OWNERS names the country of each patch by one
pixel inside it; every other enclosed patch goes to DEFAULT_OWNER. Each non-default
country becomes one state; the default owner's patches are grouped into states of
about STATE_AREA px, with exclaves and islands as states of their own.

The script rewrites the Provinces, States, Countries and Strategic Regions layers of
the decoded .pdn (work/pdn_new) and saves the result as source/HOI4 Mod Map.pdn, using
the input file itself as the template. Land outside the outlines is untouched, except
that leftover slivers of cut placeholder provinces and states join a neighbour.

    python3 scripts/apply_outlines.py <input.pdn>
"""
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi
from skimage.measure import label as sklabel

from common import COUNTRIES, MAP_W as W, MAP_H as H, MIN_PROVINCE
from provinces import adjacency
from writepdn import write_pdn

SRC = Path("work/pdn_new")
OUT = Path("source/HOI4 Mod Map.pdn")
LINE_LAYERS = ["Borders", "Necessary Provinces"]
OCEAN, LAKES = (8, 31, 130), (55, 90, 220)

# Rouental and its neighbours (author's map of 2026-09-29). (x, y) = a pixel inside.
DEFAULT_OWNER = "rouental"
OWNERS = {
    "selgrave": [(859, 762)],
    "lanzerac": [(853, 781)],
    "lustiana": [(823, 786)],
    "evriches": [(797, 802)],
    "hollier": [(845, 815)],
    "seigne": [(811, 818)],
    "guedelon": [(748, 871)],
    # Rouental's exclaves ("RT") are enclosed patches like the rest; the lake island
    # has no outline, so it is named here to be included
    "rouental": [(829, 765), (798, 792), (823, 803), (811, 906)],
}
SPLIT_AREA = 2000   # enclosed patches bigger than this are cut into ~1100 px provinces
PROVINCE_AREA = 1100
STATE_AREA = 3500   # target size of the default owner's states
MIN_LEFTOVER = 300  # smaller remains of a cut placeholder province join a neighbour


def code(rgb):
    rgb = rgb.astype(np.int64)
    return (rgb[..., 0] << 16) | (rgb[..., 1] << 8) | rgb[..., 2]


def rgb_of(c):
    return np.array([c >> 16, (c >> 8) & 255, c & 255], np.uint8)


class Colours:
    """Hands out colours not yet used on a layer."""

    def __init__(self, used, seed):
        self.used = set(int(c) for c in np.unique(used))
        self.rng = np.random.default_rng(seed)

    def new(self):
        while True:
            c = int(self.rng.integers(1, 1 << 24))
            r, g, b = c >> 16, (c >> 8) & 255, c & 255
            if c not in self.used and min(r, g, b) > 30:
                self.used.add(c)
                return c


def kmeans_split(ys, xs, k, seed=0):
    """Split a patch's pixels into k compact, connected pieces."""
    pts = np.stack([ys, xs], 1).astype(float)
    rng = np.random.default_rng(seed)
    cent = pts[rng.choice(len(pts), k, replace=False)]
    for _ in range(30):
        a = np.argmin(((pts[:, None] - cent[None]) ** 2).sum(-1), 1)
        cent = np.array([pts[a == j].mean(0) if (a == j).any() else cent[j] for j in range(k)])
    return a


def main():
    names = (SRC / "layers.txt").read_text().splitlines()
    L = {nm: np.load(SRC / f"layer{k}.npy") for k, nm in enumerate(names)}
    terr = code(L["Terrain"][..., :3])
    land = (terr != code(np.array(OCEAN))) & (terr != code(np.array(LAKES)))
    lines = np.zeros((H, W), bool)
    for nm in LINE_LAYERS:
        lines |= L[nm][..., 3] > 0

    # ------------------------------------------------ enclosed patches -> new provinces
    cells = sklabel(land & ~lines, connectivity=1)
    size = np.bincount(cells.ravel())
    touch = np.zeros(len(size), bool)  # patches that touch a line
    near = ndi.binary_dilation(lines, np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]))
    touch[np.unique(cells[near])] = True
    touch[0] = False
    outside = int(np.argmax(np.where(touch, size, 0)))  # the rest of the continent
    owner_of = {}
    for tag, pts in OWNERS.items():
        for x, y in pts:
            owner_of[int(cells[y, x])] = tag
    chosen = [i for i in np.nonzero(touch)[0] if i != outside] + \
        [i for i in owner_of if not touch[i]]
    chosen = sorted(set(chosen))
    for i in chosen:
        owner_of.setdefault(int(i), DEFAULT_OWNER)
    # line pixels on land go to the nearest patch (inside or out)
    idx = ndi.distance_transform_edt(cells == 0, return_distances=False, return_indices=True)
    cells = np.where(land & (cells == 0), cells[idx[0], idx[1]], cells)
    area = np.isin(cells, chosen)
    print(f"{len(chosen)} outlined patches, {area.sum()} px, outside patch {outside}")

    P = code(L["Provinces"][..., :3])
    cut = set(np.unique(P[area]).tolist())  # placeholder provinces the outlines cut into
    pcols = Colours(P, 1)
    newP = P.copy()
    prov_owner = {}   # new province colour -> owner
    prov_cell = {}    # new province colour -> patch id
    for i in chosen:
        ys, xs = np.nonzero(cells == i)
        k = max(1, round(len(ys) / PROVINCE_AREA)) if len(ys) > SPLIT_AREA else 1
        parts = kmeans_split(ys, xs, k, seed=int(i)) if k > 1 else np.zeros(len(ys), int)
        for j in range(k):
            c = pcols.new()
            newP[ys[parts == j], xs[parts == j]] = c
            prov_owner[c] = owner_of[int(i)]
            prov_cell[c] = int(i)

    # ------------------------------------------------ leftovers of cut provinces
    # Every province near the outlines must end up one connected piece of a decent
    # size: stray scraps join the neighbour they share most border with (a new
    # province prefers one of the same country), larger extra pieces of a cut
    # placeholder become provinces of their own. Repeat until nothing changes.
    ys, xs = np.nonzero(area)
    y0, y1 = max(ys.min() - 64, 0), min(ys.max() + 65, H)
    x0, x1 = max(xs.min() - 64, 0), min(xs.max() + 65, W)
    win = newP[y0:y1, x0:x1]  # a view: edits land in newP
    wland = land[y0:y1, x0:x1]
    cross = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])
    merged = split = 0
    for _ in range(20):
        changed = False
        for c in np.unique(win[wland]):
            m = (win == c) & wland
            comp = sklabel(m, connectivity=1)
            sizes = np.bincount(comp.ravel())[1:]
            keep = int(np.argmax(sizes)) + 1
            new = int(c) in prov_owner
            for j, sz in enumerate(sizes, 1):
                limit = MIN_PROVINCE if new else (MIN_PROVINCE if j == keep and c not in cut else MIN_LEFTOVER)
                if j == keep and sz >= limit:
                    continue
                pm = comp == j
                if sz >= limit:  # a big extra piece: its own province
                    win[pm] = pcols.new()
                    split += 1
                    changed = True
                    continue
                ring = ndi.binary_dilation(pm, cross) & ~pm & wland
                nb = Counter(v for v in win[ring].tolist() if v != c)
                if not nb:
                    continue
                pref = [v for v in nb if (prov_owner.get(v) == prov_owner.get(int(c)))]
                target = max(pref or nb, key=lambda v: nb[v])
                win[pm] = target
                merged += 1
                changed = True
        if not changed:
            break
    alive = set(np.unique(win).tolist())
    for c in [c for c in prov_owner if c not in alive]:  # tiny outlined patches merged away
        del prov_owner[c]
    print(f"{len(cut)} placeholder provinces were cut; {merged} scraps joined a neighbour, "
          f"{split} extra pieces became provinces")

    # ------------------------------------------------ states
    S = np.where(L["States"][..., 3] > 0, code(L["States"][..., :3]), -1)
    scols = Colours(S[S >= 0], 2)
    newS = S.copy()
    # group the new provinces: one state per non-default country, default owner by size
    by_owner = defaultdict(list)
    for c, t in prov_owner.items():
        by_owner[t].append(c)
    labP = np.unique(newP, return_inverse=True)[1].reshape(H, W)
    colour_of_lab = np.unique(newP)
    a, b, _ = adjacency(labP, wrap=True)
    nbrs = defaultdict(set)
    for x, y in zip(colour_of_lab[a], colour_of_lab[b]):
        nbrs[int(x)].add(int(y))
        nbrs[int(y)].add(int(x))
    psize = {int(c): int(n) for c, n in zip(colour_of_lab, np.bincount(labP.ravel()))}
    cent = {}
    for c in prov_owner:
        ys, xs = np.nonzero(newP == c)
        cent[c] = (ys.mean(), xs.mean())
    state_groups = []  # (owner, [province colours])
    for t, provs in sorted(by_owner.items()):
        # connected pieces of this owner's provinces
        left, pieces = set(provs), []
        while left:
            st, seen = [left.pop()], []
            while st:
                u = st.pop()
                seen.append(u)
                for v in nbrs[u]:
                    if v in left:
                        left.remove(v)
                        st.append(v)
            pieces.append(seen)
        for piece in pieces:
            tot = sum(psize[c] for c in piece)
            k = max(1, round(tot / STATE_AREA)) if t == DEFAULT_OWNER else 1
            if k == 1:
                state_groups.append((t, piece))
                continue
            # grow k states from spread-out seeds, always adding the next nearest province
            order = sorted(piece, key=lambda c: cent[c])
            seeds = [order[round(j * (len(order) - 1) / (k - 1))] for j in range(k)]
            owner = {s: j for j, s in enumerate(seeds)}
            grow = [psize[s] for s in seeds]
            while len(owner) < len(piece):
                best = None
                for c in piece:
                    if c in owner:
                        continue
                    for v in nbrs[c]:
                        if v in owner:
                            j = owner[v]
                            key = (grow[j], np.hypot(*np.subtract(cent[c], cent[seeds[j]])))
                            if best is None or key < best[0]:
                                best = (key, c, j)
                if best is None:
                    break
                _, c, j = best
                owner[c] = j
                grow[j] += psize[c]
            for j in range(k):
                g = [c for c in piece if owner.get(c) == j]
                if g:
                    state_groups.append((t, g))
    new_states = []
    for t, g in state_groups:
        sc = scols.new()
        for c in g:
            newS[newP == c] = sc
        new_states.append((t, sc, g))
    newS[~land] = -1
    fresh = {sc for _, sc, _ in new_states}  # old scraps must not join these
    # old states cut in pieces: pieces away from the main one join the neighbour
    for sc in np.unique(S[area & (S >= 0)]):
        rest = (newS == sc)
        if not rest.any():
            continue
        comp = sklabel(rest, connectivity=1)
        sizes = np.bincount(comp.ravel())[1:]
        keep = int(np.argmax(sizes)) + 1
        for j in range(1, len(sizes) + 1):
            if j == keep:
                continue
            m = comp == j
            ring = ndi.binary_dilation(m) & ~m & land
            nb = Counter(v for v in newS[ring].tolist() if v >= 0 and v != sc and v not in fresh)
            if nb and sizes[j - 1] < 3000:
                newS[m] = nb.most_common(1)[0][0]
    print(f"{len(new_states)} new states: " + ", ".join(
        f"{t} {sum(1 for s in new_states if s[0] == t)}" for t in sorted(by_owner)))

    # ------------------------------------------------ countries
    K = code(L["Countries"][..., :3])
    newK = K.copy()
    for t, sc, g in new_states:
        newK[newS == sc] = code(np.array(COUNTRIES[t][3]))

    # ------------------------------------------------ strategic regions
    R = code(L["Strategic Regions"][..., :3])
    newR = R.copy()
    # every state near the outlines lies in the region most of it was in
    near_area = newS[y0:y1, x0:x1]
    for sc in np.unique(near_area[near_area >= 0]):
        m = newS == sc
        newR[m] = Counter(R[m].tolist()).most_common(1)[0][0]

    # ------------------------------------------------ write
    def put(layer, codes, mask=None):
        out = L[layer].copy()
        m = np.ones((H, W), bool) if mask is None else mask
        out[m, :3] = np.stack([codes[m] >> 16, (codes[m] >> 8) & 255, codes[m] & 255], 1)
        if mask is not None:
            out[..., 3] = np.where(mask, 255, 0)
        return out

    L["Provinces"] = put("Provinces", newP)
    L["States"] = put("States", np.maximum(newS, 0), newS >= 0)
    L["Countries"] = put("Countries", newK, L["Countries"][..., 3] > 0)
    L["Strategic Regions"] = put("Strategic Regions", newR)
    template = sys.argv[1]
    tmp = OUT.with_suffix(".tmp")
    write_pdn(template, tmp, [L[nm] for nm in names])
    shutil.move(tmp, OUT)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
