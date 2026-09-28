#!/bin/sh
# Rebuild everything from source/Valsora_06SEPT2026HOTFIX.pdn. Run from the repo root.
# The .pdn decode (readpdn.py) takes ~2 minutes and is skipped if work/pdn exists.
set -e
[ -f work/pdn/layer1.npy ] || python3 scripts/readpdn.py source/Valsora_06SEPT2026HOTFIX.pdn work/pdn
python3 scripts/blocks.py        # land mask, continents, Antarctica removal
python3 scripts/layout.py        # scale and spread the continents
python3 scripts/compose.py       # game-resolution land / sea / lakes
python3 scripts/provinces.py     # placeholder square provinces
python3 scripts/regions.py       # states and strategic regions
python3 scripts/build_mod.py     # every mod file
python3 scripts/check_mod.py     # verify against HOI4's rules
python3 scripts/export_canvas.py # drawing canvases and previews
python3 scripts/package.py       # dist/valsora_test.zip
