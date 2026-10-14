"""The world tension globe in the top bar (and its small icon): Valsora instead of Earth.

Vanilla's is a strip of ten 49 x 49 frames, gfx/interface/world_tension_icon_big_strip.dds
(sprite GFX_world_tension_icon_big_strip in vanilla's interface/topbar.gfx): the same view
of Earth, more of it on fire at each tenth of world tension. The small icon,
gfx/interface/world_tension_icon.dds (29 x 25, the diplomacy view and the peace conference),
is a globe ringed with flames. Ours draw Valsora's land on a lit sphere, seen from above
Nonscio and Araseos, with the same fire rising from below as tension grows.
"""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

from imgio import write_dds

FRAMES, SIZE = 10, 49          # vanilla's strip: 10 frames of 49 x 49
SMALL = (29, 25)               # vanilla's small icon
VIEW = (-95.0, 22.0)           # longitude, latitude at the centre of the globe
K = 4                          # drawn at 4x, then reduced

SEA_DEEP, SEA_SHALLOW = np.array([18, 84, 118]), np.array([58, 168, 186])
LAND_LOW, LAND_HIGH = np.array([92, 120, 70]), np.array([150, 140, 96])
ICE = np.array([226, 232, 236])


def _noise(shape, scale, seed, stretch=1.0):
    """Smooth random field in [-0.5, 0.5]; stretch > 1 draws it out vertically (flames)."""
    rng = np.random.default_rng(seed)
    h, w = shape
    sx, sy = scale, max(1, round(scale * stretch))
    g = rng.random((h // sy + 3, w // sx + 3)).astype(np.float32)
    big = np.asarray(Image.fromarray(g).resize((g.shape[1] * sx, g.shape[0] * sy), Image.BICUBIC))
    return big[:h, :w] - 0.5


def _fractal(shape, seed, scales=(3, 7, 17, 41), stretch=1.0):
    out = sum(_noise(shape, s, seed + s, stretch) * (s ** 0.6) for s in scales)
    return out / np.abs(out).max()


def _sphere(n, view):
    """Inverse orthographic projection of an n x n disc: (inside, lon, lat, normal x, y, z)."""
    lon0, lat0 = np.radians(view[0]), np.radians(view[1])
    c = (np.arange(n) + 0.5) / n * 2 - 1
    u, v = np.meshgrid(c, -c)                      # v points up
    rho = np.hypot(u, v)
    inside = rho < 1
    z = np.sqrt(np.clip(1 - rho ** 2, 0, 1))
    cc = np.arcsin(np.clip(rho, 0, 1))
    with np.errstate(invalid="ignore", divide="ignore"):
        lat = np.arcsin(np.clip(np.cos(cc) * np.sin(lat0) + np.where(rho > 0, v * np.sin(cc) * np.cos(lat0) / rho, 0), -1, 1))
        lon = lon0 + np.arctan2(u * np.sin(cc), rho * np.cos(cc) * np.cos(lat0) - v * np.sin(cc) * np.sin(lat0))
    return inside, np.degrees(lon), np.degrees(lat), u, v, z


def _sample(field, lon, lat):
    """Bilinear sample of an equirectangular field (row 0 = north, x = -180..180) at lon/lat."""
    h, w = field.shape
    x = ((lon + 180) % 360) / 360 * w - 0.5
    y = (90 - lat) / 180 * h - 0.5
    return ndi.map_coordinates(field, [y, x], order=1, mode="wrap")


def _globe(land, n, view, level, seed=11):
    """RGBA n x n globe (n at the final size times K). level 0..1: how much is burning."""
    inside, lon, lat, u, v, z = _sphere(n, view)
    frac = _sample(land, lon, lat)
    near = _sample(ndi.gaussian_filter(land, 6), lon, lat)            # shallow water near coasts
    grain = _fractal((n, n), seed)
    sea = SEA_DEEP + (SEA_SHALLOW - SEA_DEEP) * np.clip(near * 1.6, 0, 1)[..., None]
    land_col = LAND_LOW + (LAND_HIGH - LAND_LOW) * np.clip(0.5 + grain * 0.8, 0, 1)[..., None]
    polar = np.clip((np.abs(lat) - 68) / 10, 0, 1)[..., None]          # ice caps
    land_col = land_col * (1 - polar) + ICE * polar
    col = sea * (1 - frac[..., None]) + land_col * frac[..., None]
    # light from the upper left, a glint on the sea, darker towards the rim
    nl = np.stack([u, v, z], -1)
    light = np.array([-0.55, 0.6, 0.58]); light /= np.linalg.norm(light)
    lam = np.clip((nl * light).sum(-1), 0, 1)
    col = col * (0.28 + 0.85 * lam)[..., None]
    half = light + np.array([0, 0, 1.0]); half /= np.linalg.norm(half)
    spec = np.clip((nl * half).sum(-1), 0, 1) ** 40 * (1 - frac) * 120
    col = col + spec[..., None]
    # fire: rises from the bottom along a noise field; level is the share of the disc burning
    if level > 0:
        heat = _fractal((n, n), seed + 100, (5, 11, 23), 2.6) * 0.55 + (-v) * 0.45  # flames rise
        front = np.quantile(heat[inside], 1 - 0.93 * level)
        burn = np.clip((heat - front) / 0.06, 0, 1)
        edge = np.exp(-((heat - front) / 0.05) ** 2)                            # flames at the front
        # inside the fire: red and orange tongues over darker char, yellow where hottest and lowest
        t = np.clip(0.55 + _fractal((n, n), seed + 300, (3, 7, 13), 2.2) * 0.8 + (-v) * 0.15, 0, 1)
        fire = np.array([70, 14, 6]) * (1 - t)[..., None] + np.array([226, 70, 14]) * t[..., None]
        fire = fire + np.array([255, 190, 70]) * (np.clip(t - 0.6, 0, 1) / 0.4)[..., None] * 0.9
        fire = fire * (0.6 + 0.6 * lam)[..., None]
        col = col * (1 - burn[..., None]) + fire * burn[..., None]
        col = col + np.array([255, 150, 40]) * (edge * 0.85)[..., None]
        # glowing cracks running ahead of the front
        veins = np.clip(1 - np.abs(_fractal((n, n), seed + 200, (4, 9)) * 7), 0, 1)
        ahead = np.clip(1 - (front - heat) / 0.25, 0, 1) * (1 - burn)
        col = col + np.array([240, 90, 20]) * (veins * ahead * min(1.0, level * 3) * 0.8)[..., None]
    # thin bright atmosphere at the rim
    rim = np.clip((np.hypot(u, v) - 0.9) / 0.1, 0, 1) ** 2
    col = col + np.array([120, 190, 220]) * (rim * 0.45)[..., None]
    a = inside.astype(float) * 255
    return np.dstack([np.clip(col, 0, 255), a])


def _reduce(rgba, size):
    """Premultiplied downsampling, so the transparent outside does not darken the rim."""
    a = rgba[..., 3:4] / 255
    pm = np.dstack([rgba[..., :3] * a, rgba[..., 3:]]).astype(np.float32)
    chans = [np.asarray(Image.fromarray(pm[..., i]).resize(size, Image.BOX)) for i in range(4)]
    out = np.stack(chans, -1)
    alpha = out[..., 3:4] / 255
    rgb = np.where(alpha > 0, out[..., :3] / np.maximum(alpha, 1e-6), 0)
    return np.clip(np.dstack([rgb, out[..., 3:]]), 0, 255).astype(np.uint8)


def strip(land):
    """The ten 49 x 49 frames side by side, calm to ablaze."""
    # slow at first, as vanilla's: a little smoke at low tension, ablaze near the top
    frames = [_reduce(_globe(land, SIZE * K, VIEW, (i / (FRAMES - 1)) ** 1.6), (SIZE, SIZE)) for i in range(FRAMES)]
    return np.concatenate(frames, axis=1)


def small(land):
    """29 x 25: a 17 px globe low in the icon, tongues of flame rising round it."""
    w, h = SMALL
    W, H = w * K, h * K
    out = np.zeros((H, W, 4), float)
    d = 17 * K
    g = _globe(land, d, VIEW, 0)
    cx, cy = W // 2, H - d // 2 - 2 * K
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.hypot(xx - cx, yy - cy) / (d / 2)
    ang = np.arctan2(yy - cy, xx - cx)
    rng = np.random.default_rng(5)
    tongues = np.clip(np.cos(ang * 7 + rng.random() * 6.3), 0, 1) ** 3 * 0.55 + \
        np.clip(np.cos(ang * 11 + rng.random() * 6.3), 0, 1) ** 3 * 0.25
    up = np.clip(-np.sin(ang) + 0.3, 0, 1)                  # the flames lick upwards
    reach = 1.05 + (0.1 + tongues) * up
    flame = np.clip((reach - r) / 0.1, 0, 1) * (r > 0.85)
    t = np.clip((r - 0.9) / np.maximum(reach - 0.9, 1e-6), 0, 1)   # base to tip
    fcol = np.array([190, 36, 10]) * (1 - t)[..., None] + np.array([255, 214, 96]) * t[..., None]
    out[..., :3] = fcol
    out[..., 3] = flame * 240
    y0, x0 = cy - d // 2, cx - d // 2
    region = out[y0:y0 + d, x0:x0 + d]
    ga = g[..., 3:4] / 255
    region[..., :3] = g[..., :3] * ga + region[..., :3] * (1 - ga)
    region[..., 3] = np.maximum(region[..., 3], g[..., 3])
    return _reduce(out, SMALL)


def write_files(out, land):
    """land: the game map's land mask (row 0 = north, 5120 x 2560)."""
    f = np.asarray(Image.fromarray((land * 255).astype(np.uint8)).resize((1280, 640), Image.BOX)) / 255.0
    d = out / "gfx/interface"
    d.mkdir(parents=True, exist_ok=True)
    write_dds(d / "world_tension_icon_big_strip.dds", strip(f))
    write_dds(d / "world_tension_icon.dds", small(f))


if __name__ == "__main__":
    # a preview of the built textures for the author: dist/tension_globe_preview.png
    from pathlib import Path
    from PIL import ImageDraw
    mod = Path("build/valsora_test/gfx/interface")
    big = Image.open(mod / "world_tension_icon_big_strip.dds").convert("RGBA")
    sm = Image.open(mod / "world_tension_icon.dds").convert("RGBA")
    z = 3
    canvas = Image.new("RGBA", (big.width * z + 40, big.height * z + sm.height * z + 90), (22, 30, 36, 255))
    canvas.alpha_composite(big.resize((big.width * z, big.height * z), Image.NEAREST), (20, 40))
    canvas.alpha_composite(sm.resize((sm.width * z, sm.height * z), Image.NEAREST), (20, 60 + big.height * z))
    d = ImageDraw.Draw(canvas)
    d.text((20, 12), "World tension 0% to 100% (top bar, 3x)", fill=(230, 210, 160, 255))
    d.text((40 + sm.width * z, 60 + big.height * z + 30), "small icon (diplomacy, peace conference, 3x)",
           fill=(230, 210, 160, 255))
    canvas.convert("RGB").save("dist/tension_globe_preview.png")
    print("wrote dist/tension_globe_preview.png")
