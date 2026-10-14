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
MED_STEPS = (122, 135)                            # y where the plate steps in to 12%/88%, then 26%/74%
FLAG = dict(x=51, y=18, w=82, h=52)               # player_flag (own 82x52 masked shield, 1:1)
FLAG_FRAME = dict(x=FLAG["x"] - 8, y=FLAG["y"] - 8, w=FLAG["w"] + 16, h=FLAG["h"] + 16)  # gilt + mat + gilt
NAME = dict(x=16, y=78, w=152, h=40)              # scripted-GUI country name, 1-2 lines, centred both ways
NAME_FONTS = ("valsora_deco_name_big", "valsora_deco_name")   # big for most names, small for long words
# v0.4: the seal hanging from the medallion is the DECISIONS button (used far more than factions);
# the faction button moved into the crown row (first slot)
SEAL = dict(x=70, y=125, w=44, h=44)              # decisions seal (octagon, 2 frames like vanilla)
SEAL_GLOW = 10                                    # the decisions alert glow is drawn this much larger all round
DEC_BADGES = dict(timeout=(SEAL["x"] + 31, SEAL["y"] - 1), to_take=(SEAL["x"] + 31, SEAL["y"] + 27))
FACTION_LOGO = dict(dx=8, dy=11, scale=0.85)      # faction logo (32 px miniature) centred in the crown's ring
FACTION_INIT = dict(dx=24, dy=33, w=24, h=14)     # faction initiative: bottom-right corner of the crown

# ------------------------------------------------------------------ crown buttons
BTN_W, BTN_H, BTN_GAP = 44, 46, 6
MENU_X, MENU_Y = 184, 6
MENU = ["faction", "intelligence", "technology", "diplomacy", "trade", "construction",
        "production", "deployment", "logistics", "officer"]
MENU_POS = {k: MENU_X + i * (BTN_W + BTN_GAP) for i, k in enumerate(MENU)}
MENU_END = MENU_POS[MENU[-1]] + BTN_W            # 678

# ------------------------------------------------------------------ primary readouts in the band
LABEL_FONT, VALUE_FONT = "valsora_deco_label", "valsora_deco_value_17"
ICON = 24
ITEMS = [  # key, loc key, label, widest value the engine is likely to write
    ("pp", "VAL_DECO_TB_PP", "Political Power", "999"),
    ("stability", "VAL_DECO_TB_STABILITY", "Stability", "100%"),
    ("war", "VAL_DECO_TB_WAR_SUPPORT", "War Support", "100%"),
    ("manpower", "VAL_DECO_TB_MANPOWER", "Manpower", "151.2K"),
    ("factory", "VAL_DECO_TB_FACTORIES", "Factories", "\u25c645 \u25c630 \u25c68"),
]
STRIP_X0, STRIP_X1 = 686, 1394                   # first and last divider
DIV_H, DIV_Y = 36, 11
ICON_Y = 29 - ICON // 2
LABEL_Y = box_y_for_caps(LABEL_FONT, 14)
VALUE_Y = box_y_for_caps(VALUE_FONT, 30)


def _strip():
    pad, igap = 2, 7
    content = [max(measure(LABEL_FONT, lab.upper()), measure(VALUE_FONT, v)) + 2 for _, _, lab, v in ITEMS]
    widths = [pad + ICON + igap + c + pad for c in content]
    n = len(ITEMS)
    free = (STRIP_X1 - STRIP_X0) - (n + 1) - sum(widths)   # n+1 one-pixel dividers
    gap = free / (2 * n)
    assert gap >= 6.5, ("strip too tight", gap)
    out, x = [], STRIP_X0
    dividers = [x]
    for (key, loc, lab, v), w, c in zip(ITEMS, widths, content):
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
    return out, dividers, gap


STRIP, DIVIDERS, STRIP_GAP = _strip()

