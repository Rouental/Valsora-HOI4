"""The governorates' window: the mockup's second version (2026-10-21, night), after the author's answers to the first
(make.py): "Probably open as a larger window"; the governors "appointed by the Prince ... typically a member of the
Prince's court or officials recommended by Rouental's estates general. (Except Crépuscule, which is always ruled by the
Prince of Crépuscule ...)"; loyalty from the peoples (the Carcaraise against Rêverie, the Oscarl and the Chatois loyal);
"attitudes switching with estate sessions"; "I LOVE the levy quality being hidden until you send inspectors"; "Maybe a
late "ceremonial" category?"; "A governorates map mode probably isn't necessary".

Three screens at 1920 x 1080: the window opened from the decisions tab over the map, its realm drawn from the build's own
state borders (realm.py), seen three ways (loyalty, peoples, the levies the inspectors have seen):
  governorates_window_carcarelle.png   loyalty; Carcarelle selected (the Carcaraise, Defiant; two states inspected)
  governorates_window_crepuscule.png   peoples; Crépuscule selected (governed by its own Prince, by law)
  governorates_window_graisivaudan.png levies; Graisivaudan selected, inspected throughout (Grand Brume's Blue Guard:
                                       a ceremonial corps, a sidestep from the ladder)
  governorates_window_crown.png        levies; the Crown's Domain selected
Not in the mod; governors' names and every number but the manpower are placeholders.

    CHROMIUM_PATH=/opt/pw-browsers/chromium python3 make2.py   (after a build: reads build/valsora_test)
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "next_screens"))
sys.path.insert(0, HERE)
from deco import (CREAM, CREAM2, GILT, LABEL, backdrop, band, bar, box, button, fade_rule, header, label, lit_bar,  # noqa: E402
                  note, portrait, render, rule, silhouette, tab, text, title, value, well, window, close_browser)
from PIL import Image  # noqa: E402
import realm as RM  # noqa: E402  (puts the Valsora scripts on the path)
import nations  # noqa: E402
import make as M  # noqa: E402  (the decisions panel, the seals)

X0, Y0, WW, WH = 566, 104, 1338, 790       # the window, beside the decisions panel
SCALE = 2.6                                 # the realm, 320 x 182 map px: 832 x 473
MX, MY = X0 + 20, Y0 + 100
CX, CW = X0 + 876, 446                      # the card's column


def panel_behind():
    """the decisions panel the window opens from: the category's plate, its line and the button that opens it"""
    out = M.panel()
    out += M.text(18, 246, "The Prince's governors keep what order they can among the vassals of 26 governorates; "
                  "the eleven Royal Fiefs are the Crown's own.", 13, CREAM2, w=508, font="bod", weight=500, lh=1.35)
    out += button(118, 300, 308, 34, "Open the Map of the Realm", kind="gold", size=12.5)
    out += M.label(14, 352, "Decisions", 9.5, LABEL, w=516, align="left")
    for i, s in enumerate(("Summon the Estates General", "A Royal Progress through the Realm")):
        out += bar(10, 370 + i * 44, 524, 38, c=6) + text(24, 383 + i * 44, s, 14, CREAM2)
    return out


