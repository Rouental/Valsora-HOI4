"""The selected armies', army groups', fleets' and operatives' badges on the map (unitview.gui, naviesview.gui,
operativeleader.gui), at the game's paths and sizes (2026-10-17, SCREEN_INVENTORY.md's suggestion 3).

The game draws a selected army (or army group, fleet, operative) as a badge in the screen's top left corner (moved
below the flag medallion by make_mapviews.py): one picture with a header band (insignia, name, counts, close), the
commander's portrait, a text area (title and name), the skill and statistics, the traits, and a slot along the bottom
for the divisions' counters (the ships, the operative's status bar). Its own texts are light (hoi_16mbs, hoi_18mbs,
hoi_18: white), except an operative's code name (hoi4_typewriter16: black ink). The panels here are where the game's
pictures have theirs (measured from them; the numbers are the .gui's, in each picture's own pixels): a lacquer plate
with a gilt rim, a raised header band over a gilt rule, recessed lacquer panels under the texts, statistics and
counters, an ivory label under the operative's code name. An army group's badge is the army's with a double gilt rim,
gilt corner brackets and the count's plaque in gold. Selected or lit states are jade, as everywhere.

The small buttons on them are redrawn as lacquer chips with clean line glyphs (modern subjects: a truck for
motorization, a jet for the air wings); the close button is the Deco UI's diamond. The selected air wings
(airselectionview.gui) are rows, not badges: an air base's row and its wings' rows, plain lacquer.

gen_textures.py adds them (keys mv_*); preview_mapviews.py draws the badges as the game lays them out.
"""
from art_util import DIM_FILL, LIT_FILL, GOLD, bar, frames, gilt, img_tag, vanilla_frames
from designer_art import _layer, _shrink, inset, gilt_line
from icons import icon

LAC = "repeating-linear-gradient(90deg,rgba(255,255,255,.025) 0 1px,transparent 1px 7px)"
BODY = f"{LAC},linear-gradient(180deg,#141E24,#0D1418)"
HEAD = f"{LAC},linear-gradient(180deg,#1E2A31,#131C22)"
WELL = "linear-gradient(180deg,#0B1115,#070A0D)"
RIM = "#B8954F"
GILT = "#E3C77E"
SOFT = "rgba(201,165,90,.55)"
UC = "gfx/interface/unitcontrol/"


def cham(x0, y0, x1, y1, c):
    return [(x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c), (x1 - c, y1), (x0 + c, y1), (x0, y1 - c), (x0, y0 + c)]


def _clip(pts, html):
    """html drawn inside the polygon pts only"""
    return ('<div style="position:absolute;inset:0;clip-path:polygon(' + ",".join(f"{x}px {y}px" for x, y in pts)
            + f')">{html}</div>')


def _svg(w, h, body, defs=""):
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="position:absolute;left:0;top:0">'
            f'<defs>{defs}</defs>{body}</svg>')


GOLD_DEFS = ('<linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F1DC9C"/>'
             '<stop offset="1" stop-color="#8B6A2C"/></linearGradient>'
             '<linearGradient id="pf" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1E2A31"/>'
             '<stop offset="1" stop-color="#0B1014"/></linearGradient>')


def _ppath(pts):
    return "M" + "L".join(f"{x},{y}" for x, y in pts) + "Z"


def plate(box, c=6, group=False, head=None, rule=None):
    """the badge's plate: lacquer inside a gilt rim (an army group's: a gold rim and a second hairline inside it), and
    the raised header band down to y `head` over a gilt rule"""
    pts = cham(*box, c)
    out = _layer(pts, GOLD if group else RIM) + _layer(_shrink(pts, 1.5 if group else 1.2), BODY)
    inner = _shrink(pts, 1.5 if group else 1.2)
    if head:
        x0, y0, x1, _ = box
        band = (f'<div style="position:absolute;left:0;right:0;top:0;height:{head - y0 + 2}px;background:{HEAD}"></div>'
                f'<div style="position:absolute;left:0;right:0;top:{y0 + 2}px;height:1px;background:rgba(241,220,156,.16)"></div>')
        out += _clip(inner, band)
        out += gilt_line(x0 + 1, head, x1 - 1, head, GOLD if group else "rgba(201,165,90,.8)")
        out += gilt_line(x0 + 1, head + 1, x1 - 1, head + 1, "rgba(0,0,0,.6)")
    if group:
        out += _svg(box[2] + 2, box[3] + 2, f'<path d="{_ppath(_shrink(pts, 4))}" fill="none" stroke="rgba(227,199,126,.5)" stroke-width="1"/>')
    return out


