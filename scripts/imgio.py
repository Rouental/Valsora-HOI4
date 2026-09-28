"""Minimal writers for the image formats HOI4 reads.

BMP: uncompressed, 40-byte BITMAPINFOHEADER (HOI4 rejects V4/V5 headers), rows
bottom-up and padded to 4 bytes. 8-bit images carry an explicit palette.
DDS: uncompressed A8R8G8B8, one mip level, rows top-down - the same layout as the
vanilla colormap_rgb_cityemissivemask_a.dds.
"""
import struct

import numpy as np


def write_bmp(path, img, palette=None):
    """img: HxW uint8 (8-bit, needs palette as Nx3 RGB) or HxWx3 uint8 RGB."""
    h, w = img.shape[:2]
    if img.ndim == 2:
        bpp = 8
        pal = np.zeros((len(palette), 4), np.uint8)
        pal[:, 0] = palette[:, 2]
        pal[:, 1] = palette[:, 1]
        pal[:, 2] = palette[:, 0]
        pal_bytes = pal.tobytes()
        rows = img[::-1]
    else:
        bpp = 24
        pal_bytes = b""
        rows = img[::-1, :, ::-1]  # bottom-up, BGR
    stride = (w * bpp // 8 + 3) & ~3
    data = np.zeros((h, stride), np.uint8)
    data[:, :w * bpp // 8] = rows.reshape(h, -1)
    offset = 14 + 40 + len(pal_bytes)
    size = offset + data.nbytes
    ncol = len(palette) if palette is not None else 0
    with open(path, "wb") as f:
        f.write(b"BM" + struct.pack("<IHHI", size, 0, 0, offset))
        f.write(struct.pack("<IiiHHIIiiII", 40, w, h, 1, bpp, 0, data.nbytes, 2835, 2835,
                            ncol, 0))
        f.write(pal_bytes)
        f.write(data.tobytes())


def read_bmp(path):
    """Read back an uncompressed 8- or 24-bit BMP written by write_bmp (for checks)."""
    raw = open(path, "rb").read()
    offset = struct.unpack_from("<I", raw, 10)[0]
    hdr, w, h, _, bpp = struct.unpack_from("<IiiHH", raw, 14)
    stride = (w * bpp // 8 + 3) & ~3
    data = np.frombuffer(raw, np.uint8, count=stride * abs(h), offset=offset).reshape(abs(h), stride)
    data = data[:, :w * bpp // 8]
    if bpp == 24:
        img = data.reshape(abs(h), w, 3)[:, :, ::-1]
    else:
        img = data
    if h > 0:
        img = img[::-1]
    return dict(img=img, bpp=bpp, header=hdr, width=w, height=abs(h), offset=offset)


def write_dds(path, rgba):
    """rgba: HxWx4 uint8, row 0 = north."""
    h, w = rgba.shape[:2]
    flags = 0x1 | 0x2 | 0x4 | 0x8 | 0x1000  # CAPS HEIGHT WIDTH PITCH PIXELFORMAT
    header = struct.pack("<4sIIIIIII", b"DDS ", 124, flags, h, w, w * 4, 0, 1)
    header += b"\0" * 44
    header += struct.pack("<IIIIIIII", 32, 0x41, 0, 32, 0x00FF0000, 0x0000FF00, 0x000000FF,
                          0xFF000000)
    header += struct.pack("<IIIII", 0x1000, 0, 0, 0, 0)
    bgra = rgba[:, :, [2, 1, 0, 3]]
    with open(path, "wb") as f:
        f.write(header)
        f.write(np.ascontiguousarray(bgra).tobytes())


def write_tga(path, rgba):
    """Uncompressed 32-bit TGA, bottom-left origin (the layout HOI4 flags use)."""
    h, w = rgba.shape[:2]
    header = struct.pack("<BBBHHBHHHHBB", 0, 0, 2, 0, 0, 0, 0, 0, w, h, 32, 8)
    bgra = rgba[::-1, :, [2, 1, 0, 3]]
    with open(path, "wb") as f:
        f.write(header)
        f.write(np.ascontiguousarray(bgra).tobytes())


def palette_from_header(path):
    """RGB palette from a saved BMP header+palette dump."""
    raw = open(path, "rb").read()
    offset = struct.unpack_from("<I", raw, 10)[0]
    hdr = struct.unpack_from("<I", raw, 14)[0]
    pal = np.frombuffer(raw[14 + hdr:offset], np.uint8).reshape(-1, 4)
    return pal[:, [2, 1, 0]].copy()
