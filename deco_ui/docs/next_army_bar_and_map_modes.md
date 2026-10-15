# The army bar (done in v0.7) and the bottom-right map controls (done in v0.5)

**Done in v0.7 (2026-10-15):** the army bar, by textures at the game's paths (`gen_textures.py`, `lg_*`, numbers in
`tools/layout_armybar.py`) and `make_leadergroups.py` (the counts on the plaques); preview
`build/preview_armybar.png` (`preview_armybar.py`). The plan below is kept as the record of how it was approached.

**Done in v0.5 (2026-10-14): map modes and minimap**, by textures at vanilla paths only (the game's
`mapmodes_interface.gui` and Valsora's `minimap.gui` are untouched); `gen_textures.py`, the `mm_*` and `mn_*`
sprites; preview `build/preview_corner.png` (`preview_panels.py`). What the game's textures turned out to be:

| texture | size, frames | what it is |
|---|---|---|
| `mapmode/mapmode_main_bg.dds` | 87x206 | the column behind the buttons (at the container's x 549: its last 5 px are off-screen) |
| `mapmode/mapmode_bottom_bg.dds` | 86x59 | its foot, under the six toggles (2 rows of 3, 25 px apart) |
| `mapmode/mapmode_buttons_(de)selected_big.dds` | 136x31, 4 | soldier (land), plane (air), anchor (naval), eye |
| `mapmode/mapmode_button_bg.dds` | 42x51 | the well behind each big button (the button sits 4 px in, 10 down; wells overlap) |
| `mapmode/mapmode_buttons_(de)selected_small.dds` | 360x18, 18 | `?` `?` `?`, eye, flag, cards, flame, pennant, sack, hill, star, two figures, a figure carrying, three figures, fist in a wreath, arrows, crosshair, blank (meanings not written anywhere: kept, recoloured) |
| `mapmode/mapmode_button_depressed.dds` | 23x20 | the well behind a selected small button and behind every toggle |
| toggles (`day_night_toggle`, `player_counters_toggle`, `counters_color_mode_button`, `allied_plans_button`, `fog_of_war_toggle`, `radar_toggle`) | 44x22, 2 | frame 1 coloured (on), frame 2 grey |
| `mapmode/find_screen_button.dds`, `mapmode_button_all.dds`, `mapmode_configure_bg.dds` | 39x39; 44x21, 2; 519x23, 3 | find; "<" (all map modes); the configure list's rows (plain, lit, with a chevron) |
| `sort_button_83x29.tga` | 166x29, 2 | the social button over the column (frame 2 lit); replaced by a `.dds` of the same name |
| `gfx/minimap/handle_default/pinged.dds`, `*_ping_btn.dds`, `minimap_ping_*.dds` | 24x64; 64x31, 2; ~22x22 | the minimap's slide handle, its two ping buttons, the pings on it |

The game shows either `3_button_mapmode` or `4_button_mapmode` (the 3-button one also holds a fourth button
over the third). Still to check in game: the toggles' on/off frames and the selected states.


The user's request after testing v0.2 was: *"The armies at the bottom of the screen, and the filters
on the bottom right don't have the same custom touch as the rest of the UI."*

The first session had the game's `interface/` folder but none of its textures. It therefore could not
see these elements' frame sizes, frame order or where the portraits sit inside the art, and it
deferred them. This instance should have the install (`HOI4_DIR`), so start by reading the
textures.

## Files involved

| Screen part | .gui | .gfx (sprite definitions) | Textures |
|---|---|---|---|
| Army bar: army and army group portraits along the bottom, execute/stop buttons, plan bars, division counts | `interface/leadergroups.gui` | `interface/leadergroups.gfx` (and `unitview.gfx` for a few) | `gfx/interface/unitcontrol/*` |
| Map mode buttons (bottom right): 3/4 big buttons plus a column of small ones, day/night, counters, fog, radar, find | `interface/mapmodes_interface.gui` | `interface/topbar.gfx`, `interface/mapmodes_interface.gfx` | `gfx/interface/mapmode/*` |
| Minimap (bottom right, collapsible) | `interface/minimap.gui` | various | `gfx/minimap/*` |

Container anchors: `MapmodesInterface_Ingame` is LOWER_RIGHT at (-631,-244), and
`mini_map_interface` is LOWER_RIGHT at (-343,-98).

## Known facts

- `leader_groups_portrait_window` is 68x97 in the .gui. The portrait frames measured about 74x98 in
  the user's v0.2 screenshot, because the frame overhangs.
- `GFX_LG_group_frame` and `GFX_leader_group_frame_selected` use the same texture
  (`leader_group_frame.dds`, 4 frames, `alwaystransparent`). The army group version has 3 frames.
- The leader portrait icon is at (8,-5) with `scale = 0.39`. The pending one is at `scale = 0.15`.
- `army_group_bg`, `army_mid_bg` and `army_end_bg` (2 frames each) are drawn at (-1,-46) / (1,-46)
  and form the backing strip behind a run of armies.
- `GFX_execute_button_play_small` / `stop_small` (and their `_ag` versions) have 4 frames.
  `GFX_LG_select_group_btn` and `GFX_hq_alert` are 2-frame `frameAnimatedSpriteType`s.
- Map mode icons are frame strips: `mapmode_buttons_(de)selected_big` has 4 frames and `..._small`
  has 18. The engine picks a frame per map mode, so a replacement must keep the **same icon
  order**. Read the vanilla strips to learn which frame is which mode.
- Toggle buttons (day/night, counters, fog of war, radar, allied plans) have 2 frames, probably
  off/on. Check this in game.
- `GFX_minimap_world` is `gfx/minimap/minimap.dds`, a static picture of the world. The copy of the
  Valsora mod the first session saw had **no `gfx/minimap/`**. Since 2026-10-13 Valsora draws its own
  (`scripts/minimap.py` in the main mod: 194x97 parchment, its frame `border.dds` 205x105, the window
  moved to x = -274 and `MINIMAP_TOGGLE_SHIFT` 202; **in game** 2026-10-14). Style around it: keep
  Valsora's picture and window size, or redraw both together (the picture comes from the map).
- Vanilla's sizes, read from the game files on 2026-10-14: minimap 268x97, border 276x105, map-mode
  panel 75 px wide to its right (the window's x = -343 = -(268 + 75)).

## Plan

1. **Look at the vanilla textures first.** Open each texture in the tables below with Pillow
   (vanilla DDS are mostly DXT-compressed: `Image.open` handles DXT1/3/5; `tools/ddsutil.read_dds`
   only reads our own uncompressed files). Record size, frame width and what each frame shows.
   Write the findings into this doc.
2. **Re-skin by replacing textures at their vanilla paths** wherever the shape can stay, which is
   most of the army bar and every map mode button. This needs no .gui change and survives patches.
   Keep the exact canvas size and frame count. Keep the opaque area where vanilla has it, because
   other elements are positioned against it, for example the portrait inside the frame. Add each
   texture to `gen_textures.py` with its vanilla path, and add it to the
   "replaced vanilla textures keep vanilla sizes" table in `validate_preview.py`.
   - Army bar style: an arched or octagonal gilt portrait frame like the politics portrait, in
     miniature, with a jade "selected" frame. The backing strips become a lacquer plate with a gilt
     rule. Execute/stop become small gilt diamonds (like the pause diamond in the date cartouche),
     and plan bars use the gilt ratio bar look.
   - Map modes style: a stepped lacquer plate (like the top bar's right plate, mirrored to hang from
     the bottom-right corner). Big buttons become octagonal medallions, and small ones become
     chamfered chips with the 24px line icon set from `gen_textures.ICON`. New icons are needed for
     the 18 + 4 map modes. Selected means a jade fill and a bright gilt rim.
3. **Only if the layout must change**, add `tools/make_leadergroups.py` / `make_mapmodes.py`. Patch
   the game's .gui with `guipatch`, keep every element, and use fonts from `valsora_deco_fonts.gfx`
   (for example `divisions_count` in `valsora_deco_value_12`). The element-name check in
   `validate_preview.py` covers the new files automatically.
4. Add previews to `preview_screens.py`: a bottom strip with three armies and an army group, and the
   bottom-right corner. Use stand-ins for portraits.
5. Things to ask the user to check in game:
   - selected, hover and disabled states
   - the battle plan animation (`active_battleplan_anim`, 12 frames) still reads
   - map mode tooltips still line up with the icons
   - the minimap handle

## Sprite tables (from the game's interface/*.gfx)


### leadergroups.gui (sprites used: 45)

| sprite | kind | texture | frames |
|---|---|---|---|
| GFX_attached_air_bg | spriteType | gfx/interface/attached_air_bg.dds | 1 |
| GFX_attached_air_types | spriteType | gfx/interface/strategicair/attached_air_types.dds | 5 |
| GFX_railway_gun_assign_to_army | spriteType | gfx/interface/assign_railway_gun_to_army.dds | 3 |
| GFX_LG_army_group_bg | spriteType | gfx/interface/unitcontrol/army_group_back_bg.dds | 2 |
| GFX_LG_army_mid_bg | spriteType | gfx/interface/unitcontrol/army_mid_bg.dds | 2 |
| GFX_LG_army_end_bg | spriteType | gfx/interface/unitcontrol/army_end_bg.dds | 2 |
| GFX_group_add_leader_bg | spriteType | gfx/interface/unitcontrol/group_add_leader_bg.dds | 1 |
| GFX_LG_select_group_btn | frameAnimatedSpriteType | gfx/interface/unitcontrol/group_add_leader.dds | 2 |
| GFX_leader_unknown | spriteType | gfx/leaders/leader_unknown.dds | 1 |
| GFX_opinion_arrow_right | spriteType | gfx/interface/opinion_arrow_right.dds | 1 |
| GFX_leader_en_route | spriteType | gfx/interface/leader_en_route.dds | 1 |
| GFX_LG_group_frame | spriteType | gfx/interface/unitcontrol/leader_group_frame.dds | 4 |
| GFX_leader_group_frame_selected | spriteType | gfx/interface/unitcontrol/leader_group_frame.dds | 4 |
| GFX_hq_alert | frameAnimatedSpriteType | gfx/interface/unitcontrol/hq_alert.dds | 2 |
| GFX_LG_disband_group_btn | spriteType | gfx/interface/unitcontrol/disband_orders_group.dds | 1 |
| GFX_group_marker2 | spriteType | gfx/interface/unitcontrol/group_marker2.dds | 1 |
| GFX_execute_stop_small_bg | spriteType | gfx/interface/unitcontrol/execute_stop_small_bg.dds | 1 |
| GFX_excecute_stop_border_war_bg | spriteType | gfx/interface/unitcontrol/excecute_stop_border_war_bg.dds | 1 |
| GFX_execute_button_play_small | spriteType | gfx/interface/unitcontrol/execute_btn_play_small.dds | 4 |
| GFX_execute_button_execute_order | SpriteType | gfx/interface/unitcontrol/execute_button_no_order.dds | 1 |
| GFX_active_battleplan_anim | frameAnimatedSpriteType | gfx/interface/unitcontrol/active_battleplan_anim.dds | 12 |
| GFX_execute_battle_plan_glow | frameAnimatedSpriteType | gfx/interface/tutorial/execute_battle_plan_glow.dds | 2 |
| GFX_plan_unit_power | progressbartype | gfx/interface/unitcontrol/comm_group_plan_power_bar.dds | 1 |
| GFX_naval_invasion_progress_frame | spriteType | gfx/interface/naval_invasion_progress_frame.dds | 1 |
| GFX_plan_frame | spriteType | gfx/interface/unitcontrol/plan_frame.png | 1 |
| GFX_execute_button_stop_small | spriteType | gfx/interface/unitcontrol/execute_btn_stop_small.dds | 4 |
| GFX_exercise_icon_anim_strip | frameAnimatedSpriteType | gfx/interface/exercise_anim_strip.dds | 20 |
| GFX_exercise_stop_at_max | spriteType | gfx/interface/exercise_icon_stop_at_max_icon.dds | 1 |
| GFX_area_defense_active | spriteType | gfx/interface/area_defense_active.dds | 1 |
| GFX_execute_button_point_out_mode | spriteType | gfx/interface/unitcontrol/execute_button_point_out_mode.dds | 1 |
| GFX_plan_value_strip | spriteType | gfx/interface/plan_value_strip.dds | 4 |
| GFX_LG_expand_group_btn | spriteType | gfx/interface/unitcontrol/army_group_expand_collapse.dds | 2 |
| GFX_new_expedionary_forces_group_button | spriteType | gfx/interface/expedionary_forces_army_button.dds | 1 |
| GFX_expedionary_forces_icon | spriteType | gfx/interface/expedionary_forces_icon.dds | 1 |
| GFX_give_role_leader_strip | frameAnimatedSpriteType | gfx/interface/unitcontrol/give_role_leader_strip.dds | 2 |
| GFX_leader_details_icon_available_trait | frameAnimatedSpriteType | gfx/interface/unitcontrol/leader_details_icon_available_trait.dds | 2 |
| GFX_hq_badge_bg | spriteType | gfx/interface/unitcontrol/hq_badge.dds | 1 |
| GFX_group_add_marshal_bg | spriteType | gfx/interface/unitcontrol/group_add_marshal_bg.dds | 1 |
| GFX_LG_select_group_marshal_btn | frameAnimatedSpriteType | gfx/interface/unitcontrol/group_add_marshal.dds | 2 |
| GFX_leader_marshal_unknown | spriteType | gfx/leaders/leader_marshal_unknown.dds | 1 |
| GFX_LG_army_group_frame | spriteType | gfx/interface/unitcontrol/leader_army_group_frame.dds | 3 |
| GFX_leader_army_group_frame_selected | spriteType | gfx/interface/unitcontrol/leader_army_group_frame.dds | 3 |
| GFX_group_marker4 | spriteType | gfx/interface/unitcontrol/group_marker4.dds | 1 |
| GFX_execute_button_play_small_ag | spriteType | gfx/interface/unitcontrol/execute_btn_play_small_ag.dds | 4 |
| GFX_execute_button_stop_small_ag | spriteType | gfx/interface/unitcontrol/execute_btn_stop_small_ag.dds | 4 |

### mapmodes_interface.gui (sprites used: 25)

| sprite | kind | texture | frames |
|---|---|---|---|
| GFX_sort_button_83x29 | textSpriteType | gfx/interface/sort_button_83x29.tga | 2 |
| GFX_socialview_icon | spriteType | gfx/interface/icons/pi_icon.dds | 1 |
| GFX_new_message_icon | spriteType | gfx/interface/social/new_message.dds | 1 |
| GFX_new_friend_icon | spriteType | gfx/interface/social/new_friend_request.dds | 1 |
| GFX_map_modes_bg | spriteType | gfx/interface/mapmode/mapmode_main_bg.dds | 1 |
| GFX_map_modes_bottom_bg | spriteType | gfx/interface/mapmode/mapmode_bottom_bg.dds | 1 |
| GFX_find_screen_button | spriteType | gfx/interface/mapmode/find_screen_button.dds | 1 |
| GFX_mapmode_button_all | spriteType | gfx/interface/mapmode/mapmode_button_all.dds | 2 |
| GFX_mapmode_button_bg | spriteType | gfx/interface/mapmode/mapmode_button_bg.dds | 1 |
| GFX_mapmode_buttons_deselected_big | spriteType | gfx/interface/mapmode/mapmode_buttons_deselected_big.dds | 4 |
| GFX_mapmode_buttons_selected_big | spriteType | gfx/interface/mapmode/mapmode_buttons_selected_big.dds | 4 |
| GFX_tutorial_default_mapmode_highlight | frameAnimatedSpriteType | gfx/interface/tutorial/default_mapmode_highlight.dds | 2 |
| GFX_logistics_tutorial_glow | frameAnimatedSpriteType | gfx/interface/tutorial/logistics_supply_map_mode_glow.dds | 2 |
| GFX_mapmode_button_depressed | spriteType | gfx/interface/mapmode/mapmode_button_depressed.dds | 1 |
| GFX_mapmode_buttons_deselected_small | spriteType | gfx/interface/mapmode/mapmode_buttons_deselected_small.dds | 18 |
| GFX_mapmode_buttons_selected_small | spriteType | gfx/interface/mapmode/mapmode_buttons_selected_small.dds | 18 |
| GFX_day_night_toggle | spriteType | gfx/interface/mapmode/day_night_toggle.dds | 2 |
| GFX_player_counters_toggle | spriteType | gfx/interface/mapmode/player_counters_toggle.dds | 2 |
| GFX_button_counters_color_mode | spriteType | gfx/interface/mapmode/counters_color_mode_button.dds | 2 |
| GFX_button_allied_plans | spriteType | gfx/interface/mapmode/allied_plans_button.dds | 2 |
| GFX_button_fog_of_war | spriteType | gfx/interface/mapmode/fog_of_war_toggle.dds | 2 |
| GFX_button_toggle_radar | spriteType | gfx/interface/mapmode/radar_toggle.dds | 2 |
| GFX_mapmode_configure_bg | spriteType | gfx/interface/mapmode/mapmode_configure_bg.dds | 3 |
| GFX_tiled_window_small | corneredTileSpriteType | gfx/interface/tiles/tiled_window_small.dds | 1 |
| GFX_button_94x31 | textSpriteType | gfx/interface/button_94x31.tga | 1 |

### minimap.gui (sprites used: 10)

| sprite | kind | texture | frames |
|---|---|---|---|
| GFX_minimap_ping_offensive | spriteType | gfx/minimap/minimap_ping_offensive.dds | 1 |
| GFX_minimap_ping_defensive | spriteType | gfx/minimap/minimap_ping_defensive.dds | 1 |
| GFX_minimap_world | spriteType | gfx/minimap/minimap.dds | 1 |
| GFX_minimap_quad_pixel | spriteType | gfx/minimap/minimap_quad_pixel.dds | 1 |
| GFX_minimap_ping_circle | spriteType | gfx/minimap/ping_circle.dds | 1 |
| GFX_minimap_handle_default | spriteType | gfx/minimap/handle_default.dds | 1 |
| GFX_minimap_handle_pinged | spriteType | gfx/minimap/handle_pinged.dds | 1 |
| GFX_minimap_border | spriteType | gfx/minimap/border.dds | 1 |
| GFX_minimap_offensive_ping_btn | spriteType | gfx/minimap/offensive_ping_btn.dds | 2 |
| GFX_minimap_defensive_ping_btn | spriteType | gfx/minimap/defensive_ping_btn.dds | 2 |
