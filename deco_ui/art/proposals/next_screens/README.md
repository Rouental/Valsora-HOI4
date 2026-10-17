# The next screens: proposals (not in the mod)

Mockups of every screen `docs/SCREEN_INVENTORY.md` (2026-10-17, v0.10) still lists as the game's own, plus its
suggestions after v0.10: the unit counters on the map, the division and ship details, the commanders' trait trees, the
war overview, the peace conference, operations, raids, the multiplayer, career profile and friends screens and the
achievements' header. A surprise for the author, drawn on 2026-10-17: **nothing here is in the mod**, and nothing in
`valsora_deco_ui/`, `tools/` or the Valsora build was changed to make them.

Each picture is a whole 1920 x 1080 screen. The windows are at the game's size and place, and they hold the boxes,
lists and buttons the game's own `.gui` files give them. `guilayout.py` read those files (`deco_ui/reference/vanilla/interface/`)
and laid each window out as the game would, so a restyle could go in later as textures at the game's paths and, where
the screen needs it, a patched `.gui` that keeps every element. The art is the Deco UI's: lacquer, gilt hairlines,
stepped corners, octagon medallions, the line icons (`tools/icons.py`), the deco fonts, jade for lit and selected,
oxblood and slate for attacker and defender (the land battle's, v0.10), and an ivory sheet wherever the game writes in
its dark typewriter ink. The top bar is the Deco UI's own preview (`build/preview_topbar.png`), so each screen sits in
the interface the author already has. The sample content is Valsora's: Rouental's Royal Host at war with Cardonia,
Serelle Cahun (her skill and stats from `common/characters/ROU.txt`), Roland II Cahun, the Association, Cardonia's
state names, 2036's equipment from `docs/TECH_TREE_2036.md` (the Char Royal, modular rifles, Gen 5 carrier fighters,
attack drones).

| | Picture | Screen | The game's files |
|---|---|---|---|
| 1 | `unit_counters.png` | Unit counters and map icons | `mapicons.gui` |
| 2 | `unit_counters_key.png` | The same pieces three times as large, named (a key, not a screen) | `mapicons.gui` |
| 3 | `division_details.png` | Division details | `unitview.gui` (army_division_stats_view) |
| 4 | `ship_details.png` | Ship details | `unitview.gui` (ship_stats_window) |
| 5 | `army_trait_tree.png` | A general's trait tree | `armytraittreewindow.gui`, `traittreewindow_common.gui` |
| 6 | `navy_trait_tree.png` | An admiral's trait tree | `navytraittreewindow.gui`, `traittreewindow_common.gui` |
| 7 | `abilities.png` | Commander abilities | `abilitylist.gui` |
| 8 | `theatres.png` | Theatres and army groups | `theatreselector.gui` |
| 9 | `right_click_menu.png` | The right-click menu | `rightclickmenu.gui` |
| 10 | `operations.png` | Operations (La Résistance) | `operationoverview.gui` |
| 11 | `war_overview.png` | War overview | `waroverview.gui` |
| 12 | `peace_conference.png` | Peace conference | `peaceconferencewindow.gui` |
| 13 | `raids.png` | Raids (Götterdämmerung) | `military_raids/` |
| 14 | `messages.png` | The diplomatic message icons | `menubar.gui` (diplomessageicons_window) |
| 15 | `end_of_game.png` | End of game | `menubar.gui` (endgame_dialog) |
| 16 | `server_browser.png` | Multiplayer: the server browser | `matchmaking.gui`, `frontendmultiplayerview.gui` |
| 17 | `multiplayer_host.png` | Multiplayer: hosting a game | `frontendmultiplayerview.gui` (multiplayer_host_window) |
| 18 | `career_profile.png` | Career profile | `career_profile/` |
| 19 | `friends.png` | Friends | `frontend_friends_view.gui` |
| 20 | `achievements.png` | Achievements | `achievements.gui` |

