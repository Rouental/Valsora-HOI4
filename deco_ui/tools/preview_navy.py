"""A preview of the selected fleet's panel (naviesview.gui, make_mapviews.py): the fleet's header, its tool bar, a task
force (the reserve fleet of the user's screenshot, 2026-10-17) and its ships' rows, drawn from the mod's .gui with the
mod's textures and fonts, as the game stacks them below the flag medallion; the texts are the screenshot's.

    python preview_navy.py [naviesview.gui]   -> build/preview_navy.png at 2x (another .gui: preview_navy_<name>.png)

What the game does at runtime and the preview copies (inferred from the screenshot, where it cut "Advanced Destroyer
(Advanced Destroyer I)" after 235-241 px): a ship's name and type are cut short ("...") to end where the first of the
row's right-hand pieces begins (the task force's insignia at x 450; the refit and repair buttons and the damage report
further left when they show: the game's file says "maxWidth is shrinked in code when necessary (e.g. buttons are
shown)"), and a fixed-size box cuts its text the same way at its maxWidth. Every text is checked against the room it
has: cut short, or past the recess the mod's fleet picture draws round it (the admiral's rank and name), is a problem.
Lines wrap 1 px short of their box, as the game's do (preview_events.STRICT).
The game's own art is drawn, so the picture stays in the git-ignored build/ folder.
"""
import contextlib
import io
import os
import re
import sys

import numpy as np
from PIL import Image

import layout as L
from paths import BUILD, MOD, VANILLA

with contextlib.redirect_stdout(io.StringIO()):          # validate_preview reports its checks when imported
    import preview_panels as PP
    import validate_preview as V

GUI = sys.argv[1] if len(sys.argv) > 1 else MOD + "interface/naviesview.gui"
OUT = BUILD + ("preview_navy.png" if len(sys.argv) < 2 else
               "preview_navy_" + os.path.splitext(os.path.basename(GUI))[0] + ".png")

HEADER = {"fleet_name": "Rouental Fleet 1", "taskforce_count": "1/10", "leader_desc": "Admiral",
          "leader_name": "Napoléon de Montebrise", "skill_text": "1", "leader_stat_attack_text": "1",
          "leader_stat_defense_text": "1", "leader_stat_maneuvering_text": "1", "leader_stat_coordination_text": "1",
          "active_in_regions": "Active in Regions: 0", "home_base_name": "Caux-Gautier", "select_all_btn": "Select All"}
HEADER_HIDE = {"leader_icon", "leader_enroute", "click_to_assign", "fuel_efficiency_warning_icon", "air_base_btn",
               "btn_fleet_color", "highlight", "pride_of_the_fleet_icon"}
# the rank and name sit in a recess of the mod's fleet picture (mapview_art.fleet_bg: x 79-197 on the picture, which
# the game draws 2 px left of the window's origin): text past it runs under the admiral's skill
RECESS = {"leader_desc": 195, "leader_name": 195}
TASK_FORCE = {"unit_name": "Rouental Reserve fleet 1", "activity_description": "Docked in Caux-Gautier", "select_btn": "Back"}
TF_HIDE = {"highlight", "pride", "naval_headquarter_icon", "air_base", "interrupted_mission", "current_mission",
           "underway_replenishment_icon", "dominance", "fuel_efficiency_warning_icon", "fleet_insigna", "ships_compact",
           "ships_detailed", "toggle_btn_split_for_repair_indiv", "toggle_btn_split_for_repair_indiv_icon"}
# the ships' rows: the screenshot's six destroyers, then longer types (the game's hull names, the second in a variant
# named by the player) and real names, and one row with its refit button showing (the type's room then ends at it)
SHIPS = [("Advanced Destroyer", "Advanced Destroyer (Advanced Destroyer I)", False)] * 2 + [
    ("Reine Serelle", "Advanced Heavy Ship (Advanced Heavy Ship II)", False),
    ("Principauté de Rouental", "Coastal Defense Ship (Coastal Defense Ship I)", False),
    ("Saint-Roland", "Converted Battleship (Converted Battleship I)", False),
    ("Carcarelle", "Advanced Cruiser (Rêverie Class)", True)]
