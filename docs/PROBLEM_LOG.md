# Problem log

Every error and problem met while building the Valsora mod, what caused it and how it
was fixed, newest first. Add to it whenever something goes wrong, in game or in the
build. "Check" means `scripts/check_mod.py` now catches it, so it can't slip back in.

## In-game problems (reported by the author)

**Royalist Illiricium's flag looked squashed and noisy** (2026-10-01)
- Cause: the flag is about 2:1 with fine gold filigree. The game's flag is 82×52
  (1.58:1), so it was squeezed sideways, and the filigree turned to noise at that size.
- Fix: redrawn at 82:52 with the same layout, the filigree simplified and the arms
  enlarged (`scripts/redraw_flags.py`). The original is kept in `source/flags/originals/`.

**Every country showed its leader's name on the map** (2026-09-30)
- Cause: the new leader characters were named `TAG_<subtype>` (e.g. `NSC_despotism`).
  HOI4 looks a country's name up as `TAG_<subtype>` before `TAG` (that is how vanilla
  names Germany under Nazism), so each leader's name became the country's name.
- Fix: leaders are now `TAG_leader_<subtype>`. Check: no character may be named
  `TAG_<ideology or subtype>`.

**Estande's green blended in with Rouental** (2026-09-30)
- Fix: Estande uses the red of its flag instead.

**Unzipping asked about 9 or 10 "files with the same name"** (2026-09-29)
- Cause: Windows ignores upper/lower case, so `ROU_COMMUNISM.tga` (cosmetic-tag flag)
  and `ROU_communism.tga` (ideology flag) were the same file there.
- Fix: cosmetic tags renamed `TAG_GOV_<IDEOLOGY>`. Check: no two files in the mod may
  differ only by case.

**Almost every country had the wrong map colour** (2026-09-29)
- Cause: HOI4 takes map colours from `common/countries/colors.txt`, not the colour in
  each country file; tags missing there get made-up colours. (Theocratic Rouental was
  right because cosmetic-tag colours come from `cosmetic.txt`.)
- Fix: the build writes its own `colors.txt` for every country.

**The fifth ideology overflowed the party list in the politics screen** (2026-09-29)
- Cause: vanilla's box holds four 16 px rows.
- Fix: the mod ships vanilla's `countrypoliticsview.gui` with 13 px rows. Check: the
  rows must fit.

**Superevent text was hard to read** (2026-09-29)
- Cause: the typewriter fonts draw dark text on the dark window.
- Fix: title and quote are coloured white (`§W…§!`).

