"""Hand-written content for individual nations, layered on the generated placeholders.

Aislada is the worked example: a leader with a custom portrait and its own focus tree.
Nonscio (NSC) has per-ideology names and the Cahun leaders.
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
    # Roland leads the ruling non-aligned party at start; Serelle leads the fascists
    "NSC": ["recruit_character = NSC_roland_cahun", "recruit_character = NSC_serelle_cahun"],
}

# Country names while a given ideology rules: tag -> ideology -> (name, formal
# name, adjective). Ideologies left out use the placeholder name from build_mod.py.
IDEOLOGY_NAMES = {
    "NSC": {
        "democratic": ("Boring Rouental", "The Liberal and Functional Republic of Rouental",
                       "Rouentaise"),
        "fascism": ("Powerful Rouental", "The Absolute Iron Rouentaise Monarchy", "Rouentaise"),
        "communism": ("Shitty Rouental", "The Red Workers' Peoples' Republic of Rouental",
                      "Rouentaise"),
        "neutrality": ("Perfect Rouental", "The Serene and Beautiful Feudal Realm of Rouental",
                       "Rouentaise"),
    },
}

LOCALISATION = [
    ' NSC_serelle_cahun:0 "Serelle Cahun"',
    ' NSC_roland_cahun:0 "Roland Cahun"',
    ' NSC_focus:0 "Rouentaise Focus Tree"',
    ' NSC_parasites_polite:0 "Kick Out the Parasites (Polite)"',
    ' NSC_parasites_polite_desc:0 "The Cahuns are thanked for their service and shown the door."',
    ' NSC_kick_out_brother:0 "Kick Out Your Brother"',
    ' NSC_kick_out_brother_desc:0 "Serelle has waited long enough. Roland has not."',
    ' NSC_parasites_rude:0 "Kick Out the Parasites (Rudely)"',
    ' NSC_parasites_rude_desc:0 "The Cahuns are shown the door. Then the window."',
    ' NSC_steady_as_she_goes:0 "Steady As She Goes"',
    ' NSC_steady_as_she_goes_desc:0 "The Cahuns stay. Roland stays. Everything stays."',
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

NSC_CHARACTERS = """characters = {
	NSC_roland_cahun = {
		name = NSC_roland_cahun
		portraits = {
			civilian = {
				large = GFX_portrait_NSC_roland_cahun
			}
		}
		country_leader = {
			ideology = despotism
			expire = "1965.1.1.1"
			id = -1
		}
	}
	NSC_serelle_cahun = {
		name = NSC_serelle_cahun
		portraits = {
			civilian = {
				large = GFX_portrait_NSC_serelle_cahun
			}
		}
		country_leader = {
			ideology = fascism_ideology
			expire = "1965.1.1.1"
			id = -1
		}
	}
}
"""

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


# Rouental: four mutually exclusive political paths, in one row.
NSC_FOCUS_TREE = """focus_tree = {
	id = NSC_focus

	country = {
		factor = 0
		modifier = {
			add = 10
			tag = NSC
		}
	}

	default = no
	continuous_focus_position = { x = 50 y = 1000 }

	initial_show_position = {
		focus = NSC_kick_out_brother
	}

	focus = {
		id = NSC_parasites_polite
		icon = GFX_goal_support_democracy
		x = 0
		y = 0
		cost = 10
		mutually_exclusive = { focus = NSC_kick_out_brother focus = NSC_parasites_rude focus = NSC_steady_as_she_goes }
		search_filters = { FOCUS_FILTER_POLITICAL }
		completion_reward = {
			set_popularities = {
				democratic = 100
				fascism = 0
				communism = 0
				neutrality = 0
			}
			set_politics = {
				ruling_party = democratic
				elections_allowed = yes
			}
			retire_character = NSC_roland_cahun
			retire_character = NSC_serelle_cahun
		}
	}

	focus = {
		id = NSC_kick_out_brother
		icon = GFX_goal_support_fascism
		x = 2
		y = 0
		cost = 10
		mutually_exclusive = { focus = NSC_parasites_polite focus = NSC_parasites_rude focus = NSC_steady_as_she_goes }
		search_filters = { FOCUS_FILTER_POLITICAL }
		completion_reward = {
			set_popularities = {
				democratic = 0
				fascism = 100
				communism = 0
				neutrality = 0
			}
			set_politics = {
				ruling_party = fascism
				elections_allowed = no
			}
			promote_character = NSC_serelle_cahun
			retire_character = NSC_roland_cahun
		}
	}

	focus = {
		id = NSC_parasites_rude
		icon = GFX_goal_support_communism
		x = 6
		y = 0
		cost = 10
		mutually_exclusive = { focus = NSC_parasites_polite focus = NSC_kick_out_brother focus = NSC_steady_as_she_goes }
		search_filters = { FOCUS_FILTER_POLITICAL }
		completion_reward = {
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
			retire_character = NSC_roland_cahun
			retire_character = NSC_serelle_cahun
		}
	}

	focus = {
		id = NSC_steady_as_she_goes
		icon = GFX_focus_AUS_bring_back_the_habsburg_rule
		x = 4
		y = 0
		cost = 10
		mutually_exclusive = { focus = NSC_parasites_polite focus = NSC_parasites_rude focus = NSC_kick_out_brother }
		search_filters = { FOCUS_FILTER_POLITICAL }
		completion_reward = {
			set_popularities = {
				democratic = 0
				fascism = 0
				communism = 0
				neutrality = 100
			}
			set_politics = {
				ruling_party = neutrality
				elections_allowed = no
			}
			promote_character = NSC_roland_cahun
			retire_character = NSC_serelle_cahun
		}
	}
}
"""

# Leader portraits: sprite name -> (source image, crop left, crop top, crop width,
# recolour). The crop keeps HOI4's 156x210 shape and is scaled down to it; each one
# becomes gfx/leaders/VAL/<name>.dds plus a GFX_portrait_<name> sprite.
PORTRAITS = {
    "AIS_merlovich": ("source/portraits/merlovich_emu.png", 0, 95, 300, None),
    "AIS_communist_merlovich": ("source/portraits/merlovich_emu.png", 0, 95, 300, "red"),
    "NSC_serelle_cahun": ("source/portraits/serelle_cahun.png", 260, 90, 900, None),
    "NSC_roland_cahun": ("source/portraits/roland_cahun.png", 340, 200, 1100, None),
}

# Hand-picked victory point names. Key either a province id (ids follow the placeholder
# provinces and shift when the map is rebuilt) or "capital:TAG" for a country's
# capital city, which stays correct across rebuilds.
CITY_NAMES = {
    "capital:AIS": "The Great and Noble City of Merlovia",
}


def portrait(src, x0, y0, w):
    """Crop a 156:210 box and scale it to vanilla's 156x210 leader portrait size."""
    im = Image.open(src).convert("RGB")
    h = round(w * 210 / 156)
    crop = im.crop((x0, y0, x0 + w, y0 + h)).resize((156, 210), Image.LANCZOS)
    return np.dstack([np.asarray(crop), np.full((210, 156), 255, np.uint8)])


