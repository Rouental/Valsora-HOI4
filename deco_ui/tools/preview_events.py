"""A preview of the events (v0.7): a country event, a news event and a leader event over the map, drawn as the game stacks them
(eventwindow.gui: the top, the middle stretched to the text, the bottom with the picture and the options; the news
on its broadsheet), with the mod's textures and fonts. The pictures are stand-ins (a Valsora superevent photo, the
world map art), since the game's event pictures are not in this repository's reference copy.

    python preview_events.py          -> build/preview_events.png
"""
import os
import re

import numpy as np
from PIL import Image

import guipatch as GP
import validate_preview as V
from paths import ART, BUILD, MOD

EV = MOD + "gfx/interface/"
GUI = open(MOD + "interface/eventwindow.gui", encoding="utf-8-sig").read()
NAME_X = GP.get_pos(GUI, "event_option_entry>Name")[0]
NAME_W = int(re.search(r"maxWidth\s*=\s*(\d+)", GUI[GUI.index('name = "Name"', GUI.index('name = "event_option_entry"')):]).group(1))
TITLE, TEXT, OPTION = "valsora_deco_title_18", "valsora_deco_body_15", "valsora_deco_body_15"
PHOTO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "source", "superevents", "rou_civil_war.jpg")
SAMPLE = dict(
    title="Elections in Rouental",
    text=("The Principality's assemblies have been called to elect a new chancellor. Across the Vale of Reibonne the "
          "parties have filled the squares of Rêverie and Carcarelle, and the old families watch the count with "
          "unease. Whatever the result, the Crown will have to work with the new government."),
    options=["The people have spoken.", "Postpone the count."],
    news_title="The Association Stands Together",
    news_text=("Envoys of the eight Reibonnaise states met in Rêverie today and renewed the Association's charter for "
               "another decade. Observers across Nonscio call it the strongest bond in the Vale since the old wars."),
    news_options=["A union of the Vale."],
    leader_title="The Prince Speaks",
    leader_text=("Roland II Cahun has addressed the assembled vassals of the Crown from the steps of the palace in "
                 "Rêverie. The Prince promised that the levies would be called only in the realm's defence, and that "
                 "the old privileges of the fiefs would stand."),
    leader_options=["Long live the Prince.", "The vassals will remember this."])
LEADER = MOD + "../../build/valsora_test/gfx/leaders/VAL/ROU_roland_cahun.dds"


def img(rel):
    return Image.open(rel).convert("RGBA")


def cover(path, w, h):
    """the picture cropped to fill w x h"""
    im = Image.open(path).convert("RGB")
    s = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h)).convert("RGBA")


def tile(texture, height, border=16):
    """a cornered tile stretched to `height` (the game's corneredTileSpriteType: border rows kept, the middle repeated)"""
    t = img(texture)
    out = Image.new("RGBA", (t.width, height), (0, 0, 0, 0))
    out.alpha_composite(t.crop((0, 0, t.width, border)), (0, 0))
    mid = t.crop((0, border, t.width, t.height - border))
    y = border
    while y < height - border:
        out.alpha_composite(mid.crop((0, 0, t.width, min(mid.height, height - border - y))), (0, y))
        y += mid.height
    out.alpha_composite(t.crop((0, t.height - border, t.width, t.height)), (0, height - border))
    return out


def text_height(font, text, w):
    f = V.FONTS[font]
    lh = int(f["common"]["lineHeight"])
    lines, cur = 1, ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if cur and V.text_width(f, V._runs(trial, None)) > w:
            lines, cur = lines + 1, word
        else:
            cur = trial
    return lines * lh


