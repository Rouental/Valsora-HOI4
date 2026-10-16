"""Build the side panels other than the politics screen (v0.5): army, construction, decisions, deployment,
diplomacy, intelligence, logistics, occupation, officer corps, production, research, trade, faction, faction
setup, faction pings and the international market, plus the windows that open beside them.

    python make_panels.py ["<HOI4 install folder>"]

Each panel is patched from the game's own file (none of them is in the Valsora mod) the way the politics
screen is (layout_panels.py has the numbers):
  - the window sits flush under the top bar's band (layout_panels.TOP) instead of 16 px below it;
  - its own background is clear and lets clicks through; new children draw the panel instead: a body tile
    from the seal's bottom down, invisible click-catchers beside the notch, and a header picture with a notch
    where the flag medallion and the decisions seal hang (side panels are drawn over the top bar);
  - the game's header picture is hidden, its title moves right of the notch in gilt capitals, the close
    button becomes the deco diamond, and the header buttons line up beside it;
  - every other top-anchored element moves down by the panel's shift, clearing the seal.
Every element and name is kept. The windows that open beside the panels move up to the band as well.
Writes interface/<the game's path> for each panel and interface/valsora_deco_panels.gfx.
"""
import os
import re
import sys

import guipatch as GP
import layout as L
import layout_panels as LPN
from paths import MOD, VANILLA as VANILLA_DIR

VANILLA = sys.argv[1] if len(sys.argv) > 1 else VANILLA_DIR
CLEAR, NONE = "GFX_valsora_deco_clear", "GFX_valsora_deco_none"
BODY, CLOSE = "GFX_valsora_deco_pol_body", "GFX_valsora_deco_pol_close"
TOP_ANCHORS = ("", "UPPER_LEFT", "UPPER_RIGHT", "CENTER_UP")


head_sprite, head_texture = LPN.head_sprite, LPN.head_texture


def loc_english():
    out = {}
    root = os.path.join(VANILLA, "localisation", "english")
    for d, _, files in os.walk(root):
        for f in files:
            if f.endswith(".yml"):
                for m in re.finditer(r'^\s*([\w.\-]+):\d*\s*"(.*)"\s*$',
                                     open(os.path.join(d, f), encoding="utf-8-sig", errors="ignore").read(), re.M):
                    out.setdefault(m.group(1), m.group(2))
    return out


LOC = loc_english()


# ---------------------------------------------------------------- reading the game's file
def own_head(t, s, e):
    return GP.own_region(t[s:e])[0]


def attr(head, key):
    m = re.search(r"\b" + key + r'\s*=\s*"?([\w%.@\-]+)"?', GP._strip_comments(head), re.I)
    return m.group(1) if m else None


def pos_of(head):
    """(x, y) of an element's own position, or None when it has none (a position that isn't two numbers stops)"""
    clean = GP._strip_comments(head)
    m = re.search(r"(?<![\w_])position\s*=\s*\{\s*x\s*=\s*(-?[\d.]+)\s*y\s*=\s*(-?[\d.]+)\s*\}", clean, re.I)
    assert m or not re.search(r"(?<![\w_])position\s*=", clean, re.I), ("a position this can't move", clean[:200])
    return (float(m.group(1)), float(m.group(2))) if m else None


def children(t, s, e):
    """(start, end, kind) of the element blocks and background blocks directly inside the block at s..e"""
    clean = GP._strip_comments(t)
    i, end = clean.index("{", s) + 1, e - 1
    head = re.compile(r"(" + GP.TYPES + r"|background)\s*=\s*\{", re.I)
    out = []
    while True:
        m = head.search(clean, i, end)
        if not m:
            return out
        between = clean[i:m.start()]
        assert between.count("{") == between.count("}"), ("unexpected block", clean[i:m.start()][:200])
        ce = GP._block_end(clean, m.start())
        out.append((m.start(), ce, m.group(1).lower()))
        i = ce


