"""Build interface/nationalfocusview.gui and .gfx (the national focus tree window, the FocusTree mockup, v0.6).

    python make_focus.py "<HOI4 install folder>"

The window opens flush under the top bar's band with the side panels' notch round the flag medallion and the
decisions seal (it is drawn over the top bar): its own background is clear and click-through, a header picture (a
cornered tile) draws the strip round the notch, invisible containers beside the notch catch clicks. In the header:
a small "National Focus" label, then the game's own title (the tree's name, which the game sets) in large gilt
capitals, the filter chips, the search box, zoom and close. The tree keeps the game's geometry (focus spacing, links); its background is the mockup's scale pattern
in a gilt frame. Each focus is a medallion and a plate: the game's "bg" button, whose sprite the game swaps by
state, so the four pictures are replaced (gen_textures.py) and GFX_focus_current, which the game draws from the
can-start picture with two animations, gets a picture of its own in the game's nationalfocusview.gfx, copied here
with that one sprite changed. The halo behind the focus in progress, the search highlight, the links and the marks
between mutually exclusive focuses are the game's sprites with new pictures. Focus icons are not touched. Every
element and name of the game's file is kept.
"""
import os
import re
import sys

import guipatch as GP
import layout_focus as LF
import layout_panels as LPN
from paths import MOD, VANILLA as VANILLA_DIR

ARG = sys.argv[1] if len(sys.argv) > 1 else VANILLA_DIR
src = os.path.join(ARG, "interface", "nationalfocusview.gui")
t = open(src, encoding="utf-8-sig").read().replace("\r\n", "\n")
D = "GFX_valsora_deco_nf_"
CLEAR = "GFX_valsora_deco_clear"
CLOSE = "GFX_valsora_deco_pol_close"
BODY13, BODY15, SECTION = "valsora_deco_body_13", "valsora_deco_body_15", "valsora_deco_section_11"
TEX = "gfx/interface/valsora_deco/focus/"


def at(path, **kw):
    global t
    t = GP.set_attrs(t, path, **kw)


R = "nationalfocusview"
# ---------------------------------------------------------------- the window: flush under the band, notched
at(R, position=(LF.WIN_X, LF.TOP))
t = GP.set_background(t, R, CLEAR)
s_, e_ = GP.find_block(t, R)
blk = t[s_:e_]
blk, n = re.subn(r'(background\s*=\s*\{[^{}]*?quadTextureSprite\s*=\s*"' + CLEAR + '")', r'\1\n\t\t\talwaystransparent = yes',
                 blk, count=1)
assert n == 1, "the focus window's background was not made click-through"
t = t[:s_] + blk + t[e_:]


def container(name, x, y, w, h, sprite, transparent):
    tr = "\n\t\t\talwaystransparent = yes" if transparent else ""
    return (f'\n\t\tcontainerWindowType = {{\n\t\t\tname = "{name}"\n\t\t\tposition = {{ x = {x} y = {y} }}\n'
            f'\t\t\tsize = {{ width = {w} height = {h} }}\n\t\t\tclipping = no\n'
            f'\t\t\tbackground = {{\n\t\t\t\tname = "{name}_bg"\n\t\t\t\tquadTextureSprite = "{sprite}"{tr}\n\t\t\t}}\n\t\t}}')


# first children, so the game's elements draw over them: click-catchers beside the notch (the window's own
# background no longer catches clicks there), one under it to the tree, then the header picture (click-through)
layers = ""
for i, (x0, y0, x1, y1) in enumerate(LPN.blockers(100000, LF.WIN_X)):
    w = "100%%" if x1 >= 100000 else x1 - x0
    layers += container(f"valsora_deco_nf_block_{i}", x0, y0, w, y1 - y0, CLEAR, False)
layers += container("valsora_deco_nf_block_foot", 0, LPN.NB, "100%%", LF.TREE_Y - LPN.NB, CLEAR, False)
layers += container("valsora_deco_nf_header", 0, 0, "100%%", LF.HEAD_H, D + "header", True)
t = GP.insert_child(t, R, "\n\t\t# ===== Valsora Deco: the click-catchers beside the notch and the header picture =====" + layers,
                    first=True)

# ---------------------------------------------------------------- the header
K, T_ = LF.KICKER, LF.TITLE
at(f"{R}>national_focus_title", font="valsora_deco_title_30", position=(T_["x"], T_["y"]), maxWidth=T_["w"],
   maxHeight=T_["h"])
t = GP.insert_after(t, f"{R}>national_focus_title", f"""
		instantTextboxType = {{
			name = "valsora_deco_nf_kicker"
			position = {{ x = {K['x']} y = {K['y']} }}
			font = "{SECTION}"
			text = "VAL_DECO_NF_KICKER"
			maxWidth = {K['w']}
			maxHeight = {K['h']}
			format = left
			alwaystransparent = yes
		}}""")
