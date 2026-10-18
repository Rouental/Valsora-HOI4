"""The Gazetteer's main flows, driven in Chromium with a stand-in for claude.ai's runtime (mock.js).

The owner makes passwords, adds a nation not on the map yet, fills in Rouental (mainland and its islands), Seigne's
people and a planned nation's suggestions, changes a password; then a friend, in another browser with the same atlas,
is locked out until they type the password. Desktop and phone, light and dark.

    python3 scripts/facts_export.py          # after a build: the map data the page reads
    python3 tests/gazetteer/run.py           # PROBLEMS: none, screenshots in work/gazetteer_test/shots/

(python3 tests/gazetteer/run.py friend runs the friend's part again on the owner's last atlas.)"""
import base64
import hashlib
import json
import re
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness as H  # noqa: E402

OUT = H.SHOTS
PICS = H.WORK
URL = None            # the local server's, set in main()
MOCK = H.MOCK
problems = []


def norm(pw):
    s = re.sub(r"[\s_.,]+", "-", pw.lower())
    return re.sub(r"-+", "-", s).strip("-")


def key(tag, pw):
    return hashlib.sha256(f"valsora-gazetteer|{tag}|{norm(pw)}".encode()).hexdigest()[:32]


def check(cond, msg):
    if not cond:
        problems.append(msg)
    return cond


def doc(page, path):
    return page.evaluate("p => { const v = window.__store.get(p); return v === undefined ? null : v; }", path)


def wait_doc(page, path, pred, timeout=6.0):
    end = time.time() + timeout
    v = None
    while time.time() < end:
        v = doc(page, path)
        try:
            if v is not None and pred(v):
                return v
        except (KeyError, TypeError, AttributeError):
            pass
        time.sleep(0.15)
    return v


def canvas_point(page, js_g):
    """screen point of a game pixel given by a JS expression returning [gx, gy]"""
    return page.evaluate(f"""() => {{ const g = {js_g}; const q = gToScreen(g[0], g[1]);
        const r = document.getElementById('map').getBoundingClientRect(); return [r.left + q[0], r.top + q[1]]; }}""")


BLOBS = {}  # uploaded pictures, shared by every browser like the platform's /_blob/<id>


def new_page(b, theme, size, init):
    ctx = b.new_context(viewport={"width": size[0], "height": size[1]}, color_scheme=theme,
                        device_scale_factor=1, has_touch=size[0] < 600, is_mobile=size[0] < 600)
    ctx.expose_function("__putBlob", lambda i, b64, ct: BLOBS.__setitem__(i, (base64.b64decode(b64), ct)))
    ctx.route("**/_blob/*", lambda route: route.fulfill(body=BLOBS[route.request.url.rsplit("/", 1)[1]][0],
                                                        content_type=BLOBS[route.request.url.rsplit("/", 1)[1]][1])
              if route.request.url.rsplit("/", 1)[1] in BLOBS else route.fulfill(status=404, body="no such blob"))
    ctx.add_init_script(init + MOCK)
    page = ctx.new_page()
    errs = []
    page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errs.append(str(e)))
    page.on("requestfailed", lambda r: errs.append("failed " + r.url[:90]) if "fonts.g" not in r.url else None)
    page.on("response", lambda r: errs.append(f"{r.status} {r.url[:90]}") if r.status >= 400 and "favicon" not in r.url else None)
    return ctx, page, errs


def open_nation(page, name, tag):
    page.click(f".nrow:has-text('{name}')")
    page.wait_for_function(f"app.N && app.N.tag === '{tag}' && document.getElementById('loading').hidden", timeout=20000)
    time.sleep(0.4)


def unfold(page, label):
    """open one of the owner's sections (a click on an open one would close it)"""
    if not page.evaluate("l => [...document.querySelectorAll('#owner details')].find(d => d.querySelector('summary').textContent.startsWith(l)).open", label):
        page.click(f"#owner summary:has-text('{label}')")


def pick(page, selector, value):
    page.focus(selector)
    page.select_option(selector, value)


def upload(page, click_selector, path):
    with page.expect_file_chooser() as fc:
        page.click(click_selector)
    fc.value.set_files(str(path))


def make_password(page, name, tag, label="Make one"):
    page.fill("#own-filter", name)
    time.sleep(0.2)
    page.click(f".pwrow:has-text('{name}') button:has-text('{label}')")
    keys = wait_doc(page, "data/users/u_owner/keys", lambda v: tag in v)
    return keys.get(tag) if keys else None


