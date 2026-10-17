"""The sometimes-seen windows whose look is one picture of the game's (2026-10-17, v0.10; docs/SCREEN_INVENTORY.md's
"Game's own" table), redrawn at the game's paths, sizes and frame counts, with their panels where the game's are
(measured from its pictures and from the .gui files that draw on them). The look is window_art.py's (lacquer plate,
double gilt rule, corner brackets, header band, title plate between roundels) and designer_art.py's (raised bands,
recessed panels, the ivory ruled sheet where the game writes dark text). The game's bronze medals become gilt roundels
with a line icon (tools/icons.py), its metal, rivets and photographs plain lacquer.

- trade_offer_popup_win (527 x 437; countrytradeview.gui, tradeoffer_window): the header (the trade roundel, the title
  plate under the country's name at x 132-392, a well behind the flag's frame at 425, 11), a recessed panel for the
  trade and convoy lines (x 13-292, y 80-256; the trade partners box, a core skin tile, sits right of it at 294), a
  raised band for the factories and the slider (y 259-371); and diplo_action_bottom (521 x 72), the plate the game
  lays at (7, 367) under Close and Send (the only live use of that picture: the diplomacy view's is commented out);
- equipment_upgrade_designer_bg (545 x 416; the variant designer and the market's stockpile window, the same layout):
  the title band and the close socket, the panel for the equipment and its upgrades (y 47-235) with the name's plate
  (the edit box at 125, 49) and a faint sunburst behind the equipment's picture, the ivory sheet (y 240-353, a rule at
  x 272 between the grid's two columns, dotted lines under its 21 px rows: the game writes the statistics there in the
  dark typewriter ink, hoi4_typewriter16_inverted), the footer band (y 356-410);
- agency_upgrades_popup_bg (1092 x 91; the intelligence agency's upgrades window): the header over the branches' list
  (a core skin tile from y 75): the title plate (x 262-830), two roundels with the intelligence eye and speed lines,
  the close socket (the button at 1048, 6) and a strip for the upgrade duration (x 146-946, y 54);
- army_insignia_selection_bg (317 x 444; the agency's name and logo window and the faction's logo window, a cornered
  tile 380 x 540 with borders 64 x 222 and a stretched centre; the army insignia and the faction colour pickers, a
  plain picture at its own size): the header band, the close socket (the button at x 282 in the plain windows, 342 in
  the 380 px ones: texture x 279-313 either way), the footer band (y 391-437: the 540 px windows' buttons at 491 fall
  on it, as the plain ones' checkbox and OK at 395-431). Its middle columns (64-253) and the rows round 222 are
  uniform, and it has no pinstripes, since the cornered tile stretches them;
- strategic_air_bg (552 x 436; the air view over a region, drawn at (-4, -5) of its window and past its foot): the
  region's name band, the close socket, the wing types' cells (icon | count, four a side, two rows), the weather well,
  the strip for detection, efficiency and Details (y 112-148), a night-blue field for the air battle (y 150-428) split
  by a raised band (y 224-270) under the missions row (Our Missions, the game's three mission buttons, Enemy Missions);
- naval_region_bg (433 x 300; naval_strategic_region_view.gui): a gilt frame round the terrain picture (10, 36), a
  recessed panel behind the eight counts (y 145-223), a band for naval access (its buttons at 21-122, 248) and the
  sunk ships' log (378, 245); naval_region_header (435 x 62, at (0, -2): the anchor roundel, the title plate under the
  region's name at 42-398, the close socket at 398, 7) and naval_region_dominance_header_bg (414 x 37, at (10, 106):
  a lacquer bar with gilt diamonds for the game's rivets, a well behind the dominant country's flag);
- tutorial_bg (613 x 576; the tutorial's 20 windows): window_art's hint_bg (title plate between roundels, footer band)
  with a band for "Objectives" (y 399-427) and a recessed well for the objectives' lines (y 432-508);
- the settings window (settings.gui, menu_settings_ingame): settings_popup_bg (480 x 527: the band and the title plate
  under "Options", centred on y 44); diplo_popup_bottom (494 x 72: the plate behind the tabs, and the footer plate of
  ten popups in popupwindow.gui, the credits, the multiplayer connect window and the legacy message popup: a chamfered
  lacquer plate fits them all); fullborder_tiled (190 x 190, a cornered tile, border 64, its centre clear: the frame
  under the tabs); the tabs (tab_small_110: lit in frame 1, as the game's other tabs); the option rows (generic_bg_417,
  also the multiplayer connect window's fields); the key box (generic_box_96, the settings' only live use: the top
  bar's manpower box is the Deco UI's own); the volume sliders' thumb, track and arrows (scrollbar_slider_2,
  scrollbar_sliderbackground, scrollbar_leftbutton / rightbutton: the game's 4 frames are one picture, so are these; the
  arrows serve the game setup's sliders too); and checkbox_gold_32 (the message settings and the AI settings windows).
  Left as the game's: the Video and Game tabs' arrow buttons (button_left, button_right: validate_preview.py reads every
  gfx/interface/button_*.dds as button_<w>x<h>), GFX_checkbox (live only in the Paradox account window; the settings'
  uses are commented out) and the legacy pieces (tab_settings, button_type_2: the old menu_settings window).

Each .gfx naming a .tga gets the .dds of the same name (section 6), so these are .dds. gen_textures.py adds them (keys
pp_*). Textures only: no .gui or .gfx is changed.
"""
from art_util import DIM_FILL, GOLD, STRIPES, bar, frames, lit_bar
from designer_art import band as raised, gilt_line, inset, sheet
from icons import icon
from window_art import HEAD, LAC, RIM, WELL, diamond, plate, roundel

