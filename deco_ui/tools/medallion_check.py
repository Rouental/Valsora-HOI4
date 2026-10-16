"""Windows the medallion would hide (v0.8.4, after the navy panel: "like the army, the navy is covered by the flag tab").

The Deco UI's flag medallion and decisions seal hang over the screen's top left corner, down to layout.BELOW_MEDALLION
(y 173); the game's own top bar ends at about y 75, and the game puts many windows just under it. The game draws its
map-level views (the selected armies, fleets, air wings, operatives) under the top bar, so the medallion hides their
tops; the side panels and full-screen views are drawn over it, and carry a notch so the medallion still shows.

Every top-level window the game would show in that corner, read from the mod's .gui where it ships one and the game's
otherwise, must be one of:
  MOVED     shown below the medallion (make_mapviews.py moves it there);
  NOTCHED   a panel drawn over the top bar with the medallion's notch (make_panels.py, make_politics.py, make_focus.py
            and the screens restyled since): its file must carry the notch's pieces;
  REVIEWED  looked at, with the reason it may stay where it is.
Anything else is a problem, so a window a game update adds to that corner is looked at before it ships.

    python3 tools/medallion_check.py            # the report (validate_preview.py runs the check too)
    python3 tools/medallion_check.py --selftest # the check catches a window put back under the medallion
"""
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import layout as L  # noqa: E402
from paths import MOD, VANILLA  # noqa: E402

# the corner: the medallion's wings and seal (layout.MED, layout.SEAL) down to where the views now start; a window
# whose top lies above y 55 is a template the game places itself or a piece of the top bar, not a view under it
X0, X1 = L.MED["x"], L.MED["x"] + L.MED["w"] + 6
Y0, Y1 = 55, L.BELOW_MEDALLION

MOVED = {"armies_view", "air_selection_view", "operative_view", "naviesview_window", "hotjoin_window"}
# the notch's pieces in a window's file: the side panels' header picture, the politics screen's blocks, the focus tree's
NOTCH_MARKS = ("GFX_valsora_deco_panel_head_", "valsora_deco_pol_block", "valsora_deco_nf_block", "valsora_deco_notch")
NOTCHED = {"countryarmyview", "countryconstructionsview", "countrydecisionview", "countrydeploymentview",
           "countrydiplomacyview", "countryintelligenceagencyview", "countrylogisticsview", "countryoccupationview",
           "countryofficercorpview", "countryproductionlineview", "countrytechnologyview", "countrytradeview",
           "countryfactionview", "faction_setup_window", "faction_ping_window", "countryinternationalmarketview",
           "countrypoliticsview", "nationalfocusview"}
REVIEWED = {
    "console_wnd": "the debug console (core.gui), opened by hand",
    "ai_trace_window": "a debug window (the ai_trace console command)",
    "browser_window": "the game's web browser pop-up (Paradox account pages), opened and closed by the player",
    "career_profile_ribbon_picker": "the main menu's career profile: no top bar there",
    "faction_button_container": "factions/topbarfactionbutton.gui: the game docks it into its top bar; the Deco UI's "
                                "faction button is topbar.gui's, in the crown row, and nothing of this one has shown",
    "output_window": "special projects' facility output pop-up: its picture starts 35 px down (y 195), clear of the "
                     "medallion",
    "quick_wing_deploy_plane_type_entry_item": "an entry the game places inside the air wing deployment list",
    "ships_compact_drag_drop": "a ship entry the game draws at the cursor while it is dragged",
    "combat_log_combat_tab": "a tab of the combat log, a full-screen page (combat_log_page at 0, 0) the game draws over "
                             "everything, the top bar included",
    "combat_log_equipment_tab": "a tab of the combat log (as combat_log_combat_tab)",
    "combat_log_template_tab": "a tab of the combat log (as combat_log_combat_tab)",
    "countrydoctrineview": "the old doctrine screen, kept by the game for its names (its comments: 'Dummy for legacy "
                           "reasons'); the doctrine screen in use is doctrines_view.gui's country_doctrine_view",
    "faction_countries_window": "(assumed) rests behind the faction setup panel (x -356 to 144), as in the game, which "
                                "moves it out when it opens it: check in game that nothing shows in the panel's notch",
    "invite_countries_window": "(assumed) as faction_countries_window",
    "valsora_deco_country_name_window": "the medallion's own country name (make_topbar.py)",
    "valsora_deco_country_name_small_window": "the medallion's own country name, the smaller cut (make_topbar.py)",
}


def _top_windows(text):
    """(name, own attribute text) of each top-level container window (directly inside guiTypes)"""
    text = re.sub(r"#[^\n]*", "", text)
    out, depth, starts = [], 0, []
    for m in re.finditer(r"(?i)(containerWindowType|windowType)\s*=\s*\{|[{}]", text):
        tok = m.group(0)
        if m.group(1):
            if depth == 1:
                starts.append(m.end())
            depth += 1
        elif tok == "{":
            depth += 1
        else:
            depth -= 1
    for s in starts:
        # the window's own attributes: its text with every nested block taken out
        d, j, own = 1, s, []
        while j < len(text) and d > 0:
            c = text[j]
            if c == "{":
                d += 1
            elif c == "}":
                d -= 1
            elif d == 1:
                own.append(c)
            j += 1
        own = "".join(own)
        body = text[s:j]
        nm = re.search(r'\bname\s*=\s*"?([\w.-]+)', own)
        if nm:
            out.append((nm.group(1), own, body))
    return out


