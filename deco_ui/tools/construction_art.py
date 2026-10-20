"""The construction screen's buttons and icons in the Deco style (2026-10-20, the author's go-ahead on their note of
2026-10-19: "On the construction screen, icons currently run into their headers. Let's take this opportunity both to
fix that, and to stylize the buttons and icons to better fit the UI. For now just remake the icons more of less 1 to
1, but in the color palette of the UI. The buttons should be subtle octagons").

The headers: each category's header picture (diplo_details_header, gen_textures.py) holds its plate in its top 42 px
now, clear of the category's first row of buildings; its icon sits on the plate's left end as an octagonal medallion.

At the game's paths, sizes and frames:
  buildings/building_icon_strip.dds   31 x 46 x 46   every building, the construction screen's buttons (and the state
      panel's, the tech tree's, the special projects'): a subtle octagon of lacquer with a faint gilt rim, the game's
      subject on it about 1 to 1 in gilt (the game's orange), jade (its green), steel (its blue), silver (its grey)
  state_constructions (41 x 39), shared_constructions (40 x 39), province_constructions (39 x 39),
      special_project/facility_constructions (39 x 39)   the categories' medallions: a flag on its plinth, an
      excavator, a compass rose's needle, gears and a flask
  tutorial/construction_glow_overlay.dds   2 x 48 x 48   a building's highlight, the octagon's rim lit (it pulses)
  buildings/building_status_overlay.dds    3 x 46 x 46   over a building: a stopwatch, the swap arrows, a wrench
  building_repair.dds                      2 x 42 x 42   a building to repair: a coral octagon, then with a wrench
  convert_ic_button.dds (46 x 46)          civilian works to military and back, on the buildings' octagon
  add_one, add_5, add_10 (26 x 26), subtract_one, subtract_5, subtract_10 (25 x 25)   the factory count's buttons
  non_available_factory_icon, construction/civ_factory_output_icon, factory_wrench_icon (27 x 23)   the civilian works
      (orange, as the top bar's), with the output's arrow, with a wrench; construction_speed_icon (28 x 19)
  consumer_goods_icon (44 x 35), tradeview/traded_factories_icon (41 x 43), projects_factories_icon (46 x 42),
      construction/ongoing_market_contract_icon (44 x 36), backhoe_icon_small (26 x 16): the special rows' icons
  texticons/consumer_goods_texticon (20 x 20)

gen_textures.py adds them (keys cn_*). preview_production_icons.py draws them beside the game's.
"""
import production_icons_art as PF
import proposals_icons as PI

GI = "gfx/interface/"
GOLD, LIT, RULE, INK = PI.GOLD, PI.LIT, PI.RULE, "#0B1014"
svg, at, place, octagon, works = PF.svg, PF.at, PF.place, PF.octagon, PF.works
O = PF.outline()                          # the gilt outline, its width kept however a glyph is scaled
D = PF.outline(INK, .9)                   # a dark one


def g(d, fill="url(#g)", o=O):
    return f'<path d="{d}" fill="{fill}" {o}/>'


def ln(d, colour=GOLD, w=1.6):
    return f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>'


# ------------------------------------------------------------------ the subjects, each in a 30 x 30 box
CIV = "url(#civ)"
WAVES = ln("M1,25Q4,23 7,25T13,25T19,25T25,25T31,25", "#6E8FB0", 1.4) + ln("M1,28.5Q4,26.5 7,28.5T13,28.5T19,28.5T25,28.5T31,28.5", "#6E8FB0", 1.4)
JET = PF.place(PF.JET, PF.JET_BOX, (0, 0, 30, 30))
ANCHOR = PF.place(PF.ANCHOR, PF.ANCHOR_BOX, (0, 0, 30, 30))
WRENCH = PF.WRENCH                         # in about 4..26 x 2..24
CRATE = (g("M2,12L11,8L20,12V23L11,27L2,23Z", "url(#bar)") + ln("M2,12L11,16L20,12M11,16V27", INK, .9)
         + ln("M4.5,13.2L13.5,9.2", LIT, .8))


def jet(box):
    return place(PF.JET, PF.JET_BOX, box)


