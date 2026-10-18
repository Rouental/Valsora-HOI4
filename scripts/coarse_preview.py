"""A preview, not in the mod: the provinces inside the areas the author marked as tundra, extreme desert and jungle
re-cut coarse, at a few sizes, with what each frees under HOI4's border limit (2026-10-18, the author: "I tried
marking out areas which I know will be either tundra or extreme desert or jungle like base game africa. Maybe try
generating provinces in those area with this in mind? Just a snapshot / preview, not for the full mod").

    python3 scripts/readpdn.py UPLOAD.pdn DIR        # the upload's layers, decoded
    python3 scripts/coarse_preview.py DIR [--sizes 500,800,1500] [--out work/coarse_preview]

The areas are the layer "Desert": closed outlines in red (extreme desert) and green (jungle) mean the land inside
them; white lines (tundra) run from coast to coast and mean the land they cut off from the rest. A province goes
with an area when most of it lies inside; each state's share of the areas is cut again into pieces of about the
size given (never more pieces than it had), the state itself unchanged, so its strategic region holds. States with
the author's own province lines (Necessary Provinces) are left alone. Writes report.txt and one picture per place:
the provinces as they are, then at each size.
"""
import argparse
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

import borders
from apply_outlines import organic_split
from pdn_tools import CROSS, LAKES, OCEAN, code, unfour

KINDS = (("desert", (255, 0, 0), "outline"), ("jungle", (0, 127, 14), "outline"), ("tundra", (255, 255, 255), "line"))
TINT = {"desert": (236, 170, 90), "jungle": (70, 170, 90), "tundra": (250, 252, 255)}
CUT_OFF = 60000   # a coastal piece a tundra line cuts off is smaller than this; the rest of the land is not


def areas(D, land):
    out = {}
    for name, col, how in KINDS:
        line = (D[..., 3] > 0) & (D[..., :3] == col).all(-1)
        if how == "outline":
            m = ndi.binary_fill_holes(line)
        else:
            lab, _ = ndi.label(land & ~ndi.binary_dilation(line), CROSS)
            sizes = np.bincount(lab.ravel())
            near = np.unique(lab[ndi.binary_dilation(line, iterations=3)])
            m = line | np.isin(lab, [t for t in near if t and sizes[t] < CUT_OFF])
        out[name] = m & land
    return out


def recut(P, St, land, inside, locked, size):
    """P cut again where `inside`; returns the new map and how many provinces went to how many"""
    P = P.copy()
    lp = np.where(land, P, -1)
    u, inv = np.unique(lp, return_inverse=True)
    inv = inv.reshape(P.shape)
    share = np.bincount(inv.ravel(), weights=inside.ravel()) / np.bincount(inv.ravel())
    pooled = np.isin(inv, np.nonzero((share > 0.5) & (u >= 0))[0])
    before = after = 0
    lab, n = ndi.label(pooled, CROSS)
    for i, sl in enumerate(ndi.find_objects(lab), 1):
        win = np.s_[max(sl[0].start - 2, 0):sl[0].stop + 2, max(sl[1].start - 2, 0):sl[1].stop + 2]
        comp = lab[win] == i
        for s in np.unique(St[win][comp]):
            if s in locked:
                continue
            m = comp & (St[win] == s)
            part, k2 = ndi.label(m, CROSS)
            for j in range(1, k2 + 1):
                ys, xs = np.nonzero(part == j)
                cols = sorted(set(P[win][ys, xs].tolist()))
                k = min(len(cols), max(1, int(round(len(ys) / size))))
                pieces = organic_split(ys, xs, k, seed=int(s) % 100003)
                ks = np.unique(pieces)
                P[win][ys, xs] = np.array(cols[:len(ks)])[np.searchsorted(ks, pieces)]
                unfour(P[win], set(cols))
                before += len(cols)
                after += len(ks)
    return P, before, after


def edges(a, scale):
    """the pixels of an upscaled map where it changes, one line wide"""
    a = np.repeat(np.repeat(a, scale, 0), scale, 1)
    e = np.zeros(a.shape, bool)
    e[:, 1:] |= a[:, 1:] != a[:, :-1]
    e[1:] |= a[1:] != a[:-1]
    return e


