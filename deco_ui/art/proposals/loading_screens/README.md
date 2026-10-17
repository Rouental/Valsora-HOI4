# Loading screens: in the mod since v0.10

The author (2026-10-16, the overnight list): "Do maybe 3 or 4 loading screens as suggested in 8 as well, but don't add
them yet." Then (2026-10-17): "Please start applying the proposed changes to all the UI screens": since v0.10 they are
in the mod, drawn by `tools/make_loading.py` (which this proposal's `proposals_loading.py` became) at
`valsora_deco_ui/gfx/loadingscreens/valsora_load_1..4.dds`. The pictures here are the proposal as it was shown.

Four pictures in the Deco UI's style, drawn from Valsora's own map (from the Valsora build's `work/`, so they follow the
map when it changes):

1. **`load_1.jpg` The world**: the continents in gilt on a lacquer chart with a faint graticule, their names in
   Federo capitals. "Valsora · The world in the year 2036".
2. **`load_2.jpg` Valsora rising**: the masthead's globe (`globe_art.globe`), large, rising from the bottom of the
   screen in a gilt ring, with rays behind it, as the superevent's crest.
3. **`load_3.jpg` The Vale of Reibonne**: Rouental and the seven other Association states close up, each in a deep
   tone of its own map colour with gilt borders, the rivers drawn on the map, the ranges the author drew on the fief
   map (`source/vale_ranges.png`) as gilt chevrons, Rêverie's star. Guedelon has only 48 pixels of land on the map
   today, so it is a dot with its name beside it, as are the other states whose name is wider than their land.
4. **`load_4.jpg` The nations of Valsora**: every nation in its map colour, muted towards the lacquer and warmed with
   gilt, gilt borders, faint rays behind.

`sheet.png` shows each as a 16:9 screen shows it, with plain boxes where the game draws its loading bar (top centre)
and its loading tip (bottom centre); the titles sit under the bar and the maps end above the tip.

## How they went in

The game draws no picture of its own on the loading screen (`interface/load_screen.gui`): its list of backgrounds
(`common/frontend/backgrounds/base_backgrounds.txt`, the main menu's pictures, with the game's own `load_1` ...
`load_9` among them) is, as far as the game's files show, also its list of loading pictures (to be confirmed in game). The Deco UI's list is the menu's picture first, then these
four (`make_menu.py`), 1920 x 1440 (at 16:9 the middle 1,080 rows show, from row 180), with their 192 x 144 pictures for
the menu's "Change background". The loading bar and tip are the Deco UI's too (`gen_textures.py`, the `ld_` keys).
Which picture shows when, and that the menu keeps its own as the default, are still to be seen in game.
