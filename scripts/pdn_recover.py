"""Get the layers out of a damaged paint.net file (2026-10-17: the author's latest flag file "is corrupted").

paint.net stores each layer's pixels as gzip chunks after the document's object graph (readpdn.py). A damaged graph
or a few broken chunks make paint.net refuse the whole file, but every chunk that is still whole holds its piece of
its layer. This reads what it can: the size and the layer names from the header and the graph when they are readable,
then every chunk, layer by layer, re-finding the next chunk after a broken one.

    python3 scripts/pdn_recover.py BROKEN.pdn OUTDIR [--size WxH] [--like GOOD.pdn]

writes OUTDIR/NN_<layer name>.png (whole layers, and broken ones with their lost parts see-through) and
OUTDIR/report.txt; --like takes the size and the layer names from an older good copy of the same file when the
broken one's header or graph is gone. `pdn_check.py` says what is wrong with a file; this saves what is left.
The PNGs can go straight to `import_flags.py`'s folder mode or back into paint.net as layers.
"""
import argparse
import re
import struct
import zlib
from pathlib import Path

import numpy as np
from PIL import Image

import readpdn

LAYER_HEAD = b"\x00\x00\x04\x00\x00"   # format 0, then the chunk size 262144 (big-endian)
CHUNK = 262144


def header(b):
    try:
        w, h, nl, g0 = readpdn.read_header(b)
        return w, h, nl, g0
    except Exception:  # noqa: BLE001 - a broken header is what we are here for
        return None


def names_of(b, g0, nl):
    try:
        from nrbf import Graph
        g = Graph(b, g0 + 2)
        props = [r for r in g.records if r[0] in ("class", "classid") and r[3][1] == "PaintDotNet.Layer+LayerProperties"]
        out = []
        for r in props:
            v = dict(zip(g.meta[r[3][2]][1], r[3][3]))
            s = g.records[v["name"][1]]
            out.append(s[3][1] if s[0] == "string" else g.records[g.objects[s[3]]][3][1])
        return out, g.records[-1][2]
    except Exception:  # noqa: BLE001
        names = readpdn.layer_names(b, g0, nl)
        end = b.find(b"\x0b" + LAYER_HEAD, g0)
        return names, (end + 1 if end >= 0 else None)


def chunks(b, start, total):
    """(layer, chunk index, pixels) for every whole chunk from start on; a new layer begins at each layer header"""
    nch = -(-total // CHUNK)
    p, layer, found, lost = start, -1, [], 0
    while p < len(b):
        if b[p:p + 5] == LAYER_HEAD and (layer < 0 or b[p + 13:p + 15] == b"\x1f\x8b"):
            layer, p = layer + 1, p + 5
            continue
        ok = False
        if p + 8 <= len(b) and layer >= 0:
            idx, ln = struct.unpack(">II", b[p:p + 8])
            if idx < nch and 0 < ln < 4 * CHUNK and b[p + 8:p + 10] == b"\x1f\x8b":
                try:
                    data = zlib.decompress(b[p + 8:p + 8 + ln], 16 + zlib.MAX_WBITS)
                    if len(data) == min(CHUNK, total - idx * CHUNK):
                        found.append((layer, idx, data))
                        p += 8 + ln
                        ok = True
                except zlib.error:
                    pass
        if not ok:  # broken: on to the next thing that looks like a chunk or a layer
            lost += 1
            nxt = [q for q in (b.find(b"\x1f\x8b\x08", p + 9) - 8, b.find(LAYER_HEAD, p + 1)) if q > p]
            if not nxt:
                break
            p = min(nxt)
    return found, lost


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdn")
    ap.add_argument("out")
    ap.add_argument("--size", help="WxH, when the header is gone")
    ap.add_argument("--like", help="an older good copy of the file: its size and layer names")
    a = ap.parse_args()
    b = Path(a.pdn).read_bytes()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    report = []
    hd = header(b)
    names, start = [], None
    if hd:
        w, h, nl, g0 = hd
        names, start = names_of(b, g0, nl)
        report.append(f"header: {w}x{h}, {nl} layers")
    if a.like:
        lb = Path(a.like).read_bytes()
        w, h, nl, lg0 = readpdn.read_header(lb)
        like_names, _ = names_of(lb, lg0, nl)
        if not names or len(names) < len(like_names):
            names = like_names
        report.append(f"size and names from {a.like}: {w}x{h}, {nl} layers")
    if a.size:
        w, h = map(int, a.size.lower().split("x"))
    if not (hd or a.like or a.size):
        raise SystemExit("the header is unreadable: give --size WxH or --like an older copy")
    if start is None:  # the graph's end is lost: the first layer header followed by a chunk
        m = re.search(re.escape(LAYER_HEAD) + b"\x00\x00\x00\x00.{4}\x1f\x8b", b, re.S)
        start = m.start() if m else 0
        report.append("the graph's end was not found; reading from the first chunk")
    total = 4 * w * h
    found, lost = chunks(b, start, total)
    nch = -(-total // CHUNK)
    layers = {}
    for layer, idx, data in found:
        buf, have = layers.setdefault(layer, (np.zeros(total, np.uint8), set()))
        buf[idx * CHUNK:idx * CHUNK + len(data)] = np.frombuffer(data, np.uint8)
        have.add(idx)
    for k in sorted(layers):
        buf, have = layers[k]
        img = buf.reshape(h, w, 4)[:, :, [2, 1, 0, 3]]
        name = names[k] if k < len(names) else f"Layer {k + 1}"
        safe = re.sub(r'[\\/:*?"<>|]', "_", name)
        Image.fromarray(img).save(out / f"{k:02d}_{safe}.png")
        report.append(f"layer {k:2d} {name!r}: " + ("whole" if len(have) == nch else f"{len(have)} of {nch} chunks"))
    want = len(names) or (hd[2] if hd else len(layers))
    missing = [names[k] if k < len(names) else k for k in range(want) if k not in layers]
    if missing:
        report.append(f"no pixels found for: {missing}")
    if lost:
        report.append(f"{lost} broken places skipped")
    (out / "report.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))


if __name__ == "__main__":
    main()
