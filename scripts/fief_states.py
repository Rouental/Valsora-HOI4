"""A nation's states from the author's own map of its fiefs (2026-10-20: Rouental_Map_TEMP_2.pdn, "Let's go with the
30 pixel version"): each fief a state, the fiefs too small for the game's map merged into a neighbour (run by hand).

The fief map is a paint.net file of its own at any scale (Rouental's: 8000 x 4471, 25.84 of its pixels to the game's):
  PROVINCE Colors   the fiefs, filled in a few colours, neighbours apart by
  PROVINCE Borders  black lines;
  Fief Markers      the crownlands (author: "the areas currently under the direct control of the Sacred Prince");
  Rough Governorates  the governorates, rough patches in a few colours.
It is fitted onto the nation's land on the game map (scale and offset, by overlap); each game pixel of the nation
takes the fief most of it covers. A fief under --min game px joins the neighbour it shares the most border with,
crownland only with crownland and within its governorate where it can; provinces of about --province px are cut in
each state (organic, as apply_outlines.py cuts them), each piece of land of its own, none under MIN_PROVINCE; each
state goes into the strategic region most of it lies in. The nation's outline stays the game map's.

    python3 scripts/fief_states.py FIEFS.pdn TAG [--min 30] [--province 140] [--names NAMES.json] [--apply]

Without --apply: the plan (work/fief_states/: preview.png, the states' numbers on namesheet_*.png for naming).
With --apply it rewrites, inside the nation's land, the Provinces, States and Strategic Regions layers of
source/HOI4 Mod Map.pdn, its Necessary States lines (one pixel on one side of every state border, so the lines close
each state as regroup_states.py reads them) and clears its Necessary Provinces lines (they were the old states');
source/state_names.json (the old names inside the land go, each state takes its largest named fief's name from
NAMES.json, "x,y" of a pixel of the fief map inside the name's fief -> the name); and writes work/fief_states/
remap.json: every old state name -> the new states lying mostly on it, for nations.py's lists (releasables, civil
war) and the Gazetteer's facts (gazetteer_rekey).
"""
import argparse
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi

sys.path.insert(0, str(Path(__file__).parent))
from common import COUNTRIES, MIN_PROVINCE  # noqa: E402
from apply_outlines import Colours, organic_split  # noqa: E402
import pdn_tools  # noqa: E402

WORK = Path("work/fief_states")
NAMES = Path("source/state_names.json")
CROSS = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])
FIEF_LAYERS = ("PROVINCE Colors", "PROVINCE Borders", "Fief Markers", "Rough Governorates", "PROVINCE Names")


def read_fief_map(path):
    out = WORK / "fiefmap"
    subprocess.run([sys.executable, str(Path(__file__).parent / "readpdn.py"), str(path), str(out)], check=True,
                   stdout=subprocess.DEVNULL)
    names = (out / "layers.txt").read_text().splitlines()
    missing = [n for n in FIEF_LAYERS if n not in names]
    if missing:
        sys.exit(f"{path}: no layer {missing}")
    L = {n: np.load(out / f"layer{names.index(n)}.npy") for n in FIEF_LAYERS}
    for k, n in enumerate(names):          # the rest (cultures, rivers, references ...) only take room
        if n not in FIEF_LAYERS:
            (out / f"layer{k}.npy").unlink(missing_ok=True)
    return L


def components(fill, lines=None):
    """each colour's 4-connected areas, numbered from 1 (lines, if given, apart)"""
    free = fill[..., 3] == 255
    if lines is not None:
        free &= lines[..., 3] == 0
    col = pdn_tools.code(fill[..., :3])
    lab = np.zeros(free.shape, np.int32)
    n = 0
    for c in np.unique(col[free]).tolist():
        part, k = ndi.label(free & (col == c))
        lab[part > 0] = part[part > 0] + n
        n += k
    return lab