def realm_window(lens, select_gov=None, crown=False, picked=None):
    R = RM.realm()
    G = RM.governorates()
    out = box(0, 0, 1920, 1080, "background:rgba(4,7,9,.45)")            # the game dims nothing: the mockup does, to read it
    out += window(X0, Y0, WW, WH)
    out += header(X0 + 6, Y0 + 6, WW - 12, 44, "The Governorates of Rouental", 22, close_at=True)
    out += box(X0 + WW - 46, Y0 + 17, 22, 22, "transform:rotate(45deg);border:1.5px solid #E3C77E;background:#0E1519")
    out += text(X0 + WW - 46, Y0 + 20, "×", 17, GILT, w=22, align="center", weight=400)
    # the lenses
    for i, (k, s) in enumerate((("loyalty", "Loyalty"), ("peoples", "Peoples"), ("levies", "Levies seen"))):
        out += tab(MX + i * 158, Y0 + 60, 150, 28, s, lit=(k == lens), size=12.5)
    out += label(MX + 500, Y0 + 70, "The Estates General next sits: 1 June 2036", 9.5, LABEL, w=332, align="right")
    W, H = R["S"].shape[1] * SCALE, R["S"].shape[0] * SCALE
    out += well(MX - 4, MY - 4, W + 8, H + 8, c=6)
    out += f'<div class="a" style="left:{MX}px;top:{MY}px">{RM.map_svg(SCALE, select_gov, picked, crown, lens)}</div>'
    import numpy as np
    cap = next(s for s in R["royal"] if R["st"][s]["name"] == "Rêverie")
    ys, xs = np.nonzero(R["S"] == cap)
    out += M.crown_seal(MX + (xs.mean() + .5) * SCALE, MY + (ys.mean() + .5) * SCALE, 9, lit=crown)
    if select_gov:
        sx, sy, _ = R["seal"][select_gov]
        x, y = MX + sx * SCALE, MY + sy * SCALE
        if lens != "loyalty":
            out += M.seal(x, y, 6, RM.band(G[select_gov]["loyalty"])[2])
        out += text(x - 80, y + 10, select_gov, 14, "#FFF4D0", w=160, align="center", font="fed", track=.12, caps=True,
                    style="text-shadow:0 1px 2px #000,0 0 6px #000,0 0 3px #000")
    out += legend(lens, MY + H + 14)
    out += lower_strip(lens, MY + H + 46)
    return out


def legend(lens, y):
    out, x = "", MX
    if lens == "loyalty":
        items = [(c, n) for lo, n, c in RM.BANDS]
    elif lens == "peoples":
        items = [(v[1], v[0]) for v in RM.PEOPLES.values()]
    else:
        items = list(zip(RM.LEVY_COLOURS, RM.LEVY)) + [
            ("radial-gradient(circle,#E3C77E 0 1.2px,#2C4A63 1.4px) 0 0/4px 4px", "Ceremonial (a sidestep)"),
            ("repeating-linear-gradient(-45deg,#3A464C 0 .8px,#20292E .8px 3px)", "Not yet seen")]
    if lens != "levies":
        items.append(("repeating-linear-gradient(45deg,#C9A55A 0 1.1px,#6E5626 1.1px 3px)", "Royal Fief"))
    rows = [[]]
    for c, n in items:
        wdt = 16 + len(n) * 7.3 + 14
        if x + wdt > MX + 832:
            rows.append([])
            x = MX
        rows[-1].append((x, c, n))
        x += wdt
    for r, row in enumerate(rows):
        for x, c, n in row:
            out += box(x, y + r * 18 + 1, 11, 11, f"background:{c};box-shadow:0 0 0 1px rgba(227,199,126,.7)")
            out += label(x + 16, y + r * 18 + 2, n, 9.5, CREAM2)
    return out


