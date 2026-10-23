"""Impassable borders on the Gazetteer (2026-10-22, the author: "Yes, add the impassable borders tool too"): HOI4's
adjacencies.csv rows of type impassable between two provinces, as the base game's Himalayas. HOI4 has no impassable
province: impassable states are the other way (tests/gazetteer/impassable.py).

The page, on Rouental (its map tools open): the Impassable borders tool (B) clicks a border between two provinces to
mark it, again to open it; a border of two of its own provinces and one with a neighbour's; the line drawn along the
edge on the map, in the key, on the status line and in the Map tab's list; one of the game's (the site's copy of the
export given one, as an import would) shown marked, opened (kept as false) and marked again. A click on no border says
so. On Belka (map tools closed) there is no such tool. The file of every nation, a few broken keys put in, imported into
a folder of the test's own (GAZETTEER_DIR, never source/gazetteer/): only true and false on two pixels kept, sorted. The
build's function (gazetteer.borders, called directly on the last build's map) gives the page's borders as provinces, and
leaves out with a note a border on water, one between provinces that don't touch, and a ring of walls round a province
with no coast; on the facts in source/gazetteer/ (none has borders) nothing. Desktop and phone.

    python3 scripts/facts_export.py       # after a build: the map data the page reads
    python3 tests/gazetteer/borders.py    # PROBLEMS: none, screenshots in work/gazetteer_test/shots/
"""
import base64
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import zlib
from pathlib import Path

import numpy as np
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness as H  # noqa: E402
from harness import wait_doc, open_nation, make_password, unfold  # noqa: E402

check = H.Checks()

# a clean stretch of border in the shown part, two pixels high on both sides, between two of the nation's provinces
# (own) or one of its and a neighbour's: its labels and the game pixel of its left side
EDGE = """([own, skip]) => {
  const N = app.N, P = curPart(), w = P.w, o = N.nOwn + 2;
  for (let y = 40; y < P.h - 40; y++) for (let x = 40; x < w - 40; x++) {
    const i = y * w + x, a = P.px[i], b = P.px[i + 1];
    if (a < 2 || b < 2 || a === b || a >= o || (own ? b >= o : b < o) || skip.includes(pairOf(a, b))) continue;
    if (P.px[i - w] !== a || P.px[i + w] !== a || P.px[i - w + 1] !== b || P.px[i + w + 1] !== b) continue;
    if (P.px[i - 1] !== a || P.px[i + 2] !== b) continue;
    return { a, b, p: pairOf(a, b), x, y, gx: mod(P.x0 + x, W), gy: P.y0 + y, key: wallKeyOf(a, b) };
  }
  return null;
}"""
# the screen point of the middle of that edge, the map centred on it
POINT = """e => { locate(e.gx, e.gy); const q = toScreen(e.x + 1, e.y + 0.5), r = document.getElementById('map').getBoundingClientRect();
  return [r.left + q[0], r.top + q[1]]; }"""
# the colour drawn there on the map's canvas, and the wall colour
PIXEL = """([sx, sy]) => { const c = document.getElementById('map'), r = c.getBoundingClientRect(), d = window.devicePixelRatio || 1;
  const v = c.getContext('2d').getImageData(Math.round((sx - r.left) * d), Math.round((sy - r.top) * d), 1, 1).data;
  return [[v[0], v[1], v[2]], rgb(css('--wall'))]; }"""


