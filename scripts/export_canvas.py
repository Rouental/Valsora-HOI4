"""Images for the author: the new layout at game resolution, to draw countries on.

dist/valsora_land_5120x2560.png       land / sea / lakes exactly as the game has them
dist/valsora_countries_5120x2560.png  the .pdn's country colours ("Land & Borders &
                                      Colours" layer) moved with their continents onto
                                      the new layout; border lines are filled in with
                                      the neighbouring country's colour
dist/preview_layout.png               small labelled overview
dist/preview_provinces.png            small overview of the placeholder provinces
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi

from common import MAP_W, MAP_H, SCALE, CONTINENTS

DIST = Path("dist")
LAND, SEA, LAKE = (116, 150, 92), (38, 62, 104), (92, 140, 190)


def main():
    DIST.mkdir(exist_ok=True)
    p = np.load("work/provinces.npz")
    lab, kind, cont = p["prov"], p["kind"], p["cont"]
    pk = kind[lab]
    land_img = np.zeros((MAP_H, MAP_W, 3), np.uint8)
    land_img[pk == 0] = SEA
    land_img[pk == 1] = LAND
    land_img[pk == 2] = LAKE
    Image.fromarray(land_img).save(DIST / "valsora_land_5120x2560.png", optimize=True)

    # the author's country colours, carried along with each continent block
    lay = json.load(open("work/layout.json"))
    src = np.load("work/pdn/layer1.npy", mmap_mode="r")
    blk = np.load("work/block_full.npy", mmap_mode="r")
    out = np.zeros((MAP_H, MAP_W, 3), np.uint8)
    ok = np.zeros((MAP_H, MAP_W), bool)
    for i, b in enumerate(lay["blocks"]):
        m = np.load(f"work/blocks/{i}.npy")
        ox, oy = b["offset"]
        sx0, sy0, sx1, sy1 = b["src_bbox"]
        ys, xs = np.nonzero(m)
        sy = np.clip(((ys + 0.5) / SCALE + sy0).astype(int), sy0, sy1 - 1)
        sx = np.clip(((xs + 0.5) / SCALE + sx0).astype(int), sx0, sx1 - 1)
        crop = np.asarray(src[sy0:sy1, sx0:sx1])
        bcrop = np.asarray(blk[sy0:sy1, sx0:sx1])
        rgba = crop[sy - sy0, sx - sx0]
        good = (bcrop[sy - sy0, sx - sx0] == i) & (rgba[:, 3] > 0) & (rgba[:, :3].max(axis=1) > 20)
        Y, X = ys + oy, (xs + ox) % MAP_W
        out[Y[good], X[good]] = rgba[good, :3]
        ok[Y[good], X[good]] = True
    # fill border lines and resampling gaps from the nearest coloured pixel
    idx = ndi.distance_transform_edt(~ok, return_distances=False, return_indices=True)
    out = out[idx[0], idx[1]]
    out[pk == 0] = SEA
    out[pk == 2] = LAKE
    Image.fromarray(out).save(DIST / "valsora_countries_5120x2560.png", optimize=True)

    # labelled overview
    pal = {1: (216, 84, 84), 2: (116, 152, 206), 3: (70, 170, 70), 4: (214, 110, 214),
           5: (96, 190, 150), 6: (184, 172, 100), 7: (236, 160, 70)}
    pc = cont[lab]
    ov = np.zeros((MAP_H, MAP_W, 3), np.uint8)
    ov[:] = SEA
    ov[pk == 2] = LAKE
    for k, col in pal.items():
        ov[(pk == 1) & (pc == k)] = col
    img = Image.fromarray(ov).resize((MAP_W // 4, MAP_H // 4), Image.BOX)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 18)
    except OSError:
        font = ImageFont.load_default()
    for k in pal:
        ys, xs = np.nonzero((pk == 1) & (pc == k))
        name = CONTINENTS[k - 1].capitalize()
        x, y = xs.mean() / 4, ys.mean() / 4
        draw.text((x, y), name, fill=(255, 255, 255), font=font, anchor="mm",
                  stroke_width=2, stroke_fill=(0, 0, 0))
    img.save(DIST / "preview_layout.png", optimize=True)

    rng = np.random.default_rng(3)
    cols = rng.integers(40, 255, (len(kind), 3)).astype(np.uint8)
    cols[kind == 0] = (cols[kind == 0] * 0.35 + np.array(SEA) * 0.65).astype(np.uint8)
    Image.fromarray(cols[lab]).resize((MAP_W // 2, MAP_H // 2), Image.NEAREST).save(
        DIST / "preview_provinces.png", optimize=True)
    print("wrote", ", ".join(sorted(f.name for f in DIST.glob("*.png"))))


if __name__ == "__main__":
    main()
