"""The pieces every mockup in this folder is drawn from: the Deco UI's palette, fonts and shapes as HTML (the same
recipes as tools/gen_textures.py, tools/art_util.py and the mockup boards in art/mockups/source/), the backdrop (the
map, its names, the Deco UI's top bar), and the renderer (headless Chromium through Playwright).

Nothing here is the game's art: the map and the mockup boards are the project's own, the flags and portraits the
author's (source/flags, source/portraits), the icons the Deco UI's line set (tools/icons.py).
"""
import base64
import functools
import html as _html
import io
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
DECO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
REPO = os.path.abspath(os.path.join(DECO, ".."))
FONTS = os.path.join(DECO, "source_fonts")
OUT = HERE
PRIVATE = os.path.join(DECO, "build", "next_screens")    # pictures holding the game's art: git-ignored
CHROMIUM = os.environ.get("CHROMIUM_PATH", "/opt/pw-browsers/chromium")
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(DECO, "tools"))
from icons import ICONS, icon as _icon  # noqa: E402  (read only: the Deco UI's line icons)

W, H = 1920, 1080

# ---------------------------------------------------------------- palette (deco_ui/CLAUDE.md section 5)
LAC = "#11191E"
LAC2 = "#17222A"
DARK = "#0B1014"
GILT = "#E3C77E"
RULE = "#C9A55A"
HI = "#F1DC9C"
JADE = "#2E6E60"
AMBER = "#E7B75A"
CORAL = "rgb(238,140,126)"
CREAM = "#F4ECD9"
CREAM2 = "#E8DFC8"
LABEL = "#B7A680"
POS = "#93D6A5"
NEG = "#EE8C7E"
OX = dict(deep="#4A1E19", mid="#7E3228", lit="#A9493A", pale="#E7A493", line="rgba(196,96,80,.85)")   # attacker
SL = dict(deep="#16293A", mid="#2C4F6B", lit="#40698B", pale="#A9C7DE", line="rgba(104,150,190,.85)")  # defender
INK = "#2B2114"            # dark ink on the ivory sheet
IVORY = "#EAE0C4"
STRIPES = "repeating-linear-gradient(90deg,rgba(255,255,255,.025) 0 1px,transparent 1px 7px)"
GOLD = "linear-gradient(180deg,#E8CD84,#8B6A2C)"
BAR_FILL = "linear-gradient(180deg,#1A252C,#0E1519)"
LIT_FILL = "linear-gradient(180deg,#2C665A,#163A33)"
DIM_FILL = "linear-gradient(180deg,#141D22,#0B1014)"

CSS = f"""
@font-face{{font-family:'Federo';src:url('file://{FONTS}/federo/Federo-Regular.ttf')}}
@font-face{{font-family:'Josefin Sans';src:url('file://{FONTS}/josefinsans/JosefinSans[wght].ttf');font-weight:100 700}}
@font-face{{font-family:'Bodoni Moda';font-style:italic;src:url('file://{FONTS}/bodonimoda/BodoniModa-Italic[opsz,wght].ttf');font-weight:400 900}}
@font-face{{font-family:'Limelight';src:url('file://{FONTS}/limelight/Limelight-Regular.ttf')}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:{W}px;height:{H}px;overflow:hidden;background:{DARK};font-family:'Josefin Sans',sans-serif;color:{CREAM}}}
.a{{position:absolute}}
.t{{position:absolute;white-space:nowrap;line-height:1}}
.fed{{font-family:'Federo',serif;font-weight:400}}
.bod{{font-family:'Bodoni Moda',serif;font-style:italic}}
.gilt{{background:linear-gradient(180deg,#F8EBBD 0%,#E4C67E 46%,#B08B41 58%,#E9D190 100%);-webkit-background-clip:text;background-clip:text;color:transparent}}
.cap{{text-transform:uppercase}}
.ck{{position:absolute;width:16px;height:16px;pointer-events:none}}
.ck:before{{content:"";position:absolute;inset:0;border-top:2px solid {GILT};border-left:2px solid {GILT}}}
.ck:after{{content:"";position:absolute;left:6px;top:6px;width:6px;height:6px;border-top:2px solid {GILT};border-left:2px solid {GILT}}}
.ck.sm{{width:10px;height:10px}}.ck.sm:after{{left:4px;top:4px;width:3px;height:3px;border-width:1.5px}}.ck.sm:before{{border-width:1.5px}}
.tl{{left:2px;top:2px}}.tr{{right:2px;top:2px;transform:scaleX(-1)}}.bl{{left:2px;bottom:2px;transform:scaleY(-1)}}.br{{right:2px;bottom:2px;transform:scale(-1,-1)}}
.ml{{position:absolute;white-space:nowrap;font-family:'Federo',serif;text-transform:uppercase;color:rgba(246,238,216,.5);text-shadow:0 1px 0 rgba(0,0,0,.35)}}
.vp{{position:absolute;width:7px;height:7px;background:#E8CD84;transform:translate(-50%,-50%) rotate(45deg);box-shadow:0 0 0 1.5px #16110a}}
.vn{{position:absolute;font:600 11.5px/1 'Josefin Sans',sans-serif;letter-spacing:.05em;color:#F6EEDC;text-shadow:0 1px 2px #000,0 0 4px rgba(0,0,0,.9);white-space:nowrap}}
svg{{display:block;overflow:visible}}
"""


