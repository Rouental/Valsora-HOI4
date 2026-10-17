"""The Valsora Atlas: the last build's world as data for a page that shows it in a browser
(scripts/atlas.html; docs/ATLAS.md). Not part of the mod: it only reads the build.

    python3 scripts/atlas_export.py                 # after a build: work/atlas/ (the last export moves to work/atlas_prev/)
    python3 scripts/atlas_export.py --changes-only  # compare work/atlas/ with work/atlas_prev/ again

It reads work/ (provinces.npz, regions.npz, regions.json, world.npz, game_releasables.json, terrain_test/ when
there) and build/valsora_test/ (the state and country histories, localisation, colours, flags, characters,
portraits, strategic regions, adjacencies), through the readers of country_list.py, facts_export.py and
nation_sheet.py. It writes, into work/atlas/:
    prov.png          the province of every map pixel, its id + 1 as 24-bit RGB (0: none)
    rivers.png        the rivers (rivers.bmp's code + 1, 0: none), greyscale
    shade.png         the build's heightmap as a hillshade, half size, greyscale (128 flat)
    flags.png         every country's flag at 82 x 52, a sheet of FLAG_COLS columns
    portraits.jpg     the rulers' portraits of our own (78 x 105), a sheet; the base game's are Paradox's, left out
    terrain_test.png  the terrain test (scripts/terrain_test.py, not in the mod), class + 1 per pixel, and
    terrain_shade.png its relief as a hillshade, half size (only when work/terrain_test/ exists)
    provinces.json    per province, by column: kind, state, region, size, anchor, terrain, coast, colour
    atlas.json        the countries, states, regions, cities and victory points, the Subregions layer's parts,
                      legends, and a list of the files
    changes.json      what changed since the previous export (work/atlas_prev/): provinces whose owner, state or
                      region changed or that were redrawn, states and countries added and removed, states renamed
Ids in the files are the build's indices from 0: the game's province, state and region numbers are one more.
"""
import argparse
import datetime
import json
import math
import os
import re
import shutil
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
os.chdir(ROOT)  # the readers below name build/, source/ and work/ from the repository's root

import nations  # noqa: E402
from collages import continent_of  # noqa: E402
from common import COUNTRIES, MAP_H as H, MAP_W as W  # noqa: E402
from country_list import rows  # noqa: E402
from facts_export import read_loc, read_states  # noqa: E402
from imgio import read_dds  # noqa: E402
from nation_sheet import leaders, map_colours, own_portraits  # noqa: E402

MOD = Path("build/valsora_test")
OUT = Path("work/atlas")
PREV = Path("work/atlas_prev")
FORMAT = 1  # the files' layout: a previous export of another format is not compared
FLAG = (82, 52)
FLAG_COLS = 16
PORTRAIT = (78, 105)
TERRAIN_COLOUR = {"plains": (176, 186, 120), "forest": (76, 124, 66), "hills": (160, 132, 96),
                  "mountain": (122, 108, 100), "desert": (226, 206, 150), "marsh": (98, 150, 138),
                  "jungle": (34, 98, 54), "urban": (186, 70, 60), "ocean": (30, 52, 66), "lakes": (52, 88, 110)}
# the terrain test's classes (terrain_test.CLASSES: key -> terrain.bmp index, label, colour), copied if it can't load
TEST_CLASSES = {
    "plains": (0, "Plains / farmland", (178, 196, 112)), "steppe": (5, "Steppe / savanna (plains)", (218, 204, 134)),
    "forest": (1, "Forest", (78, 136, 64)), "taiga": (4, "Taiga, conifers (forest)", (46, 98, 70)),
    "jungle": (21, "Jungle", (22, 92, 44)), "desert": (3, "Desert, sand", (240, 222, 166)),
    "rocky": (8, "Desert, rocky", (204, 170, 126)), "hills": (2, "Hills", (166, 134, 94)),
    "mountain": (6, "Mountains", (120, 104, 96)), "snow": (16, "Mountains, snow", (236, 236, 242)),
    "marsh": (9, "Marsh", (98, 156, 144)), "urban": (13, "Urban", (200, 40, 40))}
IDEOLOGY_KEY = {"Democratic": "democratic", "Communist": "communism", "Authoritarian": "fascism",
                "Monarchist": "neutrality", "Theocratic": "theocracy"}
# the ideologies' colours in the mod (ideologies.py; democratic and communist are vanilla's)
IDEOLOGY_COLOUR = {"democratic": (60, 120, 220), "communism": (200, 30, 30), "fascism": (20, 20, 20),
                   "neutrality": (128, 48, 168), "theocracy": (238, 238, 238)}


