"""The diplomatic action windows (countrydiplomacyview.gui's action windows, factions/faction_popup.gui,
operative.gui) at the game's paths and sizes (2026-10-17, SCREEN_INVENTORY.md's suggestion 6).

The game draws every diplomatic action (declare war, justify, volunteers, lend-lease, guarantee, improve relations ...)
on a picture of its own, 527 px wide (the licence window's 496) and 313 to 664 tall: one frame, the same in all of them,
with a header whose two emblems say what the action is (a handshake, a dove, tanks and a warship ...), and here and
there a band or a recessed panel where the window writes its text. The game's standard window
(standard_diplomacy_controller, "for new ones or ones that just need to change background") gets the picture of the
action from the game (inferred: no .gui names those pictures): improve relations, military access, peace, embargo,
garrisons, the spymaster, dismantling a faction ... Lend-lease's
picture also backs the market's two windows, invite to faction's the old create-faction window, request forces' the
faction's manpower and rule windows.

Here the frame is the Deco UI's, drawn for each height: lacquer, a double gilt rule and corner brackets, a raised header
band with a stepped title plate where the game writes the title (y 29, centred on x 265), a gilt octagon at either end
with the action's emblem in gilt line art (EMBLEMS: modern-day subjects in the icon set's style, on its 24 px grid; the
right-hand one mirrored to face the title), and a footer band under the Send and Cancel buttons (at height - 60, or
-57, -48, -35 where the window is shorter than its picture). The bands and recessed panels are where the game's are
(measured from its pictures: SPECS), since the game's text and lists lie on them; all the game's text there is light,
so everything stays lacquer-dark. The licence window writes its title higher (y 16): its plate and medallions move up.

Also drawn: the cancel strip of the coup and state control windows (diplo_action_cancel_bg: coral hatching, a
warning), the strip under the other country's reply (diplo_response_bg), and the two pieces the add-war-goal window lays
over the justification picture (diplo_action_justify_wargoals_top_bg and header2: cut from that picture, see
ADD_WARGOAL).

gen_textures.py adds them (keys dp_*).
"""
import math

from designer_art import frame_base, band, inset, gilt_line, footer

GILT_LINE = "#E3C77E"
EMBLEM_BG = "#0B1115"          # the medallion's lacquer: filled shapes mask the lines behind them with it


def _star(cx, cy, r1, r2, n=5, rot=-90):
    pts = []
    for k in range(2 * n):
        r = r1 if k % 2 == 0 else r2
        a = math.radians(rot + 180 * k / n)
        pts.append(f"{cx + r * math.cos(a):.2f} {cy + r * math.sin(a):.2f}")
    return "M" + "L".join(pts) + "z"


def _gear(cx, cy, r_out, r_in, teeth=8, tw=.38):
    """a cog's outline: teeth of angular width tw (fraction of the pitch) on a ring"""
    pts = []
    for k in range(teeth):
        a0 = 2 * math.pi * k / teeth
        p = 2 * math.pi / teeth
        for a, r in ((a0 - p * tw / 2 - p * .08, r_in), (a0 - p * tw / 2, r_out), (a0 + p * tw / 2, r_out),
                     (a0 + p * tw / 2 + p * .08, r_in)):
            pts.append(f"{cx + r * math.cos(a):.2f} {cy + r * math.sin(a):.2f}")
    return "M" + "L".join(pts) + "z"