def owner(b, theme, size, name, full=True):
    ctx, page, errs = new_page(b, theme, size, "window.__me = {id: 'u_owner', name: 'The Author', isOwner: true};")
    page.goto(URL)
    page.wait_for_selector(".nrow", timeout=20000)
    page.wait_for_selector("#owner:not([hidden])", timeout=8000)
    time.sleep(0.5)
    page.screenshot(path=str(OUT / f"{name}_home.png"))
    unfold(page, "Passwords")
    pw_rou = make_password(page, "Rouental", "ROU")
    check(pw_rou and re.fullmatch(r"[a-z]+-[a-z]+-[a-z]+-\d\d", pw_rou), f"{name}: odd password {pw_rou}")
    K = key("ROU", pw_rou)
    check(doc(page, f"n/ROU/{K}/key") is not None, f"{name}: no key document for ROU")
    pw_sgn = make_password(page, "Seigne", "SGN")
    # a nation not on the map yet: refused tags first
    unfold(page, "Nations not on the map yet")
    for tag, nm, want in (("GER", "Germania", "base game"), ("ROU", "Again", "taken"), ("x1", "Bad", "three capital")):
        page.fill("#own-tag", tag)
        page.fill("#own-name", nm)
        page.click("#owner button:has-text('Add')")
        time.sleep(0.3)
        msg = page.inner_text("#owner")
        check(want in msg, f"{name}: adding {tag} said nothing about '{want}'")
    page.fill("#own-tag", "QZX")
    page.fill("#own-name", "Testonia")
    pick(page, "#own-cont", "Solitas")
    page.click("#owner button:has-text('Add')")
    pl = wait_doc(page, "planned/list", lambda v: "QZX" in v)
    check(pl and pl["QZX"]["name"] == "Testonia" and pl["QZX"]["continent"] == "Solitas", f"{name}: planned nation not saved: {pl}")
    time.sleep(0.4)
    check("Testonia added" in page.inner_text("#owner"), f"{name}: no message after adding")
    check(page.locator(".nrow:has-text('Testonia')").count() == 1, f"{name}: Testonia not in the list")
    page.screenshot(path=str(OUT / f"{name}_owner.png"), full_page=True)
    if not full:
        b_close(ctx)
        return errs, {}

    # ---- Rouental, unlocked by the owner's key
    open_nation(page, "Rouental", "ROU")
    page.wait_for_function("app.N.K", timeout=5000)
    check(page.evaluate("document.getElementById('lock').hidden"), f"{name}: lock shown to the owner")
    base = f"n/ROU/{K}"
    page.screenshot(path=str(OUT / f"{name}_desk.png"))
    x, y = canvas_point(page, "app.N.states[[...app.N.states.keys()].find(s => s >= 5 && app.N.stateToPart[s] === 0 && app.N.cities.every(c => Math.hypot(c.x - app.N.states[s].label[0], c.y - app.N.states[s].label[1]) > 14))].label")
    page.mouse.click(x, y)
    page.wait_for_selector("#st-name")
    page.fill("#st-name", "Testville")
    page.fill("#st-pop", "1234567")
    page.fill("#st-b-civ", "3")
    page.fill("#st-r-oil", "12")
    w = wait_doc(page, f"{base}/states", lambda v: '"oil":12' in json.dumps(v, separators=(",", ":")) and "1234567" in json.dumps(v))
    check(w and "Testville" in json.dumps(w), f"{name}: state facts not saved: {w}")
    page.screenshot(path=str(OUT / f"{name}_state.png"))
    # terrain
    page.click("[data-tool=terrain]")
    page.click(".tchip:has-text('Mountains')")
    x0, y0 = canvas_point(page, "app.N.states[[...app.N.states.keys()].find(s => s >= 5 && app.N.stateToPart[s] === 0 && app.N.cities.every(c => Math.hypot(c.x - app.N.states[s].label[0], c.y - app.N.states[s].label[1]) > 14))].label")
    page.mouse.move(x0 - 30, y0)
    page.mouse.down()
    for k in range(12):
        page.mouse.move(x0 - 30 + k * 6, y0 + (k % 3) * 3)
    page.mouse.up()
    t = wait_doc(page, f"{base}/provinces", lambda v: "mountain" in json.dumps(v))
    check(t and "mountain" in json.dumps(t), f"{name}: terrain not saved: {t}")
    page.click("[data-mode=terrain]")
    time.sleep(0.3)
    page.screenshot(path=str(OUT / f"{name}_terrain.png"))
    # the neighbours' terrain (2026-10-18): the switch under the map colours their land by its terrain
    nb = page.evaluate("() => !!(app.N.otherT && app.N.otherT.length === app.N.others.length)")
    check(nb, f"{name}: the nation's map data has no terrain for its neighbours' provinces")
    if page.query_selector(".legend .nbterr"):
        hidden = not page.is_visible("#legend")
        if hidden:                                   # phones start with the map's key folded away
            page.click("#keybtn")
        page.click(".legend .nbterr")
        time.sleep(0.3)
        check(page.evaluate("() => app.ui.nbTerrain === true"), f"{name}: the neighbours' terrain switch did nothing")
        page.screenshot(path=str(OUT / f"{name}_terrain_neighbours.png"))
        page.click(".legend .nbterr")
        if hidden:
            page.click("#keybtn")
    else:
        check(False, f"{name}: no neighbours' terrain switch in the terrain mode's legend")
    page.click("[data-mode=states]")
    # a city, made the capital
    page.click("[data-tool=city]")
    anchor = page.evaluate("""() => { const N = app.N; for (let i = 0; i < N.nOwn; i++) { if (!N.cityInProv.has(i) && N.prov[i].area > 120 && N.stateToPart[N.prov[i].s] === app.ui.part) return [N.prov[i].x, N.prov[i].y]; } }""")
    x, y = canvas_point(page, json.dumps(anchor))
    page.mouse.click(x, y)
    time.sleep(0.3)
    page.keyboard.type("Nouvelle Ville")
    c = wait_doc(page, f"{base}/cities", lambda v: "Nouvelle Ville" in json.dumps(v, ensure_ascii=False))
    check(c and "Nouvelle Ville" in json.dumps(c, ensure_ascii=False) and "Vair" in json.dumps(c, ensure_ascii=False),
          f"{name}: city not saved (or the map's cities not copied): {str(c)[:200]}")
    page.click(".item.sel button:has-text('Capital')")
    c = wait_doc(page, f"{base}/cities", lambda v: [k for k, x in v.items() if x and x.get("capital") and x["name"] == "Nouvelle Ville"])
    caps = [k for k, v in (c or {}).items() if v and v.get("capital")]
    check(len(caps) == 1 and c[caps[0]]["name"] == "Nouvelle Ville", f"{name}: capital not set right: {caps}")
    # a river: three clicks and Enter
    page.click("[data-tool=river]")
    for dx, dy in ((-40, -30), (0, 0), (40, 25)):
        page.mouse.click(x0 + dx, y0 + dy)
        time.sleep(0.35)
    page.keyboard.press("Enter")
    r = wait_doc(page, f"{base}/rivers", lambda v: '"kind": "major"' in json.dumps(v))
    check(r, f"{name}: river not saved: {r}")
    # a railway between two cities
    page.click("[data-tool=rail]")
    cities = page.evaluate("app.N.cityList.filter(c => c.prov >= 0 && app.N.stateToPart[c.s] === 0).slice(0, 2).map(c => [c.x, c.y])")
    for g in cities:
        x, y = canvas_point(page, json.dumps(g))
        page.mouse.click(x, y)
        time.sleep(0.4)
    page.keyboard.press("Enter")
    rl = wait_doc(page, f"{base}/rails", lambda v: len(v) >= 1)
    pts = [v["pts"] for v in (rl or {}).values()]
    check(pts and [list(p) for p in pts[0]] == [list(g) for g in cities], f"{name}: railway not saved or not snapped: {pts} vs {cities}")
    # a supply hub, undone, done again
    page.click("[data-tool=hub]")
    x0, y0 = canvas_point(page, "app.N.states[[...app.N.states.keys()].find(s => s >= 5 && app.N.stateToPart[s] === 0 && app.N.cities.every(c => Math.hypot(c.x - app.N.states[s].label[0], c.y - app.N.states[s].label[1]) > 14))].label")
    page.mouse.click(x0, y0)
    t = wait_doc(page, f"{base}/provinces", lambda v: '"hub": true' in json.dumps(v))
    check(t and '"hub": true' in json.dumps(t), f"{name}: hub not saved")
    page.click("#undo")
    t = wait_doc(page, f"{base}/provinces", lambda v: '"hub": true' not in json.dumps(v))
    check('"hub": true' not in json.dumps(t), f"{name}: undo didn't remove the hub")
    page.mouse.click(x0, y0)
    time.sleep(1.0)
    # a suggestion on the mainland: a point
    page.click("[data-tool=suggest]")
    page.click(".tchip:has-text('Point')")
    x, y = canvas_point(page, "[app.N.states[[...app.N.states.keys()].find(s => s >= 5 && app.N.stateToPart[s] === 0 && app.N.cities.every(c => Math.hypot(c.x - app.N.states[s].label[0], c.y - app.N.states[s].label[1]) > 14))].label[0] + 12, app.N.states[[...app.N.states.keys()].find(s => s >= 5 && app.N.stateToPart[s] === 0 && app.N.cities.every(c => Math.hypot(c.x - app.N.states[s].label[0], c.y - app.N.states[s].label[1]) > 14))].label[1] - 9]")
    page.mouse.click(x, y)
    sg = wait_doc(page, f"{base}/suggest", lambda v: any(x and x.get("type") == "point" for x in v.values()))
    check(sg, f"{name}: point suggestion not saved: {sg}")
    time.sleep(0.3)
    page.keyboard.type("A watchtower here")
    sg = wait_doc(page, f"{base}/suggest", lambda v: any(x and x.get("label") == "A watchtower here" for x in v.values()))
    check(sg and any(x and x.get("label") == "A watchtower here" for x in sg.values()), f"{name}: suggestion label not saved: {sg}")
    page.click("[data-tool=select]")
    page.screenshot(path=str(OUT / f"{name}_lines.png"))
    # the islands: their own inset box
    n_insets = page.locator("#insets .inset").count()
    check(n_insets == 3, f"{name}: Rouental should have 3 boxes (mainland, islands, world), has {n_insets}")
    page.locator("#insets .inset").nth(1).click()
    time.sleep(0.4)
    check(page.evaluate("app.ui.part") == 1, f"{name}: the islands' box didn't open them")
    page.screenshot(path=str(OUT / f"{name}_islands.png"))
    s_isl = page.evaluate("app.N.parts[1].states[0]")
    far = page.evaluate(f"""(() => {{ const N = app.N, P = curPart(), own = N.nOwn + 2; let best = null, bd = -1;
        for (let i = 0; i < P.px.length; i++) {{ const v = P.px[i]; if (v < 2 || v >= own || N.prov[v - 2].s !== {s_isl}) continue;
          const gx = (P.x0 + i % P.w) % W, gy = P.y0 + ((i / P.w) | 0), q = gToScreen(gx, gy); if (!q) continue;
          const d = Math.min(1e9, ...N.cityList.map(c => {{ const r = gToScreen(c.x, c.y); return r ? Math.hypot(r[0] - q[0], r[1] - q[1]) : 1e9; }}));
          if (d > bd) {{ bd = d; best = [gx, gy]; }} }}
        return best; }})()""")  # the state's pixel farthest from its cities (a click on a city picks the city)
    x, y = canvas_point(page, json.dumps(far))
    page.mouse.click(x, y)
    page.wait_for_selector("#st-name")
    page.fill("#st-pop", "4321")
    w = wait_doc(page, f"{base}/states", lambda v: "4321" in json.dumps(v))
    check(w and "4321" in json.dumps(w), f"{name}: the islands' state not saved")
    page.click("[data-tool=city]")
    isl = page.evaluate(f"(() => {{ const N = app.N, p = N.states[{s_isl}].provs.find(p => !N.cityInProv.has(p)); return p == null ? null : [N.prov[p].x, N.prov[p].y]; }})()")
    if isl:
        x, y = canvas_point(page, json.dumps(isl))
        page.mouse.click(x, y)
        time.sleep(0.3)
        page.keyboard.type("Port Volonté")
        c = wait_doc(page, f"{base}/cities", lambda v: "Port Volonté" in json.dumps(v, ensure_ascii=False))
        check(c and "Port Volonté" in json.dumps(c, ensure_ascii=False), f"{name}: the islands' city not saved")
    page.click("[data-tool=select]")
    # the world map: an area suggestion
    page.locator("#insets .inset").nth(2).click()
    time.sleep(0.4)
    if not check(page.evaluate("app.N.parts[app.ui.part].world === true"), f"{name}: the world box didn't open the world"):
        print("DEBUG part", page.evaluate("app.ui.part"), page.evaluate("[...document.querySelectorAll('#insets .inset')].map(b => [b.getAttribute('aria-pressed'), Math.round(b.getBoundingClientRect().left), Math.round(b.getBoundingClientRect().top)])"),
              page.evaluate("(() => { const r = document.getElementById('insets').getBoundingClientRect(); return [r.left, r.top, document.activeElement && document.activeElement.id, document.getElementById('desk').scrollTop]; })()"))
        page.screenshot(path=str(OUT / f"{name}_DEBUG.png"))
    tools = page.evaluate("[...document.querySelectorAll('.tool')].filter(b => !b.hidden).map(b => b.dataset.tool)")
    check(tools == ["select", "suggest"], f"{name}: tools on the world map: {tools}")
    page.click("[data-tool=suggest]")
    page.click(".tchip:has-text('Area')")
    page.evaluate("locate(1730, 1720)")  # zoomed in, as a person would before drawing
    time.sleep(0.3)
    for g in ((1700, 1700), (1760, 1700), (1760, 1750)):
        x, y = canvas_point(page, json.dumps(g))
        page.mouse.click(x, y)
        time.sleep(0.35)
    page.keyboard.press("Enter")
    sg = wait_doc(page, f"{base}/suggest", lambda v: any(x and x.get("type") == "area" for x in v.values()))
    check(sg and any(x and x.get("type") == "area" and len(x["pts"]) == 3 for x in sg.values()), f"{name}: area suggestion not saved: {sg}")
    time.sleep(0.3)
    page.keyboard.type("More islands for Concorde")
    time.sleep(1.0)
    page.screenshot(path=str(OUT / f"{name}_world.png"))
    page.click("[data-tool=select]")
    page.locator("#insets .inset").nth(0).click()
    time.sleep(0.3)
    # politics
    page.click("[data-tab=politics]")
    page.fill("#pol-n-democratic-def", "the Free Republic of Testland")
    pol = wait_doc(page, f"{base}/politics", lambda v: v["names"]["democratic"]["def"] == "the Free Republic of Testland")
    check(pol and pol["names"]["democratic"]["def"] == "the Free Republic of Testland", f"{name}: politics not saved: {pol}")
    check(not page.evaluate("!!document.getElementById('pol-ruling')"), f"{name}: Rouental's hand-made rulers are editable")
    page.screenshot(path=str(OUT / f"{name}_politics.png"))
    # people: a general
    page.click("[data-tab=people]")
    page.click("button:has-text('Add a character')")
    time.sleep(0.3)
    page.keyboard.type("Général Test")
    pp = wait_doc(page, f"{base}/people", lambda v: any(x and x.get("name") == "Général Test" for x in v.values()))
    check(pp and any(x and x.get("name") == "Général Test" and x.get("role") == "general" for x in pp.values()), f"{name}: character not saved: {pp}")
    upload(page, "#pane-people .person .portrait", PICS / "test_portrait.png")
    pp = wait_doc(page, f"{base}/people", lambda v: any(x and x.get("portrait") for x in v.values()))
    check(pp and any(x and (x.get("portrait") or {}).get("asset") for x in pp.values()), f"{name}: character portrait not saved: {pp}")
    time.sleep(0.4)
    page.screenshot(path=str(OUT / f"{name}_people.png"))
    # nation: flag, about, a request, the status, a file
    page.click("[data-tab=nation]")
    upload(page, "#pane-nation .flagslot >> nth=0 >> button:has-text('Send a picture')", PICS / "test_flag.png")
    fl = wait_doc(page, f"{base}/flags", lambda v: v.get("base"))
    check(fl and fl["base"].get("asset") and fl["base"]["w"] == 164, f"{name}: flag not saved: {fl}")
    upload(page, "#pane-nation .flagslot >> nth=2 >> button:has-text('Send a picture')", PICS / "test_big.png")
    fl = wait_doc(page, f"{base}/flags", lambda v: len(v) >= 2, timeout=12)
    big = [v for k, v in (fl or {}).items() if k != "base"]
    check(big and big[0]["w"] == 2200, f"{name}: big picture not saved: {fl}")
    sizes = page.evaluate("[...window.__assets.values()].map(a => a.size)")
    check(sizes and max(sizes) < 4.5e6, f"{name}: the big picture wasn't made smaller: {sizes}")
    page.fill("#ab-motto", "Toujours la Vallée")
    ab = wait_doc(page, f"{base}/about", lambda v: v.get("motto") == "Toujours la Vallée")
    check(ab, f"{name}: motto not saved: {ab}")
    pick(page, "#rq-kind", "subject")
    page.fill("#rq-title", "A march-state subject type")
    page.fill("#rq-details", "Like a puppet, but it keeps its army.")
    page.click("text=Send request")
    time.sleep(0.6)
    rq = page.evaluate(f"[...window.__store.keys()].filter(k => k.startsWith('{base}/req-')).map(k => window.__store.get(k))")
    check(len(rq) == 1 and rq[0]["kind"] == "subject" and rq[0]["tag"] == "ROU" and rq[0]["t"] == "req", f"{name}: request not saved: {rq}")
    page.click(".seg button:has-text('Finished')")
    meta = wait_doc(page, f"{base}/meta", lambda v: v.get("status") == "done")
    check(meta and meta.get("status") == "done" and "u_owner" in meta.get("editors", {}) and meta.get("t") == "meta", f"{name}: meta not saved: {meta}")
    page.click("button:has-text('Save a file')")
    time.sleep(0.5)
    saved = page.evaluate("window.__saved")
    if saved:
        (OUT / f"{name}_saved_one.json").write_text(saved["data"])
    check(saved and "Testville" in saved["data"] and "Nouvelle Ville" in saved["data"] and "Toujours" in saved["data"],
          f"{name}: file save wrong: {str(saved)[:200]}")
    page.screenshot(path=str(OUT / f"{name}_nation.png"))
    nation_full = page.locator("#pane-nation")
    page.evaluate("document.getElementById('pane-nation').scrollTop = 1e6")
    time.sleep(0.2)
    page.screenshot(path=str(OUT / f"{name}_nation_end.png"))

    # ---- Seigne: a generated ruler, now the author's choice
    page.click("#back")
    open_nation(page, "Seigne", "SGN")
    page.wait_for_function("app.N.K", timeout=5000)
    Ks = key("SGN", pw_sgn)
    page.click("[data-tab=politics]")
    pick(page, "#pol-ruling", "liberalism")
    pol = wait_doc(page, f"n/SGN/{Ks}/politics", lambda v: v.get("ruling") == "liberalism")
    check(pol, f"{name}: SGN ruling not saved")
    page.click("[data-tab=people]")
    page.fill("#pp-ruler-name", "Jeanne Testeuse")
    page.fill("#pp-ruler-desc", "Countess of Seigne, Lady of the Silver Ford")
    pick(page, "#pp-sub-communism", "leninism")
    time.sleep(0.8)
    page.fill("#pp-name-communism", "Pierre Rouge")
    upload(page, "#pane-people .person >> nth=0 >> .portrait", PICS / "test_portrait.png")
    pp = wait_doc(page, f"n/SGN/{Ks}/people", lambda v: v["ruler"]["portrait"]["asset"] and v["party-communism"]["name"] == "Pierre Rouge")
    check(pp and pp["ruler"]["name"] == "Jeanne Testeuse" and pp["ruler"]["desc"].startswith("Countess")
          and pp["ruler"]["portrait"]["asset"] and pp["party-communism"]["name"] == "Pierre Rouge", f"{name}: SGN people not saved: {pp}")
    pol = doc(page, f"n/SGN/{Ks}/politics")
    check(pol and pol.get("parties", {}).get("communism") == "leninism", f"{name}: SGN party not saved: {pol}")
    time.sleep(0.4)
    page.screenshot(path=str(OUT / f"{name}_people_sgn.png"))

    # ---- home: requests, suggestions, every nation in a file, a new password
    page.click("#back")
    time.sleep(0.4)
    page.click("#owner button:has-text('Refresh')")
    page.wait_for_function("!app.ownerBusy && app.owner.ROU && app.owner.ROU.reqs.length === 1", timeout=8000)
    unfold(page, "Requests")
    got = page.text_content("#owner summary:has-text('Requests')")
    check("1 open" in got, f"{name}: requests not counted: {got}")
    page.click("#owner .req .tchip:has-text('Done')")
    rq = wait_doc(page, rq and [k for k in page.evaluate("[...window.__store.keys()]") if k.startswith(f"{base}/req-")][0] or "x", lambda v: v.get("status") == "done")
    check(rq and rq.get("status") == "done", f"{name}: request status not set: {rq}")
    unfold(page, "Suggestions")
    page.click("#owner button:has-text('Show them on the world map')")
    page.wait_for_function("app.ownerSug", timeout=8000)
    got = page.evaluate("app.ownerSug.ROU ? app.ownerSug.ROU.map(x => x.type + ':' + x.label) : null")
    check(got and len(got) == 2, f"{name}: the owner sees these suggestions of Rouental's: {got}")
    time.sleep(0.3)
    page.screenshot(path=str(OUT / f"{name}_home_owner.png"), full_page=True)
    # "Open" on a suggestion: the nation, at the suggestion, selected
    page.click("#owner .item:has-text('More islands for Concorde') button:has-text('Open')")
    page.wait_for_function("app.N && app.N.tag === 'ROU' && app.ui.sel.sug && app.N.sugList.length", timeout=8000)
    time.sleep(0.4)
    got = page.evaluate("[app.N.parts[app.ui.part].world, app.N.sugList.find(x => x.id === app.ui.sel.sug).label, app.ui.tab]")
    check(got == [True, "More islands for Concorde", "map"], f"{name}: opening a suggestion from the owner's list: {got}")
    page.screenshot(path=str(OUT / f"{name}_open_suggestion.png"))
    page.click("#back")
    time.sleep(0.4)
    page.click("#owner button:has-text('Save every nation as a file')")
    page.wait_for_function("window.__saved && window.__saved.filename.includes('all')", timeout=20000)
    allf = json.loads(page.evaluate("window.__saved.data"))
    (OUT / f"{name}_saved_all.json").write_text(json.dumps(allf, indent=1, ensure_ascii=False))
    check(set(allf["nations"]) == {"ROU", "SGN"} and "QZX" in allf["planned"] and allf["nations"]["SGN"]["facts"]["people"]["ruler"]["name"] == "Jeanne Testeuse",
          f"{name}: every-nation file wrong: {list(allf['nations'])}")
    unfold(page, "Passwords")
    # typed letter by letter, as a person types: the search keeps the cursor (the author, 2026-10-17: it "kicks me
    # out of the bar, making me reclick it after every letter")
    page.fill("#own-filter", "")
    page.click("#own-filter")
    page.keyboard.type("Seig", delay=60)
    time.sleep(0.2)
    got = page.evaluate("[document.activeElement && document.activeElement.id, document.getElementById('own-filter').value,"
                        " [...document.querySelectorAll('#own-filter ~ .pwlist .pwrow .nm')].map(e => e.textContent)]")
    check(got[0] == "own-filter" and got[1] == "Seig" and got[2] == ["Seigne"], f"{name}: typing in the password search: {got}")
    page.fill("#own-filter", "Seigne")
    time.sleep(0.2)
    page.click(".pwrow:has-text('Seigne') button:has-text('New password')")
    keys = wait_doc(page, "data/users/u_owner/keys", lambda v: v["SGN"] != pw_sgn)
    new_sgn = keys["SGN"]
    Kn = key("SGN", new_sgn)
    time.sleep(0.6)
    olds = page.evaluate(f"[...window.__store.keys()].filter(k => k.startsWith('n/SGN/{Ks}/'))")
    news = page.evaluate(f"[...window.__store.keys()].filter(k => k.startsWith('n/SGN/{Kn}/'))")
    check(new_sgn != pw_sgn and not olds and len(news) >= 4, f"{name}: password change: old {olds}, new {news}")

    # ---- the nation not on the map yet
    open_nation(page, "Testonia", "QZX")
    check(not page.evaluate("document.getElementById('lock').hidden"), f"{name}: Testonia has no lock before its password")
    page.click("#lock button:has-text('Make a password')")
    page.wait_for_function("app.N.K", timeout=5000)
    keys = doc(page, "data/users/u_owner/keys")
    Kq = key("QZX", keys["QZX"])
    hidden_tabs = page.evaluate("[...document.querySelectorAll('[data-tab]')].filter(b => b.hidden).map(b => b.dataset.tab)")
    check(hidden_tabs == ["state", "cities"], f"{name}: Testonia's tabs: hidden {hidden_tabs}")
    check(page.evaluate("app.ui.tool") == "suggest" and page.evaluate("app.N.parts[app.ui.part].world"), f"{name}: Testonia doesn't open on the world map with Suggest")
    page.click(".tchip:has-text('Area')")
    page.evaluate("locate(2360, 1530)")
    time.sleep(0.3)
    for g in ((2300, 1500), (2400, 1480), (2420, 1560), (2310, 1580)):
        x, y = canvas_point(page, json.dumps(g))
        page.mouse.click(x, y)
        time.sleep(0.3)
    page.keyboard.press("Enter")
    sg = wait_doc(page, f"n/QZX/{Kq}/suggest", lambda v: any(x and x.get("type") == "area" and len(x["pts"]) == 4 for x in v.values()))
    check(sg, f"{name}: Testonia's area not saved: {sg}")
    time.sleep(0.3)
    page.keyboard.type("Testonia goes here")
    page.click("[data-tab=politics]")
    page.fill("#pol-n-base-def", "the Grand Duchy of Testonia")
    pol = wait_doc(page, f"n/QZX/{Kq}/politics", lambda v: v["names"]["base"]["def"] == "the Grand Duchy of Testonia")
    check(pol, f"{name}: Testonia's title not saved")
    page.click("[data-tab=map]")
    time.sleep(0.4)
    page.screenshot(path=str(OUT / f"{name}_planned.png"))
    store = page.evaluate("Object.fromEntries(window.__store)")
    (OUT / f"{name}_store.json").write_text(json.dumps(store, indent=1, ensure_ascii=False))
    print(name, "writes:", page.evaluate("window.__writes.length"))
    ctx.close()
    return errs, {"store": store, "pw": {"ROU": pw_rou, "SGN": new_sgn, "SGN_old": pw_sgn}}


