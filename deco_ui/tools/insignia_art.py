"""The army insignias (the insignia picker's list, and every army card, fleet and air wing that shows one), in the Deco
UI's palette, and ten new ones: the numbers 1 to 10 on a shield (2026-10-20, the author: "Please edit the default army
icons to better suit the UI. In addition, make 10 new icons that are the numbers 1 through 10 on a shield whose color
can be changed").

The game's insignias are the 81 frames of GFX_theatre_army_shield (gfx/army_icons/army_icons.dds, 33 x 32 a frame)
and GFX_theatre_army_shield_selected (army_selected_icons.dds, 35 x 34: a glowing rim along the insignia's edge, drawn
over it when its army is selected), the army groups' 6 of GFX_theatre_army_group_shield (and _selected, 33 x 32). The picker
lists every frame of the sprite, so new insignias are new frames at the strip's end (make_insignia.py gives the game's
theatreselector.gfx the new frame counts); the frames the game has keep their places, so a saved game's armies keep
their insignias.

How the game colours them (2026-10-20, the author's screenshot of the picker, with hue, saturation and brightness sliders
and colour swatches; gfx/army_icons/army_icons.txt): the picker lists the frames army_icons.txt names, one `icon` block
a frame in order, and colours every frame whose block lacks `color_override = no` with the army's colour, its grey
shading tinted; the game's first 14 (the shield, the tower, the spade ... the star, the bars) are such grey masks, the
rest keep their own colours and are each for a base-game tag (`available`), so Valsora's countries see only the 14 and
four more of the Waking the Tiger set. v0.12 had redrawn the 14 in gilt, which the tint turned into the game's own red
silhouettes again, and added 50 numbered shields the list file did not name, so the picker never showed them ("the
army icons you designed aren't there"). Now (make_insignia.py writes the list file):
  frames 0-13      the game's 14, still tintable, redrawn as Deco masks (deco_mask): a dark edge, a light line
                   just inside it, the face shaded light to dark from the top, the game's own detail kept faintly
  frames 14-80     the game's own nation insignias, recoloured into the Deco palette (restyle), as before
  frames 81-90     the numbers 1 to 10 on a Deco shield, tintable ("a shield whose color can be changed"): grey masks
                   as the 14, the number light in a dark outline
  frames 91-104    the 14 in gilt, as v0.12 drew them, with `color_override = no`: kept in the gilt whatever the
                   army's colour

gen_textures.py adds them (keys ia_*); preview_insignia.py draws the game's and ours side by side.
"""
import colorsys
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from art_util import GILT_RAMP, gilt, img_tag, vanilla_frames
from paths import FONTS_SRC

A = "gfx/army_icons/"
GAME_N, GROUP_N = 81, 6
W, H, SW, SH = 33, 32, 35, 34             # a frame; a selected frame
NUMBERS = range(1, 11)
TINT_N = 14                                 # the game's tintable insignias, frames 0-13
NUMBERED0 = GAME_N                          # the numbered shields' first frame (81)
GILT0 = NUMBERED0 + len(NUMBERS)            # the gilt copies' first frame (91)
NEW_N = len(NUMBERS) + TINT_N
ALL_N = GAME_N + NEW_N                      # 105

# the Deco colour each colour family of the game's insignias moves to: (hue 0-1, saturation)
FAMILY = [(0.0, "red", (0.0, .62)), (20 / 360, "gilt", (40 / 360, .62)), (70 / 360, "jade", (166 / 360, .42)),
          (170 / 360, "blue", (210 / 360, .58)), (265 / 360, "plum", (310 / 360, .30)), (330 / 360, "red", (0.0, .62))]
WARM = (40 / 360, .14)                      # the greys: warm lacquer to ivory


def family(h):
    out = FAMILY[0][2]
    for start, _, hs in FAMILY:
        if h >= start:
            out = hs
    return out


def restyle(fr):
    """one of the game's insignias in the Deco palette"""
    a = np.asarray(fr.convert("RGBA"), dtype=float) / 255
    rgb, al = a[..., :3], a[..., 3]
    hls = np.array([colorsys.rgb_to_hls(*p) for p in rgb.reshape(-1, 3)]).reshape(rgb.shape)
    hh, ll, ss = hls[..., 0], hls[..., 1], hls[..., 2]
    m = al > .3
    sat = (rgb.max(-1) - rgb.min(-1))
    if not m.any() or sat[m].mean() < .03:          # grey metal: gilt, as the game's own small icons
        return gilt(fr)
    out = np.zeros_like(rgb)
    for i in range(rgb.shape[0]):
        for j in range(rgb.shape[1]):
            if sat[i, j] < .05:
                h2, s2 = WARM
                l2 = .05 + ll[i, j] * .88               # black to lacquer, white to ivory
            else:                                       # a dull colour stays dull (the game's olive and khaki)
                h2, s2 = family(hh[i, j])
                s2 = s2 * min(1.0, max(.25, sat[i, j] / .35))
                l2 = .06 + ll[i, j] * .86
            out[i, j] = colorsys.hls_to_rgb(h2, l2, s2)
    return Image.fromarray(np.dstack([out * 255, al * 255]).clip(0, 255).astype(np.uint8), "RGBA")


