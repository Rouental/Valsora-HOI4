"""A numbered map of the land strategic regions, for the author to name them (2026-10-16, the user's overnight list:
"a numbered map of the land strategic regions ("Region n") so I can name them").

Every land region gets a number, printed at its most inland point; numbers run continent by continent, west to east
in bands from the north. Each number is tied to the region's colour on the Strategic Regions layer
(dist/region_numbers.json), which is how the build names regions (source/region_names.json, by colour: the sea's
names are there already), so a name given by number survives a rebuild that renumbers the regions. Run after a build:

    python3 scripts/region_map.py                -> dist/region_numbers.png, .json, dist/region_names.md
    python3 scripts/region_map.py --apply FILE   -> the names in FILE ("12 = Name" or "12: Name", one a line) into
                                                    source/region_names.json; then rebuild
    python3 scripts/region_map.py --draft        -> dist/region_names_draft.md: a first draft of every name (Claude's),
                                                    in the table --apply reads
    python3 scripts/region_map.py --names-map [FILE]  -> dist/region_names_map.png: the map with the names of FILE's
                                                    table (the draft by default) where the numbers are (2026-10-19, the
                                                    author: "Please provide the map with the region names on it")
"""
import json
import re
import sys
from collections import Counter

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi

from common import CONTINENTS, COUNTRIES

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SCALE = 2                     # the map at half the game's size
BAND = 420                    # numbering bands, game pixels from the north
NAMES = "source/region_names.json"


