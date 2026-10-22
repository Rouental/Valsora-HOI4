"""Taking land away from a releasable (2026-10-22, the author: "There should also be a way to remove terrain from
releasables, I believe you can currently only add"). Until then only the toolbar's "Take them away" chip did it, and the
cards' buttons always opened the tool to add.

On Rouental (map tools open), with the mouse on the map: a releasable of the page's own given three states, a click on
one of them takes it away (the tool adding); a drag that starts on one of its states takes away what it crosses and
adds nothing, one that starts off them adds and takes nothing away. The card's "Take states away" picks the releasable
and the tool's taking-away mode (the chip "Take states away" pressed, its hint saying so), where a click takes a state
away and none is added; the toolbar's chips read "Add states" / "Take states away". A releasable of the game's has the
button too, and keeps its last state (its message). On Belka (map tools closed), a drawn area's button reads "Delete
area 1" and deletes it. Desktop and phone.

    python3 scripts/facts_export.py            # after a build: the map data the page reads
    python3 tests/gazetteer/release_remove.py  # PROBLEMS: none, screenshots in work/gazetteer_test/shots/
"""
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness as H  # noqa: E402
from harness import wait_doc, open_nation, make_password, unfold  # noqa: E402

check = H.Checks()

# three states of Rouental's no releasable holds, two of them side by side, and a pixel of each of those two on their
# shared border (a drag between them crosses no other state)
PICK = """() => {
  const N = app.N, held = s => N.relList.some(r => relGroup(r) === 'rel' && (N.relSets.get(r.id) || new Set()).has(s));
  const free = [...N.states.keys()].filter(s => !held(s) && N.stateToPart[s] === 0);
  for (const a of free) for (const d of N.stateAdj[a]) {
    if (!free.includes(d) || d === a) continue;
    const P = N.parts[0], w = P.w, own = N.nOwn + 2, st = v => v >= 2 && v < own ? N.prov[v - 2].s : -1;
    for (let i = w; i < P.px.length - w; i++) {
      if (st(P.px[i]) !== a || st(P.px[i + 1]) !== d) continue;
      const others = free.filter(s => s !== a && s !== d && ![...N.stateAdj[s]].some(t => t === a || t === d));
      if (others.length < 2) continue;
      const g = j => [P.x0 + j % w, P.y0 + ((j / w) | 0)];
      return { a, d, b: others[0], c: others[1], pa: g(i), pd: g(i + 1), keys: N.stateKey };
    }
  }
  return null;
}"""


def screen(page, gx, gy):
    """the screen point of a game pixel's centre, the map centred on it first"""
    return page.evaluate("""([x, y]) => { locate(x, y); const q = gToScreen(x, y), r = document.getElementById('map').getBoundingClientRect();
        return [r.left + q[0], r.top + q[1]]; }""", [gx, gy])


def click_state(page, s):
    x, y = screen(page, *page.evaluate("s => app.N.states[s].label", s))
    page.mouse.click(x, y)
    time.sleep(0.4)


def held(page, rid):
    return set(page.evaluate("id => [...(app.N.relSets.get(id) || [])]", rid))


