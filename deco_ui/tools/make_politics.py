"""Build interface/countrypoliticsview.gui (art deco politics screen, v0.4: the Government mockup's layout).

    python make_politics.py "<HOI4 install folder>" ["<Valsora mod folder>"]

Base file: the Valsora mod's own interface/countrypoliticsview.gui when it has one (so its edits are kept),
otherwise the game's. Every element and name is kept; positions, sprites and fonts change, and the mod adds
labels, the ribbon and the section art. What the game's screen does not provide is drawn by small scripted
GUIs docked to the politics window (common/scripted_guis/valsora_deco_politics.txt):

  title        the country's full name                     [ROOT.GetNameDefCap]
  info         ruling party + its popularity, last election, political power and its daily change
  description  the leader's description (from the Valsora characters' country_leader desc), or an ornament
  laws         the current conscription / economy / trade law (scripted localisation over the law ideas)
  faction role "Leader" / "Member"

Positions come from layout_politics.py. Also writes the scripted GUIs, scripted localisation, the trigger
for "has a description", the sprites (.gfx) and the localisation.
"""
import os
import re
import sys

import guipatch as GP
import layout_politics as LP
from paths import MOD, VANILLA as VANILLA_DIR, VALSORA as VALSORA_DIR

ARG = sys.argv[1] if len(sys.argv) > 1 else VANILLA_DIR
VALSORA = sys.argv[2] if len(sys.argv) > 2 else VALSORA_DIR
base = os.path.join(VALSORA, "interface", "countrypoliticsview.gui")
if not os.path.isfile(base):
    base = os.path.join(ARG, "interface", "countrypoliticsview.gui")
t = open(base, encoding="utf-8-sig").read().replace("\r\n", "\n")
t = t.replace("y = 1s }", "y = 1 }")      # vanilla typo in the pie overlay's position

R = "countrypoliticsview"
NONE = "GFX_valsora_deco_none"
D = "GFX_valsora_deco_pol_"
LABEL, SECTION, HEADING = "valsora_deco_label", "valsora_deco_section_11", "valsora_deco_heading_24"
BODY15, BODY13, VALUE15, VALUE12 = "valsora_deco_body_15", "valsora_deco_body_13", "valsora_deco_value_15", "valsora_deco_value_12"
ITALIC = "valsora_deco_italic_13"


def at(path, **kw):
    global t
    t = GP.set_attrs(t, path, **kw)


def new_icon(name, sprite, x, y):
    return (f'\n\t\ticonType = {{\n\t\t\tname = "{name}"\n\t\t\tspriteType = "{sprite}"\n'
            f'\t\t\tposition = {{ x = {x} y = {y} }}\n\t\t\tOrientation = "UPPER_LEFT"\n\t\t\talwaystransparent = yes\n\t\t}}')


def new_text(name, text, font, x, y, w, h, fmt="left", valign=True):
    va = "\n\t\t\tvertical_alignment = center" if valign else ""
    return (f'\n\t\tinstantTextboxType = {{\n\t\t\tname = "{name}"\n\t\t\tposition = {{ x = {x} y = {y} }}\n'
            f'\t\t\tfont = "{font}"\n\t\t\ttext = "{text}"\n\t\t\tformat = {fmt}\n\t\t\tmaxWidth = {w}\n'
            f'\t\t\tmaxHeight = {h}\n\t\t\tfixedsize = yes{va}\n\t\t\talwaystransparent = yes\n\t\t}}')


# ---------------------------------------------------------------- header
at(f"{R}>production_header_bg", sprite=NONE)
H = LP.HEAD_LABEL
at(f"{R}>political_title", position=(H["x"], H["y"]), font=LABEL, maxWidth=H["w"], maxHeight=H["h"],
   text="VAL_DECO_POL_GOVERNMENT")
at(f"{R}>close_button", sprite=D + "close", position=(LP.CLOSE["x"], LP.CLOSE["y"]))
at(f"{R}>rules", position=LP.RULES)
at(f"{R}>pol_view_bg", sprite=D + "sections", position=(0, 0))

# ---------------------------------------------------------------- head of state
at(f"{R}>leader", position=(LP.PORTRAIT["x"], LP.PORTRAIT["y"]))
at(f"{R}>leader_frame2", sprite=D + "frame", position=(LP.FRAME["x"], LP.FRAME["y"]))
N = LP.LEADER_NAME
at(f"{R}>leader_name", position=(N["x"], N["y"]), font=HEADING, maxWidth=N["w"], maxHeight=N["h"], format="left",
   fixedsize="yes")
