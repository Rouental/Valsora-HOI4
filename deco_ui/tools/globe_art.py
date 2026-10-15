"""Valsora's land for the Deco UI's globes (v0.8): art/valsora_land.png and the gilt globe gen_textures.py draws
from it (the news masthead's medallion); the other globes proposals_globes.py shows the user (v0.8.2).

    python globe_art.py          -> art/valsora_land.png, from the Valsora build's terrain.bmp (run after map changes)

The land is the game map's (terrain.bmp: index 15 is water), equirectangular (row 0 north, x -180..180 degrees), at
1440 x 720, kept in art/ so the textures don't need a Valsora build. globe() turns it into a small globe in the
Deco UI's style (v0.8.1: the first, lit and with every lake and channel, read as a speckled blob at 50 px; v0.8.2:
lit again, the land still simplified). VIEW is the Valsora mod's world tension globe's (above Nonscio and Araseos),
which the masthead shares since v0.8.2 (layout_events.NEWS_VIEW).
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


def _rgba(col, alpha, k):
    rgba = np.dstack([np.clip(col, 0, 1), alpha.astype(np.float32)])
    return Image.fromarray((rgba * 255).astype(np.uint8), "RGBA").reduce(k)


def _graticule(lon, lat, n, k, grid, pole=90):
    """meridians and parallels every `grid` degrees, about a final pixel wide, the meridians stopping at `pole`"""
    w = .5 * k / n * 360 / np.pi          # about half a final pixel, in degrees at the centre
    near = lambda a: np.abs(((a + grid / 2) % grid) - grid / 2)
    mer = np.clip(1 - near(lon) * np.cos(np.radians(lat)) / w, 0, 1) * (np.abs(lat) < pole)
    par = np.clip(1 - near(lat) / w, 0, 1) * (np.abs(lat) < pole + 1)
    return np.maximum(mer, par)


GILT = [np.array(c, np.float32) / 255 for c in ((255, 243, 200), (227, 199, 126), (139, 106, 44))]


def _gilt(t, top_end=.4, bot=None):
    """the masthead letters' gilt gradient at t (0 light .. 1 dark)"""
    top, mid, deep = GILT
    bot = deep if bot is None else np.array(bot, np.float32) / 255
    t = t[..., None]
    return np.where(t < top_end, top + (mid - top) * (t / top_end), mid + (bot - mid) * ((t - top_end) / (1 - top_end)))


def globe(d, view=VIEW, k=8, grid=30, sigma=.9, pole=72):
    """an RGBA image d x d px (drawn at k times, then reduced), in the Deco UI's style (v0.8.2, the user on v0.8.1's:
    "I'm not quite satisfied with the globe"): v0.8.1's simplified gilt land and lacquer sea, now lit from the upper
    left (the land from pale to deep gilt, the sea from lacquer to near black), with a bright limb on the lit side; the
    graticule over the sea only, its meridians stopping short of the pole (where they bunched into a star). No rim (the
    texture draws it in SVG, crisp)."""
    n = d * k
    land = simplified(sigma)
    inside, lon, lat, u, v, z = _sphere(n, view)
    frac = np.clip((_sample(land, lon, lat) - .5) / .12 + .5, 0, 1)
    light = np.array([-.45, .55, .70])
    light = light / np.linalg.norm(light)
    lam = np.clip(u * light[0] + v * light[1] + z * light[2], 0, 1)
    landc = _gilt(1 - (.35 + .65 * lam))
    sea_hi, sea_lo = np.array([34, 50, 58], np.float32) / 255, np.array([9, 13, 16], np.float32) / 255
    sea = sea_lo + (sea_hi - sea_lo) * (lam ** 2)[..., None]
    col = sea * (1 - frac[..., None]) + landc * frac[..., None]
    edge = np.clip(ndi.gaussian_gradient_magnitude(frac, k * .5) * k * 1.1, 0, 1)     # the coast, dark
    col = col * (1 - .5 * edge[..., None])
    g = _graticule(lon, lat, n, k, grid, pole) * (.25 + .75 * z) * (1 - frac) * .5
    col = col * (1 - g[..., None]) + np.array([201, 165, 90], np.float32) / 255 * g[..., None]
    rho = np.hypot(u, v)
    rim = np.clip((rho - .9) / .1, 0, 1) ** 2
    lit_side = np.clip((-u * .6 + v * .8) * .9 + .2, 0, 1)
    col = col * (1 - rim[..., None] * .5 * (1 - lit_side[..., None]))
    col = col + (np.array([241, 220, 156], np.float32) / 255 - col) * (rim * lit_side * .55)[..., None]
    return _rgba(col, inside, k)


# ------------------------------------------------ other globes, for the user to choose from (proposals_globes.py)

