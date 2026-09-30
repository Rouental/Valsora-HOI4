"""Regenerate every strategic region from the author's ocean and continent maps (by hand).

    python3 scripts/strategic_regions.py        # edits source/HOI4 Mod Map.pdn in place

Sea: each sea province takes the ocean it lies in on source/ref_oceans.webp, and each
ocean is cut into connected regions of about SEA_AREA px, named after it ("Western North
Demetric"). The author's reference maps use an older arrangement of the continents than
the drawing, so a game position is mapped back continent by continent: game -> drawing
through the layout (work/layout.json, the shift SHIFT), drawing -> reference map through
a per-continent shift fitted by overlap (REF_SHIFT); open water blends the continents
nearby. Enclosed seas (the navigable inland seas) keep their own region.

Land: the states of each continent are grouped into connected regions of about
LAND_AREA px (whole states, as HOI4 needs); lakes join the land region they border most.
A region at least half in one real country is named after it, otherwise after its
continent; several of one name get Western / Central / Eastern (along their length) or
compass points.

Region names go to source/region_names.json (colour -> name), read by build_mod.py.
"""
import colorsys
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.cluster.vq import kmeans2

import pdn_tools as T
from common import COUNTRIES, CONTINENTS, MAP_W as W, MAP_H as H, PLACEHOLDERS

NAMES = Path("source/region_names.json")
SEA_AREA = 350_000   # px per sea region (about 590 px across)
LAND_AREA = 45_000   # px per land region (about 210 px across, like vanilla's)
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


