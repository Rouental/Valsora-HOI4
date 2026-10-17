"""Previews of the land battle window (landcombat.gui) on its new pictures (combat_art.py), and of the game's own look:
the window drawn from the game's .gui as the game lays it out (centred, at (-512, -256) from the screen's centre), with
what the game fills in at run time put where the .gui puts it: two generals' portraits and flags, the progress bar
and its heading, two tactics (the defender's countered), the traits row, a few divisions in each side's list and two
reserves each, the sample texts. The tactics list (its cards) is drawn beside it. The naval battle the same way,
with a few ships on its map.

    python preview_combat.py      -> build/preview_landcombat.png, preview_navalcombat.png (+ _vanilla.png)

They show the game's art (terrain, tactics, portraits), so they stay in the git-ignored build/ folder.
"""
import copy
import os

import numpy as np
from PIL import Image

import preview_panels as PP
import validate_preview as V
from paths import BUILD, VANILLA, VALSORA

GUI = VANILLA + "interface/landcombat.gui"
SAMPLES = {
    "window_title": "Battle of Carcarelle",
    "attacker_leader_name": "Serelle Cahun", "defender_leader_name": "Aldric Venn",
    "attacker_leader_skill": "4", "defender_leader_skill": "3",
    "attacker_army_width": "70/80", "defender_army_width": "56/80",
    "combat_width": "80",
    "attacker_committed_label": "5 Divisions", "defender_committed_label": "4 Divisions",
    "attacker_reserves_label": "2 Reserves", "defender_reserves_label": "3 Reserves",
    "attacker_air_count": "24", "attacker_air_text": "Close air support",
}
HIDE = {"defender_air_icon", "defender_air_count", "defender_air_text", "attacker_countered_tactic_overlay",
        "defender_leader_initiative_overlay_glow", "defender_leader_army_hq_icon"}
PROGRESS = 0.62          # the attacker's share of the bar
FLAGS = {"attacker_flag": "ROU", "defender_flag": "CRD"}
TACTICS = {"attacker_tactic": "assault", "defender_tactic": "defend"}
TRAITS = 3               # trait icons drawn on each side's row (stand-ins: the game's trait pictures)


def _set(elems, name, **kv):
    """set attributes of the element called name, anywhere in the tree"""
    for i, (k, b) in enumerate(elems):
        if isinstance(b, list):
            if V.attrs(b).get("name") == name:
                nb = [(kk, vv) for kk, vv in b if not (kk and kk.lower() in kv)]
                nb += list(kv.items())
                elems[i] = (k, nb)
                return True
            if _set(b, name, **kv):
                return True
    return False


