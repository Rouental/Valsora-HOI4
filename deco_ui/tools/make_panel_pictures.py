"""The side panels' own pictures, the drafts of 2026-10-18 the author approved, into the mod (v0.11, the author: "Keep
the art for navy, army, air, and intelligence tabs, at least for this pass. All the other stylization looks good, I'd
like you to add them to the mod").

The drafts are proposals_panel_mockups.py's, drawn the same way (its translate(), photo_plate() and v0.7's hand-drawn
proposals in art/proposals/panel_pictures/), each written as a DDS at the game's path and size; KEEP_GAME's stay the
game's: the army, navy and air overview (countryarmyview.gui: its entries, filters and header strip) and the
intelligence agency (countryintelligenceagencyview.gui: operatives, operations, crypto, the agency's plate and photo).

    python make_panel_pictures.py
"""
import os

from PIL import Image

import proposals_panel_mockups as PM
from ddsutil import write_dds
from paths import ART, MOD, VANILLA

GI = "gfx/interface/"
KEEP_GAME = ("armyoverview_", "overview_filter_entry", "overview_top_strip", "operatives/", "operations/", "crypto/")
# drawn by an art module instead (decisions_art.py: the decisions tab, restyled whole the same day; production_art.py
# (2026-10-19): the production lines and the trade rows, whose translation lost their boxes and left specks)
DRAWN = {"decisionview/decision_item_bg.dds", "decisionview/event_header_bg.dds", "production_item.dds",
         "production_line_selected.dds", "naval_production_line_selected.dds", "naval_production_item_slots_strip.dds",
         "tradeview/country_trade_entry_bg_wide.dds",
         "military_deployment_conveyor_bg.dds",   # deployment_art.py (2026-10-20: its translation left specks over the name)
         "factions/ui/faction_goal_slot.dds"}     # faction_art.py (2026-10-20: its translation drew a folder under the goal)


# and every picture an art module draws (2026-10-21: the translations' broken lines, the author: "weird sloppy lines and
# missing pieces of the design"; panelpics_*_art.py draw the rest by hand)
def _drawn_by_modules():
    import importlib
    from art_util import ART_MODULES
    return {rel[len(GI):] for m in ART_MODULES for _, rel, *_ in importlib.import_module(m).ADDS if rel.startswith(GI)}


DRAWN |= _drawn_by_modules()


def kept(rel):
    return rel.startswith(KEEP_GAME) or rel in DRAWN


def pictures():
    """(path under gfx/interface/, a function drawing it) for every draft that goes in"""
    out = []
    for rel in PM.PICTURES:
        if not kept(rel):
            out.append((rel, lambda rel=rel: PM.translate(Image.open(VANILLA + GI + rel))))
    for rel in PM.PHOTOS:
        if not kept(rel):
            out.append((rel, lambda rel=rel: PM.photo_plate(*Image.open(VANILLA + GI + rel).size)))
    for png, rel in PM.HAND:
        if not kept(rel):
            out.append((rel, lambda png=png: Image.open(ART + "proposals/panel_pictures/" + png).convert("RGBA")))
    return out


# the paths, for validate_preview.SAME_SIZE (each is held to the game's size)
PATHS = [GI + rel for rel, _ in pictures()]

if __name__ == "__main__":
    n = 0
    for rel, draw in pictures():
        src = VANILLA + GI + rel
        if not os.path.isfile(src):
            print("not in the game's files, left out:", rel)
            continue
        im = draw()
        assert im.size == Image.open(src).size, (rel, im.size, Image.open(src).size)
        dst = MOD + GI + rel
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        write_dds(im, dst)
        n += 1
    print(f"{n} panel pictures written (the game's kept: the army, navy and air overview, the intelligence agency)")