def _shift(m, dx, dy):
    out = np.zeros_like(m)
    h, w = m.shape
    out[max(dy, 0):h + min(dy, 0), max(dx, 0):w + min(dx, 0)] = m[max(-dy, 0):h + min(-dy, 0), max(-dx, 0):w + min(-dx, 0)]
    return out


def erode(m, n=1):
    for _ in range(n):
        m = m & _shift(m, 1, 0) & _shift(m, -1, 0) & _shift(m, 0, 1) & _shift(m, 0, -1)
    return m


# the grey masks' tones (the game multiplies the army's colour into them: the light line the colour at its brightest,
# the edge near black, the face between, lighter at the top)
EDGE, INLINE, FACE_TOP, FACE_BOTTOM = 40, 238, 196, 118


def deco_mask(fr):
    """one of the game's tintable insignias as a Deco grey mask: the edge dark, a light line one pixel in, the face a
    gradient from the top, with a third of the game's own shading kept so its holes and bevels still read"""
    a = np.asarray(fr.convert("RGBA"), dtype=float)
    al = a[..., 3]
    lum = a[..., :3].mean(-1)
    m = al > 128
    if not m.any():
        return fr
    ys = np.nonzero(m.any(1))[0]
    top, bottom = ys.min(), ys.max()
    t = np.clip((np.arange(a.shape[0]) - top) / max(1, bottom - top), 0, 1)[:, None]
    face = FACE_TOP * (1 - t) + FACE_BOTTOM * t
    lo, hi = np.percentile(lum[m], 5), np.percentile(lum[m], 95)
    detail = np.clip((lum - lo) / max(1.0, hi - lo), 0, 1) - .5      # the game's shading, about its middle
    g = face + detail * 70
    e1 = erode(m)
    g = np.where(m & ~e1, EDGE, g)                                    # the edge
    inner = e1 & ~erode(e1)
    g = np.where(inner & erode(m, 1), np.maximum(g, INLINE), g)       # the light line inside it
    g = np.where(~m, EDGE, g)                                         # the anti-aliased rim outside the mask: the edge
    g = np.clip(g, 0, 255)
    return Image.fromarray(np.dstack([g, g, g, al]).astype(np.uint8), "RGBA")


def strip(frames, w):
    im = Image.new("RGBA", (w * len(frames), frames[0].height))
    for k, f in enumerate(frames):
        im.alpha_composite(f, (k * w, 0))
    return im


# ---------------------------------------------------------------- the numbered shields
S = 8                                        # drawn 8 times over, then shrunk


def shield_poly(x0, y0, x1, y1, c, d=0.0):
    """a Deco shield: a flat top with cut corners, straight sides, then curving in to a point"""
    x0, y0, x1, y1 = x0 + d, y0 + d, x1 - d, y1 - d * 1.4
    cx = (x0 + x1) / 2
    shoulder = y0 + (y1 - y0) * .42
    pts = [(x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, shoulder)]
    for k in range(1, 17):                   # the right flank, bulging, down to the point
        t = k / 16
        pts.append((x1 - (x1 - cx) * t ** 1.9, shoulder + (y1 - shoulder) * t ** .85))
    for k in range(15, 0, -1):               # and up the left one
        t = k / 16
        pts.append((x0 + (cx - x0) * t ** 1.9, shoulder + (y1 - shoulder) * t ** .85))
    pts += [(x0, shoulder), (x0, y0 + c)]
    return [(x * S, y * S) for x, y in pts]


BOX = (3, 1.5, 30, 30.5, 4)                  # the shield's box in the 33 x 32 frame, its corners cut by 4


def vgrad(w, h, top, bottom):
    t = np.linspace(0, 1, h)[:, None, None]
    g = np.array(top)[None, None] * (1 - t) + np.array(bottom)[None, None] * t
    return Image.fromarray(np.repeat(g, w, 1).astype(np.uint8), "RGB")


def gilt_grad(w, h):
    xs = [s for s, _ in GILT_RAMP]
    t = np.linspace(1, .25, h)
    col = np.stack([np.interp(t, xs, [c[i] for _, c in GILT_RAMP]) for i in range(3)], -1)
    return Image.fromarray(np.repeat(col[:, None], w, 1).astype(np.uint8), "RGB")


def mask(poly, w=W, h=H):
    m = Image.new("L", (w * S, h * S))
    ImageDraw.Draw(m).polygon(poly, fill=255)
    return m


def grey_grad(w, h, top, bottom):
    return vgrad(w, h, (top,) * 3, (bottom,) * 3)


