# Decisions worth keeping

Moved out of `CLAUDE.md` word for word on 2026-10-17 (`CLAUDE.md` keeps one line each). Each decision in full, with the author's words and dates. Add new ones here and a line to `CLAUDE.md`.


- **2036** (author, 2026-10-14: "Valsora takes place in 2036"). Everything the game dates
  moves a hundred years (`vanilla_parts.py`):
  - the clock: `START_DATE` 2036.1.1.12, `END_DATE` 2049.1.1.1 (vanilla also runs 13
    years) and `TENSION_TIME_SCALE_START_DATE` in `common/defines/valsora_game.lua`, the
    bookmark's date, and our history (last elections 2032, rulers' terms to 2065, order of
    battle files `<TAG>_2036`);
  - the tech tree: every technology's `start_year` (research ahead of it is penalised) and
    the tree's year labels (`interface/countrytechtreeview.gui`);
  - the date conditions of the generic content the mod ships (laws, the generic focus
    tree, AI templates and strategies, faction goals, special projects, raids, medals,
    events) and the game rule "war goals from focuses only, until 1938 / 1939 / 1940"
    (2038 ..., `diplomacy_scripted_triggers.txt`);
  - the generic names with years ("2036 Cruiser Hull", "Heavy cruiser 2040", the game
    rule's options), in `localisation/english/replace/`.
  Equipment keeps vanilla's `year`: licence costs count it from 1936
  (`LICENSE_IC_COST_YEAR_INCREASE`), so moving it would only make licences dearer.
  `check_mod.py` fails on any 18xx or 19xx date, `start_year` or tech tree label in the
  built files, and on a start date or bookmark outside 2036 (mutation-tested).
- **Railways wait** (author, 2026-10-15: "Let's leave railways off for now. The location of cities might change,
  and the mod doesn't need to be playable yet"): the map has only the lines drawn on the Gazetteer (one, Rouental's),
  so supply hubs away from a capital aren't connected. Don't generate a network until the author asks.
- **Province sizes by terrain** (author, 2026-10-15, on `docs/BORDER_LIMIT.md`: "For cases like desert, yes. But for
  others like Rouental, keep it dense"): when the Terrain layer is painted, deserts and land like them may get larger
  provinces to free borders; Rouental keeps its ~190 px ones.
- **The mod's zip stays in `dist/`, committed** (author, 2026-10-15: "Keep it as is. When we start getting to more
  substantial builds, I'll start transferring to the releases page"), and is sent in the chat too. A session like this
  one can't publish releases: GitHub's proxy answers "Creating, editing, or deleting releases is not permitted for this
  session type" (HTTP 403), so the Releases page, when it comes, is the author's to publish by hand (Claude gives them
  the zip and the notes). Don't work around that rule (no workflow or tag that publishes for the session).
  The old zips stay in the history too (author: "leave it until it becomes a problem"): removing them means
  rewriting it (`docs/SPEED_AND_SIZE.md`), only with the author's go-ahead.
- **Test content until the first public build** (author, 2026-10-15: "I'll remove all the test stuff before the first
  public build"): Devlon's spirits and Rouental's test decisions stay until the author takes them out.
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
- **Provinces are bricks** (at sea only until 2026-10-12, when Merlo's hand-drawn sea
  provinces replaced them; see Sea provinces below): 32 px on land, 128 px at sea, 48 px on lakes, with odd rows
  offset by half a brick so only three provinces meet at grid corners. Bricks never cross
  the seam (the edge half-bricks of odd rows are folded into their neighbour). Pieces under
  25% of a brick merge into the same-kind neighbour with the longest shared border.
  Remaining X-crossings (coasts, seam) are fixed by moving single pixels, never letting a
  lake touch the sea. **No bricks are left** (2026-10-15, author: "there are areas of the map
  that still have the old placeholder states and provinces"): every lake is one province
  (`pdn_tools.py lakes`: four lakes had 2-10 squares, 13 merged, among them the lake by Xue and
  Ungar's), and the land no outline run had reached, 87 brick provinces in 32 px squares and
  96 px grid states, was cut like an outlined patch (`pdn_tools.py recut`): Arvorenia's and
  Atrocha's islands (the friend's build of 2026-10-05; Arvorenia 34 → 56 states, Atrocha 14 →
  26), Kurikia's KU island and Belekria's island group south of the BE islets (their one state
  each kept, `--keep-states`, so Kurikia's map tools stay open). They are found as provinces
  whose borders with other land provinces run 60 % or more on the brick grid (organic ones:
  under 20 %). `dist/preview_recut_20261015.png` shows them before and after.
- **Straits are traced, not averaged** (`layout.channels`). Shrinking by area filled in
  channels narrower than ~1.5 output px and fused 21 large islands to their neighbours
  (author's report). The water's centre line is traced at source resolution and kept as
  4-connected water wherever the land on either side belongs to two different source
  landmasses. That reopened 44 straits. `dist/strait_fixes_map.png` and
  `strait_fixes_*.png` show each one before and after.
- **Islands under 16 px are dropped and ponds under 64 px filled.** About 660 islets go
  this way; they are 1–4 px specks at game scale.
- **Enclosed water becomes lakes**, including the author's inland seas (Piscary, Norlany,
  Sasurs).
  - The two inland seas that have islands are navigable sea (author's request), each in
    a sea region of its own: Nonscio's, south of Rouental, and Yastreovakia's northern
    one. They were made with `pdn_tools.py navigable`.
  - Other lakes stay lakes.
- **Sea provinces and sea regions are Merlo's** (the author's friend, 2026-10-12; merged
  with the author's approval, which reverses their 2026-09-30 wish to keep each ocean
  one region). Merlo drew the sea's borders by hand on a new layer, **Ocean Province
  Lines** (red lines), and his scripts (`build_sea.py`, `regroup_sea.py`, not in the
  repo: they ran on his machine) made 362 sea provinces from them in place of the 645
  bricks (35 areas over HOI4's size limit cut by wobbly lines, drawn into the layer
  too) and grouped them into 42 sea regions of about 9 provinces inside each ocean
  (South Demetric 8, Northern Ocean 6, North Menotius 6, South Menotius 5, Arctic
  Ocean 4, Northern Friedlich 4, Southern Friedlich 3, Midtierre Sea 2, North Demetric
  2, Piscary and Norlany 1 each); each province went whole to the ocean covering most
  of it, which moved 8.7 % of the sea to another ocean. Land, lakes and every other
  layer were untouched (checked pixel by pixel; one pixel at (2337, 933), sea on Terrain
  but painted into a Krionik land province, became sea), and his built mod matched our
  build of his file byte for byte. Our own `scripts/sea_provinces.py` now does the job
  from the layer: `build` (provinces from the lines; a line pixel keeps its province
  while that borders it, so unchanged lines give back the same provinces: 22 px
  differed on Merlo's file), `seam`, `names`, `check`. **The wrap is seamless**
  (`seam`, at the author's request): Merlo's borders met the two edges at different
  rows (up to 43 px apart, two with no partner, plus line bits drawn along the edge
  columns); now every border meets both edges at the same row (pairs bent to meet
  halfway; the right edge's border at row 229 continued across the wrap, which split a
  province: 363 sea provinces; a big province that reached the right edge only by a
  5 px neck, rows 958–975, pulled back), the lines within a few dozen px of the edges
  are redrawn from the result, and the two provinces facing each other across the wrap
  share a sea region (10 provinces changed region, the most even choice), so the oceans
  continue across it too. Names are "<ocean> <n>" west to east (`names`), the oceans'
  spelling as on the author's ocean map ("North Demetric", "Northern Friedlich").
  `strategic_regions.py` and `pdn_tools.py sea_zones` would undo all this and refuse to
  run on a map with the lines layer.
- **Sea regions were the author's oceans, unsplit** (`strategic_regions.py`, 2026-09-30,
  until 2026-10-12).
  Each sea province takes its ocean from `source/ref_oceans.webp` and each ocean is ONE
  region, as big as the map shows it: the author will edit them later. Split only where
  HOI4 forces it (a sea region must be connected); none needed it. 11 sea regions:
  Northern Ocean, North / South Demetric, North / South Menotius, Northern / Southern
  Friedlich, Midtierre Sea, Arctic Ocean, plus the navigable Piscary and Norlany seas.
  - The reference maps use an **older arrangement of the continents** than the drawing,
    so positions are mapped per continent: game → drawing through `work/layout.json`
    and the recovered centring shift (36, 16); drawing → reference by a per-continent
    shift fitted by overlap (Nonscio and Araseos fitted apart). Each continent votes
    for an ocean, weighted 1/(distance+20)²; stray bits join their neighbour; the top
    edge is forced to Northern Ocean and the bottom to Arctic (the mapping cut the
    Arctic in two).
  - An earlier version also regrouped land regions and cut oceans into ~350k px pieces;
    **the author rejected it**: land regions stay as they were (the grid ones), and
    oceans stay whole.
  - Sea names are keyed by region colour in `source/region_names.json`; land regions
    keep their generic names.
- **Region colours.** Sea regions are always blues (hue 0.53–0.70). Land regions are
  never blue, cyan or indigo (hue 0.42–0.82 is excluded), so the author can tell them
  apart on the layer.
- **States** bucket land provinces on a 96 px grid per continent, split into connected
  pieces; small island pieces join the nearest state within 160 px. **Land regions**
  bucketed whole states on a 384 px grid until 2026-10-16, when they were made from the
  nations (`land_regions.py`, the author: "could you please regenerate them taking into
  account the nations now on the map?"): 137 of them, of whole states, big nations cut
  into several, small neighbours grouped; **sea regions** bucketed sea provinces on a 512 px
  grid (Merlo's since 2026-10-12) and must stay contiguous. Lakes go into the land region
  they border most.
- **Countries**:
  - One placeholder per continent: NSC ARS AIS SLT YAS USN ORI (`SOL` is a vanilla
    tag, so Solitas is `SLT`); Araseos has no land left since 2026-10-09, nor Nonscio and
    Yastreovakia since 2026-10-12, nor Orientalis, Usnistan and Solitas since 2026-10-13,
    so ARS, NSC, YAS, ORI, USN and SLT are left out of the mod. Merlovich (AIS, still on
    the placeholder's paint) is the only one left. Until 2026-10-15 the placeholders were the only countries the
    bookmark recommended (author's wish, to keep the start menu short).
  - **Two starts on 1 January 2036** (`common/bookmarks/valsora.txt`, `build_mod.py`): **Valsora** recommends
    Rouental (author, 2026-10-15: "add Rouental to the recommended nations") and Merlovich; **the Vale of Reibonne**
    recommends Rouental and the seven other Association states (`nations.REIBONNAISE`), its picture the Vale close
    up with the eight lit and their borders (`minimap.close_up`). Two, because with one start the game skips its
    scenario screen, so Back on the country screen went to it and was sent straight on again: no way back to the
    menu (the author's video, 2026-10-15). The histories are short and factual; the author may write their own.
  - Colours follow the flags (author): Rouental royal green, Guedelon blue, Hollier red, Seigne white,
    Evriches yellow, Lustiana black, Selgrave dark maroon, Lanzerac purple (its new flag's,
    2026-10-09; dark gold before), Cardonia deep purple (kept when its own flag, black,
    white and navy, came on 2026-10-14). Guedelon's blue and Hollier's red are their flags' main colours. `pdn_tools.py recolour Countries OLD=NEW` keeps
    the `.pdn` in step.
  - **Every nation's record**, who drew, named and decided what and when, is `docs/NATIONS.md` (moved out of this
    file on 2026-10-15). As built: 194 countries in the mod, the 160 on the map and 34 that own nothing at the start
    (Rouental's 13 releasables, Belekria's 9 republics, Krionik's 3 principalities and Formosa, Pakitsk, the civil
    war's 7);
    `dist/countries.md` lists every country's names, government, culture, ruler and states. Off the map but kept in
    `COUNTRIES`, and so left out of the mod: the United States of Solitas (to come back as a formable) and
    Russovichia (author, 2026-10-15).
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
      line).
    - A map colour comes from the flag where there is one, and moves off a neighbour's it would merge with. A flag
      that comes later doesn't change the colour unless the author asks.
    - Flags in another shape are fitted to 82:52 without stretching (Flags, under Nation content).
  - The adjectives of the neighbours are guesses; the author may rename them.
- **Rouental's states are its fiefs** (author, 2026-10-20: "Let's go with the 30 pixel version for the test. Add it to
  the mod, and please update the pdn as well"): the author's fief map (`source/Rouental Fiefs.pdn`) read onto the game
  map by `fief_states.py`, a state for every fief of 30 game px or more, the smaller merged into a neighbour,
  crownland only with crownland (the red Fief Markers: "the areas currently under the direct control of the Sacred
  Prince") and within the governorate; the states' lines on Necessary States for the author to edit. The lore of the
  crownlands and governorates is in `docs/NATIONS.md` (2026-10-20).
- **Rouental's governorates are shown first, played later** (author, 2026-10-21: "They should be shown, and will
  eventually affect play. They'll hook into the levy system, with your relationship with the governorates affecting
  manpower in their provinces and the quality of their levies"; "for now they should be the strategic regions, and
  lines on the state panels. I'll work more on them later. Royal fiefs should also have a line on their state
  panels"; "Eventually I will get around to the Governorate Lines"): the fief map's rough patches, named
  (`source/governorates_ROU.json`; 15, 18 and 19 one, Terres Séparées), are Rouental's strategic regions
  (`scripts/governorates.py`), and the state panel says each state's governorate and whether it is a Royal Fief.
  Terres Séparées is two regions (author, 2026-10-21: "instead of the Severed Territories in the east being a weird
  disconnected region, it should instead be two regions. South Montvallée should encompass Hollier, Evriches, Seigne,
  Serpette, and Chirac. North Montvallée should encompass Selgrave, Lustiana, Lanzerac, Moelle, Maieul, Serieux, and
  Petit Selgrave"), one governorate; Rêverie is a Royal Fief too ("Reverie still needs to be marked as a royal fief").
- **The governorates' screen, the design so far** (author, 2026-10-21, night; the mockups in
  `deco_ui/art/proposals/governorates/`): it opens as a larger window from the decisions tab ("Probably open as a
  larger window"), its map following the game's borders exactly ("Don't go with rough shapes"); no world map mode ("how
  useless it'd be for nations other than Rouental"). Each governorate shows its governor, loyalty and the attitude of
  its estates, and the states inside it with their levies; the Royal Fiefs are shown and handled apart.
  - **Governors are the Prince's appointees** ("the governors are appointed by the Prince, and aren't necessarily the
    rulers of the vassals in the region, but instead typically a member of the Prince's court or officials recommended
    by Rouental's estates general. (Except Crépuscule, which is always ruled by the Prince of Crépuscule, as part of the
    laws that bind them to Rouental.)"); they don't age or die ("I doubt the game will take place over a long enough
    period for that to work").
  - **The governorates hold little power** ("They were designed to try to centralize the nation, but completely
    backfired. The governor remains the crown appointee, and is responsible for trying their best to reign in the
    unruly vassals").
  - **Loyalty follows the peoples** (the fief list's cultural groups): "the Carcaraise people have a long history of
    enmity with the government in Rêverie, as they see Carcarelle as the true heart of culture in Reibonne. Likewise,
    the Nataine people are descendants of invaders from the Natin empire that settled in Rouental. Meanwhile, the
    Oscarl are fiercely loyal and grateful for being allowed to settle in Rouental, and the Chatois are the descendants
    of Nation slaves raised to lordship for their help in throwing back the invaders, and are ever loyal." ("Yes, I
    meant Natin.") The Nataine "aren't as quarrelsome as the Carcaraise, nor as numerous, but they are proud, refuse to
    integrate fully into Rouentaise culture, and can be prickly."
  - **The estates' attitudes change at their sessions** ("I like attitudes switching with estate sessions though,
    that's really good"); more attitudes to come from the author once the current eight each have something
    interesting to do.
  - **Levy quality is hidden until inspectors are sent** ("I LOVE the levy quality being hidden until you send
    inspectors"); its steps (Rabble, Militia, Drilled, Seasoned, Veteran) "good for now, but could do with a rework.
    After all, a city state's ceremonial crossbow corps might be small, but they could be very well trained. Maybe a
    late "ceremonial" category?"; then: "I was more thinking of it as a sidestep rather than another rung on the
    ladder. Ceremonial units would be poorly equipped, but highly trained. For example "The Blue Guard of Brume" might
    only be two or three divisions of leg infantry, but at elite experience"; better-trained levies by an action or
    later by the focus tree.
  - **Governorates may revolt** ("I like the idea of governorates revolting, to be sure"); more Royal Fiefs by
    provoking a revolt and annexing, or a ruler's death.
  - **The civil war**: governorates choosing sides may suit another, more traditional civil war path, not the
    communist one ("the complete collapse of traditional Rouentaise society, everyone against everyone. They're not
    too concerned about the arbitrary lines of the governorates": `docs/CIVIL_WAR_NOTES.md`).
- **The game's generic advisors and theorists are back** (author, 2026-10-21: "Sure, might as well bring back generic
  advisors and theorists"): vanilla's `history/general/generic_advisors.txt`, its Earth cases taken out, for every
  country (`docs/MAP_PIPELINE.md`, Vanilla content switched off).
- **State names** are the author's, in `source/state_names.json` ("x,y" of a pixel
  inside the state → name, since ids shift; `build_mod.py` stops if a pixel is in no
  state or two name one state). Unnamed states are "Country N". First set (2026-10-01):
  Rouental's 54 and its seven neighbours', numbered by `state_map.py`; then (2026-10-02)
  21 Chouan, the islets off Solitas Concorde et Volonté, and Rolantelle split by a new
  state line into Ghessone (west) and Rolantelle (east); Maïeul split into Moelle
  (north; Selgrave takes it in the civil war) and Maïeul (south). 2026-10-05: Cardonia's 27
  (from `dist/state_numbers_cardonia.png`; numbers 6, 11 and 12 merged into Llainfair, the
  island east of Coreilia). `state_map.py --names` draws a
  country's states with their names (`dist/state_names_<name>.png`).
- **Localisation keys are our own** (`VAL_STATE_n`, `VAL_REGION_n`), so vanilla's
  `STATE_n` / `STRATEGICREGION_n` Earth names never show. Victory point names have to
  reuse vanilla's `VICTORY_POINTS_<id>` keys, so they live in `localisation/english/replace/`.
