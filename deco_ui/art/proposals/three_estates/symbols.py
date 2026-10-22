"""The three estates' symbols in place of their holders' portraits (the author, 2026-10-22: "Instead of portraits, I think
I'd prefer to use symbols for the three estates. A golden rogacina issuant from a cauldron for the First Estate (the
symbol of the faith,) three crowns pierced by a sword for the second estate, and I don't know what the third estate
could use"). Drawn by hand as SVG on a 200 x 200 box: the rogacina traced from the author's picture of the faith's
symbol; the cauldron, the crowns and sword and the Third Estate's three candidates Claude's.

symbol(key, size) gives an <svg> of that size; GROUNDS the dark ground each sits on in a medallion.
"""

GOLD = ('<linearGradient id="sy_gold" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FBEAB4"/>'
        '<stop offset=".45" stop-color="#E3C77E"/><stop offset="1" stop-color="#A8842F"/></linearGradient>'
        '<linearGradient id="sy_steel" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#9AA3AB"/>'
        '<stop offset=".5" stop-color="#F2F4F5"/><stop offset="1" stop-color="#8A939B"/></linearGradient>'
        '<linearGradient id="sy_bronze" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5A4520"/>'
        '<stop offset="1" stop-color="#1E170B"/></linearGradient>')
INK = "#16110A"

# the faith's rogacina, traced from the author's picture (200 x 186): the canopy with its two blades, the shaft, the
# cross-bar and the hooked arms
ROGACINA = [
    "M100,2 L198,75 C181,76 163,80 148,90 C141,63 127,41 107,28 L93,28 C73,41 59,63 52,90 C37,80 19,76 2,75 Z",
    "M93,20 H107 V166 H93 Z",
    "M56,100 H144 V112 H56 Z",
    ("M93,157 C76,157 57,149 44,135 C37,127 30,122 22,124 C15,126 13,135 18,141 L26,152 C23,145 24,139 29,138 "
     "C37,137 45,145 53,152 C67,165 83,175 100,176 C117,175 133,165 147,152 C155,145 163,137 171,138 C176,139 177,145 "
     "174,152 L182,141 C187,135 185,126 178,124 C170,122 163,127 156,135 C143,149 124,157 107,157 Z"),
]


def outlined(paths, fill, width=5, transform=""):
    """the paths filled, with one dark outline round all of them (the outline drawn first, the fills over it)"""
    t = f' transform="{transform}"' if transform else ""
    under = "".join(f'<path d="{d}" fill="{INK}" stroke="{INK}" stroke-width="{width}" stroke-linejoin="round"/>' for d in paths)
    over = "".join(f'<path d="{d}" fill="{fill}"/>' for d in paths)
    return f"<g{t}>{under}{over}</g>"


def first():
    """a golden rogacina issuant from a cauldron: the arms' foot in the cauldron's mouth, the rim over it"""
    s = 0.72
    rog = outlined(ROGACINA, "url(#sy_gold)", 6, f"translate({100 - 100 * s:.1f},12) scale({s})")
    mouth = '<ellipse cx="100" cy="140" rx="60" ry="9" fill="#0B0805" stroke="#C9A55A" stroke-width="2"/>'
    body = ('<path d="M40,140 C40,176 70,190 100,190 C130,190 160,176 160,140 C140,148 120,150 100,150 C80,150 60,148 40,140 Z" '
            f'fill="url(#sy_bronze)" stroke="{INK}" stroke-width="3"/>'
            '<path d="M40,140 C60,148 80,150 100,150 C120,150 140,148 160,140" fill="none" stroke="#E3C77E" stroke-width="2.6"/>'
            '<path d="M50,162 C70,170 130,170 150,162" fill="none" stroke="rgba(227,199,126,.55)" stroke-width="1.6"/>')
    legs = "".join(f'<path d="M{x - 5},184 L{x + 5},184 L{x + 3},197 L{x - 3},197 Z" fill="url(#sy_bronze)" stroke="{INK}" '
                   f'stroke-width="2"/>' for x in (66, 100, 134))
    rings = "".join(f'<circle cx="{x}" cy="150" r="8" fill="none" stroke="#C9A55A" stroke-width="3"/>' for x in (34, 166))
    return legs + rings + mouth + rog + body


