# Open questions (2026-10-19, later: the author's answers recorded)

The list of 2026-10-19 with the author's answers. Nothing answered here is in the mod yet: everything waits for the
author's go-ahead ("do not fix these or anything else I send until I give you the go-ahead"), except the Association's
emblem, which they cleared to start (version C, a proposal: `dist/emblem_proposals/reibonnaise_association/`).

## Answered, to do on the go-ahead

| # | the answer | what it means for the build |
|---|---|---|
| 1 | Rouental's internal borders will be redone almost entirely on the new map | the city state and the cutouts come with it |
| 2 | the Cultists' path: will do | with the new map |
| 3 | tundra is white on the areas layer; impassable tundra white and red | `scripts/areas.py` reads white (tundra terrain, larger provinces) and white with red (impassable, one province a state), the editing guide says so |
| 9 | Sangrád and the three ports stay releasable; Sangrád is renamed **Visokagorod** (the city it is) | `common.py`, `FORMAL_NAMES` ("the Free City of Visokagorod"), `docs/NATIONS.md` |
| 11 | the motto flag is **Port Almohavid's** (it flies the Ruq'ah version, white, since the Gazetteer import); the options are sent again to choose from | `dist/flag_proposals/safe_haven/sheet.png` |
| 12 | the emblem: neither A nor B; the author's own design instead | version C (below) |
| 13 | James Navy goes (he was a test) | out of Rouental's Gazetteer facts on the next import, or from `source/gazetteer/ROU.json` |
| 16 | the readings of the Gazetteer's suggestions were right; the one error, Rosenburg and Terreichstadt cut out leaving very small provinces, the author has fixed on the map | (`docs/PROBLEM_LOG.md`) |
| 17 | the desert nations' map tools open (most opened by the author already) | `planned/unlock`, or `gazetteer.finals` |
| 18 | the Gazetteer stays on the download (no service account) | |
| 20 | fuel, supply and convoys stay in the top bar; its look can be worked on | |
| 21 | v0.9's restyled screens stay | |
| 22 | what to restyle next: the author's notes (below) | |
| 23 | the flags stay at the normal size; the larger flags' test is dropped | |

## Still open

4. **The desert provinces**: in Usnistan's yellow areas I cut the land into fewer, larger provinces, about 600 px
   each (normal land here is about 185): `q4_desert_provinces.png`. Keep that size, or larger or smaller?
5. **The marks of your upload of 10-18** (its layer then called "Desert") that the latest areas layer doesn't have:
   the white tundra lines along the north of Yastreovakia, a jungle north of Usnistan and a desert outline south of
   it (`q5_old_marks.png`). Dropped on purpose, or should they come back (as white tundra, now that tundra is white)?
6. ~~Kieska's bump~~: settled. You repainted it; it is Kieska's, with no Crvenognjište core.
7. **The strait crossings**: the map again, on today's map (`dist/straits_map.png`, each crossing numbered and ringed
   by its width). Mark the ones you want; the green and yellow ones (up to 10 px) are already in the game.
8. **My guesses for the eleven new nations** (tag, map colour, adjective, government, formal name; the names are yours):
   - Krionik's realms, Absolute Monarchy, "the Principality of …": Belska BLS (pale grey, Belskan), Koroletz KRZ
     (charcoal, Koroletzian), Targoviste TGV (blue, Targovistean), Kosavichy KSV (teal, Kosavichian), Lagrád LGR
     (sand, Lagrádian);
   - the city and the ports, Oligarchy, "the Free City of …": Sangrád SGD (violet, Sangrádian; to be Visokagorod),
     Port Nyasha PNY (crimson, Nyashan), Port Vostok PVS (silver, Vostokian), Port Grazda PGZ (gold, Grazdan);
   - the Sisterhood SIS (Sennheiser's; sea green, Holy Order, "the Sisterhood");
   - Xugang XUG (mauve, Xugangese; "the Territory of Xugang", Social Democracy, Terreich's puppet).
   All their cultures follow their neighbours (Krionik's Serbian names for its realms). Change any of it.
10. Flags for Belekria's eight new republics: when you have them.
14. State names: when you have them (the numbered sheets are in `dist/state_numbers_*.png`).
15. **The land strategic regions' names**: `dist/region_names_map.png` is the map with my draft name on each region
    (the draft, renumbered for today's regions, is `dist/region_names_draft.md`; the numbers alone are
    `dist/region_numbers.png`). Change any name in the draft's last column, or tell me the changes.
19. **The faction screen's goals**: the lined background at the top, then a gold line, then a solid colour, with the
    text over all of it, as a folder might be drawn. That is the game's goal-slot picture translated into the Deco
    palette by the automatic pass (`make_panel_pictures.py`); on the go-ahead it is drawn by hand instead, as the
    production lines were, the text clear of the line.
24. **Rouental's elite divisions**: you say there is enough manpower that they are refilled at once at the start, which
    lowers their experience; so they start under strength although their history asks for full strength
    (`start_manpower_factor = 1.0`). On the go-ahead I'll find why (the templates against what Rouental can field, the
    Feudal Army spirit's -80% recruitable population) and either make them start full or give them their experience
    after the refill.
25. **The tech tree**: the proposal is `docs/TECH_TREE_2036.md` and the full mockup `docs/tech_tree_mockup/` (its
    screens and the interactive page, https://claude.ai/artifact/4h5nttfGvLadmHfxjHiHi8). Your eight answers of 10-16
    are in. Open: **how long a game should last** (13 years as now, or longer), **how many generations each line
    shows** (the base game's have four big steps), **whether the nations behind catch up faster**, and **whether the
    tiers are held apart by development** (a feudal state unable to reach the top whatever it researches); and the
    special projects, which you were still brainstorming.
26. **The speed and size options** (`docs/SPEED_AND_SIZE.md`) are about the repository on GitHub, not the game: the mod's
    zip is committed with every delivery (25 MB each), so the repository grows. The options: put each zip on GitHub's
    Releases page instead (by your hand: this session can't publish releases), keep fewer previews in the repository,
    or clean the old zips from its history. Nothing needs doing until it gets in your way.

## Held: the author's notes, for the go-ahead

The interface (`deco_ui/docs/VERSIONS.md`, "Held", keeps them in full):
- the loading screen's two diamonds alike; the diplomacy tab's portrait, its rays, the cut-off tab buttons (a gilt
  octagon perhaps); the new factory, dockyard and civilian factory icons everywhere the game shows them; the build
  aircraft (the air tab's jet) and infantry (a helmet and a howitzer) buttons; the construction screen (icons clear of
  their headers, subtle octagon buttons, icons redrawn in the Deco palette); the alerts across to the music tray in
  gilt octagons;
- the default army icons (the insignia picker) restyled, and ten new ones, the numbers 1 to 10 on a shield whose
  colour can be changed;
- the training bar (the deployment line: its cut-off text and stray lines);
- the production modifiers' icons not yet the Deco UI's (dockyard output, factory output and one or two more);
- the faction goals (19 above).
