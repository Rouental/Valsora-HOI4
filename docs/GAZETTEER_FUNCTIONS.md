# The Gazetteer, function by function

Every function of the site (https://rouental.github.io/Valsora-HOI4/) as it stands on 2026-10-15: where it sits now,
and what it does in the game, for sorting them into the final layout (the tutorial will follow that layout). Each has
a code (S the start page, O Owner tools, H a nation's frame, M the map, then the tabs: ST State, CI Cities, MP Map,
PO Politics, PE People, RL Releasables, NA Nation), so a new place can be given as "MP2 to the Nation tab".

Marks: **owner**: only you and your admins, signed in. **open**: only once a nation's map tools are open (its states
are your own lines, or you opened them). **closed**: only while they are closed. Everything else is for anyone with
the nation's password; without it, the page shows the map and what the mod has, and changes nothing.

## The start page

- **S1 World map.** Every nation in its colour; the pointer shows its flag and name and lights its land; a click
  opens it.
- **S2 Find a nation.** Search by name or tag, with the count of nations shown.
- **S3 The list.** The nations by continent (flag, name, states, provinces), those not on the map yet last; a click
  opens one. **owner**: a dot per nation (not started, in progress, finished) and its key.
- **S4 A nation's own address.** The site's address with `#TAG` (`…/Valsora-HOI4/#ROU`) opens that nation at once.
- **S5 Sign in with Google** (at the foot of the page; **owner**): signed in, Owner tools appear and every nation
  opens without its password; **Sign out**; your name in the top right.

## Owner tools (at the top of the start page; owner)

- **O1 Refresh.** Reloads every nation's status and requests.
- **O2 Passwords.** Find a nation; each nation's password, **Copy**, **Make one** / **New password** (the old one
  stops working; nothing entered is lost); its status and how many of its requests are open.
- **O3 Nations not on the map yet.** Add one (tag, name, continent; the base game's tags and taken ones are
  refused); **Remove**.
- **O4 Map tools.** Each nation's map tools: Automatic (open once its states are drawn), Open or Closed; find a
  nation; how many are open.
- **O5 Requests.** Every nation's requests, the open ones first: set Open, Done or Declined, write a reply (the
  player sees it under the request), **Delete**.
- **O6 Suggestions.** Every nation's suggestions: **Show them on the world map** (or hide them), and **Open** one
  where it was drawn.
- **O7 Admins.** Who they are; add one by Google address, **Remove** (only you).
- **O8 Save every nation as a file.** The whole atlas, pictures inside, for Claude to bring into the mod.
- **O9 Start over** (2026-10-16; the author's alone, not the admins'). **Clear every nation…**, then **Yes, go on**,
  then CLEAR typed and **Clear everything now** (two confirmations; **Cancel** at either): everything entered for every nation is
  deleted (facts, pictures, suggestions, requests, status, notes); passwords, admins, nations not on the map yet and
  the map-tool switches stay.

## A nation: the frame round it

- **H1 All nations.** Back to the start page.
- **H2 The nation's flag and name** in the top bar.
- **H3 Saving.** Saved, Saving…, Locked, Kept in this browser, View only, Not saved; the pointer on it says more.
- **H4 Password box.** The nation's password and **Unlock**; the device remembers it. **owner**, for a nation
  without one: **Make a password**.
- **H5 Undo** (or Ctrl+Z): the last change (a stroke of paint counts as one).
- **H6 Bigger facts** (↕ beside the tabs): the facts panel wider and the map smaller, and back.
- **H7 The status line** under the map: what is under the pointer (state, city, releasable, terrain, supply hub,
  coast, its pixel) and the page's short messages.
- **H8 Guide** (beside the nation's name; 2026-10-16): the quick-start guide, six short illustrated steps (welcome
  and saving, the map and its tools (the open map's, or Suggest while the states aren't drawn), how big a state is
  (2026-10-18, in the place of 2026-10-17's province step: Rouental's, Cardonia's and Zukchiva's states at one scale),
  the tabs, asking for more, the password). It shows by itself once in a browser, the first time a player unlocks a nation (never to the
  owner); Skip, Escape or Start close it. A first version of the tutorial: it will follow the final layout.