def draw(P, St, K, land, inside_kind, box, scale):
    """the countries' colours, pale outside the marked areas, the areas tinted by kind and edged; province lines grey,
    state lines dark, country lines red"""
    x0, y0, x1, y1 = box
    sl = np.s_[y0:y1, x0:x1]
    k = K[sl]
    img = np.stack([(k >> 16) & 255, (k >> 8) & 255, k & 255], -1).astype(float)
    img = img * 0.5 + 127
    for name, m in inside_kind.items():
        a = m[sl]
        img[a] = img[a] * 0.4 + np.array(TINT[name]) * 0.6
    img[~land[sl]] = (198, 212, 228)
    img = np.repeat(np.repeat(img.astype(np.uint8), scale, 0), scale, 1)
    img[edges(np.where(land[sl], P[sl], -1), scale)] = (95, 90, 85)
    img[edges(np.where(land[sl], St[sl], -1), scale)] = (25, 25, 25)
    img[edges(np.where(land[sl], K[sl], -1), scale)] = (200, 30, 30)
    for name, m in inside_kind.items():
        e = edges(m[sl], scale)
        img[e] = np.array(TINT[name]) * 0.6
    return Image.fromarray(img)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("layers")
    ap.add_argument("--sizes", default="500,800,1500")
    ap.add_argument("--out", default="work/coarse_preview")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    names = (Path(a.layers) / "layers.txt").read_text().splitlines()
    lay = lambda nm: np.load(Path(a.layers) / f"layer{names.index(nm)}.npy")  # noqa: E731
    t = lay("Terrain")[..., :3]
    land = ~((t == OCEAN).all(-1) | (t == LAKES).all(-1))
    P = code(lay("Provinces")[..., :3])
    S = lay("States")
    St = np.where(S[..., 3] > 0, code(S[..., :3]), -1)
    K = code(lay("Countries")[..., :3])
    locked = set(np.unique(St[(lay("Necessary Provinces")[..., 3] > 0) & land]).tolist()) - {-1}
    kinds = areas(lay("Desert"), land)
    inside = np.zeros_like(land)
    for m in kinds.values():
        inside |= m
    base = borders.count(P)[1]
    lines = [f"marked land: " + ", ".join(f"{nm} {m.sum():,} px" for nm, m in kinds.items()),
             f"province borders on the layer now: {base:,}"]
    maps = {}
    for size in map(int, a.sizes.split(",")):
        Q, before, after = recut(P, St, land, inside, locked, size)
        b = borders.count(Q)[1]
        maps[size] = Q
        lines.append(f"provinces of about {size} px: {before} provinces in the areas become {after}; "
                     f"borders {b:,} ({b - base:+,}), room for about {(base - b) // 3:,} provinces elsewhere")
    lab, n = ndi.label(ndi.binary_dilation(inside, iterations=30))
    for i, sl in enumerate(ndi.find_objects(lab), 1):
        y0, y1 = max(sl[0].start, 0), sl[0].stop
        x0, x1 = max(sl[1].start, 0), sl[1].stop
        scale = 2
        box = (x0, y0, x1, y1)
        panels = [draw(P, St, K, land, kinds, box, scale)] + [draw(maps[s], St, K, land, kinds, box, scale)
                                                              for s in maps]
        titles = ["As now"] + [f"Provinces of about {s} px" for s in maps]
        cols = 1 if (x1 - x0) > 2 * (y1 - y0) else 2   # a long strip: the panels stacked, else two by two
        w, h = panels[0].size
        rows = (len(panels) + cols - 1) // cols
        sheet = Image.new("RGB", ((w + 10) * cols - 10, (h + 28) * rows), "white")
        from PIL import ImageDraw, ImageFont
        try:
            font = ImageFont.truetype("deco_ui/source_fonts/josefinsans/JosefinSans[wght].ttf", 18)
        except OSError:
            font = ImageFont.load_default()
        d = ImageDraw.Draw(sheet)
        for j, (pn, tt) in enumerate(zip(panels, titles)):
            ox, oy = (j % cols) * (w + 10), (j // cols) * (h + 28)
            d.text((ox + 4, oy + 4), tt, fill=(0, 0, 0), font=font)
            sheet.paste(pn, (ox, oy + 28))
        f = out / f"place_{i:02d}.png"
        sheet.save(f)
        lines.append(f"{f.name}: x {x0}-{x1}, y {y0}-{y1}")
    (out / "report.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
