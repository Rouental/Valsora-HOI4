# Primer: building a Hearts of Iron IV mod (for Claude)

You are about to help someone build or extend a Hearts of Iron IV (HOI4) mod. This
primer distils what one long project (Valsora, a total-conversion map, game version
1.19.3) learned the hard way. Every rule marked **verified** was confirmed against the
base-game files or by the game itself crashing or logging an error. Treat the rest as
strong defaults.

You usually cannot run the game. The person tests it and sends back screenshots and
`error.log`. So your job is to produce files that are right the first time, check
them yourself, and say exactly what changed and how to install it.

---

## 1. How to work

- **Generate, don't hand-edit.** Write scripts (Python + numpy/scipy/pillow work well)
  that produce every mod file from editable sources, such as a paint program file, JSON
  or Python tables. Rebuilding should be one command and deterministic.
- **Write a checker and treat a clean run as the bar for shipping.** Re-read the
  built files and check every rule in section 4. Mutation-test it: break a file on
  purpose and confirm the checker catches it.
- **Keep the person's own data by position, not by id.** Province, state and region
  ids shift whenever the map changes. Store names, capitals and similar by a map pixel
  `(x, y)` inside the thing, and look the id up at build time. Stop the build if a
  pixel lands in no object, or two names land in one.
- **Keep a problem log** (cause → fix, newest first) and a project notes file
  (CLAUDE.md) recording every decision and *who* made it. Mark what the author chose
  and what you guessed, so guesses can be revisited.
- **Change only what was asked.** Don't regroup, recolour or "improve" things the
  person didn't mention. That caused a rejected revision in this project.
- **When you guess** (a colour, a culture, a tag, an ideology), say so in your reply.
- **Every reply after a build**: list the files changed and repeat the install steps:
  1. Delete `Documents/Paradox Interactive/Hearts of Iron IV/mod/<name>/` and `<name>.mod`.
  2. Unzip the new zip into `mod/` (it holds both the folder and the `.mod` file).
  3. Launch with `-debug`. Map errors crash on launch without it, and with it they go
     to `error.log` instead.
- **Ask before** large or destructive steps, and before taking in a third party's work
  (a friend's files, another mod's assets).

---

## 2. Mod skeleton

```
mod/
  <name>.mod                 launcher file: same lines as descriptor.mod + path="mod/<name>"
  <name>/
    descriptor.mod           name, version, supported_version="1.19.*", tags, replace_path lines
    thumbnail.png
    common/ history/ map/ localisation/ gfx/ interface/ events/ ...
```

- **Ship both `descriptor.mod` and the outer `<name>.mod`, with identical content**
  (verified). The launcher reads the outer one.
- **`replace_path="history/states"`** and the like stop the game loading the base
  game's folder of that name. A total conversion typically replaces `history/states`,
  `history/countries`, `history/units`, `history/general`, `map/strategicregions`,
  `events`, `common/decisions`, `common/ai_strategy`, `common/ai_strategy_plans`,
  `common/on_actions` and `common/bookmarks`. Keep at least one valid file in each
  replaced folder.
- **Overriding a single file**: ship a file with the same path and name.
- **Load order**: a mod that lists another under `dependencies={ "Exact Mod Name" }`
  loads after it, so its files win. Use this for submods and compatibility patches.
- **Leftover base-game content that names Earth places** has to be emptied or cut down
  for a new map. Examples: `tutorial/tutorial.txt`, and the 21
  ENG/FRA/GER/ITA/JAP/SOV/USA files in `common/ai_navy/{goals,fleet,taskforce}`. Base
  ideas, MIOs, scripted effects and achievements that reference missing ids only add
  noise to `error.log`, which the game tolerates.

---

## 3. Text formats

- **Paradox script** is `key = value` and `key = { ... }`, with `#` comments. Write it
  with tabs, one statement per line.
- **Localisation** is `localisation/english/<anything>_l_english.yml`, **UTF-8 with
  BOM** (verified). The first line is `l_english:`, then lines of the form
  ` KEY:0 "Text"`. Files under `localisation/english/replace/` win over the base
  game's keys; use that folder when you must redefine a base-game key, such as
  `VICTORY_POINTS_<id>` or ideology names.
- **Name lists** (`common/names/*.txt`) are UTF-8 *without* BOM, like the base game's.
- **`map/definition.csv` needs CRLF line endings** (verified).
- **Watch for case-insensitive filename clashes on Windows**, for example
  `ROU_COMMUNISM.tga` versus `ROU_communism.tga`. Check for them.

---

## 4. The map (verified against 1.19.3)

