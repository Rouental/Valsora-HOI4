"""Build interface/unitleaderwindow.gui and interface/ingamemenu.gui (2026-10-21): two of the game's button rows that
the Deco UI's buttons don't fit, moved, every element and name kept.

    python make_buttons.py "<HOI4 install folder>"

- The commander pickers (unitleaderwindow.gui: armyleaderwindow, navyleaderwindow, factioncommanderwindow; the
  author's screenshots, 2026-10-21: "For both the army and navy, the show officers and unassign buttons are cut off").
  Their buttons are anchored to the window's foot (LOWER_RIGHT, y -32 and -31) in a window 590 px tall; the game's
  button pictures are 36 px tall with a blank foot, the Deco UI's 34 px drawn to their last row, so the chamfered rim
  ran 2-3 px past the window's edge and was cut off. They move up to y -36 (BUTTON_Y), centred in the footer band
  designer_art.leader_window draws (y 546-597; the window's buttons 554-588).
- The load and save windows (ingamemenu.gui: ingamemenu_load, ingamemenu_save; the author's screenshot: "Load and
  back are running into each other"): Back at x 100 and Load (Save) at x 245, both 148 px wide, so the game's own
  buttons overlap by 3 px, which its soft-edged pictures hid and the Deco UI's gilt rims don't. They are set 10 px
  apart (BACK_X, GO_X), centred on the window's foot picture (load_save_bottom, x 76-422).
"""
import os
import sys

import guipatch as GP
from paths import MOD, VANILLA as VANILLA_DIR

ARG = sys.argv[1] if len(sys.argv) > 1 else VANILLA_DIR

BUTTON_Y = -36            # the pickers' foot buttons: top at 590 - 36 = 554, bottom at 588
PICKERS = {"armyleaderwindow": ["no_leader_button", "new_leader_button", "show_divisional_commanders_button"],
           "navyleaderwindow": ["no_leader_button", "new_leader_button", "show_ship_captains_button"],
           "factioncommanderwindow": ["no_leader_button"]}
BUTTON_W, FOOT = 148, (76, 346)     # the load and save windows' buttons, and their foot picture's x and width
GAP = 10
BACK_X = FOOT[0] + (FOOT[1] - 2 * BUTTON_W - GAP) // 2
GO_X = BACK_X + BUTTON_W + GAP
SAVES = {"ingamemenu_load": "load", "ingamemenu_save": "save"}


def read(name):
    return open(os.path.join(ARG, "interface", name), encoding="utf-8-sig").read().replace("\r\n", "\n")


t = read("unitleaderwindow.gui")
for win, buttons in PICKERS.items():
    s, e = GP.find_block(t, win)
    assert "height=590" in t[s:s + 400].replace(" ", ""), f"{win}'s height changed in the game's file"
    for b in buttons:
        x, y = GP.get_pos(t, f"{win}>{b}")
        assert y in (-31, -32), (f"{win}>{b} moved in the game's file", x, y)
        t = GP.set_attrs(t, f"{win}>{b}", position=(x, BUTTON_Y))
GP.write_gui(MOD + "interface/unitleaderwindow.gui", t)
print("unitleaderwindow.gui written")

t = read("ingamemenu.gui")
for win, go in SAVES.items():
    for b, x0, x in (("cancel", 100, BACK_X), (go, 245, GO_X)):
        px, py = GP.get_pos(t, f"{win}>{b}")
        assert (px, py) == (x0, 503), (f"{win}>{b} moved in the game's file", px, py)
        t = GP.set_attrs(t, f"{win}>{b}", position=(x, py))
GP.write_gui(MOD + "interface/ingamemenu.gui", t)
print("ingamemenu.gui written")
