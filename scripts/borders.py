"""HOI4's province border count, and its limit.

HOI4 draws at most 65,536 province borders: past that an integer overflows and the
rest are not drawn (HOI4 wiki, Map modding, "usually hit at about 21000 provinces").
A border is a stretch of boundary two touching provinces share, land or water alike,
and a pair that touches in several separate places has a border for each. They are
made in province id order, which is reading order here (ids follow each province's
first pixel, row by row), so a map over the limit loses its province and state lines
from some row down: 2026-10-12, 73,231 borders, none drawn south of row ~1995.

    python3 scripts/borders.py      # the count for the last build (work/provinces.npz)
"""
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

LIMIT = 65536


def count(prov):
    """(touching pairs, borders) for a map of province numbers; the map wraps left to
    right, as HOI4's does."""
    H, W = prov.shape
    prov = prov.astype(np.int64)
    right = np.roll(prov, -1, axis=1)
    vy, vx = np.nonzero(prov != right)                 # edge between (y, x) and (y, x + 1)
    hy, hx = np.nonzero(prov[:-1] != prov[1:])         # edge between (y, x) and (y + 1, x)
    a = np.r_[prov[vy, vx], prov[hy, hx]]
    b = np.r_[right[vy, vx], prov[hy + 1, hx]]
    pairs, pid = np.unique(np.minimum(a, b) * (1 << 24) + np.maximum(a, b), return_inverse=True)
    # each edge joins two corners of the pixel grid (H + 1 rows of W corners, wrapping);
    # a border is a connected run of one pair's edges
    c1 = np.r_[vy * W + (vx + 1) % W, (hy + 1) * W + hx]
    c2 = np.r_[(vy + 1) * W + (vx + 1) % W, (hy + 1) * W + (hx + 1) % W]
    span = (H + 1) * W
    nodes, inv = np.unique(np.r_[pid * span + c1, pid * span + c2], return_inverse=True)
    m = len(c1)
    g = coo_matrix((np.ones(m, np.int8), (inv[:m], inv[m:])), shape=(len(nodes), len(nodes)))
    return len(pairs), int(connected_components(g, directed=False)[0])


if __name__ == "__main__":
    n_pairs, n_borders = count(np.load("work/provinces.npz")["prov"])
    print(f"{n_borders} province borders ({n_pairs} touching pairs); HOI4 draws at most {LIMIT}")
