"""Mockups of the front end's rarely seen screens: multiplayer (the server browser, matchmaking.gui, with
frontendmultiplayerview.gui's name and connect button; the host window), the career profile (career_profile/), friends
(frontend_friends_view.gui) and achievements (achievements.gui, in game). The boxes are the game's."""
import deco as D

MENU_DIM = .35


def sort_head(x, y, w, s, lit=False):
    return ((D.lit_bar(x, y, w, 23, 4) if lit else D.bar(x, y, w, 23, c=4, shine=.15))
            + D.text(x, y + 1, s, 10.5, "#FBEAB4" if lit else D.LABEL, w, "center", weight=600, track=.14, caps=True, h=22, valign=True))


def editbox(x, y, w, s, placeholder=False, h=27):
    return (D.well(x, y, w, h, c=3)
            + D.text(x + 10, y + (h - 14) / 2 + 1, s, 14, D.LABEL if placeholder else D.CREAM, w - 20, font="sans", weight=500))


def big_tab(x, y, w, h, s, lit):
    """the matchmaking tabs (187 x 52, 2 frames) and the profile's (258 x 50)"""
    return ((D.lit_bar(x, y, w, h, 8) if lit else D.bar(x, y, w, h, D.DIM_FILL, "rgba(201,165,90,.45)", 8, .1))
            + D.text(x, y + 2, s, 15, "#FBEAB4" if lit else D.LABEL, w, "center", font="fed", track=.16, caps=True, h=h - 4, valign=True))


def server_browser():
    X, Y, WW, HH = 449, 260, 1022, 560
    o = D.backdrop("menu", MENU_DIM)
    o += D.window(X, Y, WW, HH)
    o += D.title(705, 278, "Multiplayer", 28, w=512, align="center", track=.24)
    o += D.fade_rule(560, 316, 1360)
    o += D.close(1425, 286, 32)
    o += big_tab(469, 330, 187, 44, "Servers", True) + big_tab(1259, 330, 187, 44, "Community", False)
    # the player's name (469, 405; 190 x 27) and the version (upper right of the view)
    o += D.label(469, 386, "Player name", 9.5, D.LABEL, 190, track=.16)
    o += editbox(469, 400, 190, "Rouental")
    o += D.text(1186, 380, "Valsora 2036 · HOI4 1.19.3", 12, D.LABEL, 256, "right")
    # filters: no password, not full, has players (764 / 805); same mod, same version (944 / 985); name and tags (924 / 1119)
    for (cx, cy, s, on) in ((764, 337, "No password", True), (764, 369, "Not full", True), (764, 401, "Has players", False),
                            (944, 337, "Same mod (Valsora)", True), (944, 369, "Same version", True)):
        o += D.checkbox(cx + 7, cy + 5, on) + D.text(cx + 41, cy + 9, s, 14, D.CREAM2, 200)
    o += editbox(924, 405, 190, "Server name", True) + editbox(1119, 405, 190, "Search tags", True)
    o += D.button(1316, 403, 123, 32, "Filter", size=11)
    # the list's sort buttons (y 475) and the servers (970 x 288 from 469, 502; rows of 32)
    for (x, w, s, lit) in ((474, 89, "Password", False), (562, 247, "Name", True), (808, 89, "Slots", False), (895, 89, "Version", False),
                           (982, 247, "Tags", False), (1224, 134, "Mod", False), (1356, 89, "Status", False)):
        o += sort_head(x, 475, w, s, lit)
    o += D.well(469, 500, 978, 290)
    rows = [(True, "Vale of Reibonne · Saturday", "5 / 8", "1.19.3", "historical, friends", "Valsora", "Lobby"),
            (False, "Merlo's Midtierre Sea", "3 / 12", "1.19.3", "naval, casual", "Valsora", "Lobby"),
            (True, "Association League 4", "8 / 8", "1.19.3", "league, ironman", "Valsora", "Playing"),
            (False, "Gazetteer test game", "1 / 6", "1.19.3", "test", "Valsora", "Lobby"),
            (False, "Krionik and friends", "4 / 10", "1.19.3", "great powers", "Valsora", "Playing")]
    for i, (pw, name, slots, ver, tags, mod, st) in enumerate(rows):
        y = 504 + i * 32
        sel = i == 0
        o += D.box(473, y, 970, 30, f"background:{'linear-gradient(90deg,rgba(46,110,96,.6),rgba(46,110,96,.2))' if sel else ('rgba(255,255,255,.025)' if i % 2 else 'transparent')};"
                                   f"box-shadow:inset 0 -1px 0 rgba(201,165,90,.15){',inset 2px 0 0 #F1DC9C' if sel else ''}")
        if pw:
            o += D.svg(509, y + 7, 16, 16, '<rect x="3.5" y="7.5" width="9" height="7" stroke="#E3C77E" stroke-width="1.3"/><path d="M5.5 7.5V5a2.5 2.5 0 0 1 5 0v2.5" stroke="#E3C77E" stroke-width="1.3"/>')
        o += D.text(573, y + 8, name, 14, "#FBEAB4" if sel else D.CREAM, 230, font="fed", track=.02)
        o += D.value(804, y + 9, slots, 13, D.CREAM, 100, "center", weight=600)
        o += D.value(897, y + 9, ver, 13, D.CREAM2, 100, weight=500)
        o += D.text(1005, y + 9, tags, 13, D.LABEL, 200, "center")
        o += D.text(1231, y + 9, mod, 13, D.CREAM2, 120, "center")
        o += D.text(1384, y + 9, st, 12, D.POS if st == "Lobby" else "#E7B75A", 80, weight=600)
    # the foot: back (469), connect to IP (591), refresh (699 / 849 / 999), join (1149), host (1299)
    o += D.rule(X + 10, 780, X + WW - 10, "rgba(201,165,90,.5)")
    o += D.button(469, 790, 118, 32, "Back", size=11) + D.button(593, 790, 104, 32, "Server ID", size=10)
    for i, s in enumerate(("Refresh", "LAN", "Internet")):
        o += D.button(701 + i * 150, 790, 144, 32, s, size=11)
    o += D.button(1151, 790, 144, 32, "Join", "gold", 12) + D.button(1301, 790, 144, 32, "Host", size=11)
    return o


