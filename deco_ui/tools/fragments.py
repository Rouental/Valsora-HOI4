"""Broken gilt in the Deco UI's pictures: the check for what the author saw again and again (2026-10-21: "with a lot of
the things you've generated recently, there's these weird sloppy lines and missing pieces of the design").

The pictures that showed it were translations of the game's art (proposals_panel_mockups.translate(), retired that
day): the game's thin bright lines traced into gilt came out as short pieces, single specks and pills where a rim
should run whole. A picture drawn by hand has its rims, rules and wells whole, so its gilt is long lines and closed
shapes. A fragment here is a patch of gilt (8-connected, its colour loosely gold, so a rim dimming along its chamfer
stays one piece) that is either a speck (4 px or fewer) or a thin short stroke (at most 2 px thick, 3 to 40 long).

Calibrated on 2026-10-21 against the 25 pictures redrawn that day: the old translations had up to 102 fragments (the
supreme commander's card), 0 to 3 a picture for the few whose breaks were dark lines or missing boxes rather than
gilt; every redrawn picture has 0. Checked: the plates and backgrounds (120 x 40 px and larger) of every art module, of
make_panel_pictures and of gen_textures. A picture may hold short strokes on purpose (a dashed arc, a dashed empty
slot, speed lines, a diamond rule's tail): KNOWN lists those, each with its count, so a changed picture is looked at
again. validate_preview.py runs it; a problem is a picture not in KNOWN with any fragment, or one in KNOWN whose count
changed.

    python fragments.py [path ...]     # the fragments of these pictures (or of all checked ones), with their places
"""
import importlib
import json
import os
import sys

import numpy as np
from scipy import ndimage as ndi

from ddsutil import read_dds
from paths import MANIFEST, MOD

MIN_W, MIN_H = 120, 40
# pictures whose short strokes are drawn on purpose (looked at 2026-10-21), with the count each has
KNOWN = {
    "gfx/interface/international_market/market_ui.dds": 72,           # the trade arc, dashed, and its arrow
    "gfx/loadingscreens/valsora_menu.dds": 57,                         # the menu's sunburst and rules
    "gfx/interface/diplo_action_mil_acess_bg.dds": 8,                  # the crossing arrow, dashed
    "gfx/interface/land_battle_bg.dds": 7,                             # speed lines either side of the title
    "gfx/interface/navalcombat/naval_battle_bg2.dds": 6,               # speed lines either side of the title
    "gfx/interface/valsora_deco/topbar_medallion.dds": 6,              # the medallion's side rules
    "gfx/interface/diplo_action_license_production_bg.dds": 4,         # the emblem's strokes, the rule's diamonds
    "gfx/interface/select_date_bg.dds": 4,                             # the diamond rules' tails
    "gfx/interface/alerts/global_alert_icons.dds": 3,                  # icons (a strip)
    "gfx/interface/country_selection_bg.dds": 2,                       # the diamond rules' tails
    "gfx/interface/diplo_action_stage_coup_bg.dds": 2,                 # the emblem's strokes
    "gfx/interface/header2.dds": 2,                                    # the chamfer's ticks
    "gfx/interface/leader_selection_bg.dds": 2,                        # the corner brackets' ticks
    "gfx/interface/operatives/agency_upgrades_popup_bg.dds": 2,        # the rule's diamonds
    "gfx/interface/valsora_deco/focus/current_bg.dds": 2,              # the diamond's points
    "gfx/interface/valsora_deco/topbar_right.dds": 2,                  # the tray's dividers
    "gfx/interface/buildings/building_icon_strip.dds": 1,              # icons (a strip)
    "gfx/interface/unitcontrol/battleplantools_cohesion_bg.dds": 1,    # the slider's middle mark
    "gfx/interface/unitcontrol/battleplantools_planning_bg.dds": 1,    # the slider's middle mark
    "gfx/interface/unitcontrol/hq_proximity_settings_bg.dds": 1,       # the slider's middle mark
}


def gilt(a):
    r, g, b, al = (a[..., i].astype(int) for i in range(4))
    return (al >= 160) & (r >= 140) & (g >= 100) & (r - b >= 50) & (g - b >= 20)


def goldish(a):
    """gilt, dim gilt and its anti-aliased edge: what joins a rim's pieces into one"""
    r, g, b, al = (a[..., i].astype(int) for i in range(4))
    return (al >= 60) & (r >= 55) & (r - b >= 20) & (g - b >= 8)


def fragments(img):
    """[(x, y, w, h, px)] of the picture's broken gilt"""
    a = np.array(img.convert("RGBA"))
    m = gilt(a)
    lab, n = ndi.label(goldish(a), np.ones((3, 3)))
    bright = np.zeros(n + 1, bool)
    bright[np.unique(lab[m])] = True
    out = []
    for i, sl in enumerate(ndi.find_objects(lab), 1):
        if not bright[i]:
            continue
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        px = int((lab[sl] == i).sum())
        if px <= 4 or (min(w, h) <= 2 and 3 <= max(w, h) <= 40):
            out.append((sl[1].start, sl[0].start, w, h, px))
    return out


def checked():
    """the pictures checked: every art module's, make_panel_pictures' and gen_textures' (its manifest) .dds"""
    from art_util import ART_MODULES
    import make_panel_pictures as MPP
    rels = {r for m in ART_MODULES for _k, r, *_ in importlib.import_module(m).ADDS} | set(MPP.PATHS)
    if os.path.exists(MANIFEST):
        rels |= {e["path"] for e in json.load(open(MANIFEST))}
    return sorted(r for r in rels if r.endswith(".dds") and os.path.exists(MOD + r))


def problems():
    out = []
    for rel in checked():
        img = read_dds(MOD + rel)
        if img.width < MIN_W or img.height < MIN_H:
            continue
        f = fragments(img)
        if rel in KNOWN:
            if len(f) != KNOWN[rel]:
                out.append(f"{rel}: {len(f)} short gilt strokes, {KNOWN[rel]} known (fragments.KNOWN): look at it again")
        elif f:
            where = ", ".join(f"({x}, {y}) {w}x{h}" for x, y, w, h, _ in f[:4])
            out.append(f"{rel}: {len(f)} pieces of broken gilt, e.g. {where} (fragments.py)")
    return out


if __name__ == "__main__":
    for rel in sys.argv[1:] or checked():
        f = fragments(read_dds(MOD + rel if not os.path.exists(rel) else rel))
        if f:
            print(rel, len(f), f[:8])
    if not sys.argv[1:]:
        print("PROBLEMS:", problems() or "none")
