# Open questions (2026-10-21)

The author's answers of 2026-10-19 and 2026-10-20 are in the mod (the go-ahead: "go ahead with the rest of it, and all
the other changes I had been holding back until now"): `docs/HISTORY.md`, 2026-10-20. What is still open:

| # | question | where |
|---|---|---|
| 5 | the old upload's tundra, jungle and desert marks: "I'll add those back in later" | the next map |
| 7 | the strait crossings to add: the map of the red ones (wider than 15 px) is `dist/straits_map_red.png`, numbered as in `dist/straits_proposed.json`; the green and yellow ones are in the game | your marks |
| 10 | flags for Belekria's eight new republics: "I'll get those to you eventually" | |
| 14 | state names (the numbered sheets `dist/state_numbers_*.png`) | |
| 15 | the land regions' names: the drafts are in the mod now ("I'm fine with those for now, I'll edit them later"); change any in `dist/region_names_draft.md`'s last column | |
| 24 | Rouental's Royal Host: it now forms on the game's first day (its own men, then the divisions), so it should start full and at its experience; it is not on the start screen's division count, only once the game runs. If it still starts short, say so | in game |
| 26 | the Army HQ designer: every country now starts with the game's own HQ template; does a new HQ template save now? If not, the button's tooltip or the `error.log` line is the next clue | in game |
| 27 | the game's generic political advisors and theorists (`generic_advisors.txt`) were switched off with the Earth histories, so no Valsoran country has any besides those the Gazetteer gives: bring them back for every country? | |
| 28 | Rouental's provinces to merge or make into states: pick them on the grouping map (https://claude.ai/artifact/RsMPNHMPW1PdhS1Soa6W19, private to you), saved there for Claude to apply | your groups |
| 29 | the governorates: names for the 20 not yet named (numbered on the grouping map); are the rough patches final, or will you draw proper lines on the Governorate Lines layer; and should they only be shown (as strategic regions, a line in the state panel, a map mode) or matter in play (what do the regional parliaments block)? Claude's suggestion: show them first (regions and the state panel line), mechanics later | your answer |
| 30 | Port Almohavid's Gazetteer page no longer has a flag (the export of 2026-10-20, night); the mod still flies the Kufi in gold you chose. Keep it? | |
| 31 | Aurifort (cut out 2026-10-21): your fief map puts the fief wholly in northern Charmas (29 game px), so 11 px of Jourdain et Moterre's southern edge were added ("a tiny bit of southern Jourdain et Moterre"): 40 px, one province. Like Charmas and Jourdain et Moterre it is in no civil war list (HMMLA takes Rêverie, Rouental, Saintiers, Brassard, Stofflet, Charet, Cournin and Vendée): should it, or the other royal fiefs, go to HMMLA? | the map 10-21 |
| 25 | the tech tree: "I'm not really ready to start with the tech tree in earnest yet" | `docs/TECH_TREE_2036.md` |

New to look at:
- **Aurifort** is a state (map 10-21), and Rouërie is now **Brassard**: the ten Royal Fiefs of your list are all on the map (Rouental, Saintiers, Cournin, Jourdain et Moterre, Aurifort, Éislek, Charmas, Rochemont, Bérault, Brassard). Aurifort's population (75,303) came out of Charmas's and Jourdain et Moterre's, by area.
- **The grouping map** shows the governorates (the governorates switch) and warns when a group crosses one.
- **Rouental's 178 states** from your fief map (the 30 px version): their names are the fiefs' as your map writes them
  (`dist/state_names_rouental.png`); two are both called Vedette. The releasables and the civil war's risers kept the
  land they had; Kové, Temerre, Callentroix and Rolantelle moved to the releasable named after them or naming them.
  Their lines are on Necessary States in the map 10-20 for you to edit; the old province lines there are gone.
- **Rouental's Gazetteer page** still holds the populations of its old states; the mod shares them out over the new
  ones (and will again at the next import). Saving the page's states afresh makes that unnecessary.
- **Rouental's rivers** run along its borders now (map 10-20-2): 35 stretches redrawn on your river layers. Karsten's river runs round its east end instead of across it, and Frélogne is 25 px (its corner beyond the river went to Valdélise). In Graisivaudan, La Recolt and Tige the river comes from your Gazetteer page, so the land moved, not the river.
- **The Deco UI v0.12.1**: your notes on v0.12 (`deco_ui/valsora_deco_ui/README.txt`, Things to check).
- **The Deco UI v0.12**: every held note done (`deco_ui/valsora_deco_ui/README.txt`, Things to check). The alerts' row
  rests on an assumption from one screenshot: 26 a row up to the music tray.
- **Tundra**: paint it white on the areas layer, impassable tundra white with red stripes (solid, not the layer's
  background): the game's snowy plains, provinces of about 600 px.
