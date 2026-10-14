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
CHARS = sorted(set(CHARS))


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


def build(name, primary, size, outline, mode, weight=None, fallback=None, fb_weight=None, tracking=0,
          atlas=(512, 512), line_extra=0, kern_set=None, caps=False, gilt=False, diamond=False, blank=False):
    """mode 'ui' or 'map'. caps: lowercase code points get the uppercase glyph (small-caps-free
    all-caps setting, so engine strings like the date or a country name render in capitals).
    gilt: bake the gilt gradient into the glyph colour (use with font colour white).
    diamond: add a filled diamond at U+25C6 (used for the factory counts, coloured with § codes).
    blank: same metrics, invisible glyphs (hides an engine string while keeping its box and tooltip)."""
    fp = load(primary, size, weight)
    ffb = load(fallback, size, fb_weight) if fallback else None
    asc, desc = fp.getmetrics()
    hb = fp.getbbox("H", anchor="ls")
    cap_top, cap_h = asc + hb[1], -hb[1]
    pad = outline + 1
    glyphs = []
    for cp in CHARS:
        ch = chr(cp)
        if caps and len(ch.upper()) == 1:
            ch = ch.upper()
        if has_glyph(primary, ord(ch)):
            f = fp
        elif ffb is not None and has_glyph(fallback, ord(ch)):
            f = ffb
        else:
            continue
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
    # shelf packing, tallest first
    W, H = atlas
    order = sorted(glyphs, key=lambda g: -g["h"])
    x = y = 1
    shelf = 0
    for g in order:
        if x + g["w"] + 1 > W:
            x = 1
            y += shelf + 1
            shelf = 0
        g["x"], g["y"] = x, y
        x += g["w"] + 1
        shelf = max(shelf, g["h"])
    need_h = y + shelf + 1
    assert need_h <= H, (name, "atlas too small", need_h, H)
    tex = np.zeros((H, W, 4), np.float32)
    for g in glyphs:
        sl = (slice(g["y"], g["y"] + g["h"]), slice(g["x"], g["x"] + g["w"]))
        if mode == "ui":
            if gilt:
                rows = np.array([gilt_ramp((g["yoff"] + r - cap_top) / cap_h) for r in range(g["h"])], np.float32)
                for c in range(3):
                    tex[sl][..., c] = g["glyph"] * rows[:, c:c + 1]
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
    # invisible twin of value_17: hides an engine number we redraw ourselves, keeping its box/tooltip
    out.append(build("valsora_deco_blank", JOS, 17, 1, "ui", weight=700, atlas=(512, 256), blank=True))
    # small tracked capitals for the readout labels (mockup .rl: Josefin 600 9.5px, .17em)
    out.append(build("valsora_deco_label", JOS, 9.5, 0, "ui", weight=600, caps=True, tracking=2, kern_set=ALNUM,
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
    # body text: Josefin Sans
    out.append(build("valsora_deco_body_15", JOS, 15, 0, "ui", weight=600, kern_set=ALNUM, atlas=(512, 256)))
    out.append(build("valsora_deco_body_13", JOS, 13, 0, "ui", weight=500, kern_set=ALNUM, atlas=(512, 256)))
    # main menu buttons: tracked Josefin capitals; the big button uses Federo
    out.append(build("valsora_deco_menu_15", JOS, 15, 0, "ui", weight=600, caps=True, tracking=3, kern_set=ALNUM,
                     atlas=(512, 256)))
    out.append(build("valsora_deco_menu_big", FED, 24, 0, "ui", fallback=JOS, fb_weight=500, caps=True, tracking=5,
                     kern_set=ALNUM, atlas=(512, 512)))
    # map font: vanilla hoi_mapfont4 is size 94, lineHeight 118, base 89 -> match the cap height
    out.append(build("hoi_mapfont4", FED, 96, 3, "map", fallback=JOS, fb_weight=400, kern_set=ALNUM, line_extra=4,
                     atlas=(2048, 1024)))
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