def regions():
    """the land regions: (number, region id, colour, continent, owners by share, current name, inland pixel)"""
    p = np.load("work/provinces.npz")
    prov, cont = p["prov"], p["cont"]
    rj = json.load(open("work/regions.json"))
    region_of = np.load("work/regions.npz")["region_of"]
    by_tag = {v[0]: c for c, v in COUNTRIES.items()}
    loc = {}
    for line in open("build/valsora_test/localisation/english/valsora_l_english.yml", encoding="utf-8-sig"):
        m = re.match(r'\s*VAL_REGION_(\d+):0 "(.*)"', line)
        if m:
            loc[int(m.group(1))] = m.group(2)
    reg_px = region_of[prov]
    out = []
    for r, rg in enumerate(rj["regions"]):
        if rg["kind"] != "land":
            continue
        mask = reg_px == r
        ys, xs = np.nonzero(mask)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        dist = ndi.distance_transform_edt(np.pad(mask[y0:y1, x0:x1], 1))[1:-1, 1:-1]
        iy, ix = np.unravel_index(int(np.argmax(dist)), dist.shape)
        c = Counter(int(cont[i]) for i in rg["provinces"]).most_common(1)[0][0]
        owners = Counter()
        for s in rg["states"]:
            owners[COUNTRIES[by_tag[rj["owners"][s]]][1]] += 1
        out.append(dict(id=r + 1, colour=rg["colour"], continent=CONTINENTS[c - 1], owners=[o for o, _ in owners.most_common()],
                        name=loc.get(r + 1, ""), x=int(x0 + ix), y=int(y0 + iy), cy=float(ys.mean()), cx=float(xs.mean())))
    out.sort(key=lambda g: (CONTINENTS.index(g["continent"]), int(g["cy"] // BAND), g["cx"]))
    for n, g in enumerate(out, 1):
        g["number"] = n
    return out, reg_px, rj


def draw(regs, reg_px, rj, out="dist/region_numbers.png", label=None,
         title="Valsora's land strategic regions, numbered (dist/region_names.md lists them)"):
    land = np.isin(reg_px, [g["id"] - 1 for g in regs])
    h, w = reg_px.shape
    img = np.zeros((h, w, 3), np.float32)
    img[:] = (0.86, 0.91, 0.95)                                    # sea, pale blue
    colour = {g["id"] - 1: tuple(int(g["colour"][i:i + 2], 16) / 255 for i in (0, 2, 4)) for g in regs}
    for r, c in colour.items():
        m = reg_px == r
        img[m] = 0.55 * np.array(c) + 0.45                          # each region its own colour, lightened
    edge = np.zeros((h, w), bool)
    edge[:, 1:] |= reg_px[:, 1:] != reg_px[:, :-1]
    edge[1:, :] |= reg_px[1:, :] != reg_px[:-1, :]
    edge &= land | np.roll(land, 1, 0) | np.roll(land, 1, 1)
    edge = ndi.binary_dilation(edge, iterations=1)
    img[edge] = (0.18, 0.16, 0.14)
    im = Image.fromarray((img * 255).astype(np.uint8)).resize((w // SCALE, h // SCALE), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    font = ImageFont.truetype(FONT, 17 if label is None else 12)
    for g in regs:
        text = str(g["number"]) if label is None else label(g)
        words = text.split(" ")
        if label is not None and len(text) > 14 and len(words) > 1:   # long names on two lines
            half = (len(words) + 1) // 2
            text = " ".join(words[:half]) + "\n" + " ".join(words[half:])
        d.multiline_text((g["x"] / SCALE, g["y"] / SCALE), text, font=font, fill=(20, 20, 20), anchor="mm",
                         align="center", stroke_width=3 if label is None else 2, stroke_fill=(255, 255, 255))
    lf = ImageFont.truetype(FONT, 22)
    d.text((24, 20), title, font=lf, fill=(20, 20, 20), stroke_width=3, stroke_fill=(255, 255, 255))
    im.save(out, optimize=True)


def names_map(regs, reg_px, path="dist/region_names_draft.md"):
    """the numbered map with the names of a table of --apply's kind (its number in the first column, the name in the
    last) written where the numbers are, a long name on two lines"""
    names = {}
    for line in open(path, encoding="utf-8"):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and cells[0].isdigit() and cells[-1]:
            names[int(cells[0])] = cells[-1]
    draw(regs, reg_px, None, out="dist/region_names_map.png", label=lambda g: names.get(g["number"], g["name"]),
         title=f"Valsora's land strategic regions, named ({path}: the numbers of dist/region_numbers.png)")
    print(f"{len(names)} names: dist/region_names_map.png")


def write(regs):
    json.dump({str(g["number"]): {k: g[k] for k in ("colour", "id", "continent", "owners", "name", "x", "y")} for g in regs},
              open("dist/region_numbers.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    lines = ["# Land strategic regions", "",
             "The numbers on `dist/region_numbers.png`. Write a name in the last column (or send \"12 = Name\" lines);",
             "`python3 scripts/region_map.py --apply FILE` puts them into `source/region_names.json`, by the region's",
             "colour. The current names are the build's (\"<country with most of its states> Region n\").", ""]
    for c in CONTINENTS:
        rows = [g for g in regs if g["continent"] == c]
        if not rows:
            continue
        lines += [f"## {COUNTRIES[c][1]}", "", "| # | countries | current name | new name |", "|---|---|---|---|"]
        for g in rows:
            own = ", ".join(g["owners"][:4]) + (" ..." if len(g["owners"]) > 4 else "")
            lines.append(f"| {g['number']} | {own} | {g['name']} | |")
        lines.append("")
    open("dist/region_names.md", "w", encoding="utf-8").write("\n".join(lines))


COMPASS = ["Northern", "North-Eastern", "Eastern", "South-Eastern", "Southern", "South-Western", "Western",
           "North-Western"]


def qualify(word, base):
    """'Northern' + 'Sarkis' -> 'Northern Sarkis'; 'Northern' + 'The Marches' -> 'The Northern Marches'"""
    return f"The {word} {base[4:]}" if base.startswith("The ") else f"{word} {base}"


def compass(dx, dy, near):
    """the compass word for an offset (map y runs south); 'Central' within `near` px"""
    if np.hypot(dx, dy) < near:
        return "Central"
    return COMPASS[int(((np.degrees(np.arctan2(dx, -dy)) + 22.5) % 360) // 45)]


def compass_words(ns, info, e):
    """one word each for a nation's several regions (Northern, North-Eastern ... Central, then Far ...), the closest to
    where each lies from the nation's centre, none used twice (an assignment, so two regions both to the west become
    North-Western and Western rather than Western twice)"""
    from scipy.optimize import linear_sum_assignment
    radius = (e["a"] / np.pi) ** 0.5
    labels = COMPASS + ["Central"] + [f"Far {w}" for w in COMPASS]
    cost = np.zeros((len(ns), len(labels)))
    for a, n in enumerate(ns):
        dx, dy = info[n]["x"] - e["x"], info[n]["y"] - e["y"]
        d = np.hypot(dx, dy) / radius
        ang = np.degrees(np.arctan2(dx, -dy)) % 360
        for b, w in enumerate(labels):
            if w == "Central":
                cost[a, b] = 4 * d
                continue
            k = COMPASS.index(w.replace("Far ", ""))
            diff = abs((ang - 45 * k + 180) % 360 - 180) / 45
            cost[a, b] = diff + 4 * max(0.0, 0.35 - d) + (1.5 + 3 * max(0.0, 1.1 - d) if w.startswith("Far") else 0)
    rows, cols = linear_sum_assignment(cost)
    return {ns[a]: labels[b] for a, b in zip(rows, cols)}


def draft(regs, reg_px, rj):
    """a first draft of every land region's name, Claude's, for the author to change (2026-10-17, the author's "Sure,
    do 1, 3, and 7"; 3 was "Draft names for the 137 land regions ... built from the nations and geography"): a nation's
    only region on a continent takes its name (its adjective and the continent's name for a colony); a nation's
    several regions take compass names round its centre ("Northern Sarkis", "Central Sarkis"), the islands off its
    main landmass "the <adjective> Isles"; two or three small nations together are named after them; four or more
    after the ocean their coast faces most ("Midtierre Coast"), or "Inner <continent>"; Rouental's region is the Vale
    of Reibonne. Names met twice get a compass word between them. Writes dist/region_names_draft.md, in the table
    `--apply` reads (the last column)."""
    p = np.load("work/provinces.npz")
    prov, kind, cont = p["prov"], p["kind"], p["cont"]
    r = np.load("work/regions.npz")
    size, centre, state_of, region_of = r["size"], r["centre"], r["state_of"], r["region_of"]
    by_tag = {v[0]: v for v in COUNTRIES.values()}
    owners = rj["owners"]
    sea_names = json.load(open(NAMES, encoding="utf-8"))
    land = kind[prov] == 1
    lm, _ = ndi.label(land)
    lm_of = np.zeros(len(kind), np.int64)
    lm_of[prov[land]] = lm[land]
    cities = {}
    for k, v in json.load(open("source/city_names.json", encoding="utf-8")).items():
        x, y = (int(t) for t in k.split(","))
        cities.setdefault(int(region_of[prov[y, x]]), []).append(v)
    # each nation's land per continent: area, centre, main landmass
    nat = {}
    for st, g in enumerate(rj["states"]):
        g = [q for q in g if kind[q] == 1]
        for q in g:
            key = (owners[st], int(cont[q]))
            e = nat.setdefault(key, dict(a=0.0, x=0.0, y=0.0, lm=Counter(), regions=set()))
            e["a"] += size[q]
            e["y"] += centre[q][0] * size[q]
            e["x"] += centre[q][1] * size[q]
            e["lm"][int(lm_of[q])] += int(size[q])
            e["regions"].add(int(region_of[q]))
    for e in nat.values():
        e["x"] /= e["a"]
        e["y"] /= e["a"]
        e["main"] = e["lm"].most_common(1)[0][0]
    # each region: area by nation, centre, landmasses, the ocean its coast faces
    sea_region = {i: sea_names.get(rg["colour"], "") for i, rg in enumerate(rj["regions"]) if rg["kind"] == "sea"}
    coast = {}
    for a, b, c in rj["adjacency"]:
        for x, y in ((a, b), (b, a)):
            if kind[x] == 1 and kind[y] == 0:
                ocean = re.sub(r"\s*\d+$", "", sea_region.get(int(region_of[y]), ""))
                if ocean:
                    coast.setdefault(int(region_of[x]), Counter())[ocean] += c
    info = {}
    for g in regs:
        rid = g["id"] - 1
        provs = [q for q in rj["regions"][rid]["provinces"] if kind[q] == 1]
        area = Counter()
        mass = Counter()
        for q in provs:
            area[owners[state_of[q]]] += int(size[q])
            mass[int(lm_of[q])] += int(size[q])
        tot = sum(area.values())
        info[g["number"]] = dict(area=area, tot=tot, mass=mass, c=CONTINENTS.index(g["continent"]) + 1,
                                 x=float(sum(centre[q][1] * size[q] for q in provs) / tot),
                                 y=float(sum(centre[q][0] * size[q] for q in provs) / tot), rid=rid)
    cont_c = {}
    for i in info.values():
        e = cont_c.setdefault(i["c"], [0.0, 0.0, 0.0])
        e[0] += i["tot"]
        e[1] += i["x"] * i["tot"]
        e[2] += i["y"] * i["tot"]
    cont_c = {k: (v[1] / v[0], v[2] / v[0], (v[0] / np.pi) ** 0.5) for k, v in cont_c.items()}
    vale = max(info, key=lambda n: info[n]["area"].get("ROU", 0))
    names, why = {}, {}
    for g in regs:
        i = info[g["number"]]
        top = [t for t, _ in i["area"].most_common()]
        share = i["area"][top[0]] / i["tot"]
        nm = lambda t: by_tag[t][1]
        c = i["c"]
        if g["number"] == vale:
            names[g["number"]], why[g["number"]] = "The Vale of Reibonne", "Rouental and its neighbours (your name for it)"
        elif share >= 0.9:
            t = top[0]
            e = nat[(t, c)]
            home = max((k for k in nat if k[0] == t), key=lambda k: nat[k]["a"])[1]
            isles = i["mass"].most_common(1)[0][0] != e["main"]
            # the nation's other regions of the same kind (its main land, or its islands) on this continent
            same = [n for n, j in info.items() if j["c"] == c and j["area"].most_common(1)[0][0] == t
                    and j["area"][t] / j["tot"] >= 0.9 and n != vale
                    and (j["mass"].most_common(1)[0][0] != e["main"]) == isles]
            if c != home:
                base = f"{by_tag[t][2]} {COUNTRIES[CONTINENTS[c - 1]][1]}"
                w = f"{nm(t)}'s land on {COUNTRIES[CONTINENTS[c - 1]][1]}"
            elif isles:
                base = f"The {by_tag[t][2]} Isles"
                w = f"{nm(t)}'s islands off its main land"
            else:
                base, w = nm(t), nm(t)
            if len(same) > 1:
                # several regions of one nation: compass words round its centre, each used once
                q = compass_words(same, info, e)[g["number"]]
                base = qualify(q, base)
                w += (f", the {q.lower()} ones" if isles else f", the {q.lower()} part") if q != "Central" else \
                    ", around its centre"
            names[g["number"]], why[g["number"]] = base, w
        elif len(top) <= 3:
            names[g["number"]] = " and ".join([", ".join(nm(t) for t in top[:-1]), nm(top[-1])]) if len(top) > 1 \
                else nm(top[0])
            why[g["number"]] = "the nations in it"
        else:
            oc = coast.get(i["rid"], Counter()).most_common(1)
            sea_ = re.sub(r" (Sea|Ocean)$", "", oc[0][0]) if oc else ""
            names[g["number"]] = f"The {sea_} Coast" if oc else f"Inner {COUNTRIES[CONTINENTS[c - 1]][1]}"
            why[g["number"]] = f"{len(top)} nations ({', '.join(nm(t) for t in top[:4])}{' ...' if len(top) > 4 else ''}); " \
                + (f"its coast faces the {oc[0][0]}" if oc else "inland")
    # coasts named twice: after the biggest nation on them instead
    seen = Counter(names.values())
    for n, v in list(names.items()):
        if seen[v] > 1 and v.endswith(" Coast"):
            names[n] = f"The {by_tag[info[n]['area'].most_common(1)[0][0]][2]} Coast"
    # names still met twice: a compass word round the middle of those that share it
    for _ in range(3):
        seen = {}
        for n, v in names.items():
            seen.setdefault(v, []).append(n)
        for v, ns in seen.items():
            if len(ns) < 2:
                continue
            mx = np.mean([info[n]["x"] for n in ns])
            my = np.mean([info[n]["y"] for n in ns])
            for n in ns:
                names[n] = qualify(compass(info[n]["x"] - mx, info[n]["y"] - my, 1), v)
    seen = Counter(names.values())
    for v in [v for v, k in seen.items() if k > 1]:
        for k, n in enumerate([n for n in names if names[n] == v], 1):
            names[n] = f"{v} {['I', 'II', 'III', 'IV', 'V', 'VI'][k - 1]}"
    lines = ["# Land strategic regions: a first draft of their names", "",
             "Claude's draft (2026-10-17), for you to change: the numbers are those on `dist/region_numbers.png`. Edit the",
             "last column (or empty it to keep the build's name), then `python3 scripts/region_map.py --apply",
             "dist/region_names_draft.md` puts every name in it into `source/region_names.json`; rebuild.",
             "How the drafts were made: a nation's only region takes its name; several regions of one nation take",
             "compass names round its centre (\"Northern Sarkis\"), its islands \"the ... Isles\", its land on another",
             "continent its adjective and the continent's name; two or three nations together are named after them, four",
             "or more after the sea their coast faces most (\"The Midtierre Coast\"; after their biggest nation when two",
             "coasts would share a name) or \"Inner <continent>\". Names that still came out twice got a compass word.",
             "Cities are the ones you named on the Cities layer.", ""]
    for c in CONTINENTS:
        rows = [g for g in regs if g["continent"] == c]
        if not rows:
            continue
        lines += [f"## {COUNTRIES[c][1]}", "", "| # | countries | why | cities | draft name |", "|---|---|---|---|---|"]
        for g in rows:
            own = ", ".join(g["owners"][:4]) + (" ..." if len(g["owners"]) > 4 else "")
            cs = ", ".join(cities.get(g["id"] - 1, [])[:4])
            lines.append(f"| {g['number']} | {own} | {why[g['number']]} | {cs} | {names[g['number']]} |")
        lines.append("")
    open("dist/region_names_draft.md", "w", encoding="utf-8").write("\n".join(lines))
    print(f"{len(names)} draft names in dist/region_names_draft.md ({len(set(names.values()))} different)")


def apply(path):
    nums = json.load(open("dist/region_numbers.json", encoding="utf-8"))
    names = json.load(open(NAMES, encoding="utf-8"))
    colours = {g["colour"] for g in regions()[0]}
    n = 0
    for line in open(path, encoding="utf-8"):
        m = re.match(r"\s*\|?\s*(\d+)\s*(?:=|:|\|)\s*(.+?)\s*\|?\s*$", line)
        if not m:
            continue
        num, name = m.group(1), m.group(2).split("|")[-1].strip()
        if not name:
            continue
        assert num in nums, f"no region {num} on the map"
        colour = nums[num]["colour"]
        assert colour in colours, f"region {num}'s colour {colour} is no longer on the map: run region_map.py again"
        names[colour] = name
        n += 1
    json.dump(names, open(NAMES, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{n} names into {NAMES}; rebuild (sh scripts/run_all.sh)")


if __name__ == "__main__":
    if "--apply" in sys.argv:
        apply(sys.argv[sys.argv.index("--apply") + 1])
    elif "--names-map" in sys.argv:
        i = sys.argv.index("--names-map")
        regs, reg_px, rj = regions()
        names_map(regs, reg_px, *sys.argv[i + 1:i + 2])
    elif "--draft" in sys.argv:
        regs, reg_px, rj = regions()
        draft(regs, reg_px, rj)
    else:
        regs, reg_px, rj = regions()
        draw(regs, reg_px, rj)
        write(regs)
        print(f"{len(regs)} land regions: dist/region_numbers.png, dist/region_numbers.json, dist/region_names.md")
