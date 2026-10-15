#!/bin/sh
# The larger flags' test version (docs/HD_FLAGS_TEST.md): the mod with the game's large flags 1.5 times larger
# (123 x 78), built beside the mod, never over it. Run from the repo root, after sh scripts/run_all.sh (it uses the
# map that build read and the build's names for the Deco UI):
#     sh scripts/build_flags15.sh
# It makes
#   work/deco_flags15/            a copy of deco_ui/ drawn for the larger flag (only the textures the flag's size
#                                 changes are redrawn: the medallion, the notched panel headers ...)
#   work/build_flags15/           the mod, built as the mod is, with VALSORA_FLAG_SCALE=1.5
#   work/valsora_test_flags15.zip the zip for the author (not kept in the repository; it installs in the mod's place)
# build/, dist/ and deco_ui/ are left as they are, so the mod needs no rebuild afterwards. About 2 minutes.
set -e
D="$PWD/work/deco_flags15"     # absolute: the Deco UI's tools run from their own folder
ZIP=work/valsora_test_flags15.zip
[ -f build/valsora_test/descriptor.mod ] || { echo "build the mod first: sh scripts/run_all.sh" >&2; exit 1; }
# a fresh copy of the Deco UI (its previews and the game's files left out), so nothing of an older one stays
rm -rf "$D"
mkdir -p "$D/reference"
tar -C deco_ui --exclude=./build --exclude=./reference -cf - . | tar -C "$D" -xf -
ln -sfn "$PWD/deco_ui/reference/vanilla" "$D/reference/vanilla"
ln -sfn "$PWD/build/valsora_test" "$D/reference/valsora"
export VALSORA_FLAG_SCALE=1.5
VALSORA_BASE_DIR="$PWD/work/deco_base/" CHROMIUM_PATH="${CHROMIUM_PATH:-/opt/pw-browsers/chromium}" \
    python3 "$D/tools/build_all.py" validate_preview.py preview_screens.py preview_panels.py preview_focus.py \
    preview_armybar.py preview_events.py preview_game_fonts.py
export VALSORA_BUILD=work/build_flags15
python3 scripts/build_mod.py
VALSORA_DECO_ROOT="$D" python3 scripts/deco_ui.py
python3 scripts/check_mod.py
VALSORA_ZIP="$ZIP" python3 scripts/package.py
echo "the larger flags' test version: $ZIP"
