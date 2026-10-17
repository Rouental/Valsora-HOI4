"""Generate BMFont (text .fnt + .dds) bitmap fonts in the layout HOI4 reads.

UI fonts: RGB = glyph, A = glyph + outline  (alphaChnl=1, rgb=0)  -> coloured text with a dark rim
Map font: A = glyph, RGB = outline          (alphaChnl=0, rgb=1)  -> same as vanilla hoi_mapfont4
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
from ddsutil import write_dds  # noqa: E402

from paths import MOD, FONTS_SRC as G, BUILD

CHARS = (list(range(0x20, 0x7F)) + list(range(0xA0, 0x100)) + list(range(0x100, 0x180))
         + [0x2013, 0x2014, 0x2018, 0x2019, 0x201A, 0x201C, 0x201D, 0x201E, 0x2022, 0x2026, 0x2030,
            0x2039, 0x203A, 0x20AC, 0x2122, 0x0152, 0x0153, 0x0160, 0x0161, 0x0178, 0x017D, 0x017E])
# v0.8.4: Vietnamese (the user, 2026-10-16: Plaija's names, "would it be possible for you to attempt to make those
# letters yourself"): the letters with horns (Ơ ơ Ư ư) and Latin Extended Additional's 90 tone-marked vowels. Josefin
# Sans has them all; the faces that don't (Federo, Bodoni Moda) get them composed (compose below)
VIETNAMESE = [0x01A0, 0x01A1, 0x01AF, 0x01B0] + list(range(0x1EA0, 0x1EFA))
CHARS += VIETNAMESE
# and the Latin Extended-A letters Vietnamese uses (Ă ă Đ đ Ĩ ĩ Ũ ũ: Văn, Nghĩa, Vũ), which Federo lacks too: until
# they were composed, a Federo font drew them in Josefin Sans, a letter of another face inside the word
COMPOSED = set(VIETNAMESE) | {0x0102, 0x0103, 0x0110, 0x0111, 0x0128, 0x0129, 0x0168, 0x0169}
CHARS = sorted(set(CHARS))
# The map font (country, state and city names on the map) is huge (96 px): with the Vietnamese letters its atlas grew
# to 2048 x 2048, which the game refuses ("Failed to load texture larger than MAX_TEXTURE_SIZE: gfx/fonts/
# hoi_mapfont4.tga", error.log 2026-10-16: no names on the map). The map's labels need none of them today, so the map
# font keeps the letters it had (2048 x 1024, as v0.8.3, seen in game), and the Valsora build's check_mod.py checks the
# map's own labels against it.
MAP_CHARS = [c for c in CHARS if c not in VIETNAMESE]
MAP_ATLAS = (2048, 1024)


FACE_NAMES = {"Federo": "Valsora Deco Display", "JosefinSans": "Valsora Deco Sans", "BodoniModa": "Valsora Deco Italic"}


def load(path, size, weight=None):
    f = ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM)
    if weight:
        f.set_variation_by_axes([weight])
    return f


def has_glyph(font_path, cp, cache={}):
    from fontTools.ttLib import TTFont
    if font_path not in cache:
        cache[font_path] = set(TTFont(font_path).getBestCmap())
    return cp in cache[font_path]


# ---------------------------------------------------------------- composed letters (v0.8.4)
# A letter the face lacks is built from the face's own base letter (or the nearest precomposed one it has: "â" for
# "ấ") and its marks: each mark is cut out of a precomposed letter (the mark's ink is what the letter has beyond its
# base letter), from the face itself where it has one (its own acute, grave, circumflex, tilde, breve), else from
# Josefin Sans (the hook above, the dot below, the horn), scaled to the face's letters, and set where the source sets
# it relative to its base. A tone mark beside a circumflex goes to its side, as Vietnamese type sets it.
import unicodedata as _ud

ABOVE = {0x300, 0x301, 0x302, 0x303, 0x306, 0x309}
BELOW = {0x323}
HORN = 0x31B
_CANVAS = {}


def _ink(f, text, size):
    """the text drawn at the canvas origin: (float array, origin x, origin y)"""
    S = int(size * 5) + 40
    ox, oy = S // 4, int(S * .62)
    im = Image.new("L", (S, S), 0)
    ImageDraw.Draw(im).text((ox, oy), text, font=f, fill=255, anchor="ls")
    return np.array(im, dtype=np.float32) / 255, ox, oy


def _bbox(a, thr=.08):
    ys, xs = np.nonzero(a > thr)
    if not len(xs):
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def _mark(font, path, base_letter, mark, size):
    """(mark ink, its box and the base letter's box in the source's drawing) for mark over base_letter, or None when
    the font has no letter that carries it"""
    pre = _ud.normalize("NFC", base_letter + chr(mark))
    if len(pre) != 1 or not has_glyph(path, ord(pre)) or not has_glyph(path, ord(base_letter)):
        return None
    a, _, oy = _ink(font, pre, size)
    b, _, _ = _ink(font, base_letter, size)
    grown = np.array(Image.fromarray((b * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)), np.float32) / 255
    m = np.where(grown > .05, 0, a)
    mb, bb = _bbox(m), _bbox(b)
    if mb is None or bb is None:
        return None
    return m[mb[1]:mb[3], mb[0]:mb[2]], mb, bb, oy


def _height(font, ch, size):
    b = _bbox(_ink(font, ch, size)[0])
    return b[3] - b[1] if b else 1


def _run(a, axis_line, thr=.5):
    """the longest run of ink along one row or column (a 1-d array)"""
    best = cur = 0
    for v in axis_line:
        cur = cur + 1 if v > thr else 0
        best = max(best, cur)
    return best


def _stroke(A, pts, w):
    """a stroke of width w through the points (canvas pixels), round ends, drawn 4x over and laid into A"""
    k = 4
    im = Image.new("L", (A.shape[1] * k, A.shape[0] * k), 0)
    d = ImageDraw.Draw(im)
    P = [(x * k, y * k) for x, y in pts]
    d.line(P, fill=255, width=max(1, int(round(w * k))), joint="curve")
    r = w * k / 2
    for x, y in (P[0], P[-1]):
        d.ellipse((x - r, y - r, x + r, y + r), fill=255)
    small = np.array(im.resize((A.shape[1], A.shape[0]), Image.BOX), np.float32) / 255
    np.maximum(A, small, out=A)


def _bezier(a, c, b, n=16):
    return [((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * c[0] + t * t * b[0],
             (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * c[1] + t * t * b[1]) for t in (i / n for i in range(n + 1))]


def _weights(fp, size, upper):
    """(stem width, crossbar thickness) of the face at this size"""
    a = _ink(fp, "I" if upper else "l", size)[0]
    b = _bbox(a)
    stem = _run(a, a[(b[1] + b[3]) // 2])
    h = _ink(fp, "H", size)[0]
    hb = _bbox(h)
    bar = _run(h, h[:, (hb[0] + hb[2]) // 2])
    return max(1.0, stem), max(1.0, bar)


def _horn(A, plain_box, upper, round_, fp, size):
    """Vietnamese type's horn, drawn in the face's own weight: from the top of the bowl (O) or the right stem (U), out
    to the right and up to the letter's top, as Josefin Sans draws it"""
    stem, bar = _weights(fp, size, upper)
    w = max(1.0, (stem + bar) / 2)
    x0, top, x1, bottom = plain_box
    h = _height(fp, "H", size) if upper else _height(fp, "x", size) * 1.15
    def right_at(y):
        xs = np.nonzero(A[int(round(y))] > .5)[0]
        return xs.max() + 1 if len(xs) else x1
    if round_:
        ya = top + .2 * (bottom - top)
        a = (right_at(ya) - w * .6, ya)
        b = (x1 + .12 * h, top - .03 * h)
        pts = _bezier(a, ((a[0] + b[0]) / 2 + .02 * h, (a[1] + b[1]) / 2 + .02 * h), b)
    else:
        ya = top + w / 2
        a = (right_at(ya) - w * .6, ya)
        c = (x1 + .15 * h, ya)
        b = (x1 + .17 * h, top - .08 * h)
        pts = _bezier(a, c, b)
    _stroke(A, pts, w)