def recess(x0, y0, x1, y1, c=3, rim=SOFT, fill=WELL):
    return inset(cham(x0, y0, x1, y1, c), fill, rim)


def corner_marks(box, gold=True):
    """small gilt brackets in the four corners (drawn as SVG, so they sit exactly)"""
    x0, y0, x1, y1 = box
    col = "#E3C77E" if gold else "rgba(201,165,90,.7)"
    d = ""
    for cx, cy, sx, sy in ((x0 + 4, y0 + 4, 1, 1), (x1 - 4, y0 + 4, -1, 1), (x0 + 4, y1 - 4, 1, -1), (x1 - 4, y1 - 4, -1, -1)):
        d += f"M{cx},{cy + sy * 7}V{cy}H{cx + sx * 7}M{cx + sx * 3},{cy + sy * 6}V{cy + sy * 3}H{cx + sx * 6}"
    return _svg(x1 + 2, y1 + 2, f'<path d="{d}" fill="none" stroke="{col}" stroke-width="1.2"/>')


# ---------------------------------------------------------------- the army badge (unitview.gui, army_badge_view)
# window coordinates = picture coordinates (army_bg and army_group_bg sit at (0, 0)). The game draws on it: the army's
# insignia (15, 0, 33 x 32) with its count; the name (edit box 66-201, y 10-33), supply (196) and fuel (220) icons;
# the army group's insignia (245), unassign (278), the divisions' count plaque (311-404, its own picture) and close
# (401-432); the portrait (9, 32, 51 x 69) in its frame (5, 27, 59 x 79) with two buttons over its foot (4 and 38, 81);
# title and name (70, 38 and 54, 133 wide); the skill (centred 211, 55) and four statistics (219-299, icons y 38-64,
# numbers y 57); the traits (302, 48: 21 x 32 a slot) and the preferred tactic (centred 418, 65); along the bottom the
# organisation and strength bars (62, 70, 21 x 36), the divisions' counters (79-271, y 75-102) and the buttons
# (select all 260, motorization 305, railway gun 346, armies/divisions or wings 387; y 77-100).
ARMY_BOX = (2, 2, 434, 107)
ARMY_HEAD = 30
NAME_TAB = [(52, 6), (248, 6), (248, 25), (244, 29), (56, 29), (52, 25)]


def army_badge(group=False):
    b = ARMY_BOX
    out = plate(b, 6, group, ARMY_HEAD)
    # the insignia's socket and the name's tab (name, supply, fuel)
    out += inset(cham(12, 3, 51, 32, 9), WELL, GOLD if group else SOFT)
    out += inset(NAME_TAB, WELL, "rgba(201,165,90,.7)" if group else SOFT)
    # the portrait's well, the title and name, the skill and statistics
    out += recess(6, 31, 63, 106, 2)
    out += recess(66, 35, 195, 74)
    out += recess(197, 35, 300, 76)
    # the traits: a faint gilt baseline under their slots, fading out to the right
    out += ('<div style="position:absolute;left:304px;top:82px;width:126px;height:1px;'
            'background:linear-gradient(90deg,rgba(201,165,90,.45),rgba(201,165,90,0))"></div>')
    # the bottom slot: the divisions' counters and the buttons
    out += recess(64, 77, 432, 104, 3, "rgba(201,165,90,.7)" if group else SOFT)
    if group:
        out += corner_marks(b)
    return out


