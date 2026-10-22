"""Guedelon's Council of Seven as its leader's portrait: the author's symbol (source/portraits/gdn_council_of_seven.png)
in a lettered ring, CONSEIL DES SEPT above and GUEDELON below (the author chose this, version B of 2026-10-22, with the
new symbol and the council of seven: "in french, obviously"), centred on the portrait's dark field as Krionik's Council
of Marshals' emblem is.

    python3 dist/portrait_proposals/guedelon_council/make.py

Writes seal.png (the ring, 1000 px, clear outside it), gazetteer_portrait.png (468 x 630: three times HOI4's 156 x 210,
under the Gazetteer's 640 px, so the page keeps it whole and the import cuts nothing off), portrait_in_game.png (156 x
210, as the game shows it) and sheet.png.
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "scripts"))
import nations  # noqa: E402

SYMBOL = os.path.join(REPO, "source", "portraits", "gdn_council_of_seven.png")
FONT = os.path.join(REPO, "deco_ui", "source_fonts", "federo", "Federo-Regular.ttf")
GOLD, NAVY = (242, 188, 81), (7, 56, 88)          # the symbol's gold; the ring's band a darker blue than its field
S = 1000                                          # the seal's size, px
WORDS = ("CONSEIL DES SEPT", "GUEDELON")
GAZ = (468, 630)                                  # the Gazetteer's picture: 3 x 156 x 210


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
        ImageDraw.Draw(g).text((size, size), ch, font=f, fill=(*GOLD, 255), anchor="mm")
        th = -math.pi / 2 + mid if top else math.pi / 2 - mid
        rot = math.degrees(th) + (90 if top else -90)
        g = g.rotate(-rot, resample=Image.BICUBIC)
        img.alpha_composite(g, (round(c + r * math.cos(th) - size), round(c + r * math.sin(th) - size)))


def seal():
    """the symbol inside a band with a gold rim either side, the words in the band, a diamond and dots at three and
    nine, as Krionik's emblem has its stars"""
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = S / 2
    for r, col in ((494, GOLD), (485, NAVY), (382, GOLD), (375, NAVY)):
        d.ellipse([c - r, c - r, c + r, c + r], fill=(*col, 255))
    sym = Image.open(SYMBOL).convert("RGBA")
    k = 2 * 372 / 490                             # the symbol's disc (490 px) inside the inner rim
    sym = sym.resize((round(sym.width * k), round(sym.height * k)), Image.LANCZOS)
    img.alpha_composite(sym, (round(c - sym.width / 2), round(c - sym.height / 2)))
    arc_text(img, WORDS[0], 434, True, 64)
    arc_text(img, WORDS[1], 434, False, 64)
    for sx in (-1, 1):
        x = c + sx * 434
        d.polygon([(x, c - 13), (x + 10, c), (x, c + 13), (x - 10, c)], fill=(*GOLD, 255))
        for k2 in (1, 2):
            dx, dy = sx * 434 * math.cos(math.radians(7 * k2)), 434 * math.sin(math.radians(7 * k2))
            for sy in (-1, 1):
                d.ellipse([c + dx - 4, c + sy * dy - 4, c + dx + 4, c + sy * dy + 4], fill=(*GOLD, 255))
    return img


def main():
    s = seal()
    s.save(os.path.join(HERE, "seal.png"))
    # the Gazetteer's picture: the seal 92 % of the width on the game's dark field (nations.PORTRAIT_BG), no clear pixels
    W, H = GAZ
    g = Image.new("RGB", GAZ, nations.PORTRAIT_BG)
    d = round(W * .92)
    sm = s.resize((d, d), Image.LANCZOS)
    g.paste(sm, ((W - d) // 2, (H - d) // 2), sm)
    g.save(os.path.join(HERE, "gazetteer_portrait.png"))
    game = g.resize((156, 210), Image.LANCZOS)
    game.save(os.path.join(HERE, "portrait_in_game.png"))
    # the sheet: the Gazetteer's picture, the game's, the seal
    sheet = Image.new("RGB", (1180, 760), (17, 25, 30))
    dr = ImageDraw.Draw(sheet)
    f, fs = ImageFont.truetype(FONT, 30), ImageFont.truetype(FONT, 20)
    sheet.paste(g, (30, 80))
    dr.text((30 + W / 2, 730), "for the Gazetteer (468 x 630)", font=fs, fill=(183, 166, 128), anchor="mm")
    sheet.paste(game, (528, 80))
    dr.text((528 + 78, 310), "in game", font=fs, fill=(183, 166, 128), anchor="mm")
    big = s.resize((420, 420), Image.LANCZOS)
    sheet.paste(big, (730, 140), big)
    dr.text((940, 590), "the seal", font=fs, fill=(183, 166, 128), anchor="mm")
    dr.text((590, 40), "Guedelon's Conseil des Sept", font=f, fill=(227, 199, 126), anchor="mm")
    sheet.save(os.path.join(HERE, "sheet.png"))


if __name__ == "__main__":
    main()
