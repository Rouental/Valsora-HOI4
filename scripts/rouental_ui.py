"""Rouental's governorates and three powers in the game, bare bones (the author, 2026-10-21, night: "I think we should
start to try to put the mockups into practice, to make sure everything were planning will work. Let's get them into
the game, even if they're bare bones for now"). The mockups are deco_ui/art/proposals/governorates/ and three_powers/.

Run after build_mod.py and deco_ui.py (run_all.sh): it reads the build (the provinces map, the states, their names and
manpower: rouental_realm.py) and writes into it:
  - the three powers (the Sacred Prince, the Voix, the Speaker of the Estates General): a button on the politics screen
    where the game's balance of power sits, and beside it a window with the triangle, the marker placed by the shares
    (scripted GUI properties), its six months' trail, the zone and its effects (a national spirit each), the three
    holders and four decisions; a monthly drift; the estates' leanings (Pious to the Voix, Leal to the Prince, Proud to
    the Speaker) moving the governorates' loyalty;
  - the governorates: a decision category (with a scripted GUI) that opens the map of the realm: every governorate
    drawn from the build's own state borders and coloured by its loyalty, clickable (its shape, and its seal), a card
    with its governor, loyalty, estates, peoples and states (a dynamic list: people, levies seen by inspectors, men),
    four actions (Send Inspectors, Grant Privileges, Demand Levies, Summon the Estates); loyalty moves each state's
    manpower (a dynamic modifier); the Crown's Domain apart; and the Blue Guard of Brume as an emergency decision.
Every name and number but the author's (the start of the three powers, the holders, the peoples' leanings, the Blue
Guard) is a placeholder, as in the mockups. What is assumed about the game is listed in docs/CONTENT.md.
"""
import math
import os
import re
import sys
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
          big="valsora_deco_heading_24", italic="valsora_deco_italic_15", button="valsora_deco_body_13")
     if DECO_UI else
     dict(title="hoi_24header", head="hoi_20bs", body="hoi_16mbs", small="hoi_16mbs", label="hoi_16mbs",
          value="hoi_18mbs", big="hoi_24header", italic="hoi_16mbs", button="hoi_16mbs"))


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


# ================================================================ the three powers
POWERS = [("prince", "The Sacred Prince", "Prince", (217, 181, 101)), ("voix", "The Voix", "Voix", (233, 227, 210)),
          ("speaker", "The Speaker", "Speaker", (111, 155, 192))]
START = (40, 35, 25)            # the author's (2026-10-21, night): "Probably Prince 40, Voix 35, Speaker 25"
# the seven zones (the author: "Yes, it looks good"); their names and effects are Claude's placeholders
ZONES = [
    dict(key="prince", name="Sacred Majesty", where="The Prince holds 60 or more",
         desc="The Prince rules by sacred right, and rules alone.", pts=((100, 0, 0), (60, 40, 0), (60, 0, 40)),
         col=POWERS[0][3], mods={"political_power_factor": 0.2, "stability_factor": -0.05},
         more="Rule by Royal Decree costs half; every governorate's loyalty -5"),
    dict(key="voix", name="Rule of the Voix", where="The Voix holds 60 or more",
         desc="The Voix speaks, and Prince and Estates obey.", pts=((0, 100, 0), (40, 60, 0), (0, 60, 40)),
         col=POWERS[1][3], mods={"stability_factor": 0.1, "political_power_factor": -0.1},
         more="Pious estates' loyalty +10; the Southmarchers' -10"),
    dict(key="speaker", name="The Estates Supreme", where="The Speaker holds 60 or more",
         desc="The Estates General governs through its Speaker; the Prince signs what it sends.",
         pts=((0, 0, 100), (40, 0, 60), (0, 40, 60)), col=POWERS[2][3], mods={"political_power_factor": -0.2},
         more="Every governorate's loyalty +10; Rule by Royal Decree closed"),
    dict(key="throne", name="Throne and Altar", where="The Speaker under 15",
         desc="Prince and Voix govern together; the Estates General sits unheard.",
         pts=((60, 40, 0), (40, 60, 0), (25, 60, 15), (60, 25, 15)), col=None,
         mods={"stability_factor": 0.05, "political_power_factor": 0.1}, more="Proud estates' loyalty -10"),
    dict(key="crown", name="Crown and Estates", where="The Voix under 15",
         desc="Prince and Speaker govern together; the Voix is kept from the council.",
         pts=((60, 0, 40), (40, 0, 60), (25, 15, 60), (60, 15, 25)), col=None,
         mods={"political_power_factor": 0.05}, more="Pious estates' loyalty -10"),
    dict(key="in_name", name="The Prince in Name", where="The Prince under 15",
         desc="The Voix and the Estates govern between them; the Prince reigns, and no more.",
         pts=((0, 60, 40), (0, 40, 60), (15, 25, 60), (15, 60, 25)), col=None,
         mods={"stability_factor": -0.1, "political_power_factor": -0.15}, more="Leal estates' loyalty -10"),
    dict(key="balance", name="The Unwritten Balance", where="None over 60, none under 15",
         desc="No power can act alone: Rouental as it has long been.",
         pts=((60, 25, 15), (60, 15, 25), (25, 15, 60), (15, 25, 60), (15, 60, 25), (25, 60, 15)), col=None, mods={},
         more="No effects"),
]
MIX = {"throne": (0, 1), "crown": (0, 2), "in_name": (1, 2)}
# the four decisions (placeholders): name, political power, shifts (prince, voix, speaker), more
DECISIONS = [("Rule by Royal Decree", 50, (6, -2, -4), "stability -2 %"),
             ("Seek the Voix's Blessing", 30, (-4, 6, -2), None),
             ("Summon the Estates General", 40, (-3, -3, 6), "every governorate's estates change their temper"),
             ("A Royal Progress", 25, (3, 0, -3), "a governorate's loyalty +5")]
