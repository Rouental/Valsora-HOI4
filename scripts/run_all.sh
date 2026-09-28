#!/bin/sh
# Rebuild everything. Run from the repo root.
#
# If source/HOI4 Mod Map.pdn exists (the game-sized map the author edits), the map is
# read from it directly. Otherwise it is built from the author's original .pdn by
# moving and scaling the continents (blocks.py + layout.py), as the first builds were.
set -e
if [ -f "source/HOI4 Mod Map.pdn" ]; then
    if [ ! -f work/pdn_mod/layer1.npy ] || [ "source/HOI4 Mod Map.pdn" -nt work/pdn_mod/layer1.npy ]; then
        python3 scripts/readpdn.py "source/HOI4 Mod Map.pdn" work/pdn_mod
    fi
else
    [ -f work/pdn/layer1.npy ] || python3 scripts/readpdn.py source/Valsora_06SEPT2026HOTFIX.pdn work/pdn
    python3 scripts/blocks.py        # land mask, continents, Antarctica removal
    python3 scripts/layout.py        # scale and spread the continents
fi
python3 scripts/compose.py       # game-resolution land / sea / lakes
python3 scripts/provinces.py     # placeholder square provinces
python3 scripts/regions.py       # states and strategic regions
python3 scripts/build_mod.py     # every mod file
python3 scripts/check_mod.py     # verify against HOI4's rules
python3 scripts/export_canvas.py # drawing canvases and previews
python3 scripts/package.py       # dist/valsora_test.zip
