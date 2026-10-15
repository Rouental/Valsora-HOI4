# Problem log

Every error and problem met while building the Valsora mod, what caused it and how it
was fixed, newest first. Add to it whenever something goes wrong, in game or in the
build. "Check" means `scripts/check_mod.py` now catches it, so it can't slip back in.

## In-game problems (reported by the author)

**Deco UI: a closed division overview stayed on screen, headerless, over the map** (2026-10-15, author's screenshot)
- Cause: the game does not hide a closed side panel; it moves it back to its `position` and leaves it drawn there.
  Vanilla's `position` is off-screen (x -606), so nothing shows. v0.5.1 had set it 36 px below the panel's place, on
  screen, to make panels rise into place; a closed panel then stayed there (its sub-windows over the map). The
  v0.5.1 entry below wrongly said the game hides a window once it has slid back: vanilla's dropdowns rest at y -300
  or -2000 or inside a clipped parent.
- Fix (Deco UI v0.5.2): every closed panel rests at the game's off-screen `position` again (just off the left edge
  where the game's is on screen: `layout_politics.closed_x`), and opens and closes at once (`animation_time = 0`, as
  several vanilla dropdowns do), so nothing slides across the flag either.

**New game: Back on the country screen looped instead of returning to the menu** (2026-10-15, author's video)
- Cause: with a single start (bookmark), the game skips its "Select scenario" screen. Back on the country screen
  returns to that screen, which picks the only start at once ("Starting History...") and opens the country screen
  again.
- Fix: two starts on 1 January 2036, Valsora (Rouental, as the author asked, and Merlovich recommended) and the Vale
  of Reibonne (the Association), so the scenario screen stays and its Back returns to the menu.

**error.log: `valsora_reibonnaise_opinions: Invalid Scope ... provided: None`** (2026-10-15, the author's error.log,
10 lines in all, down from 2,081; this was the only one of ours)
- Cause: `on_startup` runs without a scope, and the scripted effect was called straight inside it.
- Fix: `random_country = { valsora_reibonnaise_opinions = yes }` (the effect goes through every country itself).
  Check: no scripted effect of ours called at the top of an `on_startup` effect.

**Main menu: a star over the career profile button's label** (2026-10-15, author's screenshot)
- Cause: the game's `career_profile_button_star` (shown when the career profile has something new) was placed at
  the button's right end, over the end of "CAREER PROFILE".
- Fix (Deco UI v0.5.2): a small badge (scale .6) on the button's upper right corner.

