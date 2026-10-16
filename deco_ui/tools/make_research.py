"""Build interface/countrytechtreeview.gui (the research trees) and interface/doctrines/doctrines_view.gui (the doctrine
screen) in the focus tree's arrangement (v0.9, the user, 2026-10-16: "do 1 (though be prepared to possibly revert
it)", the screens still in the game's look).

    python make_research.py

Both are full-screen views drawn over the top bar: the game opens them at y 78 and 82, over the medallion's lower half
and the decisions seal (medallion_check.py). Each now opens flush under the band at the focus tree's x (-3), so the
focus tree's header picture, notched round the medallion and seal, fits it as it is: its own background is clear and
click-through, invisible containers beside the notch catch clicks, a gilt title ("Research", "Doctrines") sits right of
the notch, the game's folder tabs move into the header (hanging over the tree's top edge by as much as the game's do),
the close button is the politics screen's diamond, and the trees start under the header. The tabs, the trees' own
pictures and every technology and doctrine are the game's. Every element and name of the game's files is kept.

The research trees' file is the Valsora mod's (its year labels are 2036's): the Valsora build runs this again on its own
copy (scripts/deco_ui.py, REPLACES), as it does make_politics.py; here it starts from that copy (paths.VALSORA_BASE),
else from the built Valsora mod while it still has its own, else from the game's.
"""
import os
import re
import sys

import guipatch as GP
import layout_focus as LF
import layout_panels as LPN
from paths import MOD, VANILLA, VALSORA, VALSORA_BASE

CLEAR, CLOSE = "GFX_valsora_deco_clear", "GFX_valsora_deco_pol_close"
HEADER = "GFX_valsora_deco_nf_header"          # the focus tree's (make_focus.py): the same x, the same notch
TITLE_FONT = "valsora_deco_title_30"
HX = LF.HX                                       # 187: right of the notch
TITLE = dict(x=HX, y=16, w=600, h=40)
TAB_OVERLAP = 21                                 # the game's tabs hang this far over the tree's top edge
LANGS = ["english", "french", "german", "spanish", "braz_por", "polish", "russian", "japanese", "simp_chinese"]
MARK = "Valsora Deco UI"


def container(name, x, y, w, h, sprite, transparent):
    tr = "\n\t\t\talwaystransparent = yes" if transparent else ""
    return (f'\n\t\tcontainerWindowType = {{\n\t\t\tname = "{name}"\n\t\t\tposition = {{ x = {x} y = {y} }}\n'
            f'\t\t\tsize = {{ width = {w} height = {h} }}\n\t\t\tclipping = no\n'
            f'\t\t\tbackground = {{\n\t\t\t\tname = "{name}_bg"\n\t\t\t\tquadTextureSprite = "{sprite}"{tr}\n\t\t\t}}\n\t\t}}')


def notched(t, win, prefix, title_key, has_background=True):
    """the window flush under the band at the focus tree's x, its background clear and click-through, the
    click-catchers beside the notch, the header picture and the title"""
    t = GP.set_attrs(t, win, position=(LF.WIN_X, LF.TOP))
    if has_background:
        t = GP.set_background(t, win, CLEAR)
        s_, e_ = GP.find_block(t, win)
        blk = t[s_:e_]
        blk, n = re.subn(r'(background\s*=\s*\{[^{}]*?quadTextureSprite\s*=\s*"' + CLEAR + '")',
                         r'\1\n\t\t\talwaystransparent = yes', blk, count=1)
        assert n == 1, f"{win}'s background was not made click-through"
        t = t[:s_] + blk + t[e_:]
    layers = ""
    for i, (x0, y0, x1, y1) in enumerate(LPN.blockers(100000, LF.WIN_X)):
        w = "100%%" if x1 >= 100000 else x1 - x0
        layers += container(f"{prefix}_block_{i}", x0, y0, w, y1 - y0, CLEAR, False)
    layers += container(f"{prefix}_block_foot", 0, LPN.NB, "100%%", LF.TREE_Y - LPN.NB, CLEAR, False)
    layers += container(f"{prefix}_header", 0, 0, "100%%", LF.HEAD_H, HEADER, True)
    layers += f"""
		instantTextboxType = {{
			name = "{prefix}_title"
			position = {{ x = {TITLE['x']} y = {TITLE['y']} }}
			font = "{TITLE_FONT}"
			text = "{title_key}"
			maxWidth = {TITLE['w']}
			maxHeight = {TITLE['h']}
			format = left
			vertical_alignment = center
			alwaystransparent = yes
		}}"""
    return GP.insert_child(t, win, f"\n\t\t# ===== Valsora Deco: the click-catchers beside the notch, the header and its title =====" + layers,
                           first=True)


