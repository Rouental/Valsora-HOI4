"""Split the source land into continent blocks and remove Antarctica.

Land is layer 1 ("Land & Borders & Colours") of the .pdn: any opaque pixel. Each
block is one continent plus the islands that go with it; blocks are later scaled
and moved rigidly. Cores are the big landmasses, named by a seed pixel (x, y) in
source coordinates; every other island joins the nearest core. Nonscio and Araseos
form one block because the Aikos / Midtierre archipelago interlocks them.

Antarctica is the landmass touching the bottom edge. Islets hugging its coast
(within ANTARCTIC_HUG px) go with it; islands further out are real land and stay.

Writes work/lab_q.npy (quarter-res landmass labels), work/block_full.npy (source-res
block id per pixel, -1 = water or removed) and work/seeds.json.
"""
import json

import numpy as np
from scipy import ndimage as ndi

from common import BLOCKS

F = 4  # landmasses are grouped at quarter resolution
ANTARCTIC_HUG = 5

# seed pixels (source x, y) inside each block's core landmasses
CORES = {
    "WEST": [(3598, 1910), (1486, 1426), (3010, 5170)],  # Nonscio, Marmuk coast, Araseos
    "AISLADA": [(5234, 3314)],
    "SOLITAS": [(5194, 4258), (7126, 4386), (6070, 4326), (6358, 3942)],
    "YASTREOVAKIA": [(7450, 914)],
    "USNISTAN": [(8698, 4558)],
    "ORIENTALIS": [(12466, 3342), (10498, 4502), (11270, 5306)],  # mainland, Felteren, south
}
# islands the author's continents map puts somewhere other than their nearest core
OVERRIDES = {(9574, 3082): "ORIENTALIS"}
# for splitting the WEST block into two continents later
NONSCIO = [(3598, 1910), (1486, 1426)]
ARASEOS = [(3010, 5170)]


def main():
    layer = np.load("work/pdn/layer1.npy", mmap_mode="r")
    H, W = layer.shape[:2]
    land = np.empty((H, W), bool)
    for y0 in range(0, H, 500):
        land[y0:y0 + 500] = np.asarray(layer[y0:y0 + 500, :, 3]) > 0

    # quarter-res landmasses (8-connected, majority land)
    lq = land.reshape(H // F, F, W // F, F).mean(axis=(1, 3)) >= 0.5
    lab, n = ndi.label(lq, structure=np.ones((3, 3)))
    np.save("work/lab_q.npy", lab)
    Hq, Wq = lab.shape
    bottom = set(np.unique(lab[-1])) - {0}
    antarctica_q = max(bottom, key=lambda k: (lab == k).sum())

    def comp_at(x, y):
        k = lab[y // F, x // F]
        assert k > 0, f"seed ({x}, {y}) is not on land"
        return k

    assign = np.full(n + 1, -1)
    for b, seeds in CORES.items():
        for x, y in seeds:
            assign[comp_at(x, y)] = BLOCKS.index(b)
    # every other landmass joins the nearest core (distance wraps across the seam)
    dist = []
    for b in range(len(BLOCKS)):
        m = np.isin(lab, np.nonzero(assign == b)[0])
        t = np.concatenate([m, m, m], axis=1)
        dist.append(ndi.distance_transform_edt(~t)[:, Wq:2 * Wq])
    for k, sl in enumerate(ndi.find_objects(lab), 1):
        if assign[k] >= 0 or k == antarctica_q:
            continue
        sub = lab[sl] == k
        assign[k] = int(np.argmin([d[sl][sub].min() for d in dist]))
    for (x, y), b in OVERRIDES.items():
        assign[comp_at(x, y)] = BLOCKS.index(b)

    # carry the grouping to every full-res landmass (majority of its quarter pixels)
    bq = np.where(lab > 0, assign[lab], -1)
    bq[lab == antarctica_q] = -2
    valid = bq >= 0
    t = np.concatenate([valid, valid, valid], axis=1)
    _, (iy, ix) = ndi.distance_transform_edt(~t, return_indices=True)
    nearest = bq[iy[:, Wq:2 * Wq], ix[:, Wq:2 * Wq] % Wq]
    labf, nf = ndi.label(land, structure=np.ones((3, 3)))
    blk_of = np.full(nf + 1, -1, np.int8)
    ant = np.zeros(nf + 1, bool)
    for k, sl in enumerate(ndi.find_objects(labf), 1):
        ys, xs = np.nonzero(labf[sl] == k)
        qy = np.minimum((ys + sl[0].start) // F, Hq - 1)
        qx = np.minimum((xs + sl[1].start) // F, Wq - 1)
        if (bq[qy, qx] == -2).mean() > 0.5:
            ant[k] = True
            continue
        v = nearest[qy, qx]
        blk_of[k] = np.bincount(v[v >= 0], minlength=len(BLOCKS)).argmax()
    # Antarctica proper touches the bottom edge; islets hugging it go too, islands
    # further out join the nearest block
    main_ant = max((k for k in np.unique(labf[-1]) if k and ant[k]),
                   key=lambda k: (labf == k).sum())
    d_ant = ndi.distance_transform_edt(labf != main_ant)
    blk = np.where(labf > 0, blk_of[labf], -1).astype(np.int8)
    kept = 0
    for k in np.nonzero(ant)[0]:
        m = labf == k
        if k == main_ant or d_ant[m].min() <= ANTARCTIC_HUG:
            blk[m] = -1
            continue
        ys, xs = np.nonzero(m)
        cy, cx = int(ys.mean()), int(xs.mean())
        win = blk[max(0, cy - 1500):cy + 1500, max(0, cx - 1500):cx + 1500]
        wy, wx = np.nonzero(win >= 0)
        j = np.argmin((wy + max(0, cy - 1500) - cy) ** 2 + (wx + max(0, cx - 1500) - cx) ** 2)
        blk[m] = win[wy[j], wx[j]]
        kept += 1
    np.save("work/block_full.npy", blk)
    json.dump(dict(nonscio=NONSCIO, araseos=ARASEOS), open("work/seeds.json", "w"))
    print(f"removed Antarctica ({int((labf == main_ant).sum())} px), kept {kept} islands near it")
    for b, name in enumerate(BLOCKS):
        print(f"  {name:>13}: {int((blk == b).sum())} px")


if __name__ == "__main__":
    main()