`overview.png` shows them all on one sheet. Not drawn: the developer tools (console, AI trace, nudge) and Earth's 24
scripted windows, which never open in Valsora (the inventory's own judgement), and a few windows seen once in a long
while: the in-game clock (`ingameclock.gui`, one 228 x 42 picture), the chat windows of `social_view.gui`, the career
profile's Awards and Badge tabs, the message log.

## The suggested order

Most often seen first, and where the game gives every hook:

1. **The unit counters and map icons** (every session). Their twenty-odd pictures first (counters, battles, bases, the
   victory points), which change the map's whole look; the unit type icons (about 450 small pictures) as a second step.
   The commander abilities (small) go with them: they sit over the army bar.
2. **The division and ship details** (sometimes). Medium; they share the designers' look (v0.9) and pieces.
3. **The commanders' trait trees** (sometimes). Medium; the trait pictures can stay the game's at first.
4. **The theatres** (often, once the player uses theatres). Medium.
5. **The war overview, then the peace conference** (every war, every war's end). Medium, then large.
6. **Operations and raids** (sometimes, with their DLCs). Medium each.
7. **The right-click menu and the diplomatic message icons**. Small; quick wins.
8. **The end of game** (once a campaign). Medium.
9. **Achievements, then multiplayer, friends and the career profile** (rarely). Small to medium each.

Every restyle below is textures at the game's paths, sizes and frame counts (the Deco UI's usual way: an art module
in `tools/`, a key prefix of its own, a preview beside the game's), plus a `.gui` patch only where a box has to move or
a text needs one of the mod's own fonts. The game's text there is already in the deco faces (v0.8). "Assumed" means it
is read from the files but not seen in game.

## Per screen

### 1-2. Unit counters and map icons (`mapicons.gui`; every session)

**What changes.** The army counter becomes a lacquer chip with a gilt hairline (the Main board's counter): an icon well
with the division's type in gilt line art and the small flag (10 x 7, where the game puts it), the count in a dark well,
the ideology as a narrow pennant at the right end, organisation (jade) and strength (amber) as two hairlines under the
well; selected, a bright gilt ring and a jade glow (the army bar's selected colour); the army HQ a gilt pennant badge;
moving, attacking, dug in and training marks as small gilt roundels, no orders an amber hexagon, out of supply and
attrition coral. Allies and enemies take a slate or coral rim (the game's counter is one picture for all, so this needs
the engine's own colouring: see the hooks). The fleet's counter stacks capital ships over screens, its mission in a jade
medallion and its spotting as a slim gauge; air wings are slate-rimmed. A land battle is an octagon medallion with
crossed swords, its inner ring split oxblood and slate by the battle's progress, the percentage on a plate under it,
the direction a chevron; a naval base an anchor medallion with ten level pips; an air base a slate jet; a supply hub a
gilt diamond; a naval mission a slate hexagon with its count and efficiency. The victory points are the Main board's
gilt diamonds and capital star (as on the backdrop).

**Files and textures.** `gfx/interface/onmap_unit_counter.dds` (198 x 27, 3 frames), `onmap_unit_counter_ideology.dds`
(112 x 27, 4: democratic, communist, fascist, neutral), `onmap_unit_counter_overlay.dds` (30 x 20),
`onmap_unit_counter_selected.dds` (68 x 28), `mapicons/mapicon_bar_org_sprite.dds` and `_str_` (3 x 17),
`onmap_naval_unit_counter.dds` (222 x 36, 3), `onmap_unit_counter_overlay_navy.dds` (30 x 29),
`onmap_mission_unit_counter_types.dds` (260 x 26, 10 missions), `onmap_action_icon.dds` (168 x 12, 14 orders),
`unitcontrol/supply_strip.dds` (72 x 24, 3), `onmap_digin_icon.dds`, `onmap_in_training_icon.dds`, `onmap_attrition.dds`,
`mapicons/mapicon_unit_no_orders.dds`, `mapicon_area_defense_shield.dds`, `mapicons/mapicon_land_combat.dds` (38 x 37) and
`_frame` (76 x 37, 2), `battle_indicator_direction.dds` (70 x 70), `landcombat/battle_modifier_strip.dds` (shared with the
land battle), `mapicons/mapicon_naval_combat.dds` (80 x 33, 2), `mapicon_building_navalbase.dds` (301 x 29, 11 levels),
`mapicon_building_airbase.dds` (189 x 30, 7), the supply hub's strips (`mapicons/supply/`), `onmap_victorypoints_strip.dds`
(580 x 27, 20 frames), and the type icons: `counters/divisions_small/` (83 files of 60 x 12, 2 frames),
`counters/divisions_large/` (115), the templates' (2 x 101), `ships_small/` (22), `air_small/` (26) and
`strategicair/wing_types_map.dds` (1440 x 12, 48 planes). The unit counter's `.gui` needs no change for the textures;
moving the bars or the flag would be a `mapicons.gui` patch (the Deco UI ships none yet).

**Hooks.** The pictures, yes, at their paths. Not given, or not known: the flag stripe is "set in code to proper flag"
(`mapicons.gfx`), so its size and place are the engine's; the organisation and strength bars' place is the engine's
too (their positions in the file, 14,8 and 14,12, cannot be where they show: assumed placement under the well); a
counter's rim colour by side (own, ally, enemy) is not a hook (the game has one counter picture, recoloured by the engine
for selection only; drawn here as a suggestion: only the hatched second frame tells something apart); Valsora's fifth
ideology (Theocratic) has no frame of its own in the four-frame ideology strip. The type icons' frame order and meaning
must be kept (the map mode icons' rule, `deco_ui/CLAUDE.md` section 9).

**Work.** Large: about twenty textures for the counters, battles and bases (a few days), then the ~450 type icons (a
script drawing them from a glyph per unit type, like the line icon set; a week).

### 3. Division details (`unitview.gui`, army_division_stats_view; sometimes)

**What changes.** The window as the designers (v0.9): a lacquer frame with a double gilt rule; the left part's header band
with the gilt title, the template upgrade mark, the owner's flag; the identity row's wells (type, the name field, the
experience and its level as a gilt diamond with chevrons); the three columns of statistics on the ivory ruled sheet in
dark ink; the hardness bar in gilt over slate; the terrain adjusters as small lacquer cards, each terrain a gilt line
drawing with its movement, attack and defence chips in jade, gilt or coral; the Stats, History and Template tabs as the
core skin's; the right column's officer card (arched portrait well, Promote) and the equipment list (archetype headers as
lacquer bars, each equipment's picture in a well).

**Files and textures.** `unit_stats_bg.dds` (856 x 497), `unit_stats_view_tabs.dds` (226 x 36, 2),
`unit_stats_list_entry2.dds` (268 x 32), `unit_stats_template_tab_bg.dds`, `army_hq_unit_details_bg.dds`,
`transparent_equipment_bg.dds`, `unit_level.dds` (135 x 27, 5), `unitlist_priority_icon_strip.dds` (48 x 23, 3),
`softness_ratio_frame.dds` (207 x 27), `softness_ratio_armour.dds` (194 x 11), `terrain_mod_frame.dds` (70 x 62),
`terrain_mod_movement_strip.dds` and its attack and defence strips (63 x 21, 3 frames), the terrain pictures (`forest_icon.dds`
..., 45 x 45, shared with the division designer), `naviesview/btn_delete.dds` (31 x 31; `btn_close.dds` is the Deco UI's
already). The stats' typewriter text is dark, so the sheet stays light. `unitview.gui` is already a file of the Deco UI
(`make_mapviews.py`): fonts or positions here would be one more patch in it.

**Hooks.** Yes, all of it. The equipment pictures and the officer's portrait are the game's (its 3D renders and generated
portraits): they stay, drawn here as gilt line stand-ins.

**Work.** Medium (the designers' pieces carry over).

### 4. Ship details (`unitview.gui`, ship_stats_window; sometimes)

**What changes.** As the division's: the same frame, header, sheet and right column, the captain's card and the carrier's
air wings (rows in lacquer, an ace's star on jade); the lower field (the game's blue sea) a dark slate well with faint
swell lines, the class's name in gilt over its picture, the pride of the fleet toggle as a jade medallion, the support
and dominance readouts, the naval terrain (deep, shallow, fjords, arctic) as small cards.

**Files and textures.** `naval_unit_stats_bg.dds` (856 x 409), `air_unit_stats_equip_entry.dds` (268 x 45),
`naviesview/btn_pride.dds` (114 x 37, 3), `naviesview/naval_dominance_support_strip.dds`, the naval terrain pictures,
and the division's shared pieces.

**Hooks.** Yes. One fix needs the `.gui`: in the game's file the pride button (698, 585) lies over the support readout's
icon (705, 605); the mockup moves the two readouts right of it (a `unitview.gui` patch). The ship's picture is the game's.

**Work.** Medium, done together with the division details.

### 5-6. The commanders' trait trees (`armytraittreewindow.gui`, `navytraittreewindow.gui`, `traittreewindow_common.gui`; sometimes)

**What changes.** The window (1340 x 778) in the lacquer frame, the header band with the gilt title, the Traits and Officer
Corps Roles tabs as the core skin's large tabs; the left column's portrait in a gilt frame, the skill on the commander
cards' diamond (v0.10.1), the four stats as small octagons with their numbers under them, the experience as a gilt bar,
the active traits under gilt section titles; the tree's plates (166 x 39) as chamfered lacquer: picked jade with a gold
rim, pickable bright with a gilt diamond at the corner, locked dim; the links gilt, dashed where they lead from a trait not
yet earned; the terrain traits in a recessed well. The navy's tree is the same window with its own columns.

**Files and textures.** `trait_window/trait_tree_bg.dds` (1343 x 783), `trait_disabled.dds`, `trait_pickable.dds`,
`trait_picked.dds` (166 x 39 each), the lines (`trait_line_left.png` ... and their dotted ones), `trait_exclusive.png`,
`trait_separator.dds` (272 x 5), `trait_new.dds` (35 x 43), `trait_wiki.dds`, `unitcontrol/unit_leader_portrait_frame.dds`,
`unitcontrol/trait_attack.dds` (27 x 25) and its defence, planning, logistics, manoeuvring and coordination siblings,
`officer_corp/preferred_tactic_button.dds`; the skill badge (`land_battle_leader_skill_bg.dds`) is the Deco UI's already
(v0.10). The trait pictures (`gfx/interface/traits/`, 99 files) can stay the game's, or be redrawn as gilt line glyphs
like the mockup's (large).

**Hooks.** Yes: the tree's geometry is the game's (each trait's `gui_row` and column in `common/unit_leader/00_traits.txt`,
40 px a row), and the plates, lines and frame are pictures at the game's paths. The stats' numbers under their icons
are a `.gui` move (in the game's file they overlap their icons). The army's links in the mockup follow each trait's row,
not its real parents (the game's file gives them; a build would draw what the game draws).

**Work.** Medium; large with the trait pictures.

### 7. Commander abilities (`abilitylist.gui`; sometimes)

**What changes.** The bar over the army bar as a chamfered lacquer plate with a gilt rule and end diamonds; each ability
an octagon medallion with a gilt line glyph, active ones jade with a jade ring that empties as the ability runs, those
cooling down dimmed with a dark wedge; the core skin's tooltip.

**Files and textures.** `abilitylist/bg_begin.dds`, `bg_mid.dds`, `bg_end.dds` (99 x 45, 36 x 45, 99 x 45),
`ability_active_bg(_full).dds` and `ability_cooldown_bg(_full).dds` (33 x 33, the progress pair), the ability pictures
(about 20, 33 x 33).

**Hooks.** Yes. The list starts at the screen's centre (centre-down, x -5) and grows right, as the file says (assumed:
whether the engine centres it was not seen).

**Work.** Small.

### 8. Theatres and army groups (`theatreselector.gui`; often with theatres)

**What changes.** Each theatre's button (198 x 39) as a lacquer bar, jade when selected, its name in the display face,
its units' count in a gilt octagon, the pin as a gilt line pin, the priority as three amber diamonds on a dark plate,
its alerts as pennants to its left (amber for orders and HQ, coral for supply and battles); an expanded theatre's army
groups as framed cards: settings, name, supply priority chevrons, attacks and defences (swords and shield), the armies'
insignia as gilt shields, the count.

**Files and textures.** `theatre_selection_background.dds` (594 x 39, 3), `unitcontrol/theatre_selection_frame.dds`
(184 x 47), `theatre_selection_unit_indicator.dds` (37 x 34), `pinned_theatre_checkbox.tga` (2), `theatre_priority_bg.tga`,
`priority_strip.dds` (4), `theater/theater_group_bg.dds` (1525 x 77, 5), `selected_theatre_frame.dds`,
`assign_group_button.dds` (1196 x 35, 4), `theater_group_settings_btn.dds`, `theatre_battle_indicator.dds` (2),
`theatre_combat_logs_icon.dds` (2), `theatre_dropdown_middle/bottom.dds` (4), `theatre_settings_bg.dds`,
`div_priority_strip.dds` (6), `alerts/theater_alerts_strip.dds` (14 alerts).

**Hooks.** Yes. The armies' insignia are `army_icons/army_icons.dds` (81 shields the player picks, shared with the
insignia picker): the game's, unless they are redrawn too.

**Work.** Medium.

### 9. The right-click menu (`rightclickmenu.gui`; often)

**What changes.** The list's frame is already deco: its background, `SandboxFloaterBackground`, is the tooltip's tile
(`tiles_dialog`, the Deco UI's since v0.4.8; the inventory had it as naming no pictures). What is left is its entries:
`button_type_4` (218 x 32) as a row with a gilt diamond, jade when hovered, and `button_type_9` (105 x 32, the Open
button) as a small core skin button.

**Files and textures.** `gfx/interface/button_type_4.dds` and `button_type_9.dds` (`core.gfx` names `.tga` files; the
game ships the `.dds`, which it loads first: `deco_ui/CLAUDE.md` section 6). They have other users, which would change
with them: `button_type_4.dds` is also the advisor role picker's buttons (`GFX_advisor_role_button`, a screen the Deco UI
re-skinned in v0.9) and the developer nudge tool's, `button_type_9` the community chat's Send button.

**Hooks.** Yes. What the engine puts in the menu, and when it opens, is its own (the entries drawn are a plausible set).

**Work.** Small.

### 10. Operations (`operationoverview.gui`; sometimes, La Résistance)

**What changes.** The dossier in a lacquer frame: the target's well with the operation's emblem as a gilt medallion, the
target's flag and its location; the duration and outlook bars in gilt; the required resources' rows; the operatives'
gilt-framed portraits; the clipboard (the phases, their circular progress, the outcome) as the ivory sheet with dark ink;
the reward on a lacquer plate with a jade medallion; the foot's start button in gold.

**Files and textures.** `tiled_paper_w_frame_bg.dds` (shared: check its other users first), `operations/operations_target_info_bg.dds`
(254 x 94), `operations_clipboard_top_bg.dds`, `_mid_`, `_bottom_` (500 x 129 / 126 / 209), `circular_progress_bar_bg.dds`
(64 x 64) and the 2- and 3-phase bars, `list_entry_bg.dds`, `operation_progress_bar_frame.dds`, `reward_bg.dds`
(500 x 74), `reward_icon.dds`, `bottom_start.dds` (752 x 40), `refund_operation.dds`, `operation_complete_stamp.dds` (2),
`clip.dds`, `generic_checkbox3.dds`. The operations' own emblems (`operations/*.dds`, about 20) are the game's pictures.

**Hooks.** Yes; the typewriter text is dark, so the clipboard stays light.

**Work.** Medium.

### 11. War overview (`waroverview.gui`; sometimes)

**What changes.** The war's tabs as lacquer tabs over the frame (jade the shown one); the war's name in gilt capitals; the
war score as a gilt-framed bar, the attackers' oxblood against the defenders' slate with a gilt diamond at the line; the
filters as the core skin's sort buttons; each side's header of icons as small gilt glyph chips over an oxblood or slate
rule; the faction rows as lacquer bars, each country's row with its flag, a major's gilt diamond, its surrender as a
coral hairline, the war goal in amber, the figures.

**Files and textures.** `waroverview_bg_tiled.dds` (1168 x 506), `war_overview_progress_disabled.dds`,
`warscore_progressbar.dds` (579 x 26), `warscore_progressbar_frame.dds` (591 x 38), `waroverview_tabs_all.dds` (94 x 51, 2),
`sort_button_140x29.dds` (280 x 29, 2; shared with the peace conference), the header icons (`participants_icon`,
`wargoal_icon`, `surrender_icon`, `warscore_icon`, `division_icon`, `industrial_capacity_icon`, `casuality_icon`: 2 frames
each), `war_faction_entry.dds` (537 x 42), `war_participant_entry.dds` (1593 x 41, 3), `not_in_war_ally.dds`,
`surrender_progress(_frame).dds`, `small_flag_frame_thin2.dds`, `major_country_flag_overlay.dds`,
`stop_training_leadergroup_button.dds` (the Call button).

**Hooks.** Yes. The window's height is "85%" of the screen from y 243 by the file's numbers, which would run past the
bottom (inferred; the mockup ends it at y 1043).

**Work.** Medium.

### 12. Peace conference (`peaceconferencewindow.gui`; at every war's end)

**What changes.** The top bar as the Deco UI's band with the gilt title and a gold Confirm and Exit; the top art (580 x 100)
as a stepped gilt plate with a sunburst and a medallion ("Victors' Conference"); the current turn's plate (the speaker's
flag, score, world tension) and the conference turn under it; the side panels in lacquer frames: Make Demands with its
description, the demands' buttons as chamfered squares (jade the chosen one) with gilt glyphs, the losers' and their
states' rows (the state's cost in gilt, contested and war goal marks), the victors' cards with their bids; the reset and
submit plates. On the map, each state's cost on a dark gilt-rimmed plate, the claimant's flag above it.

**Files and textures.** `tiles/tiled_peace_upper_bar.dds` (363 x 96 tile), `peace_conference/top_art_winning_conference.dds`
(580 x 100) and its losing twin, `conference_action_header.dds` (319 x 49), `buttons/icon_button_46x46.dds` (92 x 46, 2),
`load_save_entry2.dds` (624 x 54, 2; shared with the save games), `peace_conference/conference_action_entry_bg.dds`
(1204 x 29, 4), `pc_victory_entry.dds` (624 x 84, 2), `delimeter_entry.dds`, `peace_drop_down_icon.dds` (2),
`peace_action_bottom.dds` (341 x 83), `main_lobby_button.dds` (864 x 36, 3; shared with the lobby), `peace_turn_bg.dds`
(515 x 65), `generic_text_bg_154.dds`, `players_icon.dds`, `accept_decline_icon.dds` (3), `texticons/peace_conf_icons.dds` (3).

**Hooks.** Mostly. Some demand buttons name sprites other screens use (`GFX_decision_eng_propaganda_campaigns`, the
`industry` and `resources_to_market` text icons): those would be swapped in the `.gui` for sprites of our own, not
replaced. The side panels slide in from off-screen (shown positions assumed: x 0 and 1580). The cost labels are text in
the game's font on the map.

**Work.** Large (many pieces, several shared).

### 13. Raids (`military_raids/`; sometimes, Götterdämmerung)

**What changes.** The planning window in the lacquer frame; the raiders' and the target's pictures as dark wells (the
game's are terrain photographs: here gilt line drawings); the likelihood of success as a gilt-framed dial with a jade
arc, the disaster risk on a coral plate; the additional equipment on the ivory sheet; the risk toggles as gilt-rimmed
switches; the preparation bar in gilt; the launch keys and a red octagon launch button; the core skin's buttons and
checkbox.

**Files and textures.** `military_raids/raids_launch_bg.dds` (638 x 598), `success_chance_display.dds` (210 x 80),
`raids_toggle_switch.dds` (100 x 84, 2), `raids_launch_keys.dds` (282 x 70, 3), `raids_launch_button_single.dds`,
`raids_loading_bar_fill/frame.dds`; `play_button.dds` is the Deco UI's already (game setup, v0.10). The raid map icons
and `raid_map_details_window.gui` are the same pieces.

**Hooks.** Yes. The terrain and target pictures are the game's.

**Work.** Medium.

### 14. The diplomatic message icons (`menubar.gui`; often)

**What changes.** Each waiting request (access, an invitation, peace, lend-lease, a call to arms) as a lacquer pennant
with a gilt line glyph in its kind's colour and the sender's flag, along the lower left; the core skin's tooltip.

**Files and textures.** `alerticon_banner2.dds` (1060 x 90: 20 frames of 53 x 90, one per kind; their order and meaning
kept), `flag_smallest_overlay.dds`.

**Hooks.** Yes. The menu bar's other message icons (combat, government, trade, event: `message_icons`) look unused in
1.19 (its notifications are `notifications/`, re-skinned already: inferred), so they are not drawn.

**Work.** Small.

### 15. End of game (`menubar.gui`, endgame_dialog; once a campaign)

**What changes.** A frame where the game draws none (its background is a 3 x 3 clear tile): the flag in a gilt frame, the
score in gilt, the ruler's portrait in an arched gilt frame, the country's facts, its formal name in gilt capitals, the
factions' table; the ladder as a lacquer plate, the Country and Faction filters as tabs, the six sorts as medallions,
the countries in four columns with their flags.

**Files and textures.** `leader_frame_0_75.dds` (136 x 181), `large_flag_frame.dds` (92 x 58), `ladder_background.dds`
(1285 x 502, drawn at 0.9), `career_profile/button_filter_end_screen(_long).dds` (3), `endgame_score_button.dds` and
its army, navy, air, industry and province siblings (51 x 52). The frame needs a `.gui` change (a background for
endgame_dialog, a tile of the core skin).

**Hooks.** Yes, with that one `.gui` change.

**Work.** Medium.

### 16-17. Multiplayer (`matchmaking.gui`, `frontendmultiplayerview.gui`, `matchmaking_chat.gui`, `ingamelobby.gui`; rarely)

**What changes.** The browser in the lacquer frame over the menu's picture, the Servers and Community tabs, the filters'
checkboxes and fields, the list's sort headers as the core skin's, its rows (a padlock in gilt, the status in jade or
amber), the foot's buttons with Join in gold; the host window the same way.

**Files and textures.** `matchmaking_browser_bg.dds` (1024 x 576), `MP_matchmaking_tabs.dds` (374 x 52, 2),
`matchmaking_browser_list_item_bg.dds` (1944 x 30, 2), `sort_89.dds`, `sort_134.dds`, `sort_246.dds`, `password_icon.dds`,
`edittextbox_bg1.dds` (shared), `hosting_bg.dds` (480 x 432). The buttons and checkboxes are the core skin's already.

**Hooks.** Yes.

**Work.** Medium.

### 18. Career profile (`career_profile/`, 10 files; rarely)

**What changes.** The tabs over the frame, the header's picture panel with a sunburst, the profile picture in a gilt
hexagon, the name and career points, the visibility switch and the game's note; the filters as wells; the statistics as
framed lacquer cards with small gilt corners.

**Files and textures.** `career_profile/career_profile_bg.dds` (1170 x 790), `button_tab.dds` (516 x 50, 2),
`button_close.dds`, `tiled_bg.dds`, `career_profile_bg_default.dds` (1160 x 80), `btn_dropdown.dds`, `btn_expand_isolated.dds`,
`career_checkbox.dds`, `btn_blue.dds`, `tiled_stats_bg.dds` (362 x 225), the navigation arrows; the Awards tab's medals and
ribbons and the profile backgrounds and badges are the game's pictures (the player's rewards).

**Hooks.** Yes. Its seven `.gfx` and the 7,246-line `common_components.gui` make it the largest of the rare screens.

**Work.** Medium to large; rarely seen.

### 19. Friends (`frontend_friends_view.gui`; rarely)

**What changes.** The friend cards in lacquer, the picture in a gilt hexagon over a sunburst, the name in the display face,
the status in jade or grey, View Profile as the core skin's button.

**Files and textures.** `career_profile/social_bg.dds` (1170 x 790), `tiled_stats_bg.dds`, `button_tab.dds`.
`social_view.gui` (the chat windows) is not drawn.

**Hooks.** Yes.

**Work.** Small.

### 20. Achievements (`achievements.gui`; rarely)

**What changes.** The inventory's last piece of it: the header with its trophies (gilt cups and speed lines in place of the
game's), the entries as lacquer plates, a got achievement's medallion jade, the progress on a dark plate, the foot band.
(The list's frame and well are the core skin's already.)

**Files and textures.** `achievements_top_bar.dds` (765 x 67), `achievements_bottom_bar.dds` (765 x 48),
`achievement_entry_bg.dds` (729 x 96). The achievements' pictures are the game's. The entries drawn are Valsora-flavoured
samples: what the window lists is the game's own (or a mod's, through `common/achievements`).

**Hooks.** Yes.

**Work.** Small.

## The files here

- `make.py` draws everything (about two minutes): `CHROMIUM_PATH=/opt/pw-browsers/chromium python3 make.py`, or
  `python3 make.py division_details` for one screen. It needs `deco_ui/build/preview_topbar.png` (drawn by
  `tools/build_all.py`; without it the screens have no top bar) and the game's files in `deco_ui/reference/vanilla`.
- `deco.py` holds the shared pieces (the palette, the core skin's window, bands, wells, bars, buttons, tabs, the ivory sheet,
  medallions, flags and portraits, the backdrop, the renderer), `guilayout.py` the reader for the game's `.gui` and `.gfx`
  (`python3 guilayout.py unitview.gui ship_stats_window` prints a window's boxes; `--render OUT` draws the game's look into
  `deco_ui/build/`), and `screens_units.py`, `screens_commanders.py`, `screens_war.py`, `screens_frontend.py` one function
  per screen.
- The pictures here are 256-colour PNGs, to keep the repository light; `deco_ui/build/next_screens/full/` has them at full
  colour, and `deco_ui/build/next_screens/compare_<screen>.png` sets eleven of them beside the screen inventory's picture of
  the game's look. Those stay in the git-ignored `build/`: they hold the game's art.
- Nothing here holds the game's art: the map, the boards' unit glyphs and the line icons are the project's, the flags and
  portraits the author's (`source/flags/`, `source/portraits/`), the generic officers' portraits gilt silhouettes.

To put an approved screen in: move its drawing into an art module in `tools/` (`<screen>_art.py`, `ADDS` at the game's
paths and sizes, a key prefix of its own), add a preview beside the game's, and, where the screen needs one, a `make_*.py`
that patches its `.gui` with `guipatch` and keeps every element.
