"""By hand, after a game update: refresh source/vanilla/ from the author's copy of HOI4.

    python3 scripts/vanilla_sync.py [HOI4 folder]   # default $HOI4_DIR, then /home/user/hoi4-files/HOI4 Files

source/vanilla/files/ holds exact copies of the few vanilla files the mod ships changed
(vanilla_parts.py moves their dates to Valsora's 2036 and drops their Earth-only parts at
build time). source/vanilla/index/ holds lists of vanilla's names (tags, decisions,
sprites, technologies, ...) that the build and check_mod.py check our files against, so
neither needs the game's files. Only these are kept: Paradox's files are not copied
wholesale into this repository (CLAUDE.md, "Vanilla reference files").
"""
import glob
import json
import os
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from pdxscript import read, walk  # noqa: E402

OUT = Path("source/vanilla")

# vanilla files the mod ships changed (paths in the game folder)
FILES = (
    # 2036: the tech tree's year labels (every common/technologies file is added in main())
    ["interface/countrytechtreeview.gui",
       # generic content with date conditions, shifted to 2036
       "common/ideas/_economic.txt", "common/ideas/_manpower.txt",
       "common/national_focus/generic.txt", "common/ai_templates/generic.txt",
       "common/factions/goals/faction_goals_short_term.txt",
       "common/factions/goals/faction_goals_medium_term.txt",
       "common/factions/goals/faction_goals_long_term.txt",
       "common/special_projects/projects/land_projects.txt",
       "common/special_projects/projects/radar_projects.txt",
       "common/raids/air_raids.txt", "common/raids/air_raids_custom.txt",
       "common/raids/paratrooper_raids.txt", "common/raids/paratrooper_raids_custom.txt",
       "common/unit_medals/00_default.txt", "common/ribbons/00_ribbons.txt",
       "common/resistance_compliance_modifiers/compliance_modifiers.txt",
       # the game rule "war goals from focuses only, until 1938 / 1939 / 1940" (2038 ... in Valsora)
       "common/scripted_triggers/diplomacy_scripted_triggers.txt",
       # the generic AI strategies (the folder stays switched off: these come back as ours)
       "common/ai_strategy/default.txt", "common/ai_strategy/doctrines.txt",
       "common/ai_strategy/generic_operation_strats.txt", "common/ai_strategy/operatives_default.txt",
       # the generic events the generic on_actions call (events stay switched off too)
       "events/ElectionEvents.txt", "events/AcePilots.txt", "events/WarJustification.txt",
       "events/NukeEvents.txt", "events/CapitulationEvents.txt", "events/LaR_agent_events.txt",
       "events/MTG_generic.txt",
       # events vanilla's generic content fires: joining factions, demands and the end of an ideological
       # civil war (Generic.txt, from 00_scripted_effects and the generic focus tree), collaboration
       # governments and resistance (compliance and resistance modifiers), an operation's outcome
       # (00_operations), the nuclear project (special projects)
       "events/Generic.txt", "events/LAR_occupation.txt", "events/LaR_espionage_operations.txt",
       "events/Special_Project_Events.txt",
       # the puppet: Authoritarian (fascism) overlords keep plain puppets in Valsora (vanilla_parts.EDITS)
       "common/autonomous_states/puppet.txt"])

# localisation files whose generic names carry years ("1936 Cruiser Hull", "1938 Medium", the game
# rule's "Focuses Only (Until 1938)")
YEAR_NAME_FILES = ("designer_l_english.yml", "research_l_english.yml", "tank_modules_l_english.yml",
                   "game_rules_l_english.yml")


# a country's definite name opening a sentence or a paragraph: "[Root.GetNameDef] has announced ..." gives "the
# Cardonian Kingdom has announced ..." with Valsora's names, which start with "the" (2026-10-17, the author's screenshot
# of a capitulation): such lines are shipped again with GetNameDefCap there
OPENING_NAME = re.compile(r'((?:^|\\n|(?<!§)[.!?] +)\s*(?:§[A-Za-z])?\[[A-Za-z.]+\.)GetNameDef\]')  # §! closes a colour
NAME_CAPS = Path("curated/localisation/english/replace/valsora_name_caps_l_english.yml")


