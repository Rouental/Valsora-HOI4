"""Impassable states on the Gazetteer (2026-10-22, the author: "There should be a way to mark states as impassible on
the gazeteer"): HOI4's `impassable = yes` with `force_link_ownership_to`, as the base game's Sahara; the map's own are
the author's red areas (scripts/areas.py).

The page, on Mustawi (six of its twelve states impassable in the game, its map tools open): the State tab's Impassable
box shows the game's now (facts_export.py's `impassable`, the built state files') until a choice is kept as
`impassable`, true or false; impassable states are hatched on the map, in the key and on the status line. One of the
map's untick to passable, a passable state ticked, the capital ticked (kept passable, with a warning), a state that
would be left with no passable state beside it (Rouental's islands) and one whose mark would cut a state of the map's
off (warned, kept passable), "Use the map's". The file of every nation, a few broken values put in, imported into a
folder of the test's own (GAZETTEER_DIR, never source/gazetteer/): only true and false kept. The build's rule
(build_mod.impassable_states, called directly on the last build's map) on the imported facts gives what the page
showed, with a note for each state kept passable; on the facts in source/gazetteer/ (none sets it) the map's alone.
The export's defaults are the built files'. Desktop and phone.

    python3 scripts/facts_export.py          # after a build: the map data the page reads
    python3 tests/gazetteer/impassable.py    # PROBLEMS: none, screenshots in work/gazetteer_test/shots/
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness as H  # noqa: E402
from harness import wait_doc, open_nation, make_password, unfold  # noqa: E402

check = H.Checks()
SCRIPTS = H.ROOT / "scripts"
TAG, NAME = "MST", "Mustawi"

# the states the test marks, found on the page from the export (by index into the nation's states)
FIND = """() => {
  const N = app.N, cap = capitalState(), adj = s => [...N.stateAdj[s]];
  const imp = [...N.states.keys()].filter(s => N.impGame[s]);
  // a passable state that is the only passable one beside one of the map's impassable states: marking it would cut it off
  const blocks = [...N.states.keys()].filter(s => !N.impGame[s] && s !== cap
    && imp.some(t => adj(t).filter(u => !N.impGame[u]).length === 1 && N.stateAdj[t].has(s)));
  const pass = [...N.states.keys()].find(s => !N.impGame[s] && s !== cap && !blocks.includes(s)
    && adj(s).some(t => !N.impGame[t]));
  return { imp, pass, cap, block: blocks[0] === undefined ? null : blocks[0], keys: N.stateKey };
}"""
# is a state hatched in the land's picture: two pixels well inside it (no line, no river, the selection's outline away),
# one on a hatch line and one off it
HATCHED = """s => {
  const N = app.N, P = curPart(), w = P.w, d = P.img.data;
  const ins = j => { const v = P.px[j]; return v >= 2 && v < N.nOwn + 2 && N.prov[v - 2].s === s; };
  let a = -1, b = -1;
  for (let i = w + 1; i < P.px.length - w - 1 && (a < 0 || b < 0); i++) {
    if (!ins(i) || !ins(i - 1) || !ins(i + 1) || !ins(i - w) || !ins(i + w) || P.edge[i] || P.rv[i]) continue;
    const k = (i % w + ((i / w) | 0)) % 6;
    if (k === 0 && a < 0) a = i; else if (k === 3 && b < 0) b = i;
  }
  return a < 0 || b < 0 ? null : [0, 1, 2].some(c => d[a * 4 + c] !== d[b * 4 + c]);
}"""


def state_tab(page, s):
    page.evaluate("s => selectState(s, -1)", s)
    page.click("[data-tab=state]")
    page.wait_for_selector("#st-imp")
    time.sleep(0.3)


def box(page):
    return page.evaluate("""() => { const b = document.getElementById('st-imp'), f = b && b.closest('.field');
        const sec = b && b.closest('.sec');
        return b && { on: b.checked, set: f.classList.contains('set'), text: sec.innerText,
                      warn: (sec.querySelector('.warn') || {}).textContent || '' }; }""")


def tick(page):
    page.click("label[for=st-imp]")   # the line is the label: a tap anywhere on it
    time.sleep(0.4)


def owner(b, url, size):
    label = f"{size[0]}"
    ctx, page, errs = H.new_page(b, size, "window.__me = {id: 'u_owner', name: 'The Author', isOwner: true};")
    page.goto(url)
    page.wait_for_selector(".nrow", timeout=20000)
    page.wait_for_selector("#owner:not([hidden])", timeout=8000)
    time.sleep(0.4)
    unfold(page, "Passwords")
    make_password(page, NAME, TAG)
    open_nation(page, NAME, TAG)
    page.wait_for_function("app.N.K", timeout=5000)
    base = f"n/{TAG}/{page.evaluate('app.N.K')}"
    f = page.evaluate(FIND)
    keys = f["keys"]
    check(len(f["imp"]) == 6 and f["pass"] is not None, f"{label}: {NAME}'s states: {f}")
    out = {"find": f}

    # ---- one of the map's impassable states: ticked by default, hatched, untick to passable
    s = f["imp"][0]
    state_tab(page, s)
    v = box(page)
    check(v and v["on"] and not v["set"] and "Map default: impassable" in v["text"], f"{label}: the map's impassable state: {v}")
    check("No unit can enter it" in v["text"], f"{label}: no explanation under the box: {v and v['text'][:200]}")
    check(page.evaluate(HATCHED, s) is True, f"{label}: the map's impassable state isn't hatched")
    legend = page.inner_text("#legend")
    check("Impassable" in legend, f"{label}: the key has no Impassable: {legend}")
    page.screenshot(path=str(H.SHOTS / f"impassable_{label}_default.png"))
    tick(page)
    st = wait_doc(page, f"{base}/states", lambda d: (d.get(keys[s]) or {}).get("impassable") is False)
    check(st is not None, f"{label}: unticking wasn't saved as impassable false: {st}")
    v = box(page)
    check(v and not v["on"] and v["set"], f"{label}: after unticking: {v}")
    check(page.evaluate(HATCHED, s) is False, f"{label}: a state made passable is still hatched")
    out["unticked"] = keys[s]

    # ---- a passable state ticked
    p = f["pass"]
    state_tab(page, p)
    v = box(page)
    check(v and not v["on"] and not v["set"] and "Map default: passable" in v["text"], f"{label}: a passable state: {v}")
    tick(page)
    st = wait_doc(page, f"{base}/states", lambda d: (d.get(keys[p]) or {}).get("impassable") is True)
    check(st is not None, f"{label}: ticking wasn't saved as impassable true")
    v = box(page)
    check(v and v["on"] and v["set"] and not v["warn"] and "impassable in the game" in v["text"], f"{label}: after ticking: {v}")
    check(page.evaluate(HATCHED, p) is True, f"{label}: a state marked impassable isn't hatched")
    x, y = page.evaluate("""s => { const g = app.N.states[s].label, q = gToScreen(g[0], g[1]);
        const r = document.getElementById('map').getBoundingClientRect(); return [r.left + q[0], r.top + q[1]]; }""", p)
    page.mouse.move(x, y)
    time.sleep(0.2)
    check("impassable" in page.inner_text("#status"), f"{label}: the status line doesn't say impassable: {page.inner_text('#status')}")
    page.screenshot(path=str(H.SHOTS / f"impassable_{label}_marked.png"))

    # ---- the capital: kept passable, with a warning
    c = f["cap"]
    state_tab(page, c)
    tick(page)
    st = wait_doc(page, f"{base}/states", lambda d: (d.get(keys[c]) or {}).get("impassable") is True)
    v = box(page)
    check(st is not None and v["on"] and "capital" in v["warn"], f"{label}: the capital ticked: {v}")
    check(not page.evaluate("s => impassableNow().set.has(s)", c), f"{label}: the capital would be impassable")
    check(page.evaluate(HATCHED, c) is False, f"{label}: the capital is hatched")
    # "Use the map's" takes the choice away
    page.click("#pane-state button:has-text(\"Use the map's\")")
    time.sleep(0.4)
    st = wait_doc(page, f"{base}/states", lambda d: "impassable" not in (d.get(keys[c]) or {}))
    check(st is not None and not box(page)["set"], f"{label}: Use the map's didn't take the choice away: {st and st.get(keys[c])}")

    # ---- a state whose mark would leave one of the map's without a passable state beside it
    if f["block"] is not None:
        k = f["block"]
        state_tab(page, k)
        tick(page)
        v = box(page)
        check(v["on"] and "beside it" in v["warn"], f"{label}: a state cutting one of the map's off: {v}")
        check(not page.evaluate("s => impassableNow().set.has(s)", k), f"{label}: the cutting state would be impassable")
        page.screenshot(path=str(H.SHOTS / f"impassable_{label}_blocks.png"))
    out["mst"] = page.evaluate("() => ({ set: [...impassableNow().set].map(s => app.N.stateKey[s]).sort(), "
                               "why: [...impassableNow().why].map(([s, r]) => [app.N.stateKey[s], r[0]]) })")

    # ---- Rouental: an island state of its own, with no state beside it
    page.click("#back")
    time.sleep(0.4)
    make_password(page, "Rouental", "ROU")
    open_nation(page, "Rouental", "ROU")
    page.wait_for_function("app.N.K", timeout=5000)
    rbase = f"n/ROU/{page.evaluate('app.N.K')}"
    isle = page.evaluate("() => [...app.N.states.keys()].find(s => !app.N.stateAdj[s].size && s !== capitalState())")
    check(isle is not None, f"{label}: no island state on Rouental")
    if isle is not None:
        page.evaluate("s => locate(...app.N.states[s].label)", isle)
        state_tab(page, isle)
        tick(page)
        rk = page.evaluate("s => app.N.stateKey[s]", isle)
        st = wait_doc(page, f"{rbase}/states", lambda d: (d.get(rk) or {}).get("impassable") is True)
        v = box(page)
        check(st is not None and v["on"] and "No passable state of yours borders it" in v["warn"], f"{label}: the island: {v}")
        out["isle"] = rk
        page.screenshot(path=str(H.SHOTS / f"impassable_{label}_island.png"))

    # ---- every nation in a file
    page.click("#back")
    time.sleep(0.4)
    page.click("#owner button:has-text('Save every nation as a file')")
    page.wait_for_function("window.__saved && window.__saved.filename.includes('all')", timeout=20000)
    out["all"] = json.loads(page.evaluate("window.__saved.data"))
    ctx.close()
    return errs, out


def built(res):
    """the file, with a few broken values put in, imported into a folder of the test's own, and the build's rule on it"""
    tmp = Path(tempfile.mkdtemp(prefix="impassable_", dir=H.WORK))
    try:
        _built(res, tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


BUILD_RULE = r"""
import json, re, sys
from pathlib import Path
sys.path.insert(0, "scripts")
import numpy as np
import gazetteer, build_mod
rj = json.load(open("work/regions.json"))
p = np.load("work/provinces.npz"); reg = np.load("work/regions.npz")
caps = {}
for f in Path("build/valsora_test/history/countries").glob("*.txt"):
    caps[f.name[:3]] = int(re.search(r"^capital = (\d+)", f.read_text(encoding="utf-8-sig"), re.M).group(1)) - 1
