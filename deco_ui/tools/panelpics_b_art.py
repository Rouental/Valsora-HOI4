"""The side panels' own pictures drawn by hand (2026-10-21; the author: "with a lot of the things you've generated
recently, there's these weird sloppy lines and missing pieces of the design"): they replace the automatic translations
of make_panel_pictures.py (proposals_panel_mockups.translate, which traced the game's thin lines into broken gilt
fragments), each at the game's path, size and frame count, its boxes where the game's .gui puts its texts and icons.

Group B, the faction screens (interface/factions/countryfactionview.gui, new_faction_window.gui; sprites in
factions.gfx, all plain spriteTypes, so nothing is tiled or stretched). One family with faction_art.py's goal slot:
a chamfered lacquer plate (#17222A to #0E1519, the 8 px pinstripe) inside a 1 px gilt rim (#E8CD84 to #8B6A2C) and a
gilt hairline 3 px inside it, every line on whole pixels; lit is jade under a bright rim, unavailable dim grey lacquer
with a faint hatch. Positions below are the picture's own pixels (the .gui's, less where the picture sits):

- faction_identity_background_generic (522 x 108): the faction's name plate, under the logo (its middle at (53, 53),
  layout_panels "faction"), the name (101, 5; 326 wide), the manifest (105, 45), its progress bar (99, 65; 256 x 30), the
  initiative box (435, 15) and the power projection (to x 505, y 77); the setup window writes on it too, from (5, 2) to
  the right edge, so the plate is plain inside its rims (no well a text would cross). The plate ends at row 104, the
  last 4 rows clear: the setup window draws its next band (faction_identity, y 150) over rows 104-107, which hid the
  bottom rim, and the faction screen's "Faction Influence" label starts on row 107;
- faction_supreme_commander_background (525 x 126, the theatre list's button, stacked every 125 px): a plate over
  [1, 521) x [1, 124) (2 px between cards); the portrait frame at (43, 11), the flag (121, 18), the skill (118-153,
  47-97), the title (169, 20), the name (163, 48), the stats (163-343, 63-115), the pin checkbox (480, 15); a gilt rule
  between the title and the name (y 44, x 166 to 466, a diamond at each end) is the card's only line inside its rims;
- faction_influence_chart_background (525 x 106): a plate over [2, 523) x [2, 104); the game draws the pie's frame at
  (10, 10) (101 x 89, its ink to x 110), the five members' flags, crowns and shares at x 113-383, y 13-96 (the leader's
  frame from x 114), the two buttons at (387, 22) and (387, 57) (123 x 34). Plain inside its rims: a well for the members
  would have had no room (1-2 px to the pie's frame, the leader's frame and the buttons);
- faction_intelligence_background (510 x 100, under each intelligence slot's 42 px header, the next slot's header right
  under it): a plate over [0, 510) x [2, 98), 2 px clear of both headers (touching, their chamfers met in a notch), and
  an ivory sheet over [8, 345) x [8, 92) where the game had its paper, its bronze rim as the designers' ruled sheet: the game writes
  on it in its dark typewriter ink (the advisor's title at (110, 18), name (72, 43), skill (72, 58)), with the flag's
  frame at (58, 10) and the unlock button at (100, 38); the take-over button (350-498, 48-82) stands on the lacquer
  right of the sheet;
- faction_spymaster_background (510 x 83, one frame, the spymaster's slot: at the slot's (0, 42), the slots 142 apart, so
  1 px above the next slot's header; it replaces the automatic photo_plate, which had drawn a sunburst where the game
  has its photograph of two agents): the plate over the whole picture with its rim alone. The game's elements run to
  its edges (the spymaster's eye badge at (450, -2), its ink from row 2; the title at (70, 3); the take-over button at
  (350, 48), to row 81), so a hairline 3 px in would cross the badge and the button; the flag's frame at (396, 5), the
  name at (70, 28), the skill at (70, 48) and the add button (68-282, 28-56) sit inside;
- faction_doctrine_sharing_bg (530 x 108, under the doctrine header, whose last 5 rows it covers): a plate over
  [4, 526); the game sets three or four doctrine folders on it every 126 px (icons x 34-113 + 126 i, y 13-65; the
  unlock buttons below, y 66-100), so it has no niches that a missing folder would leave empty;
- select_faction_goal_button (7 frames of 240 x 92, the goal picker's cards, two to a row 240 apart, rows 78 apart):
  the plate where the game's is ([4, 236) x [9, 83)); the name at (17, 40), the cost at (187, 60); frames in the game's
  order: open, lit (the chosen goal: jade), done (a gilt check), done and lit, failed (a coral cross), failed and lit,
  locked (dim, hatched); the marks where the game draws its own (centred at (215, 46)), as faction_art.py's;
- faction_identity_background_pop_up_generic (3 frames of 204 x 364, the faction templates, 197 px apart): a card over
  [3, 197) x [2, 362) (3 px between cards, centred on the template's texts at x 100), a dark well for the manifest
  ([15, 185) x [66, 258): its name at (19, 76), its description from (19, 134)), the template's name above it (y 20)
  and the rule and goal boxes below it (24-174, y 275-341, their own pictures); frames: open, selected (jade), unavailable
  (dim, hatched).

gen_textures.py draws ADDS (prefix pb_).
"""
from art_util import frames

