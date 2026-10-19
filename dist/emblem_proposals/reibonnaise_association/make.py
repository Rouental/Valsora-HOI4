"""The emblem of the Association of Reibonnaise States: a proposal (2026-10-19, the author: "Could you please try to
design an emblem for the Association of Reibonnaise States? It should function both as the small logo for the game,
and something that could be seen outside of it"). Not in the mod until the author says yes.

The design (Claude's), from the eight members' flags:
- a blue roundel (Guedelon's and Evriches' blue, the field of Rouental's lion and fleurs) in a gilt rim;
- a ring of eight lozenges, one for each member (Rouental, Seigne, Evriches, Hollier, Selgrave, Lustiana, Lanzerac,
  Guedelon), from the lozenges of Rouental's and Seigne's flags, as Hollier's ring of charges goes round its fleur;
- at its heart a gilt fleur-de-lis (Rouental's and Hollier's) over an upright sword (Rouental's, Selgrave's and
  Guedelon's): the faction's manifest, Strength in Unity;
- behind them the Deco UI's sunburst, faint.
Variant B has the lozenges red and white, the colours of Rouental's and Seigne's lozengy.

Written here: emblem_seal_<v>.svg / .png (with the name and the motto round it, for outside the game), emblem_<v>.svg /
.png (the roundel alone), 2048 px; game_<v>.png (the game's 200 x 100 strip: the logo and its lit frame) and
miniature_<v>.png (32 x 32); sheet.png, every size side by side, on dark and light.

    CHROMIUM_PATH=/opt/pw-browsers/chromium python3 dist/emblem_proposals/reibonnaise_association/make.py
"""
import base64
import math
import os

from PIL import Image
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__)) + "/"
ROOT = os.path.abspath(HERE + "../../..") + "/"
FEDERO = ROOT + "deco_ui/source_fonts/federo/Federo-Regular.ttf"
CHROMIUM = {"executable_path": os.environ["CHROMIUM_PATH"]} if os.environ.get("CHROMIUM_PATH") else {}

NAME = "THE ASSOCIATION OF REIBONNAISE STATES"
MOTTO = "STRENGTH IN UNITY"
BLUE, BLUE_DEEP, NAVY = "#14548C", "#0B2E52", "#0A1C30"
RED, WHITE = "#B8333A", "#F4ECD9"

DEFS = f'''<defs>
<linearGradient id="gilt" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F8E7AE"/>
<stop offset=".45" stop-color="#E3C77E"/><stop offset="1" stop-color="#8E6B2C"/></linearGradient>
<linearGradient id="giltlit" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFF6D2"/>
<stop offset=".45" stop-color="#F1DC9C"/><stop offset="1" stop-color="#B08A40"/></linearGradient>
<radialGradient id="field" cx=".5" cy=".42" r=".62"><stop offset="0" stop-color="{BLUE}"/>
<stop offset="1" stop-color="{BLUE_DEEP}"/></radialGradient>
<linearGradient id="steel" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#F2F4F5"/>
<stop offset=".5" stop-color="#C9D1D4"/><stop offset=".51" stop-color="#8C989E"/><stop offset="1" stop-color="#B7C0C4"/></linearGradient>
<path id="nameArc" d="M 500,500 m -408,0 a 408,408 0 1,1 816,0"/>
<path id="mottoArc" d="M 500,500 m -440,0 a 440,440 0 0,0 880,0"/>
</defs>'''


def _mirror(d):
    """the path mirrored about x = 500 (absolute commands only)"""
    import re
    out, cmd, is_x = [], None, True
    for t in re.findall(r"[A-Za-z]|-?\d+\.?\d*", d):
        if t.isalpha():
            out.append(t)
            cmd, is_x = t, True
            continue
        v = float(t)
        if cmd == "V":
            out.append(t)
        elif cmd == "H" or is_x:
            out.append(f"{1000 - v:g}")
            is_x = cmd == "H" or not is_x
        else:
            out.append(t)
            is_x = True
    return " ".join(out)


# the fleur-de-lis, round (500, 440), 300 tall: the middle petal, the two that sweep out and curl down, the band, the
# three feet
PETAL = "M500,290 C536,330 560,382 556,430 C553,456 538,474 524,486 L476,486 C462,474 447,456 444,430 C440,382 464,330 500,290 Z"
SIDE = ("M478,486 C470,452 446,418 420,400 C392,382 360,388 352,414 C344,440 362,462 386,462 C406,462 418,444 410,428 "
        "C430,438 446,462 450,486 Z")
BAND = "M418,486 H582 Q594,500 582,514 H418 Q406,500 418,486 Z"
FOOT = "M482,514 H518 L512,562 L500,588 L488,562 Z"
SIDE_FOOT = "M470,514 C456,534 432,548 410,546 C396,546 394,560 408,566 C438,576 466,556 482,526 Z"


