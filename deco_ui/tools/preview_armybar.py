"""A preview of the army bar (v0.7), the game's look above and the Deco UI's below: an army group and its three
armies along the bottom of the screen, laid out from the game's leadergroups.gui positions. The game places the
cards in code; here each sits where its piece of the plate ends: the army group's piece (87.5 px) starts the plate,
each army's (80 px) carries it on, the last army's ends it. Stand-in portraits are the game's generic ones. One army
is selected, one has a battle plan running, one has no commander yet. Every piece is placed where the .gui of its scene
puts it (the game's leadergroups.gui, or the mod's from make_leadergroups.py). The counts are drawn in the mod's font in
the box make_leadergroups.py gives them (layout_armybar), the game's in a stand-in font at its own place.

    python preview_armybar.py          -> build/preview_armybar.png
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import guipatch as GP
import layout_armybar as LA
import validate_preview as V
from paths import ART, BUILD, MOD, VANILLA

UC = "gfx/interface/unitcontrol/"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def tex(root, rel, frames=1, frame=0):
    im = Image.open(root + rel).convert("RGBA")
    fw = im.width // frames
    return im.crop((frame * fw, 0, (frame + 1) * fw, im.height))


def portrait(rel, scale):
    im = Image.open(VANILLA + rel).convert("RGBA")
    return im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)


def scene(root, title):
    W, H = 900, 300
    bg = Image.open(ART + "map_rouental.jpg").convert("RGB").resize((1920, 1080), Image.LANCZOS).crop((0, 1080 - H, W, 1080))
    cv = bg.convert("RGBA")
    d = ImageDraw.Draw(cv)
    f = ImageFont.truetype(FONT, 15)
    small = ImageFont.truetype(FONT, 13)
    oy = H - 100                                      # the window's top: lower_left, y -100
    gui = open(root + "interface/leadergroups.gui", encoding="utf-8-sig").read().replace("\r\n", "\n")
    A, G = "leader_groups_portrait_window", "army_group_portrait_window"

    def at(win, name):                                # every position from the .gui this scene draws (the game's or ours)
        return GP.get_pos(gui, f"{win}>{name}")

    def put(rel, win, name, ox, oy_, frames=1, frame=0, dy=0):
        x, y = at(win, name)
        cv.alpha_composite(tex(root, rel, frames, frame), (int(ox + x), int(oy_ + y + dy)))

    texts = []

    def count(win, ox, oy_, n):
        x, y = at(win, "divisions_count")
        if root == MOD:      # the mod's count: its font, centred in the plaque's box (make_leadergroups.py)
            box = LA.COUNT_ARMY if win == A else LA.COUNT_GROUP
            texts.append((str(n), ox + box["x"], oy_ + box["y"], box["w"], box["h"]))
        else:                # the game's: hoi_18mbs at the top of an 80 px box (a stand-in font here)
            d.text((ox + x + 40, oy_ + y + 2), str(n), font=f, fill=(244, 236, 217), anchor="ma")

    # the army group (field marshal): its card's piece of the plate starts the plate; its portrait window sits at
    # (-5, -5) of the group window
    cv.alpha_composite(tex(root, UC + "army_group_back_bg.dds", 2, 0), (100 - 1, oy - 46))
    gx, gy = 100 - 5, oy - 5
    put(UC + "execute_stop_small_bg.dds", G, "small_button_bg", gx, gy)
    put(UC + "execute_btn_stop_small_ag.dds", G, "btn_stop", gx, gy, 4, 0)
    put(UC + "execute_btn_play_small_ag.dds", G, "btn_execute", gx, gy, 4, 0)
    x, y = at(G, "leader_icon")
    cv.alpha_composite(portrait("gfx/leaders/Europe/Portrait_Europe_Generic_land_1.dds", .45), (gx + x, gy + y))
    put(UC + "leader_army_group_frame.dds", G, "leader_frame", gx, gy, 3, 0)
    put(UC + "disband_orders_group.dds", G, "disband_leader_btn", gx, gy)
    count(G, gx, gy, 24)
    put(UC + "army_group_expand_collapse.dds", G, "expand", gx, gy, 2, 1)
    # three armies: selected; plan running; no commander yet
    pics = ["gfx/leaders/Europe/Portrait_Europe_Generic_land_2.dds", "gfx/leaders/Europe/Portrait_Europe_Generic_land_3.dds", None]
    strips = ["army_mid_bg.dds", "army_mid_bg.dds", "army_end_bg.dds"]
    for i in range(3):
        x0, y0 = 100 + 86 + i * 80, oy
        cv.alpha_composite(tex(root, UC + strips[i], 2, 0), (x0 + 1, y0 - 46))
        put(UC + "execute_stop_small_bg.dds", A, "small_button_bg", x0, y0)
        put(UC + "execute_btn_stop_small.dds", A, "btn_stop", x0, y0, 4, 0)
        if i == 1:
            put(UC + "active_battleplan_anim.dds", A, "btn_execute_anim", x0, y0, 12, 4)
        else:
            put(UC + "execute_btn_play_small.dds", A, "btn_execute", x0, y0, 4, 0)
        if pics[i]:
            x, y = at(A, "leader_icon")
            cv.alpha_composite(portrait(pics[i], .39), (x0 + x, y0 + y))
        else:
            put(UC + "group_add_leader_bg.dds", A, "portrait_btn", x0, y0)
        put(UC + "leader_group_frame.dds", A, "leader_frame", x0, y0, 4, 1 if i == 0 else 0)
        put(UC + "disband_orders_group.dds", A, "disband_leader_btn", x0, y0)
        count(A, x0, y0, [8, 12, 4][i])
        if i == 1:                                    # the plan's strength: ours against theirs
            put(UC + "comm_group_plan_power_bar_bg.dds", A, "plan_unit_power_bar", x0, y0)
            fill = tex(root, UC + "comm_group_plan_power_bar.dds")
            x, y = at(A, "plan_unit_power_bar")
            cv.alpha_composite(fill.crop((0, 0, 38, fill.height)), (x0 + x, y0 + y))
    d.text((16, 14), title, font=small, fill=(232, 223, 200))
    if texts:                # the mod's bitmap font, drawn as the game would (validate_preview.draw_text)
        arr = np.asarray(cv.convert("RGB"), dtype=np.float32) / 255
        for s, x, y, w, h in texts:
            V.draw_text(arr, LA.COUNT_FONT, s, x, y, w, "centre", max_h=h, valign=True)
        cv = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
    return cv


def main():
    a = scene(VANILLA, "the game's army bar")
    b = scene(MOD, "Valsora Deco UI, v0.8")
    out = Image.new("RGB", (a.width, a.height * 2 + 6), (20, 24, 27))
    out.paste(a.convert("RGB"), (0, 0))
    out.paste(b.convert("RGB"), (0, a.height + 6))
    out.save(BUILD + "preview_armybar.png")
    zoom = b.crop((80, 120, 460, 300)).resize((760, 360), Image.LANCZOS)
    zoom.convert("RGB").save(BUILD + "preview_armybar_zoom.png")
    print("army bar preview written")


if __name__ == "__main__":
    main()
