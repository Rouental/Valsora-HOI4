"""Flags redrawn for HOI4's 82×52 (run by hand; writes source/flags/<TAG>.png).

    FRX  the only picture was rotated and waved, so drawn from scratch: a red-white-blue
         tricolour with a stylised Montenegrin double-headed eagle.

    python3 scripts/redraw_flags.py
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

FLAGS = Path("source/flags")
W, H = 820, 520  # 10× the game's flag


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
    frx()
    for t in ("FRX",):
        big = Image.open(FLAGS / f"{t}.png")
        prev = Image.fromarray(np.hstack([np.asarray(big.resize((82, 52), Image.LANCZOS).resize((328, 208), Image.NEAREST)),
                                          np.asarray(big.resize((328, 208), Image.LANCZOS))]))
        prev.save(f"work/flag_{t}.png")
