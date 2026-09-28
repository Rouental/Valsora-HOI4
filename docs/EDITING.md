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
| **Rivers** | rivers (empty for now) | Yes, if you add any |
| **Continents** | which continent each land province belongs to | No: blanks are filled in |
| **Provinces** | every province's shape | **Yes: the most important layer** |
| **Strategic Regions** | weather and air/naval zones | No: blanks are filled in |
| **States** | states: what a country owns, and where factories go | No: blanks are filled in |
| **Countries** | who owns each state at the start | No: blanks are filled in |
| **Notes (ignored by the build)** | nothing: the old drawing's country colours, for reference | – |

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

Leave it transparent for no rivers. HOI4 rivers are fiddly:
- A river is a **1-pixel-wide** line drawn with the Pencil, on land only.
- It starts with one **green** pixel, and every other pixel is a shade of blue.
- A **red** pixel marks where it flows into another river.
- A **yellow** pixel marks where it splits off.
- The game reports broken rivers in `error.log`.

| Pixel | Colour |
|---|---|
| start of a river | 0, 255, 0 |
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
| Nonscio (Rouental) | NSC | 216, 84, 84 |
| Araseos | ARS | 116, 152, 206 |
| Aislada | AIS | 70, 170, 70 |
| Solitas | SLT | 214, 110, 214 |
| Yastreovakia | YAS | 96, 190, 150 |
| Usnistan | USN | 184, 172, 100 |
| Orientalis | ORI | 236, 160, 70 |

Brand-new countries need a line of code as well (tag, name and colour in
`scripts/common.py`). Ask, and it's a one-line change.

### Strategic Regions

One colour per region. Weather, air zones and naval zones work per region.
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

**Remove land / make a new lake.** Terrain layer: paint it ocean or lakes. Provinces
layer: repaint it as its own water province(s), or merge it into the neighbouring sea
province with the Paint Bucket.

**Make mountains.** Terrain layer: mountain colour. Heightmap: paint brighter greys.

---

## 4. Checking your work

1. Save in paint.net (keep the `.pdn` format and the same file name).
2. Upload it to `source/` on GitHub, replacing the old file, and ask for a rebuild.
   (If you run the build yourself, it is `sh scripts/run_all.sh`.)
3. If something is wrong, the build stops with a numbered list:

```
2 problem(s) in the .pdn; fix these and rebuild:
  1. Province colour (37,11,249) is in 2 separate pieces (each province must be one
     connected area; diagonal touching doesn't count), e.g. at (100, 100), (812, 305)
  2. A province has only 5 pixels (HOI4 needs at least 8) at (2480, 226)
```

Go to those pixel positions in paint.net (watch the numbers at the bottom), fix them
and try again. Lines starting with `note:` are not errors. They tell you what the build
filled in or tidied up for you, so you can check it's what you meant.

After a successful build, install the new `dist/valsora_test.zip` as usual and start the
game with `-debug`.
