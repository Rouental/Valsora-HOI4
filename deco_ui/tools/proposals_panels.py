"""Proposals for the pictures inside the side panels (v0.7), for the user to approve. NOT in the mod: they are written
to art/proposals/panel_pictures/ as PNGs, never to valsora_deco_ui/ (the user, 2026-10-15: "do the panel pictures, but
don't put them in the mod yet. I'd like to see and approve them first").

    python proposals_panels.py      -> art/proposals/panel_pictures/*.png (our art only)
                                       build/proposals_panel_pictures.png (the game's picture beside each proposal;
                                       it holds the game's art, so it stays in build/, which git ignores)

Each proposal keeps its picture's size, frames and layout zones (the slots the game writes into, the dark side where
its text goes), so it can later go in as a texture at the game's path, like the rest of the Deco UI:
  research_top_win.dds       548 x 138  the research panel's header: a 1930s laboratory photograph
  production_win_top.dds     550 x 253  the production panel's header: riveted steel, its factory slots
  international_market/market_ui.dds  540 x 140  the market's header: a photograph of rows of trucks
  overview_top_strip.dds     1566 x 59  the army / navy / air overviews' header strips (3 frames): photographs
  operatives/create agency_bg.dds  508 x 99  the intelligence agency's plate
  officer_corp/spirit_banner_decoration_{army,navy,air}.dds  460 x 66  the officer corps' ornaments (tanks, ships, planes)
To put them in: move each into gen_textures.py at the game's path (and validate_preview.SAME_SIZE), as the army bar's.
"""
import os

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

from icons import icon
from paths import ART, BUILD, CHROMIUM, FONTS_SRC, VANILLA

OUT = ART + "proposals/panel_pictures/"
os.makedirs(OUT, exist_ok=True)
GOLD = "#E3C77E"
CSS = """*{box-sizing:border-box;margin:0;padding:0}body{background:transparent}
.s{position:absolute;overflow:hidden}
.lac{background:repeating-linear-gradient(90deg,rgba(255,255,255,.028) 0 1px,transparent 1px 8px),#11191E}
.ck{position:absolute;width:12px;height:12px}
.ck:before{content:"";position:absolute;inset:0;border-top:1.5px solid #E3C77E;border-left:1.5px solid #E3C77E}
.ck:after{content:"";position:absolute;left:4px;top:4px;width:4px;height:4px;border-top:1.5px solid #E3C77E;border-left:1.5px solid #E3C77E}
.tl{left:4px;top:4px}.tr{right:4px;top:4px;transform:scaleX(-1)}.bl{left:4px;bottom:4px;transform:scaleY(-1)}.br{right:4px;bottom:4px;transform:scale(-1,-1)}
"""


def frame(w, h, inset=0):
    """the panels' lacquer plate: a gilt rim and an inner hairline"""
    return (f'<div class="lac" style="position:absolute;inset:{inset}px"></div>'
            f'<div style="position:absolute;inset:{inset}px;box-shadow:inset 0 0 0 1px #C9A55A"></div>'
            f'<div style="position:absolute;inset:{inset + 4}px;box-shadow:inset 0 0 0 1px rgba(201,165,90,.3)"></div>')


def well(x, y, w, h, fill="#0A0F12"):
    return (f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{fill};'
            'box-shadow:inset 0 0 0 1px rgba(201,165,90,.45)"></div>')


def sunburst(cx, cy, r, alpha=.3, step=9):
    return (f'<div style="position:absolute;left:{cx - r}px;top:{cy - r}px;width:{2 * r}px;height:{2 * r}px;border-radius:50%;'
            f'background:repeating-conic-gradient(rgba(227,199,126,{alpha}) 0deg 1.6deg,transparent 1.6deg {step}deg);'
            '-webkit-mask:radial-gradient(circle,#000 0 30%,transparent 72%)"></div>')


def svg(w, h, body):
    return f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="position:absolute;left:0;top:0">{body}</svg>'


