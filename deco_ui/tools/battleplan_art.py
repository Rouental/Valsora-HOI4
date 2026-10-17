"""The battle plan toolbar (interface/battleplantools.gui) in the deco style, at the game's paths and sizes (2026-10-17,
v0.10, SCREEN_INVENTORY.md's suggestion 4).

The toolbar rises from the bottom of the screen when an army is selected: a bar of wells for the order buttons
(battleplantools_bg, 641 x 79: the title band along its top, 16 wells in 7 groups under it, measured from the game's
picture), and the pop-ups over it (planning speed, cohesion, the HQ's proximity, the area defence settings): a plate with
a title band and a body for its buttons, and two legs down to the button that opened it (where the game's are). The
order and setting buttons keep the game's own glyphs, recoloured in gilt (their meaning and frame order stay exactly
the game's): the order buttons' second frame lit with a jade glow, the setting buttons' first frame (the chosen setting)
on a jade plate and the second on a plain one. The execution chevrons, the exercise icons and the selected order's
bracket are gilt too.

gen_textures.py adds them (keys bp_*).
"""
import numpy as np
from PIL import Image

from art_util import STRIPES, GOLD, LIT_FILL, DIM_FILL, chamfer, frames, vanilla_frames, gilt, img_tag

UC = "gfx/interface/unitcontrol/"
LAC = "linear-gradient(180deg,#18232A,#0D1418)"


def _poly(pts):
    return "polygon(" + ",".join(f"{x}px {y}px" for x, y in pts) + ")"


def _oct(x0, y0, x1, y1, c):
    return [(x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c), (x1 - c, y1), (x0 + c, y1), (x0, y1 - c), (x0, y0 + c)]


def plate(w, y1=77, legs=(), body=(30, 69)):
    """the lacquer plate (x 1 to w-1, y 1 to y1), its title band and the recessed body under it, and the legs"""
    out = (f'<div style="position:absolute;inset:0;background:{GOLD};clip-path:{_poly(_oct(1, 1, w - 1, y1, 7))}"></div>'
           f'<div style="position:absolute;inset:0;background:{STRIPES},{LAC};clip-path:{_poly(_oct(2.3, 2.3, w - 2.3, y1 - 1.3, 6.4))}"></div>'
           f'<div style="position:absolute;left:8px;right:8px;top:27px;height:1px;background:rgba(201,165,90,.7)"></div>'
           f'<div style="position:absolute;left:8px;right:8px;top:29px;height:1px;background:rgba(201,165,90,.25)"></div>')
    if body:
        out += (f'<div style="position:absolute;left:7px;right:7px;top:{body[0]}px;height:{body[1] - body[0]}px;background:#080C0F;'
                'box-shadow:inset 0 0 0 1px rgba(201,165,90,.35),inset 0 3px 4px rgba(0,0,0,.6)"></div>')
    for x0, x1 in legs:
        out += leg(x0, x1, y1, 124)
    return out + '<i class="ck sm tl" style="left:4px;top:4px"></i><i class="ck sm tr" style="right:4px;top:4px"></i>'


def leg(x0, x1, y0, y1):
    """a gilt rail hanging from a plate, a small diamond at its foot"""
    w = x1 - x0 + 1
    cx = x0 + w / 2
    return (f'<div style="position:absolute;left:{x0 + 1}px;top:{y0}px;width:{w - 2}px;height:{y1 - y0 - 5}px;'
            f'background:linear-gradient(90deg,#8B6A2C,#E8CD84 50%,#8B6A2C);box-shadow:0 0 0 1px rgba(11,16,20,.8)"></div>'
            f'<div style="position:absolute;left:{cx - 3.5}px;top:{y1 - 8}px;width:7px;height:7px;transform:rotate(45deg);'
            'background:#E3C77E;box-shadow:0 0 0 1px #0B1014"></div>')


# the bar's wells, measured from the game's picture (x ranges at y 33-65), in groups
WELLS = [[(9, 41), (45, 77), (81, 113), (117, 149)], [(160, 194), (196, 229), (233, 265)],
         [(276, 310), (312, 346), (348, 382)], [(392, 426), (428, 462)], [(475, 507), (511, 543)], [(554, 588)], [(601, 633)]]


def bar():
    out = plate(641, 77, body=())
    for gi, group in enumerate(WELLS):
        for x0, x1 in group:
            out += (f'<div style="position:absolute;left:{x0}px;top:33px;width:{x1 - x0}px;height:33px;background:#080C0F;'
                    'box-shadow:inset 0 0 0 1px rgba(201,165,90,.45),inset 0 3px 4px rgba(0,0,0,.6)"></div>')
        if gi:   # a diamond in the gap before each group
            gx = (WELLS[gi - 1][-1][1] + group[0][0]) / 2
            out += (f'<div style="position:absolute;left:{gx - 3}px;top:46px;width:6px;height:6px;transform:rotate(45deg);'
                    'background:#C9A55A"></div>')
    return out + '<i class="ck sm bl" style="left:4px;bottom:4px"></i><i class="ck sm br" style="right:4px;bottom:4px"></i>'