at("find_view", position=LF.FIND)
at("find_view>find_editbox_bg", sprite=D + "search", position=(1, 1))
at("find_view>to_find_text", font=BODY13, position=(44, 9))
at("find_view>type_to_search_text", font=BODY13, position=(44, 13))
at("find_view>found_text", font=BODY13)
at("find_view>clear_search", sprite="GFX_valsora_deco_pol_close_small", position=(212, 21))
at("zoom_slider_container", position=LF.ZOOM)
# the game's button names and sprites are crossed (zoom_out uses GFX_focus_zoom_in); the picture follows the sprite
at("zoom_slider_container>zoom_out", sprite=D + "zoom_in")
at("zoom_slider_container>zoom_in", sprite=D + "zoom_out")
at(f"{R}>close_button", sprite=CLOSE, position=LF.CLOSE)
at(f"{R}>filter_container", position=LF.FILTERS)
s_, e_ = GP.find_block(t, f"{R}>filter_grid_main_container")
x_ = int(re.search(r"position\s*=\s*\{\s*x\s*=\s*(-?\d+)", GP.own_region(t[s_:e_])[0]).group(1))
at(f"{R}>filter_grid_main_container", position=(x_, LF.FILTER_DROPDOWN_Y))
# the filter's icon centred in the chip (v0.11, the author: "Icons aren't centered in the bubbles on the focus tree"):
# the game's 27 px icons at its (8, 7) were placed for its own chip; in ours (LF.FILTER, 36 px) their ink, centred at
# (13, 14) in the picture (the author's screenshot), was 3 px right of the octagon's middle and 3 px under it
for c in ("focus_tree_filter_icon_container", "focus_tree_alternate_icon_button_container"):
    at(f"{c}>checkbox", sprite=D + "filter")
    at(f"{c}>icon", position=LF.FILTER_ICON)
at("focus_tree_shortcut_item>name", font=BODY13)

# ---------------------------------------------------------------- the tree: below the header, scales in a frame
at(f"{R}>tree", position=(0, LF.TREE_Y))
s_, e_ = GP.find_block(t, f"{R}>tree")
blk = t[s_:e_]
blk, n1 = re.subn(r'"GFX_tiled_bg"', f'"{D}tree_bg"', blk, count=1)
blk, n2 = re.subn(r'"GFX_tiled_focus_bg"', f'"{D}vignette"', blk, count=1)
assert n1 == n2 == 1
t = t[:s_] + blk + t[e_:]
at("search_tooltip>tooltip_text", font=BODY15)
at("continuous_focus_window>continuous_focus_title", font="valsora_deco_title_18")
at("continuous_focus_window>continuous_focus_desc", font=BODY13)
at("focus_progress_window>continuous_focus_progress", font=BODY15)

# ---------------------------------------------------------------- a focus: medallion and plate (the bg button)
B, N = LF.BG, LF.NAME
at("national_focus_item>bg", position=(B["x"], B["y"]))
at("national_focus_item>name", position=(N["x"], N["y"]), font=BODY13, maxWidth=N["w"], maxHeight=N["h"])
hx, hy = round(LF.ICON_C[0] - LF.HALO / 2 - .5), round(LF.ICON_C[1] - LF.HALO / 2)
for g in ("continuous_glow", "highlight_glow"):          # the in-progress halo and the search highlight
    at(f"national_focus_item>{g}", position=(hx, hy))
at("continuous_national_focus_item>name", font=BODY13)

# ---------------------------------------------------------------- detail pop-ups
for v in ("national_focus_detail_view", "coninuous_focus_detail_view"):
    at(f"{v}>info_top_win", sprite="GFX_valsora_deco_none")
    at(f"{v}>close", sprite=CLOSE, position=(-46, 8))
    at(f"{v}>name", font="valsora_deco_title_18")
    at(f"{v}>prerequisites_bg", sprite=D + "prereq_bg")
    at(f"{v}>prerequisites", font=BODY13)
    at(f"{v}>desc", font="valsora_deco_italic_15")
    at(f"{v}>reward_bg", sprite=D + "reward_bar", position=(84, 360))
    at(f"{v}>reward_label", font=SECTION)
    at(f"{v}>reward", font=BODY13)
    at(f"{v}>status", font=BODY13, maxHeight=16)

# ---------------------------------------------------------------- legend, lower right (click-through)
L_ = LF.LEGEND
s_, e_ = GP.find_block(t, R)
close_at = t.rindex("}", s_, e_)
t = t[:close_at] + f"""
		# ===== Valsora Deco: legend of the focus marks =====
		iconType = {{
			name = "valsora_deco_nf_legend"
			spriteType = "{D}legend"
			position = {{ x = {L_['x']} y = {L_['y']} }}
			Orientation = "LOWER_RIGHT"
			alwaystransparent = yes
		}}
	""" + t[close_at:]

t = ("# Valsora Deco UI - national focus tree window (the FocusTree mockup). Generated by tools/make_focus.py from the\n"
     "# game's nationalfocusview.gui: every element and name is kept; the tree's geometry is unchanged.\n\n" + t)
