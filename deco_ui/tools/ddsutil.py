"""Minimal DDS reader/writer for uncompressed 32-bit A8R8G8B8 textures (what the mod ships)."""
import os
import struct

import numpy as np
from PIL import Image


def write_dds(img, path):
    img = img.convert("RGBA")
    w, h = img.size
    a = np.array(img, dtype=np.uint8)
    bgra = a[..., [2, 1, 0, 3]].tobytes()
    flags = 0x1 | 0x2 | 0x4 | 0x8 | 0x1000
    header = struct.pack("<4sIIIIIII44s", b"DDS ", 124, flags, h, w, w * 4, 0, 0, b"\0" * 44)
    pf = struct.pack("<IIIIIIII", 32, 0x41, 0, 32, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000)
    caps = struct.pack("<IIIII", 0x1000, 0, 0, 0, 0)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(header + pf + caps + bgra)


def read_dds(path):
    """Read back a file written by write_dds (validates header fields)."""
    data = open(path, "rb").read()
    magic, size, flags, h, w, pitch = struct.unpack_from("<4sIIIII", data, 0)
    assert magic == b"DDS " and size == 124, path
    pf_size, pf_flags, fourcc, bits, rm, gm, bm, am = struct.unpack_from("<IIIIIIII", data, 76)
    assert pf_size == 32 and bits == 32 and fourcc == 0 and am == 0xFF000000 and rm == 0x00FF0000, path
    assert len(data) == 128 + w * h * 4, (path, len(data), w, h)
    a = np.frombuffer(data, np.uint8, offset=128).reshape(h, w, 4)[..., [2, 1, 0, 3]]
    return Image.fromarray(a.copy(), "RGBA")