def glyph(img, cut=0):
    """the game's glyph in gilt; with cut, its dark box (pixels darker than cut) made see-through first"""
    a = np.asarray(img.convert("RGBA"), dtype=float).copy()
    if cut:
        lum = a[..., :3].mean(-1)
        a[..., 3] *= np.clip((lum - cut) / 25, 0, 1)
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def order_button(rel, w, h):
    """an order button (2 frames): its glyph in gilt, and lit (the second frame) over a jade glow"""
    f0, f1 = vanilla_frames(rel, 2)
    fw = w // 2
    glow = (f'<div style="position:absolute;left:{fw / 2 - 15}px;top:{h / 2 - 14}px;width:30px;height:28px;border-radius:50%;'
            'background:radial-gradient(ellipse,rgba(46,110,96,.75),rgba(46,110,96,0) 70%)"></div>')
    return frames(w, h, img_tag(gilt(f0)), glow + img_tag(gilt(f0, 1.2)))


def setting_button(rel, cut=0):
    """a setting button (80 x 36, 2 frames of 40): the chosen setting (frame 1) on a jade plate, the others (frame 2) on
    a plain one, the game's glyph in gilt on both (taken from its plain frame)"""
    f0, f1 = vanilla_frames(rel, 2)
    g = glyph(f1, cut)
    lit = (f'<div style="position:absolute;inset:2px 3px;background:{GOLD};clip-path:{chamfer(5)}"></div>'
           f'<div style="position:absolute;inset:3.2px 4.2px;background:{STRIPES},{LIT_FILL};clip-path:{chamfer(4.4)}"></div>')
    dim = (f'<div style="position:absolute;inset:2px 3px;background:rgba(201,165,90,.55);clip-path:{chamfer(5)}"></div>'
           f'<div style="position:absolute;inset:3.2px 4.2px;background:{STRIPES},{DIM_FILL};clip-path:{chamfer(4.4)}"></div>')
    return frames(80, 36, lit + img_tag(gilt(g, 1.15)), dim + img_tag(gilt(g)))


def strip(rel, w, h, n, gain=1.0):
    return frames(w, h, *[img_tag(gilt(f, gain)) for f in vanilla_frames(rel, n)])


def overlay():
    """the selected order's bracket (62 x 61): a gilt bar over the button and two legs down its sides (the game's)"""
    return (f'<div style="position:absolute;left:2px;top:2px;width:58px;height:14px;background:{GOLD};clip-path:{chamfer(3)}"></div>'
            f'<div style="position:absolute;left:3.2px;top:3.2px;width:55.6px;height:11.6px;background:{STRIPES},{LIT_FILL};clip-path:{chamfer(2.5)}"></div>'
            + leg(10, 15, 16, 61) + leg(46, 51, 16, 61))


ORDERS = ["order_area_defense_btn", "order_assign_units_btn", "order_delete_btn", "order_draw_blitz_btn",
          "order_draw_defence_btn", "order_draw_fallback_btn", "order_draw_naval_inv_btn", "order_draw_offence_btn",
          "order_draw_paradrop_btn", "order_reshape_btn", "order_unassign_units_btn"]
SETTINGS = ["cohesion_balanced", "cohesion_immobile", "cohesion_loose", "cohesion_strict", "execute_fast",
            "execute_mid", "execute_slow", "proximity_close", "proximity_far", "proximity_free_control",
            "proximity_frontline", "proximity_medium"]
GARRISON = ["garr_airbase", "garr_borders", "garr_coastline", "garr_facility", "garr_fort", "garr_port", "garr_rail", "garr_vp"]

ADDS = [
    ("bp_bar", UC + "battleplantools_bg.dds", 641, 79, bar),
    ("bp_areadef", UC + "battleplantools_areadef_conf_bg.dds", 347, 79, lambda: plate(347, 77, body=(30, 69))),
    ("bp_planning", UC + "battleplantools_planning_bg.dds", 148, 125, lambda: plate(148, 77, [(53, 58), (89, 94)])),
    ("bp_cohesion", UC + "battleplantools_cohesion_bg.dds", 188, 125, lambda: plate(188, 77, [(72, 77), (108, 113)])),
    ("bp_proximity", UC + "hq_proximity_settings_bg.dds", 214, 125, lambda: plate(214, 77, [(84, 89), (120, 125)])),
    ("bp_overlay", UC + "selected_order_overlay.dds", 62, 61, overlay),
    ("bp_execute_strip", UC + "plan_execution_small.dds", 81, 27, lambda: strip(UC + "plan_execution_small.dds", 81, 27, 3)),
    ("bp_exercise", "gfx/interface/exercise_icon.dds", 28, 27, lambda: strip("gfx/interface/exercise_icon.dds", 28, 27, 1)),
    ("bp_exercise_anim", "gfx/interface/exercise_anim_strip_big.dds", 520, 26,
     lambda: strip("gfx/interface/exercise_anim_strip_big.dds", 520, 26, 20)),
    ("bp_exercise_max", "gfx/interface/exercise_icon_stop_at_max_icon.dds", 14, 14,
     lambda: strip("gfx/interface/exercise_icon_stop_at_max_icon.dds", 14, 14, 1)),
]
ADDS += [("bp_" + n, UC + n + ".dds", 71 if n == "order_draw_naval_inv_with_harbor_btn" else 70,
          32 if n == "order_draw_naval_inv_with_harbor_btn" else 34,
          (lambda n=n: order_button(UC + n + ".dds", *((71, 32) if n == "order_draw_naval_inv_with_harbor_btn" else (70, 34)))))
         for n in ORDERS + ["order_draw_naval_inv_with_harbor_btn"]]
ADDS += [("bp_" + n, UC + n + ".dds", 80, 36, (lambda n=n: setting_button(UC + n + ".dds"))) for n in SETTINGS]
ADDS += [("bp_" + n, UC + n + ".dds", 80, 36, (lambda n=n: setting_button(UC + n + ".dds", 34))) for n in GARRISON]
