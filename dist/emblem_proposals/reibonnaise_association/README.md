# The Association of Reibonnaise States: emblem (proposal, 2026-10-19)

Not in the mod yet. Two versions, the same design:

- **A**: eight gold lozenges;
- **B**: the lozenges red and white, the colours of Rouental's and Seigne's lozengy.

What it is made of (all from the members' own flags):

- **a blue roundel in a gilt rim**: Guedelon's and Evriches' blue, the field of Rouental's lion and fleurs;
- **a ring of eight lozenges, one for each member** (Rouental, Seigne, Evriches, Hollier, Selgrave, Lustiana,
  Lanzerac, Guedelon): the lozenges come from Rouental's and Seigne's flags, and the ring from Hollier's ring of charges;
- **a fleur-de-lis over an upright sword**: the fleur is Rouental's and Hollier's, the sword Rouental's, Selgrave's and
  Guedelon's; together they stand for the faction's manifest, *Strength in Unity*;
- **a faint sunburst** behind them, as in the Deco UI.

| file | for |
|---|---|
| `emblem_seal_A.png` / `_B` (2048 px), `.svg` | outside the game: the roundel inside a band with the name and the motto |
| `emblem_A.png` / `_B` (2048 px), `.svg` | the roundel alone |
| `game_A.png` / `_B` (200 x 100) | the game's faction logo: the logo, then its lit frame |
| `miniature_A.png` / `_B` (32 x 32) | the game's miniature (the top bar's faction button, lists): the ring and the fleur only |
| `sheet.png` | every size side by side, on the Deco UI's lacquer and on paper |

The SVGs carry the Federo font inside them, so the name and the motto show in a browser. `make.py` draws everything
again.

To put it in the mod, after a yes: the two game pictures become `gfx/interface/factions/faction_logos/valsora_reibonnaise*.dds`,
with their sprites, and `faction_template_reibonnaise_association` (`scripts/nations.py`) takes
`icon = GFX_faction_logo_valsora_reibonnaise` in place of the game's generic logo.
