"""Previews of the diplomatic action windows on their new pictures (diplo_art.py): each window drawn from the game's .gui
(its title, texts, buttons and the boxes of the lists it fills in, in place) over the map, centred as the game shows
it, and the header of every picture with the emblem it carries; beside them, the game's own look.

    python preview_diplo.py   -> build/preview_diplo.png (+ _vanilla.png)

They show the game's art, so they stay in the git-ignored build/ folder.
"""
import os

import numpy as np
from PIL import Image, ImageDraw

import diplo_art as D
import preview_panels as PP
import validate_preview as V
from paths import BUILD, MOD, VANILLA

REPLY = "They will accept"
# (file, window, sample texts, elements hidden, the background the game swaps in)
WINDOWS = [
    ("countrydiplomacyview.gui", "declare_war",
     dict(title="Declare war", description="Declare war on Cardonia?", threat_value="+12%"), (), None),
    ("countrydiplomacyview.gui", "generate_wargoal",
     dict(title="Justify War goal", description="Justifying a war goal on Cardonia will take 96 days and raise world "
          "tension by 4%.", wargoal_name="Conquer", wargoal_warning="They have no war goal on us", threat_value="+4%"),
     (), None),
    ("countrydiplomacyview.gui", "lend_lease",
     dict(title="Start Lend lease", current_lease_info_header="Current Lend lease:", current_lease_info="None",
          num_convoys="12", diplo_reply=REPLY, autonomy_score_gain=""), (), None),
    ("countrydiplomacyview.gui", "invite_faction_diplomacy_controller",
     dict(title="Invite to faction", description="Invite Guedelon to join the Association of Reibonnaise States?",
          diplo_reply=REPLY), (), None),
    ("countrydiplomacyview.gui", "standard_diplomacy_controller",
     dict(title="Improve relations", description="Send diplomats to Lanzerac to improve our relations. It costs 0.20 "
          "political power a day.", diplo_reply=REPLY), (), "GFX_diplo_action_imp_relations_bg"),
    ("factions/faction_popup.gui", "faction_popup",
     dict(title="Leave faction", description="Leave the Association of Reibonnaise States?", diplo_reply=REPLY), (), None),
    ("countrydiplomacyview.gui", "stage_coup",
     dict(title="Cancel staging the coup", cancel_diplo_action_text="Cancel staging the coup"), ("description",), None),
    ("countrydiplomacyview.gui", "send_volunteers",
     dict(title="Send volunteers", time_text="30 days", ask_for_air_volunteers="Send air volunteers", empty="",
          description="Volunteers fight for Hollier under its command, and come back when the war is over."), (), None),
    ("operative.gui", "boost_party_popularity_mission_window",
     dict(title="Boost party popularity", description="Choose the party to boost in Seigne:"), (), None),
    ("countrydiplomacyview.gui", "add_wargoal",
     dict(title="Add war goal", wargoal_name="No war goal selected", description=""), (), None),
    ("countrydiplomacyview.gui", "send_attache",
     dict(title="Send attaché", description="Send an attaché to Hollier. They will advise its army and come back "
          "with experience.", they_get_text_box="They get:", diplo_reply=REPLY), (), None),
    ("countrydiplomacyview.gui", "request_licensed_production",
     dict(title="Request License Production", description="Cost: 2", diplo_reply=REPLY), (), None),
]


def _path(f, vanilla):
    p = MOD + "interface/" + f
    return p if (not vanilla and os.path.isfile(p)) else VANILLA + "interface/" + f


def _with_background(win, spr):
    out = []
    for k, b in win:
        if k == "background" and isinstance(b, list):
            b = [(kk, (spr if kk and kk.lower() in ("spritetype", "quadtexturesprite") else vv)) for kk, vv in b]
        out.append((k, b))
    return out