def hexcol(rgb):
    return "%02x%02x%02x" % tuple(int(v) for v in rgb)


def save_png(img, path):
    Image.fromarray(img).save(path, "PNG", compress_level=9)


def hillshade(h, z, amp):
    """a height field as light from the north-west, 0..255 with 128 flat: a soft curve scaled to the field's own
    slopes, so most of the land stays within amp of flat"""
    gy, gx = np.gradient(ndi.gaussian_filter(h.astype(np.float32), 1.0))
    nx, ny = -gx * z, -gy * z
    n = np.sqrt(nx ** 2 + ny ** 2 + 1)
    light = np.array([-0.6, -0.6, 0.55])
    light /= np.linalg.norm(light)
    d = (nx * light[0] + ny * light[1] + light[2]) / n - light[2]
    q = np.percentile(np.abs(d[d != 0]), 90) if (d != 0).any() else 1.0
    return np.clip(128 + amp * np.tanh(d / max(q, 1e-6)), 0, 255).astype(np.uint8)


def english():
    """every English localisation key of the build -> its text"""
    out = {}
    for f in sorted((MOD / "localisation/english").rglob("*.yml")):
        for k, v in re.findall(r'^\s*([\w.\-]+):\d*\s+"(.*)"\s*$', f.read_text(encoding="utf-8-sig"), re.M):
            out.setdefault(k, v)
    return out


def built_at():
    """when the last build ran: build_mod.py writes the descriptor every time (read_layers.py, and so
    work/provinces.npz, is skipped while the map is unchanged)"""
    t = max(Path(f).stat().st_mtime for f in (MOD / "descriptor.mod", "work/provinces.npz", "work/regions.json"))
    return datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M")


def histories():
    """tag -> capital state index, overlord (tag, autonomy), faction (name, leads), from the country histories"""
    L = english()
    tmpl = {}
    for f in (MOD / "common/factions/templates").glob("*.txt"):
        tmpl.update(re.findall(r"^(\w+) = \{\s*name = (\w+)", f.read_text(encoding="utf-8-sig"), re.M))
    capital, overlord, faction = {}, {}, {}
    for f in (MOD / "history/countries").glob("*.txt"):
        tag, t = f.name[:3], f.read_text(encoding="utf-8-sig")
        m = re.search(r"^capital = (\d+)", t, re.M)
        if m:
            capital[tag] = int(m.group(1)) - 1
        for target, kind in re.findall(r"set_autonomy = \{ target = (\w+) autonomous_state = autonomy_(\w+)", t):
            overlord[target] = (tag, kind)
        for tp in re.findall(r"create_faction_from_template = (\w+)", t):
            name = L.get(tmpl.get(tp, tp), tp)
            faction[tag] = (name, True)
            for member in re.findall(r"add_to_faction = (\w+)", t):
                faction[member] = (name, False)
    return capital, overlord, faction


def built_states():
    """state index -> owner, cores, from the built state histories (with read_states' manpower, buildings, VPs)"""
    out = {}
    for f in (MOD / "history/states").glob("*.txt"):
        t = f.read_text(encoding="utf-8-sig")
        sid = int(re.search(r"\bid = (\d+)", t).group(1)) - 1
        out[sid] = dict(owner=re.search(r"owner = (\w+)", t).group(1), cores=re.findall(r"add_core_of = (\w+)", t))
    return out


def straits():
    """(province, province) pairs a strait crossing joins (map/adjacencies.csv), indices from 0"""
    out = []
    for line in (MOD / "map/adjacencies.csv").read_text(encoding="utf-8").splitlines()[1:]:
        f = line.split(";")
        if len(f) > 3 and f[2] == "sea" and int(f[0]) >= 0:
            out.append((int(f[0]) - 1, int(f[1]) - 1))
    return out


def run_along(blob, y, x, ang):
    """the length of blob's run through (y, x) along the angle (radians), in pixels"""
    dx, dy = math.cos(ang), math.sin(ang)
    hgt, wid = blob.shape
    total = 0
    for sgn in (1, -1):
        gap, k = 0, 1
        while gap < 6:
            px, py = int(round(x + sgn * k * dx)), int(round(y + sgn * k * dy))
            if not (0 <= px < wid and 0 <= py < hgt):
                break
            if blob[py, px]:
                total += 1 + gap
                gap = 0
            else:
                gap += 1
            k += 1
    return total + 1


