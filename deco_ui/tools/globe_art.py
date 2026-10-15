"""Valsora's land for the Deco UI's globes (v0.7.1): art/valsora_land.png and the gilt line globe gen_textures.py
draws from it (the World News masthead).

    python globe_art.py          -> art/valsora_land.png, from the Valsora build's terrain.bmp (run after map changes)

The land is the game map's (terrain.bmp: index 15 is water), equirectangular (row 0 north, x -180..180 degrees), at
1440 x 720, kept in art/ so the textures don't need a Valsora build. globe() turns it into a small globe in the
Deco UI's line style: lacquer sea, gilt land, a brighter coast, a faint graticule, lit from the upper left; seen
from above Nonscio and Araseos, like the Valsora mod's world tension globe (scripts/globe.py there, VIEW).
"""
import os

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

from paths import ART, VALSORA

LAND = ART + "valsora_land.png"
VIEW = (-95.0, 22.0)          # longitude, latitude at the globe's centre (the tension globe's)


def write_land():
    t = np.asarray(Image.open(VALSORA + "map/terrain.bmp"))
    land = (t != 15).astype(np.uint8) * 255
    Image.fromarray(land).resize((1440, 720), Image.BOX).save(LAND, optimize=True)
    print("wrote", LAND)


def _sphere(n, view):
    """inverse orthographic projection of an n x n disc: inside, longitude, latitude, and the normal (u, v, z)"""
    lon0, lat0 = np.radians(view[0]), np.radians(view[1])
    c = (np.arange(n) + 0.5) / n * 2 - 1
    u, v = np.meshgrid(c, -c)
    rho = np.hypot(u, v)
    inside = rho < 1
    z = np.sqrt(np.clip(1 - rho ** 2, 0, 1))
    cc = np.arcsin(np.clip(rho, 0, 1))
    with np.errstate(invalid="ignore", divide="ignore"):
        lat = np.arcsin(np.clip(np.cos(cc) * np.sin(lat0) + np.where(rho > 0, v * np.sin(cc) * np.cos(lat0) / rho, 0), -1, 1))
        lon = lon0 + np.arctan2(u * np.sin(cc), rho * np.cos(cc) * np.cos(lat0) - v * np.sin(cc) * np.sin(lat0))
    return inside, np.degrees(lon), np.degrees(lat), u, v, z


def _sample(field, lon, lat):
    h, w = field.shape
    x = ((lon + 180) % 360) / 360 * w - 0.5
    y = (90 - lat) / 180 * h - 0.5
    return ndi.map_coordinates(field, [y, x], order=1, mode="wrap")


def globe(d, view=VIEW, k=8, grid=30):
    """an RGBA image d x d px (drawn at k times, then reduced): the globe inside a 1 px margin, no rim (the texture
    draws the rim in SVG, crisp)"""
    n = d * k
    land = np.asarray(Image.open(LAND), dtype=np.float32) / 255
    inside, lon, lat, u, v, z = _sphere(n, view)
    frac = np.clip((_sample(land, lon, lat) - .35) / .3, 0, 1)          # a crisp coast
    light = np.clip(.55 + .45 * (-.45 * u + .55 * v + .7 * z), 0, 1)   # lit from the upper left
    sea = np.array([14, 21, 25], np.float32) / 255 * (.75 + .5 * light[..., None])
    sea = sea + np.array([30, 42, 49], np.float32) / 255 * (light[..., None] ** 3) * .5
    gilt_lo, gilt_hi = np.array([139, 106, 44], np.float32) / 255, np.array([241, 220, 156], np.float32) / 255
    landc = gilt_lo + (gilt_hi - gilt_lo) * light[..., None]
    col = sea * (1 - frac[..., None]) + landc * frac[..., None]
    # the coast: a bright line where land meets sea
    edge = np.clip(ndi.gaussian_gradient_magnitude(frac, k * .45) * k * .9, 0, 1)
    col = col * (1 - edge[..., None] * .7) + gilt_hi * edge[..., None] * .7
    # the graticule: meridians and parallels every `grid` degrees, faint, over the sea only
    w = .5 * k / n * 360 / np.pi          # about half a final pixel, in degrees at the centre
    near = lambda a: np.abs(((a + grid / 2) % grid) - grid / 2)
    g = np.maximum(np.clip(1 - near(lon) * np.cos(np.radians(lat)) / w, 0, 1), np.clip(1 - near(lat) / w, 0, 1))
    g = g * (1 - frac) * .35 * z
    col = col * (1 - g[..., None]) + np.array([201, 165, 90], np.float32) / 255 * g[..., None]
    a = inside.astype(np.float32)
    rgba = np.dstack([np.clip(col, 0, 1), a])
    im = Image.fromarray((rgba * 255).astype(np.uint8), "RGBA")
    return im.reduce(k)


if __name__ == "__main__":
    write_land()
    globe(50).resize((300, 300), Image.LANCZOS).save(os.path.join(os.path.dirname(LAND), "..", "build", "globe_test.png"))
