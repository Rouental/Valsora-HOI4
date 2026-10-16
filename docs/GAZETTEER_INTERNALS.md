# The Gazetteer: how it works (for Claude)

The author's guide is `docs/GAZETTEER.md`; this is the working detail, moved out of `CLAUDE.md` on 2026-10-15 (later)
so the manual every session reads stays short. `CLAUDE.md` keeps a summary and the rules that must not be broken.
Keep this file up to date when the Gazetteer changes.

The author's request (2026-10-14): a tool their friends open by a link to fill in their own
nations once the states are drawn, instead of the `.pdn` ("tedious and hard to keep track of,
especially with cities"). **Since 2026-10-15 it is a web site,
https://rouental.github.io/Valsora-HOI4/**: GitHub Pages serves the `gh-pages` branch, which
holds only the site (the author allowed that branch for it: "it's ok to put it on a new
branch"; pushing it switched Pages on), and the atlas is the Firestore database of the
author's Firebase project `valsora-hoi4` (free Spark plan). Players need no account; only the
author signs in, with Google. It moved because on claude.ai only friends invited by email as
Editors can save (a public link's visitors can only view), and the author didn't want to ask
everyone for an email. The first home, the claude.ai artifact
**https://claude.ai/artifact/PqTTD5FuFJhpL4JKp8sumN** (`scripts/gazetteer.html` published with
`work/gazetteer/`, declaring `db` (rule: `planned` written by the owner only), `user`
(profile), `downloads` and `assets`), still works with an atlas of its own, but is no longer
used. One page serves both: `FIREBASE` is null on claude.ai and filled in by
`gazetteer_site.py` for the site.
- **Republish the site** after map changes (the facts are kept by map pixel):
  `sh scripts/publish_site.sh "message"` (`facts_export.py`, `gazetteer_site.py`, then
  `work/gazetteer_site/` alone as the next commit of `gh-pages` through a worktree, pushed;
  nothing is committed when the site is unchanged). Pages redeploys in a minute or two (the
  "pages build and deployment" run in Actions; github.io itself can't be reached from
  Claude's sandbox). Test the page first: `python3 tests/gazetteer/run.py`, `traits.py`, `companies.py`, `ingame.py`
  and `reset.py`.
- **Firebase** (set up by the author, 2026-10-15): Firestore (Standard, production mode), Google
  sign-in with `rouental.github.io` among the authorized domains, the web app's settings in
  `source/gazetteer_site/firebase-config.json` (not secret). The rules,
  `source/gazetteer_site/firestore.rules`, are pasted in the console by the author with their
  Google address for `OWNER_EMAIL`, which is never committed: change the file, then ask them to
  paste it again (they changed on 2026-10-15, later: admins, `releasables`). They allow `get`
  and `list` inside a nation's folder but nothing on `n` and no `{path=**}` match, so neither
  `n`, a nation's folders nor a collection-group query can be listed; writes need the folder's
  `key` document (only admins write those) and a known kind; `owner/*` is the admins' alone;
  `planned/*` is read by all, written by admins; `admins/<address>` is read by admins and
  written by the author alone (`isAdmin()` = the author's address, or an `admins` document
  under the signed-in address). Cloud
  Storage needs the paid plan, so pictures are documents beside the facts (`img-<id>`: a data
  URL of at most 640 px, JPEG over 400 kB; the rules cap them at 800,000 characters).
  Firestore keeps no array directly inside an array: lines' points are stored as
  `{"_a": [x, y]}`. The SDK is Google's, bundled into one module
  (`source/gazetteer_site/README.md`).
- **Map tools wait for a nation's states** (author, 2026-10-15: "if a nation's states have not
  yet been defined, they would be able to make suggestions for me to make their state borders,
  and do things like provide flags, leaders, full nation names, etc. Then once their state
  borders have been set in the mod, full customization would be unlocked"). `gazetteer.finals`
  marks a nation final when no two of its states share an area the Necessary Borders and
  Necessary States lines enclose (the states `apply_outlines.py` cuts from an area left without
  lines do); one-piece nations count (Claude's suggestion, accepted). 39 of 161 on 2026-10-15,
  later: AIS CRD KRK LNT LTH ROU SSA STO and 31 of one piece (Placeholdaire and San Sierra each had
  an island without lines in two states, from the placeholder grid and the old 650 px rule:
  merged with `pdn_tools.py attach`, author: "Placeholdaire has all its provinces defined, yet is
  not editable"); Belekria is partly drawn, 121 not at all. Until then the page shows the plain
  land (no cut states), only Map, Politics, People, Releasables and Nation and the Select,
  Releasables (areas) and Suggest tools;
  `planned/unlock` ({TAG: true | false}, Owner tools › Map tools, or the nation's Map tab)
  overrides the rule. The import drops a closed nation's states, provinces, cities, rivers,
  railways and releasables' states (the file of every nation carries `unlock`).
- **Drawn states** (author, 2026-10-15: "when drawing states they should snap to the borders of
  the nation and the borders of other states so that they fit together well and don't
  overlap"): Suggest › State (the default on a closed nation) keeps the nation's own land inside
  the line that no state drawn before it holds (suggestion ids begin with the time), filled
  pixel by pixel in the land's picture (`sugFill`), so a player draws past the coast and the
  borders. **Make it a state** turns an area into one. `gazetteer.py suggestions` clips them the
  same way for the `.pdn` layer.
- **Releasables** (author, 2026-10-15: "allow people to select provinces that could be
  releasables, and then the ability to define flags, names, etc."). The `releasables` document:
  `{rl-<id>: {name, adj, def, ruling, colour, flag, leader {name, desc, portrait}, notes,
  states {"x,y": true}, areas {a-<id>: points}, added}}`; whole states (2026-10-15, later; the
  author asked whether provinces would work in game: HOI4 cores states, for releasables and
  formables alike), a state belongs to one releasable; areas while the map tools are closed.
  The first ones held `provinces {"x,y": true}`: the page and the build read those as the
  states they cover by half, and the page saves them as states once their land changes. The import gives each a tag (`new_tag`: its
  name's letters, never `COUNTRIES`', the base game's (LIB is Liberia's), a planned nation's or
  another releasable's), kept by id. The build (`gazetteer.releasables`) makes each a country
  owning nothing (in `COUNTRIES` as `gazetteer_<tag>` for that build only), with cores on the
  states it holds (whole, or at least half of by provinces and areas, in pixels; the largest is its capital;
  less than half is a note, none at all leaves it out), its names, ruler and colour as facts of
  its tag, its nation's culture, and its nation's ruling sub-ideology when it has none. Its flag
  goes to `source/flags/<tag>.png` at the import like a nation's.
- **Victory points and city size** (2026-10-15, later; the author: "Rouental's capital should be worth more VPs than
  Vair for example, even though Vair is bigger, right?"). A city's victory points are how much it matters (HOI4's
  surrender share, war score, the AI's targets, the size of its marker and name), labelled on the page by what each
  value means (1 minor … 50 foremost, from the base game's: London 50, Washington 40, New York 30, Gibraltar 10,
  Manchester 5); its **size** (`size`: village, town, city, large, metropolis; unset is a town) is apart and only
  weighs the population spread (Nation › Spread a total population: a state's share is area^0.9 × (1 + the weights
  of its cities' sizes, 1 / 3 / 8 / 20 / 50, over 8)). The import keeps `size`; the build doesn't use it.
- **Characters and releasables already in the game** (2026-10-15, later; the author: "Releasables already in the game
  should be represented on the site. For example, Rouental's releasables and revolters, or Tethia in Belekria.
  Leaders already in the game should be represented and editable, for example Roland or Serelle. Their stats should
  be editable as well as their traits"). `facts_export.py` gives each nation `characters` (the ones its history
  recruits, read from the built `common/characters/` with `pdxscript`, the Gazetteer's own left out: name, the name
  taken on coming to rule (`nations.REGNAL_NAMES`), titles, sub-ideology and ideology, ruler or party leader, leader
  traits, a commander's rank, skill, stats and traits, an advisor's post, `copyOf` (`nations.COPIES`), and its portrait
  as a small JPEG when it is ours; a base-game portrait is only marked `base`, never published) and `gameReleasables`
  (the countries the game releases from it, from `work/game_releasables.json`, which `build_mod.py` writes: Rouental's
  13 and Belekria's Tethia (`nations.RELEASABLE`, kind `releasable`) and the civil war's 7 (`nations.CIVIL_WAR`, kind
  `civil_war`, `warOnly` for `CIVIL_WAR_ONLY`), with names, colour, flag, government, ruler and states). The page shows
  them on the People tab (the author's own characters as cards, `gameCharCard`; a generated ruler's and party
  leaders' names and portraits as the grey defaults of the fields they had) and the Releasables tab (sections "In the
  game" and "In the civil war", `gameRelCard`; a releasable's land and a revolter's are kept apart, as HOI4 lets
  cores overlap; a game releasable keeps its last state). Changes are kept beside the rest, so the rules needed
  nothing new: `ch-<character id>` in `people` (`{name, regnal, desc, portrait, sub, traits, unit, rank, skill, attack,
  defense, planning, logistics, maneuvering, coordination, unitTraits}`, an empty list of traits kept as `[]`) and
  `g-<TAG>` in `releasables` (`{name, adj, def, ruling, colour, flag, leader {name, desc, portrait, traits}, notes,
  states {"x,y": true}}`, the states replacing the game's whole). The import keeps `people.game_characters` (only ids
  of the nation's own tag) and `game_releasables` (only those whose parent, by `work/game_releasables.json`, is the
  nation: another nation's page can't change them). The build: `gazetteer.game_releasables` makes each changed one
  facts of its own tag (names, ruling sub-ideology, ruler, colour, merged into the facts), and new land replaces its
  states in `nations.CIVIL_WAR` / `RELEASABLE` by name (the game's capital kept first while it is still in, the rest
  largest first); `gazetteer.patch_characters` patches the hand-made characters' text (`nations.ROU_CHARACTERS`,
  `CHARACTERS`): sub-ideology within its ideology (the focus trees name the ideologies), titles (`desc` after the
  ideology), traits, a commander's rank, skill, stats (its role's only) and traits, names through the localisation
  (`patch_loc`), a new portrait under the sprite's own name, so a copy (Mahaut at Brillagne, Serelle at HMMLA) changes
  with the original; `game_character_names` gives the generated leaders of a hand-made nation (Rouental's democrat and
  communist, whose ids its focus tree names) their names, titles, portraits and traits through `NAMED_LEADERS`.
  Unchanged characters stay byte for byte, and without facts the build is byte-identical. `check_mod.py` checks every
  commander's skill (1–9) and stats (0–9), and that they are its role's (mutation-tested, 2 of 2).
- **Start over** (author, 2026-10-16: "is there a way you could reset any edits made thus far? I'd like a blank
  slate"): Owner tools › Start over (`startOverSec`, `clearEveryNation`; the word CLEAR typed first) deletes every
  document but `key` in each folder of `owner/keys`' nations (the rules let admins delete), then writes `planned/reset`
  `{at}` (admins write `planned/*`; everyone reads it). Unsent changes a browser keeps (`gazetteer-pending:<TAG>`) and
  an offline copy (`gazetteer:<TAG>`) carry the time they were saved (`__at`); one from before the reset is dropped
  when the nation is unlocked (`loadReset`, `staleSinceReset`) instead of being written back. No rules change.
  `tests/gazetteer/reset.py`. The mod's side of the blank slate: `source/gazetteer/` was removed (Rouental's page and
  its assets, `installed.json`) with the flag the import had installed (`source/flags/TES.png`); without facts the
  build is the `.pdn`'s alone.
- **Admins** (author, 2026-10-15: "How would I go about making Merlo an admin on the Gazetteer
  as well, so he can manage passwords and such"): Owner tools › Admins (the author adds or
  removes a Google address: `admins/<address>`); an admin signs in with Google and gets every
  owner tool but that list. The page tells the author from an admin by the list (the author
  isn't on it).
- **Merlo's handoff** (author, 2026-10-15: "a handoff file for Merlo, so that his instance of
  Claude generates in line with this one"): `docs/HANDOFF_MERLO.md`, how to work from this
  repository, recipes, conventions and how to hand work back. Keep it in step.
- **Version 2** (author, 2026-10-14, latest: "each nation should be locked behind a password I
  can give them so that people can't make troll edits on each others' nations ... submit
  flags, leaders, etc ... a function for them to make suggestions ... overseas territory ...
  displayed in a separate box to their mainland"). The first version's only data was the
  author's own test edit (one Lanzerac province set to forest, `facts/LZC-provinces` and
  `nations/LZC`); version 2 doesn't read those collections.
- **What it edits**, per nation: state names, population, kind of state, buildings (within
  slots and vanilla's caps), resources, notes; province terrain (8 types) and supply hubs;
  cities (one per province, victory points, size, the capital, state capitals); rivers (major,
  minor, erase strokes); railways (level 1-5); names, full titles and adjectives under every
  government and each ideology, the ruling sub-ideology; the head of state (name, titles,
  portrait, traits), each other party's sub-ideology, leader, portrait and traits, the
  characters already in the game (below), political advisors (a section of their own),
  generals, admirals and other advisors (traits, an advisor's post, a commander's rank, skill and
  stats); companies (name, logo, kind, notes); releasables, the game's own and the civil war's
  among them (below); flags (one per government too); map colour, culture,
  motto, anthem, description; suggestions (areas, lines and points anywhere on the world,
  labelled); status, notes and requests (new sub-ideologies, subject types, traits, kinds of
  company, map changes ...).
  Overseas parts of a nation and the whole world are boxes in the map's corner. Phone and
  desktop layouts (the author asked for both).
- **Passwords.** A nation's documents are at `n/<TAG>/<key>/<kind>`, the key being the first
  32 hex digits of SHA-256("valsora-gazetteer|TAG|" + the password lowercased, runs of spaces,
  dots, commas and underscores as one hyphen). The store lists a collection's own documents
  only, so `n` lists nothing, even to the owner (tested on the live atlas): without the
  password a nation can be neither found nor changed. `n/<TAG>/<key>/key` marks a real
  password; `meta` (status, notes, `editors` ids) and `req-<id>` requests sit beside the
  facts. The owner's passwords are at `data/users/<owner id>/keys` (private to them), made and
  changed in **Owner tools** (a new password copies the documents and deletes the old ones),
  and the page unlocks every nation for the owner. On the site the passwords are at
  `owner/keys`, the owner is whoever may read it (the rules decide), and a player is a random id
  per browser (`gazetteer-id`) with the name they give on the Nation tab (`meta.editors` keeps
  names on the site, ids on claude.ai). On claude.ai friends had to be invited by email as
  Editors, with no public link (outside viewers can't write), and an Editor could publish a new
  page version; pictures there are the artifact's uploaded assets, stored by id (shown as
  `/_blob/<id>`).
- **Nations not on the map yet**: `planned/list` ({TAG: name, continent}), owner-written; base
  game tags (`index.json` `earth`) are refused. Their page has Politics, People, Map
  (suggestions on the world map) and Nation; their facts carry over once they are drawn.
- **To pull it** from the site: the author's **Save every nation as a file**
  (`valsora-gazetteer-all.json`, each nation's pictures inside as `images`), then
  `python3 scripts/gazetteer.py import` it (Claude can't sign in to the author's Firebase).
  Then rebuild (and `river_provinces.py` after new rivers), run `gazetteer.py suggestions` if
  there are any, and tell the author the open requests and what `status` lists for doing by
  hand. From the claude.ai atlas (the first version): ArtifactData `get` of `data/users/me` / `keys` and of `planned` / `list`,
  both with `out_dir` `work/gazetteer_pull` (never commit the passwords: `work/` is ignored);
  `python3 scripts/gazetteer.py paths work/gazetteer_pull/data/users/<id>/keys.json` names each
  nation's folder; ArtifactData `list` of each with the same `out_dir`; then
  `python3 scripts/gazetteer.py pull work/gazetteer_pull`. It lists the pictures to download:
  the Artifact tool's `read` with `path` = the asset id and `out_dir`
  `work/gazetteer_pull/assets`, then `pull` again.
- **In the build** (`source/gazetteer/<TAG>.json`; Rouental's since 2026-10-15, below): a nation's facts
  win over the `.pdn` and `nations.py` for that nation: its cities replace the Cities layer's dots on its land
  (`regions.json` cities then carry victory points, the capital flag and the state-capital flag), its state names
  replace `state_names.json`'s (the old names still resolve for `nations.CIVIL_WAR` /
  `RELEASABLE`), its capital city replaces `nations.CAPITALS`, each state's main city (its first
  victory point, its supply hub unless the nation placed hubs, where its divisions start) is the
  national capital, else the city marked its state's capital, else the most victory points (the
  northernmost on a tie; the Cities layer's own dots keep their order), its hubs replace the one per
  state (plus its capital), its colour `nations.DISPLAY_COLOUR`. Railways take the shortest
  way over land between the provinces under their points, centre to centre (the page draws
  the same route); shared stretches are written once at the higher level. Rulers and party
  leaders get their names, titles (`desc` after the ideology) and portraits (registered in
  `nations.PORTRAITS` as `<TAG>_gazetteer_<role>`, 156:210 from the top of the picture).
  Hand-made rulers (`HAND_MADE`) keep their leaders. Its generals and admirals (2026-10-15: the author couldn't find
  Rouental's admiral, James Navy) are characters from the start (`gazetteer.characters`, `<TAG>_gazetteer_admiral_1`
  ...): corps commanders (field marshals if the page says so) and navy leaders of the page's skill and stats
  (2026-10-15, later; where not given, skill 3, attack and defence 3, the others 2; the notes stay in a comment and on
  `status`'s list for the author), with their portraits, or a generic one of the nation's culture
  (`cultures.unit_portraits`); advisors with a post (2026-10-15, later) in that slot (the post's usual cost, the ledger
  of their first trait, `allowed` their nation); others stay on that list. **Traits** (author, 2026-10-15: "add the
  option to add base-game traits to leaders, as well as the option to request new traits"): rulers, party leaders,
  generals, admirals and advisors take up to six of the base game's (`source/vanilla/index/traits.json`, made by
  `vanilla_sync.py`: the traits the game's own characters have, by kind and advisor post, Earth's one-country ones
  left out; `facts_export.py` puts them in `index.json`), and **Ask for a new trait** is a request of kind `trait`.
  `check_mod.py` checks every trait of ours against the game's own (country leader traits for rulers and advisors,
  unit leader traits for commanders), each advisor's slot and its own `idea_token` (mutation-tested, 6 of 6).
  **Political advisors and companies** (author, 2026-10-15: "allow people to create political advisors and
  companies"): political advisors are advisors of `political_advisor` (`{role: "advisor", slot:
  "political_advisor"}`), in a section of their own. Companies are `co-<id>` entries of the `people` document (so the
  rules needed no new kind): `{name, kind, logo, notes}`, the kind one of `source/vanilla/index/companies.json`'s
  (`vanilla_sync.companies`: the 28 generic arms organisations of `00_generic_organization.txt` with a name, by group,
  each with the generic designer of `zzz_generic.txt` it is without Arms Against Tyranny; the 14 traits three or more
  of the game's industrial concerns share, not one country's, with their most common research bonus, picture and
  cost; all 30 generic organisations as `templates`), or `concern:<trait>`; **Ask for a new kind of company** is a
  request of kind `company`. The import keeps them as `people.companies` (`[{name, kind, notes, logo}]`). The build
  (`gazetteer.companies`, ids `<TAG>_gazetteer_company_<n>`): an arms company is an organisation
  `<id>_organization` (`include` its kind, `icon` its logo or the kind's, `allowed = { original_tag = TAG }` as the
  game's national ones) in `common/military_industrial_organization/organizations/valsora_gazetteer_organizations.txt`
  and a designer idea (`designer = yes`, the generic designer's picture, research bonus, trait and costs) in
  `common/ideas/valsora_gazetteer_companies.txt`, where a concern is an `industrial_concern` idea; logos are
  `gfx/interface/ideas/VAL/<id>.dds` (the whole logo fitted into 64 × 64), sprites `GFX_idea_<id>` in
  `interface/valsora_gazetteer_companies.gfx`. The files are written only when a nation has companies. `check_mod.py`
  checks that each organisation of ours includes one of the game's templates, is for a country of the mod and is
  localised, and that each idea of ours is localised and has the game's traits (mutation-tested, 5 of 5). A flag in
  HOI4's 82:52 shape (within 4 %)
  becomes `source/flags/` at the import, once per picture (`source/gazetteer/installed.json`);
  others are fitted by hand, as the author's are. Pictures are kept at most 1,200 px, heavy
  opaque ones as JPEG. Without facts the build is byte-identical to before (checked again for
  version 2). `check_mod.py` checks railways (adjacent, in states, level 1-5), building caps and
  slots, resources and manpower (mutation-tested, 7 of 7). `GAZETTEER_DIR` and
  `GAZETTEER_FLAGS` point the scripts at other folders (tests).
- **Tests** (Playwright, with a stand-in for claude.ai's runtime that keeps its rules: path
  grammar, private `data/users`, the owner-only `planned`, queries, `/_blob/` pictures): the
  owner makes passwords, adds a nation not on the map, fills in Rouental's mainland and
  islands, Seigne's people and the planned nation's suggestions, changes a password; a
  friend in another browser is locked out until the password (typed loosely) opens it, an old
  password no longer does; desktop and phone, light and dark; the view-only and offline modes.
  On the site too: releasables picked by province on Rouental and drawn as areas on Hollier
  (closed), Hollier's map tools opened and closed again, the author adding Merlo as an admin,
  Merlo making a password but refused when adding an admin; the import closing Hollier's map
  facts, opened by the switch; a build with three releasables (check_mod clean; cores, capital,
  names, ruler), and without facts byte-identical.
  The site is tested the same way against Firebase's own emulators (firebase-tools 15, Java 21;
  `gazetteer_site.py --emulator 127.0.0.1:8080:9099 --project demo-...`, the rules loaded with a
  test owner), plus the rules attacked straight over REST (listing `n`, a nation's folders or
  every `states` document, reading `owner/keys`, writing `planned`, making, replacing or
  deleting a `key`, writing without a password or an unknown document: all refused; writing
  with the password allowed) and another Google account getting no owner tools. Tests sign in
  with the emulator's unsigned tokens (`window.__fb`, only in an emulator build): Google's
  sign-in window can't load in the sandbox. A file saved from the site imports with its
  pictures.
  `tests/gazetteer/companies.py`: the People tab's sections, a political advisor with the political advisors'
  traits, an arms company with a logo, a concern with notes, a request for a new kind, a company deleted, the file;
  that file imported and built (check_mod clean: organisation, designer, concern, logo and political advisor as above).
  `tests/gazetteer/ingame.py`: on Rouental, Roland's name, sub-ideology and a trait, Serelle's rank, skill and stats and
  a trait taken away, a site general's skill (and a stat held to 9); the Releasables tab's sections (13 in the game, 7
  in the civil war), Carcarelle renamed and given Ghessone's only state (which Ghessone keeps: a game releasable keeps
  its last state), Brillagne's ruler pointing to Mahaut, a revolter picked showing the civil war's land apart; a city's
  victory points and size; Belekria's Tethia while its map is closed; the file of every nation. That file imported and built: Roland's sub-ideology, titles kept, trait and new name; Serelle and
  her HMMLA copy a field marshal of skill 5; the general's logistics 9; Carcarelle Libre with cores on its four states
  (one shared with Ghessone); check_mod clean.