**Superevent had no music and no background** (2026-09-29)
- Cause (music): `play_song` only finds songs that belong to a music station ("Song
  doesnt exist" in error.log). Fix: a "Valsora Radio" station with the song.
- Cause (background): vanilla's window sprite is see-through. Fix: a generated dark
  background with gold frames.

**"Failed to generate a portrait / name" and "unknown continent europe"** (2026-09-29)
- Cause: vanilla's generic portraits and names are keyed by Earth continents and
  countries, which don't exist on this map.
- Fix: portraits per Valsora continent and name lists per country (`cultures.py`).
  Scientists still have none, so "failed to generate a portrait … scientist" remains.

**Islands fused to their neighbours** (2026-09-28)
- Cause: shrinking the world to game size filled in narrow straits.
- Fix: straits are traced at full resolution and kept open (44 reopened). One more,
  closed into a lake west of Romanoddle, was reopened by hand on 2026-09-30.

**Communist Merlovich never took over after "Fucking Explode"** (2026-09-28)
- Cause: `recruit_character` only works in history files ("should only happen in
  game/history files" in error.log).
- Fix: both Merlovichs are recruited at game start; the focus promotes the communist.

**error.log: "Palette in rivers.bmp is probably not correct"** (first build)
- Cause: the 8-bit BMP header said 256 colours used; vanilla writes 0.
- Fix: `biClrUsed = 0` in every 8-bit BMP.

**error.log: a malformed empty row in buildings.txt** (2026-09-28)
- Cause: a trailing newline at the end of `buildings.txt`.
- Fix: no trailing newline.

## Map problems found while building

**A new country bigger than the rest of its continent was nearly skipped** (2026-10-01)
- Cause: `apply_outlines.py` treated the biggest patch touching a line as "the rest of
  the continent" and left it alone. Fraxhemark (96k px) was the biggest.
- Fix: patches with a seed, on the LEAVE list, or already done can't be "the rest".

**Regions cut up and land regions redrawn without being asked** (2026-09-30)
- The author asked for the oceans of their map "split up as needed"; I also regrouped
  every land region and cut the oceans into ~350k px pieces. The author wanted the land
  left alone and each ocean whole, to edit themselves.
- Fix: land regions restored exactly (pixel for pixel), each ocean is one region.
  Lesson: change only what was asked; when "as needed" is vague, do the minimum.

**Strategic regions from the author's ocean map landed in the wrong oceans** (2026-09-30)
- Cause: the reference maps (`ref_oceans.webp`, `ref_continents.webp`) show an older
  arrangement of the continents than the drawing, so they can't be laid straight over
  the game map. Averaging each continent's mapped position then put open water in
  unrelated oceans (a "Northern Friedlich" region mid-map).
- Fix: each continent's shift was fitted separately (Nonscio and Araseos too), and the
  continents vote for the ocean. Names of oceans running all the way round were
  scrambled by the map's wrap; they are now read left to right.

**The author's `.pdn` was older than the current one** (2026-09-30)
- Cause: the upload predated the sea zones and colour changes; applying it would have
  undone them.
- Fix: game layers are kept from the current file and the author's own layers
  (outlines, rivers, names) taken from the upload. The updated `.pdn` is now sent back
  after every change.

**Selto was drawn too small** (2026-09-30)
- Cause: only the patch between two lines became Selto; the author's older drawing
  (Notes layer) has it along the Piscary coast.
- Fix: five coastal Linterre states given to Selto (`pdn_tools.py give`).

**Rivers ran through the middle of provinces** (2026-09-30)
- Cause: HOI4 only applies a river crossing between two provinces.
- Fix: `river_provinces.py` re-cuts provinces so rivers run along their borders. Its
  first versions left 1-2 pixel provinces (a tiny state with nothing to split, stray
  pixels of neighbouring states); both are now handled.

**New state lines split existing states** (2026-09-30)
- Fix: `apply_outlines.py` re-cuts only the states a new line splits, keeping their
  country. At first it also re-cut Cardonia's island states (islets across water looked
  like splits) and merged small drawn pieces as islets; both fixed. Nudges of a pixel
  or two are too small to detect and are moved by hand.

**Outlines were meant as states, not provinces** (2026-09-29)
- Fix: every outlined patch is a state (big ones several), each cut into small provinces.

**Provinces split in two, too small, or crossing at one corner**
- Cause: cutting provinces leaves scraps.
- Fix: scraps merge into a neighbour; four-province corners are fixed by moving single
  pixels. Check: every province is one connected piece of at least 16 px, and no four
  meet at a corner (these crash the game).

**Rivers drawn as 2×2 blocks, stubs, or tributaries overwriting the main river**
- Fix: the river tracer shortcuts loops, drops branches under 6 px, and finds branches
  from the raw lines. Check: HOI4's river rules.

## Rules learned the hard way (all checked by `check_mod.py`)

- `definition.csv` needs Windows line endings (CRLF).
- `weatherpositions.txt` needs a `small` and a `big` row per region (not "large").
- Localisation files need UTF-8 with BOM.
- `descriptor.mod` and the launcher's `.mod` file must match.
- Vanilla files that name Earth places (tutorial, AI navy plans) are overridden with
  empty or cut-down versions.
