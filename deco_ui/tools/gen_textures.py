"""Render every texture of the mod from HTML, then write DDS/TGA at exact sizes.

Each sprite is an absolutely positioned element of the exact pixel size; Playwright screenshots it
with a transparent background at device scale 1, and the PNG is converted to an uncompressed
A8R8G8B8 DDS (or TGA where vanilla uses TGA).
"""
import json
import os
import struct
import sys

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
from ddsutil import write_dds as _wd
from icons import icon as _icon

from paths import MOD, PNG, ART, BUILD, FONTS_SRC, CHROMIUM
os.makedirs(PNG, exist_ok=True)


def write_dds(img, path):
    """Uncompressed 32-bit A8R8G8B8 DDS, no mipmaps."""
    img = img.convert("RGBA")
    w, h = img.size
    a = np.array(img, dtype=np.uint8)
    bgra = a[..., [2, 1, 0, 3]].tobytes()
    flags = 0x1 | 0x2 | 0x4 | 0x8 | 0x1000
    header = struct.pack("<4sIIIIIII44s", b"DDS ", 124, flags, h, w, w * 4, 0, 0, b"\0" * 44)
    pf = struct.pack("<IIIIIIII", 32, 0x41, 0, 32, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000)
    caps = struct.pack("<IIIII", 0x1000, 0, 0, 0, 0)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(header + pf + caps + bgra)


