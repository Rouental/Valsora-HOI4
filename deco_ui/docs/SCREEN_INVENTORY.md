# Screen inventory

2026-10-17, Deco UI v0.9.1. Every screen of the game, grouped by how far the Valsora Deco UI has changed it, so the next
screen to restyle can be picked. The pictures are on a contact sheet, `deco_ui/build/screen_inventory.png` (the game's
look on the left, the Deco UI's on the right; one sheet per level in `deco_ui/build/inventory/`). They show the game's
art, so they stay in the git-ignored `build/` folder.

## The three levels

- **Restyled**: the Deco UI ships its own `.gui` for the screen (or the Valsora build makes it with the Deco UI's code), so
  its layout is changed. Some of these are only moved, clear of the flag medallion and seal, and keep the game's look
  otherwise: they are listed apart ("moved only").
- **Re-skinned**: no `.gui` of its own, but the screen's own pictures are replaced at the game's paths. Either they were
  drawn for that screen (the map modes, the designers, the commander pickers) or the screen's window frame is one of the
  core skin's tiles (the pause menu, the popups, the rosters), so the window reads as deco while any picture inside it
  is still the game's.
- **Game's own**: the screen's background and pictures are the game's. Only the global pieces touch it: the game's fonts
  (redrawn in the deco faces, v0.8), the standard and close buttons, tooltips, and here and there a shared header, tab
  or checkbox.

How this was worked out: each of the game's 453 `.gui` files (`deco_ui/reference/vanilla/interface/`, subfolders
included) was put under the screen it belongs to; the files the Deco UI ships (`deco_ui/valsora_deco_ui/interface/`) and
the Valsora build's own (`build/valsora_test/interface/`) were compared with them; and every sprite each file names was
followed to its texture in the game's `.gfx` files, to see whether the Deco UI ships a file at that path. A screen's
level follows its main window: a window whose own background is replaced is re-skinned; one whose background is the
game's is the game's own, even when a few shared pieces in it are deco. "In game" in the notes repeats what
`deco_ui/CLAUDE.md` records as seen in the author's screenshots; everything else there is assumed. Anything this
survey inferred rather than read from the files is marked "(inferred)". How often a screen is seen is an estimate.

The thumbnails were drawn with the side panels' renderer (`tools/preview_panels.py`: the `.gui` files read as the game
lays them out, the game's own textures, the Deco UI's where it replaces them, the redrawn fonts), or taken from the
existing previews in `deco_ui/build/` where there is one (the top bar, the politics screen, the focus tree, the state
panel, the main menu, the events, the army bar, the side panels, the research and doctrine screens, the designers, the
lower right corner, the fonts); the superevent comes from the Valsora build's `scripts/superevent_preview.py`. Lists the
game fills in while playing are drawn empty, as faint outlines, and the game's own fonts are approximated on its side
(their textures are not in the reference copy). Where nothing visible changes, the sheet says "same as the game's".
The scripts that drew the thumbnails and the sheet were one-off and are not in the repository; the per-screen
pictures are in `deco_ui/build/inventory/` (`<screen>_game.png`, `<screen>_deco.png`).

## Count

95 screens, from the game's 453 `.gui` files (253 of them the tank designer's blueprints), plus two global rows (the fonts, the shared templates) that are not screens:

- Restyled: 34 (27 re-laid out, 7 moved only)
- Re-skinned: 26 (9 with their own pictures redrawn, 17 framed by the core skin)
- Game's own: 35 (of which 2 never seen in Valsora: Earth's scripted windows, the developer tools)

The sheet has thumbnails for 79 rows; the rest say why in the last column.

## Restyled

### Restyled: re-laid out

The sixteen side panels (from Research down) share one treatment, `make_panels.py` (v0.5): each opens flush under
the top bar's band with the politics screen's notch round the medallion and seal, a lacquer header with the game's title
moved right of the notch in gilt capitals, the close diamond and the panel's header buttons beside it, and the politics
screen's body tile; everything else in the panel keeps the game's layout, moved down clear of the seal, with the pieces
the panels share (tabs, sort buttons, list headers, checkboxes, close buttons, background tiles) re-skinned at the game's
paths. The windows that open beside them are moved flush too. In game since v0.5.1 (the notch and the opening).
Each row says what inside the panel is still the game's.

