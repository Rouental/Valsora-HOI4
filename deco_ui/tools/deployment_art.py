"""The deployment panel's training lines in the Deco style (the author, 2026-10-19: "The training bar looks very odd with
cutoff text and random lines"): the division being trained (military_deployment_conveyor_view, 490 x 84), its lines
(military_deployment_line_view, 514 x 40), the summary of a folded one (518 x 40), the rule under the last line, the
location and Add Unit buttons and the add limit's badge, drawn by hand at the game's paths and sizes. The conveyor's
picture had come from the panel pictures' automatic translation (make_panel_pictures.py), which left the game's rail as
ragged gilt specks along the top, specks of its hatched name well that read as cut-off text over the name, and a stray
oval under Add Unit. The wells sit where the game's do (measured on its pictures), under the elements
countrydeploymentview.gui puts there; the progress bars, the equipment and training icons and the round buttons stay
the game's.

gen_textures.py draws ADDS (prefix dl_)."""
from art_util import frames

GI = "gfx/interface/"
LAC = "#141E24"
GILT = ("#E8CD84", "#8B6A2C")


def poly(x0, y0, x1, y1, c):
    return [(x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c), (x1 - c, y1), (x0 + c, y1), (x0, y1 - c), (x0, y0 + c)]


def pts(p):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in p)


def svg(w, h, body):
    return (f'<svg width="{w}" height="{h}" style="position:absolute;left:0;top:0">'
            '<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{GILT[0]}"/><stop offset="1" stop-color="{GILT[1]}"/></linearGradient>'
            '<linearGradient id="lac" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1A262E"/>'
            '<stop offset="1" stop-color="#0E1519"/></linearGradient>'
            '<linearGradient id="jade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2C665A"/>'
            '<stop offset="1" stop-color="#163A33"/></linearGradient>'
            '<pattern id="pin" width="8" height="8" patternUnits="userSpaceOnUse">'
            '<rect x="0" y="0" width="1" height="8" fill="rgba(255,255,255,.025)"/></pattern></defs>'
            f'{body}</svg>')


def plate(w, h, c=7, fill="url(#lac)", rim="url(#g)", inset=.8, hair=True):
    """a chamfered lacquer plate filling the picture, a gilt rim and a hairline 3.5 px inside"""
    b = (f'<polygon points="{pts(poly(inset, inset, w - inset, h - inset, c))}" fill="{fill}" stroke="{rim}" '
         'stroke-width="1.6"/>'
         f'<polygon points="{pts(poly(inset, inset, w - inset, h - inset, c))}" fill="url(#pin)"/>')
    if hair:
        b += (f'<polygon points="{pts(poly(3.5, 3.5, w - 3.5, h - 3.5, max(1, c - 2)))}" fill="none" '
              'stroke="rgba(201,165,90,.28)" stroke-width="1"/>')
    return b


def well(x0, y0, x1, y1, c=4):
    """a recessed dark well with a gilt hairline"""
    return (f'<polygon points="{pts(poly(x0 + .5, y0 + .5, x1 - .5, y1 - .5, c))}" fill="#090E11" '
            'stroke="rgba(201,165,90,.55)" stroke-width="1"/>'
            f'<line x1="{x0 + c}" y1="{y0 + 1.5}" x2="{x1 - c}" y2="{y0 + 1.5}" stroke="rgba(0,0,0,.6)" stroke-width="1"/>')


def keyhole(x0, x1, y0, y1):
    """the game's keyhole well (its x0-x1, y0-y1): a round socket for an icon, a slot for its progress bar"""
    r = (y1 - y0) / 2
    cx, cy = x0 + r, (y0 + y1) / 2
    return (well(cx, cy - 8.5, x1, cy + 8.5, 3)
            + f'<circle cx="{cx}" cy="{cy}" r="{r - .5}" fill="#090E11" stroke="rgba(201,165,90,.55)" stroke-width="1"/>')


