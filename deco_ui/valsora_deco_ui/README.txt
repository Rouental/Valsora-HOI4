VALSORA DECO UI - v0.7 (for HOI4 1.19)
======================================

An art deco interface for the Valsora total conversion: core skin, a rebuilt
top bar, the politics screen, every side panel, the province panel, the
focus tree, the army bar, the events, the map modes and minimap, and the main
menu, laid out like the Valsora mockups.


INSTALL
-------
Since v0.5 the Deco UI is part of the Valsora mod itself: install Valsora
(dist/valsora_test.zip) and you have it. There is no separate Deco UI mod
any more.
1. Delete the old one, if you have it: mod/valsora_deco_ui/ and
   mod/valsora_deco_ui.mod in Documents/Paradox Interactive/Hearts of Iron IV/,
   and take "Valsora Deco UI" out of your playset. Left in, it would load
   after Valsora and put its older files back over the new ones.
2. Install Valsora as usual (delete mod/valsora_test/ and mod/valsora_test.mod,
   unzip dist/valsora_test.zip into mod/), launch with -debug.
If anything looks wrong, check
     Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log
for lines mentioning "valsora_deco", a .gui file, a texture or a font.

To go back to the game's own interface one day: set DECO_UI = False in the
Valsora repository's scripts/common.py and rebuild (sh scripts/run_all.sh).

The layout is built for 1920 px of UI width: 1920x1080 at 100% UI scale, or
2560x1440 at up to 133%.