def fleur(g="url(#gilt)", line="#2A1E0A", w=6):
    s = f'stroke="{line}" stroke-width="{w}" stroke-linejoin="round" fill="{g}"'
    parts = [PETAL, SIDE, _mirror(SIDE), BAND, FOOT, SIDE_FOOT, _mirror(SIDE_FOOT)]
    return (f'<g {s}>' + "".join(f'<path d="{p}"/>' for p in parts) + '</g>'
            f'<path d="M500,318 C514,350 520,392 514,440" fill="none" stroke="#FFF6D2" stroke-width="{max(2, w * .6):.1f}" '
            'stroke-linecap="round" opacity=".55"/>')


def sword(line="#2A1E0A"):
    """an upright sword behind the fleur: the blade above it, the guard and grip below its feet"""
    return (f'<g stroke="{line}" stroke-width="6" stroke-linejoin="round">'
            '<path d="M500,168 L520,212 V590 H480 V212 Z" fill="url(#steel)"/>'
            '<path d="M500,188 V556" stroke="#6E7A80" stroke-width="3"/>'
            '<path d="M412,600 Q500,580 588,600 L596,620 Q500,602 404,620 Z" fill="url(#gilt)"/>'
            '<path d="M486,620 H514 V712 H486 Z" fill="#3A2A12"/>'
            '<path d="M486,642 H514 M486,666 H514 M486,690 H514" stroke="#C9A55A" stroke-width="5"/>'
            '<circle cx="500" cy="732" r="22" fill="url(#gilt)"/>'
            '</g>')


def lozenges(variant, r=280, w=32, h=52, line="#2A1E0A", sw=6):
    out = ""
    for i in range(8):
        a = math.radians(-90 + 45 * i + 22.5)
        x, y = 500 + r * math.cos(a), 500 + r * math.sin(a)
        fill = "url(#gilt)" if variant == "A" else (RED if i % 2 == 0 else WHITE)
        rot = math.degrees(a) + 90
        out += (f'<path transform="translate({x:.1f},{y:.1f}) rotate({rot:.1f})" '
                f'd="M0,{-h}L{w},0L0,{h}L{-w},0Z" fill="{fill}" stroke="{line}" stroke-width="{sw}"/>')
        if variant == "B":
            out += (f'<path transform="translate({x:.1f},{y:.1f}) rotate({rot:.1f})" '
                    f'd="M0,{-h + 12}L{w - 8},0L0,{h - 12}L{-w + 8},0Z" fill="none" stroke="url(#gilt)" stroke-width="4"/>')
    return out


def rays(r0=40, r1=360, n=32):
    out = ""
    for i in range(n):
        a0, a1 = math.radians(360 / n * i - 2.2), math.radians(360 / n * i + 2.2)
        out += (f'<path d="M{500 + r0 * math.cos(a0):.1f},{500 + r0 * math.sin(a0):.1f} '
                f'L{500 + r1 * math.cos(a0):.1f},{500 + r1 * math.sin(a0):.1f} '
                f'L{500 + r1 * math.cos(a1):.1f},{500 + r1 * math.sin(a1):.1f} Z" fill="#FFFFFF" opacity=".05"/>')
    return out


def roundel(variant, lit=False, rim_r=372, mini=False):
    """the roundel: the gilt rim at rim_r, the field, the rays, the ring of lozenges, the sword and the fleur"""
    g = "url(#giltlit)" if lit else "url(#gilt)"
    out = (f'<circle cx="500" cy="500" r="{rim_r}" fill="{g}" stroke="#2A1E0A" stroke-width="8"/>'
           f'<circle cx="500" cy="500" r="{rim_r - 30}" fill="url(#field)" stroke="#2A1E0A" stroke-width="6"/>')
    if mini:
        # 32 px: the ring and the fleur alone, drawn heavier
        return (out + lozenges(variant, r=268, w=42, h=64, sw=10)
                + f'<g transform="translate(500,470) scale(1.32) translate(-500,-440)">{fleur(g, w=12)}</g>')
    out += (rays(r1=rim_r - 30)
            + f'<circle cx="500" cy="500" r="{rim_r - 46}" fill="none" stroke="{g}" stroke-width="5" opacity=".8"/>'
            + lozenges(variant))
    return out + sword() + fleur(g)