def esc(s):
    return _html.escape(str(s), quote=False)


# ---------------------------------------------------------------- images
@functools.lru_cache(maxsize=None)
def _uri(path, w=None, h=None, mode="fit", nearest=False):
    im = Image.open(path).convert("RGBA")
    if w and h:
        if mode == "cover":
            s = max(w / im.width, h / im.height)
            nw, nh = max(1, round(im.width * s)), max(1, round(im.height * s))
            im = im.resize((nw, nh), Image.NEAREST if nearest else Image.LANCZOS)
            l, t = (nw - w) // 2, max(0, (nh - h) // 4)
            im = im.crop((l, t, l + w, t + h))
        else:
            im = im.resize((w, h), Image.NEAREST if nearest else Image.LANCZOS)
    b = io.BytesIO()
    im.save(b, "PNG")
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()


def img(path, x, y, w, h, mode="fit", style="", nearest=False):
    return (f'<img src="{_uri(path, int(w), int(h), mode, nearest)}" class="a" '
            f'style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;{style}">')


def uri_of(im):
    b = io.BytesIO()
    im.save(b, "PNG")
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()


@functools.lru_cache(maxsize=None)
def map_colours():
    """tag -> map colour, read from the Valsora build's settings (scripts/common.py, COUNTRIES), as text"""
    import re
    t = open(os.path.join(REPO, "scripts", "common.py"), encoding="utf-8").read()
    return {m.group(1): tuple(int(v) for v in m.group(2).split(","))
            for m in re.finditer(r'\(\s*"([A-Z]{3})"\s*,\s*"[^"]*"\s*,\s*"[^"]*"\s*,\s*\(([0-9 ,]+)\)', t)}


def flag(tag, x, y, w=82, h=52, frame=True, style=""):
    """the author's flag, scaled once to the game's size for that slot (82 x 52, 41 x 26, 26 x 21 ...); a nation without
    one flies the build's stripe in its map colour"""
    p = os.path.join(REPO, "source", "flags", f"{tag}.png")
    if not os.path.isfile(p):
        r, g, b = map_colours().get(tag, (90, 96, 104))
        out = box(x, y, w, h, f"background:linear-gradient(180deg,rgb({r},{g},{b}) 0 33%,rgb({min(255, r + 60)},{min(255, g + 60)},{min(255, b + 60)}) 33% 66%,rgb({r},{g},{b}) 66%);{style}")
        if frame:
            out += box(x - 1, y - 1, w + 2, h + 2, f"box-shadow:0 0 0 1px {RULE},0 0 0 2px rgba(0,0,0,.6)")
        return out
    out = img(p, x, y, w, h, "cover", style)
    if frame:
        out += box(x - 1, y - 1, w + 2, h + 2, f"box-shadow:0 0 0 1px {RULE},0 0 0 2px rgba(0,0,0,.6)")
    return out


def portrait(name, x, y, w, h, style=""):
    for ext in (".png", ".jpg", ".webp"):
        p = os.path.join(REPO, "source", "portraits", name + ext)
        if os.path.isfile(p):
            return img(p, x, y, w, h, "cover", style)
    return silhouette(x, y, w, h)


def silhouette(x, y, w, h):
    """a stand-in portrait (the game's generic portraits are its art): a gilt bust on lacquer"""
    return (box(x, y, w, h, f"background:radial-gradient(circle at 50% 35%,#1E2B33,#0B1014 75%)")
            + f'<svg class="a" style="left:{x}px;top:{y}px" width="{w}" height="{h}" viewBox="0 0 100 130">'
              '<circle cx="50" cy="48" r="20" fill="none" stroke="rgba(227,199,126,.55)" stroke-width="2"/>'
              '<path d="M14 130c3-30 17-44 36-44s33 14 36 44" fill="none" stroke="rgba(227,199,126,.55)" stroke-width="2"/></svg>')


# ---------------------------------------------------------------- boxes and text
def box(x, y, w, h, style="", inner=""):
    return f'<div class="a" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;{style}">{inner}</div>'