# Each emblem on the icon set's 24 px grid (tools/icons.py: round caps and joins, no fill unless a shape has to mask
# the lines behind it, which it does with the medallion's lacquer). Modern-day subjects only (Valsora is set in 2036).
EMBLEMS = {
    # the default window (and the faction popups): a diplomatic dispatch, sealed
    "dispatch": ('<path d="M3 5h18v11.5H3z"/><path d="M3 5.4l9 6.6 9-6.6"/>'
                 f'<path d="M10.5 18l-1.3 3.8 2.8-1.4 2.8 1.4-1.3-3.8"/>'
                 f'<circle cx="12" cy="16.3" r="2.7" fill="{EMBLEM_BG}"/><circle cx="12" cy="16.3" r="1" fill="currentColor" stroke="none"/>'),
    # improve relations: two hands clasped, cuffs either side
    "handshake": ('<path d="M1.8 9h3.4v6.8H1.8M22.2 9h-3.4v6.8h3.4"/>'
                  '<path d="M5.2 10.2c2.2-1.6 4.4-2.2 6.4-1.4l1.6.7"/>'
                  '<path d="M18.8 10.4l-3-1.6c-1.4-.7-3-.5-4.2.6l-2.4 2.2c-.6.6-.4 1.6.4 1.9.7.3 1.4.1 1.9-.4l1.5-1.4 4.1 3.4"/>'
                  '<path d="M5.2 14.6l3.2 2.8c.6.5 1.4.4 1.9-.1M10.3 17.3l1.1.9c.6.5 1.5.4 2-.1M13.4 18.1l.5.3c.6.4 1.4.3 1.9-.2l1-1.2'
                  'M16.8 17l2-1.6"/><path d="M8.1 14.6l2.2 2.7M10.7 14.1l2.7 4M13.2 13.5l2.6 4.1"/>'),
    # military access: an arrow across a dashed border
    "border": '<path d="M12 2.5v3M12 8.5v1.5M12 14v1.5M12 18.5v3"/><path d="M2.5 12h17"/><path d="M15.5 7.5l4.5 4.5-4.5 4.5"/>',
    # offer peace: a dove in flight with an olive sprig
    "dove": ('<path d="M21.2 9.2l-2.1-.5c-.6-1.3-2.3-1.6-3.4-.6-1.3 1.2-2.6 2.9-5.1 3.7-2.3.8-4.6 1.1-7.1 2.9 3.2.9 6.2 2 9.4 1.5'
             ' 3.3-.5 5.4-2.7 6.3-5.7z"/>'
             '<path d="M11.9 11.6c-1.3-2.7-1.6-5.4-.6-8.4 2.1 1.6 3.7 3.8 4.3 5.6"/><path d="M9 12.6c-1.6-1.6-2.7-3.6-2.9-6 1.6.7 3 1.9 4 3.4"/>'
             '<path d="M20.6 9.6c.2 1.8-.2 3.6-1.4 5.2"/><path d="M20.3 11.6l1.6-.5M19.9 13.4l-1.5-.5"/>'
             '<circle cx="17.4" cy="9.1" r=".55" fill="currentColor" stroke="none"/>'),
    # request forces (and the faction's manpower request): troops called in, the NATO infantry symbol and an arrow into it
    "unit_in": '<path d="M2.5 10h13v10h-13z"/><path d="M2.5 10l13 10M15.5 10l-13 10"/><path d="M21.5 2.5l-5.2 5.2M15.5 3.6v4.9h4.9"/>',
    # embargo: a shipping container under a prohibition sign
    "embargo": ('<path d="M5.8 8.6h12.4v7.2H5.8z"/><path d="M9.9 8.6v7.2M14.1 8.6v7.2"/>'
                '<circle cx="12" cy="12.2" r="9.4"/><path d="M5.4 5.6l13.2 13.2"/>'),
    # foreign garrison: a watchtower flying a flag
    "tower": ('<path d="M8 21.5l1.6-10M16 21.5l-1.6-10M8.6 17.5l6.4-4.3M15.4 17.5L9 13.2"/><path d="M6.5 8.5h11v3h-11z"/>'
              '<path d="M5.5 8.5L12 4.6l6.5 3.9"/><path d="M12 4.6V1.6l3.6 1.2L12 4"/>'),
    # the spymaster: an open eye
    "eye": ('<path d="M1.8 12s3.7-6.6 10.2-6.6S22.2 12 22.2 12s-3.7 6.6-10.2 6.6S1.8 12 1.8 12z"/><circle cx="12" cy="12" r="3.6"/>'
            '<circle cx="12" cy="12" r="1.3" fill="currentColor" stroke="none"/>'),
    # boost party popularity: a loudhailer
    "megaphone": ('<path d="M3 9.6h3.4l9.6-5.4v15.6l-9.6-5.4H3z"/><path d="M6.6 14.4l1.2 5.4h2.6l-1-4.6"/>'
                  '<path d="M18.6 9.4a4 4 0 0 1 0 5.2M20.8 7.2a7.2 7.2 0 0 1 0 9.6"/>'),
    # call allies: a radio mast broadcasting
    "radio": ('<path d="M12 9.2L8 21.5M12 9.2l4 12.3M9.6 16.6h4.8M10.6 13.4h2.8M8.8 19.1l5.4-2.5"/>'
              '<circle cx="12" cy="7.6" r="1.5"/>'
              '<path d="M8.6 4.4a4.8 4.8 0 0 0 0 6.4M15.4 4.4a4.8 4.8 0 0 1 0 6.4M5.8 2.2a8.2 8.2 0 0 0 0 10.8M18.2 2.2a8.2 8.2 0 0 1 0 10.8"/>'),
    # join allies: two chain links, joined
    "chain": ('<rect x="2.6" y="12" width="13" height="6.4" rx="3.2" transform="rotate(-45 9.1 15.2)"/>'
              '<rect x="8.4" y="5.6" width="13" height="6.4" rx="3.2" transform="rotate(-45 14.9 8.8)"/>'),
    # dissolve the faction: the two links broken apart
    "chain_broken": ('<rect x="1" y="14.2" width="11" height="6.4" rx="3.2" transform="rotate(-45 6.5 17.4)"/>'
                     '<rect x="12" y="3.4" width="11" height="6.4" rx="3.2" transform="rotate(-45 17.5 6.6)"/>'
                     '<path d="M10.2 9.4l-1.6-2.4M14.6 13.8l2.4 1.6M12.4 10.4l.3-2.6M11.6 13.6l-2.6.3"/>'),
    # invite to the faction: its three rings and a plus
    "rings_plus": ('<circle cx="10" cy="9.4" r="4"/><circle cx="6.6" cy="15.4" r="4"/><circle cx="13.4" cy="15.4" r="4"/>'
                   '<path d="M19.4 2.6v6M16.4 5.6h6"/>'),
    # guarantee independence (and the naval blockade): a shield with a star
    "shield": ('<path d="M12 2.6l7.6 2.8v5.8c0 4.8-3.2 8.6-7.6 10.2-4.4-1.6-7.6-5.4-7.6-10.2V5.4z"/>'
               f'<path d="{_star(12, 11.4, 4.2, 1.75)}"/>'),
    # send an attaché: an attaché case
    "briefcase": ('<path d="M2.8 7.8h18.4v12H2.8z"/><path d="M8.8 7.8V5.2h6.4v2.6"/><path d="M2.8 12.6h18.4"/>'
                  f'<path d="M10.6 11.2h2.8v2.8h-2.8z" fill="{EMBLEM_BG}"/>'),
    # declare war: two blades crossed
    "blades": ('<path d="M20.8 3.2l-.6 3.4L9.1 17.7l-2.8-2.8L17.4 3.8z"/><path d="M4.8 13.4l5.8 5.8M7.7 16.3l-3.4 3.4"/>'
               f'<path d="M3.2 3.2l.6 3.4 11.1 11.1 2.8-2.8L6.6 3.8z" fill="{EMBLEM_BG}"/><path d="M19.2 13.4l-5.8 5.8M16.3 16.3l3.4 3.4"/>'
               '<circle cx="3.7" cy="20.3" r=".9"/><circle cx="20.3" cy="20.3" r=".9"/>'),
    # justify a war goal: a document and a pen
    "scroll_quill": ('<path d="M3.5 3.5h9l3.5 3.5v13.5H3.5z"/><path d="M12.5 3.5V7H16"/><path d="M6 10.5h7M6 13.5h5.5M6 16.5h4"/>'
                     f'<path d="M21.6 2.4c-4.6 1-7.8 4.6-9.2 9.6l-.9 3.4 2.6-2.4c4-1.8 6.4-5.4 7.5-10.6z" fill="{EMBLEM_BG}"/>'
                     '<path d="M11.4 17.6l3.2-6"/>'),
    # stage a coup (and the state control windows): the seat of government, struck by lightning
    "capitol_bolt": ('<path d="M3.5 9L12 4.2 20.5 9z"/><path d="M5.5 11v7M9.2 11v7M14.8 11v7M18.5 11v7"/><path d="M3.5 20.5h17M4.5 18h15"/>'
                     f'<path d="M14.2 1.2l-4 7.6h3.4l-3.8 7.8 7.4-9.6h-3.6l3.4-5.8z" fill="{EMBLEM_BG}"/>'),
    # an expeditionary force: the globe, an arrow arching out over it
    "globe_arrow": ('<circle cx="10" cy="14" r="7.6"/><ellipse cx="10" cy="14" rx="3.4" ry="7.6"/><path d="M2.4 14h15.2M3.6 10.2h12.8M3.6 17.8h12.8"/>'
                    '<path d="M8.6 4.6c3.6-2.6 9.4-2.4 12.2 2.2"/><path d="M21.6 3.2l-.6 3.8-3.8-.8"/>'),
    # lend-lease (and the market's windows): a braced shipping crate
    "crate": ('<path d="M12 2.6l8.8 4.7v9.6L12 21.6l-8.8-4.7V7.3z"/><path d="M3.2 7.3L12 12l8.8-4.7M12 12v9.6"/>'
              '<path d="M3.2 10.5l8.8 4.7M3.2 13.7l8.8 4.7"/><path d="M12 21.6l8.8-14.3"/><path d="M7.6 9.65l8.8-4.7"/>'),
    # licensed production: a licence and a cog
    "licence": ('<path d="M3 2.8h10v14.6H3z"/><path d="M5.4 6h5.2M5.4 8.6h5.2M5.4 11.2h3"/>'
                f'<path d="{_gear(15.6, 15.6, 6.6, 5.0)}" fill="{EMBLEM_BG}"/><circle cx="15.6" cy="15.6" r="2.2"/>'),
}


