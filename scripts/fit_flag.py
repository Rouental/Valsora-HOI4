"""Fit a flag the author sends in another shape to HOI4's 82:52, without stretching (2026-10-15: the fits done by hand
until then, each with its own script, follow a few rules; this applies them and refuses what they don't cover).

    python3 scripts/fit_flag.py TAG picture [--ideology IDEO] [--frame auto|N] [--how auto|trim|add] [--dry]

writes source/flags/TAG.png (TAG_<ideology>.png with --ideology) and work/flag_fit_TAG.png, a sheet with the picture as
sent, the fitted flag and the flag in game (82 x 52, three times larger): look at it before committing.

Nothing is resampled: the fitted flag is the picture's own pixels with plain lines repeated or taken out, from the
middle of plain stretches (runs of rows or columns all like the first), so emblems keep their shape and size. Thin
plain strips along an edge (a border, a narrow margin) are never changed. By the flag's build, the rules of the hand
fits:
  - a field (its plain lines all one colour: Cotefer, Kianhua, Tsuruma, Myehn): plain field taken out of the long
    side, in proportion to how much each part has (Cotefer's plain fly, its hoist margin being thin; a centred
    emblem's two sides equally); if there isn't enough, plain field added to the short side;
  - vertical bands (rows across them, the same everywhere, out to the top or the bottom: Qinguo, Mezzogiorno): only
    rows change, so the bands keep their widths: added when too wide (Qinguo's above and below the ring,
    Mezzogiorno's mostly at the foot, its emblem being at the top), taken out when too tall;
  - horizontal stripes (columns across them, out to the hoist or the fly: Entroterra, Fraxhemark): too tall, they are
    lengthened; too wide, made taller, every stripe in proportion to its height (Entroterra's flowers staying in the
    middle of the white), if every stripe has plain rows of its own; else shortened at the ends (Fraxhemark's eagle
    covers its white stripe);
  - anything else (quarters, a cross, Ganden's border and triangle, which was redrawn): refused, nothing written:
    fit that flag by hand.
--how trim / add allows only taking out / only adding. --frame: screenshots come with a thin frame (the author's,
2026-10-15: 3 px); auto finds a uniform ring of 1-6 px whose colour stops at its inner edge (a flag's own border runs
on, so it is kept), N crops N px each side. --tol: how far two pixels may differ and still be the same colour (noise).
"""
import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

RATIO = 82 / 52


def alike(a, b, tol):
    """two lines (rows or columns, n x 4) the same but for noise: at most one pixel off by more than tol (a shifted
    edge moves two or more), and little difference on the whole"""
    d = np.abs(a.astype(int) - b.astype(int)).max(-1)
    return (d > tol).sum() <= 1 and d.mean() <= tol / 4


def runs(lines, tol):
    """[(first, last)] of the plain stretches: runs of lines all like the run's first line (end to end, so the slowly
    turning edge of a ring is never one); lone lines are left out"""
    out, i, n = [], 0, len(lines)
    while i < n - 1:
        j = i
        while j + 1 < n and alike(lines[i], lines[j + 1], tol):
            j += 1
        if j > i:
            out.append((i, j))
        i = j + 1
    return out


def share(n, sizes):
    """n split in proportion to sizes, whole numbers adding up to n"""
    tot = sum(sizes)
    raw = [n * s / tot for s in sizes]
    got = [int(r) for r in raw]
    for i in sorted(range(len(raw)), key=lambda i: raw[i] - got[i], reverse=True)[:n - sum(got)]:
        got[i] += 1
    return got


def frame(a, how, tol):
    """the picture without a screenshot's frame, and the frame's width"""
    if how != "auto":
        k = int(how)
        return (a[k:-k, k:-k] if k else a), k

    def ring(k):   # the pixels of the k-th ring from the edge (0-based)
        h, w = a.shape[:2]
        return np.concatenate([a[k, k:w - k], a[h - 1 - k, k:w - k], a[k:h - k, k], a[k:h - k, w - 1 - k]])

    def uniform(px, colour):
        return np.percentile(np.abs(px.astype(int) - colour).max(-1), 98) <= tol

    colour = np.median(ring(0), 0)
    k = 0
    while k < 6 and uniform(ring(k), colour):
        k += 1
    if k == 0 or uniform(ring(k), colour):   # no ring, or one that runs on: the flag's own border
        return a, 0
    return a[k:-k, k:-k], k


