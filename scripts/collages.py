"""Collages for the author: every custom flag and every custom leader in the built mod.

    python3 scripts/collages.py   # after a build: dist/flags_collage.png, dist/leaders_collage.png

Flags are the pictures in source/flags (the build uses each one), in the game's 82:52
shape at twice its size; countries still on a placeholder stripe are listed below them.
Leaders are the characters with a portrait of our own (nations.PORTRAITS, at twice the
game's size) and the generated rulers the author named (nations.NAMED_LEADERS). Base-game
portraits aren't in this repository, so those get a labelled tile.
"""
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import ideologies
import nations
from country_list import MOD, loc

FLAGS = Path("source/flags")
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BG, FRAME, INK, DIM, GOLD = (31, 34, 38), (105, 105, 105), (232, 228, 218), (155, 155, 155), (238, 214, 150)
IDEOLOGY = {"democratic": "Democratic", "communism": "Communist", "fascism": "Authoritarian",
            "neutrality": "Monarchist", "theocracy": "Theocratic"}  # the author's names
FW, FH = 164, 104   # flags: 2 x the game's 82 x 52
PW, PH = 312, 420   # portraits: 2 x the game's 156 x 210


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, fnt, width):
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if not line or d.textlength(trial, font=fnt) <= width:
            line = trial
        else:
            lines.append(line)
            line = word
    return lines + [line] if line else lines


def heading(d, x, y, title, subtitle, width):
    d.text((x, y), title, font=font(BOLD, 32), fill=GOLD)
    y += 46
    for line in wrap(d, subtitle, font(REGULAR, 17), width):
        d.text((x, y), line, font=font(REGULAR, 17), fill=DIM)
        y += 23
    return y + 14


