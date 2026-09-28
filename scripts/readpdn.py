"""Decode the author's paint.net (.pdn) file into one RGBA array per layer.

A .pdn file is: b'PDN3', a 3-byte little-endian header length, an XML header
(<pdnImage width=.. height=.. layers=..>), then a .NET BinaryFormatter object graph
describing the document and its layers, terminated by a MessageEnd record (0x0B).
After the graph comes the pixel data of every layer, in layer order (bottom first):

    formatVersion  u8       0 = gzip-compressed chunks
    chunkSize      u32 BE   262144
    then ceil(width*height*4 / chunkSize) chunks, in any order:
        chunkNumber u32 BE, dataSize u32 BE, <dataSize bytes of gzip>

Pixels are BGRA, rows packed with stride width*4. We only read layer names out of
the graph (they are plain length-prefixed strings) rather than parsing it fully.

Usage: python3 readpdn.py source.pdn outdir
Writes outdir/layer<i>.npy (H x W x 4, RGBA uint8) and outdir/layers.txt.
"""
import re
import struct
import sys
import zlib
from pathlib import Path

import numpy as np

LAYER_NAME_ANCHOR = b"PaintDotNet.LayerBlendMode"


def read_header(buf):
    if buf[:4] != b"PDN3":
        raise ValueError("not a PDN3 file")
    n = buf[4] | (buf[5] << 8) | (buf[6] << 16)
    xml = buf[7:7 + n].decode("utf-8")
    w = int(re.search(r'width="(\d+)"', xml).group(1))
    h = int(re.search(r'height="(\d+)"', xml).group(1))
    nl = int(re.search(r'layers="(\d+)"', xml).group(1))
    return w, h, nl, 7 + n


def layer_names(buf, start, count):
    """Layer names are BinaryObjectString records (0x06, id, 7-bit length, utf8)
    that appear after the LayerProperties class definition, in layer order."""
    names = []
    pos = buf.find(b"blendMode", start)
    end = buf.find(b"\x0b\x00\x00\x04\x00\x00", pos)
    i = pos
    while i < end and len(names) < count:
        if buf[i] == 0x06:
            ln = buf[i + 5]
            if 0 < ln < 128 and i + 6 + ln <= end:
                s = buf[i + 6:i + 6 + ln]
                try:
                    t = s.decode("utf-8")
                except UnicodeDecodeError:
                    t = None
                if t and t.isprintable() and not t.startswith("PaintDotNet") and t not in (
                        "value__",):
                    names.append(t)
                    i += 6 + ln
                    continue
        i += 1
    return names


def main(src, outdir):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    buf = Path(src).read_bytes()
    w, h, nl, graph_start = read_header(buf)
    names = layer_names(buf, graph_start, nl)
    print(f"{w}x{h}, {nl} layers: {names}")
    # End of the object graph: MessageEnd (0x0B) followed by the first layer's
    # format byte (0) and chunk size (262144, big-endian).
    pos = buf.find(b"\x0b\x00\x00\x04\x00\x00", graph_start) + 1
    length = w * h * 4
    for li in range(nl):
        fmt = buf[pos]
        chunk = struct.unpack(">I", buf[pos + 1:pos + 5])[0]
        pos += 5
        if fmt != 0:
            raise ValueError(f"layer {li}: unsupported format byte {fmt}")
        nchunks = (length + chunk - 1) // chunk
        out = np.empty(length, dtype=np.uint8)
        for _ in range(nchunks):
            num, size = struct.unpack(">II", buf[pos:pos + 8])
            pos += 8
            data = zlib.decompress(buf[pos:pos + size], 16 + zlib.MAX_WBITS)
            pos += size
            out[num * chunk:num * chunk + len(data)] = np.frombuffer(data, np.uint8)
        img = out.reshape(h, w, 4)[:, :, [2, 1, 0, 3]]  # BGRA -> RGBA
        np.save(outdir / f"layer{li}.npy", img)
        print(f"layer {li} '{names[li] if li < len(names) else '?'}' decoded")
    if pos != len(buf):
        print(f"warning: {len(buf) - pos} trailing bytes")
    (outdir / "layers.txt").write_text("\n".join(names) + "\n")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
