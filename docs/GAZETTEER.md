# The Valsora Gazetteer

A web site where friends fill in the facts of their own nations: once its states are drawn
on the `.pdn`, state names, terrain, rivers, cities, population, railways, supply hubs,
resources and buildings; at any time, its names and titles under each government, its
sub-ideologies, its flags, its ruler and party leaders (names, titles, portraits), its
generals and admirals, its colour, culture, motto and anthem, suggestions for the map, and
requests for things the game doesn't have yet. Each nation is locked behind a password you
give its player, so nobody can change anyone else's nation.

**Address:** https://rouental.github.io/Valsora-HOI4/

Anyone with the address can open it; players need no account, no sign-in and no email. The
site is served by GitHub Pages from this repository's `gh-pages` branch, and what people
enter is kept in your Firebase project, `valsora-hoi4` (Google's free plan).

The first version, a claude.ai page (https://claude.ai/artifact/PqTTD5FuFJhpL4JKp8sumN), is
the same page with an atlas of its own. It could only save for friends you invited by email
as Editors, so it is no longer used.

## Setting it up (once)

1. **The database's rules.** In the Firebase console, open **Firestore Database › Rules**
   (`https://console.firebase.google.com/project/valsora-hoi4/firestore/rules`). Replace
   what is there with `source/gazetteer_site/firestore.rules`, with your Google address in
   place of `OWNER_EMAIL`, and press **Publish**. Until then the database refuses everything.
2. **GitHub Pages** switched itself on when the `gh-pages` branch was first pushed
   (2026-10-15). The repository's **Settings › Pages** shows it: **Deploy from a branch**,
   **gh-pages**, **/ (root)**.
3. Open the site, scroll to the bottom and press **Sign in with Google**, with the account
   the rules name. **Owner tools** appear at the top of the start page.

## Sharing it with friends

1. Under **Owner tools › Passwords** (only you see them), press **Make one** for each
   friend's nation and send them its password (**Copy**) with the address. A link straight
   to their nation is the address with `#TAG` at the end (`…/Valsora-HOI4/#ROU` for
   Rouental).
2. They open it, find their nation, and type the password once; the page remembers it on
   that device. On the Nation tab they can give their name, so you can see who edited what.

A password opens one nation and no other. **New password** locks the old one out and keeps
everything that was entered. You never need passwords yourself: signed in, the page unlocks
every nation for you.

A friend whose page can't reach the atlas still gets the whole page: their changes stay in
their browser, and **Nation › Save a file** gives them a file to send you. Load it with
**Nation › Load a file** on that nation and it joins the atlas.

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

Pictures (flags, portraits) are kept at up to 640 px, plenty for HOI4's 82 × 52 flags and
156 × 210 portraits.

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

**Owner tools** (only you see them, signed in): the passwords; nations not on the map yet;
every **request** (set it done or declined, and reply; the player sees the reply with their
nation); every **suggestion** (shown on the world map, or opened where it was drawn); and
**Save every nation as a file**, the whole atlas in one file to send Claude.

## Getting the facts into the mod

Press **Owner tools › Save every nation as a file** and send Claude the file
(`valsora-gazetteer-all.json`; the pictures are inside it). Claude can't sign in to your
Firebase, so the file is how the facts come in. Claude runs:

```
python3 scripts/gazetteer.py import valsora-gazetteer-all.json   # or a nation's own file
python3 scripts/gazetteer.py status          # what is there, and what is left to do by hand
python3 scripts/gazetteer.py suggestions     # the suggestions as a layer for the .pdn
sh scripts/run_all.sh
```

They write `source/gazetteer/<TAG>.json`, one per nation, replacing what was there for it,
and keep the pictures in `source/gazetteer/assets/`. (The claude.ai page's atlas came in
with `gazetteer.py paths` and `pull`, which still work.)

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
survive new provinces, states and borders. After a map change Claude rebuilds and puts the
new map on the site (below); the facts stay where they are. Facts whose pixel lands on
another nation are left out (with a note in the build), and the page's Nation tab counts
them.

## How safe it is

- A nation's facts are stored at an address made from its password, and the database's
  rules refuse to list nations or their folders: without the password a nation can be
  neither found, read nor changed.
- Only your Google account (named in the rules) can make passwords, read the list of them,
  and add nations that aren't on the map. Nobody else can write anything without a password,
  and with one only that nation's own kinds of documents, pictures under 800 kB.
- Tested against Google's own Firebase emulator with these rules: listing every nation, a
  nation's folders or every states document, reading your passwords, making, replacing or
  deleting a password, writing without one or writing an unknown document were all refused;
  writing with the password worked; another Google account got no owner tools.
- The settings in the page (`source/gazetteer_site/firebase-config.json`) are not secret:
  every Firebase web page carries them, and the rules are what protect the data.
- What a password can't stop: its holder can change or clear that nation (that is the point;
  give a new password if one leaks). Google's free plan allows 50,000 reads and 20,000 saves
  a day, far more than a group of friends uses; if it ever ran out, it starts again the next
  day.

## How it is made

- `scripts/facts_export.py` (after a build): `work/gazetteer/`: `index.json` (every nation,
  sub-ideologies, the world's owners for the start page's map, the base game's tags),
  `world.png`, and `n/<TAG>.json` per nation (its states, provinces, cities and politics as
  the build has them, its flag, and its land in parts with the neighbours' around it, as
  province numbers per pixel, plus the rivers).
- `scripts/gazetteer.html`: the page. On the web site its atlas is the Firestore database:
  each nation's documents at `n/<TAG>/<key>/<kind>` (`states`, `provinces`, `cities`,
  `rivers`, `rails`, `politics`, `flags`, `people`, `about`, `suggest`, plus `meta`, `key`,
  `req-<id>` requests and `img-<id>` pictures), where the key is the first 32 hex digits of
  SHA-256("valsora-gazetteer|TAG|password"); `planned/list` (nations not on the map yet,
  written by the owner only); the owner's passwords at `owner/keys`. Firestore keeps no
  array directly inside another, so lines' points are stored as `{"_a": [x, y]}`.
  On claude.ai (the first version) the same documents are in the artifact's database, the
  passwords at `data/users/<owner>/keys`, and pictures are the artifact's uploaded files.
- `scripts/gazetteer_site.py`: `work/gazetteer_site/`, the site: `index.html` (the page in a
  document of its own, with the project's settings), Google's Firebase SDK bundled into one
  file (`source/gazetteer_site/`, so the site needs no other server), and the map data.
  Committed alone on the `gh-pages` branch, it is what GitHub Pages serves.
- `source/gazetteer_site/`: the project's settings, the rules, the SDK bundle and how to
  rebuild it (its README).
- `scripts/gazetteer.py`: the import, and the functions `read_layers.py` and `build_mod.py`
  call. `check_mod.py` checks railways, building caps and slots, resources and manpower.
