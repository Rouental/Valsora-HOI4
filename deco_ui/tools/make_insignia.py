"""Build interface/theatreselector.gfx and gfx/army_icons/army_icons.txt (2026-10-20): the game's files, with the army
insignias' two sprites (GFX_theatre_army_shield and GFX_theatre_army_shield_selected) counting insignia_art.py's
frames (the game's 81, then the numbered shields and the gilt copies), and the list the insignia picker reads naming
the new frames, in order: the numbered shields tintable, the gilt copies `color_override = no` (insignia_art.py's
docstring has how the game colours them). The picker lists only what army_icons.txt names, which v0.12 had not
changed, so its numbered shields never showed. Everything else in both files is the game's (the strips themselves are
insignia_art.py's, at the game's paths).

    python make_insignia.py "<HOI4 install folder>"
"""
import os
import re
import sys

import insignia_art as IA
from paths import MOD, VANILLA as VANILLA_DIR

ARG = sys.argv[1] if len(sys.argv) > 1 else VANILLA_DIR
g = open(os.path.join(ARG, "interface", "theatreselector.gfx"), encoding="utf-8-sig").read().replace("\r\n", "\n")
for name in ("GFX_theatre_army_shield", "GFX_theatre_army_shield_selected"):
    pat = re.compile(r'(name\s*=\s*"' + name + r'"\s*\n\s*texturefile\s*=\s*"[^"]+"\s*\n\s*noOfFrames\s*=\s*)(\d+)', re.I)
    m = pat.search(g)
    assert m and int(m.group(2)) == IA.GAME_N, f"{name}: not the game's {IA.GAME_N} frames in its theatreselector.gfx"
    g = g[:m.start(2)] + str(IA.ALL_N) + g[m.end(2):]
open(MOD + "interface/theatreselector.gfx", "w", encoding="utf-8", newline="\n").write(
    "# Valsora Deco UI: the game's theatreselector.gfx, the army insignias counting the numbered shields "
    f"({IA.GAME_N} + {IA.NEW_N} frames; tools/make_insignia.py)\n" + g)
print(f"theatreselector.gfx written: army insignias {IA.GAME_N} -> {IA.ALL_N} frames")

# the list: the game's army_icons.txt (UTF-8 with its BOM), the new frames' blocks at the end of its `army` list
lst = open(os.path.join(ARG, "gfx", "army_icons", "army_icons.txt"), encoding="utf-8-sig").read().replace("\r\n", "\n")
start = re.search(r"^army\s*=\s*\{", lst, re.M)
assert start, "army_icons.txt: no army list"
depth, i = 0, start.end() - 1
while True:
    depth += {"{": 1, "}": -1}.get(lst[i], 0)
    if depth == 0:
        break
    i += 1
body = lst[start.end():i]
n = len(re.findall(r"^\ticon\s*=\s*\{", body, re.M))
assert n == IA.GAME_N, f"army_icons.txt: {n} army icons, not the game's {IA.GAME_N}"
lst = (lst[:i].rstrip("\n\t ") + "\n\t# Valsora Deco UI (tools/make_insignia.py): the numbered shields, then the gilt insignias\n"
       + "".join(IA.NEW_ICONS) + lst[i:])
os.makedirs(MOD + "gfx/army_icons", exist_ok=True)
open(MOD + "gfx/army_icons/army_icons.txt", "w", encoding="utf-8-sig", newline="\n").write(lst)
print(f"army_icons.txt written: {IA.GAME_N} + {len(IA.NEW_ICONS)} army icons")
