"""build/preview_popups.png (+ _vanilla): the windows popup_art.py draws, as the game lays them out (2026-10-17, v0.10),
with the Deco UI's pictures and fonts and with the game's: the settings (its Audio and Video tabs), a tutorial window,
the trade offer, the variant designer and the market's stockpile window (the same picture), the air view over a region,
the naval region view, the intelligence agency's upgrades window, its name and logo window, the army insignia picker
and the faction's colour picker (the last three share one picture), and two popups that lay the settings' tab bar
(diplo_popup_bottom) under their buttons.

The windows are read from the game's .gui files (the Deco UI's copy where it ships one) with preview_panels.py's
renderer; a background block's own position (the air view's picture at -4, -5) is honoured by drawing it as the first
child. What the renderer doesn't draw is drawn here as the game places it, approximately: the sliders (their track,
thumb and arrows), the flag in the trade offer's frame, the variant designer's equipment view and its statistics.

    python preview_popups.py
"""
import os

import numpy as np
from PIL import Image, ImageDraw

import preview_panels as PP
import validate_preview as V
from paths import ART, BUILD, VANILLA

W, H = 2330, 2100
DROP = ("position", "orientation", "origo", "show_position", "hide_position")


def gui_path(rel, vanilla):
    mod = PP.M + "interface/" + rel
    return mod if not vanilla and os.path.isfile(mod) else VANILLA + "interface/" + rel


def lift(body):
    """a background block with a position of its own becomes the container's first child, at that position"""
    out, first = [], []
    for k, v in body:
        if isinstance(v, list):
            v = lift(v)
            if k and k.lower() == "background" and V.sub(v, "position"):
                a = V.attrs(v)
                spr = a.get("quadtexturesprite") or a.get("spritetype")
                first.append(("iconType", [("name", "lifted_" + a.get("name", "bg")), ("spriteType", spr),
                                           ("position", V.sub(v, "position"))]))
                continue
        out.append((k, v))
    if first:
        i = next((n for n, (k, _) in enumerate(out) if k and k.lower() in PP.ELEMENTS), len(out))
        out[i:i] = first
    return out


def placed(win, x, y, size=None):
    body = [(k, v) for k, v in win if not (k and k.lower() in DROP) and not (size and k and k.lower() == "size")]
    body.append(("position", [("x", str(x)), ("y", str(y))]))
    if size:
        body.append(("size", [("width", str(size[0])), ("height", str(size[1]))]))
    return lift(body)


