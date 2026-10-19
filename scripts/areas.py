"""The author's areas layer: land they marked impassable, desert or jungle (2026-10-18, the author: "I've tried to mark
out the regions that are desert / impassible desert in Usnistan. Red is impassible desert, yellow is regular desert").

The layer is the one whose name starts with one of LAYER_NAMES ("Impassible / Desert / Jungle / Tundra" in the author's
.pdn, "Desert" in an earlier upload). Each area is painted solid in its colour, matched loosely (paint.net's
antialiasing softens the edges):

    red     impassable desert: desert terrain, and the state it covers most of is impassable (`impassable = yes`)
    yellow  desert: desert terrain
    green   jungle: jungle terrain
    green with red stripes   impassable jungle (the author, 2026-10-19: "my idea with the red and green striped region
            of the Cultist territory is that it is impassible jungle"): jungle terrain, impassable as the red

Used by read_layers.py (terrain, impassable states), pdn_tools.py areas (larger provinces there) and pdn_tools.py
refine (which leaves those states as sparse as they are).
"""
import numpy as np
from scipy import ndimage as ndi

LAYER_NAMES = ("Impassible", "Impassable", "Desert")
KINDS = ("impassable", "impassable_jungle", "desert", "jungle")
IMPASSABLE = ("impassable", "impassable_jungle")
# terrain.bmp palette index each kind paints (source/palettes/terrain.bmp.header.bin: 3 is desert, 22 jungle)
TERRAIN = {"impassable": 3, "impassable_jungle": 22, "desert": 3, "jungle": 22}
# province size there, px (docs/EDITING.md's empty land, 300 to 800 px: Claude's choice, 2026-10-18). Impassable land is
# one province a state, whatever its size (None; the author, 2026-10-18: "By impassible I mean like the big African
# deserts that are one massive province"), the rivers through it scenery
PROVINCE_PX = {"impassable": None, "impassable_jungle": None, "desert": 600, "jungle": 400}


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
    red = on & (r > 180) & (g < 110) & (b < 110)
    green = on & (g > r + 40) & (g > b + 40)
    # a patch of green with red stripes through it is impassable jungle: the whole patch, stripes and field
    striped = np.zeros(red.shape, bool)
    lab, n = ndi.label(red | green, structure=np.ones((3, 3)))
    if n:
        nr = np.bincount(lab.ravel(), weights=red.ravel(), minlength=n + 1)
        ng = np.bincount(lab.ravel(), weights=green.ravel(), minlength=n + 1)
        tot = nr + ng
        keep = (tot > 0) & (nr > 0.03 * tot) & (ng > 0.3 * tot)
        keep[0] = False
        striped = keep[lab]
    out = {"impassable": red & ~striped,
           "impassable_jungle": striped,
           "desert": on & (r > 180) & (g >= 150) & (b < 110),
           "jungle": green & ~striped}
    if land is not None:
        out = {k: m & land for k, m in out.items()}
    return out
