"""The facts friends fill in on the Valsora Gazetteer (the shared page, see docs/GAZETTEER.md)
into the build.

    python3 scripts/gazetteer.py paths KEYS.json
        The atlas folder of each nation with a password (n/<TAG>/<key>), from the owner's
        passwords as the ArtifactData tool saves them (`get data/users/me/keys`).
    python3 scripts/gazetteer.py pull DIR
        The shared atlas as Claude's ArtifactData tool saves it (`list` with `out_dir`):
        DIR/n/<TAG>/<key>/<document>.json for each nation, DIR/planned/list.json, and the
        pictures fetched by asset id into DIR/assets/ (it lists the ones still missing).
        Imported like a "Save every nation" file.
    python3 scripts/gazetteer.py import FILE.json [FILE.json ...]
        Files saved from the page or the web site: "Save a file" (one nation) or "Save
        every nation as a file" (the owner's tools), pictures and all. Each nation's facts
        replace source/gazetteer/<TAG>.json.
    python3 scripts/gazetteer.py status
        What source/gazetteer/ holds, against the last build: how much each nation has
        filled in, facts that no longer land on their nation (borders changed), open
        requests, characters and anything else for the author to do by hand.
    python3 scripts/gazetteer.py suggestions
        Everyone's suggestions (areas, lines and points drawn on the page) as
        dist/gazetteer_suggestions.png, a transparent 5120x2560 layer to import into the
        .pdn, and dist/gazetteer_suggestions_preview.png over the map.

source/gazetteer/<TAG>.json is what the build reads: read_layers.py (terrain, rivers,
cities) and build_mod.py (state facts, capitals, railways, supply hubs, names,
sub-ideologies, rulers and party leaders with their titles and portraits, map colours)
call the functions below. A state or province is named by a map pixel "x,y" inside it
(ids shift when the map changes); cities, rivers and railways are lists of map pixels.
A nation's facts win over the .pdn and nations.py for that nation: its cities replace
the Cities layer's dots on its land, and so on. Pictures (flags, portraits) are kept in
source/gazetteer/assets/; a flag already in HOI4's 82:52 shape becomes
source/flags/<TAG>.png (or <TAG>_<ideology>.png) when it is imported, once per picture.
"""
import base64
import hashlib
import io
import json
import os
import re
import sys
import zlib
from collections import defaultdict
from heapq import heappop, heappush
from pathlib import Path

import numpy as np

from common import MAP_W, MAP_H

W, H = MAP_W, MAP_H
DIR = Path(os.environ.get("GAZETTEER_DIR", "source/gazetteer"))  # another folder for tests
FLAGS = Path(os.environ.get("GAZETTEER_FLAGS", "source/flags"))
TAG = re.compile(r"[A-Z][A-Z0-9]{2}")
# a nation's documents in the atlas (n/<TAG>/<key>/<kind>), as on the page
KINDS = ("states", "provinces", "cities", "rivers", "rails", "politics", "flags", "people", "about", "suggest",
         "releasables")
# facts drawn on a nation's provinces: taken only once its states are the author's (finals)
MAP_KINDS = ("states", "provinces", "cities", "rivers", "rails")
REL_ID = re.compile(r"rl-[a-z0-9]{6,40}")
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
ROLES = ("general", "admiral", "advisor", "other")
REQ_KINDS = ("subideology", "subject", "trait", "map", "other")   # as the page's
TRAITS_FILE = Path("source/vanilla/index/traits.json")   # the base game's traits for leaders (vanilla_sync.py)
MAX_TRAITS = 6


def trait_index():
    """the base game's traits a leader may have, by role (index.traits on the page): {"ruler": {key: name}, "general":
    ..., "admiral": ..., "advisor": {slot: {key: (name, ledger)}}, "slots": {slot: (name, cost)}, "defined": ...}"""
    if not hasattr(trait_index, "cache"):
        t = json.loads(TRAITS_FILE.read_text(encoding="utf-8")) if TRAITS_FILE.exists() else {}
        trait_index.cache = {
            **{r: {k: nm for k, nm, *_ in t.get(r, [])} for r in ("ruler", "general", "admiral")},
            "advisor": {sl: {k: (nm, led) for k, nm, led in v} for sl, v in (t.get("advisor") or {}).items()},
            "slots": {sl: (nm, cost) for sl, nm, cost in t.get("slots", [])},
            "defined": {k: set(v) for k, v in (t.get("defined") or {}).items()}}
    return trait_index.cache


def keep_traits(v, allowed):
    """a leader's traits from the page: the base game's for its role, each once, at most MAX_TRAITS"""
    out = []
    for k in v if isinstance(v, list) else []:
        if isinstance(k, str) and k in allowed and k not in out:
            out.append(k)
    return out[:MAX_TRAITS]
MAX_STATE_POP = 500_000_000
ERASE_R = 3  # erase strokes take away river lines this close (px)
CITY_REACH = 20  # a city off the coast belongs to the nearest land this close
PICTURE_MAX = 1200  # px, the longest side of a picture kept in the repo
PNG_MAX = 1_500_000  # bytes: a heavier picture with nothing see-through is kept as a JPEG
FLAG_RATIO, FLAG_SLACK = 82 / 52, 0.04  # flags this close to HOI4's shape go straight in
FLAG_MAX_W = 1180  # as wide as the author's largest (Rouental's original)


def clean(s, n=60):
    """A name as the game's localisation can take it: no quotes or control characters."""
    s = re.sub(r'["\x00-\x1f]', "", str(s or ""))
    return re.sub(r"\s+", " ", s).strip()[:n]


def text(s, n):
    """Free text (notes, descriptions): trimmed, at most n characters."""
    return str(s or "").replace("\x00", "").strip()[:n]


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


def norm_password(pw):
    """as the page reads a password: case, spaces, dots and underscores don't matter"""
    s = re.sub(r"[\s_.,]+", "-", str(pw or "").lower())
    return re.sub(r"-+", "-", s).strip("-")


def key(tag, pw):
    """the folder of a nation's documents in the atlas, n/<TAG>/<key>: from its password"""
    return hashlib.sha256(f"valsora-gazetteer|{tag}|{norm_password(pw)}".encode()).hexdigest()[:32]