def fit(fiefs, land, box):
    """(scale, ox, oy): game x = ox + fief x / scale, by the best overlap of the two outlines"""
    X0, Y0, X1, Y1 = box
    g = land[Y0:Y1, X0:X1]
    gy, gx = np.mgrid[Y0:Y1, X0:X1]
    F = fiefs > 0
    ys, xs = np.nonzero(F[::8, ::8])
    gys, gxs = np.nonzero(g)
    s0 = (xs.max() - xs.min()) * 8 / (gxs.max() - gxs.min() + 1)

    def iou(s, ox, oy):
        lx = ((gx + 0.5 - ox) * s).astype(int)
        ly = ((gy + 0.5 - oy) * s).astype(int)
        ok = (lx >= 0) & (lx < F.shape[1]) & (ly >= 0) & (ly < F.shape[0])
        v = np.zeros_like(g)
        v[ok] = F[ly[ok], lx[ok]]
        return (v & g).sum() / max((v | g).sum(), 1)

    best = (0, s0, X0 + gxs.min() - xs.min() * 8 / s0, Y0 + gys.min() - ys.min() * 8 / s0)
    for step, span in ((0.1, 8), (0.02, 5)):
        _, s1, ox1, oy1 = best
        for s in s1 + step * np.arange(-span, span + 1):
            for ox in ox1 + step * 5 * np.arange(-span, span + 1):
                for oy in oy1 + step * 5 * np.arange(-span, span + 1):
                    r = iou(s, ox, oy)
                    if r > best[0]:
                        best = (r, s, ox, oy)
    return best


def to_game(fiefs, land, box, s, ox, oy, k=6):
    """each game pixel of the land: the fief most of it covers; land the fief map leaves out, the nearest fief"""
    X0, Y0, X1, Y1 = box
    H, W = Y1 - Y0, X1 - X0
    gy, gx = np.mgrid[0:H, 0:W]
    votes = []
    for i in range(k):
        for j in range(k):
            lx = ((gx + X0 + (j + 0.5) / k - ox) * s).astype(int)
            ly = ((gy + Y0 + (i + 0.5) / k - oy) * s).astype(int)
            ok = (lx >= 0) & (lx < fiefs.shape[1]) & (ly >= 0) & (ly < fiefs.shape[0])
            v = np.zeros((H, W), np.int32)
            v[ok] = fiefs[ly[ok], lx[ok]]
            votes.append(v)
    V = np.stack(votes, -1)
    m = land[Y0:Y1, X0:X1]
    g = np.zeros((H, W), np.int32)
    for y, x in zip(*np.nonzero(m)):
        c = Counter(V[y, x][V[y, x] > 0].tolist())
        if c:
            g[y, x] = c.most_common(1)[0][0]
    if (g > 0).any():
        _, (iy, ix) = ndi.distance_transform_edt(g == 0, return_indices=True)
        miss = m & (g == 0)
        g[miss] = g[iy[miss], ix[miss]]
    g[~m] = 0
    return g


def majority(lab, other, ids):
    """id -> the value of `other` under most of its pixels (0 for none)"""
    out = {}
    for f in ids:
        c = Counter(other[(lab == f) & (other > 0)].tolist())
        out[f] = c.most_common(1)[0][0] if c else 0
    return out


def merge(u, T, crown, gov, keep=()):
    """units under T px join the neighbour they share most border with: crownland with crownland first, then
    the same governorate; an island the nearest unit. `keep`: units never merged into others (they may grow)"""
    u = u.copy()
    while True:
        ids, cnt = np.unique(u[u > 0], return_counts=True)
        small = sorted((c, i) for i, c in zip(ids, cnt) if c < T and i not in keep)
        if not small:
            return u
        _, a = small[0]
        m = u == a
        ring = ndi.binary_dilation(m, CROSS) & ~m
        nb = Counter(u[ring & (u > 0)].tolist())
        if nb:
            b = max(nb, key=lambda q: (crown.get(q, False) == crown.get(a, False), gov.get(q) == gov.get(a), nb[q], -q))
        else:
            d, (jy, jx) = ndi.distance_transform_edt(~((u > 0) & ~m), return_indices=True)
            yy, xx = np.nonzero(m)
            k0 = np.argmin(d[yy, xx])
            b = u[jy[yy[k0], xx[k0]], jx[yy[k0], xx[k0]]]
        u[m] = b


