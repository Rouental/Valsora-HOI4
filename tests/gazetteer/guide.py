"""The Gazetteer's quick-start guide (2026-10-16, the author's overnight list: "a short illustrated walkthrough shown
the first time someone opens their nation"): six steps (the province sizes since 2026-10-17), shown once in a browser the first time a player unlocks a
nation, never to the owner by itself; Next, Back, Skip, Escape; the Guide button shows it again; its map step follows
the nation (map tools open, or the states not drawn yet); it fits a phone. And the size guides: the province's
(2026-10-17, the author: "maybe there should be a guide for province size?") and the state's, which comes first
(2026-10-18: "More important than the guide for provinces is the guide for states ... Cardonia's states are about the
ideal size"): the state step, the ruler's two rows beside the zoom buttons at the map's zoom, the Map tab's two
sections, and a suggested area's size against Cardonia's states and in provinces. And the Suggestions button, which
hides what was drawn with Suggest (2026-10-18: "I wasn't able to see the provinces beneath them").

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
    """passwords for Rouental (its map tools open) and Kieska (its states not drawn yet; Hollier until 2026-10-17); the owner sees no guide"""
    ctx, page, errs = H.new_page(b, (1440, 900), OWNER)
    page.goto(url)
    page.wait_for_selector("#owner:not([hidden])", timeout=20000)
    time.sleep(0.4)
    unfold(page, "Passwords")
    pw = {tag: make_password(page, name, tag) for name, tag in (("Rouental", "ROU"), ("Kieska", "KSK"))}
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
    check(steps == 6, f"{label}: {steps} steps")
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
    for i in range(5):
        page.click("#guide-card button:has-text('Next')")
        time.sleep(0.1)
        page.screenshot(path=str(H.SHOTS / f"guide_{i + 2}_{label}.png"))
        if i == 1:  # the state sizes: three pictures loaded, the card on the screen
            text = page.inner_text("#guide-card")
            check("How big is a state?" in text and "Cardonia" in text and "Zukchiva" in text and "provinces" in text,
                  f"{label}: the sizes step: {text[:160]}")
            pics = page.evaluate("[...document.querySelectorAll('#guide-card .statepics img')].map(i => i.complete && i.naturalWidth)")
            check(len(pics) == 3 and all(pics), f"{label}: the sizes step's pictures: {pics}")
            box = page.evaluate("(() => { const r = document.getElementById('guide-card').getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom]; })()")
            check(box[0] >= 0 and box[1] >= 0 and box[2] <= size[0] and box[3] <= size[1], f"{label}: the sizes card runs off the screen: {box}")
    check("Your password" in page.inner_text("#guide-card"), f"{label}: the last step isn't the password's")
    # a key pressed while the guide is open doesn't reach the map (S would pick the Suggest tool)
    tool = page.evaluate("app.ui.tool")
    page.keyboard.press("s")
    check(page.evaluate("app.ui.tool") == tool, f"{label}: a key went through the guide to the map")
    page.click("#guide-card button:has-text('Start')")
    time.sleep(0.2)
    check(not page.evaluate(shown()), f"{label}: Start didn't close the guide")
    sizes(page, label, size)
    check(page.evaluate("localStorage.getItem('gazetteer-guided')") == "1", f"{label}: the guide isn't remembered")
    # not again on this browser: a reload (the password remembered) and another nation
    page.reload()
    page.wait_for_function("app.N && app.N.tag === 'ROU' && app.N.K", timeout=20000)
    time.sleep(0.5)
    check(not page.evaluate(shown()), f"{label}: the guide came back after a reload")
    page.click("#back")
    time.sleep(0.3)
    page.fill("#q", "Kieska")
    time.sleep(0.2)
    open_nation(page, "Kieska", "KSK")
    unlock(page, pw["KSK"])
    check(not page.evaluate(shown()), f"{label}: the guide came back on a second nation")
    # the Guide button shows it again; on Kieska (its states not drawn yet) the map step is the Suggest tool's
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


def sizes(page, label, size):
    """the ruler (states and provinces), the Map tab's sections, a suggested area's size, the Suggestions button"""
    check(page.evaluate("document.getElementById('sizes').hidden"), f"{label}: the ruler shows before it is asked for")
    page.click("#sizebtn")
    rows = lambda: page.evaluate("""[...document.querySelectorAll('#sizes .szrow')].map(r => [r.className,
        [...r.querySelectorAll('.sq')].map(e => e.getBoundingClientRect().width)])""")
    for _ in range(4):  # close enough for both rows to show
        if all(len(sq) == 3 for _, sq in rows()):
            break
        page.click("#zin")
        time.sleep(0.15)
    got = dict((c.split()[-1], sq) for c, sq in rows())
    sq, st = got.get("szprov", []), got.get("szstates", [])
    check(len(sq) == 3 and sq[0] < sq[1] < sq[2], f"{label}: the ruler's province squares: {sq}")
    check(len(st) == 3 and st[0] < st[1] < st[2], f"{label}: the ruler's state squares: {st}")
    z = page.evaluate("[app.index.sizes.usual, app.index.sizes.states.usual, app.view.s]")
    if len(sq) == 3:
        check(abs(sq[1] - (z[0] ** 0.5) * z[2]) < 1.5, f"{label}: the usual province square isn't to scale: {sq[1]} at zoom {z[2]}")
    if len(st) == 3:
        check(abs(st[1] - (z[1] ** 0.5) * z[2]) < 1.5, f"{label}: Cardonia's state square isn't to scale: {st[1]} at zoom {z[2]}")
    check("States" in page.inner_text("#sizes") and "Provinces" in page.inner_text("#sizes"), f"{label}: the ruler's rows aren't named")
    page.click("#zin")
    time.sleep(0.15)
    sq2 = dict((c.split()[-1], q) for c, q in rows()).get("szprov", [])
    check(not sq2 or (len(sq) == 3 and sq2[1] > sq[1]) or "Zoom out" in page.inner_text("#sizes"), f"{label}: the ruler didn't follow the zoom: {sq} -> {sq2}")
    r = page.evaluate("(() => { const a = document.getElementById('sizes').getBoundingClientRect(), b = document.querySelector('.mapctl').getBoundingClientRect(); return [a.right, b.left, a.left]; })()")
    check(r[0] <= r[1] and r[2] >= 0, f"{label}: the ruler runs into the zoom buttons or off the map: {r}")
    page.screenshot(path=str(H.SHOTS / f"sizes_ruler_{label}.png"))
    page.click("#sizebtn")
    check(page.evaluate("document.getElementById('sizes').hidden"), f"{label}: the ruler didn't hide")
    # the Map tab: the two sections, the state's first, folded, keep their fold when the pane is drawn again; a suggested
    # area's size
    page.evaluate("showTab('map')")
    time.sleep(0.2)
    secs = page.evaluate("[...document.querySelectorAll('#pane-map .sizesec summary')].map(e => e.textContent)")
    check(secs == ["How big is a state?", "How big is a province?"], f"{label}: the Map tab's size sections: {secs}")
    page.evaluate("document.querySelector('#pane-map .statesec summary').click()")
    page.evaluate("document.querySelector('#pane-map .provsec summary').click()")
    page.evaluate("""edit('suggest', {s_test1: {type: 'area', pts: [[600, 780], [700, 780], [700, 840], [600, 840]], label: 'A test', note: ''}})""")
    time.sleep(0.3)
    page.evaluate("renderMapPane(true)")
    time.sleep(0.2)
    check(page.evaluate("document.querySelector('#pane-map .statesec').open && document.querySelector('#pane-map .provsec').open"),
          f"{label}: a section folded when the pane was drawn again")
    pics = page.evaluate("[...document.querySelectorAll('#pane-map .statesec img')].map(i => i.complete && i.naturalWidth)")
    check(len(pics) == 3 and all(pics), f"{label}: the Map tab's state pictures: {pics}")
    text = page.inner_text("#pane-map")
    want = "About 6,000 map pixels: larger than most of Cardonia's states (820 to 1,840), 4.6 times the usual one; 38 provinces of Cardonia"
    check(want in text, f"{label}: the area's size: {[l for l in text.splitlines() if 'map pixels' in l][:2]}")
    page.screenshot(path=str(H.SHOTS / f"sizes_pane_{label}.png"), full_page=False)
    suggestions(page, label)
    page.evaluate("edit('suggest', {s_test1: null})")


def suggestions(page, label):
    """the Suggestions button hides what was drawn with Suggest, so the provinces under it show; the Suggest tool and
    Show bring it back"""
    page.evaluate("app.ui.sel.sug = null; renderBase(); requestDraw()")
    time.sleep(0.3)
    check(not page.evaluate("document.getElementById('sugbtn').hidden"), f"{label}: no Suggestions button with a suggestion drawn")
    px = "(() => { const c = document.getElementById('map'), r = c.getBoundingClientRect(); const q = gToScreen(650, 810); " \
         "const d = window.devicePixelRatio || 1; return q ? [...c.getContext('2d').getImageData(Math.round(q[0] * d), Math.round(q[1] * d), 1, 1).data] : null; })()"
    page.evaluate("locate(650, 810)")
    time.sleep(0.4)
    before = page.evaluate(px)
    page.click("#sugbtn")
    time.sleep(0.4)
    check(page.evaluate("document.getElementById('sugbtn').getAttribute('aria-pressed')") == "false", f"{label}: the button isn't off")
    after = page.evaluate(px)
    check(before and after and before != after, f"{label}: hiding the suggestions didn't change the map under one: {before} {after}")
    check(page.evaluate("sugAtScreen(...gToScreen(600, 780)) === null"), f"{label}: a hidden suggestion can still be clicked")
    page.screenshot(path=str(H.SHOTS / f"sug_hidden_{label}.png"))
    page.evaluate("setTool('suggest')")
    time.sleep(0.2)
    check(page.evaluate("!app.ui.hideSug && document.getElementById('sugbtn').getAttribute('aria-pressed') === 'true'"),
          f"{label}: the Suggest tool didn't bring the suggestions back")
    page.evaluate("setTool('select')")
    page.click("#sugbtn")
    page.evaluate("selectSug('s_test1')")
    time.sleep(0.2)
    check(page.evaluate("!app.ui.hideSug"), f"{label}: showing a suggestion didn't bring them back")


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
