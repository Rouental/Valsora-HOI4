"""The three estates of Rouental: a mockup (2026-10-22), in place of the three powers (../three_powers/). The author:
"changing the balance of power from Prince - Voix - Speaker, to one based on the three estates ... any time the second
estate triumphs it results in the decentralization, and there's a separate "Royal Authority" bar that represents the
authority of the Prince. And then a second scale for royal influence between Roland and Serelle. So going for the
Prince's path means playing the sides off each other until you come out on top"; then: "only the disloyal
governorates break away"; the start "35/35/30"; Tara Blanchart "would lead the decentralized Rouental"; the democratic
leader "just use a placeholder for now"; the scale "military bonuses for Serelle, diplomacy bonuses for Roland ... If
we can tie things to Serelle winning battles, that'd be great. But otherwise it'll mostly be through decisions";
"Go ahead with the mockup." The plan: docs/ROUENTAL_ESTATES.md.

Three screens:
  three_estates_window.png       1 June 2036: the estates in balance, Royal Authority rising, the Court behind Roland,
                                 the Promised Reforms running; Divide and Rule hovered
  three_estates_lords_realm.png  1 March 2037: the Second Estate over 60, the Lords' Realm: Royal Authority falling, the
                                 Court behind Serelle, the governorates under 40 that would break away
  three_estates_zones.png        the seven zones, Royal Authority and the Court's favour (a sheet for the author)
  three_estates_symbols.png      the estates' symbols large, and at the sizes the window draws them
The estates are shown by their symbols, not their holders' portraits (the author: "Instead of portraits, I think I'd
prefer to use symbols for the three estates": symbols.py).
Not in the mod; the zones' names and effects, the decisions, Royal Authority's bands and every number but the start
are placeholders; the Third Estate's champion is the author's to name.

    CHROMIUM_PATH=/opt/pw-browsers/chromium python3 make.py   (after a build: the governorates come from it)
"""
import importlib.util
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "next_screens"))
sys.path.insert(0, os.path.join(HERE, "..", "governorates"))
from deco import (CREAM, CREAM2, GILT, LABEL, NEG, POS, backdrop, band, box, close_browser, fade_rule, header,  # noqa: E402
                  label, lit_bar, bar, note, portrait, render, text, title, tooltip, value, well, window)
import realm as RM  # noqa: E402  (the governorates' placeholder estates)
sys.path.insert(0, HERE)
import symbols as SY  # noqa: E402  (the estates' symbols, in place of their holders' portraits)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, "..", path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


GM = load("gov_make", "governorates/make.py")      # the governorates' mockup: its seals
TP = load("tp_make", "three_powers/make.py")       # the three powers': its triangle, the politics screen behind

X0, Y0, WW, WH = 556, 96, 1010, 900        # the window, where the game's balance of power slides out
LX, LW = X0 + 20, 540                     # its left column: the triangle
RX, RW = X0 + 562, 428                    # its right column: the estates, the Crown, the decisions, the leanings

ESTATES = {   # key: (title, short, colour)
    "first": ("The First Estate", "First", (233, 227, 210)),
    "second": ("The Second Estate", "Second", (190, 98, 104)),
    "third": ("The Third Estate", "Third", (111, 155, 192)),
}
ORDER = ("first", "second", "third")
CROWN = {"roland": ("Roland", (217, 181, 101)), "serelle": ("Serelle", (196, 124, 84)), "ra": ("Royal Authority", (241, 220, 156))}
# who speaks for each estate: the author's (2026-10-22: Tara Blanchart "would lead the decentralized Rouental"; the
# Third Estate's leader "just use a placeholder for now")
HOLDERS = {
    "first": ("Anserra IX", "The clergy · the Voix", "mahaut_vi", "Head of the Seran faith; the late Voix's regency is over."),
    "second": ("Tara Blanchart", "The nobility · Lady Chancellor", "tara_blanchart",
               "Roland's friend; Speaker of the Estates General too."),
    "third": ("To be named", "The commons · their champion", None, "A placeholder: the author's to come."),
}


def sgn(d):
    return f"+{d:g}" if d > 0 else f"−{-d:g}"


rgba = TP.rgba
mix = TP.mix

