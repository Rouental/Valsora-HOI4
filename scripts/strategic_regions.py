"""Sea regions from the author's ocean map (by hand): one region per ocean, unsplit.

    python3 scripts/strategic_regions.py        # edits source/HOI4 Mod Map.pdn in place

Each sea province takes the ocean it lies in on source/ref_oceans.webp, and every ocean
becomes one strategic region, as big as the map shows it (author, 2026-09-30: "leave it
as a massive unaltered region, so we can edit it later"). Only where HOI4 forces it is
an ocean in more than one region: a sea region must be one connected body of water, so
an ocean the land cuts apart gets a region per piece. The navigable inland seas (Piscary,
Norlany) keep one each. Land regions are not touched.

The author's reference maps use an older arrangement of the continents than the drawing,
so a game position is mapped back continent by continent: game -> drawing through the
layout (work/layout.json, the shift SHIFT), drawing -> reference map through a
per-continent shift fitted by overlap (REF_SHIFT); each nearby continent votes.

Region names go to source/region_names.json (colour -> name), read by build_mod.py.
"""
import colorsys
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

import pdn_tools as T
from common import COUNTRIES, CONTINENTS, MAP_W as W, MAP_H as H, PLACEHOLDERS

NAMES = Path("source/region_names.json")
STRAY = 0.15  # a piece of an ocean under this share of its main body is mapping noise
SHIFT = (36, 16)     # (dy, dx) compose.py centred the land by, recovered by overlap
# reference map (2000 x 933) = drawing / 7 + this, per layout block (fitted by overlap)
REF_SHIFT = {0: (-93, -6), 1: (10, -130), 2: (101, -216), 3: (-20, 136), 4: (-16, -165),
             5: (-34, -1)}
REF_SHIFT_WEST = {"nonscio": (-93, -6), "araseos": (-117, -77)}
REF_W, REF_H = 2000, 933
# ocean colours on ref_oceans.webp; the lilac is two oceans, split north / south
OCEANS = {"lilac": (212, 180, 228), "North Demetric": (124, 124, 156),
          "South Demetric": (92, 116, 108), "North Menotius": (252, 204, 204),
          "South Menotius": (108, 172, 132), "Northern Friedlich": (180, 228, 204),
          "Southern Friedlich": (204, 204, 124), "Midtierre Sea": (172, 204, 164)}
INLAND = {"Piscary Sea": (806, 954), "Norlany Sea": (2457, 439)}  # a pixel (x, y) in each
CROSS = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])


def majority(values, lab, n):
    """Most common value per province (values: any integer codes, same shape as lab)."""
    v, vi = np.unique(values, return_inverse=True)
    key = lab.ravel().astype(np.int64) * len(v) + vi.ravel()
    k, c = np.unique(key, return_counts=True)
    prov, val = k // len(v), k % len(v)
    order = np.lexsort((-c, prov))
    first = np.unique(prov[order], return_index=True)[1]
    out = np.full(n, -1, np.int64)
    out[prov[order][first]] = v[val[order][first]]
    return out