# ---------------------------------------------------------------- editing in place (offsets, last first)
def with_position(head, x, y):
    """the element's own text with its position set (added after the name when it has none)"""
    val = "{ x = %d y = %d }" % (round(x), round(y))
    new, n = re.subn(r"(?<![\w_])(position\s*=\s*)\{[^}]*\}", lambda m: m.group(1) + val, head, count=1, flags=re.I)
    if n:
        return new
    return re.sub(r'(\n(\s*)name\s*=\s*"?[\w.\-&]+"?[^\n]*)', lambda m: m.group(1) + "\n" + m.group(2) + "position = " + val,
                  head, count=1)


def window_span(t, name):
    return GP.find_block(t, name)


def clear_background(t, bg_s, bg_e):
    """a background block's picture becomes the clear sprite, and it lets clicks through"""
    blk = t[bg_s:bg_e]
    blk, n = re.subn(r'((?:quadTextureSprite|spriteType)\s*=\s*)"?[\w&]+"?', r'\1"%s"' % CLEAR, blk, count=1, flags=re.I)
    assert n == 1, blk
    if not re.search(r"alwaystransparent", GP._strip_comments(blk), re.I):
        close = blk.rindex("}")
        line = blk.rindex("\n", 0, close) + 1 if "\n" in blk[:close] else close
        if blk[line:close].strip() == "":            # the closing brace on a line of its own
            blk = blk[:line] + blk[line:close] + "\talwaystransparent = yes\n" + blk[line:]
        else:
            blk = blk[:close] + " alwaystransparent = yes " + blk[close:]
    return t[:bg_s] + blk + t[bg_e:]


def snippet_container(name, x, y, w, h, sprite):
    return (f'\n\t\tcontainerWindowType = {{\n\t\t\tname = "{name}"\n\t\t\tposition = {{ x = {x} y = {y} }}\n'
            f'\t\t\tsize = {{ width = {w} height = {h} }}\n'
            f'\t\t\tbackground = {{\n\t\t\t\tname = "{name}_bg"\n\t\t\t\tquadTextureSprite = "{sprite}"\n\t\t\t}}\n\t\t}}')


def snippet_icon(name, sprite, x, y):
    return (f'\n\t\ticonType = {{\n\t\t\tname = "{name}"\n\t\t\tspriteType = "{sprite}"\n'
            f'\t\t\tposition = {{ x = {x} y = {y} }}\n\t\t\tOrientation = "UPPER_LEFT"\n\t\t\talwaystransparent = yes\n\t\t}}')


