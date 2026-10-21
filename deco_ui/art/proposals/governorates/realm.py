"""Rouental's governorates as the build has them, for the mockups in this folder: every state's pixels (the build's own
map, so the borders are the game's exactly), its governorate (source/governorates_ROU.json), name, manpower, vassals (the
author's fiefs inside it, from the fief map: work/fief_states/plan.npz) and whether it is a Royal Fief; and the map as
SVG, its fills and borders traced along the map's pixel edges.

The sample values (governors, loyalty, the estates' attitudes, levy quality) are placeholders made here, not the game's.
"""
import functools
import glob
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
MOD = os.path.join(REPO, "build", "valsora_test")
sys.path.insert(0, os.path.join(REPO, "scripts"))
import cultures  # noqa: E402
import nations  # noqa: E402

TAG = "ROU"
MARGIN = 6


def h(s, n):
    """a fixed number 0..n-1 from a name: the sample values stay the same from run to run"""
    return int(hashlib.sha1(s.encode()).hexdigest(), 16) % n


@functools.lru_cache(maxsize=None)
def realm():
    img = np.array(Image.open(os.path.join(MOD, "map", "provinces.bmp")).convert("RGB")).astype(np.int64)
    key = (img[..., 0] << 16) | (img[..., 1] << 8) | img[..., 2]
    col = {}
    for ln in open(os.path.join(MOD, "map", "definition.csv")).read().splitlines()[1:]:
        f = ln.split(";")
        col[(int(f[1]) << 16) | (int(f[2]) << 8) | int(f[3])] = int(f[0])
    u, inv = np.unique(key, return_inverse=True)
    prov = np.array([col.get(int(c), 0) for c in u])[inv].reshape(key.shape)
    loc = {}
    for f in glob.glob(os.path.join(MOD, "localisation", "english", "*.yml")):
        for m in re.finditer(r'^\s*VAL_STATE_(\d+):\d*\s*"([^"]*)"', open(f, encoding="utf-8-sig").read(), re.M):
            loc[int(m.group(1))] = m.group(2)
    st = {}
    p2s = np.zeros(prov.max() + 1, np.int32)
    for f in glob.glob(os.path.join(MOD, "history", "states", "*.txt")):
        t = open(f, encoding="utf-8-sig").read()
        sid = int(re.search(r"\bid\s*=\s*(\d+)", t).group(1))
        ps = [int(p) for p in re.search(r"provinces\s*=\s*\{([^}]*)\}", t).group(1).split()]
        p2s[ps] = sid
        st[sid] = dict(owner=re.search(r"\bowner\s*=\s*(\w+)", t).group(1), name=loc.get(sid, f"State {sid}"),
                       manpower=int(re.search(r"\bmanpower\s*=\s*(\d+)", t).group(1)), provinces=len(ps))
    S = p2s[prov]
    gfile = json.load(open(os.path.join(REPO, "source", "governorates_ROU.json"), encoding="utf-8"))
    gov = {}
    for k, g in gfile["states"].items():
        x, y = map(int, k.split(","))
        gov[int(S[y, x])] = g
    royal = {sid for sid, s in st.items() if s["owner"] == TAG and s["name"] in nations.ROYAL_FIEFS}
    ys, xs = np.nonzero(np.isin(S, list(gov)))
    box = (xs.min() - MARGIN, ys.min() - MARGIN, xs.max() + 1 + MARGIN, ys.max() + 1 + MARGIN)
    x0, y0, x1, y1 = box
    crop = S[y0:y1, x0:x1].copy()
    # the vassals: the author's fiefs inside each state (the fief map's numbering, read onto the game map)
    plan = np.load(os.path.join(REPO, "work", "fief_states", "plan.npz"))
    fx0, fy0, fx1, fy1 = plan["box"]
    fiefs = np.zeros_like(S)
    fiefs[fy0:fy1, fx0:fx1] = plan["fiefs"]
    vassals = {}
    for sid in gov:
        ids = fiefs[S == sid]
        vassals[sid] = len(set(ids[ids > 0].tolist()))
    # each governorate's seal: the point deepest inside its largest piece
    seal = {}
    for g in set(gov.values()):
        m = np.isin(crop, [s for s, gg in gov.items() if gg == g])
        lab, n = ndi.label(m)
        big = np.bincount(lab.ravel())[1:].argmax() + 1
        d = ndi.distance_transform_edt(lab == big)
        yy, xx = np.unravel_index(d.argmax(), d.shape)
        seal[g] = (xx + .5, yy + .5, float(d.max()))
    return dict(S=crop, box=box, st=st, gov=gov, royal=royal, vassals=vassals, seal=seal)


