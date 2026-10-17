"""Draws every mockup in this folder (a proposal: nothing here is in the mod).

    CHROMIUM_PATH=/opt/pw-browsers/chromium python3 make.py            every screen, the overview sheet, the comparisons
    python3 make.py division_details ship_details                      only those

Each screen is a 1920 x 1080 PNG here (256 colours, to keep the repository light) and at full colour in
deco_ui/build/next_screens/full/ (git-ignored). overview.png is the contact sheet. The comparisons with the game's own
look (build/next_screens/compare_<screen>.png) use deco_ui/build/inventory/<screen>_game.png, the screen inventory's
pictures of the game's art, so they stay in the git-ignored build/ folder.
Needs: Pillow, numpy, Playwright (Chromium), deco_ui/build/preview_topbar.png for the top bar (tools/build_all.py
draws it; without it the screens have no top bar), and the game's files in deco_ui/reference/vanilla for the trait
names (screens_commanders.py) and guilayout.py.
"""
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("NS_TMP", "/tmp")

import deco as D  # noqa: E402
import screens_units as U  # noqa: E402
import screens_commanders as C  # noqa: E402
import screens_war as WR  # noqa: E402
import screens_frontend as F  # noqa: E402

# (file name, drawing, title on the sheet, the inventory's picture of the game's look or None)
SCREENS = [
    ("unit_counters", U.unit_counters, "Unit counters and map icons", None),
    ("unit_counters_key", U.unit_counters_key, "Unit counters: the key (3x)", None),
    ("division_details", U.division_details, "Division details", "division_stats"),
    ("ship_details", U.ship_details, "Ship details", None),
    ("army_trait_tree", C.army_trait_tree, "General's trait tree", "traittree"),
    ("navy_trait_tree", C.navy_trait_tree, "Admiral's trait tree", None),
    ("abilities", U.abilities, "Commander abilities", None),
    ("theatres", U.theatres, "Theatres and army groups", "theatres"),
    ("right_click_menu", U.right_click_menu, "Right-click menu", None),
    ("operations", WR.operations, "Operations", "operation"),
    ("war_overview", WR.war_overview, "War overview", "waroverview"),
    ("peace_conference", WR.peace_conference, "Peace conference", "peace"),
    ("raids", WR.raids, "Raids", "raids"),
    ("messages", WR.messages, "Diplomatic message icons", None),
    ("end_of_game", WR.end_of_game, "End of game", "endgame"),
    ("server_browser", F.server_browser, "Multiplayer: server browser", "multiplayer"),
    ("multiplayer_host", F.multiplayer_host, "Multiplayer: host a game", None),
    ("career_profile", F.career_profile, "Career profile", "career"),
    ("friends", F.friends, "Friends", None),
    ("achievements", F.achievements, "Achievements", "achievements"),
]


def compare(name, game):
    """the game's look (the inventory's picture) beside the mockup, for the author (holds the game's art: build/ only)"""
    from PIL import Image, ImageDraw, ImageFont
    gp = os.path.join(D.DECO, "build", "inventory", f"{game}_game.png")
    if not os.path.isfile(gp):
        return None
    g = Image.open(gp).convert("RGB")
    m = Image.open(os.path.join(D.PRIVATE, "full", f"{name}.png")).convert("RGB")
    W2 = 960
    g = g.resize((W2, round(g.height * W2 / g.width)))
    m = m.resize((W2, round(m.height * W2 / m.width)))
    h = max(g.height, m.height) + 40
    out = Image.new("RGB", (2 * W2 + 20, h), (11, 16, 20))
    out.paste(g, (0, 40))
    out.paste(m, (W2 + 20, 40))
    d = ImageDraw.Draw(out)
    f = ImageFont.truetype(os.path.join(D.FONTS, "josefinsans", "JosefinSans[wght].ttf"), 20)
    d.text((10, 10), "the game's own (the screen inventory's picture)", fill=(183, 166, 128), font=f)
    d.text((W2 + 30, 10), "proposal (next_screens)", fill=(227, 199, 126), font=f)
    p = os.path.join(D.PRIVATE, f"compare_{name}.png")
    out.save(p, optimize=True)
    return p


def overview(names):
    """the contact sheet: every mockup at a fifth of its size, named"""
    from PIL import Image
    cols, tw, th = 4, 440, 248
    rows = (len(names) + cols - 1) // cols
    W_, H_ = 60 + cols * (tw + 20), 170 + rows * (th + 56)
    body = D.box(0, 0, W_, H_, f"background:{D.STRIPES},linear-gradient(180deg,#141E24,#0B1014)")
    body += D.title(40, 40, "Next screens: proposals", 34, track=.22)
    body += D.text(40, 92, "Mockups of the screens the Deco UI has not restyled yet (the screen inventory's), at the game's 1920 x 1080 "
                   "with each window at its size and place. Not in the mod.", 16, D.CREAM2, W_ - 80, font="bod", weight=400)
    body += D.rule(40, 124, W_ - 40)
    for i, (n, _, t, _g) in enumerate(names):
        c, r = i % cols, i // cols
        x, y = 40 + c * (tw + 20), 150 + r * (th + 56)
        im = Image.open(os.path.join(D.PRIVATE, "full", f"{n}.png")).convert("RGB").resize((tw, th), Image.LANCZOS)
        body += f'<img class="a" src="{D.uri_of(im)}" style="left:{x}px;top:{y}px;width:{tw}px;height:{th}px">'
        body += D.box(x - 1, y - 1, tw + 2, th + 2, f"box-shadow:0 0 0 1px {D.RULE}")
        body += D.label(x, y + th + 12, f"{i + 1:02d}  {t}", 11, D.GILT, tw, track=.16)
        body += D.text(x, y + th + 30, f"{n}.png", 12, D.LABEL, tw)
    D.render(body, os.path.join(D.OUT, "overview.png"), W_, H_, palette=True)


def main(only):
    os.makedirs(os.path.join(D.PRIVATE, "full"), exist_ok=True)
    todo = [s for s in SCREENS if not only or s[0] in only]
    for name, fn, title, game in todo:
        full = D.render(fn(), os.path.join(D.PRIVATE, "full", f"{name}.png"))
        from PIL import Image
        im = Image.open(full).convert("RGB").quantize(256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.FLOYDSTEINBERG)
        im.save(os.path.join(D.OUT, f"{name}.png"), optimize=True)
        if game:
            compare(name, game)
        print("drew", name)
    if not only:
        overview(SCREENS)
        print("drew overview")
    D.close_browser()


if __name__ == "__main__":
    main(set(sys.argv[1:]))