def _d_stroke(fp, size):
    """đ in a face without one: its d with a bar across the stem, halfway between the x-height and the ascender"""
    A, ox, oy = _ink(fp, "d", size)
    b = _bbox(A)
    xh = _height(fp, "x", size)
    stem, bar = _weights(fp, size, False)
    y = (b[1] + (oy - xh)) / 2
    xs = np.nonzero(A[int(round(b[1] + stem))] > .5)[0]          # the stem near its top
    sx0, sx1 = (xs.min(), xs.max() + 1) if len(xs) else (b[2] - stem, b[2])
    reach = .2 * xh
    _stroke(A, [(sx0 - reach, y), (sx1 + reach * .6, y)], max(1.0, bar))
    bb = _bbox(A, .02)
    adv = max(fp.getlength("d"), bb[2] - ox + 1)
    return Image.fromarray((np.clip(A[bb[1]:bb[3], bb[0]:bb[2]], 0, 1) * 255 + .5).astype(np.uint8)), bb[0] - ox, bb[1] - oy, adv


def _drop_dot(A, oy, xh):
    """the i's dot taken off (in place): every piece of ink that ends above the x-height"""
    from scipy import ndimage
    lab, n = ndimage.label(A > .15)
    for k in range(1, n + 1):
        ys = np.nonzero(lab == k)[0]
        if ys.max() < oy - .8 * xh:
            mask = np.array(Image.fromarray(((lab == k) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3))) > 0
            A[mask] = 0


