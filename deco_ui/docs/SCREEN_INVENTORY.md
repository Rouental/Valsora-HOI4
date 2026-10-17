# Screen inventory

2026-10-17, Deco UI v0.9.1, brought up to date for v0.10 the same day (the rows it changed say v0.10; their pictures are
the screens' previews in `deco_ui/build/`). Every screen of the game, grouped by how far the Valsora Deco UI has changed it, so the next
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
- Re-skinned: 45 (28 with their own pictures redrawn, 19 of them in v0.10; 17 framed by the core skin)
- Game's own: 16 (of which 2 never seen in Valsora: Earth's scripted windows, the developer tools)

(v0.9.1: 34 restyled, 26 re-skinned, 35 the game's own.)

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
| Selected armies (army badges, division list) | `unitview.gui` | every session | armies_view moved below the medallion (v0.8.2, make_mapviews.py); v0.10: the badges, plaques, frames and buttons redrawn (mapview_art.py). Before that, the badges' parchment, the expeditionary forces and the colour picker are the game's; the division list's frame is the core skin's. Not yet seen after the move. | sheet |
| Selected fleets | `naviesview.gui`, `navyleaderview.gui` | often | Moved below the medallion and made 77 % tall (v0.8.4), with the home base and refit windows beside it. The fleet headers, task force rows and admirals' cards are the game's; the cards' strips are the army bar's recoloured pieces. Not yet seen. | sheet |
| Selected air wings | `airselectionview.gui`, `airgroupview.gui`, `airwingdetails.gui`, `airwingreorganization.gui`, `carrierairwingcompositionwindow.gui` | sometimes | air_selection_view moved below the medallion (v0.8.2). The rest is the game's: the air wing reorganisation window sits on the core skin's tile, the quick deployment and carrier windows on the game's tiled_window_w_close. | not rendered: the game fills its lists in |
| Selected operatives | `operativeleader.gui` | sometimes | operative_view moved below the medallion (v0.8.2); v0.10: the badge and its bar redrawn (mapview_art.py). The mission bar is the game's. | sheet |
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
| Loading screen | `load_screen.gui` | every session | v0.10: four pictures from Valsora's map in the background list (make_loading.py), which the loading screen draws from (assumed); the loading bar, tip and progress bar in gilt (ld_). | build/preview_loading.png |
| Game setup: country selection | `frontendgamesetupview.gui` | every new game | v0.10 (setup_art.py): the country selection picture, the country cards with a flag opening, the filter buttons, the facts and history on ivory (the game's typewriter text is black), the details panel, the difficulty and Start buttons, the map screen's bars. The faction emblems and the top bar's flag frame are the game's. | build/preview_setup.png |
| Game setup: start (scenario) selection | `frontendgamesetupview.gui` | every new game | v0.10: the start's window (select_date_bg) and the start cards redrawn; the start's picture is the Valsora build's. | build/preview_setup.png |
| Battle plan toolbar | `battleplantools.gui` | often | v0.10 (battleplan_art.py): the bar's wells, the pop-ups (planning speed, cohesion, HQ distance, area defence), the order and setting buttons with the game's glyphs in gilt, the execution and exercise strips. | build/preview_battleplan.png |
| Diplomatic action windows | `countrydiplomacyview.gui` (its action windows), `factions/faction_popup.gui`, `operative.gui` | often | v0.10 (diplo_art.py): 22 pictures and their pieces, a deco frame with a gilt line emblem per action at both ends of the title plate; the war goal lists on ivory and the dark panels as lacquer wells (core skin). The licence window's filter buttons and the threat box are the game's. | build/preview_diplo.png |
| Land battle | `landcombat.gui` | often | v0.10 (combat_art.py): the battle window (terrain slot, a medallion per side, tactic slots, width readouts, division fields), the leader and progress frames, bars, cards, the skill badge, the tactics list. The terrain and tactic pictures are the game's. | build/preview_landcombat.png |
| Naval battle and results | `navalcombat.gui`, `navalcombatresultswindow.gui` | sometimes | v0.10: the naval battle's picture (an ivory plotting sheet under the ships), its leader frame, bars, screening chips and stat icons (combat_art.py). The results window's report pictures are the game's. | build/preview_navalcombat.png |
| Air missions over a region | `strategicairview.gui` | sometimes | v0.10 (popup_art.py): the window's picture (name band, wing cells, weather well, missions field); the mission icons are the game's. | build/preview_popups.png |
| Naval region view | `naval_strategic_region_view.gui` | sometimes | v0.10 (popup_art.py): the picture, its header and the dominance bar; the terrain picture is the game's. | build/preview_popups.png |
| Trade offer (beside trade) | `countrytradeview.gui` (tradeoffer_window) | sometimes | v0.10 (popup_art.py): the offer's picture and its footer plate; the partners box is a core skin tile. | build/preview_popups.png |
| Agency upgrades, name and logo | `countryintelligenceagencyview.gui` (its upgrade and logo windows), `countryintelledger.gui` | sometimes | v0.10 (popup_art.py): the upgrades popup's head and the logo window (army_insignia_selection_bg). The intelligence ledger's pieces are the game's. | build/preview_popups.png |
| World tension history | `worldtensionwindowpopup.gui` | rarely | v0.10 (window_art.py): world_tension_bg with roundels, a title plate and a band for the sort buttons; the list on a core skin tile. | build/preview_windows.png |
| Equipment variant designer | `equipmentupgradedesignerwindow.gui` | sometimes | v0.10 (popup_art.py): the picture, the statistics on an ivory sheet (dark typewriter ink); the market's stockpile window shares it. | build/preview_popups.png |
| Design save, load and folder popups | `equipmentdesigner/persistent_design_popups.gui` | sometimes | v0.10 (window_art.py): pol_goal_popup_bg as a deco frame with a header band. | build/preview_windows.png |
| Settings (options) | `settings.gui`, `messagesettings.gui`, `msg_filters.gui`, `playeraiprefs.gui` | rarely | v0.10 (popup_art.py): the window, its frame, tabs and tab arrows, option rows, the volume sliders, the gold checkbox. | build/preview_popups.png |
| Aces | `acesview.gui` | rarely | v0.10 (window_art.py): tiled_window_w_close with a socket for the close button (also the doctrine picker, the faction list, the market's access and automation windows, three air windows). | build/preview_windows.png |
| Insignia, faction logo and colours | `insigniaselection.gui`, `factions/faction_customization.gui` | rarely | v0.10 (popup_art.py): the pickers' window (army_insignia_selection_bg); the paper backgrounds are the game's. | build/preview_popups.png |
| Faction research facility | `factions/faction_research.gui` | rarely | v0.10: its frame is tiled_window_pol_goal (window_art.py). | not attempted: rarely seen |
| Tutorial and hints | `tutorialscreen.gui` | rarely (Valsora's tutorial is cut to one step) | v0.10: hint_bg (window_art.py) and tutorial_bg (popup_art.py): roundels, a title plate, an objectives band. | build/preview_windows.png, preview_popups.png |
| Shared templates (scroll bars, sliders, widgets) (global) | `core.gui`, `widgets/` (3 files), `divisions_summary.gui` | every session | v0.10: the scroll bars and sliders (sc_ in gen_textures.py: arrows, thumb, tracks, backdrops, the value slider). | not a window of its own |

### Re-skinned: framed by the core skin

| Screen | Files (`interface/`) | How often | What the Deco UI does, and what is still the game's | Picture |
|---|---|---|---|---|
| Pause menu | `ingamemenu.gui` | every session | Its frame is the core skin's window tile and its buttons the core skin's, so the whole menu reads as deco; the social icons are the game's. The layout is the game's. | sheet |
| Save and load games, saved game rules | `ingamemenu.gui`, `savedgamerules.gui` | every session | The core skin's tiles and buttons; the game's layout. | sheet |
| Diplomatic requests and other popups | `popupwindow.gui` | often | The standard request popups (accept or decline, foreign manpower, lend-lease requests) sit on the core skin's tile; since v0.10 their header strips, footer plates and the confirmation's war medallions are deco too, and the confirmation and peace summary popups' tiled_window_pol_goal (window_art.py); the lend-lease rows are the game's pictures. | sheet; build/preview_popups.png |
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
| Right-click menu | `rightclickmenu.gui` | often | Names no pictures; only the redrawn game fonts touch it. | not attempted: it names no pictures |
| Division and ship details | `unitview.gui` (army_division_stats_view, ship_stats_window) | sometimes | In a file the Deco UI ships (for the armies view's move), but these windows are unchanged: the game's parchment and frame, the deco fonts. | sheet |
| Theatres and army groups | `theatreselector.gui` | sometimes | The game's (a transparent window over its own entry pictures). | not rendered: the game fills it in |
| Commander trait trees | `armytraittreewindow.gui`, `navytraittreewindow.gui`, `traittreewindow_common.gui` | sometimes | The game's parchment and tree pieces; the core skin's tabs. | sheet |
| Commander abilities | `abilitylist.gui` | sometimes | The game's. | not attempted: a small list of the game's icons |
| Operations (La Résistance) | `operationoverview.gui` | sometimes | The game's paper and frame. | sheet |
| War overview | `waroverview.gui` | sometimes | The game's. | not rendered: the game fills it in |
| Peace conference | `peaceconferencewindow.gui`, `ingameclock.gui` | sometimes | The game's; only its chat and waiting windows use the core skin's tiles, and the biddings popup the world tension picture (deco since v0.10). The clock window (ingameclock.gui) shows during it (inferred from its offsets). | not rendered: the game fills it in |
| Message log, message icons, end of game | `menubar.gui` | rarely | The game's. | not rendered: the game fills it in |
| Multiplayer: host, join, server browser | `frontendmultiplayerview.gui`, `matchmaking.gui`, `matchmaking_chat.gui`, `ingamelobby.gui` | rarely | The game's pictures (hosting_bg ...); the join window is on a core skin tile. | sheet |
| Career profile | `career_profile/` (10 files) | rarely | The game's. | sheet |
| Friends and social | `frontend_friends_view.gui`, `social_view.gui` | rarely | The game's. | not attempted: rarely seen |
| Raids | `military_raids/` (2 files) | rarely | The game's pictures (raids_launch_bg ...); the setup view is on a core skin tile. | sheet |
| Developer tools (console, AI trace, nudge) | `core.gui` (console), `ai_trace.gui`, `backend.gui`, `nudge.gui`, `integrity/file_integrity_watermark.gui` | never (developer) | The game's (the AI trace window happens to be on a core skin tile). | not attempted: developer tools |
| Earth countries' scripted windows (24 files) | `AST_*`, `CZE_*`, `GER_*`, `JAP_*`, `RAJ_*`, `SIA_*`, `ast_*`, `aus_*`, `bul_*`, `ger_*`, `gre_*`, `raj_*`, `sia_*`, `sov_*`, `swe_*`, `usa_*`, `war_escalation_*`, `insrevolutionwindow.gui` | never (Earth content) | Vanilla's country-specific decision windows; no Valsora country uses them. | not attempted: never seen in Valsora |

## Suggested next

All eight suggestions of v0.9.1 (the loading screen, the scroll bars and sliders, the selected armies' badges, the
battle plan toolbar, the land battle, the diplomatic action windows, game setup, the window frames the core skin missed)
were done in v0.10, with the naval battle, the popups' headers and footers and the windows of one picture seen now and
then (settings, trade offer, the variant designer, the agency, the insignia pickers, air missions, the naval region,
the tutorial). Still the game's, most often seen first:

1. **Unit counters and map icons** (`mapicons.gui`, every session): 148 sprites the engine draws in many frames and
   sizes on the map. Large.
2. **Division and ship details** (`unitview.gui`'s army_division_stats_view and ship_stats_window, sometimes): the
   game's parchment and frame. Medium, as the designers' were.
3. **Commander trait trees** (`armytraittreewindow.gui`, `navytraittreewindow.gui`, sometimes): the parchment and
   tree pieces. Medium.
4. **Operations, the war overview, the peace conference** (sometimes): the game's papers and frames; the peace
   conference fills itself in. Medium to large.
5. **Multiplayer, career profile, raids, achievements' header** (rarely). Medium each.

Left out on purpose: the side panels' own pictures, whose proposals wait for the author
(`art/proposals/panel_pictures/`: "I don't want to move ahead with the panel pictures just yet").
