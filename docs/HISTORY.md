# Valsora: the build's history

The build's state, date by date, newest first. Moved out of `CLAUDE.md` on 2026-10-15 (the author: "Tidy up
the notes"); `CLAUDE.md`'s "Current state" keeps where things stand now. The nations' own record is
`docs/NATIONS.md`; every problem and its fix is `docs/PROBLEM_LOG.md`. Add each day's entry at the top.

The build began (2026-09-29) as a second attempt, deliberately minimal: the real geography with placeholder
square provinces, one placeholder country per continent, and only what the game needs to load. Borders, real
states and countries came next.

## Newest first

- 2026-10-15, the sixth round (the author: "Please give me the downloads for the mods, as well as everything else
  prepared since last night", then "Yes, please switch to using releases"): every file of the day sent again (the
  mods, the reports, the guides, the previews and design sheets, the map and flag files). The switch to GitHub's
  Releases page stopped at the first step: this session type may not create releases (HTTP 403). The author's choice:
  the zip stays in `dist/` for now; releases, by hand, for more substantial builds.
- 2026-10-15, the fifth round (the author: "Also allow people to create political advisors and companies on the
  gazetteer"): no map changes, the mod byte-identical (no nation has companies yet). **The Gazetteer's People tab**
  has a section for political advisors (with the political advisors' traits) and one for **companies**: an arms maker
  of one of the base game's 28 generic kinds (tanks, ships, aircraft, land equipment) or an industrial concern of one
  of its 14 kinds, with a name, a logo and notes, and "Ask for a new kind of company" as a request
  (`source/vanilla/index/companies.json`, from the game's files by `vanilla_sync.py`). The build makes an arms maker a
  military-industrial organisation of its kind (Arms Against Tyranny) and the designer of its kind (without it), a
  concern an industrial concern idea, a logo its 64 x 64 icon (the whole logo); `check_mod.py` checks organisations and ideas
  (`mutation_test.py`: 50 breaks, all caught). Tested in the browser (`tests/gazetteer/companies.py`) and through an
  import and a build of the test's file (check_mod clean). The site is republished.
- 2026-10-15, the fourth round (the author: "add the option to add base-game traits to leaders, as well as the option
  to request new traits", the crests, the globe "my current favorite of your designs", "Is there anything else you can
  do to streamline the modding process to make it more efficient without losing out on quality?"): no map changes.
  **The Gazetteer's traits**: rulers, party leaders, generals, admirals and advisors take up to six of the base game's
  traits (`source/vanilla/index/traits.json`, by kind and advisor post), and "Ask for a new trait" is a request; the
  build writes them, builds advisors into their post, and gives portrait-less generals and admirals a generic portrait
  of their culture; `check_mod.py` checks every trait, slot and idea token. The site is republished. The Deco UI is
  v0.8.3: the keystone's diamond lowered, the news masthead's **ringed newsreel globe**, and the superevent's crest
  that globe, **whole, across the frame's top edge**. **Streamlining**, each checked to give the same files:
  `run_all.sh` runs its checks, previews and zip side by side and replaces the zip only when the checks pass (a build
  with an unchanged map: 47 s); the Deco UI builds in 31 s (81 before); one command each for the larger flags' test
  version (`build_flags15.sh`, beside the mod), publishing the site (`publish_site.sh`), testing `check_mod.py`
  (`mutation_test.py`, 45 breaks: it found a real gap, fixed), fitting a flag (`fit_flag.py`) and a superevent's
  preview (`superevent_preview.py`); the Gazetteer's browser tests are in the repository (`tests/gazetteer/`);
  `requirements.txt` pins the libraries; the manuals are shorter (the Gazetteer's working detail is
  `docs/GAZETTEER_INTERNALS.md`, the Deco UI's version history `deco_ui/docs/HISTORY.md`); Merlo's handoff has the new
  commands (`docs/HANDOFF_MERLO.md` §7).
- 2026-10-15, later still: the author's flags of **Côtefer**, **Entroterra** and **Mezzogiorno**, fitted to 82:52
  without stretching (`docs/NATIONS.md`); 95 of the 161 nations on the map have a flag of their own.
- 2026-10-15, the third round (the author's answers and screenshots of the test decisions): no map changes. Fixed
  from the screenshots: the **state** and **operative** test events (a state event needs `trigger_for`; Rouental
  now gets an intelligence agency and an operative first), a long event option's **third line** spilling out (a 14 px
  option font), the superevent's **eight titles drawn over each other**, names like **KAMPFIAN EMPIRE** cut to their
  first word under the flag, and the **selected armies' badges under the flag medallion** (they, the air wings and
  the operatives start below it now). The Gazetteer's **generals and admirals are in the game** (Rouental's admiral,
  James Navy, wasn't: they were only listed for the author). The Deco UI is v0.8.2: the superevent's crest is
  **Valsora rising** instead of the guillotine, the event cards' a **stepped keystone**, the news globe **lit**; the
  other crests and globes (the first globe among them) wait in `deco_ui/art/proposals/crests/` and `news_globe/`.
  The releasable "Test"'s flag is fitted to 82:52 (its stripes' fly trimmed). A **test version with 1.5 times larger
  flags** (`docs/HD_FLAGS_TEST.md`) went to the author as its own zip, not into the mod. The author's answers: the
  VALSORAN STANDARD masthead stays; the panel pictures wait; terrain-sized provinces for deserts and the like, Rouental
  kept dense; the tech tree questions later; the author takes the test content out before the first public build.
- 2026-10-15, later (the author: "Give decisions to Rouental to spawn generic events of each type / layout, and a
  superevent for testing ... I'm not a big fan of the way the world news is looking though, it still looks lopsided"):
  no map changes. **Rouental's test decisions** (`scripts/test_events.py`): a "Test Events" category with one decision
  per kind of event window (country, a long one with four options, state, news, major news, leader, operative) and one
  for the **test superevent** ("This Is Only a Test": the anime picture and Entry of the Gladiators). The Deco UI is
  v0.8.1: the news masthead is **VALSORAN (globe) STANDARD**, two words of one width either side of a redrawn globe,
  and the news page is centred under it. `check_mod.py` now follows decisions too (the events and effects they use),
  and checks that our events' texts and our decisions are localised. Not yet seen in game.
- 2026-10-15, the second night (the author's notes on the previews, and: "try to find ways to improve and speed up
  the modding process without decreasing quality ... could you switch to the art deco fonts throughout the UI?"): no
  map changes. The Deco UI is v0.8: **the game's own fonts redrawn in the deco faces** (28: tooltips, lists, the
  designer, leader and unit screens, settings, window titles), a size or two under the game's so its text keeps
  fitting; the army bar's play / stop row centred over each general; event options centred between the picture and
  the card's edge; a gilt Valsoran globe in the middle of WORLD NEWS. A **mockup of larger flags**
  (`deco_ui/art/proposals/hd_flags/`, not in the mod) and **special projects** in the tech tree proposal (mechs, an
  orbital kinetic strike that works like a nuke: `docs/TECH_TREE_2036.md`, now eight questions). **Builds take a
  minute** instead of five, with the same files (`build_mod.py` 238 s → 26 s, `read_layers.py` skipped while the map
  is unchanged, the zip reproducible, the Deco UI's textures redrawn only when their drawing changes):
  `docs/SPEED_AND_SIZE.md`, with the repository's size (370 MB on GitHub, a third of it old copies of the zip) and
  options for the author. Not yet seen in game.
- 2026-10-15, overnight (the author's list: "Do the army bar, the event window, and a written proposal for the 2036
  tech tree. Tidy up the notes as well, and [find] the room under the border limit ... do the panel pictures, but
  don't put them in the mod yet"): no map changes. The Deco UI is v0.7: the **army bar** (the cards along the bottom)
  and the **events** (country, leader, operative and news events) in the deco style, with the fixes from the
  author's notes on the first army bar preview (the plate cut off above the marshal; the plus and the counts off
  centre). **Proposals for the side panels' own pictures** (research, production, the market, the overview strip,
  the intelligence agency, the army, navy and air spirit banners) wait for the author's approval in
  `deco_ui/art/proposals/panel_pictures/`, not in the mod. `docs/BORDER_LIMIT.md`: where the 62,183 province
  borders come from (3,353 left under HOI4's 65,536) and what provinces sized by terrain would free (about 8,000;
  impassable desert adds little, the terrain test's deserts being narrow). `docs/TECH_TREE_2036.md`: a proposal for the tech
  tree in 2036, with six questions for the author. The notes tidied: the nation record moved to `docs/NATIONS.md`,
  this history to `docs/HISTORY.md`. Not yet seen in game.
- 2026-10-15, latest: **Vilna moved** to Russovichia's land with the author's new flag, now Conservative and Jewish
  (the base game's Israeli names), **Placeholdgrad** on its old land with its old flag and government, Russovichia
  off the map (still 183 countries). The Deco UI is v0.6: the
  **focus tree after the mockup** (notched under the
  band, the country's title and sub-ideology in the header, medallions and plates per focus state, a gilt halo on
  the focus in progress, gilt links, red exclusive marks, the scale-pattern canvas; the focus icons are the game's,
  as the author asked) and v0.5.2's fix: closed side panels stayed on screen (the author's screenshot), so they rest
  off-screen again and open at once; the menu's career profile star moved off its label. The **superevent window**
  follows the mockup (`superevents_deco.py`). **Two starts** (Valsora: Rouental and Merlovich recommended; the Vale
  of Reibonne: the Association), so Back on the country screen returns to the scenario screen instead of looping.
  `on_startup` called the Reibonnaise opinions effect without a scope (the one line of the author's 10-line
  error.log that was ours, down from 2,081): it runs in a country scope now, and `check_mod.py` checks for it.
  Not yet seen in game.
- 2026-10-15, last: **Rouental's Gazetteer page is in the build** (`source/gazetteer/ROU.json`, read from
  the site with its password, which the author gave; the author removed its test hub and made Rêverie the
  capital again first): population 42.3 million over its 56 states, terrain for 132 provinces, 15 cities
  (Vair 20 VP, Rêverie and Carcarelle 15, eight new ones), one minor river along the Hollier border, a
  level 2 railway Rêverie–Seraine, the state kinds of Rouental (large city) and Saintiers (city), an
  admiral for the author's list, and the releasable "Test" (TES, cores on Avarre, Graisivaudan and Hevique;
  its flag, 640 × 338, still to fit by hand). 183 countries. The Gazetteer has **state capitals** (◆, one per
  state; the author: "There can be multiple cities in a state ... a way to select both a state and a national
  capital"). The Deco UI is v0.5.1: side panels rise into place instead of sliding across the flag and name.
- 2026-10-15, latest: the leftover placeholder bricks are gone (lakes one province each;
  Arvorenia, Atrocha, the KU island and a Belekria island group cut organically), Placeholdaire's
  and San Sierra's islands are one state each, so their map tools are open on the Gazetteer (39
  of 161). 21,078 provinces (20,690 land, 363 sea, 25 lake), 3,149 states, 62,183 province
  borders, 122 strategic regions, 182 countries. The Gazetteer counts the map's state names as
  named, shows each government's flag in game, picks releasables by whole states, and clips
  drawn states to the nation's land and to each other. Rouental's page (the author's test
  edits, read with its password on 2026-10-15) is not imported.
- 2026-10-15, later: the Gazetteer keeps a nation's map tools closed until its states are drawn
  (37 of 161 open), lets players define releasables, and has admins (Merlo, once the author adds
  him; the author is to paste the new rules). `docs/HANDOFF_MERLO.md` for Merlo's Claude. No
  facts imported yet, so the build is unchanged.
- 2026-10-15: the Gazetteer moved to its own web site, https://rouental.github.io/Valsora-HOI4/
  (GitHub Pages and the author's Firebase project); the author is to paste the database rules.
  No facts imported yet, so the build is unchanged.
- 2026-10-14, latest: the Gazetteer's version 2 (same link): a password per nation, flags,
  rulers, party leaders and characters with portraits, colour and culture, suggestions on the
  map, nations not on the map yet, overseas land in boxes of its own. No facts imported yet, so
  the build is unchanged.
- 2026-10-14, later still: the Gazetteer (https://claude.ai/artifact/PqTTD5FuFJhpL4JKp8sumN), for friends to fill in their nations; no
  facts imported yet, so the build is unchanged.
- 2026-10-14, later: no map changes; the Deco UI (v0.5) is part of the mod: every side panel flush under
  the top bar with the medallion's notch, map modes and a gilt minimap. Not yet seen in game.
- 2026-10-14: no map changes; the game starts in 2036, vanilla's generic events, AI
  strategies and on_actions are back, and stand-ins should take about 1,900 lines out
  of the 2,081-line error.log (decisions, Earth's histories, AI theaters, unit
  positions). Not yet seen in game.
- 20,817 provinces (20,416 land, 363 sea, 38 lakes), 61,400 province borders, 3,117
  states, 122 strategic regions (42 sea), 182 countries (2026-10-13, later: Santa Fe cut
  into 7 states, the last placeholder states given to their neighbours, so Orientalis,
  Usnistan and Solitas are left out; `dist/nations_by_continent.png`). Before: 20,778 provinces (20,377 land), 61,283
  borders, 184 countries (2026-10-13: Solitas outlined,
  nine new nations, the United States of Solitas removed, two islands added). Before:
  20,454 provinces (20,053 land), 60,318 borders, 3,065 states, 176 countries
  (2026-10-12, last: 4,313 small
  provinces merged for HOI4's border limit; before: 24,767 provinces (24,366 land),
  73,231 borders (2026-10-12, later still: ten placeholder states to their new
  owners; before: 3,070 states, 178 countries (2026-10-12, later: Usnistan outlined, 35
  new nations, 545 new states; before: 21,084 provinces (20,683 land), 2,629 states, 143 countries
  (2026-10-12: Merlo's sea, the wrap made seamless; before:
  21,366 provinces (645 sea), 91 strategic regions (11 sea) (2026-10-11: Orientalis
  outlined, 24 new nations, 667 new states; before: 16,646 provinces, 2,073 states, 119 countries (Araseos' last islet to
  Terreich); before: 2,074 states, 120
  countries (2026-10-09, later still: the Oriental Territories, and the
  Midtierre isles re-cut for Peatiktist); before: 16,625 provinces, 2,073 states, 119
  countries (2026-10-09, later: fourteen new); before: 14,812 provinces
  (two more from the Scealand line, 2026-10-09), 1,866 states,
  105 countries (2026-10-08: seven new; before: 14,334 provinces, 1,823 states,
  98 countries (with six more releasables, 2026-10-07, later; before: 92 (2026-10-07: twenty new nations, 521 new states; `dist/preview_new_nations_*.png`)).
  Before: 10,644 provinces, 1,377 states, 72 countries (with Rouental's six releasables and the Holy See). 2026-10-05, later: Terrabis-Seran 76 states, Kilkire-Battania 28, Garfield 10,
  Gaellia 7, Vineta 7, Harwick 1, Devlon 1 (`dist/state_numbers_araseos_southwest.png`,
  `state_numbers_garfield.png`, `state_numbers_san_sierra.png`). Before: 1,271 states (Llainfair's three became one),
  58 countries (2026-10-05, with the friend's Merlovich, Hoalepa and five nations south of
  Solitas). 2026-10-04, later: six more nations (Cascadia 37 states, Wersh 21, Troc
  15, Sicilianzo 14, Danelaw 20, Thorian 4) and the author's state lines kept as drawn
  (`regroup_states.py`): 1,346 states became 1,208. La Recolt and Réveillé became one
  state ("La Recolt"; the author's lines join them). 2026-10-04: the seven nations south of Estande (San Sierra 60 states,
  Anglost 55, Guardana 8, Normania 5, the Pollanas and Dremaur 1 each), Aislada's 13 drawn
  states with its rivers and 14 cities (capital Hirane, which replaced the joke name
  "The Great and Noble City of Merlovia"), four more Rouental cities (Seraine, Saintiers,
  Grande Reliette (misread as "Rebette" at first), Torres), and two more fused islands cut free (`pdn_tools.py channel`:
  the AN island at (654, 1430) and its neighbour, and a bridge at (932, 1492)). The
  author's upload had older game layers in the north-east (no Locus, no Moelle); the
  current ones were kept and only their own layers taken (author: Locus stays).
  2026-10-01, later: Kurikia 143 states, Fraxhemark 149; six Cardonian
  and two Royalist Illiricium states re-cut where new state lines split them; rivers
  edited (72 states re-cut along rivers, 92 % of river pixels on a province border);
  the first nine cities. 2026-10-01: Illiricium 18 states, Entroterra 9, Côtefer 5, Mezzogiorno 5,
  Royalist Illiricium 1, Rouental's islets 1; sea provinces recoloured blue on the
  Provinces layer (`pdn_tools.py blue_seas`). Second map of 2026-09-30: Estande 62 states (with 11 ES islands), Placeholdria
  28 (7 PC islands), Volinovia 16, Rastava 13, Coraliza 6, three RO islets to
  Romanoddle; a 1-2 px state-line nudge in Rouental (14 px moved by hand, too small for
  the split detection) and river edits (provinces re-cut: 47 states, 89 % of river
  pixels on a border). First map of 2026-09-30 added Romanoddle (90 states, with the islands the author's
  Names layer labels RO), Linterre (24, plus three LT islands), Selto (7: its outline
  plus five coastal Linterre states, author's correction from the Notes layer's older
  drawing), 13 re-cut Rouental states and new rivers in Rouental and Linterre. The
  island at (300, 785) was fused to Romanoddle's by 2-4 px land bridges that closed its
  strait into a lake; the strait was reopened (sea, its neighbour's sea region) and the
  island is Nonscio's own state (author). Earlier: Real: Rouental and its seven neighbours (56 states, about 175
  provinces), and Cardonia to the north (67 states, about 300 provinces). Cardonia is
  17 outlined patches plus nine islands the author's References layer colours
  Cardonian (seeded by hand). Everything else is still placeholder bricks. Two rivers
  in Rouental.
- **Rouental build loads and plays** (author, 2026-09-29): its error.log had nothing from
  our map or files, only vanilla noise and the name/portrait generation lines.
- **Loads in-game without crashing** (first build, confirmed by the author). Its
  `error.log` was vanilla-reference noise (decisions, missions, ai_faction_theaters
  region ids) plus the rivers.bmp palette warning above, which the biClrUsed fix
  silenced. Second build: only a trailing newline in `buildings.txt` (read as a
  malformed empty row, now removed) and "failed to generate a name/portrait" for our
  countries, which have no name lists or scientist portraits yet.

## Submods tried and removed

### Atlas submod (removed)

A "Valsora: Atlas" graphics submod (2026-10-07, `scripts/atlas_mod.py`, in git history,
last at commit 8a03ebf) tried to make the map look like a printed atlas with our own
textures: paper colour maps, engraved waterlines, sea lettering, compass rose and
cartouche, paper terrain tiles, ink border strips, a Cinzel map font (OFL), defines.
**Removed at the author's request after two in-game tests** ("maybe we'll come back to
it later"). What the tests taught (see `docs/PROBLEM_LOG.md`):
- Zoomed out, HOI4 draws a flat, shader-drawn map that no texture reaches; the look
  needs shader changes, which need the author's vanilla `gfx/FX` files.
- A flattened heightmap (a cliff at every coast) is drawn as stair steps and squares;
  `GRADIENT_BORDERS_FIELD/THICKNESS_COUNTRY_*` overrides draw a coarse grid.
- Country names didn't show with the replacement map font; the cause was never found.
It replaced the 2026-10-06 **Victorianization patch** (`victorianization_patch.py`,
graph-paper colour maps for Victorianization at Valsora's size; also in git history).

### Cartographic submod (removed)

A flat, HOI3-style "Valsora: Cartographic Map" submod was tried on 2026-10-01 and
removed at the author's request ("it wasn't great"); they may come back to it. It is
in git history (commit d2d6cd8, `scripts/cartographic.py`). It used
`GRADIENT_BORDERS_THICKNESS_COUNTRY_LOW/HIGH` = 2000 for solid country fill, a flat
`world_normal.bmp`, a khaki land colormap and a grey-blue sea with a 15° graticule.