def compose(ch, fp, primary, donor, donor_path, size):
    """the letter ch built in the primary face: (L image, x0, y0 relative to the origin, advance), or None"""
    if ch == "\u0110" and has_glyph(primary, 0xD0):                # Đ is drawn as Ð, the eth, in every Latin face
        A, ox, oy = _ink(fp, "\u00D0", size)
        bb = _bbox(A, .02)
        return (Image.fromarray((np.clip(A[bb[1]:bb[3], bb[0]:bb[2]], 0, 1) * 255 + .5).astype(np.uint8)),
                bb[0] - ox, bb[1] - oy, fp.getlength("\u00D0"))
    if ch == "\u0111" and has_glyph(primary, ord("d")):
        return _d_stroke(fp, size)
    nfd = _ud.normalize("NFD", ch)
    base = marks = None
    for k in range(len(nfd), 0, -1):
        c = _ud.normalize("NFC", nfd[:k])
        if len(c) == 1 and has_glyph(primary, ord(c)):
            base, marks = c, [ord(x) for x in nfd[k:]]
            break
    if base is None or not marks:
        return None
    upper = nfd[0].isupper()
    A, ox, oy = _ink(fp, base, size)
    plain, _, _ = _ink(fp, nfd[0], size)
    pb = _bbox(plain)
    if pb is None:
        return None
    cx = (pb[0] + pb[2]) / 2
    if base == "i" and any(m in ABOVE for m in marks):          # a mark above an i takes the place of its dot (ỉ ĩ)
        _drop_dot(A, oy, _height(fp, "x", size))
    top, base_right = _bbox(A)[1], _bbox(A)[2]
    circ = None
    if 0x302 in [ord(x) for x in _ud.normalize("NFD", base)]:      # the base carries a circumflex: its box
        grown = np.array(Image.fromarray((plain * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)), np.float32) / 255
        circ = _bbox(np.where(grown > .05, 0, A))
    for m in marks:
        if m == HORN:
            _horn(A, pb, upper, nfd[0] in "Oo", fp, size)
            top = min(top, _bbox(A)[1])
            continue
        cands = "AEOUIY" if upper else "aeouiy"
        src = None
        for font, path in ((fp, primary), (donor, donor_path)):
            for L_ in cands:
                src = _mark(font, path, L_, m, size)
                if src:
                    break
            if src:
                break
        if not src:
            return None
        img, mb, bb, soy = src
        ref = "H" if upper else "x"
        s = 1.0 if font is fp else _height(fp, ref, size) / max(1, _height(font, ref, size))
        mw, mh = max(1, round(img.shape[1] * s)), max(1, round(img.shape[0] * s))
        if s != 1.0:
            img = np.array(Image.fromarray((img * 255).astype(np.uint8)).resize((mw, mh), Image.LANCZOS), np.float32) / 255
        if m in BELOW:
            x0 = cx + ((mb[0] + mb[2]) / 2 - (bb[0] + bb[2]) / 2) * s - mw / 2
            y0 = oy + (mb[1] - soy) * s
        elif circ and m in (0x300, 0x301, 0x309):               # beside the circumflex
            cw, ch_ = circ[2] - circ[0], circ[3] - circ[1]
            x0 = circ[2] - .15 * mw if m != 0x300 else circ[0] - .85 * mw
            y0 = circ[1] + .55 * ch_ - mh
            top = min(top, y0)
        else:
            gap = (bb[1] - mb[3]) * s
            x0 = cx + ((mb[0] + mb[2]) / 2 - (bb[0] + bb[2]) / 2) * s - mw / 2
            y0 = top - gap - mh
            top = y0
        x0, y0 = int(round(x0)), int(round(y0))
        A[y0:y0 + mh, x0:x0 + mw] = np.maximum(A[y0:y0 + mh, x0:x0 + mw], img)
    b = _bbox(A, .02)
    # a mark reaching past the letter (a horn, a tone mark beside a circumflex) widens it by half of what it takes beyond
    # the letter's own right side bearing, as Josefin Sans spaces its own (Ư: U + 2 px at 100 px, for a 13 px horn)
    rsb = fp.getlength(base) - (base_right - ox)
    adv = fp.getlength(base) + max(0, b[2] - base_right - rsb) * .5
    return Image.fromarray((np.clip(A[b[1]:b[3], b[0]:b[2]], 0, 1) * 255 + .5).astype(np.uint8)), b[0] - ox, b[1] - oy, adv


