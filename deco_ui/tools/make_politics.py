"""Build interface/countrypoliticsview.gui (art deco politics screen, v0.4: the Government mockup's layout).

    python make_politics.py "<HOI4 install folder>" ["<Valsora mod folder>"]

Base file: the Valsora mod's own interface/countrypoliticsview.gui when it has one (so its edits are kept),
otherwise the game's. Every element and name is kept; positions, sprites and fonts change, and the mod adds
labels, the ribbon and the section art. What the game's screen does not provide is drawn by small scripted
GUIs docked to the politics window (common/scripted_guis/valsora_deco_politics.txt):

  title        the country's full name                     [ROOT.GetNameDefCap]
  info         ruling party + its popularity, last election, political power and its daily change
  sub-ideology the ruling leader's sub-ideology, its description as the tooltip (scripted localisation
               over has_country_leader_ideology, from the Valsora mod's ideologies)
  faction role "Leader" / "Member"

v0.4.8: the panel sits flush under the top bar with a notch around the top bar's flag medallion and
decisions seal (layout_politics.NOTCH), which show through it; the leader's description is only in the
portrait's own tooltip; the law cards are gone (the laws are in the list below); the header picture is
vanilla's pol_view_bg sprite (the game swaps it at runtime, so its textures are replaced at their paths).

Positions come from layout_politics.py. Also writes the scripted GUIs, scripted localisation, the trigger
for "has a description", the sprites (.gfx) and the localisation.
"""
import os
import re
import sys

import guipatch as GP
import layout_politics as LP
from paths import MOD, VANILLA as VANILLA_DIR, VALSORA as VALSORA_DIR, VALSORA_BASE

ARG = sys.argv[1] if len(sys.argv) > 1 else VANILLA_DIR
VALSORA = sys.argv[2] if len(sys.argv) > 2 else VALSORA_DIR
# the base: the Valsora mod's own file as it built it (paths.VALSORA_BASE), else the game's
base = next((p for p in (os.path.join(b, "interface", "countrypoliticsview.gui") for b in (VALSORA_BASE, VALSORA, ARG))
             if os.path.isfile(p)))
t = open(base, encoding="utf-8-sig").read().replace("\r\n", "\n")
assert "Valsora Deco UI" not in t, (f"{base} is the Deco UI's own output: build the Valsora mod (sh scripts/run_all.sh), "
                                    "which keeps its own copy in work/deco_base/")
t = t.replace("y = 1s }", "y = 1 }")      # vanilla typo in the pie overlay's position

R = "countrypoliticsview"
NONE = "GFX_valsora_deco_none"
D = "GFX_valsora_deco_pol_"
LABEL, SECTION, HEADING = "valsora_deco_label", "valsora_deco_section_11", "valsora_deco_heading_24"
BODY15, BODY13, VALUE15, VALUE12 = "valsora_deco_body_15", "valsora_deco_body_13", "valsora_deco_value_15", "valsora_deco_value_12"


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


# ---------------------------------------------------------------- the panel: flush under the top bar
# The panel is drawn over the top bar, so it leaves a notch where the flag medallion and decisions seal
# hang: its own background is clear and lets clicks through, and the panel's look and its click-catching
# come from children that stay out of the notch (in game: whether clicks reach the seal through it).
# closed, the panel rests at the game's off-screen x; it opens at once (layout_politics.OPEN_MS, v0.5.2)
_hx = LP.closed_x(GP.own_region(t[slice(*GP.find_block(t, R))])[0])
at(R, position=(_hx, LP.TOP), show_position=(LP.PANEL_X, LP.TOP), animation_time=LP.OPEN_MS)
t = GP.set_background(t, R, "GFX_valsora_deco_clear")
t = re.sub(r'(name = "countrypoliticsview".*?background\s*=\s*\{[^{}]*?quadTextureSprite\s*=\s*"GFX_valsora_deco_clear")',
           r'\1\n\t\t\talwaystransparent = yes', t, count=1, flags=re.S)
