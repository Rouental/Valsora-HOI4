"""Previews of the side panels (make_panels.py), drawn from the generated .gui files with the game's own art.

Unlike preview_screens.py, which draws vanilla art the mod leaves alone as stand-ins, this reads the game's
sprite definitions and textures (reference/vanilla: HOI4_DIR), so each panel is drawn with its real buttons,
frames and pictures; the mod's replaced textures win, as in game. Text in the game's fonts is drawn with a
stand-in typeface (the game's font textures are not in the reference copy); the mod's fonts are its own.
Lists the game fills in (grids, list boxes) are drawn as faint outlines.

    python preview_panels.py [panel ...]     -> build/preview_panel_<name>.png (and _vanilla.png: the game's)

Every panel is drawn shown (at its show_position), over the top bar preview, so the notch shows the medallion.
"""
import glob
import os
import re
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import validate_preview as V
import layout_panels as LPN
from paths import ART, BUILD, FONTS_SRC, MOD as M, VALSORA, VANILLA

# ---------------------------------------------------------------- sprites: the game's, then the mod's
SPRITE_KINDS = ("spritetype", "frameanimatedspritetype", "corneredtilespritetype", "textspritetype",
                "progressbartype", "maskedshieldtype", "buttontype")


def _norm(p):
    return re.sub(r"/+", "/", p.replace("\\", "/")) if p else p


def _read_gfx(path, out):
    for k, body in V.load(path):
        if not k or k.lower() != "spritetypes":
            continue
        for kind, b in body:
            if not kind or kind.lower() not in SPRITE_KINDS or not isinstance(b, list):
                continue
            a = V.attrs(b)
            if "name" not in a:
                continue
            d = dict(kind=kind.lower(), frames=int(a.get("noofframes", 1) or 1),
                     tex=_norm(a.get("texturefile") or a.get("texturefile1") or a.get("texturefile2")))
            sz = V.sub(b, "size")
            if sz:
                try:
                    d["size"] = tuple(int(v) for v in V.xy(sz))
                except (TypeError, ValueError):
                    pass
            bs = V.sub(b, "bordersize")
            if bs:
                d["border"] = tuple(int(v) for v in V.xy(bs))
            out[a["name"]] = d


VAN_SPRITES, MOD_SPRITES = {}, {}
for _f in sorted(glob.glob(VANILLA + "interface/**/*.gfx", recursive=True)):
    try:
        _read_gfx(_f, VAN_SPRITES)
    except Exception:  # noqa: BLE001  (a few vanilla files have stray tokens; their sprites are not needed)
        pass
for _f in sorted(glob.glob(M + "interface/**/*.gfx", recursive=True)):
    _read_gfx(_f, MOD_SPRITES)

_TEX = {}


def texture(rel, vanilla_only=False):
    """The texture the game would load: the mod's file first (unless vanilla_only), a .dds before a .tga."""
    rel = _norm(rel)
    key = (rel, vanilla_only)
    if key in _TEX:
        return _TEX[key]
    cands = [rel]
    if rel.lower().endswith(".tga"):
        cands.insert(0, rel[:-4] + ".dds")
    img = None
    roots = [VANILLA] if vanilla_only else [M, VALSORA, VANILLA]
    for c in cands:
        for root in roots:
            p = root + c
            if os.path.isfile(p):
                try:
                    img = Image.open(p).convert("RGBA")
                except Exception:  # noqa: BLE001
                    from ddsutil import read_dds
                    img = read_dds(p)
                break
        if img is not None:
            break
    _TEX[key] = img
    return img


def sprite(name, vanilla_only=False):
    """(definition, image) of a sprite, or (None, None)."""
    d = (None if vanilla_only else MOD_SPRITES.get(name)) or VAN_SPRITES.get(name)
    if not d and not vanilla_only and name in V.REPLACED:
        rel, fr, kind = V.REPLACED[name]
        d = dict(kind=kind.lower(), frames=fr, tex=rel)
    if not d or not d.get("tex"):
        return None, None
    return d, texture(d["tex"], vanilla_only)


