"""A teaser for the Vale of Reibonne (the author, 2026-10-22: "could you create a sort of teaser image for the Vale of
Reibonne, showing the flag and leader of each nation, maybe in front of the map?"): the eight nations of the start on
the map as the build has them, a small flag pinned on each, and a card a nation down either side (its ruler's portrait,
flag, names), in the Deco UI's look. Everything in it is the author's and their friends' (the map, the flags, the
portraits) or the mod's own fonts (OFL): nothing of the base game's.

    CHROMIUM_PATH=/opt/pw-browsers/chromium python3 dist/teasers/vale_of_reibonne/make.py   (after a build)

Writes vale_of_reibonne.png (1920 x 1080) beside this file.
"""
import base64
import glob
import io
import json
import os
import re
import sys

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "scripts"))
import gazetteer  # noqa: E402
import nations  # noqa: E402
from common import COUNTRIES  # noqa: E402

B = os.path.join(REPO, "build", "valsora_test")
FONTS = os.path.join(REPO, "deco_ui", "source_fonts")
W, H, SCALE = 1920, 1080, 3.6
# the map pixel at the image's top left: the Vale (575-882, 749-918) between the cards, under the title
X0, Y0 = 728.5 - 960 / SCALE, 833.5 - 610 / SCALE
# the cards: Rouental and the three nearest it on the left, the four of the north-east on the right, north to south
LEFT = ["ROU", "EVR", "SGN", "GDN"]
RIGHT = ["SGV", "LZC", "LST", "HLR"]
NAMES = {"GDN": "The Council of Seven"}  # the author, 2026-10-22: "making it the Council of Seven" (its page still says Six)
GOLD, RULE = (227, 199, 126), (201, 165, 90)


def owners():
    """the owner and the state of every map pixel (the build's provinces and states)"""
    img = np.array(Image.open(os.path.join(B, "map", "provinces.bmp")).convert("RGB")).astype(np.int64)
    key = (img[..., 0] << 16) | (img[..., 1] << 8) | img[..., 2]
    col = {}
    for ln in open(os.path.join(B, "map", "definition.csv")).read().splitlines()[1:]:
        f = ln.split(";")
        col[(int(f[1]) << 16) | (int(f[2]) << 8) | int(f[3])] = int(f[0])
    u, inv = np.unique(key, return_inverse=True)
    prov = np.array([col.get(int(c), 0) for c in u])[inv].reshape(key.shape)
    own, st = np.zeros(prov.max() + 1, "U3"), np.zeros(prov.max() + 1, int)
    for f in glob.glob(os.path.join(B, "history", "states", "*.txt")):
        t = open(f, encoding="utf-8-sig").read()
        o = re.search(r"\bowner\s*=\s*(\w+)", t).group(1)
        n = int(re.search(r"\bid\s*=\s*(\d+)", t).group(1))
        for p in re.search(r"provinces\s*=\s*\{([^}]*)\}", t).group(1).split():
            own[int(p)], st[int(p)] = o, n
    return own[prov], st[prov]


def colour(tag):
    return next(v[3] for v in COUNTRIES.values() if v[0] == tag)


def smooth_labels(L, ids, size, ox, oy, sigma=2.0):
    """L (a region of map pixels) up to size and cut at (ox, oy) to W x H: each id's mask enlarged and softened, the
    strongest at each pixel, so the borders are curves, not the map's stair steps; 0 where none of ids"""
    best, lab = np.full((H, W), .5, np.float32), np.zeros((H, W), int)
    sx, sy = size[0] / L.shape[1], size[1] / L.shape[0]
    for k in ids:
        ys, xs = np.nonzero(L == k)
        if not len(ys):
            continue
        a, b = max(ys.min() - 3, 0), min(ys.max() + 4, L.shape[0])
        c, d = max(xs.min() - 3, 0), min(xs.max() + 4, L.shape[1])
        X0b, Y0b, X1b, Y1b = round(c * sx), round(a * sy), round(d * sx), round(b * sy)
        m = Image.fromarray(((L[a:b, c:d] == k) * 255).astype(np.uint8)).resize((X1b - X0b, Y1b - Y0b), Image.BILINEAR)
        m = ndi.gaussian_filter(np.asarray(m, np.float32) / 255, sigma)
        # into the picture's frame
        px0, py0 = X0b - ox, Y0b - oy
        qx0, qy0, qx1, qy1 = max(px0, 0), max(py0, 0), min(px0 + m.shape[1], W), min(py0 + m.shape[0], H)
        if qx0 >= qx1 or qy0 >= qy1:
            continue
        sub = m[qy0 - py0:qy1 - py0, qx0 - px0:qx1 - px0]
        win = sub > best[qy0:qy1, qx0:qx1]
        best[qy0:qy1, qx0:qx1][win] = sub[win]
        lab[qy0:qy1, qx0:qx1][win] = k
    return lab


