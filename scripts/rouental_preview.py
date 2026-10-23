"""Previews of Rouental's governorates and three estates windows, drawn from the build's own .gui, .gfx and localisation
(scripts/rouental_ui.py's output) with the Deco UI's preview renderer (deco_ui/tools/validate_preview.py: its fonts,
its reading of positions), over the Deco UI's top bar and politics screen previews. The game's state is sampled: the
three estates on 1 June 2036 (the mockup's), the governorates' loyalty as they start, one governorate picked.

    python3 scripts/rouental_preview.py      (after a build and the Deco UI's build: deco_ui/build/preview_*.png)
Writes work/previews/rouental_three_estates.png and rouental_governorates.png.
"""
import contextlib
import io
import os
import re
import sys

import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, os.path.join(REPO, "deco_ui", "tools"))
with contextlib.redirect_stdout(io.StringIO()):
    import validate_preview as V  # noqa: E402
from imgio import read_dds  # noqa: E402
import rouental_realm as RM  # noqa: E402
import rouental_ui as UI  # noqa: E402

B = os.path.join(REPO, "build", "valsora_test") + "/"
DECO = os.path.join(REPO, "deco_ui", "valsora_deco_ui") + "/"
OUT = os.path.join(REPO, "work", "previews")


def sprites():
    for _k, body in V.load(B + "interface/valsora_rouental.gfx"):
        for kind, b in body:
            a = V.attrs(b)
            V.defs[a["name"]] = dict(kind=kind, frames=int(a.get("noofframes", 1)),
                                     img=Image.fromarray(read_dds(B + a["texturefile"])))
    V.defs["GFX_tiled_window_2b_border"] = dict(kind="corneredTileSpriteType", frames=1, border=(64, 64),
                                                img=V.read_dds(DECO + "gfx/interface/tiles/tiled_window_2b_border.dds"))
    V.defs["GFX_closebutton"] = dict(kind="spriteType", frames=1, img=V.read_dds(DECO + "gfx/interface/closebutton.dds"))
    gui = open(B + "interface/valsora_rouental.gui", encoding="utf-8").read()
    for name, scale in re.findall(r'spriteType = "(GFX_portrait_ROU_\w+)"\s*scale = ([\d.]+)', gui):
        im = Image.fromarray(read_dds(B + f"gfx/leaders/VAL/{name[len('GFX_portrait_'):]}.dds"))
        V.defs[name] = dict(kind="spriteType", frames=1,
                            img=im.resize((round(im.width * float(scale)), round(im.height * float(scale))), Image.LANCZOS))


def localisation(values):
    t = open(B + "localisation/english/valsora_rouental_l_english.yml", encoding="utf-8-sig").read()
    for k, v in re.findall(r'^\s*(\w+):0 "(.*)"$', t, re.M):
        for pat, rep in values.items():
            v = v.replace(pat, rep)
        V.loc[k] = v.replace("\\n", "\n")


def strip_hidden(elems, keep):
    out = []
    for k, body in elems:
        name = V.attrs(body).get("name") if isinstance(body, list) else None
        if name is not None and not keep(name):
            continue
        if k == "containerWindowType":
            body = [(kk, vv) for kk, vv in body if kk != "containerWindowType" and kk != "gridBoxType"] + \
                [(kk, vv) for kk, vv in strip_hidden([(kk, vv) for kk, vv in body if kk == "containerWindowType"], keep)]
            body = strip_children(body, keep)
        out.append((k, body))
    return out


def strip_children(body, keep):
    return [(k, v) for k, v in body if not (k in ("iconType", "buttonType", "instantTextBoxType")
                                            and not keep(V.attrs(v).get("name")))]


def window(name):
    gui = V.load(B + "interface/valsora_rouental.gui")
    for k, body in gui[0][1]:
        if V.attrs(body).get("name") == name:
            return body
    raise SystemExit(name)


def move(body, name, x, y):
    for i, (k, v) in enumerate(body):
        if k in ("iconType", "buttonType") and V.attrs(v).get("name") == name:
            body[i] = (k, [("position", [("x", str(round(x))), ("y", str(round(y)))]) if kk == "position" else (kk, vv)
                           for kk, vv in v])


def button_texts(cv, body, px, py):
    for k, v in body:
        if k == "buttonType":
            a = V.attrs(v)
            t = V.loc.get(a.get("buttontext"))
            if not t or a.get("spritetype") not in V.defs:
                continue
            img = V.defs[a["spritetype"]]["img"]
            x, y = (int(n) for n in V.xy(V.sub(v, "position")))
            V.draw_text(cv, a["buttonfont"], t, px + x, py + y + 1, img.width, "center", max_h=img.height, valign=True)


