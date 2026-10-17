"""Layout of the events (interface/eventwindow.gui, v0.8): the option plates, shared by the texture
(gen_textures.py, 'ev_option'), make_events.py and preview_events.py.

The game draws every option the same way (one event_option_entry for all event windows): its picture at the entry's
top left, its text in the Name box. The plate is OPTION_W wide inside the game's 352 px picture, and each window's
options_grid is moved so the plate sits in the middle of the room it has (the user, 2026-10-15: the options sat
"significantly closer to the image than ... to the other side of the box. It should be centered between the two"):
- a country event: between the picture's gilt frame (its outer line at x 218.5) and the card's inner rail (576.5);
- a news event: the broadsheet's middle (its rails at 6.5 and 521.5);
- a leader event: the card's middle (580 wide);
- an operative event: under its text column (x 70-470).
"""
OPTION_W = 334              # the plate; the game's picture is 352 wide
OPTION_PAD = 10             # the text's margin inside the plate
OPTION_TEXT_Y, OPTION_TEXT_H = 3, 42   # the text's box: the plate's height (it is drawn at y 2-46), three 14 px lines
CENTRES = {"EventWindow": (218.5 + 576.5) / 2, "EventWindow_News": (6.5 + 521.5) / 2, "EventWindow_leader": 290,
           "EventWindow_Operative": 270}


# the news page, 528 wide (v0.8.1): the game puts its picture (x 59) 5.5 px and its headline (x 12, 490 wide) 7 px
# left of the page's middle, and its story's box (x 39, 460 wide) 5 px right of it, which the centred masthead showed
# up; they are centred on it
NEWS_CX = 264
NEWS_PIC_W, NEWS_TITLE_W, NEWS_TEXT_W = 399, 490, 460     # the picture's box (and its overlay), the headline, the story
NEWS_PIC_X = int(NEWS_CX - NEWS_PIC_W / 2)                 # 64: the 399 px box centred to half a pixel
NEWS_TITLE_X = NEWS_CX - NEWS_TITLE_W // 2                 # 19
NEWS_TEXT_X = NEWS_CX - NEWS_TEXT_W // 2                   # 34


# the news story (v0.10.2, the user's screenshot of 2026-10-17, "Text on event runs over": Cardonia's capitulation, 13
# lines of the body font from y 291, ran over the rule and diamond the page draws above its option). The page is a
# fixed picture, so the story has the room between the headline and that ornament: from y 291 (the midsection's 121
# and the box's 170) to 485, where the diamond's top point is (gen_textures.EV_NEWS: the rule at 492.5, the diamond a
# 10 px square turned on its centre). It is set in the 13 px body font on a 14 px line: 13 lines fit, the most any news
# event Valsora ships needs with the longest names in it (country_capitulated.0, nuke_dropped.2), and all but one of
# the game's 324 news stories (14 lines); in the 15 px font, 12 lines fit and 11 of Valsora's 27 stories need 13 or 14
# (counted with "The Sacred Principality of Rouental" for every country's name).
NEWS_TEXT_FONT = "valsora_deco_body_13"
NEWS_STORY_Y, NEWS_STORY_END = 291, 485
# where the game puts the news option (inferred from the screenshot: its plate's top edge at y 507, so the entry at
# 505, under a story ending at 499): the bottom window under the midsection, which is the game's 385 tall unless the
# story is taller (as the country event's middle grows with its text), the options grid 1 px above its top
NEWS_MID_Y, NEWS_MID_H, NEWS_TEXT_DY = 121, 385, 170


def news_option_y(story_h):
    """the news option's top on the page for a story story_h tall"""
    return NEWS_MID_Y + max(NEWS_MID_H, NEWS_TEXT_DY + story_h) - 1


# the text boxes' height in lines of the body font (16 px), where the game's typewriter font (16 px too) had 14 (a
# country event) and 21 (a leader event): a box too short drops the lines past it, and the body font needs up to two
# more lines than the game's for the game's longest texts (stability.32: 16 lines where the game's 14 fit; 21 of the
# game's 5,736 texts lost lines at a country event's 14, among them two La Resistance events Valsora ships). The game
# stretches those events' middle to the text, so a taller box only matters for the texts that need it.
TEXT_LINES = {"EventWindow": 16, "EventWindow_leader": 24}


