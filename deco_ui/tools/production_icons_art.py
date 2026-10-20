"""The factories, dockyards and production screen's own icons in the Deco style, everywhere the game shows them
(2026-10-20, the author's go-ahead on their notes of 2026-10-19: "The new military factory, civilian factory, and
dockyard icons should take the place of the old ones throughout the game. For example, the production units and the
dropdown beneath the factory side both use the vanilla icons. Likewise, the resource deficit icons still use the base
artwork"; "Dockyard output, factory output, and I think one or two more of the icons on this line don't use our
designs"). The approved icons of proposals_icons.py (the military factory, the dockyard) are the models; civilian
factories are the same works in the top bar's orange (military green, naval blue, civilian orange: make_topbar.py).

At the game's paths, sizes and frames:
  factory_icon.dds, factory_icon_half.dds   15 x 22 x 18   a production line's factories: five states (the game's
      green, light grey, red, dark grey, tan as jade, silver, coral, slate, amber), one each, then five, then ten;
      the half factory the works' left half, its right half a faint outline
  naval_factory_icon.dds                    15 x 26 x 18   the same for dockyards (steel for the game's blue); its first
      frame is also the production header's dockyard output
  production_output_icon.dds (28 x 27)      the works and a crate of goods: factory output
  production_efficiency_loss_icon.dds (24 x 19)  efficiency_icon's bars under a coral line falling to an arrow
  missing_resources_strip.dds               7 x 27 x 27    the resources (proposals_icons.RESOURCES) in a coral glow ring:
      the resource deficit icons
  texticons/mil_factory, civ_factory, civ_factory_output (18 x 18), nav_dockyard (20 x 20), industry (21 x 21: the
      factory output), dismantle_military_industry (18 x 18: the works under a coral cross)   the factories in text
  the filters under the factory sides (2 frames of 45 x 32, refit 45 x 35: off, then on with its check): infantry and
      artillery (the helmet and the howitzer), armour, air (the air tab's jet), capital ships (a gem and an anchor),
      screens (an anchor), other ships (a submarine over a freighter); resources, outdated, stockpiling, reinforcing,
      upgrading, refitting, as the game's subjects
  naval_repair_view_button.dds              3 x 81 x 41    the anchor and wrench beside the dockyards' add-a-line
      button, in its plate (normal, hover, unavailable)

gen_textures.py adds them (keys pf_*). preview_production_icons.py draws them beside the game's.
"""
import proposals_icons as PI

GI = "gfx/interface/"
GOLD, LIT, RULE, INK = PI.GOLD, PI.LIT, PI.RULE, "#0B1014"
EXTRA = ('<defs><linearGradient id="civ" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F4BE6E"/>'
         '<stop offset="1" stop-color="#A8601E"/></linearGradient>'
         '<linearGradient id="coral" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F4A797"/>'
         '<stop offset="1" stop-color="#B04A3A"/></linearGradient>'
         '<linearGradient id="slate" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#58656C"/>'
         '<stop offset="1" stop-color="#2A3337"/></linearGradient>'
         '<linearGradient id="amber" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F0CB7A"/>'
         '<stop offset="1" stop-color="#A27028"/></linearGradient>'
         '<linearGradient id="bronze" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#A9825A"/>'
         '<stop offset="1" stop-color="#5E4128"/></linearGradient>'
         '<linearGradient id="lac" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#18232A"/>'
         '<stop offset="1" stop-color="#0D1418"/></linearGradient>'
         '<linearGradient id="lit" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1F443B"/>'
         '<stop offset="1" stop-color="#112A25"/></linearGradient>'
         '<radialGradient id="deficit" cx=".5" cy=".5" r=".5"><stop offset=".45" stop-color="rgba(238,140,126,.55)"/>'
         '<stop offset="1" stop-color="rgba(238,140,126,0)"/></radialGradient></defs>')


def svg(w, h, body):
    return f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="position:absolute;left:0;top:0">{PI.DEFS}{EXTRA}{body}</svg>'


def at(x, body, y=0):
    return f'<g transform="translate({x},{y})">{body}</g>'


def place(body, box, to, keep=True):
    """body drawn in box (x0, y0, x1, y1) scaled into to (x0, y0, x1, y1), centred, its aspect kept"""
    bw, bh = box[2] - box[0], box[3] - box[1]
    tw, th = to[2] - to[0], to[3] - to[1]
    s = min(tw / bw, th / bh)
    tx = to[0] + (tw - bw * s) / 2 - box[0] * s
    ty = to[1] + (th - bh * s) / 2 - box[1] * s
    return f'<g transform="translate({tx:.2f},{ty:.2f}) scale({s:.4f})">{body}</g>'


