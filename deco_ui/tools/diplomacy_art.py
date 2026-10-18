"""The diplomacy panel's own pictures (countrydiplomacyview.gui's main window: the country's header, its leader, its
politics and the lists under them) at the game's paths and sizes (v0.10.4, 2026-10-18, the author: "continuing to
stylize the other screens in Deco style. One specific one is the diplomacy screen ... redraw the pictures. One thing
I'd definitely like in particular is to have the leader portrait stylized the same way others are").

The panel's frame, header and shared pieces were done in v0.5 (make_panels.py), its action windows in v0.10
(diplo_art.py); this redraws what the game still drew in its riveted metal, where the game's are, since the game's text
and icons lie on them (measured from its pictures and its .gui):
- the leader's frame (134 x 175, drawn over the portrait, which the game scales 0.74 to 115 x 155 at the frame's
  (7, 10)): an arched opening in a chamfered lacquer plate with gilt rims, as the leader events' and the army bar's;
- the flag's frame (134 x 80, over the flag at its (26, 11), 82 x 52): a gilt rim, a lacquer mat and stepped corner
  brackets, as the flag medallion's (layout.FRAME_STEPS);
- the politics block behind the pie and the ruling party (399 x 167): a gilt socket for the pie (its overlay at the
  block's (19, 9), 71 x 71), lacquer wells for the texts, a fan where the game had its laurel and flags;
- the pie's overlay (71 x 71, also the game's elsewhere): a gilt ring over the pie, a glint, the middle left clear;
- the strip under the header (399 x 71), the country list's binding (533 x 35), the national focus button (3 frames
  of 285 x 64: normal, lit, pressed), its progress frame (239 x 8), the national spirits band (520 x 92) with the
  tab its label sits on, the unity well (42 x 62), the 203 px text well, the short window header (233 x 112).
Left as the game's: the filter strip (diplo_filter_area_bg) and the opinion box (diplo_opinion_bg), which have the
game's icons painted in (the globe, the fist, the arrows): no icon of the game's changes without the author's yes.

gen_textures.py adds them (keys dv_*).
"""
from art_util import DIM_FILL, STRIPES, bar, frames

G = "gfx/interface/"
DEFS = ('<linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F1DC9C"/>'
        '<stop offset="1" stop-color="#8B6A2C"/></linearGradient>'
        '<pattern id="pin" width="8" height="8" patternUnits="userSpaceOnUse"><rect width="8" height="8" fill="#11191E"/>'
        '<rect width="1" height="8" fill="#1A2329"/></pattern>')
LINE = "rgba(201,165,90,.45)"


def svg(w, h, body):
    return f'<svg width="{w}" height="{h}" style="position:absolute;left:0;top:0"><defs>{DEFS}</defs>{body}</svg>'


def cham(x0, y0, x1, y1, c):
    return f"M{x0 + c},{y0}L{x1 - c},{y0}L{x1},{y0 + c}L{x1},{y1 - c}L{x1 - c},{y1}L{x0 + c},{y1}L{x0},{y1 - c}L{x0},{y0 + c}Z"


def arch(x0, x1, top, sh, bottom):
    return f"M{x0},{bottom}L{x0},{sh}A{(x1 - x0) / 2},{sh - top} 0 0 1 {x1},{sh}L{x1},{bottom}Z"


def well(x0, y0, x1, y1, c=4, fill="#0A0F12", rim=LINE):
    return (f'<path d="{cham(x0, y0, x1, y1, c)}" fill="{fill}" stroke="{rim}"/>')


def fan(cx, cy, r, n=9, spread=70, colour="rgba(201,165,90,.16)"):
    """speed lines fanning up from (cx, cy), the deco motif standing in for the game's laurel"""
    import math
    out = ""
    for i in range(n):
        a = math.radians(-90 - spread / 2 + spread * i / (n - 1))
        out += (f'<line x1="{cx + 6 * math.cos(a):.1f}" y1="{cy + 6 * math.sin(a):.1f}" x2="{cx + r * math.cos(a):.1f}" '
                f'y2="{cy + r * math.sin(a):.1f}" stroke="{colour}" stroke-width="1"/>')
    return out


