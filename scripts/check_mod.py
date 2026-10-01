"""Verify a built mod against every rule that HOI4 is known to crash or complain on.

Reads only the files on disk (not the pipeline's intermediates), so it also catches
writer bugs. Usage: python3 scripts/check_mod.py [build/valsora_test]
Exits non-zero if any error is found.
"""
import re
import struct
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi
from skimage.measure import label as sklabel

sys.path.insert(0, str(Path(__file__).parent))
from imgio import read_bmp  # noqa: E402
from rivers import problems as river_problems  # noqa: E402

VANILLA_STATE_CATEGORIES = {"wasteland", "enclave", "tiny_island", "pastoral", "small_island",
                            "rural", "town", "large_town", "city", "large_city", "metropolis",
                            "megalopolis"}
STATE_BUILDINGS = {"air_base": 1, "anti_air_building": 3, "arms_factory": 6,
                   "industrial_complex": 6, "fuel_silo": 1, "nuclear_reactor_spawn": 1,
                   "radar_station": 1, "rocket_site_spawn": 1, "stronghold_network": 1,
                   "synthetic_refinery": 1}
# vanilla 1.19.3 common/terrain/00_terrain.txt land categories
LAND_TERRAIN = {"plains", "forest", "hills", "mountain", "desert", "marsh", "jungle", "urban"}
PROVINCE_BUILDINGS = {"bunker", "special_project_facility_spawn", "supply_node"}
COASTAL_BUILDINGS = {"naval_base_spawn", "floating_harbor", "naval_headquarters",
                     "naval_supply_hub", "coastal_bunker"}
LAND_STACKS = {0, 1, 9, 10, 21, 22, 38}
SEA_STACKS = {0, 1, 2, 9, 10, 11, 12, 21, 22, 23, 30, 31, 38}

errors, notes = [], []


def err(msg):
    errors.append(msg)


def note(msg):
    notes.append(msg)


def blocks(text, key):
    """Top-level `key = { ... }` bodies (brace-matched)."""
    out = []
    for m in re.finditer(rf"\b{key}\s*=\s*\{{", text):
        depth, i = 1, m.end()
        while depth:
            depth += {"{": 1, "}": -1}.get(text[i], 0)
            i += 1
        out.append(text[m.end():i - 1])
    return out


def field(body, key):
    m = re.search(rf"\b{key}\s*=\s*\"?([\w.\-]+)\"?", body)
    return m.group(1) if m else None


def id_list(body, key):
    b = blocks(body, key)
    return [int(x) for x in b[0].split()] if b else []


