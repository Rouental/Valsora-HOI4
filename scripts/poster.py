"""An art deco world map poster of Valsora in 2036. NOT part of the mod: nothing the build
uses reads it, and it only reads the last build.

    python3 scripts/poster.py              # dist/posters/: the print, a preview, four close-ups
    python3 scripts/poster.py --draft 0.3  # the same at 30 % size, quickly, into the scratch folder

The world as a vintage atlas plate in the style of the Valsora Deco UI (lacquer and ivory, gilt
hairlines, stepped corners, sunbursts, Federo capitals): shaded relief (the terrain test's own
relief, work/terrain_test/, when it is there; else the build's heightmap), the nations in muted
versions of their map colours, country borders crisp and state borders faint, coasts with a fine
double line and water lining, rivers, each nation's name inside its land (or beside it, with a
leader line), the oceans' and continents' names, the capitals, and a frame with a title cartouche,
a compass rose, a scale bar, a legend and every nation's flag.

Read from (all read-only): work/world.npz, work/provinces.npz, work/regions.npz,
work/terrain_test/relief.npy, build/valsora_test (states, countries, colours, localisation,
strategic regions, placeholder flags), dist/countries.csv, source/flags/, source/city_names.json,
source/region_names.json, deco_ui/source_fonts/ (OFL fonts, used to render text only).
See docs/POSTER.md.
"""
import argparse
import csv
import json
import math
import re
import sys
import time
import unicodedata
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parent.parent
MOD = ROOT / "build/valsora_test"
WORK = ROOT / "work"
OUT = ROOT / "dist/posters"
FONTS = ROOT / "deco_ui/source_fonts"
Image.MAX_IMAGE_PIXELS = None

MAP_W, MAP_H = 5120, 2560
FULL_W = 9600          # the print's width
SCALE = 1.75           # print px per map px: the map plate is 8960 x 4480
GREAT_POWERS = {"KRI": "Monarchist", "KPF": "Authoritarian", "SRK": "Communist", "FRX": "Democratic"}
CONTINENT_NAMES = ["Nonscio", "Araseos", "Aislada", "Solitas", "Yastreovakia", "Usnistan", "Orientalis"]
IDEOLOGY_KEYS = {"Democratic": "democratic", "Communist": "communism", "Authoritarian": "fascism",
                 "Monarchist": "neutrality", "Theocratic": "theocracy"}
# Valsora taken as the size of the Earth: 5,120 map px round the equator (a guess: docs/POSTER.md)
KM_PER_PX = 40075.0 / MAP_W
KM_PER_LEAGUE = 5.556   # the nautical league, three nautical miles

# the Deco UI's palette (deco_ui/CLAUDE.md section 5)
LACQUER = (14, 21, 25)
LACQUER_2 = (20, 30, 36)
GILT = (227, 199, 126)
GILT_RULE = (201, 165, 90)
GILT_HI = (241, 220, 156)
BRONZE = (139, 106, 44)
CREAM = (244, 236, 217)
CREAM_2 = (232, 223, 200)
LABEL = (183, 166, 128)
IVORY = (238, 230, 210)
INK = (34, 33, 30)
RIVER = (64, 108, 146)
PALETTES = {
    # the sea of the plate, deeper offshore; its water lining; the coast's outer line
    "pale": dict(sea=(198, 212, 206), deep=(178, 197, 193), lining=(62, 98, 104), lining_a=0.55,
                 outer=INK, outer_a=0.85, ocean_ink=(52, 86, 92), grat=(90, 120, 124)),
    "lacquer": dict(sea=(31, 52, 58), deep=(18, 32, 38), lining=(201, 165, 90), lining_a=0.62,
                    outer=(227, 199, 126), outer_a=0.9, ocean_ink=(220, 196, 132), grat=(201, 165, 90)),
}
PAL = PALETTES["lacquer"]

GILT_STOPS = [(0.0, (255, 246, 214)), (0.38, (240, 213, 142)), (0.56, (180, 138, 60)),
              (0.74, (231, 201, 121)), (1.0, (251, 235, 190))]   # the menu title's .gilt


def log(msg, t0=[time.time()]):
    print(f"[{time.time() - t0[0]:6.1f}s] {msg}", flush=True)


# ------------------------------------------------------------------------------------ data
def load_loc():
    out = {}
    for f in (MOD / "localisation").rglob("*english*.yml"):
        for k, v in re.findall(r'^\s*([\w.]+):\d*\s+"(.*)"\s*$', f.read_text(encoding="utf-8-sig"), re.M):
            out.setdefault(k, v)
    return out


def load_data():
    d = {}
    w = np.load(WORK / "world.npz")
    d["kind"], d["cont"], d["rivers"], d["height"] = w["kind"], w["cont"], w["rivers"], w["height"]
    prov = np.load(WORK / "provinces.npz")["prov"]
    d["anchor"] = np.load(WORK / "regions.npz")["anchor"]          # (y, x) per province index
    loc = load_loc()
    d["loc"] = loc
    rows = [r for r in csv.DictReader(open(ROOT / "dist/countries.csv", encoding="utf-8"))
            if int(r["states"]) > 0]
    nations = sorted(rows, key=lambda r: r["tag"])
    d["nations"] = nations
    tag_i = {r["tag"]: i for i, r in enumerate(nations)}
    d["tag_i"] = tag_i
    n_prov = prov.max() + 2
    p_owner = np.full(n_prov, -1, np.int32)
    p_state = np.zeros(n_prov, np.int32)
    vps = []
    for f in (MOD / "history/states").glob("*.txt"):
        t = f.read_text(encoding="utf-8")
        sid = int(re.search(r"\bid = (\d+)", t).group(1))
        own = re.search(r"owner = (\w+)", t).group(1)
        ids = np.array(re.search(r"provinces = \{([^}]*)\}", t).group(1).split(), int)
        p_owner[ids] = tag_i.get(own, -1)
        p_state[ids] = sid
        for a, b in re.findall(r"victory_points = \{ (\d+) ([\d.]+) \}", t):
            vps.append((int(a), float(b), sid, own))
    pid = prov + 1
    owner = p_owner[pid]
    state = p_state[pid]
    kind = d["kind"]
    land = kind == 1
    stray = land & (owner < 0)
    if stray.any():  # land in no nation's state: the nearest nation's
        idx = ndi.distance_transform_edt(owner < 0, return_distances=False, return_indices=True)
        owner = np.where(stray, owner[idx[0], idx[1]], owner)
    owner[~land] = -1
    state[~land] = 0
    d["owner"], d["state"], d["prov"] = owner, state, prov
    colours = {}
    for tag, r, g, b in re.findall(r"^(\w+) = \{\s*color = rgb \{ (\d+) (\d+) (\d+) \}",
                                    (MOD / "common/countries/colors.txt").read_text(encoding="utf-8"), re.M):
        colours[tag] = (int(r), int(g), int(b))
    d["colour"] = np.array([colours.get(r["tag"], (150, 150, 150)) for r in nations], np.float32)
    caps = {}
    for f in (MOD / "history/countries").glob("*.txt"):
        m = re.search(r"^capital = (\d+)", f.read_text(encoding="utf-8"), re.M)
        if m:
            caps[f.name[:3]] = int(m.group(1))
    # cities: every victory point with a name of its own (not the build's "<Nation> 12 City")
    dots = {}
    dot_names = set()
    for k, name in json.loads((ROOT / "source/city_names.json").read_text(encoding="utf-8")).items():
        x, y = map(int, k.split(","))
        dots[int(prov[y, x]) + 1] = (x, y)
        dot_names.add(name)
    cities = []
    for pid_, val, sid, own in vps:
        name = loc.get(f"VICTORY_POINTS_{pid_}", "")
        y, x = d["anchor"][pid_ - 1]
        x, y = dots.get(pid_, (int(x), int(y)))
        capital = caps.get(own) == sid and val >= 10
        # the build names a victory point "<Nation> 12 City" or "<State> City" until it has one
        named = bool(name) and (name in dot_names or not name.endswith(" City"))
        if capital or named:
            cities.append(dict(name=name if named else "", x=x, y=y, capital=capital, tag=own))
    for i, c in enumerate(cities):
        c["i"] = i
    d["cities"] = cities
    # relief: the terrain test's own, else the build's heightmap
    rf = WORK / "terrain_test/relief.npy"
    if rf.exists():
        rel = np.load(rf).astype(np.float32)
        miss = land & (rel < 96)   # land drawn after the test was run
        if miss.any():
            idx = ndi.distance_transform_edt(~(land & ~miss), return_distances=False, return_indices=True)
            rel = np.where(miss, rel[idx[0], idx[1]], rel)
        d["relief_src"] = "terrain test"
    else:
        rel = d["height"].astype(np.float32)
        d["relief_src"] = "heightmap"
    d["relief"] = rel
    # the oceans: the sea regions' names, "<ocean> <n>", grouped
    reg_of = np.zeros(n_prov, np.int32)
    names = {}
    for f in (MOD / "map/strategicregions").glob("*.txt"):
        t = f.read_text(encoding="utf-8")
        rid = int(re.search(r"\bid = (\d+)", t).group(1))
        ids = np.array(re.search(r"provinces = \{([^}]*)\}", t).group(1).split(), int)
        reg_of[ids] = rid
        names[rid] = loc.get(f"VAL_REGION_{rid}", "")
    oceans = sorted({re.sub(r" \d+$", "", n) for rid, n in names.items() if "Region" not in n and n})
    o_of_reg = np.full(reg_of.max() + 1, -1, np.int16)
    for rid, n in names.items():
        o = re.sub(r" \d+$", "", n)
        if o in oceans:
            o_of_reg[rid] = oceans.index(o)
    ocean = o_of_reg[reg_of[pid]]
    ocean[kind != 0] = -1
    d["ocean"], d["ocean_names"] = ocean, oceans
    log(f"data: {len(nations)} nations, {len(cities)} cities, relief from the {d['relief_src']}, "
        f"{len(oceans)} oceans")
    return d


def crop_data(d, win):
    """Only a window of the map (map px), for quick full-size tests."""
    x0, y0, x1, y1 = win
    sl = np.s_[y0:y1, x0:x1]
    for k in ("kind", "cont", "rivers", "height", "owner", "state", "prov", "relief", "ocean"):
        d[k] = d[k][sl]
    d["cities"] = [dict(c, x=c["x"] - x0, y=c["y"] - y0) for c in d["cities"]
                   if x0 <= c["x"] < x1 and y0 <= c["y"] < y1]
    d["window"] = (x0, y0)
    return d


# ------------------------------------------------------------------------------- resampling
def _rows(a, s, n_out, off_in, off_out):
    Y = np.arange(n_out, dtype=np.float64) + off_out
    y = (Y + 0.5) / s - 0.5 - off_in
    i0 = np.floor(y).astype(np.int64)
    w = (y - i0).astype(np.float32)
    i0c = np.clip(i0, 0, a.shape[0] - 1)
    i1c = np.clip(i0 + 1, 0, a.shape[0] - 1)
    sh = (-1,) + (1,) * (a.ndim - 1)
    return a[i0c] * (1 - w).reshape(sh) + a[i1c] * w.reshape(sh)


def resample(a, s, y0=0, x0=0, oy=0, ox=0, hy=None, wx=None):
    """Bilinear: the poster pixels [oy, oy + hy) x [ox, ox + wx) from a map-resolution crop whose
    first pixel is map (y0, x0); poster pixel Y samples map y = (Y + 0.5) / s - 0.5."""
    a = a.astype(np.float32, copy=False)
    hy = hy if hy is not None else int(round(a.shape[0] * s))
    wx = wx if wx is not None else int(round(a.shape[1] * s))
    r = _rows(a, s, hy, y0, oy)
    r = np.swapaxes(r, 0, 1)
    r = _rows(r, s, wx, x0, ox)
    return np.ascontiguousarray(np.swapaxes(r, 0, 1))


def nearest(a, s, Hp, Wp):
    yi = np.minimum(((np.arange(Hp) + 0.5) / s).astype(np.int64), a.shape[0] - 1)
    xi = np.minimum(((np.arange(Wp) + 0.5) / s).astype(np.int64), a.shape[1] - 1)
    return a[yi][:, xi]


def line(dist, half):
    """Anti-aliased line intensity from a distance (px) to its centre line."""
    return np.clip(half + 0.5 - dist, 0, 1)


# --------------------------------------------------------------------------- colour helpers
def srgb_to_lab(c):
    c = np.asarray(c, np.float64) / 255
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    m = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ m.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def lab_to_srgb(lab):
    lab = np.asarray(lab, np.float64)
    fy = (lab[..., 0] + 16) / 116
    fx, fz = fy + lab[..., 1] / 500, fy - lab[..., 2] / 200
    f = np.stack([fx, fy, fz], -1)
    xyz = np.where(f > 0.2069, f ** 3, (f - 16 / 116) / 7.787) * np.array([0.95047, 1.0, 1.08883])
    m = np.array([[3.2406, -1.5372, -0.4986], [-0.9689, 1.8758, 0.0415], [0.0557, -0.2040, 1.0570]])
    c = np.clip(xyz @ m.T, 0, 1)
    c = np.where(c > 0.0031308, 1.055 * c ** (1 / 2.4) - 0.055, 12.92 * c)
    return np.clip(c * 255, 0, 255)