# the divisions' count plaques (div_count_bg at (311, 6), group_div_count_bg at (311, 3)): the count is centred in
# x 312-402 from y 12 (hoi_18mbs), so the plaque's middle is at the text's (y 23 on the badge)
def count_plaque(w, h, cy, group=False):
    x0, x1 = 4, w - 4
    hh = 12.5
    pts = [(x0, cy), (x0 + 9, cy - hh), (x1 - 9, cy - hh), (x1, cy), (x1 - 9, cy + hh), (x0 + 9, cy + hh)]
    poly = " ".join(f"{x},{y}" for x, y in pts)
    s = (f'<polygon points="{poly}" fill="url(#pf)" stroke="url(#g)" stroke-width="{1.6 if group else 1.2}"/>'
         f'<polygon points="{" ".join(f"{x},{y}" for x, y in _shrink(pts, 3))}" fill="none" '
         f'stroke="rgba(201,165,90,{.6 if group else .35})" stroke-width="1"/>')
    if group:       # gilt diamonds at the plaque's points (the game's laurels)
        for x in (x0 - 1, x1 + 1):
            s += (f'<rect x="{x - 3}" y="{cy - 3}" width="6" height="6" transform="rotate(45 {x} {cy})" fill="url(#g)"/>')
    return _svg(w, h, s, GOLD_DEFS)


# the commander's portrait frames (59 x 79 at (5, 27): the portrait fills x 4-55, y 5-74 of it)
def portrait_frame(w, h, hole, group=False, c=3):
    hx0, hy0, hx1, hy1 = hole
    outer = cham(0.5, 0.5, w - 1.5, h - 1.5, c)
    d = _ppath(outer) + f"M{hx0},{hy0}H{hx1}V{hy1}H{hx0}Z"
    rim = "url(#g)" if group else RIM
    s = (f'<path d="{d}" fill="#0E1519" fill-rule="evenodd"/>'
         f'<path d="{_ppath(outer)}" fill="none" stroke="{rim}" stroke-width="{1.4 if group else 1}"/>'
         f'<rect x="{hx0 - .5}" y="{hy0 - .5}" width="{hx1 - hx0 + 1}" height="{hy1 - hy0 + 1}" fill="none" '
         f'stroke="{"#E3C77E" if group else "rgba(201,165,90,.7)"}" stroke-width="1"/>')
    if group:       # gold diamonds on the frame's four corners
        for x, y in ((hx0 - .5, hy0 - .5), (hx1 + .5, hy0 - .5), (hx0 - .5, hy1 + .5), (hx1 + .5, hy1 + .5)):
            s += f'<rect x="{x - 2.6}" y="{y - 2.6}" width="5.2" height="5.2" transform="rotate(45 {x} {y})" fill="url(#g)" stroke="#0B1014" stroke-width=".6"/>'
    return _svg(w, h, s, GOLD_DEFS)


# ---------------------------------------------------------------- small buttons
def chip(w, h, c=4, lit=False, inset_=0):
    """a lacquer chip with a gilt rim (lit: jade), `inset_` px in from the picture's edge"""
    b = bar(LIT_FILL, GOLD, c, .35) if lit else bar(DIM_FILL, "rgba(201,165,90,.75)", c, .14)
    if inset_:
        return f'<div style="position:absolute;inset:{inset_}px">{b}</div>'
    return b


def glyph(w, h, d, col=GILT, sw=1.4, fill="none", extra=""):
    return _svg(w, h, f'<path d="{d}" fill="{fill}" stroke="{col}" stroke-width="{sw}" stroke-linecap="round" '
                      f'stroke-linejoin="round"/>{extra}')


def close_diamond(w=31, h=31):
    """the Deco UI's close button (closebutton.dds) at this size: a lacquer diamond with a gilt rim and cross"""
    s = 20
    cx, cy = w / 2, h / 2
    return (f'<div style="position:absolute;left:{cx - s / 2}px;top:{cy - s / 2}px;width:{s}px;height:{s}px;transform:rotate(45deg);'
            'border:1px solid #E3C77E;background:#0B1014;box-sizing:border-box"></div>'
            + glyph(w, h, f"M{cx - 4.5},{cy - 4.5}L{cx + 4.5},{cy + 4.5}M{cx + 4.5},{cy - 4.5}L{cx - 4.5},{cy + 4.5}", sw=1.6))


def unassign(w=31, h=31):
    """leave the army group: an open bracket and an arrow out of it"""
    return chip(w, h, 5, inset_=2) + glyph(w, h, "M16,9.5H10.5V21.5H16M13.5,15.5H23M19.5,12L23,15.5L19.5,19")


