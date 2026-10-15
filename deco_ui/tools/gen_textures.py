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
# tooltip background (vanilla ToolTip textBoxType: tiles_dialog.tga, borderSize 18). The game loads a .dds of
# the same name first, and vanilla ships only gfx/interface/tiles/tiles_dialog.dds (96x96): in game (v0.4.7)
# our .tga never showed, every tooltip kept vanilla's look. So the .dds, at vanilla's size, is replaced.
add("tooltip", "gfx/interface/tiles/tiles_dialog.dds", 96, 96,
    '<div style="position:absolute;inset:0;background:#0E1519;opacity:.96"></div>'
    '<div class="frame" style="inset:0;border:1px solid #B8954F"></div>'
    '<div class="frame" style="left:1px;right:1px;top:1px;height:2px;background:linear-gradient(90deg,#8B6A2C,#F1DC9C,#8B6A2C)"></div>'
    '<i class="ck sm tl"></i><i class="ck sm tr"></i><i class="ck sm bl"></i><i class="ck sm br"></i>')

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

# ---------------------------------------------------------------- core skin: the panels' shared pieces (v0.5)
# The game draws these on every side panel and sub-window (close buttons, background tiles, header bars, tabs,
# sort buttons, checkboxes), so they are replaced at their vanilla paths, sizes and frame counts and the panels'
# contents follow the deco style with no .gui change. Two-frame sprites keep vanilla's order, which differs per
# sprite: the tabs, the diplomacy filters and sort_button_100x29_2 are lit in frame 1 (countrytechnologyview.gui
# starts its shown tab at frame 1), sort_button_202x29 and the checkbox in frame 2.
STRIPES = "repeating-linear-gradient(90deg,rgba(255,255,255,.025) 0 1px,transparent 1px 7px)"
BAR_FILL = "linear-gradient(180deg,#1A252C,#0E1519)"
LIT_FILL = "linear-gradient(180deg,#2C665A,#163A33)"           # jade, as the top bar's lit buttons
DIM_FILL = "linear-gradient(180deg,#141D22,#0B1014)"


def bar(fill=BAR_FILL, rim="rgba(201,165,90,.6)", c=5, shine=.22):
    """a chamfered lacquer bar with a gilt hairline: header strips, list headers, footers, tabs"""
    return (f'<div style="position:absolute;inset:0;background:{rim};clip-path:{chamfer(c)}"></div>'
            f'<div style="position:absolute;inset:1px;clip-path:{chamfer(max(1, c - .4))};background:{STRIPES},{fill}"></div>'
            f'<div style="position:absolute;left:{c + 3}px;right:{c + 3}px;top:2px;height:1px;background:rgba(241,220,156,{shine})"></div>')


def frames(w, h, *parts):
    fw = w // len(parts)
    return "".join(f'<div style="position:absolute;left:{i * fw}px;top:0;width:{fw}px;height:{h}px">{p}</div>'
                   for i, p in enumerate(parts))


def lit_bar(c=5):
    return bar(LIT_FILL, GOLD, c, .35)


GOLD = "linear-gradient(180deg,#E8CD84,#8B6A2C)"
SHARED = {   # vanilla path: (w, h, html)
    "gfx/interface/closebutton.dds": (32, 33,
        '<div style="position:absolute;left:5px;top:5.5px;width:22px;height:22px;transform:rotate(45deg);border:1px solid #E3C77E;'
        'background:#0B1014;box-sizing:border-box"></div>'
        '<svg width="32" height="33" viewBox="0 0 32 33" style="position:absolute;left:0;top:0"><path d="M11.5 12l9 9M20.5 12l-9 9" '
        'stroke="#E3C77E" stroke-width="1.6"/></svg>'),
    "gfx/interface/tiles/tiled_bg.dds": (192, 192, window(192, 192, dict(rule="single", corners="small"))),
    "gfx/interface/header_bg.dds": (543, 41, bar(c=7)),
    "gfx/interface/category_header.dds": (511, 44, bar("linear-gradient(180deg,#1E2A30,#111A1F)", c=7)),
    "gfx/interface/factions/ui/faction_header.dds": (530, 42, bar(c=7)),
    "gfx/interface/main_screens_bottom.dds": (545, 54, bar(DIM_FILL, c=8, shine=.12)),
    "gfx/interface/deployment_binding.dds": (533, 35, bar(c=6)),
    "gfx/interface/tradeview/trade_header.dds": (516, 35, bar(c=6)),
    "gfx/interface/intel_ledger/tab_bg.dds": (520, 40, bar(DIM_FILL, c=6, shine=.1)),
    "gfx/interface/diplo_details_header.dds": (241, 51, bar(c=7)),
    "gfx/interface/generic_text_bg_108.dds": (108, 27,
        '<div style="position:absolute;inset:0;background:#0A0F12;box-shadow:inset 0 0 0 1px rgba(201,165,90,.35)"></div>'),
    "gfx/interface/tiles/tiling_sort_button.dds": (60, 23, bar(c=4, shine=.15)),
    "gfx/interface/tab_large.dds": (516, 42, frames(516, 42, lit_bar(7), bar(DIM_FILL, "rgba(201,165,90,.4)", 7, .1))),
    "gfx/interface/intel_ledger/tab.dds": (520, 42, frames(520, 42, lit_bar(7), bar(DIM_FILL, "rgba(201,165,90,.4)", 7, .1))),
    "gfx/interface/diplo_filter_entry.dds": (246, 34, frames(246, 34, lit_bar(5), bar(c=5))),
    "gfx/interface/sort_button_100x29_2.dds": (200, 29, frames(200, 29, lit_bar(4), bar(c=4, shine=.15))),
    # vanilla's is a .tga, which the game loads only when no .dds of the same name exists
    "gfx/interface/sort_button_202x29.dds": (404, 29, frames(404, 29, bar(c=4, shine=.15), lit_bar(4))),
    "gfx/interface/generic_checkbox.dds": (68, 30, frames(68, 30,
        '<div style="position:absolute;left:7px;top:5px;width:20px;height:20px;background:#0A0F12;box-shadow:inset 0 0 0 1px #C9A55A"></div>',
        '<div style="position:absolute;left:7px;top:5px;width:20px;height:20px;background:#163A33;box-shadow:inset 0 0 0 1px #E3C77E"></div>'
        '<svg width="34" height="30" viewBox="0 0 34 30" style="position:absolute;left:0;top:0"><path d="M11 15.5l4 4 8-9" fill="none" '
        'stroke="#F1DC9C" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>')),
}
for rel, (w, h, html) in SHARED.items():
    add("shared_" + rel.split("/")[-1][:-4], rel, w, h, html)

# ---------------------------------------------------------------- map modes and minimap (lower right, v0.5)
# Replaced at their vanilla paths, sizes and frame counts (interface/mapmodes_interface.gui and Valsora's
# minimap.gui stay as they are). The game picks a map mode's icon by frame, so the small icons and the toggles
# keep vanilla's glyphs, recoloured in gilt (their meaning and order stay exactly the game's); the four big
# ones (land, air, naval, intelligence) are the mod's line icons on octagonal medallions. The minimap's own
# picture and frame are drawn by the Valsora mod (scripts/minimap.py, its deco style).
import base64
import io as _io
from paths import VANILLA as _VANILLA

MM = "gfx/interface/mapmode/"
GILT_RAMP = [(0.0, (46, 32, 12)), (0.35, (122, 92, 38)), (0.62, (201, 165, 90)), (0.85, (232, 205, 132)), (1.0, (251, 236, 186))]


def vanilla_frames(rel, n):
    im = Image.open(_VANILLA + rel).convert("RGBA")
    fw = im.width // n
    return [im.crop((i * fw, 0, (i + 1) * fw, im.height)) for i in range(n)]


def gilt(img, gain=1.0, alpha=1.0, grey=0.0):
    """a vanilla glyph in gilt: its shading mapped onto the gilt ramp, its alpha kept"""
    a = np.asarray(img, dtype=float)
    lum = a[..., :3].mean(-1)
    m = a[..., 3] > 96
    lo, hi = (np.percentile(lum[m], 4), np.percentile(lum[m], 99)) if m.any() else (0.0, 255.0)
    tt = np.clip((lum - lo) / max(1.0, hi - lo) * gain, 0, 1)
    xs = [s for s, _ in GILT_RAMP]
    col = np.stack([np.interp(tt, xs, [c[i] for _, c in GILT_RAMP]) for i in range(3)], -1)
    if grey:
        col = col * (1 - grey) + col.mean(-1, keepdims=True) * grey
    return Image.fromarray(np.clip(np.dstack([col, a[..., 3] * alpha]), 0, 255).astype(np.uint8), "RGBA")


def img_tag(img, x=0, y=0):
    b = _io.BytesIO()
    img.save(b, "PNG")
    return (f'<img src="data:image/png;base64,{base64.b64encode(b.getvalue()).decode()}" '
            f'style="position:absolute;left:{x}px;top:{y}px;width:{img.width}px;height:{img.height}px">')


def octagon(w, h, c):
    return f"polygon({c}px 0,{w - c}px 0,{w}px {c}px,{w}px {h - c}px,{w - c}px {h}px,{c}px {h}px,0 {h - c}px,0 {c}px)"


def medallion(w, h, icon_name, lit, size=20):
    rim = "#F1DC9C" if lit else "#C9A55A"
    fill = LIT_FILL if lit else "linear-gradient(180deg,#1B262D,#0B1014)"
    ic = "#FBEAB4" if lit else "#E3C77E"
    return (f'<div style="position:absolute;inset:0;background:{rim};clip-path:{octagon(w, h, 8)}"></div>'
            f'<div style="position:absolute;inset:1px;background:{STRIPES},{fill};clip-path:{octagon(w - 2, h - 2, 7.6)}"></div>'
            f'<div class="ico" style="position:absolute;inset:0">{svg(icon_name, size, ic, 1.6)}</div>')


def chip(w, h, lit):
    return bar(LIT_FILL if lit else DIM_FILL, "#E3C77E" if lit else "rgba(201,165,90,.7)", 3, .3 if lit else .12)