def lower_strip(lens, y):
    """under the map: the peoples the author has written of (loyalty, peoples), or the inspectors' reports (levies)"""
    out = fade_rule(MX, y, MX + 832)
    if lens == "levies":
        out += label(MX, y + 12, "The inspectors' reports", 9.5)
        reports = [("Feb 2036", "Grand Brume", "the Blue Guard of Brume: two divisions of leg infantry, drilled to perfection "
                    "on their grandfathers' rifles (Ceremonial)"),
                   ("Jan 2036", "Carcarelle", "the levies of Carcarelle are Rabble: the Carcaraise lords send their worst"),
                   ("Dec 2035", "Spreivald", "the Oscarl of Spreivald are Veteran, and ask only to serve")]
        for i, (d, where, s) in enumerate(reports):
            out += value(MX, y + 32 + i * 24, d, 12.5, LABEL, w=80) + text(MX + 84, y + 31 + i * 24, s, 13.5, CREAM2,
                                                                          w=748, font="bod", weight=500)
        out += label(MX, y + 112, "A state's levies show once inspectors have seen them; the Crown knows its own fiefs'.", 9.5,
                     LABEL, w=832)
        return out
    out += label(MX, y + 12, "The peoples of the realm", 9.5)
    lore = [k for k, v in RM.PEOPLES.items() if v[3]]
    for i, k in enumerate(lore):
        name, colour, mod, line = RM.PEOPLES[k]
        x, yy = MX + (i % 2) * 420, y + 30 + (i // 2) * 60
        out += box(x, yy + 2, 12, 12, f"background:{colour};box-shadow:0 0 0 1px rgba(227,199,126,.7)")
        out += text(x + 20, yy, name, 15, CREAM, font="fed", track=.06)
        sign = f"{mod:+d}" if mod else "±0"
        out += value(x + 330, yy + 1, f"{sign} loyalty", 12.5, M.RM.BANDS[0][2] if mod > 0 else ("#E7A493" if mod < 0 else LABEL),
                     w=82, align="right")
        out += text(x + 20, yy + 20, line, 12.5, CREAM2, w=392, font="bod", weight=500, lh=1.25)
    return out


def governor_block(G, y):
    out = well(CX, y, 74, 92, c=5) + silhouette(CX + 1, y + 1, 72, 90)
    out += label(CX + 86, y + 2, "Governor", 9.5)
    out += text(CX + 86, y + 16, G["governor"], 19, CREAM, font="fed", track=.02)
    out += text(CX + 86, y + 41, G["origin"], 12.5, CREAM2, w=CW - 86, font="bod", weight=500)
    line = ("Crépuscule's own ruler, governing it for the Crown as those laws require." if G["governor"].startswith("The Prince")
            else "Charged with reining in the vassals: a governorate has little power of its own.")
    out += text(CX + 86, y + 60, line, 11.5, LABEL, w=CW - 86, lh=1.3)
    return out


def loyalty_block(G, y):
    lo, word, colour = RM.band(G["loyalty"])
    out = label(CX, y, "Loyalty to the Crown", 9.5)
    out += box(CX, y + 16, 330, 10, "background:#0A0F12;box-shadow:0 0 0 1px rgba(201,165,90,.55)")
    out += box(CX + 1, y + 17, 328 * G["loyalty"] / 100, 8, f"background:{colour}")
    for t in (20, 40, 60, 80):
        out += box(CX + 330 * t / 100, y + 14, 1, 14, "background:rgba(227,199,126,.45)")
    out += value(CX + 340, y + 8, str(G["loyalty"]), 22, CREAM, w=36, align="right")
    out += text(CX + 382, y + 13, word, 12.5, colour if word != "Defiant" else "#E7A493", font="fed", track=.06, caps=True)
    yy = y + 36
    for k, v in G["breakdown"]:
        if v == 0 and k != "Base":
            continue
        if k == "The peoples":
            main = max(G["shares"], key=G["shares"].get)
            k = f"The peoples: {RM.PEOPLES.get(main, (main,))[0]}" if main in RM.PEOPLES else k
        out += text(CX + 12, yy, k, 12.5, CREAM2, w=300)
        out += value(CX + 300, yy, f"{v:+d}" if k != "Base" else str(v), 12.5,
                     "#93D6A5" if (v > 0 and k != "Base") else ("#EE8C7E" if v < 0 else CREAM2), w=76, align="right")
        yy += 17
    return out, yy


def estates_block(g, G, y):
    att, desc = G["attitude"]
    out = label(CX, y, f"The Estates of {g}", 9.5)
    out += lit_bar(CX, y + 16, 124, 26, c=5) + text(CX, y + 23, att, 13, "#FBEAB4", w=124, align="center", font="fed",
                                                    track=.14, caps=True)
    out += text(CX + 136, y + 15, desc, 12.5, CREAM2, w=CW - 136, font="bod", weight=500, lh=1.3)
    out += text(CX, y + 50, "Next session in 4 months: their temper may change.", 11.5, LABEL, w=CW)
    return out


def peoples_row(G, y):
    out = label(CX, y, "Peoples", 9.5)
    x = CX
    total = sum(G["shares"].values())
    for p, n in sorted(G["shares"].items(), key=lambda kv: -kv[1]):
        name, colour = (RM.PEOPLES[p][0], RM.PEOPLES[p][1]) if p in RM.PEOPLES else ("The Crown's", "#C9A55A")
        s = f"{name} {100 * n / total:.0f} %"
        out += box(x, y + 18, 11, 11, f"background:{colour};box-shadow:0 0 0 1px rgba(227,199,126,.7)")
        out += text(x + 16, y + 17, s, 13, CREAM)
        x += 16 + len(s) * 7.4 + 16
    return out


def states_table(sids, y, picked, sel_known, kind="Vassals"):
    R = RM.realm()
    P, guessed = RM.peoples()
    st = R["st"]
    out = bar(CX - 4, y, CW + 8, 24, c=4)
    cols = ((CX + 6, "State", 120, "left"), (CX + 126, "People", 90, "left"), (CX + 218, "Levies", 110, "left"),
            (CX + 330, "Men", 56, "right"), (CX + 392, kind, 54, "right"))
    for x, s, w, al in cols:
        out += label(x, y + 8, s, 9.5, LABEL, w=w, align=al)
    y += 28
    for sid in sids:
        lit = sid == picked
        if lit:
            out += lit_bar(CX - 4, y - 2, CW + 8, 21, c=4)
        col = "#FBEAB4" if lit else CREAM
        name = st[sid]["name"]
        out += text(CX + 6, y + 3, name if len(name) < 17 else name[:15] + "…", 13, col, w=120)
        p = P[sid]
        pn = RM.PEOPLES[p][0] if p in RM.PEOPLES else "Crown"
        out += text(CX + 126, y + 4, pn + ("*" if sid in guessed else ""), 12, CREAM2 if not lit else col, w=90)
        if RM.inspected(sid, sel_known) and name in RM.CEREMONIAL:
            out += box(CX + 218, y + 1, 104, 17, "box-shadow:inset 0 0 0 1px #E3C77E;background:#1E3446")
            out += text(CX + 218, y + 4, "Ceremonial", 11.5, "#F1DC9C", w=104, align="center", font="fed", track=.1, caps=True)
        elif RM.inspected(sid, sel_known):
            q = RM.levy(sid)
            out += M.pips(CX + 220, y + 7, q + 1)
            out += text(CX + 278, y + 4, RM.LEVY[q], 11.5, CREAM2 if not lit else col, w=60)
        else:
            out += text(CX + 220, y + 4, "Unknown", 12, "rgba(183,166,128,.7)", w=100, font="bod", weight=500)
        out += value(CX + 330, y + 3, f"{st[sid]['manpower'] / 1000:,.0f}k", 12.5, col, w=56, align="right")
        if kind == "Vassals":
            out += value(CX + 392, y + 3, str(R["vassals"].get(sid, 0)), 12.5, col, w=54, align="right")
        y += 21
    return out, y


def actions(y, names, lit=()):
    out = fade_rule(CX, y, CX + CW) + label(CX, y + 8, "Actions (the next step)", 9, LABEL, w=CW, align="center")
    y += 22
    for i, s in enumerate(names):
        out += button(CX + (i % 2) * (CW // 2 + 2), y + (i // 2) * 28, CW // 2 - 2, 24, s, size=11,
                      kind="lit" if s in lit else "lacquer", disabled=s not in lit)
    return out


def card_governorate(g, picked, known):
    G = RM.governorates()[g]
    R = RM.realm()
    lo, word, colour = RM.band(G["loyalty"])
    y = Y0 + 60
    out = band(CX - 8, y, CW + 16, 38) + rule(CX - 8, y + 38, CX + CW + 8, "rgba(201,165,90,.6)")
    out += M.seal(CX + 12, y + 19, 11, colour)
    out += title(CX + 32, y + 10, f"Governorate of {g}", 19, w=CW - 30)
    y += 46
    out += label(CX, y, f"{len(G['states'])} states  ·  {G['manpower'] / 1e6:.2f} M men  ·  seat: {R['st'][G['seat']]['name']}",
                 9.5, LABEL, w=CW)
    out += governor_block(G, y + 18)
    b, y = loyalty_block(G, y + 122)
    out += b
    out += estates_block(g, G, y + 8)
    out += peoples_row(G, y + 80)
    t, y = states_table(G["states"], y + 122, picked, known)
    out += t
    for sid in G["states"]:
        name = R["st"][sid]["name"]
        if name in RM.CEREMONIAL and RM.inspected(sid, known):
            corps, what = RM.CEREMONIAL[name]
            corps = "the" + corps[3:] if corps.startswith("The ") else corps
            out += text(CX, y + 4, f"{name} keeps {corps}: {what[0].lower() + what[1:]}.", 12, "#F1DC9C", w=CW, font="bod",
                        weight=500, lh=1.3)
            y += 36
    out += actions(y + 8, ("Send Inspectors", "Drill the Levies", "Demand Levies", "Grant Privileges", "Summon the Estates",
                           "Replace the Governor"), lit=("Send Inspectors",))
    return out


def card_crown():
    R = RM.realm()
    st = R["st"]
    fiefs = [s for name in nations.ROYAL_FIEFS for s in R["royal"] if st[s]["name"] == name]
    host = {}
    for kind, n, where in nations.ROU_HOST:
        host[where] = host.get(where, 0) + n
    y = Y0 + 60
    out = band(CX - 8, y, CW + 16, 38) + rule(CX - 8, y + 38, CX + CW + 8, "rgba(201,165,90,.6)")
    out += M.crown_seal(CX + 12, y + 19, 11, lit=True)
    out += title(CX + 32, y + 10, "The Crown's Domain", 19, w=CW - 30)
    y += 46
    out += label(CX, y, f"11 Royal Fiefs  ·  {sum(st[s]['manpower'] for s in fiefs) / 1e6:.2f} M men  ·  seat: Rêverie", 9.5,
                 LABEL, w=CW)
    y += 18
    out += well(CX, y, 74, 92, c=5) + portrait("roland_cahun", CX + 1, y + 1, 72, 90)
    out += label(CX + 86, y + 2, "Held by the Prince", 9.5)
    out += text(CX + 86, y + 16, "Roland II Cahun", 19, CREAM, font="fed", track=.02)
    out += text(CX + 86, y + 41, "No governor and no estates: the Crown's own land", 12.5, CREAM2, w=CW - 86, font="bod",
                weight=500)
    in_fiefs = sum(n for where, n in host.items() if where in nations.ROYAL_FIEFS)
    out += text(CX + 86, y + 62, f"The Royal Host: {sum(host.values())} divisions, {in_fiefs} of them in the Royal Fiefs",
                12.5, CREAM, w=CW - 86, lh=1.3)
    y += 104
    out += label(CX, y, "How the Crown gains fiefs (ideas for later)", 9.5)
    out += text(CX, y + 15, "A governorate provoked to revolt and crushed, its lands annexed; a lord's death without an heir, "
                "the fief escheating to the Crown.", 12.5, CREAM2, w=CW, font="bod", weight=500, lh=1.3)
    t, y = states_table(fiefs, y + 62, None, (), kind="Host")
    out += t
    for i, sid in enumerate(fiefs):
        n = host.get(st[sid]["name"])
        out += value(CX + 392, y - 21 * (len(fiefs) - i) + 3, str(n) if n else "–", 12.5, CREAM, w=54, align="right")
    return out


def screen(which):
    G = RM.governorates()
    body = backdrop("map", dim=.2) + panel_behind()
    if which == "carcarelle":
        g = "Carcarelle"
        known = tuple(G[g]["states"][:2])
        body += realm_window("loyalty", g, picked=G[g]["states"][0]) + card_governorate(g, G[g]["states"][0], known)
    elif which == "crepuscule":
        g = "Crépuscule"
        body += realm_window("peoples", g, picked=None) + card_governorate(g, None, ())
    elif which == "graisivaudan":
        g = "Graisivaudan"
        brume = next(x for x in G[g]["states"] if RM.realm()["st"][x]["name"] == "Grand Brume")
        known = tuple(G[g]["states"])                      # inspectors have been through it all
        body += realm_window("levies", g, picked=brume) + card_governorate(g, brume, known)
    else:
        body += realm_window("levies", crown=True) + card_crown()
    body += note(14, 470, "<b>A mockup, not in the mod.</b> The window opens from the Governorates category; its map is "
                 "the build's own state borders. Governors' names and every number but the manpower are placeholders; "
                 "* marks a state whose people is guessed from its governorate.", 510)
    return body


def main():
    outs = []
    for which in ("carcarelle", "crepuscule", "graisivaudan", "crown"):
        body = screen(which)
        outs.append(render(body, os.path.join(HERE, f"governorates_window_{which}.png")))
    close_browser()
    print("\n".join(outs))


if __name__ == "__main__":
    main()