def islands(u):
    """a piece of land too small to be a province of its own (under MIN_PROVINCE * 2) is wholly one state"""
    comp, n = ndi.label(u > 0, CROSS)
    for q in range(1, n + 1):
        m = comp == q
        if m.sum() < 2 * MIN_PROVINCE and len(np.unique(u[m])) > 1:
            u[m] = Counter(u[m].tolist()).most_common(1)[0][0]
    return u


def tidy(u):
    """a state's stray pieces (a fief's footprint touches itself only at corners, at the game's scale) join the
    neighbouring state they share most border with; a piece that is land of its own (an island) stays"""
    for _ in range(6):
        changed = False
        for a in np.unique(u[u > 0]):
            comp, n = ndi.label(u == a, CROSS)
            if n < 2:
                continue
            sizes = np.bincount(comp.ravel())[1:]
            for q in range(1, n + 1):
                if q == np.argmax(sizes) + 1:
                    continue
                pm = comp == q
                ring = ndi.binary_dilation(pm, CROSS) & ~pm
                nb = Counter(v for v in u[ring].tolist() if v > 0 and v != a)
                if nb:
                    u[pm] = nb.most_common(1)[0][0]
                    changed = True
        if not changed:
            return u
    return u


def provinces(u, P, seed=0):
    """each state's provinces: every piece of its land cut into round(area / P) organic pieces, none under
    MIN_PROVINCE (a smaller one joins a neighbour in its state), each 4-connected"""
    out = np.zeros_like(u)
    nid = 0
    for a in np.unique(u[u > 0]):
        comp, n = ndi.label(u == a, CROSS)
        for q in range(1, n + 1):
            ys, xs = np.nonzero(comp == q)
            k = max(1, min(int(round(len(ys) / P)), len(ys) // MIN_PROVINCE))
            parts = organic_split(ys, xs, k, seed=seed + nid)
            for j in range(k):
                sel = parts == j
                if sel.any():
                    nid += 1
                    out[ys[sel], xs[sel]] = nid
    # every province one 4-connected piece of MIN_PROVINCE px or more, inside its state
    for _ in range(4):
        changed = False
        for p in np.unique(out[out > 0]):
            m = out == p
            comp, n = ndi.label(m, CROSS)
            sizes = np.bincount(comp.ravel())[1:]
            for q in range(1, n + 1):
                pm = comp == q
                if n > 1 and q == np.argmax(sizes) + 1 and sizes[q - 1] >= MIN_PROVINCE:
                    continue
                if n == 1 and sizes[0] >= MIN_PROVINCE:
                    continue
                ring = ndi.binary_dilation(pm, CROSS) & ~pm & (u == u[pm][0])
                nb = Counter(v for v in out[ring].tolist() if v != p)
                if nb:
                    out[pm] = nb.most_common(1)[0][0]
                    changed = True
                elif n > 1:          # a separate piece of the state: a province of its own
                    nid += 1
                    out[pm] = nid
                    changed = True
        if not changed:
            break
    return out


def boundary(lab, inside):
    """one side of every 4-adjacent pair of different labels inside: closes each label's area"""
    e = np.zeros(lab.shape, bool)
    r = (lab[:, :-1] != lab[:, 1:]) & inside[:, :-1] & inside[:, 1:]
    d = (lab[:-1, :] != lab[1:, :]) & inside[:-1, :] & inside[1:, :]
    e[:, :-1] |= r
    e[:-1, :] |= d
    return e


def interior(m):
    """the pixel deepest inside a mask (y, x)"""
    d = ndi.distance_transform_edt(np.pad(m, 1))[1:-1, 1:-1]
    y, x = np.unravel_index(np.argmax(d), d.shape)
    return int(y), int(x)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fiefmap")
    ap.add_argument("tag")
    ap.add_argument("--min", type=int, default=30)
    ap.add_argument("--province", type=int, default=140)
    ap.add_argument("--names")
    ap.add_argument("--keep", default="", help="x,y=Name;... game pixels whose old state stays a state of its own, "
                    "so named (the capital's city state)")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    WORK.mkdir(parents=True, exist_ok=True)
    F = read_fief_map(a.fiefmap)
    fiefs = components(F["PROVINCE Colors"], F["PROVINCE Borders"])
    crown_px = F["Fief Markers"][..., 3] > 0
    govs = components(F["Rough Governorates"])

    names, L = pdn_tools.load()
    t = L["Terrain"][..., :3]
    land_all = ~((t == pdn_tools.OCEAN).all(-1) | (t == pdn_tools.LAKES).all(-1))
    colour = next(v[3] for v in COUNTRIES.values() if v[0] == a.tag)
    K = pdn_tools.code(L["Countries"][..., :3])
    nation = land_all & (K == ((colour[0] << 16) | (colour[1] << 8) | colour[2])) & (L["Countries"][..., 3] > 0)
    comp, n = ndi.label(nation, CROSS)
    big = np.argmax(np.bincount(comp.ravel())[1:]) + 1
    ys, xs = np.nonzero(comp == big)
    w, h = xs.max() - xs.min(), ys.max() - ys.min()
    box = (max(xs.min() - w // 4, 0), max(ys.min() - h // 4, 0), xs.max() + w // 4 + 1, ys.max() + h // 4 + 1)
    X0, Y0, X1, Y1 = box
    r, s, ox, oy = fit(fiefs, nation, box)
    print(f"fit: {s:.2f} fief map px to a game px, offset ({ox:.1f}, {oy:.1f}), {r:.1%} overlap; box {box}")
    g = to_game(fiefs, nation, box, s, ox, oy)
    ids = np.unique(g[g > 0])
    sub = fiefs[::2, ::2]
    tot = np.bincount(sub.ravel(), minlength=fiefs.max() + 1)
    red = np.bincount(sub[crown_px[::2, ::2]].ravel(), minlength=fiefs.max() + 1)
    crown = {int(f): bool(red[f] * 2 > tot[f]) for f in ids}
    gov = majority(fiefs[::4, ::4], govs[::4, ::4], ids)
    print(f"{len(ids)} fiefs on the land, {sum(crown.values())} of them crownland, {len(set(gov.values()))} governorates")

    # the old states: kept apart where asked (the capital's city state)
    St = np.where(L["States"][..., 3] > 0, pdn_tools.code(L["States"][..., :3]), -1)
    oldS = St[Y0:Y1, X0:X1]
    m = nation[Y0:Y1, X0:X1]
    keep, kept_name = set(), {}
    for item in filter(None, a.keep.split(";")):
        xy, _, nm = item.partition("=")
        x, y = map(int, xy.split(","))
        sc = St[y, x]
        unit = int(fiefs.max()) + 1 + len(keep)       # above every fief's number
        kept_name[unit] = nm
        crown[unit], gov[unit] = True, gov.get(Counter(g[(oldS == sc) & m].tolist()).most_common(1)[0][0], 0)
        g[m & (oldS == sc)] = unit
        keep.add(unit)
    u = islands(merge(g, a.min, crown, gov, keep))
    for _ in range(3):  # strays tidied, then any state that fell under --min merged again
        u = tidy(u)
        if np.unique(u[u > 0], return_counts=True)[1].min() >= a.min:
            break
        u = merge(u, a.min, crown, gov, keep)
    sids, cnt = np.unique(u[u > 0], return_counts=True)
    p = provinces(u, a.province)
    pids, pcnt = np.unique(p[p > 0], return_counts=True)
    print(f"{len(sids)} states (median {np.median(cnt):.0f} px, smallest {cnt.min()}), {len(pids)} provinces "
          f"(median {np.median(pcnt):.0f}, smallest {pcnt.min()})")
    np.savez(WORK / "plan.npz", states=u, provs=p, fiefs=g, box=np.array(box))

    # names: each state's largest fief with a name
    fief_name = {}
    if a.names:
        for key, nm in json.load(open(a.names, encoding="utf-8")).items():
            x, y = map(int, key.split(","))
            f = int(fiefs[y, x])
            if f:
                fief_name[f] = nm
    state_name = {k: v for k, v in kept_name.items() if v}
    for sid in sids:
        if int(sid) in state_name:
            continue
        fs = Counter(g[u == sid].tolist())
        for f, _ in fs.most_common():
            if f in fief_name:
                state_name[int(sid)] = fief_name[f]
                break
    json.dump({"fit": [s, ox, oy], "states": {int(k): v for k, v in state_name.items()},
               "fiefs_of": {int(sid): [int(f) for f, _ in Counter(g[u == sid].tolist()).most_common()] for sid in sids},
               "crown": [int(f) for f, c in crown.items() if c]},
              open(WORK / "plan.json", "w"), ensure_ascii=False, indent=0)
    if not a.apply:
        return

    # old state names inside the land, and what lies on each
    sn = json.load(open(NAMES, encoding="utf-8"))
    old_name = {}
    for key, nm in list(sn.items()):
        x, y = map(int, key.split(","))
        if X0 <= x < X1 and Y0 <= y < Y1 and m[y - Y0, x - X0]:
            old_name[int(St[y, x])] = nm
            del sn[key]
    remap = defaultdict(list)
    for sid in sids:
        sm = u == sid
        c = Counter(oldS[sm].tolist())
        sc, v = c.most_common(1)[0]
        if sc in old_name:
            remap[old_name[sc]].append(int(sid))
    # the new layers
    P = pdn_tools.code(L["Provinces"][..., :3])
    pcols, scols = Colours(P, 2026_10_20), Colours(St[St >= 0], 2026_10_21)
    R = pdn_tools.code(L["Strategic Regions"][..., :3])
    wP, wS, wR = P[Y0:Y1, X0:X1].copy(), St[Y0:Y1, X0:X1].copy(), R[Y0:Y1, X0:X1].copy()
    pc = {int(q): pcols.new() for q in pids}
    sc_ = {int(q): scols.new() for q in sids}
    keys = {}
    for sid in sids:
        sm = u == sid
        wS[sm] = sc_[int(sid)]
        wR[sm] = Counter(wR[sm].tolist()).most_common(1)[0][0]
        y, x = interior(sm)
        keys[int(sid)] = f"{x + X0},{y + Y0}"
        if int(sid) in state_name:
            sn[keys[int(sid)]] = state_name[int(sid)]
    for q in pids:
        wP[p == q] = pc[int(q)]
    for nm, arr in (("Provinces", wP), ("States", wS), ("Strategic Regions", wR)):
        lay = L[nm][Y0:Y1, X0:X1]
        pdn_tools.put(lay, arr, m)
        lay[m, 3] = 255
    for nm in ("Necessary States", "Necessary Provinces"):
        L[nm][Y0:Y1, X0:X1][m] = 0
    line = boundary(u, m)
    L["Necessary States"][Y0:Y1, X0:X1][line] = (0, 0, 0, 255)
    pdn_tools.save(names, L)
    json.dump(dict(sorted(sn.items(), key=lambda kv: (int(kv[0].split(",")[1]), int(kv[0].split(",")[0])))),
              open(NAMES, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"names": {k: [state_name.get(s, f"#{s}") for s in v] for k, v in remap.items()},
               "keys": keys, "unnamed": [int(s) for s in sids if int(s) not in state_name]},
              open(WORK / "remap.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"wrote the layers; {len(state_name)} of {len(sids)} states named; work/fief_states/remap.json")


if __name__ == "__main__":
    main()
