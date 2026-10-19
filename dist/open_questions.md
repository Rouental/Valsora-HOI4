# Open questions (2026-10-19)

Everything still waiting on an answer, newest first within each group. Answer any number, in any order; "your call"
is a fine answer for anything that isn't a name. Each item says where to look.

## The map

1. **Rouental's border edits** (the city state in the east, the cutouts for Vair, Carcarelle and Grande Reliette)
   weren't in the 10-18-3 file I got, so they probably didn't save, like Almohavid's. Please send them again with the
   next map. Are the cutouts new nations, or land for the existing releasables (Carcarelle's, Vair's, Reliette's)? And
   the city state: its name, and whose is it at the start?
2. **The Cultists' city in the jungle:** you said you might redraw it with one path in from the west. The editing guide
   now says how (`docs/EDITING.md`, under the areas layer).
3. **Tundra** (white on the areas layer): what should it be in game: ordinary tundra terrain with larger provinces, as
   I did for Belekria 1, 4, 5, 6 and 15, or something else?
4. **The desert province size** I chose: about 600 px (`scripts/areas.py`). Keep it, or larger or smaller?
5. **The jungle and tundra marks of an earlier upload** (on the layer then called "Desert") aren't in the latest file.
   Were they dropped on purpose, or should they come back?
6. **The bump of Kieska's new land by Sombor** is painted as Crvenognjište; for now it is Kieska's with a Crvenognjište
   core. Is that right?
7. **The wider strait crossings** (`dist/straits_map.png`): the orange and red ones, 10-20 px of water. Which, if any,
   should be crossings? The 414 green and yellow ones are already in.

## Nations

8. **My guesses for the eleven new nations** (`docs/NATIONS.md`, 2026-10-19): tags, map colours, adjectives,
   governments and formal names.
   - Krionik's realms: Belska, Koroletz, Targoviste, Kosavichy, Lagrád. Absolute Monarchy, "the Principality of …".
   - Sangrád and the ports Port Nyasha, Port Vostok, Port Grazda. Oligarchy, "the Free City of …".
   - The Sisterhood (Sennheiser's): a Holy Order.
   - Xugang: "the Territory of Xugang", Social Democracy, Terreich's puppet.
9. **Sangrád and the three ports:** did you mean them as releasable nations? If not, I'll take them out.
10. **Flags for Belekria's eight new republics** (they fly a stripe in their map colour until then).
11. **The motto flag** ("a safe haven amid the storm", Arabic on indigo, four hands in white and gold,
    `dist/flag_proposals/safe_haven/`): whose flag is it, and which version?
12. **The Association of Reibonnaise States' emblem:** A (gold lozenges) or B (red and white), or changes
    (`dist/emblem_proposals/reibonnaise_association/`).
13. **Rouental's admiral James Navy:** his page notes "Skilled admiral / Submarine leader". Add base-game traits for
    those?

## Names

14. **State names** (each sheet numbers the states; give names by those numbers):
    - the Cultists' 23 (`dist/state_numbers_cultists.png`; the numbers on it aren't the in-game "Cultists N", so use the
      sheet's);
    - New Formosa's 11 (Krionik's player can also name them on the Gazetteer);
    - Usnistan's 60 new ones (`dist/state_numbers_usnistan_deserts.png`);
    - Rouental's and Terreich's new ones (`dist/state_numbers_rouental.png`, `dist/state_numbers_terreich.png`);
    - from the 10-17 map: Belekria, Krionik, Kurikia, San Sierra, Sennheiser, Gorbastan and Zukchiva
      (`dist/state_numbers_<name>.png`), Cardonia's 5 and Hollier's 1.
15. **The 137 land strategic regions** (`dist/region_names.md`); a first draft of every name is
    `dist/region_names_draft.md`: approve it, change some, or replace it.
16. **The Gazetteer's suggestions I read for you to confirm:** Riverraine's capital Callentroix and Kové's Kové; the two
    Triftsund-Inseln states sharing their name; Ungar's two city-states of 31 and 63 px (Tópart, Erődítmény).

## The Gazetteer

17. **The nine desert nations' map tools:** their states are drawn now. Open their map tools on the Gazetteer?
18. **A read-only service account** so I can read the site directly instead of waiting for your saved file (its key as
    the environment's secret `GAZETTEER_SERVICE_ACCOUNT`; the steps are in `docs/GAZETTEER_INTERNALS.md`). Optional.

## The interface (Deco UI)

(Your notes on v0.11.2 of 2026-10-19, evening, are written down in `deco_ui/docs/VERSIONS.md` under "Held" and wait for
your go-ahead.)

19. **The faction screen:** what looks odd? In your screenshot I see the Long Term column tinted blue, grey carved
    leaves in the bottom corners, and the "Faction Influence" label sitting on the frame line.
20. **Fuel, supply and convoys in the top bar's strip:** keep the experiment, or back to a tray?
21. **v0.9's restyled screens** (the research trees, the doctrines, the designers): keep them?
22. **What to restyle next** (`deco_ui/docs/SCREEN_INVENTORY.md`'s suggestions: the unit counters, the division and
    ship details, the trait trees …), and the mockups of the next screens (`deco_ui/art/proposals/next_screens/`).
23. **The larger flags' test version** (`docs/HD_FLAGS_TEST.md`): did it look right, and do you want it in the mod?

## The game

24. **Rouental's elite divisions** start with new men filling their ranks; how should they stay full (the options in
    my reply of 2026-10-18, night)?
25. **The tech tree** (`docs/TECH_TREE_2036.md`): nothing is built until you've said more about its shape.
26. **The other speed and size options** (`docs/SPEED_AND_SIZE.md`).
