"""Reads the game's .gui and .gfx files and lays a window out as the game would at 1920 x 1080, so each mockup in this
folder draws its pieces in the game's own boxes. A proposal's helper, not part of the Deco UI's build.

    python3 guilayout.py FILE.gui WINDOW [--depth N]     print the window's elements with their screen boxes
    python3 guilayout.py FILE.gui WINDOW --render OUT    draw it with the game's textures (for comparison only: the
                                                         picture holds the game's art, so OUT belongs in the
                                                         git-ignored deco_ui/build/next_screens/)

The game's files come from deco_ui/reference/vanilla (links to the author's copy of the game, deco_ui/CLAUDE.md
section 3). Element sizes: containers from their size (100%% and negative sizes run to the parent's edge), icons and
buttons from their sprite's frame (times scale), text boxes from maxWidth and maxHeight.
"""
import glob
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DECO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
GAME = os.environ.get("HOI4_DIR") or os.path.join(DECO, "reference", "vanilla")
IFACE = os.path.join(GAME, "interface")
SW, SH = 1920, 1080


def tokenize(s):
    s = re.sub(r"#[^\n]*", "", s)
    return re.findall(r'"[^"]*"|[{}=]|[^\s{}="]+', s)


def parse(tokens, i=0):
    out = []
    while i < len(tokens):
        tok = tokens[i]
        if tok == "}":
            return out, i + 1
        if i + 1 < len(tokens) and tokens[i + 1] == "=":
            val = tokens[i + 2] if i + 2 < len(tokens) else ""
            if val == "{":
                sub, i = parse(tokens, i + 3)
                out.append((tok, sub))
            else:
                out.append((tok, val.strip('"')))
                i += 3
        else:
            out.append((None, tok.strip('"')))
            i += 1
    return out, i


def load(path):
    t = open(path, encoding="utf-8-sig", errors="replace").read()
    consts = dict(re.findall(r"^\s*(@[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(-?[0-9.]+)", t, re.M))
    t = re.sub(r"^\s*@[A-Za-z_][A-Za-z0-9_]*\s*=\s*-?[0-9.]+", "", t, flags=re.M)
    for k in sorted(consts, key=len, reverse=True):
        t = t.replace(k, consts[k])
    return parse(tokenize(t))[0]


def attrs(body):
    return {k.lower(): v for k, v in body if k and not isinstance(v, list)}


def sub(body, key):
    for k, v in body:
        if k and k.lower() == key and isinstance(v, list):
            return v
    return None


def pair(lst):
    d = {k.lower(): v for k, v in lst if k}
    return d.get("x", d.get("width", "0")), d.get("y", d.get("height", "0"))


# ---------------------------------------------------------------- sprites
_SPR = {}


def tex_size(rel):
    p = os.path.join(GAME, rel.replace("\\", "/"))
    if not os.path.isfile(p):
        alt = p[:-4] + (".dds" if p.endswith(".tga") else ".tga")
        p = alt if os.path.isfile(alt) else p
    try:
        with open(p, "rb") as f:
            h = f.read(32)
        if h[:4] == b"DDS ":
            hh, ww = struct.unpack("<II", h[12:20])
            return ww, hh
        if p.endswith(".tga"):
            return struct.unpack("<HH", h[12:16])
        from PIL import Image
        return Image.open(p).size
    except OSError:
        return None


def sprites():
    if _SPR:
        return _SPR
    for f in glob.glob(os.path.join(IFACE, "**", "*.gfx"), recursive=True):
        try:
            data = load(f)
        except Exception:
            continue
        for k, body in data:
            if not k or k.lower() != "spritetypes" or not isinstance(body, list):
                continue
            for kind, b in body:
                if not isinstance(b, list):
                    continue
                a = attrs(b)
                if "name" not in a:
                    continue
                d = dict(kind=kind, frames=int(float(a.get("noofframes", 1) or 1)))
                d["tex"] = a.get("texturefile") or a.get("texturefile1")
                if kind and kind.lower() == "progressbartype":
                    d["tex2"] = a.get("texturefile2")
                sz = sub(b, "size")
                if sz:
                    d["size"] = tuple(int(float(v)) for v in pair(sz))
                bs = sub(b, "bordersize")
                if bs:
                    d["border"] = tuple(int(float(v)) for v in pair(bs))
                _SPR[a["name"]] = d
    return _SPR


def sprite_size(name):
    d = sprites().get(name)
    if not d:
        return None
    if d.get("size") and (d["kind"] or "").lower() in ("corneredtilespritetype", "progressbartype"):
        return d["size"]
    if not d.get("tex"):
        return d.get("size")
    s = tex_size(d["tex"])
    if not s:
        return d.get("size")
    return s[0] // max(1, d["frames"]), s[1]