# The seven zones, as shares (First, Second, Third) in percent: an estate of 60 or more dominates (the corners) and
# takes Rouental down its path; an estate under 15 is shut out (the edges); in the middle the Crown holds the scales.
# Royal Authority (`ra`) moves with the zone each month. Claude's proposal, the zones' geometry the three powers'.
ZONES = {
    "first": dict(name="The Voix Behind the Curtain", where="The First Estate holds 60 or more", ra=-2,
                  desc="The Voix rules through the Prince's council; the realm prays as she bids.",
                  leads="The Voix's path: Anserra IX's theocracy (Accept Reality)",
                  pts=((100, 0, 0), (60, 40, 0), (60, 0, 40)), col=ESTATES["first"][2],
                  eff=[("Stability", "+10 %", 1), ("Theocratic support", "+0.05 a day", 0), ("Royal Authority", "−2 a month", -1),
                       ("Pious estates' loyalty", "+10", 1), ("The Southmarchers' loyalty", "−10", -1)]),
    "second": dict(name="The Lords' Realm", where="The Second Estate holds 60 or more", ra=-2,
                   desc="The vassals take back what the Crown had gathered: the realm comes apart.",
                   leads="The decentralization: Tara Blanchart governs; the disloyal governorates break away",
                   pts=((0, 100, 0), (40, 60, 0), (0, 60, 40)), col=ESTATES["second"][2],
                   eff=[("Royal Authority", "−2 a month", -1), ("Proud estates' loyalty", "+10", 1),
                        ("Demand Levies", "the lords raise their own", 0), ("Replace a Governor", "closed", -1)]),
    "third": dict(name="The Commons Ascendant", where="The Third Estate holds 60 or more", ra=-2,
                  desc="The Estates General's third chamber speaks for the realm, and the realm listens.",
                  leads="Reform and a constitutional monarchy; or, if reform was promised and never made, the commons rise",
                  pts=((0, 0, 100), (40, 0, 60), (0, 40, 60)), col=ESTATES["third"][2],
                  eff=[("Democratic support", "+0.05 a day", 0), ("Royal Authority", "−2 a month", -1), ("Stability", "−5 %", -1),
                       ("Mercantile estates' loyalty", "+10", 1)]),
    "no_third": dict(name="Altar and Manor", where="The Third Estate under 15", ra=0,
                     desc="Clergy and lords govern between them; the commons go unheard.",
                     leads="No path of its own: the commons' anger grows",
                     pts=((60, 40, 0), (40, 60, 0), (25, 60, 15), (60, 25, 15)),
                     col=mix(ESTATES["first"][2], ESTATES["second"][2]),
                     eff=[("Stability", "+5 %", 1), ("Political power", "+10 %", 1), ("Communist support", "+0.02 a day", -1)]),
    "no_second": dict(name="Church and Commons", where="The Second Estate under 15", ra=0,
                      desc="The Faith and the commons govern together; the lords sulk in their manors.",
                      leads="No path of its own: the lords grow restive",
                      pts=((60, 0, 40), (40, 0, 60), (25, 15, 60), (60, 15, 25)),
                      col=mix(ESTATES["first"][2], ESTATES["third"][2]),
                      eff=[("Stability", "+5 %", 1), ("Demand Levies", "costs half again", -1), ("Proud estates' loyalty", "−10", -1)]),
    "no_first": dict(name="Manor and Market", where="The First Estate under 15", ra=0,
                     desc="Lords and commons govern without the Voix; the pulpits murmur.",
                     leads="No path of its own: the faithful grow uneasy",
                     pts=((0, 60, 40), (0, 40, 60), (15, 25, 60), (15, 60, 25)),
                     col=mix(ESTATES["second"][2], ESTATES["third"][2]),
                     eff=[("Political power", "+5 %", 1), ("Stability", "−5 %", -1), ("Pious estates' loyalty", "−10", -1)]),
    "balance": dict(name="The Balance of Estates", where="None over 60, none under 15", ra=1,
                    desc="No estate can act alone, and the Crown holds the scales.",
                    leads="The Prince's path: Royal Authority grows while the balance holds",
                    pts=((60, 25, 15), (60, 15, 25), (25, 15, 60), (15, 25, 60), (15, 60, 25), (25, 60, 15)), col=None,
                    eff=[("Royal Authority", "+1 a month", 1)]),
}
LABEL_AT = {
    "first": ((76, 12, 12), 0), "second": ((12, 76, 12), 0), "third": ((12, 12, 76), 0),
    "no_third": ((50, 50, 0), -60), "no_second": ((50, 0, 50), 60), "no_first": ((0, 50, 50), 0),
    "balance": ((24, 38, 38), 0),
}
OUTSIDE = ("no_third", "no_second", "no_first")
SHORT = {"first": "Behind the<br>Curtain", "second": "The Lords'<br>Realm", "third": "The Commons<br>Ascendant",
         "balance": "The Balance<br>of Estates"}

# the three powers' triangle and politics screen, drawn with the estates (their module reads these at call time)
TP.ZONES, TP.POWERS, TP.ORDER, TP.LABEL_AT, TP.OUTSIDE, TP.SHORT = ZONES, ESTATES, ORDER, LABEL_AT, OUTSIDE, SHORT


