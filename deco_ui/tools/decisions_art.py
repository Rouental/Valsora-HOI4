"""The decisions panel's own pictures (countrydecisionview.gui) at the game's paths and sizes (v0.11, 2026-10-18, the
author: "Stylize the decisions tab as well", with a screenshot of it: the events box's torn paper and paper clip, the
category's riveted header with its metal socket, the green rows, the round status lights, the copper fold button).

- the events box (515 x 83): a lacquer plate, the title's tab at its left with a gilt diamond where the clip was; the
  game's title and event rows were typewriter ink on paper, so make_panels gives them the Deco UI's light faces
  (layout_panels.DECISION_FONTS);
- the category header (516 x 53): a lacquer bar, a round gilt socket for the category's medallion (the game's at
  (10, 16), 40 px), a dark well for its name (the game's box from x 74, 365 wide, centred);
- a decision's row (3 frames of 512 x 40: unavailable, available, under way): grey, jade, steel lacquer, the icon's
  well at its left;
- an event's row (512 x 33), the status lights (2 and 3 frames of 23 x 23: off, on, locked) as diamonds, the events'
  checkboxes (2 frames of 28 x 23), the fold button (2 frames of 24 x 25: up, down), the description's tile (48 x 48).
Left as the game's: the timer and event-type strips (icons: no icon of the game's changes without the author's yes); the
"take" envelopes are icons_art.py's since 2026-10-19 (the author's approval of the icon proposals).

gen_textures.py adds them (keys dc_*).
"""
from art_util import BAR_FILL, DIM_FILL, LIT_FILL, bar, frames

G = "gfx/interface/"
D = G + "decisionview/"
LINE = "rgba(201,165,90,.45)"
DEFS = ('<linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F1DC9C"/>'
        '<stop offset="1" stop-color="#8B6A2C"/></linearGradient>')
STEEL_FILL = "linear-gradient(180deg,#243A4A,#13212B)"


def svg(w, h, body):
    return f'<svg width="{w}" height="{h}" style="position:absolute;left:0;top:0"><defs>{DEFS}</defs>{body}</svg>'


def cham(x0, y0, x1, y1, c):
    return f"M{x0 + c},{y0}L{x1 - c},{y0}L{x1},{y0 + c}L{x1},{y1 - c}L{x1 - c},{y1}L{x0 + c},{y1}L{x0},{y1 - c}L{x0},{y0 + c}Z"


def well(x0, y0, x1, y1, c=4, fill="#0A0F12", rim=LINE):
    return f'<path d="{cham(x0, y0, x1, y1, c)}" fill="{fill}" stroke="{rim}"/>'


def diamond(cx, cy, r, fill="#C9A55A"):
    return f'<path d="M{cx},{cy - r}L{cx + r},{cy}L{cx},{cy + r}L{cx - r},{cy}Z" fill="{fill}"/>'


# the category header (drawn at the header's (-4, 8)): the medallion's socket round its ink (the game's 51 x 40 icon
# at the header's (10, 16), its ink 4 to 48 across: centred at the picture's (40, 28)), the name's well round the
# game's box (the header's x 74, 365 wide, y 26), short of the light and the fold button at its x 447 and 475
CAT = dict(w=516, h=53, socket=(40, 28, 21), well=(72, 14, 446, 44))


def category_header():
    cx, cy, r = CAT["socket"]
    x0, y0, x1, y1 = CAT["well"]
    return (bar(c=7) + svg(CAT["w"], CAT["h"],
                           well(x0, y0, x1, y1, 5) + diamond(x0 - 6, (y0 + y1) / 2, 3)
                           + f'<circle cx="{cx}" cy="{cy}" r="{r + 2}" fill="#0A0F12" stroke="url(#g)" stroke-width="1.6"/>'
                           + f'<circle cx="{cx}" cy="{cy}" r="{r - 1}" fill="none" stroke="{LINE}"/>'))


# the events box: the title at (35, 29) on the tab, the popup checkboxes from x 182 (their windows at the right of a
# 3 px box: 190 + 3 - 11), y 28 and 51
EV = dict(w=515, h=83, tab=(4, 16, 174, 58))


