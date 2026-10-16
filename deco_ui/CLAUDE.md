# Valsora Deco UI: handoff guide for Claude

This file is for a Claude instance picking up the art deco UI mod for **Valsora**, a Hearts of Iron IV
(1.19) total conversion set in Valsora, the world of The East Pacific (a NationStates region). The
mod's author is the user. This folder is the **source project**. `valsora_deco_ui/` is the built mod;
everything else is how it gets built.

The first four versions were made in a cloud session that had no game install. It had only copies of
the game's `interface/` folder, `00_defines.lua` and `00_graphics.lua`. From v0.4.5 (2026-10-14) the
project lives in the Valsora repository as `deco_ui/`, and the game's files come from the user's
private copy of their install (section 3). Everything below marked **(in game)** was confirmed from
the user's screenshots or `error.log`. Everything marked **(assumed)** has not been seen in game yet.
Treat assumed items as hypotheses.

---------------------------------------------------------------------------------------------------

## 1. Status (v0.8.4)

**v0.8.4 (2026-10-16)** is the current version: the user's screenshots and `error.log` of v0.8.3 (section 10, the
README): the focus tree's title in its header (the game's own title; the scripted one sat in the tree's canvas), opaque
headers, deco fold arrows and count badges, the large tabs 4 px in from each side, the empty card's plus on the chest,
and the game's font bases; then, from the user's later messages, Vietnamese letters in every font (Plaija's names),
the small cut for any name that needs two lines under the flag, and the navy view below the medallion. The user has seen v0.8.3 in game (2026-10-16): the army bar "looks good". **v0.8.4 is not
yet seen.** **(in game)** so far: the main menu (its background, links and button row), the top bar (the right end
too, since v0.4.5), the politics screen (v0.4.7, v0.4.8), the side panels' notch and opening (v0.5, v0.5.1), the
events and the news page (v0.8.1), the army bar and the focus tree (v0.8.3).

The history, version by version, with what the user saw in game and what it taught, is `docs/HISTORY.md`; the
lessons that still hold are in section 6 (engine facts) and section 9 (pitfalls).

| Area | State |
|---|---|
| Core skin (window frames, tooltips, standard buttons, panel background, map font) | Done. Vanilla textures are replaced at their vanilla paths and sizes. |
| Icons (`tools/icons.py`) | The mockup's 24 px gilt line icons, with modern subjects for army, deployment, air and convoys. Sheet: `build/icon_sheet.png`. |
| Top bar (`interface/topbar.gui`) | Re-laid to the mockup. v0.4: **decisions** is the seal under the flag; **faction** moved into the crown row (first slot). |
| Alerts row (`interface/alerts.gui`) | v0.3: moved below the band, under the menu buttons. |
| Politics screen (`interface/countrypoliticsview.gui`) | v0.4: the Government mockup's layout (no Court panel), with scripted GUIs for what the game's screen lacks. v0.4.8: flush under the top bar, notched round the medallion; no description or law cards; sub-ideology; spirits beside popularity. |
| Other side panels (16: army, construction, decisions, deployment, diplomacy, intelligence, logistics, occupation, officer corps, production, research, trade, faction, faction setup, faction pings, market) | v0.5 (`make_panels.py`): flush under the top bar with the notch, deco header (gilt title right of the notch, close diamond, header buttons, rule), the politics body tile, content moved below the seal; the windows that open beside them flush too. Their insides keep the game's layout; shared pieces (tabs, sort buttons, headers, checkboxes, close, `tiled_bg`) are re-skinned. |
| State / province panel (`interface/countrystateview.gui`) | v0.4: the mockup's arrangement for the state part (flag + name header, stats row, slots, buildings); the province part keeps the game's positions. |
| Focus tree (`interface/nationalfocusview.gui`, `.gfx`) | v0.6 (the FocusTree mockup): flush under the band with the notch; header with the scripted title and subtitle, chips, search, zoom, close; scale-pattern canvas in a gilt frame; medallion + plate per focus state (unavailable, available, in progress, completed); halo, search glow, links, exclusive marks, continuous focus marks, legend. Focus icons untouched. |
| Superevent (Valsora's `valsora_superevent.gui`) | v0.6: drawn by the Valsora mod (`scripts/superevents_deco.py`) from the Superevent board when `DECO_UI` is on: a veil over the map, gilt frame, crest, title strip, framed picture with corner fans, quote, button, now-playing tab. |
| Main menu (`interface/frontendmainview.gui` + background) | v0.3; v0.4.5 fixed the invisible button row (a quoted `Orientation`). Background and social links **(in game)**. |
| Army bar (bottom: `leadergroups.gui`) | v0.7: textures at the game's paths and sizes (`gen_textures.py`, `lg_*`; numbers in `layout_armybar.py`): arched gilt frames over the portraits (jade when selected; an army group's with gilt fans), the plate behind a run of cards, play/stop chips, the battle plan's chevrons, the empty card; `make_leadergroups.py` moves the division counts onto the plaques (centred, `valsora_deco_value_17`); v0.8: the play / stop row on the card's centre line. Preview `build/preview_armybar.png`. |
| Map modes and minimap (bottom right: `mapmodes_interface.gui`, `minimap.gui`) | v0.5: textures only (layouts are the game's and Valsora's): lacquer column, line-icon medallions for land/air/naval/intel, the game's small icons and toggles recoloured in gilt, deco handle and ping buttons; the minimap's picture and frame in gilt by the Valsora mod (`scripts/minimap.py`, deco style). |
| Events (`eventwindow.gui`) | v0.7: the report and newspaper textures replaced at the game's paths (`ev_*`): lacquer card with a crest, gilt rails and a picture frame; a WORLD NEWS broadsheet; options as gilt-rimmed plates; `make_events.py` sets the mod's fonts (titles `title_18`, text and options `body_15`). v0.8: the options centred in the room beside the picture (`layout_events.py`), a Valsoran globe on the masthead. v0.8.1: the masthead VALSORAN (globe) STANDARD, the news page centred. v0.8.2: the card's crest a keystone (`crests.py`), options in `option_14` (three lines to a plate), the globe lit. Preview `build/preview_events.png` (a country, a news and a leader event). |
| Fonts | The mod's own (`gen_fonts.py`) on its own screens; v0.8: the game's 28 fonts redrawn in the deco faces at their paths (`game_fonts.py`), for everything else. Preview `build/preview_game_fonts.png` (needs the game's font textures: section 7). |
| Everything else (the panels' own pictures ...) | Only the core skin so far. Proposals for the panels' pictures (not in the mod) in `art/proposals/`. |

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
- They can also send `error.log` (`Documents/Paradox Interactive/Hearts of Iron IV/logs/`). **Ask for
  it whenever something does not show in game**: the game names the file and line it rejected. v0.4.4
  was a wasted round because the fix was guessed from a screenshot.
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

### In the Valsora repository (cloud sessions)

The project is `deco_ui/` in the Valsora repository (the mod's own pipeline is in `scripts/`; see the
repository's `CLAUDE.md`). The game's files are in the user's private repository
`Rouental/HOI4-Files`: attach it to the session, clone it to `/home/user/hoi4-files` (text files under
`HOI4 Files/`, `gfx/` at its root; a sparse checkout without `gfx/fonts` textures, `gfx/models` and
`gfx/event_pictures` is enough), then link it and the built Valsora mod into `reference/`:

```
cd deco_ui && mkdir -p reference/vanilla
for f in interface common localisation map portraits history events; do
  ln -sfn "/home/user/hoi4-files/HOI4 Files/$f" reference/vanilla/$f; done
ln -sfn /home/user/hoi4-files/gfx reference/vanilla/gfx
for f in 00_defines.lua 00_graphics.lua; do
  ln -sfn "/home/user/hoi4-files/HOI4 Files/common/defines/$f" reference/vanilla/$f; done
ln -sfn ../../build/valsora_test reference/valsora    # build it first: sh scripts/run_all.sh at the root
CHROMIUM_PATH=/opt/pw-browsers/chromium python3 tools/build_all.py
cd .. && sh scripts/run_all.sh                         # the Valsora build takes the Deco UI in (section 11)
```

Since v0.5 there is no separate release: `dist/valsora_test.zip` (the Valsora mod) carries the Deco UI.
`reference/valsora` is the built mod, which then holds the Deco UI's own copies of the files it replaces;
the tools read Valsora's originals from `../work/deco_base/` (`paths.VALSORA_BASE`, kept by the Valsora build),
and `make_politics.py` stops if its base is the Deco UI's own output.

`CHROMIUM_PATH` points Playwright at the machine's pre-installed Chromium, whose version may not match
the pip package's (`playwright install` is not needed then). The full build takes about 30 seconds (v0.8.3: the steps of
a stage that don't depend on each other run side by side; 81 s one after another). Naming a step that doesn't exist
stops it.
`gen_textures.py` redraws only the textures whose drawing changed since the last run (v0.8: a signature of each one's
HTML, size, fonts and embedded files, kept in `texture_manifest.json`, which is committed, so a fresh clone redraws
nothing); `--all` redraws every one, and `gen_textures.py <prefix> ...` those whose key starts with a prefix. A redrawn texture can differ from the shipped one
by a few anti-aliased pixels: `python3 tools/restore_noise.py` (`--dry` to list) puts back every changed texture that
differs from the committed one only by such noise, so each release changes only what it meant to.

## 4. Project map

```
valsora_deco_ui/            the built mod (shipped). Generated, so do not hand-edit .gui/.gfx/.yml here; change the tools
valsora_deco_ui.mod         launcher descriptor (path="mod/valsora_deco_ui")
texture_manifest.json       each texture's path, size and signature (gen_textures.py: what to redraw)
tools/
  paths.py                  all locations (see above)
  build_all.py              runs every step, stage by stage (independent steps side by side: fonts; generators in order;
                            the checks; the previews)
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
  layout_panels.py          the other side panels (v0.5): notch per panel x, header, shift, each panel's spec
  make_panels.py            the 16 side panels' .gui files (the game's, patched) + the windows beside them + panels .gfx
  long_names.py             the long-name trigger (which names need the medallion's small font); make_topbar and the
                            Valsora build run it
  layout_armybar.py         army bar numbers (v0.7): the cards, plate pieces, plaques, counts; MOVES (v0.8)
  make_leadergroups.py      leadergroups.gui: the counts on the plaques, the play / stop row on the centre line
  make_mapviews.py          unitview.gui, airselectionview.gui, operativeleader.gui, naviesview.gui: the left-edge
                            views moved below the medallion (v0.8.2, layout.BELOW_MEDALLION; the navy v0.8.4)
  preview_armybar.py        build/preview_armybar.png (+ _zoom): the game's look and the mod's, read from the .gui
  layout_events.py          the events' option plate and each window's options centre (v0.8)
  make_events.py            eventwindow.gui: fonts, option entries, each window's options grid
  preview_events.py         build/preview_events.png: a country, a news and a leader event
  globe_art.py              art/valsora_land.png (Valsora's land from the built map), the masthead's globe (v0.8, lit
                            again in v0.8.2, the ringed newsreel globe since v0.8.3: layout_events.NEWS_GLOBE_STYLE)
                            and the other globes proposals_globes.py shows; the Valsora mod's superevent crest too
  crests.py                 the event card's crest (v0.8.2: EV_CREST, a keystone; v0.8.3: its diamond lower) and the
                            card's top piece (ev_top)
  game_fonts.py             the game's 28 fonts redrawn in the deco faces at their paths; --measure sizes them (v0.8)
  preview_game_fonts.py     build/preview_game_fonts.png: the game's fonts beside ours (needs the game's font textures)
  restore_noise.py          puts back textures that only changed by anti-aliasing noise (v0.8)
  proposals_*.py            the proposals in art/proposals/ (panel pictures, larger flags, masthead names, the news
                            globe, the crests): not in the mod
  validate_preview.py       static checks + a preview renderer that reads the generated .gui/.gfx
  preview_screens.py        politics, state panel, focus tree and main menu previews (imports validate_preview)
  preview_panels.py         every side panel (build/preview_panel_<key>.png and _vanilla.png, the game's) and the
                            lower right corner (build/preview_corner.png), drawn with the game's own textures
  package.py                zips valsora_deco_ui.mod + valsora_deco_ui/ (the separate mod; unused since v0.5)
source_fonts/               TTFs + OFL licences (Josefin Sans, Federo, Limelight, Bodoni Moda)
art/                        menu_world.jpg (main menu map), map_rouental.jpg + flag_ROU.png (preview backdrops),
                            mockups/*.jpg (renders) and mockups/source/ (the boards' HTML + assets)
docs/                       plans for the next screens
reference/                  vanilla/ and valsora/ inputs (not shipped, not committed)
build/                      intermediates and previews (safe to delete)
```

Build order matters. `gen_fonts` runs first because `layout.py` measures strings with the generated
`.fnt` files. Next comes `gen_textures`, because many texture sizes come from `layout.py` /
`layout_politics.py` / `layout_panels.py`, and it reads the game's map mode icons (to recolour them). The
`make_*` generators follow, then the checks and previews.

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
  **Write both bare** (`Orientation = CENTER_DOWN`), as vanilla does on every container (it quotes
  them only on some child elements). **(in game,
  error.log)** On a `containerWindowType` the game rejects a quoted value ("Not a valid orientation:
  CENTER_DOWN, near line: 382") and keeps the default `UPPER_LEFT`. That hid the main menu's button
  row in v0.4.3 and v0.4.4: its offset from the bottom centre, (-660,-166), put it above the top-left
  corner of the screen. It also sent five top bar windows anchored `UPPER_RIGHT` (command power,
  nukes, army, navy, air) off the left edge. Quoted values on other element types raised no error,
  but `guipatch.engine_safe` unquotes them all.
- The v0.4.4 notes blamed `Origo = center_down` for the main menu. That was a guess from a screenshot
  and was wrong: v0.4.3 quoted the orientation too. Whether `Origo = center_down` works is untested.
  **(in game)** `Origo = center` and `lower_left`/`lower_right` work on top-level frontend windows
  (the social links, the DLC column and the change-background button all land where vanilla puts
  them). Bottom-centred windows follow vanilla's peace conference chat: `Orientation = CENTER_DOWN`,
  no `Origo`, and `position = { x = -width/2 y = -(height + margin) }`.
- **(in game, error.log)** `alwaystransparent` is not a `containerWindowType` key ("Unexpected token:
  alwaystransparent"). Vanilla puts it inside a container's `background = { }` block (83 times), or on
  icons, buttons and text boxes. `engine_safe` moves a container's own `alwaystransparent` into its
  background, or drops it when there is none (the game was ignoring it anyway). **(assumed)** A
  container without a background does not catch clicks itself; its children do. Vanilla's
  scripted-GUI windows (e.g. `usa_congress_decision_ui_window`) have no background either. If one of
  ours turns out to block a tooltip under it, an untested remedy is a tiny `size` with
  `clipping = no`, so its text still draws outside it.
- The checker reads the game's rules from vanilla, not from our own parser, which accepted everything:
  `validate_preview` flags quoted orientations, `alwaystransparent` on containers, and any key that no
  vanilla element of the same type uses. Run on the v0.4.4 files, it flags all 31 lines the game's
  `error.log` named (19 quoted orientations and 12 `alwaystransparent` on containers), plus 147 quoted
  orientations on icons, buttons and text boxes that the log did not mention (vanilla quotes some of
  those itself, so they are probably harmless; they are written bare now anyway).
- A width of `100%%` runs to the parent's right edge, so right-anchored top bar elements use
  `gui_x = screen_x - 1920`. **(in game)** The world tension ring landed exactly where planned.
- The top bar container sits at `(-4,-1)`, so `gui = screen + (4,1)` for UPPER_LEFT children
  (`layout.GUI`, `layout.GUI_R`).
- `vertical_alignment = center` works on `instantTextboxType`. **(assumed;** it is used for the
  country name and labels)
- `pieChartType` is drawn centred on x with its top at y, so the centre is `(x, y + r)`. Its `.gfx`
  `size` is the **radius**; the politics pie uses its own `GFX_valsora_deco_pol_chart` (radius 40).
- An element added *before* the vanilla ones in a container draws underneath them. The decorative
  layer in `make_topbar` is inserted first for that reason. The same holds for vanilla's own order:
  `political_title` comes before `pol_view_bg` in vanilla's file, so once `pol_view_bg` became an opaque
  header picture (v0.4.8) the title vanished under it in the preview; it is emptied and a label of our own
  is inserted after the picture.
- **(in game, v0.8.3)** a scripted GUI with `parent_window_token = national_focus` is docked **inside the focus tree's
  scrolling canvas** (vanilla's `tree>grid_window>focus_tree_scripted_window_container`), not the focus window: its
  (0, 0) is ~(11, 124) in the window, and it moves with the tree. Use it for things that belong on the tree; the
  header's title is the game's own `national_focus_title` since v0.8.4.
- **(in game, v0.8.3, error.log)** a font of several files (`fontfiles` in `core.gfx`: `cg_16b` with the game's
  `hoi_16tooltip3`) must give them one `base`; `game_fonts.py` writes the game's own line height and base into each
  font it redraws.
- **(in game, v0.4.7)** **Side panels are drawn over the top bar.** The politics panel (top at y 78) hid the
  medallion's name plate and the decisions seal. v0.4.8 puts the panel at the band's bottom (y 62,
  `layout_politics.TOP`) and leaves a **notch** the shape of the medallion and seal
  (`layout_politics.NOTCH_POLY`, from the same numbers gen_textures draws the medallion with): the window's
  own background is a clear sprite with `alwaystransparent = yes` in its background block, and the
  panel's look and click-catching come from children that stay out of the notch: a body container from
  the notch's bottom down (`valsora_deco_pol_body`, a cornered tile), invisible containers with clear
  backgrounds beside the notch (`valsora_deco_pol_block_*`), the section art and the header picture
  (`pol_view_bg`, click-through). **(assumed)** clicks in the notch reach the top bar's seal beneath.
- **v0.5: every other side panel the same way** (`make_panels.py`; `layout_panels.py` has the numbers). The
  game's side panels (survey of 1.19.3's `interface/**/*.gui`, 2026-10-14): 16 windows slide in at y 78
  from the left (x -6; the construction screen at -9, faction pings at 0 and 500 wide, trade 689 wide), and
  17 more open beside them at x 537-545, y 78-83. All of them put a header band at y 0-40 (`*_header_bg` at
  (5,7), the title at (45,8) in `hoi_36header`, close at UPPER_RIGHT (-43,9)) and their content right under
  it, so the notch (local x 20-176, y 0-107) needs the title moved right of it and the content moved down:
  a per-panel survey of each element's real size (`build/` scratch, the game's textures) put the needed
  shift at 62-72 px (the faction screen's banner, which starts at y -10, 119). The notch's place in a panel
  depends on the panel's x (`layout_panels.notch_poly(x)`), so each (width, x) has its own header picture.
- **How a window slides (v0.5.2).** `position` is where a window is while closed and `show_position` where it shows;
  `show_animation_type`, `hide_animation_type` (decelerated, accelerated) and `animation_time` (ms) move it between
  the two. **(in game, v0.5.1)** the game does not hide a closed side panel: it moves it back to `position` and leaves
  it there, drawn. Vanilla's panels rest off-screen (x -606, the windows beside them at x -356 or behind the panel);
  its dropdowns (`*_expanded_window`) rest at y -300 or -2000, or inside a parent with `clipping = yes`, and several
  open with `animation_time = 0`. v0.5.1 rested the panels 36 px below their place to make them rise: a closed
  division overview then stayed on screen with its lists over the map (the user's screenshot; an earlier note here
  said the game hides a window once it has slid back, which was wrong). Since v0.5.2 every closed panel rests at the
  game's `position` when that is off-screen, else just off the left edge (`layout_politics.closed_x`), and opens at
  once (`OPEN_MS = 0`): sliding in from the left crossed the flag and the name (the user's video, v0.5).
- **(inferred from vanilla)** a **negative size** runs to the parent's edge minus that much (the logistics
  list, `height = -98`, ends where its 98 px footer, LOWER_LEFT at y -98, begins), like `100%%` runs to the
  edge; so moving a box down only shortens it, and bottom-anchored elements stay put.
- **(assumed)** `decision_grid_container`'s height is "Set in code to match the window size, but initial value
  is used as extra space in height" (vanilla's comment, `height = -10`). Whether the game subtracts the box's own
  y is unknown: if not, the decisions list now runs 72 px further past the screen's bottom. Check in game (scroll
  to the last decision); if so, give it `height = -82` in `layout_panels` (an `attrs` entry).
- The construction screen draws wider than its window: its building list (`possible_constructions`, x 433,
  267 wide) and close button (UPPER_RIGHT +107) hang out of the 550 px window (`clipping = no`); its header
  picture is 700 wide. **(assumed)** when the list is folded away (the arrow by the close diamond) the
  header still fits; check in game.
- **(inferred from vanilla, in game)** a child container with `height = 100%%` runs from its own position
  to the parent's bottom edge (vanilla's ideas list sits at y 425 with 100%%, and its scroll bar ends at
  the bottom of the screen), so the body container ends at the screen's bottom.

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
- **(in game, v0.4.7)** **A .gfx or .gui that names a `.tga` gets a `.dds` of the same name first,
  vanilla's included.** The tooltip (`ToolTip` in vanilla `core.gui`: `tiles_dialog.tga`) kept vanilla's
  look because vanilla ships only `gfx/interface/tiles/tiles_dialog.dds` (96x96) and our `.tga` lost to it.
  v0.4.8 replaces the `.dds` at vanilla's size; `validate_preview` flags any mod `.tga` that a vanilla
  `.dds` of the same name shadows. Tooltips are one style for the whole game (no per-element styling).
- **Replaced textures' sizes.** The window tiles follow the `size` in vanilla's `.gfx` (192x192), not
  vanilla's texture files (190x190 for `tiled_plain_bg` etc.): keep 192. Textures drawn at another size on
  purpose (buttons re-laid by the mod, the seal's glows, the crown buttons, the focus plates) are listed
  by `validate_preview` as information; `SAME_SIZE` there lists those that must stay vanilla's size.
- **Runtime sprite swaps: keep the vanilla sprite name and replace its textures.** Known (or very
  likely, from the sprite names in the .gfx) swaps, all handled this way:
  - `faction_button`: `GFX_topbar_faction` out of a faction (vanilla's picture has crossed axes) and
    `GFX_topbar_faction_empty` in one (vanilla's is a plain plate; the faction's logo, `faction_icon`,
    is drawn over it) → `gfx/interface/factions/ui/topbar_faction(_empty).dds`, 1 frame. **(in game,
    v0.4.5:** in a faction the game showed `_empty`; v0.3–v0.4.6 had the two pictures swapped, so our
    line icon showed under the logo**)**. The logo (a 32 px miniature) is centred in the ring at 0.85.
  - `decision_view_alert_glow`: `GFX_decisions_glow` / `_blue` / `_yellow` / `_green` →
    `gfx/interface/decisionview/decisions_glow*.dds`, 2 frames each (now octagonal halos sized to the
    seal). Vanilla also used the yellow one on `production_button_glow`, which now has its own crown
    glow sprite.
  - focus name plates: `GFX_focus_unavailable` / `_can_start` / `_completed` →
    `gfx/interface/focusview/titlebar/focus_*_bg.dds`. The joint-focus variants stay vanilla.
  - the politics header `pol_view_bg`: `GFX_pol_view_bg` / `GFX_pol_view_bg_no_dlc` (by DLC) →
    `gfx/interface/pol_view_bg(_no_dlc).dds`, 550x344 **(in game, v0.4.7:** our sprite on that icon never
    showed; vanilla's metal header with its round sockets did**)**. Both carry the same header strip.
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
- Scripted-GUI windows have no background, and their text boxes are `alwaystransparent = yes`, so
  they should not block clicks on the vanilla elements under them **(assumed;** `alwaystransparent`
  on the window itself is rejected, see .gui files above**)**. The law cards' text boxes are not
  transparent, so their tooltip shows.
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
  punctuation and the diamond, and since v0.8.4 Vietnamese (`gen_fonts.VIETNAMESE`: Ơ ơ Ư ư and the 90 tone-marked
  vowels of Latin Extended Additional; Plaija's names use 25 of them). A thin space U+2009 was tried and failed.
  The Valsora build's `check_mod.py` fails on any letter of the mod's English text or name lists missing from a
  font in `gfx/fonts` (mutation-tested).
- **Composed letters** (v0.8.4, `gen_fonts.compose`): Josefin Sans has every Vietnamese letter; Federo and Bodoni
  Moda don't, and Federo lacks Đ đ too. Such a letter is built in the face from its longest precomposed base it has
  (â for ấ) and the marks: each mark cut out of a precomposed letter (its ink beyond the base letter's), from the
  face itself (acute, grave, circumflex, tilde, breve) or else Josefin Sans (hook above, dot below), scaled by the
  x-height or cap height and set where the source sets it; a tone mark beside a circumflex goes to its side. The
  horn and đ's bar are strokes drawn in the face's weight (`_horn`, `_d_stroke`); Đ is the face's Ð; an i under a mark
  loses its dot (ỉ ĩ, `_drop_dot`). `COMPOSED` adds the Latin Extended-A letters Vietnamese uses (Ă ă Đ đ Ĩ ĩ Ũ ũ),
  which a Federo font otherwise drew in Josefin Sans. A mark reaching
  past the letter widens it by half of what it takes beyond the letter's side bearing, as Josefin spaces its own.
  The atlases grew to fit (several doubled; the mod's zip by 0.6 MB).
- **Face names** (v0.8.4): the `.fnt` files' `face` is "Valsora Deco Display" (from Federo), "Valsora Deco Sans"
  (Josefin Sans) or "Valsora Deco Italic" (Bodoni Moda), not the families' own: Federo and Josefin Sans are Reserved
  Font Names under their OFL, which a modified version (a bitmap font, letters of our own among them) may not use.
  The licences ship beside the fonts (`gfx/fonts/OFL_*.txt`).
- `vanilla "tahoma_60"` (the map's country names) is replaced by overwriting
  `gfx/fonts/hoi_mapfont4.fnt/.dds`, without touching its definition.
- `line_extra` in `gen_fonts.build` adjusts the line height (Bodoni Moda's is very loose: the italic
  description font uses -5 to fit five lines).
- **The game's own fonts** (v0.8) are defined in its `interface/core.gfx` (`fontfiles`) by file path, so a font file
  of the same path in the mod replaces one everywhere, as `hoi_mapfont4` has since v0.3. **(inferred from the game's
  files)** the engine loads the texture named like the `.fnt` (`gfx/fonts/hoi_18mbs.dds`), not the `page` named
  inside it: the game's own `.fnt` files name `hoi_18mbs_0.dds`, which the game doesn't ship. Tooltips use `cg_16b`
  (Century Gothic: `ToolTip` in `core.gui`); the rest are Ubuntu (`hoi_*`), Orator (`hoi_24header`, `_30header`,
  `_36header`: window titles), Garamond (`garamond_*`, `vic_*`, `standard*`: settings, menus, chat, the news feed) and
  the AFL typewriter (`hoi4_typewriter*`: the unit, leader, designer and scientist screens; `_inverted` is white).

### Main menu

- The background comes from the **background manager**: `common/frontend/backgrounds/
  base_backgrounds.txt` holds `name = { }` entries for `gfx/loadingscreens/<name>.dds`, plus a
  `GFX_<name>_small` (192x144) sprite for the picker. The mod's `base_backgrounds.txt` **replaces**
  the game's, so only the Valsora background is listed. **(in game)** The Valsora background shows.
- The bottom panel (`mainmenu_panel_bottom`, 1320x140) is anchored `CENTER_DOWN` (bare, see the
  Orientation note above) at `(-660, -166)` with no `Origo`. v0.4.5 is the first build in which the
  game accepts that anchor **(assumed** until the user's next screenshot**)**. It has
  `clipping = yes`, and the three subscription widgets are parked outside it at x 1344, which hides
  them. The game resizes the panel to its `subscription_size` positionType, so that is set to the
  panel's own size.
- The game moves `mainmenu_social_buttons` to one of its three positionTypes when the menu opens
  **(in game:** vanilla's `position_without_social_gui` (0,175) put the links over the middle of the
  map**)**. v0.4.4 anchors the window `UPPER_LEFT` with no `Origo` and points all three positionTypes
  at (28,44), the top-left corner. Its icon rows draw at y -17 and +19 inside the window. **(in game,
  v0.4.4:** the links sit in the top-left corner; the game rejected the quoted `UPPER_LEFT` but fell
  back to the same anchor**)**
- The console is `console_wnd` in vanilla `core.gui` (font `Arial12`, `GFX_console_win_bg`,
  `small_tiles_dialog.dds`); the mod touches none of it. The blue/green 1280x720 and 1600x900
  rectangles the user saw are the game's GUI-bounds debug overlay (console command `gui`).
- The menu background is 1920x1440, of which the middle 1080 rows show on 16:9 (crop `OY = 180`).
  The continent labels on it are `gen_textures.CN`; since v0.4.6 they are where the user put them in
  a picture they sent (measured by template matching against the old labels, then re-rendered: the
  picture came through chat as a lossy WebP, so it was not used directly).

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
  box, or more than one line (v0.8.4: two lines of the large letters filled the box to the flag's frame), are
  listed: 34 tags today (AOE ... WSM). **Re-run `make_topbar.py` whenever Valsora adds or renames countries.** Without
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

**make_politics.py, v0.4.8** (the user's screenshots): the panel sits flush under the band with a notch
round the medallion and seal (section 6); the description band, the ornament and the law cards are gone
(the description is the portrait's own tooltip; the laws are in the list); the grid has a fifth, full-width
cell, the **sub-ideology** (scripted localisation over `has_country_leader_ideology`, generated from the
`types` blocks of Valsora's ideologies, names `<key>`, descriptions `<key>_desc` as its tooltip; the
longest name is measured against the cell); "Last election" is None with `has_elections = no`; the
national spirits sit beside the popularity (2 rows of 4 large, then 7 small a row in the over-defined
grid); the list starts at `IDEAS_Y` 666. The scripted GUIs are title, info grid, sub-ideology and faction
role; the description trigger file is deleted. `preview_screens` also writes
`build/preview_politics_many_spirits.png` (15 spirits, as Devlon's test).

**make_panels.py (v0.5).** The 16 other side panels, from the game's files (Valsora ships none of them), as
the politics screen: window at `layout_panels.TOP` (shown there; hidden `RISE` px lower, v0.5.1), its background clear and
click-through; new first children (right after the window's own background) draw the panel: a body tile from
the seal's bottom (`GFX_valsora_deco_pol_body`), clear click-catchers beside the notch, and the header
picture (`GFX_valsora_deco_panel_head_<w>_<x>`); the game's header picture is hidden, the title moves right of
the notch in `valsora_deco_title_24` (one or two lines, centred in a 60 px box; `title_18` when it doesn't fit,
measured with the English text), the close button becomes the politics diamond, and the header buttons named
in the panel's spec line up beside it. Every other top-anchored direct child moves down by the panel's
`shift` (bottom-anchored ones stay; see the negative-size note in section 6). Fixed-height windows (faction
pings) grow by the shift. It also moves the 17 windows that open beside the panels to y `TOP`
(`layout_panels.BESIDE`; the politics screen's four are moved by `make_politics.py`). Asserts: each panel's x
and width are the spec's, and no header button sits beside the title's lines.

**long_names.py.** The long-name trigger (`valsora_deco_long_name`), moved out of `make_topbar.py` in v0.5 so
the Valsora build can run it on its own.

**gen_textures.py, v0.5 additions.** The panels' header pictures (one per width and x); the shared pieces
(`SHARED`: close button, `tiled_bg`, header bars, tabs, sort buttons, filters, checkbox, text field), at vanilla
paths and sizes (`validate_preview.SAME_SIZE` holds them to it); the map modes (`mm_*`: the column and its foot,
the find and "all" buttons, the big medallions with `army`/`air`/`navy`/`intel` line icons, the game's 18 small
icons and 6 toggles recoloured in gilt from its own textures, `gilt()`, the configure list, the social button)
and the minimap's handle, ping buttons and pings.

**make_stateview.py.** The panel that opens on a province click. The state part follows the mockup:
owner flag in a gilt well and the state name (gilt capitals) with the game's "owner" text as a
subtitle; a stats row (victory points | manpower | resources) with the mod's labels; shared building
slots (7 per row, 2 rows); state buildings with a label; claims, and resistance for occupied states.
The province part (name band, terrain, province buildings, modifiers) keeps the game's positions,
because several of its elements are placed relative to the province window by the engine. New
background picture (450x650 at the game's (5,5), zones in `layout_stateview.py`), building tiles,
level plates, chips, close diamond and fonts.

**make_focus.py (v0.6).** The focus tree, after the FocusTree mockup; `layout_focus.py` has the numbers.
- The window opens at `layout_politics.TOP` with the side panels' notch (its x is the game's -3, so its notch is
  `layout_panels.notch_poly(-3)`): its background is clear and click-through; first children are click-catchers
  beside the notch (to the window's right edge: `100%%` wide) and the header picture, a cornered tile 616 px wide
  whose left 260 px hold the notch and whose 96 px middle repeats to the window's width. The tree moves to y 114.
- Header: a "National Focus" label of ours (`valsora_deco_nf_kicker`, `section_11`) over the game's own title
  (`national_focus_title`, which the game sets to the tree's name, "Rouental Focus Tree") in `valsora_deco_title_30`.
  Until v0.8.4 a scripted GUI drew the title and a subtitle (full name and sub-ideology); docked to `national_focus`,
  the game put it in the tree's canvas, over the first row of focuses (section 6), so it is gone.
- Each focus: the game swaps its `bg` button's sprite by state, so the picture is the medallion and the plate
  together (157 x 118, at item (9, -27): the octagon centred on the icon's (87.5, 20), the plate overlapping its
  foot): `focus_unavailable_bg`, `focus_can_start_bg` and `focus_completed_bg` at the game's paths (completed: the
  gold medallion and a check badge; its plate a deep gold, since the game's name stays cream). The game draws a
  focus in progress with `GFX_focus_current`, the can-start picture plus two rotating shines; the mod ships the
  game's `nationalfocusview.gfx` with that one sprite changed to its own picture (the mockup's red medallion) and
  its shines dropped (`validate_preview` lets the rest of a copied game .gfx keep the game's textures, and so does
  Valsora's `check_mod.py`: a game sprite may name a texture the mod doesn't ship, unless it is in a folder of ours).
- The focus in progress has the mockup's ring of gilt rays behind it (`continuous_glow`, `GFX_ongoing_focus_goal`:
  `ongoing_focus_goal.dds`, 3 frames of 150 px the game blends); the search highlight is the same ring in jade.
- The links (`focus_link_*.dds`, 4 frames of 16 px: the game's green frames 1-2 are bright gilt, its blue-grey 3-4
  dim bronze, 2 and 4 dashed) and the exclusive marks (`focus_link_exclusive.dds`: a red diamond with a cross, small
  red diamonds at the ends; the lines red) are replaced at their paths and sizes (`SAME_SIZE`). Which link frame
  means what is **(assumed)**: green for a completed prerequisite.
- The filter chips, search box, zoom and close sit on one row at the header's right; the legend shows the mockup's
  four marks. The tree's geometry (focus spacing 96 x 130) is the game's, so links show only in the 12 px between a
  plate and the next medallion.
- `preview_focus.py` draws it over the top bar with Rouental's tree, the game's icons and the mockup's states.
- **Conflict:** the Valsora mod ships the same file path, so the UI mod must load **after** Valsora.
  If Valsora's `countrypoliticsview.gui` changes, re-run `make_politics.py`.

**make_leadergroups.py (v0.7).** The army bar. Everything but the counts is textures at the game's paths and sizes
(`gen_textures.py`, the `lg_` keys; their numbers, and the counts', in `layout_armybar.py`): the army card frame
(84 x 117, 4 frames: normal, selected, then both without the plaque, the game's order) and the army group's (90 x 126,
3: normal, selected, plain) are lacquer with an arched opening over the portrait, gilt rims and a plaque for the count
(selected: a jade line, a jade glow round the opening, a jade plaque); the plate pieces (army group 175 x 151 = two
frames of 87.5 px, the game's own odd size; mid 80; end 84 with the chamfered end) fade into the map below a gilt rule;
play and stop chips in the game's 4-frame order (normal, hatched, lit, lit and hatched; an army group's frames 3-4
show a double triangle and two squares); the battle plan's 12-frame chevrons; the empty card (a gilt bust and a plus,
drawn on the opening's centre since the game places the picture 1.5 px left of it); the HQ alert (frame 2; frame 1
is the blink's blank); the HQ badge and the staff-office strip recoloured with `gilt()`. The script itself only gives
both `divisions_count` boxes the plaque's box, centred both ways, in `valsora_deco_value_17` (the game's sat 3 px above
the plaque). `preview_armybar.py` draws the game's look and the mod's, the plate as the game lays it.

**make_events.py (v0.7).** The events. The pictures are textures at the game's paths (`ev_` keys): the country
event's top (581 x 121: a crest on the card's top edge, the title's band between two gilt hairlines), middle (a
cornered tile 580 x 66 the game stretches to the text: only the side rails, so it repeats seamlessly) and bottom
(581 x 206: a gilt frame round the 210 x 176 picture at (5, 5), the chamfered foot); the options' plate (352 x 48, it
overhangs its 300 px entry as the game's does); no paper clip; the minimize diamond; the news broadsheet (528 x 595:
WORLD NEWS masthead, the picture's frame at (59, 91), a rule over the headline, since the story starts right under
it at y 291) and its picture overlay; a leader event's arched portrait frame (172 x 232). The script sets the fonts
(the game's typewriter fonts are dark, for paper): titles `valsora_deco_title_18`, the text and the options
`valsora_deco_body_15` (in the menu's tracked capitals 811 of the game's 10,171 options would need a third line,
which the 40 px box cuts off; 4 in the body font). `preview_events.py` draws a country event and a news event.
v0.8: the option plate is `layout_events.OPTION_W` (334) wide inside the game's 352 px picture, the entry and the grid's
slots as wide, and each window's `options_grid` is moved so the plates sit in the middle of the room beside the
picture (`layout_events.CENTRES`: 12 px either side in a country event); a leader event gets the country event's foot
and no paper clip (`event_report_bottom_win_2.dds`, `events/clip.dds`); `preview_events.py` draws a leader event too.
v0.8.1: the news page's picture and overlay (x 64), headline (x 19) and story (x 34) are centred on the page
(`layout_events.NEWS_*`; the game's picture and headline sat 5-7 px left of its middle, the story's box 5 px right),
under the masthead
(`layout_events.news_masthead`: `NEWS_WORDS`, `NEWS_VIEW`, sizes).

**game_fonts.py (v0.8).** The game's 28 fonts redrawn at their paths (`gfx/fonts/<name>.fnt/.dds`), so the screens the
mod hasn't re-laid read in the deco faces: Josefin Sans for Ubuntu, Century Gothic and the typewriter, Federo for
Garamond, Federo capitals for Orator. `GAME` holds each one's face, weight, rim (the game's shadowed `..mbs`/`..bs`),
capitals, tracking and size. The sizes come from `--measure`: the largest whose text is no wider than the game's for
95 % of 4,000 of the game's English strings, and at most 5 % wider for 99 %. The deco faces are wide with a small
x-height, so they come out 2-5 px under the game's nominal sizes (Josefin bold costs another half pixel, so text is
600, not 700); tooltips grow with their text, so `cg_16b` keeps the Deco UI's 15 px. Each keeps the game's line height
with its capitals centred where the game's are (`gen_fonts.build(line=...)`), on the smallest atlas that fits
(`gen_fonts.fit_atlas`). Only `gen_fonts.CHARS` is drawn (Latin); the game's Cyrillic and CJK files stay its own.
`validate_preview` loads them with the mod's fonts, and judges their text against the game's own widths
(`GAME_W`, section 9). `preview_game_fonts.py DIR` draws each beside the game's, given the game's font textures in
DIR (the sparse copy of the game leaves them out: fetch the `gfx/fonts/*.dds` needed into a scratch folder, never
into the repository).

**gen_textures.py** (v0.8) redraws only what changed: each texture's signature (its HTML, size, format, fonts, CSS and
the files it embeds, with the project's own folder written `<root>`, so it is the same in any clone) is kept in
`texture_manifest.json` (committed with the textures; `validate_preview` reports a texture in the mod that it doesn't
list as stale), and a texture whose signature matches and whose file exists is skipped. `--all` redraws all;
`gen_textures.py <prefix> ...` those whose key starts with a prefix (`lg_`, `ev_` ...); `--sign` draws nothing and
records the textures on disk as drawn from today's code (after a change to the signature itself). A redraw changes a
few anti-aliased pixels: `restore_noise.py` puts those textures back.

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

When it runs itself (build_all's step), it then renders a top bar preview from the generated files; the preview
scripts import it for its loaders and renderer without redrawing that (v0.8.3). A new screen's .gui is covered by the
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
GP.write_gui(MOD + "interface/x.gui", t)    # braces checked, engine_safe applied, UTF-8 with LF
```

- Paths use names. `a>b` means b is a **direct child** of a, and `a/b` means b is **any
  descendant**. Every lookup asserts exactly one hit, so ambiguous names need a longer path.
- `set_attrs` formats `position`, `size`, `slotsize` and `max_slots` from tuples, and quotes
  strings for `font`, `sprite`/`spriteType` and `text`. `Orientation` and `Origo` stay bare (until
  v0.4.5 it quoted `Orientation`, which the game rejects on containers). It edits the element's
  **own** attributes, never a child's. `own_region` cuts at the element's final `}`. An earlier bug
  appended attributes after the closing brace.
- Comments are stripped before matching. Matching is case-insensitive on type keywords.
- Write every generated .gui with `GP.write_gui`, never a plain `open().write()`. It checks the
  braces and runs `engine_safe`: orientations unquoted, a container's `alwaystransparent` moved into
  its background (section 6). Files are UTF-8 with LF, which the game reads fine.

## 9. Pitfalls already hit (do not repeat)

- Stretching flags makes them pixelated. Keep them 1:1.
- A view the game puts at the screen's left edge under its top bar is drawn under the Deco UI's top bar, so the
  medallion hides its top (the armies, air wings and operatives in v0.8.1, the navy in v0.8.3). Side panels and the
  tech tree are drawn over the top bar instead. A new map-level view in that corner goes in `make_mapviews.py`.
- A picture the game lays out overlapping (the large tabs, 250-256 px apart for 258 px pictures) needs room drawn
  in: the game's slanted tabs hid the overlap, our chamfered bars didn't (v0.8.3, the captured commanders).
- Lacquer at 97 % shows the map's names through it (v0.8.3, the focus header): panels and headers are opaque.
- New sprite names can collide. Prefix everything `GFX_valsora_deco_<screen>_...` and check with
  validate.
- A new font must also be listed in `make_topbar.FONTS`, which writes `valsora_deco_fonts.gfx`,
  or the game will not know it.
- Text boxes that are too short silently drop the second line. Size boxes for 2 lines where names
  can wrap.
- A quoted `Orientation` on a container hid the whole main menu row in v0.4.3 and v0.4.4: the game
  rejected it and kept `UPPER_LEFT` (section 6). v0.4.4 changed `Origo` instead, guessing from a
  screenshot; the user's `error.log` named the real cause at once. Ask for the log first. The
  previews cannot catch this kind of bug, because they read the files with our own parser; the
  validator's vanilla-based syntax check can. `preview_screens.preview_menu` also asserts the panel
  has no Origo and fits on a 1920x1080 screen.
- Never `rm -rf` with relative globs after a `cd`. Use absolute paths, and use `unzip -o` into an
  absolute directory.
- Long-name detection must use only name keys (`TAG`, `TAG_<ideology>`, cosmetic tags). Matching
  any loc key that starts with a tag flagged the wrong countries.
- When merging into the Valsora mod (section 11), `make_politics` must not read its own output.
  Keep a pristine copy of Valsora's original `countrypoliticsview.gui` as the base (done since v0.5:
  `work/deco_base/`, kept by the Valsora build; `make_politics.py` asserts its base is not its own output).
- A .gui the mod ships at a vanilla path can name a sprite nothing defines, because the game's own file does
  (`countrydecisionview.gui`: `GFX_category_end_bg`). The checks skip those (the Valsora repository's
  `source/vanilla/index/gui_undefined_sprites.txt`, made by `scripts/vanilla_sync.py`).
- Two-frame sprites do not agree on which frame is lit: tabs (`tab_large`, `intel_ledger/tab`), the diplomacy
  filters and `sort_button_100x29_2` are lit in frame 1 (`countrytechnologyview.gui` starts its shown tab at
  `frame = 1`); `sort_button_202x29`, `sort_button_83x29` and `generic_checkbox` in frame 2. Look at the
  game's texture before redrawing one.
- The game's map mode icons are picked by frame number, and their meaning is not written anywhere: keep
  their order and glyphs (v0.5 recolours them; the big four are land, air, naval, intelligence).
- Uneven letters in a preview are the renderer's before they are the font's. Until v0.7 `draw_text` rounded each
  glyph's half-pixel position on its own (Python's `round()` takes .5 to the even number), so centred text read
  "Postpon e th e count."; a line now starts on a whole pixel, as the game draws it. The fonts' advances are whole
  pixels, and Pillow draws glyphs only at whole pixels too (an offset under .5 is ignored).
- A box narrower than its text says nothing by itself: many of the game's are narrower than the game's own text (the
  logistics panel's "Military Factories": an 80 px box, 107 px in the game's font). Since v0.8 the checks judge a game
  font's text against the game's own width (`validate_preview.GAME_W`, from the game's `.fnt`) and flag it only when
  ours is wider than the box and than the game's (by 5 %), or needs more lines than the game's; the side panels'
  "game's look" previews draw the game's fonts in an approximation and don't check them (their textures aren't in the
  repository). `preview_panels` looks up button texts in the game's localisation, fills `$VARIABLES$` with "12" and
  breaks lines at `\n`: before v0.8 it measured the raw keys ("ARMY_SORT_GROUP").

## 10. Open items and things to check in game

Check these first in the user's next screenshots and `error.log`:

- **v0.8.4**: the focus tree's title in its header and nothing over the first row; its header opaque; the lower left
  arrow in the deco style; the decisions seal's count badges (grey, red with a time limit); the captured commanders'
  two tabs apart; an empty general card's plus on the chest; no "does not match previous fontfiles" in `error.log`;
  Plaija's Vietnamese names drawn whole (tooltips, the politics screen, a general's card); a long name under the flag
  (the Kampfian Empire) in the small letters; a selected fleet's panel below the medallion, its list ending on screen.

- **v0.8.3**: the news masthead's ringed globe at its size; a superevent's crest, the whole ringed globe across the
  frame's top edge; the event card's keystone, its diamond clear of the top step.
- **v0.8.2**: one title on a superevent and its globe crest; the keystone on an event card; a long option's three
  lines inside the plate; a two-line name under the flag (Kampf, the Utopian Republic); an army's badge (select some
  divisions), the air wings and an operative below the medallion.
- **v0.8 fonts**: text everywhere the game's own fonts draw it (tooltips, lists, the designer, the leader and unit
  screens, settings, window titles): readable, nothing cut short (a box the deco face doesn't fit drops the end of
  its text or its second line); a tooltip of the ruler's portrait (Roland's titles: the user's example).
- **v0.8 layout fixes**: the army bar's play / stop row centred over each general, the plate behind it; an event's
  options centred between the picture and the card's edge.
- **v0.8.1 news**: the VALSORAN (globe) STANDARD masthead and the page under it centred (picture, headline, story,
  option). Rouental's "Test Events" decisions (the Valsora mod's `scripts/test_events.py`) fire one of each event window
  (country, long country, state, news, major news, leader, operative) and the test superevent.

- **v0.7 army bar**: a selected army (jade frame and plaque), an army group with its armies (one plate from the
  marshal over his armies), the counts centred on the plaques, a battle plan prepared and running (the chevrons), an
  army without a commander (the bust and plus centred in the opening), the HQ alert. Which of the frames' four
  pictures the game uses when (with or without the plaque) is the game's own order, kept.
- **v0.7 events**: the title, text and options readable (the mod's fonts), the middle stretching with the text, the
  picture in its frame, the options' plates (hover), a news event's broadsheet; a leader event's portrait frame.

- **v0.6 focus tree**: the window flush under the band with the medallion and seal in its notch; the title
  ("Rouentaise Focus Tree") and the full name and sub-ideology under it (if they don't show, the scripted GUI's token
  failed); the chips, search, zoom and close on one row; each focus's medallion behind its icon in its state's look
  (grey unavailable, jade available, red in progress with a gilt halo, gold completed with a check); the links gilt
  (bright from a completed focus), the exclusive marks red; the scale pattern and the frame; the legend.
- **v0.5.2**: a side panel opens and closes at once, nothing of it left on screen when it is closed (the division
  overview and the windows beside the panels especially); the main menu's career profile star on the button's corner.
- **v0.5** (the README's checklist has the user-facing version): each side panel's notch (medallion, name and
  seal visible, gilt edge, no map between), its title, close and header buttons, nothing cut off at the
  bottom (logistics, officer corps, faction, research), the construction screen with its list folded, the
  windows beside the panels; tabs and sort buttons in both states; the map mode medallions (land, air, naval)
  and the gilt small icons and toggles (on vs off); the gilt minimap, its camera frame, handle and pings.

0. **error.log (v0.4.5)**: no "Not a valid orientation" or "Unexpected token: alwaystransparent" lines
   from this mod's files. Any other line naming one of its files is the next bug.
1. **v0.3 top bar fixes**
   - flags are crisp
   - the market button has the deco icon
   - the logistics tray and XP badges read well
   - the globe is centred in its ring
   - alerts sit below the band and do not cover the tray (coordinates may be off by about 4px:
     topbar-local vs screen)
   - Terrabis-Seran and other long names use the small font on 1-2 lines
2. Daily political power format `+=2` shows like "+1.80".
3. **Z-order (answered, in game v0.4.7):** side panels draw over the top bar. v0.4.8's politics panel
   leaves a notch for the medallion; check the seal still opens decisions with the panel open, and that
   the header's empty parts don't click through to the map.
4. **Politics screen (v0.4, v0.4.8)**
   - (v0.4.8) the panel flush under the band; medallion, name and seal visible with the gilt edge round
     them, no map between; the decision counters either side of the seal; the deco header art (not
     vanilla's); tooltips in the deco frame; the sub-ideology and its tooltip; "None" for no elections;
     Devlon's 15 test spirits as small icons in the spirits card
   - every scripted value shows: ruling party · %, last election, political power and daily change,
     faction role
   - the pie (own, radius 44 since v0.4.8) sits in its ring; the legend diamonds take the party colours
   - the ideology icon in the chip (scale .34 is a guess)
   - the faction card's frames (1 in a faction, 2 create)
   - the focus card opens the focus tree; its progress bar fills; the "choose a focus" glow
   - the spirits switch to small icons past 8; the advisors & laws list scrolls and reaches the bottom
5. **Top bar (v0.4)**: the decisions seal opens decisions and shows its count badges and glow; the
   faction crown swaps between the plain and the in-faction version and shows the logo.
   **(v0.4.5)** command power, nukes and the army / navy / air buttons sit at the right end (until
   v0.4.4 the game rejected their anchor, so they were off the left edge); hovering political power
   and the factory counts still shows their tooltips (the scripted text windows sit over them)
6. **State panel**: the new background covers the province part too (the game's container is only
   496 tall; the picture is 650); building tiles line up with the building pictures; what the
   game's "owner" text says (it is used as the subtitle); the population icon's size at scale .55;
   resources with two rows do not run into the slots line; resistance (occupied states) next to
   claims
7. **Focus tree**: plates line up with the focus names and links; the medallion sits behind the
   icons; filters show on/off; the legend does not hide anything important; the search box and
   buttons under the header band respond (its click-through is on its background since v0.4.5)
8. **Main menu**
   - **(v0.4.5 fix)** the button row now shows along the bottom, centred at 16:9 and other ratios
   - the social links sit in the top-left corner **(in game, v0.4.4, done)**
   - the background manager shows the Valsora background **(in game, done)**
   - the single player sub-panel looks right
   - the version label is readable
9. Toolbar buttons have 2 frames. Frame 2 is drawn "lit" (jade) on the assumption that it is the
   active state.
10. Without La Resistance, the game shifts buttons after intelligence. Check for overlaps.

Still vanilla art:

- the world tension globe's glow (the globe itself is Valsora's own since 2026-10-14, drawn by the
  Valsora mod: `gfx/interface/world_tension_icon_big_strip.dds`, 10 frames, and the small
  `world_tension_icon.dds`; do not replace those here)
- the supply icon
- the achievements and dismissed-alert buttons
- the count badges on the menu buttons
- the music player pop-out
- faction logos
- focus icons (on purpose: the user's request)
- every screen other than the politics screen, state panel, focus tree and main menu (core skin only)

## 11. Integration: part of the Valsora mod (v0.5)

The user asked (2026-10-14) for one install, keeping the option of going back to the game's interface. So:

- **The Valsora build takes the Deco UI in.** `scripts/deco_ui.py` (run by `scripts/run_all.sh` after
  `build_mod.py`, when `DECO_UI = True` in `scripts/common.py`):
  1. keeps Valsora's own copies of the files the Deco UI replaces (`REPLACES`: only
     `interface/countrypoliticsview.gui`) in `work/deco_base/`;
  2. runs `long_names.py` and `make_politics.py` against that build (environment `VALSORA_MOD_DIR`,
     `VALSORA_BASE_DIR`), so the long-name trigger and the politics screen with its sub-ideologies always
     follow Valsora's countries and ideologies. Both need only Valsora's files and this project's fonts;
  3. copies `valsora_deco_ui/` into `build/valsora_test/`, all but `descriptor.mod`, `README.txt` and
     `thumbnail.png`. A path both mods ship stops the build unless it is in `REPLACES`. Running it twice is
     fine (`work/deco_base/copied.txt`).
  `scripts/check_mod.py` then checks the merged mod (it knows the Deco UI's 9 languages, its politics screen's
  five 19 px party rows, every sprite kind in a .gfx and the game's own undefined sprites).
- **The minimap** is Valsora's (`scripts/minimap.py`): with `DECO_UI` it draws the picture and frame in this
  style (gilt land and coasts on lacquer, a gilt frame) at the same sizes, and the start date picture too;
  this project only ships the handle, ping buttons and pings (`gfx/minimap/`, vanilla paths Valsora doesn't use).
- **Everything else** (textures, fonts, the patched game screens) is built here by hand with the game's files
  at hand (`tools/build_all.py`) and committed in `valsora_deco_ui/`; the Valsora build copies what is there.
  Rebuild it after any change to the tools, then rebuild Valsora.
- **To go back to the game's interface:** `DECO_UI = False` and rebuild. `build_mod.py` empties the build
  first, so none of this project's files remain, and the minimap is parchment again.
- `valsora_deco_ui.mod` and `descriptor.mod` stay (v0.5.0) for the separate-mod form (option A before
  v0.5: it had to load after Valsora, `dependencies = { "Valsora (test map)" }`), which `tools/package.py`
  still zips; nothing ships it now. The user was told to delete the old separate copy from `mod/`: if left in
  the playset it loads after Valsora and puts its older files back.

## 12. Next steps (in order)

1. Process the user's screenshots and `error.log` of v0.5.2 to v0.8 (section 10 and the README's checklist): the
   side panels, the focus tree, the army bar, the events, the fonts.
2. Any text the deco faces don't fit in game: shrink that font in `game_fonts.GAME` (or widen the box in the screen's
   `make_*.py`), rebuild.
3. Politics extras still missing from the Government mockup: faction member flags (needs a scripted
   GUI dynamic list over the faction's members; not verified that one exists) and a one-spirit card
   with its modifiers. The user does not want "The Court" panel.
4. The side panels' insides (v0.5 did their frames, headers and the shared pieces): the game's pictures
   inside them (research's photograph, `production_win_top`, the officer corps' coloured command boxes, the
   intelligence agency's art, `overview_top_strip`) and the +/- buttons; re-lay a panel only if the user asks.
   v0.7: proposals for the pictures in `art/proposals/` wait for the user's approval (the user: "don't put them in
   the mod yet. I'd like to see and approve them first").
5. Focus tree, after the user's screenshots of v0.6: what the mockup has that the game's window lacks (the focus in
   progress and its days in the header, a progress bar under the focus, the "on completion" list in the tooltip)
   needs scripted GUIs or can't be done; the superevent is done (Valsora's `scripts/superevents_deco.py`).
6. HD flags experiment (section 6), only if the user wants it: the mockup and what it would take are in
   `art/proposals/hd_flags/`.

For every new screen, follow this pattern:

- write a `layout_<screen>.py`
- write a `make_<screen>.py` that patches the game's file with `guipatch` and keeps every element
- add the textures in `gen_textures.py`
- add the sprites to a `valsora_deco_<screen>.gfx`
- add the loc keys in 9 languages
- extend `validate_preview.py`
- add a preview in `preview_screens.py` (or `preview_panels.py`, which draws the game's own textures)
- add the step to `build_all.py`