## The map

The tools, with their keys. While a nation's map tools are closed only M1, M7 and M8 show; on the World map box, M1
and M8.

- **M1 Select (V).** Click a state to open it on the State tab, a city for the Cities tab, a suggestion to pick it on
  the Map tab, a releasable's state (with the Releasables tab or tool on) for its card. Drag moves the map, the wheel
  or two fingers zoom; with any tool, right-drag, middle-drag or Space-drag moves it. Esc lets go of the state.
- **M2 Terrain (T)**, **open**. Pick plains, forest, hills, mountains, desert, marsh, jungle, urban or the map's
  default, then click or drag over provinces. *Game:* each province's terrain.
- **M3 Cities (C)**, **open**. Click your land to place a city (one per province; 5 victory points and a town to
  begin with); drag one to move it. *Game:* victory points (CI2).
- **M4 Rivers (R)**, **open**. A major river, a minor one, or an erase stroke (it takes away the game's rivers under
  it): click points (double-click or Enter finishes, Backspace takes the last one back, Esc cancels) or drag
  freehand. The game's rivers show in blue. *Game:* rivers, drawn and traced like yours.
- **M5 Railways (L)**, **open**. Level 1 to 5; click cities or places in order (points snap to cities, hubs and
  other railways' points); it runs by the shortest way over land, with a warning where it would cross water.
  *Game:* railways (only the ones drawn here: the generated network waits).
- **M6 Hubs (H)**, **open**. Click a province to add or remove a supply hub. *Game:* supply hubs; once a nation has
  its own, only those and its capital.
- **M7 Releasables (E).** Pick a releasable (the nation's own, the game's, the civil war's). Open: **Add states** /
  **Take them away**, then click or drag over states. Closed: draw its land as areas.
- **M8 Suggest (S).** Draw on the map or on the world: a **State** (closed only: it keeps the nation's land inside
  the line and none of a state drawn before), an **Area**, a **Line** or a **Point**, then say what each is on the
  Map tab (MP2). *Game:* nothing by itself; a layer for you.
- **M9 While drawing:** the number of points, **Finish**, **Undo point**, **Cancel**.
- **M10 The hint** under the tools: what the tool does (on a phone, a tap shows all of it).
- **M11 Colours**, **open**: States, Terrain, Population (a shade per density).
- **M12 Zoom in, zoom out, fit the map, and the key (?)**, at the map's top right.
- **M15 Sizes** (beside Undo; 2026-10-17): the size ruler at the map's zoom, two rows (2026-10-18): states (Rouental's,
  Cardonia's, Zukchiva's) and provinces (dense, usual as Cardonia's, sparse), and how big the nation's own are now.
- **M16 Suggestions** (beside Sizes, when the nation has any; 2026-10-18): hides what was drawn with Suggest, so the
  provinces under it show, and shows it again; the Suggest tool and **Show** (MP2) bring it back.
- **M13 The key:** what the colours mean in each view.
- **M14 The parts boxes** (lower right): the mainland, each piece overseas, and the World map (the whole world, for
  suggestions).

## State tab (open)

With no state picked, every state is a button (● for the named ones).

- **ST1 Name.** The map's own name in grey; whether it was named on the map or here.
- **ST2 What it is:** its number, provinces, size, coast, capital.
- **ST3 Population.** *Game:* the state's population, its manpower.
- **ST4 Kind of state:** wasteland to megalopolis, which sets its factory slots; a bar of the slots used, a warning
  when over. *Game:* the state's category.
- **ST5 Buildings:** infrastructure (0–5), civilian and military factories (0–20), dockyards (coast), air base
  (0–10), anti-air (0–5), naval base (coast, 0–10). *Game:* the state's buildings, factories cut to the slots.
- **ST6 Resources:** oil, steel, aluminium, rubber, tungsten, chromium.
- **ST7 Terrain:** how many provinces of each; a button per terrain sets every province of the state.
- **ST8 Selected province:** its terrain and size; **Make a supply hub** / **Remove supply hub**.
- **ST9 Its cities:** each (★ capital, ◆ state capital, its victory points) opens it on the Cities tab.
- **ST10 Notes.**
- **ST11 Reset this state to the map's values.**

## Cities tab (open)

- **CI1 What cities do:** the capitals, and victory points (how much a place matters) apart from size.
- **CI2 Each city:** name; **victory points** (1 minor, 3 local, 5 regional, 10 important, 15, 20 major, 25, 30
  great, 40, 50 foremost); **size** (village, town, city, large city, metropolis); **★ Capital** (at least 10
  victory points); **◆ State capital** (unmarked, a state's is the city with the most victory points); **Show**;
  **Delete**; its state and pixel; "needs a name" or "not on your land". *Game:* a victory point of that value under
  its name; the capital city's state is the capital; a state's capital is its first victory point, its supply hub
  and where its troops start. Size counts only when a total population is spread (NA7).
- **CI3 A warning** when two cities share a name.

## Map tab

- **MP1** **owner**: **Open them now** / **Close them again**, this nation's map tools (as O4).
- **MP2 Suggestions.** Each one: its kind, "What is it?", how big it is against Cardonia's states (2026-10-18) and how
  many provinces it would hold (an area or a state: Cardonia's size, sparse and dense; 2026-10-17), **Show**, **Make
  it a state** (an area, closed only), **Delete**, and more about it.
- **MP7 How big is a state?** (2026-10-18): the state size guide, folded until opened, above MP6.
- **MP6 How big is a province?** (2026-10-17): the province size guide, folded until opened.
- **MP3 Rivers you drew**, **open**: each one's size (major, minor, erase stroke), points and length, **Show**,
  **Delete**.
- **MP4 Railways**, **open**: each one's level, a warning where it crosses water, **Show**, **Delete**.
- **MP5 Supply hubs**, **open**: each by its state; a click shows it.

## Politics tab

- **PO1 Ruling sub-ideology:** the nation starts under its ideology. Not for the nations whose leaders are your own
  characters (Rouental, Merlovich): a note there points to the People tab. *Game:* the government and its
  sub-ideology.
- **PO2 Missing a sub-ideology? Ask for one:** to the request form (NA5).
- **PO3 Names and titles:** name, adjective and full title under every government, and under each of the five
  ideologies apart; the one ruling at the start is marked; empty fields keep the grey default. *Game:* the names.

## People tab

- **PE1 Head of state.**
  - Most nations: name, titles (shown on the portrait in game), portrait (the game's, when it is one of ours; a
    base-game one is a box saying so), traits, **Ask for a new trait**, and a line saying who rules in the game now.
  - The nations of your own characters: a card per ruler (PE3).
- **PE2 The other parties.**
  - Most nations: for each ideology but the ruling one, a sub-ideology (it gives the party a set leader), and the
    leader's name, portrait and traits.
  - The nations of your own characters: a card per party leader (PE3), the generated ones too.
- **PE3 A character already in the game** (Roland, Serelle, Mahaut, the Merlovichs …): name; name once ruling
  (Serelle VI); titles; sub-ideology, within its ideology (your own characters: the focus tree names the ideology);
  traits; for a general or admiral, rank (general or field marshal), skill and stats, and a commander's traits;
  portrait; **Back to the game's**. A change to Serelle or Mahaut reaches her copy at the head of HMMLA or Brillagne.
- **PE4 Political advisors.** **Add a political advisor**; each: name, portrait, traits (a political advisor's),
  **Ask for a new trait**, notes, **Delete**. *Game:* the politics screen's political advisors.
- **PE5 Generals, admirals and other advisors.** The game's own commanders without a party (PE3), then the site's:
  **Add a character**; each: role (general, admiral, advisor, other), an advisor's post (theorist, chief of the
  army, navy or air force, high command, political advisor), name, portrait, traits of their kind, a general's rank,
  a commander's skill and stats (a general's skill, attack, defence, planning and logistics; an admiral's skill,
  attack, defence, manoeuvre and coordination), **Ask for a new trait**, notes, **Delete**. *Game:* commanders from
  the start and advisors in their post; "other" is a note for you.
- **PE6 Companies.** **Add a company**; each: kind (28 kinds of arms maker in four groups, 14 kinds of industrial
  concern), name, logo, what it is in the game, notes, **Delete**; **Ask for a new kind of company**. *Game:* a
  military-industrial organisation (a designer without the DLC), or an industrial concern.
- **PE7 Portraits** are cropped to 156 × 210 from the top (a note).
- **PE8 What a trait does** (every trait list in PE1 to PE5; 2026-10-18): each chosen trait's effects under its chip
  ("Brave: Organization loss when below 25%: −10%; Defense: +1"), and **What each trait does**, folded: every trait of
  that list with its effects and **Add**.

## Releasables tab

- **RL1 Releasables**, the nation's own, made here: **Add a releasable**; each card: map colour; name; **Pick** (for
  the Releasables tool, M7); adjective; ruling sub-ideology; full title; land (**Pick its states** / **Change its
  states**, or closed **Draw its land**; **Show**; ✕ on a drawn area); flag (**Send a picture**, **Replace**,
  **Remove**); ruler (portrait, name, titles, traits); about it; **Delete this releasable**. *Game:* a country with
  cores on its states, released from the diplomacy screen.
- **RL2 In the game:** the releasables the mod has (Rouental's 13, Belekria's Tethia), each a card like RL1's with
  the game's values in grey: a badge, what it is, names, government, map colour, land (open: **Change its states**;
  **Show**; **Back to the game's land**), flag (the game's, or yours: **Back to the game's**), ruler (for one of your
  characters, a pointer to the People tab instead), about it, **Undo every change to it**.
- **RL3 In the civil war:** the seven that rise against Rouental, the same cards, saying when they rise (and which
  exist only through the war).

## Nation tab

- **NA1 The nation:** flag, name, tag, continent, states, provinces.
- **NA2 Status:** In progress / Finished; who filled it in; on the site, the player's own name.
- **NA3 Flags:** the main flag and one per government, each showing the game's until a picture is sent: **Send a
  picture**, **Replace**, **Remove**.
- **NA4 About the nation:** map colour (**Use the map's**), culture, motto, anthem, description.
- **NA5 Requests to the author:** kind (a new sub-ideology, trait or kind of company, a subject type, a map change,
  something else), the request and its details, **Send request**; the list, with its status and your reply;
  **Delete** for one's own.
- **NA6 So far**, **open**: states named, population set, provinces with terrain, cities, capital, rivers,
  railways, total population.
- **NA7 Spread a total population**, **open**: a total shared among the states by their size and their cities'
  sizes, a preview, **Apply to every state**.
- **NA8 Notes for the author.**
- **NA9 Files:** **Save a file** (this nation's facts), **Load a file** (adds a file's facts).
- **NA10 Clear everything entered for this nation.** (Above it, a note when saved facts no longer land on the
  nation's map.)

## Without a button

- Each change goes to the atlas within a second; offline, it waits on the device and goes once the page reaches the
  atlas again.
- Facts are kept by map pixel, so they survive new borders and provinces; those that land on another nation are
  counted on the Nation tab.
- Pictures are kept at up to 640 px.
- Phone and desktop, light and dark.

## In more than one place now

Where one thing can be done from two places, or is split over two tabs:

- Terrain: the Terrain tool (M2) and the State tab's buttons (ST7).
- Supply hubs: the Hubs tool (M6), the State tab (ST8) and the Map tab's list (MP5).
- Cities: placed and moved on the map (M3), filled in on the Cities tab (CI2), listed by state (ST9).
- The government: the ruling sub-ideology on Politics (PO1); the parties' sub-ideologies and every leader on People
  (PE1, PE2).
- The nation's look: names on Politics (PO3), flags and colour on the Nation tab (NA3, NA4); a releasable has all of
  it on its card.
- Releasables' land: the Releasables tool (M7) and the cards' buttons (RL1–RL3), which switch to the tool.
- Requests: the Nation tab's form (NA5), **Ask for a new trait** under each leader (PE1, PE4, PE5), **Ask for a new
  kind of company** (PE6) and PO2.
- Suggestions: drawn with Suggest (M8), described on the Map tab (MP2), gathered in Owner tools (O6).
- Map tools: Owner tools (O4) and the nation's Map tab (MP1).
