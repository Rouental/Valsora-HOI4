"""Strait crossings: land provinces on two landmasses that face each other across a narrow strait, so armies can walk
across as in the base game (map/adjacencies.csv, type "sea"). 2026-10-17, the author: "Sure, do 1, 3, and 7"; 1 was
"Strait crossings ... You'd get a preview map of them to approve before any go into the mod."

    python3 scripts/straits.py find             after a build: dist/straits_proposed.json and dist/straits_map.png
                                                (the whole map at full size, each crossing ringed in the colour of
                                                its width and numbered); the mod does not change
    python3 scripts/straits.py map --min-gap PX [--out FILE]
                                                the proposal's crossings wider than PX px of sea alone, on today's
                                                build (2026-10-20, the author: "Could you provide a map with just the
                                                red ones?": --min-gap 15, dist/straits_map_red.png)
    python3 scripts/straits.py approve [--max-gap PX] [--drop N,N,...] [--add N,N,...]
                                                the proposal's crossings up to PX px of sea (default DEFAULT_GAP),
                                                less --drop, plus --add (wider ones), into source/straits.json, which
                                                the build reads; then rebuild

The base game's 151 sea crossings span 2 to 30 px of sea: median 4, three quarters under 8.5, nine tenths under 14
(measured on its own map, 2026-10-17). Here the narrowest strait between two landmasses is found along the line where
their coasts' nearest-pixel zones meet over open sea (lakes and other land block it). Every landmass is linked once:
the narrowest straits first, and none that would only link two landmasses already linked through others (a minimum
spanning tree, so approving up to a width keeps exactly the tree's crossings that narrow). Two big landmasses
(BIG px each) facing each other along a long strait get a crossing every SPACING px of it as well. The sea province a
crossing goes through is the one the strait's centre line crosses most, one that touches both coasts' provinces if
there is one.

source/straits.json names each crossing by pixels (a coast pixel on each side and a sea pixel), not by province ids,
which shift whenever provinces change; the build turns them into ids and stops if a pixel no longer lies on land, on
land, and at sea.
"""
import json
import sys
import unicodedata
from math import hypot
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi

PROPOSAL = Path("dist/straits_proposed.json")
APPROVED = Path("source/straits.json")
MAP = Path("dist/straits_map.png")
GMAX = 20          # px of sea: the widest strait proposed
DEFAULT_GAP = 10   # px: what `approve` takes without --max-gap
BIG = 10000        # px: landmasses this big may have more than one crossing between them
SPACING = 150      # px between two crossings of the same pair of big landmasses
TIERS = [(6, (70, 200, 90)), (10, (235, 200, 60)), (15, (240, 140, 50)), (GMAX, (225, 70, 70))]
# countries no crossing may join, whatever the strait's width (author, 2026-10-18: "The strait crossing connecting
# Royalist and Republican Illiricium shouldn't exist"), and countries no crossing may reach at all (the same day:
# "Neither should the crossings to North Pollana"): `approve` leaves them out
NEVER = {frozenset(("ILR", "KIL"))}
NEVER_ANY = {"NPL"}


