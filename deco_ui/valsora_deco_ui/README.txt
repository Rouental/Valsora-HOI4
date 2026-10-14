VALSORA DECO UI - v0.4.5 (for HOI4 1.19)
======================================

An art deco interface for the Valsora total conversion: core skin, a rebuilt
top bar, the politics screen, the province panel, the focus tree and the
main menu, laid out like the Valsora mockups.


INSTALL
-------
1. Copy BOTH of these into  Documents/Paradox Interactive/Hearts of Iron IV/mod/
     valsora_deco_ui.mod
     valsora_deco_ui/          (this folder)
   Replace older versions completely (delete the old folder first).
2. In the launcher, add "Valsora Deco UI" to your playset BELOW the Valsora
   mod. Both mods contain interface/countrypoliticsview.gui, and this one was
   built from Valsora's, so it must load last.
3. Start a game. If anything looks wrong, check
     Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log
   for lines mentioning "valsora_deco", a .gui file, a texture or a font.

The layout is built for 1920 px of UI width: 1920x1080 at 100% UI scale, or
2560x1440 at up to 133%.


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
  gfx/interface/tiles/ (window frames, panel backgrounds, tooltip),
  gfx/interface/button_<w>x<h>.dds (11 standard buttons),
  gfx/fonts/hoi_mapfont4 (map country names, redrawn in Federo).
Textures the game swaps onto buttons while running, replaced at their paths:
  gfx/interface/topbar/toolbar/{international_market,diplomacy}_button.dds,
  gfx/interface/factions/ui/topbar_faction{,_empty}.dds,
  gfx/interface/decisionview/decisions_glow{,_blue,_yellow,_green}.dds,
  gfx/interface/focusview/titlebar/focus_{unavailable,can_start,completed}_bg.dds.
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
  - Politics: the law cards show the current laws; changing a law is still
    done in the advisors and laws list at the bottom of the screen.
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
  - Every value in the grid shows a value (ruling party and %, elections,
    last election, political power and daily change). If one shows raw
    text like [ROOT.GetLastElection] or stays empty, tell me which.
  - The three law cards show your current laws.
  - Roland II's description shows; other leaders show the ornament.
  - The pie sits in its gilt ring; the legend diamonds have party colours.
  - The focus card opens the focus tree and its progress bar fills.
  - The advisors and laws list scrolls.
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
  - The army bar and the map mode buttons (next), the world tension globe,
    achievements and dismissed alert buttons, the music player pop-out,
    faction logos, focus icons and focus links.


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
