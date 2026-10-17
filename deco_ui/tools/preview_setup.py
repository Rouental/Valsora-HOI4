"""Previews of the game setup screens on their new pictures (setup_art.py): the country selection (the Vale of
Reibonne's eight countries, the first selected), the start's window (Valsora's two starts) and the map's lobby (the
setup's top and bottom bars, the country's details, the difficulty panel, the Start button, and a strip of the minor
and mini cards and the filter buttons at 1:1, normal and selected). Each is drawn from the game's own .gui (Valsora
and the Deco UI ship none for this screen) over the map, as the game lays it out, with the game's pictures for the
_vanilla version.

    python preview_setup.py   -> build/preview_setup.png (+ _vanilla.png): the three screens one under the other

Flags, portraits and the starts' pictures are Valsora's (reference/valsora); the texts are samples from its
localisation. The typewriter fonts are drawn in black, as the game colours them (core.gfx). They show the game's art,
so they stay in the git-ignored build/ folder.
"""
import copy
import math
import re

import numpy as np
from PIL import Image, ImageDraw

import preview_panels as PP
import validate_preview as V
from paths import BUILD, VALSORA, VANILLA

GUI = VANILLA + "interface/frontendgamesetupview.gui"
TYPEWRITER = ("hoi4_typewriter16", "hoi4_typewriter22")
INK = (0, 0, 0)
SW, SH = 1920, 1080


def _norm(body):
    """the parsed .gui with every `Background` key written `background` (preview_panels looks for that spelling)"""
    out = []
    for k, v in body:
        if isinstance(v, list):
            v = _norm(v)
        out.append(("background" if k and k.lower() == "background" else k, v))
    return out


ELEMS = _norm(V.load(GUI))


def window(name):
    w = PP.find_window(ELEMS, name)
    assert w is not None, name
    return copy.deepcopy(w)


def find(body, name):
    for k, b in body:
        if isinstance(b, list):
            if V.attrs(b).get("name") == name:
                return k, b
            r = find(b, name)
            if r:
                return r
    return None


def placed(body, x, y):
    """a window put at (x, y) of its parent: its own position, anchors and slide positions dropped"""
    drop = ("position", "show_position", "hide_position", "orientation", "origo")
    return [(k, v) for k, v in body if not (k and k.lower() in drop)] + [("position", [("x", str(x)), ("y", str(y))])]


def shown(body, parent_w=SW):
    """every child window at its show_position (the screen as the player sees it), 50% read against the parent"""
    out = []
    for k, v in body:
        if isinstance(v, list) and k and k.lower() == "containerwindowtype":
            sp = V.sub(v, "show_position")
            if sp:
                x, y = V.xy(sp)
                x = str(parent_w * float(x.rstrip("%")) / 100) if str(x).endswith("%") else x
                v = [(kk, vv) for kk, vv in v if not (kk and kk.lower() in ("position", "show_position"))] + \
                    [("position", [("x", str(x)), ("y", str(y))])]
            v = shown(v, parent_w)
        out.append((k, v))
    return out