# the leader's frame (v0.11, the author: "the leader portrait [should be stylized] like the [one] in the politics screen
# ... as things are the leader portrait in the diplomacy tab, larger portraits like Krionik's start to get cut off"):
# the politics screen's arch (a thin rim, a thick gilt one, the diamond on top, a sunburst in the arch), flatter here,
# so that the whole portrait fits under it: the game's 156 x 210 at PORTRAIT_SCALE (103 x 139) at `portrait`, the arch's
# opening `hole` (x0, x1, its top, the springline, the bottom); the arch clears the portrait's top corners. The plate
# ends at `right`, under the politics block beside it (at the panel's x 138, the frame's 125)
PORTRAIT_SCALE = 0.66
LEADER = dict(w=134, h=175, right=124.5, hole=(9, 118, 10, 36, 168), portrait=(12, 28, 103, 139))


def arch_path(x0, x1, top, sh, bottom, d=0.0):
    """the arch's outline grown by d px (an elliptical top: half-width (x1 - x0) / 2, height sh - top)"""
    a, b = (x1 - x0) / 2 + d, sh - top + d
    return f"M{x0 - d},{bottom + d}L{x0 - d},{sh}A{a},{b} 0 0 1 {x1 + d},{sh}L{x1 + d},{bottom + d}Z"


def leader_frame():
    import math
    W, H, R = LEADER["w"], LEADER["h"], LEADER["right"]
    x0, x1, top, sh, bottom = LEADER["hole"]
    px, py, pw, ph = LEADER["portrait"]
    cx = (x0 + x1) / 2
    hole = arch_path(x0, x1, top, sh, bottom)
    outer = arch_path(x0, x1, top, sh, bottom, 5.5)
    # the sunburst behind the portrait: rays from under its middle, seen in the arch above it and at its sides
    rays = "".join(f'<path d="M{cx},{py + ph * .55}L{cx + 160 * math.cos(math.radians(a - 2.2)):.1f},'
                   f'{py + ph * .55 + 160 * math.sin(math.radians(a - 2.2)):.1f}L{cx + 160 * math.cos(math.radians(a + 2.2)):.1f},'
                   f'{py + ph * .55 + 160 * math.sin(math.radians(a + 2.2)):.1f}Z" fill="rgba(227,199,126,.16)"/>'
                   for a in range(-180, 1, 12))
    # the arch less the portrait's rectangle (the game draws this frame over the portrait)
    well_path = hole + f"M{px},{py}h{pw}v{ph}h{-pw}Z"
    return svg(W, H, f'<clipPath id="arch"><path d="{well_path}" clip-rule="evenodd"/></clipPath>'
                     # the lacquer round the arch, out to the thin rim
                     f'<path d="{outer}{hole}" fill="url(#pin)" fill-rule="evenodd"/>'
                     # inside the arch: a dark well and the sunburst (the portrait covers its lower part)
                     f'<g clip-path="url(#arch)"><rect width="{W}" height="{H}" fill="#0B1014"/>{rays}</g>'
                     f'<path d="{outer}" fill="none" stroke="#B8954F" stroke-width="1"/>'
                     f'<path d="{arch_path(x0, x1, top, sh, bottom, 1.5)}" fill="none" stroke="url(#g)" stroke-width="3"/>'
                     f'<path d="M{cx - 5},{top - 1.5}l5 -3.5 5 3.5 -5 3.5z" fill="#E3C77E"/>')


# the flag's frame: the flag (82 x 52) at (26, 11)
# v0.11 (the author: "the bar with ideology, stability, names, etc. should be level with the flag"): the mat runs MX px
# beside the flag and MY above / MY_B below it, so the frame is the bar's 71 px tall and starts at the tabs' left edge;
# make_panels moves frame and flag to where the bar's top and the tabs' edge are (layout_panels.DIPLO_FLAG)
FLAG = dict(w=134, h=80, x=26, y=11, fw=82, fh=52, mx=18, my=10, my_b=9)


def corner_steps(x, y, w, h, arm, colour):
    out = ""
    for cx, cy, sx, sy in ((x, y, 1, 1), (x + w - 1, y, -1, 1), (x, y + h - 1, 1, -1), (x + w - 1, y + h - 1, -1, -1)):
        hx = cx if sx > 0 else cx - arm + 1
        vy = cy if sy > 0 else cy - arm + 1
        out += (f'<div style="position:absolute;left:{hx}px;top:{cy}px;width:{arm}px;height:1px;background:{colour}"></div>'
                f'<div style="position:absolute;left:{cx}px;top:{vy}px;width:1px;height:{arm}px;background:{colour}"></div>')
    return out