def leader_details(w=24, h=25):
    """the commander's details: a bust"""
    return chip(w, h, 3, inset_=1) + glyph(w, h, "M7,19.5C7,16 9,14.8 12,14.8C15,14.8 17,16 17,19.5", sw=1.3,
                                           extra=f'<circle cx="12" cy="10" r="3" fill="none" stroke="{GILT}" stroke-width="1.3"/>')


def select_all_short(w=52, h=23):
    """select all the army's divisions: three cards fanned out"""
    cards = ""
    for i, op in ((0, .45), (1, .7), (2, 1)):
        x, y = 18 + i * 4, 9 - i * 2
        cards += (f'<rect x="{x}" y="{y}" width="10" height="9" fill="#0E1519" stroke="{GILT}" stroke-opacity="{op}" '
                  f'stroke-width="1.2"/>')
    return chip(w, h, 4) + _svg(w, h, cards)


def truck(x, y, s=1.0, col=GILT, op=1.0):
    """a small modern truck, side on, facing right, its box's top left at (x, y)"""
    p = (f"M{x},{y}h{9 * s}v{7 * s}h{-9 * s}zM{x + 9 * s},{y + 2.2 * s}h{3.4 * s}l{2.2 * s},{2.4 * s}v{2.4 * s}h{-5.6 * s}")
    wheels = "".join(f'<circle cx="{x + cx * s}" cy="{y + 8.4 * s}" r="{1.5 * s}" fill="#0E1519" stroke="{col}" stroke-width="1.1"/>'
                     for cx in (2.6, 11.6))
    return (f'<path d="{p}" fill="none" stroke="{col}" stroke-width="1.15" stroke-linejoin="round" opacity="{op}"/>'
            f'<g opacity="{op}">{wheels}</g>')


def motorization_strip():
    """the army's motorization priority, laid over the button (30 x 23 a frame): low (the game's horse: no trucks), a
    dim truck; medium, a truck; high, two trucks"""
    f1 = _svg(30, 23, truck(7.5, 6.5, 1.0, "#C9A55A", .5))
    f2 = _svg(30, 23, truck(7.5, 6.5, 1.0, GILT))
    f3 = _svg(30, 23, truck(4.5, 3.5, .85, "#C9A55A", .8) + truck(10, 9.5, .85, "#FBEAB4"))
    return frames(90, 23, f1, f2, f3)


def railway_gun(w=44, h=23):
    """attach a railway gun: a long barrel raised over a flat rail car, on two bogies and a rail"""
    d = "M6,14.5H38M12.5,14.5L15.5,11.5H26.5L29.5,14.5M18,11.5L39,3.5M5,19.8H39"
    wheels = "".join(f'<circle cx="{x}" cy="17" r="1.5" fill="#0E1519" stroke="{GILT}" stroke-width="1"/>'
                     for x in (9, 12.8, 31.2, 35))
    return chip(w, h, 4) + glyph(w, h, d, sw=1.2, extra=wheels)


def hierarchy(w, h, col):
    d = (f"M{w / 2 - 4},4.5h8v4.5h-{8}zM{w / 2},9V12.5M{w / 2 - 11},12.5H{w / 2 + 11}"
         f"M{w / 2 - 11},12.5V14M{w / 2},12.5V14M{w / 2 + 11},12.5V14"
         f"M{w / 2 - 15},14h8v4.5h-8zM{w / 2 - 4},14h8v4.5h-8zM{w / 2 + 7},14h8v4.5h-8z")
    return glyph(w, h, d, col, 1.1)


def armies_divisions():
    """an army group's view, armies or divisions (2 frames: normal, lit)"""
    return frames(88, 23, chip(44, 23, 4) + hierarchy(44, 23, "#C9A55A"), chip(44, 23, 4, lit=True) + hierarchy(44, 23, "#FBEAB4"))


def select_wings(w=44, h=23):
    """select the army's air wings: a modern jet"""
    return chip(w, h, 4) + f'<div class="ico" style="position:absolute;inset:0">{icon("air", 21, GILT, 1.25)}</div>'


