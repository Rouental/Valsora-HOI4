"""Layout of the politics screen (interface/countrypoliticsview.gui), v0.4.8.

Panel-local pixels. The vanilla panel is 550 wide and slides in to x = -6 (so x < 6 is off-screen).
Since v0.4.8 its top is flush with the bottom of the top bar band (TOP), and the panel leaves a notch
the shape of the top bar's flag medallion and decisions seal, which show through it: side panels are
drawn over the top bar (in game, v0.4.7: the panel hid the medallion's name plate and the seal).
Top to bottom:

  header         "Government" label, the country's full name (scripted GUI), close diamond, rules icon,
                 right of the notch
  head of state  arched portrait over a sunburst, "Head of State" ribbon; right: name, ideology chip,
                 a grid (ruling party, elections, last election, political power, sub-ideology)
  popularity     pie in a gilt ring with the party legend | national spirits
  faction | focus  faction card and national focus card side by side (the focus card opens the tree)
  buttons        occupied territories / exiles / subjects, compact
  ideas          the game's advisors & laws list (scrolls), from IDEAS_Y to the bottom of the screen

v0.4.8 (author's screenshots, 2026-10-14): the leader's description is only in the portrait's tooltip
(the game's), the law cards are gone (the laws are in the list below), the sub-ideology took their place
in the grid, the spirits moved up beside the popularity, and the list starts 156 px higher on screen.

The panel keeps vanilla's 550 px width (the mockup's is 604) so the sub-windows that open beside it
(advisor picker, subjects, exiles, occupied territories) keep their positions.
"""
import layout as L

PANEL_W = 550
X0, X1 = 18, 532                                   # content edges
PANEL_X = -6                                       # vanilla's shown x (the first 6 px are off-screen)
TOP = 62                                           # screen y of the panel's top: the band ends at 62 (layout.BAND_H)
# How a panel opens (v0.5.2). `position` is where a closed window rests and `show_position` where it opens. The
# game does not hide a closed side panel: it moves it back to `position`, which is off-screen in vanilla (x -606),
# and leaves it there. Vanilla's dropdowns rest at y -300 or -2000, or inside a clipped parent. v0.5.1 rested the
# panels 36 px below their place, on screen, to make them rise into place; a closed panel then stayed drawn there
# (the author's screenshot of 2026-10-15: a closed division overview under the open map). Sliding in from the
# left crosses the flag and the country's name (their video of 2026-10-14), so a panel now rests at vanilla's
# off-screen position and opens and closes at once (OPEN_MS 0, as vanilla's dropdowns do).
OPEN_MS = 0


def closed_x(head):
    """where a closed window rests (`head`: the window's own attributes in the game's file): the game's `position`
    when that is off-screen (x -606 for a side panel), else just off the left edge (the ships and planes windows
    rest at x 100, behind the division overview), so that nothing is left on screen"""
    import re
    x = int(re.search(r"(?<!show_)position\s*=\s*\{\s*x\s*=\s*(-?\d+)", head).group(1))
    w = re.search(r"size\s*=\s*\{\s*width\s*=\s*(\d+)\s*height", head)
    w = int(w.group(1)) if w else 2000
    return x if x + w <= 0 else -(w + 56)


def local(sx, sy):
    """screen pixels -> panel pixels"""
    return sx - PANEL_X, sy - TOP


# ---------------------------------------------------------------- the notch: the top bar's flag medallion
# (its plate steps in twice; gen_textures draws it from the same numbers) and the decisions seal hanging
# under it (an octagon), in panel pixels. The panel draws nothing inside it, so the medallion and seal show.
# The panel overlaps their outermost pixel (NOTCH_OVERLAP) and draws its own gilt edge there, so no map
# shows between them. The decision counters sit on the plate's lower step either side of the seal
# (layout.DEC_BADGES), inside the notch.
NOTCH_OVERLAP = 1
SEAL_CUT = 12                                      # the seal's corner cut (gen_textures: oct_(S_, 12))


def _notch_poly_screen():
    W, H = L.MED["w"], L.MED["h"]
    s1, s2 = L.MED_STEPS
    mx, my = L.MED["x"], L.MED["y"]
    sx, sy, ss, c = L.SEAL["x"], L.SEAL["y"], L.SEAL["w"], SEAL_CUT
    bl, br = mx + 0.26 * W, mx + 0.74 * W          # the plate's bottom edge
    assert bl <= sx and sx + ss <= br and sy + ss - c > my + H, "the seal no longer hangs under the plate's bottom"
    pts = [(mx, my - 40), (mx + W, my - 40), (mx + W, my + s1), (mx + 0.88 * W, my + s1), (mx + 0.88 * W, my + s2),
           (br, my + s2), (br, my + H),
           (sx + ss, my + H), (sx + ss, sy + ss - c), (sx + ss - c, sy + ss), (sx + c, sy + ss), (sx, sy + ss - c),
           (sx, my + H),
           (bl, my + H), (bl, my + s2), (mx + 0.12 * W, my + s2), (mx + 0.12 * W, my + s1), (mx, my + s1)]
    return pts


