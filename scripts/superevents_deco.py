"""The superevent window in the Deco UI's style (common.DECO_UI): the mockup's Superevent board
(deco_ui/art/mockups/source/Superevent.html), drawn here with numpy and Pillow so that the build needs nothing
else, and so that a new superevent gets its title strip and framed picture without the Deco UI's own tools.

The window covers the screen: a dark veil over the map (its background) with faint gilt rays round the middle,
and the superevent's panel in the middle, every element a direct child of the window (the scripted GUI's
visibility triggers name them). The panel is one picture: a gilt crest above the frame, the frame (lacquer,
gilt border and corner brackets, the rings round the picture) and the now-playing tab below it. Over it: the
title strip (one per superevent, gilt Federo capitals between stepped hairlines, baked because its hairlines
follow the title's width), the picture (with gilt fans and arcs in its corners), a diamond over the picture's
lower edge, the quote (Bodoni Moda italic), the attribution, the gilt button and the song.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONTS = Path("deco_ui/source_fonts")
FEDERO = FONTS / "federo/Federo-Regular.ttf"
JOSEFIN = FONTS / "josefinsans/JosefinSans[wght].ttf"

FW, FH = 900, 645          # the frame: the size of the window before the Deco UI
CREST = 40                 # panel rows above the frame (the crest rises 36 px over it)
TAB = 35                   # panel rows below it (the now-playing tab, 34 px)
PW, PH = FW, CREST + FH + TAB
PIC_X, PIC_Y, PIC_W, PIC_H = 30, 62, 840, 420     # in the frame
TITLE_Y, TITLE_H = 21, 40  # the title strip in the frame (the mockup's 32 px row at y 22, with room round it; 3 px
                           # lower since the crest's globe, whose bright foot met the capitals' tops)
QUOTE = (60, 500, 780, 70)
AUTHOR = (60, 572, 780, 20)
BUTTON = (339, 598, 222, 36)
DIAMOND = (430, 462, 40)   # the diamond's picture (x, y, size), centred on the picture's lower edge
TAB_X, TAB_W = 190, 520   # the now-playing tab under the frame (wider than the mockup's 440: both songs fit)
SONG = (TAB_X + 40, 653, TAB_W - 80, 16)  # the song, between a note at each end of the tab (y 644-678)
RAYS_W, RAYS_H = 960, 540  # the rays and vignette, drawn at scale 2 over a 1920x1080 screen

GILT_LINE = (201, 165, 90)
SS = 4                     # supersampling for edges that are not along the pixel grid


def hex_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def layer(w, h):
    return np.zeros((h, w, 4), np.float32)


def paint(dst, mask, rgb, alpha=1.0):
    """source-over: paint colour rgb (or an HxWx3 array) where mask (0..1, or a scalar) says, at alpha"""
    a = np.clip(np.asarray(mask, np.float32) * alpha, 0, 1)
    if a.ndim == 0:
        a = np.full(dst.shape[:2], float(a), np.float32)
    rgb = np.broadcast_to(np.asarray(rgb, np.float32), dst.shape[:2] + (3,))
    da = dst[..., 3]
    oa = a + da * (1 - a)
    with np.errstate(invalid="ignore", divide="ignore"):
        for c in range(3):
            dst[..., c] = np.where(oa > 0, (rgb[..., c] * a + dst[..., c] * da * (1 - a)) / oa, 0)
    dst[..., 3] = oa


def to_u8(img):
    return np.clip(np.round(img), 0, 255).astype(np.uint8)


def shrink(big):
    """a supersampled float layer (straight alpha) to 1x, averaging in premultiplied space"""
    h, w = big.shape[0] // SS, big.shape[1] // SS
    pre = big.copy()
    pre[..., :3] *= pre[..., 3:4]
    pre = pre.reshape(h, SS, w, SS, 4).mean(axis=(1, 3))
    out = pre.copy()
    with np.errstate(invalid="ignore", divide="ignore"):
        out[..., :3] = np.where(pre[..., 3:4] > 0, pre[..., :3] / pre[..., 3:4], 0)
    return out


def ramp(t, stops):
    """colour at t (array, 0..1) along CSS-like stops [(pos, (r, g, b)), ...]"""
    t = np.clip(t, 0, 1)
    out = np.zeros(t.shape + (3,), np.float32)
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        m = (t >= p0) & (t <= p1)
        u = ((t - p0) / max(p1 - p0, 1e-6))[..., None]
        out[m] = (np.array(c0) + (np.array(c1) - np.array(c0)) * u)[m]
    out[t < stops[0][0]] = stops[0][1]
    out[t > stops[-1][0]] = stops[-1][1]
    return out


def poly_mask(w, h, pts, ss=SS):
    """anti-aliased polygon coverage (pts in pixels)"""
    im = Image.new("L", (w * ss, h * ss), 0)
    ImageDraw.Draw(im).polygon([(x * ss, y * ss) for x, y in pts], fill=255)
    return np.asarray(im.resize((w, h), Image.BOX), np.float32) / 255


def disc(w, h, cx, cy, r, ss=SS):
    """anti-aliased coverage of the disc of radius r centred at (cx, cy) (pixel centres at +0.5)"""
    ys, xs = np.mgrid[0:h * ss, 0:w * ss].astype(np.float32)
    d = np.hypot((xs + .5) / ss - cx, (ys + .5) / ss - cy)
    return (d <= r).astype(np.float32).reshape(h, ss, w, ss).mean(axis=(1, 3))


def ring(w, h, cx, cy, r_out, r_in):
    return np.clip(disc(w, h, cx, cy, r_out) - disc(w, h, cx, cy, r_in), 0, 1)


def conic_rays(w, h, cx, cy, start, ray, period, ss=SS):
    """coverage of CSS repeating-conic-gradient rays: angle (clockwise from north, from `start`) mod period < ray"""
    ys, xs = np.mgrid[0:h * ss, 0:w * ss].astype(np.float32)
    ang = (np.degrees(np.arctan2((xs + .5) / ss - cx, -((ys + .5) / ss - cy))) - start) % 360
    return ((ang % period) < ray).astype(np.float32).reshape(h, ss, w, ss).mean(axis=(1, 3))


def brackets(img, x0, y0, x1, y1, inset=6, size=22, inner=7, inner_size=8, colour=(232, 205, 132)):
    """the mockup's .ck corner brackets: a 2 px L of `size`, and a smaller one `inner` px inside it"""
    for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        cx = x0 + inset if sx > 0 else x1 - inset - 1
        cy = y0 + inset if sy > 0 else y1 - inset - 1
        for off, n in ((0, size), (inner, inner_size)):
            ox, oy = cx + sx * off, cy + sy * off
            xa, xb = sorted((ox, ox + sx * (n - 1)))
            ya, yb = sorted((oy, oy + sy * 1))
            img[ya:yb + 1, xa:xb + 1, :3] = colour
            img[ya:yb + 1, xa:xb + 1, 3] = 1
            xa, xb = sorted((ox, ox + sx * 1))
            ya, yb = sorted((oy, oy + sy * (n - 1)))
            img[ya:yb + 1, xa:xb + 1, :3] = colour
            img[ya:yb + 1, xa:xb + 1, 3] = 1


