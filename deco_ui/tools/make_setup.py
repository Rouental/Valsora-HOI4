"""Build interface/frontendgamesetupview.gui (v0.10.1): the game's game setup screens, two changes, every element and
name kept (the pictures are setup_art.py's).

    python make_setup.py "<HOI4 install folder>"

- The country selection (gamesetup_interesting_countries_window) is one card wider. The game's window is 1225 px, eight
  of its 150 px country cards from x 15; the Vale of Reibonne start recommends eight nations, so with "Other countries"
  there are nine, and the ninth stuck out past the frame (the author's screenshot, 2026-10-17). The window is
  setup_art.CS_W wide; it is centred, so it grows setup_art.DX on each side, and everything laid out under the cards
  (the title, the filter buttons, the facts, the nation's name, spirits and focuses, the history) moves DX right to
  stay where it was on screen. The cards and the minor countries' lists still start at the left; the more-countries
  list is as much wider.
- The country's details on the map (gamesetup_country_details): the portrait, the faction emblem, the pie and the
  spirits were 9, 3 and 7 px apart, the emblem's well and the pie's overlapping ("The country info is a little
  disorganized"); they are 10 px apart on one centre line (setup_art.DT_*), and the pie's ring and centre (the frame
  and the overlay, setup_art.pie_frame and pie_overlay, the politics screen's style) are centred on the pie.
"""
import os
import sys

import guipatch as GP
import setup_art as SA
from paths import MOD, VANILLA as VANILLA_DIR

ARG = sys.argv[1] if len(sys.argv) > 1 else VANILLA_DIR
SRC = os.path.join(ARG, "interface", "frontendgamesetupview.gui")
t = open(SRC, encoding="utf-8-sig").read().replace("\r\n", "\n")

# ---------------------------------------------------------------- the country selection, one card wider
W = "gamesetup_interesting_countries_window"
t = GP.set_attrs(t, W, size=(SA.CS_W, 717))
for el in ("title", "filters", "info_title", "info", "minor_country_leader", "minor_portrait_overlay", "nation_title",
           "spirit", "history_title", "history"):
    x, y = GP.get_pos(t, f"{W}>{el}")
    t = GP.set_attrs(t, f"{W}>{el}", position=(x + SA.DX, y))
# the more-countries dropdown: its button at the right edge, its list as wide as the window (the game resizes it)
# (guipatch knows neither dropDownBoxType nor its expandButton and expandedWindow: the dropdown's block is found by hand
# and its two lines replaced)
s = t.rindex("dropDownBoxType", 0, t.index('name = "more_countries"'))
e = GP._block_end(t, s)
blk = t[s:e]
for old, new in (("position = { x = 1168 y = -4 }", f"position = {{ x = {1168 + 2 * SA.DX} y = -4 }}"),
                 ("size = { width=1205 height=58 }", f"size = {{ width={1205 + 2 * SA.DX} height=58 }}")):
    assert blk.count(old) == 1, ("the more-countries dropdown changed in the game's file", old)
    blk = blk.replace(old, new)
t = t[:s] + blk + t[e:]

# ---------------------------------------------------------------- the country's details, spaced
D = "gamesetup_country_details"
ex0, ey0, ex1, ey1 = SA.DT_EMBLEM
t = GP.set_attrs(t, f"{D}>pol_faction_icon", position=((ex0 + ex1) // 2 - 33, (ey0 + ey1) // 2 - 34))
for grid in ("spirit_grid", "spirit_grid_over_defined"):
    x, y = GP.get_pos(t, f"{D}>{grid}")
    t = GP.set_attrs(t, f"{D}>{grid}", position=(SA.DT_SPIRITS[0] + 6, y))
# the pie: the game draws the chart centred on its x with its top at its y (radius 26); the container is placed so the
# chart's centre is DT_PIE, and the ring (67 x 68, its centre at (33, 34)) and the centre (54 x 54) are centred on it
CHART = (20, -3)
cx, cy = SA.DT_PIE
t = GP.set_attrs(t, f"{D}>political_pie_chart", position=(cx - CHART[0], cy - SA.PIE_R - CHART[1]))
pcx, pcy = CHART[0], CHART[1] + SA.PIE_R            # the pie's centre inside the container
assert GP.get_pos(t, "political_pie_chart>chart") == CHART
t = GP.set_attrs(t, "political_pie_chart>pol_view_bg", position=(pcx - 27, pcy - 27))
t = GP.set_attrs(t, "political_pie_chart>piechart_frame", position=(pcx - 33, pcy - 34))

t = ("# Valsora Deco UI (make_setup.py): the game's file; the country selection one card wider, the country's details\n"
     "# spaced; every element and name kept\n" + t)
GP.check(t)
GP.write_gui(MOD + "interface/frontendgamesetupview.gui", t)
print(f"frontendgamesetupview.gui: the country selection {SA.CS_W} px wide (panels +{SA.DX}), the details spaced")
