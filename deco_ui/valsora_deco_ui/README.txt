VALSORA DECO UI - v0.10.4 (for HOI4 1.19)
=========================================

An art deco interface for the Valsora total conversion: core skin and fonts,
a rebuilt top bar, the politics screen, every side panel, the province panel,
the focus tree, the army bar, the events, the map modes and minimap, and the
main menu, laid out like the Valsora mockups; and, in the game's own layouts,
the loading bar, the battles, the battle plan toolbar, the diplomatic
actions, game setup, the selected units' badges and most popups.


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


NEW IN v0.11.1
--------------
  - The music player in the deco style: its header, buttons, volume and
    station box; the track list stays on its ivory sheet.
  - The music controller opens as a tab hanging under the music button,
    sliding down out of the tray.
  - The production lines have their boxes again (the equipment's plate,
    the factory slots, the resource wells); the trade rows lose their
    specks and stray lines.

Things to check in game (v0.11.1):
  - the music player (open it from the controller): the header, the
    buttons (play / pause, shuffle on and off), the volume;
  - the controller: it slides down from under the music button and is
    hidden in the tray when closed;
  - a few production lines (land and naval, one selected), the trade list.


NEW IN v0.11
------------
  - Top bar: military factories green, civilian orange; the decision
    plates' tops level with the bar; the logistics numbers spaced; the
    music button the tray's framed left end, after the author's mockup.
  - Diplomacy and intel: the bar level with the flag; long names cut
    with "..." before the opinion box; the portrait in the politics
    screen's arch, whole; the pie as the politics screen's; the focus
    icon centred in an octagon; a new focus button.
  - The side panels' own pictures (all but the army, navy and air
    overview's and the intelligence agency's); the research picture
    centred.
  - The decisions tab restyled; the focus tree's filter icons centred.

Things to check in game (v0.11):
  - the top bar (factories, decision plates, logistics, music button);
  - Krionik's diplomacy panel (the seal whole), a long leader name;
  - the decisions tab; the panels' new pictures; the focus filters;
  - Rouental's decision "Test: Many Alerts at Once".


NEW IN v0.10.4
--------------
  - The diplomacy panel's own pictures: the leader's portrait in an arched
    gilt frame like the events' and the army bar's, the flag in a frame
    like the medallion's, the politics block with a gilt ring round the
    pie, the national focus button, the spirits band and the wells. The
    filter strip and the opinion box keep the game's pictures (they have
    the game's icons painted in).

Things to check in game (v0.10.4):
  - another country's diplomacy panel: the portrait in its arch, the flag,
    the pie, the focus button (hover it), the national spirits.


NEW IN v0.10.3
--------------
  - The decision counts beside the seal are no longer round dots: each is
    a plate the shape of its shoulder of the medallion, as you outlined it,
    its corner by the seal cut off (red for decisions running out of time
    on the left, the ones to take on the right), the number in the middle.

Things to check in game (v0.10.3):
  - both counts at once (a decision with a time limit and one to take):
    the plates in the shoulders, the numbers centred on them.


NEW IN v0.10.2
--------------
From your screenshots of 18 October:
  - The flag medallion after your mockup: a gilt rim on the flag, a gilt
    line round it and two stepped brackets at each corner (no corner
    diamonds); the country's name 1 px further right, so it sits in the
    middle (the game centres the letters' spacing after the last one too).
  - The army, navy and air experience badges centred at the foot of their
    buttons, the number in the middle of the badge.
  - The top bar's factories read military, naval, civilian, as the list
    under them does.
  - The politics screen's faction card: eleven flags a row (eight before).
  - The state panel's flag and name moved right, clear of the corner.
  - The country and leader events lose their corner brackets: the double
    chamfered frame is the corner, the same at all four.
  - The Release Nation window: a long list of states scrolls above the
    checkboxes instead of running over them.
  - An occupied state's resistance and compliance: two tidy rows beside
    the claims, their bars gilt wells filled amber and jade (the second
    ran over State Modifiers).

Things to check in game (v0.10.2):
  - the medallion's frame and the name's centring (a one-line and a
    two-line name);
  - the experience badges' numbers;
  - the factories' order and colours;
  - a faction with more than eight members on the politics screen;
  - the state panel's top left corner;
  - a leader event (A Word with the General) and a country event;
  - Release Nation for Crvenognjište (Krionik): the list of states;
  - an occupied state's panel: resistance and compliance.


NEW IN v0.10.1
--------------
From your look at v0.10 in game:
  - The loading pictures from Valsora's map are out again, kept for when
    the map is final (the loading screen showed the game's own pictures
    anyway, and game setup had taken one as its background). The loading
    bar and tip lose the corner marks that stuck out.
  - Game setup: the country selection is a card wider, so "Other
    countries" fits; the country's details sit on one line, and the
    ideology wheel is the politics screen's.
  - The battle plan bar and its pop-ups lose their corner marks, and every
    icon is centred in its slot.
  - The top bar's fuel, supply and convoys in a slightly smaller font.
  - The decision counts sit in the medallion's shoulders, either side of
    the seal.
  - The division designer's combat width is centred in its ring; the
    commanders' skill is a white number on a dark diamond, centred.
  - The fleet panel: long ship types and admirals' names fit (a long name
    takes two lines inside its frame).
  - The news page's story is a size smaller, so it ends above the rule;
    the other events' text boxes are taller, so long texts aren't cut.

