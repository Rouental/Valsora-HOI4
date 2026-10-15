"""A preview of the game's fonts replaced by deco ones (v0.8, game_fonts.py): each font as the game draws it today
and as the mod will, with strings of the kind it shows.

    python preview_game_fonts.py "<folder with the game's gfx/fonts textures>"   -> build/preview_game_fonts.png

The game's font textures are not in the reference copy (its sparse checkout leaves them out); point the script at a
folder holding them (with their .fnt files), or it draws only the mod's.
"""
import os
import re
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from paths import BUILD, MOD

GAME_DIR = sys.argv[1] if len(sys.argv) > 1 else None
LABEL = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
ROWS = [
    ("hoi_18mbs", "lists, names, values", ["Political Advisor: Industrial Expansion", "Rouental — 42.3M population, 56 states"]),
    ("hoi_16mbs", "small text, requirements", ["Requires: Has completed National Focus", "Construction speed +10%, Stability −5%"]),
    ("hoi_18", "light text", ["Infantry Division (8 infantry, 1 artillery)", "Available in 32 days"]),
    ("hoi_20b", "bold labels", ["Army Group Vale of Reibonne", "Field Marshal Serelle Cahun"]),
    ("cg_16b", "tooltips", ["Roland II Cahun, Sovereign Prince of Rouental,", "Duke of Carcarelle, Count of Vair and Hevique."]),
    ("hoi4_typewriter16_inverted", "unit and leader screens", ["Division Template: Royal Host", "Organisation 60 · Recovery 0.30"]),
    ("vic_18", "settings, menus, filters", ["Show notifications for this event", "Autosave: monthly"]),
    ("hoi_24header", "headers", ["Production", "War Overview"]),
    ("hoi_36header", "window titles", ["Construction", "Political View"]),
]


def load(base):
    t = open(base + ".fnt", encoding="utf-8-sig", errors="ignore").read()
    common = dict(re.findall(r"(\w+)=(-?\d+)", re.search(r"^common .*$", t, re.M).group(0)))
    chars = {}
    for line in t.split("\n"):
        if line.startswith("char "):
            d = {k: int(v) for k, v in re.findall(r"(\w+)=(-?\d+)", line)}
            chars[d["id"]] = d
    kern = {(int(a), int(b)): int(k) for a, b, k in re.findall(r"kerning first=(\d+)\s+second=(\d+)\s+amount=(-?\d+)", t)}
    tex = next(p for p in (base + ".dds", base + ".tga") if os.path.exists(p) and os.path.getsize(p) > 0)
    return dict(common=common, chars=chars, kern=kern, atlas=np.asarray(Image.open(tex).convert("RGBA"), np.float32) / 255)


def draw(canvas, f, s, x, y, col):
    pen, prev = x, None
    for ch in s:
        cp = ord(ch)
        if cp not in f["chars"]:
            continue
        c = f["chars"][cp]
        if prev is not None:
            pen += f["kern"].get((prev, cp), 0)
        g = f["atlas"][c["y"]:c["y"] + c["height"], c["x"]:c["x"] + c["width"]]
        gx, gy = pen + c["xoffset"], y + c["yoffset"]
        h, w = g.shape[:2]
        if gx >= 0 and gy >= 0 and gx + w <= canvas.shape[1] and gy + h <= canvas.shape[0]:
            a = g[..., 3:4]
            canvas[gy:gy + h, gx:gx + w] = canvas[gy:gy + h, gx:gx + w] * (1 - a) + g[..., :3] * np.array(col) * a
        pen += c["xadvance"]
        prev = cp
    return pen - x


def main():
    W = 1180
    lab = ImageFont.truetype(LABEL, 12)
    blocks = []
    for name, use, texts in ROWS:
        ours = load(MOD + f"gfx/fonts/{name}")
        game = None
        if GAME_DIR and os.path.exists(os.path.join(GAME_DIR, name + ".fnt")):
            try:
                game = load(os.path.join(GAME_DIR, name))
            except StopIteration:           # its texture isn't there
                game = None
        blocks.append((name, use, texts, game, ours))
    H = 30 + sum(2 * (int(o["common"]["lineHeight"]) + 8) + 26 for *_, o in blocks)
    canvas = np.ones((H, W, 3), np.float32) * np.array([17, 25, 30]) / 255
    labels = []
    y = 24
    col = (0.96, 0.93, 0.85)
    for name, use, texts, game, ours in blocks:
        lh = int(ours["common"]["lineHeight"])
        labels.append((f"{name}", f"{use}", y))
        for i, s in enumerate(texts):
            yy = y + i * (lh + 8)
            if game:
                draw(canvas, game, s, 230, yy, col)
            draw(canvas, ours, s, 705, yy, col)
        y += 2 * (lh + 8) + 26
    im = Image.fromarray((np.clip(canvas, 0, 1) * 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    d.text((230, 4), "the game's font today", font=lab, fill=(120, 160, 170))
    d.text((705, 4), "the Deco UI's replacement (same line height, no wider)", font=lab, fill=(183, 166, 128))
    for name, use, yy in labels:
        d.text((12, yy), name, font=lab, fill=(232, 223, 200))
        d.text((12, yy + 16), use, font=lab, fill=(150, 150, 140))
    im.save(BUILD + "preview_game_fonts.png")
    print("game fonts preview written")


if __name__ == "__main__":
    main()