# the column (map_modes_bg, 87x206 at the container's x 549: its last 5 px are off-screen) and its foot
COLUMN = ('<div class="lac" style="position:absolute;inset:0;opacity:.97"></div>'
          '<div class="frame" style="left:0;top:0;bottom:0;width:1px;background:rgba(0,0,0,.6)"></div>'
          '<div class="frame" style="left:1px;top:0;bottom:0;width:1px;background:#B8954F"></div>'
          '<div class="frame" style="left:5px;top:5px;bottom:0;width:1px;background:rgba(201,165,90,.45)"></div>'
          '<div class="frame" style="left:1px;right:0;top:1px;height:1px;background:#B8954F"></div>'
          '<div class="frame" style="left:5px;right:0;top:5px;height:1px;background:rgba(201,165,90,.45)"></div>'
          '<div class="frame" style="left:54px;top:36px;bottom:18px;width:1px;'
          'background:linear-gradient(180deg,rgba(201,165,90,0),rgba(201,165,90,.35) 20%,rgba(201,165,90,.35) 80%,rgba(201,165,90,0))"></div>'
          '<i class="ck tl"></i>')
FOOT = ('<div class="lac" style="position:absolute;inset:0;opacity:.97"></div>'
        '<div class="frame" style="left:0;top:0;bottom:0;width:1px;background:rgba(0,0,0,.6)"></div>'
        '<div class="frame" style="left:1px;top:0;bottom:0;width:1px;background:#B8954F"></div>'
        '<div class="frame" style="left:1px;right:0;top:1px;height:1px;background:#B8954F"></div>'
        '<div class="frame" style="left:5px;right:0;top:5px;height:1px;background:rgba(201,165,90,.45)"></div>')
add("mm_column", MM + "mapmode_main_bg.dds", 87, 206, COLUMN)
add("mm_foot", MM + "mapmode_bottom_bg.dds", 86, 59, FOOT)
add("mm_find", MM + "find_screen_button.dds", 39, 39, medallion(39, 39, "search", False, 20))
add("mm_all", MM + "mapmode_button_all.dds", 44, 21, frames(44, 21,
    chip(22, 21, False) + f'<div class="ico" style="position:absolute;inset:0">{svg("chevron_left", 16, "#E3C77E", 1.8)}</div>',
    chip(22, 21, True) + f'<div class="ico" style="position:absolute;inset:0">{svg("chevron_left", 16, "#FBEAB4", 1.8)}</div>'))
# the well behind each big button (42x51, the button 4 px in and 10 down): a gilt thread above and below the
# medallion, so the column's big buttons read as one chain; transparent elsewhere (the wells overlap)
add("mm_well", MM + "mapmode_button_bg.dds", 42, 51,
    '<div style="position:absolute;left:20.5px;top:0;width:1px;height:11px;background:rgba(201,165,90,.5)"></div>'
    '<div style="position:absolute;left:20.5px;top:40px;width:1px;height:11px;background:rgba(201,165,90,.5)"></div>')
BIG = ["army", "air", "navy", "intel"]      # vanilla's frames: soldier, plane, anchor, eye
add("mm_big", MM + "mapmode_buttons_deselected_big.dds", 136, 31, frames(136, 31, *[medallion(34, 31, n, False, 19) for n in BIG]))
add("mm_big_s", MM + "mapmode_buttons_selected_big.dds", 136, 31, frames(136, 31, *[medallion(34, 31, n, True, 19) for n in BIG]))
# behind a selected small button and behind every toggle: a dark well with a gilt hairline
add("mm_depressed", MM + "mapmode_button_depressed.dds", 23, 20,
    '<div style="position:absolute;inset:0;background:#0A0F12;box-shadow:inset 0 0 0 1px rgba(201,165,90,.45)"></div>')
SMALL = vanilla_frames(MM + "mapmode_buttons_deselected_small.dds", 18)
add("mm_small", MM + "mapmode_buttons_deselected_small.dds", 360, 18, frames(360, 18, *[img_tag(gilt(f)) for f in SMALL]))
add("mm_small_s", MM + "mapmode_buttons_selected_small.dds", 360, 18, frames(360, 18, *[
    '<div style="position:absolute;inset:0;background:#163A33;box-shadow:inset 0 0 0 1px #E3C77E"></div>' + img_tag(gilt(f, 1.15))
    for f in SMALL]))
for key, rel in [("day_night", "day_night_toggle.dds"), ("counters", "player_counters_toggle.dds"),
                 ("counter_colours", "counters_color_mode_button.dds"), ("allied_plans", "allied_plans_button.dds"),
                 ("fog", "fog_of_war_toggle.dds"), ("radar", "radar_toggle.dds")]:
    f0, f1 = vanilla_frames(MM + rel, 2)
    add("mm_" + key, MM + rel, 44, 22, frames(44, 22, img_tag(gilt(f0, 1.1)), img_tag(gilt(f1, .9, .7, .65))))
CF = 173                                                        # configure list: plain, lit, and with a chevron
add("mm_configure", MM + "mapmode_configure_bg.dds", 3 * CF, 23, frames(3 * CF, 23, bar(c=4, shine=.15), lit_bar(4),
    bar(c=4, shine=.15) + f'<div style="position:absolute;left:4px;top:3px">{svg("chevron_left", 17, "#E3C77E", 1.8)}</div>'))
# the social button over the column (vanilla's is a .tga, so a .dds of the same name is loaded first)
add("sort_83", "gfx/interface/sort_button_83x29.dds", 166, 29, frames(166, 29, bar(c=4, shine=.15), lit_bar(4)))

# the minimap's handle (slides it away, ctrl+m) and its ping buttons and pings
MN = "gfx/minimap/"


def handle(lit):
    rim = "#F1DC9C" if lit else "#C9A55A"
    fill = "linear-gradient(90deg,#6B4E1C,#2A1F0C)" if lit else "linear-gradient(90deg,#1B262D,#0B1014)"
    pts = "polygon(8px 0,24px 0,24px 64px,0 64px,0 8px)"
    grip = "".join(f'<div style="position:absolute;left:{x}px;top:18px;width:1px;height:34px;background:{rim};opacity:.8"></div>'
                   for x in (8, 12, 16))
    return (f'<div style="position:absolute;inset:0;background:{rim};clip-path:{pts}"></div>'
            f'<div style="position:absolute;left:1px;top:1px;right:0;bottom:1px;background:{STRIPES},{fill};'
            'clip-path:polygon(7.6px 0,23px 0,23px 62px,0 62px,0 7.6px)"></div>' + grip)


add("mn_handle", MN + "handle_default.dds", 24, 64, handle(False))
add("mn_handle_pinged", MN + "handle_pinged.dds", 24, 64, handle(True))
for key, ic in (("offensive", "swords"), ("defensive", "shield")):
    add(f"mn_{key}_btn", MN + f"{key}_ping_btn.dds", 64, 31, frames(64, 31,
        f'<div style="position:absolute;left:2px;top:1px;width:28px;height:28px">{medallion(28, 28, ic, False, 18)}</div>',
        f'<div style="position:absolute;left:2px;top:1px;width:28px;height:28px">{medallion(28, 28, ic, True, 18)}</div>'))
for key, ic, w, h in (("offensive", "swords", 21, 22), ("defensive", "shield", 23, 21)):
    add(f"mn_ping_{key}", MN + f"minimap_ping_{key}.dds", w, h,
        f'<div class="ico" style="position:absolute;inset:0;filter:drop-shadow(0 0 1px #000) drop-shadow(0 0 1px #000)">'
        f'{svg(ic, min(w, h) - 2, "#F1DC9C", 2)}</div>')

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
# the vanilla textures are replaced at their paths (1 frame each, like vanilla). In a faction the game
# shows topbar_faction_empty, vanilla's plain plate, and draws the faction's logo over it: ours is an
# empty medallion ring. Out of a faction it shows topbar_faction (vanilla's crossed axes): our line icon.
# (Until v0.4.7 the two were the other way round, and in game the icon showed under the logo.)
def faction_crown(in_faction):
    w, h, c = L.BTN_W, L.BTN_H, 9
    pts = [(c, 0), (w - c, 0), (w, c), (w, h), (0, h), (0, c)]
    inner = (f'<div style="position:absolute;left:{w / 2 - 17}px;top:{h / 2 - 15}px;width:34px;height:34px;border-radius:50%;'
             'box-shadow:inset 0 0 0 1px rgba(227,199,126,.55);background:radial-gradient(circle,#18262B,#0B1115)"></div>'
             if in_faction else f'<div class="ico" style="position:absolute;inset:0">{svg("faction", 24)}</div>')
    return plate(pts, "linear-gradient(180deg,#1E2930,#0E1519)") + inner


add("tb_faction_empty", "gfx/interface/factions/ui/topbar_faction_empty.dds", L.BTN_W, L.BTN_H, faction_crown(True))
add("tb_faction", "gfx/interface/factions/ui/topbar_faction.dds", L.BTN_W, L.BTN_H, faction_crown(False))
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


def path_d(pts):
    return "M" + " L".join(f"{x} {y}" for x, y in pts) + " Z"


PW, NB, HA = LP.PANEL_W, LP.NOTCH_BOTTOM, LP.HEAD_ART_H
NOTCH_D = path_d(LP.notch_outline(0))


def clipped(html, h, w=PW, region=None):
    """html clipped to everything but the notch (and to `region`, a path, when given)"""
    region = region or f"M0 0 H{w} V{h} H0 Z"
    return (f'<div style="position:absolute;left:0;top:0;width:{w}px;height:{h}px;'
            f"clip-path:path(evenodd,'{region} {NOTCH_D}')\">{html}</div>")


def notch_ring(d_out, d_in, fill):
    """a band following the notch's outline, from d_in to d_out px out into the panel"""
    return (f'<div style="position:absolute;left:0;top:0;width:{PW}px;height:{HA}px;background:{fill};'
            f"clip-path:path(evenodd,'{path_d(LP.notch_outline(d_out))} {path_d(LP.notch_outline(d_in))}')\"></div>")


def side_lines(h, top=0):
    """the panel frame's verticals (as window(): shade at the edge, gilt 1 px in, faint 5 px in)"""
    out = ""
    for x, col in ((0, "rgba(0,0,0,.6)"), (1, "#B8954F"), (5, "rgba(201,165,90,.45)")):
        for xx in (x, PW - 1 - x):
            out += f'<div style="position:absolute;left:{xx}px;top:{top}px;width:1px;height:{h}px;background:{col}"></div>'
    return out


