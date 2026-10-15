"""Static checks for the PoC mod, then an approximate in-game preview rendered FROM the generated
.gui/.gfx files (so the preview also checks the coordinates the game will read).

Checks: brace balance; every sprite/font the mod's .gui files use is defined (by the mod or as a
known vanilla sprite); textures read back as valid DDS/TGA with sane frame widths; fonts' .fnt files
agree with their atlases; replaced vanilla textures keep vanilla's sizes; engine strings fit their
boxes; every vanilla element of topbar.gui is still present exactly once.
"""
import glob
import math
import os
import re
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from ddsutil import read_dds  # noqa: E402
import layout as L  # noqa: E402

from paths import MOD as M, VANILLA, ART, BUILD
problems = []


# ------------------------------------------------------------------ Clausewitz parser
def tokenize(s):
    s = re.sub(r"#[^\n]*", "", s)
    return re.findall(r'"[^"]*"|[{}=]|[^\s{}=]+', s)


def parse(tokens, i=0):
    out = []
    while i < len(tokens):
        tok = tokens[i]
        if tok == "}":
            return out, i + 1
        if i + 1 < len(tokens) and tokens[i + 1] == "=":
            val = tokens[i + 2]
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
    return parse(tokenize(open(path, encoding="utf-8-sig").read()))[0]


def attrs(body):
    return {k.lower(): v for k, v in body if k and not isinstance(v, list)}


def sub(body, key):
    for k, v in body:
        if k and k.lower() == key and isinstance(v, list):
            return v
    return None


def xy(lst):
    d = {k.lower(): v for k, v in lst}
    return d.get("x", d.get("width")), d.get("y", d.get("height"))


# ------------------------------------------------------------------ braces
for f in [g for g in glob.glob(M + "interface/**/*", recursive=True) if os.path.isfile(g)] + glob.glob(M + "common/**/*.txt", recursive=True):
    t = re.sub(r"#[^\n]*", "", open(f, encoding="utf-8").read())
    if t.count("{") != t.count("}"):
        problems.append(f"brace mismatch in {f}")

# ------------------------------------------------------------------ what the game's .gui reader accepts
# 1.19.3 rejects a quoted Orientation and alwaystransparent on containerWindowType (error.log of v0.4.4:
# "Not a valid orientation: CENTER_DOWN", "Unexpected token: alwaystransparent") and the window keeps
# the default UPPER_LEFT anchor: that hid the main menu's button row. guipatch.write_gui fixes both;
# this catches anything written another way, and any key the mod puts on an element type that no
# vanilla element of that type uses (the reader may reject it the same silent way).
def element_keys(path):
    """(element type, key, raw value) of every key = value in a .gui file, types lowercased."""
    toks = tokenize(open(path, encoding="utf-8-sig", errors="replace").read())
    stack, out, i = [], [], 0
    while i < len(toks):
        if toks[i] == "}":
            if stack:
                stack.pop()
            i += 1
        elif i + 2 < len(toks) and toks[i + 1] == "=":
            if toks[i + 2] == "{":
                stack.append(toks[i].lower())
            else:
                out.append((stack[-1] if stack else "", toks[i].lower(), toks[i + 2]))
            i += 3
        else:
            i += 1
    return out


vanilla_keys = {}
for f in glob.glob(VANILLA + "interface/**/*.gui", recursive=True):
    for typ, key, _ in element_keys(f):
        vanilla_keys.setdefault(typ, set()).add(key)
for f in sorted(glob.glob(M + "interface/**/*.gui", recursive=True)):
    base = os.path.relpath(f, M + "interface")
    for typ, key, val in element_keys(f):
        if key in ("orientation", "origo") and val.startswith('"'):
            problems.append(f"{base}: quoted {key} {val} on {typ}: write it bare (the game rejects a quoted "
                            f"orientation on containerWindowType; vanilla writes them bare)")
        elif typ == "containerwindowtype" and key == "alwaystransparent":
            problems.append(f"{base}: alwaystransparent on a containerWindowType (put it in the background)")
        elif vanilla_keys and typ in vanilla_keys and key not in vanilla_keys[typ]:
            problems.append(f"{base}: '{key}' on {typ}, which no vanilla {typ} uses")
if not vanilla_keys:
    problems.append("no vanilla .gui files found: the syntax check needs HOI4_DIR (reference/vanilla)")

