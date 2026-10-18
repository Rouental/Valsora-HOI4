"""Mockups of the side panels with their own pictures redrawn (2026-10-18, the author: "Do mockups of the panels and
your replacements, but dont replace them just yet"). NOT in the mod: everything is written to build/ (git-ignored:
the "now" halves show the game's art, and the drafts are made from the game's pictures).

    python proposals_panel_mockups.py            -> build/panel_proposals/   the drafts, at the game's paths
                                                    build/panel_mockups/     each panel now | with the drafts
                                                                             pictures.png: each picture, game | draft

The drafts are of two kinds:
- the eight hand-drawn proposals of v0.7 (proposals_panels.py: art/proposals/panel_pictures/), at their game paths;
- the rest of each panel's own pictures (PICTURES: the headers, list rows, cards and plates still the game's, 45),
  translated from the game's own picture so its layout stays exactly where the game's text, icons and lists expect it:
  the grain smoothed away (a median filter, which keeps the edges), the dark of it lacquer (#070B0E to #22303A by its
  brightness), each colour the Deco UI's counterpart (green jade, red lacquer red, blue steel, purple indigo, parchment
  ivory, gold frames gilt), its edges gilt hairlines, the faint pinstripes of the panels' lacquer over the dark; and
  the two photographs (the agency's spies) a hand-drawn plate instead.
A draft that is liked would then be drawn properly (an art module, as diplomacy_art.py) before going in.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi

from paths import ART, BUILD, FONTS_SRC, VANILLA

OUT = BUILD + "panel_proposals/"
MOCK = BUILD + "panel_mockups/"
GI = "gfx/interface/"

# the panels' own pictures, translated (the game's path under gfx/interface/)
PICTURES = """armyoverview_entry_bg.dds armyoverview_naval_entry_bg.dds armyoverview_air_entry_bg.dds
overview_filter_entry.dds overview_filter_entry_highlight.dds construction_screen_top.dds decisionview/decision_item_bg.dds
decisionview/event_header_bg.dds military_deployment_conveyor_bg.dds subview_header_bg_375x101.dds operatives/operatives_bg.dds
operatives/branch_upgrade_entry.dds operatives/branch_upgrade_entry_select.dds operations/operations_entry_bg.dds
crypto/country_entry_bg.dds crypto/country_entry_selected_bg.dds logistics_win_bottom.dds linechart_frame.dds
tradeview/trade_filter_bg.dds occupation/occupation_header_bg.dds occupation/occupation_country_entry_bg_top.dds
occupation/occupation_country_entry_bg_top_locked.dds occupation/occupation_state_entry_bg.dds
occupation/occupation_garrison_select_entry_bg.dds officer_corp/officer_corp_bg_banner_army.dds
officer_corp/officer_corp_bg_banner_navy.dds officer_corp/officer_corp_bg_banner_air.dds officer_corp/spirit_entry_bg_strip.dds
officer_corp/advisor_theorist_entry.dds officer_corp/officer_corp_army_hq_bg.dds officer_corp/army_hq_template_bg.dds
production_item.dds production_line_selected.dds naval_production_line_selected.dds naval_production_item_slots_strip.dds
tradeview/country_trade_entry_bg_wide.dds factions/ui/faction_identity_background_generic.dds
factions/ui/faction_supreme_commander_background.dds factions/ui/faction_influence_chart_background.dds
factions/ui/faction_intelligence_background.dds factions/ui/faction_doctrine_sharing_bg.dds factions/ui/faction_goal_slot.dds
factions/ui/select_faction_goal_button.dds factions/ui/faction_identity_background_pop_up_generic.dds
theater/theater_group_bg.dds""".split()
PHOTOS = ["operatives/intelligence_agency_header4.dds", "factions/ui/faction_spymaster_background.dds"]
# v0.7's hand-drawn proposals: (file in art/proposals/panel_pictures/, the game's path under gfx/interface/)
HAND = [("research_top_win.png", "research_top_win.dds"), ("production_win_top.png", "production_win_top.dds"),
        ("market_ui.png", "international_market/market_ui.dds"), ("overview_top_strip.png", "overview_top_strip.dds"),
        ("create_agency_bg.png", "operatives/create agency_bg.dds")] + [
        (f"spirit_banner_decoration_{k}.png", f"officer_corp/spirit_banner_decoration_{k}.dds") for k in ("army", "navy", "air")]

LAC_DARK, LAC_LIGHT = np.array([7, 11, 14.]), np.array([34, 48, 58.])
GILT, GILT_LIT = np.array([201, 165, 90.]), np.array([227, 199, 126.])
# hue (degrees) -> the Deco UI's colour for a coloured part of a picture
HUES = [((70, 170), np.array([46, 110, 96.])),       # green: jade
        ((170, 250), np.array([44, 78, 102.])),      # blue: steel
        ((250, 320), np.array([58, 46, 90.])),       # purple: indigo
        ((320, 360), np.array([122, 42, 38.])), ((0, 18), np.array([122, 42, 38.]))]   # red: lacquer red
IVORY = np.array([232, 223, 200.])


WELL, LINE = np.array([9, 13, 16.]), np.array([201, 165, 90.])
PLATE = np.array([17, 25, 30.])


def _rects(mask, min_area, fill):
    """the bounding boxes of mask's parts that are near enough rectangles (their area at least `fill` of the box)"""
    lab, n = ndi.label(mask)
    out = []
    for i, sl in enumerate(ndi.find_objects(lab), 1):
        if sl is None:
            continue
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        area = (lab[sl] == i).sum()
        if area >= min_area and area >= fill * h * w and min(h, w) >= 6:
            out.append((sl[1].start, sl[0].start, sl[1].stop, sl[0].stop))
    return out


