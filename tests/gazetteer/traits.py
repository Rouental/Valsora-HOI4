"""The Gazetteer's trait pickers (2026-10-15): a ruler's, a party leader's, a general's, an admiral's and an
advisor's traits from the base game (index.json's lists, from source/vanilla/index/traits.json), at most six; a
request for a new trait; the every-nation file with them. Desktop and phone; with no shared atlas (local mode), the
lists work and the request form is a note instead.

    python3 scripts/facts_export.py          # after a build: the map data the page reads
    python3 tests/gazetteer/traits.py        # PROBLEMS: none, screenshots in work/gazetteer_test/shots/

Then the saved file can be taken into a test build (not the real one):
    GAZETTEER_DIR=<a copy of source/gazetteer> GAZETTEER_FLAGS=<a folder> python3 scripts/gazetteer.py import \\
        work/gazetteer_test/shots/1440_saved_all.json   (and build_mod.py, check_mod.py with the same variables)"""
import json
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness as H  # noqa: E402
from harness import doc, wait_doc, open_nation, unfold, pick, options, make_password  # noqa: E402

check = H.Checks()
TR = None


def groups(page, sel):
    return page.evaluate("s => [...document.querySelectorAll(s + ' optgroup')].map(g => g.label)", sel)


def people_id(v, name):
    return next((k for k, x in v.items() if k.startswith("c-") and x and x.get("name") == name), None)