# ------------------------------------------------------------------ sprite definitions
defs = {}
for f in glob.glob(M + "interface/*.gfx"):
    # a copy of one of the game's .gfx files (the focus view's, v0.6): its other sprites keep the game's textures
    game_copy = os.path.isfile(VANILLA + "interface/" + os.path.basename(f))
    for k, body in load(f):
        if k != "spriteTypes":
            continue
        for kind, b in body:
            a = attrs(b)
            d = dict(kind=kind, frames=int(a.get("noofframes", 1)), game_copy=game_copy)
            d["tex"] = a.get("texturefile") or a.get("texturefile1")
            if kind == "maskedShieldType":
                d["mask"] = a.get("texturefile2")
            if kind == "progressbartype":
                d["bg"] = a.get("texturefile2")
                d["color"] = [float(v) for _, v in sub(b, "color")]
            sz = sub(b, "size")
            if sz:
                d["size"] = tuple(int(v) for v in xy(sz))
            bs = sub(b, "bordersize")
            if bs:
                d["border"] = tuple(int(v) for v in xy(bs))
            defs[a["name"]] = d


def read_tex(rel):
    p = M + rel
    return read_dds(p) if p.endswith(".dds") else Image.open(p).convert("RGBA")


for n, d in defs.items():
    if d["kind"] == "pieChartType":
        continue   # drawn by the game, no texture
    if d["game_copy"] and not os.path.isfile(M + re.sub(r"/+", "/", d["tex"] or "")):
        continue   # a sprite of the game's own, in a copy of its file: its texture is the game's
    try:
        d["img"] = read_tex(d["tex"])
        if "mask" in d:
            d["mask_img"] = read_tex(d["mask"])
            if d["mask_img"].size != d["img"].size:
                problems.append(f"{n}: mask and overlay sizes differ")
        if "bg" in d:
            d["bg_img"] = read_tex(d["bg"])
    except Exception as e:  # noqa: BLE001
        problems.append(f"{n}: texture unreadable {d['tex']}: {e}")
        continue
    w, h = d["img"].size
    if w % d["frames"]:
        problems.append(f"{n}: width {w} not divisible by {d['frames']} frames")
    if d["kind"] == "corneredTileSpriteType" and d.get("size") != (w, h) and not (d["game_copy"] and "size" not in d):
        problems.append(f"{n}: cornered size {d.get('size')} != texture {(w, h)}")
    if d["kind"] == "progressbartype" and d.get("size") != (w, h):
        problems.append(f"{n}: progressbar size {d.get('size')} != texture {(w, h)}")

# vanilla sprite names whose textures the mod replaces at their vanilla paths (the game swaps some of these
# sprites onto buttons at runtime, so the .gui keeps the vanilla names); previews draw the replacements
REPLACED = {
    "GFX_topbar_faction_empty": ("gfx/interface/factions/ui/topbar_faction_empty.dds", 1, "spriteType"),
    "GFX_topbar_faction": ("gfx/interface/factions/ui/topbar_faction.dds", 1, "spriteType"),
    "GFX_decisions_glow": ("gfx/interface/decisionview/decisions_glow.dds", 2, "frameAnimatedSpriteType"),
    "GFX_decisions_glow_blue": ("gfx/interface/decisionview/decisions_glow_blue.dds", 2, "frameAnimatedSpriteType"),
    "GFX_decisions_glow_yellow": ("gfx/interface/decisionview/decisions_glow_yellow.dds", 2, "frameAnimatedSpriteType"),
    "GFX_decisions_glow_green": ("gfx/interface/decisionview/decisions_glow_green.dds", 2, "frameAnimatedSpriteType"),
    "GFX_topbar_international_market": ("gfx/interface/topbar/toolbar/international_market_button.dds", 2, "spriteType"),
    "GFX_topbar_diplomacy": ("gfx/interface/topbar/toolbar/diplomacy_button.dds", 2, "spriteType"),
    "GFX_focus_unavailable": ("gfx/interface/focusview/titlebar/focus_unavailable_bg.dds", 1, "spriteType"),
    "GFX_focus_can_start": ("gfx/interface/focusview/titlebar/focus_can_start_bg.dds", 1, "spriteType"),
    "GFX_focus_completed": ("gfx/interface/focusview/titlebar/focus_completed_bg.dds", 1, "spriteType"),
    # the politics screen's header picture: the game picks one of the two at runtime (v0.4.8)
    "GFX_pol_view_bg": ("gfx/interface/pol_view_bg.dds", 1, "spriteType"),
    "GFX_pol_view_bg_no_dlc": ("gfx/interface/pol_view_bg_no_dlc.dds", 1, "spriteType"),
}
for _n, (_rel, _fr, _kind) in REPLACED.items():
    if os.path.isfile(M + _rel):
        defs.setdefault(_n, dict(kind=_kind, frames=_fr, tex=_rel, img=read_tex(_rel), vanilla_path=True))

gui = load(M + "interface/topbar.gui")
extras = load(M + "interface/valsora_deco_topbar_extras.gui")
gui_text = "".join(open(f, encoding="utf-8-sig").read() for f in sorted(glob.glob(M + "interface/**/*.gui", recursive=True)))
used = set(re.findall(r'"(GFX_valsora_[^"]+)"', gui_text))
for u in sorted(used - set(defs)):
    problems.append(f"sprite used but not defined: {u}")
