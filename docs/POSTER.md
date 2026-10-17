# The world map poster (not part of the mod)

A print of Valsora as it stands on the first day of the game, 1 January 2036: the world as a vintage atlas plate in
the style of the Valsora Deco UI (lacquer and ivory, gilt hairlines, stepped corners, sunbursts, Federo capitals),
for the author and the friends who play its nations. It was made as a surprise (2026-10-17). **Nothing the build uses
reads it**: `scripts/poster.py` only reads the last build and writes `dist/posters/`.

## The files

| File | What |
|---|---|
| `dist/posters/valsora_2036_poster.png` | the print, 9600 x 6570 px (32 x 22 in at 300 dpi, 36 x 25 in at 267 dpi), about 19 MB |
| `dist/posters/valsora_2036_poster_preview.png` | the same at 2400 px wide |
| `dist/posters/valsora_2036_poster_detail_vale_of_reibonne.png` | close-up at print resolution: Rouental and the Vale |
| `dist/posters/valsora_2036_poster_detail_yastreovakia.png` | close-up: Yastreovakia (Krionik, Belekria, Sanada, Volstokn ...) |
| `dist/posters/valsora_2036_poster_detail_cartouche.png` | close-up: the title cartouche |
| `dist/posters/valsora_2036_poster_detail_flag_frieze.png` | close-up: sixteen columns of the flag frieze |

A high-quality JPEG is written beside the PNG only if the PNG ever passes 60 MB (it is about 19: the dark sea
compresses well).

## Rerunning it

```sh
python3 scripts/poster.py              # about 3.5 minutes, about 7 GB of memory at its peak
```

after a build (`sh scripts/run_all.sh`), so it shows the current map. It is deterministic. For trying things out
(these write into the system's temporary folder, `valsora_poster/`, never into the repository):

```sh
python3 scripts/poster.py --draft 0.3                      # the whole poster at 30 % size, about 80 s
python3 scripts/poster.py --window 380,560,1150,1090       # one part of the map (map px) at print size, seconds
python3 scripts/poster.py --draft 1 --no-map               # the frame alone round an empty plate
python3 scripts/poster.py --draft 0.3 --reuse-layout       # keep the lettering's layout and reuse it next time
python3 scripts/poster.py --palette pale                   # a pale sea (old-atlas blue-grey) instead of lacquer
```

The layout of every name is decided in map pixels with the type sizes of the print, so a draft is lettered exactly
as the print is; a window lays out only what is inside it, so it can differ near its edges.

## What it shows, and where each thing comes from

Everything is read, never written: `work/world.npz` (land, sea, lakes, continents, rivers, heightmap),
`work/provinces.npz` and `work/regions.npz` (each pixel's province, the cities' pixels), `build/valsora_test` (each
state's owner and victory points from `history/states`, the capitals from `history/countries`, the map colours from
`common/countries/colors.txt`, the names of the victory points and the sea regions from the localisation, the sea
regions from `map/strategicregions`, the stand-in flags from `gfx/flags`), `dist/countries.csv` (the 160 nations on
the map, their names and governments), `source/flags/`, `source/city_names.json`, and the terrain test's relief.

- **The plate**: the whole 5120 x 2560 map at 1.75 print px per map px (8960 x 4480), centred as the build centres
  it (the land is already centred on the wrap). The sea is lacquer, deeper away from the coasts, with gilt water
  lining (six ripple lines fading offshore) and a fine gilt line just off every coast, inside a dark ink coastline.
- **The nations**: each in a muted wash of its map colour (lightness squeezed into a pale band, chroma cut, a little
  warmth added), with a stronger ribbon of its colour along the inside of its borders, as old hand-coloured maps
  had. Frontiers are crisp ink lines and state boundaries faint ones; both are drawn from each nation's (or state's)
  smoothed outline, so a shared border is one line, without the pixel staircase.
- **Relief**: hill shading (two lights, north-west and west) of the terrain test's relief (`work/terrain_test/relief.npy`,
  `scripts/terrain_test.py`: the Alps by Rouental, the Himalaya at Ganden, the Vale of Reibonne ringed by the
  author's ranges ...), calm on the lowlands, the high ranges paler. Without that file, the build's heightmap.
