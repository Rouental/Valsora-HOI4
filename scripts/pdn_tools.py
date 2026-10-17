"""Edits made directly to the layers of source/HOI4 Mod Map.pdn, run by hand.

    python3 scripts/pdn_tools.py navigable X,Y [X,Y ...]
        Turn the lakes containing these pixels into sea (Terrain layer), each in a new
        sea region of its own (Strategic Regions layer). HOI4 ships can use sea, not lakes.
    python3 scripts/pdn_tools.py recolour LAYER R,G,B=R,G,B [...]
        Swap exact colours on a layer, e.g. a country's colour on "Countries" after it
        changed in common.COUNTRIES (the build matches countries by exact colour).
    python3 scripts/pdn_tools.py give COUNTRY X,Y [X,Y ...]
        Give the whole states containing these pixels to COUNTRY (a common.COUNTRIES key),
        on the Countries layer.
    python3 scripts/pdn_tools.py attach COUNTRY X,Y [X,Y ...]
        Give COUNTRY the states containing these pixels and merge each into COUNTRY's
        nearest state (Countries, States and Strategic Regions layers), the way islets
        too small for a state of their own join their country's nearest state: for a
        sliver or islet left behind (2026-10-09: "Araseos 1", 19 px off Terreich's coast).
    python3 scripts/pdn_tools.py add_land COUNTRY [LAYER]
        Make the water under LAYER's opaque pixels (default "Islands to Add", where the
        author painted new islands on 2026-10-13) land of COUNTRY: plains, the nearest
        land's height, continent and strategic region, a province per island and one new
        state for all of them. The layer itself is left as it is.
    python3 scripts/pdn_tools.py border COUNTRY X,Y [X,Y ...]
        Give COUNTRY all the land enclosed by Necessary Borders lines around these pixels
        (the line pixels too), on the Countries layer: a border the author moved. Run
        regroup_states.py afterwards so the states follow the lines.
    python3 scripts/pdn_tools.py cede FROM TO X,Y [X,Y ...]
        Give TO the land of FROM (common.COUNTRIES keys) that Necessary Borders lines cut
        off around these pixels, for a moved border between countries without state
        lines of their own (border + regroup_states.py need those). Only FROM's pixels
        count, so open sea and other countries around it don't matter. Provinces a line
        crosses are split along it (a piece under 40 px joins a neighbour on its side);
        the part a split state loses becomes a state of its own if it has CEDED_STATE px
        or more, and otherwise joins a neighbouring state that moved whole (or becomes a
        state of its own if none touches it).
    python3 scripts/pdn_tools.py owners [--apply] [X,Y=COUNTRY ...]
        Settle every area the Necessary Borders lines enclose that holds two nations' land (a border the author moved
        through a nation, or a merge): the whole area goes to one nation, taken from an X,Y=COUNTRY given for a pixel
        in it, else from a stroke on the "Necessary Owners" layer (any colour) that starts in the area and ends in the
        new owner's land, else to the nation holding most of it. X,Y=COUNTRY also moves an area holding one nation (a
        label the author moved). Without --apply it only prints the plan and saves nothing. Applied, a nation whose
        states lie wholly inside the area hands them over as they are (as `border`); one whose states the line
        crosses is cut along it (as `cede`). Areas listed in OWNERS_KEEP are left alone. Then regroup_states.py.
        (2026-10-17, the efficiency night: the three border moves of that day's upload were each the area's majority.)
    python3 scripts/pdn_tools.py merge_small COUNTRY MIN_PX
        Merge COUNTRY's states smaller than MIN_PX into the neighbouring state of the same
        country they share most border with (States layer), e.g. the slivers a moved
        border leaves behind. Provinces stay as they are.
    python3 scripts/pdn_tools.py recut [--keep-states] X,Y [X,Y ...]
        Cut placeholder land again the way apply_outlines.py cuts an outlined patch: the
        piece of a country's land around each pixel (what the Necessary lines enclose, or
        a whole island) becomes states of about STATE_AREA px (one up to STATE_MAX px), and
        each state provinces of about PROVINCE_AREA px with organic borders. Countries stay;
        a new state takes the strategic region most of it lies in. With --keep-states the
        states stay as they are and only their provinces are cut again. For land the
        outline runs never reached, still in the placeholder build's 32 px bricks and
        96 px grid states (2026-10-15: Arvorenia's and Atrocha's islands, from the friend's
        build of 2026-10-05, and two island groups given whole).
    python3 scripts/pdn_tools.py provinces
        The author's province lines (the "Necessary Provinces" layer, read from 2026-10-17,
        when they redrew Seigne's and Royalist Illiricium's): every state such a line
        crosses gets exactly the provinces the lines and the state's own edges enclose, in
        place of the ones cut for it (pieces under MIN_PROVINCE px join the neighbour they
        share most border with, line pixels the nearest piece). A state the lines don't
        divide is left as it is, with a note. States, countries and regions don't change.
    python3 scripts/pdn_tools.py tidy
        Merge every land province under MIN_PROVINCE px into the neighbouring province it
        shares most border with, one of its own state first; a scrap that only touches
        another state's provinces takes that state, country and region too. For the line
        pixels a re-cut can leave as provinces of their own (2026-10-17: 30, mostly 1 px).
    python3 scripts/pdn_tools.py lakes
        Make each lake one province (the placeholder build cut them into 48 px squares),
        in the strategic region most of it was in.
    python3 scripts/pdn_tools.py blue_seas
        Recolour every sea province on the Provinces layer in its own blue (the author
        wants the sea easy to tell from land there). Colours only: nothing else changes.
    python3 scripts/pdn_tools.py channel X1,Y1,X2,Y2[,M] [...]
        Reopen a strait that closed when the world was scaled down: the cheapest
        4-connected path from the water at (X1, Y1) to the water at (X2, Y2), counting
        land pixels, becomes sea in the nearest sea province and region. Land provinces it
        cuts apart are split (pieces of 16+ px) or merged into a neighbour. The path stays within M px
        (default 8) of the box the two ends make: M 0 cuts an islet's neck the sea goes round otherwise.
    python3 scripts/pdn_tools.py sea_zones [CELL]
        Regroup all sea provinces into larger sea regions (about CELL px across, default
        1536), and recolour the Strategic Regions layer so sea regions are blues and land
        regions never are. Refused on a map with Merlo's "Ocean Province Lines" layer
        (2026-10-12): its 42 sea regions would be lost (scripts/sea_provinces.py handles
        the sea now).

The .pdn is decoded to work/pdn_tools, edited, and saved over itself (its own object
graph is the template, so layer names, order and visibility are kept).
"""
import colorsys
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi

