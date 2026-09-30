# Editing the map yourself

Everything about the map lives in one paint.net file: **`source/HOI4 Mod Map.pdn`**.
It is exactly the size of the game map (5120 × 2560), so one pixel in paint.net is one
pixel of the game map. Each layer is one kind of map data. You paint, save, and the build
turns the layers into the files Hearts of Iron IV reads.

You never have to touch the game's own files (`provinces.bmp`, `definition.csv`, state
files and so on). The build writes all of them.

---

## 1. The ten-second paint.net refresher

- **Layers window**: press **F4**. Click a layer to paint on it. The tick box next to a
  layer shows or hides it. Hiding a layer never changes what the build reads.
- **Layer properties**: double-click a layer to change its opacity. This is only for
  viewing and has no effect on the build.
- **Pixel position**: the numbers at the bottom of the window, e.g. `2480, 226`, are the
  pixel under the mouse. The build uses the same numbers when it reports a problem.
- **Colour picker** (**K**): click a pixel to copy its exact colour.
- **Exact colours**: in the Colors window (**F8**), press *More* to type in red, green
  and blue values, or a hex code.

### Four settings that avoid most mistakes

1. **Antialiasing off.** It is the toggle in the toolbar that looks like a smooth versus
   jagged line. Antialiasing blends the edges of every stroke into new in-between
   colours, and each new colour would count as a tiny extra province, state or country.
2. **Use the Pencil (P)** for fine work. It always paints exactly one hard pixel.
3. **Paint Bucket (F)**: set *Tolerance* to **0%** and *Flood mode* to **contiguous**
   (not global). With these settings a fill only recolours one connected patch of
   exactly one colour.
4. **Never resize the image or rename the layers.** The build finds layers by name.
   You may add extra layers of your own (sketches, notes, reference pictures); the build
   ignores any layer whose name it doesn't know.

---

## 2. The layers, bottom to top

| Layer | What it controls in the game | Must it be exact? |
|---|---|---|
| **Heightmap** | 3D relief: how high the ground looks | No: roughly is fine |
| **Terrain** | what is land, sea or lake, plus each province's terrain type | Yes, for land vs water |
| **Rivers** | rivers in HOI4's exact format (optional, for experts) | Yes |
| **Continents** | which continent each land province belongs to | No: blanks are filled in |
| **Provinces** | every province's shape | **Yes: the most important layer** |
| **Strategic Regions** | weather and air/naval zones | No: blanks are filled in |
| **States** | states: what a country owns, and where factories go | No: blanks are filled in |
| **Countries** | who owns each state at the start | No: blanks are filled in |
| **Notes (ignored by the build)** | nothing: the old drawing's country colours, for reference | – |
| **Major Rivers**, **Minor Rivers** (optional) | rivers, drawn as simple lines | No: the build tidies them |

Any other layer (your references, names, sketches) is ignored by the build.

"Blanks are filled in" means: if you leave a spot transparent, it joins whatever is
painted nearest to it, and the build tells you where it did that.

### Provinces

Each province is one solid patch of one colour. Any colour works, as long as:

- **Each colour appears in exactly one patch.** Two separate patches with the same
  colour are an error. Pixels touching only corner-to-corner don't count as connected.
- **Each province has at least 8 pixels**, and is less than 1/8 of the map wide and tall
  (640 × 320 px).
- **No pure black** (0, 0, 0), and no transparent pixels: the whole layer is painted.
- **Four provinces may not meet at one corner.** You don't need to worry about this: the
  build fixes it by moving single pixels and tells you where.
- **Nothing may cross the left or right edge.** The map wraps around there.

A province is land, sea or lake depending on what the **Terrain** layer says under most
of it. Provinces are numbered from the top-left corner, reading like a book. The numbers
change when you add or remove a province, and that is fine: everything that refers to
them is rebuilt at the same time.

### Terrain

This layer decides **what is land and what is water**, and each land province's terrain
type (the most common terrain colour inside it wins). Use these colours:

