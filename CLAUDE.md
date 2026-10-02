# Valsora — HOI4 total conversion

Turns the author's hand-drawn fictional world (paint.net `.pdn`) into a Hearts of Iron IV
map. Game version: **1.19.3**. The mod installs as `mod/valsora_test` in
`Documents/Paradox Interactive/Hearts of Iron IV/` (on the author's machine Documents sits
under OneDrive — keep that segment in any absolute path).

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
```

## The editable map: `source/HOI4 Mod Map.pdn`

The author edits this file from now on; `docs/EDITING.md` is their guide (keep it in
step with `read_layers.py`). It is exactly game size (5120×2560, one pixel = one map
pixel), and each layer is one kind of game data, found **by name**. Bottom to top:
Heightmap, Terrain, Rivers, Continents, Provinces, Strategic Regions, States, Countries,
and "Notes (ignored by the build)". **The author's editing layers are named "Necessary …"**
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
  set by `nations.CAPITALS` (the dot's pixel): Winterthorn CRD, Venezzo CTF, Alqira ILR, Malin MZG,
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
  - widths: major 7→9, minor 4→5 (7+ is a large river), per pixel by the layer it was
    drawn on, so a river can change size along its course;
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
  steps, still along the border). Rerun it whenever rivers or outlines change.
- **Outlines → states** (`apply_outlines.py`, run by hand, not by `run_all.sh`).
  The author draws 1-px country borders on "Borders" and state lines on "Necessary
  Provinces" (the author's layer name; they are **states**, author's correction).
  - Every enclosed patch becomes a state. Patches over 1,000 px are k-means split into
    ~650 px states that fill the same shape.
  - Every state is cut into ~150 px provinces for a granular map (placeholder bricks
    elsewhere are 1,024 px). Pieces are forced 4-connected.
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
  - Islets under 150 px join the nearest state of their country within 300 px
    (`ISLET_REACH`); farther ones (Rouental's two islets off Solitas) share a state of
    their own. `LEAVE` lists patches the lines close off by accident (the land south
    of Entroterra and Estande), which stay as they are.
  - Cut placeholder provinces and states are cleaned up iteratively: scraps join a
    neighbour (a new province's scrap stays in its state), never a new state, and
    states are forced into one region.
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
| `make_game_pdn.py` / `writepdn.py` | turn a placeholder build into a fresh `HOI4 Mod Map.pdn` |
| `apply_outlines.py` | by hand: the author's outline layers → provinces, states, countries in the `.pdn` |
| `pdn_tools.py` | by hand: `navigable` (lake → sea with its own region), `sea_zones` (regroup and recolour regions), `give` (whole states to a country), `recolour` |
| `strategic_regions.py` | by hand: sea regions = the author's oceans, one each, with names (`source/region_names.json`); land untouched |
| `river_provinces.py` | by hand, after a build: re-cuts the provinces of every state a river crosses so rivers run between provinces |
| `redraw_flags.py` | unused: Fraxhemark's stand-in flag (writes `work/FRX_standin.png`); the author's own `FRX.png` replaced it |
| `state_map.py` | by hand, after a build: a numbered map of some countries' states (`dist/state_numbers_<name>.png` + `.json`, number → tag and pixel), for the author to name them; `--names` labels them with their names instead |
| `organic.py` | organic splitting (seeded watershed over noise), used by `apply_outlines.py` |
| `rivers.py` | plain river lines → HOI4 rivers.bmp format, and the river rules check |
| `build_mod.py` | every mod file |
| `nations.py` | hand-written per-nation content (leaders, portraits, focus trees), used by `build_mod.py` |
| `superevents.py` | TNO-style superevent windows, their texts, picture and music |
| `cultures.py` | generic portraits, name lists and graphical culture per continent / country |
| `ideologies.py` | the five ideologies: ideology file, renamed localisation, theocracy icon |
| `check_mod.py` | re-reads the built files and checks every rule below |
| `export_canvas.py` | previews in `dist/` |
| `package.py` | `dist/valsora_test.zip` |

**A clean `check_mod.py` run is the bar for shipping a build.** It was mutation-tested
(CRLF, X-crossing, missing building row, state split across regions, descriptor
mismatch, missing localisation) and catches all of them.

## Decisions worth keeping

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
- **Provinces are bricks**: 32 px on land, 128 px at sea, 48 px on lakes, with odd rows
  offset by half a brick so only three provinces meet at grid corners. Bricks never cross
  the seam (the edge half-bricks of odd rows are folded into their neighbour). Pieces under
  25% of a brick merge into the same-kind neighbour with the longest shared border.
  Remaining X-crossings (coasts, seam) are fixed by moving single pixels, never letting a
  lake touch the sea.
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
- **Sea regions are the author's oceans, unsplit** (`strategic_regions.py`, 2026-09-30).
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
    tag, so Solitas is `SLT`). They are `common.PLACEHOLDERS`, the only countries the
    bookmark recommends (author's wish, to keep the start menu short).
  - Colours follow the flags (author): Rouental royal green, Guedelon blue, Hollier red, Seigne white,
    Evriches yellow, Lustiana black, Selgrave dark maroon, Lanzerac dark gold, Cardonia
    deep purple. Guedelon's blue and Hollier's red are their flags' main colours. `pdn_tools.py recolour Countries OLD=NEW` keeps
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
    The new three's colours and adjectives are Claude's picks. All tags were checked
    against vanilla `common/country_tags`; new tags must be too.
  - The adjectives of the neighbours are guesses; the author may rename them.
- **State names** are the author's, in `source/state_names.json` ("x,y" of a pixel
  inside the state → name, since ids shift; `build_mod.py` stops if a pixel is in no
  state or two name one state). Unnamed states are "Country N". First set (2026-10-01):
  Rouental's 54 and its seven neighbours', numbered by `state_map.py`; then (2026-10-02)
  21 Chouan, the islets off Solitas Concorde et Volonté, and Rolantelle split by a new
  state line into Ghessone (west) and Rolantelle (east); Maïeul split into Moelle
  (north; Selgrave takes it in the civil war) and Maïeul (south). `state_map.py --names` draws a
  country's states with their names (`dist/state_names_<name>.png`).
- **Localisation keys are our own** (`VAL_STATE_n`, `VAL_REGION_n`), so vanilla's
  `STATE_n` / `STRATEGICREGION_n` Earth names never show. Victory point names have to
  reuse vanilla's `VICTORY_POINTS_<id>` keys, so they live in `localisation/english/replace/`.

## Nation content (`nations.py`)

Aislada is the worked example of a built-out nation:
- **Leader.** Merlovich (`AIS_merlovich`) is defined in `common/characters/AIS.txt` as a
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
  `GFX_portrait_<name>` sprite.
- **City names**: `nations.CITY_NAMES` overrides victory point names, keyed by
  `"capital:TAG"` (e.g. Aislada's capital is "The Great and Noble City of Merlovia") or
  by province id. Ids shift whenever the map is rebuilt, so prefer the capital key;
  `build_mod.py` stops if a named id is no longer a victory point.
- **Rouental (ROU)** is the country the author outlined inside Nonscio. Everything
  first built for NSC moved to it, with `NSC_` renamed `ROU_`; NSC is plain "Nonscio"
  again. `nations.IDEOLOGY_NAMES["ROU"]`: "Rouental" on the map for every government,
  with the author's formal names (2026-09-30): Monarchist "The Sacred Principality",
  Authoritarian "The Grand Principality", Theocratic "The Most Seran State",
  Democratic "The Republic", Communist "The People's Republic" (all "… of Rouental");
  adjective Rouentaise. (The first names, Perfect / Powerful / Boring / Shitty
  Rouental, were dropped.)
  - **Capital: Rêverie**, the one-province state the author drew at (660, 805)
    ("Rouental 27" in that build), set by `nations.CAPITALS` (tag → pixel, since state
    ids shift). Neighbours' capitals are named by `CITY_NAMES` "capital:TAG": Guedelon,
    Evriches, Argent-sur-Seigne (SGN), Grande Hollier, Lanzerac, Villerose (SGV),
    Tanière (LST).
  - Leaders are in `common/characters/ROU.txt`: Roland Cahun (`despotism`, leads at
    start) and Serelle Cahun (`fascism_ideology`, fascist party leader).
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
    - Its template, `faction_template_reibonnaise_association` in
      `common/factions/templates/valsora_factions.txt`, uses vanilla's generic manifest,
      goal, rules and icon.
    - ROU's history does `create_faction_from_template` + `add_to_faction`, the way
      vanilla ENG does in 1.19.
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
  icon) and the **royal host** (`history/units/ROU_1936.txt`: 2 armoured, 2 mechanised,
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
  their map colour.
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
  Monarchy, Legitimism. Authoritarian also has the author's **Bleacherism** (Alban
  supremacy; officially a senatorial republic under a strongman): ILR CTF ETR MZG;
  KIL is Legitimism. Theocratic: Hierocracy, Clerical Monarchism, Holy Order, Synodal
  Rule, Prophetic Rule. Vanilla's Earth-bound ones (`nazism`, `japan_militarism_ideology`
  …, `ideologies.HIDDEN`) stay defined because vanilla's characters and focus files name
  them, but are never given to generated leaders. The author wants no more for now.
- Subtype descriptions start with the subtype's name ("Feudalism: …"), so it shows on
  mouse-over (author). `lordly_republic` "Lordly Republic" (democratic) is the author's
  own: a republic in which the nobility and clergy retain significant power.
- **Every ruler is a set character** (author, 2026-09-30: no subtype left to chance).
  `nations.LEADERS` gives each tag its subtypes; the first leads the country, and the
  country starts under that subtype's ideology (elections on if democratic).
  `cultures.leaders` makes the characters (`common/characters/valsora_leaders.txt`,
  id `TAG_leader_<subtype>`, never `TAG_<subtype>`, which the game reads as the country's name under that subtype): a name from the culture's list (famous surnames skipped, full
  names unique map-wide) and a generic politician portrait of the culture, seeded by
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
  - Overrides are in `TAG_CULTURE`: the Reibonnaise states (ROU SGN EVR HLR SGV LST LZC
    GDN) and Placeholdros (LNT) use FRA names and France portraits (author: French for now);
    RST VLN ESD CRZ PLH use POR names (added to `source/names/vanilla_names.txt` from
    vanilla) and Europe portraits.
- **Scientists and operatives** have no blocks yet. Vanilla's scientist file format
  (`998_scientist_portraits.txt`) couldn't be fetched, so "failed to generate a
  portrait … scientist" may remain.

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
  (icon_entry.cpp) when a second game was started. Source unknown, not seen before;
  watch for it.

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
  {0,1,2,9,10,11,12,21,22,23,30,31,38}; lakes need none.
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

Left loaded on purpose, and noisy in `error.log`:
- National focus: it holds the generic tree our countries use.
- Ideas, MIOs, scripted effects and triggers, ai_areas, operations and achievements. They
  reference vanilla ids, which the previous build showed the game tolerates.

## Cartographic submod (removed)

A flat, HOI3-style "Valsora: Cartographic Map" submod was tried on 2026-10-01 and
removed at the author's request ("it wasn't great"); they may come back to it. It is
in git history (commit d2d6cd8, `scripts/cartographic.py`). It used
`GRADIENT_BORDERS_THICKNESS_COUNTRY_LOW/HIGH` = 2000 for solid country fill, a flat
`world_normal.bmp`, a khaki land colormap and a grey-blue sea with a 15° graticule.

## Current state

- 7,648 provinces (6,965 land, 645 sea, 38 lakes), 1,208 states, 91 strategic regions (11 sea),
  31 countries. 2026-10-01, later: Kurikia 143 states, Fraxhemark 149; six Cardonian
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
   noise.
3. Lakes vs. inland seas (see Decisions).
4. Country content: only Aislada has a leader and focus tree; the rest use generated
   leaders and the generic tree. No units; flags only for Rouental and its neighbours.
   Generic portraits and name lists exist (see Cultures), but not yet for scientists.

## Working with the author

**Keep `docs/PROBLEM_LOG.md` up to date** (author, 2026-09-30): every error or problem,
its cause and its fix, newest first.

**Every time the author sends a `.pdn`, send `source/HOI4 Mod Map.pdn` back when done**
(author, 2026-09-30), so their copy has every edit. Their upload may be based on an
older version (the 2026-09-30 one predated the sea zones and recolours): diff its game
layers against `source/` first, and merge, keeping the current game layers and taking
their own layers (outlines, rivers, names, references) from the upload.

The author tests in-game and reports crashes and `error.log`. They cannot see the
pipeline, so always say which files changed and how to install:
1. Delete `mod/valsora_test/` and `mod/valsora_test.mod`.
2. Unzip `dist/valsora_test.zip` into `mod/`; it contains both.
3. Launch with `-debug`.
