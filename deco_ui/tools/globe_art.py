"""Valsora's land for the Deco UI's globes (v0.8): art/valsora_land.png and the gilt globe gen_textures.py draws
from it (the news masthead's medallion).

    python globe_art.py          -> art/valsora_land.png, from the Valsora build's terrain.bmp (run after map changes)

The land is the game map's (terrain.bmp: index 15 is water), equirectangular (row 0 north, x -180..180 degrees), at
1440 x 720, kept in art/ so the textures don't need a Valsora build. globe() turns it into a small globe in the
Deco UI's flat style (v0.8.1: the first, lit and with every lake and channel, read as a speckled blob at 50 px).
VIEW is the Valsora mod's world tension globe's (above Nonscio and Araseos); the masthead's looks down on open sea
with land round it (gen_textures.NEWS_VIEW, 30 W 25 N), which reads more readily as a globe.
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


def simplified(sigma_deg=1.2):
    """the land as a globe this small can show (v0.8.1): smoothed by sigma_deg degrees and thresholded, its lakes
    filled and its specks dropped, so the coasts read as shapes instead of speckle"""
    land = np.asarray(Image.open(LAND), dtype=np.float32) / 255
    s = sigma_deg * land.shape[1] / 360
    m = ndi.binary_fill_holes(ndi.gaussian_filter(land, s, mode="wrap") > .5)
    lab, n = ndi.label(m)
    sizes = ndi.sum(m, lab, range(1, n + 1))
    keep = np.isin(lab, 1 + np.flatnonzero(sizes > (3 * s) ** 2))
    return ndi.gaussian_filter(keep.astype(np.float32), s * .35, mode="wrap")


def globe(d, view=VIEW, k=8, grid=30, sigma=1.2):
    """an RGBA image d x d px (drawn at k times, then reduced), in the Deco UI's flat style (v0.8.1): the land
    simplified for its size, in the masthead letters' gilt gradient (light at the top) with a soft limb, a thin dark
    coast, a lacquer sea, and a graticule every `grid` degrees, gilt over the sea and faint over the land. No rim (the
    texture draws it in SVG, crisp)."""
    n = d * k
    land = simplified(sigma)
    inside, lon, lat, u, v, z = _sphere(n, view)
    frac = np.clip((_sample(land, lon, lat) - .5) / .12 + .5, 0, 1)
    t = ((1 - v) / 2)[..., None]
    top, mid, bot = (np.array(c, np.float32) for c in ((255, 243, 200), (227, 199, 126), (156, 120, 54)))
    landc = np.where(t < .45, top + (mid - top) * (t / .45), mid + (bot - mid) * ((t - .45) / .55)) / 255
    landc = landc * (.78 + .22 * z)[..., None]
    sea = np.array([17, 25, 30], np.float32) / 255 * (.85 + .3 * z)[..., None]
    col = sea * (1 - frac[..., None]) + landc * frac[..., None]
    edge = np.clip(ndi.gaussian_gradient_magnitude(frac, k * .5) * k * 1.1, 0, 1)     # the coast, dark
    col = col * (1 - .55 * edge[..., None])
    w = .55 * k / n * 360 / np.pi          # about half a final pixel, in degrees at the centre
    near = lambda a: np.abs(((a + grid / 2) % grid) - grid / 2)
    g = np.maximum(np.clip(1 - near(lon) * np.cos(np.radians(lat)) / w, 0, 1), np.clip(1 - near(lat) / w, 0, 1))
    g = g * (.35 + .65 * z)
    over_sea, over_land = (g * (1 - frac) * .55)[..., None], (g * frac * .25)[..., None]
    col = col * (1 - over_sea) + np.array([201, 165, 90], np.float32) / 255 * over_sea
    col = col * (1 - over_land)
    rgba = np.dstack([np.clip(col, 0, 1), inside.astype(np.float32)])
    return Image.fromarray((rgba * 255).astype(np.uint8), "RGBA").reduce(k)


if __name__ == "__main__":
    write_land()
    globe(60, (-30, 25)).resize((360, 360), Image.LANCZOS).save(os.path.join(os.path.dirname(LAND), "..", "build", "globe_test.png"))
