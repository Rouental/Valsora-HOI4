# Valsora — HOI4 total conversion

Turns the author's hand-drawn fictional world (paint.net `.pdn`) into a Hearts of Iron IV
map. Game version: **1.19.3**. The mod installs as `mod/valsora_test` in
`Documents/Paradox Interactive/Hearts of Iron IV/` (on the author's machine Documents sits
under OneDrive — keep that segment in any absolute path). Valsora takes place in **2036**:
the game starts on 1 January 2036 (see "2036" under Decisions worth keeping).

The map is the author's drawing at game size, 5120×2560: its land, rivers and the countries and states they
outline region by region (161 nations on the map, 204 countries with the releasables and the civil war's), and the
sea provinces their friend Merlo drew. Rouental is the built-out nation (leaders, focus tree, civil war, army); the
rest have set rulers and the game's generic content, moved to 2036. The interface is the author's art deco design,
the Valsora Deco UI (`deco_ui/`). The Gazetteer, a web site, lets the author's friends fill in their own nations.

**Where things are written down:**
- this file: the short manual (rules, one line per decision, the pipeline in brief) and where things stand; in full:
  `docs/MAP_PIPELINE.md` (the map, every script, what HOI4 requires, vanilla switched off), `docs/DECISIONS.md`,
  `docs/CONTENT.md` (nations, ideologies, cultures, superevents);
- `docs/NATIONS.md`: every nation, who named and decided what; `docs/HISTORY.md`: the build's history, date by
  date; `docs/PROBLEM_LOG.md`: every problem, its cause and its fix;
- `docs/EDITING.md`: the author's guide to the `.pdn`; `docs/GAZETTEER.md`: the Gazetteer (and how it works, for Claude:
  `docs/GAZETTEER_INTERNALS.md`; every function of the site, for the author to sort: `docs/GAZETTEER_FUNCTIONS.md`);
  `docs/HANDOFF_MERLO.md`: for Merlo's Claude; `deco_ui/CLAUDE.md`: the interface's own manual (its versions:
  `deco_ui/docs/VERSIONS.md`); `docs/WORKFLOW.md`: how a map update goes, and what makes it faster for both sides;
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

## Read before you change

This file is the short manual, loaded into every session; the detail is in `docs/`, moved there word for word on
2026-10-17 (the efficiency night). Read the part you are about to touch first:
- the map, the `.pdn`, any script of the pipeline, what HOI4 requires, the vanilla content switched off:
  `docs/MAP_PIPELINE.md`;
- a decision below, in full with the author's words: `docs/DECISIONS.md`;
- nations, leaders, ideologies, cultures, superevents (`nations.py`, `ideologies.py`, `cultures.py`, `superevents.py`):
  `docs/CONTENT.md`;
- the interface: `deco_ui/CLAUDE.md` (and its versions, `deco_ui/docs/VERSIONS.md`); the Gazetteer:
  `docs/GAZETTEER_INTERNALS.md`.
New detail goes into those files; this one gets a line.

## The map and the pipeline (in full: `docs/MAP_PIPELINE.md`)