# the header strip: vanilla's pol_view_bg sprite, which the game swaps for GFX_pol_view_bg_no_dlc at runtime, so
# both vanilla textures (550x344) are replaced. Lacquer above the notch's bottom, everything but the notch (the
# top bar's flag medallion and decisions seal show through it), the frame's verticals, a gilt edge round
# the notch, the band's shadow, the jade wash and the rule under the title. Transparent below.
HEAD = clipped('<div class="lac" style="position:absolute;inset:0;opacity:.97"></div>'
               f'<div style="position:absolute;left:0;top:0;width:{PW}px;height:{LP.HEAD_GLOW_H}px;'
               'background:linear-gradient(180deg,rgba(46,110,96,.22),rgba(46,110,96,0))"></div>'
               f'<div style="position:absolute;left:0;top:0;width:{PW}px;height:12px;'
               'background:linear-gradient(180deg,rgba(0,0,0,.55),rgba(0,0,0,0))"></div>', NB)
HEAD += side_lines(NB)
# the edge round the medallion and seal: gilt over their own outermost pixel (the panel overlaps it by
# LP.NOTCH_OVERLAP, so no map shows between them), a dark line, and the frame's faint second line
HEAD += notch_ring(1, 0, "#C9A55A") + notch_ring(2, 1, "rgba(0,0,0,.45)") + notch_ring(5, 4, "rgba(201,165,90,.45)")
HEAD += f'<div style="position:absolute;left:0;top:0;width:{PW}px;height:{NB}px"><i class="ck tr"></i></div>'
HEAD += hrule(LP.HX - 2, LP.HEAD_RULE_Y, LP.X1 + 12 - (LP.HX - 2),
              "linear-gradient(90deg,rgba(201,165,90,.15),#C9A55A 12%,#C9A55A 88%,rgba(201,165,90,.1))")
for rel in ("gfx/interface/pol_view_bg.dds", "gfx/interface/pol_view_bg_no_dlc.dds"):
    add("pol_head_" + os.path.basename(rel)[:-4], rel, PW, HA, HEAD)

# the panel below the header strip (a cornered tile running to the bottom of the screen): lacquer, the
# frame's verticals running through the top edge (they continue the header strip's), the frame along the
# bottom with the big corner brackets
add("pol_body", P + "body.dds", 192, 192,
    '<div class="lac" style="position:absolute;inset:0;opacity:.97"></div>'
    '<div class="frame" style="left:0;right:0;bottom:0;height:1px;background:rgba(0,0,0,.6)"></div>'
    '<div class="frame" style="left:0;top:0;bottom:0;width:1px;background:rgba(0,0,0,.6)"></div>'
    '<div class="frame" style="right:0;top:0;bottom:0;width:1px;background:rgba(0,0,0,.6)"></div>'
    '<div class="frame" style="left:1px;right:1px;top:-2px;bottom:1px;border:1px solid #B8954F;border-top:none"></div>'
    '<div class="frame" style="left:5px;right:5px;top:-2px;bottom:5px;border:1px solid rgba(201,165,90,.45);border-top:none"></div>'
    '<i class="ck bl"></i><i class="ck br"></i>')

# ---------------------------------------------------------------- side panels (v0.5, make_panels.py)
# Each panel's header strip, as the politics screen's (HEAD above): lacquer round a notch for the top bar's
# flag medallion and decisions seal, the frame's verticals, the notch's gilt edge, the jade wash and the rule
# under the title. One picture per panel width and screen x (the notch's place in the panel depends on both).
import layout_panels as LPN


def panel_head(w, px):
    nb, hh = LPN.NB, LPN.HEAD_H
    region = f"M0 0 H{w} V{nb} H0 Z"
    lac = ('<div class="lac" style="position:absolute;inset:0;opacity:.97"></div>'
           f'<div style="position:absolute;left:0;top:0;width:{w}px;height:{LP.HEAD_GLOW_H}px;'
           'background:linear-gradient(180deg,rgba(46,110,96,.22),rgba(46,110,96,0))"></div>'
           f'<div style="position:absolute;left:0;top:0;width:{w}px;height:12px;'
           'background:linear-gradient(180deg,rgba(0,0,0,.55),rgba(0,0,0,0))"></div>')
    out = (f'<div style="position:absolute;left:0;top:0;width:{w}px;height:{nb}px;'
           f"clip-path:path(evenodd,'{region} {path_d(LPN.notch_outline(0, px))}')\">{lac}</div>")
    for x, col in ((0, "rgba(0,0,0,.6)"), (1, "#B8954F"), (5, "rgba(201,165,90,.45)")):
        for xx in (x, w - 1 - x):
            out += f'<div style="position:absolute;left:{xx}px;top:0;width:1px;height:{nb}px;background:{col}"></div>'
    for d_out, d_in, fill in ((1, 0, "#C9A55A"), (2, 1, "rgba(0,0,0,.45)"), (5, 4, "rgba(201,165,90,.45)")):
        out += (f'<div style="position:absolute;left:0;top:0;width:{w}px;height:{hh}px;background:{fill};'
                f"clip-path:path(evenodd,'{path_d(LPN.notch_outline(d_out, px))} {path_d(LPN.notch_outline(d_in, px))}')\"></div>")
    out += f'<div style="position:absolute;left:0;top:0;width:{w}px;height:{nb}px"><i class="ck tr"></i></div>'
    hx = LPN.hx(px)
    out += hrule(hx - 2, LPN.RULE_Y, w - 6 - (hx - 2),
                 "linear-gradient(90deg,rgba(201,165,90,.15),#C9A55A 12%,#C9A55A 88%,rgba(201,165,90,.1))")
    return out


for _w, _px in LPN.HEADS:
    add(f"panel_head_{_w}_{_px}".replace("-", "m"), LPN.head_texture(_w, _px), _w, LPN.HEAD_H, panel_head(_w, _px))

# section art over the body, under everything else (its own icon, valsora_deco_pol_sections)
SEC = ""
# sunburst behind the portrait
SB = LP.SUNBURST
SEC += sunburst(SB["cx"], SB["cy"], SB["r"])
# ideology chip
C = LP.CHIP
SEC += f'<div style="position:absolute;left:{C["x"]}px;top:{C["y"]}px;width:{C["w"]}px;height:{C["h"]}px;box-shadow:inset 0 0 0 1px rgba(201,165,90,.45)"></div>'
# a faint divider between the grid's two columns (its first two rows), a hairline above the sub-ideology row
gx = LP.GRID_X[1] - 6
SEC += (f'<div style="position:absolute;left:{gx}px;top:{LP.GRID_LABEL_Y[0]}px;width:1px;height:{LP.GRID_VALUE_Y[1] + LP.GRID_VALUE_H - LP.GRID_LABEL_Y[0] - 8}px;'
        'background:linear-gradient(180deg,transparent,rgba(201,165,90,.35) 20%,rgba(201,165,90,.35) 80%,transparent)"></div>')
SEC += hrule(LP.RX, LP.GRID_LABEL_Y[2] - 9, LP.X1 - LP.RX, "linear-gradient(90deg,rgba(201,165,90,.35),rgba(201,165,90,.05))")
# section rules after each label (label widths measured from the generated font)
for key, (x, y, text) in LP.SECTION_LABELS.items():
    lw = L.measure("valsora_deco_section_11", text.upper())
    x0 = x + lw + 12
    SEC += dbl_rule(x0, y + 3, LP.SECTION_ENDS[key] - x0)
# national spirits card (mockup: gilt-edged card with a warm wash)
S_ = LP.SPIRITS
SEC += (f'<div style="position:absolute;left:{S_["x"]}px;top:{S_["y"]}px;width:{S_["w"]}px;height:{S_["h"]}px;'
        'background:linear-gradient(90deg,rgba(122,42,38,.28),rgba(122,42,38,0) 70%),rgba(6,10,12,.35);box-shadow:inset 0 0 0 1px rgba(201,165,90,.45)"></div>')
add("pol_sections", P + "pol_sections.dds", PW, LP.IDEAS_Y, clipped(SEC, LP.IDEAS_Y))

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
    # (the panel's own lacquer, stripes in phase: the frame sits at x 16, a multiple of their 8 px)
    f'<div style="position:absolute;inset:0;clip-path:path(evenodd,\'M0 0H{FW}V{FH}H0Z {inner}\');background:repeating-linear-gradient(90deg,rgba(255,255,255,.028) 0 1px,transparent 1px 8px),#11191E">'
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

# ---------------------------------------------------------------- national focus tree (v0.6: the FocusTree mockup)
import layout_focus as LF

NF = "gfx/interface/valsora_deco/focus/"
FV = "gfx/interface/focusview/"          # the game's own paths, for the textures replaced in place


def nf_header():
    """the header: a cornered tile stretched to the window's width. Its left 260 px hold the notch round the top
    bar's medallion and seal (with the panels' gilt edge), its right 260 px the frame's end and bracket, the 96 px
    between repeat. Lacquer, the jade wash, and a gilt rule along its foot (the mockup's border under the header)."""
    w, h = LF.HEAD_TILE_W, LF.HEAD_H
    notch = path_d(LPN.notch_outline(0, LF.WIN_X))
    lac = ('<div class="lac" style="position:absolute;inset:0;opacity:.97"></div>'
           f'<div style="position:absolute;left:0;top:0;width:{w}px;height:{h}px;'
           'background:linear-gradient(180deg,rgba(46,110,96,.22),rgba(46,110,96,0))"></div>'
           f'<div style="position:absolute;left:0;top:0;width:{w}px;height:12px;'
           'background:linear-gradient(180deg,rgba(0,0,0,.55),rgba(0,0,0,0))"></div>')
    out = (f'<div style="position:absolute;left:0;top:0;width:{w}px;height:{h}px;'
           f"clip-path:path(evenodd,'M0 0 H{w} V{h} H0 Z {notch}')\">{lac}</div>")
    for x, col in ((0, "rgba(0,0,0,.6)"), (1, "#B8954F"), (5, "rgba(201,165,90,.45)")):
        for xx in (x, w - 1 - x):
            out += f'<div style="position:absolute;left:{xx}px;top:0;width:1px;height:{h}px;background:{col}"></div>'
    for d_out, d_in, fill in ((1, 0, "#C9A55A"), (2, 1, "rgba(0,0,0,.45)"), (5, 4, "rgba(201,165,90,.45)")):
        out += (f'<div style="position:absolute;left:0;top:0;width:{w}px;height:{h}px;background:{fill};'
                f"clip-path:path(evenodd,'{path_d(LPN.notch_outline(d_out, LF.WIN_X))} "
                f"{path_d(LPN.notch_outline(d_in, LF.WIN_X))}')\"></div>")
    out += f'<div style="position:absolute;left:0;top:0;width:{w}px;height:{h}px"><i class="ck tr"></i></div>'
    return out + hrule(0, h - 2, w, "rgba(201,165,90,.6)") + hrule(0, h - 1, w, "#0B1014")


