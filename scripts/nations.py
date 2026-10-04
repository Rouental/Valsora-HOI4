"""Hand-written content for individual nations, layered on the generated placeholders.

Aislada is the worked example: a leader with a custom portrait and its own focus tree.
Rouental (ROU) has per-ideology names, the Cahun leaders and its own focus tree.
build_mod.py calls these hooks; add further nations the same way.
"""
import re

import numpy as np
from PIL import Image

from imgio import write_dds

# Rouental's Royal Host (author, 2026-10-02): a few armoured and mechanised divisions
# and more motorised ones, veteran, fully equipped, with plenty of support. Technology
# names, tank modules and equipment were checked against vanilla 1.19's common files;
# tank designs exist twice, for the No Step Back tank designer and without it.
ROU_ARMY_HISTORY = [
    "set_technology = { infantry_weapons = 1 infantry_weapons1 = 1 tech_support = 1 tech_engineers = 1 "
    "tech_recon = 1 tech_maintenance_company = 1 tech_logistics_company = 1 tech_field_hospital = 1 "
    "tech_signal_company = 1 tech_trucks = 1 motorised_infantry = 1 mechanised_infantry = 1 "
    "gw_artillery = 1 interwar_artillery = 1 interwar_antiair = 1 radio = 1 }",
    'if = { limit = { NOT = { has_dlc = "No Step Back" } } '
    "set_technology = { gwtank = 1 basic_light_tank = 1 basic_medium_tank = 1 } }",
    'if = { limit = { has_dlc = "No Step Back" } '
    "set_technology = { gwtank_chassis = 1 basic_light_tank_chassis = 1 basic_medium_tank_chassis = 1 "
    "armor_tech_1 = 1 engine_tech_1 = 1 } "
    'create_equipment_variant = { name = "Char Royal" type = medium_tank_chassis_1 parent_version = 0 '
    "modules = { main_armament_slot = tank_small_cannon turret_type_slot = tank_medium_three_man_tank_turret "
    "suspension_type_slot = tank_bogie_suspension armor_type_slot = tank_riveted_armor "
    "engine_type_slot = tank_gasoline_engine special_type_slot_1 = tank_radio_1 } } }",
    # well supplied: a stockpile behind the host
    *[f"add_equipment_to_stockpile = {{ type = {e} amount = {n} producer = ROU }}" for e, n in (
        ("infantry_equipment_1", 3000), ("support_equipment_1", 600), ("motorized_equipment_1", 1500),
        ("mechanized_equipment_1", 400), ("artillery_equipment_1", 500), ("anti_air_equipment_1", 300))],
    # last, once the techs and the tank design exist
    'set_oob = "ROU_1936"',
]

# The Royal Host's order of battle: (template, division count, state name to stand in)
ROU_TEMPLATES = {
    "Division Blindée de la Garde": dict(
        regiments=[["medium_armor", "medium_armor"], ["medium_armor", "medium_armor"], ["mechanized", "mechanized"]],
        support=["engineer", "recon", "maintenance_company", "signal_company", "field_hospital"]),
    "Division Mécanisée Royale": dict(
        regiments=[["mechanized", "mechanized"], ["mechanized", "mechanized"], ["medium_armor", "medium_armor"]],
        support=["engineer", "recon", "anti_air", "signal_company", "logistics_company"]),
    "Division Motorisée Royale": dict(
        regiments=[["motorized", "motorized", "motorized"], ["motorized", "motorized", "motorized"]],
        support=["engineer", "recon", "artillery", "anti_air", "logistics_company"]),
}
ROU_HOST = [("Division Blindée de la Garde", 2, "Rouental"),
            ("Division Mécanisée Royale", 1, "Saintiers"), ("Division Mécanisée Royale", 1, "Cournin"),
            ("Division Motorisée Royale", 2, "Rêverie"), ("Division Motorisée Royale", 2, "Charmas"),
            ("Division Motorisée Royale", 2, "Rochemont"), ("Division Motorisée Royale", 2, "Vendée")]

# The Feudal Army national spirit (author, 2026-10-02; harshness not final): the price
# of the levy system (docs/ROUENTAL_ARMY.md), with the author's placeholder picture
FEUDAL_ARMY = """ideas = {
	country = {
		ROU_feudal_army = {
			picture = ROU_feudal_army
			allowed = { always = no }
			removal_cost = -1
			modifier = {
				conscription_factor = -0.8
				training_time_factor = 1.0
				political_power_factor = -0.1
				stability_factor = -0.05
			}
		}
	}
}
"""


