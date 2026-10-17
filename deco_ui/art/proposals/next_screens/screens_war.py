"""Mockups: the war overview (waroverview.gui), the peace conference (peaceconferencewindow.gui), operations
(operationoverview.gui), raids (military_raids/), the end of game and the diplomatic message icons (menubar.gui).
The boxes are the game's (guilayout.py); where a window slides in, it is drawn where it shows."""
import deco as D

ASSOC = [("ROU", "Rouental", True), ("HLR", "Hollier", False), ("EVR", "Evriches", False), ("SGV", "Selgrave", False),
         ("LST", "Lustiana", False), ("SGN", "Seigne", False)]


def head_icon(cx, cy, glyph, col=D.GILT):
    """a list header's icon (the game's 35 x 29 pictures): a line glyph in a small lacquer chip"""
    return (D.box(cx - 15, cy - 13, 30, 26, f"background:rgba(201,165,90,.6);clip-path:{D.chamfer(5)}")
            + D.box(cx - 14, cy - 12, 28, 24, f"background:linear-gradient(180deg,#1C2830,#0E1519);clip-path:{D.chamfer(4.6)}")
            + D.svg(cx - 9, cy - 9, 18, 18, f'<g stroke="{col}" stroke-width="1.6">{glyph}</g>', "0 0 24 24"))


G_WARGOAL = '<path d="M5 20V4M5 5h12l-3 4 3 4H5"/>'
G_SURRENDER = '<path d="M6 20V4M6 5h11v8H6"/><path d="M9 8h5" opacity=".6"/>'
G_SCORE = '<path d="M12 3l2.6 5.3 5.8.8-4.2 4.1 1 5.8-5.2-2.7-5.2 2.7 1-5.8L3.6 9.1l5.8-.8z"/>'
G_DIV = D.ICONS["deploy"]
G_IC = D.ICONS["factory"]
G_CAS = '<path d="M12 3v18M7 8h10"/>'
G_PEOPLE = D.ICONS["manpower"]


def war_row(x, y, tag, name, ws, div, ic, cas, surrender=0.0, major=False, wargoal=False, callable_=False):
    """war_ally_entry (530 x 41): flag (9, 3; 41 x 26) in its frame, name (56, 0), surrender progress (55, 22; 142 x 6),
    call (220, 2) or war goal (237, 3), war score (269), divisions (317), factories (393), casualties (466)"""
    o = D.box(x, y, 530, 39, f"background:{D.STRIPES},linear-gradient(180deg,#18232A,#10181D);box-shadow:inset 0 0 0 1px rgba(201,165,90,.28)")
    o += D.flag(tag, x + 9, y + 6, 41, 26)
    if major:
        o += D.diamond(x + 47, y + 7, 7, "#F1DC9C", "box-shadow:0 0 0 1px #0B1014")
    o += D.text(x + 58, y + 6, name, 14, D.CREAM, 160, weight=600)
    o += D.box(x + 58, y + 25, 140, 4, "background:#0A0F12;box-shadow:0 0 0 1px rgba(201,165,90,.4)")
    o += D.box(x + 58, y + 25, 140 * surrender, 4, "background:linear-gradient(90deg,#A9493A,#E8877A)")
    if callable_:
        o += D.button(x + 220, y + 6, 72, 26, "Call", size=10)
        ws = ""
    if wargoal:
        o += D.svg(x + 242, y + 10, 18, 18, f'<g stroke="#E7B75A" stroke-width="1.7">{G_WARGOAL}</g>', "0 0 24 24")
    o += D.value(x + 269, y + 13, ws, 13, D.CREAM, 50, "center")
    o += D.value(x + 317, y + 13, div, 13, D.CREAM, 80, "center")
    o += D.value(x + 393, y + 13, ic, 13, D.CREAM, 80, "center")
    o += D.value(x + 466, y + 13, cas, 13, D.CREAM2, 60, "center", weight=600)
    return o


def faction_row(x, y, name, div, ic, cas, side):
    o = D.bar(x - 2, y, 534, 40, c=6)
    o += D.box(x, y + 38, 530, 2, f"background:{side['line']}")
    o += D.svg(x + 11, y + 13, 14, 14, '<path d="M2 4l5 6 5-6" stroke="#E3C77E" stroke-width="1.6"/>')
    o += D.text(x + 34, y + 12, name, 15, D.GILT, 220, font="fed", track=.06, caps=True)
    o += D.value(x + 317, y + 12, div, 14, D.CREAM, 80, "center")
    o += D.value(x + 393, y + 12, ic, 14, D.CREAM, 80, "center")
    o += D.value(x + 466, y + 12, cas, 14, D.CREAM2, 60, "center")
    return o


