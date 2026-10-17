"""build/preview_windows.png (+ _vanilla): the window frames window_art.py draws, as the game lays them out (2026-10-17,
v0.10): the confirmation popup (popupwindow.gui, default_confirmation_popup), the world tension window
(worldtensionwindowpopup.gui), a tutorial hint (tutorialscreen.gui) and the aces window (acesview.gui, the close
button's socket), with the Deco UI's pictures and fonts and with the game's pictures.

    python preview_windows.py
"""
import numpy as np
from PIL import Image

import validate_preview as V
from ddsutil import read_dds
from paths import ART, BUILD, MOD, VANILLA

GI = "gfx/interface/"


def pic(rel, vanilla):
    if not vanilla:
        try:
            return read_dds(MOD + rel)
        except FileNotFoundError:
            pass
    return Image.open(VANILLA + rel).convert("RGBA")


def frame(im, n, i):
    fw = im.width // n
    return im.crop((i * fw, 0, (i + 1) * fw, im.height))


def draw(vanilla):
    W, H = 2260, 1240
    bg = Image.open(ART + "map_rouental.jpg").convert("RGB").resize((2205, 1240), Image.LANCZOS)
    cv = Image.new("RGBA", (W, H))
    cv.paste(bg.convert("RGBA"), (0, 0))
    cv.paste(bg.convert("RGBA").crop((0, 0, 55, H)), (2205, 0))
    texts = []

    def put(rel, x, y, n=1, i=0):
        cv.alpha_composite(frame(pic(rel, vanilla), n, i), (x, y))

    def tile(rel, x, y, w, h, bx, by):
        cv.alpha_composite(V.cornered(pic(rel, vanilla), w, h, bx, by), (x, y))

    def button(rel, x, y, text, font="hoi_18mbs"):
        im = pic(rel, vanilla)
        cv.alpha_composite(im, (x, y))
        texts.append((font, text, x, y, im.width, im.height, "centre", True))

    # the confirmation popup, 480 x 382
    x, y = 40, 40
    tile(GI + "tiles/tiled_window_pol_goal.dds", x, y, 480, 382, 180, 85)
    texts += [("hoi_24header", "Release Lustiana?", x + 10, y + 16, 450, 40, "centre", True),
              ("hoi_18mbs", "Lustiana will be released as an independent nation and take its cores with it. "
               "Its people will remember who set them free.", x + 24, y + 90, 430, 215, "centre", False)]
    button(GI + "button_148x34.dds", x + 90, y + 310, "Decline")
    button(GI + "button_148x34.dds", x + 260, y + 310, "Accept")
    # the release dialog's picture (pol_goal_popup_bg, 480 x 382), plain
    x, y = 40, 470
    put(GI + "pol_goal_popup_bg.dds", x, y)
    texts += [("hoi_24header", "Peace Conference Summary", x + 10, y + 16, 450, 40, "centre", True)]
    # the world tension window, 527 x 534
    x, y = 580, 40
    put(GI + "world_tension_bg.dds", x, y)
    tile(GI + "tiles/tiled_plain_bg.dds", x + 13, y + 126, 500, 343, 32, 32)
    texts.append(("hoi_24header", "World Tension", x + 20, y + 28, 487, 30, "centre", True))
    for i, (bx, t) in enumerate([(40, "Date"), (149, "Country"), (258, "Tension"), (385, "Wars")]):
        sb = pic(GI + "sort_button_100x29_2.dds", vanilla)
        cv.alpha_composite(frame(sb, 2, 1), (x + bx, y + 87))
        texts.append(("hoi_18mbs", t, x + bx, y + 87, 100, 29, "centre", True))
    button(GI + "button_123x34.dds", x + 204, y + 475, "Close")
    # a tutorial hint, 613 x 576
    x, y = 1150, 40
    put(GI + "tutorial/hint_bg.dds", x, y)
    texts += [("hoi_24header", "National Focus", x + 114, y + 28, 388, 41, "centre", True),
              ("hoi_18mbs", "Your nation's focus tree sets its course: each focus takes some days to complete and "
               "grants its reward when done. Pick the next one from the tree once the current focus is finished, "
               "and your nation will not lose a day.", x + 82, y + 98, 446, 330, "left", False)]
    # the aces window, 500 x 510 (tiled_window_w_close), its close button in the socket
    x, y = 1780, 40
    tile(GI + "tiles/tiled_window_w_close.dds", x, y, 440, 510, 64, 64)
    put(GI + "closebutton.dds", x + 440 - 45, y + 13, 1, 0)
    texts.append(("hoi_24header", "Aces", x + 20, y + 17, 380, 30, "centre", True))
    # a small air wing window, 276 x 253
    x, y = 1780, 600
    tile(GI + "tiles/tiled_window_w_close.dds", x, y, 276, 253, 64, 64)
    put(GI + "closebutton.dds", x + 276 - 53, y + 10, 1, 0)

    arr = np.asarray(cv.convert("RGB"), dtype=np.float32) / 255
    for font, s, tx, ty, w, h, fmt, valign in texts:
        V.draw_text(arr, font, s, tx, ty, w, fmt, max_h=h, valign=valign)
    out = BUILD + ("preview_windows_vanilla.png" if vanilla else "preview_windows.png")
    Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8)).save(out)
    print("written", out)


if __name__ == "__main__":
    draw(False)
    draw(True)