def grid_x(window):
    """options_grid's x: the plate centred on the window's centre line (to the nearest pixel)"""
    return int(CENTRES[window] - OPTION_W / 2)


# the news masthead (v0.8.1): the paper's name in two words of one width either side of a globe of Valsora
NEWS_WORDS = ("VALSORAN", "STANDARD")
NEWS_VIEW = (-95.0, 18.0)        # the globe (globe_art.globe): above Nonscio and Araseos, as the tension globe (v0.8.2)
NEWS_SIZE, NEWS_GLOBE = 27, 60   # the words' size (Federo), the globe's diameter
# the globe's design (v0.8.3): the author's favourite of the options (2026-10-15, later: "I think the globe I'm sending
# now is my current favorite of your designs"), the newsreel globe girdled by a tilted ring; "lit" is v0.8.2's
NEWS_GLOBE_STYLE = "ringed"


def news_globe():
    """(the masthead's globe, a PIL image NEWS_GLOBE across; whether the masthead draws a gilt rim round it: not round
    the ringed one, whose ring reaches past the globe)"""
    import globe_art as GA
    if NEWS_GLOBE_STYLE == "ringed":
        return GA.globe_ringed(NEWS_GLOBE, NEWS_VIEW), False
    return GA.globe(NEWS_GLOBE, NEWS_VIEW), True
NEWS_CY, NEWS_GAP = 52.5, 13     # the band's middle (between the rules at 25.5 and 79.5), the words' gap to the medallion


def news_masthead(words, globe_uri, font_path, size=NEWS_SIZE, d=NEWS_GLOBE, rim=True):
    """(the masthead's SVG, 528 x 105; the path of its double rules) for two words: both set to the wider one's width
    (the narrower is tracked out), each placed by its ink (Pillow's measure of the font the page uses), the same distance
    either side of the medallion; the rules as wide as the words' ink, broken round the medallion, ending in diamonds.
    rim: a gilt line round the globe (not for a globe drawn with a ring round it)"""
    from PIL import ImageFont
    f = ImageFont.truetype(font_path, size)
    cx, cy, r = NEWS_CX, NEWS_CY, d / 2

    def ink(word, track):
        x0, _, x1, _ = f.getbbox(word)
        return x1 - x0 + track * (len(word) - 1), x0
    t0 = size * .12
    w = max(ink(word, t0)[0] for word in words)
    tracks = [t0 + (w - ink(word, t0)[0]) / max(1, len(word) - 1) for word in words]
    lx, rx = cx - r - 4 - NEWS_GAP - w, cx + r + 4 + NEWS_GAP          # where each word's ink starts
    base = cy + size * .365                                             # Federo's capitals (.73 em) centred on the band
    rules = "".join(f"M{lx:.0f},{y}H{cx - r - 5}M{cx + r + 5},{y}H{2 * cx - lx:.0f}" for y in (22.5, 25.5, 79.5, 82.5))
    svg = ('<svg width="528" height="105" style="position:absolute;left:0;top:0"><defs><linearGradient id="nwg" x1="0" '
           'y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFF3C8"/><stop offset=".45" stop-color="#E3C77E"/>'
           '<stop offset="1" stop-color="#9C7836"/></linearGradient></defs>'
           + "".join(f'<rect x="{x - 2.5}" y="{y - 2.5}" width="5" height="5" transform="rotate(45 {x} {y})" fill="#C9A55A"/>'
                     for x in (cx - r - 8, cx + r + 8) for y in (24, 81))
           + f'<circle cx="{cx}" cy="{cy}" r="{r + 3.5}" fill="#0B1014" stroke="#C9A55A" stroke-width="1"/>'
           f'<image href="{globe_uri}" x="{cx - r}" y="{cy - r}" width="{d}" height="{d}"/>'
           + (f'<circle cx="{cx}" cy="{cy}" r="{r - .5}" fill="none" stroke="#E3C77E" stroke-width="1"/>' if rim else "")
           + "".join(f'<text x="{x - ink(word, tr)[1]}" y="{base}" font-family="Federo" font-size="{size}" '
                     f'letter-spacing="{tr}" fill="url(#nwg)">{word}</text>' for word, x, tr in zip(words, (lx, rx), tracks))
           + '</svg>')
    return svg, rules

