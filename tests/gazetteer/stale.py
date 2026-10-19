"""Facts left under old keys after the map is cut again (2026-10-19, the author's recording: "changing the terrain of one
province can change it on others"). A key is a pixel; once Terreich's provinces were cut along its rivers, 51 of them
held two or three keys from before, often with other terrain, and the page showed whichever came first in the store's
order, which changed with every save. Now the keys are read in one fixed order (by key, the province's own key last),
the same as the build's (gazetteer.page_order), and an edit gathers a province's keys into its own.

    python3 scripts/facts_export.py          # after a build: the map data the page reads
    python3 tests/gazetteer/stale.py         # PROBLEMS: none
"""
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import harness as H  # noqa: E402
from harness import wait_doc, open_nation, unfold, make_password  # noqa: E402
import gazetteer  # noqa: E402

check = H.Checks()
TAG, NAME = "TUP", "Terreich"
# two provinces of Terreich's on the map of 10-19-2, each with two keys of the map before (Terreich's export of that
# morning): their own keys are 1021,1783 and 1042,1797
OWN = ("1021,1783", "1042,1797")
STALE = {"1023,1792": {"t": "plains"}, "1019,1779": {"t": "forest"}, "1041,1803": {"t": "hills"}, "1039,1792": {"t": "marsh"}}
WANT = {"1021,1783": "plains", "1042,1797": "hills"}   # by key, the later wins


def seed(page, base, items):
    page.evaluate("([p, items]) => window.__store.set(p, Object.fromEntries(items))", [f"{base}/provinces", items])


def reopen(page):
    page.click("#back")
    time.sleep(0.4)
    open_nation(page, NAME, TAG)


def shown(page):
    return page.evaluate("own => own.map(k => { const p = ownProvAt(...keyXY(k)); return p < 0 ? null : (app.N.provFacts[p] || {}).t || null; })",
                         list(OWN))


def run(b, url):
    ctx, page, errs = H.new_page(b, (1440, 900), "window.__me = {id: 'u_owner', name: 'The Author', isOwner: true};")
    page.goto(url)
    page.wait_for_selector(".nrow", timeout=20000)
    page.wait_for_selector("#owner:not([hidden])", timeout=8000)
    time.sleep(0.4)
    unfold(page, "Passwords")
    make_password(page, NAME, TAG)
    open_nation(page, NAME, TAG)
    page.wait_for_function("app.N.K", timeout=5000)
    base = f"n/{TAG}/{page.evaluate('app.N.K')}"
    check(page.evaluate("own => own.every(k => app.N.prov.some(p => p.key === k))", list(OWN)),
          "the test's provinces aren't Terreich's own keys any more (the map changed: pick two again)")

    # the same terrain whatever order the store hands the keys back in
    for order in (list(STALE.items()), list(reversed(STALE.items()))):
        seed(page, base, order)
        reopen(page)
        check(shown(page) == [WANT[k] for k in OWN], f"stale keys in the order {[k for k, _ in order]}: shows {shown(page)}")

    # painting another province leaves them alone, after its save comes back too
    other = page.evaluate("own => app.N.prov.findIndex(p => !own.includes(p.key))", list(OWN))
    page.evaluate("p => editProv(p, { t: 'urban' })", other)
    wait_doc(page, f"{base}/provinces", lambda v: any(x.get("t") == "urban" for x in v.values() if x))
    time.sleep(1.2)
    check(shown(page) == [WANT[k] for k in OWN], f"painting another province changed them: {shown(page)}")

    # an edit goes under the province's own key and clears its old keys
    p0 = page.evaluate("k => ownProvAt(...keyXY(k))", OWN[0])
    page.evaluate("p => editProv(p, { t: 'desert' })", p0)
    v = wait_doc(page, f"{base}/provinces", lambda v: (v.get(OWN[0]) or {}).get("t") == "desert")
    left = sorted(k for k in ("1023,1792", "1019,1779") if (v or {}).get(k))
    check(v and (v.get(OWN[0]) or {}).get("t") == "desert" and not left, f"the edit wasn't gathered under {OWN[0]}: {v}")
    reopen(page)
    check(shown(page) == ["desert", WANT[OWN[1]]], f"after the edit: {shown(page)}")

    # the build reads them the same way
    order = gazetteer.page_order(STALE.items(), lambda k: {"1023,1792": 0, "1019,1779": 0, "1041,1803": 1, "1039,1792": 1}[k],
                                 lambda p: OWN[p])
    last = {}
    for k, v in order:
        last[{"1023,1792": 0, "1019,1779": 0, "1041,1803": 1, "1039,1792": 1}[k]] = v["t"]
    check([last[0], last[1]] == [WANT[k] for k in OWN], f"the build picks {last}, the page {WANT}")
    own_last = gazetteer.page_order([(OWN[0], {"t": "urban"}), ("1023,1792", {"t": "plains"})], lambda k: 0, lambda p: OWN[0])
    check(own_last[-1][0] == OWN[0], f"the build doesn't read the own key last: {own_last}")
    page.screenshot(path=str(H.SHOTS / "stale_keys.png"))
    ctx.close()
    return errs


def main():
    H.build_site()
    with H.Server(8774) as server, sync_playwright() as p:
        b = p.chromium.launch(executable_path=H.CHROMIUM)
        errs = run(b, server.url)
        check(not errs, f"console errors {errs[:5]}")
        b.close()
    return check.report()


if __name__ == "__main__":
    sys.exit(main())