def muted(colours, light=(70, 87), chroma=0.32, warm=(3, 10)):
    """The map colours as an old atlas's washes: lightness squeezed into a pale band, chroma cut,
    a little warmth (towards the ivory paper) added."""
    lab = srgb_to_lab(colours)
    L = light[0] + (light[1] - light[0]) * np.clip(lab[:, 0] / 100, 0, 1)
    a = lab[:, 1] * chroma + warm[0] * 0.3
    b = lab[:, 2] * chroma + warm[1]
    return lab_to_srgb(np.stack([L, a, b], -1)).astype(np.float32)


def ribbon_colours(colours):
    lab = srgb_to_lab(colours)
    L = 50 + 0.32 * np.clip(lab[:, 0], 0, 100)
    return lab_to_srgb(np.stack([L, lab[:, 1] * 0.85, lab[:, 2] * 0.85 + 3], -1)).astype(np.float32)


# ---------------------------------------------------------------------------------- the map
def hillshade(h, az=315, alt=42, z=1.0):
    gy, gx = np.gradient(h)
    gx, gy = gx * z, gy * z
    a, e = math.radians(az), math.radians(alt)
    lx, ly, lz = math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)
    n = np.sqrt(gx ** 2 + gy ** 2 + 1)
    return (-gx * lx - gy * ly + lz) / n


def iso_labels(lab, labels, s, Hp, Wp, sigma, half, accumulate=False, keep=None):
    """For each label: its blurred indicator resampled to the poster, and the anti-aliased line
    where it crosses 0.5 (the label's outline, smooth, the same line from both sides of a shared
    border). Returns the max line intensity; with accumulate, also the sum of the fields, the max
    field and its label (the poster's own smooth label map)."""
    B = np.zeros((Hp, Wp), np.float32)
    if accumulate:
        S = np.zeros((Hp, Wp), np.float32)
        M = np.zeros((Hp, Wp), np.float32)
        A = np.zeros((Hp, Wp), np.int16)
    objs = ndi.find_objects(lab)
    pad = int(3 * sigma) + 3
    for l in labels:
        sl = objs[l - 1] if l - 1 < len(objs) else None
        if sl is None:
            continue
        y0, y1 = max(sl[0].start - pad, 0), min(sl[0].stop + pad, lab.shape[0])
        x0, x1 = max(sl[1].start - pad, 0), min(sl[1].stop + pad, lab.shape[1])
        m = (lab[y0:y1, x0:x1] == l).astype(np.float32)
        g = ndi.gaussian_filter(m, sigma)
        oy, ox = int(math.floor(y0 * s)), int(math.floor(x0 * s))
        hy, wx = min(int(math.ceil(y1 * s)), Hp) - oy, min(int(math.ceil(x1 * s)), Wp) - ox
        f = resample(g, s, y0, x0, oy, ox, hy, wx)
        box = np.s_[oy:oy + hy, ox:ox + wx]
        if keep is None or keep(l):
            gy, gx = np.gradient(f)
            gm = np.maximum(np.hypot(gx, gy), 1e-4)
            np.maximum(B[box], line(np.abs(f - 0.5) / gm, half), out=B[box])
        if accumulate:
            S[box] += f
            upd = f > M[box]
            M[box][upd] = f[upd]
            A[box][upd] = l
    if accumulate:
        return B, S, M, A
    return B


def render_map(d, s, Q):
    """The map plate at s print px per map px: RGB float32, and the poster's label map."""
    Hp, Wp = int(round(d["kind"].shape[0] * s)), int(round(d["kind"].shape[1] * s))
    kind, owner = d["kind"], d["owner"]
    n = len(d["nations"])
    # labels: 1 lake, 2 + i nation i; sea 0
    lab = np.zeros(kind.shape, np.int32)
    lab[kind == 2] = 1
    lab[owner >= 0] = owner[owner >= 0] + 2
    B, S, M, A = iso_labels(lab, range(1, n + 2), s, Hp, Wp, sigma=0.7, half=max(1.3 * Q, 0.45),
                            accumulate=True, keep=lambda l: l >= 2)
    log("map: nation outlines")
    # the land field is the nations' (lakes are water)
    f_lake = resample(ndi.gaussian_filter((kind == 2).astype(np.float32), 0.7), s, hy=Hp, wx=Wp)
    S_land = np.clip(S - f_lake, 0, 1)
    sea_f = 1 - S
    Lp = np.where(M > sea_f, A, 0).astype(np.int16)
    gy, gx = np.gradient(S_land)
    gm = np.maximum(np.hypot(gx, gy), 1e-3)
    sd = (S_land - 0.5) / gm               # signed distance to the coast, px (valid near it)
    del gx, gy, gm
    land_a = np.clip(0.5 + sd, 0, 1)
    coast = line(np.abs(sd), max(1.15 * Q, 0.45))   # the coast's main line
    # borders only between nations: fade out at the coast
    B *= np.clip((S_land - 0.62) / 0.25, 0, 1)
    water = sd < 0
    dw = ndi.distance_transform_edt(water).astype(np.float32)   # px from the nearest land
    log("map: coasts")

    # ---- land colour: muted washes, ribbons along the borders, relief
    tint = np.vstack([[IVORY, IVORY], muted(d["colour"])])        # index by label
    rib = np.vstack([[IVORY, IVORY], ribbon_colours(d["colour"])])
    Li = np.where(Lp >= 2, Lp, 0)
    rgb = tint[Li]                                                 # (Hp, Wp, 3)
    # ribbon: distance inside a nation from its edge (map res, any other label), resampled
    edge = np.zeros(lab.shape, bool)
    edge[:, 1:] |= lab[:, 1:] != lab[:, :-1]
    edge[:, :-1] |= lab[:, 1:] != lab[:, :-1]
    edge[1:] |= lab[1:] != lab[:-1]
    edge[:-1] |= lab[1:] != lab[:-1]
    din = ndi.distance_transform_edt(~edge).astype(np.float32)
    dinp = resample(din, s, hy=Hp, wx=Wp) * s
    rw = 16.0 * Q   # ribbon width, print px
    ra = 0.55 * np.clip(1 - dinp / rw, 0, 1) ** 1.6
    ra *= (Lp >= 2)
    rgb += (rib[Li] - rgb) * ra[..., None]
    del dinp, ra
    log("map: washes and ribbons")
    rel = d["relief"]
    # soft relief: the lowlands' noise calmed, the ranges kept; two lights, as an engraver's
    r1 = ndi.gaussian_filter(rel, 2.6)
    r2 = ndi.gaussian_filter(rel, 1.6)
    w_hi = np.clip((r1 - 104) / 30, 0, 1)
    rs = r1 * (1 - w_hi) + r2 * w_hi
    hs = 0.7 * hillshade(rs, 315, 40, z=0.45) + 0.3 * hillshade(rs, 260, 50, z=0.45)
    flat = 0.7 * math.sin(math.radians(40)) + 0.3 * math.sin(math.radians(50))
    amp = 0.45 + 0.9 * np.clip((r1 - 100) / 40, 0, 1)        # weak on the plains
    hsx = (hs - flat) * amp
    shade = resample(hsx, s, hy=Hp, wx=Wp)
    relp = resample(r1, s, hy=Hp, wx=Wp)
    # shadows toward a warm sepia, lights toward the paper: an engraved look, not plastic
    dark = np.clip(-shade * 1.25, 0, 0.42)
    light = np.clip(shade * 1.2, 0, 0.30)
    hi = np.clip((relp - 140) / 70, 0, 1)            # the high ranges paler, as on an old plate
    rgb += (np.array([246, 241, 228], np.float32) - rgb) * (0.28 * hi + light)[..., None]
    # shadows keep the wash's hue, a little warmer: darker, not greyer
    rgb *= (1 - dark[..., None] * np.array([0.50, 0.53, 0.58], np.float32))
    del shade, relp, hi, dark, light, hsx
    log("map: relief")

    # ---- the sea: pale, deeper away from the coasts, with water lining
    sea = np.empty_like(rgb)
    deep = np.clip(dw / (160 * s / 1.75), 0, 1)[..., None]
    sea[:] = np.array(PAL["sea"], np.float32)
    sea += (np.array(PAL["deep"], np.float32) - sea) * deep
    out = sea * (1 - land_a[..., None]) + rgb * land_a[..., None]
    del sea, rgb, deep
    ripple = np.zeros((Hp, Wp), np.float32)
    k = s / 1.75
    r0, sp, nr = 7.5 * k, 7.0 * k, 6
    for i in range(nr):
        r = r0 + sp * i * (1 + 0.12 * i)
        a = PAL["lining_a"] * (1 - i / nr) ** 1.3
        ripple = np.maximum(ripple, a * line(np.abs(dw - r), 0.55 * k + 0.1))
    second = line(np.abs(dw - 3.6 * k), 0.5 * k + 0.15) * water   # the coast's fine outer line
    out += (np.array(PAL["lining"], np.float32) - out) * (ripple * water)[..., None]
    out += (np.array(PAL["outer"], np.float32) - out) * (PAL["outer_a"] * second)[..., None]
    del ripple, second, dw
    log("map: water lining")

    # ---- rivers (blurred, re-sharpened: smooth, no staircase)
    rv = d["rivers"]
    riv = (rv < 254) & (kind == 1)
    code = np.where(riv, rv, 0)
    big = ndi.grey_dilation(code, size=3) >= 7
    for major, lo, hi_ in ((False, 0.30, 0.42), (True, 0.17, 0.28)):
        m = riv & (big if major else ~big)
        g = resample(ndi.gaussian_filter(m.astype(np.float32), 0.8), s, hy=Hp, wx=Wp)
        a = np.clip((g - lo) / (hi_ - lo), 0, 1) * land_a
        out += (np.array(RIVER, np.float32) - out) * (0.9 * a)[..., None]
    log("map: rivers")

    # ---- state borders: faint, inside a nation only
    st = d["state"]
    st_lab = np.zeros(st.shape, np.int32)
    ids, inv = np.unique(st, return_inverse=True)
    st_lab = inv.reshape(st.shape).astype(np.int32)   # 0 is "no state" (state id 0)
    Bs = iso_labels(st_lab, range(1, len(ids)), s, Hp, Wp, sigma=0.7, half=0.42 * k + 0.1)
    Bs *= np.clip((S_land - 0.62) / 0.25, 0, 1)
    out += (np.array(INK, np.float32) - out) * (0.17 * Bs)[..., None]
    del Bs
    log("map: state borders")
    out += (np.array(INK, np.float32) - out) * (0.92 * B)[..., None]
    out += (np.array(INK, np.float32) - out) * (0.92 * coast)[..., None]
    return dict(rgb=out, Lp=Lp, land_a=land_a, Hp=Hp, Wp=Wp)


# ------------------------------------------------------------------------------------- type
FACES = {
    "federo": (FONTS / "federo/Federo-Regular.ttf", None),
    "josefin": (FONTS / "josefinsans/JosefinSans[wght].ttf", "wght"),
    "josefin_i": (FONTS / "josefinsans/JosefinSans-Italic[wght].ttf", "wght"),
    "bodoni": (FONTS / "bodonimoda/BodoniModa[opsz,wght].ttf", "both"),
    "bodoni_i": (FONTS / "bodonimoda/BodoniModa-Italic[opsz,wght].ttf", "both"),
    "limelight": (FONTS / "limelight/Limelight-Regular.ttf", None),
}
REF = 200   # metrics are read at this size and scaled


@lru_cache(maxsize=None)
def font(face, size, wght=400):
    path, var = FACES[face]
    size = max(1, int(round(size)))
    f = ImageFont.truetype(str(path), size)
    if var == "wght":
        f.set_variation_by_axes([wght])
    elif var == "both":
        f.set_variation_by_axes([wght, min(max(size, 6), 96)])
    return f


@lru_cache(maxsize=None)
def charset(face):
    from fontTools.ttLib import TTFont
    return frozenset(TTFont(str(FACES[face][0])).getBestCmap())


def base_letter(ch):
    return unicodedata.normalize("NFD", ch)[0]


def subst(face, text):
    """The text as the face can measure it: letters it lacks become their base letters."""
    cs = charset(face)
    return "".join(c if ord(c) in cs or c == " " else base_letter(c) for c in text)


@lru_cache(maxsize=None)
def cap_h(face, wght=400):
    return -font(face, REF, wght).getbbox("H", anchor="ls")[1] / REF


@lru_cache(maxsize=None)
def x_positions(face, wght, text):
    """Each letter's start along the line at size REF, kerning kept (no tracking)."""
    f = font(face, REF, wght)
    t = subst(face, text)
    ws = tuple(f.getlength(c) for c in t)
    # a letter starts where the run up to it ends, less its own advance: the pair's kerning kept
    xs = tuple(f.getlength(t[:i + 1]) - ws[i] for i in range(len(t))) + (f.getlength(t),)
    return xs, ws


def measure(face, wght, text, size, track_em):
    xs, _ = x_positions(face, wght, text)
    return xs[-1] * size / REF + track_em * size * (len(text) - 1)


