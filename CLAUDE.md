# Valsora — HOI4 total conversion

Turns the author's hand-drawn fictional world (paint.net `.pdn`) into a Hearts of Iron IV
map. Game version: **1.19.3**. The mod installs as `mod/valsora_test` in
`Documents/Paradox Interactive/Hearts of Iron IV/` (on the author's machine Documents sits
under OneDrive — keep that segment in any absolute path). Valsora takes place in **2036**:
the game starts on 1 January 2036 (see "2036" under Decisions worth keeping).

The map is the author's drawing at game size, 5120×2560: its land, rivers and the countries and states they
outline region by region (161 nations on the map, 183 countries with the releasables and the civil war's), and the
sea provinces their friend Merlo drew. Rouental is the built-out nation (leaders, focus tree, civil war, army); the
rest have set rulers and the game's generic content, moved to 2036. The interface is the author's art deco design,
the Valsora Deco UI (`deco_ui/`). The Gazetteer, a web site, lets the author's friends fill in their own nations.

**Where things are written down:**
- this file: the manual (rules, decisions, the pipeline, what HOI4 requires) and where things stand;
- `docs/NATIONS.md`: every nation, who named and decided what; `docs/HISTORY.md`: the build's history, date by
  date; `docs/PROBLEM_LOG.md`: every problem, its cause and its fix;
- `docs/EDITING.md`: the author's guide to the `.pdn`; `docs/GAZETTEER.md`: the Gazetteer (and how it works, for Claude:
  `docs/GAZETTEER_INTERNALS.md`);
  `docs/HANDOFF_MERLO.md`: for Merlo's Claude; `deco_ui/CLAUDE.md`: the interface's own manual;
- proposals waiting for the author: `docs/TECH_TREE_2036.md`, `docs/BORDER_LIMIT.md`,
  `deco_ui/art/proposals/`, the larger flags' test version (`docs/HD_FLAGS_TEST.md`); plans: `docs/ROUENTAL_ARMY.md`,
  `docs/CIVIL_WAR_NOTES.md`.

## Layout

```
source/     the author's .pdn files, flags, portraits, names, the Gazetteer's facts, vanilla's changed files
scripts/    the pipeline (run_all.sh runs it all; common.py holds every setting)
dist/       what gets committed for the author: the mod zip, drawing canvases, previews
work/       intermediates, gitignored (decoded .pdn layers are 3.5 GB)
build/      the unzipped mod, gitignored
deco_ui/    the Valsora Deco UI, the mod's interface (its own CLAUDE.md; see below)
docs/       the records (nations, history, problems), the author's guides, proposals
```

## The editable map: `source/HOI4 Mod Map.pdn`

