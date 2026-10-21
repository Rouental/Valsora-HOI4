"""The side panels' own pictures drawn by hand (2026-10-21; the author: "with a lot of the things you've generated
recently, there's these weird sloppy lines and missing pieces of the design"): they replace the automatic translations
of make_panel_pictures.py (proposals_panel_mockups.translate, which traced the game's thin lines into broken gilt
fragments), each at the game's path, size and frame count, its boxes where the game's .gui puts its texts and icons.

Group A, the officer corps screen (interface/countryofficercorpview.gui, its sprites in countryofficercorpview.gfx, all
plain spriteTypes: nothing is tiled or stretched). One family with faction_art.py's goal slot: a chamfered lacquer plate
(#17222A to #0E1519, the 8 px pinstripe) inside a 1 px rim in the gilt gradient (#E8CD84 to #8B6A2C) and a gilt hairline
3 px inside it, the wells dark (#070B0E to #0E1519) in a gilt hairline, every straight line on whole pixels, every shape
closed. Positions below are the picture's own pixels, edges as [x0, x1) (the .gui's, less where the picture sits):

- officer_corp_bg_banner_army / _navy / _air (516 x 242, a section's title band, alwaystransparent, at the section's
  (0, -12); the special forces' section uses the army's): only the game's band is drawn (the rest is clear): a chamfered
  bar over [0, 512) x [15, 43) (the section is about 513 wide, so the end stays whole if the game clips it) with a soft
  shadow under it, the arm's colour a dark lacquer tone under the gilt rims (army olive, navy steel blue, air oxblood).
  The chief's emblem (119 x 66 at (-4, 5), its ink x 8-99) covers the left end; the title (110, 18; 240 x 20) is on the
  band's middle (y 28);
- advisor_theorist_entry (527 x 71, at the panel's (11, 45), 72 px lower in the mod): the game's two plates,
  [2, 318) and [321, 525) x [1, 68), their outer edges flush with the HQ ribbon's under them (the panel's x 13 to 535)
  and 3 px clear of its rim: the high command and the theorist on the left one (their portraits are the game's grids',
  at runtime), the preferred tactic's button (394-495, 5-65) on the right; no wells, since where the portraits land is
  the grids' business, not this picture's;
- officer_corp_army_hq_bg (539 x 59, the HQ ribbon: its window is 523 x 85 and clips it, and the officer corps list
  covers it from its y 57): one plate over [0, 523) x [0, 57), so it is whole whether clipped or not and ends above the
  list's frame; the Army HQ Templates button (ink 14-208, 5-51), the HQ badge and count (210-360, 19-46) and the
  captured commanders' button (ink 296-508, 3-59) stand on it, 14 px from each end;
- army_hq_template_bg (341 x 95, the Army HQ template card; its window draws it at (-3, 0), so a .gui x is the
  picture's x - 3; the background's size = { 341 72 } taken as unused, since the game's picture fits its elements at
  its own 95 px): a plate over [0, 338) x [1, 94) (2 px between stacked cards, 6 px margins round the wells), no hairline
  (the wells stand 6 px in); the template icon's well [6, 96) x [12, 81) centred on the icon (76 x 42 at (13, 25), its
  ink centred at (51, 46)), the "allowed as HQ" badge (ink 8-27, 15-37) in its upper left and the priority chevrons
  (74-87) at its right; the name's well [99, 332) x [12, 53) round the name (113-311, 22-42; centred on it in height, its
  right edge the delete button's); the deploy time, command power, edit and delete buttons (103-332, 54-84) stand on the
  plate under the name;
- spirit_entry_bg_strip (4 frames of 241.25 x 83, an officer corps spirit in the pick window's 231 x 74 slots): the
  card where the game's is in each frame, 229 x 72 at (4 + 241.25 i, 5) (on whole pixels: 4, 245, 486, 728), an
  octagonal well for the spirit's 45 px icon (centred at the entry's (42, 38)), its trait badge (28 px at (53, 51)) on
  the well's lower right, the name (76, 10), traits (76, 28) and cost (80-222, 47) on the plate. Frames as the game's
  (spirit_entry_bg and spirit_entry_bad_bg side by side): 1 a good spirit, 2 a good one lit (the game's frame with bright
  rules), 3 a bad spirit (the game's darker, blotched card: here a warm oxblood lacquer), 4 a bad one lit; lit is a
  bright gilt rim (#F1DC9C) with a jade hairline, the same geometry.

gen_textures.py draws ADDS (prefix pa_).
"""
GI = "gfx/interface/officer_corp/"

RIM = "url(#pa-gilt)"                 # the gilt rim: the gilt gradient, #E8CD84 at the top to #8B6A2C
BRIGHT = "#F1DC9C"                    # highlight: a lit rim
HAIR = "rgba(201,165,90,.32)"         # the hairline inside a rim
WELL_RIM = "rgba(201,165,90,.6)"
JADE = "#3E8C7A"                      # a lit card's hairline (the palette's #2E6E60, lifted to read as a line)

# lacquer tones (top, bottom): the plates, the arms' bands, a bad spirit
LAC = ("#17222A", "#0E1519")
TONES = {"army": ("#223424", "#111B13"), "navy": ("#192A3A", "#0D1621"), "air": ("#391B1C", "#1D0D0E"),
         "bad": ("#231A1A", "#130E0F")}


def defs():
    out = ('<pattern id="pa-pin" width="8" height="8" patternUnits="userSpaceOnUse">'
           '<rect x="0" y="0" width="1" height="8" fill="rgba(255,255,255,.025)"/></pattern>'
           '<linearGradient id="pa-well" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#070B0E"/>'
           '<stop offset="1" stop-color="#0E1519"/></linearGradient>'
           '<linearGradient id="pa-gilt" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E8CD84"/>'
           '<stop offset="1" stop-color="#8B6A2C"/></linearGradient>')
    for k, (a, b) in dict(TONES, lac=LAC).items():
        out += (f'<linearGradient id="pa-{k}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{a}"/>'
                f'<stop offset="1" stop-color="{b}"/></linearGradient>')
    return f"<defs>{out}</defs>"