def zone_of(f, s, t):
    if f >= 60:
        return "first"
    if s >= 60:
        return "second"
    if t >= 60:
        return "third"
    if t < 15:
        return "no_third"
    if s < 15:
        return "no_second"
    if f < 15:
        return "no_first"
    return "balance"


def corner(T, k):
    return {"first": T.A, "second": T.B, "third": T.C}[k]


# Royal Authority, 0 to 100: its bands (placeholders) and its start (Claude's: the regency only just ended)
RA_BANDS = [(0, "A Crown in Name"), (25, "A Contested Crown"), (50, "A Respected Crown"), (75, "A Sovereign Crown")]
RA_START = 30
# The Court's favour between Roland and Serelle: Roland's share of 100. Whoever leads gets their side's bonuses, the
# more the further they lead (at a lead of 50, all of them); the author's sides ("military bonuses for Serelle,
# diplomacy bonuses for Roland"), the numbers Claude's
FAVOUR_START = 60
FAVOUR = {
    "roland": [("Opinion gain", 25, "%"), ("Improve Relations upkeep", -25, "%"), ("Trade opinion", 20, ""),
               ("The Association's opinion of Rouental", 20, "")],
    "serelle": [("Army experience gain", 25, "%"), ("Land doctrine cost", -15, "%"), ("The Royal Host's organisation", 10, "%")],
}
# The decisions (placeholders: names, costs, shifts); Divide and Rule takes from the strongest estate
DECISIONS = [
    ("Endow the Cathedral Chapters", "50 PP", {"first": 6, "second": -3, "third": -3}),
    ("Confirm the Lords' Charters", "50 PP", {"second": 6, "first": -3, "third": -3}),
    ("Promise Reform", "25 PP", {"third": 8, "first": -4, "second": -4}),
    ("Divide and Rule", "10 RA", "divide"),
    ("A Royal Embassy", "50 PP", {"roland": 8}),
    ("Serelle's Command", "50 PP", {"serelle": 8}),
]
PAIRED = 4                                 # the decisions from this one on (the Court's) go two to a row
# Which estates welcome a move toward which estate: the three powers' leanings carried over (the Pious to the clergy,
# the Proud to the lords), the Mercantile to the commons and the Leal to the Crown (Claude's, for the author to change)
LEANINGS = [("Pious", "first"), ("Proud", "second"), ("Mercantile", "third"), ("Leal", "crown")]
START = (35, 35, 30)                       # 1 January 2036: the author's
BREAK_BELOW = 40                           # a governorate under it breaks away in the Lords' Realm (Claude's)

SCREENS = {
    "window": dict(date="1 June 2036", since="January", ra=35, favour=62, hover=3, mission=(212, 0),
                   trail=[(35, 35, 30), (36, 35, 29), (33, 41, 26), (29, 37, 34), (33, 35, 32), (32, 36, 32)]),
    "lords_realm": dict(date="1 March 2037", since="January", ra=12, favour=43,
                        trail=[(32, 36, 32), (30, 40, 30), (28, 46, 26), (27, 51, 22), (25, 56, 19), (24, 60, 16),
                               (23, 63, 14)]),
}


def divide(shares):
    """Divide and Rule: the strongest estate gives 6, the other two take 3 each"""
    top = ORDER[max(range(3), key=lambda i: shares[i])]
    return {k: (-6 if k == top else 3) for k in ORDER}


def ra_band(v):
    return [n for lo, n in RA_BANDS if v >= lo][-1]


def corners_of(T, shares):
    """the three medallions at the corners, each with its estate, its voice and its share"""
    out = ""
    r = 38
    for k, share in zip(ORDER, shares):
        x, y = corner(T, k)
        col = ESTATES[k][2]
        if k == "first":
            cx, cy = x, y - 58
            tx, al = cx + r + 12, "left"
        elif k == "second":
            cx, cy = x, y + 52
            tx, al = cx + r + 12, "left"
        else:
            cx, cy = x, y + 52
            tx, al = cx - r - 12 - 190, "right"
        out += TP.octo(cx, cy, r, picture(k, 2 * r - 4, 2 * r - 4))
        out += box(cx - 5, cy + r - 6, 10, 10, f"transform:rotate(45deg);background:{rgba(col, 1)};box-shadow:0 0 0 1.5px #16110A")
        out += label(tx, cy - 24, ESTATES[k][0], 10, LABEL, w=190, align=al)
        out += text(tx, cy - 9, str(share), 34, rgba(col, 1) if k != "first" else "#F4ECD9", w=190, align=al, font="fed")
    return out


