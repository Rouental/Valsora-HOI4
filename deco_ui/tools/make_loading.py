"""The loading screens, in the deco style, from Valsora's own map: four pictures for the background list (2026-10-17,
v0.10; drawn as a proposal on 2026-10-16, "don't add them yet", then the author: "Please start applying the proposed
changes to all the UI screens"). Out of the mod again in v0.10.1, kept for later (the author: "The globe map should be
kept for later, and I might return to the others but the map's not finalized quite yet"): by default they are drawn
into build/loading_screens/; --into-mod writes them where the mod would ship them (and make_menu.LOADING lists them).

    python3 tools/make_loading.py          -> valsora_deco_ui/gfx/loadingscreens/valsora_load_1..4.dds (1920 x 1440),
                                              their 192 x 144 pictures for the background picker
                                              (gfx/interface/valsora_deco/menu/valsora_load_N_small.dds), and
                                              build/preview_loading.png (each as a 16:9 screen shows it, the game's
                                              loading bar and tip drawn where it puts them)

The game draws no picture of its own on the loading screen (interface/load_screen.gui): it shows the backgrounds of the
background manager, the list `make_menu.py` writes (common/frontend/backgrounds/base_backgrounds.txt), the main menu's
picture among them. At 16:9 the middle 1080 rows of a 1920 x 1440 picture show, from row 180; the game draws its loading
bar over the top centre (about 1,400 x 100 px) and the tip over the bottom centre (about 1,400 x 150), with its two logos
in the lower corners, so the pictures keep their titles and detail clear of those. Each is drawn from the Valsora build's
map (work/, the repository's root), so run it again after the map changes (then commit the .dds files): 1 the world in
gilt, 2 Valsora rising (the masthead's globe, large), 3 the Vale of Reibonne, 4 the nations. The bar and the tip are
the Deco UI's too (gen_textures.py, the ld_ keys).
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage as ndi

import globe_art as GA
from paths import ROOT, MOD, BUILD
from ddsutil import write_dds

ROOT = ROOT.rstrip("/") + "/"
REPO = os.path.dirname(ROOT.rstrip("/")) + "/"
sys.path.insert(0, REPO + "scripts")
from common import COUNTRIES  # noqa: E402

# out of the mod since v0.10.1 (kept for later): they are drawn into build/loading_screens/, or into the mod with
# --into-mod (then list them in make_menu.LOADING)
if "--into-mod" in sys.argv:
    OUT = MOD + "gfx/loadingscreens/"
    SMALL = MOD + "gfx/interface/valsora_deco/menu/"
else:
    OUT = SMALL = BUILD + "loading_screens/"
NAMES = [f"valsora_load_{i}" for i in range(1, 5)]   # make_menu.py lists them in the background manager
W, H, TOP = 1920, 1440, 180                 # the picture, and the first row a 16:9 screen shows
VIS = (TOP, TOP + 1080)
TITLE_Y = TOP + 118                          # under the game's loading bar (the top 100 rows of the screen)
FEDERO = ROOT + "source_fonts/federo/Federo-Regular.ttf"
JOSEFIN = ROOT + "source_fonts/josefinsans/JosefinSans[wght].ttf"
LAC, LAC2, DARK = np.array([17, 25, 30]), np.array([23, 34, 42]), np.array([11, 16, 20])
GILT, RULE, HI, CREAM = np.array([227, 199, 126]), np.array([201, 165, 90]), np.array([241, 220, 156]), np.array([244, 236, 217])
REIBONNAISE = ["ROU", "GDN", "LST", "EVR", "HLR", "SGV", "LZC", "SGN"]
CAPITAL_ROU = (660, 805)                     # Rêverie (nations.CAPITALS)


# ------------------------------------------------------------------ pieces
def lacquer():
    """the panels' lacquer, pinstriped, darker towards the edges"""
    y, x = np.mgrid[0:H, 0:W]
    img = np.zeros((H, W, 3), np.float32) + LAC2
    img[(x % 8) == 0] += 4
    r = np.hypot((x - W / 2) / (W / 2), (y - (TOP + 540)) / 760)
    img = img * (1 - .45 * np.clip(r - .45, 0, 1)[..., None])
    return img


def blend(img, mask, col, a=1.0):
    m = (np.clip(mask, 0, 1) * a)[..., None]
    img[:] = img * (1 - m) + np.asarray(col, np.float32) * m


