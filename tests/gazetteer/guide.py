"""The Gazetteer's quick-start guide (2026-10-16, the author's overnight list: "a short illustrated walkthrough shown
the first time someone opens their nation"): five steps, shown once in a browser the first time a player unlocks a
nation, never to the owner by itself; Next, Back, Skip, Escape; the Guide button shows it again; its map step follows
the nation (map tools open, or the states not drawn yet); it fits a phone.

    python3 scripts/facts_export.py          # after a build: the map data the page reads
    python3 tests/gazetteer/guide.py         # PROBLEMS: none, screenshots in work/gazetteer_test/shots/
"""
import json
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness as H  # noqa: E402
from harness import open_nation, unfold, make_password  # noqa: E402

check = H.Checks()
OWNER = "window.__me = {id: 'u_owner', name: 'The Author', isOwner: true};"


def owner(b, url):
    """passwords for Rouental (its map tools open) and Hollier (its states not drawn yet); the owner sees no guide"""
    ctx, page, errs = H.new_page(b, (1440, 900), OWNER)
    page.goto(url)
    page.wait_for_selector("#owner:not([hidden])", timeout=20000)
    time.sleep(0.4)
    unfold(page, "Passwords")
    pw = {tag: make_password(page, name, tag) for name, tag in (("Rouental", "ROU"), ("Hollier", "HLR"))}
    open_nation(page, "Rouental", "ROU")
    page.wait_for_function("app.N.K", timeout=5000)
    time.sleep(0.5)
    check(page.evaluate("document.getElementById('guide').hidden"), "the owner was shown the guide by itself")
    store = page.evaluate("Object.fromEntries(window.__store)")
    ctx.close()
    return pw, store, errs


def unlock(page, pw):
    page.fill("#pw-in", pw)
    page.press("#pw-in", "Enter")
    page.wait_for_function("app.N.K", timeout=5000)
    time.sleep(0.5)


def shown():
    return "!document.getElementById('guide').hidden"


def friend(b, url, size, theme, pw, store):
    label = f"{size[0]}_{theme}"
    init = f"window.__me = {{id: 'u_friend', name: 'A Friend', isOwner: false}}; window.__seed = {json.dumps(store)};"
    ctx, page, errs = H.new_page(b, size, init, theme=theme)
    page.goto(url + "#ROU")
    page.wait_for_function("app.N && app.N.tag === 'ROU' && document.getElementById('loading').hidden", timeout=20000)
    time.sleep(0.4)
    check(not page.evaluate(shown()), f"{label}: the guide shows before the password")
    unlock(page, pw["ROU"])
    check(page.evaluate(shown()), f"{label}: no guide on the first unlock")
    steps = page.evaluate("guideSteps(app.N).length")
    check(steps == 5, f"{label}: {steps} steps")
    check("Welcome to Rouental" in page.inner_text("#guide-card"), f"{label}: the first step doesn't name the nation")
    # the card has the focus (Next would take the Enter that unlocked the nation: the first test found it skipping a step)
    check(page.evaluate("document.activeElement && document.activeElement.id") == "guide-card", f"{label}: the card isn't focused")
    # the card fits the screen, its picture too
    box = page.evaluate("(() => { const r = document.getElementById('guide-card').getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom]; })()")
    check(box[0] >= 0 and box[1] >= 0 and box[2] <= size[0] and box[3] <= size[1], f"{label}: the card runs off the screen: {box}")
    check(page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), f"{label}: the page scrolls sideways")
    page.screenshot(path=str(H.SHOTS / f"guide_1_{label}.png"))
    page.click("#guide-card button:has-text('Next')")
    time.sleep(0.15)
    text = page.inner_text("#guide-card")
    check("The map and its tools" in text and "Railways" in text, f"{label}: the map step isn't the open map's: {text[:120]}")
    page.screenshot(path=str(H.SHOTS / f"guide_2_{label}.png"))
    page.click("#guide-card button:has-text('Back')")
    time.sleep(0.15)
    check("Welcome to" in page.inner_text("#guide-card"), f"{label}: Back didn't go back")
    for i in range(4):
        page.click("#guide-card button:has-text('Next')")
        time.sleep(0.1)
        page.screenshot(path=str(H.SHOTS / f"guide_{i + 2}_{label}.png"))
    check("Your password" in page.inner_text("#guide-card"), f"{label}: the last step isn't the password's")
    # a key pressed while the guide is open doesn't reach the map (S would pick the Suggest tool)
    tool = page.evaluate("app.ui.tool")
    page.keyboard.press("s")
    check(page.evaluate("app.ui.tool") == tool, f"{label}: a key went through the guide to the map")
    page.click("#guide-card button:has-text('Start')")
    time.sleep(0.2)
    check(not page.evaluate(shown()), f"{label}: Start didn't close the guide")
    check(page.evaluate("localStorage.getItem('gazetteer-guided')") == "1", f"{label}: the guide isn't remembered")
    # not again on this browser: a reload (the password remembered) and another nation
    page.reload()
    page.wait_for_function("app.N && app.N.tag === 'ROU' && app.N.K", timeout=20000)
    time.sleep(0.5)
    check(not page.evaluate(shown()), f"{label}: the guide came back after a reload")
    page.click("#back")
    time.sleep(0.3)
    page.fill("#q", "Hollier")
    time.sleep(0.2)
    open_nation(page, "Hollier", "HLR")
    unlock(page, pw["HLR"])
    check(not page.evaluate(shown()), f"{label}: the guide came back on a second nation")
    # the Guide button shows it again; on Hollier (its states not drawn yet) the map step is the Suggest tool's
    page.click("#guide-btn")
    time.sleep(0.15)
    check(page.evaluate(shown()), f"{label}: the Guide button didn't show it")
    page.click("#guide-card button:has-text('Next')")
    time.sleep(0.15)
    text = page.inner_text("#guide-card")
    check("aren't drawn yet" in text and "Suggest" in text, f"{label}: the map step isn't the closed map's: {text[:120]}")
    page.screenshot(path=str(H.SHOTS / f"guide_closed_{label}.png"))
    page.keyboard.press("Escape")
    time.sleep(0.15)
    check(not page.evaluate(shown()), f"{label}: Escape didn't close the guide")
    check(page.evaluate("document.activeElement && document.activeElement.id") == "guide-btn", f"{label}: the focus didn't go back to the Guide button")
    page.click("#guide-btn")
    page.click("#guide-card button:has-text('Skip')")
    time.sleep(0.15)
    check(not page.evaluate(shown()), f"{label}: Skip didn't close the guide")
    ctx.close()
    return errs


def main():
    H.build_site()
    with H.Server(8774) as server, sync_playwright() as p:
        b = p.chromium.launch(executable_path=H.CHROMIUM)
        pw, store, errs = owner(b, server.url)
        check(not errs, f"owner: console errors {errs[:5]}")
        for size, theme in (((1440, 900), "light"), ((390, 844), "light"), ((1440, 900), "dark"), ((390, 844), "dark")):
            errs = friend(b, server.url, size, theme, pw, store)
            check(not errs, f"{size} {theme}: console errors {errs[:5]}")
        b.close()
    return check.report()


if __name__ == "__main__":
    sys.exit(main())