def multiplayer_host():
    o = server_browser()
    o += D.box(0, 0, D.W, D.H, "background:rgba(6,9,11,.55)")
    X, Y, WW, HH = 710, 300, 500, 480
    o += D.window(X, Y, WW, HH)
    o += D.band(X + 6, Y + 6, WW - 12, 52) + D.rule(X + 6, Y + 58, X + WW - 6)
    o += D.title(X, 320, "Host Server", 24, w=WW, align="center", track=.22)
    o += D.diamond(X + 60, 333, 6) + D.diamond(X + WW - 60, 333, 6)
    for i, (lab, val, ph) in enumerate((("Server name", "Vale of Reibonne · Saturday", False), ("Password", "••••••", False),
                                        ("Tags", "historical, friends", False), ("Description", "Rouental and the Association", False))):
        y = 377 + i * 50
        o += D.label(810, y + 2, lab, 10, D.GILT, 300, track=.18)
        o += editbox(810, y + 19, 300, val, ph, 30)
    for i, (s, on) in enumerate((("Public", False), ("Private", False), ("Friends only", True))):
        x = 750 + i * 130
        o += D.checkbox(x + 7, 595, on) + D.text(x + 40, 599, s, 14, D.CREAM2, 120)
    o += D.rule(X + 20, 636, X + WW - 20, "rgba(201,165,90,.45)")
    o += D.button(785, 652, 148, 34, "Cancel", size=12) + D.button(974, 652, 148, 34, "Host", "gold", 13)
    return o


