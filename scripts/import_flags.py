"""Copy flags out of the author's flag .pdn (one layer per flag) into source/flags/.

A layer is matched to a country by its name: the country's name, its key in
common.COUNTRIES or its tag (case and accents ignored), or ALIASES for the rest.
Extra NAME=FILE pairs on the command line add aliases for one run (e.g. "Layer 13=THD").
Layers matching nothing are listed and skipped; a flag already in source/flags is
replaced only if the picture differs (see changed()). See-through pixels are filled
first (opaque()), since the game shows them as holes in the flag.

    python3 scripts/import_flags.py <flags.pdn> ["Layer name=TAG" ...]
    python3 scripts/import_flags.py <folder> ["File name=TAG" ...]

A folder (2026-10-17) holds one PNG per flag, named after its nation the way a layer would be ("Krionik.png"); a
leading number is ignored, so the layers pdn_recover.py saves from a damaged flag file ("07_Krionik.png") import as
they are.
"""
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

from common import COUNTRIES

FLAGS = Path("source/flags")
WORK = Path("work/pdn_flags")
# layer names that are not a country's name (author's flag file, 2026-10-04)
ALIASES = {
    "communist rouental": "ROU_communism",
    "marchers": "MRC",
    "garfield": "GFR",
    "gheso": "GHS",
    "riverrain": "RVR",
    "s. pollana": "SPL",
    "kingdom of god": "SEE",
    "illiricium (kingdom)": "KIL",
    "illiricium (republic)": "ILR",
    "terreich": "TUP",
    "serantian": "SRN",
    # 2026-10-07, later (New_Mod_Flags.pdn)
    "carcaraise": "CRL",
    "marcher lords": "MRC",
    "rouental (authoritarian)": "ROU_fascism",
    "rouental (theocratic)": "ROU_theocracy",
    "rouental (communist)": "ROU_communism",
    "rouental (democratic)": "ROU_democratic",
    # 2026-10-08
    "kampf empire": "KPF",
    # 2026-10-18: the flag file's layer for Rouental's Reibonne flag (nations.COSMETICS, flown as the People's Republic)
    "rouental (reibonne)": "ROU_REIBONNE",
    # 2026-10-18: flags that came by the Gazetteer (Ungar's four governments', Krionik's releasable Formosa), as the
    # flag file names its layers
    "ungar (authoritarian)": "UNG_fascism",
    "ungar (communist)": "UNG_communism",
    "ungar (democratic)": "UNG_democratic",
    "ungar (theocratic)": "UNG_theocracy",
    "formosa": "FOM",
}


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn").strip()


def opaque(a):
    """The flag with every see-through pixel laid over the nearest solid one, as was done
    by hand for Harwick's empty top row and Royalist Illiricium's gaps (2026-10-09:
    Belka's emblem had a soft see-through edge)."""
    solid = a[..., 3] == 255
    if solid.all() or not solid.any():
        return a
    idx = ndi.distance_transform_edt(~solid, return_distances=False, return_indices=True)
    under = a[idx[0], idx[1], :3].astype(float)
    alpha = a[..., 3:].astype(float) / 255
    rgb = (a[..., :3] * alpha + under * (1 - alpha)).round().astype(np.uint8)
    return np.dstack([rgb, np.full(a.shape[:2], 255, np.uint8)])


def changed(path, a):
    """Whether the flag at path differs from the layer pixels a. At the same size any
    visible pixel counts (2026-10-09: Serie's four new corner anchors cover 4 % of the
    flag, and the old test, a mean difference of 3 or more, missed them). At another
    size, say an older or larger copy of the same picture (Rouental's 1180 x 700
    original), both are compared at twice the game's size, where resampling differs by
    little."""
    old = np.asarray(Image.open(path).convert("RGBA"), int)
    a = a.astype(int)
    if old.shape == a.shape:
        seen = (old[..., 3] > 0) | (a[..., 3] > 0)  # fully transparent pixels don't count
        return bool(np.any((old != a).any(axis=2) & seen))
    # a layer that is the old picture enlarged pixel for pixel (2026-10-18: the flags only ever had at the game's
    # 82 x 52, put into the flag file at its size) shrinks back to it by taking every block's middle
    back = np.asarray(Image.fromarray(a.astype(np.uint8), "RGBA").resize(old.shape[1::-1], Image.NEAREST), int)
    if old.shape[0] < a.shape[0] and (np.abs(back - old).max(axis=2) > 8).mean() < 0.01:
        return False
    small = [np.asarray(Image.fromarray(x.astype(np.uint8), "RGBA").resize((164, 104), Image.LANCZOS), int)
             for x in (old, a)]
    return (np.abs(small[0] - small[1]).max(axis=2) > 40).mean() > 0.005


def main():
    src = Path(sys.argv[1])
    if src.is_dir():  # one PNG per flag
        files = sorted(src.glob("*.png"))
        names = [re.sub(r"^\d+_", "", f.stem) for f in files]
        pixels = lambda k: np.asarray(Image.open(files[k]).convert("RGBA"))
    else:
        subprocess.run([sys.executable, str(Path(__file__).parent / "readpdn.py"), str(src), str(WORK)],
                       check=True, stdout=subprocess.DEVNULL)
        names = (WORK / "layers.txt").read_text().splitlines()
        pixels = lambda k: np.load(WORK / f"layer{k}.npy")
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
        raw = pixels(k)
        a = opaque(raw)
        im = Image.fromarray(a, "RGBA")
        out = FLAGS / f"{tag}.png"
        if out.exists() and not changed(out, a):
            print(f"  {nm!r} -> {out}: unchanged")
            continue
        im.save(out)
        clear = int((raw[..., 3] < 255).sum())
        print(f"  {nm!r} -> {out}: written" + (f" ({clear} see-through pixels filled)" if clear else ""))


if __name__ == "__main__":
    main()