def pylon():
    return (ln("M15,2L9,28M15,2L21,28M11.5,17H18.5M10.2,22.5H19.8M13,9.5H17", GOLD, 1.5)
            + ln("M6,7H24M7.5,13H22.5", GOLD, 1.5) + ln("M12.6,9.5L17.4,17M17.4,9.5L12.6,17M11.5,17L19.8,22.5M18.5,17L10.2,22.5", RULE, .8)
            + ln("M7,28H23", GOLD, 1.8))


BOLT = g("M21,4L13,17H18L15,28L25,13H20L23,4Z", "url(#g)")
TREFOIL = ("<g transform='translate(15,15)'>"
           + "".join(f'<path d="M0,0L-5.2,-9A10.4,10.4 0 0 1 5.2,-9Z" fill="url(#g)" {O} transform="rotate({a})"/>'
                     for a in (0, 120, 240))
           + f'<circle r="2.6" fill="url(#g)" {O}/></g>')

B = [None] * 31
B[0] = (place(works(CIV), PF.WORKS_BOX, (8, 1, 30, 19))                                   # civilian industry
        + g("M1,20H22V22.2H13.5V24.8H22V27H1V24.8H9.5V22.2H1Z", "url(#silver)"))
B[1] = place(works("url(#jade)"), PF.WORKS_BOX, (9, 2, 30, 21)) + place(WRENCH, (4, 2, 26.5, 24), (0, 9, 18, 29))   # arms
B[2] = (g("M2,29C2,19 18,18 15,11C14,7 11,5 12,1H18C18,4 22,6.5 22.5,11C24.5,21 13,21 15,29Z")             # roads
        + ln("M8.5,26.5C9,21.5 17.5,19 18.8,13M18.4,8.5C18,6 16.2,4.5 15.4,2.5", INK, 1.1))
B[3] = place(PF.dockyard("url(#steel)"), PF.DOCK_BOX, (0, 3, 30, 27))                     # dockyard
B[4] = (ln("M4,28V3", GOLD, 1.8) + g("M4.5,4L15,6.5V11L4.5,12Z", "url(#civ)")             # air base
        + ln("M8,5V11.5M12,6V10.8", "#F4ECD9", 1.2) + jet((11, 9, 30, 29)))
B[5] = ANCHOR                                                                             # naval base
B[6] = g("M2,22L7,11H23L28,22Z") + g("M9,15H21V17H9Z", INK) + ln("M2,25H28", RULE, 1.4)   # land fort
B[7] = g("M4,17L8,7H22L26,17Z") + g("M10,10.5H20V12.3H10Z", INK) + WAVES                  # coastal fort
B[8] = (jet((6, 0, 24, 13)) + g("M4,26H22L19,20H7Z") + g("M11,21L13,16H16L17,21Z")        # anti-air
        + ln("M14,17.5L26,10M15,19L27,12.5", GOLD, 1.8))
B[9] = (g("M3,28V12H8V28ZM10,28V7H15V28Z") + ln("M8,15H10M5.5,12V8L12.5,4L17,9", GOLD, 1.4)   # synthetic refinery
        + PF.place(PI.OIL, (6, 3, 21, 23.5), (15, 8, 29, 28)))
B[10] = (ln("M15,4L10,28M15,4L20,28M11.6,20H18.4M12.8,13H17.2M7.5,28H22.5", GOLD, 1.6)      # radar
         + "".join(ln(f"M{15 - r},{11 - r * .55}A{r},{r} 0 0 0 {15 - r},{11 + r * .55}", "#C9D1D4", 1.3)
                   + ln(f"M{15 + r},{11 - r * .55}A{r},{r} 0 0 1 {15 + r},{11 + r * .55}", "#C9D1D4", 1.3) for r in (6, 10)))
B[11] = (g("M23,2L26.5,5.5L12,20L8,16Z") + g("M8,16L4,22L10,20Z", "url(#civ)")              # rocket site
         + ln("M7,23L26,23M9,23L14,28M24,23L19,28M5,28H28", GOLD, 1.5) + ln("M15,17L20,23", RULE, 1.2))
B[12] = ("".join(f'<ellipse cx="15" cy="15" rx="13" ry="5" fill="none" stroke="url(#g)" stroke-width="1.6" '   # reactor
                 f'transform="rotate({a} 15 15)"/>' for a in (0, 60, 120)) + f'<circle cx="15" cy="15" r="3" fill="url(#g)" {O}/>')
