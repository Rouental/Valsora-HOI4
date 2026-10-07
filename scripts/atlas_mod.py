"""The "Valsora: Atlas" submod: Valsora drawn like a printed atlas instead of a satellite map.

A separate graphics submod (author, 2026-10-07: "something to make the game look more
like an atlas than a digital map", and a mod of its own rather than a patch for
someone else's). Everything in it is drawn by this script; it copies nothing from any
other mod. It depends on Valsora only, so it loads after it and its files win.

What it changes, all without shader code (shaders can't be written without vanilla's
own files to start from):
- Land: cream laid paper with fibre grain, faint foxing and a fine ink coastline.
- Sea: pale blue-grey paper, engraved waterlines along every coast and lake shore, a
  15-degree graticule, each ocean's name lettered in spaced italic capitals, a compass
  rose and a title cartouche in the open ocean.
- Relief: no shading (world_normal.bmp is flat). The heightmap stays Valsora's.
- Terrain tiles (map/terrain/atlas*.dds): paper fibre instead of grass and rock; mud,
  sea-floor and sky-reflection textures neutral, water gloss off.
- Borders: country borders a dash-dot ink line, states dashed, provinces a faint dotted
  line, impassable borders hachured, sea borders faint; straits a dashed ferry line.
- Map lettering: Cinzel (OFL), engraved Roman capitals, letter-spaced.
  (The zoomed-out flat map is drawn by shader code and isn't changed.)
- Defines: map-mode colours let the terrain show through, province and state lines
  fade out when zoomed away, no bloom; post effects off. Country fills and border
  bands are the base game's (overriding them showed a grid of squares in game).
- The model frame around the map: dark green book cloth.

The sea artwork follows Valsora's coasts, so it is rebuilt with the main mod
(run_all.sh) and the two zips must come from the same build.

    python3 scripts/atlas_mod.py   # build/valsora_atlas, dist/valsora_atlas.zip, previews
"""
import math
import shutil
import struct
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage as ndi

from common import MAP_W as W, MAP_H as H, MOD_NAME, COUNTRIES
from imgio import write_bmp, read_bmp

NAME = "valsora_atlas"
TITLE = "Valsora: Atlas"
OUT = Path("build") / NAME
FONTS = Path("source/atlas/fonts")
SEED = 20261007
HW, HH = W // 2, H // 2          # the colour maps are half the map size

# ---------------------------------------------------------------- palette
# HOI4's terrain shader blends the colour map over the terrain tiles (atlas*.dds),
# roughly like an overlay: mid grey leaves the tile as it is. These values aim at a
# cream page under that blend; PAPER_TILE is the tiles' own grey.
PAPER = np.array([176, 163, 130], float)     # land colour map, the page
PAPER_TILE = 212                             # terrain tiles, fibre texture around this
INK = np.array([62, 46, 32], float)          # sepia ink: coasts, graticule on land
SEA = np.array([182, 200, 204], float)       # open sea
SEA_COAST = np.array([158, 184, 194], float)  # the wash along the coast
SEA_INK = np.array([52, 82, 104], float)     # waterlines, sea lettering
CARD = np.array([226, 228, 218], float)      # the compass's and cartouche's paper
GRATICULE_DEG = 15

rng = np.random.default_rng(SEED)


# ---------------------------------------------------------------- DDS writers
def _dds_header(w, h, mips, pf, cubemap=False, linear=None):
    flags = 0x1 | 0x2 | 0x4 | 0x1000 | (0x20000 if mips > 1 else 0)
    if pf == "argb":
        flags |= 0x8
        pitch = w * 4
        pfmt = struct.pack("<IIIIIIII", 32, 0x41, 0, 32, 0x00FF0000, 0x0000FF00, 0x000000FF,
                           0xFF000000)
    else:  # DXT3
        flags |= 0x80000
        pitch = linear
        pfmt = struct.pack("<II4sIIIII", 32, 0x4, b"DXT3", 0, 0, 0, 0, 0)
    caps = 0x1000 | ((0x8 | 0x400000) if mips > 1 else 0) | (0x8 if cubemap else 0)
    caps2 = 0xFE00 if cubemap else 0
    head = struct.pack("<4sIIIIIII", b"DDS ", 124, flags, h, w, pitch, 0, mips)
    return head + b"\0" * 44 + pfmt + struct.pack("<IIIII", caps, caps2, 0, 0, 0)


