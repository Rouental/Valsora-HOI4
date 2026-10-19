"""The emblem of the Association of Reibonnaise States, version C: the author's own design (2026-10-19, their sketch:
"Try making the Association of Reibonnaise states icon similar to this ... Hollier and Lanzerac both use their old flags
... Replace them with the flags in the mod"). A proposal, not in the mod until the author says yes.

The sketch: a central stem, four rays a side branching from it and running out past the shape to arrowheads, and
between the rays eight waving banners, the members' flags, the outline of the whole a scalloped leaf. Left, from the
top: Guedelon, Seigne, Lustiana, Hollier; right: Evriches, Lanzerac, Selgrave, Rouental. The flags are the mod's own
(`source/flags/`), Hollier's and Lanzerac's the current ones. Drawn symmetric (the sketch is nearly so), in the sketch's
coordinates (1200 x 800, the stem at x 600), scaled into a 1000 px square.

Two line colours: C_ink, the sketch's dark lines, for outside the game on a light ground; C_gilt, gilt lines with a
dark edge, which read on the game's dark screens. Each: emblem_C_<v>.png (2048 px) and .svg, game_C_<v>.png (the
game's 200 x 100 strip: the logo, then its lit frame), miniature_C_<v>.png (32 x 32: the leaf, its banners and the stem,
without the arrows); sheet_C.png beside them.

    CHROMIUM_PATH=/opt/pw-browsers/chromium python3 dist/emblem_proposals/reibonnaise_association/make_c.py
"""
import base64
import io
import math
import os

from PIL import Image
from playwright.sync_api import sync_playwright

import make as M   # the A and B versions' renderer and gradients

HERE, ROOT = M.HERE, M.ROOT
FLAGS = ROOT + "source/flags/"
# the lobes, top to bottom; (left, right) as in the sketch
LOBES = [("GDN", "EVR"), ("SGN", "LZC"), ("LST", "SGV"), ("HLR", "ROU")]

# the sketch's geometry, left half (x < 600); mirrored for the right
J = [(600, 262), (600, 355), (600, 440), (600, 525)]          # where the rays leave the stem
TIP = [(548, 40), (348, 128), (238, 330), (272, 560)]        # the arrowheads
EXIT = [(556, 100), (403, 176), (300, 349), (345, 552)]      # where each ray leaves the outline
BOTTOM = (600, 640)                                          # the stem's foot
# the outline between the exits (cubic Béziers: two control points and the end)
EDGE = [
    [((505, 90), (455, 190), EXIT[1])],
    [((340, 210), (290, 290), EXIT[2])],
    [((255, 400), (370, 450), EXIT[3])],
    [((400, 620), (450, 690), (510, 672)), ((560, 655), (572, 620), BOTTOM)],
]
INNER = 0.3    # each banner runs in from the outline to this far along its rays (from the stem), white within


def tr(p, right=False):
    """sketch -> the 1000 px square; right mirrors about the stem"""
    x, y = p
    if right:
        x = 1200 - x
    return (500 + (x - 600) * 1.2, 118 + (y - 35) * 1.2)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def fmt(p):
    return f"{p[0]:.1f},{p[1]:.1f}"


def lobe_path(i, right):
    """banner i: in along its upper ray from the outline, round the outline, back along its lower ray, and a soft
    inner edge between the two points INNER along them (the last banner runs down to the stem's foot)"""
    T = lambda p: tr(p, right)  # noqa: E731
    up_a = lerp(J[i], EXIT[i], INNER)
    d = f"M{fmt(T(up_a))}L{fmt(T(EXIT[i]))}"
    for c1, c2, end in EDGE[i]:
        d += f"C{fmt(T(c1))} {fmt(T(c2))} {fmt(T(end))}"
    if i < 3:
        lo_a = lerp(J[i + 1], EXIT[i + 1], INNER)
        d += f"L{fmt(T(lo_a))}"
        mid = lerp(lerp(up_a, lo_a, .5), (600, (up_a[1] + lo_a[1]) / 2), .35)   # the inner edge bows to the stem
        d += f"Q{fmt(T(mid))} {fmt(T(up_a))}Z"
    else:
        d += f"L{fmt(T((600, 600)))}Q{fmt(T((560, 560)))} {fmt(T(up_a))}Z"
    return d


def outline_path():
    """the whole scalloped leaf (both halves)"""
    pts = []
    for right in (False, True):
        d = f"M{fmt(tr(J[0], right))}L{fmt(tr(EXIT[0], right))}"
        for seg in EDGE:
            for c1, c2, end in seg:
                d += f"C{fmt(tr(c1, right))} {fmt(tr(c2, right))} {fmt(tr(end, right))}"
        pts.append(d + "Z")
    return "".join(pts)


