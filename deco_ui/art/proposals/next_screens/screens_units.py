"""Mockups: the division details, the ship details (unitview.gui), and the map's unit counters (mapicons.gui), the
right-click menu, the commander abilities and the theatres. Every box is the game's (guilayout.py read them from
its .gui files; the numbers below are screen pixels at 1920 x 1080)."""
from deco import *  # noqa: F401,F403
import deco as D


# ---------------------------------------------------------------- terrain glyphs (line art of our own)
TERRAIN = {
    "plains": '<path d="M2 15h20"/><path d="M5 12c1-2 2-2 3 0M11 11c1-2 2-2 3 0M17 12c1-2 2-2 3 0"/>',
    "forest": '<path d="M7 19V14M7 4l-4 7h8zM7 8l-3.5 6h7z"/><path d="M17 19v-4M17 6l-4 7h8zM17 10l-3.5 6h7z"/>',
    "hills": '<path d="M2 18c3-6 6-8 9-8s5 3 7 5M9 18c3-4 6-6 8-6s3 2 5 4"/>',
    "mountain": '<path d="M2 19l7-12 4 6 3-4 6 10z"/><path d="M7.5 9.5l1.5 1.5 1.5-1.5"/>',
    "marsh": '<path d="M3 16h7M13 16h8M5 19h6M14 19h5"/><path d="M8 14V8M11 14V6M14 14V9"/>',
    "jungle": '<path d="M12 20V9"/><path d="M12 9c-2-3-6-3-8-1M12 9c2-3 6-3 8-1M12 9c-1-3-1-5 1-6M12 11c-3-1-5 0-6 3M12 11c3-1 5 0 6 3"/>',
    "urban": '<path d="M3 20V9h5v11M8 20V5h6v15M14 20v-8h6v8M2 20h20"/><path d="M10 8h2M10 11h2M10 14h2"/>',
    "desert": '<path d="M2 17c4-3 7-3 10 0s6 3 10 0"/><circle cx="17" cy="7" r="2.5"/><path d="M5 13c2-2 4-2 6 0"/>',
    "river": '<path d="M2 8c4-3 6 3 10 0s6-3 10 0M2 13c4-3 6 3 10 0s6-3 10 0M2 18c4-3 6 3 10 0s6-3 10 0"/>',
    "fort": '<path d="M4 20V9h3V6h3v3h4V6h3v3h3v11z"/><path d="M10 20v-5h4v5"/>',
    "night": '<path d="M15 3a8 8 0 1 0 6 13A7 7 0 0 1 15 3z"/>',
    "amphibious": '<path d="M2 17c3-2 5 2 8 0s5-2 8 0 3 1 4 0"/><path d="M6 13l2-6h8l2 6z"/>',
}


def terrain(name, x, y, s=24, color=GILT, sw=1.5):
    return D.svg(x, y, s, s, f'<g stroke="{color}" stroke-width="{sw}">{TERRAIN[name]}</g>', "0 0 24 24")


def mod_chip(cx, cy, kind, sign):
    """a terrain adjuster's movement / attack / defence chip (the game's 3-frame strips: better, no change, worse), 19 x 19
    in the game's 21 x 21 box"""
    col = {1: "#5FB39C", 0: "rgba(201,165,90,.5)", -1: "#C9614F"}[sign]
    fill = {1: "#123029", 0: "#0B1014", -1: "#2A1210"}[sign]
    glyph = {"move": '<path d="M5 12h12M13 8l4 4-4 4"/>', "attack": '<path d="M6 18L18 6M13 6h5v5"/>',
             "defense": '<path d="M12 4l6 2.2v4.6c0 4-2.6 6.9-6 8.2-3.4-1.3-6-4.2-6-8.2V6.2z"/>'}[kind]
    return (D.box(cx - 9.5, cy - 9.5, 19, 19, f"background:{col};clip-path:{D.chamfer(4)}")
            + D.box(cx - 8.5, cy - 8.5, 17, 17, f"background:{fill};clip-path:{D.chamfer(3.6)}")
            + D.svg(cx - 6.5, cy - 6.5, 13, 13, f'<g stroke="{col if sign else "#C9A55A"}" stroke-width="2.3">{glyph}</g>', "0 0 24 24"))


def adjuster(x, y, name, mv, at, df):
    """designer_adjuster_entry: the terrain picture (45 x 45 at +18, +11) in its frame (70 x 62 at +7, +5), the three
    strips (21 x 21 at +11 / +34 / +56, +42)"""
    out = D.layer([(x + 12, y + 5), (x + 72, y + 5), (x + 77, y + 10), (x + 77, y + 62), (x + 7, y + 62), (x + 7, y + 10)],
                  "rgba(201,165,90,.65)")
    out += D.layer([(x + 12.4, y + 6), (x + 71.6, y + 6), (x + 76, y + 10.4), (x + 76, y + 61), (x + 8, y + 61), (x + 8, y + 10.4)],
                   f"{STRIPES},linear-gradient(180deg,#1A252C,#0D1418)")
    out += D.box(x + 18, y + 11, 45, 30, "background:radial-gradient(circle at 50% 40%,#16212A,#0A0F12 80%);box-shadow:inset 0 0 0 1px rgba(201,165,90,.35)")
    out += terrain(name, x + 28, y + 14, 25)
    for i, (k, s) in enumerate((("move", mv), ("attack", at), ("defense", df))):
        out += mod_chip(x + 21.5 + i * 22.5, y + 51, k, s)
    return out


def equipment_glyph(kind, x, y, w=62, h=34):
    """an equipment picture's stand-in (the game's are its 3D renders): a lacquer well with a gilt line drawing"""
    out = D.box(x, y, w, h, "background:radial-gradient(ellipse at 50% 60%,#1A252C,#0A0F12 80%);box-shadow:inset 0 0 0 1px rgba(201,165,90,.4)")
    g = D.unit_glyph(kind, 40, "#E3C77E", 1.4)
    out += f'<div class="a" style="left:{x + (w - 40) / 2}px;top:{y + (h - 21.5) / 2}px">{g}</div>'
    return out


# ---------------------------------------------------------------- division details
DIV_BASE = [("Strength", "60.0"), ("Organisation", "41.4"), ("Recovery Rate", "0.30"), ("Reconnaissance", "3.4"),
            ("Suppression", "2.0"), ("Weight", "9.6"), ("Supply Use", "2.84"), ("Reliability", "82%"),
            ("Trickleback", "5%"), ("Exp. Loss", "-10%")]
DIV_COMBAT = [("Soft Attack", "312.6"), ("Hard Attack", "148.2"), ("Air Attack", "21.0"), ("Defence", "286.4"),
              ("Breakthrough", "504.8"), ("Armour", "142.5"), ("Piercing", "168.0"), ("Initiative", "+12%"),
              ("Entrenchment", "6.0"), ("Combat Width", "26")]
DIV_MISC = [("Manpower", "11,240"), ("Training Time", "150 d"), ("Max Speed", "14.0 km/h"), ("Hardness", "84.6%"),
            ("Fuel Capacity", "2,880"), ("Fuel Use", "9.84 /h"), ("Equip. Capture", "4%"), ("Collateral", "11.2")]


