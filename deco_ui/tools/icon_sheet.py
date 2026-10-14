"""Render build/icon_sheet.png: every icon large, and at in-game sizes on the button backgrounds."""
from playwright.sync_api import sync_playwright

from icons import ICONS, icon
from paths import BUILD, CHROMIUM

names = [k for k in ICONS if k != "supply"]
cells = []
for n in names:
    cells.append(
        '<div style="display:flex;flex-direction:column;align-items:center;gap:6px;width:150px">'
        f'<div style="background:#0E1519;padding:6px;border:1px solid #2a3a40">{icon(n, 96, "#E3C77E", 1.5)}</div>'
        '<div style="display:flex;gap:8px;align-items:center">'
        f'<div style="width:44px;height:46px;display:flex;align-items:center;justify-content:center;background:linear-gradient(180deg,#1E2930,#0E1519);box-shadow:inset 0 0 0 1px #C9A55A">{icon(n, 24)}</div>'
        f'<div style="width:44px;height:46px;display:flex;align-items:center;justify-content:center;background:linear-gradient(180deg,#2E6E60,#153730);box-shadow:inset 0 0 0 1px #FBEAB4">{icon(n, 24, "#FBEAB4")}</div>'
        f'<div style="display:flex;flex-direction:column;gap:4px;align-items:center">{icon(n, 24, "#E3C77E", 1.4)}{icon(n, 18, "#E3C77E", 1.6)}</div></div>'
        f'<div style="font:600 12px Josefin Sans, sans-serif;letter-spacing:.12em;color:#B7A680;text-transform:uppercase">{n}</div></div>')
html = ('<html><body style="margin:0;background:#11191E;padding:20px;width:1460px">'
        '<div style="display:flex;flex-wrap:wrap;gap:22px 18px">' + "".join(cells) + '</div></body></html>')
open(BUILD + "icon_sheet.html", "w").write(html)
with sync_playwright() as p:
    b = p.chromium.launch(**CHROMIUM)
    pg = b.new_page(viewport={"width": 1500, "height": 400}, device_scale_factor=1)
    pg.goto("file://" + BUILD + "icon_sheet.html")
    pg.wait_for_timeout(300)
    pg.screenshot(path=BUILD + "icon_sheet.png", full_page=True)
    b.close()
print("icon sheet written")
