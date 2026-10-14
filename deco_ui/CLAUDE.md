# Valsora Deco UI: handoff guide for Claude

This file is for a Claude instance picking up the art deco UI mod for **Valsora**, a Hearts of Iron IV
(1.19) total conversion set in Valsora, the world of The East Pacific (a NationStates region). The
mod's author is the user. This folder is the **source project**. `valsora_deco_ui/` is the built mod;
everything else is how it gets built.

The first four versions were made in a cloud session that had no game install. It had only copies of
the game's `interface/` folder, `00_defines.lua` and `00_graphics.lua`. Everything below marked
**(in game)** was confirmed from the user's screenshots. Everything marked **(assumed)** has not been
seen in game yet. Treat assumed items as hypotheses.

---------------------------------------------------------------------------------------------------

## 1. Status (v0.4.4)

v0.4.3 was the first v0.3/v0.4 build the user launched. The user's first report covered only the main
menu: the Valsora background showed **(in game)**, but none of the menu buttons did. v0.4.4 fixes the
button row's anchoring (section 6, Main menu) and moves the social links to the top-left corner.
The rest of v0.3/v0.4 (top bar, politics, state panel, focus tree) has still not been seen in game.

| Area | State |
|---|---|
| Core skin (window frames, tooltips, standard buttons, panel background, map font) | Done. Vanilla textures are replaced at their vanilla paths and sizes. |
| Icons (`tools/icons.py`) | The mockup's 24 px gilt line icons, with modern subjects for army, deployment, air and convoys. Sheet: `build/icon_sheet.png`. |
| Top bar (`interface/topbar.gui`) | Re-laid to the mockup. v0.4: **decisions** is the seal under the flag; **faction** moved into the crown row (first slot). |
| Alerts row (`interface/alerts.gui`) | v0.3: moved below the band, under the menu buttons. |
| Politics screen (`interface/countrypoliticsview.gui`) | v0.4: the Government mockup's layout (no Court panel), with scripted GUIs for what the game's screen lacks. |
| State / province panel (`interface/countrystateview.gui`) | v0.4: the mockup's arrangement for the state part (flag + name header, stats row, slots, buildings); the province part keeps the game's positions. |
| Focus tree (`interface/nationalfocusview.gui`) | v0.4: window chrome, plates, medallions, filters, detail pop-up, legend. Focus icons untouched. |
| Main menu (`interface/frontendmainview.gui` + background) | v0.3; v0.4.4 fixed the invisible button row. Background **(in game)**. |
| Army bar (bottom: `leadergroups.gui`) | **Next.** See `docs/next_army_bar_and_map_modes.md`. |
| Map modes and minimap (bottom right: `mapmodes_interface.gui`, `minimap.gui`) | **Next.** Same doc. |
| Everything else (production, research, events, diplomacy, trade, ...) | Only the core skin so far. A mockup exists for the superevent. |