add("nf_header", NF + "header.dds", LF.HEAD_TILE_W, LF.HEAD_H, nf_header())
# the tree's canvas: the mockup's scales (rings of 25.5 and 31.5 px round the foot of each 64 x 32 tile, a second
# layer shifted by 32, 16) on dark jade; 192 px repeats seamlessly in the cornered tile's centre
_RINGS = ("radial-gradient(circle at 50% 100%,transparent 0 25px,rgba(201,165,90,.10) 25px 26px,transparent 26px 31px,"
          "rgba(201,165,90,.06) 31px 32px,transparent 32px)")
add("nf_tree_bg", NF + "tree_bg.dds", LF.TREE_TILE, LF.TREE_TILE,
    f'<div style="position:absolute;inset:0;background-image:{_RINGS},{_RINGS};background-size:64px 32px,64px 32px;'
    'background-position:0 0,32px 16px;background-color:#111B1B"></div>')
# over the tree: the vignette (the mockup's canvas darkens to #0B1113 at its edges) and the panel's frame, its
# verticals and foot with the big corner brackets (a cornered tile: the corners stay, the edges stretch)
add("nf_vignette", NF + "vignette.dds", 512, 512,
    '<div style="position:absolute;inset:0;background:'
    'linear-gradient(90deg,rgba(5,8,10,.55),rgba(5,8,10,0) 26%,rgba(5,8,10,0) 74%,rgba(5,8,10,.55)),'
    'linear-gradient(180deg,rgba(5,8,10,.25),rgba(5,8,10,0) 18%,rgba(5,8,10,0) 76%,rgba(5,8,10,.55))"></div>'
    + "".join(f'<div style="position:absolute;left:{xx}px;top:0;width:1px;height:512px;background:{col}"></div>'
              for x, col in ((0, "rgba(0,0,0,.6)"), (1, "#B8954F"), (5, "rgba(201,165,90,.45)")) for xx in (x, 511 - x))
    + "".join(f'<div style="position:absolute;left:0;top:{yy}px;width:512px;height:1px;background:{col}"></div>'
              for yy, col in ((511, "rgba(0,0,0,.6)"), (510, "#B8954F"), (506, "rgba(201,165,90,.45)")))
    + '<i class="ck bl"></i><i class="ck br"></i>')

# a focus: the medallion behind its icon and the plate under it, one picture per state (the game swaps the bg
# button's sprite: unavailable, can start, current (in progress), completed; the first three at the game's paths,
# the current one at ours, since the game draws it from the can-start picture: make_focus patches its sprite)
BW, BH = LF.BG["w"], LF.BG["h"]
MD = LF.MEDALLION
MX, MY = BW / 2 - MD / 2, (LF.ICON_C[1] - LF.BG["y"]) - MD / 2
_OCT = "polygon(29% 0,71% 0,100% 29%,100% 71%,71% 100%,29% 100%,0 71%,0 29%)"
_CH = "polygon(10px 0,calc(100% - 10px) 0,100% 10px,100% 100%,0 100%,0 10px)"
_CH_IN = "polygon(9.5px 0,calc(100% - 9.5px) 0,100% 9.5px,100% 100%,0 100%,0 9.5px)"


def nf_node(rim, inner, plate_rim, plate_fill, extra="", filt=""):
    py, ph = LF.PLATE["y"], LF.PLATE["h"]
    return (f'<div style="position:absolute;inset:0;{filt}">'
            f'<div style="position:absolute;left:{MX}px;top:{MY}px;width:{MD}px;height:{MD}px;padding:2px;box-sizing:border-box;'
            f'background:{rim};clip-path:{_OCT}"><div style="width:100%;height:100%;clip-path:{_OCT};background:{inner}"></div></div>'
            f'<div style="position:absolute;left:0;top:{py}px;width:{BW}px;height:{ph}px;padding:1px;box-sizing:border-box;'
            f'background:{plate_rim};clip-path:{_CH}"><div style="width:100%;height:100%;clip-path:{_CH_IN};'
            f'background:{LAC},{plate_fill}"></div></div>{extra}</div>')


_RAYS = "repeating-conic-gradient({c} 0deg 5deg,transparent 5deg 15deg)"
_GILT_RIM = "linear-gradient(180deg,#F1DC9C,#8B6A2C)"
_BRIGHT_RIM = "linear-gradient(180deg,#FFF3C8,#C9A55A)"
_DARK_PLATE = "linear-gradient(180deg,#1E2930,#0E1519)"
_JADE = _RAYS.format(c="rgba(227,199,126,.2)") + ",radial-gradient(circle,#27493F 0%,#0E1A18 72%)"
_CHECK = (f'<div style="position:absolute;left:{BW / 2 + 22}px;top:{MY + 6}px;width:20px;height:20px;transform:rotate(45deg);'
          'background:linear-gradient(180deg,#2E6E60,#153730);border:1px solid #F6E3A6;box-sizing:border-box"></div>'
          f'<svg width="20" height="20" viewBox="0 0 24 24" style="position:absolute;left:{BW / 2 + 22}px;top:{MY + 6}px" '
          'fill="none" stroke="#F6E3A6" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">'
          '<path d="M7 12.5l3.2 3.2L17 9"/></svg>')
_NODES = {
    "can_start": nf_node(_GILT_RIM, _JADE, GOLD_V, _DARK_PLATE),
    "unavailable": nf_node(_GILT_RIM, _JADE, GOLD_V, _DARK_PLATE, filt="filter:grayscale(.85) brightness(.5)"),
    # completed: the mockup's gold medallion; the plate a deep gold, since the game's name stays cream
    "completed": nf_node(_BRIGHT_RIM, _RAYS.format(c="rgba(255,248,220,.4)") + ",radial-gradient(circle,#F6E3A6 0%,#B48F44 78%)",
                         "linear-gradient(180deg,#FFF3C8,#B48F44)",
                         "linear-gradient(180deg,rgba(255,240,190,.20),rgba(255,240,190,0) 45%),linear-gradient(180deg,#8C6C2C,#5E4718 55%,#46340F)",
                         extra=_CHECK),
    "current": nf_node(_BRIGHT_RIM, _RAYS.format(c="rgba(246,227,166,.32)") + ",radial-gradient(circle,#6B2B26 0%,#2A0F0D 75%)",
                       "linear-gradient(180deg,#FFF3C8,#B48F44)", _DARK_PLATE),
}
for _k in ("unavailable", "can_start", "completed"):
    add("nf_node_" + _k, FV + f"titlebar/focus_{_k}_bg.dds", BW, BH, _NODES[_k])
add("nf_node_current", NF + "current_bg.dds", BW, BH, _NODES["current"])
# the completed focus's shine (the game's scrolling gold streaks, added where this mask is white): sparkles on the
# medallion's rays and along the plate's top
import random as _random
_rng = _random.Random(7)
_spark = ""
for _ in range(34):
    if _rng.random() < .55:
        _x, _y = MX + 8 + _rng.random() * (MD - 16), MY + 8 + _rng.random() * (MD - 16)
    else:
        _x, _y = 6 + _rng.random() * (BW - 12), LF.PLATE["y"] + 3 + _rng.random() * 8
    _r = 1 + _rng.random() * 1.6
    _spark += (f'<div style="position:absolute;left:{_x - 3 * _r:.1f}px;top:{_y - 3 * _r:.1f}px;width:{6 * _r:.1f}px;'
               f'height:{6 * _r:.1f}px;border-radius:50%;background:radial-gradient(circle,#fff 0,rgba(255,255,255,.6) 18%,transparent 60%)"></div>')
add("nf_completed_mask", FV + "titlebar/focus_completed_mask.dds", BW, BH,
    f'<div style="position:absolute;inset:0;background:#000"></div>{_spark}')

# the in-progress halo (the game's GFX_ongoing_focus_goal behind the current focus; 3 frames it blends, 1 a second):
# the mockup's ring of gilt rays round the medallion, and its glow
H_ = LF.HALO


def nf_halo(rot, glow, ray="rgba(246,227,166,.55)", glow_rgb="241,220,156"):
    c = H_ / 2
    return (f'<div style="position:absolute;inset:0;background:radial-gradient(circle,rgba({glow_rgb},{glow}) 0 34%,rgba({glow_rgb},0) 70%)"></div>'
            f'<div style="position:absolute;left:{c - 70}px;top:{c - 70}px;width:140px;height:140px;border-radius:50%;'
            f'background:repeating-conic-gradient(from {rot}deg,{ray} 0deg 3deg,transparent 3deg 12deg);'
            '-webkit-mask:radial-gradient(circle,transparent 46px,#000 47px,#000 60px,transparent 70px)"></div>')


add("nf_halo", "gfx/interface/ongoing_focus_goal.dds", 3 * H_, H_,
    "".join(f'<div style="position:absolute;left:{i * H_}px;top:0;width:{H_}px;height:{H_}px">{nf_halo(4 + 4 * i, g)}</div>'
            for i, g in enumerate((.30, .40, .32))))
# the search result's highlight (GFX_highlight_focus_goal): the same ring in jade
add("nf_search_glow", "gfx/interface/search_current_focus.dds", 3 * H_, H_,
    "".join(f'<div style="position:absolute;left:{i * H_}px;top:0;width:{H_}px;height:{H_}px">'
            f'{nf_halo(2 + 4 * i, g, "rgba(170,230,200,.55)", "70,160,135")}</div>'
            for i, g in enumerate((.35, .48, .38))))