rb = LP.RIBBON
added = "\n\t\t# ===== Valsora Deco: ribbon, labels (static text; the values are scripted GUIs or the game's own) ====="
added += new_icon("valsora_deco_pol_ribbon", D + "ribbon", rb["x"], rb["y"])
added += new_text("valsora_deco_pol_head_of_state", "VAL_DECO_POL_HEAD_OF_STATE", LABEL, rb["x"], rb["y"] + 4, rb["w"],
                  rb["h"] - 8, "centre")
for i, key in enumerate(["RULING_PARTY", "ELECTIONS", "LAST_ELECTION", "POLITICAL_POWER"]):
    col, row = i % 2, i // 2
    added += new_text(f"valsora_deco_pol_label_{key.lower()}", f"VAL_DECO_POL_{key}", LABEL, LP.GRID_X[col],
                      LP.GRID_LABEL_Y[row], LP.GRID_W[col], 12, valign=False)
for key, (x, y, _) in LP.SECTION_LABELS.items():
    if key == "spirits":
        continue   # the game's own "National Spirits" title is restyled instead
    added += new_text(f"valsora_deco_pol_section_{key}", f"VAL_DECO_POL_SECTION_{key.upper()}", SECTION, x, y, 200, 12,
                      valign=False)
for i, (key, _) in enumerate(LP.LAW_CARDS):
    y = LP.LAW_Y0 + i * (LP.LAW_H + LP.LAW_GAP)
    added += new_text(f"valsora_deco_pol_law_{key}", f"VAL_DECO_POL_LAW_{key.upper()}", LABEL, LP.LAWS_X + 40, y + 4,
                      LP.LAWS_W - 46, 10, valign=False)
t = GP.insert_after(t, f"{R}>leader_name", added)

# ideology chip: the game's ideology icon (small) and ideology text
at(f"{R}>pol_faction_icon", position=(LP.CHIP_ICON["x"], LP.CHIP_ICON["y"]), scale=LP.CHIP_ICON["scale"])
at(f"{R}>ruling_party_info", position=(0, 0), size=(LP.PANEL_W, 60))
CT = LP.CHIP_TEXT
at("ruling_party_info>ideology", position=(CT["x"], CT["y"]), font=LABEL, maxWidth=CT["w"], maxHeight=CT["h"],
   fixedsize="yes", format="left")
# elections: the game's own text in the grid's second cell
at("ruling_party_info>elections", position=(LP.GRID_X[1], LP.GRID_VALUE_Y[0]), font=BODY13, maxWidth=LP.GRID_W[1],
   maxHeight=LP.GRID_VALUE_H, vertical_alignment="top")
at("ruling_party_info>power_balance_button", position=(LP.BOP["x"], LP.BOP["y"]))

# ---------------------------------------------------------------- faction card
FC = LP.FACTION_CARD
at("ruling_party_info>faction", position=(FC["x"], FC["y"]), size=(FC["w"], FC["h"]))
at("no_faction>new_faction_button", sprite=D + "faction_card", position=(0, 0))
at("no_faction>create_faction_icon", position=(12, 25))
at("no_faction>view_factions_text", position=(48, 30), font=BODY15, maxWidth=140)
at("faction>view_factions_button", position=(FC["w"] - 42, 23))
at("faction>view_faction_icon", position=(FC["w"] - 41, 25))
at("original_in_faction>faction_name", position=(54, 31), font=BODY15, maxWidth=136)
at("original_in_faction>dismantle_faction", position=(FC["w"] - 36, 6))
at("in_faction>open_faction_button", sprite=D + "faction_card", position=(0, 0))
at("in_faction>faction_icon", position=(9, 20), scale="1.0")
at("in_faction>faction_name_position", position=(54, 39))
at("in_faction>faction_name", font=BODY15, maxWidth=136)

