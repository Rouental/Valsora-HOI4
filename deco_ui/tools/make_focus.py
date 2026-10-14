"""Build interface/nationalfocusview.gui (the national focus tree window, art deco styling).

    python make_focus.py "<HOI4 install folder>"

The tree's geometry (focus spacing, links, the item size) is the game's; the chrome is restyled: header band
and gilt title, search box, zoom and close buttons, filter chips, tree background and vignette, a medallion
behind each focus icon, name plates (the game swaps GFX_focus_unavailable / _can_start / _completed by
state, so those textures are replaced at their vanilla paths by gen_textures.py), the detail pop-ups and a
legend. Focus icons are not touched. Every element and name of the game's file is kept.
"""
import os
import re
import sys

import guipatch as GP
import layout_focus as LF
from paths import MOD, VANILLA as VANILLA_DIR

ARG = sys.argv[1] if len(sys.argv) > 1 else VANILLA_DIR
src = os.path.join(ARG, "interface", "nationalfocusview.gui")
t = open(src, encoding="utf-8-sig").read().replace("\r\n", "\n")
D = "GFX_valsora_deco_nf_"
CLOSE = "GFX_valsora_deco_pol_close"
BODY13, BODY15, SECTION = "valsora_deco_body_13", "valsora_deco_body_15", "valsora_deco_section_11"


def at(path, **kw):
    global t
    t = GP.set_attrs(t, path, **kw)


R = "nationalfocusview"
# header band first, so everything draws over it
t = GP.insert_child(t, R, f"""
		# ===== Valsora Deco: header band (stretched to the window width; click-through) =====
		containerWindowType = {{
			name = "valsora_deco_nf_header"
			position = {{ x = 0 y = 0 }}
			size = {{ width = 100%% height = {LF.HEADER_H} }}
			clipping = no
			alwaystransparent = yes
			background = {{
				name = "valsora_deco_nf_header_bg"
				quadTextureSprite = "{D}header"
			}}
		}}""", first=True)
T = LF.TITLE
at(f"{R}>national_focus_title", font="valsora_deco_title_24", position=(T["x"], T["y"]), maxWidth=T["w"], maxHeight=T["h"])
at("find_view>find_editbox_bg", sprite=D + "search", position=(1, 1))
at("find_view>to_find_text", font=BODY13, position=(44, 9))
at("find_view>type_to_search_text", font=BODY13, position=(44, 13))
at("find_view>found_text", font=BODY13)
at("find_view>clear_search", sprite="GFX_valsora_deco_pol_close_small", position=(212, 21))
# the game's button names and sprites are crossed (zoom_out uses GFX_focus_zoom_in); the picture follows the sprite
at("zoom_slider_container>zoom_out", sprite=D + "zoom_in")
at("zoom_slider_container>zoom_in", sprite=D + "zoom_out")
at(f"{R}>close_button", sprite=CLOSE, position=LF.CLOSE)
# tree backgrounds: grid lacquer, then the vignette
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

# focus items: medallion behind the icon (before the plate), plate and name position
mx, my = round(LF.ICON_C[0] - LF.MEDALLION / 2), round(LF.ICON_C[1] - LF.MEDALLION / 2)
t = GP.insert_after(t, "national_focus_item>highlight_glow", f"""
		# Valsora Deco: medallion behind the focus icon
		iconType = {{
			name = "valsora_deco_nf_medallion"
			spriteType = "{D}medallion"
			position = {{ x = {mx} y = {my} }}
			alwaystransparent = yes
		}}""")
P, N = LF.PLATE, LF.NAME
at("national_focus_item>bg", position=(P["x"], P["y"]))
at("national_focus_item>name", position=(N["x"], N["y"]), font=BODY13, maxWidth=N["w"], maxHeight=N["h"])
at("continuous_national_focus_item>name", font=BODY13)

# filter chips (2 frames: off / on)
for c in ("focus_tree_filter_icon_container", "focus_tree_alternate_icon_button_container"):
    at(f"{c}>checkbox", sprite=D + "filter")
at("focus_tree_shortcut_item>name", font=BODY13)

