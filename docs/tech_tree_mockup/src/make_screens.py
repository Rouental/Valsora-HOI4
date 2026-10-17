"""Renders docs/tech_tree_mockup/screens/: every folder as a 1920 x 1080 in-game screen, an overview sheet and a
contact sheet, from index.html in headless Chromium. Also checks the page (clipped names, overlaps, console errors,
the phone width).

    python3 docs/tech_tree_mockup/src/make_screens.py [--tier modern] [--check-only]

Fonts: the page loads Federo, Josefin Sans and Bodoni Moda from Google Fonts; here they are served from the Deco UI's
own copies (deco_ui/source_fonts/), so the pictures don't depend on the network.
"""
import argparse
import os
import sys

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(ROOT, "..", ".."))
FONTS = os.path.join(REPO, "deco_ui", "source_fonts")
CHROMIUM = os.environ.get("CHROMIUM_PATH", "/opt/pw-browsers/chromium")
ORDER = ["infantry", "support", "artillery", "armour", "naval", "naval_support", "air", "electronics", "industry",
         "projects", "doc_land", "doc_naval", "doc_air", "doc_sf", "armour_classic", "naval_classic", "air_classic"]

LOCAL_CSS = """
@font-face { font-family: 'Federo'; src: url(https://fonts.gstatic.com/local/federo/Federo-Regular.ttf); }
@font-face { font-family: 'Josefin Sans'; src: url(https://fonts.gstatic.com/local/josefinsans/JosefinSans[wght].ttf); font-weight: 100 700; font-style: normal; }
@font-face { font-family: 'Josefin Sans'; src: url(https://fonts.gstatic.com/local/josefinsans/JosefinSans-Italic[wght].ttf); font-weight: 100 700; font-style: italic; }
@font-face { font-family: 'Bodoni Moda'; src: url(https://fonts.gstatic.com/local/bodonimoda/BodoniModa[opsz,wght].ttf); font-weight: 400 900; font-style: normal; }
@font-face { font-family: 'Bodoni Moda'; src: url(https://fonts.gstatic.com/local/bodonimoda/BodoniModa-Italic[opsz,wght].ttf); font-weight: 400 900; font-style: italic; }
"""


def route_fonts(page):
    page.route("https://fonts.googleapis.com/**", lambda r: r.fulfill(status=200, content_type="text/css", body=LOCAL_CSS))

    def font(route):
        rel = route.request.url.split("/local/", 1)[1].replace("%5B", "[").replace("%5D", "]").replace("%2C", ",")
        route.fulfill(status=200, content_type="font/ttf", path=os.path.join(FONTS, rel))
    page.route("https://fonts.gstatic.com/local/**", font)


