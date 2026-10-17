"""Game setup: the country and start selection screens (frontendgamesetupview.gui) at the game's paths and sizes
(2026-10-17, SCREEN_INVENTORY.md's suggestion 7). Textures only: the game's .gui and .gfx stay as they are.

The game draws the screen on a few large pictures and puts its own texts, portraits, flags, lists and buttons on them,
so every panel here lies where the game's does (measured from its own pictures, numbers below), and only the look
changes: lacquer bodies with a gilt rim, a title tab chamfered at 45 degrees, recessed wells where the game puts its
cards, lists, portraits and icons, raised bands under its light text, and an ivory ruled sheet wherever it writes in
the typewriter fonts, which the game colours black (`core.gfx`: hoi4_typewriter16/22 are 0xff000000).

- The country selection (`country_selection_bg`, 1225 x 728; the window 1225 x 717): the title tab (the game's
  "Select Country" at (435, 12)), the well behind the major countries' cards (y 41-315: cards 150 apart from x 15),
  the band behind the filter buttons (y 321-354), the well behind the minor and mini lists (y 352-440), and below a
  double rule three panels: the country's facts on an ivory sheet ruled as the game's (title at y 462, rules under it
  at 487 and between the five facts at 527, 568, 608, 648; the portrait pinned at its right), the name, faction, spirits
  and focuses in lacquer wells (the name at (442, 433), the faction emblem at (451, 487), the spirits at (542, 486),
  the focuses at (477, 580)), the Back and Select buttons under them (y 675-709), and the history on a second sheet
  (title at (830, 462), text from (810, 502)).
- The start's window (`select_date_bg`, 579 x 512): the title tab, the well behind the two start cards (y 55-266),
  the band under "Brief History" (y 274), the sheet under the start's name and description (typewriter, y 305 and 330), the
  band under Back and Select (y 455-489).
- The country's details (`lobby_right_sidepanel_bg`, 492 x 301, at the screen's upper right on the map): wells for
  the portrait (its frame at (27, 15)), the faction emblem (105, 30), the pie (centre about (207, 63)) and the spirits
  (253, 28), and the recess under the five facts (light text, y 143-259).
- The pieces the game lays on them: the major country card (`country_selection_entry`, 150 x 274 a frame: an arched
  opening over the portrait at (17, 22), 117 x 157, the flag's at (34, 188), 82 x 52, the name plate at y 247), the
  minor and mini cards (the flag at (26, 22) and (9, 8)), the filter buttons, the start card (`bookmark_entry_bg`: the
  start's picture at (27, 28), 180 x 104, the date at y 147), the portrait's photo corners (`minor_portrait_overlay`:
  the game turns that portrait by -0.04, so the corners are drawn on the turned photo, where the game's own border is),
  and the small pie's ring and glass.
- The map's lobby around them: the setup's top and bottom bars (cornered tiles stretched across the screen), the
  scenario plate hanging from the top bar (the date and the start's name, Change Scenario), the two map mode medallions
  under it (the countries: a flag; the players: people), the details' toggle (chevrons down, then up), the difficulty
  panel (a band under "Difficulty" and the custom rules button, the five difficulty buttons with rank marks in line
  art: a civilian, one to three chevrons, a star; a row each for Ironman and Historical AI focuses), the multiplayer
  settings (co-op, hot join), and Start (a jade plaque with pointed ends; Ready the same; the raids view's "create"
  button uses the Start picture too) with the core skin's checkbox for Ready.

Each two-frame picture keeps the game's order: frame 1 normal, frame 2 selected (the game's lighter one), except the
filter buttons, whose lit frame is the first (the game's green-striped one; the .gui starts them at frame 2), the map
modes (a strip per state, the countries then the players), the toggle (down, up) and Start (normal, hover, pressed).

Left the game's, because other screens share them: the flag's frame and the name plate in the top bar (large_flag_frame,
generic_bg: the politics screen, the popups, the division designer), the portrait frame on the details
(naval_unit_leader_frame: the navy's screen), the more-countries arrow (peace_drop_down_button: the peace conference),
the faction emblems (pol_factions_strip: the ideologies' own art) and the achievements badge (enabled_achievement_icons).

gen_textures.py adds them (keys gs_*); preview_setup.py draws the screens (build/preview_setup.png, + _vanilla.png).
"""
import math

from designer_art import LAC, GILT, _layer, _rect, _shrink, band, inset, gilt_line, sheet
from art_util import bar, frames, lit_bar
from icons import icon as _icon  # noqa: F401  (the line icons, for the lobby's buttons)

LAC_FILL = f"{LAC},linear-gradient(180deg,#141E24,#0D1418)"
WELL = "linear-gradient(180deg,#0B1115,#080C0F)"
JADE_LINE = "#6CC2A9"


# ---------------------------------------------------------------- shared pieces
def cham_pts(x0, y0, x1, y1, c):
    return [(x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c), (x1 - c, y1), (x0 + c, y1), (x0, y1 - c), (x0, y0 + c)]


def body(pts):
    """a window's body: a dark outer line, the gilt rim, lacquer, and a fainter gilt rule 5 px inside, following the
    outline (title tab included)"""
    return (_layer(pts, "rgba(0,0,0,.75)") + _layer(_shrink(pts, 1), "#B8954F") + _layer(_shrink(pts, 2), LAC_FILL)
            + _layer(_shrink(pts, 5), "rgba(201,165,90,.4)") + _layer(_shrink(pts, 6), LAC_FILL))