def outline(colour="url(#g)", width=1.2):
    # strokes keep their width however a glyph is scaled
    return f'stroke="{colour}" stroke-width="{width}" stroke-linejoin="round" vector-effect="non-scaling-stroke"'


# ------------------------------------------------------------------ the works (proposals_icons' factory) and dockyard
WORKS = "M2.5,21.5V11L8,14V11L13.5,14V11L19,14V3H21.5V7H24V21.5Z"
WORKS_BOX = (2.5, 3, 24, 21.5)
FILLS = ["url(#jade)", "url(#silver)", "url(#coral)", "url(#slate)", "url(#amber)"]       # the game's five states
NAVAL_FILLS = ["url(#steel)"] + FILLS[1:]


def works(fill, rim=None, width=1.0):
    rim = rim or ("rgba(201,165,90,.5)" if fill == "url(#slate)" else "url(#g)")
    return f'<path d="{WORKS}" fill="{fill}" {outline(rim, width)}/>'


def dockyard(fill):
    return PI.dockyard().replace("url(#steel)", fill)


DOCK_BOX = (1.5, 3.5, 27.5, 20)


def times(n, x, y, fill, size):
    return (f'<text x="{x}" y="{y}" font-family="Josefin Sans" font-weight="700" font-size="{size}" fill="{fill}" '
            f'stroke="{INK}" stroke-width="1.6" paint-order="stroke" letter-spacing="-.3">x{n}</text>')


def count_strip(glyph, box, fills, fw, fh):
    """the game's 15 frames: five states, one each, then x5, then x10"""
    out = []
    for n in (1, 5, 10):
        for fill in fills:
            g = glyph(fill)
            if n == 1:
                out.append(place(g, box, (1, 1, fw - 1, fh - 1)))
            else:
                t = "url(#g)" if fill in ("url(#jade)", "url(#steel)") else fill
                out.append(place(g, box, (0.5, 5, fw * .52, fh - 1)) +
                           times(n, fw * .45 if n == 5 else fw * .38, fh - 3, t, 10 if n == 5 else 8.6))
    return "".join(at(fw * i, o) for i, o in enumerate(out))


def half_works(fill):
    """the works' left half filled, its right half a faint outline (the game's half factory: a part of one)"""
    return (f'<clipPath id="hl{fill[5:-1]}"><rect x="0" y="0" width="13.3" height="23"/></clipPath>'
            f'<clipPath id="hr{fill[5:-1]}"><rect x="13.3" y="0" width="14" height="23"/></clipPath>'
            f'<g clip-path="url(#hl{fill[5:-1]})">{works(fill)}</g>'
            f'<g clip-path="url(#hr{fill[5:-1]})"><path d="{WORKS}" fill="none" {outline("rgba(201,165,90,.45)", .8)}/></g>')


# ------------------------------------------------------------------ the production header's line
CRATE = (f'<path d="M14.5,15.5L20.5,13L26.5,15.5V23L20.5,25.5L14.5,23Z" fill="url(#bar)" {outline()}/>'
         f'<path d="M14.5,15.5L20.5,18L26.5,15.5M20.5,18V25.5" fill="none" stroke="{INK}" stroke-width=".8"/>'
         f'<path d="M16.5,16.6L22.5,14.1" stroke="{LIT}" stroke-width=".8" opacity=".7"/>')
OUTPUT = place(works("url(#jade)"), WORKS_BOX, (0.5, 4, 19, 24)) + CRATE
DOWN = [(2, 3.5), (7, 8), (12, 5.5), (17.5, 12)]


def efficiency_loss():
    def ly(x):
        for (x0, y0), (x1, y1) in zip(DOWN, DOWN[1:]):
            if x0 <= x <= x1:
                return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
        return DOWN[-1][1]
    bars = "".join(f'<rect x="{x}" y="{ly(x + 1.3) + 3:.1f}" width="2.6" height="{15.5 - ly(x + 1.3):.1f}" '
                   f'fill="url(#bar)" stroke="{INK}" stroke-width=".6"/>' for x in (2.5, 6.8, 11.1, 15.4))
    line = "M" + " L".join(f"{x},{y}" for x, y in DOWN) + " L20,14.6"
    return (bars + PI.outlined(line, "#EE8C7E", 1.8)
            + f'<path d="M23.4,18.4L17.3,17.6L22.4,12.6Z" fill="#EE8C7E" stroke="{INK}" stroke-width=".8" stroke-linejoin="round"/>')


