"""The three powers of Rouental as a triangle: a mockup (2026-10-21, night; the author: "Rouental lacks a defined
constitution, and power tends to fluctuate between the Sacred Prince, the Voix, and the Speaker of the Estates General",
the Pious estates "will appreciate actions that push the balance of power towards the Voix"; then "Yes, give me a mockup
of the triangle"; then, of the zones, "Yes, it looks good"; the start "Prince 40, Voix 35, Speaker 25", Rouental "just
coming out of a long regency by the previous Voix"; the Voix Mahaut VI, the Speaker Tara Blanchart).

The game's own balance of power has two sides (a bar: common/bop, interface/powerbalanceview.gui, opened by a button on
the politics screen); three powers need a window of our own, opened from the same place. Three screens:
  three_powers_window.png      1 June 2036: the balance in the middle zone, its six months' trail; the decision Seek the
                               Voix's Blessing hovered (where it would move the balance, the Pious estates who welcome it)
  three_powers_throne_altar.png 1 December 2036: the Speaker under 15, Throne and Altar
  three_powers_zones.png       the seven zones and what each would do (a sheet for the author)
Not in the mod; the zones' names and effects, the decisions, the events and every number but the start are placeholders;
Tara Blanchart has no portrait yet.

    CHROMIUM_PATH=/opt/pw-browsers/chromium python3 make.py   (after a build: the governorates' estates come from it)
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "next_screens"))
sys.path.insert(0, os.path.join(HERE, "..", "governorates"))
from deco import (CREAM, CREAM2, GILT, LABEL, NEG, POS, backdrop, band, bar, box, button, close_browser, diamond,  # noqa: E402
                  esc, fade_rule, header, label, lit_bar, note, octagon_pts, poly, portrait, render, rule, silhouette,
                  sunburst, text, title, tooltip, value, well, window)
import importlib.util  # noqa: E402
import realm as RM  # noqa: E402  (the governorates' placeholder estates)
_spec = importlib.util.spec_from_file_location("gov_make", os.path.join(HERE, "..", "governorates", "make.py"))
GM = importlib.util.module_from_spec(_spec)  # the governorates' mockup: the side panel's notch, the seals
_spec.loader.exec_module(GM)

X0, Y0, WW, WH = 556, 96, 1010, 900        # the window, where the game's balance of power slides out
LX, LW = X0 + 20, 540                     # its left column: the triangle
RX, RW = X0 + 562, 428                    # its right column: the powers, the decisions, the estates, the record

POWERS = {   # key: (title, short, colour)
    "prince": ("The Sacred Prince", "Prince", (217, 181, 101)),
    "voix": ("The Voix", "Voix", (233, 227, 210)),
    "speaker": ("The Speaker", "Speaker", (111, 155, 192)),
}
ORDER = ("prince", "voix", "speaker")


def sgn(d):
    return f"+{d}" if d > 0 else f"−{-d}"


def rgba(c, a):
    return f"rgba({c[0]},{c[1]},{c[2]},{a})"


def mix(a, b):
    return tuple((x + y) // 2 for x, y in zip(a, b))


# The seven zones, as shares (Prince, Voix, Speaker) in percent: a power of 60 or more rules (the corners), a power
# under 15 is shut out (the edges), the rest is the balance Rouental has long kept (the middle). Claude's proposal.
ZONES = {
    "prince": dict(name="Sacred Majesty", where="The Prince holds 60 or more",
                   desc="The Prince rules by sacred right, and rules alone.",
                   pts=((100, 0, 0), (60, 40, 0), (60, 0, 40)), col=POWERS["prince"][2],
                   eff=[("Political power", "+20 %", 1), ("Rule by Royal Decree", "costs half", 1), ("Stability", "−5 %", -1),
                        ("Every governorate's loyalty", "−5", -1)]),
    "voix": dict(name="Rule of the Voix", where="The Voix holds 60 or more",
                 desc="The Voix speaks, and Prince and Estates obey.",
                 pts=((0, 100, 0), (40, 60, 0), (0, 60, 40)), col=POWERS["voix"][2],
                 eff=[("Stability", "+10 %", 1), ("Theocratic support", "+0.05 a day", 0), ("Political power", "−10 %", -1),
                      ("Pious estates' loyalty", "+10", 1), ("The Southmarchers' loyalty", "−10", -1)]),
    "speaker": dict(name="The Estates Supreme", where="The Speaker holds 60 or more",
                    desc="The Estates General governs through its Speaker; the Prince signs what it sends.",
                    pts=((0, 0, 100), (40, 0, 60), (0, 40, 60)), col=POWERS["speaker"][2],
                    eff=[("Every governorate's loyalty", "+10", 1), ("Demand Levies", "costs half", 1),
                         ("Political power", "−20 %", -1), ("Democratic support", "+0.05 a day", 0),
                         ("Rule by Royal Decree", "closed", -1)]),
    "throne": dict(name="Throne and Altar", where="The Speaker under 15",
                   desc="Prince and Voix govern together; the Estates General sits unheard.",
                   pts=((60, 40, 0), (40, 60, 0), (25, 60, 15), (60, 25, 15)),
                   col=mix(POWERS["prince"][2], POWERS["voix"][2]),
                   eff=[("Stability", "+5 %", 1), ("Political power", "+10 %", 1), ("Proud estates' loyalty", "−10", -1)]),
    "crown": dict(name="Crown and Estates", where="The Voix under 15",
                  desc="Prince and Speaker govern together; the Voix is kept from the council.",
                  pts=((60, 0, 40), (40, 0, 60), (25, 15, 60), (60, 15, 25)),
                  col=mix(POWERS["prince"][2], POWERS["speaker"][2]),
                  eff=[("Political power", "+5 %", 1), ("Demand Levies", "a quarter cheaper", 1),
                       ("Pious estates' loyalty", "−10", -1)]),
    "in_name": dict(name="The Prince in Name", where="The Prince under 15",
                    desc="The Voix and the Estates govern between them; the Prince reigns, and no more.",
                    pts=((0, 60, 40), (0, 40, 60), (15, 25, 60), (15, 60, 25)),
                    col=mix(POWERS["voix"][2], POWERS["speaker"][2]),
                    eff=[("Stability", "−10 %", -1), ("Political power", "−15 %", -1), ("Leal estates' loyalty", "−10", -1)]),
    "balance": dict(name="The Unwritten Balance", where="None over 60, none under 15",
                    desc="No power can act alone: Rouental as it has long been.",
                    pts=((60, 25, 15), (60, 15, 25), (25, 15, 60), (15, 25, 60), (15, 60, 25), (25, 60, 15)), col=None,
                    eff=[("No effects", "Rouental as it is", 0)]),
}
LABEL_AT = {   # where each zone's name is written, as shares, and its rotation; the edges' names outside, by their strips
    "prince": ((76, 12, 12), 0), "voix": ((12, 76, 12), 0), "speaker": ((12, 12, 76), 0),
    "throne": ((50, 50, 0), -60), "crown": ((50, 0, 50), 60), "in_name": ((0, 50, 50), 0),
    "balance": ((24, 38, 38), 0),
}
OUTSIDE = ("throne", "crown", "in_name")
SHORT = {"prince": "Sacred<br>Majesty", "voix": "Rule of<br>the Voix", "speaker": "The Estates<br>Supreme",
         "balance": "The Unwritten<br>Balance"}


def zone_of(p, v, s):
    if p >= 60:
        return "prince"
    if v >= 60:
        return "voix"
    if s >= 60:
        return "speaker"
    if s < 15:
        return "throne"
    if v < 15:
        return "crown"
    if p < 15:
        return "in_name"
    return "balance"


# The decisions that push the balance (placeholders: names, costs, shifts)
DECISIONS = [
    ("Rule by Royal Decree", 50, {"prince": 6, "voix": -2, "speaker": -4}, "Stability −2 %"),
    ("Seek the Voix's Blessing", 30, {"voix": 6, "prince": -4, "speaker": -2}, None),
    ("Summon the Estates General", 40, {"speaker": 6, "prince": -3, "voix": -3}, "The estates' tempers change"),
    ("A Royal Progress", 25, {"prince": 3, "speaker": -3}, "One governorate's loyalty +5"),
]
# Which estates welcome a move toward which power (the Pious the author's; the Leal and the Proud Claude's guesses)
LEANINGS = [("Pious", "voix", "the author's"), ("Leal", "prince", "a guess"), ("Proud", "speaker", "a guess")]
START = (40, 35, 25)                      # 1 January 2036 (the author's: just out of the late Voix's long regency)

SCREENS = {
    "window": dict(date="1 June 2036", since="January",
                   trail=[(40, 35, 25), (42, 32, 26), (48, 30, 22), (45, 29, 26), (42, 34, 24), (42, 35, 23)],
                   log=[("Jun 2036", "The month's drift", {"voix": 1, "speaker": -1}),
                        ("May 2036", "Mahaut VI preaches at Rêverie", {"voix": 5, "prince": -3, "speaker": -2}),
                        ("Apr 2036", "The Estates General sits", {"speaker": 4, "prince": -3, "voix": -1}),
                        ("Mar 2036", "Rule by Royal Decree", {"prince": 6, "voix": -2, "speaker": -4}),
                        ("Feb 2036", "The regency's last officials retire", {"prince": 2, "voix": -3, "speaker": 1})],
                   hover=1),
    "throne_altar": dict(date="1 December 2036", since="January",
                         trail=[(42, 35, 23), (48, 33, 19), (48, 34, 18), (44, 40, 16), (50, 38, 12), (52, 41, 7),
                                (52, 42, 6)],
                         log=[("Dec 2036", "The month's drift", {"voix": 1, "speaker": -1}),
                              ("Nov 2036", "Mahaut VI anoints the Prince anew", {"prince": 2, "voix": 3, "speaker": -5}),
                              ("Oct 2036", "Rule by Royal Decree", {"prince": 6, "voix": -2, "speaker": -4}),
                              ("Sep 2036", "Seek the Voix's Blessing", {"voix": 6, "prince": -4, "speaker": -2}),
                              ("Aug 2036", "The month's drift", {"voix": 1, "speaker": -1})]),
}


class Tri:
    """the triangle: the Prince at the top, the Voix bottom left, the Speaker bottom right"""

    def __init__(self, ax, ay, side):
        self.A = (ax, ay)
        h = side * math.sqrt(3) / 2
        self.B = (ax - side / 2, ay + h)
        self.C = (ax + side / 2, ay + h)
        self.side = side

    def at(self, p, v, s):
        t = p + v + s
        p, v, s = p / t, v / t, s / t
        return (p * self.A[0] + v * self.B[0] + s * self.C[0], p * self.A[1] + v * self.B[1] + s * self.C[1])

    def corner(self, k):
        return {"prince": self.A, "voix": self.B, "speaker": self.C}[k]


def pts_attr(pts):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def diamond_path(x, y, r):
    return f"M{x:.1f} {y - r:.1f}L{x + r:.1f} {y:.1f}L{x:.1f} {y + r:.1f}L{x - r:.1f} {y:.1f}Z"


def triangle(T, lit, trail, ghost=None, size=11, hover_zone=None):
    """the zones, the outline, the trail of the past months and the marker; ghost: where a decision would move it"""
    g = [(T.A[0] + T.B[0] + T.C[0]) / 3, (T.A[1] + T.B[1] + T.C[1]) / 3]
    out = sunburst(g[0], g[1] + 10, T.side * .62, .08)
    svg = ""
    for k, z in ZONES.items():
        pts = [T.at(*p) for p in z["pts"]]
        on = k == lit
        hov = k == hover_zone
        if z["col"]:
            a = (.52 if on else .34) if k in POWERS else (.36 if on else .17)
            fill = rgba(z["col"], a + (.1 if hov else 0))
        else:
            fill = "rgba(241,220,156,.13)" if on else "rgba(255,255,255,.025)"
        svg += f'<polygon points="{pts_attr(pts)}" fill="{fill}" stroke="rgba(227,199,126,.42)" stroke-width="1"/>'
    for k in (lit, hover_zone):
        if k:
            pts = [T.at(*p) for p in ZONES[k]["pts"]]
            dash = "" if k == lit else ' stroke-dasharray="4 3"'
            svg += (f'<polygon points="{pts_attr(pts)}" fill="none" stroke="#F1DC9C" stroke-width="{2 if k == lit else 1.4}"'
                    f'{dash}/>')
    # the outline: the core skin's double rule, the outer one a little away
    cx, cy = g
    outer = [(cx + (x - cx) * 1.05, cy + (y - cy) * 1.05) for x, y in (T.A, T.B, T.C)]
    svg += f'<polygon points="{pts_attr((T.A, T.B, T.C))}" fill="none" stroke="#C9A55A" stroke-width="1.6"/>'
    svg += f'<polygon points="{pts_attr(outer)}" fill="none" stroke="rgba(201,165,90,.45)" stroke-width="1"/>'
    # ticks every tenth along each edge
    for (P, Q) in ((T.A, T.B), (T.B, T.C), (T.C, T.A)):
        for i in range(1, 10):
            x, y = P[0] + (Q[0] - P[0]) * i / 10, P[1] + (Q[1] - P[1]) * i / 10
            ox, oy = x - cx, y - cy
            d = math.hypot(ox, oy)
            ln = 6 if i == 5 else 3.5
            svg += (f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x + ox / d * ln:.1f}" y2="{y + oy / d * ln:.1f}" '
                    f'stroke="rgba(227,199,126,.7)" stroke-width="1"/>')
    # the trail: a dot a month, fading into the past
    tp = [T.at(*s) for s in trail]
    svg += (f'<polyline points="{pts_attr(tp)}" fill="none" stroke="rgba(241,220,156,.55)" stroke-width="1.2" '
            f'stroke-dasharray="2 3"/>')
    for i, (x, y) in enumerate(tp[:-1]):
        a = .3 + .5 * i / max(1, len(tp) - 2)
        svg += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="rgba(241,220,156,{a:.2f})" stroke="#0B1014" stroke-width=".8"/>'
    x, y = tp[-1]
    if ghost:
        gx, gy = T.at(*ghost)
        ang = math.atan2(gy - y, gx - x)
        ex, ey = gx - 10 * math.cos(ang), gy - 10 * math.sin(ang)
        svg += (f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="#F1DC9C" stroke-width="1.6" '
                f'stroke-dasharray="5 3"/>')
        hx, hy = ex - 7 * math.cos(ang), ey - 7 * math.sin(ang)
        px, py = -math.sin(ang) * 4.5, math.cos(ang) * 4.5
        svg += f'<path d="M{ex:.1f} {ey:.1f}L{hx + px:.1f} {hy + py:.1f}L{hx - px:.1f} {hy - py:.1f}Z" fill="#F1DC9C"/>'
        svg += f'<path d="{diamond_path(gx, gy, 8)}" fill="rgba(11,16,20,.6)" stroke="#F1DC9C" stroke-width="1.4" stroke-dasharray="3 2"/>'
    svg += f'<path d="{diamond_path(x, y, 13)}" fill="rgba(241,220,156,.18)"/>'
    svg += f'<path d="{diamond_path(x, y, 9)}" fill="#E8CD84" stroke="#16110A" stroke-width="1.4"/>'
    svg += f'<path d="{diamond_path(x, y, 4)}" fill="#16110A"/>'
    out += f'<svg class="a" style="left:0;top:0;overflow:visible" width="1" height="1">{svg}</svg>'
    # the zones' names
    for k, (at, rot) in LABEL_AT.items():
        zx, zy = T.at(*at)
        if k in OUTSIDE:                                   # off the edge's middle, outward
            d = math.hypot(zx - cx, zy - cy)
            zx, zy = zx + (zx - cx) / d * (size + 8), zy + (zy - cy) / d * (size + 8)
        s = "<span>" + SHORT.get(k, ZONES[k]["name"]) + "</span>"
        w = 150
        two = "<br>" in s
        col = "#FFF4D0" if k == lit else "rgba(244,236,217,.72)"
        out += text(zx - w / 2, zy - (size * (1.15 if two else .5)), s, size, col, w=w, align="center", font="fed",
                    track=.1, caps=True, lh=1.15 if two else None,
                    style=f"transform:rotate({rot}deg);text-shadow:0 1px 2px rgba(0,0,0,.8)" if rot else
                    "text-shadow:0 1px 2px rgba(0,0,0,.8)")
    return out


def octo(cx, cy, r, inner):
    """an octagonal medallion (the Deco UI's seal shape): a gilt rim, the picture clipped inside"""
    o = [(x - cx + r, y - cy + r) for x, y in octagon_pts(cx, cy, r)]
    i = [(x - cx + r - 2, y - cy + r - 2) for x, y in octagon_pts(cx, cy, r - 2)]
    return (box(cx - r, cy - r, 2 * r, 2 * r, f"background:linear-gradient(180deg,#F8EBBD,#9C7A36);clip-path:{poly(o)}")
            + f'<div class="a" style="left:{cx - r + 2}px;top:{cy - r + 2}px;width:{2 * r - 4}px;height:{2 * r - 4}px;'
              f'clip-path:{poly(i)};background:#0B1014">{inner}</div>')


def power_picture(k, w, h):
    if k == "prince":
        return portrait("roland_cahun", 0, 0, w, h, "object-position:50% 18%")
    if k == "voix":
        return portrait("mahaut_vi", 0, 0, w, h)
    return silhouette(0, 0, w, h)                         # Tara Blanchart has no portrait yet


def corners_of(T, shares):
    """the three medallions at the corners, each with its power's name and share"""
    out = ""
    r = 38
    for k, share in zip(ORDER, shares):
        x, y = T.corner(k)
        col = POWERS[k][2]
        if k == "prince":
            cx, cy = x, y - 58
            tx, al = cx + r + 12, "left"
        elif k == "voix":
            cx, cy = x, y + 52
            tx, al = cx + r + 12, "left"
        else:
            cx, cy = x, y + 52
            tx, al = cx - r - 12 - 180, "right"
        out += octo(cx, cy, r, power_picture(k, 2 * r - 4, 2 * r - 4))
        out += box(cx - 5, cy + r - 6, 10, 10, f"transform:rotate(45deg);background:{rgba(col, 1)};box-shadow:0 0 0 1.5px #16110A")
        out += label(tx, cy - 24, POWERS[k][0], 10, LABEL, w=180, align=al)
        out += text(tx, cy - 9, str(share), 34, rgba(col, 1) if k != "voix" else "#F4ECD9", w=180, align=al, font="fed")
    return out


def politics_panel(zone, shares):
    """the politics screen the window opens from (drawn simply; the Deco UI's own is fuller): the leader, the
    popularities, and in the place of the game's balance of power button, the three powers'"""
    PX, PY, PW = GM.PX, GM.PY, GM.PW
    Hh = 1080 - PY
    outline = [(0, 0), (21, 0)] + GM.NOTCH + [(175, 0), (PW, 0), (PW, Hh), (0, Hh)]
    out = box(PX, PY, PW, Hh, "background:repeating-linear-gradient(90deg,rgba(255,255,255,.025) 0 1px,transparent 1px 7px),"
              "linear-gradient(180deg,#141E24,#0D1418);clip-path:" + poly(outline) + ";box-shadow:0 0 0 1px #000")
    out += box(PX + PW - 1, PY, 1, Hh, "background:#B8954F")
    out += label(186, 78, "Government", 9.5)
    out += title(184, 95, "The Sacred Principality of", 16, w=310, track=.1) + title(184, 117, "Rouental", 16, w=310, track=.1)
    out += box(498, 82, 22, 22, "transform:rotate(45deg);border:1.5px solid #E3C77E;background:#0E1519")
    out += text(498, 85, "×", 17, GILT, w=22, align="center", weight=400)
    out += rule(184, 150, 532)
    out += well(14, 178, 164, 222, c=0, rim="rgba(201,165,90,.8)") + portrait("roland_cahun", 15, 179, 162, 220,
                                                                           "object-position:50% 20%")
    out += lit_bar(44, 384, 104, 18, c=4) + label(44, 389, "Head of State", 8.5, "#FBEAB4", w=104, align="center")
    out += text(192, 164, "Roland II Cahun", 24, CREAM, font="fed")
    out += box(192, 196, 250, 22, "box-shadow:inset 0 0 0 1px rgba(201,165,90,.6)") + label(222, 203, "Monarchist", 9, LABEL)
    for (x, y, k, v) in ((192, 236, "Ruling party", "Monarchist · 20%"), (362, 236, "Elections", "No Elections"),
                         (192, 294, "Last election", "None"), (362, 294, "Political power", "851 +1.83"),
                         (192, 352, "Sub-ideology", "Feudalism")):
        out += label(x, y, k, 9, LABEL) + value(x, y + 14, v, 14, CREAM, weight=600)
    out += label(12, 416, "Popularity", 10, GILT) + fade_rule(100, 421, 254)
    out += box(10, 434, 94, 94, "border-radius:50%;background:conic-gradient(#7E57C2 0 20%,#EDE6D6 0 40%,#3F63C9 0 60%,"
               "#C8322E 0 80%,#23262A 0 100%);box-shadow:0 0 0 1.5px #C9A55A")
    out += box(37, 461, 40, 40, "border-radius:50%;background:#0D1418;box-shadow:0 0 0 1.5px #C9A55A")
    for i, (n, c) in enumerate((("Monarchist", "#7E57C2"), ("Theocratic", "#EDE6D6"), ("Democratic", "#3F63C9"),
                                ("Communist", "#C8322E"), ("Authoritarian", "#23262A"))):
        out += diamond(119, 443 + i * 19, 9, c, "box-shadow:0 0 0 1px #E3C77E") + text(132, 437 + i * 19, f"{n} 20%", 12.5, CREAM2)
    # the three powers' button, where the game's balance of power sits (under the popularities)
    out += lit_bar(10, 538, 244, 42, c=6)
    out += box(6, 534, 252, 50, "box-shadow:0 0 14px rgba(241,220,156,.35);border-radius:4px")
    t = Tri(37, 545, 30)
    mini = ""
    for k, z in ZONES.items():
        pts = [t.at(*p) for p in z["pts"]]
        fill = rgba(z["col"], .55) if z["col"] else "rgba(241,220,156,.15)"
        mini += f'<polygon points="{pts_attr(pts)}" fill="{fill}" stroke="rgba(227,199,126,.5)" stroke-width=".6"/>'
    mini += f'<polygon points="{pts_attr((t.A, t.B, t.C))}" fill="none" stroke="#F1DC9C" stroke-width="1.1"/>'
    sh = shares
    mx, my = t.at(*sh)
    mini += f'<path d="{diamond_path(mx, my, 3.6)}" fill="#FFF4D0" stroke="#16110A" stroke-width=".8"/>'
    out += f'<svg class="a" style="left:0;top:0;overflow:visible" width="1" height="1">{mini}</svg>'
    out += label(64, 547, "The Three Powers", 9.5, "#FBEAB4")
    out += text(64, 561, ZONES[zone]["name"], 13.5, CREAM, font="fed", track=.04)
    out += text(234, 550, "▸", 15, GILT, w=12)
    # the rest, as the Deco UI has it
    out += label(266, 416, "National spirits", 10, GILT) + fade_rule(410, 421, 532)
    out += well(266, 434, 260, 140, c=4)
    out += label(12, 592, "Faction", 10, GILT) + label(260, 592, "National focus", 10, GILT)
    out += well(12, 606, 240, 70, c=4) + text(60, 633, "Create Faction", 15, CREAM2)
    out += well(260, 606, 266, 70, c=4) + text(336, 622, "Steady As She Goes", 13.5, CREAM2)
    out += box(336, 652, 176, 4, "background:#0A0F12;box-shadow:0 0 0 1px rgba(201,165,90,.5)") + box(337, 653, 70, 2, "background:#E3C77E")
    for i, s in enumerate(("Occupied Territories", "Exiled Governments", "Manage Subjects")):
        out += bar(12 + i * 175, 690, 166, 26, c=5) + text(12 + i * 175, 697, s, 12, CREAM2, w=166, align="center")
    for i, s in enumerate(("Political advisors", "Laws", "Economy")):
        y = 744 + i * 108
        out += bar(6, y, 520, 28, c=5) + label(80, y + 10, s, 10, GILT)
        for j in range(3 if i < 2 else 1):
            out += box(30 + j * 90, y + 44, 48, 48, "border:1px dashed rgba(201,165,90,.55)") + text(30 + j * 90, y + 56, "+", 22, GILT, w=48, align="center", weight=300)
    return out


def power_cards(y, shares, since):
    out = label(RX, y, "The powers", 10, GILT) + fade_rule(RX + 90, y + 5, RX + RW)
    y += 18
    lines = {
        "prince": ("Roland II Cahun", "The Sacred Prince", "Free of the regency; the Royal Host at hand."),
        "voix": ("Mahaut VI", "The Voix · head of the Seran faith", "Gave up much of the regency's power."),
        "speaker": ("Tara Blanchart", "Speaker of the Estates General", "Speaks for the estates of 26 governorates."),
    }
    for k, share, was in zip(ORDER, shares, START):
        col = POWERS[k][2]
        name, role, line = lines[k]
        out += band(RX, y, RW, 72)
        out += box(RX, y, 3, 72, f"background:{rgba(col, 1)}")
        out += well(RX + 10, y + 7, 46, 58, c=0) + f'<div class="a" style="left:{RX + 11}px;top:{y + 8}px;width:44px;height:56px;overflow:hidden">{power_picture(k, 44, 56)}</div>'
        out += label(RX + 66, y + 9, role, 9, LABEL, w=290)
        out += text(RX + 66, y + 22, name, 17, CREAM, font="fed", track=.02)
        if share < 15:
            line, lc = "Shut out: the Proud estates grow restive.", "#EE8C7E"
        else:
            lc = CREAM2
        out += text(RX + 66, y + 46, line, 11.5, lc, w=262, font="bod", weight=500)
        out += text(RX + RW - 70, y + 12, str(share), 30, rgba(col, 1) if k != "voix" else CREAM, w=60, align="right", font="fed")
        d = share - was
        out += value(RX + RW - 104, y + 48, f"{sgn(d)} since {since}" if d else f"even since {since}", 10.5,
                     LABEL, w=94, align="right", weight=600)
        y += 78
    return out, y


def chips(x, y, shifts, size=11.5, right=None):
    """a decision's or an event's shifts, in the powers' colours"""
    out = ""
    items = [(k, shifts[k]) for k in ORDER if k in shifts]
    items.sort(key=lambda kv: -kv[1])
    widths = [len(f"{POWERS[k][1]} {sgn(d)}") * size * .56 + 16 for k, d in items]
    if right is not None:
        x = right - sum(widths)
    for (k, d), w in zip(items, widths):
        col = POWERS[k][2]
        out += box(x, y + 3, 7, 7, f"transform:rotate(45deg);background:{rgba(col, 1)}")
        out += value(x + 11, y, f"{POWERS[k][1]} {sgn(d)}", size, CREAM2 if d > 0 else LABEL, weight=600)
        x += w
    return out


def decisions(y, hover):
    out = label(RX, y, "Decisions", 10, GILT) + fade_rule(RX + 90, y + 5, RX + RW)
    y += 18
    for i, (name, pp, shifts, extra) in enumerate(DECISIONS):
        on = i == hover
        out += (lit_bar if on else bar)(RX, y, RW, 40, c=6)
        out += text(RX + 12, y + 7, name, 14, "#FBEAB4" if on else CREAM)
        out += chips(RX + 12, y + 25, shifts, 10.5)
        out += box(RX + RW - 70, y + 9, 58, 22, "box-shadow:inset 0 0 0 1px rgba(201,165,90,.6);background:rgba(0,0,0,.25)")
        out += value(RX + RW - 70, y + 14, f"{pp} PP", 12, GILT, w=58, align="center")
        y += 44
    return out, y


def leanings(y, shares, since):
    G = RM.governorates()
    out = label(RX, y, f"The estates' leanings (their loyalty since {since})", 10, GILT) + fade_rule(RX + 330, y + 5, RX + RW)
    y += 20
    for att, k, whose in LEANINGS:
        col = POWERS[k][2]
        govs = [g for g, v in G.items() if v["attitude"][0] == att]
        i = ORDER.index(k)
        mood = math.floor((shares[i] - START[i]) * .5 + .5)
        out += GM.seal(RX + 8, y + 8, 7, rgba(col, 1))
        out += text(RX + 22, y + 1, f"{att} estates lean to {POWERS[k][0].replace('The ', 'the ')}", 13.5, CREAM)
        out += label(RX + 22, y + 19, f"{', '.join(govs)}  ·  {whose}", 9, LABEL, w=RW - 22)
        out += value(RX + RW - 110, y + 2, f"loyalty {sgn(mood)}" if mood else "loyalty even", 12, POS if mood > 0 else
                     (NEG if mood < 0 else LABEL), w=110, align="right")
        y += 38
    return out, y


def record(y, log):
    out = label(RX, y, "How the balance has moved", 10, GILT) + fade_rule(RX + 200, y + 5, RX + RW)
    y += 18
    cols = {k: RX + RW - 180 + 60 * i for i, k in enumerate(ORDER)}      # each column 60 wide, numbers to the right
    for k, x in cols.items():
        out += label(x, y + 1, POWERS[k][1], 8.5, rgba(POWERS[k][2], 1), w=60, align="right")
    y += 16
    for d, what, shifts in log:
        out += value(RX, y + 1, d, 11.5, LABEL, w=64, weight=600)
        out += text(RX + 66, y, what, 13, CREAM2, w=200, font="bod", weight=500)
        for k, x in cols.items():
            v = shifts.get(k)
            if v:
                out += value(x, y + 1, sgn(v), 12, rgba(POWERS[k][2], 1) if v > 0 else LABEL, w=60, align="right")
        y += 21
    return out, y


def zone_plate(y, zone):
    z = ZONES[zone]
    out = label(LX, y, "Where the balance stands", 10, GILT) + fade_rule(LX + 190, y + 5, LX + LW)
    out += lit_bar(LX, y + 16, LW, 34, c=7)
    out += title(LX, y + 25, z["name"], 18, w=LW, align="center", track=.16)
    out += text(LX, y + 60, z["desc"], 14, CREAM2, w=LW, align="center", font="bod", weight=500)
    out += label(LX, y + 82, z["where"], 9, LABEL, w=LW, align="center")
    yy = y + 104
    for i, (k, v, sign) in enumerate(z["eff"]):
        x = LX + (i % 2) * (LW // 2 + 10)
        yr = yy + (i // 2) * 20
        out += text(x, yr, k, 13, CREAM2, w=LW // 2 - 90)
        out += value(x + LW // 2 - 150, yr, v, 13, POS if sign > 0 else (NEG if sign < 0 else CREAM2), w=140, align="right")
    return out


def window_screen(which):
    S = SCREENS[which]
    shares = S["trail"][-1]
    zone = zone_of(*shares)
    body = backdrop("map", dim=.2) + politics_panel(zone, shares)
    body += box(1480, 17, 210, 26, "background:linear-gradient(180deg,rgb(29,39,46),rgb(17,25,30))")
    body += text(1480, 23, f"12:00, {S['date'].replace(' 2036', ', 2036')}", 15.5, "#EDE3C9", w=206, align="center",
                 font="fed", track=.05, caps=True)
    body += box(0, 0, 1920, 1080, "background:rgba(4,7,9,.35)")
    body += window(X0, Y0, WW, WH)
    body += header(X0 + 6, Y0 + 6, WW - 12, 44, "The Three Powers", 22, close_at=True)
    body += box(X0 + WW - 46, Y0 + 17, 22, 22, "transform:rotate(45deg);border:1.5px solid #E3C77E;background:#0E1519")
    body += text(X0 + WW - 46, Y0 + 20, "×", 17, GILT, w=22, align="center", weight=400)
    T = Tri(X0 + 290, Y0 + 168, 460)
    ghost = None
    if "hover" in S:
        shifts = DECISIONS[S["hover"]][2]
        ghost = tuple(sh + shifts.get(k, 0) for k, sh in zip(ORDER, shares))
    body += label(LX, Y0 + 62, S["date"], 10, LABEL)
    body += text(LX, Y0 + 77, "No constitution binds them.", 12.5, CREAM2, w=200, font="bod", weight=500)
    body += triangle(T, zone, S["trail"], ghost, hover_zone=S.get("hover_zone"))
    body += corners_of(T, shares)
    body += zone_plate(Y0 + 676, zone)
    body += fade_rule(LX + 120, Y0 + WH - 62, LX + LW - 120)
    body += text(LX, Y0 + WH - 50, "A power of 60 or more rules; one under 15 is shut out. The dots are the past six months: "
                 "each month the balance drifts a point or two on its own, and decisions and events move it further.", 12, LABEL,
                 w=LW, align="center", font="bod", weight=500, lh=1.35)
    b, y = power_cards(Y0 + 62, shares, S["since"])
    body += b
    b, y = decisions(y + 10, S.get("hover"))
    body += b
    b, y = leanings(y + 10, shares, S["since"])
    body += b
    b, y = record(y + 8, S["log"])
    body += b
    if "hover" in S:
        name, pp, shifts, extra = DECISIONS[S["hover"]]
        rows = [("Political power", f"−{pp}", NEG)] + [(POWERS[k][0], sgn(shifts[k]), rgba(POWERS[k][2], 1) if shifts[k] > 0 else LABEL)
                                                     for k in ORDER if k in shifts]
        G = RM.governorates()
        pious = [g for g, v in G.items() if v["attitude"][0] == "Pious"]
        after = zone_of(*ghost)
        body += tooltip(X0 + WW + 10, Y0 + 252, 330, 232, name, rows,
                        f"Welcomed by the Pious estates of {', '.join(pious[:-1])} and {pious[-1]}: their loyalty up 3. "
                        f"Sumarche's Southmarchers, of Reformed Seranism, look on coolly: loyalty down 1. "
                        f"The balance would stay in {ZONES[after]['name']}.")
    if S.get("hover_zone"):
        z = ZONES[S["hover_zone"]]
        rows = [(k, v, POS if s > 0 else (NEG if s < 0 else CREAM2)) for k, v, s in z["eff"]]
        body += tooltip(X0 + 352, Y0 + 104, 330, 70 + 19 * len(rows), z["name"], rows, z["where"] + ".")
    body += note(14, 980, "<b>A mockup, not in the mod.</b> The game's own balance of power has two sides; this is a window "
                 "of our own, opened from the politics screen where the game's button would sit. Zones, effects, "
                 "decisions and numbers are placeholders.", 510)
    return body


def zones_sheet():
    w, h = 1600, 1000
    body = box(0, 0, w, h, "background:#0B1014")
    body += window(16, 16, w - 32, h - 32)
    body += header(22, 22, w - 44, 44, "The Three Powers: the seven zones", 22)
    T = Tri(390, 210, 600)
    body += triangle(T, None, [START], size=13)
    body += corners_of(T, START)
    body += label(60, 84, "Where the balance stands decides what Rouental gets", 10, LABEL)
    body += text(60, 100, "A power of 60 or more rules; a power under 15 is shut out; between them, the old balance.",
                 13, CREAM2, w=600, font="bod", weight=500)
    body += label(60, 830, "The marker: 1 January 2036 (Prince 40, Voix 35, Speaker 25: the author's)", 9.5, LABEL)
    body += text(60, 848, "Rouental is just out of the late Voix's long regency; Mahaut VI, the new Voix, gave much of its "
                 "power up. The zones' names and effects are placeholders.", 12.5, CREAM2, w=640, font="bod", weight=500,
                 lh=1.3)
    x, y = 770, 84
    for k in ("prince", "voix", "speaker", "throne", "crown", "in_name", "balance"):
        z = ZONES[k]
        hh = 34 + 20 + 18 * len(z["eff"]) + 8
        body += band(x, y, 790, hh)
        c = z["col"] or (60, 70, 76)
        body += box(x, y, 4, hh, f"background:{rgba(c, 1)}")
        body += title(x + 16, y + 10, z["name"], 16, w=330, track=.14)
        body += label(x + 360, y + 13, z["where"], 9, LABEL, w=414, align="right")
        body += text(x + 16, y + 32, z["desc"], 13, CREAM2, w=760, font="bod", weight=500)
        yy = y + 54
        for kk, v, s in z["eff"]:
            body += text(x + 30, yy, kk, 12.5, CREAM2, w=300)
            body += value(x + 330, yy, v, 12.5, POS if s > 0 else (NEG if s < 0 else CREAM2), w=200)
            yy += 18
        y += hh + 8
    return body, w, h


def main():
    outs = []
    for which in SCREENS:
        outs.append(render(window_screen(which), os.path.join(HERE, f"three_powers_{which}.png")))
    body, w, h = zones_sheet()
    outs.append(render(body, os.path.join(HERE, "three_powers_zones.png"), w=w, h=h))
    close_browser()
    print("\n".join(outs))


if __name__ == "__main__":
    main()