def main(mod):
    mod = Path(mod)
    strip = lambda t: re.sub(r"#[^\n]*", "", t)  # noqa: E731

    # ------------------------------------------------------------ file names
    # Windows ignores case: two names differing only in case are one file there
    seen = {}
    for f in mod.rglob("*"):
        k = str(f.relative_to(mod)).lower()
        if k in seen:
            err(f"{f.relative_to(mod)} and {seen[k]} are the same file on Windows (case)")
        seen[k] = f.relative_to(mod)
        if not str(f.relative_to(mod)).isascii():
            err(f"{f.relative_to(mod)}: file names must be ASCII (accents are a risk in mod paths)")

    # ------------------------------------------------------------ provinces.bmp
    pb = read_bmp(mod / "map/provinces.bmp")
    W, H = pb["width"], pb["height"]
    if pb["bpp"] != 24 or pb["header"] != 40:
        err(f"provinces.bmp must be 24-bit with a 40-byte header (got {pb['bpp']}, {pb['header']})")
    if W % 256 or H % 256:
        err(f"map size {W}x{H} is not a multiple of 256")
    if W * H > 13_238_272:
        err(f"map area {W * H} exceeds HOI4's ~13,238,272 pixel limit")
    if (mod / "map/provinces.bmp").stat().st_size > 40 * 1024 * 1024:
        err("provinces.bmp is over 40 MiB")
    rgb = pb["img"].astype(np.int64)
    code = (rgb[..., 0] << 16) | (rgb[..., 1] << 8) | rgb[..., 2]

    # ------------------------------------------------------------ definition.csv
    raw = (mod / "map/definition.csv").read_bytes()
    if b"\r\n" not in raw or raw.count(b"\n") != raw.count(b"\r\n"):
        err("definition.csv must use CRLF line endings")
    lines = raw.decode().strip().splitlines()
    if lines[0] != "0;0;0;0;land;false;unknown;0":
        err(f"definition.csv first line is {lines[0]!r}")
    continents = blocks(strip((mod / "map/continent.txt").read_text()), "continents")[0].split()
    ids, cols, types, coast_def, conts = [], [], [], [], []
    for ln in lines[1:]:
        f = ln.split(";")
        ids.append(int(f[0]))
        cols.append((int(f[1]) << 16) | (int(f[2]) << 8) | int(f[3]))
        types.append(f[4])
        coast_def.append(f[5] == "true")
        conts.append(int(f[7]))
        if f[4] not in ("land", "sea", "lake"):
            err(f"province {f[0]}: bad type {f[4]}")
        want = {"sea": {"ocean"}, "lake": {"lakes"}}.get(f[4], LAND_TERRAIN)
        if f[6] not in want:
            err(f"province {f[0]}: {f[4]} with terrain {f[6]}")
        if f[4] == "land" and not 1 <= int(f[7]) <= len(continents):
            err(f"province {f[0]}: land with continent {f[7]}")
    n = len(ids)
    if ids != list(range(1, n + 1)):
        err("province ids are not contiguous from 1")
    if len(set(cols)) != n:
        err("duplicate province colours in definition.csv")
    col_to_id = dict(zip(cols, ids))
    uniq = np.unique(code)
    missing = [c for c in uniq if c not in col_to_id]
    if missing:
        err(f"{len(missing)} colours in provinces.bmp have no definition")
    unused = set(cols) - set(uniq.tolist())
    if unused:
        err(f"{len(unused)} defined provinces do not appear in provinces.bmp")
    lut_keys = np.array(sorted(col_to_id))
    lut_vals = np.array([col_to_id[k] for k in lut_keys])
    prov = lut_vals[np.searchsorted(lut_keys, code)] - 1  # 0-based
    kind = np.array([{"sea": 0, "land": 1, "lake": 2}[t] for t in types])

    # ------------------------------------------------------------ province shapes
    size = np.bincount(prov.ravel(), minlength=n)
    if size.min() < 8:
        err(f"{(size < 8).sum()} provinces under 8 px (HOI4 minimum)")
    regions_n = int(sklabel(prov, background=-1, connectivity=1).max())
    if regions_n != n:
        err(f"{regions_n - n} provinces are not 4-connected")
    for i, sl in enumerate(ndi.find_objects(prov + 1)):
        if sl[0].stop - sl[0].start >= H / 8 or sl[1].stop - sl[1].start >= W / 8:
            err(f"province {i + 1} bounding box exceeds 1/8 of the map")
    a, b = prov[:-1], np.roll(prov, -1, axis=1)[:-1]
    c, d = prov[1:], np.roll(prov, -1, axis=1)[1:]
    xc = (a != b) & (a != c) & (a != d) & (b != c) & (b != d) & (c != d)
    if xc.any():
        err(f"{int(xc.sum())} X-crossings, first at {np.argwhere(xc)[0].tolist()}")
    pairs = set()
    for p1, p2 in ((prov[:, :-1], prov[:, 1:]), (prov[:-1], prov[1:]), (prov[:, -1:], prov[:, :1])):
        m = p1 != p2
        pairs |= set(zip(p1[m].tolist(), p2[m].tolist()))
    nbrs = defaultdict(set)
    for x, y in pairs:
        nbrs[x].add(y)
        nbrs[y].add(x)
    coastal = np.zeros(n, bool)
    for x, y in pairs:
        if {kind[x], kind[y]} == {0, 2}:
            err(f"lake {x + 1} touches sea {y + 1}")
        if {kind[x], kind[y]} == {0, 1}:
            coastal[x] = coastal[y] = True
    bad_coast = int((coastal != np.array(coast_def)).sum())
    if bad_coast:
        err(f"{bad_coast} provinces have a wrong coastal flag")

    # ------------------------------------------------------------ other bitmaps
    pix_kind = kind[prov]
    for name, bpp in (("heightmap", 8), ("terrain", 8), ("rivers", 8), ("cities", 8)):
        bm = read_bmp(mod / f"map/{name}.bmp")
        if (bm["width"], bm["height"]) != (W, H) or bm["bpp"] != bpp or bm["header"] != 40:
            err(f"{name}.bmp must be {W}x{H}, {bpp}-bit, 40-byte header")
        if name == "terrain" and (bm["img"][pix_kind != 1] != 15).any():
            err("terrain.bmp: water must be index 15 (ocean)")
        if name == "terrain" and (bm["img"][pix_kind == 1] == 15).any():
            err("terrain.bmp: land uses the ocean index 15")
        if name == "rivers":
            riv = bm["img"]
            for m in river_problems(np.where(riv <= 11, riv, 255).astype(np.uint8), pix_kind == 1):
                err(f"rivers.bmp: {m}")
        if name == "heightmap":
            hm = bm["img"]
            if (hm[pix_kind == 1] <= 95).any():
                err(f"{int((hm[pix_kind == 1] <= 95).sum())} land pixels at or below sea level")
            if (hm[pix_kind != 1] >= 95).any():
                err(f"{int((hm[pix_kind != 1] >= 95).sum())} water pixels at or above sea level")
    wn = read_bmp(mod / "map/world_normal.bmp")
    if (wn["width"], wn["height"], wn["bpp"]) != (W // 2, H // 2, 24):
        err("world_normal.bmp must be half the map size, 24-bit")
    tr = read_bmp(mod / "map/trees.bmp")
    if tr["bpp"] != 8:
        err("trees.bmp must be 8-bit")
    for name, div in (("colormap_rgb_cityemissivemask_a", 2), ("colormap_water_0", 2),
                      ("colormap_water_1", 4), ("colormap_water_2", 8), ("fow_rgb_waterspec_a", 2)):
        p = mod / f"map/terrain/{name}.dds"
        hdr = p.read_bytes()[:128]
        h, w = struct.unpack_from("<II", hdr, 12)
        if hdr[:4] != b"DDS " or (w, h) != (W // div, H // div):
            err(f"{name}.dds should be {W // div}x{H // div}")
        if p.stat().st_size != 128 + w * h * 4:
            err(f"{name}.dds has the wrong data length")

    # ------------------------------------------------------------ countries
    tags = {}
    for f in (mod / "common/country_tags").glob("*.txt"):
        for tag, path in re.findall(r"^(\w{3})\s*=\s*\"([^\"]+)\"", f.read_text(), re.M):
            tags[tag] = path
            if not (mod / "common" / path).exists():
                err(f"country file common/{path} missing")
    hist = {}
    for f in (mod / "history/countries").glob("*.txt"):
        tag = f.name[:3]
        if tag not in tags:
            err(f"history file {f.name} for unknown tag")
        hist[tag] = int(field(f.read_text(), "capital"))

    # ------------------------------------------------------------ states
    state_provs, owner = {}, {}
    for f in (mod / "history/states").glob("*.txt"):
        body = blocks(strip(f.read_text()), "state")[0]
        sid = int(field(body, "id"))
        state_provs[sid] = id_list(body, "provinces")
        owner[sid] = field(body, "owner")
        if field(body, "state_category") not in VANILLA_STATE_CATEGORIES:
            err(f"state {sid}: unknown state_category")
        if owner[sid] not in tags:
            err(f"state {sid}: owner {owner[sid]} is not a defined tag")
        vp = blocks(body, "victory_points")
        if vp and int(vp[0].split()[0]) not in state_provs[sid]:
            err(f"state {sid}: victory point outside the state")
    if sorted(state_provs) != list(range(1, len(state_provs) + 1)):
        err("state ids are not contiguous from 1")
    state_of = {}
    for sid, ps in state_provs.items():
        for p in ps:
            if p in state_of:
                err(f"province {p} is in states {state_of[p]} and {sid}")
            state_of[p] = sid
            if kind[p - 1] != 1:
                err(f"state {sid} contains non-land province {p}")
    for i in range(n):
        if kind[i] == 1 and i + 1 not in state_of:
            err(f"land province {i + 1} is in no state")
    for tag, cap in hist.items():
        if owner.get(cap) != tag:
            err(f"{tag}'s capital state {cap} is not owned by it")

    # ------------------------------------------------------------ strategic regions
    region_of, region_provs = {}, {}
    for f in (mod / "map/strategicregions").glob("*.txt"):
        body = blocks(strip(f.read_text()), "strategic_region")[0]
        rid = int(field(body, "id"))
        region_provs[rid] = id_list(body, "provinces")
        if len(blocks(body, "period")) != 12:
            note(f"region {rid} does not have 12 weather periods")
        for p in region_provs[rid]:
            if p in region_of:
                err(f"province {p} is in regions {region_of[p]} and {rid}")
            region_of[p] = rid
    if sorted(region_provs) != list(range(1, len(region_provs) + 1)):
        err("strategic region ids are not contiguous from 1")
    for i in range(n):
        if i + 1 not in region_of:
            err(f"province {i + 1} is in no strategic region")
    for sid, ps in state_provs.items():
        if len({region_of.get(p) for p in ps}) != 1:
            err(f"state {sid} spans several strategic regions")
    for rid, ps in region_provs.items():
        ks = {kind[p - 1] for p in ps}
        if 0 in ks and ks != {0}:
            err(f"region {rid} mixes sea with land/lakes")
        if ks == {0}:
            members, seen, stack = set(p - 1 for p in ps), set(), [ps[0] - 1]
            while stack:
                u = stack.pop()
                if u in seen:
                    continue
                seen.add(u)
                stack.extend(v for v in nbrs[u] if v in members and v not in seen)
            if seen != members:
                err(f"sea region {rid} is not contiguous")

    # ------------------------------------------------------------ positions
    def inside(x, z):
        px, py = int(float(x)), H - 1 - int(float(z))
        if not (0 <= px < W and 0 <= py < H):
            return None
        return int(prov[py, px]) + 1

    have = defaultdict(lambda: defaultdict(int))
    prov_have = defaultdict(set)
    for ln in (mod / "map/buildings.txt").read_text().splitlines():
        sid, bt, x, y, z, rot, sea = ln.split(";")
        sid, sea = int(sid), int(sea)
        at = inside(x, z)
        have[sid][bt] += 1
        if bt == "floating_harbor":
            if at is None or kind[at - 1] != 0:
                err(f"floating_harbor for state {sid} is not on the sea")
        else:
            if at is None or state_of.get(at) != sid:
                err(f"{bt} for state {sid} at ({x},{z}) lies outside the state")
                continue
            prov_have[at].add(bt)
        if bt in ("naval_base_spawn", "floating_harbor"):
            if sea < 1 or kind[sea - 1] != 0:
                err(f"{bt} in state {sid} names non-sea province {sea}")
            elif bt == "naval_base_spawn" and sea - 1 not in nbrs[at - 1]:
                err(f"naval_base_spawn in province {at} names non-adjacent sea {sea}")
    for sid, ps in state_provs.items():
        n_coast = sum(coastal[p - 1] for p in ps)
        if have[sid]["floating_harbor"] < n_coast:
            err(f"state {sid} has {have[sid]['floating_harbor']} floating_harbor rows for {n_coast} coastal provinces")
        if n_coast and have[sid]["dockyard"] < 1:
            err(f"coastal state {sid} has no dockyard position")
        for bt, cnt in STATE_BUILDINGS.items():
            if have[sid][bt] < cnt:
                err(f"state {sid} has {have[sid][bt]} {bt} positions, needs {cnt}")
    for i in range(n):
        if kind[i] != 1:
            continue
        need = PROVINCE_BUILDINGS | (COASTAL_BUILDINGS - {"floating_harbor"} if coastal[i] else set())
        if need - prov_have[i + 1]:
            err(f"province {i + 1} lacks positions for {sorted(need - prov_have[i + 1])}")
    stacks = defaultdict(set)
    for ln in (mod / "map/unitstacks.txt").read_text().splitlines():
        p, t, x, y, z, rot, off = ln.split(";")
        if inside(x, z) != int(p):
            err(f"unit stack {t} of province {p} lies outside it")
        stacks[int(p)].add(int(t))
    for i in range(n):
        want = LAND_STACKS if kind[i] == 1 else SEA_STACKS if kind[i] == 0 else set()
        if want - stacks[i + 1]:
            err(f"province {i + 1} lacks unit stacks {sorted(want - stacks[i + 1])}")
    wp = defaultdict(set)
    for ln in (mod / "map/weatherpositions.txt").read_text().splitlines():
        rid, x, y, z, sz = ln.split(";")
        if region_of.get(inside(x, z)) != int(rid):
            err(f"weather position of region {rid} lies outside it")
        wp[int(rid)].add(sz)
    for rid in region_provs:
        if wp[rid] != {"small", "big"}:
            err(f"region {rid} needs a small and a big weather position (has {wp[rid]})")
    for ln in (mod / "map/supply_nodes.txt").read_text().splitlines():
        lvl, p = ln.split()
        if int(p) not in state_of:
            err(f"supply node on province {p}, which is in no state")
    adj = (mod / "map/adjacencies.csv").read_bytes()
    if not adj.rstrip().endswith(b"-1;-1;;-1;-1;-1;-1;-1;-1") or b"\r\n" not in adj:
        err("adjacencies.csv needs CRLF and the -1 end line")
    if not (mod / "map/buildings.txt").read_text().strip():
        err("buildings.txt must not be empty")

    # ------------------------------------------------------------ localisation
    keys = set()
    for f in (mod / "localisation").rglob("*.yml"):
        raw = f.read_bytes()
        if not raw.startswith(b"\xef\xbb\xbf"):
            err(f"{f.name} must be UTF-8 with BOM")
        if not f.name.endswith("_l_english.yml") or b"l_english:" not in raw[:20]:
            err(f"{f.name} must be an l_english file")
        keys |= set(re.findall(r"^ (\S+?):\d? ", raw.decode("utf-8-sig"), re.M))
    for f in (mod / "history/states").glob("*.txt"):
        k = field(f.read_text(), "name")
        if k not in keys:
            err(f"state name {k} has no localisation")
    for f in (mod / "map/strategicregions").glob("*.txt"):
        k = field(f.read_text(), "name")
        if k not in keys:
            err(f"region name {k} has no localisation")
    for tag in tags:
        for k in (tag, f"{tag}_DEF", f"{tag}_ADJ"):
            if k not in keys:
                err(f"missing localisation {k}")
    for c in continents:
        if c not in keys:
            err(f"continent {c} has no localisation")

    # ------------------------------------------------------------ characters, focus trees
    chars = set()
    for f in (mod / "common/characters").glob("*.txt"):
        chars |= set(re.findall(r"^\t(\w+)\s*=\s*\{", strip(f.read_text()), re.M))
    sprites = {}
    for f in (mod / "interface").glob("*.gfx"):
        for name, tex in re.findall(r'name\s*=\s*"(\w+)"\s*texturefile\s*=\s*"([^"]+)"', f.read_text()):
            sprites[name] = tex
            if not (mod / tex).exists():
                err(f"sprite {name} points at missing {tex}")
    for f in (mod / "history/countries").glob("*.txt"):
        for c in re.findall(r"recruit_character\s*=\s*(\w+)", f.read_text()):
            if c not in chars:
                err(f"{f.name} recruits unknown character {c}")
            if c not in keys:
                err(f"character {c} has no localisation")
    vanilla_generic = set(l.strip() for l in open("source/names/vanilla_portrait_sprites.txt")
                          if l.startswith("GFX_"))
    for f in (mod / "common/characters").glob("*.txt"):
        for spr in re.findall(r"large\s*=\s*(GFX_\w+)", f.read_text()):
            if spr not in sprites and spr not in vanilla_generic:
                err(f"portrait sprite {spr} is neither ours (interface/) nor a vanilla generic one")
    # no localisation key may be TAG_<ideology or subtype> unless it is meant as that
    # country's name: the game looks names up that way (a leader's name once showed as
    # every country's name)
    import ideologies
    govs = set(ideologies.IDEOLOGIES) | set(ideologies.ideology_of())
    tags = {f.name[:3] for f in (mod / "history/countries").glob("*.txt")}
    for f in (mod / "common/characters").glob("*.txt"):
        for cid in re.findall(r"^\t(\w+) = \{", f.read_text(), re.M):
            if cid[:3] in tags and cid[4:] in govs:
                err(f"character {cid} would name country {cid[:3]} (TAG_<government> is a country-name key)")
    # every country is led by a character of its ruling ideology (author: no generated
    # leaders, so no subtype is left to chance)
    sub_ideo = {}
    for f in (mod / "common/characters").glob("*.txt"):
        for cid, sub in re.findall(r"^\t(\w+) = \{.*?country_leader = \{\s*ideology = (\w+)", f.read_text(), re.S | re.M):
            sub_ideo[cid] = sub
    import ideologies
    io = {**ideologies.ideology_of(), **{k: i for i, v in ideologies.HIDDEN.items() for k in v}}
    for f in (mod / "history/countries").glob("*.txt"):
        t = f.read_text()
        rp = re.search(r"ruling_party\s*=\s*(\w+)", t).group(1)
        leads = [c for c in re.findall(r"recruit_character\s*=\s*(\w+)", t) if io.get(sub_ideo.get(c)) == rp]
        if not leads:
            err(f"{f.name}: no recruited character leads its ruling party ({rp})")
    for f in (mod / "common/national_focus").glob("*.txt"):
        text = strip(f.read_text())
        ids = re.findall(r"\bfocus\s*=\s*\{\s*id\s*=\s*(\w+)", text)
        for fid in ids:
            if fid not in keys:
                err(f"focus {fid} has no localisation")
        for block in re.findall(r"(?:prerequisite|mutually_exclusive)\s*=\s*\{([^}]*)\}", text):
            for pre in re.findall(r"focus\s*=\s*(\w+)", block):
                if pre not in ids:
                    err(f"{f.name}: {pre} is referenced but is not a focus in the tree")

    # ------------------------------------------------------------ superevents and other scripting
    effects = set()
    for f in (mod / "common/scripted_effects").glob("*.txt"):
        effects |= set(re.findall(r"^(\w+)\s*=\s*\{", strip(f.read_text()), re.M))
    events = set()
    for f in (mod / "events").glob("*.txt"):
        events |= set(re.findall(r"^\s*id\s*=\s*([\w.]+)", strip(f.read_text()), re.M))
    scripted = ""
    for d in ("common/national_focus", "common/scripted_effects", "events"):
        for f in (mod / d).glob("*.txt"):
            scripted += strip(f.read_text()) + "\n"
    for name in set(re.findall(r"\b(valsora_\w+)\s*=\s*yes", scripted)):
        if name not in effects:
            err(f"scripted effect {name} is used but not defined")
    for ev in set(re.findall(r"country_event\s*=\s*\{\s*id\s*=\s*([\w.]+)", scripted)):
        if ev not in events:
            err(f"event {ev} is fired but not defined")
    # songs: defined in a music/**/*.asset next to their file, and (the game ignores them
    # otherwise: "Song doesnt exist") listed in a station .txt with music_station = "..."
    songs, in_station = {}, set()
    for f in (mod / "music").rglob("*.asset"):
        for name, fn in re.findall(r'name\s*=\s*"(\w+)"\s*file\s*=\s*"([^"]+)"', f.read_text()):
            songs[name] = fn
            if not (f.parent / fn).exists():
                err(f"song {name} points at missing {(f.parent / fn).relative_to(mod)}")
    for f in (mod / "music").rglob("*.txt"):
        text = strip(f.read_text())
        if re.search(r"music_station\s*=", text):
            in_station |= set(re.findall(r'song\s*=\s*"(\w+)"', text))
    for song in set(re.findall(r'play_song\s*=\s*"(\w+)"', scripted)):
        if song not in songs:
            err(f"play_song {song} is not defined in music/")
        elif song not in in_station:
            err(f"play_song {song} is not in any music station, so the game won't find it")
    for f in (mod / "common/scripted_localisation").glob("*.txt"):
        for k in re.findall(r"localization_key\s*=\s*(\w+)", f.read_text()):
            if k not in keys:
                err(f"scripted localisation key {k} has no localisation")
    gui = "".join(f.read_text() for f in (mod / "interface").glob("*.gui"))
    gui_names = set(re.findall(r'name\s*=\s*"(\w+)"', gui))
    for f in (mod / "common/scripted_guis").glob("*.txt"):
        text = strip(f.read_text())
        for w in re.findall(r'window_name\s*=\s*"(\w+)"', text):
            if w not in gui_names:
                err(f"scripted GUI window {w} is not in any interface/*.gui")
        for el in re.findall(r"^\s*(\w+)_(?:click|visible)\s*=", text, re.M):
            if el not in gui_names:
                err(f"scripted GUI refers to element {el}, which no .gui defines")
    for spr in set(re.findall(r'(?:spriteType|quadTextureSprite)\s*=\s*"(GFX_valsora_\w+)"', gui)):
        if spr not in sprites:
            err(f"GUI sprite {spr} is not defined in interface/")
    own_gui = "".join(f.read_text() for f in (mod / "interface").glob("valsora_*.gui"))
    for k in re.findall(r'buttonText\s*=\s*"(\w+)"', own_gui):  # vanilla overrides use vanilla keys
        if k not in keys:
            err(f"button text {k} has no localisation")
    # the party list: vanilla's box holds 4 x 16 px rows
    pv = mod / "interface/countrypoliticsview.gui"
    row = re.search(r'"parties_grid".*?slotsize\s*=\s*\{[^}]*height\s*=\s*(\d+)', pv.read_text(), re.S) \
        if pv.exists() else None
    n_ideo = len(re.findall(r"^\t(\w+) = \{", (mod / "common/ideologies/00_ideologies.txt").read_text(), re.M))
    if n_ideo * (int(row.group(1)) if row else 16) > 4 * 16 + 2:
        err(f"{n_ideo} ideologies do not fit the politics view's party list")

    # ------------------------------------------------------------ portraits, names, factions
    vanilla_sprites = set(l.strip() for l in open("source/names/vanilla_portrait_sprites.txt")
                          if l.strip() and not l.startswith("#"))
    for f in (mod / "portraits").glob("*.txt"):
        text = strip(f.read_text())
        for spr in set(re.findall(r'"(GFX_\w+)"', text)):
            if spr not in vanilla_sprites and spr not in sprites:
                err(f"{f.name}: portrait sprite {spr} exists neither in vanilla nor in the mod")
        for c in re.findall(r"continent\s*=\s*\{\s*name\s*=\s*(\w+)", text):
            if c not in continents:
                err(f"{f.name}: continent {c} is not in map/continent.txt")
    named = set()
    for f in (mod / "common/names").glob("*.txt"):
        named |= set(re.findall(r"^(\w{3}) = \{", f.read_text(encoding="utf-8"), re.M))
    for tag in tags:
        if tag not in named:
            err(f"country {tag} has no name list in common/names")
    templates = {}
    for f in (mod / "common/factions/templates").glob("*.txt"):
        for tname, body in re.findall(r"^(\w+)\s*=\s*\{(.*?)^\}", strip(f.read_text()), re.S | re.M):
            templates[tname] = body
            k = field(body, "name")
            if k and k not in keys:
                err(f"faction template {tname}: name {k} has no localisation")
    for f in (mod / "history/countries").glob("*.txt"):
        text = f.read_text()
        for t in re.findall(r"create_faction_from_template\s*=\s*(\w+)", text):
            if t not in templates:
                err(f"{f.name} creates a faction from unknown template {t}")
        for t in re.findall(r"add_to_faction\s*=\s*(\w+)", text):
            if t not in tags:
                err(f"{f.name} adds unknown country {t} to its faction")
    for t in set(re.findall(r"target\s*=\s*([A-Z]{3})\b", scripted)):
        if t not in tags:
            err(f"a war goal or effect targets {t}, which is not a country in the mod")

    # ------------------------------------------------------------ ideologies
    ideo_text = strip((mod / "common/ideologies/00_ideologies.txt").read_text())
    body = ideo_text[ideo_text.index("{") + 1:]
    ideos, subs, depth, cur = set(), set(), 0, None
    for tok in re.findall(r"\w+\s*=\s*\{|\{|\}", body):
        if tok == "}":
            depth -= 1
            continue
        name = tok.split("=")[0].strip() if "=" in tok else None
        if depth == 0 and name:
            ideos.add(name)
            cur = name
        elif depth == 2 and name and cur and name not in ("color",):
            subs.add(name)
        depth += 1
    everything = scripted + "".join(f.read_text() for f in (mod / "history/countries").glob("*.txt"))
    everything += "".join(f.read_text() for f in (mod / "common/on_actions").glob("*.txt"))
    for block in re.findall(r"set_popularities\s*=\s*\{([^}]*)\}", everything):
        vals = dict((k, int(v)) for k, v in re.findall(r"(\w+)\s*=\s*(\d+)", block))
        if set(vals) - ideos:
            err(f"set_popularities names unknown ideologies {sorted(set(vals) - ideos)}")
        if sum(vals.values()) != 100:
            err(f"set_popularities sums to {sum(vals.values())}, not 100: {vals}")
    for kw in ("ruling_party", "has_government"):
        for v in set(re.findall(rf"{kw}\s*=\s*(\w+)", everything)):
            if v not in ideos:
                err(f"{kw} = {v} is not an ideology")
    for f in (mod / "common/characters").glob("*.txt"):
        for v in re.findall(r"\bideology\s*=\s*(\w+)", f.read_text()):
            if v not in subs:
                err(f"{f.name}: sub-ideology {v} is not in 00_ideologies.txt")
    for v in set(re.findall(r"set_country_leader_ideology\s*=\s*(\w+)", everything)):
        if v not in subs:
            err(f"set_country_leader_ideology = {v} is not a sub-ideology")
    # every sub-ideology of ours has a name (vanilla's hidden ones keep vanilla's)
    import ideologies
    for v in (k for lst in ideologies.SUBTYPES.values() for k, _, _ in lst):
        if v not in keys:
            err(f"sub-ideology {v} has no localisation")
    # ------------------------------------------------------------ descriptors
    desc = (mod / "descriptor.mod").read_text()
    rps = re.findall(r'replace_path="([^"]+)"', desc)
    outer = mod.parent / f"{mod.name}.mod"
    if outer.exists() and re.findall(r'replace_path="([^"]+)"', outer.read_text()) != rps:
        err("descriptor.mod and the launcher .mod have different replace_path lines")
    for rp in rps:
        if not any((mod / rp).glob("*.*")):
            err(f"replaced folder {rp} has no file in the mod")

    lands = int((kind == 1).sum())
    print(f"{W}x{H}, {n} provinces ({lands} land, {(kind == 0).sum()} sea, {(kind == 2).sum()} lake), "
          f"{len(state_provs)} states, {len(region_provs)} strategic regions, {len(tags)} countries")
    for m in notes[:20]:
        print("note:", m)
    for m in errors[:50]:
        print("ERROR:", m)
    if errors:
        print(f"{len(errors)} errors")
        sys.exit(1)
    print("all checks passed")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "build/valsora_test")