def wrap_lines(font, text, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if cur and L.measure(font, trial) > width:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    lines.append(cur)
    return lines


def title_font(text, width, max_lines=2):
    """title_24 when the English title fits in the box's lines (two, or max_lines), else title_18"""
    for font in (LPN.TITLE_FONT, LPN.TITLE_FONT_SMALL):
        lines = wrap_lines(font, text.upper(), width)
        if len(lines) <= max_lines and len(lines) * int(L.fnt(font)[2]["lineHeight"]) <= LPN.TITLE_H \
                and all(L.measure(font, ln) <= width for ln in lines):
            return font, lines
    raise AssertionError(f"title {text!r} does not fit {width} px")


hidden_x = LPN.LP.closed_x   # where a closed window rests (off-screen; it opens at once)


# ---------------------------------------------------------------- one panel
def panel(t, key, spec):
    R = spec["window"]
    s, e = window_span(t, R)
    head = own_head(t, s, e)
    show = re.search(r"show_position\s*=\s*\{\s*x\s*=\s*(-?\d+)\s*y\s*=\s*(-?\d+)", head)
    W = int(re.search(r"size\s*=\s*\{\s*width\s*=\s*(\d+)", head).group(1))
    X = int(show.group(1))
    assert (X, W) == (spec.get("x", -6), spec.get("w", 550)), (key, X, W)
    D = spec.get("shift", LPN.SHIFT)
    HW = spec.get("head_w", W)
    HX = LPN.hx(X)
    header = set(spec.get("header", [])) | {p.split(">")[0] for p in [spec["title"], spec.get("close_path", "close_button")]}
    header |= set(spec.get("header_bg", [])) | set(spec.get("controls", {})) | {p.split(">")[0] for p in spec.get("attrs", {})}

    # 1. the game's content moves down (direct children only, last first so the offsets stay valid)
    kids = children(t, s, e)
    bg = next(((cs, ce) for cs, ce, kind in kids if kind == "background"), None)
    moved = []
    for cs, ce, kind in reversed(kids):
        if kind == "background":
            continue
        h0, rest = GP.own_region(t[cs:ce])
        name = attr(h0, "name")
        if name in header:
            continue
        ori = (attr(h0, "orientation") or "").upper()
        if ori not in TOP_ANCHORS:
            assert ori.startswith("LOWER") or ori == "CENTER_DOWN", (key, name, ori)
            continue
        x, y = pos_of(h0) or (0, 0)
        dy = spec.get("child_shift", {}).get(name, D)
        t = t[:cs] + with_position(h0, x, y + dy) + rest + t[ce:]
        moved.append(name)

    # 2. the window: flush under the band; closed, it rests at the game's off-screen x and it opens at once (sliding
    # in, it crossed the flag and the name: layout_politics.OPEN_MS); a fixed height grows by the shift
    win = dict(position=(hidden_x(head), LPN.TOP), show_position=(X, LPN.TOP))
    if re.search(r"animation_time\s*=", head):
        win["animation_time"] = LPN.OPEN_MS
    if spec.get("height"):
        win["size"] = (W, spec["height"] + D)
    t = GP.set_attrs(t, R, **win)
    s, e = window_span(t, R)
    kids = children(t, s, e)
    bg = next(((cs, ce) for cs, ce, kind in kids if kind == "background"), None)
    if bg:
        t = clear_background(t, *bg)

    # 3. the header: the game's pictures hidden, the title right of the notch, the close diamond, the controls
    for p in spec.get("header_bg", []):
        t = GP.set_attrs(t, f"{R}>{p}", sprite=NONE)
    for p in spec.get("clear", []):
        cs, ce = GP.find_block(t, f"{R}>{p}")
        b = next((bs, be) for bs, be, kind in children(t, cs, ce) if kind == "background")
        t = clear_background(t, *b)
    controls = spec.get("controls", {})
    close_x = HW - 52 if spec.get("close") is None else W + spec["close"][0]
    boxes = []                                   # (x, y) of each control right of the title's edge
    for p, xy in controls.items():
        cs, ce = GP.find_block(t, f"{R}>{p}")
        h0 = own_head(t, cs, ce)
        if xy is not None:
            t = GP.set_attrs(t, f"{R}>{p}", position=xy)
        else:
            xy = pos_of(h0) or (0, 0)
        ori = (attr(h0, "orientation") or "").upper()
        ax = W + xy[0] if ori.endswith("RIGHT") else xy[0]
        if ax > HX:
            boxes.append((ax, xy[1]))
    # the box runs to the close diamond or the first control on its row; the title takes one or two lines,
    # centred in the box, and no control may sit beside its lines (controls are taken as 36 px tall)
    tw = min([close_x] + [ax for ax, y in boxes if y < 40]) - 12 - HX
    text = LOC.get(attr(own_head(t, *GP.find_block(t, f"{R}>{spec['title']}")), "text") or "", "")
    font, lines = title_font(re.sub(r"§.|\$\w+\$", "", text) or key, tw, spec.get("title_lines", 2))
    lh = int(L.fnt(font)[2]["lineHeight"])
    ty0 = LPN.TITLE_Y + (LPN.TITLE_H - lh * len(lines)) / 2
    ty1 = ty0 + lh * len(lines)
    text_r = HX + max(L.measure(font, ln) for ln in lines)
    for ax, y in boxes:
        assert not (y < ty1 and y + 36 > ty0 and ax - 8 < text_r), (key, "a control beside the title", ax, y, lines)
    t = GP.set_attrs(t, f"{R}>{spec['title']}", position=(HX, LPN.TITLE_Y), font=font, maxWidth=tw,
                     maxHeight=LPN.TITLE_H, format="left", vertical_alignment="center")
    close = spec.get("close_path", "close_button")
    t = GP.set_attrs(t, f"{R}>{close}", sprite=CLOSE, position=spec.get("close", LPN.CLOSE))
    for p, kv in spec.get("attrs", {}).items():
        t = GP.set_attrs(t, f"{R}>{p}", **kv)
    # elements inside the content (moved down with it), changed where they are
    for p, kv in spec.get("inner_attrs", {}).items():
        t = GP.set_attrs(t, f"{R}>{p}", **kv)

    # 4. the panel's own layers, drawn under everything else: body, click-catchers, header picture
    body_h = f"{spec['height'] + D - LPN.NB}" if spec.get("height") else "100%%"
    layers = ("\n\t\t# ===== Valsora Deco: the panel below the header strip, invisible click-catchers beside the notch, "
              "the header picture =====")
    layers += snippet_container("valsora_deco_panel_body", 0, LPN.NB, W, body_h, BODY)
    for i, (x0, y0, x1, y1) in enumerate(LPN.blockers(HW, X)):
        layers += snippet_container(f"valsora_deco_panel_block_{i}", x0, y0, x1 - x0, y1 - y0, CLEAR)
    layers += snippet_icon("valsora_deco_panel_head", head_sprite(HW, X), 0, 0) + "\n"
    s, e = window_span(t, R)
    kids = children(t, s, e)
    bg = next(((cs, ce) for cs, ce, kind in kids if kind == "background"), None)
    at = bg[1] if bg else s + len(own_head(t, s, e))
    t = t[:at] + layers + t[at:]
    return t, dict(key=key, title=" / ".join(lines), font=font, title_w=tw, moved=moved, W=W, X=X)


def beside(t, names):
    for n in names:
        s, e = window_span(t, n)
        h = own_head(t, s, e)
        sx = int(re.search(r"show_position\s*=\s*\{\s*x\s*=\s*(-?\d+)", h).group(1))
        anim = dict(animation_time=LPN.OPEN_MS) if re.search(r"animation_time\s*=", h) else {}
        t = GP.set_attrs(t, n, position=(hidden_x(h), LPN.TOP), show_position=(sx, LPN.TOP), **anim)
    return t


if __name__ == "__main__":
    report = []
    files = {}
    for key, spec in LPN.PANELS.items():
        files.setdefault(spec["file"], []).append((key, spec))
    for f in sorted(set(files) | set(LPN.BESIDE)):
        t = open(os.path.join(VANILLA, "interface", f), encoding="utf-8-sig").read().replace("\r\n", "\n")
        for key, spec in files.get(f, []):
            t, info = panel(t, key, spec)
            report.append(info)
        t = beside(t, LPN.BESIDE.get(f, []))
        out = os.path.join(MOD, "interface", f)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        GP.write_gui(out, "# Valsora Deco UI (make_panels.py): the game's file, flush under the top bar with a notch for the "
                          "flag medallion; every element and name kept\n" + t)
    gfx = ["spriteTypes = {"]
    for w, x in LPN.HEADS:
        gfx.append(f'\tspriteType = {{\n\t\tname = "{head_sprite(w, x)}"\n\t\ttexturefile = "{head_texture(w, x)}"\n\t}}')
    gfx.append("}\n")
    with open(os.path.join(MOD, "interface", "valsora_deco_panels.gfx"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("# Valsora Deco UI (make_panels.py): the side panels' header pictures\n" + "\n".join(gfx))
    for r in report:
        print(f"{r['key']:14s} x {r['X']:3d} w {r['W']} | title {r['title']!r} ({r['font'][13:]}, box {r['title_w']}) | "
              f"moved {len(r['moved'])}")
