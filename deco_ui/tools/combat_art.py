"""The land and naval battle windows (landcombat.gui, navalcombat.gui) at the game's paths and sizes (2026-10-17,
SCREEN_INVENTORY.md's suggestion 5). Textures only: no .gui or .gfx changes.

The game draws its land battle window on one picture (land_battle_bg, 567 x 617) and lays its own pieces over it: the
terrain picture, the two generals' portraits in their frames, their flags, the progress bar, the traits, the two
tactics and the tactics button, the generals' names and skill, each side's combat width, the battle's width, and the
two lists of divisions and reserves. The places are the game's (landcombat.gui; measured from its own picture where
the .gui leaves them open); what is under them is drawn here: lacquer plates with gilt hairlines, a recessed slot under
the terrain picture and under each tactic, a medallion either side of the terrain (the attacker's crossed swords, the
defender's shield: the icon set's, as the minimap's pings), wells under the portraits, a sunburst and speed lines
round the tactics button, each side's width in a readout well, the battle's width in an octagon, and each side's
column of the lists as a recessed field with a faint survey grid. The attacker's side is marked in oxblood, the
defender's in slate blue (the game's red and blue, as its own tactic icons have them): the medallions' inner rings,
the captions' underlines, the progress bar (attacker from the left in oxblood chevrons, the defender's slate behind
it) and its heading marker. Every text the game writes here is light, so everything stays dark lacquer.

The smaller pictures are redrawn at their paths and sizes too: the portrait frame (gilt, its opening clear), the
initiative glow (2 frames the game blends: a jade halo on the frame and a chevron badge), the progress bar's frame and
its two fills, the heading marker (5 frames, the game's order: attacker pushing hard, attacker, even, defender,
defender pushing hard), the skill badge (a lacquer pennant; the game shows it on 11 other screens too), the division
and reserve cards, the tactics button (a chess knight on a gilt octagon), the empty tactic, the countered tactic's
cross, and the tactics list's cards (5 frames, the game's tints kept: slate, oxblood, grey for a locked one, then
slate and oxblood lit for the preferred one). The width brackets (army_width) are left clear: see army_width.

The naval battle: see naval_bg (its picture, 1056 x 736, the map a light plotting sheet under the game's black ship
silhouettes), the admirals' frame, the two progress fills, the screening chips, the map's compass and the six figures'
icons (the game's glyphs in gilt).

gen_textures.py adds them (keys cb_*). Preview: preview_combat.py.
"""
from designer_art import LAC, _layer, _shrink, band, inset, gilt_line
from art_util import chamfer, frames, STRIPES
from icons import icon as _icon

W, H = 567, 617
# the two sides: oxblood (attacker) and slate blue (defender)
ATK = dict(deep="#4A1E19", mid="#7E3228", lit="#A9493A", pale="#E7A493", line="rgba(196,96,80,.85)")
DEF = dict(deep="#16293A", mid="#2C4F6B", lit="#40698B", pale="#A9C7DE", line="rgba(104,150,190,.85)")
DARK = "linear-gradient(180deg,#0B1115,#080C0F)"


def _div(x, y, w, h, style):
    return f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;{style}"></div>'


def _svg(w, h, inner, x=0, y=0):
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="position:absolute;left:{x}px;top:{y}px">'
            f'{inner}</svg>')


def _octagon(cx, cy, r, c=None):
    c = c if c is not None else r * 0.42
    return [(cx - r + c, cy - r), (cx + r - c, cy - r), (cx + r, cy - r + c), (cx + r, cy + r - c),
            (cx + r - c, cy + r), (cx - r + c, cy + r), (cx - r, cy + r - c), (cx - r, cy - r + c)]


def medallion(cx, cy, r, side, glyph):
    """an octagonal lacquer medallion with a gilt rim, an inner ring in the side's colour, a line icon in gilt"""
    o = _octagon(cx, cy, r)
    out = (_layer(o, "linear-gradient(180deg,#E8CD84,#8B6A2C)") + _layer(_octagon(cx, cy, r - 1.4), f"{LAC},linear-gradient(180deg,#18232B,#0B1014)")
           + _layer(_octagon(cx, cy, r - 4), side["line"]) + _layer(_octagon(cx, cy, r - 5), "radial-gradient(circle at 50% 35%,#1A262E,#0B1014 75%)")
           + _layer(_octagon(cx, cy, r - 7.5), "rgba(201,165,90,.35)") + _layer(_octagon(cx, cy, r - 8.5), "radial-gradient(circle at 50% 35%,#16212A,#0A0F12 80%)"))
    s = int(r * 1.1)
    out += f'<div style="position:absolute;left:{cx - s / 2}px;top:{cy - s / 2}px">{_icon(glyph, s, "#E3C77E", 1.5)}</div>'
    return out


def _speed(x0, x1, y, fade_to_right, t=1, col="201,165,90"):
    a, b = (f"rgba({col},.9)", f"rgba({col},0)") if fade_to_right else (f"rgba({col},0)", f"rgba({col},.9)")
    return _div(x0, y, x1 - x0, t, f"background:linear-gradient(90deg,{a},{b})")


def sunburst(cx, cy, r, alpha=.22):
    return _div(cx - r, cy - r, 2 * r, 2 * r,
                f"border-radius:50%;background:repeating-conic-gradient(rgba(227,199,126,{alpha}) 0deg 3deg,transparent 3deg 11deg);"
                "-webkit-mask:radial-gradient(circle,#000 32%,transparent 70%)")


