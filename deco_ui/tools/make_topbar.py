"""Build interface/topbar.gui and interface/alerts.gui (art deco layout) from the game's own files.

    python make_topbar.py "C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV"  [path to the Valsora mod]

The first argument is the HOI4 install folder (or its interface/topbar.gui directly). The optional
second argument is the Valsora mod folder: its localisation decides which countries' names are too
long for the large name font (common/scripted_triggers/valsora_deco_triggers.txt).

Needs only Python 3 (no packages). Re-run it after a HOI4 patch that changes topbar.gui; it stops with
an AssertionError naming the element if Paradox renamed or removed something it relies on.

Every vanilla element and name is kept (the engine looks them up by name), but most are moved
and re-skinned; new decorative elements are added under the vanilla ones. All coordinates come
from layout.py. Also writes the extras .gui, scripted GUI, localisation and the two .gfx files.
"""
import os
import re
import sys

import guipatch as GP
import layout as L

from paths import MOD, VANILLA as VANILLA_DIR, VALSORA as VALSORA_DIR
ARG = sys.argv[1] if len(sys.argv) > 1 else VANILLA_DIR
if os.path.isdir(ARG):
    VANILLA, ALERTS = os.path.join(ARG, "interface", "topbar.gui"), os.path.join(ARG, "interface", "alerts.gui")
else:
    VANILLA, ALERTS = ARG, os.path.join(os.path.dirname(ARG), "alerts.gui")
VALSORA = sys.argv[2] if len(sys.argv) > 2 else VALSORA_DIR
if not os.path.isfile(VANILLA):
    sys.exit('usage: python make_topbar.py "<HOI4 install folder>" ["<Valsora mod folder>"]')
src = open(VANILLA, encoding="utf-8-sig").read().replace("\r\n", "\n")
TYPES = r"(?:containerWindowType|iconType|buttonType|instantTextBoxType|instantTextboxType|textBoxType|checkboxType)"


def find_block(text, name):
    pat = re.compile(r"name\s*=\s*\"" + re.escape(name) + r"\"")
    hits = list(pat.finditer(text))
    assert len(hits) == 1, (name, len(hits))
    i = hits[0].start()
    heads = list(re.finditer(TYPES + r"\s*=\s*\{", text[:i], re.I))
    start = heads[-1].start()
    depth = 0
    for j in range(text.index("{", start), len(text)):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return start, j + 1
    raise ValueError(name)


def own_region(block):
    m = re.search(TYPES + r"\s*=\s*\{|background\s*=\s*\{", block[block.index("{") + 1:], re.I)
    if m:
        cut = block.index("{") + 1 + m.start()
        cut = block.rindex("\n", 0, cut) + 1          # keep the child's own indentation in `rest`
    else:
        cut = block.rindex("}")                        # leaf element: attributes go before its closing brace
        cut = block.rindex("\n", 0, cut) + 1 if "\n" in block[:cut] else cut
    return block[:cut], block[cut:]


def set_attrs(text, name, **attrs):
    s, e = find_block(text, name)
    block = text[s:e]
    head, rest = own_region(block)
    indent = re.search(r"\n(\s*)name", head).group(1)
    for key, val in attrs.items():
        key_re = {"sprite": r"(?:spriteType|quadTextureSprite)"}.get(key, re.escape(key))
        if key in ("position", "show_position"):
            val = "{ x = %d y = %d }" % val
        elif key == "size":
            val = "{ width = %s height = %s }" % val
        elif isinstance(val, str) and key in ("font", "sprite", "Orientation"):
            val = '"%s"' % val
        line_re = re.compile(r"(\n\s*)(" + key_re + r")(\s*=\s*)(\{[^}]*\}|\"[^\"]*\"|[^\s#]+)", re.IGNORECASE)
        m = line_re.search(head)
        if m:
            head = head[:m.start()] + m.group(1) + m.group(2) + " = " + str(val) + head[m.end():]
        else:
            k = "spriteType" if key == "sprite" else key
            head = head.rstrip() + "\n" + indent + k + " = " + str(val) + "\n"
    return text[:s] + head + rest + text[e:]


def set_background(text, name, sprite):
    s, e = find_block(text, name)
    block = text[s:e]
    new, n = re.subn(r'(background\s*=\s*\{[^}]*?quadTextureSprite\s*=\s*)"[^"]*"', r'\1"%s"' % sprite, block, count=1)
    assert n == 1, name
    return text[:s] + new + text[e:]


G = L.GUI          # screen -> topbar coords (UPPER_LEFT)
GR = L.GUI_R       # screen -> topbar coords (UPPER_RIGHT)
CMX, CMY = L.MENU_X, L.MENU_Y   # country_menu_window origin on screen
moved = []         # (element, screen x, y) for the report


def icon(name, sprite, x, y, extra=""):
    return f"""
		iconType = {{
			name = "{name}"
			spriteType = "{sprite}"
			position = {{ x = {x} y = {y} }}
			Orientation = "UPPER_LEFT"
			alwaystransparent = yes{extra}
		}}"""


