"""Traits asked for on their characters, the author's answers to requests, a leader's description (2026-11-02).

The author: "Created traits should be shown as applied to the character, unless I veto it, in which case it should be
removed"; "When I decline something, I should be given the option to provide an explanation to the person that
submitted it. Maybe a popup the next time they open their gazeteer page?"; and "instead of 'Titles or a few words
(shown on their portrait in game)' You should ask for a character description".

On Arovannea (its requests made into the game: the site's `made`, scripts/requests_made.py), as the owner: the head
of state's box asks for a description, up to 1000 letters; a trait asked for from it is a request for the ruler
("for"), shown on them at once ("being made"); a request of a made trait without "for" shows on the character Claude's
reading gives it ("in the game"), and its card's "Whose trait" moves it; declining asks why, and keeps the reason and
the time (answeredAt), the trait off its character; Done keeps the time. Then a player in a new browser: the
quick-start guide first, then the author's answers (both, the reason with the declined one), OK remembers them, a
reload shows nothing. Desktop and phone.

    python3 scripts/facts_export.py          # after a build: the map data the page reads
    python3 tests/gazetteer/answers.py       # PROBLEMS: none, screenshots in work/gazetteer_test/shots/
"""
import json
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness as H  # noqa: E402
from harness import open_nation, unfold, make_password, wait_doc, pick  # noqa: E402

check = H.Checks()
OWNER = "window.__me = {id: 'u_owner', name: 'The Author', isOwner: true};"
MADE = "New trait: Grandmaster of the Athelian Order"


def reqs(page, base):
    return page.evaluate(f"Object.fromEntries([...window.__store.entries()].filter(([k]) => k.startsWith('{base}/req-')))")


def req_by(page, base, title):
    return next(((k, v) for k, v in reqs(page, base).items() if v.get("title") == title), (None, None))


def owner(b, url, size):
    label = f"{size[0]}"
    ctx, page, errs = H.new_page(b, size, OWNER)
    page.goto(url)
    page.wait_for_selector("#owner:not([hidden])", timeout=20000)
    time.sleep(0.4)
    unfold(page, "Passwords")
    pw = make_password(page, "Arovannea", "AVN")
    open_nation(page, "Arovannea", "AVN")
    page.wait_for_function("app.N.K && app.N.made", timeout=5000)
    base = f"n/AVN/{page.evaluate('app.N.K')}"
    page.click("[data-tab=people]")
    time.sleep(0.4)
    # the description, in place of the titles
    lab = page.inner_text("label[for=pp-ruler-desc]")
    check(lab.startswith("Description") and "Titles" not in lab, f"{label}: the ruler's field reads {lab!r}")
    check(page.get_attribute("#pp-ruler-desc", "maxlength") == "1000", f"{label}: the description's length")
    # a trait asked for from the head of state's box: the ruler's, on them at once
    page.evaluate("document.getElementById('pp-ruler-ask-name').closest('.reqform').previousElementSibling.querySelector('button').click()")
    page.fill("#pp-ruler-ask-name", "Test Serpent")
    page.fill("#pp-ruler-ask-what", "+5% stability")
    page.click(".reqform:has(#pp-ruler-ask-name) button:has-text('Send')")
    time.sleep(0.5)
    k, r = req_by(page, base, "New trait: Test Serpent")
    check(r is not None and r.get("for") == "ruler" and r.get("kind") == "trait", f"{label}: the asked trait's request: {r}")
    page.evaluate("document.activeElement.blur()")
    time.sleep(0.5)
    chips = page.evaluate("[...document.querySelectorAll('#pane-people .tchip.asked')].map(c => c.textContent)")
    check(any("Test Serpent" in c and "being made" in c for c in chips), f"{label}: the asked trait isn't on the ruler: {chips}")
    # a made trait's request without "for": on the theocrats' leader (a sub-ideology picked, as Arovannea's page has),
    # as Claude read it
    page.evaluate("edit('politics', { parties: { theocracy: 'holy_order' } })")
    page.evaluate("t => sendRequest('trait', t, 'For the head of state. stability -10%')", MADE)
    time.sleep(0.6)
    where = page.evaluate("""() => { const p = [...document.querySelectorAll('#pane-people .person')].find(x => x.querySelector('#pp-sub-theocracy'));
        return p ? [...p.querySelectorAll('.tchip.asked')].map(c => c.textContent) : null; }""")
    check(where and any("Grandmaster" in c and "in the game" in c for c in where), f"{label}: the made trait isn't on the theocrats' leader: {where}")
    page.screenshot(path=str(H.SHOTS / f"answers_people_{label}.png"))
    # its card: in the game unless declined, and whose it is
    page.click("[data-tab=nation]")
    time.sleep(0.5)
    card = f"#pane-nation .req:has-text('Grandmaster')"
    check("In the game, unless the author declines it" in page.inner_text(card), f"{label}: the card's line: {page.inner_text(card)[:300]}")
    sel = f"{card} select[aria-label='Whose trait']"
    check(page.input_value(sel) == "party-theocracy", f"{label}: whose: {page.input_value(sel)}")
    pick(page, sel, "ruler")
    k2, r2 = req_by(page, base, MADE)
    r2 = wait_doc(page, k2, lambda v: v.get("for") == "ruler")
    check(r2 and r2.get("for") == "ruler", f"{label}: the trait didn't move to the ruler: {r2}")
    # declined, with a reason: off the character
    page.click(f"{card} button.tchip:has-text('Declined')")
    time.sleep(0.3)
    page.fill(f"{card} .reqform textarea", "Too strong for now")
    page.click(f"{card} .reqform button:has-text('Decline')")
    r2 = wait_doc(page, k2, lambda v: v.get("status") == "declined")
    check(r2 and r2.get("reply") == "Too strong for now" and (r2.get("answeredAt") or 0) > 0, f"{label}: the decline: {r2}")
    page.screenshot(path=str(H.SHOTS / f"answers_cards_{label}.png"))
    page.click(f"#pane-nation .req:has-text('Test Serpent') button.tchip:has-text('Done')")
    r = wait_doc(page, k, lambda v: v.get("status") == "done")
    check(r and (r.get("answeredAt") or 0) > 0, f"{label}: Done: {r}")
    page.click("[data-tab=people]")
    time.sleep(0.5)
    chips = page.evaluate("[...document.querySelectorAll('#pane-people .tchip.asked')].map(c => c.textContent)")
    check(not any("Grandmaster" in c for c in chips) and any("Test Serpent" in c for c in chips), f"{label}: after the decline: {chips}")
    check(page.evaluate("document.getElementById('guide').hidden"), f"{label}: the owner was shown a dialog")
    store = page.evaluate("Object.fromEntries(window.__store)")
    ctx.close()
    return pw, store, errs


