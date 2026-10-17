"""Previews of the selected armies', army groups', fleets' and operatives' badges on the map (mapview_art.py): each
badge window drawn from the game's .gui with its elements in place (sample names and numbers; the lists the game fills
in, traits and the divisions' counters, as faint outlines), over the map, as the game stacks them below the flag
medallion (with "Request Expeditionaries" and the selected air wings' rows under them), and beside it the game's own
look.

    python preview_mapviews.py   -> build/preview_mapviews.png (+ _vanilla.png), at 2x

They show the game's art, so they stay in the git-ignored build/ folder.
"""
import numpy as np
from PIL import Image

import layout as L
import preview_panels as PP
import validate_preview as V
from paths import BUILD, MOD, VANILLA

LEADER = {"title": "General", "leader_name": "Roland Cahun", "leader_skill": "4", "leader_stat_attack": "3",
          "leader_stat_defense": "2", "leader_stat_planning": "4", "leader_stat_logistics": "1"}
# (file, window, what the game shows of it, the sample texts, the frames it sets)
ARMY_GROUP_ONLY = {"army_group_bg", "group_div_count_bg", "group_leader_portrait_frame", "toggle_armies_divisions_button"}
ARMY_ONLY = {"army_bg", "div_count_bg", "leader_portrait_frame", "select_all_wings_button",
             "army_railway_gun_attachment_button"}
NOT_SHOWN = {"army_color_button", "pending_leader_icon", "leader_coming", "leader_enroute", "unit_leader_tutorial_glow",
             "click_to_assign", "leader_icon"}
BADGES = [
    ("unitview.gui", "army_badge_view", "an army",
     NOT_SHOWN | ARMY_GROUP_ONLY,
     dict(LEADER, group_name="1st Army", armies_count_box="", army_group_count_box="2", divisions_count="18/24"), {}),
    ("unitview.gui", "army_badge_view", "an army group",
     NOT_SHOWN | ARMY_ONLY | {"army_group_item_button", "army_group_count_box", "unassign_army_button"},
     dict(LEADER, title="Field Marshal", group_name="Army Group North", armies_count_box="3",
          divisions_count="54/72"), {}),
    ("naviesview.gui", "fleet_view_header", "a fleet",
     {"leader_icon", "leader_enroute", "click_to_assign", "fuel_efficiency_warning_icon", "air_base_btn",
      "btn_fleet_color"},
     {"fleet_name": "Home Fleet", "taskforce_count": "3/4", "leader_desc": "Admiral", "leader_name": "Aurèle Vasse",
      "skill_text": "3", "leader_stat_attack_text": "2", "leader_stat_defense_text": "3",
      "leader_stat_maneuvering_text": "4", "leader_stat_coordination_text": "1", "active_in_regions": "Active in Regions: 2",
      "home_base_name": "Rêverie"}, {}),
    ("operativeleader.gui", "operative_badge_view", "an operative", set(),
     {"operative_code_name": "Marten", "operative_skill_level": "2", "operative_name": "Isaure Delmas",
      "operative_title": "Operative"}, {}),
]
HIGHLIGHT_OFF = {"highlight"}       # the fleet's highlight: drawn on a second copy of the fleet header
# what the game moves for an army group (the badge's positionTypes)
GROUP_MOVES = {"select_all_button": (301, 77), "army_motorization_priority_button": (346, 77),
               "army_motorization_priority_button_overlay": (353, 77)}


def moved(body, moves):
    """the window's elements, those named in moves at another position"""
    out = []
    for k, v in body:
        if isinstance(v, list) and V.attrs(v).get("name") in moves:
            x, y = moves[V.attrs(v)["name"]]
            v = [(a, b) for a, b in v if not (a and a.lower() == "position")] + [("position", [("x", str(x)), ("y", str(y))])]
        out.append((k, v))
    return out


AIR_HIDE = {"create_new_wing_glow", "exile_flag_frame", "exile_flag", "ace_kia", "air_volunteer_icon", "carrier_capable_icon",
            "quick_wing_deployment", "sticky_mission_area_icon", "sticky_mission_area_btn", "training_will_stop_at_max_icon"}
AIR_ROWS = [("airbase_selection_item", {"base_name": "Rêverie Air Base", "capacity": "120/200", "permission_wings_count": "2"}, {}),
            ("airwing_selection_item", {"count": "100", "unit_name": "1st Fighter Wing", "mission_state": "Air Superiority"}, {}),
            ("airwing_selection_item", {"count": "50", "unit_name": "2nd Strike Wing", "mission_state": "No mission"},
             {"btn_bg": 1})]


def game_font_colours(names):
    """the game's colour for its fonts (core.gfx): the preview draws every game font white, but the typewriter fonts
    are black ink (the operative's code name)"""
    import re
    t = open(VANILLA + "interface/core.gfx", encoding="utf-8-sig", errors="ignore").read()
    for n in names:
        m = re.search(r'name\s*=\s*"%s"\s*fontfiles\s*=\s*\{[^}]*\}\s*color\s*=\s*0x([0-9a-fA-F]{8})' % n, t)
        if m and n in V.FONTS:
            c = int(m.group(1), 16)
            V.FONTS[n]["color"] = ((c >> 16) & 255, (c >> 8) & 255, c & 255)