def label(name, loc, x, y, w):
    return f"""
		instantTextBoxType = {{
			name = "{name}"
			position = {{ x = {x} y = {y} }}
			font = "{L.LABEL_FONT}"
			text = "{loc}"
			format = left
			maxWidth = {w}
			maxHeight = 14
			fixedsize = yes
			Orientation = "UPPER_LEFT"
			alwaystransparent = yes
		}}"""


t = src

# ---------------------------------------------------------------- 1. new decorative layer (drawn first)
bx, by = G(0, 0)
deco = f"""
		# ================= Valsora Deco: decorative layer (not referenced by the engine) =================
		# full-width lacquer band; stretched by its corneredTile background
		containerWindowType = {{
			name = "valsora_deco_band"
			position = {{ x = {bx} y = {by} }}
			size = {{ width = 100%% height = {L.BAND_TEX_H} }}
			Orientation = "UPPER_LEFT"
			clipping = no
			background = {{
				name = "valsora_deco_band_bg"
				quadTextureSprite = "GFX_valsora_deco_topbar_band"
			}}
		}}
		# soft shadow under the band; click-through
		containerWindowType = {{
			name = "valsora_deco_band_shadow"
			position = {{ x = {bx} y = {by + L.BAND_TEX_H} }}
			size = {{ width = 100%% height = {L.SHADOW_H} }}
			Orientation = "UPPER_LEFT"
			clipping = no
			alwaystransparent = yes
			background = {{
				name = "valsora_deco_band_shadow_bg"
				quadTextureSprite = "GFX_valsora_deco_topbar_band_shadow"
			}}
		}}"""
tx, ty = G(L.TRAY["x"], L.TRAY["y"])
deco += f"""
		# tray hanging under the readouts (fuel, supply, convoys)
		iconType = {{
			name = "valsora_deco_tray"
			spriteType = "GFX_valsora_deco_tray"
			position = {{ x = {tx} y = {ty} }}
			Orientation = "UPPER_LEFT"
		}}"""
deco += "\n\t\t# readout dividers and labels"
for i, x in enumerate(L.DIVIDERS):
    deco += icon(f"valsora_deco_divider_{i + 1}", "GFX_valsora_deco_divider", *G(x, L.DIV_Y))
for it in L.STRIP:
    deco += label(f"valsora_deco_label_{it['key']}", it["loc"], *G(it["text_x"], L.LABEL_Y), it["text_w"] + 6)
deco += "\n\t\t# ================= end of decorative layer =================\n"
anchor = re.search(r"\n(\t\t)iconType\s*=\s*\{\s*\n\s*name\s*=\s*\"background\"", t)
assert anchor
t = t[:anchor.start()] + deco + t[anchor.start():]

# ---------------------------------------------------------------- 2. flag medallion, flag, plates
t = set_attrs(t, "background", sprite="GFX_valsora_deco_medallion", position=G(L.MED["x"], L.MED["y"]))
t = set_attrs(t, "player_flag", sprite="GFX_valsora_deco_player_flag", position=G(L.FLAG["x"], L.FLAG["y"]))
t = set_attrs(t, "observer_flag_overlay", position=G(L.FLAG["x"] - 1, L.FLAG["y"] + 1))
t = set_attrs(t, "armyoverview_buttons_bg", sprite="GFX_valsora_deco_topbar_right", position=GR(L.RPLATE["x"], L.RPLATE["y"]))
mx = -289
t = set_attrs(t, "toggle_music_commands_win", position=(mx, L.MUSIC_Y + 1), show_position=(-450, L.MUSIC_Y + 1))

# ---------------------------------------------------------------- 3. primary readouts in the band
PRIMARY = {  # key: (hover bg, icon, text, deco icon sprite)
    "pp": ("pol_power_value_bg", "pol_power_icon", "pol_power", "GFX_valsora_deco_icon_pp"),
    "stability": ("sability_value_bg", "stability_icon", "stability", "GFX_valsora_deco_icon_stability"),
    "war": ("war_support_value_bg", "war_support_icon", "war_support", "GFX_valsora_deco_icon_war"),
    "manpower": ("manpower_value_bg", "manpower_icon", "manpower", "GFX_valsora_deco_icon_manpower"),
    "factory": ("industrial_capacity_bg", "industrial_capacity_icon", "industrial_capacity", "GFX_valsora_deco_icon_factory"),
}
for it in L.STRIP:
    bg, ic, tx_, spr = PRIMARY[it["key"]]
    # the vanilla value box becomes an invisible hover area covering the whole readout
    t = set_attrs(t, bg, sprite=f"GFX_valsora_deco_hit_{it['w']}x46", position=G(it["x"], 6))
    t = set_attrs(t, ic, sprite=spr, position=G(it["icon_x"], L.ICON_Y))
    # factories: the game's single number is kept (box + tooltip) but drawn with an invisible font;
    # a scripted GUI draws civilian / military / naval counts with coloured diamonds in its place
    t = set_attrs(t, tx_, position=G(it["text_x"], L.VALUE_Y),
                  font="valsora_deco_blank" if it["key"] == "factory" else L.VALUE_FONT,
                  maxWidth=it["value_w"], maxHeight=20, format="left")