**HOI4 has no outliner.** The mockup's "Outliner" panel was a design idea. The closest things in the
game are the army/navy/air overview lists (opened from the top bar's army/navy/air buttons); restyle
those if the user wants that look.

Design references: `art/mockups/*.jpg` are 1920x1080 renders of the original mockups (Main = in-game
top bar and map, Government = politics screen, MainMenu, FocusTree, SpriteKit, Superevent). They are
the target. `art/mockups/source/*.html` is the HTML/CSS each board was drawn from, made self-contained
(images in `source/assets/`, fonts from `source_fonts/`). **Read the source for exact sizes,
colours, gradients, letter-spacing and wording** instead of measuring the JPGs, and render it at
1920x1080 with Playwright to compare against a preview. The SpriteKit board lists the intended
sprites, frame states and palette. The user's direction was: *"go all the way. Don't keep the layout
the same as vanilla, go with what you showed in your mockup."*

## 2. How the user works

- They test each release in game at 1920x1080 and send screenshots with a list of what to fix. Expect
  the same loop: build, check, preview, package, then they test.
- Ship a ready-to-install mod (the `valsora_deco_ui/` folder plus `valsora_deco_ui.mod`) and a
  README that says what changed and what to look at in game.
- Show previews (`build/preview_*.png`) before asking them to launch the game. They cost nothing and
  catch most layout mistakes.
- Be honest about what is assumed and what is verified. List the assumed items as "things to check in
  game" in the README.
- Their standing preferences so far:
  - follow the mockup's layout even when that takes more extensive modding and new panels
  - **Valsora is set in the modern day**: icons and art show modern equipment (a high-cut combat
    helmet, jets, modern warships, trucks), never WWII kit
  - icons: the mockup's simple line style. A detailed two-tone set was tried in v0.4 and the user
    did not like it (v0.4.1 went back to line icons), so keep icons as clean line art
  - decisions matter more than factions (decisions got the prominent seal)

## 3. Quick start

Requirements: Python 3.10+, Pillow (built with libraqm, which is needed for kerning:
`python -c "from PIL import features; print(features.check('raqm'))"`), numpy, and Playwright with
Chromium (only for textures: `pip install playwright && playwright install chromium`).

```
python tools/build_all.py                    # everything: fonts, textures, .gui generators, checks, previews
python tools/build_all.py gen_textures.py    # skip the slow texture step (any step names can be listed)
python tools/make_topbar.py                  # one generator (they all default to reference/ paths)
```

`validate_preview.py` must end with `PROBLEMS: none`. Then look at `build/preview_topbar.png`,
`build/preview_politics.png`, `build/preview_stateview.png`, `build/preview_focus.png` and
`build/preview_menu.png`. `python tools/icon_sheet.py` renders every icon to `build/icon_sheet.png`.

Paths come from `tools/paths.py`. Every one can be overridden with an environment variable:

| Variable | Default | Meaning |
|---|---|---|
| `HOI4_DIR` | `reference/vanilla` | The game folder, or a copy of the parts the tools read. Point it at the real install when there is one. |
| `VALSORA_MOD_DIR` | `reference/valsora` | The Valsora mod. Its localisation, tags, ideologies and `countrypoliticsview.gui` are read. |
| `VALSORA_DECO_MOD` | `valsora_deco_ui` | Where the built mod is written. |
| `VALSORA_DECO_ROOT` | the folder above `tools/` | The project root. |

`reference/README.md` says what to copy into `reference/` when there is no install to point at.
**Never ship or commit Paradox files.** `reference/` and `build/` are git-ignored.

## 4. Project map

```
valsora_deco_ui/            the built mod (shipped). Generated, so do not hand-edit .gui/.gfx/.yml here; change the tools
valsora_deco_ui.mod         launcher descriptor (path="mod/valsora_deco_ui")
tools/
  paths.py                  all locations (see above)
  build_all.py              runs every step in order
  gen_fonts.py              BMFont generator (Josefin Sans, Federo) -> valsora_deco_ui/gfx/fonts/*.fnt/.dds, build/font_metrics.json
  gen_textures.py           every texture, drawn as HTML/CSS/SVG, screenshotted by Playwright at exact pixel size -> DDS/TGA
  ddsutil.py                writes and reads uncompressed A8R8G8B8 DDS (our own files only; open vanilla DXT DDS with Pillow)
  guipatch.py               assertive .gui patching by element path (section 6)
  layout.py                 top bar coordinates (screen pixels at 1920x1080); measures text from the generated fonts
  icons.py                  the line icon set: icon(name, size, colour, stroke)
  icon_sheet.py             renders every icon large and at in-game sizes -> build/icon_sheet.png
  layout_politics.py        politics screen coordinates (panel-local)
  layout_stateview.py       state panel zones (the game's positions are kept)
  layout_focus.py           focus tree chrome (plate size, name box, medallion, legend)
  make_topbar.py            topbar.gui + alerts.gui + top bar extras/scripted GUIs/triggers/loc + fonts.gfx + topbar sprites
  make_politics.py          countrypoliticsview.gui + politics scripted GUIs, scripted localisation, trigger, sprites, loc
  make_stateview.py         countrystateview.gui + its sprites
  make_focus.py             nationalfocusview.gui + its sprites
  make_menu.py              frontendmainview.gui + background registration + menu sprites
  validate_preview.py       static checks + a preview renderer that reads the generated .gui/.gfx
  preview_screens.py        politics, state panel, focus tree and main menu previews (imports validate_preview)
source_fonts/               TTFs + OFL licences (Josefin Sans, Federo, Limelight, Bodoni Moda)
art/                        menu_world.jpg (main menu map), map_rouental.jpg + flag_ROU.png (preview backdrops),
                            mockups/*.jpg (renders) and mockups/source/ (the boards' HTML + assets)
docs/                       plans for the next screens
reference/                  vanilla/ and valsora/ inputs (not shipped, not committed)
build/                      intermediates and previews (safe to delete)
```

Build order matters. `gen_fonts` runs first because `layout.py` measures strings with the generated
`.fnt` files. Next comes `gen_textures`, because many texture sizes come from `layout.py` /
`layout_politics.py`. The `make_*` generators follow, then the checks.

## 5. Design language

- **Palette.** Lacquer panels `#11191E` / `#17222A` with faint 8px vertical pinstripes. Darks are
  `#0B1014` and `#0E1519`. Gilt is `#E3C77E` (lines) and `#C9A55A` (rules), and the gilt gradient
  runs `#E8CD84` to `#8B6A2C`. Highlight is `#F1DC9C`. Jade `#2E6E60` marks lit and active states.
  Amber `#E7B75A` and coral `(238,140,126)` are for warnings and lows. Text colours are cream
  `#F4ECD9` and `#E8DFC8`, with `#B7A680` for labels.
- **Shapes.** Chamfered and stepped plates, double gilt corner brackets, sunbursts and speed lines,
  octagons and diamonds, arches for portraits. Every texture is built from HTML/CSS/SVG in
  `gen_textures.py`, so a new element is a new `add(key, path, w, h, html)` call.
- **Type.** Josefin Sans covers numbers, labels and body text, with small tracked capitals for labels.
  Federo covers the date, names, headings and the main menu. Limelight and Bodoni Moda are used only
  inside baked art (the menu title).
- **Icons.** `tools/icons.py`: the mockup's line icons on a 24 grid (stroke 1.4-1.6, round caps,
  gilt `#E3C77E`, lit `#FBEAB4`). 24 px in the crown buttons and readouts, 22 on the army/navy/air
  buttons (raised above the XP badge), 18 in the trays. Modern subjects: high-cut helmet (army), NATO
  division symbol (deploy), delta-canard jet (air), container ship (convoys).
  `gen_textures.svg(name, size, colour, stroke)` draws them.

