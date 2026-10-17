"""Mockups: the commanders' trait trees (armytraittreewindow.gui, navytraittreewindow.gui, traittreewindow_common.gui).
The tree's places are the game's: the window (1340 x 778, centred), its column titles, the trait cells (166 x 39
plates, 40 px a row by each trait's gui_row in common/unit_leader/00_traits.txt), the left column's portrait, skill,
stats, active traits and preferred tactic."""
import os
import re

import deco as D

LOC = {}


def loc(key):
    if not LOC:
        p = os.path.join(D.DECO, "reference", "vanilla", "localisation", "english", "traits_l_english.yml")
        for m in re.finditer(r'^\s*([A-Za-z0-9_.]+):\d*\s*"(.*)"', open(p, encoding="utf-8-sig").read(), re.M):
            LOC[m.group(1)] = m.group(2)
    return LOC.get(key, key.replace("_", " ").title())


# a trait's line glyph (the game's trait pictures are its art)
TG = {
    "organizer": '<path d="M5 6h14M5 12h14M5 18h9"/><circle cx="18" cy="18" r="2"/>',
    "panzer_leader": '<path d="M3 15h18l-2 4H5z"/><path d="M6 15v-3h10v3M12 12V9h6"/>',
    "cavalry_leader": '<path d="M4 18c1-5 4-8 8-8l3-4 2 1-1 3c2 1 3 3 3 6"/><path d="M8 18v-3M16 18v-3"/>',
    "trait_engineer": '<path d="M4 20h16M6 20v-6h12v6M9 14V8l3-4 3 4v6"/>',
    "infantry_leader": '<path d="M5 15C5 9 8 5 13 5s7 4 7 10h-4c-.5-2-1.5-3-3-3h-2c-1.5 0-2.5 1-3 2.5z"/>',
    "naval_invader": '<path d="M3 16c3-2 5 2 8 0s5-2 8 0"/><path d="M6 12l2-6h8l2 6z"/>',
    "commando": '<path d="M12 3l3 6 6 1-4.5 4 1 6-5.5-3-5.5 3 1-6L3 10l6-1z"/>',
    "trickster": '<path d="M4 12c4-6 12-6 16 0-4 6-12 6-16 0z"/><circle cx="12" cy="12" r="2.5"/>',
    "skilled_staffer": '<path d="M6 4h12v16H6z"/><path d="M9 8h6M9 12h6M9 16h4"/>',
    "default": '<path d="M12 4l2.5 5 5.5.8-4 3.9.9 5.5L12 16.6l-4.9 2.6.9-5.5-4-3.9 5.5-.8z"/>',
    "terrain": '<path d="M2 19l7-12 4 6 3-4 6 10z"/>',
    "marshal": '<path d="M12 3l2 4.2 4.6.6-3.3 3.2.8 4.6L12 13.4l-4.1 2.2.8-4.6L5.4 7.8 10 7.2z"/><path d="M6 20h12M8 17.5h8"/>',
    "navy": '<circle cx="12" cy="5" r="2"/><path d="M12 7v13.5M8 10.5h8M4.5 13.5a7.5 7.5 0 0 0 15 0"/>',
    "air": '<path d="M12 3l1 2v5l7 6v1.5l-7-2v3l2 1.5v1H9v-1l2-1.5v-3l-7 2V16l7-6V5z"/>',
}


def glyph_for(t):
    if t in TG:
        return TG[t]
    for k in ("water", "fox", "rat", "ranger", "mountain", "hill", "urban", "winter", "adaptable"):
        if k in t:
            return TG["terrain"]
    return TG["default"]


