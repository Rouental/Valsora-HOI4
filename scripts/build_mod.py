"""Write the HOI4 mod from the province, state and region data.

Reads work/provinces.npz, work/regions.npz and work/regions.json.
Writes build/valsora_test/ (the mod folder) and build/valsora_test.mod (the
launcher's outer descriptor).
"""
import json
import math
import shutil
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

from common import MAP_W, MAP_H, CONTINENTS, MOD_NAME, MOD_DIR_NAME
from imgio import write_bmp, write_dds, write_tga, palette_from_header

W, H = MAP_W, MAP_H
OUT = Path("build") / MOD_DIR_NAME
PAL = Path("source/palettes")
CRLF = "\r\n"

# One placeholder country per continent: tag, name, adjective, colour.
COUNTRIES = {
    "nonscio": ("NSC", "Nonscio", "Nonscian", (216, 84, 84)),
    "araseos": ("ARS", "Araseos", "Araseosi", (116, 152, 206)),
    "aislada": ("AIS", "Aislada", "Aisladan", (70, 170, 70)),
    "solitas": ("SLT", "Solitas", "Solitan", (214, 110, 214)),
    "yastreovakia": ("YAS", "Yastreovakia", "Yastreovakian", (96, 190, 150)),
    "usnistan": ("USN", "Usnistan", "Usnistani", (184, 172, 100)),
    "orientalis": ("ORI", "Orientalis", "Orientalian", (236, 160, 70)),
}

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
# Unit stack types vanilla provinces carry (measured in vanilla-derived maps).
LAND_STACKS = [0, 1, 9, 10, 21, 22, 38]
SEA_STACKS = [0, 1, 2, 9, 10, 11, 12, 21, 22, 23, 30, 31, 38]


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
    n = len(kind)
    pid = np.arange(n) + 1  # HOI4 province ids start at 1
    pix_kind = kind[lab]  # repairs may have moved single pixels between kinds

    # ---------------------------------------------------------------- provinces.bmp
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
    terrain = {0: "ocean", 1: "plains", 2: "lakes"}
    ptype = {0: "sea", 1: "land", 2: "lake"}
    lines = ["0;0;0;0;land;false;unknown;0"]
    for i in range(n):
        r, g, bb = colors[i]
        lines.append(f"{pid[i]};{r};{g};{bb};{ptype[kind[i]]};{'true' if coastal[i] else 'false'};"
                     f"{terrain[kind[i]]};{int(cont[i]) if kind[i] == 1 else 0}")
    write("map/definition.csv", "\n".join(lines) + "\n", crlf=True)

    # ---------------------------------------------------------------- bitmaps
    height, d_sea = heightmap(pix_kind)
    write_bmp(OUT / "map/heightmap.bmp", height, palette_from_header(PAL / "heightmap.bmp.header.bin"))
    write_bmp(OUT / "map/terrain.bmp", np.where(pix_kind == 1, 0, 15).astype(np.uint8),
              palette_from_header(PAL / "terrain.bmp.header.bin"))
    write_bmp(OUT / "map/rivers.bmp", np.where(pix_kind == 1, 255, 254).astype(np.uint8),
              palette_from_header(PAL / "rivers.bmp.header.bin"))
    # cities.bmp index 4 belongs to no city group: no generated town meshes
    write_bmp(OUT / "map/cities.bmp", np.full((H, W), 4, np.uint8),
              palette_from_header(PAL / "cities.bmp.header.bin"))
    # trees.bmp at vanilla's 75/256 of the map size; index 0 = no trees
    write_bmp(OUT / "map/trees.bmp", np.zeros((H * 75 // 256, W * 75 // 256), np.uint8),
              palette_from_header(PAL / "trees.bmp.header.bin"))
    write_bmp(OUT / "map/world_normal.bmp", normal_map(height))
    textures(pix_kind, height, d_sea)

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
        c = CONTINENTS[int(cont[g[0]]) - 1]
        cont_count[c] += 1
        state_name.append(f"{COUNTRIES[c][1]} {cont_count[c]}")
    state_capital = [max(g, key=lambda i: (size[i], -i)) for g in states]
    state_coastal = [any(coastal[i] for i in g) for g in states]
    # country capital: the sizeable state nearest its continent's centre of mass
    capital_state = {}
    for ci, c in enumerate(CONTINENTS, 1):
        members = [s for s, g in enumerate(states) if cont[g[0]] == ci]
        cy = np.average([reg["centre"][i][0] for s in members for i in states[s]],
                        weights=[size[i] for s in members for i in states[s]])
        cx = np.average([reg["centre"][i][1] for s in members for i in states[s]],
                        weights=[size[i] for s in members for i in states[s]])
        big = [s for s in members if len(states[s]) >= 4] or members
        capital_state[c] = min(big, key=lambda s: np.hypot(*(np.mean(
            [reg["centre"][i] for i in states[s]], axis=0) - (cy, cx))))
    for s, g in enumerate(states):
        c = CONTINENTS[int(cont[g[0]]) - 1]
        tag = COUNTRIES[c][0]
        is_cap = capital_state[c] == s
        px = sum(int(size[i]) for i in g)
        cat = "city" if is_cap else ("small_island" if len(g) <= 2 else
                                     "town" if len(g) >= 16 else "rural")
        cap = state_capital[s]
        bl = [f"\t\t\tinfrastructure = {3 if is_cap else 2}"]
        if is_cap:
            bl += ["\t\t\tindustrial_complex = 3", "\t\t\tarms_factory = 2", "\t\t\tair_base = 2"]
            if state_coastal[s]:
                bl.append("\t\t\tdockyard = 1")
                port_prov = max((i for i in g if coastal[i] and i in port), key=lambda i: size[i])
                bl.append(f"\t\t\t{pid[port_prov]} = {{ naval_base = 3 }}")
        text = "\n".join([
            "state = {",
            f"\tid = {s + 1}",
            f'\tname = "VAL_STATE_{s + 1}"',
            f"\tmanpower = {max(1000, px * 20)}",
            f"\tstate_category = {cat}",
            "\thistory = {",
            f"\t\towner = {tag}",
            f"\t\tadd_core_of = {tag}",
            f"\t\tvictory_points = {{ {pid[cap]} {10 if is_cap else 1} }}",
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
    land_count = defaultdict(int)
    sea_count = 0
    for r, rg in enumerate(regions):
        provs = rg["provinces"]
        if rg["kind"] == "land":
            c = CONTINENTS[int(cont[states[rg["states"][0]][0]]) - 1]
            land_count[c] += 1
            region_name.append(f"{COUNTRIES[c][1]} Region {land_count[c]}")
        else:
            sea_count += 1
            region_name.append(f"Sea Zone {sea_count}")
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

    rows = []
    for i in range(n):
        if kind[i] == 2:
            continue
        y, x = spot(i, 0)
        types = LAND_STACKS if kind[i] == 1 else SEA_STACKS
        yy = world_y(y, x) if kind[i] == 1 else 9.5
        off = 0.3 if kind[i] == 1 else 1.0
        for t in types:
            rows.append(f"{pid[i]};{t};{x + 0.5:.2f};{yy:.2f};{H - y - 0.5:.2f};0.00;{off:.2f}")
    write("map/unitstacks.txt", "\n".join(rows) + "\n")

    rows = []
    for r, rg in enumerate(regions):
        order = sorted(rg["provinces"], key=lambda i: (-size[i], i))
        for k, sz in enumerate(("small", "big")):
            i = order[min(k, len(order) - 1)]
            y, x = spot(i, 1)
            rows.append(f"{r + 1};{pos(y, x)};{sz}")
    write("map/weatherpositions.txt", "\n".join(rows) + "\n")

    write("map/supply_nodes.txt", "".join(f"1 {pid[c]}\n" for c in state_capital))
    write("map/railways.txt", "")
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
    tags = []
    for c in CONTINENTS:
        tag, name, adj, col = COUNTRIES[c]
        tags.append(tag)
        write(f"common/countries/Valsora {name}.txt",
              "graphical_culture = western_european_gfx\n"
              "graphical_culture_2d = western_european_2d\n"
              f"color = {{ {col[0]} {col[1]} {col[2]} }}\n")
        write(f"history/countries/{tag} - {name}.txt", "\n".join([
            f"capital = {capital_state[c] + 1}",
            "set_research_slots = 3",
            "set_stability = 0.6",
            "set_war_support = 0.3",
            "set_politics = {",
            "\truling_party = neutrality",
            '\tlast_election = "1932.1.1"',
            "\telection_frequency = 48",
            "\telections_allowed = no",
            "}",
            "set_popularities = {",
            "\tdemocratic = 25",
            "\tfascism = 10",
            "\tcommunism = 10",
            "\tneutrality = 55",
            "}",
            ""]))
        flag = np.zeros((52, 82, 4), np.uint8)
        flag[..., 3] = 255
        flag[..., :3] = col
        flag[18:34, :, :3] = 255
        for path, (w, h) in (("", (82, 52)), ("medium/", (41, 26)), ("small/", (10, 7))):
            img = np.asarray(Image.fromarray(flag).resize((w, h), Image.BOX))
            (OUT / f"gfx/flags/{path}").mkdir(parents=True, exist_ok=True)
            write_tga(OUT / f"gfx/flags/{path}{tag}.tga", img)
    write("common/country_tags/valsora_countries.txt",
          "".join(f'{COUNTRIES[c][0]} = "countries/Valsora {COUNTRIES[c][1]}.txt"\n' for c in CONTINENTS))

    write("common/bookmarks/valsora.txt", "\n".join([
        "bookmarks = {",
        "\tbookmark = {",
        '\t\tname = "VALSORA_BOOKMARK"',
        '\t\tdesc = "VALSORA_BOOKMARK_DESC"',
        "\t\tdate = 1936.1.1.12",
        '\t\tpicture = "GFX_select_date_1936"',
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
    write("common/on_actions/valsora_on_actions.txt", "on_actions = {\n}\n")
    for d in ("common/decisions", "common/ai_strategy", "common/ai_strategy_plans",
              "history/units", "history/general"):
        write(f"{d}/valsora_placeholder.txt", "# Intentionally empty: vanilla content is switched off.\n")
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
    for c in CONTINENTS:
        tag, name, adj, _ = COUNTRIES[c]
        loc += [f' {tag}:0 "{name}"', f' {tag}_DEF:0 "{name}"', f' {tag}_ADJ:0 "{adj}"']
        for ideo in ("democratic", "fascism", "communism", "neutrality"):
            loc += [f' {tag}_{ideo}:0 "{name}"', f' {tag}_{ideo}_DEF:0 "{name}"',
                    f' {tag}_{ideo}_ADJ:0 "{adj}"']
        loc.append(f' {c}:0 "{name}"')
    loc += [f' VAL_STATE_{s + 1}:0 "{state_name[s]}"' for s in range(len(states))]
    loc += [f' VAL_REGION_{r + 1}:0 "{region_name[r]}"' for r in range(len(regions))]
    loc += [' VALSORA_BOOKMARK:0 "Valsora"',
            ' VALSORA_BOOKMARK_DESC:0 "Placeholder map of Valsora: square provinces, one country per continent."',
            ' VALSORA_PLACEHOLDER_DESC:0 "A placeholder country covering its whole continent."']
    write("localisation/english/valsora_l_english.yml", "\n".join(loc) + "\n", bom=True)
    # victory point names share vanilla's keys, so they go in replace/ to win over Earth names
    vp = ["l_english:"] + [f' VICTORY_POINTS_{pid[c]}:0 "{state_name[s]} City"'
                           for s, c in enumerate(state_capital)]
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
    print(f"wrote {OUT}: {n} provinces, {len(states)} states, {len(regions)} strategic regions")


if __name__ == "__main__":
    main()