NEW IN v0.7
-----------
  - The army bar along the bottom of the screen: each commander's portrait
    in a gilt arched frame on lacquer (jade when selected), the division
    count centred on a plaque, an army group's card with gilt fans, the
    plate behind them with a gilt rule, gilt play and coral stop buttons,
    a battle plan running as gilt chevrons on jade, and an empty card with
    a gilt bust and a plus when an army has no commander.
  - Events: country, leader and operative events are lacquer cards with a
    crest, gilt rails and a gilt frame round the picture; news events are a
    broadsheet with a WORLD NEWS masthead. Titles in gilt capitals, the text
    and options in cream (the game's typewriter fonts are dark, for paper).

Things to check in game (v0.7):
  - the army bar: a selected army, an army group with its armies (the plate
    should run on from the field marshal over his armies), a battle plan
    being prepared and executed, an army with no commander;
  - any event: the title, the text, the options (hover and click), the
    picture; a long event (the middle should stretch with the text); a
    news event.

NEW IN v0.6
-----------
  - The focus tree, after the mockup: it opens flush under the top bar with
    the flag medallion and decisions seal in a notch (it covered them), with
    the country's focus tree title and its full name and sub-ideology in the
    header, the filters, search, zoom and close on one row, a scale-pattern
    canvas in a gilt frame, and an octagon medallion and plate under every
    focus: grey when unavailable, jade when it can start, red with a gilt
    halo when in progress, gold with a check when completed. Gilt links,
    red marks between mutually exclusive focuses, a new legend. The focus
    icons are the game's, as before.
  - The superevent window is the mockup's (the Valsora mod draws it): the map
    veiled, a gilt frame and crest, the title between stepped hairlines, the
    picture framed with gilt fans, the quote in italics, the gilt button and
    the song in a tab below.
  - The date in the top bar has room for the widest date of 2036-2049
    ("00:00, 30 September, 2040"); its box was sized for 1936 and would
    have cut it short. The speed arrows sit 6 px further right.

Things to check in game:
  - the focus tree: the medallion and seal in the notch, no map between; the
    title and subtitle (if they are missing, tell me); a focus in each state;
    the links and the exclusive marks; the filters, search, zoom and close.
  - a superevent (the focus "Execute the Prince" on the communist path, or
    any of the five leadership focuses): the veil, the window, the song tab;
    the button and Esc close it.

NEW IN v0.5.2
-------------
  - v0.5.1 made closed side panels sit just below their place instead of
    off-screen, and the game kept drawing them there (the division overview
    over the map in your screenshot). Closed panels are off-screen again, and
    a panel now opens and closes at once, so nothing slides across the flag.
  - The main menu's career profile star sits on the button's corner instead
    of over its label.

NEW IN v0.5.1
-------------
  - Side panels, and the windows beside them, no longer slide in from the
    left across the flag and the country's name: they rise a little into
    place (and sink as they close), quickly, under the medallion. (Undone in
    v0.5.2: the game kept closed panels on screen.)


NEW IN v0.5
-----------
  - One install: the Deco UI is built into the Valsora mod (see INSTALL).
  - Every side panel now opens flush under the top bar like the country
    screen, with the same cut-out for the flag medallion and the decisions
    seal: army (division overview), construction, decisions, recruit &
    deploy, diplomacy, intelligence agency, logistics, occupied territories,
    officer corps, production, research, trade, faction, create faction,
    faction theaters and the international market. Each has a deco header:
    its title in gilt capitals right of the medallion, the close diamond,
    its own buttons beside it, a gilt rule, and the panel's body below.
    The panel's contents start below the seal (about 50 px lower on screen
    than the game's), so lists are a little shorter.
  - The windows that open beside a panel (equipment, lend-lease, templates,
    advisors, subjects, exiles ...) also open flush under the top bar.
  - The game's pictures used inside every panel are restyled: close
    buttons, background tiles, header bars, tabs (the lit one in jade),
    sort buttons, filters and checkboxes.
  - Map modes (lower right): a lacquer column with gilt edges; the land, air
    and naval buttons are octagonal medallions with the deco line icons,
    linked by a gilt thread (jade when selected); the small map modes and
    the toggles keep the game's icons, recoloured in gilt.
  - Minimap: gilt land and coastlines on dark lacquer with a faint graticule,
    in a gilt frame; deco handle and ping buttons. The start date's picture
    in single player follows.

NEW IN v0.4.8
-------------
The country (politics) screen, after your first screenshots of it:
  - It now opens flush under the top bar, with no gap. The game draws
    side panels over the top bar, so the panel leaves a cut-out the shape
    of the flag medallion and the decisions seal, and they show through it
    with a gilt edge round them. The two decision counters moved onto the
    medallion's lower step, either side of the seal, so the panel never
    covers them.
  - The leader's description (Roland II's titles) is no longer printed on
    the screen. It stays in the tooltip over the portrait.
  - Tooltips are styled at last (dark lacquer, gilt frame), everywhere in
    the game: the game was loading its own tooltip picture in place of this
    mod's (it looks for a .dds before the .tga this mod shipped).
  - The background behind the portrait, name and ruling party was the
    game's own picture: the game swaps that picture in while running, which
    hid this mod's. Both of the game's versions are now replaced.
  - The three law cards are gone (the laws are in the list below). Their
    place went to the national spirits, which moved up beside the
    popularity: two rows of large icons, then smaller ones, seven to a row,
    and a scroll bar beyond 28. The leader's sub-ideology (Feudalism,
    Khanate ...) is a new line under the political power, with its
    description in the tooltip; that row can also hold buttons for special
    mechanics later.
  - "Last election" says None for countries without elections.
  - Everything above moved up: the advisors and laws list at the bottom is
    156 px taller (about one and a half more rows at 1080p).

NEW IN v0.4.7
-------------
  - The country (politics) screen: in your screenshot it was Valsora's own
    screen with this mod's text scattered over it, because the Deco UI had
    loaded before Valsora. It now declares Valsora as a dependency, so it
    always loads after it and its own politics screen is used. This is the
    first time you will see that screen as designed: please send a
    screenshot of it.
  - The faction button: the game shows the plain picture in a faction and
    the one with the icon outside one; this mod had them the other way
    round, so its icon sat under your faction's logo. Swapped, and the logo
    is now centred in the button's ring.
  - The world tension globe now shows Valsora instead of Earth. That comes
    from the Valsora mod itself (update it too), so it shows with or without
    this mod.