@lru_cache(maxsize=4096)
def glyph(face, wght, size, ch):
    """A letter as an L image, the middle of its advance at cap-height middle on the image's
    centre. Letters the face lacks are built from their base letter and the accent another
    letter carries (Federo has no Ś: S and the acute of Á)."""
    f = font(face, size, wght)
    side = int(size * 2.4) + 10
    c = side / 2
    ch_px = cap_h(face, wght) * size
    img = Image.new("L", (side, side), 0)
    dr = ImageDraw.Draw(img)
    if ord(ch) in charset(face) or ch == " ":
        dr.text((c, c + ch_px / 2), ch, font=f, fill=255, anchor="ms")
        return img, c
    base = base_letter(ch)
    dr.text((c, c + ch_px / 2), base, font=f, fill=255, anchor="ms")
    marks = unicodedata.normalize("NFD", ch)[1:]
    donor = {"́": "AÁ", "̀": "AÀ", "̂": "AÂ", "̈": "AÄ", "̌": "AÁ",
             "̃": "AÃ", "̧": "CÇ"}
    for m in marks:
        if m not in donor:
            continue
        b0, b1 = donor[m]
        if base.islower():
            b0, b1 = b0.lower(), b1.lower()
        if ord(b1) not in charset(face):
            continue
        a = Image.new("L", (side, side), 0)
        ImageDraw.Draw(a).text((c, c + ch_px / 2), b1, font=f, fill=255, anchor="ms")
        z = Image.new("L", (side, side), 0)
        ImageDraw.Draw(z).text((c, c + ch_px / 2), b0, font=f, fill=255, anchor="ms")
        acc = np.clip(np.asarray(a, np.int16) - np.asarray(z, np.int16), 0, 255)
        img = Image.fromarray(np.maximum(np.asarray(img), acc).astype(np.uint8))
    return img, c


def paste_max(layer, a, X, Y):
    h, w = a.shape
    H, W = layer.shape
    x0, y0, x1, y1 = max(X, 0), max(Y, 0), min(X + w, W), min(Y + h, H)
    if x1 <= x0 or y1 <= y0:
        return
    sub = a[y0 - Y:y1 - Y, x0 - X:x1 - X]
    np.maximum(layer[y0:y1, x0:x1], sub, out=layer[y0:y1, x0:x1])


class Curve:
    """A polyline (print px), walked by arc length."""

    def __init__(self, x, y):
        self.x, self.y = np.asarray(x, float), np.asarray(y, float)
        dx, dy = np.diff(self.x), np.diff(self.y)
        self.seg = np.maximum(np.hypot(dx, dy), 1e-9)
        self.arc = np.concatenate([[0], np.cumsum(self.seg)])
        ang = np.arctan2(dy, dx)
        self.ang = np.unwrap(ang)

    @property
    def length(self):
        return self.arc[-1]

    def at(self, s):
        s = np.clip(s, 0, self.arc[-1])
        i = int(np.clip(np.searchsorted(self.arc, s) - 1, 0, len(self.seg) - 1))
        t = (s - self.arc[i]) / self.seg[i]
        x = self.x[i] + t * (self.x[i + 1] - self.x[i])
        y = self.y[i] + t * (self.y[i + 1] - self.y[i])
        # the tangent, smoothed over a few segments
        j0, j1 = max(i - 2, 0), min(i + 3, len(self.ang))
        return x, y, float(np.mean(self.ang[j0:j1]))

    def offset(self, o):
        x, y = [], []
        for k in range(len(self.x)):
            i = min(k, len(self.ang) - 1)
            a = self.ang[max(i - 1, 0):i + 2].mean()
            x.append(self.x[k] - math.sin(a) * o)
            y.append(self.y[k] + math.cos(a) * o)
        return Curve(x, y)


def draw_run(layer, text, face, wght, size, track, path, s_mid, offset=0.0):
    """Letters along a path (all in print px of this render), centred at arc length s_mid, their
    cap-height middle offset along the normal (positive: below the line)."""
    if not text:
        return
    xs, ws = x_positions(face, wght, text)
    k = size / REF
    pos = [xs[i] * k + i * track for i in range(len(text))]
    total = xs[-1] * k + track * (len(text) - 1)
    s0 = s_mid - total / 2
    for i, ch in enumerate(text):
        if ch == " ":
            continue
        sc = s0 + pos[i] + ws[i] * k / 2
        px, py, ang = path.at(sc)
        px -= math.sin(ang) * offset
        py += math.cos(ang) * offset
        img, c = glyph(face, wght, int(round(size)), ch)
        fx, fy = px - math.floor(px), py - math.floor(py)
        rot = img.rotate(-math.degrees(ang), resample=Image.BICUBIC, center=(c, c),
                         translate=(fx - 0.5, fy - 0.5))
        paste_max(layer, np.asarray(rot, np.float32) / 255,
                  int(math.floor(px) - c + 0.5), int(math.floor(py) - c + 0.5))


def straight(x0, y0, ang, half_len):
    ca, sa = math.cos(ang), math.sin(ang)
    return Curve([x0 - ca * half_len, x0 + ca * half_len], [y0 - sa * half_len, y0 + sa * half_len])


def disk_mask(r):
    r = max(r, 0.5)
    n = int(math.ceil(r))
    yy, xx = np.mgrid[-n:n + 1, -n:n + 1]
    return (xx * xx + yy * yy) <= r * r


# --------------------------------------------------------------------------- label fitting
# all fitting is in map px, with type sizes in full-size print px (SCALE print px per map px):
# a draft lays out exactly as the print does
NATION = dict(face="federo", wght=400)
F_MIN, F_LEAD = 19, 23        # the smallest name inside a nation; the size of names beside one


def norm_angle(a):
    """Reading direction: left to right, or bottom to top when steep."""
    a = (a + math.pi) % (2 * math.pi) - math.pi
    if a > math.pi / 2:
        a -= math.pi
    elif a <= -math.pi / 2:
        a += math.pi
    if a > math.radians(80):      # steep and falling: read upwards instead
        a -= math.pi
    return a


class Shape:
    """A piece of land (or water) to fit a label in: its mask (a crop), inner distance, axes."""

    def __init__(self, mask, y0, x0, holes=None):
        self.y0, self.x0 = y0, x0
        m = mask if holes is None else mask & ~holes
        self.mask = m
        self.D = ndi.distance_transform_edt(np.pad(m, 1))[1:-1, 1:-1].astype(np.float32)
        ys, xs = np.nonzero(m)
        self.ok = len(ys) > 3
        if not self.ok:
            return
        w = self.D[ys, xs] + 0.5
        self.cx, self.cy = np.average(xs, weights=w), np.average(ys, weights=w)
        cov = np.cov(np.vstack([xs, ys]), aweights=w)
        ev, evec = np.linalg.eigh(cov)
        self.theta = norm_angle(math.atan2(evec[1, 1], evec[0, 1]))
        self.elong = math.sqrt(max(ev[1], 1e-6) / max(ev[0], 1e-6))
        k = int(np.argmax(self.D))
        self.py, self.px = np.unravel_index(k, self.D.shape)
        self.xs, self.ys, self.w = xs, ys, w
        # straight lines go through the deepest point and a few other deep ones
        from skimage.feature import peak_local_max
        md = max(4, int(0.12 * math.sqrt(len(xs))))
        pk = peak_local_max(self.D, min_distance=md, threshold_rel=0.45, num_peaks=6, exclude_border=False)
        self.anchors = [(self.px, self.py)] + [(int(x), int(y)) for y, x in pk
                                               if (int(x), int(y)) != (self.px, self.py)]
        ix, iy = int(round(self.cx)), int(round(self.cy))
        if 0 <= iy < m.shape[0] and 0 <= ix < m.shape[1] and m[iy, ix]:
            self.anchors.append((self.cx, self.cy))

    def paths(self, angles, curved=True):
        """Candidate centre lines: (sample xs, ys in crop px, angle at the middle, curved?)."""
        out = []
        for th in angles:
            c, s_ = math.cos(th), math.sin(th)
            u = (self.xs - self.cx) * c + (self.ys - self.cy) * s_
            v = -(self.xs - self.cx) * s_ + (self.ys - self.cy) * c
            umin, umax = u.min() - 2, u.max() + 2
            uu = np.arange(umin, umax + 0.5, 0.5)
            for ax_, ay_ in self.anchors:
                vp = -(ax_ - self.cx) * s_ + (ay_ - self.cy) * c
                out.append((uu, np.full_like(uu, vp), th, False))
            if curved and len(u) > 40:
                b = np.floor((u - umin) / 2).astype(int)
                order = np.lexsort((self.D[self.ys, self.xs], b))
                last = np.r_[b[order][1:] != b[order][:-1], True]
                sel = order[last]
                ub, vb, db = u[sel], v[sel], self.D[self.ys[sel], self.xs[sel]]
                keep = db >= 1.5
                if keep.sum() >= 5:
                    he = (umax - umin) / 2
                    wts = db[keep] ** 2
                    lin = np.polyfit(ub[keep], vb[keep], 1, w=np.sqrt(wts))
                    out.append((uu, np.polyval(lin, uu), th, False))
                    q = np.polyfit(ub[keep], vb[keep], 2, w=np.sqrt(wts))
                    amax = 0.22 / max(he, 1)
                    q[0] = float(np.clip(q[0], -amax, amax))
                    out.append((uu, np.polyval(q, uu), th, True))
        res = []
        for uu, vv, th, cur in out:
            c, s_ = math.cos(th), math.sin(th)
            x = self.cx + uu * c - vv * s_
            y = self.cy + uu * s_ + vv * c
            d = ndi.map_coordinates(self.D, [y, x], order=1, cval=0)
            seg = np.hypot(np.diff(x), np.diff(y))
            arc = np.r_[0, np.cumsum(seg)]
            # the middle's angle: the centre line's direction where the shape's centre projects
            res.append(dict(x=x, y=y, d=d, arc=arc, th=th, curved=cur))
        return res


def place_on(p, need_len, req, pref=None):
    """Where a label of this length (map px) fits with clearance req on centre line p: the arc
    position of its middle nearest pref (default: the line's point nearest the shape's centre),
    or None."""
    ok = p["d"] >= req
    if not ok.any():
        return None
    arc = p["arc"]
    if pref is None:
        pref = p.get("pref", arc[-1] / 2)
    best = None
    idx = np.flatnonzero(np.diff(np.r_[0, ok.astype(np.int8), 0]))
    for a, b in zip(idx[::2], idx[1::2]):
        lo, hi = arc[a] + need_len / 2, arc[b - 1] - need_len / 2
        if hi < lo:
            continue
        c = min(max(pref, lo), hi)
        if best is None or abs(c - pref) < abs(best - pref):
            best = c
    return best


def block(face, wght, lines, size, track_em, extra=0.0):
    """A label's size (full print px): length, half-height and each line's offset."""
    ch = cap_h(face, wght) * size
    gap = 0.55 * ch
    L = max(measure(face, wght, ln, size, track_em) for ln in lines)
    H = len(lines) * ch + (len(lines) - 1) * gap + extra
    offs = [-H / 2 + ch / 2 + i * (ch + gap) for i in range(len(lines))]
    return L, H / 2, offs, ch


def split2(name):
    words = name.split(" ")
    if len(words) < 2:
        return None
    best = None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        cost = abs(len(a) - len(b))
        if best is None or cost < best[0]:
            best = (cost, [a, b])
    return best[1]


def angle_factor(a):
    deg = abs(math.degrees(a))
    return 1 - 0.5 * (deg / 90) ** 1.2


def fit_label(shape, lines_opts, f_lo, f_hi, track0, track_max, spec, margin_k=0.22, extra_k=0.0,
              angles=None, curved=True, min_margin=3.0, clear=1.0):
    """The best label for a shape: biggest size first, then angle, then nearness to the middle.
    Returns dict(path, size, track, lines, offs) in crop map px, or None."""
    if not shape.ok:
        return None
    if angles is None:
        angles = {round(shape.theta, 4)}
        for deg in (0, 15, -15, 30, -30, 45, -45, 60, -60, -90):
            angles.add(round(norm_angle(math.radians(deg)), 4))
        angles = sorted(angles)
    cands = shape.paths(angles, curved)
    # each line's preference: the point nearest the shape's centre
    for p in cands:
        k = int(np.argmin((p["x"] - shape.cx) ** 2 + (p["y"] - shape.cy) ** 2))
        p["pref"] = p["arc"][k]
    face, wght = spec["face"], spec["wght"]
    best = None
    for lines in lines_opts:
        for p in cands:
            def fits(f, tr=track0, p=p, lines=lines):
                L, hh, offs, ch = block(face, wght, lines, f, tr, extra_k * cap_h(face, wght) * f)
                req = (clear * hh + margin_k * ch + min_margin) / SCALE
                return place_on(p, L / SCALE, req)
            if fits(f_lo) is None:
                continue
            lo, hi = f_lo, f_hi
            while hi - lo > 0.5:
                mid = (lo + hi) / 2
                if fits(mid) is not None:
                    lo = mid
                else:
                    hi = mid
            f = math.floor(lo * 2) / 2
            c = fits(f)
            if c is None:
                continue
            i = int(np.clip(np.searchsorted(p["arc"], c), 1, len(p["x"]) - 1))
            amid = math.atan2(p["y"][i] - p["y"][i - 1], p["x"][i] - p["x"][i - 1])
            score = f * angle_factor(norm_angle(amid)) * (0.96 if p["curved"] else 1.0)
            score *= (1.0 if len(lines) == 1 else 0.8)
            score -= 0.02 * abs(c - p["pref"]) / max(math.sqrt(shape.mask.sum()), 1) * f
            if best is None or score > best["score"]:
                best = dict(score=score, p=p, size=f, lines=lines, fits=fits)
    if best is None:
        return None
    # letter-spacing: as wide as fits, up to track_max
    f, fits = best["size"], best["fits"]
    tr = track0
    for step in np.linspace(track_max, track0, 9):
        if fits(f, step) is not None:
            tr = step
            break
    c = fits(f, tr)
    L, hh, offs, ch = block(face, wght, best["lines"], f, tr, extra_k * cap_h(face, wght) * f)
    p = best["p"]
    return dict(x=p["x"], y=p["y"], arc=p["arc"], centre=c, size=f, track=tr, lines=best["lines"],
                offs=offs, cap=ch, length=L, half=hh, curved=p["curved"])