def gilt_ramp(t):
    """the gilt gradient, #E8CD84 at 0 to #8B6A2C at 1"""
    a, b = np.array([232, 205, 132], np.float32), np.array([139, 106, 44], np.float32)
    t = np.clip(t, 0, 1)[..., None]
    return a * (1 - t) + b * t


def text_mask(text, font, size, track=0.0):
    f = ImageFont.truetype(font, size)
    if track:
        widths = [f.getlength(c) for c in text]
        w = int(sum(widths) + track * size * (len(text) - 1)) + 8
    else:
        w = int(f.getlength(text)) + 8
    asc, desc = f.getmetrics()
    im = Image.new("L", (w, asc + desc + 8), 0)
    d = ImageDraw.Draw(im)
    if track:
        x = 4
        for c, cw in zip(text, widths):
            d.text((x, 4), c, font=f, fill=255)
            x += cw + track * size
    else:
        d.text((4, 4), text, font=f, fill=255)
    return np.asarray(im, np.float32) / 255


def put(img, m, cx, y, col=None, halo=0, gilt=False):
    """a text mask centred on cx with its top at y, in col or the gilt gradient, with a dark halo"""
    h, w = m.shape
    x0 = int(round(cx - w / 2))
    region = img[y:y + h, x0:x0 + w]
    if halo:
        hm = ndi.grey_dilation(m, size=(halo * 2 + 1, halo * 2 + 1))
        hm = ndi.gaussian_filter(hm, halo * .6)
        blend(region, hm, DARK, .85)
    if gilt:
        rows = np.linspace(0, 1, h)[:, None] * np.ones((1, w))
        c = gilt_ramp(rows * .9)
        region[:] = region * (1 - m[..., None]) + c * m[..., None]
    else:
        blend(region, m, col)
    return x0, x0 + w


def title(img, text, y, size=64, sub=None):
    """the title in gilt capitals between two hairlines ending in diamonds, and a line under it"""
    m = text_mask(text.upper(), FEDERO, size, track=.22)
    x0, x1 = put(img, m, W / 2, y, gilt=True, halo=3)
    d = Image.fromarray(np.zeros((H, W), np.uint8))
    dr = ImageDraw.Draw(d)
    cy = y + m.shape[0] // 2 + 2
    for a, b in ((x0 - 260, x0 - 24), (x1 + 24, x1 + 260)):
        dr.line((a, cy, b, cy), fill=255, width=2)
    for x in (x0 - 270, x1 + 270):
        dr.polygon([(x, cy - 7), (x + 7, cy), (x, cy + 7), (x - 7, cy)], fill=255)
    blend(img, np.asarray(d, np.float32) / 255, RULE)
    if sub:
        s = text_mask(sub.upper(), FEDERO, 19, track=.3)
        put(img, s, W / 2, y + m.shape[0] + 8, CREAM, halo=3)


def frame(img):
    """double gilt hairlines round the part a 16:9 screen shows, with stepped corners and a diamond in each"""
    d = Image.new("L", (W, H), 0)
    dr = ImageDraw.Draw(d)
    for inset, wd in ((26, 2), (34, 1)):
        x0, y0, x1, y1 = inset, VIS[0] + inset, W - inset, VIS[1] - inset
        c = 22
        dr.line([(x0 + c, y0), (x1 - c, y0), (x1 - c, y0 + 0), (x1, y0 + c), (x1, y1 - c), (x1 - c, y1), (x0 + c, y1),
                 (x0, y1 - c), (x0, y0 + c), (x0 + c, y0)], fill=255, width=wd)
    for x, y in ((26, VIS[0] + 26), (W - 26, VIS[0] + 26), (26, VIS[1] - 26), (W - 26, VIS[1] - 26)):
        dr.polygon([(x, y - 9), (x + 9, y), (x, y + 9), (x - 9, y)], fill=255)
    blend(img, np.asarray(d, np.float32) / 255, GILT, .9)


def rays(img, cx, cy, n=48, a=.07, r0=0):
    y, x = np.mgrid[0:H, 0:W]
    ang = np.arctan2(y - cy, x - cx)
    band = (np.floor((ang + np.pi) / (2 * np.pi) * n) % 2 == 0).astype(np.float32)
    r = np.hypot(x - cx, y - cy)
    fade = np.clip((r - r0) / 300, 0, 1) * np.clip(1 - (r - r0) / 1400, 0, 1)
    blend(img, band * fade, GILT, a)


def save(img, name):
    """the picture as an uncompressed DDS, as the game's own loading screens are, and its small picture for the picker"""
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
    write_dds(im, OUT + name + ".dds")
    write_dds(im.convert("RGB").resize((192, 144), Image.LANCZOS).convert("RGBA"), SMALL + name + "_small.dds")
    return im


