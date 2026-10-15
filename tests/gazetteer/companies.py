"""The Gazetteer's political advisors and companies (2026-10-15, the author: "allow people to create political
advisors and companies"): a political advisor in its own section with the political advisors' traits; companies of
the base game's kinds (an arms company and an industrial concern), a logo, a request for a new kind; the every-nation
file with them. Desktop and phone; with no shared atlas (local mode), the request form is a note instead.

    python3 scripts/facts_export.py          # after a build: the map data the page reads
    python3 tests/gazetteer/companies.py     # PROBLEMS: none, screenshots in work/gazetteer_test/shots/
"""
import base64
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


def upload(page, selector, path):
    with page.expect_file_chooser() as fc:
        page.click(selector)
    fc.value.set_files(str(path))


def owner(b, url, size):
    label = f"{size[0]}"
    ctx, page, errs = H.new_page(b, size, "window.__me = {id: 'u_owner', name: 'The Author', isOwner: true};")
    blobs = {}   # uploaded pictures, served as the platform serves /_blob/<id>
    ctx.expose_function("__putBlob", lambda i, b64, ct: blobs.__setitem__(i, (base64.b64decode(b64), ct)))

    def blob(route):
        i = route.request.url.rsplit("/", 1)[1]
        if i in blobs:
            route.fulfill(body=blobs[i][0], content_type=blobs[i][1])
        else:
            route.fulfill(status=404, body="no such blob")
    ctx.route("**/_blob/*", blob)
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
    heads = page.evaluate("[...document.querySelectorAll('#pane-people h4')].map(x => x.firstChild.textContent.trim())")
    check(heads[:5] == ["Head of state", "The other parties", "Political advisors", "Generals, admirals and other advisors",
                        "Companies"], f"{label}: the People tab's sections: {heads}")

    # a political advisor, in its own section, with the political advisors' traits
    page.click("button:has-text('Add a political advisor')")
    time.sleep(0.35)
    page.keyboard.type("Conseillère Politique")
    pp = wait_doc(page, f"{base}/people", lambda v: any(x and x.get("name") == "Conseillère Politique" for x in v.values()))
    pid = next(k for k, x in pp.items() if x and x.get("name") == "Conseillère Politique")
    check(pp[pid].get("role") == "advisor" and pp[pid].get("slot") == "political_advisor", f"{label}: political advisor: {pp[pid]}")
    popts = options(page, f"#pp-c-traits-{pid}")
    want = [k for k, *_ in IDX["traits"]["advisor"]["political_advisor"]]
    check(sorted(popts) == sorted(want), f"{label}: political advisor list {len(popts)} of {len(want)}")
    pick(page, f"#pp-c-traits-{pid}", popts[0])
    pp = wait_doc(page, f"{base}/people", lambda v: v[pid].get("traits"))
    check(pp and pp[pid]["traits"] == [popts[0]], f"{label}: political advisor's trait: {pp and pp.get(pid)}")
    sec = page.evaluate("id => document.getElementById('pp-c-name-' + id).closest('.sec').querySelector('h4').firstChild.textContent.trim()", pid)
    check(sec == "Political advisors", f"{label}: the political advisor sits under {sec}")
    page.evaluate("id => document.getElementById('pp-c-name-' + id).closest('.sec').scrollIntoView()", pid)
    time.sleep(0.3)
    page.screenshot(path=str(H.SHOTS / f"companies_{label}_advisors.png"))

    # a company of each family
    arms = IDX["companies"]["arms"]
    concerns = IDX["companies"]["concerns"]
    page.click("button:has-text('Add a company')")
    time.sleep(0.35)
    page.keyboard.type("Ateliers de la Seigne")
    pp = wait_doc(page, f"{base}/people", lambda v: any(k.startswith("co-") and x and x.get("name") == "Ateliers de la Seigne" for k, x in v.items()))
    a = next(k for k, x in pp.items() if k.startswith("co-") and x and x.get("name") == "Ateliers de la Seigne")
    kinds = options(page, f"#pp-co-kind-{a}")
    check(len(kinds) == len(arms) + len(concerns), f"{label}: {len(kinds)} kinds offered, {len(arms) + len(concerns)} expected")
    groups = page.evaluate("s => [...document.querySelectorAll(s + ' optgroup')].map(g => g.label)", f"#pp-co-kind-{a}")
    check(groups == ["Arms: tanks", "Arms: ships", "Arms: aircraft", "Arms: land equipment", "Industrial concerns"],
          f"{label}: the kinds' groups: {groups}")
    tank = next(k for k, nm, grp, *_ in arms if k == "generic_medium_tank_organization")
    pick(page, f"#pp-co-kind-{a}", tank)
    pp = wait_doc(page, f"{base}/people", lambda v: v[a].get("kind") == tank)
    check(pp and pp[a]["kind"] == tank, f"{label}: the arms company's kind: {pp and pp.get(a)}")
    row = f"#pane-people .person:has(#pp-co-name-{a})"
    what = page.inner_text(row)
    check("military-industrial organisation" in what and "armor technology research" in what.lower(), f"{label}: what it is: {what[-300:]}")
    upload(page, f"{row} .portrait", H.WORK / "test_flag.png")
    pp = wait_doc(page, f"{base}/people", lambda v: v[a].get("logo"))
    check(pp and pp[a].get("logo"), f"{label}: the logo wasn't saved: {pp and pp.get(a)}")
    page.click("button:has-text('Add a company')")
    time.sleep(0.35)
    page.keyboard.type("Banque de Seigne")
    pp = wait_doc(page, f"{base}/people", lambda v: any(k.startswith("co-") and x and x.get("name") == "Banque de Seigne" for k, x in v.items()))
    cc = next(k for k, x in pp.items() if k.startswith("co-") and x and x.get("name") == "Banque de Seigne")
    pick(page, f"#pp-co-kind-{cc}", "concern:central_bank")
    pp = wait_doc(page, f"{base}/people", lambda v: v[cc].get("kind") == "concern:central_bank")
    check(pp and pp[cc]["kind"] == "concern:central_bank", f"{label}: the concern's kind: {pp and pp.get(cc)}")
    page.fill(f"#pp-co-note-{cc}", "Founded 1802; prints the crown")
    wait_doc(page, f"{base}/people", lambda v: v[cc].get("notes"))
    # a new kind of company, asked for
    page.click("button:has-text('Ask for a new kind of company')")
    page.fill("#pp-co-ask-name", "Rocket maker")
    page.fill("#pp-co-ask-what", "Designs missiles and launchers")
    page.click("#pane-people .sec:has(#pp-co-ask-name) button:has-text('Send')")
    time.sleep(0.6)
    rq = page.evaluate(f"[...window.__store.keys()].filter(k => k.startsWith('{base}/req-')).map(k => window.__store.get(k))")
    check(len(rq) == 1 and rq[0]["kind"] == "company" and "Rocket maker" in rq[0]["title"], f"{label}: company request: {rq}")
    page.evaluate("document.getElementById('pane-people').scrollTop = 1e6")
    time.sleep(0.3)
    page.screenshot(path=str(H.SHOTS / f"companies_{label}.png"))
    # deleting a company
    page.click("button:has-text('Add a company')")
    time.sleep(0.35)
    page.keyboard.type("Doomed")
    pp = wait_doc(page, f"{base}/people", lambda v: any(x and x.get("name") == "Doomed" for x in v.values()))
    d = next(k for k, x in pp.items() if x and x.get("name") == "Doomed")
    page.click(f"#pane-people .person:has(#pp-co-name-{d}) button:has-text('Delete')")
    pp = wait_doc(page, f"{base}/people", lambda v: not v.get(d))
    check(pp and not pp.get(d), f"{label}: a deleted company stays")

    # the every-nation file
    page.click("#back")
    time.sleep(0.4)
    page.click("#owner button:has-text('Refresh')")
    page.wait_for_function(f"!app.ownerBusy && app.owner.{tag} && app.owner.{tag}.reqs.length === 1", timeout=8000)
    unfold(page, "Requests")
    check("New kind of company" in page.inner_text("#owner"), f"{label}: the owner's list doesn't show the request's kind")
    page.click("#owner button:has-text('Save every nation as a file')")
    page.wait_for_function("window.__saved && window.__saved.filename.includes('all')", timeout=20000)
    allf = json.loads(page.evaluate("window.__saved.data"))
    H.dump(allf, f"companies_{label}_saved_all.json")
    P = allf["nations"][tag]["facts"]["people"]
    check(P[a]["kind"] == tank and P[a].get("logo") and P[cc]["kind"] == "concern:central_bank" and P[pid]["slot"] == "political_advisor",
          f"{label}: the saved file: {json.dumps(P)[:300]}")
    ctx.close()
    return errs


def local(b, url, size):
    label = f"{size[0]}_local"
    ctx, page, errs = H.new_page(b, size, mock=False)
    page.goto(url)
    page.wait_for_selector(".nrow", timeout=20000)
    open_nation(page, "Seigne", "SGN")
    page.click("[data-tab=people]")
    time.sleep(0.3)
    page.click("button:has-text('Add a company')")
    time.sleep(0.3)
    page.click("button:has-text('Ask for a new kind of company')")
    time.sleep(0.2)
    check("describe the kind in the notes" in page.inner_text("#pane-people"), f"{label}: no local-mode note")
    ctx.close()
    return errs


def main():
    global IDX
    H.build_site()
    IDX = json.loads((H.SITE / "index.json").read_text())
    with H.Server(8772) as server, sync_playwright() as p:
        b = p.chromium.launch(executable_path=H.CHROMIUM)
        for size in ((1440, 900), (390, 844)):
            for fn in (owner, local):
                errs = fn(b, server.url, size)
                check(not errs, f"{size} {fn.__name__}: console errors {errs[:5]}")
        b.close()
    return check.report()


if __name__ == "__main__":
    sys.exit(main())
