"""The Gazetteer's "Start over" (2026-10-16, the author: "is there a way you could reset any edits made thus far? I'd
like a blank slate"): Owner tools › Start over deletes every nation's facts, pictures, requests, status and notes, and
keeps its password; a browser's unsent changes from before it don't come back.

    python3 scripts/facts_export.py          # after a build: the map data the page reads
    python3 tests/gazetteer/reset.py         # PROBLEMS: none, screenshots in work/gazetteer_test/shots/
"""
import json
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness as H  # noqa: E402
from harness import wait_doc, open_nation, unfold, make_password  # noqa: E402

check = H.Checks()


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
    # something entered: a motto, a company and a request
    page.click("[data-tab=nation]")
    time.sleep(0.3)
    page.fill("#ab-motto", "Semper Seigne")
    wait_doc(page, f"{base}/about", lambda v: v.get("motto") == "Semper Seigne")
    page.fill("#rq-title", "A test request")
    page.click("button:has-text('Send request')")
    time.sleep(0.5)
    before = page.evaluate(f"[...window.__store.keys()].filter(k => k.startsWith('{base}/'))")
    check(any(k.endswith("/about") for k in before) and any("/req-" in k for k in before), f"{label}: nothing to clear: {before}")

    # start over
    page.click("#back")
    time.sleep(0.4)
    unfold(page, "Start over")
    page.click("#owner button:has-text('Clear every nation')")
    time.sleep(0.3)
    check("Type CLEAR" in page.inner_text("#owner"), f"{label}: cleared without the word")
    page.fill("#own-reset", "clear")
    page.click("#owner button:has-text('Clear every nation')")
    page.wait_for_function("!app.resetBusy && (app.resetMsg || '').startsWith('Done')", timeout=10000)
    after = page.evaluate(f"[...window.__store.keys()].filter(k => k.startsWith('{base}/'))")
    check(after == [f"{base}/key"], f"{label}: left after clearing: {after}")
    check((H.doc(page, "planned/reset") or {}).get("at"), f"{label}: no reset time")
    keys = H.doc(page, "data/users/u_owner/keys") or {}
    check(tag in keys, f"{label}: the password went too")
    page.screenshot(path=str(H.SHOTS / f"reset_{label}.png"))

    # an unsent change kept in the browser from before the reset doesn't come back
    page.evaluate(f"""() => localStorage.setItem('gazetteer-pending:{tag}',
        JSON.stringify({{about: {{motto: 'Stale motto'}}, __at: 1}}))""")
    open_nation(page, "Seigne", tag)
    page.wait_for_function("app.N.K", timeout=5000)
    time.sleep(1.5)
    ab = H.doc(page, f"{base}/about")
    check(not ab or ab.get("motto") != "Stale motto", f"{label}: an unsent change from before the reset came back: {ab}")
    check(page.evaluate(f"localStorage.getItem('gazetteer-pending:{tag}')") is None, f"{label}: the stale backup stays")
    # a change made after it is saved as usual
    page.click("[data-tab=nation]")
    time.sleep(0.3)
    page.fill("#ab-motto", "A new start")
    ab = wait_doc(page, f"{base}/about", lambda v: v.get("motto") == "A new start")
    check(ab and ab.get("motto") == "A new start", f"{label}: a new change wasn't saved: {ab}")
    ctx.close()
    return errs


def main():
    H.build_site()
    with H.Server(8773) as server, sync_playwright() as p:
        b = p.chromium.launch(executable_path=H.CHROMIUM)
        for size in ((1440, 900), (390, 844)):
            errs = owner(b, server.url, size)
            check(not errs, f"{size}: console errors {errs[:5]}")
        b.close()
    return check.report()


if __name__ == "__main__":
    sys.exit(main())