The author edits this file from now on; `docs/EDITING.md` is their guide (keep it in
step with `read_layers.py`). It is exactly game size (5120×2560, one pixel = one map
pixel), and each layer is one kind of game data, found **by name**. Bottom to top:
Heightmap, Terrain, Rivers, Continents, Provinces, Strategic Regions, Ocean Province Lines
(Merlo's sea borders, from 2026-10-12: read by `sea_provinces.py`, not by the build), States,
Countries, and "Notes (ignored by the build)". **The author's editing layers are named "Necessary …"**
(from 2026-10-01): Necessary Borders (country lines), Necessary States (state lines; it
was called "Necessary Provinces" before), Necessary Names (labels; a short line points
to an island), Necessary Major / Minor Rivers (plain river lines; the old "Major Rivers"
/ "Minor Rivers" still work), Necessary Cities (from 2026-10-01: a dot of any colour
but black per city, its name written beside it in black). Necessary Provinces and Necessary Terrain are reserved for
later detail and not read yet. "… Reference" layers and "Background" (white) are only
for the author. Unknown layer names are ignored.
- **Provinces**: one colour per province, which is also its provinces.bmp colour. Ids
  are assigned in reading order (first pixel, row by row), so they shift when provinces
  change. Refer to places by `capital:TAG`, never by id.
- **Terrain**: vanilla terrain.bmp palette colours. Ocean (index 15) means sea, the
  lakes colour (14) means lake, and anything else is land. The game gets 15 for all
  water. A province's kind and terrain type are the majority of its pixels.
- **Everything else is decided per province by majority.** Blank provinces on States,
  Countries, Strategic Regions or Continents take the nearest painted area of the right
  kind, with a note. Region colours count only on their own kind (a colour is a sea
  region if most of its pixels are sea). A blank land province joins its state's region.
- **Countries** are matched by exact colour to `common.COUNTRIES`, per state; a country
  owning no state is left out of the mod.
- **Errors and notes.** Real errors (split or tiny provinces, black or transparent
  pixels, mixed or split regions, a state in two regions) stop the build with a numbered
  list of (x, y) pixel positions. X-crossings are repaired automatically.
- **Cities** (`read_layers.read_cities`): each dot is a city in the land province under
  it (or the nearest). The names are pixels, so they are typed into
  `source/city_names.json` ("x,y" of the dot → name; a dot moved up to 12 px keeps its
  name). An unnamed dot, two in one province, or a repeated name stops the build. In
  `build_mod.py` the first city of a state becomes its victory point (worth `CITY_VP` =
  5, or 10 as the capital), and further ones are extra victory points. Capitals are
  set by `nations.CAPITALS` (the dot's pixel); any other country's capital is the
  sizeable state nearest the centre of its land, chosen again on the continent holding
  most of it if it falls on one holding under a third (2026-10-10: Estande's had drifted
  onto its islands east of Terreich). Winterthorn CRD, Venezzo CTF, Alqira ILR, Malin MZG,
  Prestozza ETR, Monte Gnolia KIL (author, 2026-10-01), besides Rêverie ROU. First nine: Winterthorn, Vair, Carcarelle, Rêverie, Venezzo, Alqira,
  Malin, Prestozza, Monte Gnolia.
- **Heightmap**: clamped to 94 / 96 on the wrong side of sea level.
- **Rivers** (`rivers.py`). HOI4 needs rivers 1 px wide, edge-connected only, with
  exactly one green source per system and red flow-ins where tributaries join (vanilla
  wiki). The author draws plain lines on "Major Rivers" / "Minor Rivers" (any colour).
  `rivers.trace` converts them:
  - it skeletonises the lines and picks the mouth as the end nearest water, extending
    it up to 8 px to reach the water;
  - the main stem runs to the farthest end, preferring major pixels; side branches
    become tributaries, recursively;
  - diagonal steps get corners, and loops/U-turns are shortcut;
  - branches under 6 px are dropped;
  - widths: major 7→8, minor 3→4 (7+ is a large river), per pixel by the layer it was
    drawn on, so a river can change size along its course (`MAJOR_WIDTH`,
    `MINOR_WIDTH`; 7→9 and 4→5 until 2026-10-06, far too wide beside Valsora's small
    provinces in the author's screenshots);
  - a tributary that stops short of its river (or ends next to a 45° staircase, which
    no single pixel can join without a 2×2 block) is linked by the shortest clean path
    of up to 6 pixels, from its end or up to 4 pixels back; branches joining at a
    corner pixel the main river gained are followed too (2026-10-01 fixes).
  The exact-palette "Rivers" layer wins where set, and river pixels on water are
  dropped. `check_mod.py` checks the result with `rivers.problems`.
- **Provinces follow rivers** (`river_provinces.py`, by hand, author's request
  2026-09-30). HOI4's river penalty only applies to a river *between* the provinces of
  an attack. After a build, the script takes the drawn rivers from `work/world.npz`,
  splits each crossed state's land into banks, cuts each bank into ~150 px organic
  provinces, gives river pixels to the province beside them, then merges stray bits.
  States do not change. First run: 37 states, 113 provinces became 111; river pixels on
  a province border went from 77 % to 90 % (the rest are corner pixels of diagonal
  steps, still along the border). Rerun it whenever rivers or outlines change. It only
  re-cuts states where under 85 % of the river pixels lie on a border (`ALIGNED`);
  2026-10-06 it fixed Merlovich's and Hoalepa's rivers (13–58 % → 71–100 %; 91 % map-wide).
- **Outlines → states** (`apply_outlines.py`, run by hand, not by `run_all.sh`).
  The author draws 1-px country borders on "Borders" and state lines on "Necessary
  Provinces" (the author's layer name; they are **states**, author's correction).
  - Every enclosed patch becomes a state. Patches over 2,000 px are k-means split into
    ~1,300 px states that fill the same shape (1,000 / 650 until 2026-10-04: the author
    wants fewer states). This only happens where the author left a country's state
    lines blank.
  - **The author's own state lines are kept as drawn** (2026-10-04: "do not split any
    states that I have created"). `regroup_states.py` makes every drawn area one state
    in each country that has state lines inside it (two of its areas sharing at least
    8 px of line, both 150+ px): first run CRD 22, KRK 11 (+ islands), LNT 10, ROU 54,
    SSA 7 (+ islands), STO 4. `apply_outlines.py` no longer re-cuts a finished country
    (`RECUT_DONE = False`) unless `OWNERS` seeds a new country inside it.
  - Every state is cut into ~190 px provinces (`PROVINCE_AREA`; ~150 px for a granular
    map until 2026-10-12, when HOI4's border limit was hit: see Province borders below;
    placeholder bricks elsewhere are 1,024 px). Pieces are forced 4-connected.
  - **Borders are organic** (`organic.py`, from 2026-09-29 on). k-means places the
    pieces; then each grows from the pixel nearest its k-means centre by a compact
    watershed over fractal noise (compactness 0.2 / spacing, noise at 0.6 / 0.25 / 0.09
    of the spacing). The author approved this wiggliness from a preview.
  - Areas outlined earlier (Rouental and neighbours, Cardonia) keep their k-means
    borders, and placeholder bricks stay: the author will outline more nations and
    touch borders up by hand, rather than re-cutting what exists.
  - `OWNERS` names patches by seed pixel; the rest go to `DEFAULT_OWNER`. Each run only
    needs the new region: patches already painted in a real (non-placeholder) country
    colour are skipped, and past runs' seeds are kept as comments.
  - **Split states are re-cut.** A done patch is cut again (organic, keeping its
    country) only when a new line splits one of its states (more pieces across lines
    than the state has anyway, so islets across water don't count). These drawn pieces
    stay states even under `MIN_STATE`. First used 2026-09-30: 13 Rouental pieces. The script decodes
    its input `.pdn` itself (`work/pdn_outlines`).
  - `CITY_STATES` (cut a patch into one state per city dot) was used once for Aislada
    and **rejected by the author** (2026-10-04, later: it split their drawn states).
    Aislada's drawn regions are now one state each through `regroup_states.py`
    (`DRAWN_PLACEHOLDERS`): 9 states plus 6 islands; the circle around Hirane is one.
  - Islets under 150 px join the nearest state of their country within 300 px
    (`ISLET_REACH`); farther ones (Rouental's two islets off Solitas) share a state of
    their own. Only states made in the same run count: an islet by an older state of its
    country is joined to it with `pdn_tools.py attach` (2026-10-12, Myehn's). `LEAVE` lists patches the lines close off by accident (the land south
    of Entroterra and Estande), which stay as they are.
  - Cut placeholder provinces and states are cleaned up iteratively: scraps join a
    neighbour (a new province's scrap stays in its state), never a new state, and
    states are forced into one region. Only provinces the outlines made or cut are
    tidied (2026-10-09: untouched ones the tidy-up box clipped had pieces merged away).
  - It rewrites Provinces / States / Countries / Strategic Regions and saves
    `source/HOI4 Mod Map.pdn`, using the author's upload as the template;
    `writepdn` copies the object graph verbatim when the size is unchanged.
- **Regenerating the file.** `make_game_pdn.py` writes it from a placeholder build.
  `writepdn.py` copies the original `.pdn`'s object graph (nine layers), patches the size
  fields (19 widths, 19 heights, 9 strides, 9 lengths) and rewrites each layer's name,
  visibility and opacity. It would overwrite the author's edits, so don't run it casually.
- **Round trip.** The first layer build matched the placeholder build exactly (same
  province colours, states, owners, regions and bitmaps), with only the ids renumbered.

## Rebuilding

`sh scripts/run_all.sh` from the repo root: about 2 minutes from `HOI4 Mod Map.pdn` (2026-10-15: `read_layers.py`
57 s, `build_mod.py` 31 s, then `check_mod.py`, `export_canvas.py` and `package.py` side by side, 15 s; the new zip
replaces `dist/valsora_test.zip` only if `check_mod.py` passes; the logs are in `work/logs/`), about 1 minute when the
map hasn't changed: `read_layers.py` is skipped while nothing it reads has changed (`scripts/stamp.py`: the script and the modules
of `scripts/` it imports, the files in `source/` and `source/gazetteer/`, the decoded layers by size and time).
`FORCE=1 sh scripts/run_all.sh` reruns it. Placeholder mode (used when that file is absent) takes about 2.5 minutes,
plus about 2 minutes for the one-time decode of the original `.pdn`. Needs `pip install -r requirements.txt` (numpy,
scipy, pillow, scikit-image, pinned: the same versions give the same files; Playwright for the Deco UI's textures
and the Gazetteer's tests). `VALSORA_BUILD` builds into another folder (`common.BUILD`; the test versions). Output is
deterministic, the zip included (`package.py` gives every entry one fixed date, so the same mod gives the same bytes and
a rebuild that changed nothing adds nothing to git). `docs/SPEED_AND_SIZE.md` has the timings, the repository's size
and what could make both smaller.

| step | does |
|---|---|
| `readpdn.py` | decodes a `.pdn` into one RGBA `.npy` per layer, plus `layers.txt` |
| `read_layers.py` | **normal mode**: the layers of `HOI4 Mod Map.pdn` → provinces, states, regions, owners, heights, terrain, rivers |
| `blocks.py` | placeholder mode only: land mask, continent blocks, removes Antarctica |
| `layout.py` | placeholder mode only: scales every block and pushes them apart |
| `compose.py` | placeholder mode only: game-resolution land / ocean / lakes, continent per pixel |
| `provinces.py` | placeholder mode only: brick provinces, sliver merging, X-crossing repair |
| `regions.py` | placeholder mode only: states, strategic regions |
| `make_game_pdn.py` / `writepdn.py` | turn a placeholder build into a fresh `HOI4 Mod Map.pdn`; `writepdn` writes any `.pdn` from a template's object graph, and adds layers on top when given more than the template has (2026-10-13, the flag file) |
| `nrbf.py` | reads a `.pdn`'s .NET object graph into records with their byte spans (used by `writepdn` to add layers) |
| `apply_outlines.py` | by hand: the author's outline layers → provinces, states, countries in the `.pdn` |
| `pdn_tools.py` | by hand: `navigable` (lake → sea with its own region), `sea_zones` (regroup and recolour regions; refused on a map with Ocean Province Lines), `give` (whole states to a country), `recolour`, `channel` (reopen a strait: the cheapest water-to-water path between two sea pixels becomes sea), `border` (the land a moved Necessary Borders line encloses → a country), `cede` (the land of one country a moved line cuts off → another, for countries without state lines: only the first country's pixels count, provinces are split along the line; what a split state loses is a state of its own from 600 px (`CEDED_STATE`), smaller slivers join a state that moved whole), `merge_small` (a country's sliver states join a neighbour), `attach` (a state goes to a country and joins its nearest state, regions too: for an islet or sliver too small to be a state), `add_land` (the water under a layer's paint, default "Islands to Add", becomes a country's land: plains, the nearest land's height, continent and region, a province per island, one new state), `recut` (placeholder land the outline runs never reached cut like an outlined patch: the piece of a country's land around a pixel becomes ~1,300 px states (one up to 2,000 px) and ~190 px organic provinces, each new state in the region most of it lies in; `--keep-states` cuts only the provinces), `lakes` (each lake one province, in the region most of it was in) |
| `strategic_regions.py` | retired 2026-10-12 (refuses to run on a map with Ocean Province Lines, unless `--force`): sea regions = the author's oceans, one each, with names (`source/region_names.json`); land untouched |
| `sea_provinces.py` | by hand: the sea from the Ocean Province Lines layer (Merlo's): `build` (provinces from the lines, cut to HOI4's size limit, colours and regions kept by overlap), `seam` (borders and regions meet across the left/right wrap), `names` (`source/region_names.json`: "<ocean> <n>" west to east), `check` (report only) |
| `river_provinces.py` | by hand, after a build: re-cuts the provinces of every state a river crosses so rivers run between provinces |
| `borders.py` | HOI4's province border count (pairs of touching provinces, each separate stretch of shared boundary once, land and water alike) and its limit, 65,536; `check_mod.py` uses it; run alone, it counts the last build's |
| `border_report.py` | by hand, after a build: where the province borders come from, and what re-cutting the provinces (one size, a bigger one, sizes by terrain like the base game's, impassable desert) would free; `docs/BORDER_LIMIT.md` (2026-10-15), `--terrain map` once the Terrain layer is painted |
| `merge_provinces.py` | by hand, after a build: merges the smallest land provinces into a neighbour in the same state (never across a river, never two city provinces, at most 400 px) until the borders are down to a target (default 60,000), on the Provinces layer |
| `redraw_flags.py` | unused: Fraxhemark's stand-in flag (writes `work/FRX_standin.png`); the author's own `FRX.png` replaced it |
| `state_map.py` | by hand, after a build: a numbered map of some countries' states (`dist/state_numbers_<name>.png` + `.json`, number → tag and pixel), for the author to name them; `--names` labels them with their names instead |
| `terrain_test.py` | by hand, a test not in the game (author, 2026-10-12: "do not add it to the mod yet"): terrain for the whole map from each continent's real-world model (Nonscio western Europe, Araseos Germany, Yastreovakia eastern Europe and Russia, Usnistan the Middle East and Africa, Orientalis Asia, Solitas loosely the New World, Aislada Australia): its own relief with hand-placed ranges (the Alps down the bay east of Rouental, Tibet and the Himalaya at Ganden, the Ethiopian highlands by Mekele ...), every drawn river in a valley that falls steadily to its mouth, a climate per continent (latitude frame, prevailing winds and monsoons carrying the sea's moisture inland, rain shadows, hand-placed wet and dry areas, wetter where rivers are drawn), terrain.bmp classes (woods on uplands and slopes, farmland on low ground, along rivers and coasts, marsh only where water gathers), and each province's majority type. **The Vale of Reibonne** is the author's (2026-10-12: "Rouental and the Reibonnaise nations are in the Vale of Reibonne and are mostly surrounded by mountains and hills, except the Reliette gap which is open plains"): a low farmland floor ringed by the ranges they drew on their fief map's Mountains layer (`source/vale_ranges.png`, projected from `work/pdn_rmap`: the Osgrande Mountains north, the Nossine north-east, the Bastionne east, the Hollier inside Hollier, the Anarlaine south-west, and the Firime Highlands, hills, north-west) and by hills along the rest of its land border; the Reliette gap (west, between the coast and the Anarlaine, into Placeholdaire) open plains; Marais Verte marsh. Writes `work/terrain_test/` and `dist/terrain_test_map.png`, `terrain_test_provinces.png`, `terrain_test_vale.png` |
| `usnistan_prototype.py` | by hand, a prototype not in the game: a fully generated Usnistan (relief, climate terrain, rivers, ~800 provinces, states, 6 placeholder countries, cities) into `work/usnistan/` and `dist/usnistan_*.png` (author asked for an example, 2026-10-02) |
| `regroup_states.py` | by hand, after `apply_outlines.py`: in every country with state lines of its own, each drawn area becomes exactly one state (provinces kept, split only where a line crosses them) |
| `import_flags.py` | by hand: the author's flag `.pdn` (one layer per flag, named after the nation) → `source/flags/TAG.png`; a stored flag is replaced when any pixel differs at the same size, or by more than resampling would at another size (`changed`, 2026-10-09); see-through pixels are filled from the nearest solid one first (`opaque`), since the game shows them as holes |
| `organic.py` | organic splitting (seeded watershed over noise), used by `apply_outlines.py` |
| `rivers.py` | plain river lines → HOI4 rivers.bmp format, and the river rules check |
| `build_mod.py` | every mod file |
| `deco_ui.py` | the Valsora Deco UI into the build (`common.DECO_UI`; see Deco UI below): Valsora's own copies of what it replaces kept in `work/deco_base/`, its long-name trigger and politics screen made from this build, then `deco_ui/valsora_deco_ui/` copied in (a file both ship stops the build unless the Deco UI replaces it on purpose) |
| `nations.py` | hand-written per-nation content (leaders, portraits, focus trees), used by `build_mod.py` |
| `superevents.py` | TNO-style superevent windows, their texts, picture and music |
| `test_events.py` | Rouental's test decisions (2026-10-15, until the testing is done): one per kind of event window, and the test superevent |
| `superevents_deco.py` | the superevent window in the Deco UI's style (`DECO_UI`, 2026-10-15): the mockup's board drawn with numpy and Pillow, a title strip per superevent, the texts measured against their boxes |
| `superevent_preview.py` | by hand, after a build with the Deco UI: `dist/preview_superevent.png`, a superevent's window as the game should draw it, from the built files (its .gui, sprites, title strip and picture) with the texts in the Deco UI's own fonts (`python3 scripts/superevent_preview.py [ID ...]`, 2 s) |
| `cultures.py` | generic portraits, name lists and graphical culture per continent / country |
| `ideologies.py` | the five ideologies: ideology file, renamed localisation, theocracy icon |
| `minimap.py` | the minimap (lower right): Valsora's land on parchment instead of vanilla's Earth, its frame, window and slide (2026-10-13); with the Deco UI (`DECO_UI`) gilt land and coasts on lacquer in a gilt frame, same sizes, and the start date picture the same (2026-10-14); the Vale of Reibonne start's picture, the Vale close up (2026-10-15) |
| `globe.py` | the world tension globe (top bar, 10 frames) and its small icon: Valsora instead of Earth (2026-10-14), cracking into lava as tension grows (redrawn the same day: the first flames "didn't come out too well"); run alone, `dist/tension_globe_preview.png` |
| `vanilla_parts.py` | vanilla's parts in the mod, for `build_mod.py`: the vanilla files it ships moved to 2036, the stand-ins for what Earth's content still names (decisions, events, country histories), the start and end dates, the AI's faction theaters |
| `vanilla_sync.py` | by hand, after a game update: refreshes `source/vanilla/` from the author's copy of the game (`Rouental/HOI4-Files`): the vanilla files the mod ships changed, and lists of vanilla's names (and its traits and kinds of company, `index/traits.json` and `index/companies.json`, for the Gazetteer) |
| `pdxscript.py` | a reader for Paradox script (nested `key = value` blocks), used by `vanilla_sync.py` |
| `check_mod.py` | re-reads the built files and checks every rule below |
| `export_canvas.py` | previews in `dist/` |
| `package.py` | `dist/valsora_test.zip` (reproducible: fixed dates and permissions, sorted) |
| `stamp.py` | `fresh` / `save` a step's inputs, so `run_all.sh` skips `read_layers.py` while they are unchanged (`FORCE=1` reruns it) |
| `mutation_test.py` | by hand, after changing `check_mod.py`: breaks hard-linked copies of the build in 50 known ways (map files, history, content, files), runs `check_mod.py` on each batch side by side, and fails unless every break is reported (a miss is retried alone, in case another break hid it); 30 s. Add a break for every new check (2026-10-15: it found our on_actions' scripted effects unchecked) |
| `fit_flag.py` | by hand: a flag the author sends in another shape → `source/flags/TAG.png` at 82:52 without resampling (plain field trimmed round an emblem, vertical bands made longer, stripes lengthened or made taller, a screenshot's frame cropped; quarters, crosses and borders refused) and `work/flag_fit_TAG.png` to check |
| `build_flags15.sh` | by hand: the larger flags' test version (`docs/HD_FLAGS_TEST.md`) beside the mod: the Deco UI drawn for it in `work/deco_flags15/`, the mod in `work/build_flags15/`, `work/valsora_test_flags15.zip`; `build/` and `dist/` untouched |
| `publish_site.sh` | by hand: the Gazetteer's site (`facts_export.py`, `gazetteer_site.py`) as the next commit of `gh-pages`, pushed; nothing when unchanged |
| `tests/gazetteer/` | by hand, after `facts_export.py`: the Gazetteer page driven in Chromium with a stand-in for claude.ai's runtime: `run.py` (owner, friend, passwords, desktop and phone, light and dark), `traits.py` (traits and their requests), `companies.py` (political advisors, companies and their requests); `harness.py` builds the test site in `work/gazetteer_test/` |
| `country_list.py` | by hand, after a build: `dist/world_map_labelled.png` (every country labelled) and `dist/countries.md` / `.csv` (name, full name, ideology, sub-ideology, culture, leader, states), read from the built mod |
| `nation_sheet.py` | by hand, after a build: `dist/nations_by_continent.png`, every nation in the game under the continent of its capital: flag, ruler at the start (portrait of our own, or a "placeholder" box for a base-game one), full name, ideology and sub-ideology, culture, and a strip of its map colour (author, 2026-10-13) |
| `collages.py` | by hand, after a build: `dist/flags_collage.png` (every custom flag, and the countries still on a placeholder stripe) and `dist/leaders_collage.png` (every custom leader: own portraits at 2×, named ones with base-game portraits as labelled tiles); `--continent NAME` writes only `dist/flags_<name>.png`, the flags of the nations whose capital is on that continent, naming below them those with land there and their capital elsewhere (2026-10-10, Araseos; 2026-10-12, Yastreovakia) |
| `facts_export.py` | by hand, after a build: the Gazetteer's map data into `work/gazetteer/` (`index.json`, `world.png`, `n/<TAG>.json` per nation: its states, provinces, cities and politics as built, its flag, its land and the neighbours' around it as province numbers per pixel, in parts, with the rivers, and whether its states are drawn, `final`), published with the page |
| `gazetteer.html` | the Gazetteer (see below): the page where friends fill in their nations' facts; the web site's (`gazetteer_site.py`), or a claude.ai artifact with its own database (the first version) |
| `gazetteer_site.py` | the Gazetteer's web site into `work/gazetteer_site/` (the page with the Firebase project's settings, the SDK bundle from `source/gazetteer_site/`, `facts_export.py`'s map data), committed alone on the `gh-pages` branch, which GitHub Pages serves; `--emulator` builds it for Firebase's local emulators (tests) |
| `gazetteer.py` | the Gazetteer's facts into `source/gazetteer/<TAG>.json` (pictures in `source/gazetteer/assets/`): `paths KEYS.json` (each nation's atlas folder `n/<TAG>/<key>` from the owner's passwords), `pull DIR` (the atlas as the ArtifactData tool saves it, pictures fetched by asset id into `DIR/assets/`), `import FILE.json` (a file saved from the page or the site, pictures inside; drops the map facts of nations whose states aren't drawn; gives releasables their tags), `status` (releasables' cores, and what is left to do by hand), `suggestions` (`dist/gazetteer_suggestions.png`, a layer for the `.pdn`); `finals` (whose states are the author's); and the functions `read_layers.py` (terrain, rivers, cities) and `build_mod.py` (state facts, capitals, railways, supply hubs, names, sub-ideologies, rulers and party leaders with titles and portraits, characters, companies, map colours, releasables) call |

**A clean `check_mod.py` run is the bar for shipping a build.** It was mutation-tested
(CRLF, X-crossing, missing building row, state split across regions, descriptor
mismatch, missing localisation) and catches all of them. Since 2026-10-14 it also checks
our files against vanilla's own names (`source/vanilla/index`): sprites, technologies,
equipment, modules, battalions, ideas, defines, the map files the mod inherits, the
stand-ins for Earth's decisions and tags, every event fired (by focus, effect, event or
on_action) and 2036 (mutation-tested: 19 breaks, all caught). The checks that judge our
scripting (tags targeted, popularities, ideologies) skip vanilla's shipped files. Since 2026-10-15 the breaks are kept
in `scripts/mutation_test.py` (50, every one caught): run it after any change to `check_mod.py`.

## Decisions worth keeping

- **2036** (author, 2026-10-14: "Valsora takes place in 2036"). Everything the game dates
  moves a hundred years (`vanilla_parts.py`):
  - the clock: `START_DATE` 2036.1.1.12, `END_DATE` 2049.1.1.1 (vanilla also runs 13
    years) and `TENSION_TIME_SCALE_START_DATE` in `common/defines/valsora_game.lua`, the
    bookmark's date, and our history (last elections 2032, rulers' terms to 2065, order of
    battle files `<TAG>_2036`);
  - the tech tree: every technology's `start_year` (research ahead of it is penalised) and
    the tree's year labels (`interface/countrytechtreeview.gui`);
  - the date conditions of the generic content the mod ships (laws, the generic focus
    tree, AI templates and strategies, faction goals, special projects, raids, medals,
    events) and the game rule "war goals from focuses only, until 1938 / 1939 / 1940"
    (2038 ..., `diplomacy_scripted_triggers.txt`);
  - the generic names with years ("2036 Cruiser Hull", "Heavy cruiser 2040", the game
    rule's options), in `localisation/english/replace/`.
  Equipment keeps vanilla's `year`: licence costs count it from 1936
  (`LICENSE_IC_COST_YEAR_INCREASE`), so moving it would only make licences dearer.
  `check_mod.py` fails on any 18xx or 19xx date, `start_year` or tech tree label in the
  built files, and on a start date or bookmark outside 2036 (mutation-tested).
- **Railways wait** (author, 2026-10-15: "Let's leave railways off for now. The location of cities might change,
  and the mod doesn't need to be playable yet"): the map has only the lines drawn on the Gazetteer (one, Rouental's),
  so supply hubs away from a capital aren't connected. Don't generate a network until the author asks.
- **Province sizes by terrain** (author, 2026-10-15, on `docs/BORDER_LIMIT.md`: "For cases like desert, yes. But for
  others like Rouental, keep it dense"): when the Terrain layer is painted, deserts and land like them may get larger
  provinces to free borders; Rouental keeps its ~190 px ones.
- **The mod's zip stays in `dist/`, committed** (author, 2026-10-15: "Keep it as is. When we start getting to more
  substantial builds, I'll start transferring to the releases page"), and is sent in the chat too. A session like this
  one can't publish releases: GitHub's proxy answers "Creating, editing, or deleting releases is not permitted for this
  session type" (HTTP 403), so the Releases page, when it comes, is the author's to publish by hand (Claude gives them
  the zip and the notes). Don't work around that rule (no workflow or tag that publishes for the session).
- **Test content until the first public build** (author, 2026-10-15: "I'll remove all the test stuff before the first
  public build"): Devlon's spirits and Rouental's test decisions stay until the author takes them out.
- **Map size 5120×2560.** HOI4 needs both sides to be multiples of 256 and the area to stay
  under ~13,238,272 px. 5120×2560 = 13,107,200 is the largest size under that cap, and
  2:1 matches the author's canvas. It is proven in the wild (the Mappa Mundi mod ships this
  size). At this size every per-pixel map file has to be generated: the vanilla ones are
  5632×2048.
- **Read the `.pdn` directly.** `PDN3` + 3-byte header length + XML header, then a .NET
  BinaryFormatter graph ending in `0x0B`, then per layer: format byte 0, chunk size
  (u32 BE, 262144), then gzip chunks `(index u32 BE, size u32 BE, data)` in any order.
  Pixels are BGRA. Land is **any opaque pixel of layer 1** ("Land & Borders & Colours");
  the 1px coastline layer lies on the land's inner edge.
- **Continents move as rigid blocks** (`blocks.py`): each block is a core landmass, named
  by seed pixels, plus the islands nearest to it. Nonscio + Araseos are **one block**
  because the Aikos / Midtierre archipelago interlocks them; they are split into two
  continents afterwards by nearest main landmass. Hand overrides, all by source seed
  pixel in `blocks.py`: the island at (9574, 3082) belongs to Orientalis (author's
  continents map); the island at (2615, 4051) north of Araseos belongs to Araseos; the
  islet at (1087, 6590) south-west of Araseos is deleted (author's request).
- **Antarctica** is the landmass touching the bottom edge. Islets within 5 px of it are
  removed with it; three real islands south of Usnistan are kept.
- **Scale 0.375** output px per source px (a straight fit would be 0.366; the previous
  5632×2048 build used 0.293). At 0.38 the tightest gaps drop to ~91 px.
- **Layout** (`layout.py`): start from the source layout, stretched vertically into
  Antarctica's space. Then push apart every pair of blocks closer than 100 px along the
  line between their nearest coasts, with a fading pull back to the start. The wrap seam
  (x = 0) is a wall no block may cross. `compose.py` then centres the final land exactly
  (equal margins top/bottom and either side of the seam) and records the shift in
  `work/world.npz`, which `export_canvas.py` applies too.
- **Provinces are bricks** (at sea only until 2026-10-12, when Merlo's hand-drawn sea
  provinces replaced them; see Sea provinces below): 32 px on land, 128 px at sea, 48 px on lakes, with odd rows
  offset by half a brick so only three provinces meet at grid corners. Bricks never cross
  the seam (the edge half-bricks of odd rows are folded into their neighbour). Pieces under
  25% of a brick merge into the same-kind neighbour with the longest shared border.
  Remaining X-crossings (coasts, seam) are fixed by moving single pixels, never letting a
  lake touch the sea. **No bricks are left** (2026-10-15, author: "there are areas of the map
  that still have the old placeholder states and provinces"): every lake is one province
  (`pdn_tools.py lakes`: four lakes had 2-10 squares, 13 merged, among them the lake by Xue and
  Ungar's), and the land no outline run had reached, 87 brick provinces in 32 px squares and
  96 px grid states, was cut like an outlined patch (`pdn_tools.py recut`): Arvorenia's and
  Atrocha's islands (the friend's build of 2026-10-05; Arvorenia 34 → 56 states, Atrocha 14 →
  26), Kurikia's KU island and Belekria's island group south of the BE islets (their one state
  each kept, `--keep-states`, so Kurikia's map tools stay open). They are found as provinces
  whose borders with other land provinces run 60 % or more on the brick grid (organic ones:
  under 20 %). `dist/preview_recut_20261015.png` shows them before and after.
- **Straits are traced, not averaged** (`layout.channels`). Shrinking by area filled in
  channels narrower than ~1.5 output px and fused 21 large islands to their neighbours
  (author's report). The water's centre line is traced at source resolution and kept as
  4-connected water wherever the land on either side belongs to two different source
  landmasses. That reopened 44 straits. `dist/strait_fixes_map.png` and
  `strait_fixes_*.png` show each one before and after.
- **Islands under 16 px are dropped and ponds under 64 px filled.** About 660 islets go
  this way; they are 1–4 px specks at game scale.
- **Enclosed water becomes lakes**, including the author's inland seas (Piscary, Norlany,
  Sasurs).
  - The two inland seas that have islands are navigable sea (author's request), each in
    a sea region of its own: Nonscio's, south of Rouental, and Yastreovakia's northern
    one. They were made with `pdn_tools.py navigable`.
  - Other lakes stay lakes.
- **Sea provinces and sea regions are Merlo's** (the author's friend, 2026-10-12; merged
  with the author's approval, which reverses their 2026-09-30 wish to keep each ocean
  one region). Merlo drew the sea's borders by hand on a new layer, **Ocean Province
  Lines** (red lines), and his scripts (`build_sea.py`, `regroup_sea.py`, not in the
  repo: they ran on his machine) made 362 sea provinces from them in place of the 645
  bricks (35 areas over HOI4's size limit cut by wobbly lines, drawn into the layer
  too) and grouped them into 42 sea regions of about 9 provinces inside each ocean
  (South Demetric 8, Northern Ocean 6, North Menotius 6, South Menotius 5, Arctic
  Ocean 4, Northern Friedlich 4, Southern Friedlich 3, Midtierre Sea 2, North Demetric
  2, Piscary and Norlany 1 each); each province went whole to the ocean covering most
  of it, which moved 8.7 % of the sea to another ocean. Land, lakes and every other
  layer were untouched (checked pixel by pixel; one pixel at (2337, 933), sea on Terrain
  but painted into a Krionik land province, became sea), and his built mod matched our
  build of his file byte for byte. Our own `scripts/sea_provinces.py` now does the job
  from the layer: `build` (provinces from the lines; a line pixel keeps its province
  while that borders it, so unchanged lines give back the same provinces: 22 px
  differed on Merlo's file), `seam`, `names`, `check`. **The wrap is seamless**
  (`seam`, at the author's request): Merlo's borders met the two edges at different
  rows (up to 43 px apart, two with no partner, plus line bits drawn along the edge
  columns); now every border meets both edges at the same row (pairs bent to meet
  halfway; the right edge's border at row 229 continued across the wrap, which split a
  province: 363 sea provinces; a big province that reached the right edge only by a
  5 px neck, rows 958–975, pulled back), the lines within a few dozen px of the edges
  are redrawn from the result, and the two provinces facing each other across the wrap
  share a sea region (10 provinces changed region, the most even choice), so the oceans
  continue across it too. Names are "<ocean> <n>" west to east (`names`), the oceans'
  spelling as on the author's ocean map ("North Demetric", "Northern Friedlich").
  `strategic_regions.py` and `pdn_tools.py sea_zones` would undo all this and refuse to
  run on a map with the lines layer.
- **Sea regions were the author's oceans, unsplit** (`strategic_regions.py`, 2026-09-30,
  until 2026-10-12).
  Each sea province takes its ocean from `source/ref_oceans.webp` and each ocean is ONE
  region, as big as the map shows it: the author will edit them later. Split only where
  HOI4 forces it (a sea region must be connected); none needed it. 11 sea regions:
  Northern Ocean, North / South Demetric, North / South Menotius, Northern / Southern
  Friedlich, Midtierre Sea, Arctic Ocean, plus the navigable Piscary and Norlany seas.
  - The reference maps use an **older arrangement of the continents** than the drawing,
    so positions are mapped per continent: game → drawing through `work/layout.json`
    and the recovered centring shift (36, 16); drawing → reference by a per-continent
    shift fitted by overlap (Nonscio and Araseos fitted apart). Each continent votes
    for an ocean, weighted 1/(distance+20)²; stray bits join their neighbour; the top
    edge is forced to Northern Ocean and the bottom to Arctic (the mapping cut the
    Arctic in two).
  - An earlier version also regrouped land regions and cut oceans into ~350k px pieces;
    **the author rejected it**: land regions stay as they were (the grid ones), and
    oceans stay whole.
  - Sea names are keyed by region colour in `source/region_names.json`; land regions
    keep their generic names.
- **Region colours.** Sea regions are always blues (hue 0.53–0.70). Land regions are
  never blue, cyan or indigo (hue 0.42–0.82 is excluded), so the author can tell them
  apart on the layer.
- **States** bucket land provinces on a 96 px grid per continent, split into connected
  pieces; small island pieces join the nearest state within 160 px. **Land regions**
  bucket whole states on a 384 px grid; **sea regions** bucket sea provinces on a 512 px
  grid and must stay contiguous. Lakes go into the land region they border most.
- **Countries**:
  - One placeholder per continent: NSC ARS AIS SLT YAS USN ORI (`SOL` is a vanilla
    tag, so Solitas is `SLT`); Araseos has no land left since 2026-10-09, nor Nonscio and
    Yastreovakia since 2026-10-12, nor Orientalis, Usnistan and Solitas since 2026-10-13,
    so ARS, NSC, YAS, ORI, USN and SLT are left out of the mod. Merlovich (AIS, still on
    the placeholder's paint) is the only one left. Until 2026-10-15 the placeholders were the only countries the
    bookmark recommended (author's wish, to keep the start menu short).
  - **Two starts on 1 January 2036** (`common/bookmarks/valsora.txt`, `build_mod.py`): **Valsora** recommends
    Rouental (author, 2026-10-15: "add Rouental to the recommended nations") and Merlovich; **the Vale of Reibonne**
    recommends Rouental and the seven other Association states (`nations.REIBONNAISE`), its picture the Vale close
    up with the eight lit and their borders (`minimap.close_up`). Two, because with one start the game skips its
    scenario screen, so Back on the country screen went to it and was sent straight on again: no way back to the
    menu (the author's video, 2026-10-15). The histories are short and factual; the author may write their own.
  - Colours follow the flags (author): Rouental royal green, Guedelon blue, Hollier red, Seigne white,
    Evriches yellow, Lustiana black, Selgrave dark maroon, Lanzerac purple (its new flag's,
    2026-10-09; dark gold before), Cardonia deep purple (kept when its own flag, black,
    white and navy, came on 2026-10-14). Guedelon's blue and Hollier's red are their flags' main colours. `pdn_tools.py recolour Countries OLD=NEW` keeps
    the `.pdn` in step.
  - **Every nation's record**, who drew, named and decided what and when, is `docs/NATIONS.md` (moved out of this
    file on 2026-10-15). As built: 183 countries in the mod, the 161 on the map and 22 that own nothing at the start
    (Rouental's 13 releasables and Belekria's Tethia, the civil war's 7, the Gazetteer's releasable "Test");
    `dist/countries.md` lists every country's names, government, culture, ruler and states. Off the map but kept in
    `COUNTRIES`, and so left out of the mod: the United States of Solitas (to come back as a formable) and
    Russovichia (author, 2026-10-15).
  - **A new or changed nation** (the rules the record kept to):
    - The author's are the names, governments, formal names and rulers, and whatever else they name. Claude picks
      the rest (tag, map colour, adjective, culture), says so in the record and in a code comment (`# Claude's
      guess`), and tells the author.
    - It needs `COUNTRIES` (`common.py`: tag, name, adjective, map colour), `FORMAL_NAMES`, `LEADERS` (every ruler
      is a set character), a culture (`cultures.TAG_CULTURE`) and a flag (`source/flags/TAG.png`; without one, a
      stripe in its map colour), and a dated paragraph in `docs/NATIONS.md`.
    - All tags were checked against vanilla `common/country_tags`; new tags must be too: not the base game's
      (`source/vanilla/index/tags.txt`) nor ours. File names are ASCII (`Cotefer`).
    - Its land is cut from the author's outlines by `apply_outlines.py` (`OWNERS` seeds by pixel, `LEAVE` for land
      the lines close off by accident); islands go with the labels the author writes beside them, and labels
      written on Necessary Borders are moved to Necessary Names. Land changes hands with `pdn_tools.py`: `give`
      (whole states), `attach` (a piece joins the new owner's nearest state), `border` and `cede` (along a moved
      line).
    - A map colour comes from the flag where there is one, and moves off a neighbour's it would merge with. A flag
      that comes later doesn't change the colour unless the author asks.
    - Flags in another shape are fitted to 82:52 without stretching (Flags, under Nation content).
  - The adjectives of the neighbours are guesses; the author may rename them.
- **State names** are the author's, in `source/state_names.json` ("x,y" of a pixel
  inside the state → name, since ids shift; `build_mod.py` stops if a pixel is in no
  state or two name one state). Unnamed states are "Country N". First set (2026-10-01):
  Rouental's 54 and its seven neighbours', numbered by `state_map.py`; then (2026-10-02)
  21 Chouan, the islets off Solitas Concorde et Volonté, and Rolantelle split by a new
  state line into Ghessone (west) and Rolantelle (east); Maïeul split into Moelle
  (north; Selgrave takes it in the civil war) and Maïeul (south). 2026-10-05: Cardonia's 27
  (from `dist/state_numbers_cardonia.png`; numbers 6, 11 and 12 merged into Llainfair, the
  island east of Coreilia). `state_map.py --names` draws a
  country's states with their names (`dist/state_names_<name>.png`).
- **Localisation keys are our own** (`VAL_STATE_n`, `VAL_REGION_n`), so vanilla's
  `STATE_n` / `STRATEGICREGION_n` Earth names never show. Victory point names have to
  reuse vanilla's `VICTORY_POINTS_<id>` keys, so they live in `localisation/english/replace/`.

## Nation content (`nations.py`)

Aislada is the worked example of a built-out nation:
- **Leader.** The Great Merlovich (`AIS_merlovich`; "Merlovich" until 2026-10-04) is defined in `common/characters/AIS.txt` as a
  neutrality (`despotism`) country leader and recruited from the country history.
- **Portrait.** Referenced as a sprite (`GFX_portrait_AIS_merlovich`, declared in
  `interface/valsora_portraits.gfx`), the way vanilla does it. The image is a 156×210 DDS
  cropped from `source/merlovich_emu.png`.
- **Focus tree.** `common/national_focus/aislada.txt` is picked for AIS by
  `country = { factor = 0 modifier = { add = 10 tag = AIS } }`. It is one chain:
  1. NationStates account: +25 political power.
  2. Become Cartographer: −0.5 stability.
  3. Fucking Explode: capital state −100 manpower, communism 100%, ruling party
     communism, then `promote_character = AIS_communist_merlovich` ("Communist
     Merlovich", `marxism`, same portrait washed red by `nations.redden`) and retire
     the original.
     **`recruit_character` is ignored outside history files** (error.log: "should only
     happen in game/history files"), so both Merlovichs are recruited in the country
     history; the communist one sits as communist party leader until the focus.
- **Icons.** Vanilla icons only, checked against vanilla `interface/goals.gfx`.
- **Portraits** live in `source/portraits/` and are registered in `nations.PORTRAITS`
  (source, crop box, optional red tint). Each becomes `gfx/leaders/VAL/<name>.dds` and a
  `GFX_portrait_<name>` sprite. Transparent pixels, and a crop box reaching past the
  picture (to fit a round emblem), show `nations.PORTRAIT_BG` (dark charcoal).
- **City names**: `nations.CITY_NAMES` overrides victory point names, keyed by
  `"capital:TAG"` (e.g. Rouental's capital is "Rêverie") or
  by province id. Ids shift whenever the map is rebuilt, so prefer the capital key;
  `build_mod.py` stops if a named id is no longer a victory point.
- **Rouental (ROU)** is the country the author outlined inside Nonscio. Everything
  first built for NSC moved to it, with `NSC_` renamed `ROU_`; NSC is plain "Nonscio"
  again. `nations.IDEOLOGY_NAMES["ROU"]`: "Rouental" on the map for every government,
  with the author's formal names (2026-09-30): Monarchist "The Sacred Principality",
  Authoritarian "The Grand Principality", Theocratic "The Most Seran State",
  Democratic "The Principality" (a constitutional monarchy, since later that day), Communist
  "The People's Republic" (all "… of Rouental");
  adjective Rouentaise. (The first names, Perfect / Powerful / Boring / Shitty
  Rouental, were dropped.)
  - **Capital: Rêverie**, the one-province state the author drew at (660, 805)
    ("Rouental 27" in that build), set by `nations.CAPITALS` (tag → pixel, since state
    ids shift). Neighbours' capitals are named by `CITY_NAMES` "capital:TAG": Guedelon,
    Evriches, Argent-sur-Seigne (SGN), Grande Hollier, Lanzerac, Villerose (SGV),
    Tanière (LST).
  - Leaders are in `common/characters/ROU.txt`: **Roland II Cahun** ("Roland Cahun"
    until 2026-10-08; `despotism`, leads at start; his description, shown on his portrait,
    is the author's list of his titles: `desc` in his leader role, after `ideology`, which
    `check_mod.py` and `country_list.py` expect first) and Serelle Cahun
    (`fascism_ideology`, fascist party leader; **Serelle VI Cahun** once she rules
    Rouental by any route: `nations.REGNAL_NAMES`, renamed by `set_character_name` in the
    on_ruling_party_change on_action; HMMLA's copy keeps her name). Serelle is also
    a general from the start (corps commander, skill 4, armor officer; HMMLA's copy
    too). Polite, Steady and Accept Reality only remove her party role
    (`remove_country_leader_role`), so she stays a general; Rudely (communist) retires
    her outright (author, 2026-10-02).
  - Portraits come from `source/portraits/roland_cahun.png` and `serelle_cahun.png`.
  - `common/national_focus/rouental.txt` has four mutually exclusive focuses in one row:
    - Kick Out the Parasites (Polite): democratic, elections on, both Cahuns retired.
    - Kick Out Your Brother: fascist, Serelle promoted, Roland retired.
    - Steady As She Goes (the author's; Habsburg icon): non-aligned, Roland promoted,
      Serelle retired.
    - Kick Out the Parasites (Rudely): communist, both Cahuns retired.
      Rudely also moves the capital to Carcarelle (`set_capital`, author 2026-10-02)
      and gets Rouental cast out of the Association at once (`rudely_effects`: dismantled,
      re-formed under Hollier with the other six). The communist flag
      (`ROU_communism.png`) is the author's Liberté flag, as is the Reibonne's.
      - **Execute the Prince** (under it, x = 6, y = 1): plays superevent
        `rou_civil_war` (the author's photo `source/superevents/rou_civil_war.jpg`, the
        author's quote and song, Rafael Krux's "Epic Church Organ"), sets
        country flag `ROU_civil_war` and starts the **Rouentaise civil war**
        (author, 2026-10-02; `nations.CIVIL_WAR`, `civil_war_effects`):
        - Rouental becomes the Reibonne (cosmetic tag `ROU_REIBONNE`, "The People's
          Republic of the Reibonne", flag `ROU_REIBONNE.png`, communist maroon).
        - Lustiana takes Maïeul and Serpette, Hollier takes Chirac, Selgrave takes
          Moelle (`ANNEX`), and the
          Association becomes "The Alliance of the Vale": there is no effect to rename a
          faction, so Hollier dismantles it and founds one from
          `faction_template_alliance_of_the_vale` with the same members.
        - Seven countries that own nothing at the start are `release`d and declare war
          (`annex_everything`). They have cores on their states from the start,
          except `CIVIL_WAR_ONLY` (FTH, RLA: the author wants them to exist only
          through the war), whose cores are added by the focus just before. (An
          Alliance of the East, AOE, was dropped on 2026-10-02 for the annexations.)
          The author's plans for the war (events, rival factions) are in
          `docs/CIVIL_WAR_NOTES.md`:
          Brillagne BRL (the Holy State of Brillagne; theocratic Rouental's ruler, a
          copy `BRL_mahaut_vi`, and flag); Crépuscule CRP (Principality; Absolute
          Monarchy); Reliette RLT (Grand Duchy; Feudalism); The Marches MRC (Alliance
          of the Marcher Lords; Oligarchy); HMMLA RLA (Her Majesty's Most Loyal
          Army; map name HMMLA, the author's, 2026-10-02; Strongman Rule, `RLA_serelle_cahun`; flag the fox quarter of `ROU.png`,
          which is also `ROU_fascism.png`); Vair VAI (Duchy; Feudalism); The Faithful FTH
          (the Faithful Children of the Goddess and Her Saint; Holy Order). States
          are named in `CIVIL_WAR` (first = capital); the focus file writes
          `@STATE:<name>@`, which `nations.fill` turns into ids. Two countries may
          share a name: their country files get the tag appended.
    - Left to right: Polite, Brother, Steady, Rudely.
  - The democratic and communist parties have no defined leader, so the game generates one.
  - **Accept Reality** (x = 8) is the fifth mutually exclusive path. It makes Rouental
    theocratic under **Mahaut VI** (`theocrat`; portrait from
    `source/portraits/mahaut_vi.jpg`; recruited in history as theocratic party leader),
    retires both Cahuns and plays superevent `rou_reality`.
  - **Plans for Cardonia** (x = 11, cost 1, not exclusive) creates an `annex_everything`
    war goal on CRD. It is for testing wars without justifying.
  - **Faction.** ROU starts as leader of "The Association of Reibonnaise States",
    together with GDN, LST, EVR, HLR, SGV, LZC and SGN.
    - **Reibonnaise opinions** (author, 2026-10-02; `nations.REIBONNAISE`): +20
      `valsora_reibonnaise_ties` between them, none while either is communist, and −20
      `valsora_against_communism` towards every communist country. The scripted effect
      `valsora_reibonnaise_opinions` re-sets them on `on_startup` and every
      `on_ruling_party_change`. `common/ai_strategy/valsora_reibonnaise.txt` makes the
      AI want them as allies (alliance 200, befriend 100) while neither is communist.
    - Lanzerac and Guedelon (Lordly Republics, democratic) left the Association at
      once. Likely cause: a member needs 30 % support for the leader's ideology
      (`IDEOLOGY_JOIN_FACTION_MIN_LEVEL`) and they had 20 % monarchists. They now start
      democratic 40, monarchist 30, the rest 10 (`nations.POPULARITIES`).
    - Its template, `faction_template_reibonnaise_association` in
      `common/factions/templates/valsora_factions.txt`, uses vanilla's generic manifest,
      goal, rules and icon.
    - ROU's history does `create_faction_from_template` + `add_to_faction`, the way
      vanilla ENG does in 1.19.
- **Starting armies** (author, 2026-10-02): every country owning land but Rouental gets
  `history/units/<TAG>_2036.txt` (`nations.generic_oob`): "Infantry Division" (8
  infantry, 1 artillery, engineers, recon), about one per six states, 2 to 24, at the
  victory points of its states (capital first), plus the techs for them. An OOB
  division takes its men out of the country's pool; `start_manpower_factor = 1.0` did
  not stop that (in game, 2026-10-04: every army started empty), so each country's
  history does `add_manpower` (12,000 per division; Rouental 150,000) just before
  `set_oob`. State population is 300 per map pixel (`build_mod.POP_PER_PX`; 20 until
  2026-10-04, when the whole world held 75 million and Seigne 7,000).
- **Devlon's 15 test spirits** (author, 2026-10-14: to see how the politics screen shows many
  national spirits): `nations.TEST_SPIRITS`, ideas `DVL_test_spirit_1`..`15` with vanilla's generic
  pictures and no effects, added in Devlon's history. Remove the list and its `HISTORY` entry after
  the test. `check_mod.py` checks every idea's picture exists.
- **Rouental's test decisions** (author, 2026-10-15: "Give decisions to Rouental to spawn generic events of each type /
  layout, and a superevent for testing. The superevent should use the clown music and placeholder anime girl image"):
  `test_events.py`, the category "Test Events" (`ROU_test_events`, for Rouental's player), free and repeatable, each
  firing a placeholder event (namespace `valsora_test`): a country event; a long one with four options; a state event
  (from the capital); a news event and a major one (sent to every country); a leader event (a random general of
  Rouental's: the portrait window); an operative event (an operative created first if there is none; shown only with
  La Résistance); and the test superevent (`rou_test`, "This Is Only a Test": the anime picture and Entry of the
  Gladiators). Texts are Claude's; no option does anything. Take the category out when the testing is done (the
  author will, before the first public build). Fixed after the first test (2026-10-15): the state event names
  `trigger_for = controller` (without it the game shows a state event to no one: `check_mod.py` checks it), and the
  operative decision first gives Rouental an intelligence agency (`create_intelligence_agency`) and an operative.
- **Opinion modifier names**: `valsora_reibonnaise_ties` is "Seran Ties" and
  `valsora_against_communism` "Seran Biases" (author, 2026-10-04).
- **Named generated rulers**: `nations.NAMED_LEADERS` gives a generated ruler the
  author's name and portrait: Illiricium's is **Ema Milize**
  (`source/portraits/ema_milize.png`); Krionik's is a council, the **Kriosaivak Council of
  Marshals**, with its emblem as the portrait; Leithanien's is **Helmut Shulz**
  (`helmut_shulz.png`) and Terreich's **Charlotte Gustoff** (`charlotte_gustoff.webp`,
  cropped from a photo) (author, 2026-10-08); Chineasia's is **Han Leji**
  (`han_leji.png`, author, 2026-10-12). Solitas' new rulers (2026-10-13) and Tsuruma's
  **Akihiro Tanaka** (2026-10-13, later) are named without portraits (`None`): they keep
  a generic portrait of their culture.
- **Nation names** come from `COUNTRIES` in `build_mod.py`: name and adjective feed
  `TAG`, `TAG_DEF`, `TAG_ADJ`, the per-ideology variants (`TAG_communism` etc.) and the
  continent key.

- **Rouental's names** (2026-10-02): the author's fiefs are
  `source/names/rouental_fiefs.txt` (393 fiefs under 14 headings; `cultures.fiefs`).
  **Every fief is a vassal of the Crown; the headings are cultural groups, not vassals**
  (author's correction), and the governorates between vassals and Crown have no power.
  The author will give each fief its title; per-fief levies wait for that. They give
  Rouental's name list noble surnames ("de Beaufort", "d'Aurifort") and its division
  names: "The Royal Host" (Garde Royale, Ost de <royal fief>) and "Vassal Levies"
  (Levée de <fief>, numbered "%de" as vanilla requires), in
  `common/units/names_divisions/ROU_names_divisions.txt`. The levy-army design is in
  `docs/ROUENTAL_ARMY.md`. Built: the **Feudal Army** spirit (`ROU_feudal_army`:
  recruitable population −80 %, training ×2, PP −10 %, stability −5 %; anime placeholder
  icon) and the **royal host** (`history/units/ROU_2036.txt`: 2 armoured, 2 mechanised,
  8 motorised divisions, full support, plus techs, a "Char Royal" tank and a stockpile).
  The levies themselves are not built: tiers and costs await the author.
  - The author's detailed fief map (`Rouental_Map_TEMP_2.pdn`, 8000×4471, decoded in
    `work/pdn_rmap`) was overlaid on the game's states (axis-aligned fit, IoU 0.885;
    game x = 0.0396 fx + 572.1, y = 0.0379 fy + 747.4). Every label was read and placed:
    `docs/ROUENTAL_FIEFS.md`, `dist/rouental_fiefs_overlay.png` and
    `source/rouental_fiefs_by_state.json` (state name → its fiefs by cultural group).
- **Flags** are `source/flags/TAG.png`, any size (HOI4 gets 82×52, 41×26 and 10×7
  32-bit TGAs, bottom-left origin). `TAG_<ideology>.png` is used only while that
  ideology rules: Rouental's banner of arms is `ROU.png` and its blue-white-gold
  tricolour is `ROU_democratic.png` (author's choice). The other seven were cropped
  from the author's flag sheet. Countries without a PNG get a placeholder stripe in
  their map colour. Flags sent in another shape are fitted to 82:52 without stretching:
  scaled evenly, then plain field added inside the stripes (or plain sides trimmed), so
  emblems keep their shape (2026-10-13, the author's wish). Vertical bands get plain rows
  above and below instead, so their widths stay (Qinguo), and a field division that must
  reach the corners is redrawn at the new width round the unchanged emblems (Ganden's
  border and mountain triangle).
- **Formal names** (`nations.FORMAL_NAMES`, e.g. "the County of Evriches") feed
  `TAG_DEF` and the per-ideology `_DEF` keys that have no `IDEOLOGY_NAMES` entry.

## Ideologies (`ideologies.py`)

The author's five ideologies. The internal keys stay vanilla's so vanilla script keeps
working; names come from `localisation/english/replace/`:
- `democratic` Democratic and `communism` Communist are unchanged.
- `fascism` is Authoritarian, coloured black (20,20,20).
- `neutrality` is Monarchist, coloured purple (128,48,168).
- `theocracy` Theocratic is **new**, coloured white (238,238,238).
- **Subtypes** (sub-ideologies) are the author's set of 2026-09-30, in
  `ideologies.SUBTYPES` (key, name, description); a renamed vanilla subtype keeps its
  key (e.g. `despotism` is "Absolute Monarchy", `leninism` "Vanguardism", `theocrat`
  "Hierocracy"). Democratic: Conservatism, Liberalism, Social Democracy, Populism,
  Agrarianism, Constitutional Monarchy. Communist: Orthodox Marxism, Vanguardism, Party
  Centralism, Council Communism, Anarcho-Communism, Agrarian Socialism. Authoritarian:
  Military Junta, Fascism, Corporatism, Strongman Rule, Technocracy, Revanchism.
  Monarchist: Absolute Monarchy, Oligarchy, Feudalism, Enlightened Absolutism, Elective
  Monarchy, Legitimism, and the author's **Personal Union** (2026-10-07, Merlgould) and
  **Khanate** (2026-10-09, Sanada) and **Semi-Constitutional Monarchy** (2026-10-13,
  Avesária, then Bromé); Democratic also has the author's **Stratocracy**
  (2026-10-07, Krionik) and **Radical Republicanism** (2026-10-09, Vilna). Authoritarian also has the author's **Bleacherism** (Alban
  supremacy; officially a senatorial republic under a strongman): ILR CTF ETR MZG;
  KIL is Legitimism; and **Humanism** (2026-10-12, the Humanist State: humans above
  Valsora's other races, apartheid-style). Theocratic: Hierocracy, Clerical Monarchism,
  Holy Order, Synodal Rule, Prophetic Rule, and the author's **Divine Republicanism**
  (2026-10-12, Muqadasa Salamat). Vanilla's Earth-bound ones (`nazism`, `japan_militarism_ideology`
  …, `ideologies.HIDDEN`) stay defined because vanilla's characters and focus files name
  them, but are never given to generated leaders. The author wanted no more on 2026-09-30, and
  has added their own since (above).
- Subtype descriptions start with the subtype's name ("Feudalism: …"), so it shows on
  mouse-over (author). `lordly_republic` "Lordly Republic" (democratic) is the author's
  own: a republic in which the nobility and clergy retain significant power.
- **Every ruler is a set character** (author, 2026-09-30: no subtype left to chance).
  `nations.LEADERS` gives each tag its subtypes; the first leads the country, and the
  country starts under that subtype's ideology (elections on if democratic).
  `cultures.leaders` makes the characters (`common/characters/valsora_leaders.txt`,
  id `TAG_leader_<subtype>`, never `TAG_<subtype>`, which the game reads as the country's name under that subtype): a name from the culture's list (famous surnames skipped, full
  names unique map-wide; famous ones met in a list already in use, like Franco and Windsor on
  2026-10-13 (and di Savoia, Garibaldi and de Castro, seen on the nation sheet), are drawn again (`cultures.DRAW_AGAIN`), so no one else's name changes) and a generic politician portrait of the culture, seeded by
  tag. Hand-made rulers (`HAND_MADE`: ROU, AIS) keep theirs; Rouental also gets
  `ROU_leader_constitutional_monarchism` and `ROU_leader_leninism`, promoted by the Polite and Rudely
  focuses. Author's picks: CRD Enlightened Absolutism; EVR, SGN Feudalism; HLR, STO
  Absolute Monarchy; LST Elective Monarchy; SGV Oligarchy; LZC, GDN Lordly Republic;
  LNT Conservatism; RMD Social Democracy; RST Revanchism; VLN Liberalism; ESD, CRZ
  Constitutional Monarchy; PLH Prophetic Rule. The six continent placeholders were not
  chosen and default to Absolute Monarchy. Characters: Roland feudalism, Serelle
  strongman_rule, Mahaut theocrat, Communist Merlovich anarchist_communism.
  `check_mod.py` checks every country has a recruited leader of its ruling ideology
  (mutation-tested). Its party icon `GFX_ideology_theocracy_group` is
  a placeholder, `source/ideologies/theocracy_placeholder.png` (the anime picture),
  centre-cropped to 64×64. The author and a friend will draw the real icons.
- **Party list.** Vanilla's politics view fits four 16 px party rows. `interface/countrypoliticsview.gui`
  is vanilla's (`source/interface/`) with `parties_grid` rows at 13 px, so five fit;
  `check_mod.py` checks it.

How it's built:
- `common/ideologies/00_ideologies.txt` overrides vanilla. It is vanilla's file
  (`source/ideologies/`) with the colours changed and a theocracy block modelled on
  neutrality.
- Every country starts at 20% for each ideology; every `set_popularities` lists all five.
- `check_mod.py` checks that popularities name real ideologies and sum to 100, that
  every `ruling_party` / `has_government` is an ideology, and that character
  sub-ideologies exist.

**Map colours come from `common/countries/colors.txt`**, not the `color` in each
country file. Tags missing there got random colours in-game, which is why most were
wrong until the build wrote its own (`color` plus a lighter `color_ui`).

**Map colour per government** (`nations.LOOKS`) uses cosmetic tags `TAG_GOV_<IDEOLOGY>` (not `TAG_<IDEOLOGY>`: its flag would clash with `TAG_<ideology>.tga` on Windows, which ignores case; `check_mod.py` checks file names for this),
defined in `common/countries/cosmetic.txt`. An `on_ruling_party_change` on_action sets
them, or drops them for ideologies with no entry, so every route to power recolours the
country. Their flags reuse `source/flags/TAG_<ideology>.png`, and their names are
localised for every ideology. Rouental:

| Government | Map colour | Flag |
|---|---|---|
| Monarchist, Authoritarian | royal green | banner of arms |
| Democratic | tan | tricolour |
| Communist | maroon (128, 16, 16) | the author's Liberté flag (was plain maroon) |
| Theocratic | gold | sword and fleurs quarter of the banner |

## Cultures (`cultures.py`): generic portraits, names, graphical culture

Vanilla's generic portrait lists (`portraits/*.txt`) are keyed by Earth continents, which
don't exist here. That was the cause of "Failed to generate a portrait / name" and
"unknown continent europe" in error.log. So the build writes:
- **`portraits/valsora_portraits.txt`.** One `continent = { name = <ours> … }` block per
  continent, plus `TAG = { … }` blocks for countries that look different. Each block has
  army / navy / political (per ideology) lists of vanilla 1.19 generic sprites.
  `source/names/vanilla_portrait_sprites.txt` is the list of those sprites, copied from
  vanilla `interface/_random_portraits.gfx`; `check_mod.py` checks against it.
- **`common/names/valsora_names.txt`.** Each tag gets a vanilla culture's name block
  (`source/names/vanilla_names.txt`). UTF-8 without BOM, like vanilla.
- **Graphical culture** in `common/countries`.
- **Who gets what:**
  - The continent defaults (author's choices) all use Europe portraits except where
    noted: Nonscio ENG, Araseos ITA, Aislada AST (commonwealth gfx), Solitas SWE,
    Yastreovakia POL. Usnistan is PER with Arab + African portraits and middle_eastern
    gfx; Orientalis is JAP with Asian portraits and asian gfx.
  - The author's flags can come as one `.pdn` with a layer per flag
    (`import_flags.py`; 2026-10-04: its "Marchers" layer showed The Marches had been
    given the three-lozenge flag, which is its "Duchy of the Mountains"; fixed).
    2026-10-05: **the author swapped the Marches' flag to the three lozenges** after
    all ("the sword didn't read well"; the sword flag is now the file's "Spare" layer),
    and redrew Fraxhemark's.
  - Overrides are in `TAG_CULTURE`: the Reibonnaise states (ROU SGN EVR HLR SGV LST LZC
    GDN) and Placeholdros (LNT) use FRA names and France portraits (author: French for now);
    RST VLN ESD CRZ PLH use POR names (added to `source/names/vanilla_names.txt` from
    vanilla) and Europe portraits.
- **Scientists** (2026-10-14): every continent and country block also has
  `scientist = { male female }`, vanilla's generic scientist portraits
  (`interface/_scientists_portraits.gfx`: Europe's for European, French, Iberian and
  American cultures as vanilla does for North America, Arabia's and Africa's for Usnistan,
  Asia's, India's, South America's). Without them every generated scientist logged "Failed
  to generate a portrait … scientist" and then, on every save load, an empty icon (`""` and
  `"_small"`, icon_entry.cpp): 156 + 568 lines in the 2026-10-02 log. Operatives use
  vanilla's default (an unknown silhouette).
- **Vanilla's portrait files** (`00_portraits.txt`, the DLCs' `01_anniversary`, `02_tiger`,
  `03_mtg`, `027_lar` and `998_scientist_portraits.txt`) are keyed by Earth continents: 139
  error.log lines ("unknown continent europe", then an unexpected token per list). The mod
  ships a file under each name (`cultures.VANILLA_PORTRAIT_FILES`); `00_portraits.txt`
  keeps vanilla's `default` block (fallback and operative portraits). `check_mod.py` checks
  all six and the scientist lists (mutation-tested).

## Superevents (`superevents.py`)

TNO-style, built only from vanilla pieces. **Confirmed in-game** (author, 2026-09-29):
the first build showed window, picture and text, but no music and no background (both
fixed below and confirmed: music plays, background shows). Title and quote are
white via `§W…§!` in their localisation (the typewriter fonts draw dark). How they work:
- **Calling one.** `valsora_superevent_<id> = yes` (inside `hidden_effect` in a focus).
  It sets global flag `valsora_superevent_<id>`, clearing the others, and fires hidden
  event `valsora_superevent.N` for every human player.
- **The event** sets country flag `valsora_superevent_open` and does
  `play_song = "valsora_gladiators"`, the way vanilla plays its speeches.
- **The window.** A `player_context` scripted GUI (`valsora_superevent_window`) is
  visible while that flag is set. Title, quote and author come from scripted
  localisation keyed on the global flags. There is one picture icon per distinct image,
  shown via `<element>_visible` triggers. The close button's `_click` clears the flag.
- **Assets.** The music is `source/superevents/*.ogg`: the first 45 s of the author's
  MP3s with a 4 s fade, Vorbis like vanilla music (`SONGS` in `superevents.py`).
- **Songs must belong to a music station**, or `play_song` logs "Song doesnt exist" (the
  first build had only an `.asset`).
  - Layout, from the Music Mod Creation Tool's HOI4 template: `music/valsora/` holds the
    `.ogg`, `valsora.asset` (`music = { name file volume }`) and `valsora.txt`
    (`music_station = "valsora"` + `music = { song chance }`, here chance factor 0).
  - The station also needs `interface/valsora_music_station.gui` (`valsora_faceplate`
    and `valsora_stations_entry`), a 2-frame cover sprite, and loc `valsora_TITLE`
    ("Valsora Radio") plus each song key.
- **Pictures** are cropped to 2:1 and scaled to 840×420 DDS.
- **Background.** `GFX_tiled_window_transparent` is see-through (vanilla's event window
  gets its look from separate header/footer images), so the window has its own
  generated background, `superevent_bg.dds`: dark, with gold frames.
- **With the Deco UI** (`DECO_UI`, 2026-10-15; `superevents_deco.py`): the mockup's Superevent board
  (`deco_ui/art/mockups/source/Superevent.html`), drawn with numpy and Pillow. The window covers the screen: a dark
  veil over the map (a cornered tile) with faint gilt rays round the middle and the board's vignette (drawn at half
  size, scale 2), and the panel centred on it, every element a direct child of the window (the visibility triggers
  name them): one picture holds the crest, the 900 x 645 frame (lacquer, gilt border, corner brackets, the rings round
  the picture) and the now-playing tab; over it a title strip per superevent (gilt Federo capitals between stepped
  hairlines, baked, since the hairlines follow the title's width: long titles shrink to fit), the picture with gilt
  fans and arcs in its corners, a diamond on its lower edge, the quote (`valsora_deco_italic_18`, curly quotes, no
  `§W`), the attribution (`valsora_deco_section_11`), the gilt "History Marches On" button (Esc closes it too) and the
  song (`ValsoraSupereventSong`, "Valsora Radio · Rafael Krux — Epic Church Organ", `valsora_deco_label`). The
  build measures every quote, attribution and song with the Deco UI's font files and stops if one would not fit its
  box (a box too short drops lines silently). **Seen in game** (2026-10-15, the test superevent): all eight titles
  drew at once (only the pictures had visibility triggers; each title has its own since, from the superevent's
  flag), and the author asked for something other than the guillotine: the crest's medallion is lacquer and holds
  **Valsora rising** (the top half of the Deco UI's globe, `globe_art.globe`), `superevents_deco.EMBLEM`; a compass
  star, an hourglass and a laurel wreath are `EMBLEMS` too, shown in `deco_ui/art/proposals/crests/`.
- **Current set.** Eight superevents: one per Rouental leadership focus (five), the
  Rouentaise civil war (Execute the Prince; the author's soldier photo), AIS
  "Fucking Explode" and the test one, fired by Rouental's test decisions (`rou_test`, last so the others keep their
  event ids). The quotes are Claude-written except the civil war's (the
  author's); all but the civil war use the author's anime picture and Entry of the
  Gladiators. The civil war has Rafael Krux's "Epic Church Organ" (`valsora_organ`,
  `epic_church_organ.ogg`, made with the ffmpeg bundled in the `imageio_ffmpeg` Python
  package: first 45 s, 4 s fade, Vorbis 160k); it replaced "Monsieur d'Elbée", which
  the author didn't like.
- **Checks.** `check_mod.py` checks scripted effects and events that are used, songs
  and their files, scripted localisation keys, and GUI window, element, sprite and
  button-text references (mutation-tested). Since 2026-10-15 decisions count among the users of effects and events,
  our events' titles, descriptions and options and our decisions and categories must be localised (hidden events and
  never-visible decisions excepted), and a decision's short icon name (`generic_x`) must be a sprite
  (mutation-tested: 9 breaks, all caught).
- **error.log on that test** also had 128 pairs of `Icon definition "" / "_small"`
  (icon_entry.cpp) when a second game was started: scientists generated without a
  portrait, one pair per scientist on each load; fixed 2026-10-14 (see Cultures).

`check_mod.py` also checks that recruited characters exist and are localised, that portrait
sprites resolve to files, and that every focus id and prerequisite is valid and localised.

## What HOI4 requires (verified against vanilla 1.19.3 files)

- `provinces.bmp`: 24-bit, 40-byte BITMAPINFOHEADER (no V4/V5), under 40 MiB. Every
  province is one 4-connected blob of at least 8 px (16 here), with a box under 1/8 of the
  map each way. No 2×2 window may hold four provinces; this check wraps across the seam.
- `definition.csv`: **CRLF**, first row `0;0;0;0;land;false;unknown;0`, ids contiguous from
  1, land continent ≥ 1, sea/lake continent 0. Terrain values: `plains` / `ocean` / `lakes`.
- `heightmap.bmp`: 8-bit greyscale; the water plane is 95 (`WATER_HEIGHT = 9.5`). Land must
  be > 95, water < 95. `terrain.bmp`: index 0 = plains, 15 = ocean (lakes too). `rivers.bmp`:
  255 = land, 254 = water. `cities.bmp`: map-sized; index 4 is in no city group, so no town
  meshes. All of these must be exactly map-sized.
- 8-bit BMPs with a full 256-colour palette write `biClrUsed = 0`, as vanilla does; with
  256 there the game logs "Palette in rivers.bmp is probably not correct".
- `trees.bmp`: any size (vanilla 75/256 of the map). `world_normal.bmp`: half size,
  24-bit, flat = RGB (128,128,255).
- `map/terrain/`: `colormap_rgb_cityemissivemask_a.dds` and `fow_rgb_waterspec_a.dds` at
  half size; `colormap_water_0/1/2.dds` at 1/2, 1/4 and 1/8. Uncompressed A8R8G8B8 with one
  mip loads fine. Rows run top-down, unlike BMP.
- `buildings.txt` (`state;type;x;height;z;rot;adjacent_sea`, with z = 2560 − pixel y):
  - **Per state:** air_base, anti_air_building ×3, arms_factory ×6, industrial_complex ×6,
    fuel_silo, nuclear_reactor_spawn, radar_station, rocket_site_spawn (also used by
    rocket_site and mega_gun_emplacement), stronghold_network, synthetic_refinery, and
    dockyard if the state is coastal.
  - **Per land province:** bunker, special_project_facility_spawn, supply_node.
  - **Per coastal province:** naval_base_spawn and floating_harbor (both naming the sea
    province), naval_headquarters, naval_supply_hub, coastal_bunker.
- `unitstacks.txt`: land provinces need types {0,1,9,10,21,22,38}; sea provinces need
  {0,1,2,9,10,11,12,21,22,23,30,31,38}; lakes need none. The game places the kinds a
  province lacks itself, badly: ships in port (19, 20) "too far away from center" in two of
  Merlo's large sea provinces (error.log, 2026-10-14). So every kind vanilla's own map has
  is written (`build_mod.py`, read from vanilla's file): 0, 9, 10, 21, 38 near the centre;
  1-8 and 22-29 part of the way toward each neighbour, longest borders first, facing it;
  11-18 and 30-37 fleets on a ring round a sea province's centre; 19 and 20 ships in port,
  on a coastal province's coast and just offshore (at the centre elsewhere). The last
  column is vanilla's offset: 0.3 on land and in port, 1.0 at sea. `check_mod.py` wants 19
  and 20 everywhere but on lakes (mutation-tested).
- `weatherpositions.txt`: each strategic region needs a `small` and a **`big`** row (not
  "large").
- Other rules:
  - Every province is in exactly one strategic region, and a state's provinces all share
    one; naval regions are contiguous. State and region ids are contiguous.
  - Supply nodes and railways only go on provinces that are in states.
  - `adjacencies.csv` keeps the `-1;-1;;-1;-1;-1;-1;-1;-1` end line.
  - Localisation is UTF-8 **with BOM**.
  - `ambient_object.txt` frame positions follow the map height: top frame at H+142, logo
    at H+82.
- **At most 65,536 province borders** (HOI4 wiki, Map modding: an integer overflows and
  the rest are not drawn, "usually hit at about 21000 provinces"). A border is a stretch
  of boundary two touching provinces share, land or water alike; a pair touching in
  several places has several. They are made in province id order (here reading order),
  so a map over the limit loses its province and state lines from some row down
  (2026-10-12, author's screenshots: 73,231 borders, no lines south of row ~1995; the
  count put the overflow at row ~1990). `check_mod.py` counts them (`borders.py`) and
  fails over the limit, with a note within 4,000 of it. `merge_provinces.py` merged
  4,313 small provinces: 20,454 provinces, 60,318 borders, land provinces 186 px on
  average (river pixels still 91 % on borders), and new outlines are cut at ~190 px.
- **The minimap is a fixed picture**, not drawn from the map: `gfx/minimap/minimap.dds`
  (sprite `GFX_minimap_world`, vanilla `interface/unitview.gfx`), shown at its own size
  inside `gfx/minimap/border.dds` (drawn at -5, -5). The window sits at the lower right
  (`interface/minimap.gui`: vanilla x = -343 y = -98, for its 268×97 picture (border
  276×105, read from vanilla's own files on 2026-10-14; "about 263" was a guess before) plus
  the 75 px of map-mode buttons), and `MINIMAP_TOGGLE_SHIFT` (vanilla 270) is how far ctrl+m
  slides it away. Until 2026-10-13 ours showed vanilla's Earth (author's screenshot).
  `minimap.py` draws Valsora's at 194×97 (the map's 2:1) with the window at x = -274 and a
  slide of 202, as Equestria at War does for its 2:1 minimap (5 px further from the
  buttons than vanilla's); `check_mod.py` checks all four (mutation-tested). **In game**
  (2026-10-14, author's screenshot): Valsora's land, beside the map-mode buttons.
- **The world tension globe is a fixed picture too**: `gfx/interface/world_tension_icon_big_strip.dds`
  (sprite `GFX_world_tension_icon_big_strip`, vanilla `interface/topbar.gfx`), ten 49×49 frames
  side by side, one per tenth of world tension (vanilla's Earth catches fire frame by frame),
  and a small 29×25 icon, `world_tension_icon.dds` (diplomacy view, peace conference). Until
  2026-10-14 both showed Earth (author's screenshot). `globe.py` draws Valsora's: the land
  on a lit sphere seen from above Nonscio and Araseos (orthographic, the map read as
  longitude and latitude). As tension grows it burns from below as vanilla's does: glowing lava
  cracks (the borders of random cells on the sphere, warped) spread upwards ahead of the heat, the
  surface chars to a dark red crust that keeps the light and shape, and a molten glow rises from
  the bottom (the first version painted flames over the disc, an orange blur at 100 %, author's
  screenshot, 2026-10-14). The small icon is ringed with flames; `check_mod.py` checks both sizes (mutation-tested);
  `python3 scripts/globe.py` writes `dist/tension_globe_preview.png`.
- Map errors crash on launch unless the game runs with `-debug`. Always test with it.

## Vanilla content switched off

`replace_path`: history/states, history/countries, history/units, history/general,
map/strategicregions, events, common/decisions, common/ai_strategy,
common/ai_strategy_plans, common/on_actions, common/bookmarks. `descriptor.mod` and the
launcher's `valsora_test.mod` must carry the same lines. The launcher reads the outer file,
so ship both. Each replaced folder keeps at least one valid file.

The following vanilla files are overridden:
- `tutorial/tutorial.txt`, cut down to its one step with no ids. Vanilla's refers to Earth
  states and provinces.
- The 21 ENG/FRA/GER/ITA/JAP/SOV/USA files in `common/ai_navy/{goals,fleet,taskforce}`,
  emptied.
- The minimap's picture and frame (`gfx/minimap/minimap.dds`, `border.dds`) and
  `interface/minimap.gui` (vanilla's, `source/interface/vanilla_minimap.gui`, with the
  window moved), plus `MINIMAP_TOGGLE_SHIFT` in `common/defines/valsora_graphics.lua`.
- The six portrait files of vanilla and its DLCs (see Cultures).
- The world tension globe and its small icon (`gfx/interface/world_tension_icon_big_strip.dds`,
  `world_tension_icon.dds`).
- The start date's picture (`GFX_select_date_valsora`, `minimap.write_bookmark`: Valsora on
  the minimap's parchment, in place of 1936's soldiers).
- `common/ai_faction_theaters/ai_faction_theaters.txt`: the AI's faction theaters, one per
  continent with the sea regions on its coasts (split where they don't connect), in place
  of vanilla's Earth ones (Barbarossa, North Africa ...: 30 error.log lines, 2026-10-14).
- Everything in `source/vanilla/` (below).

**Vanilla's generic content comes back as the mod's own** (2026-10-14, read from the
author's copy of the game). The replaced folders also held what every country uses, so
from the first build there were no election, ace, war justification, nuclear, capitulation
or operative events, no faction and demand events (`Generic.txt`), no collaboration
governments (`LAR_occupation.txt`), no generic AI strategies and no generic on_actions.
`source/vanilla/` (its README lists it all) now holds:
- `files/`: exact copies of the vanilla files the mod ships changed (`vanilla_sync.py`);
  `vanilla_parts.py` moves their dates to 2036 and cuts Earth-only blocks out of the AI's
  `default.txt` (Japan's, the USA's and Britain's naval focus, Earth's area priorities);
- `curated/common/on_actions/valsora_generic_on_actions.txt`: vanilla's generic hooks
  (elections, aces, war justification, army leaders, doctrines, compliance, nuclear and
  capitulation news, the end of an ideological civil war, operatives), cut by hand from
  vanilla's on_actions without their Earth parts. Vanilla's peace conference hooks only
  clear flags on Earth states, so none came back;
- `index/`: lists of vanilla's names, which `check_mod.py` checks ours against (sprites,
  technologies, equipment, modules, battalions, ideas, defines, map files).
And stand-ins, so what vanilla still names exists (error.log, 2026-10-14):
- **Decisions**: `replace_path` is not recursive, so vanilla's decision categories still
  load, as do the focus trees, ideas and scripted triggers that name its decisions (1,142
  lines of "Invalid decision" / "Invalid Decision ID"). `vanilla_parts.stand_ins` writes a
  never-visible decision of the same kind (decision, mission, targeted, state-targeted) for
  each of the 732 names, in the category `valsora_vanilla_stand_ins`.
- **Earth's country tags** stay defined (vanilla's technologies, AI and peace conference
  name them; removing them would break those files): each of the 364 has a history file
  (`TAG - Name.txt`: capital state 1, owning nothing, monarchist), for the 728 lines of
  "is missing a history file". `check_mod.py` requires every one and no more in them.
- **Events** the shipped files fire only for Earth's countries (Denmark's election,
  Munich's Czech crisis, ...) are hidden empty events
  (`events/valsora_vanilla_event_stand_ins.txt`).

Left loaded on purpose, and noisy in `error.log`:
- National focus: it holds the generic tree our countries use.
- Ideas, MIOs, scripted effects and triggers, ai_areas, operations and achievements. They
  reference vanilla ids, which the previous build showed the game tolerates.

## The Gazetteer (`docs/GAZETTEER.md`; the working detail: `docs/GAZETTEER_INTERNALS.md`)

A web site, **https://rouental.github.io/Valsora-HOI4/**, where the author's friends fill in their own nations (author,
2026-10-14), each behind a password the author gives them: names and governments, rulers, party leaders, political
advisors, generals, admirals and other advisors with the base game's traits, companies of the base game's kinds (arms
makers as military-industrial organisations and designers, industrial concerns), flags, releasables, suggestions and
requests; once a nation's states
are the author's own lines, its map facts too (state names and buildings, cities, terrain, rivers, railways, supply
hubs). `scripts/gazetteer.html` is the page (`gazetteer_site.py` builds the site, `facts_export.py` its map data); the
atlas is the author's Firebase project `valsora-hoi4` (Firestore). Read `docs/GAZETTEER_INTERNALS.md` before changing
the page, its rules or its import.
- **Rules that must hold:**
  - Never commit a password (they stay in `work/`) or the author's Google address: the Firestore rules
    (`source/gazetteer_site/firestore.rules`) say `OWNER_EMAIL`, and the author pastes them in the console with their
    address. After changing the rules, ask them to paste them again.
  - Without its password a nation can be neither listed nor changed (the rules allow `get` and `list` only inside a
    nation's folder, no `{path=**}`); `owner/*` is the admins' alone; only the author changes admins.
  - Map tools wait for a nation's states (author, 2026-10-15: "once their state borders have been set in the mod, full
    customization would be unlocked"): `gazetteer.finals`, or `planned/unlock` set by the author; the import drops a
    closed nation's map facts.
  - Only the author's Claude publishes the site (`gh-pages`, allowed for it alone: "it's ok to put it on a new branch").
- **Republish** after map changes: `sh scripts/publish_site.sh "message"`; test the page first, after
  `python3 scripts/facts_export.py`: `python3 tests/gazetteer/run.py`, `traits.py` and `companies.py` (same folder).
- **Into the mod:** the author's **Save every nation as a file**, then `python3 scripts/gazetteer.py import FILE`
  (`source/gazetteer/<TAG>.json`, pictures in `source/gazetteer/assets/`, flags of HOI4's shape into `source/flags/`),
  a rebuild (`river_provinces.py` first after new rivers), `gazetteer.py suggestions` if there are any, and
  `gazetteer.py status`, which lists the open requests and what is left to do by hand: tell the author those. A
  nation's facts win over the `.pdn` and `nations.py` for that nation; hand-made rulers (`HAND_MADE`) keep theirs.
  Without facts the build is byte-identical. `GAZETTEER_DIR` / `GAZETTEER_FLAGS` point the scripts at other folders
  (tests: never import a test file into `source/gazetteer/`).

## Deco UI (`deco_ui/`): part of the mod

**The Valsora Deco UI** is the author's art deco interface, made with another Claude session (v0.1–v0.4.4)
and moved here on 2026-10-14 (v0.4.5–v0.4.8 the same day: the politics screen flush under the top bar,
styled tooltips). **Since v0.5 (2026-10-14, later) it is part of the Valsora mod** (author: "roll the UI mod
into the main Valsora mod, but with the knowledge that I might eventually want it taken out again ... I'd like
to simplify things to only have the one install"): a restyled top bar, every side panel (the politics screen
re-laid to its mockup; 16 others flush under the top bar with a notch for the flag medallion and a deco header,
v0.5), the state panel, focus tree, map modes and minimap (v0.5), main menu (the Valsora background) and a core
skin. `deco_ui/CLAUDE.md` is its full handoff guide (engine facts, generators, what is confirmed in game); read
it before touching the UI. In short:
- **One switch:** `DECO_UI` in `scripts/common.py`. True: `scripts/deco_ui.py` (after `build_mod.py`)
  copies `deco_ui/valsora_deco_ui/` into the build, and `minimap.py` draws the minimap in its style. False:
  the game's own interface (`build_mod.py` empties the build first, so nothing of the Deco UI is left).
- The build makes the Deco UI's Valsora-dependent files itself, so they can't go stale: the long-name trigger
  (`deco_ui/tools/long_names.py`: names too long for the medallion's large font) and the politics screen
  (`make_politics.py`, from Valsora's own `countrypoliticsview.gui`, kept in `work/deco_base/`; its
  sub-ideologies are those Valsora names, 39). The only file both ship is that one (`deco_ui.REPLACES`).
- Everything else (textures, fonts, the game screens it patches) is built by hand with the game's files at
  hand: `CHROMIUM_PATH=/opt/pw-browsers/chromium python3 tools/build_all.py` in `deco_ui/`, after the
  vanilla links its section 3 lists (`deco_ui/reference/valsora` is `build/valsora_test`); then rebuild
  Valsora. `validate_preview.py` must end with `PROBLEMS: none`. `gen_textures.py` redraws only the textures whose
  drawing changed (`--all` redraws all); after a redraw, `python3 tools/restore_noise.py` puts back those that changed
  only by anti-aliasing noise.
- `check_mod.py` checks the merged mod: the Deco UI's localisation in the game's 9 languages (only its files
  may be other than English), its politics screen's five 19 px party rows, every kind of sprite in a .gfx, and
  sprites the game's own .gui files name without defining (`source/vanilla/index/gui_undefined_sprites.txt`).
  A game sprite (`source/vanilla/index/sprites.txt`) in a game .gfx the Deco UI ships patched (`nationalfocusview.gfx`)
  may point at the game's own texture; a texture in a folder of ours (`valsora…`, `VAL/`) must be shipped
  (mutation-tested).
- There is no separate release any more (`dist/valsora_deco_ui.zip` was removed). The author was told to delete
  the old `mod/valsora_deco_ui/` and `mod/valsora_deco_ui.mod` and take it out of the playset: left in, it
  loads after Valsora and puts its older files back.
- Its `reference/` (the game's files, git-ignored) must never be committed: it is Paradox's content.
- **v0.6 and v0.7** (2026-10-15, not yet seen in game): the focus tree after its mockup (v0.6; the focus icons are
  the game's, as the author asked); the army bar (`make_leadergroups.py`, textures `lg_*`, numbers in
  `layout_armybar.py`) and the events (`make_events.py`, textures `ev_*`) in the deco style at the game's paths and
  sizes (v0.7). Their previews, `deco_ui/build/preview_armybar.png` and `preview_events.png`, show the game's art
  beside ours, so they stay in the git-ignored `build/` and are only sent to the author.
- **v0.8** (2026-10-15, the second night, not yet seen in game): **the game's own fonts** redrawn in the deco faces at
  their paths (`deco_ui/tools/game_fonts.py`, 28 fonts: tooltips, lists, the designer, leader and unit screens,
  settings, window titles; the author: "could you switch to the art deco fonts throughout the UI? for example,
  currently the title of Roland is displayed in the base game's font"), a size or two under the game's so its text
  keeps fitting the game's boxes; the army bar's play / stop row centred over each general; event options centred
  between the picture and the card's edge; a gilt Valsoran globe in the middle of WORLD NEWS. A mockup of **larger
  flags** is in `deco_ui/art/proposals/hd_flags/`, **not in the mod** (author: "Maybe do a mockup of how it could look,
  but don't add anything to do with it into the mod yet"): it needs the seven flags we have only at 82 x 52.
- **v0.8.1** (2026-10-15, later): the news masthead is **VALSORAN (globe) STANDARD** (the author: WORLD NEWS "still looks
  lopsided ... maybe swap to something like "Valsoran Standard" or Clarion or Dispatch ... so both words are the same
  length"), the globe redrawn to read at 60 px, and the news page centred under it. Other names:
  `deco_ui/art/proposals/news_masthead/`. The author kept it (2026-10-15).
- **v0.8.2** (2026-10-15, the third round, from the author's screenshots of v0.8.1): the superevent shows one title
  and Valsora rising in its crest; the event cards' crest is a stepped keystone (`deco_ui/tools/crests.py`); a long
  option's three lines fit (`valsora_deco_option_14`); a name of two lines shows both under the flag
  (`layout.NAME_SLACK`); the selected armies' badges, the air wings and the operatives start below the medallion
  (`make_mapviews.py`); the news globe is lit. Options for the globe and the crests: `deco_ui/art/proposals/news_globe/`
  and `crests/`. The larger flags' test version is drawn from the same tools (`VALSORA_FLAG_SCALE`).
- **Proposals for the side panels' own pictures** (research, production, the market, the overview strip, the
  intelligence agency, the spirit banners) are in `deco_ui/art/proposals/panel_pictures/`, **not in the mod**
  (author, 2026-10-15: "don't put them in the mod yet. I'd like to see and approve them first").

## Current state

Where things stand; the history, date by date, is `docs/HISTORY.md` (add each day's entry at its top).

- **The build** (2026-10-15): 21,078 provinces (20,690 land, 363 sea, 25 lakes), 62,183 province borders (HOI4
  draws 65,536: `docs/BORDER_LIMIT.md`), 3,149 states, 122 strategic regions (42 sea); 183 countries in the mod,
  161 of them on the map, 95 of those with a flag of their own (66 fly a stripe in their map colour); the states of
  39 are the author's own lines (`gazetteer.finals`). Two starts, both on 1 January 2036. The Deco UI is v0.8.3 (the
  ringed globe on the news masthead and, whole, as the superevent's crest; the keystone's diamond lowered).
  Rouental has test decisions for every kind of event and a test superevent (`test_events.py`).
  Rouental's Gazetteer page is in the build (`source/gazetteer/ROU.json`), its admiral among its characters; no
  other nation's yet. The Gazetteer offers the base game's traits for every leader and takes requests for new ones,
  and has political advisors and companies (arms makers and industrial concerns of the base game's kinds, with logos;
  requests for new kinds) (published 2026-10-15). The test version with 1.5 times larger flags is built beside the mod by
  `sh scripts/build_flags15.sh` and sent as its own zip (`docs/HD_FLAGS_TEST.md`), not put into the mod.
- **Seen in game last** (2026-10-15, the third round): the Deco UI v0.8.1 with Rouental's test decisions (the
  author's screenshots): the country, long, news and leader events and the news page worked; the state and operative
  events, a long option, the superevent's title, long names under the flag and the army badges under the medallion
  didn't (all fixed in v0.8.2, not yet seen). The in-game error counter showed 8 errors: their `error.log` wasn't sent.
  Not seen yet: the Deco UI v0.8.2 and v0.8.3, the two starts, Vilna and Placeholdgrad. The Deco UI's checklist for the
  author is in `deco_ui/valsora_deco_ui/README.txt` (Things to check) and `deco_ui/CLAUDE.md` (section 10).
- **Waiting on the author:** the larger flags' test version (`docs/HD_FLAGS_TEST.md`); the panel picture proposals (on
  hold, the author: "I don't want to move ahead with the panel pictures just yet"); the tech tree proposal's eight
  questions (`docs/TECH_TREE_2036.md`: "I'll get back to you on that"); the other size options
  (`docs/SPEED_AND_SIZE.md`); the `error.log` behind the 8 errors of their last test. Settled (2026-10-15): the news
  masthead stays VALSORAN STANDARD, its globe the ringed one, the event cards' crest the keystone; the zip stays in
  `dist/` (Decisions worth keeping, "The mod's zip").

## Known gaps

1. **States**: 122 of the 161 nations on the map (121, and Belekria in part) have states Claude cut from their
   outlines (`apply_outlines.py`, about 1,300 px each), not lines of the author's; their Gazetteer map tools stay
   closed until the author draws them. The old `.pdn`'s country colours, moved to the new layout, are its Notes
   layer.
2. **Terrain** is plains everywhere but Rouental's provinces (from its Gazetteer page); there are no trees, and the
   relief is noise. A generated terrain (with its own relief) exists as a test only, `terrain_test.py`
   (2026-10-12): the author said not to add it to the mod yet. It follows the author's geography where they gave
   it (the Vale of Reibonne). Rivers are only where the author or their friend drew them; railways wait (the
   author, 2026-10-15), but for Rouental's one from its Gazetteer page.
3. **Country content**: Rouental (leaders, focus tree, civil war, royal host) and Merlovich (focus tree) are built
   out; every other country has its set ruler, generated characters, the generic focus tree and a generic infantry
   army. Generic portraits and name lists exist (see Cultures), scientists' too since 2026-10-14.
4. **What still reads as the 1940s**: the tech tree's names, descriptions and pictures (its dates are 2036's;
   `docs/TECH_TREE_2036.md` is a proposal), the 3D models, and the game's own pictures inside the side panels (the
   Deco UI's proposals wait for approval).
5. **Province borders**: 3,353 left under HOI4's limit for new outlines (`docs/BORDER_LIMIT.md`).

## Working with the author

**Keep `docs/PROBLEM_LOG.md` up to date** (author, 2026-09-30): every error or problem,
its cause and its fix, newest first.

**Every time the author sends a `.pdn`, send `source/HOI4 Mod Map.pdn` back when done**
(author, 2026-09-30), so their copy has every edit. Their upload may be based on an
older version (the 2026-09-30 one predated the sea zones and recolours): diff its game
layers against `source/` first, and merge, keeping the current game layers and taking
their own layers (outlines, rivers, names, references) from the upload.

**Vanilla reference files** (2026-10-14): the author's private repo `Rouental/HOI4-Files`
holds a copy of their 1.19.3 install under `HOI4 Files/`: common, events, history,
interface, localisation (every language), map, portraits (with
`998_scientist_portraits.txt`) and, since later that day, `gfx/` at the repo's root (leader
portraits, interface images, minimap, FX shaders; a sparse checkout without the font
textures, models and event pictures is enough, 2.6 GB). Attach it to a session with the
Valsora repo and clone it to `/home/user/hoi4-files`; check vanilla there before searching
mirrors or other mods. It is Paradox's content: never copy it wholesale into this public
repo (single vanilla files the mod overrides, like `source/interface/`, are fine).

The author tests in-game and reports crashes and `error.log`. They cannot see the
pipeline, so always say which files changed and how to install:
1. Delete `mod/valsora_test/` and `mod/valsora_test.mod`.
2. Unzip `dist/valsora_test.zip` into `mod/`; it contains both.
3. Launch with `-debug`.
