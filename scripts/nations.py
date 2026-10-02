"""Hand-written content for individual nations, layered on the generated placeholders.

Aislada is the worked example: a leader with a custom portrait and its own focus tree.
Rouental (ROU) has per-ideology names, the Cahun leaders and its own focus tree.
build_mod.py calls these hooks; add further nations the same way.
"""
import re

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
            *[f"add_to_faction = {t}" for t in ("GDN", "LST", "EVR", "HLR", "SGV", "LZC", "SGN")],
            # Rouental guarantees the Kingdom of Illiricium's independence (author,
            # 2026-10-01; it was a non-aggression pact at first)
            "diplomatic_relation = { country = KIL relation = guarantee active = yes }"],
    # the civil war: Brillagne and the Loyal Army are led by copies of Rouental's own
    # theocratic and authoritarian rulers (one character can't serve two countries)
    "BRL": ["recruit_character = BRL_mahaut_vi"],
    "RLA": ["recruit_character = RLA_serelle_cahun"],
    # the Bleacherist republics start as Illiricium's puppets (author, 2026-10-01)
    "ILR": [f"set_autonomy = {{ target = {t} autonomous_state = autonomy_puppet }}"
            for t in ("CTF", "ETR", "MZG")],
}

# Country names while a given ideology rules: tag -> ideology -> (name, formal
# name, adjective). Ideologies left out use the placeholder name from build_mod.py.
IDEOLOGY_NAMES = {
    "ROU": {  # author, 2026-09-30: "Rouental" on the map for every government
        "democratic": ("Rouental", "The Principality of Rouental", "Rouentaise"),
        "fascism": ("Rouental", "The Grand Principality of Rouental", "Rouentaise"),
        "communism": ("Rouental", "The People's Republic of Rouental", "Rouentaise"),
        "neutrality": ("Rouental", "The Sacred Principality of Rouental", "Rouentaise"),
        "theocracy": ("Rouental", "The Most Seran State of Rouental", "Rouentaise"),
    },
}

# Leaders with a generic portrait and a name from their culture's name list, so no
# leader's subtype is left to chance (author, 2026-09-30): tag -> subtypes. The first
# leads the country, which starts under that subtype's ideology; the rest lead other
# parties. Tags whose ruler is a hand-made character (HAND_MADE) only get party leaders.
LEADERS = {
    # the author's choices, 2026-09-30
    "CRD": ["enlightened_absolutism"],
    "EVR": ["feudalism"],
    "SGN": ["feudalism"],
    "HLR": ["despotism"],              # Absolute Monarchy
    "LST": ["elective_monarchy"],
    "SGV": ["oligarchism"],            # Oligarchy
    "LZC": ["lordly_republic"],
    "GDN": ["lordly_republic"],
    "LNT": ["conservatism"],
    "RMD": ["socialism"],              # Social Democracy
    "RST": ["revanchism"],
    "VLN": ["liberalism"],
    "ESD": ["constitutional_monarchism"],
    "CRZ": ["constitutional_monarchism"],
    "STO": ["despotism"],
    "PLH": ["prophetic_rule"],         # the Chosen Land, under messianic rule
    # 2026-10-01: Bleacherism (the author's new Authoritarian subtype); the royalists
    "ILR": ["bleacherism"],
    "CTF": ["bleacherism"],
    "ETR": ["bleacherism"],
    "MZG": ["bleacherism"],
    "KIL": ["legitimism"],
    "KRK": ["conservatism"],
    # the Rouentaise civil war factions (author, 2026-10-02)
    "CRP": ["despotism"],              # Absolute Monarchy
    "RLT": ["feudalism"],
    "MRC": ["oligarchism"],
    "VAI": ["feudalism"],
    "LCF": ["council_communism"],
    "FTH": ["holy_order"],
    "FRX": ["socialism"],             # Social Democracy
    # Rouental's democrats and communists, promoted by their focuses
    "ROU": ["constitutional_monarchism", "leninism"],
    # the continent placeholders: not chosen by the author, Monarchist as before
    **{t: ["despotism"] for t in ("NSC", "ARS", "SLT", "YAS", "USN", "ORI")},
}
HAND_MADE = {"ROU", "AIS", "BRL", "RLA"}  # rulers defined in the character files below
# the ruling ideology of hand-made rulers' countries, if not Monarchist
RULING = {"BRL": "theocracy", "RLA": "fascism"}