def rouental_oob(state_vp):
    """history/units/ROU_1936.txt: the templates, then the divisions, named from the
    Royal Host's division names. state_vp: state name -> province id to stand in."""
    out = []
    for name, t in ROU_TEMPLATES.items():
        regs = [f"\t\t{u} = {{ x = {x} y = {y} }}" for x, col in enumerate(t["regiments"]) for y, u in enumerate(col)]
        sup = [f"\t\t{u} = {{ x = 0 y = {y} }}" for y, u in enumerate(t["support"])]
        out += ["division_template = {", f'\tname = "{name}"', "\tdivision_names_group = ROU_ROYAL_HOST",
                "\tregiments = {", *regs, "\t}", "\tsupport = {", *sup, "\t}", "}", ""]
    out += ["units = {"]
    k = 0
    for name, n, state in ROU_HOST:
        if state not in state_vp:
            raise SystemExit(f"nations.ROU_HOST: no state named {state!r}")
        for _ in range(n):
            k += 1
            out += ["\tdivision = {", f"\t\tdivision_name = {{ is_name_ordered = yes name_order = {k} }}",
                    f"\t\tlocation = {state_vp[state]}", f'\t\tdivision_template = "{name}"',
                    "\t\tstart_experience_factor = 0.6", "\t\tstart_equipment_factor = 1.0",
                    # unset, the manpower comes out of the pool, which the Feudal Army keeps tiny
                    "\t\tstart_manpower_factor = 1.0", "\t}"]
    return "\n".join(out + ["}", ""])


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
            # the Feudal Army and the Royal Host (author, 2026-10-02; docs/ROUENTAL_ARMY.md)
            "add_ideas = ROU_feudal_army",
            *ROU_ARMY_HISTORY,
            # Rouental guarantees the Kingdom of Illiricium's independence (author,
            # 2026-10-01; it was a non-aggression pact at first)
            "diplomatic_relation = { country = KIL relation = guarantee active = yes }"],
    # the civil war: Brillagne and the Loyal Army are led by copies of Rouental's own
    # theocratic and authoritarian rulers (one character can't serve two countries)
    "BRL": ["recruit_character = BRL_mahaut_vi"],
    "RLA": ["recruit_character = RLA_serelle_cahun"],
    # Normania is Anglost's dominion (author, 2026-10-04)
    "AGL": ["set_autonomy = { target = NRM autonomous_state = autonomy_dominion }"],
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
    # south of Estande (author, 2026-10-04)
    "NPL": ["stalinism"],             # Party Centralism
    "SPL": ["liberalism"],
    "AGL": ["constitutional_monarchism"],
    "NRM": ["constitutional_monarchism"],
    "DRM": ["despotism"],             # Absolute Monarchy
    "SSA": ["council_communism"],
    "GRD": ["enlightened_absolutism"],
    # 2026-10-04, later (author)
    "WRS": ["revanchism"],
    "TRC": ["liberalism"],
    "CSC": ["anarchist_communism"],   # Anarcho-Communism
    "SCZ": ["constitutional_monarchism"],
    "DNL": ["elective_monarchy"],
    "THD": ["megacorporation"],
    # Rouental's democrats and communists, promoted by their focuses
    "ROU": ["constitutional_monarchism", "leninism"],
    # the continent placeholders: not chosen by the author, Monarchist as before
    **{t: ["despotism"] for t in ("NSC", "ARS", "SLT", "YAS", "USN", "ORI")},
}
HAND_MADE = {"ROU", "AIS", "BRL", "RLA"}  # rulers defined in the character files below

# Generated rulers the author has named and drawn: character id -> (name, portrait sprite);
# the portraits are in PORTRAITS
NAMED_LEADERS = {
    "ILR_leader_bleacherism": ("Ema Milize", "GFX_portrait_ILR_ema_milize"),  # author, 2026-10-02
}
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

# The Reibonnaise nations (author, 2026-10-02): +20 opinion of each other for their
# historical ties, except while one of them is communist, and -20 opinion of every
# communist country ("it's against their religion"). Opinions are re-set at game start
# and on every change of government, by the scripted effect below.
REIBONNAISE = ("ROU",) + ASSOCIATION
_IS_REIB = "OR = { " + " ".join(f"tag = {t}" for t in REIBONNAISE) + " }"
OPINION_MODIFIERS = """opinion_modifiers = {
	valsora_reibonnaise_ties = {
		value = 20
	}
	valsora_against_communism = {
		value = -20
	}
}
"""
OPINION_EFFECTS = f"""# Re-sets the Reibonnaise opinion modifiers (nations.REIBONNAISE) for every pair
valsora_reibonnaise_opinions = {{
	every_country = {{
		limit = {{ {_IS_REIB} }}
		every_other_country = {{
			PREV = {{
				remove_opinion_modifier = {{ target = PREV modifier = valsora_reibonnaise_ties }}
				remove_opinion_modifier = {{ target = PREV modifier = valsora_against_communism }}
			}}
			if = {{
				limit = {{ PREV = {{ NOT = {{ has_government = communism }} }} }}
				if = {{
					limit = {{ has_government = communism }}
					PREV = {{ add_opinion_modifier = {{ target = PREV modifier = valsora_against_communism }} }}
				}}
				else_if = {{
					limit = {{ {_IS_REIB} }}
					PREV = {{ add_opinion_modifier = {{ target = PREV modifier = valsora_reibonnaise_ties }} }}
				}}
			}}
		}}
	}}
}}
"""
# The AI wants to stay allied with its Reibonnaise neighbours while neither is communist
# (Lanzerac and Guedelon left the Association at once, 2026-10-02)
AI_STRATEGY = "".join(f"""VAL_reibonnaise_{a}_{b} = {{
	allowed = {{ original_tag = {a} }}
	enable = {{ country_exists = {b} NOT = {{ has_government = communism }} {b} = {{ NOT = {{ has_government = communism }} }} }}
	abort = {{ OR = {{ NOT = {{ country_exists = {b} }} has_government = communism {b} = {{ has_government = communism }} }} }}
	ai_strategy = {{ type = alliance id = "{b}" value = 200 }}
	ai_strategy = {{ type = befriend id = "{b}" value = 100 }}
}}
""" for a in REIBONNAISE for b in REIBONNAISE if a != b)

