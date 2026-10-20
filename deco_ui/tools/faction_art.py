"""The faction screen's goal slots drawn by hand (the author, 2026-10-19: "the faction goals have an odd appearance where
the lined background appears at the top, then there's a gold line, then a solid color it seems. I think it might be
supposed to look like a folder? But the text sits over the entire thing and looks odd with it intersecting the line").
The panel pictures' automatic translation (make_panel_pictures.py) had read the game's gradient (light at the top) as
two parts, a pinstriped band and a dark body with a gilt edge between them, right through the goal's name; the slot is
one plate now, its icon and name on an even ground. The game's three frames (open, completed with a check, failed with
a cross; 162 x 88 each) at its path; the marks where the game's are.

gen_textures.py draws ADDS (prefix fg_)."""
from art_util import frames

W, H = 162, 88


def pts(p):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in p)


def poly(x0, y0, x1, y1, c):
    return [(x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c), (x1 - c, y1), (x0 + c, y1), (x0, y1 - c), (x0, y0 + c)]


def slot(mark=None):
    m = ""
    if mark == "done":       # the game's check: about x 124-146, y 30-50
        m = ('<polyline points="126,41 133,48 146,31" fill="none" stroke="#0B1014" stroke-width="5.5" '
             'stroke-linecap="round" stroke-linejoin="round"/>'
             '<polyline points="126,41 133,48 146,31" fill="none" stroke="#E3C77E" stroke-width="2.6" '
             'stroke-linecap="round" stroke-linejoin="round"/>')
    elif mark == "failed":   # the game's cross: about x 123-145, y 29-51
        m = ('<path d="M126 31 L144 49 M144 31 L126 49" stroke="#0B1014" stroke-width="5.5" stroke-linecap="round"/>'
             '<path d="M126 31 L144 49 M144 31 L126 49" stroke="rgb(238,140,126)" stroke-width="2.6" stroke-linecap="round"/>')
    return (f'<svg width="{W}" height="{H}" style="position:absolute;left:0;top:0">'
            '<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E8CD84"/>'
            '<stop offset="1" stop-color="#8B6A2C"/></linearGradient>'
            '<linearGradient id="f" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#17222A"/>'
            '<stop offset="1" stop-color="#0E1519"/></linearGradient>'
            '<pattern id="pin" width="8" height="8" patternUnits="userSpaceOnUse">'
            '<rect x="0" y="0" width="1" height="8" fill="rgba(255,255,255,.022)"/></pattern></defs>'
            f'<polygon points="{pts(poly(2.8, 2.8, W - 2.8, H - 2.8, 8))}" fill="url(#f)" stroke="url(#g)" stroke-width="1.6"/>'
            f'<polygon points="{pts(poly(2.8, 2.8, W - 2.8, H - 2.8, 8))}" fill="url(#pin)"/>'
            f'<polygon points="{pts(poly(6, 6, W - 6, H - 6, 6))}" fill="none" stroke="rgba(201,165,90,.26)" stroke-width="1"/>'
            f'{m}</svg>')


ADDS = [
    ("fg_goal_slot", "gfx/interface/factions/ui/faction_goal_slot.dds", W * 3, H,
     lambda: frames(W * 3, H, slot(), slot("done"), slot("failed"))),
]