def svg_strokes(w, h, segments, width, colour, scale, ox, oy, ss=SS):
    """thin strokes (polylines in an SVG viewBox, scaled and offset) as an anti-aliased layer"""
    im = Image.new("L", (w * ss, h * ss), 0)
    d = ImageDraw.Draw(im)
    for pts in segments:
        p = [((ox + x * scale) * ss, (oy + y * scale) * ss) for x, y in pts]
        d.line(p, fill=255, width=max(1, round(width * ss)), joint="curve")
        r = width * ss / 2
        for x, y in (p[0], p[-1]):
            d.ellipse((x - r, y - r, x + r, y + r), fill=255)
    out = layer(w, h)
    paint(out, np.asarray(im.resize((w, h), Image.BOX), np.float32) / 255, colour)
    return out


# ---------------------------------------------------------------- the crest
# The crest over the frame is a half disc of gilt rays round a medallion, of which the top half shows (the mockup's).
# Its emblem was the mockup's guillotine until 2026-10-15 (the author: "the guillotine logo won't be suited for all
# superevents. Maybe come up with something else?"): EMBLEM picks one of EMBLEMS, which proposals_crests.py
# (deco_ui/tools) shows side by side.
CREST_W, CREST_H = 120, 60      # the crest's picture; the medallion's centre is its bottom middle
MED_R = 38                      # the medallion's radius (its top half shows)
EMBLEMS = ("star", "globe", "hourglass", "laurel", "guillotine")
EMBLEM = "globe"


def gilt_fill(h, w, y0, y1):
    """the gilt gradient from pale at row y0 to deep at row y1, as an HxWx3 array"""
    yy = np.mgrid[0:h, 0:w][0].astype(np.float32) + .5
    return ramp((yy - y0) / max(y1 - y0, 1), [(0, hex_rgb("#FFF3C8")), (.4, hex_rgb("#E8CD84")), (1, hex_rgb("#8B6A2C"))])


def star_points(cx, cy, r_main, r_diag, r_in, turn=0.0):
    """an eight-pointed star's points: [(centre, left, tip, right, long?)], the long ones north, east, south, west"""
    out = []
    for k in range(8):
        a = np.radians(turn + k * 45)
        r = r_main if k % 2 == 0 else r_diag
        tip = (cx + r * np.sin(a), cy - r * np.cos(a))
        left = (cx + r_in * np.sin(a - np.radians(22.5)), cy - r_in * np.cos(a - np.radians(22.5)))
        right = (cx + r_in * np.sin(a + np.radians(22.5)), cy - r_in * np.cos(a + np.radians(22.5)))
        out.append(((cx, cy), left, tip, right, k % 2 == 0))
    return out


