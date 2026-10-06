"""The "Valsora: Victorianization Patch" submod: Valsora with the Victorianization map look.

Victorianization (Universal Compatibility, Steam Workshop 3807649245; the author sent it on
2026-10-06 as the look they want) gives HOI4's map a Victoria 3 style: pastel country
fills on graph paper, a grid at sea, painted borders and a period map font. Almost all
of it (shaders, border and terrain textures, fonts, graphics defines) works on any map
size; the shaders read the size from the engine. Only its colour maps are drawn for
the base game's map (2816x1024, half of 5632x2048), so this patch supplies its own at
Valsora's size, drawn here in the same style (none of Victorianization's files are
copied), plus a flat world_normal.bmp, as Victorianization's is.

The player enables Victorianization, Valsora and this patch; the patch lists both as
dependencies, so it loads after them and its files win.

    python3 scripts/victorianization_patch.py   # build/valsora_victorianization, dist/valsora_victorianization.zip
"""
import re
import shutil
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image

from common import MAP_W as W, MAP_H as H, MOD_NAME, COUNTRIES
from imgio import write_bmp, write_dds

NAME = "valsora_victorianization"
OUT = Path("build") / NAME
VIC = "Victorianization (Universal Compatibility)"
# measured from Victorianization's colour maps (half-resolution pixels)
LAND = 115.0                     # mid grey paper; the shaders tint it with the country colour
WATER = (197.0, 202.0, 197.0)    # pale grey-green paper
GRAIN = 7.0                      # fine grain, standard deviation
MINOR, MAJOR = 16, 256           # graph-paper squares and folds (32 and 512 map px)
SEED = 20261006


def half(a):
    return a.reshape(a.shape[0] // 2, 2, a.shape[1] // 2, 2, *a.shape[2:]).mean(axis=(1, 3))


def paper(h, w, base, rng):
    """Graph paper at this resolution: grain, soft blotches, thin squares and folds."""
    base = np.asarray(base, float).reshape(1, 1, -1)
    lum = rng.normal(0, GRAIN, (h, w))
    blot = np.asarray(Image.fromarray(rng.normal(0, 1, (h // 64 + 1, w // 64 + 1)).astype(np.float32))
                      .resize((w, h), Image.BICUBIC))
    lum += blot * 3
    ys, xs = np.arange(h)[:, None], np.arange(w)[None, :]
    minor = ((ys % MINOR) == 0) | ((xs % MINOR) == 0)
    lum = np.where(minor, lum - 22, lum)
    # folds: a dark crease two pixels wide with a light edge beside it, a little ragged
    off = MAJOR // 2 - 2
    for d, k in ((0, -38), (1, -30), (2, 14)):
        fold = (((ys - off - d) % MAJOR) == 0) | (((xs - off - d) % MAJOR) == 0)
        lum = np.where(fold, lum + k + rng.normal(0, 6, (h, w)), lum)
    tint = np.array([-2.0, 2.0, -2.0]).reshape(1, 1, 3) * minor[..., None]  # faintly green lines
    return np.clip(base + lum[..., None] + tint, 0, 255)


def main():
    rng = np.random.default_rng(SEED)
    hh, hw = H // 2, W // 2
    if OUT.exists():
        shutil.rmtree(OUT)
    tdir = OUT / "map" / "terrain"
    tdir.mkdir(parents=True)
    land = paper(hh, hw, (LAND, LAND, LAND), rng)
    write_dds(tdir / "colormap_rgb_cityemissivemask_a.dds",
              np.dstack([land, np.zeros((hh, hw))]).round().astype(np.uint8))  # no city lights
    w0 = np.dstack([paper(hh, hw, WATER, rng), np.full((hh, hw), 255.0)])
    write_dds(tdir / "colormap_water_0.dds", w0.round().astype(np.uint8))
    w1 = half(w0)
    write_dds(tdir / "colormap_water_1.dds", w1.round().astype(np.uint8))
    write_dds(tdir / "colormap_water_2.dds", half(w1).round().astype(np.uint8))
    flat = np.zeros((hh, hw, 3), np.uint8)
    flat[...] = (128, 128, 255)  # no relief shading, like Victorianization's
    write_bmp(OUT / "map/world_normal.bmp", flat)

    desc = ['version="0.1"', "tags={", '\t"Graphics"', '\t"Map"', "}",
            'name="Valsora: Victorianization Patch"', 'supported_version="1.19.*"',
            'picture="thumbnail.png"', "dependencies={", f'\t"{VIC}"', f'\t"{MOD_NAME}"', "}"]
    (OUT / "descriptor.mod").write_text("\n".join(desc) + "\n")
    Path("build", f"{NAME}.mod").write_text("\n".join(desc + [f'path="mod/{NAME}"']) + "\n")
    prev = preview(land, w0[..., :3])
    prev.resize((512, 256), Image.BOX).save(OUT / "thumbnail.png")
    prev.save("dist/preview_victorianization.png")
    out = Path("dist") / f"{NAME}.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for f in sorted(OUT.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(OUT.parent).as_posix())
        z.write(Path("build", f"{NAME}.mod"), f"{NAME}.mod")
    print(f"wrote {OUT} and {out} ({out.stat().st_size / 1e6:.1f} MB)")


def preview(land, water):
    """A rough picture of the look (the game draws it with Victorianization's shaders)."""
    p = np.load("work/provinces.npz")
    col = {v[0]: v[3] for v in COUNTRIES.values()}
    tags = sorted(col)
    own_of = np.full(len(p["kind"]) + 1, -1)
    for f in Path("build/valsora_test/history/states").glob("*.txt"):
        t = f.read_text(encoding="utf-8")
        tag = re.search(r"owner = (\w+)", t).group(1)
        ids = re.search(r"provinces = \{([^}]*)\}", t).group(1).split()
        own_of[np.array(ids, int)] = tags.index(tag)
    prov = p["prov"][::2, ::2]
    o = own_of[prov + 1]
    pal = np.array([col[t] for t in tags] + [(0, 0, 0)], float)
    is_water = p["kind"][prov] != 1
    pastel = pal[o] * 0.7 + 255 * 0.3
    land_img = pastel * (land / LAND) * 0.97
    sea = water * np.array([0.84, 0.9, 0.98])  # Victorianization's sea reads grey-blue
    img = np.where(is_water[..., None], sea, land_img)
    own = np.where(is_water, -1, o)
    cb = np.zeros(own.shape, bool)
    cb[:, 1:] |= own[:, 1:] != own[:, :-1]
    cb[1:] |= own[1:] != own[:-1]
    img = np.where(cb[..., None], img * 0.35, img)
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))


if __name__ == "__main__":
    main()