def plain_chip(w=44, h=23):
    return chip(w, h, 4)


def globe(cx, cy, r, col=GILT):
    """a line globe: the rim, the equator and two meridians"""
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#0B1014" stroke="{col}" stroke-width="1.2"/>'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{r * .45}" ry="{r}" fill="none" stroke="{col}" stroke-width=".9"/>'
            f'<path d="M{cx - r},{cy}H{cx + r}M{cx - r * .86},{cy - r * .5}H{cx + r * .86}M{cx - r * .86},{cy + r * .5}H{cx + r * .86}" '
            f'stroke="{col}" stroke-width=".8" opacity=".8"/>')


def expeditionary(w=264, h=32):
    """Request Expeditionaries (the game centres its text in x 20-244): a lacquer bar with a gilt globe at its left"""
    return (f'<div style="position:absolute;left:2px;right:2px;top:2px;bottom:2px">{bar(c=7)}</div>'
            + _svg(w, h, globe(20, h / 2, 9.5)))


# ---------------------------------------------------------------- the fleet header (naviesview.gui, fleet_view_header)
# fleet_bg is drawn at (-2, 2) in the 492 x 166 window, so a picture's pixel is the window's + (2, -2). On it the game
# draws: the fleet's insignia (8-41, 4-36); the name (edit box 72-284, y 10-33); the task forces' count, centred in
# 320-410 from y 8 (on a plaque that is part of this picture); close (456-487, 3-34); a column at the right for the
# pride of the fleet (453, 38), fuel (457, 73) and the air base (455, 103); the admiral's portrait (10-71, 45-127) in its
# frame (6-75, 38-133) with two buttons over its foot; rank and name (83, 48 and 64); the skill (centred 213, 63) and
# statistics (218-300, y 45-83); the traits (304, 58); the ships (77-377, y 93-127); along the bottom "Active in
# regions" (18, 138), the home base (202-356, 133-165) and Select all (356-492, 140-163).
FLEET_BOX = (1, 1, 491, 164)
FLEET_HEAD = 37


def fleet_bg():
    b = FLEET_BOX
    out = plate(b, 7, False, FLEET_HEAD)
    out += inset(cham(6, 3, 43, 35, 9), WELL, SOFT)                                  # the insignia's socket
    out += inset([(56, 7), (300, 7), (300, 30), (295, 35), (61, 35), (56, 30)], WELL, SOFT)   # the name's tab
    # the task forces' count plaque, as the army's
    cy, hh, x0, x1 = 20, 12.5, 323, 407
    pts = [(x0, cy), (x0 + 9, cy - hh), (x1 - 9, cy - hh), (x1, cy), (x1 - 9, cy + hh), (x0 + 9, cy + hh)]
    out += _svg(493, 166, f'<polygon points="{" ".join(f"{x},{y}" for x, y in pts)}" fill="url(#pf)" stroke="url(#g)" '
                          f'stroke-width="1.2"/><polygon points="{" ".join(f"{x},{y}" for x, y in _shrink(pts, 3))}" '
                          'fill="none" stroke="rgba(201,165,90,.35)" stroke-width="1"/>', GOLD_DEFS)
    out += recess(8, 40, 73, 131, 2)                                                 # the portrait's well
    out += recess(79, 44, 197, 88)                                                   # rank and name
    out += recess(199, 44, 302, 88)                                                  # skill and statistics
    out += ('<div style="position:absolute;left:306px;top:89px;width:136px;height:1px;'
            'background:linear-gradient(90deg,rgba(201,165,90,.45),rgba(201,165,90,0))"></div>')
    out += recess(449, 39, 489, 131, 3)                                              # pride, fuel, air base
    out += recess(76, 92, 407, 130, 3)                                               # the ships
    # the foot band: a raised plate under a gilt rule
    foot = (f'<div style="position:absolute;left:0;right:0;top:134px;bottom:0;background:{HEAD}"></div>')
    out += _clip(_shrink(cham(*b, 7), 1.2), foot)
    out += gilt_line(2, 133, 490, 133, "rgba(201,165,90,.8)") + gilt_line(2, 132, 490, 132, "rgba(0,0,0,.6)")
    return out


