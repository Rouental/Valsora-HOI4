"""Sheets of every picture the Deco UI replaces: the game's beside ours, screen by screen (2026-10-17).

    python3 tools/changes_sheets.py            -> build/changes/<group>_<n>.png, build/changes/icons_<n>.png,
                                                  build/changes/index.json

For the author to review what the Deco UI has changed (the author: "Last night I noticed you replaced some icons
that I didn't want you to yet, so I'll have to go through and see all that you did"). Each tile is one file at the
game's path: its name, the date it was first added, the game's picture on the left and ours on the right, on a grey
check so see-through parts show. The icons sheets hold every replaced picture no bigger than 64 px a frame. The sheets
show the game's own art, so they stay in the git-ignored build/ (never commit them).
Needs the game's gfx (paths.VANILLA, section 3 of CLAUDE.md).
"""
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFont

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import paths  # noqa: E402

ROOT = os.path.dirname(HERE)
MOD = os.path.join(ROOT, "valsora_deco_ui")
GAME_GFX = os.path.join(paths.VANILLA, "gfx")
OUT = os.path.join(ROOT, "build", "changes")
FONTS = os.path.join(ROOT, "source_fonts")

# manifest key prefix -> (what it is, the version that added it)
GROUPS = {
    "tb": ("Top bar", "v0.1-v0.4"), "pol": ("Politics screen", "v0.4"), "sv": ("State panel", "v0.4"),
    "menu": ("Main menu", "v0.3"), "dec": ("Decisions seal glows", "v0.4"), "tooltip": ("Tooltip", "v0.4.8"),
    "sort": ("Sort button", "v0.5"), "btn": ("Standard buttons", "v0.1-v0.5"), "win": ("Window tiles", "v0.1-v0.10"),
    "shared": ("Shared pieces: tabs, sort buttons, close, checkboxes", "v0.5"), "mm": ("Map modes", "v0.5"),
    "mn": ("Minimap handle, pings", "v0.5"), "mini": ("Minimap", "v0.5"), "nf": ("Focus tree", "v0.6"),
    "lg": ("Army bar", "v0.7"), "ev": ("Events and news", "v0.7-v0.8.3"), "dsg": ("Designers", "v0.9"),
    "ldr": ("Commander and advisor pickers", "v0.9"), "ld": ("Loading bar and tip", "v0.10"),
    "sc": ("Scroll bars and sliders", "v0.10"), "mv": ("Selected armies, fleets, air wings, operatives", "v0.10"),
    "bp": ("Battle plan toolbar", "v0.10"), "cb": ("Land and naval battles", "v0.10"),
    "dp": ("Diplomatic action windows", "v0.10"), "gs": ("Game setup", "v0.10"), "wf": ("Window frames", "v0.10"),
    "pp": ("Popups and one-picture windows", "v0.10"),
}
ICON_MAX = 64          # a frame no bigger than this each way counts as an icon
TILE_W, TILE_H = 392, 196
COLS, ROWS = 4, 4


@lru_cache(maxsize=None)
def font(size, bold=False):
    name = "JosefinSans-Bold.ttf" if bold else "JosefinSans-Regular.ttf"
    for dp, _, fs in os.walk(FONTS):
        for f in fs:
            if f == name or (f.startswith("JosefinSans[") and f.endswith(".ttf")):
                try:
                    return ImageFont.truetype(os.path.join(dp, f), size)
                except OSError:
                    pass
    return ImageFont.load_default()


def game_frames():
    """texture path (lower case, gfx/...) -> noOfFrames, from the game's .gfx files"""
    frames = {}
    for base in (os.path.join(paths.VANILLA, "interface"),):
        for dp, _, fs in os.walk(base):
            for f in fs:
                if not f.endswith(".gfx"):
                    continue
                t = open(os.path.join(dp, f), encoding="utf-8-sig", errors="replace").read()
                for blk in re.finditer(r"\{([^{}]*)\}", t):
                    b = blk.group(1)
                    tex = re.search(r'texturefile\s*=\s*"([^"]+)"', b, re.I)
                    if not tex:
                        continue
                    n = re.search(r"noOfFrames\s*=\s*(\d+)", b, re.I)
                    key = re.sub(r"[\\/]+", "/", tex.group(1)).lower()
                    frames[key.rsplit(".", 1)[0]] = int(n.group(1)) if n else 1
    return frames