def picture(k, w, h):
    """the estate's symbol on its ground (the author, 2026-10-22: "Instead of portraits, I think I'd prefer to use
    symbols for the three estates"; symbols.py)"""
    a, b = SY.GROUNDS[k]
    n = min(w, h)
    return (f'<div style="position:absolute;left:0;top:0;width:{w}px;height:{h}px;'
            f'background:radial-gradient(circle at 50% 42%,{a},{b} 78%)"><div style="position:absolute;left:{(w - n) / 2}px;'
            f'top:{(h - n) / 2}px">{SY.symbol(k, n)}</div></div>')


def estate_cards(y, shares, since, mission=None):
    out = label(RX, y, "The estates", 10, GILT) + fade_rule(RX + 90, y + 5, RX + RW)
    y += 18
    for k, share, was in zip(ORDER, shares, START):
        col = ESTATES[k][2]
        name, role, _, line = HOLDERS[k]
        out += band(RX, y, RW, 62)
        out += box(RX, y, 3, 62, f"background:{rgba(col, 1)}")
        out += well(RX + 10, y + 6, 40, 50, c=0) + (f'<div class="a" style="left:{RX + 11}px;top:{y + 7}px;width:38px;'
                                                   f'height:48px;overflow:hidden">{picture(k, 38, 48)}</div>')
        out += label(RX + 60, y + 7, role, 9, LABEL, w=290)
        out += text(RX + 60, y + 19, name, 16, CREAM if HOLDERS[k][2] or k != "third" else LABEL, font="fed", track=.02)
        if k == "third" and mission:
            line, lc = f"Reform promised: {mission[0]} days to make it good.", "#E7B75A"
        elif share < 15:
            line, lc = "Shut out: their estates grow restive.", "#EE8C7E"
        else:
            lc = CREAM2
        out += text(RX + 60, y + 41, line, 11, lc, w=268, font="bod", weight=500)
        out += text(RX + RW - 70, y + 9, str(share), 28, rgba(col, 1) if k != "first" else CREAM, w=60, align="right", font="fed")
        d = share - was
        out += value(RX + RW - 104, y + 42, f"{sgn(d)} since {since}" if d else f"even since {since}", 10, LABEL, w=94,
                     align="right", weight=600)
        y += 66
    return out, y


def crown_block(y, ra, zone, favour):
    """Royal Authority (a gauge with its bands) and the Court's favour (a scale between Roland and Serelle)"""
    z = ZONES[zone]
    out = label(RX, y, "The Crown", 10, GILT) + fade_rule(RX + 80, y + 5, RX + RW)
    y += 18
    out += band(RX, y, RW, 66)
    out += label(RX + 12, y + 8, "Royal Authority", 9.5, LABEL)
    out += text(RX + 12, y + 20, ra_band(ra), 15, CREAM, font="fed", track=.03)
    out += text(RX + RW - 72, y + 6, str(ra), 28, rgba(CROWN["ra"][1], 1), w=60, align="right", font="fed")
    d = z["ra"]
    why = {1: "the estates in balance", 0: "one estate shut out", -2: "one estate dominant"}[d]
    out += value(RX + RW - 250, y + 38, f"{sgn(d)} a month: {why}" if d else f"steady: {why}", 10,
                 POS if d > 0 else (NEG if d < 0 else LABEL), w=238, align="right", weight=600)
    gx, gw, gy = RX + 12, RW - 24, y + 52
    out += box(gx, gy, gw, 8, "background:#080C0F;box-shadow:0 0 0 1px rgba(201,165,90,.6)")
    out += box(gx + 1, gy + 1, (gw - 2) * ra / 100, 6, "background:linear-gradient(180deg,#F1DC9C,#9C7A36)")
    for lo, _ in RA_BANDS[1:]:
        out += box(gx + gw * lo / 100 - .5, gy - 3, 1, 14, "background:rgba(241,220,156,.8)")
    y += 72
    # the Court's favour
    out += band(RX, y, RW, 100)
    out += label(RX + 12, y + 8, "Whom the Court follows", 9.5, LABEL, w=RW - 24, align="center")
    for k, x in (("roland", RX + 10), ("serelle", RX + RW - 50)):
        out += well(x, y + 22, 40, 50, c=0) + (f'<div class="a" style="left:{x + 1}px;top:{y + 23}px;width:38px;height:48px;'
                                              f'overflow:hidden">{portrait(k + "_cahun", 0, 0, 38, 48, "object-position:50% 18%")}</div>')
    sx, sw, sy = RX + 62, RW - 124, y + 40
    share = favour
    out += box(sx, sy, sw, 6, "background:#080C0F;box-shadow:0 0 0 1px rgba(201,165,90,.6)")
    mid = sx + sw / 2
    lead = "roland" if share >= 50 else "serelle"
    # the scale runs Roland (left) to Serelle (right): his share pulls the marker left of the middle
    fill_x = mid - sw * (share - 50) / 100 if lead == "roland" else mid
    fill_w = abs(sw * (share - 50) / 100)
    out += box(fill_x, sy + 1, fill_w, 4, f"background:{rgba(CROWN[lead][1], 1)}")
    out += box(mid - .5, sy - 4, 1, 14, "background:rgba(241,220,156,.8)")
    mx = mid - sw * (share - 50) / 100
    out += box(mx - 6, sy - 3, 12, 12, "transform:rotate(45deg);background:#E8CD84;box-shadow:0 0 0 1.4px #16110A")
    out += value(sx, sy + 14, f"Roland {share}", 11.5, rgba(CROWN["roland"][1], 1) if lead == "roland" else LABEL, w=120)
    out += value(sx + sw - 120, sy + 14, f"Serelle {100 - share}", 11.5, rgba(CROWN["serelle"][1], 1) if lead == "serelle"
                 else LABEL, w=120, align="right")
    k = abs(share - 50) / 50
    effs = ", ".join(f"{n} {sgn(round(v * k))}{u}" for n, v, u in FAVOUR[lead][:3])
    who = "Roland leads: the Crown's diplomacy" if lead == "roland" else "Serelle leads: the Crown's army"
    out += text(RX + 62, y + 64, f"{who}. {effs}.", 10.5, CREAM2, w=RW - 124, lh=1.3)
    return out, y + 106


