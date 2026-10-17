# The Valsora Atlas

The last build's world in a browser (2026-10-17): pan and zoom the whole map, switch between map modes, hover
for any province's facts, click a nation, state or region for its card, and search. It lets the author check a
build in seconds instead of launching the game. **It is not part of the mod.** It only reads the build, and nothing
in `run_all.sh`, `build/` or `dist/` depends on it.

- `scripts/atlas_export.py` writes the data into `work/atlas/` (git-ignored).
- `scripts/atlas.html` is the page. It loads the data files by relative path, from beside itself.

## After a build

    python3 scripts/atlas_export.py                 # about 20 s
    python3 scripts/atlas_export.py --changes-only  # only compare work/atlas/ with work/atlas_prev/ again

Each run moves the previous export to `work/atlas_prev/` and writes `changes.json`, so the page can show what
changed since the export before. Run it after every build you want to compare. Two runs on the same build show no
changes. The export reads (and never writes) `work/provinces.npz`, `regions.npz`, `regions.json`, `world.npz`,
`game_releasables.json`, `work/terrain_test/` when it is there, and `build/valsora_test/`: state and country
histories, localisation, `colors.txt`, flags, characters, portraits, strategic regions and `adjacencies.csv`.
It reuses the readers of `country_list.py` (names, government, ruler, culture), `facts_export.py` (state
buildings, victory points), `nation_sheet.py` (map colours, rulers' portraits) and `collages.py` (continents).

| file | holds | size (2026-10-17) |
|---|---|---|
| `prov.png` | every map pixel's province, its index + 1 as 24-bit RGB (0: none) | 1.2 MB |
| `rivers.png` | the rivers, rivers.bmp's code + 1 (0: none), greyscale | 18 kB |
| `shade.png` | the build's heightmap as a hillshade, half size | 0.7 MB |
| `terrain_test.png`, `terrain_shade.png` | the terrain test's classes per pixel and its relief (only with `work/terrain_test/`) | 0.8 MB |
| `flags.png` | every nation's flag at 82 x 52, a sheet of 16 columns | 0.4 MB |
| `portraits.jpg` | the rulers' portraits of our own (the base game's are Paradox's and are left out) | 30 kB |
| `provinces.json` | per province, by column: kind, state, region, size, anchor pixel, terrain, coast, layer colour | 0.7 MB |
| `atlas.json` | nations, states, regions, cities and victory points, the Subregions layer's parts, counts, file list | 1.5 MB |
| `changes.json` | what changed since `work/atlas_prev/` | small |

Ids in the files are the build's indices from 0. The page shows the game's numbers, one more: province 4752,
state 694, region 36.

**How changes are found.** Province ids shift whenever the map changes, so the two exports are compared pixel by
pixel. A province has a *new owner* when most of its pixels had another owner before. It has a *new state* or *new
region* when most of its pixels were in a state or region other than the one its own matches. States and regions
are matched one to one, by overlap, with a shared name counting extra. A province is *redrawn* when no old province
covers 90 % of it. States without a match are *added*, old states left over are *removed*, matched ones with
another name are *renamed*, and nations added or removed are listed with those now on or off the map.

## The page

| mode | shows |
|---|---|
| Political | nations in their map colours (`colors.txt`), nation and state borders, nation names along their land |
| States | each state in a colour unlike its neighbours'; names, then the game's numbers, as you zoom in |
| Provinces | the Provinces layer's colours, state borders over them; province numbers from x3.5 |
| Regions | strategic regions in their layer colours (land never blue, sea always), named |
| Releasables | land holding another nation's core in that nation's colour; the Subregions layer's parts in gilt lines; "Show its cores" on a card shows one nation's cores alone |
| Cities | the cities of the Cities layer and every victory point (stars for capitals, diamonds for cities, small marks for a state's own) |
| Terrain | each province's terrain in the build (plains everywhere for now), shaded by the build's heightmap |
| Terrain test | **a proposal, not in the mod**: `scripts/terrain_test.py`'s terrain (2026-10-12) with its relief; land added since is hatched |
| Changes | provinces with a new owner, state or region, or redrawn, since the export before; a card lists the hand-overs (click one to fly to its provinces) and the states and nations added, removed and renamed |

- **Rivers** and **Names** can be switched off in the key (lower left; "Key" on a phone). The rivers show their
  sources in green and the points where tributaries join in red, as rivers.bmp has them.
- **Hover** gives the province, its state and number, owner, region and terrain, the mode's own facts (cores,
  victory points, the change) and the map pixel (x, y), the coordinates `nations.py` and the `.pdn` use.
- **Click**: in the political mode a nation's card, in the regions mode a region's, elsewhere a state's.
  Shift-click opens the other one. Cards link to each other (owner, cores, neighbours, region, states).
- **Search**: nations (name, formal name, tag, adjective), states, cities, regions; also `s694` (a state),
  `p4752` (a province), `r36` (a region) and `660,805` (a map pixel).
- **Keys**: `+` and `-` zoom, `0` shows the whole world, `/` searches, arrows pan, Esc closes the card.
- **Links**: `#ROU`, `#s694`, `#r36` or `#p4752` at the end of the page's address opens that card.
- **Touch**: drag to pan, pinch to zoom, tap for a card. On a phone the card is a bottom sheet (tap its grip to fold
  it).
- The look is the Deco UI's (`deco_ui/CLAUDE.md` section 5): lacquer panels and gilt rules in dark mode, an ivory
  sheet in light mode, Federo and Josefin Sans from Google Fonts. The map wraps left to right like the game's and
  shows crisp pixels from x1.

## Publishing

The atlas is published as a **private claude.ai Artifact**, https://claude.ai/artifact/A7dYCWMREAUUAH1B57toWg
(first published 2026-10-17): the page plus the data files, served side by side at the same names (flat, no
folder). Only the author can open it until they share it. A publish of the Artifact tool would be:

    file_path: scripts/atlas.html
    files:     every file in work/atlas/ at its own name (atlas.json, provinces.json, changes.json, prov.png,
               rivers.png, shade.png, flags.png, portraits.jpg, terrain_test.png, terrain_shade.png:
               atlas.json's "files" lists them)
    icon:      map

After a new export, republish to the same artifact (the same `url`) with the new files. Each file is well under the
Artifact's 15 MB limit; the set is about 5 MB.

To look at it locally, serve a folder holding the page and the data (the page fetches its files, so `file://`
won't do). The page has no doctype of its own (the Artifact adds one when it publishes), so give the copy one:

    mkdir -p /tmp/atlas && cp work/atlas/* /tmp/atlas/
    { echo '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
      cat scripts/atlas.html; } > /tmp/atlas/index.html
    python3 -m http.server -d /tmp/atlas 8000      # then open http://localhost:8000/

## Limits

- Labels are placed from each piece of land's longest run through its deepest point, so a curved or ragged nation
  gets a straight, sometimes short, label.
- Only portraits of our own are shown; rulers with a base-game portrait get their initials.
- The terrain test was made on the map of 2026-10-12, so land added or moved since then is hatched or shifted.
- The page holds the whole map in memory, roughly 150 MB of arrays and canvases. Desktop and phone browsers manage
  it; the first load takes 2 to 3 seconds (headless Chromium, 2026-10-17).