| Screen | Files (`interface/`) | How often | What the Deco UI does, and what is still the game's | Picture |
|---|---|---|---|---|
| Top bar and alerts | `topbar.gui`, `alerts.gui`, `factions/topbarfactionbutton.gui` | every session | Re-laid to the Main mockup (make_topbar.py): the flag medallion with the country's name, the decisions seal under it, the crown row of toolbar buttons with the faction first, political power and factories as scripted text, fuel, supply and convoys as the strip's last cell (v0.9.1), command power and nukes in the right-hand tray, world tension in a gilt ring; the alerts row below the band, running on to the right-hand tray. Still the game's: the world tension glow, the supply icon, the achievements and dismissed-alert buttons, the music player pop-out, faction logos (the tension globe itself is the Valsora build's). In game since v0.4.5; v0.9.1's strip not yet seen. | sheet |
| Politics (government) | `countrypoliticsview.gui` | often | The Government mockup (make_politics.py, run by the Valsora build on Valsora's own copy of the file): flush under the band and notched round the medallion and seal; the leader's arched portrait and ribbon, a five-cell grid (ruling party, elections, last election, political power, sub-ideology), the popularity pie, national spirits beside it, the faction card with its members' flags (v0.9), the focus card. The advisors and laws list below is the game's layout on the core skin. In game since v0.4.7; v0.9.1's LEADER tag and two rows of flags not yet seen. | sheet |
| National focus tree | `nationalfocusview.gui`, `nationalfocusview.gfx` | every session | The FocusTree mockup (make_focus.py): a notched header with the tree's title, filter chips, search, zoom and close on one row; a medallion and plate per focus state, gilt links, red exclusive marks, a ring of rays round the focus in progress, a scale-pattern canvas in a gilt frame. The focus icons are the game's, as the author asked. In game (v0.8.3); v0.8.4's header fixes not yet seen. The game's look here is its window only (no focuses drawn). | sheet |
| Research trees | `countrytechtreeview.gui` | often | v0.9 (make_research.py, on Valsora's copy with 2036's year labels): flush under the band at the focus tree's x, its notched header, a gilt title, the game's folder tabs in the header, the close diamond. The trees, their background pictures and every technology are the game's. In game (v0.9, 'mostly look good'); can be reverted on its own (commit 8dece16). | sheet |
| Doctrines | `doctrines/doctrines_view.gui`, `countrydoctrinetreeview.gui` | sometimes | v0.9: the research trees' notched header and title; the tabs right of the notch since v0.9.1 (not yet seen). The tracks, the grand doctrine, the doctrine picker (doctrine_selection_list, on the game's tiled_window_w_close) and the special forces folder (countrydoctrinetreeview.gui) are the game's. In game (v0.9). | sheet |
| State and province panel | `countrystateview.gui` | every session | The mockup's state part (make_stateview.py): the owner's flag in a gilt well, the state's name in gilt capitals, a stats row (victory points, manpower, resources), building slots and state buildings on a new background. The province part keeps the game's positions (the engine places some of it). The manual does not record it as seen in game. | sheet |
| Main menu | `frontendmainview.gui` | every session | make_menu.py: the logo hidden (the title is in the Valsora background), the button column turned into a row along the bottom with a large gilt Single Player, the social links in the top-left corner, the single player sub-panel on the deco buttons; Valsora's map art as the background. The DLC panel and the background picker are the game's (inferred). In game since v0.4.5. | sheet |
| Events (country, leader, operative) | `eventwindow.gui` | every session | v0.7 to v0.8.2 (make_events.py, textures ev_*): a lacquer card with a keystone crest, gilt rails and a framed picture, options on gilt-rimmed plates centred beside the picture, the mod's fonts; a leader event's arched portrait frame. The operative event's own background (GFX_event_operative_background) is still the game's (inferred from the files), and the event pictures are the game's. In game (v0.8.1). | sheet |
| News events | `eventwindow.gui` | often | The broadsheet: the VALSORAN (globe) STANDARD masthead (v0.8.1), the picture, headline and story centred under it, the option on a gilt plate. In game (v0.8.1). | sheet |
| Army bar (commanders along the bottom) | `leadergroups.gui` | every session | v0.7 to v0.8.4 (make_leadergroups.py, textures lg_*): arched gilt frames over the portraits (jade when selected), the plate behind a run of cards, play and stop chips, the battle plan's chevrons, the empty card; the division counts on the plaques. In game (v0.8.3, 'looks good'). | sheet |
| Superevent (Valsora's own window) | `valsora_superevent.gui` (Valsora's) | rarely | Drawn by the Valsora build in the Superevent mockup's style when DECO_UI is on (scripts/superevents_deco.py): a veil over the map, gilt frame, the Valsora-rising crest, a title strip per superevent, the framed picture, quote, button and now-playing tab. Seen in game on 2026-10-15; the one-title fix and the globe crest not yet seen. There is no game's version: the window is Valsora's. | sheet |
| Research (side panel) | `countrytechnologyview.gui` | every session | Frame and header restyled (v0.5, make_panels.py); the contents keep the game's layout, moved down clear of the seal, with the shared pieces re-skinned. Still the game's: the header photograph (research_top_win), the research slots' rows (research_line_bg), the folder strip. | sheet |
| Production | `countryproductionlineview.gui` | often | Frame and header restyled (v0.5, make_panels.py); the contents keep the game's layout, moved down clear of the seal, with the shared pieces re-skinned. Still the game's: the header picture (production_win_top), the production lines and factory rows, the equipment cards. The equipment, deployment, repair and ship-name windows beside it are moved flush under the band. | sheet |
| Construction | `countryconstructionsview.gui` | often | Frame and header restyled (v0.5, make_panels.py); the contents keep the game's layout, moved down clear of the seal, with the shared pieces re-skinned. Still the game's: the top picture (construction_screen_top_bg), the building strip, the queue rows. | sheet |
| Recruit and deploy | `countrydeploymentview.gui` | often | Frame and header restyled (v0.5, make_panels.py); the contents keep the game's layout, moved down clear of the seal, with the shared pieces re-skinned. Still the game's: the conveyor view, the division and reinforcement rows. The template window beside it is moved flush under the band. | sheet |
| Diplomacy | `countrydiplomacyview.gui` | often | Frame and header restyled (v0.5, make_panels.py); the contents keep the game's layout, moved down clear of the seal, with the shared pieces re-skinned. Still the game's: the country list and relation strips, the intelligence ledger tab (countryintelledger.gui). The lend-lease windows beside it are moved flush; the diplomatic action windows are a row of their own. | sheet |
| Decisions | `countrydecisionview.gui` | often | Frame and header restyled (v0.5, make_panels.py); the contents keep the game's layout, moved down clear of the seal, with the shared pieces re-skinned. Still the game's: the category headers and decision rows (category_header_bg, decision_item_bg), the progress bars. | sheet |
| Trade | `countrytradeview.gui` | sometimes | Frame and header restyled (v0.5, make_panels.py); the contents keep the game's layout, moved down clear of the seal, with the shared pieces re-skinned. Still the game's: the country rows, the resource filter; the trade offer window (a row of its own). | sheet |
| International market | `international_market/countryinternationalmarketview.gui` | sometimes | Frame and header restyled (v0.5, make_panels.py); the contents keep the game's layout, moved down clear of the seal, with the shared pieces re-skinned. Still the game's: the market banner (market_ui), the contract rows; the market's other windows (a row of their own). | sheet |
| Logistics | `countrylogisticsview.gui` | sometimes | Frame and header restyled (v0.5, make_panels.py); the contents keep the game's layout, moved down clear of the seal, with the shared pieces re-skinned. Still the game's: the bottom picture, the equipment rows, the line chart's frame. The information and fuel windows beside it are moved flush under the band. | sheet |
| Intelligence agency | `countryintelligenceagencyview.gui` | sometimes | Frame and header restyled (v0.5, make_panels.py); the contents keep the game's layout, moved down clear of the seal, with the shared pieces re-skinned. Still the game's: the agency's header art, the operation rows; the upgrades and logo windows (a row of their own). | sheet |
| Army, navy and air overview | `countryarmyview.gui` | sometimes | Frame and header restyled (v0.5, make_panels.py); the contents keep the game's layout, moved down clear of the seal, with the shared pieces re-skinned. Still the game's: the overview's top strip (overview_top_strip), the army, navy and air rows. | sheet |
| Officer corps | `countryofficercorpview.gui` | sometimes | Frame and header restyled (v0.5, make_panels.py); the contents keep the game's layout, moved down clear of the seal, with the shared pieces re-skinned. Still the game's: the coloured army, navy and air banners and marble command boxes, the spirit strip. The HQ template window beside it is moved flush under the band. | sheet |
| Occupation | `countryoccupationview.gui` | sometimes | Frame and header restyled (v0.5, make_panels.py); the contents keep the game's layout, moved down clear of the seal, with the shared pieces re-skinned. Still the game's: the country and state rows, the law headers. | sheet |
| Faction | `factions/countryfactionview.gui` | sometimes | Frame and header restyled (v0.5, make_panels.py); the contents keep the game's layout, moved down clear of the seal, with the shared pieces re-skinned. Still the game's: the goals and special project pictures, the rule rows. The faction list beside it is moved flush, on the game's tiled_window_w_close. | sheet |
| Faction setup | `factions/new_faction_window.gui` | rarely | Frame and header restyled (v0.5, make_panels.py); the contents keep the game's layout, moved down clear of the seal, with the shared pieces re-skinned. Still the game's: the faction identity pictures; the founding, countries and invitation windows in the same file keep the game's layout on the core skin's tiles. | sheet |
| Faction pings and theatres | `factions/faction_ping_window.gui` | rarely | Frame and header restyled (v0.5, make_panels.py); the contents keep the game's layout, moved down clear of the seal, with the shared pieces re-skinned. Still the game's: the theatre group rows, the theatre window. | sheet |