def svg(w, h, body, style=""):
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="position:absolute;left:0;top:0;{style}">'
            f'{defs()}{body}</svg>')


def cham(x0, y0, x1, y1, c):
    """a chamfered rectangle's outline through the given coordinates"""
    return (f"M{x0 + c},{y0}H{x1 - c}L{x1},{y0 + c}V{y1 - c}L{x1 - c},{y1}H{x0 + c}L{x0},{y1 - c}V{y0 + c}Z")


def plate(x0, y0, x1, y1, c=6, fill="lac", rim=RIM, hair=HAIR, inset=3):
    """a lacquer plate covering the pixels [x0, x1) x [y0, y1): its 1 px rim on the outermost pixels, the pinstripe, a
    hairline `inset` px inside (both closed, chamfered alike; hair=None: none, where wells sit close to the rim)"""
    p = cham(x0 + .5, y0 + .5, x1 - .5, y1 - .5, c)
    out = f'<path d="{p}" fill="url(#pa-{fill})"/><path d="{p}" fill="url(#pa-pin)"/>'
    if hair:
        q = cham(x0 + inset + .5, y0 + inset + .5, x1 - inset - .5, y1 - inset - .5, max(1, c - inset * .6))
        out += f'<path d="{q}" fill="none" stroke="{hair}"/>'
    return out + f'<path d="{p}" fill="none" stroke="{rim}"/>'


def well(x0, y0, x1, y1, c=4, rim=WELL_RIM):
    """a recessed dark well over [x0, x1) x [y0, y1), its gilt hairline on its outermost pixels"""
    return f'<path d="{cham(x0 + .5, y0 + .5, x1 - .5, y1 - .5, c)}" fill="url(#pa-well)" stroke="{rim}"/>'


def octagon(cx, cy, r, rim=WELL_RIM):
    """a regular octagonal well round (cx, cy), r its half width (flat sides on whole pixels)"""
    c = round(r * 0.4142 * 2) / 2 + .5            # the chamfer of a regular octagon, a little blunter
    return well(cx - r, cy - r, cx + r, cy + r, c, rim)


# ---------------------------------------------------------------- the section banners (army, navy, air)
BANNER = dict(w=516, h=242, x1=512, y0=15, y1=43, c=6)


def banner(arm):
    B = BANNER
    body = plate(0, B["y0"], B["x1"], B["y1"], B["c"], arm, inset=3)
    return svg(B["w"], B["h"], body, "filter:drop-shadow(0 2px 2px rgba(0,0,0,.55))")


# ---------------------------------------------------------------- the advisors' and theorist's strip
STRIP = dict(w=527, h=71, plates=((2, 318), (321, 525)), y0=1, y1=68, c=7)


def strip():
    S = STRIP
    return svg(S["w"], S["h"], "".join(plate(x0, S["y0"], x1, S["y1"], S["c"]) for x0, x1 in S["plates"]))


# ---------------------------------------------------------------- the HQ ribbon
RIBBON = dict(w=539, h=59, x1=523, y1=57, c=7)


def ribbon():
    R = RIBBON
    return svg(R["w"], R["h"], plate(0, 0, R["x1"], R["y1"], R["c"]))


# ---------------------------------------------------------------- the Army HQ template card
HQ = dict(w=341, h=95, plate=(0, 1, 338, 94), icon=(6, 12, 96, 81), name=(99, 12, 332, 53), c=7)


def hq_card():
    H = HQ
    body = plate(*H["plate"], H["c"], hair=None)
    body += well(*H["icon"], 5) + well(*H["name"], 5)
    return svg(H["w"], H["h"], body)


# ---------------------------------------------------------------- the spirits' cards (4 frames)
SPIRIT = dict(w=965, h=83, xs=(4, 245, 486, 728), cw=229, y0=5, y1=77, icon=(38, 33, 26), c=6)


def spirit_card(x, bad=False, lit=False):
    S = SPIRIT
    rim, hair = (BRIGHT, JADE) if lit else (RIM, HAIR)
    cx, cy, r = S["icon"]
    body = plate(x, S["y0"], x + S["cw"], S["y1"], S["c"], "bad" if bad else "lac", rim, hair)
    body += octagon(x + cx, S["y0"] + cy, r, rim=BRIGHT if lit else WELL_RIM)
    return body


def spirit_strip():
    S = SPIRIT
    cards = [spirit_card(x, bad=i >= 2, lit=i % 2 == 1) for i, x in enumerate(S["xs"])]
    return svg(S["w"], S["h"], "".join(cards))


ADDS = [
    ("pa_banner_army", GI + "officer_corp_bg_banner_army.dds", 516, 242, lambda: banner("army")),
    ("pa_banner_navy", GI + "officer_corp_bg_banner_navy.dds", 516, 242, lambda: banner("navy")),
    ("pa_banner_air", GI + "officer_corp_bg_banner_air.dds", 516, 242, lambda: banner("air")),
    ("pa_spirit_entry_bg_strip", GI + "spirit_entry_bg_strip.dds", 965, 83, spirit_strip),
    ("pa_advisor_theorist_entry", GI + "advisor_theorist_entry.dds", 527, 71, strip),
    ("pa_officer_corp_army_hq_bg", GI + "officer_corp_army_hq_bg.dds", 539, 59, ribbon),
    ("pa_army_hq_template_bg", GI + "army_hq_template_bg.dds", 341, 95, hq_card),
]
