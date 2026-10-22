"""The teaser's eight portraits alone, four a row (the author, 2026-10-22: "Do it with just the portraits", of the
backdrop and frame tests, to ask their friends): each sheet is make.py's portraits in their frames, without the map
or the cards.

    CHROMIUM_PATH=/opt/pw-browsers/chromium python3 dist/teasers/vale_of_reibonne/portraits.py   (after a build)

Writes beside this file portraits_vanilla.png and portraits_plain.png (the two backdrops) and portraits_photo.png (the
pictures as they are), each with the top row in the diplomacy screen's octagon and the bottom row in the politics
screen's arch (the author: "Each collage should have the top four on the octagon, the bottom four in the arch").
"""
import os

import make

H = 300                                  # a frame's height
SHEETS = {"vanilla": "vanilla", "plain": "plain", "photo": "photo"}


def sheet(name, kind, styles):
    cells = "".join(make.frame_html(make.ruler(t, kind)[1], styles.get(t, "arch"), H) if styles.get(t)
                    else f'<div class="portrait"><img src="{make.uri(make.ruler(t, kind)[1])}"></div>'
                    for t in make.LEFT + make.RIGHT)
    html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
html, body {{ margin: 0; background: #0b1014; }}
.grid {{ display: inline-grid; grid-template-columns: repeat(4, auto); gap: 22px 26px; padding: 30px 34px;
  background: linear-gradient(180deg, #17222a, #0e1519); justify-items: center; align-items: end; }}
.portrait {{ width: {round(H * 140 / 190)}px; height: {H}px; border-radius: {round(H * 70 / 190)}px {round(H * 70 / 190)}px 6px 6px;
  overflow: hidden; box-shadow: 0 0 0 3px #e3c77e, 0 0 0 7px #11191e, 0 0 0 8.5px rgba(201,165,90,.6); background: #1e1e20; }}
.portrait img {{ width: 100%; height: 100%; display: block; }}
.pf {{ position: relative; flex: none; }}
.pin_ {{ position: absolute; left: 0; top: 0; transform-origin: 0 0; }}
.pin_ img {{ position: absolute; display: block; }}
</style></head><body><div class="grid">{cells}</div></body></html>"""
    path = os.path.join(make.HERE, "sheet.html")
    open(path, "w", encoding="utf-8").write(html)
    from playwright.sync_api import sync_playwright
    out = os.path.join(make.HERE, f"portraits_{name}.png")
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=os.environ.get("CHROMIUM_PATH") or None)
        pg = b.new_page(viewport={"width": 1400, "height": 900})
        pg.goto("file://" + path)
        pg.wait_for_timeout(300)
        pg.locator(".grid").screenshot(path=out)
        b.close()
    os.remove(path)
    print(out)


if __name__ == "__main__":
    for name, kind in SHEETS.items():
        sheet(name, kind, make.FRAMES_TEST)
