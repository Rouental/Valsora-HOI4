"""The side panels' own pictures drawn by hand (2026-10-21; the author: "with a lot of the things you've generated
recently, there's these weird sloppy lines and missing pieces of the design"): they replace the automatic translations
of make_panel_pictures.py (proposals_panel_mockups.translate, which traced the game's thin lines into broken gilt
fragments), each at the game's path, size and frame count, its boxes where the game's .gui puts its texts and icons.

Group C (keys pc_*), measured on the game's pictures and from the .gui elements drawn on them (picture coordinates):
  construction_screen_top (433 x 98; countryconstructionsview.gui, at (5, 37) + the panels' shift): a chamfered plate
      to row 92 (the production list covers it from row 93), two wells side by side where production_win_top's texts
      sit (x 6-257: the civilian works, "From trade" and "Owned"; x 262-423: the construction speed and the resources,
      ending 4 px short of the building list, which hangs over the plate from x 428), a rule across at row 60 and under
      it the column headers' band, cut in four cells (rules at x 175, 248, 330) under Location, Task, the factories'
      icon and #, and Priority.
  subview_header_bg_375x101 (countrydeploymentview.gui templatedeploymentwindow, countryofficercorpview.gui
      armyhqtemplatewindow; at (1, 0)): square, its rim on the window frame's own rule (cols 0 and 372, row 1) so the
      frame runs on below it; the title band (rows 2-45, the centred title, the officers' close button), a gilt rule
      at row 46, and below it a darker compartment for the foreign templates' button, the special forces count and the
      designer button (the decommissioned templates' bar covers its last rows in the deployment window).
  logistics_win_bottom (548 x 96; production_win_bottom, LOWER_LEFT): the footer is the panel body's own frame (its
      double rule, corner brackets and lacquer show through: the picture is clear there); a hairline box on the body's
      inner hairline (cols 4 and 543, row 92, drawn in its colour so it closes by itself too) and across at row 2, so the
      fuel list's rule above it (row -2) and this one make a double rule with the frame's own 3 px spacing; two hairlines
      cut it into three bays, one for each card (military, naval, nuclear; GFX_mini_tooltip at x 19, 204, 390), with a
      gilt lozenge at the cards' middle. (assumed) the game draws a spriteType background at its own size, not stretched
      to the container's 546 x 98.
  linechart_frame (235 x 162; logistics_info_window, logistics_fuel_window): a 5 px ring round the chart's 225 x 151
      background at (4, 5), outer gilt rim chamfered, inner gilt hairline on the background's outermost pixels; the
      middle (x 5-227, y 6-154) transparent.
  tradeview/trade_filter_bg (504 x 128): not used by countrytradeview.gui but by countrylogisticsview.gui, twice: as
      the resources strip (resource_strip_container, 25 px tall, its icons drawn down to row 31 and the list's header
      at row 36, so (assumed) the container doesn't clip) and behind the fuel cards (fuel_info, where the binding header
      covers rows 0-34 and the cards the rest). So: a dark well at rows 1-33 behind the resources, clear below.
  occupation/occupation_header_bg (521 x 65; countryoccupationview.gui header, at (14, -1)): a chamfered plate in
      three bays (rules at x 264 and 407): Territory Management (its title, the garrison and law buttons), Foreign
      Support (its title and amount box), the resistance and compliance tabs (which hang 4 px below the plate, as the
      game's do).
  occupation/occupation_country_entry_bg_top (519 x 121; occupied_territory_country_entry, at (-5, 0)): a plate with
      the name tab at its top left (a gilt-washed field behind the flag, name and state count, bounded by one line from
      the left rim along row 36 and up a 45-degree cut to the top rim at x 276), the state facts' well (manpower,
      industry, resources; x 26-272, clear of the expand button at x 4-22) and the buttons' well along the foot
      (garrison, release / return, occupation law). _locked is the same with a hatched well at the right (x 281-510,
      rows 6-78) where the resistance and compliance bars would be.
  occupation/occupation_state_entry_bg (508 x 63; occupied_territory_state_entry): a plate cut by one stepped line
      (row 26 on the left, a 45-degree step at x 243-262, row 7 on the right) into the state's name above and the dark
      field below it (the garrison, the resistance bar with its modifiers above it, compliance, the law button); rows
      60-62 are left clear (the next entry starts there).
  occupation/occupation_garrison_select_entry_bg (3 x 504 x 45; the law and garrison pickers' rows): one chamfered
      plate (x 6-499, y 2-42) per frame: lacquer with a gilt rim (frame 1, normal), jade with a bright rim (frame 2,
      assumed the selected or hovered row: the game's is lit gold), dim with a faint rim (frame 3, assumed pressed or
      unavailable: the game's is grey).
  theater/theater_group_bg (5 x 305 x 77; theatreselector.gui, factions/faction_ping_window.gui): a chamfered plate
      (x 2-302, y 2-73) with the name well at its top left (x 6-208: the settings button, the name, the supply
      priority), the right of the top band free for the combat and priority buttons, a rule at row 38 above the lower
      band (which the game's assign button covers). The frames differ only by their tone, as the game's: 1 bronze (a
      faction's theatre), 2 pewter (an army's), 3 steel blue (a navy's), 4 indigo hatched (the reserve fleet), 5 lacquer
      red (the air force's).

gen_textures.py draws ADDS (prefix pc_); every SVG id here starts with "pc", so these pictures look the same whatever
else is drawn on the page.
"""
from art_util import frames