| Terrain | Colour (R, G, B) | Notes |
|---|---|---|
| **ocean** | **8, 31, 130** | sea, connected to the world ocean |
| **lakes** | **55, 90, 220** | inland water |
| plains | 86, 124, 27 | everything is plains at the moment |
| forest | 0, 86, 6 | |
| hills | 112, 74, 31 | |
| mountain | 134, 84, 30 | |
| desert | 206, 169, 99 | |
| marsh | 75, 147, 174 | |
| jungle | 0, 82, 82 | |
| urban | 240, 255, 0 | |

These are colours from the game's own terrain palette, so the game also shows them as
the matching ground texture. A colour that isn't in the palette is read as the nearest
one, and the build lists where.

### Heightmap

Grey = height. **95 is sea level**: water must be darker than 95 and land brighter. You
don't have to be careful: the build nudges anything on the wrong side of 95 (land to
96, water to 94). Brighter greys look like hills and mountains. This layer is only for
looks; the terrain *type* comes from the Terrain layer.

### Rivers

**The easy way: the Major Rivers and Minor Rivers layers.** Draw each river as a
1-pixel line with the Pencil, in any colour, on land. Major rivers count as large
rivers in the game (a bigger attack penalty to cross), minor ones as small rivers.
The build converts them into HOI4's fussy format for you:
- The end nearest the sea (or a lake) is the mouth. If the line stops a few pixels
  short of the water, it is extended to reach it.
- The longest line is the main river and gets the green source pixel. Every side
  branch becomes a tributary with a red pixel where it joins.
- Diagonal steps get an extra pixel, because HOI4 rivers may only connect edge to edge.
- Tiny loops and stubs (under 6 px) are tidied away.
- Rivers widen towards the mouth.

The build prints how many pixels it drew. Ask to see a close-up if you want to check.

Rivers matter in combat only where they lie **between** two provinces; a river
through the middle of a province is just scenery. You don't have to draw provinces
along them: after you add or move rivers, ask, and a script
(`scripts/river_provinces.py`) re-cuts the provinces of every state a river crosses so
the river becomes their border. States stay as they are.

**The exact way: the Rivers layer.** Anything painted here is used as it is, in HOI4's
own colours, and wins over the Major/Minor layers where both have a pixel:

| Pixel | Colour |
|---|---|
| start of a river (one per river) | 0, 255, 0 |
| joins another river | 255, 0, 0 |
| splits off | 255, 252, 0 |
| narrowest → widest | 0, 225, 255 · 0, 200, 255 · 0, 150, 255 · 0, 100, 255 · 0, 0, 255 · 0, 0, 225 · 0, 0, 200 · 0, 0, 150 · 0, 0, 100 |

### Continents

One colour per continent. It only matters for a few game rules, and blank land takes the
nearest continent.

| Continent | Colour |
|---|---|
| Nonscio | 216, 84, 84 |
| Araseos | 116, 152, 206 |
| Aislada | 70, 170, 70 |
| Solitas | 214, 110, 214 |
| Yastreovakia | 96, 190, 150 |
| Usnistan | 184, 172, 100 |
| Orientalis | 236, 160, 70 |

### States

One colour per state, on land only; water is ignored. Every land province belongs to the
state whose colour covers most of it. A state may be in several pieces, which is how
island states work. To make a new state, paint an area in a colour no other state uses.

### Countries

Paint land in a country's colour to give it that country. **Borders follow states**: a
whole state goes to the country whose colour covers most of it. To split a state
between two countries, first split it into two states on the States layer. A country
with no land left is simply left out of the game.

