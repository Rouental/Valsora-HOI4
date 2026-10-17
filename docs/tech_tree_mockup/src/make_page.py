"""Writes docs/tech_tree_mockup/index.html: the page (page.html, page.js) with tree.json inlined.

    python3 docs/tech_tree_mockup/src/make_page.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")


def build(out=os.path.join(ROOT, "index.html")):
    page = open(os.path.join(HERE, "page.html"), encoding="utf-8").read()
    js = open(os.path.join(HERE, "page.js"), encoding="utf-8").read()
    tree = json.load(open(os.path.join(ROOT, "tree.json"), encoding="utf-8"))
    data = json.dumps(tree, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = page.replace("/*__DATA__*/", data).replace("/*__JS__*/", js)
    open(out, "w", encoding="utf-8").write(html)
    return out, len(html.encode("utf-8"))


if __name__ == "__main__":
    out, n = build()
    print(f"{out}: {n / 1024:.0f} KB")
