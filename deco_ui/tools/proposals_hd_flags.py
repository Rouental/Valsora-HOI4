"""A mockup of larger flags (the user, 2026-10-15: "I'm thinking about using larger flags in the mod ... Maybe do a
mockup of how it could look, but don't add anything to do with it into the mod yet"). Not in the mod.

    python proposals_hd_flags.py     -> art/proposals/hd_flags/mockup.png

The top bar's flag medallion drawn as the mod draws it (layout.py's numbers, gen_textures' look) at today's size and
at 1.5 and 2 times, with the flag at 1:1 in each: today's 82 x 52, today's flag stretched (what the game does to a
flag shown larger: it doesn't smooth them, so they pixelate), and flags made at the larger size from the author's
own files (source/flags, mostly 490 x 311). Below: what the game's unsmoothed scaling would do to the larger flags
in the places that show them at 82 x 52 (the diplomacy screen, the state panel ...), unless those are re-laid too.
"""
import base64
import io
import os

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

import layout as L
from paths import ART, CHROMIUM, FONTS_SRC as G

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FLAGS = os.path.join(ROOT, "source", "flags")
OUT = ART + "proposals/hd_flags/"
LAC = "repeating-linear-gradient(90deg,rgba(255,255,255,.025) 0 1px,transparent 1px 7px)"


def uri(im):
    b = io.BytesIO()
    im.save(b, "PNG")
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()


def flag(tag, w, h, how="lanczos", base=None):
    """tag's flag at w x h: from the author's file (Lanczos), or `base` scaled without smoothing (as the game does)"""
    if how == "nearest":
        return base.resize((w, h), Image.NEAREST)
    im = Image.open(os.path.join(FLAGS, tag + ".png")).convert("RGB")
    return im.resize((w, h), Image.LANCZOS)


def medallion(s, flag_img, name):
    """the medallion at scale s with the flag at 1:1 (its frame follows the flag's size)"""
    W, H = L.MED["w"] * s, L.MED["h"] * s
    s1, s2 = L.MED_STEPS[0] * s, L.MED_STEPS[1] * s
    pts = [(0, -2), (W, -2), (W, s1), (W * .88, s1), (W * .88, s2), (W * .74, s2), (W * .74, H), (W * .26, H), (W * .26, s2),
           (W * .12, s2), (W * .12, s1), (0, s1)]
    poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    fw, fh = flag_img.size
    fx, fy = (W - (fw + 16)) / 2, (L.FLAG_FRAME["y"] - L.MED["y"]) * s
    cy = fy + (fh + 16) / 2
    wings = "".join(
        f'<line x1="{(fx - 5 - ln * s) if side == 0 else fx + fw + 16 + 5}" y1="{cy + dy * s}" '
        f'x2="{(fx - 5) if side == 0 else fx + fw + 16 + 5 + ln * s}" y2="{cy + dy * s}" stroke="url(#wg{side})" stroke-width="1"/>'
        for dy, ln in [(-6, 18), (0, 13), (6, 8)] for side in (0, 1))
    ny = (L.NAME["y"] - L.MED["y"]) * s + (fh - 52 * s)
    return f'''<div style="position:relative;width:{W}px;height:{H + max(0, fh - 52 * s)}px">
<svg width="{W}" height="{H + max(0, fh - 52 * s)}" style="position:absolute;left:0;top:0"><defs>
<linearGradient id="gr" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E8CD84"/><stop offset="1" stop-color="#8B6A2C"/></linearGradient>
<linearGradient id="wg0" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#C9A55A" stop-opacity="0"/><stop offset="1" stop-color="#C9A55A"/></linearGradient>
<linearGradient id="wg1" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#C9A55A"/><stop offset="1" stop-color="#C9A55A" stop-opacity="0"/></linearGradient>
<linearGradient id="pl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1B262D"/><stop offset="1" stop-color="#0C1317"/></linearGradient>
</defs><polygon points="{poly}" fill="url(#pl)" stroke="url(#gr)" stroke-width="1.5" transform="translate(0 {max(0, fh - 52 * s) * 0})"/>{wings}</svg>
<div style="position:absolute;left:{fx}px;top:{fy}px;width:{fw + 16}px;height:{fh + 16}px;background:#C9A55A;box-shadow:0 4px 10px rgba(0,0,0,.55)"></div>
<div style="position:absolute;left:{fx + 1}px;top:{fy + 1}px;width:{fw + 14}px;height:{fh + 14}px;background:{LAC},linear-gradient(180deg,#16212A,#0B1115)"></div>
<div style="position:absolute;left:{fx + 6}px;top:{fy + 6}px;width:{fw + 4}px;height:{fh + 4}px;background:linear-gradient(180deg,#F1DC9C,#9C7A36)"></div>
<img src="{uri(flag_img)}" style="position:absolute;left:{fx + 8}px;top:{fy + 8}px;width:{fw}px;height:{fh}px;image-rendering:pixelated">
<div style="position:absolute;left:0;width:{W}px;top:{ny}px;height:{40 * s}px;display:flex;align-items:center;justify-content:center;
font:400 {16 * s}px Federo;letter-spacing:{.25 * s}em;background:linear-gradient(180deg,#FFF3C8,#E3C77E 45%,#9C7836);
-webkit-background-clip:text;color:transparent">{name}</div></div>'''


