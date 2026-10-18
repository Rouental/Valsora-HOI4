"""The window frames the core skin had missed (2026-10-17, v0.10, SCREEN_INVENTORY.md's suggestion 8), at the game's
paths and sizes, laid out where the game's are (measured from its pictures and the .gui files that use them):

- tiled_window_w_close (192 x 192, a cornered tile, border 64): the aces, air wing and carrier windows; a socket for
  the close button in its top right corner (the button sits at x 147, y 13, 32 x 33);
- tiled_window_pol_goal (382 x 382, a cornered tile, border x 180 y 85) and pol_goal_popup_bg (480 x 382): the
  confirmation popups (default_confirmation_popup, release_country_dialog, peace_summary_popup_window,
  unlock_industrial_org_trait_popup): a header band for the title (y 16 to 56), the body under it;
- hint_bg (613 x 576): the tutorial's hints, a title plate (x 114 to 502, y 28) between two roundels, the body, a
  footer band (the game's ends at y 569);
- world_tension_bg (527 x 534): the world tension window, the same header (title y 28), a recessed band for the sort
  buttons (y 87 to 116), the list (from y 126), a footer band for the close button (y 475 to 509; the game's ends at
  y 526).

The game's bronze medallions are gilt roundels with a four-pointed star, its leather band a recessed lacquer one.

The popups' header strips, laid over a frame at (0 to 3, 8) (popupwindow.gui: the diplomatic requests, lend-lease and
foreign manpower offers, the scripted diplomacy popups, confirmations, surrenders, exiles, a finished focus; the
multiplayer connect window): diplo_popup_header_bg (494 x 86) and _large (584 x 87), a band (y 6 to 66) with the title
plate (x 82 to 412, clear of the war medallions at either end of a confirmation, and 108 to 476; the title at y 21 to 28 of the strip), plain at its ends, where the
game puts flags or the war medallion; diplo_popup_bottom_large (584 x 72), the plate under their buttons (popup_art's,
wider); diplo_war_large_icon (57 x 76), the medallion at either end of a confirmation's header: the diplomacy windows'
gilt octagon with the crossed blades (diplo_art.py).
gen_textures.py adds them (keys wf_*).
"""
from art_util import GOLD, STRIPES, chamfer
import diplo_art as DA

LAC = f"{STRIPES},linear-gradient(180deg,#131C22,#0E1519)"
HEAD = f"{STRIPES},linear-gradient(180deg,#1C2830,#141E24)"
WELL = "linear-gradient(180deg,#0A1014,#070B0E)"
RIM = "#B8954F"


def shell(w, h, corners=True):
    """the lacquer plate (w x h), its double gilt rule and corner brackets"""
    out = (f'<div style="position:absolute;left:0;top:0;width:{w}px;height:{h}px;background:{LAC};'
           'box-shadow:inset 0 0 0 1px rgba(0,0,0,.6)"></div>'
           f'<div class="frame" style="left:1px;top:1px;width:{w - 2}px;height:{h - 2}px;border:1px solid {RIM}"></div>'
           f'<div class="frame" style="left:5px;top:5px;width:{w - 10}px;height:{h - 10}px;border:1px solid rgba(201,165,90,.45)"></div>')
    if corners:
        out += (f'<i class="ck" style="left:2px;top:2px"></i><i class="ck" style="left:{w - 18}px;top:2px;transform:scaleX(-1)"></i>'
                f'<i class="ck" style="left:2px;top:{h - 18}px;transform:scaleY(-1)"></i>'
                f'<i class="ck" style="left:{w - 18}px;top:{h - 18}px;transform:scale(-1,-1)"></i>')
    return out


