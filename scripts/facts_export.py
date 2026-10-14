"""The map data of the Valsora Gazetteer, the shared page where nations' facts are filled in
(state names, terrain, rivers, cities, population, railways ...; see docs/GAZETTEER.md).

Run after a build (sh scripts/run_all.sh). Writes work/gazetteer/, which is published
with the page (scripts/gazetteer.html) as the artifact's files:
    index.json      every country that owns land: name, colour, continent, small flag,
                    counts; the world's owners at 1024x512 (to pick a nation on the map)
    world.png       the world in country colours, 2048x1024, for the start page
    n/<TAG>.json    one per country: its states, provinces and cities with the values the
                    build gives them now, its flag, and its land with its neighbours' around
                    it as province numbers per pixel, in parts (land and islands within
                    PART_GAP px of each other share a part), plus the rivers on it
Keys are pixels: a state or province is named by its anchor pixel "x,y" (the point
farthest inside it), as source/state_names.json does, since ids shift when the map
changes. Points (cities, rivers, railways) are game map pixels.
"""
import base64
import hashlib
import io
import json
import re
import shutil
import zlib
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

import gazetteer
import ideologies
import nations
from common import MAP_W, MAP_H, COUNTRIES, CONTINENTS

W, H = MAP_W, MAP_H
OUT = Path("work/gazetteer")
MOD = Path("build/valsora_test")
PART_GAP = 160  # land of one country closer than this shares a part
MARGIN = 40  # neighbours' land shown around a part
WORLD = (2048, 1024)
IDS = (1024, 512)
CONT_NAME = {"nonscio": "Nonscio", "araseos": "Araseos", "aislada": "Aislada", "solitas": "Solitas",
             "yastreovakia": "Yastreovakia", "usnistan": "Usnistan", "orientalis": "Orientalis"}
# what the page offers, in the order it shows them; palette index on terrain.bmp
TERRAINS = ["plains", "forest", "hills", "mountain", "desert", "marsh", "jungle", "urban"]
# the five ideologies as the game names them (ideologies.py), in the order the page shows them
IDEOLOGY_NAMES = [("neutrality", "Monarchist"), ("democratic", "Democratic"), ("fascism", "Authoritarian"),
                  ("communism", "Communist"), ("theocracy", "Theocratic")]


def b64z(a):
    return base64.b64encode(zlib.compress(np.ascontiguousarray(a).tobytes(), 9)).decode()


def png_uri(img):
    buf = io.BytesIO()
    img.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def hexcol(rgb):
    return "#%02x%02x%02x" % tuple(int(v) for v in rgb)


def read_states():
    """id -> manpower, category, buildings, naval base, resources, victory points, from
    the built state histories."""
    out = {}
    for f in (MOD / "history/states").glob("*.txt"):
        t = f.read_text(encoding="utf-8-sig")
        sid = int(re.search(r"\bid = (\d+)", t).group(1))
        b = dict((k, int(v)) for k, v in re.findall(
            r"\t\t\t(infrastructure|industrial_complex|arms_factory|dockyard|air_base|anti_air_building) = (\d+)", t))
        naval = re.search(r"\d+ = \{ naval_base = (\d+) \}", t)
        res = re.search(r"\tresources = \{(.*?)\}", t, re.S)
        out[sid] = dict(
            pop=int(re.search(r"manpower = (\d+)", t).group(1)),
            cat=re.search(r"state_category = (\w+)", t).group(1),
            b=b, naval=int(naval.group(1)) if naval else 0,
            res=dict((k, int(v)) for k, v in re.findall(r"(\w+) = (\d+)", res.group(1))) if res else {},
            vp=[(int(p), int(v)) for p, v in re.findall(r"victory_points = \{ (\d+) (\d+) \}", t)])
    return out


def read_loc(path, prefix):
    out = {}
    for m in re.finditer(r'^ ' + prefix + r'(\d+):0 "(.*)"$', path.read_text(encoding="utf-8-sig"), re.M):
        out[int(m.group(1))] = m.group(2)
    return out


