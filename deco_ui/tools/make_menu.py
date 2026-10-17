"""Build interface/frontendmainview.gui (art deco main menu) and the menu background registration.

    python make_menu.py "<HOI4 install folder>"

The VALSORA title and the gold world map are baked into a 1920x1440 background
(gfx/loadingscreens/valsora_menu.dds) registered through common/frontend/backgrounds, which the
game's background manager draws behind the menu (in game since v0.4.3). The menu buttons move from the
centred vertical panel into a row along the bottom of the screen, with the gold Single Player button in
the middle; the social links move to the top-left corner. Every element and name of the game's file is kept.
"""
import os
import sys

import guipatch as GP
from paths import MOD, VANILLA as VANILLA_DIR

ARG = sys.argv[1] if len(sys.argv) > 1 else VANILLA_DIR
src = os.path.join(ARG, "interface", "frontendmainview.gui")
t = open(src, encoding="utf-8-sig").read().replace("\r\n", "\n")
D = "GFX_valsora_deco_"
MENU, BIG = "valsora_deco_menu_15", "valsora_deco_menu_big"


def at(path, **kw):
    global t
    t = GP.set_attrs(t, path, **kw)


def button(path, sprite, x, y, font):
    """Re-skin a menu button: sprite, position and whichever font key the game's file uses."""
    s, e = GP.find_block(t, path)
    key = "buttonFont" if "buttonFont" in t[s:e] else "font"
    at(path, sprite=sprite, position=(x, y), **{key: font})


# ---------------------------------------------------------------- logo: the title is part of the background art
at("mainmenu_panel_upperleft>frontend_game_logo", sprite=D + "none")

