"""Zip the built mod for installing: dist/valsora_test.zip holds the mod folder and
the launcher's valsora_test.mod, ready to unzip into Hearts of Iron IV/mod/.

The zip is reproducible: the same mod gives the same bytes. Every entry carries one fixed date (1 January 1980, the
earliest a zip can hold, as reproducible builds do) and the same permissions, in sorted order, because the build
rewrites every file and their times would otherwise make each build's zip new to git even when nothing changed."""
import os
import zipfile
from pathlib import Path

from common import BUILD, MOD_DIR_NAME

DATE = (1980, 1, 1, 0, 0, 0)

build = BUILD
# VALSORA_ZIP: another file for a test version (it holds the same mod folder, so it installs in the mod's place)
out = Path(os.environ.get("VALSORA_ZIP") or Path("dist") / f"{MOD_DIR_NAME}.zip")
out.parent.mkdir(exist_ok=True)


def add(z, f, name):
    info = zipfile.ZipInfo(name, DATE)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    z.writestr(info, f.read_bytes(), compresslevel=9)


with zipfile.ZipFile(out, "w") as z:
    for f in sorted((build / MOD_DIR_NAME).rglob("*")):
        if f.is_file():
            add(z, f, f.relative_to(build).as_posix())
    add(z, build / f"{MOD_DIR_NAME}.mod", f"{MOD_DIR_NAME}.mod")
print(f"wrote {out} ({out.stat().st_size / 1e6:.1f} MB)")