def frame_of(img, d, frame=0):
    n = max(1, d.get("frames", 1))
    fw = img.width // n
    f = min(max(frame, 0), n - 1)
    return img.crop((f * fw, 0, (f + 1) * fw, img.height))


# ---------------------------------------------------------------- text
LOC = {}
for _f in glob.glob(VANILLA + "localisation/english/**/*.yml", recursive=True):
    try:
        for m in re.finditer(r'^\s*([\w.\-]+):\d*\s*"(.*)"\s*$', open(_f, encoding="utf-8-sig", errors="ignore").read(), re.M):
            LOC.setdefault(m.group(1), m.group(2))
    except OSError:
        pass
for _f in glob.glob(M + "localisation/english/*.yml"):
    LOC.update(re.findall(r'^\s*([\w.\-]+):\d*\s*"(.*)"\s*$', open(_f, encoding="utf-8-sig").read(), re.M))
_TTF = {}


def ttf(px):
    if px not in _TTF:
        path = next(iter(glob.glob(FONTS_SRC + "**/JosefinSans*Regular*.ttf", recursive=True)
                         + glob.glob(FONTS_SRC + "**/*.ttf", recursive=True)))
        _TTF[px] = ImageFont.truetype(path, px)
    return _TTF[px]


def vanilla_font_px(font):
    m = re.search(r"(\d+)", font or "")
    n = int(m.group(1)) if m else 14
    return max(9, round(n * (0.6 if "header" in (font or "") else 0.85)))


def clean_loc(s):
    s = re.sub(r"§.", "", s or "")
    s = re.sub(r"\$[^$]*\$|\[[^\]]*\]|£\w+", "", s)
    return s.replace("\\n", " ").replace("\n", " ").strip()


