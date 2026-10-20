"""The production and construction screens' icons beside the game's (2026-10-20): every picture production_icons_art.py
and construction_art.py draw, and the add-a-line buttons, at 1x on the panels' lacquer and enlarged, the game's
above ours. Written to build/preview_production_icons.png and build/preview_construction_icons.png and a category
expanded, build/preview_construction_mock.png (the game's art:
build/ only, sent to the author, never committed).

    python3 tools/preview_production_icons.py        # after gen_textures.py pf_ cn_ ic_add_prod
"""
import os

from PIL import Image, ImageDraw, ImageFont

import construction_art as CA
import production_icons_art as PF
import proposals_icons as PI
from ddsutil import read_dds
from paths import BUILD, MOD, VANILLA

FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
LACQUER = (17, 25, 30, 255)


def game(rel):
    p = VANILLA + rel
    if not os.path.isfile(p):
        return None
    return Image.open(p).convert("RGBA")


def ours(rel):
    return read_dds(MOD + rel).convert("RGBA")


def sheet(rows, out, zoom=3, wrap=1500):
    """rows: (label, the game's, ours); each pair at 1x, then enlarged (narrower pictures more)"""
    blocks = []
    for label, g, n in rows:
        z = zoom if n.width * zoom <= wrap else max(1, wrap // n.width)
        h = 18 + (n.height + 6) * 2 + (n.height * z + 6) * 2
        blocks.append((label, g, n, z, h))
    W = max(max(n.width * z, n.width) for _, _, n, z, _ in blocks) + 30
    H = sum(b[4] + 14 for b in blocks) + 10
    cv = Image.new("RGBA", (max(W, 500), H), LACQUER)
    d = ImageDraw.Draw(cv)
    y = 8
    for label, g, n, z, h in blocks:
        d.text((10, y), label + "   (the game's, then ours; 1x and enlarged)", font=FONT, fill=(232, 223, 200))
        y += 18
        for im in (g, n):
            if im is not None:
                cv.alpha_composite(im, (10, y))
            y += n.height + 6
        for im in (g, n):
            if im is not None:
                cv.alpha_composite(im.resize((im.width * z, im.height * z), Image.NEAREST), (10, y))
            y += n.height * z + 6
        y += 14
    cv.convert("RGB").save(out)
    print("wrote", out)


def rows(adds):
    return [(rel, game(rel), ours(rel)) for key, rel, w, h, fn in adds]


def construction_mock():
    """a category of the construction screen expanded, as the game lays it (countryconstructionsview.gui): the header
    picture and its icon at (5, 9), the title at (60, 20), the buildings' grid from (28, 52) in 46 x 44 slots, each
    button 4 px down in its slot; the game's pictures beside ours"""
    out = []
    for src in (game, ours):
        cv = Image.new("RGBA", (267, 160), LACQUER)
        d = ImageDraw.Draw(cv)
        head = src("gfx/interface/diplo_details_header.dds")
        icon = src("gfx/interface/state_constructions.dds")
        strip = src("gfx/interface/buildings/building_icon_strip.dds")
        cv.alpha_composite(head, (5, 9))
        cv.alpha_composite(icon, (5, 9))
        d.text((60, 20), "State Buildings", font=FONT, fill=(232, 223, 200))
        for i in range(6):
            f = strip.crop((46 * i, 0, 46 * i + 46, 46))
            cv.alpha_composite(f, (28 + 46 * (i % 4), 52 + 44 * (i // 4) + 4))
        out.append(cv.resize((cv.width * 2, cv.height * 2), Image.NEAREST))
    sheet_im = Image.new("RGBA", (out[0].width * 2 + 30, out[0].height + 30), LACQUER)
    for k, im in enumerate(out):
        sheet_im.alpha_composite(im, (10 + k * (im.width + 10), 20))
    ImageDraw.Draw(sheet_im).text((10, 3), "a category expanded: the game's (left), ours (right), 2x", font=FONT,
                                  fill=(232, 223, 200))
    sheet_im.convert("RGB").save(BUILD + "preview_construction_mock.png")
    print("wrote", BUILD + "preview_construction_mock.png")


if __name__ == "__main__":
    lines = [r for r in PI.ITEMS if r[0].startswith("add_prod_")]
    sheet(rows([("", PI.GI + rel, w, h, None) for key, rel, w, h, art in lines]) + rows(PF.ADDS),
          BUILD + "preview_production_icons.png")
    if CA.ADDS:
        sheet(rows(CA.ADDS), BUILD + "preview_construction_icons.png")
    construction_mock()