def fade_right(x0, x1):
    """the dark side the game's text sits on, as the photographs fade into"""
    return (f'<div style="position:absolute;left:{x0}px;top:0;bottom:0;width:{x1 - x0}px;'
            'background:linear-gradient(90deg,transparent,#0D1418 70%)"></div>')


# ------------------------------------------------------------------ research: an atom in a sunburst, circuit lines
def research():
    """v0.11 (the author: "I like the art for the science bar mockup, but it should be better centered and aligned to
    the box it's in"): the game shows the picture's first VIS px (the panel's edge hides the rest), so the box and the
    strip under it have M px of margin each side of that; the atom and its circuits are centred in the box"""
    w, h, VIS, M = 548, 138, 538, 12
    bw = VIS - 2 * M
    cx, cy = M + bw / 2 - 118, 45            # the atom: the composition (the atom's 40 px, the circuits to +236) centred
    ox = cx - 92                             # the drawing below was made for an atom at x 92
    pic = (sunburst(cx - M, cy, 80, .32)
           + svg(bw, 90, f'<g transform="translate({ox - M},{cy - 57})">'
                 '<g fill="none" stroke="#E3C77E" stroke-width="1.3" opacity=".9">'
                 '<ellipse cx="92" cy="57" rx="40" ry="13"/>'
                 '<ellipse cx="92" cy="57" rx="40" ry="13" transform="rotate(60 92 57)"/>'
                 '<ellipse cx="92" cy="57" rx="40" ry="13" transform="rotate(-60 92 57)"/></g>'
                 '<circle cx="92" cy="57" r="5" fill="#F1DC9C"/>'
                 '<g fill="none" stroke="rgba(227,199,126,.55)" stroke-width="1">'
                 + "".join(f'<path d="M140,{y}H{250 + k * 18}l8,{s * 8}H{330 + k * 12}"/>'
                           f'<circle cx="{330 + k * 12}" cy="{y + s * 8}" r="2" fill="rgba(227,199,126,.7)" stroke="none"/>'
                           for k, (y, s) in enumerate(((30, 1), (44, -1), (70, 1), (84, -1))))
                 + '</g><g fill="none" stroke="rgba(227,199,126,.35)" stroke-width="1">'
                 + "".join(f'<path d="M{170 + i * 26},16V100"/>' for i in range(5)) + "</g></g>"))
    return (frame(w, h)
            + f'<div style="position:absolute;left:{M}px;top:12px;width:{bw}px;height:90px;overflow:hidden;'
              f'background:radial-gradient(ellipse at 50% 50%,#1C2B30,#0D1418 65%)">{pic}</div>'
            + f'<div style="position:absolute;left:{M}px;top:12px;width:{bw}px;height:90px;box-shadow:inset 0 0 0 1px #C9A55A"></div>'
            + f'<div style="position:absolute;left:{M}px;top:104px;width:{bw}px;height:30px;background:linear-gradient(180deg,#1A252C,#0E1519);'
              'box-shadow:inset 0 1px 0 #C9A55A"></div>'
            + '<div style="position:absolute;left:30px;top:106px;width:1px;height:26px;background:rgba(201,165,90,.5)"></div>'
            + '<div style="position:absolute;left:404px;top:106px;width:1px;height:26px;background:rgba(201,165,90,.5)"></div>')