def emblem_svg(name, size, color=GILT_LINE, sw=1.3, mirror=False):
    """an emblem as <svg> markup, like icons.icon(); the volunteers' helmet is the icon set's own"""
    from icons import ICONS
    body = EMBLEMS[name] if name in EMBLEMS else ICONS[name]
    flip = ";transform:scaleX(-1)" if mirror else ""
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" style="display:block;color:{color}{flip}">'
            f'{body}</svg>')


# ---------------------------------------------------------------- the frame
GOLD_GRAD = ('<linearGradient id="{id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F1DC9C"/>'
             '<stop offset=".5" stop-color="#C9A55A"/><stop offset="1" stop-color="#8B6A2C"/></linearGradient>')
HEAD = (6, 74)          # the header band (the game's header runs from 11 to 70 and its body starts at 80)
PLATE = (20, 62)        # the title plate: the game writes the title at y 29 (its capitals from about 37 to 48)
MED_R = 27              # the octagons' circumradius; centred on the header band, MED_IN px in from each side
MED_IN = 54
NO_MIRROR = {"embargo"}   # the right-hand emblem faces the title too, but a prohibition sign's bar never flips
STEPS = ((6, 13), (11, 7))   # the plate's two steps at either end: how far out, half their height


def _pts(pts):
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)


