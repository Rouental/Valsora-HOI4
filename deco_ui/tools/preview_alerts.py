"""build/preview_alerts.png (+ _vanilla): the top bar with 30 alerts (2026-10-20, alerts_art.py), as alerts.gui lays them
out: from alerticon_startposition, alerticon_offset apart, the row broken where layout.ALERTS_END is meant to break it
(26 to the right-hand tray; the game's own break, read from one screenshot, is assumed), a few with their red and
yellow glows lit; and build/preview_loading_bar.png: the loading screen's status plate and tip (the ld_ textures), their
diamonds side by side, enlarged.

    python preview_alerts.py      (after validate_preview.py, which draws build/preview_topbar.png)
"""
import numpy as np
from PIL import Image

import layout as L
import validate_preview as V
from paths import BUILD, VANILLA

N, W, H = 70, 47, 42
FRAMES = [5, 6, 9, 10, 2, 3, 0, 7, 12, 13, 15, 16, 19, 1, 4, 8, 11, 14, 17, 18, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
GLOW = {3: "red", 8: "yellow", 12: "red", 27: "yellow"}


def strip(rel, vanilla):
    if vanilla:
        return Image.open(VANILLA + rel).convert("RGBA")
    return V.read_tex(rel).convert("RGBA")


def alerts(vanilla):
    top = Image.open(BUILD + "preview_topbar.png").convert("RGBA")
    if vanilla:
        top = top.crop((0, 0, 1920, 62)).resize((1920, 62))
    cv = Image.new("RGBA", (1920, 200), (24, 40, 64, 255))
    cv.alpha_composite(top.crop((0, 0, 1920, min(top.height, 200))), (0, 0))
    icons = strip("gfx/interface/alerts/global_alert_icons.dds", vanilla)
    glows = {c: strip(f"gfx/interface/{c}_alert_glow.dds", vanilla) for c in ("red", "yellow")}
    sx, sy = L.GUI(*L.ALERTS_START)
    end_x = (L.ALERTS_END + sx) / 2          # the reading of alerticon_endposition this layout assumes (layout.py)
    x, y = sx, sy
    for i, f in enumerate(FRAMES):
        if x > end_x:
            x, y = sx, y + 44
        cv.alpha_composite(icons.crop((f * W, 0, (f + 1) * W, H)), (int(x), int(y)))
        if i in GLOW:
            g = glows[GLOW[i]]
            cv.alpha_composite(g.crop((W, 0, 2 * W, H)), (int(x), int(y)))
        x += 48
    name = "preview_alerts_vanilla.png" if vanilla else "preview_alerts.png"
    cv.convert("RGB").save(BUILD + name)
    print("written", BUILD + name)


def loading():
    status = V.read_tex("gfx/interface/Loadingscreen_loadingstatus.dds").convert("RGBA")
    tip = V.read_tex("gfx/interface/Loadingscreen_loadingtip.dds").convert("RGBA")
    track = V.read_tex("gfx/interface/LoadingScreen_Progress_1.dds").convert("RGBA")
    fill = V.read_tex("gfx/interface/LoadingScreen_Progress_2.dds").convert("RGBA")
    cv = Image.new("RGBA", (1400, 300), (40, 52, 60, 255))
    cv.alpha_composite(status, (0, 0))
    cv.alpha_composite(track, (700 - 468, 62))
    cv.alpha_composite(fill.crop((0, 0, 560, fill.height)), (700 - 468, 62))
    cv.alpha_composite(tip, (0, 300 - 147))
    zoom = Image.new("RGBA", (1400, 300 + 260), (12, 17, 20, 255))
    zoom.alpha_composite(cv, (0, 0))
    a = cv.crop((640, 50, 760, 100)).resize((480, 200), Image.NEAREST)
    b = cv.crop((640, 160, 760, 210)).resize((480, 200), Image.NEAREST)
    zoom.alpha_composite(a, (180, 330))
    zoom.alpha_composite(b, (740, 330))
    zoom.convert("RGB").save(BUILD + "preview_loading_bar.png")
    print("written", BUILD + "preview_loading_bar.png")


if __name__ == "__main__":
    alerts(False)
    alerts(True)
    loading()