def survey(x0, y0, x1, y1, seed=0):
    """a recessed field with a faint survey grid and contour rings: the lists' ground"""
    w, h = x1 - x0, y1 - y0
    grid = (f"background-image:linear-gradient(rgba(201,165,90,.05) 1px,transparent 1px),"
            f"linear-gradient(90deg,rgba(201,165,90,.05) 1px,transparent 1px);background-size:24px 24px;"
            f"background-position:{(seed * 7) % 24}px 6px")
    # contour rings: a few irregular closed curves round a point, gilt at a whisper
    import math
    cx, cy = w * (0.62 if seed == 0 else 0.38), h * 0.42
    paths = ""
    for k, rad in enumerate((26, 44, 64, 86, 110)):
        pts = []
        for i in range(36):
            t = i / 36 * 2 * math.pi
            wob = 1 + .10 * math.sin(3 * t + seed + k * .7) + .06 * math.sin(5 * t + 1.3 * k + seed * 2)
            pts.append((cx + rad * 1.25 * wob * math.cos(t), cy + rad * .82 * wob * math.sin(t)))
        d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "Z"
        paths += f'<path d="{d}" fill="none" stroke="rgba(201,165,90,{.075 - .009 * k:.3f})" stroke-width="1"/>'
    return (inset((x0, y0, x1, y1), "linear-gradient(180deg,#0D1418,#090D10)")
            + f'<div style="position:absolute;left:{x0 + 1}px;top:{y0 + 1}px;width:{w - 2}px;height:{h - 2}px;overflow:hidden">'
            + f'<div style="position:absolute;inset:0;{grid}"></div>' + _svg(w - 2, h - 2, paths) + '</div>')


def caption(x0, y0, x1, y1, side, outer):
    """a side's caption strip (the game writes "5 Divisions", "2 Reserves" on it): a chamfered lacquer bar, a hairline
    in the side's colour under it, a small diamond at its outer end"""
    c = 5
    pts = [(x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1), (x0, y1), (x0, y0 + c)]
    dx = x0 + 9 if outer == "left" else x1 - 15
    return (_layer(pts, "rgba(201,165,90,.55)") + _layer([(x0 + c + .4, y0 + 1), (x1 - c - .4, y0 + 1), (x1 - 1, y0 + c + .4), (x1 - 1, y1), (x0 + 1, y1), (x0 + 1, y0 + c + .4)],
                                                          f"{STRIPES},linear-gradient(180deg,#1C2830,#121B21)")
            + _div(x0 + c + 3, y0 + 2, x1 - x0 - 2 * c - 6, 1, "background:rgba(241,220,156,.2)")
            + _div(x0 + 1, y1 - 2, x1 - x0 - 2, 2, f"background:{side['line']}")
            + _div(dx, (y0 + y1) / 2 - 3.5, 6, 6, f"background:{side['line']};transform:rotate(45deg);box-shadow:0 0 0 1px rgba(11,16,20,.8)"))


# ---------------------------------------------------------------- the window
def land_bg(w=W, h=H):
    out = (f'<div style="position:absolute;inset:0;background:{LAC},linear-gradient(180deg,#141E24,#0D1418)"></div>'
           '<div style="position:absolute;inset:0;box-shadow:inset 0 0 0 1px rgba(0,0,0,.7)"></div>'
           '<div style="position:absolute;inset:1px;border:1px solid #B8954F"></div>'
           '<div style="position:absolute;inset:5px;border:1px solid rgba(201,165,90,.4)"></div>'
           '<i class="ck tl"></i><i class="ck bl"></i><i class="ck br"></i>')
    # the title band (the game's title is centred in x 55-505, y 2) and the socket of the game's small close button
    # (UPPER_RIGHT -34, 5: x 533-559, y 5-31)
    out += band(6, 6, w - 6, 33) + gilt_line(6, 33, w - 6, 33, "rgba(201,165,90,.85)")
    out += inset((530, 4, 562, 33), "linear-gradient(180deg,#0E1519,#0A0F12)", "rgba(201,165,90,.75)")
    # a diamond either side of the title's box (a long title fills it)
    for x in (40, 521):
        out += _div(x, 16.5, 6, 6, "background:#C9A55A;transform:rotate(45deg)")
    # the terrain picture (77, 37; 413 x 70) in a gilt-rimmed slot, the medallions either side
    out += inset((76, 36, 491, 108), DARK, "rgba(227,199,126,.9)")
    out += medallion(39.5, 72, 29, ATK, "swords") + medallion(527.5, 72, 29, DEF, "shield")
    # the generals: dark wells under the portraits and their frames (5-89 and 478-562, y 110-221)
    out += _div(5, 110, 84, 111, "background:#0A0F12") + _div(478, 110, 84, 111, "background:#0A0F12")
    # the flags (90 and 436, y 111; the game's thin frame round them, 47 x 32 at 87 and 433): a gilt hairline round it
    for fx in (86, 432):
        out += _div(fx, 108, 49, 34, "box-shadow:0 0 0 1px rgba(201,165,90,.85);background:#0A0F12")
    # speed lines from the flags to the progress bar (183-368, y 114-134; the bar's middle at y 124)
    for dy, ln in ((-4, 40), (0, 46), (4, 40)):
        out += _speed(138, 138 + ln, 124 + dy, True) + _speed(429 - ln - 58 + 46, 429, 124 + dy, False)
    # the stepped plate: traits (y 148-173; the attacker's from x 100, the defender's to 470) and tactics (y 183-230)
    plate = [(100, 142), (467, 142), (475, 150), (475, 232), (92, 232), (92, 150)]
    out += (_layer(plate, "rgba(201,165,90,.6)") + _layer([(100.4, 143), (466.6, 143), (474, 150.4), (474, 232), (93, 232), (93, 150.4)],
                                                           f"{LAC},linear-gradient(180deg,#1B272F,#121A20)")
            + _div(104, 144, 359, 1, "background:rgba(241,220,156,.22)"))
    out += gilt_line(96, 178, 471, 178, "rgba(201,165,90,.5)") + _div(96, 179, 375, 1, "background:rgba(0,0,0,.5)")
    out += _layer([(93, 179), (474, 179), (474, 232), (93, 232)], "linear-gradient(180deg,rgba(0,0,0,.28),rgba(0,0,0,0) 22px)")
    # tactic slots (89 x 47 at 100 and 378, y 183) and the tactics button's ground (46 x 46 at 261, 184)
    out += inset((99, 182, 190, 231), DARK, "rgba(227,199,126,.85)") + inset((377, 182, 468, 231), DARK, "rgba(227,199,126,.85)")
    out += sunburst(284, 207, 46)
    for dy, ln in ((-6, 56), (0, 62), (6, 50)):
        out += _speed(260 - ln, 258, 207 + dy, False) + _speed(310, 310 + ln, 207 + dy, True)
    for x in (250, 314):
        out += _div(x, 203, 7, 7, "background:#E3C77E;transform:rotate(45deg)")
    # the names and skills band (names y 233; skill badges 35 x 50 at 230 and 304, y 230), the widths' row under it
    out += band(6, 233, w - 6, 306) + gilt_line(6, 306, w - 6, 306, "rgba(201,165,90,.85)")
    out += gilt_line(12, 276, 222, 276, "rgba(201,165,90,.35)") + gilt_line(345, 276, w - 12, 276, "rgba(201,165,90,.35)")
    # each side's width (the value centred on 137 / 425, y 284) in a readout well with the width's arrowheads at its
    # ends (the game's own arrows, army_width, sit under the value: see army_width)
    for x0 in (62, 350):
        out += inset((x0, 281, x0 + 150, 304), DARK, "rgba(201,165,90,.5)")
        out += _svg(150, 23, '<path d="M9 7.5L4.5 11.5L9 15.5ZM141 7.5L145.5 11.5L141 15.5Z" fill="#C9A55A"/>', x0, 281)
    # the battle's width (centred on 284.5, y 277-300) in a gilt octagon on the band's edge
    out += (_layer(_octagon(284.5, 289, 20), "linear-gradient(180deg,#E8CD84,#8B6A2C)")
            + _layer(_octagon(284.5, 289, 18.6), "radial-gradient(circle at 50% 35%,#1C2830,#0B1014 75%)")
            + _layer(_octagon(284.5, 289, 16), "rgba(201,165,90,.4)") + _layer(_octagon(284.5, 289, 15), "radial-gradient(circle at 50% 30%,#16212A,#0A0F12 80%)"))
    for x in (258, 305):
        out += _div(x, 285.5, 6, 6, "background:#C9A55A;transform:rotate(45deg)")
    # the lists: each side a column (the attacker's cards at 41-280, clipped at 280; the defender's at 305-549):
    # caption (y 309-329), the divisions (from y 329), the reserves' caption (y 494-514), the reserves (from 515)
    for (x0, x1, side, outer, seed) in ((10, 281, ATK, "left", 0), (289, 557, DEF, "right", 1)):
        out += caption(x0, 308, x1, 329, side, outer)
        out += survey(x0, 329, x1, 494, seed)
        out += caption(x0, 494, x1, 515, side, outer)
        out += survey(x0, 515, x1, 604, seed + 2)
    out += gilt_line(285, 312, 285, 600, "rgba(201,165,90,.35)")
    return out


