"""Write the HOI4 mod from the province, state and region data.

Reads work/provinces.npz, work/regions.npz and work/regions.json.
Writes build/valsora_test/ (the mod folder) and build/valsora_test.mod (the
launcher's outer descriptor).
"""
import json
import unicodedata
import os
import math
import shutil
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

from common import MAP_W, MAP_H, CONTINENTS, MOD_NAME, MOD_DIR_NAME, COUNTRIES, PLACEHOLDERS, DECO_UI
import cultures
import gazetteer
import ideologies
import globe
import vanilla_parts
import minimap
import nations
import superevents
from imgio import write_bmp, write_dds, write_tga, palette_from_header

W, H = MAP_W, MAP_H
OUT = Path("build") / MOD_DIR_NAME
PAL = Path("source/palettes")
FLAGS = Path("source/flags")
POP_PER_PX = 300  # state population per map pixel
IDEOLOGIES = ideologies.IDEOLOGIES
CRLF = "\r\n"
CITY_VP = 5  # victory points of a named city from the Cities layer (a capital has 10)

REPLACE_PATHS = [
    "history/states", "history/countries", "history/units", "history/general",
    "map/strategicregions", "events", "common/decisions", "common/ai_strategy",
    "common/ai_strategy_plans", "common/on_actions", "common/bookmarks",
]

# Vanilla 1.19.3 map/buildings.txt carries these per state (count) ...
STATE_BUILDINGS = [("air_base", 1), ("anti_air_building", 3), ("arms_factory", 6),
                   ("industrial_complex", 6), ("fuel_silo", 1), ("nuclear_reactor_spawn", 1),
                   ("radar_station", 1), ("rocket_site_spawn", 1), ("stronghold_network", 1),
                   ("synthetic_refinery", 1)]
# ... these per land province, and these per coastal province.
PROVINCE_BUILDINGS = ["bunker", "special_project_facility_spawn", "supply_node"]
COASTAL_BUILDINGS = ["naval_headquarters", "naval_supply_hub", "coastal_bunker"]


def country_file(c):
    """File name of a country: its name, plus the tag when another country shares the name
    (the Loyal Army is "Rouental" too)."""
    name = COUNTRIES[c][1]
    same = [k for k in COUNTRIES if COUNTRIES[k][1] == name]
    return ascii_name(name) + (f" {COUNTRIES[c][0]}" if len(same) > 1 and same[0] != c else "")


def ascii_name(name):
    """File names stay ASCII (Côtefer -> Cotefer): accents in mod paths are a risk."""
    return unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()


def ui_colour(rgb):
    """Colour for text and flags in the UI: a quarter of the way to white, so dark map
    colours (Lustiana's black) stay readable, as vanilla's color_ui is brighter too."""
    return tuple(round(v + (255 - v) * 0.25) for v in rgb)


def cosmetic(tag, ideology):
    """Cosmetic tag used while `ideology` rules `tag` (see nations.LOOKS). Not TAG_IDEOLOGY:
    its flag ROU_COMMUNISM.tga would clash with ROU_communism.tga on Windows, which
    ignores case (the author's unzip asked about duplicate files)."""
    return f"{tag}_GOV_{ideology.upper()}"


def write(path, text, bom=False, crlf=False):
    path = OUT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    if crlf:
        text = text.replace("\n", CRLF)
    data = text.encode("utf-8")
    if bom:
        data = b"\xef\xbb\xbf" + data
    path.write_bytes(data)


def coast_distance(water):
    """Distance (px) from every pixel to the nearest pixel of the other kind."""
    d_in_water = ndi.distance_transform_edt(water)
    d_in_land = ndi.distance_transform_edt(~water)
    return d_in_water, d_in_land


