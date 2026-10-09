# Problem log

Every error and problem met while building the Valsora mod, what caused it and how it
was fixed, newest first. Add to it whenever something goes wrong, in game or in the
build. "Check" means `scripts/check_mod.py` now catches it, so it can't slip back in.

## In-game problems (reported by the author)

**Atlas, second test: squares, no art, no country names** (2026-10-07, screenshot)
- Squares and a stair-stepped coast: the flattened heightmap (land 98, sea 89) put a
  cliff at every coast, and the terrain mesh is coarser than the map's pixels, so the
  coast and the surface snapped to its grid. The coarse field of the
  `GRADIENT_BORDERS_FIELD_COUNTRY_*` overrides may add to it. Fix: Valsora's own
  heightmap, base-game gradient borders.
- No art: the screenshots are at the zoom where HOI4 swaps the 3D terrain for its flat,
  shader-drawn map; textures don't reach it. Only shader files can (needs vanilla
  `gfx/FX` from the author's install).
- No country names: unknown. The font texture decodes correctly with an independent
  decoder; the kerning block (the base game's map font has none) was removed in case
  the game rejects it. Asked whether names showed without the submod, and for error.log.
- Also removed, as unverifiable: the victory-point symbol strip.

**The Atlas submod looked murky and blocky** (2026-10-07, author's screenshot)
- Causes: the political map mode draws an opaque colour over land and sea unless
  `NMapMode.MAP_MODE_TERRAIN_TRANSPARENCY` / `MAP_MODE_NAVAL_TERRAIN_TRANSPARENCY` are 1,
  so none of the paper, waterlines or sea lettering showed (flat grey-blue sea, country
  colours over grey); the 26 px country band is drawn on a coarse grid and stepped; the
  paper tile had chain lines that didn't divide its 256 px and four differently seeded
  copies, so it repeated as a grid of small squares; the town symbols' paper halos
  showed as white blobs when zoomed out.
- Fix: both defines at 1, band 2 / 9 px, one quiet seamless tile, smaller and fainter
  halos. Not yet re-tested in game.

**Rivers looked odd up close** (2026-10-06, author's screenshots)
- Cause: major rivers were drawn at widths 7–9 and minor ones at 4–5, which is far too
  wide beside Valsora's small (~150 px) provinces. Also, Merlovich's and Hoalepa's
  rivers, added later, had never had their provinces re-cut, so only 13–58 % of their
  pixels lay on a province border: the rivers ran through provinces and borders crossed
  them.
- Fix: widths are now major 7–8 (still "large rivers") and minor 3–4. `river_provinces.py`
  re-cut the 30 states whose rivers weren't on borders (now 91 % map-wide) and leaves
  states that are already aligned alone.
- Not fixed: a river running diagonally is a 1-pixel staircase (HOI4 requires
  edge-connected river pixels), which the game draws with slightly wavy banks.

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

**A flag update was missed** (2026-10-09)
- Cause: `import_flags.py` called a flag unchanged when its mean difference from the
  stored one was under 3, a test meant for resampled copies of the same picture.
  Serie's four new corner anchors cover 4 % of the flag (a mean difference of 2.65), so
  they were skipped (the author noticed). The same test had kept Claude's redraw of
  Krionik's flag once the author's own file had it.
- Fix: at the same size any visible pixel counts; at another size both are compared at
  164×104, and more than 0.5 % of pixels off by over 40 counts. Re-imported: Serie,
  Krionik, and the file's 82:52 copies of Garfield, Troc and Terrabis-Seran (the same
  pictures; the stored ones were 490×327). Rouental's 1180×700 original is kept. The
  older flag files were checked too: nothing else was missed.
- Also found: see-through pixels, which the game shows as holes in a flag (Harwick's
  top row and Royalist Illiricium's gaps were filled by hand before). Belka's emblem had
  a soft see-through edge, Riverraine's and Belekria's flags a 1-px see-through frame,
  Garfield's one faint row. `import_flags.py` now lays every see-through pixel over the
  nearest solid one before comparing and saving (`opaque`), so a re-import can't bring
  a hole back; Ponchomagnifico's faint top row (from the friend's build) was filled the
  same way. No flag in the build has see-through pixels now.

**Provinces outside a new outline were changed** (2026-10-09)
- Cause: `apply_outlines.py` tidies the provinces in a box reaching 64 px past the
  outlined area. Old provinces the box's edge clipped looked split there, and their
  pieces under 300 px were merged into neighbours: 77 px of 11 provinces in Belekria,
  Sminishia and Krionik that no outline touched, some into another state. Earlier runs
  likely did the same along their boxes' edges.
- Fix: only provinces the outlines made or cut are tidied; the run was redone, and the
  map file now differs from the upload only inside the new nations.

**Half a state cut off by a new line became part of another state** (2026-10-09)
- Cause: West Sminishia's new line cut one of Sminishia's states nearly in two.
  `pdn_tools.py cede` joined every part a split state loses to a neighbouring state that
  moved whole, which suits slivers, so West Sminishia came out as one state of 2,484 px,
  twice a usual state.
- Fix: a lost part of 600 px or more (`CEDED_STATE`) is now a state of its own; West
  Sminishia has two states.

**Vanilla's Mongolian and Belarusian name lists** (2026-10-09)
- Cause: vanilla's MON list is 14 Chinese and Manchu names, and its BLR list is part of
  the Russian one (`country_list.py` even called a Russian-named country Belarusian,
  since it matched cultures on the first dozen male names).
- Fix: Sanada uses the Buryat list (BYA, a Mongolic people) and Belka the Russian one;
  `country_list.py` matches on every male name.

**A moved border between countries without state lines** (2026-10-09)
- Cause: the author's new line between Hwitland (now Scealand) and Eschland (now Artzen)
  fitted no tool. `pdn_tools.py border` gives away a whole line-enclosed area, but
  Eschland's coast has no line, so that area ran on into the sea around Daravon's
  island; `regroup_states.py` only redraws countries with state lines of their own; and
  two of Eschland's states and three provinces straddled the line, so repainting the
  land alone would not have moved the border (each state goes whole to the country
  covering most of it).
- Fix: `pdn_tools.py cede FROM TO X,Y`. Only FROM's pixels are cut by the lines, the
  provinces are split along the line, and the part a split state loses joins a
  neighbouring state that moved whole. One sliver touched only another sliver, so they
  merge in turn (the first try stopped there, before saving).
- Also: the upload was the author's previous file plus their edits, so its game layers
  predated the 2026-10-08 changes; only their own edits were merged.
- The decoded copies of four maps filled the session's temporary disk (1.2 GB each); the
  check was redone by comparing the built files instead.

**Harwick's flag had an empty top row; Kampf's layer matched no country** (2026-10-08)
- Cause: in the author's flag file the top row of the Harwick layer is transparent (a
  see-through line along the top of the flag in game), and the layer "Kampf Empire" is
  not the country's name (the Kampfian Empire), so `import_flags.py` skipped it.
- Fix: the row was filled from the one below it; "kampf empire" is an `import_flags`
  alias.

**Labels on the Borders layer again, and another stale LEAVE pixel** (2026-10-08)
- The author's island labels (SO, MA, KE, DU, "Mahina (MA)" ...) were written on
  Necessary Borders: 88 small marks among three real new lines. As lines they would
  have cut the islets into scraps. Fix: every new mark but the three lines (found as
  8-connected pieces, checked by eye) moved to Necessary Names before apply_outlines.
- `LEAVE` still held (297, 1887), which now lies in Zwintern's patch, and (554, 1814),
  now Ungar: both would have stopped those patches being assigned, as happened with
  Transcainia. Fix: removed; every `LEAVE` pixel is now checked against the seeded
  patches before a run.

**Transcainia's land stayed Araseos** (2026-10-07, author's screenshot)
- Cause: `apply_outlines.py` had an old `LEAVE` pixel, (403, 1359), from 2026-10-05.
  The new lines put it inside Transcainia's patch, and `LEAVE` beat the seed, so the
  patch was skipped silently. A first rerun with the full 2026-10-07 `OWNERS` also
  re-cut Großlöwenburg (a seeded, finished country whose states regroup had joined
  across lines); that was thrown away.
