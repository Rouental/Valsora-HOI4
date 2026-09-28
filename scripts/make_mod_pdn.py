"""Make "source/HOI4 Mod Map.pdn": the current game map as an editable paint.net file.

It is exactly the game's size (5120x2560), so one pixel is one map pixel. It has the
same nine layers as the author's original .pdn:
    Ocean Layer (Base)         flat ocean
    Land & Borders & Colours   land in the old .pdn's country colours; transparent =
                               water. This is the layer the pipeline reads.
    Internal Borders           empty
    Outline 4..1 (Ocean)       the coastal glow bands, regenerated at game scale
    Coastline (1px Black)      land's edge
    Names                      empty (the old labels don't survive the layout change)
Also writes source/hoi4_continents_5120x2560.png, the continent of every land pixel,
which the direct build uses (new land takes the nearest continent).
"""
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

from common import CONTINENTS, CONT_COLOURS
from writepdn import write_pdn

OUT = Path("source/HOI4 Mod Map.pdn")
TEMPLATE = "source/Valsora_06SEPT2026HOTFIX.pdn"
OCEAN = (14, 24, 57)
# (colour, reach in px from the shore) for Outline 4, 3, 2, 1, measured on the
# original at source scale (p95 28.5, 12.5, 5.0, 2.2 px) and scaled by 0.375
BANDS = [((16, 26, 63), 11), ((22, 33, 72), 5), ((34, 44, 84), 2), ((45, 56, 100), 1)]


def layer(mask, colour):
    out = np.zeros(mask.shape + (4,), np.uint8)
    out[mask] = (*colour, 255)
    return out


def main():
    w = np.load("work/world.npz")
    kind, cont = w["kind"], w["cont"]
    land = kind == 1
    countries = np.asarray(Image.open("dist/valsora_countries_5120x2560.png").convert("RGB"))
    land_layer = np.zeros(land.shape + (4,), np.uint8)
    land_layer[land, :3] = countries[land]
    land_layer[land, 3] = 255
    dist = ndi.distance_transform_edt(~land)
    edge = land & ~ndi.binary_erosion(land, border_value=1)
    empty = np.zeros(land.shape + (4,), np.uint8)
    layers = [layer(np.ones_like(land), OCEAN), land_layer, empty]
    layers += [layer(~land & (dist <= r), col) for col, r in BANDS]
    layers += [layer(edge, (0, 0, 0)), empty]
    write_pdn(TEMPLATE, OUT, layers)

    ref = np.zeros(land.shape + (3,), np.uint8)
    for k in range(1, len(CONTINENTS) + 1):
        ref[cont == k] = CONT_COLOURS[k - 1]
    Image.fromarray(ref).save("source/hoi4_continents_5120x2560.png", optimize=True)
    print(f"wrote {OUT} ({OUT.stat().st_size / 1e6:.1f} MB) and the continent reference")


if __name__ == "__main__":
    main()