B[13] = (g("M3,9Q3,5 8,5Q13,5 13,9V24H3Z") + ln("M5,24L4,28M11,24L12,28M13,14H17V22", GOLD, 1.3)   # fuel silo
         + "".join(g(f"M{x},{y}H{x + 6}V{y + 8}H{x}Z", "url(#silver)") for x, y in ((17, 12), (23, 12), (20, 20))))
B[14] = place(CRATE, (2, 8, 20, 27), (11, 2, 29, 21)) + place(CRATE, (2, 8, 20, 27), (1, 10, 19, 29))   # supply hub
B[15] = ("frame", None)                                                                   # railway: RAIL below
B[16] = jet((1, 0, 29, 30))                                                               # air facility
B[17] = (g("M10,4H20L22,22H8Z", "url(#civ)") + ln("M15,2V22", GOLD, 1.4)                   # naval facility
         + g("M2,18L5,28H25L28,18L25,22H5Z", "url(#steel)"))
B[18] = place(PI.TANK, (4.5, 15, 57.5, 35), (0, 7, 30, 23))                                # land facility
B[19] = f'<circle cx="15" cy="15" r="13.5" fill="none" stroke="url(#g)" stroke-width="2"/>' + TREFOIL   # nuclear facility
B[20] = (g("M2,10L15,3L28,10Z") + "".join(g(f"M{5 + 5 * i},12H{8 + 5 * i}V24H{5 + 5 * i}Z") for i in range(5))   # landmark
         + g("M2,25H28V28H2Z"))
B[21] = (g("M15,2A7,7 0 0 1 22,9C22,14 15,22 15,22C15,22 8,14 8,9A7,7 0 0 1 15,2Z")          # marker
         + f'<circle cx="15" cy="9" r="2.6" fill="{INK}"/>' + g("M4,28L9,22H21L26,28Z"))
B[22] = (g("M7,13L12,8H17L18,13Z") + ln("M15,11L28,4M15.5,12.5L28.5,6.5", GOLD, 1.8)       # coastal bunker
         + g("M2,16H28V25H2Z") + "".join(g(f"M{5 + 6 * i},19H{8 + 6 * i}V22H{5 + 6 * i}Z", INK) for i in range(4)))
B[23] = (g("M21,2H26V28H21Z") + "".join(g(f"M{4 + 3.4 * i},{26 - 4.8 * i}H{20}V{28 - 4.8 * i}H{4 + 3.4 * i}Z", "url(#civ)")
                                       for i in range(5)))                               # stronghold stair
B[24] = (g("M2,4H8L10,28H2Z") + g("M28,4H22L20,28H28Z")                               # dam
         + "".join(ln(f"M10.5,{y}Q13,{y - 2} 15,{y}T19.5,{y}", "#6E8FB0", 1.4) for y in (14, 19, 24)))
B[25] = "".join(g(f"M{3 + 6.5 * i},28V{12 - 2 * i}L{8 + 6.5 * i},{6 - 2 * i}V28Z") for i in range(4))   # fortified line
B[26] = (g("M7,28Q10,18 8,6H22Q20,18 23,28Z") + g("M4,4H26V7H4Z") + g("M3,26H27V29H3Z")    # power plant
         + f'<circle cx="15" cy="17" r="5.5" fill="{INK}" stroke="url(#g)" stroke-width="1"/>'
         + place(TREFOIL, (2, 2, 28, 28), (11, 13, 19, 21)))
B[27] = (place(PF.ANCHOR, PF.ANCHOR_BOX, (0, 0, 17, 18)) + place(CRATE, (2, 8, 20, 27), (14, 6, 30, 22))   # naval supply hub
         + place(CRATE, (2, 8, 20, 27), (9, 14, 25, 30)))
