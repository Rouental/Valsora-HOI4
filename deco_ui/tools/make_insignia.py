"""Build interface/theatreselector.gfx (2026-10-20): the game's file, with the army insignias' two sprites
(GFX_theatre_army_shield and GFX_theatre_army_shield_selected) counting insignia_art.py's frames, the game's 81 and the
numbered shields after them. The insignia picker lists every frame of the sprite; everything else in the file is the
game's, pointing at the game's textures (the army insignia strips themselves are insignia_art.py's, at the game's
paths).

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
