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

    n = sum(1 for _ in (OUT / "files").rglob("*") if _.is_file())
    print(f"source/vanilla: {n} files, {len(tags)} tags, {len(used)} decisions referenced, {len(sprites)} sprites, "
          f"{len(techs)} technologies, {len(equipment)} equipment, {len(modules)} modules, {len(subunits)} sub-units, "
          f"{len(ideas)} ideas, "
          f"{len(defines)} defines, {len(names)} names with years")


if __name__ == "__main__":
    main()
