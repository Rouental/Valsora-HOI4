"""Mutation test of check_mod.py: break copies of the built mod in known ways and make sure each break is reported.

Run after a build, from the repo root:  python3 scripts/mutation_test.py [build/valsora_test]
Run it after changing check_mod.py, or after a change that could hide a break from it (2026-10-15: the catalogue of the
breaks each new check was tested with, gathered in one place instead of a one-off script per round).

How: the mutations are grouped in batches by what they break (the map files, the scripts and localisation, the
interface). Each batch gets its own copy of the mod made of hard links (no extra disk; a mutated file is written anew,
so the build itself is never touched), all its mutations at once, and one check_mod.py run; the batches run side by
side. A break a batch misses is tried again alone, in case another break in its batch hid it (check_mod stops some
checks early on a broken file): only one missed alone is a real miss. Exit status 1 on any miss.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)                     # check_mod.py reads source/ and work/ from the repo root
sys.path.insert(0, str(ROOT / "scripts"))
from common import BUILD, MOD_DIR_NAME  # noqa: E402

SRC = Path(sys.argv[1] if len(sys.argv) > 1 else BUILD / MOD_DIR_NAME).resolve()


# ---------------------------------------------------------------- editing a copy without touching the build
def _write(p, data):
    p.unlink()                      # a hard link to the build: the new file must be a new inode
    p.write_bytes(data)


def edit(mod, rel, fn):
    """change a text file: fn(text) -> new text (a BOM is kept)"""
    p = mod / rel
    raw = p.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    new = fn(text)
    if new == text:
        raise AssertionError(f"the mutation of {rel} changed nothing (the build changed? update the catalogue)")
    _write(p, (b"\xef\xbb\xbf" if bom else b"") + new.encode("utf-8"))


def edit_bytes(mod, rel, fn):
    p = mod / rel
    raw = p.read_bytes()
    new = fn(raw)
    if new == raw:
        raise AssertionError(f"the mutation of {rel} changed nothing")
    _write(p, new)


def add_file(mod, rel, data):
    p = mod / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        raise AssertionError(f"{rel} exists already")
    p.write_bytes(data)


def bmp(mod, rel):
    """(header bytes, pixel rows top-down as a writable array, bits per pixel) of an uncompressed BMP"""
    raw = (mod / rel).read_bytes()
    off = int.from_bytes(raw[10:14], "little")
    w = int.from_bytes(raw[18:22], "little", signed=True)
    h = int.from_bytes(raw[22:26], "little", signed=True)
    bpp = int.from_bytes(raw[28:30], "little")
    row = (w * bpp // 8 + 3) // 4 * 4
    px = np.frombuffer(raw, np.uint8, row * abs(h), off).reshape(abs(h), row)
    return raw[:off], px[::-1].copy() if h > 0 else px.copy(), bpp, h > 0


def put_bmp(mod, rel, head, rows, bottom_up):
    _write(mod / rel, head + (rows[::-1] if bottom_up else rows).tobytes())


def definition(mod):
    """province id -> (r, g, b, kind) from definition.csv"""
    out = {}
    for ln in (mod / "map/definition.csv").read_text().splitlines()[1:]:
        f = ln.split(";")
        out[int(f[0])] = (int(f[1]), int(f[2]), int(f[3]), f[4])
    return out


def rou_history(mod):
    return next((mod / "history/countries").glob("ROU - *.txt")).relative_to(mod)


# ---------------------------------------------------------------- the catalogue: (name, mutate(mod) -> expected text)
def m_crlf(mod):
    edit_bytes(mod, "map/definition.csv", lambda b: b.replace(b"\r\n", b"\n"))
    return "definition.csv must use CRLF line endings"


def m_adjacency_end(mod):
    edit_bytes(mod, "map/adjacencies.csv", lambda b: b.replace(b"-1;-1;;-1;-1;-1;-1;-1;-1", b""))
    return "adjacencies.csv needs CRLF and the -1 end line"


def m_building_row(mod):
    def drop(t):
        lines = t.splitlines(keepends=True)
        i = next(k for k, ln in enumerate(lines) if ln.split(";")[1:2] == ["arms_factory"])
        return "".join(lines[:i] + lines[i + 1:])
    edit(mod, "map/buildings.txt", drop)
    return "arms_factory positions, needs 6"


def m_ships_in_port(mod):
    rows = (mod / "map/unitstacks.txt").read_text().splitlines(keepends=True)
    first = next(r.split(";")[0] for r in rows if r.split(";")[1] == "19")
    edit(mod, "map/unitstacks.txt", lambda t: "".join(r for r in rows if not (r.split(";")[0] == first and r.split(";")[1] in ("19", "20"))))
    return f"province {first} lacks unit stacks 19 and 20 (ships in port)"


def m_earth_map_file(mod):
    (mod / "map/adjacency_rules.txt").unlink()
    return "map/adjacency_rules.txt: vanilla's (Earth's) would be loaded"


def m_weather_big(mod):
    edit(mod, "map/weatherpositions.txt", lambda t: re.sub(r";big(\r?\n)", r";large\1", t, count=1))
    return "needs a small and a big weather position"


def m_supply_node_sea(mod):
    sea = next(i for i, d in definition(mod).items() if d[3] == "sea")
    edit(mod, "map/supply_nodes.txt", lambda t: re.sub(r"^1 \d+", f"1 {sea}", t, count=1))
    return f"supply node on province {sea}, which is in no state"


def m_railway_apart(mod):
    land = [i for i, d in definition(mod).items() if d[3] == "land"]
    edit(mod, "map/railways.txt", lambda t: t + f"1 2 {land[0]} {land[-1]}\n")
    return f"railway from province {land[0]} to {land[-1]}, which don't touch"


def m_x_crossing(mod):
    head, rows, bpp, up = bmp(mod, "map/provinces.bmp")
    d = definition(mod)
    land = [i for i, v in d.items() if v[3] == "land"]
    w = rows.shape[1] // 3
    px = rows[:, :w * 3].reshape(rows.shape[0], w, 3)
    a, b, c, e = (d[land[k]] for k in (100, 200, 300, 400))
    y, x = 1200, 2600
    for (dy, dx), col in zip(((0, 0), (0, 1), (1, 0), (1, 1)), (a, b, c, e)):
        px[y + dy, x + dx] = (col[2], col[1], col[0])         # BGR
    put_bmp(mod, "map/provinces.bmp", head, rows, up)
    return "X-crossings, first at"


def m_land_low(mod):
    head, rows, bpp, up = bmp(mod, "map/heightmap.bmp")
    land = np.argwhere(bmp(mod, "map/terrain.bmp")[1] != 15)
    y, x = land[len(land) // 2]
    rows[y, x] = 90
    put_bmp(mod, "map/heightmap.bmp", head, rows, up)
    return "land pixels at or below sea level"


def m_terrain_ocean(mod):
    head, rows, bpp, up = bmp(mod, "map/terrain.bmp")
    land = np.argwhere(rows != 15)
    y, x = land[len(land) // 3]
    rows[y, x] = 15
    put_bmp(mod, "map/terrain.bmp", head, rows, up)
    return "terrain.bmp: land uses the ocean index 15"


def m_technology(mod):
    edit(mod, rou_history(mod), lambda t: t.replace("set_technology = {", "set_technology = {\n\tvalsora_no_such_tech = 1", 1))
    return "technology valsora_no_such_tech is not the game's"


def m_module(mod):
    edit(mod, rou_history(mod), lambda t: t.replace("main_armament_slot = tank_small_cannon", "main_armament_slot = tank_no_such_gun", 1))
    return "equipment module tank_no_such_gun is not the game's"


def m_equipment(mod):
    edit(mod, rou_history(mod), lambda t: t.replace("type = medium_tank_chassis_1", "type = medium_tank_no_such_chassis", 1))
    return "equipment medium_tank_no_such_chassis is not the game's"


def m_idea(mod):
    edit(mod, rou_history(mod), lambda t: t + "\nadd_ideas = valsora_no_such_idea\n")
    return "idea valsora_no_such_idea is neither ours nor the game's"


def m_battalion(mod):
    oob = next((mod / "history/units").glob("ROU_*.txt")).relative_to(mod)
    edit(mod, oob, lambda t: re.sub(r"regiments = \{", "regiments = {\n\t\tno_such_battalion = { x = 3 y = 3 }", t, count=1))
    return "battalion or company no_such_battalion is not the game's"


def m_define(mod):
    edit(mod, "common/defines/valsora_game.lua", lambda t: t + "NDefines.NGame.VALSORA_NO_SUCH_DEFINE = 1\n")
    return "NDefines.NGame.VALSORA_NO_SUCH_DEFINE is not one of the game's defines"


def m_earth_history(mod):
    next((mod / "history/countries").glob("GER - *.txt")).unlink()
    return "of Earth's tags have no history file"


def m_decision_stand_in(mod):
    edit(mod, "common/decisions/valsora_vanilla_stand_ins.txt",
         lambda t: re.sub(r"\n\t(\w+) = \{\n(\t\t[^\n]*\n)*?\t\}", "", t, count=1))
    return "vanilla decisions named by loaded files have no stand-in"


def m_event_stand_in(mod):
    edit(mod, "events/valsora_vanilla_event_stand_ins.txt",
         lambda t: re.sub(r"country_event = \{\n\tid = denmark_political_events\.3\n(\t[^\n]*\n)*?\}\n", "", t))
    return "event denmark_political_events.3 is fired but not defined"


def m_old_date(mod):
    edit(mod, "common/national_focus/generic.txt", lambda t: t.replace("2039.1.1", "1939.1.1", 1))
    return "common/national_focus/generic.txt: a date or year before 2036's century (1939.1.1)"


def m_tree_label(mod):
    edit(mod, "interface/countrytechtreeview.gui", lambda t: t.replace('text = "2036"', 'text = "1936"', 1))
    return "interface/countrytechtreeview.gui: a date or year before 2036's century (1936)"


def m_start_year(mod):
    edit(mod, "common/technologies/infantry.txt", lambda t: re.sub(r"start_year = 20(\d\d)", r"start_year = 19\1", t, count=1))
    return "common/technologies/infantry.txt: a date or year before 2036's century"


def m_bookmark(mod):
    bm = next((mod / "common/bookmarks").glob("*.txt")).relative_to(mod)
    edit(mod, bm, lambda t: t.replace("date = 2036.1.1.12", "date = 2036.6.1.12", 1))
    return "date 2036.6.1.12 is not the start date 2036.1.1.12"


def m_popularities(mod):
    edit(mod, rou_history(mod), lambda t: re.sub(r"(set_popularities = \{[^}]*?= )(\d+)", lambda m: m[1] + str(int(m[2]) + 5), t, count=1))
    return "set_popularities sums to 105, not 100"


def m_ruling_party(mod):
    edit(mod, rou_history(mod), lambda t: t.replace("ruling_party = neutrality", "ruling_party = monarchism", 1))
    return "ruling_party = monarchism is not an ideology"


def m_trait(mod):
    edit(mod, "common/characters/ROU.txt", lambda t: t.replace("traits = { armor_officer }", "traits = { made_up_trait }", 1))
    return "corps_commander trait made_up_trait is not one of the base game's"


def m_advisor_slot(mod):
    edit(mod, "common/characters/valsora_leaders.txt", lambda t: t.rstrip().rstrip("}") + (
        "\tROU_mutant_advisor = {\n\t\tname = ROU_mutant_advisor\n\t\tadvisor = {\n\t\t\tslot = court_jester\n"
        "\t\t\tidea_token = ROU_mutant_advisor\n\t\t\tcost = 100\n\t\t}\n\t}\n}\n"))
    return "character ROU_mutant_advisor: advisor without one of the game's slots"


def organisation(mod, name, include, tag):
    add_file(mod, f"common/military_industrial_organization/organizations/{name}.txt", (
        f"{name}_organization = {{\n\tinclude = {include}\n\ticon = GFX_idea_generic_tank_manufacturer_1\n"
        f"\tallowed = {{\n\t\toriginal_tag = {tag}\n\t}}\n}}\n").encode())


def m_company_include(mod):
    organisation(mod, "ROU_mutant_a", "generic_no_such_organization", "ROU")
    return "includes generic_no_such_organization, which is not one of the game's generic ones"


def m_company_tag(mod):
    organisation(mod, "ROU_mutant_b", "generic_medium_tank_organization", "XQZ")
    return "organisation ROU_mutant_b_organization is for XQZ, which is not a country in the mod"


def m_company_loc(mod):
    organisation(mod, "ROU_mutant_c", "generic_medium_tank_organization", "ROU")
    return "organisation ROU_mutant_c_organization has no localisation"


def concern(mod, name, trait):
    add_file(mod, f"common/ideas/{name}.txt", (
        f"ideas = {{\n\tindustrial_concern = {{\n\t\t{name} = {{\n\t\t\tpicture = generic_industrial_concern_1\n"
        f"\t\t\tallowed = {{ original_tag = ROU }}\n\t\t\tcost = 150\n\t\t\tremoval_cost = 10\n"
        f"\t\t\ttraits = {{ {trait} }}\n\t\t}}\n\t}}\n}}\n").encode())


def m_concern_trait(mod):
    concern(mod, "ROU_mutant_concern", "no_such_concern_trait")
    return "idea ROU_mutant_concern's trait no_such_concern_trait is not one of the game's"


def m_idea_loc(mod):
    concern(mod, "ROU_mutant_bank", "central_bank")
    return "idea ROU_mutant_bank has no localisation"


def m_skill_range(mod):
    edit(mod, "common/characters/ROU.txt", lambda t: t.replace("\t\t\tattack_skill = 4\n", "\t\t\tattack_skill = 12\n", 1))
    return "character ROU_serelle_cahun: corps_commander attack_skill = 12 is out of range"


def m_skill_kind(mod):
    edit(mod, "common/characters/ROU.txt", lambda t: t.replace("\t\t\tlogistics_skill = 3\n", "\t\t\tcoordination_skill = 3\n", 1))
    return "character ROU_serelle_cahun: corps_commander has coordination_skill, not one of its kind's stats"


def m_recruit_unknown(mod):
    edit(mod, rou_history(mod), lambda t: t.replace("recruit_character = ROU_roland_cahun", "recruit_character = ROU_roland_cahun\nrecruit_character = ROU_no_such_person", 1))
    return "recruits unknown character ROU_no_such_person"


def m_prerequisite(mod):
    edit(mod, "common/national_focus/rouental.txt", lambda t: t.replace("prerequisite = { focus = ROU_parasites_rude }", "prerequisite = { focus = ROU_no_such_focus }", 1))
    return "ROU_no_such_focus is referenced but is not a focus in the tree"


def m_state_loc(mod):
    edit(mod, "localisation/english/valsora_l_english.yml", lambda t: re.sub(r"\n VAL_STATE_1:0 \"[^\"]*\"", "", t, count=1))
    return "state name VAL_STATE_1 has no localisation"


def m_no_bom(mod):
    edit_bytes(mod, "localisation/english/valsora_l_english.yml", lambda b: b[3:] if b.startswith(b"\xef\xbb\xbf") else b)
    return "valsora_l_english.yml must be UTF-8 with BOM"


def m_decision_loc(mod):
    edit(mod, "localisation/english/valsora_l_english.yml", lambda t: re.sub(r"\n ROU_test_long_event:0 \"[^\"]*\"", "", t, count=1))
    return "decision ROU_test_long_event has no localisation"


def m_trigger_for(mod):
    edit(mod, "common/decisions/valsora_test_events.txt", lambda t: t.replace("state_event = { id = valsora_test.3 trigger_for = controller }", "state_event = { id = valsora_test.3 }", 1))
    return "is fired without trigger_for: no country would get it"


def m_scripted_effect(mod):
    edit(mod, "common/scripted_effects/valsora_opinion_effects.txt", lambda t: t.replace("valsora_reibonnaise_opinions = {", "valsora_reibonnaise_opinions_gone = {", 1))
    return "scripted effect valsora_reibonnaise_opinions is used but not defined"


def m_descriptor(mod):
    edit(mod, "descriptor.mod", lambda t: t.replace('replace_path="history/units"\n', "", 1))
    return "descriptor.mod and the launcher .mod have different replace_path lines"


def m_war_goal(mod):
    edit(mod, "common/national_focus/rouental.txt", lambda t: re.sub(r"(type = annex_everything\s+target = )CRD", r"\1XQZ", t, count=1))
    return "a war goal or effect targets XQZ, which is not a country in the mod"


def m_faction_template(mod):
    edit(mod, rou_history(mod), lambda t: t.replace("create_faction_from_template = faction_template_reibonnaise_association", "create_faction_from_template = faction_template_no_such", 1))
    return "creates a faction from unknown template faction_template_no_such"


def m_gui_sprite(mod):
    gui = next((mod / "interface").glob("valsora_superevent*.gui")).relative_to(mod)
    edit(mod, gui, lambda t: t.replace('spriteType = "GFX_', 'spriteType = "GFX_valsora_no_such_', 1))
    return "GFX_valsora_no_such_"


def m_texture_missing(mod):
    (mod / "gfx/leaders/VAL/ROU_mahaut_vi.dds").unlink()
    return "points at missing gfx/leaders/VAL/ROU_mahaut_vi.dds"


def m_minimap(mod):
    (mod / "gfx/minimap/minimap.dds").unlink()
    return "gfx/minimap/minimap.dds missing"


def m_globe(mod):
    (mod / "gfx/interface/world_tension_icon.dds").unlink()
    return "world_tension_icon.dds missing: the world tension globe would show vanilla's Earth"


def m_case_clash(mod):
    add_file(mod, "gfx/flags/rou.tga", (mod / "gfx/flags/ROU.tga").read_bytes())
    return "are the same file on Windows (case)"


def m_ascii_name(mod):
    add_file(mod, "gfx/flags/Côte.tga", (mod / "gfx/flags/ROU.tga").read_bytes())
    return "file names must be ASCII"


def m_font_letter(mod):
    edit(mod, "localisation/english/valsora_l_english.yml", lambda t: t.rstrip("\n") + '\n VAL_FONT_TEST:0 "\u01c4"\n')
    return "(U+01C4) in valsora_l_english.yml is in no font"


def m_map_letter(mod):
    """a letter the other fonts have but the map font doesn't, in a country's name"""
    edit(mod, "localisation/english/valsora_l_english.yml", lambda t: t.replace(' ROU:0 "Rouental"', ' ROU:0 "Rouent\u1ea1l"', 1))
    return "of ROU ('Rouent\u1ea1l') is not in the map font"


def m_mapfont_size(mod):
    """the map font's atlas grown past what the game loads (2026-10-16: no names on the map)"""
    import struct as _s
    edit_bytes(mod, "gfx/fonts/hoi_mapfont4.dds", lambda b: b[:12] + _s.pack("<I", 2048) + b[16:])
    return "gfx/fonts/hoi_mapfont4.dds is 2048 x 2048"


