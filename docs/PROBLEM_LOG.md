# Problem log

Every error and problem met while building the Valsora mod, what caused it and how it
was fixed, newest first. Add to it whenever something goes wrong, in game or in the
build. "Check" means `scripts/check_mod.py` now catches it, so it can't slip back in.

## In-game problems (reported by the author)

**Every army started with no manpower; opinion modifiers showed their raw keys** (2026-10-04, author)
- Cause: an OOB division takes its men from the country's manpower pool, and the pools
  were tiny: state population was 20 per map pixel (75 million people in the world,
  7,000 in Seigne). `start_manpower_factor` didn't prevent it. The opinion modifiers
  had no localisation, so the game showed `valsora_against_communism`.
- Fix: population is 300 per pixel; each country gets `add_manpower` for its starting
  divisions before `set_oob`; the modifiers are named "Seran Ties" and "Seran Biases".

**Aislada's drawn states were split, and Kurikia's eastern island was missed** (2026-10-04, author)
- Cause: Aislada's regions were cut into one state per city, so regions with two cities
  became two states; the island east of Kurikia has no outline, so nothing seeded it.
- Fix: Aislada's regions are one state each (`regroup_states.py`, `DRAWN_PLACEHOLDERS`);
  the island was given to Kurikia as one state.

**A city name misread** (2026-10-04): "Grande Rebette" is Grande Reliette.

**Drawn states cut into many small ones** (2026-10-04, author: "I want to cut back on the number of states")
- Cause: `apply_outlines.py` cut every drawn area over 1,000 px into ~650 px states,
  even where the author had drawn the states themselves.
- Fix: `regroup_states.py` makes each drawn area one state wherever a country has its
  own state lines; blank countries get ~1,300 px states. 1,346 states became 1,208.

**The Marches had the wrong flag** (2026-10-04)
- Cause: the three-lozenge flag was taken for The Marches; the author's flag file names
  it "Duchy of the Mountains" and The Marches' is the diagonal sword ("Marchers").
- Fix: flags now come from the author's flag file by layer name (`import_flags.py`).

**Country names written on the border layer** (2026-10-04)
- Cause: "Sicilianzo" and "Danelaw" were on Necessary Borders, so their letters closed
  off tiny patches.
- Fix: the letters were moved to Necessary Names.

**Two more islands fused to the land next to them** (2026-10-04, author)
- Cause: in the original drawing these islands touch their neighbours only at a corner
  pixel or through 1-2 px channels, so the strait tracing of 2026-09-28 saw one landmass
  and shrinking closed the channel.
- Fix: `pdn_tools.py channel` cuts the cheapest water-to-water path (fewest land pixels)
  between two sea pixels: the AN island at (654, 1430) and the larger island south of it
  (11 px), and a 2 px bridge at (932, 1492).

**The author's .pdn had lost Locus and the Moelle/Maïeul split** (2026-10-04)
- Cause: the upload was edited from a copy made before 2026-10-02, so its game layers
  (Provinces, States, Countries) were older in the north-east.
- Fix: as the working rules say, the current game layers were kept and only the
  author's own layers (outlines, names, rivers, cities) taken from the upload.

**San Sierra was skipped by apply_outlines** (2026-10-04)
- Cause: `LEAVE` still held a pixel of "the land south of Entroterra and Estande" from
  2026-10-01, which is San Sierra.
- Fix: that entry was removed.

**Rouental's divisions started with next to no manpower** (2026-10-02)
- Cause: an OOB division without `start_manpower_factor` takes its manpower from the
  country's pool, and the Feudal Army (−80 % recruitable population) leaves that tiny.
- Fix: every OOB division sets `start_manpower_factor = 1.0`.

**Lanzerac and Guedelon left the Association (and the Alliance of the Vale) at once** (2026-10-02)
- Cause, most likely: they are the only democratic members of a monarchist-led
  faction, with 20 % monarchist support; vanilla needs 30 % for the leader's ideology
  (`IDEOLOGY_JOIN_FACTION_MIN_LEVEL`). Not yet confirmed in game.
- Fix: they start with 30 % monarchists. The Reibonnaise nations also get +20 opinion
  of each other and an AI alliance strategy.

**The fief overlay sorted fiefs into the wrong kind of vassal** (2026-10-02)
- Cause: the 14 headings of `rouental_fiefs.txt` were read as vassals. They are cultural
  groups: every fief is a vassal of the Crown, and the governorates have no power.
- Fix: the docs and data now call them cultural groups
  (`source/rouental_fiefs_by_state.json`, renamed from `rouental_vassals.json`). The
  fief → state placement stands; levy tiers wait for each fief's title.

**Rempart and Tocsin didn't touch, though the drawing has them touching** (2026-10-02)
- Cause: the author's lines leave a corridor 2–3 px wide from Rempart up to Tocsin. A
  state is the majority of each province, and the corridor's pixels belonged to a
  province lying mostly in the neighbouring state, so the corridor went with it.
- Fix: the 17 corridor pixels were given to Rempart's nearest province on the
  Provinces layer (two 1 px leftovers joined their neighbour). Very narrow drawn
  pieces can lose out this way; a scan found a few other spots worth a look.

**Some new rivers were missing, and some minor rivers came out major** (2026-10-01)
- Causes, in `rivers.py`:
  - A whole river got one size, from the majority of its pixels, so a minor stretch
    drawn onto a mostly major river (the Prestozza branch) became major.
  - Where the main river takes a diagonal step it gets a corner pixel. When that
    corner was exactly where a tributary joined (the Gallyo river), the tributary was
    taken for part of the main river and skipped.
  - A tributary ending next to a 45° stretch of its river can't join it with one
    pixel without making the river two pixels thick (the Ossilia river), so it was
    dropped.
- Fix: each pixel's size follows the layer it was drawn on; branches off a corner
  pixel are followed; a tributary that stops short is joined by the shortest clean
  path of up to 6 pixels. Every drawn line is now traced.

**Royalist Illiricium's redrawn flag** (2026-10-01)
- The author preferred their original; it is back, as sent.

**Royalist Illiricium's flag looked squashed and noisy** (2026-10-01)
- Cause: the flag is about 2:1 with fine gold filigree. The game's flag is 82×52
  (1.58:1), so it was squeezed sideways, and the filigree turned to noise at that size.
- A redraw at 82:52 was tried and rejected by the author (see above).

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

**`apply_outlines.py` ran for hours, and nearly gave Solitas land to Terrabis-Seran** (2026-10-05)
- Cause: the clean-up of cut provinces compared every province against the whole
  window around the new outlines. This time the window ran from Cascadia to Harwick,
  about 1,900 × 1,200 px with thousands of provinces. Separately, three Solitas patches
  that the friend's outlines had closed off were unseeded, so they would have gone to
  `DEFAULT_OWNER`.
- Fix: each province is now checked inside its own bounding box. The three patches are
  on `LEAVE`. The script lists unseeded patches before writing; read that list.

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