# ---------------------------------------------------------------- the sample values (placeholders)
BANDS = [(80, "Devoted", "#4C8A6C"), (60, "Loyal", "#71905A"), (40, "Wary", "#B39143"), (20, "Restive", "#AE6440"),
         (0, "Defiant", "#8E3A33")]
# the estates' attitudes: the author's four (leal, grasping, belligerent, quarrelsome) and Claude's suggestions
ATTITUDES = [
    ("Leal", "True to the Crown: gives levies readily and asks little in return."),
    ("Grasping", "Wants privileges and coin: grants please it more, demands for levies cost more loyalty."),
    ("Belligerent", "Spoiling for a fight: levies come easily in war, it grows restless in a long peace."),
    ("Quarrelsome", "Split into feuding factions: slow to agree, and any action may go astray."),
    ("Pious", "Led by its churchmen: moved by the Faithful and by the Crown's piety."),
    ("Proud", "Jealous of its old rights: inspectors and new governors are resented."),
    ("Mercantile", "Thinks in trade: pays coin sooner than it sends men."),
    ("Timorous", "Fearful of the Crown: yields to pressure, but its levies are poor."),
]
LEVY = ["Rabble", "Militia", "Drilled", "Seasoned", "Veteran"]
FIRST = ["Aubert", "Bérenger", "Clémence", "Éloïse", "Fulbert", "Gaspard", "Hélène", "Isaure", "Josselin", "Lothaire",
         "Naudin", "Odile", "Perrine", "Raoul", "Sibylle", "Thibault", "Ursule", "Valéran", "Yolande", "Amaury",
         "Blanche", "Côme", "Gilles", "Hugues", "Aliénor", "Enguerrand"]


def band(v):
    return next(b for b in BANDS if v >= b[0])


@functools.lru_cache(maxsize=None)
def governorates():
    R = realm()
    out = {}
    names = sorted(set(R["gov"].values()))
    for i, g in enumerate(names):
        states = sorted((s for s, gg in R["gov"].items() if gg == g), key=lambda s: -R["st"][s]["manpower"])
        seat = states[0]
        loyal = 86 if g == "Couronneterre" else 18 + h(g, 70)
        out[g] = dict(states=states, seat=seat, loyalty=loyal, attitude=ATTITUDES[(i * 3 + 1) % len(ATTITUDES)],
                      governor=f"{FIRST[i % len(FIRST)]} {cultures.noble(R['st'][seat]['name'])}",
                      manpower=sum(R["st"][s]["manpower"] for s in states))
    return out


def levy(sid):
    R = realm()
    if sid in R["royal"]:
        return 4
    return h(R["st"][sid]["name"] + "levy", 5)


# ---------------------------------------------------------------- the map as SVG, along the map's pixel edges
def _runs(mask_fn, S):
    """horizontal runs of the pixels each key covers: key -> path data of unit-high rectangles"""
    out = defaultdict(list)
    H, W = S.shape
    for y in range(H):
        row = [mask_fn(int(v)) for v in S[y]]
        x = 0
        while x < W:
            k = row[x]
            e = x
            while e < W and row[e] == k:
                e += 1
            if k is not None:
                out[k].append(f"M{x} {y}h{e - x}v1h{x - e}z")
            x = e
    return {k: "".join(v) for k, v in out.items()}


def _edges(cls_fn, S):
    """the borders between pixels, merged into straight runs: class -> path data"""
    out = defaultdict(list)
    H, W = S.shape
    # vertical edges at x (between column x-1 and x), runs down the rows
    for x in range(1, W):
        a, b = S[:, x - 1], S[:, x]
        cl = [cls_fn(int(p), int(q)) if p != q else None for p, q in zip(a, b)]
        y = 0
        while y < H:
            k = cl[y]
            e = y
            while e < H and cl[e] == k:
                e += 1
            if k is not None:
                out[k].append(f"M{x} {y}V{e}")
            y = e
    for y in range(1, H):
        a, b = S[y - 1], S[y]
        cl = [cls_fn(int(p), int(q)) if p != q else None for p, q in zip(a, b)]
        x = 0
        while x < W:
            k = cl[x]
            e = x
            while e < W and cl[e] == k:
                e += 1
            if k is not None:
                out[k].append(f"M{x} {y}H{e}")
            x = e
    return {k: "".join(v) for k, v in out.items()}