class Canvas:
    def __init__(self, vanilla):
        self.vanilla = vanilla
        bg = Image.open(ART + "map_rouental.jpg").convert("RGB")
        bg = bg.resize((int(bg.width * H / bg.height), H), Image.LANCZOS)
        full = Image.new("RGB", (W, H))
        for x in range(0, W, bg.width):
            full.paste(bg, (x, 0))
        self.cv = np.array(full, np.float32) / 255

    def window(self, rel, name, x, y, size=None, hide=(), samples=None, frames=None, parent=None):
        path = gui_path(rel, self.vanilla)
        win = PP.find_window(V.load(path), name)
        assert win is not None, (path, name)
        p = PP.Panel(hide=hide, samples=samples, vanilla_only=self.vanilla, vars_=PP.gui_vars(path), frames=frames)
        px, py, pw, ph = parent or (0, 0, W, H)
        p.draw(self.cv, [("containerWindowType", placed(win, x - px, y - py, size))], px, py, pw, ph)
        return p

    def sprite(self, name, x, y, frame=0, w=None, h=None):
        d, img = PP.sprite(name, self.vanilla)
        if img is None:
            return
        if d["kind"] == "corneredtilespritetype":
            bx, by = d.get("border", (0, 0))
            V.paste(self.cv, V.cornered(img, w, h, min(bx, img.width // 2), min(by, img.height // 2)), x, y)
        else:
            V.paste(self.cv, PP.frame_of(img, d, frame), x, y)

    def image(self, img, x, y):
        V.paste(self.cv, img, x, y)

    def text(self, font, s, x, y, w, fmt="left", dark=False):
        if not self.vanilla:
            V.draw_text(self.cv, font, s, x, y, w, fmt)
            return
        im = Image.new("RGBA", (w, 24), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        f = PP.ttf(PP.vanilla_font_px(font))
        tw = d.textlength(s, font=f)
        tx = {"right": w - tw, "center": (w - tw) / 2}.get(fmt, 0)
        d.text((tx, 0), s, font=f, fill=(52, 40, 24, 255) if dark else (226, 220, 204, 255))
        V.paste(self.cv, im, x, y)

    def slider(self, x, y, w, value=.4):
        """a settings slider (scrollbarType of the yearslider_ sprites), as the game appears to place its parts"""
        self.sprite("yearslider_background", x + 23, y, w=w - 46, h=16)
        self.sprite("yearslider_leftbutton", x, y - 2)
        self.sprite("yearslider_rightbutton", x + w - 23, y - 2)
        self.sprite("yearslider_slider2", x + 23 + int((w - 62) * value), y)

    def save(self, name):
        Image.fromarray((np.clip(self.cv, 0, 1) * 255).astype(np.uint8)).save(BUILD + name)
        print("written", BUILD + name)


TABS = ("menu_settings_AUDIO", "menu_settings_CONTROLS", "menu_settings_VIDEO", "menu_settings_GAME")
WEATHER = ("weather_light_rain", "weather_heavy_rain", "weather_light_snow", "weather_heavy_snow", "weather_none_night",
           "weather_light_rain_night", "weather_heavy_rain_night", "weather_light_snow_night", "weather_heavy_snow_night")
STATS = [("Soft attack", "14.2"), ("Hard attack", "9.6"), ("Breakthrough", "31.0"), ("Defence", "18.4"),
         ("Armour", "62.0"), ("Piercing", "70.0"), ("Speed", "8.0 km/h"), ("Reliability", "84%"),
         ("Fuel usage", "2.4"), ("Production cost", "11.8")]


def settings(c, x, y, tab, tab_index):
    hide = set(TABS) - {tab}
    frames = {f"settings_tab_{i}": (0 if i == tab_index else 1) for i in range(1, 5)}
    c.window("settings.gui", "menu_settings_ingame", x, y, hide=hide, frames=frames)
    if tab == "menu_settings_AUDIO":
        for k, v in enumerate((.8, .55, .35, .6, .7)):
            c.slider(x + 270, y + 151 + 40 * k, 172, v)


def variant(c, x, y, rel, name, samples):
    c.window(rel, name, x, y, samples=samples)
    if name == "equipment_upgrade_designer_window":
        c.window("equipmentupgradedesignerwindow.gui", "land_equipment_designer_view", x, y + 50,
                 hide={"tank_aa_upgrade", "tank_art_upgrade", "tank_at_upgrade", "mech_cost_upgrade", "ac_engine_upgrade"},
                 parent=(x, y + 50, 545, 200))
    for i, (label, value) in enumerate(STATS):
        sx, sy = x + 20 + 258 * (i % 2), y + 244 + 21 * (i // 2)
        c.text("hoi4_typewriter16_inverted", label, sx, sy + 6, 130, dark=True)
        c.text("hoi4_typewriter16_inverted", value, sx + 126, sy + 6, 120, "right", dark=True)


def trade(c, x, y):
    c.window("countrytradeview.gui", "tradeoffer_window", x, y,
             hide={"player_flag"},
             samples={"country": "Lustiana", "trade": "Buying 24 Oil for 3 civilian factories",
                      "convoys_description": "Convoys: 6 needed, 41 free", "factories_description": "3 civilian factories",
                      "min_amount": "0", "max_amount": "48"})
    c.image(Image.open(ART + "flag_ROU.png").convert("RGBA").resize((82, 52), Image.NEAREST), x + 429, y + 13)
    c.sprite("GFX_large_flag_frame", x + 425, y + 11)
    # the amount slider (extendedScrollbarType at 116, 320, 300 wide): its bar picture 52 px left of it, 13 up
    c.sprite("GFX_slider_bg", x + 64, y + 307)
    c.sprite("GFX_scroll_track_horisontal", x + 136, y + 324, w=260, h=12)
    c.sprite("GFX_scroll_left", x + 119, y + 321)
    c.sprite("GFX_scroll_right", x + 397, y + 321)
    c.sprite("GFX_scroll_drager", x + 220, y + 318)


def draw(vanilla):
    c = Canvas(vanilla)
    settings(c, 30, 30, "menu_settings_AUDIO", 3)
    settings(c, 540, 30, "menu_settings_VIDEO", 2)
    c.window("tutorialscreen.gui", "tutorial_screen_1", 1050, 30)
    trade(c, 1690, 30)
    variant(c, 30, 680, "equipmentupgradedesignerwindow.gui", "equipment_upgrade_designer_window",
            {"variant_name": "Char Royal Mk II"})
    variant(c, 605, 680, "international_market/edit_market_stockpile_window.gui", "edit_market_stockpile_window",
            {"variant_name": "Char Royal Mk II", "cic_cost": "0.42"})
    c.window("strategicairview.gui", "strategicairview", 1184, 685, hide=set(WEATHER) | {"details_wnd"},
             samples={"region_name": "The Vale of Reibonne"})
    c.window("naval_strategic_region_view.gui", "navalregionview", 1772, 680,
             samples={"region_name": "North Demetric 4"})
    c.window("countryintelligenceagencyview.gui", "intelligence_agency_upgrades_window", 30, 1180, size=(1092, 520),
             samples={"upgrade_duration_title": "Upgrade in progress: 14 days"})
    c.window("countryintelligenceagencyview.gui", "name_logo_agency_selection_window", 1150, 1160)
    c.window("insigniaselection.gui", "insignia_selection_window", 1560, 1160)
    c.window("factions/faction_customization.gui", "faction_color_picker_window", 1940, 1160)
    # two of the popups that lay diplo_popup_bottom (the settings' tab bar) under their buttons
    c.window("popupwindow.gui", "confirmation_popup_window", 30, 1740,
             samples={"title": "Release Lustiana?", "desc": "Lustiana will be released as an independent nation."})
    c.window("frontendmultiplayerview.gui", "multiplayer_connect_window", 580, 1740)
    c.save("preview_popups_vanilla.png" if vanilla else "preview_popups.png")


if __name__ == "__main__":
    draw(False)
    draw(True)
