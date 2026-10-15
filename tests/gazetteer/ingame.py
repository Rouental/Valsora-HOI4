"""The Gazetteer's view of what the game already has (2026-10-15, the author: "Releasables already in the game should be
represented on the site ... Leaders already in the game should be represented and editable, for example Roland or
Serelle. Their stats should be editable as well as their traits"), and cities' size apart from their victory points
("Rouental's capital should be worth more VPs than Vair ... even though Vair is bigger").

Rouental (the author's own characters): Roland's name, sub-ideology (within his ideology) and traits, Serelle's rank,
skills and a general's traits, saved as ch-<character id>; a general of the page's own with skills; the game's
releasables and civil war revolters on the Releasables tab, Carcarelle renamed and given a state (its whole land saved
as g-CRL), Brillagne's ruler pointing to Mahaut on the People tab; Belekria's Tethia (map tools closed: no land
editing); a city's size and victory points; the every-nation file with all of it. Desktop and phone.

    python3 scripts/facts_export.py          # after a build: the map data the page reads
    python3 tests/gazetteer/ingame.py        # PROBLEMS: none, screenshots in work/gazetteer_test/shots/
"""
import json
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness as H  # noqa: E402
from harness import wait_doc, open_nation, unfold, pick, options, make_password  # noqa: E402

check = H.Checks()
IDX = None


def people_tab(page):
    page.click("[data-tab=people]")
    time.sleep(0.35)