# ---------------------------------------------------------------- layout
ELEMENT = {"containerwindowtype", "windowtype", "icontype", "buttontype", "guibuttontype", "instanttextboxtype",
           "textboxtype", "editboxtype", "gridboxtype", "listboxtype", "smoothlistboxtype", "scrollbartype",
           "extendedscrollbartype", "checkboxtype", "overlappingelementsboxtype", "positiontype", "dropdownboxtype",
           "browsertype"}


def _dim(v, parent, own):
    s = str(v)
    if "%" in s:
        return max(0, parent * float(s.replace("%", "")) / 100 - own)
    f = float(s or 0)
    return parent + f - own if f < 0 else f


def _anchor(ori, x, y, w, h):
    o = (ori or "UPPER_LEFT").upper().replace('"', "")
    ax = x + (w if "RIGHT" in o else 0 if "LEFT" in o else w / 2 if "CENTER" in o else 0)
    ay = y + (h if "LOWER" in o or "DOWN" in o else 0 if "UPPER" in o or o.endswith("_UP") else h / 2 if "CENTER" in o else 0)
    return ax, ay


def _origo(ori, w, h):
    o = (ori or "UPPER_LEFT").upper().replace('"', "")
    dx = w if "RIGHT" in o else 0 if "LEFT" in o else w / 2 if "CENTER" in o else 0
    dy = h if "LOWER" in o or "DOWN" in o else 0 if "UPPER" in o or o.endswith("_UP") else h / 2 if "CENTER" in o else 0
    return dx, dy


class El:
    def __init__(self, kind, body, x, y, w, h, depth, path):
        self.kind, self.body, self.x, self.y, self.w, self.h, self.depth, self.path = kind, body, x, y, w, h, depth, path
        self.a = attrs(body)
        self.name = self.a.get("name", "")
        self.children = []

    @property
    def sprite(self):
        a = self.a
        s = a.get("spritetype") or a.get("quadtexturesprite")
        if not s:
            bg = sub(self.body, "background")
            if bg:
                ba = attrs(bg)
                s = ba.get("quadtexturesprite") or ba.get("spritetype")
        return s

    def box(self):
        return (round(self.x), round(self.y), round(self.w), round(self.h))

    def find(self, name):
        if self.name == name:
            return self
        for c in self.children:
            r = c.find(name)
            if r:
                return r
        return None

    def walk(self):
        yield self
        for c in self.children:
            yield from c.walk()


def lay(kind, body, px, py, pw, ph, depth=0, path=""):
    a = attrs(body)
    k = kind.lower()
    pos = sub(body, "position")
    x, y = (float(v or 0) for v in pair(pos)) if pos else (0.0, 0.0)
    w = h = 0.0
    scale = float(a.get("scale", 1) or 1)
    sz = sub(body, "size")
    if sz and k not in ("icontype",):
        sw_, sh_ = pair(sz)
        w, h = _dim(sw_, pw, x), _dim(sh_, ph, y)
    spr = a.get("spritetype") or a.get("quadtexturesprite")
    if k in ("icontype", "buttontype", "guibuttontype", "checkboxtype") and spr and not (sz and w and h):
        s = sprite_size(spr)
        if s:
            w, h = s[0] * scale, s[1] * scale
    if k in ("instanttextboxtype", "textboxtype", "editboxtype"):
        w = float(a.get("maxwidth", w) or w)
        h = float(a.get("maxheight", h) or h)
    if k == "gridboxtype" and not w:
        ss, ms = sub(body, "slotsize"), sub(body, "max_slots")
        if ss and ms:
            sx, sy = (float(v) for v in pair(ss))
            mx, my = (float(v) for v in pair(ms))
            w, h = sx * mx, sy * my
    ax, ay = _anchor(a.get("orientation"), px, py, pw, ph)
    ox, oy = _origo(a.get("origo"), w, h)
    if str(a.get("centerposition", "")).lower() == "yes":
        ox, oy = ox + w / 2, oy + h / 2
    el = El(k, body, ax + x - ox, ay + y - oy, w, h, depth, path + ">" + a.get("name", "?"))
    for ck, cb in body:
        if ck and isinstance(cb, list) and ck.lower() in ELEMENT:
            el.children.append(lay(ck, cb, el.x, el.y, el.w, el.h, depth + 1, el.path))
    return el