NEW IN v0.4.6
-------------
  - The main menu background is your new arrangement: the Nonscio,
    Araseos, Yastreovakia, Usnistan and Orientalis labels moved (Orientalis
    down onto its land, Nonscio to the west). Same picture otherwise.
  - Everything from v0.4.5 below (the main menu button fix) is included;
    v0.4.5 was never tested in game.

NEW IN v0.4.5
-------------
  - Main menu fix, for real this time. Your error.log showed the cause:
    the game rejects a window's position anchor written in quotes
    ("Not a valid orientation: CENTER_DOWN") and falls back to the
    top-left corner of the screen. The button row's offset from the
    bottom centre then put it above the top-left corner, off-screen.
    Every anchor is now written the way the game's own files write it.
  - The same mistake had sent five top bar windows meant for the right
    edge (command power, nukes, and the army, navy and air buttons) to
    the left edge, off-screen. They are anchored correctly now.
  - Click-through ("alwaystransparent") was written on twelve windows
    themselves, where the game ignores it ("Unexpected token" in
    error.log). It is now on the window's background where there is one
    (the focus tree's header band, the shadow under the top bar). The ten
    scripted text windows (politics screen, top bar) have no background
    and their text boxes were already click-through, so for them nothing
    changes in game.
  - error.log should have no more "Not a valid orientation" or
    "Unexpected token: alwaystransparent" lines from this mod. If any
    remain, send the log again.

NEW IN v0.4.4
-------------
  - Main menu fix: in v0.4.3 none of the menu buttons showed. The button
    row is now placed by a plain offset from the bottom-centre of the screen
    (the method the game itself uses for bottom-centred windows), so it sits
    along the bottom as in the mockup.
  - The social links (homepage, forum, Discord, ...) moved from the middle
    of the map to the top-left corner, where the game's logo used to be.
  - The Paradox subscription box is kept out of sight (it is still in the
    file, just outside the visible part of the button row).

NEW IN v0.4 - v0.4.3
--------------------
  - Icons: back to the mockup's simple gilt line icons (v0.4.1), with
    modern subjects: a high-cut combat helmet for the army, the NATO
    division symbol for deployment, a delta-wing jet for the air force and
    a container ship for convoys.
  - Top bar: the seal under the country name is now the DECISIONS button,
    with its counters and alert glow. The FACTION button moved into the row
    of crown buttons (first slot); in a faction it shows the faction's logo.
  - Politics screen rebuilt to the Government mockup (without the Court):
      * "Government" header with the country's full name
      * arched portrait over a sunburst, gold "Head of State" ribbon
      * leader name, ideology chip, and a grid: ruling party and its
        popularity, elections, last election, political power and its
        daily change
      * the leader's description in italics (Roland II has one; leaders
        without one get an ornament)
      * popularity pie in a gilt ring with diamond swatches, next to cards
        showing the current conscription, economy and trade laws
      * national spirits band; faction and national focus cards side by
        side (click the focus card to open the focus tree)
      * advisors and laws list at the bottom, where laws are still changed
  - Province panel (what opens when you click a province), arranged like
    the mockup: owner flag and state name in the header, a row with
    victory points, manpower and resources, then the shared building slots,
    the state buildings and claims; the province part below keeps the
    game's arrangement in the new style.
  - Focus tree: gilt title on a header band, deco search box, zoom and
    close buttons, filter chips, a gridded background, an octagonal
    medallion behind every focus, new name plates (gold = completed, jade =
    available, dark = unavailable), a restyled detail pop-up and a legend.
    Focus icons are unchanged.

HOI4 has no outliner, so the mockup's outliner panel has no game screen to
restyle. The army bar at the bottom and the map mode buttons at the bottom
right are planned next.