P = "gfx/interface/factions/ui/"

GILT = ("#E8CD84", "#8B6A2C")          # a plate's rim
BRIGHT = ("#F4E2A6", "#B8954F")        # a lit plate's rim
LACQUER = ("#17222A", "#0E1519")
JADE = ("#2C665A", "#163A33")          # art_util.LIT_FILL
JADE_DEEP = ("#22544A", "#10282A")     # a tall card's jade (the template card)
DIM = ("#161C20", "#0C1013")
HAIR = "rgba(201,165,90,.30)"
HAIR_LIT = "rgba(241,220,156,.45)"
HAIR_DIM = "rgba(201,165,90,.16)"
RIM_DIM = ("rgba(201,165,90,.45)", "rgba(139,106,44,.45)")
CORAL = "rgb(238,140,126)"

STATES = {
    "open": dict(fill=LACQUER, rim=GILT, hair=HAIR),
    "lit": dict(fill=JADE, rim=BRIGHT, hair=HAIR_LIT),
    "lit_deep": dict(fill=JADE_DEEP, rim=BRIGHT, hair=HAIR_LIT),
    "locked": dict(fill=DIM, rim=RIM_DIM, hair=HAIR_DIM, hatch=True),
}


def cham(x0, y0, x1, y1, c):
    """a chamfered rectangle's outline through those edges"""
    return (f"M{x0 + c:g},{y0:g}H{x1 - c:g}L{x1:g},{y0 + c:g}V{y1 - c:g}L{x1 - c:g},{y1:g}H{x0 + c:g}"
            f"L{x0:g},{y1 - c:g}V{y0 + c:g}Z")


def inset(box, d, c):
    """the outline d px inside a plate's edges, its diagonals parallel to the plate's (a 45 degree chamfer c loses
    d * (2 - sqrt 2) when its sides move in by d)"""
    x0, y0, x1, y1 = box
    return cham(x0 + d, y0 + d, x1 - d, y1 - d, max(0.5, c - 0.586 * d))


def grad(gid, stops, vertical=True):
    a, b = stops
    xy = 'x1="0" y1="0" x2="0" y2="1"' if vertical else 'x1="0" y1="0" x2="1" y2="0"'
    return f'<linearGradient id="{gid}" {xy}><stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>'


def svg(w, h, defs, body):
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="position:absolute;left:0;top:0">'
            f'<defs>{defs}</defs>{body}</svg>')