print("sprites defined", len(defs), "used", len(used), "unused", sorted(set(defs) - used))
vanilla_gfx = set()
for f in glob.glob(VANILLA + "interface/**/*.gfx", recursive=True):
    vanilla_gfx |= set(re.findall(r'name\s*=\s*"?(GFX_[A-Za-z0-9_]+)', open(f, encoding="utf-8-sig", errors="ignore").read()))
# sprites the game's own .gui files name without defining them (countrydecisionview.gui's GFX_category_end_bg)
# are the game's to sort out: the mod keeps every element of the files it patches
vanilla_named = set()
for f in glob.glob(VANILLA + "interface/**/*.gui", recursive=True):
    vanilla_named |= set(re.findall(r'"(GFX_[A-Za-z0-9_]+)"', open(f, encoding="utf-8-sig", errors="ignore").read()))
for u in sorted(set(re.findall(r'"(GFX_[A-Za-z0-9_]+)"', gui_text)) - set(defs) - vanilla_gfx - vanilla_named):
    problems.append(f"sprite neither in the mod nor in the game: {u}")

# every vanilla element still present exactly as often: for EVERY .gui the mod ships at a vanilla path
# (the engine finds elements by name). countrypoliticsview.gui is compared with the Valsora mod's copy
# when it has one, since that is the base make_politics.py starts from.
from paths import VALSORA, VALSORA_BASE  # noqa: E402


def _names(path):
    src = re.sub(r"#[^\n]*", "", open(path, encoding="utf-8-sig", errors="ignore").read())
    return re.findall(r'\bname\s*=\s*"?([A-Za-z0-9_.\-]+)"?', src)


for mod_gui in sorted(glob.glob(M + "interface/**/*.gui", recursive=True)):
    base = os.path.relpath(mod_gui, M + "interface").replace(os.sep, "/")
    ref = next((r + "interface/" + base for r in (VALSORA_BASE, VALSORA, VANILLA) if os.path.isfile(r + "interface/" + base)
                and "Valsora Deco UI" not in open(r + "interface/" + base, encoding="utf-8-sig", errors="ignore").read(300)), None)
    if ref is None and os.path.isfile(VANILLA + "interface/" + base):
        ref = VANILLA + "interface/" + base
    if not ref:
        continue                                          # a new file of the mod's own
    van, mine = _names(ref), _names(mod_gui)
    for n in sorted(set(van)):
        if mine.count(n) != van.count(n):
            problems.append(f"{base}: vanilla element {n} count changed {van.count(n)} -> {mine.count(n)}")
    added = sorted(set(mine) - set(van))
    print(f"{base}: vanilla elements kept {len(set(van))} | added {len(added)}"
          + (f": {added}" if base == "topbar.gui" else ""))

# ------------------------------------------------------------------ fonts
fonts_gfx = load(M + "interface/valsora_deco_fonts.gfx")
fdefs = {}
for k, body in fonts_gfx:
    for kind, b in body:
        a = attrs(b)
        col = int(a["color"], 16)
        tc = {k: tuple(int(x) for _, x in v) for k, v in (sub(b, "textcolors") or [])}
        fdefs[a["name"]] = dict(path=a["path"], color=((col >> 16) & 255, (col >> 8) & 255, col & 255), tc=tc)
for u in set(re.findall(r'font\s*=\s*"(valsora_[^"]+)"', gui_text)):
    if u not in fdefs:
        problems.append(f"font used but not defined: {u}")


def load_fnt(base):
    t = open(base + ".fnt", encoding="utf-8").read()
    common = dict(re.findall(r"(\w+)=(-?\d+)", t.split("\n")[1]))
    page = re.search(r'page id=0 file="([^"]+)"', t).group(1)
    chars = {}
    for line in t.split("\n"):
        if line.startswith("char "):
            d = {k: int(v) for k, v in re.findall(r"(\w+)=(-?\d+)", line)}
            chars[d["id"]] = d
    kern = {(int(a), int(b)): int(k) for a, b, k in re.findall(r"kerning first=(\d+)\s+second=(\d+)\s+amount=(-?\d+)", t)}
    return dict(common=common, page=page, chars=chars, kern=kern, atlas=read_dds(base[: base.rfind("/") + 1] + page))


