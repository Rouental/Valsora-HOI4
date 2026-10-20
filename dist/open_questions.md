# Open questions (2026-10-20)

The author's answers of 2026-10-19 and 2026-10-20 are in the mod (the go-ahead: "go ahead with the rest of it, and all
the other changes I had been holding back until now"): `docs/HISTORY.md`, 2026-10-20. What is still open:

| # | question | where |
|---|---|---|
| 5 | the old upload's tundra, jungle and desert marks: "I'll add those back in later" | the next map |
| 7 | the strait crossings to add: the map of the red ones (wider than 15 px) is `dist/straits_map_red.png`, numbered as in `dist/straits_proposed.json`; the green and yellow ones are in the game | your marks |
| 10 | flags for Belekria's eight new republics: "I'll get those to you eventually" | |
| 14 | state names (the numbered sheets `dist/state_numbers_*.png`) | |
| 15 | the land regions' names: the drafts are in the mod now ("I'm fine with those for now, I'll edit them later"); change any in `dist/region_names_draft.md`'s last column | |
| 24 | Rouental's Royal Host: it should now start at full strength and keep its experience (its own men added just before it forms); if the game still refills it, say so and it gets its experience back after the refill instead | in game |
| 25 | the tech tree: "I'm not really ready to start with the tech tree in earnest yet" | `docs/TECH_TREE_2036.md` |

New to look at:
- **Rouental's 178 states** from your fief map (the 30 px version): their names are the fiefs' as your map writes them
  (`dist/state_names_rouental.png`); two are both called Vedette. The releasables and the civil war's risers kept the
  land they had; Kové, Temerre, Callentroix and Rolantelle moved to the releasable named after them or naming them.
  Their lines are on Necessary States in the map 10-20 for you to edit; the old province lines there are gone.
- **Rouental's Gazetteer page** still holds the populations of its old states; the mod shares them out over the new
  ones (and will again at the next import). Saving the page's states afresh makes that unnecessary.
- **The Deco UI v0.12**: every held note done (`deco_ui/valsora_deco_ui/README.txt`, Things to check). The alerts' row
  rests on an assumption from one screenshot: 26 a row up to the music tray.
- **Tundra**: paint it white on the areas layer, impassable tundra white with red stripes (solid, not the layer's
  background): the game's snowy plains, provinces of about 600 px.