# ------------------------------------------------------------------ logistics tray (hangs under the strip)
# v0.3: only fuel, supply and convoys; experience moved onto the army/navy/air buttons as badges and
# command power / nukes into the right-hand tray
SEC_FONT = "valsora_deco_value_15"
SMALL_FONT = "valsora_deco_value_12"
TRAY_ICON = 18
LOG = [("fuel", 44), ("supply", 44), ("convoys", 40)]   # key, value box width
TRAY = dict(y=62, h=32)


def _log_tray():
    item_w = [TRAY_ICON + 5 + vw for _, vw in LOG]
    w = 14 + sum(item_w) + 17 * (len(LOG) - 1) + 14
    x = round((STRIP_X0 + STRIP_X1) / 2 - w / 2)
    TRAY.update(x=x, w=w)
    out, seps, cx = [], [], x + 14
    for i, ((k, vw), iw) in enumerate(zip(LOG, item_w)):
        out.append(dict(key=k, x=cx, w=iw, icon_x=cx, value_x=cx + TRAY_ICON + 5, value_w=vw))
        cx += iw
        if i < len(LOG) - 1:
            seps.append(cx + 8)
            cx += 17
    return out, seps


SECONDARY, TRAY_SEPS = _log_tray()
SEC_Y = TRAY["y"] + 2                          # top of each slot (slot height 30)
SEC_ICON_Y = SEC_Y + 6
SEC_VALUE_Y_BAR = box_y_for_caps(SEC_FONT, SEC_Y + 5)
SEC_BAR_Y = SEC_Y + 21
BAR_W, BAR_H = 42, 3

# ------------------------------------------------------------------ date cartouche
CART = dict(x=1410, y=6, w=400, h=46)
PAUSE_C = (34, 23)                            # pause diamond centre (cartouche-local)
DATE_BOX = dict(x=58, w=220)
DATE_BOX["y"] = box_y_for_caps("valsora_deco_date", 23 - 6)
CHEV_W, CHEV_H, CHEV_X0, CHEV_STEP, CHEV_Y = 12, 18, 280, 12, 14
PM_W, PM_H, PM_X, PLUS_Y, MINUS_Y = 22, 15, 354, 7, 24

# ------------------------------------------------------------------ right-hand plate
RPLATE = dict(x=1388, y=0, w=RIGHT - 1388, h=112)   # armyoverview_buttons_bg (right-anchored)
WT_C, WT_R = (1845, 44), 30                          # ring around vanilla world tension
WT_ICON = (WT_C[0] - 25, WT_C[1] - 25)               # vanilla globe is ~50x50 (measured in-game)
WT_GLOW = (WT_ICON[0] - 15, WT_ICON[1] - 15)         # vanilla keeps the glow 15px up-left of the globe
WT_VALUE = dict(x=1820, y=82, w=50, h=20)
RTRAY = dict(x=1478, y=62, h=46)
OVERVIEW_W, OVERVIEW_H = 44, 40
OVERVIEW = {"army": 1584, "navy": 1632, "air": 1680}
OVERVIEW_Y = 65
XP_BADGE = dict(dx=22, dy=27, w=26, h=15)            # experience badge on each overview button
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
# moved from the readouts (723,40) to a row under the menu buttons, left of the logistics tray
ALERTS_START = (MENU_X, 70)
ALERTS_ROW_MAX = 432                                 # last icon offset in a row -> 10 per row

if __name__ == "__main__":
    for s in STRIP:
        print(s)
    print("dividers", DIVIDERS, "gap", round(STRIP_GAP, 1))
    for s in SECONDARY:
        print(s)
    print("tray", TRAY, "seps", TRAY_SEPS)
    print("label y", LABEL_Y, "value y", VALUE_Y, "date y", DATE_BOX["y"])
    print("date width", measure("valsora_deco_date", "12:00, 29 SEPTEMBER, 1939"))
    for n in ["ROUENTAL", "FRAXHEMARK", "TERRABIS-SERAN", "PONCHOMAGNIFICO"]:
        print(n, [measure(f, n) for f in NAME_FONTS])
