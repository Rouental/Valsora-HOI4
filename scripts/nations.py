"""Hand-written content for individual nations, layered on the generated placeholders.

Aislada is the worked example: a leader with a custom portrait and its own focus tree.
Rouental (ROU) has per-ideology names, the Cahun leaders and its own focus tree.
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
    # Mahaut VI waits as theocratic party leader until "Accept Reality"
    "ROU": ["recruit_character = ROU_roland_cahun", "recruit_character = ROU_serelle_cahun",
            "recruit_character = ROU_mahaut_vi",
            # Rouental leads the Association of Reibonnaise States from the start
            "create_faction_from_template = faction_template_reibonnaise_association",
            *[f"add_to_faction = {t}" for t in ("GDN", "LST", "EVR", "HLR", "SGV", "LZC", "SGN")]],
}

# Country names while a given ideology rules: tag -> ideology -> (name, formal
# name, adjective). Ideologies left out use the placeholder name from build_mod.py.
IDEOLOGY_NAMES = {
    "ROU": {
        "democratic": ("Boring Rouental", "The Liberal and Functional Republic of Rouental",
                       "Rouentaise"),
        "fascism": ("Powerful Rouental", "The Absolute Iron Rouentaise Monarchy", "Rouentaise"),
        "communism": ("Shitty Rouental", "The Red Workers' Peoples' Republic of Rouental",
                      "Rouentaise"),
        "neutrality": ("Perfect Rouental", "The Serene and Beautiful Feudal Realm of Rouental",
                       "Rouentaise"),
        "theocracy": ("Holy Rouental", "The Holy Principality of Rouental", "Rouentaise"),
    },
}

# Map colour per government, for countries whose colour changes with it: tag ->
# ideology -> colour. Ideologies left out use the country's own colour. Each becomes a
# cosmetic tag TAG_<IDEOLOGY> (flag source/flags/TAG_<ideology>.png), set by an
# on_ruling_party_change on_action.
LOOKS = {
    # Rouental: monarchist and authoritarian keep the royal green (author)
    "ROU": {"democratic": (215, 174, 95), "communism": (128, 16, 16), "theocracy": (212, 175, 55)},
}

# Formal names (TAG_DEF, used in phrases like "war against ..."), from the author's
# flag sheet. Ideologies with their own names in IDEOLOGY_NAMES keep those.
FORMAL_NAMES = {
    "GDN": "the Free City of Guedelon",
    "EVR": "the County of Evriches",
    "SGN": "the County of Seigne",
    "LZC": "the Republic of Lanzerac",
    "LST": "the Duchy of Lustiana",
    "SGV": "the Duchy of Selgrave",
    "HLR": "the Principality of Hollier",
    "ROU": "the Holy Principality of Rouental",
    "CRD": "the Cardonian Kingdom",
}

LOCALISATION = [
    ' ROU_mahaut_vi:0 "Mahaut VI"',
    ' ROU_accept_reality:0 "Accept Reality"',
    ' ROU_accept_reality_desc:0 "The Cahuns bicker; the faithful pray. Mahaut VI answers the prayers."',
    ' VAL_reibonnaise_association:0 "The Association of Reibonnaise States"',
    ' ROU_plans_for_cardonia:0 "Plans for Cardonia"',
    ' ROU_plans_for_cardonia_desc:0 "A war goal against Cardonia, for testing."',
    ' ROU_serelle_cahun:0 "Serelle Cahun"',
    ' ROU_roland_cahun:0 "Roland Cahun"',
    ' ROU_focus:0 "Rouentaise Focus Tree"',
    ' ROU_parasites_polite:0 "Kick Out the Parasites (Polite)"',
    ' ROU_parasites_polite_desc:0 "The Cahuns are thanked for their service and shown the door."',
    ' ROU_kick_out_brother:0 "Kick Out Your Brother"',
    ' ROU_kick_out_brother_desc:0 "Serelle has waited long enough. Roland has not."',
    ' ROU_parasites_rude:0 "Kick Out the Parasites (Rudely)"',
    ' ROU_parasites_rude_desc:0 "The Cahuns are shown the door. Then the window."',
    ' ROU_steady_as_she_goes:0 "Steady As She Goes"',
    ' ROU_steady_as_she_goes_desc:0 "The Cahuns stay. Roland stays. Everything stays."',
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

ROU_CHARACTERS = """characters = {
	ROU_mahaut_vi = {
		name = ROU_mahaut_vi
		portraits = {
			civilian = {
				large = GFX_portrait_ROU_mahaut_vi
			}
		}
		country_leader = {
			ideology = theocrat
			expire = "1965.1.1.1"
			id = -1
		}
	}
	ROU_roland_cahun = {
		name = ROU_roland_cahun
		portraits = {
			civilian = {
				large = GFX_portrait_ROU_roland_cahun
			}
		}
		country_leader = {
			ideology = despotism
			expire = "1965.1.1.1"
			id = -1
		}
	}
	ROU_serelle_cahun = {
		name = ROU_serelle_cahun
		portraits = {
			civilian = {
				large = GFX_portrait_ROU_serelle_cahun
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
			hidden_effect = { valsora_superevent_ais_explode = yes }
			capital_scope = {
				add_manpower = -100
			}
			set_popularities = {
				democratic = 0
				fascism = 0
				communism = 100
				neutrality = 0
				theocracy = 0
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
ROU_FOCUS_TREE = """focus_tree = {
	id = ROU_focus

	country = {
		factor = 0
		modifier = {
			add = 10
			tag = ROU
		}
	}

	default = no
	continuous_focus_position = { x = 50 y = 1000 }

	initial_show_position = {
		focus = ROU_kick_out_brother
	}

	focus = {
		id = ROU_parasites_polite
		icon = GFX_goal_support_democracy
		x = 0
		y = 0
		cost = 10
		mutually_exclusive = { focus = ROU_kick_out_brother focus = ROU_steady_as_she_goes focus = ROU_parasites_rude focus = ROU_accept_reality }
		search_filters = { FOCUS_FILTER_POLITICAL }
		completion_reward = {
			hidden_effect = { valsora_superevent_rou_polite = yes }
			set_popularities = {
				democratic = 100
				fascism = 0
				communism = 0
				neutrality = 0
				theocracy = 0
			}
			set_politics = {
				ruling_party = democratic
				elections_allowed = yes
			}
			retire_character = ROU_roland_cahun
			retire_character = ROU_serelle_cahun
		}
	}

	focus = {
		id = ROU_kick_out_brother
		icon = GFX_goal_support_fascism
		x = 2
		y = 0
		cost = 10
		mutually_exclusive = { focus = ROU_parasites_polite focus = ROU_steady_as_she_goes focus = ROU_parasites_rude focus = ROU_accept_reality }
		search_filters = { FOCUS_FILTER_POLITICAL }
		completion_reward = {
			hidden_effect = { valsora_superevent_rou_brother = yes }
			set_popularities = {
				democratic = 0
				fascism = 100
				communism = 0
				neutrality = 0
				theocracy = 0
			}
			set_politics = {
				ruling_party = fascism
				elections_allowed = no
			}
			promote_character = ROU_serelle_cahun
			retire_character = ROU_roland_cahun
		}
	}

	focus = {
		id = ROU_parasites_rude
		icon = GFX_goal_support_communism
		x = 6
		y = 0
		cost = 10
		mutually_exclusive = { focus = ROU_parasites_polite focus = ROU_kick_out_brother focus = ROU_steady_as_she_goes focus = ROU_accept_reality }
		search_filters = { FOCUS_FILTER_POLITICAL }
		completion_reward = {
			hidden_effect = { valsora_superevent_rou_rude = yes }
			set_popularities = {
				democratic = 0
				fascism = 0
				communism = 100
				neutrality = 0
				theocracy = 0
			}
			set_politics = {
				ruling_party = communism
				elections_allowed = no
			}
			retire_character = ROU_roland_cahun
			retire_character = ROU_serelle_cahun
		}
	}

	# the fifth path: Mahaut VI takes the throne in the name of the church
	focus = {
		id = ROU_accept_reality
		icon = GFX_focus_generic_pope
		x = 8
		y = 0
		cost = 10
		mutually_exclusive = { focus = ROU_parasites_polite focus = ROU_kick_out_brother focus = ROU_steady_as_she_goes focus = ROU_parasites_rude }
		search_filters = { FOCUS_FILTER_POLITICAL }
		completion_reward = {
			hidden_effect = { valsora_superevent_rou_reality = yes }
			set_popularities = {
				democratic = 0
				fascism = 0
				communism = 0
				neutrality = 0
				theocracy = 100
			}
			set_politics = {
				ruling_party = theocracy
				elections_allowed = no
			}
			promote_character = ROU_mahaut_vi
			retire_character = ROU_roland_cahun
			retire_character = ROU_serelle_cahun
		}
	}

	# for testing wars: a war goal on Cardonia without justifying one
	focus = {
		id = ROU_plans_for_cardonia
		icon = GFX_goal_generic_major_war
		x = 11
		y = 0
		cost = 1
		search_filters = { FOCUS_FILTER_POLITICAL }
		available = { country_exists = CRD }
		completion_reward = {
			create_wargoal = {
				type = annex_everything
				target = CRD
			}
		}
	}

	focus = {
		id = ROU_steady_as_she_goes
		icon = GFX_focus_AUS_bring_back_the_habsburg_rule
		x = 4
		y = 0
		cost = 10
		mutually_exclusive = { focus = ROU_parasites_polite focus = ROU_kick_out_brother focus = ROU_parasites_rude focus = ROU_accept_reality }
		search_filters = { FOCUS_FILTER_POLITICAL }
		completion_reward = {
			hidden_effect = { valsora_superevent_rou_steady = yes }
			set_popularities = {
				democratic = 0
				fascism = 0
				communism = 0
				neutrality = 100
				theocracy = 0
			}
			set_politics = {
				ruling_party = neutrality
				elections_allowed = no
			}
			promote_character = ROU_roland_cahun
			retire_character = ROU_serelle_cahun
		}
	}
}
"""

# Factions that exist at game start, created from these templates in the leader's
# history. Goals, rules, manifest and icon are vanilla's (as in its generic template).
FACTION_TEMPLATES = """faction_template_reibonnaise_association = {
	name = VAL_reibonnaise_association
	manifest = faction_manifest_strength_in_unity
	icon = GFX_faction_logo_generic
	visible = {
		always = no
	}
	goals = {
		faction_goal_a_military_base
	}
	default_rules = {
		joining_rule_neighbors_only
		change_leader_rule_manpower
	}
}
"""

# Leader portraits: sprite name -> (source image, crop left, crop top, crop width,
# recolour). The crop keeps HOI4's 156x210 shape and is scaled down to it; each one
# becomes gfx/leaders/VAL/<name>.dds plus a GFX_portrait_<name> sprite.
PORTRAITS = {
    "ROU_mahaut_vi": ("source/portraits/mahaut_vi.jpg", 210, 40, 1000, None),
    "AIS_merlovich": ("source/portraits/merlovich_emu.png", 0, 95, 300, None),
    "AIS_communist_merlovich": ("source/portraits/merlovich_emu.png", 0, 95, 300, "red"),
    "ROU_serelle_cahun": ("source/portraits/serelle_cahun.png", 260, 90, 900, None),
    "ROU_roland_cahun": ("source/portraits/roland_cahun.png", 340, 200, 1100, None),
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
    write("common/factions/templates/valsora_factions.txt", FACTION_TEMPLATES)
    write("common/characters/AIS.txt", CHARACTERS)
    write("common/characters/ROU.txt", ROU_CHARACTERS)
    write("common/national_focus/rouental.txt", ROU_FOCUS_TREE)
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
