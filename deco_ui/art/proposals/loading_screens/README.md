# Loading screens: a proposal (not in the mod)

The author (2026-10-16, the overnight list): "Do maybe 3 or 4 loading screens as suggested in 8 as well, but don't add
them yet." Nothing here is in the mod: the game still shows its own loading screens.

Four pictures in the Deco UI's style, drawn from Valsora's own map by `tools/proposals_loading.py` (from the Valsora
build's `work/`, so they follow the map when it changes):

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

## How they would go in

The game's loading screens are `gfx/loadingscreens/load_<n>.dds`, 1920 x 1440 (at 16:9 the middle 1,080 rows show,
from row 180), the same files the main menu's background manager lists (`common/frontend/backgrounds/`). The game
picks one at random each time it loads. To use these, the Deco UI would ship them at those paths (DDS, as the menu
background), replacing the base game's pictures; the loading bar and tip (`interface/load_screen.gui`) could be styled
to match at the same time. Say which ones to keep, or what to change, and they go in.
