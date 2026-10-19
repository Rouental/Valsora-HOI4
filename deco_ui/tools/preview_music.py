"""build/preview_music.png (+ _vanilla): the music player as the game lays it out (2026-10-19), with the Deco UI's
pictures and fonts and with the game's, and the top bar's right end with the music controller open (the mod's only):
its tab under the music button.

The window is read from the game's musicplayer.gui (the Deco UI's copy where it ships one) with preview_popups.py's
canvas; what the game fills in by code is drawn here as it places it: the faceplate (music_station_base.gui) in the
faceplate window at (184, 0), a station's album art per row of the stations' column, the tracks, 30 px apart from the
list's margin (13, 15), the first playing and the fourth disabled.

    python preview_music.py
"""
import numpy as np
from PIL import Image

import preview_popups as PU
import validate_preview as V
from music_art import TAB
from paths import BUILD

TRACKS = [("Main Theme - Allies", "05:51"), ("Hearts of Men", "04:25"), ("The War Ends", "06:19"),
          ("A Song For the Children of WW2", "06:48"), ("Morning of D-day", "05:04"), ("End of the Tour", "03:23"),
          ("Krakow", "04:22"), ("Luftwaffe March - Reprise", "03:01"), ("Bring Forth the Tanks", "03:04"),
          ("The Attack", "03:30"), ("Axis Theme", "02:23"), ("Heavy Water", "04:34"), ("Operation Barbarossa", "03:04"),
          ("Days of Thunder", "03:23"), ("We Are Soldiers", "03:25")]


def player(c, x, y):
    c.window("musicplayer.gui", "musicplayer_window", x, y, size=(780, 600), samples={"cake": "Stations"})
    c.window("music_station_base.gui", "base_music_faceplate", x + 184, y, frames={"play_button": 1},
             samples={"track_name": "Soviet Suite - Finale", "track_elapsed": "00:22", "track_duration": "02:21"})
    for i in range(4):
        c.window("music_station_base.gui", "base_music_stations_entry", x + 14, y + 126 + 120 * i)
    for i, (name, length) in enumerate(TRACKS):
        ty = y + 116 + 15 + 30 * i
        c.window("musicplayer.gui", "music_track_entry", x + 180 + 13 + 5, ty,
                 hide={"play_track_button", "disable_track_button", "disabled_track"} | (set() if i == 0 else {"current_track"}),
                 samples={"track_label": name, "track_length": length})
        if i == 3:
            c.sprite("GFX_disabled_song", x + 180 + 13 + 5 - 14, ty + 6)   # the game draws it over a disabled track


def topbar_corner(vanilla):
    """the top bar's right end (the top bar preview) with the controller open, under the music button"""
    top = np.array(Image.open(BUILD + "preview_topbar.png").convert("RGB"), np.float32)[:180, 1380:1920] / 255
    if vanilla:
        return top
    X0 = 1380
    tab = V.read_tex("gfx/interface/valsora_deco/music_tab.dds")
    V.paste(top, tab, TAB["x"] - X0, TAB["y"])
    for (bx, by), rel, n in zip(TAB["buttons"], ("music_pause_button", "music_next_button", "musicplayer_button"),
                                (2, 1, 1)):
        V.paste(top, V.read_tex(f"gfx/interface/topbar/musicplayer/{rel}.dds"), TAB["x"] - X0 + bx, TAB["y"] + by,
                frame=1 if n == 2 else 0, frames=n)
    return top


def draw(vanilla):
    c = PU.Canvas(vanilla)
    player(c, 30, 30)
    out = (np.clip(c.cv, 0, 1) * 255).astype(np.uint8)[:660, :840]
    im = Image.fromarray(out)
    if not vanilla:
        corner = Image.fromarray((np.clip(topbar_corner(False), 0, 1) * 255).astype(np.uint8))
        sheet = Image.new("RGB", (im.width + corner.width + 30, max(im.height, corner.height)), (12, 17, 20))
        sheet.paste(im, (0, 0))
        sheet.paste(corner, (im.width + 30, 0))
        im = sheet
    name = "preview_music_vanilla.png" if vanilla else "preview_music.png"
    im.save(BUILD + name)
    print("written", BUILD + name)


if __name__ == "__main__":
    draw(False)
    draw(True)
