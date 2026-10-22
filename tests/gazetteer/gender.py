"""A character's gender on the Gazetteer (2026-10-21, night, the author: "we should be able to select the gender of
characters in the gazetteer. I noticed that Serelle currently seems to be considered male"): HOI4's `gender = female`
(or `male`) in a character's block; without one the game takes a character for a man.

The page: every character it lets a player fill in or change has Male / Female, showing the game's now (the export's,
facts_export.py) until a choice is kept as `gender`: Rouental's own characters (Roland to Female, Serelle, a woman in
the game, to Male, the communist leader the game made to Female), a general and a political advisor of the page's
own, a releasable's ruler and Carcarelle's (a releasable of the game's), and on Seigne (a generated ruler) the head of
state and a party leader. The file of every nation, imported into a folder of the test's own (GAZETTEER_DIR, never
source/gazetteer/): the import keeps each. The build's functions on it (called directly, not build_mod.py):
gazetteer.characters writes `gender = female` for the general and the advisor; gazetteer.leaders and
cultures.leaders for Seigne's ruler and party leader and for the releasables' rulers; game_character_names for
Rouental's communist; patch_characters puts the line in after Roland's name, turns Serelle's into `gender = male`
and her copy at the head of HMMLA (RLA_serelle_cahun) with her, and leaves Mahaut and her copy as they were. Without
the field, nothing of the facts already in source/gazetteer/ writes a gender line. facts_export.read_characters
reads the line back (a scratch copy of the built characters). Desktop and phone.

    python3 scripts/facts_export.py          # after a build: the map data the page reads
    python3 tests/gazetteer/gender.py        # PROBLEMS: none, screenshots in work/gazetteer_test/shots/
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
from harness import wait_doc, open_nation, pick, make_password, unfold  # noqa: E402

check = H.Checks()
SCRIPTS = H.ROOT / "scripts"


def people_tab(page):
    page.click("[data-tab=people]")
    time.sleep(0.35)


def site_genders():
    """the site's copy of Rouental's map data with the genders nations.py gives now (Serelle, Mahaut, Tara Blanchart),
    whatever the last build was: the page is to show the export's"""
    sys.path.insert(0, str(SCRIPTS))
    import nations
    women = set(re.findall(r"^\t(\w+) = \{\n\t\tname = \w+\n\t\tgender = female$", nations.ROU_CHARACTERS + nations.CHARACTERS, re.M))
    women |= {k for k, v in nations.GENDERS.items() if v == "female"}
    f = H.SITE / "n" / "ROU.json"
    n = json.loads(f.read_text(encoding="utf-8"))
    for c in n["characters"]:
        c["gender"] = "female" if c["id"] in women else c.get("gender", "male")
    f.write_text(json.dumps(n, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return {c["id"]: c["gender"] for c in n["characters"]}


def value(page, sel):
    return page.evaluate("s => { const e = document.querySelector(s); return e ? e.value : null; }", sel)


def owner(b, url, size, game):
    label = f"{size[0]}"
    ctx, page, errs = H.new_page(b, size, "window.__me = {id: 'u_owner', name: 'The Author', isOwner: true};")
    page.goto(url)
    page.wait_for_selector(".nrow", timeout=20000)
    page.wait_for_selector("#owner:not([hidden])", timeout=8000)
    time.sleep(0.4)
    unfold(page, "Passwords")
    make_password(page, "Rouental", "ROU")
    open_nation(page, "Rouental", "ROU")
    page.wait_for_function("app.N.K", timeout=5000)
    base = f"n/ROU/{page.evaluate('app.N.K')}"

    # ---- Rouental's own characters: the game's gender shown, a choice kept
    people_tab(page)
    for cid, g in game.items():
        check(value(page, f"#pp-g-{cid}-gender") == g, f"{label}: {cid}'s gender shows {value(page, f'#pp-g-{cid}-gender')}, the game's is {g}")
    lab = page.evaluate("document.querySelector('label[for=\"pp-g-ROU_serelle_cahun-gender\"]').textContent")
    check(lab == "Gender", f"{label}: the gender field's label: {lab!r}")
    pick(page, "#pp-g-ROU_roland_cahun-gender", "female")
    pick(page, "#pp-g-ROU_serelle_cahun-gender", "male")
    pick(page, "#pp-g-ROU_leader_leninism-gender", "female")
    pp = wait_doc(page, f"{base}/people", lambda v: (v.get("ch-ROU_roland_cahun") or {}).get("gender") == "female"
                  and (v.get("ch-ROU_serelle_cahun") or {}).get("gender") == "male" and (v.get("ch-ROU_leader_leninism") or {}).get("gender") == "female")
    check(pp is not None, f"{label}: Roland's, Serelle's and the communist's genders weren't saved: {pp}")
    check(page.evaluate("document.getElementById('pp-g-ROU_roland_cahun-gender').closest('.field').classList.contains('set')"),
          f"{label}: Roland's gender isn't marked as changed")

    # ---- a general and a political advisor of the page's own
    page.click("button:has-text('Add a character')")
    time.sleep(0.35)
    page.keyboard.type("Générale Test")
    pp = wait_doc(page, f"{base}/people", lambda v: any(k.startswith("c-") and x and x.get("name") == "Générale Test" for k, x in v.items()))
    cg = next(k for k, x in pp.items() if k.startswith("c-") and x and x.get("name") == "Générale Test")
    check(value(page, f"#pp-c-gender-{cg}") == "male", f"{label}: a new character isn't a man to begin with")
    pick(page, f"#pp-c-gender-{cg}", "female")
    page.click("button:has-text('Add a political advisor')")
    time.sleep(0.35)
    page.keyboard.type("Conseillère Test")
    pp = wait_doc(page, f"{base}/people", lambda v: any(k.startswith("c-") and x and x.get("name") == "Conseillère Test" for k, x in v.items()))
    ca = next(k for k, x in pp.items() if k.startswith("c-") and x and x.get("name") == "Conseillère Test")
    pick(page, f"#pp-c-gender-{ca}", "female")
    pp = wait_doc(page, f"{base}/people", lambda v: v[cg].get("gender") == "female" and v[ca].get("gender") == "female")
    check(pp is not None, f"{label}: the general's and the advisor's genders weren't saved: {pp and (pp.get(cg), pp.get(ca))}")
    page.evaluate("document.getElementById('pp-g-ROU_serelle_cahun-gender').scrollIntoView({block: 'center'})")
    time.sleep(0.3)
    page.screenshot(path=str(H.SHOTS / f"gender_{label}_people.png"))

    # ---- releasables: one of the page's own, and Carcarelle, the game's
    page.click("[data-tab=release]")
    time.sleep(0.4)
    check(value(page, "#rl-gender-g-CRL") == ((page.evaluate("app.N.relList.find(r => r.id === 'g-CRL').game.ruler") or {}).get("gender") or "male"),
          f"{label}: Carcarelle's ruler's gender isn't the game's")
    pick(page, "#rl-gender-g-CRL", "female")
    page.click("button:has-text('Add a releasable')")
    time.sleep(0.4)
    page.keyboard.type("Libre Test")
    rel = wait_doc(page, f"{base}/releasables", lambda v: any(k.startswith("rl-") and x and x.get("name") == "Libre Test" for k, x in v.items()))
    rid = next(k for k, x in rel.items() if k.startswith("rl-") and x and x.get("name") == "Libre Test")
    pick(page, f"#rl-gender-{rid}", "female")
    # its land: a state of Rouental's own, so the build makes it
    st = page.evaluate("() => app.N.states.findIndex((s, i) => !app.N.relOf.has(i))")
    page.evaluate("([id, s]) => { app.ui.relMode = 'add'; selectRel(id); paintRel(app.N.states[s].provs[0]); }", [rid, st])
    rel = wait_doc(page, f"{base}/releasables", lambda v: (v["g-CRL"].get("leader") or {}).get("gender") == "female"
                   and (v[rid].get("leader") or {}).get("gender") == "female" and v[rid].get("states"))
    check(rel is not None, f"{label}: the releasables' rulers' genders weren't saved: {rel and (rel.get('g-CRL'), rel.get(rid))}")
    page.evaluate("id => document.getElementById(id).scrollIntoView({block: 'center'})", f"rl-gender-{rid}")
    time.sleep(0.3)
    page.screenshot(path=str(H.SHOTS / f"gender_{label}_releasables.png"))

    # ---- Seigne: a generated ruler and a party leader
    page.click("#back")
    time.sleep(0.4)
    make_password(page, "Seigne", "SGN")
    open_nation(page, "Seigne", "SGN")
    page.wait_for_function("app.N.K", timeout=5000)
    sbase = f"n/SGN/{page.evaluate('app.N.K')}"
    people_tab(page)
    check(value(page, "#pp-ruler-gender") == "male", f"{label}: Seigne's ruler's gender: {value(page, '#pp-ruler-gender')}")
    pick(page, "#pp-ruler-gender", "female")
    check(value(page, "#pp-gender-democratic") is None, f"{label}: a party without a leader has a gender field")
    pick(page, "#pp-sub-democratic", "liberalism")
    time.sleep(0.3)
    pick(page, "#pp-gender-democratic", "female")
    pp = wait_doc(page, f"{sbase}/people", lambda v: (v.get("ruler") or {}).get("gender") == "female"
                  and (v.get("party-democratic") or {}).get("gender") == "female")
    check(pp is not None, f"{label}: Seigne's ruler's and party leader's genders weren't saved: {pp}")
    page.screenshot(path=str(H.SHOTS / f"gender_{label}_seigne.png"))

    # ---- every nation in a file
    page.click("#back")
    time.sleep(0.4)
    page.click("#owner button:has-text('Save every nation as a file')")
    page.wait_for_function("window.__saved && window.__saved.filename.includes('all')", timeout=20000)
    allf = json.loads(page.evaluate("window.__saved.data"))
    ctx.close()
    return errs, allf


def built(allf):
    """the file imported into a folder of the test's own, and the build's functions on what it holds"""
    tmp = Path(tempfile.mkdtemp(prefix="gender_", dir=H.WORK))
    try:
        _built(allf, tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _built(allf, tmp):
    gdir, fdir = tmp / "gazetteer", tmp / "flags"
    (tmp / "all.json").write_text(json.dumps(allf, ensure_ascii=False), encoding="utf-8")
    env = {**os.environ, "GAZETTEER_DIR": str(gdir), "GAZETTEER_FLAGS": str(fdir)}
    r = subprocess.run([sys.executable, "scripts/gazetteer.py", "import", str(tmp / "all.json")], cwd=H.ROOT, env=env,
                       capture_output=True, text=True)
    check(r.returncode == 0, f"the import failed: {r.stderr[-800:]}")
    R = json.loads((gdir / "ROU.json").read_text(encoding="utf-8"))
    S = json.loads((gdir / "SGN.json").read_text(encoding="utf-8"))
    gc, chars = R["people"]["game_characters"], R["people"]["characters"]
    check(gc["ROU_roland_cahun"].get("gender") == "female" and gc["ROU_serelle_cahun"].get("gender") == "male"
          and gc["ROU_leader_leninism"].get("gender") == "female", f"the import's game characters: {gc}")
    check([c.get("gender") for c in chars] == ["female", "female"], f"the import's characters: {chars}")
    check(R["game_releasables"]["CRL"]["leader"].get("gender") == "female", f"the import's Carcarelle: {R['game_releasables'].get('CRL')}")
    check([r_.get("leader", {}).get("gender") for r_ in R["releasables"]] == ["female"], f"the import's releasable: {R['releasables']}")
    check(S["people"]["ruler"].get("gender") == "female" and S["people"]["parties"]["democratic"].get("gender") == "female",
          f"the import's Seigne: {S.get('people')}")

    # the build's functions, as build_mod.py calls them, on the imported facts (in a fresh interpreter: GAZETTEER_DIR)
    code = r"""
import json, re, sys
sys.path.insert(0, "scripts")
import numpy as np
import gazetteer, nations, cultures, ideologies
G = gazetteer.load()
out = {}
of = ideologies.ideology_of()
genders = dict(nations.GENDERS)
named = dict(nations.NAMED_LEADERS)
gchars = gazetteer.game_characters(G)
out["copy"] = gchars.get("RLA_serelle_cahun")
loc, notes = {}, []
out["rou"] = gazetteer.patch_characters(nations.ROU_CHARACTERS, gchars, loc, {}, notes)
gazetteer.game_character_names(gchars, named, {}, nations.HAND_MADE, genders)
blocks, _, _ = cultures.leaders("ROU", "nonscio", nations.LEADERS["ROU"], of, set(), named, genders)
out["rou_leaders"] = "".join(blocks)
subs = gazetteer.leaders("SGN", nations.LEADERS.get("SGN", []), G.get("SGN"), False, named, {}, genders)
out["sgn_subs"] = subs
blocks, _, _ = cultures.leaders("SGN", "nonscio", subs, of, set(), named, genders)
out["sgn_leaders"] = "".join(blocks)
blocks, _, _ = gazetteer.characters("ROU", G.get("ROU"), {}, set(), cultures.unit_portraits("ROU", "nonscio"))
out["chars"] = "".join(blocks)
p = np.load("work/provinces.npz"); reg = np.load("work/regions.npz"); rj = json.load(open("work/regions.json"))
rels = gazetteer.releasables(G, p["prov"], p["kind"], reg["state_of"], rj["owners"], notes)
out["rels"] = []
for r in rels:
    if not r["facts"]["politics"].get("ruling"):  # as build_mod.py: its nation's
        r["facts"]["politics"]["ruling"] = (nations.LEADERS.get(r["parent"]) or ["despotism"])[0]
    rsubs = gazetteer.leaders(r["tag"], nations.LEADERS.get(r["tag"], []), r["facts"], False, named, {}, genders)
    out["rels"].append([r["tag"], genders.get(f"{r['tag']}_leader_{rsubs[0]}")])
out["crl"] = gazetteer.leaders("CRL", nations.LEADERS["CRL"], {"people": {"ruler": G["ROU"]["game_releasables"]["CRL"]["leader"]}}, False, named, {}, genders)
out["crl_gender"] = genders.get(f"CRL_leader_{out['crl'][0]}")
out["genders"] = genders
print(json.dumps(out))
"""
    r = subprocess.run([sys.executable, "-c", code], cwd=H.ROOT, env=env, capture_output=True, text=True)
    check(r.returncode == 0, f"the build's functions failed: {r.stderr[-1500:]}")
    if r.returncode:
        return
    o = json.loads(r.stdout)

    def block(text, cid):
        m = re.search(rf"^\t{cid} = \{{\n(.*?)^\t\}}\n", text, re.S | re.M)
        return m.group(0) if m else ""
    rou = o["rou"]
    check(block(rou, "ROU_roland_cahun").startswith("\tROU_roland_cahun = {\n\t\tname = ROU_roland_cahun\n\t\tgender = female\n\t\tportraits"),
          f"Roland's block: {block(rou, 'ROU_roland_cahun')[:200]}")
    for cid in ("ROU_serelle_cahun", "RLA_serelle_cahun"):
        b = block(rou, cid)
        check("\t\tgender = male\n" in b and "female" not in b, f"{cid}'s block: {b[:200]}")
    sys.path.insert(0, str(SCRIPTS))
    import nations
    for cid in ("ROU_mahaut_vi", "BRL_mahaut_vi"):
        check(block(rou, cid) == block(nations.ROU_CHARACTERS, cid), f"{cid}'s block changed: {block(rou, cid)[:200]}")
    check(o["copy"] and o["copy"].get("gender") == "male", f"Serelle's copy's changes: {o['copy']}")
    check("\t\tgender = female\n" in block(o["rou_leaders"], "ROU_leader_leninism"),
          f"the communist leader's block: {block(o['rou_leaders'], 'ROU_leader_leninism')[:200]}")
    for sub in o["sgn_subs"][:2]:
        b = block(o["sgn_leaders"], f"SGN_leader_{sub}")
        check("\t\tgender = female\n" in b, f"Seigne's SGN_leader_{sub}: {b[:200]}")
    check("liberalism" in o["sgn_subs"], f"Seigne's leaders: {o['sgn_subs']}")
    gens = re.findall(r"^\t(ROU_gazetteer_\w+) = \{\n\t\tname = \1\n\t\tgender = female\n", o["chars"], re.M)
    check(sorted(gens) == ["ROU_gazetteer_advisor_1", "ROU_gazetteer_general_1"], f"the page's characters: {o['chars'][:600]}")
    check(o["rels"] and all(g == "female" for _, g in o["rels"]), f"the releasables' rulers: {o['rels']}")
    check(o["crl_gender"] == "female", f"Carcarelle's ruler: {o['crl']} {o['crl_gender']}")


def without_field():
    """the facts of source/gazetteer/ with every gender taken out (a copy, GAZETTEER_DIR; since 2026-10-22 some carry
    one): no gender line from the Gazetteer's functions"""
    code = r"""
import json, sys
sys.path.insert(0, "scripts")
import gazetteer, nations, cultures
G = gazetteer.load()
genders = dict(nations.GENDERS)
named = dict(nations.NAMED_LEADERS)
gchars = gazetteer.game_characters(G)
same = gazetteer.patch_characters(nations.ROU_CHARACTERS, gchars, {}, {}, []).count("gender =") == nations.ROU_CHARACTERS.count("gender =")
gazetteer.game_character_names(gchars, named, {}, nations.HAND_MADE, genders)
lines = 0
for tag, f in G.items():
    gazetteer.leaders(tag, nations.LEADERS.get(tag, []), f, tag in nations.HAND_MADE, named, {}, genders)
    lines += "".join(gazetteer.characters(tag, f, {}, set(), {"army": ["A"], "navy": ["N"]})[0]).count("gender")
print(json.dumps([same, genders == dict(nations.GENDERS), lines, len(G)]))
"""
    def strip(v):
        if isinstance(v, dict):
            return {k: strip(x) for k, x in v.items() if k != "gender"}
        return [strip(x) for x in v] if isinstance(v, list) else v
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(H.ROOT) / "source" / "gazetteer"
        for f in src.glob("*.json"):
            (Path(tmp) / f.name).write_text(json.dumps(strip(json.loads(f.read_text(encoding="utf-8"))),
                                                       ensure_ascii=False), encoding="utf-8")
        for d in ("assets", "rekey"):
            if (src / d).exists():
                shutil.copytree(src / d, Path(tmp) / d)
        r = subprocess.run([sys.executable, "-c", code], cwd=H.ROOT, capture_output=True, text=True,
                           env={**os.environ, "GAZETTEER_DIR": tmp})
    check(r.returncode == 0, f"the check without the field failed: {r.stderr[-800:]}")
    if not r.returncode:
        same, gsame, lines, n = json.loads(r.stdout)
        check(same and gsame and lines == 0, f"without the field ({n} nations' facts): hand-made {same}, genders {gsame}, lines {lines}")


def export():
    """facts_export reads the line back from the built characters (a scratch copy: nations.py's own blocks)"""
    sys.path.insert(0, str(SCRIPTS))
    import facts_export
    import nations
    tmp = Path(tempfile.mkdtemp(prefix="gender_mod_", dir=H.WORK))
    (tmp / "common/characters").mkdir(parents=True)
    (tmp / "common/characters/ROU.txt").write_text(nations.ROU_CHARACTERS, encoding="utf-8")
    old, facts_export.MOD = facts_export.MOD, tmp
    try:
        chars = facts_export.read_characters()
    finally:
        facts_export.MOD = old
    of = __import__("ideologies").ideology_of()
    got = {cid: facts_export.character(cid, chars[cid], {}, {}, "neutrality", of)["gender"] for cid in chars}
    want = {cid: "female" if re.search(rf"^\t{cid} = \{{\n\t\tname = {cid}\n\t\tgender = female$", nations.ROU_CHARACTERS, re.M) else "male"
            for cid in chars}
    check(got == want and got.get("ROU_roland_cahun") == "male", f"facts_export's genders: {got}, the blocks say {want}")
    shutil.rmtree(tmp, ignore_errors=True)


def main():
    H.build_site()
    game = site_genders()
    with H.Server(8774) as server, sync_playwright() as p:
        b = p.chromium.launch(executable_path=H.CHROMIUM)
        for i, size in enumerate(((1440, 900), (390, 844))):
            errs, allf = owner(b, server.url, size, game)
            check(not errs, f"{size}: console errors {errs[:5]}")
            if i == 0:
                H.dump(allf, "gender_saved_all.json")
                built(allf)
        b.close()
    without_field()
    export()
    return check.report()


if __name__ == "__main__":
    sys.exit(main())