| Country | Tag | Colour |
|---|---|---|
| Nonscio | NSC | 216, 84, 84 |
| Araseos | ARS | 116, 152, 206 |
| Aislada | AIS | 70, 170, 70 |
| Solitas | SLT | 214, 110, 214 |
| Yastreovakia | YAS | 96, 190, 150 |
| Usnistan | USN | 184, 172, 100 |
| Orientalis | ORI | 236, 160, 70 |
| Rouental | ROU | 54, 106, 64 |
| Seigne | SGN | 240, 240, 240 |
| Evriches | EVR | 240, 208, 64 |
| Hollier | HLR | 185, 53, 52 |
| Selgrave | SGV | 112, 16, 32 |
| Lustiana | LST | 28, 28, 28 |
| Lanzerac | LZC | 168, 130, 36 |
| Guedelon | GDN | 7, 76, 130 |
| Cardonia | CRD | 84, 28, 120 |
| Romanoddle | RMD | 46, 139, 150 |
| Selto | STO | 214, 120, 40 |
| Linterre | LNT | 190, 150, 200 |
| Rastava | RST | 184, 160, 72 |
| Volinovia | VLN | 70, 100, 170 |
| Estande | ESD | 153, 0, 0 |
| Coraliza | CRZ | 240, 122, 92 |
| Placeholdria | PLH | 238, 196, 222 |

The first seven are the placeholders, one per continent, and the only ones the start
menu recommends. Brand-new countries need a line of code as well (tag, name and colour
in `scripts/common.py`); ask for them, or draw them as outlines (below).

### Flags

Flags are PNG pictures in `source/flags/`, named by tag: `ROU.png`, `EVR.png`… Any
size works; the build shrinks them to the game's sizes. A flag named
`TAG_democratic.png` (or `_fascism`, `_communism`, `_neutrality`, `_theocracy`) is shown only while
that ideology rules, like Rouental's tricolour.

### Strategic Regions

One colour per region. Weather, air zones and naval zones work per region. **Sea zones
are painted in blues, land regions in anything but blue**, so they are easy to tell
apart. Keep to that when you add or repaint one. To make a sea zone bigger, paint its
blue over a neighbouring sea zone; to split one, paint part of it a new blue.
- **Sea and land need separate regions.** Lakes go with the land around them.
- **A sea region must be one connected body of water.**
- **A state must lie inside one region.** A land province with no land-region colour
  (for example new land drawn in the sea) joins its state's region by itself.

---

## 3. Common jobs, step by step

**Give a state to another country.** Countries layer, colour picker on the new owner,
Paint Bucket on the state.

**Move a border through the middle of a state.** First split the state on the States
layer by painting part of it in a new colour. Then repaint that part on the Countries
layer.

**Split a province in two.** Provinces layer, pick a new colour, paint over half the
province with the Pencil or a hard-edged brush. Both halves must stay solid patches.

**Merge two provinces.** Provinces layer, colour picker on one, Paint Bucket on the
other.

**Add an island.**
1. Terrain layer: paint the island in a land colour (e.g. plains 86, 124, 27).
2. Provinces layer: paint it in one or more new colours.
3. That's it. States, Countries, Regions and Continents fill themselves in from the
   nearest land, and the heightmap lifts it above sea level. Paint those layers too if
   you want it to go somewhere specific.

**Make a lake navigable.** Ships can't sail on lakes. Terrain layer: paint the lake in
the ocean colour (8, 31, 130). Strategic Regions layer: give it a blue of its own.

**Remove land / make a new lake.** Terrain layer: paint it ocean or lakes. Provinces
layer: repaint it as its own water province(s), or merge it into the neighbouring sea
province with the Paint Bucket.

**Make mountains.** Terrain layer: mountain colour. Heightmap: paint brighter greys.

**Draw new countries and states as outlines.** This is how Rouental and its
neighbours were made:
1. On a layer called **Borders**, draw country borders as 1-pixel Pencil lines.
2. On a layer called **Necessary Provinces**, draw the lines inside a country that
   divide it into **states**.
3. Every closed-off patch of land becomes a state; a large patch becomes several
   states that together fill its shape. Every state is then cut into small provinces
   (about 12 × 12 pixels). Leave no gaps in the lines, or the patch will leak into its
   neighbour.
4. Write each country's name in or next to its patches on any layer, e.g. "Names".
5. Islands you want included but can't outline, just mention (or colour them on a
   reference layer).
6. Upload and ask. Areas that already belong to a real country are left alone, so
   you can outline one region at a time. To split an existing state, draw a line
   through it on Necessary Provinces: only the states you cut are redone. A script (`scripts/apply_outlines.py`) turns the patches into
   states, provinces and owners on the real layers, and makes new countries.