def war_overview():
    o = D.backdrop()
    X, Y, WW, HH = 377, 243, 1167, 800
    # the war tabs over the window (waroverview_wars_box, centre-up, 47 x 51 each)
    for i, (lit, g) in enumerate(((True, "swords"), (False, "shield"))):
        tx = 936 - 24 + (i - .5) * 52
        o += D.box(tx, 196, 47, 51, f"background:{D.GOLD if lit else 'rgba(201,165,90,.5)'};clip-path:polygon(8px 0,calc(100% - 8px) 0,100% 8px,100% 100%,0 100%,0 8px)")
        o += D.box(tx + 1, 197, 45, 50, f"background:{D.LIT_FILL if lit else D.DIM_FILL};clip-path:polygon(7.6px 0,calc(100% - 7.6px) 0,100% 7.6px,100% 100%,0 100%,0 7.6px)")
        o += D.ico(g, tx + 11, 207, 24, "#FBEAB4" if lit else D.GILT, 1.5)
    o += D.window(X, Y, WW, HH)
    o += D.band(X + 6, Y + 6, WW - 12, 50) + D.rule(X + 6, Y + 56, X + WW - 6)
    o += D.title(784, 262, "The War of the Vale", 24, w=350, align="center")
    o += D.diamond(760, 274, 6) + D.diamond(1160, 274, 6)
    o += D.close(1500, 260, 32)
    # war score: the bar (671, 314; 579 x 26) in its frame (664, 309; 591 x 38); each side's fielded men and losses
    o += D.box(664, 309, 591, 38, f"background:{D.GOLD};clip-path:{D.chamfer(8)}")
    o += D.box(665, 310, 589, 36, f"background:#0B1014;clip-path:{D.chamfer(7.6)}")
    o += D.box(671, 315, 579, 26, "background:linear-gradient(180deg,#40698B,#203A52)")
    o += D.box(671, 315, 579 * .64, 26, "background:linear-gradient(180deg,#A9493A,#5A231C)")
    o += D.box(671, 315, 579, 26, "background:repeating-linear-gradient(90deg,rgba(255,255,255,.07) 0 1px,transparent 1px 12px)")
    o += D.diamond(671 + 579 * .64, 328, 12, "#F1DC9C", "box-shadow:0 0 0 2px #0B1014")
    o += D.value(681, 320, "64%", 15, "#F7D9D2", 60) + D.value(1180, 320, "36%", 15, "#D6E6F2", 60, "right")
    for x0, men, loss, col in ((397, "Fielded: 1.24M", "Losses: 18,420", D.OX), (1277, "Fielded: 0.81M", "Losses: 41,960", D.SL)):
        o += D.value(x0, 313, men, 14, D.CREAM, 250, "center", weight=600)
        o += D.value(x0, 332, loss, 13, col["pale"], 250, "center", weight=500)
    # filters (751 / 897 / 1042, y 356; 140 x 29)
    for i, (s, lit) in enumerate((("Minors", True), ("Capitulated", False), ("Callable", False))):
        x = 751 + i * 146 - (5 if i == 2 else 0)
        o += (D.lit_bar(x, 356, 140, 29, 4) if lit else D.bar(x, 356, 140, 29, c=4, shine=.15))
        o += D.text(x, 357, s, 12, "#FBEAB4" if lit else D.LABEL, 140, "center", weight=600, track=.12, caps=True, h=28, valign=True)
    # each side's header icons and list (attacker 402, defender 970; rows of 42 from y 435)
    for (sx, side, xs) in ((402, D.OX, (401, 557, 621, 680, 739, 817, 881)), (970, D.SL, (969, 1122, 1192, 1245, 1307, 1382, 1448))):
        o += D.band(sx - 4, 396, 563, 38) + D.box(sx - 4, 432, 563, 2, f"background:{side['line']}")
        glyphs = (G_PEOPLE, G_SURRENDER, G_WARGOAL, G_SCORE, G_DIV, G_IC, G_CAS)
        for gx, gl in zip(xs, glyphs):
            o += head_icon(gx + 17, 415, gl, side["pale"] if gl is G_PEOPLE else D.GILT)
    y = 438
    o += faction_row(402, y, "The Association", "214", "142", "18,420", D.OX)
    for i, (tag, name, major) in enumerate(ASSOC):
        o += war_row(402, y + 44 + i * 42, tag, name, ["+412", "+96", "+40", "+22", "+18", "+4"][i], ["124", "28", "14", "18", "16", "14"][i],
                     ["72", "21", "11", "14", "13", "11"][i], ["11,300", "3,120", "1,410", "1,090", "980", "520"][i], major=major,
                     wargoal=(i == 0), surrender=0.02 * i)
    o += war_row(402, y + 44 + 6 * 42 + 10, "GDN", "Guedelon", "—", "12", "9", "—", callable_=True)
    o += D.label(402, y + 44 + 7 * 42 + 26, "Not in the war", 10, D.LABEL, 300, track=.16)
    o += war_row(402, y + 44 + 7 * 42 + 44, "LZC", "Lanzerac", "—", "10", "8", "—", callable_=True)
    o += faction_row(970, y, "Cardonia", "88", "76", "41,960", D.SL)
    for i, (tag, name, ws, dv, ic, cas, sur, maj) in enumerate((("CRD", "Cardonia", "-488", "72", "64", "39,800", .44, True),
                                                               ("THD", "Thorian Dynamics", "-24", "16", "12", "2,160", .12, False))):
        o += war_row(970, y + 44 + i * 42, tag, name, ws, dv, ic, cas, surrender=sur, major=maj, wargoal=(i == 0))
    return o


