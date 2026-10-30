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
| **Ocean Province Lines** | the borders between sea provinces, as red lines (Merlo's) | Yes: lines must close |
| **States** | states: what a country owns, and where factories go | No: blanks are filled in |
| **Countries** | who owns each state at the start | No: blanks are filled in |
| **Notes (ignored by the build)** | nothing: the old drawing's country colours, for reference | – |
| **Necessary Major Rivers**, **Necessary Minor Rivers** | rivers, drawn as simple lines | No: the build tidies them |
| **Necessary Cities** | named cities (victory points) | No: the dot only needs to be close |

Your own layers: everything named **Necessary …** is what you edit for me to add to the
mod (Necessary Borders, States, Names, Cities, Major / Minor Rivers, Provinces; Necessary
Terrain is kept for later terrain detail). Anything with "Reference" in its name, and
**Background** (plain white, for seeing better), is only for you. The build ignores every
layer whose name it doesn't know.

- **Necessary Provinces** (read since 17 October 2026, when you redrew Seigne's and Royalist
  Illiricium's): draw lines inside a state, and that state's provinces become exactly the
  areas your lines and the state's own edges enclose; its old provinces are replaced. A line
  must run from edge to edge (a state line, a border or the coast) to divide anything. States
  you draw no province lines in keep the provinces I cut for them.
- **Subregions** and **Subnames** (from 17 October 2026): paint the parts of a nation that
  can break away (Belekria's republics, Krionik's principalities, Pakitsk inside Belka), one
  colour per part, and write each part's name on Subnames. Each becomes a nation that can be
  released, with cores on the states mostly painted in its colour. The same colour may serve
  two parts far apart, and islands painted in a part's colour go with it. A new part needs a
  line of code too (its tag, name and government), so tell me when you paint one.
- **"Should be an island!"**: ring a piece of land that the drawing joined to its neighbour
  by a thin neck, and I cut the neck so it is an island again (done by hand, not by the
  build).
- **"Impassible / Desert / Jungle / Tundra"** (from 18 October 2026; any layer whose name starts
  with Impassible, Impassable or Desert): paint areas solid, **red** for impassable desert,
  **yellow** for desert, **green** for jungle, **green with red stripes** for impassable jungle (from 19
  October: the Cultists'). The build gives that land the terrain, and a state
  mostly red, or striped, is impassable (no army can enter it; it changes hands with the passable state of
  its nation beside it, as the base game's Sahara does) and **one province**, however big, like
  the base game's great deserts. Desert and jungle states get fewer, larger provinces (desert
  about 600 px, jungle 400), which frees borders for the rest of the map. Lines you draw on
  Necessary States round the areas are states too, as in Usnistan. **White** is tundra and **white with red
  stripes** impassable tundra (from 20 October 2026, your answer: "Tundra will be marked as white. Any impassible
  tundra will be marked with white and red"): the game's snowy plains (plains under permanent snow, the nearest it
  has to tundra), provinces of about 600 px, and the striped one impassable as the red. Paint the white solid (not
  the layer's background: a white background would make the whole map tundra).
  **A passable place inside an impassable area** (a city deep in the jungle, reached by one path; the author's idea
  for the Cultists, 2026-10-19): leave the city and the path unpainted on this layer (or paint them green, for
  ordinary jungle), and give them a state of their own with lines on Necessary States (the city and its path one
  state, or the path its own). A state mostly red or striped is impassable; one mostly unpainted or green isn't. The
  path should be a few provinces wide at least (about 20 px), so a province fits in it, and it must touch passable
  land where you want the one way in.

On the **Provinces** layer the sea provinces are blues, so sea is easy to tell from land.
They are made from the **Ocean Province Lines** layer (see "Sea provinces" below), so
change sea borders there rather than on Provinces.

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
- **Not too many provinces.** HOI4 draws at most 65,536 province borders (each stretch
  of boundary two provinces share, sea included), and stops drawing province and state
  lines after that, from some point down the map. The map has about 60,000 (October
  2026), so new land is cut into provinces of about 190 px; the build stops if the
  limit is passed.

**How big a province should be** (your rule of thumb, 2026-10-17; the Gazetteer shows the
same guide to your friends, with a ruler at the map's zoom):

| land | size | for example |
|---|---|---|
| usual | about **160 px** (13 × 13), most between 120 and 240 | Cardonia's provinces (about 9 to a state) |
| dense | down to about 120 px | crowded heartlands, big cities, river valleys, fronts |
| sparse | 300 to 800 px | tundra (northern Yastreovakia), deserts (Usnistan), ice, high mountains, deep jungle |

Rouental's provinces are about 150 px, much like Cardonia's: it looks detailed because its
states are small (two or three provinces each).

**How big a state should be** (your rule, 2026-10-18: "Cardonia's states are about the ideal size"; the Gazetteer's
guide shows it first, since your friends draw states and the build cuts the provinces):

| land | size | for example |
|---|---|---|
| usual | about **1,310 px** (36 × 36), most between 820 and 1,840, about 7 provinces | Cardonia's states |
| dense | down to about 330 px, 2 provinces | Rouental's states |
| empty | about 1,860 px, 10 provinces, or larger | Zukchiva's states (Yastreovakia's north) | Each new province costs about 3 of the
65,536 borders, and about 2,000 are left (18 October 2026, kept for the states still to be
drawn), room for about 650 more provinces on the whole map: where you go smaller, go bigger somewhere empty. Never under
16 px, or thinner than 3.

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

**The easy way: the Necessary Major Rivers and Necessary Minor Rivers layers.** Draw each river as a
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

### Cities

On **Necessary Cities**, put a small dot of any colour except black where a city is,
with its name written beside it in black (exactly as you've been doing). Each dot becomes
a victory point named after the city, in the province under the dot (or the nearest
land province). The dot doesn't have to be exact, since the provinces aren't known
when you draw. A city is worth 5 victory points; a country's capital keeps 10.

The build can't read the written names (they are just pixels), so I type them into
`source/city_names.json` when you send the file. Moving a dot a few pixels keeps its name.
A new or far-moved dot stops the build until I've added its name. Two cities in the same
province, or two dots with the same name, also stop it. Cities in the same state are fine.

For a nation filled in on the **Gazetteer** (the shared page for your friends,
`docs/GAZETTEER.md`), its cities, state names, terrain, rivers, railways and politics come from
there: its dots on Necessary Cities are no longer read once its cities are edited on the page.

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
| Lindreland (was Linterre, Placeholdros, Placeholdaire) | LNT | 190, 150, 200 |
| Rastava | RST | 184, 160, 72 |
| Volinovia | VLN | 70, 100, 170 |
| Estande | ESD | 153, 0, 0 |
| Coraliza | CRZ | 240, 122, 92 |
| Placeholdria | PLH | 238, 196, 222 |
| Republican Illiricium | ILR | 32, 44, 140 |
| Côtefer | CTF | 70, 150, 190 |
| Entroterra | ETR | 140, 185, 235 |
| Mezzogiorno | MZG | 60, 105, 190 |
| Royalist Illiricium | KIL | 255, 255, 255 |
| Kurikia | KRK | 34, 62, 96 |
| Fraxhemark | FRX | 200, 60, 110 |
| Brillagne (civil war; owns nothing at the start) | BRL | 225, 190, 70 |
| Crépuscule (civil war; owns nothing at the start) | CRP | 75, 72, 85 |
| Reliette (civil war; owns nothing at the start) | RLT | 175, 45, 55 |
| The Marches (civil war; owns nothing at the start) | MRC | 85, 85, 115 |
| HMMLA (civil war; owns nothing at the start) | RLA | 40, 95, 55 |
| Vair (civil war; owns nothing at the start) | VAI | 15, 105, 150 |
| The Faithful (civil war; owns nothing at the start) | FTH | 240, 190, 80 |
| Locus | LCF | 230, 100, 30 |

The first seven are the placeholders, one per continent, and the only ones the start
menu recommends. Brand-new countries need a line of code as well (tag, name and colour
in `scripts/common.py`); ask for them, or draw them as outlines (below).

### Flags

Flags are PNG pictures in `source/flags/`, named by tag: `ROU.png`, `EVR.png`… Any
size works; the build shrinks them to the game's sizes. A flag named
`TAG_democratic.png` (or `_fascism`, `_communism`, `_neutrality`, `_theocracy`) is shown only while
that ideology rules, like Rouental's tricolour.

In the game a flag is only 82×52 pixels (a 1.58:1 rectangle), and much smaller on the
map. A flag of another shape gets squashed, and fine detail turns to noise. The best
flags are about that shape, with bold shapes. Send a flag of another shape and I fit it to 82:52
without stretching: it is scaled evenly, then plain field is added inside its stripes (or
plain sides trimmed), so emblems keep their shape. The flag file (`New_Mod_Flags.pdn`)
is kept in `source/` too, with every flag added so far.

### Sea provinces

The sea provinces are hand-drawn (Merlo, 2026-10-12): on the **Ocean Province Lines**
layer, red lines divide the sea, and every area they close off is one sea province. To
change them, draw or erase lines there, and tell me: I turn the lines into provinces
(`scripts/sea_provinces.py`), which the build doesn't do by itself.

- **Close every line.** An area that leaks into its neighbour merges with it.
- **Keep areas smaller than 1/8 of the map** (640 × 320 px). A bigger one is cut by
  wobbly lines automatically, and the cuts are drawn onto the layer.
- **The map wraps at its left and right edges.** A line that meets one edge should meet
  the other at the same height; the script makes them meet exactly, and puts the two
  provinces facing each other across the wrap in the same sea region.

### Strategic Regions

The sea regions are groups of about nine sea provinces inside each ocean of your ocean
map (Merlo's, 2026-10-12), named after their ocean and numbered west to east, like
"North Demetric 1"; the Piscary and Norlany seas are one region each. Names are tied to
each region's colour (in `source/region_names.json`): paint part of a region in a new blue
and the new region gets a plain name like "Sea Zone 3" until names are added for it.

The land regions follow the nations (2026-10-16, made by `scripts/land_regions.py`): each is
whole states, a big nation's land cut into several, small neighbours grouped. Repaint them as
you like; ask me to run the script again after big border changes (it repaints every land
region, so your own land regions would be lost).

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

**Move a country border with lines** (the usual way since 2026-10-01). Redraw it on
**Necessary Borders**. The land the new line encloses goes to the country holding most of
that area, which is right for most moves (all three on 2026-10-17). When it isn't, draw a
stroke, any colour, on a layer named **Necessary Owners**, from the land that changes hands
into its new owner's land. Do the same when you only move a **label** to give land away,
since no line says it. (`pdn_tools.py owners`; `docs/WORKFLOW.md` has the rest.)

**Merge a country into another but keep it releasable** (Pakitsk into Belka). Move the
old border from Necessary Borders to Necessary States instead of erasing it (select the
line, cut, switch layer, paste), so its states survive. Then paint it on **Subregions**,
only inside the land of the nation it belongs to.

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

   Or paint new islands on a layer of their own, named "Islands to Add" (any colour), and
   tell me whose they are: `pdn_tools.py add_land` makes them land, a province each and
   one state for the country (done for Rouental's two islands on 2026-10-13).

**Make a lake navigable.** Ships can't sail on lakes. Terrain layer: paint the lake in
the ocean colour (8, 31, 130). Strategic Regions layer: give it a blue of its own.

**Remove land / make a new lake.** Terrain layer: paint it ocean or lakes. Provinces
layer: repaint it as its own water province(s), or merge it into the neighbouring sea
province with the Paint Bucket.

**Make mountains.** Terrain layer: mountain colour. Heightmap: paint brighter greys.

**Draw new countries and states as outlines.** This is how Rouental and its
neighbours were made:
1. On **Necessary Borders**, draw country borders as 1-pixel Pencil lines.
2. On **Necessary States**, draw the lines inside a country that
   divide it into **states**.
3. Every closed-off patch of land becomes a state; a large patch becomes several
   states that together fill its shape. Every state is then cut into small provinces
   (about 13 × 13 pixels). Leave no gaps in the lines, or the patch will leak into its
   neighbour.
4. Write each country's name in or next to its patches on **Necessary Names**; a short
   line from a label points to an island it belongs to.
5. Islands you want included but can't outline, just mention (or colour them on a
   reference layer).
6. Upload and ask. Areas that already belong to a real country are left alone, so
   you can outline one region at a time. To split an existing state, draw a line
   through it on Necessary States: only the states you cut are redone. If new lines
   close off an area you don't mean as a country yet, say so and it is left alone. A script (`scripts/apply_outlines.py`) turns the patches into
   states, provinces and owners on the real layers, and makes new countries.

**Keep a copy before a big edit** ("HOI4 Mod Map 2026-10-18.pdn"). If the files live in a
folder OneDrive syncs, pause syncing while paint.net saves, or work on copies outside it:
a file synced halfway through a save can end up damaged. If one does, send it anyway:
`pdn_recover.py` saves every layer still whole.