# the links between focuses: the game draws them from 16 px tiles, 4 frames each (frames 1-2: the game's green,
# 3-4: its blue-grey; 2 and 4 dashed), a 4 px line through columns / rows 6-9. Gilt here: bright with a glow, then
# dim bronze. One div per pixel, so junctions do not double their alpha.
def link_tile(arms, frame):
    bright, dashed = frame in (1, 2), frame in (2, 4)
    prof = ({-1: "rgba(241,220,156,.16)", 0: "#8A6B32", 1: "#F6E3A6", 2: "#E3C77E", 3: "#8A6B32", 4: "rgba(241,220,156,.16)"}
            if bright else {0: "rgba(110,84,38,.35)", 1: "rgba(176,140,70,.62)", 2: "rgba(176,140,70,.62)", 3: "rgba(110,84,38,.35)"})
    rank = {"rgba(241,220,156,.16)": 0, "rgba(110,84,38,.35)": 1, "#8A6B32": 2, "rgba(176,140,70,.62)": 3, "#E3C77E": 4, "#F6E3A6": 5}
    out = ""
    for y in range(16):
        for x in range(16):
            best = None
            for arm in arms:
                vertical = arm in ("up", "down")
                c, t = (x - 6, y) if vertical else (y - 6, x)
                lo, hi = {"up": (0, 9), "down": (6, 15), "left": (0, 9), "right": (6, 15)}[arm]
                if c not in prof or not lo <= t <= hi:
                    continue
                if dashed and not ((t + 2) % 8) < 4:
                    continue
                col = prof[c]
                if best is None or rank[col] > rank[best]:
                    best = col
            if best:
                out += f'<div style="position:absolute;left:{x}px;top:{y}px;width:1px;height:1px;background:{best}"></div>'
    return out


for _name, _arms in (("up_down", ("up", "down")), ("left_right", ("left", "right")), ("down_left", ("down", "left")),
                     ("down_right", ("down", "right")), ("up_left", ("up", "left")), ("up_right", ("up", "right")),
                     ("down_left_right", ("down", "left", "right")), ("up_down_left", ("up", "down", "left")),
                     ("up_down_right", ("up", "down", "right")), ("up_left_right", ("up", "left", "right")),
                     ("up_down_left_right", ("up", "down", "left", "right"))):
    add(f"nf_link_{_name}", FV + f"focus_link_{_name}.dds", 64, 16,
        "".join(f'<div style="position:absolute;left:{16 * f}px;top:0;width:16px;height:16px">{link_tile(_arms, f + 1)}</div>'
                for f in range(4)))


# mutually exclusive focuses: the line between them (two layers, 4 frames: 1 and 4 solid, 2 and 3 dashed, as the
# game's) in red, and the mockup's red diamond with a cross in the middle; small red diamonds at the ends
def excl_line(core, soft):
    out = ""
    for f in range(4):
        for x in range(16):
            if f in (1, 2) and not ((x + 2) % 8) < 5:
                continue
            for y, col in ((6, soft), (7, core), (8, core), (9, soft)):
                out += f'<div style="position:absolute;left:{16 * f + x}px;top:{y}px;width:1px;height:1px;background:{col}"></div>'
    return out


add("nf_excl_line1", FV + "focus_exlusive_link_line1.dds", 64, 16, excl_line("rgba(180,71,60,.85)", "rgba(124,42,38,.45)"))
add("nf_excl_line2", FV + "focus_exlusive_link_line2.dds", 64, 16, excl_line("#E8877A", "rgba(180,71,60,.6)"))


def excl_diamond(cx, cy, d, cross):
    out = (f'<div style="position:absolute;left:{cx - d / 2}px;top:{cy - d / 2}px;width:{d}px;height:{d}px;transform:rotate(45deg);'
           'background:linear-gradient(180deg,#7C2A26,#3E1412);border:1px solid #E8877A;box-sizing:border-box"></div>')
    if cross:
        out += (f'<svg width="12" height="12" viewBox="0 0 12 12" style="position:absolute;left:{cx - 6}px;top:{cy - 6}px" '
                'fill="none" stroke="#F6D0C8" stroke-width="1.6" stroke-linecap="round"><path d="M3 3l6 6M9 3l-6 6"/></svg>')
    return out


add("nf_excl", FV + "focus_link_exclusive.dds", 96, 32,
    f'<div style="position:absolute;left:0;top:0;width:32px;height:32px">{excl_diamond(16, 16, 18, True)}</div>'
    f'<div style="position:absolute;left:32px;top:0;width:32px;height:32px">{excl_diamond(7, 16, 8, False)}</div>'
    f'<div style="position:absolute;left:64px;top:0;width:32px;height:32px">{excl_diamond(25, 16, 8, False)}</div>')
# the continuous focus window's progress marks (2 frames: to come, done)
add("nf_cont_check", "gfx/interface/cont_focus_check_icon.dds", 64, 32,
    '<div style="position:absolute;left:7px;top:7px;width:18px;height:18px;transform:rotate(45deg);background:#0B1014;'
    'border:1px solid rgba(201,165,90,.7);box-sizing:border-box"></div>'
    '<div style="position:absolute;left:39px;top:7px;width:18px;height:18px;transform:rotate(45deg);'
    'background:linear-gradient(180deg,#2E6E60,#153730);border:1px solid #F6E3A6;box-sizing:border-box"></div>'
    '<svg width="18" height="18" viewBox="0 0 24 24" style="position:absolute;left:39px;top:7px" fill="none" stroke="#F6E3A6" '
    'stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"><path d="M7 12.5l3.2 3.2L17 9"/></svg>')
# search box, zoom, filter chips
SW_, SH_ = LF.SEARCH["w"], LF.SEARCH["h"]
add("nf_search", NF + "search.dds", SW_, SH_,
    plate([(10, 0), (SW_ - 10, 0), (SW_, SH_ / 2), (SW_ - 10, SH_), (10, SH_), (0, SH_ / 2)], "linear-gradient(180deg,#0E1519,#0A0F12)")
    + f'<div style="position:absolute;left:12px;top:{SH_ / 2 - 9}px;width:18px;height:18px">{svg("search", 18)}</div>'
    + f'<div style="position:absolute;left:36px;top:9px;width:1px;height:{SH_ - 18}px;background:rgba(201,165,90,.45)"></div>')
Z_ = LF.ZOOM_D


def zoom_btn(glyph):
    return (f'<div style="position:absolute;left:{Z_ / 2 - 10.5}px;top:{Z_ / 2 - 10.5}px;width:21px;height:21px;transform:rotate(45deg);'
            'border:1px solid #C9A55A;background:#0B1014;box-sizing:border-box"></div>'
            f'<svg width="{Z_}" height="{Z_}" style="position:absolute;left:0;top:0" fill="none" stroke="#E3C77E" stroke-width="1.8">{glyph}</svg>')


add("nf_zoom_in", NF + "zoom_in.dds", Z_, Z_, zoom_btn(f'<path d="M{Z_ / 2 - 5} {Z_ / 2}h10M{Z_ / 2} {Z_ / 2 - 5}v10"/>'))
add("nf_zoom_out", NF + "zoom_out.dds", Z_, Z_, zoom_btn(f'<path d="M{Z_ / 2 - 5} {Z_ / 2}h10"/>'))
FL = LF.FILTER


def filter_chip(on):
    # the mockup's chips: lacquer with a faint gilt edge, jade with a bright one when on
    o = oct_(FL, 9)
    return plate(o, "linear-gradient(180deg,#2E6E60,#153730)" if on else "linear-gradient(180deg,#121B20,#0E1519)",
                 "linear-gradient(180deg,#FFF3C8,#E3C77E)" if on else "linear-gradient(180deg,rgba(201,165,90,.75),rgba(201,165,90,.45))")


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
# legend (lower right): the mockup's four marks, with English labels
LGW, LGH = LF.LEGEND["w"], LF.LEGEND["h"]
_LEG = [('<div style="width:12px;height:12px;border-radius:50%;background:radial-gradient(circle,#F6E3A6,#B48F44);'
         'box-shadow:0 0 0 1px #8B6A2C"></div>', "Completed"),
        ('<div style="width:12px;height:12px;border-radius:50%;box-sizing:border-box;border:2px solid #F1DC9C;'
         'background:radial-gradient(circle,#6B2B26,#2A0F0D)"></div>', "In progress"),
        (f'<div style="width:13px;height:13px;clip-path:{_OCT};background:{_GILT_RIM};padding:1.5px;box-sizing:border-box">'
         f'<div style="width:100%;height:100%;clip-path:{_OCT};background:radial-gradient(circle,#27493F,#0E1A18)"></div></div>', "Available"),
        ('<div style="width:10px;height:10px;transform:rotate(45deg);background:linear-gradient(180deg,#7C2A26,#3E1412);'
         'border:1px solid #E8877A;box-sizing:border-box;margin:0 2px"></div>', "Mutually exclusive")]
add("nf_legend", NF + "legend.dds", LGW, LGH,
    plate([(8, 0), (LGW - 8, 0), (LGW, 8), (LGW, LGH - 8), (LGW - 8, LGH), (8, LGH), (0, LGH - 8), (0, 8)],
          "linear-gradient(180deg,rgba(23,32,38,.95),rgba(11,17,21,.95))")
    + '<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;gap:20px;'
      "font:600 10px/1 'Josefin Sans';letter-spacing:.14em;text-transform:uppercase;color:#CBBF9F\">"
    + "".join(f'<div style="display:flex;align-items:center;gap:8px"><div style="flex:none">{sw}</div>'
              f'<span style="padding-top:2px">{lab}</span></div>' for sw, lab in _LEG) + '</div>')

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