def render_map(O, S, tags):
    """the region at SCALE, its edges smoothed: sea, the other land, the eight in their colours, gilt borders, their
    states' lines and the rivers faint"""
    pad = 4
    x0, y0 = int(X0) - pad, int(Y0) - pad
    win = (slice(y0, y0 + int(H / SCALE) + 2 * pad + 2), slice(x0, x0 + int(W / SCALE) + 2 * pad + 2))
    reg = O[win]
    classes = ["", "other"] + tags
    cls = np.where(reg == "", 0, 1)
    for i, t in enumerate(tags):
        cls = np.where(reg == t, i + 2, cls)
    # each class's mask up to SCALE and softened, then the strongest at each pixel: rounded borders, no stair steps
    size = (round(reg.shape[1] * SCALE), round(reg.shape[0] * SCALE))
    ox, oy = round((X0 - x0) * SCALE), round((Y0 - y0) * SCALE)
    stack = []
    for k in range(len(classes)):
        m = Image.fromarray(((cls == k) * 255).astype(np.uint8)).resize(size, Image.BILINEAR)
        stack.append(ndi.gaussian_filter(np.asarray(m, np.float32), 2.0))
    lab = np.argmax(np.stack(stack), 0)[oy:oy + H, ox:ox + W]
    out = np.zeros((H, W, 3), np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    sea_top, sea_bot = np.array((10, 24, 38), np.float32), np.array((6, 15, 25), np.float32)
    out[:] = sea_top + (sea_bot - sea_top) * (yy / H)[..., None]
    out[lab == 1] = (74, 76, 70)                                          # the neighbours, a muted stone
    for i, t in enumerate(tags):
        c = np.array(colour(t), np.float32)
        out[lab == i + 2] = c * .88 + np.array((40, 36, 28)) * .12        # a touch of warmth over the flag colours
    land = lab > 0
    # a soft shadow on the sea along the coasts
    dist = ndi.distance_transform_edt(~land)
    out[~land] *= (1 - .35 * np.exp(-dist[~land] / 10))[..., None]
    # the eight's states, a faint darker line where one meets another
    Sreg = np.where(np.isin(reg, tags), S[win], 0)
    st = smooth_labels(Sreg, np.unique(Sreg[Sreg > 0]), size, ox, oy)
    sb = np.zeros((H, W), bool)
    sb[:, 1:] |= (st[:, 1:] != st[:, :-1]) & (st[:, 1:] > 0) & (st[:, :-1] > 0)
    sb[1:, :] |= (st[1:, :] != st[:-1, :]) & (st[1:, :] > 0) & (st[:-1, :] > 0)
    m = np.clip(ndi.gaussian_filter((sb & (lab >= 2)).astype(np.float32), .6) * 1.4, 0, 1) * .32
    out *= (1 - m)[..., None]
    # the rivers
    R = np.array(Image.open(os.path.join(B, "map", "rivers.bmp")))[win] < 254
    r = Image.fromarray((R * 255).astype(np.uint8)).resize(size, Image.BILINEAR)
    r = ndi.gaussian_filter(np.asarray(r, np.float32)[oy:oy + H, ox:ox + W] / 255, .8)
    m = (np.clip((r - .18) * 2.4, 0, 1) * .8 * land)[..., None]
    out = out * (1 - m) + np.array((104, 150, 178), np.float32) * m
    # the borders: between nations gilt, the coast lighter, both a little soft
    nb = np.zeros((H, W), bool)
    nb[:, 1:] |= lab[:, 1:] != lab[:, :-1]
    nb[1:, :] |= lab[1:, :] != lab[:-1, :]
    coast = nb & (ndi.binary_dilation(~land, iterations=1) & ndi.binary_dilation(land, iterations=1))
    inner = nb & ~coast & (ndi.binary_dilation(lab >= 2, iterations=1))
    other = nb & ~coast & ~inner
    for mask, col, wdt, a in ((other, (90, 96, 100), 1, .5), (inner, RULE, 2, 1.0), (coast, GOLD, 2, .9)):
        m = ndi.gaussian_filter(ndi.binary_dilation(mask, iterations=wdt - 1).astype(np.float32), .7) * a
        m = np.clip(m * 1.6, 0, 1)[..., None]
        out = out * (1 - m) + np.array(col, np.float32) * m
    # vignette
    v = 1 - .45 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) ** 1.3
    out *= np.clip(v, .45, 1)[..., None]
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)), lab