def _own_pos(body, key):
    """a position block written on the window itself (its first level), not a child's"""
    d, chunk = 0, []
    for c in body:
        if c == "{":
            d += 1
        if d <= 1:
            chunk.append(c)
        if c == "}":
            d -= 1
    flat = "".join(chunk)
    m = re.search(r"(?<![\w_])" + key + r"\s*=\s*\{\s*x\s*=\s*(-?[\d.]+)\s*y\s*=\s*(-?[\d.]+)\s*\}", flat)
    return (float(m.group(1)), float(m.group(2))) if m else None


def _own_size(body):
    d, chunk = 0, []
    for c in body:
        if c == "{":
            d += 1
        if d <= 1:
            chunk.append(c)
        if c == "}":
            d -= 1
    flat = "".join(chunk)
    m = re.search(r"(?<![\w_])size\s*=\s*\{\s*(?:width|x)\s*=\s*(-?[\d.]+%*)\s*(?:height|y)\s*=\s*(-?[\d.]+%*)\s*\}", flat)
    if not m:
        return None, None
    def num(v):
        return None if "%" in v or v.startswith("-") else float(v)
    return num(m.group(1)), num(m.group(2))


def windows():
    """every top-level window the game reads: (file, name, shown x, y, width, height, from the mod?, its text)"""
    files = {}
    for root, mod in ((VANILLA, False), (MOD, True)):
        for p in glob.glob(root + "interface/**/*.gui", recursive=True):
            rel = os.path.relpath(p, root + "interface").replace(os.sep, "/")
            files[rel] = (p, mod)
    for rel, (p, mod) in sorted(files.items()):
        text = open(p, encoding="utf-8-sig", errors="replace").read()
        for name, own, body in _top_windows(text):
            ori = re.search(r"(?i)\borientation\s*=\s*\"?(\w+)", own)
            if ori and ori.group(1).lower() != "upper_left":
                continue
            pos = _own_pos(body, "show_position") or _own_pos(body, "position") or (0.0, 0.0)
            w, h = _own_size(body)
            yield rel, name, pos[0], pos[1], w, h, mod, body


def problems():
    out, seen = [], []
    for rel, name, x, y, w, h, mod, body in windows():
        if not (Y0 <= y < Y1 and x < X1 and (w is None or x + w > X0)):
            if name in MOVED and mod and y < Y1:
                out.append(f"{rel}: {name} is listed as moved below the medallion but shows at y {y:g}")
            continue
        seen.append(name)
        if name in MOVED:
            out.append(f"{rel}: {name} shows at ({x:g}, {y:g}), under the medallion (it should be below y {Y1})")
        elif name in NOTCHED:
            if not mod or not any(mk in body for mk in NOTCH_MARKS):
                out.append(f"{rel}: {name} shows at ({x:g}, {y:g}) without the medallion's notch")
        elif name not in REVIEWED:
            out.append(f"{rel}: {name} shows at ({x:g}, {y:g}), where the medallion hangs: move it below y {Y1} "
                       f"(make_mapviews.py), notch it, or list it in medallion_check.REVIEWED with the reason")
    return out, seen


def selftest(quiet=False):
    """the check must catch the navy panel put back where the game has it, a notched panel without its notch and a new
    view in the corner"""
    global windows
    real = windows
    cases = []

    def fake(edit):
        def gen():
            for row in real():
                yield edit(row)
        return gen

    def navy_back(row):
        rel, name, x, y, w, h, mod, body = row
        return (rel, name, x, 82.0, w, h, mod, body) if name == "naviesview_window" else row

    def no_notch(row):
        rel, name, x, y, w, h, mod, body = row
        if name == "countrylogisticsview":
            body = body.replace("GFX_valsora_deco_panel_head_", "GFX_x_")
        return (rel, name, x, y, w, h, mod, body)

    def new_view(row):
        rel, name, x, y, w, h, mod, body = row
        return (rel, "some_new_view", 0.0, 90.0, 300.0, 400.0, False, "") if name == "naviesview_window" else row

    ok = True
    for label, edit, expect in (("navy back at y 82", navy_back, "naviesview_window shows at"),
                                ("logistics without its notch", no_notch, "countrylogisticsview shows at"),
                                ("a new view in the corner", new_view, "some_new_view shows at")):
        windows = fake(edit)
        found = [p for p in problems()[0] if expect in p]
        if not quiet:
            print(f"  {label}: {'caught' if found else 'MISSED'}")
        ok &= bool(found)
    windows = real
    return ok


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(0 if selftest() else 1)
    probs, seen = problems()
    print(f"windows in the medallion's corner: {len(seen)} ({', '.join(sorted(seen))})")
    for p in probs:
        print("PROBLEM:", p)
    print("PROBLEMS:", "none" if not probs else len(probs))