# ---------------------------------------------------------------- popularity: pie in a gilt ring, legend
pc, ring = LP.PIE, LP.PIE_RING
R_ = pc["r"] + ring
at(f"{R}>political_pie_chart", position=(pc["cx"] - R_, pc["top"] - ring), size=(2 * R_, 2 * R_))
at("political_pie_chart>chart", sprite="GFX_valsora_deco_pol_chart", position=(R_, ring))
at("political_pie_chart>pol_view_bg", sprite=D + "pie_ring", position=(0, 0))
at(f"{R}>chart_explanation", position=(0, 0))
LG = LP.LEGEND
at("chart_explanation>parties_grid", position=(LG["x"], LG["y"]), slotsize=(LG["w"], LG["row"]))
at("political_party_info_entry", size=(LG["w"], LG["row"]))
at("political_party_info_entry>leading_pol_party_bg", sprite=D + "party_lead", position=(0, 0))
at("political_party_info_entry>color_block_bg", sprite=D + "party_swatch_bg", position=(0, 1))
at("political_party_info_entry>color_block", sprite=D + "party_diamond", position=(2, 3))
at("political_party_info_entry>name", position=(20, 2), font=BODY13, maxWidth=LG["w"] - 22, maxHeight=16)

# ---------------------------------------------------------------- national focus card
F = LP.FOCUS_CARD
at(f"{R}>active_goal", position=(F["x"], F["y"]), size=(F["w"], F["h"]))
t = GP.set_background(t, f"{R}>active_goal", "GFX_valsora_deco_clear")
at("active_goal>add_national_goal_button", sprite=D + "focus_card", position=(0, 0))
at("active_goal>nat_spirit_glow_overlay", sprite=D + "focus_glow", position=(-6, -6))
FI = LP.FOCUS_ICON
k = FI["scale"]
at("active_goal>goal_icon", position=(FI["cx"], FI["cy"]), scale=k)
at("active_goal>continuous_glow", position=(FI["cx"] + round(-63 * k), FI["cy"] + round(-54 * k)), scale=round(0.9 * k, 2))
at("active_goal>continuous_small_glow", position=(4, 4))
at("active_goal>drop_continuous_focus_button", sprite=D + "close_small", position=(F["w"] - 26, 6), scale="1.0")
at("active_goal>drop_focus_button", sprite=D + "close_small", position=(F["w"] - 26, 6), scale="1.0")
FT = LP.FOCUS_TITLE
at("active_goal>title", font=BODY13, position=(FT["x"], FT["y"]), maxWidth=FT["w"], maxHeight=FT["h"], format="left")
at("active_goal>progress", sprite="GFX_valsora_deco_pol_focus_bar", position=(LP.FOCUS_BAR["x"], LP.FOCUS_BAR["y"]))
at("active_goal>progress_frame", sprite=NONE)
FCo = LP.FOCUS_COST
at("active_goal>pol_power_icon", position=(FCo["x"], FCo["y"]), scale="0.55")
at("active_goal>focus_cost", position=(FCo["x"] + 18, FCo["y"] + 1), font=VALUE12, maxWidth=60, maxHeight=14)

# ---------------------------------------------------------------- national spirits
SP = LP.SPIRITS
at(f"{R}>national_spirit", position=(SP["x"], LP.SPIRITS_LABEL_Y), size=(SP["w"], SP["h"] + SP["y"] - LP.SPIRITS_LABEL_Y))
at("national_spirit>title", position=(0, 0), font=SECTION, maxWidth=220, maxHeight=12)
at("national_spirit>national_spirit_container", position=(0, SP["y"] - LP.SPIRITS_LABEL_Y), size=(SP["w"], SP["h"]))
at("national_spirit_container>spirit_grid", position=(6, 2), size=(SP["w"] - 12, 68), max_slots=(8, 1))
at("national_spirit_container>spirit_grid_over_defined", position=(8, 2), size=(SP["w"] - 16, 68),
   max_slots_horizontal=15)

