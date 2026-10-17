"""What changed between two copies of the map's .pdn, layer by layer and place by place: the first job when the author
sends a new upload (2026-10-17, the efficiency night: until then this was done by eye, layer by layer).

    python3 scripts/pdn_diff.py OLD.pdn NEW.pdn [--out DIR]

prints, for every layer: added, removed or renamed layers; how many pixels changed and where (each place a box and a
centre pixel, biggest first); on Countries, which nations gained or lost land; on the line layers (Necessary ...), the
pixels drawn and erased. Then the borders to act on: every area the new Necessary Borders lines enclose that holds two
nations' colours, near a line that changed (a border moved through a nation, or a merge), with the shares of each, so
`pdn_tools.py border` / `cede` / `owners` can follow. And writes into DIR (default work/pdn_diff/):
    overview.png      the world at 1/4, every change coloured by its kind of layer, the places numbered
    place_NN.png      each place before and after side by side (the Countries layer's colours, the lines and the
                      labels over them, 2x), for reading the author's new labels and lines
    report.txt        what was printed
No layer is written to disk decoded: each file's layers are found by walking their chunk headers and decoded one at a
time (two 52 MB arrays in memory at once), so a diff takes about a minute and no disk space.
"""
import argparse
import re
import struct
import zlib
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

import readpdn
from common import COUNTRIES

KIND = [  # layer name pattern -> (kind, colour on the overview)
    (r"Borders", ("country lines", (220, 30, 40))),
    (r"Necessary States|Necessary Provinces$", ("state and province lines", (255, 140, 0))),
    (r"Rivers", ("rivers", (30, 110, 230))),
    (r"Cities", ("cities", (220, 0, 200))),
    (r"Names|Subnames", ("labels", (0, 150, 60))),
    (r"Subregions", ("subregions", (140, 70, 200))),
    (r"Should be an island|Islands to Add", ("islands", (0, 190, 190))),
    (r"^(Provinces|States|Countries|Strategic Regions|Continents|Terrain|Heightmap|Ocean Province Lines)$",
     ("game layers", (120, 120, 120))),
]
LINE_LAYERS = r"^Necessary|Should be an island|Subnames|Ocean Province Lines"
PLACE_GAP = 12      # changed pixels this close are one place
MAX_PLACES = 24