def text(x, y, s, size=14, color=CREAM, w=None, align="left", font="sans", weight=500, track=0, caps=False,
         style="", h=None, valign=False, gilt=False, lh=None):
    fam = {"sans": "'Josefin Sans',sans-serif", "fed": "'Federo',serif", "bod": "'Bodoni Moda',serif"}[font]
    ital = "italic " if font == "bod" else ""
    css = (f"left:{x}px;top:{y}px;font:{ital}{weight} {size}px/{lh or 1} {fam};color:{color};letter-spacing:{track}em;"
           f"text-align:{align};")
    if w is not None:
        css += f"width:{w}px;"
        if lh:
            css += "white-space:normal;"
    if h is not None:
        css += f"height:{h}px;"
    if valign and h is not None:
        css += f"display:flex;align-items:center;justify-content:{dict(left='flex-start', center='center', right='flex-end')[align]};"
    if caps:
        css += "text-transform:uppercase;"
    cls = "t gilt" if gilt else "t"
    if gilt:
        css += "color:transparent;"
    return f'<div class="{cls}" style="{css}{style}">{esc(s) if not str(s).startswith("<") else s}</div>'


def title(x, y, s, size=24, w=None, align="left", track=.18, style=""):
    """gilt capitals in the display face: window titles"""
    return text(x, y, s, size, w=w, align=align, font="fed", weight=400, track=track, caps=True, gilt=True, style=style)


def label(x, y, s, size=10, color=LABEL, w=None, align="left", track=.17, weight=600, style=""):
    """small tracked capitals: labels"""
    return text(x, y, s, size, color, w, align, "sans", weight, track, True, style)


def value(x, y, s, size=16, color=CREAM, w=None, align="left", weight=700, style=""):
    return text(x, y, s, size, color, w, align, "sans", weight, 0, False, style)


def ico(name, x, y, size=24, color=GILT, sw=1.5):
    return f'<div class="a" style="left:{x}px;top:{y}px">{_icon(name, size, color, sw)}</div>'


def svg(x, y, w, h, inner, vb=None, style=""):
    vb = vb or f"0 0 {w} {h}"
    return (f'<svg class="a" style="left:{x}px;top:{y}px;{style}" width="{w}" height="{h}" viewBox="{vb}" fill="none" '
            f'stroke-linecap="round" stroke-linejoin="round">{inner}</svg>')


def chamfer(c):
    return (f"polygon({c}px 0,calc(100% - {c}px) 0,100% {c}px,100% calc(100% - {c}px),calc(100% - {c}px) 100%,"
            f"{c}px 100%,0 calc(100% - {c}px),0 {c}px)")


def poly(pts):
    return "polygon(" + ",".join(f"{px}px {py}px" for px, py in pts) + ")"


def octagon_pts(cx, cy, r, c=None):
    c = c if c is not None else r * 0.42
    return [(cx - r + c, cy - r), (cx + r - c, cy - r), (cx + r, cy - r + c), (cx + r, cy + r - c),
            (cx + r - c, cy + r), (cx - r + c, cy + r), (cx - r, cy + r - c), (cx - r, cy - r + c)]


def layer(pts, background, x=0, y=0, w=W, h=H):
    return box(x, y, w, h, f"background:{background};clip-path:{poly([(px - x, py - y) for px, py in pts])}")


def rule(x0, y, x1, color="rgba(201,165,90,.85)", t=1):
    return box(x0, y, x1 - x0, t, f"background:{color}")


def vrule(x, y0, y1, color="rgba(201,165,90,.55)", t=1):
    return box(x, y0, t, y1 - y0, f"background:{color}")


def fade_rule(x0, y, x1, color="201,165,90", a=.85):
    return box(x0, y, x1 - x0, 1, f"background:linear-gradient(90deg,rgba({color},0),rgba({color},{a}) 20%,rgba({color},{a}) 80%,rgba({color},0))")


def diamond(cx, cy, s=6, color=RULE, style=""):
    return box(cx - s / 2, cy - s / 2, s, s, f"background:{color};transform:rotate(45deg);{style}")


def corners(x, y, w, h, small=False):
    c = "ck sm" if small else "ck"
    return (f'<div class="a" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">'
            f'<i class="{c} tl"></i><i class="{c} tr"></i><i class="{c} bl"></i><i class="{c} br"></i></div>')