WHAT CHANGES (all files)
------------------------
Core skin (vanilla textures replaced at the same path and size):
  gfx/interface/tiles/ (window frames, panel backgrounds; the tooltip is
  tiles_dialog.dds since v0.4.8),
  gfx/interface/button_<w>x<h>.dds (11 standard buttons),
  gfx/fonts/hoi_mapfont4 (map country names, redrawn in Federo).
Textures the game swaps onto buttons while running, replaced at their paths:
  gfx/interface/topbar/toolbar/{international_market,diplomacy}_button.dds,
  gfx/interface/factions/ui/topbar_faction{,_empty}.dds,
  gfx/interface/decisionview/decisions_glow{,_blue,_yellow,_green}.dds,
  gfx/interface/focusview/titlebar/focus_{unavailable,can_start,completed}_bg.dds,
  gfx/interface/pol_view_bg{,_no_dlc}.dds (the politics screen's header).
Interface files (rebuilt from the game's or Valsora's own; every original
element is kept, only moved and re-skinned):
  interface/topbar.gui, alerts.gui, countrypoliticsview.gui,
  countrystateview.gui, nationalfocusview.gui, frontendmainview.gui.
New files: interface/valsora_deco_*.gfx/.gui,
  common/scripted_guis/valsora_deco_*, common/scripted_triggers/valsora_deco_*,
  common/scripted_localisation/valsora_deco_politics.txt,
  common/frontend/backgrounds/base_backgrounds.txt (replaces the game's list,
  so the Valsora background is the only main menu background),
  gfx/loadingscreens/valsora_menu.dds, localisation/*/valsora_deco_*.


DIFFERENCES FROM THE MOCKUP, AND WHY
------------------------------------
  - Politics: the faction member flags are not shown (the game gives the
    politics screen no list of members to draw), and national spirits are
    a row of icons with their effects in the tooltips rather than one big
    card. The national focus card is not in the mockup but the game needs
    it: it is how the focus tree opens.
  - Politics: the laws are changed in the advisors and laws list at the
    bottom of the screen (the law cards of v0.4 - v0.4.7 only repeated it).
  - Province panel: infrastructure and air base are the game's building
    tiles with levels rather than the mockup's bars, and the province part
    keeps the game's arrangement (the game places several of its pieces).
  - Top bar: the game writes the date as one string, so it is one line of
    capitals rather than date over time and weekday.
  - Main menu: the game's Career Profile button takes the place of the
    mockup's Tutorial button (the tutorial is in the Single Player panel),
    and the game's Friends / Nudge / Exit buttons sit in a second row. The
    radio widget is not part of this release. The game's social links sit
    in the top-left corner and its subscription box is hidden.


THINGS TO CHECK IN-GAME
-----------------------
  Side panels (v0.5.1)
  - A panel rises into place as it opens and sinks as it closes, without
    crossing the flag or the name, the first opening too, and when you
    switch from one panel to another.
  Side panels (v0.5; one screenshot of each you open is ideal)
  - Each opens right under the top bar; the flag medallion, the country
    name and the decisions seal show above it, with the gilt edge round
    them and no map between them. Nothing of the panel draws over the
    medallion.
  - The title sits right of the medallion; the close diamond and the
    panel's own buttons (division overview: naval HQ, sunk ships,
    equipment; occupied territories: garrison log, equipment;
    construction: the factory counter and the arrow that widens the
    building list) work.
  - The panel's contents start below the seal and nothing is cut off at
    the bottom (logistics, officer corps, the faction screen and the
    research screen have the most at the bottom). In decisions, scroll to
    the last decision: the game sizes that list itself, so it is the one
    most likely to run past the bottom of the screen now.
  - The construction screen with its building list both open and folded
    away (the arrow left of its close diamond): does the header still
    match the panel when folded?
  - Tabs show the selected one in jade; sort buttons, filters and
    checkboxes look right in their two states.
  - The windows that open beside a panel open flush under the top bar.
  Map modes and minimap (v0.5)
  - The land, air and naval buttons show a helmet, a jet and an anchor,
    and the selected one is jade. The small map mode icons and the toggles
    (day/night, counters, fog of war, radar ...) read well in gilt, and on
    and off are told apart.
  - The minimap shows Valsora in gilt; the camera frame on it, the handle
    that slides it away (ctrl+m) and the ping buttons work.
  Top bar
  - Flags look crisp. The new market icon shows.
  - The decisions seal opens decisions; its counters and glow appear.
  - The faction button shows the faction logo once you are in a faction.
  - The logistics tray and XP badges read well. The globe sits in its ring.
  - Alerts do not cover the tray or the menu buttons.
  - Long names use the small font, short names the large one.
  - (v0.4.5) Command power, nukes and the army / navy / air buttons sit at
    the right end of the bar.
  - Hovering political power and the factory counts still shows their
    tooltips (the mod's own text is drawn over them).
  Politics screen
  - (v0.4.8) The screen opens right under the top bar; the flag medallion,
    the country name and the decisions seal show above it, with the
    screen's gilt edge round them and no map showing between them.
  - (v0.4.8) The decisions seal still opens decisions while the screen is
    open (clicks should reach it through the cut-out), and the empty parts
    of the screen's header do not click through to the map.
  - (v0.4.8) The decision counters sit either side of the seal.
  - (v0.4.8) The background behind the portrait and name is the deco one.
  - (v0.4.8) Tooltips have the dark lacquer and gilt frame.
  - (v0.4.8) The sub-ideology line names the leader's sub-ideology, with
    its description in the tooltip. Last election says None without
    elections, and a date with elections.
  - (v0.4.8) National spirits: Devlon has 15 test spirits (Valsora mod):
    they should show as small icons, seven to a row, inside their box.
  - Every value in the grid shows a value (ruling party and %, elections,
    last election, political power and daily change). If one shows raw
    text or stays empty, tell me which.
  - The pie sits in its gilt ring; the legend diamonds have party colours.
  - The focus card opens the focus tree and its progress bar fills.
  - The advisors and laws list scrolls, and reaches the bottom of the
    screen.
  Province panel
  - The background covers the whole panel, including the province part at
    the bottom.
  - Building pictures sit inside their tiles.
  Focus tree
  - Focus names sit centred on their plates; the links still meet the
    plates; the medallions sit behind the icons.
  - The filter chips light up when selected.
  - The search box and buttons under the header band still respond.
  Main menu
  - (v0.4.5) The button row shows along the bottom, centred, with Friends /
    Nudge / Exit under it and the version number at its left.
  - The social links sit in the top-left corner.
  - Single Player opens its panel in the middle of the screen as before.
  - (Confirmed in v0.4.3: the Valsora background shows.)
  Console
  - The mod does not change the console (its window, font and textures are
    the game's). The blue and green rectangles marked 1280x720 and 1600x900
    are the game's own "GUI bounds" debug guides; the console command `gui`
    turns them on and off.
  Still vanilla
  - The army bar (next), the world tension globe's glow, achievements and
    dismissed alert buttons, the music player pop-out, faction logos, focus
    icons and focus links, and the pictures inside some panels (research's
    scientists, the officer corps' coloured command boxes, the
    intelligence agency's art).


SHARPER FLAGS (optional, untested)
----------------------------------
The game expects 82x52 large flags (NGraphics COUNTRY_FLAG_TEX_WIDTH/HEIGHT
in common/defines/00_graphics.lua). Raising those defines to 164x104 and
re-exporting every large flag at that size could give sharper flags. This is
an experiment for later, not part of this release.


UPDATING AFTER A HOI4 PATCH
---------------------------
Texture and font replacements survive patches. The .gui files may not. The
source project rebuilds them from your game's own files with
tools/build_all.py; see CLAUDE.md in the source project.


CREDITS
-------
Fonts: Federo, Josefin Sans and Bodoni Moda (SIL Open Font License 1.1,
licence texts in gfx/fonts/OFL_*.txt). Limelight (also SIL OFL) appears only
in the main menu artwork. All textures and icons are original.
