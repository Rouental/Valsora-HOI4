# Valsora Deco UI: its history, version by version

What each version changed, what the user saw in game and what it taught: moved out of `CLAUDE.md` §1 on 2026-10-15
(later), so the manual stays short; the lessons that still hold are in `CLAUDE.md` §6 (engine facts) and §9
(pitfalls). Add each new version at the end.

v0.4.3 was the first v0.3/v0.4 build the user launched. The user's reports so far cover only the main
menu: the Valsora background and the social links in the top-left corner show **(in game)**, but in
v0.4.3 and v0.4.4 none of the menu buttons did. v0.4.4 blamed `Origo` and was wrong. The user's
`error.log` showed the real cause: the game rejects a **quoted** `Orientation` on a
`containerWindowType` and falls back to `UPPER_LEFT` (section 6). v0.4.5 writes every orientation
bare, which also puts five right-anchored top bar windows back on the right, and moves
`alwaystransparent` off containers, where the game rejected it too. v0.4.6, the same day, moves five
continent labels on the menu background to the user's own arrangement (they sent the picture).
**(in game, v0.4.5)** the user then played: the top bar shows as designed, its right end included.
Their report and screenshots (2026-10-14) led to v0.4.7: the politics screen was Valsora's own (the
Deco UI loaded first; it now names Valsora as a dependency), the faction button's two pictures were
swapped (section 6), the world tension globe showed Earth (Valsora's main mod now draws a Valsora
globe at the vanilla path, `scripts/globe.py` there), and the map modes and minimap are still
unstyled (section 12). The state panel and focus tree have still not been seen in game.
**(in game, v0.4.7)** the user's first screenshots of the politics screen (2026-10-14) led to v0.4.8: the
panel hid the top bar's medallion below y 78 (side panels are drawn over the top bar) and left a gap under
the band; the header behind the portrait was vanilla's art (a runtime sprite swap); tooltips were
vanilla's (a .dds shadowed our .tga); the leader's description and the law cards took room the advisors &
laws list needed. v0.4.8 puts the panel flush under the band with a notch round the medallion and seal,
replaces both header textures and the tooltip's .dds, drops the description (the portrait's own tooltip
has it) and the law cards, adds the sub-ideology, moves the spirits up beside the popularity, and the
list starts 156 px higher.
**v0.5 (2026-10-14, not yet seen in game)**, the user's next request: "apply the same no-gap fix to the other
side panels, and begin styling them ... style the bar and map ... roll the UI mod into the main Valsora mod,
but with the knowledge that I might eventually want it taken out again". So: every other side panel (16, and
17 windows that open beside them) opens flush under the band with the politics screen's notch and a deco
header (`make_panels.py`, `layout_panels.py`); the pictures the panels share (close buttons, background tiles,
header bars, tabs, sort buttons, filters, checkboxes) are replaced at their vanilla paths; the map modes and
minimap are styled (gilt-recoloured game icons, line-icon medallions, a gilt minimap drawn by the Valsora
mod); and the **Deco UI is part of the Valsora mod**: the Valsora build copies `valsora_deco_ui/` into its
own (`scripts/deco_ui.py` there, switched by `DECO_UI` in `scripts/common.py`). There is no separate
release any more (section 11).
**(in game, v0.5)** the user's video (2026-10-15, playing Myehn: "I love it so far"): the panels open flush
with their notch, but a newly opened panel slid in from the left over the flag and the country's name before
its notch reached them, choppily the first time (the panel's pictures loading) and still across them later;
switching panels, the old one slid out the same way. **v0.5.1** opened every side panel, and every window
beside one, by rising 36 px into place over 200 ms instead of sliding 600 px across the screen.
**(in game, v0.5.1)** the user's screenshot (2026-10-15): a closed division overview stayed on screen 36 px below
its place, its header gone and its lists showing over the map. The game does not hide a closed side panel; it
moves it to `position` and leaves it there (section 6). **v0.5.2** parks every closed panel at the game's off-screen
`position` again and opens it at once (`animation_time = 0`, as vanilla's dropdowns do): no slide across the flag,
nothing left on screen. The same release moved the main menu's career profile star (it covered the button's label).
**v0.6 (2026-10-15, not yet seen in game)**, the user's request "begin to work on styling the superevents and focus
tree to be more like they were in the mockup. Leave the icons on the focus tree alone": the focus tree opens flush
under the band with the panels' notch (it was drawn over the medallion like the panels were), with the mockup's
header (the country's focus tree title, full name and sub-ideology from a scripted GUI on the focus view), its scale
pattern canvas in a gilt frame, an octagon medallion and plate under every focus in four states (the in-progress one
red, through a copy of the game's `nationalfocusview.gfx`), a gilt halo behind the focus in progress, gilt links and
red exclusive marks. The superevent window is the Valsora mod's (`scripts/superevents_deco.py` there, with
`DECO_UI`), drawn from the mockup's Superevent board with this project's fonts. The top bar's date box is 230 px
(x 55; 220 until then) and the speed chevrons start at x 286: since Valsora moved to 2036 the widest date the game
shows, "00:00, 30 September, 2040", is 230 px, and the preview's long sample is that date.
**v0.7 (2026-10-15, overnight, not yet seen in game)**, the user's picks "Do the army bar, the event window ...": the
**army bar** (the cards along the bottom: the user's request after v0.2) re-skinned by textures at the game's paths
and sizes, plus `make_leadergroups.py`, which moves the division counts onto the frames' plaques. The user's notes
on its first preview: "the bar above the field marshal cuts off weirdly" (the preview's fault: it put the army
group's piece of the plate behind both the marshal and his first army; the game's pieces make one plate, the army
group's piece starting it, the armies' carrying it on, the last army's ending it, `layout_armybar.py`), "the plus
over the empty general isn't quite centered, nor are the numbers" (the game draws the empty card 1.5 px left of the
opening, and its count 3 px above the plaque: both fixed). The **events** (country, leader, operative, news)
re-skinned the same way, with `make_events.py` giving them the mod's fonts. Panel picture proposals, for the user's
approval and **not in the mod**, are in `art/proposals/`.
**v0.8 (2026-10-15, the second night, not yet seen in game)**, the user's notes on the v0.7 previews and their
request "could you switch to the art deco fonts throughout the UI? for example, currently the title of Roland is
displayed in the base game's font": the **game's own fonts** (28: the tooltips', the lists', the typewriter of the unit,
leader and designer screens, the Garamond of settings and menus, the Orator of window titles) are redrawn in the deco
faces at the game's paths (`game_fonts.py`, section 7), so every screen the mod hasn't re-laid reads in Josefin and
Federo. The army bar's play / stop row and its plate sit on the card's centre line ("aren't centered above the
general": the game draws each row 4 px right of the portrait's opening; `layout_armybar.MOVES`); the events' options
are centred between the picture and the card's right edge ("the decision box is shown significantly closer to the
image than it is to the other side of the box"; `layout_events.py`) and a leader event's foot matches; the news
masthead has a gilt globe of Valsora in the middle with WORLD and NEWS balanced either side ("looks lopsided ...
maybe make the ball a stylized Valsoran globe?"; `globe_art.py`). A mockup of larger flags, **not in the mod** (the
user: "don't add anything to do with it into the mod yet"), is in `art/proposals/hd_flags/`.
**v0.8.1 (2026-10-15, later, not yet seen in game)**, the user on v0.8's masthead: "it still looks lopsided. I'd like it
to be centered, and I like the globe, but it's not quite there yet ... maybe swap to something like "Valsoran
Standard" or Clarion or Dispatch ... so both words are the same length". WORLD is wider than NEWS, so with the globe in
the middle the name leaned left. The masthead is now **VALSORAN (globe) STANDARD**, two words Federo sets to the same
width, each placed by its ink the same distance from a medallion that breaks the rules (`layout_events.news_masthead`;
its rules as wide as the words, clear of the minimize button). The globe is redrawn (`globe_art.globe`): the land
simplified to what 60 px can show (the old one, lit and with every lake, was a speckled blob), flat gilt, a graticule,
looking down on open sea with land round it. The game's own news layout was off-centre too (the picture 5.5 px and
the headline 7 px left of the page's middle, the story's box 5 px right of it): all centred (`layout_events.NEWS_*`). Other names, drawn by the same code, are in
`art/proposals/news_masthead/` (`proposals_masthead.py`; switching is `layout_events.NEWS_WORDS`).
**v0.8.2 (2026-10-15, the third round, not yet seen in game)**, from the user's screenshots of v0.8.1 with Rouental's
test decisions: the superevent's title was "all jumbled together" (the scripted GUI had a visibility trigger for each
picture but none for the eight baked title strips, so all drew at once: the Valsora mod's `superevents.py` now writes
`valsora_superevent_title_<id>_visible`); "the guillotine logo won't be suited for all superevents" (its crest is
Valsora rising, the top half of the masthead's globe on a lacquer medallion: `superevents_deco.EMBLEM`); "the logo at
the top of country / leader / long events doesn't read so well at this size" (a stepped keystone with a diamond:
`crests.py`, `EV_CREST`); a long option spilled its third line (`valsora_deco_option_14`, a 14 px line, three to the
plate); names like KAMPFIAN EMPIRE showed "KAMPFIAN ..." (the name's box was exactly two 20 px lines high and the game
showed one: `layout.NAME_SLACK` gives it 4 px above and below); "the army tab is covered up by the country tab" (the
selected armies' badges, the air wings and the operatives start under the medallion: `make_mapviews.py`,
`layout.BELOW_MEDALLION`). The globe is lit again (the user wasn't "quite satisfied"); the first globe, v0.8.1's and
three other ideas are in `art/proposals/news_globe/` (`proposals_globes.py`), the crests' other designs in
`art/proposals/crests/` (`proposals_crests.py`). A test version of the Valsora mod with 1.5 times larger flags is
built with `VALSORA_FLAG_SCALE=1.5` (`layout.FLAG_SCALE`: the medallion 26 px taller, the flag 123 x 78 at 1:1; the
Valsora repository's `docs/HD_FLAGS_TEST.md`); the mod itself stays at 82 x 52.

**v0.8.3 (2026-10-15, the fourth round, not yet seen in game)**, the user on v0.8.2's options: "For the event crest, I
think I like the stepped keystone, but maybe lower the diamond just a little so it's not touching the top?" (the
diamond 12.5 px above the card's edge, 15 before: `crests.py`); "I think the globe I'm sending now is my current
favorite of your designs" (the newsreel globe with its tilted ring is the masthead's: `layout_events.NEWS_GLOBE_STYLE =
"ringed"`); "maybe raise the globe so it intersects the top of the event panel in the center, and show the whole globe"
(the Valsora mod's superevent crest is that globe, whole, across the frame's top edge: `scripts/superevents_deco.py`
there). The build got faster without changing a byte (the user: "Is there anything else you can do to streamline the
modding process"): `tools/build_all.py` runs independent steps side by side (81 s to 31 s), `preview_panels.py` draws
the panels on four cores (41 s to 16 s), and `validate_preview.py` draws the top bar preview only when it runs itself,
not each time a preview script imports it; every file and preview was compared byte for byte.