def flag_frame():
    W, H, x, y, fw, fh = FLAG["w"], FLAG["h"], FLAG["x"], FLAG["y"], FLAG["fw"], FLAG["fh"]
    ox, oy, ow, oh = x - FLAG["mx"], y - FLAG["my"], fw + 2 * FLAG["mx"], fh + FLAG["my"] + FLAG["my_b"]
    hole = f"M{x},{y}h{fw}v{fh}h{-fw}Z"
    mat = f"M{ox},{oy}h{ow}v{oh}h{-ow}Z"
    return (svg(W, H, f'<path d="{mat}{hole}" fill="url(#pin)" fill-rule="evenodd"/>'
                      f'<rect x="{ox + 3.5}" y="{oy + 3.5}" width="{ow - 7}" height="{oh - 7}" fill="none" stroke="url(#g)"/>'
                      f'<rect x="{x - 1}" y="{y - 1}" width="{fw + 2}" height="{fh + 2}" fill="none" stroke="#C9A55A" stroke-width="2"/>')
            + corner_steps(ox, oy, ow, oh, 7, "rgba(201,165,90,.45)") + corner_steps(ox + 2, oy + 2, ow - 4, oh - 4, 12, "#C9A55A"))


# the politics block (399 x 167): the pie's socket left (the overlay at (19, 9), 71 x 71), the party's texts right.
# v0.11 (the author: "Focus icon isn't centered"): the left column's wells are centred on the pie and on the focus icon
# the game centres at the block's x 54 (its 192 - 138), y 127: the column 3 to 106, the wells' split at y `mid`; the
# focus icon sits in an octagon, as the politics screen's
TOP = dict(w=399, h=167, split=109, mid=88, pie=(54.5, 44.5, 35.5), focus=(54.5, 127, 34))


def top_block():
    W, H, sx, my = TOP["w"], TOP["h"], TOP["split"], TOP["mid"]
    cx, cy, r = TOP["pie"]
    return (f'<div style="position:absolute;inset:0;background:{STRIPES},linear-gradient(180deg,#17222A,#0E1519)"></div>'
            + svg(W, H,
                  well(3, 3, sx - 3, my - 2) + well(sx + 1, 3, W - 3, my - 2) + well(3, my + 2, sx - 3, H - 3)
                  + well(sx + 1, my + 2, W - 3, H - 3)
                  + fan((sx + W) / 2, my - 6, 58)
                  + f'<circle cx="{cx}" cy="{cy}" r="{r + 4}" fill="#0A0F12" stroke="url(#g)" stroke-width="1.6"/>'
                  + f'<circle cx="{cx}" cy="{cy}" r="{r + 1}" fill="none" stroke="{LINE}"/>'
                  + "".join(f'<path d="M{cx + dx * (r + 4)},{cy}l{dx * 4},-3v6z" fill="#C9A55A"/>' for dx in (-1, 1))
                  + octagon(*TOP["focus"])))


def octagon(cx, cy, r):
    """the focus icon's socket, the politics screen's: an octagon in a gilt rim with a fainter line inside"""
    import math
    def pts(rr):
        return " ".join(f"{cx + rr * math.cos(math.radians(22.5 + 45 * k)):.1f},{cy + rr * math.sin(math.radians(22.5 + 45 * k)):.1f}"
                        for k in range(8))
    return (f'<polygon points="{pts(r)}" fill="#0A0F12" stroke="url(#g)" stroke-width="1.4"/>'
            f'<polygon points="{pts(r - 4)}" fill="none" stroke="{LINE}"/>')


def pie_overlay():
    """over the game's pie (radius 30, its middle at the overlay's (35.5, 35)), as the politics screen's (v0.11, the
    author: "the ideology wheel should be stylized like the wheel in the politics screen"): a gilt ring at its edge with
    a dark line inside it, and a dark hole in the middle, two thirds of the radius, in a gilt line"""
    c, cy, r = 35.5, 35, 30
    return svg(71, 71, f'<circle cx="{c}" cy="{cy}" r="{r + 1}" fill="none" stroke="#0B1014" stroke-width="2"/>'
                       f'<circle cx="{c}" cy="{cy}" r="{r + 3}" fill="none" stroke="#D2B064" stroke-width="2"/>'
                       f'<circle cx="{c}" cy="{cy}" r="{r * .33:.1f}" fill="#11191E" stroke="#D2B064" stroke-width="1.5"/>')