# ---------------------------------------------------------------- management buttons
Y, BX, BH = LP.BUTTONS_Y, LP.BUTTON_X, LP.BUTTON["h"]
at(f"{R}>politics_bottom", sprite=D + "strip", position=(LP.STRIP["x"], LP.STRIP["y"]), scale="1.0")
at(f"{R}>tutorial_glow", position=(BX[0], Y))
at(f"{R}>manage_occupied_button", sprite=D + "button", position=(BX[0], Y))
at(f"{R}>icon_occupied_territories", position=(BX[0] + 3, Y - 2))
at(f"{R}>manage_occupied_button_text", position=(BX[0] + 36, Y + 6), font=BODY13, maxWidth=124)
at(f"{R}>show_exiles_collaborations_button", sprite=D + "button", position=(BX[1], Y))
at(f"{R}>icon_exiled_collaborations_governments", position=(BX[1] + 3, Y - 2))
at(f"{R}>manage_exiled_collaborations_governments", position=(BX[1] + 34, Y + 6), font=BODY13, maxWidth=126)
at(f"{R}>subjects_button_container", position=(BX[2], Y))
at("subjects_button_container>show_subjects_button", sprite=D + "button", Orientation="UPPER_LEFT")
at("subjects_button_container>show_subjects_button_text", position=(32, 6), font=BODY13, maxWidth=128)

# ---------------------------------------------------------------- advisors and laws (the game's list)
at(f"{R}>ideas", position=(0, LP.IDEAS_Y))
at(f"{R}>autonomy_progress_view", position=(0, LP.IDEAS_Y + 5))
C = LP.CAT_HEADER
at("country_politics_idea_category_entry>category_header", sprite=D + "cat_header", position=(C["x"], C["y"]))
at("country_politics_idea_category_entry>name", font=SECTION, position=(70, 13))
at("political_idea_entry>add_idea_button", sprite=D + "idea_slot")

# ---------------------------------------------------------------- sub-windows
at("political_ideas_window>close", sprite=D + "close")
at("political_ideas_window>title", font="valsora_deco_section_14")
at("political_selectable_idea_entry_grid>idea_entry_bg", sprite=D + "idea_entry_grid", position=(3, 1))
at("political_selectable_idea_entry_list>idea_entry_bg", sprite=D + "idea_entry_list", position=(3, 1))
for win, header, title in [("manage_subjects_window", "manage_occupied_header_bg", "manage_occupied_title"),
                           ("exiles_window", "title_bg", "title"),
                           ("manage_occupied_window", "manage_occupied_header_bg", "manage_occupied_title")]:
    at(f"{win}>{header}", sprite=D + "sub_header")
    at(f"{win}>close_button", sprite=D + "close")
    at(f"{win}>{title}", font="valsora_deco_section_14")
for item, sprite in [("subject_item", "entry_87"), ("collaboration_item", "entry_65"), ("exile_item", "entry_95"),
                     ("occupied_territory_entry", "entry_100")]:
    t = GP.set_background(t, item, D + sprite)

t = ("# Valsora Deco UI - politics screen (art deco layout, v0.4: the Government mockup)\n"
     f"# Generated by tools/make_politics.py from {'the Valsora mod' if VALSORA in base else 'the game'}'s\n"
     "# countrypoliticsview.gui: every element and name is kept; positions, sprites and fonts change, and labels,\n"
     "# a ribbon and the section art are added. Re-run the tool rather than hand-merging after a HOI4 patch.\n\n" + t)
GP.check(t)
GP.write_gui(MOD + "interface/countrypoliticsview.gui", t)
print("countrypoliticsview.gui written from", base)


# ================================================================ scripted GUIs docked to the politics window
def window(name, x, y, w, h, body):
    return (f'\tcontainerWindowType = {{\n\t\tname = "{name}"\n\t\tposition = {{ x = {x} y = {y} }}\n'
            f'\t\tsize = {{ width = {w} height = {h} }}\n\t\tOrientation = "UPPER_LEFT"\n\t\tclipping = no\n'
            f'\t\talwaystransparent = yes\n{body}\t}}\n')


def text(name, loc, font, x, y, w, h, fmt="left", valign=False, tooltip=None, transparent=True):
    va = "\t\t\tvertical_alignment = center\n" if valign else ""
    tt = f'\t\t\tpdx_tooltip = "{tooltip}"\n' if tooltip else ""
    tr = "\t\t\talwaystransparent = yes\n" if transparent else ""
    return (f'\t\tinstantTextBoxType = {{\n\t\t\tname = "{name}"\n\t\t\tposition = {{ x = {x} y = {y} }}\n'
            f'\t\t\tfont = "{font}"\n\t\t\ttext = "{loc}"\n\t\t\tformat = {fmt}\n\t\t\tmaxWidth = {w}\n'
            f'\t\t\tmaxHeight = {h}\n\t\t\tfixedsize = yes\n{va}{tt}{tr}\t\t}}\n')


