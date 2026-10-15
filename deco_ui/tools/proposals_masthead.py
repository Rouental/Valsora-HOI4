"""Other names for the news masthead (v0.8.1), for the user to choose from: the mod has VALSORAN (globe) STANDARD, the
first of the names they suggested ("something like "Valsoran Standard" or Clarion or Dispatch or something like that,
so both words are the same length while keeping the news theming").

    python proposals_masthead.py     -> art/proposals/news_masthead/options.png

Each name is drawn by the texture's own code (layout_events.news_masthead) on the top of the news page. Pairs whose
words set to the same width balance by themselves; in the others the narrower word is tracked out to match, which
shows (WORLD / NEWS). Switching is one line: layout_events.NEWS_WORDS, then build_all.py and the Valsora build.
"""
import base64
import io
import os

from playwright.sync_api import sync_playwright

import layout_events as LE
from paths import ART, CHROMIUM, FONTS_SRC as G

OUT = ART + "proposals/news_masthead/"
FED = G + "federo/Federo-Regular.ttf"
NAMES = [(("VALSORAN", "STANDARD"), "In the mod: VALSORAN STANDARD (the words set to the same width by themselves)"),
         (("VALSORA", "CLARION"), "VALSORA CLARION (the same width by themselves)"),
         (("VALSORAN", "DISPATCH"), "VALSORAN DISPATCH (DISPATCH tracked out a little to match)"),
         (("VALSORAN", "CHRONICLE"), "VALSORAN CHRONICLE (VALSORAN tracked out a little)"),
         (("WORLD", "NEWS"), "For comparison, WORLD NEWS: NEWS has to be tracked out a long way to match WORLD")]


def main():
    os.makedirs(OUT, exist_ok=True)
    b = io.BytesIO()
    globe, rim = LE.news_globe()
    globe.save(b, "PNG")
    uri = "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()
    cards = ""
    for words, label in NAMES:
        svg, rules = LE.news_masthead(words, uri, FED, rim=rim)
        cards += (f'<div class="lab">{label}</div><div class="card"><svg width="528" height="130" style="position:absolute;'
                  'left:0;top:0"><path d="M.5,130V14.5L14.5,.5H513.5L527.5,14.5V130" fill="none" stroke="#C9A55A"/>'
                  '<path d="M6.5,130V16.5L16.5,6.5H511.5L521.5,16.5V130" fill="none" stroke="rgba(201,165,90,.4)"/>'
                  f'<path d="{rules}" stroke="#C9A55A" stroke-width="1"/>'
                  f'<rect x="{LE.NEWS_PIC_X - 1.5}" y="89.5" width="{LE.NEWS_PIC_W + 3}" height="60" fill="#1B262D" '
                  f'stroke="#C9A55A"/></svg>{svg}</div>')
    html = (f"<html><head><style>@font-face{{font-family:'Federo';src:url('file://{FED}')}}"
            "body{margin:0;padding:18px 24px;background:#0B1014;font:600 14px sans-serif;color:#B7A680;width:1104px}"
            ".lab{margin:16px 0 6px}.card{position:relative;width:528px;height:130px;zoom:2;overflow:hidden;"
            "background:repeating-linear-gradient(90deg,rgba(255,255,255,.025) 0 1px,transparent 1px 7px),"
            "linear-gradient(180deg,#17222A,#11191E)}</style></head><body>"
            "<div style='font:400 22px Federo;color:#E3C77E;letter-spacing:.15em'>THE NEWS MASTHEAD: OTHER NAMES</div>"
            + cards + "</body></html>")
    page = OUT + "options.html"
    open(page, "w", encoding="utf-8").write(html)
    with sync_playwright() as p:
        br = p.chromium.launch(**CHROMIUM)
        pg = br.new_page(viewport={"width": 1152, "height": 900})
        pg.goto("file://" + page)
        pg.wait_for_timeout(500)
        pg.screenshot(path=OUT + "options.png", full_page=True)
        br.close()
    os.remove(page)
    print("wrote", OUT + "options.png")


if __name__ == "__main__":
    main()