# ------------------------------------------------------------------------------ the layout
OCC_K = 2   # occupancy cells per map px


class Occ:
    """What the map's lettering and furniture already cover, at OCC_K cells per map px."""

    def __init__(self, H, W):
        self.H, self.W = H * OCC_K, W * OCC_K
        self.a = np.zeros((self.H, self.W), bool)

    def _poly(self, pts):
        pts = np.asarray(pts, float) * OCC_K
        x0, y0 = np.floor(pts.min(0)).astype(int) - 1
        x1, y1 = np.ceil(pts.max(0)).astype(int) + 2
        img = Image.new("1", (max(x1 - x0, 1), max(y1 - y0, 1)), 0)
        ImageDraw.Draw(img).polygon([tuple(p) for p in pts - (x0, y0)], fill=1)
        return np.asarray(img, bool), x0, y0

    def _clip(self, m, x0, y0):
        X0, Y0, X1, Y1 = max(x0, 0), max(y0, 0), min(x0 + m.shape[1], self.W), min(y0 + m.shape[0], self.H)
        if X1 <= X0 or Y1 <= Y0:
            return None, None
        return np.s_[Y0:Y1, X0:X1], m[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]

    def hit(self, pts):
        m, x0, y0 = self._poly(pts)
        sl, mm = self._clip(m, x0, y0)
        if sl is None:
            return True     # off the map
        if mm.shape != m.shape:
            return True
        return bool((self.a[sl] & mm).any())

    def stamp(self, pts):
        m, x0, y0 = self._poly(pts)
        sl, mm = self._clip(m, x0, y0)
        if sl is not None:
            self.a[sl] |= mm

    def map_res(self):
        """Covered map px (any cell of the pixel)."""
        a = self.a.reshape(self.H // OCC_K, OCC_K, self.W // OCC_K, OCC_K)
        return a.any(axis=(1, 3))


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def circle_pts(x, y, r, n=16):
    return [(x + r * math.cos(2 * math.pi * k / n), y + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


def band(x, y, arc, centre, length, half, pad=0.0):
    """The outline of a label's band (map px): along the centre line, half-height either side."""
    p = Curve(x, y)
    s = np.linspace(centre - length / 2 - pad, centre + length / 2 + pad, 24)
    top, bot = [], []
    for si in s:
        px, py, a = p.at(si)
        nx, ny = -math.sin(a), math.cos(a)
        top.append((px - nx * (half + pad), py - ny * (half + pad)))
        bot.append((px + nx * (half + pad), py + ny * (half + pad)))
    return top + bot[::-1]


def free_spot(blocked, w, h, pref, margin):
    """The top left (map px) of a w x h box with no blocked px within margin, nearest pref."""
    H, W = blocked.shape
    ii = np.pad(np.cumsum(np.cumsum(blocked.astype(np.int32), 0), 1), ((1, 0), (1, 0)))
    bw, bh = w + 2 * margin, h + 2 * margin
    if bw >= W or bh >= H:
        return None
    cnt = ii[bh:, bw:] - ii[:-bh, bw:] - ii[bh:, :-bw] + ii[:-bh, :-bw]
    ys, xs = np.nonzero(cnt == 0)
    if not len(ys):
        return None
    cx, cy = xs + bw / 2, ys + bh / 2
    k = int(np.argmin((cx - pref[0]) ** 2 + (cy - pref[1]) ** 2))
    return int(xs[k] + margin), int(ys[k] + margin)


# the furniture on the map plate (map px): (w, h) and where it should go
COMPASS = dict(w=360, h=360, pref=(4560, 360))
EDGE, CORNER = 22, 175     # map px kept clear along the plate's edges and in its corners (the fans)


def marker_hit(marks, box, own):
    """Whether a box (map px) comes within any marker's disk but the city's own."""
    xs = [p[0] for p in box]
    ys = [p[1] for p in box]
    qx = np.clip(marks[:, 0], min(xs), max(xs))
    qy = np.clip(marks[:, 1], min(ys), max(ys))
    near = np.hypot(marks[:, 0] - qx, marks[:, 1] - qy) < marks[:, 2]
    near[own] = False
    return bool(near.any())


def place_city_names(d, occ, items, cities, areas, nation_of, marks):
    """City names beside their markers, the first free of eight places (map px)."""
    kind = d["kind"]
    H, W = kind.shape
    land = kind == 1
    owner = d["owner"]
    for c in cities:
        size = 26 if c["capital"] else 22
        wght = 600 if c["capital"] else 400
        L = measure("josefin", wght, c["name"], size, 0.02) / SCALE
        hh = cap_h("josefin", wght) * size * 0.5 / SCALE
        desc = 0.32 * size / SCALE      # room for descenders below the line
        g = c["r"] + 6 / SCALE
        cx, cy = c["x"] + 0.5, c["y"] + 0.5
        own = nation_of.get(c["tag"], -1)
        best = None
        for rank, (dx, dy, al) in enumerate(((1, 0, "l"), (-1, 0, "r"), (0.7, -0.75, "l"), (0.7, 0.75, "l"),
                                             (-0.7, -0.75, "r"), (-0.7, 0.75, "r"), (0, -1.1, "c"),
                                             (0, 1.15, "c"))):
            ox = cx + dx * g
            oy = cy + dy * (g + hh)
            if al == "l":
                bx0, bx1 = ox, ox + L
            elif al == "r":
                bx0, bx1 = ox - L, ox
            else:
                bx0, bx1 = ox - L / 2, ox + L / 2
            box = rect(bx0 - 2 / SCALE, oy - hh - 3 / SCALE, bx1 + 2 / SCALE, oy + hh + desc + 2 / SCALE)
            if occ.hit(box) or marker_hit(marks, box, c["i"]):
                continue
            ys_ = np.clip(np.arange(int(oy - hh), int(oy + hh) + 1), 0, H - 1)
            xs_ = np.clip(np.arange(int(bx0), int(bx1) + 1), 0, W - 1)
            o = owner[np.ix_(ys_, xs_)]
            foreign = ((o >= 0) & (o != own)).mean()     # over a neighbour's land
            cost = rank + 6 * foreign
            if best is None or cost < best[0]:
                best = (cost, bx0, oy, bx1, box, land[np.ix_(ys_, xs_)].mean() >= 0.5)
        if best is None:
            log(f"layout: no room for {c['name']}")
            continue
        cost, bx0, oy, bx1, box, on_land = best
        occ.stamp(box)
        items["cities"].append(dict(name=c["name"], x0=bx0, y=oy, size=size, wght=wght,
                                    ink=on_land, capital=c["capital"]))


def layout_labels(d):
    """Every label's place, in map px, decided once (a draft lays out like the print)."""
    kind, owner = d["kind"], d["owner"]
    H, W = kind.shape
    occ = Occ(H, W)
    items = dict(nations=[], leaders=[], cities=[], oceans=[], continents=[], furniture={})
    blocked = kind != 0
    if not d.get("window"):
        for x0_, y0_, x1_, y1_ in ((0, 0, W, EDGE), (0, H - EDGE, W, H), (0, 0, EDGE, H), (W - EDGE, 0, W, H),
                                   (0, 0, CORNER, CORNER), (W - CORNER, 0, W, CORNER), (0, H - CORNER, CORNER, H),
                                   (W - CORNER, H - CORNER, W, H)):
            occ.stamp(rect(x0_, y0_, x1_, y1_))
    for key, spec in (("compass", COMPASS),):
        if d.get("window"):
            break
        pos = free_spot(blocked, spec["w"], spec["h"], spec["pref"], 14)
        if pos is None:
            log(f"layout: no room for the {key}")
            continue
        x, y = pos
        items["furniture"][key] = (x, y, spec["w"], spec["h"])
        occ.stamp(rect(x - 8, y - 8, x + spec["w"] + 8, y + spec["h"] + 8))
    # markers: kept apart, so a name is tested against every marker but its own
    cap_r, dot_r = 13 / SCALE, 7 / SCALE
    occ_m = Occ(H, W)
    for c in d["cities"]:
        r = cap_r if c["capital"] else dot_r
        c["r"] = r
        occ_m.stamp(circle_pts(c["x"] + 0.5, c["y"] + 0.5, r + 4 / SCALE))
    marks = np.array([(c["x"] + 0.5, c["y"] + 0.5, c["r"] + 3 / SCALE) for c in d["cities"]])
    areas = np.bincount(owner[owner >= 0], minlength=len(d["nations"]))
    nation_of = d["tag_i"]
    nation_name = {r["tag"]: r["name"].casefold() for r in d["nations"]}
    named = [c for c in d["cities"] if c["name"] and c["name"].casefold() != nation_name.get(c["tag"])]
    by_size = lambda c: -areas[nation_of.get(c["tag"], 0)]
    # the capitals' names first, so the nations' names leave room for them
    place_city_names(d, occ, items, sorted([c for c in named if c["capital"]], key=by_size), areas,
                     nation_of, marks)
    taken = occ.map_res() | occ_m.map_res()
    # ---- nations, inside their land
    objs = ndi.find_objects(owner + 1)
    order = np.argsort(-areas)
    pending = []
    for i in order:
        r = d["nations"][i]
        sl = objs[i] if i < len(objs) else None
        if sl is None:
            continue
        y0, x0 = max(sl[0].start - 3, 0), max(sl[1].start - 3, 0)
        y1, x1 = min(sl[0].stop + 3, H), min(sl[1].stop + 3, W)
        m = owner[y0:y1, x0:x1] == i
        lab, n = ndi.label(m, structure=np.ones((3, 3)))
        sizes = np.bincount(lab.ravel())
        sizes[0] = 0
        main = lab == int(np.argmax(sizes))
        holes = taken[y0:y1, x0:x1]       # markers and the capitals' names
        shape = Shape(main, y0, x0, holes)
        area = areas[i] * SCALE ** 2
        f_hi = float(np.clip(0.125 * math.sqrt(area), F_MIN + 2, 170))
        name = r["name"].upper()
        gp = r["tag"] in GREAT_POWERS
        opts = [[name]]
        two = split2(name)
        if two:
            opts.append(two)
        tmax = 0.16 + 0.55 * float(np.clip((f_hi - 30) / 80, 0, 1))
        res = fit_label(shape, opts, F_MIN, f_hi, 0.10, tmax, NATION,
                        extra_k=0.95 if gp else 0.0)
        if res is None:
            pending.append(i)
            continue
        res.update(x=res["x"] + x0, y=res["y"] + y0, tag=r["tag"], gp=gp, name=name)
        if gp:   # the ornament under the name, in the room block() left below the lines
            ch = res["cap"]
            res["orn"] = res["offs"][-1] + ch / 2 + 0.55 * ch
        items["nations"].append(res)
        occ.stamp(band(res["x"], res["y"], res["arc"], res["centre"], res["length"] / SCALE,
                       res["half"] / SCALE, 4 / SCALE))
    log(f"layout: {len(items['nations'])} names inside their nations, {len(pending)} beside")
    land = kind == 1
    place_city_names(d, occ, items, sorted([c for c in named if not c["capital"]], key=by_size), areas,
                     nation_of, marks)
    occ.a |= occ_m.a
    # ---- oceans
    water = kind == 0
    dwater = ndi.distance_transform_edt(water)
    taken = occ.map_res()
    for o, oname in enumerate(d["ocean_names"]):
        m_all = (d["ocean"] == o) & water
        tot = int(m_all.sum())
        if tot < 500:
            continue
        # the ocean's large pieces (the seam cuts some in two), the widest halved: a name in each
        lab_o, n_o = ndi.label(m_all)
        sizes = np.bincount(lab_o.ravel())
        sizes[0] = 0
        pieces = []
        for k in range(1, n_o + 1):
            if sizes[k] < max(0.18 * tot, 12000) and k != int(np.argmax(sizes)):
                continue
            pm = lab_o == k
            xs_ = np.nonzero(pm.any(0))[0]
            if xs_[-1] - xs_[0] > 3000 and sizes[k] > 600000:
                mid = int(np.median(np.nonzero(pm)[1]))
                left, right = pm.copy(), pm.copy()
                left[:, mid:] = False
                right[:, :mid] = False
                pieces += [left, right]
            else:
                pieces.append(pm)
        small = tot < 200000
        for m in pieces:
            ys, xs = np.nonzero(m)
            y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
            taken = occ.map_res()
            crop = m[y0:y1, x0:x1] & (dwater[y0:y1, x0:x1] > (3 if small else 7)) & \
                ~ndi.binary_dilation(taken[y0:y1, x0:x1], iterations=3 if small else 6)
            shape = Shape(crop, y0, x0)
            area = tot * SCALE ** 2
            f_hi = float(np.clip(0.030 * math.sqrt(area), 34, 96))
            text = oname.upper()
            opts = [[text]]
            two = split2(text)
            if two:
                opts.append(two)
            degs = (0, 8, -8, 16, -16, 30, -30, 45, -45) if small else (0, 8, -8, 16, -16)
            angles = {round(math.radians(a), 4) for a in degs}
            if shape.ok and abs(shape.theta) < 0.5:
                angles.add(round(shape.theta, 4))
            res = fit_label(shape, opts, 18 if small else 22, f_hi, 0.25 if small else 0.45,
                            0.8 if small else 1.1, dict(face="bodoni_i", wght=400),
                            margin_k=0.15 if small else 0.3, angles=sorted(angles))
            if res is None:
                log(f"layout: no room for the {oname} ({x0}, {y0})")
                continue
            res.update(x=res["x"] + x0, y=res["y"] + y0, name=text)
            items["oceans"].append(res)
            occ.stamp(band(res["x"], res["y"], res["arc"], res["centre"], res["length"] / SCALE,
                           res["half"] / SCALE, 4 / SCALE))
    # ---- small nations: the name beside, with a leader line
    for i in pending:
        r = d["nations"][i]
        name = r["name"].upper()
        sl = objs[i]
        m = owner[sl] == i
        Dm = ndi.distance_transform_edt(np.pad(m, 1))[1:-1, 1:-1]
        k = int(np.argmax(Dm))
        ay, ax = np.unravel_index(k, Dm.shape)
        ax, ay = ax + sl[1].start + 0.5, ay + sl[0].start + 0.5
        size = F_LEAD
        L = measure("federo", 400, name, size, 0.10) / SCALE
        hh = cap_h("federo", 400) * size / 2 / SCALE
        best = None
        for rad in np.arange(16, 260, 7) / SCALE * 1.75:
            for kk in range(24):
                a = 2 * math.pi * kk / 24
                lx, ly = ax + math.cos(a) * rad * 1.25, ay + math.sin(a) * rad
                # the box's near edge points at the nation
                if math.cos(a) > 0.35:
                    bx0 = lx
                elif math.cos(a) < -0.35:
                    bx0 = lx - L
                else:
                    bx0 = lx - L / 2
                box = rect(bx0 - 4 / SCALE, ly - hh - 5 / SCALE, bx0 + L + 4 / SCALE, ly + hh + 5 / SCALE)
                if occ.hit(box):
                    continue
                xs_ = np.clip(np.arange(int(bx0), int(bx0 + L) + 1), 0, W - 1)
                ys_ = np.clip(np.arange(int(ly - hh), int(ly + hh) + 1), 0, H - 1)
                landf = land[np.ix_(ys_, xs_)].mean()
                # the leader: from the nation to the box's nearest point
                tx = min(max(ax, bx0 - 3 / SCALE), bx0 + L + 3 / SCALE)
                ty = min(max(ay, ly - hh - 4 / SCALE), ly + hh + 4 / SCALE)
                seg = np.hypot(tx - ax, ty - ay)
                cost = seg + 110 * landf
                if best is None or cost < best[0]:
                    best = (cost, bx0, ly, tx, ty, landf)
            if best is not None and best[0] < rad * 1.6:
                break
        if best is None:
            log(f"layout: no room for {name}")
            continue
        cost, bx0, ly, tx, ty, landf = best
        box = rect(bx0 - 4 / SCALE, ly - hh - 5 / SCALE, bx0 + L + 4 / SCALE, ly + hh + 5 / SCALE)
        occ.stamp(box)
        seg = math.hypot(tx - ax, ty - ay)
        leader = None
        if seg > 6 / SCALE:
            leader = (ax, ay, tx, ty)
            n_ = max(int(seg * OCC_K), 2)
            for q in np.linspace(0.15, 1, n_):
                px, py = ax + (tx - ax) * q, ay + (ty - ay) * q
                occ.stamp(circle_pts(px, py, 1.5 / SCALE, 6))
        items["leaders"].append(dict(name=name, x0=bx0, y=ly, size=size, ink=landf >= 0.5,
                                     leader=leader, tag=r["tag"], gp=r["tag"] in GREAT_POWERS))
    log(f"layout: {len(items['cities'])} city names, {len(items['leaders'])} names beside")
    # ---- continents: very large and faint, under everything
    cont = d["cont"]
    for c, cname in enumerate(CONTINENT_NAMES, 1):
        m = (cont == c) & land
        if m.sum() < 2000:
            continue
        ys, xs = np.nonzero(m)
        y0, y1, x0, x1 = ys.min() - 20, ys.max() + 21, xs.min() - 20, xs.max() + 21
        y0, x0 = max(y0, 0), max(x0, 0)
        crop = m[y0:y1, x0:x1]
        crop = ndi.binary_closing(crop, structure=disk_mask(14), iterations=1)
        crop = ndi.binary_fill_holes(crop)
        shape = Shape(crop, y0, x0)
        area = m.sum() * SCALE ** 2
        f_hi = float(np.clip(0.16 * math.sqrt(area), 140, 330))
        res = fit_label(shape, [[cname.upper()]], 60, f_hi, 0.6, 1.9, dict(face="federo", wght=400),
                        margin_k=0.0, min_margin=0, clear=0.3)
        if res is None:
            log(f"layout: no room for {cname}")
            continue
        res.update(x=res["x"] + x0, y=res["y"] + y0, name=cname.upper())
        items["continents"].append(res)
    log(f"layout: {len(items['oceans'])} oceans, {len(items['continents'])} continents")
    return items


# ----------------------------------------------------------------------------- rendering
def to_print(v, s):
    return (np.asarray(v, float) + 0.0) * s


def gilt_gradient(h):
    ys = np.linspace(0, 1, max(h, 2))
    out = np.zeros((len(ys), 3), np.float32)
    for c in range(3):
        out[:, c] = np.interp(ys, [p for p, _ in GILT_STOPS], [col[c] for _, col in GILT_STOPS])
    return out


def star_points(cx, cy, r_out, r_in, n=5, rot=-math.pi / 2):
    pts = []
    for k in range(2 * n):
        r = r_out if k % 2 == 0 else r_in
        a = rot + k * math.pi / n
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def sprite(size, draw_fn, ss=4):
    """An RGBA sprite drawn at ss times its size and reduced (anti-aliased shapes)."""
    big = Image.new("RGBA", (size * ss, size * ss), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(big), size * ss / 2, ss)
    return big.resize((size, size), Image.LANCZOS)


def capital_sprite(Q, gp=False):
    R = 13 * Q * (1.15 if gp else 1)
    size = int(math.ceil(R * 2 + 6))

    def fn(dr, c, ss):
        r = R * ss
        dr.ellipse([c - r, c - r, c + r, c + r], fill=IVORY + (255,), outline=INK + (255,),
                   width=max(int(2.2 * Q * ss), 1))
        if gp:
            r2 = r - 3.4 * Q * ss
            dr.ellipse([c - r2, c - r2, c + r2, c + r2], outline=BRONZE + (255,), width=max(int(1.2 * Q * ss), 1))
        dr.polygon(star_points(c, c + 0.4 * Q * ss, r * 0.66, r * 0.27), fill=INK + (255,))
    return sprite(size, fn)


def city_sprite(Q):
    R = 6.2 * Q
    size = int(math.ceil(R * 2 + 4))

    def fn(dr, c, ss):
        r = R * ss
        dr.ellipse([c - r, c - r, c + r, c + r], fill=IVORY + (255,), outline=INK + (255,),
                   width=max(int(1.8 * Q * ss), 1))
        r2 = 2.4 * Q * ss
        dr.ellipse([c - r2, c - r2, c + r2, c + r2], fill=INK + (255,))
    return sprite(size, fn)


def composite(rgb, alpha, colour, strength=1.0):
    a = alpha * strength
    if np.ndim(colour) == 1 or isinstance(colour, tuple):
        colour = np.array(colour, np.float32)
    rgb += (colour - rgb) * a[..., None]


def halo_of(alpha, r):
    if r < 0.6:
        return alpha.copy()
    h = ndi.grey_dilation(alpha, footprint=disk_mask(r))
    return ndi.gaussian_filter(h, max(r * 0.35, 0.5))


def render_labels(rgb, land_a, items, d, s, Q):
    Hp, Wp = land_a.shape
    P = lambda v: (np.asarray(v, float) + 0.5) * s - 0.5   # map px -> print px of this render
    # continents
    lay = np.zeros((Hp, Wp), np.float32)
    for it in items["continents"]:
        path = Curve(P(it["x"]), P(it["y"]))
        size = it["size"] * Q
        draw_run(lay, it["lines"][0], "federo", 400, size, it["track"] * size, path, it["centre"] * s,
                 it["offs"][0] * Q)
    col = (np.array(INK, np.float32)[None, None] * land_a[..., None]
           + np.array(GILT, np.float32)[None, None] * (1 - land_a[..., None]))
    rgb += (col - rgb) * (lay * (0.075 + 0.145 * (1 - land_a)))[..., None]
    log("labels: continents")
    # oceans: gilt italic capitals, the water lining cleared round them
    lay[:] = 0
    for it in items["oceans"]:
        path = Curve(P(it["x"]), P(it["y"]))
        size = it["size"] * Q
        for ln, off in zip(it["lines"], it["offs"]):
            draw_run(lay, ln, "bodoni_i", 400, size, it["track"] * size, path, it["centre"] * s, off * Q)
    halo = halo_of(lay, 5 * Q)
    composite(rgb, halo, PAL["deep"], 0.85)
    composite(rgb, lay, PAL["ocean_ink"], 0.95)
    log("labels: oceans")
    # leader lines and markers
    lead = np.zeros((Hp, Wp), np.float32)
    for it in items["leaders"]:
        if it["leader"]:
            ax, ay, tx, ty = it["leader"]
            X0, Y0, X1, Y1 = P(ax), P(ay), P(tx), P(ty)
            n = int(max(abs(X1 - X0), abs(Y1 - Y0)) * 2) + 2
            img = Image.new("L", (Wp, 1))   # placeholder to keep PIL imported paths simple
            xs = np.linspace(X0, X1, n)
            ys = np.linspace(Y0, Y1, n)
            for x_, y_ in zip(xs, ys):
                xi, yi = int(x_), int(y_)
                if 1 <= xi < Wp - 2 and 1 <= yi < Hp - 2:
                    fx, fy = x_ - xi, y_ - yi
                    w = max(1.0 * Q, 0.6)
                    lead[yi, xi] = max(lead[yi, xi], (1 - fx) * (1 - fy) * w + 0.0)
                    lead[yi, xi + 1] = max(lead[yi, xi + 1], fx * (1 - fy) * w)
                    lead[yi + 1, xi] = max(lead[yi + 1, xi], (1 - fx) * fy * w)
                    lead[yi + 1, xi + 1] = max(lead[yi + 1, xi + 1], fx * fy * w)
            r = 3.2 * Q
            yy, xx = np.ogrid[-int(r) - 2:int(r) + 3, -int(r) - 2:int(r) + 3]
            dot = np.clip(r + 0.5 - np.hypot(xx - (X0 - int(X0)), yy - (Y0 - int(Y0))), 0, 1)
            paste_max(lead, dot.astype(np.float32), int(X0) - int(r) - 2, int(Y0) - int(r) - 2)
    lead = np.clip(lead * 1.6, 0, 1)
    col = (np.array(INK, np.float32)[None, None] * land_a[..., None]
           + np.array(CREAM, np.float32)[None, None] * (1 - land_a[..., None]))
    rgb += (col - rgb) * (0.85 * lead)[..., None]
    img = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))
    caps = {False: capital_sprite(Q), True: capital_sprite(Q, gp=True)}
    dot = city_sprite(Q)
    for c in d["cities"]:
        sp = caps[c["tag"] in GREAT_POWERS] if c["capital"] else dot
        X, Y = P(c["x"] + 0.5 - 0.5) + 0.5 * s - s / 2, P(c["y"])
        X, Y = P(c["x"]), P(c["y"])
        img.alpha_composite(sp, (int(round(X - sp.width / 2)), int(round(Y - sp.height / 2)))) \
            if img.mode == "RGBA" else img.paste(sp, (int(round(X - sp.width / 2)), int(round(Y - sp.height / 2))), sp)
    rgb[:] = np.asarray(img, np.float32)
    log("labels: markers")
    # nation, city and beside names: ink on land, cream on the sea
    ink = np.zeros((Hp, Wp), np.float32)
    cream = np.zeros((Hp, Wp), np.float32)
    orn = np.zeros((Hp, Wp), np.float32)
    for it in items["nations"]:
        path = Curve(P(it["x"]), P(it["y"]))
        size = it["size"] * Q
        for ln, off in zip(it["lines"], it["offs"]):
            draw_run(ink, ln, "federo", 400, size, it["track"] * size, path, it["centre"] * s, off * Q)
        if it.get("orn") is not None:
            draw_ornament(orn, path, it["centre"] * s, it["orn"] * Q, it["length"] * Q * 0.5, it["cap"] * Q)
    for it in items["leaders"]:
        size = it["size"] * Q
        L = measure("federo", 400, it["name"], it["size"], 0.10) * Q
        x0 = P(it["x0"])
        y = P(it["y"])
        path = straight(x0 + L / 2, y, 0.0, L)
        draw_run(ink if it["ink"] else cream, it["name"], "federo", 400, size, 0.10 * size, path,
                 path.length / 2, 0)
    for it in items["cities"]:
        size = it["size"] * Q
        L = measure("josefin", it["wght"], it["name"], it["size"], 0.02) * Q
        x0, y = P(it["x0"]), P(it["y"])
        path = straight(x0 + L / 2, y, 0.0, L)
        draw_run(ink if it["ink"] else cream, it["name"], "josefin", it["wght"], size, 0.02 * size, path,
                 path.length / 2, 0)
    composite(rgb, halo_of(ink, 3.2 * Q), (240, 233, 214), 0.62)
    composite(rgb, halo_of(cream, 3.2 * Q), PAL["deep"], 0.8)
    composite(rgb, orn, (96, 70, 26), 0.95)
    composite(rgb, ink, INK, 0.96)
    composite(rgb, cream, CREAM, 0.96)
    log("labels: names")


def draw_ornament(layer, path, s_mid, off, half_w, cap):
    """The great powers' mark under their names: a diamond between two hairlines fading out."""
    p2 = path.offset(off)
    k = 4
    pts = [p2.at(s) for s in np.linspace(s_mid - half_w, s_mid + half_w, 61)]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    pad = int(cap) + 4
    x0, y0 = int(min(xs)) - pad, int(min(ys)) - pad
    w, h = int(max(xs)) + pad - x0, int(max(ys)) + pad - y0
    img = Image.new("L", (w * k, h * k), 0)
    dr = ImageDraw.Draw(img)
    gap = cap * 0.62
    lw = max(int(round(max(cap * 0.055, 1.1) * k)), 1)
    for i in range(60):
        sa = s_mid - half_w + (i + 0.5) * 2 * half_w / 60
        if abs(sa - s_mid) < gap:
            continue
        fade = 1 - ((abs(sa - s_mid) - gap) / (half_w - gap)) ** 1.5
        (xa, ya, _), (xb, yb, _) = pts[i], pts[i + 1]
        dr.line([((xa - x0) * k, (ya - y0) * k), ((xb - x0) * k, (yb - y0) * k)],
                fill=int(255 * max(fade, 0)), width=lw)
    x, y, a = p2.at(s_mid)
    r = cap * 0.34
    dr.polygon([((x + r * math.cos(a + q) - x0) * k, (y + r * 0.8 * math.sin(a + q) * 0 + r * math.sin(a + q) - y0) * k)
                for q in (0, math.pi / 2, math.pi, 3 * math.pi / 2)], fill=255)
    small = np.asarray(img.resize((w, h), Image.LANCZOS), np.float32) / 255
    paste_max(layer, small, x0, y0)


# --------------------------------------------------------------------------------- frame
TOP, SIDE, GAP, BOTTOM = 940, 320, 96, 150      # full-size px round the map plate
FRIEZE_COLS = 40


class Canvas:
    """The poster: a float RGB array, drawn on in full-size px times Q."""

    def __init__(self, W, H, Q):
        self.Q = Q
        self.W, self.H = W, H
        self.a = np.empty((H, W, 3), np.float32)
        self.a[:] = np.array(LACQUER, np.float32)
        # faint vertical pinstripes, 8 px apart, as the Deco UI's lacquer panels
        period = max(int(round(8 * Q)), 2)
        cols = (np.arange(W) % period) == 0
        self.a[:, cols] += 4.0

    def q(self, v):
        return v * self.Q

    def blend(self, alpha, colour, x0=0, y0=0, strength=1.0):
        """Alpha (a float array) in colour at (x0, y0)."""
        h, w = alpha.shape
        X0, Y0 = max(x0, 0), max(y0, 0)
        X1, Y1 = min(x0 + w, self.W), min(y0 + h, self.H)
        if X1 <= X0 or Y1 <= Y0:
            return
        a = alpha[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0] * strength
        sub = self.a[Y0:Y1, X0:X1]
        col = np.asarray(colour, np.float32)
        if col.ndim == 1:
            sub += (col - sub) * a[..., None]
        else:
            sub += (col[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0] - sub) * a[..., None]

    def hline(self, x0, x1, y, w, colour, a=1.0):
        x0, x1 = int(round(x0)), int(round(x1))
        y0 = int(round(y - w / 2))
        h = max(int(round(w)), 1)
        self.blend(np.full((h, max(x1 - x0, 1)), a, np.float32), colour, x0, y0)

    def vline(self, x, y0, y1, w, colour, a=1.0):
        y0, y1 = int(round(y0)), int(round(y1))
        x0 = int(round(x - w / 2))
        ww = max(int(round(w)), 1)
        self.blend(np.full((max(y1 - y0, 1), ww), a, np.float32), colour, x0, y0)

    def fill(self, x0, y0, x1, y1, colour, a=1.0):
        x0, y0, x1, y1 = (int(round(v)) for v in (x0, y0, x1, y1))
        self.blend(np.full((max(y1 - y0, 1), max(x1 - x0, 1)), a, np.float32), colour, x0, y0)

    def paste_rgba(self, img, x, y):
        arr = np.asarray(img.convert("RGBA"), np.float32)
        self.blend(arr[..., 3] / 255, arr[..., :3], int(round(x)), int(round(y)))

    def shapes(self, x0, y0, w, h, fn, colour, a=1.0, ss=3):
        """Anti-aliased shapes: fn(draw, k) draws at ss times, coordinates local to (x0, y0)
        times k; the result is blended in colour."""
        w, h = int(math.ceil(w)), int(math.ceil(h))
        img = Image.new("L", (w * ss, h * ss), 0)
        fn(ImageDraw.Draw(img), ss)
        small = np.asarray(img.resize((w, h), Image.LANCZOS), np.float32) / 255
        self.blend(small, colour, int(round(x0)), int(round(y0)), a)


def stepped_rect(x0, y0, x1, y1, st):
    """The outline of a rectangle with stepped (notched) corners, two steps of st."""
    pts = []
    for cx, cy, sx, sy in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x1, y1, -1, -1), (x0, y1, 1, -1)):
        corner = [(cx, cy + sy * 2 * st), (cx + sx * st, cy + sy * 2 * st), (cx + sx * st, cy + sy * st),
                  (cx + sx * 2 * st, cy + sy * st), (cx + sx * 2 * st, cy)]
        if sx * sy < 0:
            corner = corner[::-1]
        pts += corner
    return pts