def write_tga(img, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.convert("RGBA").save(path, compression=None)


# ---------------------------------------------------------------- shared styling
CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{background:transparent;font-family:sans-serif}
.s{position:absolute;overflow:hidden}
.lac{background:repeating-linear-gradient(90deg,rgba(255,255,255,.028) 0 1px,transparent 1px 8px),#11191E}
.lac2{background:repeating-linear-gradient(90deg,rgba(255,255,255,.03) 0 1px,transparent 1px 8px),#17222A}
.frame{position:absolute;pointer-events:none}
.ck{position:absolute;width:16px;height:16px}
.ck:before{content:"";position:absolute;inset:0;border-top:2px solid #E3C77E;border-left:2px solid #E3C77E}
.ck:after{content:"";position:absolute;left:6px;top:6px;width:6px;height:6px;border-top:2px solid #E3C77E;border-left:2px solid #E3C77E}
.ck.sm{width:10px;height:10px}.ck.sm:after{left:4px;top:4px;width:3px;height:3px;border-width:1.5px}
.ck.sm:before{border-width:1.5px}
.tl{left:2px;top:2px}.tr{right:2px;top:2px;transform:scaleX(-1)}.bl{left:2px;bottom:2px;transform:scaleY(-1)}.br{right:2px;bottom:2px;transform:scale(-1,-1)}
.gold{background:linear-gradient(180deg,#E8CD84,#8B6A2C)}
.ico{display:flex;align-items:center;justify-content:center}
svg{display:block}
"""

def chamfer(c):
    return f"polygon({c}px 0,calc(100% - {c}px) 0,100% {c}px,100% calc(100% - {c}px),calc(100% - {c}px) 100%,{c}px 100%,0 calc(100% - {c}px),0 {c}px)"



def svg(name, size=24, color="#E3C77E", sw=1.5):
    """The line icon set (tools/icons.py), as in the mockup."""
    return _icon(name, size, color, sw)


SPRITES = []  # (key, out_path_rel, w, h, html, fmt)


def add(key, rel, w, h, html, fmt="dds"):
    SPRITES.append((key, rel, w, h, html, fmt))


# ---------------------------------------------------------------- core skin: windows
def window(w, h, variant):
    raised = "lac2" if variant.get("raised") else "lac"
    lines = ""
    if variant["rule"] == "double":
        lines += '<div class="frame" style="inset:1px;border:1px solid #B8954F"></div>'
        lines += '<div class="frame" style="inset:5px;border:1px solid rgba(201,165,90,.45)"></div>'
    elif variant["rule"] == "single":
        lines += '<div class="frame" style="inset:1px;border:1px solid #B8954F"></div>'
    else:  # thin
        lines += '<div class="frame" style="inset:1px;border:1px solid rgba(184,149,79,.6)"></div>'
    corners = ""
    if variant.get("corners") == "big":
        corners = '<i class="ck tl"></i><i class="ck tr"></i><i class="ck bl"></i><i class="ck br"></i>'
    elif variant.get("corners") == "small":
        corners = '<i class="ck sm tl"></i><i class="ck sm tr"></i><i class="ck sm bl"></i><i class="ck sm br"></i>'
    shade = '<div class="frame" style="inset:0;box-shadow:inset 0 0 0 1px rgba(0,0,0,.6)"></div>'
    return f'<div class="{raised}" style="position:absolute;inset:0;opacity:.97"></div>{shade}{lines}{corners}'


WIN = {
    "gfx/interface/tiles/tiled_window.dds": dict(rule="double", corners="big"),
    "gfx/interface/tiles/tiled_window_2b_border.dds": dict(rule="double", corners="big"),
    "gfx/interface/tiles/tiled_window2_2b_border.dds": dict(rule="double", corners="big", raised=True),
    "gfx/interface/tiles/tiled_window_1b_border.dds": dict(rule="single", corners="small"),
    "gfx/interface/tiles/tiled_window2_1b_border.dds": dict(rule="single", corners="small", raised=True),
    "gfx/interface/tiles/tiled_window_1b_thin_border.dds": dict(rule="thin"),
    "gfx/interface/tiles/tiled_window_thin_border.dds": dict(rule="thin"),
    "gfx/interface/tiles/tiled_window_thin_border2.dds": dict(rule="thin", raised=True),
}
for rel, v in WIN.items():
    add("win_" + os.path.basename(rel)[:-4], rel, 192, 192, window(192, 192, v))
# main screen panels (politics, production, research, trade, diplomacy, logistics, ...): GFX_tiled_plain_bg
add("win_plain_bg", "gfx/interface/tiles/tiled_plain_bg.dds", 192, 192, window(192, 192, dict(rule="double", corners="big")))
add("win_plain_bg2", "gfx/interface/tiles/tiled_plain_bg2.dds", 182, 186, window(182, 186, dict(rule="double", corners="big")))
add("win_plain_bg_small", "gfx/interface/tiles/tiled_plain_bg_small.dds", 48, 48, window(48, 48, dict(rule="single")))
add("win_small", "gfx/interface/tiles/tiled_window_small.dds", 96, 96, window(96, 96, dict(rule="single", corners="small")))
add("win_small_small", "gfx/interface/tiles/tiled_window_small_small.dds", 48, 48, window(48, 48, dict(rule="single")))
add("mini_dialog", "gfx/interface/tiles/tiled_mini_dialog.dds", 32, 32,
    '<div class="lac" style="position:absolute;inset:0"></div><div class="frame" style="inset:0;border:1px solid #9C7A36"></div>')
# tooltip background (vanilla ToolTip textBoxType: tiles_dialog.tga, borderSize 18)
add("tooltip", "gfx/interface/tiles/tiles_dialog.tga", 64, 64,
    '<div style="position:absolute;inset:0;background:#0E1519;opacity:.96"></div>'
    '<div class="frame" style="inset:0;border:1px solid #B8954F"></div>'
    '<div class="frame" style="left:1px;right:1px;top:1px;height:2px;background:linear-gradient(90deg,#8B6A2C,#F1DC9C,#8B6A2C)"></div>'
    '<i class="ck sm tl"></i><i class="ck sm tr"></i><i class="ck sm bl"></i><i class="ck sm br"></i>', fmt="tga")

# ---------------------------------------------------------------- core skin: standard buttons
def button(w, h):
    c = max(4, min(8, h // 4))
    return (f'<div class="gold" style="position:absolute;inset:0;clip-path:{chamfer(c)}"></div>'
            f'<div style="position:absolute;inset:1px;clip-path:{chamfer(c - 0.4)};'
            'background:repeating-linear-gradient(90deg,rgba(255,255,255,.03) 0 1px,transparent 1px 7px),'
            'linear-gradient(180deg,#24323A 0%,#141D22 55%,#0E1519 100%)"></div>'
            f'<div style="position:absolute;left:{c + 2}px;right:{c + 2}px;top:2px;height:1px;background:rgba(241,220,156,.35)"></div>')


for (w, h) in [(148, 34), (221, 34), (123, 34), (261, 34), (359, 34), (223, 32), (238, 38), (211, 20), (148, 20), (372, 43), (94, 31)]:
    add(f"btn_{w}x{h}", f"gfx/interface/button_{w}x{h}.dds", w, h, button(w, h))

# ---------------------------------------------------------------- top bar (v2: the mockup's layout)
import layout as L

D = "gfx/interface/valsora_deco/"
LAC = "repeating-linear-gradient(90deg,rgba(255,255,255,.025) 0 1px,transparent 1px 7px)"
GOLD_V = "linear-gradient(180deg,#E8CD84,#8B6A2C)"


def poly(points):
    return "polygon(" + ",".join(f"{x}px {y}px" for x, y in points) + ")"


def inset_poly(points, d=1.0):
    """Shrink a simple orthogonal/diagonal polygon by d px (centroid-free: offset each edge inward)."""
    import math
    n = len(points)
    # signed area -> orientation
    area = sum(points[i][0] * points[(i + 1) % n][1] - points[(i + 1) % n][0] * points[i][1] for i in range(n))
    s = 1 if area > 0 else -1
    lines = []
    for i in range(n):
        (x1, y1), (x2, y2) = points[i], points[(i + 1) % n]
        dx, dy = x2 - x1, y2 - y1
        ln = math.hypot(dx, dy)
        nx, ny = -dy / ln * s, dx / ln * s          # inward normal
        lines.append(((x1 + nx * d, y1 + ny * d), (dx, dy)))
    out = []
    for i in range(n):
        (p1, d1), (p2, d2) = lines[i - 1], lines[i]
        den = d1[0] * d2[1] - d1[1] * d2[0]
        if abs(den) < 1e-9:
            out.append(p2)
            continue
        tt = ((p2[0] - p1[0]) * d2[1] - (p2[1] - p1[1]) * d2[0]) / den
        out.append((round(p1[0] + d1[0] * tt, 2), round(p1[1] + d1[1] * tt, 2)))
    return out


def plate(points, fill, rim=GOLD_V, d=1.0):
    return (f'<div style="position:absolute;inset:0;background:{rim};clip-path:{poly(points)}"></div>'
            f'<div style="position:absolute;inset:0;background:{LAC},{fill};clip-path:{poly(inset_poly(points, d))}"></div>')


# 1. band: stretched to the screen width by a corneredTile container background; the soft shadow under
#    it is a second, click-through container so the band only blocks clicks where it is drawn
add("tb_band", D + "topbar_band.dds", 196, L.BAND_TEX_H,
    f'<div style="position:absolute;left:0;right:0;top:0;height:{L.BAND_H}px;background:{LAC},linear-gradient(180deg,#1A252C,#0D1418)"></div>'
    f'<div style="position:absolute;left:0;right:0;top:{L.BAND_H}px;height:1px;background:#C9A55A"></div>'
    f'<div style="position:absolute;left:0;right:0;top:{L.BAND_H + 1}px;height:3px;background:#0B1014"></div>'
    f'<div style="position:absolute;left:0;right:0;top:{L.BAND_H + 4}px;height:1px;background:rgba(201,165,90,.45)"></div>'
    f'<div style="position:absolute;left:0;right:0;top:{L.BAND_H + 5}px;bottom:0;background:rgba(0,0,0,.42)"></div>')
add("tb_band_shadow", D + "topbar_band_shadow.dds", 16, L.SHADOW_H,
    '<div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.36),rgba(0,0,0,0))"></div>')

# 2. flag medallion (replaces the vanilla left plate): stepped plate, framed native-size flag with
#    deco "speed line" wings, room for a one- or two-line name
W, H = L.MED["w"], L.MED["h"]
s1, s2 = L.MED_STEPS
sx = lambda f: round(W * f, 2)
med = [(0, -2), (W, -2), (W, s1), (sx(.88), s1), (sx(.88), s2), (sx(.74), s2), (sx(.74), H),
       (sx(.26), H), (sx(.26), s2), (sx(.12), s2), (sx(.12), s1), (0, s1)]
F, FR = L.FLAG, L.FLAG_FRAME
fx, fy = FR["x"] - L.MED["x"], FR["y"] - L.MED["y"]
cy = fy + FR["h"] / 2
wings = ""
for dy, ln in [(-6, 18), (0, 13), (6, 8)]:
    for side in (0, 1):
        x = fx - 5 - ln if side == 0 else fx + FR["w"] + 5
        grad = "90deg,transparent,#C9A55A" if side == 0 else "90deg,#C9A55A,transparent"
        wings += f'<div style="position:absolute;left:{x}px;top:{cy + dy}px;width:{ln}px;height:1px;background:linear-gradient({grad})"></div>'
add("tb_medallion", D + "topbar_medallion.dds", W, H,
    plate(med, "linear-gradient(180deg,#1B262D,#0C1317)", "linear-gradient(180deg,#8B6A2C,#E8CD84 40%,#8B6A2C)")
    # frame: outer gilt hairline, lacquer mat, inner gilt 2px, dark flag bed
    + f'<div style="position:absolute;left:{fx}px;top:{fy}px;width:{FR["w"]}px;height:{FR["h"]}px;background:#C9A55A;box-shadow:0 4px 10px rgba(0,0,0,.55)"></div>'
    + f'<div style="position:absolute;left:{fx + 1}px;top:{fy + 1}px;width:{FR["w"] - 2}px;height:{FR["h"] - 2}px;background:{LAC},linear-gradient(180deg,#16212A,#0B1115)"></div>'
    + f'<div style="position:absolute;left:{fx + 6}px;top:{fy + 6}px;width:{F["w"] + 4}px;height:{F["h"] + 4}px;background:linear-gradient(180deg,#F1DC9C,#9C7A36)"></div>'
    + f'<div style="position:absolute;left:{fx + 8}px;top:{fy + 8}px;width:{F["w"]}px;height:{F["h"]}px;background:#0B1014"></div>'
    # small diamonds at the mat's corners
    + "".join(f'<div style="position:absolute;left:{x - 2}px;top:{y - 2}px;width:4px;height:4px;background:#E3C77E;transform:rotate(45deg)"></div>'
              for x, y in [(fx + 3, fy + 3), (fx + FR["w"] - 3, fy + 3), (fx + 3, fy + FR["h"] - 3), (fx + FR["w"] - 3, fy + FR["h"] - 3)])
    + wings)

# flag: own 82x52 masked shield, so the game's flag is drawn 1:1 (no stretching)
add("flag_mask", D + "flag_mask.tga", F["w"], F["h"], '<div style="position:absolute;inset:0;background:#fff"></div>', fmt="tga")
add("flag_overlay", D + "flag_overlay.dds", F["w"], F["h"],
    '<div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(255,255,255,.10),rgba(255,255,255,0) 45%,rgba(0,0,0,0) 70%,rgba(0,0,0,.08))"></div>')

# 3. v0.4: the seal hanging under the medallion is the DECISIONS button (2 frames like vanilla's)
oct_ = lambda s, c: [(c, 0), (s - c, 0), (s, c), (s, s - c), (s - c, s), (c, s), (0, s - c), (0, c)]
S_ = L.SEAL["w"]


def seal(lit):
    fill = "radial-gradient(circle,#3A8574 0%,#163A32 72%)" if lit else "radial-gradient(circle,#2E6E60 0%,#10241F 72%)"
    rim = "linear-gradient(180deg,#FFF3C8,#B48F44)" if lit else GOLD_V
    return (plate(oct_(S_, 12), fill, rim, 1.2)
            + f'<div style="position:absolute;inset:0;clip-path:{poly(inset_poly(oct_(S_, 12), 1.2))};background:repeating-conic-gradient(from 0deg,rgba(227,199,126,.30) 0deg 6deg,transparent 6deg 15deg);-webkit-mask:radial-gradient(circle,transparent 0 34%,#000 62%)"></div>'
            + f'<div style="position:absolute;left:5px;top:5px;right:5px;bottom:5px;clip-path:{poly(inset_poly(oct_(S_ - 10, 9), 0))};box-shadow:inset 0 0 0 1px rgba(227,199,126,.45)"></div>'
            + f'<div class="ico" style="position:absolute;inset:0">{svg("decisions", 24, "#FBEAB4" if lit else "#E3C77E")}</div>')


add("tb_decisions_seal", D + "decisions_seal.dds", 2 * S_, S_,
    f'<div style="position:absolute;left:0;top:0;width:{S_}px;height:{S_}px">{seal(False)}</div>'
    f'<div style="position:absolute;left:{S_}px;top:0;width:{S_}px;height:{S_}px">{seal(True)}</div>')

# decisions alert glows: the game swaps GFX_decisions_glow / _blue / _yellow / _green on the decisions
# button, so the vanilla textures are replaced at their paths with octagonal halos sized to the seal
GS = S_ + 2 * L.SEAL_GLOW


def halo(rgb, strength):
    r, g, b = rgb
    o = oct_(GS, 15)
    return (f'<div style="position:absolute;inset:0;clip-path:{poly(o)};'
            f'background:radial-gradient(circle,rgba({r},{g},{b},{strength}) 52%,rgba({r},{g},{b},0) 72%)"></div>'
            f'<div style="position:absolute;left:{L.SEAL_GLOW - 2}px;top:{L.SEAL_GLOW - 2}px;width:{S_ + 4}px;height:{S_ + 4}px;'
            f'clip-path:{poly(oct_(S_ + 4, 13))};background:rgba({r},{g},{b},{min(1, strength + .25)})"></div>')


for suffix, rgb in [("", (238, 140, 126)), ("_blue", (110, 150, 230)), ("_yellow", (231, 183, 90)), ("_green", (120, 200, 160))]:
    add("dec_glow" + suffix, f"gfx/interface/decisionview/decisions_glow{suffix}.dds", 2 * GS, GS,
        f'<div style="position:absolute;left:0;top:0;width:{GS}px;height:{GS}px">{halo(rgb, .35)}</div>'
        f'<div style="position:absolute;left:{GS}px;top:0;width:{GS}px;height:{GS}px">{halo(rgb, .7)}</div>')

# 4. crown buttons (menu row + army/navy/air): frame 1 normal, frame 2 lit
def crown(w, h, icon, lit, c=9):
    pts = [(c, 0), (w - c, 0), (w, c), (w, h), (0, h), (0, c)]
    fill = "linear-gradient(180deg,#2E6E60,#153730)" if lit else "linear-gradient(180deg,#1E2930,#0E1519)"
    rim = "linear-gradient(180deg,#FFF3C8,#B48F44)" if lit else GOLD_V
    return (plate(pts, fill, rim)
            # army/navy/air (40 px tall) carry an experience badge on their lower edge: icon sits higher
            + (f'<div class="ico" style="position:absolute;inset:0">{svg(icon, 24, "#FBEAB4" if lit else "#E3C77E", 1.5)}</div>'
               if h >= 46 else
               f'<div class="ico" style="position:absolute;inset:0;padding-bottom:12px">{svg(icon, 22, "#FBEAB4" if lit else "#E3C77E", 1.5)}</div>'))


def two_frames(w, h, f):
    return (f'<div style="position:absolute;left:0;top:0;width:{w}px;height:{h}px">{f(False)}</div>'
            f'<div style="position:absolute;left:{w}px;top:0;width:{w}px;height:{h}px">{f(True)}</div>')


TB = {"intelligence": "intel", "technology": "research", "diplomacy": "diplomacy",
      "trade": "trade", "construction": "construction", "production": "production", "deployment": "deploy",
      "logistics": "logistics", "officer": "officer"}
for k, ic in TB.items():
    add("tb_" + k, D + f"button_{k}.dds", 2 * L.BTN_W, L.BTN_H, two_frames(L.BTN_W, L.BTN_H, lambda lit, ic=ic: crown(L.BTN_W, L.BTN_H, ic, lit)))
# faction (first crown): the game swaps GFX_topbar_faction_empty / GFX_topbar_faction on this button, so
# the vanilla textures are replaced at their paths (1 frame each, like vanilla). In a faction the faction's
# logo is drawn over the centre, so that version shows an empty medallion ring instead of the icon.
def faction_crown(in_faction):
    w, h, c = L.BTN_W, L.BTN_H, 9
    pts = [(c, 0), (w - c, 0), (w, c), (w, h), (0, h), (0, c)]
    inner = (f'<div style="position:absolute;left:{w / 2 - 17}px;top:{h / 2 - 15}px;width:34px;height:34px;border-radius:50%;'
             'box-shadow:inset 0 0 0 1px rgba(227,199,126,.55);background:radial-gradient(circle,#18262B,#0B1115)"></div>'
             if in_faction else f'<div class="ico" style="position:absolute;inset:0">{svg("faction", 24)}</div>')
    return plate(pts, "linear-gradient(180deg,#1E2930,#0E1519)") + inner


add("tb_faction_empty", "gfx/interface/factions/ui/topbar_faction_empty.dds", L.BTN_W, L.BTN_H, faction_crown(False))
add("tb_faction", "gfx/interface/factions/ui/topbar_faction.dds", L.BTN_W, L.BTN_H, faction_crown(True))
# production alert glow (vanilla used the decisions' yellow glow there): own crown-shaped halo, 2 frames
CG = 8


def crown_halo(a):
    w, h, c = L.BTN_W + 2 * CG, L.BTN_H + 2 * CG, 14
    pts = [(c, 0), (w - c, 0), (w, c), (w, h), (0, h), (0, c)]
    return (f'<div style="position:absolute;inset:0;clip-path:{poly(pts)};'
            f'background:radial-gradient(ellipse at 50% 50%,rgba(231,183,90,{a}) 50%,rgba(231,183,90,0) 75%)"></div>')


add("tb_crown_glow", D + "crown_glow.dds", 2 * (L.BTN_W + 2 * CG), L.BTN_H + 2 * CG,
    f'<div style="position:absolute;left:0;top:0;width:{L.BTN_W + 2 * CG}px;height:{L.BTN_H + 2 * CG}px">{crown_halo(.35)}</div>'
    f'<div style="position:absolute;left:{L.BTN_W + 2 * CG}px;top:0;width:{L.BTN_W + 2 * CG}px;height:{L.BTN_H + 2 * CG}px">{crown_halo(.75)}</div>')
# the game swaps its own sprites onto the diplomacy button at runtime (GFX_topbar_international_market, and
# possibly GFX_topbar_diplomacy), so both vanilla textures are replaced at their paths: 2 frames like vanilla
add("tb_market_vanilla", "gfx/interface/topbar/toolbar/international_market_button.dds", 2 * L.BTN_W, L.BTN_H,
    two_frames(L.BTN_W, L.BTN_H, lambda lit: crown(L.BTN_W, L.BTN_H, "market", lit)))
add("tb_diplomacy_vanilla", "gfx/interface/topbar/toolbar/diplomacy_button.dds", 2 * L.BTN_W, L.BTN_H,
    two_frames(L.BTN_W, L.BTN_H, lambda lit: crown(L.BTN_W, L.BTN_H, "diplomacy", lit)))
for k in ["army", "navy", "air"]:
    add("ov_" + k, D + f"overview_{k}.dds", 2 * L.OVERVIEW_W, L.OVERVIEW_H,
        two_frames(L.OVERVIEW_W, L.OVERVIEW_H, lambda lit, k=k: crown(L.OVERVIEW_W, L.OVERVIEW_H, k, lit, 8)))

# 5. readout dividers, hit areas, icons
add("tb_divider", D + "divider.dds", 1, L.DIV_H,
    '<div style="position:absolute;inset:0;background:linear-gradient(180deg,transparent,#C9A55A 30%,#C9A55A 70%,transparent)"></div>')
HIT = sorted({(it["w"], 46) for it in L.STRIP} | {(it["w"], 30) for it in L.SECONDARY})
for (w, h) in HIT:
    add(f"hit_{w}x{h}", D + f"hit_{w}x{h}.dds", w, h, '<div style="position:absolute;inset:0;background:rgba(0,0,0,0)"></div>')
add("clear", D + "clear.dds", 8, 8, '<div style="position:absolute;inset:0;background:rgba(0,0,0,0)"></div>')
add("none", D + "none.dds", 2, 2, '<div style="position:absolute;inset:0;background:rgba(0,0,0,0)"></div>')
# badge plate (experience on the army/navy/air buttons): corneredTile so it can stretch
add("badge", D + "badge.dds", 16, 15,
    '<div style="position:absolute;inset:0;background:linear-gradient(180deg,#141D22,#0A0F12);box-shadow:inset 0 0 0 1px #C9A55A"></div>')

for k in ["pp", "stability", "war", "manpower"]:
    add("ic_" + k, D + f"icon_{k}.dds", 24, 24, f'<div class="ico" style="position:absolute;inset:0">{svg(k, 24, "#E3C77E", 1.4)}</div>')
add("ic_factory", D + "icon_factory.dds", 48, 24,
    f'<div class="ico" style="position:absolute;left:0;top:0;width:24px;height:24px">{svg("factory", 24, "#E3C77E", 1.4)}</div>'
    f'<div class="ico" style="position:absolute;left:24px;top:0;width:24px;height:24px">{svg("factory", 24, "#E7A24A", 1.4)}</div>')
T = L.TRAY_ICON
for k, ic in [("convoy", "convoy"), ("command", "command"), ("nuke", "nuke")]:
    add("ic_" + k, D + f"icon_{k}.dds", T, T, f'<div class="ico" style="position:absolute;inset:0">{svg(ic, T, "#E3C77E", 1.6)}</div>')
add("ic_fuel", D + "icon_fuel.dds", 3 * T, T, "".join(
    f'<div class="ico" style="position:absolute;left:{i * T}px;top:0;width:{T}px;height:{T}px">{svg("fuel", T, col, 1.6)}</div>'
    for i, col in enumerate(["#E3C77E", "#E7B75A", "#EE8C7E"])))

# ratio bars: the game draws the fill texture as-is (v0.2's tint colours were ignored in-game)
add("ratio_fill", D + "ratio_fill.dds", L.BAR_W, L.BAR_H, '<div style="position:absolute;inset:0;background:linear-gradient(180deg,#F1DC9C,#B48F44)"></div>')
add("ratio_bg", D + "ratio_bg.dds", L.BAR_W, L.BAR_H, '<div style="position:absolute;inset:0;background:#2A363D"></div>')

# 6. logistics tray hanging under the strip (fuel, supply, convoys)
TW, TH = L.TRAY["w"], L.TRAY["h"]
tray = [(0, -1), (TW, -1), (TW, 18), (TW - 10, 18), (TW - 10, TH), (10, TH), (10, 18), (0, 18)]
seps = "".join(f'<div style="position:absolute;left:{x - L.TRAY["x"]}px;top:{L.SEC_Y - L.TRAY["y"] + 5}px;width:1px;height:20px;'
               'background:linear-gradient(180deg,transparent,rgba(201,165,90,.8) 30%,rgba(201,165,90,.8) 70%,transparent)"></div>'
               for x in L.TRAY_SEPS)
add("tb_tray", D + "tray.dds", TW, TH, plate(tray, "linear-gradient(180deg,#141E24,#0B1115)") + seps)

# 7. date cartouche: pause diamond baked in; paused version pulses (2 frames)
CW, CH = L.CART["w"], L.CART["h"]
cart = [(16, 0), (CW - 16, 0), (CW, CH / 2), (CW - 16, CH), (16, CH), (0, CH / 2)]


def cartouche(fill, glyph, ring="#C9A55A", dfill="#0B1014", glow=""):
    px, py = L.PAUSE_C
    return (plate(cart, fill)
            + f'<div style="position:absolute;left:{px - 13}px;top:{py - 13}px;width:26px;height:26px;transform:rotate(45deg);'
              f'border:1px solid {ring};background:{dfill};box-sizing:border-box;{glow}"></div>'
            + f'<svg width="12" height="12" viewBox="0 0 12 12" style="position:absolute;left:{px - 6}px;top:{py - 6}px">{glyph}</svg>')


PAUSE = '<path d="M3.5 2v8M8.5 2v8" stroke="#E3C77E" stroke-width="2"/>'
PLAY = '<path d="M3.5 1.5v9l7-4.5z" fill="#F1DC9C"/>'
NORMAL = "linear-gradient(180deg,#1E2930,#0D1418)"
add("date_bg", D + "date_bg.dds", CW, CH, cartouche(NORMAL, PAUSE))
add("date_paused", D + "date_paused.dds", 2 * CW, CH,
    f'<div style="position:absolute;left:0;top:0;width:{CW}px;height:{CH}px">{cartouche(NORMAL, PLAY, "#E7B75A")}</div>'
    f'<div style="position:absolute;left:{CW}px;top:0;width:{CW}px;height:{CH}px">'
    f'{cartouche("linear-gradient(180deg,#4A3612,#24190A)", PLAY, "#F1D08A", "#2A1E0A", "box-shadow:0 0 8px rgba(231,183,90,.6)")}</div>')

# speed chevrons: 3 frames (off | on | bright), and the +/- buttons
add("speed_step", D + "speed_step.dds", 3 * L.CHEV_W, L.CHEV_H, "".join(
    f'<svg width="{L.CHEV_W}" height="{L.CHEV_H}" viewBox="0 0 12 18" style="position:absolute;left:{i * L.CHEV_W}px;top:0">'
    f'<path d="M2.5 2l7 7-7 7" fill="none" stroke="{col}" stroke-width="2.4"/></svg>'
    for i, col in enumerate(["#4A4434", "#F1DC9C", "#FFF6D6"])))
for k, glyph in [("speed_down", '<path d="M7 7.5h8"/>'), ("speed_up", '<path d="M7 7.5h8M11 3.5v8"/>')]:
    add(k, D + f"{k}.dds", L.PM_W, L.PM_H,
        '<div style="position:absolute;inset:0;border:1px solid rgba(201,165,90,.6);background:#0B1014"></div>'
        f'<svg width="{L.PM_W}" height="{L.PM_H}" viewBox="0 0 22 15" fill="none" stroke="#E3C77E" stroke-width="1.6" style="position:absolute;left:0;top:0">{glyph}</svg>')

# 8. right-hand plate: hanging tray (army/navy/air, music, achievements, alerts) + world tension ring
RW, RH = L.RPLATE["w"], L.RPLATE["h"]
tx0 = L.RTRAY["x"] - L.RPLATE["x"]
ty0, ty1 = L.RTRAY["y"], L.RTRAY["y"] + L.RTRAY["h"]
rtray = [(tx0, ty0 - 1), (RW + 2, ty0 - 1), (RW + 2, ty1), (tx0 + 12, ty1), (tx0 + 12, ty0 + 24), (tx0, ty0 + 24)]
cx, cy, r = L.WT_C[0] - L.RPLATE["x"], L.WT_C[1] - L.RPLATE["y"], L.WT_R
ring = (f'<div style="position:absolute;left:{cx - r - 4}px;top:{cy - r - 4}px;width:{2 * r + 8}px;height:{2 * r + 8}px;border-radius:50%;'
        'background:repeating-conic-gradient(from 0deg,rgba(227,199,126,.5) 0deg 2deg,transparent 2deg 15deg);'
        '-webkit-mask:radial-gradient(circle,transparent 0 86%,#000 87%)"></div>'
        f'<div style="position:absolute;left:{cx - r}px;top:{cy - r}px;width:{2 * r}px;height:{2 * r}px;border-radius:50%;'
        'background:linear-gradient(180deg,#E8CD84,#8B6A2C);box-shadow:0 4px 10px rgba(0,0,0,.5)"></div>'
        f'<div style="position:absolute;left:{cx - r + 2}px;top:{cy - r + 2}px;width:{2 * r - 4}px;height:{2 * r - 4}px;border-radius:50%;'
        f'background:radial-gradient(circle,#1B262D,#0B1115)"></div>'
        f'<div style="position:absolute;left:{cx - r + 5}px;top:{cy - r + 5}px;width:{2 * r - 10}px;height:{2 * r - 10}px;border-radius:50%;'
        'box-shadow:inset 0 0 0 1px rgba(201,165,90,.45)"></div>')
rseps = "".join(f'<div style="position:absolute;left:{x - L.RPLATE["x"]}px;top:{ty0 + 12}px;width:1px;height:22px;'
                'background:linear-gradient(180deg,transparent,rgba(201,165,90,.8) 30%,rgba(201,165,90,.8) 70%,transparent)"></div>'
                for x in L.RTRAY_SEPS)
add("tb_right", D + "topbar_right.dds", RW, RH, plate(rtray, "linear-gradient(180deg,#141E24,#0B1115)") + rseps + ring)

# small restyled vanilla buttons (single frame + buttonstate like vanilla)
def chip_button(w, h, icon, size):
    pts = [(5, 0), (w, 0), (w, h - 5), (w - 5, h), (0, h), (0, 5)]
    return plate(pts, "linear-gradient(180deg,#1E2930,#0E1519)") + f'<div class="ico" style="position:absolute;inset:0">{svg(icon, size, "#E3C77E", 1.6)}</div>'


add("btn_menu", D + "menu_button.dds", L.MENU_BTN["w"], L.MENU_BTN["h"], chip_button(L.MENU_BTN["w"], L.MENU_BTN["h"], "menu", 18))
add("btn_help", D + "help_button.dds", L.HELP_BTN["w"], L.HELP_BTN["h"], chip_button(L.HELP_BTN["w"], L.HELP_BTN["h"], "help", 18))
add("btn_playlist", D + "playlist_button.dds", L.PLAYLIST["w"], L.PLAYLIST["h"], chip_button(L.PLAYLIST["w"], L.PLAYLIST["h"], "music", 16))

# ---------------------------------------------------------------- politics screen (v0.4: the Government mockup)
import layout_politics as LP

P = "gfx/interface/valsora_deco/politics/"
RULE = "linear-gradient(90deg,#C9A55A,rgba(201,165,90,.15))"


def hrule(x, y, w, grad=RULE, h=1):
    return f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{grad}"></div>'


def dbl_rule(x, y, w):
    """The mockup's section rule: a 5px band between two hairlines (strong on top, faint below)."""
    return (hrule(x, y, w, "linear-gradient(90deg,rgba(201,165,90,.55),rgba(201,165,90,.25))")
            + hrule(x, y + 4, w, "linear-gradient(90deg,rgba(201,165,90,.25),rgba(201,165,90,.08))"))


def sunburst(cx, cy, r, alpha=.28, inner=.30):
    return (f'<div style="position:absolute;left:{cx - r}px;top:{cy - r}px;width:{2 * r}px;height:{2 * r}px;border-radius:50%;'
            f'background:repeating-conic-gradient(rgba(227,199,126,{alpha}) 0deg 3deg,transparent 3deg 11deg);'
            f'-webkit-mask:radial-gradient(circle,#000 {int(inner * 100)}%,transparent 70%)"></div>')


def diamond_icon(cx, cy, icon_name, d=26):
    """A law card's icon: lacquer diamond with a gilt hairline, icon upright inside."""
    return (f'<div style="position:absolute;left:{cx - d / 2}px;top:{cy - d / 2}px;width:{d}px;height:{d}px;transform:rotate(45deg);'
            f'background:#0B1014;box-shadow:inset 0 0 0 1px rgba(201,165,90,.7)"></div>'
            f'<div style="position:absolute;left:{cx - 9}px;top:{cy - 9}px;width:18px;height:18px">{svg(icon_name, 18)}</div>')


# section art under everything (replaces the vanilla pol_view_bg)
SEC = ""
# header: jade wash, double rule under it
SEC += (f'<div style="position:absolute;left:0;top:0;width:{LP.PANEL_W}px;height:{LP.HEAD_GLOW_H}px;'
        'background:linear-gradient(180deg,rgba(46,110,96,.22),rgba(46,110,96,0))"></div>')
SEC += hrule(LP.X0 - 12, LP.HEAD_RULE_Y, LP.X1 - LP.X0 + 24, "linear-gradient(90deg,rgba(201,165,90,.1),#C9A55A 12%,#C9A55A 88%,rgba(201,165,90,.1))")
# sunburst behind the portrait
SB = LP.SUNBURST
SEC += sunburst(SB["cx"], SB["cy"], SB["r"])
# ideology chip
C = LP.CHIP
SEC += f'<div style="position:absolute;left:{C["x"]}px;top:{C["y"]}px;width:{C["w"]}px;height:{C["h"]}px;box-shadow:inset 0 0 0 1px rgba(201,165,90,.45)"></div>'
# a faint divider between the two grid columns
gx = LP.GRID_X[1] - 6
SEC += (f'<div style="position:absolute;left:{gx}px;top:{LP.GRID_LABEL_Y[0]}px;width:1px;height:{LP.GRID_VALUE_Y[1] + LP.GRID_VALUE_H - LP.GRID_LABEL_Y[0]}px;'
        'background:linear-gradient(180deg,transparent,rgba(201,165,90,.35) 20%,rgba(201,165,90,.35) 80%,transparent)"></div>')
# description: rules above and below
D_ = LP.DESC
SEC += hrule(D_["x"], D_["y"], D_["w"], "rgba(201,165,90,.28)") + hrule(D_["x"], D_["y"] + D_["h"], D_["w"], "rgba(201,165,90,.28)")
# section rules after each label (label widths measured from the generated font)
for key, (x, y, text) in LP.SECTION_LABELS.items():
    lw = L.measure("valsora_deco_section_11", text.upper())
    x0 = x + lw + 12
    SEC += dbl_rule(x0, y + 3, LP.SECTION_ENDS[key] - x0)
# law cards (icons are static; the law names are a scripted GUI)
for i, (key, ic) in enumerate(LP.LAW_CARDS):
    y = LP.LAW_Y0 + i * (LP.LAW_H + LP.LAW_GAP)
    SEC += (f'<div style="position:absolute;left:{LP.LAWS_X}px;top:{y}px;width:{LP.LAWS_W}px;height:{LP.LAW_H}px;'
            'box-shadow:inset 0 0 0 1px rgba(201,165,90,.35);background:linear-gradient(90deg,rgba(201,165,90,.08),rgba(201,165,90,0))"></div>')
    SEC += diamond_icon(LP.LAWS_X + 20, y + LP.LAW_H / 2, ic, 21)
# national spirits band (mockup: gilt-edged card with a warm wash)
S_ = LP.SPIRITS
SEC += (f'<div style="position:absolute;left:{S_["x"]}px;top:{S_["y"]}px;width:{S_["w"]}px;height:{S_["h"]}px;'
        'background:linear-gradient(90deg,rgba(122,42,38,.28),rgba(122,42,38,0) 70%),rgba(6,10,12,.35);box-shadow:inset 0 0 0 1px rgba(201,165,90,.45)"></div>')
add("pol_sections", P + "pol_sections.dds", LP.PANEL_W, LP.IDEAS_Y, SEC)

# arched portrait frame: lacquer outside the arch hides the portrait's top corners; the sunburst continues
# across the lacquer so the frame sits on it seamlessly
FW, FH = LP.FRAME["w"], LP.FRAME["h"]
r_ = (FW - 16) / 2
inner = f"M8 {FH - 8} L8 {8 + r_} A{r_} {r_} 0 0 1 {FW - 8} {8 + r_} L{FW - 8} {FH - 8} Z"
rim1 = f"M2.5 {FH - 2.5} L2.5 {8 + r_} A{r_ + 5.5} {r_ + 5.5} 0 0 1 {FW - 2.5} {8 + r_} L{FW - 2.5} {FH - 2.5} Z"
rim2 = f"M6.5 {FH - 6.5} L6.5 {8 + r_} A{r_ + 1.5} {r_ + 1.5} 0 0 1 {FW - 6.5} {8 + r_} L{FW - 6.5} {FH - 6.5} Z"
sbx, sby = SB["cx"] - LP.FRAME["x"], SB["cy"] - LP.FRAME["y"]
add("pol_frame", P + "portrait_frame.dds", FW, FH,
    # panel-coloured lacquer + the same sunburst, clipped to the area outside the arch
    f'<div style="position:absolute;inset:0;clip-path:path(evenodd,\'M0 0H{FW}V{FH}H0Z {inner}\');background:{LAC},linear-gradient(180deg,#18232A,#111A1F)">'
    f'{sunburst(sbx, sby, SB["r"])}</div>'
    f'<svg width="{FW}" height="{FH}" style="position:absolute;left:0;top:0"><defs>'
    '<linearGradient id="gilt" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F6E3A6"/><stop offset="1" stop-color="#8B6A2C"/></linearGradient></defs>'
    f'<path d="{rim1}" fill="none" stroke="#B8954F" stroke-width="1"/>'
    f'<path d="{rim2}" fill="none" stroke="url(#gilt)" stroke-width="3"/>'
    f'<path d="M{FW / 2 - 5} 4.5 l5 -3.5 5 3.5 -5 3.5z" fill="#E3C77E"/></svg>')
RW_, RH_ = LP.RIBBON["w"], LP.RIBBON["h"]
add("pol_ribbon", P + "ribbon.dds", RW_, RH_,
    plate([(8, 0), (RW_ - 8, 0), (RW_, RH_ / 2), (RW_ - 8, RH_), (8, RH_), (0, RH_ / 2)], "linear-gradient(180deg,#F3DFA0,#B48F44)",
          "linear-gradient(180deg,#FFF3C8,#8B6A2C)"))

# close: gilt diamond with a cross (single frame + buttonstate)
CW_ = LP.CLOSE["w"]
add("pol_close", P + "close.dds", CW_, CW_,
    f'<div style="position:absolute;left:{CW_ / 2 - 11.5}px;top:{CW_ / 2 - 11.5}px;width:23px;height:23px;transform:rotate(45deg);border:1px solid #E3C77E;background:#0B1014;box-sizing:border-box"></div>'
    f'<svg width="{CW_}" height="{CW_}" viewBox="0 0 {CW_} {CW_}" style="position:absolute;left:0;top:0"><path d="M{CW_ / 2 - 4.5} {CW_ / 2 - 4.5}l9 9M{CW_ / 2 + 4.5} {CW_ / 2 - 4.5}l-9 9" stroke="#E3C77E" stroke-width="1.6"/></svg>')
add("pol_close_small", P + "close_small.dds", 20, 20,
    '<svg width="20" height="20" viewBox="0 0 20 20" style="position:absolute;left:0;top:0"><path d="M6 6l8 8M14 6l-8 8" stroke="#E3C77E" stroke-width="1.6"/></svg>')

# popularity: gilt ring + donut hole over the game's pie (the pie is the mod's own larger pieChartType)
PR = LP.PIE["r"] + LP.PIE_RING
D2 = 2 * PR
hole = round(LP.PIE["r"] * .66)
add("pol_pie_ring", P + "pie_ring.dds", D2, D2,
    f'<div style="position:absolute;left:{LP.PIE_RING - 2}px;top:{LP.PIE_RING - 2}px;width:{D2 - 2 * LP.PIE_RING + 4}px;height:{D2 - 2 * LP.PIE_RING + 4}px;border-radius:50%;'
    'box-shadow:inset 0 0 0 2px #0B1014"></div>'
    f'<div style="position:absolute;left:0;top:0;width:{D2}px;height:{D2}px;border-radius:50%;box-shadow:inset 0 0 0 2px #D2B064"></div>'
    f'<div style="position:absolute;left:{PR - hole / 2}px;top:{PR - hole / 2}px;width:{hole}px;height:{hole}px;border-radius:50%;'
    'background:radial-gradient(circle,#16212A,#0B1115);box-shadow:0 0 0 1.5px #D2B064"></div>')
# legend: diamond swatch (white: the game tints it with the party colour), its gilt hairline, the leading-party wash
add("pol_party_diamond", P + "party_diamond.dds", 12, 12,
    '<div style="position:absolute;left:2px;top:2px;width:8px;height:8px;transform:rotate(45deg);background:#fff"></div>')
add("pol_party_swatch_bg", P + "party_swatch_bg.dds", 16, 16,
    '<div style="position:absolute;left:3px;top:3px;width:10px;height:10px;transform:rotate(45deg);box-shadow:0 0 0 1px rgba(227,199,126,.8);background:#0B1014"></div>')
add("pol_party_lead", P + "party_lead.dds", LP.LEGEND["w"], LP.LEGEND["row"],
    '<div style="position:absolute;inset:0;background:linear-gradient(90deg,rgba(201,165,90,.20),rgba(201,165,90,0))"></div>')

# faction card (the game's faction button, 3 frames: 1 member, 2 create, 3 dim)
FCW, FCH = LP.FACTION_CARD["w"], LP.FACTION_CARD["h"]


def fcard(fill, dashed=False):
    pts = [(10, 0), (FCW, 0), (FCW, FCH - 10), (FCW - 10, FCH), (0, FCH), (0, 10)]
    extra = (f'<div style="position:absolute;left:6px;top:6px;right:6px;bottom:6px;border:1px dashed rgba(201,165,90,.45)"></div>' if dashed else "")
    return plate(pts, fill, "linear-gradient(180deg,#E8CD84,#8B6A2C)") + extra


add("pol_faction_card", P + "faction_card.dds", 3 * FCW, FCH, "".join(
    f'<div style="position:absolute;left:{i * FCW}px;top:0;width:{FCW}px;height:{FCH}px">{fcard(f, d)}</div>'
    for i, (f, d) in enumerate([("linear-gradient(180deg,#24564C,#11302A)", False), ("linear-gradient(180deg,#1A252C,#0E1519)", True),
                                ("linear-gradient(180deg,#161D21,#0B1014)", False)])))

# national focus card (the game's focus button, 3 frames like vanilla: normal, hover, disabled): octagonal
# jade medallion behind the focus picture, the progress track, gilt-cornered plate
GW, GH = LP.FOCUS_CARD["w"], LP.FOCUS_CARD["h"]
ocx, ocy, orad = LP.FOCUS_ICON["cx"], LP.FOCUS_ICON["cy"], 32
octo = [(ocx + orad * x, ocy + orad * y) for x, y in [(-.41, -1), (.41, -1), (1, -.41), (1, .41), (.41, 1), (-.41, 1), (-1, .41), (-1, -.41)]]
FB = LP.FOCUS_BAR


def focus_card(fill, rim, dim=0.0):
    return (plate([(0, 0), (GW - 12, 0), (GW, 12), (GW, GH), (12, GH), (0, GH - 12)], fill, rim)
            + plate(octo, "radial-gradient(circle,#2E6E60 0%,#10241F 70%)", GOLD_V, 1.2)
            + f'<div style="position:absolute;left:0;top:0;width:{GW}px;height:{GH}px;clip-path:{poly(inset_poly(octo, 1.2))};'
              f'background:repeating-conic-gradient(from 0deg at {ocx}px {ocy}px,rgba(227,199,126,.30) 0deg 6deg,transparent 6deg 15deg)"></div>'
            + f'<div style="position:absolute;left:{FB["x"] - 1}px;top:{FB["y"] - 1}px;width:{FB["w"] + 2}px;height:{FB["h"] + 2}px;'
              'background:#0A0F12;box-shadow:inset 0 0 0 1px rgba(201,165,90,.45)"></div>'
            + (f'<div style="position:absolute;inset:0;background:rgba(5,8,10,{dim})"></div>' if dim else ""))


add("pol_focus_card", P + "focus_card.dds", 3 * GW, GH,
    f'<div style="position:absolute;left:0;top:0;width:{GW}px;height:{GH}px">{focus_card("linear-gradient(180deg,#1B262D,#0C1317)", "linear-gradient(90deg,#E8CD84,#8B6A2C)")}</div>'
    f'<div style="position:absolute;left:{GW}px;top:0;width:{GW}px;height:{GH}px">{focus_card("linear-gradient(180deg,#223038,#111A1F)", "linear-gradient(90deg,#FFF3C8,#B48F44)")}</div>'
    f'<div style="position:absolute;left:{2 * GW}px;top:0;width:{GW}px;height:{GH}px">{focus_card("linear-gradient(180deg,#1B262D,#0C1317)", "linear-gradient(90deg,#8F8670,#4A4434)", .35)}</div>')
# "choose a focus" pulse over the card (replaces vanilla's nat_spirit_glow_overlay; 2 frames)
CGW, CGH = GW + 12, GH + 12


def card_glow(a):
    return (f'<div style="position:absolute;inset:0;box-shadow:inset 0 0 0 2px rgba(241,220,156,{a}),inset 0 0 14px rgba(231,183,90,{a})"></div>')


add("pol_focus_glow", P + "focus_glow.dds", 2 * CGW, CGH,
    f'<div style="position:absolute;left:0;top:0;width:{CGW}px;height:{CGH}px">{card_glow(.25)}</div>'
    f'<div style="position:absolute;left:{CGW}px;top:0;width:{CGW}px;height:{CGH}px">{card_glow(.7)}</div>')
# focus progress bar (the game's bar is retargeted to this progressbartype)
add("pol_focus_fill", P + "focus_fill.dds", FB["w"], FB["h"], '<div style="position:absolute;inset:0;background:linear-gradient(180deg,#F1DC9C,#B48F44)"></div>')
add("pol_focus_track", P + "focus_track.dds", FB["w"], FB["h"], '<div style="position:absolute;inset:0;background:#0A0F12"></div>')

# management buttons and the strip behind them
BW_, BH_ = LP.BUTTON["w"], LP.BUTTON["h"]
add("pol_button", P + "button.dds", BW_, BH_,
    plate([(7, 0), (BW_ - 7, 0), (BW_, 7), (BW_, BH_ - 7), (BW_ - 7, BH_), (7, BH_), (0, BH_ - 7), (0, 7)],
          "linear-gradient(180deg,#24323A,#0E1519)"))
add("pol_strip", P + "strip.dds", LP.STRIP["w"], LP.STRIP["h"],
    '<div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(8,12,14,.6),rgba(8,12,14,.3))"></div>'
    + hrule(0, 0, LP.STRIP["w"], "linear-gradient(90deg,transparent,#C9A55A 10%,#C9A55A 90%,transparent)")
    + hrule(0, LP.STRIP["h"] - 1, LP.STRIP["w"], "linear-gradient(90deg,transparent,rgba(201,165,90,.45) 10%,rgba(201,165,90,.45) 90%,transparent)"))

# laws & advisors: category header band and the empty slot (mockup: dashed "appoint" box)
CHW, CHH = LP.CAT_HEADER["w"], LP.CAT_HEADER["h"]
add("pol_cat_header", P + "category_header.dds", CHW, CHH,
    '<div style="position:absolute;inset:0;background:linear-gradient(90deg,rgba(201,165,90,.16),rgba(201,165,90,.03))"></div>'
    + hrule(0, 0, CHW, "linear-gradient(90deg,rgba(201,165,90,.6),rgba(201,165,90,.1))")
    + hrule(0, CHH - 1, CHW, "linear-gradient(90deg,rgba(201,165,90,.6),rgba(201,165,90,.1))"))
S53 = LP.IDEA_SLOT
add("pol_idea_slot", P + "idea_slot.dds", S53, S53,
    '<div style="position:absolute;left:2px;top:2px;right:2px;bottom:2px;border:1px dashed rgba(201,165,90,.7);background:rgba(11,16,20,.55)"></div>'
    f'<svg width="{S53}" height="{S53}" style="position:absolute;left:0;top:0"><path d="M{S53 / 2} {S53 / 2 - 7}v14M{S53 / 2 - 7} {S53 / 2}h14" stroke="#C9A55A" stroke-width="1.5"/></svg>')
# ornament shown in the description band when the leader has no description
add("pol_ornament", P + "ornament.dds", 240, 24,
    '<div style="position:absolute;left:0;top:11px;width:96px;height:1px;background:linear-gradient(90deg,transparent,#C9A55A)"></div>'
    '<div style="position:absolute;right:0;top:11px;width:96px;height:1px;background:linear-gradient(90deg,#C9A55A,transparent)"></div>'
    '<div style="position:absolute;left:108px;top:0;width:24px;height:24px">' + svg("pp", 24) + '</div>'
    '<div style="position:absolute;left:100px;top:9px;width:6px;height:6px;transform:rotate(45deg);background:#C9A55A"></div>'
    '<div style="position:absolute;left:134px;top:9px;width:6px;height:6px;transform:rotate(45deg);background:#C9A55A"></div>')

# sub-windows (advisor picker, subjects, exiles, occupied): header band, entry cards
add("pol_sub_header", P + "sub_header.dds", 500, 30,
    '<div style="position:absolute;inset:0;background:linear-gradient(90deg,rgba(201,165,90,.18),rgba(201,165,90,.02))"></div>'
    + hrule(0, 29, 500, "linear-gradient(90deg,#C9A55A,rgba(201,165,90,.1))"))


def card(w, h, fill="linear-gradient(180deg,#1A252C,#0E1519)", rim="rgba(201,165,90,.55)"):
    return (f'<div style="position:absolute;inset:0;background:{LAC},{fill};box-shadow:inset 0 0 0 1px {rim}"></div>'
            + f'<div style="position:absolute;left:3px;top:3px;width:10px;height:10px;border-left:1px solid #E3C77E;border-top:1px solid #E3C77E"></div>'
            + f'<div style="position:absolute;right:3px;bottom:3px;width:10px;height:10px;border-right:1px solid #E3C77E;border-bottom:1px solid #E3C77E"></div>')


for key, (w, h) in {"entry_87": (494, 87), "entry_95": (494, 95), "entry_65": (494, 65), "entry_100": (494, 100)}.items():
    add("pol_" + key, P + key + ".dds", w, h, card(w, h))
for key, (w, h) in {"idea_entry_grid": (228, 72), "idea_entry_list": (459, 72)}.items():
    add("pol_" + key, P + key + ".dds", 2 * w, h,
        f'<div style="position:absolute;left:0;top:0;width:{w}px;height:{h}px">{card(w, h)}</div>'
        f'<div style="position:absolute;left:{w}px;top:0;width:{w}px;height:{h}px">{card(w, h, "linear-gradient(180deg,#24564C,#11302A)", "#E3C77E")}</div>')

# ---------------------------------------------------------------- state / province panel (v0.4)
import layout_stateview as LS

SVP = "gfx/interface/valsora_deco/stateview/"
BW, BH = LS.BG["w"], LS.BG["h"]
ox_, oy = LS.BG["x"], LS.BG["y"]       # window -> background coordinates
ck = ('<div class="ck tl"></div><div class="ck tr"></div><div class="ck bl"></div><div class="ck br"></div>')
WIDE = "linear-gradient(90deg,rgba(201,165,90,.1),#C9A55A 12%,#C9A55A 88%,rgba(201,165,90,.1))"
SOFT = "linear-gradient(90deg,rgba(201,165,90,.08),rgba(201,165,90,.45) 12%,rgba(201,165,90,.45) 88%,rgba(201,165,90,.08))"
sv = (f'<div style="position:absolute;inset:0;background:{LAC},linear-gradient(180deg,rgba(23,32,38,.98),rgba(11,17,21,.98));'
      'box-shadow:inset 0 0 0 1px #B8954F,inset 0 0 0 3px rgba(11,16,20,.9),inset 0 0 0 4px rgba(201,165,90,.35)"></div>' + ck)
# header: jade wash, flag well, rule
h1 = LS.HEADER[1] - oy
sv += (f'<div style="position:absolute;left:4px;right:4px;top:4px;height:{h1 - 4}px;'
       'background:linear-gradient(180deg,rgba(46,110,96,.24),rgba(46,110,96,0))"></div>')
FWl = LS.FLAG_WELL
sv += (f'<div style="position:absolute;left:{FWl["x"] - ox_}px;top:{FWl["y"] - oy}px;width:{FWl["w"]}px;height:{FWl["h"]}px;'
       'background:#0B1014;box-shadow:inset 0 0 0 1px #C9A55A,0 3px 8px rgba(0,0,0,.5)"></div>')
sv += hrule(8, h1, BW - 16, WIDE)
# stats row: two column rules, rule under the row
s0, s1 = LS.STATS[0] - oy, LS.STATS[1] - oy
for x in LS.STAT_COLS[1:]:
    sv += (f'<div style="position:absolute;left:{x - 12 - ox_}px;top:{s0 + 10}px;width:1px;height:{s1 - s0 - 20}px;'
           'background:linear-gradient(180deg,transparent,rgba(201,165,90,.55) 25%,rgba(201,165,90,.55) 75%,transparent)"></div>')
sv += hrule(8, s1, BW - 16, SOFT)
# section rules (shared slots, buildings, claims)
for y in (LS.BUILDINGS[0], LS.CLAIMS[0]):
    sv += hrule(8, y - oy, BW - 16, SOFT)
# modifiers band, province header band, province body
m0 = LS.MODIFIERS[0] - oy
p0, p1 = LS.PROV_HEAD[0] - oy, LS.PROV_HEAD[1] - oy
sv += hrule(8, m0, BW - 16, SOFT)
sv += (f'<div style="position:absolute;left:4px;right:4px;top:{p0}px;height:{p1 - p0}px;'
       'background:linear-gradient(90deg,rgba(201,165,90,.14),rgba(201,165,90,.02))"></div>')
sv += hrule(8, p0, BW - 16, WIDE) + hrule(8, p1, BW - 16, SOFT)
add("sv_bg", SVP + "stateview_bg.dds", BW, BH, sv)
TW, TH = LS.TILE["w"], LS.TILE["h"]
add("sv_tile", SVP + "building_tile.dds", TW, TH,
    f'<div style="position:absolute;left:1px;top:1px;width:{TW - 2}px;height:{TH - 2}px;background:radial-gradient(circle at 50% 40%,#1A262C,#0B1115);'
    'box-shadow:inset 0 0 0 1px rgba(201,165,90,.65)"></div>'
    + "".join(f'<div style="position:absolute;left:{x - 2}px;top:{y - 2}px;width:4px;height:4px;transform:rotate(45deg);background:#E3C77E"></div>'
              for x, y in [(1, 1), (TW - 1, 1), (1, TH - 1), (TW - 1, TH - 1)]))
SW, SH = LS.SLOT["w"], LS.SLOT["h"]
add("sv_slot", SVP + "slot.dds", SW, SH,
    f'<div style="position:absolute;left:1px;top:1px;width:{SW - 2}px;height:{SH - 2}px;background:rgba(11,16,20,.7);'
    'box-shadow:inset 0 0 0 1px rgba(201,165,90,.55)"></div>')
LW, LH = LS.LEVEL["w"], LS.LEVEL["h"]
add("sv_level", SVP + "level.dds", LW, LH,
    plate([(5, 0), (LW - 5, 0), (LW, LH / 2), (LW - 5, LH), (5, LH), (0, LH / 2)], "linear-gradient(180deg,#1E2930,#0B1014)"))
CW2, CH2 = LS.CHIP["w"], LS.CHIP["h"]
add("sv_chip", SVP + "chip.dds", CW2, CH2,
    plate([(6, 0), (CW2 - 6, 0), (CW2, CH2 / 2), (CW2 - 6, CH2), (6, CH2), (0, CH2 / 2)], "linear-gradient(180deg,#1E2930,#0B1014)"))

# ---------------------------------------------------------------- national focus tree (v0.4)
import layout_focus as LF

NF = "gfx/interface/valsora_deco/focus/"
# header band (corneredTile stretched to the window width): jade wash, gilt rule at the bottom
add("nf_header", NF + "header.dds", 196, LF.HEADER_H,
    f'<div style="position:absolute;inset:0;background:{LAC},linear-gradient(180deg,rgba(46,110,96,.30),rgba(23,32,38,.95) 70%,#111A1F)"></div>'
    f'<div style="position:absolute;left:0;right:0;top:{LF.HEADER_H - 3}px;height:1px;background:#C9A55A"></div>'
    f'<div style="position:absolute;left:0;right:0;top:{LF.HEADER_H - 1}px;height:1px;background:rgba(201,165,90,.35)"></div>')
# tree background: lacquer with a faint 32 px grid (tiles seamlessly in the cornered centre)
TT = LF.TREE_TILE
add("nf_tree_bg", NF + "tree_bg.dds", TT, TT,
    f'<div style="position:absolute;inset:0;background:'
    'repeating-linear-gradient(90deg,rgba(201,165,90,.06) 0 1px,transparent 1px 32px),'
    'repeating-linear-gradient(180deg,rgba(201,165,90,.06) 0 1px,transparent 1px 32px),'
    'repeating-linear-gradient(90deg,rgba(255,255,255,.02) 0 1px,transparent 1px 8px),#0E1519"></div>')
# vignette over the tree (cornered: the corners stay, the edges stretch)
add("nf_vignette", NF + "vignette.dds", 512, 512,
    '<div style="position:absolute;inset:0;background:'
    'linear-gradient(90deg,rgba(5,8,10,.55),rgba(5,8,10,0) 26%,rgba(5,8,10,0) 74%,rgba(5,8,10,.55)),'
    'linear-gradient(180deg,rgba(5,8,10,.35),rgba(5,8,10,0) 22%,rgba(5,8,10,0) 78%,rgba(5,8,10,.5))"></div>')


# name plates under the focus icons: the game swaps these three sprites by state, so they are replaced at
# their vanilla paths (single frame each)
def nf_plate(fill, rim, glow=""):
    w, h, c = LF.PLATE["w"], LF.PLATE["h"], 8
    pts = [(c, 0), (w - c, 0), (w, c), (w, h - c), (w - c, h), (c, h), (0, h - c), (0, c)]
    return (plate(pts, fill, rim, 1.2) + glow
            + f'<div style="position:absolute;left:{w / 2 - 3}px;top:-1px;width:6px;height:6px;transform:rotate(45deg);background:{"#F1DC9C" if glow else "#C9A55A"}"></div>')


PW_, PH_ = LF.PLATE["w"], LF.PLATE["h"]
for key, fill, rim, glow in [
    ("unavailable", "linear-gradient(180deg,#1A2329,#0C1215)", "linear-gradient(180deg,#8F8670,#4A4434)", ""),
    ("can_start", "linear-gradient(180deg,#2E6E60,#123A31)", "linear-gradient(180deg,#FFF3C8,#B48F44)",
     '<div style="position:absolute;inset:3px;box-shadow:inset 0 0 8px rgba(241,220,156,.35)"></div>'),
    ("completed", "linear-gradient(180deg,#7A5E26,#3A2C10)", "linear-gradient(180deg,#FFF3C8,#C9A55A)",
     '<div style="position:absolute;inset:2px;background:linear-gradient(180deg,rgba(255,240,190,.18),rgba(255,240,190,0) 60%)"></div>'),
]:
    add("nf_plate_" + key, f"gfx/interface/focusview/titlebar/focus_{key}_bg.dds", PW_, PH_, nf_plate(fill, rim, glow))
# medallion behind every focus icon: faint octagon with a sunburst
M_ = LF.MEDALLION
mo = oct_(M_, 23)
add("nf_medallion", NF + "medallion.dds", M_, M_,
    f'<div style="position:absolute;inset:0;clip-path:{poly(mo)};background:radial-gradient(circle,rgba(30,44,50,.85),rgba(12,18,22,.85) 70%)"></div>'
    f'<div style="position:absolute;inset:0;clip-path:{poly(mo)};background:repeating-conic-gradient(from 0deg,rgba(227,199,126,.22) 0deg 5deg,transparent 5deg 15deg);'
    '-webkit-mask:radial-gradient(circle,transparent 0 40%,#000 75%)"></div>'
    f'<svg width="{M_}" height="{M_}" style="position:absolute;left:0;top:0"><polygon points="{" ".join(f"{x},{y}" for x, y in inset_poly(mo, .6))}" '
    'fill="none" stroke="rgba(201,165,90,.75)" stroke-width="1.2"/></svg>')
# search box, zoom, filter chips, close
SW_, SH_ = LF.SEARCH["w"], LF.SEARCH["h"]
add("nf_search", NF + "search.dds", SW_, SH_,
    plate([(10, 0), (SW_ - 10, 0), (SW_, SH_ / 2), (SW_ - 10, SH_), (10, SH_), (0, SH_ / 2)], "linear-gradient(180deg,#0E1519,#0A0F12)")
    + f'<div style="position:absolute;left:12px;top:{SH_ / 2 - 9}px;width:18px;height:18px">{svg("search", 18)}</div>'
    + f'<div style="position:absolute;left:36px;top:9px;width:1px;height:{SH_ - 18}px;background:rgba(201,165,90,.45)"></div>')
Z_ = LF.ZOOM


def zoom_btn(glyph):
    return (f'<div style="position:absolute;left:{Z_ / 2 - 10.5}px;top:{Z_ / 2 - 10.5}px;width:21px;height:21px;transform:rotate(45deg);'
            'border:1px solid #C9A55A;background:#0B1014;box-sizing:border-box"></div>'
            f'<svg width="{Z_}" height="{Z_}" style="position:absolute;left:0;top:0" fill="none" stroke="#E3C77E" stroke-width="1.8">{glyph}</svg>')


add("nf_zoom_in", NF + "zoom_in.dds", Z_, Z_, zoom_btn(f'<path d="M{Z_ / 2 - 5} {Z_ / 2}h10M{Z_ / 2} {Z_ / 2 - 5}v10"/>'))
add("nf_zoom_out", NF + "zoom_out.dds", Z_, Z_, zoom_btn(f'<path d="M{Z_ / 2 - 5} {Z_ / 2}h10"/>'))
FL = LF.FILTER


def filter_chip(on):
    o = oct_(FL, 9)
    return plate(o, "radial-gradient(circle,#2E6E60,#123A31)" if on else "linear-gradient(180deg,#1E2930,#0E1519)",
                 "linear-gradient(180deg,#FFF3C8,#B48F44)" if on else GOLD_V)


add("nf_filter", NF + "filter_chip.dds", 2 * FL, FL,
    f'<div style="position:absolute;left:0;top:0;width:{FL}px;height:{FL}px">{filter_chip(False)}</div>'
    f'<div style="position:absolute;left:{FL}px;top:0;width:{FL}px;height:{FL}px">{filter_chip(True)}</div>')
# detail pop-up: prerequisites well and the reward bar
add("nf_prereq_bg", NF + "prereq_bg.dds", 307, 113,
    '<div style="position:absolute;inset:0;background:rgba(8,12,14,.6);box-shadow:inset 0 0 0 1px rgba(201,165,90,.45)"></div>')
add("nf_reward_bar", NF + "reward_bar.dds", 382, 30,
    '<div style="position:absolute;inset:0;background:linear-gradient(90deg,rgba(201,165,90,0),rgba(201,165,90,.16) 50%,rgba(201,165,90,0))"></div>'
    + hrule(0, 0, 382, "linear-gradient(90deg,transparent,#C9A55A 20%,#C9A55A 80%,transparent)")
    + hrule(0, 29, 382, "linear-gradient(90deg,transparent,rgba(201,165,90,.45) 20%,rgba(201,165,90,.45) 80%,transparent)"))
# legend (lower right): the three plate states and an exclusive-link mark, with English labels
LGW, LGH = LF.LEGEND["w"], LF.LEGEND["h"]


def leg_swatch(fill, rim):
    o = [(4, 0), (22, 0), (26, 4), (26, 12), (22, 16), (4, 16), (0, 12), (0, 4)]
    return f'<div style="position:relative;width:26px;height:16px;flex:none">{plate(o, fill, rim)}</div>'


items = [(leg_swatch("linear-gradient(180deg,#7A5E26,#3A2C10)", "linear-gradient(180deg,#FFF3C8,#C9A55A)"), "Completed"),
         (leg_swatch("linear-gradient(180deg,#2E6E60,#123A31)", "linear-gradient(180deg,#FFF3C8,#B48F44)"), "Available"),
         (leg_swatch("linear-gradient(180deg,#1A2329,#0C1215)", "linear-gradient(180deg,#8F8670,#4A4434)"), "Unavailable"),
         ('<div style="width:10px;height:10px;transform:rotate(45deg);background:#EE8C7E;margin:0 5px;flex:none"></div>', "Mutually exclusive")]
add("nf_legend", NF + "legend.dds", LGW, LGH,
    plate([(8, 0), (LGW - 8, 0), (LGW, 8), (LGW, LGH - 8), (LGW - 8, LGH), (8, LGH), (0, LGH - 8), (0, 8)],
          "linear-gradient(180deg,rgba(23,32,38,.95),rgba(11,17,21,.95))")
    + '<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;gap:16px;'
      "font:600 10px/1 'Josefin Sans';letter-spacing:.14em;text-transform:uppercase;color:#CBBF9F\">"
    + "".join(f'<div style="display:flex;align-items:center;gap:7px">{sw}<span style="padding-top:2px">{lab}</span></div>'
              for sw, lab in items) + '</div>')

# ---------------------------------------------------------------- main menu
MENU = "gfx/interface/valsora_deco/menu/"
WORLD = ART + "menu_world.jpg"
# continent labels (centre x, y in the 1080-row art): the user's arrangement of 2026-10-14 (v0.4.6),
# measured from their picture; until then Nonscio (548, 548), Araseos (492, 772), Yastreovakia
# (1012, 352), Usnistan (1100, 730), Orientalis (1436, 478)
CN = [("NONSCIO", 466, 553, 14), ("ARASEOS", 511, 794, 14), ("YASTREOVAKIA", 1026, 350, 14), ("AISLADA", 800, 642, 12),
      ("SOLITAS", 806, 806, 14), ("USNISTAN", 1112, 729, 14), ("ORIENTALIS", 1455, 568, 14)]
OY = 180   # the 1920x1440 background is cropped to its middle 1080 rows on a 16:9 screen
names = "".join(
    f'<div style="position:absolute;left:{x}px;top:{y + OY}px;transform:translate(-50%,-50%);font:400 {fs}px/1 Federo;letter-spacing:.55em;'
    f'padding:6px 14px 6px calc(14px + .55em);background:radial-gradient(closest-side,rgba(12,26,25,.92) 55%,rgba(12,26,25,0));'
    f'color:rgba(246,232,190,.82);text-shadow:0 1px 3px #000,0 0 10px rgba(0,0,0,.8);white-space:nowrap">{n}</div>' for n, x, y, fs in CN)
LOGO = (
    f'<div style="position:absolute;left:0;right:0;top:{52 + OY}px;display:flex;flex-direction:column;align-items:center">'
    '<div style="display:flex;align-items:center;gap:14px"><i style="width:90px;height:1px;background:linear-gradient(90deg,transparent,#D2B064)"></i>'
    '<i style="width:9px;height:9px;background:#E8CD84;transform:rotate(45deg)"></i><i style="width:90px;height:1px;background:linear-gradient(270deg,transparent,#D2B064)"></i></div>'
    '<div style="margin-top:14px;font:400 132px/.92 Limelight;letter-spacing:.1em;padding-left:.1em;filter:drop-shadow(0 3px 0 #3B2A10) drop-shadow(0 14px 22px rgba(0,0,0,.75))">'
    '<span style="background:linear-gradient(180deg,#FFF6D6 0%,#F0D58E 38%,#B48A3C 56%,#E7C979 74%,#FBEBBE 100%);-webkit-background-clip:text;color:transparent">VALSORA</span></div>'
    '<div style="margin-top:18px;display:flex;align-items:center;gap:18px">'
    '<span style="display:flex;flex-direction:column;gap:3px;width:110px"><i style="height:1px;background:linear-gradient(90deg,transparent,#C9A55A)"></i><i style="height:1px;margin-left:26px;background:linear-gradient(90deg,transparent,#C9A55A)"></i><i style="height:1px;margin-left:52px;background:linear-gradient(90deg,transparent,#C9A55A)"></i></span>'
    '<span style="font:600 14px/1 \'Josefin Sans\';letter-spacing:.5em;padding-left:.5em;text-transform:uppercase;color:#E7D3A0;padding-top:2px">A Hearts of Iron IV total conversion</span>'
    '<span style="display:flex;flex-direction:column;gap:3px;width:110px;align-items:flex-end"><i style="height:1px;width:100%;background:linear-gradient(270deg,transparent,#C9A55A)"></i><i style="height:1px;width:calc(100% - 26px);background:linear-gradient(270deg,transparent,#C9A55A)"></i><i style="height:1px;width:calc(100% - 52px);background:linear-gradient(270deg,transparent,#C9A55A)"></i></span></div>'
    '<div style="margin-top:12px;font:italic 17px Bodoni Moda;color:#BFAF86">The world of The East Pacific</div></div>')
MENU_BG = (f'<div style="position:absolute;inset:0;background:radial-gradient(ellipse 900px 520px at 960px {OY + 40}px,#161D20,#0A0E12 70%,#080C0F)"></div>'
           # sunburst continued into the top and bottom margins (centred on the art's own burst)
           f'<div style="position:absolute;left:960px;top:{OY + 165}px;width:3200px;height:3200px;margin:-1600px 0 0 -1600px;border-radius:50%;'
           'background:repeating-conic-gradient(rgba(227,199,126,.045) 0deg 2deg,transparent 2deg 9deg);-webkit-mask:radial-gradient(circle,#000 0 18%,transparent 55%)"></div>'
           # the art fades into the margins instead of meeting them at a hard edge
           f'<img src="file://{WORLD}" style="position:absolute;left:0;top:{OY}px;width:1920px;height:1080px;'
           '-webkit-mask:linear-gradient(180deg,transparent 0,#000 110px,#000 970px,transparent 1080px)">'
           + names + LOGO)
add("menu_bg", "gfx/loadingscreens/valsora_menu.dds", 1920, 1440, MENU_BG)


def menu_button(w, h, state, big=False):
    c = h // 4 if not big else h // 4 + 2
    pts = [(c, 0), (w - c, 0), (w, h / 2), (w - c, h), (c, h), (0, h / 2)]
    if big:
        rim = "linear-gradient(180deg,#FFF3C8,#8B6A2C)"
        fill = {0: "linear-gradient(180deg,#F8E7B0,#D9B868 50%,#B48A3C)", 1: "linear-gradient(180deg,#FFF3C8,#E9CC80 50%,#C79C4A)",
                2: "linear-gradient(180deg,#8E8064,#6E6047)"}[state]
    else:
        rim = GOLD_V if state != 2 else "linear-gradient(180deg,#7A6C4E,#4B4232)"
        fill = {0: "linear-gradient(180deg,#1E2930,#0C1317)", 1: "linear-gradient(180deg,#2B3B44,#16212A)",
                2: "linear-gradient(180deg,#151C20,#0B1014)"}[state]
    return plate(pts, fill, rim)


for key, (w, h, big) in {"menu_button": (200, 48, False), "menu_button_big": (420, 64, True),
                          "menu_button_small": (150, 32, False), "menu_button_panel": (288, 36, False)}.items():
    add(key, MENU + key + ".dds", 3 * w, h, "".join(
        f'<div style="position:absolute;left:{i * w}px;top:0;width:{w}px;height:{h}px">{menu_button(w, h, i, big)}</div>' for i in range(3)))
add("menu_bg_small", MENU + "valsora_menu_small.dds", 192, 144,
    f'<div style="position:absolute;left:0;top:0;width:1920px;height:1440px;transform:scale(.1);transform-origin:0 0">{MENU_BG}</div>')

# mod thumbnail (launcher)
add("thumb", "thumbnail.png", 512, 256,
    '<div style="position:absolute;inset:0;background:radial-gradient(ellipse at 50% 0%,#1E2E2C,#0A0F12 70%)"></div>'
    '<div style="position:absolute;left:256px;top:-40px;width:600px;height:600px;margin-left:-300px;border-radius:50%;background:repeating-conic-gradient(rgba(227,199,126,.16) 0deg 3deg,transparent 3deg 10deg);-webkit-mask:radial-gradient(circle,#000 0 40%,transparent 70%)"></div>'
    '<div style="position:absolute;left:0;right:0;top:78px;text-align:center;font:400 64px/1 Limelight;letter-spacing:.1em;padding-left:.1em;background:linear-gradient(180deg,#FFF6D6,#F0D58E 38%,#B48A3C 56%,#E7C979 74%,#FBEBBE);-webkit-background-clip:text;color:transparent">VALSORA</div>'
    '<div style="position:absolute;left:0;right:0;top:162px;text-align:center;font:600 15px/1 \'Josefin Sans\';letter-spacing:.42em;padding-left:.42em;color:#E7D3A0">ART DECO INTERFACE</div>'
    '<div style="position:absolute;left:176px;right:176px;top:196px;height:5px;border-top:1px solid #C9A55A;border-bottom:1px solid rgba(201,165,90,.45)"></div>', fmt="png")


# ---------------------------------------------------------------- render
G = FONTS_SRC
FONTS = f"""@font-face{{font-family:'Limelight';src:url('file://{G}limelight/Limelight-Regular.ttf')}}
@font-face{{font-family:'Federo';src:url('file://{G}federo/Federo-Regular.ttf')}}
@font-face{{font-family:'Bodoni Moda';font-style:italic;src:url('file://{G}bodonimoda/BodoniModa-Italic[opsz,wght].ttf')}}
@font-face{{font-family:'Josefin Sans';src:url('file://{G}josefinsans/JosefinSans[wght].ttf');font-weight:100 700}}"""
body = []
y = 0
for key, rel, w, h, html, fmt in SPRITES:
    body.append(f'<div class="s" id="{key}" style="left:0;top:{y}px;width:{w}px;height:{h}px">{html}</div>')
    y += h + 10
page = f"<html><head><style>{FONTS}{CSS}</style></head><body style='width:2000px;height:{y}px'>{''.join(body)}</body></html>"
open(BUILD + "sprites.html", "w").write(page)

manifest = []
with sync_playwright() as p:
    b = p.chromium.launch(**CHROMIUM)
    pg = b.new_page(viewport={"width": 2000, "height": 1500}, device_scale_factor=1)
    pg.goto("file://" + BUILD + "sprites.html")
    pg.wait_for_timeout(600)
    for key, rel, w, h, html, fmt in SPRITES:
        el = pg.query_selector("#" + key)
        out = PNG + key + ".png"
        el.screenshot(path=out, omit_background=True)
        im = Image.open(out)
        assert im.size == (w, h), (key, im.size, (w, h))
        dest = MOD + rel
        if fmt == "dds":
            write_dds(im, dest)
        elif fmt == "tga":
            write_tga(im, dest)
        else:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            im.convert("RGB").save(dest)
        manifest.append({"key": key, "path": rel, "w": w, "h": h})
    b.close()
json.dump(manifest, open(BUILD + "texture_manifest.json", "w"), indent=1)
print(len(manifest), "textures written")