class Battle(PP.Panel):
    """the game's renderer, with the run-time pictures: flags, tactics, progress bars"""
    def __init__(self, bars=None, **kw):
        super().__init__(**kw)
        self.bars = bars or {}

    def picture(self, cv, spr, ax, ay, w, h, frame, scale, centre=False):
        if spr and spr.startswith("FLAG:"):
            tag = spr[5:]
            img = None
            for p in (VALSORA + f"gfx/flags/medium/{tag}.tga",):
                if os.path.isfile(p):
                    img = Image.open(p).convert("RGBA")
            if img is None:
                return None
            img = img.transpose(Image.FLIP_TOP_BOTTOM) if _tga_bottom_up(VALSORA + f"gfx/flags/medium/{tag}.tga") else img
            ov = PP.texture("gfx/interface/flag_overlay_small.dds", self.vanilla_only)
            V.paste(cv, img, ax, ay)
            if ov is not None:
                V.paste(cv, ov, ax, ay)
            return img.size
        if spr and spr.startswith("PIC:"):
            img = Image.open(VANILLA + spr[4:]).convert("RGBA")
            V.paste(cv, img, ax, ay)
            return img.size
        d, _ = PP.sprite(spr, self.vanilla_only) if spr else (None, None)
        if d and d["kind"] == "progressbartype":
            return self.progress(cv, spr, ax, ay)
        return super().picture(cv, spr, ax, ay, w, h, frame, scale, centre)

    def progress(self, cv, spr, ax, ay):
        if spr == "GFX_landcombat_progress":
            a = PP.texture("gfx/interface/landcombat_attacker_progress.dds", self.vanilla_only)
            b = PP.texture("gfx/interface/landcombat_defender_progress.dds", self.vanilla_only)
            V.paste(cv, b, ax, ay)
            V.paste(cv, a.crop((0, 0, int(a.width * PROGRESS), a.height)), ax, ay)
            return a.size
        if not spr.startswith("GFX_combat_unit_bar_"):
            return None          # the naval bar: drawn by draw_naval
        # a division's organisation or strength: 16 x 7, turned a quarter (rotation 1.5708): it rises from (x, y)
        val = self.bars.get(spr, .7)
        fill = PP.texture("gfx/interface/mapicons/mapicon_bar_" + ("org" if "org" in spr else "str") + ".dds", True)
        bg = PP.texture("gfx/interface/mapicons/mapicon_bar_bg.dds", True)
        fill = fill.resize((16, 7)).crop((0, 0, max(1, int(16 * val)), 7))
        im = bg.resize((16, 7)).copy()
        im.alpha_composite(fill)
        V.paste(cv, im.rotate(90, expand=True), ax, ay - 16)
        return 7, 16


def _tga_bottom_up(path):
    with open(path, "rb") as f:
        h = f.read(18)
    return not (h[17] & 0x20)


def _entry(cv, elems, name, x, y, vanilla, samples, bars):
    win = copy.deepcopy(PP.find_window(elems, name))
    p = Battle(vanilla_only=vanilla, samples=samples, outline_lists=False, bars=bars)
    p.draw(cv, [("containerWindowType", [(k, v) for k, v in win if not (k and k.lower() == "position")]
                 + [("position", [("x", str(x)), ("y", str(y))])])], 0, 0, 1920, 1080)


DIVS = [("1st Royal Armoured", "412", "88", "260"), ("Garde Royale", "390", "41", "310"),
        ("3rd Motorised", "296", "22", "214"), ("Levée de Serpette", "180", "6", "155"), ("Ost de Vair", "205", "9", "170")]
DEFS = [("12th Infantry Division", "150", "12", "402"), ("4th Mountain Division", "132", "8", "380"),
        ("Coreilia Guard", "160", "20", "355"), ("7th Infantry Division", "141", "10", "390")]