# ---------------------------------------------------------------- the generals
def leader_frame(w=84, h=111):
    """the portrait's frame (at 5, 110; the portrait, 78 x 105, at 4 / 3, 2 inside it): a gilt rim, lacquer, a gilt
    hairline round the opening (4-80, 4-107), small brackets in its corners; the opening clear"""
    o = (4, 4, 80, 107)
    # the lacquer border, four strips round the opening
    out = (_div(0, 0, w, o[1], f"background:{LAC},#121B21") + _div(0, o[3], w, h - o[3], f"background:{LAC},#121B21")
           + _div(0, o[1], o[0], o[3] - o[1], "background:#121B21") + _div(o[2], o[1], w - o[2], o[3] - o[1], "background:#121B21"))
    out += ('<div style="position:absolute;inset:0;box-shadow:inset 0 0 0 1px #B8954F"></div>'
            + _div(o[0] - 1, o[1] - 1, o[2] - o[0] + 2, o[3] - o[1] + 2, "box-shadow:inset 0 0 0 1px #E3C77E"))
    for (x, y, sx, sy) in ((o[0], o[1], 1, 1), (o[2], o[1], -1, 1), (o[0], o[3], 1, -1), (o[2], o[3], -1, -1)):
        out += _svg(9, 9, f'<path d="M1.5 8V1.5H8" fill="none" stroke="#E3C77E" stroke-width="1.4" '
                          f'transform="translate({4.5 - 4.5 * sx} {4.5 - 4.5 * sy}) scale({sx} {sy})"/>',
                    x + (1 if sx > 0 else -10), y + (1 if sy > 0 else -10))
    return out


def initiative_glow(w=174, h=118):
    """the initiative glow (2 frames the game blends): a jade halo on the frame's rim (the frame at 1 or 2, 2 in it,
    84 x 111) and a chevron badge at its foot"""
    def one(a):
        rim = (f'<div style="position:absolute;left:2px;top:3px;width:83px;height:109px;'
               f'box-shadow:0 0 0 1.5px rgba(127,211,184,{a}),0 0 6px 2px rgba(63,164,136,{a * .7}),inset 0 0 6px 1px rgba(63,164,136,{a * .55})"></div>')
        badge = (f'<div style="position:absolute;left:{43.5 - 9}px;top:98px;width:18px;height:18px;transform:rotate(45deg);'
                 f'background:linear-gradient(180deg,#2C665A,#163A33);box-shadow:0 0 0 1px rgba(227,199,126,{.6 + .4 * a}),0 0 6px rgba(63,164,136,{a * .8})"></div>'
                 + _svg(18, 18, f'<path d="M4.5 9.5L9 5.5l4.5 4M4.5 13.5L9 9.5l4.5 4" fill="none" stroke="#F1DC9C" '
                                f'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" opacity="{.75 + .25 * a}"/>', 34.5, 98))
        return rim + badge
    return frames(w, h, one(.7), one(1.0))