def _octagon(cx, cy, r):
    return [(cx + r * math.cos(math.radians(22.5 + 45 * k)), cy + r * math.sin(math.radians(22.5 + 45 * k))) for k in range(8)]


def _svg(w, h, body, defs=""):
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="position:absolute;left:0;top:0;overflow:visible">'
            f'<defs>{defs}</defs>{body}</svg>')


def _rays(x0, x1, cx, cy, r=MED_R):
    """faint gilt rays fanning out behind a medallion, on its outer side only (x0..x1 of the header band)"""
    y0, y1 = HEAD[0] + 1, HEAD[1] - 1
    return (f'<div style="position:absolute;left:{x0}px;top:{y0}px;width:{x1 - x0}px;height:{y1 - y0}px;overflow:hidden">'
            f'<div style="position:absolute;inset:0;background:repeating-conic-gradient(from 0deg at {cx - x0}px {cy - y0}px,'
            'rgba(227,199,126,.26) 0deg 2.2deg,transparent 2.2deg 9deg);'
            f'-webkit-mask:radial-gradient(circle at {cx - x0}px {cy - y0}px,#000 {r + 2}px,rgba(0,0,0,.55) {r + 12}px,transparent {r + 40}px)">'
            '</div></div>')


def medallion(cx, cy, emblem, mirror=False, gid="dp_mg", r=MED_R):
    """a gilt octagon on lacquer holding the action's emblem"""
    body = (f'<polygon points="{_pts(_octagon(cx, cy, r + 2.5))}" fill="rgba(8,12,15,.85)"/>'
            f'<polygon points="{_pts(_octagon(cx, cy, r))}" fill="#0B1115" stroke="url(#{gid})" stroke-width="1.6"/>'
            f'<polygon points="{_pts(_octagon(cx, cy, r - 3.5))}" fill="none" stroke="rgba(201,165,90,.45)" stroke-width="1"/>')
    size = round(r * 32 / MED_R)
    return (_svg(1, 1, body, GOLD_GRAD.format(id=gid))
            + f'<div style="position:absolute;left:{cx - size / 2}px;top:{cy - size / 2}px">{emblem_svg(emblem, size, sw=1.3, mirror=mirror)}</div>')