def politics(tag, loc):
    """The nation's names under each ideology, its rulers and parties, as the build has them."""
    names = {"": [loc.get(tag, ""), loc.get(f"{tag}_DEF", ""), loc.get(f"{tag}_ADJ", "")]}
    for ideo, _ in IDEOLOGY_NAMES:
        names[ideo] = [loc.get(f"{tag}_{ideo}", ""), loc.get(f"{tag}_{ideo}_DEF", ""), loc.get(f"{tag}_{ideo}_ADJ", "")]
    of = ideologies.ideology_of()
    subs = nations.LEADERS.get(tag, [])
    hand = tag in nations.HAND_MADE
    leaders = [[s, of[s], loc.get(f"{tag}_leader_{s}", "")] for s in subs]
    return dict(names=names, leaders=leaders, handmade=hand,
                ruling=(nations.RULING.get(tag, "neutrality") if hand or not subs else of[subs[0]]))


def flag(tag, medium=False):
    f = MOD / "gfx/flags" / ("medium" if medium else "") / f"{tag}.tga"
    return png_uri(Image.open(f).convert("RGB")) if f.exists() else None


def parts_of(mask4, gap4):
    """Groups of a country's land (a mask at 1/4 scale) closer than gap4 to each other,
    across the seam too. Returns lists of (y slice, x0, x1) boxes at 1/4 scale, x1 may run
    past the right edge (wrap)."""
    r = gap4 // 2  # both sides grow, so pieces gap4 apart meet
    padded = np.pad(mask4, ((0, 0), (r + 1, r + 1)), mode="wrap")
    grown = (ndi.distance_transform_edt(~padded) <= r)[:, r + 1:-(r + 1)]
    # roll the map so a column with none of this country's land is at the seam
    cols = ~grown.any(0)
    shift = int(np.argmax(cols)) if cols.any() else 0
    rolled = np.roll(grown, -shift, axis=1)
    lab, n = ndi.label(rolled, structure=np.ones((3, 3), bool))
    own = np.roll(mask4, -shift, axis=1)
    boxes = []
    for k, sl in enumerate(ndi.find_objects(lab), 1):
        m = (lab[sl] == k) & own[sl]
        if not m.any():
            continue
        ys, xs = np.nonzero(m)
        boxes.append((sl[0].start + ys.min(), sl[0].start + ys.max() + 1,
                      sl[1].start + xs.min() + shift, sl[1].start + xs.max() + 1 + shift))
    return boxes