MIN_RUN = 0.03     # a plain stretch is at least this share of the flag's height (rows) or width (columns)
EDGE_STRIP = 0.08  # a plain strip of one colour along an edge, thinner than this share, is a border: never changed
MIN_BUILD = 0.06   # plain lines across patterns tell the flag's build (bands, stripes) from this share up


def line(a, axis, k):
    return a[k] if axis == 0 else a[:, k]


def uniform_colour(ln, tol):
    """the line's one colour, or None if it has several"""
    c = np.median(ln, 0)
    return c if (np.abs(ln.astype(int) - c).max(-1) > tol).mean() <= 0.01 else None


def border(a, rows, cols, tol):
    """the stretches of a plain border round the flag (Ganden's): one colour on all four edges, thin; never changed"""
    h, w = a.shape[:2]
    edges = [rows[0] if rows and rows[0][0] == 0 else None, rows[-1] if rows and rows[-1][1] == h - 1 else None,
             cols[0] if cols and cols[0][0] == 0 else None, cols[-1] if cols and cols[-1][1] == w - 1 else None]
    if any(e is None for e in edges):
        return set()
    thick = [e[1] - e[0] + 1 for e in edges]
    if thick[0] > 0.12 * h or thick[1] > 0.12 * h or thick[2] > 0.12 * w or thick[3] > 0.12 * w:
        return set()
    cs = [uniform_colour(line(a, 0, edges[0][0]), tol), uniform_colour(line(a, 0, edges[1][1]), tol),
          uniform_colour(line(a, 1, edges[2][0]), tol), uniform_colour(line(a, 1, edges[3][1]), tol)]
    if any(c is None for c in cs) or any(np.abs(c - cs[0]).max() > tol for c in cs):
        return set()
    return {("r", edges[0]), ("r", edges[1]), ("c", edges[2]), ("c", edges[3])}


def segments(ln, tol):
    """[(first, last)] of the runs of one colour along a line (a column across stripes: the stripes)"""
    out, start = [], 0
    for k in range(1, len(ln) + 1):
        if k == len(ln) or np.abs(ln[k].astype(int) - ln[start].astype(int)).max() > tol:
            if k - start >= 0.02 * len(ln):      # leave out the edges' antialiasing
                out.append((start, k - 1))
            start = k
    return out