G, notes = gazetteer.load(), []
gfacts = gazetteer.state_facts(G, p["prov"], reg["state_of"], rj["owners"], notes, reg["anchor"], rj["states"], reg["size"])
names = [f"State {s + 1}" for s in range(len(rj["owners"]))]
is_cap = lambda s: caps.get(rj["owners"][s]) == s
imp, link = build_mod.impassable_states(set(rj["impassable"]), gfacts, rj["owners"], rj["adjacency"], reg["state_of"],
                                        is_cap, names, notes)
key = lambda s: gazetteer.anchor_key(reg["anchor"], max(rj["states"][s], key=lambda i: (reg["size"][i], -i)))
own = lambda t: sorted(key(s) for s in imp if rj["owners"][s] == t and not is_cap(s))
print(json.dumps({"MST": own("MST"), "ROU": own("ROU"), "notes": notes, "base": sorted(rj["impassable"]) == sorted(imp),
                  "linked": all(s in link and link[s] not in imp and rj["owners"][link[s]] == rj["owners"][s]
                                for s in imp if not is_cap(s)), "key_of": {key(s): s + 1 for s in range(len(rj["owners"]))}}))
"""


def _built(res, tmp):
    allf = res["all"]
    st = allf["nations"][TAG]["facts"]["states"]
    # broken values: a string, a number, null; and a state of nothing but a broken one, which leaves no state facts
    lone = next(k for k in res["find"]["keys"] if k not in st)
    st[lone] = {"impassable": "yes"}
    other = next(k for k in st if (st[k] or {}).get("impassable") is True)
    st[other] = {**st[other], "name": "Test State"}
    allf["nations"][TAG]["facts"]["states"][res["find"]["keys"][res["find"]["cap"]]] = {"impassable": 1, "name": "Capital Test"}
    (tmp / "all.json").write_text(json.dumps(allf, ensure_ascii=False), encoding="utf-8")
    gdir = tmp / "gazetteer"
    env = {**os.environ, "GAZETTEER_DIR": str(gdir), "GAZETTEER_FLAGS": str(tmp / "flags")}
    r = subprocess.run([sys.executable, "scripts/gazetteer.py", "import", str(tmp / "all.json")], cwd=H.ROOT, env=env,
                       capture_output=True, text=True)
    check(r.returncode == 0, f"the import failed: {r.stderr[-800:]}")
    M = json.loads((gdir / f"{TAG}.json").read_text(encoding="utf-8"))["states"]
    kept = {k: v["impassable"] for k, v in M.items() if "impassable" in v}
    want = {k: v["impassable"] for k, v in st.items() if isinstance((v or {}).get("impassable"), bool)}
    check(kept == want and all(isinstance(v, bool) for v in kept.values()), f"the import's impassable: {kept}, the page's {want}")
    check(lone not in M, f"a state of a broken value alone was kept: {M.get(lone)}")
    check(M.get(res["find"]["keys"][res["find"]["cap"]]) == {"name": "Capital Test"}, f"the capital's broken value: {M.get(res['find']['keys'][res['find']['cap']])}")
    check(M[other].get("name") == "Test State" and M[other].get("impassable") is True, f"a state's other facts: {M[other]}")
    R = json.loads((gdir / "ROU.json").read_text(encoding="utf-8")).get("states", {})
    check((R.get(res.get("isle")) or {}).get("impassable") is True, f"Rouental's island: {R.get(res.get('isle'))}")

    r = subprocess.run([sys.executable, "-c", BUILD_RULE], cwd=H.ROOT, env=env, capture_output=True, text=True)
    check(r.returncode == 0, f"the build's rule failed: {r.stderr[-1500:]}")
    if r.returncode:
        return
    o = json.loads(r.stdout)
    check(o["MST"] == res["mst"]["set"], f"the build's impassable states of {NAME}: {o['MST']}, the page's {res['mst']['set']}")
    check(o["linked"], "an impassable state of the build isn't linked to a passable state of its owner")
    sid = lambda k: o["key_of"][k]
    why = dict(res["mst"]["why"])
    for k, reason in why.items():
        hit = [n for n in o["notes"] if n.startswith(f"Gazetteer: state {sid(k)} (") and "can't be impassable" in n]
        words = {"capital": "capital", "alone": "borders it", "blocks": "beside it"}[reason]
        check(hit and words in hit[0], f"no note for state {sid(k)} ({reason}): {o['notes']}")
    if res.get("isle"):
        check(any(n.startswith(f"Gazetteer: state {sid(res['isle'])} (") and "no passable state of ROU borders it" in n
                  for n in o["notes"]), f"no note for Rouental's island: {o['notes']}")
        check(res["isle"] not in o["ROU"], "Rouental's island would be impassable")
    check(res["unticked"] not in o["MST"], "the state made passable is still impassable in the build")


def without_field():
    """the facts in source/gazetteer/ (none sets it): the map's impassable states alone, every one linked"""
    r = subprocess.run([sys.executable, "-c", BUILD_RULE], cwd=H.ROOT, capture_output=True, text=True)
    check(r.returncode == 0, f"the rule without the field failed: {r.stderr[-800:]}")
    if not r.returncode:
        o = json.loads(r.stdout)
        check(o["base"] and o["linked"] and not [n for n in o["notes"] if "impassable" in n],
              f"without the field: the map's {o['base']}, linked {o['linked']}, notes {[n for n in o['notes'] if 'impassable' in n]}")


