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
| HOI4 Mod Map 10-17.pdn | d8ce78a4d80d | 2026-10-17, the night | Yastreovakia redrawn; the states of Belekria, Krionik, Terreich, Kurikia, San Sierra, Sennheiser, Gorbastan, Zukchiva, the Sminishias, Pakitsk and Hollier from the author's lines, their split provinces re-cut; Seigne's and Royalist Illiricium's drawn provinces; two islands cut free; five cities. Sent undated that night and on 2026-10-18, dated on 2026-10-18 |

## The flag file (`source/New_Mod_Flags.pdn`)

Named the same way: `New_Mod_Flags 10-15.pdn`, the day it last changed.

| sent as | fingerprint (sha256, first 12) | made | what changed |
|---|---|---|---|
| New_Mod_Flags 10-15.pdn | 9343637ae354 | 2026-10-15 | 101 layers, Vilna's new flag the last added. Sent 2026-10-18. Not in it: the flags that came another way since (Côtefer's, Entroterra's and Mezzogiorno's, fitted 2026-10-15; Zastava's, Crvenognjište's and Mylostrva's, 2026-10-17), and older ones that never were in the file (the Reibonnaise states' from the flag sheet, Belekria's, the civil war's ...): about 25 of the flags in `source/flags/` |