ROW_HIDE = {"highlight", "plane_icon", "bar_planes", "pride", "history_report_button", "exile_force_flag_frame",
            "foreign_ship_flag", "available_medals", "repair_symbol", "damaged_part_report", "btn_repair_now"}
# the row's right-hand pieces the game cuts the name and type short at (anchored UPPER_RIGHT in the 460 px row)
RIGHT = ("task_force_insignia", "btn_refit", "btn_repair_now", "damaged_part_report")


def game_font_names():
    """the game's names (core.gfx) for the font files the mod redraws, which a .gui may use (Main_14_bold is the
    garamond_14_bold file in white)"""
    t = open(VANILLA + "interface/core.gfx", encoding="utf-8-sig", errors="ignore").read()
    for m in re.finditer(r'bitmapfont\s*=\s*\{\s*name\s*=\s*"([^"]+)"\s*path\s*=\s*"gfx/fonts/([^"]+)"\s*'
                         r'color\s*=\s*0x([0-9a-fA-F]{8})', t):
        name, base, c = m.groups()
        if name not in V.FONTS and base in V.FONTS:
            c = int(c, 16)
            V.FONTS[name] = dict(V.FONTS[base], color=((c >> 16) & 255, (c >> 8) & 255, c & 255))


def boxes(body):
    """name -> the text box's attributes, for every text box in a window"""
    out = {}
    for k, v in body:
        if isinstance(v, list):
            if k and k.lower() in ("instanttextboxtype", "textboxtype", "editboxtype", "buttontype"):
                out[V.attrs(v).get("name")] = V.attrs(v)
            out.update({n: a for n, a in boxes(v).items() if n not in out})
    return out


def cut(font, text, max_w):
    """the game's cut: the longest start of the text that fits with '...' after it"""
    f = V.FONTS[font]
    w = lambda s: V.text_width(f, V._runs(s, None))
    if w(text) <= max_w:
        return text, False
    n = len(text)
    while n and w(text[:n].rstrip() + "...") > max_w:
        n -= 1
    return text[:n].rstrip() + "...", True