def deficit(art):
    return ('<circle cx="13.5" cy="13.5" r="13" fill="url(#deficit)"/>'
            '<circle cx="13.5" cy="13.5" r="12.2" fill="none" stroke="#EE8C7E" stroke-width="1.1" opacity=".85"/>' + art)


# ------------------------------------------------------------------ text icons
TEXT_MIL = place(works("url(#jade)"), WORKS_BOX, (0.5, 1, 17.5, 17))
TEXT_CIV = place(works("url(#civ)"), WORKS_BOX, (0.5, 1, 17.5, 17))
TEXT_CIV_OUT = (place(works("url(#civ)"), WORKS_BOX, (0, 3, 13.5, 17.5))
                + PI.outlined("M10.5,14.5L16,6.5", LIT, 1.5)
                + f'<path d="M17.6,3.2L17.2,9L12.6,6.4Z" fill="{LIT}" stroke="{INK}" stroke-width=".7" stroke-linejoin="round"/>')
TEXT_DOCK = place(dockyard("url(#steel)"), DOCK_BOX, (0.5, 2, 19.5, 18))
TEXT_INDUSTRY = place(OUTPUT, (0.5, 4, 26.5, 25.5), (0.5, 1, 20.5, 20))
TEXT_DISMANTLE = (place(works("url(#jade)"), WORKS_BOX, (0.5, 3, 17.5, 17.5))
                  + PI.outlined("M1.5,1.5L8.5,8.5M8.5,1.5L1.5,8.5", "#EE8C7E", 1.8))


# ------------------------------------------------------------------ the helmet and the howitzer, the jet, the ships
HELMET_HOWITZER, HH_BOX = PI.HELMET_HOWITZER, PI.HH_BOX         # the add-a-line buttons' (proposals_icons.py)
JET, JET_BOX = PI.AIR_JET, PI.JET_BOX
ANCHOR = (f'<circle cx="12" cy="4.5" r="2.2" fill="none" stroke="url(#steel)" stroke-width="1.8"/>'
          f'<path d="M12,6.7V21M7.5,10H16.5M4,15.5Q5,21.5 12,21.5Q19,21.5 20,15.5" fill="none" stroke="url(#steel)" '
          f'stroke-width="2" stroke-linecap="round"/>'
          f'<path d="M2.6,17.2L4,14.3L6.2,16.9M21.4,17.2L20,14.3L17.8,16.9" fill="none" stroke="url(#steel)" stroke-width="1.5"/>')
ANCHOR_BOX = (2, 2, 22, 22.5)
GEM = (f'<path d="M5,2L9.5,8L5,14L0.5,8Z" fill="url(#steel)" {outline()}/>'
       f'<path d="M5,2V14M0.5,8H9.5" stroke="{LIT}" stroke-width=".6" opacity=".6"/>')
SUB = (f'<path d="M2,5.5Q2,3 5,3H19Q22,3 22.5,5Q22,7 19,7H5Q2,7 2,5.5Z" fill="url(#steel)" {outline()}/>'
       f'<path d="M9.5,3V0.8H13V3" fill="url(#steel)" {outline()}/>')
FREIGHTER = (f'<path d="M1,13H23L20.5,18H3.5Z" fill="url(#amber)" {outline()}/>'
             f'<path d="M4,13V10H9V13M10.5,13V10.5H16V13M17.5,13V8.5H20.5V13" fill="url(#silver)" {outline()}/>'
             f'<path d="M0,19.5Q3,18.5 6,19.5T12,19.5T18,19.5T24,19.5" fill="none" stroke="url(#steel)" stroke-width="1"/>')


# ------------------------------------------------------------------ the second row's subjects (in 24 x 24)
def arrow_up(fill, mark):
    a = f'<path d="M12,2L21,12H16V21H8V12H3Z" fill="{fill}" {outline()}/>'
    if mark == "cross":
        a += f'<path d="M12,9.5V16.5M8.5,13H15.5" stroke="{INK}" stroke-width="2.2"/>'
    return a