def globe_first(d, view=VIEW, k=8, grid=30):
    """the first (v0.7.1 to v0.8): every lake and channel, lit from the upper left, a bright coast, a faint graticule
    over the sea"""
    n = d * k
    land = np.asarray(Image.open(LAND), dtype=np.float32) / 255
    inside, lon, lat, u, v, z = _sphere(n, view)
    frac = np.clip((_sample(land, lon, lat) - .35) / .3, 0, 1)
    light = np.clip(.55 + .45 * (-.45 * u + .55 * v + .7 * z), 0, 1)
    sea = np.array([14, 21, 25], np.float32) / 255 * (.75 + .5 * light[..., None])
    sea = sea + np.array([30, 42, 49], np.float32) / 255 * (light[..., None] ** 3) * .5
    gilt_lo, gilt_hi = np.array([139, 106, 44], np.float32) / 255, np.array([241, 220, 156], np.float32) / 255
    landc = gilt_lo + (gilt_hi - gilt_lo) * light[..., None]
    col = sea * (1 - frac[..., None]) + landc * frac[..., None]
    edge = np.clip(ndi.gaussian_gradient_magnitude(frac, k * .45) * k * .9, 0, 1)
    col = col * (1 - edge[..., None] * .7) + gilt_hi * edge[..., None] * .7
    g = _graticule(lon, lat, n, k, grid) * (1 - frac) * .35 * z
    col = col * (1 - g[..., None]) + np.array([201, 165, 90], np.float32) / 255 * g[..., None]
    return _rgba(col, inside, k)


def globe_flat(d, view=(-30.0, 25.0), k=8, grid=30, sigma=1.2):
    """v0.8.1's: the land simplified, flat gilt (light at the top), a soft limb, a graticule over sea and land"""
    n = d * k
    land = simplified(sigma)
    inside, lon, lat, u, v, z = _sphere(n, view)
    frac = np.clip((_sample(land, lon, lat) - .5) / .12 + .5, 0, 1)
    landc = _gilt((1 - v) / 2, .45, (156, 120, 54)) * (.78 + .22 * z)[..., None]
    sea = np.array([17, 25, 30], np.float32) / 255 * (.85 + .3 * z)[..., None]
    col = sea * (1 - frac[..., None]) + landc * frac[..., None]
    edge = np.clip(ndi.gaussian_gradient_magnitude(frac, k * .5) * k * 1.1, 0, 1)
    col = col * (1 - .55 * edge[..., None])
    g = _graticule(lon, lat, n, k, grid) * (.35 + .65 * z)
    over_sea, over_land = (g * (1 - frac) * .55)[..., None], (g * frac * .25)[..., None]
    col = col * (1 - over_sea) + np.array([201, 165, 90], np.float32) / 255 * over_sea
    col = col * (1 - over_land)
    return _rgba(col, inside, k)


def _ellipse(xs, ys, cx, cy, rx, ry, tilt):
    """(x/rx)^2 + (y/ry)^2 in the frame of an ellipse tilted by `tilt` degrees"""
    t = np.radians(tilt)
    dx, dy = xs - cx, ys - cy
    x, y = dx * np.cos(t) + dy * np.sin(t), -dx * np.sin(t) + dy * np.cos(t)
    return (x / rx) ** 2 + (y / ry) ** 2, y


def globe_ringed(d, view=VIEW, k=8, scale=.72, tilt=-16):
    """a newsreel globe: the lit globe a little smaller, girdled by a tilted gilt ring (behind it at the back, over it
    in front), like the studio globes of the 1930s newsreels"""
    n = d * k
    gd = int(round(d * scale))
    g = np.asarray(globe(gd, view, k), np.float32) / 255
    out = np.zeros((d * k, d * k, 4), np.float32)
    big = np.asarray(Image.fromarray((g * 255).astype(np.uint8), "RGBA").resize((gd * k, gd * k), Image.LANCZOS),
                     np.float32) / 255
    o = (n - gd * k) // 2
    ys, xs = np.mgrid[0:n, 0:n].astype(np.float32) + .5
    c = n / 2
    e_out, yy = _ellipse(xs, ys, c, c, n * .49, n * .17, tilt)
    e_in, _ = _ellipse(xs, ys, c, c, n * .49 - 3.4 * k, n * .17 - 2.2 * k, tilt)
    band = (e_out <= 1) & (e_in > 1)
    keep = (e_out <= 1.06) & (e_in > .9) & ~band        # a dark line round the band, to part it from the globe
    behind = yy < 0
    shade = np.clip(.55 + .45 * (xs - c) / (n * .49) * -1, .25, 1)      # lit from the left
    ring = _gilt(1 - shade)
    def put(mask, rgb, a=1.0):
        m = mask.astype(np.float32) * a
        out[..., :3] = out[..., :3] * (1 - m[..., None]) + rgb * m[..., None]
        out[..., 3] = np.maximum(out[..., 3], m)
    put(band & behind, ring, .9)
    put(keep & behind, np.array([11, 16, 20], np.float32) / 255, .9)
    gl = np.zeros_like(out)
    gl[o:o + gd * k, o:o + gd * k] = big
    a = gl[..., 3:4]
    out[..., :3] = out[..., :3] * (1 - a) + gl[..., :3] * a
    out[..., 3] = np.maximum(out[..., 3], gl[..., 3])
    put(keep & ~behind, np.array([11, 16, 20], np.float32) / 255)
    put(band & ~behind, ring)
    pre = out.copy()
    pre[..., :3] *= pre[..., 3:4]
    pre = pre.reshape(d, k, d, k, 4).mean(axis=(1, 3))
    with np.errstate(invalid="ignore", divide="ignore"):
        pre[..., :3] = np.where(pre[..., 3:4] > 0, pre[..., :3] / pre[..., 3:4], 0)
    return Image.fromarray((np.clip(pre, 0, 1) * 255).astype(np.uint8), "RGBA")