# ------------------------------------------------------------------ production: the header's structure in lacquer
def production():
    w, h = 550, 253
    s = frame(w, h)
    s += ('<div style="position:absolute;left:59px;top:15px;width:422px;height:31px;background:linear-gradient(180deg,#1A252C,#0E1519);'
          'box-shadow:inset 0 0 0 1px rgba(201,165,90,.6)"></div>')
    s += "".join(well(x, 18, 71, 25) for x in (60, 202, 342))
    for cx in (35, 505):          # cog medallions in place of the crossed hammers
        s += sunburst(cx, 30, 22, .35, 12)
        s += (f'<div style="position:absolute;left:{cx - 13}px;top:17px;width:26px;height:26px;border-radius:50%;background:#11191E;'
              f'box-shadow:0 0 0 1px #C9A55A"></div><div style="position:absolute;left:{cx - 9}px;top:21px">{icon("factory", 18, GOLD, 1.4)}</div>')
    s += ('<div style="position:absolute;left:14px;top:52px;width:522px;height:30px;background:linear-gradient(180deg,#17222A,#0E1519);'
          'box-shadow:inset 0 1px 0 rgba(201,165,90,.6),inset 0 -1px 0 rgba(201,165,90,.25)"></div>')
    for x0, x1 in ((14, 272), (274, 536)):
        s += (f'<div style="position:absolute;left:{x0}px;top:86px;width:{x1 - x0}px;height:90px;'
              'background:radial-gradient(ellipse at 50% 50%,rgba(46,110,96,.10),transparent 70%);box-shadow:inset 0 0 0 1px rgba(201,165,90,.3)"></div>'
              f'<i class="ck tl" style="left:{x0 + 4}px;top:90px"></i><i class="ck tr" style="left:{x1 - 16}px;top:90px"></i>')
    for (x0, x1), tint, ic in (((15, 270), "rgba(46,110,96,.30)", "factory"), ((272, 535), "rgba(139,106,44,.30)", "navy")):
        s += (f'<div style="position:absolute;left:{x0}px;top:178px;width:{x1 - x0}px;height:31px;'
              'background:linear-gradient(180deg,#1A252C,#111A1F);box-shadow:inset 0 0 0 1px rgba(201,165,90,.45)"></div>'
              f'<div style="position:absolute;left:{x0}px;top:211px;width:{x1 - x0}px;height:33px;background:{tint};'
              'box-shadow:inset 0 0 0 1px rgba(201,165,90,.45)"></div>')
    for x in (36, 121, 206, 291, 376, 461):
        ic = "factory" if x < 272 else "navy"
        s += well(x, 183, 59, 24) + f'<div style="position:absolute;left:{x + 22}px;top:187px">{icon(ic, 16, GOLD, 1.4)}</div>'
        s += well(x, 215, 59, 25)
    return s


# ------------------------------------------------------------------ the market: a globe's meridians, routes, a ship
def market():
    w, h = 540, 140
    globe = ('<g fill="none" stroke="rgba(227,199,126,.55)" stroke-width="1">'
             '<circle cx="110" cy="70" r="52"/>'
             + "".join(f'<ellipse cx="110" cy="70" rx="{r}" ry="52"/>' for r in (14, 30, 44))
             + "".join(f'<path d="M{110 - (52 ** 2 - (y - 70) ** 2) ** .5:.1f},{y}H{110 + (52 ** 2 - (y - 70) ** 2) ** .5:.1f}"/>'
                       for y in (38, 54, 70, 86, 102)) + "</g>")
    routes = ('<g fill="none" stroke="#E3C77E" stroke-width="1.2" stroke-dasharray="4 4" opacity=".8">'
              '<path d="M150,46 Q240,10 330,40"/><path d="M158,92 Q260,124 360,90"/><path d="M162,70 Q250,60 345,66"/></g>'
              + "".join(f'<circle cx="{x}" cy="{y}" r="3" fill="#F1DC9C"/>' for x, y in ((330, 40), (360, 90), (345, 66))))
    ship = f'<div style="position:absolute;left:372px;top:46px;opacity:.85">{icon("convoy", 46, GOLD, 1.2)}</div>'
    return (frame(w, h)
            + f'<div style="position:absolute;left:8px;top:8px;width:524px;height:124px;overflow:hidden;'
              f'background:radial-gradient(ellipse at 22% 50%,#1C2B30,#0D1418 65%)">'
              + sunburst(110 - 8, 70 - 8, 90, .22) + svg(524, 124, '<g transform="translate(-8,-8)">' + globe + routes + "</g>")
              + ship + "</div>"
            + '<div style="position:absolute;left:8px;top:8px;width:524px;height:124px;box-shadow:inset 0 0 0 1px #C9A55A"></div>')