def chips(x, y, shifts, size=10.5):
    out = ""
    items = sorted(shifts.items(), key=lambda kv: -kv[1])
    for k, d in items:
        col = ESTATES[k][2] if k in ESTATES else CROWN[k][1]
        name = ESTATES[k][1] if k in ESTATES else CROWN[k][0]
        w = len(f"{name} {sgn(d)}") * size * .56 + 16
        out += box(x, y + 3, 7, 7, f"transform:rotate(45deg);background:{rgba(col, 1)}")
        out += value(x + 11, y, f"{name} {sgn(d)}", size, CREAM2 if d > 0 else LABEL, weight=600)
        x += w
    return out


def decisions(y, hover, shares):
    out = label(RX, y, "Decisions", 10, GILT) + fade_rule(RX + 90, y + 5, RX + RW)
    y += 18
    for i, (name, cost, shifts) in enumerate(DECISIONS):
        if shifts == "divide":
            shifts = divide(shares)
        on = i == hover
        x, w = RX, RW
        if i >= PAIRED:
            w = (RW - 6) / 2
            x = RX + (i - PAIRED) % 2 * (w + 6)
        out += (lit_bar if on else bar)(x, y, w, 38, c=6)
        out += text(x + 12, y + 6, name, 13.5, "#FBEAB4" if on else CREAM)
        out += chips(x + 12, y + 23, shifts, 10)
        out += box(x + w - 70, y + 8, 58, 22, "box-shadow:inset 0 0 0 1px rgba(201,165,90,.6);background:rgba(0,0,0,.25)")
        out += value(x + w - 70, y + 13, cost, 11.5, GILT, w=58, align="center")
        if i < PAIRED or (i - PAIRED) % 2 or i == len(DECISIONS) - 1:
            y += 41
    return out, y


def leanings(y, shares, since, ra):
    G = RM.governorates()
    out = label(RX, y, f"The estates' leanings (their loyalty since {since})", 10, GILT) + fade_rule(RX + 398, y + 5, RX + RW)
    y += 20
    for att, k in LEANINGS:
        govs = [g for g, v in G.items() if v["attitude"][0] == att]
        if k == "crown":
            col, mood, to = CROWN["ra"][1], math.floor((ra - RA_START) * .3 + .5), "the Crown"
        else:
            i = ORDER.index(k)
            col, mood, to = ESTATES[k][2], math.floor((shares[i] - START[i]) * .5 + .5), ESTATES[k][0].replace("The ", "the ")
        out += GM.seal(RX + 8, y + 8, 7, rgba(col, 1))
        out += text(RX + 22, y + 1, f"{att} estates lean to {to}", 13, CREAM)
        out += label(RX + 22, y + 18, ", ".join(govs), 8.5, LABEL, w=RW - 130)
        out += value(RX + RW - 110, y + 2, f"loyalty {sgn(mood)}" if mood else "loyalty even", 11.5, POS if mood > 0 else
                     (NEG if mood < 0 else LABEL), w=110, align="right")
        y += 34
    return out, y