def goal_button(state):
    """the national focus button: normal, lit (hover), pressed"""
    fill = {"normal": "linear-gradient(180deg,#1A252C,#0E1519)", "lit": "linear-gradient(180deg,#244E46,#13302A)",
            "pressed": DIM_FILL}[state]
    rim = "linear-gradient(180deg,#F1DC9C,#8B6A2C)" if state != "pressed" else "rgba(201,165,90,.6)"
    return (bar(fill, rim, 8, .25 if state == "lit" else .18)
            # v0.11 (the author: "the decoration on the focus button being a repeat of the election box is boring"):
            # an inner line with the flag frame's stepped corner brackets and a gilt diamond at each end, no fan
            + svg(285, 64, f'<path d="{cham(5.5, 5.5, 279.5, 58.5, 5)}" fill="none" stroke="{LINE}"/>'
                  + "".join(f'<path d="M{x},32l4 -4 4 4 -4 4z" fill="#C9A55A"/>' for x in (9, 268)))
            + corner_steps(9, 9, 267, 46, 10, "rgba(227,199,126,.7)"))


def spirits_band():
    """the national spirits band: a well under the tab the game writes its label on (the game's: 0-145 x 10-32)"""
    return svg(520, 92, well(1, 16, 519, 91, 5, "#0E1519")
                       + f'<path d="M1,10H136L150,24V32H1Z" fill="#17222A" stroke="url(#g)"/>'
                       + f'<line x1="6" y1="13" x2="130" y2="13" stroke="rgba(241,220,156,.2)"/>')


def window_header():
    """the short window header: a tab strip across the top, a dark wash under it (the game's is see-through there)"""
    return (f'<div style="position:absolute;left:0;top:22px;right:0;bottom:0;background:rgba(11,16,20,.82);'
            f'box-shadow:inset 0 0 0 1px {LINE}"></div>'
            + svg(233, 112, f'<path d="M0,0H188L210,22H0Z" fill="#17222A" stroke="url(#g)"/>'
                            f'<line x1="4" y1="3" x2="184" y2="3" stroke="rgba(241,220,156,.2)"/>'))


ADDS = [
    ("dv_leader_frame", G + "diplo_leader_frame.dds", 134, 175, leader_frame),
    ("dv_flag_frame", G + "diplo_flag_frame.dds", 134, 80, flag_frame),
    ("dv_top", G + "diplo_top_bg_diplo_tab.dds", 399, 167, top_block),
    ("dv_pie_overlay", G + "pol_piechart_overlay.dds", 71, 71, pie_overlay),
    ("dv_upper", G + "diplo_upper_win_bg.dds", 399, 71,
     lambda: bar(c=7) + svg(399, 71, f'<line x1="95" y1="8" x2="95" y2="63" stroke="{LINE}"/>')),
    ("dv_binding", G + "diplo_countrylist_binding.dds", 533, 35, lambda: bar(c=6)),
    ("dv_goal", G + "diplo_goal_button.dds", 855, 64,
     lambda: frames(855, 64, goal_button("normal"), goal_button("lit"), goal_button("pressed"))),
    ("dv_goal_progress", G + "pol_goal_progress_frame.dds", 239, 8,
     lambda: f'<div style="position:absolute;inset:0;box-shadow:inset 0 0 0 1px #C9A55A"></div>'),
    ("dv_spirits", G + "diplo_nat_spirits_bg.dds", 520, 92, spirits_band),
    ("dv_unity", G + "diplo_unity_bg.dds", 42, 62, lambda: svg(42, 62, well(1, 1, 41, 61, 4))),
    ("dv_text_203", G + "generic_text_bg_203.dds", 203, 27,
     lambda: '<div style="position:absolute;inset:0;background:#0A0F12;box-shadow:inset 0 0 0 1px rgba(201,165,90,.35)"></div>'),
    ("dv_header_short", G + "win_header_short.dds", 233, 112, window_header),
]