- **Rivers**: the drawn rivers (`world.npz` `rivers`), the major ones wider.
- **Names**: every nation's name in letter-spaced Federo capitals inside its largest piece of land, sized by its
  area, straight or curved along the land's axis, as large and as widely spaced as fits clear of its edges, its
  capital and its capital's name (106 of the 160). The other 54 are too small: their names stand beside them, in the
  sea where they can, never over another small nation, with a hairline from a dot on the nation. The four great
  powers (Krionik, the Kampfian Empire, Sarkis, Fraxhemark) have a diamond between fading hairlines under their
  names, a ringed star for a capital and a double gilt frame in the frieze.
- **Capitals and cities**: a star in a ring for every capital, a ringed dot for every other city the author has named;
  the names in Josefin Sans, the capitals' bolder. A capital is named only when its nation has named it (27 have;
  the build calls the others "<Nation> 12 City"), and not again when it bears its nation's name (Guedelon, Evriches,
  Lanzerac).
- **Oceans**: the sea regions are "<ocean> <n>", grouped into their eleven oceans; each name is set in spaced Bodoni
  italic capitals across the most open water of its ocean, once per large piece of it (the wrap cuts some in two,
  and the widest are halved), so the Northern Ocean, the Arctic Ocean and both Friedlichs are named twice.
- **Continents**: the seven names very large and faint under everything, ink over the land and gilt over the sea.
- **The frame**: a degree band round the plate, an outer gilt rule with stepped corners, corner brackets and fans;
  the cartouche (VALSORA in Limelight, gilt, over a sunburst; "The World in the Year 2036"); the key to the map; the
  four great powers with their flags, governments and capitals; the scale; a compass rose on a sunburst in the open
  sea north-east of Sanada; and the frieze: all 160 flags in alphabetical order with their names (the author's flag,
  `source/flags/<TAG>.png`, or the game's stand-in stripes in the map colour).

## What is a guess, or not the game's

- **The scale.** Nothing gives Valsora a size. The poster takes it to be the Earth's: 5,120 map pixels round the
  equator, so one map pixel is about 7.8 km there (40,075 km / 5,120), and the bar is drawn for the equator, in
  kilometres and in leagues of three nautical miles (5.556 km). The map is not a true projection (the game treats it
  as flat), so the scale is only right near the middle.
- **The degrees** round the plate are decoration: longitude 0° at the map's middle column, 180° at the wrap, the
  equator at the middle row. Valsora has no official coordinates (the terrain test used its own "latitude" per
  continent).
- **The relief is the terrain test's, not the game's.** The author asked for it to stay out of the mod (2026-10-12);
  the game's own heightmap is still noise. The test was run on the map of 2026-10-12, so land drawn since takes the
  relief of the nearest land.
- The washes are muted versions of the game's map colours, not the colours themselves; the stand-in flags are the
  game's stripes redrawn sharp at the frieze's size.

## Rough edges

- Where tiny nations crowd (the Vale of Reibonne, the coast of Illiricium, the Volstokn border), the names set
  beside them sit close together and some leader lines are long; a few capital stars almost touch (Fraternal City
  and Devlon's).
- Seven named cities find no room for their names (Kuthia, La'Fleur and Eclyea in Merlovich, Saintiers and Seraine
  by Rêverie, South Bijelkop, Weißadel): their dots are drawn, unnamed. The script logs every name it leaves out.
- The continents' names are faint on purpose; over the palest washes their great letters can read as grey shapes.
- The lettering is placed by the script, not by hand: a name may sit where a cartographer would not have put it, and
  any of them can be moved by changing the map or the script's weights (`fit_label`, `angle_factor`, the leader
  labels' costs in `layout_labels`).

## Fonts

The Deco UI's fonts, `deco_ui/source_fonts/` (Federo, Josefin Sans, Bodoni Moda, Limelight), all under the SIL Open
Font License (the `OFL.txt` beside each). They are only used to render the poster's text: no font file is copied or
embedded, which the licence allows. Federo has no Ś: Ryśny's is drawn from its S and the acute of its Á.
