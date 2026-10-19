# Problem log

Every error and problem met while building the Valsora mod, what caused it and how it
was fixed, newest first. Add to it whenever something goes wrong, in game or in the
build. "Check" means `scripts/check_mod.py` now catches it, so it can't slip back in.

## In-game problems (reported by the author)

**The production lines had no boxes, the trade rows had specks and stray lines** (2026-10-19, the author's screenshots of
v0.11: "The production screen doesn't have any boxes", "Trade screen has off artifacts and lines")
- Cause: v0.11 put the side panels' drafted pictures in the mod as `make_panel_pictures.py` makes them, the game's
  pictures translated automatically into the Deco palette (`proposals_panel_mockups.translate`). On the production line
  it found none of the boxes (the equipment's plate, the 15 factory slots, the resource wells: their edges are faint
  in the game's metal) and on the trade row (three frames side by side, which it read as one picture) it took the
  metal's scratches for the thin bright lines it gilds.
- Fix: those five pictures drawn by hand from the game's measured layout (`deco_ui/tools/production_art.py`), left out
  of the translation (`make_panel_pictures.DRAWN`). A picture of boxes in a textured metal wants drawing, not
  translating; the other translated pictures are worth a look in game for the same faults.

**The music controller popped in out of nowhere** (2026-10-19, the author: "make it fit in better as currently it just
kinda pops in our of nowhere")
- Cause: the game slides its strip in from the right, out from under its own top bar's picture; the Deco UI had kept
  that slide under its tray, where there is nothing for it to come out of.
- Fix: a tab hanging from the tray under the music button, sliding down out of the tray, which is drawn after it and
  hides it there (`music_art.TAB`, `make_topbar.py`).


**The diplomacy tab didn't match the politics screen** (2026-10-18, the author's screenshots of v0.10.4: "the box isn't
aligned with the flag. Focus icon isn't centered ... larger portraits like Krionik's start to get cut off")
- Causes: the flag's frame was 68 px tall and 3 px under the 71 px bar beside it; the left wells were drawn 5.5 px off
  the column the game centres its pie and focus icon on; the arch's opening was narrower than the portrait and cut the
  top corners of a square one (Krionik's seal); the names' boxes ran under the opinion box.
- Fix (v0.11): the frame the bar's height and level with it; the wells on the game's column; the portrait at 0.66 under
  a flatter arch; the names cut at the opinion box. When a picture sits beside or around one the game places, take its
  edges from the game's numbers, not from the picture.

**The logistics numbers ran into each other** (2026-10-18)
- Cause: in game the values' capitals sat 2 px lower than `layout.py` modelled, 1 px under the bar of the row above.
- Fix (v0.11): the values 2 px higher, the bars 3 (`layout._strip`).

**The decision plates sat a pixel or two low** (2026-10-18)
- Cause: their tops were on the step, under the gilt rule the step draws.
- Fix (v0.11): 2 px taller upwards (`layout.DEC_RAISE`), the bottoms where they were.

**Myehn's islands stuck together** (2026-10-18, the author's screenshots)
- Cause: islands the author drew apart touch by necks of land a few px wide (from the earlier scaled-up drawing), so the
  game took them for one landmass.
- Fix: `pdn_tools.py necks MYH` (7 necks) and two channels by hand (Myehn 23's narrow southern island, Shukumei's
  island off Myehn 36): 5 strait crossings link them as before (`straits.py`, up to 10 px as approved).

**A Gazetteer portrait off centre** (2026-10-18, the author: "earlier one of the portraits was off center. I think it
was Port Almohavid?")
- Cause: `gazetteer.portrait_box` cut HOI4's 156:210 from the middle of a wide picture (the top of a tall one), wherever
  the person stood: Usamah Lakhdar stands at the left of his 640 x 414 photo, so the cut took his right shoulder and
  the wall; the full-length photos (Szalai Diána seated, László Vilmos at a lectern) came out as small figures.
- Fix: the import finds each picture's face (OpenCV, kept in `source/gazetteer/faces.json`) and the cut is head and
  shoulders round it (`docs/GAZETTEER_INTERNALS.md`); all 14 portraits checked on a sheet, before and after.

**The decision counts were still round dots** (2026-10-18, the author's screenshot of v0.10.2: "The notification is
still a dot, rather than the shape I specified")
- Cause: their picture of 2026-10-17 outlined each shoulder of the medallion in red ("Maybe move the notifications on
  this screen to something like this"), the outline being the shape they wanted; v0.10.1 read it as a place and only
  moved the game's round badge (`topbar_alert_bg`, shared by every count in the top bar) into the shoulders.
- Fix (v0.10.3): each decision count has a plate of its own the shape of its shoulder, the corner by the seal cut off
  (`layout.DEC_PLATE`, `GFX_valsora_deco_dec_count_left` / `_right`), the number centred on it. A drawn outline is
  read as the shape asked for unless the author says otherwise.

**The flag file "is corrupted"** (2026-10-17, the author: "my most recent version of the flag pdn is corrupted. I'm not
sure yet whether it was a fault on your end or mine"; 2026-10-18, sending their own copy: "If it's not corrupted,
maybe it's being generated for a different update of PDN?")
- Cause (found 2026-10-18): ours. Every flag file we wrote since 2026-10-13 (94, 99, 100 and 101 layers) was refused
  by paint.net, so the author kept working in their own 90-layer copy (the one they sent, identical to the file we
  were first given). `writepdn._add_layers` numbered the new layers' blend modes (a value type, written with a
  negative id) from the lowest id down (-831, -832 ...) and their other objects from the highest up (829, 830, 831
  ...). .NET's BinaryFormatter, which paint.net reads `.pdn` files with, takes a value type's -n as n, so -831 and
  831 were one object "registered twice" and the whole file was refused. .NET's own writer keeps one counter for
  both, so paint.net's files never have the clash. `pdn_check.py` and the 2026-10-17 tests compared ids as written
  and passed; the map `.pdn` was never touched by it (we never add layers to it) and opens.
- Found by reading the files with .NET itself: BinaryFormatter (the .NET 8 SDK, `apt-get install dotnet-sdk-8.0`)
  read the author's copy and the map and refused all four of ours with "An object cannot be registered twice".
- Fix: `_add_layers` gives every new object, the blend modes too, the next number from one counter (a blend mode its
  number negated); `pdn_check.py` compares ids by absolute value (it now fails our four old files);
  `scripts/pdn_dotnet/` reads a `.pdn` with BinaryFormatter and NrbfDecoder, and `writepdn.py` runs it on every file
  it writes where .NET is installed. The flag file was written again on the author's own copy, with our 101 layers
  (the same pixels, names and visibility): BinaryFormatter reads it, and adding 1, 3 and 50 layers (the layer list
  growing) reads too. Sent as `New_Mod_Flags 10-18.pdn`.
- Earlier (2026-10-17), before the cause was known: `writepdn.py` reads every file it writes back with
  `pdn_check.py` and refuses to leave a bad one; `scripts/pdn_recover.py` pulls every layer still whole out of a
  damaged `.pdn` into PNGs.

**The Gazetteer's password search lost the cursor at every letter** (2026-10-17, the author: "it kicks me out of the
bar, making me reclick it after every letter")
- Cause: each letter redraws Owner tools; the search box was focused again while its section, rebuilt closed, was
  still shut (its open state was put back afterwards), and a field in a closed section can't take the focus. The tests
  filled the box in one go, so they never saw it.
- Fix: the sections open as they were before the field is focused again (`renderOwner`), for the map tools' search
  too; `tests/gazetteer/run.py` now types letter by letter and checks the cursor stays (it failed before the fix).

**The fleet panel's names ran off** (2026-10-17, the author: "Names run off screen")
- Cause: a ship row's type line ("Advanced Destroyer (Advanced Destroyer I)", 254 px in our `hoi_18`) is cut ("...")
  where the row's insignia begins, 240 px from its start (the game shrinks the box in code; inferred from the
  screenshot); the admiral's name ran past the name frame the fleet picture draws, under the skill badge; the home
  base was still in the game's own font, too wide for 3 of Valsora's 63 city names.
- Fix (Deco UI v0.10.1): the ship type and the admiral's name in `Main_14_bold` (the Deco UI's Federo 12.5 px), the
  name up to two lines inside its frame, the home base in `hoi_16mbs` (`make_mapviews.TEXTS`); `preview_navy.py`
  copies the game's cutting and checks every text against its room. The longest type ("Advanced Heavy Ship (Advanced
  Heavy Ship II)") is still cut by 2 px, as the base game cuts it.

**A news event's text ran over the page's rule** (2026-10-17, the author: "Text on event runs over")
- Cause: Cardonia's capitulation story starts with a blank line, so in `body_15` it took 13 lines, from y 291 to 499,
  over the rule and diamond the news page draws at y 485-500; the option stays at y 505. 11 of Valsora's 27 news
  stories would run over.
- Fix (Deco UI v0.10.1): the story in `valsora_deco_body_13`; every news story Valsora ships ends by y 473 with the
  longest country names filled in. The country and leader events' text boxes, which drop lines past their height
  silently, were made 16 and 24 lines tall (two La Résistance events needed 15-16).

**The division designer's combat width wasn't centred in its ring** (2026-10-17, the author: "Combat width isn't
centered")
- Cause: the ring was drawn round (309, 249), but the game draws the number in `combat_width_view`'s 40 x 20 box at
  (290, 240), centred: its ink centres on (310.5, 250.5), 1.5 px right of and below the ring's centre. The game centres
  text at the box's x plus half the room left, rounded up; our previews rounded down, so they showed it 1 px off the
  other way.
- Fix (Deco UI v0.10.1): the ring, its sunburst and diamonds centred on the number (`designer_art.COMBAT_WIDTH`),
  measured against the author's screenshot pixel by pixel.

**The commander cards' skill was off centre and unreadable** (2026-10-17, the author: "Skill is not centered, and the
white won't show on the tan. I like the aesthetic though.")
- Cause: the game draws the skill white (`hoi_30header`) in a 50 x 18 box at (1, 19), its ink centred on x 26, rows 28
  to 40; the card's tan diamond was centred lower, at (27, 48), so the white number stood on the stripes above it.
- Fix (Deco UI v0.10.1): a dark lacquer diamond in a gilt rim where the number is (`designer_art.skill_diamond`, centred
  on (26, 34.5); the navy card's box is left-aligned, so its diamond is at x 25), the striped strip centred on it, and a
  lacquer channel between the strip and the portrait. A "1" on the navy card still sits 2.5 px left (the game
  left-aligns it there).

**The loading screen showed the game's own picture, and game setup a loading picture** (2026-10-17, the author's
screenshots of the Deco UI v0.10)
- Cause: v0.10 listed four loading pictures from Valsora's map in the menu's background list, assuming the loading
  screen drew from it (assumed, not known). It doesn't: it showed one of the game's own loading pictures (its Chinese
  front). The frontend (game setup) took the last picture of the list as its background instead.
- Fix (Deco UI v0.10.1): the list is the menu's picture alone again, and the four pictures are out of the mod, kept for
  later (the author: "The globe map should be kept for later ... the map's not finalized quite yet"; `make_loading.py`
  draws them into `deco_ui/build/`, `--into-mod` puts them back). Showing our own would mean replacing the game's
  `gfx/loadingscreens/load_*.dds` themselves (not tried).

**Corner brackets stuck out past the loading boxes' and the battle plan bar's corners** (2026-10-17, the author: "The
boxes for the loading screen have the little decoration sticking out of the corner"; "The corners are odd and sticking
out on this bar too")
- Cause: the deco corner brackets were drawn square over plates whose corners are chamfered, so their ends showed
  outside the cut corners.
- Fix (Deco UI v0.10.1): the loading bar and tip, the battle plan bar and its pop-ups have no brackets.

**The battle plan buttons' icons weren't centred** (2026-10-17, the author: "icons aren't all centered")
- Cause: the game's glyphs sit off centre in their own pictures, and v0.10 placed each picture, not its ink, in the
  well; a setting's lit frame also drew a second plate under the gilt one.
- Fix (Deco UI v0.10.1): each glyph is centred in its well by its ink's bounds (`battleplan_art.centred`), the lit
  frame is its plate alone. (The greyed fourth button in the screenshot is the game's disabled state.)

**"Other countries" stuck out past the country selection** (2026-10-17, the author's screenshot of the Vale of
Reibonne start)
- Cause: the game lays its 150 px country cards from x 15, eight to the 1225 px window; the Vale start has eight
  nations and "Other countries", nine.
- Fix (Deco UI v0.10.1): `make_setup.py` widens the window to 1375 px (75 px each side, since it is centred), moves
  everything under the cards back where it was on screen and the more-countries button with the right edge, and the
  picture is drawn at the new width. guipatch.py knows neither `dropDownBoxType` nor `expandButton`: their lines are
  replaced by hand.

**Game setup's country details were "a little disorganized", and its ideology wheel unlike the politics screen's**
(2026-10-17, the author's screenshot)
- Cause: the portrait, faction emblem, wheel and spirits stood 9, 3 and 7 px apart on different lines, the emblem's
  well and the wheel overlapping; the wheel's ring and centre were the game's shapes recoloured.
- Fix (Deco UI v0.10.1): the four on one centre line 10 px apart; the wheel's ring (gilt, a dark inner rule) and its
  dark centre with a gilt rim as on the politics screen.

**The top bar's logistics values were a little big for their cell** (2026-10-17, the author: "maybe shrink the text on
it just a little so it fits better?")
- Fix (Deco UI v0.10.1): a new 11 px value font for them (`valsora_deco_value_11`; 12 px before).

**No names on the map** (2026-10-16, the author: "Names seem to have disappeared in the new build")
- Cause: `error.log`: "Failed to load texture larger than MAX_TEXTURE_SIZE: gfx/fonts/hoi_mapfont4.tga". The Deco UI's
  map font (it replaces the game's at its path) got the Vietnamese letters with every other font in v0.8.4, and its
  atlas grew from 2048 x 1024 to 2048 x 2048, which the game refuses: no font, so no country, state or region names.
- Fix (Deco UI v0.9.1): the map font leaves the Vietnamese letters out (no name on the map uses them; 333 glyphs,
  2048 x 1024 again) and `gen_fonts.py` stops if it would grow past that. Check: the map font's texture size, and
  every letter of the names the map draws (countries under each government, states, regions, victory points) in it
  (`check_mod.py`, mutation-tested).

**The designers' statistics were white on the ivory sheet** (2026-10-16, the author: "The text on the unit designer
can't be seen w/ white on tan")
- Cause: v0.9 drew an ivory sheet where the designers write their statistics, in the game's `hoi4_typewriter*_inverted`
  fonts. The game's own `_inverted` textures carry dark ink (they are coloured white); ours, redrawn in v0.8, were
  white glyphs, which had read on the game's dark metal.
- Fix (Deco UI v0.9.1): the two `_inverted` fonts have the ink baked in (`game_fonts.INK`).

**The doctrine screen's tabs ran into the name under the flag** (2026-10-16, the author's screenshot)
- Cause: the tabs' grid (`folders_grid`) was placed right of the notch, but the game drew the tabs about 125 px further
  left. The grid had no `format`; the game seems to centre a grid's items without one (assumed).
- Fix (Deco UI v0.9.1): `format = UPPER_LEFT` on the grid. Not yet seen in game.

**A long faction name was cut off on the faction screen** (2026-10-16, the author's screenshot)
- Cause: the name's box was the game's 300 px; "The Association of Reibonnaise States" is 323 px in our heading font.
- Fix (Deco UI v0.9.1): 326 px, starting right of the notch (`layout_panels`, `inner_attrs`).

**The faction card's LEADER tag was off centre; the seal's two badges sat unequally far from it** (2026-10-16, the
author's screenshots)
- Cause: the tag's text box was taller and wider than its plate, left-aligned; the timeout badge was 2.7 px from the
  seal and the other 4.7 px.
- Fix (Deco UI v0.9.1): the text box is the plate, centred both ways; the timeout badge 2 px further left. The members'
  flags wrap to a second row now (up to 16; the author asked whether they would).

**An "odd green bar" between Construction and Production; the music button against the tray's edge** (2026-10-16, the
author's screenshots)
- Cause: the bar was the game's production alert (`production_button_glow`), drawn by v0.2 as a gilt halo 8 px larger
  than the crown, behind it: only the 6 px gaps either side showed it, dark green over the lacquer. The right-hand
  tray's lower step was 2 px from the music button.
- Fix (Deco UI v0.9.1): the alert is a ring round the inside of the crown, drawn over it (pulsing, click-through); the
  tray's edge is 12 px further out.

**Plaija's Vietnamese names had missing letters** (2026-10-16, the author: "the font not including character for, for
example, Plaija's current nameset")
- Cause: the Deco UI's fonts held Latin-1, Latin Extended-A and punctuation only; a bitmap font draws nothing for a
  letter it lacks. Plaija's name list (the base game's Vietnamese) uses 25 letters outside that set (ơ ư ạ ấ ầ ế ộ ứ
  ...), and its communist leader is "Mai Đức Tài". Federo has none of them, nor Đ đ.
- Fix (Deco UI v0.8.4): every font has the Vietnamese letters; in Federo and Bodoni Moda they are composed from the
  face's own letters and accents (`gen_fonts.compose`). Check: every letter of the mod's English text and name lists
  must be in every font the mod ships (`check_mod.py`, mutation-tested). A specimen sheet of the built fonts then showed
  ỉ with the i's dot left under its hook (an i under a mark loses its dot now) and ă ĩ ũ (Văn, Nghĩa, Vũ) drawn in
  Josefin Sans inside Federo words, as fallbacks (now composed in Federo too).

**Long names under the flag rode up against its frame** (2026-10-16, the author: "for long names like Kampf")
- Cause: a name in two lines of the large letters (20 px each) filled the 40 px box, so its first line touched the
  flag's frame.
- Fix (Deco UI v0.8.4): a name that needs more than one line of the large letters takes the small cut (`long_names.py`:
  34 tags), whose two lines leave room above and below.

**The navy's panel was covered by the flag medallion** (2026-10-16, the author: "like the army, the navy is covered by
the flag tab")
- Cause: the game puts the selected fleets' panel (`naviesview.gui`'s `naviesview_window`) at y 82, under its own top
  bar; v0.8.2 moved the armies', air wings' and operatives' views below the medallion but missed this one.
- Fix (Deco UI v0.8.4): it starts below the medallion and the seal (`make_mapviews.py`), 77 % of the screen tall so it
  ends where the game's did; the home base and refit windows beside it move down with it. A survey of the game's .gui
  files found no other view in that corner under the top bar.

**The focus tree's title and subtitle sat on its first row of focuses** (2026-10-16, the author's screenshot of v0.8.3)
- Cause: the scripted GUI that drew them was docked with `parent_window_token = national_focus`, which the game puts
  inside the tree's scrolling canvas (`focus_tree_scripted_window_container`), not the window: the title landed ~124 px
  lower than planned, over the focuses, and would have moved with the tree.
- Fix (Deco UI v0.8.4): no scripted GUI; the game's own title (the tree's name, set by the game) is the large title in
  the header, under a "National Focus" label of ours. The subtitle (full name and sub-ideology) is gone.

**The map showed faintly through the focus tree's header** (2026-10-16, the same screenshot: a nation's name and
capital in the header)
- Cause: the headers' lacquer was drawn at 97 % opacity, as in the mockup's glassy panels; bright map text came through.
- Fix (Deco UI v0.8.4): the focus tree's header, the side panels' headers and their body tile are opaque.

**The focus tree's shortcuts arrow, the decision counts and the captured commanders' tabs were the game's look, or
overlapped** (2026-10-16)
- Cause: the arrow (`toggle_shortcuts`, the game's `production_line_arrow_left`) and the counts (`topbar_alert_bg`, 4
  coloured frames) were never redrawn; the large tabs were, but as full-width chamfered bars, while the game sets them
  250-256 px apart for 258 px pictures (its slanted tabs hide the overlap).
- Fix (Deco UI v0.8.4): the arrows and the count badges redrawn at the game's paths (gilt chevrons on lacquer chips;
  octagons in grey, red, gold and jade); the tabs drawn 4 px in from each side.

**The empty general card's plus wasn't on the chest** (2026-10-16, the author: "the + isn't quite centered on their
chest")
- Cause: the plus medallion (a 9 px square turned on its corner) reached up to the shoulders' apex.
- Fix (Deco UI v0.8.4): a smaller medallion (6.5-7 px) midway between the shoulders and the bust's foot.

**error.log: "base (13) in 'gfx/fonts/hoi_16tooltip3.fnt' does not match previous fontfiles in font 'cg_16b'"**
(2026-10-16)
- Cause: the tooltip font is two files, ours (`cg_16b`, redrawn in v0.8) and the game's `hoi_16tooltip3` (its Cyrillic);
  ours had base 14, the game's 13.
- Fix (Deco UI v0.8.4): every font the Deco UI redraws keeps the game's own line height and base (`game_fonts.py`; the
  glyphs' offsets are from the line's top, so nothing moves); `validate_preview.py` checks them against the game's.

**The superevent's title was "all jumbled together"** (2026-10-15, the author's screenshot of the test superevent)
- Cause: the Deco UI's superevent window has a baked title strip per superevent, and the scripted GUI gave a
  visibility trigger to each picture but none to the titles, so all eight drew over each other.
- Fix: `superevents.py` writes `valsora_superevent_title_<id>_visible` (the superevent's flag) when the window is the
  Deco UI's.

**A long event option's third line spilled out of its plate** (2026-10-15, the author's screenshot)
- Cause: the options were set in `valsora_deco_body_15` (a 20 px line) in a box made for two lines.
- Fix (Deco UI v0.8.2): `valsora_deco_option_14`, a 14 px line, and the text box the plate's height (42 px): three
  lines fit.

**The state test event did nothing** (2026-10-15)
- Cause: a `state_event` fired from a country needs `trigger_for` (the country it is shown to); without it the game
  shows it to no one.
- Fix: `trigger_for = controller`. Check: every `state_event` our files fire names `trigger_for`.

**The operative test event did nothing** (2026-10-15; the author: "Maybe because I have no intelligence agency?")
- Cause: right: without an agency there is no operative to fire it from.
- Fix: the decision gives Rouental an agency (`create_intelligence_agency`) and an operative first when it has none.

**Long names under the flag showed only their first word** ("KAMPFIAN ...", "UTOPIAN ...", 2026-10-15)
- Cause: the name's box was exactly two lines of the large letters high (2 x 20 px), and the game showed one line
  and "..." (Terrabis-Seran, one line, was fine).
- Fix (Deco UI v0.8.2): the box reaches 4 px above and below (`layout.NAME_SLACK`), so two lines fit; one or two
  lines land where they did.

**The selected armies' badges were covered by the flag medallion** (2026-10-15: "the army tab is covered up by the
country tab")
- Cause: the game puts them (unitview.gui's `armies_view`, "Request Expeditionaries" with it) at y 79, under its own
  top bar; the Deco UI's medallion hangs down to y 169 there. The air wings' and operatives' views sat there too.
- Fix (Deco UI v0.8.2): `make_mapviews.py` moves all three below the medallion and its seal
  (`layout.BELOW_MEDALLION`, y 173).

**Rouental's admiral, James Navy, wasn't in the game** (2026-10-15: "I can't seem to find John Navy anywhere")
- Cause: the Gazetteer's generals, admirals and advisors were only listed for the author (`gazetteer.py status`);
  the build made none of them.
- Fix: `gazetteer.characters` makes the generals corps commanders and the admirals navy leaders (skill 3, no traits:
  the page has no fields for them), with their portraits, recruited at the start. Advisors and others still need a
  slot and traits the page doesn't ask for.

**Deco UI: a closed division overview stayed on screen, headerless, over the map** (2026-10-15, author's screenshot)
- Cause: the game does not hide a closed side panel; it moves it back to its `position` and leaves it drawn there.
  Vanilla's `position` is off-screen (x -606), so nothing shows. v0.5.1 had set it 36 px below the panel's place, on
  screen, to make panels rise into place; a closed panel then stayed there (its sub-windows over the map). The
  v0.5.1 entry below wrongly said the game hides a window once it has slid back: vanilla's dropdowns rest at y -300
  or -2000 or inside a clipped parent.
- Fix (Deco UI v0.5.2): every closed panel rests at the game's off-screen `position` again (just off the left edge
  where the game's is on screen: `layout_politics.closed_x`), and opens and closes at once (`animation_time = 0`, as
  several vanilla dropdowns do), so nothing slides across the flag either.

**New game: Back on the country screen looped instead of returning to the menu** (2026-10-15, author's video)
- Cause: with a single start (bookmark), the game skips its "Select scenario" screen. Back on the country screen
  returns to that screen, which picks the only start at once ("Starting History...") and opens the country screen
  again.
- Fix: two starts on 1 January 2036, Valsora (Rouental, as the author asked, and Merlovich recommended) and the Vale
  of Reibonne (the Association), so the scenario screen stays and its Back returns to the menu.

**error.log: `valsora_reibonnaise_opinions: Invalid Scope ... provided: None`** (2026-10-15, the author's error.log,
10 lines in all, down from 2,081; this was the only one of ours)
- Cause: `on_startup` runs without a scope, and the scripted effect was called straight inside it.
- Fix: `random_country = { valsora_reibonnaise_opinions = yes }` (the effect goes through every country itself).
  Check: no scripted effect of ours called at the top of an `on_startup` effect.

**Main menu: a star over the career profile button's label** (2026-10-15, author's screenshot)
- Cause: the game's `career_profile_button_star` (shown when the career profile has something new) was placed at
  the button's right end, over the end of "CAREER PROFILE".
- Fix (Deco UI v0.5.2): a small badge (scale .6) on the button's upper right corner.

**Deco UI: a newly opened side panel slid over the flag and the country's name** (2026-10-15, author's video)
- Cause: every side panel slid in from x -606 to its place (vanilla's slide), and the windows beside them from
  -356; with the panels flush under the top bar since v0.4.8/v0.5, their header crossed the medallion before
  the notch reached it, choppily the first time a panel opened (its pictures loading), and the old panel slid
  out the same way when switching.
- Fix (Deco UI v0.5.1): they rise 36 px into place over 200 ms (`layout_politics.RISE`, `OPEN_MS`) and sink as
  they close. The notch narrows downward, so a panel lower than its place never covers the medallion or seal.
  The game hides a window once it has slid back, wherever that is (vanilla's dropdowns slide 25 px).
- Found while testing the Gazetteer's state capitals: a city's card put its buttons in a column beside its
  name, which the fourth button squeezed to a few letters; the name and the buttons now each take a row.

**Leftover placeholder bricks and grid states; Placeholdaire's map tools closed; Gazetteer gaps**
(2026-10-15, author's screenshots of the `.pdn` and the site)
- Squares by Xue, around the Associated Cities and Qinguo, and by Ungar: the lakes, still in the
  placeholder build's 48 px squares (four lakes, 2-10 each). Fix: `pdn_tools.py lakes`, each lake
  one province.
- Squares on Arvorenia's and Atrocha's islands and Kurikia's KU island: 87 land provinces still
  32 px bricks, with 96 px grid states, where no outline run had reached (the friend's build of
  2026-10-05; islands given whole with `give`). Fix: `pdn_tools.py recut` cuts them like an
  outlined patch (Kurikia's and a Belekria island group's single states kept). Found by
  provinces whose borders run 60 % or more on the brick grid; none are left.
- Placeholdaire was "not editable": an island with no line on it was two states (the edge of an
  old strategic region; San Sierra had one too, from the old 650 px state size), so the test for
  drawn states said no. Fix: each merged into one state (`pdn_tools.py attach`).
- The site counted only names typed on it ("0 / 56 named" for Rouental, named on the map), and
  showed none of Rouental's government flags. Fix: the export marks the states the map names
  (`named`) and carries the game's `TAG_<ideology>` flags; the page counts and shows them.
- Releasables picked provinces, which HOI4 can't core (cores, like formables, are per state).
  Fix: they pick whole states; the first ones' provinces count as the states they cover by half.
- Drawn states overlapped and ran into the sea and neighbours. Fix: Suggest › State keeps only the
  nation's land inside the line that no earlier state holds.
- Found while testing: on a phone the Suggest tool's hint, beside four chips (State is new), became
  a narrow column nine lines tall and squeezed the map to 85 px, so a tap landed on the boxes of the
  nation's other parts. Fix: on a phone the chips scroll in a row of their own and the hint sits
  below them in two lines (a tap shows the rest); the map keeps 230 px.
- Found on the way: `country_list.py` listed the 364 Earth tags the build has kept as stand-ins
  since 2026-10-14 (546 "countries"). Fix: it leaves out the base game's tags that aren't ours.

**Deco UI: the other side panels left a gap under the top bar and covered the medallion; two installs**
(2026-10-14, author)
- Every side panel but the politics screen still opened at y 78 (16 px below the band) and, drawn over the top
  bar, hid the medallion's lower part and the decisions seal. Fix (v0.5, `deco_ui/tools/make_panels.py`): the
  16 panels get the politics screen's treatment (flush at y 62, a notch the shape of the medallion and seal,
  the title moved right of it, the content moved below the seal) and the 17 windows that open beside them sit
  flush too. Check: the Deco UI's `validate_preview.py` keeps every element of each patched file, and
  `preview_panels.py` draws each panel with the game's textures.
- The Deco UI was a second mod to install, which had to load after Valsora (v0.4.5 loaded first). Fix: it is
  part of the Valsora build (`scripts/deco_ui.py`, `common.DECO_UI` to switch it off). The files it makes from
  Valsora's data (the long-name trigger, the politics screen) are made by the build itself, so a new country
  or sub-ideology can no longer leave them stale. Check: `deco_ui.py` stops on any file both mods ship that the
  Deco UI does not replace on purpose; `check_mod.py` checks the merged mod.

**The tension globe's fire "didn't come out too well"** (2026-10-14, author's screenshot at 100 %)
- Cause: flames were painted over the disc from below; at full tension the whole globe was a noisy
  orange blur with no shape left.
- Fix: `globe.py` burns it as vanilla's does: lava cracks (borders of random cells on the sphere,
  warped) spreading upwards, a dark red crust that keeps the globe's light and highlight, a molten
  glow from below (`dist/tension_globe_preview.png`).

**Deco UI: the politics screen covered the medallion, kept vanilla's header, unstyled tooltips**
(2026-10-14, author's screenshots of v0.4.7)
- The panel opened 16 px below the top bar's band and hid the medallion's name plate and the
  decisions seal: side panels are drawn over the top bar. Fix (v0.4.8): the panel sits at the band's
  bottom and leaves a notch the shape of the medallion and seal (they show through it); its own
  background lets clicks through and children outside the notch catch them.
- The header behind the portrait was vanilla's metal picture: the game swaps the `pol_view_bg` icon's
  sprite at runtime (`GFX_pol_view_bg` / `_no_dlc`), so ours never showed. Fix: both vanilla
  textures are replaced at their paths.
- Tooltips kept vanilla's look: the game loads `tiles_dialog.dds` (vanilla's) before the
  `tiles_dialog.tga` the Deco UI shipped. Fix: the `.dds` is replaced. Check: the Deco UI's
  `validate_preview.py` flags any `.tga` a vanilla `.dds` of the same name shadows.
- Also (author's requests): the leader's description only in the portrait's tooltip, the law cards
  gone, the sub-ideology shown, the spirits moved up: the advisors & laws list is 156 px taller.

**Valsora started in 1936** (2026-10-14, author: "Valsora takes place in 2036")
- Cause: the clock, the tech tree and every date condition were vanilla's.
- Fix: the start and end dates (`common/defines/valsora_game.lua`), the bookmark, our
  history, every technology's `start_year`, the tech tree's year labels, the date
  conditions of the generic content the mod ships, a game rule's years and the generic
  names with years moved a hundred years (`vanilla_parts.py`; see "2036" in CLAUDE.md).
  The start date's picture is Valsora's, not 1936's soldiers.
- Check: `check_mod.py` fails on an 18xx or 19xx date, research year or tech tree label in
  the built files, and on a start date or bookmark outside 2036 (mutation-tested).
- Not yet seen in game.

**The generic events, AI strategies and on_actions were missing since the first build**
(2026-10-14, found reading vanilla's own files)
- Cause: `replace_path` on `events`, `common/on_actions` and `common/ai_strategy` switched
  off Earth's content, and with it what every country uses: the election, ace, war
  justification, nuclear, capitulation and operative events, the faction and demand
  events (`Generic.txt`), collaboration governments and resistance (`LAR_occupation.txt`),
  the generic AI strategies (default, doctrines, operations, operatives) and the hooks
  that fire them.
- Fix: those files come back as the mod's own, from `source/vanilla/` (copies made by
  `vanilla_sync.py`, the on_actions cut by hand without their Earth parts, Earth-only
  blocks cut from `default.txt`); the events they fire only for Earth's countries
  (Denmark's election, ...) are hidden empty stand-ins.
- Check: `check_mod.py` fails on an event fired but not defined (mutation-tested).
- Not yet seen in game.

**error.log: 1,142 lines of "Invalid decision" and "Invalid Decision ID"** (2026-10-14)
- Cause: `replace_path` is not recursive, so vanilla's decision categories still load, and
  so do the focus trees, ideas and scripted triggers that name its decisions: 732 names.
- Fix: a never-visible decision of the same kind under each name
  (`common/decisions/valsora_vanilla_stand_ins.txt`, generated from
  `source/vanilla/index/decisions.txt`).
- Check: `check_mod.py` fails if one has no stand-in (mutation-tested).

**error.log: 728 lines of "is missing a history file"** (2026-10-14)
- Cause: Earth's 364 country tags stay defined (vanilla's `common/country_tags`), and each
  needs a history file. Removing the tags would break vanilla's files that name them
  (technologies alone, 620 times; the peace conference, the AI, achievements).
- Fix: a stand-in history for each (capital state 1, owning nothing).
- Check: `check_mod.py` fails if one is missing, holds more than the stand-in, or if one of
  our tags is Earth's (mutation-tested).

**error.log: 30 lines of AI faction theaters, and ships in port "too far away from
center"** (2026-10-14)
- Cause: vanilla's `ai_faction_theaters.txt` names Earth's strategic regions; and the game
  placed the unit positions `unitstacks.txt` didn't give, putting ships in port far from
  the centre of two of Merlo's large sea provinces.
- Fix: one AI theater per continent with its coastal seas, in a file of vanilla's name;
  every kind of unit position vanilla's map has is written (see What HOI4 requires).
- Check: `check_mod.py` wants ships in port (19, 20) everywhere but on lakes
  (mutation-tested).

**The world tension globe showed Earth** (2026-10-14, author's screenshot)
- Cause: like the minimap, it is a fixed picture: vanilla's
  `gfx/interface/world_tension_icon_big_strip.dds`, ten frames of Earth catching fire as
  tension rises, and the small `world_tension_icon.dds`.
- Fix: `scripts/globe.py` draws Valsora's at the same sizes from the land: a lit globe seen
  from above Nonscio and Araseos, flames rising frame by frame (`dist/tension_globe_preview.png`).
- Check: `check_mod.py` fails if either file is missing or not vanilla's size (mutation-tested).

**Deco UI: the politics screen was a mess** (2026-10-14, author's screenshot of v0.4.5)
- Cause: it was not the Deco UI's screen. Both mods ship `interface/countrypoliticsview.gui`,
  and the Deco UI loaded first, so Valsora's own copy won, with the Deco UI's scripted text
  (title, ruling party, last election, law names, the leader's description) drawn over it
  where the Deco UI's layout would have had room for it.
- Fix: the Deco UI (v0.4.7) names Valsora as a dependency (`dependencies = { "Valsora (test
  map)" }` in both its descriptors), so the launcher always loads it after Valsora.

**Deco UI: the faction logo sat on the button's icon** (2026-10-14, author's screenshot)
- Cause: the game shows `topbar_faction_empty` (vanilla: a plain plate) in a faction, with the
  faction's logo over it, and `topbar_faction` (vanilla: crossed axes) out of one. The Deco UI
  had drawn them the other way round.
- Fix: swapped (v0.4.7), the logo centred in the button's ring.

**Portrait files and scientists in error.log** (2026-10-14, read with vanilla's own files at last)
- Cause: vanilla's `portraits/00_portraits.txt` and the DLCs' `01_anniversary`, `02_tiger`,
  `03_mtg`, `027_lar` and `998_scientist_portraits.txt` key their lists by Earth continents
  (139 lines: "unknown continent europe", then an unexpected token for each list). And our
  own lists had no scientists: every scientist the game generated logged "Failed to generate
  a portrait … scientist" and kept an empty portrait, which logged `Icon definition ""` and
  `"_small"` on every load (156 + 568 lines in the 2026-10-02 log; the "source unknown"
  noise noted under Superevents).
- Fix: the mod ships a file under each of the six names (`cultures.VANILLA_PORTRAIT_FILES`;
  `00_portraits.txt` keeps vanilla's `default` block of fallback and operative portraits),
  and every continent and country block has vanilla's generic scientist portraits for its
  culture.
- Check: `check_mod.py` fails if one of the six files is missing or a block has no male and
  female scientists (mutation-tested).

**Deco UI: no main menu buttons** (2026-10-14, the Valsora Deco UI v0.4.3 and v0.4.4; author's
screenshot and `error.log`)
- Cause: the UI mod's `.gui` patcher wrote orientations in quotes (`Orientation = "CENTER_DOWN"`).
  On a `containerWindowType` the game rejects that ("Not a valid orientation: CENTER_DOWN") and keeps
  the default `UPPER_LEFT`, so the button row's offset from the bottom centre, (-660, -166), put it
  above the top-left corner of the screen. The same error sent five top bar windows meant for the
  right edge (command power, nukes, army, navy, air) off the left edge. It also wrote
  `alwaystransparent` on twelve containers, which the game rejects there ("Unexpected token").
  v0.4.4 had guessed at `Origo` from the screenshot and changed nothing that mattered; the log named
  the file and line at once.
- Fix: `deco_ui/tools/guipatch.write_gui` (used by every generator) writes orientations bare, as
  vanilla does on containers, and moves a container's `alwaystransparent` into its `background`
  block, where vanilla puts it. Released as v0.4.5 (`dist/valsora_deco_ui.zip`).
- Check: `deco_ui/tools/validate_preview.py` flags quoted orientations, `alwaystransparent` on a
  container and any key no vanilla element of that type uses (read from the game's own `.gui`
  files). On the v0.4.4 files it flags all 31 lines the game's log named.

**Three generated rulers with famous real names** (2026-10-13, seen on the nation sheet)
- Cause: the name lists are vanilla's, and the filter for famous surnames (`cultures.NOT_SURNAMES`)
  didn't have these: Sicilianzo's "Umberto di Savoia" (Italy's last king), Solaria's "Felice
  Garibaldi" and Coraliza's "Eugénio de Castro" (a Portuguese poet).
- Fix: their surnames are in `cultures.DRAW_AGAIN`, so those three draw again (Gaetano
  Mambretti, Fabrizio Sacchi, Bernardo Teixeira) and every other leader keeps their name
  (checked against the previous `dist/countries.csv`).

**The minimap showed Earth** (2026-10-13, author's screenshot)
- Cause: the minimap is not drawn from the map. It is a fixed picture, vanilla's
  `gfx/minimap/minimap.dds` (sprite `GFX_minimap_world`, defined in vanilla's
  `interface/unitview.gfx` and shown by `interface/minimap.gui`), which the mod never
  replaced.
- Fix: `scripts/minimap.py` draws Valsora's at build time from the land: 194×97, the
  map's 2:1 (vanilla's Earth is 268×97, for its 2.75:1 map), pale land on darker
  parchment like vanilla's, in a frame of our own (`gfx/minimap/border.dds`). The window
  is moved right to meet the map-mode buttons (`interface/minimap.gui`, x = -274 instead
  of -343) and the ctrl+m slide that hides it shortened (`MINIMAP_TOGGLE_SHIFT` 202
  instead of 270), as Equestria at War does for its own 2:1 minimap (195×97). Check:
  `check_mod.py` checks the picture's shape and the frame, window and slide that go
  with it (mutation-tested: picture missing, vanilla window position, vanilla slide).
- Not yet seen in game.

**Silvamar hard to tell from Arvorenia and Las Anod** (2026-10-13, author)
- Cause: its map colour was a green (Claude's pick, from its flag's green band), next
  to Arvorenia's dark green and Las Anod's light green.
- Fix: its flag's navy, a little lighter, (10, 30, 140); `pdn_tools.py recolour` kept
  the Countries layer in step.

**Province and state lines missing from row ~1995 down** (2026-10-12, author's screenshots)
- Cause: HOI4 draws at most 65,536 province borders; past that an integer overflows and
  the rest are not drawn (HOI4 wiki, Map modding, "usually hit at about 21000
  provinces"). A border is each stretch of boundary two touching provinces share, land
  or water alike. They are made in province id order, which here is reading order, so
  the lines stopped at the row where the count passed the limit. The map had 24,767
  provinces (~150 px each wherever the author had outlined) and 73,231 borders; the
  count puts the overflow at row ~1990, the screenshots at ~1995. Not the map's size.
- Fix: `merge_provinces.py` merged 4,313 of the smallest land provinces into a neighbour
  in the same state (never across a river, never two city provinces, at most 400 px):
  20,454 provinces and 60,318 borders, land provinces 186 px on average; new outlines
  are cut at ~190 px (`PROVINCE_AREA`). Check: `check_mod.py` counts the borders
  (`borders.py`) and fails over 65,536 (it failed on the old build), with a note within
  4,000 of it.
- The first run took which provinces touch from the build's province map, whose
  X-crossing fixes move single pixels: two provinces touching only at such a corner
  were merged and the build stopped on a province in two pieces. It now reads the
  Provinces layer itself.

**Placeholder islets left beside new countries, and a code two nations share** (2026-10-12, author)
- The author found, by their names in game, states that were still placeholders. Five
  were islets of 17-52 px a few px off land the update had just outlined (the
  Cultists', Cascadia's, Charity's, Volstokn's, Sennheiser's): no line went round them
  and no label named them, so they kept the continent's placeholder colour, and the
  report only gave the placeholder land's total. Fix: `pdn_tools.py attach` to their
  neighbour's nearest state. Check before reporting an update: list each placeholder
  state left and the country beside it (three more such islets remain, by Kyras, the
  Utopian Republic and Kianhua; the author was asked).
- "Tsuruma 6", the island far south of Arpino labelled TS, was read as Tsuruma's on
  2026-10-11, but TS has been Terrabis-Seran's code since 2026-10-05, and it is
  Terrabis-Seran's. A code two nations use, on land far from both, needs asking.
- Moving states renumbers the generic names ("Usnistan 3" became "Usnistan 2"), since
  they count each country's states in map order: refer to states by pixel, not by those
  names, once they may have changed.

**Atlas, second test: squares, no art, no country names** (2026-10-07, screenshot)
- Squares and a stair-stepped coast: the flattened heightmap (land 98, sea 89) put a
  cliff at every coast, and the terrain mesh is coarser than the map's pixels, so the
  coast and the surface snapped to its grid. The coarse field of the
  `GRADIENT_BORDERS_FIELD_COUNTRY_*` overrides may add to it. Fix: Valsora's own
  heightmap, base-game gradient borders.
- No art: the screenshots are at the zoom where HOI4 swaps the 3D terrain for its flat,
  shader-drawn map; textures don't reach it. Only shader files can (needs vanilla
  `gfx/FX` from the author's install).
- No country names: unknown. The font texture decodes correctly with an independent
  decoder; the kerning block (the base game's map font has none) was removed in case
  the game rejects it. Asked whether names showed without the submod, and for error.log.
- Also removed, as unverifiable: the victory-point symbol strip.

**The Atlas submod looked murky and blocky** (2026-10-07, author's screenshot)
- Causes: the political map mode draws an opaque colour over land and sea unless
  `NMapMode.MAP_MODE_TERRAIN_TRANSPARENCY` / `MAP_MODE_NAVAL_TERRAIN_TRANSPARENCY` are 1,
  so none of the paper, waterlines or sea lettering showed (flat grey-blue sea, country
  colours over grey); the 26 px country band is drawn on a coarse grid and stepped; the
  paper tile had chain lines that didn't divide its 256 px and four differently seeded
  copies, so it repeated as a grid of small squares; the town symbols' paper halos
  showed as white blobs when zoomed out.
- Fix: both defines at 1, band 2 / 9 px, one quiet seamless tile, smaller and fainter
  halos. Not yet re-tested in game.

**Rivers looked odd up close** (2026-10-06, author's screenshots)
- Cause: major rivers were drawn at widths 7–9 and minor ones at 4–5, which is far too
  wide beside Valsora's small (~150 px) provinces. Also, Merlovich's and Hoalepa's
  rivers, added later, had never had their provinces re-cut, so only 13–58 % of their
  pixels lay on a province border: the rivers ran through provinces and borders crossed
  them.
- Fix: widths are now major 7–8 (still "large rivers") and minor 3–4. `river_provinces.py`
  re-cut the 30 states whose rivers weren't on borders (now 91 % map-wide) and leaves
  states that are already aligned alone.
- Not fixed: a river running diagonally is a 1-pixel staircase (HOI4 requires
  edge-connected river pixels), which the game draws with slightly wavy banks.

**Every army started with no manpower; opinion modifiers showed their raw keys** (2026-10-04, author)
- Cause: an OOB division takes its men from the country's manpower pool, and the pools
  were tiny: state population was 20 per map pixel (75 million people in the world,
  7,000 in Seigne). `start_manpower_factor` didn't prevent it. The opinion modifiers
  had no localisation, so the game showed `valsora_against_communism`.
- Fix: population is 300 per pixel; each country gets `add_manpower` for its starting
  divisions before `set_oob`; the modifiers are named "Seran Ties" and "Seran Biases".

**Aislada's drawn states were split, and Kurikia's eastern island was missed** (2026-10-04, author)
- Cause: Aislada's regions were cut into one state per city, so regions with two cities
  became two states; the island east of Kurikia has no outline, so nothing seeded it.
- Fix: Aislada's regions are one state each (`regroup_states.py`, `DRAWN_PLACEHOLDERS`);
  the island was given to Kurikia as one state.

**A city name misread** (2026-10-04): "Grande Rebette" is Grande Reliette.

**Drawn states cut into many small ones** (2026-10-04, author: "I want to cut back on the number of states")
- Cause: `apply_outlines.py` cut every drawn area over 1,000 px into ~650 px states,
  even where the author had drawn the states themselves.
- Fix: `regroup_states.py` makes each drawn area one state wherever a country has its
  own state lines; blank countries get ~1,300 px states. 1,346 states became 1,208.

**The Marches had the wrong flag** (2026-10-04)
- Cause: the three-lozenge flag was taken for The Marches; the author's flag file names
  it "Duchy of the Mountains" and The Marches' is the diagonal sword ("Marchers").
- Fix: flags now come from the author's flag file by layer name (`import_flags.py`).

**Country names written on the border layer** (2026-10-04)
- Cause: "Sicilianzo" and "Danelaw" were on Necessary Borders, so their letters closed
  off tiny patches.
- Fix: the letters were moved to Necessary Names.

**Two more islands fused to the land next to them** (2026-10-04, author)
- Cause: in the original drawing these islands touch their neighbours only at a corner
  pixel or through 1-2 px channels, so the strait tracing of 2026-09-28 saw one landmass
  and shrinking closed the channel.
- Fix: `pdn_tools.py channel` cuts the cheapest water-to-water path (fewest land pixels)
  between two sea pixels: the AN island at (654, 1430) and the larger island south of it
  (11 px), and a 2 px bridge at (932, 1492).

**The author's .pdn had lost Locus and the Moelle/Maïeul split** (2026-10-04)
- Cause: the upload was edited from a copy made before 2026-10-02, so its game layers
  (Provinces, States, Countries) were older in the north-east.
- Fix: as the working rules say, the current game layers were kept and only the
  author's own layers (outlines, names, rivers, cities) taken from the upload.

**San Sierra was skipped by apply_outlines** (2026-10-04)
- Cause: `LEAVE` still held a pixel of "the land south of Entroterra and Estande" from
  2026-10-01, which is San Sierra.
- Fix: that entry was removed.

**Rouental's divisions started with next to no manpower** (2026-10-02)
- Cause: an OOB division without `start_manpower_factor` takes its manpower from the
  country's pool, and the Feudal Army (−80 % recruitable population) leaves that tiny.
- Fix: every OOB division sets `start_manpower_factor = 1.0`.

**Lanzerac and Guedelon left the Association (and the Alliance of the Vale) at once** (2026-10-02)
- Cause, most likely: they are the only democratic members of a monarchist-led
  faction, with 20 % monarchist support; vanilla needs 30 % for the leader's ideology
  (`IDEOLOGY_JOIN_FACTION_MIN_LEVEL`). Not yet confirmed in game.
- Fix: they start with 30 % monarchists. The Reibonnaise nations also get +20 opinion
  of each other and an AI alliance strategy.

**The fief overlay sorted fiefs into the wrong kind of vassal** (2026-10-02)
- Cause: the 14 headings of `rouental_fiefs.txt` were read as vassals. They are cultural
  groups: every fief is a vassal of the Crown, and the governorates have no power.
- Fix: the docs and data now call them cultural groups
  (`source/rouental_fiefs_by_state.json`, renamed from `rouental_vassals.json`). The
  fief → state placement stands; levy tiers wait for each fief's title.

**Rempart and Tocsin didn't touch, though the drawing has them touching** (2026-10-02)
- Cause: the author's lines leave a corridor 2–3 px wide from Rempart up to Tocsin. A
  state is the majority of each province, and the corridor's pixels belonged to a
  province lying mostly in the neighbouring state, so the corridor went with it.
- Fix: the 17 corridor pixels were given to Rempart's nearest province on the
  Provinces layer (two 1 px leftovers joined their neighbour). Very narrow drawn
  pieces can lose out this way; a scan found a few other spots worth a look.

**Some new rivers were missing, and some minor rivers came out major** (2026-10-01)
- Causes, in `rivers.py`:
  - A whole river got one size, from the majority of its pixels, so a minor stretch
    drawn onto a mostly major river (the Prestozza branch) became major.
  - Where the main river takes a diagonal step it gets a corner pixel. When that
    corner was exactly where a tributary joined (the Gallyo river), the tributary was
    taken for part of the main river and skipped.
  - A tributary ending next to a 45° stretch of its river can't join it with one
    pixel without making the river two pixels thick (the Ossilia river), so it was
    dropped.
- Fix: each pixel's size follows the layer it was drawn on; branches off a corner
  pixel are followed; a tributary that stops short is joined by the shortest clean
  path of up to 6 pixels. Every drawn line is now traced.

**Royalist Illiricium's redrawn flag** (2026-10-01)
- The author preferred their original; it is back, as sent.

**Royalist Illiricium's flag looked squashed and noisy** (2026-10-01)
- Cause: the flag is about 2:1 with fine gold filigree. The game's flag is 82×52
  (1.58:1), so it was squeezed sideways, and the filigree turned to noise at that size.
- A redraw at 82:52 was tried and rejected by the author (see above).

**Every country showed its leader's name on the map** (2026-09-30)
- Cause: the new leader characters were named `TAG_<subtype>` (e.g. `NSC_despotism`).
  HOI4 looks a country's name up as `TAG_<subtype>` before `TAG` (that is how vanilla
  names Germany under Nazism), so each leader's name became the country's name.
- Fix: leaders are now `TAG_leader_<subtype>`. Check: no character may be named
  `TAG_<ideology or subtype>`.

**Estande's green blended in with Rouental** (2026-09-30)
- Fix: Estande uses the red of its flag instead.

**Unzipping asked about 9 or 10 "files with the same name"** (2026-09-29)
- Cause: Windows ignores upper/lower case, so `ROU_COMMUNISM.tga` (cosmetic-tag flag)
  and `ROU_communism.tga` (ideology flag) were the same file there.
- Fix: cosmetic tags renamed `TAG_GOV_<IDEOLOGY>`. Check: no two files in the mod may
  differ only by case.

**Almost every country had the wrong map colour** (2026-09-29)
- Cause: HOI4 takes map colours from `common/countries/colors.txt`, not the colour in
  each country file; tags missing there get made-up colours. (Theocratic Rouental was
  right because cosmetic-tag colours come from `cosmetic.txt`.)
- Fix: the build writes its own `colors.txt` for every country.

**The fifth ideology overflowed the party list in the politics screen** (2026-09-29)
- Cause: vanilla's box holds four 16 px rows.
- Fix: the mod ships vanilla's `countrypoliticsview.gui` with 13 px rows. Check: the
  rows must fit.

**Superevent text was hard to read** (2026-09-29)
- Cause: the typewriter fonts draw dark text on the dark window.
- Fix: title and quote are coloured white (`§W…§!`).

**Superevent had no music and no background** (2026-09-29)
- Cause (music): `play_song` only finds songs that belong to a music station ("Song
  doesnt exist" in error.log). Fix: a "Valsora Radio" station with the song.
- Cause (background): vanilla's window sprite is see-through. Fix: a generated dark
  background with gold frames.

**"Failed to generate a portrait / name" and "unknown continent europe"** (2026-09-29)
- Cause: vanilla's generic portraits and names are keyed by Earth continents and
  countries, which don't exist on this map.
- Fix: portraits per Valsora continent and name lists per country (`cultures.py`).
  Scientists still have none, so "failed to generate a portrait … scientist" remains.

**Islands fused to their neighbours** (2026-09-28)
- Cause: shrinking the world to game size filled in narrow straits.
- Fix: straits are traced at full resolution and kept open (44 reopened). One more,
  closed into a lake west of Romanoddle, was reopened by hand on 2026-09-30.

**Communist Merlovich never took over after "Fucking Explode"** (2026-09-28)
- Cause: `recruit_character` only works in history files ("should only happen in
  game/history files" in error.log).
- Fix: both Merlovichs are recruited at game start; the focus promotes the communist.

**error.log: "Palette in rivers.bmp is probably not correct"** (first build)
- Cause: the 8-bit BMP header said 256 colours used; vanilla writes 0.
- Fix: `biClrUsed = 0` in every 8-bit BMP.

**error.log: a malformed empty row in buildings.txt** (2026-09-28)
- Cause: a trailing newline at the end of `buildings.txt`.
- Fix: no trailing newline.

## Map problems found while building

**`regroup_states.py --recut` redid states it shouldn't have** (2026-10-18, night, the upload "HOI4_Mod_Map_10-18_1")
- What happened: the new state lines were in Usnistan, Rouental and Terreich, but the script makes every country with
  lines of its own its drawn areas again, map-wide: Ungar's Tópart (31 px, a Gazetteer suggestion) joined
  Megkoronázott, Terreich's states changed far from the author's two new lines (the suggestions of the same morning,
  its isles in pairs), and the Humanist State became 2 states (from 23), because one corner of the desert lines ran
  into it.
- Fix: its result kept only where the new lines are: the whole of the nine desert nations (North Koronista, Levantinin,
  Mustawi, Almohavid, Al-Khabid, Al-Radiyaa, Koronista, Kalaistan, Solaria), and in Rouental and Terreich the states,
  old and new, the changed lines touch (grown until they close on whole states and provinces); everywhere else the map
  as it was. The Humanist State is in `regroup_states.NOT_DRAWN` until the author draws its states.
- Next time: compare the regroup's states with the map's before (`work/` script of the night: country by country) and
  keep it where the lines changed. A `--only` for the script would be the lasting fix.

**Cutting Myehn's necks left scraps of land as broken provinces** (2026-10-18, night)
- Cause: `to_sea` left a scrap under 16 px, cut off from its province alone in the water, with its province's colour:
  three provinces were in two pieces and the build stopped.
- Fix: such scraps become sea too (`to_sea`, by itself).

**The suggestions closed Rouental's and Terreich's map tools on the Gazetteer** (2026-10-18; found by the Gazetteer's
tests, which open Rouental's state panel and Cities tab)
- Cause: the Gazetteer opens a nation's map tools only where its states are drawn lines (`gazetteer.finals`: no two of
  its states in one area the Necessary Borders and Necessary States lines enclose). `apply_suggestions.py` changed the
  game's States layer but drew nothing on Necessary States, so Leclerc's and Kove's halves, and Rosenburg and
  Terreichstadt inside Terreich's areas, shared areas: Rouental and Terreich were no longer "drawn". The mod itself was
  unaffected (the build doesn't use the check), but the site would have closed their tools and the next import dropped
  their map facts.
- Fix: the new states' borders drawn on Necessary States in its own ink (405 px; `Map.draw_lines`, so the script does
  it itself from now on); Rouental, Terreich, North Pollana and Ungar (its six states from the page) count as drawn:
  49 nations.

**More provinces left a state in two strategic regions** (2026-10-18, `pdn_tools.py refine`)
- Cause: the build gives each province the state and the region covering most of its pixels on the layers, and the
  States layer's lines cross some provinces (Ungar's drawn states, at (1029, 843): a 332 px province in three state
  colours). Cut in two, a piece lying mostly in the neighbour's colour became the neighbour's, in another region.
  Painting each piece with its province's region alone wasn't enough; the state was the cause.
- Fix: each cut province's pixels take, on the States and Strategic Regions layers, the state and region the build
  already gave the whole province, so nothing the build reads changes but the provinces. Checked: every one of the
  3,192 states has the owner its land's majority colour gives it.

**The refinement measured the build against the wrong map** (2026-10-18)
- Cause: `refine` aims at a border count the build will reach, and the build adds borders of its own (the corners
  where four provinces met: about 340); it took that overhead as the last build's count less the layer's count, but
  measured the layer after re-cutting the tundra, so the overhead read 513 and only 11 provinces were added for the
  ~200 borders the tundra freed.
- Fix: the layer is counted before the tundra pass (the map the last build was made from); with it 67 provinces
  were added.

**Gazetteer suggestions left provinces of 1 or 2 px, and an islet split a sea province** (2026-10-18,
`apply_suggestions.py`)
- Cause: the new state lines (Rouental's Leclerc and Kove, Ungar's drawn states) cut provinces at the lines' edges into
  scraps; and North Pollana's islet, grown to a province's 16 px, closed a 2 px pocket of the sea province round it
  ("Province colour (44,19,168) is in 2 separate pieces").
- Fix: a second pass gives every scrap under 16 px to the neighbour of its own state it touches most; the islet
  grows only where the sea it takes leaves the sea province one piece. The map was restored from before and the
  suggestions applied again.

**A check of tags broke the next check** (2026-10-18, `check_mod.py`)
- Cause: the new check that cores and claims name defined tags looped with a variable named `kind`, the name of the
  provinces' kinds the next check reads ("IndexError: string index out of range").
- Fix: renamed; check_mod runs clean, and the mutation test covers the new check (an unknown tag in `add_claim_by`).

**The superevent text check never ran** (2026-10-17, found while looking for unused code)
- `superevents_deco.check_texts`, written with the Deco UI's superevent window (v0.6, 2026-10-15) to stop the build
  when a quote, an attribution or a song would not fit its box (a box too short drops lines silently), was never
  called: the manual said the build measured them, but nothing did. Every text fitted anyway.
- Fix: `superevents.localisation` collects the texts the window shows and calls it whenever the Deco UI is on; tested
  with a quote six times too long (stopped: "rou_polite quote: 12 lines of 23 px in a 780x70 box"). The built mod is
  byte for byte the same.

**New state lines cut 1,468 provinces into pieces down to 16 px** (2026-10-17, the author's states for Belekria,
Krionik, Terreich and others)
- Cause: `regroup_states.py` keeps the provinces and splits one only where a line crosses it; the provinces had been
  cut for the old ~1,300 px states, so the new lines left 1,703 provinces under 80 px (307 before) and 1,480 more
  provinces, enough to pass HOI4's 65,536 borders.
- Fix: the provinces of every state the regrouping changed re-cut at ~190 px (`pdn_tools.py recut --keep-states`, one
  seed per enclosed piece): 20,552 land provinces, 368 under 80 px, 61,767 borders. Only the drawn countries: a first
  run also re-cut Fraxhemark, Kampf and Belka whole, since their provinces straddling the border had lost a few pixels
  to the regrouping and their land, without lines, is one piece (undone). A seed's piece can hold another state's
  line pixels, which became provinces of 1-5 px: `pdn_tools.py tidy` merges provinces under 16 px into a neighbour.

**The river re-cut replaced the author's drawn provinces** (2026-10-17, Seigne's)
- Cause: `river_provinces.py` re-cuts every state whose rivers aren't on province borders, and a river crosses Seigne.
- Fix: it leaves alone every state the author's province lines cross; the drawn provinces were applied again.

**Royalist Illiricium's new state line wasn't applied** (2026-10-17)
- Cause: `regroup_states.py` counts a country as drawn only where two of its areas of 150+ px meet across a line; the
  two island states are 128 and 149 px, so the moved line was ignored, and the lower state's pixels above it joined its
  halves round the province line drawn in it.
- Fix: each side of the line given the state most of it is in (by hand; a first try in a box that also held mainland
  states moved 47 px of one into another, undone).

**A Krionik island kept two cut states** (2026-10-17)
- Cause: `regroup_states.py` leaves an island no line touches as it was, two states of the old cut: Krionik wasn't
  "final" for the Gazetteer.
- Fix: the two merged (the island has no line: one area, one state).

**The disk filled up mid-run** (2026-10-17)
- Cause: every decode of the `.pdn` is 1.4 GB (28 layers); four decodes for checking, plus the regrouping's own, left
  nothing, and a script died while decoding (it saved nothing).
- Fix: check decodes deleted as soon as they're read; the scripts' own folders (`work/pdn_*`) are made again when they
  run.

**Puppets of Authoritarian overlords were not allowed** (2026-10-17, found while making Kampf Fascist)
- Cause: with Death or Dishonor the game's puppet level refuses a fascist overlord (Germany's subjects are
  Reichskommissariats); Illiricium (Bleacherism, Authoritarian) had started with three puppets since 2026-10-01, and
  Kampf's Hohenzburg would have joined them.
- Fix: the mod ships the puppet level without that clause (`vanilla_parts.EDITS`).

**The ivory war goal lists showed a cross of seams** (2026-10-17, the Deco UI v0.10's diplomacy preview)
- Cause: the parchment tile they replace (`tiled_paper_w_frame_one_border`) is a cornered tile: the game repeats its
  middle and stretches its edges, so the first ivory sheet's gradients broke at every 64 px border.
- Fix: a flat ivory fill with the rim along the edges only. A cornered tile's middle must be flat (or repeat cleanly), as
  `gen_textures.py` says where it draws this one.

**`validate_preview.py` stopped on the settings' tab arrows, then called the loading screens stale** (2026-10-17, v0.10)
- Cause: its size check read every `gfx/interface/button_*.dds` as `button_<w>x<h>`, and `button_left.dds` has no size
  in its name; and its stale check knew only `gen_textures.py`'s textures, not those `make_loading.py` draws by hand.
- Fix: names without a size are skipped by the size check; the eight loading pictures are listed in the stale check
  (named there: importing `make_loading.py` would put the Valsora scripts, with their own `layout.py`, first on the
  path).

**A circular import between two art modules** (2026-10-17, v0.10)
- Cause: `window_art.py` took `popup_art.py`'s footer plate while `popup_art.py` imports `window_art.py`'s helpers.
- Fix: `window_art.py` imports it inside the one function that draws the plate.

**Enter in the password box skipped the Gazetteer guide's first step** (2026-10-16, `tests/gazetteer/guide.py`, the
night's quick-start guide)
- Cause: the guide opens as the nation unlocks, and it gave its Next button the focus; the Enter that unlocked the
  nation (a key down in the password box) went on to press the focused button, so a player who unlocked with Enter
  started on step 2. The test showed it as a guide that skipped a step on every Next after Back.
- Fix: on opening, the card itself takes the focus (Next takes it when the steps change); the test checks it.

**The Vale's loading screen framed half the world** (2026-10-16, `deco_ui/tools/proposals_loading.py`)
- Cause: the box round the Reibonnaise states took every pixel they own, and Rouental also owns islands off Solitas,
  far away.
- Fix: only their land within 320 px of Rêverie. Guedelon has 48 pixels of land on today's map, so it is a dot with
  its name beside it.

**The designers' preview showed the game's sub-windows, not the new pictures** (2026-10-16, Deco UI v0.9)
- Cause: none in the mod: the designers' popup pictures are their windows' backgrounds, and the game's panels on them
  (the module list, the statistics sheet) are drawn over them with their own tiles, so only the parts between show.
  The new pictures' panels are measured from the game's own pictures, so they lie under those sub-windows.
- Fix: none needed; checked against the game's look side by side (`preview_designers.py`).

**A test pressed a portrait instead of the Send button** (2026-10-15, `tests/gazetteer/traits.py` after the game's
characters came to the People tab)
- Cause: a portrait box for a base-game portrait first read "Base-game portrait: send one", and the test finds the
  request form's button by the text "Send"; the portrait box came first and was pressed.
- Fix: the box reads "Base-game portrait: add your own", so the request's button is the only control in the card
  that says "Send".

**The changes to the author's characters first landed out of order** (2026-10-15, the first build of the test's file)
- Cause: `gazetteer.patch_characters` looked for a leader's traits before its titles, and wrote titles after the
  traits; `check_mod.py` and `country_list.py` read a leader's `ideology` first and `desc` right after it. A changed
  stat could also be one the role doesn't have (an admiral's coordination on Serelle, a general).
- Fix: titles go right after the ideology, traits after them; a commander takes only its role's stats (the page sends
  only those, and the import keeps only those). The build was checked against an unchanged one: characters nobody
  changed stay byte for byte.

**Painting the last state off a game releasable broke the Releasables tool** (2026-10-15, writing the in-game test)
- Cause: the message for it called `toast`, which the page doesn't have (it has `flash`): an error, and the stroke
  stopped.
- Fix: `flash("A releasable needs a state: give it another first")`; the test paints such a state.

**Every stat of a commander showed the "changed" mark when one was set** (2026-10-15, the test's screenshots)
- Cause: the mark is drawn after the label of a field set by hand (`.field.set label::after`); the skill and stats are
  labels inside one field, so all five got it.
- Fix: only the field's own label (`.field.set > label::after`).

**The first release couldn't be published from the session** (2026-10-15, the author: "Yes, please switch to using
releases")
- Cause: GitHub's proxy for this kind of session refuses releases: "Creating, editing, or deleting releases is not
  permitted for this session type" (HTTP 403, on creating a draft; nothing was made). It is the session type's rule,
  not the author's GitHub access.
- Fix: none from a session, and no way round it. The author keeps the zip in `dist/` for now and will publish releases
  by hand for more substantial builds.

**The Gazetteer's company kinds lacked the helicopter maker, and the check its list of templates** (2026-10-15)
- Cause: `vanilla_sync.py` read the game's English names with a pattern wanting one leading space; the helicopter
  organisation's line has none in the game's file, so it read as unnamed and was left out. And `companies.json` was
  first written before the list of every generic organisation (`templates`) was added to it, so `check_mod.py` stopped
  on the first build with a company (a missing key), not on a real fault.
- Fix: the pattern takes any leading space (the other lists came out the same); `vanilla_sync.py` was run again, and
  the test build with companies passed. The train organisation has no English name in the game at all and stays out.

**The Gazetteer's company rows ran past the panel's right edge** (2026-10-15, the companies test's screenshots, desktop
and phone)
- Cause: a row's fields sit in a one-column grid whose column was sized by its widest content; a list of the kinds of
  company is as wide as its longest name, so the column, and every field and line of text under it, grew wider than
  the panel and were cut off.
- Fix: the column can't grow past the panel (`minmax(0, 1fr)`), and the kind list shares its line with Delete and
  shrinks. The test now also photographs the political advisors' section.

**Two of the Gazetteer page's new functions had the names of existing ones** (2026-10-15, adding companies)
- Cause: the request form for traits and kinds of company was first written as `askFor` and `requestForm`, which the
  page already had (the Nation tab's requests); in one script, the later definition silently replaces the earlier.
- Fix: one function, `askAuthor`, for both; the page was searched for any name defined twice (none left).

**The Gazetteer's arms companies named the DLC in their conditions, as the game's don't** (2026-10-15)
- Cause: the first version wrote `has_dlc = "Arms Against Tyranny"` into each organisation's `allowed`; the game's
  national organisations (Germany's Porsche, Henschel ...) give only their tags, the organisations themselves being
  the DLC's.
- Fix: `allowed = { original_tag = TAG }`, as theirs.

**`check_mod.py` didn't check the scripted effects our on_actions call** (2026-10-15, found by the new
`scripts/mutation_test.py`)
- Cause: the check of "a scripted effect used but not defined" read focus trees, scripted effects, events and
  decisions, but not our on_actions, where `valsora_reibonnaise_opinions` is called on every start and change of
  government. Renamed or misspelt, it would only have shown in game (error.log), and the Reibonnaise opinions with it.
- Fix: our on_actions (not vanilla's shipped ones) count among the users of scripted effects. The mutation test's
  45th break is that rename; all 45 are caught.

**The larger flags' script failed in the Deco UI's tools** (2026-10-15, `scripts/build_flags15.sh`'s first run)
- Cause: it gave `VALSORA_DECO_ROOT` as a relative path (`work/deco_flags15`); `deco_ui.py` runs the Deco UI's tools
  from their own folder, where that path leads nowhere (`long_names.py`: no `.fnt` file).
- Fix: the script gives the folder's absolute path. The test version then built and passed `check_mod.py`.

**A test of the Gazetteer showed the page garbled** (2026-10-15, the traits test; the page was fine)
- Cause: the test served `scripts/gazetteer.html` as it is; claude.ai wraps a page in a skeleton with
  `<meta charset=utf8>` and a doctype first. Without them the browser read the page as Latin-1, in quirks mode
  ("Â·", "â€¦"), and the layout broke.
- Fix: the tests (`tests/gazetteer/harness.py`) serve the page in claude.ai's skeleton, as the earlier tests did.
  Also learned there: Playwright's `select_option` leaves the focus where it was, and the page doesn't redraw a pane
  while someone types in it, so a test must focus a list before choosing (`harness.pick`), as a click does.

**`check_mod.py`: Seigne "had no leader" once the Gazetteer's admiral was built** (2026-10-15)
- Cause: the check read each character's ruling sub-ideology with one regular expression from a character's name to
  the next `country_leader = { ideology = ...`. The admiral has no country_leader role, so the expression ran on into
  the next character (Seigne's ruler) and took its ideology, and Seigne's own ruler was skipped.
- Fix: the check takes the characters' file block by block (brace-matched) and reads each one's own role. A country
  without a leader is still caught (tried).

**`check_mod.py` didn't look at decisions** (2026-10-15, adding Rouental's test decisions)
- Cause: the checks of events fired and scripted effects used read focus trees, scripted effects, events and
  on_actions, not decisions; nothing checked that an event's title, description and options, or a decision's name, had
  localisation (the game shows a missing key as itself); and a decision's short icon name (`generic_x`) wasn't checked.
  A decision firing a misspelt event or effect, or a missing text, would only have shown in game.
- Fix: decisions count among the users of events and effects; our events' texts (hidden ones excepted) and our
  decisions and categories (never-visible ones excepted) must be localised; short icon names must be sprites. Nine
  breaks tried, all caught.

**Deco UI news: the masthead still looked lopsided** (2026-10-15, the author on v0.8's preview)
- Cause: WORLD is wider than NEWS, so with the globe in the middle and equal gaps the name leaned left (32 px from
  the rules' start, 70 from their end). The game's own news page was off-centre as well: its picture sits 5.5 px and
  its headline 7 px left of the page's middle, its story's box 5 px right of it. And the globe, lit and with every lake and channel, read as a speckled
  blob at 50 px.
- Fix (v0.8.1): the paper's name is VALSORAN STANDARD, two words Federo sets to the same width (the author's
  suggestion), each placed by its ink the same distance from the globe (15 px from each word to its rules' end, both
  sides); the picture, headline and story centred on the page; the globe simplified to what 60 px can show, in flat
  gilt with a graticule.

**The mod's build took four minutes** (2026-10-15, looking for speed at the author's request)
- Cause: `np.load` gives a lazy `NpzFile` that decompresses an array again on every access, and the unit positions
  asked `work/regions.npz` for the province centres 82,565 times: 200 s of the 238. Three full-map distance
  transforms were spare too: one computed and thrown away (the land side, in normal mode), one computed twice (the
  water's distance from land), and one only asked whether a province edge was within 2 or 3 px.
- Fix: `reg = dict(np.load(...))` (read once), the water's distance reused, the edge test by erosion (the 3x3 and
  5x5 blocks). 26 s; the build's files are the same, byte for byte.

**Every build made a new zip for git, changed or not** (2026-10-15)
- Cause: a zip stores each file's modification time, and the build rewrites every file.
- Fix: `package.py` gives every entry one fixed date (1980-01-01) and the same permissions; the same mod now gives
  the same bytes.

**Deco UI: a texture build stirred every texture** (2026-10-15)
- Cause: `gen_textures.py` redrew all 240 textures on every run, and a redraw differs from the last by a few
  anti-aliased pixels, so every texture changed in git; they were put back by hand.
- Fix: a signature per texture (its HTML, size, fonts and embedded files) in the manifest, so only textures whose
  drawing changed are redrawn (`--all` redraws all); `tools/restore_noise.py` puts back textures a redraw changed
  only by such noise.

**Deco UI previews: over a hundred text warnings once the game's fonts were redrawn** (2026-10-15)
- Cause: the side panels' preview measured button texts as their raw keys ("ARMY_SORT_GROUP"), didn't fill
  `$VARIABLES$` or break lines at `\n`, checked its "game's look" render (now drawn in our fonts), and flagged boxes
  the game's own text overflows too (the logistics panel's "Military Factories": an 80 px box, 107 px in the game's
  font, 95 px in ours).
- Fix: texts looked up in the game's localisation, variables filled, line breaks kept; the game's look drawn with an
  approximation and unchecked; a game font's text flagged only when it is wider than the box and than the game's own
  (by 5 %), or needs more lines (`validate_preview.GAME_W`). No regressions were left: every warning was one of these.

**Deco UI events: the options sat much closer to the picture than to the card's edge** (2026-10-15, the author's note
on the preview)
- Cause: the game's options grid starts just right of the picture (its 300 px entries left-aligned in the room
  beside it), and the mod's plate overhung the entry to the right as the game's picture does.
- Fix (v0.8): the plate and the entries 334 px wide, each window's options grid moved so the plates sit in the
  middle of the room beside the picture (`deco_ui/tools/layout_events.py`: 12 px either side in a country event).

**Deco UI army bar: the play / stop row not centred over the general** (2026-10-15, the author's note on the preview)
- Cause: the game's `leadergroups.gui` puts the row (and the buttons on it) 4 px right of the portrait's opening.
- Fix (v0.8): `layout_armybar.MOVES` moves the row and what sits on it 4 px left, and the army group's extra buttons
  with it, so frame, plaque, count and row share one centre line.

**Deco UI news: the WORLD NEWS masthead looked lopsided** (2026-10-15, the author's note on the preview)
- Cause: the ball sat off the page's centre, with WORLD and NEWS at different distances from it.
- Fix (v0.8): a gilt globe of Valsora (`deco_ui/tools/globe_art.py`, from the built map) on the centre line, WORLD and
  NEWS a little smaller, at the same gap either side.

**Deco UI previews: centred text looked badly spaced ("Postpon e th e count.")** (2026-10-15, the event preview)
- Cause: the previews' text renderer (`deco_ui/tools/validate_preview.draw_text`), not the fonts: it rounded each
  glyph's position on its own, and centred text starts half a pixel in when its box has an odd number of pixels to
  spare. Python's `round()` takes .5 to the even number, so every other letter moved a pixel (vertically too, when a
  line was centred in its box). Set with the font's own advances, the same letters are even. Every preview with
  centred text had it since v0.3; the mod's files were never affected.
- Fix: each line starts on a whole pixel, as the game draws text, and the glyphs follow by the font's whole-pixel
  advances.

**Deco UI army bar preview: the plate cut off above the marshal; the plus and the counts off centre** (2026-10-15,
the author's notes on the first preview)
- Cause: the plate was the preview's fault: it drew the army group's piece behind both the marshal and his first
  army, so the plate stopped short over him. The game lays one plate under the whole run: the army group's piece
  starts it, each army's (80 px) carries it on, the last army's ends it. The other two were real: the game draws
  the empty card's picture 1.5 px left of the frame's opening, and its count box sat 3 px above the plaque. The
  army group's piece was also 174 px wide, the game's 175 (two frames of 87.5 px).
- Fix (Deco UI v0.7): the preview lays the pieces as the game does; the bust and plus are drawn on the opening's
  centre (`layout_armybar.hole_centre`); `make_leadergroups.py` gives both count boxes the plaque's box, centred
  both ways; the army group's piece is 175 px (`validate_preview.SAME_SIZE` holds all the army bar's textures to
  the game's sizes).

**Deco UI: the top bar's date box was too narrow for 20xx dates** (2026-10-15, `validate_preview.py`)
- Cause: the box (220 px) was sized for 1936-1949; "2" is wider than "1" in the date font, and the widest date
  the game shows from 2036 to 2049, "00:00, 30 September, 2040", is 230 px. The game cuts a longer text short.
  The preview's long sample was still "23:00, 29 September, 1939".
- Fix: the box is 230 px (x 55), the speed chevrons 6 px further right; the long sample is now that widest
  date, so the check covers the worst case.

**`collages.py` listed Earth's 364 tags as nations still without a flag** (2026-10-15)
- Cause: since 2026-10-14 the build ships a stand-in history for each of Earth's tags, and the collages took
  every history file for a country of ours; with `--continent`, their capital (state 1) put them all on one
  continent.
- Fix: Earth's tags (`source/vanilla/index/tags.txt`) are left out, as `country_list.py` does; flags of
  countries in `COUNTRIES` owning nothing are labelled "(off the map)".

**check_mod: 132 errors, sprites of the Deco UI's `nationalfocusview.gfx` "point at missing" textures** (2026-10-15, build)
- Cause: to give the focus in progress its own picture, the Deco UI ships the game's `nationalfocusview.gfx` with
  `GFX_focus_current` changed; its other sprites still name the game's textures (`tiled_focus_bg.dds`,
  `focuslink.dds` ...), which the game has and the mod doesn't ship. The check wanted every texture in the mod.
- Fix: a game sprite (`source/vanilla/index/sprites.txt`) may name a texture the mod doesn't ship, unless the
  texture is in a folder of ours (`valsora…`, `VAL/`): removing the Deco UI's `current_bg.dds` is still an error
  (mutation-tested).

**The Gazetteer's map tools, releasables and admins, found while testing them** (2026-10-15, later)
- Facts entered on a nation whose states the build had cut would land in the wrong places once
  the author drew its states (state facts on whichever new state holds their pixel, one replacing
  another; terrain on re-cut provinces). Fix (author's idea): a nation's map tools open only once
  its states are the author's (`gazetteer.finals`), and the import drops a closed nation's map
  facts.
- Seven tabs didn't fit the 390 px column on a desktop (483 px wide): State and Nation scrolled
  out of sight. Fix: the column is 420 px and the tab labels tighter.
- Run from `scripts/`, the import couldn't find the last build (so it couldn't tell whose states
  were drawn) nor the base game's tags, and named a releasable LIB, Liberia's tag. Fix: it
  refuses to run outside the repository's root.
- The build looked tags up before it had added the Gazetteer's releasables (KeyError). Fix: they
  join `COUNTRIES` and the lookup together.
- A releasable without a ruling sub-ideology had no leader, and `check_mod.py` failed. Fix: it
  takes its nation's.
- Any refused save locked a player out with "This nation's password has changed", so under
  rules a step behind the page (before the author pastes new ones) a player saving a releasable
  would have been told so. Fix: the page first checks the nation's key; while it is there, the
  save is only "Not saved" (tested with the first rules in the emulator).
- The tests' sign-in waited for the Sign in button, which a nation's page hides. Fix (tests
  only): they wait for the Firebase SDK instead.
- The emulator can't reload its rules in this sandbox (the CLI's reload request is blocked and
  it stops, leaving the Firestore process running); and `pgrep -f`/`pkill -f` on a pattern in
  the shell's own command line stop that shell. Fix: restart the emulators with the rules file
  in place, and stop leftovers by their process id.

**The Gazetteer moved to a web site of its own** (2026-10-15)
- On claude.ai only friends invited by email as Editors could save; visitors through a public
  link can only view, and the author didn't want to ask everyone for an email. Fix: the same
  page as a web site (GitHub Pages, the `gh-pages` branch) with its atlas in the author's
  Firebase project; players need only their nation's password.
- Firestore keeps no array directly inside another, and rivers, railways and suggestions are
  lists of points. Fix: the page's store stores each point as `{"_a": [x, y]}` and reads it
  back as a list.
- Firebase's Cloud Storage now needs the paid plan. Fix: pictures (at most 640 px) are
  documents beside the facts, which the rules cap at 800,000 characters; a saved file carries
  them as `images` (`gazetteer.py import` reads them).
- Marking a nation finished wrote `true` over the player's name among its editors. Fix: both
  writes go through one function.
- Firebase's error codes have hyphens (`permission-denied`), claude.ai's underscores. Fix: the
  store turns them into claude.ai's, so the rest of the page is the same on both.
- Google's sign-in window can't load in Claude's sandbox (apis.google.com is blocked). Fix for
  the tests: a build for the local emulators (only) signs in with the emulator's unsigned
  tokens.
- `pkill -f "firebase emulators:start"` killed the shell running it, whose command line held
  the same words. Fix: stop background tasks by their task id.

**The Gazetteer's version 2, found while testing it** (2026-10-14, latest)
- The boxes for a nation's other pieces of land were rebuilt on every redraw (any saved fact),
  so a tap could land on a box that had just been replaced and do nothing (the phone test).
  Fix: built once per nation and screen size; a redraw only repaints their pictures.
- On a phone the boxes stacked over a third of the map. Fix: one row of small chips along
  the bottom.
- The lock box showed "null" under its Unlock button: `replaceChildren` writes a null child
  as text. Fixed, and the lock box stays hidden for the owner until their passwords load
  (it said "no password yet" for a moment).
- A locked nation's chip said "Saved". Fix: "Locked" from the moment it opens.
- A link to a nation not on the map yet (`#QZX`) opened nothing: that list arrives after the
  page starts. Fix: opened when it arrives; a link changed in the same tab opens too.
- Uploaded pictures were shown from the URL the upload returned, which the platform says not
  to keep (other viewers can't use it). Fix: only the asset id is stored, shown as
  `/_blob/<id>`.
- Owner tools' messages vanished when a snapshot redrew the section. Fix: kept in the page's
  state.
- With the Suggest tool the desktop toolbar wrapped Undo onto a second line at 1440 px. Fix:
  "Hubs" for "Supply hubs", the colour switch and Undo wrap together, and under 1360 px only
  the chosen tool shows its label.

**The Gazetteer, found while testing it** (2026-10-14)
- The ledger rebuilt itself after every saved field, so a field still being typed in could
  lose its text, and a field losing focus during the rebuild threw "The node to be removed
  is no longer a child of this node". Fix: panes re-render on the next frame, never inside
  an event handler, and a pane being typed in waits until focus leaves it.
- `check_mod.py` didn't know vanilla's `large_island` state category, which the Gazetteer
  offers. Fix: the categories and their building slots are vanilla's full list (1.19.3
  `common/state_category`). Check: factories and dockyards over a state's slots, building
  levels over vanilla's caps, unknown resources, railways between provinces that don't
  touch (mutation-tested).
- Text fields ran past the ledger's edge: the page's reset sizes boxes without their padding
  (`box-sizing: content-box`). Fixed with `border-box`.

**An upload based on an older map** (2026-10-13)
- The author's file was the map as it stood after the Usnistan update (commit 4a191cb),
  before the ten placeholder states changed hands and before 4,313 provinces were merged
  for the border limit; the author noticed the island below Cascadia in the old colour.
- Fix: their file was compared layer by layer with that version: only Necessary Borders,
  Names and Cities, Even More Reference and the new Islands to Add layer differed, and
  only those were taken onto the current map (whose game layers already had the
  island as Cascadia's).

**A line short of the coast, and a label on the borders layer** (2026-10-13)
- Texaria's eastern border stopped 8 px short of the inlet south of it, so Texaria and
  Gran Yucanoa were one patch; a "CI" was written on Necessary Borders west of Surredia,
  where its strokes would have cut the patch into scraps.
- Found by matching every label to the patch under it (two names on one patch) and by
  looking for letter-sized bits among the new line pixels. Fix: the line was continued
  to the inlet along its own row, and the letters moved to Necessary Names.

**The terrain test unrealistic in places** (2026-10-12, author: "make the generated
terrain logical, realistic, and consistent")
- Causes: Rouental's mountains were four invented round domes, while the author's fief
  map has the Vale of Reibonne's own ranges; rivers ran over the generated relief with
  no valleys; woods were blobs of noise, unrelated to the land; the north of Usnistan
  (the Levant's latitudes) was desert, as the westerlies' winter rain stopped at 38°;
  half of the Siberian taiga was tundra or dry grassland (a treeline at -6 °C, and a
  steppe threshold meant for warm climates); the Sahel met the jungle along a ruler-
  straight edge; Aislada's monsoons wet the whole island, so it had no outback; bogs and
  coastal fens were scattered blobs and thin strips along the coasts.
- Fix: the vale is built from the author's ranges (`source/vale_ranges.png`), with a low
  floor, hills along the rest of its land border and the Reliette gap open; every river
  has a valley whose bed never rises downstream, and the land where rivers are drawn is
  wetter; woods follow the relief (uplands, slopes, land above its surroundings) and
  farmland the lowlands, valleys and coasts; the westerlies reach 27°; the treeline is at
  -9 °C and trees need little rain in the cold; rainforest, dry forest and savanna grade
  into each other; Aislada's monsoons reach 20° and 110-200 px inland; bogs lie in
  basins, and coastal fens only along long, low coasts.

**Straight-edged strips in the terrain test** (2026-10-12)
- Cause: the moist air is carried inland one line of pixels at a time, so a lake
  (which refilled the air with moisture) or the end of a range on one line but not
  the next drew a straight-edged wet or dry strip; round hand-placed dry areas, forced
  marshes and straight ranges looked drawn with a ruler and compass.
- Fix: only the open sea refills the air, each sweep is blurred across the wind, and
  ranges, wet and dry areas and marshes get ragged, noise-warped edges.

**Letters on the Borders layer, moved one stroke short** (2026-10-12)
- The author's CU and RA labels (the Cultists', Kyras': 11 of them) were drawn on
  Necessary Borders, where they would have cut islets and coast into scraps. They were
  moved to Necessary Names a 14 x 8 box at a time, but "CU" is 15 px wide, so each U's
  last stroke (7 px) stayed on Borders and closed off a 2 px sliver of the Cultists'
  coast.
- Found by the dry run of the patch selection: the biggest patch with no seed (its
  "outside patch") was those 2 px. Fix: the two strokes moved too; the dry run then had
  no patch without a seed.

**Two codes drawn touching, and a label in the sea** (2026-10-12)
- Six labels were two codes drawn so close they touch ("CH CH", "US US", "FE FE", "RY
  RY"), each pointing at its own islet; read as one word, each named only one islet.
  Fix: such words are split letter by letter into codes: five more islets.
- "Port Almohavid" is written in the sea, and the land nearest it is Almohavid's, so it
  named Almohavid's whole patch. Port Almohavid is the 16 px tip of land a short line
  closes off at (3551, 1640).

**An islet left out of its country's states** (2026-10-12)
- The islet the author circled near Myehn (40 px) became a state of its own:
  `apply_outlines.py` joins a small islet to the nearest state of its country made in
  the same run, and Myehn's states are from 2026-10-11.
- Fix: `pdn_tools.py attach myehn 4752,1538`, as for Araseos 1.
- Also: Sennheiser's land was in `LEAVE` (2553, 933) since 2026-10-07; the check of
  `LEAVE` pixels against the seeded patches caught it, and it was removed.

**The sea didn't meet across the wrap** (2026-10-12, Merlo's update)
- Cause: Merlo drew the sea borders near the left and right edges separately. Of about
  13 borders reaching each edge, 5 met their partner exactly, 4 within 8 px, 3 were
  16-43 px apart, and 2 on the right edge had none; short line bits ran along the edge
  columns themselves, so one big province touched the right edge only through 18 rows
  of line pixels; and the provinces facing each other across the wrap were in different
  sea regions on 71 % of the rows (and the oceans' borders met the edges at different
  rows).
- Fix: `sea_provinces.py seam`: borders meet the two edges at the same rows (halfway
  between, or continued across the wrap), the sliver is pulled back, the lines near the
  edges are redrawn from the result, and the provinces facing each other share a region.
  A first try cut the sliver's province 28 px deep with straight lines; its neck is 5 px
  deep, which is all that goes now.
- Also: Merlo's two scripts point at folders on his machine, so `sea_provinces.py` does
  their job here. Two of his provinces are 312-313 px tall, over his own cutting margin
  (311) but under HOI4's limit (320): areas are cut only within 3 px of the limit.

**Two leaders named after words in a comment** (2026-10-11)
- Cause: vanilla's German and Russian name lists have comment lines inside them ("# From
  VGE"), and `cultures.py` read every word between the braces as a name, so Daravon's
  leader was "VGE Eisele" and Kurikia's "Nikita Russian". The game itself skips
  comments, so its own generated generals were fine.
- Fix: a drawn name that is a comment word is drawn again. The words stay in the lists
  as read, so no other leader's name changed: Daravon's is now Arthur Ziegler, Kurikia's
  Nikolay Giligashvili.

**Vanilla's Chinese, Vietnamese and Tibetan name lists; famous names in others** (2026-10-11)
- Cause: vanilla's Chinese list (CHI, and its copies for the warlords) has family names
  in both its given-name and surname lists, so every generated Chinese name is two
  family names ("Wang Zhao"); its Vietnamese one has a middle name (Văn) among its given
  names, so Plaija's leader came out "Văn Nu"; its Tibetan list is eleven names, with two
  titles (Dzasa, Rinpoche) among the surnames; its Buryat one has a name in curly quotes,
  which Gorduchai's leader showed ("“Dashi-dorzho” Barannikov"). Some lists hold famous
  people's names: the Indian one
  Gandhi, Modi and "Neru" (beside "Mohandas"), the Burmese one "Suukyi", the Armenian
  one Nzhdeh and Kajaznuni (beside Garegin and Hovhannes).
- Fix: our own Chinese (`CHN`), Vietnamese (`VNM`) and Tibetan (`TBT`) lists in
  `custom_names.txt`. The Chinese and Vietnamese ones have the family names where the
  game takes the first name, so names read family name first, as they do in those
  languages ("Wang Zhiyuan", "Trần Văn Hùng"). The Buryat name has straight quotes in
  `vanilla_names.txt`. The famous names are in `cultures.NOT_SURNAMES`, so no leader of
  ours carries them.

**Faction members with 20 % for their leader's ideology** (2026-10-11, a precaution)
- Cause: every country starts with 20 % for each ideology, and a faction member likely
  needs 30 % for its leader's (see Lanzerac and Guedelon, 2026-10-02); not seen in game.
- Fix: the Great Lake Republics' four members and the Synthesist Internationale's two
  start with 40 % for their own ideology, their leader's, and 15 % for each other
  (`nations.POPULARITIES`).

**The upload predated a change** (2026-10-11)
- Cause: the author's file was from before Araseos 1 went to Terreich, so its game
  layers still had the islet as Araseos (the only difference in them).
- Fix: `apply_outlines.py` ran on the upload, then `pdn_tools.py attach terreich
  935,1862` again.

**Estande's capital was on an island overseas** (2026-10-10)
- Cause: a country's capital is the sizeable state nearest the centre of all its land.
  Estande's islands east of Terreich (Araseos) and the six added on 2026-10-09 off
  Orientalis drew that centre out to sea, and the nearest state was one of its islands
  east of Terreich ("Estande 70"), far from its homeland. Found while making the flag
  sheet of Araseos, where Estande appeared.
- Fix: a capital on a continent holding under a third of the country's land is chosen
  again on the continent holding most of it. Estande's is now "Estande 30", in the
  middle of its homeland; no other capital moved (a plain "main continent only" rule
  would also have moved Anglost's, Krionik's, Peatiktist's and Terrabis-Seran's).

**A flag update was missed** (2026-10-09)
- Cause: `import_flags.py` called a flag unchanged when its mean difference from the
  stored one was under 3, a test meant for resampled copies of the same picture.
  Serie's four new corner anchors cover 4 % of the flag (a mean difference of 2.65), so
  they were skipped (the author noticed). The same test had kept Claude's redraw of
  Krionik's flag once the author's own file had it.
- Fix: at the same size any visible pixel counts; at another size both are compared at
  164×104, and more than 0.5 % of pixels off by over 40 counts. Re-imported: Serie,
  Krionik, and the file's 82:52 copies of Garfield, Troc and Terrabis-Seran (the same
  pictures; the stored ones were 490×327). Rouental's 1180×700 original is kept. The
  older flag files were checked too: nothing else was missed.
- Also found: see-through pixels, which the game shows as holes in a flag (Harwick's
  top row and Royalist Illiricium's gaps were filled by hand before). Belka's emblem had
  a soft see-through edge, Riverraine's and Belekria's flags a 1-px see-through frame,
  Garfield's one faint row. `import_flags.py` now lays every see-through pixel over the
  nearest solid one before comparing and saving (`opaque`), so a re-import can't bring
  a hole back; Ponchomagnifico's faint top row (from the friend's build) was filled the
  same way. No flag in the build has see-through pixels now.

**Provinces outside a new outline were changed** (2026-10-09)
- Cause: `apply_outlines.py` tidies the provinces in a box reaching 64 px past the
  outlined area. Old provinces the box's edge clipped looked split there, and their
  pieces under 300 px were merged into neighbours: 77 px of 11 provinces in Belekria,
  Sminishia and Krionik that no outline touched, some into another state. Earlier runs
  likely did the same along their boxes' edges.
- Fix: only provinces the outlines made or cut are tidied; the run was redone, and the
  map file now differs from the upload only inside the new nations.

**Half a state cut off by a new line became part of another state** (2026-10-09)
- Cause: West Sminishia's new line cut one of Sminishia's states nearly in two.
  `pdn_tools.py cede` joined every part a split state loses to a neighbouring state that
  moved whole, which suits slivers, so West Sminishia came out as one state of 2,484 px,
  twice a usual state.
- Fix: a lost part of 600 px or more (`CEDED_STATE`) is now a state of its own; West
  Sminishia has two states.

**Vanilla's Mongolian and Belarusian name lists** (2026-10-09)
- Cause: vanilla's MON list is 14 Chinese and Manchu names, and its BLR list is part of
  the Russian one (`country_list.py` even called a Russian-named country Belarusian,
  since it matched cultures on the first dozen male names).
- Fix: Sanada uses the Buryat list (BYA, a Mongolic people) and Belka the Russian one;
  `country_list.py` matches on every male name.

**A moved border between countries without state lines** (2026-10-09)
- Cause: the author's new line between Hwitland (now Scealand) and Eschland (now Artzen)
  fitted no tool. `pdn_tools.py border` gives away a whole line-enclosed area, but
  Eschland's coast has no line, so that area ran on into the sea around Daravon's
  island; `regroup_states.py` only redraws countries with state lines of their own; and
  two of Eschland's states and three provinces straddled the line, so repainting the
  land alone would not have moved the border (each state goes whole to the country
  covering most of it).
- Fix: `pdn_tools.py cede FROM TO X,Y`. Only FROM's pixels are cut by the lines, the
  provinces are split along the line, and the part a split state loses joins a
  neighbouring state that moved whole. One sliver touched only another sliver, so they
  merge in turn (the first try stopped there, before saving).
- Also: the upload was the author's previous file plus their edits, so its game layers
  predated the 2026-10-08 changes; only their own edits were merged.
- The decoded copies of four maps filled the session's temporary disk (1.2 GB each); the
  check was redone by comparing the built files instead.

**Harwick's flag had an empty top row; Kampf's layer matched no country** (2026-10-08)
- Cause: in the author's flag file the top row of the Harwick layer is transparent (a
  see-through line along the top of the flag in game), and the layer "Kampf Empire" is
  not the country's name (the Kampfian Empire), so `import_flags.py` skipped it.
- Fix: the row was filled from the one below it; "kampf empire" is an `import_flags`
  alias.

**Labels on the Borders layer again, and another stale LEAVE pixel** (2026-10-08)
- The author's island labels (SO, MA, KE, DU, "Mahina (MA)" ...) were written on
  Necessary Borders: 88 small marks among three real new lines. As lines they would
  have cut the islets into scraps. Fix: every new mark but the three lines (found as
  8-connected pieces, checked by eye) moved to Necessary Names before apply_outlines.
- `LEAVE` still held (297, 1887), which now lies in Zwintern's patch, and (554, 1814),
  now Ungar: both would have stopped those patches being assigned, as happened with
  Transcainia. Fix: removed; every `LEAVE` pixel is now checked against the seeded
  patches before a run.

**Transcainia's land stayed Araseos** (2026-10-07, author's screenshot)
- Cause: `apply_outlines.py` had an old `LEAVE` pixel, (403, 1359), from 2026-10-05.
  The new lines put it inside Transcainia's patch, and `LEAVE` beat the seed, so the
  patch was skipped silently. A first rerun with the full 2026-10-07 `OWNERS` also
  re-cut Großlöwenburg (a seeded, finished country whose states regroup had joined
  across lines); that was thrown away.
- Fix: the old pixel was removed from `LEAVE`, and the rerun seeded only Transcainia
  (6 new states). Lesson: rerun with only the new seeds, and check `LEAVE` pixels still
  lie in the land they were meant for.

**Borders on the wrong layers, a gap, and unlabelled patches** (2026-10-07)
- Cause:
  - The borders of Sminishia, Gorbastan and Zukchiva were drawn on Necessary Names.
  - "PE" and "(TP)" were written on Necessary Borders.
  - A one-pixel gap south of Ostaria joined Ostaria to Hwitland.
  - Seven unlabelled patches the new lines enclosed went to `DEFAULT_OWNER`.
- Fix:
  - Line-shaped pieces on Names moved to Borders, and letter-sized pieces on Borders
    moved to Names.
  - The gap was found by listing loose line ends.
  - The unlabelled patches are on `LEAVE`.
  - Each nation's land was found from the author's labels: a name takes the bordered
    area around it, an island label the land nearest it. A rendered proposal was
    checked before `apply_outlines.py` ran.

**A 5 px province in Kurikia stopped the build; San Sierra's state lines leaked** (2026-10-05)
- Cause: re-running `regroup_states.py` over every drawn country left a 5 px scrap at
  (1242, 856). Separately, two of the author's San Sierra state lines had gaps, so
  neighbouring areas ran together into one state: one missing pixel, and one line
  stopping 4 px short of the coast.
- Fix: the scrap joined its neighbour in the same state, and the gaps were filled. To
  find dead-end line pixels, look for line pixels with at most one line neighbour that
  are not next to water.

**`apply_outlines.py` ran for hours, and nearly gave Solitas land to Terrabis-Seran** (2026-10-05)
- Cause: the clean-up of cut provinces compared every province against the whole
  window around the new outlines. This time the window ran from Cascadia to Harwick,
  about 1,900 × 1,200 px with thousands of provinces. Separately, three Solitas patches
  that the friend's outlines had closed off were unseeded, so they would have gone to
  `DEFAULT_OWNER`.
- Fix: each province is now checked inside its own bounding box. The three patches are
  on `LEAVE`. The script lists unseeded patches before writing; read that list.

**A new country bigger than the rest of its continent was nearly skipped** (2026-10-01)
- Cause: `apply_outlines.py` treated the biggest patch touching a line as "the rest of
  the continent" and left it alone. Fraxhemark (96k px) was the biggest.
- Fix: patches with a seed, on the LEAVE list, or already done can't be "the rest".

**Regions cut up and land regions redrawn without being asked** (2026-09-30)
- The author asked for the oceans of their map "split up as needed"; I also regrouped
  every land region and cut the oceans into ~350k px pieces. The author wanted the land
  left alone and each ocean whole, to edit themselves.
- Fix: land regions restored exactly (pixel for pixel), each ocean is one region.
  Lesson: change only what was asked; when "as needed" is vague, do the minimum.

**Strategic regions from the author's ocean map landed in the wrong oceans** (2026-09-30)
- Cause: the reference maps (`ref_oceans.webp`, `ref_continents.webp`) show an older
  arrangement of the continents than the drawing, so they can't be laid straight over
  the game map. Averaging each continent's mapped position then put open water in
  unrelated oceans (a "Northern Friedlich" region mid-map).
- Fix: each continent's shift was fitted separately (Nonscio and Araseos too), and the
  continents vote for the ocean. Names of oceans running all the way round were
  scrambled by the map's wrap; they are now read left to right.

**The author's `.pdn` was older than the current one** (2026-09-30)
- Cause: the upload predated the sea zones and colour changes; applying it would have
  undone them.
- Fix: game layers are kept from the current file and the author's own layers
  (outlines, rivers, names) taken from the upload. The updated `.pdn` is now sent back
  after every change.

**Selto was drawn too small** (2026-09-30)
- Cause: only the patch between two lines became Selto; the author's older drawing
  (Notes layer) has it along the Piscary coast.
- Fix: five coastal Linterre states given to Selto (`pdn_tools.py give`).

**Rivers ran through the middle of provinces** (2026-09-30)
- Cause: HOI4 only applies a river crossing between two provinces.
- Fix: `river_provinces.py` re-cuts provinces so rivers run along their borders. Its
  first versions left 1-2 pixel provinces (a tiny state with nothing to split, stray
  pixels of neighbouring states); both are now handled.

**New state lines split existing states** (2026-09-30)
- Fix: `apply_outlines.py` re-cuts only the states a new line splits, keeping their
  country. At first it also re-cut Cardonia's island states (islets across water looked
  like splits) and merged small drawn pieces as islets; both fixed. Nudges of a pixel
  or two are too small to detect and are moved by hand.

**Outlines were meant as states, not provinces** (2026-09-29)
- Fix: every outlined patch is a state (big ones several), each cut into small provinces.

**Provinces split in two, too small, or crossing at one corner**
- Cause: cutting provinces leaves scraps.
- Fix: scraps merge into a neighbour; four-province corners are fixed by moving single
  pixels. Check: every province is one connected piece of at least 16 px, and no four
  meet at a corner (these crash the game).

**Rivers drawn as 2×2 blocks, stubs, or tributaries overwriting the main river**
- Fix: the river tracer shortcuts loops, drops branches under 6 px, and finds branches
  from the raw lines. Check: HOI4's river rules.

## Rules learned the hard way (all checked by `check_mod.py`)

- `definition.csv` needs Windows line endings (CRLF).
- `weatherpositions.txt` needs a `small` and a `big` row per region (not "large").
- Localisation files need UTF-8 with BOM.
- `descriptor.mod` and the launcher's `.mod` file must match.
- Vanilla files that name Earth places (tutorial, AI navy plans) are overridden with
  empty or cut-down versions.
- With the Deco UI in the mod (2026-10-14): localisation may be in the game's other languages, but only the
  Deco UI's files (`valsora_deco_*_l_<language>.yml`, first line `l_<language>:`); a .gfx sprite of any kind
  (cornered tiles, progress bars, pie charts, `textureFile` in any case) counts as defined, and its textures
  must exist; a sprite the game's own .gui files name without defining (`GFX_category_end_bg`) is allowed in
  the copies of those files the Deco UI patches. The first merged build failed all three (38 errors), plus the
  Deco UI's sub-ideology text naming the game's Earth-bound ones (nazism ...), which Valsora keeps defined but
  never localises: the Deco UI now lists only the sub-ideologies Valsora names.