def disk(r):
    return ImageFilter.MaxFilter(2 * r + 1) if r > 0 else None


def gilt_ramp(t):
    """Vertical gilt gradient used by the mockup's .gilt text (CSS stops), t in 0..1 over the cap height."""
    stops = [(0, (0xF8, 0xEB, 0xBD)), (.46, (0xE4, 0xC6, 0x7E)), (.58, (0xB0, 0x8B, 0x41)), (1, (0xE9, 0xD1, 0x90))]
    t = min(1, max(0, t))
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        if t <= b:
            u = (t - a) / (b - a)
            return [(ca[i] + (cb[i] - ca[i]) * u) / 255 for i in range(3)]
    return [c / 255 for c in stops[-1][1]]


def fit_atlas(glyphs):
    """the smallest power-of-two atlas the glyphs pack into (game_fonts.py: the mod ships every texture uncompressed)"""
    best = None
    for W in (256, 512, 1024, 2048):
        need = _pack(glyphs, W, dry=True)
        if need is None:
            continue
        H = 1 << max(0, (need - 1).bit_length())
        if best is None or W * H < best[0] * best[1]:
            best = (W, H)
    return best


def _pack(glyphs, W, dry=False):
    """shelf packing, tallest first: the height used (None if a glyph is wider than W)"""
    order = sorted(glyphs, key=lambda g: -g["h"])
    x = y = 1
    shelf = 0
    for g in order:
        if g["w"] + 2 > W:
            return None
        if x + g["w"] + 1 > W:
            x = 1
            y += shelf + 1
            shelf = 0
        if not dry:
            g["x"], g["y"] = x, y
        x += g["w"] + 1
        shelf = max(shelf, g["h"])
    return y + shelf + 1


