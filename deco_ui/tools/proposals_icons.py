"""Proposals: the game's icons redrawn in the Deco UI's style, as close to the game's as the style allows (2026-10-18, the
author: "For things like those icons there, the resource icons, icons on the production screen, etc. I'd like you to
make an attempt at recreating them as close as possible, but in the Deco aesthetic"). NOT in the mod (no icon of the
game's changes without the author's yes on the drawn icon): written to art/proposals/icons/ as PNGs at the game's sizes
and frames, and build/proposals_icons.png beside the game's (which holds the game's art, so stays in build/).

    CHROMIUM_PATH=/opt/pw-browsers/chromium python proposals_icons.py

Each keeps the game's subject, outline and colour cue (the oil black, the factories green, the dockyards blue, the
decisions' envelopes) and draws it flat, as the Deco UI's pictures are: an even fill, a gilt outline, a gilt highlight
line, no texture. The icons:
  resources_strip.dds        7 x 27 x 27  oil, aluminium, rubber, tungsten, steel, chromium, and the 7th (a dark lump)
  focusview/filter/pol_power_icon, research_icon, industry_icon   27 x 27  the focus tree's filters (the bubbles)
  military_factory_icon (27 x 23), dockyard_icon and dockyard_icon_with_wrench (29 x 21), efficiency_icon and
  efficiency_cap_icon (24 x 21), factory_bombing_defence_icon (29 x 29)   the production screen
  add_prod_inf_art_line, _armour_line, _aircraft_line, _naval_line   3 x 81 x 41  its add-a-line buttons (normal, hover,
                                                                      unavailable), modern kit (Valsora is 2036)
  decisionview/decision_select_icon_strip.dds   4 x 40 x 28  the decisions' envelopes (can't take, take, under way, timed)
Redrawn 2026-10-19 (the author: "by and large I like them, but the efficiency, dockyard, and production icons aren't
great ... the shield on bombing defense could be better as well"; by production they meant the add-a-line buttons): the
dockyard a gantry crane over a ship (the wrench an open-ended one across it), efficiency the game's zigzag
over gilt bars rising to it, the bombing defence a heater shield in two-tone steel with a ridge.
"""
import os

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

from paths import ART, BUILD, CHROMIUM, VANILLA

OUT = ART + "proposals/icons/"
GI = "gfx/interface/"
GOLD, LIT, RULE = "#E3C77E", "#F1DC9C", "#C9A55A"
DEFS = ('<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F6E3A6"/>'
        '<stop offset="1" stop-color="#9A7634"/></linearGradient>'
        '<linearGradient id="steel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6E8FB0"/>'
        '<stop offset="1" stop-color="#2E4A66"/></linearGradient>'
        '<linearGradient id="jade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4FA884"/>'
        '<stop offset="1" stop-color="#22604C"/></linearGradient>'
        '<linearGradient id="silver" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#C9D1D4"/>'
        '<stop offset="1" stop-color="#6E7A80"/></linearGradient>'
        '<linearGradient id="bar" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E8CD84"/>'
        '<stop offset="1" stop-color="#6B4A1C"/></linearGradient>'
        '<radialGradient id="chrome" cx=".38" cy=".35" r=".7"><stop offset="0" stop-color="#9CC6C2"/>'
        '<stop offset=".6" stop-color="#3D6E6C"/><stop offset="1" stop-color="#1B3433"/></radialGradient></defs>')
O = 'stroke="url(#g)" stroke-width="1.2" stroke-linejoin="round"'      # the gilt outline


def svg(w, h, body):
    return f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="position:absolute;left:0;top:0">{DEFS}{body}</svg>'


def at(x, body):
    return f'<g transform="translate({x},0)">{body}</g>'