# ------------------------------------------------------------------ pictures
def _store(data, stem):
    """A picture's bytes into DIR/assets/<stem>.png, at most PICTURE_MAX px on its longest
    side; a photo (or a picture as heavy as one, with nothing see-through) as .jpg.
    Returns (path relative to DIR, width, height)."""
    from PIL import Image
    im = Image.open(io.BytesIO(data))
    im.load()
    photo = im.format == "JPEG"
    im = im.convert("RGBA")
    w, h = im.size
    if max(w, h) > PICTURE_MAX:
        f = PICTURE_MAX / max(w, h)
        im = im.resize((max(1, round(w * f)), max(1, round(h * f))), Image.LANCZOS)
        w, h = im.size
    solid = im.getchannel("A").getextrema()[0] == 255
    buf = io.BytesIO()
    if not photo:
        (im.convert("RGB") if solid else im).save(buf, "PNG", optimize=True)
        photo = solid and buf.tell() > PNG_MAX
    if photo:
        buf = io.BytesIO()
        im.convert("RGB").save(buf, "JPEG", quality=90)
    (DIR / "assets").mkdir(parents=True, exist_ok=True)
    rel = f"assets/{stem}.{'jpg' if photo else 'png'}"
    for old in (DIR / "assets").glob(stem + ".*"):  # a picture stored before in the other format
        old.unlink()
    (DIR / rel).write_bytes(buf.getvalue())
    return rel, w, h


def picture(v, where, sources, todo):
    """A picture from the page (an uploaded asset's id, or a small copy inline) as
    {"file": "assets/...", "w", "h", "name"} under DIR. An asset not downloaded yet stays
    {"asset": id, ...} and goes on the `todo` list."""
    if not isinstance(v, dict):
        return None
    name = clean(v.get("name"), 80)
    out = {"name": name} if name else {}
    if isinstance(v.get("file"), str) and (DIR / v["file"]).is_file():  # imported before
        return {**out, "file": v["file"], "w": v.get("w"), "h": v.get("h")}
    data, stem = None, None
    if isinstance(v.get("data"), str) and v["data"].startswith("data:image/") and "," in v["data"]:
        try:
            data = base64.b64decode(v["data"].split(",", 1)[1], validate=False)
        except ValueError:
            return None
        stem = hashlib.sha1(data).hexdigest()[:24]
    elif isinstance(v.get("asset"), str) and re.fullmatch(r"[0-9a-f]{32}", v["asset"]):
        stem = v["asset"]
        found = next((f for d in (DIR / "assets", *sources) for f in sorted(Path(d).glob(stem + ".*"))
                      if f.is_file()), None)
        if found is None:
            todo.append((where, stem))
            return {**out, "asset": stem, "w": v.get("w"), "h": v.get("h")}
        data = found.read_bytes()
    if not data:
        return None
    try:
        rel, w, h = _store(data, stem)
    except Exception as e:  # not a picture after all
        print(f"{where}: not a picture ({e}); left out")
        return None
    return {**out, "file": rel, "w": w, "h": h}


def with_pictures(v, images, missing):
    """The facts with each picture the web site keeps apart ({"img": id}, an img-<id>
    document beside the facts) put back inline from `images` (a file's or a pull's)."""
    if isinstance(v, list):
        return [with_pictures(x, images, missing) for x in v]
    if not isinstance(v, dict):
        return v
    if isinstance(v.get("img"), str):
        p = images.get(v["img"]) if isinstance(images, dict) else None
        if isinstance(p, dict) and isinstance(p.get("data"), str):
            return {"data": p["data"], "w": p.get("w"), "h": p.get("h"), "name": v.get("name") or p.get("name")}
        missing.append(v["img"])
        return v
    return {k: with_pictures(x, images, missing) for k, x in v.items()}


def portrait_box(w, h):
    """HOI4's 156:210 from the top of a picture, centred across it when it is wider:
    (left, top, width) for nations.PORTRAITS"""
    if w * 210 > h * 156:
        cw = round(h * 156 / 210)
        return (w - cw) // 2, 0, cw
    return 0, 0, w