# The Rouentaise civil war (author, 2026-10-02). When Rouental's communists execute the
# Prince (focus ROU_execute_the_prince) these countries are released from the states
# named here (they hold cores on them from the start; the first is the capital), and
# all but the Alliance of the East declare war on Rouental.
CIVIL_WAR = {
    "BRL": ["Brillagne"],
    "CRP": ["Crépuscule", "Ténèbres", "Lyrié et Rivielle"],
    "RLT": ["Reliette", "Aureimontes", "Tuilerie", "Vinterre"],
    "MRC": ["Cylône", "Osgrande", "Aurillac-de-Ciel", "Coffrefort"],
    "RLA": ["Rêverie", "Rouental", "Saintiers", "Cournin", "Vendée"],
    "VAI": ["Vair", "Pavois", "Caux-Gautier"],
    "FTH": ["Hevique", "Avarre"],
}
# exist only through the civil war (author): no cores until the Prince is executed, so
# they can't be released any other way
CIVIL_WAR_ONLY = {"FTH", "RLA"}
# the Association's members other than Rouental, and what its neighbours take when the
# Prince is executed (author, 2026-10-02: "a more credible threat to the player")
ASSOCIATION = ("GDN", "LST", "EVR", "HLR", "SGV", "LZC", "SGN")
ANNEX = {"LST": ["Maïeul", "Serpette"], "HLR": ["Chirac"],
         "SGV": ["Moelle"]}  # Moelle, the north of the old Maïeul (2026-10-02)

# Extra cosmetic tags (name, formal name, adjective, map colour, flag in source/flags),
# set by script rather than by the ruling party
COSMETICS = {
    # communist Rouental after the Prince's execution (author, 2026-10-02)
    "ROU_REIBONNE": ("Reibonne", "The People's Republic of the Reibonne", "Reibonnaise",
                     (128, 16, 16), "ROU_REIBONNE.png"),
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
    "SGN": "the County of the Seigne",
    "LZC": "the Republic of Lanzerac",
    "LST": "the Duchy of Lustiana",
    "SGV": "the Duchy of Selgrave",
    "HLR": "the Principality of Hollier",
    "ROU": "The Sacred Principality of Rouental",
    # the civil war factions (author, 2026-10-02)
    "BRL": "the Holy State of Brillagne",
    "CRP": "the Principality of Crépuscule",
    "RLT": "the Grand Duchy of Reliette",
    "MRC": "the Alliance of the Marcher Lords",
    "RLA": "Her Majesty's Most Loyal Army",
    "VAI": "the Duchy of Vair",
    "LCF": "the Worker's Republic of Locus Felicitatis",
    "FTH": "the Faithful Children of the Goddess and Her Saint",
    "CRD": "the Cardonian Kingdom",
    # the author's, 2026-09-30
    "LNT": "the Republic of Placeholdros",
    "STO": "the Empire of Selto-Hamborn",
    "RMD": "the Romanoddlian Federation",  # author, 2026-09-30
    "VLN": "the Republic of Volinovia",
    "ESD": "the Kingdom of Estande",
    "CRZ": "the Principality of Coraliza",
    "PLH": "the Chosen Land of Placeholdria",
    # the author's, 2026-10-01
    "ILR": "the Senatorial Republic of Illiricium",
    "CTF": "the Bleacherist Republic of Côtefer",
    "ETR": "the Bleacherist Republic of Entroterra",
    "MZG": "the Bleacherist Republic of Mezzogiorno",
    "KIL": "the Kingdom of Illiricium",
}