# ---------------------------------------------------------------- army bar (v0.7: interface/leadergroups.gui)
# The armies along the bottom of the screen (the user, after v0.2: "The armies at the bottom of the screen ... don't
# have the same custom touch as the rest of the UI"). Replaced at the game's paths, sizes and frame counts only: the
# game's leadergroups.gui and .gfx stay as they are. Each card frame is drawn over the portrait (the game puts the
# portrait at the frame's (9, 7), 61 x 82 for an army; (9, 6), 70 x 94 for an army group), so its arched opening
# shows the portrait and its plaque holds the division count. Frames keep the game's order: army cards normal,
# selected, then the same without the plaque; army groups normal, selected, plain. Selected is jade, as everywhere.
UC = "gfx/interface/unitcontrol/"
LG_GOLD = ('<linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F1DC9C"/>'
           '<stop offset="1" stop-color="#8B6A2C"/></linearGradient>'
           '<linearGradient id="gb" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFF3C8"/>'
           '<stop offset="1" stop-color="#C9A55A"/></linearGradient>'
           '<linearGradient id="pf" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1E2A31"/>'
           '<stop offset="1" stop-color="#0B1014"/></linearGradient>'
           '<linearGradient id="pj" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2C665A"/>'
           '<stop offset="1" stop-color="#123029"/></linearGradient>'
           '<pattern id="pin" width="8" height="8" patternUnits="userSpaceOnUse"><rect width="8" height="8" fill="#11191E"/>'
           '<rect width="1" height="8" fill="#1A2329"/></pattern>')


def _cham(x0, y0, x1, y1, c):
    return f"M{x0 + c},{y0}L{x1 - c},{y0}L{x1},{y0 + c}L{x1},{y1 - c}L{x1 - c},{y1}L{x0 + c},{y1}L{x0},{y1 - c}L{x0},{y0 + c}Z"


def _arch(x0, x1, top, sh, bottom):
    return f"M{x0},{bottom}L{x0},{sh}A{(x1 - x0) / 2},{sh - top} 0 0 1 {x1},{sh}L{x1},{bottom}Z"


def lg_frame(W, H, hole, body, plaque, selected, flat=False, marshal=False):
    """a leader card frame: lacquer with an arched opening for the portrait, gilt rims, the plaque for the count"""
    x0, x1, top, sh, bottom = hole
    bx0, by0, bx1, by1 = body
    px0, py0, px1, py1 = plaque
    rim = "url(#gb)" if selected else "url(#g)"
    b, inner = _cham(bx0, by0, bx1, by1, 5), _cham(bx0 + 3, by0 + 3, bx1 - 3, by1 - 3, 3.5)
    h = _arch(x0, x1, top, sh, bottom)
    s = [f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="position:absolute;left:0;top:0"><defs>{LG_GOLD}'
         f'<clipPath id="bc"><path d="{b}{h}" clip-rule="evenodd"/></clipPath></defs>',
         f'<path d="{b}{h}" fill="url(#pin)" fill-rule="evenodd"/>']
    if marshal and not flat:     # an army group's card: gilt fans in the top corners, beside the arch
        for cx, sx in ((bx0 + 1, 1), (bx1 - 1, -1)):
            for a in range(8, 90, 9):
                import math
                r = 16
                s.append(f'<line x1="{cx}" y1="{by0 + 1}" x2="{cx + sx * r * math.cos(math.radians(a)):.2f}" '
                         f'y2="{by0 + 1 + r * math.sin(math.radians(a)):.2f}" stroke="rgba(227,199,126,.38)" '
                         f'stroke-width=".8" clip-path="url(#bc)"/>')
    if selected:                 # jade: a lit line inside the rim and a glow round the opening; the plaque jade
        s.append(f'<path d="{_cham(bx0 + 2, by0 + 2, bx1 - 2, by1 - 2, 4)}" fill="none" stroke="#6CC2A9" '
                 f'stroke-width="2"/>')
        s.append(f'<path d="{h}" fill="none" stroke="#6CC2A9" stroke-width="4" opacity=".75" clip-path="url(#bc)"/>')
    s.append(f'<path d="{b}" fill="none" stroke="{rim}" stroke-width="{2 if selected else 1.2}"/>')
    s.append(f'<path d="{inner}" fill="none" stroke="rgba(201,165,90,{.75 if marshal else .4})" stroke-width="1"/>')
    s.append(f'<path d="{h}" fill="none" stroke="{rim}" stroke-width="1.4"/>')
    pfill = "url(#pj)" if selected else "url(#pf)"
    if flat:
        s.append(f'<rect x="{px0}" y="{py0}" width="{px1 - px0}" height="{py1 - py0}" fill="{pfill}"/>'
                 f'<line x1="{px0}" y1="{py0 + .5}" x2="{px1}" y2="{py0 + .5}" stroke="{rim}" stroke-width="1"/>')
    else:
        m = (py0 + py1) / 2
        pts = f"{px0},{m} {px0 + 7},{py0} {px1 - 7},{py0} {px1},{m} {px1 - 7},{py1} {px0 + 7},{py1}"
        s.append(f'<polygon points="{pts}" fill="{pfill}" stroke="{rim}" stroke-width="1.1"/>')
        if marshal:              # small diamonds at the plaque's points
            for x in (px0 - 1, px1 + 1):
                s.append(f'<rect x="{x - 2.2}" y="{m - 2.2}" width="4.4" height="4.4" transform="rotate(45 {x} {m})" '
                         f'fill="{rim}"/>')
    return "".join(s) + "</svg>"


import layout_armybar as LAB
ARMY, GROUP = LAB.ARMY, LAB.GROUP
add("lg_frame", UC + "leader_group_frame.dds", 336, 117, frames(336, 117,
    lg_frame(84, 117, selected=False, **ARMY), lg_frame(84, 117, selected=True, **ARMY),
    lg_frame(84, 117, selected=False, flat=True, **ARMY), lg_frame(84, 117, selected=True, flat=True, **ARMY)))
add("lg_group_frame", UC + "leader_army_group_frame.dds", 270, 126, frames(270, 126,
    lg_frame(90, 126, selected=False, marshal=True, **GROUP), lg_frame(90, 126, selected=True, marshal=True, **GROUP),
    lg_frame(90, 126, selected=False, flat=True, marshal=True, **GROUP)))


def lg_strip(w, h, lit, chamfer=None):
    """the plate behind a run of armies: lacquer fading into the map below, a gilt rule along its top"""
    op = .9 if lit else .64
    clip = ""
    if chamfer == "right":
        clip = f"clip-path:polygon(0 0,{w - 12}px 0,{w}px 12px,{w}px 100%,0 100%);"
    elif chamfer == "left":
        clip = f"clip-path:polygon(12px 0,{w}px 0,{w}px 100%,0 100%,0 12px);"
    rule = f"rgba(201,165,90,{.85 if lit else .6})"
    s = (f'<div style="position:absolute;inset:0;{clip}-webkit-mask:linear-gradient(180deg,#000 0,#000 58%,transparent 100%)">'
         f'<div class="lac" style="position:absolute;inset:0;opacity:{op}"></div>'
         f'<div style="position:absolute;left:0;right:0;top:0;height:1px;background:{rule}"></div>'
         f'<div style="position:absolute;left:0;right:0;top:3px;height:1px;background:rgba(201,165,90,{.3 if lit else .18})"></div>')
    if chamfer == "right":
        s += (f'<svg width="{w}" height="{h}" style="position:absolute;left:0;top:0"><path d="M{w - 12},0.5L{w - .5},12V{h}" '
              f'fill="none" stroke="{rule}" stroke-width="1"/></svg>')
    elif chamfer == "left":
        s += (f'<svg width="{w}" height="{h}" style="position:absolute;left:0;top:0"><path d="M12,0.5L.5,12V{h}" '
              f'fill="none" stroke="{rule}" stroke-width="1"/></svg>')
    return s + "</div>"


add("lg_strip_mid", UC + "army_mid_bg.dds", 160, 149, frames(160, 149, lg_strip(80, 149, False), lg_strip(80, 149, True)))
add("lg_strip_end", UC + "army_end_bg.dds", 168, 150, frames(168, 150, lg_strip(84, 150, False, "right"),
                                                            lg_strip(84, 150, True, "right")))
# the game's is 175 px wide, two frames of 87.5 px
add("lg_strip_back", UC + "army_group_back_bg.dds", 175, 151, "".join(
    f'<div style="position:absolute;left:{i * 87.5}px;top:0;width:87.5px;height:151px">{lg_strip(87.5, 151, lit, "left")}</div>'
    for i, lit in enumerate((False, True))))

HATCH = "repeating-linear-gradient(135deg,rgba(201,165,90,.16) 0 2px,transparent 2px 6px)"


def lg_button(w, h, glyph, state):
    """the execute / stop chips: 1 normal, 2 hatched, 3 lit, 4 lit and hatched (the game's order and look)"""
    lit = state in (3, 4)
    s = lit_bar(4) if lit else bar(c=4, shine=.15)
    if state in (2, 4):
        s += f'<div style="position:absolute;inset:1px;clip-path:{chamfer(3.6)};background:{HATCH}"></div>'
    col = {1: "#E3C77E", 2: "#9C8A62", 3: "#FBEAB4", 4: "#D9C48E"}[state]
    return s + glyph(w, h, col, state)


def g_play(w, h, col, st, double=False):
    cx, cy = w / 2, h / 2
    if double:
        d = (f"M{cx - 8},{cy - 5.5}L{cx - 1},{cy}L{cx - 8},{cy + 5.5}Z" f"M{cx},{cy - 5.5}L{cx + 7},{cy}L{cx},{cy + 5.5}Z")
    else:
        d = f"M{cx - 4},{cy - 6}L{cx + 6},{cy}L{cx - 4},{cy + 6}Z"
    return f'<svg width="{w}" height="{h}" style="position:absolute;left:0;top:0"><path d="{d}" fill="{col}"/></svg>'


def g_stop(w, h, col, st, double=False):
    coral = {1: "#D8705F", 2: "#8E4F45", 3: "#EE8C7E", 4: "#B4675B"}[st]
    cx, cy = w / 2, h / 2
    sq = [(cx - 4.5, cy - 4.5)] if not double else [(cx - 6.5, cy - 6), (cx - 2.5, cy - 2.5)]
    return (f'<svg width="{w}" height="{h}" style="position:absolute;left:0;top:0">'
            + "".join(f'<rect x="{x}" y="{y}" width="9" height="9" fill="{coral}" stroke="{col}" stroke-width=".9"/>'
                      for x, y in sq) + "</svg>")