FONTS = {}
# the game's own fonts the mod redraws (game_fonts.py): not defined by the mod, but checked like its own
import game_fonts as _GFN
_game = [(n, dict(path=f"gfx/fonts/{n}", color=(255, 255, 255))) for n in _GFN.GAME]
for name, fd in list(fdefs.items()) + [("tahoma_60", dict(path="gfx/fonts/hoi_mapfont4", color=(255, 255, 255)))] + _game:
    f = load_fnt(M + fd["path"])
    f["color"] = fd["color"]
    f["tc"] = fd.get("tc", {})
    FONTS[name] = f
    if f["page"] != fd["path"].split("/")[-1] + ".dds":
        problems.append(f"{name}: page file {f['page']} does not match {fd['path']}")
    W, H = f["atlas"].size
    if (W, H) != (int(f["common"]["scaleW"]), int(f["common"]["scaleH"])):
        problems.append(f"{name}: scaleW/H mismatch")
    for c in f["chars"].values():
        if c["x"] < 0 or c["y"] < 0 or c["x"] + c["width"] > W or c["y"] + c["height"] > H:
            problems.append(f"{name}: char {c['id']} outside atlas")
    print(f"font {name}: {len(f['chars'])} chars, {len(f['kern'])} kerning pairs, atlas {W}x{H}, line {f['common']['lineHeight']}")

# ------------------------------------------------------------------ replaced vanilla textures keep vanilla sizes
def tex_size(path):
    """(width, height) from a DDS or TGA header (vanilla's DDS may be compressed; only the header is read)"""
    with open(path, "rb") as f:
        head = f.read(20)
    if head[:4] == b"DDS ":
        return int.from_bytes(head[16:20], "little"), int.from_bytes(head[12:16], "little")
    return int.from_bytes(head[12:14], "little"), int.from_bytes(head[14:16], "little")


# the window tiles' sizes come from the sprite definitions in vanilla's .gfx (192x192 ...), not from vanilla's
# texture files (190x190 ...); the game reads them by the definition
VANILLA_TILES = {
    "gfx/interface/tiles/tiled_window.dds": (192, 192), "gfx/interface/tiles/tiled_window_2b_border.dds": (192, 192),
    "gfx/interface/tiles/tiled_window2_2b_border.dds": (192, 192), "gfx/interface/tiles/tiled_window_1b_border.dds": (192, 192),
    "gfx/interface/tiles/tiled_window2_1b_border.dds": (192, 192), "gfx/interface/tiles/tiled_window_1b_thin_border.dds": (192, 192),
    "gfx/interface/tiles/tiled_window_thin_border.dds": (192, 192), "gfx/interface/tiles/tiled_window_thin_border2.dds": (192, 192),
    "gfx/interface/tiles/tiled_window_small.dds": (96, 96), "gfx/interface/tiles/tiled_window_small_small.dds": (48, 48),
    "gfx/interface/tiles/tiled_mini_dialog.dds": (32, 32), "gfx/interface/tiles/tiled_plain_bg.dds": (192, 192),
    "gfx/interface/tiles/tiled_bg.dds": (192, 192),
}
for rel, size in VANILLA_TILES.items():
    if read_dds(M + rel).size != size:
        problems.append(f"{rel} size mismatch")
# replaced at vanilla's size on purpose: the icon whose sprite the game swaps, the tooltip's frame
SAME_SIZE = ["gfx/interface/pol_view_bg.dds", "gfx/interface/pol_view_bg_no_dlc.dds", "gfx/interface/tiles/tiles_dialog.dds",
             # the panels' shared pieces (v0.5): the game lays them out at vanilla's sizes
             "gfx/interface/closebutton.dds", "gfx/interface/header_bg.dds", "gfx/interface/category_header.dds",
             "gfx/interface/factions/ui/faction_header.dds", "gfx/interface/main_screens_bottom.dds",
             "gfx/interface/deployment_binding.dds", "gfx/interface/tradeview/trade_header.dds",
             "gfx/interface/intel_ledger/tab_bg.dds", "gfx/interface/diplo_details_header.dds",
             "gfx/interface/generic_text_bg_108.dds", "gfx/interface/tiles/tiling_sort_button.dds",
             "gfx/interface/tab_large.dds", "gfx/interface/intel_ledger/tab.dds", "gfx/interface/diplo_filter_entry.dds",
             "gfx/interface/sort_button_100x29_2.dds", "gfx/interface/generic_checkbox.dds",
             # the focus tree's links and exclusive marks (v0.6): the game cuts them into 16 and 32 px frames
             *[f"gfx/interface/focusview/focus_link_{k}.dds" for k in (
                 "up_down", "left_right", "down_left", "down_right", "up_left", "up_right", "down_left_right",
                 "up_down_left", "up_down_right", "up_left_right", "up_down_left_right", "exclusive")],
             "gfx/interface/focusview/focus_exlusive_link_line1.dds", "gfx/interface/focusview/focus_exlusive_link_line2.dds",
             "gfx/interface/cont_focus_check_icon.dds",
             # the army bar (v0.7): the game cuts these into frames and lays the cards out by their sizes
             *[f"gfx/interface/unitcontrol/{k}.dds" for k in (
                 "leader_group_frame", "leader_army_group_frame", "army_mid_bg", "army_end_bg", "army_group_back_bg",
                 "execute_btn_play_small", "execute_btn_play_small_ag", "execute_btn_stop_small", "execute_btn_stop_small_ag",
                 "execute_stop_small_bg", "excecute_stop_border_war_bg", "execute_button_no_order", "active_battleplan_anim",
                 "execute_button_point_out_mode", "army_group_expand_collapse", "comm_group_plan_power_bar",
                 "comm_group_plan_power_bar_bg", "disband_orders_group", "group_add_leader_bg", "group_add_leader",
                 "group_add_marshal_bg", "group_add_marshal", "hq_alert", "hq_badge", "give_role_leader_strip")],
             "gfx/interface/attached_air_bg.dds",
             # the events (v0.7): the game stacks and stretches these by their sizes
             *[f"gfx/interface/{k}.dds" for k in (
                 "event_report_top_win", "event_report_tileable_midsection", "event_report_bottom_win", "event_option_entry",
                 "event_pic_clip", "event_button_minimize", "event_news_bg", "event_news_pic_overlay", "event_leader_frame",
                 "event_report_bottom_win_2", "events/clip")]]
