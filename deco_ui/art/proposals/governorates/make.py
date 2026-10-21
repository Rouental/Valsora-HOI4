"""The governorates in the decisions tab: a mockup (2026-10-21, the author: "I'd like to set up a system for interacting
with the governorates in the decisions tab"; then: "let's start with the map ... The governorates should display the
name of the governor, loyalty, the attitude of the parliament ... I'm tempted to have further info on the individual
states within the governorates, since levy quality can vary wildly between them. ... The royal fiefs indeed be shown
and handled separately. ... Don't go with rough shapes for the map, exactly follow the game's borders").

Two screens at 1920 x 1080, the Deco UI's decisions panel open on the map: Rouental's Governorates category with the
realm drawn from the build's own map (realm.py: every line a state border of the game), a governorate selected (its
governor, loyalty, estates and states, one state picked), and the Crown's Domain selected (the Royal Fiefs, held by the
King, the Royal Host raised from them). Not in the mod; the governors, loyalty, attitudes and levy quality are
placeholders.

    CHROMIUM_PATH=/opt/pw-browsers/chromium python3 make.py   (after a build: reads build/valsora_test)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "next_screens"))
sys.path.insert(0, HERE)
from deco import (CREAM, CREAM2, GILT, HI, LABEL, RULE, backdrop, band, bar, box, button, chamfer, diamond, esc,  # noqa: E402
                  fade_rule, ico, label, lit_bar, note, poly, portrait, render, rule, silhouette, text, title, tooltip,
                  value, well, close_browser)
from PIL import Image  # noqa: E402
import realm as RM  # noqa: E402  (puts the Valsora scripts on the path)
import nations  # noqa: E402

PX, PY, PW = -6, 62, 550                  # the decisions panel (the Deco UI's: flush under the band, x -6)
NOTCH = [(21.0, 59.0), (39.7, 59.0), (39.7, 76.0), (61.6, 76.0), (61.6, 85.0), (77.0, 85.0), (77.0, 94.6), (88.4, 106.0),
         (107.6, 106.0), (119.0, 94.6), (119.0, 85.0), (134.4, 85.0), (134.4, 76.0), (156.3, 76.0), (156.3, 59.0),
         (175.0, 59.0)]                   # layout_panels.notch_poly(-6), its foot (the medallion and the seal)
MAP_X, MAP_Y, SCALE = 16, 238, 1.6        # the realm: 320 x 182 map px at 1.6 = 512 x 291
SELECT = "Gheso"


def panel():
    """the side panel's body with the notch round the medallion, its header and the category's plate"""
    H = 1080 - PY
    outline = [(0, 0), (21, 0)] + NOTCH + [(175, 0), (PW, 0), (PW, H), (0, H)]
    out = box(PX, PY, PW, H, "background:repeating-linear-gradient(90deg,rgba(255,255,255,.025) 0 1px,transparent 1px 7px),"
              "linear-gradient(180deg,#141E24,#0D1418);clip-path:" + poly(outline) + ";box-shadow:0 0 0 1px #000")
    out += box(PX + PW - 1, PY, 1, H, "background:#B8954F")
    out += title(190, 82, "Decisions", 26, w=300)
    out += box(498, 80, 22, 22, "transform:rotate(45deg);border:1.5px solid #E3C77E;background:#0E1519")
    out += text(498, 83, "×", 17, GILT, w=22, align="center", weight=400)
    out += rule(186, 168, PW + PX - 8, "rgba(201,165,90,.85)")
    # the category's plate, as the Deco UI's decisions tab draws them
    out += bar(10, 178, 524, 36, c=6) + ico("gov", 20, 184, 24)
    out += title(54, 188, "The Governorates", 18, w=380)
    out += text(500, 186, "▾", 16, GILT, w=20, align="center")
    out += label(14, 220, "26 governorates  ·  165 states  ·  the Crown's Domain: 11 Royal Fiefs", 9.5, w=516, align="center")
    return out


def realm_map(select_gov=None, select_state=None, crown=False):
    R = RM.realm()
    G = RM.governorates()
    W, H = R["S"].shape[1] * SCALE, R["S"].shape[0] * SCALE
    out = well(MAP_X - 4, MAP_Y - 4, W + 8, H + 8, c=6)
    out += f'<div class="a" style="left:{MAP_X}px;top:{MAP_Y}px">{RM.map_svg(SCALE, select_gov, select_state, crown)}</div>'
    # the Crown's seal on the capital; the selected governorate's name by its seal
    cap = next(s for s in R["royal"] if R["st"][s]["name"] == "Rêverie")
    import numpy as np
    ys, xs = np.nonzero(R["S"] == cap)
    cx, cy = MAP_X + (xs.mean() + .5) * SCALE, MAP_Y + (ys.mean() + .5) * SCALE
    out += crown_seal(cx, cy, 7.5, lit=crown)
    if select_gov:
        sx, sy, _ = R["seal"][select_gov]
        x, y = MAP_X + sx * SCALE, MAP_Y + sy * SCALE
        out += text(x - 60, y + 8, select_gov, 12, "#FFF4D0", w=120, align="center", font="fed", track=.12, caps=True,
                    style="text-shadow:0 1px 2px #000,0 0 5px #000,0 0 3px #000")
    if crown:
        out += text(cx - 70, cy + 11, "The Crown's Domain", 11, "#FFF4D0", w=140, align="center", font="fed", track=.1,
                    caps=True, style="text-shadow:0 1px 2px #000,0 0 5px #000,0 0 3px #000")
    # the legend
    y = MAP_Y + H + 12
    x = 16
    for lo, name, colour in RM.BANDS:
        out += box(x, y + 1, 11, 11, f"background:{colour};box-shadow:0 0 0 1px rgba(227,199,126,.7)")
        out += label(x + 16, y + 2, name, 9.5, CREAM2)
        x += 16 + len(name) * 7.2 + 14
    out += box(x, y + 1, 11, 11, "background:repeating-linear-gradient(45deg,#C9A55A 0 1.1px,#6E5626 1.1px 3px);"
               "box-shadow:0 0 0 1px rgba(227,199,126,.7)") + label(x + 16, y + 2, "Royal Fief", 9.5, CREAM2)
    return out


def crown_seal(cx, cy, r, lit=False):
    pts = [(cx + r * __import__("math").cos(__import__("math").radians(22.5 + 45 * i)),
            cy + r * __import__("math").sin(__import__("math").radians(22.5 + 45 * i))) for i in range(8)]
    rim = "#FFF2C4" if lit else "#E3C77E"
    return (f'<svg class="a" style="left:0;top:0;overflow:visible" width="1" height="1">'
            f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="#1A1408" stroke="{rim}" stroke-width="{1.6 if lit else 1.2}"/>'
            f'<path d="M{cx - 4.2} {cy + 2.6}h8.4l.9-5.4-2.6 2-2.5-3.6-2.5 3.6-2.6-2z" fill="#F1DC9C"/></svg>')


def seal(cx, cy, r, colour):
    import math
    pts = " ".join(f"{cx + r * math.cos(math.radians(22.5 + 45 * i)):.1f},{cy + r * math.sin(math.radians(22.5 + 45 * i)):.1f}"
                   for i in range(8))
    return (f'<svg class="a" style="left:0;top:0;overflow:visible" width="1" height="1"><polygon points="{pts}" fill="{colour}" '
            f'stroke="#E3C77E" stroke-width="1.6"/></svg>')


def pips(x, y, n, total=5, lit="#E3C77E"):
    out = ""
    for i in range(total):
        out += box(x + i * 11, y, 7, 7, f"transform:rotate(45deg);background:{lit if i < n else 'transparent'};"
                   f"box-shadow:0 0 0 1px {'rgba(227,199,126,.85)' if i < n else 'rgba(201,165,90,.4)'}")
    return out


def card_governorate(g, picked):
    R = RM.realm()
    G = RM.governorates()[g]
    st = R["st"]
    lo, word, colour = RM.band(G["loyalty"])
    y0 = 566
    out = band(10, y0, 524, 38) + rule(10, y0 + 38, 534, "rgba(201,165,90,.6)")
    out += seal(32, y0 + 19, 11, colour)
    out += title(52, y0 + 10, f"Governorate of {g}", 19, w=330)
    out += label(330, y0 + 15, f"{len(G['states'])} states  ·  {G['manpower'] / 1e6:.2f} M men", 9.5, w=196, align="right")
    # the governor
    y = y0 + 50
    out += well(18, y, 78, 98, c=5) + silhouette(19, y + 1, 76, 96)
    out += label(108, y + 2, "Governor", 9.5)
    out += text(108, y + 16, G["governor"], 19, CREAM, font="fed", track=.02)
    out += text(108, y + 40, f"Seat: {st[G['seat']]['name']}", 12.5, CREAM2, font="bod", weight=500)
    out += label(108, y + 62, "Loyalty to the Crown", 9.5)
    out += box(108, y + 78, 300, 10, "background:#0A0F12;box-shadow:0 0 0 1px rgba(201,165,90,.55)")
    out += box(109, y + 79, 298 * G["loyalty"] / 100, 8, f"background:linear-gradient(180deg,{colour},{colour}cc)")
    for t in (20, 40, 60, 80):
        out += box(108 + 300 * t / 100, y + 76, 1, 14, "background:rgba(227,199,126,.45)")
    out += value(418, y + 71, str(G["loyalty"]), 22, CREAM, w=40, align="right")
    out += text(464, y + 76, word, 13, colour if word != "Defiant" else "#E7A493", font="fed", track=.06, caps=True)
    # the estates
    y = y0 + 158
    out += label(18, y, f"The Estates of {g}", 9.5)
    att, desc = G["attitude"]
    out += lit_bar(18, y + 16, 118, 26, c=5) + text(18, y + 23, att, 13, "#FBEAB4", w=118, align="center", font="fed", track=.14, caps=True)
    out += text(148, y + 15, desc, 13, CREAM2, w=376, font="bod", weight=500, lh=1.3)
    # the states
    y = y0 + 214
    out += bar(12, y, 520, 24, c=4)
    for x, s, w, al in ((22, "State", 190, "left"), (212, "Levies", 140, "left"), (352, "Manpower", 90, "right"),
                        (452, "Vassals", 70, "right")):
        out += label(x, y + 8, s, 9.5, LABEL, w=w, align=al)
    y += 28
    for sid in G["states"]:
        lit = sid == picked
        if lit:
            out += lit_bar(12, y - 2, 520, 21, c=4)
        name = st[sid]["name"] + ("  ♛" if sid in R["royal"] else "")
        out += text(22, y + 3, name, 13.5, "#FBEAB4" if lit else CREAM, w=190)
        q = RM.levy(sid)
        out += pips(216, y + 6, q + 1) + text(276, y + 4, RM.LEVY[q], 12, CREAM2 if not lit else "#FBEAB4", w=80)
        out += value(352, y + 3, f"{st[sid]['manpower'] / 1000:,.0f} k", 13.5, CREAM, w=90, align="right")
        out += value(452, y + 3, str(R["vassals"].get(sid, 0)), 13.5, CREAM, w=70, align="right")
        y += 21
    y += 6
    out += fade_rule(12, y, 532) + label(12, y + 8, "Actions (the next step)", 9, LABEL, w=520, align="center")
    y += 22
    for i, s in enumerate(("Demand Levies", "Grant Privileges", "Send Inspectors", "Replace Governor")):
        out += button(12 + (i % 2) * 262, y + (i // 2) * 28, 258, 24, s, size=11, disabled=True)
    return out


def card_crown():
    R = RM.realm()
    st = R["st"]
    fiefs = [s for name in nations.ROYAL_FIEFS for s in R["royal"] if st[s]["name"] == name]
    host = {}
    for kind, n, where in nations.ROU_HOST:
        host[where] = host.get(where, 0) + n
    y0 = 566
    out = band(10, y0, 524, 38) + rule(10, y0 + 38, 534, "rgba(201,165,90,.6)")
    out += crown_seal(32, y0 + 19, 11, lit=True)
    out += title(52, y0 + 10, "The Crown's Domain", 19, w=330)
    out += label(330, y0 + 15, f"11 Royal Fiefs  ·  {sum(st[s]['manpower'] for s in fiefs) / 1e6:.2f} M men", 9.5, w=196, align="right")
    y = y0 + 50
    out += well(18, y, 78, 98, c=5) + portrait("roland_cahun", 19, y + 1, 76, 96)
    out += label(108, y + 2, "Held by the Prince", 9.5)
    out += text(108, y + 16, "Roland II Cahun", 19, CREAM, font="fed", track=.02)
    out += text(108, y + 40, "No governor and no estates: the Crown's own land", 12.5, CREAM2, font="bod", weight=500)
    out += label(108, y + 62, "The Royal Host", 9.5)
    in_fiefs = sum(n for where, n in host.items() if where in nations.ROYAL_FIEFS)
    out += text(108, y + 78, f"{sum(host.values())} divisions, {in_fiefs} of them stationed in the Royal Fiefs", 13.5, CREAM)
    y = y0 + 158
    out += label(18, y, "How the Crown gains fiefs", 9.5)
    out += text(18, y + 15, "A lord dies without an heir, the land escheats; a rebel governorate crushed is attainted; "
                "a fief bought or married into. (Ideas for later.)", 13, CREAM2, w=506, font="bod", weight=500, lh=1.3)
    y = y0 + 214
    out += bar(12, y, 520, 24, c=4)
    for x, s, w, al in ((22, "Royal Fief", 190, "left"), (212, "Levies", 140, "left"), (352, "Manpower", 90, "right"),
                        (452, "Host", 70, "right")):
        out += label(x, y + 8, s, 9.5, LABEL, w=w, align=al)
    y += 28
    for sid in fiefs:
        name = st[sid]["name"]
        out += text(22, y + 3, name, 13.5, CREAM, w=190)
        q = RM.levy(sid)
        out += pips(216, y + 6, q + 1) + text(276, y + 4, RM.LEVY[q], 12, CREAM2, w=80)
        out += value(352, y + 3, f"{st[sid]['manpower'] / 1000:,.0f} k", 13.5, CREAM, w=90, align="right")
        out += value(452, y + 3, str(host.get(name, "")) or "–", 13.5, CREAM, w=70, align="right")
        y += 24
    return out


def notes(crown):
    out = note(1490, 250, "<b>A mockup, not in the mod.</b> Every line on this map is a state border of the build "
               "(Rouental's 165 states, coloured by governorate), drawn again from the map at each build: no rough shapes.", 400)
    out += note(1490, 352, "Governors' names, loyalty, the estates' attitudes and levy quality are <b>placeholders</b> "
                "(names from the seats' fiefs, values made up) until you name and set them.", 400)
    if not crown:
        out += note(1490, 454, "Clicking: each governorate is covered by invisible buttons cut along its own state borders "
                    "(written by the build), so a click picks the governorate under the pointer; the octagons are its "
                    "seals. Picking a state in the list lights it on the map.", 400)
        out += note(1490, 574, "Vassals: the fiefs of your fief map inside each state (an abstract count for now; a list in "
                    "its tooltip).", 400)
    else:
        out += note(1490, 454, "The Royal Fiefs are the Crown's own: no governor, no estates, the best levies; the Royal "
                    "Host is raised here. They are hatched in gilt on the map and picked by the crown seal on Rêverie.", 400)
    return out


def hover_tooltip():
    """a governorate's tooltip, as the pointer rests on Vair"""
    R = RM.realm()
    # the easternmost governorate on the mainland but the selected one: its tooltip opens over the world map
    g = max((g for g in R["seal"] if g not in (SELECT, "Couronneterre", "Terres Séparées")), key=lambda g: R["seal"][g][0])
    G = RM.governorates()[g]
    lo, word, colour = RM.band(G["loyalty"])
    sx, sy, _ = R["seal"][g]
    x, y = MAP_X + sx * SCALE + 12, MAP_Y + sy * SCALE + 10
    out = box(x - 16, y - 14, 8, 8, "border-left:2px solid #F1DC9C;border-top:2px solid #F1DC9C")   # the pointer
    return out + tooltip(x, y, 262, 120, f"Governorate of {g}",
                   rows=[("Governor", G["governor"], CREAM), ("Loyalty", f"{G['loyalty']}  {word}", colour),
                         ("Estates", G["attitude"][0], CREAM), ("States", f"{len(G['states'])}  ·  {G['manpower'] / 1e6:.2f} M men", CREAM)])


def screen(crown=False):
    G = RM.governorates()
    picked = None if crown else G[SELECT]["states"][1]
    body = backdrop("map", dim=.15)
    body += panel() + realm_map(None if crown else SELECT, picked, crown)
    body += card_crown() if crown else card_governorate(SELECT, picked)
    body += notes(crown)
    if not crown:
        body += hover_tooltip()
    return body


def main():
    outs = []
    for crown, name in ((False, "governorates_gheso"), (True, "governorates_crown")):
        body = screen(crown)
        outs.append(render(body, os.path.join(HERE, name + ".png")))
        big = render(body, os.path.join(HERE, name + "_2x.png"), scale=2)
        im = Image.open(big)
        im.crop((0, 2 * 160, 2 * 545, 2 * 1080)).save(big, optimize=True)
    close_browser()
    print("\n".join(outs))


if __name__ == "__main__":
    main()