def labels_of(owner_px, n):
    """for each owner 0..n-1, its labels: [x, y, angle (degrees), length, thickness, area, x0, y0, x1, y1 (the
    piece's box)] for its largest piece and any others at least a fifth of its size (up to four), where the label
    fits best"""
    out = [[] for _ in range(n)]
    for t, sl in enumerate(ndi.find_objects(owner_px + 1)):
        if sl is None or t >= n:
            continue
        lab, k = ndi.label(owner_px[sl] == t)
        sizes = np.bincount(lab.ravel())[1:]
        order = np.argsort(-sizes)
        for rank, b in enumerate(order[:4]):
            if rank and sizes[b] < max(sizes[order[0]] * 0.2, 400):
                break
            bsl = ndi.find_objects((lab == b + 1).astype(np.uint8))[0]
            blob = lab[bsl] == b + 1
            step = 2 if blob.size > 600_000 else 1
            sb = blob[::step, ::step]
            d = ndi.distance_transform_edt(np.pad(sb, 1))[1:-1, 1:-1]
            ys, xs = np.nonzero(sb)
            ang = 0.0
            if len(xs) > 10:
                c = np.cov(np.vstack([xs, ys]).astype(np.float64))
                ev, evec = np.linalg.eigh(c)
                vx, vy = evec[:, -1]
                if vx < 0:
                    vx, vy = -vx, -vy
                ang = math.atan2(vy, vx)
                if ev[-1] < 1.6 * max(ev[0], 1e-9):  # round: level text
                    ang = 0.0
                ang = max(-0.6, min(0.6, ang))
            # the best point: deep inside and on a long run along the angle
            cand = np.argsort(-d.ravel())[:40]
            best = None
            for ci in cand:
                py, px = divmod(int(ci), d.shape[1])
                ln = run_along(sb, py, px, ang)
                score = ln * min(d[py, px], ln / 4)
                if best is None or score > best[0]:
                    best = (score, px, py, ln, d[py, px])
            _, px, py, ln, th = best
            x0, y0 = bsl[1].start + sl[1].start, bsl[0].start + sl[0].start
            out[t].append([int(px * step + x0), int(py * step + y0), round(math.degrees(ang), 1), int(ln * step),
                           int(2 * th * step), int(sizes[b]), int(x0), int(y0), int(bsl[1].stop + sl[1].start),
                           int(bsl[0].stop + sl[0].start)])
    return out


