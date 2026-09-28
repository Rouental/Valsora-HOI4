"""Zip the built mod for installing: dist/valsora_test.zip holds the mod folder and
the launcher's valsora_test.mod, ready to unzip into Hearts of Iron IV/mod/."""
import zipfile
from pathlib import Path

from common import MOD_DIR_NAME

build = Path("build")
out = Path("dist") / f"{MOD_DIR_NAME}.zip"
out.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for f in sorted((build / MOD_DIR_NAME).rglob("*")):
        if f.is_file():
            z.write(f, f.relative_to(build).as_posix())
    z.write(build / f"{MOD_DIR_NAME}.mod", f"{MOD_DIR_NAME}.mod")
print(f"wrote {out} ({out.stat().st_size / 1e6:.1f} MB)")
