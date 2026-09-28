"""Hand-written content for individual nations, layered on the generated placeholders.

Aislada is the worked example: a leader with a custom portrait and its own focus tree.
build_mod.py calls these hooks; add further nations the same way.
"""
import numpy as np
from PIL import Image

from imgio import write_dds

# extra lines appended to history/countries/<TAG> - <Name>.txt
HISTORY = {
    # recruit_character only works in history files, so Communist Merlovich is
    # recruited at game start too; he waits as communist party leader until "Explode"
    "AIS": ["recruit_character = AIS_merlovich", "recruit_character = AIS_communist_merlovich"],
}

LOCALISATION = [
    ' AIS_merlovich:0 "Merlovich"',
    ' AIS_communist_merlovich:0 "Communist Merlovich"',
    ' AIS_focus:0 "Aisladan Focus Tree"',
    ' AIS_nationstates_account:0 "Make a NationStates Account"',
    ' AIS_nationstates_account_desc:0 "Every great nation begins with a login."',
    ' AIS_become_cartographer:0 "Become Cartographer"',
    ' AIS_become_cartographer_desc:0 "Drawing the world is harder than ruling it."',
    ' AIS_explode:0 "Fucking Explode"',
    ' AIS_explode_desc:0 "It was always going to end like this. Merlovich returns, redder."',
]

CHARACTERS = """characters = {
	AIS_merlovich = {
		name = AIS_merlovich
		portraits = {
			civilian = {
				large = GFX_portrait_AIS_merlovich
			}
		}
		country_leader = {
			ideology = despotism
			expire = "1965.1.1.1"
			id = -1
		}
	}
	# who Merlovich becomes after the "Explode" focus
	AIS_communist_merlovich = {
		name = AIS_communist_merlovich
		portraits = {
			civilian = {
				large = GFX_portrait_AIS_communist_merlovich
			}
		}
		country_leader = {
			ideology = marxism
			expire = "1965.1.1.1"
			id = -1
		}
	}
}
"""

SPRITES = """spriteTypes = {
	spriteType = {
		name = "GFX_portrait_AIS_merlovich"
		texturefile = "gfx/leaders/AIS/Portrait_Aislada_Merlovich.dds"
	}
	spriteType = {
		name = "GFX_portrait_AIS_communist_merlovich"
		texturefile = "gfx/leaders/AIS/Portrait_Aislada_Communist_Merlovich.dds"
	}
}
"""

FOCUS_TREE = """focus_tree = {
	id = AIS_focus

	country = {
		factor = 0
		modifier = {
			add = 10
			tag = AIS
		}
	}

	default = no
	continuous_focus_position = { x = 50 y = 1000 }

	initial_show_position = {
		focus = AIS_nationstates_account
	}

	focus = {
		id = AIS_nationstates_account
		icon = GFX_goal_generic_political_pressure
		x = 0
		y = 0
		cost = 10
		search_filters = { FOCUS_FILTER_POLITICAL }
		completion_reward = {
			add_political_power = 25
		}
	}

	focus = {
		id = AIS_become_cartographer
		icon = GFX_goal_generic_demand_territory
		prerequisite = { focus = AIS_nationstates_account }
		x = 0
		y = 1
		cost = 10
		search_filters = { FOCUS_FILTER_POLITICAL }
		completion_reward = {
			add_stability = -0.5
		}
	}

	focus = {
		id = AIS_explode
		icon = GFX_focus_generic_communist
		prerequisite = { focus = AIS_become_cartographer }
		x = 0
		y = 2
		cost = 10
		search_filters = { FOCUS_FILTER_POLITICAL }
		completion_reward = {
			capital_scope = {
				add_manpower = -100
			}
			set_popularities = {
				democratic = 0
				fascism = 0
				communism = 100
				neutrality = 0
			}
			set_politics = {
				ruling_party = communism
				elections_allowed = no
			}
			promote_character = AIS_communist_merlovich
			retire_character = AIS_merlovich
		}
	}
}
"""


def portrait(src="source/merlovich_emu.png"):
    """156x210 leader portrait (vanilla's size), cropped around the emu's head."""
    im = Image.open(src).convert("RGB")
    w = 300
    h = round(w * 210 / 156)
    crop = im.crop((0, 95, w, 95 + h)).resize((156, 210), Image.LANCZOS)
    rgba = np.dstack([np.asarray(crop), np.full((210, 156), 255, np.uint8)])
    return rgba


def write_files(write, out):
    """Write every nation-specific file into the mod folder."""
    write("common/characters/AIS.txt", CHARACTERS)
    write("interface/valsora_portraits.gfx", SPRITES)
    write("common/national_focus/aislada.txt", FOCUS_TREE)
    path = out / "gfx/leaders/AIS/Portrait_Aislada_Merlovich.dds"
    path.parent.mkdir(parents=True, exist_ok=True)
    rgba = portrait()
    write_dds(path, rgba)
    write_dds(path.with_name("Portrait_Aislada_Communist_Merlovich.dds"), redden(rgba))


def redden(rgba):
    """The same portrait washed in revolutionary red: brightness kept, hue forced red."""
    lum = rgba[..., :3].astype(np.float32) @ np.array([0.299, 0.587, 0.114], np.float32)
    red = np.stack([np.clip(lum * 1.1 + 70, 0, 255), lum * 0.3, lum * 0.25], axis=-1)
    return np.dstack([red.round().astype(np.uint8), rgba[..., 3]])