def crown(cx, top, w=72):
    """an open crown: three fleurons and two pearls over a jewelled band; (back, front) so a blade can pass between"""
    x0, x1 = cx - w / 2, cx + w / 2
    band_y = top + 22
    fl = ""
    for i, x in enumerate((x0 + 4, cx - w / 4, cx, cx + w / 4, x1 - 4)):
        if i % 2 == 0:   # a fleuron: a point with a ball
            fl += f'<path d="M{x - 7},{band_y} L{x},{top + 4} L{x + 7},{band_y} Z"/><circle cx="{x}" cy="{top + 3}" r="4"/>'
        else:            # a pearl on a shorter point
            fl += f'<path d="M{x - 5},{band_y} L{x},{top + 12} L{x + 5},{band_y} Z"/><circle cx="{x}" cy="{top + 11}" r="3.2"/>'
    back = (f'<g fill="url(#sy_gold)" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round">{fl}</g>')
    front = (f'<path d="M{x0},{band_y} H{x1} L{x1 - 3},{band_y + 14} H{x0 + 3} Z" fill="url(#sy_gold)" stroke="{INK}" '
             f'stroke-width="2.4" stroke-linejoin="round"/>'
             + "".join(f'<rect x="{x - 3}" y="{band_y + 4}" width="6" height="6" transform="rotate(45 {x} {band_y + 7})" '
                       f'fill="{c}" stroke="{INK}" stroke-width="1"/>'
                       for x, c in ((cx - w / 3, "#8E2E2E"), (cx, "#2E5E8E"), (cx + w / 3, "#8E2E2E"))))
    return back, front


def second():
    """three crowns pierced by a sword, point upward: each crown's points behind the blade, its band in front"""
    blade = (f'<path d="M100,6 L108,22 L108,158 L92,158 L92,22 Z" fill="url(#sy_steel)" stroke="{INK}" stroke-width="2.4" '
             'stroke-linejoin="round"/><path d="M100,14 L100,156" stroke="rgba(22,17,10,.35)" stroke-width="1.2"/>')
    hilt = (f'<path d="M60,158 C70,152 90,156 100,156 C110,156 130,152 140,158 C130,166 110,164 100,164 C90,164 70,166 60,158 Z" '
            f'fill="url(#sy_gold)" stroke="{INK}" stroke-width="2.4"/>'
            f'<rect x="95" y="164" width="10" height="22" fill="#5A4520" stroke="{INK}" stroke-width="2"/>'
            f'<circle cx="100" cy="191" r="7" fill="url(#sy_gold)" stroke="{INK}" stroke-width="2.2"/>')
    crowns = [crown(100, t) for t in (18, 62, 106)]
    return "".join(b for b, _ in crowns) + blade + "".join(f for _, f in crowns) + hilt


def third_beehive():
    """a straw skep on its stand, three bees about it: the commons' industry"""
    coils = ""
    rows = [(150, 132), (128, 120), (108, 104), (90, 86), (74, 64), (62, 40)]   # (bottom y of the coil, its width)
    for (y, w), (y2, _) in zip(rows, rows[1:] + [(48, 0)]):
        h = y - y2
        coils += (f'<rect x="{100 - w / 2}" y="{y2}" width="{w}" height="{h + 2}" rx="{h / 2 + 1}" fill="url(#sy_gold)" '
                  f'stroke="{INK}" stroke-width="2.4"/>')
    top = f'<ellipse cx="100" cy="50" rx="14" ry="9" fill="url(#sy_gold)" stroke="{INK}" stroke-width="2.4"/>'
    door = f'<path d="M88,150 V138 C88,128 112,128 112,138 V150 Z" fill="#16110A"/>'
    stand = (f'<rect x="26" y="150" width="148" height="12" rx="3" fill="url(#sy_bronze)" stroke="{INK}" stroke-width="2.4"/>'
             f'<path d="M44,162 L40,186 M156,162 L160,186" stroke="#5A4520" stroke-width="7" stroke-linecap="round"/>')

    def bee(x, y, r):
        return (f'<g transform="translate({x},{y}) rotate({r})"><ellipse cx="-4" cy="-6" rx="6" ry="4" fill="rgba(251,234,180,.75)" '
                f'stroke="{INK}" stroke-width="1"/><ellipse cx="4" cy="-6" rx="6" ry="4" fill="rgba(251,234,180,.75)" '
                f'stroke="{INK}" stroke-width="1"/><ellipse cx="0" cy="0" rx="5" ry="8" fill="url(#sy_gold)" stroke="{INK}" '
                f'stroke-width="1.6"/><path d="M-4.5,-1 H4.5 M-4,3 H4" stroke="{INK}" stroke-width="1.6"/></g>')
    return stand + coils + top + door + bee(40, 70, -30) + bee(160, 62, 25) + bee(150, 112, 50)


def ear(x, y, angle, length=56):
    """an ear of wheat on its stalk, rising from (x, y) at an angle (0 = straight up)"""
    grains = ""
    for i in range(6):
        gy = -length + 10 + i * 8
        for side in (-1, 1):
            grains += (f'<ellipse cx="{side * 4.5}" cy="{gy}" rx="4" ry="7" transform="rotate({side * 22} {side * 4.5} {gy})" '
                       f'fill="url(#sy_gold)" stroke="{INK}" stroke-width="1.4"/>')
    tip = f'<ellipse cx="0" cy="{-length + 2}" rx="3.5" ry="7" fill="url(#sy_gold)" stroke="{INK}" stroke-width="1.4"/>'
    stalk = f'<path d="M0,0 L0,{-length + 12}" stroke="#A8842F" stroke-width="3"/>'
    return f'<g transform="translate({x},{y}) rotate({angle})">{stalk}{grains}{tip}</g>'


