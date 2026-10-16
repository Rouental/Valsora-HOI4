"""The game's own fonts in the deco faces (v0.8, the user: "could you switch to the art deco fonts throughout the UI?
for example, currently the title of Roland is displayed in the base game's font").

    python game_fonts.py             -> valsora_deco_ui/gfx/fonts/<the game's font>.fnt/.dds, for every font in GAME
    python game_fonts.py --measure   -> the width-safe size of each, from the game's English text (to fill in GAME)

The Deco UI's own screens use its own fonts (gen_fonts.py); everything else the game draws (lists, tooltips, the
unit and designer screens, settings, window titles ...) uses the game's bitmap fonts, defined in its core.gfx by
file path. A font file of the same name in the mod replaces the game's everywhere, as hoi_mapfont4 (the map's
country names) has since v0.3. Each is redrawn in the Deco UI's faces: Josefin Sans for text and numbers, Federo
capitals for the headers (the game's Orator titles).

The game's boxes are sized for its fonts, so each size is the largest whose text is no wider than the game's for 95 %
of the game's own English strings and at most 5 % wider for 99 % (--measure; the deco faces have wide capitals and a
small x-height, so they come out 2-5 px smaller than the game's nominal sizes). Tooltips (cg_16b) grow to fit their
text, so they use the Deco UI's 15 px body size. Each keeps the game's line height, and its capitals are centred where
the game's are, so text stays where the game puts it. The game's shadowed fonts (..mbs, ..bs) get the Deco UI's dark
rim. Only what English text needs is drawn (gen_fonts.CHARS: Latin-1, Latin Extended-A, typographic punctuation);
the game's Cyrillic files stay its own.
"""
import glob
import os
import random
import re
import sys

from paths import FONTS_SRC as G, MOD, VANILLA

JOS = G + "josefinsans/JosefinSans[wght].ttf"
FED = G + "federo/Federo-Regular.ttf"
# the game's font file -> face, weight, rim, capitals, tracking, size (from --measure; None: --measure decides)
GAME = {
    # Ubuntu: the game's text and numbers, as Josefin Sans (the Deco UI's text face)
    "hoi_16mbs":         (JOS, 600, 1, False, 0, 12),
    "hoi_18mbs":         (JOS, 600, 1, False, 0, 13.5),
    "hoi_18":            (JOS, 500, 0, False, 0, 12.5),
    "hoi_20b":           (JOS, 600, 0, False, 0, 14),
    "hoi_20bs":          (JOS, 600, 1, False, 0, 14),
    "hoi_22tech":        (JOS, 600, 0, False, 0, 16.5),
    "hoi_30":            (JOS, 400, 0, False, 0, 29.5),
    "hoi_33":            (JOS, 500, 0, False, 0, 26),
    # Century Gothic: tooltips, which grow to fit their text, so the Deco UI's 15 px body size (width-safe: 12.5)
    "cg_16b":            (JOS, 600, 0, False, 0, 15),
    # the typewriter (unit, leader, designer, scientist screens), for paper: the game colours "hoi4_typewriter16" black
    # (core.gfx color 0xff000000) over white letters, and the "_inverted" ones white over black letters baked into the
    # texture (read from the game's own, 2026-10-16), so those carry the ink themselves (INK); both draw dark text
    "hoi4_typewriter16": (JOS, 500, 0, False, 0, 13.5),
    "hoi4_typewriter16_inverted": (JOS, 500, 0, False, 0, 13.5),
    "hoi4_typewriter22": (JOS, 500, 0, False, 0, 19),
    "hoi4_typewriter22_inverted": (JOS, 500, 0, False, 0, 19),
    # Garamond (settings, menus, message filters, chat, the news feed), as Federo: narrower than Josefin, so it fits
    # 1.5-2 px larger in the same boxes (Josefin would be 9.5-13 px)
    "garamond_14":       (FED, None, 0, False, 0, 11),
    "garamond_14_bold":  (FED, None, 0, False, 0, 12.5),
    "garamond_16":       (FED, None, 0, False, 0, 13),
    "garamond_16_bold":  (FED, None, 0, False, 0, 14.5),
    "vic_18":            (FED, None, 0, False, 0, 13),
    "vic_22":            (FED, None, 0, False, 0, 14.5),
    "vic_36":            (FED, None, 0, False, 0, 24.5),
    "standard":          (FED, None, 0, False, 0, 13),
    "standard_18":       (FED, None, 0, False, 0, 13),
    "standard_22":       (FED, None, 0, False, 0, 14.5),
    "newsfeed_body":     (FED, None, 0, False, 0, 11),
    "newsfeed_title":    (FED, None, 0, False, 0, 24.5),
    # Orator: window titles and headers, as Federo capitals
    "hoi_24header":      (FED, None, 0, True, 1, 14.5),
    "hoi_30header":      (FED, None, 0, True, 1, 18.5),
    "hoi_36header":      (FED, None, 0, True, 2, 20.5),
}


INK = (24, 20, 14)          # the "_inverted" typewriter fonts' letters: near black, a little warm, for the paper


