"""Build interface/countrystateview.gui (the state / province panel that opens when a province is clicked).

    python make_stateview.py "<HOI4 install folder>"

v0.4: the mockup's arrangement for the state part (owner flag and name in the header, a stats row, shared
building slots, state buildings, claims / resistance); the province part keeps the game's arrangement.
New background, building tiles, level plates, close diamond, labels and fonts. Every element and name of
the game's file is kept. Layout notes in layout_stateview.py.
"""
import os
import sys

import re

import guipatch as GP
import layout_stateview as LS
from paths import MOD, VANILLA as VANILLA_DIR

ARG = sys.argv[1] if len(sys.argv) > 1 else VANILLA_DIR
src = os.path.join(ARG, "interface", "countrystateview.gui")
t = open(src, encoding="utf-8-sig").read().replace("\r\n", "\n")
D = "GFX_valsora_deco_sv_"
TITLE, LABEL, SECTION = "valsora_deco_title_18", "valsora_deco_label", "valsora_deco_section_11"
BODY13, BODY15, VALUE15, VALUE12 = "valsora_deco_body_13", "valsora_deco_body_15", "valsora_deco_value_15", "valsora_deco_value_12"


def at(path, **kw):
    global t
    t = GP.set_attrs(t, path, **kw)


def new_text(name, loc, font, x, y, w, h):
    return (f'\n\t\t\tinstantTextboxType = {{\n\t\t\t\tname = "{name}"\n\t\t\t\tposition = {{ x = {x} y = {y} }}\n'
            f'\t\t\t\tfont = "{font}"\n\t\t\t\ttext = "{loc}"\n\t\t\t\tformat = left\n\t\t\t\tmaxWidth = {w}\n'
            f'\t\t\t\tmaxHeight = {h}\n\t\t\t\tfixedsize = yes\n\t\t\t\talwaystransparent = yes\n\t\t\t}}')


W = "state_info_window"
t = GP.set_background(t, f"countrystateview>{W}", D + "bg")
# header: owner flag(s), state name, owner as a subtitle, close
at(f"{W}>state_owners", position=LS.OWNERS)
at(f"{W}>controller_flag", position=LS.CONTROLLER)
at(f"{W}>controller_flag_border", position=(LS.CONTROLLER[0] - 5, LS.CONTROLLER[1] - 4))
N, ST = LS.NAME, LS.SUBTITLE
at(f"{W}>state_name", font=TITLE, position=(N["x"], N["y"]), maxWidth=N["w"], maxHeight=N["h"], format="left")
at(f"{W}>owner", font=BODY13, position=(ST["x"], ST["y"]), maxWidth=ST["w"], maxHeight=ST["h"], format="left")
at("countrystateview>close_button", sprite="GFX_valsora_deco_pol_close", position=LS.CLOSE)
# stats row: victory points | manpower | resources
c0, c1, c2 = LS.STAT_COLS
at(f"{W}>victory_points_bg", sprite="GFX_valsora_deco_none")
at(f"{W}>victory_points", font=VALUE15, position=(c0, LS.STAT_VALUE_Y), maxWidth=120, format="left")
at(f"{W}>population_icon", position=(LS.POP_ICON["x"], LS.POP_ICON["y"]), scale=LS.POP_ICON["scale"])
at(f"{W}>manpower", font=VALUE15, position=(LS.MANPOWER_X, LS.STAT_VALUE_Y), maxWidth=100, format="left")
R_ = LS.RESOURCES
at(f"{W}>state_resources", position=(R_["x"], R_["y"]), size=(R_["w"], R_["h"]))
# shared building slots
SL = LS.SHARED_LABEL
at(f"{W}>shared_slot_count", font=SECTION, position=(SL["x"], SL["y"]), maxWidth=SL["w"], maxHeight=SL["h"])
ex, ey = LS.ENERGY["x"], LS.ENERGY["y"]
at(f"{W}>energy_consumption_bg", sprite=D + "chip", position=(ex, ey))
at(f"{W}>energy_icon", position=(ex + 14, ey - 3))
at(f"{W}>energy_text", font=VALUE12, position=(ex - 4, ey + 5))
G = LS.SHARED_GRID
at(f"{W}>state_shared_slot_building_entries", position=(G["x"], G["y"]), max_slots_horizontal=G["cols"],
   max_slots_vertical=G["rows"])