def skill_badge(w=35, h=50):
    """a commander's skill (the game writes the number at 2-32, 8-22; its digits' middle at y 19.5 in the mod's font,
    the game's ring at 17): a lacquer pennant with a gilt rim and a point,
    a gilt ring round the number, two rank chevrons under it. The game shows the same picture on 11 other screens (the
    army and fleet badges at 0.7, the trait trees, the faction, diplomacy and organisation screens)"""
    pen = [(3.5, 1), (31.5, 1), (31.5, 41), (17.5, 49), (3.5, 41)]
    return (_layer(pen, "linear-gradient(180deg,#E8CD84,#8B6A2C)")
            + _layer([(4.9, 2.4), (30.1, 2.4), (30.1, 40.1), (17.5, 47.3), (4.9, 40.1)], f"{LAC},linear-gradient(180deg,#1C2830,#0B1014)")
            + _svg(w, h, '<circle cx="17.5" cy="18.5" r="10.4" fill="#0A0F12" stroke="#C9A55A" stroke-width="1.2"/>'
                         '<circle cx="17.5" cy="18.5" r="8.4" fill="none" stroke="rgba(201,165,90,.35)" stroke-width=".8"/>'
                         '<path d="M12 32.5l5.5 3.2 5.5-3.2M12 37l5.5 3.2 5.5-3.2" fill="none" stroke="#E3C77E" stroke-width="1.4" '
                         'stroke-linecap="round" stroke-linejoin="round"/>'))


# ---------------------------------------------------------------- the progress bar
def progress_frame(w=185, h=20):
    """the bar's frame (at 183, 114; the bar, 179 x 14, at 2, 2 in it): its opening 4-181 x 4-16 clear"""
    o = (4, 4, 181, 16)
    border = (_div(0, 0, w, o[1], f"background:{LAC},#111A20") + _div(0, o[3], w, h - o[3], f"background:{LAC},#111A20")
              + _div(0, o[1], o[0], o[3] - o[1], "background:#111A20") + _div(o[2], o[1], w - o[2], o[3] - o[1], "background:#111A20"))
    return (border + '<div style="position:absolute;inset:0;box-shadow:inset 0 0 0 1px #B8954F"></div>'
            + _div(o[0] - 1, o[1] - 1, o[2] - o[0] + 2, o[3] - o[1] + 2, "box-shadow:inset 0 0 0 1px #E3C77E")
            + _div(3, 1.5, w - 6, 1, "background:rgba(241,220,156,.18)"))


def progress_fill(side, right):
    """a side's fill (179 x 14): its colour, lit from above, chevrons pointing its way, faintly"""
    d = "M0 0L5 7L0 14" if right else "M5 0L0 7L5 14"
    pat = "".join(f'<path d="{d}" transform="translate({x} 0)" fill="none" stroke="rgba(255,236,214,.16)" stroke-width="2.2"/>'
                  for x in range(-6, 185, 9))
    return (_div(0, 0, 179, 14, f"background:linear-gradient(180deg,{side['lit']},{side['mid']} 55%,{side['deep']})")
            + _svg(179, 14, pat) + _div(0, 0, 179, 1, "background:rgba(255,240,220,.28)")
            + _div(0, 13, 179, 1, "background:rgba(0,0,0,.35)"))


def heading_strip(w=60, h=16):
    """the marker on the bar (5 frames, the game's order): attacker pushing hard, attacker, even, defender, defender
    pushing hard"""
    def chev(paths, col):
        return _svg(12, 16, "".join(f'<path d="{p}" fill="none" stroke="#0B1014" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
                                    for p in paths)
                    + "".join(f'<path d="{p}" fill="none" stroke="{col}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
                              for p in paths))
    even = _svg(12, 16, '<path d="M1.2 3L5.6 8L1.2 13Z" fill="#E7A493" stroke="#0B1014" stroke-width="1.2" stroke-linejoin="round"/>'
                        '<path d="M10.8 3L6.4 8L10.8 13Z" fill="#A9C7DE" stroke="#0B1014" stroke-width="1.2" stroke-linejoin="round"/>')
    return frames(w, h, chev(["M2.5 3.5L6 8L2.5 12.5", "M6.5 3.5L10 8L6.5 12.5"], ATK["pale"]),
                  chev(["M4.5 3.5L8 8L4.5 12.5"], ATK["pale"]), even,
                  chev(["M7.5 3.5L4 8L7.5 12.5"], DEF["pale"]),
                  chev(["M9.5 3.5L6 8L9.5 12.5", "M5.5 3.5L2 8L5.5 12.5"], DEF["pale"]))


def army_width(w=40, h=19):
    """the brackets round a side's width (40 x 19 at 117 / 405, y 285): the game centres the value on them and draws
    it over them, and the deco font's "70/80" (about 38 px) covers them both; so this picture is left clear (its
    tooltip stays, the game's icon keeps its place) and the brackets are drawn into the window's picture at the ends
    of each side's readout well instead"""
    return ""


# ---------------------------------------------------------------- the lists' cards
def card(w, h, c=4):
    """a division's or a reserve's card (the attacker's and the defender's are the same picture, mirrored by the
    game's layout): a chamfered lacquer plate with a gilt hairline, lit along its top"""
    return (f'<div style="position:absolute;inset:0;background:rgba(201,165,90,.6);clip-path:{chamfer(c)}"></div>'
            f'<div style="position:absolute;inset:1px;clip-path:{chamfer(c - .4)};background:{STRIPES},linear-gradient(180deg,#1D2931,#121A20 55%,#0D1418)"></div>'
            f'<div style="position:absolute;left:{c + 2}px;right:{c + 2}px;top:2px;height:1px;background:rgba(241,220,156,.22)"></div>')


# ---------------------------------------------------------------- the tactics
KNIGHT = ('<path d="M7.5 20.5h10M8.5 18h8"/>'
          '<path d="M9.3 18c-.3-2.6.9-4.2 2.7-5.8l-3.4 1.4c-.9.4-1.8 0-2.1-.8l-.3-.7c-.2-.6 0-1.2.5-1.6l4.4-4.1'
          'c.5-1.6 1.6-2.7 3.1-2.9l.7-1.5 1 1.9c2.3 1.2 3.5 3.7 3.5 6.6 0 3.3-.8 5.6-1.3 7.5"/>'
          '<circle cx="12.6" cy="8.6" r=".7" fill="currentColor" stroke="none"/>')


