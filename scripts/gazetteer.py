"""The facts friends fill in on the Valsora Gazetteer (the shared page, see docs/GAZETTEER.md)
into the build.

    python3 scripts/gazetteer.py import FILE.json [FILE.json ...]
        Files saved from the page: "Save a file" (one nation) or "Save every nation"
        (all of them), or the shared atlas read back by Claude in the same shape. Each
        nation's facts replace source/gazetteer/<TAG>.json.
    python3 scripts/gazetteer.py pull DIR
        The shared atlas as Claude's ArtifactData tool saves it (`list` with `out_dir`):
        DIR/nations/<TAG>.json, DIR/facts/<TAG>-<kind>.json, DIR/requests/<id>.json. Imported
        like a "Save every nation" file; the open requests are listed.
    python3 scripts/gazetteer.py status
        What source/gazetteer/ holds, against the last build: how much each nation has
        filled in, and facts that no longer land on their nation (borders changed).

source/gazetteer/<TAG>.json is what the build reads: read_layers.py (terrain, rivers,
cities) and build_mod.py (state facts, capitals, railways, supply hubs, names and
sub-ideologies) call the functions below. A state or province is named by a map pixel
"x,y" inside it (ids shift when the map changes); cities, rivers and railways are
lists of map pixels. A nation's facts win over the .pdn and nations.py for that nation:
its cities replace the Cities layer's dots on its land, and so on.
"""
import json
import os
import re
import sys
from collections import defaultdict
from heapq import heappop, heappush
from pathlib import Path

import numpy as np

from common import MAP_W, MAP_H

W, H = MAP_W, MAP_H
DIR = Path(os.environ.get("GAZETTEER_DIR", "source/gazetteer"))  # another folder for tests
# terrain.bmp palette index of each terrain the page offers (common.TERRAIN_TYPES)
TERRAIN_INDEX = {"plains": 0, "forest": 1, "hills": 2, "desert": 3, "mountain": 6, "marsh": 9,
                 "urban": 13, "jungle": 21}
CATEGORIES = {"wasteland": 0, "enclave": 0, "tiny_island": 0, "pastoral": 1, "small_island": 1, "rural": 2,
              "large_island": 3, "town": 4, "large_town": 5, "city": 6, "large_city": 8, "metropolis": 10,
              "megalopolis": 12}
# vanilla's buildings_max_level of the island categories
ISLAND_MAX = {"tiny_island": {"naval_base": 3, "air_base": 2}, "small_island": {"naval_base": 6, "air_base": 4},
              "large_island": {"naval_base": 8, "air_base": 6}}
# the page's building keys -> the game's, and the most vanilla allows
BUILDINGS = {"infra": ("infrastructure", 5), "civ": ("industrial_complex", 20), "mil": ("arms_factory", 20),
             "dock": ("dockyard", 20), "air": ("air_base", 10), "aa": ("anti_air_building", 5),
             "naval": ("naval_base", 10)}
RESOURCES = ("oil", "steel", "aluminium", "rubber", "tungsten", "chromium")
VPS = {1, 3, 5, 10, 15, 20, 25, 30, 40, 50}
IDEOLOGIES = ("democratic", "fascism", "communism", "neutrality", "theocracy")
MAX_STATE_POP = 500_000_000
ERASE_R = 3  # erase strokes take away river lines this close (px)
CITY_REACH = 20  # a city off the coast belongs to the nearest land this close


def clean(s, n=60):
    """A name as the game's localisation can take it: no quotes or control characters."""
    s = re.sub(r'["\x00-\x1f]', "", str(s or ""))
    return re.sub(r"\s+", " ", s).strip()[:n]


def xy(key):
    x, y = (int(v) for v in str(key).split(","))
    return x % W, y


def num(v, lo, hi):
    try:
        v = int(v)
    except (TypeError, ValueError):
        return None
    return max(lo, min(hi, v))


def points(pts):
    out = []
    for p in pts or []:
        try:
            x, y = int(p[0]), int(p[1])
        except (TypeError, ValueError, IndexError):
            continue
        if 0 <= y < H:
            out.append([x % W, y])
    return out