def default_wall():
    """the site's copy of Rouental's map data given one impassable border of the game's (as the export gives the built
    rows): a clean border of two of its own provinces, far from the first one the test marks"""
    f = H.SITE / "n" / "ROU.json"
    n = json.loads(f.read_text(encoding="utf-8"))
    P = n["parts"][0]
    px = np.frombuffer(zlib.decompress(base64.b64decode(P["px"])), "<u2").reshape(P["h"], P["w"]).astype(int)
    own = len(n["provs"]) + 2
    for y in range(P["h"] - 60, 60, -1):
        for x in range(P["w"] - 60, 60, -1):
            a, b = px[y, x], px[y, x + 1]
            if 2 <= a < own and 2 <= b < own and a != b and px[y - 1, x] == a and px[y + 1, x] == a and px[y - 1, x + 1] == b \
                    and px[y + 1, x + 1] == b and px[y, x - 1] == a and px[y, x + 2] == b:
                n["walls"] = [sorted([int(a) - 2, int(b) - 2])]
                f.write_text(json.dumps(n, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
                return {"pair": n["walls"][0], "x": x, "y": y, "gx": (P["x0"] + x) % 5120, "gy": P["y0"] + y}
    return None


def borders_doc(page, base):
    return (H.doc(page, f"{base}/provinces") or {}).get("borders") or {}


def click(page, e):
    x, y = page.evaluate(POINT, e)
    page.mouse.click(x, y)
    time.sleep(0.45)
    return x, y


def run(b, url, size, dflt):
    label = f"{size[0]}"
    ctx, page, errs = H.new_page(b, size, "window.__me = {id: 'u_owner', name: 'The Author', isOwner: true};")
    page.goto(url)
    page.wait_for_selector(".nrow", timeout=20000)
    page.wait_for_selector("#owner:not([hidden])", timeout=8000)
    time.sleep(0.4)
    unfold(page, "Passwords")

    # ---- Belka (map tools closed): no tool
    make_password(page, "Belka", "BKA")
    open_nation(page, "Belka", "BKA")
    check(page.evaluate("document.querySelector('[data-tool=wall]').hidden"), f"{label}: the Impassable borders tool on a closed nation")
    page.click("#back")
    time.sleep(0.4)

    make_password(page, "Rouental", "ROU")
    open_nation(page, "Rouental", "ROU")
    page.wait_for_function("app.N.K", timeout=5000)
    base = f"n/ROU/{page.evaluate('app.N.K')}"
    check(not page.evaluate("document.querySelector('[data-tool=wall]').hidden"), f"{label}: no Impassable borders tool on Rouental")
    page.keyboard.press("b")
    time.sleep(0.3)
    check(page.evaluate("app.ui.tool") == "wall", f"{label}: B didn't pick the tool")
    hint = page.inner_text("#subtools .hinttext")
    check("Himalayas" in hint and "no unit can cross" in hint, f"{label}: the tool's hint: {hint}")
    dp = page.evaluate("([a, b]) => pairOf(a + 2, b + 2)", dflt["pair"]) if dflt else None
    check(dp is not None and page.evaluate("p => wallsNow().has(p) && app.N.wallDefault.has(p)", dp), f"{label}: the game's border isn't shown marked")

    # ---- a border of two of Rouental's own provinces: marked, drawn, opened
    e = page.evaluate(EDGE, [True, [dp]])
    check(e is not None and e["key"], f"{label}: no clean border between two of Rouental's provinces: {e}")
    if not e:
        ctx.close()
        return errs, None
    x, y = click(page, e)
    d = wait_doc(page, f"{base}/provinces", lambda v: (v.get("borders") or {}).get(e["key"]) is True)
    check(d is not None, f"{label}: the border wasn't saved: {borders_doc(page, base)}")
    check(page.evaluate("p => wallsNow().has(p)", e["p"]) and page.evaluate("() => wallSegs(curPart()).length") > 0,
          f"{label}: the marked border isn't drawn")
    got, want = page.evaluate(PIXEL, [x, y])
    check(sum(abs(a - b) for a, b in zip(got, want)) < 60, f"{label}: the map at the border is {got}, not the wall colour {want}")
    check("Impassable border" in page.inner_text("#legend") or not page.evaluate("app.ui.legend"), f"{label}: the key: {page.inner_text('#legend')}")
    check("Impassable border:" in page.inner_text("#status"), f"{label}: the message after marking: {page.inner_text('#status')}")
    page.mouse.move(x + 1, y)
    time.sleep(0.2)
    check("impassable: a click opens it" in page.inner_text("#status"), f"{label}: the status line over the border: {page.inner_text('#status')}")
    page.screenshot(path=str(H.SHOTS / f"borders_{label}_marked.png"))
    click(page, e)
    d = wait_doc(page, f"{base}/provinces", lambda v: e["key"] not in (v.get("borders") or {}))
    check(d is not None and not page.evaluate("p => wallsNow().has(p)", e["p"]), f"{label}: opening didn't take the mark away: {borders_doc(page, base)}")
    click(page, e)   # marked again, for the import
    wait_doc(page, f"{base}/provinces", lambda v: (v.get("borders") or {}).get(e["key"]) is True)

    # ---- a border with a neighbour's province
    n_ = page.evaluate(EDGE, [False, [dp, e["p"]]])
    check(n_ is not None and n_["key"], f"{label}: no clean border with a neighbour: {n_}")
    if n_:
        click(page, n_)
        d = wait_doc(page, f"{base}/provinces", lambda v: (v.get("borders") or {}).get(n_["key"]) is True)
        check(d is not None, f"{label}: the border with a neighbour wasn't saved: {borders_doc(page, base)}")
        check(" – " in page.inner_text("#status"), f"{label}: the message names both sides: {page.inner_text('#status')}")

    # ---- the game's own: opened (false), marked again (true)
    if dp is not None:
        g = {**dflt, "p": dp, "key": page.evaluate("p => wallKeyOf(Math.floor(p / 65536), p % 65536)", dp)}
        check(page.evaluate("s => { const g = wallSpot(s); return !!g; }", dp), f"{label}: Show finds no spot on the game's border")
        page.click("[data-tab=map]")
        time.sleep(0.4)
        sec = page.inner_text("#pane-map")
        check("impassable borders" in sec.lower() and "in the game" in sec.lower(), f"{label}: the Map tab's list: {sec[-400:]}")
        click(page, g)
        d = wait_doc(page, f"{base}/provinces", lambda v: (v.get("borders") or {}).get(g["key"]) is False)
        check(d is not None and not page.evaluate("p => wallsNow().has(p)", dp), f"{label}: the game's border wasn't opened as false: {borders_doc(page, base)}")
        click(page, g)
        d = wait_doc(page, f"{base}/provinces", lambda v: (v.get("borders") or {}).get(g["key"]) is True)
        check(d is not None, f"{label}: the game's border marked again isn't kept as true: {borders_doc(page, base)}")
        page.screenshot(path=str(H.SHOTS / f"borders_{label}_list.png"))

    # ---- a click away from any border
    page.evaluate("() => { const P = curPart(); app.view = { s: 3, ox: -200, oy: -200 }; requestDraw(); }")
    time.sleep(0.2)
    r = page.evaluate("() => { const r = document.getElementById('map').getBoundingClientRect(); return [r.left + 30, r.top + r.height / 2]; }")
    page.mouse.click(*r)
    time.sleep(0.3)
    check("Click on a border" in page.inner_text("#status"), f"{label}: a click on no border: {page.inner_text('#status')}")

    # ---- every nation in a file
    page.click("#back")
    time.sleep(0.4)
    page.click("#owner button:has-text('Save every nation as a file')")
    page.wait_for_function("window.__saved && window.__saved.filename.includes('all')", timeout=20000)
    allf = json.loads(page.evaluate("window.__saved.data"))
    ctx.close()
    return errs, {"all": allf, "keys": [e["key"], n_ and n_["key"], dp is not None and g["key"]]}


BUILD = r"""
import json, sys
sys.path.insert(0, "scripts")
import numpy as np
import gazetteer
rj = json.load(open("work/regions.json"))
p = np.load("work/provinces.npz"); reg = np.load("work/regions.npz")
lab, kind = p["prov"], p["kind"]
coastal = np.zeros(len(kind), bool)
for a, b, _ in rj["adjacency"]:
    if {int(kind[a]), int(kind[b])} == {0, 1}:
        coastal[a if kind[a] == 1 else b] = True
G = gazetteer.load()
if sys.argv[1:] == ["--without"]:   # the facts without the field (2026-10-23: Rouental's page has nine walls of its own)
    for f in G.values():
        f.pop("borders", None)
extra = json.loads(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1] != "--without" else {}
if extra:   # borders put in by the test: a ring round an inland province of Rouental's, and one far apart
    G.setdefault("ROU", {}).setdefault("borders", {}).update(extra)
notes = []
walls = gazetteer.borders(G, lab, kind, reg["state_of"], rj["owners"], rj["adjacency"], set(), coastal, reg["anchor"], notes)
print(json.dumps({"walls": [[a, b, t] for a, b, t in walls], "notes": notes}))
"""


def built(res):
    tmp = Path(tempfile.mkdtemp(prefix="borders_", dir=H.WORK))
    try:
        _built(res, tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _built(res, tmp):
    allf = res["all"]
    pv = allf["nations"]["ROU"]["facts"]["provinces"]
    good = dict(pv["borders"])
    k0 = res["keys"][0]
    a, b = k0.split("|")
    pv["borders"].update({"5,5": True, "a,b|c,d": True, f"{a}|{a}": True, f"{a}|9,99999": True,
                          f"{b}|{a}": "yes", f"{b}|{a}x": True})   # broken: no pair, not numbers, one place, off the map, not a yes/no
    (tmp / "all.json").write_text(json.dumps(allf, ensure_ascii=False), encoding="utf-8")
    gdir = tmp / "gazetteer"
    env = {**os.environ, "GAZETTEER_DIR": str(gdir), "GAZETTEER_FLAGS": str(tmp / "flags")}
    r = subprocess.run([sys.executable, "scripts/gazetteer.py", "import", str(tmp / "all.json")], cwd=H.ROOT, env=env,
                       capture_output=True, text=True)
    check(r.returncode == 0, f"the import failed: {r.stderr[-800:]}")
    R = json.loads((gdir / "ROU.json").read_text(encoding="utf-8"))
    check(R.get("borders") == dict(sorted(good.items())), f"the import's borders: {R.get('borders')}, the page's {good}")
    check("borders" not in (R.get("provinces") or {}), "the borders landed among the provinces' facts")

    # the build's function on them; then with a ring of walls round an inland province, and a pair that doesn't touch
    sys.path.insert(0, str(H.ROOT / "scripts"))
    rj = json.loads((H.ROOT / "work/regions.json").read_text())
    p = np.load(H.ROOT / "work/provinces.npz")
    reg = np.load(H.ROOT / "work/regions.npz")
    lab, kind, anchor, state_of = p["prov"], p["kind"], reg["anchor"], reg["state_of"]
    key = lambda i: f"{int(anchor[i][1])},{int(anchor[i][0])}"
    at = lambda k: tuple(sorted(int(lab[int(v.split(",")[1]), int(v.split(",")[0])]) for v in k.split("|")))
    coast = set()
    nb = {}
    for x, y, _ in rj["adjacency"]:
        if {int(kind[x]), int(kind[y])} == {0, 1}:
            coast.add(x if kind[x] == 1 else y)
        nb.setdefault(x, set()).add(y)
        nb.setdefault(y, set()).add(x)
    rou = [i for i in range(len(kind)) if kind[i] == 1 and state_of[i] >= 0 and rj["owners"][state_of[i]] == "ROU"]
    marked = {i for k, v in R["borders"].items() if v for i in at(k)}   # (a ring round one of them would take its border too)
    inland = next(i for i in rou if i not in coast and all(kind[j] == 1 for j in nb[i]) and len(nb[i]) >= 3
                  and not (nb[i] | {i}) & marked)
    ring = {"|".join(sorted([key(inland), key(j)], key=lambda s: tuple(map(int, s.split(","))))): True for j in sorted(nb[inland])}
    far = next(j for j in rou if j not in nb[rou[0]] and j != rou[0])
    apart = {"|".join(sorted([key(rou[0]), key(far)], key=lambda s: tuple(map(int, s.split(","))))): True}
    sea = next(i for i in range(len(kind)) if kind[i] == 0)
    water = {"|".join(sorted([key(sea), key(rou[0])], key=lambda s: tuple(map(int, s.split(","))))): True}
    r = subprocess.run([sys.executable, "-c", BUILD], cwd=H.ROOT, env=env, capture_output=True, text=True)
    check(r.returncode == 0, f"the build's function failed: {r.stderr[-1500:]}")
    if r.returncode:
        return
    o = json.loads(r.stdout)
    want = sorted(at(k) for k, v in R["borders"].items() if v)
    check(sorted(tuple(w[:2]) for w in o["walls"]) == want and all(w[2] == ["ROU"] for w in o["walls"]) and not o["notes"],
          f"the build's borders: {o}, the page's {want}")
    r = subprocess.run([sys.executable, "-c", BUILD, json.dumps({**ring, **apart, **water})], cwd=H.ROOT, env=env,
                       capture_output=True, text=True)
    check(r.returncode == 0, f"the build's function failed with the ring: {r.stderr[-1500:]}")
    if r.returncode:
        return
    o = json.loads(r.stdout)
    got = {tuple(w[:2]) for w in o["walls"]}
    check(not got & {at(k) for k in ring} and set(want) <= got, f"the ring round province {inland + 1} wasn't left out: {sorted(got)}, the page's {want}, notes {o['notes']}")
    check(any(f"would wall off 1 province without a coast, at {key(inland)}" in n_ for n_ in o["notes"]), f"no note for the ring: {o['notes']}")
    check(any(f"at {k} left out: its provinces no longer touch" in n_ for k in apart for n_ in o["notes"]), f"no note for the pair apart: {o['notes']}")
    check(any(f"at {k} left out: it isn't between two land provinces" in n_ for k in water for n_ in o["notes"]), f"no note for the border on water: {o['notes']}")


def without_field():
    r = subprocess.run([sys.executable, "-c", BUILD, "--without"], cwd=H.ROOT, capture_output=True, text=True)
    check(r.returncode == 0, f"the function without the field failed: {r.stderr[-800:]}")
    if not r.returncode:
        o = json.loads(r.stdout)
        check(o == {"walls": [], "notes": []}, f"the facts without the field give borders: {o}")


def main():
    H.build_site()
    dflt = default_wall()
    check(dflt is not None, "no border of Rouental's own to give the site's copy as the game's")
    with H.Server(8777) as server, sync_playwright() as p:
        b = p.chromium.launch(executable_path=H.CHROMIUM)
        for i, size in enumerate(((1440, 900), (390, 844))):
            errs, res = run(b, server.url, size, dflt)
            check(not errs, f"{size}: console errors {errs[:5]}")
            if i == 0 and res:
                H.dump(res["all"], "borders_saved_all.json")
                built(res)
        b.close()
    without_field()
    return check.report()


if __name__ == "__main__":
    sys.exit(main())
