# The Association of Reibonnaise States: emblem (proposal, 2026-10-19)

Not in the mod yet. The author chose neither A nor B (2026-10-19, night) and sent a sketch of their own: version C,
below. A and B are kept for the record.

## Version C: the author's design (2026-10-19, night)

The author: "Try making the Association of Reibonnaise states icon similar to this. (Note that Hollier and Lanzerac
both use their old flags, the interlinked diamonds for Lanzerac and the red field with fleurs de lis for Hollier.
Replace them with the flags in the mod.)"

As the sketch: a central stem, four rays a side branching from it and running out past the shape to arrowheads, and
between the rays eight waving banners, the members' flags, the outline of the whole a scalloped leaf. Left, from the
top: Guedelon, Seigne, Lustiana, Hollier; right: Evriches, Lanzerac, Selgrave, Rouental. Every flag is the mod's own
(`source/flags/`): Hollier's red with the fleur in its ring of charges, Lanzerac's purple with its gold emblem in a wreath.
Drawn symmetric (the sketch is nearly so).

| file | for |
|---|---|
| `emblem_C_gilt.png` (2048 px), `.svg` | gilt lines with a dark edge: reads on the game's dark screens and on paper |
| `emblem_C_ink.png` (2048 px), `.svg` | the sketch's dark lines, for outside the game on a light ground |
| `game_C_gilt.png` / `_ink` (200 x 100) | the game's faction logo: the logo, then its lit frame |
| `miniature_C_gilt.png` / `_ink` (32 x 32) | the game's miniature: the leaf, its banners and the stem, without the arrows |
| `sheet_C.png` | both line colours, every size, on the Deco UI's lacquer and on paper |

`make_c.py` draws them again (it uses `make.py`'s renderer). At 32 px eight flags are only patches of colour; a
miniature of the leaf's outline and stem alone, or of one banner, would read better if that matters.

## Versions A and B (2026-10-19)

Two versions, the same design:

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

To put one in the mod, after a yes: the two game pictures become `gfx/interface/factions/faction_logos/valsora_reibonnaise*.dds`,
with their sprites, and `faction_template_reibonnaise_association` (`scripts/nations.py`) takes
`icon = GFX_faction_logo_valsora_reibonnaise` in place of the game's generic logo.
