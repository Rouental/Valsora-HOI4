"""Approximate in-game previews of the restyled screens, rendered from the mod's generated .gui/.gfx.

Reuses the parser, sprite table, fonts and drawing helpers of validate_preview.py (importing it also
re-runs its checks and the top bar preview). Vanilla art the mod does not replace is drawn as neutral
stand-ins; sample data (portrait, parties, spirits, laws) stands in for what the game fills in.
"""
import re
import sys

import numpy as np
from PIL import Image, ImageDraw

import validate_preview as V
from paths import ART, BUILD, VALSORA

M = V.M
defs = V.defs


def tex(rel):
    return V.read_tex(rel)


# vanilla sprite names whose textures the core skin replaces at their vanilla paths
for name, rel, size, border in [
    ("GFX_tiled_plain_bg", "gfx/interface/tiles/tiled_plain_bg.dds", (192, 192), (64, 64)),
    ("GFX_tiled_window_1b_border", "gfx/interface/tiles/tiled_window_1b_border.dds", (192, 192), (64, 64)),
    ("GFX_tiled_window2_1b_border", "gfx/interface/tiles/tiled_window2_1b_border.dds", (192, 192), (64, 64)),
]:
    defs[name] = dict(kind="corneredTileSpriteType", frames=1, img=tex(rel), size=size, border=border)
CLEAR = Image.new("RGBA", (3, 3), (0, 0, 0, 0))
defs["GFX_tiled_window_transparent"] = dict(kind="corneredTileSpriteType", frames=1, img=CLEAR, size=(3, 3), border=(1, 1))

ROU = VALSORA
PORTRAIT = Image.open(ROU + "gfx/leaders/VAL/ROU_roland_cahun.dds").convert("RGBA")
SPIRIT = Image.open(ROU + "gfx/interface/ideas/ROU_feudal_army.dds").convert("RGBA")
PARTIES = [("Monarchist", (128, 74, 168)), ("Theocratic", (230, 230, 230)), ("Democratic", (64, 96, 210)),
           ("Communist", (200, 48, 40)), ("Authoritarian", (40, 40, 40))]


def standin(w, h, glyph="", round_=False):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if round_:
        d.ellipse((1, 1, w - 2, h - 2), fill=(70, 64, 54, 235), outline=(150, 140, 120, 255))
    else:
        d.rounded_rectangle((1, 1, w - 2, h - 2), 3, fill=(70, 64, 54, 235), outline=(150, 140, 120, 255))
    if glyph:
        d.text((w / 2 - 3, h / 2 - 6), glyph, fill=(220, 210, 190, 255))
    return im


STANDIN = {"GFX_pol_factions_strip": (standin(60, 60, "M", True), 1), "GFX_rules_sum_icon": (standin(26, 26, "R"), 1),
           "GFX_icon_occupied_territories": (standin(28, 28, "O"), 1),
           "GFX_icon_exiled_governments": (standin(28, 28, "E"), 1), "GFX_icon_manage_subjects": (standin(28, 28, "S"), 1),
           "GFX_tension_war_list_major": (standin(28, 28, "F"), 1), "GFX_icon_button_32x32": (standin(32, 32, "i"), 1),
           "GFX_relation_faction": (CLEAR, 1), "GFX_idea_categories": (standin(56, 24, "cat"), 1),
           "GFX_idea_traits_strip": (CLEAR, 1)}
SKIP = {"power_balance_button", "autonomy_progress_view", "in_faction", "original_in_faction", "nat_spirit_glow_overlay",
        "valsora_deco_pol_faction_role_window",
        "continuous_glow", "continuous_small_glow", "tutorial_glow", "focus_cost", "pol_power_icon",
        "drop_continuous_focus_button", "idea_alert_glow", "dismantle_faction"}
N_SPIRITS = 1          # Rouental has one; the second preview shows Devlon's 15 test spirits
import layout_politics as LP  # noqa: E402
# sample values as the game shows them (in game, v0.4.7)
TEXT = {"political_title": "Government", "ideology": "Monarchist", "leader_name": "Roland II Cahun",
        "elections": "No Elections", "view_factions_text": "Create Faction",
        "valsora_deco_pol_party": "Monarchist · 20%", "valsora_deco_pol_last_election": "None",
        "valsora_deco_pol_pp": "851  §G+1.83§!", "valsora_deco_pol_sub_ideology_text": "Feudalism",
        "title": None, "manage_occupied_button_text": "Occupied Territories",
        "manage_exiled_collaborations_governments": "Exiled Governments", "show_subjects_button_text": "Manage Subjects",
        "valsora_deco_pol_title": "The Sacred Principality of Rouental"}