# ------------------------------------------------------------------ the resources (27 x 27 each)
OIL = (f'<path d="M13.5,3.5C10,9 7,12.5 7,16.5a6.5,6.5 0 0 0 13,0C20,12.5 17,9 13.5,3.5Z" fill="#0D1316" {O}/>'
       f'<path d="M10.4,15.5a3.2,3.2 0 0 0 2,3.6" fill="none" stroke="{LIT}" stroke-width="1.1" stroke-linecap="round"/>')
ALUMINIUM = "".join(f'<path d="M4,{10 + 4 * i}L15,{6 + 4 * i}L23,{9 + 4 * i}L12,{13 + 4 * i}Z" fill="url(#silver)" {O}/>'
                    for i in (2, 1, 0))
RUBBER = (f'<circle cx="13.5" cy="13.5" r="10" fill="#14191B" {O}/>'
          f'<circle cx="13.5" cy="13.5" r="4.6" fill="#0A0E10" stroke="{RULE}" stroke-width="1"/>'
          + "".join(f'<path d="M13.5,13.5m0,-9.6v2.4" stroke="{RULE}" stroke-width="1.2" transform="rotate({a} 13.5 13.5)"/>'
                    for a in range(0, 360, 30)))
TUNGSTEN = (f'<path d="M13.5,3.5L22,20.5Q13.5,24.5 5,20.5Z" fill="url(#silver)" {O}/>'
            f'<path d="M13.5,6L9.5,19.5" stroke="{LIT}" stroke-width="1" opacity=".8"/>')
STEEL = (f'<path d="M7,9H20L24,19H3Z" fill="url(#steel)" {O}/>'
         f'<path d="M7,9L3,19M20,9L24,19" fill="none" stroke="{RULE}" stroke-width="1"/>'
         f'<path d="M8.5,11H18.5" stroke="{LIT}" stroke-width="1" opacity=".8"/>')
CHROMIUM_ORE = (f'<circle cx="13.5" cy="13.5" r="9.5" fill="url(#chrome)" {O}/>'
            f'<path d="M8.5,10.5a6,6 0 0 1 4.5,-3.5" fill="none" stroke="{LIT}" stroke-width="1.2" stroke-linecap="round"/>')
LUMP = (f'<path d="M9,5L17,4L22,9L21,19L15,24L8,22L5,14Z" fill="#1A1714" {O}/>'
        f'<path d="M9.5,8L16,7M8,13L12,11" stroke="{RULE}" stroke-width="1" opacity=".7"/>')
RESOURCES = [OIL, ALUMINIUM, RUBBER, TUNGSTEN, STEEL, CHROMIUM_ORE, LUMP]

# ------------------------------------------------------------------ the focus filters (27 x 27)
TEMPLE = (f'<path d="M3.5,10L13.5,4L23.5,10Z" fill="#7A6440" {O}/>'
          + "".join(f'<rect x="{6 + 4.2 * i}" y="11.5" width="2.2" height="9" fill="#9C8456" stroke="url(#g)" stroke-width=".8"/>'
                    for i in range(4))
          + f'<path d="M4,21.5H23V24H4Z" fill="#7A6440" {O}/>')
FLASK = (f'<path d="M10.5,3.5H16.5M11.5,3.5V10L5.5,21.5Q5,23.5 7,23.5H20Q22,23.5 21.5,21.5L15.5,10V3.5" fill="#0F171B" {O}/>'
         f'<path d="M8.6,16.5H18.4L21,21.6Q21.3,22.8 20,22.8H7Q5.7,22.8 6,21.6Z" fill="url(#jade)"/>')
WORKS = (f'<path d="M3.5,23.5V12L9,15V12L14.5,15V12L20,15V6H23.5V23.5Z" fill="#7A3A2E" {O}/>'
         f'<path d="M5,21H22" stroke="url(#jade)" stroke-width="2.4"/>'
         f'<path d="M5.5,17.5H8.5M11,17.5H14M16.5,17.5H19.5" stroke="{LIT}" stroke-width="1"/>')