GI = "gfx/interface/"
RULE = "#C9A55A"
GOLD = "#E3C77E"
HAIR = "rgba(201,165,90,.55)"         # a well's rim
FAINT = "rgba(201,165,90,.30)"        # dividers
SHINE = "rgba(241,220,156,.10)"
WIN_RULE = "rgba(184,149,79,.6)"     # the core skin's thin window rule (gen_textures.window, rule "thin")
WELL = "#0A0F12"


def _lin(i, top, bottom):
    def stop(off, c):
        if c.startswith("rgba"):
            *rgb, a = c[5:-1].split(",")
            return f'<stop offset="{off}" stop-color="rgb({",".join(rgb)})" stop-opacity="{a}"/>'
        return f'<stop offset="{off}" stop-color="{c}"/>'
    return f'<linearGradient id="{i}" x1="0" y1="0" x2="0" y2="1">{stop(0, top)}{stop(1, bottom)}</linearGradient>'


DEFS = ("<defs>" + _lin("pcg", "#E8CD84", "#8B6A2C") + _lin("pclac", "#17222A", "#0E1519")
        + _lin("pclac2", "#1A262E", "#11191E") + _lin("pcjade", "#2C665A", "#163A33") + _lin("pcdim", "#121A1F", "#0B1014")
        + _lin("pcwash", "rgba(201,165,90,.17)", "rgba(201,165,90,.05)")
        + '<pattern id="pcpin" width="8" height="8" patternUnits="userSpaceOnUse">'
          '<rect width="1" height="8" fill="rgba(255,255,255,.025)"/></pattern>'
        + '<pattern id="pchatch" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
          '<rect width="4" height="10" fill="rgba(201,165,90,.09)"/></pattern>'
        + "</defs>")


def svg(w, h, body, defs=""):
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="position:absolute;left:0;top:0">'
            f"{DEFS}{defs}{body}</svg>")


# ------------------------------------------------------------------ shapes, in pixel edges: (x0, y0, x1, y1) covers
# the pixels x0..x1-1 and y0..y1-1, so a rim (a 1 px stroke half a pixel in) lands on whole pixels
def cham(x0, y0, x1, y1, c, corners=(1, 1, 1, 1)):
    """a rectangle's path, its corners (top left, top right, bottom right, bottom left) cut by c where 1"""
    tl, tr, br, bl = (c * k for k in corners)
    return f"M{x0 + tl},{y0}H{x1 - tr}L{x1},{y0 + tr}V{y1 - br}L{x1 - br},{y1}H{x0 + bl}L{x0},{y1 - bl}V{y0 + tl}Z"


def fill(d, colour):
    return f'<path d="{d}" fill="{colour}"/>'


def stroke(d, colour, w=1):
    return f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{w}" stroke-linejoin="miter"/>'


def hline(x0, x1, y, colour):
    return f'<path d="M{x0},{y + .5}H{x1}" stroke="{colour}" stroke-width="1"/>'


