"""Build interface/eventwindow.gui (v0.7): the events in the mod's fonts.

    python make_events.py "<HOI4 install folder>"

The game's events are paper (a clipboard report, a newspaper) with dark typewriter fonts. Their pictures are
replaced at the game's paths by gen_textures.py (the 'ev_' keys: lacquer, gilt rails, a crest, the superevent's
style), so the text needs the mod's light fonts: titles in gilt capitals, the text and the options in cream.
Positions and every element of the game's file are kept: the game sizes the middle to the text and stacks the
pieces itself. v0.7.1: each window's options are centred in the room they have (layout_events).
"""
import os
import sys

import guipatch as GP
import layout_events as LE
from paths import MOD, VANILLA as VANILLA_DIR

# options in the body font: in the menu's tracked capitals 811 of the game's 10,171 options would need a third line,
# which the 40 px box cuts off (4 in the body font)
TITLE, TEXT, OPTION, NAME = "valsora_deco_title_18", "valsora_deco_body_15", "valsora_deco_body_15", "valsora_deco_heading_22"
FONTS = {
    "EventWindow>top_Window>Title": TITLE,
    "EventWindow>midsection>Description": TEXT,
    "EventWindow_Operative>top_Window>Title": TITLE,
    "EventWindow_Operative/leader_fullname": NAME,
    "EventWindow_Operative/leader_codename": TEXT,
    "EventWindow_Operative>midsection>Description": TEXT,
    "EventWindow_leader>top_Window>Title": TITLE,
    "EventWindow_leader>midsection>Description": TEXT,
    "EventWindow_News>top_Window>Title": TITLE,
    "EventWindow_News>midsection>Description": TEXT,
    "event_option_entry>Name": OPTION,
}

ARG = sys.argv[1] if len(sys.argv) > 1 else VANILLA_DIR
t = open(os.path.join(ARG, "interface", "eventwindow.gui"), encoding="utf-8-sig").read().replace("\r\n", "\n")
for path, font in FONTS.items():
    t = GP.set_attrs(t, path, font=font)
# the options: the entry as wide as its plate, the text centred on it, each window's grid centred in its room
W, PAD = LE.OPTION_W, LE.OPTION_PAD
t = GP.set_attrs(t, "event_option_entry", size=(W, 47))
t = GP.set_attrs(t, "event_option_entry>Name", position=(PAD, 0), maxWidth=W - 2 * PAD)
for win in LE.CENTRES:
    x, y = GP.get_pos(t, f"{win}/options_grid")
    t = GP.set_attrs(t, f"{win}/options_grid", position=(LE.grid_x(win), y), size=(W, 30 if win in ("EventWindow", "EventWindow_News") else 0),
                     slotsize=(W, 47))
GP.write_gui(MOD + "interface/eventwindow.gui", t)
print("eventwindow.gui written")