assert t.count("alwaystransparent = yes", 0, t.index('name ="production_header_bg"')) == 1, "panel background not click-through"
under = ("\n\t\t# ===== Valsora Deco: the panel below the header strip, invisible click-catchers beside the notch, "
         "the section art =====\n"
         f'\t\tcontainerWindowType = {{\n\t\t\tname = "valsora_deco_pol_body"\n'
         f'\t\t\tposition = {{ x = 0 y = {LP.NOTCH_BOTTOM} }}\n\t\t\tsize = {{ width = {LP.PANEL_W} height = 100%% }}\n'
         f'\t\t\tbackground = {{\n\t\t\t\tname = "valsora_deco_pol_body_bg"\n\t\t\t\tquadTextureSprite = "{D}body"\n\t\t\t}}\n\t\t}}')
for i, (x0, y0, x1, y1) in enumerate(LP.blockers()):
    under += (f'\n\t\tcontainerWindowType = {{\n\t\t\tname = "valsora_deco_pol_block_{i}"\n'
              f'\t\t\tposition = {{ x = {x0} y = {y0} }}\n\t\t\tsize = {{ width = {x1 - x0} height = {y1 - y0} }}\n'
              f'\t\t\tbackground = {{\n\t\t\t\tname = "valsora_deco_pol_block_{i}_bg"\n\t\t\t\tquadTextureSprite = "GFX_valsora_deco_clear"\n\t\t\t}}\n\t\t}}')
under += new_icon("valsora_deco_pol_sections", D + "sections", 0, 0) + "\n"
t = GP.insert_child(t, R, under, first=True)

# ---------------------------------------------------------------- header
at(f"{R}>production_header_bg", sprite=NONE)
H = LP.HEAD_LABEL
# the game's title is drawn before pol_view_bg, which is now the header picture, so it stays empty and a
# label of our own is drawn after the picture (below)
at(f"{R}>political_title", position=(H["x"], H["y"]), font=LABEL, maxWidth=H["w"], maxHeight=H["h"],
   text="VAL_DECO_POL_NONE")
at(f"{R}>close_button", sprite=D + "close", position=(LP.CLOSE["x"], LP.CLOSE["y"]))
at(f"{R}>rules", position=LP.RULES)
# the game swaps this icon's sprite to GFX_pol_view_bg or GFX_pol_view_bg_no_dlc at runtime (in game, v0.4.7:
# vanilla's header art showed), so it keeps the vanilla name and its textures are replaced (gen_textures.py)
at(f"{R}>pol_view_bg", sprite="GFX_pol_view_bg", position=(0, 0), alwaystransparent="yes")
t = GP.insert_after(t, f"{R}>pol_view_bg", new_text("valsora_deco_pol_head_label", "VAL_DECO_POL_GOVERNMENT", LABEL,
                                                     H["x"], H["y"], H["w"], H["h"], valign=False))

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
for i, key in enumerate(["RULING_PARTY", "ELECTIONS", "LAST_ELECTION", "POLITICAL_POWER", "SUB_IDEOLOGY"]):
    col, row = i % 2, i // 2
    added += new_text(f"valsora_deco_pol_label_{key.lower()}", f"VAL_DECO_POL_{key}", LABEL, LP.GRID_X[col],
                      LP.GRID_LABEL_Y[row], LP.GRID_W[col], 12, valign=False)
for key, (x, y, _) in LP.SECTION_LABELS.items():
    if key == "spirits":
        continue   # the game's own "National Spirits" title is restyled instead
    added += new_text(f"valsora_deco_pol_section_{key}", f"VAL_DECO_POL_SECTION_{key.upper()}", SECTION, x, y, 200, 12,
                      valign=False)
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
at("ruling_party_info>power_balance_button", position=(LP.BOP["x"], LP.BOP["y"]))   # under the legend

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
at("in_faction>faction_name_position", position=(54, LP.FACTION_NAME_Y))
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
big, small = LP.SPIRIT_SLOT, LP.SPIRIT_SMALL
nb = (SP["w"] - 8) // big[0]                       # 4 large spirits a row, 2 rows
ns = (SP["w"] - 24) // small[0]                    # then 7 small ones a row (room for the scrollbar)
at("national_spirit_container>spirit_grid", position=(4, 2), size=(nb * big[0], 2 * big[1]), max_slots=(nb, 2))
at("national_spirit_container>spirit_grid_over_defined", position=(4, 2), size=(ns * small[0], SP["h"] - 4),
   max_slots_horizontal=ns)

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
# v0.5: the windows that open beside the panel sit flush under the band as well (they opened at y 80)
for win in ("political_ideas_window", "manage_subjects_window", "exiles_window", "manage_occupied_window"):
    s_, e_ = GP.find_block(t, win)
    head_ = GP.own_region(t[s_:e_])[0]
    sx_ = re.search(r"show_position\s*=\s*\{\s*x\s*=\s*(-?\d+)", head_).group(1)
    at(win, position=(LP.closed_x(head_), LP.TOP), show_position=(int(sx_), LP.TOP), animation_time=LP.OPEN_MS)
