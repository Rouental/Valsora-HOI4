"""A preview of the events (v0.7): a country event and a news event over the map, drawn as the game stacks them
(eventwindow.gui: the top, the middle stretched to the text, the bottom with the picture and the options; the news
on its broadsheet), with the mod's textures and fonts. The pictures are stand-ins (a Valsora superevent photo, the
world map art), since the game's event pictures are not in this repository's reference copy.

    python preview_events.py          -> build/preview_events.png
"""
import os

import numpy as np
from PIL import Image

import validate_preview as V
from paths import ART, BUILD, MOD

EV = MOD + "gfx/interface/"
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
    news_options=["A union of the Vale."])


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
    W, H = 1500, 900
    bg = Image.open(ART + "map_rouental.jpg").convert("RGB").resize((1920, 1080), Image.LANCZOS).crop((200, 90, 200 + W, 90 + H))
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
    for i, o in enumerate(SAMPLE["options"]):
        ox, oy = ex + 215, by - 1 + i * 47
        cv.alpha_composite(img(EV + "event_option_entry.dds"), (ox, oy))
        texts.append((OPTION, o, ox + 5, oy, 340, 40, "centre", True))
    # a news event: the broadsheet, 528 x 595
    nx, ny = 800, 120
    cv.alpha_composite(img(EV + "event_news_bg.dds"), (nx, ny))
    cv.alpha_composite(cover(ART + "map_rouental.jpg", 399, 155), (nx + 59, ny + 91))
    cv.alpha_composite(img(EV + "event_news_pic_overlay.dds"), (nx + 59, ny + 91))
    cv.alpha_composite(img(EV + "event_button_minimize.dds"), (nx + 10, ny + 10))
    texts += [(TITLE, SAMPLE["news_title"], nx + 12, ny + 260, 490, 32, "centre", True),
              (TEXT, SAMPLE["news_text"], nx + 39, ny + 121 + 170, 460, 190, "left", False)]
    for i, o in enumerate(SAMPLE["news_options"]):
        ox, oy = nx + 80, ny + 520 + i * 47
        cv.alpha_composite(img(EV + "event_option_entry.dds").crop((0, 0, 352, 48)), (ox - 26, oy))
        texts.append((OPTION, o, ox + 5 - 26, oy, 340, 40, "centre", True))
    arr = np.asarray(cv.convert("RGB"), dtype=np.float32) / 255
    for font, s, x, y, w, h, fmt, valign in texts:
        V.draw_text(arr, font, s, x, y, w, fmt, max_h=h, valign=valign, check="event " + s[:20])
    Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8)).save(BUILD + "preview_events.png")
    print("events preview written", "problems:", V.problems or "none")


if __name__ == "__main__":
    main()