def sprite_table(base):
    """sprite name (lower case) -> (texture path, frames), from every .gfx under base"""
    out = {}
    for dp, _, fs in os.walk(base):
        for f in fs:
            if not f.endswith(".gfx"):
                continue
            t = open(os.path.join(dp, f), encoding="utf-8-sig", errors="replace").read()
            t = re.sub(r"\b(size|bordersize)\s*=\s*\{[^{}]*\}", "", t, flags=re.I)
            for blk in re.finditer(r"\{([^{}]*)\}", t):
                b = blk.group(1)
                nm = re.search(r'\bname\s*=\s*"([^"]+)"', b, re.I)
                tex = re.search(r'texturefile\s*=\s*"([^"]+)"', b, re.I)
                if nm and tex:
                    n = re.search(r"noOfFrames\s*=\s*(\d+)", b, re.I)
                    out[nm.group(1).lower()] = (re.sub(r"[\\/]+", "/", tex.group(1)), int(n.group(1)) if n else 1)
    return out


def gui_sprites(path):
    """element 'parent>name' -> the sprite it shows, from a .gui (a block's own lines, children left out)"""
    t = re.sub(r"#[^\n]*", "", open(path, encoding="utf-8-sig", errors="replace").read())
    out, stack = {}, [[]]
    for tok in re.split(r"([{}])", t):
        if tok == "{":
            stack.append([])
        elif tok == "}":
            if len(stack) < 2:
                continue
            own = "".join(stack.pop())
            nm = re.search(r'\bname\s*=\s*"?([^"\s}]+)"?', own, re.I)
            sp = re.search(r'\b(?:spriteType|quadTextureSprite)\s*=\s*"?([^"\s}]+)"?', own, re.I)
            if nm and sp:
                parent = re.search(r'\bname\s*=\s*"?([^"\s}]+)"?', "".join(stack[-1]), re.I)
                out[f"{parent.group(1) if parent else ''}>{nm.group(1)}"] = sp.group(1)
        else:
            stack[-1].append(tok)
    return out


def swaps(added):
    """the game's pictures a screen now shows one of ours instead of: its .gui points the element at a new sprite"""
    game_s = sprite_table(os.path.join(paths.VANILLA, "interface"))
    ours_s = {**game_s, **sprite_table(os.path.join(MOD, "interface"))}
    seen, out = set(), []
    for dp, _, fs in os.walk(os.path.join(MOD, "interface")):
        for f in fs:
            if not f.endswith(".gui"):
                continue
            rel = os.path.relpath(os.path.join(dp, f), MOD).replace("\\", "/")
            game_gui = os.path.join(paths.VANILLA, rel)
            if not os.path.isfile(game_gui):
                continue
            g, o = gui_sprites(game_gui), gui_sprites(os.path.join(dp, f))
            for key, gs in g.items():
                os_ = o.get(key)
                if not os_ or os_.lower() == gs.lower() or (gs.lower(), os_.lower()) in seen:
                    continue
                seen.add((gs.lower(), os_.lower()))
                gt, ot = game_s.get(gs.lower()), ours_s.get(os_.lower())
                game_img = os.path.join(paths.VANILLA, gt[0]) if gt else None
                ours_img = None
                if ot:
                    p = os.path.join(MOD, ot[0])
                    ours_img = p if os.path.isfile(p) else os.path.join(paths.VANILLA, ot[0])
                hidden = os_.lower() in ("gfx_valsora_deco_none", "gfx_valsora_deco_clear")
                out.append(dict(path=f"{f}: {key.split('>')[-1]}", gui=f, group="swap",
                                added=added.get(ot[0], "2026-10-14") if ot else "?",
                                size=("hidden" if hidden else f"{gs} -> {os_}"), icon=False,
                                game=game_img, ours=ours_img, element=key, game_sprite=gs, our_sprite=os_))
    return out