def owner(b, url, size):
    label = f"{size[0]}"
    ctx, page, errs = H.new_page(b, size, "window.__me = {id: 'u_owner', name: 'The Author', isOwner: true};")
    page.goto(url)
    page.wait_for_selector(".nrow", timeout=20000)
    page.wait_for_selector("#owner:not([hidden])", timeout=8000)
    time.sleep(0.4)
    unfold(page, "Passwords")
    tag = "SGN"
    make_password(page, "Seigne", tag)
    open_nation(page, "Seigne", tag)
    page.wait_for_function("app.N.K", timeout=5000)
    base = f"n/{tag}/{page.evaluate('app.N.K')}"
    page.click("[data-tab=people]")
    time.sleep(0.3)

    # the head of state: the rulers' list, grouped; two traits, then one removed; at most six
    ruler_opts = options(page, "#pp-ruler-traits")
    check(len(ruler_opts) == len(TR["ruler"]), f"{label}: ruler list has {len(ruler_opts)} of {len(TR['ruler'])}")
    check(set(groups(page, "#pp-ruler-traits")) <= {"Personality", "Basic", "Terrain", "Learned", "Terrain, learned"},
          f"{label}: odd ruler groups {groups(page, '#pp-ruler-traits')}")
    a, bb = ruler_opts[0], ruler_opts[1]
    pick(page, "#pp-ruler-traits", a)
    pick(page, "#pp-ruler-traits", bb)
    pp = wait_doc(page, f"{base}/people", lambda v: v["ruler"]["traits"] == [a, bb])
    check(pp and pp["ruler"]["traits"] == [a, bb], f"{label}: ruler traits not saved: {pp and pp.get('ruler')}")
    check(a not in options(page, "#pp-ruler-traits"), f"{label}: a chosen trait is still offered")
    page.click("#pane-people .person >> nth=0 >> .tchip .x >> nth=0")
    pp = wait_doc(page, f"{base}/people", lambda v: v["ruler"]["traits"] == [bb])
    check(pp and pp["ruler"]["traits"] == [bb], f"{label}: removing a ruler trait: {pp and pp.get('ruler')}")
    for k in options(page, "#pp-ruler-traits")[:5]:
        pick(page, "#pp-ruler-traits", k)
    pp = wait_doc(page, f"{base}/people", lambda v: len(v["ruler"]["traits"]) == 6)
    check(pp and len(pp["ruler"]["traits"]) == 6, f"{label}: six ruler traits not saved: {pp and pp.get('ruler')}")
    check(page.locator("#pp-ruler-traits").count() == 0, f"{label}: the list is still offered at six traits")
    page.screenshot(path=str(H.SHOTS / f"traits_{label}_ruler.png"))
    # asking for a new one
    page.click("#pane-people .person >> nth=0 >> button:has-text('Ask for a new trait')")
    page.fill("#pp-ruler-ask-name", "Silver Ford Diplomat")
    page.fill("#pp-ruler-ask-what", "+10% opinion with the Reibonnaise states")
    page.click("#pane-people .person >> nth=0 >> button:has-text('Send')")
    time.sleep(0.6)
    rq = page.evaluate(f"[...window.__store.keys()].filter(k => k.startsWith('{base}/req-')).map(k => window.__store.get(k))")
    check(len(rq) == 1 and rq[0]["kind"] == "trait" and "Silver Ford Diplomat" in rq[0]["title"]
          and "head of state" in rq[0]["details"] and "+10% opinion" in rq[0]["details"], f"{label}: trait request: {rq}")
    check("Sent." in page.inner_text("#pane-people .person >> nth=0"), f"{label}: no confirmation after sending")

    # a party leader: communism with a set sub-ideology gets traits
    pick(page, "#pp-sub-communism", "leninism")
    page.wait_for_selector("#pp-traits-communism", timeout=4000)
    pick(page, "#pp-traits-communism", options(page, "#pp-traits-communism")[2])
    pp = wait_doc(page, f"{base}/people", lambda v: v["party-communism"]["traits"])
    check(pp and len(pp["party-communism"]["traits"]) == 1, f"{label}: party leader trait: {pp and pp.get('party-communism')}")

    def add_character(name, role=None, slot=None):
        page.click("button:has-text('Add a character')")
        time.sleep(0.35)
        page.keyboard.type(name)
        pp = wait_doc(page, f"{base}/people", lambda v: people_id(v, name))
        cid = people_id(pp, name)
        row = f"#pane-people .person:has(#pp-c-name-{cid})"
        if role:
            pick(page, f"{row} select[aria-label=Role]", role)
        if slot:
            check("Pick the advisor's post" in page.inner_text(row), f"{label}: no hint to pick a post")
            check(page.locator(f"#pp-c-traits-{cid}").count() == 0, f"{label}: an advisor without a post has traits")
            pick(page, f"{row} select[aria-label=Post]", slot)
        return cid, row

    g, grow = add_character("Général Trait")
    gopts = options(page, f"#pp-c-traits-{g}")
    check(len(gopts) == len(TR["general"]), f"{label}: general list {len(gopts)} of {len(TR['general'])}")
    pick(page, f"#pp-c-traits-{g}", gopts[0])
    pick(page, f"#pp-c-traits-{g}", gopts[-1])
    pp = wait_doc(page, f"{base}/people", lambda v: len(v[g]["traits"]) == 2)
    check(pp and pp[g]["traits"] == [gopts[0], gopts[-1]] and pp[g]["role"] == "general", f"{label}: general: {pp and pp.get(g)}")

    ad, arow = add_character("Amiral Trait", "admiral")
    aopts = options(page, f"#pp-c-traits-{ad}")
    check(len(aopts) == len(TR["admiral"]), f"{label}: admiral list {len(aopts)} of {len(TR['admiral'])}")
    pick(page, f"#pp-c-traits-{ad}", aopts[1])
    pp = wait_doc(page, f"{base}/people", lambda v: v[ad].get("traits"))
    check(pp and pp[ad]["traits"] == [aopts[1]], f"{label}: admiral trait: {pp and pp.get(ad)}")
    pick(page, f"{arow} select[aria-label=Role]", "general")      # another role clears the traits
    pp = wait_doc(page, f"{base}/people", lambda v: v[ad]["role"] == "general")
    check(pp and not pp[ad].get("traits"), f"{label}: traits kept across a role change: {pp and pp.get(ad)}")
    pick(page, f"{arow} select[aria-label=Role]", "admiral")
    pick(page, f"#pp-c-traits-{ad}", aopts[1])

    adv, vrow = add_character("Conseiller Trait", "advisor", "army_chief")
    vopts = options(page, f"#pp-c-traits-{adv}")
    want = [k for k, *_ in TR["advisor"]["army_chief"]]
    check(sorted(vopts) == sorted(want), f"{label}: chief of army list {len(vopts)} of {len(want)}")
    pick(page, f"#pp-c-traits-{adv}", vopts[0])
    pp = wait_doc(page, f"{base}/people", lambda v: v[adv].get("traits"))
    check(pp and pp[adv]["slot"] == "army_chief" and pp[adv]["traits"] == [vopts[0]], f"{label}: advisor: {pp and pp.get(adv)}")
    pick(page, f"{vrow} select[aria-label=Post]", "theorist")       # another post clears the traits
    pp = wait_doc(page, f"{base}/people", lambda v: v[adv]["slot"] == "theorist")
    check(pp and not pp[adv].get("traits"), f"{label}: traits kept across a post change: {pp and pp.get(adv)}")
    pick(page, f"#pp-c-traits-{adv}", options(page, f"#pp-c-traits-{adv}")[0])
    wait_doc(page, f"{base}/people", lambda v: v[adv].get("traits"))
    page.click(f"{grow} button:has-text('Ask for a new trait')")
    page.fill(f"#pp-c-ask-{g}-name", "Mountain Fox")
    page.click(f"{grow} button:has-text('Send')")
    time.sleep(0.6)
    rq = page.evaluate(f"[...window.__store.keys()].filter(k => k.startsWith('{base}/req-')).map(k => window.__store.get(k))")
    check(len(rq) == 2 and any("Mountain Fox" in r["title"] and "général trait" in r["details"].lower() for r in rq),
          f"{label}: the general's request: {rq}")
    page.evaluate("document.getElementById('pane-people').scrollTop = 1e6")
    time.sleep(0.3)
    page.screenshot(path=str(H.SHOTS / f"traits_{label}_characters.png"))

    # the owner's list of requests, and every nation in a file
    page.click("#back")
    time.sleep(0.4)
    page.click("#owner button:has-text('Refresh')")
    page.wait_for_function(f"!app.ownerBusy && app.owner.{tag} && app.owner.{tag}.reqs.length === 2", timeout=8000)
    unfold(page, "Requests")
    txt = page.inner_text("#owner")
    check("New trait" in txt and "Silver Ford Diplomat" in txt, f"{label}: the owner's list doesn't show the trait request")
    page.click("#owner button:has-text('Save every nation as a file')")
    page.wait_for_function("window.__saved && window.__saved.filename.includes('all')", timeout=20000)
    allf = json.loads(page.evaluate("window.__saved.data"))
    H.dump(allf, f"{label}_saved_all.json")
    P = allf["nations"][tag]["facts"]["people"]
    check(len(P["ruler"]["traits"]) == 6 and P[g]["traits"] and P[ad]["traits"] and P[adv]["traits"]
          and P[adv]["slot"] == "theorist", f"{label}: the saved file lacks traits: {json.dumps(P)[:300]}")
    ctx.close()
    return errs


