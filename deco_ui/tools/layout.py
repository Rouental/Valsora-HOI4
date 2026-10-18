"""Single source of truth for the v2 top bar layout (the mockup's arrangement).

All coordinates are SCREEN pixels at 1920x1080, taken from the mockup (canvas Main board).
The .gui works in topbar-container coordinates: the vanilla "topbar" container sits at
x=-4 y=-1, so  gui = screen + (4, 1)  for UPPER_LEFT elements. A "100%%" width runs to the
parent's right edge (vanilla's army/navy/air offsets inside the 100%%-wide country_menu_window
only land on screen under that reading), so right-anchored elements use  gui_x = screen_x - 1920.

Widths that depend on text are measured from the generated bitmap fonts, so gen_fonts.py
must run before this module is imported.
"""
import os
import re

from paths import MOD

FONTS = MOD + "gfx/fonts/"
RIGHT = 1920


def fnt(name, cache={}):
    if name not in cache:
        t = open(FONTS + name + ".fnt", encoding="utf-8").read()
        chars = {int(d["id"]): d for d in (dict((k, int(v)) for k, v in re.findall(r"(\w+)=(-?\d+)", ln))
                                            for ln in t.split("\n") if ln.startswith("char "))}
        kern = {(int(a), int(b)): int(k) for a, b, k in
                re.findall(r"kerning first=(\d+)\s+second=(\d+)\s+amount=(-?\d+)", t)}
        common = dict((k, int(v)) for k, v in re.findall(r"(\w+)=(-?\d+)", t.split("\n")[1]))
        cache[name] = (chars, kern, common)
    return cache[name]


def measure(font, text):
    chars, kern, _ = fnt(font)
    cps = [ord(c) for c in text if ord(c) in chars]
    return sum(chars[c]["xadvance"] for c in cps) + sum(kern.get(p, 0) for p in zip(cps, cps[1:]))


def cap_top(font):
    """y of the top of a capital H relative to the text box top (as the preview draws it)."""
    chars, _, _ = fnt(font)
    return chars[ord("H")]["yoffset"] + 1  # +1: glyph padding row


def box_y_for_caps(font, caps_y):
    return caps_y - cap_top(font)


GUI = lambda x, y: (x + 4, y + 1)
GUI_R = lambda x, y: (x - RIGHT, y + 1)

# ------------------------------------------------------------------ band
BAND_H = 58                      # lacquer; gilt rule at 58, dark 59-61, faint rule 62, 1px shade at 63
BAND_TEX_H = 64
SHADOW_H = 8                     # click-through soft shadow below the band