HOLDERS = [("Roland II Cahun", "GFX_portrait_ROU_roland_cahun", "Free of the regency at last."),
           ("Anserra IX", "GFX_portrait_ROU_mahaut_vi", "Gave up much of the regency's power."),
           ("Tara Blanchart", "GFX_portrait_ROU_tara_blanchart", "Speaks for the estates of the realm.")]

TW, TH = 520, 452                 # the triangle's picture
TRI_A, TRI_L = (260, 36), 440
TRI_H = TRI_L * math.sqrt(3) / 2
TRI_B = (TRI_A[0] - TRI_L / 2, TRI_A[1] + TRI_H)
TRI_C = (TRI_A[0] + TRI_L / 2, TRI_A[1] + TRI_H)
MARK = 26                          # the marker's size
DOT = 8


def at(p, v, s):
    t = p + v + s
    return ((p * TRI_A[0] + v * TRI_B[0] + s * TRI_C[0]) / t, (p * TRI_A[1] + v * TRI_B[1] + s * TRI_C[1]) / t)


def zone_colour(z, a):
    if z["col"]:
        return (*z["col"], a)
    if z["key"] in MIX:
        i, j = MIX[z["key"]]
        c = tuple((POWERS[i][3][k] + POWERS[j][3][k]) // 2 for k in range(3))
        return (*c, int(a * .55))
    return (255, 255, 255, 8)


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
    # the zones' names (Federo capitals; the edges' outside their strips, along them)
    fnt = font("federo", 11 * SS)
    labels = {"prince": ((76, 12, 12), 0, ["SACRED", "MAJESTY"]), "voix": ((12, 76, 12), 0, ["RULE OF", "THE VOIX"]),
              "speaker": ((12, 12, 76), 0, ["THE ESTATES", "SUPREME"]),
              "balance": ((24, 38, 38), 0, ["THE UNWRITTEN", "BALANCE"]),
              "throne": ((50, 50, 0), -60, ["THRONE AND ALTAR"]), "crown": ((50, 0, 50), 60, ["CROWN AND ESTATES"]),
              "in_name": ((0, 50, 50), 0, ["THE PRINCE IN NAME"])}
    gcx, gcy = cx / SS, cy / SS
    for key, (share, rot, lines) in labels.items():
        x, y = at(*share)
        if key in ("throne", "crown", "in_name"):
            n = math.hypot(x - gcx, y - gcy)
            x, y = x + (x - gcx) / n * 19, y + (y - gcy) / n * 19
        lab = Image.new("RGBA", (220 * SS, 40 * SS), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lab)
        for i, s in enumerate(lines):
            tracked(ld, (110 * SS, (20 - 7 * len(lines) + 14 * i) * SS - fnt.size * .5), s, fnt, (244, 236, 217, 200),
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


def portrait_frame(w, h):
    """a gilt frame round a portrait, chamfered, its middle clear"""
    W, H = w * SS, h * SS
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon(chamfer_poly(0, 0, W - 1, H - 1, 8 * SS), outline=(*GILT, 255), width=int(2 * SS))
    d.polygon(chamfer_poly(4 * SS, 4 * SS, W - 1 - 4 * SS, H - 1 - 4 * SS, 6 * SS), outline=(201, 165, 90, 130),
              width=SS)
    return down(im)


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


def three_powers(write):
    """the politics screen's button, the window, their scripts and text"""
    tri = save("tp_triangle", triangle_picture())
    zone_sprites = []
    for z in ZONES:
        img, off = zone_highlight(z)
        zone_sprites.append((save(f"tp_zone_{z['key']}", img), off))
    mark = save("tp_marker", marker())
    dots = save("tp_dot", dot())
    frame = save("tp_portrait_frame", portrait_frame(70, 92))
    btn = save("tp_button", mini_triangle(), effect=BUTTON_FX)
    dec = save("tp_decision", plate(380, 36, 6), effect=BUTTON_FX)
    head = save("tp_band", plate(536, 34, 7, lit=True))
    # where the button sits: under the popularities, the game's balance of power place on the Deco UI's politics screen
    # (deco_ui/tools/layout_politics.BOP: panel x 18, y 474); on the game's own screen, under its leader (a guess)
    bx, by = (18, 474) if DECO_UI else (300, 300)
    WX, WY, WW, WH = 556, 96, 980, 822
    TX, TY = 24, 118                                         # the triangle's picture in the window
    L("ROU_TP_BUTTON_TITLE", "The Three Powers")
    L("ROU_TP_BUTTON_ZONE", "[GetRouTpZone]")
    L("ROU_TP_BUTTON_TT", "The Sacred Prince §Y[?rou_prince|0]§!, the Voix §Y[?rou_voix|0]§!, the Speaker "
      "§Y[?rou_speaker|0]§!: [GetRouTpZone]. Click to open or close the three powers.")
    button_gui = window("rou_tp_button_window", bx, by, 244, 40, [
        button("rou_tp_open_button", btn, 0, 0, tooltip="ROU_TP_BUTTON_TT"),
        text("rou_tp_button_title", 52, 6, 186, 14, "ROU_TP_BUTTON_TITLE", "label"),
        text("rou_tp_button_zone", 52, 20, 186, 16, "ROU_TP_BUTTON_ZONE", "small")])
    kids = [
        text("rou_tp_title", 0, 14, WW, 30, L("ROU_TP_TITLE", "The Three Powers"), "title", fmt="center"),
        button("rou_tp_close", "GFX_closebutton", WW - 46, 10),
        text("rou_tp_date", 24, 60, 220, 20, L("ROU_TP_SUB", "No constitution binds them."), "italic"),
        icon("rou_tp_triangle", tri, TX, TY)]
    for z, (spr, (ox, oy)) in zip(ZONES, zone_sprites):
        kids.append(icon(f"rou_tp_zone_{z['key']}", spr, TX + ox, TY + oy, transparent=True))
    for i in range(1, 7):
        kids.append(icon(f"rou_tp_trail_{i}", dots, TX, TY, transparent=True))
    kids.append(icon("rou_tp_marker", mark, TX, TY, transparent=True))
    # the three holders at their corners: portrait, frame, title and share
    spots = [(TX + TRI_A[0] - 35, 54, TX + TRI_A[0] + 44, 72, "left"),
             (TX + TRI_B[0] - 35, TY + TRI_B[1] + 14, TX + TRI_B[0] + 44, TY + TRI_B[1] + 28, "left"),
             (TX + TRI_C[0] - 35, TY + TRI_C[1] + 14, TX + TRI_C[0] - 44 - 180, TY + TRI_C[1] + 28, "right")]
    for (key, title, short, _), (name, sprite, _line), (px, py, lx, ly, al) in zip(POWERS, HOLDERS, spots):
        kids += [icon(f"rou_tp_{key}_portrait", sprite, px + 4, py + 4, scale=0.397),
                 icon(f"rou_tp_{key}_frame", frame, px, py, transparent=True),
                 text(f"rou_tp_{key}_label", lx, ly, 180, 14, L(f"ROU_TP_{key.upper()}_LABEL", title), "label", fmt=al),
                 text(f"rou_tp_{key}_share", lx, ly + 16, 180, 32, L(f"ROU_TP_{key.upper()}_SHARE", f"[?rou_{key}|0]"),
                      "big", fmt=al)]
    # where the balance stands
    ZY = 668
    kids += [text("rou_tp_where", 24, ZY, 536, 14, L("ROU_TP_WHERE", "Where the balance stands"), "label"),
             icon("rou_tp_zone_band", head, 24, ZY + 18),
             text("rou_tp_zone_name", 24, ZY + 26, 536, 22, "ROU_TP_BUTTON_ZONE", "head", fmt="center"),
             text("rou_tp_zone_desc", 24, ZY + 60, 536, 40, L("ROU_TP_ZONE_DESC", "[GetRouTpZoneDesc]"), "italic",
                  fmt="center"),
             text("rou_tp_zone_effects", 24, ZY + 104, 536, 36, L("ROU_TP_ZONE_EFFECTS", "[GetRouTpZoneEffects]"),
                  "small", fmt="center")]
    # the right column: the holders, the decisions, the estates' leanings
    RX = 584
    kids.append(text("rou_tp_powers_label", RX, 60, 380, 14, L("ROU_TP_POWERS", "The powers"), "label"))
    for i, ((key, title, short, _), (name, sprite, line)) in enumerate(zip(POWERS, HOLDERS)):
        y = 80 + i * 54
        kids += [text(f"rou_tp_{key}_name", RX, y, 300, 20, L(f"ROU_TP_{key.upper()}_NAME", f"{name}  ·  {title}"), "body"),
                 text(f"rou_tp_{key}_line", RX, y + 20, 300, 16, L(f"ROU_TP_{key.upper()}_LINE", line), "italic"),
                 text(f"rou_tp_{key}_share_r", RX + 300, y, 80, 24, f"ROU_TP_{key.upper()}_SHARE", "big", fmt="right")]
    kids.append(text("rou_tp_decisions_label", RX, 254, 380, 14, L("ROU_TP_DECISIONS", "Decisions"), "label"))
    for i, (name, pp, sh, more) in enumerate(DECISIONS):
        k = f"ROU_TP_DEC_{i + 1}"
        L(k, f"{name}  ·  {pp} PP")
        parts = [f"{t} {'+' if v > 0 else ''}{v}" for (_, t, _, _), v in zip(POWERS, sh) if v]
        L(k + "_TT", f"§Y{name}§!\\nPolitical power: -{pp}\\n" + "\\n".join(parts) + (f"\\n{more[0].upper() + more[1:]}" if more else "")
          + "\\nOnce in 30 days.")
        kids.append(button(f"rou_tp_dec_{i + 1}", dec, RX, 274 + i * 42, k, F["button"], tooltip=k + "_TT"))
    kids.append(text("rou_tp_lean_label", RX, 450, 380, 14, L("ROU_TP_LEANINGS", "The estates' leanings"), "label"))
    for i, (att, key, title) in enumerate((("Pious", "voix", "the Voix"), ("Leal", "prince", "the Sacred Prince"),
                                           ("Proud", "speaker", "the Speaker"))):
        kids.append(text(f"rou_tp_lean_{key}", RX, 470 + i * 22, 380, 20,
                         L(f"ROU_TP_LEAN_{key.upper()}", f"{att} estates lean to {title}: loyalty [?rou_lean_{key}|+0] "
                           "since 1 January"), "small"))
    kids.append(text("rou_tp_footer", RX, 560, 380, 90, L("ROU_TP_FOOTER", "Each month the balance drifts a point "
                     "or two on its own; decisions, events and focuses move it further. A move toward a power pleases "
                     "the estates who lean to it (half the shift, as loyalty)."), "italic"))
    win_gui = window("rou_tp_window", WX, WY, WW, WH, kids, bg="GFX_tiled_window_2b_border")

    # ---- the scripts
    ax, ay = TRI_A
    bxx, byy = TRI_B
    cxx, cyy = TRI_C
    coef = lambda v: f"{v / 100:.4f}"  # noqa: E731
    # the marker's place in the window: the properties below set its x and y there, not in the triangle (in game,
    # 2026-10-22: without the triangle's own place, TX and TY, the marker stood 24 px left and 118 px up)
    pos = ["set_variable = { rou_tp_mx = rou_prince }", f"multiply_variable = {{ rou_tp_mx = {coef(ax)} }}",
           "set_temp_variable = { tp_t = rou_voix }", f"multiply_temp_variable = {{ tp_t = {coef(bxx)} }}",
           "add_to_variable = { rou_tp_mx = tp_t }", "set_temp_variable = { tp_t = rou_speaker }",
           f"multiply_temp_variable = {{ tp_t = {coef(cxx)} }}", "add_to_variable = { rou_tp_mx = tp_t }",
           f"add_to_variable = {{ rou_tp_mx = {TX - MARK // 2} }}",
           "set_variable = { rou_tp_my = rou_prince }", f"multiply_variable = {{ rou_tp_my = {coef(ay)} }}",
           "set_temp_variable = { tp_t = rou_voix }", f"multiply_temp_variable = {{ tp_t = {coef(byy)} }}",
           "add_to_variable = { rou_tp_my = tp_t }", "set_temp_variable = { tp_t = rou_speaker }",
           f"multiply_temp_variable = {{ tp_t = {coef(cyy)} }}", "add_to_variable = { rou_tp_my = tp_t }",
           f"add_to_variable = {{ rou_tp_my = {TY - MARK // 2} }}"]
    zone_if = []
    order = [("rou_prince > 59.99", 1), ("rou_voix > 59.99", 2), ("rou_speaker > 59.99", 3), ("rou_speaker < 15", 4),
             ("rou_voix < 15", 5), ("rou_prince < 15", 6)]
    for i, (cond, n) in enumerate(order):
        zone_if.append(f"{'if' if i == 0 else 'else_if'} = {{ limit = {{ check_variable = {{ {cond} }} }} "
                       f"set_variable = {{ rou_tp_zone = {n} }} }}")
    zone_if.append("else = { set_variable = { rou_tp_zone = 7 } }")
    spirits = ["if = { limit = { NOT = { check_variable = { rou_tp_zone = rou_tp_zone_shown } } }"]
    for z in ZONES[:-1]:
        spirits.append(f"\tif = {{ limit = {{ has_idea = ROU_zone_{z['key']} }} remove_ideas = ROU_zone_{z['key']} }}")
    for n, z in enumerate(ZONES[:-1], start=1):
        spirits.append(f"\tif = {{ limit = {{ check_variable = {{ rou_tp_zone = {n} }} }} add_ideas = ROU_zone_{z['key']} }}")
    spirits += ["\tset_variable = { rou_tp_zone_shown = rou_tp_zone }", "}"]
    effects = {
        # call with the temp variables tp_d_prince, tp_d_voix, tp_d_speaker set
        "ROU_tp_shift": [
            "add_to_variable = { rou_prince = tp_d_prince }", "add_to_variable = { rou_voix = tp_d_voix }",
            "add_to_variable = { rou_speaker = tp_d_speaker }",
            *[f"clamp_variable = {{ var = rou_{k} min = 0 max = 100 }}" for k, *_ in POWERS],
            "set_temp_variable = { tp_total = rou_prince }", "add_to_temp_variable = { tp_total = rou_voix }",
            "add_to_temp_variable = { tp_total = rou_speaker }",
            "if = { limit = { check_variable = { tp_total > 0 } }",
            "\tset_temp_variable = { tp_k = 100 }", "\tdivide_temp_variable = { tp_k = tp_total }",
            *[f"\tmultiply_variable = {{ rou_{k} = tp_k }}" for k, *_ in POWERS], "}",
            # the estates' leanings: half the shift, as loyalty
            *[f"set_temp_variable = {{ tp_h_{k} = tp_d_{k} }}" for k, *_ in POWERS],
            *[f"multiply_temp_variable = {{ tp_h_{k} = 0.5 }}" for k, *_ in POWERS],
            *[f"add_to_variable = {{ rou_lean_{k} = tp_h_{k} }}" for k, *_ in POWERS],
            "ROU_gov_leanings = yes", "ROU_tp_update = yes"],
        "ROU_tp_update": [*zone_if, *spirits, *pos, "add_to_variable = { rou_tp_dirty = 1 }"],
        "ROU_tp_trail": [*[f"set_variable = {{ rou_tp_h{a}{i} = rou_tp_h{a}{i - 1} }}" for i in range(6, 1, -1) for a in "xy"],
                         f"set_variable = {{ rou_tp_hx1 = rou_tp_mx }}", f"add_to_variable = {{ rou_tp_hx1 = {MARK // 2 - DOT // 2} }}",
                         f"set_variable = {{ rou_tp_hy1 = rou_tp_my }}", f"add_to_variable = {{ rou_tp_hy1 = {MARK // 2 - DOT // 2} }}"],
        "ROU_tp_drift": ["random_list = {", *[
            f"\t10 = {{ set_temp_variable = {{ tp_d_prince = {a} }} set_temp_variable = {{ tp_d_voix = {b} }} "
            f"set_temp_variable = {{ tp_d_speaker = {c} }} }}"
            for a, b, c in ((1, -1, 0), (-1, 1, 0), (1, 0, -1), (-1, 0, 1), (0, 1, -1), (0, -1, 1), (2, -1, -1),
                            (-1, 2, -1), (-1, -1, 2))],
            "\t10 = { set_temp_variable = { tp_d_prince = 0 } set_temp_variable = { tp_d_voix = 0 } "
            "set_temp_variable = { tp_d_speaker = 0 } }", "}", "ROU_tp_shift = yes"],
        "ROU_tp_init": [*[f"set_variable = {{ rou_{k} = {v} }}" for (k, *_), v in zip(POWERS, START)],
                        "set_variable = { rou_tp_zone_shown = 0 }", "ROU_tp_update = yes",
                        *[f"set_variable = {{ rou_tp_h{a}{i} = rou_tp_m{a} }}" for i in range(1, 7) for a in "xy"],
                        *[f"add_to_variable = {{ rou_tp_h{a}{i} = {MARK // 2 - DOT // 2} }}" for i in range(1, 7) for a in "xy"]],
    }
    dec_effects, dec_triggers = [], []
    for i, (name, pp, sh, more) in enumerate(DECISIONS, start=1):
        body = [f"add_political_power = -{pp}", *[f"set_temp_variable = {{ tp_d_{k} = {v} }}" for (k, *_), v in zip(POWERS, sh)],
                "ROU_tp_shift = yes", f"set_country_flag = {{ flag = rou_tp_cd_{i} days = 30 }}"]
        if i == 1:
            body.insert(1, "add_stability = -0.02")
        if i == 3:
            body.insert(1, "ROU_gov_session_all = yes")
        if i == 4:
            body.insert(1, "ROU_gov_progress = yes")
        dec_effects.append(f"\t\t\trou_tp_dec_{i}_click = {{\n" + "\n".join("\t\t\t\t" + b for b in body) + "\n\t\t\t}")
        cond = [f"has_political_power > {pp - 0.01}", f"NOT = {{ has_country_flag = rou_tp_cd_{i} }}"]
        if i == 1:
            cond.append("NOT = { check_variable = { rou_tp_zone = 3 } }")
        dec_triggers.append(f"\t\t\trou_tp_dec_{i}_click_enabled = {{ {' '.join(cond)} }}")
    zone_triggers = [f"\t\t\trou_tp_zone_{z['key']}_visible = {{ check_variable = {{ rou_tp_zone = {n} }} }}"
                     for n, z in enumerate(ZONES, start=1)]
    props = ["\t\t\trou_tp_marker = { x = rou_tp_mx y = rou_tp_my }"]
    props += [f"\t\t\trou_tp_trail_{i} = {{ x = rou_tp_hx{i} y = rou_tp_hy{i} }}" for i in range(1, 7)]
    sgui = f"""	rou_tp_button = {{
		context_type = player_context
		window_name = "rou_tp_button_window"
		parent_window_token = politics_tab
		visible = {{ original_tag = ROU }}
		effects = {{
			rou_tp_open_button_click = {{
				if = {{ limit = {{ has_country_flag = rou_tp_open }} clr_country_flag = rou_tp_open }}
				else = {{ set_country_flag = rou_tp_open }}
			}}
		}}
		ai_enabled = {{ always = no }}
	}}
	rou_tp_window = {{
		context_type = player_context
		window_name = "rou_tp_window"
		visible = {{ original_tag = ROU has_country_flag = rou_tp_open }}
		effects = {{
			rou_tp_close_click = {{ clr_country_flag = rou_tp_open }}
{chr(10).join(dec_effects)}
		}}
		triggers = {{
{chr(10).join(dec_triggers + zone_triggers)}
		}}
		properties = {{
{chr(10).join(props)}
		}}
		ai_enabled = {{ always = no }}
	}}"""
    # the zones' spirits (placeholders: the effects of the mockup's sheet)
    ideas = ["ideas = {", "\tcountry = {"]
    for z in ZONES[:-1]:
        ideas += [f"\t\tROU_zone_{z['key']} = {{", "\t\t\tpicture = generic_central_management",
                  "\t\t\tallowed = { always = no }", "\t\t\tremoval_cost = -1", "\t\t\tmodifier = {",
                  *[f"\t\t\t\t{k} = {v}" for k, v in z["mods"].items()], "\t\t\t}", "\t\t}"]
        L(f"ROU_zone_{z['key']}", z["name"])
        L(f"ROU_zone_{z['key']}_desc", f"{z['desc']} {z['where']}. {z['more']}. (A placeholder, from the mockup.)")
    ideas += ["\t}", "}", ""]
    write("common/ideas/valsora_rouental_powers.txt", "\n".join(ideas))
    sloc = ["defined_text = {", "\tname = GetRouTpZone"]
    sloc += [f"\ttext = {{ trigger = {{ check_variable = {{ rou_tp_zone = {n} }} }} localization_key = ROU_TP_ZONE_{n} }}"
             for n in range(1, 8)]
    sloc += ["}", "defined_text = {", "\tname = GetRouTpZoneDesc"]
    sloc += [f"\ttext = {{ trigger = {{ check_variable = {{ rou_tp_zone = {n} }} }} localization_key = ROU_TP_ZONE_{n}_DESC }}"
             for n in range(1, 8)]
    sloc += ["}", "defined_text = {", "\tname = GetRouTpZoneEffects"]
    sloc += [f"\ttext = {{ trigger = {{ check_variable = {{ rou_tp_zone = {n} }} }} localization_key = ROU_TP_ZONE_{n}_EFF }}"
             for n in range(1, 8)]
    sloc.append("}")
    for n, z in enumerate(ZONES, start=1):
        L(f"ROU_TP_ZONE_{n}", z["name"])
        L(f"ROU_TP_ZONE_{n}_DESC", f"{z['desc']} ({z['where']}.)")
        mods = {"political_power_factor": "political power", "stability_factor": "stability"}
        parts = [f"{mods[k]} {'+' if v > 0 else ''}{round(v * 100)} %" for k, v in z["mods"].items()]
        L(f"ROU_TP_ZONE_{n}_EFF", "; ".join(parts + ([z["more"]] if z["more"] != "No effects" or not parts else [])))
    # a test (Rouental's Test Events category, out with the other tests): the balance to each zone in turn
    presets = [(70, 20, 10), (15, 70, 15), (15, 15, 70), (50, 42, 8), (50, 8, 42), (8, 46, 46), START]
    body = ["add_to_variable = { rou_tp_test = 1 }", "if = { limit = { check_variable = { rou_tp_test > 7 } } "
            "set_variable = { rou_tp_test = 1 } }"]
    for n, sh in enumerate(presets, start=1):
        body.append(f"if = {{ limit = {{ check_variable = {{ rou_tp_test = {n} }} }} "
                    + " ".join(f"set_variable = {{ rou_{k} = {v} }}" for (k, *_), v in zip(POWERS, sh)) + " }")
    body += ["ROU_tp_update = yes", "ROU_gov_update = yes"]
    write("common/decisions/valsora_rouental_tests.txt", "\n".join(
        ["ROU_test_events = {", "\tROU_test_three_powers = {", "\t\ticon = GFX_decision_generic_political_discourse",
         "\t\tfire_only_once = no", "\t\tcost = 0", "\t\tcomplete_effect = {", *["\t\t\t" + b for b in body], "\t\t}",
         "\t\tai_will_do = { base = 0 }", "\t}", "}", ""]))
    L("ROU_test_three_powers", "Test: the Three Powers to the Next Zone")
    L("ROU_test_three_powers_desc", "Moves the balance into each of the seven zones in turn (Sacred Majesty, Rule of the "
      "Voix, the Estates Supreme, Throne and Altar, Crown and Estates, the Prince in Name, back to the start), to see "
      "their spirits and the governorates' colours. A test: it goes with the others.")
    return button_gui, win_gui, sgui, effects, sloc


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
        overlays.append(save(f"gov_{g['n']}_sel", rgba_from(np.maximum(ring, cov * .32), HI)))
        fills.append((g, sprites, at_))
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
    kids = [text("rou_gov_title", 0, 16, WW, 30, L("ROU_GOV_TITLE", "The Governorates of Rouental"), "title", fmt="center"),
            button("rou_gov_close", "GFX_closebutton", WW - 46, 10),
            icon("rou_gov_map", base_spr, MX, MY)]
    for g, sprites, (x0, y0) in fills:
        for b, spr in enumerate(sprites, start=1):
            kids.append(icon(f"rou_gov_{g['n']}_b{b}", spr, MX + 4 + x0, MY + 4 + y0, transparent=True))
    kids.append(icon("rou_gov_crown_fill", crown_spr, MX + 4 + crown_at[0], MY + 4 + crown_at[1], transparent=True))
    for g, spr in zip(govs, overlays):
        x0, y0 = next(f[2] for f in fills if f[0] is g)
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
             text("rou_gov_hint", MX, MY + MH + 46, MW, 60, L("ROU_GOV_HINT", "Click a governorate, or its seal, to see "
                  "it. The colours are the governorates' loyalty to the Crown. A state's levies are known once inspectors "
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
             text("rou_gov_card_peoples", CX, 314, CW, 20, L("ROU_GOV_SEL_PEOPLES", "[GetRouGovPeoples]"), "small"),
             text("rou_gov_card_states_label", CX + 6, 344, 150, 14, L("ROU_GOV_STATES_HEAD", "State"), "label"),
             text("rou_gov_card_people_head", CX + 160, 344, 110, 14, L("ROU_GOV_PEOPLE_HEAD", "People"), "label"),
             text("rou_gov_card_levy_head", CX + 272, 344, 90, 14, L("ROU_GOV_LEVY_HEAD", "Levies"), "label"),
             text("rou_gov_card_men_head", CX + 360, 344, 64, 14, L("ROU_GOV_MEN_HEAD", "Men"), "label", fmt="right"),
             grid("rou_gov_states_grid", CX, 362, CW, 12 * 22, CW, 22, 1, 12)]
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
             "among the vassals of 26 governorates; the eleven Royal Fiefs answer to the Crown."), "italic"),
        # dark ink on the gold plate (the Deco fonts' K, as the politics screen's Head of State ribbon): the fonts' cream
        # was barely readable on it (the author, 2026-10-22)
        button("rou_gov_open_button", open_btn, 110, 52, L("ROU_GOV_OPEN", "§KOpen the Map of the Realm§!" if DECO_UI
                                                           else "Open the Map of the Realm"), F["button"])])

    # ---- the scripts
    n_all = [g["n"] for g in govs]
    att_names = [a for a, _ in RM.ATTITUDES]
    zone_mod = {1: ("all", -5), 2: [("Pious", 10)], 3: ("all", 10), 4: [("Proud", -10)], 5: [("Pious", -10)],
                6: [("Leal", -10)]}
    south = [g["n"] for g in govs if g["main"] == "Southmarch"]
    upd = []
    for g in govs:
        n = g["n"]
        v = f"rou_gov_{n}"
        upd += [f"set_variable = {{ {v}_loyalty = {g['static']} }}", f"add_to_variable = {{ {v}_loyalty = {v}_favour }}"]
        upd += [f"if = {{ limit = {{ check_variable = {{ {v}_att = {i} }} }} add_to_variable = {{ {v}_loyalty = {RM.ATTITUDE_MOD[a]} }} }}"
                for i, a in enumerate(att_names, start=1) if RM.ATTITUDE_MOD[a]]
        for z, spec in zone_mod.items():
            if isinstance(spec, tuple):
                upd.append(f"if = {{ limit = {{ check_variable = {{ rou_tp_zone = {z} }} }} add_to_variable = {{ {v}_loyalty = {spec[1]} }} }}")
            else:
                for att, d in spec:
                    i = att_names.index(att) + 1
                    upd.append(f"if = {{ limit = {{ check_variable = {{ rou_tp_zone = {z} }} check_variable = {{ {v}_att = {i} }} }} "
                               f"add_to_variable = {{ {v}_loyalty = {d} }} }}")
        if n in south:
            upd.append(f"if = {{ limit = {{ check_variable = {{ rou_tp_zone = 2 }} }} add_to_variable = {{ {v}_loyalty = -10 }} }}")
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
        "ROU_gov_leanings": [ln for g in govs for ln in (
            f"if = {{ limit = {{ {att_is(g, 'Pious')} }} add_to_variable = {{ rou_gov_{g['n']}_favour = tp_h_voix }} }}",
            f"if = {{ limit = {{ {att_is(g, 'Leal')} }} add_to_variable = {{ rou_gov_{g['n']}_favour = tp_h_prince }} }}",
            f"if = {{ limit = {{ {att_is(g, 'Proud')} }} add_to_variable = {{ rou_gov_{g['n']}_favour = tp_h_speaker }} }}")]
        + [ln for n in south for ln in (
            f"if = {{ limit = {{ check_variable = {{ tp_d_voix > 0 }} }} set_temp_variable = {{ tp_s = tp_d_voix }} "
            f"multiply_temp_variable = {{ tp_s = -0.2 }} add_to_variable = {{ rou_gov_{n}_favour = tp_s }} }}",)]
        + ["ROU_gov_update = yes"],
        "ROU_gov_select": ["clear_array = rou_sel_states"]
        + [ln for g in govs for ln in (
            f"if = {{ limit = {{ check_variable = {{ rou_gov_sel = {g['n']} }} }}",
            *[f"\t{s} = {{ ROU = {{ add_to_array = {{ rou_sel_states = PREV }} }} }}" for s in g["states"]], "}")]
        + ["if = { limit = { check_variable = { rou_gov_sel = 27 } }",
           *[f"\t{s} = {{ ROU = {{ add_to_array = {{ rou_sel_states = PREV }} }} }}" for s in royal], "}",
           "ROU_gov_update = yes"],
        "ROU_gov_session_all": [ln for g in govs for ln in roll(f"rou_gov_{g['n']}_att")],
        "ROU_gov_progress": ["random_list = {", *[f"\t10 = {{ add_to_variable = {{ rou_gov_{n}_favour = 5 }} }}" for n in n_all], "}"],
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
            f"else = {{ add_to_variable = {{ rou_gov_{g['n']}_favour = -10 }} }}"])
        + ["ROU_gov_update = yes"],
        "ROU_gov_act_session": ["add_political_power = -20"] + per_sel(lambda g: roll(f"rou_gov_{g['n']}_att"))
        + ["ROU_gov_update = yes"],
    }
    init = []
    for g in govs:
        init += [f"set_variable = {{ rou_gov_{g['n']}_att = {g['att']} }}", f"set_variable = {{ rou_gov_{g['n']}_favour = 0 }}"]
    people_keys = list(RM.PEOPLES) + ["Crown"]
    for s in sorted(set(gov_of) | set(royal)):
        p = P.get(s, "Crown")
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
    for key, field, crown_text, none in (("GetRouGovGovernor", "governor", "Held by the Prince", "Pick a governorate on the map"),
                                         ("GetRouGovOrigin", "origin", "Of the Governorate of Couronneterre in name, bound to the Crown in "
                                          "practice", ""),
                                         ("GetRouGovPeoples", "peoples", "The Crown's", "")):
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
        L(f"ROU_GOV_{g['n']}_NAME", f"Governorate of {g['name']}")
        L(f"ROU_GOV_{g['n']}_GOVERNOR", f"Governor: {g['governor']}")
        L(f"ROU_GOV_{g['n']}_ORIGIN", g["origin"])
        peoples = ", ".join(f"{RM.PEOPLES[p][0] if p in RM.PEOPLES else 'Crown'} {100 * c / total[g['n']]:.0f} %"
                            for p, c in sorted(g["shares"].items(), key=lambda kv: -kv[1]))
        L(f"ROU_GOV_{g['n']}_PEOPLES", peoples)
        L(f"ROU_GOV_{g['n']}_TT", f"§Y{g['name']}§!: loyalty [?rou_gov_{g['n']}_loyalty|0]. Click to see it.")
    L("ROU_GOV_27_TT", "§YThe Crown's Domain§!: the eleven Royal Fiefs, technically of the Governorate of "
      "Couronneterre, though bound more to the Crown than to its governor. Click to see them.")
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
        L(f"ROU_PEOPLE_{i}", RM.PEOPLES[p][0] if p in RM.PEOPLES else "Crown")
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
        "\t\tfire_only_once = no", "\t\tdays_re_enable = 180", "\t\tcomplete_effect = {",
        *[f"\t\t\t{s_} = {{ set_state_flag = rou_inspected }}" for s_ in sorted(gov_of)],
        *[f"\t\t\tif = {{ limit = {{ check_variable = {{ rou_gov_{g['n']}_att = {att_names.index('Proud') + 1} }} }} "
          f"add_to_variable = {{ rou_gov_{g['n']}_favour = -5 }} }}" for g in govs],
        "\t\t\tROU_gov_update = yes", "\t\t}", "\t\tai_will_do = { base = 0 }", "\t}", "}", ""]))
    L("ROU_survey_levies", "Survey the Realm's Levies")
    L("ROU_survey_levies_desc", "Inspectors through every governorate at once: every state's levies become known. Proud "
      "estates resent it (loyalty -5).")
    L("ROU_governorates", "The Governorates")
    L("ROU_governorates_desc", "The Prince's governors and the estates of the realm.")
    L("ROU_raise_blue_guard", "Raise the Blue Guard of Brume")
    L("ROU_raise_blue_guard_desc", "An emergency measure: Grand Brume's ceremonial corps, two divisions of leg infantry "
      "elite in their drill and poor in their arms, called out. It costs little, but Graisivaudan's loyalty falls by 20, "
      "and every other governorate's by 5: the vassals are angered.")
    dyn = "\n".join(["ROU_governorate_loyalty = {", "\ticon = GFX_idea_generic_manpower_bonus",
                     "\tenable = { is_owned_by = ROU }", "\tlocal_manpower = rou_mp_mod", "}", ""])
    write("common/dynamic_modifiers/valsora_rouental.txt", dyn)
    L("ROU_governorate_loyalty", "The Governorate's Loyalty")
    return [window_gui, entry, category], sgui, effects, sl


