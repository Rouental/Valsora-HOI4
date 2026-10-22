"""Guedelon's Council of Six as its leader's portrait: the author's symbol (source/portraits/gdn_council_of_six.png),
three ways. A: the symbol alone, centred on the portrait's dark field, as Krionik's Council of Marshals; B and C: the
symbol inside a lettered ring, as Krionik's emblem has one (B in French, Guedelon's language in the mod; C in English).
Each as the game shows it (156 x 210, gfx/leaders) and at full size, and a sheet of the three.

    python3 dist/portrait_proposals/guedelon_council_of_six/make.py
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "scripts"))
import nations  # noqa: E402

SYMBOL = os.path.join(REPO, "source", "portraits", "gdn_council_of_six.png")
FONT = os.path.join(REPO, "deco_ui", "source_fonts", "federo", "Federo-Regular.ttf")
GOLD, BLUE, NAVY = (242, 188, 81), (12, 103, 147), (7, 56, 88)   # the symbol's gold and blue; the ring's band darker
S = 1000                                                          # the seals' size, px


def arc_text(img, text, r, top, size, track=0.06):
    """letters set round a circle of radius r about the centre: along the top reading clockwise, upright outward, or
    along the bottom reading left to right, upright inward"""
    f = ImageFont.truetype(FONT, size)
    c = S / 2
    widths = [f.getlength(ch) + size * track for ch in text]
    total = sum(widths) - size * track
    ang = -total / 2 / r
    for ch, w in zip(text, widths):
        mid = ang + (w - size * track) / 2 / r
        ang += w / r
        if ch == " ":
            continue
        g = Image.new("RGBA", (size * 2, size * 2), (0, 0, 0, 0))
        d = ImageDraw.Draw(g)
        d.text((size, size), ch, font=f, fill=(*GOLD, 255), anchor="mm")
        if top:
            th = -math.pi / 2 + mid
            rot = math.degrees(th) + 90
        else:
            th = math.pi / 2 - mid
            rot = math.degrees(th) - 90
        g = g.rotate(-rot, resample=Image.BICUBIC)
        x, y = c + r * math.cos(th), c + r * math.sin(th)
        img.alpha_composite(g, (round(x - size), round(y - size)))


def diamond(d, x, y, s):
    d.polygon([(x, y - s), (x + s * .75, y), (x, y + s), (x - s * .75, y)], fill=(*GOLD, 255))


def ringed(top_text, bottom_text):
    """the symbol inside a band with a gold rim either side, its words in the band, diamonds at three and nine"""
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = S / 2
    for r, col in ((494, GOLD), (485, NAVY), (382, GOLD), (375, NAVY)):
        d.ellipse([c - r, c - r, c + r, c + r], fill=(*col, 255))
    sym = Image.open(SYMBOL).convert("RGBA")
    k = 2 * 372 / 490                                             # the symbol's disc (490 px) inside the inner rim
    sym = sym.resize((round(sym.width * k), round(sym.height * k)), Image.LANCZOS)
    img.alpha_composite(sym, (round(c - sym.width / 2), round(c - sym.height / 2)))
    arc_text(img, top_text, 434, True, 64)
    arc_text(img, bottom_text, 434, False, 64)
    for sx in (-1, 1):                                            # the diamonds between the words, as Krionik's stars
        diamond(d, c + sx * 434, c, 13)
        for k2 in (1, 2):
            dx = sx * 434 * math.cos(math.radians(7 * k2))
            dy = 434 * math.sin(math.radians(7 * k2))
            for sy in (-1, 1):
                d.ellipse([c + dx - 4, c + sy * dy - 4, c + dx + 4, c + sy * dy + 4], fill=(*GOLD, 255))
    return img


def in_game(src):
    """the portrait as the build makes it (nations.portrait): the disc 92 % of the width, centred on the dark field"""
    bx0, by0, bx1, by1 = Image.open(src).getchannel("A").getbbox()
    w = round((bx1 - bx0) / .92)
    h = round(w * 210 / 156)
    x0, y0 = bx0 - round((w - (bx1 - bx0)) / 2), by0 - round((h - (by1 - by0)) / 2)
    return Image.fromarray(nations.portrait(src, x0, y0, w)), (x0, y0, w)


def main():
    seals = {"A": Image.open(SYMBOL).convert("RGBA"),
             "B": ringed("CONSEIL DES SIX", "GUEDELON"),
             "C": ringed("COUNCIL OF SIX", "GUEDELON")}
    games, crops = {}, {}
    for k, im in seals.items():
        p = os.path.join(HERE, f"seal_{k}.png")
        im.save(p)
        games[k], crops[k] = in_game(p)
        games[k].save(os.path.join(HERE, f"portrait_{k}.png"))
    # the sheet: each at the game's size, twice it, and its seal, on the Deco UI's lacquer
    COL = 520
    W, H = 3 * COL + 40, 700
    sheet = Image.new("RGB", (W, H), (17, 25, 30))
    d = ImageDraw.Draw(sheet)
    f, fs = ImageFont.truetype(FONT, 30), ImageFont.truetype(FONT, 20)
    notes = {"A": "the symbol alone (as Krionik's)", "B": "in a ring, French", "C": "in a ring, English"}
    for i, k in enumerate("ABC"):
        x = 20 + i * COL
        d.text((x + COL / 2, 34), f"{k}: {notes[k]}", font=f, fill=(244, 236, 217), anchor="mm")
        g = games[k]
        sheet.paste(g.resize((312, 420), Image.LANCZOS), (x + 16, 70))
        sheet.paste(g, (x + 348, 70))
        d.text((x + 348 + 78, 294), "in game", font=fs, fill=(183, 166, 128), anchor="mm")
        seal = seals[k].resize((150, 150), Image.LANCZOS)
        sheet.paste(seal, (x + 351, 330), seal)
        d.text((x + 172, 512), "twice the game's size", font=fs, fill=(183, 166, 128), anchor="mm")
    d.text((W / 2, 584), "Guedelon's Council of Six: the author's symbol, its leader's portrait", font=f,
           fill=(227, 199, 126), anchor="mm")
    d.text((W / 2, 628), "A is in the mod; B or C replaces it in one line", font=fs, fill=(183, 166, 128), anchor="mm")
    sheet.save(os.path.join(HERE, "sheet.png"))
    for k in "ABC":
        print(k, "crop", crops[k])


if __name__ == "__main__":
    main()
