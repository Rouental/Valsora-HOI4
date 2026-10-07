#!/bin/sh
# Rebuild everything. Run from the repo root.
#
# The map comes from source/HOI4 Mod Map.pdn, the game-sized paint.net file the author
# edits: one layer per kind of map data (see docs/EDITING.md). Without that file the
# placeholder map is built from the author's original drawing instead, by moving and
# scaling the continents, as the first builds were; make_game_pdn.py then turns that
# build into a fresh "HOI4 Mod Map.pdn".
set -e
if [ -f "source/HOI4 Mod Map.pdn" ]; then
    if [ ! -f work/pdn_game/layers.txt ] || [ "source/HOI4 Mod Map.pdn" -nt work/pdn_game/layers.txt ]; then
        python3 scripts/readpdn.py "source/HOI4 Mod Map.pdn" work/pdn_game
    fi
    python3 scripts/read_layers.py   # layers -> provinces, states, regions, owners
else
    [ -f work/pdn/layer1.npy ] || python3 scripts/readpdn.py source/Valsora_06SEPT2026HOTFIX.pdn work/pdn
    python3 scripts/blocks.py        # land mask, continents, Antarctica removal
    python3 scripts/layout.py        # scale and spread the continents
    python3 scripts/compose.py       # game-resolution land / sea / lakes
    python3 scripts/provinces.py     # placeholder square provinces
    python3 scripts/regions.py       # states and strategic regions
fi
python3 scripts/build_mod.py     # every mod file
python3 scripts/check_mod.py     # verify against HOI4's rules
python3 scripts/export_canvas.py # previews
python3 scripts/package.py       # dist/valsora_test.zip