Things to check in game (v0.10.1):
  - the loading screen's bar and tip, and game setup's background (the
    menu's picture);
  - New game, the Vale of Reibonne start: all nine cards inside the frame,
    the country's details;
  - draw a battle plan: the bar's corners and icons;
  - the fuel, supply and convoy numbers;
  - the decision counts beside the seal (one with a time limit, one to
    take);
  - the division designer's combat width; the commander picker's skill;
  - a fleet with long ship names and an admiral with a long name;
  - a news event with a long story (a capitulation), a long country event.


NEW IN v0.10
------------
"Please start applying the proposed changes to all the UI screens": the
screen inventory's suggestions, all of them, and more. These are new
pictures at the game's own paths and sizes; the game's layouts are kept.
  - Loading screens: the four drawn from Valsora's map (the world in gilt,
    Valsora rising, the Vale of Reibonne, the nations) are in the mod, in
    the menu's background list after the menu's own picture, and the
    loading bar and tip are gilt.
  - Scroll bars and sliders everywhere: gilt arrows, a diamond thumb,
    slim grooves.
  - The selected army, army group, fleet and operative badges, and the
    selected air wings' rows.
  - The battle plan toolbar and its pop-ups (planning speed, cohesion, the
    HQ's distance, area defence); the order buttons keep the game's
    symbols, in gilt.
  - The land battle window (terrain slot, medallions for both sides, the
    tactics, the divisions' cards, the tactics list) and the naval battle
    (the plotting sheet under the ships).
  - The diplomatic action windows (declare war, justify, lend-lease,
    volunteers, guarantee, licences and the rest): one frame each, with a
    gilt line emblem for the action; the war goal lists on ivory.
  - Game setup: the country selection, the start's window, the country's
    details, the difficulty buttons, the Start button.
  - The windows the skin had missed: the confirmations and other popups
    (their headers and footers too), the peace summary, world tension, the
    aces and air wing windows, the tutorial and its hints.
  - Now and then: the settings (Options), the trade offer, the variant
    designer and market stockpile, the agency's upgrades and logo, the
    insignia and colour pickers, air missions over a region, the naval
    region view.
  - Small shared pieces: the small close button, the dark recessed panels,
    the strength bars' chip.

Things to check in game (v0.10):
  - the loading screen: which picture shows, and the bar and tip;
  - the main menu still opens on its own picture (Change background
    should now offer five);
  - a scroll bar and a slider (the settings' volume, a trade);
  - select an army, an army group, a fleet: the badge's texts and buttons
    on their panels;
  - draw a battle plan: the toolbar and a pop-up;
  - a land battle, and its tactics list;
  - declare war or justify a war goal; send an offer that gets an answer
    (the request popup's header);
  - New game: the country selection and the start's window;
  - Options (settings), the world tension window, a trade offer.


NEW IN v0.9.1
-------------
From your screenshots and error.log of v0.9:
  - The names on the map are back. The map's font had grown too large for
    the game to load (2048 x 2048, with the Vietnamese letters); it is its
    old size again, and the build now checks it.
  - The designers' statistics are dark again on the ivory sheet (the
    game's "inverted" typewriter fonts are dark ink; ours were white).
  - Doctrine screen: the tabs start right of the notch instead of running
    into the name under the flag.
  - Faction screen: long faction names fit (the box is wider and starts
    right of the notch).
  - Politics screen: LEADER is centred in its tag both ways; the members'
    flags wrap onto a second row (up to 16).
  - The decisions seal's two badges are the same distance from it.
  - Top bar: fuel, supply and convoys moved up into the band, as its last
    readout (three small rows: icon, value, bar), so the tray under the
    readouts is gone and the alerts row runs on across the screen to the
    right-hand tray (26 a row instead of 10). To make the room the crown
    buttons are 4 px apart instead of 6 and the labels slightly tighter.
  - The right-hand tray's edge sits further out from the music button.
  - The "green bar" between Construction and Production was the game's
    production alert (it lights the Production button when something
    there wants you), drawn behind the button so it only showed in the
    gap. It is now a gilt ring that pulses round the Production button.

Things to check in game (v0.9.1):
  - names on the map;
  - a designer's statistics readable;
  - the doctrine tabs clear of the name;
  - a long faction name on the faction screen;
  - LEADER centred, flags in two rows (a faction of nine or more);
  - the top bar: fuel, supply and convoys in the band (hover each row for
    the game's tooltip), the alerts running across, the music button's
    tray, the ring round Production when the game raises that alert.


NEW IN v0.9
-----------
  (The user: "do 1 (though be prepared to possibly revert it,) 2, 3 ..."
  The restyled screens are one commit of their own, so they can be taken
  out again in one step.)
  - Research trees and the doctrine screen: they open flush under the top
    bar like the focus tree, with its notched header round the medallion
    and seal (they used to cover the medallion's lower half), a gilt title
    ("Research", "Doctrines") right of the notch, the game's folder tabs in
    the header and the close diamond. The trees, technologies and doctrines
    are the game's.
  - The designers (division, tank, plane, ship) and the commander pickers:
    their background pictures redrawn in the deco style at the game's
    sizes: lacquer plates with gilt hairlines where the game's metal was,
    recessed panels where it draws its lists, an ivory ruled sheet where it
    writes the statistics (dark text), and the commanders' cards in
    parchment with a gilt rim, a lacquer portrait well and an emblem strip
    in the card's colour (army red, navy blue, captured grey). The advisor
    picker uses the same pictures.
  - Politics screen: the faction card shows its members' flags in a row
    under the faction's name, as the Government mockup has them (up to
    eight; the name of each is its tooltip).
  - The hot-join window (multiplayer) opens below the medallion.
  - A check now fails the Deco UI's build if a game window at the top left
    would sit under the flag medallion, so a new one is caught before it
    ships.

Things to check in game (v0.9):
  - the research screen and the doctrine screen: the medallion and seal in
    the notch, the title, the tabs (each opens its tree), the close diamond,
    the trees under the header and not cut off;
  - the designers (division, tank, plane, ship) and the commander picker
    (a general's "assign" button): the pictures under the game's lists and
    statistics, nothing misplaced; the statistics readable on the sheet;
  - the politics screen while in a faction: its members' flags under its
    name (the flags drawn by the game's text: their size is a guess);
  - the faction screen opened: nothing showing in its notch (the game parks
    the member and invite lists behind it; assumed, not seen).

NEW IN v0.8.4
-------------
  - Focus tree: the title is in the header ("NATIONAL FOCUS" over the
    tree's name in large gilt capitals). It sat on the first row of focuses:
    the game had put it inside the tree's scrolling canvas. The full name
    and sub-ideology line under it is gone with it.
  - Focus tree and side panels: the headers are opaque (the map's names
    showed through faintly). The shortcuts arrow (lower left of the focus
    tree) and the construction list's fold arrow are gilt chevrons on
    lacquer chips, not the game's copper arrows.
  - The counts on the decisions seal (and the top bar's other counts) are
    small gilt-rimmed octagons in grey, red, gold and jade, not the game's
    round badges.
  - Tabs: the large tabs are drawn 4 px in from each side, so the captured
    commanders' two tabs (and the research and trait screens') no longer
    overlap.
  - Army bar: the plus on an empty general or field marshal card is a
    smaller medallion in the middle of the chest, clear of the shoulders.
  - Fonts: the game's fonts the Deco UI redraws keep the game's own base
    line, which the game checks against its Cyrillic files (error.log:
    "base (13) in 'gfx/fonts/hoi_16tooltip3.fnt' does not match ...").
  - Fonts: Vietnamese letters (the horned Ơ Ư, Đ, and every tone-marked
    vowel), for Plaija's names ("Mai Đức Tài"). Josefin Sans has them;
    Federo and Bodoni Moda don't, so those letters are put together from the
    face's own letters and accents, with the hook above and the dot below
    from Josefin Sans, and the horn and đ's bar drawn in the face's weight.
    The Valsora build now checks that every letter of the mod's text and
    name lists is in the fonts.
  - Names under the flag: a name that needs two lines in the large letters
    (the Kampfian Empire) uses the smaller ones, which leave room above and
    below (two large lines filled the box up to the flag's frame).
  - The navy: the selected fleets' panel starts below the medallion and the
    decisions seal, as the armies' did in v0.8.2, and the home base and
    refit windows beside it move down with it.

Things to check in game (v0.8.4):
  - the focus tree: the title in the header, nothing over the focuses,
    no map showing through the header; the lower left arrow;
  - the decisions seal's counts (start a decision with a time limit for a
    red one);
  - the captured commanders window (the army screen): two tabs apart;
  - an empty general card: the plus on the chest;
  - error.log: no "does not match previous fontfiles" line.
  - Plaija's characters (a Vietnamese name in a tooltip, on the politics
    screen, a general's card): every letter drawn, accents in place;
  - a long name under the flag (the Kampfian Empire): small letters, clear
    of the flag's frame;
  - select a fleet: its panel below the medallion, nothing hidden, its list
    reaching the bottom of the screen without running off it.

NEW IN v0.8.3
-------------
  - Events: the keystone's diamond sits a little lower, clear of the
    keystone's top step (it touched it).
  - The news: the masthead's globe is the newsreel globe, girdled by a
    tilted gilt ring (behind the globe at the back, over it in front): the
    user's favourite of the designs. The others stay in
    art/proposals/news_globe/.
  - Superevents: the crest is the same ringed globe, whole, rising across
    the middle of the frame's top edge (it was the top half of a globe, cut
    off at the frame).

Things to check in game (v0.8.3):
  - the news masthead's ringed globe at its size;
  - a superevent (Rouental's test decision): the whole globe across the
    frame's edge;
  - an event card: the keystone's diamond clear of the top step.

NEW IN v0.8.2
-------------
  - Superevents: only the open superevent's title shows (all eight titles
    were drawn over each other). The crest over the frame holds Valsora
    rising, the top half of the news masthead's globe, on lacquer, in place
    of the mockup's red guillotine. Other emblems (a compass star, an
    hourglass, a laurel wreath) are in art/proposals/crests/.
  - Events: the crest on the card's top edge is a stepped keystone with a
    gilt diamond, in place of the half sunburst whose thin rays blurred at
    its size. Other designs are in art/proposals/crests/. An option's text
    is a size smaller, so three lines fit its plate (the third spilled out).
  - The news: the globe is lit (pale to deep gilt land, a bright edge on the
    lit side), its grid over the sea only, seen above Nonscio and Araseos.
    The first globe, the one before this and three other ideas are in
    art/proposals/news_globe/.
  - Country names under the flag: a name that needs two lines in the large
    letters shows both (KAMPFIAN EMPIRE, UTOPIAN REPUBLIC showed only their
    first word and "...").
  - The selected armies' badges ("Request Expeditionaries" with them), the
    selected air wings and the operatives start below the flag medallion
    and its seal: the medallion covered them.

Things to check in game (v0.8.2):
  - a superevent (Rouental's test decision): one title, the new crest;
  - an event with the keystone; a long option on three lines;
  - Kampf or the Utopian Republic: the whole name under the flag;
  - select some divisions: their army's badge below the medallion.

NEW IN v0.8.1
-------------
  - The news: the masthead is now VALSORAN STANDARD, the two words the
    same width either side of the globe, so it sits in the middle. The
    globe is redrawn: simpler land that reads at its size, flat gilt, a
    graticule, looking down on open sea with land round it. The page under
    it is centred too (the game's picture, headline and story sat a few
    pixels off the middle). Other names are in art/proposals/news_masthead/.
  - For testing (in the Valsora mod): Rouental has a "Test Events"
    decision category with one decision per kind of event window (country,
    long country with four options, state, news, major news, leader,
    operative) and one for a test superevent.

Things to check in game (v0.8.1):
  - fire each of Rouental's test decisions and look at each window: the
    news page and its masthead especially.

NEW IN v0.8
-----------
  - The art deco fonts throughout. The game's own fonts are redrawn in the
    Deco UI's faces, so the screens the Deco UI hasn't re-laid read like the
    rest: tooltips (Roland's titles on his portrait, for one), lists, the
    division designer, the leader and unit screens, settings, window titles.
    Josefin Sans for text and numbers, Federo for headings and the game's
    serif menus. The game's boxes were made for its own fonts, and Josefin
    is wider than the game's, so the text is a size or two smaller than the
    game's; lines keep the game's spacing.
  - The army bar: the play / stop buttons and the plate behind them are
    centred over the general, on one line with the frame, the plaque and
    the division count.
  - Events: the options sit centred between the picture and the card's right
    edge (they were much closer to the picture). A leader event's foot
    matches the country event's.
  - The news: WORLD NEWS has a small gilt globe of Valsora in the middle,
    with WORLD and NEWS at the same distance either side.

Things to check in game (v0.8):
  - text everywhere: readable at its new sizes, nothing cut off (a word
    missing at the end of a line or button means a box the new font doesn't
    fit: a screenshot names it); tooltips (a leader portrait, a law, a
    building);
  - the army bar's buttons over the generals; an event's options; a news
    event's masthead.

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
Fonts: drawn from Federo, Josefin Sans and Bodoni Moda (SIL Open Font
License 1.1, licence texts in gfx/fonts/OFL_*.txt). They are modified (bitmap
versions, with letters of our own), so they carry names of their own, Valsora
Deco Display, Sans and Italic, as the licence asks of a modified version. Limelight (also SIL OFL) appears only
in the main menu artwork. All textures and icons are original.
