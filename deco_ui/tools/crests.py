"""The crest on the event cards' top edge (v0.8.2), shared by gen_textures.py ('ev_top') and proposals_crests.py.

The user (2026-10-15): "The logo at the top of country / leader / long events doesn't read so well at this size. Maybe
go with a different design?" It was a half sunburst 56 px across (v0.7): at that size its 36 thin rays and the ring
inside them blur into a speckle. The designs here are drawn from a few bold shapes instead, in SVG so their edges stay
crisp; EV_CREST is the one in the mod, and proposals_crests.py shows them all (with the superevent's crests, whose
emblems are scripts/superevents_deco.py's) in art/proposals/crests/.

ev_crest(design, cx, base) gives the crest's HTML, centred on x = cx and standing on the card's top edge at y = base,
and how far either side of cx the card's top rail has to stop for it.
"""
import base64
import io

import numpy as np

DESIGNS = ("keystone", "globe", "fan", "diamond", "sunburst")
EV_CREST = "keystone"

GILT_GRAD = ('<linearGradient id="{id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFF3C8"/>'
             '<stop offset=".45" stop-color="#E3C77E"/><stop offset="1" stop-color="#9C7836"/></linearGradient>')


def _svg(w, h, x, y, body, defs=""):
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="position:absolute;left:{x}px;top:{y}px;overflow:visible">'
            f'<defs>{defs}</defs>{body}</svg>')


def _diamond(cx, cy, r, grad):
    """the superevent's diamond, smaller: gilt, a lacquer inside, a gilt core"""
    d = lambda rr: f"M{cx},{cy - rr}L{cx + rr},{cy}L{cx},{cy + rr}L{cx - rr},{cy}Z"
    return (f'<path d="{d(r)}" fill="url(#{grad})"/><path d="{d(r - 1.6)}" fill="#0B1115"/>'
            f'<path d="{d(r * .42)}" fill="url(#{grad})"/>')


def keystone(cx, base):
    """a stepped deco keystone of three tiers rising from the edge, gilt-edged lacquer, a diamond in its top tiers"""
    tiers = [(33, 9), (23, 8), (13, 8)]            # half-width, height of each tier, from the bottom
    pts, y = [], base
    for hw, th in tiers:
        pts += [(cx - hw, y), (cx - hw, y - th)]
        y -= th
    right = [(2 * cx - x, yy) for x, yy in reversed(pts)]
    outline = pts + right
    d = "M" + "L".join(f"{x},{yy}" for x, yy in outline)
    inner, y = [], base
    for hw, th in tiers:
        inner += [(cx - hw + 3, y), (cx - hw + 3, y - th + 3)]
        y -= th
    inner = inner[:-1] + [(cx - tiers[-1][0] + 3, y + 3)]
    inner_d = "M" + "L".join(f"{x},{yy}" for x, yy in inner + [(2 * cx - x, yy) for x, yy in reversed(inner)])
    body = (f'<path d="{d}Z" fill="#0F171C"/>'
            f'<path d="{inner_d}" fill="none" stroke="rgba(201,165,90,.45)" stroke-width="1"/>'
            f'<path d="{d}" fill="none" stroke="url(#kg)" stroke-width="1.2"/>'
            + _diamond(cx, base - 15, 7.5, "kg"))
    return _svg(581, 40, 0, 0, body, GILT_GRAD.format(id="kg")), 33