LOCALISATION = [
    ' ROU_mahaut_vi:0 "Mahaut VI"',
    ' ROU_accept_reality:0 "Accept Reality"',
    ' ROU_accept_reality_desc:0 "The Cahuns bicker; the faithful pray. Mahaut VI answers the prayers."',
    ' VAL_reibonnaise_association:0 "The Association of Reibonnaise States"',
    ' VAL_alliance_of_the_vale:0 "The Alliance of the Vale"',
    ' ROU_plans_for_cardonia:0 "Plans for Cardonia"',
    ' ROU_plans_for_cardonia_desc:0 "A war goal against Cardonia, for testing."',
    ' ROU_serelle_cahun:0 "Serelle Cahun"',
    ' BRL_mahaut_vi:0 "Mahaut VI"',
    ' RLA_serelle_cahun:0 "Serelle Cahun"',
    ' ROU_roland_cahun:0 "Roland Cahun"',
    ' ROU_focus:0 "Rouentaise Focus Tree"',
    ' ROU_parasites_polite:0 "Kick Out the Parasites (Polite)"',
    ' ROU_parasites_polite_desc:0 "The Cahuns are thanked for their service and shown the door."',
    ' ROU_kick_out_brother:0 "Kick Out Your Brother"',
    ' ROU_kick_out_brother_desc:0 "Serelle has waited long enough. Roland has not."',
    ' ROU_parasites_rude:0 "Kick Out the Parasites (Rudely)"',
    ' ROU_parasites_rude_desc:0 "The Cahuns are shown the door. Then the window."',
    ' ROU_execute_the_prince:0 "Execute the Prince"',
    ' ROU_execute_the_prince_desc:0 "The committee has voted. Roland Cahun will not see another spring, and neither, perhaps, will the peace."',
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
			ideology = feudalism
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
			ideology = strongman_rule
			expire = "1965.1.1.1"
			id = -1
		}
	}
	# the same two women at the head of civil war factions
	BRL_mahaut_vi = {
		name = BRL_mahaut_vi
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
	RLA_serelle_cahun = {
		name = RLA_serelle_cahun
		portraits = {
			civilian = {
				large = GFX_portrait_ROU_serelle_cahun
			}
		}
		country_leader = {
			ideology = strongman_rule
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
			ideology = anarchist_communism
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
			promote_character = ROU_leader_constitutional_monarchism
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
			promote_character = ROU_leader_leninism
			# the communists move the capital to Carcarelle (author, 2026-10-02)
			set_capital = { state = @STATE:Carcarelle@ }
@RUDELY@
		}
	}

	# the communist path: the Prince is executed and the civil war begins (author,
	# 2026-10-01; how the war goes is still to come). ROU_civil_war marks it for later
	focus = {
		id = ROU_execute_the_prince
		icon = GFX_focus_spr_the_anti_fascist_workers_revolution
		x = 6
		y = 1
		cost = 10
		prerequisite = { focus = ROU_parasites_rude }
		search_filters = { FOCUS_FILTER_POLITICAL }
		completion_reward = {
			hidden_effect = { valsora_superevent_rou_civil_war = yes }
			set_country_flag = ROU_civil_war
			# the nation becomes the Reibonne (author, 2026-10-02)
			set_cosmetic_tag = ROU_REIBONNE
@CIVIL_WAR@
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
FACTION_TEMPLATES = """faction_template_alliance_of_the_vale = {
	name = VAL_alliance_of_the_vale
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
faction_template_reibonnaise_association = {
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
    # the author's capitals, 2026-09-30
    "capital:ROU": "Rêverie",
    "capital:GDN": "Guedelon",
    "capital:EVR": "Evriches",
    "capital:SGN": "Argent-sur-Seigne",
    "capital:HLR": "Grande Hollier",
    "capital:LZC": "Lanzerac",
    "capital:SGV": "Villerose",
    "capital:LST": "Tanière",
    "capital:FRX": "Fraternal City",  # 2026-10-01
}

# Capitals chosen by the author, as a pixel (x, y) inside the capital state; other
# countries get the sizeable state nearest the middle of their land.
CAPITALS = {
    "ROU": (660, 805),  # Rêverie, the small state the author drew for it ("Rouental 27")
    "CRD": (805, 670),  # Winterthorn (author, 2026-10-01)
    # the author's cities, made capitals (2026-10-01): the dots on Necessary Cities
    "CTF": (791, 1004),  # Venezzo
    "ILR": (868, 1084),  # Alqira
    "MZG": (894, 1153),  # Malin
    "ETR": (813, 1165),  # Prestozza
    "KIL": (920, 1165),  # Monte Gnolia
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


def reform(template, leader="HLR"):
    """The Association's members (without Rouental) in a faction led by Hollier."""
    t = "\t\t\t"
    return [f"{t}{leader} = {{",
            f"{t}\tcreate_faction_from_template = {template}",
            *[f"{t}\tif = {{ limit = {{ country_exists = {m} }} add_to_faction = {m} }}"
              for m in ASSOCIATION if m != leader],
            f"{t}}}"]


def rudely_effects():
    """The communists take power: the Association of Reibonnaise States casts Rouental
    out at once and re-forms under Hollier (author, 2026-10-02)."""
    t = "\t\t\t"
    return "\n".join([f"{t}# the Association of Reibonnaise States casts Rouental out",
                      f"{t}if = {{ limit = {{ is_faction_leader = yes }} dismantle_faction = yes }}",
                      f"{t}else_if = {{ limit = {{ is_in_faction = yes }} leave_faction = yes }}",
                      *reform("faction_template_reibonnaise_association")])


def civil_war_effects():
    """Execute the Prince: the factions break away; Lustiana and Hollier take the east,
    and the Association becomes the Alliance of the Vale (there is no effect to rename a
    faction, so Hollier dismantles it and founds the new one with the same members)."""
    t = "\t\t\t"
    lines = [f"{t}# Lustiana and Hollier take the east"]
    lines += [f"{t}{tag} = {{ transfer_state = @STATE:{nm}@ }}" for tag, names in ANNEX.items() for nm in names]
    lines += [f"{t}# the factions break away"]
    lines += [f"{t}@STATE:{nm}@ = {{ add_core_of = {tag} }}"
              for tag in CIVIL_WAR if tag in CIVIL_WAR_ONLY for nm in CIVIL_WAR[tag]]
    lines += [f"{t}release = {tag}" for tag in CIVIL_WAR]
    lines += [f"{t}{tag} = {{ declare_war_on = {{ target = ROU type = annex_everything }} }}"
              for tag in CIVIL_WAR]
    lines += [f"{t}# the Association becomes the Alliance of the Vale",
              f"{t}HLR = {{ if = {{ limit = {{ is_faction_leader = yes }} dismantle_faction = yes }} }}"]
    lines += reform("faction_template_alliance_of_the_vale")
    return "\n".join(lines)


def fill(text, state_ids):
    """Focus files name states as @STATE:<name>@ (ids shift when the map changes)."""
    def sub(m):
        if m.group(1) not in state_ids:
            raise SystemExit(f"nations: no state named {m.group(1)!r}")
        return str(state_ids[m.group(1)])
    text = text.replace("@CIVIL_WAR@", civil_war_effects()).replace("@RUDELY@", rudely_effects())
    return re.sub(r"@STATE:([^@]+)@", sub, text)


def rouental_division_names():
    """Rouental's division names (author's fief list, 2026-10-02): the Royal Host after
    the royal fiefs, the vassals' levies after their own fiefs."""
    import cultures
    f = cultures.fiefs()
    royal = f.pop("Royal Fiefs")
    host = ["Garde Royale"] + [f"Ost {cultures.noble(x)}" for x in royal]
    levies = [f"Levée {cultures.noble(x)}" for fs in f.values() for x in fs]

    def group(key, name, types, fallback, names):
        return "\n".join([f"{key} = {{", f'\tname = "{name}"', "\tfor_countries = { ROU }",
                          "\tcan_use = { always = yes }",
                          "\tdivision_types = { " + " ".join(f'"{t}"' for t in types) + " }",
                          f'\tfallback_name = "{fallback}"', "\tordered = {",
                          *[f'\t\t{i} = {{ "{n}" }}' for i, n in enumerate(names, 1)], "\t}", "}", ""])
    return (group("ROU_ROYAL_HOST", "The Royal Host", ["infantry", "cavalry", "light_armor", "medium_armor"],
                  "%d Compagnie d'Ordonnance", host)
            + group("ROU_LEVIES", "Vassal Levies", ["infantry", "cavalry", "motorized", "mountaineers"],
                    "%d Levée Féodale", levies))


def write_files(write, out, state_ids):
    """Write every nation-specific file into the mod folder. state_ids: state name -> id."""
    write("common/factions/templates/valsora_factions.txt", FACTION_TEMPLATES)
    write("common/characters/AIS.txt", CHARACTERS)
    write("common/characters/ROU.txt", ROU_CHARACTERS)
    write("common/national_focus/rouental.txt", fill(ROU_FOCUS_TREE, state_ids))
    write("common/national_focus/aislada.txt", FOCUS_TREE)
    write("common/units/names_divisions/ROU_names_divisions.txt", rouental_division_names())
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
