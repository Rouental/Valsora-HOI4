"""A superevent's window as the game should draw it (2026-10-15: each round's preview was a one-off script until then):
the window's pieces as the built mod has them (build/valsora_test: interface/valsora_superevent.gui's positions, its
.gfx sprites and textures, the superevent's title strip and picture) and its texts in the Deco UI's own fonts, through
the Deco UI's renderer (deco_ui/tools/validate_preview.py), on a 1920 x 1080 screen.

    python3 scripts/superevent_preview.py [ID ...] [--out PATH]

ID is a superevent's id (rou_civil_war, rou_test ...; superevents.SUPEREVENTS); none: rou_civil_war. Writes
dist/preview_superevent.png (one) or dist/preview_superevent_<id>.png (several). After sh scripts/run_all.sh with
common.DECO_UI on (the game's own interface has another window)."""
import argparse
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "deco_ui" / "tools"))
from common import BUILD, MOD_DIR_NAME  # noqa: E402
import superevents  # noqa: E402

W, H = 1920, 1080


def blocks(text, kind):
    """the bodies of the top-level elements of a kind (iconType ...) inside the window"""
    out = []
    for m in re.finditer(rf"\b{kind}\s*=\s*\{{", text, re.I):
        depth, i = 1, m.end()
        while depth:
            depth += {"{": 1, "}": -1}.get(text[i], 0)
            i += 1
        out.append(text[m.end():i - 1])
    return out


def attr(body, key):
    m = re.search(rf'\b{key}\s*=\s*"?([^"\n}}]+)"?', body)
    return m.group(1).strip() if m else None


def pos(body):
    m = re.search(r"position\s*=\s*\{\s*x\s*=\s*(-?\d+)\s*y\s*=\s*(-?\d+)", body)
    return int(m.group(1)), int(m.group(2))


def texture(mod, sprites, name):
    from ddsutil import read_dds
    return np.asarray(read_dds(str(mod / sprites[name])))      # RGBA, our own uncompressed DDS


def paste(cv, img, x, y, scale=1):
    """an RGBA picture over the canvas (float RGB 0..1) at x, y"""
    if scale != 1:
        img = np.asarray(Image.fromarray(img).resize((img.shape[1] * scale, img.shape[0] * scale), Image.BILINEAR))
    h, w = img.shape[:2]
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, W), min(y + h, H)
    if x1 <= x0 or y1 <= y0:
        return
    src = img[y0 - y:y1 - y, x0 - x:x1 - x].astype(np.float32) / 255
    a = src[..., 3:4]
    cv[y0:y1, x0:x1] = cv[y0:y1, x0:x1] * (1 - a) + src[..., :3] * a


def tile(img, w, h):
    reps = (h // img.shape[0] + 1, w // img.shape[1] + 1, 1)
    return np.tile(img, reps)[:h, :w]


def render(se_id, out):
    import validate_preview as V                     # the Deco UI's fonts and text renderer
    mod = BUILD / MOD_DIR_NAME
    gui = (mod / "interface/valsora_superevent.gui").read_text(encoding="utf-8-sig")
    gfx = (mod / "interface/valsora_superevent.gfx").read_text(encoding="utf-8-sig")
    sprites = dict(re.findall(r'name\s*=\s*"(GFX_[^"]+)"\s*(?:\w+\s*=\s*[^\n]*\n\s*)*?texture[Ff]ile\s*=\s*"([^"]+)"', gfx))
    loc = dict(re.findall(r'^ (VAL_SE_\w+):0 "(.*)"$', (mod / "localisation/english/valsora_l_english.yml")
                          .read_text(encoding="utf-8-sig"), re.M))
    se = next((s for s in superevents.SUPEREVENTS if s["id"] == se_id), None)
    if se is None:
        sys.exit(f"no superevent {se_id}: {', '.join(s['id'] for s in superevents.SUPEREVENTS)}")
    key = f"VAL_SE_{se_id.upper()}"
    texts = {"[ValsoraSupereventQuote]": loc.get(key + "_QUOTE", ""), "[ValsoraSupereventAuthor]": loc.get(key + "_AUTHOR", ""),
             "[ValsoraSupereventSong]": loc.get(key + "_SONG", "")}
    pic = superevents.picture_sprite(se["picture"])
    cv = tile(texture(mod, sprites, "GFX_valsora_superevent_veil"), W, H)[..., :3].astype(np.float32) / 255
    for body in blocks(gui, "iconType"):
        name, spr = attr(body, "name"), attr(body, "spriteType")
        if name.startswith("valsora_superevent_title_") and name != f"valsora_superevent_title_{se_id}":
            continue                                   # only the open superevent's title and picture show
        if name.startswith("valsora_superevent_pic_") and spr != pic:
            continue
        x, y = pos(body)
        paste(cv, texture(mod, sprites, spr), W // 2 + x, H // 2 + y, int(attr(body, "scale") or 1))
    for body in blocks(gui, "buttonType"):
        x, y = pos(body)
        paste(cv, texture(mod, sprites, attr(body, "spriteType")), W // 2 + x, H // 2 + y)
    for body in blocks(gui, "instantTextBoxType"):
        x, y = pos(body)
        txt = texts.get(attr(body, "text"), attr(body, "text"))
        V.draw_text(cv, attr(body, "font"), txt, W // 2 + x, H // 2 + y, int(attr(body, "maxWidth")),
                    attr(body, "format") or "left", max_h=int(attr(body, "maxHeight")),
                    valign=attr(body, "vertical_alignment") == "center")
    Image.fromarray((np.clip(cv, 0, 1) * 255).astype(np.uint8)).save(out)
    print(f"wrote {out}")


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("ids", nargs="*", default=["rou_civil_war"])
    p.add_argument("--out", help="the picture's path (one superevent)")
    o = p.parse_args()
    for se_id in o.ids:
        out = Path(o.out) if o.out and len(o.ids) == 1 else ROOT / "dist" / (
            "preview_superevent.png" if len(o.ids) == 1 else f"preview_superevent_{se_id}.png")
        render(se_id, out)


if __name__ == "__main__":
    main()