def export():
    """the export's defaults are the built state files' impassable states"""
    files = {}
    for f in (H.ROOT / "build/valsora_test/history/states").glob("*.txt"):
        t = f.read_text(encoding="utf-8-sig")
        files[int(re.search(r"\bid = (\d+)", t).group(1))] = bool(re.search(r"^\timpassable = yes$", t, re.M))
    n = 0
    for f in sorted((H.DATA / "n").glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        want = [s["key"] for s in d["states"] if files.get(s["id"])]
        check(d.get("impassable", []) == want, f"{f.stem}: the export's impassable {d.get('impassable')}, the build's {want}")
        n += len(want)
    check(n == sum(files.values()) and n > 0, f"the export has {n} impassable states, the build {sum(files.values())}")


def main():
    H.build_site()
    export()
    with H.Server(8775) as server, sync_playwright() as p:
        b = p.chromium.launch(executable_path=H.CHROMIUM)
        for i, size in enumerate(((1440, 900), (390, 844))):
            errs, res = owner(b, server.url, size)
            check(not errs, f"{size}: console errors {errs[:5]}")
            if i == 0:
                H.dump(res["all"], "impassable_saved_all.json")
                built(res)
        b.close()
    without_field()
    return check.report()


if __name__ == "__main__":
    sys.exit(main())