def draw_poly_outline(cv, pts, w, colour, a=1.0):
    """Axis-aligned polyline segments (closed), crisp."""
    n = len(pts)
    for i in range(n):
        (xa, ya), (xb, yb) = pts[i], pts[(i + 1) % n]
        if abs(ya - yb) < 1e-6:
            cv.hline(min(xa, xb) - w / 2, max(xa, xb) + w / 2, ya, w, colour, a)
        elif abs(xa - xb) < 1e-6:
            cv.vline(xa, min(ya, yb) - w / 2, max(ya, yb) + w / 2, w, colour, a)


def plate(cv, x0, y0, x1, y1, st, fill=LACQUER_2, a=0.96):
    """A deco plate: lacquer with a gilt double rim and stepped corners."""
    q = cv.q
    pts = stepped_rect(x0, y0, x1, y1, st)

    def fn(dr, k):
        dr.polygon([((x - x0) * k, (y - y0) * k) for x, y in pts], fill=255)
    cv.shapes(x0, y0, x1 - x0 + 1, y1 - y0 + 1, fn, fill, a, ss=1)
    draw_poly_outline(cv, pts, max(q(3), 1), GILT_RULE)
    inset = q(12)
    draw_poly_outline(cv, stepped_rect(x0 + inset, y0 + inset, x1 - inset, y1 - inset, st * 0.75),
                      max(q(1.4), 1), GILT, 0.8)


