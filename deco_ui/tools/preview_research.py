"""Previews of the research trees and the doctrine screen (make_research.py), drawn as the game would: the top bar
behind them (so the notch shows the medallion and seal), the window from the generated .gui with the game's sprites
where the mod keeps them, the infantry tree's own picture and year labels, and the folder tabs (the doctrine screen's
the game fills in: the four drawn here as its template lays them out). Beside each, the game's look.

    python preview_research.py   -> build/preview_research.png, preview_doctrines.png (+ _vanilla.png)

They show the game's art, so they stay in the git-ignored build/ folder.
"""
import numpy as np
from PIL import Image

import layout_focus as LF
import make_research as MR
import preview_panels as PP
import validate_preview as V
from paths import BUILD, MOD as M, VANILLA, VALSORA

TT_FOLDERS = ["infantry_folder", "support_folder", "armour_folder", "nsb_armour_folder", "artillery_folder", "naval_folder",
              "mtgnavalfolder", "mtgnavalsupportfolder", "air_techs_folder", "bba_air_techs_folder", "industry_folder",
              "electronics_folder"]
TT_HIDE = set(TT_FOLDERS[1:]) | {"nsb_armour_folder_tab", "mtgnavalfolder_tab", "mtgnavalsupportfolder_tab", "bba_air_techs_folder_tab",
                                 "highlight_infantry_folder", "highlight_support_folder", "highlight_armour_folder",
                                 "highlight_artillery_folder", "highlight_naval_folder", "highlight_air_folder",
                                 "highlight_industry_folder", "highlight_electronics_folder", "highlight_doctrine_folder"}
DOC_TABS = [("GFX_landdoctrine_tab_large", "Land"), ("GFX_navaldoctrine_tab_large", "Naval"),
            ("GFX_airdoctrine_tab_large", "Air"), ("GFX_specialforcesdoctrine_tab_large", "Special Forces")]


def save(cv, name):
    Image.fromarray((np.clip(cv, 0, 1) * 255).astype(np.uint8)).save(BUILD + name)


def research(vanilla):
    path = (VANILLA if vanilla else M) + "interface/countrytechtreeview.gui"
    if vanilla:
        path = VALSORA + "interface/countrytechtreeview.gui" if "Deco UI" not in open(VALSORA + "interface/countrytechtreeview.gui",
                                                                                       encoding="utf-8-sig").read(300) else path
    win = PP.find_window(V.load(path), "countrytechtreeview")
    cv = PP.backdrop(not vanilla)
    p = PP.Panel(hide=TT_HIDE, samples={"valsora_deco_tt_title": "Research"}, vanilla_only=vanilla, outline_lists=False,
                 vars_=PP.gui_vars(path), frames={"infantry_folder_tab": 1})
    p.draw(cv, [("containerWindowType", win)], 0, 0, 1920, 1080)
    save(cv, "preview_research" + ("_vanilla" if vanilla else "") + ".png")


def doctrines(vanilla):
    path = (VANILLA if vanilla else M) + "interface/doctrines/doctrines_view.gui"
    elems = V.load(path)
    win = PP.find_window(elems, "country_doctrine_view")
    cv = PP.backdrop(not vanilla)
    p = PP.Panel(hide={"no_grand_doctrine_info", "grand_doctrine", "tracks_container"},
                 samples={"valsora_deco_doc_title": "Doctrines"}, vanilla_only=vanilla, outline_lists=False,
                 vars_=PP.gui_vars(path))
    p.draw(cv, [("containerWindowType", win)], 0, 0, 1920, 1080)
    # the folder tabs the game puts in folders_grid: its template's button at (16, 0), the name at (66, 18)
    gx, gy = (LF.WIN_X + MR.HX - 16, LF.TOP + LF.TREE_Y - (61 - MR.TAB_OVERLAP)) if not vanilla else (128, 82 + 1)
    for i, (spr, name) in enumerate(DOC_TABS):
        d, img = PP.sprite(spr, vanilla)
        if img is not None:
            V.paste(cv, PP.frame_of(img, d, 1 if i == 0 else 0), gx + i * 256 + 16, gy)
        p.text(cv, name, "hoi_20bs", gx + i * 256 + 66, gy + 18, 180, 24, "left", "folder_name")
    save(cv, "preview_doctrines" + ("_vanilla" if vanilla else "") + ".png")


if __name__ == "__main__":
    for v in (False, True):
        research(v)
        doctrines(v)
    print("wrote build/preview_research.png, preview_doctrines.png (+ _vanilla)")
