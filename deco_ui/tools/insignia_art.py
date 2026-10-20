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

Each of the game's insignias keeps its drawing, recoloured (restyle()): the grey metal ones (the shield, the tower, the
spade ...) in gilt, the coloured ones in the Deco palette, each colour family moved to its Deco colour with the
picture's own shading kept (reds to the deco crimson, blues to its blue, greens to jade, yellows and oranges to gilt,
purples to plum, greys to warm lacquer and ivory). The selected rims are recoloured in gilt.

The numbered shields: the game colours an insignia with nothing (its sprite has no colour of its own: the picker's
colour sliders set the army's colour on the map, its counters and its front line), so a shield of each number comes in
FILLS' five colours, 50 new frames (81 to 130): crimson, blue, jade, lacquer and ivory, the numbers in Federo, gilt
(dark on ivory), a gilt rim.

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
# (name, fill top, fill bottom, numeral) for the numbered shields
FILLS = [("crimson", (150, 42, 40), (96, 22, 24), "gilt"), ("blue", (36, 84, 138), (18, 48, 82), "gilt"),
         ("jade", (52, 120, 104), (24, 70, 60), "gilt"), ("lacquer", (32, 44, 52), (11, 16, 20), "gilt"),
         ("ivory", (240, 232, 214), (200, 188, 156), "ink")]
NEW_N = len(FILLS) * len(NUMBERS)
ALL_N = GAME_N + NEW_N

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


def numbered(n, fill):
    name, top, bottom, ink = fill
    x0, y0, x1, y1, c = BOX
    big = Image.new("RGBA", (W * S, H * S))
    outer = mask(shield_poly(x0, y0, x1, y1, c))
    rim = mask(shield_poly(x0, y0, x1, y1, c, 1.6))
    inner_line = mask(shield_poly(x0, y0, x1, y1, c, 2.4))
    body = mask(shield_poly(x0, y0, x1, y1, c, 3.0))
    big.paste(Image.new("RGB", big.size, (14, 10, 6)), (0, 0), outer)            # the dark edge round the rim
    big.paste(gilt_grad(*big.size), (0, 0), rim)                                # the gilt rim
    big.paste(Image.new("RGB", big.size, (30, 22, 10)), (0, 0), inner_line)     # a dark line inside it
    big.paste(vgrad(*big.size, top, bottom), (0, 0), body)
    # a faint sheen on the upper left of the field
    sheen = Image.new("L", big.size)
    ImageDraw.Draw(sheen).polygon(shield_poly(x0, y0, x1, y1, c, 3.0)[:3] + [((x0 + x1) / 2 * S, (y0 + 12) * S),
                                                                            ((x0 + 3) * S, (y0 + 12) * S)], fill=38)
    sheen = Image.composite(sheen, Image.new("L", big.size), body)
    big.paste(Image.new("RGB", big.size, (255, 246, 214)), (0, 0), sheen)
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
    if ink == "gilt":
        edge = tm.filter(ImageFilter.MaxFilter(2 * S + 1))
        big.paste(Image.new("RGB", big.size, (16, 11, 6)), (0, 0), Image.composite(edge, Image.new("L", big.size), body))
        big.paste(gilt_grad(*big.size), (0, 0), tm)
    else:
        big.paste(Image.new("RGB", big.size, (22, 18, 12)), (0, 0), tm)
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
    game = [restyle(f) for f in game_frames("army_icons.dds", GAME_N)]
    new = [numbered(n, f) for f in FILLS for n in NUMBERS]
    return strip(game + new, W)


def army_selected_strip():
    game = [gilt(f) for f in game_frames("army_selected_icons.dds", GAME_N)]
    new = [selected_rim(numbered(n, f)) for f in FILLS for n in NUMBERS]
    return strip(game + new, SW)


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