# ------------------------------------------------------------------ the overviews' strips: army, navy, air
FRIGATE = ('<path d="M6,30 L14,36 H98 L106,28 H84 L80,22 H70 L68,14 H64 L62,22 H50 L48,18 H40 L38,24 H24 L22,28 Z" '
           'fill="none" stroke="#E3C77E" stroke-width="1.3" stroke-linejoin="round"/><path d="M66,14V6M60,9h12" '
           'stroke="#E3C77E" stroke-width="1.1"/>')


def strip(kind):
    w, h = 522, 59
    art = {"army": f'<div style="position:absolute;left:58px;top:7px">{icon("army", 44, GOLD, 1.2)}</div>'
                   + svg(220, 59, '<g stroke="rgba(227,199,126,.6)" stroke-width="1.2" fill="none">'
                          '<path d="M118,20l8,6-8,6M128,20l8,6-8,6M138,20l8,6-8,6"/></g>'),
           "navy": svg(220, 59, f'<g transform="translate(40,8)">{FRIGATE}</g><g fill="none" stroke="rgba(227,199,126,.45)" '
                                'stroke-width="1"><path d="M30,48q10,-4 20,0t20,0t20,0t20,0t20,0"/><path d="M40,54q10,-4 20,0t20,0t20,0t20,0"/></g>'),
           "air": f'<div style="position:absolute;left:70px;top:6px;transform:rotate(90deg)">{icon("air", 44, GOLD, 1.2)}</div>'
                  + svg(220, 59, '<g stroke="rgba(227,199,126,.45)" stroke-width="1"><path d="M20,24H68M30,30H66M14,36H68"/></g>')}[kind]
    return (frame(w, h)
            + f'<div style="position:absolute;left:5px;top:5px;width:512px;height:49px;overflow:hidden;'
              f'background:radial-gradient(ellipse at 18% 50%,#1C2B30,#0D1418 60%)">' + sunburst(90, 24, 70, .26) + art
            + fade_right(190, 512) + "</div>")


def strips():
    return "".join(f'<div style="position:absolute;left:{i * 522}px;top:0;width:522px;height:59px">{strip(k)}</div>'
                   for i, k in enumerate(("army", "navy", "air")))


# ------------------------------------------------------------------ the intelligence agency's plate
def agency():
    w, h = 508, 99
    return (f'<div style="position:absolute;left:3px;top:3px;width:{w - 6}px;height:{h - 6}px;'
            'clip-path:polygon(18px 0,calc(100% - 18px) 0,100% 18px,100% calc(100% - 18px),calc(100% - 18px) 100%,18px 100%,0 calc(100% - 18px),0 18px);'
            'background:repeating-linear-gradient(90deg,rgba(255,255,255,.025) 0 1px,transparent 1px 8px),'
            'radial-gradient(ellipse at 62% 50%,#3A2848,#1A1222 70%)"></div>'
            + svg(w, h, '<path d="M21,3.5H487L504.5,21V78L487,95.5H21L3.5,78V21Z" fill="none" stroke="#C9A55A"/>'
                        '<path d="M23,8H485L500,23V76L485,91H23L8,76V23Z" fill="none" stroke="rgba(201,165,90,.35)"/>')
            + sunburst(314, 49, 44, .35)
            + f'<div style="position:absolute;left:290px;top:25px">{icon("intel", 48, "#F1DC9C", 1.3)}</div>')


# ------------------------------------------------------------------ the officer corps' ornaments: gilt wings round the middle
def banner(kind):
    w, h = 460, 66
    lines = "".join(f'<path d="M{224 - i * 2},{33 - 3 * i}H{110 + i * 9}M{235 + i * 2},{33 - 3 * i}H{350 - i * 9}'
                    f'M{224 - i * 2},{33 + 3 * i}H{110 + i * 9}M{235 + i * 2},{33 + 3 * i}H{350 - i * 9}"/>' for i in range(0, 7))
    ic = {"army": "army", "navy": "navy", "air": "air"}[kind]
    medal = "".join(f'<div style="position:absolute;left:{x - 14}px;top:19px;width:28px;height:28px;transform:rotate(45deg);'
                    'background:#11191E;box-shadow:0 0 0 1px #C9A55A"></div>'
                    f'<div style="position:absolute;left:{x - 9}px;top:24px">{icon(ic, 18, GOLD, 1.4)}</div>' for x in (92, 368))
    return svg(w, h, f'<g stroke="rgba(227,199,126,.65)" stroke-width="1.1" fill="none">{lines}</g>') + medal