def flag_sheet(tags):
    rows_ = (len(tags) + FLAG_COLS - 1) // FLAG_COLS
    sheet = Image.new("RGB", (FLAG_COLS * FLAG[0], max(1, rows_) * FLAG[1]), (20, 26, 30))
    index = {}
    for k, tag in enumerate(tags):
        f = MOD / "gfx/flags" / f"{tag}.tga"
        if not f.exists():
            continue
        im = Image.open(f).convert("RGB")
        if im.size != FLAG:
            im = im.resize(FLAG, Image.LANCZOS)
        sheet.paste(im, ((k % FLAG_COLS) * FLAG[0], (k // FLAG_COLS) * FLAG[1]))
        index[tag] = k
    return sheet, index


def portrait_sheet(sprites):
    """sprite name -> index in a sheet of our own portraits"""
    files = own_portraits()
    have = [s for s in sorted(set(sprites)) if s in files and files[s].exists()]
    cols = 10
    sheet = Image.new("RGB", (cols * PORTRAIT[0], max(1, (len(have) + cols - 1) // cols) * PORTRAIT[1]), (20, 26, 30))
    index = {}
    for k, s in enumerate(have):
        im = Image.fromarray(read_dds(files[s])).convert("RGB").resize(PORTRAIT, Image.LANCZOS)
        sheet.paste(im, ((k % cols) * PORTRAIT[0], (k // cols) * PORTRAIT[1]))
        index[s] = k
    return sheet, index, cols


def export(dst):
    t0 = time.time()
    p = np.load("work/provinces.npz")
    prov, kind, pcol = p["prov"], p["kind"], p["colors"]
    terrain = [str(v) for v in p["terrain"]]
    reg = np.load("work/regions.npz")
    anchor, centre, size = reg["anchor"], reg["centre"], reg["size"]
    state_of, region_of = reg["state_of"], reg["region_of"]
    rj = json.load(open("work/regions.json", encoding="utf-8"))
    states, owners, regions = rj["states"], rj["owners"], rj["regions"]
    world = np.load("work/world.npz")
    n, ns, nr = len(kind), len(states), len(regions)
    L = english()
    built = read_states()
    hist_states = built_states()
    vp_names = read_loc(MOD / "localisation/english/replace/valsora_victory_points_l_english.yml", "VICTORY_POINTS_")
    table = {r["tag"]: r for r in rows()}
    colour = map_colours()
    capital, overlord, faction = histories()
    where = continent_of()
    ruler_of, sprite_of = leaders()
    game_rel = json.loads(Path("work/game_releasables.json").read_text(encoding="utf-8")) \
        if Path("work/game_releasables.json").exists() else {}
    by_tag = {v[0]: v for v in COUNTRIES.values()}
    print(f"read the build ({time.time() - t0:.1f} s)")

    # countries: every country of the mod (country_list.rows: ours, not Earth's stand-ins)
    tags = sorted(table)
    ti = {t: i for i, t in enumerate(tags)}
    state_owner = [hist_states[s]["owner"] if s in hist_states else owners[s] for s in range(ns)]
    prov_owner = np.full(n + 1, -1, np.int32)  # index n: no province
    for s, g in enumerate(states):
        prov_owner[g] = ti.get(state_owner[s], -1)
    owner_px = np.where(prov >= 0, prov_owner[prov], -1).astype(np.int32)
    owner_px[kind[np.maximum(prov, 0)] != 1] = -1

    # --- the pictures
    v = (prov + 1).astype(np.uint32)
    save_png(np.dstack([(v >> 16) & 255, (v >> 8) & 255, v & 255]).astype(np.uint8), dst / "prov.png")
    rv = world["rivers"]
    save_png(np.where(rv < 254, rv.astype(np.int16) + 1, 0).astype(np.uint8), dst / "rivers.png")
    save_png(hillshade(world["height"][::2, ::2], 1.2, 26), dst / "shade.png")
    test = Path("work/terrain_test")
    has_test = (test / "terrain_class.npy").exists()
    test_classes = TEST_CLASSES
    if has_test:
        try:
            from terrain_test import CLASSES as test_classes  # noqa: F811
        except Exception:  # its imports are heavy; the copy above serves
            pass
        cls = np.load(test / "terrain_class.npy")
        land = kind[np.maximum(prov, 0)] == 1
        save_png(np.where(land & (cls != 255), cls.astype(np.int16) + 1, 0).astype(np.uint8), dst / "terrain_test.png")
        relief = np.load(test / "relief.npy", mmap_mode="r")[::2, ::2]
        save_png(hillshade(np.asarray(relief), 0.35, 46), dst / "terrain_shade.png")
    sheet, flag_index = flag_sheet(tags)
    sheet.save(dst / "flags.png", "PNG", optimize=True)
    rulers = {t: ruler_of.get(t) for t in tags}
    psheet, pindex, pcols = portrait_sheet([sprite_of.get(c) for c in rulers.values() if c])
    psheet.save(dst / "portraits.jpg", "JPEG", quality=86, optimize=True)
    print(f"pictures ({time.time() - t0:.1f} s)")

    # --- provinces
    coast = np.zeros(n, np.uint8)
    nb_owner = defaultdict(Counter)  # country -> neighbour -> shared border length
    for a, b, ln in rj["adjacency"]:
        if kind[a] == 1 and kind[b] == 0:
            coast[a] = 1
        elif kind[b] == 1 and kind[a] == 0:
            coast[b] = 1
        if kind[a] == 1 and kind[b] == 1:
            oa, ob = prov_owner[a], prov_owner[b]
            if oa != ob and oa >= 0 and ob >= 0:
                nb_owner[tags[oa]][tags[ob]] += ln
                nb_owner[tags[ob]][tags[oa]] += ln
    by_sea = defaultdict(set)
    for a, b in straits():
        oa, ob = prov_owner[a], prov_owner[b]
        if oa != ob and oa >= 0 and ob >= 0:
            by_sea[tags[oa]].add(tags[ob])
            by_sea[tags[ob]].add(tags[oa])
    tnames = sorted(set(terrain))
    provinces = dict(
        kind=kind.tolist(), state=state_of.tolist(), region=region_of.tolist(), size=size.tolist(),
        x=anchor[:, 1].tolist(), y=anchor[:, 0].tolist(),
        terrain=[tnames.index(t) for t in terrain], terrains=tnames, coast=coast.tolist(),
        colour=[(int(c[0]) << 16) | (int(c[1]) << 8) | int(c[2]) for c in pcol])
    (dst / "provinces.json").write_text(json.dumps(provinces, separators=(",", ":")), encoding="utf-8")

    # --- states
    boxes = ndi.find_objects(prov + 1)
    city_at = {int(c[0]): c for c in rj.get("cities", [])}
    state_rows, cities = [], []
    for s, g in enumerate(states):
        b = built.get(s + 1, {})
        w_ = np.array([size[i] for i in g], float)
        cy = float(np.average([centre[i][0] for i in g], weights=w_))
        cx = float(np.average([centre[i][1] for i in g], weights=w_))
        lp = min(g, key=lambda i: (anchor[i][0] - cy) ** 2 + (anchor[i][1] - cx) ** 2)
        bx = [min(boxes[i][1].start for i in g), min(boxes[i][0].start for i in g),
              max(boxes[i][1].stop for i in g), max(boxes[i][0].stop for i in g)]
        owner = state_owner[s]
        cap = capital.get(owner) == s
        vps = []
        for pp, val in b.get("vp", []):
            i = pp - 1
            nm = vp_names.get(pp, "")
            c = city_at.get(i)
            generic = nm in ("", f"{L.get(f'VAL_STATE_{s + 1}', '')} City")
            x, y = (int(c[2]), int(c[3])) if c else (int(anchor[i][1]), int(anchor[i][0]))
            cities.append(dict(p=i, s=s, v=val, n=c[1] if c else nm, x=x, y=y, dot=bool(c), named=bool(c) or not generic,
                               cap=bool(cap and val >= 10)))
            vps.append([i, val, c[1] if c else nm])
        state_rows.append(dict(
            name=L.get(f"VAL_STATE_{s + 1}", f"State {s + 1}"), owner=owner,
            cores=hist_states.get(s, {}).get("cores", []), provs=g, area=int(sum(int(size[i]) for i in g)),
            pop=b.get("pop", 0), cat=b.get("cat", ""), b=b.get("b", {}), res=b.get("res", {}), naval=b.get("naval", 0),
            vp=vps, region=int(region_of[g[0]]), label=[int(anchor[lp][1]), int(anchor[lp][0])], box=bx,
            capital=cap, coast=int(coast[g].any())))
    print(f"states ({time.time() - t0:.1f} s)")

    # --- strategic regions
    region_rows = []
    for r, rg in enumerate(regions):
        g = rg["provinces"]
        w_ = np.array([size[i] for i in g], float)
        cy = float(np.average([centre[i][0] for i in g], weights=w_))
        cx = float(np.average([centre[i][1] for i in g], weights=w_))
        lp = min(g, key=lambda i: (anchor[i][0] - cy) ** 2 + (anchor[i][1] - cx) ** 2)
        region_rows.append(dict(name=L.get(f"VAL_REGION_{r + 1}", f"Region {r + 1}"), kind=rg["kind"], colour=rg["colour"],
                                states=rg.get("states", []), provs=len(g), area=int(w_.sum()),
                                label=[int(anchor[lp][1]), int(anchor[lp][0])]))

    # --- the Subregions layer's parts, given to their nations as build_mod.py does (a patch to its own seed's
    # nation, else the nearest seed of its colour)
    patches = rj.get("subregions", [])
    seeds_of = defaultdict(list)
    for tag, (x, y) in nations.SUBREGIONS.items():
        pi = int(prov[y, x])
        home = next((k for k, pt in enumerate(patches) if pi in pt[1]), None)
        if home is not None:
            seeds_of[patches[home][0]].append((tag, home, x, y))
    subregions = []
    for k, (c, provs, cx, cy) in enumerate(patches):
        cands = seeds_of.get(c, [])
        own = [t for t, h, _, _ in cands if h == k]
        tag = own[0] if own else (min(cands, key=lambda sd: (sd[2] - cx) ** 2 + (sd[3] - cy) ** 2)[0] if cands else "")
        subregions.append(dict(colour="%06x" % c, provs=provs, x=cx, y=cy, tag=tag))

    # --- countries
    labels = labels_of(owner_px, len(tags))
    mine = defaultdict(list)
    for s in range(ns):
        mine[state_owner[s]].append(s)
    cores_on = defaultdict(list)  # tag -> states it has a core on
    for s in range(ns):
        for c in state_rows[s]["cores"]:
            cores_on[c].append(s)
    subjects = defaultdict(list)
    for t, (o, kd) in overlord.items():
        subjects[o].append([t, kd])
    country_rows = []
    for tag in tags:
        r = table[tag]
        st = mine.get(tag, [])
        ruler = rulers.get(tag)
        spr = sprite_of.get(ruler)
        ideo = IDEOLOGY_KEY.get(r["ideology"], r["ideology"])
        rel_here = sorted({c for s in st for c in state_rows[s]["cores"] if c != tag})
        claims = [s for s in cores_on.get(tag, []) if state_owner[s] != tag]
        lands = [lb for lb in labels[ti[tag]]]
        bx = max(lands, key=lambda lb: lb[5])[6:10] if lands else None  # its largest piece, to fly to
        gr = game_rel.get(tag)
        cap = capital.get(tag, -1)
        country_rows.append(dict(
            tag=tag, name=r["name"], full=r["full"], adj=L.get(f"{tag}_ADJ", ""),
            colour=hexcol(colour.get(tag, by_tag.get(tag, (0, 0, 0, (128, 128, 128)))[3])),
            ideology=ideo, sub=r["subideology"], culture=r["culture"], ruler=r["leader"],
            portrait=pindex.get(spr, -1), flag=flag_index.get(tag, -1), continent=where.get(tag, "").capitalize(),
            capital=cap if cap in st else -1, states=st, provs=int(sum(len(states[s]) for s in st)),
            area=int(sum(state_rows[s]["area"] for s in st)), pop=int(sum(state_rows[s]["pop"] for s in st)),
            neighbours=[t for t, _ in nb_owner[tag].most_common()], bySea=sorted(by_sea[tag] - set(nb_owner[tag])),
            releasables=rel_here, claims=claims, overlord=list(overlord[tag]) if tag in overlord else None,
            subjects=sorted(subjects.get(tag, [])), faction=list(faction[tag]) if tag in faction else None,
            parent=gr["parent"] if gr else None, kind=gr["kind"] if gr else None,
            warOnly=bool(gr and gr.get("war_only")), labels=lands, box=bx, note=r["note"]))
    print(f"countries ({time.time() - t0:.1f} s)")

    files = sorted(f.name for f in dst.iterdir()) + ["atlas.json", "changes.json"]
    atlas = dict(
        format=FORMAT, built=built_at(), exported=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        w=W, h=H, counts=dict(provinces=n, land=int((kind == 1).sum()), sea=int((kind == 0).sum()),
                              lakes=int((kind == 2).sum()), states=ns, regions=nr, countries=len(tags),
                              onMap=sum(1 for t in tags if mine.get(t)), cities=len(rj.get("cities", [])),
                              straits=len(straits())),
        countries=country_rows, states=state_rows, regions=region_rows, cities=cities, subregions=subregions,
        terrain=dict(colours={k: hexcol(v) for k, v in TERRAIN_COLOUR.items()}),
        test=dict(classes=[[k, v[1], hexcol(v[2])] for k, v in test_classes.items()]) if has_test else None,
        ideologies={k: hexcol(v) for k, v in IDEOLOGY_COLOUR.items()},
        flag=dict(w=FLAG[0], h=FLAG[1], cols=FLAG_COLS), portrait=dict(w=PORTRAIT[0], h=PORTRAIT[1], cols=pcols),
        files=sorted(set(files)))
    (dst / "atlas.json").write_text(json.dumps(atlas, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"tables ({time.time() - t0:.1f} s)")


# ------------------------------------------------------------------------------------------------- changes


def snapshot(d):
    a = json.loads((d / "atlas.json").read_text(encoding="utf-8"))
    pv = json.loads((d / "provinces.json").read_text(encoding="utf-8"))
    img = np.asarray(Image.open(d / "prov.png").convert("RGB")).astype(np.int32)
    P = ((img[..., 0] << 16) | (img[..., 1] << 8) | img[..., 2]) - 1
    state = np.array(pv["state"] + [-1], np.int32)
    region = np.array(pv["region"] + [-1], np.int32)
    kind = np.array(pv["kind"] + [255], np.int32)
    return dict(a=a, P=P, state=state, region=region, kind=kind, n=len(pv["kind"]))


def overlaps(x, y, nx, ny):
    """pixels shared by each (x label, y label) pair, labels -1 left out: (xs, ys, counts)"""
    m = (x >= 0) & (y >= 0)
    u, c = np.unique(x[m].astype(np.int64) * ny + y[m], return_counts=True)
    return u // ny, u % ny, c


def best_match(x, y, nx, ny, thr):
    """for each x label the y label it overlaps most by intersection over union, -1 under thr; and the iou"""
    xs, ys, c = overlaps(x, y, nx, ny)
    sx = np.bincount(x[x >= 0], minlength=nx)
    sy = np.bincount(y[y >= 0], minlength=ny)
    iou = c / (sx[xs] + sy[ys] - c)
    best = np.full(nx, -1, np.int64)
    score = np.zeros(nx)
    order = np.argsort(iou)  # the last write wins: the highest
    best[xs[order]] = ys[order]
    score[xs[order]] = iou[order]
    best[score < thr] = -1
    return best, score


def assign(x, y, nx, ny, xnames, ynames, thr=0.5):
    """states or regions matched one to one, by intersection over union, a shared name counting half as much again
    (so a state cut in two keeps its name's half): for each x label its y label (-1: none) and their iou"""
    xs, ys, c = overlaps(x, y, nx, ny)
    sx = np.bincount(x[x >= 0], minlength=nx)
    sy = np.bincount(y[y >= 0], minlength=ny)
    iou = c / (sx[xs] + sy[ys] - c)
    same = np.array([xnames[a] == ynames[b] for a, b in zip(xs, ys)], bool)
    score = iou + 0.5 * same
    best, got, taken = np.full(nx, -1, np.int64), np.zeros(nx), np.zeros(ny, bool)
    for k in np.argsort(-score, kind="stable"):
        if score[k] < thr:
            break
        a, b = xs[k], ys[k]
        if best[a] < 0 and not taken[b]:
            best[a], got[a], taken[b] = b, iou[k], True
    return best, got


def majority(x, y, nx, ny):
    """for each x label the y label most of its pixels have (-1 for none of them)"""
    m = x >= 0
    yy = np.where(y >= 0, y + 1, 0)
    u, c = np.unique(x[m].astype(np.int64) * (ny + 1) + yy[m], return_counts=True)
    xs, ys = u // (ny + 1), u % (ny + 1) - 1
    out = np.full(nx, -1, np.int64)
    order = np.argsort(c)
    out[xs[order]] = ys[order]
    return out


def changes(new_dir, old_dir):
    if not (old_dir / "atlas.json").exists():
        return dict(prev=None, note="No previous export to compare with: the next run will show what changed.")
    N, O = snapshot(new_dir), snapshot(old_dir)
    if O["a"].get("format") != N["a"].get("format") or O["P"].shape != N["P"].shape:
        return dict(prev=O["a"].get("built"), note="The previous export has another layout: nothing compared.")
    PN, PO = N["P"], O["P"]
    nn, no = N["n"], O["n"]
    # per pixel: the state, region and owner (as a tag) of each export
    SN, SO = N["state"][np.where(PN >= 0, PN, nn)], O["state"][np.where(PO >= 0, PO, no)]
    RN, RO = N["region"][np.where(PN >= 0, PN, nn)], O["region"][np.where(PO >= 0, PO, no)]
    KO = O["kind"][np.where(PO >= 0, PO, no)]
    alltags = sorted({s["owner"] for s in N["a"]["states"]} | {s["owner"] for s in O["a"]["states"]})
    tix = {t: i for i, t in enumerate(alltags)}
    own_n = np.array([tix[s["owner"]] for s in N["a"]["states"]] + [-1], np.int32)
    own_o = np.array([tix[s["owner"]] for s in O["a"]["states"]] + [-1], np.int32)
    OO = own_o[np.where(SO >= 0, SO, len(own_o) - 1)]
    ns_n, ns_o = len(N["a"]["states"]), len(O["a"]["states"])
    nr_n, nr_o = len(N["a"]["regions"]), len(O["a"]["regions"])
    # provinces: redrawn when no previous one covers 90 % of it by intersection over union, or its kind changed
    pm, piou = best_match(PN, PO, nn, no, 0.0)
    kmaj = majority(PN, KO, nn, 256)
    nk = N["kind"][:nn]
    redrawn = (piou < 0.9) | (kmaj != nk)
    smatch, siou = assign(SN, SO, ns_n, ns_o, [st["name"] for st in N["a"]["states"]], [st["name"] for st in O["a"]["states"]])
    rmatch, _ = assign(RN, RO, nr_n, nr_o, [r["name"] for r in N["a"]["regions"]], [r["name"] for r in O["a"]["regions"]])
    o_maj = majority(PN, OO, nn, len(alltags))
    s_maj = majority(PN, SO, nn, ns_o)
    r_maj = majority(PN, RO, nn, nr_o)
    pstate, pregion = N["state"][:nn], N["region"][:nn]
    p_owner = np.where(pstate >= 0, own_n[np.maximum(pstate, 0)], -1)
    owner_ch = (nk == 1) & (p_owner != o_maj)
    state_ch = (nk == 1) & (pstate >= 0) & (np.where(pstate >= 0, smatch[np.maximum(pstate, 0)], -1) != s_maj)
    region_ch = (pregion >= 0) & (np.where(pregion >= 0, rmatch[np.maximum(pregion, 0)], -1) != r_maj)
    flags = (owner_ch * 1) | (state_ch * 2) | (region_ch * 4) | (redrawn * 8)
    changed = np.nonzero(flags)[0]
    # who held each province that changed hands, and who holds it now: the flows, most provinces first
    pair = {int(i): (alltags[o_maj[i]] if o_maj[i] >= 0 else "", alltags[p_owner[i]] if p_owner[i] >= 0 else "")
            for i in np.nonzero(owner_ch)[0]}
    flows = Counter(pair.values())
    flow_list = [fp for fp, _ in flows.most_common()]
    flow_ix = {fp: k for k, fp in enumerate(flow_list)}
    matched_old = set(int(v) for v in smatch if v >= 0)
    sa, so = N["a"]["states"], O["a"]["states"]
    added = [[s, sa[s]["name"], sa[s]["owner"]] for s in range(ns_n) if smatch[s] < 0]
    removed = [[so[t]["name"], so[t]["owner"], so[t]["label"][0], so[t]["label"][1]]
               for t in range(ns_o) if t not in matched_old]
    renamed = [[s, so[int(smatch[s])]["name"], sa[s]["name"]] for s in range(ns_n)
               if smatch[s] >= 0 and so[int(smatch[s])]["name"] != sa[s]["name"]]
    reshaped = [s for s in range(ns_n) if smatch[s] >= 0 and siou[s] < 0.98]

    def on_map(a):
        return {c["tag"] for c in a["countries"] if c["states"]}

    def in_mod(a):
        return {c["tag"]: c["name"] for c in a["countries"]}
    mn, mo = in_mod(N["a"]), in_mod(O["a"])
    gone_map = sorted(on_map(O["a"]) - on_map(N["a"]))
    return dict(
        prev=O["a"].get("built"), prevExported=O["a"].get("exported"),
        provinces=[[int(i), int(flags[i]), flow_ix[pair[int(i)]] if int(i) in pair else -1] for i in changed],
        counts=dict(owner=int(owner_ch.sum()), state=int(state_ch.sum()), region=int(region_ch.sum()),
                    redrawn=int(redrawn.sum()), provincesBefore=no, provincesNow=nn, statesBefore=ns_o, statesNow=ns_n),
        flows=[[a, b, flows[(a, b)]] for a, b in flow_list],
        statesAdded=added, statesRemoved=removed, statesRenamed=renamed, statesReshaped=reshaped,
        countriesAdded=[[t, mn[t]] for t in sorted(set(mn) - set(mo))],
        countriesRemoved=[[t, mo[t]] for t in sorted(set(mo) - set(mn))],
        onMapAdded=[[t, mn.get(t, t)] for t in sorted(on_map(N["a"]) - on_map(O["a"]))],
        onMapRemoved=[[t, mn.get(t, mo.get(t, t))] for t in gone_map],
        names={t: mn.get(t, mo.get(t, t)) for t in set(mn) | set(mo)})


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--changes-only", action="store_true", help="only compare work/atlas/ with work/atlas_prev/ again")
    args = ap.parse_args()
    t0 = time.time()
    if args.changes_only:
        ch = changes(OUT, PREV)
    else:
        for f in ("work/provinces.npz", "work/regions.json", MOD / "history/states"):
            if not Path(f).exists():
                sys.exit(f"{f} is missing: build the mod first (sh scripts/run_all.sh)")
        tmp = Path("work/atlas.tmp")
        if tmp.exists():
            shutil.rmtree(tmp)
        tmp.mkdir(parents=True)
        export(tmp)
        ch = changes(tmp, OUT)
        (tmp / "changes.json").write_text(json.dumps(ch, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        if OUT.exists():
            if PREV.exists():
                shutil.rmtree(PREV)
            OUT.rename(PREV)
        tmp.rename(OUT)
    (OUT / "changes.json").write_text(json.dumps(ch, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    c = ch.get("counts")
    if c:
        print(f"changes since {ch['prev']}: {len(ch['provinces'])} provinces ({c['owner']} owner, {c['state']} state, "
              f"{c['region']} region, {c['redrawn']} redrawn), {len(ch['statesAdded'])} states added, "
              f"{len(ch['statesRemoved'])} removed, {len(ch['statesRenamed'])} renamed")
    else:
        print(ch["note"])
    files = sorted(f for f in OUT.iterdir() if f.is_file())
    total = sum(f.stat().st_size for f in files)
    big = max(files, key=lambda f: f.stat().st_size)
    print(f"wrote {OUT}: {len(files)} files, {total / 1e6:.1f} MB (largest {big.name}, {big.stat().st_size / 1e6:.1f} MB) "
          f"in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
