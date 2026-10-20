"""build/preview_insignia.png: the army insignias, the game's above the Deco UI's (insignia_art.py, 2026-10-20), each
then with its selected rim over it, at three times their size; the numbered shields and the gilt copies after the game's
81; the army groups' last. build/preview_insignia_picker.png: the picker's list as a Valsoran country sees it (6 a row,
42 x 44 a slot, insigniaselection.gui's item_grid: the 14 tintable insignias, the five of the game's own any country
may take, the numbered shields, the gilt copies) on the picker's picture, twice: tinted crimson, then blue, as the
game tints the frames army_icons.txt does not mark `color_override = no` (assumed: the army's colour multiplied in).

    python preview_insignia.py
"""
import math

from PIL import Image

import insignia_art as IA
from art_util import vanilla_frames
from ddsutil import read_dds
from paths import BUILD, MOD, VANILLA

Z, COLS, CELL = 3, 27, 38


def frames(rel, n, w):
    im = read_dds(MOD + rel)
    return [im.crop((k * w, 0, (k + 1) * w, im.height)) for k in range(n)]


def over(icon, rim):
    out = Image.new("RGBA", rim.size)
    out.alpha_composite(icon, ((rim.width - icon.width) // 2, (rim.height - icon.height) // 2))
    out.alpha_composite(rim)
    return out


def sheet():
    game = vanilla_frames(IA.A + "army_icons.dds", IA.GAME_N)
    gsel = vanilla_frames(IA.A + "army_selected_icons.dds", IA.GAME_N)
    ours = frames(IA.A + "army_icons.dds", IA.ALL_N, IA.W)
    osel = frames(IA.A + "army_selected_icons.dds", IA.ALL_N, IA.SW)
    ggrp = vanilla_frames(IA.A + "army_group_icons.dds", IA.GROUP_N)
    ogrp = frames(IA.A + "army_group_icons.dds", IA.GROUP_N, IA.W)
    rows = math.ceil((IA.ALL_N + IA.GROUP_N) / COLS)
    cv = Image.new("RGBA", (COLS * CELL * Z, rows * 4 * CELL * Z), (17, 25, 30, 255))
    for k in range(IA.ALL_N + IA.GROUP_N):
        r, c = divmod(k, COLS)
        x, y = c * CELL * Z, r * 4 * CELL * Z
        if k < IA.ALL_N:
            g, gs = (game[k], gsel[k]) if k < IA.GAME_N else (None, None)
            o, os_ = ours[k], osel[k]
        else:
            g, gs, o, os_ = ggrp[k - IA.ALL_N], None, ogrp[k - IA.ALL_N], None
        big = lambda im: im.resize((im.width * Z, im.height * Z), Image.NEAREST)  # noqa: E731
        if g is not None:
            cv.alpha_composite(big(g), (x, y))
            if gs is not None:
                cv.alpha_composite(big(over(g, gs)), (x, y + CELL * Z * 2))
        cv.alpha_composite(big(o), (x, y + CELL * Z))
        if os_ is not None:
            cv.alpha_composite(big(over(o, os_)), (x, y + CELL * Z * 3))
    out = BUILD + "preview_insignia.png"
    cv.convert("RGB").save(out)
    print("written", out)


FOR_ALL = (54, 55, 56, 60, 61)          # the game's insignias with no tag in their `available` (Waking the Tiger)
TINTED = set(range(IA.TINT_N)) | set(range(IA.NUMBERED0, IA.GILT0))


def tint(im, rgb):
    """the army's colour multiplied into a grey mask (assumed to be how the game colours them)"""
    r, g, b, a = im.split()
    from PIL import ImageChops
    col = Image.new("RGB", im.size, rgb)
    out = ImageChops.multiply(Image.merge("RGB", (r, g, b)), col)
    out.putalpha(a)
    return out


def picker():
    """the list as the picker lays it for a Valsoran country, on the picker's picture, in two army colours"""
    try:
        bg = read_dds(MOD + "gfx/interface/army_insignia_selection_bg.dds")
    except FileNotFoundError:
        bg = Image.open(VANILLA + "gfx/interface/army_insignia_selection_bg.dds").convert("RGBA")
    ours = frames(IA.A + "army_icons.dds", IA.ALL_N, IA.W)
    shown = list(range(IA.TINT_N)) + list(FOR_ALL) + list(range(IA.GAME_N, IA.ALL_N))
    rows = -(-len(shown) // 6)
    h = max(bg.height, 83 + 5 + rows * 44 + 10)
    out = Image.new("RGBA", (bg.width * 2 + 10, h), (17, 25, 30, 255))
    for j, rgb in enumerate(((186, 40, 40), (60, 110, 200))):
        x0 = j * (bg.width + 10)
        out.alpha_composite(bg, (x0, 0))
        for i, k in enumerate(shown):
            r, c = divmod(i, 6)
            icon = tint(ours[k], rgb) if k in TINTED else ours[k]
            out.alpha_composite(icon, (x0 + 22 + 5 + c * 42 + 4, 83 + 5 + r * 44 + 5))
    path = BUILD + "preview_insignia_picker.png"
    out.resize((out.width * 2, out.height * 2), Image.NEAREST).convert("RGB").save(path)
    print("written", path)


if __name__ == "__main__":
    sheet()
    picker()
