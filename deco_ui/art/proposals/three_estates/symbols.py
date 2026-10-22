"""The three estates' symbols in place of their holders' portraits (the author, 2026-10-22: "Instead of portraits, I think
I'd prefer to use symbols for the three estates"; then: "'rogacina issuant from a cauldron' is the name of the symbol, it
didn't mean to put it above an actual cauldron. Maybe just have the symbol for the 2nd estate be three crowns arranged in
a triangle. Maybe have the crowns look like a slightly more ornamented version of this? One with a red gem, one with
blue, one with green? For the third estate, I prefer the wheat and key"). Drawn by hand as SVG on a 200 x 200 box:
the First Estate's rogacina issuant from a cauldron traced from the author's picture of the faith's symbol; the Second's
crown traced from the author's picture of a crown (Heraldicon's), its ornaments Claude's; the Third's sheaf of wheat
bound with a key Claude's, the author's choice of three.

symbol(key, size) gives an <svg> of that size; GROUNDS the dark ground each sits on in a medallion.
"""

GOLD = ('<linearGradient id="sy_gold" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FBEAB4"/>'
        '<stop offset=".45" stop-color="#E3C77E"/><stop offset="1" stop-color="#A8842F"/></linearGradient>'
        '<linearGradient id="sy_bronze" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5A4520"/>'
        '<stop offset="1" stop-color="#1E170B"/></linearGradient>'
        + "".join(f'<radialGradient id="sy_gem_{k}" cx=".38" cy=".32" r=".75"><stop offset="0" stop-color="{a}"/>'
                  f'<stop offset=".55" stop-color="{b}"/><stop offset="1" stop-color="{c}"/></radialGradient>'
                  for k, (a, b, c) in {"red": ("#FFB4A8", "#C8322E", "#5E1010"), "blue": ("#B8D8FF", "#2E64C8", "#0F2A5E"),
                                       "green": ("#B8F0C4", "#2E9A4E", "#0E4A22")}.items()))
INK = "#16110A"

# the faith's rogacina issuant from a cauldron (the symbol's name), traced from the author's picture (200 x 186): the
# canopy with its two blades, the shaft, the cross-bar and the hooked arms
ROGACINA = [
    "M100,2 L198,75 C181,76 163,80 148,90 C141,63 127,41 107,28 L93,28 C73,41 59,63 52,90 C37,80 19,76 2,75 Z",
    "M93,20 H107 V166 H93 Z",
    "M56,100 H144 V112 H56 Z",
    ("M93,157 C76,157 57,149 44,135 C37,127 30,122 22,124 C15,126 13,135 18,141 L26,152 C23,145 24,139 29,138 "
     "C37,137 45,145 53,152 C67,165 83,175 100,176 C117,175 133,165 147,152 C155,145 163,137 171,138 C176,139 177,145 "
     "174,152 L182,141 C187,135 185,126 178,124 C170,122 163,127 156,135 C143,149 124,157 107,157 Z"),
]
# the crown, traced from the author's picture (200 x 80): two outer points flaring out, a lozenge in the middle, two
# scallops each side of it, the base an arch
CROWN = ("M0,9.3 L35.5,24.8 C27,34 32,52 45.3,53.3 C54,54 61,47 64.8,39.5 C68,45 74,46.5 77.9,46.1 "
         "C86,45.5 93,38 90.7,30.7 L79.5,20.5 L100,0 L120.5,20.5 L109.3,30.7 C107,38 114,45.5 121.3,46.1 "
         "C126,46.5 132,45 134.7,39.5 C139,47 146,54 154.7,53.3 C168,52 173,34 164.5,24.8 L200,9.3 L169.3,80 "
         "Q100,57.6 29.9,80 Z")


def outlined(paths, fill, width=5, transform=""):
    """the paths filled, with one dark outline round all of them (the outline drawn first, the fills over it)"""
    t = f' transform="{transform}"' if transform else ""
    under = "".join(f'<path d="{d}" fill="{INK}" stroke="{INK}" stroke-width="{width}" stroke-linejoin="round"/>' for d in paths)
    over = "".join(f'<path d="{d}" fill="{fill}"/>' for d in paths)
    return f"<g{t}>{under}{over}</g>"


def first():
    """the golden rogacina issuant from a cauldron, the faith's symbol, as the author drew it"""
    s = 0.88
    return outlined(ROGACINA, "url(#sy_gold)", 5, f"translate({100 - 100 * s:.1f},{(200 - 186 * s) / 2:.1f}) scale({s})")


def crown(x, y, w, gem):
    """the author's crown a little more ornate, its top left at (x, y), w wide: a jewelled band along the arch, pearls on
    the three points, a gem in the lozenge and a larger one in the band's middle, both of `gem`'s colour"""
    k = w / 200
    band = "M29.9,80 Q100,57.6 169.3,80 L173.6,70 Q100,46 25.6,70 Z"            # the band under the arch's top line
    pearls = "".join(f'<circle cx="{px}" cy="{py}" r="6" fill="url(#sy_gold)" stroke="{INK}" stroke-width="2.4"/>'
                     for px, py in ((2, 8), (198, 8), (100, -4)))
    studs = "".join(f'<circle cx="{px}" cy="{py}" r="2.6" fill="#FFF4D0" stroke="{INK}" stroke-width="1.2"/>'
                    for px, py in ((46, 70.5), (70, 65.6), (130, 65.6), (154, 70.5)))
    return (f'<g transform="translate({x},{y}) scale({k})">'
            + outlined([CROWN], "url(#sy_gold)", 5)
            + f'<path d="{band}" fill="rgba(168,132,47,.55)" stroke="{INK}" stroke-width="1.6"/>'
            + f'<path d="M100,10 L109,20.5 L100,31 L91,20.5 Z" fill="url(#sy_gem_{gem})" stroke="{INK}" stroke-width="1.6"/>'
            + f'<ellipse cx="100" cy="63.8" rx="9" ry="6.6" fill="url(#sy_gem_{gem})" stroke="{INK}" stroke-width="1.8"/>'
            + studs + pearls + "</g>")


def second():
    """three crowns in a triangle, two and one (as heraldry sets three charges): red and blue above, green below"""
    w = 90
    h = w * .4
    return (crown(100 - w - 5, 100 - h - 12, w, "red") + crown(105, 100 - h - 12, w, "blue")
            + crown(100 - w / 2, 100 + 12, w, "green"))


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


DRAW = {"first": first, "second": second, "third": third_sheaf}
GROUNDS = {"first": ("#3A352A", "#0E0D0A"), "second": ("#4A1E24", "#12080A"), "third": ("#1E3347", "#090E14")}


def symbol(key, size, pad=0.08):
    """the symbol as an <svg> of size x size px, a margin of `pad` all round"""
    m = 200 * pad
    return (f'<svg width="{size}" height="{size}" viewBox="{-m} {-m} {200 + 2 * m} {200 + 2 * m}" style="display:block">'
            f'<defs>{GOLD}</defs>{DRAW[key]()}</svg>')
