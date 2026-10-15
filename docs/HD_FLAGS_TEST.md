# Larger flags: the test version (1.5 times)

The author (2026-10-15), after the mockup (`deco_ui/art/proposals/hd_flags/`): "I'm not sure on it quite yet. Maybe
make a test version of the mod with the flag at 1.5?"

The test version is the mod with the game's large flags at **123 x 78** instead of 82 x 52. It is a separate zip,
`valsora_test_flags15.zip`, sent to the author and not kept in the repository; it installs in the mod's place (the same
`mod/valsora_test/` folder), so going back is installing `dist/valsora_test.zip` again.

## What differs from the mod

- **The flags.** Every large flag the build writes (`gfx/flags/*.tga`, the per-government ones too) is 123 x 78, made
  from the author's originals in `source/flags/` as before; the medium (41 x 26) and small (10 x 7) flags are the
  same. The game is told the size: `common/defines/valsora_flags.lua` sets `COUNTRY_FLAG_TEX_WIDTH` / `HEIGHT`.
  Seven flags exist only at 82 x 52 (Merlovich, Arvorenia, Atrocha, Hoalepa, Ponchomagnifico, Silvamar, the United
  States of Solitas): they are scaled up, so they look soft, as they would until their originals come.
- **The top bar's medallion** shows the flag at 1:1: the flag's frame is 139 x 94 instead of 98 x 68, the medallion
  26 px taller (174), the name under the flag and the decisions seal 26 px lower, and the side panels' notch round
  the medallion 26 px deeper. The "speed line" wings beside the frame are left out (no room), and the views under
  the medallion at the screen's left (the selected armies, air wings, operatives) start 26 px lower.
- **Everywhere else** the game draws the large flag in the boxes its own screens give it (82 x 52 and smaller), so
  there it is the larger texture shrunk, without smoothing: what those screens would look like unless each is re-laid
  for the larger flag.

## Things to check in game

1. The flag in the top bar: sharp, at 1:1, framed, the name and the decisions seal below it.
2. The diplomacy screen, the country selection at the start, the politics screen and the state panel: how the
   flags look there.
3. `error.log`: anything about flags or textures (`COUNTRY_FLAG_TEX_MAX_SIZE` is left at the game's 256; its comment
   ties it to the number of countries).
4. Loading time and memory, with about 200 larger flags.

## How it is built

`common.FLAG_SCALE` (the Valsora build) and `layout.FLAG_SCALE` (the Deco UI's tools) both read the environment
variable `VALSORA_FLAG_SCALE`; at 1, nothing changes (the mod is built byte for byte as before). Since 2026-10-15,
later, one command builds the test version beside the mod, after `sh scripts/run_all.sh`:

```sh
sh scripts/build_flags15.sh       # about 75 s: work/valsora_test_flags15.zip
```

It copies the Deco UI to `work/deco_flags15/` and draws the textures the flag's size changes there (11 of 240), builds
the mod into `work/build_flags15/` (`VALSORA_BUILD`), checks it and zips it. `build/`, `dist/` and `deco_ui/` are left
as they are, so the mod needs no rebuild afterwards (until then the test version was built over the mod, which then
had to be built again).

If the author takes the larger flags, the switch becomes the mod's own (`FLAG_SCALE = 1.5` in both places), the seven
small flags need their originals, and each screen that shows a large flag is re-laid to show it at 1:1.