# ------------------------------------------------------------------ the map
def world():
    w = np.load(REPO + "work/world.npz")
    p = np.load(REPO + "work/provinces.npz")
    rj = json.load(open(REPO + "work/regions.json"))
    state_of = np.load(REPO + "work/regions.npz")["state_of"]
    tags = sorted({t for t in rj["owners"]})
    idx = {t: i + 1 for i, t in enumerate(tags)}
    owner_of_state = np.array([idx[t] for t in rj["owners"]] + [0])
    so = state_of[p["prov"]]
    owner = np.where(so >= 0, owner_of_state[so], 0)
    return w["kind"], w["cont"], w["rivers"], owner, tags


def fit(a, size, resample=Image.BILINEAR):
    return np.asarray(Image.fromarray(a.astype(np.float32)).resize(size, resample), np.float32)


def edges(lab):
    e = np.zeros(lab.shape, bool)
    e[:, 1:] |= lab[:, 1:] != lab[:, :-1]
    e[1:, :] |= lab[1:, :] != lab[:-1, :]
    return e


def graticule(img, box, step=30, a=.12):
    x0, y0, x1, y1 = box
    d = Image.new("L", (W, H), 0)
    dr = ImageDraw.Draw(d)
    for lon in range(-180, 181, step):
        x = x0 + (lon + 180) / 360 * (x1 - x0)
        dr.line((x, y0, x, y1), fill=255, width=1)
    for lat in range(-90, 91, step):
        y = y0 + (90 - lat) / 180 * (y1 - y0)
        dr.line((x0, y, x1, y), fill=255, width=1)
    blend(img, np.asarray(d, np.float32) / 255, RULE, a)