# ---------------------------------------------------------------- the core skin's pieces
def window(x, y, w, h, rule_="double", corner="big", raised=False, shadow=True, alpha=.97):
    fill = LAC2 if raised else LAC
    out = box(x, y, w, h, f"background:{STRIPES},linear-gradient(180deg,#141E24,#0D1418);opacity:{alpha};"
                          + ("box-shadow:0 16px 36px rgba(0,0,0,.55);" if shadow else ""))
    if raised:
        out = box(x, y, w, h, f"background:{STRIPES},linear-gradient(180deg,#1A262E,{fill});opacity:{alpha};"
                              + ("box-shadow:0 16px 36px rgba(0,0,0,.55);" if shadow else ""))
    out += box(x, y, w, h, "box-shadow:inset 0 0 0 1px rgba(0,0,0,.7)")
    if rule_ == "double":
        out += box(x + 1, y + 1, w - 2, h - 2, "border:1px solid #B8954F") + box(x + 5, y + 5, w - 10, h - 10, "border:1px solid rgba(201,165,90,.42)")
    elif rule_ == "single":
        out += box(x + 1, y + 1, w - 2, h - 2, "border:1px solid #B8954F")
    else:
        out += box(x + 1, y + 1, w - 2, h - 2, "border:1px solid rgba(184,149,79,.6)")
    if corner:
        out += corners(x, y, w, h, corner == "small")
    return out


def band(x, y, w, h, fill="linear-gradient(180deg,#1C2830,#131C22)"):
    """a raised lacquer plate: a gilt hairline on top, a shadow under it"""
    return (box(x, y, w, h, f"background:{STRIPES},{fill}") + box(x, y, w, 1, "background:rgba(227,199,126,.38)")
            + box(x, y + h - 1, w, 1, "background:rgba(0,0,0,.65)"))


def well(x, y, w, h, fill="linear-gradient(180deg,#0B1115,#080C0F)", rim="rgba(201,165,90,.55)", c=0):
    """a recessed lacquer panel"""
    cp = f"clip-path:{chamfer(c)};" if c else ""
    cp2 = f"clip-path:{chamfer(max(0.5, c - .4))};" if c else ""
    return (box(x, y, w, h, f"background:{rim};{cp}") + box(x + 1, y + 1, w - 2, h - 2, f"background:{STRIPES},{fill};{cp2}")
            + box(x + 1, y + 1, w - 2, min(14, h - 2), f"background:linear-gradient(180deg,rgba(0,0,0,.35),rgba(0,0,0,0));{cp2}"))


def bar(x, y, w, h, fill=BAR_FILL, rim="rgba(201,165,90,.6)", c=5, shine=.22, inner=""):
    """a chamfered lacquer bar with a gilt hairline: header strips, list headers, tabs"""
    return box(x, y, w, h, "", f'<div class="a" style="inset:0;background:{rim};clip-path:{chamfer(c)}"></div>'
               f'<div class="a" style="inset:1px;clip-path:{chamfer(max(1, c - .4))};background:{STRIPES},{fill}"></div>'
               f'<div class="a" style="left:{c + 3}px;right:{c + 3}px;top:2px;height:1px;background:rgba(241,220,156,{shine})"></div>{inner}')


def lit_bar(x, y, w, h, c=5, inner=""):
    return bar(x, y, w, h, LIT_FILL, GOLD, c, .35, inner)


