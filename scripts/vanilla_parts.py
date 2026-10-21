"""Vanilla's parts in the mod: its files we ship changed, and what stands in for its Earth.

Valsora takes place in 2036 (author, 2026-10-14), a hundred years after vanilla's start, so
every date and research year the game reads moves by YEARS:
  - the start and end dates (defines()) and our own history (build_mod.py, nations.py);
  - vanilla's files in source/vanilla/files/ (copied by vanilla_sync.py) and the curated ones
    in source/vanilla/curated/: the technologies' start_year (the research penalty for being
    ahead of time is counted from it), the tech tree's year labels, and the date conditions of
    the generic content the mod keeps (laws, the generic focus tree, faction goals, AI
    templates and strategies, raids, special projects, medals, events);
  - the generic names with years ("1936 Cruiser Hull", "1938 Medium").
Equipment keeps its years: they set licence costs, counted from 1936 (LICENSE_IC_COST_YEAR_INCREASE).

Earth's content still loads where the mod does not switch it off, and refers to things the
mod has removed. Stand-ins keep that quiet (error.log of 2026-10-14):
  - stand_ins(): a never-visible decision under each of the 732 vanilla decision names that
    loaded files refer to (1,142 lines: the mod switches vanilla's decisions off);
  - history_stubs(): a history file for each of Earth's 364 country tags, which stay defined
    because vanilla's technologies, peace conference, AI and achievements name them (728
    lines of "is missing a history file").
"""
import re
from pathlib import Path

SRC = Path("source/vanilla")
YEARS = 100
START_DATE = "2036.1.1.12"
END_DATE = "2049.1.1.1"          # vanilla runs 13 years too

# Earth-only blocks of the generic AI strategies (default.txt): Japan's, the USA's and Britain's naval
# focus, and the area priorities for Earth's regions (europe, asia, suez, ...)
DROP = {"common/ai_strategy/default.txt": ("slightly_naval_focused_nation", "more_naval_focused_nation",
                                           "default_area_priority", "default_area_priority_non_africa")}

# Lines of vanilla's files changed or taken out: path -> [(vanilla's text, ours)]. The puppet (2026-10-17): with Death
# or Dishonor, vanilla allows no puppet under a fascist overlord (Germany's are Reichskommissariats), but Valsora's
# "Authoritarian" is every strongman and junta: Kampf's Hohenzburg and Illiricium's three Bleacherist republics are
# puppets of Authoritarian overlords
EDITS = {"common/autonomous_states/puppet.txt": [(
    """\t\tif = {\n\t\t\tlimit = { has_dlc = "Death or Dishonor" }\n\t\t\tOVERLORD = { NOT = { has_government = fascism } }\n\t\t}\n""",
    "\t\t# Valsora: Authoritarian overlords too (vanilla: no fascist overlord with Death or Dishonor)\n")]}

# The game's generic advisors and theorists (history/general/generic_advisors.txt; author, 2026-10-21: "might as well
# bring back generic advisors and theorists"): its first five blocks are the generic ones (the four political
# advisors, then the industrialists, chiefs, high command and theorists), the rest Earth's special cases (Iceland,
# Belgium, Afghanistan, ...), dropped. In the five, every condition naming an Earth country (the countries left out,
# New Zealand's focuses) goes; the military block, which vanilla gives only to a list of Earth's minor countries,
# goes to every country that is not a dynamic one, as the political advisors do
ADVISORS = "history/general/generic_advisors.txt"
ADVISOR_BLOCKS = 5
EARTH = re.compile(r"\b(?:original_)?tag\s*=|is_chinese_warlord|has_completed_focus\s*=\s*[A-Z]{3}_")
CONDITION = re.compile(r"\b(IF|if|ELSE_IF|else_if|NOT|OR|AND)\s*=\s*\{")