def friend(b, url, size, pw, store):
    label = f"{size[0]}"
    init = f"window.__me = {{id: 'u_friend', name: 'A Friend', isOwner: false}}; window.__seed = {json.dumps(store)};"
    ctx, page, errs = H.new_page(b, size, init)
    page.goto(url + "#AVN")
    page.wait_for_function("app.N && app.N.tag === 'AVN' && document.getElementById('loading').hidden", timeout=20000)
    time.sleep(0.4)
    page.fill("#pw-in", pw)
    page.press("#pw-in", "Enter")
    page.wait_for_function("app.N.K", timeout=5000)
    time.sleep(0.6)
    check("Quick start" in page.text_content("#guide-card"), f"{label}: the guide doesn't come first")
    page.click("#guide-card button:has-text('Skip')")
    time.sleep(0.4)
    shown = not page.evaluate("document.getElementById('guide').hidden")
    text = page.text_content("#guide-card") if shown else ""
    check(shown and "From the author" in text, f"{label}: no answers after the guide: {text[:200]}")
    check("Grandmaster" in text and "Too strong for now" in text and "Declined" in text, f"{label}: the declined answer: {text[:400]}")
    check("Test Serpent" in text and "Done" in text, f"{label}: the done answer: {text[:400]}")
    box = page.evaluate("(() => { const r = document.getElementById('guide-card').getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom]; })()")
    check(box[0] >= 0 and box[1] >= 0 and box[2] <= size[0] and box[3] <= size[1] + 1, f"{label}: the answers run off the screen: {box}")
    page.screenshot(path=str(H.SHOTS / f"answers_popup_{label}.png"))
    page.click("#guide-card button:has-text('OK')")
    time.sleep(0.3)
    check(page.evaluate("document.getElementById('guide').hidden"), f"{label}: OK didn't close the answers")
    check(page.evaluate("+localStorage.getItem('gazetteer-answers:AVN') > 0"), f"{label}: the answers aren't remembered")
    page.reload()
    page.wait_for_function("app.N && app.N.tag === 'AVN' && app.N.K", timeout=20000)
    time.sleep(0.8)
    check(page.evaluate("document.getElementById('guide').hidden"), f"{label}: the answers came again after a reload")
    ctx.close()
    return errs


def main():
    H.build_site()
    with H.Server(8777) as server, sync_playwright() as p:
        b = p.chromium.launch(executable_path=H.CHROMIUM)
        for size in ((1440, 900), (390, 844)):
            pw, store, errs = owner(b, server.url, size)
            check(not errs, f"{size}: console errors as the owner {errs[:5]}")
            errs = friend(b, server.url, size, pw, store)
            check(not errs, f"{size}: console errors as a player {errs[:5]}")
        b.close()
    return check.report()


if __name__ == "__main__":
    sys.exit(main())
