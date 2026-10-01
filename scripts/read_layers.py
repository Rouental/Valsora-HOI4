"""Turn the layers of "source/HOI4 Mod Map.pdn" into the data build_mod.py writes out.

The .pdn is decoded to work/pdn_game first (readpdn.py). Layers are found by name:

    Heightmap          grey = height; water must be below 95, land above (auto-clamped)
    Terrain            HOI4's terrain palette; ocean colour = sea, lakes colour = lake,
                       every other colour = land of that terrain type
    Rivers             transparent = no river; HOI4's river palette colours
    Continents         one colour per continent (common.CONT_COLOURS)
    Provinces          one colour per province, like provinces.bmp
    Strategic Regions  one colour per strategic region
    States             one colour per state, on land
    Countries          one colour per country (common.COUNTRIES); owns the states it covers

Everything a province, state or region gets is decided by the majority of its pixels.
Problems are printed as a numbered list with (x, y) pixel coordinates, the same numbers
paint.net shows in its status bar, and the build stops.

Writes work/world.npz, work/provinces.npz, work/regions.npz and work/regions.json in
the same formats as the placeholder pipeline, plus the author's colours and owners.
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi
from skimage.measure import label as sklabel

from common import (MAP_W, MAP_H, CONT_COLOURS, COUNTRIES, TERRAIN_TYPES,
                    TERRAIN_OCEAN, TERRAIN_LAKE, MAX_BOX)
from imgio import palette_from_header
from provinces import adjacency, crossings, repair
import rivers as river_lines
from regions import anchors

W, H = MAP_W, MAP_H
SRC = Path(sys.argv[1] if len(sys.argv) > 1 else "work/pdn_game")
LAYERS = ["Heightmap", "Terrain", "Rivers", "Continents", "Provinces", "Strategic Regions",
          "States", "Countries"]
# rivers drawn as plain lines, converted by rivers.py
OPTIONAL = ["Major Rivers", "Minor Rivers"]
# the author's layer names (2026-10-01: their editing layers are "Necessary …"); the
# older names still work
ALIASES = {"Major Rivers": "Necessary Major Rivers", "Minor Rivers": "Necessary Minor Rivers"}
MIN_PIXELS = 8

errors, notes = [], []


def where(ys, xs, limit=3):
    pts = sorted(zip(xs.tolist(), ys.tolist()))[:limit]
    return ", ".join(f"({x}, {y})" for x, y in pts)


def load():
    names = (SRC / "layers.txt").read_text().splitlines()
    out = {}
    for want in LAYERS:
        if want not in names:
            sys.exit(f'The .pdn has no layer named "{want}". Layers found: {names}')
        out[want] = np.load(SRC / f"layer{names.index(want)}.npy")
    for opt in OPTIONAL:
        for nm in (ALIASES.get(opt), opt):
            if nm in names:
                out[opt] = np.load(SRC / f"layer{names.index(nm)}.npy")
                break
    if out["Provinces"].shape[:2] != (H, W):
        sys.exit(f"The .pdn must be {W}x{H} pixels.")
    return out


def rgb_code(a):
    a = a.astype(np.int64)
    return (a[..., 0] << 16) | (a[..., 1] << 8) | a[..., 2]


def to_palette(layer, palette, allowed, what):
    """Map colours to palette indices; off-palette colours snap to the nearest allowed one."""
    code = rgb_code(layer[..., :3])
    idx = np.full(code.shape, -1, np.int32)
    for i in allowed:
        idx[code == ((int(palette[i][0]) << 16) | (int(palette[i][1]) << 8) | int(palette[i][2]))] = i
    off = (idx < 0) & (layer[..., 3] > 0)
    if off.any():
        cols, inv = np.unique(code[off], return_inverse=True)
        pal = np.array([palette[i] for i in allowed], float)
        rgb = np.stack([cols >> 16, (cols >> 8) & 255, cols & 255], 1)
        near = np.array(allowed)[np.argmin(((rgb[:, None] - pal[None]) ** 2).sum(-1), 1)]
        idx[off] = near[inv]
        ys, xs = np.nonzero(off)
        notes.append(f"{what}: {off.sum()} pixels are not one of the palette colours and were "
                     f"read as the nearest one, e.g. at {where(ys, xs)}")
    return idx


def majority(values, lab, n, ignore=-1):
    """Most common value per label (ignoring `ignore`); -1 where a label has none."""
    v, l = values.ravel(), lab.ravel()
    keep = v != ignore
    vals, vi = np.unique(v[keep], return_inverse=True)
    if len(vals) == 0:
        return np.full(n, -1, np.int64)
    counts = np.bincount(l[keep].astype(np.int64) * len(vals) + vi,
                         minlength=n * len(vals)).reshape(n, len(vals))
    return np.where(counts.max(1) > 0, vals[counts.argmax(1)], -1).astype(np.int64)


def fill_blanks(code, lab, n, ids, valid, layer):
    """Majority colour per province; provinces in `ids` with no colour at all take the
    nearest painted pixel where `valid` is true, with a note saying where."""
    of = majority(code, lab, n)
    blank = [i for i in ids if of[i] < 0]
    if blank:
        src = valid & (code >= 0)
        if not src.any():
            return of
        idx = ndi.distance_transform_edt(~src, return_distances=False, return_indices=True)
        near = majority(code[idx[0], idx[1]], lab, n)
        for i in blank:
            of[i] = near[i]
        ys, xs = np.nonzero(lab == blank[0])
        notes.append(f"{layer}: {len(blank)} provinces were left blank and joined the nearest "
                     f"painted area, e.g. at {where(ys, xs, 1)}")
    return of


def main():
    L = load()

    # ---------------------------------------------------------------- terrain -> kind
    tpal = palette_from_header("source/palettes/terrain.bmp.header.bin")
    terr = to_palette(L["Terrain"], tpal, sorted(TERRAIN_TYPES), "Terrain")
    if (L["Terrain"][..., 3] == 0).any():
        ys, xs = np.nonzero(L["Terrain"][..., 3] == 0)
        errors.append(f"Terrain has transparent pixels (it must cover the whole map), "
                      f"e.g. at {where(ys, xs)}")
        terr[terr < 0] = TERRAIN_OCEAN
    pix_kind = np.where(terr == TERRAIN_OCEAN, 0, np.where(terr == TERRAIN_LAKE, 2, 1))

    # ---------------------------------------------------------------- provinces
    P = L["Provinces"]
    if (P[..., 3] < 255).any():
        ys, xs = np.nonzero(P[..., 3] < 255)
        errors.append(f"Provinces has transparent or see-through pixels, e.g. at {where(ys, xs)}")
    code = rgb_code(P[..., :3])
    if (code == 0).any():
        ys, xs = np.nonzero(code == 0)
        errors.append(f"Provinces uses pure black (0,0,0), which HOI4 reserves, e.g. at {where(ys, xs)}")
    colours, pcol = np.unique(code, return_inverse=True)
    pcol = pcol.reshape(H, W)
    # number provinces by where each colour first appears, reading left to right, top down
    first = np.full(len(colours), H * W)
    np.minimum.at(first, pcol.ravel(), np.arange(H * W))
    order = np.argsort(first)
    rank = np.empty_like(order)
    rank[order] = np.arange(len(order))
    lab = rank[pcol].astype(np.int32)
    colours = colours[order]
    n = len(colours)
    pieces = sklabel(lab, background=-1, connectivity=1) - 1
    per = np.bincount(lab.ravel(), minlength=n)
    counts = np.zeros(n, int)
    first_px = np.unique(pieces.ravel(), return_index=True)[1]  # one pixel per piece
    np.add.at(counts, lab.ravel()[first_px], 1)
    for i in np.nonzero(counts > 1)[0][:20]:
        ys, xs = np.nonzero(lab == i)
        c = colours[i]
        errors.append(f"Province colour ({c >> 16},{(c >> 8) & 255},{c & 255}) is in {counts[i]} "
                      f"separate pieces (each province must be one connected area; diagonal "
                      f"touching doesn't count), e.g. at {where(ys, xs)}")
    for i in np.nonzero(per < MIN_PIXELS)[0][:20]:
        ys, xs = np.nonzero(lab == i)
        errors.append(f"A province has only {per[i]} pixels (HOI4 needs at least {MIN_PIXELS}) "
                      f"at {where(ys, xs)}")
    for i, sl in enumerate(ndi.find_objects(lab + 1)):
        if sl[0].stop - sl[0].start >= H * MAX_BOX or sl[1].stop - sl[1].start >= W * MAX_BOX:
            errors.append(f"A province is too big (over 1/8 of the map wide or tall) around "
                          f"({(sl[1].start + sl[1].stop) // 2}, {(sl[0].start + sl[0].stop) // 2})")

    # a province is land, sea or lake by the majority of its Terrain pixels
    kind = majority(pix_kind, lab, n).astype(np.uint8)
    mixed = pix_kind != kind[lab]
    if mixed.any():
        m_lab = np.unique(lab[mixed])
        ys, xs = np.nonzero(mixed)
        notes.append(f"{len(m_lab)} provinces are partly land and partly water on the Terrain "
                     f"layer; each was treated as whichever covers most of it, e.g. at {where(ys, xs)}")
    # X-crossings: four provinces at one corner. Fixed here by moving single pixels.
    xc = crossings(lab)
    if len(xc):
        cont0 = np.zeros(n, np.uint8)
        lab, fixed = repair(lab, kind, cont0, np.bincount(lab.ravel(), minlength=n))
        notes.append(f"Fixed {fixed} places where four provinces met at one corner (HOI4 "
                     f"forbids it) by moving single pixels, e.g. at "
                     f"{', '.join(f'({x}, {y})' for y, x in xc[:3])}")
    pix_kind = kind[lab]

    # ---------------------------------------------------------------- continents
    cpal = [(int(r) << 16) | (int(g) << 8) | int(b) for r, g, b in CONT_COLOURS]
    ccode = np.where(L["Continents"][..., 3] > 0, rgb_code(L["Continents"][..., :3]), -1)
    cval = np.full((H, W), -1)
    for k, c in enumerate(cpal, 1):
        cval[ccode == c] = k
    bad = (ccode >= 0) & (cval < 0)
    if bad.any():
        ys, xs = np.nonzero(bad)
        notes.append(f"Continents: {bad.sum()} pixels are not a continent colour and were "
                     f"ignored, e.g. at {where(ys, xs)}")
    cont = majority(cval, lab, n)
    land_ids = np.nonzero(kind == 1)[0]
    missing = [i for i in land_ids if cont[i] < 0]
    if missing:  # land without a continent colour takes the nearest continent
        idx = ndi.distance_transform_edt(cval < 0, return_distances=False, return_indices=True)
        near = cval[idx[0], idx[1]]
        cont2 = majority(near, lab, n)
        for i in missing:
            cont[i] = cont2[i]
    cont = np.where(kind == 1, np.maximum(cont, 0), 0).astype(np.uint8)

    # ---------------------------------------------------------------- states, countries
    scode = np.where(L["States"][..., 3] > 0, rgb_code(L["States"][..., :3]), -1)
    s_of = fill_blanks(scode, lab, n, land_ids, pix_kind == 1, "States")
    for i in land_ids:
        if s_of[i] < 0:
            ys, xs = np.nonzero(lab == i)
            errors.append(f"A land province has no state colour on the States layer, at {where(ys, xs, 1)}")
    groups = defaultdict(list)
    for i in land_ids:
        if s_of[i] >= 0:
            groups[int(s_of[i])].append(int(i))
    states = sorted(groups.values(), key=lambda g: g[0])
    state_of = np.full(n, -1)
    for s, g in enumerate(states):
        state_of[g] = s

    tagcol = {(int(c[0]) << 16) | (int(c[1]) << 8) | int(c[2]): t for t, _, _, c in COUNTRIES.values()}
    kcode = np.where(L["Countries"][..., 3] > 0, rgb_code(L["Countries"][..., :3]), -1)
    st_lab = np.where(state_of[lab] >= 0, state_of[lab], len(states))
    known = np.isin(kcode, list(tagcol))
    odd = (kcode >= 0) & ~known & (pix_kind == 1)
    if odd.any():
        ys, xs = np.nonzero(odd)
        notes.append(f"Countries: {odd.sum()} pixels are not a country colour and were ignored, "
                     f"e.g. at {where(ys, xs)}. Country colours: "
                     + ", ".join(f"{t} {tuple(col)}" for t, _, _, col in COUNTRIES.values()))
    kcode = np.where(known, kcode, -1)
    k_of = fill_blanks(kcode, st_lab, len(states) + 1, range(len(states)),
                       pix_kind == 1, "Countries")
    # states painted in more than one country colour go whole to the bigger share
    kv, ki = np.unique(kcode, return_inverse=True)
    pairs = np.bincount(st_lab.ravel().astype(np.int64) * len(kv) + ki.ravel(),
                        minlength=(len(states) + 1) * len(kv)).reshape(len(states) + 1, len(kv))
    split = np.nonzero((pairs[:-1, kv >= 0] > 0).sum(1) > 1)[0]
    if len(split):
        ys, xs = np.nonzero(lab == states[split[0]][0])
        notes.append(f"{len(split)} states are painted in more than one country colour; each "
                     f"went whole to the country covering most of it (borders follow states), "
                     f"e.g. at {where(ys, xs, 1)}")
    owners = []
    for s, g in enumerate(states):
        c = int(k_of[s])
        if c not in tagcol:
            ys, xs = np.nonzero(lab == g[0])
            what = "no country colour" if c < 0 else f"colour ({c >> 16},{(c >> 8) & 255},{c & 255}), which is no country's"
            errors.append(f"A state has {what} on the Countries layer, at {where(ys, xs, 1)}. "
                          f"Country colours: " + ", ".join(f"{t} {tuple(col)}" for t, _, _, col in COUNTRIES.values()))
            owners.append(None)
        else:
            owners.append(tagcol[c])

    # ---------------------------------------------------------------- strategic regions
    rcode = np.where(L["Strategic Regions"][..., 3] > 0, rgb_code(L["Strategic Regions"][..., :3]), -1)
    # a colour is a sea region if most of its pixels are sea; land provinces ignore sea
    # region colours and the other way round (so new land drawn at sea needs no repaint)
    rv, ri = np.unique(rcode, return_inverse=True)
    ri = ri.reshape(H, W)
    sea_share = np.bincount(ri.ravel(), weights=(pix_kind == 0).ravel(), minlength=len(rv)) / \
        np.bincount(ri.ravel(), minlength=len(rv))
    is_sea_col = (sea_share > 0.5)[ri]
    r_sea = fill_blanks(np.where(is_sea_col, rcode, -1), lab, n, np.nonzero(kind == 0)[0],
                        pix_kind == 0, "Strategic Regions")
    rc_land = np.where(is_sea_col, -1, rcode)
    r_land = majority(rc_land, lab, n)
    moved = 0
    for g in states:  # a blank land province joins the region of the rest of its state
        have = [int(r_land[i]) for i in g if r_land[i] >= 0]
        if have and len(have) < len(g):
            best = Counter(have).most_common(1)[0][0]
            for i in g:
                if r_land[i] < 0:
                    r_land[i] = best
                    moved += 1
    if moved:
        notes.append(f"Strategic Regions: {moved} land provinces had no land region colour and "
                     f"joined their state's region")
    painted = r_land >= 0
    r_land = np.where(painted, r_land, fill_blanks(rc_land, lab, n, np.nonzero((kind != 0) & ~painted)[0],
                                                     pix_kind != 0, "Strategic Regions"))
    r_of = np.where(kind == 0, r_sea, r_land)
    for i in np.nonzero(r_of < 0)[0][:20]:
        ys, xs = np.nonzero(lab == i)
        errors.append(f"A province has no colour on the Strategic Regions layer, at {where(ys, xs, 1)}")
    rgroups = defaultdict(list)
    for i in range(n):
        if r_of[i] >= 0:
            rgroups[int(r_of[i])].append(i)
    a, b, cnt = adjacency(lab, wrap=True)
    nbrs = defaultdict(set)
    for x, y in zip(a, b):
        nbrs[x].add(y)
        nbrs[y].add(x)
    regions = []
    for g in sorted(rgroups.values(), key=lambda g: (kind[g[0]] == 0, g[0])):
        ks = {int(kind[i]) for i in g}
        ys, xs = np.nonzero(lab == g[0])
        if 0 in ks and ks != {0}:
            errors.append(f"A strategic region mixes sea with land or lakes (sea and land need "
                          f"separate regions), at {where(ys, xs, 1)}")
        if ks == {2}:
            errors.append(f"A strategic region holds only lakes (a lake joins the land region "
                          f"around it), at {where(ys, xs, 1)}")
        if ks == {0}:
            seen, stack, members = set(), [g[0]], set(g)
            while stack:
                u = stack.pop()
                if u not in seen:
                    seen.add(u)
                    stack.extend(v for v in nbrs[u] if v in members)
            if seen != members:
                errors.append(f"A sea region is split into separate pieces (sea regions must be "
                              f"connected), at {where(ys, xs, 1)}")
        regions.append(dict(kind="sea" if ks == {0} else "land", provinces=sorted(int(i) for i in g),
                            colour=f"{int(r_of[g[0]]):06x}"))
    region_of = np.full(n, -1)
    for r, rg in enumerate(regions):
        region_of[rg["provinces"]] = r
    for s, g in enumerate(states):
        rs = {int(region_of[i]) for i in g}
        if len(rs) > 1:
            ys, xs = np.nonzero(lab == g[0])
            errors.append(f"A state lies in {len(rs)} strategic regions (a state must be inside "
                          f"one region), at {where(ys, xs, 1)}")
    for r, rg in enumerate(regions):
        rg["states"] = sorted({int(state_of[i]) for i in rg["provinces"] if state_of[i] >= 0})

    # ---------------------------------------------------------------- report
    for m in notes:
        print("note:", m)
    if errors:
        print(f"\n{len(errors)} problem(s) in the .pdn; fix these and rebuild:")
        for k, m in enumerate(errors[:40], 1):
            print(f"  {k}. {m}")
        sys.exit(1)

    # ---------------------------------------------------------------- heights, rivers
    height = L["Heightmap"][..., :3].astype(np.float32).mean(-1).round().astype(np.int32)
    water = pix_kind != 1
    clamp = (water & (height >= 95)) | (~water & (height <= 95))
    if clamp.any():
        print(f"note: {clamp.sum()} heightmap pixels were on the wrong side of sea level (95) "
              f"and were adjusted")
    height = np.where(water, np.minimum(height, 94), np.maximum(height, 96)).astype(np.uint8)
    rpal = palette_from_header("source/palettes/rivers.bmp.header.bin")
    rv = to_palette(L["Rivers"], rpal, list(range(12)), "Rivers")
    if ((rv >= 0) & water).any():
        print(f"note: Rivers: {((rv >= 0) & water).sum()} river pixels on water were ignored")
    if any(nm in L for nm in OPTIONAL):
        lines = {nm: (L[nm][..., 3] > 0) if nm in L else np.zeros((H, W), bool) for nm in OPTIONAL}
        auto = river_lines.trace(lines["Major Rivers"], lines["Minor Rivers"], ~water)
        drawn = sum(int(m.sum()) for m in lines.values())
        rv = np.where(rv >= 0, rv, np.where(auto != river_lines.NONE, auto, -1))
        print(f"note: Rivers: {drawn} pixels drawn on Major/Minor Rivers became "
              f"{(auto != river_lines.NONE).sum()} river pixels")
    rv = np.where(water, -1, rv)
    for m in river_lines.problems(np.where(rv >= 0, rv, river_lines.NONE).astype(np.uint8), ~water):
        print("note: river problem (the game may draw this river wrong):", m)
    rivers = np.where(rv >= 0, rv, np.where(water, 254, 255)).astype(np.uint8)
    terrain_bmp = np.where(water, TERRAIN_OCEAN, terr).astype(np.uint8)
    t_major = majority(terrain_bmp.astype(np.int64), lab, n)
    ptype = [TERRAIN_TYPES[int(t)] if kind[i] == 1 else ("ocean" if kind[i] == 0 else "lakes")
             for i, t in enumerate(t_major)]

    np.savez_compressed("work/world.npz", kind=pix_kind.astype(np.uint8), cont=cont[lab],
                        shift=(0, 0), height=height, terrain=terrain_bmp, rivers=rivers)
    np.savez_compressed("work/provinces.npz", prov=lab, kind=kind, cont=cont,
                        colors=np.stack([colours >> 16, (colours >> 8) & 255, colours & 255], 1).astype(np.uint8),
                        terrain=np.array(ptype))
    anchor, centre, size = anchors(lab, n)
    np.savez_compressed("work/regions.npz", anchor=anchor, centre=centre, size=size,
                        state_of=state_of, region_of=region_of)
    json.dump(dict(states=states, regions=regions, owners=owners,
                   adjacency=[[int(x), int(y), int(c)] for x, y, c in zip(a, b, cnt)]),
              open("work/regions.json", "w"))
    print(f"read {n} provinces ({(kind == 1).sum()} land, {(kind == 0).sum()} sea, "
          f"{(kind == 2).sum()} lake), {len(states)} states, {len(regions)} strategic regions")


if __name__ == "__main__":
    main()
