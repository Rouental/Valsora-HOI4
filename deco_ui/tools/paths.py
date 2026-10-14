"""Where everything lives. All build scripts import their paths from here.

Layout (relative to the project root = the folder above tools/):
    valsora_deco_ui/            the mod itself (output of the build; also shipped)
    tools/                      these scripts
    source_fonts/               Josefin Sans, Federo, Limelight, Bodoni Moda (SIL OFL)
    art/                        source art: menu_world.jpg (main menu map), map_rouental.jpg + flag_ROU.png (previews)
    reference/vanilla/          copy of the game's files the tools read: interface/*.gui, *.gfx
    reference/valsora/          the Valsora mod (localisation, ideologies, country tags, leaders for previews)
    build/                      intermediates and previews (safe to delete)

Every location can be overridden with an environment variable:
    VALSORA_DECO_ROOT, VALSORA_DECO_MOD, HOI4_DIR (the game folder, used instead of reference/vanilla),
    VALSORA_MOD_DIR (instead of reference/valsora).
"""
import os

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.environ.get("VALSORA_DECO_ROOT") or os.path.join(TOOLS, ".."))


def _d(p):
    return os.path.abspath(p) + os.sep


MOD = _d(os.environ.get("VALSORA_DECO_MOD") or os.path.join(ROOT, "valsora_deco_ui"))
FONTS_SRC = _d(os.path.join(ROOT, "source_fonts"))
ART = _d(os.path.join(ROOT, "art"))
VANILLA = _d(os.environ.get("HOI4_DIR") or os.path.join(ROOT, "reference", "vanilla"))
VALSORA = _d(os.environ.get("VALSORA_MOD_DIR") or os.path.join(ROOT, "reference", "valsora"))
BUILD = _d(os.path.join(ROOT, "build"))
PNG = _d(os.path.join(BUILD, "png"))
for _p in (BUILD, PNG):
    os.makedirs(_p, exist_ok=True)
