"""Previews of the designers and the commander picker on their new pictures (designer_art.py): each window drawn from
the game's .gui (its elements in place, the lists the game fills left empty) over the map, centred as the game shows
it, and beside it the game's own look. The commander picker's list holds an army, a navy and a captured commander's
card, and the numbers the game writes on these pictures (the combat width, the skills, the stats) are sample values,
placed as the game places them (validate_preview.draw_text rounds a centred line's start up, as the game does,
measured in game on 2026-10-17).

    python preview_designers.py   -> build/preview_designers.png (+ _vanilla.png), and build/preview_designers_zoom.png
                                     (the combat width's ring and the cards' skill diamonds, 4x)

They show the game's art, so they stay in the git-ignored build/ folder.
"""
import os

import numpy as np
from PIL import Image

import preview_panels as PP
import validate_preview as V
from paths import BUILD, MOD, VANILLA

# the designers sit at (0, 0) from the screen's centre, and the game centres them on it: their pictures' half sizes
WINDOWS = [("tank_designer_view.gui", "tank_designer_view", (-546, -276)),
           ("divisiondesignerview.gui", "countrydivisiondesignerview", (-600, -360)),
           ("unitleaderwindow.gui", "armyleaderwindow", (0, 0))]
# the cards drawn into the commander picker's list, one under another as the game's grid lays them (98 px slots)
CARDS = ["armyleaderentry", "navyleaderentry", "capturedarmyleaderentry"]
SAMPLES = {"combat_width_text": "12", "skill": "4", "title": "General", "name": "Serelle Cahun", "divisions_count": "24",
           "leader_stat_attack": "4", "leader_stat_defense": "2", "leader_stat_planning": "3",
           "leader_stat_logistics": "3", "leader_stat_maneuvering": "3", "leader_stat_coordination": "2"}

# what the game shows only on demand: an army HQ's template (its header bar and panels lie over the ring and the
# columns), and the windows that open over the designer (the battalion picker, the equipment and symbol pickers, the
# 3D model picker, the niche icons)
HIDE = {"hq_overlay_images", "designerregimentswindow", "division_equipment_view", "div_templ_custom_icon_view",
        "div_template_select_model", "niche_icon_selector"}


def draw(vanilla):
    cvs, boxes = [], {}
    for f, name, (dx, dy) in WINDOWS:
        # the mod's copy where it ships one (the commander picker's foot buttons, make_buttons.py), else the game's
        path = (MOD if not vanilla and os.path.exists(MOD + "interface/" + f) else VANILLA) + "interface/" + f
        elems = V.load(path)
        win = PP.find_window(elems, name)
        cv = PP.backdrop(False)
        p = PP.Panel(vanilla_only=vanilla, outline_lists=True, vars_=PP.gui_vars(path), samples=SAMPLES, hide=HIDE)
        p.draw(cv, [("containerWindowType", win)], dx, dy, 1920, 1080)
        if name == "armyleaderwindow":
            gx, gy = next((b[1], b[2]) for b in p.boxes if b[0] == "leaders_grid")
            for i, card in enumerate(CARDS):
                # the captured card's own position (0, 8) is its place in its own list: drawn here at the slot
                p.draw(cv, [("containerWindowType", PP.find_window(elems, card))], gx, gy + 98 * i - (8 if "captured" in card else 0), 510, 98)
                boxes[card] = (int(gx), int(gy + 98 * i))
        else:
            boxes.update({b[0]: (int(b[1]), int(b[2])) for b in p.boxes if b[0] == "combat_width_view"})
        cvs.append(cv)
    rows = [Image.fromarray((np.clip(c, 0, 1) * 255).astype(np.uint8)).resize((960, 540)) for c in cvs]
    sheet = Image.new("RGB", (960, 540 * len(rows)))
    for i, r in enumerate(rows):
        sheet.paste(r, (0, 540 * i))
    sheet.save(BUILD + "preview_designers" + ("_vanilla" if vanilla else "") + ".png")
    if not vanilla:
        zoom(cvs, boxes)


def zoom(cvs, boxes, z=4):
    """the combat width's ring (the division designer) and the left ends of the three cards, at 4x"""
    x, y = boxes["combat_width_view"]
    crops = [cvs[1][y - 30:y + 71, x - 40:x + 81]]          # the ring in the middle (the text box: 40 x 20 at y + 10)
    crops += [cvs[2][cy:cy + 98, cx:cx + 130] for cx, cy in (boxes[c] for c in CARDS)]
    ims = [Image.fromarray((np.clip(c, 0, 1) * 255).astype(np.uint8)) for c in crops]
    ims = [im.resize((im.width * z, im.height * z), Image.NEAREST) for im in ims]
    out = Image.new("RGB", (sum(im.width for im in ims) + 12 * (len(ims) - 1), max(im.height for im in ims)), (40, 40, 40))
    left = 0
    for im in ims:
        out.paste(im, (left, 0))
        left += im.width + 12
    out.save(BUILD + "preview_designers_zoom.png")


if __name__ == "__main__":
    draw(False)
    draw(True)
    print("wrote build/preview_designers.png (+ _vanilla, _zoom)")
