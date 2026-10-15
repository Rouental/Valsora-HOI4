"""A preview of the army bar (v0.7), the game's look above and the Deco UI's below: an army group and its three
armies along the bottom of the screen, laid out from the game's leadergroups.gui positions. The game places the
cards in code; here each sits where its piece of the plate ends: the army group's piece (87.5 px) starts the plate,
each army's (80 px) carries it on, the last army's ends it. Stand-in portraits are the game's generic ones. One army
is selected, one has a battle plan running, one has no commander yet. The counts are drawn in the mod's font in the
box make_leadergroups.py gives them (layout_armybar), the game's in a stand-in font at its own place.

    python preview_armybar.py          -> build/preview_armybar.png
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

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

    def put(rel, x, y, frames=1, frame=0):
        cv.alpha_composite(tex(root, rel, frames, frame), (int(x), int(y)))

    texts = []

    def count(x, y, n, box, vanilla_xy):
        if root == MOD:      # the mod's count: its font, centred in the plaque's box (make_leadergroups.py)
            texts.append((str(n), x + box["x"], y + box["y"], box["w"], box["h"]))
        else:                # the game's: hoi_18mbs at the top of an 80 px box (a stand-in font here)
            d.text((x + vanilla_xy[0] + 40, y + vanilla_xy[1] + 2), str(n), font=f, fill=(244, 236, 217), anchor="ma")

    # the army group (field marshal): its card's piece of the plate starts the plate; its portrait window sits at
    # (-5, -5) of the group window
    put(UC + "army_group_back_bg.dds", 100 - 1, oy - 46, 2, 0)
    gx, gy = 100 - 5, oy - 5
    put(UC + "execute_stop_small_bg.dds", gx + 8, gy - 44)
    put(UC + "execute_btn_stop_small_ag.dds", gx + 10, gy - 42, 4, 0)
    put(UC + "execute_btn_play_small_ag.dds", gx + 40, gy - 42, 4, 0)
    cv.alpha_composite(portrait("gfx/leaders/Europe/Portrait_Europe_Generic_land_1.dds", .45), (gx + 8, gy - 15))
    put(UC + "leader_army_group_frame.dds", gx - 1, gy - 21, 3, 0)
    put(UC + "disband_orders_group.dds", gx + 68, gy - 15)
    count(gx, gy, 24, LA.COUNT_GROUP, (4, 75))
    put(UC + "army_group_expand_collapse.dds", gx + 73, gy - 15, 2, 1)
    # three armies: selected; plan running; no commander yet
    pics = ["gfx/leaders/Europe/Portrait_Europe_Generic_land_2.dds", "gfx/leaders/Europe/Portrait_Europe_Generic_land_3.dds", None]
    strips = ["army_mid_bg.dds", "army_mid_bg.dds", "army_end_bg.dds"]
    for i in range(3):
        x, y = 100 + 86 + i * 80, oy
        put(UC + strips[i], x + 1, y - 46, 2, 0)
        put(UC + "execute_stop_small_bg.dds", x + 4, y - 34)
        put(UC + "execute_btn_stop_small.dds", x + 6, y - 32, 4, 0)
        if i == 1:
            put(UC + "active_battleplan_anim.dds", x + 36, y - 31, 12, 4)
        else:
            put(UC + "execute_btn_play_small.dds", x + 36, y - 32, 4, 0)
        if pics[i]:
            cv.alpha_composite(portrait(pics[i], .39), (x + 8, y - 5))
        else:
            put(UC + "group_add_leader_bg.dds", x + 7, y - 6)
        put(UC + "leader_group_frame.dds", x - 1, y - 12, 4, 1 if i == 0 else 0)
        put(UC + "disband_orders_group.dds", x + 62, y - 7)
        count(x, y, [8, 12, 4][i], LA.COUNT_ARMY, (0, 75))
        if i == 1:                                    # the plan's strength: ours against theirs
            put(UC + "comm_group_plan_power_bar_bg.dds", x + 9, y + 92)
            fill = tex(root, UC + "comm_group_plan_power_bar.dds")
            cv.alpha_composite(fill.crop((0, 0, 38, fill.height)), (x + 9, y + 92))
    d.text((16, 14), title, font=small, fill=(232, 223, 200))
    if texts:                # the mod's bitmap font, drawn as the game would (validate_preview.draw_text)
        arr = np.asarray(cv.convert("RGB"), dtype=np.float32) / 255
        for s, x, y, w, h in texts:
            V.draw_text(arr, LA.COUNT_FONT, s, x, y, w, "centre", max_h=h, valign=True)
        cv = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
    return cv


def main():
    a = scene(VANILLA, "the game's army bar")
    b = scene(MOD, "Valsora Deco UI, v0.7")
    out = Image.new("RGB", (a.width, a.height * 2 + 6), (20, 24, 27))
    out.paste(a.convert("RGB"), (0, 0))
    out.paste(b.convert("RGB"), (0, a.height + 6))
    out.save(BUILD + "preview_armybar.png")
    zoom = b.crop((80, 120, 460, 300)).resize((760, 360), Image.LANCZOS)
    zoom.convert("RGB").save(BUILD + "preview_armybar_zoom.png")
    print("army bar preview written")


if __name__ == "__main__":
    main()