def trait_node(x, y, key, state, glyph=None, w=166, h=39):
    """a trait's plate (the game's 166 x 39 pictures: disabled, pickable, picked), its picture (10, 4; 23 x 33) and
    name (40, 12; 123 wide)"""
    if state == "picked":
        rim, fill, col, gcol = D.GOLD, "linear-gradient(180deg,#2C665A,#163A33)", "#FBEAB4", "#FBEAB4"
    elif state == "pickable":
        rim, fill, col, gcol = "linear-gradient(180deg,#F1DC9C,#B48F44)", "linear-gradient(180deg,#24323A,#121B21)", D.CREAM, D.GILT
    else:
        rim, fill, col, gcol = "rgba(201,165,90,.35)", "linear-gradient(180deg,#141D22,#0B1014)", "rgba(232,223,200,.42)", "rgba(201,165,90,.4)"
    c = 6
    o = D.box(x, y, w, h, f"background:{rim};clip-path:{D.chamfer(c)}")
    o += D.box(x + 1, y + 1, w - 2, h - 2, f"background:{D.STRIPES},{fill};clip-path:{D.chamfer(c - .4)}")
    if state != "disabled":
        o += D.box(x + c + 2, y + 2, w - 2 * c - 4, 1, f"background:rgba(241,220,156,{.4 if state == 'picked' else .22})")
    # the picture well: a small octagon
    cx, cy = x + 21.5, y + h / 2
    o += D.layer(D.octagon_pts(cx, cy, 13), rim if state != "disabled" else "rgba(201,165,90,.3)")
    o += D.layer(D.octagon_pts(cx, cy, 11.8), "radial-gradient(circle at 50% 35%,#1A262E,#0B1014 80%)")
    o += D.svg(cx - 8, cy - 8, 16, 16, f'<g stroke="{gcol}" stroke-width="1.7">{glyph or glyph_for(key)}</g>', "0 0 24 24")
    name = loc(key)
    size = 13 if len(name) < 17 else 11.5
    o += D.text(x + 40, y + 2, name, size, col, w - 46, font="sans", weight=600, h=h - 4, valign=True, lh=1.05)
    if state == "pickable":
        o += D.diamond(x + w - 2, y + 2, 9, "#F1DC9C", "box-shadow:0 0 6px rgba(241,220,156,.8)")
    return o


def link(x0, y0, x1, y1, lit=True, dotted=False):
    """the tree's links (trait_tree_line_*): a gilt line, out from a plate's right edge and into the next one's left"""
    col = "rgba(227,199,126,.85)" if lit else "rgba(201,165,90,.32)"
    dash = ' stroke-dasharray="3 3"' if dotted else ""
    mx = (x0 + x1) / 2
    xs, ys = min(x0, x1) - 2, min(y0, y1) - 2
    w, h = abs(x1 - x0) + 4, abs(y1 - y0) + 4
    return D.svg(xs, ys, w, h, f'<path d="M{x0 - xs} {y0 - ys}H{mx - xs}V{y1 - ys}H{x1 - xs}" stroke="{col}" stroke-width="1.4"{dash}/>')


