"""The designers' and the commander pickers' background pictures (v0.9), in the deco style at the game's paths and sizes.

The game draws each designer (division, tank, plane, ship) and each commander picker on one large picture: a header
band, plates and recessed panels where its lists and pictures go, a ruled sheet where it writes the statistics in dark
text, a footer band. The panels' places are the game's, measured from its own pictures (they have to lie under what the
game draws on them); everything else is drawn here: lacquer plates with gilt hairlines, recessed lacquer panels, an
ivory sheet ruled in sepia (it stays light: the game's text on it is dark), gilt corner brackets, and on the division
designer a sunburst and diamond in place of the game's eagle. The commander cards stay parchment-light for the same
reason, with a gilt rim, a lacquer portrait well and an emblem strip in the card's colour.

gen_textures.py adds them (keys dsg_* and ldr_*); validate_preview.py holds them to the game's sizes.
"""
LAC = "repeating-linear-gradient(90deg,rgba(255,255,255,.025) 0 1px,transparent 1px 7px)"
GILT = "#C9A55A"

from icons import icon as _icon  # noqa: E402
GILT_SOFT = "rgba(201,165,90,.55)"


def _poly(pts):
    return "polygon(" + ",".join(f"{x}px {y}px" for x, y in pts) + ")"


def _rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def _shrink(pts, d):
    """an orthogonal or 45-degree polygon moved d px inward (each edge offset along its inward normal)"""
    import math
    n = len(pts)
    area = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))
    s = 1 if area > 0 else -1
    lines = []
    for i in range(n):
        (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % n]
        dx, dy = x2 - x1, y2 - y1
        ln = math.hypot(dx, dy)
        lines.append(((x1 - dy / ln * s * d, y1 + dx / ln * s * d), (dx, dy)))
    out = []
    for i in range(n):
        (p1, d1), (p2, d2) = lines[i - 1], lines[i]
        den = d1[0] * d2[1] - d1[1] * d2[0]
        if abs(den) < 1e-9:
            out.append(p2)
            continue
        t = ((p2[0] - p1[0]) * d2[1] - (p2[1] - p1[1]) * d2[0]) / den
        out.append((round(p1[0] + d1[0] * t, 2), round(p1[1] + d1[1] * t, 2)))
    return out


def _layer(pts, background):
    return f'<div style="position:absolute;inset:0;background:{background};clip-path:{_poly(pts)}"></div>'


def frame_base(w, h):
    """the whole picture: lacquer, a double gilt rule round it, gilt corner brackets"""
    return (f'<div style="position:absolute;inset:0;background:{LAC},linear-gradient(180deg,#141E24,#0D1418)"></div>'
            '<div style="position:absolute;inset:0;box-shadow:inset 0 0 0 1px rgba(0,0,0,.7)"></div>'
            f'<div style="position:absolute;inset:1px;border:1px solid #B8954F"></div>'
            f'<div style="position:absolute;inset:5px;border:1px solid rgba(201,165,90,.4)"></div>'
            '<i class="ck tl"></i><i class="ck tr"></i><i class="ck bl"></i><i class="ck br"></i>')


def band(x0, y0, x1, y1):
    """a raised lacquer plate: a gilt hairline along its top, a shadow under it"""
    return (_layer(_rect(x0, y0, x1, y1), f"{LAC},linear-gradient(180deg,#1C2830,#131C22)")
            + f'<div style="position:absolute;left:{x0}px;top:{y0}px;width:{x1 - x0}px;height:1px;background:rgba(227,199,126,.38)"></div>'
            + f'<div style="position:absolute;left:{x0}px;top:{y1 - 1}px;width:{x1 - x0}px;height:1px;background:rgba(0,0,0,.65)"></div>')


def inset(pts, fill="linear-gradient(180deg,#0B1115,#080C0F)", rim=GILT_SOFT):
    """a recessed panel: a gilt hairline round it, darker lacquer inside, a soft shadow along its top"""
    if len(pts) == 4 and isinstance(pts[0], (int, float)):
        pts = _rect(*pts)
    return (_layer(pts, rim) + _layer(_shrink(pts, 1), f"{LAC},{fill}")
            + _layer(_shrink(pts, 1), "linear-gradient(180deg,rgba(0,0,0,.35),rgba(0,0,0,0) 14px)"))


