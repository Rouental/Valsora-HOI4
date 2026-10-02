"""A numbered map of the states of some countries, for the author to name them (by hand).

Each state gets a number printed at its most inland point. The numbers are tied to
that pixel in dist/state_numbers_<name>.json (number -> tag, x, y, current state id),
so names given by number can be stored by pixel, which survives rebuilds, unlike ids.
Run after a build:

    python3 scripts/state_map.py reibonnaise ROU SGN EVR HLR SGV LST LZC GDN
    python3 scripts/state_map.py --names rouental ROU   # the names from source/state_names.json
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi

from common import COUNTRIES

SCALE = 5
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def main():
    args = sys.argv[1:]
    show_names = "--names" in args
    args = [a for a in args if a != "--names"]
    name, tags = args[0], args[1:]
    scale = 7 if show_names else SCALE
    p = np.load("work/provinces.npz")
    prov, kind = p["prov"], p["kind"]
    # states and owners as the game sees them (province id = index + 1)
    state_of = np.full(len(kind) + 1, -1)
    owner = {}
    for f in Path("build/valsora_test/history/states").glob("*.txt"):
        t = f.read_text(encoding="utf-8")
        sid = int(re.search(r"\bid = (\d+)", t).group(1))
        owner[sid] = re.search(r"owner = (\w+)", t).group(1)
        ids = np.array(re.search(r"provinces = \{([^}]*)\}", t).group(1).split(), int)
        state_of[ids] = sid
    st = state_of[prov + 1]
    own = np.vectorize(lambda s: owner.get(s, ""), otypes=[object])
    mine = [s for s in owner if owner[s] in tags]
    m = np.isin(st, mine)
    ys, xs = np.nonzero(m)
    # far-off exclaves (Rouental's islets off Solitas) would make the picture huge:
    # the frame holds the homeland, states outside it are listed instead
    near = (np.abs(ys - np.median(ys)) < 400) & (np.abs(xs - np.median(xs)) < 400)
    ys, xs = ys[near], xs[near]
    y0, y1 = max(ys.min() - 15, 0), ys.max() + 16
    x0, x1 = max(xs.min() - 15, 0), xs.max() + 16
    S = st[y0:y1, x0:x1]
    land = kind[prov[y0:y1, x0:x1]] == 1
    O = own(S)

    col = {v[0]: np.array(v[3], float) for v in COUNTRIES.values()}
    img = np.where(land[..., None], 225.0, 0.0) + np.where(land[..., None], 0, np.array([170, 195, 225]))
    for t in tags:
        img[O == t] = col[t] * 0.45 + 255 * 0.55
    img = np.repeat(np.repeat(img, scale, 0), scale, 1)
    Sb = np.repeat(np.repeat(S, scale, 0), scale, 1)
    Ob = np.repeat(np.repeat(O, scale, 0), scale, 1)

    def edges(a):
        e = np.zeros(a.shape, bool)
        e[:, 1:] |= a[:, 1:] != a[:, :-1]
        e[1:] |= a[1:] != a[:-1]
        return e
    img[edges(Sb)] = (70, 70, 70)
    img[ndi.binary_dilation(edges(Ob), iterations=2)] = (20, 20, 20)
    im = Image.fromarray(img.clip(0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    font = ImageFont.truetype(FONT, 18)
    small = ImageFont.truetype(FONT, 14)
    state_names = {}
    if show_names:
        for k, nm in json.loads(Path("source/state_names.json").read_text(encoding="utf-8")).items():
            x, y = map(int, k.split(","))
            state_names[int(st[y, x])] = nm
    key, n = {}, 0
    for t in tags:
        sts = [s for s in mine if owner[s] == t and (S == s).any()]
        pts = {}
        for s in sts:
            sm = S == s
            dist = ndi.distance_transform_edt(np.pad(sm, 1))[1:-1, 1:-1]
            py, px = np.unravel_index(dist.argmax(), dist.shape)
            pts[s] = (int(py), int(px))
        for s in sorted(sts, key=lambda s: (pts[s][0] // 40, pts[s][1])):  # rows, then left to right
            n += 1
            py, px = pts[s]
            key[n] = dict(tag=t, x=int(px + x0), y=int(py + y0), state=s)
            cx, cy = px * scale + scale // 2, py * scale + scale // 2
            if show_names:
                label = state_names.get(s, f"({n}: no name)")
                words = label.split(" ")  # long names on two lines
                if len(label) > 11 and len(words) > 1:
                    half = (len(words) + 1) // 2
                    label = " ".join(words[:half]) + "\n" + " ".join(words[half:])
                d.multiline_text((cx, cy), label, fill=(0, 0, 0), font=small, anchor="mm",
                                 align="center", stroke_width=2, stroke_fill=(255, 255, 255))
            else:
                d.text((cx, cy), str(n), fill=(0, 0, 0), font=font, anchor="mm",
                       stroke_width=3, stroke_fill=(255, 255, 255))
    # legend: country names, bottom left (author)
    lf = ImageFont.truetype(FONT, 22)
    for k, t in enumerate([] if show_names else tags):
        nm = next(v[1] for v in COUNTRIES.values() if v[0] == t)
        nums = [i for i, v in key.items() if v["tag"] == t]
        d.text((10, im.height - 10 - 28 * (len(tags) - k)), f"{nm}: {min(nums)}" + (f"–{max(nums)}" if len(nums) > 1 else ""), fill=tuple(int(c * 0.6) for c in col[t]),
               font=lf, stroke_width=3, stroke_fill=(255, 255, 255))
    Path("dist").mkdir(exist_ok=True)
    if show_names:
        im.save(f"dist/state_names_{name}.png")
    else:
        im.save(f"dist/state_numbers_{name}.png")
        json.dump(key, open(f"dist/state_numbers_{name}.json", "w"), indent=1)
    out = sorted({owner[s] + f" state {s}" for s in mine} - {v["tag"] + f" state {v['state']}" for v in key.values()})
    kind_ = "names" if show_names else "numbers"
    print(f"{n} states: dist/state_{kind_}_{name}.png, {im.size}; outside the frame: {out}")


if __name__ == "__main__":
    main()
