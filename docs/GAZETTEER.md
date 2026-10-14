# The Valsora Gazetteer

A web page where friends fill in the facts of their own nations: once its states are drawn
on the `.pdn`, state names, terrain, rivers, cities, population, railways, supply hubs,
resources and buildings; at any time, its names and titles under each government, its
sub-ideologies, its flags, its ruler and party leaders (names, titles, portraits), its
generals and admirals, its colour, culture, motto and anthem, suggestions for the map, and
requests for things the game doesn't have yet. Each nation is locked behind a password you
give its player, so nobody can change anyone else's nation.

**Link:** https://claude.ai/artifact/PqTTD5FuFJhpL4JKp8sumN (a claude.ai page, private to you until you share it)

## Sharing it with friends

1. Open the link, then **Share**.
2. Invite each friend **by email, as Editor**. Each needs a claude.ai account and opens the
   page signed in.
3. **Don't turn on the public link.** With a public link, people from outside your
   organization can only view: they see the atlas but can't save to it.
4. On the page, under **Owner tools › Passwords** (only you see them), press **Make one** for
   each friend's nation and send them its password (**Copy**). They open their nation, type the
   password once, and the page remembers it on that device.

A password opens one nation and no other. **New password** locks the old one out and keeps
everything that was entered. You never need passwords yourself: the page unlocks every nation
for you.

A friend who can only view (or opens the page where it can't reach the atlas) still gets
the whole page: their changes stay in their browser, and **Nation › Save a file** gives them
a file to send you. Load it with **Nation › Load a file** on that nation and it joins the atlas.

A link straight to a nation: the page's link with `#TAG` at the end (`…#ROU` for Rouental).

## What friends fill in

| Where | Facts | In the game |
|---|---|---|
| State tab | name, population, kind of state (building slots), infrastructure, civilian and military factories, dockyards, air base, anti-air, naval base, resources, notes | the state's history file; factories and dockyards are cut to the slots, island bases to vanilla's caps |
| map, Terrain tool | each province's terrain (plains, forest, hills, mountains, desert, marsh, jungle, urban) | `definition.csv` and `terrain.bmp` |
| map, Rivers tool | major and minor rivers as lines; erase strokes take away rivers already in the game | drawn into the river layers before `rivers.py` traces them, exactly like yours |
| Cities tab and tool | cities (one per province), their victory points, the capital | victory points and their names; the capital city's state becomes the capital |
| map, Railways tool | railways (level 1-5) through cities and places | `map/railways.txt`: the shortest way over land between the provinces under the points, as the page draws it |
| map, Hubs tool | supply hubs | `map/supply_nodes.txt`: once a nation has its own, only those and its capital |
| map, Suggest tool | areas, lines and points drawn anywhere on the world (a border, an island that should be theirs, a mountain range, where an undrawn nation goes), each with what it is | nothing by itself: a layer for you (below) |
| Politics tab | name, full title and adjective under every government and each ideology; ruling sub-ideology | localisation, `nations.LEADERS` |
| People tab | head of state (name, titles, portrait); each other party's sub-ideology, leader and portrait; generals, admirals, advisors (name, notes, portrait) | the rulers and party leaders, with their titles shown on the portrait; the characters are a list for you |
| Nation tab | status (in progress / finished), flags (one, and one per government if they like), map colour, culture, motto, anthem, description, notes for you, requests | flags into `source/flags/`; the map colour; the rest is for you |

**Overseas land** (Rouental's Concorde et Volonté, Krionik's colonies ...) has a box of its own
in the map's lower right corner, beside the mainland's and the whole world's: a click opens it
with every tool.

**Nations not on the map yet.** Under **Owner tools › Nations not on the map yet**, add a
nation with the tag it will have (base-game tags are refused). Make it a password like any
other: its player can fill in its names, titles, sub-ideologies, flags and people, and draw on
the world map where it should be, until you or Merlo draw it. When it is on the map, its
facts carry over.

Nations whose leaders are your own characters (Rouental, Merlovich, Brillagne, HMMLA) keep
their sub-ideologies and rulers; their names can still be changed.

## Your tools on the start page

**Owner tools** (only you see them): the passwords; nations not on the map yet; every
**request** (set it done or declined, and reply; the player sees the reply with their
nation); every **suggestion** (shown on the world map, or opened where it was drawn); and
**Save every nation as a file**, the whole atlas in one file to send Claude.

## Getting the facts into the mod

Ask Claude to **pull the Gazetteer**, or send the file from **Save every nation as a file**.
Claude reads the atlas with your passwords, downloads the pictures and runs:

```
python3 scripts/gazetteer.py paths <keys file>          # each nation's folder in the atlas
python3 scripts/gazetteer.py pull <folder>              # the atlas as Claude saved it
python3 scripts/gazetteer.py import valsora-gazetteer-all.json   # or a file saved from the page
python3 scripts/gazetteer.py status                     # what is there, and what is left to do by hand
python3 scripts/gazetteer.py suggestions                # the suggestions as a layer for the .pdn
sh scripts/run_all.sh
```

They write `source/gazetteer/<TAG>.json`, one per nation, replacing what was there for it,
and keep the pictures in `source/gazetteer/assets/`.

- **Flags** already in HOI4's 82:52 shape become `source/flags/<TAG>.png` (or
  `<TAG>_<ideology>.png` for one government), once per picture: a flag you change later stays
  yours. Others are fitted by hand, like yours, without stretching. Add them to your flag file
  too, or your next flag file would put your old ones back.
