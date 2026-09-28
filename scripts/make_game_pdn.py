"""Make "source/HOI4 Mod Map.pdn": the game's own map data as paint.net layers.

One pixel is one map pixel (5120x2560). Each layer is one thing the game needs, and
read_layers.py turns them back into the mod. Bottom to top:

    Heightmap           grey = height (sea level 95)
    Terrain             HOI4 terrain colours; also decides land / sea / lake
    Rivers              empty (transparent = no river)
    Continents          one colour per continent
    Provinces           one colour per province (becomes provinces.bmp)
    Strategic Regions   one colour per region
    States              one colour per state
    Countries           one colour per country; see-through over the provinces
    Notes (ignored by the build)   the old .pdn's country colours, for reference

It is made from the current build (work/*.npz), so run the placeholder pipeline first.
"""
from pathlib import Path

import numpy as np
from PIL import Image

import build_mod
from common import CONT_COLOURS, COUNTRIES, CONTINENTS, TERRAIN_OCEAN, TERRAIN_LAKE, TERRAIN_PLAINS
from imgio import palette_from_header
from writepdn import write_pdn

OUT = Path("source/HOI4 Mod Map.pdn")
TEMPLATE = "source/Valsora_06SEPT2026HOTFIX.pdn"
NAMES = ["Heightmap", "Terrain", "Rivers", "Continents", "Provinces", "Strategic Regions",
         "States", "Countries", "Notes (ignored by the build)"]
VISIBLE = [False, False, False, False, True, False, False, True, False]
OPACITY = [255, 255, 255, 255, 255, 255, 255, 140, 255]


def paint(values, colours, mask=None):
    """RGBA layer: pixel gets colours[values]; transparent outside mask."""
    out = np.zeros(values.shape + (4,), np.uint8)
    out[..., :3] = np.asarray(colours, np.uint8)[values]
    out[..., 3] = 255 if mask is None else np.where(mask, 255, 0)
    return out


def distinct(n, seed):
    """n different, fairly bright colours, none black."""
    rng = np.random.default_rng(seed)
    codes = rng.choice(np.arange(1 << 15), size=n, replace=False)
    r, g, b = (codes >> 10) & 31, (codes >> 5) & 31, codes & 31
    return (np.stack([r, g, b], 1) * 6 + 60).astype(np.uint8)  # 60..246 per channel


def main():
    p = np.load("work/provinces.npz")
    lab, kind, cont = p["prov"], p["kind"], p["cont"]
    reg = np.load("work/regions.npz")
    state_of, region_of = reg["state_of"], reg["region_of"]
    n = len(kind)
    pix_kind = kind[lab]
    land = pix_kind == 1

    height, _ = build_mod.heightmap(pix_kind)
    grey = np.repeat(height[..., None], 3, -1)
    heightmap = np.dstack([grey, np.full(height.shape, 255, np.uint8)])

    tpal = palette_from_header("source/palettes/terrain.bmp.header.bin")
    tidx = np.where(pix_kind == 0, TERRAIN_OCEAN, np.where(pix_kind == 2, TERRAIN_LAKE, TERRAIN_PLAINS))
    terrain = paint(tidx, tpal)

    rivers = np.zeros(lab.shape + (4,), np.uint8)
    continents = paint(np.maximum(cont[lab].astype(int) - 1, 0), CONT_COLOURS, land)

    # the same province colours build_mod.py has always used
    rng = np.random.default_rng(20260928)
    codes = rng.choice(np.arange(1, 1 << 24), size=n, replace=False)
    pcol = np.stack([codes >> 16, (codes >> 8) & 255, codes & 255], 1)
    provinces = paint(lab, pcol)

    regions = paint(region_of[lab], distinct(region_of.max() + 1, 1))
    s = state_of[lab]
    states = paint(np.maximum(s, 0), distinct(state_of.max() + 1, 2), s >= 0)
    kcol = [COUNTRIES[c][3] for c in CONTINENTS]
    countries = paint(np.maximum(cont[lab].astype(int) - 1, 0), kcol, s >= 0)

    notes = np.zeros(lab.shape + (4,), np.uint8)
    old = Path("dist/valsora_countries_5120x2560.png")
    if old.exists():
        notes[..., :3] = np.asarray(Image.open(old).convert("RGB"))
        notes[land, 3] = 255

    layers = [heightmap, terrain, rivers, continents, provinces, regions, states, countries, notes]
    write_pdn(TEMPLATE, OUT, layers, NAMES, VISIBLE, OPACITY)
    print(f"wrote {OUT} ({OUT.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