ITEMS = [  # out name, the game's path, w, h, html
    ("research_top_win", "gfx/interface/research_top_win.dds", 548, 138, research()),
    ("production_win_top", "gfx/interface/production_win_top.dds", 550, 253, production()),
    ("market_ui", "gfx/interface/international_market/market_ui.dds", 540, 140, market()),
    ("overview_top_strip", "gfx/interface/overview_top_strip.dds", 1566, 59, strips()),
    ("create_agency_bg", "gfx/interface/operatives/create agency_bg.dds", 508, 99, agency()),
    *[(f"spirit_banner_decoration_{k}", f"gfx/interface/officer_corp/spirit_banner_decoration_{k}.dds", 460, 66, banner(k))
      for k in ("army", "navy", "air")]]


def main():
    G = FONTS_SRC
    fonts = f"@font-face{{font-family:'Federo';src:url('file://{G}federo/Federo-Regular.ttf')}}"
    body, y = [], 0
    for key, rel, w, h, html in ITEMS:
        body.append(f'<div class="s" id="{key}" style="left:0;top:{y}px;width:{w}px;height:{h}px">{html}</div>')
        y += h + 10
    page = f"<html><head><style>{fonts}{CSS}</style></head><body style='width:1700px;height:{y}px'>{''.join(body)}</body></html>"
    open(BUILD + "proposals_panels.html", "w").write(page)
    with sync_playwright() as p:
        b = p.chromium.launch(**CHROMIUM)
        pg = b.new_page(viewport={"width": 1700, "height": 1200}, device_scale_factor=1)
        pg.goto("file://" + BUILD + "proposals_panels.html")
        pg.wait_for_timeout(500)
        for key, rel, w, h, html in ITEMS:
            pg.query_selector("#" + key).screenshot(path=OUT + key + ".png", omit_background=True)
            assert Image.open(OUT + key + ".png").size == (w, h), key
        b.close()
    # the comparison sheet (the game's art beside ours: build/, never committed)
    rows = []
    for key, rel, w, h, html in ITEMS:
        van = Image.open(VANILLA + rel).convert("RGBA")
        new = Image.open(OUT + key + ".png").convert("RGBA")
        if w > 1000:                                   # the strips: one frame above the other
            van = Image.fromarray(__import__("numpy").vstack([__import__("numpy").asarray(van.crop((i * 522, 0, i * 522 + 522, h))) for i in range(3)]))
            new = Image.fromarray(__import__("numpy").vstack([__import__("numpy").asarray(new.crop((i * 522, 0, i * 522 + 522, h))) for i in range(3)]))
        rows.append((key, rel, van, new))
    pad, lab = 20, 24
    W = pad * 3 + max(r[2].width for r in rows) * 2
    H = sum(max(r[2].height, r[3].height) + lab + pad for r in rows) + pad
    cv = Image.new("RGBA", (W, H), (40, 46, 50, 255))
    d = ImageDraw.Draw(cv)
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    y = pad
    colw = max(r[2].width for r in rows)
    for key, rel, van, new in rows:
        d.text((pad, y), f"{rel}  -  the game's", font=f, fill=(225, 225, 225))
        d.text((pad * 2 + colw, y), "proposal", font=f, fill=(241, 220, 156))
        cv.alpha_composite(van, (pad, y + lab))
        cv.alpha_composite(new, (pad * 2 + colw, y + lab))
        y += max(van.height, new.height) + lab + pad
    cv.convert("RGB").save(BUILD + "proposals_panel_pictures.png")
    print(len(ITEMS), "proposals written to", OUT, "| comparison: build/proposals_panel_pictures.png")


if __name__ == "__main__":
    main()