def icon_el(name, sprite, x, y):
    return (f'\t\ticonType = {{\n\t\t\tname = "{name}"\n\t\t\tspriteType = "{sprite}"\n'
            f'\t\t\tposition = {{ x = {x} y = {y} }}\n\t\t\talwaystransparent = yes\n\t\t}}\n')


HT = LP.HEAD_TITLE
gx0, gy0 = LP.GRID_X[0], LP.GRID_VALUE_Y[0]
dy = LP.GRID_VALUE_Y[1] - LP.GRID_VALUE_Y[0]
dx = LP.GRID_X[1] - LP.GRID_X[0]
DT = LP.DESC_TEXT
law_rows = "".join(text(f"valsora_deco_pol_law_{key}_value", f"VAL_DECO_POL_LAW_{key.upper()}_VALUE", BODY13, 0,
                        i * (LP.LAW_H + LP.LAW_GAP) + 14, LP.LAWS_W - 46, 15, tooltip="VAL_DECO_POL_LAWS_TT",
                        transparent=False)
                   for i, (key, _) in enumerate(LP.LAW_CARDS))
WINDOWS = [
    ("valsora_deco_pol_title", "valsora_deco_pol_title_window", HT["x"], HT["y"], HT["w"], HT["h"],
     text("valsora_deco_pol_title", "VAL_DECO_POL_TITLE", "valsora_deco_title_18", 0, 0, HT["w"], HT["h"], valign=True), None),
    ("valsora_deco_pol_info", "valsora_deco_pol_info_window", gx0, gy0, LP.X1 - gx0, dy + LP.GRID_VALUE_H,
     text("valsora_deco_pol_party", "VAL_DECO_POL_PARTY_VALUE", VALUE15, 0, 0, LP.GRID_W[0], LP.GRID_VALUE_H)
     + text("valsora_deco_pol_last_election", "VAL_DECO_POL_LAST_ELECTION_VALUE", VALUE15, 0, dy, LP.GRID_W[0], LP.GRID_VALUE_H)
     + text("valsora_deco_pol_pp", "VAL_DECO_POL_PP_VALUE", VALUE15, dx, dy, LP.GRID_W[1], LP.GRID_VALUE_H), None),
    ("valsora_deco_pol_desc", "valsora_deco_pol_desc_window", DT["x"], DT["y"], DT["w"], DT["h"],
     text("valsora_deco_pol_desc_text", "VAL_DECO_POL_DESC", ITALIC, 0, 0, DT["w"], DT["h"]),
     "valsora_deco_leader_has_desc = yes"),
    ("valsora_deco_pol_desc_none", "valsora_deco_pol_desc_none_window", LP.DESC["x"] + LP.DESC["w"] // 2 - 120,
     LP.DESC["y"] + LP.DESC["h"] // 2 - 12, 240, 24, icon_el("valsora_deco_pol_ornament", D + "ornament", 0, 0),
     "NOT = { valsora_deco_leader_has_desc = yes }"),
    ("valsora_deco_pol_laws", "valsora_deco_pol_laws_window", LP.LAWS_X + 40, LP.LAW_Y0, LP.LAWS_W - 46,
     3 * LP.LAW_H + 2 * LP.LAW_GAP, law_rows, None),
    ("valsora_deco_pol_faction_role", "valsora_deco_pol_faction_role_window", FC["x"] + 110, FC["y"] + 7, 82, 12,
     text("valsora_deco_pol_faction_role_text", "VAL_DECO_POL_FACTION_ROLE", LABEL, 0, 0, 82, 12, "right"),
     "is_in_faction = yes"),
]
GP.write_gui(MOD + "interface/valsora_deco_politics_extras.gui", 
    "# Valsora Deco UI - scripted-GUI windows on the politics screen (common/scripted_guis/valsora_deco_politics.txt)\n"
    "# Positions are politics-window pixels. Generated by tools/make_politics.py.\nguiTypes = {\n"
    + "".join(window(w, x, y, ww, hh, body) for _, w, x, y, ww, hh, body, _ in WINDOWS) + "}\n")
