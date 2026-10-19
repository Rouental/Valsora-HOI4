"""Helpers shared by gen_textures.py and the art modules it draws from (designer_art.py, mapview_art.py ...): the
chamfered lacquer bars, frame strips, and the game's own glyphs recoloured in gilt. Moved out of gen_textures.py on
2026-10-17 (unchanged), so an art module can use them without importing gen_textures (which draws on import)."""
import base64
import io as _io

import numpy as np
from PIL import Image

from paths import VANILLA as _VANILLA


# the art modules gen_textures.py draws (each an ADDS list of (key, path, w, h, function)); validate_preview.py holds
# every one of their textures to the game's size
ART_MODULES = ["designer_art", "battleplan_art", "mapview_art", "combat_art", "diplo_art", "setup_art", "window_art",
               "popup_art", "diplomacy_art", "decisions_art", "music_art",
               "production_art", "icons_art"]

def chamfer(c):
    return f"polygon({c}px 0,calc(100% - {c}px) 0,100% {c}px,100% calc(100% - {c}px),calc(100% - {c}px) 100%,{c}px 100%,0 calc(100% - {c}px),0 {c}px)"


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