def _globe_uri(d):
    import globe_art as GA
    buf = io.BytesIO()
    GA.globe(d, GA.VIEW).save(buf, "PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def globe(cx, base):
    """the superevent's crest, small: Valsora rising in a half sunburst of bold rays"""
    r, rg = 28, 16
    rays = ""
    for k in range(9):
        a0, a1 = np.radians(180 - 10 - 20 * k - 4), np.radians(180 - 10 - 20 * k + 4)
        p = [(cx + r * np.cos(a0), base - r * np.sin(a0)), (cx + r * np.cos(a1), base - r * np.sin(a1)),
             (cx + (rg + 3) * np.cos(a1), base - (rg + 3) * np.sin(a1)), (cx + (rg + 3) * np.cos(a0), base - (rg + 3) * np.sin(a0))]
        rays += '<path d="M' + "L".join(f"{x:.2f},{y:.2f}" for x, y in p) + 'Z" fill="url(#cg)"/>'
    body = (f'<path d="M{cx - r - 1},{base}A{r + 1},{r + 1} 0 0 1 {cx + r + 1},{base}Z" fill="#0B1115"/>' + rays
            + f'<clipPath id="half"><rect x="{cx - rg}" y="{base - rg}" width="{2 * rg}" height="{rg}"/></clipPath>'
            f'<image href="{_globe_uri(2 * rg)}" x="{cx - rg}" y="{base - rg}" width="{2 * rg}" height="{2 * rg}" clip-path="url(#half)"/>'
            f'<path d="M{cx - rg - .5},{base}A{rg + .5},{rg + .5} 0 0 1 {cx + rg + .5},{base}" fill="none" stroke="#E3C77E" stroke-width="1"/>')
    return _svg(581, 40, 0, 0, body, GILT_GRAD.format(id="cg")), r + 3


def fan(cx, base):
    """a deco fan: a half disc of seven broad wedges, gilt and lacquer in turn, round a gilt half sun"""
    r0, r1 = 9, 25
    body = f'<path d="M{cx - r1 - 1.5},{base}A{r1 + 1.5},{r1 + 1.5} 0 0 1 {cx + r1 + 1.5},{base}Z" fill="#0B1115"/>'
    n = 7
    for k in range(n):
        if k % 2:
            continue
        a0, a1 = np.radians(180 - 180 * k / n), np.radians(180 - 180 * (k + 1) / n)
        (x0, y0), (x1, y1) = (cx + r1 * np.cos(a0), base - r1 * np.sin(a0)), (cx + r1 * np.cos(a1), base - r1 * np.sin(a1))
        (x2, y2), (x3, y3) = (cx + r0 * np.cos(a1), base - r0 * np.sin(a1)), (cx + r0 * np.cos(a0), base - r0 * np.sin(a0))
        body += (f'<path d="M{x0:.2f},{y0:.2f}A{r1},{r1} 0 0 1 {x1:.2f},{y1:.2f}L{x2:.2f},{y2:.2f}'
                 f'A{r0},{r0} 0 0 0 {x3:.2f},{y3:.2f}Z" fill="url(#fg)"/>')
    body += (f'<path d="M{cx - r1 - 1},{base}A{r1 + 1},{r1 + 1} 0 0 1 {cx + r1 + 1},{base}" fill="none" stroke="#E3C77E" stroke-width="1.2"/>'
             f'<path d="M{cx - r0 + 2},{base}A{r0 - 2},{r0 - 2} 0 0 1 {cx + r0 - 2},{base}Z" fill="url(#fg)"/>')
    return _svg(581, 40, 0, 0, body, GILT_GRAD.format(id="fg")), r1 + 4


def diamond(cx, base):
    """a gilt diamond on the edge, with tapering rules above the rail either side, like the news masthead's"""
    body = ""
    for side in (-1, 1):
        for y, x0, x1 in ((base - 4, 15, 52), (base - 8, 15, 36)):
            a, b = cx + side * x0, cx + side * x1
            body += f'<path d="M{min(a, b)},{y + .5}H{max(a, b)}" stroke="url(#dg{side + 1})" stroke-width="1"/>'
    defs = "".join(f'<linearGradient id="dg{side + 1}" x1="{0 if side > 0 else 1}" y1="0" x2="{1 if side > 0 else 0}" y2="0">'
                   '<stop offset="0" stop-color="#E3C77E"/><stop offset="1" stop-color="#E3C77E" stop-opacity="0"/></linearGradient>'
                   for side in (-1, 1)) + GILT_GRAD.format(id="dmg")
    body += _diamond(cx, base, 12, "dmg")
    return _svg(581, 50, 0, 0, body, defs), 14


def sunburst(cx, base, r=28):
    """v0.7 to v0.8.1: a half sunburst of thin rays with a ring and a diamond (for comparison)"""
    return (f'<div style="position:absolute;left:{cx - r}px;top:{base - r}px;width:{2 * r}px;height:{r}px;overflow:hidden">'
            f'<div style="position:absolute;left:0;top:0;width:{2 * r}px;height:{2 * r}px;border-radius:50%;'
            'background:repeating-conic-gradient(from -90deg,rgba(227,199,126,.55) 0deg 2.5deg,transparent 2.5deg 12deg),'
            'radial-gradient(circle,#1E2A31 0 55%,#11191E 56%)"></div>'
            f'<div style="position:absolute;left:{r * .38}px;top:{r * .38}px;width:{r * 1.24}px;height:{r * 1.24}px;border-radius:50%;'
            'border:1px solid #C9A55A;box-sizing:border-box"></div></div>'
            f'<div style="position:absolute;left:{cx - 5}px;top:{base - r * .55 - 5}px;width:10px;height:10px;transform:rotate(45deg);'
            'background:linear-gradient(135deg,#F1DC9C,#8B6A2C)"></div>'), 30


def ev_crest(design, cx, base):
    """(the crest's HTML, the half-width of the gap the card's top rail leaves for it)"""
    return {"keystone": keystone, "globe": globe, "fan": fan, "diamond": diamond, "sunburst": sunburst}[design](cx, base)


EVT = 30     # the card's top edge in the event window's top piece (581 x 121; the crest rises above it)


def ev_top(design):
    """the top piece of a country event's card (gen_textures.py's 'ev_top'; its classes are gen_textures.CSS's): the
    lacquer card from y EVT with chamfered corners, its gilt rails broken round the crest, the title's band"""
    crest, gap = ev_crest(design, 290.5, EVT)
    return (f'<div class="lac" style="position:absolute;left:0;right:0;top:{EVT}px;bottom:0;'
            f'clip-path:polygon(10px 0,calc(100% - 10px) 0,100% 10px,100% 100%,0 100%,0 10px)"></div>'
            + f'<svg width="581" height="121" style="position:absolute;left:0;top:0"><path d="M.5,121V{EVT + 10}L10.5,{EVT + .5}'
            f'H{290.5 - gap}M{290.5 + gap},{EVT + .5}H570.5L580.5,{EVT + 10}V121" fill="none" stroke="url(#evg)" stroke-width="1"/>'
            '<defs><linearGradient id="evg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F1DC9C"/>'
            '<stop offset="1" stop-color="#C9A55A"/></linearGradient></defs>'
            f'<path d="M4.5,121V{EVT + 12}L12.5,{EVT + 4.5}H568.5L576.5,{EVT + 12}V121" fill="none" stroke="rgba(201,165,90,.35)"/></svg>'
            # the title's band (the title is centred at y 70-102): a gilt hairline above and below, fading at the ends
            + '<div class="frame" style="left:46px;right:46px;top:63px;height:1px;'
            'background:linear-gradient(90deg,transparent,#C9A55A 18%,#C9A55A 82%,transparent)"></div>'
            + '<div class="frame" style="left:46px;right:46px;top:107px;height:1px;'
            'background:linear-gradient(90deg,transparent,rgba(201,165,90,.6) 18%,rgba(201,165,90,.6) 82%,transparent)"></div>'
            + f'<i class="ck tr" style="top:{EVT + 6}px;right:8px"></i>' + crest)