GP.check(t)
GP.write_gui(MOD + "interface/nationalfocusview.gui", t)

# ---------------------------------------------------------------- the kicker's text (the title is the game's own)
# the scripted GUI of v0.6-v0.8.3 (valsora_deco_focus_extras.gui, common/scripted_guis/valsora_deco_focus.txt) is gone:
# docked to national_focus, the game put it inside the tree's scrolling canvas
for old in ("interface/valsora_deco_focus_extras.gui", "common/scripted_guis/valsora_deco_focus.txt"):
    if os.path.exists(MOD + old):
        os.remove(MOD + old)
for lang in ["english", "french", "german", "spanish", "braz_por", "polish", "russian", "japanese", "simp_chinese"]:
    d = MOD + f"localisation/{lang}/"
    os.makedirs(d, exist_ok=True)
    open(d + f"valsora_deco_focus_l_{lang}.yml", "w", encoding="utf-8-sig", newline="\n").write(
        f'l_{lang}:\n VAL_DECO_NF_KICKER:0 "National Focus"\n')

# ---------------------------------------------------------------- the game's focus sprites: the in-progress plate
# The game draws a focus in progress with GFX_focus_current, which is the can-start picture with two rotating
# shines. It gets its own picture (the mockup's red medallion); its shines are dropped, since the halo behind the
# focus (GFX_ongoing_focus_goal) is the mark of a focus in progress here. Everything else is the game's file.
gsrc = os.path.join(ARG, "interface", "nationalfocusview.gfx")
g = open(gsrc, encoding="utf-8-sig").read().replace("\r\n", "\n")
m = re.search(r'\n(\s*)SpriteType\s*=\s*\{\s*\n\s*name\s*=\s*"GFX_focus_current"', g)
assert m, "GFX_focus_current not found in the game's nationalfocusview.gfx"
start = m.start() + 1
depth, i = 0, g.index("{", start)
while True:
    depth += {"{": 1, "}": -1}.get(g[i], 0)
    i += 1
    if depth == 0:
        break
g = (g[:start] + f'\tSpriteType = {{\n\t\tname = "GFX_focus_current"\n\t\ttexturefile = "{TEX}current_bg.dds"\n'
     '\t\teffectFile = "gfx/FX/buttonstate_onlydisable.lua"\n\t\tlegacy_lazy_load = no\n\t}' + g[i:])
open(MOD + "interface/nationalfocusview.gfx", "w", encoding="utf-8", newline="\n").write(
    "# Valsora Deco UI: the game's nationalfocusview.gfx, with GFX_focus_current given its own picture (tools/make_focus.py)\n" + g)

# ---------------------------------------------------------------- our sprites
gfx = "# Valsora Deco UI - focus tree sprites (generated by tools/make_focus.py)\nspriteTypes = {\n"
gfx += (f'\tcorneredTileSpriteType = {{\n\t\tname = "{D}header"\n\t\tsize = {{ x = {LF.HEAD_TILE_W} y = {LF.HEAD_H} }}\n'
        f'\t\ttextureFile = "{TEX}header.dds"\n\t\tborderSize = {{ x = {LF.HEAD_TILE_B} y = {LF.HEAD_H // 2} }}\n'
        '\t\ttilingCenter = yes\n\t}\n')
gfx += (f'\tcorneredTileSpriteType = {{\n\t\tname = "{D}tree_bg"\n\t\tsize = {{ x = {LF.TREE_TILE} y = {LF.TREE_TILE} }}\n'
        f'\t\ttextureFile = "{TEX}tree_bg.dds"\n\t\tborderSize = {{ x = 64 y = 64 }}\n\t\ttilingCenter = yes\n\t}}\n')
gfx += (f'\tcorneredTileSpriteType = {{\n\t\tname = "{D}vignette"\n\t\tsize = {{ x = 512 y = 512 }}\n'
        f'\t\ttextureFile = "{TEX}vignette.dds"\n\t\tborderSize = {{ x = 255 y = 255 }}\n\t}}\n')
for name, tex, frames, eff in [("search", "search.dds", 1, None), ("zoom_in", "zoom_in.dds", 1, "buttonstate.lua"),
                               ("zoom_out", "zoom_out.dds", 1, "buttonstate.lua"), ("filter", "filter_chip.dds", 2, None),
                               ("prereq_bg", "prereq_bg.dds", 1, None), ("reward_bar", "reward_bar.dds", 1, None),
                               ("legend", "legend.dds", 1, None)]:
    gfx += f'\tspriteType = {{\n\t\tname = "{D}{name}"\n\t\ttexturefile = "{TEX}{tex}"\n'
    if frames > 1:
        gfx += f"\t\tnoOfFrames = {frames}\n"
    if eff:
        gfx += f'\t\teffectFile = "gfx/FX/{eff}"\n'
    gfx += "\t}\n"
gfx += "}\n"
open(MOD + "interface/valsora_deco_focus.gfx", "w", encoding="utf-8", newline="\n").write(gfx)
print("nationalfocusview.gui and .gfx written")