def local(b, url, size):
    """no shared atlas: the trait lists work, the request form is a note"""
    label = f"{size[0]}_local"
    ctx, page, errs = H.new_page(b, size, mock=False)
    page.goto(url)
    page.wait_for_selector(".nrow", timeout=20000)
    open_nation(page, "Seigne", "SGN")
    page.click("[data-tab=people]")
    time.sleep(0.3)
    opts = options(page, "#pp-ruler-traits")
    pick(page, "#pp-ruler-traits", opts[3])
    time.sleep(0.4)
    names = {k: n for k, n, *_ in TR["ruler"]}
    check(names[opts[3]] in page.inner_text("#pane-people .person >> nth=0"), f"{label}: the chosen trait isn't shown")
    page.click("#pane-people .person >> nth=0 >> button:has-text('Ask for a new trait')")
    time.sleep(0.2)
    check("describe the trait in the notes" in page.inner_text("#pane-people .person >> nth=0"), f"{label}: no local note")
    page.screenshot(path=str(H.SHOTS / f"traits_{label}.png"))
    ctx.close()
    return errs


def main():
    global TR
    H.build_site()
    TR = json.loads((H.SITE / "index.json").read_text())["traits"]
    with H.Server(8771) as server, sync_playwright() as p:
        b = p.chromium.launch(executable_path=H.CHROMIUM)
        for size in ((1440, 900), (390, 844)):
            for fn in (owner, local):
                errs = fn(b, server.url, size)
                check(not errs, f"{size} {fn.__name__}: console errors {errs[:5]}")
        b.close()
    return check.report()


if __name__ == "__main__":
    sys.exit(main())
