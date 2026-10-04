"""Copy flags out of the author's flag .pdn (one layer per flag) into source/flags/.

A layer is matched to a country by its name: the country's name, its key in
common.COUNTRIES or its tag (case and accents ignored), or ALIASES for the rest.
Extra NAME=FILE pairs on the command line add aliases for one run (e.g. "Layer 13=THD").
Layers matching nothing are listed and skipped; a flag already in source/flags is
replaced only if the picture differs.

    python3 scripts/import_flags.py <flags.pdn> ["Layer name=TAG" ...]
"""
import subprocess
import sys
import unicodedata
from pathlib import Path

import numpy as np
from PIL import Image

from common import COUNTRIES

FLAGS = Path("source/flags")
WORK = Path("work/pdn_flags")
# layer names that are not a country's name (author's flag file, 2026-10-04)
ALIASES = {
    "communist rouental": "ROU_communism",
    "marchers": "MRC",
}


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn").strip()


def main():
    subprocess.run([sys.executable, str(Path(__file__).parent / "readpdn.py"), sys.argv[1], str(WORK)],
                   check=True, stdout=subprocess.DEVNULL)
    names = (WORK / "layers.txt").read_text().splitlines()
    match = dict(ALIASES)
    for key, (tag, name, _, _) in COUNTRIES.items():
        for k in (key, tag, name):
            match[norm(k)] = tag
    for a in sys.argv[2:]:
        layer, tag = a.rsplit("=", 1)
        match[norm(layer)] = tag
    for k, nm in enumerate(names):
        tag = match.get(norm(nm))
        if tag is None:
            print(f"  {nm!r}: no country of that name, skipped")
            continue
        a = np.load(WORK / f"layer{k}.npy")
        im = Image.fromarray(a, "RGBA")
        out = FLAGS / f"{tag}.png"
        if out.exists():
            old = Image.open(out).convert("RGBA").resize(im.size)
            if np.abs(np.asarray(old, int) - a).mean() < 3:
                print(f"  {nm!r} -> {out}: unchanged")
                continue
        im.save(out)
        print(f"  {nm!r} -> {out}: written")


if __name__ == "__main__":
    main()