class Setup(PP.Panel):
    """the panel renderer, with the typewriter fonts in black (the game's colour) and the boxes in `free` allowed to
    run to as many lines as the text needs (the game grows the history's box)"""
    free = ("history", "bookmark_desc")

    def text(self, cv, text, font, x, y, w, h, fmt, name, valign=False):
        f = (font or "").strip('"')
        if name in self.free:
            h = None
        if f not in TYPEWRITER:
            return super().text(cv, text, font, x, y, w, h, fmt, name, valign)
        text = PP.LOC.get(str(text).strip('"'), str(text).strip('"'))
        text = re.sub(r"\$[^$\s]*\$", "12", text).replace("\\n", "\n")
        if f in V.FONTS and not self.vanilla_only:
            V.draw_text(cv, f, text, x, y, w, fmt, color=INK, max_h=h if h else (400 if name in self.free else None),
                        valign=valign, check=name)
        else:                       # the game's look: its typewriter approximated in black
            s = PP.clean_loc(text)
            px = PP.vanilla_font_px(f)
            im = Image.new("RGBA", (max(1, w or 400), 200 if name in self.free else px + 8), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            lines, cur = [], ""
            for word in s.split():
                t = (cur + " " + word).strip()
                if w and d.textlength(t, font=PP.ttf(px)) > w and cur:
                    lines.append(cur)
                    cur = word
                else:
                    cur = t
            lines.append(cur)
            for i, ln in enumerate(lines if name in self.free else lines[:1]):
                tw = d.textlength(ln, font=PP.ttf(px))
                tx = (im.width - tw) / 2 if fmt in ("center", "centre") else 0
                d.text((tx, i * (px + 4)), ln, font=PP.ttf(px), fill=(*INK, 255))
            V.paste(cv, im, x, y)


# ---------------------------------------------------------------- sample content (Valsora's)
VALE = ["ROU", "GDN", "LST", "EVR", "HLR", "SGV", "LZC", "SGN"]
NAMES = {"ROU": "Rouental", "GDN": "Guedelon", "LST": "Lustiana", "EVR": "Evriches", "HLR": "Hollier",
         "SGV": "Selgrave", "LZC": "Lanzerac", "SGN": "Seigne", "AIS": "Merlovich"}


def img(path):
    for p in (path, path[:-4] + ".dds", path[:-4] + ".tga"):
        try:
            return Image.open(p).convert("RGBA")
        except OSError:
            continue
    return None


def flag(tag, size="large"):
    sub = {"large": "", "medium": "medium/", "small": "small/"}[size]
    im = img(VALSORA + f"gfx/flags/{sub}{tag}.tga")
    return im


def portrait(tag, i):
    if tag == "ROU":
        return img(VALSORA + "gfx/leaders/VAL/ROU_roland_cahun.dds")
    return img(VANILLA + f"gfx/leaders/Europe/Portrait_Europe_Generic_{1 + i % 3}.dds")


def scaled(im, s):
    return im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)


def frame(spr, n, vanilla):
    d, im = PP.sprite(spr, vanilla)
    return PP.frame_of(im, d, n)


IDEAS = ["generic_economic_increase", "generic_disjointed_gov"]
GOALS = ["focus_generic_advisors", "focus_generic_advanced_military_studies", "focus_generic_aegean_sea_focus"]


def idea(n):
    return img(VANILLA + f"gfx/interface/ideas/idea_{n}.dds") or img(VANILLA + f"gfx/interface/ideas/{n}.dds")


def goal(n):
    return img(VANILLA + f"gfx/interface/goals/{n}.dds")


