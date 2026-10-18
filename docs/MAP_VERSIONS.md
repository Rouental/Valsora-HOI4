# The map's and the flag file's versions, as sent to the author

The author, 2026-10-18: "In the future, start dating the map as you send it. If the map changes multiple times in a
day, do something like 10/17-2, 10/17-3, etc. I'm going to start keeping a backup."

So every copy of `source/HOI4 Mod Map.pdn` sent to the author is named for the day the map last changed, month and
day: `HOI4 Mod Map 10-17.pdn` (a file name can't hold a `/`), and the second version made that day
`HOI4 Mod Map 10-17-2.pdn`, then `-3` and so on. The file in the repository keeps its plain name; the dated copy is
made only to send (in the scratchpad, never committed). A map sent again unchanged keeps its old name (check its
fingerprint below). Run `python3 scripts/pdn_check.py` on the copy before sending, and add a row here, newest first.

| sent as | fingerprint (sha256, first 12) | made | what changed |
|---|---|---|---|
| HOI4 Mod Map 10-18-2.pdn | d545d7405686 | 2026-10-18, night | The author's upload of that evening ("HOI4_Mod_Map_10-18_1": the layer "Impassible / Desert / Jungle / Tundra" with Usnistan's deserts, its state lines, Rouental's and Terreich's new lines, new rivers): Usnistan's nine desert nations' states from their lines (60), 22 of them impassable; the marked states cut coarse (486 provinces to 119); Rouental's and Terreich's new states and provinces; provinces cut along the new rivers; Myehn's stuck islands cut apart (9 channels) |
| HOI4 Mod Map 10-18.pdn | 83a5f6772010 | 2026-10-18, later | The Gazetteer's suggestions (their new state lines drawn on Necessary States) (Rouental's Leclerc and Kove split; North Pollana's islet and second province; Terreich's merged states and isles in pairs, Rosenburg, Terreichstadt; Ungar's six drawn states); more provinces map-wide (21,148 land, up from 20,552), Belekria 1, 4, 5, 6 and 15 coarse as tundra; Belekria 64 West Sminishia's; Ungar's, Terreich's and Rouental's new state names in `state_names.json`; Vilna 2 cut into two islands |
| HOI4 Mod Map 10-17.pdn | d8ce78a4d80d | 2026-10-17, the night | Yastreovakia redrawn; the states of Belekria, Krionik, Terreich, Kurikia, San Sierra, Sennheiser, Gorbastan, Zukchiva, the Sminishias, Pakitsk and Hollier from the author's lines, their split provinces re-cut; Seigne's and Royalist Illiricium's drawn provinces; two islands cut free; five cities. Sent undated that night and on 2026-10-18, dated on 2026-10-18 |

## The flag file (`source/New_Mod_Flags.pdn`)

Named the same way: `New_Mod_Flags 10-18-3.pdn`, the day it last changed and the version that day. The author's own copy, sent 2026-10-18 (90
layers, fingerprint 9f6d720d5d56), is the file we were first given: the copies we had sent never opened for them.

| sent as | fingerprint (sha256, first 12) | made | what changed |
|---|---|---|---|
| New_Mod_Flags 10-18-3.pdn | 742d3b5a979b | 2026-10-18, later still | 132 layers: the six flags that came by the Gazetteer added on top, hidden: Formosa (Krionik's releasable, the dragon alone), Port Almohavid, and Ungar's Communist, Democratic, Authoritarian and Theocratic flags (`import_flags.py` reads them back by those names). Read back, every flag unchanged |
| New_Mod_Flags 10-18-2.pdn | 50cf7797bcf3 | 2026-10-18, later | 126 layers: the 25 flags of `source/flags/` the file lacked added on top, hidden (the author: "Please add the flags to the file"): Merlovich, Arvorenia, Atrocha, Hoalepa, Ponchomagnifico, Silvamar and the United States of Solitas (Merlo's, only ever 82 x 52: enlarged pixel for pixel), Brillagne, Crvenognjište, Côtefer, Entroterra, The Faithful, Guedelon, Republican and Royalist Illiricium, Kurikia, Mylostrva, Mezzogiorno, Vultuca, HMMLA, Rouental (Reibonne), Holy See, Seigne, Selgrave, Zastava (stretched to the file's 490 x 311 as the build stretches them). Read back by `import_flags.py`, every flag comes out unchanged. Every flag of the mod is in it now |
| New_Mod_Flags 10-18.pdn | 7c72127ebd68 | 2026-10-18 | The first copy of ours paint.net opens: the 101 layers of 10-15 (the same pixels, names and visibility) written again on the author's own 90-layer copy with the fixed writer (`docs/PROBLEM_LOG.md`, "The flag file is corrupted"). Every copy we sent from 2026-10-13 to 10-15 was refused by paint.net. Not in it, as in 10-15: about 25 of the flags in `source/flags/` |
| New_Mod_Flags 10-15.pdn | 9343637ae354 | 2026-10-15 | 101 layers, Vilna's new flag the last added. Sent 2026-10-18; paint.net refused it (our writer's id clash). Not in it: the flags that came another way since (Côtefer's, Entroterra's and Mezzogiorno's, fitted 2026-10-15; Zastava's, Crvenognjište's and Mylostrva's, 2026-10-17), and older ones that never were in the file (the Reibonnaise states' from the flag sheet, Belekria's, the civil war's ...): about 25 of the flags in `source/flags/` |
