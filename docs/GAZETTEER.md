# The Valsora Gazetteer

A web site where friends fill in the facts of their own nations: once you have drawn its
states on the `.pdn`, state names, terrain, rivers, cities (their victory points and size),
population, railways, supply hubs, resources and buildings; at any time, its names and titles
under each government, its sub-ideologies, its flags, its ruler and party leaders (names,
titles, portraits, traits), the characters it already has in the game (Roland and Serelle,
Rouental's, among them, their skills and stats too), its political advisors, generals, admirals
and other advisors (with the base game's traits, and the commanders' skill and stats), its
companies (arms makers and industrial concerns, with their logos), its colour, culture, motto
and anthem, its releasables (their land, names, government, flag and ruler), the ones already
in the game among them (Rouental's, the risers of its civil war, Belekria's Tethia),
suggestions for the map (its states and cities among them, before you draw them), and requests
for things the game doesn't have yet (a new trait or kind of company among them). Each nation is
locked behind a password you give its player, so nobody can change anyone else's nation.

**Every function of the site**, where it sits and what it does in the game, is listed in
`docs/GAZETTEER_FUNCTIONS.md` (2026-10-15), for sorting them into the final layout.

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
   When the rules file changes (it did on 2026-10-15, later, for admins and releasables),
   paste it again the same way.
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

## Admins (Merlo)

Admins sign in with Google as you do and get the same Owner tools: passwords, nations not on
the map yet, map tools, requests, suggestions and the file of every nation. Only you can add or
remove them. To add one: **Owner tools › Admins**, type their Google address, **Add**. They
open the site, scroll to the bottom and press **Sign in with Google** with that account. Remove
them with **Remove** beside their address. The list is kept in the database (`admins/<their
address>`); the rules let only your account change it.

## A nation's map tools wait for its states

A nation's map tools (the State and Cities tabs, and terrain, cities, rivers, railways and supply
hubs on the map) open only once its states are your own lines: drawing them later cuts its
provinces again, and what was entered on the old ones would land in the wrong places. A nation
counts as ready when no two of its states share an area your Necessary Borders and Necessary
States lines enclose (the build splits an area you left without state lines into states of about
1,300 px); a nation of single pieces (one state, islands) counts too. On 2026-10-15, 39 of 161
nations were ready: Rouental, Cardonia, Kurikia, Merlovich, Leithanien, Selto, Placeholdaire,
San Sierra and 31 nations of one piece each (Seigne, Evriches, Guedelon, Devlon, the Holy See
...). Placeholdaire and San Sierra each had an island with no line on it cut into two states (an
old placeholder state and the old 650 px rule); each is one state now.

Until then its player sees its land without the states the build cut, and can fill in its names,
flags, people and releasables, and suggest its states and cities with the Suggest tool: a
**State** for each (the default there), lines along borders, and a point for each city, each
saying what it is. A drawn state keeps only the nation's own land inside its line, and none of a
state drawn before it, so a player draws past the coast and the borders and the states fit
together without overlapping; **Make it a state** turns an area drawn before into one.
Use them when you draw (below). When you have drawn a nation's states, its tools open by
themselves at the next update of the site. **Owner tools › Map tools** opens or closes any
nation by hand (Automatic, Open, Closed); a nation's own Map tab has the same button for you.

## Releasables

On the **Releasables** tab, a player adds the nations that could be released from theirs: its
name, adjective and full title, its ruling sub-ideology, map colour, flag, ruler (name, titles,
portrait) and a few words about it, and its land. With the **Releasables** tool they pick its
states on the map, whole (a state belongs to one releasable; **Take them away** removes them),
or, while their map tools are closed, draw its land as areas. In the game a releasable is a
country owning nothing at the start, with cores on its states, so its nation can release it
from the diplomacy screen. HOI4 gives cores on whole states, never on provinces (a formable
nation works the same way), so a releasable whose border runs through a state needs that state
split: the player draws the line with the Suggest tool and you draw the state line. The first
releasables (before this) held provinces; they count as the states those cover by half, and are
saved as states once their land changes.