def _box(out, x0, y0, x1, y1, fill, rim, c=3):
    """a chamfered box: fill, a 1 px rim"""
    H, W = out.shape[:2]
    yy, xx = np.mgrid[y0:y1, x0:x1]
    inside = ((xx - x0) + (yy - y0) >= c) & ((x1 - 1 - xx) + (yy - y0) >= c) & \
             ((xx - x0) + (y1 - 1 - yy) >= c) & ((x1 - 1 - xx) + (y1 - 1 - yy) >= c)
    border = inside & ~(((xx - x0) + (yy - y0) >= c + 1) & ((x1 - 1 - xx) + (yy - y0) >= c + 1) &
                        ((xx - x0) + (y1 - 1 - yy) >= c + 1) & ((x1 - 1 - xx) + (y1 - 1 - yy) >= c + 1) &
                        (xx > x0) & (xx < x1 - 1) & (yy > y0) & (yy < y1 - 1))
    reg = out[y0:y1, x0:x1]
    reg[inside] = fill
    reg[border] = reg[border] * .35 + rim * .65


def translate(im):
    """the game's picture in the Deco palette, its layout kept, rebuilt from rectangles: a flat lacquer plate with a gilt
    rim where the game's picture is; its recessed wells (darker than round about them, near enough rectangular) and its
    coloured and paper parts (classified on a heavily smoothed copy) as clean chamfered boxes in their Deco colours with
    gilt rims; its own thin bright lines (highlight frames) gilt"""
    a = np.asarray(im.convert("RGBA")).astype(float)
    rgb, alpha = a[..., :3] / 255, a[..., 3]
    solid = alpha > 128
    S = np.stack([ndi.gaussian_filter(ndi.median_filter(rgb[..., c], size=9), 2) for c in range(3)], -1)
    mx, mn = S.max(-1), S.min(-1)
    lum = S @ np.array([.299, .587, .114])
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    r, g, b = S[..., 0], S[..., 1], S[..., 2]
    hue = (np.degrees(np.arctan2(np.sqrt(3) * (g - b), 2 * r - g - b)) + 360) % 360
    out = np.zeros(rgb.shape) + PLATE
    stripe = (np.arange(out.shape[1]) % 8 == 0)[None, :]
    out[np.broadcast_to(stripe, solid.shape)] += 7
    # coloured parts and paper
    paper = (lum > .42) & (sat > .10) & (sat < .62) & (hue >= 18) & (hue < 62) & solid
    coloured = (sat > .30) & (mx > .20) & ~paper & solid
    taken = np.zeros(solid.shape, bool)
    for mask, col in [(paper, IVORY)] + [(coloured & (hue >= h0) & (hue < h1), c) for (h0, h1), c in HUES]:
        mask = ndi.binary_opening(ndi.binary_closing(mask, iterations=3), iterations=2)
        for x0, y0, x1, y1 in _rects(mask, 150, .55):
            _box(out, x0, y0, x1, y1, col, LINE)
            taken[y0:y1, x0:x1] = True
    # recessed wells: darker than round about them
    # the picture's frame tone: its brightness in a band 3-8 px inside its outline (per frame of a strip alike)
    band = solid & ~ndi.binary_erosion(solid, iterations=8) & ndi.binary_erosion(solid, iterations=3)
    tone = max(np.median(lum[band]) if band.any() else 0, np.percentile(lum[solid], 70) if solid.any() else 0)
    well = (lum < min(tone - .03, tone * .82)) & solid & ~taken
    well = ndi.binary_opening(ndi.binary_closing(well, iterations=2), iterations=2)
    for x0, y0, x1, y1 in _rects(well, 120, .7):
        _box(out, x0, y0, x1, y1, WELL, LINE)
    # the picture's outline: a gilt rim
    rim = solid & ~ndi.binary_erosion(solid, iterations=1)
    out[rim] = LINE
    # thin bright lines of the game's picture (rims, highlight frames): gilt, the brightest lit
    L0 = rgb @ np.array([.299, .587, .114])
    thin = ((L0 - ndi.grey_opening(L0, size=5)) > .16) & (L0 > .45) & solid
    out[thin] = np.where((L0[thin] > .62)[..., None], GILT_LIT, GILT)
    return Image.fromarray(np.dstack([np.clip(out, 0, 255), alpha]).astype(np.uint8), "RGBA")