def game_metrics(name):
    """the game's .fnt: line height, base, and its capitals' top and bottom (from 'H', less the cell's padding)"""
    t = open(VANILLA + f"gfx/fonts/{name}.fnt", encoding="utf-8-sig", errors="ignore").read()
    common = dict(re.findall(r"(\w+)=(-?\d+)", re.search(r"^common .*$", t, re.M).group(0)))
    pad = [int(v) for v in re.search(r"padding=(\d+),(\d+),(\d+),(\d+)", t).groups()]
    h = re.search(r"^char id=72\s.*$", t, re.M)
    d = {k: int(v) for k, v in re.findall(r"(\w+)=(-?\d+)", h.group(0))}
    top = d["yoffset"] + pad[0]
    bottom = d["yoffset"] + d["height"] - pad[2]
    return int(common["lineHeight"]), int(common["base"]), top, bottom


def game_widths(name):
    t = open(VANILLA + f"gfx/fonts/{name}.fnt", encoding="utf-8-sig", errors="ignore").read()
    chars = {int(m.group(1)): int(m.group(2)) for m in re.finditer(r"^char id=(\d+).*?xadvance=(-?\d+)", t, re.M)}
    kern = {(int(a), int(b)): int(k) for a, b, k in re.findall(r"kerning first=(\d+)\s+second=(\d+)\s+amount=(-?\d+)", t)}

    def width(s):
        cps = [ord(c) for c in s if ord(c) in chars]
        return sum(chars[c] for c in cps) + sum(kern.get(p, 0) for p in zip(cps, cps[1:]))
    return width


def measure(n=4000):
    """for each font in GAME, the largest size (0.5 px steps) whose text is no wider than the game's for 95 % of a
    sample of the game's English strings, and at most 5 % wider for 99 % (strings as character-count rows, so each
    size is one matrix product)"""
    import numpy as np
    import gen_fonts as GF
    texts = []
    for path in glob.glob(VANILLA + "localisation/english/**/*.yml", recursive=True):
        for line in open(path, encoding="utf-8-sig", errors="ignore"):
            m = re.match(r'\s*[^#\s][^:]*:\d*\s*"(.*)"\s*$', line)
            if m:
                s = re.sub(r"§.|£[^£\s]*£?|\$[^$]*\$|\[[^\]]*\]|\\n", " ", m.group(1)).strip()
                if 3 <= len(s) <= 60:
                    texts.append(s)
    random.seed(1)
    texts = random.sample(texts, min(n, len(texts)))
    for name, (face, wt, rim, caps, tr, size) in GAME.items():
        gw = game_widths(name)
        base = np.array([max(1, gw(s)) for s in texts], float)
        rows = [s.upper() if caps else s for s in texts]
        chars = sorted(set("".join(rows)))
        idx = {c: i for i, c in enumerate(chars)}
        C = np.zeros((len(rows), len(chars)))
        for r, s in enumerate(rows):
            for c in s:
                C[r, idx[c]] += 1
        best = None
        for sz in [x / 2 for x in range(16, 100)]:
            f = GF.load(face, sz, wt)
            adv = np.array([round(f.getlength(c)) + tr for c in chars], float)
            q = C @ adv / base
            p50, p95, p99 = np.percentile(q, [50, 95, 99])
            if p95 <= 1.0 and p99 <= 1.05:
                best = (sz, p50, p95, p99)
        print(f"{name:28} -> {best[0]}  (p50 {best[1]:.2f} p95 {best[2]:.2f} p99 {best[3]:.2f})" if best else f"{name:28} -> none",
              flush=True)


def build_all():
    import gen_fonts as GF
    out = []
    for name, (face, wt, rim, caps, tr, size) in GAME.items():
        lh, base, top, bottom = game_metrics(name)
        fb = dict(fallback=JOS, fb_weight=500) if face == FED else {}
        out.append(GF.build(name, face, size, rim, "ui", weight=wt, caps=caps, tracking=tr, kern_set=GF.ALNUM,
                            atlas=GF.fit_atlas, line=(lh, (top + bottom) / 2), diamond=True,
                            ink=INK if name.endswith("_inverted") else None, **fb))
        # the game's own base (v0.8.4): a font of several files (cg_16b with the game's hoi_16tooltip3, for Cyrillic)
        # must give them one base, or the game logs "base (13) in 'gfx/fonts/hoi_16tooltip3.fnt' does not match
        # previous fontfiles in font 'cg_16b'" (the user's error.log). The glyphs' offsets are measured from the line's
        # top, so the text draws where it did.
        fnt = MOD + f"gfx/fonts/{name}.fnt"
        t = open(fnt, encoding="utf-8").read()
        t2, n = re.subn(r"^(common lineHeight=\d+ base=)\d+", lambda m: m.group(1) + str(base), t, count=1, flags=re.M)
        assert n == 1, fnt
        open(fnt, "w", encoding="utf-8", newline="\n").write(t2)
    for o in out:
        print(f"{o['name']:28} {o['glyphs']} glyphs, atlas {o['atlas'][0]}x{o['atlas'][1]}, line {o['line']}")
    return out


if __name__ == "__main__":
    if "--measure" in sys.argv:
        measure()
    else:
        build_all()
