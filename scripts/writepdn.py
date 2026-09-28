"""Write a paint.net (.pdn) file by reusing another .pdn's structure.

A .pdn stores its document as a .NET object graph followed by each layer's pixels.
Rather than generate that graph, we copy the template's (same layer count, names,
blend modes and visibility) and patch the size fields: the image and every layer
and surface width/height (int32), each surface's row stride (int32) and each pixel
buffer's length (int64). Then the new pixels follow in paint.net's chunk format
(see readpdn.py). The layer count and names therefore always match the template.
"""
import base64
import gzip
import io
import re
import struct

import numpy as np
from PIL import Image

CHUNK = 262144


def _patch(graph, old, new, fmt, expect):
    a, b = struct.pack(fmt, old), struct.pack(fmt, new)
    hits = graph.count(a)
    if hits != expect:
        raise ValueError(f"expected {expect} {fmt} fields equal to {old}, found {hits}")
    return graph.replace(a, b)


def write_pdn(template, out, layers):
    """layers: list of HxWx4 uint8 RGBA arrays, bottom layer first."""
    buf = open(template, "rb").read()
    n = buf[4] | (buf[5] << 8) | (buf[6] << 16)
    xml = buf[7:7 + n].decode("utf-8")
    ow = int(re.search(r'width="(\d+)"', xml).group(1))
    oh = int(re.search(r'height="(\d+)"', xml).group(1))
    nl = int(re.search(r'layers="(\d+)"', xml).group(1))
    if len(layers) != nl:
        raise ValueError(f"template has {nl} layers, got {len(layers)}")
    h, w = layers[0].shape[:2]
    g0 = 7 + n
    g1 = buf.find(b"\x0b\x00\x00\x04\x00\x00", g0) + 1  # MessageEnd, then layer data
    graph = buf[g0:g1]
    graph = _patch(graph, ow, w, "<i", 2 * nl + 1)
    graph = _patch(graph, oh, h, "<i", 2 * nl + 1)
    graph = _patch(graph, ow * 4, w * 4, "<i", nl)
    graph = _patch(graph, ow * oh * 4, w * h * 4, "<q", nl)

    # header: new size and a thumbnail of the flattened image
    flat = Image.new("RGBA", (w, h))
    for lay in layers:
        flat = Image.alpha_composite(flat, Image.fromarray(lay))
    thumb = flat.resize((256, 128), Image.BOX)
    png = io.BytesIO()
    thumb.save(png, "PNG")
    xml = re.sub(r'width="\d+"', f'width="{w}"', xml, count=1)
    xml = re.sub(r'height="\d+"', f'height="{h}"', xml, count=1)
    xml = re.sub(r'png="[^"]*"', 'png="' + base64.b64encode(png.getvalue()).decode() + '"', xml)
    hdr = xml.encode("utf-8")

    with open(out, "wb") as f:
        f.write(b"PDN3" + bytes([len(hdr) & 255, (len(hdr) >> 8) & 255, len(hdr) >> 16]))
        f.write(hdr)
        f.write(graph)
        for lay in layers:
            data = np.ascontiguousarray(lay[:, :, [2, 1, 0, 3]]).tobytes()  # RGBA -> BGRA
            f.write(b"\x00" + struct.pack(">I", CHUNK))
            for k in range(0, len(data), CHUNK):
                z = gzip.compress(data[k:k + CHUNK], compresslevel=6)
                f.write(struct.pack(">II", k // CHUNK, len(z)))
                f.write(z)