### Restyled: moved clear of the medallion only

| Screen | Files (`interface/`) | How often | What the Deco UI does, and what is still the game's | Picture |
|---|---|---|---|---|
| Advisor and law picker, subjects, exiles (beside politics) | `countrypoliticsview.gui` | often | Moved flush under the band beside the politics screen (make_politics.py). The game's layout on the core skin's tile (tiled_plain_bg); the subject and collaboration rows are the game's pictures. | sheet |
| Selected armies (army badges, division list) | `unitview.gui` | every session | armies_view moved below the medallion (v0.8.2, make_mapviews.py). The badges' parchment, the expeditionary forces and the colour picker are the game's; the division list's frame is the core skin's. Not yet seen after the move. | sheet |
| Selected fleets | `naviesview.gui`, `navyleaderview.gui` | often | Moved below the medallion and made 77 % tall (v0.8.4), with the home base and refit windows beside it. The fleet headers, task force rows and admirals' cards are the game's; the cards' strips are the army bar's recoloured pieces. Not yet seen. | sheet |
| Selected air wings | `airselectionview.gui`, `airgroupview.gui`, `airwingdetails.gui`, `airwingreorganization.gui`, `carrierairwingcompositionwindow.gui` | sometimes | air_selection_view moved below the medallion (v0.8.2). The rest is the game's: the air wing reorganisation window sits on the core skin's tile, the quick deployment and carrier windows on the game's tiled_window_w_close. | not rendered: the game fills its lists in |
| Selected operatives | `operativeleader.gui` | sometimes | operative_view moved below the medallion (v0.8.2). The operative badges and mission bar are the game's. | sheet |
| Ships and planes in the field, equipment overview, character list | `detailedwindows.gui`, `equipmentoverview.gui`, `command_character_view.gui` | sometimes | Moved flush under the band where they open beside a side panel (v0.5, layout_panels.BESIDE). The game's layout on the core skin's tiles. | sheet |
| Hot-join requests (multiplayer host) | `hotjoin.gui` | rarely | Moved below the medallion (v0.9); otherwise the game's. | not rendered: an empty list until someone asks to join |