def friend(b, theme, size, name, store, pws):
    init = f"window.__me = {{id: 'u_friend', name: 'A Friend', isOwner: false}}; window.__seed = {json.dumps(store)};"
    ctx, page, errs = new_page(b, theme, size, init)
    page.goto(URL)
    try:
        page.wait_for_selector(".nrow", timeout=20000)
    except Exception:
        page.screenshot(path=str(OUT / f"{name}_FAIL.png"))
        print(page.evaluate("({home: document.getElementById('home').hidden, desk: document.getElementById('desk').hidden, N: app.N && app.N.tag, hash: location.hash, mode: app.mode})"))
        print(errs[:5])
        raise
    time.sleep(0.5)
    check(page.evaluate("document.getElementById('owner').hidden"), f"{name}: owner tools shown to a friend")
    check(page.evaluate("Object.keys(app.keys).length") == 0, f"{name}: a friend can read the owner's passwords")
    page.screenshot(path=str(OUT / f"{name}_home.png"))
    open_nation(page, "Rouental", "ROU")
    check(not page.evaluate("document.getElementById('lock').hidden"), f"{name}: no lock for a friend")
    check(page.evaluate("document.getElementById('save').textContent") == "Locked", f"{name}: chip doesn't say Locked")
    page.screenshot(path=str(OUT / f"{name}_locked.png"))
    n0 = page.evaluate("window.__writes.length")
    # a locked nation can be looked at, not changed
    x, y = canvas_point(page, "app.N.states[[...app.N.states.keys()].find(s => s >= 5 && app.N.stateToPart[s] === 0 && app.N.cities.every(c => Math.hypot(c.x - app.N.states[s].label[0], c.y - app.N.states[s].label[1]) > 14))].label")
    page.mouse.click(x, y)
    time.sleep(0.4)
    check(page.evaluate("document.querySelector('#pane-state fieldset.lockable').disabled"), f"{name}: locked fields not disabled")
    check(page.evaluate("stateName(5)") != "Testville", f"{name}: the saved facts show before the password")
    page.click("[data-tool=terrain]")
    page.mouse.click(x, y)
    time.sleep(0.3)
    page.click("[data-tool=select]")
    check(page.evaluate("window.__writes.length") == n0, f"{name}: a locked nation was written to")
    # a wrong password, then the right one typed loosely
    page.fill("#pw-in", "wrong-password-11")
    page.click("#lock button:has-text('Unlock')")
    time.sleep(0.5)
    check("isn't right" in page.inner_text("#lock"), f"{name}: no message for a wrong password")
    loose = "  " + pws["ROU"].replace("-", " ").title() + " "
    page.fill("#pw-in", loose)
    page.press("#pw-in", "Enter")
    page.wait_for_function("app.N.K", timeout=5000)
    time.sleep(0.6)
    # the quick-start guide, the first time a player unlocks a nation (tests/gazetteer/guide.py tests it)
    check(not page.evaluate("document.getElementById('guide').hidden"), f"{name}: no guide on the first unlock")
    page.click("#guide-card button:has-text('Skip')")
    time.sleep(0.2)
    check(page.evaluate("app.N.K") == key("ROU", pws["ROU"]), f"{name}: wrong key after unlocking")
    check(page.evaluate("stateName(5)") == "Testville", f"{name}: the owner's facts don't show after unlocking: {page.evaluate('stateName(5)')}")
    check(page.evaluate("document.getElementById('save').textContent") == "Saved", f"{name}: chip after unlocking")
    page.screenshot(path=str(OUT / f"{name}_desk.png"))
    K = key("ROU", pws["ROU"])
    x, y = canvas_point(page, "app.N.states[7].label")
    page.mouse.click(x, y)
    page.wait_for_selector("#st-name")
    page.fill("#st-name", "Friendville")
    w = wait_doc(page, f"n/ROU/{K}/states", lambda v: "Friendville" in json.dumps(v))
    check(w and "Friendville" in json.dumps(w) and "Testville" in json.dumps(w), f"{name}: friend's edit not saved")
    page.screenshot(path=str(OUT / f"{name}_state.png"))
    page.click("[data-tab=people]")
    time.sleep(0.3)
    page.screenshot(path=str(OUT / f"{name}_people.png"))
    page.click("[data-tab=nation]")
    time.sleep(0.3)
    page.screenshot(path=str(OUT / f"{name}_nation.png"))
    # the islands box on a phone
    if page.locator("#insets .inset").count() == 3:
        page.locator("#insets .inset").nth(1).click()
        time.sleep(0.4)
        page.screenshot(path=str(OUT / f"{name}_islands.png"))
    meta = doc(page, f"n/ROU/{K}/meta")
    check(meta and "u_friend" in meta.get("editors", {}), f"{name}: friend not among the editors: {meta}")
    # remembered: a reload opens it again
    page.reload()  # the link keeps #ROU: it opens straight into Rouental
    page.wait_for_function("app.N && app.N.tag === 'ROU' && app.N.K", timeout=8000)
    # another nation stays locked; the old password of a changed one doesn't open it
    page.click("#back")
    open_nation(page, "Seigne", "SGN")
    page.fill("#pw-in", pws["SGN_old"])
    page.click("#lock button:has-text('Unlock')")
    time.sleep(0.6)
    check(not page.evaluate("app.N.K"), f"{name}: an old password still opens Seigne")
    page.fill("#pw-in", pws["SGN"])
    page.click("#lock button:has-text('Unlock')")
    page.wait_for_function("app.N.K", timeout=5000)
    page.click("[data-tab=people]")
    time.sleep(0.4)
    check(page.input_value("#pp-ruler-name") == "Jeanne Testeuse", f"{name}: Seigne's ruler missing after the password change")
    page.screenshot(path=str(OUT / f"{name}_people_sgn.png"))
    # a link to the nation not on the map yet
    page.goto(URL + "#QZX")
    page.wait_for_function("app.N && app.N.tag === 'QZX'", timeout=10000)
    time.sleep(0.5)
    check(not page.evaluate("app.N.K"), f"{name}: Testonia open without its password")
    page.screenshot(path=str(OUT / f"{name}_planned.png"))
    ctx.close()
    return errs