def smooth_noise(shape, sigma, seed):
    rng = np.random.default_rng(seed)
    small = rng.standard_normal((shape[0] // 8 + 2, shape[1] // 8 + 2)).astype(np.float32)
    small = ndi.gaussian_filter(small, sigma / 8, mode="wrap")
    big = np.asarray(Image.fromarray(small).resize((shape[1], shape[0]), Image.BICUBIC))
    return big / (big.std() + 1e-6)


def heightmap(pix_kind):
    """8-bit heights: HOI4's water plane sits at 95 (9.5 world units)."""
    water = pix_kind != 1
    d_sea, d_land = coast_distance(water)
    noise = smooth_noise(pix_kind.shape, 60, 7) * 5 + smooth_noise(pix_kind.shape, 16, 8) * 2
    land_h = 97 + 13 * (1 - np.exp(-d_land / 30)) + noise * (1 - np.exp(-d_land / 12))
    sea_h = 94 - 7 * (1 - np.exp(-d_sea / 18))
    h = np.where(water, sea_h, land_h)
    h = np.where(pix_kind == 2, np.minimum(h, 92.5), h)  # lakes: shallow
    h = np.where(water, np.clip(h, 80, 94), np.clip(h, 96, 160))
    return np.round(h).astype(np.uint8), d_sea


def normal_map(height):
    """world_normal.bmp at half resolution, RGB = (x, y, z) with flat = (128,128,255)."""
    h = height.astype(np.float32).reshape(H // 2, 2, W // 2, 2).mean(axis=(1, 3)) / 10
    gx = (np.roll(h, -1, axis=1) - np.roll(h, 1, axis=1)) / 2
    gy = np.zeros_like(h)
    gy[1:-1] = (h[2:] - h[:-2]) / 2
    k = 1.5
    n = np.stack([-gx * k, gy * k, np.ones_like(h)], axis=-1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    return np.clip(np.round((n + 1) * 127.5), 0, 255).astype(np.uint8)


def half(a):
    return a.reshape(a.shape[0] // 2, 2, a.shape[1] // 2, 2, *a.shape[2:]).mean(axis=(1, 3))


def interp(d, stops):
    xs = np.array([s[0] for s in stops], float)
    ys = np.array([s[1] for s in stops], float)
    return np.stack([np.interp(d, xs, ys[:, c]) for c in range(ys.shape[1])], axis=-1)


def textures(pix_kind, height, d_sea):
    """Colour maps, water colour maps and fog-of-war map, following the colours the
    vanilla 1.19.3 textures use over land and at each distance from the coast."""
    tdir = OUT / "map" / "terrain"
    tdir.mkdir(parents=True, exist_ok=True)
    water = half((pix_kind != 1).astype(np.float32)) >= 0.5
    hh = half(height.astype(np.float32))
    dd = half(d_sea.astype(np.float32)) / 2  # half-res pixels from the coast
    # colormap: land tint by height, flat water colour, no city lights
    land_rgb = interp(hh, [(96, (64, 70, 34)), (110, (70, 70, 36)), (140, (84, 74, 50))])
    land_rgb += smooth_noise(hh.shape, 40, 3)[..., None] * 4
    cmap = np.where(water[..., None], np.array([79, 102, 141], float), land_rgb)
    rgba = np.dstack([np.clip(cmap, 0, 255), np.zeros(hh.shape)]).astype(np.uint8)
    write_dds(tdir / "colormap_rgb_cityemissivemask_a.dds", rgba)
    # water colour: bright shallows, dark open sea
    wcol = interp(dd, [(0, (60, 103, 140)), (3, (81, 128, 173)), (6, (72, 115, 159)),
                       (12, (60, 96, 134)), (24, (46, 75, 108)), (48, (36, 60, 86)),
                       (96, (33, 55, 75))])
    wcol = np.where(water[..., None], wcol, np.array([56, 86, 103], float))
    w0 = np.dstack([wcol, np.full(hh.shape, 255.0)])
    write_dds(tdir / "colormap_water_0.dds", w0.round().astype(np.uint8))
    w1 = half(w0)
    write_dds(tdir / "colormap_water_1.dds", w1.round().astype(np.uint8))
    write_dds(tdir / "colormap_water_2.dds", half(w1).round().astype(np.uint8))
    # fog of war (grey) and water specular (alpha)
    grey = np.where(water, np.interp(dd, [0, 2, 4, 8, 16], [116, 96, 81, 70, 66]),
                    np.interp(hh, [95, 97, 110, 140], [132, 144, 147, 156]))
    alpha = np.where(water, 38, 25)
    fow = np.dstack([grey, grey, grey, alpha]).round().astype(np.uint8)
    write_dds(tdir / "fow_rgb_waterspec_a.dds", fow)


def weather_block(lat):
    """12 monthly periods. lat in [-1, 1]: 0 = map's middle row, -1 = top edge."""
    days = [30, 27, 30, 29, 30, 29, 30, 30, 29, 30, 29, 30]
    mean = 24 - 30 * abs(lat) ** 1.3
    amp = 3 + 12 * abs(lat)
    peak = 6 if lat < 0 else 0  # northern half peaks in July, southern in January
    out = ["\tweather={"]
    for m in range(12):
        t = mean + amp * math.cos(2 * math.pi * (m - peak) / 12)
        cold = min(1.0, max(0.0, (2 - t) / 12))
        snow = round(0.35 * cold, 3)
        bliz = round(0.1 * max(0.0, cold - 0.5), 3)
        rain_l = round(0.25 * (1 - cold), 3)
        rain_h = round(0.1 * (1 - cold), 3)
        none = round(max(0.0, 1 - snow - bliz - rain_l - rain_h), 3)
        out += [
            "\t\tperiod={",
            f"\t\t\tbetween={{ 0.{m} {days[m]}.{m} }}",
            f"\t\t\ttemperature={{ {t - 6:.1f} {t + 6:.1f} }}",
            f"\t\t\tno_phenomenon={none:.3f}",
            f"\t\t\train_light={rain_l:.3f}",
            f"\t\t\train_heavy={rain_h:.3f}",
            f"\t\t\tsnow={snow:.3f}",
            f"\t\t\tblizzard={bliz:.3f}",
            "\t\t\tarctic_water=0.000",
            f"\t\t\tmud={0.3 * (1 - cold) + 0.1:.3f}",
            "\t\t\tsandstorm=0.000",
            "\t\t\tmin_snow_level=0.000",
            "\t\t}",
        ]
    out.append("\t}")
    return "\n".join(out)


def fmt_ids(ids, per_line=20):
    ids = [str(i) for i in ids]
    return "\n".join("\t\t" + " ".join(ids[k:k + per_line]) for k in range(0, len(ids), per_line))


def neighbours(lab, anchor):
    """province -> [(neighbour, border pixels, border y, border x)], the longest borders first;
    the border point is the mean of the shared edge, x measured round the province's anchor (wrap)."""
    H, W = lab.shape
    ys, xs = np.mgrid[0:H, 0:W]
    pa = np.concatenate([lab[:, :-1].ravel(), lab[:-1, :].ravel(), lab[:, -1]])
    pb = np.concatenate([lab[:, 1:].ravel(), lab[1:, :].ravel(), lab[:, 0]])
    py = np.concatenate([ys[:, :-1].ravel().astype(float), ys[:-1, :].ravel() + 0.5, ys[:, -1].astype(float)])
    px = np.concatenate([xs[:, :-1].ravel() + 0.5, xs[:-1, :].ravel().astype(float), np.full(H, W - 0.5)])
    m = pa != pb
    a = np.concatenate([pa[m], pb[m]]).astype(np.int64)
    b = np.concatenate([pb[m], pa[m]]).astype(np.int64)
    y = np.concatenate([py[m], py[m]])
    x = np.concatenate([px[m], px[m]])
    ax = np.array([anchor[i][1] for i in range(len(anchor))], float)
    dx = ((x - ax[a] + W / 2) % W) - W / 2
    key = a * (int(b.max()) + 1) + b
    uniq, inv, cnt = np.unique(key, return_inverse=True, return_counts=True)
    my = np.bincount(inv, y) / cnt
    mdx = np.bincount(inv, dx) / cnt
    ua, ub = uniq // (int(b.max()) + 1), uniq % (int(b.max()) + 1)
    out = defaultdict(list)
    for i, j, c, yy, ddx in zip(ua.tolist(), ub.tolist(), cnt.tolist(), my.tolist(), mdx.tolist()):
        out[i].append((j, c, yy, (ax[i] + ddx) % W))
    for i in out:
        out[i].sort(key=lambda e: (-e[1], e[0]))
    return out


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    p = np.load("work/provinces.npz")
    lab, kind, cont = p["prov"], p["kind"], p["cont"]
    reg = np.load("work/regions.npz")
    anchor, size, state_of = reg["anchor"], reg["size"], reg["state_of"]
    rj = json.load(open("work/regions.json"))
    states, regions = rj["states"], rj["regions"]
    world = np.load("work/world.npz")
    by_tag = {v[0]: c for c, v in COUNTRIES.items()}
    # what friends filled in on the Gazetteer (source/gazetteer/, scripts/gazetteer.py)
    G, gnotes = gazetteer.load(), []
    gfacts = gazetteer.state_facts(G, lab, state_of, rj["owners"], gnotes) if G else {}
    # the releasables the Gazetteer's players made: countries owning nothing, with cores on
    # the states they hold most of, named, led and coloured as their facts say
    grel = gazetteer.releasables(G, lab, kind, state_of, rj["owners"], gnotes,
                                 taken={v[0] for v in COUNTRIES.values()}) if G else []
    for r in grel:
        COUNTRIES[f"gazetteer_{r['tag'].lower()}"] = (r["tag"], r["name"], r["adj"], r["colour"])
        by_tag[r["tag"]] = f"gazetteer_{r['tag'].lower()}"
        G[r["tag"]] = r["facts"]
        if not r["facts"]["politics"].get("ruling"):  # none given: its nation's
            r["facts"]["politics"]["ruling"] = (nations.LEADERS.get(r["parent"]) or ["despotism"])[0]
        if r["parent"] in cultures.TAG_CULTURE:  # its nation's names and faces
            cultures.TAG_CULTURE.setdefault(r["tag"], cultures.TAG_CULTURE[r["parent"]])
    # owner of every state: from the Countries layer, or the continent's placeholder
    owners = [by_tag[t] for t in rj["owners"]] if "owners" in rj else \
        [CONTINENTS[int(cont[g[0]]) - 1] for g in states]
    # countries that own a state, plus those released later (they own nothing at start)
    later = {by_tag[t] for t in (*nations.CIVIL_WAR, *nations.RELEASABLE, *(r["tag"] for r in grel))}
    present = [c for c in COUNTRIES if c in owners or c in later]
    n = len(kind)
    pid = np.arange(n) + 1  # HOI4 province ids start at 1
    pix_kind = kind[lab]  # repairs may have moved single pixels between kinds

    # ---------------------------------------------------------------- provinces.bmp
    if "colors" in p:  # the author's Provinces layer
        colors = p["colors"]
    else:
        rng = np.random.default_rng(20260928)
        codes = rng.choice(np.arange(1, 1 << 24), size=n, replace=False)
        colors = np.stack([codes >> 16, (codes >> 8) & 255, codes & 255], 1).astype(np.uint8)
    (OUT / "map").mkdir(parents=True, exist_ok=True)
    write_bmp(OUT / "map/provinces.bmp", colors[lab])

    # ---------------------------------------------------------------- adjacency, coast
    a, b, cnt = (np.array(v) for v in zip(*rj["adjacency"]))
    coastal = np.zeros(n, bool)
    ls = ((kind[a] == 1) & (kind[b] == 0)) | ((kind[a] == 0) & (kind[b] == 1))
    coastal[a[ls]] = True
    coastal[b[ls]] = True
    # for every coastal land province: the sea province it shares most coast with,
    # and one land/sea pixel pair in the middle of that stretch of coast
    pairs = []
    for dy, dx in ((0, 1), (1, 0)):
        l1 = lab[: H - dy, :]
        l2 = np.roll(lab, -dx, axis=1)[dy:, :] if dx else lab[dy:, :]
        ys, xs = np.nonzero((kind[l1] == 1) & (kind[l2] == 0) | (kind[l1] == 0) & (kind[l2] == 1))
        y2, x2 = ys + dy, (xs + dx) % W
        swap = kind[l1[ys, xs]] == 0
        ly, lx = np.where(swap, y2, ys), np.where(swap, x2, xs)
        sy, sx = np.where(swap, ys, y2), np.where(swap, xs, x2)
        pairs.append(np.stack([lab[ly, lx], lab[sy, sx], ly, lx, sy, sx], 1))
    pairs = np.concatenate(pairs)
    pairs = pairs[np.lexsort((pairs[:, 3], pairs[:, 2], pairs[:, 1], pairs[:, 0]))]
    port = {}
    key = pairs[:, 0] * n + pairs[:, 1]
    uk, start, count = np.unique(key, return_index=True, return_counts=True)
    for k, s, c in zip(uk, start, count):
        L, S = divmod(int(k), n)
        if L not in port or c > port[L][0]:
            r = pairs[s + c // 2]
            port[L] = (c, S, int(r[2]), int(r[3]), int(r[4]), int(r[5]))

    # ---------------------------------------------------------------- definition.csv
    terrain = list(p["terrain"]) if "terrain" in p else \
        [{0: "ocean", 1: "plains", 2: "lakes"}[k] for k in kind]
    ptype = {0: "sea", 1: "land", 2: "lake"}
    lines = ["0;0;0;0;land;false;unknown;0"]
    for i in range(n):
        r, g, bb = colors[i]
        lines.append(f"{pid[i]};{r};{g};{bb};{ptype[kind[i]]};{'true' if coastal[i] else 'false'};"
                     f"{terrain[i]};{int(cont[i]) if kind[i] == 1 else 0}")
    write("map/definition.csv", "\n".join(lines) + "\n", crlf=True)

    # ---------------------------------------------------------------- bitmaps
    # heights, terrain and rivers come from the .pdn's layers when there are some
    if "height" in world:
        height, d_sea = world["height"], coast_distance(pix_kind != 1)[0]
        tmap, rmap = world["terrain"], world["rivers"]
    else:
        height, d_sea = heightmap(pix_kind)
        tmap = np.where(pix_kind == 1, 0, 15).astype(np.uint8)
        rmap = np.where(pix_kind == 1, 255, 254).astype(np.uint8)
    write_bmp(OUT / "map/heightmap.bmp", height, palette_from_header(PAL / "heightmap.bmp.header.bin"))
    write_bmp(OUT / "map/terrain.bmp", tmap, palette_from_header(PAL / "terrain.bmp.header.bin"))
    write_bmp(OUT / "map/rivers.bmp", rmap, palette_from_header(PAL / "rivers.bmp.header.bin"))
    # cities.bmp index 4 belongs to no city group: no generated town meshes
    write_bmp(OUT / "map/cities.bmp", np.full((H, W), 4, np.uint8),
              palette_from_header(PAL / "cities.bmp.header.bin"))
    # trees.bmp at vanilla's 75/256 of the map size; index 0 = no trees
    write_bmp(OUT / "map/trees.bmp", np.zeros((H * 75 // 256, W * 75 // 256), np.uint8),
              palette_from_header(PAL / "trees.bmp.header.bin"))
    write_bmp(OUT / "map/world_normal.bmp", normal_map(height))
    textures(pix_kind, height, d_sea)
    minimap.write_files(write, OUT, pix_kind == 1, DECO_UI)  # Valsora, not vanilla's Earth
    minimap.write_bookmark(write, OUT, pix_kind == 1, DECO_UI)  # the start date's picture too
    globe.write_files(OUT, pix_kind == 1)  # the world tension globe too

    def world_y(y, x):
        return height[y, x] / 10

    def pos(y, x):
        return f"{x + 0.5:.2f};{world_y(y, x):.2f};{H - y - 0.5:.2f}"

    # distance of every pixel to its province edge, for spreading positions safely
    edge = np.zeros((H, W), bool)
    edge[:, :-1] |= lab[:, :-1] != lab[:, 1:]
    edge[:, 1:] |= lab[:, :-1] != lab[:, 1:]
    edge[:-1] |= lab[:-1] != lab[1:]
    edge[1:] |= lab[:-1] != lab[1:]
    edge[0, :] = edge[-1, :] = True
    inner = ndi.distance_transform_edt(~edge)
    spread = [(0, 0), (0, 3), (3, 0), (0, -3), (-3, 0), (2, 2), (-2, -2), (2, -2), (-2, 2)]

    def spot(i, k):
        """k-th distinct point inside province i."""
        y, x = int(anchor[i][0]), int(anchor[i][1])
        for dy, dx in spread[k % len(spread):] + spread[:k % len(spread)]:
            yy, xx = y + dy, (x + dx) % W
            if 0 <= yy < H and lab[yy, xx] == i and inner[yy, xx] >= 2:
                return yy, xx
        return y, x

    # ---------------------------------------------------------------- states
    cont_count = defaultdict(int)
    state_name = []
    for s, g in enumerate(states):
        c = owners[s]
        cont_count[c] += 1
        state_name.append(f"{COUNTRIES[c][1]} {cont_count[c]}")
    # the author's state names, by a pixel inside the state (state ids shift); numbered
    # for them by scripts/state_map.py
    names_file = Path("source/state_names.json")
    named = {}
    for key, nm in (json.loads(names_file.read_text(encoding="utf-8")) if names_file.exists() else {}).items():
        x, y = map(int, key.split(","))
        s = int(state_of[lab[y, x]])
        if s < 0:
            raise SystemExit(f"source/state_names.json: ({x}, {y}) {nm} is not in a state")
        if s in named:
            raise SystemExit(f"source/state_names.json: {named[s]} and {nm} name the same state")
        named[s] = nm
        state_name[s] = nm
    by_old_name = {nm: s for s, nm in named.items()}  # nations.py's references keep working after a rename
    for s, f in gfacts.items():
        if f.get("name"):
            named[s] = state_name[s] = f["name"]
    state_by_name = {**by_old_name, **{nm: s for s, nm in named.items()}}
    # cores of countries released later (nations.CIVIL_WAR), by state name
    extra_cores = defaultdict(list)
    for tag, names in (*nations.CIVIL_WAR.items(), *nations.RELEASABLE.items()):
        for nm in names:
            if nm not in state_by_name:
                raise SystemExit(f"nations.CIVIL_WAR / RELEASABLE: no state named {nm!r} for {tag}")
            if tag not in nations.CIVIL_WAR_ONLY:  # those get their cores in the focus
                extra_cores[state_by_name[nm]].append(tag)
    for r in grel:  # the Gazetteer's, by state
        for s in r["states"]:
            extra_cores[s].append(r["tag"])
    grel_capital = {r["tag"]: r["states"][0] for r in grel}
    state_capital = [max(g, key=lambda i: (size[i], -i)) for g in states]
    # the author's cities (Cities layer): the first in a state becomes its victory point,
    # any others extra ones; all named, worth CITY_VP unless the country's capital
    city_of = {int(c[0]): c[1] for c in rj.get("cities", [])}
    # the Gazetteer's cities carry their victory points and the capital
    city_vp = {int(c[0]): int(c[4]) for c in rj.get("cities", []) if len(c) > 4}
    city_capital = [int(c[0]) for c in rj.get("cities", []) if len(c) > 5 and c[5]]
    extra_vps = defaultdict(list)
    for p in sorted(city_of, key=lambda p: p not in city_capital):  # a capital city first in its state
        s = int(state_of[p])
        if state_capital[s] in city_of and state_capital[s] != p:
            extra_vps[s].append(p)
        else:
            state_capital[s] = p
    state_coastal = [any(coastal[i] for i in g) for g in states]
    # country capital: the sizeable state nearest the centre of the country's land
    def central(members):
        cy = np.average([reg["centre"][i][0] for s in members for i in states[s]],
                        weights=[size[i] for s in members for i in states[s]])
        cx = np.average([reg["centre"][i][1] for s in members for i in states[s]],
                        weights=[size[i] for s in members for i in states[s]])
        big = [s for s in members if len(states[s]) >= 4] or members
        return min(big, key=lambda s: np.hypot(*(np.mean(
            [reg["centre"][i] for i in states[s]], axis=0) - (cy, cx))))
    capital_state = {}
    for c in present:
        members = [s for s in range(len(states)) if owners[s] == c]
        if not members:  # released later: its first named state
            t = COUNTRIES[c][0]
            capital_state[c] = grel_capital[t] if t in grel_capital else \
                state_by_name[(nations.CIVIL_WAR.get(t) or nations.RELEASABLE[t])[0]]
            continue
        capital_state[c] = central(members)
        # a capital drawn out to a continent holding under a third of the country's land
        # is chosen again on the continent holding most of it (2026-10-10: Estande's
        # islands off Araseos and Orientalis had put its capital on one of them)
        on = Counter()
        for s in members:
            on[int(cont[states[s][0]])] += sum(int(size[i]) for i in states[s])
        if on[int(cont[states[capital_state[c]][0]])] * 3 < sum(on.values()):
            home = on.most_common(1)[0][0]
            capital_state[c] = central([s for s in members if int(cont[states[s][0]]) == home])
    # capitals the author chose, by a map pixel (state ids shift when the map changes)
    for tag, (x, y) in nations.CAPITALS.items():
        c = next(k for k in COUNTRIES if COUNTRIES[k][0] == tag)
        s = int(state_of[lab[y, x]])
        if c not in capital_state or s < 0 or owners[s] != c:
            raise SystemExit(f"nations.CAPITALS: ({x}, {y}) is not in a state of {tag}")
        capital_state[c] = s
    # a capital city named on the Gazetteer moves its country's capital there
    for p in city_capital:
        s = int(state_of[p])
        if capital_state.get(owners[s]) != s:
            gnotes.append(f"Gazetteer: {COUNTRIES[owners[s]][0]}'s capital is {city_of[p]}")
        capital_state[owners[s]] = s
    for s, g in enumerate(states):
        c = owners[s]
        tag = COUNTRIES[c][0]
        is_cap = capital_state[c] == s
        px = sum(int(size[i]) for i in g)
        f = gfacts.get(s, {})
        cat = f.get("cat") or ("city" if is_cap else ("small_island" if len(g) <= 2 else
                                                      "town" if len(g) >= 16 else "rural"))
        cap = state_capital[s]
        # buildings: a capital gets some industry; the Gazetteer's numbers win, within what the
        # state takes (factories share its building slots; islands cap air and naval bases)
        build = {"infrastructure": 3 if is_cap else 2}
        if is_cap:
            build.update(industrial_complex=3, arms_factory=2, air_base=2)
            if state_coastal[s]:
                build.update(dockyard=1, naval_base=3)
        for k, (b, most) in gazetteer.BUILDINGS.items():
            if f.get(k) is not None:
                build[b] = min(int(f[k]), most)
        if not state_coastal[s]:
            build.pop("dockyard", None)
            build.pop("naval_base", None)
        for b, most in gazetteer.ISLAND_MAX.get(cat, {}).items():
            if build.get(b, 0) > most:
                build[b] = most
        slots = gazetteer.CATEGORIES[cat]
        for b in ("dockyard", "arms_factory", "industrial_complex"):  # over the slots: dockyards go first
            over = sum(build.get(k, 0) for k in ("industrial_complex", "arms_factory", "dockyard")) - slots
            if over > 0 and build.get(b):
                if f:
                    gnotes.append(f"Gazetteer: state {s + 1} ({state_name[s]}) has {slots} building slots; "
                                  f"{min(over, build[b])} {b} left out")
                build[b] -= min(over, build[b])
        bl = [f"\t\t\t{b} = {v}" for b, v in build.items() if b != "naval_base" and v]
        if build.get("naval_base"):
            port_prov = max((i for i in g if coastal[i] and i in port), key=lambda i: size[i])
            bl.append(f"\t\t\t{pid[port_prov]} = {{ naval_base = {build['naval_base']} }}")
        res = {r: int(v) for r, v in (f.get("res") or {}).items() if v}
        text = "\n".join([
            "state = {",
            f"\tid = {s + 1}",
            f'\tname = "VAL_STATE_{s + 1}"',
            # 300 people per map pixel (20 until 2026-10-04: the world held 75 million and
            # no country could man its starting army), or the Gazetteer's population
            f"\tmanpower = {max(100, int(f['pop'])) if f.get('pop') is not None else max(15000, px * POP_PER_PX)}",
            *(["\tresources = {", *[f"\t\t{r} = {v}" for r, v in res.items()], "\t}"] if res else []),
            f"\tstate_category = {cat}",
            "\thistory = {",
            f"\t\towner = {tag}",
            f"\t\tadd_core_of = {tag}",
            *[f"\t\tadd_core_of = {t}" for t in extra_cores[s]],
            f"\t\tvictory_points = {{ {pid[cap]} {city_vp.get(cap, 10 if is_cap else CITY_VP if cap in city_of else 1)} }}",
            *[f"\t\tvictory_points = {{ {pid[e]} {city_vp.get(e, CITY_VP)} }}" for e in extra_vps[s]],
            "\t\tbuildings = {",
            *bl,
            "\t\t}",
            "\t}",
            "\tprovinces = {",
            fmt_ids(pid[g]),
            "\t}",
            "}",
            "",
        ])
        write(f"history/states/{s + 1}-State_{s + 1}.txt", text)

    # ---------------------------------------------------------------- strategic regions
    region_name = []
    # names by region colour, from strategic_regions.py (a repainted region falls back)
    names_by_colour = json.load(open("source/region_names.json", encoding="utf-8")) \
        if os.path.exists("source/region_names.json") else {}
    land_count = defaultdict(int)
    sea_count = 0
    for r, rg in enumerate(regions):
        provs = rg["provinces"]
        if rg["kind"] == "land":
            c = Counter(owners[s] for s in rg["states"]).most_common(1)[0][0] \
                if rg["states"] else CONTINENTS[int(cont[provs[0]]) - 1]
            land_count[c] += 1
            region_name.append(names_by_colour.get(rg.get("colour"), f"{COUNTRIES[c][1]} Region {land_count[c]}"))
        else:
            sea_count += 1
            region_name.append(names_by_colour.get(rg.get("colour"), f"Sea Zone {sea_count}"))
        cy = np.average([reg["centre"][i][0] for i in provs], weights=[size[i] for i in provs])
        lat = (cy - H / 2) / (H / 2)
        body = [
            "strategic_region = {",
            f"\tid = {r + 1}",
            f'\tname = "VAL_REGION_{r + 1}"',
            "\tprovinces = {",
            fmt_ids(pid[provs]),
            "\t}",
        ]
        if rg["kind"] == "sea":
            share = np.mean([coastal[i] for i in provs])
            body.append(f"\tnaval_terrain = {'water_shallow_sea' if share > 0.5 else 'water_deep_ocean'}")
        body += [weather_block(lat), "}", ""]
        write(f"map/strategicregions/{r + 1}-Region_{r + 1}.txt", "\n".join(body))

    # ---------------------------------------------------------------- positions
    rows = []
    for s, g in enumerate(states):
        order = sorted(g, key=lambda i: (-size[i], i))
        for btype, count in STATE_BUILDINGS:
            for k in range(count):
                i = order[k % len(order)]
                y, x = spot(i, k // len(order) + (1 if btype != "arms_factory" else 0))
                rows.append(f"{s + 1};{btype};{pos(y, x)};0.00;0")
        if state_coastal[s]:
            i = max((i for i in g if i in port), key=lambda i: port[i][0])
            _, S, ly, lx, sy, sx = port[i]
            rows.append(f"{s + 1};dockyard;{pos(ly, lx)};0.00;0")
    for i in range(n):
        if kind[i] != 1:
            continue
        s = state_of[i] + 1
        for k, btype in enumerate(PROVINCE_BUILDINGS):
            y, x = spot(i, k + 2)
            rows.append(f"{s};{btype};{pos(y, x)};0.00;0")
        if i in port:
            _, S, ly, lx, sy, sx = port[i]
            rot = math.atan2(-(sy - ly), ((sx - lx + W // 2) % W) - W // 2)
            rows.append(f"{s};naval_base_spawn;{pos(ly, lx)};{rot:.2f};{pid[S]}")
            rows.append(f"{s};floating_harbor;{sx + 0.5:.2f};9.50;{H - sy - 0.5:.2f};{rot:.2f};{pid[S]}")
            for btype in COASTAL_BUILDINGS:
                rows.append(f"{s};{btype};{pos(ly, lx)};{rot:.2f};0")
    # no trailing newline: the game reads an empty last line as a malformed row
    write("map/buildings.txt", "\n".join(rows))

    # unit positions, every kind vanilla's map gives (read from vanilla's unitstacks.txt, 2026-10-14):
    #   0, 9, 10, 21, 38   near the centre (standing, defending, ...)
    #   1-8 and 22-29      toward each neighbour, the longest borders first (moving, attacking)
    #   11-18 and 30-37    fleets, spread across a sea province
    #   19, 20             ships in port: the coast and just offshore of a coastal province
    # Until then only the required kinds were written, and the game placed the rest itself: in two
    # of Merlo's large sea provinces "too far away from center" (error.log, 2026-10-14).
    nb = neighbours(lab, anchor)

    def toward(i, j_y, j_x):
        """A point inside province i, part of the way from its anchor to a border point."""
        ay, ax = anchor[i]
        dx = ((j_x - ax + W / 2) % W) - W / 2
        for f in (0.55, 0.45, 0.35, 0.25, 0.15):
            yy, xx = int(round(ay + f * (j_y - ay))), int(round(ax + f * dx)) % W
            if 0 <= yy < H and lab[yy, xx] == i and inner[yy, xx] >= 2:
                return yy, xx
        return spot(i, 0)

    def ring(i, k):
        """The k-th of eight fleet spots round a sea province's anchor."""
        ay, ax = anchor[i]
        r = min(30.0, max(6.0, 0.35 * math.sqrt(size[i])))
        a = k * math.pi / 4
        while r >= 3:
            yy, xx = int(round(ay + r * math.sin(a))), int(round(ax + r * math.cos(a))) % W
            if 0 <= yy < H and lab[yy, xx] == i and inner[yy, xx] >= 3:
                return yy, xx
            r *= 0.75
        return spot(i, k + 1)

    def facing(y0, x0, y1, x1):
        return math.atan2(-(y1 - y0), ((x1 - x0 + W // 2) % W) - W // 2)

    rows = []
    for i in range(n):
        if kind[i] == 2:
            continue
        land = kind[i] == 1
        off = 0.3 if land else 1.0

        def row(t, y, x, rot=0.0, o=off, sea_level=not land):
            yy = 9.5 if sea_level else world_y(y, x)
            rows.append(f"{pid[i]};{t};{x + 0.5:.2f};{yy:.2f};{H - y - 0.5:.2f};{rot:.2f};{o:.2f}")
        for k, t in enumerate((0, 9, 10, 21, 38)):
            y, x = spot(i, k)
            row(t, y, x)
        ay, ax = anchor[i]
        near = nb.get(i, [])[:8] or [(None, 0, ay, ax)]
        if not land and len(near) < 2:                  # a sea province needs kinds 2 and 23 too
            near = near + [(None, 0, ay, ax)]
        for k, (j, _, by, bx) in enumerate(near):
            y, x = toward(i, by, bx)
            rot = facing(ay, ax, by, bx) if j is not None else 0.0
            row(1 + k, y, x, rot)
            row(22 + k, y, x, rot)
        if not land:
            for k in range(8):
                y, x = ring(i, k)
                row(11 + k, y, x, facing(ay, ax, y, x))
                row(30 + k, y, x, facing(ay, ax, y, x))
        if land and i in port:
            _, S, ly, lx, sy, sx = port[i]
            rot = facing(ly, lx, sy, sx)
            row(19, ly, lx, rot, 0.3)
            row(20, sy, sx, rot, 0.3, sea_level=True)
        else:
            y, x = spot(i, 0)
            row(19, y, x)
            row(20, y, x)
    write("map/unitstacks.txt", "\n".join(rows) + "\n")

    # the AI's faction theaters: each continent's land regions and the sea regions on its coasts,
    # split where they don't connect (a theater must be one connected area)
    region_of = np.full(n, -1)
    for r, rg in enumerate(regions):
        region_of[rg["provinces"]] = r
    radj = defaultdict(set)
    for i, near in nb.items():
        for j, _, _, _ in near:
            a_, b_ = region_of[i], region_of[j]
            if a_ != b_ and a_ >= 0 and b_ >= 0:
                radj[a_].add(b_)
    land_cont = {r: Counter(int(cont[i]) for i in rg["provinces"]).most_common(1)[0][0]
                 for r, rg in enumerate(regions) if rg["kind"] == "land"}
    theater_list = []
    for ci, c in enumerate(CONTINENTS, start=1):
        own = {r for r, k in land_cont.items() if k == ci}
        area = own | {s for r in own for s in radj[r] if regions[s]["kind"] == "sea"}
        seen, parts = set(), []
        for start in sorted(own):
            if start in seen:
                continue
            comp, todo = [], [start]
            seen.add(start)
            while todo:
                r = todo.pop()
                comp.append(r)
                for s in radj[r]:
                    if s in area and s not in seen:
                        seen.add(s)
                        todo.append(s)
            parts.append(comp)
        parts.sort(key=len, reverse=True)
        for k, comp in enumerate(parts):
            if not any(r in own for r in comp):
                continue
            first = min(r for r in comp if r in own)
            ids = [first + 1] + sorted(r + 1 for r in comp if r != first)
            theater_list.append((c + ("" if k == 0 else f"_{k + 1}"), c, ids))
    write("common/ai_faction_theaters/ai_faction_theaters.txt",
          vanilla_parts.theaters([(key, c, ids) for key, c, ids in theater_list]))

    rows = []
    for r, rg in enumerate(regions):
        order = sorted(rg["provinces"], key=lambda i: (-size[i], i))
        for k, sz in enumerate(("small", "big")):
            i = order[min(k, len(order) - 1)]
            y, x = spot(i, 1)
            rows.append(f"{r + 1};{pos(y, x)};{sz}")
    write("map/weatherpositions.txt", "\n".join(rows) + "\n")

    # supply hubs: one in every state, unless the Gazetteer places a nation's own (then those
    # and its capital); railways only from the Gazetteer
    ghubs = gazetteer.hubs(G, lab, kind, state_of, rj["owners"])
    nodes = [state_capital[s] for s in range(len(states)) if COUNTRIES[owners[s]][0] not in ghubs]
    for tag, hs in ghubs.items():
        nodes += hs + [state_capital[capital_state[by_tag[tag]]]]
    write("map/supply_nodes.txt", "".join(f"1 {pid[c]}\n" for c in dict.fromkeys(nodes)))
    rails = gazetteer.railways(G, lab, kind, reg["centre"], rj["adjacency"], gnotes)
    write("map/railways.txt", "".join(f"{lv} {len(line)} {' '.join(str(pid[i]) for i in line)}\n" for lv, line in rails))
    write("map/positions.txt", "")

    # ---------------------------------------------------------------- other map files
    write("map/default.map", "\n".join([
        'definitions = "definition.csv"', 'provinces = "provinces.bmp"',
        'positions = "positions.txt"', 'terrain = "terrain.bmp"', 'rivers = "rivers.bmp"',
        'heightmap = "heightmap.bmp"', 'tree_definition = "trees.bmp"',
        'continent = "continent.txt"', 'adjacency_rules = "adjacency_rules.txt"',
        'adjacencies = "adjacencies.csv"', '#climate = "climate.txt"',
        'ambient_object = "ambient_object.txt"', 'seasons = "seasons.txt"', "",
        "# Define which indices in trees.bmp palette which should count as trees for "
        "automatic terrain assignment", "tree = { 3 4 7 10 }", ""]))
    write("map/continent.txt", "continents = {\n" + "".join(f"\t{c}\n" for c in CONTINENTS) + "}\n")
    write("map/adjacencies.csv", "From;To;Type;Through;start_x;start_y;stop_x;stop_y;"
          "adjacency_rule_name;Comment\n-1;-1;;-1;-1;-1;-1;-1;-1\n", crlf=True)
    write("map/adjacency_rules.txt", "# No straits or canals on the placeholder map.\n")
    # ambient objects: vanilla's wind and frame, water ambience moved to our open seas
    water_far = ndi.distance_transform_edt(pix_kind != 1)
    spots = []
    for gy in range(2):
        for gx in range(7):
            y0, y1 = gy * H // 2, (gy + 1) * H // 2
            x0, x1 = gx * W // 7, (gx + 1) * W // 7
            sub = water_far[y0:y1, x0:x1]
            k = int(np.argmax(sub))
            yy, xx = divmod(k, x1 - x0)
            if sub.flat[k] > 40:
                spots.append((x0 + xx, H - (y0 + yy)))
    obj = "".join(f"\tobject={{\n\t\tname=\"ambient_water\"\n\t\tposition={{\n\t\t\t{x} 10 {z} \n\t\t}}\n"
                  f"\t\trotation={{\n\t\t\t0 0 0 \n\t\t}}\n\t}}\n" for x, z in spots)

    def frame(tp, name, scale, x, y, z):
        return (f'type={{\n\ttype="{tp}"\n\tuse_animation=no\n\tscale={scale:.6f}\n\talways_visible=yes\n'
                f'\tobject={{\n\t\tname="{name}"\n\t\tposition={{\n\t\t\t{x} {y} {z} \n\t\t}}\n'
                f'\t\trotation={{\n\t\t\t0 0 0 \n\t\t}}\n\t}}\n}}\n')
    write("map/ambient_object.txt",
          'type={\n\ttype="ambient_wind_entity"\n\tuse_animation=no\n\talways_visible=yes\n'
          '\tobject={\n\t\tname="ambient_wind"\n\t\tposition={\n\t\t\t0 0 0 \n\t\t}\n'
          '\t\trotation={\n\t\t\t0 0 0 \n\t\t}\n\t}\n}\n'
          'type={\n\ttype="ambient_water_entity"\n\tuse_animation=no\n\tscale=10.000000\n'
          + obj + "}\n"
          + frame("frame_border_entity", "frame_border_entity_top", 100, 0, 0, H + 142)
          + frame("frame_border_bottom_entity", "frame_border_bottom_entity_bottom", 100, 0, 0, -140)
          + frame("frame_border_logo_entity", "frame_border_logo_entity_top", 300, W // 2, 0, H + 82))

    # ---------------------------------------------------------------- countries
    # the bookmark recommends only the placeholder countries, to keep the list short
    tags = [COUNTRIES[c][0] for c in present if c in PLACEHOLDERS]
    # generic portraits, name lists and graphical culture by the capital's continent
    tag_continent = {COUNTRIES[c][0]: CONTINENTS[int(cont[states[capital_state[c]][0]]) - 1]
                     for c in present}
    gfx = cultures.write_files(write, tag_continent, CONTINENTS)
    # every ruler (and Rouental's other party leaders) is a set character (author)
    ideology_of = ideologies.ideology_of()
    ruling, recruits, leader_blocks, leader_loc, used_names = {}, {}, [], [], set()
    named_leaders = dict(nations.NAMED_LEADERS)
    # map colours that differ from the .pdn paint: nations.py's, then the Gazetteer's
    display_colour = {**nations.DISPLAY_COLOUR, **gazetteer.colours(G)}
    for c in present:
        tag = COUNTRIES[c][0]
        # the Gazetteer's ruling sub-ideology, parties and ruler, over nations.LEADERS
        subs = gazetteer.leaders(tag, nations.LEADERS.get(tag, []), G.get(tag),
                                 tag in nations.HAND_MADE, named_leaders, nations.PORTRAITS)
        blocks, lloc, ids = cultures.leaders(tag, tag_continent[tag], subs, ideology_of, used_names,
                                             named_leaders)
        leader_blocks += blocks
        leader_loc += lloc
        recruits[tag] = [f"recruit_character = {i}" for i in ids]
        ruling[tag] = ideology_of[subs[0]] if subs and tag not in nations.HAND_MADE else \
            nations.RULING.get(tag, "neutrality")
    write("common/characters/valsora_leaders.txt",
          "# Generated by scripts/cultures.py from nations.LEADERS\ncharacters = {\n"
          + "".join(leader_blocks) + "}\n")
    # a starting army for every country that owns land, sized by its states
    # (Rouental's own royal host is in nations.py)
    army = {}
    for c in present:
        tag = COUNTRIES[c][0]
        mine = [s for s in range(len(states)) if owners[s] == c]
        army[tag] = []
        if tag == "ROU" or not mine:
            continue
        mine.sort(key=lambda s: (s != capital_state[c], -len(states[s]), s))
        write(f"history/units/{tag}_2036.txt", nations.generic_oob(tag, [int(pid[state_capital[s]]) for s in mine]))
        army[tag] = [nations.GENERIC_ARMY_TECH, *nations.oob_manpower(nations.generic_divisions(len(mine))),
                     f'set_oob = "{tag}_2036"']
    for c in present:
        tag, name, adj, col = COUNTRIES[c]
        fname = country_file(c)
        write(f"common/countries/Valsora {fname}.txt",
              f"graphical_culture = {gfx[tag]}_gfx\n"
              f"graphical_culture_2d = {gfx[tag]}_2d\n"
              "color = rgb {{ {} {} {} }}\n".format(*display_colour.get(tag, col)))
        write(f"history/countries/{tag} - {fname}.txt", "\n".join([
            f"capital = {capital_state[c] + 1}",
            "set_research_slots = 3",
            "set_stability = 0.6",
            "set_war_support = 0.3",
            "set_politics = {",
            f"\truling_party = {ruling[tag]}",
            '\tlast_election = "2032.1.1"',
            "\telection_frequency = 48",
            f"\telections_allowed = {'yes' if ruling[tag] == 'democratic' else 'no'}",
            "}",
            # every country starts with an equal mix of the five ideologies (author),
            # unless nations.POPULARITIES says otherwise
            "set_popularities = {",
            *[f"\t{i} = {nations.POPULARITIES.get(tag, {}).get(i, 100 // len(IDEOLOGIES))}" for i in IDEOLOGIES],
            "}",
            *nations.HISTORY.get(tag, []),
            *army[tag],
            *recruits[tag],
            ""]))
        # flags: the author's source/flags/TAG.png (and TAG_<ideology>.png for a flag
        # used only while that ideology rules), else a placeholder in the map colour
        variants = {tag: FLAGS / f"{tag}.png"}
        variants.update({f"{tag}_{i}": FLAGS / f"{tag}_{i}.png" for i in IDEOLOGIES
                         if (FLAGS / f"{tag}_{i}.png").exists()})
        # cosmetic tags (map colour per government) use the same ideology flags
        variants.update({cosmetic(tag, i): FLAGS / f"{tag}_{i}.png" for i in nations.LOOKS.get(tag, {})
                         if (FLAGS / f"{tag}_{i}.png").exists()})
        variants.update({cos: FLAGS / v[4] for cos, v in nations.COSMETICS.items()
                         if cos.startswith(tag + "_")})
        for name, src in variants.items():
            if src.exists():
                big = Image.open(src).convert("RGBA")
            else:
                flag = np.zeros((52, 82, 4), np.uint8)
                flag[..., 3] = 255
                flag[..., :3] = col
                flag[18:34, :, :3] = 255
                big = Image.fromarray(flag)
            for path, (w, h) in (("", (82, 52)), ("medium/", (41, 26)), ("small/", (10, 7))):
                img = np.asarray(big.resize((w, h), Image.LANCZOS if src.exists() else Image.BOX))
                (OUT / f"gfx/flags/{path}").mkdir(parents=True, exist_ok=True)
                write_tga(OUT / f"gfx/flags/{path}{name}.tga", img)
    write("common/country_tags/valsora_countries.txt",
          "".join(f'{COUNTRIES[c][0]} = "countries/Valsora {country_file(c)}.txt"\n' for c in present))

    write("common/bookmarks/valsora.txt", "\n".join([
        "bookmarks = {",
        "\tbookmark = {",
        '\t\tname = "VALSORA_BOOKMARK"',
        '\t\tdesc = "VALSORA_BOOKMARK_DESC"',
        f"\t\tdate = {vanilla_parts.START_DATE}",
        '\t\tpicture = "GFX_select_date_valsora"',
        f'\t\tdefault_country = "{tags[0]}"',
        "\t\tdefault = yes",
        *[f'\t\t{t} = {{ history = "VALSORA_PLACEHOLDER_DESC" ideology = neutrality }}' for t in tags],
        '\t\t"---" = { history = "VALSORA_PLACEHOLDER_DESC" }',
        "\t\teffect = { randomize_weather = 22345 }",
        "\t}",
        "}",
        ""]))

    # ---------------------------------------------------------------- vanilla switches
    # Folders we replace must still contain a valid file.
    write("events/valsora_events.txt", "add_namespace = valsora\n")
    # a country with LOOKS changes map colour (cosmetic tag) with its government
    looks = []
    for tag, per in nations.LOOKS.items():
        branches = [f"\t\t\t\t{'if' if k == 0 else 'else_if'} = {{ limit = {{ has_government = {i} }} "
                    f"set_cosmetic_tag = {cosmetic(tag, i)} }}" for k, i in enumerate(per)]
        looks += ["\t\t\tif = {", f"\t\t\t\tlimit = {{ tag = {tag} }}", *branches,
                  "\t\t\t\telse = { drop_cosmetic_tag = yes }", "\t\t\t}"]
    # a character who comes to rule takes their regnal name (nations.REGNAL_NAMES)
    regnal = [f"\t\t\tif = {{ limit = {{ tag = {tag} has_country_leader = {{ character = {c} ruling_only = yes }} }} "
              f"set_character_name = {{ character = {c} name = {key} }} }}"
              for c, (tag, key) in nations.REGNAL_NAMES.items()]
    write("common/on_actions/valsora_on_actions.txt", "\n".join([
        "on_actions = {", "\ton_ruling_party_change = {", "\t\teffect = {", *looks, *regnal,
        # the Reibonnaise nations' opinions follow who is communist (nations.py)
        "\t\t\tvalsora_reibonnaise_opinions = yes",
        "\t\t}", "\t}",
        "\ton_startup = {", "\t\teffect = {", "\t\t\tvalsora_reibonnaise_opinions = yes", "\t\t}", "\t}",
        "}", ""]))
    # the map colour comes from colors.txt, not the country file: tags missing there get
    # generated colours (in-game, 2026-09-29), so ours replaces vanilla's
    write("common/countries/colors.txt", "#reload countrycolors\n\n" + "".join(
        f"{COUNTRIES[c][0]} = {{\n\tcolor = rgb {{ {r} {g} {b} }}\n\tcolor_ui = rgb {{ {' '.join(map(str, ui_colour((r, g, b))))} }}\n}}\n"
        for c in present for r, g, b in [display_colour.get(COUNTRIES[c][0], COUNTRIES[c][3])]))
    write("common/countries/cosmetic.txt", "".join(
        f"{cosmetic(tag, i)} = {{\n\tcolor = rgb {{ {r} {g} {b} }}\n\tcolor_ui = rgb {{ {' '.join(map(str, ui_colour((r, g, b))))} }}\n}}\n"
        for tag, per in nations.LOOKS.items() for i, (r, g, b) in per.items())
        + "".join(f"{cos} = {{\n\tcolor = rgb {{ {r} {g} {b} }}\n\tcolor_ui = rgb {{ {' '.join(map(str, ui_colour((r, g, b))))} }}\n}}\n"
                  for cos, (_, _, _, (r, g, b), _) in nations.COSMETICS.items()))
    ideologies.write_files(write, OUT)
    for d in ("common/decisions", "common/ai_strategy", "common/ai_strategy_plans",
              "history/units", "history/general"):
        write(f"{d}/valsora_placeholder.txt", "# Intentionally empty: vanilla content is switched off.\n")
    # vanilla's files the mod ships changed (2036; the generic AI strategies, events and
    # on_actions), stand-ins for its removed decisions, histories for Earth's country tags
    shipped = vanilla_parts.files()
    for rel, text, bom in shipped:
        write(rel, text, bom=bom)
    write("events/valsora_vanilla_event_stand_ins.txt", vanilla_parts.event_stand_ins(shipped)[0])
    cat, stand_ins = vanilla_parts.stand_ins()
    write("common/decisions/categories/valsora_vanilla_stand_ins.txt", cat)
    write("common/decisions/valsora_vanilla_stand_ins.txt", stand_ins)
    for fname, text in vanilla_parts.history_stubs(1).items():
        write(f"history/countries/{fname}", text)
    write("common/defines/valsora_game.lua", vanilla_parts.defines())
    write("localisation/english/replace/valsora_vanilla_years_l_english.yml", vanilla_parts.year_names(), bom=True)
    # vanilla's tutorial points at Earth states/provinces; keep only its first, id-free step
    write("tutorial/tutorial.txt", 'tutorial = {\n\twindow = "tutorial_screen_1"\n'
          '\tuse_mil_fac = {\n\t\ttextbox = "obj_1"\n\t}\n}\n')
    # vanilla's country-specific naval AI (ENG FRA GER ITA JAP SOV USA) is overridden
    for t in ("ENG", "FRA", "GER", "ITA", "JAP", "SOV", "USA"):
        write(f"common/ai_navy/goals/goals_{t}.txt", "# overridden: country not on this map\n")
        write(f"common/ai_navy/fleet/{t}_fleet_templates.txt", "# overridden: country not on this map\n")
        write(f"common/ai_navy/taskforce/{t}_taskforce_templates.txt",
              "# overridden: country not on this map\n")

    # ---------------------------------------------------------------- localisation
    loc = ["l_english:"]
    names_of = {}
    for c in present:
        tag, name, adj, _ = COUNTRIES[c]
        # the Gazetteer's names and titles over nations.FORMAL_NAMES and IDEOLOGY_NAMES
        (name, formal, adj), per = gazetteer.names(tag, (name, nations.FORMAL_NAMES.get(tag, name), adj),
                                                   nations.IDEOLOGY_NAMES.get(tag, {}),
                                                   G.get(tag, {}).get("politics"))
        names_of[tag] = per
        loc += [f' {tag}:0 "{name}"', f' {tag}_DEF:0 "{formal}"', f' {tag}_ADJ:0 "{adj}"']
        for ideo in IDEOLOGIES:
            i_name, i_def, i_adj = per[ideo]
            loc += [f' {tag}_{ideo}:0 "{i_name}"', f' {tag}_{ideo}_DEF:0 "{i_def}"',
                    f' {tag}_{ideo}_ADJ:0 "{i_adj}"']
    loc += [f' {c}:0 "{COUNTRIES[c][1]}"' for c in CONTINENTS]  # continent names
    loc += [f' theater_valsora_{key}:0 "{COUNTRIES[c][1]}"' for key, c, _ in theater_list]  # AI theaters
    loc += [f' VAL_STATE_{s + 1}:0 "{state_name[s]}"' for s in range(len(states))]
    loc += [f' VAL_REGION_{r + 1}:0 "{region_name[r]}"' for r in range(len(regions))]
    loc += [' VALSORA_BOOKMARK:0 "Valsora"',
            ' VALSORA_BOOKMARK_DESC:0 "The world of Valsora, 1 January 2036."',
            ' VALSORA_PLACEHOLDER_DESC:0 "A placeholder country, until the real ones are drawn."']
    loc += nations.LOCALISATION
    # cosmetic tags need their own names, for every ideology
    for c in present:
        tag, name, adj, _ = COUNTRIES[c]
        for look in nations.LOOKS.get(tag, {}):
            cos = cosmetic(tag, look)
            n0, d0, a0 = names_of[tag][look]
            loc += [f' {cos}:0 "{n0}"', f' {cos}_DEF:0 "{d0}"', f' {cos}_ADJ:0 "{a0}"']
            for ideo in IDEOLOGIES:
                n1, d1, a1 = names_of[tag][ideo]
                loc += [f' {cos}_{ideo}:0 "{n1}"', f' {cos}_{ideo}_DEF:0 "{d1}"', f' {cos}_{ideo}_ADJ:0 "{a1}"']
    for cos, (n0, d0, a0, _, _) in nations.COSMETICS.items():
        loc += [f' {cos}:0 "{n0}"', f' {cos}_DEF:0 "{d0}"', f' {cos}_ADJ:0 "{a0}"']
        loc += [f' {cos}_{i}{suf}:0 "{v}"' for i in IDEOLOGIES for suf, v in (("", n0), ("_DEF", d0), ("_ADJ", a0))]
    loc += leader_loc
    loc += superevents.write_files(write, OUT)
    write("localisation/english/valsora_l_english.yml", "\n".join(loc) + "\n", bom=True)
    nations.write_files(write, OUT, {nm: s + 1 for nm, s in state_by_name.items()},
                        {nm: int(pid[state_capital[s]]) for nm, s in state_by_name.items()})
    vp_ids = {int(pid[c]) for c in state_capital} | {int(pid[e]) for v in extra_vps.values() for e in v}
    city_names = {int(pid[p]): name for p, name in city_of.items()}
    for key, name in nations.CITY_NAMES.items():
        if isinstance(key, str) and key.startswith("capital:"):
            c = by_tag[key[8:]]
            if c not in capital_state:
                continue  # that country owns no land at the moment
            if "cities" in G.get(key[8:], {}):
                continue  # its cities are the Gazetteer's, named there
            key = int(pid[state_capital[capital_state[c]]])
        if city_names.get(key, name) != name:
            raise SystemExit(f"nations.CITY_NAMES calls {city_names[key]} {name}")
        city_names[key] = name
    stale = sorted(set(city_names) - vp_ids)
    if stale:
        raise SystemExit(f"nations.CITY_NAMES names provinces that are not victory points: {stale}")
    # victory point names share vanilla's keys, so they go in replace/ to win over Earth names
    vp = ["l_english:"] + [f' VICTORY_POINTS_{pid[c]}:0 "{city_names.get(int(pid[c]), state_name[s] + " City")}"'
                           for s, c in enumerate(state_capital)] + \
        [f' VICTORY_POINTS_{pid[e]}:0 "{city_names[int(pid[e])]}"' for v in extra_vps.values() for e in v]
    write("localisation/english/replace/valsora_victory_points_l_english.yml", "\n".join(vp) + "\n",
          bom=True)

    # ---------------------------------------------------------------- descriptor
    desc = ["version=\"0.2\"", "tags={", '\t"Map"', '\t"Total Conversion"', "}",
            f'name="{MOD_NAME}"', 'supported_version="1.19.*"', 'picture="thumbnail.png"']
    desc += [f'replace_path="{rp}"' for rp in REPLACE_PATHS]
    write("descriptor.mod", "\n".join(desc) + "\n")
    Path("build", f"{MOD_DIR_NAME}.mod").write_text(
        "\n".join(desc + [f'path="mod/{MOD_DIR_NAME}"']) + "\n")
    thumb = np.where(pix_kind[..., None] == 1, np.array([96, 140, 70]),
                     np.array([35, 60, 105])).astype(np.uint8)
    Image.fromarray(thumb).resize((512, 256), Image.BOX).save(OUT / "thumbnail.png")
    for m in gnotes:
        print("note:", m)
    print(f"wrote {OUT}: {n} provinces, {len(states)} states, {len(regions)} strategic regions"
          + (f"; Gazetteer facts of {len(G)} nations, {len(rails)} railway lines" if G else ""))


if __name__ == "__main__":
    main()