# ------------------------------------------------------------------ flag medallion (left)
# v0.3: the flag is shown at the game's native 82x52 (stretching it pixelates: flags are not smoothed)
MED = dict(x=14, y=0, w=156, h=148)               # vanilla "background" icon
MED_STEPS = (122, 139)                            # y where the plate steps in to 12%/88%, then 26%/74%
# (135 until v0.10.1: the shoulders between the steps are now as tall as the decision count badges they hold)
FLAG = dict(x=51, y=18, w=82, h=52)               # player_flag (own 82x52 masked shield, 1:1)
NAME = dict(x=16, y=78, w=152, h=40)              # scripted-GUI country name, 1-2 lines, centred both ways
# a test version with larger flags (VALSORA_FLAG_SCALE, the Valsora mod's common.FLAG_SCALE; v0.8.2): the flag at
# 1:1 in the medallion's middle, the medallion as much taller as the flag is, and what hangs under it with it
FLAG_SCALE = float(os.environ.get("VALSORA_FLAG_SCALE", "1"))
if FLAG_SCALE != 1:
    _fw, _fh = round(82 * FLAG_SCALE), round(52 * FLAG_SCALE)
    _dy = _fh - 52
    FLAG = dict(x=MED["x"] + (MED["w"] - _fw) // 2, y=18, w=_fw, h=_fh)
    MED = dict(MED, h=MED["h"] + _dy)
    MED_STEPS = (MED_STEPS[0] + _dy, MED_STEPS[1] + _dy)
    NAME = dict(NAME, y=NAME["y"] + _dy)
# the flag's frame (v0.10.2, from the user's mockup of the medallion): a gilt rim on the flag, a lacquer mat, a gilt
# line round it, and at each corner two gilt brackets stepping out from it (FRAME_STEPS: each one's distance in from
# the frame's outer edge and the length of its arms); 8 px with a hairline, a mat and corner diamonds until then
FLAG_MARGIN = 10
FLAG_FRAME = dict(x=FLAG["x"] - FLAG_MARGIN, y=FLAG["y"] - FLAG_MARGIN, w=FLAG["w"] + 2 * FLAG_MARGIN,
                  h=FLAG["h"] + 2 * FLAG_MARGIN)
FRAME_LINE = 5                                    # the gilt line round the mat, in from the frame's edge
FRAME_STEPS = ((0, 7), (2, 12))                   # the corner brackets: (in from the edge, arm length)
# the name's text box reaches this much further above and below NAME (v0.8.2): in a box exactly two lines of the large
# font high (2 x 20 px), the game showed only the first line ("KAMPFIAN ...", "UTOPIAN ...": the user's screenshot,
# 2026-10-15); centred in the taller box, one or two lines land where they did
NAME_SLACK = 4
NAME_FONTS = ("valsora_deco_name_big", "valsora_deco_name")   # big for most names, small for long words
# the game centres a line on its letters' advances, the last letter's tracking (gen_fonts: 4 and 1 px) included, so a
# centred name's ink sat left of the medallion's middle: 1 px, measured on the user's mockup (v0.10.2: "it looks like
# the name isn't centered?"; ROUENTAL's ink 27 to 134, the plate 4 to 159). Each font's box is that much further right
NAME_SHIFT = {"valsora_deco_name_big": 1, "valsora_deco_name": 0}
# v0.4: the seal hanging from the medallion is the DECISIONS button (used far more than factions);
# the faction button moved into the crown row (first slot)
SEAL = dict(x=70, y=125 + MED["h"] - 148, w=44, h=44)   # decisions seal (octagon, 2 frames like vanilla)
SEAL_GLOW = 10                                    # the decisions alert glow is drawn this much larger all round
# the game's views at the screen's left edge under the top bar (the selected armies, air wings, operatives) start this
# far down, under the medallion and its seal, instead of at the game's y 77-80 (v0.8.2: make_mapviews.py; the user,
# 2026-10-15: "the army tab is covered up by the country tab")
BELOW_MEDALLION = SEAL["y"] + SEAL["h"] + 4
# the decision counters (vanilla's 17 px badges, 20 px text) sit on the plate's lower step either side of the
# seal (v0.4.8; until then both were on its right edge, partly below the plate): the politics panel, drawn
# over the top bar, leaves the plate and the seal uncovered (layout_politics.NOTCH), so they stay visible
# v0.9.1: the user's screenshot had the seal 2.7 px from the timeout badge and 4.7 px from the other ("they should both
# be the same distance away from the decision button"): the timeout badge 2 px further left
# v0.10.1 (the author's screenshot, the shoulders either side of the seal outlined: "Maybe move the notifications on
# this screen to something like this"): each badge centred in a shoulder of the plate, between its two steps (12 % to
# 26 % of the medallion's width, and 74 % to 88 %), its top on the first step. The badge's picture is drawn 2 px right
# of the position the game's number is given (as the game's own are), so the position is 2 px left of the picture.
_shoulder = lambda f0, f1: MED["x"] + MED["w"] * (f0 + f1) / 2
DEC_BADGE = 17                                       # the game's topbar_alert_bg (the Deco UI's count badge)
DEC_BADGES = dict(timeout=(round(_shoulder(.12, .26) - DEC_BADGE / 2) - 2, MED_STEPS[0]),
                  to_take=(round(_shoulder(.74, .88) - DEC_BADGE / 2) - 2, MED_STEPS[0]))
FACTION_LOGO = dict(dx=8, dy=11, scale=0.85)      # faction logo (32 px miniature) centred in the crown's ring
FACTION_INIT = dict(dx=24, dy=33, w=24, h=14)     # faction initiative: bottom-right corner of the crown

# ------------------------------------------------------------------ crown buttons
# v0.9.1: the crowns 4 px apart (6 until then), to make room in the strip for fuel, supply and convoys
BTN_W, BTN_H, BTN_GAP = 44, 46, 4
MENU_X, MENU_Y = 184, 6
MENU = ["faction", "intelligence", "technology", "diplomacy", "trade", "construction",
        "production", "deployment", "logistics", "officer"]
MENU_POS = {k: MENU_X + i * (BTN_W + BTN_GAP) for i, k in enumerate(MENU)}
MENU_END = MENU_POS[MENU[-1]] + BTN_W            # 660

# ------------------------------------------------------------------ primary readouts in the band
# the labels' own cut of the small tracked capitals, tracked 1 px less than valsora_deco_label (v0.9.1: room for the
# logistics cell)
LABEL_FONT, VALUE_FONT = "valsora_deco_label_tb", "valsora_deco_value_17"
ICON = 24
ITEMS = [  # key, loc key, label, widest value the engine is likely to write
    ("pp", "VAL_DECO_TB_PP", "Political Power", "999"),
    ("stability", "VAL_DECO_TB_STABILITY", "Stability", "100%"),
    ("war", "VAL_DECO_TB_WAR_SUPPORT", "War Support", "100%"),
    ("manpower", "VAL_DECO_TB_MANPOWER", "Manpower", "151.2K"),
    ("factory", "VAL_DECO_TB_FACTORIES", "Factories", "\u25c645 \u25c630 \u25c68"),
]
# ------------------------------------------------------------------ logistics: a cell of its own in the strip
# v0.9.1 (the user, 2026-10-16: "could we experiment with trying to find a way to move this up into the main bar? That
# way notifications could extend across the screen until the music bar"): fuel, supply and convoys hung in a tray under
# the strip until then; now they are the strip's last cell, after Factories: three rows, each an icon, the value and
# the game's ratio bar under the value
LOG = ["fuel", "supply", "convoys"]
LOG_FONT = "valsora_deco_value_11"               # value_12 until v0.10.1 (the author: "shrink the text ... just a little")
LOG_ICON, LOG_ROW_H, LOG_Y0 = 13, 15, 7          # rows at y 7, 22, 37 (the readouts' hover areas are y 6-52)
LOG_VALUE_W = 38                                 # "999.9K" in value_12 (value_11 since v0.10.1: room to spare)
LOG_W = 2 + LOG_ICON + 4 + LOG_VALUE_W + 2
BAR_W, BAR_H = LOG_VALUE_W, 2

STRIP_X0, STRIP_X1 = MENU_END + 8, 1400          # first and last divider (686, 1394 until v0.9.1)
DIV_H, DIV_Y = 36, 11
ICON_Y = 29 - ICON // 2
LABEL_Y = box_y_for_caps(LABEL_FONT, 14)
VALUE_Y = box_y_for_caps(VALUE_FONT, 30)


def _strip():
    pad, igap = 2, 6                                  # igap 7 until v0.9.1
    content = [max(measure(LABEL_FONT, lab.upper()), measure(VALUE_FONT, v)) + 2 for _, _, lab, v in ITEMS]
    widths = [pad + ICON + igap + c + pad for c in content] + [LOG_W]
    n = len(widths)
    free = (STRIP_X1 - STRIP_X0) - (n + 1) - sum(widths)   # n+1 one-pixel dividers
    gap = free / (2 * n)
    assert gap >= 6.5, ("strip too tight", gap)
    out, x = [], STRIP_X0
    dividers = [x]
    for (key, loc, lab, v), w, c in zip(ITEMS + [("logistics", None, None, None)], widths, content + [None]):
        x0 = x + 1 + gap
        out.append(dict(key=key, loc=loc, label=lab, x=round(x0), w=w, icon_x=round(x0 + pad),
                        text_x=round(x0 + pad + ICON + igap), text_w=c))
        x = x0 + w + gap
        dividers.append(round(x))
        x = round(x)
    dividers[-1] = STRIP_X1
    # value boxes may run on into the gap, up to the next divider (large numbers)
    for it, d in zip(out, dividers[1:]):
        it["value_w"] = d - 3 - it["text_x"]
    cell = out.pop()
    rows = []
    for i, k in enumerate(LOG):
        y = LOG_Y0 + i * LOG_ROW_H
        vx = cell["x"] + 2 + LOG_ICON + 4
        # the value's capitals from y to y + 9 (the font draws them 1 px under box_y_for_caps), its bar 2 px under them,
        # the icon level with both
        rows.append(dict(key=k, x=cell["x"], w=LOG_W, y=y, h=LOG_ROW_H, icon_x=cell["x"] + 2, icon_y=y,
                         value_x=vx, value_w=LOG_VALUE_W, value_y=box_y_for_caps(LOG_FONT, y - 1), bar_y=y + 12))
    return out, dividers, gap, rows


STRIP, DIVIDERS, STRIP_GAP, SECONDARY = _strip()

# ------------------------------------------------------------------ the right-hand tray's values (command power, nukes)
SEC_FONT = "valsora_deco_value_15"
SMALL_FONT = "valsora_deco_value_12"
TRAY_ICON = 18

# ------------------------------------------------------------------ date cartouche
CART = dict(x=1410, y=6, w=400, h=46)
PAUSE_C = (34, 23)                            # pause diamond centre (cartouche-local)
DATE_BOX = dict(x=55, w=230)                  # the widest date of 2036-2049, '00:00, 30 September, 2040', is 230 px
DATE_BOX["y"] = box_y_for_caps("valsora_deco_date", 23 - 6)
CHEV_W, CHEV_H, CHEV_X0, CHEV_STEP, CHEV_Y = 12, 18, 286, 12, 14   # x 280 until v0.6 (220 px dates)
PM_W, PM_H, PM_X, PLUS_Y, MINUS_Y = 22, 15, 354, 7, 24

# ------------------------------------------------------------------ right-hand plate
RPLATE = dict(x=1388, y=0, w=RIGHT - 1388, h=112)   # armyoverview_buttons_bg (right-anchored)
WT_C, WT_R = (1845, 44), 30                          # ring around vanilla world tension
WT_ICON = (WT_C[0] - 25, WT_C[1] - 25)               # vanilla globe is ~50x50 (measured in-game)
WT_GLOW = (WT_ICON[0] - 15, WT_ICON[1] - 15)         # vanilla keeps the glow 15px up-left of the globe
WT_VALUE = dict(x=1820, y=82, w=50, h=20)
# v0.9.1: the tray's edge 12 px further left (the user, 2026-10-16: "it currently looks odd how the music button is
# directly next to the border of this. Please extend the border out a little"): its lower step 14 px from the button
RTRAY = dict(x=1466, y=62, h=46)
OVERVIEW_W, OVERVIEW_H = 44, 40
OVERVIEW = {"army": 1584, "navy": 1632, "air": 1680}
OVERVIEW_Y = 65
# experience badge on each overview button: centred on its foot, inside it (v0.10.2, the user: "The xp bars should be
# at the bottom center of the army, navy and air tabs. The xp number should be centered in the box"; it sat at the
# right, 4 px past the button's edge and 2 px below it). text_y: the digits' box y, from the screenshot of v0.10.1 (with
# y 5 the game drew the digits' ink 5.5 to 13.8 px down the 15 px badge, 2.5 px lower than the preview's font model
# has it), so the ink is centred at 7.5 in game
XP_BADGE = dict(dx=(OVERVIEW_W - 26) // 2, dy=OVERVIEW_H - 15, w=26, h=15, text_y=3)
XP_KEYS = {"army": "land", "navy": "navy", "air": "air"}
PLAYLIST = dict(x=1492, y=72, w=26, h=26)
CP = dict(x=1526, y=66, w=50, h=32)                  # command power: icon + value
NUKES = dict(x=1732, y=66, w=44, h=32)
ACHIEVEMENTS = (1782, 70)
RTRAY_SEPS = [1522, 1579, 1728]
DISMISSED = (1882, 70)
MENU_BTN = dict(x=1882, y=6, w=30, h=24)
HELP_BTN = dict(x=1882, y=32, w=30, h=22)
MUSIC_Y = 112

# ------------------------------------------------------------------ alerts (interface/alerts.gui)
# moved from the readouts (723,40) to a row under the menu buttons; until v0.9.1 it stopped at the logistics tray (10
# icons a row), now it runs on to the right-hand tray
ALERTS_START = (MENU_X, 70)
ALERT_STEP, ALERT_W = 48, 44                         # alerticon_offset x; the icons' width
ALERTS_ROW_MAX = (RTRAY["x"] - 8 - ALERT_W - ALERTS_START[0]) // ALERT_STEP * ALERT_STEP   # last icon offset in a row

if __name__ == "__main__":
    for s in STRIP:
        print(s)
    print("dividers", DIVIDERS, "gap", round(STRIP_GAP, 1))
    for s in SECONDARY:
        print(s)
    print("alerts row max", ALERTS_ROW_MAX, "->", ALERTS_ROW_MAX // ALERT_STEP + 1, "icons a row")
    print("label y", LABEL_Y, "value y", VALUE_Y, "date y", DATE_BOX["y"])
    print("date width", measure("valsora_deco_date", "12:00, 29 SEPTEMBER, 1939"))
    for n in ["ROUENTAL", "FRAXHEMARK", "TERRABIS-SERAN", "PONCHOMAGNIFICO"]:
        print(n, [measure(f, n) for f in NAME_FONTS])