def name_caps(V):
    """English lines of the game's with a country's definite name opening a sentence, as GetNameDefCap there: the
    lines for source/vanilla/curated/localisation/english/replace/ (the mod ships them over the game's)"""
    out = []
    for f in sorted((V / "localisation/english").glob("*.yml")):
        for line in f.read_text(encoding="utf-8-sig").splitlines():
            m = re.match(r'^\s*([\w.\-]+):(\d*)\s*"(.*)"\s*$', line)
            if m and OPENING_NAME.search(m[3]):
                out.append(f' {m[1]}:{m[2] or 0} "{OPENING_NAME.sub(lambda g: g[1] + "GetNameDefCap]", m[3])}"')
    return out


def vanilla_dir(argv):
    for d in (argv[1] if len(argv) > 1 else None, os.environ.get("HOI4_DIR"), "/home/user/hoi4-files/HOI4 Files"):
        if d and Path(d, "common").is_dir():
            return Path(d)
    raise SystemExit("no HOI4 folder: give its path, set HOI4_DIR, or clone Rouental/HOI4-Files")


def decisions(V):
    """name -> kind of every vanilla decision (decision, mission, targeted, state_targeted)"""
    kinds = {}
    for f in glob.glob(str(V / "common/decisions/*.txt")):
        for cat, _, body in read(f):
            if not isinstance(body, list):
                continue
            for name, _, d in body:
                if not (name and isinstance(d, list)):
                    continue
                keys = {k for k, _, _ in d}
                if "days_mission_timeout" in keys:
                    kinds[name] = "mission"
                elif "state_target" in keys:
                    kinds[name] = "state_targeted"
                elif keys & {"target_trigger", "targets", "target_array", "target_root_trigger"}:
                    kinds[name] = "targeted"
                else:
                    kinds[name] = "decision"
    return kinds


def referenced(V, names):
    """the names among `names` that files the game still loads refer to (the mod switches off
    common/decisions but not its categories, nor focus trees, ideas, scripted triggers ...)"""
    off = ("common/decisions/", "common/ai_strategy/", "common/ai_strategy_plans/", "common/on_actions/",
           "common/bookmarks/")
    found = set()
    for f in glob.glob(str(V / "common/**/*.txt"), recursive=True):
        rel = Path(f).relative_to(V).as_posix()
        if rel.startswith(off) and not rel.startswith("common/decisions/categories/"):
            continue
        for _, k, _, v in walk(read(f)):
            if isinstance(v, str) and v in names:
                found.add(v)
    return found


# the Gazetteer's trait groups (unit leader trait_type): how a player sees them
TRAIT_GROUPS = {"personality_trait": "Personality", "basic_trait": "Basic", None: "Basic", "basic_terrain_trait": "Terrain",
                "assignable_trait": "Learned", "assignable_terrain_trait": "Terrain, learned"}
ADVISOR_SLOTS = [("political_advisor", "Political advisor"), ("theorist", "Theorist"), ("army_chief", "Chief of army"),
                 ("navy_chief", "Chief of navy"), ("air_chief", "Chief of air force"), ("high_command", "High command")]


def loc_names(V):
    """English localisation: key -> text without the game's colour and icon codes"""
    out = {}
    for f in sorted(glob.glob(str(V / "localisation/english/**/*.yml"), recursive=True)):
        for line in Path(f).read_text(encoding="utf-8-sig", errors="replace").splitlines():
            m = re.match(r'^\s*([\w.\-]+):\d* "(.*)"', line)   # one key per line (indented or not: the game reads both)
            if m and m[1] not in out:
                out[m[1]] = re.sub(r"\s+", " ", re.sub(r"§.|£\w+|\[[^]]*\]|\\n", " ", m[2])).strip()
    return out


# what a trait does, as the game's tooltips say it (2026-10-18, the author: "When looking at the traits for leaders and
# such, you should be able to see the effects of the traits"): each modifier's name from its tooltip (`KEY_tt`, which
# also says whether it is a percentage) or its MODIFIER_ key, the skills by name, terrain and unit bonuses under the
# terrain's or unit's name; what isn't a number (who may have it, the AI's weights, xp) left out
SKILLS = {"attack_skill": "Attack", "defense_skill": "Defense", "planning_skill": "Planning", "logistics_skill": "Logistics",
          "maneuvering_skill": "Maneuvering", "coordination_skill": "Coordination", "skill": "Skill"}
STATS = {"attack": "Attack", "defence": "Defense", "defense": "Defense", "movement": "Movement", "breakthrough": "Breakthrough",
         "soft_attack": "Soft attack", "hard_attack": "Hard attack", "max_organisation": "Organization",
         "max_strength": "Strength", "dig_in_speed_factor": "Entrenchment speed"}