def index(path):
    """(width, height, layer names, the byte offset of each layer's pixel data, the file's bytes)"""
    b = Path(path).read_bytes()
    w, h, nl, g0 = readpdn.read_header(b)
    names = readpdn.layer_names(b, g0, nl)
    pos = b.find(b"\x0b\x00\x00\x04\x00\x00", g0) + 1
    offs, total = [], w * h * 4
    for _ in range(nl):
        offs.append(pos)
        chunk = struct.unpack(">I", b[pos + 1:pos + 5])[0]
        pos += 5
        for _ in range(-(-total // chunk)):
            ln = struct.unpack(">I", b[pos + 4:pos + 8])[0]
            pos += 8 + ln
    return w, h, names, offs, b


def decode(b, off, w, h):
    total = w * h * 4
    chunk = struct.unpack(">I", b[off + 1:off + 5])[0]
    out = np.empty(total, np.uint8)
    pos = off + 5
    for _ in range(-(-total // chunk)):
        num, ln = struct.unpack(">II", b[pos:pos + 8])
        data = zlib.decompress(b[pos + 8:pos + 8 + ln], 16 + zlib.MAX_WBITS)
        out[num * chunk:num * chunk + len(data)] = np.frombuffer(data, np.uint8)
        pos += 8 + ln
    return out.reshape(h, w, 4)[:, :, [2, 1, 0, 3]]


def kind_of(name):
    for pat, k in KIND:
        if re.search(pat, name):
            return k
    return ("reference and notes", (190, 190, 120))


def code(a):
    a = a.astype(np.int64)
    return (a[..., 0] << 16) | (a[..., 1] << 8) | a[..., 2]


def places(mask):
    """boxes of the changed pixels, biggest first: (y0, y1, x0, x1, changed px)"""
    small = mask[::4, ::4] | mask[1::4, ::4] | mask[::4, 1::4]
    grown = ndi.binary_dilation(small, iterations=max(1, PLACE_GAP // 4))
    lab, n = ndi.label(grown)
    out = []
    for i, sl in enumerate(ndi.find_objects(lab), 1):
        y0, y1, x0, x1 = sl[0].start * 4, sl[0].stop * 4, sl[1].start * 4, sl[1].stop * 4
        out.append((y0, y1, x0, x1, int(mask[y0:y1, x0:x1].sum())))
    return sorted(out, key=lambda p: -p[4])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("old")
    ap.add_argument("new")
    ap.add_argument("--out", default="work/pdn_diff")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for f in out.glob("place_*.png"):
        f.unlink()
    lines = []

    def say(s=""):
        print(s)
        lines.append(s)

    W, H, on, ooff, ob = index(a.old)
    w, h, nn, noff, nb = index(a.new)
    if (W, H) != (w, h):
        raise SystemExit(f"the sizes differ: {W}x{H} and {w}x{h}")
    say(f"{a.old}: {len(on)} layers; {a.new}: {len(nn)} layers ({w}x{h})")
    added = [n for n in nn if n not in on]
    gone = [n for n in on if n not in nn]
    if added:
        say("layers added: " + ", ".join(added))
    if gone:
        say("layers removed or renamed: " + ", ".join(gone))
    order_old = [n for n in on if n in nn]
    order_new = [n for n in nn if n in on]
    if order_old != order_new:
        say("layers in a new order")
    tag_of = {c[3]: c[0] for c in COUNTRIES.values()}
    tag_code = {(r << 16) | (g << 8) | bb: t for (r, g, bb), t in tag_of.items()}

    overview = None
    every = np.zeros((h, w), bool)
    keep = {}
    for name in nn:
        new = decode(nb, noff[nn.index(name)], w, h)
        if name == "Terrain":
            t = new[..., :3]
            land = ~((t == (8, 31, 130)).all(-1) | (t == (55, 90, 220)).all(-1))
            keep["land"] = land
            ov = np.where(land[::4, ::4, None], np.uint8(214), np.uint8(240)).repeat(3, axis=2)
            overview = ov.copy()
        if name in ("Countries", "Necessary Borders", "Necessary Names", "Necessary States"):
            keep["new " + name] = new
        if name not in on:
            mask = new[..., 3] > 0
            say(f"\n{name} (new layer): {int(mask.sum())} painted pixels")
            k = kind_of(name)
        else:
            old = decode(ob, ooff[on.index(name)], w, h)
            if name in ("Countries", "Necessary Borders", "Necessary Names", "Necessary States"):
                keep["old " + name] = old
            if re.search(LINE_LAYERS, name):  # lines and labels: where the paint is, not its exact colour
                was, now = old[..., 3] > 0, new[..., 3] > 0
                mask = was != now
                if not mask.any():
                    continue
                k = kind_of(name)
                say(f"\n{name} ({k[0]}): {int((now & ~was).sum())} px drawn, {int((was & ~now).sum())} px erased")
            else:
                mask = (old != new).any(-1)
                if not mask.any():
                    continue
                k = kind_of(name)
                say(f"\n{name} ({k[0]}): {int(mask.sum())} px changed")
                if name == "Countries":
                    oc, nc = code(old[..., :3]), code(new[..., :3])
                    lost = Counter(oc[mask].tolist())
                    won = Counter(nc[mask].tolist())
                    for c in sorted(set(lost) | set(won), key=lambda c: -(won.get(c, 0) + lost.get(c, 0)))[:30]:
                        say(f"  {tag_code.get(c, f'#{c:06x}')}: +{won.get(c, 0)} -{lost.get(c, 0)} px")
            del old
        every |= mask
        if overview is not None:
            m4 = mask[::4, ::4] | mask[1::4, ::4] | mask[::4, 1::4] | mask[1::4, 1::4]
            overview[m4] = k[1]
        for y0, y1, x0, x1, n in places(mask)[:8]:
            say(f"  at x {x0}-{x1}, y {y0}-{y1} (centre {(x0 + x1) // 2},{(y0 + y1) // 2}): {n} px")
        del new

    # the places, numbered: before and after of the Countries colours with the lines and labels over them
    pl = places(every)[:MAX_PLACES]
    say(f"\n{len(places(every))} places changed; the biggest {len(pl)} are drawn in {out}/place_NN.png")

    def composite(side, y0, y1, x0, x1):
        img = keep.get(f"{side} Countries")
        img = img[y0:y1, x0:x1, :3].copy() if img is not None else np.full((y1 - y0, x1 - x0, 3), 200, np.uint8)
        land = keep["land"][y0:y1, x0:x1] if "land" in keep else np.ones(img.shape[:2], bool)
        img[~land] = (150, 175, 200)
        img = (img * 0.55 + 255 * 0.45).astype(np.uint8)  # pale, so the lines read
        for lay, col in (("Necessary States", (255, 140, 0)), ("Necessary Borders", (200, 0, 0)), ("Necessary Names", (0, 0, 0))):
            src = keep.get(f"{side} {lay}")
            if src is not None:
                img[src[y0:y1, x0:x1, 3] > 0] = col
        return img

    pic = Image.fromarray(overview) if overview is not None else None
    dr = ImageDraw.Draw(pic) if pic else None
    for k, (y0, y1, x0, x1, n) in enumerate(pl, 1):
        m = 24
        y0, y1, x0, x1 = max(0, y0 - m), min(h, y1 + m), max(0, x0 - m), min(w, x1 + m)
        if (y1 - y0) * (x1 - x0) > 900 * 900:  # a big place: its middle at full size
            cy, cx = (y0 + y1) // 2, (x0 + x1) // 2
            y0, y1, x0, x1 = max(0, cy - 450), min(h, cy + 450), max(0, cx - 450), min(w, cx + 450)
        b4, af = composite("old", y0, y1, x0, x1), composite("new", y0, y1, x0, x1)
        sep = np.full((b4.shape[0], 6, 3), 255, np.uint8)
        both = Image.fromarray(np.concatenate([b4, sep, af], 1))
        if both.width < 1400:
            both = both.resize((both.width * 2, both.height * 2), Image.NEAREST)
        both.save(out / f"place_{k:02d}.png")
        if dr:
            dr.rectangle([x0 // 4, y0 // 4, x1 // 4, y1 // 4], outline=(0, 0, 0))
            dr.text((x0 // 4 + 2, y0 // 4 + 1), str(k), fill=(0, 0, 0))
        say(f"  {k:2d}: x {x0}-{x1}, y {y0}-{y1}, {n} px changed")
    if pic:
        pic.save(out / "overview.png")

    # the borders to act on: areas the new country lines enclose that hold two nations' colours, near a changed line
    if "new Necessary Borders" in keep and "new Countries" in keep and "land" in keep:
        nbl = keep["new Necessary Borders"][..., 3] > 0
        obl = keep["old Necessary Borders"][..., 3] > 0 if "old Necessary Borders" in keep else nbl
        near = ndi.binary_dilation(nbl != obl, iterations=10)
        cells, _ = ndi.label(keep["land"] & ~nbl, np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]))
        cc = code(keep["new Countries"][..., :3])
        todo = []
        for i in np.unique(cells[near & (cells > 0)]):
            m = cells == i
            if m.sum() < 50:
                continue
            share = Counter(cc[m].tolist()).most_common()
            if len(share) > 1 and share[1][1] >= max(100, 0.03 * m.sum()):
                ys, xs = np.nonzero(m)
                j = len(ys) // 2
                todo.append((int(m.sum()), int(xs[j]), int(ys[j]), share[:4]))
        say(f"\n{len(todo)} areas inside the new country lines hold two nations' colours (a moved border or a merge):")
        for n, x, y, share in sorted(todo, reverse=True):
            say(f"  area at ({x}, {y}), {n} px: " + ", ".join(f"{tag_code.get(c, f'#{c:06x}')} {v}" for c, v in share))
    (out / "report.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
