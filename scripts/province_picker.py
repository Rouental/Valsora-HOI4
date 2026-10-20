"""Rouental's provinces for the author to group (2026-10-20, the author: "Give me a map of Rouental where I can select
the various provinces and group them together. I want to combine some of them together").

    python3 scripts/province_picker.py [TAG]      # after a build; writes work/province_picker/<TAG>.html

The page (the template scripts/province_picker.html, filled with the build's data) is published as a private claude.ai
artifact with a database: the author picks provinces on the map, makes groups of them (to merge into one province, or
to make into one state) and the groups are saved in its `groups` collection, one document a group, each province named
by a pixel inside it ("x,y", as everywhere: ids shift when the map is cut again) and its id in the build it was picked
on. Reading them back is ArtifactData's job; merge_provinces.py and pdn_tools.py do the merging.

The map is the nation's box on the game map, a pixel a game pixel, its far islands and territories in boxes of their own
in a row under it: a PNG whose red and green give each pixel's province (its place in the page's list, from 1; 65535
another country's land, 65534 water, 0 between the boxes) and whose blue is 1 on a river. The page draws it larger, the
states' borders thick, the provinces' thin.
"""
import base64
import io
import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import atlas_export as AE  # noqa: E402  (chdirs to the repository's root)
from facts_export import read_loc, read_states  # noqa: E402

MARGIN = 10
NEAR = 80                  # a piece of the nation this near the main one is drawn in the main box
INSET_GAP = 14             # px between the boxes of the far pieces, and under the main box
OTHER, WATER = 65535, 65534


def main(tag="ROU"):
    p = np.load("work/provinces.npz")
    prov, kind, terrain = p["prov"], p["kind"], p["terrain"]
    reg = np.load("work/regions.npz")
    anchor, state_of, size = reg["anchor"], reg["state_of"], reg["size"]
    rj = json.load(open("work/regions.json", encoding="utf-8"))
    states, owners = rj["states"], rj["owners"]
    hist = AE.built_states()
    owner = [hist[s]["owner"] if s in hist else owners[s] for s in range(len(states))]
    L = AE.english()
    built = read_states()
    vp_names = read_loc(AE.MOD / "localisation/english/replace/valsora_victory_points_l_english.yml", "VICTORY_POINTS_")
    rivers = np.load("work/world.npz")["rivers"]

    mine = sorted(int(q) for s, g in enumerate(states) if owner[s] == tag for q in g)
    if not mine:
        raise SystemExit(f"no province of {tag} in the build")
    local = {q: i + 1 for i, q in enumerate(mine)}
    lut = np.full(int(prov.max()) + 2, OTHER, np.int32)
    for q, i in local.items():
        lut[q] = i
    parts = pieces(np.isin(prov, mine))
    # the map: the main part's box, the far ones in boxes of their own in a row under it (INSET_GAP apart)
    tiles, x, y_row = [], 0, parts[0][3] - parts[0][1] + INSET_GAP
    for k, (x0, y0, x1, y1) in enumerate(parts):
        if k == 0:
            tiles.append((x0, y0, x1, y1, 0, 0))
        else:
            tiles.append((x0, y0, x1, y1, x, y_row))
            x += x1 - x0 + INSET_GAP
    w = max(parts[0][2] - parts[0][0], x - INSET_GAP if x else 0)
    h = y_row - INSET_GAP + (max(y1 - y0 for x0, y0, x1, y1 in parts[1:]) + INSET_GAP if len(parts) > 1 else 0)
    idx = np.zeros((h, w), np.int32)
    river = np.zeros((h, w), bool)
    for x0, y0, x1, y1, dx, dy in tiles:
        box = prov[y0:y1, x0:x1]
        b = np.where(box >= 0, lut[np.maximum(box, 0)], 0)
        b[(box >= 0) & (kind[np.maximum(box, 0)] != 1) & (b == OTHER)] = WATER
        idx[dy:dy + y1 - y0, dx:dx + x1 - x0] = b
        river[dy:dy + y1 - y0, dx:dx + x1 - x0] = (rivers[y0:y1, x0:x1] < 254) & (b > 0) & (b < WATER)
    img = np.dstack([(idx >> 8) & 255, idx & 255, river.astype(np.int32)]).astype(np.uint8)
    buf = io.BytesIO()
    Image.fromarray(img, "RGB").save(buf, "PNG", optimize=True)

    def shown(ax, ay):
        for x0, y0, x1, y1, dx, dy in tiles:
            if x0 <= ax < x1 and y0 <= ay < y1:
                return ax - x0 + dx, ay - y0 + dy
        return None

    # the states and their victory points
    vp_of = {}
    for sid, d in built.items():
        for q, v in d["vp"]:
            vp_of[q - 1] = (vp_names.get(q, ""), v)
    st = sorted({int(state_of[q]) for q in mine})
    st_index = {s: i for i, s in enumerate(st)}
    state_list = [dict(id=s + 1, name=L.get(f"VAL_STATE_{s + 1}", f"State {s + 1}"), n=len(states[s])) for s in st]
    provs = []
    for q in mine:
        ay, ax = int(anchor[q][0]), int(anchor[q][1])
        name, value = vp_of.get(q, ("", 0))
        sx, sy = shown(ax, ay)
        provs.append(dict(id=q + 1, key=f"{ax},{ay}", s=st_index[int(state_of[q])], px=int(size[q]),
                          t=str(terrain[q]), vp=name, v=value, dx=int(sx), dy=int(sy)))
    insets = [dict(x=int(dx), y=int(dy), w=int(x1 - x0), h=int(y1 - y0), at=f"{x0},{y0}")
              for x0, y0, x1, y1, dx, dy in tiles[1:]]
    data = dict(tag=tag, name=L.get(tag, tag), size=[int(w), int(h)], insets=insets,
                built=AE.built_at(), states=state_list, provinces=provs,
                map="data:image/png;base64," + base64.b64encode(buf.getvalue()).decode())
    page = (ROOT / "scripts/province_picker.html").read_text(encoding="utf-8")
    out = ROOT / "work/province_picker" / f"{tag}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page.replace("/*DATA*/null", json.dumps(data, ensure_ascii=False, separators=(",", ":"))),
                   encoding="utf-8")
    print(f"wrote {out}: {len(provs)} provinces in {len(st)} states, a {w} x {h} px map ({len(insets)} insets), "
          f"{out.stat().st_size / 1e3:.0f} kB")


