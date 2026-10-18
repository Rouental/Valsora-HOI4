# Room under HOI4's province border limit

The author's request (2026-10-15): check the room under the border limit, bearing in mind that "the reduction in
provinces once terrain starts being applied in earnest" will free some ("areas that are impassible desert use less
provinces"). Numbers from the build of 2026-10-15; rerun them with `python3 scripts/border_report.py` (add
`--terrain map` once the Terrain layer is painted, `--preview` for the picture).

**Now** (2026-10-18): 63,531 borders built, 2,005 under the limit, the buffer `pdn_tools.py refine` keeps (it spent
the rest on more provinces map-wide); the numbers below are the 2026-10-15 ones the report was written with.

## Where we are

HOI4 draws at most **65,536 province borders**: past that, province and state lines stop being drawn from some row
of the map down (it happened on 2026-10-12, at 73,231). A border is a stretch of boundary two touching provinces
share, land or water alike (`scripts/borders.py`). `check_mod.py` fails over the limit and warns within 4,000 of it.

- **62,183 borders now: 3,353 left**, about 1,100 more provinces' worth (each province adds about 3).
- By kind: land–land 55,341 (89 %), land–sea 5,628, sea–sea 946, lake–land 268.
- By continent: Orientalis 16,665, Nonscio 10,866, Yastreovakia 10,766, Araseos 9,682, Usnistan 8,564,
  Solitas 3,910, Aislada 784 (sea and lakes alone 946).
- 20,690 land provinces, median 168 px (cut at ~190 px since 2026-10-12); 367 are under 100 px; 380 are islands
  alone in the water (407 borders).
- Only 166 borders come from pairs that touch in more than one place, so tidying borders frees almost nothing:
  the count follows the number of provinces.

## The base game, for comparison

Vanilla 1.19.3's map: 13,413 provinces and **40,694 borders**. Its land provinces are dense in Europe and sparse
elsewhere (median 160 px, mean 399 px), and their size follows the terrain:

| terrain | provinces | median size | vs plains |
|---|---|---|---|
| desert | 815 | 516 px | 4.1 × |
| marsh | 142 | 234 px | 1.8 × |
| mountain | 1,708 | 232 px | 1.8 × |
| jungle | 477 | 207 px | 1.6 × |
| forest | 2,364 | 152 px | 1.2 × |
| plains | 3,031 | 127 px | 1 |
| hills | 1,352 | 120 px | 0.9 × |
| urban | 265 | 100 px | 0.8 × |

Its 22 **impassable** states (interior Borneo, the Gibson Desert, parts of the Sahara ...) are still cut into
provinces, but large ones: 140 provinces, median **1,456 px**, against 157 px for every other land province.
So the author is right: impassable land needs about a tenth of the provinces.

## What would free room

Estimates from re-cutting every state's provinces (a quick weighted k-means per state, compared with the same cut at
today's 190 px: 59,780 borders, which is below today's 62,183 because today's map also has provinces split along
rivers and the author's small drawn states). The terrain is the **terrain test's** (`terrain_test.py`, not in the
mod), standing in for the terrain the author will paint, so the real figures will differ.

| re-cut | land provinces | borders | change |
|---|---|---|---|
| 190 px everywhere (the comparison) | 19,664 | 59,780 | |
| **sizes by terrain like the base game's** | 17,021 | 51,932 | **−7,848 (−13 %)** |
| ... and deep desert in 2,500 px 'impassable' provinces | 16,980 | 51,782 | −7,998 |
| 220 px everywhere | 16,992 | 51,869 | −7,911 |
| 250 px everywhere | 14,949 | 45,804 | −13,976 |

- **Sizes by terrain** are the big win: about 8,000 borders, roughly what a province size of 220 px instead of 190
  would give, but kept small where the ground is open. Applied to today's map, that would mean about 54,000 borders,
  11,500 under the limit. `dist/border_room_preview.png` shows the deserts of Usnistan, now and re-cut.
- **Impassable land** adds little here (−150), because the terrain test's deserts are mostly narrow: only 59,000 px
  are more than 40 px inside one. It grows with how much land the author makes impassable: every 10,000 px of
  impassable land cut like the base game's (about 1,500 px a province) instead of 190 px saves about 140 borders,
  so 200,000 px (a large desert or ice sheet) would save about 2,800.
