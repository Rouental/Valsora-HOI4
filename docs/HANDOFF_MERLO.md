# Handoff: working on Valsora alongside the author's Claude

This file is for **Merlo's Claude**. Merlo is the author's friend. He drew Valsora's sea
provinces, made Merlovich and the nations south of Solitas, and is an admin of the
Gazetteer.

Read this file first, then follow it. Its aim is that what you make merges into the
author's mod without rework, and looks and reads as if one hand made it.

**What wins when sources disagree:**
1. The repository's `CLAUDE.md` is the full manual and wins over this file.
2. The code wins over both.
3. The author's word wins over everything. Quote them, with the date.

Written 2026-10-15. The author's line moves fast, so check `CLAUDE.md`'s "Current state"
before you trust any number below.

## 1. Work from the repository

- **Where it lives.** https://github.com/Rouental/Valsora-HOI4 is public.
  - Its default branch is `claude/compassionate-allen-slfww9`; there is no `main`.
  - `gh-pages` holds only the Gazetteer's web site. Never work on it.
- **Use Claude Code, not a chat.** Use the web, desktop or terminal version, with a clone
  of the repository.
  - The pipeline is Python, and every map change goes through its scripts.
  - Your earlier sea work ran on scripts that never reached the repository
    (`build_sea.py`, `regroup_sea.py`). The author's Claude had to rebuild them as
    `scripts/sea_provinces.py` to keep your work maintainable.
  - If you write a tool, put it in `scripts/` and add a row for it to `CLAUDE.md`'s table.
- **Read before you start:**
  - `CLAUDE.md`: at least "The editable map", "Rebuilding", "Decisions worth keeping",
    "Current state" and "Working with the author".
  - `docs/NATIONS.md`: how every nation was made and who decided what; `docs/HISTORY.md`:
    the build's history, newest first (both moved out of `CLAUDE.md` on 2026-10-15).
  - `docs/EDITING.md`: the `.pdn`'s layers, as the author uses them.
  - `docs/HOI4_MODDING_PRIMER.md`: what HOI4 requires, learned the hard way.
  - `docs/PROBLEM_LOG.md`: newest first.
- **Set up.**
  - You need Python 3.11 with numpy, scipy, pillow and scikit-image (there is no
    requirements file).
  - From the repository root, run `sh scripts/run_all.sh`. It takes about two minutes, one
    when the map hasn't changed (it skips `read_layers.py` while nothing that step reads has
    changed: `scripts/stamp.py`; `FORCE=1 sh scripts/run_all.sh` reruns it), and longer the
    first time, when it decodes the `.pdn`. The same sources give the same files, the zip
    included, so a rebuild that changed nothing shows nothing to commit.
  - Its `check_mod.py` step must end with `all checks passed`. A clean `check_mod.py` is
    the bar for shipping anything.
- **Run everything from the repository root.** Paths are relative to it (`work/`,
  `source/`, `build/`).

## 2. The map file, and how to merge without pain

- **`source/HOI4 Mod Map.pdn` is the map.** It is a paint.net file at game size, 5120 ×
  2560. Each layer is one kind of game data, found by its name.
  - Every map change happens in it, through the repository's scripts.
  - Never edit the generated files in `build/`, `work/` or `dist/`.
- **Start from the latest `.pdn` in the repository.** Tell the author which layers you
  changed.
  - When an upload is based on an older file, the merge rule is: keep the current game
    layers (Provinces, States, Countries, Strategic Regions, Terrain…) and take only the
    sender's own layers (outlines, rivers, names, references).
  - So say exactly which layers you touched. If you ran a script that rewrote game
    layers, say which script and its arguments, so it can be run again on the current
    file.
- **Agree a region with the author before editing game layers there.** Two people
  re-cutting the same states can't be merged.
- **Keep places by pixel, not by id.** Province, state and region ids are reading order,
  and they shift whenever the map changes.
  - Names, capitals and Gazetteer facts are all kept by an `"x,y"` pixel inside the
    thing.
  - In tables, refer to a capital as `"capital:TAG"`, never by province id.
- **Never regenerate the `.pdn`.** `make_game_pdn.py` would replace the author's file
  with a placeholder one.
- **Don't undo the sea work.**
  - `strategic_regions.py` and `pdn_tools.py sea_zones` would undo the sea regions you
    drew; both refuse to run on a map with Ocean Province Lines.
  - The sea comes from `python3 scripts/sea_provinces.py build|seam|names|check`.
- **Keep under HOI4's border limit.** The limit is 65,536 province borders; the map has
  about 62,200 (2026-10-15; `docs/BORDER_LIMIT.md`). `check_mod.py` counts them.
  - If new outlines push the count near the limit, run `python3 scripts/merge_provinces.py`.
  - New outlines are cut into provinces of about 190 px.

## 3. Recipes

COUNTRY is a key of `common.COUNTRIES` (snake_case), not a tag. X,Y is a map pixel.

### A nation the author outlined

