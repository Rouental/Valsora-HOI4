"""The minimap in the lower right corner: Valsora instead of vanilla's Earth.

Vanilla draws it from gfx/minimap/minimap.dds (sprite GFX_minimap_world, defined in
vanilla's interface/unitview.gfx) at the texture's own size, inside a frame,
gfx/minimap/border.dds, and maps the whole world onto it for the camera rectangle.
Vanilla's is 268 x 97 px for its 2.75 : 1 map; Valsora's map is 2 : 1, so ours is
194 x 97, with the window moved right to meet the map-mode panel (80 px wide) and the
slide that hides it (ctrl+m) shortened to match, as Equestria at War does for its own
2 : 1 minimap (195 x 97). The picture is a parchment map in the spirit of vanilla's:
pale land on darker paper, inked coasts. The frame is our own: a thin dark metal rim.
"""
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

from imgio import write_dds

GUI = Path("source/interface/vanilla_minimap.gui")  # vanilla 1.19.3's
HEIGHT = 97          # vanilla's minimap height (its window sits 98 px above the bottom)
PANEL = 80           # the map-mode buttons to the right of the minimap
LEFT, TOP, RIGHT, BOTTOM = 5, 5, 6, 3  # frame margins round the picture (it is drawn at -5, -5)
POSITION = '\t\tposition = { x=-343 y=-98 }'


def size(map_w, map_h):
    return round(HEIGHT * map_w / map_h), HEIGHT


def smooth_noise(shape, scale, seed):
    """Paper grain: random values on a coarse grid, smoothly enlarged."""
    rng = np.random.default_rng(seed)
    h, w = shape
    g = rng.random((h // scale + 2, w // scale + 2)).astype(np.float32)
    big = np.asarray(Image.fromarray(g).resize((g.shape[1] * scale, g.shape[0] * scale), Image.BICUBIC))
    return big[:h, :w] - 0.5


def picture(land, w, h):
    """land: the game map's land mask (row 0 = north). Returns h x w x 4 uint8."""
    k = 4  # drawn at 4x, then reduced
    W, H = w * k, h * k
    frac = np.asarray(Image.fromarray((land * 255).astype(np.uint8)).resize((W, H), Image.BOX)) / 255.0
    frac = ndi.gaussian_filter(frac, 0.7)
    on = frac >= 0.5
    d_in = ndi.distance_transform_edt(on)    # inside the land, from the coast
    d_out = ndi.distance_transform_edt(~on)  # out at sea, from the coast
    grain = sum(smooth_noise((H, W), s, 1013 + s) * a for s, a in ((3, 0.35), (9, 0.4), (27, 0.6)))
    sea = np.array([118, 108, 92], float) * (1 + 0.07 * np.exp(-d_out / 5))[..., None]  # paler offshore
    paper = np.array([210, 198, 172], float) * (1 - 0.10 * np.exp(-d_in / 3))[..., None]  # shaded coasts
    col = sea * (1 - frac[..., None]) + paper * frac[..., None]
    col += grain[..., None] * np.array([26, 24, 20])
    # inked coastline
    edge = np.clip(np.hypot(ndi.sobel(frac, 0), ndi.sobel(frac, 1)) * 0.9, 0, 1)
    col = col * (1 - 0.55 * edge[..., None]) + np.array([70, 60, 48]) * 0.55 * edge[..., None]
    # a little darker towards the edges, like old paper
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2))
    col *= (1 - 0.18 * np.clip(r - 0.55, 0, None) ** 1.5)[..., None]
    small = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).resize((w, h), Image.LANCZOS)
    return np.dstack([np.asarray(small), np.full((h, w), 255, np.uint8)])


def frame(w, h):
    """A thin dark metal rim round a w x h picture, transparent inside."""
    fw, fh = w + LEFT + RIGHT, h + TOP + BOTTOM
    yy, xx = np.mgrid[0:fh, 0:fw]
    # distance outwards from the picture's edge (0 on its first pixel row/column outside)
    dx = np.maximum(LEFT - 1 - xx, xx - (LEFT + w))
    dy = np.maximum(TOP - 1 - yy, yy - (TOP + h))
    d = np.maximum(dx, dy)  # >= 0 outside the picture, < 0 inside
    rgba = np.zeros((fh, fw, 4), float)
    ring = (d >= 0) & (d <= 2)
    # the rim: dark, a lighter middle line (brighter at the top and left), dark again
    tone = np.select([d == 0, d == 1, d == 2], [34.0, 96.0, 22.0], 0.0)
    lit = np.where(((xx < LEFT) & (dx >= dy)) | ((yy < TOP) & (dy >= dx)), 1.15, 0.85)  # bevel
    tone = np.where(d == 1, tone * lit, tone)
    rgba[ring, :3] = np.stack([tone, tone * 0.98, tone * 0.9], -1)[ring]
    rgba[ring, 3] = 255
    # a soft shadow outside the rim, and a faint one cast onto the picture's edge
    out = d >= 3
    rgba[out, 3] = np.clip(150 - (d[out] - 3) * 60, 0, 255)
    inside = d < 0
    rgba[inside, 3] = np.clip(90 + (d[inside] + 1) * 30, 0, 255)  # 90, 60, 30 px in, then 0
    # rounded outer corners
    for cy, cx in ((0, 0), (0, fw - 1), (fh - 1, 0), (fh - 1, fw - 1)):
        rgba[cy, cx, 3] = 0
    return np.clip(rgba, 0, 255).astype(np.uint8)


def gui(w):
    s = GUI.read_text(encoding="utf-8")
    if s.count(POSITION) != 1:
        raise SystemExit(f"{GUI}: the minimap window's position line was not found as expected")
    return s.replace(POSITION, f'\t\tposition = {{ x=-{w + PANEL} y=-{HEIGHT + 1} }}')


BOOKMARK = (180, 104)  # vanilla's start date pictures (gfx/interface/select_date_1936.dds)


def write_bookmark(write, out, land):
    """The start date's picture (single player's date screen): vanilla's shows 1936's soldiers over
    Europe; ours is Valsora on the minimap's parchment, darkened at the edges like vanilla's."""
    w, h = BOOKMARK
    pic = picture(land, round(h * land.shape[1] / land.shape[0]), h).astype(float)
    x0 = (pic.shape[1] - w) // 2
    pic = pic[:, x0:x0 + w]
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.hypot((xx - w / 2) / (w / 2), (yy - h / 2) / (h / 2))
    pic[..., :3] *= (1 - 0.45 * np.clip(r - 0.45, 0, None) ** 1.3)[..., None]
    d = out / "gfx/interface"
    d.mkdir(parents=True, exist_ok=True)
    write_dds(d / "valsora_select_date.dds", np.clip(pic, 0, 255).astype(np.uint8))
    write("interface/valsora_bookmark.gfx", 'spriteTypes = {\n\tspriteType = {\n\t\tname = "GFX_select_date_valsora"\n'
          '\t\ttexturefile = "gfx/interface/valsora_select_date.dds"\n\t}\n}\n')


def write_files(write, out, land):
    h_map, w_map = land.shape
    w, h = size(w_map, h_map)
    d = out / "gfx/minimap"
    d.mkdir(parents=True, exist_ok=True)
    write_dds(d / "minimap.dds", picture(land, w, h))
    write_dds(d / "border.dds", frame(w, h))
    write("interface/minimap.gui", gui(w))
    write("common/defines/valsora_graphics.lua",
          "-- the minimap slides this far right to hide it (vanilla 270, for its wider minimap)\n"
          f"NDefines_Graphics.NInterface.MINIMAP_TOGGLE_SHIFT = {w + 8}\n")