def main():
    texts = []

    def write(rel, content):
        p = OUT / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        texts.append(rel)

    tp_button, tp_window, tp_sgui, tp_effects, tp_sloc = three_powers(write)
    gov_windows, gov_sgui, gov_effects, gov_sloc = governorates(write)
    write("interface/valsora_rouental.gui", "guiTypes = {\n" + "\n".join([tp_button, tp_window] + gov_windows) + "\n}\n")
    write("interface/valsora_rouental.gfx", "spriteTypes = {\n" + "\n".join(SPRITES) + "\n}\n")
    write("common/scripted_guis/valsora_rouental.txt", "scripted_gui = {\n" + tp_sgui + "\n" + gov_sgui + "\n}\n")
    eff = []
    every = {**tp_effects, **gov_effects}
    first = ["ROU_tp_update", "ROU_gov_update", "ROU_gov_leanings", "ROU_gov_session_all", "ROU_gov_progress",
             "ROU_tp_shift"]   # each before the effects that call it
    for name, body in [(n, every[n]) for n in first] + [(n, b) for n, b in every.items() if n not in first]:
        eff += [f"{name} = {{", *["\t" + b for b in body], "}"]
    write("common/scripted_effects/valsora_rouental.txt", "\n".join(eff) + "\n")
    write("common/scripted_localisation/valsora_rouental.txt", "\n".join(tp_sloc + gov_sloc) + "\n")
    write("common/on_actions/valsora_rouental.txt", "\n".join([
        "on_actions = {", "\ton_startup = {", "\t\teffect = {", "\t\t\tROU = {",
        "\t\t\t\tif = {", "\t\t\t\t\tlimit = { NOT = { has_global_flag = valsora_rouental_systems } }",
        "\t\t\t\t\tROU_gov_init = yes", "\t\t\t\t\tROU_tp_init = yes",
        "\t\t\t\t\tset_global_flag = valsora_rouental_systems", "\t\t\t\t}", "\t\t\t}", "\t\t}", "\t}",
        "\ton_monthly_ROU = {", "\t\teffect = {", "\t\t\tROU_tp_trail = yes", "\t\t\tROU_tp_drift = yes", "\t\t}", "\t}",
        "}", ""]))
    p = OUT / "localisation/english/valsora_rouental_l_english.yml"
    p.write_text("\n".join(LOC) + "\n", encoding="utf-8-sig")
    print(f"rouental_ui.py: the three powers and the governorates' windows into {OUT} ({len(SPRITES)} pictures, "
          f"{len(texts) + 1} files)")


if __name__ == "__main__":
    main()