## Re-skinned

### Re-skinned: its own pictures redrawn

| Screen | Files (`interface/`) | How often | What the Deco UI does, and what is still the game's | Picture |
|---|---|---|---|---|
| Map modes (lower right) | `mapmodes_interface.gui` | every session | v0.5 textures at the game's paths (mm_*): a lacquer column, line-icon medallions for land, air, naval and intelligence, the game's small icons and toggles recoloured in gilt, the find and 'all' buttons, the configure list. The layout is the game's. | sheet |
| Minimap | `minimap.gui` (Valsora's) | every session | The handle, ping buttons and pings are the Deco UI's (v0.5); the picture and frame are the Valsora build's, drawn in the deco style when DECO_UI is on (gilt land on lacquer in a gilt frame, scripts/minimap.py). The .gui is Valsora's (its window moved for the 2:1 picture), not the Deco UI's. | sheet |
| Tooltips | `core.gui` (ToolTip) | every session | The core skin: the tooltip frame (tiles_dialog.dds: lacquer with a gilt rule) and the game's tooltip font redrawn in Josefin Sans (v0.8). The tooltips' layout and icons are the game's. | sheet |
| The game's own fonts (every screen) (global) | `gfx/fonts` (28 fonts) | every session | v0.8 (game_fonts.py): the game's 28 fonts redrawn in the deco faces at their paths, a size or two smaller so the game's boxes still fit; only Latin letters (the game's Cyrillic and CJK files stay its own). | sheet |
| Division designer | `divisiondesignerview.gui` | sometimes | v0.9 (designer_art.py): the popup picture redrawn at the game's path and size: lacquer plates, recessed panels, an ivory ruled sheet under the statistics. Lists, buttons and icons are the game's. In game (v0.9); the statistics' dark ink (v0.9.1) not yet seen. | sheet |
| Tank designer | `tank_designer_view.gui`, `equipmentdesigner/tanks/` (253 blueprints) | sometimes | v0.9: the popup picture redrawn as the division designer's. The tank blueprints (253 files) and modules are the game's. | sheet |
| Plane designer | `plane_designer_view.gui`, `equipmentdesigner/planes/` (8 blueprints) | sometimes | v0.9: the popup picture redrawn. The plane blueprints and modules are the game's. | sheet |
| Ship designer | `equipmentdesignerview.gui`, `equipmentdesigner/ships/` (6 hulls) | sometimes | v0.9: the popup picture redrawn. The hull drawings and modules are the game's. | sheet |
| Commander pickers (army, navy, captured) | `unitleaderwindow.gui` | sometimes | v0.9: the window and the cards redrawn: parchment cards with a lacquer portrait well. The traits and lists are the game's. | sheet |
| Advisor role picker | `advisorroleselectionview.gui` | rarely | Shares the commander picker's window picture and card (leader_selection_bg, v0.9). | sheet |

