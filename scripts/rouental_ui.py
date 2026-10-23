"""Rouental's governorates and three estates in the game, bare bones (the author, 2026-10-21, night: "I think we should
start to try to put the mockups into practice, to make sure everything were planning will work. Let's get them into
the game, even if they're bare bones for now"; 2026-10-23: "Put the three estates in game, bare bones"). The mockups are
deco_ui/art/proposals/governorates/ and three_estates/ (the three powers' before them, three_powers/).

Run after build_mod.py and deco_ui.py (run_all.sh): it reads the build (the provinces map, the states, their names and
manpower: rouental_realm.py) and writes into it:
  - the three estates (the First, the clergy; the Second, the nobility; the Third, the commons), in place of the three
    powers: a button on the politics screen where the game's balance of power sits, and beside it a window with the
    triangle (each estate's symbol in its corner, source/estates/), the marker placed by the shares (scripted GUI
    properties), its six months' trail, the zone and its effects (a national spirit each), the estates' cards, the
    Crown (Royal Authority, and whom the Court follows between Roland and Serelle: a dynamic modifier of each side's
    bonuses, moved toward Serelle by her won battles), six decisions, the Promised Reforms (a mission), the estates'
    leanings moving the governorates' loyalty (Pious to the First, Proud to the Second, Mercantile to the Third, Leal
    to the Crown), and in the Lords' Realm how many généralités would break away; a monthly drift;
  - the governorates: a decision category (with a scripted GUI) that opens the map of the realm: every governorate
    drawn from the build's own state borders and coloured by its loyalty, clickable (its shape, and its seal), a card
    with its governor, loyalty, estates, peoples and states (a dynamic list: people, levies seen by inspectors, men),
    four actions (Send Inspectors, Grant Privileges, Demand Levies, Summon the Estates); loyalty moves each state's
    manpower (a dynamic modifier); the Crown's Domain apart; and the Blue Guard of Brume as an emergency decision.
Every name and number but the author's (the estates' start, the holders, the symbols, Cloister and Castle, the peoples'
leanings, the Blue Guard) is a placeholder, as in the mockups. What is assumed about the game is listed in
docs/CONTENT.md.
"""
import math
import os
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rouental_realm as RM  # noqa: E402
import nations  # noqa: E402
from common import DECO_UI  # noqa: E402
from imgio import write_dds  # noqa: E402

OUT = Path("build/valsora_test")
GFX = "gfx/interface/valsora_rouental"
FONTS_DIR = Path("deco_ui/source_fonts")
SS = 4                                     # supersampling for the pictures drawn here

# ---------------------------------------------------------------- palette (deco_ui/CLAUDE.md, section 5)
LAC, LAC2, DARK = (17, 25, 30), (23, 34, 42), (11, 16, 20)
GILT, RULE, HI = (227, 199, 126), (201, 165, 90), (241, 220, 156)
JADE = (46, 110, 96)
CREAM, LABEL = (244, 236, 217), (183, 166, 128)

F = (dict(title="valsora_deco_title_24", head="valsora_deco_title_18", body="valsora_deco_body_15",
          small="valsora_deco_body_13", label="valsora_deco_label", value="valsora_deco_value_15",
          big="valsora_deco_heading_24", italic="valsora_deco_italic_15", italic_13="valsora_deco_italic_13",
          button="valsora_deco_body_13")
     if DECO_UI else
     dict(title="hoi_24header", head="hoi_20bs", body="hoi_16mbs", small="hoi_16mbs", label="hoi_16mbs",
          value="hoi_18mbs", big="hoi_24header", italic="hoi_16mbs", italic_13="hoi_16mbs", button="hoi_16mbs"))


# ---------------------------------------------------------------- drawing
def font(face, px):
    path = {"federo": FONTS_DIR / "federo/Federo-Regular.ttf",
            "josefin": FONTS_DIR / "josefinsans/JosefinSans[wght].ttf"}[face]
    f = ImageFont.truetype(str(path), px)
    if face == "josefin":
        try:
            f.set_variation_by_axes([600])
        except Exception:  # noqa: BLE001  (a Pillow without variation support draws the default weight)
            pass
    return f


def tracked(draw, xy, text, fnt, fill, track=0.0, anchor_centre=False):
    """text with letter spacing (track: a fraction of the size), its left (or centre) at xy"""
    size = fnt.size
    widths = [draw.textlength(c, font=fnt) for c in text]
    total = sum(widths) + track * size * (len(text) - 1)
    x, y = xy
    if anchor_centre:
        x -= total / 2
    for c, w in zip(text, widths):
        draw.text((x, y), c, font=fnt, fill=fill)
        x += w + track * size
    return total