def vline(x, y0, y1, colour):
    return f'<path d="M{x + .5},{y0}V{y1}" stroke="{colour}" stroke-width="1"/>'


def plate(x0, y0, x1, y1, c, fill_="url(#pclac)", rim="url(#pcg)", pin=True, corners=(1, 1, 1, 1)):
    """a plate over the pixels (x0..x1-1, y0..y1-1): lacquer, the faint pinstripe, a 1 px rim on its outermost pixels"""
    k = c + .3 if c else 0
    out = fill(cham(x0, y0, x1, y1, k, corners), fill_)
    if pin:
        out += fill(cham(x0, y0, x1, y1, k, corners), "url(#pcpin)")
    return out + stroke(cham(x0 + .5, y0 + .5, x1 - .5, y1 - .5, c, corners), rim)


def well(x0, y0, x1, y1, c=3, fill_=WELL, rim=HAIR):
    return plate(x0, y0, x1, y1, c, fill_, rim, pin=False)


def lozenge(cx, cy, r, colour=GOLD, rim="#8B6A2C"):
    return (f'<path d="M{cx},{cy - r}L{cx + r},{cy}L{cx},{cy + r}L{cx - r},{cy}Z" fill="{colour}" stroke="{rim}" '
            'stroke-width=".8" stroke-linejoin="miter"/>')


# ------------------------------------------------------------------ the construction screen's top
def construction_top():
    b = plate(0, 0, 433, 93, 5)
    b += well(6, 5, 258, 56, 4) + well(262, 5, 424, 56, 4)
    b += hline(1, 432, 60, RULE)
    for x in (175, 248, 330):
        b += vline(x, 61, 92, FAINT)
    return svg(433, 98, b)


# ------------------------------------------------------------------ the template windows' header
def subview_header():
    b = fill("M0,1H373V101H0Z", "url(#pclac2)") + fill("M0,1H373V101H0Z", "url(#pcpin)")
    b += fill("M1,47H372V100H1Z", "#0E1519") + fill("M1,47H372V100H1Z", "url(#pcpin)")
    b += hline(4, 369, 3, SHINE)
    b += hline(1, 372, 46, RULE)
    b += stroke("M.5,1.5H372.5V100.5H.5Z", WIN_RULE)
    return svg(375, 101, b)


# ------------------------------------------------------------------ the logistics footer
def logistics_bottom():
    # the panel body's inner hairline (gen_textures pol_body: rgba(201,165,90,.45) on its lacquer) lies under this
    # picture at cols 4 and 543 and row 92; it is drawn here in its own colour, opaque, so the footer's box is closed
    # by itself too and looks the same in place; the rest is clear, so the body's lacquer and brackets show through
    inner = "rgb(100,88,57)"
    b = stroke("M4.5,2.5H543.5V92.5H4.5Z", inner)
    for x in (176, 362):
        b += vline(x, 3, 92, FAINT) + lozenge(x + .5, 42.5, 4)
    return svg(548, 96, b)


# ------------------------------------------------------------------ the line chart's frame
def linechart_frame():
    ring = (cham(0, 1, 233, 161, 3.3) + " " + "M5,6V155H228V6Z")
    b = f'<path d="{ring}" fill="#0E1519" fill-rule="evenodd"/>'
    b += stroke(cham(.5, 1.5, 232.5, 160.5, 3), "url(#pcg)")
    b += stroke("M4.5,5.5H228.5V155.5H4.5Z", "rgba(227,199,126,.7)")
    return svg(235, 162, b)


# ------------------------------------------------------------------ the logistics resources strip
def trade_filter():
    return svg(504, 128, well(0, 1, 504, 34, 4, "url(#pcdim)", "rgba(201,165,90,.6)"))


# ------------------------------------------------------------------ occupation
def occupation_header():
    b = plate(0, 0, 516, 65, 5)
    b += hline(6, 510, 2, SHINE)
    for x in (264, 407):
        b += vline(x, 1, 64, FAINT)
    return svg(521, 65, b)


