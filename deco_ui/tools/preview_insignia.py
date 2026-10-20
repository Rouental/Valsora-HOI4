"""build/preview_insignia.png: the army insignias, the game's above the Deco UI's (insignia_art.py, 2026-10-20), each
then with its selected rim over it, at three times their size; the numbered shields after the game's 81; the army
groups' last. build/preview_insignia_picker.png: the picker's list (6 a row, 42 x 44 a slot, insigniaselection.gui's
item_grid) on the picker's picture, at the game's size, scrolled to the numbered shields.

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


def picker():
    """the list as the picker lays it, from the first numbered shield, on the picker's picture"""
    try:
        bg = read_dds(MOD + "gfx/interface/army_insignia_selection_bg.dds")
    except FileNotFoundError:
        bg = Image.open(VANILLA + "gfx/interface/army_insignia_selection_bg.dds").convert("RGBA")
    cv = Image.new("RGBA", bg.size, (17, 25, 30, 255))
    cv.alpha_composite(bg)
    ours = frames(IA.A + "army_icons.dds", IA.ALL_N, IA.W)
    start = IA.GAME_N - IA.GAME_N % 6
    for i, k in enumerate(range(start, min(IA.ALL_N, start + 30))):
        r, c = divmod(i, 6)
        cv.alpha_composite(ours[k], (22 + 5 + c * 42 + 4, 83 + 5 + r * 44 + 5))
    out = BUILD + "preview_insignia_picker.png"
    cv.resize((cv.width * 2, cv.height * 2), Image.NEAREST).convert("RGB").save(out)
    print("written", out)


if __name__ == "__main__":
    sheet()
    picker()