# ------------------------------------------------------------------ import
def normalise(tag, facts, meta):
    """One nation's facts from the page, checked and tidied: unknown or broken entries
    are dropped, numbers clamped to what the game takes."""
    import ideologies
    subs = ideologies.ideology_of()
    out = {"tag": tag}
    if meta.get("status") in ("draft", "done"):
        out["status"] = meta["status"]
    if meta.get("notes"):
        out["notes"] = str(meta["notes"])[:4000]
    states = {}
    for k, v in (facts.get("states") or {}).items():
        if not isinstance(v, dict):
            continue
        try:
            xy(k)
        except ValueError:
            continue
        s = {}
        if clean(v.get("name")):
            s["name"] = clean(v["name"])
        if v.get("pop") is not None and num(v["pop"], 0, MAX_STATE_POP) is not None:
            s["pop"] = num(v["pop"], 0, MAX_STATE_POP)
        if v.get("cat") in CATEGORIES:
            s["cat"] = v["cat"]
        for b, (_, most) in BUILDINGS.items():
            if v.get(b) is not None and num(v[b], 0, most) is not None:
                s[b] = num(v[b], 0, most)
        res = {r: num(n, 0, 999) for r, n in (v.get("res") or {}).items()
               if r in RESOURCES and n is not None and num(n, 0, 999) is not None}
        if res:
            s["res"] = res
        if str(v.get("note") or "").strip():
            s["note"] = str(v["note"]).strip()[:2000]
        if s:
            states[f"{xy(k)[0]},{xy(k)[1]}"] = s
    if states:
        out["states"] = states
    provs = {}
    for k, v in (facts.get("provinces") or {}).items():
        if not isinstance(v, dict):
            continue
        p = {}
        if v.get("t") in TERRAIN_INDEX:
            p["t"] = v["t"]
        if v.get("hub") is True:
            p["hub"] = True
        try:
            if p:
                provs[f"{xy(k)[0]},{xy(k)[1]}"] = p
        except ValueError:
            continue
    if provs:
        out["provinces"] = provs
    if facts.get("cities") is not None:  # edited on the page: the whole list, maybe empty
        cities, capital = [], False
        for c in sorted((c for c in (facts.get("cities") or {}).values() if isinstance(c, dict)),
                        key=lambda c: (c.get("y", 0), c.get("x", 0))):
            pt = points([[c.get("x"), c.get("y")]])
            if not pt or not clean(c.get("name")):
                continue
            vp = c.get("vp") if c.get("vp") in VPS else 5
            city = {"x": pt[0][0], "y": pt[0][1], "name": clean(c["name"]), "vp": vp}
            if c.get("capital") and not capital:
                city["capital"] = capital = True
            cities.append(city)
        out["cities"] = cities
    rivers = []
    for r in (facts.get("rivers") or {}).values():
        if isinstance(r, dict) and r.get("kind") in ("major", "minor", "erase") and len(points(r.get("pts"))) >= 2:
            rivers.append({"kind": r["kind"], "pts": points(r["pts"])})
    if rivers:
        out["rivers"] = sorted(rivers, key=lambda r: (r["kind"], r["pts"]))
    rails = []
    for r in (facts.get("rails") or {}).values():
        if isinstance(r, dict) and len(points(r.get("pts"))) >= 2:
            rails.append({"level": num(r.get("level"), 1, 5) or 3, "pts": points(r["pts"])})
    if rails:
        out["rails"] = sorted(rails, key=lambda r: r["pts"])
    pol = facts.get("politics") or {}
    p = {}
    names = {}
    for ideo, v in (pol.get("names") or {}).items():
        if ideo in ("base", *IDEOLOGIES) and isinstance(v, dict):
            n = {k: clean(v.get(k), 100) for k in ("name", "def", "adj") if clean(v.get(k), 100)}
            if n:
                names[ideo] = n
    if names:
        p["names"] = names
    if pol.get("ruling") in subs:
        p["ruling"] = pol["ruling"]
    if clean(pol.get("ruler"), 80):
        p["ruler"] = clean(pol["ruler"], 80)
    parties = {i: s for i, s in (pol.get("parties") or {}).items() if i in IDEOLOGIES and subs.get(s) == i}
    if parties:
        p["parties"] = parties
    if p:
        out["politics"] = p
    return out


