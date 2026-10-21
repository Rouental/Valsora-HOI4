# Open questions (2026-10-21, later still)

The author's answers of 2026-10-19 and 2026-10-20 are in the mod (the go-ahead: "go ahead with the rest of it, and all
the other changes I had been holding back until now"): `docs/HISTORY.md`, 2026-10-20. Answered on 2026-10-21 and in the mod since: the governorates' names (29), the generic advisors (27), the Kufi
in gold (30), HMMLA's Royal Fiefs (31) (`docs/NATIONS.md`, 2026-10-21, later); the Royal Host Elite (24: "The troops
are now elite!"), the Army HQ cards (26: "Army HQ cards seem to work"), the governorate line ("worked just fine"), and
Rouental's groups (28: applied, `docs/NATIONS.md`, 2026-10-21, later still). What is still open:

| # | question | where |
|---|---|---|
| 5 | the old upload's tundra, jungle and desert marks: "I'll add those back in later" | the next map |
| 7 | the strait crossings to add: the map of the red ones (wider than 15 px) is `dist/straits_map_red.png`, numbered as in `dist/straits_proposed.json`; the green and yellow ones are in the game | your marks |
| 10 | flags for Belekria's eight new republics: "I'll get those to you eventually" | |
| 14 | state names (the numbered sheets `dist/state_numbers_*.png`) | |
| 15 | the land regions' names: the drafts are in the mod now ("I'm fine with those for now, I'll edit them later"); change any in `dist/region_names_draft.md`'s last column | |
| 25 | the tech tree: "I'm not really ready to start with the tech tree in earnest yet" | `docs/TECH_TREE_2036.md` |
| 32 | the Vale of Reibonne's strategic region: with Hollier, Evriches and Seigne in South Montvallée and Selgrave, Lustiana and Lanzerac in North Montvallée, it holds only Guedelon and the island Brillagne, which don't touch (a region may be in two pieces, but the AI plans by regions). Guedelon into its neighbour's region (Côte d'Ambre's), Brillagne into the sea's nearest land region, or leave it? | |
| 34 | the governorates (`deco_ui/art/proposals/governorates/`): which heading of your fief list is the Vairande's (Vair is listed under Conflans) and the Riverlanders' (Conflans, the largest, is Claude's guess); the Lyrién and the Lustianaise; how loyal the Northmarchers, Southmarchers, Piscans and Recoltaise are (0 in the mockups) | your notes |
| 35 | the three powers' triangle (`deco_ui/art/proposals/three_powers/`, a mockup, not in the mod): do the seven zones suit (a power of 60 or more rules, one under 15 is shut out), and their names and effects (`three_powers_zones.png`)? Where Rouental stands on 1 January 2036 (Prince 40, Voix 30, Speaker 30 is a guess)? Do Leal estates lean to the Prince and Proud ones to the Speaker, as the Pious do to the Voix? Does Reformed Seranism (the Southmarch) answer to the Voix? The Voix's and the Speaker's names, when you have them | your notes |
| 33 | the groups' way back: "Be prepared for the posibility of returning to how it currently is though": the map before them is kept (`work/pre_groups_1021/`, and the commit before) until you say they stay | |

New to look at:
- **Rouental's 13 groups** (map 10-21-3): twelve states joined their neighbours as one province (Élan into Cylône,
  Brochets into Erdoine, Chantelleux into Chattanay, Verrie into Stofflet, Focislar into Vesontio, Gourdelle into
  Vinterre, Gironte into Valenmont, Friere into Quebelle, Frélogne into Spreivald, Prèsloin into Poitevallée, Lugunica
  into Karsten, Pénombre into Petit Crépuscule), and Jourdain et Moterre is one state of two provinces, Jourdain in the
  north, Moterre in the south. Jourdain keeps the 15 victory points your Gazetteer page gives it; the page has its
  Jourdain in Elbée, where it stood since the fief states, so the build moves it (moving it on the page too keeps them
  in step). Focislar's land was Carcarelle's releasable and is the Rivage d'Argent's now, with Vesontio.
- **South and North Montvallée** are two strategic regions for Terres Séparées, as you listed them; their states'
  panels still say "Governorate of Terres Séparées".
- **Rêverie** is a Royal Fief on its state panel.
- **The Royal Host**: the 1e and 2e armoured, nine mechanized divisions, and the 12th, now "12e Ost des Territoires
  Orientaux" (territoire is masculine, hence Orientaux), motorized and in Concorde et Volonté.
- **Kalaistan** is the Kingdom of Kalaistan (still Authoritarian) with **The King in Chains** (the Feudal Army's
  placeholder icon, your text, no effects yet: say if it should do something).
- **The Gazetteer** takes national spirit requests (Requests for the author, "National spirit").
- **The Deco UI v0.12.3**: the commander pickers' Show Field Officers / Show Ship Captains, New Leader and Unassign
  whole; the load and save windows' Back and Load apart; the declare war window with the battle screen's crossed swords.
- **error.log**: the Confederacy's and Scotland's flag lines are gone (the base game's own flags, at a pixel depth its
  loader dislikes, replaced by plain stand-ins). The rest is not the mod's: two Workshop mods' descriptors in your mod
  folder, two of the base game's 3D model lines, and the AI asking for commander traits the game then refuses
  ("unlock_trait_command"), harmless; if that last one grows into the thousands, send the log again.
- **The governorates** are Rouental's strategic regions now (the 26: the fief map's 8 and your 20, Terres Séparées
  one), each named; Brillagne and Concorde et Volonté are in none. The state panel has a line under the victory points
  and manpower: "Governorate of Vair", and for the ten "Royal Fief · Governorate of Couronneterre". The line is a
  scripted GUI on the state panel, the first of its kind here: if it shows nowhere, or in the wrong place (the top left
  of the screen), say so. With the Deco UI only. When you draw the Governorate Lines, `scripts/governorates.py` makes
  the regions again from them.
- **The generic advisors and theorists** are back for every country: the game's own (industrialists, chiefs of
  staff, high command, theorists, the four political ones), its Earth cases taken out.
- **HMMLA** rises in Rêverie and all ten Royal Fiefs in the civil war (Stofflet, Charet and Vendée as before).
- **The Deco UI v0.12.2**: every picture that was traced from the game's art (the broken gilt lines you kept seeing,
  the Army HQ card among them) is drawn by hand now, 26 of them; a check fails the build on broken gilt; the
  diplomacy tab's focus icon fits inside its octagon (`deco_ui/valsora_deco_ui/README.txt`, Things to check).
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
