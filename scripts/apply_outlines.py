"""Turn outlines drawn on "HOI4 Mod Map.pdn" into states, provinces and countries.

The author draws 1-px lines on two layers:
    Borders              country borders
    Necessary Provinces  state borders inside a country (the layer name is historical)
Every patch of land enclosed by those lines becomes a state; patches over STATE_MAX px
are cut into several states that fill the same shape. Every state is cut into
provinces of about PROVINCE_AREA px, for a granular map. OWNERS names the country of
each patch by one pixel inside it; every other enclosed patch goes to DEFAULT_OWNER.

The script rewrites the Provinces, States, Countries and Strategic Regions layers of
the decoded .pdn (work/pdn_new) and saves the result as source/HOI4 Mod Map.pdn, using
the input file itself as the template. Land outside the outlines is untouched, except
that leftover slivers of cut placeholder provinces and states join a neighbour.

    python3 scripts/apply_outlines.py <input.pdn>
"""
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi
from skimage.measure import label as sklabel

from common import COUNTRIES, MAP_W as W, MAP_H as H, MIN_PROVINCE, PLACEHOLDERS
import organic
from writepdn import write_pdn

SRC = Path("work/pdn_outlines")  # the input .pdn, decoded here first
OUT = Path("source/HOI4 Mod Map.pdn")
LINE_LAYERS = ["Borders", "Necessary Provinces"]
OCEAN, LAKES = (8, 31, 130), (55, 90, 220)

# Who gets the newly outlined patches. Patches already painted in a real (non-
# placeholder) country's colour were done by an earlier run and are left alone, so
# each run only needs the new countries. (x, y) = a pixel inside a patch.
#
# 2026-09-29, Rouental and neighbours: DEFAULT_OWNER "rouental"; selgrave (859, 762),
# lanzerac (853, 781), lustiana (823, 786), evriches (797, 802), hollier (845, 815),
# seigne (811, 818), guedelon (748, 871); rouental exclaves (829, 765), (798, 792),
# (823, 803) and the lake island (811, 906), which has no outline.
# 2026-09-29, Cardonia north of Rouental: every new patch, plus the islands the
# author's References layer colours Cardonian (they have no outlines): (873, 630),
# (905, 593), (920, 548), (605, 646), (598, 726), (698, 536), (618, 549), (593, 562),
# (689, 580).
# 2026-09-30, Romanoddle, Selto and Linterre south-west of Rouental: DEFAULT_OWNER
# "linterre"; the islands are the ones the author's Names layer labels RO / LT.
# Afterwards (pdn_tools.py give) five Linterre states along the Piscary coast went to
# Selto, matching the author's older drawing (Notes layer), and the island at (300, 785)
# was cut off from Romanoddle's island by reopening its strait, as Nonscio's.
# Afterwards (pdn_tools.py give) five Linterre states along the Piscary coast went to
# Selto, matching the author's older drawing (Notes layer), and the island at (300, 785)
# was cut off from Romanoddle's island by reopening its strait, as Nonscio's.
DEFAULT_OWNER = "linterre"
OWNERS = {
    "romanoddle": [(350, 1000), (323, 835), (481, 829), (447, 807), (438, 813), (514, 822)],
    "selto": [(600, 965)],
    "linterre": [(559, 734), (556, 760), (532, 802)],
}
MIN_STATE = 150      # smaller patches (islets) join the nearest state of their country
STATE_MAX = 1000     # patches bigger than this become several states ...
STATE_AREA = 650     # ... of about this size
PROVINCE_AREA = 150  # target province size inside the outlines (placeholders: 1024)
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
    """Split pixels into k compact pieces, each one 4-connected."""
    if k <= 1:
        return np.zeros(len(ys), int)
    pts = np.stack([ys, xs], 1).astype(float)
    rng = np.random.default_rng(seed)
    # spread-out start: farthest-point seeding
    cent = [pts[rng.integers(len(pts))]]
    for _ in range(k - 1):
        d = np.min([((pts - c) ** 2).sum(1) for c in cent], 0)
        cent.append(pts[int(np.argmax(d))])
    cent = np.array(cent)
    for _ in range(30):
        a = np.argmin(((pts[:, None] - cent[None]) ** 2).sum(-1), 1)
        cent = np.array([pts[a == j].mean(0) if (a == j).any() else cent[j] for j in range(k)])
    # make every piece connected: stray bits join the piece they touch most
    y0, x0 = ys.min(), xs.min()
    grid = np.full((ys.max() - y0 + 1, xs.max() - x0 + 1), -1)
    grid[ys - y0, xs - x0] = a
    cross = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])
    for _ in range(20):
        changed = False
        for j in range(k):
            comp = sklabel(grid == j, connectivity=1)
            sizes = np.bincount(comp.ravel())[1:]
            if len(sizes) <= 1:
                continue
            keep = int(np.argmax(sizes)) + 1
            for q in range(1, len(sizes) + 1):
                if q == keep:
                    continue
                m = comp == q
                ring = ndi.binary_dilation(m, cross) & ~m & (grid >= 0) & (grid != j)
                if ring.any():
                    grid[m] = Counter(grid[ring].tolist()).most_common(1)[0][0]
                    changed = True
        if not changed:
            break
    return grid[ys - y0, xs - x0]