1. **Add it to `scripts/common.py` `COUNTRIES`.** The format is
   `"key": (TAG, name, adjective, (R, G, B))`. Example:
   `"santa_fe": ("SFE", "Santa Fe", "Santa Fean", (230, 175, 35)),`
   - The colour is the exact paint on the Countries layer; ownership is matched by exact
     colour. Pick one far from its neighbours, and from its flag where there is one.
   - **Tag:** three capitals, not in `COUNTRIES` and not in
     `source/vanilla/index/tags.txt` (the base game's). `SOL` and `SOM` are vanilla
     tags, which is why Solitas is `SLT`.
2. **Seed it in `scripts/apply_outlines.py`.** Put one pixel inside each enclosed patch
   in `OWNERS`: `"santa_fe": [(2323, 1884)],`. Patches the lines close off by accident
   go in `LEAVE`.
   - Then run `python3 scripts/apply_outlines.py <the .pdn>`.
   - If the author drew state lines, then run `python3 scripts/regroup_states.py`.
     Each drawn area becomes one state; the author's state lines are never split.
3. **Fill in `scripts/nations.py`:**
   - `FORMAL_NAMES["SFE"] = "the Fifth Republic of Santa Fe"`.
   - `LEADERS["SFE"] = ["stalinism"]`. This is the ruling sub-ideology, and it is
     **required**: `check_mod` fails without a leader.
   - Optional: `CAPITALS` (a pixel inside the capital state), `NAMED_LEADERS`
     (`"TAG_leader_<subtype>": (name, sprite or None)`), and `HISTORY` (puppets via
     `set_autonomy`, pacts, factions).
   - Optional: `POPULARITIES`. Faction members need 30 % for the leader's ideology, so
     they get 40.
4. **Set its culture.** Add `scripts/cultures.py` `TAG_CULTURE["SFE"] = dict(names=…,
   portraits=…, gfx=…)`. Otherwise it gets its continent's default.
   - Name lists come from `source/names/vanilla_names.txt`. Copy any new block from
     vanilla's `00_names.txt`. Our own lists are in `custom_names.txt`.
5. **Rebuild:** `sh scripts/run_all.sh`. If rivers cross the new land, run
   `python3 scripts/river_provinces.py` and rebuild.
6. **Write it down** in a dated paragraph at the end of `docs/NATIONS.md`, and the day's
   work at the top of `docs/HISTORY.md`.

### Moving land between countries

All of these are `scripts/pdn_tools.py` commands, and they edit the `.pdn` in place:

| What | Command | Example used |
|---|---|---|
| Whole states | `give COUNTRY X,Y …` | `give holy_see 896,1184` |
| An islet or sliver, joining the new owner's nearest state | `attach COUNTRY X,Y …` | `attach terreich 935,1862` |
| What a moved line cuts off, for countries without state lines | `cede FROM TO X,Y` | `cede sminishia w_sminishia 1919,414` |
| What a moved border line encloses | `border COUNTRY X,Y` | `border san_sierra 700,1290` |
| Painted islands become land | `add_land COUNTRY` | the "Islands to Add" layer |
| A colour on a layer | `recolour LAYER R,G,B=R,G,B` | — |
| A country's sliver states, joined to a neighbour | `merge_small COUNTRY MIN_PX` | — |
| Reopen a strait | `channel X1,Y1,X2,Y2` | — |
| Lake to sea | `navigable X,Y` | — |
| Placeholder land cut like an outlined patch (~1,300 px states, ~190 px provinces) | `recut [--keep-states] X,Y …` | `recut 1950,1811` (Arvorenia) |
| Each lake one province | `lakes` | — |

### Names

- **State names** go in `source/state_names.json` as `{"x,y": "Name"}`, with any pixel
  inside the state.
  - The build stops if a pixel is in no state, or if two names land in one state.
  - `python3 scripts/state_map.py <name> TAG …` draws a numbered map for the author to
    name states from.
- **City names.** A city is a dot of any colour but black on the "Necessary Cities"
  layer. Its name goes in `source/city_names.json` as `{"x,y": "Name"}`; a dot moved up
  to 12 px keeps its name.
  - The first city of a state is its victory point.
  - Capitals are named with `nations.CITY_NAMES` `"capital:TAG"`.

### Sub-ideologies

Add sub-ideologies only when the author asks. They go in `scripts/ideologies.py`
`SUBTYPES[ideology]` as `(key, "Name", "description")`. Write the description without
the name; the build puts "Name: " in front.

### Flags and portraits

- **Flags** are `source/flags/TAG.png`. `TAG_<ideology>.png` is used while that ideology
  rules; the internal keys are democratic, fascism (Authoritarian), communism,
  neutrality (Monarchist) and theocracy.
  - The author's flag file is `source/New_Mod_Flags.pdn`. Import it with
    `python3 scripts/import_flags.py <file.pdn>`.
  - Fit other shapes to HOI4's 82:52 **without stretching**: scale evenly, then add plain
    field inside the stripes or trim plain sides.
  - Add a fitted flag to the flag file as a layer, so the next import doesn't put the old
    one back.
  - Keep map colours when a flag arrives, unless the author asks.
- **Portraits:** put the picture in `source/portraits/` and register it in
  `nations.PORTRAITS` as `(file, left, top, width, None)`, cropped to 156:210. Use it in
  `NAMED_LEADERS`.

### Releasables

- **The author's own** are in `nations.RELEASABLE`, as `"TAG": [state names]`. The first
  state is the capital. Each also needs `COUNTRIES`, `FORMAL_NAMES`, `LEADERS`, a culture
  and a flag.
- **The Gazetteer's** come in through its import (§6) and need nothing by hand.

## 4. Make it look like one hand made it

- **Record who decided what.** The author's names, governments and formal names are
  theirs. Everything you choose (tag, colour, adjective, culture) is "Claude's".
  - Write each choice in that day's paragraph in `docs/NATIONS.md` (the day's work in
    `docs/HISTORY.md`, rules in `CLAUDE.md`), and in a code comment:
    `# author, 2026-10-13` or `# Claude's guess`.
  - Tell the author what you guessed.