# Starting popularities other than the even mix. A faction member needs 30 % support
# for its leader's ideology (IDEOLOGY_JOIN_FACTION_MIN_LEVEL), so the two Lordly
# Republics in the monarchist Association keep their monarchists strong
POPULARITIES = {t: {"democratic": 40, "neutrality": 30, "fascism": 10, "communism": 10, "theocracy": 10}
                for t in ("LZC", "GDN")}

# Every other country's starting army (author, 2026-10-02: "something according to their
# size"): infantry divisions, about one per six states, 2 to 24
GENERIC_ARMY_TECH = ("set_technology = { infantry_weapons = 1 tech_support = 1 tech_engineers = 1 "
                     "tech_recon = 1 gw_artillery = 1 }")


def generic_oob(tag, vps):
    """history/units/<tag>_1936.txt: vps are the victory point provinces of the
    country's states, capital first."""
    n = max(2, min(24, round(len(vps) / 6) + 2))
    out = ["division_template = {", '\tname = "Infantry Division"', "\tregiments = {",
           *[f"\t\tinfantry = {{ x = {x} y = {y} }}" for x in range(3) for y in range(3) if (x, y) != (2, 2)],
           "\t\tartillery_brigade = { x = 3 y = 0 }", "\t}",
           "\tsupport = {", "\t\tengineer = { x = 0 y = 0 }", "\t\trecon = { x = 0 y = 1 }", "\t}", "}", "",
           "units = {"]
    for k in range(n):
        out += ["\tdivision = {", f"\t\tdivision_name = {{ is_name_ordered = yes name_order = {k + 1} }}",
                f"\t\tlocation = {vps[k % len(vps)]}", '\t\tdivision_template = "Infantry Division"',
                "\t\tstart_experience_factor = 0.2", "\t\tstart_equipment_factor = 1.0",
                "\t\tstart_manpower_factor = 1.0", "\t}"]
    return "\n".join(out + ["}", ""])

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
    # 2026-10-04, the author's
    "NPL": "the Worker's State of Pollana",
    "SPL": "the Most Serene Republic of South Pollana",
    "AGL": "the Kingdom of Anglost",
    "NRM": "the Principality of Normania",
    "DRM": "the Pangolin Empire of Dremaur",
    "SSA": "the People's Republic of San Sierra",
    "GRD": "the Duchy of Guardana",
    "WRS": "the Republic of Wersh",
    "TRC": "the Democratic Republic of Troc",
    "CSC": "the United Forests of Cascadia",
    "SCZ": "the Kingdom of Sicilianzo",
    "DNL": "the Kingdom of Danelaw-Scandinavia",
    "THD": "Thorian Dynamics",
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
    ' ROU_feudal_army:0 "Feudal Army"',
    ' ROU_feudal_army_desc:0 "Rouental fights as it always has: a small, superbly equipped royal host, swelled in war by the levies its vassals owe the crown. Few men answer a recruiting sergeant here, and none train quickly; but the banners can be called."',
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
    ' AIS_merlovich:0 "The Great Merlovich"',  # author, 2026-10-04
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
			army = {
				large = GFX_portrait_ROU_serelle_cahun
			}
		}
		country_leader = {
			ideology = strongman_rule
			expire = "1965.1.1.1"
			id = -1
		}
		# a general from the start (author, 2026-10-02); the communist path retires her
		corps_commander = {
			traits = { armor_officer }
			skill = 4
			attack_skill = 4
			defense_skill = 2
			planning_skill = 3
			logistics_skill = 3
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
			army = {
				large = GFX_portrait_ROU_serelle_cahun
			}
		}
		country_leader = {
			ideology = strongman_rule
			expire = "1965.1.1.1"
			id = -1
		}
		# a general from the start (author, 2026-10-02); the communist path retires her
		corps_commander = {
			traits = { armor_officer }
			skill = 4
			attack_skill = 4
			defense_skill = 2
			planning_skill = 3
			logistics_skill = 3
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
			remove_country_leader_role = { character = ROU_serelle_cahun ideology = strongman_rule }  # stays a general
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
			remove_country_leader_role = { character = ROU_serelle_cahun ideology = strongman_rule }  # stays a general
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
			remove_country_leader_role = { character = ROU_serelle_cahun ideology = strongman_rule }  # stays a general
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
    "ILR_ema_milize": ("source/portraits/ema_milize.png", 2, 0, 237, None),
}