def main():
    W, H = 1500, 1200
    bg = Image.open(ART + "map_rouental.jpg").convert("RGB").resize((2134, 1200), Image.LANCZOS).crop((300, 0, 300 + W, H))
    cv = bg.convert("RGBA")
    texts = []
    # a country event: 581 wide; the middle is as tall as the text (at least the game's 100)
    ex, ey = 70, 90
    mid_h = max(100, text_height(TEXT, SAMPLE["text"], 512) + 16)
    cv.alpha_composite(img(EV + "event_report_top_win.dds"), (ex, ey))
    cv.alpha_composite(tile(EV + "event_report_tileable_midsection.dds", mid_h), (ex, ey + 121))
    by = ey + 121 + mid_h
    cv.alpha_composite(img(EV + "event_report_bottom_win.dds"), (ex, by))
    cv.alpha_composite(cover(PHOTO, 210, 176), (ex + 5, by + 5))
    cv.alpha_composite(img(EV + "event_pic_clip.dds"), (ex - 3, by + 35))
    cv.alpha_composite(img(EV + "event_button_minimize.dds"), (ex + 10, ey + 45))
    texts += [(TITLE, SAMPLE["title"], ex + 14, ey + 70, 551, 32, "centre", True),
              (TEXT, SAMPLE["text"], ex + 31, ey + 121, 512, mid_h, "left", False)]
    gx, gy = GP.get_pos(GUI, "EventWindow/options_grid")
    for i, o in enumerate(SAMPLE["options"]):
        ox, oy = ex + gx, by + gy + i * 47
        cv.alpha_composite(img(EV + "event_option_entry.dds"), (ox, oy))
        texts.append((OPTION, o, ox + NAME_X, oy, NAME_W, 40, "centre", True))
    # a news event: the broadsheet, 528 x 595
    nx, ny = 800, 120
    cv.alpha_composite(img(EV + "event_news_bg.dds"), (nx, ny))
    px, py = GP.get_pos(GUI, "EventWindow_News>top_Window>event_picture")
    cv.alpha_composite(cover(ART + "map_rouental.jpg", 399, 155), (nx + px, ny + py))
    cv.alpha_composite(img(EV + "event_news_pic_overlay.dds"), (nx + px, ny + py))
    hx, hy = GP.get_pos(GUI, "EventWindow_News>top_Window>Title")
    sx, sy = GP.get_pos(GUI, "EventWindow_News>midsection>Description")
    cv.alpha_composite(img(EV + "event_button_minimize.dds"), (nx + 10, ny + 10))
    texts += [(TITLE, SAMPLE["news_title"], nx + hx, ny + hy, 490, 32, "centre", True),
              (TEXT, SAMPLE["news_text"], nx + sx, ny + 121 + sy, 460, 190, "left", False)]
    gx, _ = GP.get_pos(GUI, "EventWindow_News/options_grid")
    for i, o in enumerate(SAMPLE["news_options"]):
        ox, oy = nx + gx, ny + 520 + i * 47       # the game stacks the options under the story
        cv.alpha_composite(img(EV + "event_option_entry.dds"), (ox, oy))
        texts.append((OPTION, o, ox + NAME_X, oy, NAME_W, 40, "centre", True))
    # a leader event: the top, the middle (235 px: the portrait at 0.85 in its arched frame, the text beside it), the
    # options on the middle's tile, the foot (bottom_window_end)
    lx, ly = 70, 600
    cv.alpha_composite(img(EV + "event_report_top_win.dds"), (lx, ly))
    cv.alpha_composite(tile(EV + "event_report_tileable_midsection.dds", 235), (lx, ly + 121))
    por = Image.open(LEADER).convert("RGBA")
    por = por.resize((round(por.width * .85), round(por.height * .85)), Image.LANCZOS)
    cv.alpha_composite(por, (lx + 10 + 33, ly + 121 + 4))
    fr = img(EV + "event_leader_frame.dds")
    cv.alpha_composite(fr.resize((round(fr.width * .85), round(fr.height * .85)), Image.LANCZOS), (lx + 10 + 25, ly + 121 - 5))
    cv.alpha_composite(img(EV + "event_button_minimize.dds"), (lx + 10, ly + 45))
    texts += [(TITLE, SAMPLE["leader_title"], lx + 14, ly + 70, 551, 32, "centre", True),
              (TEXT, SAMPLE["leader_text"], lx + 198, ly + 121, 350, 220, "left", False)]
    gx, gy = GP.get_pos(GUI, "EventWindow_leader/options_grid")
    bh = gy + len(SAMPLE["leader_options"]) * 47 + 10
    cv.alpha_composite(tile(EV + "event_report_tileable_midsection.dds", bh), (lx, ly + 356))
    for i, o in enumerate(SAMPLE["leader_options"]):
        ox, oy = lx + gx, ly + 356 + gy + i * 47
        cv.alpha_composite(img(EV + "event_option_entry.dds"), (ox, oy))
        texts.append((OPTION, o, ox + NAME_X, oy, NAME_W, 40, "centre", True))
    cv.alpha_composite(img(EV + "event_report_bottom_win_2.dds"), (lx, ly + 356 + bh))
    arr = np.asarray(cv.convert("RGB"), dtype=np.float32) / 255
    for font, s, x, y, w, h, fmt, valign in texts:
        V.draw_text(arr, font, s, x, y, w, fmt, max_h=h, valign=valign, check="event " + s[:20])
    Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8)).save(BUILD + "preview_events.png")
    print("events preview written", "problems:", V.problems or "none")


if __name__ == "__main__":
    main()
