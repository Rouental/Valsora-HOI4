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
    # layers -> provinces, states, regions, owners; skipped when nothing it reads has changed (FORCE=1 reruns it)
    if python3 scripts/stamp.py fresh read_layers; then
        echo "read_layers.py: its inputs are unchanged, so work/ is kept (FORCE=1 to rerun)"
    else
        python3 scripts/read_layers.py
        python3 scripts/stamp.py save read_layers
    fi
else
    [ -f work/pdn/layer1.npy ] || python3 scripts/readpdn.py source/Valsora_06SEPT2026HOTFIX.pdn work/pdn
    python3 scripts/blocks.py        # land mask, continents, Antarctica removal
    python3 scripts/layout.py        # scale and spread the continents
    python3 scripts/compose.py       # game-resolution land / sea / lakes
    python3 scripts/provinces.py     # placeholder square provinces
    python3 scripts/regions.py       # states and strategic regions
fi
python3 scripts/build_mod.py     # every mod file
python3 scripts/deco_ui.py       # the Valsora Deco UI into the mod (common.DECO_UI)
# The checks, the previews and the zip at once (each only reads the build: 15 s instead of 33). The new zip is
# written beside the old one and takes its place only if check_mod.py passes: a clean check is the bar for shipping.
ZIP=${VALSORA_ZIP:-dist/valsora_test.zip}
mkdir -p work/logs "$(dirname "$ZIP")"
python3 scripts/check_mod.py > work/logs/check_mod.log 2>&1 &     # verify against HOI4's rules
CHECK=$!
python3 scripts/export_canvas.py > work/logs/export_canvas.log 2>&1 &   # previews
CANVAS=$!
VALSORA_ZIP="$ZIP.new" python3 scripts/package.py > work/logs/package.log 2>&1 &   # the zip
PACK=$!
failed=""
wait $CHECK || failed="$failed check_mod.py"
cat work/logs/check_mod.log
wait $CANVAS || failed="$failed export_canvas.py"
cat work/logs/export_canvas.log
wait $PACK || failed="$failed package.py"
if [ -n "$failed" ]; then
    rm -f "$ZIP.new"
    echo "failed:$failed (logs in work/logs/); $ZIP is unchanged" >&2
    exit 1
fi
mv "$ZIP.new" "$ZIP"
echo "wrote $ZIP ($(du -m "$ZIP" | cut -f1) MB): the checks passed"