def text_layer(text, face, wght, size, track_em):
    """A straight run of text as an alpha array, and its (width, cap height); the cap middle at
    the array's vertical middle."""
    L = measure(face, wght, text, size, track_em)
    ch = cap_h(face, wght) * size
    w, h = int(math.ceil(L + size * 1.2)), int(math.ceil(size * 2.2))
    lay = np.zeros((h, w), np.float32)
    draw_run(lay, text, face, wght, size, track_em * size, straight(w / 2, h / 2, 0, L), L, 0)
    return lay, L, ch


def put_text(cv, text, face, wght, size, track_em, cx, cy, colour, a=1.0, align="c", gilt=False,
             shadow=None):
    lay, L, ch = text_layer(text, face, wght, size, track_em)
    h, w = lay.shape
    if align == "c":
        x0 = cx - w / 2
    elif align == "l":
        x0 = cx - (w - L) / 2
    else:
        x0 = cx - w + (w - L) / 2
    y0 = cy - h / 2
    if shadow:
        dx, dy, blur, sc, sa = shadow
        sh = ndi.gaussian_filter(lay, blur) if blur else lay
        cv.blend(sh, sc, int(round(x0 + dx)), int(round(y0 + dy)), sa)
    if gilt:
        grad = gilt_gradient(int(ch * 1.3))
        col = np.zeros((h, w, 3), np.float32)
        top = int(h / 2 - ch * 0.65)
        for yy in range(h):
            col[yy] = grad[int(np.clip(yy - top, 0, len(grad) - 1))]
        cv.blend(lay, col, int(round(x0)), int(round(y0)), a)
    else:
        cv.blend(lay, colour, int(round(x0)), int(round(y0)), a)
    return L


def wrap(text, face, wght, size, track_em, width, max_lines=2):
    words = text.split(" ")
    lines = [words[0]]
    for wd in words[1:]:
        trial = lines[-1] + " " + wd
        if measure(face, wght, trial, size, track_em) <= width:
            lines[-1] = trial
        else:
            lines.append(wd)
    if len(lines) > max_lines:
        lines = lines[:max_lines - 1] + [" ".join(lines[max_lines - 1:])]
    return lines


def sunburst(cv, cx, cy, r0, r1, n, a, colour=GILT, span=(0, 2 * math.pi), width_k=0.5, fade=True):
    """Rays from (cx, cy): n wedges between r0 and r1, faded outwards."""
    x0, y0 = cx - r1, cy - r1
    size = 2 * r1

    def fn(dr, k):
        for i in range(n):
            a0 = span[0] + (span[1] - span[0]) * i / n
            da = (span[1] - span[0]) / n * width_k
            pts = [((cx - x0 + r0 * math.cos(a0)) * k, (cy - y0 + r0 * math.sin(a0)) * k),
                   ((cx - x0 + r1 * math.cos(a0 - da / 2)) * k, (cy - y0 + r1 * math.sin(a0 - da / 2)) * k),
                   ((cx - x0 + r1 * math.cos(a0 + da / 2)) * k, (cy - y0 + r1 * math.sin(a0 + da / 2)) * k)]
            dr.polygon(pts, fill=255)
    w = int(math.ceil(size))
    img = Image.new("L", (w * 2, w * 2), 0)
    fn(ImageDraw.Draw(img), 2)
    lay = np.asarray(img.resize((w, w), Image.LANCZOS), np.float32) / 255
    if fade:
        yy, xx = np.mgrid[0:w, 0:w]
        rr = np.hypot(xx - (cx - x0), yy - (cy - y0))
        lay *= np.clip(1 - (rr - r0) / (r1 - r0), 0, 1) ** 1.2
    cv.blend(lay, colour, int(round(x0)), int(round(y0)), a)


def diamond(cv, cx, cy, r, colour, a=1.0):
    def fn(dr, k):
        dr.polygon([(r * k, 0), (2 * r * k, r * k), (r * k, 2 * r * k), (0, r * k)], fill=255)
    cv.shapes(cx - r, cy - r, 2 * r + 1, 2 * r + 1, fn, colour, a, ss=4)


def fade_line(cv, x0, x1, y, w, colour, a=1.0, towards="right"):
    """A hairline fading out at one end (the Deco UI's gradient rules)."""
    x0, x1 = int(round(x0)), int(round(x1))
    n = max(x1 - x0, 1)
    ramp = np.linspace(0, 1, n, dtype=np.float32)
    if towards == "left":
        ramp = ramp[::-1]
    ramp = 1 - ramp if towards in ("right",) else ramp
    h = max(int(round(w)), 1)
    cv.blend(np.tile(ramp, (h, 1)) * a, colour, x0, int(round(y - w / 2)))


def stepped_rules(cv, x0, x1, y, side, q):
    """Three stepped hairlines (the menu's), fading away from the text on side 'l' or 'r'."""
    for k in range(3):
        yy = y - q(9) + k * q(9)
        if side == "l":
            fade_line(cv, x0, x1 - k * q(50), yy, max(q(2), 1), GILT_RULE, 0.9, towards="left")
        else:
            fade_line(cv, x0 + k * q(50), x1, yy, max(q(2), 1), GILT_RULE, 0.9, towards="right")


