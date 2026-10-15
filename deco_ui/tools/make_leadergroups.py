"""Build interface/leadergroups.gui (v0.7): the army bar's division counts on the frames' plaques.

    python make_leadergroups.py "<HOI4 install folder>"

The army bar is re-skinned by textures at the game's paths (gen_textures.py, the 'lg_' keys); the one thing a
texture can't do is place the game's count, which sat 3 px above the plaque and 1 px left of its centre (the user,
from the v0.7 preview: "nor are the numbers [centred]"). Both counts, an army's and an army group's, get the plaque's
box (layout_armybar), centred both ways, in the mod's value font. Every element of the game's file is kept.
"""
import os
import sys

import guipatch as GP
import layout_armybar as LA
from paths import MOD, VANILLA as VANILLA_DIR

ARG = sys.argv[1] if len(sys.argv) > 1 else VANILLA_DIR
t = open(os.path.join(ARG, "interface", "leadergroups.gui"), encoding="utf-8-sig").read().replace("\r\n", "\n")
for win, box in (("leader_groups_portrait_window", LA.COUNT_ARMY), ("army_group_portrait_window", LA.COUNT_GROUP)):
    t = GP.set_attrs(t, f"{win}>divisions_count", position=(box["x"], box["y"]), maxWidth=box["w"],
                     maxHeight=box["h"], format="centre", vertical_alignment="center", font=LA.COUNT_FONT)
GP.write_gui(MOD + "interface/leadergroups.gui", t)
print("leadergroups.gui written")