def tab_body(w, h, tab, top=3, base=35):
    """the outline of a window with a title tab: the body from y base down to 3 px above the picture's foot, 3 px in
    from its sides (as the game's), the tab's top edge from tab[0] to tab[1] at y top, its sides at 45 degrees"""
    t0, t1 = tab
    d = base - top
    return [(3, base), (t0 - d, base), (t0, top), (t1, top), (t1 + d, base), (w - 3, base), (w - 3, h - 3), (3, h - 3)]


def ck(x, y, sx=1, sy=1, small=False):
    """a double gilt corner bracket with its corner at (x, y); sx, sy = -1 turn it to face left or up"""
    s = 10 if small else 16
    return (f'<i class="ck{" sm" if small else ""}" style="left:{x - (s if sx < 0 else 0)}px;top:{y - (s if sy < 0 else 0)}px;'
            f'transform:scale({sx},{sy})"></i>')


def brackets(x0, y0, x1, y1, small=False):
    return ck(x0, y0, 1, 1, small) + ck(x1, y0, -1, 1, small) + ck(x0, y1, 1, -1, small) + ck(x1, y1, -1, -1, small)


def diamond(cx, cy, s, color="#E3C77E"):
    return (f'<div style="position:absolute;left:{cx - s / 2}px;top:{cy - s / 2}px;width:{s}px;height:{s}px;'
            f'background:{color};transform:rotate(45deg)"></div>')


def rule_diamond(x0, x1, y, s=6):
    """a gilt hairline from x0 to x1 that fades to both ends, with a diamond in its middle"""
    cx = (x0 + x1) / 2
    return (f'<div style="position:absolute;left:{x0}px;top:{y}px;width:{cx - x0 - s}px;height:1px;'
            'background:linear-gradient(90deg,rgba(201,165,90,0),#C9A55A)"></div>'
            f'<div style="position:absolute;left:{cx + s}px;top:{y}px;width:{x1 - cx - s}px;height:1px;'
            'background:linear-gradient(90deg,#C9A55A,rgba(201,165,90,0))"></div>'
            + diamond(cx, y + .5, s))


def rays(x0, y0, x1, y1, cx, cy, alpha=.045, reach=70):
    """faint gilt rays from (cx, cy) inside a box (the main menu's sunburst, quieter), fading out by reach %"""
    return (f'<div style="position:absolute;left:{x0}px;top:{y0}px;width:{x1 - x0}px;height:{y1 - y0}px;'
            f'background:repeating-conic-gradient(from 0deg at {cx - x0}px {cy - y0}px,rgba(227,199,126,{alpha}) 0deg 2.2deg,'
            f'transparent 2.2deg 9deg);-webkit-mask:radial-gradient(ellipse at {cx - x0}px {cy - y0}px,#000 0%,'
            f'rgba(0,0,0,.55) {reach * .45:.0f}%,transparent {reach}%)"></div>')


def glow(x0, y0, x1, y1, cx, cy, alpha=.10):
    return (f'<div style="position:absolute;left:{x0}px;top:{y0}px;width:{x1 - x0}px;height:{y1 - y0}px;'
            f'background:radial-gradient(ellipse at {cx - x0}px {cy - y0}px,rgba(201,165,90,{alpha}),rgba(201,165,90,0) 65%)"></div>')


def paper(x0, y0, x1, y1, head, rows=()):
    """an ivory sheet for the game's typewriter text, in a recessed lacquer frame with small gilt brackets"""
    return (inset((x0 - 7, y0 - 7, x1 + 7, y1 + 7), "linear-gradient(180deg,#0A0F12,#070A0C)", "rgba(201,165,90,.7)")
            + sheet(x0, y0, x1, y1, head, [], list(rows))
            + brackets(x0 - 5, y0 - 5, x1 + 5, y1 + 5, small=True))


def double_rule(x0, x1, y):
    return gilt_line(x0, y, x1, y, GILT) + gilt_line(x0, y + 2, x1, y + 2, "rgba(201,165,90,.4)")


def title_marks(cx, cy, half):
    """two small diamonds either side of a title box, with a short hairline running out to each"""
    out = ""
    for sx in (-1, 1):
        x = cx + sx * half
        out += diamond(x, cy, 5)
        a, b = (x - 16, x - 5) if sx < 0 else (x + 5, x + 16)
        grad = "90deg,rgba(201,165,90,0),#C9A55A" if sx < 0 else "90deg,#C9A55A,rgba(201,165,90,0)"
        out += f'<div style="position:absolute;left:{a}px;top:{cy}px;width:{b - a}px;height:1px;background:linear-gradient({grad})"></div>'
    return out


# ---------------------------------------------------------------- the country selection (1225 x 728)
CS_W, CS_H = 1225, 728
CS_TAB = (409, 815)                 # the tab's top edge (the game's: 411-813 at y 4, 377-847 where it meets the body)
CS_CARDS = (14, 44, 1211, 316)      # the major countries' cards: 150 apart from x 15, their frames y 51-314
CS_FILTERS = (8, 318, 1217, 356)    # the filter buttons, 33 tall at y 321
CS_LISTS = (14, 359, 1211, 441)     # the minor cards (y 361-440) and the mini flags (two rows from y 360)
CS_SPLIT = 444                      # the double rule over the lower panels
CS_INFO = (32, 457, 418, 703)       # the facts' sheet: the game's parchment 33-420 x 455-703
CS_HIST = (807, 457, 1193, 703)     # the history's sheet: the game's 808-1195 x 455-703
CS_HEAD = 487                       # the game's red rule under both sheets' titles
CS_ROWS = (527, 568, 608, 648)      # its dotted rules between the five facts


