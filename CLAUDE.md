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

## Rebuilding

`sh scripts/run_all.sh` from the repo root: about 2.5 minutes, plus about 2 minutes for the
one-time `.pdn` decode. Needs `numpy scipy pillow scikit-image`. Output is deterministic.

| step | does |
|---|---|
| `readpdn.py` | decodes the `.pdn` into one RGBA `.npy` per layer |
| `blocks.py` | land mask, groups landmasses into continent blocks, removes Antarctica |
| `layout.py` | scales every block and pushes them apart |
| `compose.py` | game-resolution land / ocean / lakes, continent per pixel |
| `provinces.py` | brick provinces, sliver merging, X-crossing repair, validation |
| `regions.py` | states, strategic regions, anchor points |
| `build_mod.py` | every mod file |
| `check_mod.py` | re-reads the built files and checks every rule below |
| `export_canvas.py` | drawing canvases and previews in `dist/` |
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
- **Islands under 16 px are dropped and ponds under 64 px filled.** About 660 islets go
  this way; they are 1–4 px specks at game scale.
- **Enclosed water becomes lakes**, including the author's inland seas (Piscary, Norlany,
  Sasurs). If they should be navigable, they need to become sea provinces in their own
  naval regions.
- **States** bucket land provinces on a 96 px grid per continent, split into connected
  pieces; small island pieces join the nearest state within 160 px. **Land regions**
  bucket whole states on a 384 px grid; **sea regions** bucket sea provinces on a 512 px
  grid and must stay contiguous. Lakes go into the land region they border most.
- **Countries**: one placeholder per continent. Tags are NSC ARS AIS SLT YAS USN ORI;
  `SOL` is a vanilla tag, so Solitas is `SLT`.
- **Localisation keys are our own** (`VAL_STATE_n`, `VAL_REGION_n`), so vanilla's
  `STATE_n` / `STRATEGICREGION_n` Earth names never show. Victory point names have to
  reuse vanilla's `VICTORY_POINTS_<id>` keys, so they live in `localisation/english/replace/`.

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

## Current state

- 5,138 provinces (4,453 land, 613 sea, 72 lakes), 548 states, 128 strategic regions
  (81 land, 47 sea), 7 countries.
- **Loads in-game without crashing** (first build, confirmed by the author). Its
  `error.log` was vanilla-reference noise (decisions, missions, ai_faction_theaters
  region ids) plus the rivers.bmp palette warning above, which the biClrUsed fix
  silenced. Second build: only a trailing newline in `buildings.txt` (read as a
  malformed empty row, now removed) and "failed to generate a name/portrait" for our
  countries, which have no name lists or scientist portraits yet.

## Known gaps

1. Provinces, states and regions are placeholders. Next is the author drawing countries
   on `dist/valsora_countries_5120x2560.png` (the old `.pdn` colours already moved to the
   new layout), then real provinces that respect those borders.
2. Terrain is plains everywhere; there are no rivers, railways or trees; the relief is
   noise.
3. Lakes vs. inland seas (see Decisions).
4. Country content: no leaders, focuses, units or proper flags.

## Working with the author

The author tests in-game and reports crashes and `error.log`. They cannot see the
pipeline, so always say which files changed and how to install:
1. Delete `mod/valsora_test/` and `mod/valsora_test.mod`.
2. Unzip `dist/valsora_test.zip` into `mod/`; it contains both.
3. Launch with `-debug`.
