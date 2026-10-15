# Valsora — HOI4 total conversion

Turns the author's hand-drawn fictional world (paint.net `.pdn`) into a Hearts of Iron IV
map. Game version: **1.19.3**. The mod installs as `mod/valsora_test` in
`Documents/Paradox Interactive/Hearts of Iron IV/` (on the author's machine Documents sits
under OneDrive — keep that segment in any absolute path). Valsora takes place in **2036**:
the game starts on 1 January 2036 (see "2036" under Decisions worth keeping).

This is the second attempt. The current build is deliberately minimal: the real
geography with **placeholder square provinces**, one placeholder country per continent,
and only what the game needs to load. Borders, real states and countries come next.

## Layout

```
source/     the author's .pdn, reference maps (webp), vanilla BMP palettes
scripts/    the pipeline (run_all.sh runs it all; common.py holds every setting)
dist/       what gets committed for the author: the mod zip, drawing canvases, previews
work/       intermediates, gitignored (decoded .pdn layers are 3.5 GB)
build/      the unzipped mod, gitignored
deco_ui/    the Valsora Deco UI, a separate interface mod (its own CLAUDE.md; see below)
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

`sh scripts/run_all.sh` from the repo root: about 1 minute from `HOI4 Mod Map.pdn`. Placeholder
mode (used when that file is absent) takes about 2.5 minutes, plus about 2 minutes for the
one-time decode of the original `.pdn`. Needs `numpy scipy pillow scikit-image`. Output is deterministic.

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
| `superevents_deco.py` | the superevent window in the Deco UI's style (`DECO_UI`, 2026-10-15): the mockup's board drawn with numpy and Pillow, a title strip per superevent, the texts measured against their boxes |
| `cultures.py` | generic portraits, name lists and graphical culture per continent / country |
| `ideologies.py` | the five ideologies: ideology file, renamed localisation, theocracy icon |
| `minimap.py` | the minimap (lower right): Valsora's land on parchment instead of vanilla's Earth, its frame, window and slide (2026-10-13); with the Deco UI (`DECO_UI`) gilt land and coasts on lacquer in a gilt frame, same sizes, and the start date picture the same (2026-10-14); the Vale of Reibonne start's picture, the Vale close up (2026-10-15) |
| `globe.py` | the world tension globe (top bar, 10 frames) and its small icon: Valsora instead of Earth (2026-10-14), cracking into lava as tension grows (redrawn the same day: the first flames "didn't come out too well"); run alone, `dist/tension_globe_preview.png` |
| `vanilla_parts.py` | vanilla's parts in the mod, for `build_mod.py`: the vanilla files it ships moved to 2036, the stand-ins for what Earth's content still names (decisions, events, country histories), the start and end dates, the AI's faction theaters |
| `vanilla_sync.py` | by hand, after a game update: refreshes `source/vanilla/` from the author's copy of the game (`Rouental/HOI4-Files`): the vanilla files the mod ships changed, and lists of vanilla's names |
| `pdxscript.py` | a reader for Paradox script (nested `key = value` blocks), used by `vanilla_sync.py` |
| `check_mod.py` | re-reads the built files and checks every rule below |
| `export_canvas.py` | previews in `dist/` |
| `package.py` | `dist/valsora_test.zip` |
| `country_list.py` | by hand, after a build: `dist/world_map_labelled.png` (every country labelled) and `dist/countries.md` / `.csv` (name, full name, ideology, sub-ideology, culture, leader, states), read from the built mod |
| `nation_sheet.py` | by hand, after a build: `dist/nations_by_continent.png`, every nation in the game under the continent of its capital: flag, ruler at the start (portrait of our own, or a "placeholder" box for a base-game one), full name, ideology and sub-ideology, culture, and a strip of its map colour (author, 2026-10-13) |
| `collages.py` | by hand, after a build: `dist/flags_collage.png` (every custom flag, and the countries still on a placeholder stripe) and `dist/leaders_collage.png` (every custom leader: own portraits at 2×, named ones with base-game portraits as labelled tiles); `--continent NAME` writes only `dist/flags_<name>.png`, the flags of the nations whose capital is on that continent, naming below them those with land there and their capital elsewhere (2026-10-10, Araseos; 2026-10-12, Yastreovakia) |
| `facts_export.py` | by hand, after a build: the Gazetteer's map data into `work/gazetteer/` (`index.json`, `world.png`, `n/<TAG>.json` per nation: its states, provinces, cities and politics as built, its flag, its land and the neighbours' around it as province numbers per pixel, in parts, with the rivers, and whether its states are drawn, `final`), published with the page |
| `gazetteer.html` | the Gazetteer (see below): the page where friends fill in their nations' facts; the web site's (`gazetteer_site.py`), or a claude.ai artifact with its own database (the first version) |
| `gazetteer_site.py` | the Gazetteer's web site into `work/gazetteer_site/` (the page with the Firebase project's settings, the SDK bundle from `source/gazetteer_site/`, `facts_export.py`'s map data), committed alone on the `gh-pages` branch, which GitHub Pages serves; `--emulator` builds it for Firebase's local emulators (tests) |
| `gazetteer.py` | the Gazetteer's facts into `source/gazetteer/<TAG>.json` (pictures in `source/gazetteer/assets/`): `paths KEYS.json` (each nation's atlas folder `n/<TAG>/<key>` from the owner's passwords), `pull DIR` (the atlas as the ArtifactData tool saves it, pictures fetched by asset id into `DIR/assets/`), `import FILE.json` (a file saved from the page or the site, pictures inside; drops the map facts of nations whose states aren't drawn; gives releasables their tags), `status` (releasables' cores, and what is left to do by hand), `suggestions` (`dist/gazetteer_suggestions.png`, a layer for the `.pdn`); `finals` (whose states are the author's); and the functions `read_layers.py` (terrain, rivers, cities) and `build_mod.py` (state facts, capitals, railways, supply hubs, names, sub-ideologies, rulers and party leaders with titles and portraits, map colours, releasables) call |

**A clean `check_mod.py` run is the bar for shipping a build.** It was mutation-tested
(CRLF, X-crossing, missing building row, state split across regions, descriptor
mismatch, missing localisation) and catches all of them. Since 2026-10-14 it also checks
our files against vanilla's own names (`source/vanilla/index`): sprites, technologies,
equipment, modules, battalions, ideas, defines, the map files the mod inherits, the
stand-ins for Earth's decisions and tags, every event fired (by focus, effect, event or
on_action) and 2036 (mutation-tested: 19 breaks, all caught). The checks that judge our
scripting (tags targeted, popularities, ideologies) skip vanilla's shipped files.

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
  - Real countries the author drew: Rouental ROU, Seigne SGN, Evriches EVR, Hollier
    HLR, Selgrave SGV, Lustiana LST, Lanzerac LZC, Guedelon GDN, Cardonia CRD,
    Romanoddle RMD ("the Romanoddlian Federation"), Selto STO, Placeholdros LNT (a
    placeholder nation, author; called Linterre until 2026-10-01, the key in
    `COUNTRIES` is still `linterre`), and
    (second map of 2026-09-30, all Portuguese: POR names, European portraits) Rastava
    RST, Volinovia VLN, Estande ESD (flag `source/flags/ESD.png`, map colour the flag's red (153,0,0): the
    green blended with Rouental),
    Coraliza CRZ, Placeholdria PLH (theocratic, prophetic rule), and (2026-10-01, east of
    Estande, Italian names: Claude's guess) Illiricium ILR (map name "Republican
    Illiricium", "Senatorial" until 2026-10-02; flag `ILR.png`), Côtefer CTF, Entroterra ETR, Mezzogiorno MZG (the three
    Bleacherist republics, shades of blue, Illiricium's puppets from the start) and
    Royalist Illiricium KIL (its island; white on the map so it stands out against the
    blue republics, author 2026-10-01; flag `KIL.png`, the author's original with the
    transparent gaps filled with the flag's blue; a redraw at 82:52 was rejected;
    Rouental guarantees its independence from the start, which replaced a
    non-aggression pact), and (2026-10-01, later,
    east of Selgrave and Hollier) Kurikia KRK (conservatism, flag `KRK.png`, its navy
    as map colour) and Fraxhemark FRX (social democracy, capital Fraternal City; map
    colour raspberry because its flag red would vanish next to Hollier; flag
    `FRX.png`, the author's own, 2026-10-01). Kurikia also holds the five islands to
    its north the author's Names layer labels KU (2026-10-02, four states). Kurikia's culture is Claude's
    guess from its flag (SOV names, Europe portraits, eastern European gfx); Fraxhemark is
    American (author): USA names, US generals and admirals, Europe politicians (vanilla
    has no US generic politicians), western European gfx. Locus LCF (2026-10-02; the
    Worker's Republic of Locus Felicitatis; Council Communism; 3 states around
    Fraxhemark's lake; colour, culture (American, like Fraxhemark) and the stand-in
    flag are Claude's): outlined inside Fraxhemark, so `apply_outlines` seeded it
    (`OWNERS` now wins over a re-cut patch's old country) and left the rest of
    Fraxhemark alone (`LEAVE`). The unnamed peninsula with the bay east of Fraxhemark is
    outlined but left as NSC (`LEAVE`). File names are ASCII (`Cotefer`). Formal names are the
    author's; Selto's "Empire of Seito-Hamborn" was read as Selto-Hamborn.
    The new three's colours and adjectives are Claude's picks.
    2026-10-04, south of Estande (the author's names, governments and formal names;
    colours and adjectives Claude's): San Sierra SSA (Council Communism, flag `SSA.png`,
    capital Sanhueza, with the SS islands and the archipelago its label points to),
    Anglost AGL (Constitutional Monarchy, flag `AGL.png`, with every AN island), Normania
    NRM (Constitutional Monarchy, Anglost's dominion: `autonomy_dominion`), Guardana GRD
    (Enlightened Absolutism), North Pollana NPL ("the Worker's State of Pollana", Party
    Centralism; the north tip of S. Pollana's island), South Pollana SPL (Liberalism) and
    Dremaur DRM ("the Pangolin Empire of Dremaur", Absolute Monarchy, flag `DRM.png`).
    Cultures (author): SSA GRD Spanish, NPL SPL Latin American (MEX names, vanilla's South
    American portraits, `southamerican` gfx), AGL NRM English, DRM Dutch (HOL names). The
    land between Anglost and San Sierra is undecided (author) and stays a placeholder.
    2026-10-04, later (the author's names, governments and formal names; colours Claude's):
    in Nonscio's west Wersh WRS (Revanchism, "the Republic of Wersh"), Troc TRC
    (Liberalism, flag `TRC.png`) and Cascadia CSC (Anarcho-Communism, "the United
    Forests of Cascadia", with every CS island); between Anglost and San Sierra
    Sicilianzo SCZ (Constitutional Monarchy, flag `SCZ.png`) and Danelaw DNL ("the
    Kingdom of Danelaw-Scandinavia", Elective Monarchy; Sweden's flag drawn as a stand-in
    until the author's own, 2026-10-08);
    inside Fraxhemark Thorian Dynamics THD (the author's new **Megacorporation**
    sub-ideology, flag `THD.png`). Cultures are Claude's guesses: DNL Swedish, SCZ
    Italian, CSC and THD American, WRS TRC the continent's (English). The author wrote
    "Sicilianzo" and "Danelaw" on Necessary Borders; the letters were moved to Necessary
    Names. Capitals: Kurikia Markovograd, Fraxhemark Fraternal City (dots now).
    Map colours by the author (2026-10-04, later): Wersh dark blue, Troc red, Cascadia
    dark green, Sicilianzo white (an off-white, since Royalist Illiricium is pure white).
    Kurikia also holds the island off its east coast at (1409, 925), one state (the
    author's Notes layer colours it Kurikian).
    2026-10-05, **the author's friend's two sessions**, merged from their build and
    `.pdn` (no code came with them; our scripts were given the same settings and the
    build matched theirs file for file, except image encodings): Aislada became
    **Merlovich** ("the Federation of Merlovich", Merlovian, Liberalism: `RULING`, the
    character's ideology; its leader is named "PLACEHOLDER" for now, with the author's
    portrait `source/portraits/merlovich_leader.png`; Communist Merlovich keeps the emu;
    flag `AIS.png`; state names and 17 more cities; more rivers). Its paint stays the
    placeholder green (70,170,70); `nations.DISPLAY_COLOUR` shows #2D694F in game.
    New nations: Hoalepa HOA (two islands north-west of Solitas; Constitutional
    Monarchy; "the Exteriorem Kingdom of Hoalepa"; George Tupou VII the Generous;
    capital Nuku'alofa; Australian names, commonwealth gfx) and, south of Solitas,
    Arvorenia ARV (Constitutional Monarchy, "the United Kingdom of Éden, Santo Domingo,
    and Arovia", Arovian, Portuguese, capital São Francisco), Atrocha ATR (Liberalism,
    capital Corales), the United States of Solitas USS (Liberalism, American, capital
    Tallahassee; removed 2026-10-13), Silvamar SVM (Liberalism, "the New Republic of Silvamar", Silvestran,
    capital Marcanova) and Ponchomagnifico PNC (Strongman Rule, "the Community of
    Ponchomagnifico", capital Rosas); ATR SVM PNC Spanish. Leaders' names and portraits
    are in `NAMED_LEADERS`. Their flags were taken from the build at 82×52 (the
    originals weren't sent). The friend also swapped some of the author's Merlovich
    rivers between Major and Minor (author: fine) and split two leftover placeholder
    states at Corales along the paint.
    2026-10-05, later (the author's names, governments, formal names and cultures; colours,
    adjectives and the Welsh/Irish name lists' source Claude's): Guardana renamed
    **Malvekia** (tag GRD kept); in Araseos' south-west Terrabis-Seran TBS (Social
    Democracy, "the Commonwealth of Terrabis-Seran", English, flag `TBS.png`, with the TS
    islands), Gaellia GAE (Absolute Monarchy, "the Kingdom of Gaellia", Irish),
    Kilkire-Foraois KKB (Elective Monarchy, "the High Kingdom of Kilkire-Foraois",
    Irish; the author's message said "Kilkire-Battania" at first) and
    Harwick HWK (Party Centralism, "the People's Rule Over Harwick", Welsh, Vineta's
    puppet), with Vineta VNT (Party Centralism, "the People's Rule Over Vineta", Welsh,
    flag `VNT.png`) on the VI islands off them; the Garfield Republics GFR (Fascism, "the
    United Greater Garfield Republics", Spanish, flag `GFR.png`) on the GR islands south
    of Malvekia; Devlon DVL (Agrarianism, "the Free State of Devlon", American) on the
    28 px islet its label sits on, off Fraxhemark. Thorian got the two islets labelled
    TD, Cascadia every islet labelled CS. San Sierra's border with Sicilianzo moved west
    (`pdn_tools.py border`): San Sierra took most of Sicilianzo, its state lines
    continued into it; the slivers left of Sicilianzo's old states were merged
    (`pdn_tools.py merge_small sicilianzo 400`), leaving it 3 states. The tip of
    Danelaw's eastern peninsula, cut off by a new line and labelled GR, is Garfield's
    (the "GR" was written on Necessary Borders; moved to Necessary Names).
    The bit of coast Gaellia's forked west border closes off at (596, 2222) is
    **another nation's, later** (author): it stays Araseos (`LEAVE`). Welsh (WLS) and Irish (IRE) names were added to
    `source/names/vanilla_names.txt` from vanilla. The peninsula east of Thorian is two
    **exclaves**: Terrabis-Seran's (TS, north) and Cardonia's (CA, south) (author).
    San Sierra's state lines had two gaps (a pixel at (778, 1263); a line 4 px short of
    the coast at (890, 1263–1266)), filled. **Rouental's releasables** (author,
    2026-10-05; `nations.RELEASABLE`, cores from the start, owning nothing, so they can
    be released by hand; **not** released by the civil war): the Kingdom of Carcarelle
    CRL (Carcarelle, Nerié, Hyères), the Duchy of the Mountains MTN (Everlon, Tocsin,
    Rolantelle, Rempart), the Oriflamme Alliance ORF (Oriflamme, Glacierre), the Free
    State of Ghessone GHS, the Grand Duchy of the Riverraine RVR (Leclerc, Marais
    Verte) and the Duchy of the Piscary PSC (Belleplaine-sur-Mer, Baie de Torres,
    Graisivaudan); the author's flags, French culture; governments and colours are
    Claude's (Absolute Monarchy, Feudalism, Oligarchy, Liberalism, Feudalism,
    Feudalism). Royalist Illiricium's ruler is **Beatrice di Alqiro** (`NAMED_LEADERS`,
    `source/portraits/beatrice_di_alqiro.png`). New flags for Romanoddle and South
    Pollana too. The **Holy See** SEE ("the Kingdom of the Church", Theocratic,
    Hierocracy; author, 2026-10-05; tag SEE by the author's choice, VAT at first) holds
    San Sierra's island state 1 at (896, 1184), given with `pdn_tools.py give holy_see`;
    flag `SEE.png` is the author's ("Kingdom of God" layer of the flag file; it replaced
    a stand-in Claude drew); Italian culture and the pale gold colour are Claude's.
    **2026-10-07, the big update** (the author's names, governments and formal names;
    tags, colours (from the flags where there is one), adjectives and cultures Claude's):
    Placeholdros renamed **Placeholdaire**; Placeholdria became **Vultuca** PLH
    (Constitutional Monarchy, "the United Kingdom of Vultuca", flag `PLH.png`); Volinovia
    is "the Kingdom of Volinovia" (Enlightened Absolutism). New, in Araseos' south and
    west: Merlgould MGD (the author's new **Personal Union** sub-ideology; "the Kingdom of
    Merlgould" (written "Melgould"); carved out of Vultuca; Volinovia's puppet),
    Transcainia TCN (Oligarchy), Peatiktist PTK (Strongman Rule, "the Constitutional
    Dictatorship of Peatiktist", with the PE islands and an exclave by Transcainia),
    Serentia SRN (Elective Monarchy, "the High Kingdom of Serentia", flag), Leithanien LTH
    (Populism, flag; its own state lines: 7 states; cities Rostock, Litzstädt, Thielfurt,
    Weißadel, Frundsstadt, Kaltsit, Veisheim), Ostaria OST (Absolute Monarchy, "the
    Archcounty of Ostaria", flag), Großlöwenburg GLB (Feudalism, "the Efeuüberwuchterte
    Steinsäule of Großlöwenburg", flag), the Kampfian Empire KPF (Absolute Monarchy, "the
    Iron Empire of Kampf"), Dumas DUM (Holy Order, "the Order of Saint Dumas"), Terreich
    und Preußen TUP (Social Democracy, "the Bundeskaiserreich of Terreich und Preußen",
    flag, with the TP islands and the coast patch west of Gaellia), Schteirmark STM
    (Feudalism, Terreich's puppet), Daravon DRV, Eschland ESC and Hwitland HWT (Orthodox
    Marxism; Daravon leads **the Synthesist Internationale** with the other two,
    `faction_template_synthesist_internationale`), Someriania SMR (Vanguardism; SOM is a
    vanilla tag); in Yastreovakia: Krionik KRI (the author's new **Stratocracy**
    sub-ideology, Democratic; "the Militariat State of the Kriosnika", "Regency" until
    2026-10-08; ruled by the **Kriosaivak Council of Marshals**, whose portrait is the
    author's round emblem of the council (`source/portraits/kri_council_of_marshals.png`,
    centred on a dark field); with every KR island, the two KR islets west of Araseos
    and, on its label, a region of Orientalis), Gorbastan GOB and Zukchiva ZUK
    (Liberalism), Sminishia SMN (Social Democracy, "the Worker's Republic of Sminishia"),
    Russovichia RSV (Council Communism, with the RU islands). The ES islands east of
    Terreich are **Estande's**, and the island labelled CA (Cascadia's until then) is
    **Cardonia's** (author). Cultures (Claude's guesses):
    German for the new Araseos nations, French for Dumas, Portuguese for Merlgould,
    Russian for Yastreovakia's. The borders of Sminishia, Gorbastan and Zukchiva were drawn
    on Necessary Names, and "PE" and "(TP)" were written on Necessary Borders: moved; a
    one-pixel gap south of Ostaria was closed. New flags: Illiricium's two (kingdom and
    republic) replaced. Corrections the same day (author): the land north of Peatiktist's
    exclave is **Transcainia's** (6 states; an old `LEAVE` pixel had kept it Araseos),
    and four placeholder states changed hands with `pdn_tools.py give`: Araseos 3 →
    Serentia (452, 1494), Nonscio 7 → Malvekia (1015, 1366), Nonscio 6 → San Sierra
    (1006, 1239), Nonscio 3 → Kurikia (1257, 664). Leithanien's capital is Thielfurt.
    Krionik's flag `KRI.png` was redrawn from the author's picture (the file didn't come
    through) until 2026-10-09, when their flag file's own replaced it; its map colour stays green (the flag's maroon would merge
    with Russovichia).
    2026-10-07, later: **five more Rouental releasables** (author; same rules as above):
    the Alliance of the East AOE (Chirac, Serpette, Maïeul, Moelle; Oligarchy, as when it
    was a civil-war country; the civil war still gives those states to Lustiana, Hollier
    and Selgrave), the Principality of the Recolt RCL (La Recolt, Fleurastre, Fourier),
    the Duchy of Sangterre SGT (Sangterre, Carune la Cœur), the County of Kové KOV and
    the County of Hevique HVQ (Hevique, Avarre), and the Duchy of Serie SRE (Serie, Verdoyantes;
    Feudalism; charcoal like its flag). Governments, adjectives and colours
    Claude's. The author's `New_Mod_Flags.pdn` (490×311, HOI4's 82:52 shape; layers
    "Carcaraise", "Marcher Lords", "Rouental (Authoritarian)" etc. are `import_flags`
    aliases) replaced 23 flags, including Rouental's four government flags; the
    Reibonne's and HMMLA's were copied from the new communist and authoritarian ones.
    **2026-10-08** (the author's names, governments and formal names; tags, colours,
    adjectives and cultures Claude's unless noted): in Yastreovakia's north **Belekria**
    BLK (Vanguardism, "the Union of Belekrian Republics", 44 states, with every BE island:
    five off its coast, eleven north of Nonscio, two further east), whose region
    **Tethia** is one state (named "Tethia") and a releasable, the Principality of
    Tethia TTH (Absolute Monarchy, Polish (author), flag `TTH.png`, colour from it); the
    box west of Tethia is one state too (both drawn with state lines). In Araseos' far
    south-west **Merigo** MRG (Conservatism, "the Republic of Merigo", Peatiktist's
    puppet, Italian), **Zwintern** ZWT (Technocracy, "the State of Zwintern", Dutch) and
    **Ungar** UNG ("the Grand Duchy of Ungar"; Feudalism is Claude's: the author named
    it later the same day; Hungarian, the author's, 2026-10-09, German at first); **Ostercoirasreich** OCR (Feudalism, "the
    Kaiserinnreichfedderation of Ostercoirasreich", German) on the OS islets and
    **Mahina** MAH (Liberalism, "the Republic of Mahina", Australian names like Hoalepa)
    on the MA islets. Islets also went to Someriania (SO), Kilkire-Foraois (the west of
    the SO island, cut off by a line), Kampfian Empire (KE) and Dumas (DU). The author
    wrote most of those labels on Necessary Borders: moved to Necessary Names (88 marks;
    only three new lines were real). Their upload predated the Transcainia fix and the
    four state transfers, so the current game layers were kept. New flags for Hevique,
    Riverraine, Vair and Fraxhemark came with the flag file. Later that day (author):
    Merigo renamed **Merikaan** ("the Republic of Merikaan", Merikaans; key `merigo`, tag
    MRG kept) and Dutch; Mahina **Polynesian**: vanilla has no such culture, so the name
    list `PLY` is our own (Hawaiian, Maori, Samoan, Tongan, Tahitian names) in
    `source/names/custom_names.txt`, which `cultures.py` reads alongside the vanilla
    lists; portraits are South America's generic ones (vanilla has no Pacific ones).
    Then (author) Krionik, Sminishia, Gorbastan and Zukchiva became Balkan: vanilla has
    several Balkan name lists, so each gets one (copied into `vanilla_names.txt` from
    vanilla's `00_names.txt`): Krionik Serbian SER, Sminishia Croatian CRO, Gorbastan
    Albanian ALB (the author's pick; Bulgarian first), Zukchiva Macedonian MAC.
    Then a new flag file (58 layers): 18 nations got their first flag (Belekria,
    Daravon, Dumas, Eschland, Gorbastan, Harwick, Hwitland, the Kampfian Empire (layer
    "Kampf Empire", an `import_flags` alias), Kilkire-Foraois, Malvekia, Merikaan,
    Peatiktist, Sminishia, Someriania, Transcainia, Ungar, Zukchiva, Zwintern) and
    eight were replaced (Danelaw's own for the Swedish stand-in, a new Ostaria, and
    Vineta, Romanoddle, Terreich, Großlöwenburg, Serentia and Leithanien redrawn at
    82:52). Harwick's empty top row was filled from the row below. Map colours were
    not changed to match the new flags.
    **2026-10-09** (author): the Synthesist Internationale redrawn. Hwitland is renamed
    **Scealand** (HWT and the key `hwitland` kept; "the Republik of Scealand",
    Scealändisch) and Eschland **Artzen** (ESC, key `eschland`; "the Wyrhterrepublik of
    Artzen", Artzener): the formal names follow the new names, the adjectives are
    Claude's. A new line gives Scealand Eschland's land north of it (`pdn_tools.py cede
    eschland hwitland 551,1582`: 2 states whole, the north slivers of 2 more joined one
    of them, 3 provinces split along the line): Scealand 6 states, Artzen 5. The upload
    was the author's previous file plus these edits, so its game layers predated the
    2026-10-08 changes; only their own edits were taken (the Necessary Borders and Names
    pixels where it differed from that previous file). New flags for Lustiana, Evriches,
    Lanzerac (now purple, white and gold) and Hollier. Lanzerac's map colour followed
    (author): the flag's own plum purple (145,58,106), since a bluer purple would read as
    Cardonia's a few pixels north.
    **2026-10-09, later** (the author's names, governments and formal names; tags,
    colours (Belka's from its flag), adjectives and cultures Claude's, but Volstokn's
    Finnish): Yastreovakia's north-east, now all outlined, and two islands off it.
    Belka BKA (Fascism, "the Most Serene State of Belka", flag `BKA.png`, black like its
    flag's top band; with every BK island), West Sminishia WSM (Vanguardism, "the
    Autonomous Region of Western Sminishia", Belekria's puppet; cut out of Sminishia by a
    new line: `pdn_tools.py cede sminishia w_sminishia 1919,414`), Sanada SNA (the
    author's new **Khanate** sub-ideology, "the United Sanadan Clans", with every SA
    island), Kamyachyn KMY (Liberalism), Volstokn VSK (Enlightened Absolutism, "the Tsaral
    Realm of Volstokn", with the VO islands), Brethren BRT (Synodal Rule, "the Great
    Congregation of Brethren", with the BT island), Ryśny RYS (Agrarianism, "the United
    Voivodes of Ryśny"), Pakitsk PKT (Strongman Rule), Kieska KSK (Oligarchy, "the
    Confederated Kingdoms of Kieska"), Zoluzeme ZLZ (Absolute Monarchy), Vilna VIL (the
    author's new **Radical Republicanism** sub-ideology, Democratic; "the Free Republic of
    Vilna"), Sombor SMB (Lordly Republic, "the Free City of Sombor"), Skillia SKL
    (Agrarian Socialism; its island south-east of Krionik and the SK islet) and, in
    Orientalis, Tenkyoku TKY (Prophetic Rule, "the Remnant of Tenkyoku"; the island its
    label sits on, while the peninsula beside it stays Orientalis, `LEAVE`). The islands
    labelled ES south-west of Tenkyoku are Estande's (6 states). Cultures: Russian (Belka,
    Pakitsk), Croatian (West Sminishia), Buryat (Sanada: vanilla's Mongolian list is 14
    Chinese names, and Buryat is Mongolic), Ukrainian (Kamyachyn), German (Brethren),
    Polish (Ryśny, Kieska), Latvian (Zoluzeme), Lithuanian (Vilna), Serbian (Sombor), Greek
    (Skillia), Japanese (Tenkyoku); UKR, FIN, LAT, LIT, GRE and BYA were copied into
    `vanilla_names.txt` from vanilla (its BLR list is part of SOV's, so it was not used).
    States: Sanada 84, Volstokn 61, Belka 39, Brethren 20, Kieska 13, Pakitsk 9, Ryśny 8,
    Kamyachyn 5, Skillia 4, Vilna 3, Zoluzeme 2, West Sminishia 2, Sombor 1, Tenkyoku 1
    (`dist/preview_new_nations_yastreovakia_northeast.png`). Left for the author: the ES
    on Orientalis' north coast at (4178, 793) had no line around it (it has since
    2026-10-11), and four unlabelled islets off the new coasts stay Yastreovakia's. The same day's
    flag file brought Belka's flag and redrawn Artzen and Daravon flags. Its update to
    Serie's (four gold anchors in the corners) was missed at first: `import_flags.py`
    called a flag unchanged under a mean difference of 3. With the new test, Krionik
    also got the author's own flag in place of the redraw, and Garfield, Troc and
    Terrabis-Seran the file's 82:52 copies of the same pictures (the old ones were
    490×327); Rouental keeps its 1180×700 original. See-through pixels, which show as
    holes in game, are now filled on import: Belka's emblem edge, a 1-px frame around
    Riverraine's and Belekria's flags, a faint row in Garfield's (and, by hand, the top
    row of Ponchomagnifico's, taken from the friend's build).
    2026-10-09, later still (author): **the Oriental Territories** ORT, a new Rouental
    releasable (`nations.RELEASABLE`: Concorde et Volonté, Rouental's islets off Solitas, on
    the islands north of it since 2026-10-13;
    "the Oriental Territories", the author's flag `ORT.png`; Oligarchy, French culture
    and the colour are Claude's, a shade off the flag's plum, which is Lanzerac's map
    colour exactly). The three isles and three islets the author labelled PE in the
    Midtierre, between Anglost and Normania (Nonscio's until then), are Peatiktist's: 3
    states, one per isle (`apply_outlines.py`). The flag file brought 20 first flags
    (Coraliza, Volinovia, Merlgould, Rastava, North Pollana, Gaellia, Schteirmark, Mahina,
    Russovichia, and West Sminishia, Pakitsk, Sanada, Brethren, Ryśny, Sombor, Kamyachyn,
    Kieska, Zoluzeme, Vilna, Skillia) and four redrawn ones (Estande, South Pollana,
    Dremaur, Sminishia); map colours were not changed to match. Then (author) "Araseos
    1", a 19 px islet off Terreich's coast and the Araseos placeholder's last land, went
    to Terreich, joining its nearest state (`pdn_tools.py attach terreich 935,1862`), so
    ARS is no longer in the mod; and Ungar became Hungarian (HUN names, copied into
    `vanilla_names.txt` from vanilla).
    **2026-10-11** (the author's names, governments and formal names; tags, colours,
    adjectives and cultures Claude's, but Arpino's Indian culture the author's):
    **Orientalis outlined**, all but its south-west. Gorduchai GOR (Clerical Monarchism,
    "the Holy Kingdom of Gorduchai", the island west of Orientalis), Sarkis SRK
    (Revanchism, "the People's State of Sarkis", with the SR islets), Wanea WAN
    (Agrarianism), **the Great Lake Republics** (`faction_template_great_lake_republics`):
    Qingou QNG (Liberalism, "the Qingou Republics", its leader; **Qinguo**, "the Qinguo
    Republics", since 2026-10-13), Xuè XUE (Conservatism;
    the accent is the author's), Hulinguo HLG (Populism, "the Hulinguo Republic"), the
    Associated Cities ASC ("the Associated Cities of Dahu and Jinhu", Liberalism) and
    Haidao HDO ("the Associated City of Haidao", Liberalism); Kuran KRN (Vanguardism, "the
    Red Mountains of Kuran"), Red Path RDP (Vanguardism, "the People's Republic of
    Kianhua", the three RP patches), Kianhua KNH (Liberalism, "the United States of
    Kianhua"; "Kainhua" in the author's message was a typo), Charity CRT (Absolute
    Monarchy, "the Empire of Charitia", with the AC islands and the peninsula beside
    Tenkyoku, which was in `LEAVE`), Kaizan KZN (Personal Union, Charity's puppet), Sho
    SHO (Oligarchy, "the Kingdom of the Sho Dynasty"), Uyizar UYZ and Yatar YTR
    (Khanate), Myehn MYH (Conservatism, "the Imperial Republic of Myehn"; with the 49
    islands the author circled in red east of it, and an exclave on Plaija's west tip
    its label sits on), Tsuruma TSU (Lordly Republic, "the Most Serene Republic of
    Tsuruma", with the TS islands; the one far south of Arpino is Terrabis-Seran's since
    2026-10-12: TS is its code too), Daihai DHI
    (Feudalism, "the Island Principalities of Daihai", the DI islets), Plaija PLJ
    (Orthodox Marxism), Pinzahao PZH (Radical Republicanism, "the Liberated Peoples of
    Pinzahao"), Ganden GND (Fascism) and Arpino ARP (Enlightened Absolutism, "the United
    Empire of Arpino", with the AR islands). Three bits of other countries: TP in
    Kianhua (Terreich's), KR at the tip of Arpino's south (Krionik's) and the ES cape on
    the north coast (Estande's, now outlined). Then (author) **Shinnokawa** SHN ("the
    Empire of Shinnokawa", Absolute Monarchy): the six SH islets east of the circle, one
    state. The unlabelled land (the south-west's big island and peninsula, the islands
    between Krionik's and Plaija, about 125,000 px) stays Orientalis for now: the author
    will fill it later. Cultures: our own Chinese list `CHN` (family name first;
    vanilla's is family names only) for QNG XUE HLG ASC HDO KRN RDP KNH CRT DHI PZH;
    Japanese for TSU KZN SHO SHN (Sho after Ryukyu's Shō dynasty), Korean WAN, Buryat GOR (a
    lamaist Mongol monarchy, like the Bogd Khanate), Armenian SRK, Uzbek UYZ, Kazakh YTR,
    Burmese MYH, our own Vietnamese `VNM` for PLJ (family name first too), our own
    Tibetan `TBT` for GND, and Indian ARP (vanilla's Raj names and portraits, commonwealth
    gfx); KOR ARM UZB KAZ BRM RAJ were copied into `vanilla_names.txt` from vanilla, and
    its Buryat list's one name in curly quotes was given straight ones (Gorduchai's
    leader showed them). The members of the Great Lake Republics and of
    the Synthesist Internationale start with 40 % for their (and their leader's) ideology
    (`nations.POPULARITIES`), a precaution after Lanzerac and Guedelon. States: Sarkis 198,
    Arpino 109, Plaija 65, Myehn 63, Charity 56, Kianhua 53, Qingou 24, Uyizar 16, Sho 13,
    Xuè 12, Yatar 7, Gorduchai, Ganden, Pinzahao, Red Path and Tsuruma 6 each, Wanea 5,
    Kaizan 4, Hulinguo 3, Kuran 2, the Associated Cities, Haidao, Daihai and Shinnokawa 1
    each, and one each for Terreich, Krionik and Estande: 667 in all
    (`dist/preview_new_nations_orientalis.png`). Wanea's line carves a tongue of land
    south-east of it out to Sarkis, as drawn. The upload predated Araseos 1's move to
    Terreich, so `pdn_tools.py attach` was run again.
    **2026-10-12** (the author's names, governments and formal names; tags, colours,
    adjectives and cultures Claude's): **Usnistan outlined**, Orientalis' south-west and
    Sennheiser. In Usnistan: the Cultists CUL (Prophetic Rule, "the Cult of the Great
    Cthulu", the CU archipelago), Arcadia ARC (Conservatism, Terreich's puppet), Muqadasa
    Salamat MQS (the author's new **Divine Republicanism**, Theocratic; "the Holy
    Republic of Muqadasa Salamat"), Sarza SRZ (Absolute Monarchy, "the Empire of Sarza"),
    Leviathan LEV (Populism), Kyras KYS (Liberalism, "the Commonwealth of Kyras", with the
    RA islands and a coastal exclave by Almohavid), Hulya HLY (Conservatism, "the
    Territory of Hulya", a 148 px box), Levantinin LVN (Holy Order, "the Crusader State of
    Levantinin"), Mustawi MST (Strongman Rule), Almohavid AMH (Constitutional Monarchy),
    Port Almohavid PAM (Lordly Republic, "the Free Port of Almohavid": the 16 px tip of
    land a short line closes off), Mekele MKL (Anarcho-Communism, "the Mekele Peoples'
    State"), Kalaistan KLS (Military Junta), Al-Radiyaa RDY (Conservatism), Al-Khabid KHB
    (Oligarchy), the Humanist State HMN (the author's new **Humanism**, Authoritarian: "an
    apartheid-style ideology placing humans as superior beings to the other races of
    Valsora"), South Usnistan SUS (Conservatism), Royabad RYB and Koronista KRS (Absolute
    Monarchy, sultanates), North Koronista NKR (Strongman Rule; "North Kornista" on the
    map), Zanzimibia ZNZ (Social Democracy), the Utopian Republic UTP (Lordly Republic,
    "the Second Utopian Republic"), Soloriania SLN (Liberalism, "the Solorianois
    Confederacy"), Hohenzburg HZB (Strongman Rule, the Kampfian Empire's puppet), Nuevo
    Paraíso NPR (Conservatism, the United States of Solitas' dominion), Arklen ARK
    (Conservatism, "the Arklen Free State", a non-aggression pact with Ostaria), Isigoriya
    ISG (Military Junta), Kizimwe KZW (Synodal Rule, "the Kizimwe Conference of Bishops"),
    Lafari LFR (Council Communism, "the Worker's Republic of the Lafari"), Meddacah MDC
    (Fascism, "the Meddacah River Autonomous Zone"), Khaleeya KHY (Feudalism) and Solaria
    SLA (Hierocracy, "the Holy State of Solaria": on the map but not in the author's
    list; named when asked); in Orientalis' south-west Chineasia CNA (Vanguardism, "the
    People's Republic of Chineasia", with the CH islands as far as Krionik's island; led
    by the author's **Han Leji**, `source/portraits/han_leji.png`; flag `CNA.png`) and
    Felter FLT (Liberalism, with the FE islands); Sennheiser SNH (Constitutional Monarchy,
    "the Sennheiser Union", labelled AK) in Yastreovakia's south-west, a `LEAVE` patch
    until then. The author's "direct colonies": islets and bits of coast labelled US (the
    United States of Solitas, 3 states), KR (Krionik, 3), KE (the Kampfian Empire, 1), SR
    (Sarkis, 2) and KF (Kilkire-Foraois, Claude's reading, 1 islet); the islet the author
    circled near Myehn's red circle joined Myehn's nearest state (`pdn_tools.py attach`).
    Cultures: the continent's Persian for Kyras (Kyros is Cyrus), Sarza, Royabad,
    Kalaistan, South Usnistan, the Cultists and the Humanist State; Arabic for Muqadasa
    Salamat, Al-Khabid and Khaleeya (SAU names) and Mustawi, Al-Radiyaa and Meddacah
    (KUW), Moroccan for both Almohavids, Turkish for Hulya and both Koronistas, Ethiopian
    for Mekele and Lafari, Eritrean for Kizimwe, Nigerian for Zanzimibia, Ghanaian for
    Isigoriya (with the `arabia` and `africa` portraits, the two halves of the continent's
    mixed set), Greek for Arcadia, English for Leviathan and the Utopian Republic (Hobbes,
    More), French for Levantinin and Soloriania, German for Hohenzburg and Sennheiser,
    Dutch for Arklen (the Orange Free State) and Felter, Latin American for Nuevo
    Paraíso, Italian for Solaria, Chinese for Chineasia. SAU KUW MOR TUR ETH ERI NGA GAH
    were copied into `vanilla_names.txt` from vanilla; their heads of state and a few
    other famous names are in `NOT_SURNAMES` (none of them was in a list already in use,
    so no older leader changed). States: Chineasia 73, the Utopian Republic 68, Kyras and
    Sarza 33 each, Royabad 31, Felter and Lafari 29 each, the Humanist State 23,
    Sennheiser 22, the Cultists 21, Muqadasa Salamat and South Usnistan 19 each, North
    Koronista 18, Arcadia 17, Levantinin 12, Mustawi 11, Almohavid and Zanzimibia 9 each,
    Al-Khabid, Hohenzburg and Nuevo Paraíso 8 each, Al-Radiyaa 6, Soloriania 4,
    Isigoriya, Kalaistan, Kizimwe, Koronista, Meddacah and Solaria 3 each, Arklen, Hulya,
    Khaleeya, Leviathan, Mekele and Port Almohavid 1 each: 545 with the colonies'
    (`dist/preview_new_nations_usnistan.png`, `..._orientalis_southwest.png`,
    `..._sennheiser.png`). Left as placeholders: about 1,700 px of Usnistan islets (most
    of it the three islands south of it), 300 px of islets off Orientalis and 350 px in
    Yastreovakia. The CU and RA labels were drawn on Necessary Borders: moved to
    Necessary Names. Then (author) ten placeholder states changed hands, named as the game
    showed them: Nonscio 1 (2,696 px, the island group south of the BE islets) to
    Belekria, Orientalis 4 to Ostercoirasreich, Tsuruma 6 (the TS island far south of
    Arpino) to Terrabis-Seran, Yastreovakia 1 to Sarkis and Yastreovakia 3 to Volstokn,
    as states of their own (`pdn_tools.py give`); the islets Usnistan 2, Nonscio 2,
    Orientalis 3, Yastreovakia 2 and 4 (17-52 px, beside the Cultists', Cascadia's,
    Charity's, Volstokn's and Sennheiser's land) joined their new owner's nearest state
    (`attach`). Nonscio and Yastreovakia own nothing now. Left as placeholders: Usnistan
    1-4 (islets beside Kyras and the Utopian Republic, and the islands south of South
    Usnistan; the old Usnistan 3-5, renumbered), Orientalis 1-2 (beside Kianhua and Daihai)
    and Solitas 1-20, the land between the friend's nations. Flags for Sennheiser and
    Volstokn came the same day (`SNH.png`, `VSK.png`; map colours unchanged).
    **2026-10-13** (the author's names, governments, formal names and rulers; tags,
    adjectives, cultures and colours (from the flags where there is one) Claude's):
    **Solitas outlined.** The upload was the 4a191cb map (after Usnistan, before the ten
    transfers and the province merge) plus the author's edits, so only those were taken:
    Necessary Borders, Names and Cities (Tallahassee's dot removed), Even More Reference
    and a new layer, **Islands to Add**. **The United States of Solitas is removed**
    ("eventually it will be readded as a formable": it stays in `COUNTRIES`, owning
    nothing, so it is left out of the mod); its colonies, relabelled AN (six pieces, three
    states), are Anglost's (`pdn_tools.py give`), and **Nuevo Paraíso is New Paradise**
    ("the Dominion of New Paradise", now Anglost's dominion and English; key
    `nuevo_paraiso` kept). Its land on Solitas was repainted as the placeholder's before
    `apply_outlines.py`, so the new nations were cut afresh. New: Recaxa REC (Agrarianism,
    "the Republic of Recaxa", Diana Zorreguieta, flag), Surredia SRD (Strongman Rule, "the
    Republic of Surredia", Sunny Hurricane, flag), Arovannea AVN (Conservatism, "the
    Confederative Republics of Arovannea", Estúr Illger fön Reegen; code CI, so many
    pieces), Avesária AVE (the author's new **Semi-Constitutional Monarchy**, "the
    Avesária Dimokratía", Nikosanis Coisan II; "Aversaria" in the author's message, the
    map says Avesária), Abalón ABL (Absolute Monarchy, "the Kingdom of Abalón"), Texaria
    TEX (Liberalism, "the Republic of Texaria", Iyun' Savon, flag), Gran Yucanoa GYC
    (Liberalism, "the Federation of Gran Yucanoa", ruled by the General Cortes, its
    parliament, flag), Las Anod LAN (Conservatism, "the United Isle of Las Anod", Michael
    Ryan) and Bromé BRO (Party Centralism, "the Republic of Bromé", Jose Castañeda); the
    AV patches are Arvorenia's. **Santa Fe**, labelled but not in the author's list, stayed
    the placeholder (`LEAVE`) until that evening. Cultures: Latin American for Recaxa, Gran Yucanoa and Bromé,
    American Surredia, German Arovannea, Greek Avesária, Spanish Abalón, Russian Texaria
    (Iyun' is June), Irish Las Anod. States: Arovannea 26, Surredia 19, Recaxa 16, Gran
    Yucanoa 13, Avesária 6, Abalón 5, Texaria 5, Las Anod 5, Arvorenia 2, Bromé 1
    (`dist/preview_new_nations_solitas.png`). Fixes on the way: Texaria's eastern line
    stopped 8 px short of the inlet south of it (closed), a "CI" was written on Necessary
    Borders (moved to Names), and five slivers of a small loop of line by Abalón's coast
    are Abalón's. **Rouental's eastern territories moved** (author, "to better align with
    the lore"): the two islands painted on Islands to Add (27 and 45 px, north of
    Arovannea) are land now (`pdn_tools.py add_land rouental`), one state named Concorde et
    Volonté, so the Oriental Territories' cores follow; the old islets off Solitas' south
    are Solitas' again, and their ROU label moved to the islands. The four flags were
    fitted to 82:52 without stretching (scaled evenly, then plain field added inside the
    stripes, or Surredia's plain sides trimmed; `dist/flags_new_20261013.png`), and added
    to the author's flag file as layers (`source/New_Mod_Flags.pdn`, now kept in the repo;
    `writepdn.py` adds layers on top).
    **2026-10-13, later** (the author's names, governments and transfers; tag, colours,
    adjective and culture Claude's): **Santa Fe** SFE ("the Fifth Republic of Santa Fe",
    Party Centralism, Latin American, gold to stand out from Bromé's crimson and
    Atrocha's red; its patch, "Solitas 3" and "4" in game, cut by `apply_outlines.py` into
    7 states like its neighbours); **Bromé** is "the Grand Duchy of Bromé", a
    Semi-Constitutional Monarchy (Party Centralism until then; Jose Castañeda still rules,
    the author named no other); **Silvamar**'s map colour is its flag's navy, a little
    lighter (10, 30, 140): its green was too close to Arvorenia's and Las Anod's. The
    placeholder states the author named in game went to their neighbours: Solitas 1 (298
    px) to Hoalepa and Usnistan 3 and 4 (214 and 1,432 px) to Royabad as states of their
    own (`pdn_tools.py give`); Solitas 5 (the two old Rouental islets, 90 px) to Atrocha,
    Orientalis 1 and 2 (38 and 95 px) to Kianhua and Daihai, and Usnistan 1 and 2 (31 and
    17 px) to Kyras and the Utopian Republic, each joining its new owner's nearest state
    (`attach`). Orientalis and Usnistan own nothing now. The last placeholder land,
    Solitas 2, a 16 px islet off Recaxa's west coast at (1443, 1832), joined Recaxa's
    nearest state afterwards (author), so Solitas is left out too
    (`dist/preview_new_nations_solitas.png`). Then (author) **Qingou is renamed Qinguo**
    (tag QNG and key `qingou` kept); five first flags, for Qinguo, Kianhua, Tsuruma, Myehn
    and Ganden (fitted to 82:52 as below, and added to the flag file); Tsuruma's ruler is
    **Akihiro Tanaka** and its capital **Kishito**, Myehn's capital **Shukumei**
    (`CITY_NAMES`). Map colours were not changed to match the new flags.
    **2026-10-14**: Cardonia's first flag (the author's: black, white and navy bands, an
    owl on a compass star), fitted to 82:52 by trimming 9 px of plain band at each side
    and added to the flag file (`dist/flag_cardonia_20261014.png`); its map colour stays
    deep purple.
    **2026-10-15** (author): **Vilna moved** to Russovichia's land (its 2 states, with the RU islands), taking
    its paint (140, 0, 0), dark red like Vilna's new flag (the author's: a crimson field framed by blue bars and
    Stars of David, a menorah over a sword, a line in Hebrew), which came at 1280 × 841 and was fitted to 82:52
    by lengthening the top and bottom bars 23 px at each end (`dist/flag_vilna_20261015.png`; in the flag file
    as "Vilna", the old layer renamed "Placeholdgrad"). It keeps its formal name; then (author, the same day) it
    is **Conservatism** (Radical Republicanism until then) and **Jewish**: the base game has no Jewish culture, so
    its nearest, the Israeli name list (ISR, copied into `vanilla_names.txt`; it has some Arab-Israeli surnames),
    with Europe portraits and eastern European gfx (Lithuanian until then). **Russovichia stays in `COUNTRIES`,
    off the map** (author: "should remain in the code,
    but be off the map for now"): it owns nothing, so it is left out of the mod like the United States of
    Solitas, with an unused colour from its flag, (153, 47, 45). Vilna's old land (3 states) is
    **Placeholdgrad** PHG, with Vilna's old flag (`PHG.png`) and Radical Republicanism, and Vilna's old green;
    the adjective Placeholdgradian, Russian culture (for the "-grad") and no formal name yet are Claude's.
    Since the paint moved with the names, the `.pdn` is unchanged.
    All tags were checked against vanilla `common/country_tags`; new tags must be too.
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
  box (a box too short drops lines silently). Not yet seen in game.
- **Current set.** Seven superevents: one per Rouental leadership focus (five), the
  Rouentaise civil war (Execute the Prince; the author's soldier photo) and AIS
  "Fucking Explode". The quotes are Claude-written except the civil war's (the
  author's); all but the civil war use the author's anime picture and Entry of the
  Gladiators. The civil war has Rafael Krux's "Epic Church Organ" (`valsora_organ`,
  `epic_church_organ.ogg`, made with the ffmpeg bundled in the `imageio_ffmpeg` Python
  package: first 45 s, 4 s fade, Vorbis 160k); it replaced "Monsieur d'Elbée", which
  the author didn't like.
- **Checks.** `check_mod.py` checks scripted effects and events that are used, songs
  and their files, scripted localisation keys, and GUI window, element, sprite and
  button-text references (mutation-tested).
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

## The Gazetteer (`docs/GAZETTEER.md`)

The author's request (2026-10-14): a tool their friends open by a link to fill in their own
nations once the states are drawn, instead of the `.pdn` ("tedious and hard to keep track of,
especially with cities"). **Since 2026-10-15 it is a web site,
https://rouental.github.io/Valsora-HOI4/**: GitHub Pages serves the `gh-pages` branch, which
holds only the site (the author allowed that branch for it: "it's ok to put it on a new
branch"; pushing it switched Pages on), and the atlas is the Firestore database of the
author's Firebase project `valsora-hoi4` (free Spark plan). Players need no account; only the
author signs in, with Google. It moved because on claude.ai only friends invited by email as
Editors can save (a public link's visitors can only view), and the author didn't want to ask
everyone for an email. The first home, the claude.ai artifact
**https://claude.ai/artifact/PqTTD5FuFJhpL4JKp8sumN** (`scripts/gazetteer.html` published with
`work/gazetteer/`, declaring `db` (rule: `planned` written by the owner only), `user`
(profile), `downloads` and `assets`), still works with an atlas of its own, but is no longer
used. One page serves both: `FIREBASE` is null on claude.ai and filled in by
`gazetteer_site.py` for the site.
- **Republish the site** after map changes (the facts are kept by map pixel):
  `python3 scripts/facts_export.py`, `python3 scripts/gazetteer_site.py`, then commit
  `work/gazetteer_site/` alone as the next commit of `gh-pages` and push it:
  `git fetch origin gh-pages && git worktree add work/gh-pages origin/gh-pages`; in
  `work/gh-pages`: `git rm -rq . && cp -r ../gazetteer_site/. . && git add -A && git commit`
  and `git push origin HEAD:gh-pages`; then `git worktree remove work/gh-pages`. Pages
  redeploys in a minute or two (the "pages build and deployment" run in Actions; github.io
  itself can't be reached from Claude's sandbox).
- **Firebase** (set up by the author, 2026-10-15): Firestore (Standard, production mode), Google
  sign-in with `rouental.github.io` among the authorized domains, the web app's settings in
  `source/gazetteer_site/firebase-config.json` (not secret). The rules,
  `source/gazetteer_site/firestore.rules`, are pasted in the console by the author with their
  Google address for `OWNER_EMAIL`, which is never committed: change the file, then ask them to
  paste it again (they changed on 2026-10-15, later: admins, `releasables`). They allow `get`
  and `list` inside a nation's folder but nothing on `n` and no `{path=**}` match, so neither
  `n`, a nation's folders nor a collection-group query can be listed; writes need the folder's
  `key` document (only admins write those) and a known kind; `owner/*` is the admins' alone;
  `planned/*` is read by all, written by admins; `admins/<address>` is read by admins and
  written by the author alone (`isAdmin()` = the author's address, or an `admins` document
  under the signed-in address). Cloud
  Storage needs the paid plan, so pictures are documents beside the facts (`img-<id>`: a data
  URL of at most 640 px, JPEG over 400 kB; the rules cap them at 800,000 characters).
  Firestore keeps no array directly inside an array: lines' points are stored as
  `{"_a": [x, y]}`. The SDK is Google's, bundled into one module
  (`source/gazetteer_site/README.md`).
- **Map tools wait for a nation's states** (author, 2026-10-15: "if a nation's states have not
  yet been defined, they would be able to make suggestions for me to make their state borders,
  and do things like provide flags, leaders, full nation names, etc. Then once their state
  borders have been set in the mod, full customization would be unlocked"). `gazetteer.finals`
  marks a nation final when no two of its states share an area the Necessary Borders and
  Necessary States lines enclose (the states `apply_outlines.py` cuts from an area left without
  lines do); one-piece nations count (Claude's suggestion, accepted). 39 of 161 on 2026-10-15,
  later: AIS CRD KRK LNT LTH ROU SSA STO and 31 of one piece (Placeholdaire and San Sierra each had
  an island without lines in two states, from the placeholder grid and the old 650 px rule:
  merged with `pdn_tools.py attach`, author: "Placeholdaire has all its provinces defined, yet is
  not editable"); Belekria is partly drawn, 121 not at all. Until then the page shows the plain
  land (no cut states), only Map, Politics, People, Releasables and Nation and the Select,
  Releasables (areas) and Suggest tools;
  `planned/unlock` ({TAG: true | false}, Owner tools › Map tools, or the nation's Map tab)
  overrides the rule. The import drops a closed nation's states, provinces, cities, rivers,
  railways and releasables' states (the file of every nation carries `unlock`).
- **Drawn states** (author, 2026-10-15: "when drawing states they should snap to the borders of
  the nation and the borders of other states so that they fit together well and don't
  overlap"): Suggest › State (the default on a closed nation) keeps the nation's own land inside
  the line that no state drawn before it holds (suggestion ids begin with the time), filled
  pixel by pixel in the land's picture (`sugFill`), so a player draws past the coast and the
  borders. **Make it a state** turns an area into one. `gazetteer.py suggestions` clips them the
  same way for the `.pdn` layer.
- **Releasables** (author, 2026-10-15: "allow people to select provinces that could be
  releasables, and then the ability to define flags, names, etc."). The `releasables` document:
  `{rl-<id>: {name, adj, def, ruling, colour, flag, leader {name, desc, portrait}, notes,
  states {"x,y": true}, areas {a-<id>: points}, added}}`; whole states (2026-10-15, later; the
  author asked whether provinces would work in game: HOI4 cores states, for releasables and
  formables alike), a state belongs to one releasable; areas while the map tools are closed.
  The first ones held `provinces {"x,y": true}`: the page and the build read those as the
  states they cover by half, and the page saves them as states once their land changes. The import gives each a tag (`new_tag`: its
  name's letters, never `COUNTRIES`', the base game's (LIB is Liberia's), a planned nation's or
  another releasable's), kept by id. The build (`gazetteer.releasables`) makes each a country
  owning nothing (in `COUNTRIES` as `gazetteer_<tag>` for that build only), with cores on the
  states it holds (whole, or at least half of by provinces and areas, in pixels; the largest is its capital;
  less than half is a note, none at all leaves it out), its names, ruler and colour as facts of
  its tag, its nation's culture, and its nation's ruling sub-ideology when it has none. Its flag
  goes to `source/flags/<tag>.png` at the import like a nation's.
- **Admins** (author, 2026-10-15: "How would I go about making Merlo an admin on the Gazetteer
  as well, so he can manage passwords and such"): Owner tools › Admins (the author adds or
  removes a Google address: `admins/<address>`); an admin signs in with Google and gets every
  owner tool but that list. The page tells the author from an admin by the list (the author
  isn't on it).
- **Merlo's handoff** (author, 2026-10-15: "a handoff file for Merlo, so that his instance of
  Claude generates in line with this one"): `docs/HANDOFF_MERLO.md`, how to work from this
  repository, recipes, conventions and how to hand work back. Keep it in step.
- **Version 2** (author, 2026-10-14, latest: "each nation should be locked behind a password I
  can give them so that people can't make troll edits on each others' nations ... submit
  flags, leaders, etc ... a function for them to make suggestions ... overseas territory ...
  displayed in a separate box to their mainland"). The first version's only data was the
  author's own test edit (one Lanzerac province set to forest, `facts/LZC-provinces` and
  `nations/LZC`); version 2 doesn't read those collections.
- **What it edits**, per nation: state names, population, kind of state, buildings (within
  slots and vanilla's caps), resources, notes; province terrain (8 types) and supply hubs;
  cities (one per province, victory points, the capital); rivers (major, minor, erase strokes);
  railways (level 1-5); names, full titles and adjectives under every government and each
  ideology, the ruling sub-ideology; the head of state (name, titles, portrait), each other
  party's sub-ideology, leader and portrait, generals, admirals and advisors; flags (one per
  government too); map colour, culture, motto, anthem, description; suggestions (areas, lines
  and points anywhere on the world, labelled); status, notes and requests (new sub-ideologies,
  subject types, map changes ...). Overseas parts of a nation and the whole world are boxes in
  the map's corner. Phone and desktop layouts (the author asked for both).
- **Passwords.** A nation's documents are at `n/<TAG>/<key>/<kind>`, the key being the first
  32 hex digits of SHA-256("valsora-gazetteer|TAG|" + the password lowercased, runs of spaces,
  dots, commas and underscores as one hyphen). The store lists a collection's own documents
  only, so `n` lists nothing, even to the owner (tested on the live atlas): without the
  password a nation can be neither found nor changed. `n/<TAG>/<key>/key` marks a real
  password; `meta` (status, notes, `editors` ids) and `req-<id>` requests sit beside the
  facts. The owner's passwords are at `data/users/<owner id>/keys` (private to them), made and
  changed in **Owner tools** (a new password copies the documents and deletes the old ones),
  and the page unlocks every nation for the owner. On the site the passwords are at
  `owner/keys`, the owner is whoever may read it (the rules decide), and a player is a random id
  per browser (`gazetteer-id`) with the name they give on the Nation tab (`meta.editors` keeps
  names on the site, ids on claude.ai). On claude.ai friends had to be invited by email as
  Editors, with no public link (outside viewers can't write), and an Editor could publish a new
  page version; pictures there are the artifact's uploaded assets, stored by id (shown as
  `/_blob/<id>`).
- **Nations not on the map yet**: `planned/list` ({TAG: name, continent}), owner-written; base
  game tags (`index.json` `earth`) are refused. Their page has Politics, People, Map
  (suggestions on the world map) and Nation; their facts carry over once they are drawn.
- **To pull it** from the site: the author's **Save every nation as a file**
  (`valsora-gazetteer-all.json`, each nation's pictures inside as `images`), then
  `python3 scripts/gazetteer.py import` it (Claude can't sign in to the author's Firebase).
  Then rebuild (and `river_provinces.py` after new rivers), run `gazetteer.py suggestions` if
  there are any, and tell the author the open requests and what `status` lists for doing by
  hand. From the claude.ai atlas (the first version): ArtifactData `get` of `data/users/me` / `keys` and of `planned` / `list`,
  both with `out_dir` `work/gazetteer_pull` (never commit the passwords: `work/` is ignored);
  `python3 scripts/gazetteer.py paths work/gazetteer_pull/data/users/<id>/keys.json` names each
  nation's folder; ArtifactData `list` of each with the same `out_dir`; then
  `python3 scripts/gazetteer.py pull work/gazetteer_pull`. It lists the pictures to download:
  the Artifact tool's `read` with `path` = the asset id and `out_dir`
  `work/gazetteer_pull/assets`, then `pull` again.
- **In the build** (`source/gazetteer/<TAG>.json`; Rouental's since 2026-10-15, below): a nation's facts
  win over the `.pdn` and `nations.py` for that nation: its cities replace the Cities layer's dots on its land
  (`regions.json` cities then carry victory points, the capital flag and the state-capital flag), its state names
  replace `state_names.json`'s (the old names still resolve for `nations.CIVIL_WAR` /
  `RELEASABLE`), its capital city replaces `nations.CAPITALS`, each state's main city (its first
  victory point, its supply hub unless the nation placed hubs, where its divisions start) is the
  national capital, else the city marked its state's capital, else the most victory points (the
  northernmost on a tie; the Cities layer's own dots keep their order), its hubs replace the one per
  state (plus its capital), its colour `nations.DISPLAY_COLOUR`. Railways take the shortest
  way over land between the provinces under their points, centre to centre (the page draws
  the same route); shared stretches are written once at the higher level. Rulers and party
  leaders get their names, titles (`desc` after the ideology) and portraits (registered in
  `nations.PORTRAITS` as `<TAG>_gazetteer_<role>`, 156:210 from the top of the picture).
  Hand-made rulers (`HAND_MADE`) keep their leaders. A flag in HOI4's 82:52 shape (within 4 %)
  becomes `source/flags/` at the import, once per picture (`source/gazetteer/installed.json`);
  others are fitted by hand, as the author's are. Pictures are kept at most 1,200 px, heavy
  opaque ones as JPEG. Without facts the build is byte-identical to before (checked again for
  version 2). `check_mod.py` checks railways (adjacent, in states, level 1-5), building caps and
  slots, resources and manpower (mutation-tested, 7 of 7). `GAZETTEER_DIR` and
  `GAZETTEER_FLAGS` point the scripts at other folders (tests).
- **Tests** (Playwright, with a stand-in for claude.ai's runtime that keeps its rules: path
  grammar, private `data/users`, the owner-only `planned`, queries, `/_blob/` pictures): the
  owner makes passwords, adds a nation not on the map, fills in Rouental's mainland and
  islands, Seigne's people and the planned nation's suggestions, changes a password; a
  friend in another browser is locked out until the password (typed loosely) opens it, an old
  password no longer does; desktop and phone, light and dark; the view-only and offline modes.
  On the site too: releasables picked by province on Rouental and drawn as areas on Hollier
  (closed), Hollier's map tools opened and closed again, the author adding Merlo as an admin,
  Merlo making a password but refused when adding an admin; the import closing Hollier's map
  facts, opened by the switch; a build with three releasables (check_mod clean; cores, capital,
  names, ruler), and without facts byte-identical.
  The site is tested the same way against Firebase's own emulators (firebase-tools 15, Java 21;
  `gazetteer_site.py --emulator 127.0.0.1:8080:9099 --project demo-...`, the rules loaded with a
  test owner), plus the rules attacked straight over REST (listing `n`, a nation's folders or
  every `states` document, reading `owner/keys`, writing `planned`, making, replacing or
  deleting a `key`, writing without a password or an unknown document: all refused; writing
  with the password allowed) and another Google account getting no owner tools. Tests sign in
  with the emulator's unsigned tokens (`window.__fb`, only in an emulator build): Google's
  sign-in window can't load in the sandbox. A file saved from the site imports with its
  pictures.

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
  Valsora. `validate_preview.py` must end with `PROBLEMS: none`. Rendering noise: restore textures that only
  changed by a few anti-aliased pixels (`git checkout`).
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

## Atlas submod (removed)

A "Valsora: Atlas" graphics submod (2026-10-07, `scripts/atlas_mod.py`, in git history,
last at commit 8a03ebf) tried to make the map look like a printed atlas with our own
textures: paper colour maps, engraved waterlines, sea lettering, compass rose and
cartouche, paper terrain tiles, ink border strips, a Cinzel map font (OFL), defines.
**Removed at the author's request after two in-game tests** ("maybe we'll come back to
it later"). What the tests taught (see `docs/PROBLEM_LOG.md`):
- Zoomed out, HOI4 draws a flat, shader-drawn map that no texture reaches; the look
  needs shader changes, which need the author's vanilla `gfx/FX` files.
- A flattened heightmap (a cliff at every coast) is drawn as stair steps and squares;
  `GRADIENT_BORDERS_FIELD/THICKNESS_COUNTRY_*` overrides draw a coarse grid.
- Country names didn't show with the replacement map font; the cause was never found.
It replaced the 2026-10-06 **Victorianization patch** (`victorianization_patch.py`,
graph-paper colour maps for Victorianization at Valsora's size; also in git history).

## Cartographic submod (removed)

A flat, HOI3-style "Valsora: Cartographic Map" submod was tried on 2026-10-01 and
removed at the author's request ("it wasn't great"); they may come back to it. It is
in git history (commit d2d6cd8, `scripts/cartographic.py`). It used
`GRADIENT_BORDERS_THICKNESS_COUNTRY_LOW/HIGH` = 2000 for solid country fill, a flat
`world_normal.bmp`, a khaki land colormap and a grey-blue sea with a 15° graticule.

## Current state

- 2026-10-15, latest: **Vilna moved** to Russovichia's land with the author's new flag, now Conservative and Jewish
  (the base game's Israeli names), **Placeholdgrad** on its old land with its old flag and government, Russovichia
  off the map (still 183 countries). The Deco UI is v0.6: the
  **focus tree after the mockup** (notched under the
  band, the country's title and sub-ideology in the header, medallions and plates per focus state, a gilt halo on
  the focus in progress, gilt links, red exclusive marks, the scale-pattern canvas; the focus icons are the game's,
  as the author asked) and v0.5.2's fix: closed side panels stayed on screen (the author's screenshot), so they rest
  off-screen again and open at once; the menu's career profile star moved off its label. The **superevent window**
  follows the mockup (`superevents_deco.py`). **Two starts** (Valsora: Rouental and Merlovich recommended; the Vale
  of Reibonne: the Association), so Back on the country screen returns to the scenario screen instead of looping.
  `on_startup` called the Reibonnaise opinions effect without a scope (the one line of the author's 10-line
  error.log that was ours, down from 2,081): it runs in a country scope now, and `check_mod.py` checks for it.
  Not yet seen in game.
- 2026-10-15, last: **Rouental's Gazetteer page is in the build** (`source/gazetteer/ROU.json`, read from
  the site with its password, which the author gave; the author removed its test hub and made Rêverie the
  capital again first): population 42.3 million over its 56 states, terrain for 132 provinces, 15 cities
  (Vair 20 VP, Rêverie and Carcarelle 15, eight new ones), one minor river along the Hollier border, a
  level 2 railway Rêverie–Seraine, the state kinds of Rouental (large city) and Saintiers (city), an
  admiral for the author's list, and the releasable "Test" (TES, cores on Avarre, Graisivaudan and Hevique;
  its flag, 640 × 338, still to fit by hand). 183 countries. The Gazetteer has **state capitals** (◆, one per
  state; the author: "There can be multiple cities in a state ... a way to select both a state and a national
  capital"). The Deco UI is v0.5.1: side panels rise into place instead of sliding across the flag and name.
- 2026-10-15, latest: the leftover placeholder bricks are gone (lakes one province each;
  Arvorenia, Atrocha, the KU island and a Belekria island group cut organically), Placeholdaire's
  and San Sierra's islands are one state each, so their map tools are open on the Gazetteer (39
  of 161). 21,078 provinces (20,690 land, 363 sea, 25 lake), 3,149 states, 62,183 province
  borders, 122 strategic regions, 182 countries. The Gazetteer counts the map's state names as
  named, shows each government's flag in game, picks releasables by whole states, and clips
  drawn states to the nation's land and to each other. Rouental's page (the author's test
  edits, read with its password on 2026-10-15) is not imported.
- 2026-10-15, later: the Gazetteer keeps a nation's map tools closed until its states are drawn
  (37 of 161 open), lets players define releasables, and has admins (Merlo, once the author adds
  him; the author is to paste the new rules). `docs/HANDOFF_MERLO.md` for Merlo's Claude. No
  facts imported yet, so the build is unchanged.
- 2026-10-15: the Gazetteer moved to its own web site, https://rouental.github.io/Valsora-HOI4/
  (GitHub Pages and the author's Firebase project); the author is to paste the database rules.
  No facts imported yet, so the build is unchanged.
- 2026-10-14, latest: the Gazetteer's version 2 (same link): a password per nation, flags,
  rulers, party leaders and characters with portraits, colour and culture, suggestions on the
  map, nations not on the map yet, overseas land in boxes of its own. No facts imported yet, so
  the build is unchanged.
- 2026-10-14, later still: the Gazetteer (https://claude.ai/artifact/PqTTD5FuFJhpL4JKp8sumN), for friends to fill in their nations; no
  facts imported yet, so the build is unchanged.
- 2026-10-14, later: no map changes; the Deco UI (v0.5) is part of the mod: every side panel flush under
  the top bar with the medallion's notch, map modes and a gilt minimap. Not yet seen in game.
- 2026-10-14: no map changes; the game starts in 2036, vanilla's generic events, AI
  strategies and on_actions are back, and stand-ins should take about 1,900 lines out
  of the 2,081-line error.log (decisions, Earth's histories, AI theaters, unit
  positions). Not yet seen in game.
- 20,817 provinces (20,416 land, 363 sea, 38 lakes), 61,400 province borders, 3,117
  states, 122 strategic regions (42 sea), 182 countries (2026-10-13, later: Santa Fe cut
  into 7 states, the last placeholder states given to their neighbours, so Orientalis,
  Usnistan and Solitas are left out; `dist/nations_by_continent.png`). Before: 20,778 provinces (20,377 land), 61,283
  borders, 184 countries (2026-10-13: Solitas outlined,
  nine new nations, the United States of Solitas removed, two islands added). Before:
  20,454 provinces (20,053 land), 60,318 borders, 3,065 states, 176 countries
  (2026-10-12, last: 4,313 small
  provinces merged for HOI4's border limit; before: 24,767 provinces (24,366 land),
  73,231 borders (2026-10-12, later still: ten placeholder states to their new
  owners; before: 3,070 states, 178 countries (2026-10-12, later: Usnistan outlined, 35
  new nations, 545 new states; before: 21,084 provinces (20,683 land), 2,629 states, 143 countries
  (2026-10-12: Merlo's sea, the wrap made seamless; before:
  21,366 provinces (645 sea), 91 strategic regions (11 sea) (2026-10-11: Orientalis
  outlined, 24 new nations, 667 new states; before: 16,646 provinces, 2,073 states, 119 countries (Araseos' last islet to
  Terreich); before: 2,074 states, 120
  countries (2026-10-09, later still: the Oriental Territories, and the
  Midtierre isles re-cut for Peatiktist); before: 16,625 provinces, 2,073 states, 119
  countries (2026-10-09, later: fourteen new); before: 14,812 provinces
  (two more from the Scealand line, 2026-10-09), 1,866 states,
  105 countries (2026-10-08: seven new; before: 14,334 provinces, 1,823 states,
  98 countries (with six more releasables, 2026-10-07, later; before: 92 (2026-10-07: twenty new nations, 521 new states; `dist/preview_new_nations_*.png`)).
  Before: 10,644 provinces, 1,377 states, 72 countries (with Rouental's six releasables and the Holy See). 2026-10-05, later: Terrabis-Seran 76 states, Kilkire-Battania 28, Garfield 10,
  Gaellia 7, Vineta 7, Harwick 1, Devlon 1 (`dist/state_numbers_araseos_southwest.png`,
  `state_numbers_garfield.png`, `state_numbers_san_sierra.png`). Before: 1,271 states (Llainfair's three became one),
  58 countries (2026-10-05, with the friend's Merlovich, Hoalepa and five nations south of
  Solitas). 2026-10-04, later: six more nations (Cascadia 37 states, Wersh 21, Troc
  15, Sicilianzo 14, Danelaw 20, Thorian 4) and the author's state lines kept as drawn
  (`regroup_states.py`): 1,346 states became 1,208. La Recolt and Réveillé became one
  state ("La Recolt"; the author's lines join them). 2026-10-04: the seven nations south of Estande (San Sierra 60 states,
  Anglost 55, Guardana 8, Normania 5, the Pollanas and Dremaur 1 each), Aislada's 13 drawn
  states with its rivers and 14 cities (capital Hirane, which replaced the joke name
  "The Great and Noble City of Merlovia"), four more Rouental cities (Seraine, Saintiers,
  Grande Reliette (misread as "Rebette" at first), Torres), and two more fused islands cut free (`pdn_tools.py channel`:
  the AN island at (654, 1430) and its neighbour, and a bridge at (932, 1492)). The
  author's upload had older game layers in the north-east (no Locus, no Moelle); the
  current ones were kept and only their own layers taken (author: Locus stays).
  2026-10-01, later: Kurikia 143 states, Fraxhemark 149; six Cardonian
  and two Royalist Illiricium states re-cut where new state lines split them; rivers
  edited (72 states re-cut along rivers, 92 % of river pixels on a province border);
  the first nine cities. 2026-10-01: Illiricium 18 states, Entroterra 9, Côtefer 5, Mezzogiorno 5,
  Royalist Illiricium 1, Rouental's islets 1; sea provinces recoloured blue on the
  Provinces layer (`pdn_tools.py blue_seas`). Second map of 2026-09-30: Estande 62 states (with 11 ES islands), Placeholdria
  28 (7 PC islands), Volinovia 16, Rastava 13, Coraliza 6, three RO islets to
  Romanoddle; a 1-2 px state-line nudge in Rouental (14 px moved by hand, too small for
  the split detection) and river edits (provinces re-cut: 47 states, 89 % of river
  pixels on a border). First map of 2026-09-30 added Romanoddle (90 states, with the islands the author's
  Names layer labels RO), Linterre (24, plus three LT islands), Selto (7: its outline
  plus five coastal Linterre states, author's correction from the Notes layer's older
  drawing), 13 re-cut Rouental states and new rivers in Rouental and Linterre. The
  island at (300, 785) was fused to Romanoddle's by 2-4 px land bridges that closed its
  strait into a lake; the strait was reopened (sea, its neighbour's sea region) and the
  island is Nonscio's own state (author). Earlier: Real: Rouental and its seven neighbours (56 states, about 175
  provinces), and Cardonia to the north (67 states, about 300 provinces). Cardonia is
  17 outlined patches plus nine islands the author's References layer colours
  Cardonian (seeded by hand). Everything else is still placeholder bricks. Two rivers
  in Rouental.
- **Rouental build loads and plays** (author, 2026-09-29): its error.log had nothing from
  our map or files, only vanilla noise and the name/portrait generation lines.
- **Loads in-game without crashing** (first build, confirmed by the author). Its
  `error.log` was vanilla-reference noise (decisions, missions, ai_faction_theaters
  region ids) plus the rivers.bmp palette warning above, which the biClrUsed fix
  silenced. Second build: only a trailing newline in `buildings.txt` (read as a
  malformed empty row, now removed) and "failed to generate a name/portrait" for our
  countries, which have no name lists or scientist portraits yet.

## Known gaps

1. Outside Rouental, provinces, states and regions are placeholders. The author is
   outlining countries region by region (see `apply_outlines.py`). The old `.pdn`'s
   country colours, moved to the new layout, are its Notes layer.
2. Terrain is plains everywhere; there are no rivers, railways or trees; the relief is
   noise. A generated terrain (with its own relief) exists as a test only,
   `terrain_test.py` (2026-10-12): the author said not to add it to the mod yet. It
   follows the author's geography where they gave it (the Vale of Reibonne).
3. Lakes vs. inland seas (see Decisions).
4. Country content: only Aislada has a leader and focus tree; the rest use generated
   leaders and the generic tree. No units; flags only for Rouental and its neighbours.
   Generic portraits and name lists exist (see Cultures), scientists' too since 2026-10-14.

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