def title_plate(cx, half, y0=PLATE[0], y1=PLATE[1], gid="dp_tg"):
    """the stepped plate under the title: chamfered, gilt-edged, two steps out at either end with a gilt diamond in the
    outer one; one outline, so the steps read as part of the plate (the game's plate is 330 wide: some titles fill it)"""
    x0, x1, c = cx - half, cx + half, 6
    my = (y0 + y1) / 2
    (d1, h1), (d2, h2) = STEPS
    right = [(x1 - c, y0), (x1, y0 + c), (x1, my - h1), (x1 + d1, my - h1), (x1 + d1, my - h2), (x1 + d2, my - h2),
             (x1 + d2, my + h2), (x1 + d1, my + h2), (x1 + d1, my + h1), (x1, my + h1), (x1, y1 - c), (x1 - c, y1)]
    left = [(2 * cx - x, y) for x, y in reversed(right)]
    inner = [(x0 + c + 1, y0 + 4), (x1 - c - 1, y0 + 4), (x1 - 4, y0 + c + 1), (x1 - 4, y1 - c - 1), (x1 - c - 1, y1 - 4),
             (x0 + c + 1, y1 - 4), (x0 + 4, y1 - c - 1), (x0 + 4, y0 + c + 1)]
    out = (f'<polygon points="{_pts(right + left)}" fill="url(#dp_tp)" stroke="url(#{gid})" stroke-width="1.3"/>'
           f'<polygon points="{_pts(inner)}" fill="none" stroke="rgba(201,165,90,.35)" stroke-width="1"/>')
    for s in (-1, 1):
        dx = cx + s * (half + (d1 + d2) / 2)
        out += f'<path d="M{dx},{my - 3}L{dx + 2.4},{my}L{dx},{my + 3}L{dx - 2.4},{my}Z" fill="url(#{gid})"/>'
    defs = (GOLD_GRAD.format(id=gid) + '<linearGradient id="dp_tp" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0" stop-color="#070B0E"/><stop offset="1" stop-color="#0E151A"/></linearGradient>')
    return _svg(1, 1, out, defs)


def header(w, emblem, title_cx=265, half=162, med_in=MED_IN, plate=PLATE, med_cy=None, med_r=MED_R):
    """the header band: rays, a medallion at either end, the title plate between them"""
    cy = med_cy or (HEAD[0] + HEAD[1]) / 2
    ml, mr = med_in, w - med_in
    out = (band(HEAD[0], HEAD[0], w - HEAD[0], HEAD[1]) + gilt_line(HEAD[0], HEAD[1], w - HEAD[0], HEAD[1])
           + gilt_line(HEAD[0], HEAD[1] + 2, w - HEAD[0], HEAD[1] + 2, "rgba(201,165,90,.35)")
           + _rays(HEAD[0] + 1, ml, ml, cy, med_r) + _rays(mr, w - HEAD[0] - 1, mr, cy, med_r))
    return (out + title_plate(title_cx, half, *plate) + medallion(ml, cy, emblem, gid="dp_ml", r=med_r)
            + medallion(mr, cy, emblem, mirror=emblem not in NO_MIRROR, gid="dp_mr", r=med_r))


def strip(x0, y0, x1, y1):
    """a raised band across the window under the header, where the game writes a line or two (the game's brown band):
    lacquer a shade lighter, gilt hairlines along both edges"""
    return (band(x0, y0, x1, y1) + gilt_line(x0, y0, x1, y0, "rgba(201,165,90,.7)")
            + gilt_line(x0, y1 - 1, x1, y1 - 1, "rgba(201,165,90,.7)")
            + gilt_line(x0, y1 + 1, x1, y1 + 1, "rgba(201,165,90,.25)"))