### Re-skinned: framed by the core skin

| Screen | Files (`interface/`) | How often | What the Deco UI does, and what is still the game's | Picture |
|---|---|---|---|---|
| Pause menu | `ingamemenu.gui` | every session | Its frame is the core skin's window tile and its buttons the core skin's, so the whole menu reads as deco; the social icons are the game's. The layout is the game's. | sheet |
| Save and load games, saved game rules | `ingamemenu.gui`, `savedgamerules.gui` | every session | The core skin's tiles and buttons; the game's layout. | sheet |
| Diplomatic requests and other popups | `popupwindow.gui` | often | The standard request popups (accept or decline, foreign manpower, lend-lease requests) sit on the core skin's tile; the confirmation and peace summary popups on the game's tiled_window_pol_goal, the lend-lease rows on the game's pictures. | sheet |
| Notifications | `notifications/notification.gui`, `notifications/legacy_message_popup_window.gui`, `notifications/idea_expired_notification.gui`, `notifications/externally_completed_focus.gui` | often | The notification cards on the core skin's tile; the message popup and the idea-expired and focus-completed notices draw no frame of their own (inferred). | sheet |
| Find (province and unit search) | `findview.gui` | sometimes | The core skin's window tile and buttons; the header's icons are the game's. | sheet |
| Military-industrial organisations | `military_industrial_organization/` (5 files) | sometimes | The list, policy and detail windows on the core skin's tile; the organisation tree's background (MIO_details_background) and the save and load popups are the game's. The tree's links share the focus tree's gilt link textures. | sheet |
| Special projects and scientists | `special_projects/` (7 files) | sometimes | The facility, scientist and history rosters on the core skin's tiles; the programme window (projects_bg) and the output window are the game's paper. | sheet |
| International market's other windows | `international_market/` (its 9 other files) | sometimes | The purchasable equipment, stockpile and subsidies windows on the core skin's tile; the purchase draft and add-equipment windows on the game's lend-lease picture, the access and automation windows on the game's tiled_window_w_close. | sheet |
| Combat log, garrison log, naval losses | `combatlogview.gui`, `garrisonlogview.gui`, `naval_losses.gui`, `destroyedshipswindow.gui` | rarely | The frames on the core skin's tile; the combat log's paper pages and the garrison log's picture are the game's. | sheet |
| Multiplayer lobby and chat | `playerlobby.gui`, `chat.gui` | rarely | The core skin's tile; the game's layout. | sheet |
| Achievements | `achievements.gui` | rarely | The body on the core skin's tile; the header with its trophies is the game's. | sheet |
| Music player | `musicplayer.gui`, `music_station_base.gui`, `music_station_classic.gui` | rarely | The window on the core skin's tile; the station covers and the parchment track list are the game's (Valsora Radio's faceplate, valsora_music_station.gui, is the Valsora build's). | sheet |
| Credits | `frontendcreditview.gui`, `credits.gui` | rarely | The core skin's tile and button; the emblem overlay is the game's. | sheet |
| Paradox account dialogs, browser, store messages | `pdx_online/` (2 files), `pops_login.gui`, `browser.gui`, `subscription_message_view.gui` | rarely | The account dialogs on the core skin's tile; the in-game browser (browser_bg) and the store messages are the game's. | not attempted: rarely seen |
| Railway guns | `railway_gun.gui` | rarely | The list on the core skin's thin-bordered tile; the stats window is the game's. | sheet |
| Naval headquarters roster | `building_roster/` (3 files) | rarely | The roster on the core skin's tile; the headquarters rows (naval_hq_entry) are the game's. | not attempted: rarely seen |
| Balance of power | `powerbalanceview.gui` | never (Valsora has none) | The core skin's tile; Valsora defines no balance of power, so it never opens. | not attempted: never opens in Valsora |