def organic_split(ys, xs, k, seed=0):
    """k pieces with natural borders: k-means picks where the pieces sit, then each grows
    from the pixel nearest its k-means centre over noise (organic.py)."""
    if k <= 1:
        return np.zeros(len(ys), int)
    a = kmeans_split(ys, xs, k, seed)
    seeds = []
    for j in range(k):
        m = a == j
        if not m.any():
            continue
        cy, cx = ys[m].mean(), xs[m].mean()
        i = np.argmin((ys[m] - cy) ** 2 + (xs[m] - cx) ** 2)
        seeds.append((ys[m][i], xs[m][i]))
    return organic.split(ys, xs, seeds, seed)


def main():
    subprocess.run([sys.executable, str(Path(__file__).parent / "readpdn.py"), sys.argv[1], str(SRC)],
                   check=True, stdout=subprocess.DEVNULL)
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
    # skip patches an earlier run already turned into a real country, unless a new line
    # cuts through one of their states: those are cut again and keep their country
    K0 = code(L["Countries"][..., :3])
    real_col = {code(np.array(COUNTRIES[c][3])): c for c in COUNTRIES if c not in PLACEHOLDERS}
    done = np.isin(K0, list(real_col)) & land
    dsum = np.bincount(cells[done], minlength=len(size))
    S0 = np.where(L["States"][..., 3] > 0, code(L["States"][..., :3]), -1)

    def cut_by_lines(sc):
        """True if the lines split state sc into more pieces than it has anyway
        (islets across water are fine)."""
        ys, xs = np.nonzero(S0 == sc)
        sl = np.s_[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        m = S0[sl] == sc
        whole = np.bincount(sklabel(m, connectivity=1).ravel())[1:]
        parts = np.bincount(sklabel(m & ~lines[sl], connectivity=1).ravel())[1:]
        return (parts >= 8).sum() > (whole >= 8).sum()

    before = len(chosen)
    kept, recut = [], []
    for i in chosen:
        if dsum[i] * 2 < size[i]:
            kept.append(i)
            continue
        ys, xs = np.nonzero(cells == i)
        if not any(cut_by_lines(sc) for sc in np.unique(S0[ys, xs]) if sc >= 0):
            continue
        kept.append(i)
        recut.append(i)
        owner_of[int(i)] = real_col[Counter(K0[ys, xs].tolist()).most_common(1)[0][0]]
    chosen = kept
    print(f"{before - len(chosen)} patches were outlined by an earlier run and are kept as they are; "
          f"{len(recut)} are cut again because new lines split their states")
    for i in chosen:
        owner_of.setdefault(int(i), DEFAULT_OWNER)
    # line pixels on land go to the nearest patch (inside or out)
    idx = ndi.distance_transform_edt(cells == 0, return_distances=False, return_indices=True)
    cells = np.where(land & (cells == 0), cells[idx[0], idx[1]], cells)
    area = np.isin(cells, chosen) & (~done | np.isin(cells, recut))
    print(f"{len(chosen)} outlined patches, {area.sum()} px, outside patch {outside}")

    P = code(L["Provinces"][..., :3])
    cut = set(np.unique(P[area]).tolist())  # placeholder provinces the outlines cut into
    pcols = Colours(P, 1)
    newP = P.copy()
    prov_owner = {}   # new province colour -> owner
    prov_state = {}   # new province colour -> (patch id, state number in the patch)
    for i in chosen:
        ys, xs = np.nonzero(cells == i)
        ks = max(1, round(len(ys) / STATE_AREA)) if len(ys) > STATE_MAX else 1
        st = organic_split(ys, xs, ks, seed=int(i))
        for j in range(ks):
            sy, sx = ys[st == j], xs[st == j]
            if len(sy) == 0:
                continue
            kp = min(max(1, round(len(sy) / PROVINCE_AREA)), len(sy) // MIN_PROVINCE or 1)
            parts = organic_split(sy, sx, kp, seed=int(i) * 31 + j)
            for q in range(kp):
                if not (parts == q).any():
                    continue
                c = pcols.new()
                newP[sy[parts == q], sx[parts == q]] = c
                prov_owner[c] = owner_of[int(i)]
                prov_state[c] = (int(i), j)

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
                # a new province's scrap stays in its state, an old one's outside
                same_state = [v for v in nb if prov_state.get(v) == prov_state.get(int(c))]
                same_owner = [v for v in nb if prov_owner.get(v) == prov_owner.get(int(c))]
                target = max(same_state or same_owner or nb, key=lambda v: nb[v])
                win[pm] = target
                merged += 1
                changed = True
        if not changed:
            break
    alive = set(np.unique(win).tolist())
    for c in [c for c in prov_owner if c not in alive]:  # tiny outlined patches merged away
        del prov_owner[c], prov_state[c]
    print(f"{len(cut)} placeholder provinces were cut; {merged} scraps joined a neighbour, "
          f"{split} extra pieces became provinces")

    # ------------------------------------------------ states
    S = np.where(L["States"][..., 3] > 0, code(L["States"][..., :3]), -1)
    scols = Colours(S[S >= 0], 2)
    newS = S.copy()
    # islets too small for a state of their own join the nearest state of their country
    cent = {}
    for c in prov_state:
        ys, xs = np.nonzero(win == c)
        cent[c] = (ys.mean(), xs.mean())
    patch_size = {i: int(size[i]) for i in chosen}
    for c, key in list(prov_state.items()):
        if patch_size[key[0]] >= MIN_STATE or key[0] in recut:  # a drawn split is kept
            continue
        best = min((k for k in prov_state if patch_size[prov_state[k][0]] >= MIN_STATE
                    and prov_owner[k] == prov_owner[c]),
                   key=lambda k: np.hypot(cent[k][0] - cent[c][0], cent[k][1] - cent[c][1]),
                   default=None)
        if best is not None:
            prov_state[c] = prov_state[best]
    # one state per (patch, piece), as drawn
    groups = defaultdict(list)
    for c, key in prov_state.items():
        groups[key].append(c)
    by_owner = defaultdict(list)
    state_groups = []  # (owner, [province colours])
    for key in sorted(groups):
        g = groups[key]
        state_groups.append((prov_owner[g[0]], g))
        by_owner[prov_owner[g[0]]].append(key)
    new_states = []
    for t, g in state_groups:
        sc = scols.new()
        newS[np.isin(newP, g)] = sc
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
