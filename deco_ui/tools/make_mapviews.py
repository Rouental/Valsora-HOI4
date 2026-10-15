"""Build interface/unitview.gui, airselectionview.gui and operativeleader.gui (v0.8.2): the game's views at the
screen's left edge under the top bar, moved down below the flag medallion and its seal.

    python make_mapviews.py "<HOI4 install folder>"

The game puts the selected armies' badges (unitview.gui's armies_view, with "Request Expeditionaries"), the selected
air wings (airselectionview.gui's air_selection_view) and the operatives (operativeleader.gui's operative_view) at
y 77-80, just under its own top bar; the Deco UI's medallion hangs over that corner down to y 169 (layout.SEAL), so it
covered them (the user's screenshot, 2026-10-15: "the army tab is covered up by the country tab"). Each now starts at
layout.BELOW_MEDALLION. Every element of the game's files is kept.
"""
import os
import sys

import guipatch as GP
import layout as L
from paths import MOD, VANILLA as VANILLA_DIR

ARG = sys.argv[1] if len(sys.argv) > 1 else VANILLA_DIR
VIEWS = {"unitview.gui": "armies_view", "airselectionview.gui": "air_selection_view",
         "operativeleader.gui": "operative_view"}

for f, win in VIEWS.items():
    t = open(os.path.join(ARG, "interface", f), encoding="utf-8-sig").read().replace("\r\n", "\n")
    x, y = GP.get_pos(t, win)
    assert y < L.BELOW_MEDALLION, (f, win, y)
    t = GP.set_attrs(t, win, position=(x, L.BELOW_MEDALLION))
    t = (f"# Valsora Deco UI (make_mapviews.py): the game's file, {win} moved down under the flag medallion "
         f"(y {y} -> {L.BELOW_MEDALLION}); every element and name kept\n" + t)
    GP.write_gui(MOD + "interface/" + f, t)
    print(f"{f}: {win} y {y} -> {L.BELOW_MEDALLION}")