DARK = "linear-gradient(180deg,#0B1115,#080C0F)"
PANEL = "linear-gradient(180deg,#121B21,#0C1216)"
SOCKET = "linear-gradient(180deg,#0E1519,#0A0F12)"


def at(x, y, w, h, inner="", style=""):
    return f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;{style}">{inner}</div>'


def shell(x, y, w, h, fill=LAC, skip=()):
    """window_art's plate at (x, y): lacquer, a double gilt rule, gilt corner brackets (skip: tl, tr, bl, br)"""
    out = (at(x, y, w, h, style=f"background:{fill};box-shadow:inset 0 0 0 1px rgba(0,0,0,.6)")
           + f'<div class="frame" style="left:{x + 1}px;top:{y + 1}px;width:{w - 2}px;height:{h - 2}px;border:1px solid {RIM}"></div>'
           + f'<div class="frame" style="left:{x + 5}px;top:{y + 5}px;width:{w - 10}px;height:{h - 10}px;'
           'border:1px solid rgba(201,165,90,.45)"></div>')
    for k, (cx, cy, tf) in {"tl": (x + 2, y + 2, "none"), "tr": (x + w - 18, y + 2, "scaleX(-1)"),
                            "bl": (x + 2, y + h - 18, "scaleY(-1)"), "br": (x + w - 18, y + h - 18, "scale(-1,-1)")}.items():
        if k not in skip:
            out += f'<i class="ck" style="left:{cx}px;top:{cy}px;transform:{tf}"></i>'
    return out


def hband(x0, x1, y0, y1, fill=HEAD, top=False, bottom=True):
    """window_art's band between x0 and x1: gilt rules along its edges (a bright one and a faint one 3 px out)"""
    w = x1 - x0
    out = at(x0, y0, w, y1 - y0, style=f"background:{fill}")
    if bottom:
        out += at(x0, y1, w, 1, style="background:rgba(201,165,90,.8)") + at(x0, y1 + 3, w, 1, style="background:rgba(201,165,90,.3)")
    if top:
        out += at(x0, y0 - 1, w, 1, style="background:rgba(201,165,90,.8)") + at(x0, y0 - 4, w, 1, style="background:rgba(201,165,90,.3)")
    return out