def redden(rgba):
    """The same portrait washed in revolutionary red: brightness kept, hue forced red."""
    lum = rgba[..., :3].astype(np.float32) @ np.array([0.299, 0.587, 0.114], np.float32)
    red = np.stack([np.clip(lum * 1.1 + 70, 0, 255), lum * 0.3, lum * 0.25], axis=-1)
    return np.dstack([red.round().astype(np.uint8), rgba[..., 3]])


def write_files(write, out):
    """Write every nation-specific file into the mod folder."""
    write("common/characters/AIS.txt", CHARACTERS)
    write("common/characters/NSC.txt", NSC_CHARACTERS)
    write("common/national_focus/rouental.txt", NSC_FOCUS_TREE)
    write("common/national_focus/aislada.txt", FOCUS_TREE)
    sprites = []
    for name, (src, x0, y0, w, tint) in PORTRAITS.items():
        rgba = portrait(src, x0, y0, w)
        if tint == "red":
            rgba = redden(rgba)
        path = out / f"gfx/leaders/VAL/{name}.dds"
        path.parent.mkdir(parents=True, exist_ok=True)
        write_dds(path, rgba)
        sprites.append(f'\tspriteType = {{\n\t\tname = "GFX_portrait_{name}"\n'
                       f'\t\ttexturefile = "gfx/leaders/VAL/{name}.dds"\n\t}}\n')
    write("interface/valsora_portraits.gfx", "spriteTypes = {\n" + "".join(sprites) + "}\n")