def band(w, y0, y1, fill=HEAD, top=False, bottom=True):
    """a band across the plate inside its inner rule (x 6 to w-6), gilt rules on its edges"""
    out = f'<div style="position:absolute;left:6px;top:{y0}px;width:{w - 12}px;height:{y1 - y0}px;background:{fill}"></div>'
    if bottom:
        out += (f'<div style="position:absolute;left:6px;top:{y1}px;width:{w - 12}px;height:1px;background:rgba(201,165,90,.8)"></div>'
                f'<div style="position:absolute;left:6px;top:{y1 + 3}px;width:{w - 12}px;height:1px;background:rgba(201,165,90,.3)"></div>')
    if top:
        out += (f'<div style="position:absolute;left:6px;top:{y0 - 1}px;width:{w - 12}px;height:1px;background:rgba(201,165,90,.8)"></div>'
                f'<div style="position:absolute;left:6px;top:{y0 - 4}px;width:{w - 12}px;height:1px;background:rgba(201,165,90,.3)"></div>')
    return out


def diamond(cx, cy, r=3.5, color="#C9A55A"):
    return (f'<div style="position:absolute;left:{cx - r}px;top:{cy - r}px;width:{2 * r}px;height:{2 * r}px;'
            f'transform:rotate(45deg);background:{color}"></div>')


def star(cx, cy, r):
    """a four-pointed gilt star"""
    k = r * .28
    pts = [(cx, cy - r), (cx + k, cy - k), (cx + r, cy), (cx + k, cy + k), (cx, cy + r), (cx - k, cy + k), (cx - r, cy), (cx - k, cy - k)]
    poly = ",".join(f"{x:.1f}px {y:.1f}px" for x, y in pts)
    return f'<div style="position:absolute;inset:0;background:{GOLD};clip-path:polygon({poly})"></div>'


def roundel(cx, cy, r):
    """a gilt roundel: two rings, a dark field and a four-pointed star"""
    return (f'<div style="position:absolute;left:{cx - r}px;top:{cy - r}px;width:{2 * r}px;height:{2 * r}px;border-radius:50%;'
            f'background:{GOLD}"></div>'
            f'<div style="position:absolute;left:{cx - r + 2.5}px;top:{cy - r + 2.5}px;width:{2 * r - 5}px;height:{2 * r - 5}px;'
            'border-radius:50%;background:radial-gradient(circle,#1E2B33,#0A1014 75%)"></div>'
            f'<div style="position:absolute;left:{cx - r + 6}px;top:{cy - r + 6}px;width:{2 * r - 12}px;height:{2 * r - 12}px;'
            'border-radius:50%;border:1px solid rgba(201,165,90,.55)"></div>'
            + star(cx, cy, r - 9))


def plate(x0, y0, x1, y1):
    """a recessed title plate with a gilt rim"""
    return (f'<div style="position:absolute;left:{x0}px;top:{y0}px;width:{x1 - x0}px;height:{y1 - y0}px;background:{GOLD};'
            f'clip-path:{chamfer(7)}"></div>'
            f'<div style="position:absolute;left:{x0 + 1.3}px;top:{y0 + 1.3}px;width:{x1 - x0 - 2.6}px;height:{y1 - y0 - 2.6}px;'
            f'background:{WELL};clip-path:{chamfer(6.4)};box-shadow:inset 0 3px 5px rgba(0,0,0,.7)"></div>'
            + diamond(x0 + 11, (y0 + y1) / 2, 2.5) + diamond(x1 - 11, (y0 + y1) / 2, 2.5))


def w_close():
    """tiled_window_w_close: the plate with a socket for the close button in its top right corner"""
    return (shell(192, 192).replace('<i class="ck" style="left:174px;top:2px;transform:scaleX(-1)"></i>', '')
            + f'<div style="position:absolute;left:143px;top:9px;width:40px;height:40px;background:{GOLD};clip-path:{chamfer(5)}"></div>'
            f'<div style="position:absolute;left:144.3px;top:10.3px;width:37.4px;height:37.4px;background:{WELL};'
            f'clip-path:{chamfer(4.4)};box-shadow:inset 0 2px 4px rgba(0,0,0,.7)"></div>')


# the release dialog's text (make_popups.py, v0.10.2): under the header band, ending above the first checkbox (y 198)
RELEASE_TEXT_Y, RELEASE_TEXT_END = 76, 190