MODIFIER_BLOCKS = ("modifier", "non_shared_modifier", "corps_commander_modifier", "field_marshal_modifier")
NOT_EFFECTS = {"type", "trait_type", "gui_row", "gui_column", "new_commander_weight", "allowed", "ai_will_do", "gain_xp",
               "gain_xp_leader", "gain_xp_on_spotting", "trait_xp_factor", "show_in_combat", "prerequisites",
               "mutually_exclusive", "parent", "any_parent", "all_parents", "num_parents_needed", "slot", "cost", "sprite",
               "random", "specialist_advanced", "enable_ability", "ai_strategy", "name", "visible", "available",
               "custom_prerequisite_tooltip", "on_add", "on_remove", "daily_effect", "unit_type", "override_effect_tooltip",
               "command_power"}  # an advisor's command power cost, 0 in every trait


def percent(k, v, fmt=None):
    """whether the game shows a modifier as a percentage: its tooltip says so where it has one; otherwise the game's
    habit, factors and multipliers and fractions are, flat amounts (`_flat`, a daily `_gain`, daily experience, whole
    numbers such as skills or caps) are not"""
    if k.endswith("_flat"):
        return False
    if fmt is not None:
        return "%" in fmt
    if k.endswith(("_factor", "_mult", "_chance")):
        return True
    if k.endswith(("_flat", "_gain", "_increase", "_cap")) or k.startswith("experience_gain") or k in SKILLS:
        return False
    try:
        return abs(float(v)) < 1
    except (TypeError, ValueError):
        return False


def trait_effects(V, loc, bodies, consts=None):
    """{trait: [effect, ...]} for the traits in `bodies` ({trait: its block}); `consts`, the files' @constants"""
    consts = consts or {}
    abilities = {}  # ability -> its name's key
    for f in sorted(glob.glob(str(V / "common/abilities/*.txt"))):
        for top, _, body in read(f):
            if top == "ability" and isinstance(body, list):
                for k, _, v in body:
                    if isinstance(v, list):
                        abilities[k] = next((x for kk, _, x in v if kk == "name" and isinstance(x, str)), "")
    def text(k):
        t = loc.get(k)
        for _ in range(3):  # $KEY$ inside a text: that key's text
            if not t or "$" not in t:
                break
            t = re.sub(r"\$(\w+)\$", lambda m: loc.get(m[1], ""), t)
        return re.sub(r"\s+", " ", re.sub(r"\$[^$]*\$|£", "", t or "")).strip(" :") or None

    def label(k, v=None):
        tt = loc.get(k + "_tt") or ""
        m = re.search(r"\$(\w+)\$\s*:\s*\$RIGHT\|([^$]*)\$", tt)
        name = text(m[1]) if m else None
        for c in (f"MODIFIER_{k.upper()}", f"modifier_{k}", f"MODIFIERS_{k.upper()}", k.upper(), k):
            name = name or text(c)
        return name or k.replace("_", " ").removesuffix(" factor").capitalize(), percent(k, v, m[2] if m else None)

    def num(v, pct):
        try:
            x = float(consts.get(v, v)) * (100 if pct else 1)
        except ValueError:
            return None
        if x == 0:
            return None
        x = round(x, 1 if pct else 3)
        s = f"{x:g}"
        return ("+" if x > 0 else "\u2212") + s.lstrip("-") + ("%" if pct else "")

    def mods(block, under=None):
        out = []
        for k, _, v in block:
            if k is None or k in NOT_EFFECTS:
                continue
            if isinstance(v, list):  # a terrain's or a unit's own bonuses
                inner = [f"{STATS.get(kk) or label(kk)[0]} {num(vv, True if kk in STATS else label(kk, vv)[1])}"
                         for kk, _, vv in v if isinstance(vv, str) and num(vv, True) is not None]
                if inner:
                    out.append(f"{text(k) or k.replace('_', ' ').capitalize()}: " + ", ".join(inner))
                continue
            if k in ("custom_modifier_tooltip", "custom_effect_tooltip"):
                if text(v):
                    out.append(text(v))
                continue
            name, pct = label(k, consts.get(v, v))
            val = num(v, pct)
            if val is not None:
                out.append(f"{name}: {val}")
        return out

    eff = {}
    for t, body in bodies.items():
        out = []
        for k, _, v in body:
            if k in SKILLS and isinstance(v, str):
                if num(v, False):
                    out.append(f"{SKILLS[k]}: {num(v, False)}")
            elif k and k.endswith("_skill_factor") and k[:-7] in SKILLS and isinstance(v, str):
                out.append(f"{SKILLS[k[:-7]]} gained on promotion: {num(v, True)}")
            elif k in MODIFIER_BLOCKS and isinstance(v, list):
                out += mods(v)
            elif k == "sub_unit_modifiers" and isinstance(v, list):
                out += mods(v)
            elif k == "equipment_bonus" and isinstance(v, list):
                out += mods([(kk, None, [x for x in vv if x[0] != "instant"]) for kk, _, vv in v if isinstance(vv, list)])
            elif isinstance(v, str) and k not in NOT_EFFECTS and k not in SKILLS:
                out += mods([(k, None, v)])
            elif k in ("custom_modifier_tooltip", "custom_effect_tooltip"):
                out += mods([(k, None, v)])
            elif k == "trait_xp_factor" and isinstance(v, list):  # learns other traits faster
                out += [f"Learns {text(kk) or kk.replace('_', ' ')} faster: {num(vv, True)}" for kk, _, vv in v
                        if isinstance(vv, str) and num(vv, True)]
            elif k == "enable_ability" and isinstance(v, str):
                out.append(f"Unlocks the ability {text(abilities.get(v, '')) or v.replace('_', ' ')}")
        eff[t] = [e for e in out if e]
    return eff