def block_end(text, i):
    """The index just past the `}` closing the block whose `{` is at i - 1."""
    depth = 1
    while depth:
        c = text[i]
        if c == "#":
            i = text.index("\n", i)
            continue
        depth += {"{": 1, "}": -1}.get(c, 0)
        i += 1
    return i


def strip_earth(text):
    """The text without the condition blocks (IF, NOT, OR, ...) and the lines that name an Earth country."""
    out, i = [], 0
    while (m := CONDITION.search(text, i)):
        end = block_end(text, m.end())
        if EARTH.search(text[m.end():end - 1]):
            start = text.rfind("\n", 0, m.start()) + 1
            out.append(text[i:start] + "\0" if not text[start:m.start()].strip() else text[i:m.start()])
            i = end
        else:
            out.append(text[i:m.end()] + strip_earth(text[m.end():end - 1]) + "}")
            i = end
    out.append(text[i:])
    return re.sub(r"(?m)^[ \t]*(?:original_)?tag\s*=\s*\w+[ \t]*$", "\0", "".join(out))


def tidy(text):
    """strip_earth's marks taken out, with the comments above them (about what was removed) and blank lines."""
    text = re.sub(r"(?m)(?:^[ \t]*#[^\n]*\n|^[ \t]*\n)*^\0[ \t]*\n", "", text)
    return re.sub(r"\n(?:[ \t]*\n)+(?=\t*\})", "\n", text)


def generic_advisors(text):
    text = text.replace("\r\n", "\n")
    spans, i = [], 0
    while (m := re.compile(r"(?m)^\s*every_possible_country\s*=\s*\{").search(text, i)):
        spans.append((m.start(), block_end(text, m.end())))
        i = spans[-1][1]
    tokens = [re.findall(r"token_base\s*=\s*(\w+)", text[a:b]) for a, b in spans[:ADVISOR_BLOCKS]]
    if len(spans) <= ADVISOR_BLOCKS or tokens[-1][:1] != ["generic_captain_of_industry"] \
            or "generic_air_warfare_theorist" not in tokens[-1]:
        raise SystemExit(f"vanilla_parts: {ADVISORS} is not laid out as Valsora expects (game updated?)")
    keep = []
    for a, b in spans[:ADVISOR_BLOCKS]:
        block = tidy(strip_earth(text[a:b]))
        m = re.search(r"\blimit\s*=\s*\{", block)
        if "is_dynamic_country" not in block[m.end():block_end(block, m.end())]:
            block = block[:m.end()] + "\n\t\tis_dynamic_country = no" + block[m.end():]
        keep.append(block.lstrip("\n"))
    out = (text[:spans[0][0]].rstrip("\n") + "\n# Valsora: every country but the dynamic ones; Earth's special cases "
           "and the conditions naming Earth's countries removed\n\n" + "\n\n".join(keep) + "\n")
    if EARTH.search(out):
        raise SystemExit(f"vanilla_parts: {ADVISORS} still names an Earth country")
    return out


DATE = re.compile(r"(?<![\w.@])(1[89]\d\d)(\.\d{1,2}\.\d{1,2})(?![\d])")
START_YEAR = re.compile(r"(\bstart_year\s*=\s*)(1[89]\d\d)\b")
GUI_YEAR = re.compile(r'(\btext\s*=\s*")(1[89]\d\d)(")')


def year(y):
    return str(int(y) + YEARS)


def shift(text, gui=False):
    """Every date (1936.1.1), research year (start_year = 1936) and, in a .gui, year label moved."""
    text = DATE.sub(lambda m: year(m[1]) + m[2], text)
    text = START_YEAR.sub(lambda m: m[1] + year(m[2]), text)
    if gui:
        text = GUI_YEAR.sub(lambda m: m[1] + year(m[2]) + m[3], text)
    return text