def tactics_button(w=46, h=46):
    """the button that opens the tactics list (46 x 46 at 261, 184): a gilt octagon, a chess knight in line art"""
    o = _octagon(23, 23, 22.5, 9.4)
    return (_layer(o, "linear-gradient(180deg,#E8CD84,#8B6A2C)") + _layer(_octagon(23, 23, 21.1, 8.8), "radial-gradient(circle at 50% 30%,#22313A,#0E1519 70%)")
            + _layer(_octagon(23, 23, 18.6, 7.8), "rgba(201,165,90,.45)") + _layer(_octagon(23, 23, 17.6, 7.4), "radial-gradient(circle at 50% 30%,#1B272F,#0B1014 75%)")
            + '<div style="position:absolute;left:8px;top:7.5px">'
            + f'<svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#E3C77E" stroke-width="1.45" stroke-linecap="round" '
              f'stroke-linejoin="round" style="display:block;color:#E3C77E">{KNIGHT}</svg></div>')


def no_tactic(w=89, h=47):
    """the empty tactic (before one is drawn): dark lacquer, a faint hatch, an hourglass in dim gilt"""
    glass = ('<path d="M7 3.5h10M7 20.5h10M8 3.5c0 4.5 3.5 6 4 8.5.5-2.5 4-4 4-8.5M8 20.5c0-4.5 3.5-6 4-8.5.5 2.5 4 4 4 8.5"/>'
             '<path d="M10 18.5h4" stroke-width="2"/>')
    return (_div(0, 0, w, h, "background:repeating-linear-gradient(135deg,rgba(201,165,90,.06) 0 1px,transparent 1px 7px),linear-gradient(180deg,#141E24,#0B1014)")
            + f'<div style="position:absolute;left:{w / 2 - 11}px;top:{h / 2 - 11}px">'
              f'<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="rgba(227,199,126,.75)" stroke-width="1.5" '
              f'stroke-linecap="round" stroke-linejoin="round" style="display:block">{glass}</svg></div>'
            + _speed(8, 30, 23, False, col="201,165,90") + _speed(w - 30, w - 8, 23, True))


def countered(w=85, h=43):
    """a countered tactic (over its picture: 85 x 43 at 2, 2 in the slot): the picture dimmed, a coral cross"""
    x = ("M14 6L71 37M71 6L14 37")
    return (_div(0, 0, w, h, "background:rgba(8,12,15,.55)")
            + _div(0, 0, w, h, "box-shadow:inset 0 0 0 1px rgba(238,140,126,.7)")
            + _svg(w, h, f'<path d="{x}" stroke="#0B1014" stroke-width="5.5" stroke-linecap="round"/>'
                         f'<path d="{x}" stroke="rgb(238,140,126)" stroke-width="2.6" stroke-linecap="round"/>'))


def tactic_entry(tint, state):
    """a card of the tactics list (354 x 94; the game's container is 350): the name band (name at 14, 6; phase right,
    to 335), a slot for the tactic's picture (89 x 47 at 15, 33), the figures right of it on the plate. tint: the
    game's slate or oxblood (None: the grey of a locked tactic); state: lit (the preferred tactic)"""
    w, h, c = 354, 92, 6        # the plate; the picture is 94 tall, the 2 px under the plate clear (the game stacks
    #                             the cards 94 apart, so each stands apart from the next)
    rim = "linear-gradient(180deg,#F1DC9C,#B8954F)" if state else ("rgba(201,165,90,.35)" if tint is None else "rgba(201,165,90,.6)")
    if tint is None:
        body = "linear-gradient(180deg,#1A1F22,#121618 60%,#0E1113)"
    else:
        body = f"linear-gradient(180deg,{tint['mid']}66,{tint['deep']}88 55%,#0D141899),linear-gradient(180deg,#141E24,#0D1418)"
    out = (f'<div style="position:absolute;left:0;top:0;width:{w}px;height:{h}px;background:{rim};clip-path:{chamfer(c)}"></div>'
           f'<div style="position:absolute;left:1px;top:1px;width:{w - 2}px;height:{h - 2}px;clip-path:{chamfer(c - .4)};background:{STRIPES},{body}"></div>'
           f'<div style="position:absolute;left:1px;top:1px;right:1px;height:26px;clip-path:polygon({c - .4}px 0,calc(100% - {c - .4}px) 0,100% {c - .4}px,100% 100%,0 100%,0 {c - .4}px);'
           f'background:{STRIPES},linear-gradient(180deg,#121A20,#0B1014)"></div>'
           + _div(1, 27, w - 2, 1, f"background:{'#E3C77E' if state else 'rgba(201,165,90,.55)'}")
           + _div(c + 3, 2, w - 2 * c - 6, 1, "background:rgba(241,220,156,.18)")
           + inset((14, 32, 105, 81), DARK, "rgba(227,199,126,.8)" if tint is not None else "rgba(201,165,90,.45)"))
    if state:
        out += (_div(1, 26, w - 2, 3, "background:linear-gradient(90deg,rgba(241,220,156,0),rgba(241,220,156,.55) 20%,rgba(241,220,156,.55) 80%,rgba(241,220,156,0));filter:blur(1px)")
                + _div(c + 2, h - 4, w - 2 * c - 4, 2, "background:linear-gradient(90deg,rgba(241,220,156,0),#F1DC9C 20%,#F1DC9C 80%,rgba(241,220,156,0))"))
    return out


def tactics_entries(w=1770, h=94):
    return frames(w, h, tactic_entry(DEF, False), tactic_entry(ATK, False), tactic_entry(None, False),
                  tactic_entry(DEF, True), tactic_entry(ATK, True))