**The ones already in the game** are on the same tab: under **In the game**, those the mod lets
the nation release (Rouental's 13, Belekria's Tethia), and under **In the civil war**, those that
rise in it (Rouental's seven). Each card shows the game's names, government, colour, flag, ruler
and states in grey, and anything filled in replaces them: a new name, a flag, a ruler, other
states (with the Releasables tool, while the nation's map tools are open). **Undo every change
to it** puts the game's back. A state can belong to a releasable and to a riser of the civil war
at once, as cores can overlap in HOI4; one of the game's releasables always keeps a state. A
riser led by one of your own characters (Brillagne's Mahaut, HMMLA's Serelle) points to the
People tab: she is changed there, and her copy follows. The changes are made on the page of the
nation the releasable comes from (the owner of its first state), never on another's.

A friend whose page can't reach the atlas still gets the whole page: their changes stay in
their browser, and **Nation › Save a file** gives them a file to send you. Load it with
**Nation › Load a file** on that nation and it joins the atlas.

## What friends fill in

| Where | Facts | In the game |
|---|---|---|
| State tab | name, population, kind of state (building slots), infrastructure, civilian and military factories, dockyards, air base, anti-air, naval base, resources, notes | the state's history file; factories and dockyards are cut to the slots, island bases to vanilla's caps |
| map, Terrain tool | each province's terrain (plains, forest, hills, mountains, desert, marsh, jungle, urban) | `definition.csv` and `terrain.bmp` |
| map, Rivers tool | major and minor rivers as lines; erase strokes take away rivers already in the game | drawn into the river layers before `rivers.py` traces them, exactly like yours |
| Cities tab and tool | cities (one per province, as many as they like in a state), their victory points (how much the place matters: 1 minor to 50 foremost), their size (village to metropolis), the national capital (★) and each state's capital (◆) | victory points and their names; the capital city's state becomes the capital; each state's capital is its main city: its first victory point, its supply hub (unless they place their own) and where its troops start. Unmarked, a state's capital is the national capital if it's there, else the city with the most victory points. Size only shares out a total population (Nation tab) |
| map, Railways tool | railways (level 1-5) through cities and places | `map/railways.txt`: the shortest way over land between the provinces under the points, as the page draws it |
| map, Hubs tool | supply hubs | `map/supply_nodes.txt`: once a nation has its own, only those and its capital |
| map, Suggest tool | states (their own land inside the line, none of an earlier one's), areas, lines and points drawn anywhere on the world (a border, an island that should be theirs, a mountain range, where an undrawn nation goes), each with what it is | nothing by itself: a layer for you (below) |
| Politics tab | name, full title and adjective under every government and each ideology; ruling sub-ideology | localisation, `nations.LEADERS` |
| People tab | head of state (name, titles, portrait, traits); each other party's sub-ideology, leader, portrait and traits; the characters already in the game (for your own nations' characters, as Roland and Serelle: name, the name taken on coming to rule, titles, sub-ideology within its ideology, traits, portrait, and a commander's rank, skill and stats); political advisors (a section of their own); generals, admirals and other advisors (name, portrait, traits, an advisor's post, a general's rank, a commander's skill and stats, notes); traits are the base game's (up to six each, picked from lists by kind: a ruler's, a general's, an admiral's, each advisor post's), and **Ask for a new trait** sends you a request for one the game doesn't have; companies (name, logo, kind, notes): an arms maker of one of the base game's 28 kinds (tanks, ships, aircraft, land equipment) or an industrial concern of one of its 14, and **Ask for a new kind of company** sends you a request | the rulers and party leaders, with their titles shown on the portrait and their traits; your characters changed where they are (a copy, as Mahaut at Brillagne, changes with them); generals and admirals as characters from the start (their skill and stats, skill 3 where not given; their traits; their portraits or a generic one of the nation's culture); advisors in their post on the political screen (the post's usual cost, their traits); an arms maker as a military-industrial organisation of its kind (with Arms Against Tyranny) and, without that DLC, the designer of its kind in the political screen; a concern in the political screen's industrial concern slot, with its kind's trait and research bonus; logos as the company's icon (the whole logo fitted into 64 × 64), else the game's for its kind; the notes are a list for you |
| Releasables tab and tool | releasables: name, adjective, full title, ruling sub-ideology, colour, flag, ruler, notes, land (whole states, or drawn areas); the game's own and the civil war's risers: the same, over the game's | a country each, owning nothing, with cores on its states (and those its areas cover by half; the largest is its capital), its names, ruler, colour and flag; culture its nation's. The game's own keep their tags, with what was changed |
| Nation tab | status (in progress / finished), flags (one, and one per government if they like; each slot shows the game's flag until a picture is sent), map colour, culture, motto, anthem, description, notes for you, requests; how far it is (states named counts the names already on your map) | flags into `source/flags/`; the map colour; the rest is for you |

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

Nations whose leaders are your own characters (Rouental, Merlovich) show them on the People
tab as the game has them, and every field can be changed but the ideology, which the focus tree
names: a sub-ideology stays within it. Their generated party leaders (Rouental's democrat and
communist) are changed the same way. The ruling sub-ideology isn't on their Politics tab.

## Your tools on the start page

**Owner tools** (only you and your admins see them, signed in): the passwords; nations not on
the map yet; **map tools** (open, closed or automatic, per nation); every **request** (set it
done or declined, and reply; the player sees the reply with their nation); every
**suggestion** (shown on the world map, or opened where it was drawn); **admins** (only you
change them); **Start over** (2026-10-16, your "blank slate"; yours alone, your admins don't see it): press **Clear
every nation…**, then **Yes, go on** (the first confirmation), then type CLEAR and press **Clear everything now** (the
second; **Cancel** backs out at either) to delete
everything entered for every nation with a password (facts, pictures, suggestions, requests, status and notes); the
passwords, admins, nations not on the map yet and map-tool switches stay, and what a player's browser kept from before
(unsent changes, an offline copy) is dropped rather than sent back. It can't be undone, so save every nation as a file
first if you want a copy. And **Save every nation as a file**, the whole atlas in one file to send Claude.

**The mod from the map alone** (2026-10-16): Rouental's page, the only one imported so far, was taken out of the mod
(`source/gazetteer/`, with its river, railway, terrain, cities, admiral and "Test" releasable), so the mod is built from
the `.pdn` alone until the next import.

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
  every suggestion with its label (a drawn state as the page shows it: the nation's land inside
  its line that an earlier one doesn't hold); import it into the `.pdn` as a layer (it lines up
  exactly) and draw from it. `dist/gazetteer_suggestions_preview.png` shows them over the map.
- **Releasables** get a tag each at their first import (from their name, never one in use or
  the base game's), kept from one import to the next. `status` lists their cores; one holding
  no state is left out of the build with a note.
- **Nations whose map tools are closed**: their states, provinces, cities, rivers and railways,
  and their releasables' states, are left out at the import (the file carries your switches;
  the import reads which states are drawn from the last build).
- **By hand**: requests (new traits and kinds of company among them), advisors without a post, characters' and
  companies' notes, cultures and flags of other shapes; `status` lists them.
- **Traits** are the base game's (`source/vanilla/index/traits.json`, made by `scripts/vanilla_sync.py` from your copy of
  the game: the ones its own characters have, Earth's one-country ones left out); the import keeps only those of the right
  kind, and `check_mod.py` checks every trait in the mod against the game's.
- **Companies** are of the base game's kinds (`source/vanilla/index/companies.json`, from the same script): its generic
  arms makers (the military-industrial organisations of Arms Against Tyranny, each also the designer of its kind for
  players without the DLC: a tank maker gives +15 % armour research, as the game's generic one does) and the kinds of
  industrial concern its own countries' concerns most often are (the research bonus and cost they most often have). A
  nation's own designer hides the game's generic one of its kind; the game's generic organisations stay beside the
  nation's. `check_mod.py` checks every organisation and idea of ours against the game's.

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
- Only your Google account (named in the rules) and the admins you add can make passwords,
  read the list of them, add nations that aren't on the map and open map tools; only yours can
  change the admins. Nobody else can write anything without a password, and with one only that
  nation's own kinds of documents, pictures under 800 kB.
- Tested against Google's own Firebase emulator with these rules: listing every nation, a
  nation's folders or every states document, reading your passwords, reading or changing the
  admins, opening a nation's map tools, making, replacing or deleting a password, writing
  without one or writing an unknown document were all refused; writing with the password
  worked; another Google account got no owner tools; an admin got them, but couldn't add an
  admin, even straight at the database. The live database answered the same to a stranger
  (2026-10-15, with the first rules, before admins).
- The settings in the page (`source/gazetteer_site/firebase-config.json`) are not secret:
  every Firebase web page carries them, and the rules are what protect the data.
- What a password can't stop: its holder can change or clear that nation (that is the point;
  give a new password if one leaks). Google's free plan allows 50,000 reads and 20,000 saves
  a day, far more than a group of friends uses; if it ever ran out, it starts again the next
  day.

## How it is made

- `scripts/facts_export.py` (after a build): `work/gazetteer/`: `index.json` (every nation,
  whether its states are drawn (`final`, from `gazetteer.finals`), sub-ideologies, the world's
  owners for the start page's map, the base game's tags),
  `world.png`, and `n/<TAG>.json` per nation (its states, provinces, cities and politics as
  the build has them, its characters and the releasables the game has for it, its flag, and
  its land in parts with the neighbours' around it, as province numbers per pixel, plus the
  rivers). Portraits of ours are on the site; the base game's are Paradox's and never are.
- `scripts/gazetteer.html`: the page. On the web site its atlas is the Firestore database:
  each nation's documents at `n/<TAG>/<key>/<kind>` (`states`, `provinces`, `cities`,
  `rivers`, `rails`, `politics`, `flags`, `people`, `about`, `suggest`, `releasables`, plus
  `meta`, `key`, `req-<id>` requests and `img-<id>` pictures), where the key is the first 32
  hex digits of SHA-256("valsora-gazetteer|TAG|password"); `planned/list` (nations not on the
  map yet) and `planned/unlock` (your map-tool switches), written by admins only; the
  passwords at `owner/keys`; the admins at `admins/<address>`. Firestore keeps no
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