# ---------------------------------------------------------------- main buttons: one row along the bottom
W, H = 1320, 140
MARGIN = 26          # gap between the panel and the bottom of the screen
# Anchored to the bottom-centre of the screen by explicit offsets, with no Origo. v0.4.3 used
# Origo = center_down, and in game (1.19) none of the buttons showed: the panel most likely landed just
# below the screen (its top-left at the bottom-centre).
# This is the pattern vanilla uses for its bottom-centred peace conference chat (CENTER_DOWN, x = -35%, y = -150).
at("mainmenu_panel_bottom", size=(W, H), position=(-W // 2, -(H + MARGIN)), Orientation="CENTER_DOWN",
   clipping="yes")   # clipping keeps the subscription widgets (parked outside the panel, below) out of sight
t = GP.remove_attr(t, "mainmenu_panel_bottom", "Origo")
t = GP.set_background(t, "mainmenu_panel_bottom", D + "clear")
at("mainmenu_panel_bottom>subscription_size", position=(W, H))     # the game resizes the panel to this
row = [("career_profile_button", 200), ("multi_player_button", 200), ("single_player_button", 420),
       ("settings_button", 200), ("credits_button", 200)]
x = 0
pos = {}
for name, w in row:
    big = name == "single_player_button"
    y = 26 if big else 34
    button(f"mainmenu_panel_bottom>{name}", D + ("mm_button_big" if big else "mm_button"), x, y, BIG if big else MENU)
    pos[name] = (x, y, w)
    x += w + 25
small = [("friends_button", 150), ("nudge_button", 150), ("exit_button", 150)]
x = (W - (sum(w for _, w in small) + 16 * (len(small) - 1))) // 2
for name, w in small:
    button(f"mainmenu_panel_bottom>{name}", D + "mm_button_small", x, 100, MENU)
    x += w + 16
cx, cy, cw = pos["career_profile_button"]
# the game's career profile star (GFX_icon_best_in_career, 36 px, centred on its position): a small badge on the
# button's upper right corner (at its right end, cy + 24, it covered the label: the author's screenshot, v0.5.1)
at("mainmenu_panel_bottom>career_profile_button_star", position=(cx + cw - 18, cy + 1), Orientation="UPPER_LEFT", scale=0.6)
sx, sy, sw = pos["single_player_button"]
at("mainmenu_panel_bottom>single_player_button_warn", position=(sx + sw - 46, sy + 16))
at("mainmenu_panel_bottom>version_label", position=(0, 108), font="valsora_deco_label", maxWidth=400, format="left")
at("mainmenu_panel_bottom>version_label_subscription_position", position=(0, 108))
at("mainmenu_panel_bottom>subscription_divider", sprite=D + "none")
for c in ["subscription_widget", "subscription_widget_simp_chinese", "subscription_widget_subscribed"]:
    at(f"mainmenu_panel_bottom>{c}", position=(W + 24, 0))

# ---------------------------------------------------------------- social links: top-left corner
# The game moves this window to one of its positionTypes when the menu opens (in v0.4.3 it sat over the
# middle of the map, as in vanilla). Anchored to the top-left corner instead, where the game's logo used to
# be; all three positionTypes point at the same spot. The rows draw at y -17 and +19 inside the window.
SOCIAL = (28, 44)
at("mainmenu_social_buttons", position=SOCIAL, Orientation="UPPER_LEFT")
t = GP.remove_attr(t, "mainmenu_social_buttons", "origo")
for p in ["position_without_social_gui", "subscription_position", "subscription_position_without_social_gui"]:
    at(f"mainmenu_social_buttons>{p}", position=SOCIAL)

# ---------------------------------------------------------------- single player panel (stays centred)
for name in ["sp_continue_button", "sp_new_button", "sp_load_button", "sp_tutorial_button", "sp_back_button"]:
    s, e = GP.find_block(t, f"mainmenu_single_player>{name}")
    key = "buttonFont" if "buttonFont" in t[s:e] else "font"
    at(f"mainmenu_single_player>{name}", sprite=D + "mm_button_panel", **{key: MENU})

t = ("# Valsora Deco UI - main menu (art deco layout). Generated by tools/make_menu.py from the game's\n"
     "# frontendmainview.gui: every element and name is kept; the logo is hidden (the title is in the\n"
     "# background art), the main buttons form a row along the bottom and the social links sit top left.\n\n" + t)
GP.check(t)
GP.write_gui(MOD + "interface/frontendmainview.gui", t)

# ---------------------------------------------------------------- background registration
# the loading screens make_loading.py draws were listed here in v0.10; out again in v0.10.1 (the author: "The globe map
# should be kept for later, and I might return to the others but the map's not finalized quite yet"; listed, the game
# also took the last of them for the frontend's background). To bring them back: their names here, and make_loading.py
# --into-mod.
LOADING = []
for _n in LOADING:
    assert os.path.isfile(MOD + f"gfx/loadingscreens/{_n}.dds"), f"{_n}.dds is missing: run tools/make_loading.py"
os.makedirs(MOD + "common/frontend/backgrounds", exist_ok=True)
open(MOD + "common/frontend/backgrounds/base_backgrounds.txt", "w", encoding="utf-8", newline="\n").write(
    """# Valsora Deco UI - the backgrounds: the main menu's, and (since v0.10) the four loading screens drawn from
# Valsora's map (tools/make_loading.py). The game shows these backgrounds on the main menu (the "Change background"
# picker chooses which, and cycles through several) and on the loading screen, which has no picture of its own.
# This file replaces the game's list, so only Valsora's are offered; the menu's is first, as the default.
# Format (from the game's own file): name_of_dds_file = { } with the .dds in gfx/loadingscreens,
# plus a GFX_<name>_small sprite (192x144) for the background picker.
valsora_menu = { }
""" + "".join(f"{n} = {{ }}\n" for n in LOADING))
open(MOD + "interface/valsora_deco_menu.gfx", "w", encoding="utf-8", newline="\n").write(
    "# Valsora Deco UI - main menu sprites (generated by tools/make_menu.py)\nspriteTypes = {\n"
    + "".join(f'\tspriteType = {{\n\t\tname = "{D}mm_{k[5:]}"\n\t\ttexturefile = "gfx/interface/valsora_deco/menu/{k}.dds"\n'
              '\t\tnoOfFrames = 3\n\t\teffectFile = "gfx/FX/buttonstate_onlydisable.lua"\n\t}\n'
              for k in ["menu_button", "menu_button_big", "menu_button_small", "menu_button_panel"])
    + "".join(f'\tspriteType = {{\n\t\tname = "GFX_{n}_small"\n'
              f'\t\ttexturefile = "gfx/interface/valsora_deco/menu/{n}_small.dds"\n\t}}\n' for n in ["valsora_menu"] + LOADING)
    + "}\n")
print("frontendmainview.gui written")