def seal(variant):
    """the emblem with its name and motto round it, for outside the game"""
    font = base64.b64encode(open(FEDERO, "rb").read()).decode()
    style = (f'<style>@font-face{{font-family:"VDeco";src:url(data:font/ttf;base64,{font})}}'
             'text{font-family:"VDeco",serif;fill:url(#gilt)}</style>')
    stars = "".join(f'<path transform="translate({500 + 412 * math.cos(math.radians(a)):.1f},'
                    f'{500 + 412 * math.sin(math.radians(a)):.1f}) rotate({a + 90})" d="M0,-16L9,0L0,16L-9,0Z" '
                    'fill="url(#gilt)"/>' for a in (180 - 8, 8))
    return (style
            + '<circle cx="500" cy="500" r="490" fill="url(#gilt)" stroke="#2A1E0A" stroke-width="6"/>'
            + f'<circle cx="500" cy="500" r="474" fill="{NAVY}"/>'
            + '<circle cx="500" cy="500" r="462" fill="none" stroke="url(#gilt)" stroke-width="3"/>'
            + '<circle cx="500" cy="500" r="384" fill="none" stroke="url(#gilt)" stroke-width="3"/>'
            + f'<text font-size="47" letter-spacing="7.5" text-anchor="middle"><textPath href="#nameArc" '
            f'startOffset="50%">{NAME}</textPath></text>'
            + f'<text font-size="47" letter-spacing="12" text-anchor="middle" dy="17"><textPath href="#mottoArc" '
            f'startOffset="50%">{MOTTO}</textPath></text>'
            + stars + roundel(variant))


def doc(body, size=1000, box="0 0 1000 1000", glow=False):
    flt = ('<filter id="glow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="26"/></filter>'
           if glow else "")
    halo = ('<circle cx="500" cy="500" r="400" fill="#F1DC9C" opacity=".55" filter="url(#glow)"/>' if glow else "")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="{box}">'
            f'{DEFS.replace("</defs>", flt + "</defs>")}{halo}{body}</svg>')


def render(pg, svg, path, size):
    pg.set_viewport_size({"width": size, "height": size})
    pg.set_content(f'<html><body style="margin:0;background:transparent">{svg}</body></html>')
    pg.wait_for_timeout(150)
    pg.screenshot(path=path, omit_background=True, clip={"x": 0, "y": 0, "width": size, "height": size})


def main():
    with sync_playwright() as p:
        b = p.chromium.launch(**CHROMIUM)
        pg = b.new_page(device_scale_factor=1)
        for v in "AB":
            seal_svg, plain_svg = doc(seal(v)), doc(roundel(v), box="120 120 760 760")
            open(HERE + f"emblem_seal_{v}.svg", "w").write(seal_svg)
            open(HERE + f"emblem_{v}.svg", "w").write(plain_svg)
            render(pg, seal_svg.replace('width="1000" height="1000"', 'width="2048" height="2048"'),
                   HERE + f"emblem_seal_{v}.png", 2048)
            render(pg, plain_svg.replace('width="1000" height="1000"', 'width="2048" height="2048"'),
                   HERE + f"emblem_{v}.png", 2048)
            # the game's strip: two 100 px frames, the roundel 84 px across as the game's own logos are, the second
            # lit (its gilt brighter, a soft glow), drawn at 4x and reduced
            frames = []
            for lit in (False, True):
                svg = doc(roundel(v, lit), size=400, box="80 80 840 840", glow=lit)
                render(pg, svg, HERE + "_frame.png", 400)
                frames.append(Image.open(HERE + "_frame.png").convert("RGBA").resize((100, 100), Image.LANCZOS))
            strip = Image.new("RGBA", (200, 100))
            strip.paste(frames[0], (0, 0))
            strip.paste(frames[1], (100, 0))
            strip.save(HERE + f"game_{v}.png")
            render(pg, doc(roundel(v, mini=True), size=256, box="110 110 780 780"), HERE + "_mini.png", 256)
            Image.open(HERE + "_mini.png").convert("RGBA").resize((32, 32), Image.LANCZOS).save(HERE + f"miniature_{v}.png")
        b.close()
    for f in ("_frame.png", "_mini.png"):
        os.remove(HERE + f)
    sheet()


def sheet():
    """every size side by side, on the Deco UI's lacquer and on paper"""
    W, H = 1700, 1120
    cv = Image.new("RGBA", (W, H), (17, 25, 30, 255))
    paper = Image.new("RGBA", (W // 2, H), (240, 232, 214, 255))
    cv.paste(paper, (W // 2, 0))
    for side in (0, 1):
        x0 = side * (W // 2)
        for row, v in enumerate("AB"):
            y0 = 30 + row * 545
            seal_im = Image.open(HERE + f"emblem_seal_{v}.png").resize((420, 420), Image.LANCZOS)
            cv.alpha_composite(seal_im, (x0 + 30, y0))
            plain = Image.open(HERE + f"emblem_{v}.png").resize((200, 200), Image.LANCZOS)
            cv.alpha_composite(plain, (x0 + 480, y0))
            game = Image.open(HERE + f"game_{v}.png")
            cv.alpha_composite(game, (x0 + 480, y0 + 230))
            mini = Image.open(HERE + f"miniature_{v}.png")
            cv.alpha_composite(mini, (x0 + 700, y0 + 264))
            cv.alpha_composite(mini.resize((96, 96), Image.NEAREST), (x0 + 700, y0 + 310))
    cv.convert("RGB").save(HERE + "sheet.png")


if __name__ == "__main__":
    main()
