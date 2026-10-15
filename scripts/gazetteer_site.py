"""The Gazetteer as a web site: the page (scripts/gazetteer.html) with the author's Firebase
project keeping its atlas, served by GitHub Pages from the gh-pages branch, at
https://rouental.github.io/Valsora-HOI4/ (docs/GAZETTEER.md).

    python3 scripts/gazetteer_site.py [--out DIR]
        work/gazetteer_site/: index.html, the Firebase SDK (source/gazetteer_site/) and the
        map data facts_export.py wrote in work/gazetteer/. Run facts_export.py first.
    python3 scripts/gazetteer_site.py --out DIR --emulator 127.0.0.1:8080:9099 --project demo-x
        the same against Firebase's local emulators, for tests.

Publishing is a commit of DIR's files on the gh-pages branch (CLAUDE.md, The Gazetteer).
"""
import argparse
import json
import re
import shutil
from pathlib import Path

PAGE = Path("scripts/gazetteer.html")
SITE = Path("source/gazetteer_site")
DATA = Path("work/gazetteer")
SDK = "firebase-sdk-12.19.0.js"
PLACEHOLDER = "const FIREBASE = null;  // the web site's build fills this in"
DESCRIPTION = ("Fill in your nation for Valsora, a Hearts of Iron IV world: states, terrain, rivers, "
               "cities, railways, flags and leaders.")
# the page's own reset, as claude.ai wraps an artifact (the page was made against it)
RESET = (":root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);"
         "padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px/1.4 system-ui,sans-serif}"
         "img{max-width:100%}[hidden]{display:none!important}")
ICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E"
        "%3Cpath d='M8 1l6 7-6 7-6-7z' fill='%238e6d27'/%3E%3C/svg%3E")


def page(firebase):
    """index.html: the page in a document of its own, its title and font links in the head"""
    src = PAGE.read_text(encoding="utf-8")
    if src.count(PLACEHOLDER) != 1:
        raise SystemExit(f"{PAGE}: the FIREBASE line the site fills in is missing")
    src = src.replace(PLACEHOLDER, "const FIREBASE = " + json.dumps(firebase, separators=(",", ":")) + ";")
    head = []
    while True:  # the page starts with its title, meta and font links
        m = re.match(r"\s*(<title>.*?</title>|<meta [^>]*>|<link [^>]*>)", src, re.S)
        if not m:
            break
        if not m.group(1).startswith("<meta name=\"claude:"):
            head.append(m.group(1))
        src = src[m.end():]
    return ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1,viewport-fit=cover\">"
            "<meta name=\"robots\" content=\"noindex\">"
            f"<meta name=\"description\" content=\"{DESCRIPTION}\">"
            "<meta property=\"og:title\" content=\"Valsora Gazetteer\">"
            f"<meta property=\"og:description\" content=\"{DESCRIPTION}\">"
            f"<link rel=\"icon\" href=\"{ICON}\">"
            + "".join(head) + f"<style>{RESET}</style></head><body>" + src.strip() + "\n</body></html>\n")


def build(out, emulator=None, project=None):
    out = Path(out)
    if not (DATA / "index.json").exists():
        raise SystemExit(f"{DATA} is empty: run scripts/facts_export.py first")
    config = json.loads((SITE / "firebase-config.json").read_text(encoding="utf-8"))
    firebase = {"config": config, "sdk": "./" + SDK}
    if emulator:
        host, fs, auth = emulator.split(":")
        firebase["config"] = {**config, "projectId": project, "authDomain": f"{host}:{auth}"}
        firebase["emulator"] = {"host": host, "firestore": int(fs), "auth": int(auth)}
    if out.exists():
        shutil.rmtree(out)
    (out / "n").mkdir(parents=True)
    (out / "index.html").write_text(page(firebase), encoding="utf-8")
    shutil.copy(SITE / SDK, out / SDK)
    shutil.copy(DATA / "index.json", out / "index.json")
    shutil.copy(DATA / "world.png", out / "world.png")
    for f in sorted((DATA / "n").glob("*.json")):
        shutil.copy(f, out / "n" / f.name)
    (out / ".nojekyll").write_text("")  # served as it is
    size = sum(f.stat().st_size for f in out.rglob("*") if f.is_file())
    print(f"wrote {out}: index.html, {SDK}, {len(list((out / 'n').glob('*.json')))} nations, "
          f"{size / 1e6:.1f} MB" + (f" (emulators at {emulator})" if emulator else ""))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="work/gazetteer_site")
    ap.add_argument("--emulator", help="HOST:FIRESTORE_PORT:AUTH_PORT of Firebase's local emulators (tests)")
    ap.add_argument("--project", default="demo-valsora", help="the emulators' project id")
    a = ap.parse_args()
    build(a.out, a.emulator, a.project)
