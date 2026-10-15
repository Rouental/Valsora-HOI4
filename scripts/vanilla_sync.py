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
       "events/Special_Project_Events.txt"])

# localisation files whose generic names carry years ("1936 Cruiser Hull", "1938 Medium", the game
# rule's "Focuses Only (Until 1938)")
YEAR_NAME_FILES = ("designer_l_english.yml", "research_l_english.yml", "tank_modules_l_english.yml",
                   "game_rules_l_english.yml")


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
            m = re.match(r'^ ([\w.\-]+):\d* "(.*)"', line)
            if m and m[1] not in out:
                out[m[1]] = re.sub(r"\s+", " ", re.sub(r"§.|£\w+|\[[^]]*\]|\\n", " ", m[2])).strip()
    return out


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
    unit = {}
    for f in sorted(glob.glob(str(V / "common/unit_leader/*.txt"))):
        for top, _, body in read(f):
            if top == "leader_traits" and isinstance(body, list):
                for k, _, v in body:
                    if k and isinstance(v, list):
                        d = {kk: vv for kk, _, vv in v if isinstance(vv, str)}
                        unit[k] = (d.get("type"), d.get("trait_type"), Path(f).name == "00_traits.txt")
    country = set()
    for f in sorted(glob.glob(str(V / "common/country_leader/*.txt"))):
        for top, _, body in read(f):
            if top == "leader_traits" and isinstance(body, list):
                country |= {k for k, _, v in body if k and isinstance(v, list)}
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
    return {
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

    n = sum(1 for _ in (OUT / "files").rglob("*") if _.is_file())
    print(f"source/vanilla: {n} files, {len(tags)} tags, {len(used)} decisions referenced, {len(sprites)} sprites, "
          f"{len(techs)} technologies, {len(equipment)} equipment, {len(modules)} modules, {len(subunits)} sub-units, "
          f"{len(ideas)} ideas, "
          f"{len(defines)} defines, {len(names)} names with years; traits: {len(tr['general'])} generals', "
          f"{len(tr['admiral'])} admirals', {len(tr['ruler'])} rulers', "
          f"{sum(len(v) for v in tr['advisor'].values())} advisors'")


if __name__ == "__main__":
    main()
