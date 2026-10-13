"""Every nation in the built mod on one sheet, grouped by continent, for the author.

    python3 scripts/nation_sheet.py   # after a build: dist/nations_by_continent.png

Each nation shows its flag, its ruler at the start (portrait and name), its full name,
its ideology and sub-ideology, and the culture its names come from (country_list.py
reads them all from build/valsora_test). Only portraits of our own are shown (the
author's and nations.PORTRAITS): a ruler with a base-game generic portrait, which isn't
in this repository, gets a box saying "placeholder". Nations go under the continent of
their capital; those with no land at the start (releasables, civil war countries) come
last in theirs. Flags are the pictures in source/flags, or the game's placeholder stripe.
"""
import re
import unicodedata
from pathlib import Path

from PIL import Image, ImageDraw

import ideologies
import nations
from collages import BG, BOLD, DIM, FRAME, GOLD, INK, REGULAR, continent_of, font, wrap
from common import CONTINENTS
from country_list import MOD, loc, rows

OUT = Path("dist/nations_by_continent.png")
FLAGS = Path("source/flags")
PW, PH = 78, 105        # portraits at half the game's 156 x 210
FW, FH = 123, 78        # flags at 1.5 x the game's 82 x 52
TW = 300                # text column
GAP = 12
CW = PW + FW + TW + 3 * GAP + 20   # card width
COLS, PAD = 4, 30
BOX = (52, 56, 62)


def leaders():
    """tag -> the character who rules at the start, and character -> portrait sprite"""
    sub_of, sprite = {}, {}
    for f in (MOD / "common/characters").glob("*.txt"):
        for cid, body in re.findall(r"^\t(\w+) = \{(.*?)^\t\}", f.read_text(encoding="utf-8"), re.S | re.M):
            m = re.search(r"country_leader = \{\s*ideology = (\w+)", body)
            if m:
                sub_of[cid] = m.group(1)
            m = re.search(r"large = \"?(\w+)", body)
            if m:
                sprite[cid] = m.group(1)
    group = ideologies.ideology_of()
    ruler = {}
    for f in (MOD / "history/countries").glob("*.txt"):
        t = f.read_text(encoding="utf-8")
        rp = re.search(r"ruling_party\s*=\s*(\w+)", t).group(1)
        ruler[f.name[:3]] = next((c for c in re.findall(r"recruit_character\s*=\s*(\w+)", t)
                                  if group.get(sub_of.get(c)) == rp), None)
    return ruler, sprite


def own_portraits():
    """sprite -> portrait file in the mod, for the portraits of our own"""
    out = {}
    for f in (MOD / "interface").glob("*.gfx"):
        for name, path in re.findall(r'name = "(GFX_portrait_\w+)"\s*texturefile = "([^"]+)"',
                                     f.read_text(encoding="utf-8")):
            out[name] = MOD / path
    return out


def flag(tag):
    src = FLAGS / f"{tag}.png"
    im = Image.open(src if src.exists() else MOD / f"gfx/flags/{tag}.tga").convert("RGB")
    return im.resize((FW, FH), Image.LANCZOS)