from common import MAP_W as W, MAP_H as H, MIN_PROVINCE
from writepdn import write_pdn

PDN = Path("source/HOI4 Mod Map.pdn")
WORK = Path("work/pdn_tools")
OCEAN, LAKES = (8, 31, 130), (55, 90, 220)
CROSS = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])
CEDED_STATE = 600  # cede: a split state's ceded part this big is a state, not a sliver


def code(rgb):
    rgb = rgb.astype(np.int64)
    return (rgb[..., 0] << 16) | (rgb[..., 1] << 8) | rgb[..., 2]


def load():
    subprocess.run([sys.executable, str(Path(__file__).parent / "readpdn.py"), str(PDN), str(WORK)],
                   check=True, stdout=subprocess.DEVNULL)
    names = (WORK / "layers.txt").read_text().splitlines()
    return names, {nm: np.load(WORK / f"layer{k}.npy") for k, nm in enumerate(names)}


def save(names, L):
    tmp = PDN.with_suffix(".tmp")
    write_pdn(PDN, tmp, [L[nm] for nm in names])
    shutil.move(tmp, PDN)
    print(f"wrote {PDN}")


def put(layer, codes, mask):
    layer[mask, 0] = codes[mask] >> 16
    layer[mask, 1] = (codes[mask] >> 8) & 255
    layer[mask, 2] = codes[mask] & 255


def palette(n, blue, seed, used=()):
    """n distinct colours; blues (hue 0.53-0.70) or anything but blue."""
    rng = np.random.default_rng(seed)
    out, seen = [], set(used)
    while len(out) < n:
        if blue:
            h, s, v = rng.uniform(0.53, 0.70), rng.uniform(0.45, 0.95), rng.uniform(0.40, 0.95)
        else:
            h = rng.uniform(0.0, 0.78)
            h = h if h < 0.42 else h + 0.40  # skip cyans, blues and indigos (0.42-0.82)
            s, v = rng.uniform(0.35, 0.85), rng.uniform(0.55, 0.95)
        r, g, b = (round(c * 255) for c in colorsys.hsv_to_rgb(h % 1.0, s, v))
        c = (r << 16) | (g << 8) | b
        if c not in seen and c != 0:
            seen.add(c)
            out.append(c)
    return out


def navigable(names, L, seeds):
    T = code(L["Terrain"][..., :3])
    lake = T == code(np.array(LAKES))
    lab, _ = ndi.label(lake, CROSS)
    R = code(L["Strategic Regions"][..., :3])
    for x, y in seeds:
        i = lab[y, x]
        if i == 0:
            sys.exit(f"({x}, {y}) is not on a lake")
        m = lab == i
        L["Terrain"][m, :3] = OCEAN
        col = palette(1, True, x * 7919 + y, set(np.unique(R).tolist()))[0]
        put(L["Strategic Regions"], np.full(R.shape, col), m)
        print(f"lake at ({x}, {y}): {m.sum()} px is now sea, in its own sea region")