def flag_image(tag, ideology, w, h):
    key = IDEOLOGY_KEYS.get(ideology, "")
    for f in (ROOT / f"source/flags/{tag}_{key}.png", ROOT / f"source/flags/{tag}.png"):
        if f.exists():
            return Image.open(f).convert("RGB").resize((w, h), Image.LANCZOS)
    tga = MOD / f"gfx/flags/{tag}.tga"
    if tga.exists():   # the game's stand-in: stripes of the map colour, drawn crisp
        src = np.asarray(Image.open(tga).convert("RGB"))
        rows = (np.arange(h) + 0.5) * src.shape[0] / h
        col = src[np.minimum(rows.astype(int), src.shape[0] - 1), src.shape[1] // 2]
        return Image.fromarray(np.repeat(col[:, None], w, 1).astype(np.uint8))
    return Image.new("RGB", (w, h), (128, 128, 128))


def framed_flag(cv, img, x, y, gp=False):
    q = cv.q
    w, h = img.size
    pad = q(5)
    cv.fill(x - pad - q(2), y - pad - q(2), x + w + pad + q(2), y + h + pad + q(2), (8, 12, 15), 0.9)
    draw_poly_outline(cv, rect(x - pad, y - pad, x + w + pad, y + h + pad), max(q(2.2 if gp else 1.4), 1),
                      GILT if gp else GILT_RULE)
    if gp:
        draw_poly_outline(cv, rect(x - pad - q(6), y - pad - q(6), x + w + pad + q(6), y + h + pad + q(6)),
                          max(q(1.2), 1), GILT, 0.8)
    cv.paste_rgba(img, x, y)


def compass(cv, cx, cy, R):
    """A sixteen-point compass rose on a sunburst, in a ringed dial."""
    q = cv.q
    sunburst(cv, cx, cy, R * 0.18, R * 1.28, 72, 0.16, GILT, width_k=0.42)
    ring = int(R * 2.4)
    x0, y0 = cx - ring / 2, cy - ring / 2

    def circle(dr, k, r, w):
        c = ring / 2 * k
        dr.ellipse([c - r * k, c - r * k, c + r * k, c + r * k], outline=255, width=max(int(w * k), 1))

    def rings(dr, k):
        circle(dr, k, R * 0.98, q(3.2))
        circle(dr, k, R * 0.90, q(1.6))
        circle(dr, k, R * 0.34, q(1.6))
        c = ring / 2 * k
        for deg in range(0, 360, 5):
            a = math.radians(deg)
            r_in = R * (0.84 if deg % 45 == 0 else 0.87 if deg % 15 == 0 else 0.885)
            dr.line([(c + r_in * k * math.cos(a), c + r_in * k * math.sin(a)),
                     (c + R * 0.90 * k * math.cos(a), c + R * 0.90 * k * math.sin(a))],
                    fill=255, width=max(int(q(1.6 if deg % 45 == 0 else 1.0) * k), 1))
    cv.shapes(x0, y0, ring, ring, rings, GILT, 0.95)

    def points(dr, k, rank, half):
        c = ring / 2 * k
        for i in range(16):
            if (0 if i % 4 == 0 else 1 if i % 2 == 0 else 2) != rank:
                continue
            a = -math.pi / 2 + i * math.pi / 8
            L = R * (0.86 if i % 4 == 0 else 0.62 if i % 2 == 0 else 0.44)
            wd = R * (0.13 if i % 4 == 0 else 0.10 if i % 2 == 0 else 0.07)
            tip = (c + L * k * math.cos(a), c + L * k * math.sin(a))
            side = a + (math.pi / 2 if half else -math.pi / 2)
            base = (c + wd * k * math.cos(side), c + wd * k * math.sin(side))
            dr.polygon([(c, c), tip, base], fill=255)
            if not half:   # a fine dark rim round the whole point
                other = (c + wd * k * math.cos(a - math.pi / 2), c + wd * k * math.sin(a - math.pi / 2))
                dr.line([other, tip, base], fill=255, width=max(int(q(1.2) * k), 1))
    # the minor points first, the main ones over them: each point a light and a dark half
    for rank in (2, 1, 0):
        for half, col in ((True, GILT_HI), (False, BRONZE)):
            cv.shapes(x0, y0, ring, ring, lambda dr, k, r=rank, h=half: points(dr, k, r, h), col, 1.0)

    def hub(dr, k):
        c = ring / 2 * k
        r = R * 0.06 * k
        dr.ellipse([c - r, c - r, c + r, c + r], fill=255)
    cv.shapes(x0, y0, ring, ring, hub, LACQUER, 1.0)
    for lab, a in (("N", -90), ("E", 0), ("S", 90), ("W", 180)):
        rr = R * 1.12
        put_text(cv, lab, "federo", 400, q(70) if lab == "N" else q(44), 0,
                 cx + rr * math.cos(math.radians(a)), cy + rr * math.sin(math.radians(a)),
                 GILT, gilt=lab == "N")


def scale_bar(cv, x, y, q, s):
    """Kilometres over leagues, at the equator (Valsora taken as the Earth's size)."""
    km_px = s / KM_PER_PX            # print px per km
    for row, (unit, per, step, n, lab) in enumerate((("KILOMETRES", 1.0, 500, 6, "km"),
                                                       ("LEAGUES", KM_PER_LEAGUE, 100, 5, "leagues"))):
        yy = y + row * q(110)
        seg = step * per * km_px
        h = q(16)
        for i in range(n):
            x0 = x + i * seg
            if i % 2 == 0:
                cv.fill(x0, yy, x0 + seg, yy + h, GILT_RULE, 0.95)
            draw_poly_outline(cv, rect(x0, yy, x0 + seg, yy + h), max(q(1.6), 1), GILT)
        for i in range(n + 1):
            put_text(cv, f"{i * step:,}", "josefin", 600, q(22), 0.05, x + i * seg, yy + h + q(26), CREAM_2)
        put_text(cv, unit, "josefin", 600, q(20), 0.32, x + n * seg + q(26), yy + h / 2, LABEL, align="l")
    for k, note in enumerate(("At the equator, taking Valsora to be the size of the Earth:",
                              f"5,120 map pixels round the world, one map pixel ≈ {KM_PER_PX:.1f} km.")):
        put_text(cv, note, "bodoni_i", 400, q(29), 0.0, x, y + q(250) + k * q(42), LABEL, align="l")


def legend_swatch(cv, key, sx0, sy0, sw, sh, Q):
    q = cv.q
    tint = muted(np.array([[120, 160, 110], [200, 150, 110]], np.float32))
    if key in ("border", "state", "river", "capital", "gpcapital", "city", "gp"):
        cv.fill(sx0, sy0, sx0 + sw, sy0 + sh, tint[0])
    if key == "border":
        cv.fill(sx0 + sw / 2, sy0, sx0 + sw, sy0 + sh, tint[1])
        cv.vline(sx0 + sw / 2, sy0, sy0 + sh, max(q(2.6), 1), INK, 0.92)
    elif key == "state":
        cv.vline(sx0 + sw / 2, sy0, sy0 + sh, max(q(1.0), 1), INK, 0.3)
    elif key == "coast":
        cv.fill(sx0, sy0, sx0 + sw * 0.4, sy0 + sh, tint[0])
        cv.fill(sx0 + sw * 0.4, sy0, sx0 + sw, sy0 + sh, PAL["sea"])
        cv.vline(sx0 + sw * 0.4, sy0, sy0 + sh, max(q(2.3), 1), INK, 0.92)
        cv.vline(sx0 + sw * 0.4 + q(6.3), sy0, sy0 + sh, max(q(1.0), 1), PAL["outer"], 0.9)
        for i in range(5):
            cv.vline(sx0 + sw * 0.4 + q(13 + 12.5 * i), sy0, sy0 + sh, max(q(1.0), 1), PAL["lining"],
                     PAL["lining_a"] * (1 - i / 6))
    elif key == "river":
        def fn(dr, k, sw=sw, sh=sh):
            pts = [(i / 40 * sw * k, (sh / 2 + math.sin(i / 40 * 2 * math.pi) * sh * 0.22) * k) for i in range(41)]
            dr.line(pts, fill=255, width=max(int(q(3.2) * k), 1))
        cv.shapes(sx0, sy0, sw, sh, fn, RIVER, 0.9)
    elif key in ("capital", "gpcapital", "city"):
        spr = capital_sprite(Q, key == "gpcapital") if key != "city" else city_sprite(Q)
        cv.paste_rgba(spr, sx0 + sw / 2 - spr.width / 2, sy0 + sh / 2 - spr.height / 2)
    elif key == "gp":
        lay = np.zeros((int(sh), int(sw)), np.float32)
        f = q(24)
        ch = cap_h("federo") * f
        L = measure("federo", 400, "NAME", f, 0.12)
        draw_run(lay, "NAME", "federo", 400, f, 0.12 * f, straight(sw / 2, sh * 0.36, 0, L), L, 0)
        cv.blend(lay, INK, int(sx0), int(sy0), 0.95)
        orn = np.zeros((int(sh), int(sw)), np.float32)
        draw_ornament(orn, straight(sw / 2, sh * 0.36, 0, sw * 0.4), sw * 0.4, ch / 2 + 0.55 * ch,
                      sw * 0.36, ch)
        cv.blend(orn, BRONZE, int(sx0), int(sy0), 0.95)
    elif key == "beside":
        cv.fill(sx0, sy0, sx0 + sw, sy0 + sh, PAL["sea"])
        cv.fill(sx0 + q(6), sy0 + sh * 0.5, sx0 + q(30), sy0 + sh * 0.85, tint[1])
        diamond(cv, sx0 + q(18), sy0 + sh * 0.66, q(3), CREAM)
        cv.hline(sx0 + q(18), sx0 + q(52), sy0 + sh * 0.66, max(q(1.2), 1), CREAM, 0.85)
        put_text(cv, "NAME", "federo", 400, q(21), 0.1, sx0 + q(56), sy0 + sh * 0.4, CREAM, align="l")
    draw_poly_outline(cv, rect(sx0, sy0, sx0 + sw, sy0 + sh), max(q(1.2), 1), GILT_RULE, 0.8)


def plate_title(cv, text, cx, y, half):
    q = cv.q
    L = measure("federo", 400, text, q(46), 0.42)
    put_text(cv, text, "federo", 400, q(46), 0.42, cx, y, GILT, gilt=True)
    fade_line(cv, cx - L / 2 - half, cx - L / 2 - q(66), y, max(q(2), 1), GILT_RULE, 0.9, towards="left")
    fade_line(cv, cx + L / 2 + q(66), cx + L / 2 + half, y, max(q(2), 1), GILT_RULE, 0.9, towards="right")
    diamond(cv, cx - L / 2 - q(44), y, q(7), GILT)
    diamond(cv, cx + L / 2 + q(44), y, q(7), GILT)


def legend(cv, x0, y0, x1, y1, d, Q, s):
    q = cv.q
    plate(cv, x0, y0, x1, y1, q(18))
    plate_title(cv, "KEY TO THE MAP", (x0 + x1) / 2, y0 + q(84), q(420))
    sw, sh = q(132), q(62)
    columns = [["border", "state", "coast"], ["river", "city", "beside"], ["capital", "gpcapital", "gp"]]
    labels = {"border": "Frontier between nations", "state": "Boundary of a state",
              "coast": "Coast, with its water lining", "river": "River", "city": "City",
              "beside": "Name set beside a small nation", "capital": "National capital",
              "gpcapital": "Capital of a great power", "gp": "Great power"}
    col_w = (x1 - x0 - q(130)) / 3
    for ci, col in enumerate(columns):
        for ri, key in enumerate(col):
            ex = x0 + q(80) + ci * col_w
            ey = y0 + q(190) + ri * q(112)
            legend_swatch(cv, key, ex, ey - sh / 2, sw, sh, Q)
            put_text(cv, labels[key], "josefin", 400, q(30), 0.02, ex + sw + q(28), ey, CREAM_2, align="l")
    notes = ["A capital is named where its nation has named it. Every nation's name sits inside its land when it fits;",
             "the relief is the terrain test's (not yet in the game), the lettering the Valsora Deco UI's."]
    for k, ln in enumerate(notes):
        put_text(cv, ln, "bodoni_i", 400, q(29), 0.0, (x0 + x1) / 2, y1 - q(122) + k * q(42), LABEL)


def great_powers(cv, x0, y0, x1, y1, d, Q, s):
    q = cv.q
    plate(cv, x0, y0, x1, y1, q(18))
    mid = x0 + (x1 - x0) * 0.52
    plate_title(cv, "THE FOUR GREAT POWERS", (x0 + mid) / 2 + q(20), y0 + q(84), q(260))
    plate_title(cv, "SCALE", (mid + x1) / 2, y0 + q(84), q(330))
    cv.vline(mid, y0 + q(150), y1 - q(70), max(q(1.4), 1), GILT_RULE, 0.6)
    diamond(cv, mid, y0 + q(150), q(6), GILT_RULE)
    diamond(cv, mid, y1 - q(70), q(6), GILT_RULE)
    caps = {c["tag"]: c["name"] for c in d["cities"] if c["capital"]}
    by = {r["tag"]: r for r in d["nations"]}
    fw, fh = int(q(112)), int(q(112) * 52 / 82)
    for k, tag in enumerate(["KRI", "KPF", "SRK", "FRX"]):
        r = by.get(tag)
        if r is None:
            continue
        ex = x0 + q(90)
        ey = y0 + q(168) + k * q(112)
        framed_flag(cv, flag_image(tag, r["ideology"], fw, fh), ex, ey, gp=True)
        tx = ex + fw + q(44)
        put_text(cv, r["name"].upper(), "federo", 400, q(36), 0.16, tx, ey + q(16), CREAM, align="l")
        sub = f"{GREAT_POWERS[tag]} great power"
        if caps.get(tag):
            sub += f" · capital {caps[tag]}"
        put_text(cv, sub, "josefin", 400, q(26), 0.02, tx, ey + q(56), LABEL, align="l")
    scale_bar(cv, mid + q(110), y0 + q(250), q, s)


def cartouche(cv, cx, y0, y1):
    q = cv.q
    w = q(3060)
    x0, x1 = cx - w / 2, cx + w / 2
    sunburst(cv, cx, y1 + q(40), q(160), q(1900), 64, 0.11, GILT, span=(math.pi, 2 * math.pi), width_k=0.45)
    plate(cv, x0, y0, x1, y1, q(22), a=0.97)
    # the crest: a diamond between hairlines, the title, the subtitle between stepped rules
    ty = y0 + q(270)
    put_text(cv, "VALSORA", "limelight", 400, q(300), 0.1, cx, ty, GILT, gilt=True,
             shadow=(0, q(7), 0, (59, 42, 16), 1.0))
    dy = y0 + q(62)
    diamond(cv, cx, dy, q(13), GILT)
    fade_line(cv, cx - q(300), cx - q(30), dy, max(q(2), 1), GILT_RULE, 0.95, towards="left")
    fade_line(cv, cx + q(30), cx + q(300), dy, max(q(2), 1), GILT_RULE, 0.95, towards="right")
    sy = y0 + q(500)
    L = measure("josefin", 600, "THE WORLD IN THE YEAR 2036", q(56), 0.5)
    put_text(cv, "THE WORLD IN THE YEAR 2036", "josefin", 600, q(56), 0.5, cx + q(14), sy, (231, 211, 160))
    stepped_rules(cv, cx - L / 2 - q(360), cx - L / 2 - q(40), sy + q(9), "l", q)
    stepped_rules(cv, cx + L / 2 + q(40), cx + L / 2 + q(360), sy + q(9), "r", q)
    put_text(cv, "The nations of the world of The East Pacific on the first of January, 2036",
             "bodoni_i", 400, q(40), 0.0, cx, y0 + q(590), (191, 175, 134))


def plate_frame(cv, mx0, my0, mx1, my1):
    """The map plate's frame: a degree band with ticks, double gilt rules, corner brackets."""
    q = cv.q
    band_w = q(30)
    # the degree band round the plate
    cv.fill(mx0 - band_w, my0 - band_w, mx1 + band_w, my0, (10, 15, 18))
    cv.fill(mx0 - band_w, my1, mx1 + band_w, my1 + band_w, (10, 15, 18))
    cv.fill(mx0 - band_w, my0, mx0, my1, (10, 15, 18))
    cv.fill(mx1, my0, mx1 + band_w, my1, (10, 15, 18))
    W, H = mx1 - mx0, my1 - my0
    for deg in range(-180, 181, 5):
        x = mx0 + (deg + 180) / 360 * W
        L = band_w * (0.9 if deg % 30 == 0 else 0.55 if deg % 15 == 0 else 0.3)
        for yb, sgn in ((my0, -1), (my1, 1)):
            cv.vline(x, min(yb, yb + sgn * L), max(yb, yb + sgn * L), max(q(1.4), 1), GILT_RULE, 0.9)
        if deg % 30 == 0 and -180 < deg < 180:
            lab = "0°" if deg == 0 else f"{abs(deg)}°{'E' if deg > 0 else 'W'}"
            put_text(cv, lab, "josefin", 600, q(21), 0.1, x, my0 - band_w - q(24), LABEL)
            put_text(cv, lab, "josefin", 600, q(21), 0.1, x, my1 + band_w + q(24), LABEL)
    for deg in range(-90, 91, 5):
        y = my0 + (90 - deg) / 180 * H
        L = band_w * (0.9 if deg % 30 == 0 else 0.55 if deg % 15 == 0 else 0.3)
        for xb, sgn in ((mx0, -1), (mx1, 1)):
            cv.hline(min(xb, xb + sgn * L), max(xb, xb + sgn * L), y, max(q(1.4), 1), GILT_RULE, 0.9)
        if deg % 30 == 0 and -90 < deg < 90:
            lab = "0°" if deg == 0 else f"{abs(deg)}°{'N' if deg > 0 else 'S'}"
            put_text(cv, lab, "josefin", 600, q(21), 0.1, mx0 - band_w - q(44), y, LABEL)
            put_text(cv, lab, "josefin", 600, q(21), 0.1, mx1 + band_w + q(44), y, LABEL)
    draw_poly_outline(cv, rect(mx0, my0, mx1, my1), max(q(2), 1), GILT)
    draw_poly_outline(cv, rect(mx0 - band_w, my0 - band_w, mx1 + band_w, my1 + band_w), max(q(3), 1), GILT_RULE)
    o = band_w + q(14)
    draw_poly_outline(cv, stepped_rect(mx0 - o, my0 - o, mx1 + o, my1 + o, q(26)), max(q(1.4), 1), GILT, 0.85)
    # double corner brackets inside the plate, and a fan in each corner
    for cx, cy, sx, sy in ((mx0, my0, 1, 1), (mx1, my0, -1, 1), (mx1, my1, -1, -1), (mx0, my1, 1, -1)):
        for k, L in ((q(14), q(120)), (q(30), q(80))):
            x, y = cx + sx * k, cy + sy * k
            cv.hline(min(x, x + sx * L), max(x, x + sx * L), y, max(q(2), 1), GILT, 0.95)
            cv.vline(x, min(y, y + sy * L), max(y, y + sy * L), max(q(2), 1), GILT, 0.95)
        a0 = math.atan2(sy, sx)
        sunburst(cv, cx + sx * q(14), cy + sy * q(14), q(40), q(300), 13, 0.30, GILT,
                 span=(a0 - math.pi / 4, a0 + math.pi / 4), width_k=0.35)


def frieze(cv, x0, x1, y0, d):
    """Every nation's flag, alphabetical, with its name."""
    q = cv.q
    rows = sorted(d["nations"], key=lambda r: unicodedata.normalize("NFD", r["name"]).encode("ascii", "ignore")
                  .decode().casefold())
    cx = (x0 + x1) / 2
    put_text(cv, f"THE {len(rows)} NATIONS OF VALSORA", "federo", 400, q(50), 0.45, cx, y0 + q(30), GILT, gilt=True)
    L = measure("federo", 400, f"THE {len(rows)} NATIONS OF VALSORA", q(50), 0.45)
    stepped_rules(cv, cx - L / 2 - q(700), cx - L / 2 - q(60), y0 + q(39), "l", q)
    stepped_rules(cv, cx + L / 2 + q(60), cx + L / 2 + q(700), y0 + q(39), "r", q)
    cols = FRIEZE_COLS
    cw = (x1 - x0) / cols
    fw = int(q(150))
    fh = int(round(fw * 52 / 82))
    top = y0 + q(120)
    rh = q(196)
    for k, r in enumerate(rows):
        c, rr = k % cols, k // cols
        fx = x0 + c * cw + (cw - fw) / 2
        fy = top + rr * rh
        gp = r["tag"] in GREAT_POWERS
        framed_flag(cv, flag_image(r["tag"], r["ideology"], fw, fh), fx, fy, gp=gp)
        size = q(21)
        lines = wrap(r["name"], "josefin", 600, size, 0.03, cw - q(14))
        while max(measure("josefin", 600, ln, size, 0.03) for ln in lines) > cw - q(10) and size > q(14):
            size -= q(1)
        for j, ln in enumerate(lines):
            put_text(cv, ln, "josefin", 600, size, 0.03, x0 + c * cw + cw / 2, fy + fh + q(30) + j * q(25),
                     GILT_HI if gp else CREAM_2)
    return top + ((len(rows) - 1) // cols + 1) * rh


def compose(m, items, d, Q):
    s = SCALE * Q
    q = lambda v: v * Q
    Hp, Wp = m["rgb"].shape[:2]
    W = int(round(FULL_W * Q))
    mx0, my0 = int(round((W - Wp) / 2)), int(round(q(TOP)))
    n_rows = (len(d["nations"]) - 1) // FRIEZE_COLS + 1
    frieze_h = q(120 + n_rows * 196)
    H = int(round(my0 + Hp + q(GAP) + frieze_h + q(BOTTOM)))
    cv = Canvas(W, H, Q)
    # the outer frame: a gilt double rule with stepped corners
    o = q(60)
    draw_poly_outline(cv, stepped_rect(o, o, W - o, H - o, q(30)), max(q(3), 1), GILT_RULE)
    draw_poly_outline(cv, stepped_rect(o + q(16), o + q(16), W - o - q(16), H - o - q(16), q(24)),
                      max(q(1.4), 1), GILT, 0.85)
    cv.a[my0:my0 + Hp, mx0:mx0 + Wp] = m["rgb"]
    plate_frame(cv, mx0, my0, mx0 + Wp, my0 + Hp)
    # the furniture on the plate
    f = items["furniture"]
    if "compass" in f:
        x, y, w, h = f["compass"]
        compass(cv, mx0 + (x + w / 2) * s, my0 + (y + h / 2) * s, w / 2 * s * 0.78)
    band_top, band_bot = q(150), my0 - q(110)
    cartouche(cv, W / 2, band_top, band_bot)
    side_w = (W - q(3060)) / 2 - q(420)
    legend(cv, mx0, band_top + q(10), mx0 + side_w, band_bot, d, Q, s)
    great_powers(cv, mx0 + Wp - side_w, band_top + q(10), mx0 + Wp, band_bot, d, Q, s)
    end = frieze(cv, mx0, mx0 + Wp, my0 + Hp + q(GAP), d)
    imprint = ("VALSORA  ·  A HEARTS OF IRON IV TOTAL CONVERSION  ·  DRAWN FROM THE MOD'S MAP  ·  "
               "THE WORLD OF THE EAST PACIFIC")
    yi = (end + H - q(76)) / 2
    L = measure("josefin", 600, imprint, q(22), 0.4)
    put_text(cv, imprint, "josefin", 600, q(22), 0.4, W / 2, yi, LABEL, 0.9)
    diamond(cv, W / 2 - L / 2 - q(40), yi, q(5), GILT_RULE)
    diamond(cv, W / 2 + L / 2 + q(40), yi, q(5), GILT_RULE)
    return cv


def save_outputs(img, out_dir, Q, draft=False):
    """The print, a preview about 2,400 px wide, and four close-ups at the print's resolution."""
    stem = "valsora_2036_poster"
    if draft:
        img.save(out_dir / "draft.png")
        log(f"saved {out_dir / 'draft.png'} {img.size}")
        return
    full = out_dir / f"{stem}.png"
    img.save(full, optimize=True)
    mb = full.stat().st_size / 1e6
    log(f"saved {full} {img.size}, {mb:.1f} MB")
    if mb > 60:   # too big to pass round: a high-quality JPEG beside it
        img.save(out_dir / f"{stem}.jpg", quality=93, subsampling=0, optimize=True)
        log(f"saved {stem}.jpg")
    pw = 2400
    img.resize((pw, round(img.height * pw / img.width)), Image.LANCZOS).save(out_dir / f"{stem}_preview.png",
                                                                             optimize=True)
    mx0, my0 = (img.width - round(MAP_W * SCALE * Q)) / 2, TOP * Q
    m = lambda x, y: (round(mx0 + x * SCALE * Q), round(my0 + y * SCALE * Q))
    W = img.width
    crops = {
        "vale_of_reibonne": (*m(380, 560), *m(1150, 1090)),           # Rouental and the Vale
        "yastreovakia": (*m(1480, 60), *m(3420, 1180)),
        "cartouche": (round(W / 2 - 1800 * Q), round(110 * Q), round(W / 2 + 1800 * Q), round(TOP * Q - 40 * Q)),
        "flag_frieze": (round(W / 2 - 1700 * Q), m(0, MAP_H)[1] + round(70 * Q), round(W / 2 + 1700 * Q),
                        img.height - round(110 * Q)),
    }
    for k, box in crops.items():
        img.crop(box).save(out_dir / f"{stem}_detail_{k}.png", optimize=True)
    log("saved the preview and the close-ups")


# ------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft", type=float, default=0, help="render at this fraction of print size")
    ap.add_argument("--out", default=None)
    ap.add_argument("--reuse-layout", nargs="?", const=True, default=None,
                    help="(tests) keep the layout in the scratch folder and reuse it")
    ap.add_argument("--no-map", action="store_true", help="(tests) the frame only")
    ap.add_argument("--palette", default="lacquer", choices=sorted(PALETTES))
    ap.add_argument("--window", default="", help="x0,y0,x1,y1 in map px: only that part (tests)")
    args = ap.parse_args()
    Q = args.draft or 1.0
    out_dir = Path(args.out) if args.out else (OUT if not args.draft else Path("/tmp/claude-0/poster_scratch"))
    out_dir.mkdir(parents=True, exist_ok=True)
    global PAL
    PAL = PALETTES[args.palette]
    d = load_data()
    if args.window:
        d = crop_data(d, [int(v) for v in args.window.split(",")])
    s = SCALE * Q
    cache = Path("/tmp/claude-0/poster_scratch/layout.pkl")
    if args.reuse_layout and cache.exists():
        import pickle
        items = pickle.loads(cache.read_bytes())
        for c, cc in zip(d["cities"], items.pop("_cities")):
            c.update(cc)
    else:
        items = layout_labels(d)
        if args.reuse_layout is not None:
            import pickle
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_bytes(pickle.dumps(dict(items, _cities=d["cities"])))
    if args.no_map:   # (tests) the frame round an empty plate
        Hp, Wp = int(round(MAP_H * s)), int(round(MAP_W * s))
        rgb = np.empty((Hp, Wp, 3), np.float32)
        rgb[:] = np.array(PAL["deep"], np.float32)
        m = dict(rgb=rgb)
    else:
        m = render_map(d, s, Q)
        render_labels(m["rgb"], m["land_a"], items, d, s, Q)
    if d.get("window"):
        Image.fromarray(np.clip(m["rgb"], 0, 255).astype(np.uint8)).save(out_dir / "map_only.png")
        log("saved the window")
        return
    cv = compose(m, items, d, Q)
    del m
    img = Image.fromarray(np.clip(cv.a, 0, 255).astype(np.uint8))
    del cv
    save_outputs(img, out_dir, Q, draft=bool(args.draft))


if __name__ == "__main__":
    main()