B[28] = (place(PF.ANCHOR, PF.ANCHOR_BOX, (0, 1, 15, 17))                                   # naval base city
         + g("M16,28V12H22V28ZM23,28V6H29V28Z") + ln("M19,12V5", GOLD, 1) + g("M19,5H23V7.5H19Z", "url(#civ)")
         + "".join(g(f"M{17 + 6.5 * (i % 2)},{14 + 4 * (i // 2)}H{19 + 6.5 * (i % 2)}V{16 + 4 * (i // 2)}H{17 + 6.5 * (i % 2)}Z", INK)
                   for i in range(6)))
B[29] = (place(pylon(), (5, 1, 25, 29), (0, 4, 20, 30))                                    # protected substation
         + g("M23.5,2L29,4V9Q29,14 23.5,16Q18,14 18,9V4Z", "url(#steel)") + place(BOLT, (13, 4, 25, 28), (21, 4.5, 26, 14)))
B[30] = place(pylon(), (5, 1, 25, 29), (0, 1, 22, 30)) + place(BOLT, (13, 4, 25, 28), (19, 9, 29, 29))   # power grid




# the railway (2026-10-20, the author: "the railroad icon could use another path. Currently the bars go over the side of
# the track, and the track to the right has no tracks. You should try to recreate the base game icon more or less 1 to
# 1"): the game's switch, traced from its 46 px frame and drawn in the frame's own pixels: a straight track (rails at x
# 13 and 21, y 6 to 40) with six sleepers, and a branch leaving it, its inner rail from the left rail at y 27 and its
# outer from the right rail at y 30, both curving up to the right, with sleepers of its own on the top three rows. Each
# rail has a dark edge, so the sleepers break where they pass under it, as the game's do; the whole drawing is made a
# little smaller about the frame's middle (RAIL_FIT) to stay inside the octagon
def rail():
    sleepers = (9, 14.5, 20, 25.5, 31, 36.5)
    inner, outer = "M13,27C13,20 30,15 30,6", "M21,30C21,23 38,19 38,6"
    def curve_x(d, y):                      # the curve's x at height y (sampled)
        import re
        x0, y0, x1, y1, x2, y2, x3, y3 = map(float, re.findall(r"-?\d+\.?\d*", d))
        best = min((abs(((1 - s) ** 3 * y0 + 3 * (1 - s) ** 2 * s * y1 + 3 * (1 - s) * s * s * y2 + s ** 3 * y3) - y), s)
                   for s in [i / 200 for i in range(201)])[1]
        return (1 - best) ** 3 * x0 + 3 * (1 - best) ** 2 * best * x1 + 3 * (1 - best) * best * best * x2 + best ** 3 * x3
    # one gilt gradient over the whole drawing, light at the top (an object's own box would shade each sleeper alike,
    # and gives a straight rail, a box of no width, no paint at all)
    defs = ('<defs><linearGradient id="rail_g" gradientUnits="userSpaceOnUse" x1="0" y1="6" x2="0" y2="40">'
            '<stop offset="0" stop-color="#F6E3A6"/><stop offset="1" stop-color="#9A7634"/></linearGradient></defs>')
    ties = "".join(f'<rect x="10.6" y="{y - 1.05}" width="13.2" height="2.1" fill="url(#rail_g)"/>' for y in sleepers)
    ties += "".join(f'<rect x="{curve_x(inner, y) - 2.4:.2f}" y="{y - 1.05}" width="{curve_x(outer, y) - curve_x(inner, y) + 4.8:.2f}" '
                    f'height="2.1" fill="url(#rail_g)"/>' for y in sleepers[:3])
    rails = ""
    for d in (inner, outer, "M13,40V6", "M21,40V6"):
        rails += (f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="3.6" stroke-linecap="butt"/>'
                  f'<path d="{d}" fill="none" stroke="url(#rail_g)" stroke-width="1.75" stroke-linecap="butt"/>')
    return defs + ties + rails


RAIL_FIT = (10.6, 6, 40.4, 40)              # the drawing's box in the frame, and where it goes:
RAIL_TO = (11.5, 7.5, 37.5, 38.5)
RAIL = place(rail(), RAIL_FIT, RAIL_TO)


# ------------------------------------------------------------------ the buttons: subtle octagons
PLATE = octagon(1.5, 1.5, 44.5, 44.5, 12)