# ---------------------------------------------------------------- the peace conference
def peace_conference():
    o = D.backdrop(top=False)
    # Cardonia's states on the map: those Rouental demands hatched in its colours, the cost over each (peace_cost_mapicon)
    for (x, y, cost, taker) in ((640, 250, "42", "ROU"), (820, 268, "38", "ROU"), (990, 316, "26", "HLR"), (560, 160, "31", None),
                               (480, 300, "57", "ROU"), (1140, 250, "22", None), (1228, 176, "24", None)):
        o += D.box(x - 60, y - 40, 120, 80, "border-radius:46%;background:repeating-linear-gradient(135deg,rgba(54,106,64,.55) 0 4px,rgba(54,106,64,0) 4px 9px)" if taker == "ROU"
                   else ("border-radius:46%;background:repeating-linear-gradient(135deg,rgba(185,53,52,.5) 0 4px,rgba(185,53,52,0) 4px 9px)" if taker else ""))
        if taker:
            o += D.flag(taker, x - 13, y - 34, 26, 16)
        o += (D.box(x - 30, y - 12, 60, 22, f"background:rgba(11,16,20,.9);clip-path:{D.chamfer(4)};box-shadow:inset 0 0 0 1px rgba(201,165,90,.7)")
              + D.value(x - 30, y - 7, cost, 14, "#F1DC9C", 60, "center"))
    # the top bar (tiled_peace_upper_bar, 1978 x 96 at -20, -3): title (30, 32), the art (centre-up, 580 x 100), done
    o += D.box(0, 0, 1920, 93, f"background:{D.STRIPES},linear-gradient(180deg,#1A252C,#0D1418);box-shadow:0 8px 20px rgba(0,0,0,.5)")
    o += D.rule(0, 90, 1920, D.RULE) + D.rule(0, 93, 1920, "rgba(201,165,90,.45)")
    o += D.title(30, 34, "Peace Conference", 26)
    # the top art: Valsora's laurel and a gilt fan, the winner's side
    o += D.layer([(674, 0), (1254, 0), (1214, 96), (714, 96)], D.GOLD)
    o += D.layer([(676, 0), (1252, 0), (1213, 94), (715, 94)], f"{D.STRIPES},linear-gradient(180deg,#1E2B33,#0E1519)")
    o += D.sunburst(964, 96, 90, .2)
    o += D.speed_lines(730, 870, 48, False) + D.speed_lines(1058, 1198, 48, True)
    o += D.medallion(964, 44, 30, "officer", icon_size=30)
    o += D.title(674, 80, "Victors' Conference", 11, w=580, align="center", track=.3)
    o += D.button(1638, 37, 261, 34, "Confirm and Exit", "gold", 12)
    # the current turn (515 x 65, centre-up at 85) and the bid phase (400 x 40 under it)
    o += D.window(702, 100, 515, 60, "single", "small")
    o += D.flag("ROU", 716, 113, 41, 26)
    o += D.text(764, 108, "Rouental", 18, D.CREAM, 200, font="fed", track=.04)
    o += D.ico("faction", 806, 132, 18, "#E7B75A", 1.4) + D.value(828, 135, "World tension 38%", 12, D.CREAM2, 150)
    o += D.label(1018, 112, "Score", 9.5, D.LABEL, 140, track=.16) + D.value(1018, 126, "214 / 860", 17, "#F1DC9C", 180)
    o += D.window(760, 160, 400, 36, "thin", None)
    o += D.text(780, 172, "Conference turn: 3", 13, D.CREAM2, 200) + D.text(1000, 172, "Score this turn: 74", 13, D.CREAM2, 150)
    o += D.text(1116, 172, "2 left", 13, D.LABEL, 50)
    # the left panel (340 wide, shown at x 0): make demands, the demands' buttons, the available actions
    o += D.window(0, 87, 340, 993)
    o += D.band(10, 97, 319, 46) + D.rule(10, 143, 329) + D.title(10, 109, "Make Demands", 19, w=319, align="center")
    o += D.well(5, 146, 330, 72)
    o += D.text(17, 156, "Select the Demands you want to make.", 13, D.CREAM2, 300)
    o += D.text(17, 176, "Current action:", 13, D.CREAM2, 120) + D.text(113, 176, "Take States", 13, "#E7B75A", 160, weight=700)
    o += D.label(14, 228, "Demands:", 10, D.GILT, 200, track=.18)
    acts = [("Take", '<path d="M4 20V8l8-4 8 4v12z"/><path d="M9 20v-6h6v6"/>'), ("Liberate", '<path d="M6 21V3M6 4h11l-3 4 3 4H6"/>'),
            ("Puppet", '<path d="M12 3v6M6 9h12M8 9l-2 6M16 9l2 6M9 21l3-6 3 6"/>'), ("Govt.", D.ICONS["gov"]),
            ("Navy", D.ICONS["navy"])]
    for i, (n, g) in enumerate(acts):
        lit = i == 0
        x = 3 + i * 46
        o += D.box(x, 244, 44, 44, f"background:{D.GOLD if lit else 'rgba(201,165,90,.6)'};clip-path:{D.chamfer(7)}")
        o += D.box(x + 1, 245, 42, 42, f"background:{D.LIT_FILL if lit else D.BAR_FILL};clip-path:{D.chamfer(6.6)}")
        o += D.svg(x + 11, 255, 22, 22, f'<g stroke="{"#FBEAB4" if lit else D.GILT}" stroke-width="1.5">{g}</g>', "0 0 24 24")
    o += D.label(14, 296, "Additional Demands:", 10, D.GILT, 220, track=.18)
    for i, g in enumerate(('<path d="M4 12h16M12 4v16" stroke-dasharray="2 2"/><circle cx="12" cy="12" r="7"/>', D.ICONS["market"], D.ICONS["factory"],
                           '<path d="M3 20V11l5 3v-3l5 3v-3l5 3V4.5h3v16z"/><path d="M4 4l16 16"/>')):
        x = 3 + i * 46
        o += D.box(x, 312, 44, 44, f"background:rgba(201,165,90,.6);clip-path:{D.chamfer(7)}")
        o += D.box(x + 1, 313, 42, 42, f"background:{D.BAR_FILL};clip-path:{D.chamfer(6.6)}")
        o += D.svg(x + 11, 323, 22, 22, f'<g stroke="{D.GILT}" stroke-width="1.5">{g}</g>', "0 0 24 24")
    # the available actions (340 x 633 from y 370): one aggregated header per loser (342 x 54) and its states (29 tall)
    o += D.well(2, 370, 336, 626)
    o += D.box(4, 374, 332, 52, f"background:{D.STRIPES},linear-gradient(180deg,#1E2A31,#121B21);box-shadow:inset 0 0 0 1px rgba(201,165,90,.45)")
    o += D.flag("CRD", 18, 382, 41, 26) + D.text(72, 381, "Cardonia", 15, D.CREAM, 190, font="fed", track=.04)
    for i, (g, n, col) in enumerate(((G_SCORE, "27", D.GILT), ('<path d="M4 20L20 4M4 4l16 16"/>', "3", "#E8877A"), (G_WARGOAL, "1", "#E7B75A"))):
        o += D.svg(72 + i * 60, 402, 16, 16, f'<g stroke="{col}" stroke-width="1.7">{g}</g>', "0 0 24 24") + D.value(92 + i * 60, 404, n, 13, D.CREAM, 30)
    o += D.svg(270, 405, 14, 14, '<path d="M2 4l5 6 5-6" stroke="#E3C77E" stroke-width="1.6"/>')
    states = [("57", "Greater Cardia", True, True), ("42", "Polkria", False, False), ("38", "Mesina", False, False), ("31", "Coreilia", True, False),
              ("26", "Llainfair", False, False), ("24", "Lesser Cardia", False, False), ("22", "Great North", False, False), ("19", "Lestershire", False, False),
              ("17", "Lavia", False, False), ("15", "North Whitemore", False, False), ("14", "North Pine", False, False)]
    for i, (sc, nm, cont, wg) in enumerate(states):
        y = 430 + i * 29
        sel = i == 1
        o += D.box(4, y, 332, 27, f"background:{'linear-gradient(90deg,rgba(46,110,96,.6),rgba(46,110,96,.2))' if sel else 'rgba(255,255,255,.02)'};"
                                  f"box-shadow:inset 0 -1px 0 rgba(201,165,90,.15){',inset 2px 0 0 #F1DC9C' if sel else ''}")
        o += D.flag("CRD", 18, y + 5, 26, 17, frame=False)
        o += D.value(50, y + 8, sc, 14, "#F1DC9C", 50) + D.text(110, y + 8, nm, 14, D.CREAM, 140)
        if cont:
            o += D.svg(253, y + 6, 15, 15, '<path d="M4 20L20 4M4 4l16 16" stroke="#E8877A" stroke-width="2"/>', "0 0 24 24")
        if wg:
            o += D.svg(272, y + 6, 15, 15, f'<g stroke="#E7B75A" stroke-width="1.8">{G_WARGOAL}</g>', "0 0 24 24")
    # the reset plate (341 x 83, lower left) and its button
    o += D.band(3, 996, 334, 80) + D.rule(3, 996, 337) + D.button(98, 1020, 148, 36, "Reset", size=12)
    # the right panel (340 wide, shown at x 1580): the taker tabs, current demands, the winners' bids
    RX = 1580
    o += D.window(RX, 87, 340, 993)
    o += D.lit_bar(RX + 25, 108, 140, 29, 4) + D.text(RX + 25, 109, "Victors", 12, "#FBEAB4", 140, "center", weight=600, track=.12, caps=True, h=28, valign=True)
    o += D.bar(RX + 170, 108, 140, 29, c=4, shine=.15) + D.text(RX + 170, 109, "Beneficiaries", 12, D.LABEL, 140, "center", weight=600, track=.12, caps=True, h=28, valign=True)
    o += D.band(RX + 10, 147, 319, 46) + D.rule(RX + 10, 193, RX + 329) + D.title(RX + 10, 160, "Current Demands", 19, w=319, align="center")
    o += D.well(RX + 4, 198, 332, 794)
    yy = 204
    for tag, name, score, bids, ratio, rows in (("ROU", "Rouental", "214", "4", "61%", [("42", "Polkria"), ("38", "Mesina"), ("57", "Greater Cardia"), ("31", "Coreilia")]),
                                                 ("HLR", "Hollier", "96", "1", "27%", [("26", "Llainfair")]),
                                                 ("EVR", "Evriches", "40", "0", "12%", [])):
        o += D.box(RX + 8, yy, 324, 80, f"background:{D.STRIPES},linear-gradient(180deg,#1E2A31,#121B21);box-shadow:inset 0 0 0 1px rgba(201,165,90,.45)")
        o += D.flag(tag, RX + 15, yy + 16, 41, 26)
        o += D.text(RX + 66, yy + 19, name, 16, D.CREAM, 140, font="fed", track=.04)
        o += D.value(RX + 258, yy + 19, score, 15, "#F1DC9C", 60, "right")
        for i, (lab, v) in enumerate((("Bids", bids), ("Contested", "1" if tag == "ROU" else "0"), ("Share", ratio))):
            o += D.label(RX + 66 + i * 70, yy + 50, lab, 8.5, D.LABEL, 60, track=.1) + D.value(RX + 66 + i * 70, yy + 61, v, 12, D.CREAM, 60)
        yy += 84
        for cost, st in rows:
            o += D.box(RX + 18, yy, 312, 27, "background:rgba(255,255,255,.02);box-shadow:inset 0 -1px 0 rgba(201,165,90,.15)")
            o += D.flag("CRD", RX + 30, yy + 5, 26, 17, frame=False)
            o += D.value(RX + 62, yy + 8, cost, 13, "#F1DC9C", 50) + D.text(RX + 116, yy + 8, st, 13, D.CREAM, 150)
            yy += 29
        yy += 8
    # submit (the plate 341 x 83 left of the right panel, lower left; the button 288 x 36)
    o += D.band(1243, 996, 337, 80) + D.rule(1243, 996, 1580)
    o += D.button(1270, 1020, 288, 36, "Submit Demands   ◆ 74", "gold", 12)
    return o


