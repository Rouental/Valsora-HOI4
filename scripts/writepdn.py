"""Write a paint.net (.pdn) file by reusing another .pdn's structure.

A .pdn stores its document as a .NET object graph followed by each layer's pixels.
Rather than generate that graph, we copy the template's (same layer count, names,
blend modes and visibility) and patch the size fields: the image and every layer
and surface width/height (int32), each surface's row stride (int32) and each pixel
buffer's length (int64). Then the new pixels follow in paint.net's chunk format
(see readpdn.py). The layer count and names therefore match the template, unless more
layers are given: those are added on top (2026-10-13, four new flags for the author's
flag file), as copies of the template's top layer's objects with new ids (nrbf.py reads
the graph).
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


def _set_layer_props(graph, names, visible, opacity):
    """Rewrite each layer's name, visibility and opacity. In the graph a name is a
    BinaryObjectString (0x06, object id, length byte, UTF-8), followed by a 5-byte
    reference to its metadata list and then three bytes: visible, isBackground,
    opacity. The stream has no byte offsets, so a name may change length."""
    out, pos = bytearray(), 0
    start = graph.find(b"blendMode")
    for k, (name, vis, opa) in enumerate(zip(names, visible, opacity)):
        i = start
        while True:  # next string record that is followed by the property bytes
            i = graph.find(b"\x06", i)
            ln = graph[i + 5]
            j = i + 6 + ln
            if graph[j] == 0x09 and graph[j + 5] in (0, 1) and graph[j + 6] in (0, 1):
                break
            i += 1
        enc = name.encode("utf-8")
        if len(enc) > 127:
            raise ValueError("layer names must be under 128 bytes")
        out += graph[pos:i + 5] + bytes([len(enc)]) + enc + graph[j:j + 5]
        out += bytes([1 if vis else 0, graph[j + 6], opa])
        pos = j + 8
        start = j + 8
    out += graph[pos:]
    return bytes(out)


def _lps(text):
    raw = text.encode("utf-8")
    n, out = len(raw), bytearray()
    while True:
        out.append((n & 0x7F) | (0x80 if n > 0x7F else 0))
        n >>= 7
        if not n:
            return bytes(out) + raw


def _add_layers(graph, new_names, w, h):
    """The graph (paint.net's two-byte marker, then the NRBF stream) with len(new_names)
    hidden bitmap layers added on top: a BitmapLayer with its properties, surface, layer
    properties, blend op and pixel memory block each, appended before the end of the
    stream (so their memory blocks, whose pixels follow the graph in that order, come
    last), referenced from the end of the layer list's item array."""
    from nrbf import Graph
    g = Graph(graph, 2)
    R = g.records
    i32, i64 = (lambda v: struct.pack("<i", v)), (lambda v: struct.pack("<q", v))
    ref = lambda oid: b"\x09" + i32(oid)

    def vals(rec):
        return dict(zip(g.meta[rec[3][2]][1], rec[3][3]))

    ll = next(r for r in R if r[0] in ("class", "classid") and r[3][1] == "PaintDotNet.LayerList")
    lv = vals(ll)
    size_off, ver_off = lv["ArrayList+_size"][2], lv["ArrayList+_version"][2]
    size = struct.unpack_from("<i", graph, size_off)[0]
    arr = R[g.objects[R[lv["ArrayList+_items"][1]][3]]]
    arr_oid, arr_len, items = arr[3]
    layer_ids = [R[j][3] for j in items if R[j][0] == "ref"]
    if len(layer_ids) != size:
        raise ValueError("the layer list's items don't match its size")
    top = vals(R[g.objects[layer_ids[-1]]])
    tprops = vals(R[g.objects[R[top["Layer+properties"][1]][3]]])
    meta_ref = R[tprops["userMetadataItems"][1]]
    if meta_ref[0] != "ref":
        raise ValueError("the top layer's metadata is not a shared reference")
    ids = [o for o in g.objects] + [r[3] for r in R if r[0] == "ref"] + \
        [r[3][0] for r in R if r[0] == "library"]  # libraries share the id counter
    nxt, neg = max(ids) + 1, min(min(ids), 0) - 1
    mid = g.meta_id
    k, out_layers, out_parts, out_blocks, new_refs = len(new_names), b"", b"", b"", b""
    for name in new_names:
        lay, props, surf, lprops, op, mem, sid = range(nxt, nxt + 7)
        nxt += 7
        mode, neg = neg, neg - 1
        out_layers += (b"\x01" + i32(lay) + i32(mid("PaintDotNet.BitmapLayer")) + ref(props) + ref(surf)
                       + b"\x00" + i32(w) + i32(h) + ref(lprops))
        out_parts += (b"\x01" + i32(props) + i32(mid("PaintDotNet.BitmapLayer+BitmapLayerProperties"))
                      + ref(op))
        out_parts += (b"\x01" + i32(surf) + i32(mid("PaintDotNet.Surface")) + i32(w) + i32(h) + i32(w * 4)
                      + ref(mem))
        out_parts += (b"\x01" + i32(lprops) + i32(mid("PaintDotNet.Layer+LayerProperties"))
                      + b"\x06" + i32(sid) + _lps(name) + ref(meta_ref[3]) + bytes([0, 0, 255])
                      + b"\x01" + i32(mode) + i32(mid("PaintDotNet.LayerBlendMode")) + i32(0))
        out_blocks += b"\x01" + i32(op) + i32(mid("PaintDotNet.UserBlendOps+NormalBlendOp"))
        out_blocks += b"\x01" + i32(mem) + i32(mid("PaintDotNet.MemoryBlock")) + i64(w * h * 4) + b"\x00\x01"
        new_refs += ref(lay)
    # edits from the end backwards, so earlier offsets stay valid
    end = R[-1][1]
    graph = graph[:end] + out_layers + out_parts + out_blocks + graph[end:]
    tail = R[items[-1]]
    free = tail[3] if tail[0] in ("null", "nulls") else 0
    left = free - k
    rest = b"" if left <= 0 else (b"\x0d" + bytes([left]) if left < 256 else b"\x0e" + i32(left))
    if free:
        graph = graph[:tail[1]] + new_refs + rest + graph[tail[2]:]
    else:
        graph = graph[:arr[2]] + new_refs + graph[arr[2]:]
    if left < 0:  # the item array grows
        graph = graph[:arr[1] + 5] + i32(arr_len - left) + graph[arr[1] + 9:]
    ver = struct.unpack_from("<i", graph, ver_off)[0]
    graph = graph[:size_off] + i32(size + k) + i32(ver + k) + graph[ver_off + 4:]
    return graph


def write_pdn(template, out, layers, names=None, visible=None, opacity=None):
    """layers: list of HxWx4 uint8 RGBA arrays, bottom layer first. names, visible
    (bools) and opacity (0-255) are per layer; left out, the template's are kept."""
    buf = open(template, "rb").read()
    n = buf[4] | (buf[5] << 8) | (buf[6] << 16)
    xml = buf[7:7 + n].decode("utf-8")
    ow = int(re.search(r'width="(\d+)"', xml).group(1))
    oh = int(re.search(r'height="(\d+)"', xml).group(1))
    nl = int(re.search(r'layers="(\d+)"', xml).group(1))
    if len(layers) < nl:
        raise ValueError(f"template has {nl} layers, got {len(layers)}")
    h, w = layers[0].shape[:2]
    g0 = 7 + n
    g1 = buf.find(b"\x0b\x00\x00\x04\x00\x00", g0) + 1  # MessageEnd, then layer data
    graph = buf[g0:g1]
    if (ow, oh) != (w, h):
        graph = _patch(graph, ow, w, "<i", 2 * nl + 1)
        graph = _patch(graph, oh, h, "<i", 2 * nl + 1)
        graph = _patch(graph, ow * 4, w * 4, "<i", nl)
        graph = _patch(graph, ow * oh * 4, w * h * 4, "<q", nl)
    if len(layers) > nl:  # new layers on top, named "Layer N" unless names are given
        graph = _add_layers(graph, [f"Layer {i + 1}" for i in range(nl, len(layers))], w, h)
    if names is not None:
        count = len(layers)
        graph = _set_layer_props(graph, names, visible or [True] * count, opacity or [255] * count)

    # header: new size and a thumbnail of the flattened image
    flat = Image.new("RGBA", (w, h))
    for k, lay in enumerate(layers):
        if visible is None or visible[k]:
            flat = Image.alpha_composite(flat, Image.fromarray(lay))
    thumb = flat.resize((256, max(1, round(256 * h / w))), Image.BOX)
    png = io.BytesIO()
    thumb.save(png, "PNG")
    xml = re.sub(r'width="\d+"', f'width="{w}"', xml, count=1)
    xml = re.sub(r'height="\d+"', f'height="{h}"', xml, count=1)
    xml = re.sub(r'layers="\d+"', f'layers="{len(layers)}"', xml, count=1)
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
                z = gzip.compress(data[k:k + CHUNK], compresslevel=6, mtime=0)  # same bytes each time
                f.write(struct.pack(">II", k // CHUNK, len(z)))
                f.write(z)