# state buildings
B = LS.BUILD_GRID
at(f"{W}>state_building_entries", position=(B["x"], B["y"]), max_slots_horizontal=7)
# claims (left) and resistance / compliance (right, occupied states)
CT = LS.CLAIMS_TEXT
at(f"{W}>claims", font=BODY13, position=(CT["x"], CT["y"]), maxWidth=CT["w"], maxHeight=CT["h"], format="left")
at(f"{W}>state_claims", position=LS.CLAIMS_FLAGS)
at(f"{W}>resistance_container", position=LS.RESISTANCE)
for row, (icon, pos) in enumerate((("state_resistance_icon", "resistance_status_pos"),
                                   ("state_compliance_icon", "compliance_status_pos"))):
    at(f"{W}>resistance_container>{icon}", position=(0, row * LS.RES_ROW), scale=str(LS.RES_SCALE))
    at(f"{W}>resistance_container>{pos}", position=(LS.RES_BAR_X, row * LS.RES_ROW + 1))
# labels the game does not have
added = "\n\t\t\t# ===== Valsora Deco: section labels ====="
for key, x, y in [("VICTORY_POINTS", c0, LS.STAT_LABEL_Y), ("MANPOWER", c1, LS.STAT_LABEL_Y),
                  ("RESOURCES", c2, LS.STAT_LABEL_Y)]:
    added += new_text(f"valsora_deco_sv_label_{key.lower()}", f"VAL_DECO_SV_{key}", LABEL, x, y, 130, 12)
BL = LS.BUILD_LABEL
added += new_text("valsora_deco_sv_label_buildings", "VAL_DECO_SV_BUILDINGS", SECTION, BL["x"], BL["y"], BL["w"], BL["h"])
t = GP.insert_after(t, f"{W}>state_name", added)

# building entries: deco tiles, level plates, fonts
for tpl in ("state_building_entry", "province_building_entry"):
    t = GP.set_background(t, tpl, D + "tile")
    _, ly = GP.get_pos(t, f"{tpl}>level_bg")
    at(f"{tpl}>level_bg", sprite=D + "level", position=(LS.LEVEL_X, ly))
    # the number centred on the plate: its box (maxWidth) about the tile's middle
    lw = int(re.search(r"maxWidth\s*=\s*(\d+)", GP.own_region(t[slice(*GP.find_block(t, f"{tpl}>level"))])[0]).group(1))
    _, ty = GP.get_pos(t, f"{tpl}>level")
    at(f"{tpl}>level", font=VALUE15, position=(LS.TILE["w"] // 2 - lw // 2, ty))
    at(f"{tpl}>building_picture", position=LS.PICTURE)
    at(f"{tpl}>damage_bar", position=LS.DAMAGE, rotation=0)
at("state_shared_slot_building_entry>build_slot_bg", sprite=D + "slot", position=(LS.SLOT["x"], LS.SLOT["y"]))
at("state_shared_slot_building_entry>damage_bar", position=LS.SLOT_DAMAGE, rotation=0)
at("state_resource_entry>amount", font=VALUE12)
at("province_info_window>province", font=BODY15, position=(0, -27))
at("province_info_window>state_modifiers", font=SECTION)
at("law_and_template_container>template_need_text", font=BODY13)
for c in ("state_compliance_status_container", "state_resistance_status_container"):
    at(f"{c}>progress_text", font=VALUE12)

t = ("# Valsora Deco UI - state / province panel (art deco, the mockup's arrangement for the state part).\n"
     "# Generated by tools/make_stateview.py from the game's countrystateview.gui: every element and name is kept.\n\n" + t)
GP.check(t)
GP.write_gui(MOD + "interface/countrystateview.gui", t)

TEX = "gfx/interface/valsora_deco/stateview/"
gfx = "# Valsora Deco UI - state panel sprites (generated by tools/make_stateview.py)\nspriteTypes = {\n"
for name, tex in [("bg", "stateview_bg.dds"), ("tile", "building_tile.dds"), ("slot", "slot.dds"),
                  ("level", "level.dds"), ("chip", "chip.dds")]:
    gfx += f'\tspriteType = {{\n\t\tname = "{D}{name}"\n\t\ttexturefile = "{TEX}{tex}"\n\t}}\n'
gfx += "}\n"
open(MOD + "interface/valsora_deco_stateview.gfx", "w", encoding="utf-8", newline="\n").write(gfx)

LOC = {"VAL_DECO_SV_VICTORY_POINTS": "Victory Points", "VAL_DECO_SV_MANPOWER": "Manpower",
       "VAL_DECO_SV_RESOURCES": "Resources", "VAL_DECO_SV_BUILDINGS": "State Buildings"}
for lang in ["english", "french", "german", "spanish", "braz_por", "polish", "russian", "japanese", "simp_chinese"]:
    d = MOD + f"localisation/{lang}/"
    os.makedirs(d, exist_ok=True)
    open(d + f"valsora_deco_stateview_l_{lang}.yml", "w", encoding="utf-8-sig", newline="\n").write(
        f"l_{lang}:\n" + "".join(f' {k}:0 "{v}"\n' for k, v in LOC.items()))
print("countrystateview.gui written")
