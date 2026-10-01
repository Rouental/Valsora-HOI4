"""Flags redrawn for HOI4's 82×52 (run by hand; writes source/flags/<TAG>.png).

    KIL  the author's flag (source/flags/originals/KIL.png) is about 2:1 with fine gold
         filigree; squeezed into 82×52 it came out as noise. Redrawn at 82:52 with the
         same layout (framed arms on the left, six gold-edged bars on the right), the
         filigree left out and the arms enlarged.
    FRX  the only picture was rotated and waved, so drawn from scratch: a red-white-blue
         tricolour with a stylised Montenegrin double-headed eagle.

    python3 scripts/redraw_flags.py
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

FLAGS = Path("source/flags")
W, H = 820, 520  # 10× the game's flag


def kil():
    src = Image.open(FLAGS / "originals/KIL.png").convert("RGB")
    blue, gold, white, black = (41, 45, 129), (253, 212, 76), (255, 255, 255), (0, 0, 0)
    im = Image.new("RGB", (W, H), blue)
    d = ImageDraw.Draw(im)
    cw = 470  # the canton (framed arms), full height
    d.rectangle([12, 12, cw - 12, H - 13], outline=gold, width=10)
    fr = 62   # frame: blue band with white rosettes at the corners and midpoints
    for x, y in [(37, 37), (cw - 37, 37), (37, H - 38), (cw - 37, H - 38), (cw // 2, 37),
                 (cw // 2, H - 38), (37, H // 2), (cw - 37, H // 2)]:
        d.rectangle([x - 20, y - 20, x + 20, y + 20], fill=black)
        d.ellipse([x - 15, y - 15, x + 15, y + 15], fill=white)
        d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=gold)
    d.rectangle([fr, fr, cw - fr, H - fr - 1], fill=gold)
    # the arms on their tricolour field, cropped from the author's flag
    inner = src.crop((90, 100, 597, 522))
    iw, ih = cw - 2 * fr - 16, H - 2 * fr - 17
    im.paste(inner.resize((iw, ih), Image.LANCZOS), (fr + 8, fr + 8))
    # six bars on the right
    x0, x1 = cw + 22, W - 14
    gap = (H - 24) / 6
    for i in range(6):
        y0 = 12 + i * gap + 9
        y1 = 12 + (i + 1) * gap - 9
        d.rectangle([x0, y0, x1, y1], outline=gold, width=9)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=black, outline=gold, width=4)
        d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=white)
        for s in (-1, 1):  # a plain gold stroke for the filigree
            d.line([cx + s * 32, cy, cx + s * ((x1 - x0) / 2 - 22), cy], fill=gold, width=7)
    im.save(FLAGS / "KIL.png")


def eagle(d, cx, cy, s, gold, dark):
    """A stylised Montenegrin double-headed eagle, centred on (cx, cy), unit s px."""
    def P(pts, mirror=False):
        return [(cx + (-x if mirror else x) * s, cy + y * s) for x, y in pts]
    wing = [(0.6, -0.6), (1.4, -2.4), (2.6, -3.3), (3.3, -3.2), (3.0, -2.6), (3.5, -2.4),
            (3.1, -1.8), (3.6, -1.5), (3.0, -1.0), (3.4, -0.6), (2.7, -0.3), (2.9, 0.2),
            (2.1, 0.2), (2.2, 0.7), (1.4, 0.6), (0.8, 0.4)]
    neck = [(0.2, -0.7), (0.5, -1.7), (0.9, -2.3), (1.4, -2.4), (1.8, -2.15), (1.55, -1.95),
            (1.25, -1.95), (1.0, -1.6), (0.9, -0.8)]
    tongue = [(1.55, -1.95), (2.0, -1.9), (1.7, -1.75)]
    tail = [(0.0, 1.4), (0.5, 1.4), (0.9, 2.4), (0.55, 2.3), (0.4, 2.7), (0.0, 2.4)]
    leg = [(0.6, 1.1), (1.2, 1.5), (1.55, 1.45), (1.6, 1.75), (1.2, 1.8), (0.6, 1.5)]
    for m in (False, True):
        for part in (wing, neck, tail, leg):
            d.polygon(P(part, m), fill=gold, outline=dark)
        d.polygon(P(tongue, m), fill=(200, 30, 30))
        x, y = P([(1.25, -2.15)], m)[0]
        d.ellipse([x - 0.08 * s, y - 0.08 * s, x + 0.08 * s, y + 0.08 * s], fill=dark)
    d.ellipse(P([(-0.95, -0.9), (0.95, 1.5)]), fill=gold, outline=dark)  # body
    # crown between the heads
    d.polygon(P([(-0.7, -2.5), (-0.8, -3.2), (-0.35, -2.9), (0, -3.45), (0.35, -2.9), (0.8, -3.2),
                 (0.7, -2.5)]), fill=gold, outline=dark)
    d.ellipse(P([(-0.12, -3.75), (0.12, -3.5)]), fill=gold, outline=dark)
    # sceptre (right claw) and orb (left claw)
    d.line(P([(1.45, 1.6), (2.3, 0.6)]), fill=dark, width=int(s * 0.14))
    d.ellipse(P([(2.15, 0.35), (2.5, 0.7)]), fill=gold, outline=dark)
    d.ellipse(P([(-1.85, 1.35), (-1.25, 1.95)]), fill=gold, outline=dark)
    # shield: blue over green, a gold lion passant
    shield = [(-0.75, -0.75), (0.75, -0.75), (0.75, 0.55), (0, 1.25), (-0.75, 0.55)]
    d.polygon(P(shield), fill=(30, 70, 160), outline=dark)
    d.polygon(P([(-0.75, 0.6), (0.75, 0.6), (0.7, 0.62), (0, 1.25), (-0.7, 0.62)]), fill=(40, 130, 60))
    lion = [(-0.5, 0.15), (-0.45, -0.15), (0.2, -0.15), (0.3, -0.45), (0.55, -0.45), (0.55, -0.1),
            (0.45, 0.0), (0.45, 0.45), (0.33, 0.45), (0.3, 0.1), (-0.25, 0.1), (-0.3, 0.45),
            (-0.42, 0.45), (-0.45, 0.2), (-0.6, -0.3), (-0.5, -0.35)]
    d.polygon(P(lion), fill=gold, outline=dark)


def frx():
    im = Image.new("RGB", (W * 2, H * 2))
    d = ImageDraw.Draw(im)
    for i, c in enumerate([(171, 28, 40), (255, 255, 255), (34, 69, 139)]):
        d.rectangle([0, i * H * 2 // 3, W * 2, (i + 1) * H * 2 // 3], fill=c)
    eagle(d, W, H * 1.08, 125, (222, 178, 60), (120, 80, 20))
    im.resize((W, H), Image.LANCZOS).save(FLAGS / "FRX.png")


if __name__ == "__main__":
    kil()
    frx()
    for t in ("KIL", "FRX"):
        big = Image.open(FLAGS / f"{t}.png")
        prev = Image.fromarray(np.hstack([np.asarray(big.resize((82, 52), Image.LANCZOS).resize((328, 208), Image.NEAREST)),
                                          np.asarray(big.resize((328, 208), Image.LANCZOS))]))
        prev.save(f"work/flag_{t}.png")