- Fix: the old pixel was removed from `LEAVE`, and the rerun seeded only Transcainia
  (6 new states). Lesson: rerun with only the new seeds, and check `LEAVE` pixels still
  lie in the land they were meant for.

**Borders on the wrong layers, a gap, and unlabelled patches** (2026-10-07)
- Cause:
  - The borders of Sminishia, Gorbastan and Zukchiva were drawn on Necessary Names.
  - "PE" and "(TP)" were written on Necessary Borders.
  - A one-pixel gap south of Ostaria joined Ostaria to Hwitland.
  - Seven unlabelled patches the new lines enclosed went to `DEFAULT_OWNER`.
- Fix:
  - Line-shaped pieces on Names moved to Borders, and letter-sized pieces on Borders
    moved to Names.
  - The gap was found by listing loose line ends.
  - The unlabelled patches are on `LEAVE`.
  - Each nation's land was found from the author's labels: a name takes the bordered
    area around it, an island label the land nearest it. A rendered proposal was
    checked before `apply_outlines.py` ran.

**A 5 px province in Kurikia stopped the build; San Sierra's state lines leaked** (2026-10-05)
- Cause: re-running `regroup_states.py` over every drawn country left a 5 px scrap at
  (1242, 856). Separately, two of the author's San Sierra state lines had gaps, so
  neighbouring areas ran together into one state: one missing pixel, and one line
  stopping 4 px short of the coast.
- Fix: the scrap joined its neighbour in the same state, and the gaps were filled. To
  find dead-end line pixels, look for line pixels with at most one line neighbour that
  are not next to water.

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