def divider(x, y0, y1):
    """a vertical gilt hairline fading at its ends, a diamond at its middle"""
    m = (y0 + y1) // 2
    return (f'<div style="position:absolute;left:{x}px;top:{y0}px;width:1px;height:{y1 - y0}px;'
            'background:linear-gradient(180deg,rgba(201,165,90,0),rgba(201,165,90,.7) 20%,rgba(201,165,90,.7) 80%,rgba(201,165,90,0))"></div>'
            f'<div style="position:absolute;left:{x - 3.5}px;top:{m - 4}px;width:8px;height:8px;background:#0E151A;'
            'border:1px solid #C9A55A;transform:rotate(45deg);box-sizing:border-box"></div>')


def window(w, h, emblem, foot, extras=(), title_cx=265, half=162, med_in=MED_IN, plate=PLATE, med_cy=None, med_r=MED_R):
    """one action window's picture: the frame, the header with the action's emblem, the extras where the game's own
    picture has a band, a recessed panel or a divider, the footer band under the buttons (from y foot)"""
    out = frame_base(w, h)
    for kind, *a in extras:
        out += {"strip": strip, "panel": lambda *b: inset(tuple(b)), "divider": divider,
                "raised": lambda x0, y0, x1, y1: band(x0, y0, x1, y1) + gilt_line(x0, y0, x1, y0, "rgba(201,165,90,.6)")}[kind](*a)
    return (out + footer(w, foot, h - 12) + header(w, emblem, title_cx, half, med_in, plate, med_cy, med_r)
            + '<i class="ck tl"></i><i class="ck tr"></i><i class="ck bl"></i><i class="ck br"></i>')


# The pictures: (key, the game's file, width, height, emblem, footer top, extras). The footer, bands and panels are
# where the game's own pictures have them (measured from its textures), as the game's windows put their buttons, text
# and lists there: the brown band at y 80-121 (85-128 for boost party, 80-144 for the licence window), declare war's
# panel at x 273-505, y 127-466 with the call-allies strip from 424, the coup's at x 273-505, y 159-462, the
# justification's at x 18-506, y 127-217, the attaché's divider at x 340.
BAND = ("strip", 6, 80, 521, 122)
JUSTIFY_PANEL = ("panel", 18, 127, 506, 217)
SPECS = [
    ("dp_generic", "generic_diplo_action_bg", 527, 315, "dispatch", 250, ()),
    ("dp_dissolve_faction", "diplo_action_dissolve_faction_bg", 527, 315, "chain_broken", 250, ()),
    ("dp_imp_relations", "diplo_action_imp_relations_bg", 527, 315, "handshake", 250, ()),
    ("dp_mil_access", "diplo_action_mil_acess_bg", 527, 315, "border", 250, ()),
    ("dp_offer_peace", "diplo_action_offer_peace_bg", 527, 315, "dove", 250, ()),
    ("dp_request_forces", "diplo_action_request_forces_bg", 527, 315, "unit_in", 250, ()),
    ("dp_embargo", "diplo_action_embargo", 526, 313, "embargo", 249, ()),
    ("dp_foreign_garrison", "diplo_action_foreign_garrison_bg", 526, 313, "tower", 249, ()),
    ("dp_spymaster", "diplo_action_spymaster_bg", 526, 313, "eye", 249, ()),
    ("dp_boost_party", "diplo_action_boost_party_bg", 527, 360, "megaphone", 295, (("strip", 6, 85, 521, 128),)),
    ("dp_call_allies", "diplo_action_call_allies_bg", 527, 360, "radio", 295, ()),
    ("dp_guarantee", "diplo_action_guarantee_independence_bg", 527, 360, "shield", 295, ()),
    ("dp_join_allies", "diplo_action_join_allies_bg", 527, 360, "chain", 295, ()),
    ("dp_invite_to_faction", "diplo_action_invite_to_faction_bg", 527, 410, "rings_plus", 346, ()),
    ("dp_send_attache", "diplo_action_send_attache_bg", 527, 430, "briefcase", 369, (("divider", 340, 92, 300),)),
    # declare war: the land battle's crossed swords (icons.py "swords", combat_art's attacker medallion), not the blades
    # (the author, 2026-10-21: "The declare war screen should use the same crossed swords as the battle screen, at
    # least for now"); the confirmation popups' medallion (window_art.war_icon) keeps the blades
    ("dp_declare_war", "diplo_action_declare_war_bg", 527, 532, "swords", 467,
     (BAND, ("panel", 273, 127, 505, 466), ("raised", 274, 423, 504, 465))),
    ("dp_justify", "diplo_action_justify_wargoals_bg", 527, 532, "scroll_quill", 467,
     (("strip", 13, 80, 513, 122), JUSTIFY_PANEL)),
    ("dp_stage_coup", "diplo_action_stage_coup_bg", 527, 532, "capitol_bolt", 467, (("panel", 273, 159, 505, 462),)),
    ("dp_expeditionary", "diplo_action_expeditionary_force_bg", 527, 612, "globe_arrow", 547, ()),
    ("dp_lend_lease", "diplo_action_lend_lease_bg", 527, 612, "crate", 547, (BAND,)),
    ("dp_volunteers", "diplo_action_volunteers_bg", 527, 612, "army", 547, (BAND,)),
    ("dp_license", "diplo_action_license_production_bg", 496, 664, "licence", 599, (("strip", 6, 80, 490, 145),)),
]
# the licence window's picture is 496 wide; its title box (x 122-382) is centred on x 252, and at y 16, 13 px higher
# than the others (the game's plate sat under the title's lower half): the plate and the medallions move up to it
LICENCE = dict(title_cx=252, half=146, med_in=52, plate=(11, 49), med_cy=33, med_r=25)


