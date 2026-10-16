"""A numbered map of the land strategic regions, for the author to name them (2026-10-16, the user's overnight list:
"a numbered map of the land strategic regions ("Region n") so I can name them").

Every land region gets a number, printed at its most inland point; numbers run continent by continent, west to east
in bands from the north. Each number is tied to the region's colour on the Strategic Regions layer
(dist/region_numbers.json), which is how the build names regions (source/region_names.json, by colour: the sea's
names are there already), so a name given by number survives a rebuild that renumbers the regions. Run after a build:

    python3 scripts/region_map.py                -> dist/region_numbers.png, .json, dist/region_names.md
    python3 scripts/region_map.py --apply FILE   -> the names in FILE ("12 = Name" or "12: Name", one a line) into
                                                    source/region_names.json; then rebuild
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


def draw(regs, reg_px, rj):
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
    font = ImageFont.truetype(FONT, 17)
    for g in regs:
        d.text((g["x"] / SCALE, g["y"] / SCALE), str(g["number"]), font=font, fill=(20, 20, 20), anchor="mm",
               stroke_width=3, stroke_fill=(255, 255, 255))
    lf = ImageFont.truetype(FONT, 22)
    d.text((24, 20), "Valsora's land strategic regions, numbered (dist/region_names.md lists them)", font=lf,
           fill=(20, 20, 20), stroke_width=3, stroke_fill=(255, 255, 255))
    im.save("dist/region_numbers.png", optimize=True)


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
    else:
        regs, reg_px, rj = regions()
        draw(regs, reg_px, rj)
        write(regs)
        print(f"{len(regs)} land regions: dist/region_numbers.png, dist/region_numbers.json, dist/region_names.md")