# ------------------------------------------------------------------ import
def normalise(tag, facts, meta, requests=(), sources=(), todo=None):
    """One nation's facts from the page, checked and tidied: unknown or broken entries
    are dropped, numbers clamped to what the game takes, pictures stored."""
    import ideologies
    subs = ideologies.ideology_of()
    todo = [] if todo is None else todo
    out = {"tag": tag}
    if meta.get("status") in ("draft", "done"):
        out["status"] = meta["status"]
    if meta.get("notes"):
        out["notes"] = text(meta["notes"], 4000)
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
        if text(v.get("note"), 2000):
            s["note"] = text(v["note"], 2000)
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
            elif c.get("stateCapital"):  # its state's capital (the national capital is its own state's)
                city["state_capital"] = True
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
    parties = {i: s for i, s in (pol.get("parties") or {}).items() if i in IDEOLOGIES and subs.get(s) == i}
    if parties:
        p["parties"] = parties
    if p:
        out["politics"] = p
    # people: the head of state, the parties' leaders, characters for the author
    ppl, people = facts.get("people") or {}, {}
    ruler = dict(ppl.get("ruler") or {}) if isinstance(ppl.get("ruler"), dict) else {}
    if clean(pol.get("ruler"), 80) and not ruler.get("name"):  # the first version kept it with politics
        ruler["name"] = pol["ruler"]
    r = {}
    if clean(ruler.get("name"), 80):
        r["name"] = clean(ruler["name"], 80)
    if clean(ruler.get("desc"), 600):
        r["desc"] = clean(ruler["desc"], 600)
    pic = picture(ruler.get("portrait"), f"{tag} ruler's portrait", sources, todo)
    if pic:
        r["portrait"] = pic
    tr = keep_traits(ruler.get("traits"), trait_index()["ruler"])
    if tr:
        r["traits"] = tr
    if r:
        people["ruler"] = r
    party = {}
    for ideo in IDEOLOGIES:
        v = ppl.get(f"party-{ideo}")
        if not isinstance(v, dict):
            continue
        q = {}
        if clean(v.get("name"), 80):
            q["name"] = clean(v["name"], 80)
        pic = picture(v.get("portrait"), f"{tag} {ideo} leader's portrait", sources, todo)
        if pic:
            q["portrait"] = pic
        tr = keep_traits(v.get("traits"), trait_index()["ruler"])
        if tr:
            q["traits"] = tr
        if q:
            party[ideo] = q
    if party:
        people["parties"] = party
    chars = []
    for k, v in sorted(ppl.items()):
        if not (k.startswith("c-") and isinstance(v, dict)):
            continue
        c = {"role": v.get("role") if v.get("role") in ROLES else "general"}
        if clean(v.get("name"), 80):
            c["name"] = clean(v["name"], 80)
        if text(v.get("notes"), 1000):
            c["notes"] = text(v["notes"], 1000)
        pic = picture(v.get("portrait"), f"{tag} character's portrait", sources, todo)
        if pic:
            c["portrait"] = pic
        ti = trait_index()
        if c["role"] == "advisor" and v.get("slot") in ti["slots"]:
            c["slot"] = v["slot"]
        allowed = ti["advisor"].get(c.get("slot"), {}) if c["role"] == "advisor" else ti.get(c["role"], {})
        tr = keep_traits(v.get("traits"), allowed)
        if tr:
            c["traits"] = tr
        if len(c) > 1:
            chars.append(c)
    if chars:
        people["characters"] = chars
    if people:
        out["people"] = people
    flags = {}
    for slot, v in (facts.get("flags") or {}).items():
        if slot in ("base", *IDEOLOGIES):
            pic = picture(v, f"{tag} {slot} flag", sources, todo)
            if pic:
                flags[slot] = pic
    if flags:
        out["flags"] = flags
    ab, about = facts.get("about") or {}, {}
    if isinstance(ab.get("colour"), str) and re.fullmatch(r"#[0-9a-fA-F]{6}", ab["colour"]):
        about["colour"] = ab["colour"].lower()
    for k, n in (("culture", 80), ("motto", 120), ("anthem", 200)):
        if clean(ab.get(k), n):
            about[k] = clean(ab[k], n)
    if text(ab.get("description"), 6000):
        about["description"] = text(ab["description"], 6000)
    if about:
        out["about"] = about
    sugg = []
    raw = facts.get("suggest") or {}
    for k in sorted(raw):  # ids begin with the time: drawn states keep their order (an earlier one wins)
        v = raw[k]
        if not isinstance(v, dict) or v.get("type") not in ("state", "area", "line", "point"):
            continue
        pts = points(v.get("pts"))
        if len(pts) < {"state": 3, "area": 3, "line": 2, "point": 1}[v["type"]]:
            continue
        sugg.append({"type": v["type"], "pts": pts, "label": clean(v.get("label"), 80), "note": text(v.get("note"), 1000)})
    if sugg:
        out["suggest"] = sorted(sugg, key=lambda v: v["type"])
    # releasables: their land (whole states by pixel; provinces, saved before 2026-10-15 (later);
    # or drawn areas), names, flag and ruler
    rels = []
    raw = facts.get("releasables") or {}
    for rid in sorted(raw, key=lambda k: (num((raw[k] or {}).get("added") if isinstance(raw[k], dict) else 0, 0, 10 ** 14) or 0, k)):
        v = raw[rid]
        if not isinstance(v, dict) or not REL_ID.fullmatch(str(rid)):
            continue
        r = {"id": rid}
        for k, n in (("name", 60), ("adj", 60), ("def", 100)):
            if clean(v.get(k), n):
                r[k] = clean(v[k], n)
        if v.get("ruling") in subs:
            r["ruling"] = v["ruling"]
        if isinstance(v.get("colour"), str) and re.fullmatch(r"#[0-9a-fA-F]{6}", v["colour"]):
            r["colour"] = v["colour"].lower()
        label = f"{tag} releasable {r.get('name') or rid}"
        pic = picture(v.get("flag"), f"{label}: flag", sources, todo)
        if pic:
            r["flag"] = pic
        ld, lead = v.get("leader") if isinstance(v.get("leader"), dict) else {}, {}
        if clean(ld.get("name"), 80):
            lead["name"] = clean(ld["name"], 80)
        if clean(ld.get("desc"), 600):
            lead["desc"] = clean(ld["desc"], 600)
        pic = picture(ld.get("portrait"), f"{label}: ruler's portrait", sources, todo)
        if pic:
            lead["portrait"] = pic
        if lead:
            r["leader"] = lead
        if text(v.get("notes"), 2000):
            r["notes"] = text(v["notes"], 2000)
        land = {}
        for kind_ in ("states", "provinces"):
            keys = set()
            for k, on in (v.get(kind_) or {}).items():
                try:
                    if on:
                        keys.add("%d,%d" % xy(k))
                except ValueError:
                    continue
            if keys:
                land[kind_] = r[kind_] = sorted(keys, key=lambda k: xy(k)[::-1])
        areas = [points(a) for _, a in sorted((v.get("areas") or {}).items()) if isinstance(a, list)]
        if any(len(a) >= 3 for a in areas):
            r["areas"] = [a for a in areas if len(a) >= 3]
        if r.get("name") or land or r.get("areas"):
            rels.append(r)
    if rels:
        out["releasables"] = rels
    reqs = []
    for v in requests or ():
        if isinstance(v, dict) and clean(v.get("title"), 100):
            reqs.append({"kind": v.get("kind") if v.get("kind") in REQ_KINDS else "other",
                         "title": clean(v["title"], 100), "details": text(v.get("details"), 3000),
                         "status": v.get("status") if v.get("status") in ("open", "done", "declined") else "open",
                         "reply": text(v.get("reply"), 2000), "at": num(v.get("at"), 0, 10 ** 14) or 0})
    if reqs:
        out["requests"] = sorted(reqs, key=lambda r: (r["at"], r["title"]))
    return out


def map_open(unlock=None):
    """{tag: True or False}: whose map facts the import takes: a nation's whose states are the
    author's (finals), or whose map tools the owner opened on the page ({TAG: True}, or False to
    keep them closed); None when there is no build to tell"""
    try:
        fin = finals()
    except FileNotFoundError:
        print("No build in work/ to tell whose states are drawn: every nation's map facts are taken.")
        return None
    unlock = unlock or {}
    return {t: unlock.get(t) is True or (unlock.get(t) is not False and f) for t, f in fin.items()}