def country_bg(w=CS_W, h=CS_H):
    out = body(tab_body(w, h, CS_TAB, 3, 35))
    # the tab: a raised plate under the game's title (hoi_24header, light), marks either side of its 340 px box
    out += _layer(_shrink([(377, 36), (409, 4), (815, 4), (847, 36)], 7), "linear-gradient(180deg,#1C2830,#141D23)")
    out += title_marks(612, 21, 186)
    # the cards' well, quiet rays from the filter band's middle
    x0, y0, x1, y1 = CS_CARDS
    out += (inset(CS_CARDS, "linear-gradient(180deg,#0C1216,#080C0F)") + glow(x0 + 1, y0 + 1, x1 - 1, y1 - 1, 612, y1, .09)
            + rays(x0 + 1, y0 + 1, x1 - 1, y1 - 1, 612, y1 + 40, .04, 80))
    # the filter band, the lists' well
    fx0, fy0, fx1, fy1 = CS_FILTERS
    out += (band(fx0, fy0, fx1, fy1) + gilt_line(fx0, fy0, fx1, fy0, "rgba(201,165,90,.75)")
            + gilt_line(fx0, fy1 - 1, fx1, fy1 - 1, "rgba(201,165,90,.5)") + diamond(fx0 + 7, (fy0 + fy1) / 2, 6)
            + diamond(fx1 - 7, (fy0 + fy1) / 2, 6))
    out += inset(CS_LISTS, "linear-gradient(180deg,#0C1216,#090D10)")
    out += double_rule(8, w - 8, CS_SPLIT)
    # the facts and the history on ivory (the game writes them in black typewriter)
    out += paper(*CS_INFO, CS_HEAD, CS_ROWS) + paper(*CS_HIST, CS_HEAD)
    # the middle: the name over a hairline, the faction emblem in an octagonal well, the spirits' and focuses' wells
    out += rule_diamond(446, 779, 478)
    out += inset(cham_pts(445, 483, 523, 561, 13), "linear-gradient(180deg,#0E151A,#080C0F)", "rgba(201,165,90,.75)")
    out += inset((533, 483, 781, 559)) + inset((445, 568, 781, 668))
    return out + brackets(5, 37, w - 5, h - 5)


# ---------------------------------------------------------------- the start's window (579 x 512)
SD_W, SD_H = 579, 512
SD_TAB = (88, 490)                  # the game's tab: 88-490 at y 4, 58-520 where it meets the body at y 34


def date_bg(w=SD_W, h=SD_H):
    out = body(tab_body(w, h, SD_TAB, 4, 34))
    out += _layer(_shrink([(58, 35), (88, 5), (490, 5), (520, 35)], 7), "linear-gradient(180deg,#1C2830,#141D23)")
    out += title_marks(290, 23, 182)
    # the start cards' well (two cards, 232 wide, from x 43 and 303, y 55-266)
    out += (inset((14, 44, 565, 265), "linear-gradient(180deg,#0C1216,#080C0F)") + glow(15, 45, 564, 264, 289, 264, .09)
            + rays(15, 45, 564, 264, 289, 300, .04, 85))
    # "History" (hoi_20b, light) on a band; the start's name and description (typewriter, black) on the sheet
    out += band(8, 268, w - 8, 295) + gilt_line(8, 268, w - 8, 268, "rgba(201,165,90,.75)") + diamond(16, 281.5, 6) + diamond(w - 16, 281.5, 6)
    out += paper(19, 303, 560, 442, 331)
    # Back and Select (y 455-489)
    out += band(8, 452, w - 8, 501) + gilt_line(8, 452, w - 8, 452, "rgba(201,165,90,.75)") + rule_diamond(255, 324, 472, 5)
    return out + brackets(5, 36, w - 5, h - 5)


# ---------------------------------------------------------------- the country's details (492 x 301)
def details_bg(w=492, h=301):
    out = body(_rect(3, 0, 477, 297))
    out += band(7, 6, 473, 119)
    # the portrait (the game's frame at (27, 15), 69 x 95), the faction emblem (66 x 68 at (105, 30)), the pie's well,
    # the spirits (from (253, 28): three large or two rows of six small)
    out += inset((23, 11, 100, 114), "linear-gradient(180deg,#0A0F12,#06090B)")
    out += inset(cham_pts(101, 27, 176, 102, 14), "linear-gradient(180deg,#0E151A,#080C0F)", "rgba(201,165,90,.75)")
    out += ('<div style="position:absolute;left:171.5px;top:27px;width:72px;height:72px;border-radius:50%;'
            'background:radial-gradient(circle,#080C0F 60%,#101820);box-shadow:0 0 0 1px rgba(201,165,90,.45)"></div>')
    out += inset((248, 20, 470, 106))
    out += double_rule(8, 472, 122)
    # the five facts (hoi_20bs, light), with faint gilt dots between them
    out += inset((18, 130, 460, 287), "linear-gradient(180deg,#0C1216,#090D10)")
    for y in (165, 189, 213, 237):
        out += (f'<div style="position:absolute;left:30px;top:{y}px;width:418px;height:2px;'
                'background-image:radial-gradient(circle,rgba(201,165,90,.45) .7px,transparent .9px);background-size:4px 2px"></div>')
    return out + brackets(5, 2, 475, 295, small=True)