def traits(V, earth):
    """The base game's traits the Gazetteer offers its leaders (2026-10-15, the author: "add the option to add
    base-game traits to leaders"): generals' and admirals' from the generic unit leader traits (00_traits.txt; the
    country-specific files left out), rulers' those the game's own country leaders have, advisors' those its advisors
    have in each slot (with the slot's usual cost and each trait's ledger). Traits named for one of Earth's countries
    (their keys start with a tag in capitals: GER_..., trait_SPA_...) and those without an English name are left out, and so are rulers' and political
    advisors' traits only one of Earth's countries has (flavour such as a monarch's titles): those kept are the game's
    generic ones. `defined` lists every trait the game defines, for check_mod.py."""
    loc = loc_names(V)
    # a country's own traits start with its tag in capitals (GER_..., trait_SPA_..., JUNO_...)
    earthy = lambda k: bool(re.match(r"(?:trait_)?[A-Z][A-Z0-9]{1,4}_", k))
    named = lambda k: bool(loc.get(k)) and "$" not in loc[k] and not earthy(k)
    unit, bodies, consts = {}, {}, {}
    for f in sorted(glob.glob(str(V / "common/unit_leader/*.txt"))):
        for top, _, body in read(f):
            if top and top.startswith("@") and isinstance(body, str):
                consts[top] = body
            if top == "leader_traits" and isinstance(body, list):
                for k, _, v in body:
                    if k and isinstance(v, list):
                        d = {kk: vv for kk, _, vv in v if isinstance(vv, str)}
                        unit[k] = (d.get("type"), d.get("trait_type"), Path(f).name == "00_traits.txt")
                        bodies.setdefault(("unit", k), v)
    country = set()
    for f in sorted(glob.glob(str(V / "common/country_leader/*.txt"))):
        for top, _, body in read(f):
            if top and top.startswith("@") and isinstance(body, str):
                consts[top] = body
            if top == "leader_traits" and isinstance(body, list):
                country |= {k for k, _, v in body if k and isinstance(v, list)}
                for k, _, v in body:
                    if k and isinstance(v, list):
                        bodies.setdefault(("country", k), v)
    ruler, slots = {}, {s: {} for s, _ in ADVISOR_SLOTS}
    costs = {s: {} for s, _ in ADVISOR_SLOTS}
    who = {}            # (role or slot, trait) -> the countries whose characters have it
    for f in sorted(glob.glob(str(V / "common/characters/*.txt"))):
        for top, _, body in read(f):
            if top != "characters" or not isinstance(body, list):
                continue
            for cid, _, c in body:
                if not isinstance(c, list):
                    continue
                for role, _, r in c:
                    if not isinstance(r, list):
                        continue
                    ts = [t for k, _, v in r if k == "traits" and isinstance(v, list) for _, _, t in v if t in country]
                    if role == "country_leader":
                        for t in ts:
                            ruler[t] = ruler.get(t, 0) + 1
                            who.setdefault(("ruler", t), set()).add((cid or "")[:3])
                    elif role == "advisor":
                        d = {k: v for k, _, v in r if isinstance(v, str)}
                        slot = d.get("slot")
                        if slot not in slots:
                            continue
                        if d.get("cost", "").isdigit():
                            costs[slot][int(d["cost"])] = costs[slot].get(int(d["cost"]), 0) + 1
                        for t in ts:
                            who.setdefault((slot, t), set()).add((cid or "")[:3])
                            led = slots[slot].setdefault(t, {})
                            led[d.get("ledger")] = led.get(d.get("ledger"), 0) + 1

    def unit_list(kinds):
        out = [[k, loc[k], TRAIT_GROUPS[tt]] for k, (t, tt, generic) in unit.items()
               if generic and t in kinds and tt in TRAIT_GROUPS and named(k)]
        order = list(TRAIT_GROUPS.values())
        return sorted(out, key=lambda x: (order.index(x[2]), x[1].lower()))
    out = {
        "general": unit_list({"land", "all", "corps_commander"}),
        "admiral": unit_list({"navy", "all"}),
        "ruler": sorted(([k, loc[k]] for k in ruler if named(k) and len(who[("ruler", k)]) > 1),
                        key=lambda x: x[1].lower()),
        "slots": [[s, nm, max(costs[s], key=costs[s].get) if costs[s] else 150] for s, nm in ADVISOR_SLOTS],
        "advisor": {s: sorted(([k, loc[k], max(led, key=led.get) or ""] for k, led in slots[s].items()
                               if named(k) and (s != "political_advisor" or len(who[(s, k)]) > 1)),
                              key=lambda x: x[1].lower()) for s, _ in ADVISOR_SLOTS},
        "defined": {"unit": sorted(unit), "country": sorted(country)},
    }
    offered = {("unit", k) for r in ("general", "admiral") for k, *_ in out[r]} | \
        {("country", k) for k, *_ in out["ruler"]} | {("country", k) for v in out["advisor"].values() for k, *_ in v}
    eff = trait_effects(V, loc, {k: bodies[k] for k in offered}, consts)
    out["effects"] = {"unit": {k: v for (w, k), v in sorted(eff.items()) if w == "unit"},
                      "country": {k: v for (w, k), v in sorted(eff.items()) if w == "country"}}
    return out