# ---------------------------------------------------------------- career profile
def career_profile():
    X, Y, WW, HH = 375, 145, 1170, 790
    o = D.backdrop("menu", MENU_DIM)
    o += D.window(X, Y + 40, WW, HH - 40)
    # the tabs (258 x 50 from 382, 141) over the window's top, the close (1505, 150)
    o += big_tab(386, 141, 250, 44, "Career Profile", True) + big_tab(636, 141, 250, 44, "Awards", False) + big_tab(886, 141, 250, 44, "Badge", False)
    o += D.diamond(866, 158, 9, "#E7B75A", "box-shadow:0 0 0 1px #0B1014")
    o += D.close(1505, 150, 33)
    # the header (1170 x 180 from y 187): the profile's background picture (574 x 140), its picture (126 x 126), name,
    # career points, privacy (upper right) and the note under it
    o += D.box(378, 203, 574, 140, f"background:{D.STRIPES},radial-gradient(ellipse at 30% 50%,#22343C,#0D1418 75%);box-shadow:inset 0 0 0 1px rgba(201,165,90,.5)")
    o += D.sunburst(446, 273, 120, .14)
    o += D.speed_lines(650, 940, 260, True) + D.speed_lines(650, 900, 290, True, ((0, 1),))
    o += D.box(383, 210, 126, 126, f"background:{D.GOLD};clip-path:polygon(50% 0,100% 25%,100% 75%,50% 100%,0 75%,0 25%)")
    o += D.box(385, 212, 122, 122, "background:radial-gradient(circle at 50% 35%,#1E2B33,#0B1014 75%);clip-path:polygon(50% 0,100% 25%,100% 75%,50% 100%,0 75%,0 25%)")
    o += D.svg(406, 233, 80, 80, '<g stroke="#E3C77E" stroke-width="2"><circle cx="40" cy="40" r="24"/><path d="M16 40h48M40 16c-9 7-9 41 0 48M40 16c9 7 9 41 0 48"/>'
                                 '<path d="M40 6v6M40 68v6M6 40h6M68 40h6"/></g>')
    o += D.title(530, 223, "Rouental", 28, track=.12)
    o += D.value(530, 264, "14,820", 26, "#F1DC9C", 280) + D.label(530, 300, "Career points", 10, D.LABEL, 280, track=.2)
    o += D.label(1337, 209, "Profile visibility", 10, D.LABEL, 180, "center", track=.16)
    o += D.button(1347, 233, 18, 18, "") + D.text(1337, 236, "Public", 14, D.CREAM, 180, "center", font="fed")
    o += D.button(1507, 233, 18, 18, "")
    o += D.text(1337, 270, "Using console commands and most mods will prevent awards from being tracked", 12, D.LABEL, 180, "right", font="bod", weight=400, lh=1.35)
    # the statistics: filters (country, data set, game mode: 244 x 48 each), compare toggle, subscribe, the stat cards
    o += D.rule(383, 362, 1537)
    for i, s in enumerate(("All countries", "Base game", "All modes")):
        x = 380 + i * 254
        o += D.well(x, 380, 244, 44, c=5) + D.text(x, 393, s, 15, D.CREAM, 244, "center", font="fed", track=.04)
        o += D.svg(x + 210, 395, 14, 14, '<path d="M2 4l5 6 5-6" stroke="#E3C77E" stroke-width="1.6"/>')
    o += D.text(1215, 393, "Compare to your statistics", 14, D.CREAM2, 200, "right") + D.checkbox(1424, 390, False, 22)
    stats = [("Campaigns", "12", "started with Rouental 9"), ("Hours played", "340", "since 1 January 2036"), ("Wars won", "18", "of 21 fought"),
             ("Peace conferences", "14", "led 11"), ("Divisions destroyed", "1,204", "lost 386"), ("Focuses completed", "412", "Rouental: Steady As She Goes ×6"),
             ("States annexed", "96", "Cardonia most often"), ("Nations puppeted", "7", "Placeholdaire ×3")]
    for i, (k, v, sub) in enumerate(stats):
        c, r = i % 4, i // 4
        x, y = 395 + c * 284, 450 + r * 150
        o += D.box(x, y, 270, 136, f"background:{D.STRIPES},linear-gradient(180deg,#1A252C,#0E1519);box-shadow:inset 0 0 0 1px rgba(201,165,90,.45)")
        o += D.corners(x, y, 270, 136, True)
        o += D.label(x + 20, y + 22, k, 10.5, D.GILT, 230, track=.18)
        o += D.value(x + 20, y + 48, v, 34, D.CREAM, 230)
        o += D.rule(x + 20, y + 96, x + 250, "rgba(201,165,90,.35)")
        o += D.text(x + 20, y + 106, sub, 12, D.LABEL, 230)
    return o


# ---------------------------------------------------------------- friends
def friends():
    X, Y, WW, HH = 375, 145, 1170, 790
    o = D.backdrop("menu", MENU_DIM)
    o += D.window(X, Y + 40, WW, HH - 40)
    o += big_tab(385, 141, 250, 44, "Friends", True)
    o += D.close(1505, 150, 33)
    # the grid (1134 x 720 from 395, 200; cards of 218 x 327 in slots of 228 x 337)
    people = [("Merlo", "In the lobby", True), ("Odile", "Online", True), ("Bastien", "Playing Valsora", True),
              ("Hélène", "Offline", False), ("Gaspard", "Offline", False), ("Aubert", "Offline", False), ("Ines", "Offline", False)]
    for i, (n, st, on) in enumerate(people):
        c, r = i % 5, i // 5
        x, y = 398 + c * 228, 205 + r * 337
        o += D.box(x, y, 218, 327, f"background:{D.STRIPES},linear-gradient(180deg,#18232A,#0E1519);box-shadow:inset 0 0 0 1px rgba(201,165,90,.5)")
        o += D.box(x + 1, y + 1, 216, 70, f"background:radial-gradient(ellipse at 50% 100%,#22343C,#0D1418 80%)")
        o += D.sunburst(x + 110, y + 70, 90, .12)
        # the picture (113 x 113, centred on 110, 70), the name (35, 150), the status (35, 185), view profile (49, 220)
        o += D.box(x + 53, y + 13, 113, 113, f"background:{D.GOLD if on else 'rgba(201,165,90,.5)'};clip-path:polygon(50% 0,100% 25%,100% 75%,50% 100%,0 75%,0 25%)")
        o += D.box(x + 55, y + 15, 109, 109, "background:radial-gradient(circle at 50% 35%,#1E2B33,#0B1014 75%);clip-path:polygon(50% 0,100% 25%,100% 75%,50% 100%,0 75%,0 25%)")
        o += D.title(x + 55, y + 55, n[0], 30, w=109, align="center", track=0)
        o += D.text(x + 35, y + 150, n, 18, D.CREAM, 150, "center", font="fed", track=.06)
        o += D.diamond(x + 47, y + 192, 7, D.POS if on else "#4A565C")
        o += D.text(x + 35, y + 186, st, 13, D.POS if on else D.LABEL, 150, "center", weight=600)
        o += D.button(x + 49, y + 220, 123, 34, "View Profile", size=10)
    return o