def left_column(name, title, portrait, skill, stats, sections, tactic, stat_names):
    o = ""
    # portrait (301, 255; 61 x 82) in a gilt frame, title and name (415, 259 / 277), the skill (391), the four stats
    o += D.box(298, 252, 67, 88, f"background:{D.GOLD}") + D.box(299, 253, 65, 86, "background:#0B1014")
    o += (D.portrait(portrait, 301, 255, 61, 82) if portrait else D.silhouette(301, 255, 61, 82))
    o += D.corners(298, 252, 67, 88, small=True)
    o += D.skill_diamond(391, 280, skill, 30)
    o += D.label(415, 259, title, 10.5, D.LABEL, 150, track=.2)
    o += D.text(415, 274, name, 18 if len(name) < 15 else 15, D.CREAM, 160, font="fed", track=.03)
    for i, ((ic, v), nm) in enumerate(zip(stats, stat_names)):
        cx = 444 + i * 33
        o += D.layer(D.octagon_pts(cx, 309, 12.5), D.GOLD) + D.layer(D.octagon_pts(cx, 309, 11.3), "#0E1519")
        o += D.svg(cx - 8, 301, 16, 16, f'<g stroke="#E3C77E" stroke-width="1.6">{ic}</g>', "0 0 24 24")
        o += D.value(cx - 15, 325, str(v), 13, D.CREAM, 30, "center")
    # experience (374, 338)
    o += D.progress(374, 345, 190, 5, .42)
    o += D.label(374, 353, "Experience 420 / 1000", 8.5, D.LABEL, 190, track=.1)
    # the active traits (310, 365): section titles on a separator (272 x 5), the traits (active_trait: 200 x 27)
    y = 372
    for head, items in sections:
        o += D.fade_rule(296, y + 9, 568, a=.7) + D.box(380, y + 1, 112, 17, "background:#0E1519")
        o += D.label(290, y + 5, head, 11, D.GILT, 284, "center", track=.22)
        y += 26
        for key, buff, new in items:
            if key is None:
                o += D.box(312, y + 2, 26, 26, f"background:{D.GOLD};clip-path:{D.chamfer(5)}")
                o += D.box(313, y + 3, 24, 24, f"background:#0E1519;clip-path:{D.chamfer(4.6)}")
                o += D.svg(317, y + 7, 16, 16, '<path d="M8 2v12M2 8h12" stroke="#F1DC9C" stroke-width="2"/>')
                o += D.text(345, y + 9, "Pick Trait", 14, "#F1DC9C", 200, weight=600)
                y += 36
                continue
            o += D.layer(D.octagon_pts(324, y + 13, 12), D.GOLD) + D.layer(D.octagon_pts(324, y + 13, 10.8), "#0E1519")
            o += D.svg(316, y + 5, 16, 16, f'<g stroke="#E3C77E" stroke-width="1.7">{glyph_for(key)}</g>', "0 0 24 24")
            o += D.text(345, y + 2, loc(key), 15, D.CREAM, 220, font="fed", track=.02)
            o += D.text(346, y + 19, buff, 11.5, D.LABEL, 225)
            y += 40
        y += 6
    # preferred tactic (300, 865; 270 x 93): header, the tactic's button (313, 890; 101 x 60), its four effects (the
    # navy's window has none)
    if not tactic:
        return o
    o += D.well(300, 865, 270, 93)
    o += D.label(310, 872, "Preferred Tactic", 10.5, D.GILT, 250, "center", track=.2)
    o += D.box(313, 890, 101, 60, f"background:{D.GOLD};clip-path:{D.chamfer(6)}")
    o += D.box(314, 891, 99, 58, f"background:radial-gradient(circle at 50% 40%,#1C2830,#0B1014 80%);clip-path:{D.chamfer(5.6)}")
    o += D.sunburst(363.5, 920, 30, .16)
    o += D.ico("swords", 351, 908, 25, "#F1DC9C", 1.5)
    o += D.text(420, 893, tactic, 14, D.CREAM, 145, font="fed")
    for i, (lab, v, col) in enumerate((("Attack", "+10%", D.POS), ("Width", "+5%", D.CREAM), ("Defence", "-5%", D.NEG), ("Speed", "+0%", D.CREAM))):
        o += D.label(420 + (i % 2) * 74, 914 + (i // 2) * 20, lab, 8.5, D.LABEL, 44, track=.06) + D.value(462 + (i % 2) * 74, 913 + (i // 2) * 20, v, 11, col, 28, "right")
    return o


def frame_and_header(tab_lit=0):
    X, Y, WW, HH = 290, 190, 1340, 778
    o = D.window(X, Y, WW, HH)
    # header band (title at 325, 197) with the tabs (805 and 1061, y 204; 258 x 42) and close (1586, 201)
    o += D.band(X + 6, Y + 6, WW - 12, 48) + D.rule(X + 6, Y + 54, X + WW - 6)
    o += D.title(330, 205, "Leader Details", 24)
    o += D.tab(809, 205, 250, 38, "Traits", tab_lit == 0, 14) + D.tab(1065, 205, 250, 38, "Officer Corps Roles", tab_lit == 1, 14)
    o += D.close(1586, 201, 32)
    # the left column's plate and the tree's field
    o += D.band(X + 6, Y + 58, 280, HH - 64, "linear-gradient(180deg,#18232A,#10181D)")
    o += D.vrule(X + 286, Y + 58, Y + HH - 6, "rgba(201,165,90,.6)")
    return o


def army_trait_tree():
    o = D.backdrop()
    o += frame_and_header()
    stats = [(D.ICONS["swords"], 4), (D.ICONS["shield"], 2), ('<path d="M5 4h14v16H5z"/><path d="M8 9h8M8 13h8M8 17h5"/>', 3),
             (D.ICONS["logistics"], 3)]
    o += left_column("Serelle Cahun", "General", "serelle_cahun", 4, stats,
                     [("Background", [("armor_officer", "Armoured divisions: +5% organisation", False)]),
                      ("Traits", [("panzer_leader", "Armour: +10% speed", False), ("combined_arms_expert", "Mixed divisions: +5% attack", False), (None, "", False)])],
                     "Blitz", ["Attack", "Defence", "Planning", "Logistics"])
    # the column titles (centred on 670 / 878 / 1090, y 260) and the terrain column's (1415)
    for cx, t in ((670, "Earned Traits"), (878, "General Traits"), (1090, "Field Marshal Traits"), (1415, "Terrain Traits")):
        o += D.label(cx - 150, 266, t, 11, D.GILT, 300, "center", track=.2)
        o += D.fade_rule(cx - 95, 285, cx + 95, a=.6)
    o += D.vrule(1222, 262, 950, "rgba(201,165,90,.35)")
    o += D.well(1229, 296, 396, 650, fill="linear-gradient(180deg,#0D1418,#090D10)", rim="rgba(201,165,90,.3)")
    COL = {0: 587, 1: 795, 2: 1007}
    Y0 = 302
    basic = {0: "organizer", 1: "panzer_leader", 3: "cavalry_leader", 4: "trait_engineer", 6: "infantry_leader", 8: "naval_invader",
             10: "commando", 13: "trickster", 15: "skilled_staffer"}
    assign = {1: "panzer_expert", 2: "combined_arms_expert", 3: "cavalry_expert", 4: "fortress_buster", 5: "scavenger", 6: "infantry_expert",
              7: "ambusher", 8: "invader_ii", 9: "naval_liason", 10: "skirmisher", 11: "paratrooper", 12: "camouflage_expert",
              13: "expert_improviser", 14: "guerilla_fighter"}
    parent = {1: 1, 2: 1, 3: 3, 4: 4, 5: 4, 6: 6, 7: 6, 8: 8, 9: 8, 10: 10, 11: 10, 12: 13, 13: 13, 14: 13}
    marshal = {0: "logistics_wizard", 1: "fast_planner", 2: "thorough_planner", 3: "unyielding_defender", 4: "aggressive_assaulter",
               5: "offensive_doctrine", 6: "defensive_doctrine", 7: "organisational_leader", 8: "inspirational_leader", 15: "expert_delegator"}
    # links first, so the plates lie over them
    for r, pr in parent.items():
        lit = pr == 1
        o += link(COL[0] + 166, Y0 + pr * 40 + 19.5, COL[1], Y0 + r * 40 + 19.5, lit, dotted=not lit)
    for r, k in basic.items():
        o += trait_node(COL[0], Y0 + r * 40, k, "picked" if k == "panzer_leader" else "disabled")
    for r, k in assign.items():
        st = "picked" if k == "combined_arms_expert" else ("pickable" if k == "panzer_expert" else "disabled")
        o += trait_node(COL[1], Y0 + r * 40, k, st)
    for r, k in marshal.items():
        o += trait_node(COL[2], Y0 + r * 40, k, "disabled", TG["marshal"])
    # terrain: the basic terrain traits (rows 0-7) and the two assignable ones (adaptable r3, winter expert r7)
    terr = {0: "desert_fox", 1: "swamp_fox", 2: "hill_fighter", 3: "trait_mountaineer", 4: "urban_assault_specialist", 5: "ranger",
            6: "jungle_rat", 7: "winter_specialist"}
    for r in range(8):
        o += link(1240 + 166, Y0 + r * 40 + 19.5, 1440, Y0 + 3 * 40 + 19.5, False, True) if r in (0, 1, 2, 3, 4, 5, 6) else ""
    o += link(1240 + 166, Y0 + 7 * 40 + 19.5, 1440, Y0 + 7 * 40 + 19.5, False, True)
    for r, k in terr.items():
        o += trait_node(1240, Y0 + r * 40, k, "picked" if k == "hill_fighter" else "disabled")
    o += trait_node(1440, Y0 + 3 * 40, "adaptable", "disabled", w=166)
    o += trait_node(1440, Y0 + 7 * 40, "winter_expert", "disabled", w=166)
    return o


def navy_trait_tree():
    o = D.backdrop()
    o += frame_and_header()
    stats = [(D.ICONS["swords"], 3), (D.ICONS["shield"], 4), ('<path d="M4 16c3-6 13-6 16 0"/><path d="M16 9l4 7-7 1"/>', 4),
             (D.ICONS["faction"], 5)]
    o += left_column("Odile de Lys", "Admiral", None, 4, stats,
                     [("Background", [("navy_career_officer", "Naval career: +5% organisation", False)]),
                      ("Traits", [("air_controller", "Carrier air wings: +10% sortie efficiency", False),
                                  ("flight_deck_manager", "Carrier capacity: +1 air wing", False), (None, "", False)])],
                     None, ["Attack", "Defence", "Manoeuvring", "Coordination"])
    for cx, t in ((685, "Earned Traits"), (897, "Admiral Traits"), (1425, "Terrain Traits")):
        o += D.label(cx - 150, 266, t, 11, D.GILT, 300, "center", track=.2)
        o += D.fade_rule(cx - 95, 285, cx + 95, a=.6)
    o += D.vrule(1222, 262, 950, "rgba(201,165,90,.35)")
    o += D.well(1229, 296, 396, 650, fill="linear-gradient(180deg,#0D1418,#090D10)", rim="rgba(201,165,90,.3)")
    COL = {0: 587, 1: 795, 2: 1007}
    Y0 = 302
    col0 = {0: "blockade_runner", 2: "seawolf", 4: "spotter", 5: "fleet_protector", 6: "superior_tactician", 8: "air_controller", 10: "ironside"}
    col1 = {0: "concealment_expert", 1: "lone_wolf", 2: "silent_hunter", 3: "lancer", 4: "search_pattern_expert", 5: "destroyer_leader",
            6: "cruiser_captain", 7: "mine_craft", 8: "flight_deck_manager", 9: "ground_pounder", 10: "big_guns_expert", 11: "safety_first"}
    col2 = {0: "smoke_screen_expert", 2: "torpedo_expert", 3: "loading_drill_master", 5: "hunter_killer", 6: "fly_swatter",
            7: "fighter_director", 8: "dive_bomber", 9: "torpedo_bomber", 10: "marksman", 11: "crisis_magician"}
    p1 = {0: 0, 1: 0, 2: 2, 3: 2, 4: 4, 5: 5, 6: 6, 7: 6, 8: 8, 9: 8, 10: 10, 11: 10}
    p2 = {0: 0, 2: 2, 3: 3, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11}
    for r, pr in p1.items():
        o += link(COL[0] + 166, Y0 + pr * 40 + 19.5, COL[1], Y0 + r * 40 + 19.5, pr == 8, dotted=pr != 8)
    for r, pr in p2.items():
        o += link(COL[1] + 166, Y0 + pr * 40 + 19.5, COL[2], Y0 + r * 40 + 19.5, pr == 8, dotted=pr != 8)
    for r, k in col0.items():
        o += trait_node(COL[0], Y0 + r * 40, k, "picked" if k == "air_controller" else "disabled", TG["air"] if k == "air_controller" else TG["navy"])
    for r, k in col1.items():
        st = "picked" if k == "flight_deck_manager" else ("pickable" if k == "ground_pounder" else "disabled")
        o += trait_node(COL[1], Y0 + r * 40, k, st, TG["navy"])
    for r, k in col2.items():
        st = "pickable" if k in ("fighter_director", "dive_bomber") else "disabled"
        o += trait_node(COL[2], Y0 + r * 40, k, st, TG["air"] if r in (6, 7, 8, 9) else TG["navy"])
    for r, k in {0: "arctic_water_expert", 1: "inshore_fighter", 2: "blue_water_expert", 3: "green_water_expert"}.items():
        o += trait_node(1340, Y0 + r * 40, k, "picked" if k == "blue_water_expert" else "disabled", TG["navy"])
    return o
