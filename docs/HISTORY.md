# Valsora: the build's history

The build's state, date by date, newest first. Moved out of `CLAUDE.md` on 2026-10-15 (the author: "Tidy up
the notes"); `CLAUDE.md`'s "Current state" keeps where things stand now. The nations' own record is
`docs/NATIONS.md`; every problem and its fix is `docs/PROBLEM_LOG.md`. Add each day's entry at the top.

The build began (2026-09-29) as a second attempt, deliberately minimal: the real geography with placeholder
square provinces, one placeholder country per continent, and only what the game needs to load. Borders, real
states and countries came next.

## Newest first

- 2026-10-18, night (the author's upload "HOI4_Mod_Map_10-18_1", their in-game findings in v0.10.2 to v0.10.4 and
  "Alright, get started"): **the map**: Usnistan's desert areas (`scripts/areas.py`: red impassable, yellow desert),
  the nine desert nations' states from their lines (60, 22 of them impassable as the base game's Sahara), the marked
  states cut coarse (`pdn_tools.py areas`: 486 provinces to 119), Rouental's and Terreich's new lines, provinces along
  the new rivers, Myehn's stuck islands cut apart (`pdn_tools.py necks`, 9 channels, 5 new strait crossings and Vilna
  2's): 21,093 provinces (20,705 land), 62,193 borders (3,343 under the limit), 3,179 states; **Deco UI v0.11**
  (`deco_ui/docs/VERSIONS.md`: the top bar's factory colours, decision plates, logistics and music button; the
  diplomacy and intel tabs like the politics screen; the panels' own pictures and the decisions tab in the mod; the
  focus filters centred; the game's icons redrawn as proposals); **a test decision for many alerts**; **the Gazetteer**
  shows the neighbours' terrain (republished).
- 2026-10-18, night (the author: "Do mockups of the panels and your replacements, but dont replace them just yet. Also do
  a tidy-up pass"): **mockups of the 16 side panels** with their own pictures drafted (`deco_ui/tools/
  proposals_panel_mockups.py`: v0.7's eight hand-drawn proposals and 47 more, in `deco_ui/build/`, not in the mod);
  **a tidy-up pass**: the stale border counts in `CLAUDE.md`, `docs/EDITING.md` and `docs/BORDER_LIMIT.md`, the
  country count in `docs/DECISIONS.md`, the decision badges' note in `deco_ui/CLAUDE.md`; every script compiled, the
  mutation test and the Gazetteer's tests run again.
- 2026-10-18, evening (the author: "continuing to stylized the other screens in Deco style. One specific one is the
  diplomacy screen ... I'd definitely like ... the leader portrait stylized the same way others are"; "when importing
  pictures of characters from the Gazetteer, try to center the image around the character"): **Deco UI v0.10.4**, the
  diplomacy panel's own pictures (`deco_ui/tools/diplomacy_art.py`: the leader's arched frame, the flag's frame, the
  politics block and its pie ring, the national focus button, the spirits band and the wells); **the Gazetteer's
  portraits cut round their faces** (`source/gazetteer/faces.json`: Port Almohavid's Usamah Lakhdar was cut in half,
  the full-length photos are head and shoulders now).
- 2026-10-18, later still (the author's upload, "I tried marking out areas which I know will be either tundra or
  extreme desert or jungle like base game africa. Maybe try generating provinces in those area with this in mind? Just
  a snapshot / preview, not for the full mod"; "The notification is still a dot, rather than the shape I specified"):
  **a preview of coarse provinces** in the marked areas (`scripts/coarse_preview.py`, not in the mod: 702 provinces to
  273, 195 or 154 at 500, 800 or 1,500 px, freeing 1,282 to 1,639 borders: `docs/BORDER_LIMIT.md`); the map in the
  repository unchanged (the upload's layer "Desert" and its new lines in Rouental wait for the author's word). **Deco UI
  v0.10.3**: the decision counts on plates shaped like the medallion's shoulders.
- 2026-10-18, later (the author: "a number of changes have been made on the Gazetteer. Please add them to the mod, I
  want to see how you handle a significant number of changes at once"; "I'd like a general increase of the province
  count"; "In the future you need a way to read the website directly"; screenshots of v0.10.1 and a mockup of the
  medallion; Sminishia's claims, the Illiricium and North Pollana crossings, the tundra, Belekria 64): **the Gazetteer's
  export** imported (17 nations with something entered: Rouental, Terreich, Ungar, Port Almohavid, Merlovich, Krionik's
  Formosa and others: `docs/NATIONS.md`), its 15 suggestions put on the map (`apply_suggestions.py`), Formosa's flag
  fitted (the dragon alone, the author's choice), the six new flags into the flag file (10-18-3). **More provinces**:
  `pdn_tools.py refine`, 20,552 land provinces to 21,148 (Evriches, South Pollana and Haidao 4 each), 63,531 borders
  built, 2,005 under HOI4's limit; Belekria 1, 4, 5, 6 and 15 re-cut coarse as tundra (84 provinces to 27), the borders
  that freed spent elsewhere. **Sminishia's claims** (`nations.CLAIMS`, checked by `check_mod.py` and the mutation
  test, now 58 breaks); **Belekria 64** to West Sminishia (now West Sminishia 1); **no crossings** between the
  Illiriciums or to North Pollana (413 left). **Reading the site directly**: `gazetteer_fetch.py`, a read-only service
  account (the secret `GAZETTEER_SERVICE_ACCOUNT`, the author's to add), tested against a stand-in for Google. **The
  Deco UI v0.10.2**: the medallion's frame from the author's mockup, shaded as the rest of the interface ("it doesn't
  have to be exactly the same"), the name centred; the experience badges centred; the factories military, naval,
  civilian; eleven faction flags a row; the state panel's corner clear; the events without corner brackets; the Release
  Nation window's list above its checkboxes, the state panel's resistance and compliance in gilt wells. Vilna 2 cut into
  its two islands. Problems met on the way (provinces left in two regions, the overhead
  measured on the wrong map, scraps of 1-2 px, a check breaking the next): `docs/PROBLEM_LOG.md`.
- 2026-10-18 (the author: the review deck of every Deco UI change, "no icon of the game's changes until I've seen it";
  the map and the flag file sent dated, "10/17-2, 10/17-3"; their own flag file, "If it's not corrupted, maybe it's
  being generated for a different update of PDN?"; the Gazetteer's guide for states, hiding suggestions, trait effects;
  a flag in Arabic calligraphy): **the flag file**: paint.net refused every copy of ours since 2026-10-13, because
  `writepdn.py` gave the new layers' blend modes ids that .NET's BinaryFormatter reads as the same as other new objects'
  (found by reading the files with .NET itself; `docs/PROBLEM_LOG.md`); fixed, checked by `pdn_check.py` and the new
  `scripts/pdn_dotnet/`, and the flag file written again on the author's own copy with all 101 flags
  (`New_Mod_Flags 10-18.pdn`). **The Gazetteer**: a state size guide, first (Cardonia's states, about 1,310 px and 7
  provinces each, as the usual size; Rouental's and Zukchiva's either side; the quick start's third step, a section on
  the Map tab, a row of Sizes, and each suggestion against Cardonia's states), the province guide kept after it;
  **Suggestions** above the map hides what was drawn with Suggest; every base-game trait shows what it does, as the
  game's tooltips say it (`vanilla_sync.trait_effects`). **The motto flag** ("a safe haven amid the storm") in four
  Arabic hands, white and gold on indigo, not in the mod until the author says whose it is
  (`dist/flag_proposals/safe_haven/`). The map and the mod are as on 2026-10-17.
- 2026-10-17, the second night (the author: Belekria's cores, a province size guide, the password search, "three or
  four big things to surprise me ... DO NOT ADD THEM TO THE MOD YET!", one a full mockup of the tech tree, and "ways to
  make the modding process more efficient both for you, and for me"): Belekria owns Tethia's and Kalnsfereta's states
  without its core (`nations.NO_OWNER_CORE`); the Gazetteer's password search keeps the cursor (the sections were
  rebuilt closed before the field took the focus back) and has a **province size guide** (Cardonia's ~160 px as the
  usual size, from the build: the guide's third step, a section on the Map tab, a Sizes ruler at the map's zoom, each
  suggested area's size in provinces); the corrupted flag file checked: every copy we wrote reads cleanly
  (`pdn_check.py`, now run on every file `writepdn.py` writes), and `pdn_recover.py` saves the layers of a damaged one.
  **The modding process** (`docs/WORKFLOW.md`): `pdn_diff.py` (every change between two `.pdn` copies, where, with
  pictures, and the borders to act on: the 2026-10-17 upload's three border moves found by itself), `pdn_tools.py
  owners` (settles them), `regroup_states.py --recut` (both checked against that night's hand-made result), and
  `CLAUDE.md` a quarter of its size (117 KB to 30 KB, the detail moved word for word into `docs/MAP_PIPELINE.md`,
  `docs/DECISIONS.md`, `docs/CONTENT.md` and `deco_ui/docs/VERSIONS.md`). **The Valsora Atlas** (not in the mod): the
  build's world in a browser, published as a private Artifact (`docs/ATLAS.md`). Three more surprises, none in the
  mod: **the tech tree's full mockup** (`docs/tech_tree_mockup/`: 559 technologies, 91 new and 468 of the game's renamed,
  the special projects and doctrines, the Cold War as the floor, a page with what each kind of nation starts with and
  every folder as an in-game screen, a private Artifact; nine questions in its README), **a world map poster**
  (`dist/posters/`, 9600 x 6570 in the Deco UI's style, 160 flags round it: `docs/POSTER.md`) and **the Deco UI's next
  20 screens** as mockups (`deco_ui/art/proposals/next_screens/`: the unit counters, division and ship details, trait
  trees, the peace conference ..., with what each would take).
- 2026-10-17, the night (the author's map, "Another thing to work on overnight: significant changes to the map", with
  three flags): **Yastreovakia redrawn**. Belekria south over Sminishia's north and West Sminishia's old land, West
  Sminishia over Sminishia's west end, Pakitsk into Belka (still releasable), Krionik's north-east to Belka and Kieska
  (`pdn_tools.py border` and `cede`). States drawn for Belekria, Krionik, Terreich, Kurikia, San Sierra, Sennheiser,
  Gorbastan, Zukchiva, the Sminishias, Pakitsk and Hollier (`regroup_states.py`, 3,149 states became 3,190), and the
  provinces of the states they changed re-cut at ~190 px (the lines had cut 1,468 provinces into pieces; 61,767
  borders after, 62,183 before); the first drawn provinces (Seigne's, Royalist Illiricium's: `pdn_tools.py provinces`);
  two islands cut free of the coast; five cities, Vazgorod Krionik's capital. Krionik a Regency Council (Monarchist)
  under the Council of Marshals, "the Royal Confederation of the Kriosnika"; Kampf Fascism, Sarkis Vanguardism: four
  great powers, one per ideology with Fraxhemark. Sombor Krionik's protectorate (a level of the mod's own) and the
  game's puppet allowed to Authoritarian overlords. Eleven new nations to release from the new Subregions layer
  (Belekria's eight republics besides Tethia, Krionik's three principalities with the author's flags), Pakitsk's
  cores, Sminishia's on its old land. The game's lines that open a sentence with "the …" capitalised (the author's
  screenshot of a capitulation). 416 strait crossings (two new islands). The Gazetteer's map tools open for 48
  nations (39 before). Rebuilt, all checks passed, 57 of 57 breaks caught.
- 2026-10-17, later (the author's screenshots of v0.10, ending "That's all for now I think"): **the Deco UI v0.10.1**.
  The loading pictures from Valsora's map out of the mod until the map is final (kept by `make_loading.py`; the loading
  screen had shown the game's own picture, game setup the last of ours); corner brackets off the loading boxes and the
  battle plan bar, its icons centred; game setup's country selection a card wider for "Other countries"
  (`deco_ui/tools/make_setup.py`), its details on one line and the ideology wheel as on the politics screen; the top
  bar's logistics in an 11 px font; the decision counts in the medallion's shoulders beside the seal; the division
  designer's combat width and the commanders' skill centred on where the game draws them (two helpers measured the
  screenshots: the game rounds a centred line's start up), the skill on a dark diamond; the fleet panel's long names
  in fonts that fit; the news story a size smaller, ending above the page's rule, and the events' text boxes taller.
  Rebuilt, all checks passed; the zip 24 MB (27 before: the loading pictures out).
- 2026-10-17, evening (the author: "Please start applying the proposed changes to all the UI screens"): **the Deco UI
  v0.10**. All eight suggestions of `deco_ui/docs/SCREEN_INVENTORY.md` and more, as pictures at the game's paths and
  sizes with its layouts kept: the four loading screens from Valsora's map (the proposal of 2026-10-16, now in the
  background list) and a gilt loading bar; scroll bars and sliders; the selected armies', fleets' and operatives'
  badges; the battle plan toolbar; the land and naval battles; the diplomatic action windows (a gilt line emblem per
  action); game setup (country and start selection); the window frames and popup headers the skin had missed; the
  settings, trade offer, variant designer, agency, insignia pickers, air missions, naval region and tutorial windows.
  Five helpers drew the screens side by side, one art module each (`deco_ui/tools/*_art.py`), reviewed against the
  game's layouts in previews (sent: they show the game's art beside ours). The inventory now counts 34 restyled, 45
  re-skinned (28 with their own pictures), 16 the game's own. `validate_preview.py`: PROBLEMS none; all Valsora checks
  passed; the zip is 26 MB (the loading screens add about 3 MB). Not yet seen in game.
- 2026-10-17, later (the author: "Apply all the green and yellow strait crossings, I'll judge the others later"): the
  414 strait crossings up to 10 px of sea are in the mod (`source/straits.json`, `straits.py approve --max-gap 10`);
  every landmass within 10 px of another is reachable on foot. All checks passed.
- 2026-10-17 (the author: "Sure, do 1, 3, and 7", of a list of things to do until they got home):
  - **Strait crossings, proposed** (1): `scripts/straits.py find` links every landmass once across its narrowest strait
    (a minimum spanning tree over open sea): 492 crossings for 606 landmasses, `dist/straits_map.png` (each ringed by
    width and numbered) and `dist/straits_proposed.json`; 72 islets lie over 20 px from any land. The base game's 151
    span 2 to 30 px (median 4). Nothing is in the mod until the author approves (`straits.py approve`, default up to
    10 px: 414); `build_mod.py` writes them from `source/straits.json`, `check_mod.py` checks every row (a new mutation
    break: 56). A test build with the 414 passed every check; without the file the zip is byte-identical.
  - **Draft names for the 137 land regions** (3): `region_map.py --draft`, `dist/region_names_draft.md` (nations'
    names, compass names round a nation's centre, its isles, the coasts of groups, the Vale of Reibonne); nothing applied.
  - **Every game screen against the Deco UI** (7): `deco_ui/docs/SCREEN_INVENTORY.md`, 95 screens: 34 restyled, 26
    re-skinned, 35 the game's own, and what to restyle next; thumbnails in the git-ignored `deco_ui/build/` (sent).
- 2026-10-16, later (the author's screenshots and `error.log` of the Deco UI v0.9, and: "could you please regenerate
  [the strategic regions] taking into account the nations now on the map?"):
  - **Land strategic regions from the nations** (`scripts/land_regions.py`): 137 land regions (80 before, buckets of a
    384 px grid that ignored borders), each of whole states: nations over 45,000 px cut into regions of about 30,000
    (Sarkis 11, Krionik 9 ...), nations of 18,000 to 45,000 px one region each, smaller ones grouped with small
    neighbours; Rouental and the other seven Association states are one region, the Vale. Sea regions untouched.
    Written on the Strategic Regions layer of `source/HOI4 Mod Map.pdn`; `dist/region_numbers.png` and
    `dist/region_names.md` renumbered for naming. 179 strategic regions in all.
  - **The Deco UI v0.9.1**: the map's names back (the map font's texture had grown past what the game loads; checked
    now, with the map's letters), dark ink in the designers' typewriter fonts, the doctrine tabs at their x, the
    faction screen's long names whole, the LEADER tag centred and the faction's flags in two rows, the seal's badges
    equidistant; in the top bar fuel, supply and convoys in the strip's last cell (the tray under it gone), the alerts
    across to the right-hand tray, that tray's edge clear of the music button, and the production alert a ring round
    its crown (the "odd green bar" was its halo, showing in the gaps).
  - The build: 179 strategic regions, 62,183 borders, all checks passed, the mutation test's 55 breaks caught.
- 2026-10-16, the night (the author's overnight list: "do 1 (though be prepared to possibly revert it,) 2, 3, 11, 12,
  and 13. Do maybe 3 or 4 loading screens as suggested in 8 as well, but don't add them yet"):
  - **The Deco UI v0.9** (1, 2, 3): the research trees and the doctrine screen under the focus tree's notched header;
    the four designers' and the commander pickers' pictures redrawn; one commit (`8dece16`), so it can be reverted
    alone. The faction's members' flags on the politics screen (assumed until seen). The focus in progress in the focus
    tree's header, a bar under a focus and a one-spirit card can't be built (no hook in the game:
    `deco_ui/CLAUDE.md` section 12). A check fails the Deco UI's build when a game window at the top left would sit
    under the medallion (`medallion_check.py`); it moved the hot-join window.
  - **Land regions numbered for naming** (12): `scripts/region_map.py`, `dist/region_numbers.png` (80 land regions),
    `dist/region_names.md` to fill in; `--apply` puts the names into `source/region_names.json` by region colour.
  - **The border budget for drawing the remaining states** (11): `border_report.py --drawn-states`,
    `docs/BORDER_LIMIT.md`: Rouental-sized states cost about 600 borders, but Rouental's province density everywhere
    about 8,150 (over the limit), unless provinces are sized by terrain.
  - **The Gazetteer's quick-start guide** (13): five illustrated steps the first time a player unlocks a nation,
    Guide to see it again; `tests/gazetteer/guide.py`; published.
  - **Four loading screens** (8), a proposal only: `deco_ui/art/proposals/loading_screens/`.
  - The build: 62,183 borders, all checks passed, the mutation test's 53 breaks caught.
- 2026-10-16, later again (the author: "I think I'll actually not reset it. Could you make sure the reset button is only
  available for me, not my admin, and that it requires two separate confirmations before resetting everything?"): the
  site's **Start over** is the author's alone (admins don't see it, and the Firestore rules let only the author write
  `planned/reset`, which the page writes before it deletes anything) and asks twice ("Yes, go on", then CLEAR typed);
  tested on the stand-in and against Firebase's emulators, published. The rules changed: the author pastes them again.
  Nothing was reset. The fonts: ỉ and ĩ without the i's dot, ă ĩ ũ composed in Federo (a specimen sheet of the built
  fonts showed both).
  The tech tree (the author: "I'd like to take inspiration from the fire rises and TNO. I might make the earliest era
  the cold war actually. I'm not sure how many years I want the game to last"): `docs/TECH_TREE_2036.md` has a new
  section, the tree's depth and the game's length: the base game's numbers from its files, TFR's and Millennium Dawn's
  from theirs, TNO's from its bug tracker, and what they suggest. Nothing built.
- 2026-10-16, later (the author's screenshots and `error.log` of v0.8.3, and: "I don't know if you're still giving
  nations the extra manpower ... please remove it", "is there a way you could reset any edits made thus far? I'd like a
  blank slate. The same goes for the mod. I'd like it just as it was on the last pdn, no extra rivers or internal
  borders"): **the Deco UI v0.8.4**: the focus tree's title in its header (the game's own title in large gilt capitals
  under a "National Focus" label; the scripted title had been docked in the tree's scrolling canvas, over the first row),
  opaque headers on the focus tree and the side panels (the map showed through faintly), the focus shortcuts' and the
  construction list's fold arrows in the deco style, the count badges (the decisions seal's and the top bar's others)
  as small gilt-rimmed octagons, the large tabs drawn 4 px in from each side (the captured commanders' overlapped), the
  empty general card's plus a smaller medallion in the middle of the chest, and the game's own bases on the fonts it
  redraws (`error.log`: the tooltip font's base against the game's Cyrillic file). **No extra manpower** for the starting
  divisions. **A blank slate**: the mod from the `.pdn` alone (Rouental's Gazetteer page, its river, railway, terrain,
  cities, admiral and "Test" releasable out: 182 countries), and Owner tools › Start over on the site, which clears every
  nation's entries (the author presses it) and keeps browsers from sending old copies back (`tests/gazetteer/reset.py`).
  Later still (the author: "would it be possible for you to attempt to make those letters yourself by editing the
  font", "for long names like Kampf, they ride up against the flag", "like the army, the navy is covered by the flag
  tab"): **Vietnamese letters in every font** the Deco UI ships (Plaija's names: Josefin Sans has them, the Federo and
  Bodoni Moda fonts have them composed from their own letters and accents), and `check_mod.py` fails on any letter of
  the mod's text or name lists a font lacks (53 breaks in `mutation_test.py`, all caught; the trait break moved to
  Serelle, Rouental's admiral being gone); a name needing two lines under the flag takes the small letters (34 tags);
  the navy's panel below the medallion. The fonts are named Valsora Deco Display, Sans and Italic (the OFL reserves
  Federo's and Josefin Sans' names). The zip grew from 21.3 to 21.9 MB (larger font atlases).
- 2026-10-16 (the author's answers to the tech tree proposal's eight questions): no build. Recorded in
  `docs/TECH_TREE_2036.md`, whose calendar, tiers, drones, battleship line and orbital strike were reworked from them:
  a realistic 2036 (what is in development now is in full service, most nations at today's level, the superpowers a
  little ahead); the tree begins where the base game's ends (gun battleships, then Kirov-like battlecruisers, then
  arsenal ships); nuclear weapons only for the superpowers, in small numbers; Krionik, Kampf and Fraxhemark or Sarkis
  as the superpowers; designed for the DLCs with fallbacks; drones as a support company, larger ones as aircraft, FPV
  strike drones down the recon line; special projects open to anyone but very difficult; the orbital strike weaker than
  a nuke, without fallout, unstoppable once launched and destroyable only by a raid before. The author is still
  brainstorming; nothing is built.
- 2026-10-15, the seventh round (the author: "Rouental's capital should be worth more VPs than Vair for example, even
  though Vair is bigger, right?", "give me a list of every function of the gazetteer", "Releasables already in the game
  should be represented on the site", "Leaders already in the game should be represented and editable, for example
  Roland or Serelle. Their stats should be editable as well as their traits"): no map changes, the mod byte-identical
  (the facts of Rouental's page have none of the new fields yet). **The Gazetteer**: victory points are labelled by what
  they mean (1 minor to 50 foremost, with the base game's examples), and a city has a size of its own (village to
  metropolis) that shares out a total population; the characters the game already has are on the People tab (the
  author's own, as Roland, Serelle and Mahaut, with every field, a sub-ideology within its ideology, and a commander's
  rank, skill and stats; generated rulers and party leaders as the defaults of their fields), and generals and
  admirals made on the site have a rank, skill and stats too; the Releasables tab has the releasables the game already
  has (Rouental's 13, Belekria's Tethia) and Rouental's civil war risers (7), each editable over the game's (names,
  government, colour, flag, ruler, states). The build patches the author's characters where they are (copies follow)
  and makes changed releasables facts of their own tags; `check_mod.py` checks commanders' skills and stats
  (`mutation_test.py`: 52 breaks, all caught). `docs/GAZETTEER_FUNCTIONS.md` lists every function of the site for the
  author to sort. Tested in the browser (`tests/gazetteer/ingame.py`, with `run.py`, `traits.py`, `companies.py`) and
  through an import and a build of the test's file (check_mod clean). The site is republished.
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