# ---------------------------------------------------------------- achievements (in game, from the menu)
ACH = [("Valsora Rising", "Start a game in 2036.", "1 / 1", True), ("The Vale United", "As Rouental, have all eight Reibonnaise states in your faction.", "8 / 8", True),
       ("Steady As She Goes", "Keep Roland II Cahun on the throne until 2049.", "4 / 13", False),
       ("Map Maker", "Own every state of Nonscio.", "41 / 112", False), ("Carrier Strike", "Sink a carrier with carrier aircraft.", "0 / 1", False)]


def achievements():
    o = D.backdrop()
    X, Y, WW, HH = 612, 288, 795, 605
    o += D.window(X, Y, WW, HH)
    # the top bar (765 x 67 at 628, 300) with the title (760, 316); the trophies are the game's: here laurels and a cup
    o += D.band(628, 300, 765, 60) + D.rule(628, 360, 1393)
    o += D.title(760, 316, "Achievements", 28, w=500, align="center", track=.24)
    for sx in (1, -1):
        cx = 1010 + sx * 310
        o += D.svg(cx - 22, 306, 44, 48, '<g stroke="#E3C77E" stroke-width="1.5"><path d="M14 8h16v8a8 8 0 0 1-16 0z"/><path d="M14 11H9a5 5 0 0 0 5 7M30 11h5a5 5 0 0 1-5 7"/>'
                                         '<path d="M22 24v8M16 36h12M18 32h8"/></g>')
    o += D.speed_lines(740, 830, 330, False) + D.speed_lines(1190, 1280, 330, True)
    # the list (760 x 470 at 630, 362): entries of 600 x 83 (95 a row) on their plates (729 x 96)
    o += D.well(630, 364, 760, 466)
    for i, (n, d, prog, got) in enumerate(ACH[:5]):
        y = 372 + i * 92
        if y + 86 > 828:
            break
        o += D.box(638, y, 744, 86, f"background:{D.STRIPES},linear-gradient(180deg,#1A252C,#0E1519);box-shadow:inset 0 0 0 1px rgba(201,165,90,{.6 if got else .3})")
        o += D.layer(D.octagon_pts(688, y + 43, 32), D.GOLD if got else "rgba(201,165,90,.35)")
        o += D.layer(D.octagon_pts(688, y + 43, 30.4), "radial-gradient(circle at 50% 35%,#2C665A,#123029 80%)" if got else "radial-gradient(circle at 50% 35%,#1A262E,#0B1014 75%)")
        o += D.ico("officer" if got else "search", 672, y + 27, 32, "#FBEAB4" if got else "rgba(227,199,126,.5)", 1.5)
        o += D.text(752, y + 14, n, 18, D.CREAM if got else D.CREAM2, 400, font="fed", track=.04)
        o += D.text(752, y + 40, d, 13, D.LABEL, 440, lh=1.3)
        o += D.box(1241, y + 30, 110, 26, f"background:#0B1014;clip-path:{D.chamfer(4)};box-shadow:inset 0 0 0 1px {'#E3C77E' if got else 'rgba(201,165,90,.4)'}")
        o += D.value(1241, y + 36, prog, 13, "#F1DC9C" if got else D.CREAM2, 110, "center")
    # the foot (765 x 48, lower left) and its close button (261 x 34)
    o += D.band(628, 834, 765, 46) + D.rule(628, 834, 1393)
    o += D.button(880, 840, 261, 34, "Close", size=12)
    return o