def save(cv, name):
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, name)
    Image.fromarray((np.clip(cv, 0, 1) * 255).astype(np.uint8)).save(p)
    return p


def backdrop(politics=False):
    src = "preview_politics.png" if politics else "preview_topbar.png"
    bg = Image.open(os.path.join(REPO, "deco_ui", "art", "map_rouental.jpg")).convert("RGB").resize((1920, 1080))
    top = Image.open(os.path.join(REPO, "deco_ui", "build", src)).convert("RGB")
    bg.paste(top, (0, 0))
    a = np.array(bg, np.float32) / 255
    if not politics:
        a[230:] *= .62
    return a


def three_estates(lords=False):
    """1 June 2036, the mockup's: the estates in balance, Royal Authority 35, the Court behind Roland (62), the Promised
    Reforms running; or (lords) 1 March 2037: the Second Estate over 60, the Lords' Realm, the Court behind Serelle"""
    if lords:
        trail = [(30, 40, 30), (28, 46, 26), (27, 51, 22), (25, 56, 19), (24, 60, 16), (23, 63, 14)]
        zi, ra, fav, lead = 1, 12, 43, "serelle"
    else:
        trail = [(35, 35, 30), (36, 35, 29), (33, 41, 26), (29, 37, 34), (33, 35, 32), (32, 36, 32)]
        zi, ra, fav, lead = 6, 35, 62, "roland"
    f, s, t = trail[-1]
    z = UI.ZONES[zi]
    k = abs(fav - 50) / 50
    court = ", ".join(f"{nm} {full * k * 100:+.0f}%" for _key, _m, full, nm in UI.FAVOUR[lead])
    localisation({"[GetRouEsZone]": z["name"], "[?rou_first|0]": str(f), "[?rou_second|0]": str(s), "[?rou_third|0]": str(t),
                  "[GetRouEsZoneDesc]": z["desc"], "[GetRouEsZoneWhere]": z["where"],
                  "[GetRouEsZoneEffects]": UI.zone_effects(z), "[GetRouEsZoneLeads]": z["leads"],
                  "[GetRouEsFirstLine]": UI.HOLDERS[0][2], "[GetRouEsSecondLine]": UI.HOLDERS[1][2],
                  "[GetRouEsThirdLine]": "§RShut out: their estates grow restive.§!" if lords else
                  "§YReform promised: 212 days left.§!",
                  "[?rou_es_d_first|+0]": "§R-3§!", "[?rou_es_d_second|+0]": "§G+1§!", "[?rou_es_d_third|+0]": "§G+2§!",
                  "[?rou_es_ra|0]": str(ra), "[GetRouEsRaBand]": UI.RA_BANDS[0 if lords else 1][1],
                  "[GetRouEsRaChange]": "§R-2 a month§!: one estate dominant" if lords else
                  "§G+1 a month§!: the estates in balance", "[?rou_es_breaking|0]": "5",
                  "[?rou_es_favour|0]": str(fav), "[?rou_es_serelle|0]": str(100 - fav),
                  "[GetRouEsCourt]": f"{lead.capitalize()} leads: {court}.",
                  "[?rou_es_reform_days|0]": "212", "[?rou_lean_first|+0]": "§R-2§!", "[?rou_lean_second|+0]": "§G+1§!",
                  "[?rou_lean_third|+0]": "§G+1§!", "[?rou_lean_crown|+0]": "§G+2§!"})
    cv = backdrop(politics=True)
    # the politics screen's button (docked to the politics panel: its x -6, its y 62)
    b = window("rou_es_button_window")
    V.render(cv, [("containerWindowType", b)], -6, 62, 544)
    w = window("rou_es_window")
    hidden = {"rou_es_risen", "rou_es_footer"}
    if lords:
        hidden |= {"rou_es_reform_label", "rou_es_reform_band", "rou_es_reform_days", "rou_es_reform_note", "rou_es_risen",
                   "rou_es_lean_label"} | {f"rou_es_lean_{k}{x}" for _a, k, _t in UI.LEANINGS for x in ("", "_swatch", "_v")}
        hidden -= {"rou_es_footer"}
    else:
        hidden |= {"rou_es_break_label", "rou_es_break_text", "rou_es_break_map"}
    lit = f"rou_es_zone_{z['key']}"
    body = strip_children(w, lambda n: n not in hidden and (not n.startswith("rou_es_zone_") or n in (
        lit, "rou_es_zone_band", "rou_es_zone_name", "rou_es_zone_desc", "rou_es_zone_where", "rou_es_zone_effects")))
    TX, TY = 30, 120
    mx, my = UI.at(f, s, t)
    move(body, "rou_es_marker", TX + mx - UI.MARK / 2, TY + my - UI.MARK / 2)
    for i, sh in enumerate(reversed(trail[:-1]), start=1):
        x, y = UI.at(*sh)
        move(body, f"rou_es_trail_{i}", TX + x - UI.DOT / 2, TY + y - UI.DOT / 2)
    for i in range(len(trail), 7):
        body = strip_children(body, lambda n, i=i: n != f"rou_es_trail_{i}")
    V.FRAME["rou_es_ra_bar"] = round(ra / 5)
    V.FRAME["rou_es_court_bar"] = round(fav / 5)
    wx, wy = (int(n) for n in V.xy(V.sub(w, "position")))
    V.render(cv, [("containerWindowType", body)], 0, 0, 1920)
    button_texts(cv, body, wx, wy)
    return save(cv, "rouental_three_estates_lords_realm.png" if lords else "rouental_three_estates.png")


