"""Build interface/eventwindow.gui (v0.7): the events in the mod's fonts.

    python make_events.py "<HOI4 install folder>"

The game's events are paper (a clipboard report, a newspaper) with dark typewriter fonts. Their pictures are
replaced at the game's paths by gen_textures.py (the 'ev_' keys: lacquer, gilt rails, a crest, the superevent's
style), so the text needs the mod's light fonts: titles in gilt capitals, the text and the options in cream.
Positions and every element of the game's file are kept: the game sizes the middle to the text and stacks the
pieces itself. v0.8: each window's options are centred in the room they have (layout_events). v0.8.1: the news
page's picture, headline and story are centred on the page, as its masthead is. v0.10.2: the news story in the 13 px
body font, so a long one ends above the ornament over its option (the user's screenshot: "Text on event runs over");
the country and leader events' text boxes two and three lines taller, so the body font's longest texts keep their last
lines (layout_events).
"""
import os
import sys

import guipatch as GP
import layout_events as LE
from paths import MOD, VANILLA as VANILLA_DIR

# options: in the menu's tracked capitals 811 of the game's 10,171 options would need a third line (4 in the body
# font); since v0.8.2 their own font (Josefin 14 on a 14 px line) fits three lines on the plate, where the body font's
# third line spilled over it (the user's screenshot of the long test event)
TITLE, TEXT, OPTION, NAME = "valsora_deco_title_18", "valsora_deco_body_15", "valsora_deco_option_14", "valsora_deco_heading_22"
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
    "EventWindow_News>midsection>Description": LE.NEWS_TEXT_FONT,
    "event_option_entry>Name": OPTION,
}

ARG = sys.argv[1] if len(sys.argv) > 1 else VANILLA_DIR
t = open(os.path.join(ARG, "interface", "eventwindow.gui"), encoding="utf-8-sig").read().replace("\r\n", "\n")
for path, font in FONTS.items():
    t = GP.set_attrs(t, path, font=font)
# the options: the entry as wide as its plate, the text centred on it, each window's grid centred in its room
W, PAD = LE.OPTION_W, LE.OPTION_PAD
t = GP.set_attrs(t, "event_option_entry", size=(W, 47))
t = GP.set_attrs(t, "event_option_entry>Name", position=(PAD, LE.OPTION_TEXT_Y), maxWidth=W - 2 * PAD,
                 maxHeight=LE.OPTION_TEXT_H)
for win in LE.CENTRES:
    x, y = GP.get_pos(t, f"{win}/options_grid")
    t = GP.set_attrs(t, f"{win}/options_grid", position=(LE.grid_x(win), y), size=(W, 30 if win in ("EventWindow", "EventWindow_News") else 0),
                     slotsize=(W, 47))
# the news page centred on its middle, as its masthead is (v0.8.1): the picture and its overlay, the headline, the story
for el in ("event_picture", "event_picture_overlay"):
    x, y = GP.get_pos(t, f"EventWindow_News>top_Window>{el}")
    t = GP.set_attrs(t, f"EventWindow_News>top_Window>{el}", position=(LE.NEWS_PIC_X, y))
x, y = GP.get_pos(t, "EventWindow_News>top_Window>Title")
t = GP.set_attrs(t, "EventWindow_News>top_Window>Title", position=(LE.NEWS_TITLE_X, y), maxWidth=LE.NEWS_TITLE_W)
x, y = GP.get_pos(t, "EventWindow_News>midsection>Description")
assert LE.NEWS_MID_Y + y == LE.NEWS_STORY_Y, ("the news story moved", y)
t = GP.set_attrs(t, "EventWindow_News>midsection>Description", position=(LE.NEWS_TEXT_X, y), maxWidth=LE.NEWS_TEXT_W)
# the text boxes' height (layout_events.TEXT_LINES, lines of the body font)
for win, n in LE.TEXT_LINES.items():
    t = GP.set_attrs(t, f"{win}>midsection>Description", maxHeight=n * 16)
GP.write_gui(MOD + "interface/eventwindow.gui", t)
print("eventwindow.gui written")