# ---------------------------------------------------------------- the cards the game lays on them
SVG_DEFS = ('<linearGradient id="gs_g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F1DC9C"/>'
            '<stop offset="1" stop-color="#8B6A2C"/></linearGradient>'
            '<linearGradient id="gs_gb" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFF3C8"/>'
            '<stop offset="1" stop-color="#C9A55A"/></linearGradient>'
            '<linearGradient id="gs_pf" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1E2A31"/>'
            '<stop offset="1" stop-color="#0B1014"/></linearGradient>'
            '<linearGradient id="gs_pj" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2C665A"/>'
            '<stop offset="1" stop-color="#123029"/></linearGradient>'
            '<pattern id="gs_pin" width="8" height="8" patternUnits="userSpaceOnUse"><rect width="8" height="8" fill="#11191E"/>'
            '<rect width="1" height="8" fill="#1A2329"/></pattern>')


def _path(pts):
    return "M" + "L".join(f"{x},{y}" for x, y in pts) + "Z"


def _rect_path(x0, y0, x1, y1):
    return _path(_rect(x0, y0, x1, y1))


def _arch(x0, x1, top, spring, bottom):
    return f"M{x0},{bottom}L{x0},{spring}A{(x1 - x0) / 2},{spring - top} 0 0 1 {x1},{spring}L{x1},{bottom}Z"


def _svg(w, h, inner):
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="position:absolute;left:0;top:0">'
            f'<defs>{SVG_DEFS}</defs>{inner}</svg>')


def _plaque(x0, y0, x1, y1, selected, point=7):
    m = (y0 + y1) / 2
    pts = f"{x0},{m} {x0 + point},{y0} {x1 - point},{y0} {x1},{m} {x1 - point},{y1} {x0 + point},{y1}"
    rim = "url(#gs_gb)" if selected else "url(#gs_g)"
    return (f'<polygon points="{pts}" fill="{"url(#gs_pj)" if selected else "url(#gs_pf)"}" stroke="{rim}" '
            f'stroke-width="{1.6 if selected else 1.1}"/>')


def _sdiamond(cx, cy, s, fill="url(#gs_g)"):
    return f'<rect x="{cx - s / 2}" y="{cy - s / 2}" width="{s}" height="{s}" transform="rotate(45 {cx} {cy})" fill="{fill}"/>'


def country_card(selected):
    """a major country's card (150 x 274): the portrait (17, 22; 117 x 157) under an arch, the flag (34, 188; 82 x 52),
    the name plate (the game's name at (8, 247), 131 wide)"""
    outer = cham_pts(10, 10, 140, 243, 6)
    hole_p = _arch(19, 131, 22, 52, 177)
    hole_f = _rect_path(34, 188, 116, 240)
    rim = "url(#gs_gb)" if selected else "url(#gs_g)"
    s = [f'<path d="{_path(outer)}{hole_p}{hole_f}" fill="url(#gs_pin)" fill-rule="evenodd"/>']
    if selected:
        s.append(f'<path d="{_path(cham_pts(12, 12, 138, 241, 5))}" fill="none" stroke="{JADE_LINE}" stroke-width="2"/>')
        s.append(f'<path d="{hole_p}" fill="none" stroke="{JADE_LINE}" stroke-width="4" opacity=".7"/>')
    s.append(f'<path d="{_path(outer)}" fill="none" stroke="{rim}" stroke-width="{2 if selected else 1.2}"/>')
    s.append(f'<path d="{_path(cham_pts(14, 14, 136, 239, 4))}" fill="none" stroke="rgba(201,165,90,.4)"/>')
    s.append(f'<path d="{hole_p}" fill="none" stroke="{rim}" stroke-width="1.4"/>')
    s.append(f'<rect x="33.5" y="187.5" width="83" height="53" fill="none" stroke="{rim}" stroke-width="1"/>')
    # between the arch and the flag: a diamond on a hairline
    s.append('<line x1="40" y1="182.5" x2="110" y2="182.5" stroke="rgba(201,165,90,.55)" stroke-width="1"/>')
    s.append(_sdiamond(75, 182.5, 5, rim))
    # the name plate, a step wider than the card
    s.append(_plaque(3, 245, 147, 272, selected))
    return _svg(150, 274, "".join(s))


def minor_card(selected):
    """a minor country's card (138 x 97): the flag at (26, 22), 82 x 52"""
    outer = cham_pts(9, 9, 129, 88, 5)
    rim = "url(#gs_gb)" if selected else "url(#gs_g)"
    s = [f'<path d="{_path(outer)}{_rect_path(26, 22, 108, 74)}" fill="url(#gs_pin)" fill-rule="evenodd"/>']
    if selected:
        s.append(f'<path d="{_path(cham_pts(11, 11, 127, 86, 4))}" fill="none" stroke="{JADE_LINE}" stroke-width="2"/>')
    s.append(f'<path d="{_path(outer)}" fill="none" stroke="{rim}" stroke-width="{2 if selected else 1.2}"/>')
    s.append(f'<path d="{_path(cham_pts(13, 13, 125, 84, 3))}" fill="none" stroke="rgba(201,165,90,.35)"/>')
    s.append(f'<rect x="25.5" y="21.5" width="83" height="53" fill="none" stroke="{rim}" stroke-width="1"/>')
    s.append(_sdiamond(69, 80.5, 4.5, rim))
    return _svg(138, 97, "".join(s))