# the base game's generic arms companies (common/military_industrial_organization/organizations/
# 00_generic_organization.txt, with Arms Against Tyranny) the Gazetteer offers, by kind: their group on the page and the
# generic designer (common/ideas/zzz_generic.txt) a company of that kind is without the DLC, which replaces designers
# by these organizations. Left out: the Black Sea Fleet (Earth's), the debug ones.
ARMS = {
    "tank": ("Tanks", "generic_tank_manufacturer"), "infantry_tank": ("Tanks", "generic_tank_manufacturer"),
    "assault_guns": ("Tanks", "generic_tank_manufacturer"), "mobile_tank": ("Tanks", "generic_tank_manufacturer"),
    "medium_tank": ("Tanks", "generic_tank_manufacturer"), "heavy_tank": ("Tanks", "generic_tank_manufacturer"),
    "tank_refurbishment_plant": ("Tanks", "generic_tank_manufacturer"),
    "task_force_ship": ("Ships", "generic_naval_manufacturer"), "battle_line_ship": ("Ships", "generic_naval_manufacturer"),
    "escort_ship": ("Ships", "generic_naval_manufacturer"), "raider_ship": ("Ships", "generic_naval_manufacturer"),
    "submarine": ("Ships", "generic_naval_manufacturer"), "refurbishment_repair": ("Ships", "generic_naval_manufacturer"),
    "general_aircraft": ("Aircraft", "generic_light_aircraft_manufacturer"),
    "light_aircraft": ("Aircraft", "generic_light_aircraft_manufacturer"),
    "cas_aircraft": ("Aircraft", "generic_light_aircraft_manufacturer"),
    "multi_role_aircraft": ("Aircraft", "generic_light_aircraft_manufacturer"),
    "high_agility_fighter_aircraft": ("Aircraft", "generic_light_aircraft_manufacturer"),
    "helicopter": ("Aircraft", "generic_light_aircraft_manufacturer"),
    "medium_aircraft": ("Aircraft", "generic_medium_aircraft_manufacturer"),
    "range_focused_aircraft": ("Aircraft", "generic_medium_aircraft_manufacturer"),
    "heavy_aircraft": ("Aircraft", "generic_heavy_aircraft_manufacturer"),
    "naval_aircraft": ("Aircraft", "generic_naval_aircraft_manufacturer"),
    "artillery": ("Land equipment", "generic_artillery_manufacturer"),
    "infantry_equipment": ("Land equipment", "generic_infantry_equipment_manufacturer"),
    "support_equipment": ("Land equipment", "generic_infantry_equipment_manufacturer"),
    "motorized_mechanized": ("Land equipment", "generic_motorized_equipment_manufacturer"),
    "armored_car": ("Land equipment", "generic_motorized_equipment_manufacturer"),
    "train": ("Land equipment", "generic_motorized_equipment_manufacturer"),
}
DESIGNER_SLOTS = ("tank_manufacturer", "naval_manufacturer", "aircraft_manufacturer", "materiel_manufacturer")