def uri(img, fmt="PNG"):
    buf = io.BytesIO()
    img.save(buf, fmt)
    return f"data:image/{fmt.lower()};base64," + base64.b64encode(buf.getvalue()).decode()


def ruler(tag):
    """(name, portrait 312 x 420) of a nation's ruler: its Gazetteer page's, else the mod's own"""
    try:
        f = json.load(open(os.path.join(REPO, "source", "gazetteer", f"{tag}.json"), encoding="utf-8"))
    except FileNotFoundError:
        f = {}
    r = (f.get("people") or {}).get("ruler") or {}
    if r.get("portrait"):
        pic = r["portrait"]
        x0, y0, cw = gazetteer.portrait_box(pic)
        img = nations.portrait(os.path.join(REPO, "source", "gazetteer", pic["file"]), x0, y0, cw, size=(312, 420))
        return NAMES.get(tag, r.get("name")), Image.fromarray(img)
    if tag == "ROU":
        src, x0, y0, cw, _ = nations.PORTRAITS["ROU_roland_cahun"]
        return "Roland II Cahun", Image.fromarray(nations.portrait(os.path.join(REPO, src), x0, y0, cw, size=(312, 420)))
    raise SystemExit(f"{tag}: no ruler with a portrait")


def loc(tag):
    t = "".join(open(f, encoding="utf-8-sig").read() for f in glob.glob(os.path.join(B, "localisation", "english", "*.yml")))
    short = re.search(rf'^ {tag}:0 "([^"]*)"', t, re.M).group(1)
    formal = re.search(rf'^ {tag}_DEF:0 "([^"]*)"', t, re.M).group(1)
    return short, formal[0].upper() + formal[1:]


def flag(tag):
    im = Image.open(os.path.join(REPO, "source", "flags", f"{tag}.png")).convert("RGB")
    return im.resize((164, 104), Image.LANCZOS)


def card(tag):
    short, formal = loc(tag)
    name, face = ruler(tag)
    return f"""<div class="card"><div class="portrait"><img src="{uri(face)}"></div>
      <div class="text"><img class="flag" src="{uri(flag(tag))}"><div class="nation">{short}</div>
      <div class="ruler">{name}</div><div class="formal">{formal}</div></div></div>"""


def main():
    O, S = owners()
    tags = LEFT + RIGHT
    bg, lab = render_map(O, S, tags)
    pts = []
    for i, t in enumerate(tags):
        if t == "ROU":   # Rêverie, its capital, rather than the middle of its long land
            pts.append([(660 - X0) * SCALE, (805 - Y0) * SCALE])
        else:
            k = np.argmax(ndi.distance_transform_edt(lab == i + 2))   # the point deepest inside it
            y, x = np.unravel_index(k, lab.shape)
            pts.append([float(x), float(y)])
    # small neighbours' pins pushed apart until none touch
    for _ in range(200):
        moved = False
        for a in range(len(pts)):
            for b in range(a + 1, len(pts)):
                dx, dy = pts[b][0] - pts[a][0], pts[b][1] - pts[a][1]
                if abs(dx) < 54 and abs(dy) < 37:
                    if 54 - abs(dx) < 37 - abs(dy):
                        d = (54 - abs(dx)) / 2 * (1 if dx >= 0 else -1)
                        pts[a][0] -= d; pts[b][0] += d
                    else:
                        d = (37 - abs(dy)) / 2 * (1 if dy >= 0 else -1)
                        pts[a][1] -= d; pts[b][1] += d
                    moved = True
        if not moved:
            break
    pins = [f'<img class="pin" style="left:{x - 23:.0f}px;top:{y - 15:.0f}px" '
            f'src="{uri(flag(t).resize((46, 29), Image.LANCZOS))}">' for t, (x, y) in zip(tags, pts)]
    font = lambda d, f: "file://" + os.path.join(FONTS, d, f)  # noqa: E731
    html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family: Federo; src: url("{font('federo', 'Federo-Regular.ttf')}"); }}
@font-face {{ font-family: Josefin; src: url("{font('josefinsans', 'JosefinSans[wght].ttf')}"); font-weight: 100 700; }}
html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; background: #0b1014; }}
.bg {{ position: absolute; inset: 0; background: url("{uri(bg)}"); }}
.frame {{ position: absolute; inset: 14px; border: 2px solid rgba(201,165,90,.85); outline: 1px solid rgba(201,165,90,.35);
  outline-offset: 5px; pointer-events: none; }}