- **Bigger provinces overall**: each 10 % on the province size takes about 9 % off the borders.
- Not worth it: borders touching twice (166), merging the tiny provinces left (367 under 100 px: about 1,000
  borders, and `merge_provinces.py` already took 4,313), the islands (they can't join other land).

## What adds borders

Every new province adds about 3: provinces re-cut along new rivers (`river_provinces.py`), new state lines that
split provinces, new islands. With 3,353 left, the map can take about 1,100 more provinces as it is.

## Drawing the remaining nations' states (2026-10-16)

What the author drawing their own states for the 122 nations still on Claude's cut ones (`gazetteer.finals`) would
cost: `python3 scripts/border_report.py --drawn-states`. Those nations hold 3,406,261 px of land in 2,952 states
(1,154 px each) and 18,873 provinces. Rouental, the densest drawn nation, has states of **395 px** (two provinces
each) and provinces of **166 px** (its small states and its rivers). Each scenario splits the 122 nations' states into
states of that size (a k-means of their provinces, standing in for the author's lines) and re-cuts the provinces,
compared with the same re-cut of today's states:

| drawn like this | states | land provinces | borders | change |
|---|---|---|---|---|
| today's states, 190 px provinces (the comparison) | 3,149 | 19,664 | 59,780 | |
| **states like Rouental's (395 px)**, 190 px provinces | 8,890 | 19,823 | 60,397 | **+617** |
| states **and provinces** like Rouental's (166 px) | 8,890 | 22,351 | 67,934 | **+8,154** |
| states of 800 px, 190 px provinces | 4,655 | 19,640 | 59,844 | +64 |
| states of 800 px, provinces of 220 px | 4,655 | 17,161 | 52,521 | −7,259 |
| states and provinces like Rouental's, sized by terrain (the terrain test's) | 8,890 | 19,556 | 59,638 | −142 |

- **The states cost almost nothing; the provinces cost everything.** States are only groups of provinces: drawing
  them small adds about 600 borders, because the provinces inside are cut to 190 px whatever the state's size. On
  today's map (62,183) that leaves about 2,700 under the limit.
- **Rouental's province density everywhere does not fit**: about 8,150 more borders, roughly 70,300 on today's map,
  4,800 over the limit. It comes from Rouental's rivers (`river_provinces.py`) and its many one-province states.
- **With provinces sized by terrain** (desert 4 ×, mountains and marshes 1.8 × ..., as in the base game) even
  Rouental's density everywhere fits, with about the room there is now. So the order matters: terrain first, or at
  the same time as the states.
- **The number of states** is the other cost: Rouental's density means about 8,900 states, eight times the base
  game's 1,081 (we have 3,149). HOI4 sets no limit we know of, but every state carries buildings, supply and the AI's
  plans, so the game would slow; states of about 800 px (4,700 states) would be the lighter choice.
- Recommendation: draw the remaining nations' states at whatever size suits each; keep provinces at 190 px (or let
  the terrain size them) outside the Vale of Reibonne; keep Rouental's density for the Vale.

## Recommendation

- Nothing is needed now: 3,353 borders is enough for the river and state-line edits ahead.
- When the terrain is painted, re-cut the provinces of each region by terrain, with the base game's sizes (desert
  4 ×, mountains and marshes 1.8 ×, jungle 1.6 ×, forest 1.2 ×), and the land the author marks impassable in
  provinces of about 1,500 px. The states stay; only the Provinces layer changes, then `river_provinces.py` runs
  again. Facts on the Gazetteer are kept by map pixel, so they follow the new provinces. This would be a new option
  of `pdn_tools.py recut --keep-states` (sizes from the Terrain layer).
- If the Vale of Reibonne, where most of the play is, should stay dense, the room can come from the rest of the
  world, as in the base game (Europe dense, elsewhere sparse).

## The author's marked areas (2026-10-18, a preview)

The author marked the land they know will be tundra, extreme desert or jungle "like base game africa" on a layer
"Desert" of their upload (red outlines: four deserts round North Kornista and Al-Khabid and one by Koronista; green:
two jungles; white lines: Sanada's north coast as tundra): 124,000 px of land, 702 provinces.
`scripts/coarse_preview.py` cut each state's share of them again (a preview only, not in the mod):

| provinces of about | provinces in the areas | borders on the layer | freed | room elsewhere |
|---|---|---|---|---|
| as now (about 175 px) | 702 | 63,189 | | |
| 500 px (the base game's deserts) | 273 | 61,907 | 1,282 | about 427 provinces |
| 800 px (the size guide's emptiest) | 195 | 61,673 | 1,516 | about 505 |
| 1,500 px (the base game's impassable land) | 154 | 61,550 | 1,639 | about 546 |

- Past 800 px it barely matters: a province can't be larger than its state, and the states there are Claude's, about
  1,300 px each, so most become one province. Coarser still would mean fewer, larger states there too.
- The areas are small next to the map (3 % of its land), so they free about 1,500 borders, a quarter of what sizing
  the whole map by terrain would.
- The dense middle of North Kornista and the Mustawi strip lie between the outlines and stay as they are.
