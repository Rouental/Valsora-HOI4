# The Deco UI in the Valsora mod: versions and what was seen in game

Moved out of the root `CLAUDE.md` word for word on 2026-10-17 (it keeps the essentials). `deco_ui/CLAUDE.md` is the interface's full manual; this is what each version did and what the author saw of it.

## Deco UI (`deco_ui/`): part of the mod

**The Valsora Deco UI** is the author's art deco interface, made with another Claude session (v0.1–v0.4.4)
and moved here on 2026-10-14 (v0.4.5–v0.4.8 the same day: the politics screen flush under the top bar,
styled tooltips). **Since v0.5 (2026-10-14, later) it is part of the Valsora mod** (author: "roll the UI mod
into the main Valsora mod, but with the knowledge that I might eventually want it taken out again ... I'd like
to simplify things to only have the one install"): a restyled top bar, every side panel (the politics screen
re-laid to its mockup; 16 others flush under the top bar with a notch for the flag medallion and a deco header,
v0.5), the state panel, focus tree, map modes and minimap (v0.5), main menu (the Valsora background) and a core
skin. `deco_ui/CLAUDE.md` is its full handoff guide (engine facts, generators, what is confirmed in game); read
it before touching the UI. In short:
- **One switch:** `DECO_UI` in `scripts/common.py`. True: `scripts/deco_ui.py` (after `build_mod.py`)
  copies `deco_ui/valsora_deco_ui/` into the build, and `minimap.py` draws the minimap in its style. False:
  the game's own interface (`build_mod.py` empties the build first, so nothing of the Deco UI is left).