def world_disc(d, k=8, reach=150, turn=-95, grid=30, spokes=45, sigma=.9):
    """the whole world on one disc, as on an emblem: an azimuthal map round the north pole out to `reach` degrees from
    it (60 S), the meridians as spokes and the parallels as rings, gilt land lit from the top"""
    n = d * k
    land = simplified(sigma)
    c = (np.arange(n) + .5) / n * 2 - 1
    u, v = np.meshgrid(c, -c)
    rho = np.hypot(u, v)
    inside = rho < 1
    lat = 90 - rho * reach
    lon = np.degrees(np.arctan2(u, -v)) + turn
    frac = np.clip((_sample(land, lon, lat) - .5) / .12 + .5, 0, 1)
    landc = _gilt(np.clip((1 - v) / 2, 0, 1), .45)
    sea = np.array([17, 25, 30], np.float32) / 255 * (1.15 - .3 * rho)[..., None]
    col = sea * (1 - frac[..., None]) + landc * frac[..., None]
    edge = np.clip(ndi.gaussian_gradient_magnitude(frac, k * .5) * k * 1.1, 0, 1)
    col = col * (1 - .5 * edge[..., None])
    w = .5 * k / n * 2 * reach          # about half a final pixel, in degrees of latitude
    near = lambda a: np.abs(((a + grid / 2) % grid) - grid / 2)
    par = np.clip(1 - near(lat) / w, 0, 1)
    with np.errstate(invalid="ignore", divide="ignore"):
        spoke = lambda a: np.abs(((a + spokes / 2) % spokes) - spokes / 2)
        mer = np.clip(1 - spoke(lon - turn) * np.radians(1) * rho * n / 2 / (k * .5), 0, 1) * (rho > .22)
    g = np.maximum(par, mer) * (1 - frac) * .55
    col = col * (1 - g[..., None]) + np.array([201, 165, 90], np.float32) / 255 * g[..., None]
    return _rgba(col, inside, k)


def globe_engraved(d, view=VIEW, k=8, grid=30, sigma=.9):
    """an engraving: lacquer throughout, the land a shade lighter and drawn by its coast in bright gilt, the graticule
    in gilt over sea and land alike, as the line globes of deco emblems"""
    n = d * k
    land = simplified(sigma)
    inside, lon, lat, u, v, z = _sphere(n, view)
    frac = np.clip((_sample(land, lon, lat) - .5) / .12 + .5, 0, 1)
    sea = np.array([14, 20, 24], np.float32) / 255 * (.8 + .3 * z)[..., None]
    landc = np.array([58, 50, 34], np.float32) / 255 * (.75 + .35 * z)[..., None]
    col = sea * (1 - frac[..., None]) + landc * frac[..., None]
    edge = np.clip(ndi.gaussian_gradient_magnitude(frac, k * .45) * k * 1.6, 0, 1)
    coast = _gilt((1 - v) / 2, .45)
    col = col * (1 - edge[..., None]) + coast * edge[..., None]
    g = _graticule(lon, lat, n, k, grid, 72) * (.3 + .7 * z) * .6
    col = col * (1 - g[..., None]) + np.array([201, 165, 90], np.float32) / 255 * g[..., None]
    return _rgba(col, inside, k)


if __name__ == "__main__":
    write_land()
    globe(60, (-30, 25)).resize((360, 360), Image.LANCZOS).save(os.path.join(os.path.dirname(LAND), "..", "build", "globe_test.png"))