def country_top(locked):
    b = plate(3, 1, 515, 119, 5)
    # the name tab: a gilt wash bounded by one line, from the left rim along row 36 and up a 45-degree cut to the top
    tab = "M4,6L8,2H277L242,37H4Z"
    b += fill(tab, "url(#pcwash)")
    b += stroke("M3.5,36.5H242.5L276.5,2.5V1.5", RULE)
    b += well(26, 42, 273, 79, 4)
    b += well(7, 82, 511, 116, 4)
    if locked:
        b += well(281, 6, 511, 79, 4, "#0B1013") + fill(cham(282, 7, 510, 78, 3.3), "url(#pchatch)")
    return svg(519, 121, b)


def state_entry():
    b = plate(2, 1, 506, 60, 4)
    field = "M3,27H243L262,8H505V55.5L501.5,59H6.5L3,55.5Z"
    b += fill(field, "#0B1014")
    b += stroke("M2.5,26.5H243.5L262.5,7.5H505.5", RULE)
    return svg(508, 63, b)


def garrison_entry(state):
    fill_, rim, shine = {"normal": ("url(#pclac)", "rgba(201,165,90,.6)", .10),
                         "lit": ("url(#pcjade)", GOLD, .30),
                         "dim": ("url(#pcdim)", "rgba(201,165,90,.25)", 0)}[state]
    b = plate(6, 2, 500, 43, 5, fill_, rim)
    if shine:
        b += hline(12, 494, 4, f"rgba(241,220,156,{shine})")
    return svg(504, 45, b)


# ------------------------------------------------------------------ the theatres' groups: five tones, one shape
TONES = [  # (top band's top, its foot, the lower band)
    ("#4C3D20", "#2B2314", "#1C1810"),     # 1 bronze: a faction's theatre
    ("#4A4F52", "#2A2E31", "#1B1E20"),     # 2 pewter: an army's theatre
    ("#24455C", "#14283A", "#101C28"),     # 3 steel blue: a navy's
    ("#2C3159", "#191C37", "#121429"),     # 4 indigo, hatched: the reserve fleet
    ("#5C211D", "#331210", "#230D0B"),     # 5 lacquer red: the air force's
]


def theater(i):
    top, foot, low = TONES[i]
    tid = f"pct{i}"
    defs = "<defs>" + _lin(tid, top, foot) + "</defs>"
    shape = cham(2, 2, 303, 74, 5.3)
    b = fill(shape, f"url(#{tid})") + fill("M3,39H302V69L298,73H7L3,69Z", low) + fill(shape, "url(#pcpin)")
    if i == 3:
        b += fill(shape, "url(#pchatch)")
    b += well(6, 7, 209, 35, 5)
    b += hline(3, 302, 38, RULE)
    b += stroke(cham(2.5, 2.5, 302.5, 73.5, 5), "url(#pcg)")
    return svg(305, 77, b, defs)


ADDS = [
    ("pc_construction_top", GI + "construction_screen_top.dds", 433, 98, construction_top),
    ("pc_subview_header", GI + "subview_header_bg_375x101.dds", 375, 101, subview_header),
    ("pc_logistics_bottom", GI + "logistics_win_bottom.dds", 548, 96, logistics_bottom),
    ("pc_linechart_frame", GI + "linechart_frame.dds", 235, 162, linechart_frame),
    ("pc_trade_filter", GI + "tradeview/trade_filter_bg.dds", 504, 128, trade_filter),
    ("pc_occupation_header", GI + "occupation/occupation_header_bg.dds", 521, 65, occupation_header),
    ("pc_occupation_top", GI + "occupation/occupation_country_entry_bg_top.dds", 519, 121, lambda: country_top(False)),
    ("pc_occupation_top_locked", GI + "occupation/occupation_country_entry_bg_top_locked.dds", 519, 121,
     lambda: country_top(True)),
    ("pc_occupation_state", GI + "occupation/occupation_state_entry_bg.dds", 508, 63, state_entry),
    ("pc_occupation_garrison", GI + "occupation/occupation_garrison_select_entry_bg.dds", 1512, 45,
     lambda: frames(1512, 45, *(garrison_entry(s) for s in ("normal", "lit", "dim")))),
    ("pc_theater_group", GI + "theater/theater_group_bg.dds", 1525, 77,
     lambda: frames(1525, 77, *(theater(i) for i in range(5)))),
]