def fleet_hl():
    """the fleet header's highlight (497 x 170, drawn at (-4, 0): 2 px round the picture): a jade line on the plate's
    rim and a soft jade glow either side of it"""
    pts = cham(3, 3, 493, 166, 7)
    d = _ppath(pts)
    return _svg(497, 170, f'<path d="{d}" fill="none" stroke="rgba(108,194,169,.28)" stroke-width="5"/>'
                          f'<path d="{d}" fill="none" stroke="#6CC2A9" stroke-width="1.6"/>'
                          f'<path d="{_ppath(_shrink(pts, 3))}" fill="none" stroke="rgba(108,194,169,.35)" stroke-width="1"/>')


def select_all_bar(w=136, h=23):
    """Select all (the game writes it in hoi_18mbs): a lacquer bar"""
    return bar(c=5, shine=.18)


def pride_icon():
    return img_tag(gilt(vanilla_frames("gfx/interface/naviesview/pride_of_the_fleet_icon.dds", 1)[0], 1.05))


# ---------------------------------------------------------------- the operative badge (operativeleader.gui)
# operative_leader_badge is the badge's background (0, 0). On it the game draws: the agency's emblem (8, 0: about
# 35 x 36); the code name (edit box 66-201, y 10-33) in the typewriter font, in black ink, so it sits on an ivory label;
# close (401, 3); the skill (centred 211, 57); name and title (70, 38 and 54); the traits (230, 48); the nationalities'
# flags (324-424, y 34-80, from the right); the portrait (5, 27) in the army's frame; the status bar (64, 78: its bar
# 66-425, y 80-97, and its text).
def operative_badge():
    b = ARMY_BOX
    out = plate(b, 6, False, ARMY_HEAD)
    # the agency's emblem: a round socket
    out += _svg(437, 109, '<circle cx="25.5" cy="17" r="14.5" fill="#080C0F" stroke="rgba(201,165,90,.75)" stroke-width="1.2"/>'
                          '<circle cx="25.5" cy="17" r="11.5" fill="none" stroke="rgba(201,165,90,.25)" stroke-width="1"/>')
    # the code name's ivory label: chamfered, a sepia rule inside
    lab = [(56, 6), (242, 6), (248, 12), (248, 29), (62, 29), (56, 23)]
    out += _layer(lab, "#9C7A36") + _layer(_shrink(lab, 1), "linear-gradient(180deg,#EFE6CE,#DCCDA6)")
    out += _svg(437, 109, f'<path d="{_ppath(_shrink(lab, 3))}" fill="none" stroke="rgba(156,122,54,.55)" stroke-width="1"/>')
    out += recess(6, 31, 63, 106, 2)
    out += recess(66, 35, 195, 74)
    out += recess(197, 35, 322, 76)
    out += ('<div style="position:absolute;left:326px;top:80px;width:104px;height:1px;'
            'background:linear-gradient(270deg,rgba(201,165,90,.45),rgba(201,165,90,0))"></div>')
    out += recess(64, 78, 432, 101, 3)
    return out


def progress_bg(w=359, h=17):
    """the operative's status bar, empty: a recess"""
    return ('<div style="position:absolute;inset:0;background:#080C0F;box-shadow:inset 0 0 0 1px rgba(201,165,90,.5),'
            'inset 0 2px 3px rgba(0,0,0,.6)"></div>')


# ---------------------------------------------------------------- the selected air wings (airselectionview.gui)
# One row per air base (548 x 48: its flag, name, capacity, the quick deployment and create buttons, close) and one per
# wing under it (548 x 48 a frame, 2 frames side by side; also the rocket sites' and gun emplacements' rows): the game
# writes light text across them (hoi_18, hoi_16mbs) and has no panels inside them, so they are plain lacquer rows. The
# game's second wing frame is red, a state the game sets in code (assumed: a wing that needs attention), so it is
# coral-tinted lacquer here.
CORAL = f"{LAC},linear-gradient(180deg,#3A2226,#1E1214)"