def building(art):
    """a building's octagon and its subject (30 x 30 units into the octagon; ("frame", None): the railway, drawn in the
    frame's own pixels)"""
    body = RAIL if isinstance(art, tuple) else place(art, (0, 0, 30, 30), (7, 7, 39, 39))
    return (f'<path d="{PLATE}" fill="url(#lac)" stroke="rgba(201,165,90,.5)"/>'
            f'<path d="{octagon(4, 4, 42, 42, 10.8)}" fill="none" stroke="rgba(241,220,156,.10)"/>' + body)


def glow(bright):
    a = .95 if bright else .45
    return (f'<path d="{octagon(2, 2, 46, 46, 12.5)}" fill="none" stroke="rgba(241,220,156,{a})" stroke-width="2"/>'
            f'<path d="{octagon(0.8, 0.8, 47.2, 47.2, 13)}" fill="none" stroke="rgba(227,199,126,{a * .45})" stroke-width="1.4"/>')


def medallion(w, h, art):
    """a category's medallion: an octagon of lacquer in a gilt rim, the subject in gilt"""
    s = min(w, h) - 1
    x0, y0 = (w - s) / 2, (h - s) / 2
    return (f'<path d="{octagon(x0, y0, x0 + s, y0 + s, s * .29)}" fill="url(#lac)" stroke="url(#g)" stroke-width="1.3"/>'
            f'<path d="{octagon(x0 + 3, y0 + 3, x0 + s - 3, y0 + s - 3, s * .25)}" fill="none" stroke="rgba(201,165,90,.35)"/>'
            + place(art, (0, 0, 30, 30), (x0 + 6, y0 + 6, x0 + s - 6, y0 + s - 6)))


FLAG = g("M8,3V25", "none", PF.outline("url(#g)", 1.8)) + g("M9,4H25L21,9.5L25,15H9Z", "url(#civ)") + g("M3,24H20L23,28H3Z")
EXCAVATOR = (g("M2,26H20V29H2Z", "url(#silver)") + g("M4,18H17V25H4Z") + g("M12,13H17V18H12Z", "url(#civ)")
             + ln("M16,15L24,6L28,13", GOLD, 2) + g("M24,13H29L27,18H24Z"))
NEEDLE = (f'<circle cx="15" cy="15" r="12" fill="none" stroke="url(#g)" stroke-width="1.4"/>'
          + g("M21,6L16.5,16.5L13.5,13.5Z", "#EE8C7E") + g("M9,24L13.5,13.5L16.5,16.5Z"))