# ---------------------------------------------------------------- operations (La Résistance)
def operations():
    o = D.backdrop()
    X, Y, WW, HH = 590, 284, 780, 560
    o += D.window(X, Y, WW, HH)
    o += D.band(X + 3, Y + 3, WW - 6, 38) + D.rule(X + 3, Y + 41, X + WW - 3)
    o += D.title(638, 293, "Infiltrate the Armed Forces", 22)
    o += D.close(1332, 290, 32)
    # the target (operation_bg 254 x 94 at 605, 327): the operation's emblem (85 x 85), the target's flag and name, location
    o += D.well(605, 330, 250, 92)
    o += D.medallion(657, 376, 40, "intel", icon_size=36)
    o += D.flag("CRD", 708, 345, 41, 26) + D.text(756, 349, "Cardonia", 15, D.CREAM, 100, font="fed")
    o += D.button(705, 379, 144, 32, "Winterthorn", size=11)
    # the lists the game stacks under it: duration, outlook, resources, operatives
    y = 430
    for lab, frac, txt in (("Duration", .38, "38 / 100 days"), ("Outlook", .72, "Good")):
        o += D.box(605, y, 250, 35, f"background:{D.STRIPES},linear-gradient(180deg,#18232A,#10181D);box-shadow:inset 0 0 0 1px rgba(201,165,90,.3)")
        o += D.label(615, y + 13, lab, 10, D.LABEL, 90, track=.14)
        o += D.progress(708, y + 9, 134, 16, frac)
        o += D.value(708, y + 11, txt, 11, D.CREAM, 134, "center", style="text-shadow:0 0 3px #000,0 0 2px #000")
        y += 39
    for lab, have, need, g in (("Civilian Factories", 1, 1, D.ICONS["factory"]), ("Infantry Equipment", 400, 400, G_DIV), ("Recon Drones", 20, 40, D.ICONS["air"])):
        o += D.box(605, y, 250, 40, f"background:{D.STRIPES},linear-gradient(180deg,#18232A,#10181D);box-shadow:inset 0 0 0 1px rgba(201,165,90,.3)")
        o += D.well(615, y + 6, 85, 27, c=3) + D.svg(647, y + 10, 20, 20, f'<g stroke="{D.GILT}" stroke-width="1.5">{g}</g>', "0 0 24 24")
        o += D.progress(710, y + 21, 95, 7, have / need, fill="linear-gradient(180deg,#5FC9A2,#2E6E60)" if have >= need else "linear-gradient(180deg,#E7B75A,#9C7A36)")
        o += D.value(710, y + 6, f"{have} / {need}", 11, D.CREAM, 98, "center")
        o += D.text(812, y + 6, "", 10)
        y += 44
    o += D.label(612, y + 6, "Operatives", 10, D.GILT, 120, track=.16)
    for i, nm in enumerate(("silh", "silh")):
        ox = 612 + i * 62
        o += D.box(ox, y + 22, 54, 72, f"background:{D.GOLD}") + D.silhouette(ox + 1.5, y + 23.5, 51, 69)
        o += D.diamond(ox + 47, y + 26, 8, "#5FC9A2", "box-shadow:0 0 0 1px #0B1014")
    o += D.box(612 + 124, y + 22, 54, 72, "box-shadow:inset 0 0 0 1px rgba(201,165,90,.45)")
    o += D.svg(612 + 152, y + 48, 18, 18, '<path d="M9 2v14M2 9h14" stroke="#C9A55A" stroke-width="1.6"/>').replace('class="a" style="left:764px', 'class="a" style="left:754px')
    # the dossier (the game's clipboard: top 581 x 121, middle, bottom 581 x 206): an ivory sheet under the typewriter
    o += D.ivory(860, 330, 500, 390, cols=())
    o += D.box(860, 330, 500, 4, "background:linear-gradient(90deg,#8B6A2C,#F1DC9C,#8B6A2C)")
    o += D.text(880, 346, "Phases", 17, D.INK, 300, font="fed", track=.08)
    o += D.box(880, 368, 460, 1, "background:rgba(122,92,38,.55)")
    phases = [("Infiltration", "Agents placed in the Cardonian General Staff", 1.0), ("Assets", "Recruit an officer in the Winterthorn garrison", .45),
              ("Exfiltration", "Bring the files out through Polkria", 0.0)]
    for i, (pn, desc, fr) in enumerate(phases):
        py = 382 + i * 66
        o += (f'<div class="a" style="left:880px;top:{py}px;width:46px;height:46px;border-radius:50%;'
              f'background:conic-gradient(#2E6E60 0 {fr * 360:.0f}deg,rgba(122,92,38,.25) {fr * 360:.0f}deg 360deg);'
              '-webkit-mask:radial-gradient(circle,transparent 17px,#000 17.5px)"></div>')
        o += D.box(888, py + 8, 30, 30, f"border-radius:50%;background:{'#2E6E60' if fr >= 1 else '#EFE6CC'};box-shadow:inset 0 0 0 1px #9C7A36")
        o += D.text(888, py + 16, "✓" if fr >= 1 else str(i + 1), 14, "#F4ECD9" if fr >= 1 else D.INK, 30, "center", weight=700)
        o += D.text(940, py + 6, pn, 15, D.INK, 380, font="fed", track=.04)
        o += D.text(940, py + 26, desc, 13, "#4A3B22", 400)
    o += D.box(880, 584, 460, 1, "background:rgba(122,92,38,.45)")
    o += D.text(880, 594, "Outcome", 15, D.INK, 300, font="fed", track=.08)
    o += D.text(880, 616, "Our operatives will sit inside Cardonia's command: its armies' plans are ours to read, "
                "and its divisions fight at a disadvantage against Rouental.", 13, "#3A2E1C", 450, lh=1.35)
    # the reward (500 x 80 at 857, 724): its emblem (95 x 95) and text
    o += D.box(857, 726, 500, 64, f"background:{D.STRIPES},linear-gradient(180deg,#1E2A31,#121B21);box-shadow:inset 0 0 0 1px rgba(201,165,90,.5)")
    o += D.medallion(898, 758, 34, "officer", icon_size=28, lit=True)
    o += D.text(957, 738, "Reward: −10% enemy planning speed against Rouental; their battle plans visible on the map.", 13, D.CREAM2, 390, lh=1.3)
    # the foot (752 x 40, lower left): commence when ready (823), the start button (858; 221 x 36), refund (1092), repeat (1133)
    o += D.band(603, 794, 752, 40) + D.rule(603, 794, 1355)
    o += D.text(638, 806, "Commence when ready", 12, D.CREAM2, 178, "right") + D.checkbox(826, 802, True, 20)
    o += D.button(858, 796, 221, 36, "Start Operation", "gold", 12)
    o += D.button(1092, 798, 31, 31, "")
    o += D.svg(1098, 804, 19, 19, '<path d="M15 6.5A6.5 6.5 0 1 0 16 12"/><path d="M15.5 2.5v4h-4"/>'.replace('<path', '<path stroke="#E3C77E" stroke-width="1.6"'))
    o += D.checkbox(1136, 802, False, 20) + D.text(1168, 806, "Automatically repeat", 12, D.CREAM2, 180)
    return o