def companies(V, earth):
    """The base game's companies the Gazetteer offers (2026-10-15, the author: "allow people to create political
    advisors and companies"): arms companies of the generic kinds (with their name, icon and the generic designer each
    is without Arms Against Tyranny: picture, research bonus, trait, cost), and industrial concerns of the kinds the
    game's own concerns most often are (a trait used by three or more of them, not one country's: the trait's name, the
    research bonus and generic picture they most often have, their usual cost). `research` names the research
    categories, for the page."""
    loc = loc_names(V)

    def fields(body):
        return {k: v for k, _, v in body if k and isinstance(v, str)}

    def research(body):
        rb = next((v for k, _, v in body if k == "research_bonus" and isinstance(v, list)), [])
        return {k: float(v) for k, _, v in rb if k and isinstance(v, str) and re.fullmatch(r"-?[\d.]+", v)}

    def trait_of(body):
        tr = next((v for k, _, v in body if k == "traits" and isinstance(v, list)), [])
        return next((t for _, _, t in tr if isinstance(t, str)), None)
    mio = {k: body for k, _, body in read(V / "common/military_industrial_organization/organizations/"
                                              "00_generic_organization.txt") if isinstance(body, list)}
    designers = {}
    for top, _, cats in read(V / "common/ideas/zzz_generic.txt"):
        for cat, _, entries in (cats if top == "ideas" and isinstance(cats, list) else []):
            if cat not in DESIGNER_SLOTS or not isinstance(entries, list):
                continue
            for key, _, body in entries:
                if key and isinstance(body, list):
                    f = fields(body)
                    designers[key] = dict(category=cat, picture=f.get("picture"), research=research(body),
                                          trait=trait_of(body), cost=int(f.get("cost", 150)),
                                          removal_cost=int(f.get("removal_cost", 10)))
    arms = []
    for kind, (group, designer) in ARMS.items():
        key = f"generic_{kind}_organization"
        why = (f"{key} is no longer the game's" if key not in mio else f"{designer} is no longer the game's"
               if designer not in designers else f"{key} has no English name in the game" if not loc.get(key) else None)
        if why:   # (2026-10-15: generic_train_organization has no name)
            print(f"companies: {why}; left out")
            continue
        arms.append([key, loc[key], group, fields(mio[key]).get("icon"), designer])
    # industrial concerns: every idea of the slot in the game's files, by its trait
    uses = {}
    for f in sorted(glob.glob(str(V / "common/ideas/*.txt"))):
        for top, _, cats in read(f):
            for cat, _, entries in (cats if top == "ideas" and isinstance(cats, list) else []):
                if cat != "industrial_concern" or not isinstance(entries, list):
                    continue
                for key, _, body in entries:
                    if not (key and isinstance(body, list)):
                        continue
                    t = trait_of(body)
                    if t:
                        f_ = fields(body)
                        uses.setdefault(t, []).append((key, f_.get("picture"), research(body), f_.get("cost")))
    earthy = lambda k: bool(re.match(r"(?:trait_)?[A-Z][A-Z0-9]{1,4}_", k)) or k.split("_")[0] in earth
    concerns = []
    for t, us in uses.items():
        if len(us) < 3 or earthy(t) or not loc.get(t) or "$" in loc[t]:
            continue
        most = lambda xs: max(set(xs), key=xs.count) if xs else None
        rb = most([json.dumps(r, sort_keys=True) for _, _, r, _ in us if r])
        pics = [p for _, p, _, _ in us if p and p.startswith("generic_")]
        cost = most([c for _, _, _, c in us if c and c.isdigit()])
        concerns.append([t, loc[t], most(pics) or "generic_industrial_concern_1", json.loads(rb) if rb else {},
                         int(cost or 150)])
    concerns.sort(key=lambda c: (-len(uses[c[0]]), c[1].lower()))
    cats = sorted({c for d in designers.values() for c in d["research"]} | {c for x in concerns for c in x[3]})
    return {"arms": arms, "designers": designers, "concerns": concerns,
            "research": {c: loc.get(c, c.replace("_", " ").capitalize()) for c in cats},
            "templates": sorted(mio)}   # every generic organisation, for check_mod.py