os.makedirs(MOD + "common/scripted_guis", exist_ok=True)
sg = "# Valsora Deco UI - politics screen additions (windows in interface/valsora_deco_politics_extras.gui)\nscripted_gui = {\n"
for gname, wname, *_, vis in WINDOWS:
    sg += (f"\t{gname} = {{\n\t\tcontext_type = player_context\n\t\twindow_name = \"{wname}\"\n"
           f"\t\tparent_window_token = politics_tab\n" + (f"\t\tvisible = {{ {vis} }}\n" if vis else "") + "\t}\n")
sg += "}\n"
open(MOD + "common/scripted_guis/valsora_deco_politics.txt", "w", encoding="utf-8", newline="\n").write(sg)

# ================================================================ data from the Valsora mod
# ideologies (popularity of the ruling party), leaders with a description
ideologies = ["democratic", "communism", "fascism", "neutrality"]
ipath = os.path.join(VALSORA, "common", "ideologies")
if os.path.isdir(ipath):
    found = []
    for f in sorted(os.listdir(ipath)):
        src = re.sub(r"#[^\n]*", "", open(os.path.join(ipath, f), encoding="utf-8-sig").read())
        depth = 0
        for m in re.finditer(r"([A-Za-z_]+)\s*=\s*\{|\{|\}", src):
            if m.group(0).endswith("{") and m.group(1):
                if depth == 1:
                    found.append(m.group(1))
                depth += 1
            elif m.group(0) == "{":
                depth += 1
            else:
                depth -= 1
    ideologies = found or ideologies
leaders_with_desc = []
cpath = os.path.join(VALSORA, "common", "characters")
if os.path.isdir(cpath):
    for f in sorted(os.listdir(cpath)):
        src = re.sub(r"#[^\n]*", "", open(os.path.join(cpath, f), encoding="utf-8-sig").read())
        for m in re.finditer(r"^\t([A-Za-z0-9_]+)\s*=\s*\{", src, re.M):
            s_, e_ = m.start(), m.end()
            depth, j = 1, e_
            while depth and j < len(src):
                depth += {"{": 1, "}": -1}.get(src[j], 0)
                j += 1
            body = src[e_:j]
            cl = re.search(r"country_leader\s*=\s*\{(.*?)\}", body, re.S)
            if cl:
                dm = re.search(r'desc\s*=\s*"?([A-Za-z0-9_.]+)"?', cl.group(1))
                if dm:
                    leaders_with_desc.append((m.group(1), dm.group(1)))
print("ideologies:", ideologies, "| leaders with a description:", [c for c, _ in leaders_with_desc])

# the game's laws (Valsora uses vanilla's law ideas)
LAWS = {
    "conscription": ["disarmed_nation", "volunteer_only", "limited_conscription", "extensive_conscription",
                     "service_by_requirement", "all_adults_serve", "scraping_the_barrel"],
    "economy": ["undisturbed_isolation", "isolation", "civilian_economy", "low_economic_mobilisation",
                "partial_economic_mobilisation", "war_economy", "tot_economic_mobilisation"],
    "trade": ["closed_economy", "limited_exports", "export_focus", "free_trade"],
}

os.makedirs(MOD + "common/scripted_localisation", exist_ok=True)
sl = ["# Valsora Deco UI - politics screen text (generated by tools/make_politics.py from the Valsora mod)"]


def defined(name, entries, fallback):
    out = [f"defined_text = {{\n\tname = {name}"]
    for trig, key in entries:
        out.append(f"\ttext = {{\n\t\ttrigger = {{ {trig} }}\n\t\tlocalization_key = {key}\n\t}}")
    out.append(f"\ttext = {{\n\t\tlocalization_key = {fallback}\n\t}}\n}}")
    return "\n".join(out)


sl.append(defined("GetValsoraDecoRulingPopularity", [(f"has_government = {i}", f"VAL_DECO_POL_POP_{i.upper()}") for i in ideologies],
                  "VAL_DECO_POL_NONE"))
sl.append(defined("GetValsoraDecoLeaderDesc",
                  [(f"has_country_leader = {{ character = {c} ruling_only = yes }}", d) for c, d in leaders_with_desc],
                  "VAL_DECO_POL_NONE"))
for key, ideas in LAWS.items():
    sl.append(defined(f"GetValsoraDecoLaw{key.capitalize()}", [(f"has_idea = {i}", i) for i in ideas], "VAL_DECO_POL_NONE"))