def map_svg(scale, select_gov=None, select_state=None, crown=False):
    """the realm at `scale` screen px a map px: governorates by loyalty, the Royal Fiefs the Crown's gilt, the rest of
    the land dim; state, governorate and coast lines; the selection outlined; each governorate's seal"""
    R = realm()
    S, st, gov, royal = R["S"], R["st"], R["gov"], R["royal"]
    G = governorates()
    H, W = S.shape

    def fill_key(s):
        if s == 0:
            return None
        if s in royal:
            return "royal"
        if s in gov:
            return "g:" + gov[s]
        return "other"

    def edge_cls(p, q):
        ip, iq = p in gov, q in gov
        if ip and iq:
            if gov[p] != gov[q]:
                return "gov"
            return "state"
        if ip or iq:
            return "coast" if (p == 0 or q == 0 or st.get(p if not ip else q, {}).get("owner") != TAG) else "coast"
        if p == 0 or q == 0:
            return "shore"
        return "foreign" if st[p]["owner"] != st[q]["owner"] else None

    fills = _runs(fill_key, S)
    edges = _edges(edge_cls, S)
    sel = set()
    if select_gov:
        sel = set(G[select_gov]["states"])
    if crown:
        sel = set(royal)
    out = [f'<svg width="{W * scale:.0f}" height="{H * scale:.0f}" viewBox="0 0 {W} {H}" style="display:block">',
           '<defs><pattern id="crown" width="3" height="3" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
           '<rect width="3" height="3" fill="#6E5626"/><rect width="1.1" height="3" fill="#C9A55A"/></pattern>'
           '<filter id="glow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation=".8"/></filter></defs>',
           f'<rect width="{W}" height="{H}" fill="#0B1317"/>']
    if "other" in fills:
        out.append(f'<path d="{fills["other"]}" fill="#1B262C"/>')
    for k, d in fills.items():
        if k.startswith("g:"):
            g = k[2:]
            out.append(f'<path d="{d}" fill="{band(G[g]["loyalty"])[2]}" fill-opacity="{1 if (not sel or select_gov == g) else .55}"/>')
    if "royal" in fills:
        out.append(f'<path d="{fills["royal"]}" fill="url(#crown)" fill-opacity="{1 if (crown or not sel) else .6}"/>')
    if select_state:
        d = _runs(lambda s: 1 if s == select_state else None, S).get(1, "")
        out.append(f'<path d="{d}" fill="#F1DC9C" fill-opacity=".35"/>')
    style = 'fill="none" vector-effect="non-scaling-stroke" stroke-linecap="square"'
    for k, colour, w in (("foreign", "rgba(201,165,90,.22)", .8), ("shore", "rgba(201,165,90,.30)", .8),
                         ("state", "rgba(8,12,15,.55)", .7), ("gov", "rgba(227,199,126,.80)", 1.1),
                         ("coast", "#E3C77E", 1.4)):
        if k in edges:
            out.append(f'<path d="{edges[k]}" stroke="{colour}" stroke-width="{w}" {style}/>')
    if sel:
        d = _edges(lambda p, q: 1 if ((p in sel) != (q in sel)) else None, S).get(1, "")
        out.append(f'<path d="{d}" stroke="#F8E7B0" stroke-width="2.6" {style} opacity=".45" filter="url(#glow)"/>')
        out.append(f'<path d="{d}" stroke="#F8E7B0" stroke-width="1.6" {style}/>')
    # the seals: an octagon in each governorate's colour; the Crown's a gilt one on its capital
    r = 4.6 / scale
    for g, (sx, sy, depth) in R["seal"].items():
        c = band(G[g]["loyalty"])[2]
        pts = " ".join(f"{sx + r * np.cos(np.radians(22.5 + 45 * i)):.2f},{sy + r * np.sin(np.radians(22.5 + 45 * i)):.2f}"
                       for i in range(8))
        lit = select_gov == g
        out.append(f'<polygon points="{pts}" fill="{c}" stroke="{"#FFF2C4" if lit else "#E3C77E"}" '
                   f'stroke-width="{1.4 if lit else 1}" vector-effect="non-scaling-stroke"/>')
    out.append("</svg>")
    return "".join(out)


if __name__ == "__main__":
    R = realm()
    print("box", R["box"], "size", R["S"].shape[::-1], "states", len(R["gov"]), "royal", sorted(R["st"][s]["name"] for s in R["royal"]))
    for g, v in sorted(governorates().items()):
        print(g, len(v["states"]), v["loyalty"], v["attitude"][0], v["governor"], v["manpower"])
