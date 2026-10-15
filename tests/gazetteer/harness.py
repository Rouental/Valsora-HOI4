"""What the Gazetteer's browser tests share: the page served as claude.ai serves it, with the map data of the last
build, a stand-in for claude.ai's runtime (mock.js), the test pictures, and helpers to drive the page.

The site is built into work/gazetteer_test/ (git-ignored) from scripts/gazetteer.html and work/gazetteer/ (run
python3 scripts/facts_export.py after a build first) and served on a local port while the tests run."""
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
WORK = ROOT / "work" / "gazetteer_test"
SITE = WORK / "site"
SHOTS = WORK / "shots"
DATA = ROOT / "work" / "gazetteer"
CHROMIUM = os.environ.get("CHROMIUM_PATH", "/opt/pw-browsers/chromium")
# claude.ai wraps a published page in this skeleton (the Artifact tool's): the page itself has no <head>
SKELETON = ('<!doctype html><html><head><meta charset=utf8><meta name=viewport content="width=device-width,'
            'initial-scale=1,viewport-fit=cover"><style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,'
            '0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px/1.4 system-ui,sans-serif}'
            'img{max-width:100%}[hidden]{display:none!important}</style></head><body>')
MOCK = (HERE / "mock.js").read_text(encoding="utf-8")
# console lines that are this sandbox's, not the page's: Google Fonts through the proxy, the favicon
NOISE = ("ERR_CERT_AUTHORITY_INVALID", "404 (File not found)")


def build_site():
    """the page and the map data, and the test pictures, into work/gazetteer_test/"""
    if not (DATA / "index.json").exists():
        sys.exit("no map data: run python3 scripts/facts_export.py after a build first")
    shutil.rmtree(SITE, ignore_errors=True)
    SITE.mkdir(parents=True)
    SHOTS.mkdir(parents=True, exist_ok=True)
    page = (ROOT / "scripts/gazetteer.html").read_text(encoding="utf-8")
    (SITE / "index.html").write_text(SKELETON + page + "</body></html>", encoding="utf-8")
    for f in ("index.json", "world.png"):
        shutil.copy(DATA / f, SITE / f)
    shutil.copytree(DATA / "n", SITE / "n")
    pictures()


def pictures():
    """a portrait (300 x 420), a flag in HOI4's shape (164 x 104) and a big picture (2200 x 1600, to be made smaller)"""
    im = Image.new("RGB", (300, 420), (60, 70, 90))
    d = ImageDraw.Draw(im)
    d.ellipse((90, 60, 210, 200), fill=(220, 190, 160))
    d.rectangle((60, 220, 240, 420), fill=(40, 40, 60))
    im.save(WORK / "test_portrait.png")
    im = Image.new("RGB", (164, 104), (30, 90, 40))
    ImageDraw.Draw(im).rectangle((0, 35, 163, 69), fill=(240, 240, 240))
    im.save(WORK / "test_flag.png")
    import numpy as np
    rng = np.random.default_rng(1)
    Image.fromarray(rng.integers(0, 255, (1600, 2200, 3), dtype=np.uint8)).save(WORK / "test_big.png")


class Server:
    """python's own static server on the site, for the length of a with block"""
    def __init__(self, port):
        self.port = port
        self.url = f"http://127.0.0.1:{port}/"

    def __enter__(self):
        self.proc = subprocess.Popen([sys.executable, "-m", "http.server", str(self.port), "-d", str(SITE)],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.8)
        return self

    def __exit__(self, *exc):
        self.proc.terminate()


class Checks:
    def __init__(self):
        self.problems = []

    def __call__(self, cond, msg):
        if not cond:
            self.problems.append(msg)
        return cond

    def report(self):
        print("PROBLEMS:", "none" if not self.problems else "")
        for p in self.problems:
            print(" -", p)
        return 1 if self.problems else 0


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
        except (KeyError, TypeError, AttributeError, IndexError):
            pass
        time.sleep(0.15)
    return v


def new_page(browser, size, init="", mock=True, theme="light"):
    """a browser context and page; with mock, the stand-in runtime (init sets window.__me / __seed first)"""
    ctx = browser.new_context(viewport={"width": size[0], "height": size[1]}, color_scheme=theme,
                              device_scale_factor=1, has_touch=size[0] < 600, is_mobile=size[0] < 600)
    if mock:
        ctx.add_init_script(init + MOCK)
    page = ctx.new_page()
    errs = []
    page.on("console", lambda m: errs.append(m.text) if m.type == "error" and not any(n in m.text for n in NOISE) else None)
    page.on("pageerror", lambda e: errs.append(str(e)))
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
    """a select's value, as a click would set it (Playwright's select_option alone leaves the focus where it was,
    and the page doesn't redraw a pane while someone types in it)"""
    page.focus(selector)
    page.select_option(selector, value)
    time.sleep(0.35)


def options(page, selector):
    return page.evaluate("s => [...document.querySelectorAll(s + ' option')].map(o => o.value).filter(Boolean)", selector)


def make_password(page, name, tag):
    page.fill("#own-filter", name)
    time.sleep(0.2)
    page.click(f".pwrow:has-text('{name}') button:has-text('Make one')")
    keys = wait_doc(page, "data/users/u_owner/keys", lambda v: tag in v)
    return keys.get(tag) if keys else None


def dump(obj, name):
    (SHOTS / name).write_text(json.dumps(obj, indent=1, ensure_ascii=False), encoding="utf-8")