def photo_plate(w, h):
    """a lacquer plate with a gilt rim and a fan of gilt lines, for a picture that was a photograph"""
    im = Image.new("RGBA", (w, h), (17, 25, 30, 255))
    d = ImageDraw.Draw(im)
    for x in range(0, w, 8):
        d.line((x, 0, x, h), fill=(26, 35, 41, 255))
    cx, cy = w * .72, h + 6
    for i in range(13):
        ang = np.radians(-90 - 60 + 120 * i / 12)
        d.line((cx, cy, cx + h * 1.4 * np.cos(ang), cy + h * 1.4 * np.sin(ang)), fill=(201, 165, 90, 46), width=1)
    d.rectangle((0, 0, w - 1, h - 1), outline=(201, 165, 90, 255))
    d.rectangle((3, 3, w - 4, h - 4), outline=(201, 165, 90, 110))
    return im


def make_drafts():
    made = []
    for rel in PICTURES:
        src = VANILLA + GI + rel
        if not os.path.isfile(src):
            print("not in the game's files:", rel)
            continue
        dst = OUT + GI + rel
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        translate(Image.open(src)).save(dst, "PNG")        # a PNG under the .dds name: only the previews read it
        made.append(rel)
    for rel in PHOTOS:
        w, h = Image.open(VANILLA + GI + rel).size
        dst = OUT + GI + rel
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        photo_plate(w, h).save(dst, "PNG")
        made.append(rel)
    for png, rel in HAND:
        src = ART + "proposals/panel_pictures/" + png
        if os.path.isfile(src):
            dst = OUT + GI + rel
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            Image.open(src).convert("RGBA").save(dst, "PNG")
            made.append(rel)
    return made


def picture_sheet(made):
    """each picture: the game's, then the draft"""
    font = ImageFont.truetype(FONTS_SRC + "josefinsans/JosefinSans[wght].ttf", 15)
    rows, y = [], 10
    for rel in made:
        g = Image.open(VANILLA + GI + rel).convert("RGBA")
        p = Image.open(OUT + GI + rel).convert("RGBA")
        s = min(1.0, 900 / g.width)
        g = g.resize((max(1, round(g.width * s)), max(1, round(g.height * s))), Image.LANCZOS)
        p = p.resize(g.size, Image.LANCZOS)
        rows.append((rel, g, p, y))
        y += 24 + g.height * 2 + 14
    sheet = Image.new("RGBA", (940, y), (54, 58, 64, 255))
    d = ImageDraw.Draw(sheet)
    for rel, g, p, yy in rows:
        d.text((10, yy), f"{rel}   (top: the game's; under it: the draft)", fill=(240, 236, 220), font=font)
        sheet.alpha_composite(g, (10, yy + 22))
        sheet.alpha_composite(p, (10, yy + 26 + g.height))
    os.makedirs(MOCK, exist_ok=True)
    sheet.convert("RGB").save(MOCK + "pictures.png")


def panel_mockups(keys):
    """each side panel as the mod draws it now, and with the drafts (preview_panels.py reads PROPOSALS first)"""
    import subprocess
    env = dict(os.environ)
    here = os.path.dirname(os.path.abspath(__file__))
    for tag, extra in (("now", {}), ("draft", {"VALSORA_DECO_PROPOSALS": OUT})):
        e = dict(env, **extra, VALSORA_PREVIEW_SUFFIX="_" + tag)
        subprocess.run([sys.executable, os.path.join(here, "preview_panels.py"), *keys], env=e, check=True,
                       stdout=subprocess.DEVNULL)
    os.makedirs(MOCK, exist_ok=True)
    font = ImageFont.truetype(FONTS_SRC + "josefinsans/JosefinSans[wght].ttf", 20)
    for k in keys:
        a = Image.open(BUILD + f"preview_panel_{k}_now.png")
        b = Image.open(BUILD + f"preview_panel_{k}_draft.png")
        w = min(a.width, 760)
        a, b = a.crop((0, 0, w, a.height)), b.crop((0, 0, w, b.height))
        sheet = Image.new("RGB", (2 * w + 20, a.height + 34), (40, 44, 50))
        d = ImageDraw.Draw(sheet)
        d.text((10, 6), f"{k}: now", fill=(240, 236, 220), font=font)
        d.text((w + 30, 6), f"{k}: with the drafts", fill=(240, 236, 220), font=font)
        sheet.paste(a, (0, 34))
        sheet.paste(b, (w + 20, 34))
        sheet.save(MOCK + f"{k}.png")
        print("mockup:", k)


if __name__ == "__main__":
    import layout_panels as LPN
    made = make_drafts()
    print(len(made), "drafts in", OUT)
    picture_sheet(made)
    panel_mockups(sys.argv[1:] or [k for k in LPN.PANELS])