# detail pop-ups
for v in ("national_focus_detail_view", "coninuous_focus_detail_view"):
    at(f"{v}>info_top_win", sprite="GFX_valsora_deco_none")
    at(f"{v}>close", sprite=CLOSE, position=(-46, 8))
    at(f"{v}>name", font="valsora_deco_title_18")
    at(f"{v}>prerequisites_bg", sprite=D + "prereq_bg")
    at(f"{v}>prerequisites", font=BODY13)
    at(f"{v}>desc", font=BODY15)
    at(f"{v}>reward_bg", sprite=D + "reward_bar", position=(84, 360))
    at(f"{v}>reward_label", font=SECTION)
    at(f"{v}>reward", font=BODY13)
    at(f"{v}>status", font=BODY13, maxHeight=16)

# legend, lower right (click-through)
L_ = LF.LEGEND
s_, e_ = GP.find_block(t, R)
close_at = t.rindex("}", s_, e_)
t = t[:close_at] + f"""
		# ===== Valsora Deco: legend of the plate colours =====
		iconType = {{
			name = "valsora_deco_nf_legend"
			spriteType = "{D}legend"
			position = {{ x = {L_['x']} y = {L_['y']} }}
			Orientation = "LOWER_RIGHT"
			alwaystransparent = yes
		}}
	""" + t[close_at:]

t = ("# Valsora Deco UI - national focus tree window (art deco styling). Generated by tools/make_focus.py from the\n"
     "# game's nationalfocusview.gui: every element and name is kept; the tree's geometry is unchanged.\n\n" + t)
GP.check(t)
open(MOD + "interface/nationalfocusview.gui", "w", encoding="utf-8", newline="\n").write(t)

TEX = "gfx/interface/valsora_deco/focus/"
gfx = "# Valsora Deco UI - focus tree sprites (generated by tools/make_focus.py)\nspriteTypes = {\n"
gfx += (f'\tcorneredTileSpriteType = {{\n\t\tname = "{D}header"\n\t\tsize = {{ x = 196 y = {LF.HEADER_H} }}\n'
        f'\t\ttextureFile = "{TEX}header.dds"\n\t\tborderSize = {{ x = 8 y = 4 }}\n\t}}\n')
gfx += (f'\tcorneredTileSpriteType = {{\n\t\tname = "{D}tree_bg"\n\t\tsize = {{ x = {LF.TREE_TILE} y = {LF.TREE_TILE} }}\n'
        f'\t\ttextureFile = "{TEX}tree_bg.dds"\n\t\tborderSize = {{ x = 64 y = 64 }}\n\t\ttilingCenter = yes\n\t}}\n')
gfx += (f'\tcorneredTileSpriteType = {{\n\t\tname = "{D}vignette"\n\t\tsize = {{ x = 512 y = 512 }}\n'
        f'\t\ttextureFile = "{TEX}vignette.dds"\n\t\tborderSize = {{ x = 255 y = 255 }}\n\t}}\n')
for name, tex, frames, eff in [("medallion", "medallion.dds", 1, None), ("search", "search.dds", 1, None),
                               ("zoom_in", "zoom_in.dds", 1, "buttonstate.lua"), ("zoom_out", "zoom_out.dds", 1, "buttonstate.lua"),
                               ("filter", "filter_chip.dds", 2, None), ("prereq_bg", "prereq_bg.dds", 1, None),
                               ("reward_bar", "reward_bar.dds", 1, None), ("legend", "legend.dds", 1, None)]:
    gfx += f'\tspriteType = {{\n\t\tname = "{D}{name}"\n\t\ttexturefile = "{TEX}{tex}"\n'
    if frames > 1:
        gfx += f"\t\tnoOfFrames = {frames}\n"
    if eff:
        gfx += f'\t\teffectFile = "gfx/FX/{eff}"\n'
    gfx += "\t}\n"
gfx += "}\n"
open(MOD + "interface/valsora_deco_focus.gfx", "w", encoding="utf-8", newline="\n").write(gfx)
print("nationalfocusview.gui written")