# ---------------------------------------------------------------- raids
def raids():
    o = D.backdrop()
    X, Y, WW, HH = 640, 140, 640, 598
    o += D.window(X, Y, WW, HH)
    o += D.band(X + 6, Y + 6, WW - 12, 54) + D.rule(X + 6, Y + 60, X + WW - 6)
    o += D.title(800, 158, "Planning", 24, w=320, align="center")
    o += D.close(1233, 160, 32)
    o += D.label(760, 214, "Airborne Raid · Seize the Winterthorn Radar", 11, D.GILT, 400, "center", track=.18)
    # the raiders and the target (unit 660, 236; target 960, 236 right), their pictures (413 x 70 at 656 / 1170 right)
    o += D.text(660, 238, "1er Régiment Parachutiste", 14, D.CREAM, 300) + D.text(960, 238, "Winterthorn Radar Station", 14, D.CREAM, 300, "right")
    o += D.well(656, 258, 296, 74) + D.well(968, 258, 296, 74)
    o += D.svg(690, 270, 230, 50, '<g stroke="#E3C77E" stroke-width="1.3"><path d="M20 38c30-22 60-28 90-28M110 10l-8-4M110 10l-6 6"/>'
                                  '<path d="M150 20c-8 0-12 6-12 12h24c0-6-4-12-12-12zM138 32l12 12 12-12M150 32v12"/>'
                                  '<path d="M190 14c-8 0-12 6-12 12h24c0-6-4-12-12-12zM178 26l12 12 12-12M190 26v12"/></g>')
    o += D.svg(1000, 266, 230, 60, '<g stroke="#E3C77E" stroke-width="1.3"><path d="M30 52h170"/><path d="M110 52V26M96 52l14-26 14 26"/>'
                                   '<path d="M110 26c-14-10-14-24 0-30M110 26c14-10 14-24 0-30" opacity=".7"/><path d="M60 52V40h20v12M150 52V36h24v16"/></g>')
    # likelihood of success (664, 352) on its dial (210 x 80 at 700, 399), the equipment list (965-1260) on ivory
    o += D.value(664, 357, "Likelihood of Success", 15, D.GILT, 287, "center", weight=600)
    o += D.box(700, 399, 210, 80, f"background:{D.GOLD};clip-path:{D.chamfer(10)}")
    o += D.box(701, 400, 208, 78, f"background:radial-gradient(ellipse at 50% 100%,#1E2B33,#0B1014 80%);clip-path:{D.chamfer(9.6)}")
    o += (f'<div class="a" style="left:735px;top:410px;width:140px;height:140px;border-radius:50%;'
          'background:conic-gradient(from 270deg,#5FC9A2 0 112deg,rgba(201,165,90,.2) 112deg 180deg,transparent 180deg);'
          '-webkit-mask:radial-gradient(circle,transparent 58px,#000 59px,#000 64px,transparent 65px);clip-path:inset(0 0 50% 0)"></div>')
    o += D.value(705, 432, "62%", 24, D.CREAM, 200, "center")
    o += D.text(705, 459, "Favourable", 12, D.LABEL, 200, "center", weight=600)
    o += D.box(884, 476, 44, 18, f"background:#0B1014;clip-path:{D.chamfer(3)};box-shadow:inset 0 0 0 1px rgba(232,135,122,.7)")
    o += D.svg(888, 478, 14, 14, '<path d="M7 1.5l5.5 10.5h-11z" stroke="#E8877A" stroke-width="1.4"/>') + D.value(904, 480, "8%", 11, "#E8877A", 24)
    o += D.value(967, 357, "Additional Equipment", 15, D.GILT, 287, "center", weight=600)
    o += D.ivory(967, 380, 290, 120)
    o += D.text(976, 389, "Equipment", 12, D.INK, 130, weight=700) + D.text(1100, 389, "Have", 12, D.INK, 76, "right", weight=700)
    o += D.text(1182, 389, "Need", 12, D.INK, 66, "right", weight=700)
    for i, (n, h, r) in enumerate((("Transport Aircraft", "24", "16"), ("Support Equipment", "60", "40"), ("Recon Drones", "6", "12"))):
        yy = 412 + i * 22
        o += D.text(976, yy, n, 13, "#3A2E1C", 130) + D.text(1100, yy, h, 13, D.INK, 76, "right", weight=700)
        o += D.text(1182, yy, r, 13, "#8E2F22" if int(h) < int(r) else D.INK, 66, "right", weight=700)
        o += D.box(975, yy + 17, 274, 1, "background:rgba(156,122,54,.25)")
    # risk taking: three toggles (50 x 84 at 705 / 780 / 855, y 565) with their labels; preparation and its bar
    o += D.value(665, 513, "Risk Taking", 15, D.GILT, 287, "center", weight=600)
    for i, (n, on) in enumerate((("Low", False), ("Medium", True), ("High", False))):
        tx = 705 + i * 75
        o += D.text(tx - 20, 548, n, 12, D.CREAM2 if on else D.LABEL, 90, "center", weight=600)
        o += D.box(tx + 10, 567, 30, 72, f"background:#0A0F12;border-radius:15px;box-shadow:inset 0 0 0 1px {'#E3C77E' if on else 'rgba(201,165,90,.45)'}")
        ky = 573 if on else 609
        o += D.box(tx + 14, ky, 22, 22, f"border-radius:50%;background:{'radial-gradient(circle at 40% 35%,#5FC9A2,#2E6E60)' if on else 'radial-gradient(circle at 40% 35%,#4A565C,#1C2428)'};box-shadow:0 0 0 1px #0B1014")
    o += D.value(969, 513, "Preparation", 15, D.GILT, 287, "center", weight=600)
    o += D.text(967, 557, "12 days until ready", 13, D.CREAM2, 300, "center")
    o += D.box(977, 587, 283, 28, f"background:{D.GOLD};clip-path:{D.chamfer(5)}")
    o += D.box(978, 588, 281, 26, f"background:#0A0F12;clip-path:{D.chamfer(4.6)}")
    o += D.box(981, 593, 274 * .6, 16, "background:linear-gradient(180deg,#F1DC9C,#B48F44)")
    o += D.value(967, 594, "60%", 12, "#1B140A", 300, "center")
    o += D.text(967, 627, "Intelligence on the target: 48%", 12, D.LABEL, 300, "center")
    # the foot: auto-launch options (650, 680; 150 x 30), auto-launch (820 / 920), the launch keys and button, cancel
    o += D.rule(X + 10, 662, X + WW - 10, "rgba(201,165,90,.5)")
    o += D.well(650, 680, 150, 30, c=3) + D.text(662, 690, "When ready", 12, D.CREAM, 120)
    o += D.svg(780, 690, 10, 10, '<path d="M1 3l4 4 4-4" stroke="#C9A55A" stroke-width="1.4"/>')
    o += D.text(814, 690, "Auto-launch", 12, D.CREAM2, 96, "right") + D.checkbox(925, 685, False, 20)
    o += D.svg(968, 670, 94, 56, '<g stroke="#E3C77E" stroke-width="1.5"><circle cx="24" cy="28" r="9"/><path d="M33 28h16l3 4 3-4 3 4"/>'
                                 '<circle cx="70" cy="28" r="9" opacity=".55"/><path d="M61 28h-6" opacity=".55"/></g>')
    o += D.layer(D.octagon_pts(1086, 699, 24), D.GOLD) + D.layer(D.octagon_pts(1086, 699, 22.5), "radial-gradient(circle at 50% 35%,#A9493A,#4A1E19 80%)")
    o += D.svg(1077, 689, 20, 20, '<path d="M6 3l11 7-11 7z" fill="#FBEAB4" stroke="#FBEAB4" stroke-width="1"/>')
    o += D.button(1125, 681, 123, 34, "Cancel", size=11)
    return o