def row(w, h, fill, rim, c=6, shine=.16, line=None):
    pts = cham(1, 1, w - 1, h - 1, c)
    out = _layer(pts, rim) + _layer(_shrink(pts, 1.1), fill)
    out += f'<div style="position:absolute;left:{c + 4}px;right:{c + 4}px;top:3px;height:1px;background:rgba(241,220,156,{shine})"></div>'
    if line:
        out += _svg(w, h, f'<path d="{_ppath(_shrink(pts, 3.5))}" fill="none" stroke="{line}" stroke-width="1"/>')
    return out


def air_base_row():
    return row(548, 48, HEAD, RIM, 7, .2, "rgba(201,165,90,.3)")


def air_wing_rows():
    """2 frames: normal, the game's red one"""
    return frames(1096, 48, row(548, 46, BODY, "rgba(201,165,90,.6)", 5, .12),
                  row(548, 46, CORAL, "rgba(238,140,126,.75)", 5, .14))


ADDS = [
    # the army badge and the army group's (same layout; the game's group picture is 436 x 110)
    ("mv_army_bg", UC + "army_group_bg.dds", 437, 109, army_badge),
    ("mv_army_group_bg", UC + "army_group_group_bg.dds", 436, 110, lambda: army_badge(group=True)),
    ("mv_div_count", "gfx/interface/div_count_bg.dds", 93, 35, lambda: count_plaque(93, 35, 17)),
    ("mv_group_div_count", "gfx/interface/group_div_count_bg.dds", 92, 39, lambda: count_plaque(92, 39, 20, group=True)),
    ("mv_leader_frame", UC + "unit_leader_portrait_frame_badge.dds", 59, 79,
     lambda: portrait_frame(59, 79, (5, 6, 54, 73))),
    ("mv_group_leader_frame", UC + "group_leader_portrait_frame_badge.dds", 59, 79,
     lambda: portrait_frame(59, 79, (5, 6, 54, 73), group=True)),
    ("mv_unassign", UC + "btn_unassign.dds", 31, 31, unassign),
    ("mv_close", "gfx/interface/naviesview/btn_close.dds", 31, 31, close_diamond),
    ("mv_leader_details", UC + "leader_details_icon.dds", 24, 25, leader_details),
    ("mv_select_all_short", UC + "select_all_armylist_short_button.dds", 52, 23, select_all_short),
    ("mv_motor_btn", UC + "motorization_level_toggle_button.dds", 44, 23, plain_chip),
    ("mv_motor_strip", UC + "motorization_level_toggle_strip.dds", 90, 23, motorization_strip),
    ("mv_railway_gun", UC + "army_railway_gun_toggles_button.dds", 44, 23, railway_gun),
    ("mv_armies_divisions", "gfx/interface/army_group_toggle_armies_divisions_btn.dds", 88, 23, armies_divisions),
    ("mv_select_wings", UC + "army_select_wings_button.dds", 44, 23, select_wings),
    ("mv_expeditionary", UC + "expeditionary_force_button_bg.dds", 264, 32, expeditionary),
    # the fleet header
    ("mv_fleet_bg", "gfx/interface/naviesview/fleet_bg.dds", 493, 166, fleet_bg),
    ("mv_fleet_hl", "gfx/interface/naviesview/fleet_bg_hl.dds", 497, 170, fleet_hl),
    ("mv_naval_leader_frame", "gfx/interface/naval_unit_leader_frame.dds", 69, 95,
     lambda: portrait_frame(69, 95, (5, 8, 64, 88))),
    ("mv_select_all", "gfx/interface/select_all_armylist_btn.dds", 136, 23, select_all_bar),
    ("mv_pride", "gfx/interface/naviesview/pride_of_the_fleet_icon.dds", 32, 30, pride_icon),
    # the operative badge
    ("mv_operative_badge", "gfx/interface/operatives/operative_leader_badge.dds", 437, 109, operative_badge),
    ("mv_operative_bar_bg", "gfx/interface/operatives/operative_activity_progress_bar_bg.dds", 359, 17, progress_bg),
    # the selected air wings
    ("mv_air_base_row", "gfx/interface/airview/base_entry_bg.dds", 548, 48, air_base_row),
    ("mv_air_wing_rows", "gfx/interface/airview/wing_entry_bg.dds", 1096, 48, air_wing_rows),
]