# ---------------------------------------------------------------- 4. logistics tray, right tray, badges
SEC = {it["key"]: it for it in L.SECONDARY}
for key, bg, ic, txt, bar, spr in [
    ("fuel", "fuel_value_bg", "fuel_icon", "fuel_value", "fuel_ratio_bar", "GFX_valsora_deco_icon_fuel"),
    ("supply", "supply_value_bg", "supply_icon", "supply_value", "supply_ratio_bar", None),
    ("convoys", "convoy_text_bg", "convoys_icon", "convoys_count", "convoys_ratio_bar", "GFX_valsora_deco_icon_convoy"),
]:
    it = SEC[key]
    t = set_attrs(t, bg, sprite=f"GFX_valsora_deco_hit_{it['w']}x30", position=G(it["x"], L.SEC_Y))
    if spr:
        t = set_attrs(t, ic, sprite=spr, position=G(it["icon_x"], L.SEC_ICON_Y))
    else:  # vanilla equipment icon (kept: the engine may pick its frame)
        t = set_attrs(t, ic, position=G(it["icon_x"] - 3, L.SEC_ICON_Y - 3))
    t = set_attrs(t, txt, position=G(it["value_x"], L.SEC_VALUE_Y_BAR), font=L.SEC_FONT, maxWidth=it["value_w"],
                  maxHeight=18, format="left", fixedsize="yes")
    t = set_attrs(t, bar, sprite="GFX_valsora_deco_ratio_bar", position=G(it["value_x"], L.SEC_BAR_Y))

