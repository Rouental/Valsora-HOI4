"""Writes docs/tech_tree_mockup/tree.json: Valsora's 2036 tech tree as data (a mockup, not part of the mod).

    python3 docs/tech_tree_mockup/src/make_tree.py

The tree itself is written by hand in data_*.py. This script fills in the base game's facts for every technology
that renames one of the game's (its name, year, prerequisites and what it unlocks, read from the author's copy of
the game, HOI4_FILES, default /home/user/hoi4-files/HOI4 Files), checks the tree (ids, prerequisites, places, the
game's ids against source/vanilla/index/), and writes the result. Without the game's files the facts are taken from
the tree.json already written.
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "tree.json")
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
GAME = os.environ.get("HOI4_FILES", "/home/user/hoi4-files/HOI4 Files")
sys.path.insert(0, HERE)

import common  # noqa: E402
from common import ERAS, TIERS, RANK, era_of, start_of  # noqa: E402
import data_land, data_sea, data_air, data_tech, data_projects, data_doctrines, data_classic  # noqa: E402,F401

TAB_ORDER = ["infantry", "support", "artillery", "armour", "naval", "naval_support", "air", "electronics",
             "industry", "projects", "doc_land", "doc_naval", "doc_air", "doc_sf", "armour_classic",
             "naval_classic", "air_classic"]

# notes on renamed technologies whose game mechanics the design changes
NOTES = {
    "infantry_weapons": "Its infantry battalion moves to Battle Rifles (1965), so the feudal tier can raise infantry.",
    "tech_trucks": "Dated 1965 (not 2025 like the game's other pre-1936 technologies): every nation has trucks.",
    "gw_artillery": "Dated 1965: every nation has towed guns.",
    "basic_train": "Dated 1965: every nation has railways.",
    "tech_support": "Dated 1965: every nation has support equipment.",
    "electronic_mechanical_engineering": "Dated 1965: the root of electronics.",
    "early_bombs": "Dated 1965: the root of the bombs line.",
    "engines_1": "Dated 1965: every air force flies jets.",
}

# ----- the base game's facts --------------------------------------------------------------------------------------

def load_index(name):
    p = os.path.join(REPO, "source", "vanilla", "index", name)
    return {ln.strip() for ln in open(p, encoding="utf-8") if ln.strip() and not ln.startswith("#")}


def read_game():
    """The game's technologies, doctrines and projects, or None without the game's files."""
    if not os.path.isdir(GAME):
        return None
    sys.path.insert(0, os.path.join(REPO, "scripts"))
    import pdxscript as P
    import glob
    loc = {}
    for f in glob.glob(os.path.join(GAME, "localisation", "english", "*.yml")):
        for line in open(f, encoding="utf-8-sig", errors="replace"):
            m = re.match(r'\s*([\w\.\-]+):\d*\s*"(.*)"\s*$', line)
            if m:
                loc[m.group(1)] = m.group(2)

    def text(key):
        s = loc.get(key, "")
        for _ in range(3):
            s = re.sub(r"\$(\w+)\$", lambda m: loc.get(m.group(1), m.group(1)), s)
        return re.sub(r"§.|§!", "", s)

    STRUCT = {"path", "folder", "categories", "ai_will_do", "research_cost", "start_year", "enable_equipments",
              "enable_subunits", "enable_equipment_modules", "allow", "allow_branch", "XOR", "show_equipment_icon",
              "desc", "on_research_complete", "special_project_specialization", "is_special_project_tech",
              "sub_technologies", "sub_tech_index", "dependencies", "xp_research_type", "xp_boost_cost",
              "xp_research_bonus", "doctrine", "show_effect_as_desc", "enable_building", "dlc_unlock"}

    def fmt(v):
        try:
            x = float(v)
        except (TypeError, ValueError):
            return str(v)
        if abs(x) < 1 and x != 0:
            return f"{x * 100:+.0f}%"
        return f"{x:+g}"

    techs = {}
    for f in sorted(glob.glob(os.path.join(GAME, "common", "technologies", "*.txt"))):
        txt = open(f, encoding="utf-8-sig").read()
        for k, _, v in P.parse(txt):
            if k != "technologies":
                continue
            for tid, _, body in v:
                if tid is None or not isinstance(body, list):
                    continue
                t = {"file": os.path.basename(f), "folders": [], "leads": [], "xor": [], "eq": [], "units": [],
                     "mods": [], "effects": [], "buildings": [], "dlc": None, "year": None, "cost": None}
                for kk, _, vv in body:
                    if kk == "folder":
                        t["folders"].append(dict((a, b) for a, _, b in vv).get("name"))
                    elif kk == "path":
                        t["leads"].append(dict((a, b) for a, _, b in vv).get("leads_to_tech"))
                    elif kk == "XOR":
                        t["xor"] = [b for a, _, b in vv if a is None]
                    elif kk == "enable_equipments":
                        t["eq"] = [b for a, _, b in vv if a is None]
                    elif kk == "enable_subunits":
                        t["units"] = [b for a, _, b in vv if a is None]
                    elif kk == "enable_equipment_modules":
                        t["mods"] = [b for a, _, b in vv if a is None]
                    elif kk == "enable_building":
                        t["buildings"].append(dict((a, b) for a, _, b in vv).get("building"))
                    elif kk == "start_year":
                        t["year"] = int(vv)
                    elif kk == "research_cost":
                        t["cost"] = float(vv)
                    elif kk in ("allow", "allow_branch"):
                        d = re.findall(r"'has_dlc', '=', '([^']+)'", str(vv))
                        sp = re.findall(r"'is_special_project_completed', '=', '([^']+)'", str(vv))
                        neg = "'NOT'" in str(vv)
                        t["dlc"] = ("not " if neg else "") + ", ".join(d) if d else (
                            "special project " + ", ".join(s.replace("sp:", "") for s in sp) if sp else None)
                    elif kk in STRUCT:
                        continue
                    elif isinstance(vv, list):
                        stats = [(a, b) for a, _, b in vv if a and not isinstance(b, list)]
                        if stats:
                            who = kk.replace("category_", "").replace("_", " ")
                            t["effects"].append(who + ": " + ", ".join(
                                f"{a.replace('_', ' ')} {fmt(b)}" for a, b in stats[:4]))
                    else:
                        t["effects"].append(f"{kk.replace('_', ' ')} {fmt(vv)}")
                t["name"] = text(tid) or (text(t["eq"][0]) if t["eq"] else "") or (
                    text(t["eq"][0] + "_short") if t["eq"] else "")
                techs[tid] = t
    parents = defaultdict(list)
    for tid, t in techs.items():
        for c in t["leads"]:
            if c:
                parents[c].append(tid)
    for tid, t in techs.items():
        t["requires"] = sorted(parents.get(tid, []))

    # doctrines: names
    doc = {}
    for f in glob.glob(os.path.join(GAME, "common", "doctrines", "*", "*.txt")) + \
            glob.glob(os.path.join(GAME, "common", "doctrines", "*", "*", "*.txt")):
        for k, _, v in P.parse(open(f, encoding="utf-8-sig").read()):
            if isinstance(v, list):
                d = {a: b for a, _, b in v if a}
                if "name" in d:
                    doc[k] = text(d["name"])
    for k in ("infantry", "combat_support", "armor", "operations", "capital_ships", "carriers", "screens",
              "submarines", "fighter_aircraft", "strike_aircraft", "medium_aircraft", "heavy_aircraft"):
        doc["track:" + k] = text("DOCTRINE_TRACK_" + k.upper())

    # projects: complexity, prototype time, specialisation, name
    proj = {}
    for f in glob.glob(os.path.join(GAME, "common", "special_projects", "projects", "*.txt")):
        for k, _, v in P.parse(open(f, encoding="utf-8-sig").read()):
            if isinstance(v, list):
                d = {a: b for a, _, b in v if a}
                proj[k] = {"name": text(k), "complexity": str(d.get("complexity", "")).replace("sp_complexity.", ""),
                           "prototype": str(d.get("prototype_time", "")).replace("sp_time.prototype.", ""),
                           "specialization": d.get("specialization")}
    return {"techs": techs, "doctrines": doc, "projects": proj}


# ----- unlocks in game terms ----------------------------------------------------------------------------------------
UNIT_NAMES = {
    "infantry": "Infantry Battalion", "fire_support": "Heavy Weapons Battalion",
    "mot_fire_support": "Motorised Heavy Weapons Battalion", "hq_motorized": "motorised support",
    "motorized": "Motorised Infantry", "mechanized": "Mechanised Infantry", "armored_car": "Armoured Car Squadron",
    "amphibious_mechanized": "Amphibious Mechanised Infantry", "marine": "Marines", "mountaineers": "Mountain Troops",
    "hq_paratrooper": "Airborne (paratrooper) support", "ranger_battalion": "Rangers",
    "hq_engineer": "Combat Engineer Company", "hq_recon": "Reconnaissance Company",
    "hq_military_police": "Military Police Company", "hq_maintenance": "Maintenance Company",
    "hq_field_hospital": "Field Hospital", "hq_logistics": "Logistics Company",
    "hq_signal": "Signals and Electronic Warfare Company", "armored_engineer": "Armoured Engineer Company",
    "helicopter_recon": "Air Cavalry Troop", "motorized_military_police": "Motorised Military Police",
    "armored_maintenance": "Armoured Recovery Company", "helicopter_field_hospital": "Air Ambulance Company",
    "helicopter_transport": "Tiltrotor Lift Company", "armored_signal": "Armoured Command Post",
    "field_guns": "Artillery Battalion", "anti_air_battery": "Air Defence Battery",
    "anti_tank_battery": "Anti-Tank Missile Battery", "rocket_battery": "Rocket Artillery Battalion",
    "light_armor": "Light Tank Battalion", "medium_armor": "Main Battle Tank Battalion",
    "heavy_armor": "Heavy Assault Tank Battalion", "super_heavy_armor": "Siege Tank Battalion",
    "modern_armor": "Next-Generation Tank Battalion", "amphibious_armor": "Amphibious Tank Battalion",
}

EQ_FAMILIES = [
    (r"^infantry_equipment_\d$", "infantry kit"), (r"^support_equipment_\d$", "support equipment"),
    (r"^motorized_equipment_\d$", "trucks and protected vehicles"), (r"^mechanized_equipment_\d$", "IFV"),
    (r"^amphibious_mechanized_equipment_\d$", "amphibious combat vehicle"),
    (r"^(gw_)?armored_car_equipment(_\d)?$", "armoured car"), (r"^artillery_equipment_\d$", "howitzer"),
    (r"^anti_air_equipment_\d$", "air defence system"), (r"^anti_tank_equipment_\d$", "anti-tank missile system"),
    (r"^rocket_artillery_equipment_\d$", "rocket launcher"), (r"^train_equipment_\d$", "locomotive"),
    (r"^railway_gun_equipment_\d$", "rail-mobile launcher"), (r"^motorbike_equipment_\d$", "light utility vehicle"),
    (r"^(light|medium|heavy|super_heavy|modern)_tank_(destroyer_|artillery_|aa_|amphibious_)?chassis_\d$",
     "tank designer chassis"), (r"^amphibious_tank_chassis_\d$", "amphibious chassis"),
    (r"^(gw|light|medium|heavy|super_heavy|modern|amphibious)_tank_(equipment|destroyer|artillery)", "tank"),
    (r"^ship_hull_carrier_conversion_(bb|ca)$", "carrier conversion"), (r"^ship_hull_\w+_\d$", "ship hull"),
    (r"^(destroyer|light_cruiser|heavy_cruiser|battle_cruiser|battleship|carrier|submarine)_\d$", "ship class"),
    (r"^SH_battleship_\d$", "ship class"),
    (r"^(cv_)?small_plane_\w*airframe_\d$", "small airframe"), (r"^medium_plane_\w*airframe_\d$", "medium airframe"),
    (r"^large_plane_\w*airframe_\d$", "large airframe"), (r"^transport_plane_equipment_\d$", "airlifter"),
    (r"^(jet_)?(fighter|CAS|heavy_fighter|tac_bomber|nav_bomber|strat_bomber|scout_plane|jet_fighter|"
     r"jet_tac_bomber|jet_strat_bomber)_equipment_\d$", "aircraft"),
    (r"^floating_harbor_equipment_\d$", "floating harbour"), (r"^(support|repair)_ship_\d$", "support ship"),
    (r"^rocket_interceptor_equipment_\d$", "interceptor missile"), (r"_aa_equipment_\d$", "air defence vehicle"),
    (r"^cv_\w+_equipment_\d$", "carrier aircraft"),
]

MOD_FAMILIES = [
    (r"^ship_torpedo_sub_\d", "submarine torpedo tubes"), (r"^ship_torpedo_\d", "anti-ship missile launcher"),
    (r"^ship_(light|light_medium)_battery_\d", "medium gun mount"), (r"^ship_medium_battery_\d", "heavy gun mount"),
    (r"^ship_(heavy|super_heavy)_battery_\d", "heavy turret"), (r"^(dp_)?ship_secondaries", "secondary guns"),
    (r"^dp_", "air defence missile cells"), (r"^ship_anti_air_\d", "close-in weapon system"),
    (r"^ship_radar_\d", "ship radar"), (r"^ship_sonar_\d", "sonar"), (r"^ship_depth_charge_\d", "ASW weapons"),
    (r"^ship_fire_control_system_\d", "combat system"), (r"^ship_armor_", "ship protection"),
    (r"^(light|cruiser|heavy|carrier|sub)_ship_engine_\d|^ship_engine_", "ship propulsion"),
    (r"^ship_(airplane_launcher|seaplane_tender)", "helicopter deck"), (r"^ship_deck_space", "flight deck"),
    (r"^ship_sub_snorkel", "masts and snorkel"), (r"^ship_mine", "mine rails"),
    (r"^tank_(light|medium|heavy|super_heavy|modern)_\w*turret", "turret"), (r"suspension$", "suspension"),
    (r"^tank_\w*engine", "power pack"), (r"armor$|^sloped_armor|armor_skirts", "armour"),
    (r"^tank_radio|^lc_radio", "battle management system"), (r"^tank_\w*(cannon|howitzer|gun)", "main gun"),
    (r"^tank_rocket_launcher|^rocket_rails|^lc_rocket", "rocket pods"), (r"^tank_heavy_machine_gun|machine_gun",
                                                                        "machine gun"),
    (r"^lc_", "Assault Mech module"), (r"^engine_\d", "jet engine"), (r"bomb", "bombs and racks"),
    (r"mg_|cannon", "air-to-air weapons"), (r"^torpedo_mounting", "anti-ship missile pylon"),
    (r"radar", "aircraft radar"), (r"fuel_tank|drop_tanks", "fuel tanks"), (r"armor_plate|self_sealing", "survivability"),
    (r"recon_camera", "reconnaissance pod"), (r"non_strategic|floats|flying_boat|dive_brakes", "airframe options"),
    (r"radio_navigation", "navigation"), (r"rocket_engine", "rocket motor"), (r"guided_anti_ship", "guided missile"),
    (r"stabilizer", "stabiliser"), (r"ammo_storage", "ammunition stowage"), (r"smoke_launchers", "smoke and decoy launchers"),
    (r"advanced_flamethrower", "thermobaric launcher"), (r"amphibious_drive", "amphibious drive"),
    (r"auto_loader", "autoloader"), (r"demining_coil", "mine countermeasures"), (r"dozer_blade", "dozer blade"),
    (r"easy_maintenance", "predictive maintenance"), (r"airdropped_mines", "air-dropped mines"),
    (r"secondary_turret", "remote weapon station"), (r"squeezebore", "sabot adaptor"),
    (r"tank_buster", "anti-tank missile rails"), (r"jet_engine", "jet engine"),
]


def family(x, table):
    for pat, label in table:
        if re.search(pat, x):
            return label
    return x


def vanilla_unlocks(vt):
    out = []
    groups = defaultdict(list)
    for e in vt.get("eq", []):
        groups[family(e, EQ_FAMILIES)].append(e)
    for fam, ids in groups.items():
        more = f" and {len(ids) - 1} versions" if len(ids) > 1 else ""
        out.append(f"equipment ({fam}): {ids[0]}{more}")
    for u in vt.get("units", []):
        out.append(f"unit: {UNIT_NAMES.get(u, u)} ({u})")
    if vt.get("mods"):
        fams = Counter(family(m, MOD_FAMILIES) for m in vt["mods"])
        out.append(f"designer modules ({len(vt['mods'])}): " + ", ".join(fams))
    for b in vt.get("buildings", []):
        if b:
            out.append(f"building: {b}")
    for e in vt.get("effects", [])[:4]:
        out.append(e)
    return out


# ----- build --------------------------------------------------------------------------------------------------------

def main():
    game = read_game()
    old = None
    if os.path.exists(OUT):
        old = json.load(open(OUT, encoding="utf-8"))
    old_v = {}
    if old:
        for t in old["techs"]:
            if t.get("vanilla"):
                old_v[t["id"]] = t["vanilla"]
    vtech = game["techs"] if game else {}
    vindex = load_index("technologies.txt")
    problems = []

    by_id = {}
    for t in common.TECHS:
        if t["id"] in by_id:
            problems.append(f"duplicate id {t['id']}")
        by_id[t["id"]] = t

    # classic mirrors take name, description and icon from their designer counterpart
    for t in common.TECHS:
        same = t.get("same")
        if same:
            s = by_id.get(same)
            if not s:
                problems.append(f"{t['id']}: same={same} unknown")
                continue
            t["name"] = t["name"] or s["name"]
            t["desc"] = t["desc"] or s["desc"]
            t["icon"] = t["icon"] or s["icon"]

    # default prerequisites: the previous technology in the same lane
    lanes = defaultdict(list)
    for t in common.TECHS:
        lanes[(t["folder"], t["lane"])].append(t)
    for key, ts in lanes.items():
        ts.sort(key=lambda t: t["year"])
        for i, t in enumerate(ts):
            if t["req"] is None:
                t["req"] = [ts[i - 1]["id"]] if i else []
    # places
    seen = {}
    for t in common.TECHS:
        k = (t["folder"], t["lane"], t["year"])
        if k in seen and t["folder"] != "projects":
            problems.append(f"{t['id']} and {seen[k]} share lane {t['lane']} in {t['year']} ({t['folder']})")
        seen[k] = t["id"]

    for t in common.TECHS:
        for r in t["req"] + t["excl"]:
            if r not in by_id:
                problems.append(f"{t['id']}: prerequisite {r} unknown")
        rep = t["replaces"]
        t["era"] = era_of(t["year"])
        if t["start"] == "auto":
            t["start"] = start_of(t["year"]) if t["folder"] != "projects" else None
        if rep != "new" and t["folder"] != "projects":
            if rep not in vindex:
                problems.append(f"{t['id']}: replaces {rep}, not a technology of the game")
            v = vtech.get(rep)
            if v:
                t["vanilla"] = {"id": rep, "name": v["name"], "year": v["year"], "file": v["file"],
                                "folders": v["folders"], "requires": v["requires"], "leads": [x for x in v["leads"] if x],
                                "xor": v["xor"], "dlc": v["dlc"], "cost": v["cost"],
                                "unlocks": vanilla_unlocks(v)}
                for a in t["also"]:
                    va = vtech.get(a)
                    if va:
                        t["vanilla"].setdefault("also", []).append({"id": a, "name": va["name"], "dlc": va["dlc"]})
            elif rep in old_v:
                t["vanilla"] = old_v[rep] if old_v[rep]["id"] == rep else old_v.get(t["id"])
        unl = list(t.get("vanilla", {}).get("unlocks", [])) if t.get("vanilla") else []
        t["unlocks"] = unl + t["unl"]
        if t["size"] is None:
            v = t.get("vanilla") or {}
            big = any(u.startswith(("equipment", "unit:")) for u in v.get("unlocks", [])) or any(
                re.search(r"new (equipment|hull|airframe|support company|chassis|battalion)|^unit:", u) for u in t["unl"])
            t["size"] = "big" if big else "small"
        if t["id"] in NOTES:
            t["note"] = ((t.get("note") or "") + " " + NOTES[t["id"]]).strip()
        if not t["desc"]:
            problems.append(f"{t['id']}: no description")
        if not t["name"]:
            problems.append(f"{t['id']}: no name")

    # projects: the game's complexity beside the proposed one
    if game:
        for t in common.TECHS:
            if t["folder"] == "projects" and t["replaces"] != "new":
                p = game["projects"].get(t["replaces"])
                if not p:
                    problems.append(f"{t['id']}: not a special project of the game")
                    continue
                t["vanilla"] = {"id": t["replaces"], "name": p["name"], "complexity": p["complexity"],
                                "prototype": p["prototype"], "specialization": p["specialization"], "unlocks": []}
    elif old:
        for t in common.TECHS:
            if t["folder"] == "projects" and t["id"] in old_v:
                t["vanilla"] = old_v[t["id"]]

    # every technology of the game's folders is accounted for
    if game:
        covered = set()
        for t in common.TECHS:
            if t["replaces"] != "new":
                covered.add(t["replaces"])
            covered.update(t["also"])
        variants = {f.key for f in common.FOLDERS if f.variant_of}
        dup = Counter(t["replaces"] for t in common.TECHS
                      if t["replaces"] != "new" and t["folder"] != "projects" and t["folder"] not in variants)
        for k, n in dup.items():
            if n > 1:
                problems.append(f"{k} is renamed twice")
        wanted = {f.game for f in common.FOLDERS if f.kind == "tree"}
        for tid, v in vtech.items():
            if any(fo in wanted for fo in v["folders"]) and tid not in covered:
                problems.append(f"the game's {tid} ({', '.join(v['folders'])}) is not in the tree")
        allp = set(game["projects"])
        missing = allp - {t["replaces"] for t in common.TECHS if t["folder"] == "projects"}
        for m in sorted(missing):
            problems.append(f"the game's project {m} is not in the tree")

    # doctrines
    docs = []
    for f in data_doctrines.DOCTRINES:
        for g in f.extra["grands"]:
            if game:
                g["vanilla_name"] = game["doctrines"].get(g["id"], "")
        for tr in f.extra["tracks"]:
            if game:
                tr["vanilla_name"] = game["doctrines"].get("track:" + tr["id"], "")
            for s in tr["subs"]:
                if game and s["replaces"] != "new":
                    s["vanilla_name"] = game["doctrines"].get(s["id"], "")
                    if s["id"] not in game["doctrines"]:
                        problems.append(f"subdoctrine {s['id']} unknown")
        docs.append(f.key)
    if old and not game:
        olddoc = {f["key"]: f for f in old["folders"]}
        for f in data_doctrines.DOCTRINES:
            of = olddoc.get(f.key)
            if of:
                f.extra = of["extra"]

    # folders
    folders = []
    order = {k: i for i, k in enumerate(TAB_ORDER)}
    for f in sorted(common.FOLDERS, key=lambda f: order[f.key]):
        ts = [t for t in common.TECHS if t["folder"] == f.key]
        years = sorted({t["year"] for t in ts})
        nl = max([t["lane"] for t in ts], default=-1) + 1
        folders.append({"key": f.key, "name": f.name, "game": f.game, "orient": f.orient, "icon": f.icon,
                        "ledger": f.ledger, "blurb": f.blurb, "dlc": f.dlc, "variant_of": f.variant_of,
                        "kind": f.kind, "sections": f.sections, "years": years, "lanes": nl, "extra": f.extra})

    keep = ("id", "name", "year", "era", "folder", "section", "lane", "size", "icon", "req", "excl", "replaces",
            "start", "desc", "unlocks", "dlc", "note", "vanilla", "cost", "same", "spec", "line", "complexity",
            "tags", "also")
    techs = [{k: t[k] for k in keep if t.get(k) not in (None, [], "")} | {"start": t["start"]}
             for t in common.TECHS]

    # counts
    counts = {"folders": {}, "eras": Counter(), "new": 0, "renamed": 0}
    for t in techs:
        c = counts["folders"].setdefault(t["folder"], {"total": 0, "new": 0, "renamed": 0, "eras": Counter(),
                                                        "start": Counter()})
        c["total"] += 1
        c["new" if t["replaces"] == "new" else "renamed"] += 1
        c["eras"][t["era"]] += 1
        c["start"][t["start"] or "none"] += 1
    for f in data_doctrines.DOCTRINES:
        subs = [s for tr in f.extra["tracks"] for s in tr["subs"]]
        counts["folders"][f.key] = {"grands": len(f.extra["grands"]), "tracks": len(f.extra["tracks"]),
                                    "subs": len(subs), "new": sum(s["replaces"] == "new" for s in subs),
                                    "renamed": sum(s["replaces"] != "new" for s in subs)}

    tree = {
        "meta": {
            "title": "Valsora's 2036 tech tree: a mockup",
            "made": "2026-10-17",
            "status": "A mockup for the author to react to. Not in the mod.",
            "anchor": "The base game's 1936 is Valsora's 2036.",
            "eras": [{"key": k, "name": n, "from": a, "to": b, "desc": d} for k, n, a, b, d in ERAS],
            "tiers": [{"key": k, "name": n, "rank": r, "desc": d} for k, n, r, d in TIERS],
            "superpowers": [{"tag": "KRI", "name": "Krionik", "ideology": "Monarchist"},
                            {"tag": "KPF", "name": "Kampfian Empire", "ideology": "Authoritarian"},
                            {"tag": "SRK", "name": "Sarkis", "ideology": "Communist"},
                            {"tag": "FRX", "name": "Fraxhemark", "ideology": "Democratic"}],
            "counts": counts,
        },
        "folders": folders,
        "techs": techs,
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(tree, fh, ensure_ascii=False, indent=1, sort_keys=False)
    tot = sum(1 for t in techs)
    new = sum(t["replaces"] == "new" for t in techs)
    print(f"{len(folders)} folders, {tot} technologies and projects ({new} new, {tot - new} renamed); "
          f"{'game files read' if game else 'game files absent: facts from the old tree.json'}")
    for f in folders:
        c = counts["folders"][f["key"]]
        print(f"  {f['key']:16s} {c}")
    if problems:
        print(f"{len(problems)} problems:")
        for p in problems:
            print("  -", p)
        sys.exit(1)


if __name__ == "__main__":
    main()