def b_close(ctx):
    ctx.close()


def main(only=None):
    global URL
    if only != "friend":
        H.build_site()
    with H.Server(8765) as server:
        URL = server.url
        with sync_playwright() as p:
            b = p.chromium.launch(executable_path=H.CHROMIUM)
            runs = []
            if only == "friend":
                res = json.loads((OUT / "desk_light_res.json").read_text())
            else:
                e1, res = owner(b, "light", (1440, 900), "desk_light")
                runs.append(("desk_light", e1))
                (OUT / "desk_light_res.json").write_text(json.dumps(res))
            if res:
                runs.append(("phone_dark", friend(b, "dark", (390, 844), "phone_dark", res["store"], res["pw"])))
                runs.append(("desk_dark_friend", friend(b, "dark", (1440, 900), "desk_dark_friend", res["store"], res["pw"])))
            if only is None:
                e2, _ = owner(b, "light", (390, 844), "phone_light", full=True)
                runs.append(("phone_light", e2))
                e3, _ = owner(b, "dark", (1440, 900), "desk_dark", full=False)
                runs.append(("desk_dark", e3))
            b.close()
    for nm, errs in runs:
        for e in errs:
            if any(n in e for n in H.NOISE):
                continue
            problems.append(f"{nm}: console: {e}")
    print("PROBLEMS:", "none" if not problems else "")
    for p_ in problems:
        print(" -", p_)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else None))