def draw_star(dst, cx, cy, r_main, r_diag, r_in, dark="#8B6A2C"):
    """a compass star: the short points behind the long ones, each point's left half light and right half dark,
    parted from what is under it by a thin lacquer edge"""
    h, w = dst.shape[:2]
    pale = gilt_fill(h, w, cy - r_main, cy + r_main)
    for long_first in (False, True):
        for c, left, tip, right, is_long in star_points(cx, cy, r_main, r_diag, r_in):
            if is_long != long_first:
                continue
            kite = poly_mask(w, h, [c, left, tip, right])
            grown = np.clip(ndi_grow(kite), 0, 1)
            paint(dst, grown, hex_rgb("#0B1115"), .9)
            paint(dst, poly_mask(w, h, [c, left, tip]), pale)
            paint(dst, poly_mask(w, h, [c, tip, right]), hex_rgb(dark) if is_long else hex_rgb("#A9843E"))


def ndi_grow(mask, px=1):
    """the mask grown by about px pixels (a soft max filter), for an edge round a shape"""
    from scipy import ndimage as ndi
    return ndi.maximum_filter(mask, size=2 * px + 1)


def crest(emblem=None):
    """the crest's picture (CREST_W x CREST_H, straight alpha floats)"""
    emblem = emblem or EMBLEM
    cw, ch = CREST_W, CREST_H
    cx, cy = cw / 2, ch
    out = layer(cw, ch)
    rays_base = np.where(disc(cw, ch, cx, cy, 34.5)[..., None] > .5, hex_rgb("#1B262D"), hex_rgb("#0B1115"))
    outer = disc(cw, ch, cx, cy, 59.5)
    paint(out, outer, rays_base)
    paint(out, outer * conic_rays(cw, ch, cx, cy, 0, 2.5, 10), hex_rgb("#E8CD84"))
    yy, xx = np.mgrid[0:ch, 0:cw].astype(np.float32)
    dd = np.hypot(xx + .5 - cx, yy + .5 - cy)
    if emblem == "guillotine":       # the mockup's: a red medallion
        fill = ramp(dd / 36, [(0, hex_rgb("#2A1210")), (1, hex_rgb("#120807"))])
    else:                            # lacquer, for any superevent
        fill = ramp(dd / 36, [(0, hex_rgb("#22323B")), (1, hex_rgb("#0E161B"))])
    paint(out, disc(cw, ch, cx, cy, MED_R), fill)
    paint(out, ring(cw, ch, cx, cy, MED_R, MED_R - 1.5), hex_rgb("#E8CD84"))
    if emblem == "star":
        draw_star(out, cx, 41, 17.5, 10.5, 4.8)
    elif emblem == "globe":
        # Valsora rising: the top half of the Deco UI's globe (deco_ui/tools/globe_art.py), as the news masthead's
        import sys
        tools = str(Path(__file__).resolve().parent.parent / "deco_ui" / "tools")
        if tools not in sys.path:
            sys.path.append(tools)       # last: its layout.py and package.py are not the build's
        import globe_art
        d = 2 * (MED_R - 4)
        g = np.asarray(globe_art.globe(d, globe_art.VIEW), np.float32)
        g = g[: d // 2]
        sub = out[int(cy) - d // 2:int(cy), int(cx) - d // 2:int(cx) - d // 2 + d]
        paint(sub, g[..., 3] / 255, g[..., :3])
        paint(out, ring(cw, ch, cx, cy, MED_R - 4, MED_R - 5), hex_rgb("#E8CD84"), .9)
    elif emblem == "hourglass":
        hx, top, bot, half = cx, 26, 58, 11
        pale = gilt_fill(ch, cw, top, bot)
        for y in (top, bot - 2.5):                               # the caps
            paint(out, poly_mask(cw, ch, [(hx - half - 2, y), (hx + half + 2, y), (hx + half + 2, y + 2.5),
                                          (hx - half - 2, y + 2.5)]), pale)
        for x in (hx - half - .5, hx + half - 1):                 # the posts
            paint(out, poly_mask(cw, ch, [(x, top + 2.5), (x + 1.5, top + 2.5), (x + 1.5, bot - 2.5), (x, bot - 2.5)]), pale)
        mid = (top + bot) / 2
        glass = [(hx - half + 2, top + 3.5), (hx + half - 2, top + 3.5), (hx + 1, mid), (hx + half - 2, bot - 3.5),
                 (hx - half + 2, bot - 3.5), (hx - 1, mid)]
        paint(out, poly_mask(cw, ch, glass), hex_rgb("#E8CD84"), .35)
        inner = [(hx - half + 3.3, top + 4.5), (hx + half - 3.3, top + 4.5), (hx, mid - .5), (hx + half - 3.3, bot - 4.5),
                 (hx - half + 3.3, bot - 4.5), (hx, mid + .5)]
        paint(out, poly_mask(cw, ch, inner), hex_rgb("#0E161B"))
        paint(out, poly_mask(cw, ch, [(hx - 3.2, mid - 4.5), (hx + 3.2, mid - 4.5), (hx, mid - .8)]), pale)   # sand above
        paint(out, poly_mask(cw, ch, [(hx - .5, mid), (hx + .5, mid), (hx + .5, bot - 6), (hx - .5, bot - 6)]), pale)
        paint(out, poly_mask(cw, ch, [(hx - half + 3.5, bot - 4.5), (hx + half - 3.5, bot - 4.5), (hx, bot - 9.5)]), pale)
    elif emblem == "laurel":
        # two laurel branches up the medallion's sides round a small star: leaves on alternate sides of the stem,
        # smaller towards the top
        pale = gilt_fill(ch, cw, 26, 60)
        r = 27.5
        for side in (-1, 1):
            th = np.radians(np.linspace(6, 74, 40))
            stem = [(cx + side * r * np.cos(t), cy - 1 - r * np.sin(t)) for t in th]
            paint(out, svg_strokes(cw, ch, [stem], 1.1, hex_rgb("#C9A55A"), 1, 0, 0)[..., 3], hex_rgb("#C9A55A"))
            for i in range(7):
                t = np.radians(10 + 10 * i)
                bx, by = cx + side * r * np.cos(t), cy - 1 - r * np.sin(t)
                tx, ty = -side * np.sin(t), -np.cos(t)                 # along the stem, upwards
                nx, ny = side * np.cos(t), -np.sin(t)                   # outwards
                o = 2.4 if i % 2 == 0 else -2.4
                ln, wd = 4.6 - .25 * i, 1.9 - .08 * i
                lx, ly = bx + nx * o + tx * 1.2, by + ny * o + ty * 1.2
                ax, ay = tx + nx * (.45 if o > 0 else -.45), ty + ny * (.45 if o > 0 else -.45)
                norm = np.hypot(ax, ay)
                ax, ay = ax / norm, ay / norm
                pts = [(lx + ax * ln * np.cos(a) - ay * wd * np.sin(a), ly + ay * ln * np.cos(a) + ax * wd * np.sin(a))
                       for a in np.linspace(0, 2 * np.pi, 24, endpoint=False)]
                paint(out, poly_mask(cw, ch, pts), pale)
        draw_star(out, cx, 43, 10, 6, 2.8)
    elif emblem == "guillotine":
        icon = svg_strokes(cw, ch, [[(13, 44), (13, 4)], [(35, 44), (35, 4)], [(11, 4), (37, 4)],
                                    [(13, 10), (35, 16), (35, 21), (13, 21), (13, 10)]],
                           2.6 * 30 / 48, hex_rgb("#F6E3A6"), 30 / 48, 45, 30)
        paint(out, icon[..., 3], icon[..., :3])
    else:
        raise ValueError(f"no emblem {emblem!r}: {EMBLEMS}")
    return out


# ---------------------------------------------------------------- the panel picture
def panel(emblem=None):
    img = layer(PW, PH)
    fy = CREST
    # the frame: lacquer (a glow at the top, 7 px hairline stripes, dark to darker), then its edge
    ys, xs = np.mgrid[0:FH, 0:FW].astype(np.float32)
    base = ramp(ys / (FH - 1), [(0, hex_rgb("#172128")), (1, hex_rgb("#0B1115"))])
    stripe = (xs % 7 == 0).astype(np.float32) * .022
    base = base * (1 - stripe[..., None]) + 255 * stripe[..., None]
    d = np.hypot((xs + .5 - FW / 2) / (FW / 2 * 2 ** .5), (ys + .5) / (FH * 2 ** .5))
    glow = np.clip(1 - d / .55, 0, 1) * .16
    base = base * (1 - glow[..., None]) + np.array(GILT_LINE) * glow[..., None]
    img[fy:fy + FH, :, :3] = base
    img[fy:fy + FH, :, 3] = 1
    frame = img[fy:fy + FH]
    edge = np.minimum(np.minimum(xs, FW - 1 - xs), np.minimum(ys, FH - 1 - ys))
    frame[edge == 0, :3] = GILT_LINE
    frame[(edge >= 1) & (edge <= 4), :3] = hex_rgb("#0B1115")
    m5 = edge == 5
    frame[m5, :3] = frame[m5, :3] * .5 + np.array(GILT_LINE) * .5
    brackets(frame, 0, 0, FW, FH)
    # the rings round the picture (outside it: dark, gilt, dark, faint gilt)
    for off, col, a in ((6, GILT_LINE, .55), (5, "#0B1115", 1), (4, "#0B1115", 1), (3, "#D2B064", 1), (2, "#D2B064", 1),
                        (1, "#0B1115", 1)):
        rgb = hex_rgb(col) if isinstance(col, str) else col
        x0, y0, x1, y1 = PIC_X - off, PIC_Y - off, PIC_X + PIC_W + off, PIC_Y + PIC_H + off
        m = np.zeros((FH, FW), np.float32)
        m[y0:y1, x0:x1] = 1
        m[y0 + 1:y1 - 1, x0 + 1:x1 - 1] = 0
        paint(frame, m, rgb, a)
    # the crest: a half disc of gilt rays round a medallion with an emblem (EMBLEM), rising 36 px over the frame
    x0 = (PW - CREST_W) // 2
    sub = img[fy - 36:fy - 36 + CREST_H, x0:x0 + CREST_W]
    c = crest(emblem)
    paint(sub, c[..., 3], c[..., :3])
    # the now-playing tab under the frame: a trapezoid, gilt on three sides, with a music note at each end
    tx, tw, th = TAB_X, TAB_W, 34
    tab = layer(tw, th)
    shape = poly_mask(tw, th, [(0, 0), (tw, 0), (tw - 14, th), (14, th)])
    inner = poly_mask(tw, th, [(1.1, -1), (tw - 1.1, -1), (tw - 14.4, th - 1), (14.4, th - 1)])
    paint(tab, shape, hex_rgb("#C9A55A"))
    yy = np.mgrid[0:th, 0:tw][0].astype(np.float32)
    paint(tab, inner, ramp(yy / (th - 1), [(0, hex_rgb("#0B1115")), (1, hex_rgb("#131C22"))]))
    for nx in (20, tw - 20 - 14):
        note = svg_strokes(tw, th, [[(9, 18), (9, 5), (20, 3), (20, 16)]], 2 * 14 / 24, hex_rgb("#E3C77E"), 14 / 24, nx, 10)
        paint(tab, note[..., 3], note[..., :3])
        for ccx, ccy in ((6, 18), (17, 16)):
            cxp, cyp = nx + ccx * 14 / 24, 10 + ccy * 14 / 24
            paint(tab, ring(tw, th, cxp, cyp, 3 * 14 / 24 + .6, 3 * 14 / 24 - .6), hex_rgb("#E3C77E"))
    sub = img[fy + FH - 1:fy + FH - 1 + th, tx:tx + tw]
    paint(sub, tab[..., 3], tab[..., :3])
    return to_u8(np.dstack([img[..., :3], img[..., 3:] * 255]))


def diamond():
    n = DIAMOND[2]
    img = layer(n, n)
    c = n / 2
    h_out = 13 * 2 ** .5
    paint(img, poly_mask(n, n, [(c, c - h_out), (c + h_out, c), (c, c + h_out), (c - h_out, c)]), hex_rgb("#D2B064"))
    h_in = h_out - 1.5 * 2 ** .5
    paint(img, poly_mask(n, n, [(c, c - h_in), (c + h_in, c), (c, c + h_in), (c - h_in, c)]), hex_rgb("#0B1115"))
    h_sq = 4.5 * 2 ** .5
    paint(img, poly_mask(n, n, [(c, c - h_sq), (c + h_sq, c), (c, c + h_sq), (c - h_sq, c)]), hex_rgb("#E8CD84"))
    return to_u8(np.dstack([img[..., :3], img[..., 3:] * 255]))


def josefin(size, weight):
    f = ImageFont.truetype(str(JOSEFIN), size)
    try:
        f.set_variation_by_axes([weight])
    except OSError:
        pass
    return f


def tracked(draw, x, y, text, font, tracking, fill):
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += font.getlength(ch) + tracking
    return x


def tracked_width(text, font, tracking):
    return sum(font.getlength(ch) for ch in text) + tracking * (len(text) - 1)


def button():
    w, h = BUTTON[2], BUTTON[3]
    img = layer(w, h)
    yy = np.mgrid[0:h, 0:w][0].astype(np.float32)
    paint(img, poly_mask(w, h, [(10, 0), (w - 10, 0), (w, h / 2), (w - 10, h), (10, h), (0, h / 2)]),
          ramp(yy / (h - 1), [(0, hex_rgb("#FFF0C2")), (1, hex_rgb("#8B6A2C"))]))
    paint(img, poly_mask(w, h, [(10.5, 1), (w - 10.5, 1), (w - 1, h / 2), (w - 10.5, h - 1), (10.5, h - 1), (1, h / 2)]),
          ramp((yy - 1) / (h - 3), [(0, hex_rgb("#F3DFA0")), (.46, hex_rgb("#D5B266")), (.54, hex_rgb("#B08B41")),
                                    (1, hex_rgb("#DCBD72"))]))
    text = "HISTORY MARCHES ON"
    f = josefin(round(12.5 * SS), 700)
    tw = tracked_width(text, f, .22 * 12.5 * SS) - .22 * 12.5 * SS * 0
    im = Image.new("L", (w * SS, h * SS), 0)
    dr = ImageDraw.Draw(im)
    asc, desc = f.getmetrics()
    top = (h * SS - (asc + desc)) / 2 + 1.5 * SS + desc * .15
    tracked(dr, (w * SS - tw) / 2, top, text, f, .22 * 12.5 * SS, 255)
    paint(img, np.asarray(im.resize((w, h), Image.BOX), np.float32) / 255, hex_rgb("#1A1307"))
    return to_u8(np.dstack([img[..., :3], img[..., 3:] * 255]))


def title_strip(title):
    """the title in gilt Federo capitals between stepped hairlines, centred in the frame's 840 px row"""
    w, h = PIC_W, TITLE_H
    text = title.upper()
    size, gap, line_w = 31.0, 22, 120
    while True:
        f = ImageFont.truetype(str(FEDERO), round(size * SS))
        tw = tracked_width(text, f, .2 * size * SS) / SS
        if tw + 2 * (line_w + gap) <= w - 8 or size <= 20:
            break
        size -= 1
    group = tw + 2 * (line_w + gap)
    gx = (w - group) / 2
    mid = h / 2
    img = layer(w, h)
    # hairlines: three per side, the inner two shorter (stepped), fading out towards the frame
    for side in (-1, 1):
        for i, (dy, cut) in enumerate(((-4, 0), (0, 30), (4, 60))):
            y = int(round(mid + dy - .5))
            if side < 0:
                xa, xb = gx + cut, gx + line_w
            else:
                xa, xb = gx + group - line_w, gx + group - cut
            xs = np.arange(int(np.floor(xa)), int(np.ceil(xb)))
            t = (xs + .5 - xa) / max(xb - xa, 1)
            a = t if side < 0 else 1 - t
            row = img[y:y + 1, xs[0]:xs[-1] + 1]
            paint(row, a[None, :], GILT_LINE)
    # the title: glyph coverage at 4x, coloured by the mockup's gilt gradient over the 31 px line
    im = Image.new("L", (w * SS, h * SS), 0)
    dr = ImageDraw.Draw(im)
    asc, desc = f.getmetrics()
    line_top = mid * SS - size * SS / 2
    tracked(dr, (gx + line_w + gap) * SS, line_top + (size * SS - (asc + desc)) / 2, text, f, .2 * size * SS, 255)
    cov = np.asarray(im.resize((w, h), Image.BOX), np.float32) / 255
    yy = np.mgrid[0:h, 0:w][0].astype(np.float32)
    grad = ramp((yy + .5 - (mid - size / 2)) / size,
                [(0, hex_rgb("#FBF0C8")), (.44, hex_rgb("#E8CB82")), (.58, hex_rgb("#B08B41")), (1, hex_rgb("#EDD596"))])
    shadow = np.zeros_like(cov)
    shadow[1:, :] = cov[:-1, :]
    paint(img, shadow, (8, 10, 12), .55)
    paint(img, cov, grad)
    return to_u8(np.dstack([img[..., :3], img[..., 3:] * 255]))


def ornament_picture(rgba):
    """gilt fans of rays and arcs in the picture's corners (the mockup's .fan and .arc)"""
    img = rgba.astype(np.float32)
    img[..., 3] /= 255
    w, h = PIC_W, PIC_H
    n = 64
    fan = layer(n, n)
    cov = conic_rays(n, n, 0, 0, 90, 2.2, 9) * disc(n, n, 0, 0, 52.5)
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    cov *= ((np.degrees(np.arctan2(xx + .5, -(yy + .5))) % 360) <= 180.5)
    paint(fan, cov, (240, 216, 150), .95)
    paint(fan, ring(n, n, 0, 0, 60, 58.5), (240, 216, 150), .9)
    for fx, fy in ((False, False), (True, False), (False, True), (True, True)):
        piece = fan
        if fx:
            piece = piece[:, ::-1]
        if fy:
            piece = piece[::-1]
        x0 = w - n if fx else 0
        y0 = h - n if fy else 0
        sub = img[y0:y0 + n, x0:x0 + n]
        paint(sub, piece[..., 3], piece[..., :3])
    return to_u8(np.dstack([img[..., :3], img[..., 3:] * 255]))


def rays():
    """the veil's gilt rays round the middle of the screen and its vignette, at half size (drawn at scale 2)"""
    w, h = RAYS_W, RAYS_H
    img = layer(w, h)
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    sx, sy = (xs + .5) * 2 - 960, (ys + .5) * 2 - 540
    d = np.hypot(sx / (960 * 2 ** .5), sy / (540 * 2 ** .5))
    vig = np.clip((d - .30) / (.85 - .30), 0, 1) * .75
    paint(img, vig, (4, 6, 8))
    r = np.hypot(sx, sy)
    mask = np.where(r < 330, 0, np.where(r < 420, (r - 330) / 90, np.clip(1 - (r - 420) / 480, 0, 1)))
    ang = np.degrees(np.arctan2(sx, -sy)) % 360
    ray = np.clip(1 - np.abs((ang % 10) - 1.5) / 1.5, 0, 1) ** .5 * ((ang % 10) < 3)
    paint(img, ray * mask, (227, 199, 126), .05)
    return to_u8(np.dstack([img[..., :3], img[..., 3:] * 255]))


def veil():
    """the dark veil over the map (the mockup dims it to a third), a tiny tile the window stretches"""
    a = np.zeros((32, 32, 4), np.uint8)
    a[..., :3] = (5, 8, 10)
    a[..., 3] = round(.68 * 255)
    return a


FONT_DIR = Path("deco_ui/valsora_deco_ui/gfx/fonts")
TEXTS = {"QUOTE": ("valsora_deco_italic_18", QUOTE), "AUTHOR": ("valsora_deco_section_11", AUTHOR),
         "SONG": ("valsora_deco_label", SONG)}


def fnt(name, cache={}):
    import re
    if name not in cache:
        t = (FONT_DIR / f"{name}.fnt").read_text(encoding="utf-8")
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


def wrap(font, text, width):
    lines, cur = [], ""
    for word in text.split():
        t = (cur + " " + word).strip()
        if cur and measure(font, t) > width:
            lines.append(cur)
            cur = word
        else:
            cur = t
    return lines + [cur]


def check_texts(texts):
    """texts: {(superevent id, part): text}; stops the build when one would not fit its box"""
    bad = []
    for (sid, part), text in texts.items():
        font, (_, _, w, h) = TEXTS[part]
        lines = wrap(font, text, w)
        line_h = fnt(font)[2]["lineHeight"]
        if len(lines) * line_h > h or any(measure(font, ln) > w for ln in lines):
            bad.append(f"{sid} {part.lower()}: {len(lines)} lines of {line_h} px in a {w}x{h} box")
    if bad:
        raise SystemExit("superevent texts too long for the Deco UI's window:\n  " + "\n  ".join(bad))


def gui(supers, pictures, picture_sprite, flag):
    """the window: every element a direct child, placed from the screen's centre"""
    px, py = -PW // 2, -FH // 2 - CREST     # the panel's corner: the frame centred on the screen

    def at(x, y):
        return f"position = {{ x = {px + x} y = {py + CREST + y} }}"

    out = ["guiTypes = {", "\tcontainerWindowType = {",
           '\t\tname = "valsora_superevent_window"',
           "\t\tposition = { x = 0 y = 0 }",
           "\t\tsize = { width = 100%% height = 100%% }",
           "\t\tshow_sound = event_popup",
           "\t\thide_sound = menu_close_window",
           '\t\tbackground = { name = "Background" quadTextureSprite = "GFX_valsora_superevent_veil" }',
           "\t\ticonType = {", '\t\t\tname = "valsora_superevent_rays"', '\t\t\tspriteType = "GFX_valsora_superevent_rays"',
           f"\t\t\tposition = {{ x = {-RAYS_W} y = {-RAYS_H} }}", "\t\t\tOrientation = CENTER", "\t\t\tscale = 2",
           "\t\t\talwaystransparent = yes", "\t\t}",
           "\t\ticonType = {", '\t\t\tname = "valsora_superevent_panel"', '\t\t\tspriteType = "GFX_valsora_superevent_bg"',
           f"\t\t\tposition = {{ x = {px} y = {py} }}", "\t\t\tOrientation = CENTER", "\t\t\talwaystransparent = yes", "\t\t}"]
    for se in supers:
        out += ["\t\ticonType = {", f'\t\t\tname = "valsora_superevent_title_{se["id"]}"',
                f'\t\t\tspriteType = "GFX_valsora_superevent_title_{se["id"]}"',
                f"\t\t\t{at(PIC_X, TITLE_Y)}", "\t\t\tOrientation = CENTER", "\t\t\talwaystransparent = yes", "\t\t}"]
    for pic in pictures:
        out += ["\t\ticonType = {", f'\t\t\tname = "valsora_superevent_pic_{Path(pic).stem}"',
                f'\t\t\tspriteType = "{picture_sprite(pic)}"', f"\t\t\t{at(PIC_X, PIC_Y)}", "\t\t\tOrientation = CENTER",
                "\t\t\talwaystransparent = yes", "\t\t}"]
    out += ["\t\ticonType = {", '\t\t\tname = "valsora_superevent_diamond"', '\t\t\tspriteType = "GFX_valsora_superevent_diamond"',
            f"\t\t\t{at(DIAMOND[0], DIAMOND[1])}", "\t\t\tOrientation = CENTER", "\t\t\talwaystransparent = yes", "\t\t}"]
    for name, box, font, text in (("valsora_superevent_quote", QUOTE, "valsora_deco_italic_18", "[ValsoraSupereventQuote]"),
                                  ("valsora_superevent_author", AUTHOR, "valsora_deco_section_11", "[ValsoraSupereventAuthor]"),
                                  ("valsora_superevent_song", SONG, "valsora_deco_label", "[ValsoraSupereventSong]")):
        x, y, w, h = box
        out += ["\t\tinstantTextBoxType = {", f'\t\t\tname = "{name}"', f"\t\t\t{at(x, y)}", "\t\t\tOrientation = CENTER",
                f'\t\t\tfont = "{font}"', f'\t\t\ttext = "{text}"', f"\t\t\tmaxWidth = {w}", f"\t\t\tmaxHeight = {h}",
                "\t\t\tformat = centre", "\t\t\tvertical_alignment = center", "\t\t\tfixedsize = yes",
                "\t\t\talwaystransparent = yes", "\t\t}"]
    x, y, w, h = BUTTON
    out += ["\t\tbuttonType = {", '\t\t\tname = "valsora_superevent_close"', f"\t\t\t{at(x, y)}", "\t\t\tOrientation = CENTER",
            '\t\t\tspriteType = "GFX_valsora_superevent_button"', '\t\t\tshortcut = "ESCAPE"', "\t\t\tclicksound = click_default",
            "\t\t}", "\t}", "}", ""]
    return "\n".join(out)


def write(write_text, out, supers, pictures, picture_sprite, fit, write_dds):
    """the textures, sprites and window; returns nothing (the localisation is superevents.py's)"""
    root = out / "gfx/interface/valsora/superevent"
    root.mkdir(parents=True, exist_ok=True)
    gfx = []

    def sprite(name, rel, extra=""):
        gfx.append(f'\tspriteType = {{\n\t\tname = "{name}"\n\t\ttexturefile = "{rel}"\n{extra}\t}}\n')

    for key, img in (("panel", panel()), ("diamond", diamond()), ("button", button()), ("rays", rays())):
        write_dds(root / f"{key}.dds", img)
    write_dds(root / "veil.dds", veil())
    sprite("GFX_valsora_superevent_bg", "gfx/interface/valsora/superevent/panel.dds")
    sprite("GFX_valsora_superevent_diamond", "gfx/interface/valsora/superevent/diamond.dds")
    sprite("GFX_valsora_superevent_rays", "gfx/interface/valsora/superevent/rays.dds")
    sprite("GFX_valsora_superevent_button", "gfx/interface/valsora/superevent/button.dds",
           '\t\tnoOfFrames = 1\n\t\teffectFile = "gfx/FX/buttonstate.lua"\n')
    gfx.append('\tcorneredTileSpriteType = {\n\t\tname = "GFX_valsora_superevent_veil"\n\t\tsize = { x = 32 y = 32 }\n'
               '\t\ttextureFile = "gfx/interface/valsora/superevent/veil.dds"\n\t\tborderSize = { x = 4 y = 4 }\n'
               "\t\ttilingCenter = yes\n\t}\n")
    for se in supers:
        write_dds(root / f"title_{se['id']}.dds", title_strip(se["title"]))
        sprite(f"GFX_valsora_superevent_title_{se['id']}", f"gfx/interface/valsora/superevent/title_{se['id']}.dds")
    for pic in pictures:
        rel = f"gfx/interface/valsora/superevent_{Path(pic).stem}.dds"
        write_dds(out / rel, ornament_picture(fit(pic)))
        sprite(picture_sprite(pic), rel)
    write_text("interface/valsora_superevent.gfx", "spriteTypes = {\n" + "".join(gfx) + "}\n")
    write_text("interface/valsora_superevent.gui", gui(supers, pictures, picture_sprite, None))


def preview(supers, pictures, fit, se_index=0, backdrop=None):
    """a 1920x1080 preview of one superevent over a dimmed backdrop (the fonts drawn with their TTFs)"""
    W, H = 1920, 1080
    if backdrop is None:
        bg = np.zeros((H, W, 3), np.float32) + 40
    else:
        bg = np.asarray(Image.open(backdrop).convert("RGB").resize((W, H), Image.LANCZOS), np.float32)
    v = veil()[0, 0]
    bg = bg * (1 - v[3] / 255) + v[:3] * (v[3] / 255)
    canvas = Image.fromarray(to_u8(bg)).convert("RGBA")
    r = Image.fromarray(rays()).resize((W, H), Image.BILINEAR)
    canvas.alpha_composite(r)
    px, py = W // 2 - PW // 2, H // 2 - FH // 2 - CREST
    canvas.alpha_composite(Image.fromarray(panel()), (px, py))
    se = supers[se_index]
    fx, fy = px, py + CREST
    canvas.alpha_composite(Image.fromarray(title_strip(se["title"])), (fx + PIC_X, fy + TITLE_Y))
    canvas.alpha_composite(Image.fromarray(ornament_picture(fit(se["picture"]))), (fx + PIC_X, fy + PIC_Y))
    canvas.alpha_composite(Image.fromarray(diamond()), (fx + DIAMOND[0], fy + DIAMOND[1]))
    canvas.alpha_composite(Image.fromarray(button()), (fx + BUTTON[0], fy + BUTTON[1]))
    d = ImageDraw.Draw(canvas)
    bod = ImageFont.truetype(str(FONTS / "bodonimoda/BodoniModa-Italic[opsz,wght].ttf"), 18)
    words, lines, cur = f"“{se['quote']}”".split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if bod.getlength(t) > QUOTE[2] and cur:
            lines.append(cur)
            cur = wd
        else:
            cur = t
    lines.append(cur)
    lh = 22
    y0 = fy + QUOTE[1] + (QUOTE[3] - lh * len(lines)) / 2
    for i, ln in enumerate(lines):
        d.text((fx + QUOTE[0] + (QUOTE[2] - bod.getlength(ln)) / 2, y0 + i * lh), ln, font=bod, fill=(239, 230, 208))
    for text, box, col, size, track in ((f"\u2014 {se['author']}".upper(), AUTHOR, (235, 211, 151), 11, 3),
                                        (("Valsora Radio \u00b7 " + se.get("song_title", "")).upper(), SONG,
                                         (183, 166, 128), 9.5, 2)):
        jos = josefin(round(size), 600)
        tw = tracked_width(text, jos, track)
        tracked(d, fx + box[0] + (box[2] - tw) / 2, fy + box[1] + 3, text, jos, track, col)
    return canvas.convert("RGB")