# ------------------------------------------------------------------ the production screen
# the factory as the civilian one's (the WORKS filter): the author, 2026-10-19: "The military factory icon was okay, it
# matching the civilian factory icon is good"
MIL_FACTORY = (f'<path d="M2.5,21.5V11L8,14V11L13.5,14V11L19,14V3H21.5V7H24V21.5Z" fill="url(#jade)" {O}/>'
               f'<path d="M4.5,18H22" stroke="{LIT}" stroke-width="1" opacity=".7"/>')


def outlined(d, colour, width, dark=1.6):
    """a stroke with a dark rim under it, so a thin line reads on any fill"""
    return (f'<path d="{d}" fill="none" stroke="#0B1014" stroke-width="{width + dark}" stroke-linecap="round" '
            f'stroke-linejoin="round"/><path d="{d}" fill="none" stroke="{colour}" stroke-width="{width}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


def dockyard(wrench=False):
    """a gantry crane over a ship on its slipway (the game's: a crane and a shed)"""
    body = (f'<path d="M4.5,19.5L6.5,6.5M11.5,19.5L9.5,6.5M5.5,13H10.5M5,16.5L10.7,9.5M6,9.5L11,16.5" '
            f'fill="none" stroke="url(#steel)" stroke-width="1.3"/>'
            f'<path d="M2.5,3.5H23.5V6.5H2.5Z" fill="url(#steel)" {O}/>'
            f'<path d="M20.5,6.5V10.5" stroke="{GOLD}" stroke-width="1"/><path d="M19,10.5H22" stroke="{GOLD}" stroke-width="1.2"/>'
            f'<path d="M14.5,14.5H27.5L25,19.5H16.5Z" fill="url(#steel)" {O}/>'
            f'<path d="M18,14.5V11.5H22V14.5" fill="url(#steel)" {O}/>'
            f'<path d="M1.5,20H27.5" stroke="{GOLD}" stroke-width="1.2"/>')
    if wrench:
        body += (outlined("M8,18L17.5,8.5", "#C9D1D4", 2.4)
                 + '<circle cx="19.5" cy="6.5" r="4" fill="#C9D1D4" stroke="#0B1014" stroke-width="1"/>'
                 + '<path d="M19.5,6.5L23.5,2.5L25,4L21,8Z" fill="#0B1014"/>'
                 + '<path d="M17,5.2Q18,3.6 19.8,3.4" fill="none" stroke="#FFFFFF" stroke-width=".8" opacity=".7"/>')
    return body


# the zigzag over its bars, as the game's: gilt bars rising from the floor to under the line
ZIG = [(2, 10), (7, 5.5), (12, 11.5), (18.5, 4)]


def zig_y(x):
    for (x0, y0), (x1, y1) in zip(ZIG, ZIG[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return ZIG[-1][1]


def efficiency(cap=False):
    bars = "".join(f'<rect x="{x}" y="{zig_y(x + 1.3) + 3:.1f}" width="2.6" height="{17.5 - zig_y(x + 1.3):.1f}" '
                   f'fill="url(#bar)" stroke="#0B1014" stroke-width=".6"/>' for x in (2.5, 6.8, 11.1, 15.4, 19.7))
    line = "M" + " L".join(f"{x},{y}" for x, y in ZIG)
    if cap:
        return (bars + outlined("M1.5,3H22.5", "#EE8C7E", 1.6) + outlined(line, "#EE8C7E", 1.8))
    return (bars + outlined(line + " L20.5,2", LIT, 1.8)
            + '<path d="M17,1.2L22.8,0.8L22.4,6.6Z" fill="#F1DC9C" stroke="#0B1014" stroke-width=".8" stroke-linejoin="round"/>')


# a heater shield, two-tone steel with a ridge and a gilt rim, before the factory (the game's: a brick works and a
# steel shield)
SHIELD = "M13.5,10.5Q20.5,8.6 27.5,10.5V17Q27.5,24.5 20.5,28Q13.5,24.5 13.5,17Z"
BOMB_DEFENCE = (f'<path d="M1.5,25.5V14L6,11V14L10.5,11V14L12,13V4.5H14.5V12.5L17,13.5V25.5Z" fill="#7A3A2E" {O}/>'
                + "".join(f'<rect x="{3.5 + 3.5 * i}" y="18" width="1.8" height="2.4" fill="#2A1410"/>' for i in range(3))
                + f'<path d="{SHIELD}" fill="#0B1014" stroke="#0B1014" stroke-width="2.4"/>'
                f'<clipPath id="sh"><path d="{SHIELD}"/></clipPath>'
                f'<g clip-path="url(#sh)"><rect x="12" y="8" width="8.5" height="21" fill="#D9DFE2"/>'
                f'<rect x="20.5" y="8" width="8" height="21" fill="#7E8A90"/>'
                f'<path d="M15.5,12.2Q20.5,11 25.5,12.2V17Q25.5,23 20.5,25.6Q15.5,23 15.5,17Z" fill="none" '
                f'stroke="rgba(11,16,20,.35)" stroke-width=".8"/></g>'
                f'<path d="M20.5,9.6V27.5" stroke="{RULE}" stroke-width="1"/>'
                f'<path d="{SHIELD}" fill="none" stroke="url(#g)" stroke-width="1.3" stroke-linejoin="round"/>')

# ------------------------------------------------------------------ the add-a-line buttons (3 frames of 81 x 41)
# a high-cut combat helmet over an assault rifle (the game's: a WWII helmet and a field gun)
HELMET_GUN = (f'<path d="M10.5,17.5Q10.5,6.5 21,6.5Q31.5,6.5 31.5,17.5H28Q27.5,14.5 25,14.5L24.5,17.5Z" fill="url(#jade)" {O}/>'
              f'<path d="M15,10Q18,8.4 21,8.4" fill="none" stroke="{LIT}" stroke-width="1" opacity=".7"/>'
              f'<path d="M5.5,25L12.5,24V29L7.5,31.5Z" fill="url(#jade)" {O}/>'
              f'<path d="M12.5,23.5H33V28H12.5Z" fill="url(#jade)" {O}/>'
              f'<path d="M33,24.5H43V27.5H33Z" fill="#14201C" {O}/>'
              f'<path d="M23,28H26.5Q27.5,32 29.5,35H26Q24,32 23,28Z" fill="url(#jade)" {O}/>'
              f'<path d="M17,23.5V21.2H24V23.5" fill="none" stroke="{GOLD}" stroke-width="1.1"/>'
              f'<path d="M43,26H55" stroke="{GOLD}" stroke-width="1.5"/>'
              f'<path d="M15,25.5H31" stroke="{LIT}" stroke-width=".8" opacity=".6"/>')
# a modern main battle tank, side on: the angular turret, the long gun, six road wheels under a skirt
TANK = (f'<path d="M7,28.5H45Q47,31.5 44,34.5H9Q5.5,31.5 7,28.5Z" fill="#14201C" {O}/>'
        + "".join(f'<circle cx="{11.5 + 6.4 * i}" cy="31.5" r="2.2" fill="url(#jade)" stroke="url(#g)" stroke-width=".7"/>'
                  for i in range(6))
        + f'<path d="M4.5,28.5L8,23.5H44L48,28.5Z" fill="url(#jade)" {O}/>'
        f'<path d="M14.5,23.5L17.5,17.5H33L38,20.5V23.5Z" fill="url(#jade)" {O}/>'
        f'<path d="M22,17.5V15.5H27V17.5" fill="url(#jade)" stroke="url(#g)" stroke-width="1"/>'
        f'<path d="M37,19.5H57" stroke="{GOLD}" stroke-width="1.8"/><path d="M53,18.3V20.7" stroke="{GOLD}" stroke-width="2.4"/>'
        f'<path d="M9,26H43" stroke="{LIT}" stroke-width=".8" opacity=".6"/>')
JET = (f'<path d="M30,6L33,16L52,27V30L33,26L32,32L37,35V37L30,35L23,37V35L28,32L27,26L8,30V27L27,16Z" '
       f'fill="url(#jade)" {O}/>')
ANCHOR = (f'<circle cx="30" cy="8" r="3" fill="none" stroke="url(#steel)" stroke-width="2"/>'
          f'<path d="M30,11V35M22,16H38M14,26Q16,35 30,35Q44,35 46,26" fill="none" stroke="url(#steel)" stroke-width="2.6" stroke-linecap="round"/>'
          f'<path d="M12,28L14,24L17,28M48,28L46,24L43,28" fill="none" stroke="url(#steel)" stroke-width="2"/>')


def line_button(art, state):
    w, h = 81, 41
    fill = {"normal": "#141E24", "hover": "#1C3A33", "off": "#101418"}[state]
    rim = {"normal": "url(#g)", "hover": "url(#g)", "off": "rgba(201,165,90,.45)"}[state]
    plate = (f'<path d="M5.5,.5H75.5L80.5,5.5V35.5L75.5,40.5H5.5L.5,35.5V5.5Z" fill="{fill}" stroke="{rim}"/>'
             f'<path d="M7,3.5H74" stroke="rgba(241,220,156,{.35 if state == "hover" else .18})"/>')
    plus = f'<path d="M66,7V21M59,14H73" stroke="{GOLD if state != "off" else "#7E8890"}" stroke-width="2.6"/>'
    a = art if state != "off" else f'<g opacity=".45" style="filter:grayscale(1)">{art}</g>'
    ban = ('<circle cx="40" cy="22" r="11" fill="none" stroke="#EE8C7E" stroke-width="2.4"/>'
           '<path d="M32.5,29.5L47.5,14.5" stroke="#EE8C7E" stroke-width="2.4"/>') if state == "off" else ""
    return plate + f'<g transform="translate(4,1)">{a}</g>' + plus + ban


# ------------------------------------------------------------------ the decisions' envelopes (4 frames of 40 x 28)
def envelope(kind):
    fill = {"no": "#4A5358", "take": "#E8DFC8", "busy": "#C9B98F", "timed": "#C9B98F"}[kind]
    rim = "rgba(201,165,90,.55)" if kind == "no" else "url(#g)"
    flap = "#3A4146" if kind == "no" else "#B8A06A"
    e = (f'<path d="M3.5,8.5H30.5V24.5H3.5Z" fill="{fill}" stroke="{rim}" stroke-width="1.2"/>'
         f'<path d="M3.5,8.5L17,18L30.5,8.5" fill="{flap}" stroke="{rim}" stroke-width="1.2"/>')
    if kind in ("no", "take"):
        col = "#7E8890" if kind == "no" else "#3FA88E"
        e += f'<path d="M24,21.5l4,4 9,-10" fill="none" stroke="#0B1014" stroke-width="4" stroke-linecap="round"/>'
        e += f'<path d="M24,21.5l4,4 9,-10" fill="none" stroke="{col}" stroke-width="2.2" stroke-linecap="round"/>'
    elif kind == "busy":
        e += (f'<circle cx="24" cy="15" r="6" fill="#8E2A24" stroke="url(#g)" stroke-width="1"/>'
              f'<path d="M21.5,15H26.5M24,12.5V17.5" stroke="#F1DC9C" stroke-width="1"/>')
    else:
        e += (f'<circle cx="30" cy="16" r="7.5" fill="#11191E" stroke="url(#g)" stroke-width="1.4"/>'
              f'<path d="M30,11.5V16L33,18" fill="none" stroke="{LIT}" stroke-width="1.4"/>'
              f'<path d="M28.5,7H31.5M30,7V8.5" stroke="{GOLD}" stroke-width="1.4"/>')
    return e


ITEMS = [  # name, the game's path (under gfx/interface/), w, h, svg body
    ("resources_strip", "resources_strip.dds", 189, 27, "".join(at(27 * i, r) for i, r in enumerate(RESOURCES))),
    ("filter_pol_power", "focusview/filter/pol_power_icon.dds", 27, 27, TEMPLE),
    ("filter_research", "focusview/filter/research_icon.dds", 27, 27, FLASK),
    ("filter_industry", "focusview/filter/industry_icon.dds", 27, 27, WORKS),
    ("military_factory_icon", "military_factory_icon.dds", 27, 23, MIL_FACTORY),
    ("dockyard_icon", "dockyard_icon.dds", 29, 21, dockyard()),
    ("dockyard_icon_with_wrench", "dockyard_icon_with_wrench.dds", 29, 21, dockyard(True)),
    ("efficiency_icon", "efficiency_icon.dds", 24, 21, efficiency()),
    ("efficiency_cap_icon", "efficiency_cap_icon.dds", 24, 21, efficiency(True)),
    ("factory_bombing_defence_icon", "factory_bombing_defence_icon.dds", 29, 29, BOMB_DEFENCE),
    *[(f"add_prod_{k}_line", f"add_prod_{k}_line.dds", 243, 41,
       "".join(at(81 * i, line_button(art, s)) for i, s in enumerate(("normal", "hover", "off"))))
      for k, art in (("inf_art", HELMET_GUN), ("armour", TANK), ("aircraft", JET), ("naval", ANCHOR))],
    ("decision_select_icon_strip", "decisionview/decision_select_icon_strip.dds", 160, 28,
     "".join(at(40 * i, envelope(k)) for i, k in enumerate(("no", "take", "busy", "timed")))),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    body, y = [], 0
    for key, rel, w, h, art in ITEMS:
        body.append(f'<div id="{key}" style="position:absolute;left:0;top:{y}px;width:{w}px;height:{h}px">{svg(w, h, art)}</div>')
        y += h + 10
    page = f"<html><body style='margin:0;background:transparent;width:400px;height:{y}px'>{''.join(body)}</body></html>"
    open(BUILD + "proposals_icons.html", "w").write(page)
    with sync_playwright() as p:
        b = p.chromium.launch(**CHROMIUM)
        pg = b.new_page(viewport={"width": 400, "height": 800}, device_scale_factor=1)
        pg.goto("file://" + BUILD + "proposals_icons.html")
        pg.wait_for_timeout(300)
        for key, rel, w, h, art in ITEMS:
            pg.query_selector("#" + key).screenshot(path=OUT + key + ".png", omit_background=True)
            assert Image.open(OUT + key + ".png").size == (w, h), key
        b.close()
    # the comparison sheet: the game's and ours, at 1x on the panels' lacquer and enlarged 3x
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
    rows = [(key, rel, Image.open(VANILLA + GI + rel).convert("RGBA"), Image.open(OUT + key + ".png").convert("RGBA"))
            for key, rel, w, h, art in ITEMS]
    W = 40 + max(g.width for _, _, g, _ in rows) * 8 + 60
    H = sum(g.height * 3 + 40 for _, _, g, _ in rows) + 20
    cv = Image.new("RGBA", (W, H), (17, 25, 30, 255))
    d = ImageDraw.Draw(cv)
    y = 10
    for key, rel, g, n in rows:
        d.text((10, y), f"{rel}: the game's | the proposal (1x, then 3x)", font=font, fill=(232, 223, 200))
        y += 18
        x = 10
        for im in (g, n):
            cv.alpha_composite(im, (x, y))
            x += im.width + 12
        for im in (g, n):
            big = im.resize((im.width * 3, im.height * 3), Image.NEAREST)
            cv.alpha_composite(big, (x, y))
            x += big.width + 12
        y += g.height * 3 + 22
    cv = cv.crop((0, 0, W, y))
    cv.convert("RGB").save(BUILD + "proposals_icons.png")
    print(len(ITEMS), "icon proposals in", OUT, "| beside the game's: build/proposals_icons.png")


if __name__ == "__main__":
    main()
