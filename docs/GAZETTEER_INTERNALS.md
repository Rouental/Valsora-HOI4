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
  Claude's sandbox). Test the page first: `python3 tests/gazetteer/run.py` and `traits.py`.
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
  cities (one per province, victory points, the capital); rivers (major, minor, erase
  strokes); railways (level 1-5); names, full titles and adjectives under every government and
  each ideology, the ruling sub-ideology; the head of state (name, titles, portrait, traits),
  each other party's sub-ideology, leader, portrait and traits, generals, admirals and
  advisors (traits, an advisor's post); flags (one per government too); map colour, culture,
  motto, anthem, description; suggestions (areas, lines and points anywhere on the world,
  labelled); status, notes and requests (new sub-ideologies, subject types, map changes ...).
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
  ...): corps commanders and navy leaders of skill 3 (the page has no skill fields; the notes stay in a comment and
  on `status`'s list for the author), with their portraits, or a generic one of the nation's culture
  (`cultures.unit_portraits`); advisors with a post (2026-10-15, later) in that slot (the post's usual cost, the ledger
  of their first trait, `allowed` their nation); others stay on that list. **Traits** (author, 2026-10-15: "add the
  option to add base-game traits to leaders, as well as the option to request new traits"): rulers, party leaders,
  generals, admirals and advisors take up to six of the base game's (`source/vanilla/index/traits.json`, made by
  `vanilla_sync.py`: the traits the game's own characters have, by kind and advisor post, Earth's one-country ones
  left out; `facts_export.py` puts them in `index.json`), and **Ask for a new trait** is a request of kind `trait`.
  `check_mod.py` checks every trait of ours against the game's own (country leader traits for rulers and advisors,
  unit leader traits for commanders), each advisor's slot and its own `idea_token` (mutation-tested, 6 of 6). A flag in HOI4's 82:52 shape (within 4 %)
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
