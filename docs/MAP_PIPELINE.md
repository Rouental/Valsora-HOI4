# The map and the pipeline

Moved out of `CLAUDE.md` word for word on 2026-10-17 (the efficiency night: the manual is loaded into every session, so it keeps a summary and points here). Read this before changing the map, the `.pdn` tools or any step of the build. Newer additions go here, not into `CLAUDE.md`.

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
but black per city, its name written beside it in black), Necessary Provinces (from 2026-10-17: province lines
inside a state, applied by hand, `pdn_tools.py provinces`). Necessary Terrain is reserved for later detail and not
read yet. **Subregions** and **Subnames** (from 2026-10-17): the parts of a nation that can be released (Belekria's
republics, Krionik's principalities, Pakitsk), one colour per part (a colour may serve two parts far apart), the names
written on Subnames; `read_layers.py` records every painted patch and `build_mod.py` gives them to `nations.SUBREGIONS`.
**"Should be an island!"** (2026-10-17): rings round land the drawing joined to its neighbour, cut by hand
(`pdn_tools.py channel`). "… Reference" layers, "Notes" and "Background" (white) are only for the author. Unknown
layer names are ignored.
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
  name). An unnamed dot, two in one province, or a repeated name stops the build. Cities the author names outside
  the layer and their Gazetteer page are `nations.CITIES` (pixel → name, 2026-10-21: Jourdain and Moterre); a page
  city of the same name and owner moves to that spot with its victory points. In
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
  - diagonal steps get corners, on a province border where one of the two is (read_layers.py passes the province borders, 2026-10-20), and loops/U-turns are shortcut;
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
| `read_layers.py` | **normal mode**: the layers of `HOI4 Mod Map.pdn` → provinces, states, regions, owners, heights, terrain, rivers, and the Subregions layer's painted patches (`work/regions.json`, 2026-10-17) |
| `blocks.py` | placeholder mode only: land mask, continent blocks, removes Antarctica |
| `layout.py` | placeholder mode only: scales every block and pushes them apart |
| `compose.py` | placeholder mode only: game-resolution land / ocean / lakes, continent per pixel |
| `provinces.py` | placeholder mode only: brick provinces, sliver merging, X-crossing repair |
| `regions.py` | placeholder mode only: states, strategic regions |
| `make_game_pdn.py` / `writepdn.py` | turn a placeholder build into a fresh `HOI4 Mod Map.pdn`; `writepdn` writes any `.pdn` from a template's object graph, and adds layers on top when given more than the template has (2026-10-13, the flag file) |
| `nrbf.py` | reads a `.pdn`'s .NET object graph into records with their byte spans (used by `writepdn` to add layers) |
| `pdn_check.py` | a `.pdn` read from end to end as paint.net would (header, object graph, every layer's objects, every pixel chunk), 2 s; `writepdn.py` runs it on every file it writes (2026-10-17: the author's flag file came back corrupted; every copy we had written passed). Object ids are compared by absolute value, as BinaryFormatter reads them (2026-10-18) |
| `pdn_dotnet/run.sh` | a `.pdn`'s object graph read by .NET's own BinaryFormatter, the reader paint.net uses, and by NrbfDecoder (`Program.cs`; needs the .NET 8 SDK, `apt-get install dotnet-sdk-8.0`, and builds itself into `work/pdn_dotnet/`); `writepdn.py` runs it too where .NET is installed. It found why paint.net refused our flag files, which `pdn_check.py` passed (2026-10-18, `docs/PROBLEM_LOG.md`) |
| `pdn_recover.py` | by hand: every layer still whole in a damaged `.pdn` as a PNG (the size and names from the file, or from an older copy with `--like`) |
| `pdn_diff.py` | by hand, first thing with a new upload (2026-10-17): every layer's changes and where, Countries' gains and losses, lines drawn and erased, the areas the new country lines enclose that hold two nations; `work/pdn_diff/` (an overview and each place before and after); 15 s, no disk |
| `apply_outlines.py` | by hand: the author's outline layers → provinces, states, countries in the `.pdn` |
| `pdn_tools.py` | by hand: `navigable` (lake → sea with its own region), `sea_zones` (regroup and recolour regions; refused on a map with Ocean Province Lines), `give` (whole states to a country), `recolour`, `channel` (reopen a strait: the cheapest water-to-water path between two sea pixels becomes sea; `X1,Y1,X2,Y2,M` keeps the path within M px, M 0 to cut an islet's neck the sea goes round otherwise), `border` (the land a moved Necessary Borders line encloses → a country), `cede` (the land of one country a moved line cuts off → another, for countries without state lines: only the first country's pixels count, provinces are split along the line; what a split state loses is a state of its own from 600 px (`CEDED_STATE`), smaller slivers join a state that moved whole), `merge_small` (a country's sliver states join a neighbour), `attach` (a state goes to a country and joins its nearest state, regions too: for an islet or sliver too small to be a state), `add_land` (the water under a layer's paint, default "Islands to Add", becomes a country's land: plains, the nearest land's height, continent and region, a province per island, one new state), `recut` (placeholder land the outline runs never reached cut like an outlined patch: the piece of a country's land around a pixel becomes ~1,300 px states (one up to 2,000 px) and ~190 px organic provinces, each new state in the region most of it lies in; `--keep-states` cuts only the provinces), `lakes` (each lake one province, in the region most of it was in), `provinces` (2026-10-17: every state the author's Necessary Provinces lines cross gets exactly the provinces those lines and its edges enclose), `tidy` (land provinces under 16 px join the neighbour they share most border with, of their own state first), `owners` (2026-10-17: every area the Necessary Borders lines enclose that holds two nations goes to one, the one an `X,Y=COUNTRY` names, else the one a stroke on a "Necessary Owners" layer points to, else the one holding most of it; whole states hand over as they are, crossed ones are cut along the line; a plan without `--apply`), `refine` (2026-10-18, the author: "I'd like a general increase of the province count ... still leave a buffer": more provinces within HOI4's border limit, keeping `REFINE_BUFFER`, 2,000, free; it measures what the build's own fixes add on the last build (61,767 built for 61,429 on the layer) and aims at 63,536 built. First the tundra (`REFINE_TUNDRA`, by pixel: Belekria 1, 4, 5, 6 and 15, the author: "will be tundra, and thus don't need high counts") is cut again into ~`TUNDRA_PX` (600) px pieces; then every nation at least `REFINE_NATION` (4) provinces where its land allows 90 px pieces, every state of 240 px or more at least two, then the largest pieces cut in two, organically (`apply_outlines.organic_split`), until the budget is spent; the states with the author's province lines, `REFINE_SPARSE` (Terreich's "very sparse" isles), Merlo's land (`REFINE_KEEP`) and the provinces across the wrap are left alone. Each piece keeps its province's state and region on the layers, as the build reads them; a plan without `--apply`; `--borders N` another target), `join KEEP=GONE KEEP+GONE ...` (2026-10-21, the author's groups from the grouping map: each pixel pair a state to keep and one to join it; `=` makes the two one province, `+` keeps two provinces in one state; States, Strategic Regions and Provinces recoloured to the keeper's, the Necessary States line between them cleared, or moved to Necessary Provinces for `+`; then drop the gone state's name from `source/state_names.json` and its keys from the Gazetteer facts, summing their populations, as on 2026-10-21) |
| `strategic_regions.py` | retired 2026-10-12 (refuses to run on a map with Ocean Province Lines, unless `--force`): sea regions = the author's oceans, one each, with names (`source/region_names.json`); land untouched |
| `sea_provinces.py` | by hand: the sea from the Ocean Province Lines layer (Merlo's): `build` (provinces from the lines, cut to HOI4's size limit, colours and regions kept by overlap), `seam` (borders and regions meet across the left/right wrap), `names` (`source/region_names.json`: "<ocean> <n>" west to east), `check` (report only) |
| `areas.py` | a module (2026-10-18): the author's areas layer ("Impassible / Desert / Jungle / Tundra": red impassable, yellow desert, green jungle, painted solid); `read_layers.py` gives the land its terrain (desert, desert, jungle; the Gazetteer's still wins) and marks the states mostly red impassable (`regions.json` `impassable`), which `build_mod.py` writes as the base game's Sahara is: `impassable = yes`, `wasteland`, infrastructure 0, no victory points, a twentieth of the manpower, `force_link_ownership_to` the passable state of its owner it shares most border with, never a capital (`check_mod.py`: every impassable state linked, no capital impassable; mutation-tested) |
| `pdn_tools.py areas` | by hand, after a build (and after `river_provinces.py`): the states mostly inside one kind of area cut again into provinces of `areas.PROVINCE_PX` (desert 600, jungle 400; an impassable state one province, the author: "like the big African deserts that are one massive province"), the last build's rivers kept on province borders (not in impassable land), states with Necessary Provinces lines left alone; `refine` leaves these states as they are (2026-10-18: Usnistan's 57 marked states, 486 provinces to 119). Each piece is the tidier of two cuts, k-means or along the area's length (`tidiest`, 2026-10-20, after Mekele's, one province bent round the other); `areas X,Y` cuts the states holding those pixels again even when already coarse |
| `pdn_tools.py necks TAG` | by hand: islands stuck together (2026-10-18, Myehn): in the land masses holding TAG's land, the lobes an opening of `--radius` px leaves (necks narrower than about 2 x radius + 1) of `--min-lobe` px or more cut apart by 2 px channels of sea (`to_sea`); prints the necks and draws `work/pdn_tools/necks.png`, `--apply` saves. Necks wider than the radius, or between a lobe and a small one, by hand: `pdn_tools.py channel X1,Y1,X2,Y2,M`. `to_sea` turns scraps of land under 16 px a cut leaves alone in the water into sea (they broke the build as provinces in two pieces) |
| `river_provinces.py` | by hand, after a build: re-cuts the provinces of every state a river crosses so rivers run between provinces, never a state whose provinces the author drew (2026-10-17); for whole states cut coarse; for a nation with small, drawn provinces use `river_borders.py` |
| `river_borders.py TAG` | by hand, after a build (2026-10-20): every stretch of river inside one of the nation's provinces moved onto a province border (on the author's river layers), the province cut again along it where both parts are big enough, or a sliver beside a Gazetteer river (which the .pdn can't move) given across it; prints the plan, `--apply` does it, then rebuild and run it again until nothing is left; `--rekey` after the last build re-keys the nation's Gazetteer province facts. For land whose provinces were cut without the rivers (`fief_states.py`). Left on 2026-10-20 (stretches of 2+ px off a border): TUP 39 (238 px), UTP 21 (120), AIS 12 (63; Merlo's land), ILR 7 (41), RYB 4 (21), TBS 3, ZNZ 2, NKR 1 (28), KLS 1 (18), MST, HOA, ISG, KRS, SGN, KHB 1 each |
| `borders.py` | HOI4's province border count (pairs of touching provinces, each separate stretch of shared boundary once, land and water alike) and its limit, 65,536; `check_mod.py` uses it; run alone, it counts the last build's |
| `border_report.py` | by hand, after a build: where the province borders come from, and what re-cutting the provinces (one size, a bigger one, sizes by terrain like the base game's, impassable desert) would free; `docs/BORDER_LIMIT.md` (2026-10-15), `--terrain map` once the Terrain layer is painted; `--drawn-states` (2026-10-16): what drawing their own states would cost the nations still on cut ones, at Rouental's density and lighter ones |
| `fief_states.py` | by hand: a nation's states from the author's map of its fiefs (2026-10-20, Rouental's `source/Rouental Fiefs.pdn`: its layers PROVINCE Colors / Borders, Fief Markers, Rough Governorates): fitted onto the game map by overlap (25.84 fief px to a game px), each fief of `--min` game px a state, the smaller merged into a neighbour (crownland with crownland, within the governorate; `--keep x,y=Name` keeps an old state, Rêverie), provinces of ~`--province` px, each state in the region most of it lies in; `--apply` writes Provinces, States, Strategic Regions and the Necessary States lines (and clears the old Necessary Provinces lines) in the nation's land, the names from `--names` (`source/fief_names_ROU.json`, read off the fief map by hand) into `source/state_names.json`, and `work/fief_states/remap.json` (old state name → new states) for `nations.py`'s lists and `gazetteer.rekey` |
| `governorates.py` | by hand, after a build (2026-10-21): a nation's governorates (`source/governorates_<TAG>.json`, Rouental's): the patches of its fief map's Rough Governorates layer read onto the game map with the fit `fief_states.py` found, named by a game pixel inside each (patches of one name are one governorate: Terres Séparées, three; the unnamed numbered west to east), each province in the patch most of its land lies on; without arguments, each governorate's states and the states in none; `--apply` paints each of the nation's states (in the governorate most of its land is in) in that governorate's strategic region on the Strategic Regions layer, a colour of its own kept in the file's `regions` (never blue), and names the regions in `source/region_names.json`; a state in none keeps its region. A governorate in two regions (2026-10-21, the author: Terres Séparées as "South Montvallée" and "North Montvallée") is a `split` in the file: each region's members by state name or a whole nation's tag; its states keep the one governorate on their panels. `--apply` also writes `states` (each state's pixel key in `source/state_names.json` → its governorate), which the state panel's line (`build_mod.state_lines`) reads, and stops the build when a key is gone; `province_picker.py` reads the patches. Run it again when the author draws the Governorate Lines or the states change |
| `merge_provinces.py` | by hand, after a build: merges the smallest land provinces into a neighbour in the same state (never across a river, never two city provinces, at most 400 px) until the borders are down to a target (default 60,000), on the Provinces layer |
| `redraw_flags.py` | unused: Fraxhemark's stand-in flag (writes `work/FRX_standin.png`); the author's own `FRX.png` replaced it |
| `land_regions.py` | by hand, after a build (2026-10-16): the land strategic regions from the nations, on the Strategic Regions layer: a nation (its land on one continent) of over 1.5 × 30,000 px is cut into regions of its own (area-weighted k-means centres, each state joining the nearest along the nation's land), one of 0.6–1.5 × is one region, smaller ones are grouped with small neighbours (longest border first, up to 1.25 ×), a group under 0.25 × joins its neighbour's region, a lake the region it borders most; sea regions untouched; `--target PX`, `--dry` (only `work/land_regions_preview.png`). First run: 137 land regions (80 grid ones before), 5,843 to 59,193 px; Rouental and the seven other Association states one region, the Vale. Run `region_map.py` after the rebuild |
| `region_map.py` | by hand, after a build (2026-10-16): `dist/region_numbers.png`, the 137 land strategic regions numbered for the author to name, `dist/region_names.md` (a table to fill in) and `dist/region_numbers.json` (number → the region's colour); `--apply FILE` ("12 = Name" lines, or the filled table) puts the names into `source/region_names.json` by colour, which the build reads; `--draft` (2026-10-17) writes `dist/region_names_draft.md`, Claude's first draft of every name in the same table (a nation's only region its name, several of one nation compass names round its centre, islands "the ... Isles", two or three nations together their names, four or more the sea their coast faces or their biggest nation's coast, Rouental's the Vale of Reibonne), for the author to change and `--apply` |
| `straits.py` | by hand, after a build (2026-10-17): strait crossings (`adjacencies.csv`, type `sea`). `find`: the narrowest strait between every two landmasses over open sea (where their coasts' nearest-pixel zones meet; lakes and other land block it), each landmass linked once (a minimum spanning tree, narrowest first; big landmass pairs every 150 px of a long strait too), through the sea province the strait's line crosses most that touches both sides: `dist/straits_proposed.json` and `dist/straits_map.png` (full size, each crossing ringed by width and numbered). `approve [--max-gap PX] [--drop N,..] [--add N,..]` writes `source/straits.json` (each crossing by pixels: a coast pixel each side and a sea pixel, since ids shift), which `build_mod.py` reads (`straits.rows`; without it no crossings, the build unchanged). First run: 492 crossings for 606 landmasses (313 up to 6 px of sea, 414 up to 10, the default; the base game's 151 span 2-30 px, median 4); 72 islets lie over 20 px from any land. **In the mod since 2026-10-17**: the 414 up to 10 px (the author: "Apply all the green and yellow strait crossings, I'll judge the others later"); the 78 wider ones (orange 10-15 px, red 15-20) wait for the author. Never between Royalist and Republican Illiricium nor to North Pollana (2026-10-18, the author: "The strait crossing connecting Royalist and Republican Illiricium shouldn't exist ... Neither should the crossings to North Pollana"; `NEVER`, `NEVER_ANY`, which `approve` leaves out): 413 in the mod |
| `province_picker.py [TAG]` | by hand, after a build (2026-10-20, the author: "Give me a map of Rouental where I can select the various provinces and group them together"): `work/province_picker/<TAG>.html`, the nation's provinces on a clickable map (far pieces in boxes under it), from the page `scripts/province_picker.html`; published as a private claude.ai page with a database (Rouental's: https://claude.ai/artifact/RsMPNHMPW1PdhS1Soa6W19), where the author saves groups (collection `groups`: name, kind `province` to merge or `state` to make one state, note, the provinces by pixel "x,y" and by id in the build named). Read back with ArtifactData; merged with `merge_provinces.py` / `pdn_tools.py`. Republish the same file after a map change. Governorates (2026-10-20, the author: "make an option to display governorates so I don't accidentally combine outside them"): a nation with `source/governorates_<TAG>.json` (Rouental's: its fief map, the fit `fief_states.py` found, and the eight names its Governorate Names layer writes, each by a game pixel) has a governorates switch (their borders and names), colours by governorate, the governorate in each province's tooltip, and a warning on a selection or group that crosses one. Each province is in the patch of the Rough Governorates layer most of its land lies on (patches under 20,000 fief map px are leftover paint); off every patch, its state's, else its neighbours'. Rouental: 28 governorates, 20 of them unnamed (numbered west to east), no state split between two; Brillagne and Concorde et Volonté in none |
| `state_map.py` | by hand, after a build: a numbered map of some countries' states (`dist/state_numbers_<name>.png` + `.json`, number → tag and pixel), for the author to name them; `--names` labels them with their names instead |
| `terrain_test.py` | by hand, a test not in the game (author, 2026-10-12: "do not add it to the mod yet"): terrain for the whole map from each continent's real-world model (Nonscio western Europe, Araseos Germany, Yastreovakia eastern Europe and Russia, Usnistan the Middle East and Africa, Orientalis Asia, Solitas loosely the New World, Aislada Australia): its own relief with hand-placed ranges (the Alps down the bay east of Rouental, Tibet and the Himalaya at Ganden, the Ethiopian highlands by Mekele ...), every drawn river in a valley that falls steadily to its mouth, a climate per continent (latitude frame, prevailing winds and monsoons carrying the sea's moisture inland, rain shadows, hand-placed wet and dry areas, wetter where rivers are drawn), terrain.bmp classes (woods on uplands and slopes, farmland on low ground, along rivers and coasts, marsh only where water gathers), and each province's majority type. **The Vale of Reibonne** is the author's (2026-10-12: "Rouental and the Reibonnaise nations are in the Vale of Reibonne and are mostly surrounded by mountains and hills, except the Reliette gap which is open plains"): a low farmland floor ringed by the ranges they drew on their fief map's Mountains layer (`source/vale_ranges.png`, projected from `work/pdn_rmap`: the Osgrande Mountains north, the Nossine north-east, the Bastionne east, the Hollier inside Hollier, the Anarlaine south-west, and the Firime Highlands, hills, north-west) and by hills along the rest of its land border; the Reliette gap (west, between the coast and the Anarlaine, into Placeholdaire) open plains; Marais Verte marsh. Writes `work/terrain_test/` and `dist/terrain_test_map.png`, `terrain_test_provinces.png`, `terrain_test_vale.png` |
| `coarse_preview.py` | by hand, a preview not in the game (author, 2026-10-18: "I tried marking out areas which I know will be either tundra or extreme desert or jungle like base game africa ... Just a snapshot / preview, not for the full mod"): the upload's layers (`readpdn.py UPLOAD DIR`), its layer "Desert" (red outlines extreme desert, green jungle: the land inside; white lines tundra: the coastal land they cut off), each state's share of those areas cut again into provinces of about each size given (`--sizes`, default 500, 800, 1500; never more pieces than before, the states unchanged, states with Necessary Provinces lines left alone); writes `work/coarse_preview/report.txt` (the borders each size frees) and `place_NN.png` (each area as it is and at each size) |
| `usnistan_prototype.py` | by hand, a prototype not in the game: a fully generated Usnistan (relief, climate terrain, rivers, ~800 provinces, states, 6 placeholder countries, cities) into `work/usnistan/` and `dist/usnistan_*.png` (author asked for an example, 2026-10-02) |
| `regroup_states.py` | by hand, after `apply_outlines.py`: in every country with state lines of its own, each drawn area becomes exactly one state (provinces kept, split only where a line crosses them; `NOT_DRAWN`: Belka, whose only lines are Pakitsk's). After a big redraw, re-cut the provinces of the states it changed (`pdn_tools.py recut --keep-states`, one seed per piece, only in the countries drawn; then `tidy`): on 2026-10-17 the new lines had cut 1,468 provinces into pieces down to 16 px; `--recut` (2026-10-17) does that re-cut and `tidy` in the same run |
| `import_flags.py` | by hand: the author's flag `.pdn` (one layer per flag, named after the nation) → `source/flags/TAG.png`; a stored flag is replaced when any pixel differs at the same size, or by more than resampling would at another size (`changed`, 2026-10-09); see-through pixels are filled from the nearest solid one first (`opaque`), since the game shows them as holes; or a folder of PNGs, one per flag named after its nation, a leading number ignored (2026-10-17: what `pdn_recover.py` saves) |
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
| `vanilla_parts.py` | vanilla's parts in the mod, for `build_mod.py`: the vanilla files it ships moved to 2036, the stand-ins for what Earth's content still names (decisions, events, country histories, and `EARTH_FLAGS`: plain 32-bit flags for two of Earth's the base game ships at a pixel depth its loader complains of, 2026-10-21), the start and end dates, the AI's faction theaters |
| `vanilla_sync.py` | by hand, after a game update: refreshes `source/vanilla/` from the author's copy of the game (`Rouental/HOI4-Files`): the vanilla files the mod ships changed, and lists of vanilla's names (and its traits and kinds of company, `index/traits.json` and `index/companies.json`, for the Gazetteer, and its autonomy levels, `index/autonomy_states.txt`), and the game's English lines that open a sentence with a country's definite name, capitalised (`GetNameDefCap`: "the Cardonian Kingdom has announced ..." in the author's screenshot, 2026-10-17; `curated/localisation/english/replace/valsora_name_caps_l_english.yml`) |
| `pdxscript.py` | a reader for Paradox script (nested `key = value` blocks), used by `vanilla_sync.py` |
| `check_mod.py` | re-reads the built files and checks every rule below |
| `export_canvas.py` | previews in `dist/` |
| `package.py` | `dist/valsora_test.zip` (reproducible: fixed dates and permissions, sorted) |
| `stamp.py` | `fresh` / `save` a step's inputs, so `run_all.sh` skips `read_layers.py` while they are unchanged (`FORCE=1` reruns it) |
| `mutation_test.py` | by hand, after changing `check_mod.py`: breaks hard-linked copies of the build in 56 known ways (map files, history, content, files), runs `check_mod.py` on each batch side by side, and fails unless every break is reported (a miss is retried alone, in case another break hid it); 30 s. Add a break for every new check (2026-10-15: it found our on_actions' scripted effects unchecked) |
| `fit_flag.py` | by hand: a flag the author sends in another shape → `source/flags/TAG.png` at 82:52 without resampling (plain field trimmed round an emblem, vertical bands made longer, stripes lengthened or made taller, a screenshot's frame cropped; quarters, crosses and borders refused) and `work/flag_fit_TAG.png` to check |
| `build_flags15.sh` | by hand: the larger flags' test version (`docs/HD_FLAGS_TEST.md`) beside the mod: the Deco UI drawn for it in `work/deco_flags15/`, the mod in `work/build_flags15/`, `work/valsora_test_flags15.zip`; `build/` and `dist/` untouched |
| `publish_site.sh` | by hand: the Gazetteer's site (`facts_export.py`, `gazetteer_site.py`) as the next commit of `gh-pages`, pushed; nothing when unchanged |
| `tests/gazetteer/` | by hand, after `facts_export.py`: the Gazetteer page driven in Chromium with a stand-in for claude.ai's runtime: `run.py` (owner, friend, passwords, desktop and phone, light and dark), `traits.py` (traits and their requests), `companies.py` (political advisors, companies and their requests), `ingame.py` (the game's own characters and releasables, commanders' stats, cities' size), `reset.py` (Owner tools › Start over), `guide.py` (the quick-start guide); `harness.py` builds the test site in `work/gazetteer_test/` |
| `country_list.py` | by hand, after a build: `dist/world_map_labelled.png` (every country labelled) and `dist/countries.md` / `.csv` (name, full name, ideology, sub-ideology, culture, leader, states), read from the built mod |
| `nation_sheet.py` | by hand, after a build: `dist/nations_by_continent.png`, every nation in the game under the continent of its capital: flag, ruler at the start (portrait of our own, or a "placeholder" box for a base-game one), full name, ideology and sub-ideology, culture, and a strip of its map colour (author, 2026-10-13) |
| `collages.py` | by hand, after a build: `dist/flags_collage.png` (every custom flag, and the countries still on a placeholder stripe) and `dist/leaders_collage.png` (every custom leader: own portraits at 2×, named ones with base-game portraits as labelled tiles); `--continent NAME` writes only `dist/flags_<name>.png`, the flags of the nations whose capital is on that continent, naming below them those with land there and their capital elsewhere (2026-10-10, Araseos; 2026-10-12, Yastreovakia) |
| `atlas_export.py` / `atlas.html` | by hand, after a build (2026-10-17, not in the mod): the Valsora Atlas, the build's world in a browser (every map mode, search, nations' and states' cards, what changed since the last export); `work/atlas/`, published as a private claude.ai Artifact; `docs/ATLAS.md` |
| `facts_export.py` | by hand, after a build: the Gazetteer's map data into `work/gazetteer/` (`index.json`, `world.png`, `n/<TAG>.json` per nation: its states, provinces, cities and politics as built, its flag, its land and the neighbours' around it as province numbers per pixel, in parts, with the rivers, and whether its states are drawn, `final`), published with the page |
| `gazetteer.html` | the Gazetteer (see below): the page where friends fill in their nations' facts; the web site's (`gazetteer_site.py`), or a claude.ai artifact with its own database (the first version) |
| `gazetteer_site.py` | the Gazetteer's web site into `work/gazetteer_site/` (the page with the Firebase project's settings, the SDK bundle from `source/gazetteer_site/`, `facts_export.py`'s map data), committed alone on the `gh-pages` branch, which GitHub Pages serves; `--emulator` builds it for Firebase's local emulators (tests) |
| `gazetteer_fetch.py` | 2026-10-18: the Gazetteer's atlas read straight from Firestore as a read-only service account (the secret `GAZETTEER_SERVICE_ACCOUNT`), into the file the page's Save every nation as a file writes (`docs/GAZETTEER_INTERNALS.md`, "Reading the site directly") |
| `apply_suggestions.py` | 2026-10-18: the Gazetteer's suggestions (the export of that day, 15 of them) onto the `.pdn`, each by its label and the plan in the script (`PLAN`): split a state along its drawn line (Rouental's Leclerc and Kove), merge states (Terreich's Reuenland-Thuringen; the Triftsund-Inseln and Teuton isles in states of two, `pairs`, as the author asked, few provinces, `sparse`), new states from drawn polygons (Rosenburg, Terreichstadt; Ungar's six), a province or an islet of its own (North Pollana); names into `state_names.json` at each state's deepest pixel; the new states' borders drawn on Necessary States, so the Gazetteer counts them as drawn. Provinces the new lines leave under 16 px join their neighbours; an islet grows to a province without closing off sea. Kept as the record of what was done and how; 2026-10-19: Ostaria's five drawn states too, `--only=OST` (each run applies only the nations named, the rest of `PLAN` being on the map already) |
| `gazetteer.py` | the Gazetteer's facts into `source/gazetteer/<TAG>.json` (pictures in `source/gazetteer/assets/`): `paths KEYS.json` (each nation's atlas folder `n/<TAG>/<key>` from the owner's passwords), `pull DIR` (the atlas as the ArtifactData tool saves it, pictures fetched by asset id into `DIR/assets/`), `import FILE.json` (a file saved from the page or the site, pictures inside; drops the map facts of nations whose states aren't drawn; gives releasables their tags), `status` (releasables' cores, and what is left to do by hand), `suggestions` (`dist/gazetteer_suggestions.png`, a layer for the `.pdn`); `finals` (whose states are the author's); and the functions `read_layers.py` (terrain, rivers, cities) and `build_mod.py` (state facts, capitals, railways, supply hubs, names, sub-ideologies, rulers and party leaders with titles and portraits, characters, companies, map colours, releasables) call |

**A clean `check_mod.py` run is the bar for shipping a build.** It was mutation-tested
(CRLF, X-crossing, missing building row, state split across regions, descriptor
mismatch, missing localisation) and catches all of them. Since 2026-10-14 it also checks
our files against vanilla's own names (`source/vanilla/index`): sprites, technologies,
equipment, modules, battalions, ideas, defines, the map files the mod inherits, the
stand-ins for Earth's decisions and tags, every event fired (by focus, effect, event or
on_action) and 2036 (mutation-tested: 19 breaks, all caught). The checks that judge our
scripting (tags targeted, popularities, ideologies) skip vanilla's shipped files. Since 2026-10-15 the breaks are kept
in `scripts/mutation_test.py` (56, every one caught): run it after any change to `check_mod.py`. Since 2026-10-16 it
also fails on a letter of our text or name lists that a font the mod ships lacks (a bitmap font draws nothing for it),
on a letter of a name drawn on the map (countries, states, regions, victory points) that the map font lacks, and on a
map font texture over 2048 x 1024 (the game refuses it and draws no names: 2026-10-16).

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
  - `adjacencies.csv` keeps the `-1;-1;;-1;-1;-1;-1;-1;-1` end line. A strait crossing is
    `From;To;sea;Through;-1;-1;-1;-1;;Comment` (two land provinces, the sea province between; -1 lets the game place
    the crossing's line, as most of vanilla's do); `check_mod.py` checks every row (mutation-tested).
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
- `history/general/generic_advisors.txt` comes back (2026-10-21, the author: "might as well bring back generic advisors
  and theorists"), from `source/vanilla/files/`: `vanilla_parts.generic_advisors` keeps its five generic blocks (the
  four political advisors; the industrialists, chiefs, high command and theorists) for every country but the dynamic
  ones, drops Earth's special cases (Iceland, Belgium, Afghanistan, the Philippines, Indonesia, Manchukuo) and every
  condition naming an Earth country or focus, and stops the build if the game's file changes its layout or still names
  one. 20 generated characters a country; a country whose Gazetteer page gives it a political advisor of one of the
  four kinds gets no generic one of that kind (the game's own `has_allowed_idea_with_traits`).

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
