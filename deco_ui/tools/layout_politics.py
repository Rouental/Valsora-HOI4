"""Layout of the politics screen (interface/countrypoliticsview.gui), v0.4: the Government mockup's layout.

Panel-local pixels. The vanilla panel is 550 wide and slides in to x = -6 (so x < 6 is off-screen),
top at y = 78 on screen, full height (about 1000 px at 1080p). Top to bottom, as in the mockup:

  header         "Government" label, the country's full name (scripted GUI), close diamond, rules icon
  head of state  arched portrait over a sunburst, "Head of State" ribbon; right: name, ideology chip,
                 a 2x2 grid (ruling party, elections, last election, political power)
  description    the leader's title/description in italics between two rules (scripted GUI; an
                 ornament instead when the leader has none)
  popularity     pie in a gilt ring with the party legend | laws: conscription, economy, trade cards
  spirits        national spirits in one band
  faction | focus  faction card and national focus card side by side (the mockup has no focus; the
                 game needs it, it opens the focus tree)
  buttons        occupied territories / exiles / subjects, compact
  ideas          the game's advisors & laws list (scrolls)

The panel keeps vanilla's 550 px width (the mockup's is 604) so the sub-windows that open beside it
(advisor picker, subjects, exiles, occupied territories) keep their positions.
"""
PANEL_W = 550
X0, X1 = 18, 532                                   # content edges

# ---------------------------------------------------------------- header (clear of the top bar's flag
# medallion, which hangs over the panel's top-left corner: panel-local x 20..176, y 0..70, and the
# decisions seal to y 92)
HEAD_LABEL = dict(x=190, y=20, w=260, h=12)        # "Government" (vanilla political_title, re-texted)
HEAD_TITLE = dict(x=190, y=34, w=292, h=46)        # scripted GUI: [ROOT.GetNameDefCap], 1-2 lines
CLOSE = dict(x=-52, y=26, w=34, h=34)              # UPPER_RIGHT
RULES = (506, 64)
HEAD_RULE_Y = 90
HEAD_GLOW_H = 90                                   # jade wash at the top of the panel (mockup header)

# ---------------------------------------------------------------- head of state
PORTRAIT = dict(x=24, y=100, w=156, h=210)
FRAME = dict(x=PORTRAIT["x"] - 8, y=PORTRAIT["y"] - 8, w=PORTRAIT["w"] + 16, h=PORTRAIT["h"] + 16)
SUNBURST = dict(cx=PORTRAIT["x"] + 78, cy=PORTRAIT["y"] + 92, r=118)
RIBBON = dict(x=PORTRAIT["x"] + 14, y=PORTRAIT["y"] + PORTRAIT["h"] - 10, w=128, h=22)
RX = 198                                           # right column
LEADER_NAME = dict(x=RX, y=100, w=X1 - RX, h=30)   # Federo 24, one line (the longest Valsora name fits)
CHIP = dict(x=RX, y=138, w=250, h=24)              # ideology chip: the game's ideology icon + text
CHIP_ICON = dict(x=RX + 5, y=140, scale=0.34)
CHIP_TEXT = dict(x=RX + 30, y=143, w=214, h=14)
BOP = dict(x=392, y=548)                           # balance of power (only some countries; Valsora has none):
                                                  # right end of the spirits label row
GRID_X = (RX, 368)
GRID_W = (160, X1 - 368)
GRID_LABEL_Y = (178, 234)
GRID_VALUE_Y = (192, 248)
GRID_VALUE_H = 34                                  # two lines
# cells: 0 ruling party (scripted) | 1 elections (the game's text) | 2 last election (scripted) | 3 political power (scripted)

# ---------------------------------------------------------------- leader description
DESC = dict(x=X0, y=328, w=X1 - X0, h=92)          # the two rules sit at DESC y and y+h
DESC_TEXT = dict(x=X0 + 12, y=334, w=X1 - X0 - 24, h=80)   # 5 lines of 16 px

# ---------------------------------------------------------------- popularity | laws
SEC1_Y = 430                                       # section labels
POP_X, POP_W = X0, 242
PIE = dict(cx=X0 + 40, top=452, r=40)              # the game's pie: drawn centred on x, top at y
PIE_RING = 4                                       # ring drawn this much outside the pie
LEGEND = dict(x=X0 + 92, y=452, w=150, row=18)
LAWS_X = 274
LAWS_W = X1 - LAWS_X
LAW_CARDS = [("conscription", "manpower"), ("economy", "factory"), ("trade", "trade")]   # key, icon
LAW_Y0, LAW_H, LAW_GAP = 450, 30, 6

# ---------------------------------------------------------------- national spirits
SPIRITS_LABEL_Y = 566
SPIRITS = dict(x=X0, y=582, w=X1 - X0, h=72)

# ---------------------------------------------------------------- faction | national focus
SEC3_Y = 666
FACTION_CARD = dict(x=X0, y=682, w=240, h=78)
FOCUS_CARD = dict(x=266, y=682, w=X1 - 266, h=78)
FOCUS_ICON = dict(cx=38, cy=39, scale=0.62)        # the focus picture, centred on the card's medallion
FOCUS_TITLE = dict(x=76, y=8, w=158, h=36)
FOCUS_BAR = dict(x=76, y=52, w=176, h=4)
FOCUS_COST = dict(x=76, y=60)

# ---------------------------------------------------------------- management buttons
BUTTONS_Y = 772
BUTTON = dict(w=164, h=26)
BUTTON_X = [X0, X0 + 175, X0 + 350]
STRIP = dict(x=6, y=BUTTONS_Y - 6, w=PANEL_W - 12, h=38)

# ---------------------------------------------------------------- advisors and laws (the game's list)
IDEAS_Y = 806
CAT_HEADER = dict(x=-5, y=4, w=X1 - X0 + 6, h=30)
IDEA_SLOT = 53

# section labels drawn by the mod (rules after them are part of the section art)
SECTION_LABELS = {  # key: (x, y, English text)
    "popularity": (POP_X, SEC1_Y, "Popularity"),
    "laws": (LAWS_X, SEC1_Y, "Laws"),
    "spirits": (X0, SPIRITS_LABEL_Y, "National Spirits"),   # the game's own label, restyled
    "faction": (FACTION_CARD["x"], SEC3_Y, "Faction"),
    "focus": (FOCUS_CARD["x"], SEC3_Y, "National Focus"),
}
SECTION_ENDS = {"popularity": POP_X + POP_W, "laws": X1, "spirits": X1,
                "faction": FACTION_CARD["x"] + FACTION_CARD["w"], "focus": X1}
