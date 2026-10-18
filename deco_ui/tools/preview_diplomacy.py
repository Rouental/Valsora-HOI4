"""build/preview_diplomacy.png (+ _vanilla): the diplomacy panel's header row and its leader block (the
countrydiplomacyview.gui's flag row and diplomacy_tab_top, as the game lays them: the flag and its frame, the strip
behind them, the leader's portrait under its frame, the politics block with its pie, the national focus button and its
progress frame), with Rouental's flag and Roland's portrait from the Valsora build, the Deco UI's pictures and the
game's (v0.10.4, diplomacy_art.py).

    python preview_diplomacy.py
"""
import math

import numpy as np
from PIL import Image, ImageDraw

import diplomacy_art as DA
from ddsutil import read_dds
from paths import BUILD, MOD, VALSORA, VANILLA

GI = "gfx/interface/"


def pic(rel, vanilla):
    if not vanilla:
        try:
            return read_dds(MOD + rel)
        except FileNotFoundError:
            pass
    return Image.open(VANILLA + rel).convert("RGBA")


def fake_pie(r):
    """a pie of four parties' colours, as the game draws one (radius r)"""
    im = Image.new("RGBA", (2 * r, 2 * r))
    d = ImageDraw.Draw(im)
    a = -90
    for share, col in ((.46, (59, 114, 180)), (.27, (200, 170, 90)), (.17, (160, 40, 40)), (.10, (120, 120, 120))):
        d.pieslice((0, 0, 2 * r - 1, 2 * r - 1), a, a + share * 360, fill=col + (255,))
        a += share * 360
    return im


def draw(vanilla):
    W, H = 560, 300
    cv = Image.new("RGBA", (W, H), (17, 25, 30, 255))
    put = lambda im, x, y: cv.alpha_composite(im, (round(x), round(y)))  # noqa: E731
    # the flag row (its container's y 16 here, as the elements reach 10 px above it)
    oy = 16
    put(pic(GI + "diplo_upper_win_bg.dds", vanilla), 139, oy - 4)
    flag = Image.open(VALSORA + "gfx/flags/ROU.tga").convert("RGBA")
    put(flag, *((40, oy + 1) if vanilla else (33, oy + 6)))
    put(pic(GI + "diplo_flag_frame.dds", vanilla), *((14, oy - 10) if vanilla else (7, oy - 5)))
    # diplomacy_tab_top
    oy = 110
    face = read_dds(VALSORA + "gfx/leaders/VAL/ROU_roland_cahun.dds")
    sc = .74 if vanilla else DA.PORTRAIT_SCALE
    face = face.resize((round(face.width * sc), round(face.height * sc)), Image.LANCZOS)
    put(face, *((20, oy + 10) if vanilla else (25, oy + 28)))
    put(pic(GI + "diplo_leader_frame.dds", vanilla), 13, oy)
    put(pic(GI + "diplo_top_bg_diplo_tab.dds", vanilla), 138, oy)
    put(fake_pie(33), 157 + 35.5 - 33, oy + 9 + 35.5 - 33)
    put(pic(GI + "pol_piechart_overlay.dds", vanilla), 157, oy + 9)
    gb = pic(GI + "diplo_goal_button.dds", vanilla)
    put(gb.crop((0, 0, gb.width // 3, gb.height)), 144 + 103, oy + 88 + 7)
    put(pic(GI + "pol_goal_progress_frame.dds", vanilla), 144 + 127, oy + 88 + 57)
    out = BUILD + ("preview_diplomacy_vanilla.png" if vanilla else "preview_diplomacy.png")
    cv.convert("RGB").save(out)
    print("written", out)


if __name__ == "__main__":
    draw(False)
    draw(True)