def mip_chain(rgba):
    """Box-filtered mip levels down to 1x1 (float in, uint8 out)."""
    lv = [np.asarray(rgba, np.float32)]
    while max(lv[-1].shape[:2]) > 1:
        a = lv[-1]
        h, w = a.shape[:2]
        h2, w2 = max(h // 2, 1), max(w // 2, 1)
        a = a[:h2 * (h // h2), :w2 * (w // w2)]
        lv.append(a.reshape(h2, h // h2, w2, w // w2, a.shape[2]).mean(axis=(1, 3)))
    return [np.clip(np.round(x), 0, 255).astype(np.uint8) for x in lv]


def write_dds(path, rgba, mips=True):
    """Uncompressed A8R8G8B8, rows top-down, with a full mip chain unless mips=False."""
    path.parent.mkdir(parents=True, exist_ok=True)
    rgba = np.asarray(rgba)
    if rgba.shape[2] == 3:
        rgba = np.dstack([rgba, np.full(rgba.shape[:2], 255, np.uint8)])
    levels = mip_chain(rgba) if mips else [np.clip(np.round(rgba), 0, 255).astype(np.uint8)]
    h, w = rgba.shape[:2]
    with open(path, "wb") as f:
        f.write(_dds_header(w, h, len(levels), "argb"))
        for lv in levels:
            f.write(np.ascontiguousarray(lv[:, :, [2, 1, 0, 3]]).tobytes())


def write_cubemap(path, faces):
    """Six HxWx4 faces (+x -x +y -y +z -z), one mip each, uncompressed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    h, w = faces[0].shape[:2]
    with open(path, "wb") as f:
        f.write(_dds_header(w, h, 1, "argb", cubemap=True))
        for face in faces:
            f.write(np.ascontiguousarray(face[:, :, [2, 1, 0, 3]].astype(np.uint8)).tobytes())


def write_dds_dxt3_alpha(path, alpha):
    """DXT3 with black colour and this 8-bit alpha (as 4 bits), one mip: the format of
    HOI4's map font texture. Exact, since every colour block is plain black."""
    path.parent.mkdir(parents=True, exist_ok=True)
    h, w = alpha.shape
    a4 = np.clip(np.round(alpha.astype(np.float32) / 17), 0, 15).astype(np.uint8)
    blocks = a4.reshape(h // 4, 4, w // 4, 4).transpose(0, 2, 1, 3).reshape(h // 4, w // 4, 16)
    packed = (blocks[..., 0::2] | (blocks[..., 1::2] << 4)).astype(np.uint8)   # 8 bytes
    out = np.zeros((h // 4, w // 4, 16), np.uint8)
    out[..., :8] = packed                                                    # colour = 0
    with open(path, "wb") as f:
        f.write(_dds_header(w, h, 1, "dxt3", linear=out.nbytes))
        f.write(out.tobytes())


# ---------------------------------------------------------------- noise
def fractal(shape, beta=2.0, lo=0.0, seed=None, periodic=True):
    """Gaussian 1/f^beta noise, unit std. Periodic, so it tiles seamlessly."""
    g = np.random.default_rng(seed) if seed is not None else rng
    h, w = shape
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.rfftfreq(w)[None, :]
    f = np.sqrt(fx * fx + fy * fy)
    f[0, 0] = 1
    amp = 1 / f ** (beta / 2)
    if lo:
        amp *= 1 - np.exp(-(f / lo) ** 2)
    amp[0, 0] = 0
    spec = (g.standard_normal((h, fx.shape[1])) + 1j * g.standard_normal((h, fx.shape[1]))) * amp
    n = np.fft.irfft2(spec, s=shape)
    return (n / (n.std() + 1e-9)).astype(np.float32)


def fibres(shape, seed, n=None, length=(6, 22)):
    """Short dark and light paper fibres, mostly horizontal (laid paper), tileable."""
    g = np.random.default_rng(seed)
    h, w = shape
    n = n or int(h * w / 90)
    img = Image.new("F", (w * 3, h * 3), 0.0)  # draw on a 3x3 tile, keep the middle
    d = ImageDraw.Draw(img)
    for _ in range(n):
        x, y = g.uniform(0, w), g.uniform(0, h)
        ang = g.normal(0, 0.45)
        ln = g.uniform(*length)
        v = g.choice([-1.0, 1.0], p=[0.55, 0.45]) * g.uniform(0.3, 1.0)
        dx, dy = math.cos(ang) * ln / 2, math.sin(ang) * ln / 2
        for ox in (0, w, 2 * w):
            for oy in (0, h, 2 * h):
                d.line([(x + ox - dx, y + oy - dy), (x + ox + dx, y + oy + dy)], fill=v, width=1)
    a = np.asarray(img, np.float32)
    a = a[h:2 * h, w:2 * w] + a[:h, :w] * 0
    return ndi.gaussian_filter(a, 0.6, mode="wrap")


# ---------------------------------------------------------------- geography
def load_world():
    w = np.load("work/world.npz")
    kind = w["kind"]                      # 0 sea, 1 land, 2 lake
    return kind


def coast_fields(kind):
    """Distance (map pixels) from the shore, on both sides, at full resolution. The
    signed distance is smoothed a little so the inked lines don't follow every pixel
    step of the coast."""
    water = kind != 1
    sd = (ndi.distance_transform_edt(~water) - ndi.distance_transform_edt(water)).astype(np.float32)
    sd = ndi.gaussian_filter(sd, 1.1, mode="wrap")     # > 0 on land, < 0 at sea
    d_water = np.clip(-sd + 0.5, 0, None)
    d_land = np.clip(sd + 0.5, 0, None)
    return water, d_water, d_land


def to_half(a):
    return a.reshape(HH, 2, HW, 2).mean(axis=(1, 3))


def graticule(shape, scale, deg=GRATICULE_DEG):
    """Anti-aliased meridians and parallels every `deg` degrees. Returns (lines, equator)
    in [0, 1]; scale = pixels of this image per map pixel."""
    h, w = shape
    step_x = w / (360 / deg)
    step_y = h / (180 / deg)
    x = np.arange(w)[None, :] + 0.5
    y = np.arange(h)[:, None] + 0.5
    dx = np.abs(((x + step_x / 2) % step_x) - step_x / 2)
    dy = np.abs(((y - h / 2 + step_y / 2) % step_y) - step_y / 2)
    width = 0.55 * max(scale, 0.5) * 2
    lines = np.maximum(np.clip(1 - dx / width, 0, 1) + 0 * y, np.clip(1 - dy / width, 0, 1) + 0 * x)
    eq = np.clip(1 - np.abs(y - h / 2) / (width * 1.8), 0, 1) + 0 * x
    return lines.astype(np.float32), eq.astype(np.float32)


def blend(base, colour, alpha):
    """Lay ink of `colour` with coverage `alpha` (HxW in [0, 1]) over base (HxWx3)."""
    a = np.clip(alpha, 0, 1)[..., None]
    return base * (1 - a) + np.asarray(colour, float) * a


def foxing(shape, seed, count):
    """Sparse brown age spots: soft, uneven blots of different sizes."""
    g = np.random.default_rng(seed)
    h, w = shape
    acc = np.zeros(shape, np.float32)
    for _ in range(count):
        y, x = g.integers(0, h), g.integers(0, w)
        r = g.uniform(1.0, 6.0)
        acc[y, x] += g.uniform(0.4, 1.0) * r * r
    acc = ndi.gaussian_filter(acc, 2.5)
    return acc / (acc.max() + 1e-9)


# ---------------------------------------------------------------- land colour map
def land_colormap(kind, d_land):
    """The page: cream paper, uneven tone, foxing, graticule and an inked coastline."""
    shape = (HH, HW)
    col = np.broadcast_to(PAPER, shape + (3,)).astype(np.float32).copy()
    tone = fractal(shape, beta=3.2, seed=SEED + 1) * 3.5           # uneven page
    mottle = fractal(shape, beta=1.6, seed=SEED + 2) * 1.6         # finer cloudiness
    warm = fractal(shape, beta=3.6, seed=SEED + 3)                 # some areas yellower
    col += (tone + mottle)[..., None]
    col += np.clip(warm, 0, None)[..., None] * np.array([2.0, 0.5, -3.0])
    col = blend(col, (150, 112, 70), foxing(shape, SEED + 4, 2600) * 0.22)
    lines, eq = graticule(shape, 0.5)
    col = blend(col, INK, lines * 0.16 + eq * 0.10)
    # coastline: a fine ink line just inside the land, and a soft shadow behind it
    land = kind == 1
    line = np.clip(1.15 - np.abs(d_land - 1.0) / 0.95, 0, 1) * land
    shade = np.exp(-d_land / 7.0) * land
    col = blend(col, INK, to_half(shade) * 0.10)
    col = blend(col, INK, to_half(line) * 0.78)
    water = to_half((kind != 1).astype(np.float32)) > 0.5
    col[water] = SEA_COAST
    return np.clip(col, 0, 255)


# ---------------------------------------------------------------- sea colour map
WATERLINES = [  # (distance from the shore in map pixels, strength)
    (3.2, 0.66), (7.4, 0.54), (12.6, 0.43), (18.8, 0.33), (26.2, 0.25), (35.0, 0.17), (45.4, 0.11)]


def sea_colormap(kind, d_water, overlay_ink, overlay_paper):
    """Pale sea with a coastal wash, engraved waterlines, graticule and the lettering."""
    shape = (HH, HW)
    water = kind != 1
    # waterlines: contours of the distance to the shore, wobbling a little like a burin
    wob = fractal((H, W), beta=2.6, seed=SEED + 5) * 0.55
    dd = d_water + wob
    wl = np.zeros((H, W), np.float32)
    for dist, strength in WATERLINES:
        wl = np.maximum(wl, np.clip(1 - np.abs(dd - dist) / 0.85, 0, 1) * strength)
    wl *= water
    wash = np.exp(-d_water / 42.0)
    col = blend(np.broadcast_to(SEA, shape + (3,)).astype(np.float32).copy(),
                SEA_COAST, to_half(wash) * 0.85)
    col += (fractal(shape, beta=3.0, seed=SEED + 6) * 2.2
            + fractal(shape, beta=1.5, seed=SEED + 7) * 1.0)[..., None]
    lines, eq = graticule(shape, 0.5)
    col = blend(col, SEA_INK, lines * 0.20 + eq * 0.12)
    col = blend(col, SEA_INK, to_half(wl))
    col = blend(col, CARD, overlay_paper)
    col = blend(col, SEA_INK, overlay_ink)
    return np.clip(col, 0, 255)


# ---------------------------------------------------------------- lettering
def font(path, size, weight=None):
    f = ImageFont.truetype(str(FONTS / path), size)
    if weight is not None:
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
    return f


def glyph_patch(fnt, ch, scale=1):
    """A character's coverage, its advance and the offset of its origin."""
    l, t, r, b = fnt.getbbox(ch)
    pad = 4
    im = Image.new("L", (r - l + 2 * pad, b - t + 2 * pad), 0)
    ImageDraw.Draw(im).text((pad - l, pad - t), ch, font=fnt, fill=255)
    return np.asarray(im, np.float32) / 255, fnt.getlength(ch), (pad - l, pad - t)


def text_on_arc(fnt, text, tracking, angle, bend):
    """Render text along a gentle circular arc. Returns (coverage image, centre of the
    text inside it). angle: radians, the baseline's direction at the middle; bend:
    curvature in 1/px (positive arches the text upwards)."""
    chars = list(text)
    adv = [fnt.getlength(c) + tracking for c in chars]
    total = sum(adv) - tracking
    asc, desc = fnt.getmetrics()
    size = int(total + 4 * asc + 40)
    canvas = Image.new("L", (size, size), 0)
    cx = cy = size / 2
    s = -total / 2
    for c, a in zip(chars, adv):
        mid = s + (a - tracking) / 2
        s += a
        if c == " ":
            continue
        # position along the arc (arc length `mid` from the centre)
        if abs(bend) > 1e-6:
            phi = mid * bend
            px, py = math.sin(phi) / bend, (1 - math.cos(phi)) / bend
            rot = phi
        else:
            px, py, rot = mid, 0.0, 0.0
        # rotate the arc into place
        th = angle
        # an arch: the ends fall away below the baseline at the middle
        gx = cx + px * math.cos(th) - py * math.sin(th)
        gy = cy + px * math.sin(th) + py * math.cos(th)
        l, t, r, b = fnt.getbbox(c)
        g = Image.new("L", (int(r - l) + 8, int(asc + desc) + 8), 0)
        ImageDraw.Draw(g).text((4 - l, 4), c, font=fnt, fill=255)
        # the glyph's anchor: middle of its advance on the baseline
        ax, ay = 4 - l + fnt.getlength(c) / 2, 4 + asc
        deg = -math.degrees(th + rot)
        big = Image.new("L", (g.width * 3, g.height * 3), 0)
        big.paste(g, (g.width, g.height))
        rot_im = big.rotate(deg, resample=Image.BICUBIC, center=(g.width + ax, g.height + ay))
        ox, oy = int(round(gx - (g.width + ax))), int(round(gy - (g.height + ay)))
        canvas.paste(Image.fromarray(np.maximum(
            np.asarray(canvas.crop((ox, oy, ox + rot_im.width, oy + rot_im.height))),
            np.asarray(rot_im))), (ox, oy))
    a = np.asarray(canvas, np.float32) / 255
    ys, xs = np.nonzero(a > 0.01)
    m = 6
    y0, y1 = max(ys.min() - m, 0), ys.max() + m + 1
    x0, x1 = max(xs.min() - m, 0), xs.max() + m + 1
    return a[y0:y1, x0:x1], (cx - x0, cy - y0)


def stamp(dst, patch, centre, mode="max"):
    """Place patch (h x w) on dst so that patch's middle lands on centre (x, y)."""
    ph, pw = patch.shape[:2]
    x0 = int(round(centre[0] - pw / 2))
    y0 = int(round(centre[1] - ph / 2))
    H0, W0 = dst.shape[:2]
    sx0, sy0 = max(0, -x0), max(0, -y0)
    ex, ey = min(pw, W0 - x0), min(ph, H0 - y0)
    if ex <= sx0 or ey <= sy0:
        return
    region = dst[y0 + sy0:y0 + ey, x0 + sx0:x0 + ex]
    src = patch[sy0:ey, sx0:ex]
    if mode == "max":
        np.maximum(region, src, out=region)
    else:
        region[...] = src


def depth(clear, step=4):
    """How far (map pixels) each point of a coarse grid lies inside `clear`, counting the
    map's edges as obstacles."""
    c = np.pad(clear[::step, ::step], 1)
    return ndi.distance_transform_edt(c)[1:-1, 1:-1] * step


def footprint(cov, pad):
    m = cov > 0.05
    return ndi.binary_dilation(m, iterations=pad) if pad else m


def sea_regions(kind):
    """{name: full-res mask} for the named sea regions."""
    import json
    names = json.load(open("source/region_names.json"))
    regs = json.load(open("work/regions.json"))["regions"]
    region_of = np.load("work/regions.npz")["region_of"]
    prov = np.load("work/provinces.npz")["prov"]
    out = {}
    for i, r in enumerate(regs):
        nm = names.get(r["colour"])
        if nm is None or r["kind"] != "sea":
            continue
        ids = np.nonzero(region_of == i)[0]
        out[nm] = np.isin(prov, ids) & (kind != 1)
    return out


def place_sea_labels(kind, d_water, ink, taken):
    """Each ocean's name, in spaced italic capitals on a gentle arc, where it fits."""
    regions = sea_regions(kind)
    S = 2  # lettering is placed in map pixels on the full-res canvas
    placed = []
    for name, mask in sorted(regions.items(), key=lambda kv: -kv[1].sum()):
        area = mask.sum()
        ys, xs = np.nonzero(mask[::4, ::4])
        if len(xs) < 20:
            continue
        pts = np.stack([xs * 4.0, ys * 4.0], 1)
        cov = np.cov((pts - pts.mean(0)).T)
        ev, evec = np.linalg.eigh(cov)
        major = evec[:, 1]
        angle = math.atan2(major[1], major[0])
        if angle > math.pi / 2:
            angle -= math.pi
        if angle < -math.pi / 2:
            angle += math.pi
        angle = max(-0.45, min(0.45, angle))
        extent = 4 * math.sqrt(ev[1])
        lines = [name.upper()]
        if " " in name:
            a, b = name.upper().split(" ", 1)
            lines_alt = [a, b]
        else:
            lines_alt = None
        size0 = int(max(34, min(92, extent * 0.10)))
        done = False
        attempts = [(margin, size) for margin in (26, 12, 5, 2)
                    for size in range(size0 if margin == 26 else min(size0, 44),
                                      19 if margin > 5 else 13, -4 if margin > 5 else -2)]
        last_margin = None
        for margin, size in attempts:
            if margin != last_margin:
                clear = mask & (d_water > margin) & ~taken
                # coarse grid for speed: how deep each point lies inside the clear area
                inside = depth(clear)
                last_margin = margin
            fnt = font("EBGaramond-Italic[wght].ttf", size, 520)
            for variant in ([lines] + ([lines_alt] if lines_alt else [])):
                tracking = size * (0.42 if size >= 24 else 0.25)
                covs = []
                for ln in variant:
                    w_est = sum(fnt.getlength(c) + tracking for c in ln)
                    bend = 1.0 / max(w_est * 2.4, 1)
                    covs.append(text_on_arc(fnt, ln, tracking, angle, bend)[0])
                # stack the lines (second one under the first, along the label's normal)
                lead = size * 1.25
                hgt = max(c.shape[0] for c in covs) + int(lead * (len(covs) - 1)) + 10
                wid = max(c.shape[1] for c in covs) + int(lead * (len(covs) - 1)) + 10
                cov = np.zeros((hgt, wid), np.float32)
                for k, c in enumerate(covs):
                    off = (k - (len(covs) - 1) / 2) * lead
                    cx = wid / 2 - math.sin(angle) * off
                    cy = hgt / 2 + math.cos(angle) * off
                    stamp(cov, c, (cx, cy))
                ys_, xs_ = np.nonzero(cov > 0.01)
                cov = cov[max(ys_.min() - 8, 0):ys_.max() + 9, max(xs_.min() - 8, 0):xs_.max() + 9]
                need = footprint(cov, 6)
                ys2, xs2 = np.nonzero(need)
                rad = math.hypot(xs2.max() - xs2.min(), ys2.max() - ys2.min()) / 2
                # candidates: clear points deep enough, nearest the region's centre of mass
                cand = np.argwhere(inside > rad * 0.35)
                if not len(cand):
                    continue
                com = pts.mean(0) / 4
                order = np.argsort(np.hypot(cand[:, 1] - com[0], cand[:, 0] - com[1]))
                for yx in cand[order][:1500]:
                    cx, cy = yx[1] * 4 + 2, yx[0] * 4 + 2
                    x0 = int(cx - cov.shape[1] / 2)
                    y0 = int(cy - cov.shape[0] / 2)
                    if x0 < 8 or y0 < 8 or x0 + cov.shape[1] > W - 8 or y0 + cov.shape[0] > H - 8:
                        continue
                    win = clear[y0:y0 + cov.shape[0], x0:x0 + cov.shape[1]]
                    if (need & ~win).any():
                        continue
                    stamp(ink, cov, (cx, cy))
                    taken[y0:y0 + cov.shape[0], x0:x0 + cov.shape[1]] |= ndi.binary_dilation(
                        need, iterations=20)
                    placed.append((name, size, cx, cy, len(variant)))
                    done = True
                    break
                if done:
                    break
            if done:
                break
        if not done:
            print(f"  sea label {name!r}: no room, left out")
    for p in placed:
        print(f"  sea label {p[0]!r}: size {p[1]}, at ({p[2]}, {p[3]}), {p[4]} line(s)")
    return placed


# ---------------------------------------------------------------- ornaments
def compass_rose(R):
    """A 32-point compass rose of radius R map pixels: (ink, paper) coverage, 2R+ square.
    Each point is split along its spine, one half inked and one left as paper, the
    way engravers drew them; a ring of degree ticks and the cardinal letters."""
    ss = 4
    size = int(2 * R * 1.25)
    S = size * ss
    c = S / 2
    r = R * ss
    ink = Image.new("L", (S, S), 0)
    pap = Image.new("L", (S, S), 0)
    di, dp = ImageDraw.Draw(ink), ImageDraw.Draw(pap)
    lw = max(2, int(r * 0.016))
    # rings and degree ticks
    for rad, w in ((0.99, lw * 1.6), (0.93, lw), (0.86, lw * 0.8)):
        di.ellipse([c - rad * r, c - rad * r, c + rad * r, c + rad * r], outline=255, width=int(w))
    for deg in range(0, 360, 2):
        a = math.radians(deg)
        inner = 0.93 if deg % 10 == 0 else (0.955 if deg % 10 == 5 else 0.97)
        di.line([(c + math.sin(a) * inner * r, c - math.cos(a) * inner * r),
                 (c + math.sin(a) * 0.99 * r, c - math.cos(a) * 0.99 * r)],
                fill=255, width=lw if deg % 10 == 0 else max(1, lw // 2))
    # the points, smallest first so the cardinal ones lie on top
    spec = []
    for i in range(32):
        if i % 8 == 0:
            spec.append((3, i, 0.84, 0.115))
        elif i % 4 == 0:
            spec.append((2, i, 0.62, 0.095))
        elif i % 2 == 0:
            spec.append((1, i, 0.47, 0.06))
        else:
            spec.append((0, i, 0.36, 0.042))
    for rank, i, ln, hw in sorted(spec):
        a = math.radians(i * 11.25)
        u = (math.sin(a), -math.cos(a))
        v = (math.cos(a), math.sin(a))
        tip = (c + u[0] * ln * r, c + u[1] * ln * r)
        base = 0.0
        left = (c + v[0] * hw * r + u[0] * base, c + v[1] * hw * r + u[1] * base)
        right = (c - v[0] * hw * r + u[0] * base, c - v[1] * hw * r + u[1] * base)
        centre = (c, c)
        # paper under the whole point (so the rings don't show through), ink on one half
        dp.polygon([centre, left, tip, right], fill=255)
        di.polygon([centre, tip, right], fill=255)
        di.line([left, tip, right, centre, left], fill=255, width=lw, joint="curve")
        di.line([centre, tip], fill=255, width=max(1, lw // 2))
        # erase the ink of the paper half (lower-ranked points were drawn underneath)
        di.polygon([centre, left, tip], fill=0)
        di.line([left, tip, centre], fill=255, width=lw, joint="curve")
    # centre boss
    for rad, fill in ((0.075, None), (0.03, 255)):
        dp.ellipse([c - rad * r, c - rad * r, c + rad * r, c + rad * r], fill=255)
        di.ellipse([c - rad * r, c - rad * r, c + rad * r, c + rad * r], outline=255,
                   width=lw, fill=fill)
    # cardinal letters outside the ring
    for letter, deg, sz in (("N", 0, 0.24), ("E", 90, 0.15), ("S", 180, 0.15), ("W", 270, 0.15)):
        f = font("Cinzel[wght].ttf", int(sz * r), 700)
        a = math.radians(deg)
        rad = 1.12 if letter == "N" else 1.09
        x, y = c + math.sin(a) * rad * r, c - math.cos(a) * rad * r
        di.text((x, y), letter, font=f, fill=255, anchor="mm")
    # a small fleur-like diamond above the north point
    tipy = c - 0.84 * r
    di.polygon([(c, tipy - 0.05 * r), (c + 0.025 * r, tipy - 0.01 * r), (c, tipy + 0.02 * r),
                (c - 0.025 * r, tipy - 0.01 * r)], fill=255)
    out = []
    for im in (ink, pap):
        out.append(np.asarray(im.resize((size, size), Image.LANCZOS), np.float32) / 255)
    return out


def cartouche(width):
    """The title piece: a paper panel with a double rule and corner rosettes,
    'VALSORA' in engraved capitals and a line beneath. Returns (ink, paper)."""
    ss = 3
    w, h = width, int(width * 0.40)
    S = (w * ss, h * ss)
    ink = Image.new("L", S, 0)
    pap = Image.new("L", S, 0)
    di, dp = ImageDraw.Draw(ink), ImageDraw.Draw(pap)
    W_, H_ = S
    m = int(0.03 * W_)
    lw = max(2, int(W_ * 0.004))
    dp.rectangle([m, m, W_ - m, H_ - m], fill=255)
    di.rectangle([m, m, W_ - m, H_ - m], outline=255, width=lw * 2)
    g = m + int(lw * 4.5)
    di.rectangle([g, g, W_ - g, H_ - g], outline=255, width=max(1, lw // 2 + 1))
    for cx, cy in ((m, m), (W_ - m, m), (m, H_ - m), (W_ - m, H_ - m)):
        rr = int(m * 0.9)
        dp.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=255)
        di.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=255, width=lw)
        rr2 = int(rr * 0.45)
        di.ellipse([cx - rr2, cy - rr2, cx + rr2, cy + rr2], fill=255)
    title = font("Cinzel[wght].ttf", int(H_ * 0.34), 700)
    text = "VALSORA"
    track = H_ * 0.05
    tw = sum(title.getlength(ch) + track for ch in text) - track
    x = W_ / 2 - tw / 2
    for ch in text:
        di.text((x, H_ * 0.44), ch, font=title, fill=255, anchor="ls")
        x += title.getlength(ch) + track
    # rule with a lozenge
    y = H_ * 0.56
    di.line([(W_ * 0.2, y), (W_ * 0.46, y)], fill=255, width=lw)
    di.line([(W_ * 0.54, y), (W_ * 0.8, y)], fill=255, width=lw)
    d = H_ * 0.03
    di.polygon([(W_ / 2, y - d), (W_ / 2 + d * 1.6, y), (W_ / 2, y + d), (W_ / 2 - d * 1.6, y)],
               fill=255)
    sub = font("EBGaramond-Italic[wght].ttf", int(H_ * 0.115), 500)
    di.text((W_ / 2, H_ * 0.73), "A New and Accurate Map of the World", font=sub, fill=255,
            anchor="mm")
    small = font("Cinzel[wght].ttf", int(H_ * 0.065), 500)
    line = "DRAWN FROM THE LATEST SURVEYS"
    tr = H_ * 0.02
    tw = sum(small.getlength(ch) + tr for ch in line) - tr
    x = W_ / 2 - tw / 2
    for ch in line:
        di.text((x, H_ * 0.87), ch, font=small, fill=255, anchor="ls")
        x += small.getlength(ch) + tr
    return [np.asarray(im.resize((w, h), Image.LANCZOS), np.float32) / 255 for im in (ink, pap)]


def place_ornament(ink_cov, pap_cov, d_water, taken, ink, paper, rows=(0.0, 1.0), near=None,
                   min_sep=0):
    """Put an ornament where the open sea is widest, within the band of rows given as
    fractions of the map's height (and at least min_sep from `near`)."""
    h, w = ink_cov.shape
    need = footprint(np.maximum(ink_cov, pap_cov), 10)
    clear = (d_water > 40) & ~taken
    inside = depth(clear)
    yy = (np.arange(inside.shape[0]) * 4 + 2)[:, None] / H
    inside = np.where((yy >= rows[0]) & (yy <= rows[1]), inside, 0)
    rad = math.hypot(w, h) / 2
    cand = np.argwhere(inside > rad * 0.6)
    if near is not None and len(cand):
        dist = np.hypot(cand[:, 1] * 4 - near[0], cand[:, 0] * 4 - near[1])
        cand = cand[dist > min_sep]
    order = np.argsort(-inside[cand[:, 0], cand[:, 1]]) if len(cand) else []
    for yx in cand[order][:3000] if len(cand) else []:
        cx, cy = yx[1] * 4 + 2, yx[0] * 4 + 2
        x0, y0 = int(cx - w / 2), int(cy - h / 2)
        if x0 < 8 or y0 < 8 or x0 + w > W - 8 or y0 + h > H - 8:
            continue
        if (need & ~clear[y0:y0 + h, x0:x0 + w]).any():
            continue
        stamp(ink, ink_cov, (cx, cy))
        stamp(paper, pap_cov, (cx, cy))
        taken[y0:y0 + h, x0:x0 + w] |= ndi.binary_dilation(need, iterations=30)
        return (cx, cy)
    return None


# ---------------------------------------------------------------- terrain tiles
def paper_tile(seed, size=256):
    """One seamless tile of paper: grain, cloudiness, fibres and faint laid lines."""
    # quiet and strictly seamless: the game repeats this tile every few map pixels, so
    # anything with a direction or a period of its own turns into a visible grid
    # (the first in-game test, 2026-10-07)
    grain = fractal((size, size), beta=0.6, seed=seed) * 1.4
    fib = fibres((size, size), seed + 2, n=size * size // 110) * 3.0
    v = PAPER_TILE + grain + fib
    rgb = np.dstack([v + 1.0, v + 0.5, v - 1.5])
    return np.clip(rgb, 0, 255)


def tile_atlas():
    """4x4 tiles of 256 px, every terrain type the same paper (different seeds, so the
    repetition doesn't show)."""
    a = np.tile(paper_tile(SEED + 100), (4, 4, 1))  # one tile everywhere: no patchwork
    return np.dstack([a, np.full(a.shape[:2], 80.0)])


def flat_normal(size, alpha):
    a = np.zeros((size, size, 4), np.float32)
    a[...] = (128, 128, 255, alpha)
    return a


# ---------------------------------------------------------------- borders
def soft_band(v, centre, half, edge):
    """1 inside |v - centre| < half, falling off over `edge` pixels."""
    return np.clip((half + edge / 2 - np.abs(v - centre)) / edge, 0, 1)


def border_texture(w, h, style):
    """A border strip: u runs along the border (tiled), v across it (centre = middle)."""
    ss = 4
    W_, H_ = w * ss, h * ss
    u = np.arange(W_)[None, :] + 0.5
    v = np.arange(H_)[:, None] + 0.5
    c = H_ / 2
    ink = np.array([34, 27, 21], float)
    if style == "country":
        # dash-dot: a long dash, a round dot, as on printed maps' international boundaries
        period = W_ / 2
        half = H_ * 0.06
        dash_len, gap = 0.56, 0.11
        pos = (u % period)
        dash = np.clip(np.minimum(pos - 0, period * dash_len - pos) + 0.5 * ss, 0, ss) / ss
        line = soft_band(v, c, half, ss * 1.2) * dash
        dot_c = period * (dash_len + gap) + half
        dist = np.hypot(((u % period) - dot_c), v - c)
        dotcov = np.clip((half * 1.4 - dist) / (ss * 1.2) + 0.5, 0, 1)
        a = np.maximum(line, dotcov)
        a = np.maximum(a, soft_band(v, c, half * 0.32, ss) * 0.55)  # hairline joining them
        col = ink
    elif style == "country_far":
        a = soft_band(v, c, H_ * 0.07, ss * 1.2)
        col = ink
    elif style == "state":
        period = W_ / 2
        pos = u % period
        dash = np.clip(np.minimum(pos, period * 0.62 - pos) / ss + 0.5, 0, 1)
        a = soft_band(v, c, H_ * 0.05, ss) * dash * 0.85
        col = np.array([58, 46, 36], float)
    elif style == "province":
        period = W_ / 4
        dist = np.hypot((u % period) - period / 2, v - c)
        a = np.clip((H_ * 0.06 - dist) / ss + 0.5, 0, 1) * 0.45
        col = np.array([80, 66, 52], float)
    elif style == "impassable":
        # a line with short hachures on one side, like a cliff or mountain wall
        a = soft_band(v, c, H_ * 0.04, ss)
        period = W_ / 8
        tick = (np.abs((u % period) - period / 2 + (v - c) * 0.3) < ss * 1.0) & (v > c) & (v < c + H_ * 0.22)
        a = np.maximum(a, tick.astype(np.float32))
        col = np.array([70, 48, 36], float)
    elif style == "sea":
        a = np.zeros((H_, W_), np.float32)
        col = SEA_INK
    elif style == "sea_region":
        period = W_ / 2
        pos = u % period
        dash = np.clip(np.minimum(pos, period * 0.35 - pos) / ss + 0.5, 0, 1)
        a = soft_band(v, c, H_ * 0.035, ss) * dash * 0.35
        col = SEA_INK
    else:
        raise ValueError(style)
    a = np.broadcast_to(a, (H_, W_)).astype(np.float32)
    a = a.reshape(h, ss, w, ss).mean(axis=(1, 3))
    rgb = np.broadcast_to(col, (h, w, 3))
    return np.dstack([rgb, a * 255])


def strait_texture():
    """A dashed ferry line along v (the strait's direction), in the middle of u."""
    ss = 4
    n = 64 * ss
    u = np.arange(n)[None, :] + 0.5
    v = np.arange(n)[:, None] + 0.5
    period = n / 4
    pos = v % period
    dash = np.clip(np.minimum(pos, period * 0.6 - pos) / ss + 0.5, 0, 1)
    a = soft_band(u, n / 2, n * 0.03, ss) * dash
    a = a.reshape(64, ss, 64, ss).mean(axis=(1, 3))
    return np.dstack([np.broadcast_to(np.array([34, 30, 26], float), (64, 64, 3)), a * 230])


# ---------------------------------------------------------------- the map's frame
def book_cloth(size=1024):
    """Dark green book cloth: a fine linen weave with some unevenness."""
    x = np.arange(size)[None, :]
    y = np.arange(size)[:, None]
    weave = (np.sin(2 * np.pi * x / 6) * np.sign(np.sin(2 * np.pi * y / 12)) * 0.5
             + np.sin(2 * np.pi * y / 6) * np.sign(np.sin(2 * np.pi * x / 12)) * 0.5)
    tone = fractal((size, size), beta=2.4, seed=SEED + 50) * 4
    grain = fractal((size, size), beta=0.8, seed=SEED + 51) * 3
    v = weave * 5 + tone + grain
    base = np.array([34, 58, 44], float)
    rgb = base + v[..., None] * np.array([0.8, 1.0, 0.85])
    return np.dstack([np.clip(rgb, 0, 255), np.full((size, size), 255.0)])


# ---------------------------------------------------------------- the map font
FONT_CHARS = ([c for c in range(32, 127)] + [c for c in range(160, 384)]
              + [0x2013, 0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x2022, 0x2026])
FONT_SIZE = 256
FONT_TRACKING = 0.10   # extra space between letters, in ems: engraved map lettering


def map_font(out_dir):
    """gfx/fonts/hoi_mapfont4.fnt + .dds (BMFont text format, DXT3, black with the
    glyphs in alpha), the font HOI4 letters country names on the map with. Cinzel, with
    its kerning, letter-spaced."""
    from PIL import features
    eng = ImageFont.Layout.RAQM if features.check("raqm") else ImageFont.Layout.BASIC
    fnt = ImageFont.truetype(str(FONTS / "Cinzel[wght].ttf"), FONT_SIZE, layout_engine=eng)
    fnt.set_variation_by_axes([600])
    notdef = np.asarray(fnt.getmask(""))
    asc, desc = fnt.getmetrics()
    track = round(FONT_SIZE * FONT_TRACKING)
    glyphs = []
    for code in FONT_CHARS:
        ch = chr(code)
        m = fnt.getmask(ch)
        if code != 32 and code != 160 and np.asarray(m).shape == notdef.shape and (np.asarray(m) == notdef).all():
            continue
        l, t, r, b = fnt.getbbox(ch, anchor="ls")
        adv = fnt.getlength(ch)
        if r <= l or b <= t:
            glyphs.append((code, None, 0, 0, 0, 0, adv))
            continue
        im = Image.new("L", (r - l + 4, b - t + 4), 0)
        ImageDraw.Draw(im).text((2 - l, 2 - t), ch, font=fnt, fill=255, anchor="ls")
        glyphs.append((code, np.asarray(im), l - 2, t - 2, r - l + 4, b - t + 4, adv))
    # shelf-pack into a 4096-wide page
    TW = 4096
    order = sorted([g for g in glyphs if g[1] is not None], key=lambda g: -g[5])
    x = y = shelf = 0
    pos = {}
    for g in order:
        gw, gh = g[4], g[5]
        if x + gw + 2 > TW:
            x, y, shelf = 0, y + shelf + 2, 0
        pos[g[0]] = (x, y)
        x += gw + 2
        shelf = max(shelf, gh)
    TH = 1
    while TH < y + shelf + 2:
        TH *= 2
    page = np.zeros((TH, TW), np.uint8)
    for g in order:
        px, py = pos[g[0]]
        page[py:py + g[5], px:px + g[4]] = g[1]
    write_dds_dxt3_alpha(out_dir / "hoi_mapfont4.dds", page)
    base = asc
    lines = [f'info face="Cinzel" size={FONT_SIZE} bold=0 italic=0 charset="" unicode=1 '
             f'stretchH=100 smooth=1 aa=1 padding=0,0,0,0 spacing=2,2 outline=0',
             f"common lineHeight={asc + desc} base={base} scaleW={TW} scaleH={TH} pages=1 "
             f"packed=0 alphaChnl=0 redChnl=3 greenChnl=3 blueChnl=3",
             'page id=0 file="hoi_mapfont4.dds"',
             f"chars count={len(glyphs)}"]
    for code, img, ox, oy, gw, gh, adv in glyphs:
        if img is None:
            px = py = 0
            gw = gh = 0
            ox, oy = 0, 0
        else:
            px, py = pos[code]
        lines.append(f"char id={code:<5d} x={px:<5d} y={py:<5d} width={gw:<5d} height={gh:<5d} "
                     f"xoffset={ox:<5d} yoffset={oy + base:<5d} xadvance={round(adv) + track:<5d} "
                     f"page=0  chnl=15")
    # no kerning block: the base game's map font has none, and the first in-game test
    # showed no country names at all, so the font is kept to what the game is known to
    # read (only its letter spacing is widened)
    (out_dir / "hoi_mapfont4.fnt").write_bytes(("\r\n".join(lines) + "\r\n").encode("ascii"))
    return len(glyphs), (TW, TH)


# ---------------------------------------------------------------- defines
DEFINES = """-- Valsora: Atlas. Graphics defines for a printed-atlas look.
-- Map modes draw an opaque colour over the land and the sea; at 1 it is transparent,
-- so the paper, the waterlines and the sea lettering show (the first in-game test,
-- 2026-10-07, without these: flat grey sea, country colours over grey).
NDefines_Graphics.NMapMode.MAP_MODE_TERRAIN_TRANSPARENCY = 1
NDefines_Graphics.NMapMode.MAP_MODE_NAVAL_TERRAIN_TRANSPARENCY = 1
-- Province lines only up close, state lines a little further out, as an atlas shows
-- smaller divisions only on its larger-scale plates.
NDefines_Graphics.NGraphics.PROVINCE_BORDER_FADE_NEAR = 260
NDefines_Graphics.NGraphics.PROVINCE_BORDER_FADE_FAR = 320
NDefines_Graphics.NGraphics.STATE_BORDER_FADE_NEAR = 620
NDefines_Graphics.NGraphics.STATE_BORDER_FADE_FAR = 720
-- Paper doesn't glow.
NDefines_Graphics.NGraphics.BLOOM_SCALE = 0.0
"""


def descriptor(extra=()):
    return "\n".join(['version="1.0"', "tags={", '\t"Graphics"', '\t"Map"', "}",
                      f'name="{TITLE}"', 'supported_version="1.19.*"', 'picture="thumbnail.png"',
                      "dependencies={", f'\t"{MOD_NAME}"', "}", *extra]) + "\n"


# ---------------------------------------------------------------- build
def main():
    import time
    t0 = time.time()
    if OUT.exists():
        shutil.rmtree(OUT)
    tdir = OUT / "map" / "terrain"
    tdir.mkdir(parents=True)
    kind = load_world()
    water, d_water, d_land = coast_fields(kind)

    # sea artwork: ornaments first (they need the widest water), then each ocean's name
    ink = np.zeros((H, W), np.float32)
    pap = np.zeros((H, W), np.float32)
    taken = np.zeros((H, W), bool)
    ci, cp = compass_rose(230)
    rose = place_ornament(ci, cp, d_water, taken, ink, pap, rows=(0.0, 0.5))
    ti, tp = cartouche(820)
    title = place_ornament(ti, tp, d_water, taken, ink, pap, rows=(0.6, 1.0), near=rose,
                           min_sep=900)
    print(f"  compass rose at {rose}, cartouche at {title}")
    place_sea_labels(kind, d_water, ink, taken)

    land = land_colormap(kind, d_land)
    write_dds(tdir / "colormap_rgb_cityemissivemask_a.dds",
              np.dstack([land, np.zeros(land.shape[:2])]))   # no city lights at night
    sea = sea_colormap(kind, d_water, to_half(ink), to_half(pap))
    w0 = np.dstack([sea, np.full(sea.shape[:2], 255.0)])
    write_dds(tdir / "colormap_water_0.dds", w0)
    w1 = mip_chain(w0)[1].astype(np.float32)
    write_dds(tdir / "colormap_water_1.dds", w1)
    write_dds(tdir / "colormap_water_2.dds", mip_chain(w1)[1])
    # fog of war tint as the main mod has it; no water gloss
    wh = to_half(water.astype(np.float32)) > 0.5
    grey = np.where(wh, 96.0, 146.0)
    write_dds(tdir / "fow_rgb_waterspec_a.dds", np.dstack([grey, grey, grey, np.zeros(wh.shape)]))
    print(f"  colour maps written ({time.time() - t0:.0f} s)")

    # terrain tiles, their normals, mud, the sea floor, the sky's reflection
    atl = tile_atlas()
    for i in range(3):
        write_dds(tdir / f"atlas{i}.dds", atl)
        write_dds(tdir / f"atlas_normal{i}.dds", flat_normal(256, 40))
    mud = np.dstack([paper_tile(SEED + 300), np.full((256, 256), 30.0)])
    for i in range(2):
        write_dds(tdir / f"mud_diffuse_rgb_gloss_a_{i}.dds", mud)
        write_dds(tdir / f"mud_normal_rgb_spec_a_{i}.dds", flat_normal(256, 20))
    floor = np.zeros((256, 256, 4), np.float32)
    floor[...] = (*SEA_COAST, 255)
    for i in range(3):
        write_dds(tdir / f"underwater_terrain_{i}.dds", floor)
    face = np.zeros((128, 128, 4), np.uint8)
    face[...] = (*SEA.astype(int), 255)
    write_cubemap(tdir / "reflection.dds", [face] * 6)

    # borders (same sizes as the base game's), straits
    for name, sizes, style in [
            ("country", [(256, 128), (128, 64), (64, 32)], ["country", "country", "country_far"]),
            ("state", [(128, 64), (256, 128), (256, 128)], ["state"] * 3),
            ("province", [(64, 32)] * 3, ["province"] * 3),
            ("impassable", [(128, 64), (64, 32), (32, 16)], ["impassable"] * 3),
            ("sea", [(64, 32), (53, 32), (53, 32)], ["sea"] * 3),
            ("sea_region", [(64, 32), (53, 32), (53, 32)], ["sea_region"] * 3)]:
        for i, ((w, h), st) in enumerate(zip(sizes, style)):
            write_dds(tdir / f"border_{name}_{i}.dds", border_texture(w, h, st), mips=False)
    write_dds(tdir / "strait.dds", strait_texture(), mips=False)

    # relief: no shading. The heightmap stays Valsora's: flattening it (land 98, sea 89)
    # made a cliff at every coast that the terrain mesh, coarser than the map's pixels,
    # drew as stair steps and squares (in-game test, 2026-10-07)
    flat = np.zeros((HH, HW, 3), np.uint8)
    flat[...] = (128, 128, 255)
    write_bmp(OUT / "map/world_normal.bmp", flat)

    # symbols, the frame, the lettering
    cloth = book_cloth()
    write_dds(OUT / "gfx/models/map_border_d.dds", cloth)
    nrm = np.zeros((1024, 1024, 4), np.float32)
    nrm[...] = (128, 128, 0, 128)
    write_dds(OUT / "gfx/models/map_border_n.dds", nrm, mips=False)
    spec = np.zeros((1024, 1024, 4), np.float32)
    spec[...] = (0, 24, 24, 40)
    write_dds(OUT / "gfx/models/map_border_s.dds", spec, mips=False)
    n_glyphs, page = map_font(OUT / "gfx" / "fonts")
    print(f"  map font: {n_glyphs} characters, page {page[0]}x{page[1]}")

    # defines, post effects off, descriptor, licences
    (OUT / "common/defines").mkdir(parents=True)
    (OUT / "common/defines/00_valsora_atlas.lua").write_text(DEFINES)
    (OUT / "gfx/posteffect_volumes.txt").write_text("")
    (OUT / "descriptor.mod").write_text(descriptor())
    Path("build", f"{NAME}.mod").write_text(descriptor([f'path="mod/{NAME}"']))
    lic = ["Valsora: Atlas uses two typefaces under the SIL Open Font License 1.1:",
           "Cinzel (c) The Cinzel Project Authors, and EB Garamond (c) The EB Garamond",
           "Project Authors. Their licences follow.", ""]
    lic += [(FONTS / f).read_text() for f in ("OFL_Cinzel.txt", "OFL_EBGaramond.txt")]
    (OUT / "FONT_LICENSES.txt").write_text("\n".join(lic))

    check()
    prev = preview(kind, land, sea)
    prev.resize((512, 256), Image.LANCZOS).save(OUT / "thumbnail.png")
    prev.save("dist/preview_atlas.png")
    preview_closeups(prev)
    out = Path("dist") / f"{NAME}.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for f in sorted(OUT.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(OUT.parent).as_posix())
        z.write(Path("build", f"{NAME}.mod"), f"{NAME}.mod")
    print(f"wrote {OUT} and {out} ({out.stat().st_size / 1e6:.1f} MB) in {time.time() - t0:.0f} s")


# ---------------------------------------------------------------- previews
def owners_map():
    """Country colour index per map pixel (-1 = none), from the main mod's build."""
    import re
    p = np.load("work/provinces.npz")
    tags = {v[0]: v[3] for v in COUNTRIES.values()}
    order = sorted(tags)
    own_of = np.full(len(p["kind"]) + 1, -1)
    for f in Path("build/valsora_test/history/states").glob("*.txt"):
        t = f.read_text(encoding="utf-8")
        tag = re.search(r"owner = (\w+)", t).group(1)
        ids = re.search(r"provinces = \{([^}]*)\}", t).group(1).split()
        own_of[np.array(ids, int)] = order.index(tag)
    names = {v[0]: v[1] for v in COUNTRIES.values()}
    return own_of[p["prov"] + 1], order, tags, names


def overlay(base, blend_):
    """The overlay blend HOI4's terrain shader is assumed to use (colour map over tiles)."""
    b, c = base / 255, blend_ / 255
    return 255 * np.where(b < 0.5, 2 * b * c, 1 - 2 * (1 - b) * (1 - c))


def preview(kind, land_cmap, sea_cmap):
    """A rough picture of the political map with this submod: the game draws it with its
    own shaders, so colours and line widths in game will differ somewhat."""
    own, order, cols, names = owners_map()
    own_h = own[::2, ::2]
    landm = kind[::2, ::2] == 1
    tile = np.tile(paper_tile(SEED + 100, 256), (HH // 256 + 1, HW // 256 + 1, 1))[:HH, :HW]
    page = overlay(tile, land_cmap)
    pal = np.array([cols[t] for t in order] + [(0, 0, 0)], float)
    # the wash and the band along borders
    o = np.where(landm, own_h, -1)
    edge = np.zeros(o.shape, bool)
    for ax in (0, 1):
        d = np.diff(o, axis=ax) != 0
        if ax == 0:
            edge[1:] |= d
            edge[:-1] |= d
        else:
            edge[:, 1:] |= d
            edge[:, :-1] |= d
    coast = landm & ~ndi.binary_erosion(landm)
    dist_b = ndi.distance_transform_edt(~(edge & landm))
    band = np.clip(1 - dist_b / 13.0, 0, 1) ** 1.5
    fill = pal[o]
    wash = 0.30 + 0.32 * band
    img = np.where(landm[..., None], page * (1 - wash[..., None]) + fill * page / 255 * wash[..., None] * 1.15,
                   sea_cmap)
    # country borders: ink line
    line = edge & landm & (o >= 0)
    img = np.where(line[..., None], img * 0.25 + INK * 0.75 * 0.75, img)
    img = np.clip(img, 0, 255)
    pim = Image.fromarray(img.astype(np.uint8))
    # country names, letter-spaced capitals across each country's largest piece
    d = ImageDraw.Draw(pim)
    for idx, tag in enumerate(order):
        m = o == idx
        if m.sum() < 400:
            continue
        lab, n = ndi.label(m)
        sizes = np.bincount(lab.ravel())[1:]
        big = lab == (np.argmax(sizes) + 1)
        ys, xs = np.nonzero(big)
        if len(xs) < 400:
            continue
        name = names[tag].upper()
        span = np.percentile(xs, 92) - np.percentile(xs, 8)
        sz = int(np.clip(span / max(len(name), 3) * 0.9, 9, 60))
        f = font("Cinzel[wght].ttf", sz, 600)
        tr = sz * 0.12
        tw = sum(f.getlength(ch) + tr for ch in name) - tr
        cx, cy = np.median(xs), np.median(ys)
        x = cx - tw / 2
        for ch in name:
            d.text((x, cy), ch, font=f, fill=(40, 32, 26), anchor="lm")
            x += f.getlength(ch) + tr
    return pim


def preview_closeups(prev):
    """Two close-ups at the colour maps' full resolution, for the author to judge."""
    W_, H_ = prev.size
    crops = [((150, 230, 950, 680), "dist/preview_atlas_closeup_nonscio.png"),
             ((1300, 20, 2100, 470), "dist/preview_atlas_closeup_yastreovakia.png")]
    for box, path in crops:
        prev.crop(box).save(path)


# ---------------------------------------------------------------- self-check
EXPECTED = {  # path: (width, height), the sizes the base game's files have
    "map/terrain/colormap_rgb_cityemissivemask_a.dds": (HW, HH),
    "map/terrain/colormap_water_0.dds": (HW, HH),
    "map/terrain/colormap_water_1.dds": (HW // 2, HH // 2),
    "map/terrain/colormap_water_2.dds": (HW // 4, HH // 4),
    "map/terrain/fow_rgb_waterspec_a.dds": (HW, HH),
    "map/terrain/border_country_0.dds": (256, 128), "map/terrain/border_country_1.dds": (128, 64),
    "map/terrain/border_country_2.dds": (64, 32), "map/terrain/border_state_0.dds": (128, 64),
    "map/terrain/border_state_1.dds": (256, 128), "map/terrain/border_state_2.dds": (256, 128),
    "map/terrain/border_sea_1.dds": (53, 32), "map/terrain/strait.dds": (64, 64),
}


def check():
    """Re-read everything written and stop on anything malformed."""
    import re
    problems = []
    for f in sorted(OUT.rglob("*.dds")):
        rel = f.relative_to(OUT).as_posix()
        b = f.read_bytes()
        if b[:4] != b"DDS " or struct.unpack_from("<I", b, 4)[0] != 124:
            problems.append(f"{rel}: not a DDS file")
            continue
        h, w = struct.unpack_from("<II", b, 12)
        mips = max(struct.unpack_from("<I", b, 28)[0], 1)
        pf, four = struct.unpack_from("<I", b, 80)[0], b[84:88]
        caps2 = struct.unpack_from("<I", b, 112)[0]
        faces = 6 if caps2 & 0x200 else 1
        size, ww, hh = 0, w, h
        for _ in range(mips):
            size += ww * hh * 4 if pf == 0x41 else max(1, (ww + 3) // 4) * max(1, (hh + 3) // 4) * 16
            ww, hh = max(ww // 2, 1), max(hh // 2, 1)
        if len(b) != 128 + size * faces:
            problems.append(f"{rel}: {len(b) - 128} bytes of data, expected {size * faces}")
        if rel in EXPECTED and EXPECTED[rel] != (w, h):
            problems.append(f"{rel}: {w}x{h}, expected {EXPECTED[rel]}")
        if pf == 0x4 and four != b"DXT3":
            problems.append(f"{rel}: unexpected format {four}")
    fnt = (OUT / "gfx/fonts/hoi_mapfont4.fnt").read_text()
    tw, th = map(int, re.search(r"scaleW=(\d+) scaleH=(\d+)", fnt).groups())
    for m in re.finditer(r"char id=(\d+)\s+x=(\d+)\s+y=(\d+)\s+width=(\d+)\s+height=(\d+)", fnt):
        cid, x, y, w, h = map(int, m.groups())
        if x + w > tw or y + h > th:
            problems.append(f"font: character {cid} lies outside the page")
    if "\r\n" not in fnt.replace("\n", "\r\n") or not fnt.startswith("info "):
        problems.append("font: not a BMFont text file")
    wn = read_bmp(OUT / "map/world_normal.bmp")
    if (wn["width"], wn["height"], wn["bpp"]) != (HW, HH, 24):
        problems.append("world_normal.bmp: wrong size or depth")
    desc = (OUT / "descriptor.mod").read_text()
    if f'"{MOD_NAME}"' not in desc:
        problems.append("descriptor.mod: Valsora is not a dependency")
    if problems:
        raise SystemExit("atlas_mod check failed:\n  " + "\n  ".join(problems))
    print(f"  check: {len(list(OUT.rglob('*.dds')))} textures and the map files are well formed")


if __name__ == "__main__":
    main()