# ---------------------------------------------------------------- the naval battle (navalcombat.gui)
# The window's picture (naval_battle_bg2, 1056 x 736; the window is centred at (-528, -356)): the game's silhouette
# (a title tab, the header, the wide middle with the side panels, the foot) and its places, measured from its picture
# and navalcombat.gui (the header container at x 125): the title and close (y 8-46), the admirals' frames (140 and
# 835, y 53), their four figures (x 215-305 and 749-838, y 57-103), the weather picture (486 x 63 at 323, 55), the
# progress bar (351 x 14 at 352 / 355, y 133), the names (y 168), the flags (frames at 339 and 667, y 158), the
# disengage button (512, 155), the six stat boxes a side (y 193-235), the screening chips (y 237), the battle map
# (x 132-924, y 244-612: the ships' columns, the front at x 528, the submarines' band from y 520), the back fields
# either side (x 4-130 and 926-1051) and the sunk ships' wells (y 628-718). The ships are black silhouettes with a
# white rim, so the map stays a light plotting sheet (ivory, sepia grid), its back fields a shaded ivory; the rest is
# lacquer.
NW, NH = 1056, 736
NAVAL_SHAPE = [(292, 3), (763, 3), (768, 8), (768, 30), (776, 38), (926, 38), (931, 43), (931, 235), (1046, 235),
               (1051, 240), (1051, 620), (1046, 625), (932, 625), (932, 727), (927, 732), (130, 732), (125, 727),
               (125, 625), (9, 625), (4, 620), (4, 240), (9, 235), (124, 235), (124, 43), (129, 38), (279, 38),
               (287, 30), (287, 8)]
IVORY = "radial-gradient(ellipse at 40% 30%,rgba(255,250,235,.5),rgba(255,250,235,0) 65%),linear-gradient(180deg,#EDE3CA,#DFD1AC)"
SEPIA = "92,70,32"


def _waves(w, y, period, amp, shift=0):
    """a smooth wave line across w px: one quadratic curve, then reflections of it (T), every half period"""
    x = -shift
    d = f"M{x} {y} Q{x + period / 4} {y - amp} {x + period / 2} {y}"
    x += period / 2
    while x < w + period:
        x += period / 2
        d += f" T{x} {y}"
    return d


def plotting_sheet(x0, y0, x1, y1, shade=0.0, grid=24, water_from=None):
    """an ivory plotting sheet with a sepia rim and a faint square grid; shade darkens it (the back fields);
    water_from: a slate-washed band from that y down (the submarines')"""
    w, h = x1 - x0, y1 - y0
    out = (_div(x0 - 1, y0 - 1, w + 2, h + 2, "background:#8A6C30")
           + _div(x0, y0, w, h, f"background:{IVORY}")
           + _div(x0, y0, w, h, f"background-image:linear-gradient(rgba({SEPIA},.10) 1px,transparent 1px),"
                                f"linear-gradient(90deg,rgba({SEPIA},.10) 1px,transparent 1px);background-size:{grid}px {grid}px;"
                                f"background-position:{(528 - x0) % grid}px 0"))
    if shade:
        out += _div(x0, y0, w, h, f"background:rgba(60,46,22,{shade})")
    if water_from:
        out += (_div(x0, water_from, w, y1 - water_from, "background:linear-gradient(180deg,rgba(64,105,139,.20),rgba(44,79,107,.34))")
                + _svg(w, y1 - water_from, "".join(
                    f'<path d="{_waves(w, yy, 30, 2.2, k * 15)}" fill="none" stroke="rgba(44,79,107,.22)" stroke-width="1"/>'
                    for k, yy in enumerate(range(16, y1 - water_from, 20))), x0, water_from)
                + _div(x0, water_from, w, 2, f"background-image:radial-gradient(circle,rgba({SEPIA},.6) .8px,transparent 1px);background-size:5px 2px"))
    return out + _div(x0, y0, w, h, "box-shadow:inset 0 0 0 1px rgba(255,250,235,.35),inset 0 0 18px rgba(92,70,32,.22)")


def dotted_v(x, y0, y1, col=f"rgba({SEPIA},.55)", step=6):
    return _div(x - 1, y0, 2, y1 - y0, f"background-image:radial-gradient(circle,{col} .9px,transparent 1.1px);background-size:2px {step}px")