def division_details():
    X, Y, WW, HH = 685, 305, 856, 522
    o = D.backdrop()
    o += D.window(X, Y, WW, HH)
    # the left part's header (title "Unit Details" at 720, 304, hoi_36header) and the right column's strip
    o += D.band(X + 6, Y + 6, 552, 33) + D.rule(X + 6, Y + 39, X + 558, "rgba(201,165,90,.85)")
    o += D.title(720, 314, "Unit Details", 21)
    o += D.diamond(708, Y + 22, 6)
    # template upgrade (1060, 310), the owner's small flag in its frame (1183, 312, 26 x 21)
    o += D.box(1063, 312, 22, 22, "transform:rotate(45deg) scale(.78);background:#0B1014;box-shadow:0 0 0 1px #E7B75A")
    o += D.svg(1065, 314, 18, 18, '<path d="M9 14V5M5 9l4-4 4 4" stroke="#E7B75A" stroke-width="1.8"/>')
    o += D.flag("ROU", 1184, 313, 26, 18)
    o += D.vrule(X + 559, Y + 6, Y + HH - 6, "rgba(201,165,90,.6)")
    o += D.band(1246, Y + 6, 289, 33) + D.rule(1246, Y + 39, 1535, "rgba(201,165,90,.85)")
    # delete (1245, 307), manpower (1285 + text 1328 c60), equipment (1420 + text 1453), close (1507, 307)
    o += D.button(1249, 309, 28, 27, "", icon=None)
    o += D.svg(1254, 313, 18, 18, '<path d="M4 6h10M7.5 6V4h3v2M5.5 6l.8 9h5.4l.8-9M8 8.5v4.5M10 8.5v4.5" stroke="#E3C77E" stroke-width="1.3"/>')
    o += D.ico("manpower", 1287, 310, 22, D.GILT, 1.4) + D.value(1316, 315, "11,240", 15, D.CREAM, 84, "center")
    o += D.ico("logistics", 1412, 310, 22, D.GILT, 1.4) + D.value(1442, 315, "100%", 15, D.POS, 56)
    o += D.close(1505, 306, 31)
    # identity row: the division's type (705, 340; 49 x 27), template change (764), priority (778), its name (793-1065),
    # experience (1070) and its level (1149, 27 x 27)
    o += D.well(701, 345, 86, 28, c=3)
    o += f'<div class="a" style="left:713px;top:350px">{D.unit_glyph("armor", 34, "#EBD397", 1.3)}</div>'
    o += D.svg(763, 351, 14, 16, '<path d="M3 6h8l-2.5-2.5M11 11H3l2.5 2.5" stroke="#C9A55A" stroke-width="1.4"/>')
    o += D.well(793, 342, 270, 30, c=3)
    o += D.chevrons(779, 344, 3, 12, "#E7B75A")
    o += D.text(805, 351, "1e Garde Royale", 16, D.CREAM, 240, font="fed", track=.04)
    o += D.svg(1046, 352, 10, 10, '<path d="M1 3l4 4 4-4" stroke="#C9A55A" stroke-width="1.4"/>')
    o += D.label(1074, 353, "Seasoned", 11, D.LABEL, 74, track=.12)
    o += D.box(1149, 343, 27, 27, "transform:rotate(45deg) scale(.82);background:linear-gradient(180deg,#E8CD84,#8B6A2C)")
    o += D.box(1152, 346, 21, 21, "transform:rotate(45deg) scale(.82);background:#0E1519")
    o += D.chevrons(1155, 349, 2, 15, "#F1DC9C")
    # the stats sheet: three columns (698 / 867 / 1042, labels at y 381 in the typewriter, rows of 20 from y 405)
    o += D.ivory(695, 374, 545, 250, cols=(864, 1037))
    for (cx, lab, rows) in ((703, "Base Stats", DIV_BASE), (877, "Combat Stats", DIV_COMBAT), (1049, "Misc. Stats", DIV_MISC)):
        o += D.text(cx, 383, lab, 16, D.INK, 160, font="fed", track=.06)
        o += D.box(cx, 401, 152, 1, "background:rgba(122,92,38,.55)")
        for i, (k, v) in enumerate(rows):
            yy = 405 + i * 20 + 4
            o += D.text(cx, yy, k, 13, "#3A2E1C", 110, weight=500) + D.text(cx + 60, yy, v, 13, D.INK, 95, "right", weight=700)
            o += D.box(cx, 405 + (i + 1) * 20 - 1, 152, 1, "background:rgba(156,122,54,.22)")
    # hardness: composition (890, 630), armour (928, 635), the bar (972, 635; frame 967, 630, 207 x 27), infantry (1186, 634)
    o += D.band(695, 628, 545, 30)
    o += D.label(705, 640, "Adjusters", 11, D.GILT, 150, track=.18)
    o += D.svg(889, 631, 22, 22, '<g stroke="#C9A55A" stroke-width="1.3"><rect x="3" y="3" width="7" height="7"/><rect x="12" y="3" width="7" height="7"/><rect x="3" y="12" width="7" height="7"/><path d="M15.5 12v7M12 15.5h7"/></g>')
    o += f'<div class="a" style="left:927px;top:636px">{D.unit_glyph("armor", 32, "#C9A55A", 1.2)}</div>'
    o += D.box(967, 631, 207, 24, "background:#0A0F12;box-shadow:inset 0 0 0 1px rgba(201,165,90,.6)")
    o += D.box(972, 637, int(194 * .846), 12, "background:linear-gradient(180deg,#F1DC9C,#B48F44)")
    o += D.box(972 + int(194 * .846), 637, 194 - int(194 * .846), 12, "background:linear-gradient(180deg,#4F6B7A,#2C4250)")
    o += D.diamond(972 + 194 * .846, 643, 7, "#F1DC9C", "box-shadow:0 0 0 1px #0B1014")
    o += f'<div class="a" style="left:1183px;top:635px">{D.unit_glyph("infantry", 26, "#C9A55A", 1.3)}</div>'
    # terrain adjusters: the grid at (695, 658), 545 x 132, slots of 110 x 62
    o += D.well(695, 660, 545, 130)
    adj = [("forest", 0, -1, 0), ("hills", 0, -1, 1), ("mountain", -1, -1, 1), ("marsh", -1, -1, -1),
           ("plains", 1, 1, 0), ("urban", -1, -1, 1), ("river", 0, -1, 0), ("amphibious", -1, -1, 0)]
    for i, (n, a, b, c) in enumerate(adj):
        o += adjuster(695 + 14 + (i % 4) * 110 + 30, 660 + (i // 4) * 62 + 1, n, a, b, c)
    o += D.vrule(1220, 666, 784, "rgba(201,165,90,.35)") + D.box(1217, 672, 7, 40, "background:#C9A55A;clip-path:polygon(50% 0,100% 15%,100% 85%,50% 100%,0 85%,0 15%)")
    # tabs (695 / 805 / 915, y 792, 113 x 36)
    o += D.tab(695, 792, 113, 30, "Stats", True) + D.tab(805, 792, 113, 30, "History") + D.tab(915, 792, 113, 30, "Template")
    # the officer: header (1247, 339; 270 x 30) "Officer", promote (1425, 339; 90 x 31), portrait (1253, 365), name (1317, 377),
    # traits (1296, 409)
    o += D.bar(1247, 341, 175, 28, c=5) + D.label(1259, 352, "Officer", 11, D.GILT, 120, track=.2)
    o += D.button(1425, 340, 90, 29, "Promote", size=11)
    o += D.box(1251, 372, 44, 50, "background:linear-gradient(180deg,#E8CD84,#8B6A2C);clip-path:polygon(0 8px,8px 0,36px 0,44px 8px,44px 50px,0 50px)")
    o += D.box(1252.5, 373.5, 41, 47, "clip-path:polygon(0 7px,7px 0,34px 0,41px 7px,41px 47px,0 47px);overflow:hidden",
               D.silhouette(0, 0, 41, 47))
    o += D.text(1306, 379, "Lt. Col. Armand de Beaufort", 14, D.CREAM, 220, font="fed", track=.02)
    o += D.label(1306, 397, "Division commander", 9.5, D.LABEL, 200, track=.14)
    o += D.chevrons(1307, 409, 2, 11, D.GILT) + D.text(1323, 411, "Panzer Leader", 12, D.CREAM2, 120)
    o += D.text(1420, 411, "· Trickster", 12, D.CREAM2, 100)
    # equipment list (1247, 426; 294 x 356): archetype headers (270 x 30) and equipment rows (270 x 50)
    o += D.well(1247, 426, 290, 356)
    yy = 430
    rows = [("Main Battle Tanks", "240 / 240", [("armor", "ROU", "Char Royal", "240")]),
            ("Infantry Fighting Vehicles", "216 / 216", [("mechanized", "ROU", "VCI Écuyer", "216")]),
            ("Infantry Equipment", "1,200 / 1,200", [("infantry", "ROU", "Modular Rifles", "1,200")]),
            ("Support Equipment", "180 / 180", [("motorized", "ROU", "Combat Support Kit", "180")])]
    for head, amt, eq in rows:
        o += D.bar(1251, yy, 270, 28, c=5)
        o += D.text(1261, yy + 9, head, 13, D.GILT, 175, weight=600) + D.text(1441, yy + 9, amt, 13, D.CREAM, 72, "right", weight=700)
        yy += 30
        for kind, tag, name, n in eq:
            o += D.box(1251, yy, 270, 48, "background:linear-gradient(90deg,rgba(201,165,90,.07),rgba(201,165,90,0));border-bottom:1px solid rgba(201,165,90,.15)")
            o += equipment_glyph(kind, 1257, yy + 7, 58, 34)
            o += D.flag(tag, 1321, yy + 25, 22, 14, frame=True)
            o += D.text(1351, yy + 18, name, 14, D.CREAM, 110, weight=500)
            o += D.text(1429, yy + 18, n, 14, D.CREAM, 80, "right", weight=700)
            yy += 50
    o += D.vrule(1528, 432, 776, "rgba(201,165,90,.3)")
    return o


# ---------------------------------------------------------------- ship details
TERRAIN.update({
    "deep": '<path d="M2 9c3-2 5 2 8 0s5-2 8 0 3 1 4 0M2 14c3-2 5 2 8 0s5-2 8 0 3 1 4 0"/><path d="M12 17v4M9 20l3 2 3-2"/>',
    "shallow": '<path d="M2 11c3-2 5 2 8 0s5-2 8 0 3 1 4 0"/><path d="M3 18h18M6 15.5h4M13 15.5h5"/>',
    "fjords": '<path d="M2 20l5-9 3 4 3-7 4 6 2-2 3 8"/><path d="M5 20c2-1 3 1 5 0s3-1 5 0"/>',
    "arctic": '<path d="M12 3v18M4.2 7.5l15.6 9M4.2 16.5l15.6-9"/><path d="M10 5l2 2 2-2M10 19l2-2 2 2"/>',
})
SHIP_BASE = [("Hit Points", "1,820"), ("Organisation", "60.0"), ("Max Speed", "31.5 kn"), ("Range", "12,000 km"),
             ("Reliability", "88%"), ("Supply Use", "1.20"), ("Fuel Use", "4.20 /h"), ("Carrier Size", "72")]
SHIP_COMBAT = [("Light Attack", "18.0"), ("Light Piercing", "12.0"), ("Heavy Attack", "0.0"), ("Heavy Piercing", "0.0"),
               ("Missile Attack", "0.0"), ("Sub Attack", "6.0"), ("Armour", "28.0"), ("Air Defence", "96.0")]
SHIP_MISC = [("Surface Detection", "44.0"), ("Sub Detection", "18.0"), ("Surface Visibility", "52.0"), ("Sub Visibility", "—"),
             ("Mines Sweeping", "0"), ("Mines Planting", "0"), ("Manpower", "4,200"), ("Build Cost", "38,400")]


def ship_details():
    X, Y, WW, HH = 685, 305, 856, 409
    o = D.backdrop()
    o += D.window(X, Y, WW, HH)
    o += D.band(X + 6, Y + 6, 552, 33) + D.rule(X + 6, Y + 39, X + 558, "rgba(201,165,90,.85)")
    o += D.title(720, 314, "Ship Details", 21) + D.diamond(708, Y + 22, 6)
    o += D.vrule(X + 559, Y + 6, Y + HH - 6, "rgba(201,165,90,.6)")
    o += D.band(1246, Y + 6, 289, 33) + D.rule(1246, Y + 39, 1535, "rgba(201,165,90,.85)")
    o += D.button(1249, 310, 28, 27, "")
    o += D.svg(1254, 314, 18, 18, '<path d="M4 6h10M7.5 6V4h3v2M5.5 6l.8 9h5.4l.8-9M8 8.5v4.5M10 8.5v4.5" stroke="#E3C77E" stroke-width="1.3"/>')
    o += D.ico("manpower", 1287, 311, 22, D.GILT, 1.4) + D.value(1316, 316, "4,200", 15, D.CREAM, 84, "center")
    o += D.ico("fuel", 1418, 311, 22, D.GILT, 1.4) + D.value(1448, 316, "4.20", 15, D.CREAM, 56)
    o += D.close(1505, 307, 31)
    # identity: type (702, 348; 76 x 42), name (798, 347; 264), experience (1070), level (1181)
    o += D.well(701, 345, 86, 30, c=3)
    o += f'<div class="a" style="left:713px;top:352px">{D.unit_glyph("carrier", 40, "#EBD397", 1.3)}</div>'
    o += D.well(793, 344, 272, 30, c=3)
    o += D.text(805, 353, "Souveraine", 17, D.CREAM, 240, font="fed", track=.06)
    o += D.label(1074, 355, "Regular", 11, D.LABEL, 100, track=.12)
    o += D.box(1181, 345, 27, 27, "transform:rotate(45deg) scale(.82);background:linear-gradient(180deg,#E8CD84,#8B6A2C)")
    o += D.box(1184, 348, 21, 21, "transform:rotate(45deg) scale(.82);background:#0E1519")
    o += D.chevrons(1188, 352, 1, 15, "#F1DC9C")
    # the stats sheet (rows of 20 from y 403)
    o += D.ivory(695, 378, 545, 192, cols=(864, 1037))
    for (cx, lab, rows) in ((703, "Base Stats", SHIP_BASE), (877, "Combat Stats", SHIP_COMBAT), (1049, "Misc. Stats", SHIP_MISC)):
        o += D.text(cx, 384, lab, 16, D.INK, 160, font="fed", track=.06)
        o += D.box(cx, 400, 152, 1, "background:rgba(122,92,38,.55)")
        for i, (k, v) in enumerate(rows):
            yy = 403 + i * 20 + 4
            o += D.text(cx, yy, k, 13, "#3A2E1C", 112, weight=500) + D.text(cx + 60, yy, v, 13, D.INK, 95, "right", weight=700)
            o += D.box(cx, 403 + (i + 1) * 20 - 1, 152, 1, "background:rgba(156,122,54,.22)")
    # the lower field (the game's blue sea): pride of the fleet (698, 585; 3 frames), support and dominance readouts
    # (705 / 735, y 603 and 635: they lie under the pride button in the game's file, so they move right of it),
    # the class picture and its name (centred on x 920, y 585), the role (700, 665), the naval terrain (1055, 565:
    # 70 x 58 slots)
    o += D.well(695, 576, 545, 122, fill="linear-gradient(180deg,#0E1A22,#09121A)")
    o += D.box(696, 577, 543, 120, "overflow:hidden", "".join(
        f'<div class="a" style="left:0;top:{18 + i * 16}px;width:543px;height:1px;background:linear-gradient(90deg,rgba(104,150,190,0),rgba(104,150,190,.10) 30%,rgba(104,150,190,.10) 70%,rgba(104,150,190,0))"></div>'
        for i in range(7)))
    o += D.medallion(717, 603.5, 18, "officer", icon_size=18, lit=True)
    o += D.ico("faction", 752, 612, 16, D.GILT, 1.4) + D.value(774, 615, "Support +12.0", 13, D.CREAM2, 120, weight=600)
    o += D.ico("navy", 752, 639, 16, D.GILT, 1.4) + D.value(774, 642, "Dominance 34.6", 13, D.CREAM2, 120, weight=600)
    o += D.title(745, 588, "Couronne-class Carrier", 15, w=350, align="center", track=.12)
    o += D.fade_rule(800, 607, 1040)
    o += D.box(886, 616, 147, 69, "background:radial-gradient(ellipse at 50% 60%,rgba(201,165,90,.10),rgba(0,0,0,0) 70%)")
    o += D.carrier_art(886, 616)
    o += D.box(700, 663, 35, 30, f"background:#0B1014;clip-path:{D.chamfer(5)};box-shadow:inset 0 0 0 1px #C9A55A")
    o += D.layer([(705, 663), (730, 663), (735, 668), (735, 693), (730, 698), (705, 698), (700, 693), (700, 668)], "rgba(201,165,90,.75)")
    o += D.layer([(705.4, 664), (729.6, 664), (734, 668.4), (734, 692.6), (729.6, 697), (705.4, 697), (701, 692.6), (701, 668.4)], "#0B1014")
    o += f'<div class="a" style="left:705px;top:675px">{D.unit_glyph("jet", 25, "#E3C77E", 1.2)}</div>'
    for i, (n, mv, at) in enumerate((("deep", 1, 0), ("shallow", 0, 1), ("fjords", -1, -1), ("arctic", -1, 0))):
        tx, ty = 1060 + (i % 2) * 86, 580 + (i // 2) * 58
        o += D.box(tx, ty, 70, 54, "background:rgba(201,165,90,.6);clip-path:" + D.chamfer(5))
        o += D.box(tx + 1, ty + 1, 68, 52, f"background:{STRIPES},linear-gradient(180deg,#1A252C,#0D1418);clip-path:" + D.chamfer(4.6))
        o += terrain(n, tx + 8, ty + 6, 24, "#A9C7DE", 1.4)
        o += mod_chip(tx + 57, ty + 15, "move", mv) + mod_chip(tx + 57, ty + 39, "attack", at)
        o += D.label(tx + 6, ty + 38, {"deep": "Deep", "shallow": "Shallow", "fjords": "Fjords", "arctic": "Arctic"}[n], 7.5, D.LABEL, 42, track=0)
    # tabs (695 / 805 / 912, y 702)
    o += D.tab(695, 704, 113, 28, "Stats", True) + D.tab(805, 704, 113, 28, "History") + D.tab(912, 704, 113, 28, "Design")
    # the captain (1247, 339 ...) and the air wings (header 1247, 429; list 1247, 460, rows of 280 x 46)
    o += D.bar(1247, 341, 175, 28, c=5) + D.label(1259, 352, "Captain", 11, D.GILT, 120, track=.2)
    o += D.button(1425, 340, 90, 29, "Promote", size=11)
    o += D.box(1251, 372, 44, 50, "background:linear-gradient(180deg,#E8CD84,#8B6A2C);clip-path:polygon(0 8px,8px 0,36px 0,44px 8px,44px 50px,0 50px)")
    o += D.box(1252.5, 373.5, 41, 47, "clip-path:polygon(0 7px,7px 0,34px 0,41px 7px,41px 47px,0 47px);overflow:hidden", D.silhouette(0, 0, 41, 47))
    o += D.text(1306, 379, "Capt. Hélène d'Aurifort", 14, D.CREAM, 220, font="fed", track=.02)
    o += D.label(1306, 397, "Commanding officer", 9.5, D.LABEL, 200, track=.14)
    o += D.chevrons(1307, 409, 1, 11, D.GILT) + D.text(1323, 411, "Air Controller", 12, D.CREAM2, 140)
    o += D.bar(1247, 431, 270, 28, c=5) + D.label(1259, 442, "Air Wings", 11, D.GILT, 200, track=.2)
    o += D.value(1440, 441, "60 / 72", 13, D.CREAM, 70, "right")
    o += D.well(1247, 462, 286, 246)
    wings = [("jet", "1re Flottille de Chasse", "Gen 5 Carrier Fighter", "24", True),
             ("jet", "2e Flottille de Chasse", "Gen 5 Carrier Fighter", "24", False),
             ("jet", "Flottille d'Assaut", "Attack Drone", "12", False)]
    for i, (g, name, kind, n, ace) in enumerate(wings):
        yy = 466 + i * 46
        o += D.box(1251, yy, 278, 44, f"background:{STRIPES},linear-gradient(180deg,#18232A,#0F171C);box-shadow:inset 0 0 0 1px rgba(201,165,90,.35)")
        o += D.well(1257, yy + 9, 50, 26, c=3)
        o += f'<div class="a" style="left:1270px;top:{yy + 15}px">{D.unit_glyph(g, 25, "#E3C77E", 1.1)}</div>'
        o += D.text(1327, yy + 7, name, 13, D.CREAM, 160, weight=600)
        o += D.text(1327, yy + 25, f"{n} × {kind}", 12, D.LABEL, 170)
        if ace:
            o += D.box(1489, yy + 7, 30, 30, "background:radial-gradient(circle,#2C665A,#123029);border-radius:50%;box-shadow:0 0 0 1px #E3C77E")
            o += D.svg(1494, yy + 12, 20, 20, '<path d="M10 2.5l2 4.3 4.7.6-3.4 3.3.8 4.7L10 13.1l-4.1 2.3.8-4.7-3.4-3.3 4.7-.6z" fill="#F1DC9C" stroke="none"/>')
    return o


# ---------------------------------------------------------------- unit counters and map icons (mapicons.gui)
IDEO = {"democratic": "#3E6FA8", "communism": "#A8322C", "fascism": "#2A2A2A", "neutrality": "#80309F"}
SIDE_RIM = {"own": "#D2B064", "ally": "#8FB5A6", "enemy": "#C46A5A"}


def _chip(w, h, rim, fill, c=4):
    return (f'<div class="a" style="left:0;top:0;width:{w}px;height:{h}px;background:{rim};clip-path:{D.chamfer(c)}"></div>'
            f'<div class="a" style="left:1px;top:1px;width:{w - 2}px;height:{h - 2}px;background:{fill};clip-path:{D.chamfer(c - .4)}"></div>')


def counter(kind="motorized", n=2, tag="ROU", ideo="neutrality", frame=0, selected=False, org=1.0, strength=1.0,
            extras=(), side="own", glyph_color="#EBD397"):
    """the army counter (unit_counter, 76 x 24): count_bg (66 x 27, 3 frames: plain, hatched, pressed), the ideology
    corner (28 x 27 at 37, 0; 4 frames), the icon well (counter_overlay 30 x 20 at 3, 3) with the type icon and the
    small flag (5, 15), the count (36, 6; 20 wide), organisation and strength (assumed: under the well), the selection
    ring (68 x 28), and the small icons round it at the game's offsets"""
    rim = SIDE_RIM[side]
    fill = "linear-gradient(180deg,#22303A,#0E1519)" if frame != 2 else "linear-gradient(180deg,#2A3A44,#141E24)"
    o = '<div class="a" style="left:0;top:0;width:76px;height:27px;filter:drop-shadow(0 3px 3px rgba(0,0,0,.6))">'
    o += _chip(66, 27, rim, fill)
    if frame == 1:   # the game's hatched frame
        o += ('<div class="a" style="left:1px;top:1px;width:64px;height:25px;clip-path:' + D.chamfer(3.6) + ';'
              'background:repeating-linear-gradient(135deg,rgba(227,199,126,.22) 0 1px,transparent 1px 4px)"></div>')
    # the ideology pennant at the right end (x 58-64), a gilt hairline on its left
    o += (f'<div class="a" style="left:57px;top:1px;width:8px;height:25px;background:{IDEO[ideo]};'
          f'clip-path:polygon(0 0,4.6px 0,8px 3.4px,8px calc(100% - 3.4px),4.6px 100%,0 100%)"></div>'
          '<div class="a" style="left:57px;top:2px;width:1px;height:23px;background:rgba(227,199,126,.75)"></div>')
    # the number's well (x 34-56)
    o += ('<div class="a" style="left:34px;top:4px;width:22px;height:19px;background:#070B0E;box-shadow:inset 0 0 0 1px rgba(201,165,90,.35)"></div>'
          f'<div class="a" style="left:34px;top:5px;width:22px;font:700 14px/18px \'Josefin Sans\';text-align:center;color:#F4ECD9">{n}</div>')
    # the icon well (3, 3; 30 x 20), the type icon, the small flag (10 x 7 at 5, 15)
    o += '<div class="a" style="left:3px;top:3px;width:30px;height:20px;background:linear-gradient(180deg,#0E161B,#080C0F);box-shadow:inset 0 0 0 1px rgba(201,165,90,.3)"></div>'
    o += f'<div class="a" style="left:8px;top:4px">{D.unit_glyph(kind, 22, glyph_color, 1.3)}</div>'
    o += D.flag(tag, 5, 16, 10, 7, frame=False, style="box-shadow:0 0 0 1px rgba(0,0,0,.7)")
    # organisation (jade) and strength (amber) under the well (assumed placement: the game places them itself)
    o += (f'<div class="a" style="left:4px;top:23.5px;width:28px;height:1.5px;background:#0A0F12"></div>'
          f'<div class="a" style="left:4px;top:23.5px;width:{28 * org:.1f}px;height:1.5px;background:#5FC9A2"></div>'
          f'<div class="a" style="left:4px;top:25px;width:{28 * strength:.1f}px;height:1px;background:#E7B75A"></div>')
    if selected:
        o += ('<div class="a" style="left:-1px;top:-1px;width:68px;height:29px;background:#F1DC9C;clip-path:' + D.chamfer(4.6) + ';'
              '-webkit-mask:linear-gradient(#000,#000) content-box,linear-gradient(#000,#000);-webkit-mask-composite:xor;padding:1.5px"></div>'
              '<div class="a" style="left:-4px;top:-4px;width:74px;height:35px;border-radius:6px;box-shadow:0 0 8px 2px rgba(95,201,162,.75)"></div>')
    o += '</div>'
    for e in extras:
        if e == "hq":        # hq_badge (-20, 0; 18 x 27)
            o += ('<div class="a" style="left:-20px;top:0;width:18px;height:27px;background:linear-gradient(180deg,#E8CD84,#8B6A2C);clip-path:polygon(0 0,100% 0,100% 72%,50% 100%,0 72%)"></div>'
                  '<div class="a" style="left:-19px;top:1px;width:16px;height:24.5px;background:#121B21;clip-path:polygon(0 0,100% 0,100% 72%,50% 100%,0 72%)"></div>'
                  + D.svg(-17, 4, 12, 12, '<path d="M6 1l1.5 3.2 3.4.4-2.5 2.3.7 3.4L6 8.6 2.9 10.3l.7-3.4L1.1 4.6l3.4-.4z" fill="#F1DC9C" stroke="none"/>'))
        elif e == "move":    # onmap_action_icon (54, 7; 12 x 12), here the move order
            o += ('<div class="a" style="left:58px;top:-6px;width:14px;height:14px;border-radius:50%;background:#0B1014;box-shadow:0 0 0 1px #E3C77E"></div>'
                  + D.svg(60, -4, 10, 10, '<path d="M1.5 5h6M5 2l3 3-3 3" stroke="#F1DC9C" stroke-width="1.5"/>'))
        elif e == "attack":
            o += ('<div class="a" style="left:58px;top:-6px;width:14px;height:14px;border-radius:50%;background:#2A1210;box-shadow:0 0 0 1px #E8877A"></div>'
                  + D.svg(60, -4, 10, 10, '<path d="M2 8L8 2M5 2h3v3" stroke="#F5B8AD" stroke-width="1.5"/>'))
        elif e == "digin":   # onmap_digin_icon (56, 8; 8 x 11)
            o += ('<div class="a" style="left:58px;top:-6px;width:14px;height:14px;border-radius:50%;background:#0B1014;box-shadow:0 0 0 1px #E3C77E"></div>'
                  + D.svg(60, -4.5, 10, 11, '<path d="M5 1l3.6 1.4v3c0 2.5-1.6 4.3-3.6 5-2-.7-3.6-2.5-3.6-5v-3z" stroke="#F1DC9C" stroke-width="1.2"/><path d="M3 6.5h4" stroke="#F1DC9C" stroke-width="1"/>'))
        elif e == "training":
            o += ('<div class="a" style="left:58px;top:-6px;width:14px;height:14px;border-radius:50%;background:#0B1014;box-shadow:0 0 0 1px #9FCBE0"></div>'
                  + D.svg(60, -4, 10, 10, '<circle cx="5" cy="5" r="3.2" stroke="#BFE0EE" stroke-width="1.2"/><circle cx="5" cy="5" r="1" fill="#BFE0EE" stroke="none"/>'))
        elif e == "noorders":   # mapicon_unit_no_orders (-10, 8; 12 x 14)
            o += ('<div class="a" style="left:-11px;top:6px;width:10px;height:15px;background:#E7B75A;clip-path:polygon(50% 0,100% 30%,100% 70%,50% 100%,0 70%,0 30%)"></div>'
                  '<div class="a" style="left:-10px;top:7px;width:8px;height:13px;background:#1B140A;clip-path:polygon(50% 0,100% 30%,100% 70%,50% 100%,0 70%,0 30%)"></div>'
                  '<div class="a" style="left:-7px;top:9px;width:2px;height:6px;background:#E7B75A"></div><div class="a" style="left:-7px;top:16px;width:2px;height:2px;background:#E7B75A"></div>')
        elif e == "areadef":    # mapicon_area_defense_shield (-13, 6; 15 x 15)
            o += D.svg(-14, 6, 14, 15, '<path d="M7 1l5.6 2.1v4.2c0 3.8-2.4 6.5-5.6 7.6-3.2-1.1-5.6-3.8-5.6-7.6V3.1z" fill="#121B21" stroke="#E3C77E" stroke-width="1.2"/><path d="M7 4v8" stroke="#E3C77E" stroke-width="1"/>')
        elif e == "lowsupply":  # supply_strip (24, -4; 18 x 18 at .75), frame 3: out of supply
            o += ('<div class="a" style="left:25px;top:-9px;width:13px;height:13px;transform:rotate(45deg);background:#2A1210;box-shadow:0 0 0 1px #E8877A"></div>'
                  + D.svg(26.5, -7.5, 10, 10, '<path d="M1.5 3.5h5v4h-5zM6.5 5h1.6l1.4 1.4v1.1h-3" stroke="#F5B8AD" stroke-width="1"/>'))
        elif e == "attrition":
            o += ('<div class="a" style="left:-5px;top:-6px;width:13px;height:13px;border-radius:50%;background:#0B1014;box-shadow:0 0 0 1px #E8877A"></div>'
                  + D.svg(-3, -4, 9, 9, '<circle cx="4.5" cy="4" r="3" stroke="#F5B8AD" stroke-width="1"/><path d="M3 4.2h.1M6 4.2h.1M4.5 7v1.5" stroke="#F5B8AD" stroke-width="1.2"/>'))
    return o


def place(x, y, inner, w=76, h=27, scale=1):
    return (f'<div class="a" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;transform:scale({scale});transform-origin:0 0">'
            f'{inner}</div>')


def naval_counter(capitals=1, screens=4, tag="ROU", ideo="neutrality", mission="patrol", spot=.7, selected=False):
    """unit_counter_navy (66 x 33): count_bg 74 x 36 (3 frames), two icon wells (overlay_navy 30 x 29), the capital
    ships' count (32, 3) with its mark (59, 7), the screens' count (32, 18), the mission (63, 5; 26 x 26, 10 frames)
    and the spotting bar (65, 3; 6 x 29)"""
    o = '<div class="a" style="left:0;top:0;width:96px;height:36px;filter:drop-shadow(0 3px 3px rgba(0,0,0,.6))">'
    o += _chip(66, 36, SIDE_RIM["own"], "linear-gradient(180deg,#22303A,#0E1519)")
    o += ('<div class="a" style="left:3px;top:3px;width:30px;height:14px;background:#0A0F12;box-shadow:inset 0 0 0 1px rgba(201,165,90,.3)"></div>'
          '<div class="a" style="left:3px;top:18px;width:30px;height:14px;background:#0A0F12;box-shadow:inset 0 0 0 1px rgba(201,165,90,.3)"></div>')
    o += f'<div class="a" style="left:6px;top:4px">{D.unit_glyph("carrier", 24, "#EBD397", 1.2)}</div>'
    o += f'<div class="a" style="left:9px;top:18.5px">{D.unit_glyph("ship", 21, "#EBD397", 1.2)}</div>'
    for yy, nn in ((3, capitals), (18, screens)):
        o += f'<div class="a" style="left:33px;top:{yy}px;width:22px;height:14px;background:#070B0E;box-shadow:inset 0 0 0 1px rgba(201,165,90,.3)"></div>'
        o += f'<div class="a" style="left:33px;top:{yy + 1}px;width:22px;font:700 12.5px/13px \'Josefin Sans\';text-align:center;color:#F4ECD9">{nn}</div>'
    o += '<div class="a" style="left:57px;top:7px;width:5px;height:5px;transform:rotate(45deg);background:#F1DC9C"></div>'
    o += f'<div class="a" style="left:57px;top:15px;width:6px;height:18px;background:{IDEO[ideo]};box-shadow:0 0 0 1px rgba(227,199,126,.6)"></div>'
    o += D.flag(tag, 5, 25, 10, 7, frame=False, style="box-shadow:0 0 0 1px rgba(0,0,0,.7)")
    # the mission medallion (63, 5) and the spotting bar (65, 3 -> drawn just right of the chip)
    o += D.medallion(81, 18, 12.5, "intel" if mission == "patrol" else "swords", icon_size=13, lit=True)
    o += ('<div class="a" style="left:67px;top:3px;width:4px;height:29px;background:#0A0F12;box-shadow:0 0 0 1px rgba(201,165,90,.5)"></div>'
          f'<div class="a" style="left:67px;top:{3 + 29 * (1 - spot):.1f}px;width:4px;height:{29 * spot:.1f}px;background:linear-gradient(180deg,#A9C7DE,#40698B)"></div>')
    o += '</div>'
    return o


def air_counter(n=24, kind="jet", tag="ROU", mission=True):
    """air_wing_counter (58 x 27): the army counter's frame, the wing's type (3, 3; 30 x 12) and its count (21, 6; 50)"""
    o = '<div class="a" style="left:0;top:0;width:66px;height:27px;filter:drop-shadow(0 3px 3px rgba(0,0,0,.6))">'
    o += _chip(66, 27, "#A9C7DE", "linear-gradient(180deg,#1C2C38,#0C141B)")
    o += '<div class="a" style="left:3px;top:3px;width:30px;height:20px;background:#0A0F12;box-shadow:inset 0 0 0 1px rgba(169,199,222,.35)"></div>'
    o += f'<div class="a" style="left:6px;top:7px">{D.unit_glyph("jet", 24, "#D8E8F2", 1.1)}</div>'
    o += ('<div class="a" style="left:34px;top:4px;width:28px;height:19px;background:#070B0E;box-shadow:inset 0 0 0 1px rgba(169,199,222,.3)"></div>'
          f'<div class="a" style="left:34px;top:5px;width:28px;font:700 14px/18px \'Josefin Sans\';text-align:center;color:#F4ECD9">{n}</div>')
    o += f'<div class="a" style="left:4px;top:23.5px;width:28px;height:1.5px;background:#E7B75A"></div>'
    o += '</div>'
    return o


def land_battle_icon(progress=62, attacker_winning=True, bombard=False):
    """land_combat_mapicon (35 x 34): the round button (38 x 37 at -2, -2), its frame (2 frames), the progress (3, 16)
    and an air superiority mark (4, 8); here an octagon medallion with crossed swords, its inner ring split between the
    attacker's oxblood and the defender's slate by the battle's progress"""
    a = progress / 100
    o = '<div class="a" style="left:0;top:0;width:35px;height:34px;filter:drop-shadow(0 3px 4px rgba(0,0,0,.65))">'
    o += D.layer(D.octagon_pts(17.5, 17, 18), D.GOLD, 0, 0, 35, 34)
    o += D.layer(D.octagon_pts(17.5, 17, 16.6), "#0B1014", 0, 0, 35, 34)
    o += (f'<div class="a" style="left:3px;top:2.5px;width:29px;height:29px;border-radius:50%;'
          f'background:conic-gradient(#A9493A 0 {a * 360:.0f}deg,#40698B {a * 360:.0f}deg 360deg);'
          '-webkit-mask:radial-gradient(circle,transparent 11px,#000 11.5px,#000 14px,transparent 14.5px)"></div>')
    o += f'<div class="a" style="left:8.5px;top:8px">{D._icon("swords", 18, "#F1DC9C", 1.7)}</div>'
    o += ('<div class="a" style="left:3px;top:31px;width:30px;height:13px;background:#0B1014;clip-path:' + D.chamfer(3) + ';box-shadow:inset 0 0 0 1px #C9A55A"></div>'
          f'<div class="a" style="left:3px;top:32px;width:30px;font:700 10px/12px \'Josefin Sans\';text-align:center;color:{"#F5B8AD" if attacker_winning else "#BFD6E6"}">{progress}%</div>')
    if bombard:
        o += ('<div class="a" style="left:22px;top:-7px;width:15px;height:15px;transform:rotate(45deg);background:#0B1014;box-shadow:0 0 0 1px #A9C7DE"></div>'
              f'<div class="a" style="left:23.5px;top:-5.5px">{D._icon("air", 12, "#D8E8F2", 1.4)}</div>')
    o += '</div>'
    return o


def battle_arrow(cx, cy, ang, r=25, col="#E8877A"):
    """the battle's direction (battle_indicator_direction, 70 x 70): a gilt-edged chevron round the medallion"""
    return (f'<div class="a" style="left:{cx - 35}px;top:{cy - 35}px;width:70px;height:70px;transform:rotate({ang}deg)">'
            + D.svg(0, 0, 70, 70, f'<path d="M35 {35 - r - 5}l7 8M35 {35 - r - 5}l-7 8" stroke="{col}" stroke-width="2.6"/>'
                                  f'<path d="M35 {35 - r + 2}l5 6M35 {35 - r + 2}l-5 6" stroke="{col}" stroke-width="1.6" opacity=".7"/>')
            + '</div>')


def port_icon(level=6, cap="6/10"):
    """naval_base_mapicon: the base (27 x 29 at 4, 3; 11 frames, one per level), its capacity (36, 8)"""
    o = D.layer(D.octagon_pts(17.5, 17.5, 14), D.GOLD, 0, 0, 40, 40) + D.layer(D.octagon_pts(17.5, 17.5, 12.8), "linear-gradient(180deg,#18232B,#0B1014)", 0, 0, 40, 40)
    o += f'<div class="a" style="left:9.5px;top:8.5px">{D._icon("navy", 16, "#E3C77E", 1.6)}</div>'
    for i in range(10):
        o += f'<div class="a" style="left:{4 + i * 3}px;top:33px;width:2px;height:3px;background:{"#F1DC9C" if i < level else "#2A363D"}"></div>'
    o += (f'<div class="a" style="left:34px;top:9px;padding:2px 6px 1px;background:rgba(11,16,20,.85);box-shadow:inset 0 0 0 1px rgba(201,165,90,.5);'
          f'font:700 11px/12px \'Josefin Sans\';color:#F4ECD9;white-space:nowrap">{cap}</div>')
    return o


def air_base_icon(level=5, wings="48"):
    o = D.layer(D.octagon_pts(14, 14, 13.5), "linear-gradient(180deg,#BFD6E6,#5E7F99)", 0, 0, 40, 40)
    o += D.layer(D.octagon_pts(14, 14, 12.3), "linear-gradient(180deg,#18232B,#0B1014)", 0, 0, 40, 40)
    o += f'<div class="a" style="left:6px;top:6px">{D._icon("air", 16, "#D8E8F2", 1.4)}</div>'
    o += (f'<div class="a" style="left:32px;top:2px;padding:2px 6px 1px;background:rgba(11,16,20,.85);box-shadow:inset 0 0 0 1px rgba(169,199,222,.5);'
          f'font:700 11px/12px \'Josefin Sans\';color:#F4ECD9;white-space:nowrap">{wings}</div>')
    return o


def supply_hub_icon(val="20/20", ok=True):
    """supply_node_map_icon (36 x 36, 5 frames by state) and its value (52 x 32 under it)"""
    col = "#5FC9A2" if ok else "#E7B75A"
    o = (f'<div class="a" style="left:4px;top:4px;width:28px;height:28px;transform:rotate(45deg);background:{D.GOLD}"></div>'
         '<div class="a" style="left:5.5px;top:5.5px;width:25px;height:25px;transform:rotate(45deg);background:#0E1519"></div>'
         f'<div class="a" style="left:9px;top:9px;width:18px;height:18px;transform:rotate(45deg);box-shadow:inset 0 0 0 1px {col}"></div>'
         f'<div class="a" style="left:10px;top:10px">{D._icon("logistics", 16, "#F1DC9C", 1.4)}</div>')
    o += (f'<div class="a" style="left:-8px;top:35px;width:52px;height:16px;background:rgba(11,16,20,.9);clip-path:{D.chamfer(3)};box-shadow:inset 0 0 0 1px rgba(201,165,90,.6)"></div>'
          f'<div class="a" style="left:-8px;top:37px;width:52px;font:700 11px/13px \'Josefin Sans\';text-align:center;color:{col}">{val}</div>')
    return o


def naval_mission_icon(n="2/3", eff="86%"):
    """naval_mission_mapicon_entry (42 x 66): the mission button (46 x 50), its count (7, 33) and efficiency (7, 46)"""
    o = D.layer([(23, 1), (44, 12), (44, 38), (23, 49), (2, 38), (2, 12)], "linear-gradient(180deg,#BFD6E6,#5E7F99)", 0, 0, 46, 66)
    o += D.layer([(23, 2.6), (42.6, 12.8), (42.6, 37.2), (23, 47.4), (3.4, 37.2), (3.4, 12.8)], "linear-gradient(180deg,#18273A,#0B1220)", 0, 0, 46, 66)
    o += f'<div class="a" style="left:13px;top:8px">{D._icon("intel", 20, "#D8E8F2", 1.5)}</div>'
    o += f'<div class="a" style="left:7px;top:31px;width:32px;font:700 11px/12px \'Josefin Sans\';text-align:center;color:#F4ECD9">{n}</div>'
    o += (f'<div class="a" style="left:4px;top:49px;width:38px;height:14px;background:#0B1014;clip-path:{D.chamfer(3)};box-shadow:inset 0 0 0 1px rgba(169,199,222,.6)"></div>'
          f'<div class="a" style="left:4px;top:50px;width:38px;font:700 10px/12px \'Josefin Sans\';text-align:center;color:#BFD6E6">{eff}</div>')
    return o


def unit_counters():
    o = D.backdrop()
    # Rouental's divisions (the Royal Host and the levies) at war with Cardonia along the northern border
    own = [
        (500, 452, dict(kind="motorized", n=2), ()),
        (604, 446, dict(kind="armor", n=2, selected=True), ("hq",)),
        (692, 410, dict(kind="motorized", n=2), ("move",)),
        (790, 420, dict(kind="mechanized", n=1, org=.46, strength=.82), ("attack",)),
        (860, 446, dict(kind="motorized", n=2), ("digin",)),
        (650, 556, dict(kind="levy", n=1, org=.7), ("noorders", "lowsupply")),
        (760, 592, dict(kind="infantry", n=2), ("areadef",)),
        (470, 548, dict(kind="levy", n=3, org=.35), ("training",)),
        (1000, 434, dict(kind="infantry", n=1, org=.62, strength=.55), ("attack", "attrition")),
    ]
    for x, y, kw, ex in own:
        o += place(x, y, counter(extras=ex, **kw))
    # Cardonia's (the enemy's rim; hatched: the game's second frame)
    for x, y, kw in ((790, 328, dict(kind="infantry", n=3, org=.58)), (676, 338, dict(kind="infantry", n=2)),
                     (1000, 342, dict(kind="armor", n=1, org=.8)), (560, 352, dict(kind="motorized", n=1, frame=1))):
        o += place(x, y, counter(tag="CRD", ideo="neutrality", side="enemy", **kw))
    # battles between the attackers and the defenders north of them
    o += battle_arrow(817.5, 385, 0) + place(800, 368, land_battle_icon(62, True, bombard=True), 35, 34)
    o += battle_arrow(1032.5, 399, 0, col="#9FC0DA") + place(1015, 382, land_battle_icon(38, False), 35, 34)
    # the navy at sea south of Guedelon, the port, a naval mission over the sea region
    o += place(904, 772, naval_counter(), 96, 36)
    o += place(770, 706, port_icon(), 80, 40)
    o += place(1030, 830, naval_mission_icon(), 46, 66)
    return o


def unit_counters_key():
    """the same pieces three times as large, each named (a key for the author: not a screen of the game)"""
    S = 3
    o = D.backdrop(dim=.55, labels=False, top=False, blur=1.2)
    o += D.box(0, 0, D.W, D.H, "background:rgba(11,16,20,.55)")
    o += D.title(60, 40, "Unit counters and map icons", 30, track=.2)
    o += D.text(60, 84, "A key, three times the size the game draws them: each counter is the game's pieces at its paths, sizes and frames "
                "(mapicons.gui). Not a screen of the game.", 15, D.CREAM2, 1500, font="bod", weight=400)
    o += D.rule(60, 112, 1860)

    def cell(x, y, inner, w, h, name, sub):
        out = place(x, y, inner, w, h, S)
        out += D.label(x, y + h * S + 14, name, 11, D.GILT, 300, track=.16)
        out += D.text(x, y + h * S + 31, sub, 12, D.LABEL, 300, lh=1.25)
        return out
    y1 = 160
    items = [(counter(), "Own division", "count_bg frame 1, the ideology pennant (Monarchist), the type and the flag"),
             (counter(frame=1, tag="CRD", side="enemy"), "Frame 2 (hatched)", "the game's second frame; an enemy rim"),
             (counter(kind="armor", selected=True, extras=("hq",)), "Selected, army HQ", "the selection ring (68 x 28) and the HQ badge"),
             (counter(kind="levy", n=3, org=.35, strength=.6), "Worn down", "organisation (jade) and strength (amber) under the well"),
             (counter(kind="infantry", side="ally", tag="GDN", ideo="democratic"), "Ally (Guedelon)", "an ally's rim; the Democratic pennant")]
    for i, (inner, n, sub) in enumerate(items):
        o += cell(90 + i * 360, y1, inner, 76, 27, n, sub)
    y2 = 372
    marks = [("move", "Moving"), ("attack", "Attacking"), ("digin", "Dug in"), ("training", "Training"),
             ("noorders", "No orders"), ("areadef", "Area defence"), ("lowsupply", "Out of supply"), ("attrition", "Attrition")]
    for i, (e, n) in enumerate(marks):
        x = 90 + (i % 4) * 450 + (45 if e in ("noorders", "areadef", "attrition") else 0)
        y = y2 + (i // 4) * 168
        o += place(x, y, counter(kind="motorized", extras=(e,)), 76, 27, S)
        o += D.label(x, y + 98, n, 11, D.GILT, 220, track=.16)
    y3 = 748
    o += place(90, y3, naval_counter(), 96, 36, S) + D.label(90, y3 + 124, "Fleet", 11, D.GILT, 300, track=.16)
    o += D.text(90, y3 + 141, "capital ships over screens, the mission, spotting", 12, D.LABEL, 300)
    o += place(470, y3, air_counter(), 66, 27, S) + D.label(470, y3 + 96, "Air wing", 11, D.GILT, 300, track=.16)
    o += place(760, y3 - 10, land_battle_icon(62, True, True), 35, 34, S) + D.label(760, y3 + 130, "Land battle", 11, D.GILT, 220, track=.16)
    o += D.text(760, y3 + 147, "the ring shows who is winning", 12, D.LABEL, 230)
    o += place(1010, y3 - 4, port_icon(), 80, 40, S) + D.label(1010, y3 + 124, "Naval base", 11, D.GILT, 220, track=.16)
    o += place(1340, y3 - 4, air_base_icon(), 80, 40, S) + D.label(1340, y3 + 124, "Air base", 11, D.GILT, 220, track=.16)
    o += place(1640, y3 - 10, supply_hub_icon(), 52, 56, S) + D.label(1610, y3 + 160, "Supply hub", 11, D.GILT, 220, track=.16)
    return o


# ---------------------------------------------------------------- the Deco UI's army bar (its own textures), for context
MODGFX = os.path.join(D.DECO, "valsora_deco_ui", "gfx", "interface", "unitcontrol")


def _frame_of(path, i, n):
    from PIL import Image
    im = Image.open(path).convert("RGBA")
    fw = im.width // n
    return im.crop((i * fw, 0, (i + 1) * fw, im.height))


def _tex(path, i, n, x, y):
    im = _frame_of(path, i, n)
    return f'<img class="a" src="{D.uri_of(im)}" style="left:{x}px;top:{y}px;width:{im.width}px;height:{im.height}px">'


def army_bar(cards, x0=100, y0=980):
    """the army bar as the Deco UI draws it (leadergroups.gui, its lg_ textures): cards of (portrait or None, count,
    selected, playing)"""
    o = ""
    for i, (who, n, sel, play) in enumerate(cards):
        x = x0 + i * 84
        last = i == len(cards) - 1
        o += _tex(os.path.join(MODGFX, "army_end_bg.dds" if last else "army_mid_bg.dds"), 1 if sel else 0, 2, x + 1, y0 - 46)
    for i, (who, n, sel, play) in enumerate(cards):
        x = x0 + i * 84
        o += _tex(os.path.join(MODGFX, "execute_stop_small_bg.dds"), 0, 1, x, y0 - 34) if os.path.isfile(os.path.join(MODGFX, "execute_stop_small_bg.dds")) else ""
        o += _tex(os.path.join(MODGFX, "execute_btn_stop_small.dds"), 0, 4, x + 2, y0 - 32)
        o += _tex(os.path.join(MODGFX, "execute_btn_play_small.dds"), 2 if play else 0, 4, x + 32, y0 - 32)
        if who:
            o += D.portrait(who, x + 8, y0 - 3, 59, 80)
        else:
            o += D.silhouette(x + 8, y0 - 3, 59, 80)
        o += _tex(os.path.join(MODGFX, "leader_group_frame.dds"), 1 if sel else 0, 4, x - 1, y0 - 12)
        o += D.text(x + 5, y0 + 80, str(n), 15, "#F4ECD9", 74, "center", weight=700)
    return o


# ---------------------------------------------------------------- commander abilities (abilitylist.gui)
ABILITY_GLYPH = {
    "force_attack": '<path d="M4 20L16 8M12 6h6v6"/><path d="M4 14l4 4"/>',
    "last_stand": '<path d="M12 3l7 2.6v5.4c0 4.6-3 8.1-7 9.6-4-1.5-7-5-7-9.6V5.6z"/><path d="M9 11h6M12 8v8"/>',
    "staff_plan": '<path d="M5 4h14v16H5z"/><path d="M8 8h8M8 11.5h8M8 15h5"/><path d="M15 17l1.5 1.5L19 15"/>',
    "siege": '<path d="M3 17h12l3-6"/><path d="M7 17v-3h6v3"/><circle cx="7" cy="19" r="1.6"/><circle cx="13" cy="19" r="1.6"/><path d="M18 11l3-5"/>',
    "supplies": '<path d="M4 9l8-4 8 4-8 4z"/><path d="M4 9v7l8 4 8-4V9M12 13v7"/>',
    "probe": '<circle cx="10" cy="10" r="5.5"/><path d="M14 14l6 6"/><path d="M8 10h4M10 8v4"/>',
}


def ability_slot(cx, top, glyph, state="ready", frac=0):
    """an ability's button (33 x 33 picture at -8, -3 of its 36 x 80 container) over its active or cooldown ring"""
    o = ""
    if state == "active":
        o += (f'<div class="a" style="left:{cx - 21}px;top:{top - 4}px;width:42px;height:42px;border-radius:50%;'
              f'background:conic-gradient(#5FC9A2 0 {frac * 360:.0f}deg,rgba(95,201,162,.15) {frac * 360:.0f}deg 360deg);'
              '-webkit-mask:radial-gradient(circle,transparent 17px,#000 17.5px)"></div>')
    o += D.layer(D.octagon_pts(cx, top + 17, 17), D.GOLD if state != "cooldown" else "linear-gradient(180deg,#8E7A4E,#4E3F22)")
    o += D.layer(D.octagon_pts(cx, top + 17, 15.6), "radial-gradient(circle at 50% 35%,#2C665A,#123029 80%)" if state == "active"
                 else "radial-gradient(circle at 50% 35%,#1A262E,#0B1014 75%)")
    col = "#FBEAB4" if state == "active" else ("rgba(227,199,126,.45)" if state == "cooldown" else "#E3C77E")
    o += D.svg(cx - 10, top + 7, 20, 20, f'<g stroke="{col}" stroke-width="1.6">{ABILITY_GLYPH[glyph]}</g>', "0 0 24 24")
    if state == "cooldown":
        o += (f'<div class="a" style="left:{cx - 15}px;top:{top + 2}px;width:30px;height:30px;border-radius:50%;'
              f'background:conic-gradient(rgba(11,16,20,.75) 0 {frac * 360:.0f}deg,transparent {frac * 360:.0f}deg 360deg)"></div>')
    return o


def abilities():
    o = D.backdrop()
    o += place(604, 446, counter(kind="armor", n=2, selected=True, extras=("hq",)))
    o += army_bar([("serelle_cahun", 12, True, True), (None, 8, False, False), (None, 6, False, False)])
    # abilitylist_window: centre-down (-5, -99), 165 x 80; bg_begin (99 x 45) at 0, a 36 px middle per extra ability,
    # bg_end; the buttons from (37, 11), 36 apart
    ab = [("force_attack", "active", .35), ("last_stand", "ready", 0), ("staff_plan", "ready", 0), ("siege", "cooldown", .6),
          ("supplies", "ready", 0), ("probe", "ready", 0)]
    n = len(ab)
    wbar = 99 * 2 + 36 * (n - 2)
    x0 = 955      # the window's left edge (centre-down, x -5); the game grows the list to the right
    y0 = 981
    o += D.box(x0, y0, wbar, 45, f"background:{D.GILT};clip-path:polygon(14px 0,calc(100% - 14px) 0,100% 14px,100% 100%,0 100%,0 14px);opacity:.75")
    o += D.box(x0 + 1, y0 + 1, wbar - 2, 44, f"background:{D.STRIPES},linear-gradient(180deg,#1C2830,#0E1519);clip-path:polygon(13.6px 0,calc(100% - 13.6px) 0,100% 13.6px,100% 100%,0 100%,0 13.6px)")
    o += D.box(x0 + 16, y0 + 3, wbar - 32, 1, "background:rgba(241,220,156,.3)")
    o += D.diamond(x0 + 8, y0 + 26, 5) + D.diamond(x0 + wbar - 8, y0 + 26, 5)
    for i, (g, st, fr) in enumerate(ab):
        cx = x0 + 37 - 8 + 16.5 + i * 36 + (wbar - (36 * n + 58)) / 2
        o += ability_slot(cx, y0 + 6, g, st, fr)
    # the tooltip over the active ability
    o += D.tooltip(x0 - 70, 776, 330, 186, "Force Attack",
                   [("Command power", "0.22 / div. / day", "#E7B75A"), ("Attack", "+10%", D.POS),
                    ("Organisation damage taken", "+15%", D.NEG), ("Active for", "4 days left", D.CREAM)],
                   "Press the attack whatever the cost: the Garde will not be the first to give ground.")
    return o


# ---------------------------------------------------------------- the right-click menu (rightclickmenu.gui)
def right_click_menu():
    o = D.backdrop()
    o += place(604, 446, counter(kind="armor", n=2, selected=True, extras=("hq",)))
    # the click: a ring where the player clicked, the menu's list (120 wide; entries 250 x 25, their button at 26)
    cx, cy = 820, 520
    o += D.box(cx - 9, cy - 9, 18, 18, "border-radius:50%;box-shadow:0 0 0 1.5px #F1DC9C,0 0 8px rgba(241,220,156,.6)")
    x, y = cx + 8, cy + 6
    entries = [("Move to Saintiers", False, False), ("Support attack", False, False), ("Strategic redeployment", False, True),
               ("Vale of Reibonne", True, False), ("Rêverie Air Base", True, False)]
    h = 25 * len(entries) + 16
    o += D.window(x + 25, y, 300, h, "single", "small")
    for i, (s, opener, disabled) in enumerate(entries):
        ey = y + 8 + i * 25
        hover = i == 0
        o += D.box(x + 26 + 7, ey, 250 - 8, 23, f"background:{'linear-gradient(90deg,rgba(46,110,96,.55),rgba(46,110,96,.15))' if hover else 'transparent'};"
                                               f"{'box-shadow:inset 2px 0 0 #F1DC9C' if hover else ''}")
        col = "rgba(227,199,126,.4)" if disabled else ("#FBEAB4" if hover else D.CREAM)
        o += D.diamond(x + 44, ey + 11.5, 5, "#F1DC9C" if hover else ("rgba(201,165,90,.35)" if disabled else D.RULE))
        o += D.text(x + 56, ey + 6, s, 14, col, 200, font="fed", track=.02)
        if opener:
            o += D.button(x + 237 + 26, ey + 1, 52, 21, "Open", size=10)
    return o


# ---------------------------------------------------------------- theatres (theatreselector.gui)
def theatre_entry(x, y, name, n, prio, alerts=(), pinned=False, selected=False):
    """theatre_selection_entry (450 x 65): the button (198 x 39 at 260), its frame (184 x 47), the name (278, 6;
    120 x 36), the units' count (400, 8; 37 x 34), the pin (439, 6), the priority (318, 42; three of 20 x 21), alerts
    to the left (125-255)"""
    o = ""
    bx = x + 260
    o += (D.lit_bar(bx, y, 198, 39, 6) if selected else D.bar(bx, y, 198, 39, c=6))
    o += D.text(x + 270, y + 7, name, 14, "#FBEAB4" if selected else D.CREAM, 124, "center", font="fed", track=.03, lh=1.05, h=28, valign=True)
    o += D.layer(D.octagon_pts(x + 418.5, y + 19.5, 16), D.GOLD) + D.layer(D.octagon_pts(x + 418.5, y + 19.5, 14.6), "linear-gradient(180deg,#1C2830,#0B1014)")
    o += D.value(x + 400, y + 13, str(n), 15, D.CREAM, 37, "center")
    o += D.svg(x + 461, y + 9, 14, 26, f'<path d="M7 2v13M3 6l4-4 4 4M4 15h6l-1 8H5z" stroke="{"#F1DC9C" if pinned else "rgba(201,165,90,.45)"}" stroke-width="1.4"/>')
    o += D.box(x + 318, y + 41, 75, 17, f"background:#0B1014;clip-path:{D.chamfer(4)};box-shadow:inset 0 0 0 1px rgba(201,165,90,.5)")
    for i in range(3):
        on = i < prio
        o += D.diamond(x + 335 + i * 20, y + 49.5, 8, "#E7B75A" if on else "#2A363D", "box-shadow:0 0 0 1px rgba(11,16,20,.9)")
    for i, a in enumerate(alerts):
        ax = x + 255 - (i + 1) * 30
        o += alert_chip(ax, y + 2, a)
    return o


def alert_chip(x, y, kind):
    col = {"orders": "#E7B75A", "supply": "#E8877A", "battle": "#E8877A", "hq": "#E7B75A"}[kind]
    glyph = {"orders": '<path d="M12 5v8M12 17v1"/>', "supply": '<path d="M4 8h10v7H4zM14 10h3.5l2.5 2.5V15H14"/><circle cx="7" cy="17" r="1.5"/><circle cx="17" cy="17" r="1.5"/>',
             "battle": D.ICONS["swords"], "hq": '<path d="M12 4l2 4.3 4.6.6-3.3 3.2.8 4.6L12 14.4l-4.1 2.3.8-4.6L5.4 8.9 10 8.3z"/>'}[kind]
    return (D.box(x, y, 26, 34, f"background:{col};clip-path:polygon(0 0,100% 0,100% 78%,50% 100%,0 78%)")
            + D.box(x + 1, y + 1, 24, 31.5, "background:#120D08;clip-path:polygon(0 0,100% 0,100% 78%,50% 100%,0 78%)")
            + D.svg(x + 4, y + 5, 18, 18, f'<g stroke="{col}" stroke-width="2">{glyph}</g>', "0 0 24 24"))


def army_shield(x, y, num, sel=False):
    """an army's insignia (orders_group_item, 33 x 32): the game's are pictures; here a gilt heater shield with its number"""
    return (D.svg(x, y, 26, 30, f'<path d="M13 1.5l10.5 3.6v8c0 6.8-4.6 11.6-10.5 14-5.9-2.4-10.5-7.2-10.5-14v-8z" fill="{"#123029" if sel else "#121B21"}" '
                                 f'stroke="{"#F1DC9C" if sel else "#C9A55A"}" stroke-width="1.4"/>')
            + D.text(x, y + 8, num, 11, "#F1DC9C", 26, "center", font="fed"))


def theatres():
    o = D.backdrop()
    # theatre_selection_window: UPPER_RIGHT (-760, 117), 760 x (screen - 240); the entries' grid at (2, 3)
    gx, gy = 1162, 120
    o += theatre_entry(gx, gy, "The Vale of Reibonne", 24, 3, ("orders", "battle"), pinned=True, selected=True)
    # the selected theatre's army groups (theater_group_item, 305 x 77, under it, right-aligned)
    ty = gy + 66
    for gi, (name, n, armies, atk, dfn) in enumerate((("Ost du Nord", 16, ["I", "II", "III"], 3, 1), ("Ost du Levant", 8, ["IV", "V"], 0, 2))):
        x = gx + 458 - 305
        y = ty + gi * 84
        o += D.box(x, y, 305, 77, "", D.window(0, 0, 305, 77, "single", "small", shadow=False).replace("left:0px;top:0px", "left:0;top:0"))
        o += D.button(x + 9, y + 11, 23, 23, "", icon=None) + D.svg(x + 13, y + 15, 15, 15, '<circle cx="7.5" cy="7.5" r="2.4" stroke="#E3C77E" stroke-width="1.3"/><path d="M7.5 1.5v2.2M7.5 11.3v2.2M1.5 7.5h2.2M11.3 7.5h2.2M3.3 3.3l1.6 1.6M10.1 10.1l1.6 1.6M3.3 11.7l1.6-1.6M10.1 4.9l1.6-1.6" stroke="#E3C77E" stroke-width="1.3"/>')
        o += D.text(x + 40, y + 15, name, 15, D.CREAM, 140, font="fed", track=.04)
        o += D.chevrons(x + 183, y + 12, 3 - gi, 10, "#E7B75A")
        # battles: attacking (swords) and defending (shield) counts, the combat log
        o += D.ico("swords", x + 232, y + 13, 16, "#E8877A", 1.6) + D.value(x + 250, y + 15, str(atk), 13, D.CREAM, 20)
        o += D.ico("shield", x + 266, y + 13, 16, "#9FC0DA", 1.6) + D.value(x + 284, y + 15, str(dfn), 13, D.CREAM, 20)
        o += D.rule(x + 8, y + 42, x + 297, "rgba(201,165,90,.35)")
        for ai, a in enumerate(armies):
            o += army_shield(x + 12 + ai * 30, y + 46, a, sel=(gi == 0 and ai == 0))
        o += D.value(x + 256, y + 55, f"{n}", 14, D.CREAM, 40, "right")
        o += D.label(x + 200, y + 57, "Divisions", 8.5, D.LABEL, 56, track=.1)
    y = ty + 2 * 84 + 4
    o += D.button(gx + 458 - 305, y, 303, 30, "+ New army group", size=11)
    y += 44
    o += theatre_entry(gx, y, "Linterre and Selto", 6, 2, ("supply",))
    o += theatre_entry(gx, y + 66, "The Abalonese Coast", 4, 1, ())
    o += theatre_entry(gx, y + 132, "Midtierre Sea", 9, 2, ("hq",))
    # the selection: Serelle's army chosen in the theatre: the army bar and its counters
    o += army_bar([("serelle_cahun", 12, True, True), (None, 8, False, False), (None, 6, False, False)])
    o += place(604, 446, counter(kind="armor", n=2, selected=True, extras=("hq",)))
    return o