def plate(p, box, c, state="open", inner=3):
    """(defs, body) of a plate over the pixel edges box = (x0, y0, x1, y1): its fill and pinstripes (and hatch when
    locked), the 1 px rim on the outermost pixels, the hairline `inner` px inside it. p: a prefix for the ids (one
    page holds every texture, so each picture's gradients are its own)"""
    s = STATES[state]
    x0, y0, x1, y1 = box
    defs = (grad(p + "f", s["fill"]) + grad(p + "r", s["rim"])
            + f'<pattern id="{p}s" x="{x0}" y="0" width="8" height="8" patternUnits="userSpaceOnUse">'
              '<rect x="0" y="0" width="1" height="8" fill="rgba(255,255,255,.022)"/></pattern>')
    body = (f'<path d="{cham(*box, c)}" fill="url(#{p}f)"/>'
            f'<path d="{cham(*box, c)}" fill="url(#{p}s)"/>')
    if s.get("hatch"):
        defs += (f'<pattern id="{p}h" width="12" height="12" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
                 '<rect x="0" y="0" width="4" height="12" fill="rgba(201,165,90,.07)"/></pattern>')
        body += f'<path d="{cham(*box, c)}" fill="url(#{p}h)"/>'
    body += f'<path d="{inset(box, .5, c)}" fill="none" stroke="url(#{p}r)" stroke-width="1"/>'
    if inner:
        body += f'<path d="{inset(box, inner + .5, c)}" fill="none" stroke="{s["hair"]}" stroke-width="1"/>'
    return defs, body


def well(box, c=4, fill="#0A0F12", rim="rgba(201,165,90,.45)"):
    """a recessed dark well with a 1 px rim on its outermost pixels"""
    return (f'<path d="{cham(*box, c)}" fill="{fill}"/>'
            f'<path d="{inset(box, .5, c)}" fill="none" stroke="{rim}" stroke-width="1"/>')


def diamond(cx, cy, r, fill="#E3C77E"):
    return f'<path d="M{cx:g},{cy - r:g}L{cx + r:g},{cy:g}L{cx:g},{cy + r:g}L{cx - r:g},{cy:g}Z" fill="{fill}"/>'


def check(cx, cy):
    """the done goal's check (faction_art.py's, a little smaller: the picker's card is shorter than the slot)"""
    pts = f"{cx - 8:g},{cy + .5:g} {cx - 2.5:g},{cy + 6:g} {cx + 8:g},{cy - 7:g}"
    return (f'<polyline points="{pts}" fill="none" stroke="#0B1014" stroke-width="5" stroke-linecap="round" '
            'stroke-linejoin="round"/>'
            f'<polyline points="{pts}" fill="none" stroke="#E3C77E" stroke-width="2.4" stroke-linecap="round" '
            'stroke-linejoin="round"/>')


def cross(cx, cy):
    d = f"M{cx - 7:g} {cy - 7:g}L{cx + 7:g} {cy + 7:g}M{cx + 7:g} {cy - 7:g}L{cx - 7:g} {cy + 7:g}"
    return (f'<path d="{d}" stroke="#0B1014" stroke-width="5" stroke-linecap="round"/>'
            f'<path d="{d}" stroke="{CORAL}" stroke-width="2.4" stroke-linecap="round"/>')


# ---------------------------------------------------------------- the name plate (faction screen, setup window)
IDENTITY = dict(w=522, h=108, box=(0, 0, 522, 104), c=7)


def identity():
    g = IDENTITY
    defs, body = plate("pbid", g["box"], g["c"])
    return svg(g["w"], g["h"], defs, body)


# ---------------------------------------------------------------- the supreme commander's card (the theatre list)
COMMANDER = dict(w=525, h=126, box=(1, 1, 521, 124), c=8, rule=(166, 466, 44))


def commander():
    g = COMMANDER
    defs, body = plate("pbsc", g["box"], g["c"])
    x0, x1, y = g["rule"]
    body += (f'<path d="M{x0 + 4},{y + .5}H{x1 - 4}" stroke="rgba(201,165,90,.55)" stroke-width="1"/>'
             + diamond(x0 + 2.5, y + .5, 2.5) + diamond(x1 - 2.5, y + .5, 2.5))
    return svg(g["w"], g["h"], defs, body)


# ---------------------------------------------------------------- the faction's influence (the pie and the members)
INFLUENCE = dict(w=525, h=106, box=(2, 2, 523, 104), c=7)


def influence():
    g = INFLUENCE
    defs, body = plate("pbin", g["box"], g["c"])
    return svg(g["w"], g["h"], defs, body)


# ---------------------------------------------------------------- an intelligence slot (its advisor on an ivory sheet)
INTEL = dict(w=510, h=100, box=(0, 2, 510, 98), c=6, sheet=(8, 8, 345, 92))