# ---------------------------------------------------------------- end of game
def end_of_game():
    o = D.backdrop(dim=.45, top=False)
    X, Y, WW, HH = 382, 188, 1156, 703
    o += D.window(X, Y, WW, HH)
    # the flag (410, 228; in its frame 92 x 58 at 402, 214), the score, the ruler (520, 214; 117 x 158 in 136 x 181)
    o += D.box(402, 214, 92, 58, f"background:{D.GOLD}") + D.flag("ROU", 407, 219, 82, 48, frame=False)
    o += D.label(405, 290, "Score", 10, D.LABEL, 120, track=.2)
    o += D.value(405, 306, "48,612", 26, "#F1DC9C", 200)
    o += D.text(405, 342, "1st of 160", 15, D.CREAM2, 200, font="fed", track=.06)
    o += D.box(513, 206, 136, 181, f"background:{D.GOLD};clip-path:polygon(0 18px,18px 0,118px 0,136px 18px,136px 181px,0 181px)")
    o += D.box(515, 208, 132, 177, "clip-path:polygon(0 17px,17px 0,115px 0,132px 17px,132px 177px,0 177px);overflow:hidden",
               D.portrait("roland_cahun", 0, 0, 132, 177))
    # the country's facts (670, 210 ...), its name (1059, 196)
    for i, (k, v) in enumerate((("Leader", "Roland II Cahun"), ("Ideology", "Monarchist"), ("Government", "Absolute Monarchy"),
                                ("Ruling party", "Maison Cahun"))):
        o += D.label(670, 214 + i * 46, k, 10, D.LABEL, 300, track=.2) + D.text(670, 230 + i * 46, v, 16, D.CREAM, 340, font="fed", track=.03)
    o += D.title(1059, 204, "The Sacred Principality of Rouental", 18, w=470, track=.12)
    o += D.rule(1059, 240, 1520, "rgba(201,165,90,.6)")
    # factions (1062, 242: faction, strength, members; the list 475 x 136, rows of 25)
    o += D.label(1062, 272, "Faction", 10, D.GILT, 160, track=.18) + D.label(1200, 272, "Strength", 10, D.GILT, 100, "center", track=.18)
    o += D.label(1320, 272, "Members", 10, D.GILT, 100, "center", track=.18)
    for i, (f, s, m) in enumerate((("The Association", "412", "8"), ("The Fraxhemark Accord", "388", "6"),
                                   ("The Kampfian Compact", "301", "5"), ("The Sarkisian Front", "277", "7"))):
        yy = 292 + i * 25
        o += D.box(1062, yy, 460, 23, f"background:{'rgba(46,110,96,.35)' if i == 0 else 'rgba(255,255,255,.02)'};box-shadow:inset 0 -1px 0 rgba(201,165,90,.15)")
        o += D.text(1070, yy + 5, f, 13, D.CREAM, 180) + D.value(1200, yy + 5, s, 13, D.CREAM, 100, "center") + D.value(1320, yy + 5, m, 13, D.CREAM, 100, "center")
    # the ladder (1156 x 452 from y 434): filters, six sort medallions, the countries in four columns of 270
    o += D.rule(X + 8, 430, X + WW - 8)
    o += D.band(X + 6, 434, WW - 12, 448, "linear-gradient(180deg,#141E24,#0D1418)")
    o += D.lit_bar(442, 460, 260, 28, 5) + D.text(442, 461, "Country", 12, "#FBEAB4", 260, "center", weight=600, track=.14, caps=True, h=27, valign=True)
    o += D.bar(712, 460, 148, 28, c=5) + D.text(712, 461, "Faction", 12, D.LABEL, 148, "center", weight=600, track=.14, caps=True, h=27, valign=True)
    for i, g in enumerate(("officer", "army", "navy", "air", "production", "construction")):
        o += D.medallion(977 + i * 100, 476, 22, g, icon_size=22, lit=(i == 0))
    ladder = [("ROU", "Rouental"), ("KRI", "Krionik"), ("FRX", "Fraxhemark"), ("KPF", "Kampfian Empire"), ("SRK", "Sarkis"),
              ("CRD", "Cardonia"), ("KRK", "Kurikia"), ("TUP", "Terreich und Preußen"), ("HLR", "Hollier"), ("BLK", "Belekria"),
              ("WRS", "Wersh"), ("EVR", "Evriches"), ("SGV", "Selgrave"), ("LST", "Lustiana"), ("LNT", "Placeholdaire"),
              ("ESD", "Estande"), ("GDN", "Guedelon"), ("SGN", "Seigne"), ("LZC", "Lanzerac"), ("THD", "Thorian Dynamics"),
              ("GOB", "Gorbastan"), ("ZUK", "Zukchiva"), ("SNH", "Sennheiser"), ("AIS", "Merlovich"), ("ILR", "Illiricium"),
              ("LTH", "Leithanien"), ("CNA", "Chineasia"), ("TSU", "Tsuruma"), ("PLJ", "Plaija"), ("VIL", "Vilna"),
              ("DVL", "Devlon"), ("KSK", "Kieska"), ("SMB", "Sombor"), ("AVE", "Avesária"), ("BRO", "Bromé"), ("SNA", "Sanada"),
              ("QNG", "Qinguo"), ("GND", "Ganden"), ("KIL", "Royalist Illiricium"), ("CTF", "Côtefer"), ("ETR", "Entroterra"),
              ("MZG", "Mezzogiorno"), ("STM", "Schteirmark"), ("HZB", "Hohenzburg"), ("ARC", "Arcadia"), ("VLN", "Volinovia"),
              ("RST", "Rastava"), ("CRZ", "Coraliza"), ("RMD", "Romanoddle"), ("SMN", "Sminishia"),
              ("ZST", "West Sminishia"), ("MRG", "Merlgould"), ("VNT", "Vultuca"), ("TRC", "Troc")]
    for i, (tag, n) in enumerate(ladder[:56]):
        c, r = i // 14, i % 14
        x, y = 402 + c * 284, 520 + r * 25
        if x > 1500:
            break
        o += D.box(x, y, 276, 23, f"background:{'rgba(46,110,96,.35)' if i == 0 else 'rgba(255,255,255,.02)'};box-shadow:inset 0 -1px 0 rgba(201,165,90,.12)")
        o += D.value(x + 6, y + 5, f"{i + 1}.", 12, D.LABEL, 26, "right")
        o += D.flag(tag, x + 38, y + 4, 22, 15, frame=False)
        o += D.text(x + 68, y + 5, n, 13, D.CREAM, 140) + D.value(x + 200, y + 5, f"{int(48612 * (0.93 ** i)):,}", 12, D.CREAM2, 66, "right", weight=600)
    return o


