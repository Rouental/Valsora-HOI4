"""The crests, for the user to choose from (v0.8.2): the superevent's emblem and the event cards' crest.

    python proposals_crests.py      -> art/proposals/crests/options.png   (from the Deco UI's tools/ or the project root)

The user (2026-10-15): "the guillotine logo won't be suited for all superevents. Maybe come up with something else?"
and "The logo at the top of country / leader / long events doesn't read so well at this size. Maybe go with a
different design?" The superevent's crests are drawn by the Valsora build's own code (scripts/superevents_deco.py,
EMBLEMS; the mod has EMBLEM), the event cards' by gen_textures.py's (crests.py, DESIGNS; the mod has EV_CREST), each
shown at the game's size and at twice it.
"""
import base64
import io
import os
import re
import sys

from PIL import Image
from playwright.sync_api import sync_playwright

import crests as CR
from paths import ART, CHROMIUM, ROOT, TOOLS

OUT = ART + "proposals/crests/"
PROJECT = os.path.abspath(os.path.join(ROOT, ".."))
LABELS = {"star": "a compass star", "globe": "the whole globe (lit), across the frame's top edge",
          "globe_ringed": "the whole globe with its ring (the news masthead's), across the frame's top edge",
          "hourglass": "an hourglass",
          "laurel": "a laurel wreath round a star", "guillotine": "before: the mockup's guillotine",
          "keystone": "a stepped keystone with a diamond", "fan": "a fan of seven broad rays",
          "diamond": "a diamond on the edge, with rules", "sunburst": "before: the half sunburst (v0.7)"}
SAMPLE_TITLE = "The Rouentaise Civil War"


def uri(img):
    b = io.BytesIO()
    img.save(b, "PNG")
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()


def superevent_crests():
    """{emblem: the top of the superevent's frame with that crest and a title, 1:1}"""
    cwd = os.getcwd()
    os.chdir(PROJECT)                    # superevents_deco names its fonts from the project's root
    sys.path.insert(0, os.path.join(PROJECT, "scripts"))
    try:
        import superevents_deco as SD
        out = {}
        for e in SD.EMBLEMS:
            p = Image.fromarray(SD.panel(e))
            p.alpha_composite(Image.fromarray(SD.title_strip(SAMPLE_TITLE)), (SD.PIC_X, SD.CREST + SD.TITLE_Y))
            bg = Image.new("RGBA", p.size, (30, 36, 34, 255))
            bg.alpha_composite(p)
            out[e] = bg.crop((0, 0, SD.PW, SD.CREST + 64))
        return out, SD.EMBLEM
    finally:
        os.chdir(cwd)


def event_tops(css):
    """{design: the top piece of an event card with that crest, drawn as gen_textures.py draws it (1:1)}"""
    body = "".join(f'<div class="s" id="{d}" style="left:0;top:{i * 131}px;width:581px;height:121px">{CR.ev_top(d)}</div>'
                   for i, d in enumerate(CR.DESIGNS))
    page = OUT + "tops.html"
    open(page, "w", encoding="utf-8").write(f"<html><head><style>{css}</style></head><body>{body}</body></html>")
    out = {}
    with sync_playwright() as p:
        br = p.chromium.launch(**CHROMIUM)
        pg = br.new_page(viewport={"width": 700, "height": 131 * len(CR.DESIGNS)}, device_scale_factor=1)
        pg.goto("file://" + page)
        pg.wait_for_timeout(500)
        for d in CR.DESIGNS:
            out[d] = Image.open(io.BytesIO(pg.query_selector("#" + d).screenshot(omit_background=True))).convert("RGBA")
        br.close()
    os.remove(page)
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    css = re.search(r'CSS = """(.*?)"""', open(os.path.join(TOOLS, "gen_textures.py")).read(), re.S).group(1)
    se, se_mod = superevent_crests()
    tops = event_tops(css)
    rows = []
    for e in [se_mod] + [e for e in se if e != se_mod]:
        rows.append(("THE SUPEREVENT'S CREST" if not rows else None, ("In the mod: " if e == se_mod else "") + LABELS[e], se[e]))
    first = True
    for d in [CR.EV_CREST] + [d for d in CR.DESIGNS if d != CR.EV_CREST]:
        bg = Image.new("RGBA", tops[d].size, (30, 36, 34, 255))
        bg.alpha_composite(tops[d])
        rows.append(("THE EVENT CARDS' CREST" if first else None, ("In the mod: " if d == CR.EV_CREST else "") + LABELS[d],
                     bg.crop((150, 0, 431, 72))))
        first = False
    cards = ""
    for head, label, im in rows:
        if head:
            cards += f"<h2>{head}</h2>"
        zoom = im.crop(((im.width - 280) // 2, 0, (im.width + 280) // 2, im.height)) if im.width > 600 else im
        cards += (f'<div class="lab">{label}</div><div class="row"><img src="{uri(im)}" width="{im.width}">'
                  f'<img src="{uri(zoom)}" width="{zoom.width * 2}" class="px"></div>')
    html = ("<html><head><style>"
            "body{margin:0;padding:18px 24px;background:#0B1014;font:600 14px sans-serif;color:#B7A680;width:1560px}"
            "h2{font:400 20px serif;letter-spacing:.15em;color:#E3C77E;margin:26px 0 4px}"
            ".lab{margin:14px 0 6px}.row{display:flex;gap:24px;align-items:flex-start}"
            "img{display:block}.px{image-rendering:pixelated}"
            "</style></head><body><div style='font:400 24px serif;color:#E3C77E;letter-spacing:.15em'>THE CRESTS: OPTIONS "
            "<span style='font:600 13px sans-serif;color:#8E826A;letter-spacing:0'>(each at the game's size, then twice it)</span></div>"
            + cards + "</body></html>")
    page = OUT + "options.html"
    open(page, "w", encoding="utf-8").write(html)
    with sync_playwright() as p:
        br = p.chromium.launch(**CHROMIUM)
        pg = br.new_page(viewport={"width": 1608, "height": 900})
        pg.goto("file://" + page)
        pg.wait_for_timeout(300)
        pg.screenshot(path=OUT + "options.png", full_page=True)
        br.close()
    os.remove(page)
    print("wrote", OUT + "options.png")


if __name__ == "__main__":
    main()