def ascii(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().replace(";", ",")


def load():
    p = np.load("work/provinces.npz")
    j = json.load(open("work/regions.json"))
    r = np.load("work/regions.npz")
    return p["prov"], p["kind"], r["state_of"], j


def state_names():
    out = {}
    for line in open("build/valsora_test/localisation/english/valsora_l_english.yml", encoding="utf-8-sig"):
        line = line.strip()
        if line.startswith("VAL_STATE_") and ':0 "' in line:
            k, v = line.split(':0 "', 1)
            out[int(k[len("VAL_STATE_"):]) - 1] = v.rstrip('"')
    return out


def segment(ay, ax, by, bx):
    n = int(max(abs(by - ay), abs(bx - ax))) + 1
    t = np.linspace(0, 1, n + 1)
    return np.round(ay + (by - ay) * t).astype(int), np.round(ax + (bx - ax) * t).astype(int)


def find():
    prov, kind, state_of, j = load()
    H, W = prov.shape
    pk = kind[prov]
    land, sea = pk == 1, pk == 0
    lm, nl = ndi.label(land)
    size = np.bincount(lm.ravel())
    dist, (iy, ix) = ndi.distance_transform_edt(~land, return_indices=True)
    near = np.where(sea, lm[iy, ix], 0)
    # where two coasts' zones meet over open sea: candidate pairs of coast pixels
    cy = []
    for hz in (True, False):
        a = (slice(None), slice(0, -1)) if hz else (slice(0, -1), slice(None))
        b = (slice(None), slice(1, None)) if hz else (slice(1, None), slice(None))
        m = (near[a] > 0) & (near[b] > 0) & (near[a] != near[b]) & (dist[a] + dist[b] + 1 <= GMAX + 1)
        ys, xs = np.nonzero(m)
        qy, qx = (ys, xs + 1) if hz else (ys + 1, xs)
        cy.append(np.stack([iy[ys, xs], ix[ys, xs], iy[qy, qx], ix[qy, qx]], 1))
    c = np.unique(np.concatenate(cy), axis=0)
    u, v = lm[c[:, 0], c[:, 1]], lm[c[:, 2], c[:, 3]]
    swap = u > v
    c[swap] = c[swap][:, [2, 3, 0, 1]]
    u, v = np.minimum(u, v), np.maximum(u, v)
    g = np.hypot(c[:, 0] - c[:, 2], c[:, 1] - c[:, 3])
    keep = g <= GMAX
    c, u, v, g = c[keep], u[keep], v[keep], g[keep]

    def clear(k):
        """the strait's line runs over open sea only, between its two coast pixels"""
        sy, sx = segment(*c[k])
        water, mass = pk[sy, sx][1:-1] == 0, lm[sy, sx][1:-1]
        if not len(water):
            return True
        return bool((water | (mass == u[k]) | (mass == v[k])).all() and water.any())

    order = np.lexsort((c[:, 1], c[:, 0], g))
    first, extra = {}, []
    for k in order:
        key = (int(u[k]), int(v[k]))
        if key not in first:
            if clear(k):
                first[key] = k
        elif size[key[0]] >= BIG and size[key[1]] >= BIG:
            mid = (c[k, :2] + c[k, 2:]) / 2
            taken = [first[key]] + [e for e in extra if (int(u[e]), int(v[e])) == key]
            if all(np.hypot(*(mid - (c[t, :2] + c[t, 2:]) / 2)) >= SPACING for t in taken) and clear(k):
                extra.append(k)
    # minimum spanning tree (Kruskal) over the landmasses: the narrowest strait of each pair, narrowest first
    parent = list(range(nl + 1))

    def root(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    tree = []
    for key, k in sorted(first.items(), key=lambda kv: (g[kv[1]], kv[0])):
        ra, rb = root(key[0]), root(key[1])
        if ra != rb:
            parent[ra] = rb
            tree.append(k)
    # the extra crossings of big landmass pairs whose first crossing is in the tree
    in_tree = {(int(u[k]), int(v[k])) for k in tree}
    extra = [k for k in extra if (int(u[k]), int(v[k])) in in_tree]

    # the sea province each crosses: most of its line, one touching both coasts' provinces if there is one
    nbr = {}
    for a_, b_, n_ in j["adjacency"]:
        nbr.setdefault(a_, set()).add(b_)
        nbr.setdefault(b_, set()).add(a_)
    names = state_names()
    owners = j["owners"]
    out = []
    for k in tree + extra:
        ay, ax, by, bx = (int(t) for t in c[k])
        pa, pb = int(prov[ay, ax]), int(prov[by, bx])
        sy, sx = segment(ay, ax, by, bx)
        on = [int(prov[y, x]) for y, x in zip(sy, sx) if pk[y, x] == 0]
        if not on:   # coasts touching corner to corner: the sea pixel beside them
            ys_, xs_ = np.nonzero(sea[max(ay - 2, 0):ay + 3, max(ax - 2, 0):ax + 3])
            on = [int(prov[max(ay - 2, 0) + ys_[0], max(ax - 2, 0) + xs_[0]])]
        both = [q for q in dict.fromkeys(on) if q in nbr.get(pa, ()) and q in nbr.get(pb, ())]
        if not both:
            both = sorted(q for q in nbr.get(pa, set()) & nbr.get(pb, set()) if kind[q] == 0)
        through = max(both, key=on.count) if both else max(set(on), key=on.count)
        ty, tx = next(((y, x) for y, x in zip(sy, sx) if prov[y, x] == through), None) or \
            tuple(int(t) for t in np.argwhere(prov == through)[0])
        sa, sb = int(state_of[pa]), int(state_of[pb])
        out.append(dict(a=[ax, ay], b=[bx, by], through=[int(tx), int(ty)], gap=round(float(g[k]), 1),
                        kind="link" if k in tree else "extra",
                        name=f"{names.get(sa, owners[sa])} - {names.get(sb, owners[sb])}",
                        owners=[owners[sa], owners[sb]], landmass_px=[int(size[u[k]]), int(size[v[k]])],
                        through_touches_both=bool(both)))
    # numbered west to east in bands from the north, as region_map.py numbers regions
    out.sort(key=lambda e: ((e["a"][1] + e["b"][1]) // 2 // 320, (e["a"][0] + e["b"][0]) / 2))
    for n, e in enumerate(out, 1):
        e["n"] = n
    PROPOSAL.write_text(json.dumps(dict(
        note="Proposed strait crossings (scripts/straits.py find): approve with `python3 scripts/straits.py approve`.",
        default_gap=DEFAULT_GAP, crossings=out), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    draw(out, prov, kind, pk, j)
    tiers = [(t, sum(e["gap"] <= t for e in out)) for t, _ in TIERS]
    print(f"{len(out)} crossings proposed ({len(tree)} linking {nl} landmasses, {len(extra)} more along long straits "
          f"between big ones); up to " + ", ".join(f"{t} px: {n}" for t, n in tiers))
    print(f"{sum(not e['through_touches_both'] for e in out)} cross a sea province that touches only one side")
    unlinked = nl - len({r for k in tree for r in (int(u[k]), int(v[k]))})
    print(f"landmasses no crossing reaches (over {GMAX} px from any other): {unlinked}")
    print(f"wrote {PROPOSAL} and {MAP}")


def draw(out, prov, kind, pk, j, path=MAP, title="Proposed strait crossings (scripts/straits.py), by width of sea"):
    from PIL import Image, ImageDraw, ImageFont
    sys.path.insert(0, "scripts")
    from common import COUNTRIES
    colour = {v[0]: v[3] for v in COUNTRIES.values()}
    owner_p = np.full(len(kind), -1)
    tags = sorted(set(j["owners"]))
    for s, g in enumerate(j["states"]):
        owner_p[g] = tags.index(j["owners"][s])
    pal = np.array([colour.get(t, (180, 180, 180)) for t in tags] + [(0, 0, 0)], float)
    op = owner_p[prov]
    img = np.empty(prov.shape + (3,), np.uint8)
    img[pk == 0] = (24, 44, 70)
    img[pk == 2] = (60, 90, 130)
    lt = pk == 1
    img[lt] = (pal[op[lt]] * 0.45 + 255 * 0.55).astype(np.uint8)
    edge = np.zeros(prov.shape, bool)
    edge[:, 1:] |= (op[:, 1:] != op[:, :-1]) & lt[:, 1:] & lt[:, :-1]
    edge[1:] |= (op[1:] != op[:-1]) & lt[1:] & lt[:-1]
    img[edge] = (90, 90, 90)
    im = Image.fromarray(img)
    d = ImageDraw.Draw(im)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)
    rings = []
    for e in out:
        col = next(c for t, c in TIERS if e["gap"] <= t)
        (ax, ay), (bx, by) = e["a"], e["b"]
        mx, my = (ax + bx) / 2, (ay + by) / 2
        r = max(8, e["gap"] / 2 + 5)
        d.line([(ax, ay), (bx, by)], fill=col, width=2)
        d.ellipse([mx - r, my - r, mx + r, my + r], outline=col, width=2)
        rings.append((mx, my, r))
    # numbers beside their rings, each where it overlaps no number placed before it and the fewest rings
    placed = []

    def hits(box, others):
        x0, y0, x1, y1 = box
        return sum(not (x1 < a or x0 > c or y1 < b or y0 > d_) for a, b, c, d_ in others)
    for e, (mx, my, r) in zip(out, rings):
        t = str(e["n"])
        w = d.textlength(t, font=font) + 4
        spots = []
        for ang in range(0, 360, 30):
            for dist in (r + 2, r + 12, r + 24):
                cx, cy = mx + np.cos(np.radians(ang)) * (dist + w / 2), my + np.sin(np.radians(ang)) * (dist + 7)
                box = (cx - w / 2, cy - 8, cx + w / 2, cy + 8)
                ring_boxes = [(x - q, y - q, x + q, y + q) for x, y, q in rings if (x, y) != (mx, my)]
                spots.append((hits(box, placed) * 100 + hits(box, ring_boxes) * 10 + dist / r, box))
        box = min(spots)[1]
        placed.append(box)
        if hypot((box[0] + box[2]) / 2 - mx, (box[1] + box[3]) / 2 - my) > r + w / 2 + 10:
            d.line([(mx, my), ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)], fill=(200, 200, 200), width=1)
        d.text((box[0] + 2, box[1] + 1), t, font=font, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
    # the key
    x, y = 20, 20
    d.rectangle([x - 8, y - 8, x + 420, y + 24 * len(TIERS) + 30], fill=(16, 24, 34))
    d.text((x, y), title, font=font, fill=(255, 255, 255))
    lo = 0
    for i, (t, col) in enumerate(TIERS):
        n = sum(lo < e["gap"] <= t for e in out)
        d.ellipse([x, y + 26 + 24 * i, x + 14, y + 40 + 24 * i], outline=col, width=3)
        d.text((x + 24, y + 26 + 24 * i), f"{lo}-{t} px: {n}", font=font, fill=(255, 255, 255))
        lo = t
    im.save(path, optimize=True)


def approve(args):
    prop = json.loads(PROPOSAL.read_text(encoding="utf-8"))["crossings"]
    gap = float(args[args.index("--max-gap") + 1]) if "--max-gap" in args else DEFAULT_GAP

    def nums(flag):
        return {int(x) for x in args[args.index(flag) + 1].split(",")} if flag in args else set()
    drop, add = nums("--drop"), nums("--add")
    known = {e["n"] for e in prop}
    bad = (drop | add) - known
    if bad:
        sys.exit(f"no crossing numbered {sorted(bad)} in {PROPOSAL}")
    chosen = [e for e in prop if (e["gap"] <= gap or e["n"] in add) and e["n"] not in drop
              and frozenset(e["owners"]) not in NEVER and not NEVER_ANY & set(e["owners"])]
    APPROVED.write_text(json.dumps([dict(a=e["a"], b=e["b"], through=e["through"], name=e["name"])
                                    for e in chosen], ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{len(chosen)} crossings into {APPROVED} (up to {gap} px, {len(drop)} dropped, {len(add)} added); rebuild")


def rows(lab, kind, pid):
    """adjacencies.csv rows for source/straits.json (none without it), for build_mod.py"""
    if not APPROVED.is_file():
        return []
    out, seen = [], set()
    for k, e in enumerate(json.loads(APPROVED.read_text(encoding="utf-8")), 1):
        (ax, ay), (bx, by), (tx, ty) = e["a"], e["b"], e["through"]
        a, b, t = int(lab[ay, ax]), int(lab[by, bx]), int(lab[ty, tx])
        if kind[a] != 1 or kind[b] != 1 or kind[t] != 0 or a == b:
            sys.exit(f"source/straits.json, crossing {k} ({e['name']}): its pixels must lie on land, on other land "
                     f"and at sea; the map changed under them (run straits.py find and approve again)")
        if (min(a, b), max(a, b)) in seen:
            continue
        seen.add((min(a, b), max(a, b)))
        out.append(f"{pid[a]};{pid[b]};sea;{pid[t]};-1;-1;-1;-1;;{ascii(e['name'])}")
    return out


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "find":
        find()
    elif cmd == "map":
        a = sys.argv[2:]
        lo = float(a[a.index("--min-gap") + 1]) if "--min-gap" in a else 0
        path = Path(a[a.index("--out") + 1]) if "--out" in a else Path(f"dist/straits_map_over_{int(lo)}px.png")
        cr = [e for e in json.loads(PROPOSAL.read_text(encoding="utf-8"))["crossings"] if e["gap"] > lo]
        prov, kind, state_of, j = load()
        pk = np.asarray(kind)[prov]
        draw(cr, prov, kind, pk, j, path, f"Strait crossings wider than {lo:g} px of sea (their numbers in {PROPOSAL})")
        print(f"{len(cr)} crossings over {lo:g} px -> {path}")
    elif cmd == "approve":
        approve(sys.argv[2:])
    else:
        sys.exit(__doc__)
