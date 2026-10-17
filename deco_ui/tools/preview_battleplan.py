"""build/preview_battleplan.png (+ _vanilla): the battle plan toolbar and its planning speed pop-up as the game lays them
out (interface/battleplantools.gui), with the Deco UI's pictures and with the game's (2026-10-17, v0.10)."""
from PIL import Image

from paths import MOD, VANILLA, BUILD
from ddsutil import read_dds

UC = "gfx/interface/unitcontrol/"
BAR = [("exercise_icon", "gfx/interface/", -25, 37, 1, 1), ("execute_mid", UC, 4, 32, 2, 1), ("cohesion_balanced", UC, 40, 32, 2, 1),
       ("proximity_close", UC, 77, 33, 2, 1), ("order_draw_naval_inv_btn", UC, 124, 33, 2, 0),
       ("order_draw_naval_inv_with_harbor_btn", UC, 158, 33, 2, 0), ("order_draw_paradrop_btn", UC, 194, 33, 2, 0),
       ("order_draw_defence_btn", UC, 239, 33, 2, 0), ("order_draw_offence_btn", UC, 276, 33, 2, 1),
       ("order_draw_blitz_btn", UC, 311, 33, 2, 0), ("order_draw_fallback_btn", UC, 355, 33, 2, 0),
       ("order_area_defense_btn", UC, 391, 33, 2, 0), ("order_assign_units_btn", UC, 437, 33, 2, 0),
       ("order_unassign_units_btn", UC, 472, 33, 2, 0), ("order_reshape_btn", UC, 517, 32, 2, 0),
       ("order_delete_btn", UC, 563, 33, 2, 0)]
POP = [("execute_slow", 15, 30, 1), ("execute_mid", 55, 30, 0), ("execute_fast", 96, 30, 1)]


def pic(rel, vanilla):
    if not vanilla:
        try:
            return read_dds(MOD + rel)
        except FileNotFoundError:
            pass
    return Image.open(VANILLA + rel).convert("RGBA")


def frame(im, n, i):
    fw = im.width // n
    return im.crop((i * fw, 0, (i + 1) * fw, im.height))


def draw(vanilla):
    cv = Image.new("RGBA", (720, 230), (58, 74, 60, 255))
    ox, oy = 60, 120                     # the window's origin (the bar picture sits 36 px left of it)
    cv.alpha_composite(pic(UC + "battleplantools_bg.dds", vanilla), (ox - 36, oy))
    for name, folder, x, y, n, f in BAR:
        cv.alpha_composite(frame(pic(folder + name + ".dds", vanilla), n, f), (ox + x, oy + y))
    px, py = ox - 50, oy - 50 - 125 + 60  # the planning pop-up over the priority button
    px, py = ox - 50 + 0, oy - 105
    cv.alpha_composite(pic(UC + "battleplantools_planning_bg.dds", vanilla), (px, py))
    for name, x, y, f in POP:
        cv.alpha_composite(frame(pic(UC + name + ".dds", vanilla), 2, f), (px + x, py + y))
    cv = cv.resize((cv.width * 2, cv.height * 2), Image.NEAREST)
    cv.save(BUILD + ("preview_battleplan_vanilla.png" if vanilla else "preview_battleplan.png"))


if __name__ == "__main__":
    draw(False)
    draw(True)
    print("wrote build/preview_battleplan.png (+ _vanilla)")