def sea_zones(names, L, cell):
    T = code(L["Terrain"][..., :3])
    sea = T == code(np.array(OCEAN))
    P = code(L["Provinces"][..., :3])
    R = code(L["Strategic Regions"][..., :3])
    pcols, plab = np.unique(P, return_inverse=True)
    plab = plab.reshape(H, W)
    n = len(pcols)
    size = np.bincount(plab.ravel(), minlength=n)
    seasz = np.bincount(plab.ravel(), weights=sea.ravel(), minlength=n)
    is_sea = seasz * 2 > size
    cy, cx = (np.bincount(plab.ravel(), weights=g.ravel(), minlength=n) / size
              for g in np.mgrid[0:H, 0:W])
    # which provinces touch (sea-sea only)
    nbrs = defaultdict(Counter)
    for a, b in ((plab[:, :-1], plab[:, 1:]), (plab[:-1], plab[1:]), (plab[:, -1], plab[:, 0])):
        d = (a != b) & is_sea[a] & is_sea[b]
        for u, v in zip(a[d].tolist(), b[d].tolist()):
            nbrs[u][v] += 1
            nbrs[v][u] += 1
    seas = np.nonzero(is_sea)[0]
    # bucket by a coarse grid, then split buckets into connected pieces
    bucket = {int(p): (int(cy[p] // (cell / 2)), int(cx[p] // cell)) for p in seas}
    region = {}
    groups = []
    for p in seas:
        p = int(p)
        if p in region:
            continue
        stack, g = [p], []
        region[p] = len(groups)
        while stack:
            u = stack.pop()
            g.append(u)
            for v in nbrs[u]:
                if v not in region and bucket[v] == bucket[p]:
                    region[v] = len(groups)
                    stack.append(v)
        groups.append(g)
    # small pieces join the neighbouring piece they share most coast with
    area = [sum(size[u] for u in g) for g in groups]
    for k in sorted(range(len(groups)), key=lambda k: area[k]):
        if area[k] >= cell * cell / 8 or not groups[k]:
            continue
        border = Counter()
        for u in groups[k]:
            for v, c in nbrs[u].items():
                if region[v] != k:
                    border[region[v]] += c
        if border:
            t = border.most_common(1)[0][0]
            for u in groups[k]:
                region[u] = t
            groups[t] += groups[k]
            area[t] += area[k]
            groups[k], area[k] = [], 0
    live = [k for k in range(len(groups)) if groups[k]]
    blues = palette(len(live), True, 11)
    newcol = np.zeros(n, np.int64)
    for k, c in zip(live, blues):
        newcol[groups[k]] = c
    # land regions: same regions, new non-blue colours
    land_cols = np.unique(R[~sea])
    reds = palette(len(land_cols), False, 12, set(blues))
    remap = dict(zip(land_cols.tolist(), reds))
    out = np.where(sea, newcol[plab], 0)
    lv = np.vectorize(remap.get, otypes=[np.int64])(R[~sea])
    out[~sea] = lv
    put(L["Strategic Regions"], out, np.ones((H, W), bool))
    print(f"{len(live)} sea regions (were {len(np.unique(R[sea]))}), {len(land_cols)} land regions recoloured")


def give(names, L, country, seeds):
    from common import COUNTRIES
    St = code(L["States"][..., :3])
    painted = L["States"][..., 3] > 0
    for x, y in seeds:
        m = painted & (St == St[y, x])
        L["Countries"][m, :3] = COUNTRIES[country][3]
        L["Countries"][m, 3] = 255
        print(f"state at ({x}, {y}): {m.sum()} px -> {country}")


def attach(names, L, country, seeds, reach=300):
    from common import COUNTRIES
    t = L["Terrain"][..., :3]
    land = ~((t == OCEAN).all(-1) | (t == LAKES).all(-1))
    col = code(np.array(COUNTRIES[country][3]))
    for x, y in seeds:
        St = np.where(L["States"][..., 3] > 0, code(L["States"][..., :3]), -1)
        m = land & (St == St[y, x])
        ys, xs = np.nonzero(m)
        y0, y1 = max(ys.min() - reach, 0), min(ys.max() + reach + 1, H)
        x0, x1 = max(xs.min() - reach, 0), min(xs.max() + reach + 1, W)
        win = np.s_[y0:y1, x0:x1]
        theirs = land[win] & (code(L["Countries"][win][..., :3]) == col) & ~m[win] & (St[win] >= 0)
        if not theirs.any():
            sys.exit(f"attach: no state of {country} within {reach} px of ({x}, {y})")
        dist, (iy, ix) = ndi.distance_transform_edt(~theirs, return_indices=True)
        k = np.argmin(np.where(m[win], dist, np.inf))
        ny, nx = iy.flat[k] + y0, ix.flat[k] + x0  # the nearest pixel of COUNTRY's
        to = St[ny, nx]
        L["States"][m, :3] = [(to >> 16) & 255, (to >> 8) & 255, to & 255]
        L["Strategic Regions"][m, :3] = L["Strategic Regions"][ny, nx, :3]
        L["Countries"][m, :3] = COUNTRIES[country][3]
        L["Countries"][m, 3] = 255
        print(f"state at ({x}, {y}): {m.sum()} px -> {country}, joining its state at ({nx}, {ny}), "
              f"{dist.flat[k]:.0f} px away")


def add_land(names, L, country, layer="Islands to Add"):
    """Water under the opaque pixels of LAYER becomes land of COUNTRY (2026-10-13: the
    author painted two islands on a layer of their own). Each 4-connected island is a
    province; together they are one new state. Terrain is plains; height, continent and
    strategic region are the nearest land's. The sea provinces they were in must stay
    in one piece."""
    from common import COUNTRIES
    from skimage.measure import label as sklabel
    t = L["Terrain"][..., :3]
    water = (t == OCEAN).all(-1) | (t == LAKES).all(-1)
    new = (L[layer][..., 3] > 0) & water
    if not new.any():
        sys.exit(f"add_land: no water under the {layer!r} layer")
    isl = sklabel(new, connectivity=1)
    sizes = np.bincount(isl.ravel())[1:]
    if sizes.min() < MIN_PROVINCE:
        sys.exit(f"add_land: an island of {sizes.min()} px is under {MIN_PROVINCE} px (a province's least)")
    P = code(L["Provinces"][..., :3])
    sea_before = {int(c) for c in np.unique(P[new])}
    dist, (iy, ix) = ndi.distance_transform_edt(water, return_indices=True)
    ys, xs = np.nonzero(new)
    ny, nx = iy[ys, xs], ix[ys, xs]  # each new pixel's nearest land
    L["Terrain"][new] = (86, 124, 27, 255)  # plains, as on the rest of the land
    hm = L["Heightmap"][ny, nx, 0]
    L["Heightmap"][ys, xs, :3] = np.maximum(hm, 98)[:, None]
    L["Heightmap"][ys, xs, 3] = 255
    for nm in ("Continents", "Strategic Regions"):
        L[nm][ys, xs, :3] = L[nm][ny, nx, :3]
        L[nm][ys, xs, 3] = 255
    pcols = palette(len(sizes), False, 1013, used=np.unique(P).tolist())
    for k, c in enumerate(pcols, 1):
        m = isl == k
        put(L["Provinces"], np.full((H, W), c), m)
        L["Provinces"][m, 3] = 255
    S = code(L["States"][..., :3])
    sc = palette(1, False, 1014, used=np.unique(S[L["States"][..., 3] > 0]).tolist())[0]
    put(L["States"], np.full((H, W), sc), new)
    L["States"][new, 3] = 255
    L["Countries"][new, :3] = COUNTRIES[country][3]
    L["Countries"][new, 3] = 255
    P = code(L["Provinces"][..., :3])
    for c in sorted(sea_before):  # still one piece each?
        n = sklabel(P == c, connectivity=1).max()
        if n != 1:
            sys.exit(f"add_land: sea province {c:06x} would be cut into {n} pieces")
    print(f"{len(sizes)} islands ({', '.join(f'{s} px' for s in sizes)}) -> one new state of {country}, "
          f"at ({xs[0]}, {ys[0]}); continent and region of the land at ({nx[0]}, {ny[0]})")


def border(names, L, country, seeds):
    from common import COUNTRIES
    from skimage.measure import label as sklabel
    t = L["Terrain"][..., :3]
    land = ~((t == (8, 31, 130)).all(-1) | (t == (55, 90, 220)).all(-1))
    lines = L["Necessary Borders"][..., 3] > 0
    cells = sklabel(land & ~lines, connectivity=1)
    idx = ndi.distance_transform_edt(cells == 0, return_distances=False, return_indices=True)
    cells = np.where(land & (cells == 0), cells[idx[0], idx[1]], cells)
    for x, y in seeds:
        m = cells == cells[y, x]
        moved = m & (code(L["Countries"][..., :3]) != code(np.array(COUNTRIES[country][3])))
        L["Countries"][m, :3] = COUNTRIES[country][3]
        L["Countries"][m, 3] = 255
        print(f"area at ({x}, {y}): {m.sum()} px, {moved.sum()} of them newly {country}")


def cede(names, L, frm, to, seeds):
    from common import COUNTRIES
    lines = L["Necessary Borders"][..., 3] > 0
    mine = code(L["Countries"][..., :3]) == code(np.array(COUNTRIES[frm][3]))
    lab, _ = ndi.label(mine & ~lines, CROSS)
    gone = np.isin(lab, [lab[y, x] for x, y in seeds if lab[y, x]]) & (lab > 0)
    stay = mine & ~lines & ~gone
    print(f"{frm}: {gone.sum()} px cut off, {stay.sum()} px stay (line pixels follow their province)")
    P = code(L["Provinces"][..., :3])
    side = np.zeros(P.shape, np.int8)  # 1 ceded, 2 kept, for every pixel of FROM
    for pc in np.unique(P[mine]):
        m = P == pc
        if not (m & stay).any():
            side[m] = 1
        elif not (m & gone).any():
            side[m] = 2
        else:  # line pixels take the side of the nearest pixel of the same province
            known = np.where(m & gone, 1, np.where(m & stay, 2, 0))
            idx = ndi.distance_transform_edt(known == 0, return_distances=False, return_indices=True)
            side[m] = known[idx[0], idx[1]][m]
    fresh = iter(palette(256, False, seeds[0][0] * 7919 + seeds[0][1], set(np.unique(P).tolist())))
    for pc in np.unique(P[mine]):
        m = P == pc
        if len(np.unique(side[m])) < 2:
            continue
        for sd in (1, 2):
            piece = m & (side == sd)
            ring = ndi.binary_dilation(piece, CROSS) & ~m & (side == sd)
            if piece.sum() < 40 and ring.any():
                to_p = Counter(P[ring].tolist()).most_common(1)[0][0]
                P[piece] = to_p
                print(f"province {pc:06x}: its {piece.sum()} px {'ceded' if sd == 1 else 'kept'} piece joins {to_p:06x}")
            elif sd == 1:
                P[piece] = next(fresh)
                print(f"province {pc:06x}: split along the line, {piece.sum()} px ceded as a new province")
    put(L["Provinces"], P, mine)
    moved = side == 1
    L["Countries"][moved, :3] = COUNTRIES[to][3]
    St = code(L["States"][..., :3])
    R = code(L["Strategic Regions"][..., :3])
    whole = {sc for sc in np.unique(St[moved]).tolist() if not ((St == sc) & (side == 2)).any()}
    split = [sc for sc in np.unique(St[moved]).tolist() if sc not in whole]
    new_states = iter(palette(64, False, seeds[0][1] * 7919 + seeds[0][0], set(np.unique(St).tolist())))
    for sc in list(split):  # 2026-10-09: West Sminishia's half of a state was not a sliver
        part = (St == sc) & moved
        if part.sum() >= CEDED_STATE:
            St[part] = new = next(new_states)
            whole.add(new)
            split.remove(sc)
            print(f"state {sc:06x}: its {part.sum()} px ceded become a state of their own")
    while split:  # a split state's ceded part joins a neighbouring state that moved whole
        for sc in split:
            part = (St == sc) & moved
            ring = ndi.binary_dilation(part, CROSS) & ~part & moved
            nb = Counter(v for v in St[ring].tolist() if v in whole)
            if nb:
                to_s = nb.most_common(1)[0][0]
                R[part] = Counter(R[St == to_s].tolist()).most_common(1)[0][0]
                St[part] = to_s
                print(f"state {sc:06x}: its {part.sum()} px ceded join state {to_s:06x}")
                split.remove(sc)
                break
        else:  # none touches a state that moved whole: the biggest part becomes a state
            sc = max(split, key=lambda s: ((St == s) & moved).sum())
            part = (St == sc) & moved
            St[part] = new = next(new_states)
            whole.add(new)
            split.remove(sc)
            print(f"state {sc:06x}: its {part.sum()} px ceded become a state of their own")
    put(L["States"], St, moved)
    put(L["Strategic Regions"], R, moved)
    print(f"{moved.sum()} px -> {to}; states that moved whole: {len(whole)}")


OWNERS_KEEP = []  # (x, y) pixels in areas whose two nations stay as they are (none known: the 2026-10-17 map has none)


def owners(names, L, given, apply):
    """the `owners` command; returns whether anything was changed"""
    from common import COUNTRIES
    key_of = {**{v[0]: k for k, v in COUNTRIES.items()}, **{k: k for k in COUNTRIES}}
    col = {k: code(np.array(v[3])) for k, v in COUNTRIES.items()}
    key_of_code = {c: k for k, c in col.items()}
    t = L["Terrain"][..., :3]
    land = ~((t == OCEAN).all(-1) | (t == LAKES).all(-1))
    lines = L["Necessary Borders"][..., 3] > 0
    cells, _ = ndi.label(land & ~lines, CROSS)
    K = code(L["Countries"][..., :3])
    St = code(L["States"][..., :3])
    keep = {int(cells[y, x]) for x, y in OWNERS_KEEP}
    # strokes: each blob's two farthest points; an end in a mixed area, the other in the owner's land
    strokes = []
    if "Necessary Owners" in L:
        bl, n = ndi.label(L["Necessary Owners"][..., 3] > 0, np.ones((3, 3)))
        for i, sl in enumerate(ndi.find_objects(bl), 1):
            ys, xs = np.nonzero(bl[sl] == i)
            ys, xs = ys + sl[0].start, xs + sl[1].start
            a = int(np.argmin(xs + ys)); d = (xs - xs[a]) ** 2 + (ys - ys[a]) ** 2; b = int(np.argmax(d))
            d2 = (xs - xs[b]) ** 2 + (ys - ys[b]) ** 2; a = int(np.argmax(d2))
            strokes.append(((int(xs[a]), int(ys[a])), (int(xs[b]), int(ys[b]))))
    plan = {}  # cell -> (owner key, why)
    for (x, y), country in given:
        c = int(cells[y, x])
        if c == 0:
            raise SystemExit(f"({x}, {y}) is on a line or at sea: give a pixel inside the area")
        plan[c] = (key_of[country], f"given at ({x}, {y})")
    mixed = {}
    for c, sl in enumerate(ndi.find_objects(cells), 1):
        if sl is None or c in keep:
            continue
        m = cells[sl] == c
        n = int(m.sum())
        if n < 50:
            continue
        share = Counter(K[sl][m].tolist()).most_common()
        share = [(k, v) for k, v in share if k in key_of_code]
        if len(share) > 1 and share[1][1] >= max(100, 0.03 * n):
            mixed[c] = share
    for c, share in mixed.items():
        if c in plan:
            continue
        for p, q in strokes:
            for s0, s1 in ((p, q), (q, p)):
                if int(cells[s0[1], s0[0]]) == c and int(cells[s1[1], s1[0]]) != c and K[s1[1], s1[0]] in key_of_code:
                    plan[c] = (key_of_code[K[s1[1], s1[0]]], f"a stroke from ({s0[0]}, {s0[1]}) to ({s1[0]}, {s1[1]})")
        if c not in plan:
            plan[c] = (key_of_code[share[0][0]], "most of it")
    if not plan:
        print("no area inside the country lines holds two nations: nothing to settle")
        return False
    tag = {k: v[0] for k, v in COUNTRIES.items()}
    for c, (owner, why) in plan.items():
        m = cells == c
        ys, xs = np.nonzero(m)
        share = Counter(K[m].tolist()).most_common()
        print(f"area at ({xs[len(xs) // 2]}, {ys[len(ys) // 2]}), {int(m.sum())} px -> {tag[owner]} ({why}): "
              + ", ".join(f"{tag.get(key_of_code.get(k), f'#{k:06x}')} {v}" for k, v in share[:5]))
    if not apply:
        print("(a plan only: --apply to make it)")
        return False
    for c, (owner, why) in plan.items():
        m = cells == c
        for k, v in Counter(K[m].tolist()).most_common():
            frm = key_of_code.get(k)
            if frm is None or frm == owner:
                continue
            theirs = (K == k) & m
            states = np.unique(St[theirs])
            whole = all(not ((St == s) & (K == k) & land & ~lines & ~m).any() for s in states.tolist())
            if whole:  # its states lie inside the area: they change hands as they are
                inside = np.isin(St, states) & (K == k)
                L["Countries"][inside, :3] = COUNTRIES[owner][3]
                print(f"  {tag[frm]}: {len(states)} whole states ({int(inside.sum())} px) -> {tag[owner]}")
            else:  # the line crosses its states: cut them along it
                comp, n = ndi.label(theirs & ~lines, CROSS)
                seeds = []
                for j, sl in enumerate(ndi.find_objects(comp), 1):
                    yy, xx = np.nonzero(comp[sl] == j)
                    seeds.append((int(xx[len(xx) // 2] + sl[1].start), int(yy[len(yy) // 2] + sl[0].start)))
                print(f"  {tag[frm]}: cut along the line ({len(seeds)} pieces)")
                cede(names, L, frm, owner, seeds)
                K = code(L["Countries"][..., :3])
                St = code(L["States"][..., :3])
    return True


def merge_small(names, L, country, min_px):
    from common import COUNTRIES
    t = L["Terrain"][..., :3]
    land = ~((t == (8, 31, 130)).all(-1) | (t == (55, 90, 220)).all(-1))
    mine = land & (code(L["Countries"][..., :3]) == code(np.array(COUNTRIES[country][3])))
    while True:
        St = np.where(L["States"][..., 3] > 0, code(L["States"][..., :3]), -1)
        sizes = Counter(St[mine].tolist())
        small = [s for s, n in sizes.items() if n < min_px and s >= 0]
        done = False
        for sc in sorted(small, key=lambda s: sizes[s]):
            m = (St == sc) & land
            ring = ndi.binary_dilation(m, CROSS) & ~m & mine
            nb = Counter(v for v in St[ring].tolist() if v >= 0 and v != sc)
            if not nb:
                continue
            to = nb.most_common(1)[0][0]
            ys, xs = np.nonzero(m)
            print(f"state at ({int(xs.mean())}, {int(ys.mean())}), {m.sum()} px -> its neighbour")
            L["States"][m, :3] = [(to >> 16) & 255, (to >> 8) & 255, to & 255]
            done = True
            break
        if not done:
            return


def recut(names, L, seeds, keep_states=False):
    from apply_outlines import Colours, organic_split, STATE_MAX, STATE_AREA, PROVINCE_AREA, MIN_LEFTOVER
    from skimage.measure import label as sklabel
    t = L["Terrain"][..., :3]
    land = ~((t == OCEAN).all(-1) | (t == LAKES).all(-1))
    lines = np.zeros((H, W), bool)
    for nm in ("Necessary Borders", "Borders", "Necessary States"):
        if nm in L:
            lines |= L[nm][..., 3] > 0
    K = code(L["Countries"][..., :3])
    P = code(L["Provinces"][..., :3])
    S = np.where(L["States"][..., 3] > 0, code(L["States"][..., :3]), -1)
    R = code(L["Strategic Regions"][..., :3])
    pcols, scols = Colours(P, 1015), Colours(S[S >= 0], 1016)
    for n, (x, y) in enumerate(seeds):
        if not land[y, x] or lines[y, x]:
            sys.exit(f"recut: ({x}, {y}) is not land off the lines")
        mine = land & (K == K[y, x])
        cells = sklabel(mine & ~lines, connectivity=1)
        me = cells[y, x]
        ys, xs = np.nonzero(cells == me)
        win = np.s_[max(ys.min() - 40, 0):min(ys.max() + 41, H), max(xs.min() - 40, 0):min(xs.max() + 41, W)]
        wc = cells[win]
        M = wc == me
        wl = lines[win] & mine[win]
        if wl.any():  # the country's line pixels go to the nearest piece
            iy, ix = ndi.distance_transform_edt(wc == 0, return_distances=False, return_indices=True)
            M |= wl & (wc[iy, ix] == me)
        wP, wS, wR = P[win], S[win], R[win]  # views: edits land in P, S, R
        old_p = set(np.unique(wP[M]).tolist())
        yy, xx = np.nonzero(M)
        if keep_states:
            groups = [(sc, M & (wS == sc)) for sc in sorted(set(np.unique(wS[M]).tolist()))]
        else:
            k = max(1, round(len(yy) / STATE_AREA)) if len(yy) > STATE_MAX else 1
            st = organic_split(yy, xx, k, seed=1000 + n)
            groups = []
            for j in range(k):
                g = np.zeros(M.shape, bool)
                g[yy[st == j], xx[st == j]] = True
                if g.any():
                    groups.append((scols.new(), g))
        nprov = 0
        for sc, g in groups:
            comp = sklabel(g, connectivity=1)  # each island of a state gets provinces of its own
            for q in range(1, comp.max() + 1):
                cy, cx = np.nonzero(comp == q)
                kp = min(max(1, round(len(cy) / PROVINCE_AREA)), len(cy) // MIN_PROVINCE or 1)
                parts = organic_split(cy, cx, kp, seed=2000 + 97 * n + q)
                for j in range(kp):
                    if (parts == j).any():
                        wP[cy[parts == j], cx[parts == j]] = pcols.new()
                        nprov += 1
            if not keep_states:
                wS[g] = sc
                wR[g] = Counter(wR[g].tolist()).most_common(1)[0][0]
        # what is left of a province cut here beyond the lines: a big piece stays a province,
        # scraps join the neighbour they share most border with
        for c in old_p:
            comp = sklabel((wP == c) & ~M, connectivity=1)
            if not comp.max():
                continue
            sizes = np.bincount(comp.ravel())[1:]
            for q in np.argsort(-sizes) + 1:
                pm = comp == q
                if sizes[q - 1] >= MIN_LEFTOVER:
                    if q != np.argmax(sizes) + 1:
                        wP[pm] = pcols.new()
                    continue
                ring = ndi.binary_dilation(pm, CROSS) & ~pm & land[win]
                nb = Counter(v for v in zip(wP[ring].tolist(), wS[ring].tolist()) if v[0] != c)
                same = {v: k_ for v, k_ in nb.items() if v[1] == wS[pm][0]}
                if nb:
                    wP[pm] = max(same or nb, key=(same or nb).get)[0]
        for nm, arr in (("Provinces", wP), ("States", wS), ("Strategic Regions", wR)):
            put(L[nm][win], arr, M)
            L[nm][win][M, 3] = 255
        put(L["Provinces"][win], wP, land[win] & ~M & np.isin(wP, list(old_p), invert=True) & (code(L["Provinces"][win][..., :3]) != wP))
        print(f"({x}, {y}): {M.sum()} px of {len(old_p)} provinces -> {len(groups)} state(s){' (kept)' if keep_states else ''}, "
              f"{nprov} provinces")


def provinces(names, L):
    from skimage.measure import label as sklabel
    t = L["Terrain"][..., :3]
    land = ~((t == OCEAN).all(-1) | (t == LAKES).all(-1))
    lines = (L["Necessary Provinces"][..., 3] > 0) & land
    # the state and border lines divide too: their pixels belong to a state, and would join its pieces round a
    # province line's end (2026-10-17, Royalist Illiricium's southern island)
    every = lines | (((L["Necessary States"][..., 3] > 0) | (L["Necessary Borders"][..., 3] > 0)) & land)
    P = code(L["Provinces"][..., :3])
    St = np.where(L["States"][..., 3] > 0, code(L["States"][..., :3]), -1)
    fresh = iter(palette(1024, False, 20261017, set(np.unique(P).tolist())))
    for sc in sorted(set(np.unique(St[lines]).tolist()) - {-1}):
        ys, xs = np.nonzero(St == sc)
        sl = np.s_[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        m = (St[sl] == sc) & land[sl]
        cells = sklabel(m & ~every[sl], connectivity=1)
        sizes = np.bincount(cells.ravel())[1:]
        big = [q + 1 for q in np.argsort(-sizes) if sizes[q] >= MIN_PROVINCE]
        if len(big) < 2:
            print(f"state {sc:06x} at ({xs[0]}, {ys[0]}): its province lines don't divide it, left as it is")
            continue
        # small pieces join the big piece they share most border with; line pixels the nearest piece
        for q in range(1, cells.max() + 1):
            if q in big:
                continue
            piece = cells == q
            ring = ndi.binary_dilation(piece, CROSS) & m & ~piece
            nb = Counter(v for v in cells[ring].tolist() if v in big)
            if nb:
                cells[piece] = nb.most_common(1)[0][0]
        iy, ix = ndi.distance_transform_edt(~np.isin(cells, big), return_distances=False, return_indices=True)
        cells = np.where(m, cells[iy, ix], 0)
        before = len(np.unique(P[sl][m]))
        new = np.zeros(m.shape, np.int64)
        for q in big:
            new[cells == q] = next(fresh)
        put(L["Provinces"][sl], new, m)
        print(f"state {sc:06x} at ({xs[0]}, {ys[0]}): {before} provinces -> {len(big)} drawn ones "
              f"({', '.join(str(int((cells == q).sum())) for q in big)} px)")


def tidy(names, L):
    t = L["Terrain"][..., :3]
    land = ~((t == OCEAN).all(-1) | (t == LAKES).all(-1))
    P = code(L["Provinces"][..., :3])
    St = np.where(L["States"][..., 3] > 0, code(L["States"][..., :3]), -1)
    u, inv, cnt = np.unique(np.where(land, P, -1), return_inverse=True, return_counts=True)
    inv = inv.reshape(P.shape)
    small = [i for i in range(len(u)) if u[i] >= 0 and cnt[i] < MIN_PROVINCE]
    boxes = ndi.find_objects(inv + 1)
    moved = 0
    for i in sorted(small, key=lambda i: cnt[i]):
        sl = boxes[i]
        sl = np.s_[max(sl[0].start - 1, 0):sl[0].stop + 1, max(sl[1].start - 1, 0):sl[1].stop + 1]
        m = (P[sl] == u[i]) & land[sl]
        if not m.any():
            continue
        ring = ndi.binary_dilation(m, CROSS) & ~m & land[sl]
        st = Counter(St[sl][m].tolist()).most_common(1)[0][0]
        nb = Counter(zip(P[sl][ring].tolist(), St[sl][ring].tolist()))
        same = {k: n for k, n in nb.items() if k[1] == st}
        if not nb:
            print(f"province {u[i]:06x} ({cnt[i]} px): no land neighbour, left as it is")
            continue
        (to_p, to_s) = max(same or nb, key=(same or nb).get)
        if to_s != st:  # a scrap of another state: it joins that state outright
            ref = (P[sl] == to_p) & land[sl]
            for nm in ("States", "Countries", "Strategic Regions"):
                L[nm][sl][m] = L[nm][sl][ref][0]
            St[sl][m] = to_s
        put(L["Provinces"][sl], np.full(m.shape, to_p, np.int64), m)
        P[sl][m] = to_p
        moved += 1
    print(f"tidy: {moved} of {len(small)} provinces under {MIN_PROVINCE} px merged into a neighbour")


def lakes(names, L):
    from skimage.measure import label as sklabel
    lake = (L["Terrain"][..., :3] == LAKES).all(-1)
    lab = sklabel(lake, connectivity=1)
    P = code(L["Provinces"][..., :3])
    R = code(L["Strategic Regions"][..., :3])
    merged = 0
    for k, sl in enumerate(ndi.find_objects(lab), 1):
        m = lab[sl] == k
        cols = Counter(P[sl][m].tolist())
        if len(cols) <= 1:
            continue
        if sl[0].stop - sl[0].start >= H // 8 or sl[1].stop - sl[1].start >= W // 8:
            print(f"lake at ({sl[1].start}, {sl[0].start}) is too big for one province (HOI4: 1/8 of the map); left")
            continue
        put(L["Provinces"][sl], np.full(m.shape, cols.most_common(1)[0][0]), m)
        put(L["Strategic Regions"][sl], np.full(m.shape, Counter(R[sl][m].tolist()).most_common(1)[0][0]), m)
        merged += len(cols) - 1
        print(f"lake at ({sl[1].start}, {sl[0].start}), {m.sum()} px: {len(cols)} provinces -> 1")
    print(f"{merged} lake provinces merged")


def blue_seas(names, L):
    P = code(L["Provinces"][..., :3])
    sea = code(L["Terrain"][..., :3]) == code(np.array(OCEAN))
    cols, lab = np.unique(P, return_inverse=True)
    lab = lab.reshape(P.shape)
    size = np.bincount(lab.ravel())
    is_sea = np.bincount(lab.ravel(), sea.ravel()) * 2 > size
    land_cols = set(cols[~is_sea].tolist())
    blues = palette(int(is_sea.sum()), True, 31, land_cols)
    new = cols.copy()
    new[np.nonzero(is_sea)[0]] = blues
    put(L["Provinces"], new[lab], is_sea[lab])
    print(f"{is_sea.sum()} sea provinces recoloured blue")


def recolour(names, L, layer, pairs):
    C = code(L[layer][..., :3])
    painted = L[layer][..., 3] > 0
    for old, new in pairs:
        m = painted & (C == code(np.array(old)))
        L[layer][m, :3] = new
        print(f"{layer}: {old} -> {new}, {m.sum()} px")


def channel(names, L, pairs):
    import heapq
    from skimage.measure import label as sklabel
    terr = code(L["Terrain"][..., :3])
    sea = terr == code(np.array(OCEAN))
    land = ~sea & (terr != code(np.array(LAKES)))
    for x1, y1, x2, y2, *mm in pairs:
        if not (sea[y1, x1] and sea[y2, x2]):
            sys.exit(f"channel {x1},{y1} {x2},{y2}: both ends must be sea")
        # the path stays within M px of the two ends' box (8 by default): a smaller M keeps it from going round an
        # islet the sea already surrounds but for a neck of land (2026-10-17: "Should be an island!")
        m = mm[0] if mm else 8
        bx0, by0 = min(x1, x2) - m, min(y1, y2) - m
        bx1, by1 = max(x1, x2) + m + 1, max(y1, y2) + m + 1
        cost = land[by0:by1, bx0:bx1].astype(int)
        start, goal = (y1 - by0, x1 - bx0), (y2 - by0, x2 - bx0)
        dist, prev, pq = {start: 0}, {}, [(0, start)]
        while pq:
            d, u = heapq.heappop(pq)
            if u == goal:
                break
            if d > dist[u]:
                continue
            for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                v = (u[0] + dy, u[1] + dx)
                if 0 <= v[0] < cost.shape[0] and 0 <= v[1] < cost.shape[1]:
                    nd = d + cost[v] * 1000 + 1  # fewest land pixels, then shortest
                    if nd < dist.get(v, 1 << 60):
                        dist[v], prev[v] = nd, u
                        heapq.heappush(pq, (nd, v))
        path, u = [], goal
        while u != start:
            path.append(u)
            u = prev[u]
        cut = np.zeros((H, W), bool)
        for py, px in path:
            if land[py + by0, px + bx0]:
                cut[py + by0, px + bx0] = True
        before = sklabel(land[by0:by1, bx0:bx1], connectivity=1).max()
        # the carved pixels join the nearest sea province and region
        P = code(L["Provinces"][..., :3])
        R = code(L["Strategic Regions"][..., :3])
        sl = np.s_[by0 - 20:by1 + 20, bx0 - 20:bx1 + 20]
        idx = ndi.distance_transform_edt(~sea[sl], return_distances=False, return_indices=True)
        c = cut[sl]
        for nm, val in (("Provinces", P[sl][idx[0], idx[1]]), ("Strategic Regions", R[sl][idx[0], idx[1]])):
            arr = L[nm][sl]
            arr[c, 0], arr[c, 1], arr[c, 2] = val[c] >> 16, (val[c] >> 8) & 255, val[c] & 255
        L["Terrain"][cut, :3] = OCEAN
        L["Heightmap"][cut, :3] = 93
        for nm in ("Continents", "States", "Countries", "Rivers"):
            L[nm][cut, 3] = 0
        sea |= cut
        land &= ~cut
        # land provinces cut apart: pieces of 16+ px become provinces, scraps join a neighbour
        P = code(L["Provinces"][..., :3])
        used = set(np.unique(P).tolist())
        rng = np.random.default_rng(x1 * 7 + y1)
        for pc in set(np.unique(P[ndi.binary_dilation(cut, CROSS) & land]).tolist()):
            comp = sklabel((P == pc) & land, connectivity=1)
            sizes = np.bincount(comp.ravel())[1:]
            for j in np.argsort(-sizes)[1:] + 1:
                piece = comp == j
                if sizes[j - 1] >= 16:
                    while True:
                        nc = int(rng.integers(1 << 20, 1 << 24))
                        if nc not in used:
                            used.add(nc)
                            break
                else:
                    ring = ndi.binary_dilation(piece, CROSS) & land & ~piece
                    nc = Counter(P[ring].tolist()).most_common(1)[0][0]
                L["Provinces"][piece, :3] = [nc >> 16, (nc >> 8) & 255, nc & 255]
                P[piece] = nc
        after = sklabel(land[by0:by1, bx0:bx1], connectivity=1).max()
        print(f"channel {x1},{y1} -> {x2},{y2}: {cut.sum()} land px became sea; "
              f"landmasses nearby {before} -> {after}")


def main():
    cmd = sys.argv[1]
    names, L = load()
    if cmd == "navigable":
        navigable(names, L, [tuple(int(v) for v in a.split(",")) for a in sys.argv[2:]])
    elif cmd == "recolour":
        pairs = [tuple(tuple(int(v) for v in side.split(",")) for side in a.split("="))
                 for a in sys.argv[3:]]
        recolour(names, L, sys.argv[2], pairs)
    elif cmd == "give":
        give(names, L, sys.argv[2], [tuple(int(v) for v in a.split(",")) for a in sys.argv[3:]])
    elif cmd == "attach":
        attach(names, L, sys.argv[2], [tuple(int(v) for v in a.split(",")) for a in sys.argv[3:]])
    elif cmd == "add_land":
        add_land(names, L, sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "Islands to Add")
    elif cmd == "border":
        border(names, L, sys.argv[2], [tuple(int(v) for v in a.split(",")) for a in sys.argv[3:]])
    elif cmd == "cede":
        cede(names, L, sys.argv[2], sys.argv[3], [tuple(int(v) for v in a.split(",")) for a in sys.argv[4:]])
    elif cmd == "owners":
        given = []
        for a in sys.argv[2:]:
            if a == "--apply":
                continue
            xy, country = a.split("=")
            given.append((tuple(int(v) for v in xy.split(",")), country))
        if not owners(names, L, given, "--apply" in sys.argv):
            return
    elif cmd == "merge_small":
        merge_small(names, L, sys.argv[2], int(sys.argv[3]))
    elif cmd == "recut":
        keep = "--keep-states" in sys.argv
        recut(names, L, [tuple(int(v) for v in a.split(",")) for a in sys.argv[2:] if a != "--keep-states"], keep)
    elif cmd == "lakes":
        lakes(names, L)
    elif cmd == "blue_seas":
        blue_seas(names, L)
    elif cmd == "provinces":
        provinces(names, L)
    elif cmd == "tidy":
        tidy(names, L)
    elif cmd == "channel":
        channel(names, L, [tuple(int(v) for v in a.split(",")) for a in sys.argv[2:]])
    elif cmd == "sea_zones":
        if "Ocean Province Lines" in L:
            sys.exit("the sea regions are Merlo's now (scripts/sea_provinces.py): not regrouped")
        sea_zones(names, L, int(sys.argv[2]) if len(sys.argv) > 2 else 1536)
    else:
        sys.exit(__doc__)
    save(names, L)


if __name__ == "__main__":
    main()
