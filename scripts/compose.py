"""Compose the game-resolution world from the placed continent blocks.

Output (work/world.npz):
    kind  uint8  0 = ocean, 1 = land, 2 = lake
    cont  uint8  continent index (1..7, see CONTINENTS), 0 on water

Cleanup, all with 4-connectivity because HOI4 provinces must be 4-connected:
  * islands smaller than MIN_PROVINCE pixels are dropped (they cannot hold a province);
  * water bodies not connected to the world ocean become lakes; ponds smaller than
    MIN_LAKE are filled in as land.
"""
import json

import numpy as np
from scipy import ndimage as ndi

from common import MAP_W, MAP_H, SCALE, MIN_PROVINCE, MIN_LAKE, CONTINENTS

N4 = ndi.generate_binary_structure(2, 1)


def label_wrap(mask):
    """4-connected labels of mask, joining components across the x seam."""
    lab, n = ndi.label(mask, structure=N4)
    parent = np.arange(n + 1)

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    left, right = lab[:, 0], lab[:, -1]
    for a, b in zip(left[(left > 0) & (right > 0)], right[(left > 0) & (right > 0)]):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)
    roots = np.array([find(i) for i in range(n + 1)])
    _, dense = np.unique(roots, return_inverse=True)
    return dense.reshape(-1)[lab], dense.max()


def west_split():
    """Quarter-source-res map saying, for every pixel, whether Nonscio's or Araseos'
    main landmass is nearer. Islands of the WEST block follow the nearer one."""
    lab = np.load("work/lab_q.npy")
    seeds = json.load(open("work/seeds.json"))
    nonscio = np.isin(lab, [lab[y // 4, x // 4] for x, y in seeds["nonscio"]])
    araseos = np.isin(lab, [lab[y // 4, x // 4] for x, y in seeds["araseos"]])
    dn = ndi.distance_transform_edt(~nonscio)
    da = ndi.distance_transform_edt(~araseos)
    return np.where(dn <= da, CONTINENTS.index("nonscio") + 1, CONTINENTS.index("araseos") + 1)


def despeckle(cont):
    """The Nonscio/Araseos split is sampled per pixel, so its boundary leaves specks of
    one continent inside the other. Hand any such speck (a 4-connected patch under
    SPECK px that touches the other continent) to the continent around it."""
    SPECK = 4096
    for _ in range(3):
        changed = 0
        for k in (1, 2):
            other = 3 - k
            lab, n = ndi.label(cont == k, structure=N4)
            if n == 0:
                continue
            size = np.bincount(lab.ravel(), minlength=n + 1)
            near_other = ndi.binary_dilation(cont == other, structure=N4)
            touching = np.bincount(lab[near_other & (lab > 0)], minlength=n + 1) > 0
            bad = (size < SPECK) & touching
            bad[0] = False
            m = bad[lab]
            cont[m] = other
            changed += int(m.sum())
        if not changed:
            break


def main():
    cont = from_blocks()
    land = cont > 0
    despeckle(cont)
    finish(cont, land)


def from_blocks():
    """Original mode: continent blocks from the author's .pdn, placed by layout.py."""
    lay = json.load(open("work/layout.json"))
    cont = np.zeros((MAP_H, MAP_W), np.uint8)
    split = west_split()
    block_cont = {"AISLADA": "aislada", "SOLITAS": "solitas", "YASTREOVAKIA": "yastreovakia",
                  "USNISTAN": "usnistan", "ORIENTALIS": "orientalis"}
    for i, b in enumerate(lay["blocks"]):
        m = np.load(f"work/blocks/{i}.npy")
        ox, oy = b["offset"]
        ys, xs = np.nonzero(m)
        Y, X = ys + oy, (xs + ox) % MAP_W
        if b["name"] == "WEST":
            sx0, sy0 = b["src_bbox"][:2]
            qy = np.clip(((ys + 0.5) / SCALE + sy0) // 4, 0, split.shape[0] - 1).astype(int)
            qx = np.clip(((xs + 0.5) / SCALE + sx0) // 4, 0, split.shape[1] - 1).astype(int)
            cont[Y, X] = split[qy, qx]
        else:
            cont[Y, X] = CONTINENTS.index(block_cont[b["name"]]) + 1
    return cont


def finish(cont, land):
    # drop islands too small to be a province
    lab, n = label_wrap(land)
    sizes = np.bincount(lab.ravel(), minlength=n + 1)
    small = (sizes < MIN_PROVINCE) & (np.arange(n + 1) > 0)
    dropped = int(small.sum())
    land &= ~small[lab]

    # water: the world ocean is the largest water body; the rest are lakes or ponds
    wlab, wn = label_wrap(~land)
    wsizes = np.bincount(wlab.ravel(), minlength=wn + 1)
    wsizes[0] = 0
    ocean_id = int(np.argmax(wsizes))
    pond = (wsizes < MIN_LAKE) & (np.arange(wn + 1) > 0)
    pond[ocean_id] = False
    filled = int(pond.sum())
    land |= pond[wlab]
    kind = np.where(land, 1, np.where(wlab == ocean_id, 0, 2)).astype(np.uint8)

    # centre exactly on the final land (layout.py centres on a coarse grid, before
    # specks are dropped); export_canvas.py applies the same shift
    rows = np.nonzero(land.any(axis=1))[0]
    cols = np.nonzero(land.any(axis=0))[0]
    dy = ((MAP_H - 1 - rows[-1]) - rows[0]) // 2
    dx = ((MAP_W - 1 - cols[-1]) - cols[0]) // 2
    kind, cont, land = (np.roll(a, (dy, dx), axis=(0, 1)) for a in (kind, cont, land))

    # a province may not cross the wrap seam, so no land in the first or last column
    if land[:, 0].any() or land[:, -1].any():
        rows = np.nonzero(land[:, 0] | land[:, -1])[0]
        raise SystemExit(f"land touches the left/right map edge (rows {rows.min()}-{rows.max()}); "
                         "leave the first and last pixel columns as water")

    # continent id for pond pixels that were filled: take the nearest land pixel's
    need = land & (cont == 0)
    if need.any():
        idx = ndi.distance_transform_edt(cont == 0, return_distances=False, return_indices=True)
        cont[need] = cont[idx[0][need], idx[1][need]]
    cont[~land] = 0
    lakes = kind == 2
    llab, ln = ndi.label(lakes, structure=N4)
    print(f"land {land.sum()} px ({land.mean():.1%}), ocean {(kind == 0).sum()} px, "
          f"{ln} lakes ({lakes.sum()} px); dropped {dropped} specks, filled {filled} ponds")
    for k, name in enumerate(CONTINENTS, 1):
        print(f"  {name:>13}: {(cont == k).sum():>8} px")
    np.savez_compressed("work/world.npz", kind=kind, cont=cont, shift=(dy, dx))


if __name__ == "__main__":
    main()
