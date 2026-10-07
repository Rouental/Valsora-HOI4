"""Every country in the built mod: a labelled world map and a table, for the author.

    python3 scripts/country_list.py   # after a build: dist/world_map_labelled.png,
                                      # dist/countries.md, dist/countries.csv

Everything is read from build/valsora_test (what the game gets): names and formal names
from the localisation, the ruling ideology from the country history, the sub-ideology
and the leader from the character who leads the ruling party, the culture from the
country's name list, and land from the state files.
"""
import csv
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi

import ideologies
from common import COUNTRIES, MAP_W as W, MAP_H as H

MOD = Path("build/valsora_test")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
CULTURE_NAMES = {
    "FRA": "French", "GER": "German", "ENG": "English", "ITA": "Italian", "SWE": "Swedish",
    "SPR": "Spanish", "POL": "Polish", "PER": "Persian", "JAP": "Japanese",
    "AST": "Australian", "POR": "Portuguese", "SOV": "Russian", "YUG": "Yugoslav",
    "USA": "American", "MEX": "Latin American", "HOL": "Dutch", "IRE": "Irish",
    "WLS": "Welsh", "PLY": "Polynesian"}


def loc():
    out = {}
    for f in (MOD / "localisation").rglob("*.yml"):
        for k, v in re.findall(r'^\s*([\w.]+):\d*\s+"(.*)"\s*$', f.read_text(encoding="utf-8-sig"), re.M):
            out.setdefault(k, v)
    return out


def name_blocks(path):
    text = path.read_text(encoding="utf-8")
    return {m.group(1): m.group(2) for m in re.finditer(r"^([A-Z]{3}) = \{(.*?)^\}", text, re.S | re.M)}


def male_names(block):
    m = re.search(r"male\s*=\s*\{\s*names\s*=\s*\{(.*?)\}", block, re.S)
    return m.group(1).split()[:12] if m else []


def rows():
    L = loc()
    src = {**name_blocks(Path("source/names/vanilla_names.txt")),
           **name_blocks(Path("source/names/custom_names.txt"))}
    by_males = {tuple(male_names(b)): k for k, b in src.items()}
    tag_names = name_blocks(MOD / "common/names/valsora_names.txt")
    sub_of, ids = {}, ideologies.ideology_of()
    for f in (MOD / "common/characters").glob("*.txt"):
        for cid, sub in re.findall(r"^\t(\w+) = \{.*?country_leader = \{\s*ideology = (\w+)",
                                   f.read_text(encoding="utf-8"), re.S | re.M):
            sub_of[cid] = sub
    sub_names = {k: n for subs in ideologies.SUBTYPES.values() for k, n, _ in subs}
    ide_names = {"democratic": "Democratic", "communism": "Communist", "fascism": "Authoritarian",
                 "neutrality": "Monarchist", "theocracy": "Theocratic"}  # the author's names
    states = {}
    for f in (MOD / "history/states").glob("*.txt"):
        t = f.read_text(encoding="utf-8")
        states[re.search(r"owner = (\w+)", t).group(1)] = states.get(re.search(r"owner = (\w+)", t).group(1), 0) + 1
    puppets = {}
    for f in (MOD / "history/countries").glob("*.txt"):
        for target, kind in re.findall(r"set_autonomy = \{ target = (\w+) autonomous_state = autonomy_(\w+)",
                                       f.read_text(encoding="utf-8")):
            puppets[target] = (f.name[:3], kind)
    out = []
    for f in sorted((MOD / "history/countries").glob("*.txt")):
        tag = f.name[:3]
        t = f.read_text(encoding="utf-8")
        rp = re.search(r"ruling_party\s*=\s*(\w+)", t).group(1)
        leader = next((c for c in re.findall(r"recruit_character\s*=\s*(\w+)", t)
                       if ids.get(sub_of.get(c)) == rp), None)
        culture = by_males.get(tuple(male_names(tag_names.get(tag, ""))), "?")
        note = []
        if tag in puppets:
            note.append(f"{puppets[tag][1]} of {L.get(puppets[tag][0], puppets[tag][0])}")
        if not states.get(tag):
            note.append("no land at the start (releasable or civil war)")
        out.append(dict(tag=tag, name=L.get(tag, tag), full=L.get(tag + "_DEF", ""),
                        ideology=ide_names.get(rp, rp),
                        subideology=sub_names.get(sub_of.get(leader), sub_of.get(leader, "")),
                        culture=CULTURE_NAMES.get(culture, culture),
                        leader=L.get(leader, leader or ""), states=states.get(tag, 0),
                        note="; ".join(note)))
    return out