### Size
- Both sides must be multiples of 256, and the area must stay under about 13,238,272 px.
  The base game is 5632×2048. 5120×2560 works and is the largest 2:1 size.
- `provinces.bmp`, `heightmap.bmp`, `terrain.bmp`, `rivers.bmp` and `cities.bmp` must
  all be exactly the map size.

### Files
| file | format and rules |
|---|---|
| `provinces.bmp` | 24-bit, 40-byte BITMAPINFOHEADER (no V4/V5), under 40 MiB. Each province is one 4-connected blob of ≥ 8 px (use 16 for headroom), with a bounding box under 1/8 of the map each way. **No 2×2 window may contain four different provinces ("X-crossing")**; the check wraps across the left/right seam. |
| `definition.csv` | CRLF. First row `0;0;0;0;land;false;unknown;0`. Ids contiguous from 1: `id;R;G;B;land/sea/lake;coastal;terrain;continent`. Land continent ≥ 1; sea and lake continent 0. Terrain e.g. `plains`, `ocean`, `lakes`. |
| `heightmap.bmp` | 8-bit greyscale. The water plane is 95 (`WATER_HEIGHT = 9.5`): land must be > 95, water < 95. |
| `terrain.bmp` | 8-bit, the base game's palette. Index 0 = plains, 15 = ocean (use 15 for lakes too). |
| `rivers.bmp` | 8-bit palette. 255 = land, 254 = water. Rivers are 1 px wide and edge-connected only. Each river system has exactly one green source pixel; red marks where a tributary flows in. Width index ≥ 7 is a large river. |
| `cities.bmp` | Map-sized. Index 4 belongs to no city group, so no town meshes appear. |
| `trees.bmp` | Any size (the base game's is 75/256 of the map). |
| `world_normal.bmp` | 24-bit; flat = (128,128,255). The base game's is half size; any size loads. |
| 8-bit BMPs | With a full 256-colour palette, write `biClrUsed = 0` as the base game does. Writing 256 logs "Palette … probably not correct". |
| `map/terrain/colormap_rgb_cityemissivemask_a.dds`, `fow_rgb_waterspec_a.dds` | Half map size. |
| `map/terrain/colormap_water_0/1/2.dds` | 1/2, 1/4 and 1/8 map size. Uncompressed A8R8G8B8 with one mip loads fine. **DDS rows run top-down; BMP rows run bottom-up.** |
| `buildings.txt` | `state;type;x;height;z;rot;adjacent_sea`, with z = map height − pixel y. **No trailing empty line** (it reads as a malformed row). |
| `unitstacks.txt` | Land provinces need types {0,1,9,10,21,22,38}; sea provinces need {0,1,2,9,10,11,12,21,22,23,30,31,38}; lakes need none. |
| `weatherpositions.txt` | One `small` and one **`big`** row (not "large") per strategic region. |
| `adjacencies.csv` | Keep the `-1;-1;;-1;-1;-1;-1;-1;-1` end line. |
| `ambient_object.txt` | Frame positions follow the map height: top frame at H+142, logo at H+82. |

### Buildings needed (`buildings.txt`)
- **Per state:** air_base, anti_air_building ×3, arms_factory ×6, industrial_complex ×6,
  fuel_silo, nuclear_reactor_spawn, radar_station, rocket_site_spawn (also used by
  rocket_site and mega_gun_emplacement), stronghold_network, synthetic_refinery, plus
  dockyard if the state is coastal.
- **Per land province:** bunker, special_project_facility_spawn, supply_node.
- **Per coastal province:** naval_base_spawn and floating_harbor (both naming the sea
  province), naval_headquarters, naval_supply_hub, coastal_bunker.

### States and strategic regions
- Every province is in exactly one strategic region. A state's provinces all share one
  region. Naval regions must be contiguous. State and region ids are contiguous.
- Supply nodes and railways go only on provinces that are in states.
- Use your own localisation keys (`VAL_STATE_n`, `VAL_REGION_n` or similar), so the
  base game's Earth names (`STATE_n`) never show.
- Victory-point names must reuse the base game's `VICTORY_POINTS_<province id>` keys, so
  put them in `localisation/english/replace/`.

### Building a map from a drawing
- Read the source drawing directly. A paint.net `.pdn` is `PDN3` + a 3-byte header
  length + an XML header, then a .NET BinaryFormatter graph, then per layer gzip chunks
  of BGRA pixels. Keep **one layer per kind of data** (heightmap, terrain, provinces,
  states, countries, regions, rivers…), found by layer name, at exactly game size, so
  the author edits game data directly.
- **Decide everything per province by majority** of its pixels (kind, terrain, state,
  owner, region). Blank areas take the nearest painted area, with a note.
- **Repair X-crossings automatically** by moving single pixels. Report real errors
  (split or tiny provinces, transparent pixels, a state in two regions) as a numbered
  list of `(x, y)` positions the author can find.
- **Shrinking a drawing fuses islands and closes straits.** Trace the water's centre
  line at source resolution and keep it open.
- **Rivers drawn by hand** need converting: skeletonise them, pick the mouth nearest
  water, give side branches flow-in pixels, add a corner to each diagonal step, drop
  stubs under ~6 px, and join tributaries that stop short.
- **River penalties only apply across a province border**, so cut provinces so that
  rivers run between them.
- **Organic province borders**: k-means seeds, then a compact watershed over fractal
  noise. This looked far better than square bricks.
- **The author's own state lines are sacred**: never split a state they drew. Small
  gaps in their lines (a missing pixel, a line stopping short of the coast) merge
  areas. Detect dead-end line pixels and fill them.
- Don't let a script run quadratically over the whole map. Process each object inside
  its bounding box (`scipy.ndimage.find_objects`).

---

## 5. Countries

- **Tags** are three letters. **Check every new tag against the base game's
  `common/country_tags/00_countries.txt`** (PAP, VIN, SOL and others are taken).
  Reusing a base-game tag pulls in its flags, localisation and file; avoid it unless
  that is the point.
- Per country you need:
  - `common/country_tags/<file>.txt`: `TAG = "countries/<Name>.txt"`;
  - `common/countries/<Name>.txt`: `graphical_culture`, `graphical_culture_2d` and `color`;
  - `history/countries/TAG - <Name>.txt`: capital (a state id), politics,
    popularities, starting characters, OOB and so on;
  - localisation: `TAG`, `TAG_DEF` (formal name), `TAG_ADJ`, and per-ideology
    variants `TAG_<ideology>`, `TAG_<ideology>_DEF` and `TAG_<ideology>_ADJ`.
- **Map colours come from `common/countries/colors.txt`**, not from the country
  file's `color` (verified). A tag missing there gets a random colour. Write `color`
  plus a lighter `color_ui` for every tag.
- **Flags**: `gfx/flags/TAG.tga` (82×52), `gfx/flags/medium/TAG.tga` (41×26) and
  `gfx/flags/small/TAG.tga` (10×7). Use 32-bit uncompressed TGA with a bottom-left
  origin. `TAG_<ideology>.tga` is used while that ideology rules.
- **Cosmetic tags** (`common/countries/cosmetic.txt`, `set_cosmetic_tag`) change the
  name, colour and flag per government. Name them `TAG_GOV_X`, not `TAG_<ideology>`,
  to avoid flag filename clashes. Set or drop them from an `on_ruling_party_change`
  on_action.
- **A country that owns nothing at the start but can be released**: give it cores on
  its states in `history/states` (`add_core_of = TAG`), plus a country file, history
  file and flag. It can then be released by hand, or by script with `release = TAG`.
- **Subjects** go in the overlord's history:
  `set_autonomy = { target = X autonomous_state = autonomy_puppet }`. Dominions use
  `autonomy_dominion`.
- **Factions in 1.19**: `create_faction_from_template = <template>` plus
  `add_to_faction`, with the template in `common/factions/templates/`. A member needs
  about 30 % support for the leader's ideology (`IDEOLOGY_JOIN_FACTION_MIN_LEVEL`), or
  it leaves at once.
- **Opinion modifiers** (`common/opinion_modifiers/`) need a localisation key equal to
  the modifier id, or the raw key shows.

---

## 6. Characters, leaders and ideologies

- **Characters** live in `common/characters/<TAG>.txt`, with roles such as
  `country_leader = { ideology = <sub-ideology> }` and `corps_commander = {...}`.
- **`recruit_character` only works in history files** (verified; elsewhere it logs
  "should only happen in game/history files"). Recruit every character the country
  will ever use in its history file. Switch them later with `promote_character`,
  `retire_character` or `remove_country_leader_role`.
- **Never id a character `TAG_<sub-ideology>`.** The game reads that as the country's
  name under that sub-ideology, so the leader's name appears on the map (verified).
  Use something like `TAG_leader_<sub-ideology>`.
- **Give every country a recruited leader of its ruling ideology**, and check this.
  Otherwise the game generates one, which works but logs "failed to generate a name or
  portrait" when name lists or portraits are missing.
- **Portraits**: a 156×210 DDS sprite declared in an `interface/*.gfx` spriteType
  (`GFX_portrait_<name>`) and referenced from the character.
- **Ideologies** (`common/ideologies/00_ideologies.txt`): overriding the base game's
  file lets you rename, recolour or add ideologies.
  - Keep the base game's keys (`democratic`, `communism`, `fascism`, `neutrality`) so
    base-game script keeps working, and rename them through
    `localisation/english/replace/`.
  - A fifth ideology fits only if `interface/countrypoliticsview.gui` gets shorter
    party rows (13 px instead of 16).
  - Every `set_popularities` must list every ideology and sum to 100.
- **Base-game portrait and name lists are keyed by Earth continents.** A new map's
  continents need their own `portraits/*.txt` blocks (built from the base game's
  generic sprite names) and `common/names` blocks. Otherwise you get "unknown continent
  europe" and "Failed to generate a portrait/name".

---

## 7. Armies and economy

- `history/units/<TAG>_1936.txt` holds division templates and units, loaded by
  `set_oob = "<TAG>_1936"` in the country history. **OOB divisions take their men from
  the country's manpower pool** (verified: armies started empty), and
  `start_manpower_factor` did not prevent it. So give the country enough population,
  or `add_manpower` before `set_oob`.
- Grant the techs each template's units need in the history file before `set_oob`.
- State population (`manpower` in the state history) sets everything downstream. Scale
  it to a believable world total.

---

## 8. Focus trees, events and GUI

- **Focus tree**: `common/national_focus/<file>.txt`, picked per country with
  `country = { factor = 0 modifier = { add = 10 tag = TAG } }`.
  - Use `mutually_exclusive`, `prerequisite`, `x`/`y` and `cost`.
  - Use only icons that exist (check the base game's `interface/goals.gfx`).
  - Localise every focus id and its `_desc`.
- **Custom pop-up windows**, like TNO-style "superevents", can be built from base-game
  pieces:
  - a `player_context` scripted GUI shown while a country flag is set;
  - scripted localisation keyed on global flags;
  - an icon per picture with `<element>_visible` triggers;
  - a close button whose `_click` clears the flag.
  - `GFX_tiled_window_transparent` is see-through, so ship your own background DDS.
  - Typewriter fonts draw dark; colour text with `§W…§!`.
- **Music**: `play_song = "<song>"` only works if the song belongs to a music station:
  - `music/<station>/` holds the `.ogg` (Vorbis), `<station>.asset` with
    `music = { name file volume }`, and `<station>.txt` with `music_station` and the
    songs (chance 0 keeps them out of the radio);
  - plus a station GUI (`<station>_faceplate`, `<station>_stations_entry`), a
    two-frame cover sprite, and localisation for the station title and each song.
- **Check every reference** in the checker: scripted effects, events, songs, sprites,
  GUI elements, localisation keys, and focus ids and prerequisites.

---

## 9. Map graphics (look and feel)

- Graphics defines live in `common/defines/*.lua`:
  - `NDefines_Graphics.NGraphics.GRADIENT_BORDERS_THICKNESS_COUNTRY_LOW/HIGH` set how
    far country colour spreads in from borders (huge values fill whole countries);
  - the `*_CUTOFF` values set draw distances;
  - `MAP_MODE_TERRAIN_TRANSPARENCY` and similar.
- Base-game map shaders (`gfx/FX/pdxmap.shader`, `pdxwater.shader`, `river.shader`)
  read the map size from the engine (`MAP_SIZE_X/Y`), so shader-based graphics mods
  are usually size-independent. Only their colormaps are drawn at a fixed size.
- To use another author's graphics mod with a differently sized map, **don't copy its
  files**. Ship a small patch that `dependencies` on it and supplies only the
  map-size-dependent files (colormaps, world_normal) at your size. Redistributing
  someone else's assets needs their permission.

---

## 10. Before you ship: checklist

1. The build runs end to end from sources with one command.
2. The checker passes, covering at least everything in section 4 plus localisation,
   characters, flags, ideologies, popularities, focus references, GUI references and
   file-name clashes.
3. `descriptor.mod` matches the outer `.mod`, and the zip contains both at the top
   level.
4. You looked at a rendered preview of anything visual you changed, such as maps,
   flags and portraits. Generate PNG previews and view them.
5. The problem log and notes file are updated.
6. Your reply says what changed, which files, what you guessed, and the install steps.

## 11. Reading error.log

- The person runs with `-debug` and sends
  `Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log`.
- Group the lines by source file. Lines about base-game content you left loaded
  (decisions, ai_faction_theaters, missions referencing Earth ids) are usually noise.
- Lines about your map files, your characters or your localisation are real. Fix them,
  then add a check so they can't come back.