def run(b, url, size):
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
    f = page.evaluate(PICK)
    check(f is not None, f"{label}: no free states side by side on Rouental")
    if f is None:
        ctx.close()
        return errs
    a, d, b_, c = f["a"], f["d"], f["b"], f["c"]

    # ---- a releasable of the page's own, three states picked with the card's button and the mouse
    page.click("[data-tab=release]")
    time.sleep(0.4)
    page.click("button:has-text('Add a releasable')")
    time.sleep(0.4)
    page.keyboard.type("Retrait Test")
    rel = wait_doc(page, f"{base}/releasables", lambda v: any(k.startswith("rl-") and x and x.get("name") == "Retrait Test" for k, x in v.items()))
    rid = next(k for k, x in rel.items() if k.startswith("rl-") and x and x.get("name") == "Retrait Test")
    card = f"#pane-release .relcard:has(#rl-name-{rid})"
    check(page.locator(f"{card} button:has-text('Take states away')").count() == 0, f"{label}: Take states away on a releasable with no states")
    page.click(f"{card} button:has-text('Pick its states')")
    time.sleep(0.3)
    check(page.evaluate("app.ui.tool === 'release' && app.ui.relMode === 'add'") and page.evaluate("app.ui.rel") == rid,
          f"{label}: Pick its states didn't open the tool to add")
    chips = page.evaluate("[...document.querySelectorAll('#subtools .tchip')].map(b => b.textContent)")
    check(chips == ["Add states", "Take states away"], f"{label}: the tool's chips: {chips}")
    hint = page.inner_text("#subtools .hinttext")
    check("takes it away" in hint, f"{label}: the hint doesn't say a click takes a state away: {hint}")
    for s in (a, b_, c):
        click_state(page, s)
    check(held(page, rid) == {a, b_, c}, f"{label}: three clicks gave {held(page, rid)}, not {a, b_, c}")

    # ---- a click on one of its states takes it away
    click_state(page, b_)
    check(held(page, rid) == {a, c}, f"{label}: a click on one of its states left {held(page, rid)}")
    rel = wait_doc(page, f"{base}/releasables", lambda v: not (v[rid].get("states") or {}).get(f["keys"][b_]))
    check(rel is not None, f"{label}: the state taken away is still saved")

    # ---- a drag from one of its states onto a free one: takes away, adds nothing
    xa, ya = screen(page, *f["pa"])
    xd, yd = page.evaluate("([x, y]) => { const q = gToScreen(x, y), r = document.getElementById('map').getBoundingClientRect(); return [r.left + q[0], r.top + q[1]]; }", f["pd"])
    page.mouse.move(xa, ya)
    page.mouse.down()
    page.mouse.move(xd, yd, steps=4)
    page.mouse.up()
    time.sleep(0.4)
    check(held(page, rid) == {c}, f"{label}: a drag from its state {a} onto {d} left {held(page, rid)}, not only {c}")
    # ... and back, starting on a free state: adds both, takes nothing away
    page.mouse.move(xd, yd)
    page.mouse.down()
    page.mouse.move(xa, ya, steps=4)
    page.mouse.up()
    time.sleep(0.4)
    check(held(page, rid) == {a, c, d}, f"{label}: a drag from the free {d} onto {a} left {held(page, rid)}")
    page.screenshot(path=str(H.SHOTS / f"release_remove_{label}_drag.png"))

    # ---- the card's Take states away: the tool in its taking-away mode
    page.click(f"{card} button:has-text('Take states away')")
    time.sleep(0.3)
    check(page.evaluate("app.ui.tool === 'release' && app.ui.relMode === 'remove'") and page.evaluate("app.ui.rel") == rid,
          f"{label}: Take states away didn't pick the releasable and the taking-away mode")
    on = page.evaluate("[...document.querySelectorAll('#subtools .tchip')].filter(b => b.getAttribute('aria-pressed') === 'true').map(b => b.textContent)")
    check(on == ["Take states away"], f"{label}: pressed chips: {on}")
    hint = page.inner_text("#subtools .hinttext")
    check("take them away" in hint, f"{label}: the hint in the taking-away mode: {hint}")
    click_state(page, d)
    click_state(page, b_)   # not one of its: nothing is added while taking away
    check(held(page, rid) == {a, c}, f"{label}: taking away left {held(page, rid)}")
    page.screenshot(path=str(H.SHOTS / f"release_remove_{label}_card.png"))

    # ---- a releasable of the game's: the button too; the last state stays
    page.click("[data-tab=release]")
    time.sleep(0.3)
    one = page.evaluate("""() => (app.N.relList.find(r => r.game && r.game.kind === 'releasable'
        && (app.N.relSets.get(r.id) || new Set()).size === 1) || {}).id || null""")
    if one:
        gcard = f"#pane-release .relcard:has(#rl-name-{one})"
        page.locator(f"{gcard} button:has-text('Take states away')").scroll_into_view_if_needed()
        page.click(f"{gcard} button:has-text('Take states away')")
        time.sleep(0.3)
        check(page.evaluate("app.ui.rel") == one and page.evaluate("app.ui.relMode") == "remove", f"{label}: {one}'s Take states away")
        last = next(iter(held(page, one)))
        click_state(page, last)
        check(held(page, one) == {last}, f"{label}: {one} lost its last state")
        check("needs a state" in page.inner_text("#status"), f"{label}: no message for the last state: {page.inner_text('#status')}")
    else:
        check(False, f"{label}: no releasable of the game's with one state")

    # ---- Belka (map tools closed): a drawn area's button deletes it
    page.click("#back")
    time.sleep(0.4)
    make_password(page, "Belka", "BKA")
    open_nation(page, "Belka", "BKA")
    page.wait_for_function("app.N.K", timeout=5000)
    kbase = f"n/BKA/{page.evaluate('app.N.K')}"
    page.click("[data-tab=release]")
    time.sleep(0.4)
    page.click("button:has-text('Add a releasable')")
    time.sleep(0.4)
    page.keyboard.type("Aire Test")
    rel = wait_doc(page, f"{kbase}/releasables", lambda v: any(k.startswith("rl-") and x and x.get("name") == "Aire Test" for k, x in v.items()))
    kid = next(k for k, x in rel.items() if k.startswith("rl-") and x and x.get("name") == "Aire Test")
    page.evaluate("document.activeElement.blur()")   # the pane isn't redrawn under a field being typed in
    page.evaluate("""id => { const s = app.N.states[0], [x, y] = s.label;
        edit('releasables', { [id]: { areas: { 'a-testarea1': [[x - 6, y - 6], [x + 6, y - 6], [x + 6, y + 6], [x - 6, y + 6]] } } }); }""", kid)
    time.sleep(0.4)
    kcard = f"#pane-release .relcard:has(#rl-name-{kid})"
    btn = page.locator(f"{kcard} button:has-text('Delete area 1')")
    check(btn.count() == 1 and "Delete area 1" in (btn.get_attribute("aria-label") or ""), f"{label}: the drawn area's button: {btn.count()} {btn.count() and btn.get_attribute('aria-label')}")
    check(page.locator(f"{kcard} button:has-text('Take states away')").count() == 0, f"{label}: Take states away with the map tools closed")
    page.screenshot(path=str(H.SHOTS / f"release_remove_{label}_area.png"))
    if btn.count():
        btn.click()
        rel = wait_doc(page, f"{kbase}/releasables", lambda v: not (v[kid].get("areas") or {}).get("a-testarea1"))
        check(rel is not None, f"{label}: the area wasn't deleted")
    ctx.close()
    return errs


def main():
    H.build_site()
    with H.Server(8776) as server, sync_playwright() as p:
        b = p.chromium.launch(executable_path=H.CHROMIUM)
        for size in ((1440, 900), (390, 844)):
            errs = run(b, server.url, size)
            check(not errs, f"{size}: console errors {errs[:5]}")
        b.close()
    return check.report()


if __name__ == "__main__":
    sys.exit(main())