def split(members, cy, cx, area, target, adj, seed):
    """Split connected `members` (provinces or states) into about sum(area)/target
    connected groups: weighted k-means, then stray pieces and tiny groups join the
    neighbouring group they touch most."""
    members = list(members)
    total = sum(area[m] for m in members)
    k = min(len(members), max(1, round(total / target)))
    if k == 1:
        return [members]
    pts = np.array([[cy[m], cx[m]] for m in members], float)
    wts = np.array([area[m] for m in members], float)
    rep = np.repeat(np.arange(len(members)), np.maximum(1, (wts / wts.mean() * 3).round().astype(int)))
    cent, _ = kmeans2(pts[rep], k, minit="++", seed=np.random.default_rng(seed))
    group = {m: int(g) for m, g in zip(members, np.argmin(((pts[:, None] - cent[None]) ** 2).sum(-1), 1))}
    items = set(members)
    for _ in range(50):
        changed = False
        # every group one connected piece: the smaller pieces move to a neighbour
        by_g = defaultdict(list)
        for piece in _pieces(items, lambda u, v: group[u] == group[v], adj):
            by_g[group[piece[0]]].append(piece)
        for g, ps in by_g.items():
            gsize = sum(area[m] for p in ps for m in p)
            ps.sort(key=lambda p: -sum(area[m] for m in p))
            movers = ps[1:] if len(ps) > 1 else (ps if gsize < target / 6 and len(by_g) > 1 else [])
            for p in movers:
                c = Counter(group[v] for u in p for v in adj[u] if v in items and group[v] != g)
                if c:
                    for u in p:
                        group[u] = c.most_common(1)[0][0]
                    changed = True
        if not changed:
            break
    out = defaultdict(list)
    for m, g in group.items():
        out[g].append(m)
    return list(out.values())


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
    sea_groups = []
    for o, members in sorted(by_ocean.items()):
        # oceans across the seam: measure x from the far side
        # an ocean across the seam is unrolled at its widest empty gap in x (an ocean
        # with no gap, all the way round, is left as it is)
        bins = np.zeros(W // 64, bool)
        bins[(np.array([cx[m] for m in members]) // 64).astype(int)] = True
        ux = cx.copy()
        if not bins.all():
            empty = np.nonzero(~bins)[0]
            run = best = start = best_start = 0
            for b_ in np.concatenate([np.arange(len(bins)), np.arange(len(bins))]):
                if not bins[b_]:
                    run += 1
                    if run == 1:
                        start = b_
                    if run > best:
                        best, best_start = run, start
                else:
                    run = 0
            cut = ((best_start + best // 2) % len(bins)) * 64
            for m in members:
                if cx[m] < cut:
                    ux[m] = cx[m] + W
        # an ocean may be in pieces (islands, seam): split each connected piece
        comp, seen = [], set()
        mem = set(members)
        for m in members:
            if m in seen:
                continue
            stack, piece = [m], []
            seen.add(m)
            while stack:
                u = stack.pop()
                piece.append(u)
                for v in adj[u]:
                    if v in mem and v not in seen:
                        seen.add(v)
                        stack.append(v)
            comp.append(piece)
        # compass names are relative to the whole ocean, all its pieces together
        oy = np.average([cy[m] for m in members], weights=[size[m] for m in members])
        ox_ = np.average([ux[m] for m in members], weights=[size[m] for m in members])
        span = max(np.ptp([cy[m] for m in members]), np.ptp([ux[m] for m in members]), 1)
        groups = [g for piece in comp
                  for g in split(piece, cy, ux, size, SEA_AREA, adj, seed=len(sea_groups) + 1)]
        # names read left to right as the map is seen, unless the ocean really straddles
        # the seam (a Friedlich sea): then across it
        nx = cx if bins.mean() > 0.6 else ux

        def wmedian(v, w):  # a region across the seam counts where most of it lies
            o = np.argsort(v)
            return float(np.array(v)[o][np.searchsorted(np.cumsum(np.array(w)[o]), sum(w) / 2)])
        cen = [(np.average([cy[m] for m in g], weights=[size[m] for m in g]),
                wmedian([nx[m] for m in g], [size[m] for m in g])) for g in groups]
        for g, name in zip(groups, place_names(cen, o)):
            sea_groups.append((name, g))
    # a stray bit of an ocean too small to be a region joins the region it touches most
    while True:
        area = [sum(size[m] for m in g) for _, g in sea_groups]
        owner = {m: k for k, (_, g) in enumerate(sea_groups) for m in g}
        small = [k for k in range(len(sea_groups)) if area[k] < SEA_AREA / 6
                 and not sea_groups[k][0] in INLAND]
        moved = False
        for k in sorted(small, key=lambda k: area[k]):
            c = Counter(owner[v] for m in sea_groups[k][1] for v in adj[m] if v in owner and owner[v] != k
                        and sea_groups[owner[v]][0] not in INLAND)
            if c:
                t = c.most_common(1)[0][0]
                sea_groups[t][1].extend(sea_groups[k][1])
                sea_groups.pop(k)
                moved = True
                break
        if not moved:
            break

    # ------------------------------------------------ land
    St = np.where(L["States"][..., 3] > 0, code(L["States"][..., :3]), -1)
    K = code(L["Countries"][..., :3])
    land_provs = np.nonzero(kind == 1)[0]
    st_maj = majority(St, lab, n)
    co_maj = majority(Co, lab, n)
    k_maj = majority(K, lab, n)
    state_of = {int(i): int(st_maj[i]) for i in land_provs if st_maj[i] >= 0}
    # per state: continent, owner, area, centre
    st_members = defaultdict(list)
    for i, s in state_of.items():
        st_members[s].append(i)
    col_cont = {code(np.array(COUNTRIES[c][3])): c for c in CONTINENTS}
    col_country = {code(np.array(v[3])): k for k, v in COUNTRIES.items()}
    s_area, s_cy, s_cx, s_cont, s_owner = {}, {}, {}, {}, {}
    for s, ps in st_members.items():
        s_area[s] = sum(size[p] for p in ps)
        s_cy[s] = np.average([cy[p] for p in ps], weights=[size[p] for p in ps])
        s_cx[s] = np.average([cx[p] for p in ps], weights=[size[p] for p in ps])
        cc, ow = Counter(), Counter()
        for p in ps:
            cc[int(co_maj[p])] += size[p]
            ow[int(k_maj[p])] += size[p]
        s_cont[s] = col_cont.get(cc.most_common(1)[0][0], "?")
        s_owner[s] = col_country.get(ow.most_common(1)[0][0], "?")
    s_adj = defaultdict(set)
    for u, vs in adj.items():
        if u in state_of:
            for v in vs:
                if v in state_of and state_of[u] != state_of[v]:
                    s_adj[state_of[u]].add(state_of[v])
    def regions_of(members, seed):
        """Split states into connected regions of about LAND_AREA; islands too small
        for a region join the nearest piece."""
        mem = set(members)
        comps, seen = [], set()
        for m in sorted(members, key=lambda s: -s_area[s]):
            if m in seen:
                continue
            stack, piece = [m], []
            seen.add(m)
            while stack:
                u = stack.pop()
                piece.append(u)
                for v in s_adj[u]:
                    if v in mem and v not in seen:
                        seen.add(v)
                        stack.append(v)
            comps.append(piece)
        big = [c for c in comps if sum(s_area[s] for s in c) >= LAND_AREA / 4] or [max(comps, key=len)]
        for c in comps:
            if c in big:
                continue
            cyc, cxc = np.mean([s_cy[s] for s in c]), np.mean([s_cx[s] for s in c])
            tgt = min(big, key=lambda b: min(np.hypot(s_cy[s] - cyc, s_cx[s] - cxc) for s in b))
            tgt.extend(c)
            for s in c:  # adjacent for splitting purposes
                s_adj[s].add(tgt[0])
                s_adj[tgt[0]].add(s)
        return [g for piece in big for g in split(piece, s_cy, s_cx, s_area, LAND_AREA, s_adj, seed)]

    land_groups = []
    for cont in CONTINENTS:
        members = [s for s in st_members if s_cont[s] == cont]
        if not members:
            continue
        # real countries big enough get regions of their own; small ones join the big
        # country they border most, so regions follow the borders of drawn countries
        area_of = Counter()
        for s in members:
            area_of[s_owner[s]] += s_area[s]
        anchors = {c for c, a in area_of.items() if c not in PLACEHOLDERS and c != "?" and a >= LAND_AREA / 4}
        home = {s: s_owner[s] for s in members if s_owner[s] in anchors}
        for c in [c for c in area_of if c not in anchors and c not in PLACEHOLDERS and c != "?"]:
            touch = Counter(s_owner[v] for s in members if s_owner[s] == c for v in s_adj[s]
                            if v in s_owner and s_owner[v] in anchors)
            if touch:
                for s in members:
                    if s_owner[s] == c:
                        home[s] = touch.most_common(1)[0][0]
        units = defaultdict(list)
        for s in members:
            units[home.get(s, None)].append(s)
        for country, sts in units.items():
            for g in regions_of(sts, seed=len(land_groups) + 7):
                gy_ = np.average([s_cy[s] for s in g], weights=[s_area[s] for s in g])
                gx_ = np.average([s_cx[s] for s in g], weights=[s_area[s] for s in g])
                own = Counter()
                for s in g:
                    own[s_owner[s]] += s_area[s]
                real = [(c, a) for c, a in own.most_common() if c not in PLACEHOLDERS and c != "?"]
                if country:
                    base = COUNTRIES[country][1]
                elif real and real[0][1] >= 0.5 * sum(own.values()):
                    base = COUNTRIES[real[0][0]][1]
                else:
                    base = cont.capitalize()
                land_groups.append((base, gy_, gx_, g))
    # names: a base used once stands alone; otherwise compass words around its centre
    by_base = defaultdict(list)
    for base, gy_, gx_, g in land_groups:
        by_base[base].append((gy_, gx_, g))
    land_named = []
    for base, items in by_base.items():
        if len(items) == 1:
            land_named.append((base, items[0][2]))
            continue
        for (y, x, g), name in zip(items, place_names([(y, x) for y, x, _ in items], base)):
            land_named.append((name, g))

    # unique names: number repeats
    def uniq(pairs):
        count = Counter(n for n, _ in pairs)
        seen = Counter()
        out = []
        for nm, g in pairs:
            if count[nm] > 1:
                seen[nm] += 1
                nm = f"{nm} {seen[nm]}" if seen[nm] > 1 else nm
            out.append((nm, g))
        return out
    sea_groups = uniq(sea_groups)
    land_named = uniq(land_named)

    # ------------------------------------------------ colours and write
    blues = T.palette(len(sea_groups), True, 21)
    others = T.palette(len(land_named), False, 22, set(blues))
    newR = np.zeros((H, W), np.int64)
    names_out = {}
    prov_col = np.zeros(n, np.int64)
    for (nm, g), c in zip(sea_groups, blues):
        prov_col[g] = c
        names_out[f"{c:06x}"] = nm
    for (nm, g), c in zip(land_named, others):
        provs = [p for s in g for p in st_members[s]]
        prov_col[provs] = c
        names_out[f"{c:06x}"] = nm
    # lakes join the land region they border most
    for i in np.nonzero(kind == 2)[0]:
        c = Counter(prov_col[v] for v in adj[i] if kind[v] == 1 and prov_col[v])
        prov_col[i] = c.most_common(1)[0][0] if c else others[0]
    # anything left (a land province with no state) takes its neighbours' region
    for i in np.nonzero(prov_col == 0)[0]:
        c = Counter(prov_col[v] for v in adj[i] if prov_col[v] and kind[v] == kind[i])
        if c:
            prov_col[i] = c.most_common(1)[0][0]
    newR = prov_col[lab]
    T.put(L["Strategic Regions"], newR, np.ones((H, W), bool))
    L["Strategic Regions"][..., 3] = 255
    NAMES.write_text(json.dumps(names_out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(sea_groups)} sea regions, {len(land_named)} land regions; names in {NAMES}")
    T.save(names, L)


if __name__ == "__main__":
    main()