WAREHOUSE = (f'<path d="M2,10L12,3L22,10V21H2Z" fill="url(#jade)" {outline()}/>'
             f'<path d="M6,21V12H18V21" fill="#14201C" stroke="url(#g)" stroke-width=".8"/>'
             + "".join(f'<path d="M6.8,{13.5 + 2 * i}H17.2" stroke="{RULE}" stroke-width=".9"/>' for i in range(4)))
REINFORCE = (PI.outlined("M5,9A8,8 0 0 1 18,6.5", "#4FA884", 1.8) + PI.outlined("M19,15A8,8 0 0 1 6,17.5", "#4FA884", 1.8)
             + f'<path d="M16,3.5L20.5,6.8L15.6,8.6Z" fill="#4FA884" stroke="{INK}" stroke-width=".7"/>'
             + f'<path d="M8,20.5L3.5,17.2L8.4,15.4Z" fill="#4FA884" stroke="{INK}" stroke-width=".7"/>'
             + f'<path d="M10,7.5H14V10H16.5V14H14V16.5H10V14H7.5V10H10Z" fill="#EE8C7E" {outline(INK, .8)}/>')
REFIT = (f'<path d="M12,1.5L19.5,9.5H15V14Q15,17 12,17Q9,17 9,14V9.5H4.5Z" fill="url(#g)" {outline(INK, .8)}/>'
         f'<path d="M1.5,16.5Q12,25 22.5,16.5L21,21.5Q12,26 3,21.5Z" fill="url(#bar)" {outline()}/>')
RESOURCES2 = (place(PI.OIL, (6, 3, 21, 23.5), (0, 1, 12, 20)) + place(PI.STEEL, (3, 9, 24, 19), (8, 8, 24, 19)))


# ------------------------------------------------------------------ the filters' plates (off, on), 45 x 32 frames
def octagon(x0, y0, x1, y1, c):
    return f"M{x0 + c},{y0}H{x1 - c}L{x1},{y0 + c}V{y1 - c}L{x1 - c},{y1}H{x0 + c}L{x0},{y1 - c}V{y0 + c}Z"


CHECK = (f'<path d="M33,24.5l3,3 6.5,-7.5" fill="none" stroke="{INK}" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/>'
         f'<path d="M33,24.5l3,3 6.5,-7.5" fill="none" stroke="{LIT}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>')


def filter_box(art, box, h=32, area=None):
    area = area or (8, 4, 37, h - 5)
    plate = octagon(2.5, 2.5, 42.5, h - 2.5, 6)
    off = (f'<path d="{plate}" fill="url(#lac)" stroke="rgba(201,165,90,.42)"/>'
           f'<g opacity=".72">{place(art, box, area)}</g>')
    on = (f'<path d="{plate}" fill="url(#lit)" stroke="url(#g)" stroke-width="1.2"/>'
          f'<path d="M9,4.5H36" stroke="rgba(241,220,156,.28)"/>{place(art, box, area)}{CHECK}')
    return off + at(45, on)


# ------------------------------------------------------------------ the naval repair button (the add-a-line plate)
# an open-ended wrench, its jaw cut out of the head (a mask, so whatever is under it shows through)
WRENCH = ('<mask id="wjaw" maskUnits="userSpaceOnUse" x="0" y="0" width="30" height="30"><rect width="30" height="30" '
          'fill="white"/><path d="M20.6,7.4L25.2,2.8L27.6,5.2L23,9.8Z" fill="black"/></mask>'
          '<g mask="url(#wjaw)">' + PI.outlined("M6.5,21.5L18.5,9.5", "#C9D1D4", 3.4)
          + '<circle cx="21" cy="7" r="5" fill="#C9D1D4" stroke="#0B1014" stroke-width="1"/></g>'
          + '<path d="M17.5,5.2Q18.5,3.2 20.6,2.6" fill="none" stroke="#FFFFFF" stroke-width=".8" opacity=".7"/>')


def repair_button(state):
    fill = {"normal": "#141E24", "hover": "#1C3A33", "off": "#101418"}[state]
    rim = {"normal": "url(#g)", "hover": "url(#g)", "off": "rgba(201,165,90,.45)"}[state]
    plate = (f'<path d="M5.5,.5H75.5L80.5,5.5V35.5L75.5,40.5H5.5L.5,35.5V5.5Z" fill="{fill}" stroke="{rim}"/>'
             f'<path d="M7,3.5H74" stroke="rgba(241,220,156,{.35 if state == "hover" else .18})"/>')
    art = place(ANCHOR, ANCHOR_BOX, (12, 5, 40, 37)) + place(WRENCH, (4, 2, 26.5, 24), (40, 6, 68, 36))
    if state == "off":
        art = (f'<g opacity=".45" style="filter:grayscale(1)">{art}</g>'
               '<circle cx="47" cy="21" r="11" fill="none" stroke="#EE8C7E" stroke-width="2.4"/>'
               '<path d="M39.5,28.5L54.5,13.5" stroke="#EE8C7E" stroke-width="2.4"/>')
    return plate + art