def find_window(gui, name):
    """the top-level (or nested) element of that name in a .gui file, as a (kind, body) pair"""
    def rec(items):
        for k, b in items:
            if not isinstance(b, list):
                continue
            if k and k.lower() in ELEMENT and attrs(b).get("name") == name:
                return k, b
            r = rec(b)
            if r:
                return r
        return None
    p = gui if os.path.isabs(gui) else os.path.join(IFACE, gui)
    r = rec(load(p))
    if not r:
        raise KeyError(f"{name} not in {gui}")
    return r


def window(gui, name, parent=(0, 0, SW, SH)):
    k, b = find_window(gui, name)
    return lay(k, b, *parent)


def dump(el, depth=99, file=sys.stdout):
    for e in el.walk():
        if e.depth - el.depth > depth:
            continue
        a = e.a
        extra = []
        if e.sprite:
            d = sprites().get(e.sprite)
            extra.append(f"spr={e.sprite}" + (f"[{d['frames']}f {d.get('tex')}]" if d else "[?]"))
        for key in ("text", "buttontext", "font", "buttonfont", "format", "orientation", "origo", "scale"):
            if key in a:
                extra.append(f"{key}={a[key]}")
        if e.kind == "gridboxtype":
            for key in ("slotsize", "max_slots"):
                s = sub(e.body, key)
                if s:
                    extra.append(f"{key}={pair(s)}")
        x, y, w, h = e.box()
        print(f"{'  ' * (e.depth - el.depth)}{e.kind[:-4] if e.kind.endswith('type') else e.kind} {e.name} "
              f"@({x},{y}) {w}x{h}  " + " ".join(extra), file=file)


# ---------------------------------------------------------------- the game's look (comparison only)
def _img(rel):
    from PIL import Image
    p = os.path.join(GAME, rel.replace("\\", "/"))
    if not os.path.isfile(p):
        alt = p[:-4] + (".dds" if p.endswith(".tga") else ".tga")
        p = alt if os.path.isfile(alt) else p
    return Image.open(p).convert("RGBA")


def nine(img, w, h, bx, by):
    from PIL import Image
    w, h = max(1, int(w)), max(1, int(h))
    out = Image.new("RGBA", (w, h))
    W, H = img.size
    bx, by = min(bx, W // 2, w // 2), min(by, H // 2, h // 2)
    xs = [(0, bx, 0, bx), (bx, W - bx, bx, w - bx), (W - bx, W, w - bx, w)]
    ys = [(0, by, 0, by), (by, H - by, by, h - by), (H - by, H, h - by, h)]
    for sx0, sx1, dx0, dx1 in xs:
        for sy0, sy1, dy0, dy1 in ys:
            if sx1 > sx0 and sy1 > sy0 and dx1 > dx0 and dy1 > dy0:
                out.paste(img.crop((sx0, sy0, sx1, sy1)).resize((dx1 - dx0, dy1 - dy0)), (dx0, dy0))
    return out


def render(el, canvas, frame=None):
    """paste the game's own pictures of every element into canvas (a PIL RGBA image of the screen)"""
    frame = frame or {}
    for e in el.walk():
        s = e.sprite
        d = sprites().get(s) if s else None
        if not d or not d.get("tex"):
            continue
        try:
            img = _img(d["tex"])
        except Exception:
            continue
        kind = (d["kind"] or "").lower()
        if kind == "corneredtilespritetype":
            bx, by = d.get("border", (8, 8))
            img = nine(img, e.w or img.width, e.h or img.height, bx, by)
        else:
            fw = img.width // max(1, d["frames"])
            f = frame.get(e.name, 0)
            img = img.crop((f * fw, 0, (f + 1) * fw, img.height))
            if e.w and e.h and (abs(e.w - img.width) > 1 or abs(e.h - img.height) > 1):
                img = img.resize((max(1, int(e.w)), max(1, int(e.h))))
        put(canvas, img, int(e.x), int(e.y))
    return canvas


def put(canvas, img, x, y):
    """alpha-composite img at (x, y), cropped to the canvas"""
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(canvas.width, x + img.width), min(canvas.height, y + img.height)
    if x1 > x0 and y1 > y0:
        canvas.alpha_composite(img.crop((x0 - x, y0 - y, x1 - x, y1 - y)), (x0, y0))


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("gui")
    ap.add_argument("window")
    ap.add_argument("--depth", type=int, default=99)
    ap.add_argument("--render")
    ap.add_argument("--parent", help="x,y,w,h of the parent box")
    o = ap.parse_args()
    par = tuple(int(v) for v in o.parent.split(",")) if o.parent else (0, 0, SW, SH)
    w = window(o.gui, o.window, par)
    dump(w, o.depth)
    if o.render:
        from PIL import Image
        cv = Image.new("RGBA", (SW, SH), (40, 46, 50, 255))
        render(w, cv).save(o.render)