## 6. Engine facts learned (the important part)

### .gui files

- The engine finds elements **by name**. Never delete or rename a vanilla element. Move it, re-skin
  it, or hide it (sprite `GFX_valsora_deco_none`, a 2x2 transparent texture, or the blank font).
  New elements are fine.
- Type keywords vary in case within vanilla files (`ButtonType`/`buttonType`,
  `instantTextboxType`/`instantTextBoxType`). Always match case-insensitively. `guipatch` does.
- Vanilla files contain typos that the engine tolerates. `countrypoliticsview.gui` has `y = 1s` in
  the pie overlay, which `make_politics` fixes before parsing.
- `Orientation` sets the anchor in the parent. `Origo` sets the anchor point of the element itself.
  **(in game)** `Origo = center` and `lower_left`/`lower_right` work on top-level frontend windows
  (the social links, the DLC column and the change-background button all land where vanilla puts
  them). **(in game)** `Orientation = CENTER_DOWN` plus `Origo = center_down` on the main menu panel
  did **not** work: none of its buttons showed in v0.4.3, most likely because the panel's top-left
  landed at the bottom-centre, below the screen. Do not rely on `center_down`. For bottom-centred
  windows use what vanilla's peace conference chat does: `Orientation = CENTER_DOWN`, no `Origo`,
  and `position = { x = -width/2 y = -(height + margin) }`.
- A width of `100%%` runs to the parent's right edge, so right-anchored top bar elements use
  `gui_x = screen_x - 1920`. **(in game)** The world tension ring landed exactly where planned.
- The top bar container sits at `(-4,-1)`, so `gui = screen + (4,1)` for UPPER_LEFT children
  (`layout.GUI`, `layout.GUI_R`).
- `vertical_alignment = center` works on `instantTextboxType`. **(assumed;** it is used for the
  country name and labels)
- `pieChartType` is drawn centred on x with its top at y, so the centre is `(x, y + r)`. Its `.gfx`
  `size` is the **radius**; the politics pie uses its own `GFX_valsora_deco_pol_chart` (radius 40).
- An element added *before* the vanilla ones in a container draws underneath them. The decorative
  layer in `make_topbar` is inserted first for that reason.

### Sprites and textures

- Replacing a texture **at its vanilla path** is the most patch-proof way to re-skin anything. No
  .gui or .gfx change is needed, and it survives game updates. Keep the exact pixel size and frame
  count. The `.gfx` definition (frames, `borderSize` for cornered tiles, effect files) stays vanilla.
- `noOfFrames` strips are laid out horizontally, each frame `width / frames` wide.
- `progressbartype` ignores `color`/`colortwo` when textures are given. The fill texture is drawn
  as is.