def direct_children(t, win, kind="containerWindowType"):
    """the names of a window's direct children of one kind"""
    s_, e_ = GP.find_block(t, win)
    body = re.sub(r"#[^\n]*", "", t[s_:e_])
    out, d = [], 0
    for m in re.finditer(r"(?i)(" + kind + r")\s*=\s*\{|[{}]", body):
        if m.group(1):
            if d == 1:
                nm = re.search(r'name\s*=\s*"?([\w.-]+)', body[m.end():m.end() + 300])
                out.append(nm.group(1))
            d += 1
        elif m.group(0) == "{":
            d += 1
        else:
            d -= 1
    return out


def research():
    rel = "interface/countrytechtreeview.gui"
    base = next(p for p in (os.path.join(b, rel) for b in (VALSORA_BASE, VALSORA, VANILLA)) if os.path.isfile(p)
                and MARK not in open(p, encoding="utf-8-sig", errors="ignore").read(400))
    t = open(base, encoding="utf-8-sig").read().replace("\r\n", "\n")
    R = "countrytechtreeview"
    t = notched(t, R, "valsora_deco_tt", "VAL_DECO_TT_TITLE")
    folders = [n for n in direct_children(t, R) if n.endswith("folder")]
    assert len(folders) >= 10, folders
    for f in folders:
        t = GP.set_attrs(t, f"{R}>{f}", position=(0, LF.TREE_Y))
    tabs = GP.get_pos(t, f"{R}>folder_tabs")
    # the first tab sits at x 22 in its row (the game's): the row moves so it starts right of the notch
    t = GP.set_attrs(t, f"{R}>folder_tabs", position=(HX - 22, LF.TREE_Y - (61 - TAB_OVERLAP)))
    t = GP.set_attrs(t, f"{R}>close_button", sprite=CLOSE, position=LF.CLOSE)
    t = (f"# {MARK} - research trees (tools/make_research.py, from {'the Valsora mod' if VALSORA in base or VALSORA_BASE in base else 'the game'}'s "
         f"countrytechtreeview.gui):\n# the focus tree's notched header; every element and name kept\n\n" + t)
    GP.write_gui(MOD + rel, t)
    print(f"{rel}: from {base}; {len(folders)} folders under the header, the tabs at {tabs} -> right of the notch")


def doctrines():
    rel = "interface/doctrines/doctrines_view.gui"
    t = open(os.path.join(VANILLA, rel), encoding="utf-8-sig").read().replace("\r\n", "\n")
    R = "country_doctrine_view"
    t = notched(t, R, "valsora_deco_doc", "VAL_DECO_DOC_TITLE", has_background=False)
    t = GP.set_attrs(t, f"{R}>doctrine_folder_view", position=(0, LF.TREE_Y))
    # the folder tabs: 256 px slots, each tab drawn at x 16 in its slot (the game's doctrine_folder_tab)
    t = GP.set_attrs(t, f"{R}>folders_grid", position=(HX - 16, LF.TREE_Y - (61 - TAB_OVERLAP)))
    t = GP.set_attrs(t, f"{R}>close_button", sprite=CLOSE, position=LF.CLOSE)
    t = (f"# {MARK} - doctrine screen (tools/make_research.py, from the game's doctrines_view.gui): the focus tree's\n"
         "# notched header; every element and name kept\n\n" + t)
    os.makedirs(os.path.dirname(MOD + rel), exist_ok=True)
    GP.write_gui(MOD + rel, t)
    print(f"{rel}: under the header")


def loc():
    for lang in LANGS:
        d = MOD + f"localisation/{lang}/"
        os.makedirs(d, exist_ok=True)
        open(d + f"valsora_deco_research_l_{lang}.yml", "w", encoding="utf-8-sig", newline="\n").write(
            f'l_{lang}:\n VAL_DECO_TT_TITLE:0 "Research"\n VAL_DECO_DOC_TITLE:0 "Doctrines"\n')


if __name__ == "__main__":
    research()
    if "--research-only" not in sys.argv:       # the Valsora build makes only the research trees again
        doctrines()
        loc()