add("lg_play", UC + "execute_btn_play_small.dds", 172, 23, frames(172, 23, *[lg_button(43, 23, g_play, s) for s in (1, 2, 3, 4)]))
add("lg_play_ag", UC + "execute_btn_play_small_ag.dds", 172, 23, frames(172, 23, *[
    lg_button(43, 23, (lambda w, h, c, st: g_play(w, h, c, st, st > 2)), s) for s in (1, 2, 3, 4)]))
add("lg_stop", UC + "execute_btn_stop_small.dds", 112, 23, frames(112, 23, *[lg_button(28, 23, g_stop, s) for s in (1, 2, 3, 4)]))
add("lg_stop_ag", UC + "execute_btn_stop_small_ag.dds", 112, 23, frames(112, 23, *[
    lg_button(28, 23, (lambda w, h, c, st: g_stop(w, h, c, st, st > 2)), s) for s in (1, 2, 3, 4)]))
add("lg_buttons_bg", UC + "execute_stop_small_bg.dds", 78, 26, bar(DIM_FILL, c=5, shine=.12))
add("lg_border_war_bg", UC + "excecute_stop_border_war_bg.dds", 73, 27,
    bar(DIM_FILL, "#E7B75A", 5, .12) + f'<div style="position:absolute;inset:1px;clip-path:{chamfer(4.6)};'
    'background:repeating-linear-gradient(135deg,rgba(231,183,90,.28) 0 3px,transparent 3px 8px)"></div>')
add("lg_no_order", UC + "execute_button_no_order.dds", 82, 37, bar(c=6, shine=.15))
# the battle plan in progress, over the execute button: gilt chevrons running right on jade (12 frames, a loop)
add("lg_plan_anim", UC + "active_battleplan_anim.dds", 528, 20, frames(528, 20, *[
    lit_bar(4) + '<svg width="44" height="20" style="position:absolute;left:0;top:0"><defs><clipPath id="ca">'
    f'<path d="{_cham(1, 1, 43, 19, 3.6)}"/></clipPath></defs><g clip-path="url(#ca)">'
    + "".join(f'<path d="M{x - 3},5L{x + 2},10L{x - 3},15" fill="none" stroke="#F1DC9C" stroke-width="2" '
              f'stroke-linecap="round" stroke-linejoin="round" opacity="{.45 + .55 * ((x - 2) / 46)}"/>'
              for x in [2 + k * 11 + i * 11 / 12 for k in range(-1, 5)]) + "</g></svg>" for i in range(12)]))
add("lg_point_out", UC + "execute_button_point_out_mode.dds", 45, 26,
    f'<svg width="45" height="26" style="position:absolute;left:0;top:0"><path d="{_cham(1.5, 1.5, 43.5, 24.5, 4)}" fill="none" '
    'stroke="#E7B75A" stroke-width="1.5"/></svg>'
    '<svg width="45" height="26" style="position:absolute;left:0;top:0"><path d="M31,3L35,7L31,11M36,3L40,7L36,11" '
    'fill="none" stroke="#F1DC9C" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>')
add("lg_expand", UC + "army_group_expand_collapse.dds", 28, 20, frames(28, 20,
    chip(14, 20, False) + '<svg width="14" height="20" style="position:absolute;left:0;top:0"><path d="M5,6L10,10L5,14Z" fill="#E3C77E"/></svg>',
    chip(14, 20, False) + '<svg width="14" height="20" style="position:absolute;left:0;top:0"><path d="M9,6L4,10L9,14Z" fill="#E3C77E"/></svg>'))
add("lg_power", UC + "comm_group_plan_power_bar.dds", 59, 6,
    '<div style="position:absolute;inset:0;background:linear-gradient(180deg,#8FD0BB,#3E8E7A)"></div>'
    '<div style="position:absolute;left:0;right:0;top:0;height:1px;background:rgba(241,220,156,.7)"></div>')
add("lg_power_bg", UC + "comm_group_plan_power_bar_bg.dds", 59, 6,
    '<div style="position:absolute;inset:0;background:linear-gradient(180deg,#C46A5C,#6E2E26)"></div>'
    '<div style="position:absolute;left:0;right:0;top:0;height:1px;background:rgba(241,220,156,.35)"></div>')
add("lg_disband", UC + "disband_orders_group.dds", 16, 16,
    '<div style="position:absolute;left:2.5px;top:2.5px;width:11px;height:11px;transform:rotate(45deg);background:#0B1014;'
    'border:1px solid #C9A55A;box-sizing:border-box"></div>'
    '<svg width="16" height="16" style="position:absolute;left:0;top:0"><path d="M5.6,5.6L10.4,10.4M10.4,5.6L5.6,10.4" '
    'stroke="#F1DC9C" stroke-width="1.3" stroke-linecap="round"/></svg>')
add("lg_air_bg", "gfx/interface/attached_air_bg.dds", 39, 45, bar(c=4, shine=.15))


def lg_add(w, h, lit, cx, plus=True):
    """the empty card asking for a commander: a gilt line bust and a plus medallion, centred on the frame's opening
    (cx: the game draws this picture 1.5 px left of the opening's centre on an army card)"""
    hr, hy = w * .18, h * .36
    sh = h * .58
    half = w * .36
    s = (f'<div style="position:absolute;inset:0;background:radial-gradient(ellipse at {cx}px 40%,#1E2A31,#0B1014 75%)"></div>'
         f'<svg width="{w}" height="{h}" style="position:absolute;left:0;top:0">'
         f'<circle cx="{cx}" cy="{hy}" r="{hr}" fill="none" stroke="rgba(227,199,126,.55)" stroke-width="1.3"/>'
         f'<path d="M{cx - half},{h * .92}C{cx - half},{sh + 6} {cx - hr - 4},{sh} {cx},{sh}C{cx + hr + 4},{sh} {cx + half},{sh + 6} '
         f'{cx + half},{h * .92}" fill="none" stroke="rgba(227,199,126,.55)" stroke-width="1.3"/>')
    if plus:
        r = 9
        my = h * .75
        fill, rim, pc = ("#2C665A", "#F1DC9C", "#FBEAB4") if lit else ("#11191E", "#C9A55A", "#E3C77E")
        s += (f'<rect x="{cx - r}" y="{my - r}" width="{2 * r}" height="{2 * r}" transform="rotate(45 {cx} {my})" fill="{fill}" '
              f'stroke="{rim}" stroke-width="1"/>'
              f'<path d="M{cx - 5},{my}H{cx + 5}M{cx},{my - 5}V{my + 5}" stroke="{pc}" stroke-width="1.8" stroke-linecap="round"/>')
    return s + "</svg>"


_ca = LAB.hole_centre(ARMY, LAB.FRAME_ARMY, LAB.ADD_ARMY)[0]
_cg = LAB.hole_centre(GROUP, LAB.FRAME_GROUP, LAB.ADD_GROUP)[0]
add("lg_add_bg", UC + "group_add_leader_bg.dds", 61, 83, lg_add(61, 83, False, _ca))
add("lg_add", UC + "group_add_leader.dds", 122, 83, frames(122, 83, lg_add(61, 83, False, _ca), lg_add(61, 83, True, _ca)))
add("lg_add_marshal_bg", UC + "group_add_marshal_bg.dds", 70, 96, lg_add(70, 96, False, _cg))
add("lg_add_marshal", UC + "group_add_marshal.dds", 140, 96, frames(140, 96, lg_add(70, 96, False, _cg), lg_add(70, 96, True, _cg)))
# a commander's headquarters needs attention: frame 2 (frame 1 is the game's blank, the blink)
add("lg_hq_alert", UC + "hq_alert.dds", 122, 83, frames(122, 83, "",
    f'<div style="position:absolute;inset:0;background:rgba(238,140,126,.16);box-shadow:inset 0 0 0 2px #EE8C7E"></div>'
    '<div style="position:absolute;left:44px;top:5px;width:12px;height:12px;transform:rotate(45deg);background:#EE8C7E"></div>'
    '<svg width="61" height="83" style="position:absolute;left:0;top:0"><path d="M50,6.5V12.5" stroke="#1A0E0B" stroke-width="1.8" '
    'stroke-linecap="round"/><circle cx="50" cy="15.3" r="1" fill="#1A0E0B"/></svg>'))
add("lg_hq_badge", UC + "hq_badge.dds", 18, 27, img_tag(gilt(vanilla_frames(UC + "hq_badge.dds", 1)[0], 1.05)))
_gr = vanilla_frames(UC + "give_role_leader_strip.dds", 2)
add("lg_give_role", UC + "give_role_leader_strip.dds", 56, 28, frames(56, 28, img_tag(gilt(_gr[0])),
    '<div style="position:absolute;inset:1px;border:1px solid #5FB39C;border-radius:3px"></div>' + img_tag(gilt(_gr[1], 1.15))))

# ---------------------------------------------------------------- events (v0.7: interface/eventwindow.gui)
# The game's events are paper reports on a clipboard (country, leader and operative events) and a newspaper (news
# events). Their pictures are replaced at the game's paths and sizes, and make_events.py gives the window the mod's
# fonts (the game's typewriter fonts are dark, for paper). A country event is three pieces the game stacks: the top
# (title), the middle, stretched to the text (a cornered tile: 16 px kept at top and bottom), and the bottom (the
# picture at (5, 5), 210 x 176, and the options at x 215). In the superevent's style: lacquer, gilt rails, a crest.
EV = "gfx/interface/"
RAIL = ('<div class="frame" style="left:0;top:{t}px;bottom:{b}px;width:1px;background:#C9A55A"></div>'
        '<div class="frame" style="right:0;top:{t}px;bottom:{b}px;width:1px;background:#C9A55A"></div>'
        '<div class="frame" style="left:4px;top:{t2}px;bottom:{b2}px;width:1px;background:rgba(201,165,90,.35)"></div>'
        '<div class="frame" style="right:4px;top:{t2}px;bottom:{b2}px;width:1px;background:rgba(201,165,90,.35)"></div>')