def world_map(table):
    p = np.load("work/provinces.npz")
    prov = p["prov"]
    own = np.full(len(p["kind"]) + 1, -1)
    tags = [r["tag"] for r in table]
    for f in (MOD / "history/states").glob("*.txt"):
        t = f.read_text(encoding="utf-8")
        ids = np.array(re.search(r"provinces = \{([^}]*)\}", t).group(1).split(), int)
        own[ids] = tags.index(re.search(r"owner = (\w+)", t).group(1))
    O = own[prov + 1]
    cols = {v[0]: v[3] for v in COUNTRIES.values()}
    pal = np.array([cols.get(t, (128, 128, 128)) for t in tags] + [(0, 0, 0)], float)
    img = np.where((O >= 0)[..., None], pal[O] * 0.85 + 255 * 0.15, np.array([196, 214, 232.0]))
    edge = np.zeros(O.shape, bool)
    edge[:, 1:] |= O[:, 1:] != O[:, :-1]
    edge[1:] |= O[1:] != O[:-1]
    img[edge] = (40, 40, 40)
    im = Image.fromarray(img.astype(np.uint8))
    d = ImageDraw.Draw(im)
    boxes = []

    def free(b):
        return all(b[2] < o[0] or b[0] > o[2] or b[3] < o[1] or b[1] > o[3] for o in boxes)

    land = O >= 0
    order = sorted(range(len(tags)), key=lambda i: -(O == i).sum())
    for i in order:
        m = O == i
        if not m.any():
            continue
        name = table[i]["name"]
        lab, n = ndi.label(m)
        big = lab == (np.argmax(np.bincount(lab.ravel())[1:]) + 1)
        sl = ndi.find_objects(big.astype(int))[0]
        dist = ndi.distance_transform_edt(np.pad(big[sl], 1))[1:-1, 1:-1]
        y, x = np.unravel_index(np.argmax(dist), dist.shape)
        cx, cy = x + sl[1].start, y + sl[0].start
        width = sl[1].stop - sl[1].start
        size = int(np.clip(np.sqrt(m.sum()) / 6, 12, 64))
        fnt = ImageFont.truetype(FONT, size)
        tw = d.textlength(name, font=fnt)
        while tw > width * 1.15 and size > 12:
            size -= 2
            fnt = ImageFont.truetype(FONT, size)
            tw = d.textlength(name, font=fnt)
        inside = tw <= width * 1.3 and dist.max() * 2 >= size * 0.8
        pos = None
        if inside:
            b = (cx - tw / 2, cy - size / 2, cx + tw / 2, cy + size / 2)
            if free(b):
                pos = (cx, cy)
        if pos is None:  # a small country: the label beside it, with a pointer
            for r in range(30, 400, 14):
                for k in range(16):
                    a = k * np.pi / 8
                    px, py = cx + r * np.cos(a) * 1.6, cy + r * np.sin(a)
                    b = (px - tw / 2, py - size / 2, px + tw / 2, py + size / 2)
                    if b[0] < 0 or b[2] >= W or b[1] < 0 or b[3] >= H or not free(b):
                        continue
                    xs = np.clip([int(b[0]), int(b[2])], 0, W - 1)
                    ys = np.clip([int(b[1]), int(b[3])], 0, H - 1)
                    if land[ys[0]:ys[1], xs[0]:xs[1]].mean() > 0.4:
                        continue
                    pos = (px, py)
                    break
                if pos:
                    break
            if pos is None:
                pos = (cx, cy)
            d.line([(cx, cy), (pos[0], pos[1] + size / 2 if pos[1] < cy else pos[1] - size / 2)],
                   fill=(30, 30, 30), width=2)
            d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(30, 30, 30))
        b = (pos[0] - tw / 2, pos[1] - size / 2, pos[0] + tw / 2, pos[1] + size / 2)
        boxes.append(b)
        d.text(pos, name, font=fnt, fill=(15, 15, 15), anchor="mm",
               stroke_width=max(2, size // 9), stroke_fill=(255, 255, 255))
    return im


def main():
    table = rows()
    with open("dist/countries.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(table[0]))
        w.writeheader()
        w.writerows(table)
    lines = ["# Valsora: every country", "",
             f"{len(table)} countries, {sum(1 for r in table if r['states'])} owning land at the start. "
             "Read from the built mod; regenerate with `python3 scripts/country_list.py`.", "",
             "| Tag | Name | Full name | Ideology | Sub-ideology | Culture | Leader | States | Notes |",
             "|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(table, key=lambda r: r["name"]):
        lines.append("| " + " | ".join(str(r[k]) for k in
                                         ("tag", "name", "full", "ideology", "subideology", "culture",
                                          "leader", "states", "note")) + " |")
    Path("dist/countries.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    world_map(table).save("dist/world_map_labelled.png", optimize=True)
    print(f"wrote dist/countries.md, dist/countries.csv and dist/world_map_labelled.png ({len(table)} countries)")


if __name__ == "__main__":
    main()