def plain(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()


def main():
    L = loc()
    table = {r["tag"]: r for r in rows()}
    where = continent_of()
    ruler, sprite = leaders()
    files = own_portraits()
    later = {**{t: "civil war country" for t in nations.CIVIL_WAR},
             **{t: "releasable" for t in nations.RELEASABLE}}
    groups = {c: [] for c in CONTINENTS}
    for tag, r in table.items():
        groups[where[tag]].append(r)
    for c in groups:
        groups[c].sort(key=lambda r: (r["states"] == 0, plain(r["name"])))

    name_f, text_f, small_f = font(BOLD, 16), font(REGULAR, 14), font(REGULAR, 13)
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))

    def lines(r):
        """(text, font, colour) lines of a nation's card"""
        tag = r["tag"]
        full = r["full"][:1].upper() + r["full"][1:] if r["full"] else r["name"]
        out = [(line, text_f, INK) for line in wrap(probe, full, text_f, TW)]
        out.append((f"Leader: {r['leader'] or '—'}", text_f, INK))
        out.append((f"{r['ideology']} · {r['subideology']}", text_f, INK))
        out.append((f"Culture: {r['culture']}", small_f, DIM))
        if not r["states"]:
            out.append((f"No land at the start ({later.get(tag, 'released later')})", small_f, DIM))
        return out

    def card_height(r):
        return max(PH, 22 + sum(18 for _ in lines(r)))

    # height: a heading per continent, then rows of cards as tall as their tallest
    def rows_of(entries):
        return [entries[i:i + COLS] for i in range(0, len(entries), COLS)]

    total = len(table)
    landed = sum(1 for r in table.values() if r["states"])
    height = PAD + 150
    for c, entries in groups.items():
        if entries:
            height += 70 + sum(max(card_height(r) for r in row) + 22 for row in rows_of(entries)) + 20
    width = 2 * PAD + COLS * CW
    im = Image.new("RGB", (width, height), BG)
    d = ImageDraw.Draw(im)
    d.text((PAD, PAD), "Valsora: every nation, by continent", font=font(BOLD, 34), fill=GOLD)
    y = PAD + 52
    note = (f"{total} nations in the game, {landed} with land at the start, under the continent of their "
            "capital. Each shows its flag, its ruler at the start, its full name, ideology and "
            "sub-ideology, and the culture its names come from. Rulers without a portrait of their own "
            "(a base-game generic one, not in this repository) have a placeholder box.")
    for line in wrap(d, note, font(REGULAR, 17), width - 2 * PAD):
        d.text((PAD, y), line, font=font(REGULAR, 17), fill=DIM)
        y += 23
    y = PAD + 150
    for c, entries in groups.items():
        if not entries:
            continue
        n_land = sum(1 for r in entries if r["states"])
        d.text((PAD, y), c.capitalize(), font=font(BOLD, 30), fill=GOLD)
        d.text((PAD + d.textlength(c.capitalize(), font=font(BOLD, 30)) + 16, y + 12),
               f"{len(entries)} nations" + (f", {len(entries) - n_land} of them without land at the start"
                                           if n_land < len(entries) else ""),
               font=font(REGULAR, 16), fill=DIM)
        d.line([(PAD, y + 48), (width - PAD, y + 48)], fill=FRAME, width=1)
        y += 70
        for row in rows_of(entries):
            for i, r in enumerate(row):
                x = PAD + i * CW
                tag = r["tag"]
                pic = files.get(sprite.get(ruler.get(tag)))
                if pic is not None and pic.exists():
                    im.paste(Image.open(pic).convert("RGB").resize((PW, PH), Image.LANCZOS), (x, y))
                else:
                    d.rectangle([x, y, x + PW - 1, y + PH - 1], fill=BOX)
                    d.text((x + PW / 2, y + PH / 2), "placeholder", font=small_f, fill=DIM, anchor="mm")
                d.rectangle([x - 1, y - 1, x + PW, y + PH], outline=FRAME)
                fx = x + PW + GAP
                im.paste(flag(tag), (fx, y))
                d.rectangle([fx - 1, y - 1, fx + FW, y + FH], outline=FRAME)
                tx, ty = fx + FW + GAP, y - 2
                d.text((tx, ty), r["name"], font=name_f, fill=GOLD)
                d.text((tx + d.textlength(r["name"], font=name_f) + 8, ty + 2), tag, font=small_f, fill=DIM)
                ty += 22
                for text, fnt, fill in lines(r):
                    d.text((tx, ty), text, font=fnt, fill=fill)
                    ty += 18
            y += max(card_height(r) for r in row) + 22
        y += 20
    im = im.crop((0, 0, width, y + PAD - 20))
    im.save(OUT, optimize=True)
    print(f"wrote {OUT} ({total} nations, {width}x{im.height})")


if __name__ == "__main__":
    main()