def button(x, y, w, h, s="", kind="lacquer", size=13, caps=True, disabled=False, icon=None):
    """the core skin's standard button (gilt rim, lacquer), a gold one for the main action, jade when lit"""
    c = max(4, min(8, h // 4))
    if kind == "gold":
        rim, fill, col = "linear-gradient(180deg,#F8EBBD,#B08B41)", "linear-gradient(180deg,#E9D190 0%,#C9A55A 50%,#9C7A36 100%)", "#1B140A"
    elif kind == "lit":
        rim, fill, col = GOLD, "linear-gradient(180deg,#2C665A,#163A33)", "#FBEAB4"
    else:
        rim, fill, col = GOLD, "linear-gradient(180deg,#24323A 0%,#141D22 55%,#0E1519 100%)", GILT
    if disabled:
        rim, col = "rgba(201,165,90,.35)", "rgba(227,199,126,.4)"
    inner = (f'<div class="a" style="inset:0;background:{rim};clip-path:{chamfer(c)}"></div>'
             f'<div class="a" style="inset:1px;clip-path:{chamfer(c - .4)};background:{STRIPES},{fill}"></div>'
             f'<div class="a" style="left:{c + 2}px;right:{c + 2}px;top:2px;height:1px;background:rgba(241,220,156,.35)"></div>')
    if icon:
        isz = min(h - 8, 20)
        inner += f'<div class="a" style="left:{(w - isz) / 2}px;top:{(h - isz) / 2}px">{_icon(icon, isz, col, 1.5)}</div>'
    if s:
        tr = .14 if caps else .02
        inner += (f'<div class="a" style="inset:0;display:flex;align-items:center;justify-content:center;padding-top:{1 if caps else 2}px;'
                  f'font:600 {size}px/1 \'Josefin Sans\';letter-spacing:{tr}em;{"text-transform:uppercase;" if caps else ""}color:{col}">{esc(s)}</div>')
    return box(x, y, w, h, "", inner)


def close(x, y, s=32):
    """the close diamond (the core skin's closebutton, 32 x 33)"""
    d = s * 22 / 32
    return box(x, y, s, s, "", f'<div class="a" style="left:{(s - d) / 2}px;top:{(s - d) / 2}px;width:{d}px;height:{d}px;transform:rotate(45deg);'
               f'border:1px solid {GILT};background:{DARK}"></div>'
               + f'<svg class="a" style="left:0;top:0" width="{s}" height="{s}" viewBox="0 0 32 32"><path d="M11.5 11.5l9 9M20.5 11.5l-9 9" '
                 f'stroke="{GILT}" stroke-width="1.6"/></svg>')


def tab(x, y, w, h, s, lit=False, size=13):
    b = lit_bar(x, y, w, h, 7) if lit else bar(x, y, w, h, DIM_FILL, "rgba(201,165,90,.4)", 7, .1)
    col = "#FBEAB4" if lit else LABEL
    return b + text(x, y + 1, s, size, col, w, "center", "sans", 600, .14, True, h=h, valign=True)


def checkbox(x, y, on=False, s=20):
    out = box(x, y, s, s, f"background:{'#163A33' if on else '#0A0F12'};box-shadow:inset 0 0 0 1px {GILT if on else RULE}")
    if on:
        out += svg(x, y, s, s, f'<path d="M{s * .2} {s * .52}l{s * .2} {s * .2} {s * .4} {-s * .45}" stroke="{HI}" stroke-width="2"/>')
    return out


def progress(x, y, w, h, frac, fill="linear-gradient(180deg,#F1DC9C,#B48F44)", track="#0A0F12", rim="rgba(201,165,90,.55)"):
    return (box(x, y, w, h, f"background:{track};box-shadow:0 0 0 1px {rim}")
            + box(x, y, max(0, w * frac), h, f"background:{fill}"))


def medallion(cx, cy, r, glyph=None, inner_line="rgba(201,165,90,.45)", fill="radial-gradient(circle at 50% 35%,#1A262E,#0B1014 75%)",
              icon_size=None, icon_color=GILT, lit=False):
    """an octagonal lacquer medallion with a gilt rim (the land battle's, the map modes')"""
    if lit:
        fill = "radial-gradient(circle at 50% 35%,#2C665A,#123029 80%)"
    out = (layer(octagon_pts(cx, cy, r), GOLD) + layer(octagon_pts(cx, cy, r - 1.4), f"{STRIPES},linear-gradient(180deg,#18232B,#0B1014)")
           + layer(octagon_pts(cx, cy, r - 4), inner_line) + layer(octagon_pts(cx, cy, r - 5), fill))
    if glyph:
        s = icon_size or int(r * 1.1)
        out += f'<div class="a" style="left:{cx - s / 2}px;top:{cy - s / 2}px">{_icon(glyph, s, icon_color, 1.5)}</div>'
    return out


def sunburst(cx, cy, r, alpha=.22):
    return box(cx - r, cy - r, 2 * r, 2 * r, f"border-radius:50%;background:repeating-conic-gradient(rgba(227,199,126,{alpha}) 0deg 3deg,transparent 3deg 11deg);"
                                             "-webkit-mask:radial-gradient(circle,#000 32%,transparent 70%)")


def speed_lines(x0, x1, y, to_right=True, rows=((-4, 1), (0, 1), (4, 1)), col="201,165,90"):
    out = ""
    for dy, t in rows:
        a, b = (f"rgba({col},.9)", f"rgba({col},0)") if to_right else (f"rgba({col},0)", f"rgba({col},.9)")
        out += box(x0, y + dy, x1 - x0, t, f"background:linear-gradient(90deg,{a},{b})")
    return out


def ivory(x, y, w, h, rows=0, row_h=20, top=0, rim="#9C7A36", cols=()):
    """the designers' ivory sheet, ruled in sepia (the game writes dark text on it)"""
    out = box(x, y, w, h, f"background:{rim}") + box(x + 1, y + 1, w - 2, h - 2,
                                                     "background:linear-gradient(180deg,#EFE6CC,#E4D8B8);box-shadow:inset 0 0 18px rgba(120,90,40,.18)")
    out += box(x + 4, y + 4, w - 8, h - 8, "border:1px solid rgba(156,122,54,.45)")
    for i in range(rows):
        yy = y + top + (i + 1) * row_h
        if yy < y + h - 4:
            out += box(x + 8, yy, w - 16, 1, "background:rgba(156,122,54,.28)")
    for cx in cols:
        out += box(cx, y + 6, 1, h - 12, "background:rgba(156,122,54,.35)")
    return out


def header(x, y, w, h=40, s="", size=22, close_at=None, align="center", sub=None):
    """a window's header band: lacquer, a gilt rule under it, the title in gilt capitals, diamonds at its ends"""
    out = band(x, y, w, h) + rule(x, y + h, x + w, "rgba(201,165,90,.85)")
    if s:
        tw = w - 120
        out += title(x + 60, y + (h - size) / 2 + 2, s, size, w=tw, align=align)
        if align == "center":
            out += diamond(x + 34, y + h / 2, 6) + diamond(x + w - 34 - (40 if close_at else 0), y + h / 2, 6)
    if sub:
        out += label(x + 60, y + h - 12, sub, 9, w=w - 120, align=align)
    return out


def unit_glyph(kind, size=26, color="#EBD397", sw=1.3):
    """the Main board's unit glyphs (26 x 14): motorised (truck), armour (tank), mechanised (IFV), infantry (helmet)"""
    g = {
        "motorized": '<path d="M2 3.5h13v7H2zM15 6h5l3.5 3v1.5H15z"/><circle cx="6" cy="11.5" r="1.8"/><circle cx="19" cy="11.5" r="1.8"/>',
        "armor": '<path d="M8 2.5h7.5l1.5 3H7z"/><path d="M16 4h8.5"/><path d="M2 6.5h21l-1.5 4.5H3.5z"/><path d="M5 11h16"/>',
        "mechanized": '<path d="M2.5 4h14l5 3.5v3H2.5z"/><path d="M6 4V2h6v2"/><circle cx="6.5" cy="11.5" r="1.6"/><path d="M13 12h7"/>',
        "infantry": '<path d="M6 11.5C6 6.5 8.8 3 13 3s7 3.5 7 8.5h-3.2c-.4-1.8-1.3-2.7-2.8-2.7h-1.8c-1.4 0-2.2.8-2.6 1.8z"/><path d="M8.6 7.6h9.6"/>',
        "levy": '<path d="M8 13V1.2"/><path d="M8 1.8h11l-3 2.9 3 2.9H8"/><path d="M4.5 13h7"/>',
        "hq": '<path d="M13 1.8l1.5 3 3.3.4-2.4 2.3.6 3.3-3-1.6-3 1.6.6-3.3-2.4-2.3 3.3-.4z"/>',
        "ship": '<path d="M2 8.5h22l-2.5 4H4.5z"/><path d="M6 8.5V6h5V3.5h3V6h4v2.5"/><path d="M12.5 3.5V1.5"/>',
        "sub": '<path d="M2.5 9c0-2 3-3 10.5-3s10.5 1 10.5 3-3 3-10.5 3S2.5 11 2.5 9z"/><path d="M11 6V3.5h4V6M13 3.5V1.8"/>',
        "carrier": '<path d="M1.5 7h23l-2.5 5H4z"/><path d="M15 7V4h3.5v3"/><path d="M4 7l3-2h6"/>',
        "jet": '<path d="M13 1l1 3v3l9 4v1.5l-9-1.5v2.5l3 1.5v1h-8v-1l3-1.5V11L3 12.5V11l9-4V4z" transform="scale(1 .82) translate(0 1)"/>',
    }[kind]
    return (f'<svg width="{size}" height="{size * 14 / 26}" viewBox="0 0 26 14" fill="none" stroke="{color}" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round">{g}</svg>')


def carrier_art(x, y, w=147, h=69, color=GILT):
    """a modern aircraft carrier in side view, in gilt line (the class picture's stand-in)"""
    return svg(x, y, w, h, f'''<g stroke="{color}" stroke-width="1.3">
<path d="M4 40h138l-6 6H110l-4 9H22l-6-9H9z"/><path d="M20 55c20 2 60 2 86 0"/>
<path d="M2 38h143"/><path d="M90 38V24h16l3 6v8"/><path d="M93 24v-7h9v7M97 17v-6M94 11h7"/><path d="M95 29h8"/>
<path d="M28 34l6-3h5l1 3M54 34l6-3h5l1 3M118 34l6-3h5l1 3" stroke-width="1.1"/>
<path d="M12 49h4M24 49h4M36 49h4M48 49h4M60 49h4M72 49h4M84 49h4" stroke-width="1" opacity=".7"/>
<path d="M0 62c8-2 14 2 22 0s14-2 22 0 14 2 22 0 14-2 22 0 14 2 22 0 14-2 22 0 8 1 15 0" stroke-width=".9" opacity=".55"/></g>''', f"0 0 {w} {h}")


def chevrons(x, y, n=3, s=10, color=GILT):
    out = ""
    for i in range(n):
        out += svg(x, y + i * s * .45, s, s * .6, f'<path d="M1 {s * .55}L{s / 2} 1L{s - 1} {s * .55}" stroke="{color}" stroke-width="1.6"/>')
    return out


def skill_diamond(cx, cy, n, s=26):
    """the commanders' skill: a dark diamond in a gilt rim (designer_art.skill_diamond's look)"""
    return (box(cx - s / 2, cy - s / 2, s, s, f"transform:rotate(45deg);background:{GOLD}")
            + box(cx - s / 2 + 1.5, cy - s / 2 + 1.5, s - 3, s - 3, "transform:rotate(45deg);background:radial-gradient(circle,#1C2830,#0B1014)")
            + text(cx - 15, cy - 8, n, 16, CREAM, 30, "center", weight=700))


def stat_pip(x, y, n, total=5, w=14, h=6):
    out = ""
    for i in range(total):
        on = i < n
        out += box(x + i * (w + 3), y, w, h, f"transform:skewX(-20deg);background:{'linear-gradient(180deg,#F1DC9C,#B48F44)' if on else '#2A363D'}")
    return out


def tooltip(x, y, w, h, s_title, rows=(), body=None):
    """the core skin's tooltip: lacquer, gilt rule, a gilt top line, small corner brackets"""
    out = (box(x, y, w, h, f"background:#0E1519;opacity:.97;box-shadow:0 10px 24px rgba(0,0,0,.55)")
           + box(x, y, w, h, "border:1px solid #B8954F") + box(x + 1, y + 1, w - 2, 2, "background:linear-gradient(90deg,#8B6A2C,#F1DC9C,#8B6A2C)")
           + corners(x, y, w, h, True))
    out += title(x + 14, y + 14, s_title, 15, track=.14)
    yy = y + 38
    for k, v, col in rows:
        out += text(x + 14, yy, k, 13, CREAM2, w - 100) + text(x + w - 94, yy, v, 13, col, 80, "right", weight=700)
        yy += 19
    if body:
        out += text(x + 14, yy + 6, body, 13, "#D9CFB6", w - 28, font="bod", weight=400, lh=1.35)
    return out


# ---------------------------------------------------------------- backdrops
MAP_LABELS = """
<div class="ml" style="left:880px;top:626px;font-size:44px;letter-spacing:.55em;transform:translate(-50%,-50%) rotate(9deg)">Rouental</div>
<div class="ml" style="left:840px;top:318px;font-size:50px;letter-spacing:.6em;transform:translate(-50%,-50%) rotate(-2deg)">Cardonia</div>
<div class="ml" style="left:1380px;top:760px;font-size:40px;letter-spacing:.45em;transform:translate(-50%,-50%) rotate(-16deg)">Fraxhemark</div>
<div class="ml" style="left:1440px;top:262px;font-size:30px;letter-spacing:.45em;transform:translate(-50%,-50%) rotate(10deg)">Kurikia</div>
<div class="ml" style="left:430px;top:596px;font-size:22px;letter-spacing:.35em;transform:translate(-50%,-50%) rotate(19deg)">Placeholdaire</div>
<div class="ml" style="left:250px;top:108px;font-size:20px;letter-spacing:.4em;transform:translate(-50%,-50%) rotate(-8deg)">Wersh</div>
<div class="ml" style="left:598px;top:846px;font-size:18px;letter-spacing:.4em;transform:translate(-50%,-50%) rotate(-26deg)">Selto</div>
<div class="ml" style="left:760px;top:1000px;font-size:18px;letter-spacing:.4em;transform:translate(-50%,-50%) rotate(-6deg)">Estande</div>
"""
VPS = [(603, 485, "Seraine"), (655, 521, "Saintiers"), (337, 448, "Carcarelle"), (332, 356, "Vair"),
       (351, 523, "Grande Reliette"), (943, 675, "Torres"), (1108, 541, "Grande Hollier"), (1134, 402, "Tanière"),
       (989, 482, "Evriches"), (1061, 537, "Argent-sur-Seigne"), (1191, 341, "Villerose"), (1177, 425, "Lanzerac"),
       (852, 703, "Guedelon")]


def vps(skip=()):
    out = ('<div class="a" style="left:563px;top:483px;width:18px;height:18px"><svg width="18" height="18" viewBox="0 0 18 18">'
           '<circle cx="9" cy="9" r="8" fill="#16110A" stroke="#E8CD84" stroke-width="1.2"/><path d="M9 3.6l1.5 3.4 3.7.3-2.8 2.4.9 3.6L9 11.4 '
           '5.7 13.3l.9-3.6L3.8 7.3l3.7-.3z" fill="#F3DE9E"/></svg></div>'
           '<div class="vn" style="left:520px;top:504px;font-size:13px;font-weight:700">Rêverie</div>')
    for x, y, n in VPS:
        if n in skip:
            continue
        dx = {"Evriches": (-49, -20), "Argent-sur-Seigne": (-93, 29), "Grande Hollier": (4, 11)}.get(n, (9, 3))
        out += f'<div class="vp" style="left:{x}px;top:{y}px"></div><div class="vn" style="left:{x + dx[0]}px;top:{y + dx[1]}px">{esc(n)}</div>'
    return out


@functools.lru_cache(maxsize=None)
def _map_uri(dim=0.0, blur=0):
    im = Image.open(os.path.join(DECO, "art", "map_rouental.jpg")).convert("RGB").resize((W, H), Image.LANCZOS)
    if dim:
        a = np.asarray(im, np.float32) * (1 - dim)
        im = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    if blur:
        from PIL import ImageFilter
        im = im.filter(ImageFilter.GaussianBlur(blur))
    b = io.BytesIO()
    im.save(b, "JPEG", quality=92)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()


@functools.lru_cache(maxsize=None)
def _topbar_uri():
    """the Deco UI's top bar as its own preview draws it (deco_ui/build/preview_topbar.png, drawn by
    tools/validate_preview.py from the mod's own textures over the same map), cut out from the map by difference"""
    p = os.path.join(DECO, "build", "preview_topbar.png")
    if not os.path.isfile(p):
        return None
    tb = np.asarray(Image.open(p).convert("RGB"), np.int16)
    mp = np.asarray(Image.open(os.path.join(DECO, "art", "map_rouental.jpg")).convert("RGB").resize((W, H), Image.LANCZOS), np.int16)[:tb.shape[0]]
    d = np.abs(tb - mp).max(-1)
    a = np.where(d > 6, 255, 0).astype(np.uint8)
    # the band and the medallion are solid: keep everything above the band's foot, and close small holes
    a[:64] = 255
    from PIL import ImageFilter
    am = Image.fromarray(a).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))
    out = Image.fromarray(tb.astype(np.uint8)).convert("RGBA")
    out.putalpha(am)
    b = io.BytesIO()
    out.save(b, "PNG")
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()