FOCUS_TITLE = "Kick Out the Parasites (Rudely)"
CATEGORIES = [("Political Advisors", 3), ("Laws", 3), ("Economy", 1)]


def templates(gui):
    return {V.attrs(b).get("name"): b for k, b in gui[0][1] if k}


def render(cv, elems, px, py, pr, T, ctx=None):
    for key, body in elems:
        kl = key.lower() if key else None
        if kl not in ("containerwindowtype", "icontype", "buttontype", "instanttextboxtype", "gridboxtype"):
            continue
        d = V.attrs(body)
        name = d.get("name")
        if name in SKIP:
            continue
        pos = V.sub(body, "position")
        x, y = (int(float(v)) for v in V.xy(pos)) if pos else (0, 0)
        ori = d.get("orientation", "UPPER_LEFT").upper()
        ax = pr + x if ori == "UPPER_RIGHT" else px + x
        ay = py + y
        if kl == "containerwindowtype":
            sz = V.sub(body, "size")
            w, h = V.xy(sz) if sz else (0, 0)
            w = pr - ax if "%" in str(w) else int(w)
            h = (1080 - ay) if "%" in str(h) else int(h)
            bg = V.sub(body, "background")
            if bg:
                spr = V.attrs(bg).get("quadtexturesprite") or V.attrs(bg).get("spritetype")
                if spr in defs:
                    dd = defs[spr]
                    img = V.cornered(dd["img"], w, h, *dd["border"]) if dd["kind"] == "corneredTileSpriteType" else dd["img"]
                    V.paste(cv, img, ax, ay)
            render(cv, body, ax, ay, ax + w, T, ctx)
        elif kl == "gridboxtype":
            slot = V.sub(body, "slotsize")
            sw, sh = (int(v) for v in V.xy(slot))
            if name == "parties_grid":
                for i, (pn, col) in enumerate(PARTIES):
                    render(cv, T["political_party_info_entry"], ax, ay + i * sh, ax + 330, T, dict(party=(pn, col, i == 0)))
            elif name == "spirit_grid" and N_SPIRITS <= LP.SPIRIT_ROWS * ((LP.SPIRITS["w"] - 8) // sw):
                for i in range(N_SPIRITS):
                    per = (LP.SPIRITS["w"] - 8) // sw
                    V.paste(cv, SPIRIT.resize((56, 56), Image.LANCZOS), ax + (i % per) * sw + 2, ay + (i // per) * sh + 4)
            elif name == "spirit_grid_over_defined" and N_SPIRITS > LP.SPIRIT_ROWS * ((LP.SPIRITS["w"] - 8) // LP.SPIRIT_SLOT[0]):
                per = int(d.get("max_slots_horizontal", 7))
                for i in range(N_SPIRITS):
                    V.paste(cv, SPIRIT.resize((30, 30), Image.LANCZOS), ax + (i % per) * sw + 1, ay + (i // per) * sh + 2)
            elif name == "idea_categories_grid":
                for i, (cn, n) in enumerate(CATEGORIES):
                    render(cv, T["country_politics_idea_category_entry"], ax, ay + 14 + i * sh, ax + 550, T,
                           dict(category=(cn, n)))
            elif name == "ideas_grid" and ctx and "category" in ctx:
                for i in range(ctx["category"][1]):
                    render(cv, T["political_idea_entry"], ax + i * (sw + 10), ay, ax + 53, T, ctx)
        elif kl in ("icontype", "buttontype"):
            spr = d.get("quadtexturesprite") or d.get("spritetype")
            frame = int(d.get("frame", 1)) - 1
            scale = float(d.get("scale", 1))
            if name == "leader":
                V.paste(cv, PORTRAIT, ax, ay)
                continue
            if name == "chart" and spr in ("GFX_political_chart", "GFX_valsora_deco_pol_chart"):
                r = LP.PIE["r"] if spr == "GFX_valsora_deco_pol_chart" else 27
                im = Image.new("RGBA", (2 * r, 2 * r), (0, 0, 0, 0))
                dr = ImageDraw.Draw(im)
                for i, (_, col) in enumerate(PARTIES):
                    dr.pieslice((0, 0, 2 * r - 1, 2 * r - 1), -90 + i * 72, -90 + (i + 1) * 72, fill=col + (255,))
                V.paste(cv, im, ax - r + 1, ay)
                continue
            if name == "goal_icon":
                im = standin(int(94 * scale), int(84 * scale), "focus")
                V.paste(cv, im, ax - im.width // 2, ay - im.height // 2)
                continue
            if name == "color_block" and ctx and "party" in ctx:
                dia = defs[spr]["img"].copy() if spr in defs else Image.new("RGBA", (10, 6), (255, 255, 255, 255))
                tint = Image.new("RGBA", dia.size, ctx["party"][1] + (255,))
                tint.putalpha(dia.getchannel("A"))
                V.paste(cv, tint, ax, ay)
                continue
            if name == "leading_pol_party_bg" and not (ctx and ctx.get("party", (0, 0, False))[2]):
                continue
            if name == "progress":
                w_ = int(LP.FOCUS_BAR["w"] * .62)
                cv[ay:ay + LP.FOCUS_BAR["h"], ax:ax + w_] = np.array((228, 198, 126), np.float32) / 255
                continue
            if spr in defs:
                dd = defs[spr]
                img = dd["img"]
                if scale != 1:
                    fw = img.width // dd["frames"]
                    img = img.crop((frame * fw, 0, (frame + 1) * fw, img.height)).resize(
                        (max(1, int(fw * scale)), max(1, int(img.height * scale))), Image.LANCZOS)
                    V.paste(cv, img, ax, ay)
                else:
                    V.paste(cv, img, ax, ay, min(frame, dd["frames"] - 1), dd["frames"])
            elif spr in STANDIN:
                im, _ = STANDIN[spr]
                if scale != 1:
                    im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))))
                V.paste(cv, im, ax, ay)
            elif spr and spr.startswith("GFX_"):
                V.problems.append(f"preview: no art for {name} ({spr})")
        else:
            if name == "name" and ctx and "party" in ctx:
                txt = f"{ctx['party'][0]}  20%"
            elif name == "name" and ctx and "category" in ctx:
                txt = ctx["category"][0]
            elif name == "title" and ctx is None and d.get("text") == "POLITICS_ACTIVE_GOAL":
                txt = FOCUS_TITLE
            elif name == "title" and d.get("text") == "POLITICS_NATIONAL_SPIRIT":
                txt = "National Spirits"
            else:
                txt = TEXT.get(name) or V.loc.get(d.get("text"), None) or POL_LOC.get(d.get("text"))
            if not txt:
                continue
            font = d.get("font")
            if font not in V.FONTS:
                continue  # vanilla font: not previewed
            mw = int(d.get("maxwidth", 0)) or None
            mh = int(d.get("maxheight", 0)) or None
            V.draw_text(cv, font, txt, ax, ay, mw, d.get("format", "left"), max_h=mh,
                        valign=d.get("vertical_alignment") == "center", check=name)


POL_LOC = {}
for line in open(M + "localisation/english/valsora_deco_politics_l_english.yml", encoding="utf-8-sig"):
    m = re.match(r'\s*(\w+):0 "(.*)"', line)
    if m:
        POL_LOC[m.group(1)] = m.group(2)

if __name__ == "__main__":
    full = Image.open(ART + "map_rouental.jpg").convert("RGB").resize((1920, 1080), Image.LANCZOS)
    cv = np.array(full, np.float32) / 255
    # top bar first (as in game)
    V.BOXES.clear()
    top = V.gui[0][1]
    tb = next(b for k, b in top if k == "containerWindowType" and V.attrs(b).get("name") == "topbar")
    V.render(cv, [("containerWindowType", tb)], 0, 0, 1920)
    V.render(cv, [(k, b) for k, b in V.extras[0][1] if V.attrs(b).get("name") != "valsora_deco_country_name_small_window"],
             -4, -1, 1920)
    pol = V.load(M + "interface/countrypoliticsview.gui")
    T = templates(pol)
    panel = T["countrypoliticsview"]
    shown = V.xy(V.sub(panel, "show_position"))
    assert (int(shown[0]), int(shown[1])) == (LP.PANEL_X, LP.TOP), shown
    ex = V.load(M + "interface/valsora_deco_politics_extras.gui")
    base = cv.copy()
    for N_SPIRITS, name in ((1, "preview_politics"), (15, "preview_politics_many_spirits")):
        cv = base.copy()
        # shown position: flush under the top bar's band
        render(cv, [("containerWindowType", [(k, v) for k, v in panel if not (k and k.lower() == "position")]
                     + [("position", [("x", str(LP.PANEL_X)), ("y", str(LP.TOP))])])], 0, 0, 1920, T)
        render(cv, ex[0][1], LP.PANEL_X, LP.TOP, LP.PANEL_X + LP.PANEL_W, T)
        out = Image.fromarray((np.clip(cv, 0, 1) * 255).astype(np.uint8))
        if N_SPIRITS == 1:
            out.save(BUILD + "preview_politics_full.png")
        out.crop((0, 0, 760, 1080)).save(BUILD + name + ".png")
    print("politics preview written; problems:", [p for p in V.problems if "preview" in p or "overflow" in p or "lines" in p])


# ================================================================ main menu
MENU_TEXT = {"FE_SINGLE_PLAYER": "Single Player", "FE_MULTI_PLAYER": "Multiplayer", "OPTIONS": "Settings",
             "MENU_BAR_CAREER_PROFILE": "Career Profile", "MENU_BAR_FRIENDS": "Friends", "FE_CREDITS": "Credits",
             "Nudge!": "Nudge!", "FE_EXIT": "Exit", "ALPHA": "v1.17.4.1 (2a3f)"}


def preview_menu():
    bg = V.read_tex("gfx/loadingscreens/valsora_menu.dds").crop((0, 180, 1920, 1260)).convert("RGB")
    cv = np.array(bg, np.float32) / 255
    g = V.load(M + "interface/frontendmainview.gui")
    T = templates(g)
    panel = T["mainmenu_panel_bottom"]
    d = V.attrs(panel)
    w, h = (int(v) for v in V.xy(V.sub(panel, "size")))
    px, py = (int(v) for v in V.xy(V.sub(panel, "position")))
    # CENTER_DOWN with explicit offsets and no Origo (with Origo center_down the buttons did not show in game)
    assert d["orientation"].upper() == "CENTER_DOWN" and "origo" not in d, "menu panel anchoring changed"
    ox, oy = 960 + px, 1080 + py
    assert 0 <= ox and ox + w <= 1920 and 0 <= oy and oy + h <= 1080, ("menu panel off-screen", ox, oy, w, h)
    for key, body in panel:
        if not key or key.lower() not in ("buttontype", "icontype", "instanttextboxtype"):
            continue
        a = V.attrs(body)
        x, y = (int(v) for v in V.xy(V.sub(body, "position")))
        spr = a.get("quadtexturesprite") or a.get("spritetype")
        if key.lower() == "buttontype" and spr in defs:
            dd = defs[spr]
            V.paste(cv, dd["img"], ox + x, oy + y, 0, dd["frames"])
            fw, fh = dd["img"].width // dd["frames"], dd["img"].height
            font = a.get("buttonfont") or a.get("font")
            txt = MENU_TEXT.get(a.get("buttontext") or a.get("text"), "")
            if font in V.FONTS and txt:
                lh = int(V.FONTS[font]["common"]["lineHeight"])
                V.draw_text(cv, font, txt, ox + x, oy + y + (fh - lh) / 2, fw, "centre", check=a.get("name"))
        elif key.lower() == "instanttextboxtype" and a.get("font") in V.FONTS:
            V.draw_text(cv, a["font"], MENU_TEXT.get(a.get("text"), ""), ox + x, oy + y, int(a.get("maxwidth", 0)) or None,
                        a.get("format", "left"))
    out = Image.fromarray((np.clip(cv, 0, 1) * 255).astype(np.uint8))
    # social links (vanilla icons, not in the mod): an outline where the two rows draw (y -17 .. +49)
    soc = T["mainmenu_social_buttons"]
    sd = V.attrs(soc)
    assert sd.get("orientation", "").upper() == "UPPER_LEFT" and "origo" not in sd
    sx0, sy0 = (int(v) for v in V.xy(V.sub(soc, "position")))
    ImageDraw.Draw(out).rectangle((sx0 + 30, sy0 - 17, sx0 + 210, sy0 + 49), outline=(120, 110, 90))
    out.save(BUILD + "preview_menu.png")
    print("menu preview written")


if __name__ == "__main__":
    preview_menu()


# ================================================================ state panel and focus tree (v0.4)
def anchor(ori, x, y, px, py, pw, ph):
    o = (ori or "UPPER_LEFT").upper()
    ax = px + pw + x if o in ("UPPER_RIGHT", "LOWER_RIGHT") else px + pw / 2 + x if o == "CENTER" else px + x
    ay = py + ph + y if o in ("LOWER_LEFT", "LOWER_RIGHT") else py + ph / 2 + y if o == "CENTER" else py + y
    return int(ax), int(ay)


def sprite_img(spr, frame=0):
    if spr in defs and "img" in defs[spr]:
        dd = defs[spr]
        fw = dd["img"].width // dd["frames"]
        f = min(frame, dd["frames"] - 1)
        return dd["img"].crop((f * fw, 0, (f + 1) * fw, dd["img"].height))
    return None


def render2(cv, elems, px, py, pw, ph, hooks, ctx=None):
    """Generic renderer for the restyled vanilla windows. hooks: name -> fn(cv, body, ax, ay, ctx) -> bool (handled)."""
    for key, body in elems:
        kl = key.lower() if key else ""
        if kl not in ("containerwindowtype", "icontype", "buttontype", "instanttextboxtype", "gridboxtype",
                      "overlappingelementsboxtype"):
            continue
        d = V.attrs(body)
        name = d.get("name")
        if d.get("hide") == "yes":
            continue
        pos = V.sub(body, "position")
        x, y = (int(float(v)) for v in V.xy(pos)) if pos else (0, 0)
        ax, ay = anchor(d.get("orientation"), x, y, px, py, pw, ph)
        if name in hooks and hooks[name](cv, body, ax, ay, ctx):
            continue
        if kl == "containerwindowtype":
            sz = V.sub(body, "size")
            w, h = V.xy(sz) if sz else (0, 0)
            w = pw if "%" in str(w) else int(w)
            h = ph if "%" in str(h) else int(h)
            for bk, bg in body:
                if bk != "background":
                    continue
                spr = V.attrs(bg).get("quadtexturesprite") or V.attrs(bg).get("spritetype")
                bp = V.sub(bg, "position")
                bx, by = (int(v) for v in V.xy(bp)) if bp else (0, 0)
                if spr in defs and "img" in defs[spr]:
                    dd = defs[spr]
                    img = V.cornered(dd["img"], w, h, *dd["border"]) if dd["kind"] == "corneredTileSpriteType" else dd["img"]
                    V.paste(cv, img, ax + bx, ay + by)
            render2(cv, body, ax, ay, w, h, hooks, ctx)
        elif kl in ("icontype", "buttontype"):
            spr = d.get("quadtexturesprite") or d.get("spritetype")
            img = sprite_img(spr, int(d.get("frame", 1)) - 1)
            if img is None:
                continue
            sc = float(d.get("scale", 1))
            if sc != 1:
                img = img.resize((max(1, int(img.width * sc)), max(1, int(img.height * sc))), Image.LANCZOS)
            if d.get("centerposition") == "yes":
                ax, ay = ax - img.width // 2, ay - img.height // 2
            V.paste(cv, img, ax, ay)
        elif kl == "instanttextboxtype":
            font = d.get("font")
            txt = (ctx or {}).get(name) if ctx else None
            txt = txt if txt is not None else SAMPLE.get(name)
            if txt is None:
                txt = LOC_ALL.get(d.get("text"))
            if not txt or font not in V.FONTS:
                continue
            mw = int(d.get("maxwidth", 0)) or None
            mh = int(d.get("maxheight", 0)) or None
            V.draw_text(cv, font, txt, ax, ay, mw, d.get("format", "left"), max_h=mh,
                        valign=d.get("vertical_alignment") == "center", check=name)


SAMPLE = {}
LOC_ALL = {}
for _f in __import__("glob").glob(M + "localisation/english/*.yml"):
    LOC_ALL.update(re.findall(r'^\s*(\w+):0 "(.*)"$', open(_f, encoding="utf-8-sig").read(), re.M))
FLAG = Image.open(ART + "flag_ROU.png").convert("RGBA")


def standin_icon(w, h, glyph=""):
    im = standin(w, h, glyph)
    return im


def preview_stateview():
    full = Image.open(ART + "map_rouental.jpg").convert("RGB").resize((1920, 1080), Image.LANCZOS)
    cv = np.array(full, np.float32) / 255
    g = V.load(M + "interface/countrystateview.gui")
    T = templates(g)
    panel = T["countrystateview"]
    sp = V.xy(V.sub(panel, "show_position"))
    w, h = (int(v) for v in V.xy(V.sub(panel, "size")))
    ox, oy = int(sp[0]), 1080 + int(sp[1])          # lower_left
    SAMPLE.clear()
    SAMPLE.update({"state_name": "Rêverie", "owner": "Owner", "manpower": "21,900", "victory_points": "10",
                   "shared_slot_count": "Shared building slots  5/6", "province": "Rêverie",
                   "state_modifiers": "State modifiers"})

    def entries(tpl, items, sw):
        def fn(cv_, body, ax, ay, ctx):
            for i, (glyph, lvl) in enumerate(items):
                render2(cv_, [("containerWindowType", T[tpl])], ax + i * sw, ay, 0, 0, hooks, dict(level=lvl, glyph=glyph))
            return True
        return fn

    def building_picture(cv_, body, ax, ay, ctx):
        if ctx and "glyph" in ctx:
            V.paste(cv_, standin(36, 36, ctx["glyph"]), ax, ay)
        return True

    def owners(cv_, body, ax, ay, ctx):
        V.paste(cv_, FLAG.resize((41, 26), Image.LANCZOS), ax, ay)
        return True

    def terrain(cv_, body, ax, ay, ctx):
        V.paste(cv_, standin(128, 64, "terrain"), ax, ay)
        return True

    def resources(cv_, body, ax, ay, ctx):
        return True

    hooks = {"state_building_entries": entries("state_building_entry", [("I", "3"), ("A", "2"), ("AA", "1")], 60),
             "state_shared_slot_building_entries": entries("state_shared_slot_building_entry",
                                                           [("F", None), ("F", None), ("F", None), ("M", None), ("M", None)], 61),
             "province_building_entries": entries("province_building_entry", [("Fo", "1")], 61),
             "building_picture": building_picture, "state_owners": owners, "terrain_picture": terrain,
             "state_resources_entries": resources, "resistance_container": lambda *a: True,
             "population_icon": lambda cv_, b, ax, ay, c: (V.paste(cv_, standin(22, 22, "P"), ax, ay), True)[1],
             "controller_flag": lambda *a: True, "controller_flag_border": lambda *a: True,
             "energy_consumption_bg": lambda *a: True, "energy_icon": lambda *a: True,
             "scorched_earth_state_button": lambda *a: True, "damage_bar": lambda *a: True,
             "building_status_overlay": lambda *a: True, "remove": lambda *a: True,
             "building_modifiers_icon": lambda *a: True, "dynamic_modifiers_grid": lambda *a: True,
             "strategic_locations_grid": lambda *a: True, "province_required_rule": lambda *a: True}
    SAMPLE["level"] = None

    def level_text(cv_, body, ax, ay, ctx):
        if ctx and ctx.get("level"):
            d = V.attrs(body)
            V.draw_text(cv_, d["font"], ctx["level"], ax, ay, int(d.get("maxwidth", 60)), d.get("format", "center"))
        return True
    hooks["level"] = level_text
    hooks["level_bg"] = lambda cv_, b, ax, ay, c: not (c and c.get("level"))
    render2(cv, [(k, b) for k, b in panel if k and k.lower() != "position"], ox, oy, w, h, hooks)
    out = Image.fromarray((np.clip(cv, 0, 1) * 255).astype(np.uint8))
    out.crop((0, 380, 760, 1080)).save(BUILD + "preview_stateview.png")
    print("state panel preview written")


if __name__ == "__main__":
    preview_stateview()   # the focus tree's preview is preview_focus.py (v0.6)
