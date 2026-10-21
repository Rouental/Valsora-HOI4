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
    VALSORA_MOD_DIR (instead of reference/valsora), VALSORA_DECO_BUILD (instead of build/), VALSORA_BASE_DIR (instead of ../work/deco_base: the Valsora
    mod's own copies of the files the Deco UI replaces), CHROMIUM_PATH (the browser Playwright uses).
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
# the Valsora mod's own files that the Deco UI replaces (interface/countrypoliticsview.gui), as Valsora built them:
# since the Deco UI is part of the Valsora build (2026-10-14), build/valsora_test holds the Deco UI's copies, so
# the Valsora build keeps its own in work/deco_base/ (scripts/deco_ui.py) and make_politics.py starts from there
_base = os.environ.get("VALSORA_BASE_DIR") or os.path.join(ROOT, "..", "work", "deco_base")
VALSORA_BASE = _d(_base) if os.path.isdir(_base) else VALSORA
# VALSORA_DECO_BUILD: a build folder of one's own (2026-10-21), for helpers drawing side by side (gen_textures.py
# writes its page and screenshots there)
BUILD = _d(os.environ.get("VALSORA_DECO_BUILD") or os.path.join(ROOT, "build"))
# each texture's signature (gen_textures.py): in the repository, so a fresh clone redraws only what changed
# a scratch manifest for a test run of gen_textures.py (VALSORA_TEXTURE_MANIFEST), so it leaves the committed one alone
MANIFEST = os.environ.get("VALSORA_TEXTURE_MANIFEST") or os.path.join(ROOT, "texture_manifest.json")
# Chromium for Playwright: by default Playwright's own download; CHROMIUM_PATH points at another one
# (e.g. a cloud machine's pre-installed /opt/pw-browsers/chromium when the versions differ)
CHROMIUM = {"executable_path": os.environ["CHROMIUM_PATH"]} if os.environ.get("CHROMIUM_PATH") else {}
PNG = _d(os.path.join(BUILD, "png"))
for _p in (BUILD, PNG):
    os.makedirs(_p, exist_ok=True)
