"""Organic splitting: cut an area into pieces with natural, wandering borders.

Each piece grows from a seed by a compact watershed over fractal noise: borders follow
the noise's valleys, so they wander, while compactness keeps pieces roughly round and
even. The strength (compactness 0.2 / spacing, noise at 0.6 / 0.25 / 0.09 of the
spacing) is the one the author approved from the preview on 2026-09-29.
"""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.segmentation import watershed

COMPACTNESS = 0.2   # divided by the piece spacing
NOISE = (0.6, 0.25, 0.09)  # noise feature sizes, as fractions of the piece spacing


def fractal_noise(shape, scales, seed):
    r = np.random.default_rng(seed)
    total = np.zeros(shape, np.float32)
    for k, s in enumerate(scales):
        f = max(1, int(s // 4))  # big features are made at reduced resolution
        small = r.standard_normal((shape[0] // f + 2, shape[1] // f + 2)).astype(np.float32)
        small = ndi.gaussian_filter(small, s / f, mode="wrap")
        big = np.asarray(Image.fromarray(small).resize((small.shape[1] * f, small.shape[0] * f),
                                                       Image.BICUBIC))[:shape[0], :shape[1]]
        total += big / (big.std() + 1e-9) * (0.55 ** k)
    total -= total.min()
    return total / (total.max() + 1e-9)


def _connected(lab, mask):
    """Detached bits of a piece join the piece they touch most."""
    for _ in range(5):
        changed = False
        for i, sl in enumerate(ndi.find_objects(lab), 1):
            if sl is None:
                continue
            comp, n = ndi.label(lab[sl] == i)
            if n <= 1:
                continue
            keep = np.bincount(comp.ravel())[1:].argmax() + 1
            for k in range(1, n + 1):
                if k == keep:
                    continue
                piece = np.zeros(lab.shape, bool)
                piece[sl] = comp == k
                ring = ndi.binary_dilation(piece) & ~piece & mask & (lab != i) & (lab > 0)
                if ring.any():
                    v, c = np.unique(lab[ring], return_counts=True)
                    lab[piece] = v[c.argmax()]
                    changed = True
        if not changed:
            break
    return lab


def split(ys, xs, seeds, seed=0):
    """Organic pieces of the area (ys, xs) grown from `seeds` [(y, x), ...].
    Returns a piece number (0-based) per pixel; every piece is 4-connected."""
    k = len(seeds)
    if k <= 1:
        return np.zeros(len(ys), int)
    y0, x0 = ys.min(), xs.min()
    h, w = ys.max() - y0 + 1, xs.max() - x0 + 1
    mask = np.zeros((h, w), bool)
    mask[ys - y0, xs - x0] = True
    spacing = np.sqrt(len(ys) / k / 0.866)
    noise = fractal_noise((h, w), [max(1.5, f * spacing) for f in NOISE], seed)
    markers = np.zeros((h, w), np.int32)
    for j, (sy, sx) in enumerate(seeds, 1):
        markers[sy - y0, sx - x0] = j
    lab = watershed(noise, markers, mask=mask, compactness=COMPACTNESS / spacing)
    miss = mask & (lab == 0)  # bits the flood could not reach
    if miss.any():
        idx = ndi.distance_transform_edt(lab == 0, return_distances=False, return_indices=True)
        lab[miss] = lab[idx[0][miss], idx[1][miss]]
    lab = _connected(lab, mask)
    return lab[ys - y0, xs - x0] - 1