for item, sprite in [("subject_item", "entry_87"), ("collaboration_item", "entry_65"), ("exile_item", "entry_95"),
                     ("occupied_territory_entry", "entry_100")]:
    t = GP.set_background(t, item, D + sprite)

t = ("# Valsora Deco UI - politics screen (art deco layout, v0.4: the Government mockup)\n"
     f"# Generated by tools/make_politics.py from {'the game' if base.startswith(ARG) else 'the Valsora mod'}'s\n"
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


HT = LP.HEAD_TITLE
gx0, gy0 = LP.GRID_X[0], LP.GRID_VALUE_Y[0]
dy = LP.GRID_VALUE_Y[1] - LP.GRID_VALUE_Y[0]
dx = LP.GRID_X[1] - LP.GRID_X[0]
SI = LP.SUB_IDEOLOGY
WINDOWS = [
    ("valsora_deco_pol_title", "valsora_deco_pol_title_window", HT["x"], HT["y"], HT["w"], HT["h"],
     text("valsora_deco_pol_title", "VAL_DECO_POL_TITLE", "valsora_deco_title_18", 0, 0, HT["w"], HT["h"], valign=True), None),
    ("valsora_deco_pol_info", "valsora_deco_pol_info_window", gx0, gy0, LP.X1 - gx0, dy + LP.GRID_VALUE_H,
     text("valsora_deco_pol_party", "VAL_DECO_POL_PARTY_VALUE", VALUE15, 0, 0, LP.GRID_W[0], LP.GRID_VALUE_H)
     + text("valsora_deco_pol_last_election", "VAL_DECO_POL_LAST_ELECTION_VALUE", VALUE15, 0, dy, LP.GRID_W[0], LP.GRID_VALUE_H)
     + text("valsora_deco_pol_pp", "VAL_DECO_POL_PP_VALUE", VALUE15, dx, dy, LP.GRID_W[1], LP.GRID_VALUE_H), None),
    # the sub-ideology; its description is the tooltip (the text box is not click-through, so it shows)
    ("valsora_deco_pol_sub_ideology", "valsora_deco_pol_sub_ideology_window", SI["x"], SI["y"], SI["w"], SI["h"],
     text("valsora_deco_pol_sub_ideology_text", "VAL_DECO_POL_SUB_IDEOLOGY_VALUE", VALUE15, 0, 0, SI["w"], SI["h"],
          tooltip="VAL_DECO_POL_SUB_IDEOLOGY_TT", transparent=False), None),
    ("valsora_deco_pol_faction_role", "valsora_deco_pol_faction_role_window", FC["x"] + LP.FACTION_COL["x"],
     FC["y"] + LP.FACTION_ROLE["y"], LP.FACTION_COL["w"], LP.FACTION_ROLE["h"],
     text("valsora_deco_pol_faction_role_text", "VAL_DECO_POL_FACTION_ROLE", LABEL, 0, 0, LP.FACTION_COL["w"],
          LP.FACTION_ROLE["h"], "centre", valign=True),
     "is_in_faction = yes"),
]
# the faction's members: a grid the scripted GUI fills from the game's faction_members, one flag per member (v0.9)
FM = LP.FACTION_MEMBERS
FM_W, FM_H = FM["slot"][0] * FM["cols"], FM["slot"][1] * FM["rows"]
MEMBERS = (window("valsora_deco_pol_faction_members_window", FC["x"] + FM["x"], FC["y"] + FM["y"], FM_W, FM_H,
                  f'\t\tgridBoxType = {{\n\t\t\tname = "valsora_deco_pol_faction_members_grid"\n'
                  f'\t\t\tposition = {{ x = 0 y = 0 }}\n\t\t\tsize = {{ width = {FM_W} height = {FM_H} }}\n'
                  f'\t\t\tslotsize = {{ width = {FM["slot"][0]} height = {FM["slot"][1]} }}\n'
                  f'\t\t\tmax_slots = {{ x = {FM["cols"]} y = {FM["rows"]} }}\n\t\t\tformat = "UPPER_LEFT"\n\t\t}}\n')
           + window("valsora_deco_pol_faction_member_entry", 0, 0, FM["slot"][0], FM["slot"][1],
                    text("valsora_deco_pol_faction_member_flag", "VAL_DECO_POL_FACTION_MEMBER_FLAG", VALUE12, 0, 0,
                         FM["slot"][0], FM["slot"][1], "left", valign=True, tooltip="VAL_DECO_POL_FACTION_MEMBER_TT",
                         transparent=False)))
GP.write_gui(MOD + "interface/valsora_deco_politics_extras.gui", 
    "# Valsora Deco UI - scripted-GUI windows on the politics screen (common/scripted_guis/valsora_deco_politics.txt)\n"
    "# Positions are politics-window pixels. Generated by tools/make_politics.py.\nguiTypes = {\n"
    + "".join(window(w, x, y, ww, hh, body) for _, w, x, y, ww, hh, body, _ in WINDOWS) + MEMBERS + "}\n")
os.makedirs(MOD + "common/scripted_guis", exist_ok=True)
sg = "# Valsora Deco UI - politics screen additions (windows in interface/valsora_deco_politics_extras.gui)\nscripted_gui = {\n"
for gname, wname, *_, vis in WINDOWS:
    sg += (f"\t{gname} = {{\n\t\tcontext_type = player_context\n\t\twindow_name = \"{wname}\"\n"
           f"\t\tparent_window_token = politics_tab\n" + (f"\t\tvisible = {{ {vis} }}\n" if vis else "") + "\t}\n")
sg += ("\tvalsora_deco_pol_faction_members = {\n\t\tcontext_type = player_context\n"
       "\t\twindow_name = \"valsora_deco_pol_faction_members_window\"\n\t\tparent_window_token = politics_tab\n"
       "\t\tvisible = { is_in_faction = yes }\n"
       "\t\tdynamic_lists = {\n\t\t\tvalsora_deco_pol_faction_members_grid = {\n\t\t\t\tarray = faction_members\n"
       "\t\t\t\tchange_scope = yes\n\t\t\t\tentry_container = \"valsora_deco_pol_faction_member_entry\"\n"
       "\t\t\t}\n\t\t}\n\t}\n")
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
# sub-ideologies: the keys inside each ideology's types = { } block (their names and descriptions are the
# game's localisation keys <key> and <key>_desc, which Valsora writes)
sub_ideologies = []


def _block_end(s, i):
    """index just past the brace that closes the block opened right before i"""
    depth = 1
    while depth and i < len(s):
        depth += {"{": 1, "}": -1}.get(s[i], 0)
        i += 1
    return i


if os.path.isdir(ipath):
    for f in sorted(os.listdir(ipath)):
        src = re.sub(r"#[^\n]*", "", open(os.path.join(ipath, f), encoding="utf-8-sig").read())
        for m in re.finditer(r"\btypes\s*=\s*\{", src):
            body = src[m.end():_block_end(src, m.end()) - 1]
            depth = 0
            for mm in re.finditer(r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\{|\{|\}", body):
                if mm.group(0) == "}":
                    depth -= 1
                else:
                    if depth == 0 and mm.group(1):
                        sub_ideologies.append(mm.group(1))
                    depth += 1
print("ideologies:", ideologies, "| sub-ideologies:", len(sub_ideologies))
# the longest sub-ideology name must fit its row, in one line
sub_names = {}
for root, _, files in os.walk(os.path.join(VALSORA, "localisation", "english")):
    for f in files:
        if f.endswith(".yml"):
            for k, v in re.findall(r'^ ([A-Za-z0-9_]+):\d* "(.*)"', open(os.path.join(root, f), encoding="utf-8-sig").read(), re.M):
                sub_names[k] = v
if sub_names:
    # only the sub-ideologies the Valsora mod names and describes: the game's Earth-bound ones it keeps defined
    # (scripts/ideologies.py HIDDEN: nazism, falangism ...) are never a ruler's there
    sub_ideologies = [s for s in sub_ideologies if s in sub_names and f"{s}_desc" in sub_names]
    print("sub-ideologies the Valsora mod names:", len(sub_ideologies))
if sub_ideologies and sub_names:
    longest = max((sub_names.get(s, s) for s in sub_ideologies), key=lambda n: LP.L.measure(VALUE15, n))
    width = LP.L.measure(VALUE15, longest)
    assert width <= LP.SUB_IDEOLOGY["w"], f"sub-ideology {longest!r} is {width} px, its row {LP.SUB_IDEOLOGY['w']}"
    print(f"longest sub-ideology name: {longest!r}, {width} of {LP.SUB_IDEOLOGY['w']} px")

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
sl.append(defined("GetValsoraDecoSubIdeology",
                  [(f"has_country_leader_ideology = {s}", s) for s in sub_ideologies], "VAL_DECO_POL_NONE"))
sl.append(defined("GetValsoraDecoSubIdeologyDesc",
                  [(f"has_country_leader_ideology = {s}", f"{s}_desc") for s in sub_ideologies], "VAL_DECO_POL_NONE"))
sl.append(defined("GetValsoraDecoLastElection", [("has_elections = no", "VAL_DECO_POL_NO_ELECTIONS")],
                  "VAL_DECO_POL_LAST_ELECTION_DATE"))
sl.append(defined("GetValsoraDecoFactionRole", [("is_faction_leader = yes", "VAL_DECO_POL_FACTION_LEADER")],
                  "VAL_DECO_POL_FACTION_MEMBER"))
open(MOD + "common/scripted_localisation/valsora_deco_politics.txt", "w", encoding="utf-8", newline="\n").write(
    "\n\n".join(sl) + "\n")

# v0.4.7's "the leader has a description" trigger went with the description band
old_trigger = MOD + "common/scripted_triggers/valsora_deco_politics_triggers.txt"
if os.path.isfile(old_trigger):
    os.remove(old_trigger)

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
# the panel below the header strip: lacquer with the frame down the sides and along the bottom
gfx += (f'\tcorneredTileSpriteType = {{\n\t\tname = "GFX_valsora_deco_pol_body"\n\t\tsize = {{ x = 192 y = 192 }}\n'
        f'\t\ttextureFile = "{TEX}body.dds"\n\t\tborderSize = {{ x = 64 y = 64 }}\n\t\ttilingCenter = yes\n\t}}\n')
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
    "VAL_DECO_POL_SUB_IDEOLOGY": "Sub-Ideology",
    "VAL_DECO_POL_SECTION_POPULARITY": "Popularity",
    "VAL_DECO_POL_SECTION_FACTION": "Faction",
    "VAL_DECO_POL_SECTION_FOCUS": "National Focus",
    "VAL_DECO_POL_PARTY_VALUE": "[ROOT.GetRulingParty] · [GetValsoraDecoRulingPopularity]",
    "VAL_DECO_POL_LAST_ELECTION_VALUE": "[GetValsoraDecoLastElection]",
    "VAL_DECO_POL_LAST_ELECTION_DATE": "[ROOT.GetLastElection]",
    "VAL_DECO_POL_NO_ELECTIONS": "None",
    "VAL_DECO_POL_PP_VALUE": "[?political_power|0]  [?political_power_daily|+=2]",
    "VAL_DECO_POL_SUB_IDEOLOGY_VALUE": "[GetValsoraDecoSubIdeology]",
    "VAL_DECO_POL_SUB_IDEOLOGY_TT": "[GetValsoraDecoSubIdeologyDesc]",
    "VAL_DECO_POL_FACTION_ROLE": "[GetValsoraDecoFactionRole]",
    "VAL_DECO_POL_FACTION_LEADER": "Leader",
    "VAL_DECO_POL_FACTION_MEMBER": "Member",
    "VAL_DECO_POL_FACTION_MEMBER_FLAG": "[This.GetFlag]",
    "VAL_DECO_POL_FACTION_MEMBER_TT": "[This.GetNameDefCap]",
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