# Hand-picked victory point names. Key either a province id (ids follow the placeholder
# provinces and shift when the map is rebuilt) or "capital:TAG" for a country's
# capital city, which stays correct across rebuilds.
CITY_NAMES = {
    # "capital:AIS" was "The Great and Noble City of Merlovia" until the author named
    # Aislada's capital Hirane on the Cities layer (2026-10-04)
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
    # 2026-10-04: Sanhueza, and Hirane inside the circle the author drew on Aislada
    "SSA": (928, 1249),
    "AIS": (1838, 1313),
    # 2026-10-04, later: Markovograd (author) and Fraternal City, now dots on the map
    "KRK": (1156, 692),
    "FRX": (1024, 1130),
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
    the royal fiefs, the vassals' levies after their own fiefs. Every ordered name
    must hold %d (vanilla's rule), so they read "3e Levée de Beaufort"."""
    import cultures
    f = cultures.fiefs()
    royal = f.pop("Royal Fiefs")
    host = ["%de Garde Royale"] + [f"%de Ost {cultures.noble(x)}" for x in royal]
    levies = [f"%de Levée {cultures.noble(x)}" for fs in f.values() for x in fs]

    def group(key, name, types, fallback, names):
        return "\n".join([f"{key} = {{", f'\tname = "{name}"', "\tfor_countries = { ROU }",
                          "\tcan_use = { always = yes }",
                          "\tdivision_types = { " + " ".join(f'"{t}"' for t in types) + " }",
                          f'\tfallback_name = "{fallback}"', "\tordered = {",
                          *[f'\t\t{i} = {{ "{n}" }}' for i, n in enumerate(names, 1)], "\t}", "}", ""])
    return (group("ROU_ROYAL_HOST", "The Royal Host", ["infantry", "cavalry", "light_armor", "medium_armor"],
                  "%de Compagnie d'Ordonnance", host)
            + group("ROU_LEVIES", "Vassal Levies", ["infantry", "cavalry", "motorized", "mountaineers"],
                    "%de Levée Féodale", levies))


def write_files(write, out, state_ids, state_vp):
    """Write every nation-specific file into the mod folder. state_ids: state name -> id;
    state_vp: state name -> its victory point province."""
    write("common/factions/templates/valsora_factions.txt", FACTION_TEMPLATES)
    write("common/characters/AIS.txt", CHARACTERS)
    write("common/characters/ROU.txt", ROU_CHARACTERS)
    write("common/national_focus/rouental.txt", fill(ROU_FOCUS_TREE, state_ids))
    write("common/national_focus/aislada.txt", FOCUS_TREE)
    # UTF-8 with BOM, like vanilla's files of these kinds (the names have accents)
    write("common/units/names_divisions/ROU_names_divisions.txt", rouental_division_names(), bom=True)
    write("history/units/ROU_1936.txt", rouental_oob(state_vp), bom=True)
    write("common/ideas/valsora_ideas.txt", FEUDAL_ARMY)
    write("common/opinion_modifiers/valsora_opinion_modifiers.txt", OPINION_MODIFIERS)
    write("common/scripted_effects/valsora_opinion_effects.txt", OPINION_EFFECTS)
    write("common/ai_strategy/valsora_reibonnaise.txt", AI_STRATEGY)
    pic = Image.open("source/ideologies/theocracy_placeholder.png").convert("RGBA")
    side = min(pic.size)
    pic = pic.crop(((pic.width - side) // 2, (pic.height - side) // 2,
                    (pic.width + side) // 2, (pic.height + side) // 2)).resize((64, 64), Image.LANCZOS)
    path = out / "gfx/interface/ideas/ROU_feudal_army.dds"
    path.parent.mkdir(parents=True, exist_ok=True)
    write_dds(path, np.asarray(pic))
    write("interface/valsora_ideas.gfx", 'spriteTypes = {\n\tspriteType = {\n\t\tname = "GFX_idea_ROU_feudal_army"\n'
          '\t\ttexturefile = "gfx/interface/ideas/ROU_feudal_army.dds"\n\t}\n}\n')
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