sl.append(defined("GetValsoraDecoFactionRole", [("is_faction_leader = yes", "VAL_DECO_POL_FACTION_LEADER")],
                  "VAL_DECO_POL_FACTION_MEMBER"))
open(MOD + "common/scripted_localisation/valsora_deco_politics.txt", "w", encoding="utf-8", newline="\n").write(
    "\n\n".join(sl) + "\n")

os.makedirs(MOD + "common/scripted_triggers", exist_ok=True)
trig = ("\n".join(f"\t\thas_country_leader = {{ character = {c} ruling_only = yes }}" for c, _ in leaders_with_desc)
        or "\t\talways = no")
open(MOD + "common/scripted_triggers/valsora_deco_politics_triggers.txt", "w", encoding="utf-8", newline="\n").write(
    "# Valsora Deco UI - generated by tools/make_politics.py from the Valsora characters (country_leader desc).\n"
    "# True when the ruling leader has a description to show on the politics screen.\n"
    f"valsora_deco_leader_has_desc = {{\n\tOR = {{\n{trig}\n\t\talways = no\n\t}}\n}}\n")

# ================================================================ sprites and localisation
TEX = "gfx/interface/valsora_deco/politics/"
SPRITES = [  # name, texture, frames, effect, extra
    ("sections", "pol_sections.dds", 1, None, ""),
    ("frame", "portrait_frame.dds", 1, None, ""),
    ("ribbon", "ribbon.dds", 1, None, ""),
    ("close", "close.dds", 1, "buttonstate.lua", ""),
    ("close_small", "close_small.dds", 1, "buttonstate.lua", ""),
    ("faction_card", "faction_card.dds", 3, None, ""),
    ("focus_card", "focus_card.dds", 3, "buttonstate_onlydisable.lua", ""),
    ("pie_ring", "pie_ring.dds", 1, None, "\t\talwaystransparent = yes\n"),
    ("party_diamond", "party_diamond.dds", 1, None, ""),
    ("party_swatch_bg", "party_swatch_bg.dds", 1, None, ""),
    ("party_lead", "party_lead.dds", 1, None, ""),
    ("button", "button.dds", 1, "buttonstate.lua", ""),
    ("strip", "strip.dds", 1, None, ""),
    ("cat_header", "category_header.dds", 1, None, ""),
    ("idea_slot", "idea_slot.dds", 1, None, ""),
    ("ornament", "ornament.dds", 1, None, ""),
    ("sub_header", "sub_header.dds", 1, None, ""),
    ("idea_entry_grid", "idea_entry_grid.dds", 2, None, ""),
    ("idea_entry_list", "idea_entry_list.dds", 2, None, ""),
]
gfx = "# Valsora Deco UI - politics screen sprites (generated by tools/make_politics.py)\nspriteTypes = {\n"
for name, tex, frames, eff, extra in SPRITES:
    gfx += f'\tspriteType = {{\n\t\tname = "GFX_valsora_deco_pol_{name}"\n\t\ttexturefile = "{TEX}{tex}"\n'
    if frames > 1:
        gfx += f"\t\tnoOfFrames = {frames}\n"
    if eff:
        gfx += f'\t\teffectFile = "gfx/FX/{eff}"\n'
    gfx += extra + "\t}\n"
gfx += ('\t# "choose a focus" pulse over the focus card (the game shows/hides it)\n'
        '\tframeAnimatedSpriteType = {\n\t\tname = "GFX_valsora_deco_pol_focus_glow"\n'
        f'\t\ttexturefile = "{TEX}focus_glow.dds"\n\t\tnoOfFrames = 2\n\t\tanimation_rate_fps = 1\n\t\tlooping = yes\n'
        '\t\tplay_on_show = yes\n\t\tpause_on_loop = 0.0\n\t\talwaystransparent = yes\n'
        '\t\teffectFile = "gfx/FX/buttonstate_blendframes.lua"\n\t}\n')
gfx += (f'\t# the popularity pie, larger than vanilla\'s (size = radius)\n'
        f'\tpieChartType = {{\n\t\tname = "GFX_valsora_deco_pol_chart"\n\t\tsize = {LP.PIE["r"]}\n\t}}\n')