# command power and nukes: icon + value in the right-hand tray (right-anchored like the tray)
for box, cont, ic, txt, spr in [(L.CP, "cp", "command_power_icon", "command_power_value", "GFX_valsora_deco_icon_command"),
                                (L.NUKES, "nukes", "nuke_icon", "nukes_value", "GFX_valsora_deco_icon_nuke")]:
    t = set_attrs(t, cont, position=GR(box["x"], box["y"]), size=(box["w"], box["h"]), Orientation="UPPER_RIGHT")
    t = set_background(t, cont, "GFX_valsora_deco_clear")
    t = set_attrs(t, ic, sprite=spr, position=(0, (box["h"] - L.TRAY_ICON) // 2))
    if cont == "nukes":
        t = set_attrs(t, ic, scale="1.0")
    t = set_attrs(t, txt, position=(L.TRAY_ICON + 4, L.box_y_for_caps(L.SEC_FONT, box["h"] // 2 - 5)), font=L.SEC_FONT,
                  maxWidth=box["w"] - L.TRAY_ICON - 4, maxHeight=18, format="left")

# army / navy / air experience: small badges on the matching overview buttons. The containers are
# moved after country_menu_window so they draw above the buttons.
B = L.XP_BADGE
for k, cont in L.XP_KEYS.items():
    ic, txt = {"land": ("experience_icon", "experience_value"), "navy": ("navy_experience_icon", "navy_experience_value"),
               "air": ("air_experience_icon", "air_experience_value")}[cont]
    t = set_attrs(t, cont, position=GR(L.OVERVIEW[k] + B["dx"], L.OVERVIEW_Y + B["dy"]), size=(B["w"], B["h"]),
                  Orientation="UPPER_RIGHT")
    t = set_background(t, cont, "GFX_valsora_deco_badge")
    t = set_attrs(t, ic, sprite="GFX_valsora_deco_none", position=(0, 0))
    t = set_attrs(t, txt, position=(0, L.box_y_for_caps(L.SMALL_FONT, 3)), font=L.SMALL_FONT, maxWidth=B["w"],
                  maxHeight=B["h"], format="centre")

# ---------------------------------------------------------------- 5. world tension value under its ring
t = set_attrs(t, "threat_button", position=GR(*L.WT_ICON))          # centre the globe in its ring
t = set_attrs(t, "threat_icon_glow", position=GR(*L.WT_GLOW))
wv = GR(L.WT_VALUE["x"], L.WT_VALUE["y"])
t = set_attrs(t, "threat_value_button", position=wv)
t = set_attrs(t, "threat_value", position=wv, font=L.SEC_FONT, maxWidth=L.WT_VALUE["w"], format="centre")

# ---------------------------------------------------------------- 6. date cartouche
t = set_attrs(t, "time_control_window", position=GR(L.CART["x"], L.CART["y"]), size=(L.CART["w"], L.CART["h"]))
for b in ("pause_button_date", "pause_button_date_paused"):
    spr = "GFX_valsora_deco_date_bg" if b == "pause_button_date" else "GFX_valsora_deco_date_paused"
    t = set_attrs(t, b, sprite=spr, position=(0, 0), Orientation="UPPER_LEFT")
t = set_attrs(t, "button_speedup", sprite="GFX_valsora_deco_speed_up", position=(L.PM_X, L.PLUS_Y))
t = set_attrs(t, "button_speeddown", sprite="GFX_valsora_deco_speed_down", position=(L.PM_X, L.MINUS_Y))
for i in range(5):
    t = set_attrs(t, f"button_speedstep{i + 1}", sprite="GFX_valsora_deco_speed_step",
                  position=(L.CHEV_X0 + i * L.CHEV_STEP, L.CHEV_Y))
t = set_attrs(t, "DateText", position=(L.DATE_BOX["x"], L.DATE_BOX["y"]), Orientation="UPPER_LEFT",
              font="valsora_deco_date", maxWidth=L.DATE_BOX["w"], maxHeight=22, format="centre", fixedsize="yes")

# ---------------------------------------------------------------- 7. right-hand buttons
t = set_attrs(t, "menu_button", sprite="GFX_valsora_deco_menu_button", position=GR(L.MENU_BTN["x"], L.MENU_BTN["y"]))
t = set_attrs(t, "help_button", sprite="GFX_valsora_deco_help_button", position=GR(L.HELP_BTN["x"], L.HELP_BTN["y"]))
t = set_attrs(t, "playlist_button", sprite="GFX_valsora_deco_playlist_button", position=GR(L.PLAYLIST["x"], L.PLAYLIST["y"]))
t = set_attrs(t, "achievements_button", position=GR(*L.ACHIEVEMENTS))
t = set_attrs(t, "dismissed_alerts_button", position=GR(*L.DISMISSED))

# ---------------------------------------------------------------- 8. menu row (country_menu_window)
t = set_attrs(t, "country_menu_window", position=G(CMX, CMY), size=("100%%", L.BTN_H), clipping="no")
rel = lambda k: L.MENU_POS[k] - CMX
# faction: first crown of the row. The game swaps this button between GFX_topbar_faction (out of a
# faction) and GFX_topbar_faction_empty (in one, with the faction's logo, faction_icon, drawn over it) at
# runtime, so both vanilla textures are replaced at their paths and the button keeps the vanilla sprite
# name. The logo is centred in the ring of our in-faction picture.
f0 = rel("faction")
t = set_attrs(t, "faction_button_container", position=(f0, 0), size=(L.BTN_W, L.BTN_H), clipping="no")
t = set_attrs(t, "faction_button", sprite="GFX_topbar_faction_empty", position=(0, 0))
t = set_attrs(t, "faction_icon", position=(L.FACTION_LOGO["dx"], L.FACTION_LOGO["dy"]), scale=str(L.FACTION_LOGO["scale"]))
FI = L.FACTION_INIT
t = set_attrs(t, "initiative_text", position=(FI["dx"], FI["dy"]), Orientation="UPPER_LEFT", font=L.SMALL_FONT,
              maxWidth=FI["w"], maxHeight=FI["h"], format="centre")

# decisions: the seal hanging from the flag medallion, with its two count badges on the right edge and the
# alert glow (vanilla textures replaced at their paths, sized to the seal) underneath
t = set_attrs(t, "after_faction_button", position=(0, 0), clipping="no")
sx, sy = L.SEAL["x"] - CMX, L.SEAL["y"] - CMY
t = set_attrs(t, "decision_view_alert_glow", position=(sx - L.SEAL_GLOW, sy - L.SEAL_GLOW))
t = set_attrs(t, "decisionview_button", sprite="GFX_valsora_deco_decisions_seal", position=(sx, sy))
(tx_, ty_), (bx_, by_) = L.DEC_BADGES["timeout"], L.DEC_BADGES["to_take"]
t = set_attrs(t, "decisionview_amount_timeout_bg", position=(tx_ - CMX + 2, ty_ - CMY))
t = set_attrs(t, "decisionview_amount_timeout_items", position=(tx_ - CMX, ty_ - CMY))
t = set_attrs(t, "decisionview_amount_to_take_bg", position=(bx_ - CMX + 2, by_ - CMY))
t = set_attrs(t, "decisionview_amount_to_take_items", position=(bx_ - CMX, by_ - CMY))
n = rel("intelligence")
t = set_attrs(t, "intel_agency_button", sprite="GFX_valsora_deco_tb_intelligence", position=(n, 0))
t = set_attrs(t, "intelview_ops_prepared_or_completed_bg", position=(n + 3, 3))
t = set_attrs(t, "intelview_ops_prepared_or_completed_items", position=(n + 1, 3))
t = set_attrs(t, "intelview_ops_available_bg", position=(n + 3, 26))
t = set_attrs(t, "intelview_ops_available_items", position=(n + 1, 26))
ai = rel("technology")
t = set_attrs(t, "after_intel_agency_button", position=(ai, 0))
r2 = lambda k: L.MENU_POS[k] - L.MENU_POS["technology"]
t = set_attrs(t, "technology_button", sprite="GFX_valsora_deco_tb_technology", position=(r2("technology"), 0))
t = set_attrs(t, "prototype_rewards_aquired_bg", position=(r2("technology") + 24, 26))
t = set_attrs(t, "prototype_rewards_aquired", position=(r2("technology") + 22, 26))
t = set_attrs(t, "diplomacy_button", sprite="GFX_valsora_deco_tb_diplomacy", position=(r2("diplomacy"), 0))
t = set_attrs(t, "non_delivering_contracts", position=(r2("diplomacy") + 7, 3))
t = set_attrs(t, "delivering_contracts", position=(r2("diplomacy") + 7, 26))
for k, b in [("trade", "trade_button"), ("construction", "construction_button"), ("production", "production_button"),
             ("deployment", "deployment_button"), ("logistics", "logistics_button"), ("officer", "officer_corp_button")]:
    t = set_attrs(t, b, sprite="GFX_valsora_deco_tb_" + k, position=(r2(k), 0))
t = set_attrs(t, "production_button_glow", sprite="GFX_valsora_deco_crown_glow", position=(r2("production") - 8, -8))
for k in ["army", "navy", "air"]:
    t = set_attrs(t, k + "_button", sprite="GFX_valsora_deco_overview_" + k,
                  position=(L.OVERVIEW[k] - L.RIGHT, L.OVERVIEW_Y - CMY))

# international market: the game swaps GFX_topbar_international_market onto diplomacy_button at runtime;
# that sprite's texture is replaced at its vanilla path (gfx/interface/topbar/toolbar/), so no .gui change

blocks = []
for cont in L.XP_KEYS.values():
    s_, e_ = find_block(t, cont)
    ls = t.rindex("\n", 0, s_)
    blocks.append(t[ls:e_])
    t = t[:ls] + t[e_:]
s_, e_ = find_block(t, "country_menu_window")
t = t[:e_] + "\n\t\t# experience badges (moved here from the top row so they draw above the army/navy/air buttons)" + "".join(blocks) + t[e_:]

header = """# Valsora Deco UI - top bar (art deco layout)
# Based on the HOI4 1.19 interface/topbar.gui. Every vanilla element and name is kept, because the
# engine finds them by name, but most are moved and re-skinned to the mockup's arrangement:
#   flag medallion (left) > crown buttons > labelled readouts > date cartouche > world tension ring
# with fuel/supply/convoys in a tray under the band, army/navy/air (experience as badges), command
# power and nukes in a tray on the right, and the land/navy/air experience containers moved after
# country_menu_window so they draw on top of the buttons.
# The decorative layer (band, tray, dividers, labels) is the block marked "Valsora Deco" below.
# Generated by make_topbar.py from layout.py; when Paradox updates topbar.gui, re-run it against
# the new vanilla file rather than hand-merging.

"""
t = header + t
assert t.count("{") == t.count("}"), (t.count("{"), t.count("}"))
GP.write_gui(MOD + "interface/topbar.gui", t)
print("topbar.gui", len(t.splitlines()), "lines")

# ================================================================ scripted-GUI windows on the top bar
def window(name, x, y, w, h, font, text, fmt="left", valign=False):
    gx, gy = G(x, y)
    va = "\n\t\t\tvertical_alignment = center" if valign else ""
    return f"""
	containerWindowType = {{
		name = "{name}_window"
		position = {{ x = {gx} y = {gy} }}
		size = {{ width = {w} height = {h} }}
		Orientation = "UPPER_LEFT"
		clipping = no
		alwaystransparent = yes

		instantTextBoxType = {{
			name = "{name}"
			position = {{ x = 0 y = 0 }}
			font = "{font}"
			text = "{text}"
			format = {fmt}
			maxWidth = {w}
			maxHeight = {h}
			fixedsize = yes{va}
			alwaystransparent = yes
		}}
	}}
"""


N = L.NAME
pp = next(it for it in L.STRIP if it["key"] == "pp")
fac = next(it for it in L.STRIP if it["key"] == "factory")
extras = ("# Valsora Deco UI - extra top bar windows driven by scripted GUIs\n"
          "# (common/scripted_guis/valsora_deco_topbar.txt). Positions are relative to the top bar.\n"
          "guiTypes = {"
          # country name: large tracked capitals, or a smaller cut for names with very long words
          + window("valsora_deco_country_name", N["x"], N["y"] - L.NAME_SLACK, N["w"], N["h"] + 2 * L.NAME_SLACK,
                   L.NAME_FONTS[0], "VAL_DECO_TB_COUNTRY_NAME", "centre", True)
          + window("valsora_deco_country_name_small", N["x"], N["y"] - L.NAME_SLACK, N["w"], N["h"] + 2 * L.NAME_SLACK,
                   L.NAME_FONTS[1], "VAL_DECO_TB_COUNTRY_NAME", "centre", True)
          # political power: daily gain, right-aligned under the label (the game's own number stays left)
          + window("valsora_deco_pp_daily", pp["text_x"], L.box_y_for_caps(L.SEC_FONT, 32), pp["text_w"], 18,
                   L.SEC_FONT, "VAL_DECO_TB_PP_DAILY", "right")
          # factories: civilian / military / naval counts with coloured diamonds
          + window("valsora_deco_factory_counts", fac["text_x"], L.VALUE_Y, fac["value_w"], 20, L.VALUE_FONT,
                   "VAL_DECO_TB_FACTORY_COUNTS")
          + "}\n")
GP.write_gui(MOD + "interface/valsora_deco_topbar_extras.gui", extras)
os.makedirs(MOD + "common/scripted_guis", exist_ok=True)
open(MOD + "common/scripted_guis/valsora_deco_topbar.txt", "w", encoding="utf-8", newline="\n").write(
    """# Valsora Deco UI - top bar additions. No 'dirty' variable, so the texts refresh every tick.
scripted_gui = {
	valsora_deco_country_name = {
		context_type = player_context
		window_name = "valsora_deco_country_name_window"
		parent_window_token = top_bar
		visible = { NOT = { valsora_deco_long_name = yes } }
	}
	valsora_deco_country_name_small = {
		context_type = player_context
		window_name = "valsora_deco_country_name_small_window"
		parent_window_token = top_bar
		visible = { valsora_deco_long_name = yes }
	}
	valsora_deco_pp_daily = {
		context_type = player_context
		window_name = "valsora_deco_pp_daily_window"
		parent_window_token = top_bar
	}
	valsora_deco_factory_counts = {
		context_type = player_context
		window_name = "valsora_deco_factory_counts_window"
		parent_window_token = top_bar
	}
}
""")

# ================================================================ which names need the smaller font
# (long_names.py; the Valsora build runs it as well, so a new country's long name is caught at once)
import long_names  # noqa: E402
long_tags, long_cosmetic = long_names.write(VALSORA, MOD)
print("long names:", sorted(long_tags), sorted(long_cosmetic))

# ================================================================ alerts row: below the band, under the menu buttons
if os.path.isfile(ALERTS):
    al = open(ALERTS, encoding="utf-8-sig").read().replace("\r\n", "\n")
    ax, ay = G(*L.ALERTS_START)

    def set_pos(text, name, x, y):
        pat = re.compile(r'(positionType\s*=\s*\{\s*name\s*=\s*"' + name + r'"\s*position\s*=\s*\{)[^}]*(\})')
        new, n = pat.subn(lambda m: f"{m.group(1)} x = {x} y = {y} {m.group(2)}", text)
        assert n == 1, name
        return new
    al = set_pos(al, "alerticon_startposition", ax, ay)
    al = set_pos(al, "alerticon_startposition_extended", ax, ay)
    al = set_pos(al, "alerticon_endposition", L.ALERTS_ROW_MAX, 0)
    al = ("# Valsora Deco UI - the game's alerts.gui with only the alert row moved below the top bar band\n"
          "# (alerticon_startposition, alerticon_startposition_extended, alerticon_endposition).\n"
          "# Generated by tools/make_topbar.py.\n\n" + al)
    assert al.count("{") == al.count("}")
    GP.write_gui(MOD + "interface/alerts.gui", al)

LOC = {"VAL_DECO_TB_COUNTRY_NAME": "[ROOT.GetName]",
       "VAL_DECO_TB_PP_DAILY": "[?political_power_daily|+=2]",
       "VAL_DECO_TB_FACTORY_COUNTS": "§W◆§![?num_of_civilian_factories|0] §O◆§![?num_of_military_factories|0]"
                                     " §C◆§![?num_of_naval_factories|0]"}
LOC.update({it["loc"]: it["label"] for it in L.STRIP})
for lang in ["english", "french", "german", "spanish", "braz_por", "polish", "russian", "japanese", "simp_chinese"]:
    d = MOD + f"localisation/{lang}/"
    os.makedirs(d, exist_ok=True)
    body = f"l_{lang}:\n" + "".join(f' {k}:0 "{v}"\n' for k, v in LOC.items())
    open(d + f"valsora_deco_ui_l_{lang}.yml", "w", encoding="utf-8-sig", newline="\n").write(body)

# ================================================================ sprites (.gfx)
SP = []


def sprite(name, tex, frames=1, effect=None, extra=""):
    s = f'\tspriteType = {{\n\t\tname = "{name}"\n\t\ttexturefile = "gfx/interface/valsora_deco/{tex}"\n'
    if frames > 1:
        s += f"\t\tnoOfFrames = {frames}\n"
    if effect:
        s += f'\t\teffectFile = "gfx/FX/{effect}"\n'
    s += extra + "\t}\n"
    SP.append(s)


def cornered(name, tex, w, h, bx, by):
    SP.append(f'\tcorneredTileSpriteType = {{\n\t\tname = "{name}"\n\t\tsize = {{ x = {w} y = {h} }}\n'
              f'\t\ttextureFile = "gfx/interface/valsora_deco/{tex}"\n\t\tborderSize = {{ x = {bx} y = {by} }}\n\t\ttilingCenter = yes\n\t}}\n')


def comment(c):
    SP.append(f"\n\t# ---- {c}\n")


comment("band, plates and trays")
cornered("GFX_valsora_deco_topbar_band", "topbar_band.dds", 196, L.BAND_TEX_H, 14, 20)
cornered("GFX_valsora_deco_topbar_band_shadow", "topbar_band_shadow.dds", 16, L.SHADOW_H, 4, 2)
sprite("GFX_valsora_deco_medallion", "topbar_medallion.dds", extra="\t\ttransparencecheck = yes\n")
sprite("GFX_valsora_deco_topbar_right", "topbar_right.dds", extra="\t\ttransparencecheck = yes\n")
sprite("GFX_valsora_deco_tray", "tray.dds", extra="\t\ttransparencecheck = yes\n")
sprite("GFX_valsora_deco_divider", "divider.dds")
cornered("GFX_valsora_deco_clear", "clear.dds", 8, 8, 2, 2)
cornered("GFX_valsora_deco_badge", "badge.dds", 16, 15, 4, 4)
sprite("GFX_valsora_deco_none", "none.dds")
comment("player flag at the game's native 82x52 (an own mask so the frame can differ from vanilla's)")
SP.append('\tmaskedShieldType = {\n\t\tname = "GFX_valsora_deco_player_flag"\n'
          '\t\ttextureFile1 = "gfx/interface/valsora_deco/flag_overlay.dds"\n'
          '\t\ttextureFile2 = "gfx/interface/valsora_deco/flag_mask.tga"\n'
          '\t\teffectFile = "gfx/FX/maskedflag.lua"\n\t}\n')
sprite("GFX_valsora_deco_decisions_seal", "decisions_seal.dds", 2)
SP.append('\t# production alert glow (crown-shaped; vanilla borrowed the decisions glow here)\n'
          '\tframeAnimatedSpriteType = {\n\t\tname = "GFX_valsora_deco_crown_glow"\n'
          '\t\ttexturefile = "gfx/interface/valsora_deco/crown_glow.dds"\n\t\tnoOfFrames = 2\n'
          '\t\tanimation_rate_fps = 1\n\t\tlooping = yes\n\t\tplay_on_show = yes\n\t\tpause_on_loop = 0.0\n'
          '\t\talwaystransparent = yes\n\t\teffectFile = "gfx/FX/buttonstate_blendframes.lua"\n\t}\n')
comment("invisible hover areas (the vanilla value boxes keep their tooltips)")
for w, h in sorted({(it["w"], 46) for it in L.STRIP} | {(it["w"], 30) for it in L.SECONDARY}):
    sprite(f"GFX_valsora_deco_hit_{w}x{h}", f"hit_{w}x{h}.dds")
comment("readout icons (frame counts mirror the vanilla sprites they replace)")
for k in ["pp", "stability", "war", "manpower", "convoy", "command", "nuke"]:
    sprite(f"GFX_valsora_deco_icon_{k}", f"icon_{k}.dds")
sprite("GFX_valsora_deco_icon_factory", "icon_factory.dds", 2)
sprite("GFX_valsora_deco_icon_fuel", "icon_fuel.dds", 3, "buttonstate.lua")
SP.append(f'\tprogressbartype = {{\n\t\tname = "GFX_valsora_deco_ratio_bar"\n\t\tcolor = {{ 1.0 1.0 1.0 }}\n'
          f'\t\tcolortwo = {{ 1.0 1.0 1.0 }}\n\t\ttextureFile1 = "gfx/interface/valsora_deco/ratio_fill.dds"\n'
          f'\t\ttextureFile2 = "gfx/interface/valsora_deco/ratio_bg.dds"\n\t\tsize = {{ x = {L.BAR_W} y = {L.BAR_H} }}\n'
          '\t\teffectFile = "gfx/FX/progress_startend.lua"\n\t}\n')
comment("crown buttons: frame 1 normal, frame 2 lit (vanilla toolbar sprites have 2 frames)")
for k in L.MENU:
    if k != "faction":  # the faction button keeps the vanilla sprite names (textures replaced at their paths)
        sprite(f"GFX_valsora_deco_tb_{k}", f"button_{k}.dds", 2)
for k in ["army", "navy", "air"]:
    sprite(f"GFX_valsora_deco_overview_{k}", f"overview_{k}.dds", 2)
comment("small buttons (single frame + buttonstate)")
for k in ["menu", "help", "playlist"]:
    sprite(f"GFX_valsora_deco_{k}_button", f"{k}_button.dds", 1, "buttonstate.lua")
comment("date cartouche and speed controls")
sprite("GFX_valsora_deco_date_bg", "date_bg.dds")
SP.append('\t# pulses between its two frames while paused, like vanilla GFX_date_pause_button\n'
          '\tframeAnimatedSpriteType = {\n\t\tname = "GFX_valsora_deco_date_paused"\n'
          '\t\ttexturefile = "gfx/interface/valsora_deco/date_paused.dds"\n\t\tnoOfFrames = 2\n'
          '\t\tanimation_rate_fps = 1\n\t\tlooping = yes\n\t\tplay_on_show = yes\n\t\tpause_on_loop = 0.0\n'
          '\t\teffectFile = "gfx/FX/buttonstate_blendframes.lua"\n\t}\n')
sprite("GFX_valsora_deco_speed_step", "speed_step.dds", 3, "buttonstate.lua")
sprite("GFX_valsora_deco_speed_down", "speed_down.dds", 1, "buttonstate.lua")
sprite("GFX_valsora_deco_speed_up", "speed_up.dds", 1, "buttonstate.lua")
gfx = ("# Valsora Deco UI - sprites for the art deco top bar (interface/topbar.gui and the extras .gui).\n"
       "# Generated by make_topbar.py.\n\nspriteTypes = {\n" + "".join(SP) + "}\n")
open(MOD + "interface/valsora_deco_topbar.gfx", "w", encoding="utf-8", newline="\n").write(gfx)

# ================================================================ fonts (.gfx)
TC = """		textcolors = {
			C = { 92 160 170 }
			L = { 195 176 145 }
			W = { 244 236 217 }
			B = { 110 150 230 }
			G = { 147 214 165 }
			R = { 238 140 126 }
			b = { 0 0 0 }
			g = { 176 168 146 }
			Y = { 231 183 90 }
			H = { 241 220 156 }
			T = { 246 238 220 }
			O = { 231 162 74 }
			K = { 44 31 10 }
		}
"""
FONTS = [("valsora_deco_value_17", "0xfff4ecd9", "readout values (U+25C6 is a diamond, for the factory counts)"),
         ("valsora_deco_value_15", "0xfff4ecd9", "tray values, world tension, daily political power"),
         ("valsora_deco_value_12", "0xfff4ecd9", "badges: experience, faction initiative"),
         ("valsora_deco_blank", "0xfff4ecd9", "invisible: hides the game's factory number, which a scripted GUI redraws"),
         ("valsora_deco_label", "0xffb7a680", "readout labels: small tracked capitals"),
         ("valsora_deco_date", "0xfff4ecd9", "date: Federo capitals"),
         ("valsora_deco_name_big", "0xffffffff", "country name: gilt is baked into the glyphs, so the colour is white"),
         ("valsora_deco_name", "0xffffffff", "country name, smaller cut for long words"),
         ("valsora_deco_heading_22", "0xfff4ecd9", "screens: character names"),
         ("valsora_deco_title_18", "0xffffffff", "screens: titles in gilt capitals (gilt baked in)"),
         ("valsora_deco_section_14", "0xffffffff", "screens: section headers in gilt capitals (gilt baked in)"),
         ("valsora_deco_title_24", "0xffffffff", "focus tree: window title in gilt capitals (gilt baked in)"),
         ("valsora_deco_title_30", "0xffffffff", "focus tree: the country's focus tree title in gilt capitals (gilt baked in)"),
         ("valsora_deco_italic_15", "0xffcbbf9f", "focus tree: the subtitle (Bodoni Moda italic)"),
         ("valsora_deco_italic_18", "0xffefe6d0", "superevent: the quote (Bodoni Moda italic)"),
         ("valsora_deco_heading_24", "0xfff6eedc", "politics: the leader's name"),
         ("valsora_deco_italic_13", "0xffcbbf9f", "politics: the leader's description (Bodoni Moda italic)"),
         ("valsora_deco_section_11", "0xffebd397", "screens: section labels (tracked capitals)"),
         ("valsora_deco_body_15", "0xffe8dfc8", "screens: body text"),
         ("valsora_deco_body_13", "0xffd9cfb6", "screens: small body text"),
         ("valsora_deco_option_14", "0xffe8dfc8", "event options: three lines fit the plate"),
         ("valsora_deco_menu_15", "0xffe7d3a0", "main menu buttons"),
         ("valsora_deco_menu_big", "0xff2a1e0a", "main menu: the gold Single Player button (dark text)")]
fg = ("# Valsora Deco UI - bitmap fonts (top bar and screens).\n"
      "# Generated from Josefin Sans and Federo (SIL Open Font License); see README.\n"
      "# The *_label, *_date and *_name fonts draw lowercase letters as capitals.\n"
      "# The map font is not defined here: it replaces the files behind vanilla \"tahoma_60\"\n"
      "# (gfx/fonts/hoi_mapfont4.fnt/.dds) without touching its definition.\n\nbitmapfonts = {\n")
for name, col, note in FONTS:
    fg += f'\n\t# {note}\n\tbitmapfont = {{\n\t\tname = "{name}"\n\t\tpath = "gfx/fonts/{name}"\n\t\tcolor = {col}\n{TC}\t}}\n'
fg += "}\n"
open(MOD + "interface/valsora_deco_fonts.gfx", "w", encoding="utf-8", newline="\n").write(fg)
print("extras, scripted gui, localisation, gfx written")