# ------------------------------------------------------------------ the four screens
def screen_world(kind, cont):
    img = lacquer()
    mw, mh = 1480, 740
    x0, y0 = (W - mw) // 2, 412
    box = (x0, y0, x0 + mw, y0 + mh)
    land = fit((kind == 1).astype(np.float32), (mw, mh))
    land = np.clip((land - .5) * 3 + .5, 0, 1)
    full = np.zeros((H, W), np.float32)
    full[y0:y0 + mh, x0:x0 + mw] = land
    blend(img, np.ones((H, W)) * 0, DARK)
    sea = np.zeros((H, W), np.float32)
    sea[y0:y0 + mh, x0:x0 + mw] = 1
    blend(img, sea, DARK, .55)
    graticule(img, box)
    yy, xx = np.mgrid[0:H, 0:W]
    shade = gilt_ramp(.25 + .55 * ((xx - x0) / mw * .4 + (yy - y0) / mh * .6))
    img[:] = img * (1 - full[..., None]) + shade * full[..., None]
    coast = np.clip(ndi.gaussian_gradient_magnitude(full, 1.0) * 2.2, 0, 1)
    blend(img, coast, HI, .9)
    # the continents' names, at the middle of each one's land
    names = ["Nonscio", "Araseos", "Aislada", "Solitas", "Yastreovakia", "Usnistan", "Orientalis"]
    cs = fit(cont.astype(np.float32), (mw, mh), Image.NEAREST)
    for i, nm in enumerate(names, 1):
        m = (cs == i) & (land > .5)
        if m.sum() < 50:
            continue
        dist = ndi.distance_transform_edt(m)
        cy, cx = np.unravel_index(int(np.argmax(dist)), dist.shape)
        t = text_mask(nm.upper(), FEDERO, 26, track=.3)
        put(img, t, x0 + cx, y0 + cy - t.shape[0] // 2, CREAM, halo=4)
    frame(img)
    title(img, "Valsora", TITLE_Y, 58, "The world in the year 2036")
    return img


def screen_rising():
    img = lacquer()
    cx, cy, d = W // 2, 1080, 1180
    rays(img, cx, cy, n=56, a=.10, r0=d // 2 - 40)
    g = GA.globe(d, k=2, grid=30, sigma=.6)
    g = np.asarray(g.convert("RGBA"), np.float32) if hasattr(g, "convert") else np.asarray(g, np.float32)
    a = g[..., 3:4] / 255
    y0, x0 = cy - d // 2, cx - d // 2
    ys, ye = max(0, y0), min(H, y0 + d)
    reg = img[ys:ye, x0:x0 + d]
    gg, aa = g[ys - y0:ye - y0, :, :3], a[ys - y0:ye - y0]
    reg[:] = reg * (1 - aa) + gg * aa
    # a gilt ring round it
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.hypot(xx - cx, yy - cy)
    blend(img, np.clip(1 - np.abs(r - d / 2 - 10) / 1.6, 0, 1), GILT)
    blend(img, np.clip(1 - np.abs(r - d / 2 - 22) / 1.0, 0, 1), RULE, .8)
    frame(img)
    title(img, "Valsora", TITLE_Y, 72, "Rising, 2036")
    return img


def screen_vale(kind, rivers, owner, tags):
    img = lacquer()
    idx = {t: i + 1 for i, t in enumerate(tags)}
    ids = [idx[t] for t in REIBONNAISE if t in idx]
    yy0, xx0 = np.mgrid[0:owner.shape[0], 0:owner.shape[1]]
    near = np.hypot(xx0 - CAPITAL_ROU[0], yy0 - CAPITAL_ROU[1]) < 320
    ys, xs = np.nonzero(np.isin(owner, ids) & near)
    gx0, gx1, gy0, gy1 = xs.min(), xs.max(), ys.min(), ys.max()
    # a 16:9 box round the Vale, with room for the title and the tip
    vw, vh = 1760, 860
    scale = min(vw / (gx1 - gx0 + 40), vh / (gy1 - gy0 + 40))
    bw, bh = vw / scale, vh / scale
    cxg, cyg = (gx0 + gx1) / 2, (gy0 + gy1) / 2
    bx0, by0 = int(cxg - bw / 2), int(cyg - bh / 2)
    bx1, by1 = int(bx0 + bw), int(by0 + bh)
    ox, oy = (W - vw) // 2, VIS[0] + 196
    crop = lambda a: a[by0:by1, bx0:bx1]
    k, ow, rv = crop(kind), crop(owner), crop(rivers)
    size = (vw, vh)
    land = ndi.gaussian_filter(fit((k == 1).astype(np.float32), size, Image.BILINEAR), scale * .45)
    land = np.clip((land - .5) * 3 + .5, 0, 1)
    full = lambda a: np.pad(a, ((oy, H - oy - vh), (ox, W - ox - vw)))
    L = full(land)
    blend(img, full(np.ones((vh, vw))), DARK, .6)
    # waves on the sea
    yy, xx = np.mgrid[0:H, 0:W]
    lines = ((yy % 14) == 0).astype(np.float32)
    blend(img, full(np.ones((vh, vw))) * lines * (1 - L), RULE, .10)
    # other land: lacquer; the Reibonnaise states: deep jewels from their own colours
    blend(img, L, np.array([32, 44, 50]))
    lab = np.zeros((vh, vw), np.int32)
    best = np.zeros((vh, vw), np.float32)
    for t in REIBONNAISE:
        if t not in idx:
            continue
        m = ndi.gaussian_filter(fit((ow == idx[t]).astype(np.float32), size, Image.BILINEAR), scale * .45)
        lab[m > best] = idx[t]
        best = np.maximum(best, m)
        col = np.array(COUNTRIES[next(c for c, v in COUNTRIES.items() if v[0] == t)][3], np.float32)
        col = col * .5 + LAC * .3 + GILT * .2
        blend(img, full(np.clip((m - .5) * 4 + .5, 0, 1) * land), col)
    lab[best < .5] = 0
    border = edges(lab) & (land > .5)
    border = ndi.binary_dilation(border, iterations=1)
    blend(img, full(ndi.gaussian_filter(border.astype(np.float32), .6)) * 1.4, GILT)
    coast = np.clip(ndi.gaussian_gradient_magnitude(L, 1.0) * 2.4, 0, 1)
    blend(img, coast, HI, .85)
    # rivers (rivers.bmp: 0-11 are river pixels) in pale jade
    riv = (rv < 12) & (k == 1)
    d = Image.new("L", (vw * 2, vh * 2), 0)
    dr = ImageDraw.Draw(d)
    ry, rx = np.nonzero(riv)
    on = set(zip(ry.tolist(), rx.tolist()))
    s2 = scale * 2
    for y, x in on:
        for dy, dx in ((0, 1), (1, 0), (1, 1), (1, -1)):
            if (y + dy, x + dx) in on and not (dx and dy and ((y, x + dx) in on or (y + dy, x) in on)):
                dr.line(((x + .5) * s2, (y + .5) * s2, (x + dx + .5) * s2, (y + dy + .5) * s2), fill=255, width=5)
    rmask = np.asarray(d.resize((vw, vh), Image.LANCZOS), np.float32) / 255
    # the game's rivers step from pixel to pixel: softened, then drawn as a line of even width
    g = ndi.gaussian_filter(rmask, scale * .55)
    rmask = np.clip((g - .16) / .14, 0, 1)
    blend(img, full(rmask), np.array([120, 190, 172]), .9)
    # the ranges the author drew (source/vale_ranges.png at (572, 747)): gilt chevrons
    rng = np.asarray(Image.open(REPO + "source/vale_ranges.png").convert("RGB")).any(axis=2)
    gm = np.zeros(kind.shape, bool)
    gm[747:747 + rng.shape[0], 572:572 + rng.shape[1]] = rng
    rm = fit(crop(gm).astype(np.float32), size, Image.BILINEAR) > .5
    d = Image.new("L", (vw, vh), 0)
    dr = ImageDraw.Draw(d)
    step = 26
    for y in range(step // 2, vh, step):
        for x in range((y // step % 2) * step // 2, vw, step):
            if rm[y, x]:
                dr.line([(x - 8, y + 5), (x, y - 5), (x + 8, y + 5)], fill=255, width=2)
    blend(img, full(np.asarray(d, np.float32) / 255), HI, .75)
    # names and the capital
    placed = []
    order = sorted((t for t in REIBONNAISE if t in idx), key=lambda t: -(lab == idx[t]).sum())
    for t in order:
        m = lab == idx[t]
        if not m.any():
            continue
        dist = ndi.distance_transform_edt(m)
        cy, cx = np.unravel_index(int(np.argmax(dist)), dist.shape)
        area = m.sum() / scale ** 2                  # in game pixels
        nm = COUNTRIES[next(c for c, v in COUNTRIES.items() if v[0] == t)][1]
        size_ = 34 if t == "ROU" else 22 if area > 500 else 17
        tm = text_mask(nm.upper(), FEDERO, size_, track=.25)
        th, tw = tm.shape
        small = tw > 2 * dist.max() + 20             # the name is wider than the nation
        if small:                                    # a dot on it, the name beside, clear of the others
            dot = np.zeros((H, W), np.float32)
            yy_, xx_ = np.ogrid[0:H, 0:W]
            dot[(yy_ - (oy + cy)) ** 2 + (xx_ - (ox + cx)) ** 2 <= 30] = 1
            blend(img, ndi.gaussian_filter(dot, 1.5) * 1.5, DARK, .8)
            blend(img, dot, HI)
        cands = [(0, 0)] if not small else []
        cands += [(0, -th - 4), (0, th + 4), (tw // 2 + 14, 0), (-tw // 2 - 14, 0), (0, -2 * th), (0, 2 * th),
                  (tw // 2 + 14, -th), (-tw // 2 - 14, th)]
        for dx_, dy_ in cands:
            bx, by = ox + cx + dx_ - tw / 2, oy + cy + dy_ - th / 2
            box = (bx - 4, by - 2, bx + tw + 4, by + th + 2)
            if not any(box[0] < q[2] and q[0] < box[2] and box[1] < q[3] and q[1] < box[3] for q in placed):
                break
        placed.append(box)
        put(img, tm, ox + cx + dx_, int(oy + cy + dy_ - th / 2), CREAM, halo=4)
    sx, sy = ox + (CAPITAL_ROU[0] - bx0) * scale, oy + (CAPITAL_ROU[1] - by0) * scale
    star = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(star)
    pts = []
    for i in range(16):
        ang = np.pi / 2 + i * np.pi / 8
        rr = 16 if i % 2 == 0 else 6
        pts.append((sx + rr * np.cos(ang), sy - rr * np.sin(ang)))
    sd.polygon(pts, fill=255)
    blend(img, ndi.gaussian_filter(np.asarray(star, np.float32) / 255, 4) * 1.2, DARK, .8)
    blend(img, np.asarray(star, np.float32) / 255, HI)
    tm = text_mask("Rêverie", FEDERO, 20, track=.1)
    put(img, tm, sx, int(sy + 18), HI, halo=3)
    frame(img)
    title(img, "The Vale of Reibonne", TITLE_Y, 52, "Rouental and the Association of Reibonnaise States")
    return img


def screen_nations(kind, owner, tags):
    img = lacquer()
    rays(img, W / 2, TOP + 600, n=64, a=.05, r0=200)
    mw, mh = 1480, 740
    x0, y0 = (W - mw) // 2, 412
    # each nation's map colour, muted towards lacquer and warmed with gilt; the sea dark
    pal = np.zeros((len(tags) + 1, 3), np.float32)
    by_tag = {v[0]: v[3] for v in COUNTRIES.values()}
    for i, t in enumerate(tags, 1):
        c = np.array(by_tag.get(t, (120, 120, 120)), np.float32)
        pal[i] = c * .55 + LAC * .30 + GILT * .15
    small = np.asarray(Image.fromarray(owner.astype(np.int32)).resize((mw, mh), Image.NEAREST))
    land = np.clip((fit((kind == 1).astype(np.float32), (mw, mh)) - .5) * 3 + .5, 0, 1)
    sea = np.zeros((H, W), np.float32)
    sea[y0:y0 + mh, x0:x0 + mw] = 1
    blend(img, sea, DARK, .6)
    graticule(img, (x0, y0, x0 + mw, y0 + mh), a=.08)
    col = pal[small]
    reg = img[y0:y0 + mh, x0:x0 + mw]
    lm = (land * (small > 0))[..., None]
    reg[:] = reg * (1 - lm) + col * lm
    b = edges(small) & (small > 0) & (land > .5)
    blend(reg, ndi.gaussian_filter(b.astype(np.float32), .5) * 1.3, GILT, .9)
    full = np.zeros((H, W), np.float32)
    full[y0:y0 + mh, x0:x0 + mw] = land
    blend(img, np.clip(ndi.gaussian_gradient_magnitude(full, 1.0) * 2.2, 0, 1), HI, .9)
    frame(img)
    title(img, "The Nations of Valsora", TITLE_Y, 52, f"{len(tags)} nations on the map, 1 January 2036")
    return img


# ------------------------------------------------------------------ the sheet: as the game would show them
def sheet(pictures):
    """build/preview_loading.png: each picture as a 16:9 screen shows it, with the game's loading bar and tip (the Deco
    UI's pictures for them, when gen_textures.py has drawn them) where load_screen.gui puts them"""
    from ddsutil import read_dds
    def piece(name):
        try:
            return read_dds(MOD + "gfx/interface/" + name + ".dds").convert("RGBA")
        except Exception:
            return None
    status, tip = piece("Loadingscreen_loadingstatus"), piece("Loadingscreen_loadingtip")
    bar_bg, bar_fill = piece("LoadingScreen_Progress_1"), piece("LoadingScreen_Progress_2")
    f = ImageFont.truetype(FEDERO, 28)
    f2 = ImageFont.truetype(FEDERO, 22)
    tiles = []
    for pic in pictures:
        im = pic.crop((0, TOP, W, TOP + 1080)).convert("RGBA")
        d = ImageDraw.Draw(im, "RGBA")
        if status is not None:     # the status window: CENTER_UP, its picture at x -700 (1400 wide)
            im.alpha_composite(status, (960 - 700, 0))
            if bar_bg is not None:
                im.alpha_composite(bar_bg, (960 - 468, 62))
                im.alpha_composite(bar_fill.crop((0, 0, 560, bar_fill.height)), (960 - 468, 62))
        d.text((960, 13 + 20), "LOADING THE MAP", font=f, fill=(244, 236, 217, 255), anchor="mm")
        if tip is not None:        # the tip window: CENTER_DOWN, its picture at y -147
            im.alpha_composite(tip, (960 - 700, 1080 - 147))
        d.text((960, 1080 - 57), "A loading tip, in the game's own words.", font=f2, fill=(244, 236, 217, 255), anchor="mm")
        tiles.append(im.convert("RGB").resize((960, 540), Image.LANCZOS))
    out = Image.new("RGB", (1920 + 12, 1080 + 12), (11, 16, 20))
    for i, t in enumerate(tiles):
        out.paste(t, ((i % 2) * 972, (i // 2) * 552))
    out.save(BUILD + "preview_loading.png", optimize=True)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(SMALL, exist_ok=True)
    kind, cont, rivers, owner, tags = world()
    pictures = []
    for name, (label, draw) in zip(NAMES, (("the world", lambda: screen_world(kind, cont)),
                                           ("Valsora rising", screen_rising),
                                           ("the Vale of Reibonne", lambda: screen_vale(kind, rivers, owner, tags)),
                                           ("the nations", lambda: screen_nations(kind, owner, tags)))):
        pictures.append(save(draw(), name))
        print(f"{name}.dds: {label}")
    sheet(pictures)
    print("wrote", OUT, "and", BUILD + "preview_loading.png")