def gear(cx, cy, r, n):
    teeth = "".join(f'<rect x="{cx - 1.4}" y="{cy - r - 2.2}" width="2.8" height="3" fill="url(#g)" '
                    f'transform="rotate({360 / n * i} {cx} {cy})"/>' for i in range(n))
    return (teeth + f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#g)" {O}/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r * .4}" fill="{INK}"/>')


GEARS = (gear(10, 18, 7, 8) + gear(20.5, 24, 4.2, 6)
         + g("M20,2H26M21,2V8L18,15H28L25,8V2", "url(#jade)") + ln("M19,2H27", GOLD, 1.2))

# ------------------------------------------------------------------ the overlays
STOPWATCH = (f'<circle cx="23" cy="25" r="11" fill="url(#bar)" {O}/><circle cx="23" cy="25" r="8.4" fill="#E8DFC8"/>'
             + ln("M23,25V19.5M23,25L27,27", INK, 1.4) + g("M21,10H25V13H21Z") + g("M20.5,8.5H25.5V10H20.5Z"))
SWAP = (g("M8,13H22V10L28,15L22,20V17H8Z", "url(#jade)") + g("M22,24H8V21L2,26L8,31V28H22Z", "url(#civ)"))
BIG_WRENCH = place(WRENCH, (4, 2, 26.5, 24), (12, 8, 42, 40))


def repair(with_wrench):
    rim = (f'<path d="{octagon(1.5, 1.5, 40.5, 40.5, 11)}" fill="none" stroke="#EE8C7E" stroke-width="1.8"/>')
    if not with_wrench:
        return rim
    hatch = (f'<clipPath id="rh"><path d="{octagon(1.5, 1.5, 40.5, 40.5, 11)}"/></clipPath>'
             '<g clip-path="url(#rh)">' + "".join(f'<path d="M{x},0L{x - 42},42" stroke="rgba(238,140,126,.22)" stroke-width="3"/>'
                                                   for x in range(0, 90, 8)) + '</g>')
    return hatch + rim + place(WRENCH, (4, 2, 26.5, 24), (8, 8, 34, 34))


# ------------------------------------------------------------------ the factory count's buttons
def count_button(size, plus, n):
    c = size / 2
    sign = f"M{c - 6},{c}H{c + 6}" + (f"M{c},{c - 6}V{c + 6}" if plus else "")
    num = (f'<text x="{size - 1}" y="{size - 1.5}" text-anchor="end" font-family="Josefin Sans" font-weight="700" '
           f'font-size="{9 if n == 5 else 8}" fill="{LIT}" stroke="{INK}" stroke-width="1.8" paint-order="stroke">{n}</text>'
           if n > 1 else "")
    return (f'<path d="{octagon(1, 1, size - 1, size - 1, size * .29)}" fill="url(#lac)" stroke="url(#g)"/>'
            + PF.PI.outlined(sign, GOLD, 2) + num)


# ------------------------------------------------------------------ the header's and the special rows' icons
CIV_WORKS = place(works(CIV), PF.WORKS_BOX, (1, 1, 26, 22))
CIV_OUTPUT = (place(works(CIV), PF.WORKS_BOX, (0, 3, 19, 22)) + PF.PI.outlined("M14,17L22.5,6", LIT, 1.8)
              + f'<path d="M25.5,2.5L25.2,9.6L19.6,6.4Z" fill="{LIT}" stroke="{INK}" stroke-width=".8" stroke-linejoin="round"/>')
CIV_WRENCH = place(works(CIV), PF.WORKS_BOX, (0, 3, 19, 22)) + place(WRENCH, (4, 2, 26.5, 24), (11, 1, 27, 17))
SPEED = (f'<circle cx="18" cy="11" r="7" fill="url(#bar)" {O}/><circle cx="18" cy="11" r="5" fill="#E8DFC8"/>'
         + ln("M18,11V7.5M18,11L20.5,12.5", INK, 1.2) + g("M16.5,2.5H19.5V4H16.5Z")
         + ln("M2,8H9M1,11.5H8.5M3,15H9.5", RULE, 1.4))
TOASTER = (g("M5,12Q5,7 10,7H33Q38,7 38,12V29H5Z", "url(#silver)") + g("M11,7V5H18V7M24,7V5H31V7", INK)
           + ln("M38,17H42V21", "#C9D1D4", 1.6) + g("M8,29H35V32H8Z", INK) + ln("M10,12H33", LIT, .8))
TRADED = (place(CRATE, (2, 8, 20, 27), (8, 9, 33, 35))
          + PF.PI.outlined("M4,22C2,10 14,4 26,6", "#4FA884", 2) + g("M24,2L32,6L25,10Z", "#4FA884", D)
          + PF.PI.outlined("M37,22C39,34 27,40 15,38", GOLD, 2) + g("M17,34L9,38L16,42Z", "url(#g)", D))
PROJECTS = (g("M3,10H34V36H3Z", "url(#steel)") + "".join(ln(f"M3,{14 + 5 * i}H34", "rgba(241,220,156,.25)", .7) for i in range(5))
            + g("M30,6Q34,6 34,10V32Q34,28 30,28Z", "url(#silver)") + g("M8,32V14L26,32Z", "none", PF.outline(GOLD, 2))
            + ln("M12,27V22L17,27Z", GOLD, 1) + ln("M28,4L40,38", "#C9D1D4", 1.4))
CONTRACT = (place(CRATE, (2, 8, 20, 27), (10, 6, 36, 34))
            + g("M3,30L33,10L35,12.5L6,32Z", "url(#silver)") + g("M3,30L9,26L11,31L6,33Z", "url(#bar)")
            + g("M17,23L20,21L22,25L19,26Z", INK))
BACKHOE = (g("M1,12H13V15H1Z", "url(#silver)") + g("M2,7H11V12H2Z") + g("M6,4H10V7H6Z", CIV)
           + ln("M10,5L17,1.5L22,6.5", GOLD, 1.6) + g("M19.5,6.5H25L23.5,10.5H20.5Z"))
CONVERT = (place(works(CIV), PF.WORKS_BOX, (3, 2, 17, 14)) + place(works("url(#jade)"), PF.WORKS_BOX, (13, 16, 27, 28))
           + g("M17,6H24V3.5L28.5,8L24,12.5V10H17Z", "url(#jade)", D) + g("M13,20H6V17.5L1.5,22L6,26.5V24H13Z", CIV, D))


def frames(fw, parts):
    return "".join(at(fw * i, p) for i, p in enumerate(parts))


ADDS = [
    ("cn_building_icon_strip", GI + "buildings/building_icon_strip.dds", 1426, 46,
     lambda: svg(1426, 46, frames(46, [building(b) for b in B]))),
    ("cn_state_constructions", GI + "state_constructions.dds", 41, 39, lambda: svg(41, 39, medallion(41, 39, FLAG))),
    ("cn_shared_constructions", GI + "shared_constructions.dds", 40, 39, lambda: svg(40, 39, medallion(40, 39, EXCAVATOR))),
    ("cn_province_constructions", GI + "province_constructions.dds", 39, 39, lambda: svg(39, 39, medallion(39, 39, NEEDLE))),
    ("cn_facility_constructions", GI + "special_project/facility_constructions.dds", 39, 39,
     lambda: svg(39, 39, medallion(39, 39, GEARS))),
    ("cn_construction_glow_overlay", GI + "tutorial/construction_glow_overlay.dds", 96, 48,
     lambda: svg(96, 48, frames(48, [glow(True), glow(False)]))),
    ("cn_building_status_overlay", GI + "buildings/building_status_overlay.dds", 138, 46,
     lambda: svg(138, 46, frames(46, [STOPWATCH, place(SWAP, (2, 10, 28, 31), (8, 8, 40, 38)), BIG_WRENCH]))),
    ("cn_building_repair", GI + "building_repair.dds", 84, 42, lambda: svg(84, 42, frames(42, [repair(False), repair(True)]))),
    ("cn_convert_ic_button", GI + "convert_ic_button.dds", 46, 46, lambda: svg(46, 46, building(CONVERT))),
    *[(f"cn_{'add' if p else 'subtract'}_{'one' if n == 1 else n}", GI + f"{'add' if p else 'subtract'}_{'one' if n == 1 else n}.dds",
       26 if p else 25, 26 if p else 25, (lambda p=p, n=n, s=26 if p else 25: svg(s, s, count_button(s, p, n))))
      for p in (True, False) for n in (1, 5, 10)],
    ("cn_non_available_factory_icon", GI + "non_available_factory_icon.dds", 27, 23, lambda: svg(27, 23, CIV_WORKS)),
    ("cn_civ_factory_output_icon", GI + "construction/civ_factory_output_icon.dds", 27, 23, lambda: svg(27, 23, CIV_OUTPUT)),
    ("cn_factory_wrench_icon", GI + "factory_wrench_icon.dds", 27, 23, lambda: svg(27, 23, CIV_WRENCH)),
    ("cn_construction_speed_icon", GI + "construction_speed_icon.dds", 28, 19, lambda: svg(28, 19, SPEED)),
    ("cn_consumer_goods_icon", GI + "consumer_goods_icon.dds", 44, 35, lambda: svg(44, 35, TOASTER)),
    ("cn_traded_factories_icon", GI + "tradeview/traded_factories_icon.dds", 41, 43, lambda: svg(41, 43, TRADED)),
    ("cn_projects_factories_icon", GI + "projects_factories_icon.dds", 46, 42, lambda: svg(46, 42, PROJECTS)),
    ("cn_ongoing_market_contract_icon", GI + "construction/ongoing_market_contract_icon.dds", 44, 36,
     lambda: svg(44, 36, CONTRACT)),
    ("cn_backhoe_icon_small", GI + "backhoe_icon_small.dds", 26, 16, lambda: svg(26, 16, BACKHOE)),
    ("cn_consumer_goods_texticon", "gfx/texticons/consumer_goods_texticon.dds", 20, 20,
     lambda: svg(20, 20, place(TOASTER, (5, 5, 42, 32), (0.5, 3, 19.5, 17)))),
]
