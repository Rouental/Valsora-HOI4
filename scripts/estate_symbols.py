"""The three estates' symbols as pictures for the build (source/estates/<key>.png, 320 px, clear around): drawn from the
mockup's own drawing (deco_ui/art/proposals/three_estates/symbols.py: the rogacina, the three crowns, the sheaf and key)
in Chromium, so the game's are the mockup's. rouental_ui.py reads them; run this by hand after a change to symbols.py
and commit the pictures (the build itself needs no browser).

    CHROMIUM_PATH=/opt/pw-browsers/chromium python3 scripts/estate_symbols.py
"""
import os
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(REPO, "deco_ui", "art", "proposals", "three_estates"))
import symbols as SY  # noqa: E402

SIZE = 320
OUT = os.path.join(REPO, "source", "estates")


def main():
    from playwright.sync_api import sync_playwright
    os.makedirs(OUT, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ.get("CHROMIUM_PATH") or None)
        page = browser.new_page(viewport={"width": SIZE, "height": SIZE})
        for key in SY.DRAW:
            page.set_content(f'<html><body style="margin:0;background:transparent">{SY.symbol(key, SIZE, pad=0)}</body></html>')
            path = os.path.join(OUT, f"{key}.png")
            page.screenshot(path=path, omit_background=True, clip=dict(x=0, y=0, width=SIZE, height=SIZE))
            print(path)
        browser.close()


if __name__ == "__main__":
    main()