def pieces(m):
    """the nation's land in boxes (x0, y0, x1, y1), margins included: the largest piece's box first, grown to take the
    pieces near it (within NEAR px), then each far piece's own"""
    lab, n = ndi.label(m, structure=np.ones((3, 3)))
    boxes = ndi.find_objects(lab)
    sizes = ndi.sum(m, lab, range(1, n + 1))
    order = sorted(range(n), key=lambda i: -sizes[i])
    bb = lambda s: [s[1].start, s[0].start, s[1].stop, s[0].stop]  # noqa: E731
    main, far = bb(boxes[order[0]]), []
    changed = True
    rest = [bb(boxes[i]) for i in order[1:]]
    while changed:
        changed = False
        for b in list(rest):
            if b[0] < main[2] + NEAR and b[2] > main[0] - NEAR and b[1] < main[3] + NEAR and b[3] > main[1] - NEAR:
                main = [min(main[0], b[0]), min(main[1], b[1]), max(main[2], b[2]), max(main[3], b[3])]
                rest.remove(b)
                changed = True
    # far pieces near each other share a box
    for b in rest:
        for f in far:
            if b[0] < f[2] + NEAR and b[2] > f[0] - NEAR and b[1] < f[3] + NEAR and b[3] > f[1] - NEAR:
                f[:] = [min(f[0], b[0]), min(f[1], b[1]), max(f[2], b[2]), max(f[3], b[3])]
                break
        else:
            far.append(list(b))
    H_, W_ = m.shape
    grow = lambda b: (max(0, b[0] - MARGIN), max(0, b[1] - MARGIN), min(W_, b[2] + MARGIN), min(H_, b[3] + MARGIN))  # noqa: E731
    return [grow(main)] + [grow(f) for f in sorted(far)]


if __name__ == "__main__":
    main(*sys.argv[1:])