def event_header():
    x0, y0, x1, y1 = EV["tab"]
    return (f'<div style="position:absolute;left:0;top:6px;width:{EV["w"]}px;height:{EV["h"] - 6}px">{bar(c=8)}</div>'
            + svg(EV["w"], EV["h"],
                  f'<path d="M{x0},{y0}H{x1 - 10}L{x1},{y0 + 10}V{y1}H{x0}Z" fill="#1E2A30" stroke="url(#g)"/>'
                  + f'<line x1="{x0 + 4}" y1="{y0 + 3}" x2="{x1 - 14}" y2="{y0 + 3}" stroke="rgba(241,220,156,.2)"/>'
                  + diamond(x0 + 14, (y0 + y1) / 2, 5, "#E3C77E")
                  + well(x1 + 4, 14, EV["w"] - 8, EV["h"] - 8, 5, "rgba(10,15,18,.7)")))


# the icon's well in a row, centred on the icon the game draws there (2026-10-19, the author: "Icons on the events &
# decisions are out of alignment with their boxes"; v0.11's wells started at x 5): a decision's icon is centred at the
# row's (30, 19) (countrydecisionview.gui: decision_item>icon, centerposition, the game's 50 px icons with their ink in
# about 38), an event's type icon (30 x 26) at the picture's x 16 to 46, y 3 to 29 (event_item>event_type_icon at
# (15, 3), the picture at x -1)
DECISION_WELL = (11, 1, 49, 38)
EVENT_WELL = (13, 2, 49, 31)


def row(fill, w, h, box):
    return bar(fill, c=5) + svg(w, h, well(*box, 4))


def light(state):
    """a status light as a diamond in a dark socket: off, on (jade, lit), locked (grey with a bar)"""
    socket = diamond(11.5, 11.5, 9, "#0A0F12") + (f'<path d="M11.5,2.5L20.5,11.5L11.5,20.5L2.5,11.5Z" fill="none" '
                                                   'stroke="url(#g)" stroke-width="1.2"/>')
    if state == "on":
        socket += diamond(11.5, 11.5, 5.5, "#3FA88E") + diamond(10.5, 9.5, 1.8, "rgba(255,255,255,.55)")
    elif state == "locked":
        socket += diamond(11.5, 11.5, 5.5, "#4A5358") + '<rect x="8" y="10.5" width="7" height="2" fill="#E3C77E"/>'
    return svg(23, 23, socket)


def checkbox(checked):
    body = well(2, 2, 26, 21, 3, "#0A0F12", "url(#g)")
    if checked:
        body += '<path d="M8,11.5l4,4 8,-8" fill="none" stroke="#E3C77E" stroke-width="2" stroke-linecap="round"/>'
    return svg(28, 23, body)


def fold(up):
    path = "M7,15l5,-5 5,5" if up else "M7,10l5,5 5,-5"
    return bar(c=4) + svg(24, 25, f'<path d="{path}" fill="none" stroke="#E3C77E" stroke-width="1.8" stroke-linecap="round"/>')


ADDS = [
    ("dc_category_header", D + "category_header_bg.dds", 516, 53, category_header),
    ("dc_event_header", D + "event_header_bg.dds", 515, 83, event_header),
    ("dc_decision_item", D + "decision_item_bg.dds", 1536, 40,
     lambda: frames(1536, 40, *(row(f, 512, 40, DECISION_WELL) for f in (DIM_FILL, LIT_FILL, STEEL_FILL)))),
    ("dc_event_item", D + "event_item_bg.dds", 512, 33, lambda: row(BAR_FILL, 512, 33, EVENT_WELL)),
    ("dc_light2", D + "checkbox_small4.dds", 46, 23, lambda: frames(46, 23, light("off"), light("on"))),
    ("dc_light3", D + "checkbox_small5.dds", 69, 23, lambda: frames(69, 23, light("off"), light("on"), light("locked"))),
    ("dc_checkbox", G + "generic_checkbox3.dds", 56, 23, lambda: frames(56, 23, checkbox(False), checkbox(True))),
    ("dc_fold", G + "collapse_conveyor_btn.dds", 48, 25, lambda: frames(48, 25, fold(True), fold(False))),
    ("dc_tile", G + "tiles/tiled_decisions_bg_small.dds", 48, 48,
     lambda: svg(48, 48, well(.5, .5, 47.5, 47.5, 4, "#0B1014", "url(#g)") + well(4.5, 4.5, 43.5, 43.5, 2, "none"))),
]