def mini_card(selected):
    """a mini flag's frame (59 x 44): the flag at (9, 8), 41 x 26"""
    outer = cham_pts(5, 5, 54, 40, 3)
    rim = "url(#gs_gb)" if selected else "url(#gs_g)"
    s = [f'<path d="{_path(outer)}{_rect_path(9, 8, 50, 34)}" fill="url(#gs_pin)" fill-rule="evenodd"/>']
    if selected:
        s.append(f'<path d="{_path(cham_pts(6.5, 6.5, 52.5, 38.5, 2.5))}" fill="none" stroke="{JADE_LINE}" stroke-width="1.6"/>')
    s.append(f'<path d="{_path(outer)}" fill="none" stroke="{rim}" stroke-width="{1.6 if selected else 1}"/>')
    s.append(f'<rect x="8.5" y="7.5" width="42" height="27" fill="none" stroke="{rim}" stroke-width="1"/>')
    s.append(_sdiamond(29.5, 37.3, 3, rim))
    return _svg(59, 44, "".join(s))


def filter_button(lit):
    b = lit_bar(5) if lit else bar(c=5)
    return f'<div style="position:absolute;left:2px;right:2px;top:1px;bottom:1px">{b}</div>'


def start_card(selected):
    """a start's card (232 x 211): its picture at (27, 28), 180 x 104, the date at (22, 147), 185 wide"""
    outer = cham_pts(10, 10, 222, 201, 8)
    rim = "url(#gs_gb)" if selected else "url(#gs_g)"
    s = [f'<path d="{_path(outer)}" fill="url(#gs_pin)"/>',
         '<rect x="27" y="28" width="180" height="104" fill="#06090B"/>']
    if selected:
        s.append(f'<path d="{_path(cham_pts(12, 12, 220, 199, 7))}" fill="none" stroke="{JADE_LINE}" stroke-width="2"/>')
    s.append(f'<path d="{_path(outer)}" fill="none" stroke="{rim}" stroke-width="{2 if selected else 1.2}"/>')
    s.append(f'<path d="{_path(cham_pts(14, 14, 218, 197, 6))}" fill="none" stroke="rgba(201,165,90,.4)"/>')
    s.append(f'<rect x="26.5" y="27.5" width="181" height="105" fill="none" stroke="{rim}" stroke-width="1"/>')
    s.append('<rect x="22.5" y="23.5" width="189" height="113" fill="none" stroke="rgba(201,165,90,.35)" stroke-width="1"/>')
    # small brackets at the outer rule's corners
    for x, y, sx, sy in ((22.5, 23.5, 1, 1), (211.5, 23.5, -1, 1), (22.5, 136.5, 1, -1), (211.5, 136.5, -1, -1)):
        s.append(f'<path d="M{x},{y + sy * 9}L{x},{y}L{x + sx * 9},{y}" fill="none" stroke="{rim}" stroke-width="1.5"/>')
    s.append(_plaque(18, 142, 214, 172, selected, 9))
    s.append('<line x1="40" y1="186.5" x2="107" y2="186.5" stroke="rgba(201,165,90,.5)"/>'
             '<line x1="125" y1="186.5" x2="192" y2="186.5" stroke="rgba(201,165,90,.5)"/>')
    s.append(_sdiamond(116, 186.5, 6, rim))
    return _svg(232, 211, "".join(s))


# the portrait pinned on the facts' sheet (minor_portrait_overlay, 126 x 166, drawn over the portrait): the game puts
# the portrait at the overlay's (9, 11), 108.6 x 146.2 (156 x 210 at 0.696), turned by its rotation (-0.04; the game's
# own border round it is turned about 0.045 rad clockwise, about the portrait's middle), so gilt photo corners hold
# the turned photo, with a hairline on its edge and a soft shadow outside it
PH_CX, PH_CY, PH_W, PH_H, PH_DEG = 63.0, 83.6, 108.6, 146.2, 2.6


