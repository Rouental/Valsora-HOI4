"""Place the continents on the game canvas: scale each one up, then push them apart.

Each continent block (a continent plus the islands assigned to it) is moved rigidly:
one uniform scale for every block, then a translation. Start positions spread the
source layout over the whole canvas (x keeps the source's wrap-around proportions,
y stretches into the room Antarctica left). Then every pair of blocks closer than
MIN_GAP output pixels is pushed apart along the line between their nearest
coastlines until all gaps clear MIN_GAP. The map wraps horizontally, so gaps are
measured across the seam too, and the seam itself is a wall no continent may
straddle (HOI4 rejects a province that crosses it).

Reads work/block_full.npy (source-resolution block ids, -1 = water).
Writes work/blocks/<i>.npy (each block's land at output scale), work/layout.json
(scale, canvas, per-block source bbox and output offset) and a preview PNG.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.morphology import skeletonize

from common import BLOCKS, MAP_W, MAP_H, SCALE, MIN_GAP, MARGIN_Y, SEAM_MARGIN

SRC_W = 14000
F = 4  # optimise at quarter output resolution


def channels(land, w, h):
    """Output pixels that must stay water so separate islands stay separate.

    Shrinking by area fills in straits narrower than ~1.5 output px and fuses the
    islands either side. So the centre line of the water is traced at source
    resolution, and an output pixel on it is kept as water when the land around it
    belongs to two different source landmasses. Centre-line spurs that only run into
    a single coastline are ignored. The kept line is made 4-connected, so a strait
    stays continuous for provinces and ships."""
    lab, _ = ndi.label(land, structure=np.ones((3, 3)))
    sy, sx = land.shape
    yc = np.minimum(((np.arange(h) + 0.5) * sy / h).astype(int), sy - 1)
    xc = np.minimum(((np.arange(w) + 0.5) * sx / w).astype(int), sx - 1)
    # landmass under each output pixel (sampled at its centre; gaps take a neighbour's)
    owner = lab[yc][:, xc]
    owner = np.where(owner > 0, owner, ndi.maximum_filter(owner, size=3))
    sk = skeletonize(~land)
    ys, xs = np.nonzero(sk)
    line = np.zeros((h, w), bool)
    line[np.minimum(ys * h // sy, h - 1), np.minimum(xs * w // sx, w - 1)] = True
    hi = ndi.maximum_filter(owner, size=3)
    lo = -ndi.maximum_filter(np.where(owner > 0, -owner, -np.iinfo(owner.dtype).max), size=3)
    out = line & (hi != lo) & (lo > 0)
    # a diagonal-only step would let land touch across it; fill the corner
    diag = out[:-1, :-1] & out[1:, 1:] & ~out[:-1, 1:] & ~out[1:, :-1]
    anti = out[:-1, 1:] & out[1:, :-1] & ~out[:-1, :-1] & ~out[1:, 1:]
    out[:-1, 1:] |= diag
    out[:-1, :-1] |= anti
    return out


def scale_blocks(blk):
    """Scale each block's land mask to output resolution (area-weighted, >=50%)."""
    Path("work/blocks").mkdir(exist_ok=True)
    meta = []
    for i, _ in enumerate(BLOCKS):
        m = blk == i
        rows = np.nonzero(m.any(axis=1))[0]
        cols = np.nonzero(m.any(axis=0))[0]
        y0, y1, x0, x1 = int(rows[0]), int(rows[-1]) + 1, int(cols[0]), int(cols[-1]) + 1
        crop = m[y0:y1, x0:x1]
        cy, cx = ndi.center_of_mass(crop)
        w = round((x1 - x0) * SCALE)
        h = round((y1 - y0) * SCALE)
        small = np.asarray(Image.fromarray(crop.astype(np.float32)).resize((w, h), Image.BOX))
        np.save(f"work/blocks/{i}.npy", (small >= 0.5) & ~channels(crop, w, h))
        meta.append(dict(src_bbox=[x0, y0, x1, y1], src_centroid=[cx + x0, cy + y0]))
    return meta