def drop_blocks(text, names):
    """The text without the top-level `name = { ... }` blocks named."""
    for name in names:
        m = re.search(rf"(?m)^{re.escape(name)}\s*=\s*\{{", text)
        if not m:
            raise SystemExit(f"vanilla_parts: block {name} not found (game updated? re-run vanilla_sync.py)")
        i, depth = m.end(), 1
        while depth:
            c = text[i]
            if c == "#":
                i = text.index("\n", i)
                continue
            depth += {"{": 1, "}": -1}.get(c, 0)
            i += 1
        text = text[:m.start()] + f"# Valsora: {name} removed (Earth only)\n" + text[i:]
    return text


def files():
    """(path in the mod, text, has BOM) of every vanilla file the mod ships, shifted to 2036."""
    out = []
    for root in (SRC / "files", SRC / "curated"):
        for p in sorted(root.rglob("*")):
            if not p.is_file():
                continue
            rel = p.relative_to(root).as_posix()
            raw = p.read_bytes()
            bom = raw.startswith(b"\xef\xbb\xbf")
            text = raw.decode("utf-8-sig")
            text = shift(text, gui=rel.endswith(".gui"))
            if rel in DROP:
                text = drop_blocks(text, DROP[rel])
            if rel == ADVISORS:
                text = generic_advisors(text)
            for old, new in EDITS.get(rel, []):
                if old not in text.replace("\r\n", "\n"):
                    raise SystemExit(f"vanilla_parts: {rel} no longer has the text Valsora changes (game updated?)")
                text = text.replace("\r\n", "\n").replace(old, new)
            out.append((rel, text, bom))
    return out


EVENT_FIRE = re.compile(r"\b(country|news|state|unit_leader|operative_leader)_event\s*=\s*\{[^{}]*?\bid\s*=\s*([\w.]+)", re.S)
EVENT_DEF = re.compile(r"^(country|news|state|unit_leader|operative_leader)_event\s*=\s*\{\s*(?:#[^\n]*\s*)*id\s*=\s*([\w.]+)",
                       re.M)


def event_stand_ins(shipped):
    """events/valsora_vanilla_event_stand_ins.txt: a hidden, empty event for each event the shipped
    vanilla files fire that none of them defines (only for Earth's countries, e.g. Denmark's election
    event; their files stay switched off), so the game finds every event it is told to fire."""
    texts = [re.sub(r"#[^\n]*", "", text) for _, text, _ in shipped]
    defined = {m[2] for text in texts for m in EVENT_DEF.finditer(text)}
    fired = {}
    for text in texts:
        for m in EVENT_FIRE.finditer(text):
            fired.setdefault(m[2], m[1])
    missing = sorted(e for e in fired if e not in defined)
    out = ["# Valsora: stand-ins for events that vanilla's generic files fire only for Earth's countries",
           "# (generated by scripts/vanilla_parts.py)"]
    for ns in sorted({e.split(".")[0] for e in missing}):
        out.append(f"add_namespace = {ns}")
    for e in missing:
        kind = fired[e] if fired[e] in ("country", "news", "state") else "country"
        out += [f"{kind}_event = {{", f"\tid = {e}", "\thidden = yes", "\tis_triggered_only = yes",
                "\toption = { name = OK }", "}"]
    return "\n".join(out) + "\n", missing


def index(name):
    path = SRC / "index" / name
    return [line for line in path.read_text(encoding="utf-8").splitlines() if line and not line.startswith("#")]


def year_names():
    """localisation/english/replace: vanilla's generic names with years, moved to Valsora's."""
    lines = ["l_english:"]
    for line in index("year_names.yml"):
        key, text = re.match(r'^ ([^:]+): "(.*)"$', line).groups()
        text = re.sub(r"\b(1[89]\d\d)\b", lambda m: year(m[1]), text)
        lines.append(f' {key}: "{text}"')
    return "\n".join(lines) + "\n"