def draw(vanilla):
    elems = V.load(GUI)
    for k, v in FLAGS.items():
        _set(elems, k, quadTextureSprite="FLAG:" + v)
    for k, v in TACTICS.items():
        _set(elems, k, spriteType=f"PIC:gfx/interface/landcombat/tactics/{v}.dds")
    win = PP.find_window(elems, "landcombatview")
    cv = PP.backdrop(False)
    p = Battle(vanilla_only=vanilla, samples=SAMPLES, hide=HIDE, outline_lists=False)
    p.draw(cv, [("containerWindowType", win)], 0, 0, 1920, 1080)
    X, Y = 448, 284          # the window: centred, (-512, -256) from the screen's centre
    # the heading indicator where the two sides meet on the bar (the game moves it there)
    d, img = PP.sprite("GFX_land_battle_heading_indicator_strip", vanilla)
    V.paste(cv, PP.frame_of(img, d, 1), X + 185 + 179 * PROGRESS - 6, Y + 116)
    # traits: the game's trait pictures in the two grids (attacker from x 100 rightwards, defender to 470 leftwards)
    tr = [Image.open(VANILLA + "gfx/interface/" + f).convert("RGBA") for f in
          ("traits/trait_aggressive_assaulter.dds", "traits/trait_infantry_leader.dds",
           "traits/trait_engineer.dds")
          if os.path.isfile(VANILLA + "gfx/interface/" + f)]
    for i, t in enumerate(tr[:TRAITS]):
        t = t.resize((17, 25), Image.LANCZOS)
        V.paste(cv, t, X + 102 + 21 * i, Y + 148)
        V.paste(cv, t, X + 470 - 21 * (i + 1) + 2, Y + 148)
    # the lists: committed (window 300 + committed 19 + margin 10, grid x 31 / 10, 40 a slot), clipped as the game
    # clips them to their committed_window (280 x 175 at 0 / 285, 319: clipping = yes), then the reserves
    for divs, entry, gx, wx, org in ((DIVS, "division_combat_attacker_entry", 31, 0, .9),
                                      (DEFS, "division_combat_defender_entry", 10, 285, .5)):
        tmp = cv.copy()
        for i, (nm, sa, ha, de) in enumerate(divs):
            _entry(tmp, elems, entry, X + wx + gx, Y + 329 + 40 * i, vanilla,
                   {"name": nm, "soft_attack": sa, "hard_attack": ha, "defense": de},
                   {"GFX_combat_unit_bar_org": org - .1 * i, "GFX_combat_unit_bar_str": 1 - .05 * i})
        cv[Y + 319:Y + 494, X + wx:X + wx + 280] = tmp[Y + 319:Y + 494, X + wx:X + wx + 280]
    for side, gx, n in (("attacker", RES_X[0], 2), ("defender", RES_X[1], 3)):
        for i in range(n):
            _entry(cv, elems, "reserve_combat_entry", X + gx + 119 * (i % 2), Y + 515 + 26 * (i // 2), vanilla,
                   {"name": ["Levée de Brie", "2nd Infantry", "Ost de Lys"][i]}, {})
    # the tactics list beside it, one card per frame (the game's 5 frames)
    tl = PP.find_window(elems, "tactics_list_view")
    TX, TY = X + 567 + 30, Y
    q = Battle(vanilla_only=vanilla, samples={"current_phase": "Current phase: Default",
                                                "preferred_tactic_desc_text": "Preferred tactic:"},
               hide={"tactics_list_container"}, outline_lists=False)
    q.draw(cv, [("containerWindowType", [(k, v) for k, v in tl if not (k and k.lower() == "position")]
                 + [("position", [("x", str(TX)), ("y", str(TY))])])], 0, 0, 1920, 1080)
    ent = PP.find_window(elems, "tactics_list_entry")
    for i in range(5):
        e = copy.deepcopy(ent)
        _set(e, "tactics_icon", spriteType="PIC:gfx/interface/landcombat/tactics/" + ["assault", "defend", "encircle",
                                                                                      "elastic_defence", "assault"][i] + ".dds")
        q2 = Battle(vanilla_only=vanilla, frames={"Background": i, "button_background": i}, outline_lists=False,
                    hide={"locked_icon", "command_power_cost"} | ({"locked_icon"} if i != 2 else set()),
                    samples={"tactics_name": ["Assault", "Defend", "Encircle", "Elastic Defence", "Assault"][i],
                             "phase": ["Default", "Default", "Locked", "Preferred", "Preferred"][i],
                             "attacker_damage_value": "+10%", "defender_damage_value": "-5%",
                             "combat_width_change_value": "+0%", "attacker_speed_value": "+5%",
                             "attacker_org_modifier_value": "+5%", "defender_org_modifier_value": "-2%",
                             "tactics_chance": "4%"})
        q2.draw(cv, [("containerWindowType", [(k, v) for k, v in e if not (k and k.lower() == "position")]
                      + [("position", [("x", str(TX + 13)), ("y", str(TY + 125 + 94 * i))])])], 0, 0, 1920, 1080)
    out = Image.fromarray((np.clip(cv, 0, 1) * 255).astype(np.uint8))
    out = out.crop((X - 20, Y - 20, TX + 392 + 20, Y + 617 + 20))
    out.save(BUILD + "preview_landcombat" + ("_vanilla" if vanilla else "") + ".png")
    return out


NAVAL_GUI = VANILLA + "interface/navalcombat.gui"
# ships on the map: (icon file, x, y, frame) in the window; the game places them by code, in its columns (carriers
# 142-260, the line 260-406, screens 406-528, then the defender's mirrored; submarines from y 520)
SHIPS = [("battleship", 300, 300, 0), ("heavy_cruiser", 296, 350, 0), ("destroyer", 430, 290, 0), ("destroyer", 425, 330, 0),
         ("light_cruiser", 432, 380, 0), ("carrier", 160, 320, 0), ("submarine", 440, 548, 0),
         ("battleship", 668, 310, 1), ("destroyer", 545, 300, 1), ("destroyer", 552, 350, 1), ("light_cruiser", 548, 400, 1),
         ("submarine", 560, 560, 1), ("destroyer", 25, 330, 0), ("destroyer", 942, 300, 1)]


def draw_naval(vanilla):
    elems = V.load(NAVAL_GUI)
    _set(elems, "flag_attacker", quadTextureSprite="FLAG:ROU")
    _set(elems, "flag_defender", quadTextureSprite="FLAG:CRD")
    win = PP.find_window(elems, "navalcombatview")
    cv = PP.backdrop(False)
    X, Y = 960 - 528, 540 - 356
    samples = {"naval_battle_title": "Naval Battle of the Northern Ocean", "leader_attacker_name": "Ysolde Marec",
               "leader_defender_name": "Teo Vasks", "leader_attacker_ships_count": "", "leader_defender_ships_count": "",
               "leader_stat_attack_text": "4", "leader_stat_defense_text": "3", "leader_stat_maneuvering_text": "5",
               "leader_stat_coordination_text": "2"}
    for k in ("stat_depth_charges", "stat_anti_air", "stat_torpedo", "stat_heavy_gun", "stat_light_gun", "stat_positioning"):
        samples[k] = "123"
    for k in ("left_wnd_capital_screening_efficiency", "left_wnd_carrier_screening_efficiency",
              "right_wnd_capital_screening_efficiency", "right_wnd_carrier_screening_efficiency"):
        samples[k] = "100%"
    p = Battle(vanilla_only=vanilla, samples=samples, hide={"progress_defender"}, outline_lists=False)
    p.draw(cv, [("containerWindowType", win)], 0, 0, 1920, 1080)
    # the progress bar (the attacker's: "loose" from the left, "win" behind it), drawn where the .gui puts it
    a = PP.texture("gfx/interface/navalcombat/bar_progress_loose.dds", vanilla)
    b = PP.texture("gfx/interface/navalcombat/bar_progress_win.dds", vanilla)
    V.paste(cv, b, X + 125 + 227, Y + 133)
    V.paste(cv, a.crop((0, 0, int(a.width * .45), a.height)), X + 125 + 227, Y + 133)
    for name, x, y, fr in SHIPS:
        im = Image.open(VANILLA + f"gfx/interface/navalcombat/ships/{name}.dds").convert("RGBA")
        V.paste(cv, im, X + x, Y + y, frame=fr, frames=2)
    out = Image.fromarray((np.clip(cv, 0, 1) * 255).astype(np.uint8)).crop((X - 20, Y - 20, X + 1056 + 20, Y + 736 + 20))
    out.save(BUILD + "preview_navalcombat" + ("_vanilla" if vanilla else "") + ".png")


# the reserves' grids: the game's gridboxes sit at x -56 and -80 in their windows, which as read would put the first
# column outside the window; drawn here two columns under each side's "Reserves" label instead (assumed)
RES_X = (27 + 3, 285 + 10 + 3)


if __name__ == "__main__":
    import sys
    van = "--vanilla-only" in sys.argv
    if not van:
        draw(False)
        draw_naval(False)
    draw(True)
    draw_naval(True)
    print("wrote build/preview_landcombat.png, preview_navalcombat.png (+ _vanilla)")