def third_sheaf():
    """a sheaf of wheat bound with a key: the fields and the towns"""
    stalks = ""
    for a in (-30, -18, -6, 6, 18, 30):     # the stalks below the band, fanning out to the ground
        stalks += (f'<path d="M100,118 L{100 + 70 * __import__("math").sin(__import__("math").radians(a)):.1f},'
                   f'{118 + 70 * __import__("math").cos(__import__("math").radians(a)):.1f}" stroke="#C9A55A" '
                   f'stroke-width="4" stroke-linecap="round"/>')
    ears = "".join(ear(100, 118, a, 92) for a in (-34, -20, -7, 7, 20, 34)) + ear(100, 118, 0, 100)
    band = f'<rect x="80" y="110" width="40" height="14" rx="3" fill="url(#sy_bronze)" stroke="{INK}" stroke-width="2.4"/>'
    key = (f'<g transform="rotate(-18 100 132)"><circle cx="46" cy="132" r="13" fill="none" stroke="{INK}" stroke-width="9"/>'
           f'<circle cx="46" cy="132" r="13" fill="none" stroke="url(#sy_gold)" stroke-width="5"/>'
           f'<path d="M58,128 H160 V136 H58 Z" fill="url(#sy_gold)" stroke="{INK}" stroke-width="2.2"/>'
           f'<path d="M140,136 V150 H148 V144 H154 V150 H160 V136 Z" fill="url(#sy_gold)" stroke="{INK}" stroke-width="2.2"/></g>')
    return stalks + ears + band + key


def third_mural():
    """a mural crown, the towns' crown, two ears of wheat crossed behind it: the burghers and the peasants"""
    ears = ear(128, 196, -27, 150) + ear(72, 196, 27, 150)
    merlons = "".join(f'<rect x="{x}" y="92" width="22" height="20" fill="url(#sy_gold)" stroke="{INK}" stroke-width="2.4"/>'
                      for x in (44, 89, 134))
    wall = (f'<path d="M38,110 H162 V162 H38 Z" fill="url(#sy_gold)" stroke="{INK}" stroke-width="2.6"/>'
            + "".join(f'<path d="M38,{y} H162" stroke="rgba(22,17,10,.55)" stroke-width="1.4"/>' for y in (127, 144))
            + "".join(f'<path d="M{x},{y0} V{y0 + 17}" stroke="rgba(22,17,10,.55)" stroke-width="1.4"/>'
                      for y0, xs in ((110, (64, 100, 136)), (127, (82, 118)), (144, (64, 136))) for x in xs)
            + f'<path d="M89,162 V142 C89,131 111,131 111,142 V162 Z" fill="#16110A"/>'
            + "".join(f'<path d="M{x},118 V130" stroke="#16110A" stroke-width="5" stroke-linecap="round"/>' for x in (54, 146)))
    return ears + merlons + wall


DRAW = {"first": first, "second": second, "third": third_beehive,
        "third_beehive": third_beehive, "third_sheaf": third_sheaf, "third_mural": third_mural}
GROUNDS = {"first": ("#3A352A", "#0E0D0A"), "second": ("#4A1E24", "#12080A"), "third": ("#1E3347", "#090E14")}
THIRD = [("third_beehive", "A beehive", "the commons' industry: many hands, one hive (Claude's first choice)"),
         ("third_sheaf", "A sheaf bound with a key", "the fields and the towns: the peasants' wheat, the burghers' keys"),
         ("third_mural", "A mural crown and wheat", "the towns' crown beside the nobles' three, the peasants' wheat behind it")]


def symbol(key, size, pad=0.08):
    """the symbol as an <svg> of size x size px, a margin of `pad` all round"""
    m = 200 * pad
    return (f'<svg width="{size}" height="{size}" viewBox="{-m} {-m} {200 + 2 * m} {200 + 2 * m}" style="display:block">'
            f'<defs>{GOLD}</defs>{DRAW[key]()}</svg>')


def medallion(key, size):
    """the symbol on its estate's ground: a dark radial wash in the estate's colour"""
    a, b = GROUNDS[key.split("_")[0] if key.startswith("third") else key]
    return (f'<div style="position:absolute;left:0;top:0;width:{size}px;height:{size}px;'
            f'background:radial-gradient(circle at 50% 42%,{a},{b} 78%)">{symbol(key, size)}</div>')