def zone_plate(y, zone):
    z = ZONES[zone]
    out = label(LX, y, "Where the balance stands", 10, GILT) + fade_rule(LX + 190, y + 5, LX + LW)
    out += lit_bar(LX, y + 16, LW, 34, c=7)
    out += title(LX, y + 25, z["name"], 18, w=LW, align="center", track=.16)
    out += text(LX, y + 58, z["desc"], 13.5, CREAM2, w=LW, align="center", font="bod", weight=500)
    out += label(LX, y + 79, z["where"], 9, LABEL, w=LW, align="center")
    yy = y + 100
    for i, (k, v, sign) in enumerate(z["eff"]):
        x = LX + (i % 2) * (LW // 2 + 10)
        yr = yy + (i // 2) * 19
        out += text(x, yr, k, 12.5, CREAM2, w=LW // 2 - 90)
        out += value(x + LW // 2 - 150, yr, v, 12.5, POS if sign > 0 else (NEG if sign < 0 else CREAM2), w=140, align="right")
    yy += ((len(z["eff"]) + 1) // 2) * 19 + 6
    out += label(LX, yy, "Where it leads", 9, LABEL) + text(LX + 104, yy - 3, z["leads"], 12.5, "#FBEAB4", w=LW - 104,
                                                             font="bod", weight=500, lh=1.3)
    return out, yy + (40 if len(z["leads"]) > 70 else 24)


def mission(y, left, done):
    """the Promised Reforms: a mission the Promise Reform decision starts"""
    out = label(LX, y, "The Promised Reforms", 10, "#E7B75A") + fade_rule(LX + 170, y + 5, LX + LW, "231,183,90")
    out += band(LX, y + 16, LW, 56)
    out += text(LX + 12, y + 23, f"{left} days left · reform focuses done: {done} of 3", 13.5, CREAM)
    out += box(LX + 12, y + 44, LW - 24, 6, "background:#080C0F;box-shadow:0 0 0 1px rgba(231,183,90,.6)")
    out += box(LX + 13, y + 45, (LW - 26) * (1 - left / 365), 4, "background:linear-gradient(90deg,#E7B75A,#B9822E)")
    out += text(LX + 12, y + 54, "If the reform focuses are not done in time, the commons rise: the secret communist path opens.",
                11, LABEL, w=LW - 24, font="bod", weight=500)
    return out


def breakaway(y):
    """the Lords' Realm: the realm map, the governorates under BREAK_BELOW outlined, their names at their seals"""
    G = RM.governorates()
    R = RM.realm()
    goes = sorted((g for g, v in G.items() if v["loyalty"] < BREAK_BELOW), key=lambda g: G[g]["loyalty"])
    out = label(RX, y, f"What would break away (loyalty under {BREAK_BELOW})", 10, GILT) + fade_rule(RX + 350, y + 5, RX + RW)
    y += 18
    sc = (RW - 8) / R["S"].shape[1]
    W, H = R["S"].shape[1] * sc, R["S"].shape[0] * sc
    out += well(RX, y, W + 8, H + 8, c=6)
    out += f'<div class="a" style="left:{RX + 4}px;top:{y + 4}px">{RM.map_svg(sc, select_govs=goes)}</div>'
    for n, g in enumerate(goes, 1):            # numbered on their seals: the western ones lie close together
        sx, sy, _ = R["seal"][g]
        cx, cy = RX + 4 + sx * sc, y + 4 + sy * sc
        out += box(cx - 8, cy - 8, 16, 16, "border-radius:50%;background:#16110A;box-shadow:0 0 0 1.4px #F1DC9C")
        out += value(cx - 8, cy - 5, str(n), 10.5, "#FFF4D0", w=16, align="center")
    y += H + 16
    names = ", ".join(f"{n} {g} ({G[g]['loyalty']})" for n, g in enumerate(goes, 1))
    out += text(RX, y, f"{len(goes)} governorates would go their own way as the Crown's vassal states: {names}. Tara "
                "Blanchart governs what stays. No governor can be replaced; each lost governorate can be won back by "
                "decision, as the base game's Yugoslavia wins back its banovinas.", 11.5, CREAM2, w=RW, font="bod",
                weight=500, lh=1.35)
    return out


def window_screen(which):
    S = SCREENS[which]
    shares = S["trail"][-1]
    zone = zone_of(*shares)
    body = backdrop("map", dim=.2) + TP.politics_panel(zone, shares).replace("The Three Powers", "The Three Estates")
    body += box(1480, 17, 210, 26, "background:linear-gradient(180deg,rgb(29,39,46),rgb(17,25,30))")
    body += text(1480, 23, f"12:00, {S['date'].replace(' 203', ', 203')}", 15.5, "#EDE3C9", w=206, align="center",
                 font="fed", track=.05, caps=True)
    body += box(0, 0, 1920, 1080, "background:rgba(4,7,9,.35)")
    body += window(X0, Y0, WW, WH)
    body += header(X0 + 6, Y0 + 6, WW - 12, 44, "The Three Estates", 22, close_at=True)
    body += box(X0 + WW - 46, Y0 + 17, 22, 22, "transform:rotate(45deg);border:1.5px solid #E3C77E;background:#0E1519")
    body += text(X0 + WW - 46, Y0 + 20, "×", 17, GILT, w=22, align="center", weight=400)
    T = TP.Tri(X0 + 290, Y0 + 160, 400)
    ghost = None
    if "hover" in S:
        sh = DECISIONS[S["hover"]][2]
        sh = divide(shares) if sh == "divide" else sh
        ghost = tuple(v + sh.get(k, 0) for k, v in zip(ORDER, shares))
    body += label(LX, Y0 + 62, S["date"], 10, LABEL)
    body += text(LX, Y0 + 77, "The Crown above the estates.", 12.5, CREAM2, w=220, font="bod", weight=500)
    body += TP.triangle(T, zone, S["trail"], ghost)
    body += corners_of(T, shares)
    b, y = zone_plate(Y0 + 618, zone)
    body += b
    if S.get("mission"):
        body += mission(y + 6, *S["mission"])
    else:
        body += fade_rule(LX + 120, Y0 + WH - 62, LX + LW - 120)
        body += text(LX, Y0 + WH - 50, "An estate of 60 or more takes Rouental down its path; one under 15 is shut out. Royal "
                     "Authority grows only while the balance holds, and falls while an estate dominates.", 12, LABEL,
                     w=LW, align="center", font="bod", weight=500, lh=1.35)
    b, y = estate_cards(Y0 + 62, shares, S["since"], S.get("mission"))
    body += b
    b, y = crown_block(y + 8, S["ra"], zone, S["favour"])
    body += b
    if which == "lords_realm":
        body += breakaway(y + 8)
    else:
        b, y = decisions(y + 8, S.get("hover"), shares)
        body += b
        b, y = leanings(y + 8, shares, S["since"], S["ra"])
        body += b
    if "hover" in S:
        name, cost, _ = DECISIONS[S["hover"]]
        sh = divide(shares)
        rows = [("Royal Authority", "−10", NEG)] + [(ESTATES[k][0], sgn(sh[k]), rgba(ESTATES[k][2], 1) if sh[k] > 0 else LABEL)
                                                    for k in ORDER]
        after = zone_of(*ghost)
        body += tooltip(X0 + WW + 10, Y0 + 470, 330, 218, name, rows,
                        "The Crown sets the estates against each other: the strongest gives ground, the other two take "
                        f"it. The balance would stay in {ZONES[after]['name']}, and Royal Authority keep growing.")
    body += note(14, 980, "<b>A mockup, not in the mod.</b> The three estates in place of the three powers: zones, effects, "
                 "decisions, Royal Authority's bands and every number but the start (35 / 35 / 30) are placeholders.", 510)
    return body


def zones_sheet():
    w, h = 1600, 1180
    body = box(0, 0, w, h, "background:#0B1014")
    body += window(16, 16, w - 32, h - 32)
    body += header(22, 22, w - 44, 44, "The Three Estates: the seven zones and the Crown", 22)
    T = TP.Tri(390, 210, 600)
    body += TP.triangle(T, None, [START], size=13)
    body += corners_of(T, START)
    body += label(60, 84, "Where the balance stands decides where Rouental goes", 10, LABEL)
    body += text(60, 100, "An estate of 60 or more takes Rouental down its path; an estate under 15 is shut out; between "
                 "them, the Crown holds the scales.", 13, CREAM2, w=640, font="bod", weight=500, lh=1.3)
    body += label(60, 830, "The marker: 1 January 2036 (First 35, Second 35, Third 30: the author's)", 9.5, LABEL)
    # the Crown: Royal Authority's bands and the Court's favour, under the triangle
    y = 870
    body += label(60, y, "Royal Authority", 10, GILT) + fade_rule(190, y + 5, 700)
    y += 18
    for lo, n in RA_BANDS:
        hi = next((l2 for l2, _ in RA_BANDS if l2 > lo), 100)
        body += text(60, y, n, 13, CREAM, w=260) + value(320, y, f"{lo} to {hi}", 12.5, LABEL, w=120)
        y += 19
    body += text(60, y + 4, "+1 a month in the Balance of Estates, steady while an estate is shut out, −2 a month while one "
                 "dominates; Divide and Rule spends it. Starts at 30 (Claude's: the regency only just ended).", 12, CREAM2,
                 w=640, lh=1.35)
    y += 52
    body += label(60, y, "Whom the Court follows", 10, GILT) + fade_rule(240, y + 5, 700)
    y += 18
    for k in ("roland", "serelle"):
        effs = ", ".join(f"{n} {sgn(v)}{u}" for n, v, u in FAVOUR[k])
        body += text(60, y, f"{CROWN[k][0]} leads:", 13, rgba(CROWN[k][1], 1), w=120)
        body += text(170, y, effs, 12, CREAM2, w=540, lh=1.35)
        y += 36
    body += text(60, y, "In full at a lead of 50, in part below it; only the one who leads. It moves by decisions, and "
                 "toward Serelle with every battle her army wins.", 12, LABEL, w=640, font="bod", weight=500, lh=1.3)
    x, y = 770, 84
    for k in ("first", "second", "third", "no_third", "no_second", "no_first", "balance"):
        z = ZONES[k]
        hh = 34 + 20 + 18 * len(z["eff"]) + 30
        body += band(x, y, 790, hh)
        c = z["col"] or (60, 70, 76)
        body += box(x, y, 4, hh, f"background:{rgba(c, 1)}")
        body += title(x + 16, y + 10, z["name"], 16, w=360, track=.14)
        body += label(x + 380, y + 13, z["where"], 9, LABEL, w=394, align="right")
        body += text(x + 16, y + 32, z["desc"], 13, CREAM2, w=760, font="bod", weight=500)
        yy = y + 54
        for kk, v, s in z["eff"]:
            body += text(x + 30, yy, kk, 12.5, CREAM2, w=300)
            body += value(x + 330, yy, v, 12.5, POS if s > 0 else (NEG if s < 0 else CREAM2), w=300)
            yy += 18
        body += text(x + 16, yy + 4, z["leads"], 12.5, "#FBEAB4", w=760, font="bod", weight=500)
        y += hh + 8
    return body, w, h


def symbols_sheet():
    """the three symbols large in the corners' medallions, and each at the sizes the window draws it"""
    w, h = 1300, 760
    body = box(0, 0, w, h, "background:#0B1014")
    body += window(16, 16, w - 32, h - 32)
    body += header(22, 22, w - 44, 44, "The Three Estates: their symbols", 22)
    lines = {"first": ("A golden rogacina issuant from a cauldron", "The symbol of the faith, as the author drew it"),
             "second": ("Three crowns, two and one", "The author's crown, a jewelled band and pearls added; red, blue, green"),
             "third": ("A sheaf of wheat bound with a key", "The fields and the towns (the author's choice of three)")}
    for i, k in enumerate(ORDER):
        cx, cy = 240 + i * 410, 270
        body += TP.octo(cx, cy, 140, picture(k, 276, 276))
        body += box(cx - 9, cy + 131, 18, 18, f"transform:rotate(45deg);background:{rgba(ESTATES[k][2], 1)};"
                    "box-shadow:0 0 0 2px #16110A")
        body += label(cx - 190, cy + 168, ESTATES[k][0], 11, LABEL, w=380, align="center")
        body += title(cx - 200, cy + 186, lines[k][0], 14.5, w=400, align="center", track=.06)
        body += text(cx - 200, cy + 214, lines[k][1], 13, CREAM2, w=400, align="center", font="bod", weight=500)
        # at the window's sizes: the corner's medallion (76) and the card's well (38)
        body += TP.octo(cx - 40, cy + 300, 38, picture(k, 72, 72))
        body += (f'<div class="a" style="left:{cx + 20}px;top:{cy + 276}px;width:38px;height:48px;'
                 f'box-shadow:0 0 0 1px rgba(201,165,90,.55);overflow:hidden">{picture(k, 38, 48)}</div>')
    body += label(60, h - 52, "Below each, the symbol at the sizes the window draws it: a corner's medallion and an "
                  "estate's card", 9.5, LABEL, w=w - 120, align="center")
    return body, w, h


def main():
    outs = []
    for which in SCREENS:
        outs.append(render(window_screen(which), os.path.join(HERE, f"three_estates_{which}.png")))
    body, w, h = zones_sheet()
    outs.append(render(body, os.path.join(HERE, "three_estates_zones.png"), w=w, h=h))
    body, w, h = symbols_sheet()
    outs.append(render(body, os.path.join(HERE, "three_estates_symbols.png"), w=w, h=h))
    close_browser()
    print("\n".join(outs))


if __name__ == "__main__":
    main()
