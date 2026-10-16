"""The Valsora Deco UI as part of the mod (common.DECO_UI; author, 2026-10-14: "simplify things to only have
the one install", keeping the option of going back to the game's own interface).

Run by run_all.sh after build_mod.py. With DECO_UI on:
  1. the Valsora files the Deco UI replaces (REPLACES) are kept as Valsora built them in work/deco_base/: the
     Deco UI's tools start from those (deco_ui/tools/paths.py VALSORA_BASE), never from their own output;
  2. the Deco UI's files that depend on the Valsora mod are made again from this build, so they can't go stale:
     which country names need the medallion's small font (long_names.py), the politics screen with its
     sub-ideologies (make_politics.py, from Valsora's own countrypoliticsview.gui) and the research trees with
     Valsora's year labels (make_research.py, from its countrytechtreeview.gui);
  3. deco_ui/valsora_deco_ui/ is copied into build/valsora_test/, all but its own launcher descriptor, readme and
     thumbnail. A file both mods ship stops the build, unless the Deco UI replaces it on purpose (REPLACES).
Everything else of the Deco UI (textures, fonts, the patched game screens) is built by hand with the game's
files at hand: deco_ui/tools/build_all.py (deco_ui/CLAUDE.md, section 3).
With DECO_UI off it does nothing: build_mod.py has written the mod with the game's interface.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

from common import BUILD, DECO_UI, MOD_DIR_NAME

OUT = BUILD / MOD_DIR_NAME
DECO = Path(os.environ.get("VALSORA_DECO_ROOT") or "deco_ui")   # another copy of it for a test version
DECO_MOD = DECO / "valsora_deco_ui"
BASE = Path("work/deco_base") if BUILD == Path("build") else Path("work") / f"deco_base_{BUILD.name}"   # per build
SKIP = {"descriptor.mod", "README.txt", "thumbnail.png"}       # the Deco UI's own, as a separate mod
REPLACES = {"interface/countrypoliticsview.gui",                # built by the Deco UI from Valsora's own
            "interface/countrytechtreeview.gui"}               # (make_research.py: its year labels are Valsora's)
MARK = "Valsora Deco UI"                                       # the first lines of the Deco UI's files say so


def main():
    if not DECO_UI:
        print("Deco UI: off (common.DECO_UI), the game's own interface")
        return
    # 1. Valsora's own copies of the files the Deco UI replaces (when this runs again on a build it already
    #    merged, the copies from the first run stay)
    for rel in sorted(REPLACES):
        if MARK in (OUT / rel).read_text(encoding="utf-8-sig", errors="ignore")[:400]:
            if not (BASE / rel).exists():
                sys.exit(f"{OUT / rel} is the Deco UI's and work/deco_base has no Valsora copy: run build_mod.py first")
            continue
        (BASE / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(OUT / rel, BASE / rel)
    # 2. the Deco UI's files that follow the Valsora mod, made from this build
    env = dict(os.environ, VALSORA_MOD_DIR=str(OUT.resolve()) + os.sep, VALSORA_BASE_DIR=str(BASE.resolve()) + os.sep)
    for script, *args in (("long_names.py",), ("make_politics.py",), ("make_research.py", "--research-only")):
        r = subprocess.run([sys.executable, script, *args], cwd=DECO / "tools", env=env, capture_output=True, text=True)
        if r.returncode:
            sys.exit(f"deco_ui/tools/{script} failed:\n{r.stdout[-2000:]}\n{r.stderr[-3000:]}")
        last = [ln for ln in r.stdout.splitlines() if ln.strip()]
        print(f"Deco UI: {script}: {last[0] if script == 'long_names.py' and last else (last[-1] if last else 'done')}")
    # 3. into the mod (work/deco_base/copied.txt lists what an earlier run on this build copied, so this can run
    #    again without build_mod.py: those files are the Deco UI's, not Valsora's)
    listing = BASE / "copied.txt"
    ours = set(listing.read_text(encoding="utf-8").split()) if listing.exists() and MARK in \
        (OUT / sorted(REPLACES)[0]).read_text(encoding="utf-8-sig", errors="ignore")[:400] else set()
    clash, copied = [], []
    for f in sorted(DECO_MOD.rglob("*")):
        if not f.is_file():
            continue
        rel = f.relative_to(DECO_MOD).as_posix()
        if rel in SKIP:
            continue
        dst = OUT / rel
        if dst.exists() and rel not in REPLACES and rel not in ours:
            clash.append(rel)
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dst)
        copied.append(rel)
    listing.write_text("\n".join(copied) + "\n", encoding="utf-8")
    n = len(copied)
    if clash:
        sys.exit("Deco UI: these files are both the Valsora mod's and the Deco UI's (add them to REPLACES only if the "
                 "Deco UI builds its copy from Valsora's):\n  " + "\n  ".join(clash))
    print(f"Deco UI: {n} files copied into {OUT} (replacing Valsora's {', '.join(sorted(REPLACES))})")


if __name__ == "__main__":
    main()