def numbered(n):
    """the number n on a Deco shield, a grey mask for the game's tint: a dark edge, a light rim, a dark line inside it,
    the field shaded from the top, the number light in a dark outline"""
    x0, y0, x1, y1, c = BOX
    big = Image.new("RGBA", (W * S, H * S))
    outer = mask(shield_poly(x0, y0, x1, y1, c))
    rim = mask(shield_poly(x0, y0, x1, y1, c, 1.6))
    inner_line = mask(shield_poly(x0, y0, x1, y1, c, 2.4))
    body = mask(shield_poly(x0, y0, x1, y1, c, 3.0))
    big.paste(Image.new("RGB", big.size, (EDGE,) * 3), (0, 0), outer)                 # the dark edge round the rim
    big.paste(grey_grad(*big.size, 236, 168), (0, 0), rim)                             # the light rim
    big.paste(Image.new("RGB", big.size, (52,) * 3), (0, 0), inner_line)              # a dark line inside it
    big.paste(grey_grad(*big.size, FACE_TOP - 12, FACE_BOTTOM - 22), (0, 0), body)    # the field
    # the number, centred on the field's upper two thirds
    txt = str(n)
    size = (19 if len(txt) == 1 else 16) * S
    font = ImageFont.truetype(os.path.join(FONTS_SRC, "federo/Federo-Regular.ttf"), int(size))
    tm = Image.new("L", big.size)
    d = ImageDraw.Draw(tm)
    l, t, r, b = d.textbbox((0, 0), txt, font=font)
    track = -1.5 * S if len(txt) > 1 else 0
    tw = r - l + track * (len(txt) - 1)
    cx, cy = (x0 + x1) / 2 * S, (y0 + (y1 - y0) * .43) * S
    x = cx - tw / 2
    for ch in txt:
        cl, ct, cr, cb = d.textbbox((0, 0), ch, font=font)
        d.text((x - cl, cy - (b - t) / 2 - t), ch, font=font, fill=255)
        x += cr - cl + track
    edge = tm.filter(ImageFilter.MaxFilter(2 * S + 1))
    big.paste(Image.new("RGB", big.size, (22,) * 3), (0, 0), Image.composite(edge, Image.new("L", big.size), body))
    big.paste(Image.new("RGB", big.size, (250,) * 3), (0, 0), tm)
    return big.resize((W, H), Image.LANCZOS)


def selected_rim(fr, w=SW, h=SH):
    """the selected rim of a new insignia, as the game's: a glow along the inside of its edge, bright at the top"""
    al = fr.split()[-1]
    canvas = Image.new("L", (w, h))
    canvas.paste(al, ((w - fr.width) // 2, (h - fr.height) // 2))
    inner = canvas.filter(ImageFilter.MinFilter(7))
    ring = Image.fromarray(np.clip(np.asarray(canvas, float) - np.asarray(inner, float), 0, 255).astype(np.uint8))
    ring = ring.filter(ImageFilter.GaussianBlur(.6))
    col = gilt_grad(w, h).convert("RGBA")
    col.putalpha(ring)
    return col


def game_frames(rel, n):
    return vanilla_frames(A + rel, n)


def army_strip():
    src = game_frames("army_icons.dds", GAME_N)
    game = [deco_mask(f) if k < TINT_N else restyle(f) for k, f in enumerate(src)]
    new = [numbered(n) for n in NUMBERS] + [gilt(f) for f in src[:TINT_N]]
    return strip(game + new, W)


def army_selected_strip():
    sel = [gilt(f) for f in game_frames("army_selected_icons.dds", GAME_N)]
    new = [selected_rim(numbered(n)) for n in NUMBERS] + sel[:TINT_N]   # a gilt copy keeps its own's rim
    return strip(sel + new, SW)


# the list file's blocks for the new frames, in order (make_insignia.py appends them to the game's `army` list)
NEW_ICONS = ["\ticon = {\n\t}\n"] * len(NUMBERS) + ["\ticon = {\n\t\tcolor_override = no\n\t}\n"] * TINT_N


def group_strip(sel=False):
    if sel:
        return strip([gilt(f) for f in game_frames("army_group_selected_icons.dds", GROUP_N)], W)
    return strip([restyle(f) for f in game_frames("army_group_icons.dds", GROUP_N)], W)


# the two army strips are wider than the game's by the new frames (validate_preview.py holds the rest to its sizes)
RESIZED = (A + "army_icons.dds", A + "army_selected_icons.dds")

ADDS = [
    ("ia_army", A + "army_icons.dds", W * ALL_N, H, lambda: img_tag(army_strip())),
    ("ia_army_selected", A + "army_selected_icons.dds", SW * ALL_N, SH, lambda: img_tag(army_selected_strip())),
    ("ia_group", A + "army_group_icons.dds", W * GROUP_N, H, lambda: img_tag(group_strip())),
    ("ia_group_selected", A + "army_group_selected_icons.dds", W * GROUP_N, H, lambda: img_tag(group_strip(True))),
]
