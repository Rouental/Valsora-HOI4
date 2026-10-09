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
    python3 scripts/pdn_tools.py merge_small COUNTRY MIN_PX
        Merge COUNTRY's states smaller than MIN_PX into the neighbouring state of the same
        country they share most border with (States layer), e.g. the slivers a moved
        border leaves behind. Provinces stay as they are.
    python3 scripts/pdn_tools.py blue_seas
        Recolour every sea province on the Provinces layer in its own blue (the author
        wants the sea easy to tell from land there). Colours only: nothing else changes.
    python3 scripts/pdn_tools.py channel X1,Y1,X2,Y2 [...]
        Reopen a strait that closed when the world was scaled down: the cheapest
        4-connected path from the water at (X1, Y1) to the water at (X2, Y2), counting
        land pixels, becomes sea in the nearest sea province and region. Land provinces it
        cuts apart are split (pieces of 16+ px) or merged into a neighbour.
    python3 scripts/pdn_tools.py sea_zones [CELL]
        Regroup all sea provinces into larger sea regions (about CELL px across, default
        1536), and recolour the Strategic Regions layer so sea regions are blues and land
        regions never are.

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

from common import MAP_W as W, MAP_H as H
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
    for x1, y1, x2, y2 in pairs:
        if not (sea[y1, x1] and sea[y2, x2]):
            sys.exit(f"channel {x1},{y1} {x2},{y2}: both ends must be sea")
        m = 8
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
    elif cmd == "border":
        border(names, L, sys.argv[2], [tuple(int(v) for v in a.split(",")) for a in sys.argv[3:]])
    elif cmd == "cede":
        cede(names, L, sys.argv[2], sys.argv[3], [tuple(int(v) for v in a.split(",")) for a in sys.argv[4:]])
    elif cmd == "merge_small":
        merge_small(names, L, sys.argv[2], int(sys.argv[3]))
    elif cmd == "blue_seas":
        blue_seas(names, L)
    elif cmd == "channel":
        channel(names, L, [tuple(int(v) for v in a.split(",")) for a in sys.argv[2:]])
    elif cmd == "sea_zones":
        sea_zones(names, L, int(sys.argv[2]) if len(sys.argv) > 2 else 1536)
    else:
        sys.exit(__doc__)
    save(names, L)


if __name__ == "__main__":
    main()
