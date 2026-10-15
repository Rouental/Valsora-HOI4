"""The news masthead's globe, for the user to choose from (v0.8.2). The user (2026-10-15), on v0.8.1's: "I'm not quite
satisfied with the globe. Could you give me a few options, including an improved version of this one and the first
globe, and maybe two or three other concepts?"

    python proposals_globes.py     -> art/proposals/news_globe/options.png

Each globe (globe_art.py) is drawn in the masthead the texture has (layout_events.news_masthead), at the game's size
and at twice it. Switching is one line in gen_textures.py (GA.globe for another of globe_art's), then build_all.py and
the Valsora build.
"""
import base64
import io
import os

from playwright.sync_api import sync_playwright

import globe_art as GA
import layout_events as LE
from paths import ART, CHROMIUM, FONTS_SRC as G

OUT = ART + "proposals/news_globe/"
FED = G + "federo/Federo-Regular.ttf"
D = LE.NEWS_GLOBE
OPTIONS = [
    (lambda: GA.globe(D, LE.NEWS_VIEW), True,
     "In the mod: this one, improved (v0.8.2): lit from the upper left, a bright limb on the lit side, the graticule over "
     "the sea only and stopping short of the pole, the land a little less smoothed, seen above Nonscio and Araseos"),
    (lambda: GA.globe_flat(D), True, "Before (v0.8.1): flat gilt land, the graticule over sea and land, looking down on open sea"),
    (lambda: GA.globe_first(D), True, "The first (v0.8): every lake and channel, lit, a bright coast"),
    (lambda: GA.globe_ringed(D, LE.NEWS_VIEW), False,
     "Concept: the newsreel globe, girdled by a tilted gilt ring (behind it at the back, over it in front)"),
    (lambda: GA.world_disc(D), True,
     "Concept: the whole world on one disc, as on an emblem: a map round the north pole, the meridians as spokes"),
    (lambda: GA.globe_engraved(D, LE.NEWS_VIEW), True,
     "Concept: an engraving: the land a shade lighter than the sea, drawn by its coast in bright gilt, the graticule over both"),
]


def uri(img):
    b = io.BytesIO()
    img.save(b, "PNG")
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()


def card(svg, rules):
    return ('<div class="card"><svg width="528" height="130" style="position:absolute;left:0;top:0">'
            '<path d="M.5,130V14.5L14.5,.5H513.5L527.5,14.5V130" fill="none" stroke="#C9A55A"/>'
            '<path d="M6.5,130V16.5L16.5,6.5H511.5L521.5,16.5V130" fill="none" stroke="rgba(201,165,90,.4)"/>'
            f'<path d="{rules}" stroke="#C9A55A" stroke-width="1"/>'
            f'<rect x="{LE.NEWS_PIC_X - 1.5}" y="89.5" width="{LE.NEWS_PIC_W + 3}" height="60" fill="#1B262D" '
            f'stroke="#C9A55A"/></svg>{svg}</div>')


STYLE = ("body{margin:0;padding:18px 24px;background:#0B1014;font:600 14px sans-serif;color:#B7A680;width:1640px}"
         ".lab{margin:18px 0 6px;max-width:1500px}.row{display:flex;gap:24px;align-items:flex-start}"
         ".card{position:relative;width:528px;height:130px;overflow:hidden;"
         "background:repeating-linear-gradient(90deg,rgba(255,255,255,.025) 0 1px,transparent 1px 7px),"
         "linear-gradient(180deg,#17222A,#11191E)}img{display:block}.px{image-rendering:pixelated}")


def main():
    os.makedirs(OUT, exist_ok=True)
    head = f"<html><head><style>@font-face{{font-family:'Federo';src:url('file://{FED}')}}{STYLE}</style></head><body>"
    cards = []
    for make, rim, label in OPTIONS:
        svg, rules = LE.news_masthead(LE.NEWS_WORDS, uri(make()), FED, rim=rim)
        cards.append(card(svg, rules))
    page = OUT + "options.html"
    with sync_playwright() as p:
        br = p.chromium.launch(**CHROMIUM)
        pg = br.new_page(viewport={"width": 1688, "height": 900}, device_scale_factor=1)
        # each card at the game's size, then the sheet with each shown 1:1 and doubled pixel for pixel
        open(page, "w", encoding="utf-8").write(head + "".join(f'<div id="c{i}" style="margin:4px">{c}</div>'
                                                               for i, c in enumerate(cards)) + "</body></html>")
        pg.goto("file://" + page)
        pg.wait_for_timeout(500)
        shots = ["data:image/png;base64," + base64.b64encode(pg.query_selector(f"#c{i} .card").screenshot()).decode()
                 for i in range(len(cards))]
        rows = "".join(f'<div class="lab">{label}</div><div class="row"><img src="{u}" width="528">'
                       f'<img src="{u}" width="1056" class="px"></div>' for u, (_, _, label) in zip(shots, OPTIONS))
        open(page, "w", encoding="utf-8").write(
            head + "<div style='font:400 22px Federo;color:#E3C77E;letter-spacing:.15em'>THE NEWS MASTHEAD'S GLOBE: "
            "OPTIONS</div><div style='margin-top:4px;color:#8E826A'>each at the game's size, then twice it (the globe is "
            "60 px across in game)</div>" + rows + "</body></html>")
        pg.goto("file://" + page)
        pg.wait_for_timeout(300)
        pg.screenshot(path=OUT + "options.png", full_page=True)
        br.close()
    os.remove(page)
    print("wrote", OUT + "options.png")


if __name__ == "__main__":
    main()