class Fleet(PP.Panel):
    """the panel with the game's runtime cuts, and a record of every text's fit"""

    def __init__(self, body, room=None, recess=None, ox=0, **kw):
        super().__init__(**kw)
        self.attrs, self.room, self.recess, self.ox, self.fits = boxes(body), room or {}, recess or {}, ox, []

    def text(self, cv, text, font, x, y, w, h, fmt, name, valign=False):
        a = self.attrs.get(name, {})
        font = (font or "").strip('"')
        if font in V.FONTS and name in self.samples:
            text, f = self.samples[name], V.FONTS[font]
            room = self.room.get(name, w)
            lh = int(f["common"]["lineHeight"])
            one_line = not (h and h >= 2 * lh)
            shown, was_cut = text, False
            if room and one_line and (a.get("fixedsize") == "yes" or name in self.room):
                shown, was_cut = cut(font, text, room)
            # a box of several lines: the game's word wrap; lines past its height are dropped (cut)
            lines = V.wrap(V._runs(shown, None), None if one_line else room - 1, lambda rs: V.text_width(f, rs))
            if not one_line and len(lines) * lh > h + 2:
                was_cut, shown = True, " / ".join("".join(c for c, _ in ln) for ln in lines[:int((h + 2) // lh)]) + " ..."
            width = max(V.text_width(f, ln) for ln in lines)
            over = name in self.recess and x + width > self.ox + self.recess[name]
            self.fits.append((name, font, text, shown if one_line or was_cut else
                              " / ".join("".join(c for c, _ in ln) for ln in lines), room, was_cut, over))
            if was_cut or over:
                V.problems.append(f"navy {name}: {text!r} " + ("cut to " + repr(shown) if was_cut else
                                                               f"past its recess ({x + width - self.ox:.0f} > {self.recess[name]})"))
            text, w = (shown, None) if one_line and was_cut else (text, w)
        super().text(cv, text, font, x, y, w, h, fmt, name, valign)


def window(elems, name, pos):
    """(the window placed at pos, as a list to draw; its body as the file has it)"""
    w = PP.find_window(elems, name)
    assert w is not None, name
    body = [(k, v) for k, v in w if not (k and k.lower() in ("position", "show_position"))]
    return [("containerWindowType", body + [("position", [("x", str(pos[0])), ("y", str(pos[1]))])])], w


def main():
    game_font_names()
    elems = V.load(GUI)
    vars_ = PP.gui_vars(GUI)
    cv = PP.backdrop(True)
    x0, y0 = 0, L.BELOW_MEDALLION
    fits = []
    # the fleet's header (the game's list slot is 165 tall), the tool bar under it, the task force under that
    body, w = window(elems, "fleet_view_header", (x0, y0))
    p = Fleet(w, recess=RECESS, ox=x0, hide=HEADER_HIDE, samples=HEADER, vars_=vars_)
    p.draw(cv, body, 0, 0, 1920, 1080)
    fits += p.fits
    body, w = window(elems, "tool_bar_window", (x0, y0 + 167))
    PP.Panel(vars_=vars_).draw(cv, body, 0, 0, 1920, 1080)
    ty = y0 + 213
    body, w = window(elems, "taskforce_view_entry", (x0, ty))
    p = Fleet(w, ox=x0, hide=TF_HIDE, samples=TASK_FORCE, vars_=vars_, frames={"insigna": 5})
    p.draw(cv, body, 0, 0, 1920, 1080)
    fits += p.fits
    # the ships' rows, 41 px apart, from the task force's ships_detailed (y 122)
    row = PP.find_window(elems, "ship_entry_detailed")
    rw = float(V.xy(V.sub(row, "size"))[0])
    rights = {}
    for k, v in row:
        if isinstance(v, list) and V.attrs(v).get("name") in RIGHT:
            rx = PP.Panel().posval(V.xy(V.sub(v, "position"))[0])
            rights[V.attrs(v)["name"]] = rx + (rw if V.attrs(v).get("orientation", "").upper() == "UPPER_RIGHT" else 0)
    for i, (name, kind, refit) in enumerate(SHIPS):
        ry = ty + 122 + i * 41
        body, _ = window(elems, "ship_entry_detailed", (x0, ry))
        shown = {"task_force_insignia"} | ({"btn_refit"} if refit else set())
        edge = min(rights[n] for n in shown)
        room = {}
        for n in ("ship_name", "ship_type"):
            a = boxes(row)[n]
            room[n] = min(int(a["maxwidth"]), edge - PP.Panel().posval(V.xy(V.sub(
                next(v for k, v in row if isinstance(v, list) and V.attrs(v).get("name") == n), "position"))[0]))
        p = Fleet(row, room=room, ox=x0, hide=ROW_HIDE | (set() if refit else {"btn_refit"}),
                  samples={"ship_name": name, "ship_type": kind}, vars_=vars_,
                  frames={"task_force_insignia": 5, "ship_level": 3})
        p.draw(cv, body, 0, 0, 1920, 1080)
        fits += p.fits
    y1 = ty + 122 + len(SHIPS) * 41 + 8
    out = Image.fromarray((np.clip(cv, 0, 1) * 255).astype(np.uint8)).crop((0, y0 - 8, 560, y1))
    out.resize((out.width * 2, out.height * 2), Image.NEAREST).save(OUT)
    for name, font, text, shown, room, was_cut, over in fits:
        print(f"  {name:22} {font:24} room {room!s:>5}  {'CUT ' if was_cut else ''}{'PAST ' if over else ''}{shown!r}")
    print("wrote", OUT, "| problems:", [q for q in V.problems if q.startswith("navy")] or "none")


if __name__ == "__main__":
    main()
