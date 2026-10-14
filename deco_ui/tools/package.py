"""Zip the built mod for the author: valsora_deco_ui/ plus the launcher's valsora_deco_ui.mod, ready to
unzip into Documents/Paradox Interactive/Hearts of Iron IV/mod/.

    python tools/package.py [output.zip]      (default: build/valsora_deco_ui_<version>.zip)
"""
import os
import re
import sys
import zipfile

from paths import ROOT, MOD, BUILD

version = re.search(r'version="([^"]+)"', open(os.path.join(ROOT, "valsora_deco_ui.mod"), encoding="utf-8").read()).group(1)
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BUILD, f"valsora_deco_ui_{version}.zip")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(os.path.join(ROOT, "valsora_deco_ui.mod"), "valsora_deco_ui.mod")
    n = 0
    for d, _, files in os.walk(MOD):
        for f in sorted(files):
            p = os.path.join(d, f)
            z.write(p, os.path.join("valsora_deco_ui", os.path.relpath(p, MOD)))
            n += 1
print(f"wrote {out} (v{version}, {n} files, {os.path.getsize(out) / 1e6:.1f} MB)")