def governorates(which="Graisivaudan"):
    R, G, P, govs, royal = UI.governorate_data()
    att_names = [x for x, _ in RM.ATTITUDES]
    band = {}
    for g in govs:
        loy = max(2, min(97, g["static"] + RM.ATTITUDE_MOD[att_names[g["att"] - 1]]))
        band[g["n"]] = 1 if loy >= 80 else 2 if loy >= 60 else 3 if loy >= 40 else 4 if loy >= 20 else 5
        g["loyalty"] = loy
    pick = next(g for g in govs if g["name"] == which)
    n = pick["n"]
    st = R["st"]
    lab = UI.BAND_NAMES[band[n] - 1]
    localisation({"[GetRouGovName]": f"Généralité of {pick['name']}", "[GetRouGovGovernor]": V.loc.get(f"ROU_GOV_{n}_GOVERNOR", ""),
                  "[GetRouGovOrigin]": pick["origin"], "[GetRouGovLoyalty]": f"§Y{pick['loyalty']}§!  {lab}",
                  "[GetRouGovAttitude]": f"{att_names[pick['att'] - 1]}  (next session: their temper may change)",
                  "[GetRouGovAttitudeDesc]": RM.ATTITUDES[pick["att"] - 1][1]})
    V.loc["ROU_GOV_SEL_GOVERNOR"] = f"Governor: {pick['governor']}"
    V.loc["ROU_GOV_SEL_PEOPLES"] = V.loc[f"ROU_GOV_{n}_PEOPLES"]
    cv = backdrop()
    w = window("rou_gov_window")
    def keep(nm):
        if (nm or "").startswith("rou_gov_hit_"):          # the click areas: all but clear
            return False
        m = re.match(r"rou_gov_(\d+)_b(\d)$", nm or "")
        if m:
            return band[int(m.group(1))] == int(m.group(2))
        if nm and (nm.endswith("_sel") or nm.endswith("_seal_lit")):
            return nm in (f"rou_gov_{n}_sel", f"rou_gov_{n}_seal_lit")
        return True
    body = strip_children(w, keep)
    FR = round(pick["loyalty"] / 5)
    V.FRAME["rou_gov_card_bar"] = max(1, min(20, FR)) - 1
    wx, wy = (int(v) for v in V.xy(V.sub(w, "position")))
    V.render(cv, [("containerWindowType", body)], 0, 0, 1920)
    button_texts(cv, body, wx, wy)
    # the states' list: the entry container once a row
    e = window("rou_gov_state_entry")
    gx, gy = 880, 370
    for i, s in enumerate(pick["states"]):
        name = st[s]["name"]
        V.SAMPLE.update({"rou_gov_state_name": name,
                         "rou_gov_state_people": RM.PEOPLES[P.get(s, RM.ROYAL_PEOPLE)][0],
                         "rou_gov_state_levy": "§YCeremonial§!" if name in RM.CEREMONIAL else
                         (RM.LEVY[RM.levy(s)] if i % 2 else "Unknown"),
                         "rou_gov_state_men": f"{round(st[s]['manpower'] / 1000)}k"})
        V.render(cv, [("containerWindowType", e)], wx + gx, wy + gy + i * 22, wx + gx + 430)
    cat = window("rou_gov_category_window")
    return save(cv, "rouental_governorates.png" if which == "Graisivaudan" else f"rouental_governorates_{RM_slug(which)}.png")


def RM_slug(name):
    return re.sub(r"[^a-z]+", "_", name.lower().replace("é", "e")).strip("_")


def main():
    sprites()
    print(three_estates())
    print(three_estates(lords=True))
    print(governorates())
    print(governorates("Terres Séparées"))
    print(governorates("Couronneterre"))


if __name__ == "__main__":
    main()