- `corneredTileSpriteType` takes its tile size from `.gfx` (`size`, `borderSize`).
  `GFX_tiled_plain_bg` (192x192, border 64) is the main background of the politics, production,
  research, trade, diplomacy and other side panels, so re-skinning that one texture changes most
  screens.
- **(in game)** The engine swaps `GFX_topbar_international_market` onto `diplomacy_button` at
  runtime, which is why v0.2 showed a vanilla icon there. The fix is to replace the texture
  `gfx/interface/topbar/toolbar/international_market_button.dds` (2 frames) at its vanilla path.
- **Runtime sprite swaps: keep the vanilla sprite name and replace its textures.** Known (or very
  likely, from the sprite names in the .gfx) swaps, all handled this way:
  - `faction_button`: `GFX_topbar_faction_empty` / `GFX_topbar_faction` (in a faction) →
    `gfx/interface/factions/ui/topbar_faction(_empty).dds`, 1 frame. **(assumed)** v0.3 retargeted
    this button to an own sprite, which the swap would have undone.
  - `decision_view_alert_glow`: `GFX_decisions_glow` / `_blue` / `_yellow` / `_green` →
    `gfx/interface/decisionview/decisions_glow*.dds`, 2 frames each (now octagonal halos sized to the
    seal). Vanilla also used the yellow one on `production_button_glow`, which now has its own crown
    glow sprite.
  - focus name plates: `GFX_focus_unavailable` / `_can_start` / `_completed` →
    `gfx/interface/focusview/titlebar/focus_*_bg.dds`. The joint-focus variants stay vanilla.
  - `validate_preview.REPLACED` lists these so previews can draw them.