def gilt_line(x0, y0, x1, y1, color=GILT, t=1):
    if y0 == y1:
        return f'<div style="position:absolute;left:{x0}px;top:{y0}px;width:{x1 - x0}px;height:{t}px;background:{color}"></div>'
    return f'<div style="position:absolute;left:{x0}px;top:{y0}px;width:{t}px;height:{y1 - y0}px;background:{color}"></div>'


def sheet(x0, y0, x1, y1, head, cols, rows):
    """the ruled ivory sheet the game writes its statistics on: a header row (head = its bottom y), column rules at
    the x pairs in cols, dotted row rules at the y's in rows"""
    out = (f'<div style="position:absolute;left:{x0 - 1}px;top:{y0 - 1}px;width:{x1 - x0 + 2}px;height:{y1 - y0 + 2}px;background:#9C7A36"></div>'
           f'<div style="position:absolute;left:{x0}px;top:{y0}px;width:{x1 - x0}px;height:{y1 - y0}px;'
           'background:radial-gradient(ellipse at 30% 20%,rgba(255,250,235,.55),rgba(255,250,235,0) 60%),linear-gradient(180deg,#EFE6CE,#E2D5B2)"></div>'
           f'<div style="position:absolute;left:{x0}px;top:{y0}px;width:{x1 - x0}px;height:{head - y0}px;background:linear-gradient(180deg,#DCCCA2,#D2C094)"></div>'
           + gilt_line(x0, head, x1, head, "#9C7A36") + gilt_line(x0, head + 2, x1, head + 2, "rgba(156,122,54,.45)"))
    for a, b in cols:
        out += gilt_line(a + (b - a) // 2, y0, a + (b - a) // 2 + 1, y1, "rgba(156,122,54,.7)")
    for y in rows:
        out += (f'<div style="position:absolute;left:{x0 + 4}px;top:{y}px;width:{x1 - x0 - 8}px;height:2px;'
                'background-image:radial-gradient(circle,rgba(92,70,32,.55) 0.75px,transparent 0.95px);background-size:4px 2px"></div>')
    return out


def ornament(cx, cy, span):
    """the division designer's centre piece: a gilt ring (the game's toggle sits in it), speed-line wings, a sunburst"""
    out = (f'<div style="position:absolute;left:{cx - 44}px;top:{cy - 44}px;width:88px;height:88px;border-radius:50%;'
           'background:repeating-conic-gradient(rgba(227,199,126,.22) 0deg 3deg,transparent 3deg 11deg);'
           '-webkit-mask:radial-gradient(circle,#000 30%,transparent 70%)"></div>')
    for dy, ln in [(-6, span), (0, span - 22), (6, span - 44)]:
        for side in (0, 1):
            x = cx - 24 - ln if side == 0 else cx + 24
            grad = "90deg,rgba(201,165,90,0),#C9A55A" if side == 0 else "90deg,#C9A55A,rgba(201,165,90,0)"
            out += f'<div style="position:absolute;left:{x}px;top:{cy + dy}px;width:{ln}px;height:1px;background:linear-gradient({grad})"></div>'
    for side in (-1, 1):
        out += (f'<div style="position:absolute;left:{cx + side * 30 - 4}px;top:{cy - 4}px;width:8px;height:8px;'
                'background:#E3C77E;transform:rotate(45deg)"></div>')
    out += (f'<div style="position:absolute;left:{cx - 17}px;top:{cy - 17}px;width:34px;height:34px;border-radius:50%;'
            'background:radial-gradient(circle,#0B1014 60%,#16212A);box-shadow:0 0 0 1.5px #C9A55A,0 0 0 4px rgba(11,16,20,.9),0 0 0 5px rgba(201,165,90,.45)"></div>')
    return out


def header(w, y1, close_x=None):
    """the title band along the top, and the socket the game's close button sits in"""
    out = band(6, 6, w - 6, y1) + gilt_line(6, y1, w - 6, y1)
    if close_x:
        out += inset((close_x, 9, close_x + 44, y1 - 3), "linear-gradient(180deg,#0E1519,#0A0F12)", "rgba(201,165,90,.7)")
    return out


def footer(w, y0, y1):
    return gilt_line(6, y0, w - 6, y0) + band(6, y0 + 2, w - 6, y1)


# ---------------------------------------------------------------- the designers
def tank_like(w=1092, h=553):
    """the tank and plane designers (the same layout): name plate with a tab, the vehicle's panel, the sheet, the
    stepped panel under it"""
    return (frame_base(w, h) + header(w, 43)
            + band(13, 44, 525, 144) + band(456, 144, 525, 194)
            + inset([(13, 144), (456, 144), (456, 194), (525, 194), (525, 493), (13, 493)])
            + gilt_line(529, 46, 529, 493, "rgba(201,165,90,.35)")
            + sheet(546, 46, 1063, 231, 68, [(715, 718), (890, 893)], [90, 110, 130, 150, 170, 190, 210])
            + inset([(535, 241), (744, 241), (763, 260), (1064, 260), (1064, 493), (535, 493)])
            + footer(w, 494, 541))


def ship(w=1092, h=553):
    return (frame_base(w, h) + header(w, 43)
            + band(13, 44, 525, 140)
            + inset((13, 140, 267, 224), "linear-gradient(180deg,#121B21,#0C1216)") + inset((270, 140, 525, 224), "linear-gradient(180deg,#121B21,#0C1216)")
            + gilt_line(54, 225, 481, 225, "rgba(201,165,90,.6)")
            + inset((13, 227, 525, 493))
            + inset((13, 231, 98, 487), "linear-gradient(180deg,#06090B,#040607)")
            + gilt_line(529, 46, 529, 493, "rgba(201,165,90,.35)")
            + sheet(546, 46, 1063, 307, 67, [(714, 719), (889, 894)], [89 + 20 * k for k in range(11)])
            + inset([(535, 319), (737, 319), (756, 338), (1066, 338), (1066, 493), (535, 493)], "linear-gradient(180deg,#142029,#0D161C)")
            + footer(w, 494, 541))


def division(w=1200, h=720):
    cols = [36, 138, 240, 342, 444]
    lines = gilt_line(37, 277, 584, 277, "rgba(201,165,90,.75)") + gilt_line(309, 266, 309, 277, "rgba(201,165,90,.75)")
    for x in cols:
        lines += gilt_line(x, 277, x, 550, "rgba(201,165,90,.6)") + gilt_line(x, 549, x + 20, 549, "rgba(201,165,90,.6)")
    lines += gilt_line(583, 277, 583, 288, "rgba(201,165,90,.75)")
    return (frame_base(w, h) + header(w, 40)
            + band(16, 45, 644, 97) + band(16, 99, 644, 155) + band(16, 157, 644, 181) + band(16, 184, 644, 222)
            + inset((12, 224, 647, 608), "linear-gradient(180deg,#10181D,#0A0F12)")
            + ornament(309, 249, 120) + lines
            + inset((543, 288, 625, 502), "linear-gradient(180deg,#06090B,#040607)")
            + inset((46, 527, 536, 594), "linear-gradient(180deg,#06090B,#040607)")
            + gilt_line(652, 46, 652, 608, "rgba(201,165,90,.35)")
            + sheet(668, 47, 1186, 310, 68, [(837, 840), (1012, 1015)], [90 + 20 * k for k in range(10)])
            + band(658, 320, 1187, 356)
            + inset((667, 366, 910, 606), "linear-gradient(180deg,#14221E,#0D1714)") + inset((933, 366, 1167, 606))
            + footer(w, 612, 660) + band(12, 663, w - 12, 706))


# ---------------------------------------------------------------- the commander pickers
def leader_window(w=550, h=607):
    return (frame_base(w, h) + header(w, 36) + band(9, 37, 524, 70)
            + inset((180, 41, 316, 66), "linear-gradient(180deg,#0B1115,#080C0F)", "rgba(201,165,90,.75)")
            # the search glass, where the game's picture has it: the search text starts right of it (x 201)
            + f'<div style="position:absolute;left:183px;top:45px">{_icon("search", 16, "#C9A55A", 1.6)}</div>'
            + inset((9, 71, 524, 544)) + footer(w, 546, 597))


def leader_card(stripe, stone=False, w=510, h=98):
    """a commander's card: emblem strip, portrait well, the parchment body with the name's dotted line and the box at
    its top right (the game's)"""
    body = ("linear-gradient(180deg,#E6E1D6,#CFC9BB)" if stone else "linear-gradient(180deg,#F0E6CC,#E1D2AC)")
    s1, s2 = stripe
    return (f'<div style="position:absolute;left:0;top:1px;width:{w}px;height:{h - 2}px;background:#9C7A36"></div>'
            f'<div style="position:absolute;left:1px;top:2px;width:{w - 2}px;height:{h - 4}px;background:{body}"></div>'
            f'<div style="position:absolute;left:1px;top:2px;width:54px;height:{h - 4}px;'
            f'background:repeating-linear-gradient(90deg,{s1} 0 6px,{s2} 6px 12px)"></div>'
            '<div style="position:absolute;left:19px;top:40px;width:16px;height:16px;background:#E3C77E;transform:rotate(45deg);'
            'box-shadow:0 0 0 2px rgba(11,16,20,.55)"></div>'
            f'<div style="position:absolute;left:55px;top:2px;width:1px;height:{h - 4}px;background:#C9A55A"></div>'
            f'<div style="position:absolute;left:56px;top:2px;width:64px;height:{h - 4}px;background:linear-gradient(180deg,#16212A,#0B1014)"></div>'
            f'<div style="position:absolute;left:120px;top:2px;width:1px;height:{h - 4}px;background:#C9A55A"></div>'
            f'<div style="position:absolute;left:300px;top:2px;width:{w - 301}px;height:{h - 4}px;background:linear-gradient(90deg,rgba(120,90,40,0),rgba(120,90,40,.10))"></div>'
            '<div style="position:absolute;left:126px;top:47px;width:170px;height:2px;'
            'background-image:radial-gradient(circle,rgba(92,70,32,.6) 0.75px,transparent 0.95px);background-size:4px 2px"></div>'
            '<div style="position:absolute;left:435px;top:15px;width:63px;height:23px;background:rgba(60,45,20,.16);'
            'box-shadow:inset 0 0 0 1px rgba(156,122,54,.55)"></div>'
            '<i class="ck sm tl"></i><i class="ck sm tr"></i><i class="ck sm bl"></i><i class="ck sm br"></i>')


ADDS = [
    ("dsg_division", "gfx/interface/division_designer_popup_bg_new.dds", 1200, 720, division),
    ("dsg_tank", "gfx/interface/equipmentdesigner/tanks/tank_designer_popup_bg.dds", 1092, 553, tank_like),
    ("dsg_plane", "gfx/interface/equipmentdesigner/planes/plane_designer_popup_bg.dds", 1092, 553, tank_like),
    ("dsg_ship", "gfx/interface/equipmentdesigner/ship_designer_popup_bg.dds", 1092, 553, ship),
    ("ldr_window", "gfx/interface/leader_selection_bg.dds", 550, 607, leader_window),
    ("ldr_card", "gfx/interface/leader_selection_entry_bg.dds", 510, 98, lambda: leader_card(("#7A2E26", "#9A4A3A"))),
    ("ldr_card_navy", "gfx/interface/naval_leader_selection_entry_bg.dds", 510, 98, lambda: leader_card(("#2C4256", "#476178"))),
    ("ldr_card_captured", "gfx/interface/marshal_captured_bg.dds", 510, 98, lambda: leader_card(("#6E6A62", "#8E877C"), stone=True)),
]