def import_files(files):
    DIR.mkdir(parents=True, exist_ok=True)
    nations = {}
    for f in files:
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        if not d.get("gazetteer"):
            sys.exit(f"{f} is not a file saved from the Gazetteer")
        if d.get("tag"):
            nations[d["tag"]] = (d.get("facts") or {}, d.get("meta") or {})
        for tag, v in (d.get("nations") or {}).items():
            nations[tag] = (v.get("facts") or {}, v.get("meta") or {})
    for tag, (facts, meta) in sorted(nations.items()):
        if not re.fullmatch(r"[A-Z][A-Z0-9]{2}", tag):
            print(f"skipped {tag!r}: not a country tag")
            continue
        n = normalise(tag, facts, meta)
        path = DIR / f"{tag}.json"
        if len(n) == 1:
            if path.exists():
                path.unlink()
                print(f"{tag}: nothing filled in any more; removed {path}")
            continue
        path.write_text(json.dumps(n, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print(f"{tag}: {summary(n)}")


def _body(path):
    """a saved document: its fields, whether the file holds them bare or wrapped with its id"""
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    for k in ("data", "fields", "document"):
        if isinstance(d.get(k), dict) and set(d) <= {k, "id", "doc_id", "version", "path", "collection",
                                                         "created_at", "updated_at", "createTime", "updateTime"}:
            return d[k]
    return d


def pull(root):
    """the atlas from an ArtifactData out_dir -> source/gazetteer/, and the open requests"""
    root = Path(root)
    nations = defaultdict(lambda: {"facts": {}, "meta": {}})
    for f in sorted((root / "facts").glob("*.json")):
        tag, _, kind = f.stem.partition("-")
        nations[tag]["facts"][kind] = _body(f)
    for f in sorted((root / "nations").glob("*.json")):
        nations[f.stem]["meta"] = _body(f)
    out = root / "gazetteer-all.json"
    out.write_text(json.dumps({"gazetteer": 1, "nations": nations}, ensure_ascii=False), encoding="utf-8")
    import_files([out])
    reqs = [_body(f) for f in sorted((root / "requests").glob("*.json"))]
    open_ = [r for r in reqs if (r.get("status") or "open") == "open"]
    print(f"{len(reqs)} requests, {len(open_)} open")
    for r in sorted(open_, key=lambda r: r.get("at") or 0):
        print(f"  {r.get('tag')} [{r.get('kind')}] {r.get('title')}: {str(r.get('details') or '')[:200]}")


def summary(n):
    parts = []
    for k, what in (("states", "states"), ("provinces", "provinces"), ("cities", "cities"),
                    ("rivers", "rivers"), ("rails", "railways")):
        if k in n:
            parts.append(f"{len(n[k])} {what}")
    if "politics" in n:
        parts.append("politics")
    if n.get("status") == "done":
        parts.append("finished")
    return ", ".join(parts) or "nothing"


def load():
    """{tag: facts} from source/gazetteer/."""
    return {f.stem: json.loads(f.read_text(encoding="utf-8")) for f in sorted(DIR.glob("*.json"))} \
        if DIR.exists() else {}


# ------------------------------------------------------------------ the build
def _owner_of(lab, state_of, owners):
    """tag of the state each province is in (None for water and stateless land)"""
    st = np.asarray(state_of)
    tags = np.array([o or "" for o in owners] + [""], dtype=object)
    return tags[np.where(st >= 0, st, len(owners))]


def at(lab, key):
    x, y = xy(key)
    return int(lab[y, x])


def terrain(G, terr, lab, kind, state_of, owners, notes):
    """The terrain the facts give provinces, painted onto the Terrain layer's land pixels."""
    if not any("provinces" in f for f in G.values()):
        return terr
    own = _owner_of(lab, state_of, owners)
    paint = np.full(len(kind), -1, np.int32)
    lost = 0
    for tag, f in G.items():
        for k, v in f.get("provinces", {}).items():
            p = at(lab, k)
            if kind[p] != 1 or own[p] != tag:
                lost += 1
                continue
            if v.get("t") in TERRAIN_INDEX:
                paint[p] = TERRAIN_INDEX[v["t"]]
    if lost:
        notes.append(f"Gazetteer: {lost} province facts no longer land on their nation's provinces")
    over = paint[lab]
    return np.where((over >= 0) & (kind[lab] == 1), over, terr)


def _line(x0, y0, x1, y1):
    """pixels of a straight line, 8-connected (Bresenham); x may wrap"""
    pts = []
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err = dx + dy
    while True:
        pts.append((x0, y0))
        if x0 == x1 and y0 == y1:
            return pts
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def _unwrap(pts):
    """consecutive points the short way round the seam"""
    out = [list(pts[0])]
    for x, y in pts[1:]:
        px = out[-1][0]
        x = x + W * round((px - x) / W)
        out.append([x, y])
    return out


def rivers(G, lines, rv, lab, kind, state_of, owners):
    """Rivers drawn on the page into the Major / Minor Rivers line masks (rivers.py traces
    them like the author's), and erase strokes, which take away the lines and exact river
    pixels near them on their own nation's land. Returns the pixels drawn."""
    if not any("rivers" in f for f in G.values()):
        return 0
    own = _owner_of(lab, state_of, owners)
    drawn = 0
    yy, xx = np.mgrid[-ERASE_R:ERASE_R + 1, -ERASE_R:ERASE_R + 1]
    disk = (yy ** 2 + xx ** 2) <= ERASE_R ** 2
    for tag, f in G.items():
        for r in f.get("rivers", []):
            pts = _unwrap(r["pts"])
            px = [p for a, b in zip(pts, pts[1:]) for p in _line(a[0], a[1], b[0], b[1])]
            if r["kind"] == "erase":
                for x, y in px:
                    for dy, dx in zip(yy[disk], xx[disk]):
                        X, Y = (x + dx) % W, y + dy
                        if 0 <= Y < H and own[lab[Y, X]] == tag:
                            lines["Major Rivers"][Y, X] = lines["Minor Rivers"][Y, X] = False
                            rv[Y, X] = -1
            else:
                m = lines["Major Rivers" if r["kind"] == "major" else "Minor Rivers"]
                for x, y in px:
                    if 0 <= y < H:
                        m[y, x % W] = True
                        drawn += 1
    return drawn


def cities(G, layer, lab, kind, state_of, owners, notes):
    """The Cities layer's cities, with each nation's own list from the facts in place of
    the dots on its land: [province, name, x, y, victory points, capital]."""
    with_cities = {t for t, f in G.items() if "cities" in f}
    if not with_cities:
        return layer
    own = _owner_of(lab, state_of, owners)
    out = [c for c in layer if own[c[0]] not in with_cities]
    taken = {c[0] for c in out}
    land = None
    for tag in sorted(with_cities):
        for c in G[tag]["cities"]:
            x, y = c["x"], c["y"]
            p = int(lab[y, x])
            if kind[p] != 1:
                if land is None:
                    from scipy import ndimage as ndi
                    land = ndi.distance_transform_edt(kind[lab] != 1, return_distances=True, return_indices=True)
                d, (iy, ix) = land[0][y, x], (land[1][0][y, x], land[1][1][y, x])
                if d > CITY_REACH:
                    notes.append(f"Gazetteer: {tag}'s city {c['name']} at ({x}, {y}) is not on land; left out")
                    continue
                p = int(lab[iy, ix])
            if own[p] != tag:
                notes.append(f"Gazetteer: {tag}'s city {c['name']} at ({x}, {y}) is no longer on its land; left out")
                continue
            if p in taken:
                notes.append(f"Gazetteer: {tag}'s city {c['name']} at ({x}, {y}) shares a province with another; left out")
                continue
            taken.add(p)
            out.append([p, c["name"], x, y, c["vp"], bool(c.get("capital"))])
    names = defaultdict(list)
    for c in out:
        names[c[1]].append(c)
    for nm, cs in names.items():
        if len(cs) > 1 and any(len(c) > 4 for c in cs):
            notes.append(f"Gazetteer: {len(cs)} cities are named {nm}")
    return out


def state_facts(G, lab, state_of, owners, notes):
    """{state index: its facts} for every state the facts name by a pixel inside it."""
    own = _owner_of(lab, state_of, owners)
    out, lost = {}, 0
    for tag, f in G.items():
        for k, v in f.get("states", {}).items():
            p = at(lab, k)
            s = int(state_of[p])
            if s < 0 or own[p] != tag:
                lost += 1
                continue
            out[s] = {**out.get(s, {}), **v}
    if lost:
        notes.append(f"Gazetteer: {lost} state facts no longer land on their nation's states")
    return out


def hubs(G, lab, kind, state_of, owners):
    """{tag: [province]} of the supply hubs the facts place."""
    own = _owner_of(lab, state_of, owners)
    out = {}
    for tag, f in G.items():
        hs = sorted({at(lab, k) for k, v in f.get("provinces", {}).items() if v.get("hub")})
        hs = [p for p in hs if kind[p] == 1 and own[p] == tag]
        if hs:
            out[tag] = hs
    return out


def railways(G, lab, kind, centre, adjacency, notes):
    """The facts' railways as HOI4 wants them: (level, [provinces]) with every two in a row
    touching. Between two points a railway takes the shortest way over land, measured
    from province centre to centre (the page draws it the same way). Where railways share
    a stretch the higher level wins, and every stretch is written once."""
    if not any("rails" in f for f in G.values()):
        return []
    nbrs = defaultdict(list)
    for a, b, _ in adjacency:
        if kind[a] == 1 and kind[b] == 1:
            nbrs[a].append(b)
            nbrs[b].append(a)

    def dist(u, v):
        dx = abs(centre[u][1] - centre[v][1])
        return float(np.hypot(min(dx, W - dx), centre[u][0] - centre[v][0]))

    def route(a, b):
        if a == b:
            return [a]
        best, prev, done, heap = {a: 0.0}, {}, set(), [(0.0, a)]
        while heap:
            d, u = heappop(heap)
            if u in done:
                continue
            done.add(u)
            if u == b:
                break
            for v in nbrs[u]:
                if v in done:
                    continue
                nd = d + dist(u, v)
                if nd < best.get(v, float("inf")):
                    best[v], prev[v] = nd, u
                    heappush(heap, (nd, v))
        if b not in done:
            return None
        path = [b]
        while path[-1] != a:
            path.append(prev[path[-1]])
        return path[::-1]

    edges = {}
    for tag, f in sorted(G.items()):
        for r in f.get("rails", []):
            provs = []
            for x, y in r["pts"]:
                p = int(lab[y, x])
                if kind[p] != 1:
                    notes.append(f"Gazetteer: a railway point of {tag} at ({x}, {y}) is not on land")
                    provs = None
                    break
                provs.append(p)
            if not provs:
                continue
            for a, b in zip(provs, provs[1:]):
                path = route(a, b)
                if path is None:
                    notes.append(f"Gazetteer: {tag}'s railway has no land route between provinces {a + 1} "
                                 f"and {b + 1}; that stretch is left out")
                    continue
                for u, v in zip(path, path[1:]):
                    e = (min(u, v), max(u, v))
                    edges[e] = max(edges.get(e, 0), r["level"])
    # chain the stretches of each level into lines, no province twice in a line
    out = []
    for level in sorted(set(edges.values()), reverse=True):
        left = {e for e, lv in edges.items() if lv == level}
        adj = defaultdict(set)
        for u, v in left:
            adj[u].add(v)
            adj[v].add(u)
        while left:
            odd = sorted(u for u in adj if len(adj[u]) % 2 and adj[u])
            start = odd[0] if odd else min(u for u in adj if adj[u])
            line, seen = [start], {start}
            while True:
                u = line[-1]
                nxt = sorted(v for v in adj[u] if v not in seen)
                if not nxt:
                    break
                v = nxt[0]
                adj[u].discard(v)
                adj[v].discard(u)
                left.discard((min(u, v), max(u, v)))
                line.append(v)
                seen.add(v)
            out.append((level, line))
    return out


def leaders(tag, subs, pol, handmade, named):
    """nations.LEADERS' sub-ideologies of a country with the facts' ruling one and parties
    (first rules), and the ruler's name into the copy of nations.NAMED_LEADERS `named`."""
    if not pol or handmade:
        return subs
    import ideologies
    of = ideologies.ideology_of()
    ruling = pol.get("ruling") or (subs[0] if subs else None)
    if not ruling:
        return subs
    parties = {of[s]: s for s in subs[1:] if s in of}
    parties.update({i: s for i, s in (pol.get("parties") or {}).items() if s})
    parties.pop(of[ruling], None)
    out = [ruling] + [parties[i] for i in IDEOLOGIES if i in parties]
    if pol.get("ruler"):
        cid = f"{tag}_leader_{ruling}"
        named[cid] = (pol["ruler"], (named.get(cid) or (None, None))[1])
    return out


def names(tag, base, by_ideology, pol):
    """The country's (name, formal name, adjective), and per ideology, with the facts'
    names over the build's: base = (name, formal, adj); by_ideology = nations.IDEOLOGY_NAMES[tag]."""
    n = (pol or {}).get("names", {})
    b = n.get("base", {})
    base = (b.get("name") or base[0], b.get("def") or base[1], b.get("adj") or base[2])
    out = {}
    for ideo in IDEOLOGIES:
        d = by_ideology.get(ideo, base)
        f = n.get(ideo, {})
        out[ideo] = (f.get("name") or d[0], f.get("def") or d[1], f.get("adj") or d[2])
    return base, out


# ------------------------------------------------------------------ status
def status():
    G = load()
    if not G:
        print(f"{DIR} holds nothing yet.")
        return
    p = np.load("work/provinces.npz")
    lab, kind = p["prov"], p["kind"]
    reg = np.load("work/regions.npz")
    rj = json.load(open("work/regions.json"))
    own = _owner_of(lab, reg["state_of"], rj["owners"])
    for tag, f in G.items():
        lost = [k for kind_ in ("states", "provinces") for k in f.get(kind_, {})
                if own[at(lab, k)] != tag]
        print(f"{tag}: {summary(f)}" + (f"; {len(lost)} facts no longer on {tag}'s land, e.g. {lost[:3]}" if lost else ""))


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "import":
        import_files(sys.argv[2:])
    elif len(sys.argv) == 3 and sys.argv[1] == "pull":
        pull(sys.argv[2])
    elif len(sys.argv) == 2 and sys.argv[1] == "status":
        status()
    else:
        sys.exit(__doc__)