def naval_bg(w=NW, h=NH):
    shape = NAVAL_SHAPE
    out = (_layer(shape, "#B8954F") + _layer(_shrink(shape, 1), f"{LAC},linear-gradient(180deg,#141E24,#0D1418)")
           + _layer(_shrink(shape, 5), "rgba(201,165,90,.4)") + _layer(_shrink(shape, 6), f"{LAC},linear-gradient(180deg,#141E24,#0D1418)"))
    # the title (the game's at 305, 14; 420 wide) on a plate in the tab, the close button's socket at its right end
    out += inset((294, 8, 762, 46), "linear-gradient(180deg,#0E1519,#090D10)", "rgba(227,199,126,.85)")
    out += inset((724, 9, 761, 45), "linear-gradient(180deg,#121B21,#0B1014)", "rgba(201,165,90,.6)")
    for x in (300, 712):
        out += _div(x, 24, 6, 6, "background:#C9A55A;transform:rotate(45deg)")
    # the admirals: dark wells under the portraits (their frames, 81 x 107, at 140 and 835, y 53)
    out += _div(140, 53, 81, 107, "background:#0A0F12") + _div(835, 53, 81, 107, "background:#0A0F12")
    # the weather picture (486 x 63 at 323, 55) in a gilt slot
    out += inset((322, 54, 810, 119), DARK, "rgba(227,199,126,.9)")
    # the progress bar's track (the bars 351 x 14 at 352 and 355, y 133): a gilt rim round both
    out += (_div(347, 128, 365, 24, "background:#B8954F;clip-path:" + chamfer(4))
            + _div(348, 129, 363, 22, f"background:{LAC},#0E151A;clip-path:" + chamfer(3.6))
            + _div(350, 131, 359, 18, "box-shadow:inset 0 0 0 1px #E3C77E;background:#080C0F"))
    # the names (y 168: the attacker's from 149, the defender's to 909) on dark bars, the flags' frames gilt-ringed
    out += inset((142, 164, 336, 191), DARK, "rgba(201,165,90,.55)") + inset((722, 164, 914, 191), DARK, "rgba(201,165,90,.55)")
    for fx in (338, 666):
        out += _div(fx, 157, 54, 40, "box-shadow:0 0 0 1px rgba(201,165,90,.85);background:#0A0F12")
    # the middle plate under the disengage button (31 x 31 at 512, 155) and the carriers' penalty marks (400, 620)
    plate = [(404, 152), (652, 152), (668, 168), (668, 235), (388, 235), (388, 168)]
    out += (_layer(plate, "rgba(201,165,90,.6)") + _layer(_shrink(plate, 1), f"{LAC},linear-gradient(180deg,#1C2830,#121A20)")
            + _div(410, 153, 236, 1, "background:rgba(241,220,156,.22)"))
    out += inset((508, 151, 548, 191), "linear-gradient(180deg,#0E1519,#0A0F12)", "rgba(227,199,126,.8)")
    out += sunburst(528, 171, 40, .16)
    for dy, ln in ((-4, 40), (0, 52), (4, 40)):
        out += _speed(500 - ln, 500, 171 + dy, False) + _speed(556, 556 + ln, 171 + dy, True)
    # the six stat boxes a side (icons 26 x 26 at y 196, the figures under them to y 240)
    for x0 in (143, 182, 223, 263, 303, 346, 674, 717, 757, 797, 837, 877):
        out += inset((x0, 193, x0 + 38, 235), "linear-gradient(180deg,#101820,#090D10)", "rgba(201,165,90,.5)")
    out += gilt_line(130, 235, 926, 235, "rgba(201,165,90,.8)")
    # the battle map: the back fields, the sheet, the columns' rules, the front
    out += plotting_sheet(14, 246, 124, 614, shade=.20) + plotting_sheet(932, 246, 1042, 614, shade=.20)
    out += plotting_sheet(134, 246, 922, 612, water_from=520)
    for x in (260, 406, 650, 796):
        out += dotted_v(x, 250, 518)
    out += _div(527, 246, 2, 366, "background:repeating-linear-gradient(180deg,rgba(126,50,40,.85) 0 7px,transparent 7px 11px)")
    out += (_layer(_octagon(528, 405, 15), "linear-gradient(180deg,#E8CD84,#8B6A2C)") + _layer(_octagon(528, 405, 13.8), "radial-gradient(circle at 50% 35%,#1C2830,#0B1014 75%)")
            + f'<div style="position:absolute;left:{528 - 10}px;top:{405 - 10}px">{_icon("swords", 20, "#E3C77E", 1.6)}</div>')
    # the sunk ships' wells (the lists at 185-525 and 529-867, y 632-714)
    for x0, x1 in ((140, 525), (531, 916)):
        out += inset((x0, 628, x1, 720), "linear-gradient(180deg,#0B1216,#060A0C)", "rgba(201,165,90,.6)")
        out += _svg(x1 - x0 - 2, 90, "".join(f'<path d="{_waves(x1 - x0, yy, 40, 3, k * 20)}" fill="none" '
                                             f'stroke="rgba(104,150,190,{.10 - .015 * k:.3f})" stroke-width="1"/>'
                                             for k, yy in enumerate(range(20, 90, 16))), x0 + 1, 629)
    out += gilt_line(527, 626, 527, 724, "rgba(201,165,90,.5)") + gilt_line(130, 625, 926, 625, "rgba(201,165,90,.8)")
    return out


def naval_leader_frame(w=81, h=107):
    """an admiral's frame (at 15, 53 in the header; the portrait, 70 x 94.5 at 0.45, at 5, 6 in it; the naval results
    window shows it too): as the generals', its opening 5-76 x 6-101 clear"""
    o = (5, 6, 76, 101)
    out = (_div(0, 0, w, o[1], f"background:{LAC},#121B21") + _div(0, o[3], w, h - o[3], f"background:{LAC},#121B21")
           + _div(0, o[1], o[0], o[3] - o[1], "background:#121B21") + _div(o[2], o[1], w - o[2], o[3] - o[1], "background:#121B21"))
    out += ('<div style="position:absolute;inset:0;box-shadow:inset 0 0 0 1px #B8954F"></div>'
            + _div(2, 2, w - 4, h - 4, "box-shadow:inset 0 0 0 1px rgba(201,165,90,.35)")
            + _div(o[0] - 1, o[1] - 1, o[2] - o[0] + 2, o[3] - o[1] + 2, "box-shadow:inset 0 0 0 1px #E3C77E"))
    for (x, y, sx, sy) in ((o[0], o[1], 1, 1), (o[2], o[1], -1, 1), (o[0], o[3], 1, -1), (o[2], o[3], -1, -1)):
        out += _svg(9, 9, f'<path d="M1.5 8V1.5H8" fill="none" stroke="#E3C77E" stroke-width="1.4" '
                          f'transform="translate({4.5 - 4.5 * sx} {4.5 - 4.5 * sy}) scale({sx} {sy})"/>',
                    x + (1 if sx > 0 else -10), y + (1 if sy > 0 else -10))
    return out


def naval_progress(side, right, w=351):
    d = "M0 0L5 7L0 14" if right else "M5 0L0 7L5 14"
    pat = "".join(f'<path d="{d}" transform="translate({x} 0)" fill="none" stroke="rgba(255,236,214,.16)" stroke-width="2.2"/>'
                  for x in range(-6, w + 6, 9))
    return (_div(0, 0, w, 14, f"background:linear-gradient(180deg,{side['lit']},{side['mid']} 55%,{side['deep']})")
            + _svg(w, 14, pat) + _div(0, 0, w, 1, "background:rgba(255,240,220,.28)") + _div(0, 13, w, 1, "background:rgba(0,0,0,.35)"))


SHIELD = '<path d="M12 3.2l7.2 2.6v5.4c0 4.6-3 8.1-7.2 9.6-4.2-1.5-7.2-5-7.2-9.6V5.8z"/>'


