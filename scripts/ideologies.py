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


def icon():
    """A 64x64 party icon for Theocratic: a white cross on a gold disc."""
    s = 64
    y, x = np.mgrid[0:s, 0:s]
    d = np.hypot(y - s / 2 + 0.5, x - s / 2 + 0.5)
    img = np.zeros((s, s, 4), np.uint8)
    disc = d < s / 2 - 2
    img[disc] = (190, 150, 60, 255)
    img[(d >= s / 2 - 4) & disc] = (120, 90, 30, 255)
    cross = ((abs(x - s / 2) < 5) & (y > 12) & (y < 52)) | ((abs(y - 26) < 5) & (x > 18) & (x < 46))
    img[cross & disc] = (250, 250, 245, 255)
    return img


def write_files(write, out):
    write("common/ideologies/00_ideologies.txt", ideology_file())
    path = out / "gfx/interface/ideologies/valsora_theocracy_group.dds"
    path.parent.mkdir(parents=True, exist_ok=True)
    write_dds(path, icon())
    write("interface/valsora_ideologies.gfx", "spriteTypes = {\n\tspriteType = {\n"
          '\t\tname = "GFX_ideology_theocracy_group"\n'
          '\t\ttexturefile = "gfx/interface/ideologies/valsora_theocracy_group.dds"\n\t}\n}\n')
    write("localisation/english/replace/valsora_ideologies_l_english.yml",
          "l_english:\n" + "\n".join(LOCALISATION) + "\n", bom=True)