def tags_taken(planned=None):
    """Every tag in use: Valsora's countries, the base game's, nations not on the map yet and
    releasables already named."""
    from common import COUNTRIES
    taken = {v[0] for v in COUNTRIES.values()}
    f = Path("source/vanilla/index/tags.txt")
    if f.exists():
        taken |= {ln.split("\t")[0] for ln in f.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")}
    taken |= set(planned or {})
    if (DIR / "planned.json").exists():
        taken |= set(json.loads((DIR / "planned.json").read_text(encoding="utf-8")))
    for g in load().values():
        taken |= {r["tag"] for r in g.get("releasables", []) if r.get("tag")}
    return taken


def new_tag(name, taken):
    """A free tag for a releasable: its name's first three letters, else its first letter and
    two later ones, else the first free one; never D and two digits (the game's own)."""
    import itertools
    import string
    import unicodedata
    letters = [c for c in unicodedata.normalize("NFKD", name or "").upper() if "A" <= c <= "Z"]
    cands = ["".join(letters[:3])] if len(letters) >= 3 else []
    cands += [letters[0] + a + b for i, a in enumerate(letters[1:], 1) for b in letters[i + 1:]] if letters else []
    cands += ("".join(t) for t in itertools.product(string.ascii_uppercase, repeat=3))
    for t in cands:
        if TAG.fullmatch(t) and t not in taken:
            taken.add(t)
            return t
    raise SystemExit("no free tag left")


def import_nations(nations, planned=None, sources=(), unlock=None):
    """{tag: {"facts", "meta", "requests", "images"}} (and the owner's nations not on the
    map yet, and their switches of the map tools) -> source/gazetteer/; then the new flags
    into source/flags/. A nation whose states aren't drawn yet (finals) keeps no map facts;
    releasables keep their tags from one import to the next. Lists pictures still to
    download."""
    DIR.mkdir(parents=True, exist_ok=True)
    todo = []
    opened = map_open(unlock)
    taken = tags_taken(planned)
    for tag, v in sorted(nations.items()):
        if not TAG.fullmatch(tag):
            print(f"skipped {tag!r}: not a country tag")
            continue
        missing = []
        facts = with_pictures(v.get("facts") or {}, v.get("images") or {}, missing)
        if missing:
            print(f"{tag}: {len(missing)} pictures are not in the file; left out")
        n = normalise(tag, facts, v.get("meta") or {}, v.get("requests") or (), sources, todo)
        if opened is not None and opened.get(tag) is False:
            dropped = [k for k in MAP_KINDS if n.pop(k, None) is not None]
            dropped += [f"the {k} of {r.get('name') or r['id']}" for r in n.get("releasables", [])
                        for k in ("states", "provinces") if r.pop(k, None)]
            if dropped:
                print(f"{tag}: its states aren't drawn yet (map tools closed): left out {', '.join(dropped)}")
        path = DIR / f"{tag}.json"
        had = {r["id"]: r["tag"] for r in (json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}).get("releasables", [])
               if r.get("tag")}
        for r in n.get("releasables", []):
            r["tag"] = had.get(r["id"]) or new_tag(r.get("name"), taken)
        if len(n) == 1:
            if path.exists():
                path.unlink()
                print(f"{tag}: nothing filled in any more; removed {path}")
            continue
        path.write_text(json.dumps(n, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print(f"{tag}: {summary(n)}")
    if planned is not None:
        keep = {t: {"name": clean(p.get("name")), "continent": clean(p.get("continent"))}
                for t, p in sorted(planned.items()) if TAG.fullmatch(t) and isinstance(p, dict) and clean(p.get("name"))}
        f = DIR / "planned.json"
        if keep:
            f.write_text(json.dumps(keep, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        elif f.exists():
            f.unlink()
    install_flags(load())
    if todo:
        print(f"{len(todo)} pictures to download first (Artifact read with path = the asset id, into "
              f"assets/ beside the pulled atlas or the file), then run this again:")
        for where, a in todo:
            print(f"  {a}  {where}")
    return todo


def import_files(files):
    nations, planned, unlock = {}, None, None
    for f in files:
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        if not d.get("gazetteer"):
            sys.exit(f"{f} is not a file saved from the Gazetteer")
        if d.get("tag"):
            nations[d["tag"]] = d
        for tag, v in (d.get("nations") or {}).items():
            nations[tag] = v
        if isinstance(d.get("planned"), dict):
            planned = d["planned"]
        if isinstance(d.get("unlock"), dict):
            unlock = d["unlock"]
    import_nations(nations, planned, [Path(f).parent / "assets" for f in files], unlock)


def _body(path):
    """a saved document: its fields, whether the file holds them bare or wrapped with its id"""
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    for k in ("data", "fields", "document"):
        if isinstance(d.get(k), dict) and set(d) <= {k, "id", "doc_id", "version", "path", "collection", "created_at",
                                                         "updated_at", "createdAt", "updatedAt", "createTime", "updateTime"}:
            return d[k]
    return d


def pull(root):
    """the atlas from ArtifactData out_dirs (DIR/n/<TAG>/<key>/...) -> source/gazetteer/"""
    root = Path(root)
    keys = {}
    for f in sorted(root.rglob("keys.json")):  # the owner's passwords, if saved here: the current folders
        keys.update({t: pw for t, pw in _body(f).items() if TAG.fullmatch(t) and isinstance(pw, str)})
    nations = {}
    for tagdir in sorted(p for p in (root / "n").glob("*") if p.is_dir() and TAG.fullmatch(p.name)):
        tag = tagdir.name
        dirs = sorted(d for d in tagdir.iterdir() if d.is_dir())
        if tag in keys:
            dirs = [d for d in dirs if d.name == key(tag, keys[tag])] or dirs
        if len(dirs) > 1:  # an old password's documents too: the most recently edited
            def edited(d):
                m = d / "meta.json"
                return (_body(m).get("updatedAt") or 0) if m.exists() else 0
            dirs.sort(key=edited)
            print(f"{tag}: {len(dirs)} folders; took {dirs[-1].name}, the last edited")
        d = dirs[-1]
        facts = {f.stem: _body(f) for f in sorted(d.glob("*.json")) if f.stem in KINDS}
        meta = _body(d / "meta.json") if (d / "meta.json").exists() else {}
        reqs = [_body(f) for f in sorted(d.glob("req-*.json"))]
        imgs = {f.stem[4:]: _body(f) for f in sorted(d.glob("img-*.json"))}
        nations[tag] = {"facts": facts, "meta": meta, "requests": reqs, "images": imgs}
    planned_f, unlock_f = root / "planned" / "list.json", root / "planned" / "unlock.json"
    todo = import_nations(nations, _body(planned_f) if planned_f.exists() else None, [root / "assets"],
                          _body(unlock_f) if unlock_f.exists() else None)
    reqs = [(t, r) for t, v in nations.items() for r in v["requests"] if (r.get("status") or "open") == "open"]
    print(f"{len(reqs)} open requests")
    for t, r in sorted(reqs, key=lambda x: x[1].get("at") or 0):
        print(f"  {t} [{r.get('kind')}] {r.get('title')}: {str(r.get('details') or '')[:200]}")
    return todo


def paths(keys_file):
    """n/<TAG>/<key> of every nation in the owner's passwords"""
    for tag, pw in sorted(_body(keys_file).items()):
        if TAG.fullmatch(tag) and isinstance(pw, str):
            print(f"n/{tag}/{key(tag, pw)}")


def install_flags(G):
    """Flags sent on the page into source/flags/, each picture once (so a flag the author
    changes later stays theirs). Shapes other than HOI4's 82:52 wait to be fitted by hand."""
    from PIL import Image
    record_f = DIR / "installed.json"
    record = json.loads(record_f.read_text(encoding="utf-8")) if record_f.exists() else {}
    sent = [(tag, slot, im) for tag, f in sorted(G.items()) for slot, im in sorted((f.get("flags") or {}).items())]
    sent += [(r["tag"], "base", r["flag"]) for f in G.values() for r in f.get("releasables", []) if r.get("tag") and r.get("flag")]
    for tag, slot, im in sent:  # nations' flags, and their releasables'
        if not im.get("file"):
            continue
        k = f"{tag}:{slot}"
        if record.get(k) == im["file"]:
            continue
        w, h = im["w"], im["h"]
        if abs(w / h / FLAG_RATIO - 1) > FLAG_SLACK:
            print(f"{tag}: its {slot} flag is {w} x {h}, not HOI4's 82:52; fit it by hand from {DIR / im['file']}")
            continue
        from import_flags import opaque
        a = np.asarray(Image.open(DIR / im["file"]).convert("RGBA"))
        pic = Image.fromarray(opaque(a))
        if pic.width > FLAG_MAX_W:
            pic = pic.resize((FLAG_MAX_W, round(pic.height * FLAG_MAX_W / pic.width)), Image.LANCZOS)
        FLAGS.mkdir(parents=True, exist_ok=True)
        out = FLAGS / (f"{tag}.png" if slot == "base" else f"{tag}_{slot}.png")
        pic.save(out)
        record[k] = im["file"]
        print(f"{tag}: {slot} flag -> {out}")
    if record:
        record_f.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def summary(n):
    parts = []
    for k, what in (("states", "states"), ("provinces", "provinces"), ("cities", "cities"),
                    ("rivers", "rivers"), ("rails", "railways"), ("suggest", "suggestions")):
        if k in n:
            parts.append(f"{len(n[k])} {what}")
    for k in ("politics", "people", "flags", "about"):
        if k in n:
            parts.append(k)
    if n.get("releasables"):
        parts.append("releasables " + ", ".join(f"{r.get('name') or r['id']} ({r['tag']})" for r in n["releasables"]))
    if n.get("status") == "done":
        parts.append("finished")
    return ", ".join(parts) or "nothing"


def load():
    """{tag: facts} from source/gazetteer/."""
    return {f.stem: json.loads(f.read_text(encoding="utf-8")) for f in sorted(DIR.glob("*.json"))
            if TAG.fullmatch(f.stem)} if DIR.exists() else {}


# ------------------------------------------------------------------ whose states are final
LINE_LAYERS = ("Necessary Borders", "Necessary States")


def finals(lab=None, kind=None, states=None, owners=None, layers=Path("work/pdn_game")):
    """{tag: True or False} for every country owning land, after a build: True when its states
    are the author's, i.e. no two of them share an area the Necessary Borders and Necessary
    States lines enclose (apply_outlines.py cuts an area without lines into states of about
    1,300 px, which the author's lines replace later, provinces and all). A country of whole
    areas (one state, islands) counts as final. Until then the Gazetteer keeps its map tools
    (states, cities, terrain, rivers, railways, hubs) closed, and the import drops such facts."""
    from scipy import ndimage as ndi
    from skimage.measure import label as sklabel
    if lab is None:
        p = np.load("work/provinces.npz")
        lab, kind = p["prov"], p["kind"]
        rj = json.load(open("work/regions.json"))
        states, owners = rj["states"], rj["owners"]
    tags = sorted({o for o in owners if o})
    names_f = layers / "layers.txt"
    if not names_f.exists():  # a placeholder build: no lines to read
        return {t: True for t in tags}
    names = names_f.read_text().splitlines()
    state_of = np.full(len(kind), -1, np.int64)
    for s, g in enumerate(states):
        state_of[g] = s
    st = state_of[lab]
    land = st >= 0
    lines = np.zeros(land.shape, bool)
    for nm in LINE_LAYERS:
        if nm in names:
            lines |= np.load(layers / f"layer{names.index(nm)}.npy", mmap_mode="r")[..., 3] > 0
    lines &= land
    cells = sklabel(land & ~lines, connectivity=1)
    idx = ndi.distance_transform_edt(cells == 0, return_distances=False, return_indices=True)
    area = np.where(land & (cells == 0), cells[idx[0], idx[1]], cells)  # line pixels: the nearest area
    n = int(area.max()) + 1
    pair, count = np.unique(st[land].astype(np.int64) * n + area[land], return_counts=True)
    main = {}  # each state's area: where most of its land is
    for k, c in zip(pair.tolist(), count.tolist()):
        s, a = divmod(k, n)
        if c > main.get(s, (0, 0))[0]:
            main[s] = (c, a)
    together = defaultdict(int)  # states of one country in one area
    for s, (_, a) in main.items():
        together[(a, owners[s])] += 1
    out = {t: True for t in tags}
    for s, (_, a) in main.items():
        if together[(a, owners[s])] > 1:
            out[owners[s]] = False
    return out


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
    the dots on its land: [province, name, x, y, victory points, capital, its state's capital]."""
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
            out.append([p, c["name"], x, y, c["vp"], bool(c.get("capital")), bool(c.get("state_capital"))])
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


def leaders(tag, subs, facts, handmade, named, portraits):
    """nations.LEADERS' sub-ideologies of a country with the facts' ruling one and parties
    (first rules). The ruler and the party leaders the facts name (with titles and
    portraits) go into `named`, a copy of nations.NAMED_LEADERS, their portraits into
    `portraits` (nations.PORTRAITS)."""
    pol, ppl = (facts or {}).get("politics") or {}, (facts or {}).get("people") or {}
    if (not pol and not ppl) or handmade:
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
    people = [(ruling, "ruler", ppl.get("ruler") or {})]
    people += [(parties[i], f"party_{i}", v) for i, v in sorted((ppl.get("parties") or {}).items()) if i in parties]
    for sub, role, v in people:
        cid = f"{tag}_leader_{sub}"
        name, sprite = (named.get(cid) or (None, None))[:2]
        pic = v.get("portrait") or {}
        if pic.get("file") and (DIR / pic["file"]).is_file() and pic.get("w") and pic.get("h"):
            pname = f"{tag}_gazetteer_{role}"
            portraits[pname] = (str(DIR / pic["file"]), *portrait_box(pic["w"], pic["h"]), None)
            sprite = f"GFX_portrait_{pname}"
        traits = tuple(t for t in v.get("traits") or [] if t in trait_index()["ruler"])
        if v.get("name") or v.get("desc") or sprite or traits:
            named[cid] = (v.get("name") or name, sprite, v.get("desc"), traits)
    return out


COMMANDER = {"general": ("army", "corps_commander", (("skill", 3), ("attack_skill", 3), ("defense_skill", 3),
                                                     ("planning_skill", 2), ("logistics_skill", 2))),
             "admiral": ("navy", "navy_leader", (("skill", 3), ("attack_skill", 3), ("defense_skill", 3),
                                                 ("maneuvering_skill", 2), ("coordination_skill", 2)))}


def characters(tag, facts, portraits, small=None, generic=None):
    """The facts' generals, admirals and advisors as characters the country has from the start (2026-10-15: the
    author couldn't find Rouental's admiral in game; until then the page's characters were only listed for the
    author): a corps commander or an admiral of skill 3, an advisor in the post the page gives (the slot's usual cost,
    the ledger the base game gives its first trait), with the base game's traits the page picked and the portrait it
    holds (into `portraits`, nations.PORTRAITS; an advisor's also small, into `small`). The notes stay a comment for
    the author. An advisor without a post, and others, stay on `status`'s list. A general or admiral without a portrait
    gets one of `generic`'s ({"army": [...], "navy": [...]}: the base game's generic portraits of the nation's culture,
    cultures.unit_portraits), picked by its id, as the game's own generated ones are; an advisor without one shows the
    game's silhouette, as 44 of the base game's do. Returns (character blocks, loc lines, ids)."""
    blocks, loc, ids = [], [], []
    n = defaultdict(int)
    ti = trait_index()
    for c in ((facts or {}).get("people") or {}).get("characters", []):
        role_ = c.get("role")
        if not c.get("name") or not (role_ in COMMANDER or (role_ == "advisor" and c.get("slot") in ti["slots"])):
            continue
        n[role_] += 1
        cid = f"{tag}_gazetteer_{role_}_{n[role_]}"
        pic, sprite = c.get("portrait") or {}, None
        if pic.get("file") and (DIR / pic["file"]).is_file() and pic.get("w") and pic.get("h"):
            portraits[cid] = (str(DIR / pic["file"]), *portrait_box(pic["w"], pic["h"]), None)
            sprite = f"GFX_portrait_{cid}"
        notes = " / ".join(ln.strip() for ln in (c.get("notes") or "").splitlines() if ln.strip())
        traits = c.get("traits") or []
        tr = f"\t\t\ttraits = {{ {' '.join(traits)} }}\n" if traits else ""
        if role_ == "advisor":
            slot = c["slot"]
            ledger = ti["advisor"].get(slot, {}).get(traits[0], ("", ""))[1] if traits else ""
            if sprite and small is not None:
                small.add(cid)
            body = ("\t\tadvisor = {\n"
                    f"\t\t\tslot = {slot}\n\t\t\tidea_token = {cid}\n"
                    + (f"\t\t\tledger = {ledger}\n" if ledger else "")
                    + f"\t\t\tallowed = {{ original_tag = {tag} }}\n" + tr
                    + f"\t\t\tcost = {ti['slots'][slot][1]}\n\t\t\tai_will_do = {{ factor = 1 }}\n\t\t}}\n")
            port = (f"\t\tportraits = {{\n\t\t\tcivilian = {{\n\t\t\t\tlarge = {sprite}\n"
                    f"\t\t\t\tsmall = {sprite}_small\n\t\t\t}}\n\t\t}}\n") if sprite else ""
        else:
            kind, role, skills = COMMANDER[role_]
            pool = (generic or {}).get(kind) or []
            if not sprite and pool:
                sprite = pool[zlib.crc32(cid.encode()) % len(pool)]
            body = f"\t\t{role} = {{\n" + tr + "".join(f"\t\t\t{k} = {v}\n" for k, v in skills) + "\t\t}\n"
            port = (f"\t\tportraits = {{\n\t\t\t{kind} = {{\n\t\t\t\tlarge = {sprite}\n\t\t\t}}\n\t\t}}\n"
                    if sprite else "")
        blocks.append(f"\t{cid} = {{\n" + (f"\t\t# the Gazetteer's notes: {notes}\n" if notes else "")
                      + f"\t\tname = {cid}\n" + port + body + "\t}\n")
        loc.append(f' {cid}:0 "{c["name"]}"')
        ids.append(cid)
    return blocks, loc, ids


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


REL_COLOURS = ("#b5543c", "#3c7db5", "#6f9a3a", "#8a4fb0", "#c2912e", "#2f9a93", "#b04f7c", "#5c6670")  # as the page


def releasables(G, lab, kind, state_of, owners, notes, taken=()):
    """The facts' releasables as the build makes them: countries owning nothing, with cores
    on the states of their nation they hold (whole states), or at least half of (by provinces,
    saved before states were picked whole, or the areas drawn before its states were), the
    largest first (the capital). Each is {tag, parent,
    name, adj, colour, states, facts}, facts being what the build reads for a nation
    (politics with its names and ruling sub-ideology, its ruler, its colour). `taken`: tags
    of countries already in the mod."""
    rels = [(tag, i, r) for tag, f in sorted(G.items()) for i, r in enumerate(f.get("releasables", []))]
    if not rels:
        return []
    from PIL import Image, ImageDraw
    st = np.asarray(state_of)
    own = _owner_of(lab, state_of, owners)
    px_state = np.where(kind[lab] == 1, st[lab], -1)
    state_px = np.bincount(px_state[px_state >= 0], minlength=len(owners))
    prov_px = np.bincount(lab.ravel(), minlength=len(kind))
    out, used = [], set(taken)
    for tag, i, r in rels:
        name = r.get("name") or r.get("tag") or r["id"]
        if not r.get("tag") or r["tag"] in used:
            notes.append(f"Gazetteer: {tag}'s releasable {name} has no tag of its own (import it again); left out")
            continue
        cover = defaultdict(int)  # state -> its pixels the releasable holds
        for k in r.get("states", []):
            s_ = int(st[at(lab, k)])
            if s_ >= 0 and owners[s_] == tag:
                cover[s_] = int(state_px[s_])
        provs = {at(lab, k) for k in r.get("provinces", [])}
        for p in provs:
            if kind[p] == 1 and own[p] == tag and cover[int(st[p])] < state_px[int(st[p])]:
                cover[int(st[p])] += int(prov_px[p])
        for pts in r.get("areas", []):
            u = _unwrap(pts)
            x0, y0 = min(x for x, _ in u), max(0, min(y for _, y in u))
            x1, y1 = max(x for x, _ in u), min(H - 1, max(y for _, y in u))
            im = Image.new("1", (x1 - x0 + 1, y1 - y0 + 1), 0)
            ImageDraw.Draw(im).polygon([(x - x0, y - y0) for x, y in u], fill=1, outline=1)
            ys, xs = np.nonzero(np.asarray(im))
            ys, xs = ys + y0, (xs + x0) % W
            ps = lab[ys, xs]
            mine = (kind[ps] == 1) & (own[ps] == tag) & ~np.isin(ps, list(provs))
            for s_, c in zip(*np.unique(st[ps[mine]], return_counts=True)):
                cover[int(s_)] += int(c)
        cores = sorted((s_ for s_, c in cover.items() if owners[s_] == tag and c * 2 >= state_px[s_]),
                       key=lambda s_: (-cover[s_], s_))
        part = [s_ for s_, c in cover.items() if owners[s_] == tag and 0 < c * 2 < state_px[s_]]
        if part:
            notes.append(f"Gazetteer: {tag}'s releasable {name} holds less than half of {len(part)} state(s); "
                         f"they stay {tag}'s alone (a state line along its border would give them to it)")
        if not cores:
            notes.append(f"Gazetteer: {tag}'s releasable {name} holds no state by half; left out")
            continue
        used.add(r["tag"])
        colour = r.get("colour") or REL_COLOURS[i % len(REL_COLOURS)]
        parent_pol = G.get(tag, {}).get("politics") or {}
        facts = {"politics": {"names": {"base": {k: r[k] for k in ("name", "def", "adj") if r.get(k)}}},
                 "about": {"colour": colour}}
        if r.get("ruling") or parent_pol.get("ruling"):
            facts["politics"]["ruling"] = r.get("ruling") or parent_pol["ruling"]
        if r.get("leader"):
            facts["people"] = {"ruler": r["leader"]}
        out.append(dict(tag=r["tag"], parent=tag, name=name, adj=r.get("adj") or name,
                        colour=tuple(int(colour[k:k + 2], 16) for k in (1, 3, 5)), states=cores, facts=facts))
    return out


def colours(G):
    """{tag: (r, g, b)}: the map colours the facts give, over the .pdn paint (like
    nations.DISPLAY_COLOUR)"""
    out = {}
    for tag, f in G.items():
        c = (f.get("about") or {}).get("colour")
        if c:
            out[tag] = tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))
    return out


# ------------------------------------------------------------------ suggestions
SUGGEST = (168, 50, 110)  # the page's colour for suggestions


def suggestions(out_dir=Path("dist")):
    """Everyone's suggestions as a transparent map-sized layer for the .pdn, and a preview
    over the map. Returns how many. A drawn state is the nation's land inside its line that
    no state it drew before holds, as the page shows it."""
    from PIL import Image, ImageDraw, ImageFont
    from scipy import ndimage as ndi
    G = load()
    items = [(tag, v) for tag, f in sorted(G.items()) for v in f.get("suggest", [])]
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fill = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d, df = ImageDraw.Draw(layer), ImageDraw.Draw(fill)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
    ink = SUGGEST + (255,)
    where = {}  # drawn state -> its label's place
    drawn = [(tag, v) for tag, v in items if v["type"] == "state"]
    if drawn:
        p = np.load("work/provinces.npz")
        lab, kind = p["prov"], p["kind"]
        own = _owner_of(lab, np.load("work/regions.npz")["state_of"], json.load(open("work/regions.json"))["owners"])
        tags = sorted({t for t, _ in drawn})
        code = np.array([tags.index(t) + 1 if t in tags else 0 for t in own.tolist()], np.int32)
        land_of = np.where(kind[lab] == 1, code[lab], 0)
        rgba = np.zeros((H, W, 4), np.uint8)
        taken = {t: np.zeros((H, W), bool) for t in tags}
        for tag, v in drawn:
            im = Image.new("1", (W, H), 0)
            dm = ImageDraw.Draw(im)
            pts = _unwrap(v["pts"])
            for shift in (-W, 0, W):
                dm.polygon([(x + shift, y) for x, y in pts], fill=1, outline=1)
            m = np.asarray(im) & (land_of == tags.index(tag) + 1) & ~taken[tag]
            taken[tag] |= m
            if not m.any():
                continue
            rim = m & ~ndi.binary_erosion(m, np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]))
            rgba[m] = SUGGEST + (90,)
            rgba[rim] = SUGGEST + (255,)
            ys, xs = np.nonzero(m)
            where[id(v)] = (float(xs.mean()), float(ys.mean()))
        fill = Image.alpha_composite(fill, Image.fromarray(rgba))
        df = ImageDraw.Draw(fill)
    for tag, v in items:
        if v["type"] == "state":
            continue
        pts = _unwrap(v["pts"])
        for shift in (-W, 0, W):  # whatever crosses the seam shows on both sides
            q = [(x + shift, y) for x, y in pts]
            if max(x for x, _ in q) < 0 or min(x for x, _ in q) >= W:
                continue
            if v["type"] == "area":
                df.polygon(q, fill=SUGGEST + (70,))
                d.line(q + q[:1], fill=ink, width=3, joint="curve")
            elif v["type"] == "line":
                d.line(q, fill=ink, width=3, joint="curve")
            else:
                x, y = q[0]
                d.polygon([(x, y - 8), (x + 7, y), (x, y + 8), (x - 7, y)], fill=ink, outline=(255, 255, 255, 255))
    for tag, v in items:
        pts = _unwrap(v["pts"])
        if v["type"] == "state" and id(v) not in where:
            continue  # none of its nation's land inside it
        mid = v["type"] in ("area", "state")
        x, y = where.get(id(v)) or ((sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)) if mid else pts[0])
        label = f"{tag}: {v['label']}" if v["label"] else tag
        x = x % W
        d.text((x + (0 if mid else 10), y), label, font=font, fill=(30, 20, 30, 255),
               anchor="mm" if mid else "lm", stroke_width=3, stroke_fill=(255, 255, 255, 255))
    layer = Image.alpha_composite(fill, layer)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    layer.save(out_dir / "gazetteer_suggestions.png", optimize=True)
    base = Path("dist/valsora_countries_5120x2560.png")
    under = Image.open(base).convert("RGBA") if base.exists() else Image.new("RGBA", (W, H), (185, 205, 216, 255))
    Image.alpha_composite(under.resize((W, H)), layer).convert("RGB").resize((W // 2, H // 2), Image.LANCZOS) \
        .save(out_dir / "gazetteer_suggestions_preview.png", optimize=True)
    print(f"{len(items)} suggestions from {len({t for t, _ in items})} nations: "
          f"{out_dir / 'gazetteer_suggestions.png'} (import it into the .pdn as a layer), "
          f"{out_dir / 'gazetteer_suggestions_preview.png'}")
    return len(items)


# ------------------------------------------------------------------ status
def status():
    G = load()
    if not G:
        print(f"{DIR} holds nothing yet.")
        return
    p = np.load("work/provinces.npz")
    lab = p["prov"]
    reg = np.load("work/regions.npz")
    rj = json.load(open("work/regions.json"))
    own = _owner_of(lab, reg["state_of"], rj["owners"])
    on_map = set(rj["owners"])
    planned_f = DIR / "planned.json"
    planned = json.loads(planned_f.read_text(encoding="utf-8")) if planned_f.exists() else {}
    record_f = DIR / "installed.json"
    record = json.loads(record_f.read_text(encoding="utf-8")) if record_f.exists() else {}
    todo = []
    notes = []  # how the build takes the releasables: their cores, or why they are left out
    rels = releasables(G, lab, p["kind"], reg["state_of"], rj["owners"], notes)
    by_rel = {r["tag"]: r for r in rels}
    for tag, f in G.items():
        lost = [k for kind_ in ("states", "provinces") for k in f.get(kind_, {})
                if own[at(lab, k)] != tag]
        where = "" if tag in on_map else f" (not on the map yet{': ' + planned[tag]['name'] if tag in planned else ''})"
        print(f"{tag}{where}: {summary(f)}" + (f"; {len(lost)} facts no longer on {tag}'s land, e.g. {lost[:3]}" if lost else ""))
        for r in f.get("requests", []):
            if r["status"] == "open":
                todo.append(f"{tag} asks [{r['kind']}] {r['title']}: {r['details'][:200]}")
        for c in (f.get("people") or {}).get("characters", []):
            built = c.get("name") and (c["role"] in COMMANDER or (c["role"] == "advisor" and c.get("slot") in trait_index()["slots"]))
            if built:   # in the build (characters()); the notes are the author's
                if c.get("notes"):
                    what = "skill 3" if c["role"] in COMMANDER else trait_index()["slots"][c["slot"]][0].lower()
                    tr = ", ".join(c.get("traits") or []) or "no traits"
                    said = " / ".join(ln.strip() for ln in c["notes"].splitlines() if ln.strip())
                    todo.append(f"{tag} {c['role']} {c['name']} is in the game ({what}; {tr}); notes: {said[:160]}")
                continue
            todo.append(f"{tag} {c['role']}: {c.get('name', '(no name)')}" + (f" - {c['notes'][:160]}" if c.get("notes") else "")
                        + (f" [portrait {c['portrait'].get('file') or 'not downloaded'}]" if c.get("portrait") else ""))
        ab = f.get("about") or {}
        if ab.get("culture"):
            todo.append(f"{tag} culture: {ab['culture']}")
        for slot, im in (f.get("flags") or {}).items():
            if not im.get("file"):
                todo.append(f"{tag} {slot} flag: not downloaded yet (asset {im.get('asset')})")
            elif record.get(f"{tag}:{slot}") != im["file"]:
                todo.append(f"{tag} {slot} flag: {im['w']} x {im['h']}, to fit to 82:52 by hand ({DIR / im['file']})")
        for r in f.get("releasables", []):
            b_ = by_rel.get(r.get("tag"))
            print(f"  releasable {r.get('name') or r['id']} ({r.get('tag')}): "
                  + (f"cores on {len(b_['states'])} state(s)" if b_ else "not in the build")
                  + (f", {len(r['states'])} states picked" if r.get("states") else "")
                  + (f", {len(r['provinces'])} provinces" if r.get("provinces") else "")
                  + (f", {len(r['areas'])} drawn areas" if r.get("areas") else ""))
            im = r.get("flag")
            if im and (not im.get("file") or record.get(f"{r.get('tag')}:base") != im["file"]):
                todo.append(f"{r.get('tag')} (releasable of {tag}) flag: " + (f"{im['w']} x {im['h']}, to fit to 82:52 by hand ({DIR / im['file']})" if im.get("file") else "not downloaded yet"))
    todo += [n.replace("Gazetteer: ", "") for n in notes]
    if todo:
        print("\nFor the author (or Claude) to do by hand:")
        for t in todo:
            print("  " + t)


if __name__ == "__main__":
    if not Path("source/vanilla").is_dir():  # the base game's tags, the last build: all by the root
        sys.exit("Run this from the repository's root: python3 scripts/gazetteer.py ...")
    if len(sys.argv) >= 3 and sys.argv[1] == "import":
        import_files(sys.argv[2:])
    elif len(sys.argv) == 3 and sys.argv[1] == "pull":
        pull(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == "paths":
        paths(sys.argv[2])
    elif len(sys.argv) == 2 and sys.argv[1] == "status":
        status()
    elif len(sys.argv) == 2 and sys.argv[1] == "suggestions":
        suggestions()
    else:
        sys.exit(__doc__)
