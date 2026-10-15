# Speed and size (2026-10-15)

The author, overnight: "just generally try to find ways to improve and speed up the modding process without
decreasing quality. In addition, is there any ways to improve the quality of the mod or cut down on unnecessary
bloat in the mod or GitHub?"

In short: a build takes about a minute now (five before), and gives exactly the same files. The mod itself has no
bloat worth cutting: the map files are what HOI4 needs at this size. The repository on GitHub is about 370 MB, a
third of it old copies of the mod's zip; two ways to stop that, both the author's call, are under "GitHub" below.

## Speed

Every change below gives the same files as before, checked byte for byte against a build made with the old code.

| step | before | after | how |
|---|---|---|---|
| `build_mod.py` | 238 s | 26 s | `work/regions.npz` is read once (`dict(np.load(...))`): an `.npz` file decompresses an array again on every access, and the unit positions asked for the province centres 82,565 times. Three of four full-map distance transforms are gone: one was computed and thrown away, one computed twice, and the third was only ever asked "is a province edge within 2 (or 3) px", which a 3x3 (5x5) erosion answers in a tenth of the time |
| `read_layers.py` | 57 s, every build | skipped while nothing it reads has changed | `scripts/stamp.py` (the script and its modules, `source/`, the Gazetteer's facts, the decoded layers); `FORCE=1 sh scripts/run_all.sh` reruns it |
| `package.py` | a new zip every build | the same zip for the same mod | fixed dates and permissions: the build rewrites every file, and the zip used to store their times, so an unchanged mod still made a new 21 MB file for git |
| Deco UI textures (`gen_textures.py`) | all 240 redrawn every time | only those whose drawing changed (0.7 s when none did); `--all` redraws them all | a signature per texture (its HTML, size, fonts and the files it embeds), kept in `deco_ui/texture_manifest.json`, which is committed, so a fresh clone (a new session, Merlo's) redraws nothing either. It also stops the anti-aliasing noise a redraw put into every texture, so a commit changes only what changed |
| Deco UI noise | restored by hand (`git checkout` of each texture that only changed by a few pixels) | `python3 tools/restore_noise.py` (`--dry` to list) | compares each changed texture with the committed one, colour weighted by alpha |
| Deco UI preview checks | 100+ warnings after the font switch, nearly all false | only real regressions | button texts are looked up in the game's localisation, `$VARIABLES$` and line breaks are handled, and the game's own fonts are judged against the game's own widths: text that overflows a box in the game too is the game's layout, not ours |

A whole build, `sh scripts/run_all.sh` (2026-10-15):

| step | seconds |
|---|---|
| `read_layers.py` | 57, or 0 when the map is unchanged |
| `build_mod.py` | 26 |
| `deco_ui.py` | 1 |
| `check_mod.py` | 13 |
| `export_canvas.py` | 6 |
| `package.py` | 14 (level 9; level 6 would take 3 s and make the zip 3 % larger, 21.1 MB instead of 20.4: kept at 9) |
| **in all** | **about 1 minute, 2 when the map changed** |

What is left to gain is small: `build_mod.py`'s province neighbours (7 s) and `package.py`'s compression (14 s).
The Deco UI's full build (`tools/build_all.py`) takes about a minute, nearly all of it previews.

## Later the same day: the round's chores in one command each

The author: "Is there anything else you can do to streamline the modding process to make it more efficient without
losing out on quality?" What took the most time in a round was no longer the build but the steps around it, done by
hand each time: the larger flags' test version, the Deco UI's build, publishing the Gazetteer, fitting flags, testing
`check_mod.py` and the Gazetteer page. Each is now one command, and each was checked to give what the manual way gave:

| job | before | after | how it was checked |
|---|---|---|---|
| the checks, previews and zip (`run_all.sh`) | 33 s, one after another | 15 s, side by side | the same zip; the zip now replaces the old one only if `check_mod.py` passes |
| the Deco UI (`build_all.py`) | 81 s | 31 s | every one of its 432 files and 48 previews byte for byte the same: the panel previews are drawn on four cores (41 s to 16 s), the previews side by side, the fonts too; each preview script no longer redraws the top bar's preview (`validate_preview.py` draws it only when it runs itself) |
| the larger flags' test version | 7 commands, then the mod built again over it (about 4 minutes) | `sh scripts/build_flags15.sh`, 75 s, beside the mod | its own `check_mod.py` passes; its flags 123 x 78, the mod's 82 x 52 |
| publishing the Gazetteer | 6 git commands | `sh scripts/publish_site.sh "message"` | it found the live site unchanged, as it was |
| testing `check_mod.py` | a one-off script each round | `python3 scripts/mutation_test.py`, 35 s, 50 breaks (45 at first) | it found a real gap at once: a misspelt scripted effect in our on_actions passed (fixed) |
| fitting a flag | a script per flag | `python3 scripts/fit_flag.py TAG picture` | the past fits' rules, tried on the fitted flags made too wide and too tall: fields, bands and stripes come back right, Ganden's border and Rouental's quarters are refused (they were done by hand) |
| testing the Gazetteer page | the tests lived in a session's scratch space, lost with it | `tests/gazetteer/run.py`, `traits.py` | they pass on the page as it is |
| setting up (Merlo's Claude, a new session) | "numpy, scipy, pillow, scikit-image" | `pip install -r requirements.txt`, versions pinned | the same versions give the same files |

`docs/HANDOFF_MERLO.md` (§7) has them as a table for Merlo's Claude, with the habits that keep a session quick: the
manual read by section, skipped steps left skipped, long steps in the background, every speed-up proven byte for byte.

## GitHub

The repository is 370 MB on GitHub (packed) and 163 MB checked out. Its history holds 1.8 GB of file versions; packed
the way GitHub stores them (each version as its difference from a similar one):

| what | versions | packed |
|---|---|---|
| `dist/valsora_test.zip`, the mod | 104 | 127 MB |
| `dist/*.png`, previews and collages | 190 | 101 MB |
| the removed submods' zips (Atlas, Victorianization, the separate Deco UI) | 13 | 28 MB |
| `source/HOI4 Mod Map.pdn` | 50 | 27 MB |
| everything else (scripts, sources, the Deco UI, the Gazetteer site's branch) | 2,250 | 51 MB |

A new zip adds about 1.2 MB once packed (most of its contents repeat the last one's), a new set of previews a few
MB. The repository has grown about 20 MB a day since it began (2026-09-28). GitHub recommends staying under 1 GB (5 GB at
most), so there is no hurry, but at this pace it gets there in about a month.

What could be done (none of it done, but the first):

1. **Done tonight:** the zip is reproducible, so a build that changed nothing adds nothing.
2. **The zip on GitHub's Releases page** instead of in the repository: each delivery a release ("Valsora 2026-10-15"),
   its zip attached; release files don't count towards the repository's size. The author would download from the
   Releases page (`https://github.com/Rouental/Valsora-HOI4/releases/latest` always points at the newest) instead of
   `dist/`. Claude would publish them through GitHub's API (not yet tried from a session). This changes where the
   author gets the mod, so it waits for their go-ahead. **Tried 2026-10-15, at the author's go-ahead:** a session
   like ours can't create releases (GitHub's proxy: "Creating, editing, or deleting releases is not permitted for this
   session type", HTTP 403). The author's choice then: "Keep it as is. When we start getting to more substantial
   builds, I'll start transferring to the releases page" (publishing them by hand, from the zip and notes Claude
   gives them).
3. **Fewer committed previews:** the routine previews (`dist/preview_*.png`, rewritten by every build) could stay
   in the ignored `work/`, with only the pictures made for the author committed. Also the author's call: they may
   browse `dist/` on GitHub.
4. **Cleaning the history** (`git filter-repo`): dropping the old zips from every past commit would take the
   repository to about 215 MB, the old previews too to about 115 MB. But it rewrites every commit: each one gets a
   new id (the docs name a few: the removed submods' last commits, which would need updating), the branch has to be
   force-pushed, and everyone with a clone (Merlo) has to clone again. Worth it only if the size becomes a problem,
   and only with the author's explicit go-ahead.

## The mod

260 MB unpacked, 20.4 MB zipped. 171 MB of it (9 MB zipped) is the map: `provinces.bmp` (39 MB), the 8-bit
bitmaps (heightmap, terrain, rivers, cities: 13 MB each), three colour maps (13 MB each), `world_normal.bmp` (10 MB)
and `unitstacks.txt` (15 MB, every unit position for 21,078 provinces). HOI4 needs each of them at the map's full
size, as it does for its own map, and most compress to under 1 MB each. The rest of the zip is the interface's
pictures (3 MB), the fonts (2 MB: 37 MB unpacked, the game's 28 redrawn tonight among them), the menu's background
(2 MB), the music (2 MB), portraits, flags and the scripts. The Deco UI's textures and fonts are uncompressed, as the
crisp gilt lines need; the menu's background (11 MB in memory) could be compressed to an eighth with a little loss,
which would save memory no one will miss. Nothing worth cutting.

## Quality

What would improve the mod most, in the order they matter:

- **Seeing it in game.** `check_mod.py` catches what the files can show and the previews what a layout can, but only
  the game shows the rest. The Deco UI v0.5.2 to v0.8, the two starts and the 2036 dates have not been seen yet; the
  checklists are in `deco_ui/valsora_deco_ui/README.txt`. Screenshots and `error.log` after a test are worth more than
  any check here.
- **Terrain.** It is plains everywhere: the biggest difference between the map and a playable one. A whole-map
  terrain from each continent's real-world model is ready as a test (`scripts/terrain_test.py`), waiting for the
  author's word ("do not add it to the mod yet"). It would also free province borders (`docs/BORDER_LIMIT.md`).
- **Test content to take out:** Devlon's 15 test spirits (`nations.TEST_SPIRITS`), once the politics screen has been
  seen with them.
- **A build number in the launcher** (an idea): the mod's version is always "0.2", so an installed build can't be
  told from another. A version made from the mod's contents (the same build, the same number) would show at a
  glance whether the newest zip is installed.
