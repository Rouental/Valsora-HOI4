"""The "Valsora: Cartographic Map" submod: a flat, old-atlas look like HOI3's political map.

It loads after the main mod (a dependency) and only swaps graphics, so saves and
gameplay are untouched:
    - country colours fill whole countries instead of fading out from the borders
      (NGraphics.GRADIENT_BORDERS_THICKNESS_COUNTRY_*, in pixels, made huge);
    - no relief shading: world_normal.bmp flat (heights stay, so buildings and units
      still sit on the ground);
    - land tinted a plain muted khaki; sea one flat grey-blue with a 15° graticule.

Run after a build (it reads work/world.npz):
    python3 scripts/cartographic.py     # build/valsora_cartographic, dist/valsora_cartographic.zip
"""
import shutil
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image

from common import MAP_W as W, MAP_H as H, MOD_NAME, COUNTRIES
from imgio import write_bmp, write_dds

NAME = "valsora_cartographic"
OUT = Path("build") / NAME
LAND = (118, 110, 88)      # colormap tint over land: muted khaki (vanilla ~ (64, 70, 34))
SEA = (72, 90, 106)        # flat grey-blue (vanilla 33-81, blue, darker offshore)
GRID = (92, 110, 124)      # graticule lines on the sea
GRID_DEG = 15              # the map is 360° wide and 180° tall around the equator (row H/2)
THICKNESS = 2000.0         # px: more than any country is wide, so the fill covers it


def half(a):
    return a.reshape(a.shape[0] // 2, 2, a.shape[1] // 2, 2, *a.shape[2:]).mean(axis=(1, 3))


def graticule(h, w):
    """Lines every GRID_DEG degrees, one pixel wide at this resolution."""
    step = w / (360 / GRID_DEG)
    ys, xs = np.arange(h), np.arange(w)
    on_x = np.abs(((xs + step / 2) % step) - step / 2) < 0.5
    on_y = np.abs(((ys - h / 2 + step / 2) % step) - step / 2) < 0.5
    return on_y[:, None] | on_x[None, :]


def main():
    world = np.load("work/world.npz")
    water = half((world["kind"] != 1).astype(np.float32)) >= 0.5
    hh, hw = water.shape
    if OUT.exists():
        shutil.rmtree(OUT)
    tdir = OUT / "map" / "terrain"
    tdir.mkdir(parents=True)

    sea = np.where(graticule(hh, hw)[..., None], np.array(GRID), np.array(SEA)).astype(float)
    land_rgb = np.where(water[..., None], sea, np.array(LAND, float))
    write_dds(tdir / "colormap_rgb_cityemissivemask_a.dds",
              np.dstack([land_rgb, np.zeros((hh, hw))]).astype(np.uint8))
    w0 = np.dstack([np.where(water[..., None], sea, np.array(SEA, float)), np.full((hh, hw), 255.0)])
    write_dds(tdir / "colormap_water_0.dds", w0.round().astype(np.uint8))
    w1 = half(w0)
    write_dds(tdir / "colormap_water_1.dds", w1.round().astype(np.uint8))
    write_dds(tdir / "colormap_water_2.dds", half(w1).round().astype(np.uint8))
    flat = np.zeros((H // 2, W // 2, 3), np.uint8)
    flat[...] = (128, 128, 255)
    write_bmp(OUT / "map/world_normal.bmp", flat)

    (OUT / "common/defines").mkdir(parents=True)
    (OUT / "common/defines/zz_valsora_cartographic.lua").write_text("".join(
        f"NDefines_Graphics.NGraphics.{k} = {v}\n" for k, v in [
            ("GRADIENT_BORDERS_THICKNESS_COUNTRY_LOW", THICKNESS),
            ("GRADIENT_BORDERS_THICKNESS_COUNTRY_HIGH", THICKNESS)]))

    desc = ['version="0.1"', "tags={", '\t"Graphics"', '\t"Map"', "}",
            'name="Valsora: Cartographic Map"', 'supported_version="1.19.*"',
            'picture="thumbnail.png"', "dependencies={", f'\t"{MOD_NAME}"', "}"]
    (OUT / "descriptor.mod").write_text("\n".join(desc) + "\n")
    Path("build", f"{NAME}.mod").write_text("\n".join(desc + [f'path="mod/{NAME}"']) + "\n")
    prev = preview()
    prev.resize((512, 256), Image.BOX).save(OUT / "thumbnail.png")
    prev.save("dist/preview_cartographic.png")

    out = Path("dist") / f"{NAME}.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for f in sorted(OUT.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(OUT.parent).as_posix())
        z.write(Path("build", f"{NAME}.mod"), f"{NAME}.mod")
    print(f"wrote {OUT} and {out} ({out.stat().st_size / 1e6:.1f} MB)")


def preview():
    """A rough picture of the intended look (the game draws it with its own shaders)."""
    import re
    p = np.load("work/provinces.npz")
    col = {v[0]: v[3] for v in COUNTRIES.values()}
    # owners as the game sees them: the built state files (province id = index + 1)
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
    fill = pal[o]
    water = p["kind"][prov] != 1
    hh, hw = prov.shape
    sea = np.where(graticule(hh, hw)[..., None], np.array(GRID), np.array(SEA)).astype(float) * 1.35
    land = np.array(LAND, float) * 1.6 * 0.35 + fill * 0.65
    img = np.where(water[..., None], sea, land)
    st = np.where(water, -1, prov)
    edge = np.zeros(st.shape, bool)
    edge[:, 1:] |= st[:, 1:] != st[:, :-1]
    edge[1:] |= st[1:] != st[:-1]
    own = np.where(water, -1, o)
    cb = np.zeros(st.shape, bool)
    cb[:, 1:] |= own[:, 1:] != own[:, :-1]
    cb[1:] |= own[1:] != own[:-1]
    img = np.where((edge & ~water)[..., None], img * 0.93, img)
    img = np.where(cb[..., None], img * 0.45, img)
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))


if __name__ == "__main__":
    main()