def _origo(elems):
    """the renderer places elements by their top left corner: an element with origo = center_up (the justification
    window's right-hand list) is moved left by half its width, as the game centres it"""
    out = []
    for k, b in elems:
        if isinstance(b, list):
            a = V.attrs(b)
            if str(a.get("origo", "")).lower().strip('"') == "center_up" and V.sub(b, "position") and V.sub(b, "size"):
                (x, y), (w, _) = V.xy(V.sub(b, "position")), V.xy(V.sub(b, "size"))
                b = [(kk, ([("x", str(float(x) - float(w) / 2)), ("y", y)] if kk == "position" else vv))
                     for kk, vv in b if kk != "origo"]
            b = _origo(b)
        out.append((k, b))
    return out


def draw_window(f, name, samples, hide, bg, vanilla):
    path = _path(f, vanilla)
    win = PP.find_window(V.load(path), name)
    assert win is not None, (path, name)
    if bg:
        win = _with_background(win, bg)
    win = _origo(win)
    cv = PP.backdrop(False)
    p = PP.Panel(hide=hide, samples=samples, vanilla_only=vanilla, outline_lists=True, vars_=PP.gui_vars(path))
    p.draw(cv, [("containerWindowType", win)], 0, 0, 1920, 1080)
    x, y = (float(v) for v in V.xy(V.sub(win, "position")))
    w, h = (float(v) for v in V.xy(V.sub(win, "size")))
    spr = bg or next((V.attrs(b).get("spritetype") or V.attrs(b).get("quadtexturesprite"))
                     for k, b in win if k == "background" and isinstance(b, list))
    _, img = PP.sprite(spr, vanilla)
    if img is not None:
        w, h = max(w, img.width), max(h, img.height)
    x0, y0 = 960 + x, 540 + y
    im = Image.fromarray((np.clip(cv, 0, 1) * 255).astype(np.uint8))
    return im.crop((int(x0) - 10, int(y0) - 10, int(x0 + w) + 10, int(y0 + h) + 10))


def headers(vanilla, cols=3, crop=84):
    """the top of every picture, labelled"""
    items = [(k, rel, w, h) for k, rel, w, h, _ in D.ADDS]
    emb = {s[0]: s[4] for s in D.SPECS}
    cw, ch = 537, crop + 22
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cw * cols + 10, ch * rows + 10), (24, 30, 34))
    d = ImageDraw.Draw(sheet)
    for i, (k, rel, w, h) in enumerate(items):
        img = PP.texture(rel, vanilla_only=vanilla)
        if img is None:
            continue
        x, y = 10 + (i % cols) * cw, 10 + (i // cols) * ch
        bgc = Image.new("RGBA", (img.width, min(crop, img.height)), (24, 30, 34, 255))
        bgc.alpha_composite(img.crop((0, 0, img.width, min(crop, img.height))))
        sheet.paste(bgc.convert("RGB"), (x, y))
        d.text((x + 2, y + min(crop, img.height) + 4), f"{k}  {os.path.basename(rel)}  {w}x{h}"
               + (f"  [{emb[k]}]" if k in emb and not vanilla else ""), fill=(201, 165, 90), font=PP.ttf(12))
    return sheet


def draw(vanilla):
    wins = [draw_window(*w, vanilla=vanilla) for w in WINDOWS]
    cols = 3
    cw = max(w.width for w in wins)
    rows = [wins[i:i + cols] for i in range(0, len(wins), cols)]
    rh = [max(w.height for w in r) for r in rows]
    hs = headers(vanilla)
    W = max(cw * cols, hs.width)
    sheet = Image.new("RGB", (W, sum(rh) + hs.height), (24, 30, 34))
    y = 0
    for r, h in zip(rows, rh):
        for i, w in enumerate(r):
            sheet.paste(w, (i * cw, y))
        y += h
    sheet.paste(hs, (0, y))
    sheet.save(BUILD + "preview_diplo" + ("_vanilla" if vanilla else "") + ".png")


if __name__ == "__main__":
    draw(False)
    draw(True)
    print("wrote build/preview_diplo.png (+ _vanilla); problems:", [q for q in V.problems if "overflow" in q or "lines" in q])
