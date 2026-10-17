"""Build interface/unitview.gui, airselectionview.gui, operativeleader.gui (v0.8.2) and naviesview.gui (v0.8.4): the game's views at the
screen's left edge under the top bar, moved down below the flag medallion and its seal.

    python make_mapviews.py "<HOI4 install folder>"

The game puts the selected armies' badges (unitview.gui's armies_view, with "Request Expeditionaries"), the selected
air wings (airselectionview.gui's air_selection_view) and the operatives (operativeleader.gui's operative_view) at
y 77-80, just under its own top bar; the Deco UI's medallion hangs over that corner down to y 169 (layout.SEAL), so it
covered them (the user's screenshot, 2026-10-15: "the army tab is covered up by the country tab"). Each now starts at
layout.BELOW_MEDALLION. Every element of the game's files is kept.

v0.8.4: the navy too (naviesview.gui's naviesview_window, the selected fleets, shown at y 82; the user's screenshot,
2026-10-16: "like the army, the navy is covered by the flag tab"). It is 86 % of the screen tall, so it is made 77 %
to end where it did (y 1005 at 1080 rows; the game's ended at 1011); the two windows that open beside it (home base,
refits; x 490 and 510, clear of the medallion) move down as far, so their tops stay level with it.

v0.10.2: the fleet's names in the room they have (the user's screenshot, 2026-10-17: "Names run off screen"). A ship's
row cut its type short, "Advanced Destroyer (Advanced Destroy...": the game shrinks the type's box at runtime to end
where the row's insignia begins (x 450; the refit and repair buttons further left when they show), 240 px from x 210,
and "Advanced Destroyer (Advanced Destroyer I)" is 254 px in the redrawn hoi_18 (262 in the game's own font, so the
game cuts it too). The type is set in the game's font Main_14_bold, whose file garamond_14_bold game_fonts.py redraws
in Federo at 12.5 px (222 px, and the longest of the game's hull names twice over, "Coastal Defense Ship (Coastal
Defense Ship I)", 230), on the game's baseline. The admiral's name ran past the fleet picture's recess
(mapview_art.fleet_bg: x 77-195) under the skill badge (the game's box is 140 wide from x 81): it keeps to the recess
(112 px) on up to two lines of the same Federo (most names fit one, centred where the game's line sat; "Napoléon de
Montebrise" takes two), the rank 3 px higher to make the room. The home base's name was the panel's one text in the
game's own font (hoi_18b, not redrawn: 3 of Valsora's 63 city names cut at its 90 px): the redrawn hoi_16mbs, which
fits them all. preview_navy.py draws the panel and checks every text's room.
"""
import os
import re
import sys

import guipatch as GP
import layout as L
from paths import MOD, VANILLA as VANILLA_DIR

ARG = sys.argv[1] if len(sys.argv) > 1 else VANILLA_DIR
VIEWS = {"unitview.gui": "armies_view", "airselectionview.gui": "air_selection_view",
         "operativeleader.gui": "operative_view", "naviesview.gui": "naviesview_window",
         "hotjoin.gui": "hotjoin_window"}             # multiplayer: the host's list of join requests (medallion_check)
SIZE = {"naviesview_window": (500, "77%%")}                   # the game's: 500 x 86%%
BESIDE = {"naviesview.gui": ["home_base_selection_window", "ship_refit_equipment_view"]}
# v0.10.2: the fleet panel's texts (see above): element -> (font, dy to keep the game's baseline, other attributes).
# hoi_18 and hoi_18b put their baseline 14 px into the box, hoi_16mbs 13 and garamond_14_bold 11 (the game's own
# metrics, which game_fonts.py keeps).
NAME_FONT = "Main_14_bold"              # the game's font of its garamond_14_bold file, white: Federo 12.5 px, 14 px line
NAME_W, NAME_LINES = 112, 2             # the admiral's recess: x 81 (the name's x) to 193; two lines
TEXTS = {"naviesview.gui": {
    "ship_entry_detailed>ship_type": (NAME_FONT, 14 - 11, {}),
    "fleet_view_header>leader_desc": (None, -3, {}),
    # one line centred where the game's sat (baseline y 79), two lines filling the recess under the rank (to y 89)
    "fleet_view_header>leader_name": (NAME_FONT, -5, dict(maxWidth=NAME_W, maxHeight=14 * NAME_LINES,
                                                          vertical_alignment="center")),
    "home_base_view>home_base_name": ("hoi_16mbs", 14 - 13, {}),
}}


def shown(t, path):
    """(x, y) where the window shows: its show_position, else its position"""
    s, e = GP.find_block(t, path)
    head, _ = GP.own_region(t[s:e])
    m = re.search(r"\bshow_position\s*=\s*\{\s*x\s*=\s*(-?\d+)\s*y\s*=\s*(-?\d+)\s*\}", GP._strip_comments(head))
    return (int(m.group(1)), int(m.group(2))) if m else None


def move_down(t, path, dy):
    """the window dy lower, shown and closed"""
    x, y = GP.get_pos(t, path)
    attrs = dict(position=(x, y + dy))
    sp = shown(t, path)
    if sp:
        attrs["show_position"] = (sp[0], sp[1] + dy)
    return GP.set_attrs(t, path, **attrs)


for f, win in VIEWS.items():
    t = open(os.path.join(ARG, "interface", f), encoding="utf-8-sig").read().replace("\r\n", "\n")
    x, y = shown(t, win) or GP.get_pos(t, win)
    assert y < L.BELOW_MEDALLION, (f, win, y)
    dy = L.BELOW_MEDALLION - y
    t = move_down(t, win, dy)
    if win in SIZE:
        t = GP.set_attrs(t, win, size=SIZE[win])
    for other in BESIDE.get(f, []):
        t = move_down(t, other, dy)
    for path, (font, ty, more) in TEXTS.get(f, {}).items():
        tx, y0 = GP.get_pos(t, path)
        t = GP.set_attrs(t, path, position=(tx, y0 + ty), **(dict(font=font) if font else {}), **more)
    t = (f"# Valsora Deco UI (make_mapviews.py): the game's file, {win} moved down under the flag medallion "
         f"(y {y} -> {L.BELOW_MEDALLION}"
         + (f", with {', '.join(BESIDE[f])}" if f in BESIDE else "")
         + (f"; the fleet's names in their room ({', '.join(p.split('>')[-1] for p in TEXTS[f])})" if f in TEXTS else "")
         + "); every element and name kept\n" + t)
    GP.write_gui(MOD + "interface/" + f, t)
    print(f"{f}: {win} y {y} -> {L.BELOW_MEDALLION}" + (f", {len(BESIDE[f])} beside it" if f in BESIDE else ""))
