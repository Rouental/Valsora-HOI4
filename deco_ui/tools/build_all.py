"""Rebuild the whole mod: fonts, textures, then the .gui/.gfx/localisation generators, then checks
and previews. Usage:  python tools/build_all.py            (uses reference/ and art/ under the project)
Textures need Playwright with Chromium (pip install playwright; playwright install chromium);
everything else is plain Python 3 + Pillow + numpy.

    python tools/build_all.py gen_textures.py ...   skips the steps named (e.g. the slow texture step)

Steps in the same stage don't depend on each other and run side by side (2026-10-15: 81 s one after another, about
35 s so); each step's output is printed whole, in order, once its stage is done. The files are the same either way.
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
STAGES = [
    ["gen_fonts.py", "game_fonts.py"],                       # the mod's fonts and the game's, redrawn
    ["gen_textures.py"],                                     # sizes come from the fonts' metrics
    ["make_topbar.py", "make_politics.py", "make_stateview.py", "make_focus.py", "make_menu.py", "make_panels.py",
     "make_leadergroups.py", "make_mapviews.py", "make_events.py", "make_research.py", "make_setup.py",
     "make_popups.py",                                       # v0.10.2: the release dialog's text above its checkboxes
     "make_music.py",                                        # 2026-10-19: the music player's station box
     "make_panel_pictures.py",                               # v0.11: the side panels' own pictures
     "make_insignia.py"],                                    # 2026-10-20: the army insignias' frame count
    ["validate_preview.py"],                                 # the checks, before any preview
    ["preview_screens.py", "preview_panels.py", "preview_focus.py", "preview_armybar.py", "preview_events.py",
     "preview_game_fonts.py", "preview_research.py", "preview_designers.py",
     # v0.10's screens: the battle plan, the frames and popups, the badges, the battles, diplomacy, game setup
     "preview_battleplan.py", "preview_windows.py", "preview_popups.py", "preview_mapviews.py", "preview_combat.py",
     "preview_diplo.py", "preview_setup.py",
     "preview_navy.py",                                      # v0.10.1: the selected fleet's panel
     "preview_alerts.py", "preview_deployment.py",           # 2026-10-20: the alerts, loading bar, training, goals
     "preview_insignia.py"],                                 # 2026-10-20: the army insignias
]
# the generators write files the next ones read (make_topbar writes the fonts' .gfx, make_politics reads Valsora's
# screen ...), so they stay one after another
SEQUENTIAL = {2}
steps = [s for stage in STAGES for s in stage]           # the order, for anyone reading the list
skip = set(sys.argv[1:])
unknown = skip - set(steps)
if unknown:
    sys.exit(f"no such step: {', '.join(sorted(unknown))} (steps: {', '.join(steps)})")
start = time.time()
for n, stage in enumerate(STAGES):
    todo = [s for s in stage if s not in skip]
    if n in SEQUENTIAL or len(todo) < 2:
        for s in todo:
            print(f"== {s}", flush=True)
            t = time.time()
            r = subprocess.run([sys.executable, os.path.join(HERE, s)], cwd=HERE)
            if r.returncode:
                sys.exit(f"{s} failed")
            print(f"   ({time.time() - t:.1f} s)", flush=True)
        continue
    t = time.time()
    runs = [(s, subprocess.Popen([sys.executable, os.path.join(HERE, s)], cwd=HERE, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, text=True)) for s in todo]
    failed = []
    for s, p in runs:
        out, _ = p.communicate()
        print(f"== {s}", flush=True)
        print(out, end="" if out.endswith("\n") or not out else "\n", flush=True)
        if p.returncode:
            failed.append(s)
    print(f"   ({', '.join(todo)}: {time.time() - t:.1f} s side by side)", flush=True)
    if failed:
        sys.exit(f"{', '.join(failed)} failed")
print(f"done ({time.time() - start:.0f} s)")