def photo_corners():
    x0, y0 = PH_CX - PH_W / 2, PH_CY - PH_H / 2
    x1, y1 = x0 + PH_W, y0 + PH_H
    c = 15
    rot = f'transform="rotate({PH_DEG} {PH_CX} {PH_CY})"'
    s = [f'<clipPath id="gs_out"><path d="M-20,-20H150V190H-20Z{_rect_path(x0, y0, x1, y1)}" clip-rule="evenodd"/></clipPath>']
    g = [f'<rect x="{x0 + 1.5}" y="{y0 + 2.5}" width="{PH_W}" height="{PH_H}" fill="none" stroke="rgba(60,42,14,.28)" '
         'stroke-width="3" clip-path="url(#gs_out)"/>',
         f'<rect x="{x0 + .5}" y="{y0 + .5}" width="{PH_W - 1}" height="{PH_H - 1}" fill="none" stroke="rgba(120,90,40,.55)"/>']
    for (x, y, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        tri = f"M{x - sx * 2},{y - sy * 2}L{x + sx * c},{y - sy * 2}L{x - sx * 2},{y + sy * c}Z"
        g.append(f'<path d="{tri}" fill="url(#gs_g)" stroke="#6E5222" stroke-width=".6"/>')
        g.append(f'<path d="M{x + sx * (c - 3)},{y + sy * 1}L{x + sx * 1},{y + sy * (c - 3)}" stroke="rgba(255,243,200,.55)" stroke-width=".8"/>')
    return _svg(126, 166, "".join(s) + f'<g {rot}>{"".join(g)}</g>')


# the small pie's ring (67 x 68 at (174, 29)) and the glass over the pie (54 x 54 at (180, 35)); the game draws the pie
# (radius 26) under both, so the ring's inner band covers its edge
def pie_frame():
    cx, cy = 33.5, 34
    return _svg(67, 68,
                f'<circle cx="{cx}" cy="{cy}" r="29.5" fill="none" stroke="#0B1014" stroke-width="5"/>'
                f'<circle cx="{cx}" cy="{cy}" r="27.6" fill="none" stroke="url(#gs_g)" stroke-width="1.3"/>'
                f'<circle cx="{cx}" cy="{cy}" r="31.6" fill="none" stroke="rgba(201,165,90,.6)" stroke-width="1"/>'
                + "".join(_sdiamond(cx + 31.6 * math.cos(a), cy + 31.6 * math.sin(a), 3.4)
                          for a in (0, math.pi / 2, math.pi, 3 * math.pi / 2)))


def pie_overlay():
    return ('<div style="position:absolute;left:1px;top:1px;width:52px;height:52px;border-radius:50%;'
            'background:radial-gradient(ellipse at 34% 26%,rgba(255,250,235,.16),rgba(255,250,235,0) 46%),'
            'radial-gradient(circle,rgba(0,0,0,0) 70%,rgba(0,0,0,.28) 100%)"></div>')


# ---------------------------------------------------------------- the map's lobby: its bars, plates and buttons
# The setup's top bar (tiled_frontend_upper_bar, a cornered tile 484 x 128, border 70, stretched across the screen from
# x -10, at y -30 when shown: rows 30-127 show) and bottom bar (the lower one, its rows 0-99 show, at the screen's foot)
# are lacquer with a double gilt rule along the edge that faces the map, the same along their whole length (the game
# stretches or repeats their middle). The scenario plate (menu_top_bg, 394 x 104 at the top's middle, 6 px above the
# screen) hangs from the top bar: a well for the date and the start's name (hoi_24header, light, centred on its x 192),
# the Change Scenario button below (x 61-322, y 61-95).
def upper_bar(w=484, h=128):
    return (f'<div style="position:absolute;left:4px;right:4px;top:4px;height:{h - 8}px;background:{LAC},'
            'linear-gradient(180deg,#121B21,#0E1519 70%,#0B1115)"></div>'
            + gilt_line(4, 116, w - 4, 116, "rgba(201,165,90,.4)") + gilt_line(4, 119, w - 4, 119, "#B8954F")
            + gilt_line(4, 120, w - 4, 120, "rgba(241,220,156,.35)")
            + '<div style="position:absolute;left:4px;right:4px;top:121px;height:3px;background:linear-gradient(180deg,rgba(0,0,0,.7),rgba(0,0,0,0))"></div>'
            + gilt_line(4, 4, 5, 119, "#B8954F") + gilt_line(w - 5, 4, w - 4, 119, "#B8954F"))


def lower_bar(w=484, h=128):
    return (f'<div style="position:absolute;left:4px;right:4px;top:4px;height:{h - 8}px;background:{LAC},'
            'linear-gradient(180deg,#0B1115,#0E1519 30%,#121B21)"></div>'
            + '<div style="position:absolute;left:4px;right:4px;top:4px;height:3px;background:rgba(0,0,0,.7)"></div>'
            + gilt_line(4, 6, w - 4, 6, "#B8954F") + gilt_line(4, 7, w - 4, 7, "rgba(241,220,156,.3)")
            + gilt_line(4, 10, w - 4, 10, "rgba(201,165,90,.4)")
            + gilt_line(4, 6, 5, h - 4, "#B8954F") + gilt_line(w - 5, 6, w - 4, h - 4, "#B8954F"))


def scenario_plate(w=394, h=104):
    out = body([(3, 0), (381, 0), (381, 88), (369, 100), (15, 100), (3, 88)])
    out += inset((15, 6, 369, 57), WELL, "rgba(201,165,90,.7)")
    for sx in (-1, 1):
        x = 192 + sx * 150
        out += diamond(x, 78, 6)
        a, b = (x - 22, x - 6) if sx < 0 else (x + 6, x + 22)
        out += gilt_line(min(a, b), 78, max(a, b), 78, "rgba(201,165,90,.6)")
    return out


# The difficulty panel (lobby_lower_right_sidepanel_bg, 598 x 250; the window 598 x 196 at the screen's lower right, its
# last rows under the bottom bar): a band under "Difficulty" (hoi_24header at (9, 12)) and the custom rules button
# (357, 12); the five difficulty buttons (y 47-82); a double rule; a row each for Ironman (text (30, 103), checkbox
# (530, 101)) and Historical AI focuses ((30, 148), (530, 145)). The multiplayer settings (game_settings_bg, 484 x 97):
# a row each for co-op ((30, 19), (365, 18)) and hot join ((30, 51), (365, 49)).
ROW_FILL = "linear-gradient(180deg,#0E151A,#0A0F12)"


def difficulty_bg(w=598, h=250):
    out = body(_rect(3, 3, w - 3, h - 3))
    out += band(7, 7, w - 7, 45) + gilt_line(7, 45, w - 7, 45, "rgba(201,165,90,.6)")
    out += double_rule(7, w - 7, 88)
    out += inset((9, 95, w - 9, 136), ROW_FILL) + inset((9, 140, w - 9, 181), ROW_FILL)
    return out + brackets(5, 5, w - 5, h - 5)


def mp_settings_bg(w=484, h=97):
    out = body(_rect(3, 3, w - 3, h - 3))
    out += inset((9, 11, w - 9, 47), ROW_FILL) + inset((9, 48, w - 9, 84), ROW_FILL)
    return out + brackets(5, 5, w - 5, h - 5, small=True)


# Start (play_button, 723 x 60: three frames of 241, the game's normal, hover, pressed; the raids view's "create" button
# uses it too) and Ready (play_button_ready, 241 x 60): a jade plaque with pointed ends in a gilt rim, as the deco's lit
# states (the game writes "START" on it in hoi_30header, light)
def play_plate(state=0):
    fills = [("#2C665A", "#163A33"), ("#3A8273", "#1D4A41"), ("#163A33", "#2A6256")][state]
    pts = "5,30 21,4 220,4 236,30 220,56 21,56"
    inner = "11,30 24.5,9 216.5,9 230,30 216.5,51 24.5,51"
    return _svg(241, 60,
                f'<linearGradient id="gs_play{state}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{fills[0]}"/>'
                f'<stop offset="1" stop-color="{fills[1]}"/></linearGradient>'
                f'<polygon points="{pts}" fill="url(#gs_play{state})" stroke="url(#gs_gb)" stroke-width="2"/>'
                f'<polygon points="{inner}" fill="none" stroke="rgba(241,220,156,{.5 if state == 1 else .35})" stroke-width="1"/>'
                '<line x1="27" y1="11.5" x2="214" y2="11.5" stroke="rgba(255,255,255,.12)"/>'
                + _sdiamond(5, 30, 5, "url(#gs_gb)") + _sdiamond(236, 30, 5, "url(#gs_gb)"))


# the details' toggle (extended_country_button, 82 x 57: two frames of 41, the game's arrow down then up)
def toggle(up):
    ch = "M13,26 L20.5,19 L28,26 M13,33 L20.5,26 L28,33" if up else "M13,24 L20.5,31 L28,24 M13,31 L20.5,38 L28,31"
    return _svg(41, 57,
                f'<path d="{_path(cham_pts(3, 3, 38, 54, 6))}" fill="url(#gs_pin)" stroke="url(#gs_g)" stroke-width="1.2"/>'
                f'<path d="{_path(cham_pts(6, 6, 35, 51, 4))}" fill="none" stroke="rgba(201,165,90,.35)"/>'
                f'<path d="{ch}" fill="none" stroke="#E3C77E" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>')


# the difficulty buttons (232 x 35 each: two frames of 116, normal and selected; the game writes the level centred 9 px
# right of the button's middle, clear of its emblem at the left) with rank marks in line art: a civilian, one to three
# chevrons, a star
def rank(kind, lit):
    c = "#FBEAB4" if lit else "#E3C77E"
    a = f'fill="none" stroke="{c}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"'
    marks = {
        "civilian": f'<circle cx="9" cy="5.6" r="2.8" {a}/><path d="M3.6,15.5 a5.4,5.4 0 0 1 10.8,0" {a}/>',
        "recruit": f'<path d="M3,12 L9,6.5 L15,12" {a}/>',
        "regular": f'<path d="M3,10 L9,4.5 L15,10 M3,14.5 L9,9 L15,14.5" {a}/>',
        "veteran": f'<path d="M3,7.5 L9,2.5 L15,7.5 M3,11.5 L9,6.5 L15,11.5 M3,15.5 L9,10.5 L15,15.5" {a}/>',
        "elite": ('<path d="' + "".join(("M" if i == 0 else "L") + f"{9 + (7.2 if i % 2 == 0 else 3) * math.sin(i * math.pi / 5):.2f},"
                                          f"{9.6 - (7.2 if i % 2 == 0 else 3) * math.cos(i * math.pi / 5):.2f}" for i in range(10))
                  + f'Z" {a}/>'),
    }
    return (f'<svg width="18" height="18" viewBox="0 0 18 18" style="position:absolute;left:7px;top:8.5px">'
            f'{marks[kind]}</svg>')


def difficulty_button(kind, lit):
    b = lit_bar(5) if lit else bar(c=5)
    return f'<div style="position:absolute;left:1px;right:1px;top:1px;bottom:1px">{b}</div>' + rank(kind, lit)


# the custom rules button (custom_set_button_2, 464 x 35: two frames of 232, the same picture in the game's; the game
# writes its text centred in x 5-235)
def gear(lit):
    c = "#FBEAB4" if lit else "#E3C77E"
    teeth = "".join(f'<line x1="{9 + 5.2 * math.cos(i * math.pi / 4):.2f}" y1="{9 + 5.2 * math.sin(i * math.pi / 4):.2f}" '
                    f'x2="{9 + 7.6 * math.cos(i * math.pi / 4):.2f}" y2="{9 + 7.6 * math.sin(i * math.pi / 4):.2f}" '
                    f'stroke="{c}" stroke-width="2.2"/>' for i in range(8))
    return (f'<svg width="18" height="18" viewBox="0 0 18 18" style="position:absolute;left:9px;top:8.5px">'
            f'<circle cx="9" cy="9" r="5" fill="none" stroke="{c}" stroke-width="1.6"/><circle cx="9" cy="9" r="1.7" '
            f'fill="none" stroke="{c}" stroke-width="1.3"/>{teeth}</svg>')


def custom_button(lit):
    b = lit_bar(5) if lit else bar(c=5)
    return f'<div style="position:absolute;left:1px;right:1px;top:1px;bottom:1px">{b}</div>' + gear(lit)


# the Ready mark on the Start button in multiplayer (generic_checkbox2, 68 x 30): the core skin's checkbox
def ready_check():
    return frames(68, 30,
                  '<div style="position:absolute;left:7px;top:5px;width:20px;height:20px;background:#0A0F12;box-shadow:inset 0 0 0 1px #C9A55A"></div>',
                  '<div style="position:absolute;left:7px;top:5px;width:20px;height:20px;background:#163A33;box-shadow:inset 0 0 0 1px #E3C77E"></div>'
                  '<svg width="34" height="30" viewBox="0 0 34 30" style="position:absolute;left:0;top:0"><path d="M11 15.5l4 4 8-9" '
                  'fill="none" stroke="#F1DC9C" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>')


# the two map modes under the scenario plate (lobby_country_mapmode_strip and _selected, 100 x 50: two frames of 50,
# drawn centred): the countries (a flag) and the players (people), as the in-game map modes' medallions; selected jade
def mapmode(icon_name, selected):
    disc = ("radial-gradient(circle at 50% 35%,#2F6E61,#163A33 70%)" if selected
            else "radial-gradient(circle at 50% 35%,#1C2830,#0B1014 70%)")
    ring = "#F1DC9C" if selected else "#C9A55A"
    return (f'<div style="position:absolute;left:3px;top:3px;width:44px;height:44px;border-radius:50%;background:{disc};'
            f'box-shadow:0 0 0 {2 if selected else 1.4}px {ring},0 0 0 4px rgba(11,16,20,.85),0 0 0 5px rgba(201,165,90,.45)"></div>'
            f'<div class="ico" style="position:absolute;left:3px;top:3px;width:44px;height:44px">'
            f'{_icon(icon_name, 24, "#FBEAB4" if selected else "#E3C77E", 1.6)}</div>')


DIFFICULTY = ("civilian", "recruit", "regular", "veteran", "elite")

ADDS = [
    ("gs_country_bg", "gfx/interface/country_selection_bg.dds", CS_W, CS_H, country_bg),
    ("gs_date_bg", "gfx/interface/select_date_bg.dds", SD_W, SD_H, date_bg),
    ("gs_details_bg", "gfx/interface/lobby_right_sidepanel_bg.dds", 492, 301, details_bg),
    # the game's .gfx names .tga files for the card and the country selection picture; it loads a .dds of the same
    # name first, and its own files are .dds
    ("gs_card", "gfx/interface/country_selection_entry.dds", 300, 274,
     lambda: frames(300, 274, country_card(False), country_card(True))),
    ("gs_card_minor", "gfx/interface/country_selection_minor_entry.dds", 276, 97,
     lambda: frames(276, 97, minor_card(False), minor_card(True))),
    ("gs_card_mini", "gfx/interface/diplo_countrylist_flag_frame_mini.dds", 118, 44,
     lambda: frames(118, 44, mini_card(False), mini_card(True))),
    ("gs_filter", "gfx/interface/country_filter_entry.dds", 298, 34,
     lambda: frames(298, 34, filter_button(True), filter_button(False))),
    ("gs_start_card", "gfx/interface/bookmark_entry_bg.dds", 464, 211,
     lambda: frames(464, 211, start_card(False), start_card(True))),
    ("gs_portrait_corners", "gfx/interface/minor_portrait_overlay.dds", 126, 166, photo_corners),
    ("gs_pie_frame", "gfx/interface/small_pol_piechart_frame.dds", 67, 68, pie_frame),
    ("gs_pie_glass", "gfx/interface/small_pol_piechart_overlay.dds", 54, 54, pie_overlay),
    # the map's lobby
    ("gs_upper_bar", "gfx/interface/tiles/tiled_frontend_upper_bar.dds", 484, 128, upper_bar),
    ("gs_lower_bar", "gfx/interface/tiles/tiled_frontend_lower_bar.dds", 484, 128, lower_bar),
    ("gs_scenario_plate", "gfx/interface/menu_top_bg.dds", 394, 104, scenario_plate),
    ("gs_difficulty_bg", "gfx/interface/lobby_lower_right_sidepanel_bg.dds", 598, 250, difficulty_bg),
    ("gs_mp_settings_bg", "gfx/interface/game_settings_bg.dds", 484, 97, mp_settings_bg),
    ("gs_play", "gfx/interface/play_button.dds", 723, 60, lambda: frames(723, 60, play_plate(0), play_plate(1), play_plate(2))),
    ("gs_play_ready", "gfx/interface/play_button_ready.dds", 241, 60, lambda: play_plate(0)),
    ("gs_details_toggle", "gfx/interface/extended_country_button.dds", 82, 57, lambda: frames(82, 57, toggle(False), toggle(True))),
    *[(f"gs_difficulty_{k}", f"gfx/interface/difficulty_button_{k}.dds", 232, 35,
       (lambda k=k: frames(232, 35, difficulty_button(k, False), difficulty_button(k, True)))) for k in DIFFICULTY],
    # the game's two frames are the same picture; so are ours
    ("gs_custom_rules", "gfx/interface/custom_set_button_2.dds", 464, 35, lambda: frames(464, 35, custom_button(False), custom_button(False))),
    ("gs_ready_check", "gfx/interface/generic_checkbox2.dds", 68, 30, ready_check),
    ("gs_mapmode", "gfx/interface/lobby_country_mapmode_strip.dds", 100, 50,
     lambda: frames(100, 50, mapmode("war", False), mapmode("manpower", False))),
    ("gs_mapmode_selected", "gfx/interface/lobby_country_mapmode_strip_selected.dds", 100, 50,
     lambda: frames(100, 50, mapmode("war", True), mapmode("manpower", True))),
]
