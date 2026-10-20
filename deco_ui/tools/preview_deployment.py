"""build/preview_deployment.png (+ _vanilla): a division in training on the deployment panel (2026-10-20,
deployment_art.py): the conveyor (its template, name, amount, priorities, location and Add Unit buttons), two of its
lines (a division's name, equipment and training bars, the series number), the rule under them and a folded conveyor's
summary; and build/preview_faction_goals.png (+ _vanilla): the faction screen's goal slots (faction_art.py), open,
completed and failed, each with an icon and a long name. Windows as the game lays them out (preview_popups.py's canvas,
the Deco UI's .gui where it ships one); the progress bars' fill is drawn here at 60 %.

    python preview_deployment.py
"""
from PIL import Image

import preview_popups as PU
import validate_preview as V
from paths import BUILD

GUI = "countrydeploymentview.gui"


def deployment(vanilla):
    c = PU.Canvas(vanilla)
    x, y = 30, 30
    c.window(GUI, "military_deployment_conveyor_view", x, y,
             samples={"generic_name_edit": "Infantry Division", "amount": "2", "add_limit": "4",
                      "deploy_location_button": "§RNo location set§!", "add_button": "Add Unit"})
    for i, name in enumerate(("1st Infantry Division", "2nd Infantry Division")):
        c.window(GUI, "military_deployment_line_view", x - 13, y + 84 + 40 * i,
                 samples={"editbox": name, "series_number": f"{i + 1}"})
        for bx, by in ((235, 13), (329, 13)):
            c.sprite("GFX_deployment_entry_progressbar", x - 13 + bx, y + 84 + 40 * i + by)
    c.window(GUI, "military_deployment_conveyor_end_view", x - 14, y + 84 + 80 - 3)
    c.window(GUI, "military_deployment_conveyor_summary_view", x - 15, y + 200, samples={"lines_count": "3"})
    c.sprite("GFX_deployment_entry_progressbar", x - 15 + 237, y + 200 + 9)
    out = (c.cv.clip(0, 1) * 255).astype("uint8")[:270, :560]
    name = "preview_deployment_vanilla.png" if vanilla else "preview_deployment.png"
    Image.fromarray(out).resize((1120, 540), Image.NEAREST).save(BUILD + name)
    print("written", BUILD + name)


def goals(vanilla):
    c = PU.Canvas(vanilla)
    rel = "factions/countryfactionview.gui"
    for i, (frame, label) in enumerate(((1, "Institute a Joint Command Structure"), (2, "Expand Military Industry"),
                                        (3, "Win the War"))):
        c.window(rel, "goal_item_container", 30 + 180 * i, 30, frames={"background": frame},
                 hide={"empty_goal_item_container", "idea_alert_glow"}, samples={"label": label})
    c.window(rel, "goal_item_container", 30, 130, hide={"assigned_goal_item_container"})
    out = (c.cv.clip(0, 1) * 255).astype("uint8")[:240, :590]
    name = "preview_faction_goals_vanilla.png" if vanilla else "preview_faction_goals.png"
    Image.fromarray(out).resize((1180, 480), Image.NEAREST).save(BUILD + name)
    print("written", BUILD + name)


if __name__ == "__main__":
    for v in (False, True):
        deployment(v)
        goals(v)
