# The Valsora Gazetteer

A web page where friends fill in the facts of their own nations, once its states are
drawn on the `.pdn`: state names, terrain, rivers, cities, population, railways, supply
hubs, resources and buildings, the nation's names and titles under each government, its
sub-ideologies and ruler, and requests for things the game doesn't have yet. What they
enter is kept in the page's shared atlas until it is pulled into the build.

**Link:** https://claude.ai/artifact/PqTTD5FuFJhpL4JKp8sumN (a claude.ai page, private to you until you share it)

## Sharing it with friends

1. Open the link, then **Share**.
2. Invite each friend **by email, as Editor**. Each needs a claude.ai account and opens the
   page signed in.
3. **Don't turn on the public link.** With a public link, people from outside your
   organization can only view: they see the atlas but can't save to it.

A friend who can only view (or opens the page where it can't reach the atlas) still gets
the whole page: their changes stay in their browser, and **Nation › Save a file** gives them
a file to send you. Load it with **Nation › Load a file** on that nation and it joins the atlas.

A link straight to a nation: the page's link with `#TAG` at the end (`…#ROU` for Rouental).

## What friends fill in

| Tab | Facts | In the game |
|---|---|---|
| State | name, population, kind of state (building slots), infrastructure, civilian and military factories, dockyards, air base, anti-air, naval base, resources, notes | the state's history file; factories and dockyards are cut to the slots, island bases to vanilla's caps |
| map, Terrain tool | each province's terrain (plains, forest, hills, mountains, desert, marsh, jungle, urban) | `definition.csv` and `terrain.bmp` |
| map, Rivers tool | major and minor rivers as lines; erase strokes take away rivers already in the game | drawn into the river layers before `rivers.py` traces them, exactly like yours |
| Cities | cities (one per province), their victory points, the capital | victory points and their names; the capital city's state becomes the capital |
| map, Railways tool | railways (level 1-5) through cities and places | `map/railways.txt`: the shortest way over land between the provinces under the points, as the page draws it |
| map, Supply hubs tool | supply hubs | `map/supply_nodes.txt`: once a nation has its own, only those and its capital |
| Politics | name, full title and adjective under every government and each ideology; ruling sub-ideology; head of state; the other parties' sub-ideologies | localisation, `nations.LEADERS`, `NAMED_LEADERS` |
| Nation | status (in progress / finished), notes for you, requests | the requests board on the start page, for you to answer |

Nations whose leaders are your own characters (Rouental, Merlovich, Brillagne, HMMLA) keep
their sub-ideologies and rulers; their names can still be changed.

## Getting the facts into the mod

Ask Claude to **pull the Gazetteer**. It reads the shared atlas (collections `nations`,
`facts` and `requests`) into a folder and imports it; or you save **Nation › Save every
nation** (shown to you as the owner) and send the file. Then:

```
python3 scripts/gazetteer.py pull <folder>                       # the atlas as Claude saved it
python3 scripts/gazetteer.py import valsora-gazetteer-all.json   # or a file saved from the page
python3 scripts/gazetteer.py status                             # what is there; facts off their nation
sh scripts/run_all.sh
```

Both write `source/gazetteer/<TAG>.json`, one per nation, replacing what was there for it.

After new rivers, run `python3 scripts/river_provinces.py` and rebuild, so provinces follow
them as they follow yours.

**What wins.** For a nation in `source/gazetteer/`, its facts win over the `.pdn` and
`nations.py`: its cities replace the Necessary Cities dots on its land, its state names
replace `source/state_names.json`'s (the old names still work in `nations.py`), its capital
city replaces `nations.CAPITALS`. Anything not filled in keeps the map's value.

## When the map changes

Facts are kept by map pixel (a state or province is the one under its pixel), so they
survive new provinces, states and borders. After a map change, rebuild and run
`python3 scripts/facts_export.py`, and Claude publishes the page again at the same link.
Facts whose pixel lands on another nation are left out (with a note in the build), and the
page's Nation tab counts them.

## How it is made

- `scripts/facts_export.py` (after a build): `work/gazetteer/`: `index.json` (every nation,
  sub-ideologies, the world's owners for the start page's map), `world.png`, and
  `n/<TAG>.json` per nation (its states, provinces, cities and politics as the build has
  them, its flag, and its land with the neighbours' around it, as province numbers per
  pixel, plus the rivers).
- `scripts/gazetteer.html`: the page, published with those files; its shared atlas is the
  artifact's database (`nations/<TAG>`: status, notes, who edited; `facts/<TAG>-<kind>` for
  states, provinces, cities, rivers, rails and politics; `requests/<id>`).
- `scripts/gazetteer.py`: the import, and the functions `read_layers.py` and `build_mod.py`
  call. `check_mod.py` checks railways, building caps and slots, resources and manpower.