FILTERS = [  # file (under gfx/interface/), height, art, its box
    ("inf_art_checkbox", 32, HELMET_HOWITZER, HH_BOX),
    ("armour_checkbox", 32, PI.TANK, (4.5, 15, 57.5, 35)),
    ("air_checkbox", 32, JET, JET_BOX),
    ("capital_ships_checkbox", 32, GEM + at(10, ANCHOR, 0), (0, 2, 32, 22.5)),
    ("screen_ships_checkbox", 32, ANCHOR, ANCHOR_BOX),
    ("other_ships_checkbox", 32, SUB + FREIGHTER, (0, 0.5, 24, 20)),
    ("resources_checkbox", 32, RESOURCES2, (0, 1, 24, 20)),
    ("outdated_checkbox", 32, arrow_up("url(#bronze)", "cross"), (3, 2, 21, 21)),
    ("stockpiling_checkbox", 32, WAREHOUSE, (2, 3, 22, 21)),
    ("reinforcing_checkbox", 32, REINFORCE, (3, 3, 21, 21)),
    ("upgrading_checkbox", 32, arrow_up("url(#g)", "cross"), (3, 2, 21, 21)),
    ("refit_checkbox", 35, REFIT, (1.5, 1.5, 22.5, 24)),
]

ADDS = [
    ("pf_factory_icon", GI + "factory_icon.dds", 330, 18,
     lambda: svg(330, 18, count_strip(works, WORKS_BOX, FILLS, 22, 18))),
    ("pf_factory_icon_half", GI + "factory_icon_half.dds", 330, 18,
     lambda: svg(330, 18, count_strip(half_works, (2.5, 3, 24, 21.5), FILLS, 22, 18))),
    ("pf_naval_factory_icon", GI + "naval_factory_icon.dds", 390, 18,
     lambda: svg(390, 18, count_strip(dockyard, DOCK_BOX, NAVAL_FILLS, 26, 18))),
    ("pf_production_output_icon", GI + "production_output_icon.dds", 28, 27, lambda: svg(28, 27, OUTPUT)),
    ("pf_production_efficiency_loss_icon", GI + "production_efficiency_loss_icon.dds", 24, 19,
     lambda: svg(24, 19, efficiency_loss())),
    ("pf_missing_resources_strip", GI + "missing_resources_strip.dds", 189, 27,
     lambda: svg(189, 27, "".join(at(27 * i, deficit(r)) for i, r in enumerate(PI.RESOURCES)))),
    ("pf_text_mil_factory", "gfx/texticons/mil_factory.dds", 18, 18, lambda: svg(18, 18, TEXT_MIL)),
    ("pf_text_civ_factory", "gfx/texticons/civ_factory.dds", 18, 18, lambda: svg(18, 18, TEXT_CIV)),
    ("pf_text_civ_factory_output", "gfx/texticons/civ_factory_output.dds", 18, 18, lambda: svg(18, 18, TEXT_CIV_OUT)),
    ("pf_text_nav_dockyard", "gfx/texticons/nav_dockyard.dds", 20, 20, lambda: svg(20, 20, TEXT_DOCK)),
    ("pf_text_industry", "gfx/texticons/industry.dds", 21, 21, lambda: svg(21, 21, TEXT_INDUSTRY)),
    ("pf_text_dismantle_military_industry", "gfx/texticons/dismantle_military_industry_text_icon.dds", 18, 18,
     lambda: svg(18, 18, TEXT_DISMANTLE)),
    ("pf_naval_repair_view_button", GI + "naval_repair_view_button.dds", 243, 41,
     lambda: svg(243, 41, "".join(at(81 * i, repair_button(s)) for i, s in enumerate(("normal", "hover", "off"))))),
    *[("pf_" + f, GI + f + ".dds", 90, h, (lambda h=h, art=art, box=box: svg(90, h, filter_box(art, box, h))))
      for f, h, art, box in FILTERS],
]