- **Change only what was asked.** Don't regroup, recolour or improve what wasn't
  mentioned. That caused rejected work before (regrouped land regions, CITY_STATES).
- **Keep the year at 2036.** Never write an 18xx or 19xx date; `check_mod` fails on one.
- **Every ruler is a set character.** Every country owning land, or released later, needs
  a `LEADERS` entry.
- **Keep sea and land colours apart.** Sea regions are blues (hue 0.53–0.70). Land
  regions are never blue, cyan or indigo.
- **Never commit Paradox's files.** Vanilla files may be read from the author's private
  `Rouental/HOI4-Files`, but must never be copied wholesale into this public repository.
  Only single files the mod overrides, and lists of names, belong here.
  - `deco_ui/reference/` is git-ignored, and stays so.
- **Never commit secrets.** That means Gazetteer passwords (they stay in `work/`) and the
  author's email address (the rules file keeps `OWNER_EMAIL`).
- **Keep `docs/PROBLEM_LOG.md`.** Log every problem as a bold title with the date, then
  Cause / Fix / Check, newest first.
- **Write docs the way they're written now:** plain words, short dated entries, the
  author quoted.
- **After every build, tell the author what changed and how to install it:**
  1. Delete `mod/valsora_test/` and `mod/valsora_test.mod`.
  2. Unzip `dist/valsora_test.zip` into `mod/`.
  3. Launch with `-debug`.

## 5. Handing your work back

Hand it back either way below, and include the notes after the list:
- **A pull request** from a fork, based on the latest default branch, if you have
  GitHub. Commit small, described steps. Don't push to the author's branch unless they
  gave you access and asked you to.
- **Files**, without GitHub: the edited `.pdn`, any changed or new files under
  `scripts/` and `source/`, and a short note.

What the note covers:
- Which `.pdn` layers you changed. Give the scripts you ran, with their arguments, in
  order.
- What you decided and who decided it, as you'd write it in `docs/NATIONS.md` or `CLAUDE.md`.
- New problem-log entries.
- `check_mod.py`'s result, and any previews you made in `dist/` (before / after images
  help the author check map work quickly).

Ask before taking in someone else's work (another mod's files, a third party's art). The
author decides.

## 6. The Gazetteer: you're an admin

The Gazetteer is a web site where players fill in their own nations, each behind a
password: https://rouental.github.io/Valsora-HOI4/

- **Signing in.** Open it, scroll to the bottom and sign in with Google, using the
  address the author added.
- **Owner tools** at the top give you:
  - passwords: make one, change one, copy it to send to a player;
  - nations not on the map yet;
  - **map tools**, open or closed per nation;
  - requests, suggestions, and **Save every nation as a file**.
  Only the author can add or remove admins.
- **A nation's map tools** (states, cities, terrain, rivers, railways, supply hubs) open
  only once its states are the author's own lines.
  - Before that, its player suggests states and cities with the Suggest tool, and fills
    in names, flags, people and releasables. A drawn state (Suggest › State) keeps only the
    nation's own land inside the line, and none of a state drawn before it.
  - When you or the author draw a nation's states, its tools open at the next site
    update. "Map tools" in Owner tools can open or close any nation by hand.
- **Use the suggestions when you draw.** Owner tools › Suggestions › "Show them on the
  world map". Or, in the repository, run `python3 scripts/gazetteer.py suggestions`,
  which writes `dist/gazetteer_suggestions.png`: a transparent 5120 × 2560 layer to
  import into the `.pdn`.
- **Releasables.** Players can define releasables: their land (whole states, since HOI4
  cores states, or drawn areas while the nation's states aren't drawn), names, government,
  flag and ruler. Once imported, the build makes each a country owning nothing, with cores
  on its states (and on those its areas cover by half). So when you draw a nation's states,
  follow its releasables' borders where you can.
- **Facts come in through the file.** Facts reach the mod through "Save every nation as a
  file" and `python3 scripts/gazetteer.py import <file>` (`docs/GAZETTEER.md`).
  - After map changes, the site is republished from the repository by the author's
    Claude (`facts_export.py`, `gazetteer_site.py`, a commit on `gh-pages`).
  - Don't push to `gh-pages` yourself.