def main():
    p = np.load("work/provinces.npz")
    lab, kind = p["prov"], p["kind"]
    reg = np.load("work/regions.npz")
    anchor, size, state_of, centre = reg["anchor"], reg["size"], reg["state_of"], reg["centre"]
    rj = json.load(open("work/regions.json"))
    states, owners = rj["states"], rj["owners"]
    world = np.load("work/world.npz")
    rivers = world["rivers"]
    n = len(kind)
    built = read_states()
    names = read_loc(MOD / "localisation/english/valsora_l_english.yml", "VAL_STATE_")
    loc = dict(re.findall(r'^ ([A-Za-z0-9_]+):0 "(.*)"$',
                          (MOD / "localisation/english/valsora_l_english.yml").read_text(encoding="utf-8-sig"), re.M))
    vp_names = read_loc(MOD / "localisation/english/replace/valsora_victory_points_l_english.yml",
                        "VICTORY_POINTS_")
    by_tag = {v[0]: k for k, v in COUNTRIES.items()}
    tags = sorted({t for t in owners if t})
    tindex = {t: i for i, t in enumerate(tags)}
    prov_owner = np.full(n, -1)
    for s, g in enumerate(states):
        prov_owner[g] = tindex[owners[s]]
    # coastal provinces: land touching sea
    coastal = np.zeros(n, bool)
    for a, b, _ in rj["adjacency"]:
        if kind[a] == 1 and kind[b] == 0:
            coastal[a] = True
        elif kind[a] == 0 and kind[b] == 1:
            coastal[b] = True
    terrain = list(p["terrain"])
    city_at = {int(c[0]): c for c in rj.get("cities", [])}

    shown = {**nations.DISPLAY_COLOUR, **gazetteer.colours(gazetteer.load())}  # as the build colours them

    def colour(tag):
        return hexcol(shown.get(tag, COUNTRIES[by_tag[tag]][3]))

    def key(i):
        return f"{int(anchor[i][1])},{int(anchor[i][0])}"

    # capitals and continents, from the built country histories
    capital = {}
    for f in (MOD / "history/countries").glob("*.txt"):
        tag = f.name[:3]
        if tag in tindex:
            capital[tag] = int(re.search(r"^capital = (\d+)", f.read_text(encoding="utf-8-sig"), re.M).group(1)) - 1

    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "n").mkdir(parents=True)

    owner_px = np.where(kind[lab] == 1, prov_owner[lab], -1)
    # 1/4 scale masks of every country's land, for its parts
    small = owner_px[::4, ::4]
    index = []
    biggest = (0, "")
    for tag in tags:
        t = tindex[tag]
        mine = [s for s in range(len(states)) if owners[s] == tag]
        boxes = parts_of(small == t, PART_GAP // 4)
        own = [i for s in mine for i in states[s]]
        local = {i: k for k, i in enumerate(own)}
        others, nb = [], {}
        parts = []
        for (y0, y1, x0, x1) in sorted(boxes, key=lambda b: -(b[1] - b[0]) * (b[3] - b[2])):
            Y0 = max(0, y0 * 4 - MARGIN)
            Y1 = min(H, y1 * 4 + MARGIN)
            X0 = x0 * 4 - MARGIN
            X1 = x1 * 4 + MARGIN
            if X1 - X0 >= W:
                X0, X1 = 0, W
            xs = np.arange(X0, X1) % W
            crop = lab[Y0:Y1][:, xs]
            ck = kind[crop]
            ids = np.unique(crop[ck == 1])
            for i in ids:
                i = int(i)
                if i not in local:
                    local[i] = len(own) + len(others)
                    o = tags[prov_owner[i]] if prov_owner[i] >= 0 else ""
                    if o and o not in nb:
                        nb[o] = len(nb)
                    others.append(nb[o] if o else -1)
            lut = np.zeros(n, np.uint16)
            for i, k in local.items():
                lut[i] = k + 2
            px = np.where(ck == 0, 0, np.where(ck == 2, 1, lut[crop])).astype("<u2")
            rv = rivers[Y0:Y1][:, xs]
            rv = np.where(rv < 254, rv.astype(np.int16) + 1, 0).astype(np.uint8)
            # which of this country's states are in the part (to name it)
            st = sorted({int(state_of[i]) for i in ids if prov_owner[i] == t},
                        key=lambda s: -sum(int(size[i]) for i in states[s]))
            parts.append(dict(x0=int(X0 % W), y0=int(Y0), w=int(X1 - X0), h=int(Y1 - Y0),
                              states=[mine.index(s) for s in st], px=b64z(px), rv=b64z(rv)))
            if (X1 - X0) * (Y1 - Y0) > biggest[0]:
                biggest = ((X1 - X0) * (Y1 - Y0), f"{tag} {X1 - X0}x{Y1 - Y0}")
        cities = []
        st_list = []
        cap_state = capital.get(tag, -1)
        for k, s in enumerate(mine):
            g = states[s]
            b = built[s + 1]
            # where the state's name goes: the anchor of its province nearest its middle
            w_ = np.array([size[i] for i in g], float)
            cy = float(np.average([centre[i][0] for i in g], weights=w_))
            cx = float(np.average([centre[i][1] for i in g], weights=w_))
            lp = min(g, key=lambda i: (anchor[i][0] - cy) ** 2 + (anchor[i][1] - cx) ** 2)
            st_list.append(dict(
                key=key(max(g, key=lambda i: (size[i], -i))), id=s + 1, name=names.get(s + 1, ""),
                pop=b["pop"], cat=b["cat"], b=b["b"], naval=b["naval"], res=b["res"],
                coastal=bool(coastal[g].any()), capital=s == cap_state,
                provs=[local[i] for i in g], area=int(sum(int(size[i]) for i in g)),
                label=[int(anchor[lp][1]), int(anchor[lp][0])]))
            for pp, vp in b["vp"]:
                i = pp - 1
                if i in city_at:  # a dot on the Cities layer
                    c = city_at[i]
                    x, y, nm = int(c[2]), int(c[3]), c[1]
                elif vp_names.get(pp, "") not in ("", f"{names.get(s + 1, '')} City"):
                    # a victory point named by hand (nations.CITY_NAMES), shown as a city
                    x, y, nm = int(anchor[i][1]), int(anchor[i][0]), vp_names[pp]
                else:
                    continue
                cities.append(dict(x=x, y=y, name=nm, vp=vp, capital=s == cap_state and vp >= 10))
        provs = [[key(i), mine.index(int(state_of[i])), terrain[i], int(coastal[i]), int(size[i]),
                  int(anchor[i][1]), int(anchor[i][0])] for i in own]
        cont = CONTINENTS[int(p["cont"][states[cap_state][0]]) - 1] if cap_state >= 0 else ""
        c = COUNTRIES[by_tag[tag]]
        nation = dict(tag=tag, name=c[1], adj=c[2], colour=colour(tag), flag=flag(tag),
                      continent=CONT_NAME.get(cont, cont), states=st_list, provs=provs,
                      others=others, nb=[dict(tag=o, name=COUNTRIES[by_tag[o]][1], colour=colour(o))
                                         for o in sorted(nb, key=nb.get)],
                      cities=cities, politics=politics(tag, loc), parts=parts)
        text = json.dumps(nation, ensure_ascii=False, separators=(",", ":"))
        (OUT / "n" / f"{tag}.json").write_text(text, encoding="utf-8")
        index.append(dict(tag=tag, name=c[1], colour=colour(tag), continent=nation["continent"],
                          flag=flag(tag, medium=True), states=len(mine), provinces=len(own),
                          cities=len(cities), area=int(sum(int(size[i]) for i in own)),
                          v=hashlib.sha1(text.encode()).hexdigest()[:10]))

    # the world in country colours for the start page, with borders between countries
    fy = (np.arange(WORLD[1]) * H // WORLD[1])
    fx = (np.arange(WORLD[0]) * W // WORLD[0])
    o = owner_px[fy][:, fx]
    k = kind[lab][fy][:, fx]
    pal = np.array([[int(v) for v in bytes.fromhex(colour(t)[1:])] for t in tags] + [[0, 0, 0]], np.uint8)
    img = pal[np.where(o >= 0, o, len(tags))]
    sea, lake = np.array([168, 190, 205], np.uint8), np.array([150, 180, 205], np.uint8)
    img[k == 0] = sea
    img[k == 2] = lake
    edge = np.zeros(o.shape, bool)
    edge[:, 1:] |= o[:, 1:] != o[:, :-1]
    edge[1:] |= o[1:] != o[:-1]
    land = k == 1
    img[edge & land] = (img[edge & land] * 0.55).astype(np.uint8)
    Image.fromarray(img).save(OUT / "world.png", optimize=True)
    iy = (np.arange(IDS[1]) * H // IDS[1]) + H // IDS[1] // 2
    ix = (np.arange(IDS[0]) * W // IDS[0]) + W // IDS[0] // 2
    ids = owner_px[iy][:, ix]
    ids = np.where(ids >= 0, ids + 1, 0).astype(np.uint8)
    subtypes = {ideo: [[k, nm, desc] for k, nm, desc in ideologies.SUBTYPES[ideo]] for ideo, _ in IDEOLOGY_NAMES}
    # tags a nation not on the map yet may not take (Earth's), and ours that own no land
    earth = [ln.split("\t")[0] for ln in Path("source/vanilla/index/tags.txt").read_text(encoding="utf-8").splitlines()
             if ln and not ln.startswith("#")]
    known = {v[0]: v[1] for v in COUNTRIES.values() if v[0] not in tindex}
    json.dump(dict(built=__import__("datetime").date.today().isoformat(), w=W, h=H,
                   terrains=TERRAINS, ideologies=IDEOLOGY_NAMES, subtypes=subtypes, earth=earth, known=known,
                   nations=index,
                   ids=dict(w=IDS[0], h=IDS[1], tags=tags, px=b64z(ids))),
              open(OUT / "index.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    total = sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file())
    print(f"wrote {OUT}: {len(tags)} nations, {sum(len(json.loads((OUT / 'n' / (t + '.json')).read_text())['parts']) for t in tags)} "
          f"parts, {total / 1e6:.1f} MB; largest part {biggest[1]}")


if __name__ == "__main__":
    main()