def flags(L):
    def key(stem):
        tag, _, var = stem.partition("_")
        base = L.get(tag, tag)
        if not var:
            return (base, 0, ""), base
        if var in IDEOLOGY:  # used while that government rules
            return (base, 1, var), f"{base} ({IDEOLOGY[var]})"
        return (base, 2, var), f"{L.get(stem, var.title())} ({base})"  # a cosmetic tag
    items = sorted(key(p.stem) + (p,) for p in FLAGS.glob("*.png"))
    tags = sorted(f.name[:3] for f in (MOD / "history/countries").glob("*.txt"))
    missing = sorted(L.get(t, t) for t in tags if not (FLAGS / f"{t}.png").exists())
    cols, cw, ch, pad = 10, FW + 22, FH + 52, 30
    width = pad * 2 + cols * cw
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    foot = wrap(probe, "Still a placeholder stripe in their map colour (no flag yet): "
                + ", ".join(missing) + ".", font(REGULAR, 16), width - 2 * pad)
    rows = -(-len(items) // cols)
    im = Image.new("RGB", (width, 150 + rows * ch + 30 + 22 * len(foot) + pad), BG)
    d = ImageDraw.Draw(im)
    top = heading(d, pad, pad, f"Valsora: the {len(items)} custom flags",
                  "As the game shows them (82 × 52), at twice the size. A flag named after a "
                  "government is used while that government rules.", width - 2 * pad)
    small = font(REGULAR, 13)
    for i, (_, label, path) in enumerate(items):
        x, y = pad + (i % cols) * cw + 11, top + (i // cols) * ch
        pic = Image.open(path).convert("RGBA").resize((FW, FH), Image.LANCZOS)
        tile = Image.new("RGBA", (FW, FH), BG + (255,))
        tile.alpha_composite(pic)
        im.paste(tile.convert("RGB"), (x, y))
        d.rectangle([x - 1, y - 1, x + FW, y + FH], outline=FRAME)
        for k, line in enumerate(wrap(d, label, small, FW)[:2]):
            d.text((x + FW / 2, y + FH + 8 + 16 * k), line, font=small, fill=INK, anchor="ma")  # the font's ascender line, so every label sits level
    y = top + rows * ch + 16
    for line in foot:
        d.text((pad, y), line, font=font(REGULAR, 16), fill=DIM)
        y += 22
    return im.crop((0, 0, width, y + pad)), len(items), missing


def leaders(L):
    ours = {f"GFX_portrait_{k}": k for k in nations.PORTRAITS}
    group_of = ideologies.ideology_of()
    subname = {k: n for subs in ideologies.SUBTYPES.values() for k, n, _ in subs}
    ruling = {f.name[:3]: re.search(r"ruling_party\s*=\s*(\w+)", f.read_text(encoding="utf-8")).group(1)
              for f in (MOD / "history/countries").glob("*.txt")}
    cards = {}  # (name, portrait) -> card; a character copied to a civil war country shares one
    for f in sorted((MOD / "common/characters").glob("*.txt")):
        for cid, body in re.findall(r"^\t(\w+) = \{(.*?)^\t\}", f.read_text(encoding="utf-8"), re.S | re.M):
            pic = re.search(r"large = (\w+)", body).group(1)
            if pic not in ours and cid not in nations.NAMED_LEADERS:
                continue
            tag, sub = cid.split("_")[0], re.search(r"country_leader = \{\s*ideology = (\w+)", body).group(1)
            group = group_of[sub]
            if tag in nations.CIVIL_WAR:
                role = "leads it in the civil war"
            elif ruling.get(tag) == group:
                role = "rules at the start"
            else:
                role = f"leads the {IDEOLOGY[group]} party"
            card = cards.setdefault((L.get(cid, cid), pic), {"lines": [], "notes": [], "first": tag})
            civil = " (civil war)" if tag in nations.CIVIL_WAR else ""
            card["lines"].append(f"{L.get(tag, tag)}{civil}: {subname.get(sub, sub)}, {role}")
            if cid in nations.REGNAL_NAMES:
                rtag, rkey = nations.REGNAL_NAMES[cid]
                card["notes"].append(f"Becomes {L[rkey]} on taking power in {L.get(rtag, rtag)}")
            if "corps_commander" in body and "Also a general" not in card["notes"]:
                card["notes"].append("Also a general")
    own = [(n, p, c) for (n, p), c in cards.items() if p in ours]
    base = [(n, p, c) for (n, p), c in cards.items() if p not in ours]
    order = lambda e: (L.get(e[2]["first"], ""), "rules" not in e[2]["lines"][0], e[0])
    own.sort(key=order)
    base.sort(key=order)
    big, mid, small = font(BOLD, 21), font(REGULAR, 15), font(REGULAR, 14)
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))

    def text_height(name, card):
        return (26 * len(wrap(probe, name, big, PW))
                + 19 * sum(len(wrap(probe, s, mid, PW)) for s in card["lines"])
                + 19 * sum(len(wrap(probe, s, small, PW)) for s in card["notes"]))
    cols, cw, pad = 6, PW + 30, 30
    ch = PH + 34 + max(text_height(n, c) for n, _, c in own + base)
    width = pad * 2 + cols * cw
    rows = -(-len(own) // cols) + -(-len(base) // cols)
    im = Image.new("RGB", (width, 150 + rows * ch + 2 * 50 + pad), BG)
    d = ImageDraw.Draw(im)
    y = heading(d, pad, pad, f"Valsora: the {len(own) + len(base)} custom leaders",
                "Portraits at twice the game's size (156 × 210). A leader who also heads a civil "
                "war country appears once.", width - 2 * pad)
    for title, entries in (("With portraits of their own", own),
                           ("Named, with base-game portraits (not in this repository, so not shown)", base)):
        d.text((pad, y), title, font=font(BOLD, 22), fill=INK)
        y += 40
        for i, (name, pic, card) in enumerate(entries):
            x, yy = pad + (i % cols) * cw + 15, y + (i // cols) * ch
            if pic in ours:
                src, x0, y0, w, tint = nations.PORTRAITS[ours[pic]]
                rgba = nations.portrait(src, x0, y0, w, size=(PW, PH))
                if tint == "red":
                    rgba = nations.redden(rgba)
                im.paste(Image.fromarray(rgba[..., :3]), (x, yy))
            else:
                d.rectangle([x, yy, x + PW - 1, yy + PH - 1], fill=(52, 56, 62))
                label = pic.replace("GFX_Portrait_", "").replace("_", " ")
                d.text((x + PW / 2, yy + PH / 2 - 14), "base-game portrait", font=mid, fill=DIM, anchor="mm")
                d.text((x + PW / 2, yy + PH / 2 + 12), label, font=mid, fill=INK, anchor="mm")
            d.rectangle([x - 1, yy - 1, x + PW, yy + PH], outline=FRAME)
            ty = yy + PH + 10
            for line in wrap(d, name, big, PW):
                d.text((x, ty), line, font=big, fill=GOLD)
                ty += 26
            for text, fnt, fill in [(t, mid, INK) for t in card["lines"]] + [(t, small, DIM) for t in card["notes"]]:
                for line in wrap(d, text, fnt, PW):
                    d.text((x, ty), line, font=fnt, fill=fill)
                    ty += 19
        y += -(-len(entries) // cols) * ch + 10
    return im.crop((0, 0, width, y + pad - 10)), len(own) + len(base)


def main():
    L = loc()
    im, n, missing = flags(L)
    im.save("dist/flags_collage.png", optimize=True)
    im2, m = leaders(L)
    im2.save("dist/leaders_collage.png", optimize=True)
    print(f"wrote dist/flags_collage.png ({n} flags; {len(missing)} countries without one) "
          f"and dist/leaders_collage.png ({m} leaders)")


if __name__ == "__main__":
    main()
