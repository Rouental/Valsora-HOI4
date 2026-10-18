"""The author's areas layer: land they marked impassable, desert or jungle (2026-10-18, the author: "I've tried to mark
out the regions that are desert / impassible desert in Usnistan. Red is impassible desert, yellow is regular desert").

The layer is the one whose name starts with one of LAYER_NAMES ("Impassible / Desert / Jungle / Tundra" in the author's
.pdn, "Desert" in an earlier upload). Each area is painted solid in its colour, matched loosely (paint.net's
antialiasing softens the edges):

    red     impassable desert: desert terrain, and the state it covers most of is impassable (`impassable = yes`)
    yellow  desert: desert terrain
    green   jungle: jungle terrain

Used by read_layers.py (terrain, impassable states), pdn_tools.py areas (larger provinces there) and pdn_tools.py
refine (which leaves those states as sparse as they are).
"""
import numpy as np

LAYER_NAMES = ("Impassible", "Impassable", "Desert")
KINDS = ("impassable", "desert", "jungle")
# terrain.bmp palette index each kind paints (source/palettes/terrain.bmp.header.bin: 3 is desert, 22 jungle)
TERRAIN = {"impassable": 3, "desert": 3, "jungle": 22}
# province size there, px (docs/EDITING.md's empty land, 300 to 800 px; impassable land larger, as the base game's
# Sahara): Claude's choice, 2026-10-18, the author asked for no number
PROVINCE_PX = {"impassable": 1500, "desert": 600, "jungle": 400}


def layer_name(names):
    for nm in names:
        if nm.startswith(LAYER_NAMES):
            return nm
    return None


def masks(layer, land=None):
    """kind -> bool mask of the pixels marked as that kind (on land, when land is given)"""
    if layer is None:
        return {}
    r, g, b = (layer[..., i].astype(int) for i in range(3))
    on = layer[..., 3] > 127
    out = {"impassable": on & (r > 180) & (g < 110) & (b < 110),
           "desert": on & (r > 180) & (g >= 150) & (b < 110),
           "jungle": on & (g > r + 40) & (g > b + 40)}
    if land is not None:
        out = {k: m & land for k, m in out.items()}
    return out
