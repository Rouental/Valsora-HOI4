"""Previews of the designers and the commander picker on their new pictures (designer_art.py): each window drawn from
the game's .gui (its elements in place, the lists the game fills left empty) over the map, centred as the game shows
it, and beside it the game's own look.

    python preview_designers.py   -> build/preview_designers.png (+ _vanilla.png)

They show the game's art, so they stay in the git-ignored build/ folder.
"""
import numpy as np
from PIL import Image

import preview_panels as PP
import validate_preview as V
from paths import BUILD, VANILLA

# the designers sit at (0, 0) from the screen's centre, and the game centres them on it: their pictures' half sizes
WINDOWS = [("tank_designer_view.gui", "tank_designer_view", (-546, -276)),
           ("divisiondesignerview.gui", "countrydivisiondesignerview", (-600, -360)),
           ("unitleaderwindow.gui", "armyleaderwindow", (0, 0))]


def draw(vanilla):
    cvs = []
    for f, name, (dx, dy) in WINDOWS:
        path = VANILLA + "interface/" + f
        win = PP.find_window(V.load(path), name)
        cv = PP.backdrop(False)
        p = PP.Panel(vanilla_only=vanilla, outline_lists=True, vars_=PP.gui_vars(path))
        p.draw(cv, [("containerWindowType", win)], dx, dy, 1920, 1080)
        cvs.append(cv)
    rows = [Image.fromarray((np.clip(c, 0, 1) * 255).astype(np.uint8)).resize((960, 540)) for c in cvs]
    sheet = Image.new("RGB", (960, 540 * len(rows)))
    for i, r in enumerate(rows):
        sheet.paste(r, (0, 540 * i))
    sheet.save(BUILD + "preview_designers" + ("_vanilla" if vanilla else "") + ".png")


if __name__ == "__main__":
    draw(False)
    draw(True)
    print("wrote build/preview_designers.png (+ _vanilla)")
