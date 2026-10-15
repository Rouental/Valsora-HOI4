"""Put back textures that a re-render changed only by anti-aliasing noise (2026-10-15).

    python tools/restore_noise.py          from the project folder: restore them (git checkout)
    python tools/restore_noise.py --dry    list every changed texture and how much it changed

gen_textures.py draws through Chromium, and a re-render moves a few anti-aliased pixels in textures nothing changed
(section 3 of CLAUDE.md: "restore the shipped files when only that changed, so each release changes only what it
meant to"). A texture whose signature in texture_manifest.json differs from the committed manifest's was drawn from changed code
and is kept whatever it looks like (a deliberate colour tweak can be as small as noise). Any other modified texture
under valsora_deco_ui/ is compared with the committed one as the game composites it (colour times alpha, and alpha)
and restored when no pixel moved more than LIMIT (48 of 255: soft gradients and arcs vary by up to ~45 between runs);
a real change moves hundreds of pixels far more. Since gen_textures.py draws only the textures whose drawing changed,
this matters after `gen_textures.py --all`.
"""
import json
import os
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image

from ddsutil import read_dds
from paths import MANIFEST, ROOT

LIMIT = 48               # Chromium's soft gradients and arcs vary by up to ~45 from run to run


def signatures(top, ref=None):
    """the manifest's {path in the mod: signature}, as committed (ref) or on disk"""
    rel = os.path.relpath(MANIFEST, top)
    if ref is None:
        return {m["path"]: m.get("sig") for m in json.load(open(MANIFEST))} if os.path.isfile(MANIFEST) else {}
    r = subprocess.run(["git", "show", f"{ref}:{rel}"], capture_output=True, text=True, cwd=top)
    return {m["path"]: m.get("sig") for m in json.loads(r.stdout)} if r.returncode == 0 else {}


def main():
    dry = "--dry" in sys.argv
    top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, cwd=ROOT).stdout.strip()
    mod = os.path.relpath(os.path.join(ROOT, "valsora_deco_ui"), top)         # paths from the repository's root
    then, now = signatures(top, "HEAD"), signatures(top)
    out = subprocess.run(["git", "status", "--porcelain", "--", mod], capture_output=True, text=True, cwd=top).stdout
    for line in out.splitlines():
        st, path = line[:2], line[3:]
        if st.strip() != "M" or not path.endswith((".dds", ".png", ".tga")):
            continue
        full = os.path.join(top, path)
        in_mod = os.path.relpath(path, mod).replace(os.sep, "/")
        if then.get(in_mod) and now.get(in_mod) and then[in_mod] != now[in_mod]:
            print(f"keep   {path} (its drawing changed)")
            continue
        old = subprocess.run(["git", "show", "HEAD:" + path], capture_output=True, cwd=top).stdout
        with tempfile.NamedTemporaryFile(suffix=os.path.splitext(path)[1], delete=False) as tmp:
            tmp.write(old)
        read = read_dds if path.endswith(".dds") else Image.open
        try:
            a = np.asarray(read(tmp.name).convert("RGBA")).astype(int)
            b = np.asarray(read(full).convert("RGBA")).astype(int)
        finally:
            os.unlink(tmp.name)
        if a.shape != b.shape:
            print(f"keep   {path} (new size)")
            continue
        # as the game composites it: colour times alpha, and alpha (a fully clear pixel's colour is invisible)
        pa = np.dstack([a[..., :3] * a[..., 3:4] // 255, a[..., 3]])
        pb = np.dstack([b[..., :3] * b[..., 3:4] // 255, b[..., 3]])
        d = np.abs(pa - pb).max(axis=2)
        real = int((d > LIMIT).sum())
        print(f"{'keep ' if real else 'noise'}  {path}: {int((d > 0).sum())} px changed, at most {int(d.max())}")
        if not real and not dry:
            subprocess.run(["git", "checkout", "--", path], cwd=top)


if __name__ == "__main__":
    main()