VG = VANILLA + "gfx/"
if os.path.isdir(VG):
    resized = []
    for f in sorted(glob.glob(M + "gfx/**/*.*", recursive=True)):
        rel = f[len(M):].replace(os.sep, "/")
        if not rel.endswith((".dds", ".tga")) or rel.startswith("gfx/fonts/"):
            continue
        van = VANILLA + rel
        # the game loads a .dds of the same name before a .tga, vanilla's included (in game, v0.4.7: the
        # tooltip .tga never showed, vanilla's tiles_dialog.dds did)
        if rel.endswith(".tga") and os.path.isfile(van[:-4] + ".dds"):
            problems.append(f"{rel}: the game loads vanilla's {rel[:-4]}.dds instead; replace the .dds")
        if os.path.isfile(van) and tex_size(f) != tex_size(van):
            if rel in SAME_SIZE:
                problems.append(f"{rel}: {tex_size(f)} but vanilla's is {tex_size(van)}")
            elif rel not in VANILLA_TILES:
                resized.append(f"{rel.split('/')[-1]} {tex_size(van)}->{tex_size(f)}")
    for rel in SAME_SIZE:
        if not os.path.isfile(M + rel):
            problems.append(f"{rel} missing")
    print("replaced vanilla textures drawn at another size (laid out by the mod's .gui):", ", ".join(resized))
else:
    problems.append(f"no vanilla gfx at {VG}: replaced textures were not checked (section 3 of CLAUDE.md)")
for p in glob.glob(M + "gfx/interface/button_*.dds"):
    w, h = map(int, re.search(r"button_(\d+)x(\d+)", p).groups())
    if read_dds(p).size != (w, h):
        problems.append(f"{p} size mismatch")

# every texture in the mod comes from the current build (stale files from older versions are reported)
import json  # noqa: E402
from paths import MANIFEST  # noqa: E402
_man = {m["path"] for m in json.load(open(MANIFEST))}
for f in glob.glob(M + "gfx/**/*", recursive=True):
    rel = f[len(M):].replace(os.sep, "/")
    if os.path.isfile(f) and not rel.startswith("gfx/fonts/") and rel not in _man:
        problems.append(f"stale texture not produced by gen_textures.py (delete it): {rel}")

# localisation files have a BOM and define every key the .gui files use
for f in glob.glob(M + "localisation/*/*.yml"):
    if not open(f, "rb").read(3) == b"\xef\xbb\xbf":
        problems.append(f"{f}: missing UTF-8 BOM")
loc = dict(re.findall(r'^\s*(\w+):0 "(.*)"$', open(M + "localisation/english/valsora_deco_ui_l_english.yml", encoding="utf-8-sig").read(), re.M))
loc_all = {}
for f in glob.glob(M + "localisation/english/*.yml"):
    loc_all.update(re.findall(r'^\s*(\w+):0 "(.*)"$', open(f, encoding="utf-8-sig").read(), re.M))
for k in set(re.findall(r'text\s*=\s*"(VAL_DECO_[A-Z_]+)"', gui_text)):
    if k not in loc_all:
        problems.append(f"loc key missing: {k}")
for k in []:
    if k not in loc:
        problems.append(f"loc key missing: {k}")


# ------------------------------------------------------------------ preview renderer
def _runs(text, base):
    """Split a string with §X ... §! colour codes into (char, colour-letter) pairs."""
    out, stack, i = [], [], 0
    while i < len(text):
        if text[i] == "\u00a7" and i + 1 < len(text):
            if text[i + 1] == "!":
                stack and stack.pop()
            else:
                stack.append(text[i + 1])
            i += 2
            continue
        out.append((text[i], stack[-1] if stack else None))
        i += 1
    return out