def offset_poly(points, d):
    """The polygon with every edge moved d px outwards (d < 0: inwards); points are clockwise on screen."""
    import math
    n = len(points)
    out_lines = []
    for i in range(n):
        (x1, y1), (x2, y2) = points[i], points[(i + 1) % n]
        dx, dy = x2 - x1, y2 - y1
        ln = math.hypot(dx, dy)
        nx, ny = dy / ln, -dx / ln                 # outward normal of a clockwise (y down) polygon
        out_lines.append(((x1 + nx * d, y1 + ny * d), (dx, dy)))
    out = []
    for i in range(n):
        (p1, d1), (p2, d2) = out_lines[i - 1], out_lines[i]
        den = d1[0] * d2[1] - d1[1] * d2[0]
        if abs(den) < 1e-9:
            out.append(p2)
            continue
        tt = ((p2[0] - p1[0]) * d2[1] - (p2[1] - p1[1]) * d2[0]) / den
        out.append((round(p1[0] + d1[0] * tt, 3), round(p1[1] + d1[1] * tt, 3)))
    return out


NOTCH_POLY = offset_poly([local(x, y) for x, y in _notch_poly_screen()], -NOTCH_OVERLAP)


def notch_outline(d):
    """The notch's outline moved d px out into the panel (closed polygon, clockwise)."""
    return offset_poly(NOTCH_POLY, d)