def topbar():
    u = _topbar_uri()
    return f'<img class="a" src="{u}" style="left:0;top:0">' if u else ""


def backdrop(kind="map", dim=0.0, labels=True, top=True, blur=0):
    if kind == "menu":
        p = os.path.join(DECO, "valsora_deco_ui", "gfx", "loadingscreens", "valsora_menu.dds")
        im = Image.open(p).convert("RGB")
        oy = (im.height - H * im.width // W) // 2
        im = im.resize((W, im.height * W // im.width)).crop((0, oy, W, oy + H))
        if dim:
            im = Image.fromarray((np.asarray(im, np.float32) * (1 - dim)).astype(np.uint8))
        return f'<img class="a" src="{uri_of(im)}" style="left:0;top:0;width:{W}px;height:{H}px">'
    out = f'<img class="a" src="{_map_uri(dim, blur)}" style="left:0;top:0;width:{W}px;height:{H}px">'
    if labels:
        out += MAP_LABELS + vps()
    if dim and labels:
        out += box(0, 0, W, H, f"background:rgba(0,0,0,0)")
    if top:
        out += topbar()
    return out


def note(x, y, s, w=360):
    """a mockup's note (not in game): a small paper tag, so the author can tell it from the interface"""
    return (box(x, y, w, 0, "") + f'<div class="a" style="left:{x}px;top:{y}px;width:{w}px;padding:7px 10px 6px;background:rgba(244,236,217,.93);'
            f'border-left:3px solid #9C7A36;font:500 12px/1.35 \'Josefin Sans\';color:#2B2114;box-shadow:0 4px 10px rgba(0,0,0,.4)">{s}</div>')


# ---------------------------------------------------------------- rendering
def page(body):
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{body}</body></html>'


_PW = {}


def _browser():
    if "b" not in _PW:
        from playwright.sync_api import sync_playwright
        _PW["p"] = sync_playwright().start()
        _PW["b"] = _PW["p"].chromium.launch(executable_path=CHROMIUM)
    return _PW["b"]


def render(body, out, w=W, h=H, scale=1, palette=False):
    """draw the page and save it as a PNG (optimised; palette=True quantises it, for the overview sheet)"""
    b = _browser()
    pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=scale)
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, dir=os.environ.get("NS_TMP", "/tmp/claude-0")) as f:
        f.write(page(body).replace(f"width:{W}px;height:{H}px;overflow:hidden", f"width:{w}px;height:{h}px;overflow:hidden"))
        tmp = f.name
    pg.goto("file://" + tmp)
    pg.wait_for_timeout(250)
    data = pg.screenshot(clip={"x": 0, "y": 0, "width": w, "height": h})
    pg.close()
    os.unlink(tmp)
    im = Image.open(io.BytesIO(data)).convert("RGB")
    if palette:
        im = im.quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    im.save(out, optimize=True)
    return out


def close_browser():
    if "b" in _PW:
        _PW["b"].close()
        _PW["p"].stop()
        _PW.clear()