CHECK_JS = """() => {
  const out = {clipped: [], overlaps: [], offside: []};
  const cards = [...document.querySelectorAll('.tc, .pc, .sd, .gd')].filter(c => c.offsetParent);
  for (const c of cards) {
    const n = c.querySelector('.tn, .pn, .sn, b');
    if (n && n.scrollHeight > n.clientHeight + 1) out.clipped.push(c.dataset.id || c.dataset.doc);
  }
  const tcs = [...document.querySelectorAll('.canvas .tc')].map(c => ({id: c.dataset.id, r: c.getBoundingClientRect()}));
  for (let i = 0; i < tcs.length; i++) for (let j = i + 1; j < tcs.length; j++) {
    const a = tcs[i].r, b = tcs[j].r;
    if (a.left < b.right - 1 && b.left < a.right - 1 && a.top < b.bottom - 1 && b.top < a.bottom - 1) out.overlaps.push(tcs[i].id + '/' + tcs[j].id);
  }
  return out;
}"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tier", default="modern")
    ap.add_argument("--check-only", action="store_true")
    a = ap.parse_args()
    url = "file://" + os.path.join(ROOT, "index.html")
    os.makedirs(os.path.join(ROOT, "screens"), exist_ok=True)
    problems = []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROMIUM)
        pg = b.new_page(viewport={"width": 1920, "height": 1080})
        errors = []
        pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: errors.append(str(e)))
        route_fonts(pg)
        pg.goto(url + "#overview")
        pg.wait_for_function("document.fonts.status === 'loaded'")
        pg.wait_for_timeout(300)
        # web view of every folder and tier: clipped names and overlaps
        for key in ORDER:
            pg.evaluate(f"() => {{ tt.state.dlc = !'{key}'.endswith('_classic'); tt.state.tab = '{key}'; tt.render(); }}"
                        .replace("endswith", "endsWith"))
            r = pg.evaluate(CHECK_JS)
            if r["clipped"]:
                problems.append(f"{key}: clipped names {r['clipped']}")
            if r["overlaps"]:
                problems.append(f"{key}: overlapping cards {r['overlaps']}")
        if not a.check_only:
            # the in-game screens
            scales = {}
            for i, key in enumerate(ORDER, 1):
                s = pg.evaluate(f"() => tt.showGame('{key}', '{a.tier}', true)")
                pg.wait_for_timeout(120)
                scales[key] = s
                pg.screenshot(path=os.path.join(ROOT, "screens", f"{i:02d}_{key}.png"))
            pg.evaluate("() => tt.hideGame()")
            # the overview sheet: the overview page at 1920 wide
            pg.evaluate("() => { tt.state.tab = 'overview'; tt.state.tier = '%s'; tt.state.dlc = true; tt.render(); window.scrollTo(0,0); }" % a.tier)
            pg.wait_for_timeout(150)
            pg.screenshot(path=os.path.join(ROOT, "screens", "00_overview.png"), full_page=True)
            print("scales:", {k: round(v, 2) for k, v in scales.items()})
        # phone width: no horizontal page scroll
        ph = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2)
        route_fonts(ph)
        for h in ("overview", "infantry", "projects", "doc_land"):
            ph.goto("about:blank")
            ph.goto(url + "#" + h)
            ph.wait_for_timeout(250)
            w = ph.evaluate("() => [document.documentElement.scrollWidth, window.innerWidth]")
            if w[0] > w[1]:
                problems.append(f"phone #{h}: page {w[0]} px wide in a {w[1]} px window")
        b.close()
    if not a.check_only:
        contact_sheet()
    if errors:
        problems.append("console: " + " | ".join(errors[:5]))
    for pr in problems:
        print("PROBLEM", pr)
    print("problems:", len(problems))
    return 1 if problems else 0


def contact_sheet():
    from PIL import Image, ImageDraw, ImageFont
    shots = [f for f in sorted(os.listdir(os.path.join(ROOT, "screens"))) if f[:2].isdigit() and f[:2] != "00"
             and f.endswith(".png") and "contact" not in f]
    cols, tw, th, pad, top = 4, 470, 264, 10, 70
    rows = (len(shots) + cols - 1) // cols
    W = cols * tw + (cols + 1) * pad
    H = top + rows * (th + 28) + pad
    sheet = Image.new("RGB", (W, H), (11, 16, 20))
    d = ImageDraw.Draw(sheet)
    try:
        title = ImageFont.truetype(os.path.join(FONTS, "federo", "Federo-Regular.ttf"), 30)
        lab = ImageFont.truetype(os.path.join(FONTS, "josefinsans", "JosefinSans[wght].ttf"), 15)
    except OSError:
        title = lab = ImageFont.load_default()
    d.text((pad + 4, 18), "VALSORA · RESEARCH 2036 · EVERY SCREEN", font=title, fill=(227, 199, 126))
    for i, f in enumerate(shots):
        im = Image.open(os.path.join(ROOT, "screens", f)).convert("RGB").resize((tw, th), Image.LANCZOS)
        x = pad + (i % cols) * (tw + pad)
        y = top + (i // cols) * (th + 28)
        sheet.paste(im, (x, y))
        d.rectangle([x - 1, y - 1, x + tw, y + th], outline=(139, 106, 44))
        d.text((x + 2, y + th + 5), f[3:-4].replace("_", " ").upper(), font=lab, fill=(183, 166, 128))
    sheet.save(os.path.join(ROOT, "screens", "00_contact_sheet.png"), optimize=True)


if __name__ == "__main__":
    sys.exit(main())