def text_width(f, runs):
    cps = [ord(c) for c, _ in runs if ord(c) in f["chars"]]
    return sum(f["chars"][c]["xadvance"] for c in cps) + sum(f["kern"].get(p, 0) for p in zip(cps, cps[1:]))


def wrap(runs, max_w, width):
    """the game's greedy word wrap: forced breaks at newlines, then words onto a line while it fits"""
    out = []
    para = []
    for r in runs + [("\n", None)]:
        if r[0] != "\n":
            para.append(r)
            continue
        cur, word = [], []
        for q in para + [(" ", None)]:
            if q[0] == " ":
                if word:
                    trial = cur + ([(" ", None)] if cur else []) + word
                    if cur and max_w and width(trial) > max_w:
                        out.append(cur)
                        cur = word
                    else:
                        cur = trial
                word = []
            else:
                word.append(q)
        out.append(cur)
        para = []
    return out


# the game's own widths for the fonts the mod redraws: a box the game's text overflows too is the game's, not ours
GAME_W = {}
for _n in _GFN.GAME:
    try:
        GAME_W[_n] = _GFN.game_widths(_n)
    except OSError:
        pass


def draw_text(canvas, font, text, x, y, max_w=None, fmt="left", color=None, check=None, max_h=None, valign=False):
    f = FONTS[font]
    chars = f["chars"]
    atlas = f.setdefault("_np", np.array(f["atlas"], dtype=np.float32) / 255)
    runs = _runs(text, None)
    lh = int(f["common"]["lineHeight"])
    # word wrap when the box has room for more than one line (as the game does); newlines always break
    multi = bool(max_w and max_h and max_h >= 2 * lh)
    ours = lambda rs: text_width(f, rs)
    lines = wrap(runs, max_w if multi else None, ours)
    game = GAME_W.get(font)
    as_game = (lambda rs: game("".join(c for c, _ in rs))) if game else None
    game_lines = wrap(runs, max_w if multi else None, as_game) if game else None
    if check and max_h and len(lines) * lh > max_h + 2 and not (game_lines and len(game_lines) >= len(lines)):
        problems.append(f"text needs {len(lines)} lines in {check}: {text!r}")
    total_h = len(lines) * lh
    y0 = y + (max_h - total_h) / 2 if (valign and max_h) else y
    for li, line in enumerate(lines):
        width = text_width(f, line)
        # flagged when wider than the box and than the game's own text (by 5 %): where the game's overflows too, ours
        # may as well
        if check and max_w and width > max_w and (not as_game or width > max(max_w, as_game(line) * 1.05)):
            problems.append(f"text overflow in {check}: {text!r} {width}px > {max_w}px")
        lx = x
        if max_w and fmt in ("center", "centre"):
            lx = x + (max_w - width) / 2
        elif max_w and fmt == "right":
            lx = x + max_w - width
        # a line starts on a whole pixel, as the game draws text: rounding each glyph's half-pixel position on its own
        # (round() takes .5 to the even number) moved every other letter of centred text a pixel ("Postpon e")
        pen, ly, prev = math.floor(lx), math.floor(y0) + li * lh, None
        for ch, code in line:
            cp = ord(ch)
            if cp not in chars:
                continue
            c = chars[cp]
            if prev is not None:
                pen += f["kern"].get((prev, cp), 0)
            col = np.array((f["tc"].get(code) if code else None) or color or f["color"], np.float32) / 255
            g = atlas[c["y"]:c["y"] + c["height"], c["x"]:c["x"] + c["width"]]
            gx, gy = pen + c["xoffset"], ly + c["yoffset"]
            h, w = g.shape[:2]
            if 0 <= gx and 0 <= gy and gx + w <= canvas.shape[1] and gy + h <= canvas.shape[0]:
                rgb, a = g[..., :3], g[..., 3:4]
                region = canvas[gy:gy + h, gx:gx + w]
                canvas[gy:gy + h, gx:gx + w] = region * (1 - a) + (rgb * col) * a
            pen += c["xadvance"]
            prev = cp
    return 0


def paste(canvas, img, x, y, frame=0, frames=1, alpha=1.0):
    a = np.array(img.convert("RGBA"), np.float32) / 255
    fw = a.shape[1] // frames
    a = a[:, frame * fw:(frame + 1) * fw]
    x, y = int(round(x)), int(round(y))
    h, w = a.shape[:2]
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(canvas.shape[1], x + w), min(canvas.shape[0], y + h)
    if x1 <= x0 or y1 <= y0:
        return
    s = a[y0 - y:y1 - y, x0 - x:x1 - x]
    al = s[..., 3:4] * alpha
    canvas[y0:y1, x0:x1] = canvas[y0:y1, x0:x1] * (1 - al) + s[..., :3] * al