## Game's own

| Screen | Files (`interface/`) | How often | What the Deco UI does, and what is still the game's | Picture |
|---|---|---|---|---|
| Unit counters and map icons | `mapicons.gui` | every session | Unit counters, map icons, the naval mission panels: the game's (the HQ badge is the army bar's recoloured one). | not rendered: drawn on the map by the game |
| Loading screen | `load_screen.gui` | every session | The game's loading pictures and status bar. Four loading screens from Valsora's map are a proposal (art/proposals/loading_screens/), not in the mod. | not rendered: the picture is chosen at run time |
| Game setup: country selection | `frontendgamesetupview.gui` | every new game | The game's country selection picture and details panel; only the buttons and fonts change. | sheet |
| Game setup: start (scenario) selection | `frontendgamesetupview.gui` | every new game | The game's window (select_date_bg) and parchment; the start's picture is Valsora's (the Valsora build draws it in the deco style), the buttons and fonts the Deco UI's. | sheet |
| Battle plan toolbar | `battleplantools.gui` | often | The game's pictures and icons. | sheet |
| Right-click menu | `rightclickmenu.gui` | often | Names no pictures; only the redrawn game fonts touch it. | not attempted: it names no pictures |
| Diplomatic action windows | `countrydiplomacyview.gui` (its action windows), `factions/faction_popup.gui`, `operative.gui` | often | Declare war, justify, volunteers, lend-lease, guarantee and the rest keep the game's pictures (generic_diplo_action_bg and the diplo_action_* set); only buttons and fonts change. They sit in a file the Deco UI ships, but only the diplomacy panel itself was changed. | sheet |
| Land battle | `landcombat.gui` | often | The battle window's own picture (land_battle_bg) and the tactics cards are the game's; only the title font and the close button change. | sheet |
| Division and ship details | `unitview.gui` (army_division_stats_view, ship_stats_window) | sometimes | In a file the Deco UI ships (for the armies view's move), but these windows are unchanged: the game's parchment and frame, the deco fonts. | sheet |
| Naval battle and results | `navalcombat.gui`, `navalcombatresultswindow.gui` | sometimes | The game's battle map and report pictures. | sheet |
| Air missions over a region | `strategicairview.gui` | sometimes | The game's picture (strategic_air_bg) and mission icons. | sheet |
| Naval region view | `naval_strategic_region_view.gui` | sometimes | The game's picture (naval_region_window_bg). | sheet |
| Theatres and army groups | `theatreselector.gui` | sometimes | The game's (a transparent window over its own entry pictures). | not rendered: the game fills it in |
| Commander trait trees | `armytraittreewindow.gui`, `navytraittreewindow.gui`, `traittreewindow_common.gui` | sometimes | The game's parchment and tree pieces; the core skin's tabs. | sheet |
| Commander abilities | `abilitylist.gui` | sometimes | The game's. | not attempted: a small list of the game's icons |
| Trade offer (beside trade) | `countrytradeview.gui` (tradeoffer_window) | sometimes | The game's picture (trade_offer_popup_win); its trade partners box picks up a core skin tile, so the window mixes the two looks. | sheet |
| Agency upgrades, name and logo | `countryintelligenceagencyview.gui` (its upgrade and logo windows), `countryintelledger.gui` | sometimes | The game's pictures (agency_branch_upgrades_popup_bg, tiled_window_insigna). | sheet |
| Operations (La Résistance) | `operationoverview.gui` | sometimes | The game's paper and frame. | sheet |
| War overview | `waroverview.gui` | sometimes | The game's. | not rendered: the game fills it in |
| Peace conference | `peaceconferencewindow.gui`, `ingameclock.gui` | sometimes | The game's; only its chat and waiting windows use the core skin's tiles, and the biddings popup the game's world tension picture. The clock window (ingameclock.gui) shows during it (inferred from its offsets). | not rendered: the game fills it in |
| World tension history | `worldtensionwindowpopup.gui` | rarely | The game's picture (world_tension_bg); the body picks up a core skin tile. | sheet |
| Equipment variant designer | `equipmentupgradedesignerwindow.gui` | sometimes | The game's picture (equipment_upgrade_designer_bg). | sheet |
| Design save, load and folder popups | `equipmentdesigner/persistent_design_popups.gui` | sometimes | The game's popup picture (pol_goal_popup_bg). | sheet |
| Message log, message icons, end of game | `menubar.gui` | rarely | The game's. | not rendered: the game fills it in |
| Settings (options) | `settings.gui`, `messagesettings.gui`, `msg_filters.gui`, `playeraiprefs.gui` | rarely | The game's picture (settings_popup_bg); the core skin's buttons and checkboxes. | sheet |
| Multiplayer: host, join, server browser | `frontendmultiplayerview.gui`, `matchmaking.gui`, `matchmaking_chat.gui`, `ingamelobby.gui` | rarely | The game's pictures (hosting_bg ...); the join window is on a core skin tile. | sheet |
| Career profile | `career_profile/` (10 files) | rarely | The game's. | sheet |
| Friends and social | `frontend_friends_view.gui`, `social_view.gui` | rarely | The game's. | not attempted: rarely seen |
| Aces | `acesview.gui` | rarely | The game's tiled_window_w_close. | sheet |
| Insignia, faction logo and colours | `insigniaselection.gui`, `factions/faction_customization.gui` | rarely | The game's pictures. | sheet |
| Faction research facility | `factions/faction_research.gui` | rarely | The game's tiled_window_pol_goal. | not attempted: rarely seen |
| Raids | `military_raids/` (2 files) | rarely | The game's pictures (raids_launch_bg ...); the setup view is on a core skin tile. | sheet |
| Tutorial and hints | `tutorialscreen.gui` | rarely (Valsora's tutorial is cut to one step) | The game's pictures (tutorial_bg, hint_bg). | sheet |
| Shared templates (scroll bars, sliders, widgets) (global) | `core.gui`, `widgets/` (3 files), `divisions_summary.gui` | every session | Pieces other screens draw. The scroll bars and sliders are the game's: the core skin has no texture for them. | not a window of its own |
| Developer tools (console, AI trace, nudge) | `core.gui` (console), `ai_trace.gui`, `backend.gui`, `nudge.gui`, `integrity/file_integrity_watermark.gui` | never (developer) | The game's (the AI trace window happens to be on a core skin tile). | not attempted: developer tools |
| Earth countries' scripted windows (24 files) | `AST_*`, `CZE_*`, `GER_*`, `JAP_*`, `RAJ_*`, `SIA_*`, `ast_*`, `aus_*`, `bul_*`, `ger_*`, `gre_*`, `raj_*`, `sia_*`, `sov_*`, `swe_*`, `usa_*`, `war_escalation_*`, `insrevolutionwindow.gui` | never (Earth content) | Vanilla's country-specific decision windows; no Valsora country uses them. | not attempted: never seen in Valsora |

## Suggested next

The screens a player meets most that are still in the game's style, most often seen first, with what restyling each
would involve. "Small" is a few textures in `gen_textures.py`; "medium" is a set of pictures drawn at the game's sizes
(as the army bar's were), perhaps with a `make_*.py` for a few positions; "large" needs a mockup and a re-laid `.gui`.

1. **Loading screen** (every session; `load_screen.gui`). Four loading screens from Valsora's map are already drawn
   and waiting for the author's approval (`art/proposals/loading_screens/`); adding them means writing them at the
   game's paths (`gfx/loadingscreens/load_<n>.dds`, 1920 x 1440, with their `_small` twins), and the status bar
   (`Loadingscreen_loadingstatus.dds`, 1400 x 92) and progress bar could be redrawn in gilt. Small.
2. **Scroll bars and sliders** (every screen with a list; `core.gui`'s `standardlistbox_slider` and its kin). No core
   skin texture covers them: `scroll_drager`, `scroll_up`, `scroll_down` (16 x 16), the track and the slider bars
   (`slider_bg`, 404 x 42 ...). About ten small textures at the game's paths and sizes. Small, and seen everywhere.
3. **Selected armies, fleets and operatives** (every session and often; `unitview.gui`, `naviesview.gui`,
   `operativeleader.gui`, which `make_mapviews.py` already ships). The army badge (`army_group_bg`, 437 x 109, and the
   army group's), the division count plates, the fleet header (`fleet_bg`, 493 x 166, and its highlight) and the
   operative badge (437 x 109) redrawn at the game's sizes as the army bar's cards were, their buttons recoloured with
   `gilt()`. Medium: about a dozen pictures whose bars and buttons sit at fixed places.
4. **Battle plan toolbar** (often; `battleplantools.gui`). The toolbar picture (`battleplantools_bg`, 641 x 79), the
   area defence and planning panels, and about 25 order and setting buttons (70 x 34 and 80 x 36, several frames
   each) that `gilt()` could recolour as it did the small map mode icons. Small to medium.
5. **Land battle** (often in a war; `landcombat.gui`). One large picture (`land_battle_bg`, 567 x 617) with the leader
   frames, progress frames and tactic cards, redrawn at the game's sizes with the terrain picture's slot kept (the
   terrain pictures stay the game's). Medium; re-laying it to a mockup would be a `make_landcombat.py` and large.
6. **Diplomatic action windows** (often; the action windows in `countrydiplomacyview.gui`, `factions/faction_popup.gui`,
   `operative.gui`). Twenty-three pictures (`generic_diplo_action_bg` and 22 `diplo_action_*_bg`, 527 px wide, 315 to
   664 tall), each the same frame with its own header picture. One frame per height with a gilt line-art header per
   action would cover them. Medium to large: it needs a decision on the header pictures first.
7. **Game setup: country and start selection** (every new game; `frontendgamesetupview.gui`). The country selection
   picture (`country_selection_bg`, 1225 x 728), the start's window (`select_date_bg`, 579 x 512) and the details panel
   (`lobby_right_sidepanel_bg`, 492 x 301) with their parchment panels. Medium as textures; large as a re-laid screen.
   It is the first screen after the main menu.
8. **The window frames the core skin misses** (sometimes, but across many windows). `tiled_window_w_close` (8 windows:
   aces, the doctrine picker, the faction list, the market's access and automation windows, three air windows),
   `tiled_window_pol_goal` and `pol_goal_popup_bg` (14: the confirmation and peace summary popups, the design and MIO
   save popups), `hint_bg` (26 tutorial and hint windows) and `world_tension_bg` (3). Four or five textures in the core
   skin section of `gen_textures.py`; each one restyles several windows at once. Small.

Left out on purpose: the unit counters and map icons (`mapicons.gui`, every session, but 148 sprites the engine draws in
many frames and sizes on the map: large), and the side panels' own pictures, whose proposals wait for the author
(`art/proposals/panel_pictures/`: "I don't want to move ahead with the panel pictures just yet").
