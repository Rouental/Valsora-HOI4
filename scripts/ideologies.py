"""Valsora's ideologies: vanilla's four, renamed and recoloured, plus Theocratic.

The author's set (2026-09-29):
    democratic  Democratic     (unchanged)
    communism   Communist      (unchanged)
    fascism     Authoritarian  black
    neutrality  Monarchist     purple
    theocracy   Theocratic     white (new)
The internal keys stay vanilla's, so vanilla script that says fascism / neutrality keeps
working; only names and colours change. The ideology file is vanilla's
common/ideologies/00_ideologies.txt (source/ideologies/) with new colours and a theocracy
block modelled on neutrality. It overrides vanilla's file of the same name.
"""
import re
from pathlib import Path

import numpy as np
from PIL import Image

from imgio import write_dds

IDEOLOGIES = ("democratic", "fascism", "communism", "neutrality", "theocracy")
COLOURS = {"fascism": (20, 20, 20), "neutrality": (128, 48, 168), "theocracy": (238, 238, 238)}
SRC = Path("source/ideologies/vanilla_00_ideologies.txt")

THEOCRACY = """
	theocracy = {

		types = {

			theocrat = {
			}

			clerical_monarchism = {
			}

		}

		dynamic_faction_names = {
			"FACTION_NAME_THEOCRATIC_1"
			"FACTION_NAME_THEOCRATIC_2"
		}

		color = { COLOUR }

		war_impact_on_world_tension = 0.5
		faction_impact_on_world_tension = 0.25

		rules = {
			can_force_government = yes
			can_puppet = yes
			can_send_volunteers = yes
		}

		modifiers = {
			generate_wargoal_tension = 0.5
			join_faction_tension = 0.5
			lend_lease_tension = 0.5
			send_volunteers_tension = 0.5
			guarantee_tension = 0.5
			drift_defence_factor = 0.2
		}

		faction_modifiers = {
		}

		ai_neutral = yes
		ai_ideology_wanted_units_factor = 1.15

		ai_give_core_state_control_threshold = 10000
	}
"""

# replaces vanilla's names (localisation/english/replace/, so they win)
LOCALISATION = [
    ' fascism:0 "Authoritarian"',
    ' fascism_noun:0 "Authoritarianism"',
    ' fascism_desc:0 "Authoritarian Regime"',
    ' neutrality:0 "Monarchist"',
    ' neutrality_noun:0 "Monarchism"',
    ' neutrality_desc:0 "Monarchy"',
    ' theocracy:0 "Theocratic"',
    ' theocracy_noun:0 "Theocracy"',
    ' theocracy_desc:0 "Theocratic State"',
    ' theocracy_drift:0 "Theocratic Drift"',
    ' theocracy_acceptance:0 "Theocratic Acceptance"',
    ' theocrat:0 "Theocrat"',
    ' theocrat_desc:0 "Theocracy is a form of government in which the clergy rule in the name of God."',
    ' clerical_monarchism:0 "Clerical Monarchism"',
    ' clerical_monarchism_desc:0 "A monarchy that draws its right to rule from the church."',
    ' FACTION_NAME_THEOCRATIC_1:0 "The Holy League"',
    ' FACTION_NAME_THEOCRATIC_2:0 "The Covenant of the Faithful"',
]


def ideology_file():
    text = SRC.read_text()
    for ideo, (r, g, b) in COLOURS.items():
        if ideo == "theocracy":
            continue
        # the colour line inside this ideology's block
        start = text.index(f"\t{ideo} = {{")
        m = re.compile(r"color = \{[^}]*\}").search(text, start)
        text = text[:m.start()] + f"color = {{ {r} {g} {b} }}" + text[m.end():]
    r, g, b = COLOURS["theocracy"]
    block = THEOCRACY.replace("COLOUR", f"{r} {g} {b}")
    end = text.rstrip().rindex("}")  # the file's closing brace
    return text[:end] + block + "}\n"


POLITICS_GUI = Path("source/interface/vanilla_countrypoliticsview.gui")
# vanilla's party list has room for four 16 px rows; five fit at 13 px, one px higher
PARTY_ROW = 13
PARTY_GRID = ("position = { x = 260 y = 184 }\n\t\t\t\tsize = { width = 100%% height = 100%% }\n"
              "\t\t\t\tslotsize = { width = 230 height = 16 }")


def politics_gui():
    """Vanilla's politics view with the party list squeezed so five ideologies fit."""
    s = POLITICS_GUI.read_text(encoding="utf-8")
    if PARTY_GRID not in s:
        raise SystemExit(f"{POLITICS_GUI}: parties_grid not found as expected")
    return s.replace(PARTY_GRID, PARTY_GRID.replace("y = 184", "y = 183")
                     .replace("height = 16", f"height = {PARTY_ROW}"))


ICON = Path("source/ideologies/theocracy_placeholder.png")  # author's placeholder, to be replaced


def icon():
    """The 64x64 party icon for Theocratic: the author's placeholder picture, centre-cropped."""
    im = Image.open(ICON).convert("RGBA")
    w, h = im.size
    k = min(w, h)
    im = im.crop(((w - k) // 2, (h - k) // 2, (w - k) // 2 + k, (h - k) // 2 + k))
    return np.asarray(im.resize((64, 64), Image.LANCZOS))


def write_files(write, out):
    write("common/ideologies/00_ideologies.txt", ideology_file())
    path = out / "gfx/interface/ideologies/valsora_theocracy_group.dds"
    path.parent.mkdir(parents=True, exist_ok=True)
    write_dds(path, icon())
    write("interface/valsora_ideologies.gfx", "spriteTypes = {\n\tspriteType = {\n"
          '\t\tname = "GFX_ideology_theocracy_group"\n'
          '\t\ttexturefile = "gfx/interface/ideologies/valsora_theocracy_group.dds"\n\t}\n}\n')
    write("interface/countrypoliticsview.gui", politics_gui())
    write("localisation/english/replace/valsora_ideologies_l_english.yml",
          "l_english:\n" + "\n".join(LOCALISATION) + "\n", bom=True)