def emblem(cx, cy, r, name):
    """window_art's roundel with one of the line icons in place of its star"""
    size = round(2 * (r - 8) * .9)
    sw = round(1.7 * 24 / size, 2)
    return (f'<div style="position:absolute;left:{cx - r}px;top:{cy - r}px;width:{2 * r}px;height:{2 * r}px;border-radius:50%;'
            f'background:{GOLD}"></div>'
            f'<div style="position:absolute;left:{cx - r + 2.5}px;top:{cy - r + 2.5}px;width:{2 * r - 5}px;height:{2 * r - 5}px;'
            'border-radius:50%;background:radial-gradient(circle,#1E2B33,#0A1014 75%)"></div>'
            f'<div style="position:absolute;left:{cx - r + 6}px;top:{cy - r + 6}px;width:{2 * r - 12}px;height:{2 * r - 12}px;'
            'border-radius:50%;border:1px solid rgba(201,165,90,.55)"></div>'
            + at(cx - size / 2, cy - size / 2, size, size, icon(name, size, "#E3C77E", sw)))


def wings(x0, x1, cy, toward_right, gap=6, n=3):
    """speed lines from an emblem (at x0 when toward_right, else at x1) fading toward the other end, the middle one
    longest"""
    out = ""
    for i, dy in enumerate(range(-(n // 2) * gap, (n // 2) * gap + 1, gap)):
        cut = abs(dy) // gap * 18
        a, b = (x0, x1 - cut) if toward_right else (x0 + cut, x1)
        grad = "90deg,#C9A55A,rgba(201,165,90,0)" if toward_right else "90deg,rgba(201,165,90,0),#C9A55A"
        out += at(a, cy + dy, b - a, 1, style=f"background:linear-gradient({grad})")
    return out


def socket(x0, y0, x1, y1):
    """the recess a close button sits in"""
    return inset((x0, y0, x1, y1), SOCKET, "rgba(201,165,90,.7)")


def ruled(x0, y0, x1, y1, cols, rows):
    """designer_art's ivory sheet without a header row: a double rule along its top, column rules, dotted rows"""
    return sheet(x0, y0, x1, y1, y0, cols, rows)


def foot_plate(x0, y0, x1, y1):
    """a raised chamfered plate under a row of buttons, its shadow under it"""
    w, h = x1 - x0, y1 - y0
    return (at(x0 + 3, y1, w - 6, 10, style="background:linear-gradient(180deg,rgba(0,0,0,.55),rgba(0,0,0,0))")
            + at(x0, y0, w, h, bar(f"{STRIPES},linear-gradient(180deg,#1B262D,#0E1519)", "rgba(201,165,90,.75)", 6, .25))
            + diamond(x0 + 12, (y0 + y1) / 2, 2.5) + diamond(x1 - 12, (y0 + y1) / 2, 2.5))


# ---------------------------------------------------------------- the trade offer
def trade_offer():
    """527 x 437: header (y 9-74), the info panel (x 13-292; the trade text's box runs to 299) and the trade partners'
    place (y 80-256), the factories' and slider's band (259-371), the footer under diplo_action_bottom (373-427)"""
    return (shell(3, 3, 521, 430)
            + hband(9, 518, 9, 74)
            + emblem(56, 41, 27, "trade")
            + plate(102, 19, 420, 63)
            + inset((423, 10, 517, 70), "linear-gradient(180deg,#0A1014,#070B0E)", "rgba(201,165,90,.7)")
            + inset((13, 81, 292, 256), PANEL)
            + gilt_line(9, 259, 518, 259, "rgba(201,165,90,.8)") + raised(9, 260, 518, 371)
            + hband(9, 518, 374, 427, fill=WELL, top=True, bottom=False))


def trade_offer_foot():
    """diplo_action_bottom, 521 x 72: the plate (x 11-510, y 8-53, the game's) under Close (x 63) and Send (x 343)"""
    return foot_plate(11, 8, 510, 53)


# ---------------------------------------------------------------- the variant designer (and the market's stockpile window)
def sunburst(cx, cy, r, alpha=.13):
    return (f'<div style="position:absolute;left:{cx - r}px;top:{cy - r}px;width:{2 * r}px;height:{2 * r}px;border-radius:50%;'
            f'background:repeating-conic-gradient(rgba(227,199,126,{alpha}) 0deg 2.5deg,transparent 2.5deg 10deg);'
            '-webkit-mask:radial-gradient(circle,#000 25%,transparent 72%)"></div>'
            f'<div style="position:absolute;left:{cx - r * .62}px;top:{cy - r * .62}px;width:{r * 1.24}px;height:{r * 1.24}px;'
            'border-radius:50%;border:1px solid rgba(201,165,90,.22)"></div>')


def variant_designer():
    w, h = 545, 416
    rows = [266 + 21 * k for k in range(5)]
    return (shell(0, 0, w, h, skip=("tr",))
            + raised(6, 6, w - 6, 43) + gilt_line(6, 43, w - 6, 43)
            + socket(499, 7, 539, 43)
            + inset((13, 47, 532, 235), PANEL)
            + sunburst(272, 158, 92)
            + inset((120, 49, 429, 81), DARK, "rgba(201,165,90,.75)")
            + ruled(16, 240, 530, 354, [(271, 273)], rows[:-1] + [350])
            + gilt_line(6, 358, w - 6, 358) + raised(6, 360, w - 6, 410))


# ---------------------------------------------------------------- the intelligence agency
def agency_upgrades():
    """1092 x 91: the window's head, open at the foot (the branches' tile starts at y 75)"""
    w = 1092
    out = (at(0, 2, w, 73, style=f"background:{LAC}")
           + at(1, 3, w - 2, 71, style=f"border:1px solid {RIM};border-top-width:1px")
           + at(5, 7, w - 10, 68, style="border:1px solid rgba(201,165,90,.45);border-bottom:none")
           + '<i class="ck" style="left:2px;top:4px"></i>'
           + hband(6, w - 6, 8, 46)
           + wings(132, 258, 36, True) + wings(834, 960, 36, False)
           + plate(262, 7, 830, 45)
           + emblem(102, 38, 28, "intel") + emblem(990, 38, 28, "intel")
           + socket(1044, 5, 1086, 44)
           + inset((146, 52, 946, 72), DARK, "rgba(201,165,90,.55)")
           + diamond(158, 62, 2.5) + diamond(934, 62, 2.5))
    return out


def insignia():
    """317 x 444, also a cornered tile (borders 64 x 222, centre stretched): uniform in x 64-253 and round row 222"""
    w, h = 317, 444
    fill = "linear-gradient(180deg,#151F26 0,#10181D 130px,#10181D 320px,#0D1418 100%)"
    head = "linear-gradient(180deg,#1C2830,#141E24)"
    return (shell(0, 0, w, h, fill=fill, skip=("tr",))
            + hband(6, w - 6, 6, 37, fill=head)
            + socket(275, 4, 314, 38)
            + hband(6, w - 6, 391, h - 6, fill=head, top=True, bottom=False))


# ---------------------------------------------------------------- the air view over a region
def strategic_air():
    """552 x 436, drawn at (-4, -5) of its 552 x 327 window and past its foot (the air battle's lists)"""
    out = (shell(4, 3, 544, 431, skip=("tr",))
           + hband(10, 542, 9, 32)
           + socket(511, 4, 545, 34))
    # the wing types: icon | count (the game's at 12-46 | 46-76 and 83-117 | 117-147, mirrored on the right)
    for y0, y1 in ((36, 64), (73, 101)):
        for x0, x1, div in ((11, 77, 46), (82, 148, 117), (402, 468, 433), (473, 539, 504)):
            out += inset((x0, y0, x1, y1), DARK) + at(div, y0 + 3, 1, y1 - y0 - 6, style="background:rgba(201,165,90,.45)")
    out += (inset((149, 34, 405, 105), DARK)
            + at(9, 107, 534, 1, style="background:rgba(201,165,90,.8)") + at(9, 110, 534, 1, style="background:rgba(201,165,90,.3)")
            + raised(9, 112, 543, 148)
            # the air battle: the sky over the missions band, the ground missions under it
            + at(9, 149, 534, 75, style="background:" + STRIPES + ",linear-gradient(180deg,#1B2C39,#142430 60%,#11202A)")
            + at(9, 271, 534, 158, style="background:" + STRIPES + ",linear-gradient(180deg,#111D25,#0C151B)"))
    for y in (176, 198, 214):
        out += at(30, y, 492, 1, style="background:linear-gradient(90deg,rgba(201,165,90,0),rgba(201,165,90,.09) 30%,"
                                       "rgba(201,165,90,.09) 70%,rgba(201,165,90,0))")
    out += (f'<div style="position:absolute;left:156px;top:144px;width:240px;height:160px;'
            'background:repeating-conic-gradient(from -90deg at 50% 50%,rgba(227,199,126,.07) 0deg 2deg,transparent 2deg 9deg);'
            '-webkit-mask:linear-gradient(180deg,#000 0,#000 50%,transparent 50%),radial-gradient(circle at 50% 50%,#000 20%,transparent 70%);'
            '-webkit-mask-composite:source-in;mask-composite:intersect"></div>'
            + hband(9, 543, 225, 268, top=True))
    return out


# ---------------------------------------------------------------- the naval region view
def naval_region():
    """433 x 300 (its window is 438 wide; the header picture lies over its top)"""
    w, h = 433, 300
    return (shell(0, 0, w, h)
            + at(9, 35, 416, 73, style="background:#070B0E;box-shadow:0 0 0 1px #B8954F,0 0 0 3px rgba(11,16,20,.9),0 0 0 4px rgba(201,165,90,.35)")
            + inset((10, 146, 424, 223), PANEL)
            + gilt_line(6, 226, w - 6, 226, "rgba(201,165,90,.8)") + raised(6, 227, w - 6, 294)
            + inset((15, 245, 128, 287), DARK) + inset((372, 241, 421, 287), DARK))


def naval_header():
    """435 x 62, laid at (0, -2): the band (y 2-38) under the region's name (x 42-398) and the close button (398, 7)"""
    w = 435
    return (at(0, 2, w, 37, style=f"background:{HEAD};box-shadow:inset 0 0 0 1px rgba(0,0,0,.6)")
            + at(1, 3, w - 2, 35, style=f"border:1px solid {RIM}")
            + at(5, 7, w - 10, 27, style="border:1px solid rgba(201,165,90,.45)")
            + at(0, 39, w, 1, style="background:rgba(201,165,90,.3)")
            + plate(44, 6, 392, 35)
            + emblem(23, 20, 16, "navy")
            + socket(394, 5, 428, 36))


def naval_dominance():
    """414 x 37, at (10, 106): the dominance icon (80, 8), the bar's frame (110, 9), the dominant flag (350, 6)"""
    return (at(0, 1, 414, 35, bar(f"{STRIPES},linear-gradient(180deg,#1B262D,#10181D)", "rgba(201,165,90,.6)", 5, .2))
            + diamond(12, 18.5, 3) + diamond(402, 18.5, 3)
            + inset((346, 4, 381, 32), DARK, "rgba(201,165,90,.55)"))


# ---------------------------------------------------------------- the tutorial
def tutorial():
    """613 x 576: window_art's hint_bg (the same size, header and footer), a band for "Objectives" (y 403) and a well
    for the objectives (y 434-491)"""
    w, h = 613, 570
    return (shell(0, 0, w, h) + hband(6, w - 6, 6, 72) + plate(100, 18, w - 100, 62)
            + roundel(50, 39, 29) + roundel(w - 50, 39, 29)
            + hband(6, w - 6, 399, 427, top=True)
            + inset((18, 433, w - 18, 508), DARK, "rgba(201,165,90,.45)")
            + hband(6, w - 6, 516, h - 6, top=True, bottom=False))


# ---------------------------------------------------------------- the settings
def settings():
    """480 x 527 (its window 480 x 600): the title plate under "Options" (the box at 105-355, y 25; hoi_36header puts
    its capitals 7-31 px under the box's top, the deco face's 11-28, so the title is centred on y 44), the band down to
    the tab bar (diplo_popup_bottom at -7, 53, its plate from y 61); the frame under the tabs (fullborder_tiled at 6,
    92) lies over the rest"""
    return (shell(2, 2, 476, 523)
            + hband(8, 472, 8, 60)
            + plate(92, 22, 368, 58)
            + roundel(48, 40, 16) + roundel(412, 40, 16))


def popup_bottom():
    """diplo_popup_bottom, 494 x 72: the plate (x 12-482, y 8-53, the game's) behind the settings' tabs and under the
    popups' buttons"""
    return foot_plate(12, 8, 482, 53)


def settings_frame():
    """fullborder_tiled, 190 x 190, a cornered tile (border 64) with a clear centre: a double gilt rule"""
    return ('<div class="frame" style="inset:1px;border:1px solid #B8954F"></div>'
            '<div class="frame" style="inset:5px;border:1px solid rgba(201,165,90,.45)"></div>'
            '<i class="ck sm tl"></i><i class="ck sm tr"></i><i class="ck sm bl"></i><i class="ck sm br"></i>')


def arrow(w, h, rot, size=None):
    """a gilt triangle (pointing up, turned by rot) on a small chamfered lacquer plate"""
    s = size or min(w, h)
    return (bar(c=3, shine=.15)
            + f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="position:absolute;left:0;top:0">'
            '<defs><linearGradient id="pa" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F1DC9C"/>'
            '<stop offset="1" stop-color="#9C7A36"/></linearGradient></defs>'
            f'<g transform="rotate({rot} {w / 2} {h / 2})"><path d="M{w / 2} {h / 2 - s * .24}L{w / 2 + s * .27} {h / 2 + s * .2}'
            f'H{w / 2 - s * .27}z" fill="url(#pa)" stroke="#0B1014" stroke-width=".8" stroke-linejoin="round"/></g></svg>')


def thumb(dim=False):
    g = "linear-gradient(135deg,#9A968C,#5E5B55)" if dim else GOLD
    return ('<div style="position:absolute;left:3px;top:3px;width:10px;height:10px;transform:rotate(45deg);'
            f'background:{g};box-shadow:0 0 0 1px #0B1014"></div>'
            '<div style="position:absolute;left:5.5px;top:5.5px;width:5px;height:5px;transform:rotate(45deg);background:#0B1014"></div>'
            '<div style="position:absolute;left:7px;top:7px;width:2px;height:2px;transform:rotate(45deg);background:#F1DC9C"></div>')


def year_track():
    """scrollbar_sliderbackground, 16 x 16, a cornered tile (border 4) along the slider: a slim dark groove"""
    return ('<div style="position:absolute;left:1px;right:1px;top:5px;height:6px;background:#070A0C;border-radius:3px;'
            'box-shadow:0 0 0 1px rgba(201,165,90,.55)"></div>')


def gold_check(on):
    """checkbox_gold_32 (32 x 32 a frame): the core skin's checkbox (generic_checkbox) at this size"""
    if not on:
        return '<div style="position:absolute;left:6px;top:6px;width:20px;height:20px;background:#0A0F12;box-shadow:inset 0 0 0 1px #C9A55A"></div>'
    return ('<div style="position:absolute;left:6px;top:6px;width:20px;height:20px;background:#163A33;box-shadow:inset 0 0 0 1px #E3C77E"></div>'
            '<svg width="32" height="32" viewBox="0 0 32 32" style="position:absolute;left:0;top:0"><path d="M10.5 16l4 4 8-9" '
            'fill="none" stroke="#F1DC9C" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>')


GI = "gfx/interface/"
ADDS = [
    ("pp_trade_offer", GI + "tradeview/trade_offer_popup_win.dds", 527, 437, trade_offer),
    ("pp_trade_offer_foot", GI + "diplo_action_bottom.dds", 521, 72, trade_offer_foot),
    ("pp_variant_designer", GI + "equipment_upgrade_designer_bg.dds", 545, 416, variant_designer),
    ("pp_agency_upgrades", GI + "operatives/agency_upgrades_popup_bg.dds", 1092, 91, agency_upgrades),
    ("pp_insignia", GI + "army_insignia_selection_bg.dds", 317, 444, insignia),
    ("pp_strategic_air", GI + "strategicair/strategic_air_bg.dds", 552, 436, strategic_air),
    ("pp_naval_region", GI + "strategicnavy/naval_region_bg.dds", 433, 300, naval_region),
    ("pp_naval_header", GI + "strategicnavy/naval_region_header.dds", 435, 62, naval_header),
    ("pp_naval_dominance", GI + "strategicnavy/naval_region_dominance_header_bg.dds", 414, 37, naval_dominance),
    ("pp_tutorial", GI + "tutorial/tutorial_bg.dds", 613, 576, tutorial),
    ("pp_settings", GI + "settings_popup_bg.dds", 480, 527, settings),
    ("pp_popup_bottom", GI + "diplo_popup_bottom.dds", 494, 72, popup_bottom),
    ("pp_settings_frame", GI + "fullborder_tiled.dds", 190, 190, settings_frame),
    ("pp_settings_tab", GI + "tab_small_110.dds", 210, 37,
     lambda: frames(210, 37, lit_bar(6), bar(DIM_FILL, "rgba(201,165,90,.4)", 6, .1))),
    ("pp_settings_row", GI + "generic_bg_417.dds", 417, 29,
     lambda: bar("linear-gradient(180deg,#0E1519,#0A0F12)", "rgba(201,165,90,.35)", 4, .06)),
    ("pp_settings_box", GI + "generic_box_96.dds", 96, 26,
     lambda: '<div style="position:absolute;inset:0;background:#0A0F12;box-shadow:inset 0 0 0 1px rgba(201,165,90,.35)"></div>'),
    ("pp_year_thumb", GI + "scrollbar_slider_2.dds", 64, 16, lambda: frames(64, 16, *[thumb()] * 4)),
    ("pp_year_track", GI + "scrollbar_sliderbackground.dds", 16, 16, year_track),
    ("pp_year_left", GI + "scrollbar_leftbutton.dds", 92, 21, lambda: frames(92, 21, *[arrow(23, 21, 270)] * 4)),
    ("pp_year_right", GI + "scrollbar_rightbutton.dds", 92, 21, lambda: frames(92, 21, *[arrow(23, 21, 90)] * 4)),
    # the settings' Video and Game tab arrows (core.gfx GFX_button_left names a .tga: the game loads the .dds first)
    ("pp_settings_left", GI + "button_left.dds", 23, 21, lambda: arrow(23, 21, 270)),
    ("pp_settings_right", GI + "button_right.dds", 23, 21, lambda: arrow(23, 21, 90)),
    ("pp_gold_checkbox", GI + "checkbox_gold_32.dds", 64, 32, lambda: frames(64, 32, gold_check(False), gold_check(True))),
]
