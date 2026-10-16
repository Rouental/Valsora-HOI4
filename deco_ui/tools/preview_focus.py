"""A preview of the focus tree (make_focus.py), drawn as the game would: the top bar behind the window (so the notch
shows the medallion and seal), the window from the generated .gui with the game's own sprites where the mod keeps
them, and Valsora's Rouental tree on it, with the game's focus icons, in the mockup's states: one path completed,
the next focus in progress, the paths it excludes unavailable, another focus available.

    python preview_focus.py          -> build/preview_focus.png

Where the game places links and exclusive marks is not written in its files; the preview draws vertical links on
the focus's centre line and exclusive marks at the medallions' height, between them, as the mockup does.
"""
import re

import numpy as np
from PIL import Image

import layout_focus as LF
import preview_panels as PP
import validate_preview as V
from paths import BUILD, MOD as M, VALSORA

SPACING = (96, 130)                    # the game's focus_spacing
STATES = {"ROU_parasites_polite": "unavailable", "ROU_kick_out_brother": "unavailable",
          "ROU_steady_as_she_goes": "unavailable", "ROU_parasites_rude": "completed", "ROU_accept_reality": "unavailable",
          "ROU_execute_the_prince": "current", "ROU_plans_for_cardonia": "can_start"}
SPRITE = {"unavailable": "GFX_focus_unavailable", "can_start": "GFX_focus_can_start", "completed": "GFX_focus_completed",
          "current": "GFX_focus_current"}


def focuses():
    src = re.sub(r"#[^\n]*", "", open(VALSORA + "common/national_focus/rouental.txt", encoding="utf-8-sig").read())
    out = []
    for m in re.finditer(r"\bfocus\s*=\s*\{\s*\n\s*id\s*=\s*(\w+)(.*?)\n\t\}", src, re.S):
        body = m.group(2)
        pre = re.findall(r"prerequisite\s*=\s*\{\s*focus\s*=\s*(\w+)", body)
        exc = re.search(r"mutually_exclusive\s*=\s*\{([^}]*)\}", body)
        out.append(dict(id=m.group(1), icon=re.search(r"icon\s*=\s*(\w+)", body).group(1),
                        x=int(re.search(r"\bx\s*=\s*(-?\d+)", body).group(1)), y=int(re.search(r"\by\s*=\s*(-?\d+)", body).group(1)),
                        pre=pre, exc=re.findall(r"focus\s*=\s*(\w+)", exc.group(1)) if exc else []))
    return out


def valsora_loc():
    loc = {}
    for f in __import__("glob").glob(VALSORA + "localisation/english/*.yml"):
        loc.update(re.findall(r'^\s*([\w.\-]+):\d*\s*"(.*)"\s*$', open(f, encoding="utf-8-sig", errors="ignore").read(), re.M))
    return loc


def paste_sprite(cv, name, x, y, frame=0, centre=False):
    d, img = PP.sprite(name)
    if img is None:
        return None
    im = PP.frame_of(img, d, frame)
    if centre:
        x, y = x - im.width / 2, y - im.height / 2
    V.paste(cv, im, x, y)
    return im


def tile(cv, name, frame, x, y):
    paste_sprite(cv, name, x, y, frame)


def main():
    cv = PP.backdrop(True)
    elems = V.load(M + "interface/nationalfocusview.gui")
    win = PP.find_window(elems, "nationalfocusview")
    hide = {"continuous_focus_window", "search_tooltip", "shortcut_grid_container", "toggle_shortcuts", "techtree_stripes",
            "tutorial_glow_1", "tutorial_glow_2", "tutorial_glow_3", "tutorial_glow_4", "open_focus", "clear_search",
            "filter_grid_main_container", "grid"}
    p = PP.Panel(hide=hide, samples={"national_focus_title": "Rouental Focus Tree", "type_to_search_text": "Search focuses",
                                     "valsora_deco_nf_kicker": "National Focus"}, outline_lists=False)
    p.draw(cv, [("containerWindowType", win)], 0, 0, 1920, 1080)
    wx, wy = LF.WIN_X, LF.TOP
    # the filter chips (the game fills the grid: one chip per filter its tree uses; the generic tree's seven here)
    fx0 = 1920 + LF.FILTERS[0] + wx
    for i in range(7):
        tile(cv, "GFX_valsora_deco_nf_filter", 1 if i == 0 else 0, fx0 + i * 37, wy + LF.FILTERS[1])

    # the tree: Rouental's focuses where the game puts them (grid at 50, 50 inside the tree's 13 px margin)
    ox, oy = wx + 13 + 50 + 40, wy + LF.TREE_Y + 13 + 50 + 30
    loc = valsora_loc()
    fs = focuses()
    at = {f["id"]: (ox + f["x"] * SPACING[0], oy + f["y"] * SPACING[1]) for f in fs}
    cx = lambda fid: at[fid][0] + LF.ICON_C[0]
    cy = lambda fid: at[fid][1] + LF.ICON_C[1]
    # links: from under the parent's plate down to the child, on the focus's centre line (bright: completed parent)
    for f in fs:
        for pre in f["pre"]:
            x = round(cx(f["id"]) - 8)
            frame = 0 if STATES.get(pre) == "completed" else 2
            for y in range(at[pre][1] + 64, at[f["id"]][1], 16):
                tile(cv, "GFX_focus_link_up_down", frame, x, y)
    # exclusive marks between neighbours in a row: the line, its end diamonds and the cross in the middle
    done = set()
    row = sorted((f for f in fs if f["exc"]), key=lambda f: f["x"])
    for a, b in zip(row, row[1:]):
        if b["id"] in a["exc"] and (a["id"], b["id"]) not in done:
            done.add((a["id"], b["id"]))
            x0, x1 = cx(a["id"]) + LF.MEDALLION / 2 + 4, cx(b["id"]) - LF.MEDALLION / 2 - 4
            y = cy(a["id"]) - 8
            for x in range(int(x0), int(x1) - 15, 16):
                tile(cv, "GFX_focus_exclusive_line1", 1, x, y)
            tile(cv, "GFX_focus_link_exclusive", 1, x0 - 6, y - 8)
            tile(cv, "GFX_focus_link_exclusive", 2, x1 - 26, y - 8)
            tile(cv, "GFX_focus_link_exclusive", 0, (x0 + x1) / 2 - 16, y - 8)
    # the focuses: halo (in progress), medallion and plate, the game's icon, the name
    for f in fs:
        st = STATES.get(f["id"], "can_start")
        x, y = at[f["id"]]
        if st == "current":
            paste_sprite(cv, "GFX_ongoing_focus_goal", x + round(LF.ICON_C[0] - LF.HALO / 2 - .5),
                         y + round(LF.ICON_C[1] - LF.HALO / 2), 1)
        paste_sprite(cv, SPRITE[st], x + LF.BG["x"], y + LF.BG["y"])
        paste_sprite(cv, f["icon"], x + LF.ICON_C[0], y + LF.ICON_C[1], centre=True)
        N = LF.NAME
        V.draw_text(cv, "valsora_deco_body_13", loc.get(f["id"], f["id"]), x + N["x"], y + N["y"], N["w"], "center",
                    max_h=N["h"], valign=True)
    out = Image.fromarray((np.clip(cv, 0, 1) * 255).astype(np.uint8))
    out.save(BUILD + "preview_focus.png")
    print("focus tree preview written")


if __name__ == "__main__":
    main()
