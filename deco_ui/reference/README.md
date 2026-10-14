# reference/: inputs the build reads (never shipped, never committed)

The tools read the game's and the Valsora mod's files. They are not part of this project.
**Paradox's files must not be redistributed, so keep them out of the mod and out of git**
(`.gitignore` already excludes this folder's contents).

## Easiest: point at the real folders

```
HOI4_DIR="C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV"
VALSORA_MOD_DIR="<path to the Valsora mod folder>"
```

Set these as environment variables and nothing needs copying.

## Or copy into reference/

```
reference/vanilla/                 from the HOI4 install folder
    interface/                     the whole folder (*.gui, *.gfx)
    00_defines.lua                 common/defines/00_defines.lua     (reference only)
    00_graphics.lua                common/defines/00_graphics.lua    (reference only: flag sizes etc.)
    gfx/interface/...              only the textures you need to measure (army bar, map modes: see
                                   docs/next_army_bar_and_map_modes.md)
reference/valsora/                 the Valsora mod folder (or a symlink to it): localisation/,
                                   common/country_tags, common/ideologies, interface/countrypoliticsview.gui,
                                   gfx/leaders (for the politics preview portrait)
```

What reads what:

- `make_topbar.py` reads `interface/topbar.gui` and `interface/alerts.gui` from vanilla. From
  Valsora it reads `localisation/**/_l_english.yml`, `common/country_tags`, `common/ideologies`, and
  `set_cosmetic_tag` uses in any `.txt`.
- `make_politics.py` reads Valsora's `interface/countrypoliticsview.gui`, falling back to
  vanilla's.
- `make_menu.py` reads `interface/frontendmainview.gui` from vanilla.
- `validate_preview.py` reads every vanilla `interface/**/*.gfx` (to know which sprites exist) and
  the vanilla copies of each .gui the mod overrides.