def stand_ins():
    """(category file, decisions file): a never-visible stand-in for each vanilla decision the
    loaded files name, of the same kind (a mission for has_active_mission, a targeted decision
    for activate_targeted_decision ...)."""
    cat = ("# Valsora: holds the stand-ins for vanilla's decisions (scripts/vanilla_parts.py); never shown\n"
           "valsora_vanilla_stand_ins = {\n\tvisible = { always = no }\n\tallowed = { always = no }\n}\n")
    body = {
        "decision": "",
        "mission": "\t\tactivation = { always = no }\n\t\tdays_mission_timeout = 30\n",
        "targeted": "\t\ttarget_trigger = { FROM = { always = no } }\n",
        "state_targeted": "\t\tstate_target = yes\n\t\ttarget_trigger = { FROM = { always = no } }\n",
    }
    out = ["# Valsora: stand-ins for the vanilla decisions that vanilla's focus trees, ideas, scripted",
           "# triggers and decision categories still name (the mod switches vanilla's decisions off).",
           "# They can never be seen or taken. Generated by scripts/vanilla_parts.py from",
           "# source/vanilla/index/decisions.txt.", "valsora_vanilla_stand_ins = {"]
    for line in index("decisions.txt"):
        name, kind = line.split("\t")
        out += [f"\t{name} = {{", "\t\tallowed = { always = no }", "\t\tvisible = { always = no }",
                "\t\tavailable = { always = no }", body[kind].rstrip("\n"), "\t}"]
    out.append("}")
    return cat, "\n".join(x for x in out if x != "") + "\n"


def ascii_name(name):
    import unicodedata
    return re.sub(r"[^A-Za-z0-9 \-']", "", unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode())


def history_stubs(capital):
    """{file name: text}: a history for each of Earth's country tags (none of them is on the map)."""
    out = {}
    for line in index("tags.txt"):
        tag, name = line.split("\t")
        out[f"{tag} - {ascii_name(name)}.txt"] = (
            f"# Valsora: Earth's {tag} ({name}) is not on this map. This file only keeps error.log free of\n"
            f"# \"{tag} - is missing a history file\"; the tag stays defined because vanilla's files name it.\n"
            f"capital = {capital}\n"
            "set_politics = {\n\truling_party = neutrality\n\telections_allowed = no\n}\n"
            "set_popularities = {\n\tdemocratic = 0\n\tfascism = 0\n\tcommunism = 0\n\tneutrality = 100\n"
            "\ttheocracy = 0\n}\n")
    return out


def defines():
    return ("-- Valsora takes place in 2036 (scripts/vanilla_parts.py)\n"
            f'NDefines.NGame.START_DATE = "{START_DATE}"\n'
            f'NDefines.NGame.END_DATE = "{END_DATE}"\n'
            f'NDefines.NDiplomacy.TENSION_TIME_SCALE_START_DATE = "{START_DATE}"\n')


def theaters(continents):
    """common/ai_faction_theaters/ai_faction_theaters.txt (vanilla's file name, so Earth's theaters go):
    continents is a list of (theater key, continent, [region ids, connected, the first a land region])."""
    out = ["# Valsora: the AI's faction theaters, one per continent (and its seas), in place of vanilla's",
           "# Earth theaters (Barbarossa, North Africa ...). Generated by scripts/build_mod.py.", ""]
    for key, cont, regions in continents:
        out += [f"valsora_{key} = {{", f"\tname = theater_valsora_{key}", "\tregions = {"]
        out += [f"\t\t{r}" for r in regions]
        out += ["\t}", "\tcan_skip_first_region = yes",
                "\tcancel = {", "\t\thas_war = no", "\t}",
                "\tai_will_do = {", "\t\tbase = 0",
                "\t\tmodifier = {", "\t\t\tadd = 1", f"\t\t\tcapital_scope = {{ is_on_continent = {cont} }}", "\t\t}",
                "\t\tmodifier = {", "\t\t\tadd = 5",
                f"\t\t\tany_enemy_country = {{ capital_scope = {{ is_on_continent = {cont} }} }}", "\t\t}",
                "\t\tmodifier = {", "\t\t\tfactor = 0", "\t\t\thas_war = no", "\t\t}",
                "\t}", "}", ""]
    return "\n".join(out)