# ---------------------------------------------------------------- diplomatic message icons (menubar.gui)
def banner(x, y, kind, tag, glyph, col):
    """messageicon_bg (53 x 90, 20 frames by kind): a pennant with the request's glyph, the sender's flag (14, 39)"""
    o = D.box(x, y, 53, 64, f"background:{col};clip-path:polygon(0 0,100% 0,100% 74%,50% 100%,0 74%)")
    o += D.box(x + 1.5, y + 1.5, 50, 60, "background:linear-gradient(180deg,#1E2A31,#0B1014);clip-path:polygon(0 0,100% 0,100% 74%,50% 100%,0 74%)")
    o += D.box(x + 5, y + 5, 43, 1, f"background:{col};opacity:.7")
    o += D.svg(x + 15, y + 10, 23, 23, f'<g stroke="{col}" stroke-width="1.6">{glyph}</g>', "0 0 24 24")
    o += D.flag(tag, x + 14, y + 39, 25, 16)
    return o


def messages():
    o = D.backdrop()
    reqs = [("access", "HLR", '<path d="M4 12h14M14 8l4 4-4 4"/><path d="M4 6v12"/>', "#E3C77E", "Military access"),
            ("faction", "LZC", D.ICONS["faction"], "#5FC9A2", "Join the Association"),
            ("peace", "CRD", '<path d="M12 21c-5-3-8-7-8-11a4 4 0 0 1 8-1 4 4 0 0 1 8 1c0 4-3 8-8 11z"/>', "#A9C7DE", "Offer of peace"),
            ("lendlease", "GDN", D.ICONS["convoy"], "#E7B75A", "Lend-lease"),
            ("war", "THD", D.ICONS["swords"], "#E8877A", "Call to arms")]
    for i, (k, tag, g, col, name) in enumerate(reqs):
        o += banner(10 + i * 64, 1012, k, tag, g, col)
    # hovering the second: its tooltip
    o += D.tooltip(60, 846, 330, 150, "Lanzerac asks to join",
                   [("Faction", "The Association", D.CREAM), ("Opinion of us", "+45", D.POS), ("Answer within", "6 days", "#E7B75A")],
                   "Click to answer; right-click to dismiss.")
    return o
