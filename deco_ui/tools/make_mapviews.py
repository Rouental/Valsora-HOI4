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
"""
import os
import re
import sys

import guipatch as GP
import layout as L
from paths import MOD, VANILLA as VANILLA_DIR

ARG = sys.argv[1] if len(sys.argv) > 1 else VANILLA_DIR
VIEWS = {"unitview.gui": "armies_view", "airselectionview.gui": "air_selection_view",
         "operativeleader.gui": "operative_view", "naviesview.gui": "naviesview_window"}
SIZE = {"naviesview_window": (500, "77%%")}                   # the game's: 500 x 86%%
BESIDE = {"naviesview.gui": ["home_base_selection_window", "ship_refit_equipment_view"]}


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
    t = (f"# Valsora Deco UI (make_mapviews.py): the game's file, {win} moved down under the flag medallion "
         f"(y {y} -> {L.BELOW_MEDALLION}"
         + (f", with {', '.join(BESIDE[f])}" if f in BESIDE else "") + "); every element and name kept\n" + t)
    GP.write_gui(MOD + "interface/" + f, t)
    print(f"{f}: {win} y {y} -> {L.BELOW_MEDALLION}" + (f", {len(BESIDE[f])} beside it" if f in BESIDE else ""))