def conveyor():
    # 490 x 84 under the template icon (12,22) and priority (62,22), the name (100,18 200 x 25), the amount (312-413,
    # 10-40) and the priorities (420-480, 17); the location (91,46 223 x 31) and Add Unit (315,50 105 x 23) buttons and
    # the deploy and cancel buttons (421-479, 47) on the plate below
    b = plate(490, 84, 8)
    b += well(7, 10, 85, 76, 7)                           # the template's icon
    b += well(92, 15, 312, 40, 4)                         # the name
    b += well(320, 15, 409, 38, 4)                        # the amount, between the - and + buttons
    b += f'<line x1="92" y1="44" x2="478" y2="44" stroke="rgba(201,165,90,.22)" stroke-width="1"/>'
    return svg(490, 84, b)


def line():
    # 514 x 40 (the line window at x -13, 520 wide): the division's name (5,5 150 x 30), equipment (icon 214,12, bar
    # 235,13 68 x 12), training (icon 306,6, bar 329,13), the series number (398-463, 11), deploy (458,7) and cancel (484,7)
    b = plate(514, 40, 6)
    b += well(5, 8, 204, 32, 4)
    b += keyhole(211, 303, 6, 32)
    b += keyhole(306, 398, 6, 32)
    b += well(403, 10, 456, 30, 3)
    return svg(514, 40, b)


def add_line():
    # 518 x 40 (the summary of a folded conveyor, at x -15, 510 wide): the order buttons (11 and 36, 4), equipment (icon
    # 215,7, bar 237,9), the lines' count (330-450, 8), the fold button (481,4)
    b = plate(518, 40, 6)
    b += keyhole(213, 305, 3, 26)
    b += well(318, 6, 460, 28, 3)
    return svg(518, 40, b)


def end_line():
    # 516 x 11, under the last line (at x -14, y -3): a gilt rule on a lacquer sill, the ends chamfered
    return svg(516, 11, f'<polygon points="{pts(poly(1, 1, 515, 10, 4))}" fill="url(#lac)"/>'
                        '<line x1="5" y1="2.5" x2="511" y2="2.5" stroke="url(#g)" stroke-width="1.6"/>'
                        '<line x1="8" y1="6.5" x2="508" y2="6.5" stroke="rgba(201,165,90,.25)" stroke-width="1"/>')


def location(lit):
    # 223 x 31 a frame: the group button's round socket at the left (its frame at (3, 2), 27 x 27), the text centred
    fill = "url(#jade)" if lit else "url(#lac)"
    b = plate(223, 31, 6, fill, hair=False)
    b += (f'<circle cx="16.5" cy="15.5" r="13" fill="#090E11" stroke="url(#g)" stroke-width="1.4"/>'
          f'<line x1="34" y1="4" x2="216" y2="4" stroke="rgba(241,220,156,{.35 if lit else .2})" stroke-width="1"/>')
    return svg(223, 31, b)


def add_button(lit):
    fill = "url(#jade)" if lit else "url(#lac)"
    b = plate(105, 23, 5, fill, hair=False)
    b += f'<line x1="7" y1="3.5" x2="98" y2="3.5" stroke="rgba(241,220,156,{.4 if lit else .22})" stroke-width="1"/>'
    return svg(105, 23, b)


def limit():
    return svg(21, 19, plate(21, 19, 4, "#090E11", hair=False))


ADDS = [
    ("dl_conveyor", GI + "military_deployment_conveyor_bg.dds", 490, 84, conveyor),
    ("dl_line", GI + "military_deployment_line_bg.dds", 514, 40, line),
    ("dl_add_line", GI + "military_deployment_add_line_bg.dds", 518, 40, add_line),
    ("dl_end_line", GI + "military_deployment_end_line.dds", 516, 11, end_line),
    ("dl_location", GI + "conveyor_location_btn.dds", 446, 31, lambda: frames(446, 31, location(False), location(True))),
    ("dl_add_button", GI + "military_deployment_add_line_btn.dds", 210, 23,
     lambda: frames(210, 23, add_button(False), add_button(True))),
    ("dl_limit", GI + "add_limit_bg.dds", 21, 19, limit),
]
