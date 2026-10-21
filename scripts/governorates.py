"""A nation's governorates (Rouental's, source/governorates_ROU.json): which province and state lies in which.

    python3 scripts/governorates.py [TAG]            # after a build: each governorate's states, and the states in none
    python3 scripts/governorates.py [TAG] --apply    # their strategic regions on the .pdn, and the regions' names

The governorates are the patches of the fief map's Rough Governorates layer (source/Rouental Fiefs.pdn, read onto the
game map with the file's fit, as fief_states.py found it), until the author draws its Governorate Lines (2026-10-21:
"Eventually I will get around to the Governorate Lines, but I don't have the time quite yet"). Each province is in the
patch most of its land lies on; a province off every patch takes its state's, or else its neighbours'. The names are
the file's, each by a game pixel inside its patch; patches of one name are one governorate (Terres Séparées, three);
the unnamed are numbered west to east.

Shown as the strategic regions (author, 2026-10-21: "for now they should be the strategic regions, and lines on the
state panels"): --apply paints each of the nation's states, in the governorate most of its land lies in, in that
governorate's region on the Strategic Regions layer (a colour of its own, kept in the file's "regions"; never blue), and
names the region after it in source/region_names.json. A governorate in the file's "split" has several regions instead,
each of states of its own and of whole nations beside it (2026-10-21: Terres Séparées, South and North Montvallée with
the Association's Hollier, Evriches, Seigne, Selgrave, Lustiana and Lanzerac). A state in no governorate keeps its
region. --apply also writes each state's governorate ("states", by its key in source/state_names.json), which the build
reads for the state panel's line (build_mod.state_lines); run it again after states change. The governorates "will
eventually affect play. They'll hook into the levy system" (the author).
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

GOV_LAYER = "Rough Governorates"
GOV_MIN = 20000            # fief map px: smaller patches of the layer are paint left over, not governorates
SEED = 2026_10_21          # the regions' colours


def spec_path(tag):
    return ROOT / f"source/governorates_{tag}.json"


def patches(tag):
    """(the file, the fief map's patches numbered from 1, patch(x, y): the patch most of game pixel (x, y) lies on)"""
    import fief_states as FS
    spec = json.loads(spec_path(tag).read_text(encoding="utf-8"))
    cache = FS.WORK / "fiefmap"
    names = (cache / "layers.txt").read_text().splitlines() if (cache / "layers.txt").exists() else []
    if GOV_LAYER in names and (cache / f"layer{names.index(GOV_LAYER)}.npy").exists():
        rough = np.load(cache / f"layer{names.index(GOV_LAYER)}.npy")
    else:
        rough = FS.read_fief_map(ROOT / spec["fief_map"])[GOV_LAYER]
    lab = FS.components(rough)
    small = np.bincount(lab.ravel()) < GOV_MIN
    small[0] = True
    lab[small[lab]] = 0
    s, ox, oy = spec["fit"]
    H_, W_ = lab.shape

    def patch(x, y):
        x0, x1 = int((x - ox) * s), int((x + 1 - ox) * s)
        y0, y1 = int((y - oy) * s), int((y + 1 - oy) * s)
        if x1 <= 0 or y1 <= 0 or x0 >= W_ or y0 >= H_:
            return 0
        v = lab[max(y0, 0):y1, max(x0, 0):x1].ravel()
        v = v[v > 0]
        return int(np.bincount(v).argmax()) if len(v) else 0
    return spec, lab, patch


def of_provinces(tag, prov, mine, state_of):
    """({province: its governorate's number in the list, -1 for none}, [{i, name, named, n}]), the list west to east"""
    spec, lab, patch = patches(tag)
    of = {}
    boxes = ndi.find_objects(prov + 1)
    for q in mine:
        sl = boxes[q]
        ys, xs = np.nonzero(prov[sl] == q)
        c = Counter(patch(x + sl[1].start, y + sl[0].start) for y, x in zip(ys[::2], xs[::2]))
        c.pop(0, None)
        of[q] = c.most_common(1)[0][0] if c else 0
    by_state = {}
    for q in mine:
        if of[q]:
            by_state.setdefault(int(state_of[q]), Counter())[of[q]] += 1
    for q in mine:   # off every patch: the state's governorate
        if not of[q] and int(state_of[q]) in by_state:
            of[q] = by_state[int(state_of[q])].most_common(1)[0][0]
    left = [q for q in mine if not of[q]]
    for _ in range(20):   # else the neighbours' (the province's pixels next to it)
        if not left:
            break
        for q in left:
            sl = boxes[q]
            sl = np.s_[max(sl[0].start - 1, 0):sl[0].stop + 1, max(sl[1].start - 1, 0):sl[1].stop + 1]
            m = prov[sl] == q
            ring = prov[sl][ndi.binary_dilation(m) & ~m]
            c = Counter(of.get(int(r), 0) for r in ring if r >= 0)
            c.pop(0, None)
            if c:
                of[q] = c.most_common(1)[0][0]
        left = [q for q in left if not of[q]]
    named = {}
    for k, n in spec["names"].items():
        x, y = map(int, k.split(","))
        g = patch(x, y)
        if not g:
            raise SystemExit(f"governorates_{tag}.json: {n} at ({x}, {y}) is on no patch of {GOV_LAYER}")
        if g in named and named[g] != n:
            raise SystemExit(f"governorates_{tag}.json: {named[g]} and {n} are on the same patch")
        named[g] = n
    used = sorted({g for g in of.values() if g})
    sub, mid = lab[::4, ::4], {}
    for g in used:
        xs = np.nonzero(sub == g)[1]
        mid[g] = xs.mean() if len(xs) else 0
    k, name_of = 0, {}
    for g in sorted(used, key=lambda g: mid[g]):
        if g not in named:
            k += 1
        name_of[g] = named.get(g, f"Governorate {k}")
    out, index = [], {}
    for g in sorted(used, key=lambda g: mid[g]):   # one entry a name, where its westernmost patch is
        if name_of[g] not in index:
            index[name_of[g]] = len(out)
            out.append(dict(i=len(out), name=name_of[g], named=g in named, n=0))
    res = {q: index[name_of[of[q]]] if of[q] else -1 for q in mine}
    for q in mine:
        if res[q] >= 0:
            out[res[q]]["n"] += 1
    return res, out


def load_build(tag):
    """(prov, state_of, size, regions.json, the nation's provinces, the build's owner of each state)"""
    import atlas_export as AE
    p = np.load(ROOT / "work/provinces.npz")
    reg = np.load(ROOT / "work/regions.npz")
    rj = json.load(open(ROOT / "work/regions.json", encoding="utf-8"))
    hist = AE.built_states()
    owner = [hist[s]["owner"] if s in hist else rj["owners"][s] for s in range(len(rj["states"]))]
    mine = sorted(int(q) for s, g in enumerate(rj["states"]) if owner[s] == tag for q in g)
    return p["prov"], reg["state_of"], reg["size"], rj, mine, owner


def of_states(tag):
    """({state id: governorate name}, the governorates' list) of the nation's states, each in the governorate most
    of its land is in; a state in none is left out"""
    prov, state_of, size, rj, mine, owner = load_build(tag)
    of, govs = of_provinces(tag, prov, mine, state_of)
    votes = {}
    for q in mine:
        if of[q] >= 0:
            votes.setdefault(int(state_of[q]), Counter())[of[q]] += int(size[q])
    return {s: govs[c.most_common(1)[0][0]]["name"] for s, c in votes.items()}, govs


def state_name_of(rj):
    """{state id: its name} from source/state_names.json (by a pixel inside it)"""
    prov = np.load(ROOT / "work/provinces.npz")["prov"]
    state_of = np.load(ROOT / "work/regions.npz")["state_of"]
    names = json.loads((ROOT / "source/state_names.json").read_text(encoding="utf-8"))
    out = {}
    for k, n in names.items():
        x, y = map(int, k.split(","))
        q = int(prov[y, x])
        if q >= 0:
            out[int(state_of[q])] = n
    return out


def report(tag):
    st, govs = of_states(tag)
    prov, state_of, size, rj, mine, owner = load_build(tag)
    names = state_name_of(rj)
    for g in govs:
        ss = sorted(names.get(s, f"#{s}") for s, n in st.items() if n == g["name"])
        print(f"{g['name']} ({len(ss)} states): {', '.join(ss)}")
    none = sorted(names.get(s, f"#{s}") for s in range(len(owner)) if owner[s] == tag and s not in st)
    print(f"in no governorate: {', '.join(none) or 'none'}")


def apply(tag):
    import pdn_tools
    st, govs = of_states(tag)
    prov, state_of, size, rj, mine, owner = load_build(tag)
    spec = json.loads(spec_path(tag).read_text(encoding="utf-8"))
    names = state_name_of(rj)
    # a governorate's region, or the regions its "split" gives it: each a list of the nation's state names and of
    # whole nations (tags) around it (2026-10-21, the author: "instead of the Severed Territories in the east being a
    # weird disconnected region, it should instead be two regions. South Montvallée should encompass Hollier, Evriches,
    # Seigne, Serpette, and Chirac. North Montvallée should encompass Selgrave, Lustiana, Lanzerac, Moelle, Maieul,
    # Serieux, and Petit Selgrave")
    region_of = {s: g for s, g in st.items()}
    order = []
    for g in govs:
        parts = spec.get("split", {}).get(g["name"])
        if not parts:
            order.append(g["name"])
            continue
        mine_g = {s for s, n in st.items() if n == g["name"]}
        placed = {}
        for region, members in parts.items():
            order.append(region)
            for m in members:
                if re.fullmatch(r"[A-Z][A-Z0-9]{2}", m):
                    ss = [s for s in range(len(owner)) if owner[s] == m]
                else:
                    ss = [s for s in mine_g if names.get(s) == m]
                if not ss:
                    raise SystemExit(f"governorates_{tag}.json: {m} ({region}) names no state of {g['name']} or nation")
                for s in ss:
                    if s in placed:
                        raise SystemExit(f"governorates_{tag}.json: {names.get(s, s)} is in {placed[s]} and {region}")
                    placed[s] = region
        left = sorted(names.get(s, f"#{s}") for s in mine_g - set(placed))
        if left:
            raise SystemExit(f"governorates_{tag}.json: {g['name']}'s {', '.join(left)} in none of its regions")
        region_of.update(placed)
    names_, L = pdn_tools.load()
    R = pdn_tools.code(L["Strategic Regions"][..., :3])
    regions = spec.get("regions", {})
    others = set(np.unique(R).tolist()) - {int(c, 16) for c in regions.values()}
    fresh = iter(pdn_tools.palette(len(order), False, SEED, others | {int(c, 16) for c in regions.values()}))
    for r in order:
        if r not in regions:
            regions[r] = f"{next(fresh):06x}"
    gone = {c for r, c in regions.items() if r not in order}
    regions = {r: regions[r] for r in order}     # the list's order; gone names dropped
    lut = np.full(int(prov.max()) + 2, -1, np.int64)
    for s, r in region_of.items():
        for q in rj["states"][s]:
            lut[q] = int(regions[r], 16)
    paint = lut[prov]
    m = paint >= 0
    changed = int((R[m] != paint[m]).sum())
    pdn_tools.put(L["Strategic Regions"], paint, m)
    pdn_tools.save(names_, L)
    spec["regions"] = regions
    # each state's governorate, by its key in source/state_names.json: the state panel's line (build_mod.state_lines),
    # apart from the regions since a split governorate has several
    keys = {}
    for k in json.loads((ROOT / "source/state_names.json").read_text(encoding="utf-8")):
        x, y = map(int, k.split(","))
        q = int(prov[y, x])
        if q >= 0 and int(state_of[q]) in st:
            keys[k] = st[int(state_of[q])]
    spec["states"] = dict(sorted(keys.items(), key=lambda kv: (int(kv[0].split(",")[1]), int(kv[0].split(",")[0]))))
    spec_path(tag).write_text(json.dumps(spec, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    rn_path = ROOT / "source/region_names.json"
    rn = json.loads(rn_path.read_text(encoding="utf-8"))
    for c in gone:
        rn.pop(c, None)
    for name, col in regions.items():
        rn[col] = name
    rn_path.write_text(json.dumps(rn, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(regions)} governorates' regions painted ({changed} px changed), {len(keys)} states' governorates; "
          f"names in {rn_path.name}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    tag = args[0] if args else "ROU"
    apply(tag) if "--apply" in sys.argv else report(tag)