def main():
    V = vanilla_dir(sys.argv)
    files = sorted(Path(p).relative_to(V).as_posix() for p in glob.glob(str(V / "common/technologies/*.txt")))
    files += FILES
    if OUT.exists():
        shutil.rmtree(OUT / "files", ignore_errors=True)
        shutil.rmtree(OUT / "index", ignore_errors=True)
    for rel in files:
        dst = OUT / "files" / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(V / rel, dst)
    idx = OUT / "index"
    idx.mkdir(parents=True, exist_ok=True)

    def put(name, lines, head):
        (idx / name).write_text(f"# {head} (vanilla 1.19.3, scripts/vanilla_sync.py)\n" + "\n".join(lines) + "\n",
                                encoding="utf-8")

    # country tags, with the name of their country file
    tags = []
    for line in (V / "common/country_tags/00_countries.txt").read_text(encoding="utf-8-sig").splitlines():
        m = re.match(r'\s*([A-Z0-9]{3})\s*=\s*"countries/([^"]+)\.txt"', line)
        if m:
            tags.append(f"{m[1]}\t{m[2]}")
    put("tags.txt", tags, "Earth's country tags: tag, country file name")

    kinds = decisions(V)
    used = referenced(V, set(kinds))
    put("decisions.txt", [f"{n}\t{kinds[n]}" for n in sorted(used)],
        "vanilla decisions that files the game still loads refer to: name, kind")

    sprites = set()
    for f in glob.glob(str(V / "interface/**/*.gfx"), recursive=True):
        sprites |= set(re.findall(r'name\s*=\s*"(GFX_[^"]+)"', Path(f).read_text(encoding="utf-8-sig", errors="replace")))
    put("sprites.txt", sorted(sprites), "every sprite vanilla's interface/*.gfx declares")
    named = set()
    for f in glob.glob(str(V / "interface/**/*.gui"), recursive=True):
        named |= set(re.findall(r'"(GFX_\w+)"', Path(f).read_text(encoding="utf-8-sig", errors="replace")))
    put("gui_undefined_sprites.txt", sorted(named - sprites),
        "sprites vanilla's own interface/*.gui files name but no .gfx declares (the game tolerates them; the "
        "Deco UI keeps them in the vanilla files it patches)")

    techs = set()
    for f in glob.glob(str(V / "common/technologies/*.txt")):
        for top, _, body in read(f):
            if top == "technologies" and isinstance(body, list):
                techs |= {k for k, _, v in body if k and isinstance(v, list) and not k.startswith("@")}
    put("technologies.txt", sorted(techs), "technologies")

    equipment = set()
    for f in glob.glob(str(V / "common/units/equipment/*.txt")):
        for top, _, body in read(f):
            if top == "equipments" and isinstance(body, list):
                equipment |= {k for k, _, v in body if k and isinstance(v, list)}
    put("equipment.txt", sorted(equipment), "equipment types")

    modules = set()
    for f in glob.glob(str(V / "common/units/equipment/modules/*.txt")):
        for top, _, body in read(f):
            if top == "equipment_modules" and isinstance(body, list):
                modules |= {k for k, _, v in body if k and isinstance(v, list)}
    put("modules.txt", sorted(modules), "equipment modules (tank, ship and plane designer parts)")

    subunits = set()
    for f in glob.glob(str(V / "common/units/*.txt")):
        for top, _, body in read(f):
            if top == "sub_units" and isinstance(body, list):
                subunits |= {k for k, _, v in body if k and isinstance(v, list)}
    put("subunits.txt", sorted(subunits), "battalions and companies")

    ideas = set()
    for f in glob.glob(str(V / "common/ideas/*.txt")):
        for top, _, body in read(f):
            if top == "ideas" and isinstance(body, list):
                for cat, _, group in body:
                    if isinstance(group, list):
                        ideas |= {k for k, _, v in group if k and isinstance(v, list) and k != "designer"}
    put("ideas.txt", sorted(ideas), "ideas (national spirits, laws, advisors)")
    caps = OUT / NAME_CAPS
    caps.parent.mkdir(parents=True, exist_ok=True)
    caps.write_text("\ufeffl_english:\n # the game's lines with a country's name opening a sentence, capitalised "
                    "(scripts/vanilla_sync.py, name_caps)\n" + "\n".join(name_caps(V)) + "\n", encoding="utf-8")
    autonomy = set()
    for f in sorted((V / "common/autonomous_states").glob("*.txt")):
        autonomy |= set(re.findall(r"\bid\s*=\s*(\w+)", f.read_text(encoding="utf-8-sig")))
    put("autonomy_states.txt", sorted(autonomy), "autonomy levels (puppet, dominion ...)")

    defines = []
    for f, ns in (("common/defines/00_defines.lua", "NDefines"), ("common/defines/00_graphics.lua", "NDefines_Graphics")):
        cat = None
        for line in (V / f).read_text(encoding="utf-8-sig", errors="replace").splitlines():
            m = re.match(r"^(\w+)\s*=\s*\{", line)          # a category, at the left margin
            if m and m[1] != ns:
                cat = m[1]
                continue
            m = re.match(r"^\t(\w+)\s*=", line)
            if m and cat:
                defines.append(f"{ns}.{cat}.{m[1]}")
    put("defines.txt", sorted(set(defines)), "defines")

    put("map_files.txt", sorted(Path(p).relative_to(V / "map").as_posix()
                                for p in glob.glob(str(V / "map/**/*"), recursive=True) if Path(p).is_file()),
        "files in vanilla's map folder")

    # generic names with years (equipment, hulls, chassis), shifted with the start date
    names = []
    earth = {t.split("\t")[0] for t in tags}
    for fn in YEAR_NAME_FILES:
        p = V / "localisation/english" / fn
        if not p.exists():
            continue
        for line in p.read_text(encoding="utf-8-sig").splitlines():
            m = re.match(r'^ ([A-Za-z][\w.\-]*):\d* "(.*)"\s*(#.*)?$', line)
            if not m or not re.search(r"\b1[89]\d\d\b", m[2]):
                continue
            key = m[1]
            if key.split("_")[0] in earth or key.endswith("_desc"):
                continue
            names.append(f' {key}: "{m[2]}"')
    put("year_names.yml", names, "generic localisation with years: key and text")

    tr = traits(V, earth)
    (idx / "traits.json").write_text(json.dumps(dict(_="the base game's traits the Gazetteer offers its leaders, and every "
                                                      "trait it defines (vanilla 1.19.3, scripts/vanilla_sync.py)", **tr),
                                                 ensure_ascii=False, indent=0, sort_keys=False) + "\n", encoding="utf-8")

    co = companies(V, earth)
    (idx / "companies.json").write_text(json.dumps(dict(_="the base game's company kinds the Gazetteer offers: arms "
                                                         "companies (organizations, and their designers without Arms "
                                                         "Against Tyranny) and industrial concerns (vanilla 1.19.3, "
                                                         "scripts/vanilla_sync.py)", **co),
                                                    ensure_ascii=False, indent=0) + "\n", encoding="utf-8")

    n = sum(1 for _ in (OUT / "files").rglob("*") if _.is_file())
    print(f"source/vanilla: {n} files, {len(tags)} tags, {len(used)} decisions referenced, {len(sprites)} sprites, "
          f"{len(techs)} technologies, {len(equipment)} equipment, {len(modules)} modules, {len(subunits)} sub-units, "
          f"{len(ideas)} ideas, "
          f"{len(defines)} defines, {len(names)} names with years; traits: {len(tr['general'])} generals', "
          f"{len(tr['admiral'])} admirals', {len(tr['ruler'])} rulers', "
          f"{sum(len(v) for v in tr['advisor'].values())} advisors'; companies: {len(co['arms'])} arms kinds, "
          f"{len(co['concerns'])} industrial concern kinds")


if __name__ == "__main__":
    main()