def _picture(spec):
    key, f, w, h, emblem, foot, extras = spec
    kw = LICENCE if key == "dp_license" else {}
    return lambda: window(w, h, emblem, foot, extras, **kw)


# add_wargoal (adding a war goal in a war) lays two pieces over the justification picture: its top (500 x 150 at
# (13, 11)) and header2 (525 x 42 at (1, 15), the game's title plate; no other window uses it), puts the game's category
# bar at y 113-157 with the war goal's name on it, and writes its title at y 23, 6 px higher than the others. The top
# covers the header and the band (which is why the justification band runs from x 13 to 513), so both pieces are cut
# from the justification picture with its plate raised 5 px, centred on that title, and without the band, which the
# category bar replaces; elsewhere they match the picture under them.
ADD_WARGOAL = dict(plate=(PLATE[0] - 5, PLATE[1] - 5))


def _cut(x, y):
    """a piece of the justification picture as add_wargoal draws it, as the game lays it over that picture at (x, y)"""
    _, _, w, h, emblem, foot, _ = next(s for s in SPECS if s[0] == "dp_justify")
    return (f'<div style="position:absolute;left:{-x}px;top:{-y}px;width:{w}px;height:{h}px">'
            + window(w, h, emblem, foot, (JUSTIFY_PANEL,), **ADD_WARGOAL) + '</div>')


def justify_top():
    return _cut(13, 11)


def header2():
    return _cut(1, 15)


def cancel_strip(w=503, h=48):
    """the strip behind the coup's and state control's cancel button: coral hatching, a warning"""
    from art_util import bar
    return bar("repeating-linear-gradient(-45deg,rgba(238,140,126,.22) 0 5px,transparent 5px 13px),"
               "linear-gradient(180deg,#1E1517,#120D0E)", "rgba(238,140,126,.8)", 8, .1)


def response_strip(w=449, h=40):
    """the strip under the other country's reply (its text centred over it, the tick or cross at its right end)"""
    from art_util import bar
    return (bar("radial-gradient(ellipse at 50% 50%,rgba(227,199,126,.12),rgba(227,199,126,0) 70%),"
                "linear-gradient(180deg,#0A0F12,#0D1418)", "rgba(201,165,90,.6)", 7, .12))


ADDS = ([(key, f"gfx/interface/{f}.dds", w, h, _picture((key, f, w, h, e, ft, ex))) for key, f, w, h, e, ft, ex in SPECS]
        + [("dp_justify_top", "gfx/interface/diplo_action_justify_wargoals_top_bg.dds", 500, 150, justify_top),
           ("dp_header2", "gfx/interface/header2.dds", 525, 42, header2),
           ("dp_cancel", "gfx/interface/diplo_action_cancel_bg.dds", 503, 48, cancel_strip),
           ("dp_response", "gfx/interface/diplo_response_bg.dds", 449, 40, response_strip)])