# for clicks: the notch as bands of rows (y0, y1, x0, x1), each covering the polygon in that band
def bands(poly=None):
    poly = NOTCH_POLY if poly is None else poly
    ys = sorted({max(0.0, y) for _, y in poly})
    out = []
    for ya, yb in zip(ys, ys[1:]):
        xs = []
        for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
            lo, hi = min(y1, y2), max(y1, y2)
            if hi <= ya or lo >= yb:
                continue
            for yy in (max(lo, ya), min(hi, yb)):
                xs.append(x1 + (x2 - x1) * ((yy - y1) / (y2 - y1)) if y2 != y1 else x1)
                xs.append(x2 if y2 == y1 else xs[-1])
        if xs:
            out.append((int(ya), int(-(-yb // 1)), int(min(xs)), int(-(-max(xs) // 1))))
    return out


NOTCH = [(x0, y0, x1, y1) for y0, y1, x0, x1 in bands()]
NOTCH_BOTTOM = max(r[3] for r in NOTCH)            # 106: the header strip above it is drawn by pol_view_bg
HEAD_ART_H = 344                                   # vanilla's pol_view_bg(_no_dlc).dds are 550x344


def blockers():
    """Rectangles covering the header strip (0..NOTCH_BOTTOM) outside the notch: invisible containers
    there catch the clicks the panel's (click-through) background no longer does."""
    out = []
    for x0, y0, x1, y1 in NOTCH:
        if x0 > 0:
            out.append((0, y0, x0, y1))
        if x1 < PANEL_W:
            out.append((x1, y0, PANEL_W, y1))
    return out


# ---------------------------------------------------------------- header (right of the notch)
HX = 190                                           # right of the notch (its widest: x < 177)
HEAD_LABEL = dict(x=HX, y=16, w=260, h=12)         # "Government" (vanilla political_title, re-texted)
HEAD_TITLE = dict(x=HX, y=30, w=292, h=46)         # scripted GUI: [ROOT.GetNameDefCap], 1-2 lines
CLOSE = dict(x=-52, y=14, w=34, h=34)              # UPPER_RIGHT
RULES = (506, 56)
HEAD_RULE_Y = 88                                   # under the title, right of the notch
HEAD_GLOW_H = 90                                   # jade wash at the top of the panel (mockup header)

# ---------------------------------------------------------------- head of state
PORTRAIT = dict(x=24, y=NOTCH_BOTTOM + 16, w=156, h=210)   # its frame clears the seal by 8 px
FRAME = dict(x=PORTRAIT["x"] - 8, y=PORTRAIT["y"] - 8, w=PORTRAIT["w"] + 16, h=PORTRAIT["h"] + 16)
SUNBURST = dict(cx=PORTRAIT["x"] + 78, cy=PORTRAIT["y"] + 92, r=118)
RIBBON = dict(x=PORTRAIT["x"] + 14, y=PORTRAIT["y"] + PORTRAIT["h"] - 10, w=128, h=22)
HERO_BOTTOM = FRAME["y"] + FRAME["h"]              # 340
RX = 198                                           # right column
LEADER_NAME = dict(x=RX, y=98, w=X1 - RX, h=30)    # Federo 24, one line (the longest Valsora name fits)
CHIP = dict(x=RX, y=134, w=250, h=24)              # ideology chip: the game's ideology icon + text
CHIP_ICON = dict(x=RX + 5, y=136, scale=0.34)
CHIP_TEXT = dict(x=RX + 30, y=139, w=214, h=14)
GRID_X = (RX, 368)
GRID_W = (160, X1 - 368)
GRID_LABEL_Y = (172, 230, 288)
GRID_VALUE_Y = (186, 244, 302)
GRID_VALUE_H = 34                                  # two lines
# cells: 0 ruling party (scripted) | 1 elections (the game's text) | 2 last election (scripted) |
# 3 political power (scripted) | 4 sub-ideology, the row's full width (scripted; its description is the tooltip)
SUB_IDEOLOGY = dict(x=RX, y=GRID_VALUE_Y[2], w=X1 - RX, h=18)

# ---------------------------------------------------------------- popularity | national spirits
SEC1_Y = HERO_BOTTOM + 14                          # section labels (354)
POP_X, POP_W = X0, 242
PIE = dict(cx=X0 + 44, top=SEC1_Y + 22, r=44)      # the game's pie: drawn centred on x, top at y
PIE_RING = 4                                       # ring drawn this much outside the pie
LEGEND = dict(x=X0 + 100, y=SEC1_Y + 18, w=142, row=19)
BOP = dict(x=X0 + 100, y=SEC1_Y + 18 + 5 * 19 + 6) # balance of power (only some countries; Valsora has none)
SPIRITS_X = 272
SPIRITS_LABEL_Y = SEC1_Y
SPIRITS = dict(x=SPIRITS_X, y=SEC1_Y + 18, w=X1 - SPIRITS_X, h=140)
SPIRIT_SLOT = (59, 68)                             # vanilla's large slot: 4 a row
SPIRIT_ROWS = 2                                    # rows of large spirits
SPIRIT_SMALL = (33, 34)                            # vanilla's slot once there are more spirits than large slots: 7 a row

# ---------------------------------------------------------------- faction | national focus
SEC3_Y = SPIRITS["y"] + SPIRITS["h"] + 12          # 524
FACTION_CARD = dict(x=X0, y=SEC3_Y + 16, w=240, h=78)
FACTION_NAME_Y = 33                                # the name's centre (the game centres it on its position's y)
# v0.9: the members' flags under the name, as the Government mockup has them (a scripted GUI's list over the game's
# faction_members; each flag is the text icon [This.GetFlag], whose size in game is (assumed) about 20 x 13)
FACTION_MEMBERS = dict(x=54, y=56, slot=(22, 16), n=8)
FOCUS_CARD = dict(x=266, y=SEC3_Y + 16, w=X1 - 266, h=78)
FOCUS_ICON = dict(cx=38, cy=39, scale=0.62)        # the focus picture, centred on the card's medallion
FOCUS_TITLE = dict(x=76, y=8, w=158, h=36)
FOCUS_BAR = dict(x=76, y=52, w=176, h=4)
FOCUS_COST = dict(x=76, y=60)

# ---------------------------------------------------------------- management buttons
BUTTONS_Y = FACTION_CARD["y"] + FACTION_CARD["h"] + 12   # 630
BUTTON = dict(w=164, h=26)
BUTTON_X = [X0, X0 + 175, X0 + 350]
STRIP = dict(x=6, y=BUTTONS_Y - 6, w=PANEL_W - 12, h=38)

# ---------------------------------------------------------------- advisors and laws (the game's list)
IDEAS_Y = BUTTONS_Y + 36                           # 666 (806 until v0.4.7, with the panel 16 px lower)
CAT_HEADER = dict(x=-5, y=4, w=X1 - X0 + 6, h=30)
IDEA_SLOT = 53

# section labels drawn by the mod (rules after them are part of the section art)
SECTION_LABELS = {  # key: (x, y, English text)
    "popularity": (POP_X, SEC1_Y, "Popularity"),
    "spirits": (SPIRITS_X, SPIRITS_LABEL_Y, "National Spirits"),   # the game's own label, restyled
    "faction": (FACTION_CARD["x"], SEC3_Y, "Faction"),
    "focus": (FOCUS_CARD["x"], SEC3_Y, "National Focus"),
}
SECTION_ENDS = {"popularity": POP_X + POP_W, "spirits": X1,
                "faction": FACTION_CARD["x"] + FACTION_CARD["w"], "focus": X1}