def draw_ttf(cv, text, x, y, w, h, fmt, font):
    px = vanilla_font_px(font)
    im = Image.new("RGBA", (max(1, w or 400), max(1, h or px + 6)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    tw = d.textlength(text, font=ttf(px))
    tx = (im.width - tw) / 2 if fmt in ("center", "centre") else (im.width - tw if fmt == "right" else 0)
    d.text((tx, 0), text, font=ttf(px), fill=(226, 220, 204, 255))
    V.paste(cv, im, x, y)


# ---------------------------------------------------------------- layout
def num(v, ref, pos=0, vars_=None):
    """A size value: n, -n (to the parent's edge minus n), 100%% (to the parent's edge), p% of the parent."""
    s = str(v).strip('"')
    if vars_ and s.startswith("@"):
        s = vars_.get(s, "0")
    if s.endswith("%"):
        p = float(s.rstrip("%"))
        return (ref - pos) if p >= 100 else ref * p / 100
    try:
        f = float(s)
    except ValueError:
        return 0
    return (ref - pos + f) if f < 0 else f


def anchor(ori, x, y, px, py, pw, ph):
    o = (ori or "UPPER_LEFT").upper().strip('"')
    ax = {"UPPER_RIGHT": px + pw, "LOWER_RIGHT": px + pw, "CENTER_RIGHT": px + pw,
          "CENTER": px + pw / 2, "CENTER_UP": px + pw / 2, "CENTER_DOWN": px + pw / 2}.get(o, px) + x
    ay = {"LOWER_LEFT": py + ph, "LOWER_RIGHT": py + ph, "CENTER_DOWN": py + ph,
          "CENTER": py + ph / 2, "CENTER_LEFT": py + ph / 2, "CENTER_RIGHT": py + ph / 2}.get(o, py) + y
    return ax, ay


ELEMENTS = ("containerwindowtype", "icontype", "buttontype", "instanttextboxtype", "textboxtype", "gridboxtype",
            "listboxtype", "smoothlistboxtype", "overlappingelementsboxtype", "checkboxtype", "editboxtype")


class Panel:
    def __init__(self, hide=(), samples=None, vanilla_only=False, vars_=None, outline_lists=True, frames=None):
        self.frames = frames or {}           # element name -> frame index (what the game sets at runtime)
        self.hide = set(hide)
        self.samples = samples or {}
        self.vanilla_only = vanilla_only
        self.vars = vars_ or {}
        self.outline_lists = outline_lists
        self.boxes = []

    def draw(self, cv, elems, px, py, pw, ph):
        for key, body in elems:
            kl = key.lower() if key else ""
            if kl not in ELEMENTS or not isinstance(body, list):
                continue
            d = V.attrs(body)
            name = d.get("name", "")
            if name in self.hide or d.get("hide") == "yes":
                continue
            pos = V.sub(body, "position")
            x, y = (self.posval(v) for v in V.xy(pos)) if pos else (0, 0)
            ax, ay = anchor(d.get("orientation"), x, y, px, py, pw, ph)
            sz = V.sub(body, "size")
            if sz:
                w, h = V.xy(sz)
                w = num(w, pw, ax - px, self.vars) if w is not None else 0
                h = num(h, ph, ay - py, self.vars) if h is not None else 0
            else:
                w, h = num(d.get("maxwidth", 0), pw, 0, self.vars), num(d.get("maxheight", 0), ph, 0, self.vars)
            if kl == "containerwindowtype":
                drew = None
                for bk, bg in body:
                    if bk != "background" or not isinstance(bg, list):
                        continue
                    a = V.attrs(bg)
                    drew = self.picture(cv, a.get("quadtexturesprite") or a.get("spritetype"), ax, ay, w, h, 0, 1) or drew
                self.boxes.append((name, ax, ay, w, h, bool(drew)))
                self.draw(cv, body, ax, ay, w, h)
            elif kl in ("icontype", "buttontype", "checkboxtype"):
                spr = d.get("quadtexturesprite") or d.get("spritetype")
                fr = self.frames.get(name, int(float(d.get("frame", 1) or 1)) - 1)
                sc = float(d.get("scale", 1) or 1)
                img_w = self.picture(cv, spr, ax, ay, w, h, fr, sc, centre=d.get("centerposition") == "yes")
                bt = d.get("buttontext") or d.get("text")
                if kl == "buttontype" and bt and img_w:
                    self.text(cv, bt, d.get("buttonfont") or d.get("font"), ax, ay + (img_w[1] - 16) / 2,
                              img_w[0], 18, "center", name)
                self.boxes.append((name, ax, ay, *(img_w or (0, 0)), bool(img_w)))
            elif kl in ("instanttextboxtype", "textboxtype", "editboxtype"):
                txt = self.samples.get(name)
                if txt is None:
                    txt = LOC.get(str(d.get("text", "")).strip('"'), "")
                if txt:
                    self.text(cv, txt, d.get("font"), ax, ay, int(w) or None, int(h) or None,
                              d.get("format", "left").lower(), name, d.get("vertical_alignment") == "center")
                self.boxes.append((name, ax, ay, w or 60, h or 16, bool(txt)))
            elif self.outline_lists and w > 0 and h > 0:
                self.boxes.append((name, ax, ay, w, h, True))
                im = Image.new("RGBA", (int(min(w, 1920)), int(min(h, 1080))), (0, 0, 0, 0))
                ImageDraw.Draw(im).rectangle((0, 0, im.width - 1, im.height - 1), outline=(120, 200, 190, 90))
                V.paste(cv, im, ax, ay)

    def posval(self, v):
        s = str(v if v is not None else 0).strip('"')
        s = self.vars.get(s, s) if s.startswith("@") else s
        try:
            return float(s.rstrip("%"))
        except ValueError:
            return 0.0

    def picture(self, cv, spr, ax, ay, w, h, frame, scale, centre=False):
        if not spr:
            return None
        d, img = sprite(spr, self.vanilla_only)
        if img is None:
            return None
        if d["kind"] == "corneredtilespritetype":
            if w <= 0 or h <= 0:
                return None
            tw, th = d.get("size", img.size)
            if (tw, th) != img.size:
                img = img.resize((tw, th), Image.LANCZOS)
            bx, by = d.get("border", (0, 0))
            bx, by = min(bx, img.width // 2), min(by, img.height // 2)
            V.paste(cv, V.cornered(img, int(w), int(h), bx, by), ax, ay)
            return int(w), int(h)
        if d["kind"] == "progressbartype":
            return None
        im = frame_of(img, d, frame)
        if scale != 1:
            im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.LANCZOS)
        if centre:
            ax, ay = ax - im.width / 2, ay - im.height / 2
        V.paste(cv, im, ax, ay)
        return im.width, im.height

    def text(self, cv, text, font, x, y, w, h, fmt, name, valign=False):
        font = (font or "").strip('"')
        text = LOC.get(str(text).strip('"'), str(text).strip('"'))
        # the game's variables as a sample number, its \\n as a line break
        text = re.sub(r"\$[^$\s]*\$", "12", text).replace("\\n", "\n")
        # the game's look: its own fonts (whose textures the repository doesn't have) approximated, unchecked
        if font in V.FONTS and not (self.vanilla_only and font in V.GAME_W):
            V.draw_text(cv, font, text, x, y, w, fmt, max_h=h, valign=valign, check=name)
        else:
            s = clean_loc(text)
            if s:
                draw_ttf(cv, s, x, y, w, h, fmt, font)


# ---------------------------------------------------------------- screens
def find_window(elems, name):
    for k, b in elems:
        if isinstance(b, list):
            if k and k.lower() == "containerwindowtype" and V.attrs(b).get("name") == name:
                return b
            r = find_window(b, name)
            if r is not None:
                return r
    return None


def gui_vars(path):
    return dict(re.findall(r"^\s*(@\w+)\s*=\s*(-?[\d.]+)", open(path, encoding="utf-8-sig", errors="ignore").read(), re.M))


def backdrop(with_topbar):
    full = Image.open(ART + "map_rouental.jpg").convert("RGB").resize((1920, 1080), Image.LANCZOS)
    cv = np.array(full, np.float32) / 255
    if with_topbar:
        top = V.gui[0][1]
        tb = next(b for k, b in top if k == "containerWindowType" and V.attrs(b).get("name") == "topbar")
        V.render(cv, [("containerWindowType", tb)], 0, 0, 1920)
        V.render(cv, [(k, b) for k, b in V.extras[0][1]
                      if V.attrs(b).get("name") != "valsora_deco_country_name_small_window"], -4, -1, 1920)
    return cv


def render_panel(spec, vanilla=False, cv=None):
    path = (VANILLA if vanilla else M) + "interface/" + spec["file"]
    elems = V.load(path)
    win = find_window(elems, spec["window"])
    assert win is not None, (path, spec["window"])
    sx, sy = (int(float(v)) for v in V.xy(V.sub(win, "show_position")))
    w, _ = V.xy(V.sub(win, "size"))
    W = int(float(w))
    cv = backdrop(not vanilla) if cv is None else cv
    p = Panel(hide=spec.get("preview_hide", ()), samples=spec.get("samples"), vanilla_only=vanilla, vars_=gui_vars(path))
    # the window itself, then its children (as the game draws them: background, then children in order)
    p.draw(cv, [("containerWindowType", [(k, v) for k, v in win if not (k and k.lower() == "position")]
                 + [("position", [("x", str(sx)), ("y", str(sy))])])], 0, 0, 1920, 1080)
    return cv, (sx, sy, W), p


def save(cv, name, x1):
    out = Image.fromarray((np.clip(cv, 0, 1) * 255).astype(np.uint8))
    out.crop((0, 0, min(1920, x1), 1080)).save(BUILD + name)


# ---------------------------------------------------------------- the lower right corner: map modes and minimap
CORNER_HIDE = {"tutorial_highlight_default_mapmode", "logistics_tutorial_glow_1", "logistics_tutorial_glow_2",
               "handle_pinged", "circle", "minimap_offensive_icon", "minimap_defensive_icon"}


def corner_files(vanilla=False):
    """(path, window) of the map modes and the minimap: the mod's files when it ships them (the minimap's is the
    Valsora mod's own), else the game's"""
    out = []
    for f, win in (("mapmodes_interface.gui", "MapmodesInterface_Ingame"), ("minimap.gui", "mini_map_interface")):
        roots = [VANILLA] if vanilla else [M, VALSORA, VANILLA]
        path = next(r + "interface/" + f for r in roots if os.path.isfile(r + "interface/" + f))
        out.append((path, win))
    return out


def render_corner(vanilla=False, selected=(1, 5)):
    """the lower right corner; `selected` names the map mode buttons drawn selected (big 1, small 5)"""
    cv = backdrop(False)
    for path, win in corner_files(vanilla):
        w = find_window(V.load(path), win)
        hide = set(CORNER_HIDE)
        # the game shows either a button or its selected twin: hide the twin of every unselected button
        for i in range(1, 23):
            hide.add(f"mapmode_button_{i}" if i in selected else f"mapmode_button_{i}_s")
            if i not in selected:
                hide.add(f"mapmode_button_{i}_s_bg")
        hide.add("4_button_mapmode")         # the game shows the 3- or the 4-button column
        hide |= {"mapmode_button_4", "mapmode_button_4_s", "mapmode_button_4_bg", "mapmode_button_4_s_bg"}
        # what the game sets per button: land, air, naval; then a few of the small map modes
        frames = {f"mapmode_button_{i}{s}": i - 1 for i in (1, 2, 3) for s in ("", "_s")}
        frames.update({f"mapmode_button_{i}{s}": f for i, f in zip(range(5, 12), (3, 4, 6, 8, 9, 10, 11)) for s in ("", "_s")})
        p = Panel(hide=hide, vanilla_only=vanilla, vars_=gui_vars(path), outline_lists=False, frames=frames)
        p.draw(cv, [("containerWindowType", w)], 0, 0, 1920, 1080)
    return cv


def preview_corner():
    for van, name in ((False, "preview_corner.png"), (True, "preview_corner_vanilla.png")):
        cv = render_corner(vanilla=van)
        out = Image.fromarray((np.clip(cv, 0, 1) * 255).astype(np.uint8)).crop((1520, 780, 1920, 1080))
        out.resize((out.width * 2, out.height * 2), Image.NEAREST).save(BUILD + name)


def preview_panel(key):
    """one panel, the mod's and the game's; returns the problems found while drawing it"""
    n = len(V.problems)
    spec = LPN.PANELS[key]
    cv, (sx, sy, W), p = render_panel(spec)
    save(cv, f"preview_panel_{key}.png", sx + W + max(40, spec.get("extra_w", 0)) + 40)
    if os.path.isfile(VANILLA + "interface/" + spec["file"]):
        cvv, (vx, vy, VW), _ = render_panel(spec, vanilla=True)
        save(cvv, f"preview_panel_{key}_vanilla.png", vx + VW + max(40, spec.get("extra_w", 0)) + 40)
    return V.problems[n:]


def _job(key):
    if key == "corner":
        preview_corner()
        return []
    return preview_panel(key)


if __name__ == "__main__":
    only = set(sys.argv[1:]) - {"corner"}
    keys = [k for k in LPN.PANELS if not only or k in only]
    if not only or "corner" in sys.argv[1:]:
        keys.append("corner")
    # each panel on its own core (2026-10-15: 41 s one after another, 13 s on four); the loaded sprites, fonts and
    # localisation are shared by forking, so the pictures are the same as drawn one by one
    import multiprocessing as mp
    try:
        ctx = mp.get_context("fork")
    except ValueError:   # no fork (Windows): one by one
        ctx = None
    if ctx and len(keys) > 1:
        with ctx.Pool(min(len(keys), os.cpu_count() or 1)) as pool:
            found = pool.map(_job, keys, chunksize=1)
    else:
        found = [_job(k) for k in keys]
    for key, probs in zip(keys, found):
        V.problems.extend(probs)
        if key != "corner":
            print("panel preview:", key)
    print("panel previews written; problems:", [q for q in V.problems if "overflow" in q or "lines" in q])
    if "corner" in keys:
        print("corner preview written (map modes and minimap, 2x)")