def intelligence():
    g = INTEL
    defs, body = plate("pbit", g["box"], g["c"])
    x0, y0, x1, y1 = g["sheet"]
    defs += (grad("pbitp", ("#EFE6CE", "#E0D3B0"))
             + '<radialGradient id="pbitl" cx=".3" cy=".25" r=".7"><stop offset="0" stop-color="rgba(255,250,235,.5)"/>'
               '<stop offset="1" stop-color="rgba(255,250,235,0)"/></radialGradient>')
    body += (f'<path d="{cham(x0, y0, x1, y1, 4)}" fill="url(#pbitp)"/>'
             f'<path d="{cham(x0, y0, x1, y1, 4)}" fill="url(#pbitl)"/>'
             f'<path d="{inset((x0, y0, x1, y1), .5, 4)}" fill="none" stroke="#9C7A36" stroke-width="1"/>')
    return svg(g["w"], g["h"], defs, body)


# ---------------------------------------------------------------- the spymaster's slot (its rim alone: see above)
SPYMASTER = dict(w=510, h=83, box=(0, 0, 510, 83), c=6)


def spymaster():
    g = SPYMASTER
    defs, body = plate("pbsm", g["box"], g["c"], inner=0)
    return svg(g["w"], g["h"], defs, body)


# ---------------------------------------------------------------- doctrine sharing (the folders' plate)
DOCTRINE = dict(w=530, h=108, box=(4, 0, 526, 108), c=6)


def doctrine():
    g = DOCTRINE
    defs, body = plate("pbdc", g["box"], g["c"])
    return svg(g["w"], g["h"], defs, body)


# ---------------------------------------------------------------- the goal picker's cards (7 frames)
GOAL = dict(w=240, h=92, box=(4, 9, 236, 83), c=6, mark=(215, 46))
GOAL_FRAMES = [("open", None), ("lit", None), ("open", "done"), ("lit", "done"), ("open", "failed"),
               ("lit", "failed"), ("locked", None)]


def goal_card(i, state, mark):
    g = GOAL
    defs, body = plate(f"pbg{i}", g["box"], g["c"], state)
    if mark == "done":
        body += check(*g["mark"])
    elif mark == "failed":
        body += cross(*g["mark"])
    return svg(g["w"], g["h"], defs, body)


# ---------------------------------------------------------------- the faction templates (3 frames)
TEMPLATE = dict(w=204, h=364, box=(3, 2, 197, 362), c=10, well=(15, 66, 185, 258))


def template_card(i, state):
    g = TEMPLATE
    defs, body = plate(f"pbt{i}", g["box"], g["c"], state, inner=4)
    fill = "rgba(8,12,15,.72)" if state != "locked" else "rgba(8,11,13,.55)"
    rim = {"open": "rgba(201,165,90,.45)", "lit_deep": "rgba(241,220,156,.6)", "locked": "rgba(201,165,90,.2)"}[state]
    body += well(g["well"], 6, fill, rim)
    return svg(g["w"], g["h"], defs, body)


ADDS = [
    ("pb_identity", P + "faction_identity_background_generic.dds", 522, 108, identity),
    ("pb_commander", P + "faction_supreme_commander_background.dds", 525, 126, commander),
    ("pb_influence", P + "faction_influence_chart_background.dds", 525, 106, influence),
    ("pb_intelligence", P + "faction_intelligence_background.dds", 510, 100, intelligence),
    ("pb_spymaster", P + "faction_spymaster_background.dds", 510, 83, spymaster),
    ("pb_doctrine", P + "faction_doctrine_sharing_bg.dds", 530, 108, doctrine),
    ("pb_goal_button", P + "select_faction_goal_button.dds", 1680, 92,
     lambda: frames(1680, 92, *(goal_card(i, s, m) for i, (s, m) in enumerate(GOAL_FRAMES)))),
    ("pb_template", P + "faction_identity_background_pop_up_generic.dds", 612, 364,
     lambda: frames(612, 364, *(template_card(i, s) for i, s in enumerate(("open", "lit_deep", "locked"))))),
]