FBAR = LP.FOCUS_BAR
gfx += (f'\tprogressbartype = {{\n\t\tname = "GFX_valsora_deco_pol_focus_bar"\n\t\tcolor = {{ 1.0 1.0 1.0 }}\n'
        f'\t\tcolortwo = {{ 1.0 1.0 1.0 }}\n\t\ttextureFile1 = "{TEX}focus_fill.dds"\n\t\ttextureFile2 = "{TEX}focus_track.dds"\n'
        f'\t\tsize = {{ x = {FBAR["w"]} y = {FBAR["h"]} }}\n\t\teffectFile = "gfx/FX/progress_startend.lua"\n\t}}\n')
# the entry cards are container backgrounds: corneredTile so they fill the container
for name, (w, h) in {"entry_87": (494, 87), "entry_95": (494, 95), "entry_65": (494, 65), "entry_100": (494, 100)}.items():
    gfx += (f'\tcorneredTileSpriteType = {{\n\t\tname = "GFX_valsora_deco_pol_{name}"\n\t\tsize = {{ x = {w} y = {h} }}\n'
            f'\t\ttextureFile = "{TEX}{name}.dds"\n\t\tborderSize = {{ x = 16 y = 16 }}\n\t\ttilingCenter = yes\n\t}}\n')
gfx += "}\n"
open(MOD + "interface/valsora_deco_politics.gfx", "w", encoding="utf-8", newline="\n").write(gfx)

LOC = {
    "VAL_DECO_POL_TITLE": "[ROOT.GetNameDefCap]",
    "VAL_DECO_POL_GOVERNMENT": "Government",
    "VAL_DECO_POL_HEAD_OF_STATE": "§KHead of State§!",   # dark text on the gold ribbon
    "VAL_DECO_POL_RULING_PARTY": "Ruling Party",
    "VAL_DECO_POL_ELECTIONS": "Elections",
    "VAL_DECO_POL_LAST_ELECTION": "Last Election",
    "VAL_DECO_POL_POLITICAL_POWER": "Political Power",
    "VAL_DECO_POL_SECTION_POPULARITY": "Popularity",
    "VAL_DECO_POL_SECTION_LAWS": "Laws",
    "VAL_DECO_POL_SECTION_FACTION": "Faction",
    "VAL_DECO_POL_SECTION_FOCUS": "National Focus",
    "VAL_DECO_POL_LAW_CONSCRIPTION": "Conscription",
    "VAL_DECO_POL_LAW_ECONOMY": "Economy",
    "VAL_DECO_POL_LAW_TRADE": "Trade",
    "VAL_DECO_POL_LAW_CONSCRIPTION_VALUE": "[GetValsoraDecoLawConscription]",
    "VAL_DECO_POL_LAW_ECONOMY_VALUE": "[GetValsoraDecoLawEconomy]",
    "VAL_DECO_POL_LAW_TRADE_VALUE": "[GetValsoraDecoLawTrade]",
    "VAL_DECO_POL_LAWS_TT": "Laws are changed in the advisors and laws list at the bottom of this screen.",
    "VAL_DECO_POL_PARTY_VALUE": "[ROOT.GetRulingParty] · [GetValsoraDecoRulingPopularity]",
    "VAL_DECO_POL_LAST_ELECTION_VALUE": "[ROOT.GetLastElection]",
    "VAL_DECO_POL_PP_VALUE": "[?political_power|0]  [?political_power_daily|+=2]",
    "VAL_DECO_POL_DESC": "[GetValsoraDecoLeaderDesc]",
    "VAL_DECO_POL_FACTION_ROLE": "[GetValsoraDecoFactionRole]",
    "VAL_DECO_POL_FACTION_LEADER": "Leader",
    "VAL_DECO_POL_FACTION_MEMBER": "Member",
    "VAL_DECO_POL_NONE": "",
}
for i in ideologies:
    LOC[f"VAL_DECO_POL_POP_{i.upper()}"] = f"[?party_popularity_100@{i}|0]%"
for lang in ["english", "french", "german", "spanish", "braz_por", "polish", "russian", "japanese", "simp_chinese"]:
    d = MOD + f"localisation/{lang}/"
    os.makedirs(d, exist_ok=True)
    open(d + f"valsora_deco_politics_l_{lang}.yml", "w", encoding="utf-8-sig", newline="\n").write(
        f"l_{lang}:\n" + "".join(f' {k}:0 "{v}"\n' for k, v in LOC.items()))
print("politics scripted GUIs, localisation and sprites written")