def ocean_map():
    """Ocean name per reference-map pixel (every pixel gets the nearest ocean)."""
    oc = np.asarray(Image.open("source/ref_oceans.webp").convert("RGB")).astype(int)
    co = np.asarray(Image.open("source/ref_continents.webp").convert("RGB")).astype(int)
    water = np.abs(co - [51, 51, 51]).sum(-1) < 40
    names = []
    lab = np.zeros(water.shape, int)
    for k, (name, rgb) in enumerate(OCEANS.items(), 1):
        m = water & (np.abs(oc - rgb).sum(-1) < 24)
        comp, n = ndi.label(m)
        sz = np.bincount(comp.ravel())
        m &= (sz[comp] >= 2000) & (comp > 0)  # drop inland seas and specks
        lab[m] = k
        names.append(name)
    idx = ndi.distance_transform_edt(lab == 0, return_distances=False, return_indices=True)
    lab = lab[idx[0], idx[1]]
    out = np.array(names, object)[lab - 1]
    lilac = out == "lilac"
    ys = np.arange(REF_H)[:, None].repeat(REF_W, 1)
    out[lilac & (ys < REF_H // 2)] = "Northern Ocean"
    out[lilac & (ys >= REF_H // 2)] = "Arctic Ocean"
    return out


def ocean_grid(oceans, continents, step=4):
    """Ocean name for every game pixel on a grid of `step`. Each continent predicts,
    through its own move, where a game pixel lay on the reference map; the continents
    vote with weight 1 / (distance + 20)^2, so near a coast its own continent decides.
    (Averaging the positions instead put open water in unrelated oceans.)"""
    lay = json.load(open("work/layout.json"))
    gy, gx = np.mgrid[0:H:step, 0:W:step].astype(float)
    names = sorted(set(oceans.ravel().tolist()))
    votes = np.zeros((len(names),) + gy.shape)
    oidx = np.searchsorted(names, oceans)
    for b, blk in enumerate(lay["blocks"]):
        land = np.load(f"work/blocks/{b}.npy")
        ox, oy = blk["offset"]
        g = np.zeros((H, W), bool)
        y0, x0 = oy + SHIFT[0], ox + SHIFT[1]
        g[y0:y0 + land.shape[0], x0:x0 + land.shape[1]] = land[:H - y0, :W - x0]
        # Nonscio and Araseos share a layout block but moved apart on the reference map
        parts = [(REF_SHIFT[b], g)] if b != 0 else [
            (REF_SHIFT_WEST[c], g & (continents == c)) for c in REF_SHIFT_WEST]
        for (sy_, sx_), gm in parts:
            d = ndi.distance_transform_edt(~gm[::step, ::step]) * step
            w = 1.0 / (d + 20.0) ** 2
            ry = ((blk["src_bbox"][1] + (gy - y0) / lay["scale"]) / 7 + sy_).round().astype(int)
            rx = ((blk["src_bbox"][0] + (gx - x0) / lay["scale"]) / 7 + sx_).round().astype(int)
            k = oidx[np.clip(ry, 0, REF_H - 1), rx % REF_W]
            np.add.at(votes, (k, np.arange(gy.shape[0])[:, None], np.arange(gy.shape[1])[None]), w)
    return np.array(names, object)[votes.argmax(0)]


def compass(dy, dx):
    if abs(dy) < 0.2 and abs(dx) < 0.2:
        return "Central"
    a = np.degrees(np.arctan2(-dy, dx)) % 360
    return ["Eastern", "Northeastern", "Northern", "Northwestern", "Western",
            "Southwestern", "Southern", "Southeastern"][int(((a + 22.5) % 360) // 45)]


def _pieces(items, same, adj):
    """Connected pieces of `items` where neighbours count only if same(u, v)."""
    seen, out = set(), []
    for m in items:
        if m in seen:
            continue
        stack, piece = [m], []
        seen.add(m)
        while stack:
            u = stack.pop()
            piece.append(u)
            for v in adj[u]:
                if v in items and v not in seen and same(u, v):
                    seen.add(v)
                    stack.append(v)
        out.append(piece)
    return out


RANKS = {2: ["{a}", "{b}"], 3: ["{a}", "Central", "{b}"], 4: ["Far {a}", "{a}", "{b}", "Far {b}"],
         5: ["Far {a}", "{a}", "Central", "{b}", "Far {b}"],
         6: ["Far {a}", "{a}", "{a}-Central", "{b}-Central", "{b}", "Far {b}"],
         7: ["Far {a}", "{a}", "{a}-Central", "Central", "{b}-Central", "{b}", "Far {b}"]}


def place_names(centres, base):
    """Names for the pieces of one area: along its length for long areas (Western,
    Central, Eastern...), compass points otherwise; repeats get numbers."""
    k = len(centres)
    if k == 1:
        return [base]
    ys = np.array([c[0] for c in centres])
    xs = np.array([c[1] for c in centres])
    if k <= 7 and np.ptp(xs) >= 1.5 * np.ptp(ys):
        words = [w.format(a="Western", b="Eastern").replace("Western-", "West-").replace("Eastern-", "East-")
                 for w in RANKS[k]]
        order = np.argsort(xs)
    elif k <= 7 and np.ptp(ys) >= 1.5 * np.ptp(xs):
        words = [w.format(a="Northern", b="Southern").replace("Northern-", "North-").replace("Southern-", "South-")
                 for w in RANKS[k]]
        order = np.argsort(ys)
    else:
        span = max(np.ptp(ys), np.ptp(xs), 1)
        words = [compass((y - ys.mean()) / span * 2, (x - xs.mean()) / span * 2) for y, x in centres]
        order = np.arange(k)
    names = [None] * k
    for w, i in zip(words, order):
        names[i] = f"{w} {base}"
    return names


def main():
    names, L = T.load()
    code = T.code
    P = code(L["Provinces"][..., :3])
    ter = code(L["Terrain"][..., :3])
    sea_px = ter == code(np.array(T.OCEAN))
    lake_px = ter == code(np.array(T.LAKES))
    cols, lab = np.unique(P, return_inverse=True)
    lab = lab.reshape(H, W)
    n = len(cols)
    size = np.bincount(lab.ravel(), minlength=n).astype(float)
    kind = np.where(np.bincount(lab.ravel(), sea_px.ravel(), n) * 2 > size, 0,
                    np.where(np.bincount(lab.ravel(), lake_px.ravel(), n) * 2 > size, 2, 1))
    gy, gx = np.mgrid[0:H, 0:W]
    cy = np.bincount(lab.ravel(), gy.ravel(), n) / size
    cx = np.bincount(lab.ravel(), gx.ravel(), n) / size
    # province adjacency (wrapping at the seam)
    adj = defaultdict(set)
    for a, b in ((lab[:, :-1], lab[:, 1:]), (lab[:-1], lab[1:]), (lab[:, -1], lab[:, 0])):
        d = a != b
        for u, v in set(zip(a[d].tolist(), b[d].tolist())):
            adj[u].add(v)
            adj[v].add(u)

    # ------------------------------------------------ sea
    oceans = ocean_map()
    Co = code(L["Continents"][..., :3])
    cont_name = np.full(Co.shape, "", object)
    for c in CONTINENTS:
        cont_name[Co == code(np.array(COUNTRIES[c][3]))] = c
    ocean_px = ocean_grid(oceans, cont_name, 4)
    onames = sorted(set(ocean_px.ravel().tolist()))
    oidx = np.searchsorted(onames, ocean_px)
    lab4 = lab[::4, ::4]
    maj = majority(oidx, lab4, n)
    seas = np.nonzero(kind == 0)[0]
    ocean_of = {}
    for i in seas:
        if maj[i] < 0:  # too small for the 1/4 grid: its centre decides
            maj[i] = oidx[min(int(cy[i]) // 4, oidx.shape[0] - 1), min(int(cx[i]) // 4, oidx.shape[1] - 1)]
        ocean_of[int(i)] = onames[maj[i]]
    # on the reference map the top edge is all Northern Ocean and the bottom edge all
    # Arctic Ocean; the mapping let South Demetric reach the bottom and cut the Arctic
    for row, name in ((0, "Northern Ocean"), (H - 1, "Arctic Ocean")):
        for i in np.unique(lab[row]):
            if kind[i] == 0:
                ocean_of[int(i)] = name
    # enclosed seas (the navigable inland ones) keep their own region
    wcomp, _ = ndi.label(sea_px, CROSS)
    for name, (x, y) in INLAND.items():
        inl = np.unique(lab[wcomp == wcomp[y, x]])
        for i in inl:
            if kind[i] == 0:
                ocean_of[int(i)] = name
    by_ocean = defaultdict(list)
    for i, o in ocean_of.items():
        by_ocean[o].append(int(i))
    # one region per ocean, as the reference map shows it (author, 2026-09-30). HOI4
    # needs a sea region to be one connected body of water, so an ocean the land cuts
    # in two becomes two regions; stray bits (mapping noise along coasts) join the
    # region they touch most.
    sea_groups = []
    for o, members in sorted(by_ocean.items()):
        for piece in _pieces(set(members), lambda u, v: True, adj):
            sea_groups.append([o, piece])
    while True:
        area = [sum(size[m] for m in g) for _, g in sea_groups]
        owner = {m: k for k, (_, g) in enumerate(sea_groups) for m in g}
        biggest = {}
        for k, (o, g) in enumerate(sea_groups):
            if o not in biggest or area[k] > area[biggest[o]]:
                biggest[o] = k
        # a piece is a stray if it is small next to its ocean's main body
        stray = [k for k, (o, g) in enumerate(sea_groups) if o not in INLAND and k != biggest[o]
                 and area[k] < STRAY * area[biggest[o]]]
        moved = False
        for k in sorted(stray, key=lambda k: area[k]):
            c = Counter(owner[v] for m in sea_groups[k][1] for v in adj[m]
                        if v in owner and owner[v] != k and sea_groups[owner[v]][0] not in INLAND)
            if c:
                t = c.most_common(1)[0][0]
                sea_groups[t][1].extend(sea_groups[k][1])
                sea_groups.pop(k)
                moved = True
                break
        if not moved:
            break
    # an ocean still in several pieces: West / East (or compass) names
    named = []
    by_o = defaultdict(list)
    for o, g in sea_groups:
        by_o[o].append(g)
    for o, gs in by_o.items():
        cen = [(np.average([cy[m] for m in g], weights=[size[m] for m in g]),
                np.average([cx[m] for m in g], weights=[size[m] for m in g])) for g in gs]
        for g, nm in zip(gs, place_names(cen, o)):
            named.append((nm, g))

    # ------------------------------------------------ write: sea provinces only
    R = code(L["Strategic Regions"][..., :3])
    land_cols = set(np.unique(R[~sea_px]).tolist())
    blues = T.palette(len(named), True, 21, land_cols)
    prov_col = np.full(n, -1, np.int64)
    names_out = {}
    for (nm, g), c in zip(named, blues):
        prov_col[g] = c
        names_out[f"{c:06x}"] = nm
    new = prov_col[lab]
    m = new >= 0
    R[m] = new[m]
    T.put(L["Strategic Regions"], R, m)
    NAMES.write_text(json.dumps(names_out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    for nm, g in sorted(named):
        print(f"  {nm}: {len(g)} sea provinces")
    print(f"{len(named)} sea regions; land regions untouched; names in {NAMES}")
    T.save(names, L)


if __name__ == "__main__":
    main()
