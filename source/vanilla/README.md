# Vanilla's parts in the mod

What the mod takes from vanilla Hearts of Iron IV 1.19.3, kept here so the build and its checks
need no copy of the game. Refresh after a game update with
`python3 scripts/vanilla_sync.py [HOI4 folder]` (default: `$HOI4_DIR`, then the author's
`Rouental/HOI4-Files` cloned to `/home/user/hoi4-files`).

This is Paradox's content. Only two kinds of it belong here: the single files the mod ships in
place of vanilla's, and lists of vanilla's names. Never copy the game's folders wholesale.

## `files/`: vanilla files the mod ships changed

Exact copies, made by `vanilla_sync.py`. `scripts/vanilla_parts.py` changes them at build time:
every date moves a hundred years to Valsora's 2036 (`1936.1.1` → `2036.1.1`, `start_year`, the
tech tree's year labels), and `common/ai_strategy/default.txt` loses its Earth-only blocks
(Japan's, the USA's and Britain's naval focus, Earth's area priorities).

- `common/technologies/*.txt` and `interface/countrytechtreeview.gui`: the research years.
- `common/scripted_triggers/diplomacy_scripted_triggers.txt`: the game rule "war goals from
  focuses only, until 1938 / 1939 / 1940", now until 2038 / 2039 / 2040.
- The generic content with date conditions: laws (`_economic`, `_manpower`), the generic focus
  tree, AI division templates, faction goals, special projects, raids, medals, ribbons,
  compliance modifiers.
- The generic AI strategies (`common/ai_strategy`: default, doctrines, operations, operatives).
  The mod switches vanilla's `common/ai_strategy` off, since most of it is about Earth's
  countries; these four come back as files of the mod.
- The generic events: elections, aces, war justification, nuclear attacks, capitulation,
  operatives (LaR), army leaders (MTG), factions, demands and civil wars (`Generic.txt`),
  collaboration governments and resistance (`LAR_occupation.txt`), operations
  (`LaR_espionage_operations.txt`), the nuclear project (`Special_Project_Events.txt`). The mod
  switches vanilla's `events` off, and these had been missing since the first build.

- `common/autonomous_states/puppet.txt`: the puppet, without its clause refusing a fascist overlord with Death or
  Dishonor (`vanilla_parts.EDITS`): Valsora's Authoritarian overlords keep plain puppets (2026-10-17).

## `curated/`: vanilla's, cut by hand

`localisation/english/replace/valsora_name_caps_l_english.yml` (made by `vanilla_sync.py`, not by hand): the
game's 170 English lines that open a sentence or paragraph with a country's definite name, `GetNameDefCap` there.
Valsora's definite names start with "the" ("the Cardonian Kingdom has announced its total surrender", 2026-10-17).

`common/on_actions/valsora_generic_on_actions.txt`: the generic hooks of vanilla's on_actions
(elections, aces, army leaders, operatives, nuclear news, capitulations, civil wars), without
their Earth-specific parts. Dates are moved like `files/`.

## `index/`: vanilla's names

Lists made by `vanilla_sync.py`, one name per line (`traits.json` and `companies.json` are JSON):

| file | holds | used by |
|---|---|---|
| `tags.txt` | Earth's 364 country tags and file names | Earth's history stand-ins; our tags must differ |
| `autonomy_states.txt` | the autonomy levels (puppet, dominion ...) | `check_mod.py` (every level a history sets) |
| `decisions.txt` | the 732 vanilla decisions that loaded files name, and their kind | the decision stand-ins |
| `sprites.txt` | every sprite vanilla declares | `check_mod.py` |
| `technologies.txt`, `equipment.txt`, `modules.txt`, `subunits.txt`, `ideas.txt`, `defines.txt` | vanilla's names of each | `check_mod.py` |
| `map_files.txt` | the files of vanilla's `map` folder | `check_mod.py` (map files the mod inherits) |
| `year_names.yml` | generic names with a year ("1936 Cruiser Hull") | renamed for 2036 |
| `traits.json` | the traits the game's own characters have, by kind (ruler, general, admiral) and advisor post, with their names, groups and ledgers, Earth's one-country ones left out; and every trait the game defines (`defined`) | the Gazetteer's trait lists (`facts_export.py`), the import, `check_mod.py` |
| `companies.json` | the generic arms organisations the Gazetteer offers (`arms`: id, name, group, icon and the generic designer each is without Arms Against Tyranny), those designers (`designers`: category, picture, research bonus, trait, costs), the industrial concern kinds (`concerns`: trait, name, picture, research bonus, cost, as most of the game's own concerns of that trait have them), research category names (`research`) and every generic organisation (`templates`) | the Gazetteer's company kinds (`facts_export.py`), the import and build (`gazetteer.companies`), `check_mod.py` |