def first_added():
    """file (relative to the mod) -> the date it was first committed"""
    log = subprocess.run(["git", "log", "--diff-filter=A", "--name-only", "--format=@@%cs", "--",
                          "valsora_deco_ui/gfx"], cwd=ROOT, capture_output=True, text=True).stdout
    out, cur = {}, None
    for ln in log.splitlines():
        if ln.startswith("@@"):
            cur = ln[2:]
        elif ln.strip():
            out[ln.strip().split("valsora_deco_ui/", 1)[1]] = cur
    return out


def load(path):
    try:
        return Image.open(path).convert("RGBA")
    except Exception:
        return None


def checker(w, h, s=8):
    im = Image.new("RGBA", (w, h), (92, 92, 96, 255))
    d = ImageDraw.Draw(im)
    for y in range(0, h, s):
        for x in range((y // s) % 2 * s, w, 2 * s):
            d.rectangle([x, y, x + s - 1, y + s - 1], fill=(112, 112, 116, 255))
    return im


def fit(img, w, h):
    """scale into w x h: small pictures up by whole steps (crisp), big ones down"""
    iw, ih = img.size
    if iw <= w // 2 and ih <= h // 2:
        k = max(1, min(w // iw, h // ih, 4))
        return img.resize((iw * k, ih * k), Image.NEAREST)
    k = min(w / iw, h / ih, 1.0)
    return img.resize((max(1, round(iw * k)), max(1, round(ih * k))), Image.LANCZOS)


def tile(name, date, game, ours, size_txt):
    t = Image.new("RGBA", (TILE_W, TILE_H), (20, 27, 32, 255))
    d = ImageDraw.Draw(t)
    d.rectangle([0, 0, TILE_W - 1, TILE_H - 1], outline=(110, 90, 50, 255))
    short = name if len(name) <= 46 else "..." + name[-43:]
    d.text((8, 6), short, font=font(13, True), fill=(236, 222, 186, 255))
    d.text((8, 24), f"added {date}  ·  {size_txt}", font=font(12), fill=(170, 156, 120, 255))
    cw, ch = (TILE_W - 24) // 2, TILE_H - 66
    for i, (img, label) in enumerate(((game, "GAME"), (ours, "OURS"))):
        x0 = 8 + i * (cw + 8)
        box = checker(cw, ch)
        if img is not None:
            f = fit(img, cw, ch)
            box.alpha_composite(f, ((cw - f.width) // 2, (ch - f.height) // 2))
        t.paste(box, (x0, 44))
        d.text((x0, TILE_H - 18), label, font=font(12, True),
               fill=(150, 150, 150, 255) if i == 0 else (227, 199, 126, 255))
    return t


def sheet(tiles, title):
    rows = (len(tiles) + COLS - 1) // COLS
    W, H = COLS * TILE_W + (COLS + 1) * 8, 44 + rows * (TILE_H + 8) + 8
    s = Image.new("RGBA", (W, H), (11, 16, 20, 255))
    ImageDraw.Draw(s).text((8, 10), title, font=font(22, True), fill=(227, 199, 126, 255))
    for i, t in enumerate(tiles):
        s.paste(t, (8 + (i % COLS) * (TILE_W + 8), 44 + (i // COLS) * (TILE_H + 8)))
    return s.convert("RGB")


def main():
    os.makedirs(OUT, exist_ok=True)
    manifest = {x["path"].lower(): x["key"] for x in json.load(open(os.path.join(ROOT, "texture_manifest.json")))}
    frames, added = game_frames(), first_added()
    entries = []
    for dp, _, fs in os.walk(os.path.join(MOD, "gfx")):
        for f in fs:
            if not f.lower().endswith((".dds", ".tga", ".png")) or "/fonts" in dp.replace("\\", "/"):
                continue
            rel = os.path.relpath(os.path.join(dp, f), MOD).replace("\\", "/")
            stem = rel.rsplit(".", 1)[0]
            game = next((os.path.join(paths.VANILLA, stem + e) for e in (".dds", ".tga", ".png")
                         if os.path.isfile(os.path.join(paths.VANILLA, stem + e))), None)
            if game is None:
                continue                      # a picture of our own, at a path of ours: not a replacement
            key = manifest.get(rel.lower(), "")
            g = key.split("_")[0] if key.split("_")[0] in GROUPS else "other"
            ours, theirs = load(os.path.join(dp, f)), load(game)
            n = frames.get(stem.lower(), 1)
            fw = (ours.width // max(1, n)) if ours else 0
            icon = ours is not None and fw <= ICON_MAX and ours.height <= ICON_MAX
            entries.append(dict(path=rel, group=g, key=key, added=added.get(rel, "before 2026-10-14"),
                                size=f"{ours.width}x{ours.height}" + (f", {n} frames" if n > 1 else "") if ours else "?",
                                icon=icon, game=game, ours=os.path.join(dp, f)))
    entries.sort(key=lambda e: (e["added"], e["path"]))
    index = defaultdict(list)

    def write(name, items, title):
        for i in range(0, len(items), COLS * ROWS):
            part = items[i:i + COLS * ROWS]
            n = i // (COLS * ROWS) + 1
            pages = (len(items) + COLS * ROWS - 1) // (COLS * ROWS)
            tiles = [tile(e["path"].split("gfx/interface/", 1)[-1], e["added"], load(e["game"]) if e["game"] else None,
                          load(e["ours"]) if e["ours"] else None, e["size"]) for e in part]
            fn = f"{name}_{n}.png"
            sheet(tiles, title + (f"  ({n} of {pages})" if pages > 1 else "")).save(os.path.join(OUT, fn))
            index[name].append(dict(file=fn, paths=[e["path"] for e in part]))

    by_group = defaultdict(list)
    for e in entries:
        by_group[e["group"]].append(e)
    for g, items in by_group.items():
        what, ver = GROUPS.get(g, ("Other", ""))
        write(g, items, f"{what} ({ver}): {len(items)} of the game's pictures replaced, the game's left, ours right")
    icons = [e for e in entries if e["icon"]]
    write("icons", icons, f"Every replaced picture of icon size (up to {ICON_MAX} px a frame): {len(icons)}")
    sw = sorted(swaps(added), key=lambda e: (e["gui"], e["path"]))
    for e in sw:
        if e["game"] and not os.path.isfile(e["game"]):
            e["game"] = next((e["game"].rsplit(".", 1)[0] + x for x in (".dds", ".tga")
                              if os.path.isfile(e["game"].rsplit(".", 1)[0] + x)), None)
    write("swaps", sw, f"The game's pictures a screen now shows one of ours in place of ({len(sw)}): "
                       "its .gui points the element at a new picture")
    by_group["swap"] = sw
    json.dump({"groups": {g: dict(what=GROUPS.get(g, ("Other", ""))[0], version=GROUPS.get(g, ("", ""))[1],
                                  count=len(v), icons=sum(e["icon"] for e in v),
                                  added=sorted({e["added"] for e in v})) for g, v in by_group.items()},
               "sheets": index, "entries": [{k: e[k] for k in ("path", "group", "added", "size", "icon")}
                                            for e in entries]},
              open(os.path.join(OUT, "index.json"), "w"), indent=1)
    print(f"{len(entries)} replaced pictures, {len(icons)} of icon size, in {len(by_group)} groups -> {OUT}")


if __name__ == "__main__":
    main()