def build(name, primary, size, outline, mode, weight=None, fallback=None, fb_weight=None, tracking=0,
          atlas=(512, 512), line_extra=0, kern_set=None, caps=False, gilt=False, diamond=False, blank=False, line=None,
          chars=None, max_atlas=None, ink=None):
    """mode 'ui' or 'map'. caps: lowercase code points get the uppercase glyph (small-caps-free
    all-caps setting, so engine strings like the date or a country name render in capitals).
    gilt: bake the gilt gradient into the glyph colour (use with font colour white).
    diamond: add a filled diamond at U+25C6 (used for the factory counts, coloured with § codes).
    blank: same metrics, invisible glyphs (hides an engine string while keeping its box and tooltip).
    atlas: (width, height), or fit_atlas for the smallest that fits.
    line: (line height, where the capitals' centre sits below the line's top): another font's vertical metrics, so
    this one can replace it in the boxes laid out for it (game_fonts.py).
    chars: the code points to draw (CHARS by default); max_atlas: the atlas may not grow past it.
    ink: (r, g, b) baked into the glyphs for a font the game colours white (the typewriter's "_inverted" files: the
    game's texture holds black letters, which it draws on paper)."""
    fp = load(primary, size, weight)
    ffb = load(fallback, size, fb_weight) if fallback else None
    donor_path = fallback or G + "josefinsans/JosefinSans[wght].ttf"   # the marks a face lacks come from Josefin Sans
    donor = ffb if fallback else load(donor_path, size, 500)
    asc, desc = fp.getmetrics()
    hb = fp.getbbox("H", anchor="ls")
    cap_top, cap_h = asc + hb[1], -hb[1]
    pad = outline + 1
    glyphs = []
    for cp in (CHARS if chars is None else chars):
        ch = chr(cp)
        if caps and len(ch.upper()) == 1:
            ch = ch.upper()
        made = None
        if has_glyph(primary, ord(ch)):
            f = fp
        elif ord(ch) in COMPOSED and (made := compose(ch, fp, primary, donor, donor_path, size)) is not None:
            f = None
        elif ffb is not None and has_glyph(fallback, ord(ch)):
            f = ffb
        else:
            continue
        if made is not None:
            mi, x0, y0, adv = made
            im = Image.new("L", (mi.width + 2 * pad, mi.height + 2 * pad), 0)
            im.paste(mi, (pad, pad))
        else:
            x0, y0, x1, y1 = f.getbbox(ch, anchor="ls")
            adv = f.getlength(ch)
            gw, gh = max(1, x1 - x0), max(1, y1 - y0)
            im = Image.new("L", (gw + 2 * pad, gh + 2 * pad), 0)
            if cp != 0x20 and cp != 0xA0:
                ImageDraw.Draw(im).text((pad - x0, pad - y0), ch, font=f, fill=255, anchor="ls")
        glyph = np.array(im, dtype=np.float32) / 255
        if outline > 0:
            ol = np.array(im.filter(disk(outline)), dtype=np.float32) / 255
            ol = np.maximum(ol, glyph)
        else:
            ol = glyph
        glyphs.append(dict(cp=cp, glyph=glyph, ol=ol, w=im.width, h=im.height,
                           xoff=x0 - pad, yoff=asc + y0 - pad, adv=int(round(adv)) + tracking))
    if diamond:
        d = max(5, round(cap_h * 0.72))
        ss = 8
        big = Image.new("L", ((d + 2 * pad) * ss, (d + 2 * pad) * ss), 0)
        c = (d + 2 * pad) * ss / 2
        r = d * ss / 2
        ImageDraw.Draw(big).polygon([(c, c - r), (c + r, c), (c, c + r), (c - r, c)], fill=255)
        im = big.resize((d + 2 * pad, d + 2 * pad), Image.LANCZOS)
        glyph = np.array(im, dtype=np.float32) / 255
        ol = np.maximum(np.array(im.filter(disk(outline)), dtype=np.float32) / 255, glyph) if outline > 0 else glyph
        mid = cap_top + cap_h / 2
        glyphs.append(dict(cp=0x25C6, glyph=glyph, ol=ol, w=im.width, h=im.height, xoff=1 - pad,
                           yoff=int(round(mid - im.height / 2)), adv=d + 3 + tracking))
    if line is not None:          # another font's line: same height, the capitals centred where its are
        shift = int(round(line[1] - (asc - cap_h / 2)))
        for g in glyphs:
            g["yoff"] += shift
        asc, desc, line_extra = asc + shift, line[0] - asc - shift, 0
    # shelf packing, tallest first
    if callable(atlas):
        atlas = atlas(glyphs)
    W, H = atlas
    need_h = _pack(glyphs, W)
    assert need_h is not None, (name, "a glyph is wider than the atlas", W)
    while need_h > H:          # v0.8.4: the Vietnamese letters may need a taller atlas than the one asked for
        H *= 2
    assert max_atlas is None or (W <= max_atlas[0] and H <= max_atlas[1]), \
        (name, f"needs a {W} x {H} atlas, over {max_atlas[0]} x {max_atlas[1]}: the game refuses a larger texture")
    tex = np.zeros((H, W, 4), np.float32)
    for g in glyphs:
        sl = (slice(g["y"], g["y"] + g["h"]), slice(g["x"], g["x"] + g["w"]))
        if mode == "ui":
            if gilt:
                rows = np.array([gilt_ramp((g["yoff"] + r - cap_top) / cap_h) for r in range(g["h"])], np.float32)
                for c in range(3):
                    tex[sl][..., c] = g["glyph"] * rows[:, c:c + 1]
            elif ink is not None:
                for c in range(3):
                    tex[sl][..., c] = ink[c] / 255
            else:
                tex[sl][..., 0] = g["glyph"]
                tex[sl][..., 1] = g["glyph"]
                tex[sl][..., 2] = g["glyph"]
            tex[sl][..., 3] = g["ol"]
        else:
            tex[sl][..., 0] = g["ol"]
            tex[sl][..., 1] = g["ol"]
            tex[sl][..., 2] = g["ol"]
            tex[sl][..., 3] = g["glyph"]
    if blank:
        tex[:] = 0
    img = Image.fromarray((np.clip(tex, 0, 1) * 255 + .5).astype(np.uint8), "RGBA")
    os.makedirs(MOD + "gfx/fonts", exist_ok=True)
    write_dds(img, MOD + f"gfx/fonts/{name}.dds")
    img.save(BUILD + f"png/font_{name}.png")

    # kerning pairs from the shaping engine (primary font only)
    kerns = []
    if kern_set:
        cs = [c for c in kern_set if has_glyph(primary, ord(c.upper() if caps else c))]
        up = (lambda s: s.upper()) if caps else (lambda s: s)
        L = {c: fp.getlength(up(c)) for c in cs}
        for a in cs:
            for b in cs:
                k = int(round(fp.getlength(up(a + b)) - L[a] - L[b]))
                if k != 0:
                    kerns.append((ord(a), ord(b), k))

    line_h = asc + desc + line_extra
    if mode == "ui":
        chn = "alphaChnl=1 redChnl=0 greenChnl=0 blueChnl=0"
    else:
        chn = "alphaChnl=0 redChnl=1 greenChnl=1 blueChnl=1"
    face = os.path.basename(primary).split("[")[0].split("-")[0].replace(".ttf", "")
    # v0.8.4: the faces' own names are Reserved Font Names under their licences (Federo, Josefin Sans), which a
    # modified version, a bitmap font with letters of our own among them, may not carry; OFL_<family>.txt credits them
    face = FACE_NAMES.get(face, "Valsora Deco " + face)
    lines = [
        f'info face="{face}" size={int(round(size))} bold={1 if (weight or 0) >= 600 else 0} italic=0 charset="" unicode=1 stretchH=100 smooth=1 aa=1 padding=0,0,0,0 spacing=1,1 outline={outline}',
        f"common lineHeight={line_h} base={asc} scaleW={W} scaleH={H} pages=1 packed=0 {chn}",
        f'page id=0 file="{name}.dds"',
        f"chars count={len(glyphs)}",
    ]
    for g in sorted(glyphs, key=lambda g: g["cp"]):
        lines.append(f'char id={g["cp"]:<5} x={g["x"]:<5} y={g["y"]:<5} width={g["w"]:<5} height={g["h"]:<5} '
                     f'xoffset={g["xoff"]:<5} yoffset={g["yoff"]:<5} xadvance={g["adv"]:<5} page=0  chnl=15')
    lines.append(f"kernings count={len(kerns)}")
    for a, b, k in kerns:
        lines.append(f"kerning first={a:<5} second={b:<5} amount={k}")
    with open(MOD + f"gfx/fonts/{name}.fnt", "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    return dict(name=name, asc=asc, desc=desc, line=line_h, cap_top=cap_top, cap_h=cap_h, glyphs=len(glyphs), kerns=len(kerns), atlas_used=need_h, atlas=atlas)


ALNUM = [chr(c) for c in range(0x41, 0x5B)] + [chr(c) for c in range(0x61, 0x7B)] + list("0123456789.,:%/")
if __name__ == "__main__":
    JOS = G + "josefinsans/JosefinSans[wght].ttf"
    FED = G + "federo/Federo-Regular.ttf"
    BOD_I = G + "bodonimoda/BodoniModa-Italic[opsz,wght].ttf"
    out = []
    out.append(build("valsora_deco_value_17", JOS, 17, 1, "ui", weight=700, kern_set=ALNUM, atlas=(512, 256), diamond=True))
    out.append(build("valsora_deco_value_15", JOS, 15, 1, "ui", weight=700, kern_set=ALNUM, atlas=(512, 256), diamond=True))
    # small numbers: badges (experience, faction initiative) and the trays
    out.append(build("valsora_deco_value_12", JOS, 12, 1, "ui", weight=700, kern_set=ALNUM, atlas=(512, 256)))
    # a size down, for the top bar's logistics cell (v0.10.1, the author: "maybe shrink the text on it just a little")
    out.append(build("valsora_deco_value_11", JOS, 11, 1, "ui", weight=700, kern_set=ALNUM, atlas=(512, 256)))
    # invisible twin of value_17: hides an engine number we redraw ourselves, keeping its box/tooltip
    out.append(build("valsora_deco_blank", JOS, 17, 1, "ui", weight=700, atlas=(512, 256), blank=True))
    # small tracked capitals for the readout labels (mockup .rl: Josefin 600 9.5px, .17em)
    out.append(build("valsora_deco_label", JOS, 9.5, 0, "ui", weight=600, caps=True, tracking=2, kern_set=ALNUM,
                     atlas=(512, 128)))
    # the top bar's readout labels, tracked 1 px less (v0.9.1: room in the strip for fuel, supply and convoys)
    out.append(build("valsora_deco_label_tb", JOS, 9.5, 0, "ui", weight=600, caps=True, tracking=1, kern_set=ALNUM,
                     atlas=(512, 128)))
    # date in the cartouche: Federo capitals, light tracking
    out.append(build("valsora_deco_date", FED, 16, 0, "ui", fallback=JOS, fb_weight=500, caps=True, tracking=1,
                     kern_set=ALNUM, atlas=(512, 256)))
    # country name under the flag: gilt Federo capitals; sized so the longest single-word Valsora
    # names (Ostercoirasreich, Ponchomagnifico) fit one line, multi-word names wrap at spaces
    # the mockup's large, widely tracked name for countries whose name fits it (most of them)
    out.append(build("valsora_deco_name_big", FED, 16, 0, "ui", fallback=JOS, fb_weight=500, caps=True, tracking=4,
                     gilt=True, kern_set=ALNUM, atlas=(512, 256)))
    out.append(build("valsora_deco_name", FED, 13, 0, "ui", fallback=JOS, fb_weight=500, caps=True, tracking=1,
                     gilt=True, kern_set=ALNUM, atlas=(512, 256)))
    # ---- screens (politics etc.)
    # leader / character names: Federo, mixed case, light
    out.append(build("valsora_deco_heading_22", FED, 22, 0, "ui", fallback=JOS, fb_weight=500, kern_set=ALNUM,
                     atlas=(512, 512)))
    # screen titles (country's full name): gilt Federo capitals
    out.append(build("valsora_deco_title_18", FED, 18, 0, "ui", fallback=JOS, fb_weight=500, caps=True, tracking=1,
                     gilt=True, kern_set=ALNUM, atlas=(512, 512)))
    # big window titles (focus tree): gilt Federo capitals
    out.append(build("valsora_deco_title_24", FED, 24, 0, "ui", fallback=JOS, fb_weight=500, caps=True, tracking=3,
                     gilt=True, kern_set=ALNUM, atlas=(512, 512)))
    # section headers inside screens: gilt Federo capitals
    out.append(build("valsora_deco_section_14", FED, 14, 0, "ui", fallback=JOS, fb_weight=500, caps=True, tracking=2,
                     gilt=True, kern_set=ALNUM, atlas=(512, 256)))
    # v0.4 politics screen: leader name (Federo 24: the longest Valsora leader name fits one line),
    # the leader's description (Bodoni Moda italic, like the mockup) and section labels (tracked caps)
    out.append(build("valsora_deco_heading_24", FED, 24, 0, "ui", fallback=JOS, fb_weight=500, kern_set=ALNUM,
                     atlas=(512, 512)))
    out.append(build("valsora_deco_italic_13", BOD_I, 13, 0, "ui", fallback=JOS, fb_weight=400, kern_set=ALNUM, line_extra=-5,
                     atlas=(512, 256)))
    out.append(build("valsora_deco_section_11", JOS, 11, 0, "ui", weight=600, caps=True, tracking=3, kern_set=ALNUM,
                     atlas=(512, 256)))
    # v0.6 focus tree header and superevent (the mockups): the focus tree's title (Federo 30, .2em), its subtitle
    # and the superevent's quote (Bodoni Moda italic 15 and 18)
    out.append(build("valsora_deco_title_30", FED, 30, 0, "ui", fallback=JOS, fb_weight=500, caps=True, tracking=6,
                     gilt=True, kern_set=ALNUM, atlas=(1024, 256)))
    out.append(build("valsora_deco_italic_15", BOD_I, 15, 0, "ui", fallback=JOS, fb_weight=400, kern_set=ALNUM, line_extra=-4,
                     atlas=(512, 256)))
    out.append(build("valsora_deco_italic_18", BOD_I, 18, 0, "ui", fallback=JOS, fb_weight=400, kern_set=ALNUM, line_extra=-6,
                     atlas=(512, 256)))
    # body text: Josefin Sans
    out.append(build("valsora_deco_body_15", JOS, 15, 0, "ui", weight=600, kern_set=ALNUM, atlas=(512, 256)))
    out.append(build("valsora_deco_body_13", JOS, 13, 0, "ui", weight=500, kern_set=ALNUM, atlas=(512, 256)))
    # event options (v0.8.2): Josefin 14 on a 14 px line, so three lines (42 px) fit the option's 44 px plate (the body
    # font's 16 px line let a third line spill over it: the user's screenshot of the long test event)
    out.append(build("valsora_deco_option_14", JOS, 14, 0, "ui", weight=600, kern_set=ALNUM, atlas=(512, 256),
                     line=(14, 7)))
    # main menu buttons: tracked Josefin capitals; the big button uses Federo
    out.append(build("valsora_deco_menu_15", JOS, 15, 0, "ui", weight=600, caps=True, tracking=3, kern_set=ALNUM,
                     atlas=(512, 256)))
    out.append(build("valsora_deco_menu_big", FED, 24, 0, "ui", fallback=JOS, fb_weight=500, caps=True, tracking=5,
                     kern_set=ALNUM, atlas=(512, 512)))
    # map font: vanilla hoi_mapfont4 is size 94, lineHeight 118, base 89 -> match the cap height
    out.append(build("hoi_mapfont4", FED, 96, 3, "map", fallback=JOS, fb_weight=400, kern_set=ALNUM, line_extra=4,
                     atlas=MAP_ATLAS, chars=MAP_CHARS, max_atlas=MAP_ATLAS))
    json.dump(out, open(BUILD + "font_metrics.json", "w"), indent=1)
    # the SIL Open Font License travels with fonts derived from these families
    import shutil
    for folder, label in [("federo", "Federo"), ("josefinsans", "JosefinSans"), ("bodonimoda", "BodoniModa")]:
        shutil.copy(G + folder + "/OFL.txt", MOD + f"gfx/fonts/OFL_{label}.txt")
    for o in out:
        print(o)
    # width check for strings the engine writes into fixed boxes
    for path, size, wt, s, box in [
        (FED, 16, None, "12:00, 29 SEPTEMBER, 1939", 220),
        (JOS, 17, 700, "151.2K", 66), (JOS, 17, 700, "100%", 44), (JOS, 15, 700, "3/2/0", 44), (JOS, 15, 700, "120/80/12", 50),
    ]:
        f = load(path, size, wt)
        print(f"{s!r:32} {f.getlength(s):6.1f}px  box {box}")