- **(in game)** Flags are not smoothed when scaled, so any scaling pixelates them. Show them at
  native size. The large flag is 82x52, set by `NDefines_Graphics.NGraphics.COUNTRY_FLAG_TEX_WIDTH/
  HEIGHT = 82/52` ("Expected texture size") with `COUNTRY_FLAG_TEX_MAX_SIZE = 256` ("power of 2, no
  more than 2048; depends on the number of countries"). Medium flags are 41x26 and small ones 10x7.
  A `maskedShieldType` is sized by its mask texture, so the mask is 82x52 (`flag_mask.tga`).
- **HD flags (untested idea).** Override `COUNTRY_FLAG_TEX_WIDTH/HEIGHT` to 164/104 in a
  `common/defines/*.lua` (`NDefines_Graphics.NGraphics.X = ...`), raise `COUNTRY_FLAG_TEX_MAX_SIZE`
  (meaning unclear: probably the flag atlas size), re-export **every** large flag in Valsora
  (`gfx/flags/*.tga`, 194 files today) at 164x104, then set the medallion's mask, frame and
  `layout.FLAG` to show them at 82x52 *or* larger. Try it on a branch and check `error.log` and
  memory. Never mix flag sizes.

### Scripted GUIs, localisation and game variables

- A small scripted GUI (`common/scripted_guis`) with `parent_window_token = top_bar` (or
  `politics_tab`) and a window in a `.gui` file is how new dynamic text gets onto a vanilla screen.
  `context_type = player_context`. Without `dirty =`, it refreshes every tick (fine for a few
  strings).
- Variables usable in localisation (confirmed by the DUI top bar mod on 1.19):
  `[?political_power_daily|+=2]`, `[?num_of_civilian_factories|0]`,
  `[?num_of_military_factories|0]`, `[?num_of_naval_factories|0]`. Also `[ROOT.GetName]` and
  `[ROOT.GetNameDefCap]`.
- `visible = { ... }` on a scripted GUI can call a scripted trigger. The long country name switch
  uses `valsora_deco_long_name` (generated, see section 7).
- Scripted-GUI windows are `alwaystransparent = yes` so they never block clicks on the vanilla
  elements under them. The law cards' text boxes are not transparent, so their tooltip shows.
- Scripted localisation (`common/scripted_localisation`, `defined_text` with `trigger` /
  `localization_key` entries) picks text by state: the current law of each kind (`has_idea`), the
  ruling party's popularity (`has_government` → `[?party_popularity_100@<ideology>|0]%`), the leader's
  description (`has_country_leader = { character = X ruling_only = yes }`), the faction role
  (`is_faction_leader`). Call it in loc as `[GetValsoraDeco...]`.
- Used in v0.4 and **(assumed)**, from documentation, not yet seen working: `[?political_power|0]`,
  `[?party_popularity_100@ideology|0]`, `[ROOT.GetRulingParty]`, `[ROOT.GetLastElection]`. If one
  shows raw text or nothing in game, swap that cell's loc for another value.
- Text colour codes `§X...§!` use the font's `textcolors` table. Each bitmap font in
  `valsora_deco_fonts.gfx` carries its own table, and we added `C = {92 160 170}`.
- Ship localisation for all 9 languages (the generators write the English text into every
  language). Files are UTF-8 **with BOM** and start with `l_<lang>:`.

### Bitmap fonts (BMFont text .fnt + .dds)

- UI fonts are laid out with **RGB = glyph and A = glyph + outline**. The engine colours the RGB
  and the alpha gives a dark rim. The map font is the reverse (A = glyph, RGB = outline), like
  vanilla `hoi_mapfont4`.
- **Gilt text:** the gold gradient is baked into the RGB and the font colour is set to white
  (`0xffffffff`). Used for the country name, titles and section headers.
- **Caps fonts** map lowercase code points to uppercase glyphs, so loc strings stay normal case.
- **Custom glyph:** U+25C6 (diamond) was added to the value fonts and is coloured with `§` codes.
  It draws the coloured factory diamonds.
- **Blank font** (`valsora_deco_blank`): every glyph is empty. It hides an engine-written string
  while keeping its box and tooltip. The factory readout uses it, and a scripted GUI redraws the
  numbers.
- Characters outside the generated set do not render. The set is Latin-1, Latin Extended-A, common
  punctuation and the diamond. A thin space U+2009 was tried and failed.
- `vanilla "tahoma_60"` (the map's country names) is replaced by overwriting
  `gfx/fonts/hoi_mapfont4.fnt/.dds`, without touching its definition.
- `line_extra` in `gen_fonts.build` adjusts the line height (Bodoni Moda's is very loose: the italic
  description font uses -5 to fit five lines).

### Main menu

- The background comes from the **background manager**: `common/frontend/backgrounds/
  base_backgrounds.txt` holds `name = { }` entries for `gfx/loadingscreens/<name>.dds`, plus a
  `GFX_<name>_small` (192x144) sprite for the picker. The mod's `base_backgrounds.txt` **replaces**
  the game's, so only the Valsora background is listed. **(in game)** The Valsora background shows.
- The bottom panel (`mainmenu_panel_bottom`, 1320x140) is anchored `CENTER_DOWN` at `(-660, -166)`
  with no `Origo` (see the Origo note above). It has `clipping = yes`, and the three subscription
  widgets are parked outside it at x 1344, which hides them. The game resizes the panel to its
  `subscription_size` positionType, so that is set to the panel's own size.
- The game moves `mainmenu_social_buttons` to one of its three positionTypes when the menu opens
  **(in game:** vanilla's `position_without_social_gui` (0,175) put the links over the middle of the
  map**)**. v0.4.4 anchors the window `UPPER_LEFT` with no `Origo` and points all three positionTypes
  at (28,44), the top-left corner. Its icon rows draw at y -17 and +19 inside the window. **(assumed)**
- The console is `console_wnd` in vanilla `core.gui` (font `Arial12`, `GFX_console_win_bg`,
  `small_tiles_dialog.dds`); the mod touches none of it. The blue/green 1280x720 and 1600x900
  rectangles the user saw are the game's GUI-bounds debug overlay (console command `gui`).
- The menu background is 1920x1440, of which the middle 1080 rows show on 16:9 (crop `OY = 180`).

### Alerts

- `interface/alerts.gui` uses positionTypes: `alerticon_startposition` (vanilla 662,38) and
  `alerticon_startposition_extended` (718,38). **(in game)** The extended one is the one in use. The
  others are `alerticon_offset` (48,44) and `alerticon_endposition` x, which is the row width before
  wrapping. Alert icons measure about 43x38 **(in game)**. The mod sets start and extended to the
  same point (188,71) and the row width to 432 (10 per row).

### Measured from screenshots (in game)

- The world tension globe is about 50x50 at `threat_button`'s position, with its glow 15px up and
  to the left.
- Army bar portrait frames are about 74x98. `leader_groups_portrait_window` is 68x97 in the .gui.

## 7. What each generator does (and why)

**make_topbar.py.** It reads the game's `topbar.gui` and `alerts.gui` and the Valsora mod's
localisation, tags, cosmetic tags and ideologies.

- Moves and re-skins every vanilla element into the mockup's layout (sections 1 to 8 in the file).
  It keeps every vanilla element and adds a decorative layer.
- The flag is 82x52 at 1:1, inside a gilt frame on a stepped medallion with speed-line wings.
- The country name is two scripted GUI windows in the same box. The large font is used unless the
  trigger `valsora_deco_long_name` says the current name would not fit. The trigger is
  **generated**. Each `TAG`, `TAG_<ideology>` and cosmetic-tag name from Valsora's English
  localisation is greedy-wrapped at the large font's metrics, and names with a word wider than the
  box, or more than 2 lines, are listed. Today the list is GLB HZB KKB LNT MTN MZG OCR PNC RMD STM
  TBS TUP. **Re-run `make_topbar.py` whenever Valsora adds or renames countries.** Without
  localisation, the trigger is `always = yes`.
- Daily political power and the three factory counts (with coloured diamonds) are scripted GUI
  text. The engine's own factory string is hidden with the blank font.
- Logistics (fuel, supply, convoys) sits in a slim tray hanging under the readout strip. Army, navy
  and air XP are small badges on the right-hand overview buttons. This replaced vanilla's big
  dropdown at the user's request.
- Command power and nukes are in the right-hand tray. World tension sits in a gilt ring with its
  value underneath.
- It writes `common/scripted_guis/valsora_deco_topbar.txt`,
  `common/scripted_triggers/valsora_deco_triggers.txt`, `interface/valsora_deco_topbar_extras.gui`,
  `interface/valsora_deco_topbar.gfx`, `interface/valsora_deco_fonts.gfx`, the loc files and
  `interface/alerts.gui`.
- It stops with an AssertionError naming the element if a patch renamed something.

**make_topbar.py, v0.4 change.** The seal hanging from the flag medallion is now the **decisions**
button (2 frames, its count badges on the seal's right edge, the alert glow under it). The **faction**
button is the first crown of the row, keeping its vanilla sprite names (see the runtime swaps); the
faction logo is drawn over the crown at scale .7 and the initiative number sits at its lower right.

**make_politics.py (v0.4).** It starts from **Valsora's `interface/countrypoliticsview.gui`** and falls
back to vanilla's. It re-lays the screen as the Government mockup (`layout_politics.py` has the map):

- header: "Government" label (the game's `political_title`, re-texted), the full country name, close
- arched portrait over a sunburst, gold "Head of State" ribbon
- leader name (Federo 24), an ideology chip (the game's ideology icon and text)
- a 2x2 grid: ruling party · popularity, elections (the game's text), last election, political power
  and its daily change
- the leader's description in Bodoni italics between two rules, or an ornament when there is none
- popularity pie (own pieChartType) in a gilt ring, legend with diamond swatches | three law cards
  (conscription, economy, trade; display only, laws are still changed in the list below)
- national spirits band, faction card | national focus card (the card opens the focus tree)
- compact occupied / exiles / subjects buttons, then the game's advisors & laws list from y 806

Six scripted GUIs fill in the dynamic text (title, info grid, description, ornament, laws, faction
role). It also writes `common/scripted_localisation/valsora_deco_politics.txt` and
`common/scripted_triggers/valsora_deco_politics_triggers.txt` (leaders that have a description,
read from Valsora's `common/characters`; re-run when leaders are added). It adds 13 elements and
keeps all vanilla ones. Balance of power (Valsora has none) sits at the right of the spirits label.

**make_stateview.py.** The panel that opens on a province click. The state part follows the mockup:
owner flag in a gilt well and the state name (gilt capitals) with the game's "owner" text as a
subtitle; a stats row (victory points | manpower | resources) with the mod's labels; shared building
slots (7 per row, 2 rows); state buildings with a label; claims, and resistance for occupied states.
The province part (name band, terrain, province buildings, modifiers) keeps the game's positions,
because several of its elements are placed relative to the province window by the engine. New
background picture (450x650 at the game's (5,5), zones in `layout_stateview.py`), building tiles,
level plates, chips, close diamond and fonts.

**make_focus.py.** Focus tree chrome: header band (stretched corneredTile), gilt title, search box,
zoom diamonds, close, filter chips (2 frames), the tree's grid background and vignette, an octagon
medallion behind every focus icon, the name plates (replaced at their vanilla paths, 160x34; the name
is re-centred on them), the detail pop-ups and a legend in the lower right. The tree's geometry is
untouched.
- **Conflict:** the Valsora mod ships the same file path, so the UI mod must load **after** Valsora.
  If Valsora's `countrypoliticsview.gui` changes, re-run `make_politics.py`.

**make_menu.py.**

- Hides the logo (the title is baked into the background art).
- Turns the vertical button column into a row anchored to the bottom centre (explicit offsets, no
  Origo): Career, Multiplayer, a big gold Single Player, Settings, Credits, with Friends, Nudge and
  Exit below.
- Moves the social links to the top-left corner (all three of the game's positionTypes).
- The single player sub-panel buttons get the panel sprite.
- Writes `base_backgrounds.txt` and `valsora_deco_menu.gfx`. Main menu sprites are named
  `GFX_valsora_deco_mm_*`, because `GFX_valsora_deco_menu_button` already exists in the top bar.

**validate_preview.py** checks the following:

- brace balance
- every sprite and font used is defined (by the mod or by vanilla .gfx)
- textures read back with sane frame widths
- `.fnt` files agree with their atlases
- replaced vanilla textures keep their vanilla sizes
- engine strings fit their boxes, using worst-case sample values
- **every .gui the mod ships at a vanilla path still has every vanilla element name, as often as
  the game's copy does** (compared with Valsora's copy for `countrypoliticsview.gui`)

It then renders a top bar preview from the generated files. A new screen's .gui is covered by the
element check automatically. Add its own string-fit checks and a preview.

## 8. guipatch: how to edit a vanilla .gui

```python
import guipatch as GP
t = open(src, encoding="utf-8-sig").read().replace("\r\n", "\n")
t = GP.set_attrs(t, "countrypoliticsview>close_button", sprite="GFX_x", position=(-54, 20))
t = GP.set_background(t, "mainmenu_panel_bottom", "GFX_valsora_deco_clear")
t = GP.insert_after(t, "countrypoliticsview>leader_name", snippet)    # new sibling element
t = GP.insert_child(t, "some_container", snippet, first=True)        # first = drawn underneath
GP.check(t)                                                          # brace balance
```

- Paths use names. `a>b` means b is a **direct child** of a, and `a/b` means b is **any
  descendant**. Every lookup asserts exactly one hit, so ambiguous names need a longer path.
- `set_attrs` formats `position`, `size`, `slotsize` and `max_slots` from tuples, and quotes
  strings for `font`, `sprite`/`spriteType`, `text` and `Orientation`. It edits the element's
  **own** attributes, never a child's. `own_region` cuts at the element's final `}`. An earlier bug
  appended attributes after the closing brace.
- Comments are stripped before matching. Matching is case-insensitive on type keywords.
- Write files as UTF-8 with LF. Vanilla reads them fine.

## 9. Pitfalls already hit (do not repeat)

- Stretching flags makes them pixelated. Keep them 1:1.
- New sprite names can collide. Prefix everything `GFX_valsora_deco_<screen>_...` and check with
  validate.
- A new font must also be listed in `make_topbar.FONTS`, which writes `valsora_deco_fonts.gfx`,
  or the game will not know it.
- Text boxes that are too short silently drop the second line. Size boxes for 2 lines where names
  can wrap.
- `Origo = center_down` on a top-level window hid the whole main menu row in v0.4.3. Anchor with
  explicit offsets instead (section 6). `preview_screens.preview_menu` asserts the panel has no Origo
  and fits on a 1920x1080 screen.
- Never `rm -rf` with relative globs after a `cd`. Use absolute paths, and use `unzip -o` into an
  absolute directory.
- Long-name detection must use only name keys (`TAG`, `TAG_<ideology>`, cosmetic tags). Matching
  any loc key that starts with a tag flagged the wrong countries.
- When merging into the Valsora mod (section 11), `make_politics` must not read its own output.
  Keep a pristine copy of Valsora's original `countrypoliticsview.gui` as the base.

## 10. Open items and things to check in game

Check these first in the user's next screenshots:

1. **v0.3 top bar fixes**
   - flags are crisp
   - the market button has the deco icon
   - the logistics tray and XP badges read well
   - the globe is centred in its ring
   - alerts sit below the band and do not cover the tray (coordinates may be off by about 4px:
     topbar-local vs screen)
   - Terrabis-Seran and other long names use the small font on 1-2 lines
2. Daily political power format `+=2` shows like "+1.80".
3. **Z-order:** does the top bar medallion draw over side panels? The politics header is kept clear
   of it either way.
4. **Politics screen (v0.4)**
   - every scripted value shows: ruling party · %, last election, political power and daily change,
     the three laws, the leader description (Roland II) / ornament (others), faction role
   - the pie (own, radius 40) sits in its ring; the legend diamonds take the party colours
   - the ideology icon in the chip (scale .34 is a guess)
   - the faction card's frames (1 in a faction, 2 create)
   - the focus card opens the focus tree; its progress bar fills; the "choose a focus" glow
   - the spirits band wraps at 8; the advisors & laws list scrolls (it starts lower than before)
5. **Top bar (v0.4)**: the decisions seal opens decisions and shows its count badges and glow; the
   faction crown swaps between the plain and the in-faction version and shows the logo
6. **State panel**: the new background covers the province part too (the game's container is only
   496 tall; the picture is 650); building tiles line up with the building pictures; what the
   game's "owner" text says (it is used as the subtitle); the population icon's size at scale .55;
   resources with two rows do not run into the slots line; resistance (occupied states) next to
   claims
7. **Focus tree**: plates line up with the focus names and links; the medallion sits behind the
   icons; filters show on/off; the legend does not hide anything important
8. **Main menu**
   - **(v0.4.4 fix)** the button row now shows along the bottom, centred at 16:9 and other ratios
   - the social links sit in the top-left corner
   - the background manager shows the Valsora background **(in game, done)**
   - the single player sub-panel looks right
   - the version label is readable
9. Toolbar buttons have 2 frames. Frame 2 is drawn "lit" (jade) on the assumption that it is the
   active state.
10. Without La Resistance, the game shifts buttons after intelligence. Check for overlaps.

Still vanilla art:

- the world tension globe and glow
- the supply icon
- the achievements and dismissed-alert buttons
- the count badges on the menu buttons
- the music player pop-out
- faction logos
- focus icons and the links between focuses
- every screen other than the politics screen, state panel, focus tree and main menu (core skin only)

## 11. Integration options (decide with the user)

- **A. Separate mod (current).** `valsora_deco_ui/` goes into `Documents/Paradox Interactive/
  Hearts of Iron IV/mod/` with its `.mod` file. Load it **after** Valsora in the playset, because
  both mods ship `interface/countrypoliticsview.gui`. It also works on vanilla, in which case the
  long-name trigger is built from Valsora data and stays harmless.
- **B. Merged into the Valsora mod.** Set `VALSORA_DECO_MOD` to the Valsora mod folder. The
  generators then write straight into it. Before doing this:
  - copy Valsora's original `interface/countrypoliticsview.gui` to a separate base path and point
    `make_politics` at it
  - check the Valsora mod does not already have files at the same paths (`topbar.gui`, `alerts.gui`,
    `frontendmainview.gui`, `base_backgrounds.txt`, the replaced textures)
  - keep this source project (tools, fonts, art) **outside** the mod folder, because the Valsora
    repo root *is* the mod folder (`descriptor.mod` at the root), and anything inside it gets
    uploaded with the mod
  - a sibling folder or a separate repo works, or a subfolder that is excluded from uploads
- Either way, copy `valsora_deco_ui/README.txt`'s install notes into the release.

## 12. Next steps (in order)

1. Process the user's screenshots of v0.4 (section 10).
2. **Army bar and map modes / minimap**: see `docs/next_army_bar_and_map_modes.md`. It covers the
   sprite tables, the plan and what to read from the game's textures first. These need the real
   `gfx/interface/unitcontrol/`, `gfx/interface/mapmode/` and minimap textures (frame sizes and
   meanings). The first session did not have them.
3. Politics extras still missing from the Government mockup: faction member flags (needs a scripted
   GUI dynamic list over the faction's members; not verified that one exists) and a one-spirit card
   with its modifiers. The user does not want "The Court" panel.
4. Apply the mockup style to the other side panels. Production, research, trade, diplomacy and
   logistics already inherit the skinned `tiled_plain_bg`, windows and buttons. Re-lay them only
   if the user asks.
5. Superevent screen (mockup in `art/mockups/`). Valsora has its own `valsora_superevent.gui`, so
   coordinate with that file rather than overriding it blindly. The focus tree's links are still
   vanilla (16 px tiles, 4 frames per state, frame meaning unknown: read the textures first).
6. HD flags experiment (section 6), only if the user wants it.

For every new screen, follow this pattern:

- write a `layout_<screen>.py`
- write a `make_<screen>.py` that patches the game's file with `guipatch` and keeps every element
- add the textures in `gen_textures.py`
- add the sprites to a `valsora_deco_<screen>.gfx`
- add the loc keys in 9 languages
- extend `validate_preview.py`
- add a preview in `preview_screens.py`
- add the step to `build_all.py`
