"""Check a paint.net .pdn file from end to end, as paint.net would read it: the header, the whole .NET object graph,
every layer's objects and every pixel chunk. Run it on every .pdn we write before it goes to the author, and on an
upload that will not open (2026-10-17: the author's flag file "is corrupted").

    python3 scripts/pdn_check.py FILE.pdn [...]     -> "ok" or a list of problems per file; exit 1 on any problem

What it checks:
  - "PDN3", the XML header (width, height, layers) and paint.net's two-byte marker before the graph;
  - the graph (nrbf.py) to its end record: every object id used once (a value type's -n counting as n, as
    BinaryFormatter reads it), every reference pointing at an object;
  - the layer list: its size, its item array, one BitmapLayer per item, each with its properties, surface, layer
    properties (name, metadata, visibility, opacity, blend mode) and memory block, of the document's size;
  - the layers' memory blocks in the graph's order, as many as the header's layers;
  - after the graph, per layer: the format byte, the chunk size, every chunk's index once and its gzip data
    decompressing to the chunk's length (the last one shorter), and nothing after the last layer.
"""
import gzip
import re
import struct
import sys
import zlib
from collections import Counter

from nrbf import Graph


def check(path):
    out = []
    b = open(path, "rb").read()
    if b[:4] != b"PDN3":
        return [f"not a paint.net 3+ file (starts {b[:4]!r})"]
    n = b[4] | (b[5] << 8) | (b[6] << 16)
    try:
        xml = b[7:7 + n].decode("utf-8")
    except UnicodeDecodeError:
        return ["the XML header is not UTF-8"]
    m = {k: re.search(rf'{k}="(\d+)"', xml) for k in ("width", "height", "layers")}
    if not all(m.values()):
        return [f"the XML header lacks {[k for k, v in m.items() if not v]}"]
    W, H, NL = (int(m[k].group(1)) for k in ("width", "height", "layers"))
    g0 = 7 + n
    if b[g0:g0 + 2] != b"\x00\x01":
        out.append(f"the graph's marker is {b[g0:g0 + 2].hex()}, not 0001")
    try:
        g = Graph(b, g0 + 2)
    except Exception as e:  # noqa: BLE001 - any parse failure is the finding
        return out + [f"the object graph does not parse: {e}"]
    R = g.records
    # by absolute value: BinaryFormatter, which paint.net reads with, takes a value type's id -n as n (2026-10-18:
    # our flag files had -831 beside 831, "An object cannot be registered twice")
    ids = Counter(abs(r[3][0]) for r in R if r[0] in ("class", "classid", "string", "objarray", "binarray",
                                                      "primarray"))
    dup = [o for o, c in ids.items() if c > 1]
    if dup:
        out.append(f"object ids used twice (a value type's -n counts as n): {dup[:10]}")
    bad = sorted({r[3] for r in R if r[0] == "ref" and r[3] not in g.objects})
    if bad:
        out.append(f"references to no object: {bad[:10]}")

    def vals(rec):
        return dict(zip(g.meta[rec[3][2]][1], rec[3][3]))

    def obj(v):  # a member that is a reference or an inline record -> its record
        r = R[v[1]]
        return R[g.objects[r[3]]] if r[0] == "ref" else r

    def i32(v):
        return struct.unpack("<i", v[1])[0]

    try:
        ll = next(r for r in R if r[0] in ("class", "classid") and r[3][1] == "PaintDotNet.LayerList")
        lv = vals(ll)
        size = i32(lv["ArrayList+_size"])
        arr = obj(lv["ArrayList+_items"])
        items = arr[3][2]
        lids = [R[j][3] for j in items if R[j][0] == "ref"]
        slots = sum(R[j][3] if R[j][0] in ("null", "nulls") else 1 for j in items)
        if slots != arr[3][1]:
            out.append(f"the layer array holds {slots} slots, its length says {arr[3][1]}")
        if len(lids) != size or size != NL:
            out.append(f"layers: the list says {size}, its items {len(lids)}, the header {NL}")
        dv = vals(next(r for r in R if r[0] in ("class", "classid") and r[3][1] == "PaintDotNet.Document"))
        if (i32(dv["width"]), i32(dv["height"])) != (W, H):
            out.append(f"the document is {i32(dv['width'])}x{i32(dv['height'])}, the header {W}x{H}")
        mems = []
        for k, lid in enumerate(lids):
            lay = R[g.objects[lid]]
            if lay[3][1] != "PaintDotNet.BitmapLayer":
                out.append(f"layer {k}: a {lay[3][1]}")
                continue
            v = vals(lay)
            lp = vals(obj(v["Layer+properties"]))
            name = R[lp["name"][1]]
            name = name[3][1] if name[0] == "string" else R[g.objects[name[3]]][3][1]
            if (i32(v["Layer+width"]), i32(v["Layer+height"])) != (W, H):
                out.append(f"layer {k} ({name}): {i32(v['Layer+width'])}x{i32(v['Layer+height'])}")
            s = vals(obj(v["surface"]))
            if (i32(s["width"]), i32(s["height"]), i32(s["stride"])) != (W, H, 4 * W):
                out.append(f"layer {k} ({name}): surface {i32(s['width'])}x{i32(s['height'])} stride {i32(s['stride'])}")
            mb = obj(s["scan0"])
            mv = vals(mb)
            ln = struct.unpack("<q", mv["length64"][1])[0]
            if ln != 4 * W * H:
                out.append(f"layer {k} ({name}): memory block of {ln} bytes, not {4 * W * H}")
            if lp["visible"][1] not in (b"\x00", b"\x01") or lp["isBackground"][1] not in (b"\x00", b"\x01"):
                out.append(f"layer {k} ({name}): visible / isBackground not booleans")
            if "blendMode" in lp:
                obj(lp["blendMode"])
            obj(vals(obj(v["properties"]))["blendOp"])
            mems.append(mb[1])
        order = [r[1] for r in R if r[0] in ("class", "classid") and r[3][1] == "PaintDotNet.MemoryBlock"]
        if sorted(mems) != sorted(order):
            out.append(f"{len(order)} memory blocks in the graph, {len(mems)} used by layers")
        elif mems != sorted(mems):
            out.append("the layers' memory blocks are not in layer order in the graph (the pixels would be swapped)")
    except (StopIteration, KeyError, IndexError) as e:
        out.append(f"the layer objects are not as paint.net writes them ({type(e).__name__}: {e})")

    # the pixels after the graph
    p = R[-1][2]
    for k in range(NL):
        if p + 5 > len(b):
            out.append(f"the file ends before layer {k}'s pixels")
            return out
        fmt, chunk = b[p], struct.unpack(">I", b[p + 1:p + 5])[0]
        p += 5
        if fmt != 0 or chunk <= 0:
            out.append(f"layer {k}: format byte {fmt}, chunk size {chunk}")
            return out
        total = 4 * W * H
        nch = -(-total // chunk)
        seen = set()
        for _ in range(nch):
            if p + 8 > len(b):
                out.append(f"layer {k}: the file ends after {len(seen)} of its {nch} chunks")
                return out
            idx, ln = struct.unpack(">II", b[p:p + 8])
            p += 8
            data = b[p:p + ln]
            p += ln
            if idx in seen or idx >= nch:
                out.append(f"layer {k}: chunk index {idx} again or out of range")
            seen.add(idx)
            want = min(chunk, total - idx * chunk) if idx < nch else None
            try:
                got = len(gzip.decompress(data))
            except (OSError, EOFError, zlib.error) as e:
                out.append(f"layer {k}: chunk {idx} does not decompress ({e})")
                continue
            if want is not None and got != want:
                out.append(f"layer {k}: chunk {idx} holds {got} bytes, not {want}")
    if p != len(b):
        out.append(f"{len(b) - p} bytes after the last layer")
    return out


def main():
    bad = 0
    for path in sys.argv[1:]:
        probs = check(path)
        bad += bool(probs)
        print(f"{path}: " + ("ok" if not probs else "\n  " + "\n  ".join(probs)))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
