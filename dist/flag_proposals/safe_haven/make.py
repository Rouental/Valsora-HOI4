"""The author's motto flag (2026-10-18: "Please make a flag with the following text in calligraphic arabic on an indigo
background: ملاذٌ آمنٌ / في خضمِّ العاصفة", "A safe haven / amid the storm"), in four of Google Fonts' Arabic hands, in
white and in gold, for the author to choose from. Not in the mod: the author hasn't said whose flag it is.

    python3 dist/flag_proposals/safe_haven/make.py      (from the repository's root)

Each hand is rendered large on a transparent page by Chromium (which shapes Arabic), cropped to its ink and fitted into
the flag, so every hand fills it alike; the flags are 1640 x 1040 (82:52 at 20x: fit_flag.py or the build shrinks them).
The fonts (SIL Open Font License) are downloaded into work/fonts/arabic/ the first time, never committed."""
import base64
import io
import pathlib
import urllib.request

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
FONTS = pathlib.Path("work/fonts/arabic")
SRC = "https://raw.githubusercontent.com/google/fonts/main/ofl/"
L1, L2 = "ملاذٌ آمنٌ", "في خضمِّ العاصفة"
INDIGO = (46, 39, 117)
W, H = 1640, 1040
BOX = (0.80, 0.72)            # the ink's share of the width and height, at most
HANDS = {  # name: (font file in Google Fonts, its name, weight, line 2's size against line 1's, line spacing)
    "ruqaa": ("arefruqaa/ArefRuqaa-Bold.ttf", "Aref Ruqaa (Ruq'ah)", 700, 0.80, 1.05),
    "naskh": ("amiri/Amiri-Bold.ttf", "Amiri (Naskh)", 700, 0.78, 1.20),
    "nastaliq": ("gulzar/Gulzar-Regular.ttf", "Gulzar (Nastaliq)", 400, 0.80, 1.70),
    "kufi": ("reemkufi/ReemKufi%5Bwght%5D.ttf", "Reem Kufi (Kufi)", 600, 0.78, 1.25),
}
INKS = {"white": "#FFFFFF", "gold": "#E9C46A"}


def font(path):
    f = FONTS / pathlib.Path(path.replace("%5B", "[").replace("%5D", "]")).name
    if not f.exists():
        FONTS.mkdir(parents=True, exist_ok=True)
        f.write_bytes(urllib.request.urlopen(SRC + path).read())
    return f


def page(f, w, r, gap, ink):
    b64 = base64.b64encode(f.read_bytes()).decode()
    return f"""<!doctype html><meta charset=utf-8><style>
@font-face{{font-family:F;src:url(data:font/ttf;base64,{b64});font-weight:{w}}}
html,body{{margin:0;background:transparent}}
.t{{font-family:F;font-weight:{w};color:{ink};direction:rtl;text-align:center;line-height:{gap};padding:200px 300px;
 width:max-content}}
.a{{font-size:400px}} .b{{font-size:{400 * r}px}}
</style><div class=t lang=ar><div class=a>{L1}</div><div class=b>{L2}</div></div>"""


def main():
    flags = {}
    with sync_playwright() as p:
        br = p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        pg = br.new_page(viewport={"width": 4000, "height": 2400})
        for name, (path, _, w, r, gap) in HANDS.items():
            f = font(path)
            for ink_name, ink in INKS.items():
                pg.set_content(page(f, w, r, gap, ink))
                pg.evaluate("document.fonts.ready")
                pg.wait_for_timeout(150)
                assert pg.evaluate('document.fonts.check("40px F")'), name
                im = Image.open(io.BytesIO(pg.query_selector(".t").screenshot(omit_background=True))).convert("RGBA")
                im = im.crop(im.getchannel("A").getbbox())
                k = min(BOX[0] * W / im.width, BOX[1] * H / im.height)
                im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
                flag = Image.new("RGBA", (W, H), INDIGO + (255,))
                flag.alpha_composite(im, ((W - im.width) // 2, (H - im.height) // 2))
                flag.convert("RGB").save(HERE / f"{name}_{ink_name}.png", optimize=True)
                flags[name, ink_name] = flag.convert("RGB")
        br.close()
    # the sheet: each hand in both inks, with the game's sizes beside (82 x 52, 41 x 26, 10 x 7 enlarged)
    cw, ch, side, pad = 410, 260, 120, 14
    try:
        lab = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
        small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    except OSError:
        lab = small = ImageFont.load_default()
    sheet = Image.new("RGB", (pad + 2 * (cw + side + pad), pad + len(HANDS) * (ch + 34) + 4), (240, 236, 228))
    d = ImageDraw.Draw(sheet)
    for i, (name, (_, title, *_)) in enumerate(HANDS.items()):
        y = pad + i * (ch + 34)
        d.text((pad, y), title, fill=(40, 34, 28), font=lab)
        for j, ink_name in enumerate(INKS):
            x, im = pad + j * (cw + side + pad), flags[name, ink_name]
            sheet.paste(im.resize((cw, ch), Image.LANCZOS), (x, y + 22))
            sheet.paste(im.resize((82, 52), Image.LANCZOS), (x + cw + 10, y + 22))
            sheet.paste(im.resize((41, 26), Image.LANCZOS), (x + cw + 10, y + 82))
            sheet.paste(im.resize((10, 7), Image.LANCZOS).resize((40, 28), Image.NEAREST), (x + cw + 10, y + 116))
            d.text((x + cw + 10, y + 150), f"{name}_{ink_name}", fill=(90, 80, 66), font=small)
    sheet.save(HERE / "sheet.png", optimize=True)


if __name__ == "__main__":
    main()