def flag_uri(tag):
    im = Image.open(FLAGS + f"{tag}.png").convert("RGB")
    buf = io.BytesIO()
    im.save(buf, "PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode(), im.size


def bbox(d_pts):
    xs, ys = [p[0] for p in d_pts], [p[1] for p in d_pts]
    return min(xs), min(ys), max(xs), max(ys)


def lobe_points(i, right):
    pts = [lerp(J[i], EXIT[i], INNER), EXIT[i]] + [q for seg in EDGE[i] for q in seg]
    if i < 3:
        pts.append(lerp(J[i + 1], EXIT[i + 1], INNER))
    return [tr(p, right) for p in pts]


def arrow(a, b, w, colour):
    """a line from a to b with an open chevron at b"""
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    k, s = 34, 0.55
    l1 = (b[0] - k * math.cos(ang - s), b[1] - k * math.sin(ang - s))
    l2 = (b[0] - k * math.cos(ang + s), b[1] - k * math.sin(ang + s))
    return (f'<path d="M{fmt(a)}L{fmt(b)}M{fmt(l1)}L{fmt(b)}L{fmt(l2)}" fill="none" stroke="{colour}" '
            f'stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')


def emblem(variant, lit=False, mini=False):
    ink = "#16120C"
    line = ink if variant == "ink" else ("url(#giltlit)" if lit else "url(#gilt)")
    body, clips = "", ""
    for i, pair in enumerate(LOBES):
        for right, tag in zip((False, True), pair):
            cid = f"lobe{i}{'r' if right else 'l'}"
            d = lobe_path(i, right)
            clips += f'<clipPath id="{cid}"><path d="{d}"/></clipPath>'
            uri, (fw, fh) = flag_uri(tag)
            x0, y0, x1, y1 = bbox(lobe_points(i, right))
            # the flag covers the banner, its middle on the banner's middle, unstretched
            sc = max((x1 - x0) / fw, (y1 - y0) / fh) * 1.08
            w, h = fw * sc, fh * sc
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            body += (f'<g clip-path="url(#{cid})"><image href="{uri}" x="{cx - w / 2:.1f}" y="{cy - h / 2:.1f}" '
                     f'width="{w:.1f}" height="{h:.1f}" preserveAspectRatio="none"/></g>')
            body += f'<path d="{d}" fill="none" stroke="{ink}" stroke-width="{7 if not mini else 12}" stroke-linejoin="round"/>'
    leaf = outline_path()
    under = f'<path d="{leaf}" fill="#F4ECD9" stroke="{ink}" stroke-width="{14 if variant == "gilt" else 7}" stroke-linejoin="round"/>'
    # the stem and the rays with their arrowheads; gilt lines get a dark edge under them so they read on light and dark
    lines = ""
    stem = (tr(J[0]), tr(BOTTOM))
    widths = [(16, ink), (9, line)] if variant == "gilt" else [(9, ink)]
    if mini:
        widths = [(26, ink), (15, line)] if variant == "gilt" else [(16, ink)]
    for w, colour in widths:
        lines += (f'<path d="M{fmt(stem[0])}L{fmt(stem[1])}" stroke="{colour}" stroke-width="{w}" stroke-linecap="round"/>')
        if mini:   # 32 px: the leaf, its banners and the stem; the arrows would only blur it
            continue
        for i in range(4):
            for right in (False, True):
                lines += arrow(tr(J[i], right), tr(TIP[i], right), w, colour)
    return f"<defs>{clips}</defs>{under}{body}{lines}"


def main():
    out = {}
    with sync_playwright() as p:
        b = p.chromium.launch(**M.CHROMIUM)
        pg = b.new_page(device_scale_factor=1)
        for v in ("ink", "gilt"):
            svg = M.doc(emblem(v))
            open(HERE + f"emblem_C_{v}.svg", "w").write(svg)
            M.render(pg, svg.replace('width="1000" height="1000"', 'width="2048" height="2048"'), HERE + f"emblem_C_{v}.png", 2048)
            frames = []
            for lit in (False, True):
                s = M.doc(emblem(v, lit), size=400, box="40 40 920 920", glow=lit)
                M.render(pg, s, HERE + "_frame.png", 400)
                frames.append(Image.open(HERE + "_frame.png").convert("RGBA").resize((100, 100), Image.LANCZOS))
            strip = Image.new("RGBA", (200, 100))
            strip.paste(frames[0], (0, 0))
            strip.paste(frames[1], (100, 0))
            strip.save(HERE + f"game_C_{v}.png")
            M.render(pg, M.doc(emblem(v, mini=True), size=256, box="150 140 700 700"), HERE + "_mini.png", 256)
            Image.open(HERE + "_mini.png").convert("RGBA").resize((32, 32), Image.LANCZOS).save(HERE + f"miniature_C_{v}.png")
            out[v] = True
        b.close()
    for f in ("_frame.png", "_mini.png"):
        os.remove(HERE + f)
    sheet()


def sheet():
    """both line colours, every size, on the Deco UI's lacquer and on paper"""
    W, H = 1400, 1000
    cv = Image.new("RGBA", (W, H), (17, 25, 30, 255))
    cv.paste(Image.new("RGBA", (W // 2, H), (240, 232, 214, 255)), (W // 2, 0))
    for side in (0, 1):
        x0 = side * (W // 2)
        for row, v in enumerate(("gilt", "ink")):
            y0 = 30 + row * 490
            big = Image.open(HERE + f"emblem_C_{v}.png").resize((440, 440), Image.LANCZOS)
            cv.alpha_composite(big, (x0 + 20, y0))
            game = Image.open(HERE + f"game_C_{v}.png")
            cv.alpha_composite(game, (x0 + 480, y0 + 60))
            mini = Image.open(HERE + f"miniature_C_{v}.png")
            cv.alpha_composite(mini, (x0 + 480, y0 + 200))
            cv.alpha_composite(mini.resize((96, 96), Image.NEAREST), (x0 + 530, y0 + 200))
    cv.convert("RGB").save(HERE + "sheet_C.png")


if __name__ == "__main__":
    main()