def m_song(mod):
    edit(mod, "events/valsora_superevents.txt", lambda t: t.replace('play_song = "valsora_gladiators"', 'play_song = "valsora_no_such_song"', 1))
    return "play_song valsora_no_such_song is not defined in music/"


BATCHES = {
    "map": [m_crlf, m_adjacency_end, m_building_row, m_ships_in_port, m_earth_map_file, m_weather_big, m_supply_node_sea,
            m_railway_apart, m_x_crossing, m_land_low, m_terrain_ocean],
    "history": [m_technology, m_module, m_equipment, m_idea, m_battalion, m_define, m_earth_history, m_popularities,
                m_ruling_party, m_recruit_unknown, m_faction_template, m_bookmark, m_descriptor],
    "content": [m_decision_stand_in, m_event_stand_in, m_old_date, m_tree_label, m_start_year, m_trait, m_advisor_slot,
                m_prerequisite, m_state_loc, m_decision_loc, m_trigger_for, m_scripted_effect, m_war_goal, m_song,
                m_company_include, m_company_tag, m_company_loc, m_concern_trait, m_idea_loc, m_skill_range, m_skill_kind],
    "files": [m_no_bom, m_gui_sprite, m_texture_missing, m_minimap, m_globe, m_case_clash, m_ascii_name,
              m_font_letter, m_map_letter, m_mapfont_size],
}