def progress(cv, x, y, vanilla, part=.6):
    """the operative's status bar, which the preview's renderer leaves out (a progressbartype): its track, and the
    fill's middle third (the game's 51 px fill picture holds the bar in rows 17-34) over part of it"""
    bg = PP.texture("gfx/interface/operatives/operative_activity_progress_bar_bg.dds", vanilla)
    fill = PP.texture("gfx/interface/operatives/operative_activity_progress_bar.dds", True)
    V.paste(cv, bg, x, y)
    V.paste(cv, fill.crop((0, 17, int(fill.width * part), 34)), x, y)


def draw(vanilla):
    game_font_colours(["hoi4_typewriter16"])
    cv = PP.backdrop(not vanilla)
    x0, y = 1, L.BELOW_MEDALLION + 1
    spots = []
    for f, win, _what, hide, samples, frames in BADGES + [BADGES[2]]:
        path = (VANILLA if vanilla else MOD) + "interface/" + f
        w = PP.find_window(V.load(path), win)
        assert w is not None, (path, win)
        extra = set()
        if win == "fleet_view_header":
            extra = set() if any(s[0] == "fleet_view_header" for s in spots) else HIGHLIGHT_OFF
        p = PP.Panel(hide=set(hide) | extra, samples=samples, vanilla_only=vanilla, vars_=PP.gui_vars(path),
                     frames=frames)
        body = [(k, v) for k, v in w if not (k and k.lower() == "position")]
        if _what == "an army group":
            body = moved(body, GROUP_MOVES)
        p.draw(cv, [("containerWindowType", body + [("position", [("x", str(x0)), ("y", str(y))])])], 0, 0, 1920, 1080)
        if win == "operative_badge_view":
            # the game puts the operative's portrait (operative_leader_portrait_window_small) and status bar
            # (operative_status_window) at the badge's positionTypes
            for sub, (dx, dy) in (("operative_leader_portrait_window_small", (5, 27)), ("operative_status_window", (64, 78))):
                sw = PP.find_window(V.load(path), sub)
                sb = [(k, v) for k, v in sw if not (k and k.lower() == "position")]
                q = PP.Panel(hide={"leader_captured", "leader_enroute", "portrait_dismiss_btn", "activity_captured_alert",
                                   "activity_progressbar_disabled", "activity_progressbar_captured",
                                   "activity_progressbar_operation"},
                             samples={"status_text": "Building a network", "eta_text": "12 days"}, vanilla_only=vanilla)
                if sub == "operative_status_window":
                    progress(cv, x0 + dx + 2, y + dy + 2, vanilla)
                q.draw(cv, [("containerWindowType", sb + [("position", [("x", str(x0 + dx)), ("y", str(y + dy))])])],
                       0, 0, 1920, 1080)
        hh = int(float(V.xy(V.sub(w, "size"))[1]))
        spots.append((win, y))
        y += hh + 10
    # "Request Expeditionaries" (armies_view's expeditionary_force_button_container, shown), on its own here
    path = (VANILLA if vanilla else MOD) + "interface/unitview.gui"
    w = PP.find_window(V.load(path), "content")
    p = PP.Panel(vanilla_only=vanilla)
    p.draw(cv, [("containerWindowType", [(k, v) for k, v in w if not (k and k.lower() in ("position", "show_position"))]
                 + [("position", [("x", str(x0 + 20)), ("y", str(y))])])], 0, 0, 1920, 1080)
    y += 42
    # the selected air wings: an air base's row and two wings' rows under it (the second in the game's other frame)
    path = (VANILLA if vanilla else MOD) + "interface/airselectionview.gui"
    for win, samples, frames in AIR_ROWS:
        w = PP.find_window(V.load(path), win)
        p = PP.Panel(hide=AIR_HIDE, samples=samples, vanilla_only=vanilla, vars_=PP.gui_vars(path), frames=frames)
        p.draw(cv, [("containerWindowType", [(k, v) for k, v in w if not (k and k.lower() == "position")]
                     + [("position", [("x", str(x0)), ("y", str(y))])])], 0, 0, 1920, 1080)
        y += 48
    y += 10
    out = Image.fromarray((np.clip(cv, 0, 1) * 255).astype(np.uint8)).crop((0, L.BELOW_MEDALLION - 10, 560, y))
    out.resize((out.width * 2, out.height * 2), Image.NEAREST).save(
        BUILD + "preview_mapviews" + ("_vanilla" if vanilla else "") + ".png")


if __name__ == "__main__":
    draw(False)
    draw(True)
    print("wrote build/preview_mapviews.png (+ _vanilla)")
