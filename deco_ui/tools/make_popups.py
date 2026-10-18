"""Build interface/popupwindow.gui (v0.10.2): the game's popup windows, one change, every element and name kept (their
pictures are window_art.py's).

    python make_popups.py "<HOI4 install folder>"

- The release dialog (release_country_dialog): the game's text box runs from y 90 for 128 px, to y 218, past the first
  checkbox at y 198, so a long list of states ran over the checkboxes (the user's screenshot, 2026-10-18: "This screen
  overflows", Crvenognjište's forty-odd states of Krionik). It starts under the header band (window_art.pol_goal: to
  y 62) and ends above the checkbox (window_art.RELEASE_TEXT_Y, RELEASE_TEXT_END); the rest scrolls on the game's
  slider.
"""
import os
import sys

import guipatch as GP
from paths import MOD, VANILLA as VANILLA_DIR
from window_art import RELEASE_TEXT_END, RELEASE_TEXT_Y

ARG = sys.argv[1] if len(sys.argv) > 1 else VANILLA_DIR
t = open(os.path.join(ARG, "interface", "popupwindow.gui"), encoding="utf-8-sig").read().replace("\r\n", "\n")
D = "release_country_dialog"
x, y = GP.get_pos(t, f"{D}>description")
assert (x, y) == (23, 90), ("the release dialog's text moved in the game's file", x, y)
cx, cy = GP.get_pos(t, f"{D}>release_puppet_checkbox")
assert RELEASE_TEXT_END < cy, ("the release dialog's checkboxes moved in the game's file", cy)
t = GP.set_attrs(t, f"{D}>description", position=(x, RELEASE_TEXT_Y), maxHeight=RELEASE_TEXT_END - RELEASE_TEXT_Y)
GP.write_gui(MOD + "interface/popupwindow.gui", t)
print("popupwindow.gui written")