def pie(r=26):
    im = Image.new("RGBA", (2 * r + 1, 2 * r + 1), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    a = -90
    for share, col in ((.42, (128, 48, 168)), (.2, (20, 20, 20)), (.18, (60, 120, 200)), (.12, (190, 30, 30)), (.08, (238, 238, 238))):
        d.pieslice((0, 0, 2 * r, 2 * r), a, a + share * 360, fill=(*col, 255))
        a += share * 360
    return im


# ---------------------------------------------------------------- the screens
def bars(cv, vanilla, hide=()):
    """the setup's top and bottom bars, as shown"""
    root = shown(window("frontendgamesetupview"))
    p = Setup(vanilla_only=vanilla, outline_lists=False,
              hide={"observer_button", "observer_button_overlay", "mapmode_button_1", "mapmode_button_2_s",
                    "play_button_ready", "play_button_checkbox", *hide},
              samples={"date": "1 January 2036, 12:00", "name": "The Vale of Reibonne",
                       "selected_nation_label": "Rouental"},
              frames={"extended_country_button": 0, "enabled_achievement_icons": 2})
    p.draw(cv, [("containerWindowType", root)], 0, 0, SW, SH)
    # the player's flag in the top bar's frame (the game masks it with shield_medium_mask: 82 x 52)
    k, b = find(root, "player_shield")
    f = flag("ROU")
    if f:
        V.paste(cv, f, SW - 449, 18)
    k2, b2 = find(root, "large_flag_frame")
    Setup(vanilla_only=vanilla).draw(cv, [(k2, b2)], SW, -30, 0, 128)   # UPPER_RIGHT of the top bar (at y -30)
    return root


def country_selection(vanilla):
    cv = PP.backdrop(False)
    bars(cv, vanilla)
    w = window("gamesetup_interesting_countries_window")
    WX, WY = (SW - 1225) // 2, (SH - 717) // 2
    hide = {"minor_country_leader", "minor_portrait_overlay"}
    samples = {"nation_title": "The Sacred Principality of Rouental", "leader": "Roland II Cahun", "ideology": "Monarchist",
               "government": "Absolute Monarchy", "elections": "None", "party": "The Crown",
               "history": PP.LOC.get("VALSORA_HISTORY_ROU") or
               "The Sacred Principality of Rouental rules the Vale of Reibonne from Rêverie under Prince Roland II Cahun, "
               "and leads the Association of Reibonnaise States."}
    p = Setup(vanilla_only=vanilla, outline_lists=False, hide=hide, samples=samples, frames={"pol_faction_icon": 3})
    p.draw(cv, [("containerWindowType", placed(w, 0, 0))], WX, WY, SW, SH)
    # the major countries' cards (the game's country_entry, 150 apart from (15, 41)), the first selected
    entry = window("country_entry")
    for i, tag in enumerate(VALE):
        ex, ey = WX + 15 + 150 * i, WY + 41
        po = portrait(tag, i)
        if po:
            V.paste(cv, scaled(po, .75), ex + 17, ey + 22)
        f = flag(tag)
        if f:
            V.paste(cv, f, ex + 34, ey + 188)
        Setup(vanilla_only=vanilla, hide={"country_leader", "country_flag", "new_content"},
              samples={"country_name": NAMES[tag]}, frames={"country": 1 if i == 0 else 0}).draw(
            cv, [("containerWindowType", placed(entry, 0, 0))], ex, ey, 150, 274)
    # the spirits (60 x 66 slots from (542, 486)) and the focuses (105 apart from (477, 580), 60 x 80 entries)
    for i, n in enumerate(IDEAS):
        im = idea(n)
        if im:
            V.paste(cv, im, WX + 542 + 60 * i + 30 - im.width / 2, WY + 486 + 33 - im.height / 2)
    for i, n in enumerate(GOALS):
        im = goal(n)
        if im:
            V.paste(cv, im, WX + 477 + 105 * i + 30 - im.width / 2, WY + 580 + 40 - im.height / 2)
    # the pinned portrait: 0.696 of the portrait, turned by the .gui's rotation (-0.04: clockwise on screen, about its
    # middle), then the overlay over it
    po = scaled(portrait("ROU", 0), .696)
    rot = po.rotate(-math.degrees(.04), resample=Image.BICUBIC, expand=True)
    cx, cy = WX + 289 + po.width / 2, WY + 457 + po.height / 2
    V.paste(cv, rot, cx - rot.width / 2, cy - rot.height / 2)
    k, b = find(w, "minor_portrait_overlay")
    Setup(vanilla_only=vanilla).draw(cv, [(k, b)], WX, WY, 1225, 717)
    return cv


def start_selection(vanilla):
    cv = PP.backdrop(False)
    bars(cv, vanilla)
    w = window("gamesetup_scenario_window")
    WX, WY = (SW - 579) // 2, (SH - 512) // 2
    p = Setup(vanilla_only=vanilla, outline_lists=False,
              samples={"bookmark_title": "The Vale of Reibonne",
                       "bookmark_desc": PP.LOC.get("VALSORA_BOOKMARK_VALE_DESC")
                       or "Rouental and the Association of Reibonnaise States, 1 January 2036."})
    p.draw(cv, [("containerWindowType", placed(w, 0, 0))], WX, WY, SW, SH)
    entry = window("bookmark_entry")
    for i, pic in enumerate(("valsora_select_date", "valsora_select_date_vale")):
        ex, ey = WX + 43 + 260 * i, WY + 55
        V.paste(cv, frame("GFX_bookmark_entry_bg", 1 if i == 1 else 0, vanilla), ex, ey)
        im = img(VALSORA + f"gfx/interface/{pic}.dds")
        if im:
            V.paste(cv, im, ex + 27, ey + 28)
        e = [(k, v) for k, v in entry if not (k == "background")]
        Setup(vanilla_only=vanilla, hide={"icon"}, samples={"date": "1 January, 2036"}).draw(
            cv, [("containerWindowType", placed(e, 0, 0))], ex, ey, 232, 211)
    return cv


def lobby(vanilla):
    cv = PP.backdrop(False)
    # the country's details at the upper right (upper_right, show (20, 90))
    w = window("gamesetup_country_details")
    WX, WY = SW - 20 - 492, 90
    hide = {"country_leader", "country_leader_frame", "pol_view_bg", "piechart_frame", "spirit_grid_over_defined"}
    p = Setup(vanilla_only=vanilla, outline_lists=False, hide=hide, frames={"pol_faction_icon": 3},
              samples={"leader": "Roland II Cahun", "ideology": "Monarchist", "government": "Absolute Monarchy",
                       "elections": "None", "party": "The Crown"})
    p.draw(cv, [("containerWindowType", placed(w, 0, 0))], WX, WY, SW, SH)
    V.paste(cv, scaled(portrait("ROU", 0), .4), WX + 30, WY + 20)
    V.paste(cv, pie(), WX + 205 - 26, WY + 37)
    for name in ("country_leader_frame",):
        k, b = find(w, name)
        Setup(vanilla_only=vanilla).draw(cv, [(k, b)], WX, WY, 492, 301)
    for name in ("pol_view_bg", "piechart_frame"):
        k, b = find(w, name)
        Setup(vanilla_only=vanilla).draw(cv, [(k, b)], WX + 185, WY + 40, 100, 100)
    for i, n in enumerate(IDEAS):
        im = idea(n)
        if im:
            V.paste(cv, im, WX + 253 + 60 * i + 30 - im.width / 2, WY + 30 + 34 - im.height / 2)
    # the difficulty panel (lower_right, show (5, -85), 598 x 196), normal selected
    g = window("gamesetup_gameplay_settings_window")
    GX, GY = SW - 5 - 598, SH - 85 - 196
    Setup(vanilla_only=vanilla, outline_lists=False, frames={"normal_cb": 1}).draw(
        cv, [("containerWindowType", placed(g, 0, 0))], GX, GY, SW, SH)
    bars(cv, vanilla)
    # a strip of the cards and buttons at 1:1: minor and mini cards (normal, selected), filter buttons (lit, plain)
    x, y = 470, 300
    V.paste(cv, Image.new("RGBA", (980, 150), (11, 16, 20, 200)), x - 10, y - 10)
    for i, tag in enumerate(("HLR", "SGV")):
        f = flag(tag)
        if f:
            V.paste(cv, f, x + 150 * i + 26, y + 22)
        V.paste(cv, frame("GFX_country_selection_minor_entry", i, vanilla), x + 150 * i, y)
    for i, tag in enumerate(("LZC", "SGN", "EVR")):
        f = flag(tag, "medium")
        if f:
            V.paste(cv, f, x + 310 + 60 * i + 9, y + 8)
        V.paste(cv, frame("GFX_mini_country_selector", 1 if i == 1 else 0, vanilla), x + 310 + 60 * i, y)
    filt = window("country_filter")
    for i in range(2):
        Setup(vanilla_only=vanilla, frames={"button": i}).draw(cv, [("containerWindowType", placed(filt, 0, 0))],
                                                                x + 500 + 160 * i, y, 149, 33)
    return cv


def sheet(vanilla):
    rows = [country_selection(vanilla), start_selection(vanilla), lobby(vanilla)]
    out = Image.new("RGB", (SW, SH * len(rows)))
    for i, cv in enumerate(rows):
        out.paste(Image.fromarray((np.clip(cv, 0, 1) * 255).astype(np.uint8)), (0, SH * i))
    name = "preview_setup" + ("_vanilla" if vanilla else "") + ".png"
    out.save(BUILD + name)
    return name


if __name__ == "__main__":
    n = len(V.problems)
    print("wrote build/" + sheet(False))
    print("wrote build/" + sheet(True))
    print("text problems:", [q for q in V.problems[n:] if "overflow" in q or "lines" in q])