def shrink(mask):
    h, w = mask.shape
    h2, w2 = -(-h // F), -(-w // F)
    pad = np.zeros((h2 * F, w2 * F), bool)
    pad[:h, :w] = mask
    return pad.reshape(h2, F, w2, F).any(axis=(1, 3))


def render(masks, pos, W, H):
    can = np.full((H, W), -1, np.int16)
    for i, m in enumerate(masks):
        oy, ox = int(round(pos[i][1])), int(round(pos[i][0]))
        ys, xs = np.nonzero(m)
        can[np.clip(ys + oy, 0, H - 1), (xs + ox) % W] = i
    return can


def gaps(masks, pos, W, H, reach):
    """Pairwise min distance and unit direction from block i's nearest point to j's.
    Distances are exact up to `reach` pixels; the seam is handled by padding."""
    can = render(masks, pos, W, H)
    padded = np.concatenate([can[:, -reach:], can, can[:, :reach]], axis=1)
    res = {}
    for i in range(len(masks)):
        d, (iy, ix) = ndi.distance_transform_edt(padded != i, return_indices=True)
        d = d[:, reach:reach + W]
        iy = iy[:, reach:reach + W]
        ix = ix[:, reach:reach + W] - reach
        for j in range(i + 1, len(masks)):
            dj = np.where(can == j, d, np.inf)
            k = int(np.argmin(dj))
            y, x = divmod(k, W)
            g = float(dj[y, x])
            vy, vx = y - iy[y, x], x - ix[y, x]
            nrm = float(np.hypot(vy, vx)) or 1.0
            res[(i, j)] = (g, vx / nrm, vy / nrm)
    return res


def main():
    blk = np.load("work/block_full.npy")
    meta = scale_blocks(blk)
    del blk
    full = [np.load(f"work/blocks/{i}.npy") for i in range(len(BLOCKS))]
    masks = [shrink(m) for m in full]
    W, H = MAP_W // F, MAP_H // F
    ytop = min(m["src_bbox"][1] for m in meta)
    ybot = max(m["src_bbox"][3] for m in meta)
    my = MARGIN_Y / F
    pos = []
    for m, b in zip(meta, masks):
        x0, y0 = m["src_bbox"][:2]
        cx, cy = m["src_centroid"]
        tx = cx * W / SRC_W
        ty = my + (cy - ytop) * (H - 2 * my) / (ybot - ytop)
        pos.append([tx - (cx - x0) * SCALE / F, ty - (cy - y0) * SCALE / F])
    pos = np.array(pos)
    start = pos.copy()
    gmin = MIN_GAP / F
    reach = int(gmin * 3)
    for it in range(600):
        g = gaps(masks, pos, W, H, reach)
        worst = min(v[0] for v in g.values())
        moved = False
        for (i, j), (d, ux, uy) in g.items():
            if d < gmin + 0.5:
                push = (gmin + 0.5 - d) / 2 + 0.25
                pos[j] += (ux * push, uy * push)
                pos[i] -= (ux * push, uy * push)
                moved = True
        # weak pull toward the start keeps the arrangement recognisable; it fades out
        # so the pushes can settle
        pos += 0.01 * max(0.0, 1 - it / 150) * (start - pos)
        for i, b in enumerate(masks):
            pos[i][1] = min(max(pos[i][1], my), H - my - b.shape[0])
        if it % 10 == 0:
            print(f"iter {it}: min gap {worst * F:.0f}px")
        # the wrap seam (x = 0) is a fixed wall no block may straddle
        can = render(masks, pos, W, H)
        wall = SEAM_MARGIN / F
        for i in range(len(masks)):
            xs = np.nonzero((can == i).any(axis=0))[0]
            d = np.minimum(xs, W - 1 - xs).min()
            if d < wall + 0.5:
                centre = (pos[i][0] + masks[i].shape[1] / 2) % W
                pos[i][0] += (wall + 0.5 - d) * (1 if centre < W / 2 else -1)
                moved = True
        if not moved:
            print(f"converged after {it} iterations")
            break
    # centre the land: equal empty bands top and bottom, and equal ocean either side
    # of the wrap seam (whole-map shifts keep every gap)
    can = render(masks, pos, W, H)
    rows = np.nonzero((can >= 0).any(axis=1))[0]
    cols = np.nonzero((can >= 0).any(axis=0))[0]
    pos[:, 1] += ((H - 1 - rows[-1]) - rows[0]) / 2
    pos[:, 0] += ((W - 1 - cols[-1]) - cols[0]) / 2
    # report at full output resolution
    posf = pos * F
    g = gaps(full, posf, MAP_W, MAP_H, int(MIN_GAP * 3))
    for (i, j), (d, _, _) in sorted(g.items(), key=lambda kv: kv[1][0]):
        print(f"  {BLOCKS[i]:>13} - {BLOCKS[j]:<13} {d:6.0f}px")
    can = render(full, [[round(p[0]), round(p[1])] for p in posf], MAP_W, MAP_H)
    xs = np.nonzero((can >= 0).any(axis=0))[0]
    print(f"  land keeps {min(xs.min(), MAP_W - 1 - xs.max())}px from the wrap seam")
    out = dict(scale=SCALE, map_w=MAP_W, map_h=MAP_H, blocks=[])
    for i, m in enumerate(meta):
        out["blocks"].append(dict(name=BLOCKS[i], offset=[round(posf[i][0]), round(posf[i][1])],
                                  shape=list(full[i].shape), **m))
    Path("work/layout.json").write_text(json.dumps(out, indent=1))
    can = render(full, [[round(p[0]), round(p[1])] for p in posf], MAP_W, MAP_H)
    pal = np.array([[230, 80, 80], [80, 200, 80], [230, 120, 230], [90, 200, 160],
                    [200, 190, 110], [240, 170, 70]], np.uint8)
    img = np.full((MAP_H, MAP_W, 3), (25, 35, 70), np.uint8)
    img[can >= 0] = pal[can[can >= 0]]
    Image.fromarray(img).resize((MAP_W // 4, MAP_H // 4), Image.BOX).save("work/layout_preview.png")


if __name__ == "__main__":
    main()