**Deco UI: a newly opened side panel slid over the flag and the country's name** (2026-10-15, author's video)
- Cause: every side panel slid in from x -606 to its place (vanilla's slide), and the windows beside them from
  -356; with the panels flush under the top bar since v0.4.8/v0.5, their header crossed the medallion before
  the notch reached it, choppily the first time a panel opened (its pictures loading), and the old panel slid
  out the same way when switching.
- Fix (Deco UI v0.5.1): they rise 36 px into place over 200 ms (`layout_politics.RISE`, `OPEN_MS`) and sink as
  they close. The notch narrows downward, so a panel lower than its place never covers the medallion or seal.
  The game hides a window once it has slid back, wherever that is (vanilla's dropdowns slide 25 px).
- Found while testing the Gazetteer's state capitals: a city's card put its buttons in a column beside its
  name, which the fourth button squeezed to a few letters; the name and the buttons now each take a row.

**Leftover placeholder bricks and grid states; Placeholdaire's map tools closed; Gazetteer gaps**
(2026-10-15, author's screenshots of the `.pdn` and the site)
- Squares by Xue, around the Associated Cities and Qinguo, and by Ungar: the lakes, still in the
  placeholder build's 48 px squares (four lakes, 2-10 each). Fix: `pdn_tools.py lakes`, each lake
  one province.
- Squares on Arvorenia's and Atrocha's islands and Kurikia's KU island: 87 land provinces still
  32 px bricks, with 96 px grid states, where no outline run had reached (the friend's build of
  2026-10-05; islands given whole with `give`). Fix: `pdn_tools.py recut` cuts them like an
  outlined patch (Kurikia's and a Belekria island group's single states kept). Found by
  provinces whose borders run 60 % or more on the brick grid; none are left.
- Placeholdaire was "not editable": an island with no line on it was two states (the edge of an
  old strategic region; San Sierra had one too, from the old 650 px state size), so the test for
  drawn states said no. Fix: each merged into one state (`pdn_tools.py attach`).
- The site counted only names typed on it ("0 / 56 named" for Rouental, named on the map), and
  showed none of Rouental's government flags. Fix: the export marks the states the map names
  (`named`) and carries the game's `TAG_<ideology>` flags; the page counts and shows them.
- Releasables picked provinces, which HOI4 can't core (cores, like formables, are per state).
  Fix: they pick whole states; the first ones' provinces count as the states they cover by half.
- Drawn states overlapped and ran into the sea and neighbours. Fix: Suggest › State keeps only the
  nation's land inside the line that no earlier state holds.
- Found while testing: on a phone the Suggest tool's hint, beside four chips (State is new), became
  a narrow column nine lines tall and squeezed the map to 85 px, so a tap landed on the boxes of the
  nation's other parts. Fix: on a phone the chips scroll in a row of their own and the hint sits
  below them in two lines (a tap shows the rest); the map keeps 230 px.
- Found on the way: `country_list.py` listed the 364 Earth tags the build has kept as stand-ins
  since 2026-10-14 (546 "countries"). Fix: it leaves out the base game's tags that aren't ours.

**Deco UI: the other side panels left a gap under the top bar and covered the medallion; two installs**
(2026-10-14, author)
- Every side panel but the politics screen still opened at y 78 (16 px below the band) and, drawn over the top
  bar, hid the medallion's lower part and the decisions seal. Fix (v0.5, `deco_ui/tools/make_panels.py`): the
  16 panels get the politics screen's treatment (flush at y 62, a notch the shape of the medallion and seal,
  the title moved right of it, the content moved below the seal) and the 17 windows that open beside them sit
  flush too. Check: the Deco UI's `validate_preview.py` keeps every element of each patched file, and
  `preview_panels.py` draws each panel with the game's textures.
- The Deco UI was a second mod to install, which had to load after Valsora (v0.4.5 loaded first). Fix: it is
  part of the Valsora build (`scripts/deco_ui.py`, `common.DECO_UI` to switch it off). The files it makes from
  Valsora's data (the long-name trigger, the politics screen) are made by the build itself, so a new country
  or sub-ideology can no longer leave them stale. Check: `deco_ui.py` stops on any file both mods ship that the
  Deco UI does not replace on purpose; `check_mod.py` checks the merged mod.

**The tension globe's fire "didn't come out too well"** (2026-10-14, author's screenshot at 100 %)
- Cause: flames were painted over the disc from below; at full tension the whole globe was a noisy
  orange blur with no shape left.
- Fix: `globe.py` burns it as vanilla's does: lava cracks (borders of random cells on the sphere,
  warped) spreading upwards, a dark red crust that keeps the globe's light and highlight, a molten
  glow from below (`dist/tension_globe_preview.png`).

**Deco UI: the politics screen covered the medallion, kept vanilla's header, unstyled tooltips**
(2026-10-14, author's screenshots of v0.4.7)
- The panel opened 16 px below the top bar's band and hid the medallion's name plate and the
  decisions seal: side panels are drawn over the top bar. Fix (v0.4.8): the panel sits at the band's
  bottom and leaves a notch the shape of the medallion and seal (they show through it); its own
  background lets clicks through and children outside the notch catch them.
- The header behind the portrait was vanilla's metal picture: the game swaps the `pol_view_bg` icon's
  sprite at runtime (`GFX_pol_view_bg` / `_no_dlc`), so ours never showed. Fix: both vanilla
  textures are replaced at their paths.
- Tooltips kept vanilla's look: the game loads `tiles_dialog.dds` (vanilla's) before the
  `tiles_dialog.tga` the Deco UI shipped. Fix: the `.dds` is replaced. Check: the Deco UI's
  `validate_preview.py` flags any `.tga` a vanilla `.dds` of the same name shadows.
- Also (author's requests): the leader's description only in the portrait's tooltip, the law cards
  gone, the sub-ideology shown, the spirits moved up: the advisors & laws list is 156 px taller.

**Valsora started in 1936** (2026-10-14, author: "Valsora takes place in 2036")
- Cause: the clock, the tech tree and every date condition were vanilla's.
- Fix: the start and end dates (`common/defines/valsora_game.lua`), the bookmark, our
  history, every technology's `start_year`, the tech tree's year labels, the date
  conditions of the generic content the mod ships, a game rule's years and the generic
  names with years moved a hundred years (`vanilla_parts.py`; see "2036" in CLAUDE.md).
  The start date's picture is Valsora's, not 1936's soldiers.
- Check: `check_mod.py` fails on an 18xx or 19xx date, research year or tech tree label in
  the built files, and on a start date or bookmark outside 2036 (mutation-tested).
- Not yet seen in game.

**The generic events, AI strategies and on_actions were missing since the first build**
(2026-10-14, found reading vanilla's own files)
- Cause: `replace_path` on `events`, `common/on_actions` and `common/ai_strategy` switched
  off Earth's content, and with it what every country uses: the election, ace, war
  justification, nuclear, capitulation and operative events, the faction and demand
  events (`Generic.txt`), collaboration governments and resistance (`LAR_occupation.txt`),
  the generic AI strategies (default, doctrines, operations, operatives) and the hooks
  that fire them.
- Fix: those files come back as the mod's own, from `source/vanilla/` (copies made by
  `vanilla_sync.py`, the on_actions cut by hand without their Earth parts, Earth-only
  blocks cut from `default.txt`); the events they fire only for Earth's countries
  (Denmark's election, ...) are hidden empty stand-ins.
- Check: `check_mod.py` fails on an event fired but not defined (mutation-tested).
- Not yet seen in game.

**error.log: 1,142 lines of "Invalid decision" and "Invalid Decision ID"** (2026-10-14)
- Cause: `replace_path` is not recursive, so vanilla's decision categories still load, and
  so do the focus trees, ideas and scripted triggers that name its decisions: 732 names.
- Fix: a never-visible decision of the same kind under each name
  (`common/decisions/valsora_vanilla_stand_ins.txt`, generated from
  `source/vanilla/index/decisions.txt`).
- Check: `check_mod.py` fails if one has no stand-in (mutation-tested).

**error.log: 728 lines of "is missing a history file"** (2026-10-14)
- Cause: Earth's 364 country tags stay defined (vanilla's `common/country_tags`), and each
  needs a history file. Removing the tags would break vanilla's files that name them
  (technologies alone, 620 times; the peace conference, the AI, achievements).
- Fix: a stand-in history for each (capital state 1, owning nothing).
- Check: `check_mod.py` fails if one is missing, holds more than the stand-in, or if one of
  our tags is Earth's (mutation-tested).

**error.log: 30 lines of AI faction theaters, and ships in port "too far away from
center"** (2026-10-14)
- Cause: vanilla's `ai_faction_theaters.txt` names Earth's strategic regions; and the game
  placed the unit positions `unitstacks.txt` didn't give, putting ships in port far from
  the centre of two of Merlo's large sea provinces.
- Fix: one AI theater per continent with its coastal seas, in a file of vanilla's name;
  every kind of unit position vanilla's map has is written (see What HOI4 requires).
- Check: `check_mod.py` wants ships in port (19, 20) everywhere but on lakes
  (mutation-tested).

**The world tension globe showed Earth** (2026-10-14, author's screenshot)
- Cause: like the minimap, it is a fixed picture: vanilla's
  `gfx/interface/world_tension_icon_big_strip.dds`, ten frames of Earth catching fire as
  tension rises, and the small `world_tension_icon.dds`.
- Fix: `scripts/globe.py` draws Valsora's at the same sizes from the land: a lit globe seen
  from above Nonscio and Araseos, flames rising frame by frame (`dist/tension_globe_preview.png`).
- Check: `check_mod.py` fails if either file is missing or not vanilla's size (mutation-tested).

**Deco UI: the politics screen was a mess** (2026-10-14, author's screenshot of v0.4.5)
- Cause: it was not the Deco UI's screen. Both mods ship `interface/countrypoliticsview.gui`,
  and the Deco UI loaded first, so Valsora's own copy won, with the Deco UI's scripted text
  (title, ruling party, last election, law names, the leader's description) drawn over it
  where the Deco UI's layout would have had room for it.
- Fix: the Deco UI (v0.4.7) names Valsora as a dependency (`dependencies = { "Valsora (test
  map)" }` in both its descriptors), so the launcher always loads it after Valsora.

**Deco UI: the faction logo sat on the button's icon** (2026-10-14, author's screenshot)
- Cause: the game shows `topbar_faction_empty` (vanilla: a plain plate) in a faction, with the
  faction's logo over it, and `topbar_faction` (vanilla: crossed axes) out of one. The Deco UI
  had drawn them the other way round.
- Fix: swapped (v0.4.7), the logo centred in the button's ring.

**Portrait files and scientists in error.log** (2026-10-14, read with vanilla's own files at last)
- Cause: vanilla's `portraits/00_portraits.txt` and the DLCs' `01_anniversary`, `02_tiger`,
  `03_mtg`, `027_lar` and `998_scientist_portraits.txt` key their lists by Earth continents
  (139 lines: "unknown continent europe", then an unexpected token for each list). And our
  own lists had no scientists: every scientist the game generated logged "Failed to generate
  a portrait … scientist" and kept an empty portrait, which logged `Icon definition ""` and
  `"_small"` on every load (156 + 568 lines in the 2026-10-02 log; the "source unknown"
  noise noted under Superevents).
- Fix: the mod ships a file under each of the six names (`cultures.VANILLA_PORTRAIT_FILES`;
  `00_portraits.txt` keeps vanilla's `default` block of fallback and operative portraits),
  and every continent and country block has vanilla's generic scientist portraits for its
  culture.
- Check: `check_mod.py` fails if one of the six files is missing or a block has no male and
  female scientists (mutation-tested).

**Deco UI: no main menu buttons** (2026-10-14, the Valsora Deco UI v0.4.3 and v0.4.4; author's
screenshot and `error.log`)
- Cause: the UI mod's `.gui` patcher wrote orientations in quotes (`Orientation = "CENTER_DOWN"`).
  On a `containerWindowType` the game rejects that ("Not a valid orientation: CENTER_DOWN") and keeps
  the default `UPPER_LEFT`, so the button row's offset from the bottom centre, (-660, -166), put it
  above the top-left corner of the screen. The same error sent five top bar windows meant for the
  right edge (command power, nukes, army, navy, air) off the left edge. It also wrote
  `alwaystransparent` on twelve containers, which the game rejects there ("Unexpected token").
  v0.4.4 had guessed at `Origo` from the screenshot and changed nothing that mattered; the log named
  the file and line at once.
- Fix: `deco_ui/tools/guipatch.write_gui` (used by every generator) writes orientations bare, as
  vanilla does on containers, and moves a container's `alwaystransparent` into its `background`
  block, where vanilla puts it. Released as v0.4.5 (`dist/valsora_deco_ui.zip`).
- Check: `deco_ui/tools/validate_preview.py` flags quoted orientations, `alwaystransparent` on a
  container and any key no vanilla element of that type uses (read from the game's own `.gui`
  files). On the v0.4.4 files it flags all 31 lines the game's log named.

**Three generated rulers with famous real names** (2026-10-13, seen on the nation sheet)
- Cause: the name lists are vanilla's, and the filter for famous surnames (`cultures.NOT_SURNAMES`)
  didn't have these: Sicilianzo's "Umberto di Savoia" (Italy's last king), Solaria's "Felice
  Garibaldi" and Coraliza's "Eugénio de Castro" (a Portuguese poet).
- Fix: their surnames are in `cultures.DRAW_AGAIN`, so those three draw again (Gaetano
  Mambretti, Fabrizio Sacchi, Bernardo Teixeira) and every other leader keeps their name
  (checked against the previous `dist/countries.csv`).

**The minimap showed Earth** (2026-10-13, author's screenshot)
- Cause: the minimap is not drawn from the map. It is a fixed picture, vanilla's
  `gfx/minimap/minimap.dds` (sprite `GFX_minimap_world`, defined in vanilla's
  `interface/unitview.gfx` and shown by `interface/minimap.gui`), which the mod never
  replaced.
- Fix: `scripts/minimap.py` draws Valsora's at build time from the land: 194×97, the
  map's 2:1 (vanilla's Earth is 268×97, for its 2.75:1 map), pale land on darker
  parchment like vanilla's, in a frame of our own (`gfx/minimap/border.dds`). The window
  is moved right to meet the map-mode buttons (`interface/minimap.gui`, x = -274 instead
  of -343) and the ctrl+m slide that hides it shortened (`MINIMAP_TOGGLE_SHIFT` 202
  instead of 270), as Equestria at War does for its own 2:1 minimap (195×97). Check:
  `check_mod.py` checks the picture's shape and the frame, window and slide that go
  with it (mutation-tested: picture missing, vanilla window position, vanilla slide).
- Not yet seen in game.

**Silvamar hard to tell from Arvorenia and Las Anod** (2026-10-13, author)
- Cause: its map colour was a green (Claude's pick, from its flag's green band), next
  to Arvorenia's dark green and Las Anod's light green.
- Fix: its flag's navy, a little lighter, (10, 30, 140); `pdn_tools.py recolour` kept
  the Countries layer in step.

**Province and state lines missing from row ~1995 down** (2026-10-12, author's screenshots)
- Cause: HOI4 draws at most 65,536 province borders; past that an integer overflows and
  the rest are not drawn (HOI4 wiki, Map modding, "usually hit at about 21000
  provinces"). A border is each stretch of boundary two touching provinces share, land
  or water alike. They are made in province id order, which here is reading order, so
  the lines stopped at the row where the count passed the limit. The map had 24,767
  provinces (~150 px each wherever the author had outlined) and 73,231 borders; the
  count puts the overflow at row ~1990, the screenshots at ~1995. Not the map's size.
- Fix: `merge_provinces.py` merged 4,313 of the smallest land provinces into a neighbour
  in the same state (never across a river, never two city provinces, at most 400 px):
  20,454 provinces and 60,318 borders, land provinces 186 px on average; new outlines
  are cut at ~190 px (`PROVINCE_AREA`). Check: `check_mod.py` counts the borders
  (`borders.py`) and fails over 65,536 (it failed on the old build), with a note within
  4,000 of it.
- The first run took which provinces touch from the build's province map, whose
  X-crossing fixes move single pixels: two provinces touching only at such a corner
  were merged and the build stopped on a province in two pieces. It now reads the
  Provinces layer itself.

**Placeholder islets left beside new countries, and a code two nations share** (2026-10-12, author)
- The author found, by their names in game, states that were still placeholders. Five
  were islets of 17-52 px a few px off land the update had just outlined (the
  Cultists', Cascadia's, Charity's, Volstokn's, Sennheiser's): no line went round them
  and no label named them, so they kept the continent's placeholder colour, and the
  report only gave the placeholder land's total. Fix: `pdn_tools.py attach` to their
  neighbour's nearest state. Check before reporting an update: list each placeholder
  state left and the country beside it (three more such islets remain, by Kyras, the
  Utopian Republic and Kianhua; the author was asked).
- "Tsuruma 6", the island far south of Arpino labelled TS, was read as Tsuruma's on
  2026-10-11, but TS has been Terrabis-Seran's code since 2026-10-05, and it is
  Terrabis-Seran's. A code two nations use, on land far from both, needs asking.
- Moving states renumbers the generic names ("Usnistan 3" became "Usnistan 2"), since
  they count each country's states in map order: refer to states by pixel, not by those
  names, once they may have changed.

**Atlas, second test: squares, no art, no country names** (2026-10-07, screenshot)
- Squares and a stair-stepped coast: the flattened heightmap (land 98, sea 89) put a
  cliff at every coast, and the terrain mesh is coarser than the map's pixels, so the
  coast and the surface snapped to its grid. The coarse field of the
  `GRADIENT_BORDERS_FIELD_COUNTRY_*` overrides may add to it. Fix: Valsora's own
  heightmap, base-game gradient borders.
- No art: the screenshots are at the zoom where HOI4 swaps the 3D terrain for its flat,
  shader-drawn map; textures don't reach it. Only shader files can (needs vanilla
  `gfx/FX` from the author's install).
- No country names: unknown. The font texture decodes correctly with an independent
  decoder; the kerning block (the base game's map font has none) was removed in case
  the game rejects it. Asked whether names showed without the submod, and for error.log.
- Also removed, as unverifiable: the victory-point symbol strip.

**The Atlas submod looked murky and blocky** (2026-10-07, author's screenshot)
- Causes: the political map mode draws an opaque colour over land and sea unless
  `NMapMode.MAP_MODE_TERRAIN_TRANSPARENCY` / `MAP_MODE_NAVAL_TERRAIN_TRANSPARENCY` are 1,
  so none of the paper, waterlines or sea lettering showed (flat grey-blue sea, country
  colours over grey); the 26 px country band is drawn on a coarse grid and stepped; the
  paper tile had chain lines that didn't divide its 256 px and four differently seeded
  copies, so it repeated as a grid of small squares; the town symbols' paper halos
  showed as white blobs when zoomed out.
- Fix: both defines at 1, band 2 / 9 px, one quiet seamless tile, smaller and fainter
  halos. Not yet re-tested in game.

**Rivers looked odd up close** (2026-10-06, author's screenshots)
- Cause: major rivers were drawn at widths 7–9 and minor ones at 4–5, which is far too
  wide beside Valsora's small (~150 px) provinces. Also, Merlovich's and Hoalepa's
  rivers, added later, had never had their provinces re-cut, so only 13–58 % of their
  pixels lay on a province border: the rivers ran through provinces and borders crossed
  them.
- Fix: widths are now major 7–8 (still "large rivers") and minor 3–4. `river_provinces.py`
  re-cut the 30 states whose rivers weren't on borders (now 91 % map-wide) and leaves
  states that are already aligned alone.
- Not fixed: a river running diagonally is a 1-pixel staircase (HOI4 requires
  edge-connected river pixels), which the game draws with slightly wavy banks.

**Every army started with no manpower; opinion modifiers showed their raw keys** (2026-10-04, author)
- Cause: an OOB division takes its men from the country's manpower pool, and the pools
  were tiny: state population was 20 per map pixel (75 million people in the world,
  7,000 in Seigne). `start_manpower_factor` didn't prevent it. The opinion modifiers
  had no localisation, so the game showed `valsora_against_communism`.
- Fix: population is 300 per pixel; each country gets `add_manpower` for its starting
  divisions before `set_oob`; the modifiers are named "Seran Ties" and "Seran Biases".

**Aislada's drawn states were split, and Kurikia's eastern island was missed** (2026-10-04, author)
- Cause: Aislada's regions were cut into one state per city, so regions with two cities
  became two states; the island east of Kurikia has no outline, so nothing seeded it.
- Fix: Aislada's regions are one state each (`regroup_states.py`, `DRAWN_PLACEHOLDERS`);
  the island was given to Kurikia as one state.

**A city name misread** (2026-10-04): "Grande Rebette" is Grande Reliette.

**Drawn states cut into many small ones** (2026-10-04, author: "I want to cut back on the number of states")
- Cause: `apply_outlines.py` cut every drawn area over 1,000 px into ~650 px states,
  even where the author had drawn the states themselves.
- Fix: `regroup_states.py` makes each drawn area one state wherever a country has its
  own state lines; blank countries get ~1,300 px states. 1,346 states became 1,208.

**The Marches had the wrong flag** (2026-10-04)
- Cause: the three-lozenge flag was taken for The Marches; the author's flag file names
  it "Duchy of the Mountains" and The Marches' is the diagonal sword ("Marchers").
- Fix: flags now come from the author's flag file by layer name (`import_flags.py`).

**Country names written on the border layer** (2026-10-04)
- Cause: "Sicilianzo" and "Danelaw" were on Necessary Borders, so their letters closed
  off tiny patches.
- Fix: the letters were moved to Necessary Names.

**Two more islands fused to the land next to them** (2026-10-04, author)
- Cause: in the original drawing these islands touch their neighbours only at a corner
  pixel or through 1-2 px channels, so the strait tracing of 2026-09-28 saw one landmass
  and shrinking closed the channel.
- Fix: `pdn_tools.py channel` cuts the cheapest water-to-water path (fewest land pixels)
  between two sea pixels: the AN island at (654, 1430) and the larger island south of it
  (11 px), and a 2 px bridge at (932, 1492).

**The author's .pdn had lost Locus and the Moelle/Maïeul split** (2026-10-04)
- Cause: the upload was edited from a copy made before 2026-10-02, so its game layers
  (Provinces, States, Countries) were older in the north-east.
- Fix: as the working rules say, the current game layers were kept and only the
  author's own layers (outlines, names, rivers, cities) taken from the upload.

**San Sierra was skipped by apply_outlines** (2026-10-04)
- Cause: `LEAVE` still held a pixel of "the land south of Entroterra and Estande" from
  2026-10-01, which is San Sierra.
- Fix: that entry was removed.

**Rouental's divisions started with next to no manpower** (2026-10-02)
- Cause: an OOB division without `start_manpower_factor` takes its manpower from the
  country's pool, and the Feudal Army (−80 % recruitable population) leaves that tiny.
- Fix: every OOB division sets `start_manpower_factor = 1.0`.

**Lanzerac and Guedelon left the Association (and the Alliance of the Vale) at once** (2026-10-02)
- Cause, most likely: they are the only democratic members of a monarchist-led
  faction, with 20 % monarchist support; vanilla needs 30 % for the leader's ideology
  (`IDEOLOGY_JOIN_FACTION_MIN_LEVEL`). Not yet confirmed in game.
- Fix: they start with 30 % monarchists. The Reibonnaise nations also get +20 opinion
  of each other and an AI alliance strategy.

**The fief overlay sorted fiefs into the wrong kind of vassal** (2026-10-02)
- Cause: the 14 headings of `rouental_fiefs.txt` were read as vassals. They are cultural
  groups: every fief is a vassal of the Crown, and the governorates have no power.
- Fix: the docs and data now call them cultural groups
  (`source/rouental_fiefs_by_state.json`, renamed from `rouental_vassals.json`). The
  fief → state placement stands; levy tiers wait for each fief's title.

**Rempart and Tocsin didn't touch, though the drawing has them touching** (2026-10-02)
- Cause: the author's lines leave a corridor 2–3 px wide from Rempart up to Tocsin. A
  state is the majority of each province, and the corridor's pixels belonged to a
  province lying mostly in the neighbouring state, so the corridor went with it.
- Fix: the 17 corridor pixels were given to Rempart's nearest province on the
  Provinces layer (two 1 px leftovers joined their neighbour). Very narrow drawn
  pieces can lose out this way; a scan found a few other spots worth a look.

**Some new rivers were missing, and some minor rivers came out major** (2026-10-01)
- Causes, in `rivers.py`:
  - A whole river got one size, from the majority of its pixels, so a minor stretch
    drawn onto a mostly major river (the Prestozza branch) became major.
  - Where the main river takes a diagonal step it gets a corner pixel. When that
    corner was exactly where a tributary joined (the Gallyo river), the tributary was
    taken for part of the main river and skipped.
  - A tributary ending next to a 45° stretch of its river can't join it with one
    pixel without making the river two pixels thick (the Ossilia river), so it was
    dropped.
- Fix: each pixel's size follows the layer it was drawn on; branches off a corner
  pixel are followed; a tributary that stops short is joined by the shortest clean
  path of up to 6 pixels. Every drawn line is now traced.

**Royalist Illiricium's redrawn flag** (2026-10-01)
- The author preferred their original; it is back, as sent.

**Royalist Illiricium's flag looked squashed and noisy** (2026-10-01)
- Cause: the flag is about 2:1 with fine gold filigree. The game's flag is 82×52
  (1.58:1), so it was squeezed sideways, and the filigree turned to noise at that size.
- A redraw at 82:52 was tried and rejected by the author (see above).

**Every country showed its leader's name on the map** (2026-09-30)
- Cause: the new leader characters were named `TAG_<subtype>` (e.g. `NSC_despotism`).
  HOI4 looks a country's name up as `TAG_<subtype>` before `TAG` (that is how vanilla
  names Germany under Nazism), so each leader's name became the country's name.
- Fix: leaders are now `TAG_leader_<subtype>`. Check: no character may be named
  `TAG_<ideology or subtype>`.

**Estande's green blended in with Rouental** (2026-09-30)
- Fix: Estande uses the red of its flag instead.

**Unzipping asked about 9 or 10 "files with the same name"** (2026-09-29)
- Cause: Windows ignores upper/lower case, so `ROU_COMMUNISM.tga` (cosmetic-tag flag)
  and `ROU_communism.tga` (ideology flag) were the same file there.
- Fix: cosmetic tags renamed `TAG_GOV_<IDEOLOGY>`. Check: no two files in the mod may
  differ only by case.

**Almost every country had the wrong map colour** (2026-09-29)
- Cause: HOI4 takes map colours from `common/countries/colors.txt`, not the colour in
  each country file; tags missing there get made-up colours. (Theocratic Rouental was
  right because cosmetic-tag colours come from `cosmetic.txt`.)
- Fix: the build writes its own `colors.txt` for every country.

**The fifth ideology overflowed the party list in the politics screen** (2026-09-29)
- Cause: vanilla's box holds four 16 px rows.
- Fix: the mod ships vanilla's `countrypoliticsview.gui` with 13 px rows. Check: the
  rows must fit.

**Superevent text was hard to read** (2026-09-29)
- Cause: the typewriter fonts draw dark text on the dark window.
- Fix: title and quote are coloured white (`§W…§!`).

**Superevent had no music and no background** (2026-09-29)
- Cause (music): `play_song` only finds songs that belong to a music station ("Song
  doesnt exist" in error.log). Fix: a "Valsora Radio" station with the song.
- Cause (background): vanilla's window sprite is see-through. Fix: a generated dark
  background with gold frames.

**"Failed to generate a portrait / name" and "unknown continent europe"** (2026-09-29)
- Cause: vanilla's generic portraits and names are keyed by Earth continents and
  countries, which don't exist on this map.
- Fix: portraits per Valsora continent and name lists per country (`cultures.py`).
  Scientists still have none, so "failed to generate a portrait … scientist" remains.

**Islands fused to their neighbours** (2026-09-28)
- Cause: shrinking the world to game size filled in narrow straits.
- Fix: straits are traced at full resolution and kept open (44 reopened). One more,
  closed into a lake west of Romanoddle, was reopened by hand on 2026-09-30.

**Communist Merlovich never took over after "Fucking Explode"** (2026-09-28)
- Cause: `recruit_character` only works in history files ("should only happen in
  game/history files" in error.log).
- Fix: both Merlovichs are recruited at game start; the focus promotes the communist.

**error.log: "Palette in rivers.bmp is probably not correct"** (first build)
- Cause: the 8-bit BMP header said 256 colours used; vanilla writes 0.
- Fix: `biClrUsed = 0` in every 8-bit BMP.

**error.log: a malformed empty row in buildings.txt** (2026-09-28)
- Cause: a trailing newline at the end of `buildings.txt`.
- Fix: no trailing newline.

## Map problems found while building

**Deco UI: the top bar's date box was too narrow for 20xx dates** (2026-10-15, `validate_preview.py`)
- Cause: the box (220 px) was sized for 1936-1949; "2" is wider than "1" in the date font, and the widest date
  the game shows from 2036 to 2049, "00:00, 30 September, 2040", is 230 px. The game cuts a longer text short.
  The preview's long sample was still "23:00, 29 September, 1939".
- Fix: the box is 230 px (x 55), the speed chevrons 6 px further right; the long sample is now that widest
  date, so the check covers the worst case.

**`collages.py` listed Earth's 364 tags as nations still without a flag** (2026-10-15)
- Cause: since 2026-10-14 the build ships a stand-in history for each of Earth's tags, and the collages took
  every history file for a country of ours; with `--continent`, their capital (state 1) put them all on one
  continent.
- Fix: Earth's tags (`source/vanilla/index/tags.txt`) are left out, as `country_list.py` does; flags of
  countries in `COUNTRIES` owning nothing are labelled "(off the map)".

**check_mod: 132 errors, sprites of the Deco UI's `nationalfocusview.gfx` "point at missing" textures** (2026-10-15, build)
- Cause: to give the focus in progress its own picture, the Deco UI ships the game's `nationalfocusview.gfx` with
  `GFX_focus_current` changed; its other sprites still name the game's textures (`tiled_focus_bg.dds`,
  `focuslink.dds` ...), which the game has and the mod doesn't ship. The check wanted every texture in the mod.
- Fix: a game sprite (`source/vanilla/index/sprites.txt`) may name a texture the mod doesn't ship, unless the
  texture is in a folder of ours (`valsora…`, `VAL/`): removing the Deco UI's `current_bg.dds` is still an error
  (mutation-tested).

**The Gazetteer's map tools, releasables and admins, found while testing them** (2026-10-15, later)
- Facts entered on a nation whose states the build had cut would land in the wrong places once
  the author drew its states (state facts on whichever new state holds their pixel, one replacing
  another; terrain on re-cut provinces). Fix (author's idea): a nation's map tools open only once
  its states are the author's (`gazetteer.finals`), and the import drops a closed nation's map
  facts.
- Seven tabs didn't fit the 390 px column on a desktop (483 px wide): State and Nation scrolled
  out of sight. Fix: the column is 420 px and the tab labels tighter.
- Run from `scripts/`, the import couldn't find the last build (so it couldn't tell whose states
  were drawn) nor the base game's tags, and named a releasable LIB, Liberia's tag. Fix: it
  refuses to run outside the repository's root.
- The build looked tags up before it had added the Gazetteer's releasables (KeyError). Fix: they
  join `COUNTRIES` and the lookup together.
- A releasable without a ruling sub-ideology had no leader, and `check_mod.py` failed. Fix: it
  takes its nation's.
- Any refused save locked a player out with "This nation's password has changed", so under
  rules a step behind the page (before the author pastes new ones) a player saving a releasable
  would have been told so. Fix: the page first checks the nation's key; while it is there, the
  save is only "Not saved" (tested with the first rules in the emulator).
- The tests' sign-in waited for the Sign in button, which a nation's page hides. Fix (tests
  only): they wait for the Firebase SDK instead.
- The emulator can't reload its rules in this sandbox (the CLI's reload request is blocked and
  it stops, leaving the Firestore process running); and `pgrep -f`/`pkill -f` on a pattern in
  the shell's own command line stop that shell. Fix: restart the emulators with the rules file
  in place, and stop leftovers by their process id.

**The Gazetteer moved to a web site of its own** (2026-10-15)
- On claude.ai only friends invited by email as Editors could save; visitors through a public
  link can only view, and the author didn't want to ask everyone for an email. Fix: the same
  page as a web site (GitHub Pages, the `gh-pages` branch) with its atlas in the author's
  Firebase project; players need only their nation's password.
- Firestore keeps no array directly inside another, and rivers, railways and suggestions are
  lists of points. Fix: the page's store stores each point as `{"_a": [x, y]}` and reads it
  back as a list.
- Firebase's Cloud Storage now needs the paid plan. Fix: pictures (at most 640 px) are
  documents beside the facts, which the rules cap at 800,000 characters; a saved file carries
  them as `images` (`gazetteer.py import` reads them).
- Marking a nation finished wrote `true` over the player's name among its editors. Fix: both
  writes go through one function.
- Firebase's error codes have hyphens (`permission-denied`), claude.ai's underscores. Fix: the
  store turns them into claude.ai's, so the rest of the page is the same on both.
- Google's sign-in window can't load in Claude's sandbox (apis.google.com is blocked). Fix for
  the tests: a build for the local emulators (only) signs in with the emulator's unsigned
  tokens.
- `pkill -f "firebase emulators:start"` killed the shell running it, whose command line held
  the same words. Fix: stop background tasks by their task id.

**The Gazetteer's version 2, found while testing it** (2026-10-14, latest)
- The boxes for a nation's other pieces of land were rebuilt on every redraw (any saved fact),
  so a tap could land on a box that had just been replaced and do nothing (the phone test).
  Fix: built once per nation and screen size; a redraw only repaints their pictures.
- On a phone the boxes stacked over a third of the map. Fix: one row of small chips along
  the bottom.
- The lock box showed "null" under its Unlock button: `replaceChildren` writes a null child
  as text. Fixed, and the lock box stays hidden for the owner until their passwords load
  (it said "no password yet" for a moment).
- A locked nation's chip said "Saved". Fix: "Locked" from the moment it opens.
- A link to a nation not on the map yet (`#QZX`) opened nothing: that list arrives after the
  page starts. Fix: opened when it arrives; a link changed in the same tab opens too.
- Uploaded pictures were shown from the URL the upload returned, which the platform says not
  to keep (other viewers can't use it). Fix: only the asset id is stored, shown as
  `/_blob/<id>`.
- Owner tools' messages vanished when a snapshot redrew the section. Fix: kept in the page's
  state.
- With the Suggest tool the desktop toolbar wrapped Undo onto a second line at 1440 px. Fix:
  "Hubs" for "Supply hubs", the colour switch and Undo wrap together, and under 1360 px only
  the chosen tool shows its label.

**The Gazetteer, found while testing it** (2026-10-14)
- The ledger rebuilt itself after every saved field, so a field still being typed in could
  lose its text, and a field losing focus during the rebuild threw "The node to be removed
  is no longer a child of this node". Fix: panes re-render on the next frame, never inside
  an event handler, and a pane being typed in waits until focus leaves it.
- `check_mod.py` didn't know vanilla's `large_island` state category, which the Gazetteer
  offers. Fix: the categories and their building slots are vanilla's full list (1.19.3
  `common/state_category`). Check: factories and dockyards over a state's slots, building
  levels over vanilla's caps, unknown resources, railways between provinces that don't
  touch (mutation-tested).
- Text fields ran past the ledger's edge: the page's reset sizes boxes without their padding
  (`box-sizing: content-box`). Fixed with `border-box`.

**An upload based on an older map** (2026-10-13)
- The author's file was the map as it stood after the Usnistan update (commit 4a191cb),
  before the ten placeholder states changed hands and before 4,313 provinces were merged
  for the border limit; the author noticed the island below Cascadia in the old colour.
- Fix: their file was compared layer by layer with that version: only Necessary Borders,
  Names and Cities, Even More Reference and the new Islands to Add layer differed, and
  only those were taken onto the current map (whose game layers already had the
  island as Cascadia's).

**A line short of the coast, and a label on the borders layer** (2026-10-13)
- Texaria's eastern border stopped 8 px short of the inlet south of it, so Texaria and
  Gran Yucanoa were one patch; a "CI" was written on Necessary Borders west of Surredia,
  where its strokes would have cut the patch into scraps.
- Found by matching every label to the patch under it (two names on one patch) and by
  looking for letter-sized bits among the new line pixels. Fix: the line was continued
  to the inlet along its own row, and the letters moved to Necessary Names.

**The terrain test unrealistic in places** (2026-10-12, author: "make the generated
terrain logical, realistic, and consistent")
- Causes: Rouental's mountains were four invented round domes, while the author's fief
  map has the Vale of Reibonne's own ranges; rivers ran over the generated relief with
  no valleys; woods were blobs of noise, unrelated to the land; the north of Usnistan
  (the Levant's latitudes) was desert, as the westerlies' winter rain stopped at 38°;
  half of the Siberian taiga was tundra or dry grassland (a treeline at -6 °C, and a
  steppe threshold meant for warm climates); the Sahel met the jungle along a ruler-
  straight edge; Aislada's monsoons wet the whole island, so it had no outback; bogs and
  coastal fens were scattered blobs and thin strips along the coasts.
- Fix: the vale is built from the author's ranges (`source/vale_ranges.png`), with a low
  floor, hills along the rest of its land border and the Reliette gap open; every river
  has a valley whose bed never rises downstream, and the land where rivers are drawn is
  wetter; woods follow the relief (uplands, slopes, land above its surroundings) and
  farmland the lowlands, valleys and coasts; the westerlies reach 27°; the treeline is at
  -9 °C and trees need little rain in the cold; rainforest, dry forest and savanna grade
  into each other; Aislada's monsoons reach 20° and 110-200 px inland; bogs lie in
  basins, and coastal fens only along long, low coasts.

**Straight-edged strips in the terrain test** (2026-10-12)
- Cause: the moist air is carried inland one line of pixels at a time, so a lake
  (which refilled the air with moisture) or the end of a range on one line but not
  the next drew a straight-edged wet or dry strip; round hand-placed dry areas, forced
  marshes and straight ranges looked drawn with a ruler and compass.
- Fix: only the open sea refills the air, each sweep is blurred across the wind, and
  ranges, wet and dry areas and marshes get ragged, noise-warped edges.

**Letters on the Borders layer, moved one stroke short** (2026-10-12)
- The author's CU and RA labels (the Cultists', Kyras': 11 of them) were drawn on
  Necessary Borders, where they would have cut islets and coast into scraps. They were
  moved to Necessary Names a 14 x 8 box at a time, but "CU" is 15 px wide, so each U's
  last stroke (7 px) stayed on Borders and closed off a 2 px sliver of the Cultists'
  coast.
- Found by the dry run of the patch selection: the biggest patch with no seed (its
  "outside patch") was those 2 px. Fix: the two strokes moved too; the dry run then had
  no patch without a seed.

**Two codes drawn touching, and a label in the sea** (2026-10-12)
- Six labels were two codes drawn so close they touch ("CH CH", "US US", "FE FE", "RY
  RY"), each pointing at its own islet; read as one word, each named only one islet.
  Fix: such words are split letter by letter into codes: five more islets.
- "Port Almohavid" is written in the sea, and the land nearest it is Almohavid's, so it
  named Almohavid's whole patch. Port Almohavid is the 16 px tip of land a short line
  closes off at (3551, 1640).

**An islet left out of its country's states** (2026-10-12)
- The islet the author circled near Myehn (40 px) became a state of its own:
  `apply_outlines.py` joins a small islet to the nearest state of its country made in
  the same run, and Myehn's states are from 2026-10-11.
- Fix: `pdn_tools.py attach myehn 4752,1538`, as for Araseos 1.
- Also: Sennheiser's land was in `LEAVE` (2553, 933) since 2026-10-07; the check of
  `LEAVE` pixels against the seeded patches caught it, and it was removed.

**The sea didn't meet across the wrap** (2026-10-12, Merlo's update)
- Cause: Merlo drew the sea borders near the left and right edges separately. Of about
  13 borders reaching each edge, 5 met their partner exactly, 4 within 8 px, 3 were
  16-43 px apart, and 2 on the right edge had none; short line bits ran along the edge
  columns themselves, so one big province touched the right edge only through 18 rows
  of line pixels; and the provinces facing each other across the wrap were in different
  sea regions on 71 % of the rows (and the oceans' borders met the edges at different
  rows).
- Fix: `sea_provinces.py seam`: borders meet the two edges at the same rows (halfway
  between, or continued across the wrap), the sliver is pulled back, the lines near the
  edges are redrawn from the result, and the provinces facing each other share a region.
  A first try cut the sliver's province 28 px deep with straight lines; its neck is 5 px
  deep, which is all that goes now.
- Also: Merlo's two scripts point at folders on his machine, so `sea_provinces.py` does
  their job here. Two of his provinces are 312-313 px tall, over his own cutting margin
  (311) but under HOI4's limit (320): areas are cut only within 3 px of the limit.

**Two leaders named after words in a comment** (2026-10-11)
- Cause: vanilla's German and Russian name lists have comment lines inside them ("# From
  VGE"), and `cultures.py` read every word between the braces as a name, so Daravon's
  leader was "VGE Eisele" and Kurikia's "Nikita Russian". The game itself skips
  comments, so its own generated generals were fine.
- Fix: a drawn name that is a comment word is drawn again. The words stay in the lists
  as read, so no other leader's name changed: Daravon's is now Arthur Ziegler, Kurikia's
  Nikolay Giligashvili.

**Vanilla's Chinese, Vietnamese and Tibetan name lists; famous names in others** (2026-10-11)
- Cause: vanilla's Chinese list (CHI, and its copies for the warlords) has family names
  in both its given-name and surname lists, so every generated Chinese name is two
  family names ("Wang Zhao"); its Vietnamese one has a middle name (Văn) among its given
  names, so Plaija's leader came out "Văn Nu"; its Tibetan list is eleven names, with two
  titles (Dzasa, Rinpoche) among the surnames; its Buryat one has a name in curly quotes,
  which Gorduchai's leader showed ("“Dashi-dorzho” Barannikov"). Some lists hold famous
  people's names: the Indian one
  Gandhi, Modi and "Neru" (beside "Mohandas"), the Burmese one "Suukyi", the Armenian
  one Nzhdeh and Kajaznuni (beside Garegin and Hovhannes).
- Fix: our own Chinese (`CHN`), Vietnamese (`VNM`) and Tibetan (`TBT`) lists in
  `custom_names.txt`. The Chinese and Vietnamese ones have the family names where the
  game takes the first name, so names read family name first, as they do in those
  languages ("Wang Zhiyuan", "Trần Văn Hùng"). The Buryat name has straight quotes in
  `vanilla_names.txt`. The famous names are in `cultures.NOT_SURNAMES`, so no leader of
  ours carries them.

**Faction members with 20 % for their leader's ideology** (2026-10-11, a precaution)
- Cause: every country starts with 20 % for each ideology, and a faction member likely
  needs 30 % for its leader's (see Lanzerac and Guedelon, 2026-10-02); not seen in game.
- Fix: the Great Lake Republics' four members and the Synthesist Internationale's two
  start with 40 % for their own ideology, their leader's, and 15 % for each other
  (`nations.POPULARITIES`).

**The upload predated a change** (2026-10-11)
- Cause: the author's file was from before Araseos 1 went to Terreich, so its game
  layers still had the islet as Araseos (the only difference in them).
- Fix: `apply_outlines.py` ran on the upload, then `pdn_tools.py attach terreich
  935,1862` again.

**Estande's capital was on an island overseas** (2026-10-10)
- Cause: a country's capital is the sizeable state nearest the centre of all its land.
  Estande's islands east of Terreich (Araseos) and the six added on 2026-10-09 off
  Orientalis drew that centre out to sea, and the nearest state was one of its islands
  east of Terreich ("Estande 70"), far from its homeland. Found while making the flag
  sheet of Araseos, where Estande appeared.
- Fix: a capital on a continent holding under a third of the country's land is chosen
  again on the continent holding most of it. Estande's is now "Estande 30", in the
  middle of its homeland; no other capital moved (a plain "main continent only" rule
  would also have moved Anglost's, Krionik's, Peatiktist's and Terrabis-Seran's).

**A flag update was missed** (2026-10-09)
- Cause: `import_flags.py` called a flag unchanged when its mean difference from the
  stored one was under 3, a test meant for resampled copies of the same picture.
  Serie's four new corner anchors cover 4 % of the flag (a mean difference of 2.65), so
  they were skipped (the author noticed). The same test had kept Claude's redraw of
  Krionik's flag once the author's own file had it.
- Fix: at the same size any visible pixel counts; at another size both are compared at
  164×104, and more than 0.5 % of pixels off by over 40 counts. Re-imported: Serie,
  Krionik, and the file's 82:52 copies of Garfield, Troc and Terrabis-Seran (the same
  pictures; the stored ones were 490×327). Rouental's 1180×700 original is kept. The
  older flag files were checked too: nothing else was missed.
- Also found: see-through pixels, which the game shows as holes in a flag (Harwick's
  top row and Royalist Illiricium's gaps were filled by hand before). Belka's emblem had
  a soft see-through edge, Riverraine's and Belekria's flags a 1-px see-through frame,
  Garfield's one faint row. `import_flags.py` now lays every see-through pixel over the
  nearest solid one before comparing and saving (`opaque`), so a re-import can't bring
  a hole back; Ponchomagnifico's faint top row (from the friend's build) was filled the
  same way. No flag in the build has see-through pixels now.

**Provinces outside a new outline were changed** (2026-10-09)
- Cause: `apply_outlines.py` tidies the provinces in a box reaching 64 px past the
  outlined area. Old provinces the box's edge clipped looked split there, and their
  pieces under 300 px were merged into neighbours: 77 px of 11 provinces in Belekria,
  Sminishia and Krionik that no outline touched, some into another state. Earlier runs
  likely did the same along their boxes' edges.
- Fix: only provinces the outlines made or cut are tidied; the run was redone, and the
  map file now differs from the upload only inside the new nations.

**Half a state cut off by a new line became part of another state** (2026-10-09)
- Cause: West Sminishia's new line cut one of Sminishia's states nearly in two.
  `pdn_tools.py cede` joined every part a split state loses to a neighbouring state that
  moved whole, which suits slivers, so West Sminishia came out as one state of 2,484 px,
  twice a usual state.
- Fix: a lost part of 600 px or more (`CEDED_STATE`) is now a state of its own; West
  Sminishia has two states.

**Vanilla's Mongolian and Belarusian name lists** (2026-10-09)
- Cause: vanilla's MON list is 14 Chinese and Manchu names, and its BLR list is part of
  the Russian one (`country_list.py` even called a Russian-named country Belarusian,
  since it matched cultures on the first dozen male names).
- Fix: Sanada uses the Buryat list (BYA, a Mongolic people) and Belka the Russian one;
  `country_list.py` matches on every male name.

**A moved border between countries without state lines** (2026-10-09)
- Cause: the author's new line between Hwitland (now Scealand) and Eschland (now Artzen)
  fitted no tool. `pdn_tools.py border` gives away a whole line-enclosed area, but
  Eschland's coast has no line, so that area ran on into the sea around Daravon's
  island; `regroup_states.py` only redraws countries with state lines of their own; and
  two of Eschland's states and three provinces straddled the line, so repainting the
  land alone would not have moved the border (each state goes whole to the country
  covering most of it).
- Fix: `pdn_tools.py cede FROM TO X,Y`. Only FROM's pixels are cut by the lines, the
  provinces are split along the line, and the part a split state loses joins a
  neighbouring state that moved whole. One sliver touched only another sliver, so they
  merge in turn (the first try stopped there, before saving).
- Also: the upload was the author's previous file plus their edits, so its game layers
  predated the 2026-10-08 changes; only their own edits were merged.
- The decoded copies of four maps filled the session's temporary disk (1.2 GB each); the
  check was redone by comparing the built files instead.

**Harwick's flag had an empty top row; Kampf's layer matched no country** (2026-10-08)
- Cause: in the author's flag file the top row of the Harwick layer is transparent (a
  see-through line along the top of the flag in game), and the layer "Kampf Empire" is
  not the country's name (the Kampfian Empire), so `import_flags.py` skipped it.
- Fix: the row was filled from the one below it; "kampf empire" is an `import_flags`
  alias.

**Labels on the Borders layer again, and another stale LEAVE pixel** (2026-10-08)
- The author's island labels (SO, MA, KE, DU, "Mahina (MA)" ...) were written on
  Necessary Borders: 88 small marks among three real new lines. As lines they would
  have cut the islets into scraps. Fix: every new mark but the three lines (found as
  8-connected pieces, checked by eye) moved to Necessary Names before apply_outlines.
- `LEAVE` still held (297, 1887), which now lies in Zwintern's patch, and (554, 1814),
  now Ungar: both would have stopped those patches being assigned, as happened with
  Transcainia. Fix: removed; every `LEAVE` pixel is now checked against the seeded
  patches before a run.

**Transcainia's land stayed Araseos** (2026-10-07, author's screenshot)
- Cause: `apply_outlines.py` had an old `LEAVE` pixel, (403, 1359), from 2026-10-05.
  The new lines put it inside Transcainia's patch, and `LEAVE` beat the seed, so the
  patch was skipped silently. A first rerun with the full 2026-10-07 `OWNERS` also
  re-cut Großlöwenburg (a seeded, finished country whose states regroup had joined
  across lines); that was thrown away.
- Fix: the old pixel was removed from `LEAVE`, and the rerun seeded only Transcainia
  (6 new states). Lesson: rerun with only the new seeds, and check `LEAVE` pixels still
  lie in the land they were meant for.

**Borders on the wrong layers, a gap, and unlabelled patches** (2026-10-07)
- Cause:
  - The borders of Sminishia, Gorbastan and Zukchiva were drawn on Necessary Names.
  - "PE" and "(TP)" were written on Necessary Borders.
  - A one-pixel gap south of Ostaria joined Ostaria to Hwitland.
  - Seven unlabelled patches the new lines enclosed went to `DEFAULT_OWNER`.
- Fix:
  - Line-shaped pieces on Names moved to Borders, and letter-sized pieces on Borders
    moved to Names.
  - The gap was found by listing loose line ends.
  - The unlabelled patches are on `LEAVE`.
  - Each nation's land was found from the author's labels: a name takes the bordered
    area around it, an island label the land nearest it. A rendered proposal was
    checked before `apply_outlines.py` ran.

**A 5 px province in Kurikia stopped the build; San Sierra's state lines leaked** (2026-10-05)
- Cause: re-running `regroup_states.py` over every drawn country left a 5 px scrap at
  (1242, 856). Separately, two of the author's San Sierra state lines had gaps, so
  neighbouring areas ran together into one state: one missing pixel, and one line
  stopping 4 px short of the coast.
- Fix: the scrap joined its neighbour in the same state, and the gaps were filled. To
  find dead-end line pixels, look for line pixels with at most one line neighbour that
  are not next to water.

**`apply_outlines.py` ran for hours, and nearly gave Solitas land to Terrabis-Seran** (2026-10-05)
- Cause: the clean-up of cut provinces compared every province against the whole
  window around the new outlines. This time the window ran from Cascadia to Harwick,
  about 1,900 × 1,200 px with thousands of provinces. Separately, three Solitas patches
  that the friend's outlines had closed off were unseeded, so they would have gone to
  `DEFAULT_OWNER`.
- Fix: each province is now checked inside its own bounding box. The three patches are
  on `LEAVE`. The script lists unseeded patches before writing; read that list.

**A new country bigger than the rest of its continent was nearly skipped** (2026-10-01)
- Cause: `apply_outlines.py` treated the biggest patch touching a line as "the rest of
  the continent" and left it alone. Fraxhemark (96k px) was the biggest.
- Fix: patches with a seed, on the LEAVE list, or already done can't be "the rest".

**Regions cut up and land regions redrawn without being asked** (2026-09-30)
- The author asked for the oceans of their map "split up as needed"; I also regrouped
  every land region and cut the oceans into ~350k px pieces. The author wanted the land
  left alone and each ocean whole, to edit themselves.
- Fix: land regions restored exactly (pixel for pixel), each ocean is one region.
  Lesson: change only what was asked; when "as needed" is vague, do the minimum.

**Strategic regions from the author's ocean map landed in the wrong oceans** (2026-09-30)
- Cause: the reference maps (`ref_oceans.webp`, `ref_continents.webp`) show an older
  arrangement of the continents than the drawing, so they can't be laid straight over
  the game map. Averaging each continent's mapped position then put open water in
  unrelated oceans (a "Northern Friedlich" region mid-map).
- Fix: each continent's shift was fitted separately (Nonscio and Araseos too), and the
  continents vote for the ocean. Names of oceans running all the way round were
  scrambled by the map's wrap; they are now read left to right.

**The author's `.pdn` was older than the current one** (2026-09-30)
- Cause: the upload predated the sea zones and colour changes; applying it would have
  undone them.
- Fix: game layers are kept from the current file and the author's own layers
  (outlines, rivers, names) taken from the upload. The updated `.pdn` is now sent back
  after every change.

**Selto was drawn too small** (2026-09-30)
- Cause: only the patch between two lines became Selto; the author's older drawing
  (Notes layer) has it along the Piscary coast.
- Fix: five coastal Linterre states given to Selto (`pdn_tools.py give`).

**Rivers ran through the middle of provinces** (2026-09-30)
- Cause: HOI4 only applies a river crossing between two provinces.
- Fix: `river_provinces.py` re-cuts provinces so rivers run along their borders. Its
  first versions left 1-2 pixel provinces (a tiny state with nothing to split, stray
  pixels of neighbouring states); both are now handled.

**New state lines split existing states** (2026-09-30)
- Fix: `apply_outlines.py` re-cuts only the states a new line splits, keeping their
  country. At first it also re-cut Cardonia's island states (islets across water looked
  like splits) and merged small drawn pieces as islets; both fixed. Nudges of a pixel
  or two are too small to detect and are moved by hand.

**Outlines were meant as states, not provinces** (2026-09-29)
- Fix: every outlined patch is a state (big ones several), each cut into small provinces.

**Provinces split in two, too small, or crossing at one corner**
- Cause: cutting provinces leaves scraps.
- Fix: scraps merge into a neighbour; four-province corners are fixed by moving single
  pixels. Check: every province is one connected piece of at least 16 px, and no four
  meet at a corner (these crash the game).

**Rivers drawn as 2×2 blocks, stubs, or tributaries overwriting the main river**
- Fix: the river tracer shortcuts loops, drops branches under 6 px, and finds branches
  from the raw lines. Check: HOI4's river rules.

## Rules learned the hard way (all checked by `check_mod.py`)

- `definition.csv` needs Windows line endings (CRLF).
- `weatherpositions.txt` needs a `small` and a `big` row per region (not "large").
- Localisation files need UTF-8 with BOM.
- `descriptor.mod` and the launcher's `.mod` file must match.
- Vanilla files that name Earth places (tutorial, AI navy plans) are overridden with
  empty or cut-down versions.
- With the Deco UI in the mod (2026-10-14): localisation may be in the game's other languages, but only the
  Deco UI's files (`valsora_deco_*_l_<language>.yml`, first line `l_<language>:`); a .gfx sprite of any kind
  (cornered tiles, progress bars, pie charts, `textureFile` in any case) counts as defined, and its textures
  must exist; a sprite the game's own .gui files name without defining (`GFX_category_end_bg`) is allowed in
  the copies of those files the Deco UI patches. The first merged build failed all three (38 errors), plus the
  Deco UI's sub-ideology text naming the game's Earth-bound ones (nazism ...), which Valsora keeps defined but
  never localises: the Deco UI now lists only the sub-ideologies Valsora names.
