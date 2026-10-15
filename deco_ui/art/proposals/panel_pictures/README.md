# Panel picture proposals (not in the mod)

Proposals for the pictures still inside the side panels, drawn by `tools/proposals_panels.py` (2026-10-15). The
author asked to see and approve them before they go in: "do the panel pictures, but don't put them in the mod yet".
Each keeps the size, frames and layout of the game's picture it would replace (the slots the game writes into, the
dark side its text sits on), so it can go in later as a texture at the game's path, like the rest of the Deco UI.

| proposal | replaces (the game's path) | the game's picture |
|---|---|---|
| `research_top_win.png` | `gfx/interface/research_top_win.dds` (548 x 138) | the research panel's header: a 1930s laboratory photograph |
| `production_win_top.png` | `gfx/interface/production_win_top.dds` (550 x 253) | the production header: riveted steel, crossed hammers, its factory slots |
| `market_ui.png` | `gfx/interface/international_market/market_ui.dds` (540 x 140) | the market's header: a photograph of rows of trucks |
| `overview_top_strip.png` | `gfx/interface/overview_top_strip.dds` (1566 x 59, 3 frames) | the army, navy and air overviews' headers: photographs |
| `create_agency_bg.png` | `gfx/interface/operatives/create agency_bg.dds` (508 x 99) | the intelligence agency's plate |
| `spirit_banner_decoration_{army,navy,air}.png` | `gfx/interface/officer_corp/spirit_banner_decoration_*.dds` (460 x 66) | the officer corps' ornaments: tanks, ships, planes |

To put an approved one in: move its drawing from `tools/proposals_panels.py` into `tools/gen_textures.py` at the game's
path, and add the path to `validate_preview.SAME_SIZE`. The comparison with the game's pictures is written to
`build/proposals_panel_pictures.png` (git-ignored: it holds the game's art).
