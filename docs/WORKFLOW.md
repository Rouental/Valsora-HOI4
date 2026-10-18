# How a map update goes, and how to make it faster

The author, 2026-10-17: "tonight please try to figure out ways to make the modding process more efficient both for you,
and for me. Maybe there's something I could do differently with the PDN?" This is the answer: what happens to a `.pdn`
now, what changed on Claude's side, and what the author could do differently (all optional).

## What happens when the author sends a `.pdn`

| step | command | time | before 2026-10-17 |
|---|---|---|---|
| 1. Does it open? | `python3 scripts/pdn_check.py UPLOAD.pdn` | 2 s | not checked |
| 2. What changed, and where | `python3 scripts/pdn_diff.py "source/HOI4 Mod Map.pdn" UPLOAD.pdn` | 15 s | by eye, layer by layer, an hour or more |
| 3. Merge, if the upload is older than ours | keep our game layers, take theirs (as before) | minutes | the same |
| 4. Moved borders | `python3 scripts/pdn_tools.py owners` (the plan), then `owners --apply` | 5 min | a script written for each upload |
| 5. New outlines, state lines | `apply_outlines.py`; `regroup_states.py --recut` | 4 min | regroup, then a script of its own to cut the split provinces again, then `tidy` |
| 6. Province lines, islands, rivers | `pdn_tools.py provinces`, `channel`, `river_provinces.py` | minutes | the same |
| 7. Build and check | `sh scripts/run_all.sh` | 2 min | the same |
| 8. For the author | `state_map.py` for the new states; the `.pdn` (dated: `docs/MAP_VERSIONS.md`), the zip and the pictures sent back | minutes | the same |

`pdn_diff.py` prints every change by layer and place (with a box and a centre pixel), which nations gained or lost land
on Countries, the lines drawn and erased, and **the areas the new country lines enclose that hold two nations** (a
border moved through a nation, or a merge). Its pictures (`work/pdn_diff/`) show each place before and after, with the
labels, so a new label is read once. On the 2026-10-17 upload it found, by itself, the three border moves worked out by
hand that night (Belekria over Sminishia, Belka over Pakitsk and Krionik, Kieska over Krionik).

`pdn_tools.py owners` settles those areas: each goes to one nation (the one an `X,Y=COUNTRY` names, else the one a
stroke on a "Necessary Owners" layer points to, else the one holding most of it), a nation whose states lie wholly
inside handing them over as they are, one whose states the line crosses cut along it. On the 2026-10-17 upload it gave
the same result as that night's hand-made script, with two hints for the moves made by a label alone.

`regroup_states.py --recut` makes the author's drawn areas the states and cuts again, in the same run, the provinces the
new lines cut into pieces: on the 2026-10-17 map exactly that night's result (20,563 land provinces, none under 16 px).

## On Claude's side (built 2026-10-17)

- **The manual is a quarter of its size.** `CLAUDE.md` is read into every session; it was 117 KB (about 30,000 tokens)
  and is 30 KB now: the rules and a line per decision, with the detail moved word for word into `docs/MAP_PIPELINE.md`,
  `docs/DECISIONS.md`, `docs/CONTENT.md` and `deco_ui/docs/VERSIONS.md` (checked: every line of the old file is in one
  of them). Sessions start faster, cost less of the weekly limit, and run longer before their context fills.
- **The steps above** (`pdn_diff.py`, `pdn_tools.py owners`, `regroup_states.py --recut`).
- **Every `.pdn` we write is read back** end to end before it leaves (`writepdn.py` runs `pdn_check.py`).
- **A damaged `.pdn` can be saved**: `pdn_recover.py` pulls every layer still whole out of it as PNGs;
  `import_flags.py` now reads a folder of PNGs as well as a flag file.

## What the author could do differently (each one optional)

Ranked by how much each would save.

1. **Mark who takes land, when it isn't obvious.** When a border moves, the land it encloses now goes, by default, to
   the nation holding most of that area. That was right for all three moves on 2026-10-17, so usually nothing is
   needed. Two cases need a mark:
   - a small nation taking a big piece of a bigger one;
   - a change made by moving a **label** alone (West Sminishia's west end, 2026-10-17: no line moved, so only the
     label said who owns it now).
   For those, draw a stroke, any colour, on a new layer named **Necessary Owners**: from the land that changes hands
   into its new owner's land.
2. **When two nations merge but one stays releasable** (Pakitsk into Belka), don't erase their old border: move it
   from Necessary Borders to Necessary States (select the line, cut, switch layer, paste), so the old states survive.
   Then paint the releasable on Subregions.
3. **Paint each subregion only inside its own nation.** The bump by Sombor was painted in Crvenognjište's colour over
   land the new line gave to Kieska, which left it ambiguous.
4. **Keep a dated copy before a big edit** ("HOI4 Mod Map 2026-10-18.pdn"). If the `.pdn` files live in a folder
   OneDrive syncs, pause syncing while paint.net saves, or keep the working copies outside it. A file synced halfway
   through a save is one way to end up with a damaged one.
5. **Flags as separate PNGs** (one per nation, named after it), if one big flag file starts to feel fragile: one bad
   save can't take all the flags with it, and they import the same way. The flag file works too: keep a copy of it.
6. **Close every province and state line.** A line with an open end divides nothing. And for province size, the guide
   is in `docs/EDITING.md`: usually Cardonia's, about 160 px.
7. **Keep saying what you changed** in your message, as now. `pdn_diff.py` checks the list against the file, so
   nothing is missed either way.

## Not built (ideas for later)

- paint.net palettes of every nation's exact map colour: only worth it if the author paints the Countries layer
  themselves, which the steps above make unnecessary.
- Decoding only the layers a tool needs: each full decode of the map takes about 1.4 GB of disk.
- The Valsora Atlas (`docs/ATLAS.md`, in progress the same night, not in the mod): the build's map in a browser, to
  check a build without starting the game.