def owner(b, url, size):
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
    game = page.evaluate("app.N.characters.map(c => c.id)")
    check(game[:3] == ["ROU_roland_cahun", "ROU_serelle_cahun", "ROU_mahaut_vi"], f"{label}: Rouental's characters: {game}")

    # ---- the People tab: Roland at the head of state, Serelle among the party leaders, with her skills
    people_tab(page)
    heads = page.evaluate("[...document.querySelectorAll('#pane-people h4')].map(x => x.firstChild.textContent.trim())")
    check(heads[:2] == ["Head of state", "The other parties"], f"{label}: the People tab's sections: {heads}")
    r = "#pp-g-ROU_roland_cahun"
    check(page.get_attribute(f"{r}-name", "placeholder") == "Roland II Cahun", f"{label}: Roland's name isn't shown")
    check("Most Seran Duke" in (page.get_attribute(f"{r}-desc", "placeholder") or ""), f"{label}: Roland's titles aren't shown")
    bg = page.evaluate("id => getComputedStyle(document.getElementById(id).closest('.person').querySelector('.portrait')).backgroundImage",
                       "pp-g-ROU_roland_cahun-name")
    check(bg.startswith('url("data:image/jpeg'), f"{label}: Roland's portrait isn't shown ({bg[:40]})")
    page.fill(f"{r}-name", "Roland III Cahun")
    pp = wait_doc(page, f"{base}/people", lambda v: (v.get("ch-ROU_roland_cahun") or {}).get("name") == "Roland III Cahun")
    check(pp is not None, f"{label}: Roland's new name wasn't saved")
    subs = options(page, f"{r}-sub")
    check(subs and all(IDX_SUB_IDEO[k] == "neutrality" for k in subs), f"{label}: Roland's sub-ideologies aren't all Monarchist: {subs}")
    pick(page, f"{r}-sub", "despotism")
    pick(page, f"{r}-traits", options(page, f"{r}-traits")[0])
    pp = wait_doc(page, f"{base}/people", lambda v: v["ch-ROU_roland_cahun"].get("sub") == "despotism" and v["ch-ROU_roland_cahun"].get("traits"))
    check(pp and len(pp["ch-ROU_roland_cahun"]["traits"]) == 1, f"{label}: Roland's sub-ideology and trait: {pp and pp.get('ch-ROU_roland_cahun')}")
    s_ = "#pp-g-ROU_serelle_cahun"
    sec = page.evaluate("id => document.getElementById(id).closest('.sec').querySelector('h4').firstChild.textContent.trim()", "pp-g-ROU_serelle_cahun-name")
    check(sec == "The other parties", f"{label}: Serelle sits under {sec}")
    check(page.get_attribute(f"{s_}-skill", "placeholder") == "4" and page.get_attribute(f"{s_}-attack", "placeholder") == "4",
          f"{label}: Serelle's skills aren't shown")
    check(page.get_attribute(f"{s_}-regnal", "placeholder") == "Serelle VI Cahun", f"{label}: Serelle's regnal name isn't shown")
    ut = page.evaluate("s => [...document.querySelectorAll(s)].map(x => x.textContent)", f"#pane-people .person:has({s_}-name) .tchip")
    check(any("Armor Officer" in t or "Armour" in t or "armor" in t.lower() for t in ut), f"{label}: Serelle's general trait isn't shown: {ut}")
    page.fill(f"{s_}-skill", "5")
    page.fill(f"{s_}-attack", "6")
    pick(page, f"{s_}-rank", "field_marshal")
    pp = wait_doc(page, f"{base}/people", lambda v: (v.get("ch-ROU_serelle_cahun") or {}).get("attack") == 6 and v["ch-ROU_serelle_cahun"].get("rank"))
    g = (pp or {}).get("ch-ROU_serelle_cahun") or {}
    check(g.get("skill") == 5 and g.get("attack") == 6 and g.get("rank") == "field_marshal" and g.get("unit") == "general",
          f"{label}: Serelle's skills: {g}")
    # taking her game trait away is kept as an empty list
    page.click(f"#pane-people .person:has({s_}-name) .tchip .x")
    pp = wait_doc(page, f"{base}/people", lambda v: v["ch-ROU_serelle_cahun"].get("unitTraits") == [])
    check(pp is not None, f"{label}: taking Serelle's trait away wasn't kept")
    page.evaluate("document.getElementById('pp-g-ROU_serelle_cahun-name').scrollIntoView()")
    time.sleep(0.3)
    page.screenshot(path=str(H.SHOTS / f"ingame_{label}_people.png"))

    # ---- a general of the page's own, with skills
    page.click("button:has-text('Add a character')")
    time.sleep(0.35)
    page.keyboard.type("Général Test")
    pp = wait_doc(page, f"{base}/people", lambda v: any(k.startswith("c-") and x and x.get("name") == "Général Test" for k, x in v.items()))
    cg = next(k for k, x in pp.items() if k.startswith("c-") and x and x.get("name") == "Général Test")
    page.fill(f"#pp-c-st-{cg}-skill", "4")
    page.fill(f"#pp-c-st-{cg}-logistics", "12")
    pp = wait_doc(page, f"{base}/people", lambda v: v[cg].get("logistics"))
    check(pp and pp[cg]["skill"] == 4 and pp[cg]["logistics"] == 9, f"{label}: the general's skills (12 kept at 9): {pp and pp.get(cg)}")

    # ---- the Releasables tab: the game's releasables and revolters
    page.click("[data-tab=release]")
    time.sleep(0.4)
    heads = page.evaluate("[...document.querySelectorAll('#pane-release h4')].map(x => x.firstChild.textContent.trim())")
    check(heads == ["Releasables", "In the game", "In the civil war"], f"{label}: the Releasables tab's sections: {heads}")
    n_game = page.evaluate("app.N.relList.filter(r => r.game && r.game.kind === 'releasable').length")
    n_war = page.evaluate("app.N.relList.filter(r => r.game && r.game.kind === 'civil_war').length")
    check(n_game == 13 and n_war == 7, f"{label}: {n_game} releasables and {n_war} revolters")
    check(page.get_attribute("#rl-name-g-CRL", "placeholder") == "Carcarelle", f"{label}: Carcarelle's name isn't shown")
    page.fill("#rl-name-g-CRL", "Carcarelle Libre")
    rel = wait_doc(page, f"{base}/releasables", lambda v: (v.get("g-CRL") or {}).get("name") == "Carcarelle Libre")
    check(rel is not None, f"{label}: Carcarelle's new name wasn't saved")
    # a state of Rouental's own goes to Carcarelle: its whole land is saved, and the state leaves the releasable that had it
    before = page.evaluate("app.N.relSets.get('g-CRL').size")
    target = page.evaluate("""() => { const N = app.N, own = N.relSets.get('g-CRL');
        const other = [...N.relSets.get('g-GHS')][0]; return other; }""")
    page.evaluate("s => { app.ui.relMode = 'add'; selectRel('g-CRL'); paintRel(app.N.states[s].provs[0]); }", target)
    rel = wait_doc(page, f"{base}/releasables", lambda v: (v.get("g-CRL") or {}).get("states") and len([k for k, on in v["g-CRL"]["states"].items() if on]) == before + 1)
    check(rel is not None, f"{label}: Carcarelle's new land wasn't saved as its whole list of states")
    check(page.evaluate("app.N.relSets.get('g-GHS').size") == 1, f"{label}: Ghessone, whose only state it was, lost it")
    # Brillagne's ruler is Mahaut: changed on the People tab
    brl = page.inner_text("#pane-release .relcard:has(#rl-name-g-BRL)")
    check("Mahaut VI" in brl and "People tab" in brl, f"{label}: Brillagne's ruler: {brl[-300:]}")
    # the civil war's revolters are apart: picking one shows their land
    page.evaluate("selectRel('g-VAI')")
    check(page.evaluate("[...app.N.relOf.values()].every(id => ['g-BRL','g-CRP','g-RLT','g-MRC','g-RLA','g-VAI','g-FTH'].includes(id))"),
          f"{label}: the revolters' land mixes with the releasables'")
    page.evaluate("document.getElementById('rl-name-g-CRL').scrollIntoView()")
    time.sleep(0.3)
    page.screenshot(path=str(H.SHOTS / f"ingame_{label}_releasables.png"))

    # ---- cities: victory points by importance, size apart
    page.click("[data-tab=cities]")
    time.sleep(0.4)
    first = page.evaluate("app.N.cityList[0].id")
    vps = page.evaluate("s => [...document.querySelector(s).options].map(o => o.textContent)", f"#city-vp-{first}")
    check(vps and vps[0].startswith("1 · minor") and any("foremost" in v for v in vps), f"{label}: victory points' labels: {vps}")
    pick(page, f"#city-size-{first}", "metropolis")
    cs = wait_doc(page, f"{base}/cities", lambda v: v[first].get("size") == "metropolis")
    check(cs is not None, f"{label}: the city's size wasn't saved")
    page.screenshot(path=str(H.SHOTS / f"ingame_{label}_cities.png"))

    # ---- Belekria: Tethia, map tools closed
    page.click("#back")
    time.sleep(0.4)
    make_password(page, "Belekria", "BLK")
    open_nation(page, "Belekria", "BLK")
    page.click("[data-tab=release]")
    time.sleep(0.4)
    tth = page.inner_text("#pane-release .relcard:has(#rl-name-g-TTH)")
    check("Tethia" in page.get_attribute("#rl-name-g-TTH", "placeholder") and "Change its states" not in tth
          and "once the author has drawn your states" in tth, f"{label}: Tethia: {tth[:300]}")

    # ---- every nation in a file
    page.click("#back")
    time.sleep(0.4)
    page.click("#owner button:has-text('Save every nation as a file')")
    page.wait_for_function("window.__saved && window.__saved.filename.includes('all')", timeout=20000)
    allf = json.loads(page.evaluate("window.__saved.data"))
    H.dump(allf, f"ingame_{label}_saved_all.json")
    R = allf["nations"]["ROU"]["facts"]
    check(R["people"]["ch-ROU_serelle_cahun"]["attack"] == 6 and R["releasables"]["g-CRL"]["name"] == "Carcarelle Libre"
          and R["cities"][first]["size"] == "metropolis", f"{label}: the saved file: {json.dumps(R)[:300]}")
    ctx.close()
    return errs


IDX_SUB_IDEO = {}


def main():
    global IDX
    H.build_site()
    IDX = json.loads((H.SITE / "index.json").read_text())
    for ideo, lst in IDX["subtypes"].items():
        for k, *_ in lst:
            IDX_SUB_IDEO[k] = ideo
    with H.Server(8773) as server, sync_playwright() as p:
        b = p.chromium.launch(executable_path=H.CHROMIUM)
        for size in ((1440, 900), (390, 844)):
            errs = owner(b, server.url, size)
            check(not errs, f"{size}: console errors {errs[:5]}")
        b.close()
    return check.report()


if __name__ == "__main__":
    sys.exit(main())