def main():
    os.makedirs(OUT, exist_ok=True)
    rou = flag("ROU", 82, 52)
    cols = [("Today: 82 x 52 at 1:1", medallion(1, rou, "ROUENTAL")),
            ("Today's flag shown 1.5x: the game doesn't smooth it", medallion(1.5, flag("ROU", 123, 78, "nearest", rou), "ROUENTAL")),
            ("A 123 x 78 flag at 1:1 (1.5x)", medallion(1.5, flag("ROU", 123, 78), "ROUENTAL")),
            ("A 164 x 104 flag at 1:1 (2x)", medallion(2, flag("ROU", 164, 104), "ROUENTAL"))]
    # a close-up (3x) of the lion: today's flag stretched 1.5x, and a flag made at 123 x 78
    zoom = lambda im: im.crop((0, 0, 62, 39)).resize((186, 117), Image.NEAREST)
    close = (f'<div class="cell"><img src="{uri(zoom(flag("ROU", 123, 78, "nearest", rou)))}" width="186" height="117">'
             f'<img src="{uri(zoom(flag("ROU", 123, 78)))}" width="186" height="117"></div>')
    tags = ["ROU", "CRD", "VIL", "KRI", "SNH"]
    strip = ""
    for t in tags:
        big = flag(t, 164, 104)
        strip += (f'<div class="cell"><img src="{uri(flag(t, 82, 52))}" width="82" height="52">'
                  f'<img src="{uri(big.resize((82, 52), Image.NEAREST))}" width="82" height="52">'
                  f'<img src="{uri(big)}" width="164" height="104"></div>')
    css = f"""@font-face{{font-family:'Federo';src:url('file://{G}federo/Federo-Regular.ttf')}}
@font-face{{font-family:'Josefin Sans';src:url('file://{G}josefinsans/JosefinSans[wght].ttf');font-weight:100 700}}
body{{margin:0;background:#0E1519;font:600 15px 'Josefin Sans';color:#E8DFC8}}
.row{{display:flex;gap:42px;align-items:flex-start;padding:28px 36px 10px}}
.col{{display:flex;flex-direction:column;align-items:center;gap:14px}}
.lab{{width:300px;text-align:center;color:#B7A680;font-size:14px;line-height:1.35}}
h1{{font:400 22px Federo;letter-spacing:.2em;margin:26px 36px 0;color:#E3C77E}}
p{{margin:8px 36px;max-width:1240px;line-height:1.45;color:#C9BFA6}}
.cell{{display:flex;gap:18px;align-items:center;padding:8px 0}}
.cell img{{image-rendering:pixelated}}
.strip{{display:grid;grid-template-columns:repeat(3,auto);justify-content:start;gap:10px 40px;padding:6px 36px 24px}}"""
    html = (f"<html><head><style>{css}</style></head><body><h1>LARGER FLAGS: A MOCKUP (NOT IN THE MOD)</h1>"
            "<p>The top bar's medallion with the flag at 1:1, as the mod draws it today and at 1.5 and 2 times. "
            "The game doesn't smooth flags, so a flag shown larger than its texture pixelates (second). Flags made at "
            "the larger size from your own files stay sharp (third and fourth).</p><div class='row'>"
            + "".join(f'<div class="col">{m}<div class="lab">{lab}</div></div>' for lab, m in cols)
            + "</div><p>Close up (3x): the second medallion's flag, and the third's.</p><div class='strip'>" + close + "</div>"
            "<h1>ELSEWHERE</h1><p>Each flag: today's 82 x 52; a 164 x 104 flag shrunk to 82 x 52 the way the "
              "game scales flags (no smoothing: jagged), as it would be wherever a screen still shows it at the old size; "
              "the 164 x 104 flag itself. So larger flags mean re-laying every place that shows the big flag, or "
              "accepting the jagged ones there.</p><div class='strip'>" + strip + "</div></body></html>")
    page = OUT + "mockup.html"
    open(page, "w", encoding="utf-8").write(html)
    with sync_playwright() as p:
        b = p.chromium.launch(**CHROMIUM)
        pg = b.new_page(viewport={"width": 1400, "height": 900})
        pg.goto("file://" + page)
        pg.wait_for_timeout(600)
        pg.screenshot(path=OUT + "mockup.png", full_page=True)
        b.close()
    os.remove(page)
    print("wrote", OUT + "mockup.png")


if __name__ == "__main__":
    main()