def cornered(img, w, h, bx, by):
    a = np.array(img.convert("RGBA"))
    H, W = a.shape[:2]
    xs = np.concatenate([np.arange(bx), bx + (np.arange(max(0, w - 2 * bx)) % max(1, W - 2 * bx)), W - bx + np.arange(bx)])[:w]
    ys = np.concatenate([np.arange(by), by + (np.arange(max(0, h - 2 * by)) % max(1, H - 2 * by)), H - by + np.arange(by)])[:h]
    return Image.fromarray(a[ys][:, xs], "RGBA")


def standin(kind, w, h):
    """Neutral stand-ins for vanilla art the mod leaves untouched (drawn so the layout reads)."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    from PIL import ImageDraw
    d = ImageDraw.Draw(im)
    if kind == "globe":
        d.ellipse((1, 1, w - 2, h - 2), fill=(52, 70, 78, 255), outline=(150, 160, 150, 255), width=2)
        d.ellipse((w * .3, 2, w * .7, h - 3), outline=(150, 160, 150, 160), width=1)
        d.line((2, h / 2, w - 3, h / 2), fill=(150, 160, 150, 160), width=1)
        d.pieslice((1, 1, w - 2, h - 2), -90, -40, fill=(200, 120, 70, 200))
    else:
        d.rounded_rectangle((1, 1, w - 2, h - 2), 4, fill=(60, 56, 48, 235), outline=(150, 140, 120, 255))
        if kind == "crate":
            d.rectangle((5, 6, w - 6, h - 5), outline=(190, 182, 160, 255))
            d.line((5, 10, w - 6, 10), fill=(190, 182, 160, 255))
        else:
            d.text((w / 2 - 3, h / 2 - 6), kind, fill=(210, 200, 180, 255))
    return im


STANDIN = {"GFX_world_tension_icon_big_strip": ("globe", 50, 50), "GFX_equipment_icon": ("crate", 24, 24),
           "GFX_achievements_button": ("A", 28, 28), "GFX_show_dismissed_alerts_icon": ("!", 28, 28)}
SKIP = {"reopen_ingame_lobby", "reopen_ingame_lobby_label", "toggle_music_commands_win", "observer_flag_overlay",
        "pause_button_date_paused", "threat_icon_glow", "decision_view_alert_glow", "production_button_glow",
        "decisionview_amount_timeout_bg", "decisionview_amount_timeout_items", "decisionview_amount_to_take_bg",
        "decisionview_amount_to_take_items", "intelview_ops_prepared_or_completed_bg",
        "intelview_ops_prepared_or_completed_items", "intelview_ops_available_bg", "intelview_ops_available_items",
        "prototype_rewards_aquired_bg", "prototype_rewards_aquired", "non_delivering_contracts", "delivering_contracts",
        "faction_icon", "industrial_ratio_bar", "pause_window"}
SAMPLE = {"valsora_deco_pp_daily": "\u00a7G+1.80\u00a7!",
          "valsora_deco_factory_counts": "\u00a7W\u25c6\u00a7!3 \u00a7O\u25c6\u00a7!2 \u00a7C\u25c6\u00a7!0",
          "valsora_deco_country_name_small": "Terrabis-Seran", "pol_power": "47", "stability": "60%", "war_support": "30%", "manpower": "151.2K",
          "industrial_capacity": "3/2/0", "fuel_value": "4.1K", "supply_value": "92%", "convoys_count": "20",
          "command_power_value": "18", "experience_value": "12", "navy_experience_value": "8",
          "air_experience_value": "5", "nukes_value": "2", "initiative_text": "0", "industrial_capacity": "5", "threat_value": "4%", "DateText": "12:00, 1 March, 2036",
          "valsora_deco_country_name": "Rouental"}
WORST = {"valsora_deco_pp_daily": "\u00a7G+12.50\u00a7!",
         "valsora_deco_factory_counts": "\u00a7W\u25c6\u00a7!45 \u00a7O\u25c6\u00a7!30 \u00a7C\u25c6\u00a7!8",
         "valsora_deco_country_name_small": "Ponchomagnifico", "pol_power": "999", "stability": "100%", "war_support": "100%", "manpower": "12.34M",
         "industrial_capacity": "120/80/12", "fuel_value": "99.9K", "supply_value": "100%", "convoys_count": "999",
         "command_power_value": "200", "experience_value": "999", "navy_experience_value": "999",
         "air_experience_value": "999", "nukes_value": "99", "threat_value": "100%",
         "DateText": "00:00, 30 September, 2040", "valsora_deco_country_name": "Utopian Republic"}
FRAME = {"button_speedstep1": 1, "button_speedstep2": 1, "button_speedstep3": 1}
BOXES = []   # (name, x, y, w, h) for the debug overlay


def render(cv, elems, px, py, pr, worst=False):
    for key, body in elems:
        kl = key.lower() if key else None
        if kl not in ("containerwindowtype", "icontype", "buttontype", "instanttextboxtype"):
            continue
        d = attrs(body)
        name = d.get("name")
        if name in SKIP:
            continue
        pos = sub(body, "position")
        x, y = (int(v) for v in xy(pos)) if pos else (0, 0)
        ori = d.get("orientation", "UPPER_LEFT").upper()
        ax = pr + x if ori == "UPPER_RIGHT" else px + x
        ay = py + y
        if kl == "containerwindowtype":
            sz = sub(body, "size")
            w, h = xy(sz) if sz else (0, 0)
            w = pr - ax if "%" in str(w) else int(w)
            h = 1080 if "%" in str(h) else int(h)
            bg = sub(body, "background")
            if bg:
                spr = attrs(bg).get("quadtexturesprite") or attrs(bg).get("spritetype")
                if spr in defs:
                    dd = defs[spr]
                    img = cornered(dd["img"], w, h, *dd["border"]) if dd["kind"] == "corneredTileSpriteType" else dd["img"]
                    paste(cv, img, ax, ay)
            if d.get("spritetype") in defs:
                paste(cv, defs[d["spritetype"]]["img"], ax, ay)
            render(cv, body, ax, ay, ax + w, worst)
        elif kl in ("icontype", "buttontype"):
            spr = d.get("quadtexturesprite") or d.get("spritetype")
            if name == "threat_value_button":
                cv[ay:ay + 20, ax:ax + 50] *= 0.55
                continue
            if spr in defs:
                dd = defs[spr]
                if dd["kind"] == "maskedShieldType":
                    W, H = dd["img"].size
                    flag = Image.open(ART + "flag_ROU.png").convert("RGB")
                    flag = flag.resize((82, 52), Image.LANCZOS).resize((W, H), Image.NEAREST)  # game flag is 82x52, unsmoothed
                    paste(cv, flag, ax, ay)
                    paste(cv, dd["img"], ax, ay)
                elif dd["kind"] == "progressbartype":
                    W, H = dd["img"].size
                    paste(cv, dd["bg_img"], ax, ay)
                    fill = np.array(dd["img"], np.float32)
                    fill[..., :3] *= np.array(dd["color"], np.float32)
                    fill = Image.fromarray(fill.clip(0, 255).astype(np.uint8)).crop((0, 0, int(W * .78), H))
                    paste(cv, fill, ax, ay)
                else:
                    paste(cv, dd["img"], ax, ay, FRAME.get(name, 0), dd["frames"])
                BOXES.append((name, ax, ay, dd["img"].size[0] // dd["frames"], dd["img"].size[1]))
            elif spr in STANDIN:
                k, w, h = STANDIN[spr]
                paste(cv, standin(k, w, h), ax, ay)
                BOXES.append((name, ax, ay, w, h))
            elif spr:
                problems.append(f"preview: no art for {name} ({spr})")
        else:
            txt = (WORST if worst else SAMPLE).get(name) or loc.get(d.get("text"), None)
            if txt is None:
                continue
            mw = int(d.get("maxwidth", 0)) or None
            mh = int(d.get("maxheight", 0)) or None
            draw_text(cv, d["font"], txt, ax, ay, mw, d.get("format", "left"), check=name if worst else None,
                      max_h=mh, valign=d.get("vertical_alignment") == "center")
            BOXES.append((name, ax, ay, mw or 0, int(d.get("maxheight", 0))))


SW, SH = 1920, 230
bg = Image.open(ART + "map_rouental.jpg").convert("RGB").resize((1920, 1080), Image.LANCZOS).crop((0, 0, SW, SH))


def build(worst=False):
    cv = np.array(bg, np.float32) / 255
    top = gui[0][1]  # guiTypes
    for k, b in top:
        if k == "containerWindowType" and attrs(b).get("name") == "topbar":
            tb = b
    render(cv, [("containerWindowType", tb)], 0, 0, 1920, worst)
    # scripted-GUI window: child of the top bar container (origin -4,-1)
    wins = [(k, b) for k, b in extras[0][1]
            if worst or attrs(b).get("name") != "valsora_deco_country_name_small_window"]
    render(cv, wins, -4, -1, 1920, worst)
    return cv


BOXES.clear()
build(worst=True)          # overflow check with long engine strings
BOXES.clear()
cv = build()
out = Image.fromarray((np.clip(cv, 0, 1) * 255).astype(np.uint8))
out.save(BUILD + "preview_topbar.png")

# debug overlay: element boxes (to eyeball overlaps)
dbg = out.copy()
from PIL import ImageDraw  # noqa: E402
dd_ = ImageDraw.Draw(dbg)
for n, x, y, w, h in BOXES:
    if w and h:
        dd_.rectangle((x, y, x + w - 1, y + h - 1), outline=(0, 255, 255))
dbg.save(BUILD + "preview_topbar_boxes.png")

print("PROBLEMS:", problems if problems else "none")