- **The editable map** is `source/HOI4 Mod Map.pdn`, exactly game size (5120×2560, one pixel = one map pixel), a layer
  per kind of game data found **by name** (Heightmap, Terrain, Rivers, Continents, Provinces, Strategic Regions, Ocean
  Province Lines, States, Countries ...). The author's editing layers are "Necessary ..." (Borders, States, Provinces,
  Names, Major / Minor Rivers, Cities), plus Subregions / Subnames (releasables' land) and "Should be an island!";
  references and notes are ignored. Their guide is `docs/EDITING.md`: keep it in step with `read_layers.py`.
- **Refer to places by `capital:TAG` or by pixel, never by province id**: ids follow reading order and shift.
  Countries are matched by exact colour to `common.COUNTRIES`; everything else is decided per province by majority.
- **Rebuild:** `sh scripts/run_all.sh` from the repo root (about 2 minutes; `read_layers.py` is skipped while its
  inputs are unchanged, `FORCE=1` reruns it; logs in `work/logs/`). Needs `pip install -r requirements.txt`. Output is
  deterministic, the zip included. **A clean `check_mod.py` run is the bar for shipping a build**; run
  `scripts/mutation_test.py` after any change to `check_mod.py`, and add a break for every new check.
- **When the author sends a `.pdn`** (each step in `docs/MAP_PIPELINE.md`): `pdn_check.py` the upload;
  `pdn_diff.py CURRENT UPLOAD` (every change and where, before/after pictures in `work/pdn_diff/`, and the areas the
  moved country lines enclose); if their copy is older than ours, merge (keep our game layers, take their own layers);
  then as needed `pdn_tools.py owners` (settle the moved borders; plan first, `--apply`), `apply_outlines.py` (new
  outlines), `regroup_states.py --recut` (their state lines; the provinces the lines cut are cut again; it redoes every country with lines of its own, so keep its result only where the lines changed: `docs/PROBLEM_LOG.md`, 2026-10-18),
  `pdn_tools.py provinces` (their province lines), `pdn_tools.py channel` / `necks` (islands to cut free), `river_provinces.py`
  (after new rivers; `river_borders.py TAG` for a nation of small drawn provinces), `pdn_tools.py areas` (the marked deserts and jungles coarse; after a build); rebuild; `state_map.py` for the newly drawn states to name; send the `.pdn` back, dated (`docs/MAP_VERSIONS.md`).
- **The scripts** (each one's detail in `docs/MAP_PIPELINE.md`'s table): the build (`readpdn`, `read_layers`,
  `build_mod`, `deco_ui`, `check_mod`, `export_canvas`, `package`, with `nations`, `cultures`, `ideologies`,
  `superevents`, `superevents_deco`, `test_events`, `minimap`, `globe`, `vanilla_parts`, `straits`, `borders`;
  `rouental_ui` after `deco_ui`: Rouental's governorates and three powers windows, its data `rouental_realm`, its
  previews `rouental_preview`);
  by hand on the `.pdn` (`pdn_tools`, `apply_outlines`, `regroup_states`, `sea_provinces`, `river_provinces`, `river_borders`,
  `merge_provinces`, `land_regions`, `fief_states` (a nation's states from the author's fief map), `governorates` (a
  nation's governorates: their states, `--apply` their strategic regions), `pdn_diff`, `pdn_check`, `pdn_dotnet` (paint.net's own reader, .NET), `pdn_recover`, `writepdn`, `nrbf`, `organic`, `rivers`);
  flags (`import_flags`, `fit_flag`); after a build, reports and maps (`country_list`, `nation_sheet`, `collages`,
  `state_map`, `region_map`, `border_report`, `province_picker` (a nation's provinces to group, a private claude.ai page; the groups applied with `pdn_tools.py join`), `superevent_preview`, and the Valsora Atlas `atlas_export` +
  `atlas.html`, the build in a browser, not in the mod: `docs/ATLAS.md`); the Gazetteer (`facts_export`, `gazetteer`,
  `gazetteer_site`, `publish_site.sh`, `tests/gazetteer/`); vanilla (`vanilla_sync`, `pdxscript`); tests not in the
  game (`terrain_test`, `usnistan_prototype`, `coarse_preview`); `build_flags15.sh` (the larger flags' test version).
- **HOI4's hard rules** (all checked by `check_mod.py`): the map is 5120×2560 (the largest size under the game's cap);
  **at most 65,536 province borders** (3,214 left on 2026-10-21; new land is cut at ~190 px; `borders.py` counts); provinces
  one 4-connected blob of 16+ px, no 2×2 window of four provinces; `definition.csv` CRLF; localisation UTF-8 with BOM;
  every province in one strategic region, a state's provinces in one, naval regions contiguous; the map files exactly
  map-sized. Map errors crash on launch unless the game runs with `-debug`: always test with it.
- **Vanilla content**: Earth's history, events, decisions, AI strategies, on_actions and bookmarks are switched off
  (`replace_path`, the same lines in `descriptor.mod` and the launcher's `valsora_test.mod`); vanilla's generic content
  comes back as the mod's own (`source/vanilla/`), with stand-ins for what Earth's content still names; the generic
  advisors and theorists too since 2026-10-21 (`vanilla_parts.generic_advisors`, Earth's cases out).

## Decisions worth keeping (each in full: `docs/DECISIONS.md`)

- **2036** (author, 2026-10-14): everything the game dates moves a hundred years (clock, tech tree years, generic
  content's dates, names with years; equipment keeps vanilla's `year`); `check_mod.py` fails on any 18xx or 19xx date.
- **Railways wait** (author, 2026-10-15): only the lines drawn on the Gazetteer; don't generate a network until asked.
- **Province sizes by terrain** (author, 2026-10-15): deserts and the like may get larger provinces once the Terrain
  layer is painted; Rouental keeps its dense ones. The guide's numbers (2026-10-17): usually Cardonia's ~160 px,
  down to ~120 for crowded land, 300 to 800 for empty land.
- **The mod's zip stays in `dist/`, committed** (author, 2026-10-15) and is sent in the chat too. This session can't
  publish releases (GitHub answers 403): the Releases page, when it comes, is the author's to publish by hand; don't
  work around that. Old zips stay in the history unless the author says otherwise.
- **Test content until the first public build** (author, 2026-10-15): Devlon's spirits and Rouental's test decisions
  stay until the author takes them out.
- **Read the `.pdn` directly** (its format: `docs/DECISIONS.md`); the placeholder mode's layout of the continents
  (rigid blocks, scale 0.375, straits traced, islets dropped, Antarctica removed) is history now that the author draws
  at game size.
- **The areas layer** (author, 2026-10-18): red is impassable desert, "like the big African deserts that are one
  massive province" (one province a state, `impassable = yes`); yellow desert; green with red stripes impassable jungle
  (2026-10-19); white tundra, white with red impassable tundra (2026-10-20: the game's snowy plains, 600 px provinces);
  the lines round them on Necessary States are states too (`scripts/areas.py`, `pdn_tools.py areas`).
- **Rouental's governorates are shown first, played later** (author, 2026-10-21: "They should be shown, and will
  eventually affect play. They'll hook into the levy system"): its 26 (`source/governorates_ROU.json`, the fief map's
  rough patches until the author draws the Governorate Lines) are its strategic regions (`scripts/governorates.py`;
  Terres Séparées two, South and North Montvallée, 2026-10-21), and the state panel says each state's governorate and
  "Royal Fief" for the eleven, Rêverie among them (`build_mod.state_lines`).
- **Rouental's states are its fiefs** (author, 2026-10-20: "Let's go with the 30 pixel version"): the author's fief map
  `source/Rouental Fiefs.pdn` read onto the game map by `fief_states.py` (each fief of 30 game px a state, the smaller
  merged into a neighbour, crownland with crownland, within the governorate); its lines on Necessary States.
- **No bricks are left** (2026-10-15): every lake is one province and all land is cut like an outlined patch.
- **Enclosed water becomes lakes**; the two inland seas with islands are navigable sea.
- **Sea provinces and sea regions are Merlo's** (2026-10-12, the author's friend; `sea_provinces.py`), seamless across
  the wrap; `strategic_regions.py` and `pdn_tools.py sea_zones` refuse to run on the map.
- **Region colours**: sea regions always blues, land regions never blue, cyan or indigo.
- **Land strategic regions are made from the nations** (`land_regions.py`, 2026-10-16), 137 of them.
- **Countries**:
  - Placeholders (one per continent) are left out once they own nothing; only Merlovich (AIS) is left.
  - Two starts on 1 January 2036: Valsora (Rouental, Merlovich) and the Vale of Reibonne (the Association's eight);
    two, because with one the game skips its scenario screen and Back loops.
  - Colours follow the flags (author); `pdn_tools.py recolour Countries OLD=NEW` keeps the `.pdn` in step.
  - **Every nation's record**, who drew, named and decided what and when, is `docs/NATIONS.md`. As built: 204
    countries in the mod, the 161 on the map and 43 that own nothing at the start (Rouental's 13 releasables,
    Belekria's 9 republics, Krionik's 3 principalities, 5 realms, Visokagorod (Sangrád until 2026-10-20), 3 ports and
    Formosa (the Gazetteer's), Pakitsk, the civil war's 7; the Sisterhood removed 2026-10-20); `dist/countries.md` lists them.
    Off the map but kept in `COUNTRIES`: the United States of Solitas and Russovichia.
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
      line), `owners` (every moved line at once).
    - A map colour comes from the flag where there is one, and moves off a neighbour's it would merge with. A flag
      that comes later doesn't change the colour unless the author asks.
    - Flags in another shape are fitted to 82:52 without stretching (`fit_flag.py`).
  - The adjectives of the neighbours are guesses; the author may rename them.
- **State names** are the author's, in `source/state_names.json` ("x,y" of a pixel inside the state, since ids shift);
  unnamed states are "Country N"; `state_map.py` numbers a country's states for naming.
- **Localisation keys are our own** (`VAL_STATE_n`, `VAL_REGION_n`); victory point names reuse vanilla's
  `VICTORY_POINTS_<id>` keys in `localisation/english/replace/`.

## Nation content, ideologies, cultures, superevents (in full: `docs/CONTENT.md`)

- **Rouental (ROU)** is the built-out nation: its states are its fiefs (2026-10-20; the ten Royal Fiefs all on the map since 2026-10-21, Aurifort and Brassard, and Rêverie the eleventh; the author's 13 groups applied the same day: 167 states, 216 provinces), capital Rêverie (`nations.CAPITALS`), Roland II Cahun and Serelle Cahun
  (`common/characters/ROU.txt`), a focus tree of five mutually exclusive paths (Polite, Kick Out Your Brother, Steady
  As She Goes, Rudely with Execute the Prince and the Rouentaise civil war, Accept Reality), the Association of
  Reibonnaise States, the Feudal Army spirit and the royal host (Elite since 2026-10-21; mechanized but the two armoured divisions and the 12th, motorized in Concorde), its 26 governorates (its
  strategic regions, a line on the state panel; HMMLA rises in all eleven Royal Fiefs); since 2026-10-21, night, the
  mockups in game, bare bones (`scripts/rouental_ui.py`): the Governorates category and its map of the realm, and the
  three powers (the Sacred Prince, the Voix Mahaut VI, the Speaker Tara Blanchart, democratic Rouental's leader) on the
  politics screen. Merlovich (AIS) has its own focus tree. Every other
  country has its set ruler, generated characters, the generic focus tree and a generic infantry army.
- **Gender**: HOI4 takes a character without `gender = female` for a man; the author's women carry it
  (`nations.GENDERS`, the hand-made blocks), the Gazetteer's characters by their page's choice; never from a name.
- **Every ruler is a set character** (author, 2026-09-30): `nations.LEADERS` gives each tag its sub-ideologies, the
  first leads; `cultures.leaders` makes them (`TAG_leader_<subtype>`, never `TAG_<subtype>`), names unique map-wide,
  famous surnames drawn again (`cultures.DRAW_AGAIN`). Named generated rulers: `nations.NAMED_LEADERS`.
- **`recruit_character` is ignored outside history files**: recruit every character in the country history.
- **Five ideologies** (`ideologies.py`): vanilla's keys, the author's names (`fascism` Authoritarian, `neutrality`
  Monarchist, `theocracy` new); sub-ideologies are the author's (`ideologies.SUBTYPES`), each description starting with
  its name; every `set_popularities` lists all five.
- **Map colours come from `common/countries/colors.txt`**; colour per government by cosmetic tags `TAG_GOV_<IDEOLOGY>`
  (never `TAG_<IDEOLOGY>`: its flag would clash on Windows, which ignores case).
- **Releasables**: `nations.RELEASABLE` (by state name), `nations.SUBREGIONS` (from the Subregions layer), cores on
  others' states `nations.CORES`, an owner without its core `nations.NO_OWNER_CORE`; subjects by `set_autonomy` (the
  mod's own Protectorate; the puppet level without its "no fascist overlord" clause).
- **Cultures** (`cultures.py`): generic portraits, name lists, graphical culture and scientists per continent and
  country, since vanilla's are keyed by Earth continents.
- **Superevents** (`superevents.py`, `superevents_deco.py`): TNO-style windows built from vanilla pieces; songs must
  belong to a music station; the Deco UI's board measures every text against its box.
- **Flags** are `source/flags/TAG.png` (any size; `TAG_<ideology>.png` while that ideology rules).

## The Gazetteer (`docs/GAZETTEER.md`; the working detail: `docs/GAZETTEER_INTERNALS.md`)

A web site, **https://rouental.github.io/Valsora-HOI4/**, where the author's friends fill in their own nations (author,
2026-10-14), each behind a password the author gives them: names and governments, rulers, party leaders, political
advisors, generals, admirals and other advisors with the base game's traits (commanders with their skill and stats),
companies of the base game's kinds (arms makers as military-industrial organisations and designers, industrial
concerns), flags, releasables, suggestions and requests, and what the game already has (the author's own characters,
as Roland and Serelle, and the releasables and civil war risers of `nations.py`), changed over the game's; once a
nation's states
are the author's own lines, its map facts too (state names and buildings, cities, terrain, rivers, railways, supply
hubs). `scripts/gazetteer.html` is the page (`gazetteer_site.py` builds the site, `facts_export.py` its map data); the
atlas is the author's Firebase project `valsora-hoi4` (Firestore). Read `docs/GAZETTEER_INTERNALS.md` before changing
the page, its rules or its import.
- **Rules that must hold:**
  - Never commit a password (they stay in `work/`) or the author's Google address: the Firestore rules
    (`source/gazetteer_site/firestore.rules`) say `OWNER_EMAIL`, and the author pastes them in the console with their
    address. After changing the rules, ask them to paste them again.
  - Without its password a nation can be neither listed nor changed (the rules allow `get` and `list` only inside a
    nation's folder, no `{path=**}`); `owner/*` is the admins' alone; only the author changes admins, and only the
    author starts over (Owner tools › Start over, asked twice; the rules keep `planned/reset` the author's).
  - Map tools wait for a nation's states (author, 2026-10-15: "once their state borders have been set in the mod, full
    customization would be unlocked"): `gazetteer.finals`, or `planned/unlock` set by the author; the import drops a
    closed nation's map facts.
  - Only the author's Claude publishes the site (`gh-pages`, allowed for it alone: "it's ok to put it on a new branch").
- **Republish** after map changes: `sh scripts/publish_site.sh "message"`; test the page first, after
  `python3 scripts/facts_export.py`: `python3 tests/gazetteer/run.py`, `traits.py`, `companies.py`, `ingame.py`,
  `reset.py`, `guide.py`, `stale.py` and `gender.py` (same folder).
- **Into the mod:** the author's **Save every nation as a file**, then `python3 scripts/gazetteer.py import FILE`
  (`source/gazetteer/<TAG>.json`, pictures in `source/gazetteer/assets/`, flags of HOI4's shape into `source/flags/`),
  a rebuild (`river_provinces.py` first after new rivers), `gazetteer.py suggestions` if there are any, and
  `gazetteer.py status`, which lists the open requests and what is left to do by hand: tell the author those. A
  nation's facts win over the `.pdn` and `nations.py` for that nation; hand-made characters (`HAND_MADE`) are changed
  where they are, within their ideology (`gazetteer.patch_characters`), and their copies (`nations.COPIES`) follow.
  Without facts the build is byte-identical. `GAZETTEER_DIR` / `GAZETTEER_FLAGS` point the scripts at other folders
  (tests: never import a test file into `source/gazetteer/`).

## Deco UI (`deco_ui/`): part of the mod (its manual: `deco_ui/CLAUDE.md`; its versions: `deco_ui/docs/VERSIONS.md`)

**The Valsora Deco UI** is the author's art deco interface, part of the Valsora mod since v0.5 (2026-10-14; author: "roll the UI mod into the main Valsora mod, but with the knowledge that I might eventually want it taken out again ... I'd like to simplify things to only have the one install"). Read `deco_ui/CLAUDE.md` before touching the UI. In short:
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
  (mutation-tested). Every letter of the mod's English text and name lists must be in every font in `gfx/fonts`
  (2026-10-16: Plaija's Vietnamese names; the fonts have Vietnamese since, composed where a face lacks it; the factory
  diamond, U+25C6, only in the value fonts that draw it; mutation-tested).
- Its `reference/` (the game's files, git-ignored) must never be committed: it is Paradox's content.
- **Now v0.12.3** (2026-10-21, later still: the commander pickers' foot buttons whole, the load and save windows' Back and Load apart, `deco_ui/tools/make_buttons.py`; the declare war window with the battle screen's crossed swords); before it v0.12.2 (2026-10-21: the 26 pictures traced from the game's art drawn by hand, `deco_ui/tools/fragments.py`'s
  check for broken gilt, the diplomacy focus icon inside its octagon, a row on the state panel for Rouental's
  governorate line; `deco_ui/docs/VERSIONS.md`); before it v0.12.1 (2026-10-20, later: the insignias in the picker, the faction logos centred, the diplomacy line, the goals' ground, the state panel's icons, the division list's corner, the railway icon, the loading diamond); before that v0.12 (2026-10-20: every note the author had held, seen that day); before that v0.11.2 (2026-10-19, later: the game's icons in the Deco style in the mod, approved, `deco_ui/tools/icons_art.py`; the diplomacy portrait as the politics screen's; the loading bar's diamond; the decision plates, the production resources, the decisions' icon wells; v0.11.1 of 2026-10-19, the music player and its controller, the production lines' boxes, the trade rows, seen the same day; v0.11 of 2026-10-18, night, the top bar's findings, diplomacy like politics, the panels' pictures and the decisions tab, seen 2026-10-19; v0.10.2 to v0.10.4 seen 2026-10-18). v0.9's restyled screens are one commit, `8dece16`: `git revert 8dece16` and a rebuild of both take them out. Previews that show the game's own art stay in the git-ignored `deco_ui/build/` and are only sent to the author. Proposals not in the mod, waiting for the author: `deco_ui/art/proposals/` (the larger flags: "don't add anything to do with it into the mod yet").

## Current state

Where things stand; the history, date by date, is `docs/HISTORY.md` (add each day's entry at its top).

- **The build** (2026-10-21): 21,136 provinces (20,748 land, 363 sea, 25 lakes), 62,322 province borders
  (HOI4 draws 65,536: 3,214 free, `docs/BORDER_LIMIT.md`), 3,300 states (Rouental's its fiefs since 2026-10-20, Aurifort cut out on 2026-10-21, the author's 13 groups the same day; 22 impassable, without supply hubs or troops: Usnistan's deserts and the
  Cultists' striped jungle, the
  author's areas layer, `scripts/areas.py`; one province each, as the base game's great deserts; their land and the yellow areas desert terrain, cut coarse), 206 strategic
  regions (164 land: 137 made from the nations on 2026-10-16, `land_regions.py`, not redone for the borders since, and
  Rouental's 27 governorate regions, 2026-10-21, `governorates.py`; 42 sea);
  419 strait crossings (none between the Illiriciums or to North Pollana); Belekria 1, 4, 5, 6 and 15 coarse as
  tundra; Sminishia's claims on West Sminishia's land (`nations.CLAIMS`); the land regions named (the drafts, 2026-10-20; the governorates the author's, 2026-10-21); 204 countries
  in the mod, 161 of them on the map (2026-10-19: Krionik's realms, Sangrád (Visokagorod since 2026-10-20) and its ports
  releasable; Xugang Terreich's puppet; the Sisterhood removed 2026-10-20: `docs/NATIONS.md`), 104 of those with a flag of their own (57 fly a stripe in their map colour); the
  states of 61 are drawn lines (`gazetteer.finals`, 2026-10-19; 49 on 2026-10-18; 39 until 2026-10-17's map: Belekria, Krionik, Terreich,
  Gorbastan, Zukchiva, Sennheiser, Sminishia, West Sminishia and Hollier joined; Ungar's six from the Gazetteer on
  2026-10-18). The four great powers, one per
  ideology but Theocratic (author, 2026-10-17): Krionik (Monarchist), Kampf (Authoritarian), Sarkis (Communist),
  Fraxhemark (Democratic); great in name for now (their industry is as drawn). Two starts, both on 1 January 2036. The Deco UI is v0.12.3 (`deco_ui/docs/VERSIONS.md`). Rouental's rivers run along its borders (97 % of their pixels, 2026-10-20: `river_borders.py`; map-wide 93 %, the other nations' stretches listed in `docs/MAP_PIPELINE.md`). The Royal Host forms on the first day (`on_startup`); every country has the game's Army HQ template. The Gazetteer shows players a quick-start guide the first time they unlock a nation, a state size guide (Cardonia's states the usual size, author 2026-10-18) before the province one, a button to hide suggestions, what each base-game trait does, and (2026-10-18, night) the neighbours' terrain.
  Rouental has test decisions for every kind of event, a test superevent and one that sets off many alerts at once
  (`test_events.py`).
  **The Gazetteer's facts are in the mod** (the author's export of 2026-10-20, night, 30 nations, `source/gazetteer/`;
  the 15 suggestions of 2026-10-18's put on the map by `apply_suggestions.py`), after the blank slate of 2026-10-16. `gazetteer_fetch.py` reads the site directly once the author adds a read-only service
  account's key as the secret `GAZETTEER_SERVICE_ACCOUNT` (`docs/GAZETTEER_INTERNALS.md`); until then their saved file. The Gazetteer offers the base game's traits for every leader and takes requests for new ones,
  and has political advisors and companies (arms makers and industrial concerns of the base game's kinds, with logos;
  requests for new kinds); since 2026-10-15 (later) it shows what the game already has, editable (the author's own
  characters with their stats; Rouental's 13 releasables, its civil war's 7 risers and Belekria's Tethia), commanders'
  skill and stats, and cities' size apart from their victory points (now labelled by importance). The test version with 1.5 times larger flags is built beside the mod by
  `sh scripts/build_flags15.sh` and sent as its own zip (`docs/HD_FLAGS_TEST.md`), not put into the mod.
- **Tonight's tools and pages** (2026-10-17, the second night; `docs/WORKFLOW.md`): a map update is now `pdn_check.py`,
  `pdn_diff.py`, `pdn_tools.py owners`, `regroup_states.py --recut`; the Gazetteer has a province size guide; the
  Valsora Atlas (the build in a browser, a private Artifact: `docs/ATLAS.md`). Proposals made the same night, not in
  the mod: the tech tree's full mockup (`docs/tech_tree_mockup/`), a world map poster (`dist/posters/`), the Deco UI's
  next screens (`deco_ui/art/proposals/next_screens/`).
- **Seen in game last** (2026-10-22): the governorates and the three powers, bare bones ("Looks great so far"): the
  Open button's text barely readable on its gold, the map clicked only at the seals ("I can't click on Rivage d'argent
  anywhere but the badge"), the marker out of place, the zone's text cut: all changed the same day, with the Terres
  Séparées' peoples (`rouental_realm.STATE_PEOPLES`), not yet seen. Before that (2026-10-21, later): v0.12.2 and the build of 2026-10-21, later (the author's notes and
  screenshots): the governorate line works, the Royal Host Elite, the Army HQ cards work; the commander pickers' foot
  buttons cut off, the load window's Back and Load run together, the declare war window's emblem wanted as the battle
  screen's swords, two of Earth's flags in error.log: all changed in v0.12.3 and the build of 2026-10-21, later still,
  not yet seen. Before that (2026-10-21): v0.12.1 (the author's screenshots): the Army HQ card's gilt broken (and "weird
  sloppy lines and missing pieces of the design" in much else of late), the Royal Host below Elite, the diplomacy tab's
  focus icons past their octagon: all changed in v0.12.2 and the build of 2026-10-21, later, not yet seen. Before that
  (2026-10-20): v0.12 (the author's screenshots): the faction logo off centre (top bar and faction screen), a line's remains above the diplomacy portrait, the faction goals without a solid ground, the state panel's icons off centre, the division list's corner past the chamfer, the insignias missing from the picker, the railway icon, the loading diamond, the Royal Host still short of experience, the Army HQ designer that would not save, the rivers through Rouental's provinces, Mekele's cut: all changed in v0.12.1 and the map 10-20-2, not yet seen. Before that (2026-10-19, evening): v0.11.2, the author's notes held until their go-ahead ("do not fix these or
  anything else I send until I give you the go-ahead"): `deco_ui/docs/VERSIONS.md`, "Held". Before that (2026-10-19, later): v0.11.1: the loading bar's diamond half cut off, the diplomacy portrait unchanged and a cut-off bar over its actions, the icons not yet in (approved then): all changed in v0.11.2, with the notes held from v0.11 (the decision plates, the resource counts, the decisions' icons); the faction screen's "odd appearance" asked about; the theocracy token warning explained, not changed. Before that (2026-10-19): v0.11: the music player and its controller, the trade rows' specks and the production lines without boxes, fixed in v0.11.1 (not yet seen); the faction screen, the diplomacy portrait, the decision plates a little high, the production screen's resource counts and the decisions' icons noted, waiting ("Do not act on the following yet"). Before that (2026-10-18, night): v0.10.4 (the factories' colours, the decision plates a pixel low, the logistics numbers crowded, the music button, the diplomacy and intel tabs, the panels' drafts, the decisions tab, the focus filters' icons: all changed in v0.11, not yet seen). Before that (2026-10-18, later) the Deco UI v0.10.2: the decision counts still round dots in the
  shoulders, not the shoulder-shaped plates the author had outlined: plates in v0.10.3, not yet seen. Before that
  (2026-10-18) v0.10.1 (the author's screenshots and a mockup of the medallion):
  the Release Nation window's list over its checkboxes, eight faction flags a row with room for more, the events'
  corner brackets ("you have a lot of trouble with this particular decorative element"), the factories' order, the
  state panel's corner under the flag, the experience badges off centre, the medallion's name 1 px left: all changed
  in v0.10.2, not yet seen. Before that (2026-10-17) v0.10's findings, fixed in v0.10.1. Older findings, all fixed since: `deco_ui/docs/VERSIONS.md`. Not seen yet besides: the two starts, Vilna and Placeholdgrad. The Deco UI's checklist for the author is in `deco_ui/valsora_deco_ui/README.txt` (Things to check) and `deco_ui/CLAUDE.md` (section 10).
- **Waiting on the author:** (`dist/open_questions.md`, 2026-10-21, later still; keep it in step) everything they had
  answered or held is in the mod (2026-10-20, their go-ahead; 2026-10-21, the governorates' names, the generic
  advisors, the Kufi in gold, HMMLA's Royal Fiefs, Rouental's groups, Montvallée, Rêverie, the Royal Host, Kalaistan).
  New: the governorates' window and the three powers in game, bare bones (2026-10-21, night, seen 2026-10-22: what to
  see in game in `docs/CONTENT.md`, Rouental; the zones' effects and the decisions still placeholders); Guedelon's
  Council of Six's portrait, A in the mod, B or C (`dist/portrait_proposals/guedelon_council_of_six/`, 2026-10-22); the Vale of Reibonne's region left with Guedelon and Brillagne apart; whether the groups stay (the way back:
  `work/pre_groups_1021/`, or the commit before them). Open: the strait crossings to add from the red ones
  (`dist/straits_map_red.png`); the old upload's tundra, jungle and desert marks ("I'll add those back in later");
  flags for Belekria's eight republics and state names (later, the author's); the region names (the drafts in the mod
  "for now"); the tech tree ("not really ready"); more groups on the grouping map when the author wants them (a private
  claude.ai page, `scripts/province_picker.py`; the groups read back with ArtifactData); the Governorate Lines ("Eventually I will get
  around to the Governorate Lines"; then `governorates.py --apply` again) and the levies they will hook into. To look at: Rouental's 165 fief states and their names (two Vedettes), the releasables' carried-over land, the
  Gazetteer page's old state populations (shared out in the mod, `gazetteer.rekey`), the Deco UI v0.12.3's Things to
  check (and v0.12's: the alerts' row an assumption). Rouental's border edits of 10-18-3 (a city state in the east, cutouts for
  Vair, Carcarelle and Grande Reliette) come with the author's new map. Settled: the desert provinces' size ("a good
  size"), Claude's guesses for the eleven nations of 2026-10-19 ("good for now"), the Gazetteer on the download, fuel,
  supply and convoys in the top bar, v0.9's screens, the flags at their size; (2026-10-15) the news masthead VALSORAN
  STANDARD, its ringed globe, the event cards' keystone; the zip in `dist/`.

## Known gaps

1. **States**: 100 of the 161 nations on the map (2026-10-19) have states Claude cut from their
   outlines (`apply_outlines.py`, about 1,300 px each), not lines of the author's; their Gazetteer map tools stay
   closed until the author draws them. The old `.pdn`'s country colours, moved to the new layout, are its Notes
   layer.
2. **Terrain** is plains everywhere; there are no trees, and the
   relief is noise. A generated terrain (with its own relief) exists as a test only, `terrain_test.py`
   (2026-10-12): the author said not to add it to the mod yet. It follows the author's geography where they gave
   it (the Vale of Reibonne). Rivers are only where the author or their friend drew them; railways wait (the
   author, 2026-10-15): there are none.
3. **Country content**: Rouental (leaders, focus tree, civil war, royal host) and Merlovich (focus tree) are built
   out; every other country has its set ruler, generated characters, the generic focus tree and a generic infantry
   army. Generic portraits and name lists exist (see Cultures), scientists' too since 2026-10-14.
4. **What still reads as the 1940s**: the tech tree's names, descriptions and pictures (its dates are 2036's;
   `docs/TECH_TREE_2036.md` is a proposal), the 3D models, and the game's own pictures inside the side panels (the
   Deco UI's proposals wait for approval).
5. **Province borders**: 3,214 left under HOI4's limit (62,322 of 65,536, 2026-10-21: Rouental's fiefs took 291, its rivers 3, Aurifort 3, its 13 groups gave back 36; the
   coarse deserts gave back 1,368 on 2026-10-18), for the states still to be drawn (`docs/BORDER_LIMIT.md`).

## Working with the author

**Keep `docs/PROBLEM_LOG.md` up to date** (author, 2026-09-30): every error or problem,
its cause and its fix, newest first.

**Every time the author sends a `.pdn`, send `source/HOI4 Mod Map.pdn` back when done**
(author, 2026-09-30), so their copy has every edit. Their upload may be based on an
older version (the 2026-09-30 one predated the sea zones and recolours): diff its game
layers against `source/` first, and merge, keeping the current game layers and taking
their own layers (outlines, rivers, names, references) from the upload.

**Send the map dated** (author, 2026-10-18: "start dating the map as you send it. If the map changes multiple times in
a day, do something like 10/17-2, 10/17-3"; they keep the copies as backups): a copy named for the day the map last
changed, `HOI4 Mod Map 10-17.pdn`, then `10-17-2`, `10-17-3` for later versions that day; the repository's file keeps
its plain name. `docs/MAP_VERSIONS.md` lists every name sent with its fingerprint, so an unchanged map keeps its name
and the next number is known.

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