- **Portraits** are cropped to HOI4's 156 × 210 from the top of the picture.
- **Suggestions**: `dist/gazetteer_suggestions.png` is a transparent 5120 × 2560 picture of
  every suggestion with its label; import it into the `.pdn` as a layer (it lines up exactly)
  and draw from it. `dist/gazetteer_suggestions_preview.png` shows them over the map.
- **By hand**: requests, generals and admirals, cultures and flags of other shapes; `status`
  lists them.

After new rivers, run `python3 scripts/river_provinces.py` and rebuild, so provinces follow
them as they follow yours.

**What wins.** For a nation in `source/gazetteer/`, its facts win over the `.pdn` and
`nations.py`: its cities replace the Necessary Cities dots on its land, its state names
replace `source/state_names.json`'s (the old names still work in `nations.py`), its capital
city replaces `nations.CAPITALS`, its colour the `.pdn`'s paint in game. Anything not filled
in keeps the map's value.

## When the map changes

Facts are kept by map pixel (a state or province is the one under its pixel), so they
survive new provinces, states and borders. After a map change, rebuild and run
`python3 scripts/facts_export.py`, and Claude publishes the page again at the same link.
Facts whose pixel lands on another nation are left out (with a note in the build), and the
page's Nation tab counts them.

## How safe it is

A nation's facts are stored at an address made from its password, which the atlas can't
list: without the password they can be neither found nor changed, by friends or by anyone
looking at the page's data directly (tested on the live atlas). Only you can add nations
that aren't on the map. Your passwords are kept in your own private corner of the atlas,
which nobody else can read. One limit: an Editor can also publish a new version of the page
itself. Only invite people you trust that far; Claude can publish it again from the repository.

## How it is made

- `scripts/facts_export.py` (after a build): `work/gazetteer/`: `index.json` (every nation,
  sub-ideologies, the world's owners for the start page's map, the base game's tags),
  `world.png`, and `n/<TAG>.json` per nation (its states, provinces, cities and politics as
  the build has them, its flag, and its land in parts with the neighbours' around it, as
  province numbers per pixel, plus the rivers).
- `scripts/gazetteer.html`: the page, published with those files. Its atlas is the artifact's
  database: each nation's documents at `n/<TAG>/<key>/<kind>` (`states`, `provinces`,
  `cities`, `rivers`, `rails`, `politics`, `flags`, `people`, `about`, `suggest`, plus `meta`,
  `key` and `req-<id>` requests), where the key is the first 32 hex digits of
  SHA-256("valsora-gazetteer|TAG|password"); `planned/list` (nations not on the map yet,
  written by the owner only); the owner's passwords at `data/users/<owner>/keys`. Pictures
  are the artifact's uploaded files, kept by id.
- `scripts/gazetteer.py`: the import, and the functions `read_layers.py` and `build_mod.py`
  call. `check_mod.py` checks railways, building caps and slots, resources and manpower.