- The build makes the Deco UI's Valsora-dependent files itself, so they can't go stale: the long-name trigger
  (`deco_ui/tools/long_names.py`: names too long for the medallion's large font) and the politics screen
  (`make_politics.py`, from Valsora's own `countrypoliticsview.gui`, kept in `work/deco_base/`; its
  sub-ideologies are those Valsora names, 39). The only file both ship is that one (`deco_ui.REPLACES`).
- Everything else (textures, fonts, the game screens it patches) is built by hand with the game's files at
  hand: `CHROMIUM_PATH=/opt/pw-browsers/chromium python3 tools/build_all.py` in `deco_ui/`, after the
  vanilla links its section 3 lists (`deco_ui/reference/valsora` is `build/valsora_test`); then rebuild
  Valsora. `validate_preview.py` must end with `PROBLEMS: none`. `gen_textures.py` redraws only the textures whose
  drawing changed (`--all` redraws all); after a redraw, `python3 tools/restore_noise.py` puts back those that changed
  only by anti-aliasing noise.
- `check_mod.py` checks the merged mod: the Deco UI's localisation in the game's 9 languages (only its files
  may be other than English), its politics screen's five 19 px party rows, every kind of sprite in a .gfx, and
  sprites the game's own .gui files name without defining (`source/vanilla/index/gui_undefined_sprites.txt`).
  A game sprite (`source/vanilla/index/sprites.txt`) in a game .gfx the Deco UI ships patched (`nationalfocusview.gfx`)
  may point at the game's own texture; a texture in a folder of ours (`valsora…`, `VAL/`) must be shipped
  (mutation-tested). Every letter of the mod's English text and name lists must be in every font in `gfx/fonts`
  (2026-10-16: Plaija's Vietnamese names; the fonts have Vietnamese since, composed where a face lacks it; the factory
  diamond, U+25C6, only in the value fonts that draw it; mutation-tested).
- There is no separate release any more (`dist/valsora_deco_ui.zip` was removed). The author was told to delete
  the old `mod/valsora_deco_ui/` and `mod/valsora_deco_ui.mod` and take it out of the playset: left in, it
  loads after Valsora and puts its older files back.
- Its `reference/` (the game's files, git-ignored) must never be committed: it is Paradox's content.
- **v0.6 and v0.7** (2026-10-15, not yet seen in game): the focus tree after its mockup (v0.6; the focus icons are
  the game's, as the author asked); the army bar (`make_leadergroups.py`, textures `lg_*`, numbers in
  `layout_armybar.py`) and the events (`make_events.py`, textures `ev_*`) in the deco style at the game's paths and
  sizes (v0.7). Their previews, `deco_ui/build/preview_armybar.png` and `preview_events.png`, show the game's art
  beside ours, so they stay in the git-ignored `build/` and are only sent to the author.
- **v0.8** (2026-10-15, the second night, not yet seen in game): **the game's own fonts** redrawn in the deco faces at
  their paths (`deco_ui/tools/game_fonts.py`, 28 fonts: tooltips, lists, the designer, leader and unit screens,
  settings, window titles; the author: "could you switch to the art deco fonts throughout the UI? for example,
  currently the title of Roland is displayed in the base game's font"), a size or two under the game's so its text
  keeps fitting the game's boxes; the army bar's play / stop row centred over each general; event options centred
  between the picture and the card's edge; a gilt Valsoran globe in the middle of WORLD NEWS. A mockup of **larger
  flags** is in `deco_ui/art/proposals/hd_flags/`, **not in the mod** (author: "Maybe do a mockup of how it could look,
  but don't add anything to do with it into the mod yet"): it needs the seven flags we have only at 82 x 52.
- **v0.8.1** (2026-10-15, later): the news masthead is **VALSORAN (globe) STANDARD** (the author: WORLD NEWS "still looks
  lopsided ... maybe swap to something like "Valsoran Standard" or Clarion or Dispatch ... so both words are the same
  length"), the globe redrawn to read at 60 px, and the news page centred under it. Other names:
  `deco_ui/art/proposals/news_masthead/`. The author kept it (2026-10-15).
- **v0.8.2** (2026-10-15, the third round, from the author's screenshots of v0.8.1): the superevent shows one title
  and Valsora rising in its crest; the event cards' crest is a stepped keystone (`deco_ui/tools/crests.py`); a long
  option's three lines fit (`valsora_deco_option_14`); a name of two lines shows both under the flag
  (`layout.NAME_SLACK`); the selected armies' badges, the air wings and the operatives start below the medallion
  (`make_mapviews.py`); the news globe is lit. Options for the globe and the crests: `deco_ui/art/proposals/news_globe/`
  and `crests/`. The larger flags' test version is drawn from the same tools (`VALSORA_FLAG_SCALE`).
- **v0.9** (2026-10-16, the night, not yet seen in game; the author: "do 1 (though be prepared to possibly revert
  it,)"): the research trees and the doctrine screen under the focus tree's notched header (`make_research.py`; the
  research file is Valsora's, made again by `scripts/deco_ui.py`, REPLACES), the designers' and commander pickers'
  pictures (`designer_art.py`), the faction's members' flags on the politics screen, the hot-join window below the
  medallion, and `medallion_check.py` (a window under the medallion fails the Deco UI's build). The restyled screens
  are one commit, `8dece16`: `git revert 8dece16` and a rebuild of both take them out. The focus in progress in the
  focus tree's header, a bar under a focus and a one-spirit card have no hook in the game (`deco_ui/CLAUDE.md` section
  12). **Four loading screens** from Valsora's map were drawn as a proposal (`deco_ui/art/proposals/loading_screens/`:
  "don't add them yet"); they were in the mod in v0.10 only (out again in v0.10.1, kept for later).
- **v0.10** (2026-10-17, not yet seen in game; the author: "Please start applying the proposed changes to all the UI
  screens"): every suggestion of `deco_ui/docs/SCREEN_INVENTORY.md` and more, as pictures at the game's paths and sizes
  with its layouts kept: the loading screens (`deco_ui/tools/make_loading.py`, in the background list after the menu's
  picture) and a gilt loading bar; scroll bars and sliders; the selected armies', fleets' and operatives' badges; the
  battle plan toolbar; the land and naval battles; the diplomatic action windows, a gilt line emblem per action; game
  setup; the window frames and popup headers the core skin had missed; the settings, the trade offer and other windows
  seen now and then. One art module per screen (`deco_ui/tools/*_art.py`, `ART_MODULES`), each with a preview beside
  the game's (only sent: the game's art).
- **v0.10.1** (2026-10-17, later, not yet seen in game; from the author's screenshots of v0.10): the loading pictures
  out of the mod again until the map is final (the author: "The globe map should be kept for later ... the map's not
  finalized quite yet"; the loading screen showed the game's own pictures anyway, and game setup had taken the last of
  ours as its background), kept by `make_loading.py` (into `deco_ui/build/`, `--into-mod` to put them back); no corner
  brackets on the loading boxes and the battle plan bar, its icons centred; game setup a card wider for "Other
  countries", its details tidied and the ideology wheel as on the politics screen (`make_setup.py`); the logistics
  values a size smaller; the decision counts beside the seal; the division designer's combat width and the commanders'
  skill centred (the game rounds centred text up, measured on the screenshots); the fleet panel's long names fit; the
  news story a size smaller so it ends above the page's rule.
- **v0.10.2** (2026-10-18, not yet seen in game; from the author's screenshots of v0.10.1 and a mockup): the flag
  medallion after the author's mockup ("a rough mockup of how I'd like the flag box to look"): a gilt rim on the flag,
  a gilt line round its mat and two stepped gilt brackets at each corner (`layout.FLAG_MARGIN`, `FRAME_LINE`,
  `FRAME_STEPS`), the corner diamonds gone; the name 1 px right ("it looks like the name isn't centered?": the game
  centres a line on its advances, the last letter's tracking included; `layout.NAME_SHIFT`); the experience badges
  centred at the foot of the army, navy and air buttons, their numbers centred ("The xp bars should be at the bottom
  center ... The xp number should be centered in the box"; the digits' y measured on the screenshot); the factories
  military, naval, civilian ("to match the order in the list"); the faction card's flags eleven a row ("room for a few
  more in each row"); the state panel's flag and name clear of its corner bracket ("the decorative corner in the top
  left is covered by the flag"); the country and leader events without corner brackets ("The corners of this look
  weird. It seems like you have a lot of trouble with this particular decorative element": one big bracket in one
  corner, two small ones at the foot, none under the back button; the double chamfered frame is the corner now); the
  Release Nation window's list of states scrolling above its checkboxes (`make_popups.py`, the game's
  `popupwindow.gui` with one change: "This screen overflows"); the state panel's resistance and compliance in two rows
  inside the claims band, their bars the panel's gilt wells, amber to coral and jade ("Compliance and resistance look
  out of place": the second row ran over the State Modifiers rule, the bars the game's).
- **v0.10.3** (2026-10-18, later, not yet seen in game; the author's screenshot of v0.10.2: "The notification is still
  a dot, rather than the shape I specified"): the decision counts on plates of their own, each the shape of its
  shoulder of the medallion (the author's red outline of 2026-10-17: the shoulder from the plate's edge to the step,
  its corner by the seal cut off), in the game's four colours, the number centred on it (`layout.DEC_PLATE`,
  `DEC_CUT`; sprites `GFX_valsora_deco_dec_count_left` / `_right`; v0.10.1 had only moved the game's round badge into
  the shoulder). The game's shared `topbar_alert_bg` stays the round badge for the intelligence agency's, the
  prototypes', the trade contracts' and the officer corps' counts.
- **v0.10.4** (2026-10-18, evening, not yet seen in game; the author: "continuing to stylized the other screens in Deco
  style. One specific one is the diplomacy screen ... Yep, redraw the pictures. One thing I'd definitely like in
  particular is to have the leader portrait stylized the same way others are"): the diplomacy panel's own pictures at
  the game's paths and sizes (`diplomacy_art.py`, `dv_`): the leader's frame an arched opening in a chamfered gilt
  plate (as the leader events' and the army bar's; the plate ends where the politics block covers the game's frame),
  the flag's frame as the medallion's, the politics block (a gilt socket for the pie, wells for the texts, a fan where
  the game had its laurel and flags), the pie's ring, the national focus button's three frames, its progress frame, the
  national spirits band with its label's tab, the header strip, the country list's binding, the unity and text wells,
  the short window header. The filter strip and the opinion box stay the game's: its icons are painted into them.
- **v0.11** (2026-10-18, night, not yet seen in game; the author's findings in v0.10.2 to v0.10.4 and their go-ahead):
  - the top bar: military factories green, civilian orange, naval still blue ("military factories should be green,
    civilians should be orange"); the decision plates 2 px taller, their tops on the gilt rule of the step ("Their tops
    should be level with the rest of the bar ... Their bottoms should remain anchored": `layout.DEC_RAISE`); the
    logistics cell's values 2 px higher and their bars 3 ("Logistics numbers are running into each other": in game the
    values sat 2 px lower than planned, 1 px under the bar above); the music button the tray's left end, its full
    height, in a double gilt frame with its lower left corner cut and hatched (the author's mockup; the tray's step is
    gone: `layout.PLAYLIST`, `RTRAY_CUT`, `gen_textures.music_button`);
  - the diplomacy and intel tabs (their shared header and the diplomacy tab's leader block, `diplomacy_art.py`,
    `layout_panels.DIPLO`): the flag's frame the bar's 71 px tall and level with it, from the tabs' left edge ("the bar
    with ideology, stability, names, etc. should be level with the flag"); the names stop at the opinion box, a long one
    cut with "..." ("the leader's name can run off the screen"); the portrait as the politics screen's (its arch, rims,
    diamond and sunburst), flatter, the portrait at 0.66 so a square one fits whole ("larger portraits like Krionik's
    start to get cut off"); the pie a donut in a gilt ring as the politics screen's (`pol_piechart_overlay`, also the
    faction and setup screens'); the left column's wells centred on the pie and the focus icon, the icon in an octagon
    ("Focus icon isn't centered"); the focus button's fan gone for stepped corners and gilt diamonds ("a repeat of the
    election box is boring");
  - the side panels' own pictures, the drafts of 2026-10-18 (`make_panel_pictures.py`: the translated ones and v0.7's
    hand-drawn ones; "All the other stylization looks good, I'd like you to add them to the mod"), less the army, navy
    and air overview's and the intelligence agency's ("Keep the art for navy, army, air, and intelligence tabs, at least
    for this pass"); the research picture's box with equal margins in what the panel shows (538 of its 548 px) and the
    atom and circuits centred in it ("better centered and aligned to the box it's in");
  - the decisions tab (`decisions_art.py`, `dc_`: "Stylize the decisions tab as well"): the events box a lacquer plate
    with the title's tab, the category header with a round socket for its medallion and a well for its name, the
    decision rows (grey, jade, steel), the event rows, the status lights as diamonds, the checkboxes, the fold button,
    the description's tile; the events box's title and rows in the Deco UI's light faces (they were typewriter ink on
    paper: `layout_panels.DECISION_FONTS`, `make_panels` `toplevel_attrs`). The envelopes, timer and event-type strips
    stay the game's (icons);
  - the focus tree's filter icons centred in their octagons (the game's 27 px icons at its (8, 7) sat 3 px right and
    3 px low in ours: `layout_focus.FILTER_ICON`).
  Proposals, not in the mod: the game's icons redrawn in the Deco style (`proposals_icons.py`, `art/proposals/icons/`:
  the resources, the focus filters, the production screen's icons and add-a-line buttons, the decisions' envelopes;
  the author: "make an attempt at recreating them as close as possible, but in the Deco aesthetic").
- **Proposals for the side panels' own pictures** (research, production, the market, the overview strip, the
  intelligence agency, the spirit banners) were in `deco_ui/art/proposals/panel_pictures/`; all but the overview strip
  and the agency's went in with v0.11.

- **v0.11.1** (2026-10-19, not yet seen in game; the author's screenshots of v0.11: "Please also style the music
  controlller and the music player to better match the ui, and in the case of the controller popup, make it fit in
  better as currently it just kinda pops in our of nowhere. Trade screen has off artifacts and lines. The production
  screen doesn't have any boxes"):
  - the music player (`music_art.py`, `mu_`; `make_music.py` for `musicplayer.gui`): the faceplate a lacquer plate
    with the track's well and a gilt loudspeaker in a sunburst either side (the game's megaphones), the control rail
    under it, the buttons chamfered plates with gilt glyphs (previous, play / pause, next, the station's music, shuffle
    and shuffle off), the volume's gilt fill, the station box a lacquer plate with the top bar's note and its title in
    gilt capitals; the track list keeps its ivory sheet (the typewriter text is dark), its rules and margin bronze, the
    playing track's pointer jade, a disabled track's line oxblood. Preview `build/preview_music.png` (+ `_vanilla`);
  - the controller (`toggle_music_commands_win`): a tab hanging from the tray under the music button
    (`music_art.TAB`), sliding down from behind the tray (the game slid its strip in from the right, out of nothing),
    its three buttons as the player's;
  - the production lines and the trade rows (`production_art.py`, `pl_`): drawn by hand from the game's measured
    layout instead of `make_panel_pictures.py`'s automatic translation, which had lost the line's boxes (the
    equipment's plate, the factory slots, the resource wells) and turned the game's scratches into gilt specks along
    the trade rows (`make_panel_pictures.DRAWN`).

- **v0.11.2** (2026-10-19, later, not yet seen in game; the author's screenshots of v0.11.1 and the notes they had held
  with v0.11, "Do not act on the following yet", now acted on):
  - **the game's icons in the Deco style, in the mod** (the author: "You haven't changed the icons yet, but maybe I
    forgot to approve that"): `icons_art.py` (`ic_`) draws `proposals_icons.py`'s fifteen at the game's paths: the
    resources strip, the focus tree's three filters, the production screen's factory, dockyard (and with its wrench),
    efficiency (and its cap) and bombing defence icons, its four add-a-line buttons, the decisions' envelopes;
  - the diplomacy tab's portrait as the politics screen's (the author: "The diplomacy view is about the same as last
    time"): the portrait at 0.72 filling a round-headed arch, its top corners under the lacquer, the sunburst on it
    (`diplomacy_art.LEADER`; v0.11 had it at 0.66 under a flatter arch with an empty cap above); the actions list's
    empty header strip hidden ("an odd and seemingly useless cut off bar visible if you scroll all the way up");
  - the loading bar's diamond whole ("Half of the diamond on the top bar in the loading screen is cut off"): the
    status plate's foot at y 84, the diamond smaller, the progress track 4 px higher (`gen_textures.ld_status`);
  - the decision count plates 1 px lower ("a little too high": `layout.DEC_RAISE` 1);
  - the production screen's resource strip under all seven cells, the cog medallions gone ("resource counts go past
    the bar": `proposals_panels.production`, the hand-drawn header);
  - the decisions' and events' icon wells centred on their icons ("Icons on the events & decisions are out of
    alignment with their boxes": `decisions_art.DECISION_WELL`, `EVENT_WELL`).
  Not changed: the `error.log`'s "Token theocracy is a dynamic token" (the politics screen's popularity of the
  Theocratic party, `[?party_popularity_100@theocracy|0]`: the game knows its own four ideologies' tokens, not ours;
  a multiplayer desync warning, harmless in single player, and no way is known to declare the token); the faction
  screen ("Odd appearance of faction screen"): asked what looks odd.

- **Held: the author's notes on v0.11.2** (2026-10-19, evening, with screenshots; "do not fix these or anything else I
  send until I give you the go-ahead"). Nothing done yet:
  - the loading screen: the upper diamond (on the status plate's foot) looks odd beside the lower one (the tip's); both
    should look the same;
  - the diplomacy tab: the round-headed portrait suits it less than the politics screen; its rays stop suddenly at the
    plate's edge, where the politics screen's run on and fade out; the bottoms of the Diplomacy and Intel Ledger tab
    buttons are cut off; perhaps a gilt octagon frame instead;
  - the new military factory, civilian factory and dockyard icons everywhere the game shows those (the production
    units, the dropdown under the factory side, the resource deficit icons still the game's); the build aircraft button
    as the air tab's jet; the build infantry & artillery button a helmet and a howitzer, not a rifle;
  - the construction screen: icons running into their headers; restyle its buttons as subtle octagons and its icons
    about 1 to 1 in the Deco palette;
  - the alerts: only across half the screen (they wrap after 11 in the screenshot); they should run to the music tray
    before wrapping; their frames in the Deco style (gilt octagons), the icons kept and centred.

## From the root manual's "Current state" (2026-10-17)

Where things stand; the history, date by date, is `docs/HISTORY.md` (add each day's entry at its top).

- **The build** (2026-10-17, the night): 20,940 provinces (20,552 land, 363 sea, 25 lakes), 61,767 province borders
  (HOI4 draws 65,536: `docs/BORDER_LIMIT.md`), 3,190 states, 179 strategic regions (137 land, made from the nations on
  2026-10-16: `land_regions.py`, not redone for the 2026-10-17 borders; 42 sea); 416 strait crossings; 193 countries
  in the mod, 160 of them on the map, 94 of those with a flag of their own (66 fly a stripe in their map colour); the
  states of 48 are the author's own lines (`gazetteer.finals`; 39 until 2026-10-17's map: Belekria, Krionik, Terreich,
  Gorbastan, Zukchiva, Sennheiser, Sminishia, West Sminishia and Hollier joined). The four great powers, one per
  ideology but Theocratic (author, 2026-10-17): Krionik (Monarchist), Kampf (Authoritarian), Sarkis (Communist),
  Fraxhemark (Democratic); great in name for now (their industry is as drawn). Two starts, both on 1 January 2036. The Deco UI is v0.10.1 (the
  author's findings on v0.10: loading pictures out until the map is final, game setup's ninth card, the battle plan
  bar, the decision counts beside the seal, the combat width and commanders' skill centred, the fleet's names, the news
  story), after v0.10 (the scroll bars, the selected units' badges, the battle plan toolbar, the battles,
  the diplomatic actions, game setup and the popups in the deco style: `deco_ui/docs/SCREEN_INVENTORY.md` counts 34
  screens restyled, 45 re-skinned, 16 still the game's), after v0.9.1 (the map's names back, the
  designers' statistics dark, the doctrine tabs clear of the name, fuel, supply and convoys in the top bar's strip and
  the alerts across to the right-hand tray, the production alert a ring round its crown), after v0.9 (the research
  trees and doctrines under a notched header, the designers' and commander pickers' pictures, the faction's members'
  flags, a check for windows under the medallion) and v0.8.4 (the focus tree's title in its header, the count
  badges and fold arrows, Vietnamese letters in every font, the small letters for names of two lines, the navy's panel
  below the medallion). The Gazetteer shows players a quick-start guide the first time they unlock a nation.
  Rouental has test decisions for every kind of event and a test superevent (`test_events.py`).
  **A blank slate** (author, 2026-10-16: "is there a way you could reset any edits made thus far? I'd like a blank
  slate. The same goes for the mod. I'd like it just as it was on the last pdn, no extra rivers or internal borders"):
  the mod is built from the `.pdn` alone, with no Gazetteer facts (`source/gazetteer/` removed: Rouental's page, its
  river, railway, terrain, cities, admiral and "Test" releasable with its flag), and Owner tools › **Start over**
  would clear the site's atlas (the author's alone, asked twice; they decided not to, 2026-10-16: "I think I'll
  actually not reset it"). The Gazetteer offers the base game's traits for every leader and takes requests for new ones,
  and has political advisors and companies (arms makers and industrial concerns of the base game's kinds, with logos;
  requests for new kinds); since 2026-10-15 (later) it shows what the game already has, editable (the author's own
  characters with their stats; Rouental's 13 releasables, its civil war's 7 risers and Belekria's Tethia), commanders'
  skill and stats, and cities' size apart from their victory points (now labelled by importance). The test version with 1.5 times larger flags is built beside the mod by
  `sh scripts/build_flags15.sh` and sent as its own zip (`docs/HD_FLAGS_TEST.md`), not put into the mod.
- **Seen in game last** (2026-10-17): the Deco UI v0.10 (the author's screenshots): the logistics "as part of the main
  bar" and the commanders' card's look liked; the loading screen showed the game's own picture, corner brackets stuck
  out of the loading boxes and the battle plan bar, its icons off centre, "Other countries" off the edge of game
  setup, its details disorganised, the combat width and the commanders' skill off centre (white on tan), the fleet's
  names running over, a news story over its rule: all fixed in v0.10.1, not yet seen. Before that (2026-10-16, later):
  the Deco UI v0.9 (the author's screenshots and `error.log`): the
  research and doctrine screens "mostly look good" and the faction's flags "look amazing"; no names on the map (the
  map font's texture too large for the game), the designers' statistics white on the ivory sheet, the doctrine tabs
  into the name under the flag, a long faction name cut off, the LEADER tag off centre, the seal's badges unequally
  far, the music button against the right-hand tray's edge and "an odd green bar" (the production alert's halo) between
  Construction and Production: all fixed in v0.9.1, not yet seen. The log's last two lines ("Invalid effect 'TAG'",
  file "") came from the console, not the mod. Before that (2026-10-16): the Deco UI v0.8.3 (the author's screenshots and `error.log`): the army bar
  looked good but for the empty cards' plus, off their chest; the decision counts were the game's round badges; the
  focus tree's title and subtitle sat on its first row of focuses, the map showed faintly through its header, and its
  shortcuts arrow was the game's copper one; the captured commanders' two tabs overlapped; one log line was ours (the
  tooltip font's base against the game's Cyrillic file); later screenshots: long names (the Kampfian Empire) against
  the flag's frame, the navy's panel under the medallion, and Plaija's Vietnamese names missing letters. All fixed in
  v0.8.4, not yet seen. The log's other lines are
  the game's own (two Workshop mods, missing Italian and German tank models, SCO's and CSA's flags). Not seen yet
  besides: the two starts, Vilna and Placeholdgrad. The Deco UI's checklist for the author is in
  `deco_ui/valsora_deco_ui/README.txt` (Things to check) and `deco_ui/CLAUDE.md` (section 10).
- **Waiting on the author:** from the 2026-10-17 map: names for the new states (`dist/state_numbers_belekria.png`,
  `_krionik`, `_terreich`, `_kurikia`, `_san_sierra`, `_sennheiser`, `_gorbastan_zukchiva`, and Cardonia's 5 and
  Hollier's 1 new ones), flags for Belekria's eight new republics, and the bump of Kieska's new land by Sombor that is
  painted as Crvenognjište (Kieska's, with a Crvenognjište core: `docs/NATIONS.md`); names for the 137 land strategic regions (`dist/region_names.md`, renumbered for the
  new regions; a first draft of every name, Claude's, is `dist/region_names_draft.md`, 2026-10-17); the wider strait crossings
  (`dist/straits_map.png`: the orange and red ones, 10-20 px; the 414 green and yellow ones are in the mod since 2026-10-17;
  `straits.py approve --max-gap 10 --add N,...`, then a rebuild);
  what the Deco UI restyles after v0.10 (`deco_ui/docs/SCREEN_INVENTORY.md`'s suggestions: the unit counters, the division
  and ship details, the trait trees ...); whether fuel, supply and convoys stay in the top bar's strip (an experiment, the author's); whether v0.9's restyled screens stay; the larger flags' test version (`docs/HD_FLAGS_TEST.md`); the panel picture proposals (on
  hold, the author: "I don't want to move ahead with the panel pictures just yet"); the tech tree (its eight questions
  answered on 2026-10-16 and recorded in `docs/TECH_TREE_2036.md`: a realistic 2036, the tree beginning where the base
  game's ends, nuclear weapons for the superpowers only, Krionik, Kampf and Fraxhemark or Sarkis as the superpowers;
  the author is still brainstorming and will say more about the tree's shape, so nothing is built until then); the other
  size options
  (`docs/SPEED_AND_SIZE.md`). Settled (2026-10-15): the news
  masthead stays VALSORAN STANDARD, its globe the ringed one, the event cards' crest the keystone; the zip stays in
  `dist/` (Decisions worth keeping, "The mod's zip").