.title {{ position: absolute; left: 0; right: 0; top: 34px; text-align: center; }}
.kicker {{ font: 600 17px Josefin; letter-spacing: .55em; color: #b7a680; padding-left: .55em; }}
.name {{ font: 74px Federo; letter-spacing: .14em; padding-left: .14em; margin-top: 4px;
  background: linear-gradient(180deg, #f6e3a6 0%, #e3c77e 45%, #a8842f 100%); -webkit-background-clip: text; color: transparent;
  filter: drop-shadow(0 3px 6px rgba(0,0,0,.8)); }}
.date {{ display: inline-flex; align-items: center; gap: 18px; margin-top: 2px; font: 600 19px Josefin; letter-spacing: .4em;
  color: #f4ecd9; text-shadow: 0 2px 6px #000; padding-left: .4em; }}
.date i {{ width: 90px; height: 1px; background: linear-gradient(90deg, transparent, #c9a55a); }}
.date i:last-child {{ background: linear-gradient(90deg, #c9a55a, transparent); }}
.date b {{ width: 9px; height: 9px; background: #e3c77e; transform: rotate(45deg); }}
.col {{ position: absolute; top: 60px; bottom: 60px; width: 344px; display: flex; flex-direction: column;
  justify-content: space-between; }}
.col.left {{ left: 40px; }} .col.right {{ right: 40px; }}
.card {{ position: relative; height: 222px; display: flex; gap: 14px; padding: 12px; box-sizing: border-box;
  background: linear-gradient(180deg, rgba(23,34,42,.94), rgba(14,21,25,.94));
  clip-path: polygon(14px 0, calc(100% - 14px) 0, 100% 14px, 100% calc(100% - 14px), calc(100% - 14px) 100%, 14px 100%,
    0 calc(100% - 14px), 0 14px);
  box-shadow: inset 0 0 0 1.5px #c9a55a, inset 0 0 0 5px rgba(11,16,20,.9), inset 0 0 0 6px rgba(201,165,90,.45); }}
.portrait {{ flex: none; width: 140px; height: 190px; border-radius: 70px 70px 4px 4px; margin-top: 4px; overflow: hidden;
  box-shadow: 0 0 0 2px #e3c77e, 0 0 0 5px #11191e, 0 0 0 6px rgba(201,165,90,.6); background: #1e1e20; }}
.portrait img {{ width: 100%; height: 100%; display: block; }}
.text {{ display: flex; flex-direction: column; min-width: 0; padding-top: 2px; }}
.flag {{ width: 98px; height: 62px; display: block; box-shadow: 0 0 0 1.5px #e3c77e, 0 0 0 4px #0b1014, 0 3px 8px #000;
  margin: 4px 0 12px 3px; }}
.nation {{ font: 23px Federo; letter-spacing: .07em; text-transform: uppercase; color: #e3c77e; line-height: 1.05; }}
.ruler {{ font: 600 16px Josefin; color: #f4ecd9; margin-top: 7px; line-height: 1.2; }}
.formal {{ font: 400 13.5px Josefin; color: #b7a680; margin-top: 6px; line-height: 1.25; font-style: italic; }}
.pin {{ position: absolute; width: 46px; height: 29px; box-shadow: 0 0 0 1.5px #e3c77e, 0 0 0 3px #0b1014, 0 4px 10px rgba(0,0,0,.9); }}
.foot {{ position: absolute; left: 0; right: 0; bottom: 30px; text-align: center; font: 600 14px Josefin; letter-spacing: .5em;
  color: #b7a680; padding-left: .5em; text-shadow: 0 2px 4px #000; }}
.shade {{ position: absolute; inset: 0; pointer-events: none;
  background: radial-gradient(ellipse 560px 150px at 50% 95px, rgba(7,12,16,.82), rgba(7,12,16,.55) 55%, transparent 100%),
    linear-gradient(0deg, rgba(7,12,16,.85), transparent 90px); }}
</style></head><body><div class="bg"></div><div class="shade"></div>{''.join(pins)}
<div class="title"><div class="kicker">VALSORA</div><div class="name">THE VALE OF REIBONNE</div>
<div class="date"><i></i><b></b>1 JANUARY 2036<b></b><i></i></div></div>
<div class="col left">{''.join(card(t) for t in LEFT)}</div><div class="col right">{''.join(card(t) for t in RIGHT)}</div>
<div class="foot">THE ASSOCIATION OF REIBONNAISE STATES</div><div class="frame"></div></body></html>"""
    path = os.path.join(HERE, "page.html")
    open(path, "w", encoding="utf-8").write(html)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=os.environ.get("CHROMIUM_PATH") or None)
        pg = b.new_page(viewport={"width": W, "height": H})
        pg.goto("file://" + path)
        pg.wait_for_timeout(400)
        pg.screenshot(path=os.path.join(HERE, "vale_of_reibonne.png"))
        b.close()
    os.remove(path)
    print(os.path.join(HERE, "vale_of_reibonne.png"))


if __name__ == "__main__":
    main()