def run(name, mutations, tmp):
    """a hard-linked copy of the mod with these mutations; check_mod's output and the expected texts"""
    root = Path(tmp) / name
    root.mkdir()
    mod = root / SRC.name
    subprocess.run(["cp", "-al", str(SRC), str(mod)], check=True)
    outer = SRC.parent / f"{SRC.name}.mod"
    if outer.exists():
        shutil.copy(outer, root / outer.name)
    expect = {}
    for m in mutations:
        expect[m.__name__] = m(mod)
    r = subprocess.run([sys.executable, "scripts/check_mod.py", str(mod)], capture_output=True, text=True)
    shutil.rmtree(root)
    return r.stdout + r.stderr, expect


def main():
    if not (SRC / "descriptor.mod").exists():
        sys.exit(f"no built mod at {SRC}: build it first (sh scripts/run_all.sh)")
    t0 = time.time()
    clean = subprocess.run([sys.executable, "scripts/check_mod.py", str(SRC)], capture_output=True, text=True)
    if clean.returncode:
        sys.exit("check_mod.py fails on the build itself; fix that first:\n" + clean.stdout[-3000:])
    with tempfile.TemporaryDirectory(prefix="mutants_", dir=ROOT / "work") as tmp:
        with ThreadPoolExecutor(len(BATCHES)) as ex:
            results = dict(zip(BATCHES, ex.map(lambda kv: run(kv[0], kv[1], tmp), BATCHES.items())))
        missed, total = [], 0
        for batch, (out, expect) in results.items():
            for name, text in expect.items():
                total += 1
                if text not in out:
                    missed.append((batch, name, text))
        real = []
        for batch, name, text in missed:      # alone, in case another break in its batch hid it
            fn = next(m for m in BATCHES[batch] if m.__name__ == name)
            out, _ = run(f"alone_{name}", [fn], tmp)
            if text not in out:
                real.append((name, text, out[-1500:]))
    print(f"{total - len(real)} of {total} breaks caught ({len(missed) - len(real)} only when tried alone), "
          f"{time.time() - t0:.0f} s")
    for name, text, out in real:
        print(f"MISSED {name}: expected {text!r}\n{out}")
    sys.exit(1 if real else 0)


if __name__ == "__main__":
    main()