def down(img):
    return img.resize((img.width // SS, img.height // SS), Image.LANCZOS)


def chamfer_poly(x0, y0, x1, y1, c):
    return [(x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c), (x1 - c, y1), (x0 + c, y1), (x0, y1 - c),
            (x0, y0 + c)]


def plate(w, h, c=6, lit=False, gold=False):
    """a chamfered lacquer plate with a gilt rim (the Deco UI's bar and button): jade when lit, gold for the main one"""
    W, H = w * SS, h * SS
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon(chamfer_poly(0, 0, W - 1, H - 1, c * SS), fill=(*RULE, 255))
    top, bot = ((44, 102, 90), (22, 58, 51)) if lit else (((233, 209, 144), (156, 122, 54)) if gold else ((36, 50, 58), (14, 21, 25)))
    inner = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = np.linspace(0, 1, H)[:, None, None]
    grad = (np.array(top)[None, None] * (1 - g) + np.array(bot)[None, None] * g).repeat(W, 1)
    stripes = ((np.arange(W) // SS) % 7 == 0)[None, :, None] * 6
    grad = np.clip(grad + stripes, 0, 255)
    inner = Image.fromarray(np.concatenate([grad, np.full((H, W, 1), 255)], 2).astype(np.uint8))
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon(chamfer_poly(SS, SS, W - 1 - SS, H - 1 - SS, c * SS - SS * .4), fill=255)
    im.paste(inner, (0, 0), m)
    d.line([(c * SS + 3 * SS, 2 * SS), (W - c * SS - 3 * SS, 2 * SS)], fill=(241, 220, 156, 90), width=SS)
    return down(im)


def save(name, img, frames=1, effect=None):
    """writes the picture and returns its sprite's definition"""
    rel = f"{GFX}/{name}.dds"
    (OUT / rel).parent.mkdir(parents=True, exist_ok=True)
    write_dds(OUT / rel, np.asarray(img.convert("RGBA")))
    lines = ["\tspriteType = {", f'\t\tname = "GFX_rou_{name}"', f'\t\ttexturefile = "{rel}"']
    if frames > 1:
        lines.append(f"\t\tnoOfFrames = {frames}")
    if effect:
        lines.append(f'\t\teffectFile = "{effect}"')
    SPRITES.append("\n".join(lines + ["\t}"]))
    return f"GFX_rou_{name}"


def save_tile(name, img):
    """a picture the game stretches to its element's size (a cornered tile without corners): the click areas"""
    rel = f"{GFX}/{name}.dds"
    (OUT / rel).parent.mkdir(parents=True, exist_ok=True)
    write_dds(OUT / rel, np.asarray(img.convert("RGBA")))
    SPRITES.append("\n".join(["\tcorneredTileSpriteType = {", f'\t\tname = "GFX_rou_{name}"', f'\t\ttexturefile = "{rel}"',
                              "\t\tborderSize = { x = 0 y = 0 }", "\t}"]))
    return f"GFX_rou_{name}"


SPRITES = []
BUTTON_FX = "gfx/FX/buttonstate.lua"
HIT = 4                                          # the click areas' grain, window px


def hit_rects(S, gov_of, royal):
    """rectangles that tile the governorates at the window's scale, (x, y, w, h, governorate: 27 the Crown's): a cell
    of HIT px goes to the governorate with most of it once Rouental has 30 % of it; a row's cells of one governorate
    are one rectangle, and rows alike below one another one too"""
    lut = {int(s): gov_of.get(int(s), 27 if int(s) in royal else 0) for s in np.unique(S)}
    cls = np.vectorize(lut.get)(S)
    MW, MH = S.shape[1] * U // 5, S.shape[0] * U // 5
    win = cls[(np.arange(MH) * 5 // U)[:, None], (np.arange(MW) * 5 // U)[None, :]]
    out, open_ = [], {}
    for r, cy in enumerate(range(0, MH, HIT)):
        row = []
        for cx in range(0, MW, HIT):
            n = np.bincount(win[cy:cy + HIT, cx:cx + HIT].ravel(), minlength=28)
            row.append(0 if n[1:].sum() < .3 * n.sum() else int(np.argmax(n[1:])) + 1)
        runs, c = [], 0
        while c < len(row):
            c0 = c
            while c < len(row) and row[c] == row[c0]:
                c += 1
            if row[c0]:
                runs.append((c0, c, row[c0]))
        nxt = {run: open_.pop(run, r) for run in runs}
        out += [(c0 * HIT, r0 * HIT, min(c1 * HIT, MW) - c0 * HIT, r * HIT - r0 * HIT, k) for (c0, c1, k), r0 in open_.items()]
        open_ = nxt
    rows = -(-MH // HIT)
    out += [(c0 * HIT, r0 * HIT, min(c1 * HIT, MW) - c0 * HIT, min(rows * HIT, MH) - r0 * HIT, k)
            for (c0, c1, k), r0 in open_.items()]
    return sorted(out, key=lambda o: (o[1], o[0]))


# ---------------------------------------------------------------- .gui pieces
def q(s):
    return f'"{s}"'


def box(kind, name, x, y, extra, kids=()):
    lines = [f"\t{kind} = {{", f"\t\tname = {q(name)}", f"\t\tposition = {{ x = {round(x)} y = {round(y)} }}"]
    lines += [f"\t\t{e}" for e in extra]
    for k in kids:
        lines += ["\t" + ln for ln in k.split("\n")]
    return "\n".join(lines + ["\t}"])


def window(name, x, y, w, h, kids, bg=None):
    extra = [f"size = {{ width = {w} height = {h} }}", "Orientation = UPPER_LEFT", "clipping = no"]
    if bg:
        extra.append(f'background = {{ name = "{name}_bg" quadTextureSprite = "{bg}" }}')
    return box("containerWindowType", name, x, y, extra, kids)


def icon(name, sprite, x, y, scale=None, transparent=False, tooltip=None, frame=None):
    extra = [f"spriteType = {q(sprite)}"]
    if scale:
        extra.append(f"scale = {scale}")
    if frame:
        extra.append(f"frame = {frame}")
    if transparent:
        extra.append("alwaystransparent = yes")
    if tooltip:
        extra.append(f"pdx_tooltip = {q(tooltip)}")
    return box("iconType", name, x, y, extra)


def button(name, sprite, x, y, text=None, fnt=None, tooltip=None):
    extra = [f"spriteType = {q(sprite)}"]
    if text:
        extra += [f"buttonText = {q(text)}", f"buttonFont = {q(fnt or F['button'])}"]
    if tooltip:
        extra.append(f"pdx_tooltip = {q(tooltip)}")
    extra.append('clicksound = click_default')
    return box("buttonType", name, x, y, extra)


def text(name, x, y, w, h, key, fnt, fmt="left", tooltip=None, valign=False):
    extra = [f"font = {q(F[fnt] if fnt in F else fnt)}", f"text = {q(key)}", f"format = {fmt}", f"maxWidth = {w}",
             f"maxHeight = {h}", "fixedsize = yes"]
    if valign:
        extra.append("vertical_alignment = center")
    if tooltip:
        extra.append(f"pdx_tooltip = {q(tooltip)}")
    else:
        extra.append("alwaystransparent = yes")
    return box("instantTextBoxType", name, x, y, extra)


def grid(name, x, y, w, h, slot_w, slot_h, cols, rows):
    return box("gridBoxType", name, x, y, [f"size = {{ width = {w} height = {h} }}",
                                           f"slotsize = {{ width = {slot_w} height = {slot_h} }}",
                                           f"max_slots = {{ x = {cols} y = {rows} }}", 'format = "UPPER_LEFT"'])


LOC = ["l_english:"]


def L(key, value):
    LOC.append(f' {key}:0 "{value}"')
    return key


# ================================================================ the three estates
# In place of the three powers (the author, 2026-10-22: "changing the balance of power from Prince - Voix - Speaker, to
# one based on the three estates"; 2026-10-23: "Put the three estates in game, bare bones"): the mockup is
# deco_ui/art/proposals/three_estates/, the plan docs/ROUENTAL_ESTATES.md. The author's: the estates, the start 35 / 35 /
# 30, Royal Authority apart from the triangle, the Court's scale between Roland and Serelle (diplomacy for him, the army
# for her, her battles), Tara Blanchart for the Second Estate, the Third's champion to be named, the symbols inside the
# triangle, Cloister and Castle. Everything else (the zones' names and effects, Royal Authority's numbers, the
# decisions, the leanings, the breaking line) is the mockup's placeholder.
ESTATES = [("first", "The First Estate", "First", (233, 227, 210)), ("second", "The Second Estate", "Second", (190, 98, 104)),
           ("third", "The Third Estate", "Third", (111, 155, 192))]
START = (35, 35, 30)            # the author's (2026-10-22): "35/35/30 yes"
HOLDERS = [("Anserra IX", "The clergy · the Voix", "Head of the Seran faith."),
           ("Tara Blanchart", "The nobility · Lady Chancellor", "Roland's friend; Speaker of the Estates."),
           ("To be named", "The commons · their champion", "A placeholder: the author's to come.")]
GROUNDS = {"first": ((58, 53, 42), (14, 13, 10)), "second": ((74, 30, 36), (18, 8, 10)),
           "third": ((30, 51, 71), (9, 14, 20))}          # the symbols' grounds (the mockup's symbols.GROUNDS)
SYMBOLS = Path("source/estates")                          # scripts/estate_symbols.py draws them from the mockup's
DRIFT_NAMES = {"political_power_factor": ("political power", "%"), "stability_factor": ("stability", "%"),
               "theocracy_drift": ("Theocratic support", "day"), "democratic_drift": ("Democratic support", "day"),
               "communism_drift": ("Communist support", "day")}
# the seven zones (scripted as rou_es_zone 1 to 7, in this order); ra: Royal Authority a month there; loyalty: the
# estates of an attitude (or "south", the Southmarchers' généralités) gaining or losing loyalty while it holds
ZONES = [
    dict(key="first", name="The Voix Behind the Curtain", where="The First Estate holds 60 or more",
         desc="The Voix rules through the Prince's council; the realm prays as she bids.",
         leads="The Voix's path: Anserra IX's theocracy (Accept Reality)",
         pts=((100, 0, 0), (60, 40, 0), (60, 0, 40)), col=ESTATES[0][3], ra=-2,
         mods={"stability_factor": 0.1, "theocracy_drift": 0.05}, loyalty=[("Pious", 10), ("south", -10)]),
    dict(key="second", name="The Lords' Realm", where="The Second Estate holds 60 or more",
         desc="The vassals take back what the Crown had gathered: the realm comes apart.",
         leads="The decentralization: Tara Blanchart governs; the disloyal généralités break away",
         pts=((0, 100, 0), (40, 60, 0), (0, 60, 40)), col=ESTATES[1][3], ra=-2, mods={}, loyalty=[("Proud", 10)]),
    dict(key="third", name="The Commons Ascendant", where="The Third Estate holds 60 or more",
         desc="The Estates General's third chamber speaks for the realm, and the realm listens.",
         leads="Reform and a constitutional monarchy; or, if reform was promised and never made, the commons rise",
         pts=((0, 0, 100), (40, 0, 60), (0, 40, 60)), col=ESTATES[2][3], ra=-2,
         mods={"democratic_drift": 0.05, "stability_factor": -0.05}, loyalty=[("Mercantile", 10)]),
    # "Cloister and Castle" is the author's (2026-10-23: "I'll go with Cloister and Castle"); the rest Claude's
    dict(key="no_third", name="Cloister and Castle", where="The Third Estate under 15",
         desc="Clergy and lords govern between them; the commons go unheard.", leads="No path of its own: the commons' anger grows",
         pts=((60, 40, 0), (40, 60, 0), (25, 60, 15), (60, 25, 15)), col=None, mix=(0, 1), ra=0,
         mods={"stability_factor": 0.05, "political_power_factor": 0.1, "communism_drift": 0.02}, loyalty=[]),
    dict(key="no_second", name="Church and Commons", where="The Second Estate under 15",
         desc="The Faith and the commons govern together; the lords sulk in their manors.",
         leads="No path of its own: the lords grow restive",
         pts=((60, 0, 40), (40, 0, 60), (25, 15, 60), (60, 15, 25)), col=None, mix=(0, 2), ra=0,
         mods={"stability_factor": 0.05}, loyalty=[("Proud", -10)], more="Demand Levies costs half again in loyalty"),
    dict(key="no_first", name="Manor and Market", where="The First Estate under 15",
         desc="Lords and commons govern without the Voix; the pulpits murmur.", leads="No path of its own: the faithful grow uneasy",
         pts=((0, 60, 40), (0, 40, 60), (15, 25, 60), (15, 60, 25)), col=None, mix=(1, 2), ra=0,
         mods={"political_power_factor": 0.05, "stability_factor": -0.05}, loyalty=[("Pious", -10)]),
    dict(key="balance", name="The Balance of Estates", where="None over 60, none under 15",
         desc="No estate can act alone, and the Crown holds the scales.",
         leads="The Prince's path: Royal Authority grows while the balance holds",
         pts=((60, 25, 15), (60, 15, 25), (25, 15, 60), (15, 25, 60), (15, 60, 25), (25, 60, 15)), col=None, ra=1,
         mods={}, loyalty=[]),
]
EDGE_LABELS = {"no_third": ((50, 50, 0), -60), "no_second": ((50, 0, 50), 60), "no_first": ((0, 50, 50), 0)}
# Royal Authority, 0 to 100 (its bands and start Claude's: the regency only just ended)
RA_BANDS = [(0, "A Crown in Name"), (25, "A Contested Crown"), (50, "A Respected Crown"), (75, "A Sovereign Crown")]
RA_START = 30
# whom the Court follows: Roland's share of 100 (Serelle's the rest). Whoever leads gets their side's bonuses, the more
# the further they lead (all of them at a lead of 50): the author's sides, Claude's numbers. key, modifier, full value
FAVOUR_START = 60
FAVOUR = {"roland": [("opinion", "opinion_gain_monthly_factor", 0.25, "opinion gain"),
                     ("relations", "improve_relations_maintain_cost_factor", -0.25, "relations upkeep"),
                     ("trade", "trade_opinion_factor", 0.2, "trade opinion")],
          "serelle": [("xp", "experience_gain_army_factor", 0.25, "army experience"),
                      ("doctrine", "land_doctrine_cost_factor", -0.15, "land doctrine cost"),
                      ("org", "army_org_factor", 0.1, "army organisation")]}
BATTLES_A_MONTH = 5             # Serelle's won combats that move the Court toward her, at most, a month (Claude's)
# the decisions (placeholders): name, what it costs ("pp" political power, "ra" Royal Authority), how much, the estates'
# shifts (first, second, third; "divide": the strongest gives 6, the others take 3), the Court's (toward Roland +)
DECISIONS = [("Endow the Cathedral Chapters", "pp", 50, (6, -3, -3), 0),
             ("Confirm the Lords' Charters", "pp", 50, (-3, 6, -3), 0),
             ("Promise Reform", "pp", 25, (-4, -4, 8), 0),
             ("Divide and Rule", "ra", 10, "divide", 0),
             ("A Royal Embassy", "pp", 50, None, 8),
             ("Serelle's Command", "pp", 50, None, -8)]
PAIRED = 4                                 # the decisions from this one on (the Court's) go two to a row
REFORM_DAYS = 365                          # the Promised Reforms' mission (Claude's)
LEANINGS = [("Pious", "first", "the First Estate"), ("Proud", "second", "the Second Estate"),
            ("Mercantile", "third", "the Third Estate"), ("Leal", "crown", "the Crown")]
BREAK_BELOW = 40                           # a généralité under it would break away in the Lords' Realm (Claude's)

TW, TH = 520, 440                 # the triangle's picture
TRI_A, TRI_L = (260, 40), 400
TRI_H = TRI_L * math.sqrt(3) / 2
TRI_B = (TRI_A[0] - TRI_L / 2, TRI_A[1] + TRI_H)
TRI_C = (TRI_A[0] + TRI_L / 2, TRI_A[1] + TRI_H)
MARK = 26                          # the marker's size
DOT = 8
SYM = 80                           # a symbol in its corner of the triangle


def at(f, s, t):
    n = f + s + t
    return ((f * TRI_A[0] + s * TRI_B[0] + t * TRI_C[0]) / n, (f * TRI_A[1] + s * TRI_B[1] + t * TRI_C[1]) / n)


def zone_colour(z, a):
    if z["col"]:
        return (*z["col"], a)
    if z.get("mix"):
        i, j = z["mix"]
        c = tuple((ESTATES[i][3][k] + ESTATES[j][3][k]) // 2 for k in range(3))
        return (*c, int(a * .55))
    return (255, 255, 255, 8)


def symbol_img(key, n):
    return Image.open(SYMBOLS / f"{key}.png").convert("RGBA").resize((n, n), Image.LANCZOS)


def shadowed(img, blur=2, a=.7):
    """a symbol with a soft dark shadow a pixel under it, as the mockup's drop-shadow"""
    pad = 4
    out = Image.new("RGBA", (img.width + 2 * pad, img.height + 2 * pad), (0, 0, 0, 0))
    sh = np.zeros((out.height, out.width), np.float32)
    sh[pad + 1:pad + 1 + img.height, pad:pad + img.width] = np.asarray(img)[..., 3] / 255 * a
    sh = ndi.gaussian_filter(sh, blur)
    shadow = np.zeros((out.height, out.width, 4), np.uint8)
    shadow[..., 3] = (sh * 255).clip(0, 255).astype(np.uint8)
    out = Image.fromarray(shadow)
    out.alpha_composite(img, (pad, pad))
    return out


def ground(key, w, h):
    """an estate's symbol on its dark ground (the cards' wells)"""
    a, b = GROUNDS[key]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.hypot((xx - w * .5) / w, (yy - h * .42) / h) / .78
    g = np.clip(r, 0, 1)[..., None]
    rgb = np.array(a)[None, None] * (1 - g) + np.array(b)[None, None] * g
    im = Image.fromarray(np.concatenate([rgb, np.full((h, w, 1), 255)], 2).astype(np.uint8))
    n = min(w, h)
    im.alpha_composite(symbol_img(key, n), ((w - n) // 2, (h - n) // 2))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w - 1, h - 1], outline=(201, 165, 90, 150))
    return im


def triangle_picture():
    W, H = TW * SS, TH * SS
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, cy = [(TRI_A[i] + TRI_B[i] + TRI_C[i]) / 3 * SS for i in (0, 1)]
    for k in range(36):                                   # a faint sunburst behind
        a = math.radians(k * 10)
        r = TRI_L * .62 * SS
        d.polygon([(cx, cy), (cx + r * math.cos(a - .04), cy + r * math.sin(a - .04)),
                   (cx + r * math.cos(a + .04), cy + r * math.sin(a + .04))], fill=(201, 165, 90, 14))
    for z in ZONES:
        pts = [tuple(c * SS for c in at(*p)) for p in z["pts"]]
        d.polygon(pts, fill=zone_colour(z, 86))
        d.line(pts + [pts[0]], fill=(227, 199, 126, 105), width=SS)
    corners = [tuple(c * SS for c in p) for p in (TRI_A, TRI_B, TRI_C)]
    d.line(corners + [corners[0]], fill=(*RULE, 255), width=int(1.6 * SS), joint="curve")
    outer = [(cx + (x - cx) * 1.05, cy + (y - cy) * 1.05) for x, y in corners]
    d.line(outer + [outer[0]], fill=(201, 165, 90, 115), width=SS, joint="curve")
    for P, Q in ((TRI_A, TRI_B), (TRI_B, TRI_C), (TRI_C, TRI_A)):     # ticks every tenth
        for i in range(1, 10):
            x, y = (P[0] + (Q[0] - P[0]) * i / 10) * SS, (P[1] + (Q[1] - P[1]) * i / 10) * SS
            ox, oy = x - cx, y - cy
            n = math.hypot(ox, oy)
            ln = (6 if i == 5 else 3.5) * SS
            d.line([(x, y), (x + ox / n * ln, y + oy / n * ln)], fill=(227, 199, 126, 180), width=SS)
    pic = down(im)
    # the names: the edges' outside their strips, along them; the middle's in it (the corners have their symbols)
    fnt = font("federo", 11 * SS)
    labels = {k: (sh, rot, [ZONES[[z["key"] for z in ZONES].index(k)]["name"].upper()]) for k, (sh, rot) in EDGE_LABELS.items()}
    labels["balance"] = ((24, 38, 38), 0, ["THE BALANCE", "OF ESTATES"])
    gcx, gcy = cx / SS, cy / SS
    for key, (share, rot, lines) in labels.items():
        x, y = at(*share)
        if key in EDGE_LABELS:
            n = math.hypot(x - gcx, y - gcy)
            x, y = x + (x - gcx) / n * 19, y + (y - gcy) / n * 19
        lab = Image.new("RGBA", (240 * SS, 40 * SS), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lab)
        for i, s in enumerate(lines):
            tracked(ld, (120 * SS, (20 - 7 * len(lines) + 14 * i) * SS - fnt.size * .5), s, fnt, (244, 236, 217, 200),
                    .1, anchor_centre=True)
        if rot:
            lab = lab.rotate(-rot, resample=Image.BICUBIC, expand=True)
        lab = down(lab)
        pic.alpha_composite(lab, (round(x - lab.width / 2), round(y - lab.height / 2)))
    return pic


def zone_highlight(z):
    """the lit zone: a brighter wash and a gilt line round it, cut to its box"""
    pts = [at(*p) for p in z["pts"]]
    x0, y0 = math.floor(min(p[0] for p in pts)) - 2, math.floor(min(p[1] for p in pts)) - 2
    x1, y1 = math.ceil(max(p[0] for p in pts)) + 2, math.ceil(max(p[1] for p in pts)) + 2
    im = Image.new("RGBA", ((x1 - x0) * SS, (y1 - y0) * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    sp = [((x - x0) * SS, (y - y0) * SS) for x, y in pts]
    d.polygon(sp, fill=(241, 220, 156, 40) if not z["col"] else (*z["col"], 70))
    d.line(sp + [sp[0]], fill=(*HI, 255), width=2 * SS, joint="curve")
    return down(im), (x0, y0)


def corner_centre(k):
    """the centre of an estate's corner zone (a triangle like the whole): where its symbol sits"""
    pts = [at(*p) for p in ZONES[k]["pts"]]
    return sum(p[0] for p in pts) / 3, sum(p[1] for p in pts) / 3


def marker():
    s = MARK * SS
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = s / 2
    def dia(r, fill, outline=None, w=0):
        d.polygon([(c, c - r), (c + r, c), (c, c + r), (c - r, c)], fill=fill, outline=outline, width=w)
    dia(13 * SS, (241, 220, 156, 50))
    dia(9 * SS, (232, 205, 132, 255), (22, 17, 10, 255), int(1.4 * SS))
    dia(4 * SS, (22, 17, 10, 255))
    return down(im)


def dot():
    s = DOT * SS
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse([SS, SS, s - SS, s - SS], fill=(241, 220, 156, 170), outline=(11, 16, 20, 255),
                               width=SS)
    return down(im)


def well_frame(w, h):
    """a thin gilt frame round a portrait or a symbol's well, its middle clear"""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w - 1, h - 1], outline=(*RULE, 200))
    return im


def swatch(col, s=12):
    """a diamond in an estate's colour (the leanings' rows)"""
    im = Image.new("RGBA", (s * SS, s * SS), (0, 0, 0, 0))
    c = s * SS / 2
    r = c - SS
    ImageDraw.Draw(im).polygon([(c, c - r), (c + r, c), (c, c + r), (c - r, c)], fill=(*col, 255),
                               outline=(22, 17, 10, 255), width=int(1.2 * SS))
    return down(im)


def strip(col, h=62):
    return Image.new("RGBA", (3, h), (*col, 255))


def gauge(w, h, fill_top, fill_bot, ticks):
    """a bar of 21 frames, 0 to 100 by fives (the frame set by a variable: properties)"""
    frames = []
    for i in range(21):
        im = Image.new("RGBA", (w, h), (8, 12, 15, 255))
        d = ImageDraw.Draw(im)
        v = i * 5
        fw = round((w - 2) * v / 100)
        if fw:
            for y in range(1, h - 1):
                t = (y - 1) / max(1, h - 3)
                c = tuple(round(fill_top[k] * (1 - t) + fill_bot[k] * t) for k in range(3))
                d.line([(1, y), (fw, y)], fill=(*c, 255))
        for t in ticks:
            x = round((w - 1) * t / 100)
            d.line([(x, 0), (x, h - 1)], fill=(241, 220, 156, 200))
        d.rectangle([0, 0, w - 1, h - 1], outline=(201, 165, 90, 160))
        frames.append(im)
    out = Image.new("RGBA", (w * 21, h))
    for i, im in enumerate(frames):
        out.paste(im, (i * w, 0))
    return out


def scale(w, h):
    """whom the Court follows: a bar from Roland (left) to Serelle (right), filled from the middle toward the one who
    leads, its marker at Roland's share; 21 frames, Roland's share 0 to 100 by fives"""
    frames = []
    roland, serelle = (217, 181, 101), (196, 124, 84)
    for i in range(21):
        fav = i * 5
        im = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        y0, y1 = (h / 2 - 3) * SS, (h / 2 + 3) * SS
        d.rectangle([0, y0, w * SS - 1, y1], fill=(8, 12, 15, 255), outline=(201, 165, 90, 160), width=SS)
        mid = w * SS / 2
        mx = mid - (w - 12) * SS * (fav - 50) / 100
        if fav != 50:
            col = roland if fav > 50 else serelle
            d.rectangle([min(mid, mx), y0 + SS, max(mid, mx), y1 - SS], fill=(*col, 255))
        d.line([(mid, 1 * SS), (mid, h * SS - SS)], fill=(241, 220, 156, 200), width=SS)
        r = 6 * SS
        cy = h * SS / 2
        d.polygon([(mx, cy - r), (mx + r, cy), (mx, cy + r), (mx - r, cy)], fill=(232, 205, 132, 255),
                  outline=(22, 17, 10, 255), width=int(1.4 * SS))
        frames.append(down(im))
    out = Image.new("RGBA", (w * 21, h))
    for i, im in enumerate(frames):
        out.paste(im, (i * w, 0))
    return out


def mini_triangle():
    """the politics screen's button: a plate with a small triangle of the zones"""
    pl = plate(244, 40, 6, lit=True)
    W, H = 34 * SS, 30 * SS
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    A, B, C = (17 * SS, 2 * SS), (1 * SS, 28 * SS), (33 * SS, 28 * SS)
    def p(sh):
        t = sum(sh)
        return tuple((sh[0] * A[i] + sh[1] * B[i] + sh[2] * C[i]) / t for i in (0, 1))
    for z in ZONES:
        d.polygon([p(s) for s in z["pts"]], fill=zone_colour(z, 160))
    d.line([A, B, C, A], fill=(*HI, 255), width=int(1.2 * SS))
    pl.alpha_composite(down(im), (9, 5))
    return pl


def sgn(v):
    return f"+{v:g}" if v > 0 else f"-{-v:g}"


def zone_effects(z):
    parts = []
    for k, v in z["mods"].items():
        nm, unit = DRIFT_NAMES[k]
        parts.append(f"{nm} {sgn(round(v * 100))} %" if unit == "%" else f"{nm} {sgn(v)} a day")
    if z["ra"]:
        parts.append(f"Royal Authority {sgn(z['ra'])} a month")
    for att, d in z["loyalty"]:
        parts.append(f"the Southmarchers' loyalty {sgn(d)}" if att == "south" else f"{att} estates' loyalty {sgn(d)}")
    if z.get("more"):
        parts.append(z["more"])
    if not parts:
        return "No effects"
    s = "; ".join(parts)
    return s[0].upper() + s[1:]


def three_estates(write):
    """the politics screen's button, the window, their scripts and text"""
    tri = save("es_triangle", triangle_picture())
    zone_sprites = []
    for z in ZONES:
        img, off = zone_highlight(z)
        zone_sprites.append((save(f"es_zone_{z['key']}", img), off))
    syms = {k: save(f"es_symbol_{k}", shadowed(symbol_img(k, SYM))) for k, *_ in ESTATES}
    grounds = {k: save(f"es_ground_{k}", ground(k, 38, 48)) for k, *_ in ESTATES}
    mark = save("es_marker", marker())
    dots = save("es_dot", dot())
    frame = save("es_well", well_frame(40, 50))
    btn = save("es_button", mini_triangle(), effect=BUTTON_FX)
    card = save("es_card", plate(428, 62, 6))
    crown = save("es_crown", plate(428, 66, 6))
    court = save("es_court", plate(428, 100, 6))
    dec = save("es_decision", plate(428, 38, 6), effect=BUTTON_FX)
    dec2 = save("es_decision_half", plate(211, 38, 6), effect=BUTTON_FX)
    head = save("es_band", plate(540, 34, 7, lit=True))
    reform = save("es_reform", plate(540, 56, 6))
    open_btn = save("es_open", plate(300, 34, 6, gold=True), effect=BUTTON_FX)
    strips = {k: save(f"es_strip_{k}", strip(c)) for k, _t, _s, c in ESTATES}
    lean_sw = {k: save(f"es_swatch_{k}", swatch(c)) for k, c in
               [(k, c) for k, _t, _s, c in ESTATES] + [("crown", (241, 220, 156))]}
    # 21 frames of 380 px: a strip under 8192 px, the widest picture every graphics card loads
    ra_bar = save("es_ra_bar", gauge(380, 8, (241, 220, 156), (156, 122, 54), [lo for lo, _ in RA_BANDS[1:]]), frames=21)
    court_bar = save("es_court_bar", scale(304, 16), frames=21)
    # where the button sits: under the popularities, the game's balance of power place on the Deco UI's politics screen
    # (deco_ui/tools/layout_politics.BOP: panel x 18, y 474); on the game's own screen, under its leader (a guess)
    bx, by = (18, 474) if DECO_UI else (300, 300)
    WX, WY, WW, WH = 556, 96, 1010, 900                       # the mockup's window
    TX, TY = 30, 120                                         # the triangle's picture in the window
    LX, LW, RX, RW = 20, 540, 562, 428                       # the columns
    L("ROU_ES_BUTTON_TITLE", "The Three Estates")
    L("ROU_ES_BUTTON_ZONE", "[GetRouEsZone]")
    L("ROU_ES_BUTTON_TT", "The First Estate §Y[?rou_first|0]§!, the Second §Y[?rou_second|0]§!, the Third "
      "§Y[?rou_third|0]§!: [GetRouEsZone]. Royal Authority §Y[?rou_es_ra|0]§!. Click to open or close the three estates.")
    button_gui = window("rou_es_button_window", bx, by, 244, 40, [
        button("rou_es_open_button", btn, 0, 0, tooltip="ROU_ES_BUTTON_TT"),
        text("rou_es_button_title", 52, 6, 186, 14, "ROU_ES_BUTTON_TITLE", "label"),
        text("rou_es_button_zone", 52, 20, 186, 16, "ROU_ES_BUTTON_ZONE", "small")])
    kids = [
        text("rou_es_title", 0, 14, WW, 30, L("ROU_ES_TITLE", "The Three Estates"), "title", fmt="center"),
        button("rou_es_close", "GFX_closebutton", WW - 46, 10),
        text("rou_es_sub", LX, 62, 230, 20, L("ROU_ES_SUB", "The Crown above the estates."), "italic"),
        icon("rou_es_triangle", tri, TX, TY)]
    for z, (spr, (ox, oy)) in zip(ZONES, zone_sprites):
        kids.append(icon(f"rou_es_zone_{z['key']}", spr, TX + ox, TY + oy, transparent=True))
    # each estate's symbol in its corner (the author, 2026-10-23: "Let's go with the symbols inside the triangle"), its
    # name, zone and share outside it
    for k, title, _short, _c in ESTATES:
        cx, cy = corner_centre([z["key"] for z in ZONES].index(k))
        img_w = SYM + 8
        kids.append(icon(f"rou_es_symbol_{k}", syms[k], TX + cx - img_w / 2, TY + cy - img_w / 2, transparent=True))
    spots = {"first": (TX + TRI_A[0] - 120, TY + TRI_A[1] - 76, "center"),
             "second": (TX + TRI_B[0] - 10, TY + TRI_B[1] + 34, "left"),
             "third": (TX + TRI_C[0] + 10 - 240, TY + TRI_C[1] + 34, "right")}
    for (k, title, _short, _c), z in zip(ESTATES, ZONES):
        x, y, al = spots[k]
        kids += [text(f"rou_es_{k}_label", x, y, 240, 14, L(f"ROU_ES_{k.upper()}_LABEL", title), "label", fmt=al),
                 text(f"rou_es_{k}_zone", x, y + 13, 240, 16, L(f"ROU_ES_{k.upper()}_ZONE", z["name"]), "italic_13", fmt=al),
                 text(f"rou_es_{k}_share", x, y + 29, 240, 30, L(f"ROU_ES_{k.upper()}_SHARE", f"[?rou_{k}|0]"), "big", fmt=al)]
    for i in range(1, 7):
        kids.append(icon(f"rou_es_trail_{i}", dots, TX, TY, transparent=True))
    kids.append(icon("rou_es_marker", mark, TX, TY, transparent=True))
    # where the balance stands
    ZY = 618
    kids += [text("rou_es_where", LX, ZY, LW, 14, L("ROU_ES_WHERE", "Where the balance stands"), "label"),
             icon("rou_es_zone_band", head, LX, ZY + 16),
             text("rou_es_zone_name", LX, ZY + 24, LW, 22, "ROU_ES_BUTTON_ZONE", "head", fmt="center"),
             text("rou_es_zone_desc", LX, ZY + 56, LW, 20, L("ROU_ES_ZONE_DESC", "[GetRouEsZoneDesc]"), "italic", fmt="center"),
             text("rou_es_zone_where", LX, ZY + 78, LW, 14, L("ROU_ES_ZONE_WHERE", "[GetRouEsZoneWhere]"), "label", fmt="center"),
             text("rou_es_zone_effects", LX, ZY + 98, LW, 36, L("ROU_ES_ZONE_EFFECTS", "[GetRouEsZoneEffects]"), "small",
                  fmt="center"),
             text("rou_es_leads_label", LX, ZY + 140, 118, 14, L("ROU_ES_LEADS", "Where it leads"), "label"),
             text("rou_es_leads", LX + 122, ZY + 137, LW - 122, 36, L("ROU_ES_ZONE_LEADS", "[GetRouEsZoneLeads]"), "italic_13")]
    # the Promised Reforms (a mission: the Promise Reform decision starts it), or the commons risen, or a note
    MY = 794
    kids += [text("rou_es_reform_label", LX, MY, LW, 14, L("ROU_ES_REFORM_LABEL", "§YThe Promised Reforms§!"), "label"),
             icon("rou_es_reform_band", reform, LX, MY + 16),
             text("rou_es_reform_days", LX + 12, MY + 22, LW - 24, 20,
                  L("ROU_ES_REFORM_DAYS", "About [?rou_es_reform_days|0] days left to carry out the reforms"), "body"),
             text("rou_es_reform_note", LX + 12, MY + 42, LW - 24, 18,
                  L("ROU_ES_REFORM_NOTE", "Not carried out in time, the commons rise. (The mission is in the decisions.)"),
                  "italic_13"),
             text("rou_es_risen", LX, MY + 16, LW, 56,
                  L("ROU_ES_RISEN", "§RThe commons have risen.§! Reform was promised and never made: the secret communist "
                    "path is open. (A placeholder: the path is still to come.)"), "italic", fmt="center"),
             text("rou_es_footer", LX, MY + 40, LW, 56,
                  L("ROU_ES_FOOTER", "An estate of 60 or more takes Rouental down its path; one under 15 is shut out. Royal "
                    "Authority grows only while the balance holds, and falls while an estate dominates."), "italic_13",
                  fmt="center")]
    # the right column: the estates
    kids.append(text("rou_es_estates_label", RX, 62, RW, 14, L("ROU_ES_ESTATES", "The estates"), "label"))
    for i, ((k, title, short, _c), (name, role, line)) in enumerate(zip(ESTATES, HOLDERS)):
        y = 80 + i * 66
        kids += [icon(f"rou_es_{k}_card", card, RX, y), icon(f"rou_es_{k}_strip", strips[k], RX, y),
                 icon(f"rou_es_{k}_ground", grounds[k], RX + 11, y + 7), icon(f"rou_es_{k}_well", frame, RX + 10, y + 6, transparent=True),
                 text(f"rou_es_{k}_role", RX + 60, y + 7, 280, 14, L(f"ROU_ES_{k.upper()}_ROLE", role), "label"),
                 text(f"rou_es_{k}_name", RX + 60, y + 19, 280, 22, L(f"ROU_ES_{k.upper()}_NAME", name), "head"),
                 text(f"rou_es_{k}_line", RX + 60, y + 41, 252, 18, L(f"ROU_ES_{k.upper()}_LINE_T", f"[GetRouEs{short}Line]"),
                      "italic_13"),
                 text(f"rou_es_{k}_share_r", RX + RW - 80, y + 7, 70, 30, f"ROU_ES_{k.upper()}_SHARE", "big", fmt="right"),
                 text(f"rou_es_{k}_since", RX + RW - 110, y + 42, 100, 16,
                      L(f"ROU_ES_{k.upper()}_SINCE", f"[?rou_es_d_{k}|+0] since January"), "small", fmt="right")]
        L(f"ROU_ES_{k.upper()}_LINE", line)
    # the Crown: Royal Authority and whom the Court follows
    CY = 282
    kids += [text("rou_es_crown_label", RX, CY, RW, 14, L("ROU_ES_CROWN", "The Crown"), "label"),
             icon("rou_es_crown_band", crown, RX, CY + 18),
             text("rou_es_ra_label", RX + 12, CY + 26, 240, 14, L("ROU_ES_RA_LABEL", "Royal Authority"), "label"),
             text("rou_es_ra_band", RX + 12, CY + 38, 260, 20, L("ROU_ES_RA_BAND", "[GetRouEsRaBand]"), "head"),
             text("rou_es_ra", RX + RW - 82, CY + 24, 70, 30, L("ROU_ES_RA", "[?rou_es_ra|0]"), "big", fmt="right"),
             text("rou_es_ra_change", RX + RW - 262, CY + 58, 250, 14, L("ROU_ES_RA_CHANGE", "[GetRouEsRaChange]"), "small",
                  fmt="right"),
             icon("rou_es_ra_bar", ra_bar, RX + 24, CY + 74),
             icon("rou_es_court_band", court, RX, CY + 90),
             text("rou_es_court_label", RX, CY + 98, RW, 14, L("ROU_ES_COURT", "Whom the Court follows"), "label", fmt="center"),
             icon("rou_es_roland", "GFX_portrait_ROU_roland_cahun", RX + 11, CY + 113, scale=0.244),
             icon("rou_es_roland_well", frame, RX + 10, CY + 112, transparent=True),
             icon("rou_es_serelle", "GFX_portrait_ROU_serelle_cahun", RX + RW - 49, CY + 113, scale=0.244),
             icon("rou_es_serelle_well", frame, RX + RW - 50, CY + 112, transparent=True),
             icon("rou_es_court_bar", court_bar, RX + 62, CY + 120),
             text("rou_es_court_roland", RX + 62, CY + 138, 150, 16, L("ROU_ES_COURT_ROLAND", "Roland [?rou_es_favour|0]"),
                  "small"),
             text("rou_es_court_serelle", RX + RW - 62 - 150, CY + 138, 150, 16,
                  L("ROU_ES_COURT_SERELLE", "Serelle [?rou_es_serelle|0]"), "small", fmt="right"),
             text("rou_es_court_text", RX + 58, CY + 154, RW - 116, 34, L("ROU_ES_COURT_TEXT", "[GetRouEsCourt]"), "small",
                  fmt="center")]
    # the decisions
    DY = 486
    kids.append(text("rou_es_decisions_label", RX, DY, RW, 14, L("ROU_ES_DECISIONS", "Decisions"), "label"))
    y = DY + 18
    for i, (name, kind, cost, sh, fav) in enumerate(DECISIONS, start=1):
        k = f"ROU_ES_DEC_{i}"
        x, w, spr = RX, RW, dec
        if i > PAIRED:
            w, spr = 211, dec2
            x = RX + (i - PAIRED - 1) % 2 * (w + 6)
        L(k, name)
        if sh == "divide":
            chips = "The strongest estate -6, the other two +3"
        elif sh:
            chips = "  ·  ".join(f"{s} {sgn(v)}" for (_k, _t, s, _c), v in sorted(zip(ESTATES, sh), key=lambda e: -e[1]))
        else:
            chips = f"{'Roland' if fav > 0 else 'Serelle'} +{abs(fav)}"
        L(k + "_CHIPS", chips)
        price = f"{cost} PP" if kind == "pp" else f"{cost} RA"
        L(k + "_COST", price)
        what = {"pp": "Political power", "ra": "Royal Authority"}[kind]
        more = {3: f"\\nThe Promised Reforms begin: {REFORM_DAYS} days to carry them out, or the commons rise."}.get(i, "")
        L(k + "_TT", f"§Y{name}§!\\n{what}: -{cost}\\n{chips.replace('  ·  ', ', ')}.{more}\\nOnce in 30 days.")
        kids += [button(f"rou_es_dec_{i}", spr, x, y, tooltip=k + "_TT"),
                 text(f"rou_es_dec_{i}_name", x + 12, y + 5, w - 84, 16, k, "body" if i <= PAIRED else "small"),
                 text(f"rou_es_dec_{i}_chips", x + 12, y + 22, w - 84, 14, k + "_CHIPS", "label"),
                 text(f"rou_es_dec_{i}_cost", x + w - 70, y + 11, 58, 16, k + "_COST", "value", fmt="center")]
        if i <= PAIRED or (i - PAIRED) % 2 == 0 or i == len(DECISIONS):
            y += 41
    # the estates' leanings, or (in the Lords' Realm) what would break away
    LY = 714
    kids.append(text("rou_es_lean_label", RX, LY, RW, 14,
                     L("ROU_ES_LEANINGS", "The estates' leanings (their loyalty since 1 January)"), "label"))
    for i, (att, key, to) in enumerate(LEANINGS):
        y = LY + 20 + i * 34
        kids += [icon(f"rou_es_lean_{key}_swatch", lean_sw[key], RX + 2, y + 3),
                 # 336 px: "Mercantile estates lean to the Third Estate" was cut at 300 (in game, 2026-10-23)
                 text(f"rou_es_lean_{key}", RX + 22, y + 1, 336, 20, L(f"ROU_ES_LEAN_{key.upper()}", f"{att} estates lean to {to}"),
                      "body"),
                 text(f"rou_es_lean_{key}_v", RX + RW - 70, y + 2, 70, 18,
                      L(f"ROU_ES_LEAN_{key.upper()}_V", f"loyalty [?rou_lean_{key}|+0]"), "small", fmt="right")]
    kids += [text("rou_es_break_label", RX, LY, RW, 14,
                  L("ROU_ES_BREAK_LABEL", f"What would break away (loyalty under {BREAK_BELOW})"), "label"),
             text("rou_es_break_text", RX, LY + 22, RW, 84,
                  L("ROU_ES_BREAK_TEXT", f"§Y[?rou_es_breaking|0]§! of the 26 généralités are under {BREAK_BELOW} and would "
                    "go their own way as the Crown's vassal states; Tara Blanchart governs what stays, and each lost "
                    "généralité could be won back by decision. (A placeholder: the breaking itself is still to come.) The "
                    "Restive and Defiant on the Map of the Realm are those under the line."), "italic_13"),
             button("rou_es_break_map", open_btn, RX + 64, LY + 112, L("ROU_ES_OPEN_MAP", "§KOpen the Map of the Realm§!" if DECO_UI
                                                                       else "Open the Map of the Realm"), F["button"])]
    win_gui = window("rou_es_window", WX, WY, WW, WH, kids, bg="GFX_tiled_window_2b_border")

    # ---- the scripts
    keys = [k for k, *_ in ESTATES]
    coef = lambda v: f"{v / 100:.4f}"  # noqa: E731
    # the marker's place in the window: the properties below set its x and y there, not in the triangle (in game,
    # 2026-10-22: without the triangle's own place in the window the three powers' marker stood off by it)
    pos = []
    for axis, i, off in (("x", 0, TX), ("y", 1, TY)):
        pos += [f"set_variable = {{ rou_es_m{axis} = rou_first }}", f"multiply_variable = {{ rou_es_m{axis} = {coef(TRI_A[i])} }}",
                "set_temp_variable = { es_t = rou_second }", f"multiply_temp_variable = {{ es_t = {coef(TRI_B[i])} }}",
                f"add_to_variable = {{ rou_es_m{axis} = es_t }}", "set_temp_variable = { es_t = rou_third }",
                f"multiply_temp_variable = {{ es_t = {coef(TRI_C[i])} }}", f"add_to_variable = {{ rou_es_m{axis} = es_t }}",
                f"add_to_variable = {{ rou_es_m{axis} = {off - MARK // 2} }}"]
    zone_if = []
    order = [("rou_first > 59.99", 1), ("rou_second > 59.99", 2), ("rou_third > 59.99", 3), ("rou_third < 15", 4),
             ("rou_second < 15", 5), ("rou_first < 15", 6)]
    for i, (cond, n) in enumerate(order):
        zone_if.append(f"{'if' if i == 0 else 'else_if'} = {{ limit = {{ check_variable = {{ {cond} }} }} "
                       f"set_variable = {{ rou_es_zone = {n} }} }}")
    zone_if.append("else = { set_variable = { rou_es_zone = 7 } }")
    spirits = ["if = { limit = { NOT = { check_variable = { rou_es_zone = rou_es_zone_shown } } }"]
    with_mods = [(n, z) for n, z in enumerate(ZONES, start=1) if z["mods"]]
    for n, z in with_mods:
        spirits.append(f"\tif = {{ limit = {{ has_idea = ROU_estates_{z['key']} }} remove_ideas = ROU_estates_{z['key']} }}")
    for n, z in with_mods:
        spirits.append(f"\tif = {{ limit = {{ check_variable = {{ rou_es_zone = {n} }} }} add_ideas = ROU_estates_{z['key']} }}")
    spirits += ["\tset_variable = { rou_es_zone_shown = rou_es_zone }", "}"]
    since = [ln for k, v in zip(keys, START) for ln in (f"set_variable = {{ rou_es_d_{k} = rou_{k} }}",
                                                         f"subtract_from_variable = {{ rou_es_d_{k} = {v} }}")]
    frames = ["set_variable = { rou_es_ra_frame = rou_es_ra }", "divide_variable = { rou_es_ra_frame = 5 }",
              "round_variable = rou_es_ra_frame", "add_to_variable = { rou_es_ra_frame = 1 }",
              "clamp_variable = { var = rou_es_ra_frame min = 1 max = 21 }"]
    # the Court: Roland's lead (his share over 50) or Serelle's, as a part of 50, scales each side's bonuses
    court = ["clamp_variable = { var = rou_es_favour min = 0 max = 100 }",
             "set_variable = { rou_es_serelle = 100 }", "subtract_from_variable = { rou_es_serelle = rou_es_favour }",
             "set_variable = { rou_es_court_frame = rou_es_favour }", "divide_variable = { rou_es_court_frame = 5 }",
             "round_variable = rou_es_court_frame", "add_to_variable = { rou_es_court_frame = 1 }",
             "clamp_variable = { var = rou_es_court_frame min = 1 max = 21 }",
             "set_temp_variable = { es_kr = rou_es_favour }", "subtract_from_temp_variable = { es_kr = 50 }",
             "divide_temp_variable = { es_kr = 50 }", "set_temp_variable = { es_ks = es_kr }",
             "multiply_temp_variable = { es_ks = -1 }",
             "clamp_temp_variable = { var = es_kr min = 0 max = 1 }", "clamp_temp_variable = { var = es_ks min = 0 max = 1 }"]
    for who, k in (("roland", "es_kr"), ("serelle", "es_ks")):
        for key, _mod, full, _nm in FAVOUR[who]:
            court += [f"set_variable = {{ rou_es_m_{key} = {k} }}", f"multiply_variable = {{ rou_es_m_{key} = {full} }}",
                      f"set_variable = {{ rou_es_p_{key} = rou_es_m_{key} }}", f"multiply_variable = {{ rou_es_p_{key} = 100 }}"]
    court.append("force_update_dynamic_modifier = yes")
    effects = {
        "ROU_es_court": court,
        "ROU_es_update": [*zone_if, *spirits, *pos, *since, *frames, "add_to_variable = { rou_es_dirty = 1 }"],
        # call with the temp variables es_d_first, es_d_second, es_d_third set
        "ROU_es_shift": [
            *[f"add_to_variable = {{ rou_{k} = es_d_{k} }}" for k in keys],
            *[f"clamp_variable = {{ var = rou_{k} min = 0 max = 100 }}" for k in keys],
            "set_temp_variable = { es_total = rou_first }", "add_to_temp_variable = { es_total = rou_second }",
            "add_to_temp_variable = { es_total = rou_third }",
            "if = { limit = { check_variable = { es_total > 0 } }",
            "\tset_temp_variable = { es_k = 100 }", "\tdivide_temp_variable = { es_k = es_total }",
            *[f"\tmultiply_variable = {{ rou_{k} = es_k }}" for k in keys], "}",
            "ROU_es_update = yes",
            # the estates' leanings: half the shift, as loyalty
            *[f"set_temp_variable = {{ es_h_{k} = es_d_{k} }}" for k in keys],
            *[f"multiply_temp_variable = {{ es_h_{k} = 0.5 }}" for k in keys],
            *[f"add_to_variable = {{ rou_lean_{k} = es_h_{k} }}" for k in keys],
            "set_temp_variable = { es_h_crown = 0 }", "ROU_gov_leanings = yes",
            *[f"set_temp_variable = {{ es_{a}_{k} = 0 }}" for k in keys for a in ("d", "h")]],
        # call with the temp variable es_d_ra set: Royal Authority moves, and the Leal estates with it (three tenths)
        "ROU_es_ra_change": [
            "add_to_variable = { rou_es_ra = es_d_ra }", "clamp_variable = { var = rou_es_ra min = 0 max = 100 }",
            "set_temp_variable = { es_h_crown = es_d_ra }", "multiply_temp_variable = { es_h_crown = 0.3 }",
            "add_to_variable = { rou_lean_crown = es_h_crown }",
            *[f"set_temp_variable = {{ es_h_{k} = 0 }}" for k in keys], "ROU_gov_leanings = yes",
            "set_temp_variable = { es_h_crown = 0 }", "set_temp_variable = { es_d_ra = 0 }", "ROU_es_update = yes"],
        "ROU_es_trail": [*[f"set_variable = {{ rou_es_h{a}{i} = rou_es_h{a}{i - 1} }}" for i in range(6, 1, -1) for a in "xy"],
                         "set_variable = { rou_es_hx1 = rou_es_mx }", f"add_to_variable = {{ rou_es_hx1 = {MARK // 2 - DOT // 2} }}",
                         "set_variable = { rou_es_hy1 = rou_es_my }", f"add_to_variable = {{ rou_es_hy1 = {MARK // 2 - DOT // 2} }}"],
        "ROU_es_drift": ["random_list = {", *[
            f"\t10 = {{ set_temp_variable = {{ es_d_first = {a} }} set_temp_variable = {{ es_d_second = {b} }} "
            f"set_temp_variable = {{ es_d_third = {c} }} }}"
            for a, b, c in ((1, -1, 0), (-1, 1, 0), (1, 0, -1), (-1, 0, 1), (0, 1, -1), (0, -1, 1), (2, -1, -1),
                            (-1, 2, -1), (-1, -1, 2))],
            "\t10 = { set_temp_variable = { es_d_first = 0 } set_temp_variable = { es_d_second = 0 } "
            "set_temp_variable = { es_d_third = 0 } }", "}", "ROU_es_shift = yes"],
        # each month: Royal Authority by the zone (it grows only while the balance holds), the battle count again
        "ROU_es_month": [
            *[f"if = {{ limit = {{ check_variable = {{ rou_es_zone = {n} }} }} set_temp_variable = {{ es_d_ra = {z['ra']} }} }}"
              for n, z in enumerate(ZONES, start=1) if z["ra"]],
            "ROU_es_ra_change = yes", "set_variable = { rou_es_battles = 0 }",
            "if = { limit = { has_country_flag = rou_es_reform_promised } subtract_from_variable = { rou_es_reform_days = 30 } "
            "clamp_variable = { var = rou_es_reform_days min = 0 max = 365 } }"],
        "ROU_es_init": [*[f"set_variable = {{ rou_{k} = {v} }}" for k, v in zip(keys, START)],
                        f"set_variable = {{ rou_es_ra = {RA_START} }}", f"set_variable = {{ rou_es_favour = {FAVOUR_START} }}",
                        "set_variable = { rou_es_zone_shown = 0 }", "add_dynamic_modifier = { modifier = ROU_court_favour }",
                        "ROU_es_court = yes", "ROU_es_update = yes",
                        *[f"set_variable = {{ rou_es_h{a}{i} = rou_es_m{a} }}" for i in range(1, 7) for a in "xy"],
                        *[f"add_to_variable = {{ rou_es_h{a}{i} = {MARK // 2 - DOT // 2} }}" for i in range(1, 7) for a in "xy"]],
    }
    divide_body = []
    for i, k in enumerate(keys):
        others = [o for o in keys if o != k]
        cond = " ".join(f"check_variable = {{ rou_{k} > rou_{o} }}" if j == 0 and i > 0 else
                        f"NOT = {{ check_variable = {{ rou_{o} > rou_{k} }} }}" for j, o in enumerate(others))
        divide_body.append(f"{'if' if i == 0 else 'else_if'} = {{ limit = {{ {cond} }} set_temp_variable = {{ es_d_{k} = -6 }} "
                           + " ".join(f"set_temp_variable = {{ es_d_{o} = 3 }}" for o in others) + " }")
    dec_effects, dec_triggers = [], []
    for i, (name, kind, cost, sh, fav) in enumerate(DECISIONS, start=1):
        body = [f"add_political_power = -{cost}"] if kind == "pp" else [f"set_temp_variable = {{ es_d_ra = -{cost} }}",
                                                                         "ROU_es_ra_change = yes"]
        if sh == "divide":
            body += divide_body + ["ROU_es_shift = yes"]
        elif sh:
            body += [f"set_temp_variable = {{ es_d_{k} = {v} }}" for k, v in zip(keys, sh)] + ["ROU_es_shift = yes"]
        if fav:
            body += [f"add_to_variable = {{ rou_es_favour = {fav} }}", "ROU_es_court = yes"]
        if i == 3:
            body += ["set_country_flag = rou_es_reform_promised", f"set_variable = {{ rou_es_reform_days = {REFORM_DAYS} }}"]
        body.append(f"set_country_flag = {{ flag = rou_es_cd_{i} days = 30 }}")
        dec_effects.append(f"\t\t\trou_es_dec_{i}_click = {{\n" + "\n".join("\t\t\t\t" + b for b in body) + "\n\t\t\t}")
        cond = [f"has_political_power > {cost - 0.01}" if kind == "pp" else f"check_variable = {{ rou_es_ra > {cost - 0.01} }}",
                f"NOT = {{ has_country_flag = rou_es_cd_{i} }}"]
        if i == 3:
            cond.append("NOT = { has_country_flag = rou_es_reform_promised }")
        dec_triggers.append(f"\t\t\trou_es_dec_{i}_click_enabled = {{ {' '.join(cond)} }}")
    zone_triggers = [f"\t\t\trou_es_zone_{z['key']}_visible = {{ check_variable = {{ rou_es_zone = {n} }} }}"
                     for n, z in enumerate(ZONES, start=1)]
    lords = "check_variable = { rou_es_zone = 2 }"
    shows = [f"\t\t\trou_es_lean_label_visible = {{ NOT = {{ {lords} }} }}"]
    for _att, key, _to in LEANINGS:
        shows += [f"\t\t\trou_es_lean_{key}{s}_visible = {{ NOT = {{ {lords} }} }}" for s in ("_swatch", "", "_v")]
    shows += [f"\t\t\trou_es_break_{s}_visible = {{ {lords} }}" for s in ("label", "text", "map")]
    promised, risen = "has_country_flag = rou_es_reform_promised", "has_country_flag = rou_es_commons_risen"
    shows += [f"\t\t\trou_es_reform_{s}_visible = {{ {promised} }}" for s in ("label", "band", "days", "note")]
    shows += [f"\t\t\trou_es_risen_visible = {{ {risen} NOT = {{ {promised} }} }}",
              f"\t\t\trou_es_footer_visible = {{ NOT = {{ {promised} }} NOT = {{ {risen} }} }}"]
    props = ["\t\t\trou_es_marker = { x = rou_es_mx y = rou_es_my }",
             "\t\t\trou_es_ra_bar = { frame = rou_es_ra_frame }", "\t\t\trou_es_court_bar = { frame = rou_es_court_frame }"]
    props += [f"\t\t\trou_es_trail_{i} = {{ x = rou_es_hx{i} y = rou_es_hy{i} }}" for i in range(1, 7)]
    sgui = f"""	rou_es_button = {{
		context_type = player_context
		window_name = "rou_es_button_window"
		parent_window_token = politics_tab
		visible = {{ original_tag = ROU }}
		effects = {{
			rou_es_open_button_click = {{
				if = {{ limit = {{ has_country_flag = rou_es_open }} clr_country_flag = rou_es_open }}
				else = {{ set_country_flag = rou_es_open }}
			}}
		}}
		ai_enabled = {{ always = no }}
	}}
	rou_es_window = {{
		context_type = player_context
		window_name = "rou_es_window"
		visible = {{ original_tag = ROU has_country_flag = rou_es_open }}
		effects = {{
			rou_es_close_click = {{ clr_country_flag = rou_es_open }}
			rou_es_break_map_click = {{ clr_country_flag = rou_es_open set_country_flag = rou_gov_open add_to_variable = {{ rou_gov_dirty = 1 }} }}
{chr(10).join(dec_effects)}
		}}
		triggers = {{
{chr(10).join(dec_triggers + zone_triggers + shows)}
		}}
		properties = {{
{chr(10).join(props)}
		}}
		ai_enabled = {{ always = no }}
	}}"""
    # the zones' spirits (placeholders: the mockup's effects; Royal Authority and loyalty are scripted)
    ideas = ["ideas = {", "\tcountry = {"]
    for n, z in with_mods:
        ideas += [f"\t\tROU_estates_{z['key']} = {{", "\t\t\tpicture = generic_central_management",
                  "\t\t\tallowed = { always = no }", "\t\t\tremoval_cost = -1", "\t\t\tmodifier = {",
                  *[f"\t\t\t\t{k} = {v}" for k, v in z["mods"].items()], "\t\t\t}", "\t\t}"]
        L(f"ROU_estates_{z['key']}", z["name"])
        L(f"ROU_estates_{z['key']}_desc", f"{z['desc']} {z['where']}. (The three estates: a placeholder, from the mockup.)")
    ideas += ["\t}", "}", ""]
    write("common/ideas/valsora_rouental_estates.txt", "\n".join(ideas))
    # the Court's bonuses: a dynamic modifier on Rouental, each value a variable ROU_es_court sets
    write("common/dynamic_modifiers/valsora_rouental_court.txt", "\n".join(
        ["ROU_court_favour = {", "\ticon = GFX_idea_generic_political_support", "\tenable = { always = yes }",
         *[f"\t{mod} = rou_es_m_{key}" for who in FAVOUR for key, mod, _f, _n in FAVOUR[who]], "}", ""]))
    L("ROU_court_favour", "Whom the Court Follows")
    # the scripted localisation
    sloc = []
    def defined(name, cases):
        sloc.extend(["defined_text = {", f"\tname = {name}"] +
                    [f"\ttext = {{ trigger = {{ {t} }} localization_key = {k} }}" for t, k in cases] + ["}"])
    for suffix, field in (("", "name"), ("Desc", "desc"), ("Where", "where"), ("Effects", "eff"), ("Leads", "leads")):
        defined(f"GetRouEsZone{suffix}", [(f"check_variable = {{ rou_es_zone = {n} }}", f"ROU_ES_ZONE_{n}_{field.upper()}")
                                          for n in range(1, 8)])
    for n, z in enumerate(ZONES, start=1):
        L(f"ROU_ES_ZONE_{n}_NAME", z["name"])
        L(f"ROU_ES_ZONE_{n}_DESC", z["desc"])
        L(f"ROU_ES_ZONE_{n}_WHERE", z["where"])
        L(f"ROU_ES_ZONE_{n}_EFF", zone_effects(z))
        L(f"ROU_ES_ZONE_{n}_LEADS", z["leads"])
    for (k, _t, short, _c) in ESTATES:
        cases = []
        if k == "third":
            cases.append(("has_country_flag = rou_es_reform_promised", "ROU_ES_LINE_PROMISED"))
        cases += [(f"check_variable = {{ rou_{k} < 15 }}", "ROU_ES_LINE_SHUT"), ("always = yes", f"ROU_ES_{k.upper()}_LINE")]
        defined(f"GetRouEs{short}Line", cases)
    L("ROU_ES_LINE_PROMISED", "§YReform promised: [?rou_es_reform_days|0] days left.§!")
    L("ROU_ES_LINE_SHUT", "§RShut out: their estates grow restive.§!")
    defined("GetRouEsRaBand", [(f"check_variable = {{ rou_es_ra > {lo - .01} }}", f"ROU_ES_RA_BAND_{i}")
                               for i, (lo, _n) in reversed(list(enumerate(RA_BANDS)))])
    for i, (_lo, nm) in enumerate(RA_BANDS):
        L(f"ROU_ES_RA_BAND_{i}", nm)
    defined("GetRouEsRaChange", [(f"check_variable = {{ rou_es_zone = {n} }}", f"ROU_ES_RA_CHANGE_{n}") for n in range(1, 8)])
    for n, z in enumerate(ZONES, start=1):
        why = {1: "the estates in balance", 0: "one estate shut out", -2: "one estate dominant"}[z["ra"]]
        L(f"ROU_ES_RA_CHANGE_{n}", (f"§G+1 a month§!: {why}" if z["ra"] > 0 else f"§R{sgn(z['ra'])} a month§!: {why}")
          if z["ra"] else f"steady: {why}")
    defined("GetRouEsCourt", [("check_variable = { rou_es_favour > 50 }", "ROU_ES_COURT_ROLAND_LEADS"),
                              ("check_variable = { rou_es_favour < 50 }", "ROU_ES_COURT_SERELLE_LEADS"),
                              ("always = yes", "ROU_ES_COURT_EVEN")])
    def bonus(who):
        return ", ".join(f"{nm} [?rou_es_p_{key}|+0]%" for key, _m, _f, nm in FAVOUR[who])
    L("ROU_ES_COURT_ROLAND_LEADS", f"Roland leads: {bonus('roland')}.")
    L("ROU_ES_COURT_SERELLE_LEADS", f"Serelle leads: {bonus('serelle')}.")
    L("ROU_ES_COURT_EVEN", "The Court is divided between them: no bonuses either way.")
    # the Promised Reforms: a mission in a category of its own (only while it runs), and the commons' rising
    write("common/decisions/categories/valsora_rouental_estates.txt", "\n".join([
        "ROU_three_estates = {", "\ticon = GFX_decision_category_generic", "\tallowed = { original_tag = ROU }",
        "\tvisible = { original_tag = ROU }", "\tpriority = 205", "}", ""]))
    write("common/decisions/valsora_rouental_estates.txt", "\n".join([
        "ROU_three_estates = {", "\tROU_promised_reforms = {", "\t\ticon = GFX_decision_generic_political_discourse",
        "\t\tallowed = { original_tag = ROU }", "\t\tactivation = { has_country_flag = rou_es_reform_promised }",
        "\t\tavailable = { has_country_flag = rou_es_reforms_done }", f"\t\tdays_mission_timeout = {REFORM_DAYS}",
        "\t\tfire_only_once = no", "\t\tis_good = no",
        "\t\tcomplete_effect = { clr_country_flag = rou_es_reform_promised clr_country_flag = rou_es_reforms_done "
        "set_variable = { rou_es_reform_days = 0 } }",
        "\t\ttimeout_effect = {", "\t\t\tclr_country_flag = rou_es_reform_promised", "\t\t\tset_country_flag = rou_es_commons_risen",
        "\t\t\tset_variable = { rou_es_reform_days = 0 }", "\t\t\tadd_stability = -0.10",
        "\t\t\tadd_popularity = { ideology = communism popularity = 0.10 }",
        "\t\t\tset_temp_variable = { es_d_first = -5 }", "\t\t\tset_temp_variable = { es_d_second = -5 }",
        "\t\t\tset_temp_variable = { es_d_third = 10 }", "\t\t\tROU_es_shift = yes", "\t\t}",
        "\t\tai_will_do = { base = 0 }", "\t}", "}", ""]))
    L("ROU_three_estates", "The Three Estates")
    L("ROU_three_estates_desc", "The First Estate, the clergy; the Second, the nobility; the Third, the commons. The Crown "
      "stands above them.")
    L("ROU_promised_reforms", "The Promised Reforms")
    L("ROU_promised_reforms_desc", "Reform was promised to the commons. If it is not carried out in time, they rise, and "
      "the secret communist path opens. (A placeholder: the reform focuses that carry it out are still to come.)")
    # a test (Rouental's Test Events category, out with the other tests): the balance to each zone in turn
    presets = [(70, 20, 10), (20, 65, 15), (15, 15, 70), (50, 42, 8), (50, 8, 42), (8, 46, 46), START]
    body = ["add_to_variable = { rou_es_test = 1 }", "if = { limit = { check_variable = { rou_es_test > 7 } } "
            "set_variable = { rou_es_test = 1 } }"]
    for n, sh in enumerate(presets, start=1):
        body.append(f"if = {{ limit = {{ check_variable = {{ rou_es_test = {n} }} }} "
                    + " ".join(f"set_variable = {{ rou_{k} = {v} }}" for k, v in zip(keys, sh)) + " }")
    body += ["ROU_es_update = yes", "ROU_gov_update = yes"]
    write("common/decisions/valsora_rouental_tests.txt", "\n".join(
        ["ROU_test_events = {", "\tROU_test_three_estates = {", "\t\ticon = GFX_decision_generic_political_discourse",
         "\t\tfire_only_once = no", "\t\tcost = 0", "\t\tcomplete_effect = {", *["\t\t\t" + b for b in body], "\t\t}",
         "\t\tai_will_do = { base = 0 }", "\t}",
         "\tROU_test_reforms_done = {", "\t\ticon = GFX_decision_generic_political_discourse",
         "\t\tvisible = { has_country_flag = rou_es_reform_promised }", "\t\tfire_only_once = no", "\t\tcost = 0",
         "\t\tcomplete_effect = { set_country_flag = rou_es_reforms_done }", "\t\tai_will_do = { base = 0 }", "\t}",
         "}", ""]))
    L("ROU_test_three_estates", "Test: the Three Estates to the Next Zone")
    L("ROU_test_three_estates_desc", "Moves the balance into each of the seven zones in turn (the Voix Behind the Curtain, "
      "the Lords' Realm, the Commons Ascendant, Cloister and Castle, Church and Commons, Manor and Market, back to the "
      "start), to see their spirits and the généralités' colours. A test: it goes with the others.")
    L("ROU_test_reforms_done", "Test: the Reforms Carried Out")
    L("ROU_test_reforms_done_desc", "Counts the Promised Reforms as carried out, so their mission ends well (the reform "
      "focuses that will do it are still to come). A test: it goes with the others.")
    return button_gui, win_gui, sgui, effects, sloc


def serelle_battles():
    """every combat Serelle wins moves the Court a point toward her, at most BATTLES_A_MONTH a month (the author,
    2026-10-22: "If we can tie things to Serelle winning battles, that'd be great"); ROOT is the general, FROM her
    country (the game's on_actions)"""
    return ["\ton_army_leader_won_combat = {", "\t\teffect = {", "\t\t\tif = {",
            "\t\t\t\tlimit = { is_character = ROU_serelle_cahun FROM = { original_tag = ROU "
            f"NOT = {{ check_variable = {{ rou_es_battles > {BATTLES_A_MONTH - 0.01} }} }} }} }}",
            "\t\t\t\tFROM = { add_to_variable = { rou_es_battles = 1 } add_to_variable = { rou_es_favour = -1 } ROU_es_court = yes }",
            "\t\t\t}", "\t\t}", "\t}"]


# ================================================================ the governorates
SC = 2.6                                  # map pixels to the window's
U = 13                                    # SC = U / 5: drawn at 13 times, then 5 x 5 averaged
BAND_COLOURS = [(76, 138, 108), (113, 144, 90), (179, 145, 67), (174, 100, 64), (142, 58, 51)]   # Devoted ... Defiant
BAND_NAMES = ["Devoted", "Loyal", "Wary", "Restive", "Defiant"]
LEVY_NAMES = RM.LEVY


def governorate_data():
    R = RM.realm()
    G = RM.governorates()
    P, guessed = RM.peoples()
    names = sorted(G)
    royal = sorted(R["royal"], key=lambda s: R["st"][s]["name"] != "Rêverie")
    govs = []
    for n, g in enumerate(names, start=1):
        d = G[g]
        states = [s for s in d["states"] if s not in R["royal"]]
        static = sum(v for k, v in d["breakdown"] if not k.startswith("Estates"))
        main = max(d["shares"], key=d["shares"].get)
        govs.append(dict(n=n, name=g, states=states, seat=d["seat"], static=static,
                         att=[a for a, _ in RM.ATTITUDES].index(d["attitude"][0]) + 1, governor=d["governor"],
                         origin=d["origin"], shares=d["shares"], main=main, seal=R["seal"][g]))
    return R, G, P, govs, royal


def coverage(mask):
    """a mask of the crop (padded to a multiple of 5 rows) at the window's scale, anti-aliased"""
    H, W = mask.shape
    big = np.repeat(np.repeat(mask, U, 0), U, 1).astype(np.float32)
    return big.reshape(H * U // 5, 5, W * U // 5, 5).mean((1, 3))


def edge_alpha(classes, width):
    """the borders where `classes` (an int array of the crop, at U times) changes, `width` window px wide"""
    e = np.zeros(classes.shape, bool)
    e[:, 1:] |= classes[:, 1:] != classes[:, :-1]
    e[1:, :] |= classes[1:, :] != classes[:-1, :]
    r = max(1, round(width * 5 / 2))
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    e = ndi.binary_dilation(e, structure=(xx * xx + yy * yy) <= r * r)
    H, W = e.shape
    return e.astype(np.float32).reshape(H // 5, 5, W // 5, 5).mean((1, 3))


def rgba_from(alpha, colour, a=1.0):
    out = np.zeros((*alpha.shape, 4), np.uint8)
    out[..., :3] = colour
    out[..., 3] = (np.clip(alpha, 0, 1) * 255 * a).astype(np.uint8)
    return Image.fromarray(out)


def governorates(write):
    R, G, P, govs, royal = governorate_data()
    S = R["S"]
    pad = (-S.shape[0]) % 5
    S = np.pad(S, ((0, pad), (0, 0)))
    st = R["st"]
    gov_of = {s: g["n"] for g in govs for s in g["states"]}
    MW, MH = S.shape[1] * U // 5, S.shape[0] * U // 5
    # ---- the base: the well, the sea, the neighbours' land, Rouental's land outside the governorates
    owner = np.vectorize(lambda s: 0 if s == 0 else (1 if st.get(int(s), {}).get("owner") == "ROU" else 2))(S)
    base = np.zeros((MH, MW, 4), np.float32)
    base[..., :3] = (14, 22, 27)
    base[..., 3] = 255
    for cls, col in ((2, (34, 42, 47)), (1, (52, 60, 64))):
        a = coverage(owner == cls)[..., None]
        base[..., :3] = base[..., :3] * (1 - a) + np.array(col) * a
    well = Image.new("RGBA", (MW + 8, MH + 8), (0, 0, 0, 0))
    wd = ImageDraw.Draw(well)
    wd.polygon(chamfer_poly(0, 0, MW + 7, MH + 7, 6), fill=(*RULE, 200))
    well.paste(Image.fromarray(base.astype(np.uint8)), (4, 4))
    base_spr = save("gov_map", well)
    # ---- each governorate's fill, one picture per loyalty band (only the one matching shows); not clicked: the game
    # takes a button's whole box for it, and the boxes overlap (in game, 2026-10-22: "I can't click on Rivage d'argent
    # anywhere but the badge"), so the clicks are hit_rects() below
    fills, overlays = [], []

    def cut(m):
        """a mask's box in map px, widened to multiples of 5 (so 13 / 5 stays whole), its coverage and its ring"""
        ys, xs = np.nonzero(m)
        cx0, cy0 = xs.min() // 5 * 5, ys.min() // 5 * 5
        cx1, cy1 = -(-(xs.max() + 1) // 5) * 5, -(-(ys.max() + 1) // 5) * 5
        sub = np.pad(m[cy0:cy1, cx0:cx1], 5)                  # a margin, so the ring is whole at the box's edge
        cov = coverage(sub)[13:-13, 13:-13]
        ring = edge_alpha(np.repeat(np.repeat(sub, U, 0), U, 1).astype(np.int32), 3.2)[13:-13, 13:-13] * cov
        return cov, ring, (cx0 * U // 5, cy0 * U // 5)

    for g in govs:
        cov, ring, at_ = cut(np.isin(S, g["states"]))
        sprites = [save(f"gov_{g['n']}_b{b + 1}", rgba_from(cov, c, .9)) for b, c in enumerate(BAND_COLOURS)]
        fills.append((g, sprites, at_))
        # Couronneterre selected lights the crownlands too, which are its in name (the author, 2026-10-23: "include
        # the crownlands in the Couronterre generalite visually when it is selected, but keep it so that clicking on
        # them brings up the Crownlands tab": their clicks and seal stay the Crown's Domain's)
        sel = np.isin(S, g["states"] + (royal if g["name"] == "Couronneterre" else []))
        if g["name"] == "Couronneterre":
            cov, ring, at_ = cut(sel)
        overlays.append((save(f"gov_{g['n']}_sel", rgba_from(np.maximum(ring, cov * .32), HI)), at_))
    cov, ring, crown_at = cut(np.isin(S, royal))
    hatch = ((np.add.outer(np.arange(cov.shape[0]), np.arange(cov.shape[1])) // 3) % 2).astype(np.float32)
    crown = np.zeros((*cov.shape, 4), np.uint8)
    crown[..., :3] = np.where(hatch[..., None] > 0, np.array((201, 165, 90)), np.array((110, 86, 38)))
    crown[..., 3] = (cov * 235).astype(np.uint8)
    crown_spr = save("gov_crown", Image.fromarray(crown))
    crown_sel = save("gov_crown_sel", rgba_from(np.maximum(ring, cov * .32), HI))
    # ---- the borders: states (dark), governorates (gilt), the realm (bright)
    big = np.repeat(np.repeat(S, U, 0), U, 1)
    cls_gov = np.vectorize(lambda s: gov_of.get(int(s), 100 if int(s) in royal else
                                                (200 if st.get(int(s), {}).get("owner") == "ROU" else 0)))(S)
    cls_gov_big = np.repeat(np.repeat(cls_gov, U, 0), U, 1)
    rou = np.repeat(np.repeat(owner == 1, U, 0), U, 1).astype(np.int32)
    land = np.repeat(np.repeat(owner > 0, U, 0), U, 1)
    a_state = edge_alpha(np.where(land, big, -1), .9)
    a_gov = edge_alpha(np.where(rou > 0, cls_gov_big, -1), 1.5) * (coverage(owner == 1) > 0)
    a_realm = edge_alpha(rou, 2.0)
    lines = np.zeros((MH, MW, 4), np.float32)
    for a, col, k in ((a_state, (10, 14, 16), .55), (a_gov, RULE, 1.0), (a_realm, GILT, 1.0)):
        a = np.clip(a * k, 0, 1)[..., None]
        lines[..., :3] = lines[..., :3] * (1 - a) + np.array(col) * a
        lines[..., 3:] = lines[..., 3:] + (255 - lines[..., 3:]) * a
    lines_spr = save("gov_lines", Image.fromarray(lines.clip(0, 255).astype(np.uint8)))
    # ---- seals
    def seal(lit):
        s = 22 * SS
        im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        r, c = 10 * SS, s / 2
        pts = [(c + r * math.cos(math.radians(22.5 + 45 * i)), c + r * math.sin(math.radians(22.5 + 45 * i))) for i in range(8)]
        d.polygon(pts, fill=(*(JADE if lit else (26, 20, 8)), 255), outline=(*(HI if lit else GILT), 255), width=int(1.6 * SS))
        d.polygon([(c, c - 3.5 * SS), (c + 3.5 * SS, c), (c, c + 3.5 * SS), (c - 3.5 * SS, c)], fill=(*HI, 255))
        return down(im)
    seal_spr = save("gov_seal", seal(False), effect=BUTTON_FX)
    seal_lit = save("gov_seal_lit", seal(True))
    legend = Image.new("RGBA", (MW + 8, 26), (0, 0, 0, 0))
    ld = ImageDraw.Draw(legend)
    lf = font("josefin", 12)
    x = 6
    for c, nm in list(zip(BAND_COLOURS, BAND_NAMES)) + [((201, 165, 90), "Royal Fief")]:
        ld.rectangle([x, 8, x + 11, 19], fill=(*c, 255), outline=(*GILT, 200))
        w = tracked(ld, (x + 17, 6), nm.upper(), lf, (*CREAM, 230), .12)
        x += 17 + w + 18
    legend_spr = save("gov_legend", legend)
    # ---- the card's pieces
    band = save("gov_band", plate(430, 38, 7))
    act = save("gov_action", plate(212, 34, 6), effect=BUTTON_FX)
    open_btn = save("gov_open", plate(300, 34, 6, gold=True), effect=BUTTON_FX)
    bar = []
    for i in range(20):                                  # the loyalty bar: a frame each 5 points
        im = Image.new("RGBA", (300, 10), (10, 15, 18, 255))
        d = ImageDraw.Draw(im)
        v = (i + 1) * 5
        col = BAND_COLOURS[0 if v >= 80 else 1 if v >= 60 else 2 if v >= 40 else 3 if v >= 20 else 4]
        d.rectangle([1, 1, round(298 * v / 100), 8], fill=(*col, 255))
        for t in (20, 40, 60, 80):
            d.line([(round(300 * t / 100), 0), (round(300 * t / 100), 9)], fill=(227, 199, 126, 120))
        d.rectangle([0, 0, 299, 9], outline=(*RULE, 160))
        bar.append(im)
    strip = Image.new("RGBA", (300 * 20, 10))
    for i, im in enumerate(bar):
        strip.paste(im, (i * 300, 0))
    bar_spr = save("gov_bar", strip, frames=20)

    # ---- the window
    WX, WY, WW, WH = 566, 104, 1330, 846
    MX, MY = 20, 66
    kids = [text("rou_gov_title", 0, 16, WW, 30, L("ROU_GOV_TITLE", "The Généralités of Rouental"), "title", fmt="center"),
            button("rou_gov_close", "GFX_closebutton", WW - 46, 10),
            icon("rou_gov_map", base_spr, MX, MY)]
    for g, sprites, (x0, y0) in fills:
        for b, spr in enumerate(sprites, start=1):
            kids.append(icon(f"rou_gov_{g['n']}_b{b}", spr, MX + 4 + x0, MY + 4 + y0, transparent=True))
    kids.append(icon("rou_gov_crown_fill", crown_spr, MX + 4 + crown_at[0], MY + 4 + crown_at[1], transparent=True))
    for g, (spr, (x0, y0)) in zip(govs, overlays):
        kids.append(icon(f"rou_gov_{g['n']}_sel", spr, MX + 4 + x0, MY + 4 + y0, transparent=True))
    kids.append(icon("rou_gov_crown_sel", crown_sel, MX + 4 + crown_at[0], MY + 4 + crown_at[1], transparent=True))
    kids.append(icon("rou_gov_lines", lines_spr, MX + 4, MY + 4, transparent=True))
    # the click areas: rectangles that tile each governorate, under the seals
    hits = hit_rects(S, gov_of, royal)
    hit_spr = save_tile("gov_hit", Image.new("RGBA", (8, 8), (0, 0, 0, 1)))   # all but clear, in case the game skips a
    for i, (x, y, w, h, n) in enumerate(hits, start=1):                       # clear pixel
        kids.append(box("buttonType", f"rou_gov_hit_{i}", MX + 4 + x, MY + 4 + y,
                        [f"size = {{ x = {w} y = {h} }}", f"spriteType = {q(hit_spr)}", f"pdx_tooltip = {q(f'ROU_GOV_{n}_TT')}",
                         "clicksound = click_default"]))
    cap = next(s for s in royal if st[s]["name"] == "Rêverie")
    ys, xs = np.nonzero(R["S"] == cap)
    seals = [(g["n"], g["seal"][0], g["seal"][1]) for g in govs] + [(27, xs.mean() + .5, ys.mean() + .5)]
    for n, sx, sy in seals:
        x, y = MX + 4 + sx * SC - 11, MY + 4 + sy * SC - 11
        kids += [button(f"rou_gov_{n}_seal", seal_spr, x, y, tooltip=f"ROU_GOV_{n}_TT"),
                 icon(f"rou_gov_{n}_seal_lit", seal_lit, x, y, transparent=True)]
    kids += [icon("rou_gov_legend", legend_spr, MX, MY + MH + 12),
             text("rou_gov_hint", MX, MY + MH + 46, MW, 60, L("ROU_GOV_HINT", "Click a généralité, or its seal, to see "
                  "it. The colours are the généralités' loyalty to the Crown. A state's levies are known once inspectors "
                  "have seen it; the Crown knows its own fiefs'."), "italic")]
    CX, CW = 880, 430
    kids += [icon("rou_gov_card_band", band, CX, 66),
             text("rou_gov_card_title", CX, 75, CW, 22, L("ROU_GOV_SEL_NAME", "[GetRouGovName]"), "head", fmt="center"),
             text("rou_gov_card_governor", CX, 114, CW, 20, L("ROU_GOV_SEL_GOVERNOR", "[GetRouGovGovernor]"), "body"),
             text("rou_gov_card_origin", CX, 136, CW, 18, L("ROU_GOV_SEL_ORIGIN", "[GetRouGovOrigin]"), "italic"),
             text("rou_gov_card_loyalty_label", CX, 166, CW, 14, L("ROU_GOV_LOYALTY", "Loyalty to the Crown"), "label"),
             icon("rou_gov_card_bar", bar_spr, CX, 188),
             text("rou_gov_card_loyalty", CX + 310, 180, 120, 26, L("ROU_GOV_SEL_LOYALTY", "[GetRouGovLoyalty]"), "body"),
             text("rou_gov_card_estates_label", CX, 216, CW, 14, L("ROU_GOV_ESTATES", "The estates"), "label"),
             text("rou_gov_card_estates", CX, 234, CW, 20, L("ROU_GOV_SEL_ATT", "[GetRouGovAttitude]"), "body"),
             text("rou_gov_card_estates_desc", CX, 254, CW, 42, L("ROU_GOV_SEL_ATT_DESC", "[GetRouGovAttitudeDesc]"),
                  "italic"),
             text("rou_gov_card_peoples_label", CX, 296, CW, 14, L("ROU_GOV_PEOPLES", "Peoples"), "label"),
             # two lines (in game, 2026-10-23: "Cultures list of severed lands runs off screen": the Terres Séparées' six
             # peoples), the states' list 8 px lower under them (ten states at most, 220 px of the grid's 264)
             text("rou_gov_card_peoples", CX, 314, CW, 34, L("ROU_GOV_SEL_PEOPLES", "[GetRouGovPeoples]"), "small"),
             text("rou_gov_card_states_label", CX + 6, 352, 150, 14, L("ROU_GOV_STATES_HEAD", "State"), "label"),
             text("rou_gov_card_people_head", CX + 160, 352, 110, 14, L("ROU_GOV_PEOPLE_HEAD", "People"), "label"),
             text("rou_gov_card_levy_head", CX + 272, 352, 90, 14, L("ROU_GOV_LEVY_HEAD", "Levies"), "label"),
             text("rou_gov_card_men_head", CX + 360, 352, 64, 14, L("ROU_GOV_MEN_HEAD", "Men"), "label", fmt="right"),
             grid("rou_gov_states_grid", CX, 370, CW, 12 * 22, CW, 22, 1, 12)]
    for i, (k, nm) in enumerate((("insp", "Send Inspectors"), ("grant", "Grant Privileges"), ("demand", "Demand Levies"),
                                 ("session", "Summon the Estates"))):
        L(f"ROU_GOV_ACT_{k.upper()}", nm)
        kids.append(button(f"rou_gov_act_{k}", act, CX + (i % 2) * 218, 640 + (i // 2) * 40,
                           f"ROU_GOV_ACT_{k.upper()}", tooltip=f"ROU_GOV_ACT_{k.upper()}_TT"))
    L("ROU_GOV_ACT_INSP_TT", "§YSend Inspectors§!\\nPolitical power: -25\\nEvery state's levies become known.\\n"
      "Proud estates resent it: loyalty -5.")
    L("ROU_GOV_ACT_GRANT_TT", "§YGrant Privileges§!\\nPolitical power: -50\\nLoyalty +10 (Grasping estates +15).")
    L("ROU_GOV_ACT_DEMAND_TT", "§YDemand Levies§!\\nManpower +5000\\nLoyalty -10 (Leal estates -4, Grasping -15).")
    L("ROU_GOV_ACT_SESSION_TT", "§YSummon the Estates§!\\nPolitical power: -20\\nThe estates sit, and their temper may "
      "change.")
    window_gui = window("rou_gov_window", WX, WY, WW, WH, kids, bg="GFX_tiled_window_2b_border")
    entry = window("rou_gov_state_entry", 0, 0, CW, 22, [
        text("rou_gov_state_name", 6, 3, 150, 18, L("ROU_GOV_STATE_NAME", "[This.GetName]"), "small"),
        text("rou_gov_state_people", 160, 3, 110, 18, L("ROU_GOV_STATE_PEOPLE", "[GetRouStatePeople]"), "small"),
        text("rou_gov_state_levy", 272, 3, 96, 18, L("ROU_GOV_STATE_LEVY", "[GetRouStateLevy]"), "small"),
        text("rou_gov_state_men", 360, 3, 64, 18, L("ROU_GOV_STATE_MEN", "[?rou_manpower_k|0]k"), "small", fmt="right")])
    category = window("rou_gov_category_window", 0, 0, 520, 96, [
        text("rou_gov_cat_text", 10, 6, 500, 40, L("ROU_GOV_CAT_TEXT", "The Prince's governors keep what order they can "
             "among the vassals of 26 généralités; the eleven Royal Fiefs answer to the Crown."), "italic"),
        # dark ink on the gold plate (the Deco fonts' K, as the politics screen's Head of State ribbon): the fonts' cream
        # was barely readable on it (the author, 2026-10-22)
        button("rou_gov_open_button", open_btn, 110, 52, L("ROU_GOV_OPEN", "§KOpen the Map of the Realm§!" if DECO_UI
                                                           else "Open the Map of the Realm"), F["button"])])

    # ---- the scripts
    n_all = [g["n"] for g in govs]
    att_names = [a for a, _ in RM.ATTITUDES]
    # the estates' zones: the estates of an attitude gain or lose loyalty while one holds (ZONES' loyalty)
    zone_mod = {n: [(a, d) for a, d in z["loyalty"] if a != "south"] for n, z in enumerate(ZONES, start=1)}
    south_mod = [(n, d) for n, z in enumerate(ZONES, start=1) for a, d in z["loyalty"] if a == "south"]
    south = [g["n"] for g in govs if g["main"] == "Southmarch"]
    upd = []
    for g in govs:
        n = g["n"]
        v = f"rou_gov_{n}"
        upd += [f"set_variable = {{ {v}_loyalty = {g['static']} }}", f"add_to_variable = {{ {v}_loyalty = {v}_favour }}"]
        upd += [f"if = {{ limit = {{ check_variable = {{ {v}_att = {i} }} }} add_to_variable = {{ {v}_loyalty = {RM.ATTITUDE_MOD[a]} }} }}"
                for i, a in enumerate(att_names, start=1) if RM.ATTITUDE_MOD[a]]
        for z, spec in zone_mod.items():
            for att, d in spec:
                i = att_names.index(att) + 1
                upd.append(f"if = {{ limit = {{ check_variable = {{ rou_es_zone = {z} }} check_variable = {{ {v}_att = {i} }} }} "
                           f"add_to_variable = {{ {v}_loyalty = {d} }} }}")
        if n in south:
            upd += [f"if = {{ limit = {{ check_variable = {{ rou_es_zone = {z} }} }} add_to_variable = {{ {v}_loyalty = {d} }} }}"
                    for z, d in south_mod]
        upd += [f"clamp_variable = {{ var = {v}_loyalty min = 2 max = 97 }}",
                f"set_variable = {{ {v}_band = 5 }}",
                *[f"if = {{ limit = {{ check_variable = {{ {v}_loyalty > {t - .01} }} }} set_variable = {{ {v}_band = {b} }} }}"
                  for b, t in ((4, 20), (3, 40), (2, 60), (1, 80))],
                f"set_variable = {{ {v}_mp = {v}_loyalty }}", f"subtract_from_variable = {{ {v}_mp = 50 }}",
                f"divide_variable = {{ {v}_mp = 200 }}",
                *[f"{s} = {{ set_variable = {{ rou_mp_mod = ROU.{v}_mp }} }}" for s in g["states"]]]
    sel_copy = []
    for g in govs:
        v = f"rou_gov_{g['n']}"
        sel_copy.append(f"if = {{ limit = {{ check_variable = {{ rou_gov_sel = {g['n']} }} }} set_variable = {{ rou_gov_sel_loyalty = {v}_loyalty }} "
                        f"set_variable = {{ rou_gov_sel_att = {v}_att }} }}")
    # the Lords' Realm: how many would break away (loyalty under BREAK_BELOW)
    upd += ["set_variable = { rou_es_breaking = 0 }"] + [
        f"if = {{ limit = {{ check_variable = {{ rou_gov_{g['n']}_loyalty < {BREAK_BELOW} }} }} add_to_variable = {{ rou_es_breaking = 1 }} }}"
        for g in govs]
    upd += sel_copy + ["set_variable = { rou_gov_sel_bar = rou_gov_sel_loyalty }", "divide_variable = { rou_gov_sel_bar = 5 }",
                       "round_variable = rou_gov_sel_bar", "clamp_variable = { var = rou_gov_sel_bar min = 1 max = 20 }",
                       "add_to_variable = { rou_gov_dirty = 1 }"]
    def per_sel(body_for):
        out = []
        for g in govs:
            out.append(f"if = {{ limit = {{ check_variable = {{ rou_gov_sel = {g['n']} }} }}")
            out += ["\t" + b for b in body_for(g)]
            out.append("}")
        return out
    def att_is(g, a):
        return f"check_variable = {{ rou_gov_{g['n']}_att = {att_names.index(a) + 1} }}"
    def roll(v):
        return ["random_list = {", *[f"\t10 = {{ set_variable = {{ {v} = {i} }} }}" for i in range(1, 9)], "}"]
    effects = {
        "ROU_gov_update": upd,
        "ROU_gov_leanings": [f"if = {{ limit = {{ {att_is(g, att)} }} add_to_variable = {{ rou_gov_{g['n']}_favour = es_h_{key} }} }}"
                             for g in govs for att, key, _to in LEANINGS]
        + [ln for n in south for ln in (
            f"if = {{ limit = {{ check_variable = {{ es_d_first > 0 }} }} set_temp_variable = {{ es_s = es_d_first }} "
            f"multiply_temp_variable = {{ es_s = -0.2 }} add_to_variable = {{ rou_gov_{n}_favour = es_s }} }}",)]
        + ["ROU_gov_update = yes"],
        "ROU_gov_select": ["clear_array = rou_sel_states"]
        + [ln for g in govs for ln in (
            f"if = {{ limit = {{ check_variable = {{ rou_gov_sel = {g['n']} }} }}",
            *[f"\t{s} = {{ ROU = {{ add_to_array = {{ rou_sel_states = PREV }} }} }}" for s in g["states"]], "}")]
        + ["if = { limit = { check_variable = { rou_gov_sel = 27 } }",
           *[f"\t{s} = {{ ROU = {{ add_to_array = {{ rou_sel_states = PREV }} }} }}" for s in royal], "}",
           "ROU_gov_update = yes"],
        "ROU_gov_act_insp": ["add_political_power = -25"] + per_sel(lambda g: [
            *[f"{s} = {{ set_state_flag = rou_inspected }}" for s in g["states"]],
            f"if = {{ limit = {{ {att_is(g, 'Proud')} }} add_to_variable = {{ rou_gov_{g['n']}_favour = -5 }} }}"])
        + ["ROU_gov_update = yes"],
        "ROU_gov_act_grant": ["add_political_power = -50"] + per_sel(lambda g: [
            f"add_to_variable = {{ rou_gov_{g['n']}_favour = 10 }}",
            f"if = {{ limit = {{ {att_is(g, 'Grasping')} }} add_to_variable = {{ rou_gov_{g['n']}_favour = 5 }} }}"])
        + ["ROU_gov_update = yes"],
        "ROU_gov_act_demand": ["add_manpower = 5000"] + per_sel(lambda g: [
            f"if = {{ limit = {{ {att_is(g, 'Leal')} }} add_to_variable = {{ rou_gov_{g['n']}_favour = -4 }} }}",
            f"else_if = {{ limit = {{ {att_is(g, 'Grasping')} }} add_to_variable = {{ rou_gov_{g['n']}_favour = -15 }} }}",
            f"else = {{ add_to_variable = {{ rou_gov_{g['n']}_favour = -10 }} }}",
            f"if = {{ limit = {{ check_variable = {{ rou_es_zone = 5 }} }}",
            f"\tif = {{ limit = {{ {att_is(g, 'Leal')} }} add_to_variable = {{ rou_gov_{g['n']}_favour = -2 }} }}",
            f"\telse_if = {{ limit = {{ {att_is(g, 'Grasping')} }} add_to_variable = {{ rou_gov_{g['n']}_favour = -8 }} }}",
            f"\telse = {{ add_to_variable = {{ rou_gov_{g['n']}_favour = -5 }} }}", "}"])
        + ["ROU_gov_update = yes"],
        "ROU_gov_act_session": ["add_political_power = -20"] + per_sel(lambda g: roll(f"rou_gov_{g['n']}_att"))
        + ["ROU_gov_update = yes"],
    }
    init = []
    for g in govs:
        init += [f"set_variable = {{ rou_gov_{g['n']}_att = {g['att']} }}", f"set_variable = {{ rou_gov_{g['n']}_favour = 0 }}"]
    people_keys = list(RM.PEOPLES)
    for s in sorted(set(gov_of) | set(royal)):
        p = P.get(s, RM.ROYAL_PEOPLE)
        lv = RM.levy(s)
        flags = ["set_state_flag = rou_inspected"] if s in royal else []
        if st[s]["name"] in RM.CEREMONIAL:
            flags.append("set_state_flag = rou_ceremonial")
        mods = [] if s in royal else ["add_dynamic_modifier = { modifier = ROU_governorate_loyalty }"]
        init.append(f"{s} = {{ set_variable = {{ rou_people = {people_keys.index(p) + 1} }} set_variable = {{ rou_levy = {lv} }} "
                    f"set_variable = {{ rou_manpower_k = {round(st[s]['manpower'] / 1000)} }} {' '.join(flags + mods)} }}")
    init += ["set_variable = { rou_gov_sel = 0 }", "ROU_gov_update = yes"]
    effects["ROU_gov_init"] = init
    # the GUIs
    sel_trig = [f"\t\t\trou_gov_{g['n']}_b{b}_visible = {{ check_variable = {{ rou_gov_{g['n']}_band = {b} }} }}"
                for g in govs for b in range(1, 6)]
    sel_trig += [f"\t\t\trou_gov_{n}_sel_visible = {{ check_variable = {{ rou_gov_sel = {n} }} }}" for n in n_all]
    sel_trig += [f"\t\t\trou_gov_{n}_seal_lit_visible = {{ check_variable = {{ rou_gov_sel = {n} }} }}" for n in n_all + [27]]
    sel_trig += ["\t\t\trou_gov_crown_sel_visible = { check_variable = { rou_gov_sel = 27 } }",
                 "\t\t\trou_gov_card_bar_visible = { check_variable = { rou_gov_sel > 0 } check_variable = { rou_gov_sel < 27 } }"]
    card_ok = "check_variable = { rou_gov_sel > 0 } check_variable = { rou_gov_sel < 27 }"
    sel_trig += [f"\t\t\trou_gov_act_insp_click_enabled = {{ {card_ok} has_political_power > 24.99 NOT = {{ has_country_flag = rou_gov_act_cd }} }}",
                 f"\t\t\trou_gov_act_grant_click_enabled = {{ {card_ok} has_political_power > 49.99 NOT = {{ has_country_flag = rou_gov_act_cd }} }}",
                 f"\t\t\trou_gov_act_demand_click_enabled = {{ {card_ok} NOT = {{ has_country_flag = rou_gov_act_cd }} }}",
                 f"\t\t\trou_gov_act_session_click_enabled = {{ {card_ok} has_political_power > 19.99 NOT = {{ has_country_flag = rou_gov_act_cd }} }}"]
    clicks = []
    pick = lambda n: f"set_variable = {{ rou_gov_sel = {n} }} ROU_gov_select = yes"  # noqa: E731
    clicks += [f"\t\t\trou_gov_{n}_seal_click = {{ {pick(n)} }}" for n in n_all + [27]]
    clicks += [f"\t\t\trou_gov_hit_{i}_click = {{ {pick(n)} }}" for i, (_x, _y, _w, _h, n) in enumerate(hits, start=1)]
    clicks += [
               "\t\t\trou_gov_close_click = { clr_country_flag = rou_gov_open add_to_variable = { rou_gov_dirty = 1 } }"]
    clicks += [f"\t\t\trou_gov_act_{k}_click = {{ ROU_gov_act_{k} = yes set_country_flag = {{ flag = rou_gov_act_cd days = 1 }} }}"
               for k in ("insp", "grant", "demand", "session")]
    sgui = f"""	rou_gov_category = {{
		context_type = decision_category
		window_name = "rou_gov_category_window"
		effects = {{
			rou_gov_open_button_click = {{ set_country_flag = rou_gov_open add_to_variable = {{ rou_gov_dirty = 1 }} }}
		}}
		ai_enabled = {{ always = no }}
	}}
	rou_gov_window = {{
		context_type = player_context
		window_name = "rou_gov_window"
		visible = {{ original_tag = ROU has_country_flag = rou_gov_open }}
		effects = {{
{chr(10).join(clicks)}
		}}
		triggers = {{
{chr(10).join(sel_trig)}
		}}
		properties = {{
			rou_gov_card_bar = {{ frame = rou_gov_sel_bar }}
		}}
		dynamic_lists = {{
			rou_gov_states_grid = {{
				array = rou_sel_states
				change_scope = yes
				entry_container = "rou_gov_state_entry"
			}}
		}}
		ai_enabled = {{ always = no }}
	}}"""
    # the scripted localisation
    sl = ["defined_text = {", "\tname = GetRouGovName",
          "\ttext = { trigger = { check_variable = { rou_gov_sel = 0 } } localization_key = ROU_GOV_NONE }"]
    sl += [f"\ttext = {{ trigger = {{ check_variable = {{ rou_gov_sel = {g['n']} }} }} localization_key = ROU_GOV_{g['n']}_NAME }}"
           for g in govs] + ["\ttext = { trigger = { check_variable = { rou_gov_sel = 27 } } localization_key = ROU_GOV_27_NAME }", "}"]
    L("ROU_GOV_NONE", "The Realm")
    L("ROU_GOV_27_NAME", "The Crown's Domain")
    crown_mp = Counter()
    for s in royal:
        crown_mp[P.get(s, RM.ROYAL_PEOPLE)] += st[s]["manpower"]
    crown_peoples = ", ".join(f"{RM.PEOPLES[p][0]} {100 * c / sum(crown_mp.values()):.0f} %" for p, c in crown_mp.most_common())
    for key, field, crown_text, none in (("GetRouGovGovernor", "governor", "Held by the Prince", "Pick a généralité on the map"),
                                         ("GetRouGovOrigin", "origin", "Of the Généralité of Couronneterre in name (but the "
                                          "Oriental Territories), bound to the Crown in practice", ""),
                                         ("GetRouGovPeoples", "peoples", crown_peoples, "")):
        sl += ["defined_text = {", f"\tname = {key}"]
        sl.append(f"\ttext = {{ trigger = {{ check_variable = {{ rou_gov_sel = 0 }} }} localization_key = ROU_GOV_0_{field.upper()} }}")
        L(f"ROU_GOV_0_{field.upper()}", none)
        for g in govs:
            sl.append(f"\ttext = {{ trigger = {{ check_variable = {{ rou_gov_sel = {g['n']} }} }} localization_key = ROU_GOV_{g['n']}_{field.upper()} }}")
        sl.append(f"\ttext = {{ trigger = {{ check_variable = {{ rou_gov_sel = 27 }} }} localization_key = ROU_GOV_27_{field.upper()} }}")
        L(f"ROU_GOV_27_{field.upper()}", crown_text)
        sl.append("}")
    total = {g["n"]: sum(g["shares"].values()) for g in govs}
    for g in govs:
        L(f"ROU_GOV_{g['n']}_NAME", f"Généralité of {g['name']}")
        L(f"ROU_GOV_{g['n']}_GOVERNOR", f"Governor: {g['governor']}")
        L(f"ROU_GOV_{g['n']}_ORIGIN", g["origin"])
        peoples = ", ".join(f"{RM.PEOPLES[p][0]} {100 * c / total[g['n']]:.0f} %"
                            for p, c in sorted(g["shares"].items(), key=lambda kv: -kv[1]))
        L(f"ROU_GOV_{g['n']}_PEOPLES", peoples)
        L(f"ROU_GOV_{g['n']}_TT", f"§Y{g['name']}§!: loyalty [?rou_gov_{g['n']}_loyalty|0]. Click to see it.")
    L("ROU_GOV_27_TT", "§YThe Crown's Domain§!: the eleven Royal Fiefs, all but the Oriental Territories technically of "
      "the Généralité of Couronneterre, though bound more to the Crown than to its governor. Click to see them.")
    sl += ["defined_text = {", "\tname = GetRouGovLoyalty",
           "\ttext = { trigger = { OR = { check_variable = { rou_gov_sel = 0 } check_variable = { rou_gov_sel = 27 } } } localization_key = ROU_GOV_LOYALTY_NONE }"]
    L("ROU_GOV_LOYALTY_NONE", "")
    for b, (nm, t) in enumerate(zip(BAND_NAMES, (80, 60, 40, 20, 0))):
        sl.append(f"\ttext = {{ trigger = {{ check_variable = {{ rou_gov_sel_loyalty > {t - .01} }} }} localization_key = ROU_GOV_LOYALTY_{b + 1} }}")
        L(f"ROU_GOV_LOYALTY_{b + 1}", f"§Y[?rou_gov_sel_loyalty|0]§!  {nm}")
    sl.append("}")
    for key, suffix in (("GetRouGovAttitude", ""), ("GetRouGovAttitudeDesc", "_DESC")):
        sl += ["defined_text = {", f"\tname = {key}",
               "\ttext = { trigger = { OR = { check_variable = { rou_gov_sel = 0 } check_variable = { rou_gov_sel = 27 } } } "
               "localization_key = ROU_GOV_LOYALTY_NONE }"]
        for i, (a, desc) in enumerate(RM.ATTITUDES, start=1):
            sl.append(f"\ttext = {{ trigger = {{ check_variable = {{ rou_gov_sel_att = {i} }} }} localization_key = ROU_GOV_ATT_{i}{suffix} }}")
            if suffix:
                L(f"ROU_GOV_ATT_{i}_DESC", desc)
            else:
                L(f"ROU_GOV_ATT_{i}", f"{a}  (next session: their temper may change)")
        sl.append("}")
    sl += ["defined_text = {", "\tname = GetRouStatePeople"]
    for i, p in enumerate(people_keys, start=1):
        sl.append(f"\ttext = {{ trigger = {{ check_variable = {{ rou_people = {i} }} }} localization_key = ROU_PEOPLE_{i} }}")
        L(f"ROU_PEOPLE_{i}", RM.PEOPLES[p][0])
    sl += ["}", "defined_text = {", "\tname = GetRouStateLevy",
           "\ttext = { trigger = { NOT = { has_state_flag = rou_inspected } } localization_key = ROU_LEVY_UNKNOWN }",
           "\ttext = { trigger = { has_state_flag = rou_ceremonial } localization_key = ROU_LEVY_CEREMONIAL }"]
    L("ROU_LEVY_UNKNOWN", "§gUnknown§!")
    L("ROU_LEVY_CEREMONIAL", "§YCeremonial§!")
    for i, nm in enumerate(LEVY_NAMES):
        sl.append(f"\ttext = {{ trigger = {{ check_variable = {{ rou_levy = {i} }} }} localization_key = ROU_LEVY_{i} }}")
        L(f"ROU_LEVY_{i}", nm)
    sl.append("}")
    # the decision category and the Blue Guard of Brume (the author's: "an emergency measure. Costs little Political
    # power, but greatly degrades loyalty and angers the vassals"; "two or three divisions of leg infantry, but at elite
    # experience")
    brume = next(s for s in gov_of if st[s]["name"] == "Grand Brume")
    brume_gov = gov_of[brume]
    prov = int(re.search(r"provinces\s*=\s*\{\s*(\d+)", (OUT / "history" / "states").joinpath(
        next(p.name for p in (OUT / "history" / "states").iterdir() if p.name.startswith(f"{brume}-"))).read_text(
        encoding="utf-8-sig")).group(1))
    write("common/decisions/categories/valsora_rouental.txt", "\n".join([
        "ROU_governorates = {", "\ticon = GFX_decision_category_generic", "\tpicture = GFX_decision_cat_picture_operational_planning",
        "\tallowed = { original_tag = ROU }", "\tvisible = { original_tag = ROU }", "\tscripted_gui = rou_gov_category",
        "\tpriority = 210", "}", ""]))
    write("common/decisions/valsora_rouental.txt", "\n".join([
        "ROU_governorates = {", "\tROU_raise_blue_guard = {", "\t\ticon = GFX_decision_generic_military",
        f"\t\tvisible = {{ owns_state = {brume} }}", f"\t\tavailable = {{ owns_state = {brume} }}",
        "\t\tfire_only_once = yes", "\t\tcost = 10", "\t\tcomplete_effect = {",
        "\t\t\tdivision_template = {", '\t\t\t\tname = "Garde Bleue de Brume"', "\t\t\t\tregiments = {",
        *[f"\t\t\t\t\tinfantry = {{ x = {x} y = {y} }}" for x in range(2) for y in range(3)], "\t\t\t\t}", "\t\t\t}",
        f"\t\t\t{brume} = {{",
        *[f'\t\t\t\tcreate_unit = {{ division = "name = \\"{k} Garde Bleue de Brume\\" division_template = \\"Garde Bleue de Brume\\" '
          f'start_experience_factor = 1 start_equipment_factor = 0.3" owner = ROU prioritize_location = {prov} }}'
          for k in ("1re", "2e")], "\t\t\t}",
        f"\t\t\tadd_to_variable = {{ rou_gov_{brume_gov}_favour = -20 }}",
        *[f"\t\t\tadd_to_variable = {{ rou_gov_{n}_favour = -5 }}" for n in n_all],
        "\t\t\tROU_gov_update = yes", "\t\t}", "\t\tai_will_do = { base = 0 }", "\t}",
        # a survey of every governorate's levies: repeatable, so the category (and its map) never empties
        "\tROU_survey_levies = {", "\t\ticon = GFX_decision_generic_civil_support", "\t\tcost = 75",
        # waiting by a flag, not days_re_enable: a decision waiting to be taken again leaves the list, and with the
        # Blue Guard raised the category emptied and its map button went with it (in game, 2026-10-23: "When the
        # survey all levies decision is taken, the box to open the map dissapears")
        "\t\tfire_only_once = no",
        "\t\tavailable = { custom_trigger_tooltip = { tooltip = ROU_survey_levies_wait NOT = { has_country_flag = rou_survey_cd } } }",
        "\t\tcomplete_effect = {", "\t\t\tset_country_flag = { flag = rou_survey_cd days = 180 }",
        *[f"\t\t\t{s_} = {{ set_state_flag = rou_inspected }}" for s_ in sorted(gov_of)],
        *[f"\t\t\tif = {{ limit = {{ check_variable = {{ rou_gov_{g['n']}_att = {att_names.index('Proud') + 1} }} }} "
          f"add_to_variable = {{ rou_gov_{g['n']}_favour = -5 }} }}" for g in govs],
        "\t\t\tROU_gov_update = yes", "\t\t}", "\t\tai_will_do = { base = 0 }", "\t}", "}", ""]))
    L("ROU_survey_levies", "Survey the Realm's Levies")
    L("ROU_survey_levies_wait", "The inspectors went out less than 180 days ago")
    L("ROU_survey_levies_desc", "Inspectors through every généralité at once: every state's levies become known. Proud "
      "estates resent it (loyalty -5).")
    L("ROU_governorates", "The Généralités")  # the author, 2026-10-22: "Let's go with Généralité for the name of the districts"
    L("ROU_governorates_desc", "The Prince's governors and the estates of the realm.")
    L("ROU_raise_blue_guard", "Raise the Blue Guard of Brume")
    L("ROU_raise_blue_guard_desc", "An emergency measure: Grand Brume's ceremonial corps, two divisions of leg infantry "
      "elite in their drill and poor in their arms, called out. It costs little, but Graisivaudan's loyalty falls by 20, "
      "and every other généralité's by 5: the vassals are angered.")
    # a state modifier's icon is 32 px (the game's gfx/interface/state_modifiers/; its grid's slots 33): a national
    # spirit's, 64 px, ran over the province band below it (in game, 2026-10-23: "State modifiers also don't quite fit
    # right"). The game's crown (its Norwegian monarchism modifier): loyalty to the Crown
    dyn = "\n".join(["ROU_governorate_loyalty = {", "\ticon = GFX_modifiers_NOR_monarchism",
                     "\tenable = { is_owned_by = ROU }", "\tlocal_manpower = rou_mp_mod", "}", ""])
    write("common/dynamic_modifiers/valsora_rouental.txt", dyn)
    L("ROU_governorate_loyalty", "The Généralité's Loyalty")
    return [window_gui, entry, category], sgui, effects, sl


def main():
    texts = []

    def write(rel, content):
        p = OUT / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        texts.append(rel)

    es_button, es_window, es_sgui, es_effects, es_sloc = three_estates(write)
    gov_windows, gov_sgui, gov_effects, gov_sloc = governorates(write)
    write("interface/valsora_rouental.gui", "guiTypes = {\n" + "\n".join([es_button, es_window] + gov_windows) + "\n}\n")
    write("interface/valsora_rouental.gfx", "spriteTypes = {\n" + "\n".join(SPRITES) + "\n}\n")
    write("common/scripted_guis/valsora_rouental.txt", "scripted_gui = {\n" + es_sgui + "\n" + gov_sgui + "\n}\n")
    eff = []
    every = {**es_effects, **gov_effects}
    first = ["ROU_es_court", "ROU_es_update", "ROU_gov_update", "ROU_gov_leanings", "ROU_es_shift",
             "ROU_es_ra_change"]   # each before the effects that call it
    for name, body in [(n, every[n]) for n in first] + [(n, b) for n, b in every.items() if n not in first]:
        eff += [f"{name} = {{", *["\t" + b for b in body], "}"]
    write("common/scripted_effects/valsora_rouental.txt", "\n".join(eff) + "\n")
    write("common/scripted_localisation/valsora_rouental.txt", "\n".join(es_sloc + gov_sloc) + "\n")
    write("common/on_actions/valsora_rouental.txt", "\n".join([
        "on_actions = {", "\ton_startup = {", "\t\teffect = {", "\t\t\tROU = {",
        "\t\t\t\tif = {", "\t\t\t\t\tlimit = { NOT = { has_global_flag = valsora_rouental_systems } }",
        "\t\t\t\t\tROU_es_init = yes", "\t\t\t\t\tROU_gov_init = yes",
        "\t\t\t\t\tset_global_flag = valsora_rouental_systems", "\t\t\t\t}", "\t\t\t}", "\t\t}", "\t}",
        "\ton_monthly_ROU = {", "\t\teffect = {", "\t\t\tROU_es_trail = yes", "\t\t\tROU_es_drift = yes",
        "\t\t\tROU_es_month = yes", "\t\t}", "\t}", *serelle_battles(), "}", ""]))
    p = OUT / "localisation/english/valsora_rouental_l_english.yml"
    p.write_text("\n".join(LOC) + "\n", encoding="utf-8-sig")
    print(f"rouental_ui.py: the three estates and the governorates' windows into {OUT} ({len(SPRITES)} pictures, "
          f"{len(texts) + 1} files)")


if __name__ == "__main__":
    main()
