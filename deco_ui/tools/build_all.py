"""Rebuild the whole mod: fonts, textures, then the .gui/.gfx/localisation generators, then checks
and previews. Usage:  python tools/build_all.py            (uses reference/ and art/ under the project)
Textures need Playwright with Chromium (pip install playwright; playwright install chromium);
everything else is plain Python 3 + Pillow + numpy.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
steps = ["gen_fonts.py", "gen_textures.py", "make_topbar.py", "make_politics.py", "make_stateview.py",
         "make_focus.py", "make_menu.py", "make_panels.py",
         "validate_preview.py", "preview_screens.py", "preview_panels.py", "preview_focus.py"]
skip = set(sys.argv[1:])           # e.g.  python build_all.py gen_textures.py   to skip the slow step
for s in steps:
    if s in skip:
        continue
    print(f"== {s}", flush=True)
    r = subprocess.run([sys.executable, os.path.join(HERE, s)], cwd=HERE)
    if r.returncode:
        sys.exit(f"{s} failed")
print("done")