def screening_chips(w=248, h=27):
    """the screening figures' chips (4 frames, the game's order: a gilt shield (the capital ships') on the left, a
    steel one (the carriers') on the left, steel on the right, gilt on the right; the figure beside it)"""
    def chip(col, left):
        sx = 2 if left else 62 - 20
        return ('<div style="position:absolute;left:0;top:1px;width:62px;height:25px;background:rgba(201,165,90,.6);clip-path:' + chamfer(4) + '"></div>'
                '<div style="position:absolute;left:1px;top:2px;width:60px;height:23px;clip-path:' + chamfer(3.6) + f';background:{STRIPES},linear-gradient(180deg,#1C2830,#0E1519)"></div>'
                f'<div style="position:absolute;left:{sx}px;top:4px"><svg width="19" height="19" viewBox="0 0 24 24" fill="rgba(11,16,20,.6)" stroke="{col}" '
                f'stroke-width="1.8" stroke-linejoin="round" style="display:block">{SHIELD}</svg></div>')
    return frames(w, h, chip("#E3C77E", True), chip("#B9CCDA", True), chip("#B9CCDA", False), chip("#E3C77E", False))


def compass(w=438, h=61):
    """the map's overlay (at 133, 251): the game's faint stains dropped, a compass rose in sepia line art where its
    compass is (36, 37)"""
    cx, cy = 36, 37
    pts = []
    import math
    for i in range(16):
        a = i * math.pi / 8 - math.pi / 2
        r = 16 if i % 4 == 0 else (10 if i % 2 == 0 else 5)
        pts.append(f"{cx + r * math.cos(a):.2f} {cy + r * math.sin(a):.2f}")
    star = "M" + " L".join(pts) + "Z"
    return _svg(w, h, f'<circle cx="{cx}" cy="{cy}" r="12.5" fill="none" stroke="rgba({SEPIA},.55)" stroke-width="1"/>'
                      f'<circle cx="{cx}" cy="{cy}" r="14.5" fill="none" stroke="rgba({SEPIA},.3)" stroke-width=".8"/>'
                      f'<path d="{star}" fill="rgba({SEPIA},.12)" stroke="rgba({SEPIA},.75)" stroke-width="1" stroke-linejoin="round"/>'
                      f'<path d="M{cx} {cy - 16}L{cx + 2.4} {cy - 3}L{cx} {cy}Z" fill="rgba(126,50,40,.75)"/>'
                      f'<circle cx="{cx}" cy="{cy}" r="1.6" fill="rgba({SEPIA},.8)"/>')


def naval_stats(w=156, h=26):
    """the six figures' icons (positioning, light guns, heavy guns, torpedoes, anti-air, depth charges: the game's
    glyphs and order, in gilt; the ship designer shows them too)"""
    from art_util import vanilla_frames, gilt, img_tag
    fr = vanilla_frames("gfx/interface/navalcombat/combat_stat_icons.dds", 6)
    return "".join(img_tag(gilt(f, 1.05), i * 26, 0) for i, f in enumerate(fr))

ADDS = [
    ("cb_land_bg", "gfx/interface/land_battle_bg.dds", 567, 617, land_bg),
    ("cb_leader_frame", "gfx/interface/land_battle_leader_frame.dds", 84, 111, leader_frame),
    ("cb_initiative_glow", "gfx/interface/leader_initiative_overlay_glow.dds", 174, 118, initiative_glow),
    ("cb_progress_frame", "gfx/interface/land_battle_progress_frame.dds", 185, 20, progress_frame),
    ("cb_progress_attacker", "gfx/interface/landcombat_attacker_progress.dds", 179, 14, lambda: progress_fill(ATK, True)),
    ("cb_progress_defender", "gfx/interface/landcombat_defender_progress.dds", 179, 14, lambda: progress_fill(DEF, False)),
    ("cb_heading", "gfx/interface/land_battle_heading_indicator_strip.dds", 60, 16, heading_strip),
    ("cb_army_width", "gfx/interface/army_width.dds", 40, 19, army_width),
    ("cb_skill_badge", "gfx/interface/land_battle_leader_skill_bg.dds", 35, 50, skill_badge),
    ("cb_unit_card", "gfx/interface/land_battle_unit_bg.dds", 244, 43, lambda: card(244, 43, 5)),
    ("cb_reserve_card", "gfx/interface/land_battle_reserve_bg.dds", 119, 29, lambda: card(119, 29, 4)),
    ("cb_tactics_button", "gfx/interface/tactics_icon.dds", 46, 46, tactics_button),
    ("cb_no_tactic", "gfx/interface/landcombat/tactics/no_tactic.dds", 89, 47, no_tactic),
    ("cb_countered", "gfx/interface/landcombat/tactics/countered_tactic_overlay.dds", 85, 43, countered),
    ("cb_tactic_entry", "gfx/interface/tactics_list_entry_bg.dds", 1770, 94, tactics_entries),
    # the naval battle
    ("cb_naval_bg", "gfx/interface/navalcombat/naval_battle_bg2.dds", NW, NH, naval_bg),
    ("cb_naval_leader_frame", "gfx/interface/navalcombat/naval_battle_leader_frame.dds", 81, 107, naval_leader_frame),
    ("cb_naval_bar_win", "gfx/interface/navalcombat/bar_progress_win.dds", 351, 14, lambda: naval_progress(DEF, False)),
    ("cb_naval_bar_lose", "gfx/interface/navalcombat/bar_progress_loose.dds", 351, 14, lambda: naval_progress(ATK, True)),
    ("cb_naval_screening", "gfx/interface/navalcombat/screening_bg.dds", 248, 27, screening_chips),
    ("cb_naval_compass", "gfx/interface/navalcombat/naval_battlemap_overlay1.dds", 438, 61, compass),
    ("cb_naval_stats", "gfx/interface/navalcombat/combat_stat_icons.dds", 156, 26, naval_stats),
]