def resize_lines(a, axis, parts, add):
    """k lines added to (or taken from) the middle of each plain stretch: parts = [((first, last), k)]"""
    idx = list(range(a.shape[axis]))
    for (r0, r1), k in sorted(parts, reverse=True):    # from the end, so the indices before stay put
        mid = (r0 + r1) // 2
        if add:
            idx[mid:mid] = [mid] * k
        else:
            del idx[mid - k // 2:mid - k // 2 + k]
    return np.take(a, idx, axis=axis)


def fit(a, how, tol):
    """(fitted picture, what was done) or (None, why not)"""
    h, w = a.shape[:2]
    if abs(w / h - RATIO) / RATIO < 0.005:
        return a, "already 82:52"
    all_rows = runs([a[y] for y in range(h)], tol)
    all_cols = runs([a[:, x] for x in range(w)], tol)
    edge = border(a, all_rows, all_cols, tol)

    def keep(axis, r, size):   # long enough, and not a border or a thin plain strip along an edge
        if (("r" if axis == 0 else "c"), r) in edge or r[1] - r[0] + 1 < MIN_RUN * size:
            return False
        thin_edge = (r[0] == 0 or r[1] == size - 1) and r[1] - r[0] + 1 < EDGE_STRIP * size
        return not (thin_edge and uniform_colour(line(a, axis, r[0]), tol) is not None)
    rows = [r for r in all_rows if keep(0, r, h)]
    cols = [c for c in all_cols if keep(1, c, w)]

    def mid(axis, r):
        return line(a, axis, (r[0] + r[1]) // 2)
    uni_rows = [r for r in rows if uniform_colour(mid(0, r), tol) is not None]
    uni_cols = [c for c in cols if uniform_colour(mid(1, c), tol) is not None]
    # lines across patterns, long enough to tell the flag's build (a big round emblem's middle rows are nearly alike
    # for a few rows: too few to count)
    multi_rows = [r for r in rows if r not in uni_rows and r[1] - r[0] + 1 >= MIN_BUILD * h]
    multi_cols = [c for c in cols if c not in uni_cols and c[1] - c[0] + 1 >= MIN_BUILD * w]

    def one_pattern(axis, stretch_list):   # every stretch the same lines (true bands or stripes, not quarters)
        return all(alike(mid(axis, stretch_list[0]), mid(axis, r), tol) for r in stretch_list[1:])
    if multi_rows and multi_cols:
        build = "mixed"          # plain lines across patterns both ways: quarters, a cross ...
    elif multi_rows:             # rows cross vertical bands, the same everywhere, out to the top or the bottom
        build = "bands" if one_pattern(0, multi_rows) and any(r[0] == 0 or r[1] == h - 1 for r in multi_rows) \
            else "mixed"
    elif multi_cols:             # columns cross horizontal stripes, the same everywhere, out to the hoist or the fly
        build = "stripes" if one_pattern(1, multi_cols) and any(c[0] == 0 or c[1] == w - 1 for c in multi_cols) \
            else "mixed"
    else:                        # only plain lines of one colour: a field, if it is one colour throughout
        colours = [uniform_colour(mid(0, r), tol) for r in uni_rows] + [uniform_colour(mid(1, c), tol) for c in uni_cols]
        build = "field" if colours and all(np.abs(c - colours[0]).max() <= tol for c in colours) else "mixed"
    rows_b = [r for r in rows if r not in uni_rows]      # the lines across the bands
    cols_s = [c for c in cols if c not in uni_cols]      # the lines across the stripes
    wide = w / h > RATIO
    trim_n = (w - round(h * RATIO)) if wide else (h - round(w / RATIO))
    add_n = (round(w / RATIO) - h) if wide else (round(h * RATIO) - w)

    def proportional(stretch_list, n, add):
        parts = list(zip(stretch_list, share(n, [r1 - r0 + 1 for r0, r1 in stretch_list])))
        if not add and any(k > (r1 - r0 + 1) // 2 for (r0, r1), k in parts):
            return None
        return parts

    def stripes_taller():    # rows into every stripe, in proportion to its height (Entroterra), if every one can grow
        across = a[:, (multi_cols[0][0] + multi_cols[0][1]) // 2]
        stripes = segments(across, tol)
        by_stripe = []
        for s0, s1 in stripes:   # a stripe's own plain rows: of its colour, not a thin line, not across an emblem
            colour = across[(s0 + s1) // 2].astype(int)
            by_stripe.append([r for r in all_rows if s0 <= r[0] and r[1] <= s1 and r[1] - r[0] + 1 >= 0.02 * h
                              and (c := uniform_colour(a[(r[0] + r[1]) // 2], tol)) is not None
                              and np.abs(c - colour).max() <= tol])
        if not stripes or any(not b for b in by_stripe):
            return None
        parts = []
        for b, k in zip(by_stripe, share(add_n, [s1 - s0 + 1 for s0, s1 in stripes])):
            parts += list(zip(b, share(k, [r1 - r0 + 1 for r0, r1 in b])))
        return parts

    plans = []   # (axis, parts, add, what it is), the first that works is used
    if build == "bands":         # vertical bands keep their widths: only rows change
        plans = [(0, proportional(rows_b, add_n, True) if wide else proportional(rows_b, trim_n, False), wide, "bands")]
    elif build == "stripes":     # horizontal stripes: lengthened, or made taller if every stripe can be
        if wide:
            plans = [(0, stripes_taller(), True, "stripes made taller"),
                     (1, proportional([c for c in cols_s if c[0] == 0 or c[1] == w - 1], trim_n, False)
                      if any(c[0] == 0 or c[1] == w - 1 for c in cols_s) else None, False,
                      "stripes shortened at the ends")]
        else:
            plans = [(1, proportional(cols_s, add_n, True), True, "stripes lengthened")]
    elif build == "field":       # an emblem on a field: plain field taken out, else added
        if wide:
            plans = [(1, proportional(uni_cols, trim_n, False) if uni_cols else None, False, "a field round the emblem"),
                     (0, proportional(uni_rows, add_n, True) if uni_rows else None, True, "a field round the emblem")]
        else:
            plans = [(0, proportional(uni_rows, trim_n, False) if uni_rows else None, False, "a field round the emblem"),
                     (1, proportional(uni_cols, add_n, True) if uni_cols else None, True, "a field round the emblem")]
    if how != "auto":
        plans = [p for p in plans if p[2] == (how == "add")]
    for axis, parts, add, what in plans:
        if parts:
            n = sum(k for _, k in parts)
            where = ", ".join(f"{k} in {'rows' if axis == 0 else 'columns'} {r0}-{r1}" for (r0, r1), k in parts if k)
            return resize_lines(a, axis, parts, add), (
                f"{'too wide' if wide else 'too tall'}, {what}: {n} plain {'rows' if axis == 0 else 'columns'} "
                f"{'added' if add else 'taken out'} ({where})")
    why = {"mixed": "plain lines cross its patterns both ways (quarters, a cross ...)",
           "field": "its plain field is too narrow", "bands": "its bands have too little plain length",
           "stripes": "not every stripe has plain rows, and its ends are too short"}[build]
    if not rows and not cols:
        why = "it has no plain stretch" + (" besides its border" if edge else "")
    return None, f"{'too wide' if wide else 'too tall'}: {why}"


def sheet(src, out, path):
    """the picture as sent, the fitted flag, and the flag as the game shows it (82 x 52, three times larger)"""
    H = 240
    a = Image.fromarray(src).convert("RGB")
    b = Image.fromarray(out).convert("RGB")
    a = a.resize((round(a.width * H / a.height), H), Image.LANCZOS)
    b = b.resize((round(b.width * H / b.height), H), Image.LANCZOS)
    g = Image.fromarray(out).convert("RGB").resize((82, 52), Image.LANCZOS).resize((246, 156), Image.NEAREST)
    c = Image.new("RGB", (40 + a.width + 40 + b.width + 40 + g.width + 40, H + 70), (31, 34, 38))
    xs = [40, 40 + a.width + 40, 40 + a.width + 40 + b.width + 40]
    for x, im in zip(xs, (a, b, g)):
        c.paste(im, (x, 50))
    d = ImageDraw.Draw(c)
    try:
        f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
    except OSError:
        f = ImageFont.load_default()
    for x, t in zip(xs, ("as sent", f"fitted {out.shape[1]} x {out.shape[0]} (82:52)", "in game, 82 x 52 (x3)")):
        d.text((x, 20), t, font=f, fill=(230, 228, 218))
    c.save(path)


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("tag")
    p.add_argument("picture")
    p.add_argument("--ideology", help="the flag of one government: TAG_<ideology>.png")
    p.add_argument("--frame", default="auto", help="auto, or the frame's width in px to crop (0: none)")
    p.add_argument("--how", default="auto", choices=("auto", "trim", "add"),
                   help="force the way: trim (take plain lines out of the long side) or add (repeat plain lines "
                        "along the short side)")
    p.add_argument("--tol", type=float, default=24, help="how far two lines may differ and still be one plain line")
    p.add_argument("--out", help="where to write it (default source/flags/TAG[_ideology].png)")
    p.add_argument("--dry", action="store_true", help="only the sheet")
    o = p.parse_args()
    a = np.asarray(Image.open(o.picture).convert("RGBA"))
    a, k = frame(a, o.frame, o.tol)
    if k:
        print(f"a {k} px frame cropped")
    if (a[..., 3] < 255).any():
        print("note: see-through pixels made solid (the game shows them as holes)")
        a = a.copy()
        a[..., 3] = 255
    out, note = fit(a, o.how, o.tol)
    print(f"{o.picture}: {a.shape[1]} x {a.shape[0]}: {note}")
    if out is None:
        sys.exit("not fitted: fit this flag by hand (see the docstring for the rules)")
    name = f"{o.tag}_{o.ideology}" if o.ideology else o.tag
    shot = Path("work") / f"flag_fit_{name}.png"
    shot.parent.mkdir(exist_ok=True)
    sheet(a, out, shot)
    print(f"sheet: {shot}")
    if not o.dry:
        dst = Path(o.out or f"source/flags/{name}.png")
        Image.fromarray(out, "RGBA").save(dst)
        print(f"wrote {dst} ({out.shape[1]} x {out.shape[0]})")


if __name__ == "__main__":
    main()