def ev_crest(cx, base, r):
    """a half sunburst rising from the card's top edge, as the superevent's crest"""
    return (f'<div style="position:absolute;left:{cx - r}px;top:{base - r}px;width:{2 * r}px;height:{r}px;overflow:hidden">'
            f'<div style="position:absolute;left:0;top:0;width:{2 * r}px;height:{2 * r}px;border-radius:50%;'
            'background:repeating-conic-gradient(from -90deg,rgba(227,199,126,.55) 0deg 2.5deg,transparent 2.5deg 12deg),'
            'radial-gradient(circle,#1E2A31 0 55%,#11191E 56%)"></div>'
            f'<div style="position:absolute;left:{r * .38}px;top:{r * .38}px;width:{r * 1.24}px;height:{r * 1.24}px;border-radius:50%;'
            'border:1px solid #C9A55A;box-sizing:border-box"></div></div>'
            f'<div style="position:absolute;left:{cx - 5}px;top:{base - r * .55 - 5}px;width:10px;height:10px;transform:rotate(45deg);'
            'background:linear-gradient(135deg,#F1DC9C,#8B6A2C)"></div>')


EVT = 30     # the card's top edge in the top piece (the crest rises above it)
EV_TOP = (ev_crest(290.5, EVT, 28)
          + f'<div class="lac" style="position:absolute;left:0;right:0;top:{EVT}px;bottom:0;'
            f'clip-path:polygon(10px 0,calc(100% - 10px) 0,100% 10px,100% 100%,0 100%,0 10px)"></div>'
          + f'<svg width="581" height="121" style="position:absolute;left:0;top:0"><path d="M.5,121V{EVT + 10}L10.5,{EVT + .5}'
            f'H{290.5 - 30}M{290.5 + 30},{EVT + .5}H570.5L580.5,{EVT + 10}V121" fill="none" stroke="url(#evg)" stroke-width="1"/>'
            '<defs><linearGradient id="evg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F1DC9C"/>'
            '<stop offset="1" stop-color="#C9A55A"/></linearGradient></defs>'
            f'<path d="M4.5,121V{EVT + 12}L12.5,{EVT + 4.5}H568.5L576.5,{EVT + 12}V121" fill="none" stroke="rgba(201,165,90,.35)"/></svg>'
          # the title's band (the title is centred at y 70-102): a gilt hairline above and below, fading at the ends
          + '<div class="frame" style="left:46px;right:46px;top:63px;height:1px;'
            'background:linear-gradient(90deg,transparent,#C9A55A 18%,#C9A55A 82%,transparent)"></div>'
          + '<div class="frame" style="left:46px;right:46px;top:107px;height:1px;'
            'background:linear-gradient(90deg,transparent,rgba(201,165,90,.6) 18%,rgba(201,165,90,.6) 82%,transparent)"></div>'
          + f'<i class="ck tr" style="top:{EVT + 6}px;right:8px"></i>')
add("ev_top", EV + "event_report_top_win.dds", 581, 121, EV_TOP)
add("ev_mid", EV + "event_report_tileable_midsection.dds", 580, 66,
    '<div class="lac" style="position:absolute;inset:0"></div>' + RAIL.format(t=0, b=0, t2=0, b2=0))
EV_BOTTOM = ('<div class="lac" style="position:absolute;left:0;right:0;top:0;bottom:6px;'
             'clip-path:polygon(0 0,100% 0,100% calc(100% - 10px),calc(100% - 10px) 100%,10px 100%,0 calc(100% - 10px))"></div>'
             '<svg width="581" height="206" style="position:absolute;left:0;top:0">'
             '<path d="M.5,0V189.5L10.5,199.5H570.5L580.5,189.5V0" fill="none" stroke="#C9A55A"/>'
             '<path d="M4.5,0V187.5L12.5,195.5H568.5L576.5,187.5V0" fill="none" stroke="rgba(201,165,90,.35)"/>'
             # the picture (210 x 176 at 5, 5): a gilt frame round it, small fans at its corners
             '<rect x="3.5" y="3.5" width="213" height="179" fill="none" stroke="#C9A55A"/>'
             '<rect x="1.5" y="1.5" width="217" height="183" fill="none" stroke="rgba(201,165,90,.3)"/></svg>'
             '<i class="ck sm bl" style="left:8px;bottom:13px"></i><i class="ck sm br" style="right:8px;bottom:13px"></i>')
add("ev_bottom", EV + "event_report_bottom_win.dds", 581, 206, EV_BOTTOM)
# an option: a chamfered lacquer plate with a gilt rim (352 wide, under a 300 px entry: it overhangs to the right)
add("ev_option", EV + "event_option_entry.dds", 352, 48,
    f'<div style="position:absolute;left:0;top:2px;width:352px;height:44px">{bar("linear-gradient(180deg,#1E2A31,#0E1519)", GOLD, 9, .25)}</div>'
    '<div class="frame" style="left:16px;right:16px;top:41px;height:1px;background:rgba(201,165,90,.25)"></div>')
add("ev_clip", EV + "event_pic_clip.dds", 55, 30, "")        # the paper clip: none on lacquer
add("ev_minimize", EV + "event_button_minimize.dds", 32, 33,
    '<div style="position:absolute;left:5px;top:5.5px;width:22px;height:22px;transform:rotate(45deg);border:1px solid #E3C77E;'
    'background:#0B1014;box-sizing:border-box"></div>'
    '<svg width="32" height="33" viewBox="0 0 32 33" style="position:absolute;left:0;top:0"><path d="M18,12.5L13.5,16.5L18,20.5" '
    'fill="none" stroke="#E3C77E" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>')
# the news: a broadsheet in lacquer and gilt; the picture at (59, 91), 399 x 155; the headline at y 260-292
NEWS_TITLE = ('<span style="background:linear-gradient(180deg,#FFF3C8,#E3C77E 45%,#9C7836);-webkit-background-clip:text;'
              'color:transparent">{}</span>')
EV_NEWS = ('<div class="lac" style="position:absolute;inset:0;clip-path:polygon(14px 0,calc(100% - 14px) 0,100% 14px,100% calc(100% - 14px),'
           'calc(100% - 14px) 100%,14px 100%,0 calc(100% - 14px),0 14px)"></div>'
           '<svg width="528" height="595" style="position:absolute;left:0;top:0">'
           '<path d="M14.5,.5H513.5L527.5,14.5V580.5L513.5,594.5H14.5L.5,580.5V14.5Z" fill="none" stroke="#C9A55A"/>'
           '<path d="M16.5,6.5H511.5L521.5,16.5V578.5L511.5,588.5H16.5L6.5,578.5V16.5Z" fill="none" stroke="rgba(201,165,90,.4)"/>'
           '<path d="M40,22.5H488M40,25.5H488M40,79.5H488M40,82.5H488" stroke="#C9A55A" stroke-width="1"/>'
           '<rect x="57.5" y="89.5" width="402" height="158" fill="none" stroke="#C9A55A"/>'
           '<path d="M60,298.5H468" stroke="rgba(201,165,90,.55)"/>'
           '<path d="M170,492.5H358" stroke="rgba(201,165,90,.55)"/></svg>'
           '<div style="position:absolute;left:259px;top:487.5px;width:10px;height:10px;transform:rotate(45deg);background:#C9A55A"></div>'
           '<div style="position:absolute;left:0;right:0;top:29px;height:46px;display:flex;align-items:center;justify-content:center;'
           "gap:26px;font:400 40px/1 Federo;letter-spacing:.16em\">" + NEWS_TITLE.format("WORLD")
           + '<span style="position:relative;width:44px;height:44px;border-radius:50%;background:repeating-conic-gradient('
             'rgba(227,199,126,.7) 0deg 3deg,transparent 3deg 15deg),#11191E;box-shadow:0 0 0 1px #C9A55A"></span>'
           + NEWS_TITLE.format("NEWS") + '</div>')
add("ev_news", EV + "event_news_bg.dds", 528, 595, EV_NEWS)
add("ev_news_overlay", EV + "event_news_pic_overlay.dds", 399, 155,
    '<div style="position:absolute;inset:0;box-shadow:inset 0 0 22px rgba(11,16,20,.55),inset 0 0 0 1px rgba(241,220,156,.35)"></div>')
# a leader event's portrait frame (172 x 232; the portrait at its (8, 9), 156 x 210): an arch, as the army cards
LF_HOLE = _arch(10, 162, 11, 52, 218)
LF_BODY = _cham(2, 2, 170, 230, 7)
add("ev_leader_frame", EV + "event_leader_frame.dds", 172, 232,
    f'<svg width="172" height="232" style="position:absolute;left:0;top:0"><defs>{LG_GOLD}</defs>'
    f'<path d="{LF_BODY}{LF_HOLE}" fill="url(#pin)" fill-rule="evenodd"/>'
    f'<path d="{LF_BODY}" fill="none" stroke="url(#g)" stroke-width="1.4"/>'
    f'<path d="{_cham(5, 5, 167, 227, 5)}" fill="none" stroke="rgba(201,165,90,.4)"/>'
    f'<path d="{LF_HOLE}" fill="none" stroke="url(#g)" stroke-width="1.6"/></svg>')

# ---------------------------------------------------------------- render
G = FONTS_SRC
FONTS = f"""@font-face{{font-family:'Limelight';src:url('file://{G}limelight/Limelight-Regular.ttf')}}
@font-face{{font-family:'Federo';src:url('file://{G}federo/Federo-Regular.ttf')}}
@font-face{{font-family:'Bodoni Moda';font-style:italic;src:url('file://{G}bodonimoda/BodoniModa-Italic[opsz,wght].ttf')}}
@font-face{{font-family:'Josefin Sans';src:url('file://{G}josefinsans/JosefinSans[wght].ttf');font-weight:100 700}}"""
# python gen_textures.py lg_ ev_   renders only the textures whose key starts with one of those prefixes (the others
# keep their files and manifest entries: re-rendering everything changes a few anti-aliased pixels everywhere)
ONLY = [a for a in sys.argv[1:] if not a.startswith("-")]
if ONLY:
    SPRITES = [s for s in SPRITES if s[0].startswith(tuple(ONLY))]
    assert SPRITES, f"no texture key starts with {ONLY}"
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
if ONLY and os.path.isfile(BUILD + "texture_manifest.json"):
    done = {m["key"] for m in manifest}
    manifest = [m for m in json.load(open(BUILD + "texture_manifest.json")) if m["key"] not in done] + manifest
json.dump(manifest, open(BUILD + "texture_manifest.json", "w"), indent=1)
print(len(manifest), "textures written")