def pol_goal(w, h):
    """the confirmation popups: a header band for the title (y 6 to 62), the body under it"""
    return shell(w, h) + band(w, 6, 62) + diamond(20, 34) + diamond(w - 20, 34)


def hint():
    """hint_bg: title plate between two roundels, body, footer band; the plate ends at y 570 as the game's does"""
    w, h = 613, 570
    return (shell(w, h) + band(w, 6, 72) + band(w, 516, h - 6, top=True, bottom=False)
            + plate(100, 18, w - 100, 62) + roundel(50, 39, 29) + roundel(w - 50, 39, 29))


def tension():
    """world_tension_bg: the same header, a recessed band for the sort buttons, the list, a footer band (to y 527)"""
    w, h = 527, 527
    return (shell(w, h) + band(w, 6, 72) + plate(92, 18, w - 92, 62) + roundel(46, 39, 29) + roundel(w - 46, 39, 29)
            + band(w, 80, 121, fill=WELL, top=True) + band(w, 470, h - 6, top=True, bottom=False))


def popup_header(w, x0, x1):
    """the popups' header strip: a band (y 6 to 66) under a double gilt rule, the title plate (x0 to x1, y 14 to 56),
    gilt hairlines along the plain ends"""
    out = (f'<div style="position:absolute;left:3px;top:6px;width:{w - 6}px;height:60px;background:{HEAD};'
           'box-shadow:0 2px 4px rgba(0,0,0,.55)"></div>'
           f'<div style="position:absolute;left:3px;top:6px;width:{w - 6}px;height:1px;background:rgba(201,165,90,.55)"></div>'
           f'<div style="position:absolute;left:3px;top:66px;width:{w - 6}px;height:1px;background:rgba(201,165,90,.8)"></div>'
           f'<div style="position:absolute;left:3px;top:69px;width:{w - 6}px;height:1px;background:rgba(201,165,90,.3)"></div>')
    for a, b in ((10, x0 - 14), (x1 + 14, w - 10)):
        for y in (20, 52):
            out += (f'<div style="position:absolute;left:{a}px;top:{y}px;width:{b - a}px;height:1px;'
                    'background:linear-gradient(90deg,rgba(201,165,90,0),rgba(201,165,90,.5) 30%,rgba(201,165,90,.5) 70%,rgba(201,165,90,0))"></div>')
    half = (x1 - x0) / 2 - 20
    return out + DA.title_plate((x0 + x1) / 2, half, 14, 56, gid="wf_tg")


def popup_bottom_large():
    """diplo_popup_bottom_large, 584 x 72: popup_art's footer plate (it imports this module: imported here)"""
    from popup_art import foot_plate
    return foot_plate(12, 8, 572, 53)


def war_icon():
    """diplo_war_large_icon, 57 x 76: the gilt octagon with the crossed blades, centred where the game's medal is"""
    return DA.medallion(28.5, 38, "blades", gid="wf_wg", r=26)


ADDS = [
    ("wf_w_close", "gfx/interface/tiles/tiled_window_w_close.dds", 192, 192, w_close),
    ("wf_pol_goal", "gfx/interface/tiles/tiled_window_pol_goal.dds", 382, 382, lambda: pol_goal(382, 382)),
    ("wf_pol_goal_popup", "gfx/interface/pol_goal_popup_bg.dds", 480, 382, lambda: pol_goal(480, 382)),
    ("wf_hint", "gfx/interface/tutorial/hint_bg.dds", 613, 576, hint),
    ("wf_tension", "gfx/interface/world_tension_bg.dds", 527, 534, tension),
    ("wf_popup_header", "gfx/interface/diplo_popup_header_bg.dds", 494, 86, lambda: popup_header(494, 82, 412)),
    ("wf_popup_header_large", "gfx/interface/diplo_popup_header_bg_large.dds", 584, 87, lambda: popup_header(584, 108, 476)),
    ("wf_popup_bottom_large", "gfx/interface/diplo_popup_bottom_large.dds", 584, 72, popup_bottom_large),
    ("wf_war_icon", "gfx/interface/diplo_war_large_icon.dds", 57, 76, war_icon),
]
