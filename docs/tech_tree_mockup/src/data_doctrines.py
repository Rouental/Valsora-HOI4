"""The doctrines (the game's 1.19 system): four folders of grand doctrines, tracks and subdoctrines, renamed for 2036.

A grand doctrine is chosen once (they exclude each other); each track holds one subdoctrine at a time, and every
subdoctrine has five mastery rewards (kept, renamed in a later step). The game's _no_lar copies (the same
subdoctrine without La Resistance) are folded into one entry.
"""
from common import folder

DOCTRINES = []


def doctrine_folder(key, name, game, icon, ledger, blurb, dlc=None):
    f = folder(key, name, game, "doctrine", icon, ledger, blurb, dlc=dlc, kind="doctrines")
    f.extra = {"grands": [], "tracks": []}
    DOCTRINES.append(f)
    return f


def G(f, gid, name, desc):
    f.extra["grands"].append({"id": gid, "name": name, "desc": desc, "replaces": "new" if gid.startswith("val_")
                              else gid})


def TRACK(f, tid, name):
    tr = {"id": tid, "name": name, "subs": []}
    f.extra["tracks"].append(tr)
    return tr


def S(tr, sid, name, desc, dlc=None, also=(), unl=None):
    tr["subs"].append({"id": sid, "name": name, "desc": desc, "dlc": dlc, "also": list(also),
                       "replaces": "new" if sid.startswith("val_") else sid, "unl": unl or []})


# ---- land ----------------------------------------------------------------------------------------------------
L = doctrine_folder("doc_land", "Land Doctrine", "land", "helmet", "army",
                    "How the army fights: one grand doctrine, then a subdoctrine in each of four tracks.")
G(L, "new_mobile_warfare", "Multi-Domain Operations",
  "Strike from land, air, sea, space and cyberspace at once, faster than the enemy can decide.")
G(L, "superior_firepower", "Precision Fires",
  "Find the target, hit it with one guided round: firepower measured in hits, not tonnes.")
G(L, "grand_battleplan", "Defence in Depth",
  "Layered positions, minefields and fires prepared in advance: the attacker bleeds before he arrives.")
G(L, "mass_assault", "People's War",
  "Numbers, endurance and the whole nation under arms: the army that cannot be exhausted.")
tr = TRACK(L, "infantry", "Infantry")
S(tr, "mobile_infantry", "Motorised Manoeuvre", "Infantry that moves fast on wheels and fights on the move.")
S(tr, "defensive_postures", "Prepared Defence", "Infantry that digs in deep and holds its ground.")
S(tr, "large_unit_tactics", "Brigade Combat Teams", "Self-contained brigades of all arms, concentrated at the point "
  "of main effort.")
S(tr, "assault_infantry", "Combined-Arms Infantry", "Drones, missiles and mortars down to the smallest unit.")
S(tr, "mounted_infantry", "Light Mobile Infantry", "Infantry on light vehicles and motorbikes that raids and "
  "disperses.", dlc="No Compromise, No Surrender")
S(tr, "commandos", "Small-Unit Excellence", "Small teams trained to fight alone and decide for themselves.",
  dlc="No Compromise, No Surrender")
S(tr, "irregulars", "Territorial Defence", "Volunteer and reserve battalions that defend their own towns.",
  dlc="No Compromise, No Surrender")
S(tr, "peoples_war", "People's Militia", "The whole people armed, the land traded for time.",
  dlc="No Compromise, No Surrender")
S(tr, "great_war_infantry", "Positional Warfare", "Trench lines, dugouts and drones overhead: the front of the "
  "2020s, frozen in place.")
tr = TRACK(L, "combat_support", "Fires & Combat Support")
S(tr, "fire_concentration", "Massed Fires", "Every gun and launcher on one target at once.")
S(tr, "anti_tank_frontline", "Anti-Armour Belts", "Missile teams and mines in depth across the tank routes.")
S(tr, "flying_batteries", "Shoot-and-Scoot", "Batteries that fire and move before the counter-fire lands.",
  dlc="No Compromise, No Surrender")
S(tr, "air_cavalry", "Air Assault", "Tiltrotors and helicopters carry the fight over the front.",
  dlc="Götterdämmerung")
S(tr, "mobile_recon_and_assault", "Drone-Led Reconnaissance", "Drones find the enemy; the division strikes what "
  "they find.", dlc="La Resistance (the game has a copy without it)", also=["mobile_recon_and_assault_no_lar"])
S(tr, "self_propelled_support", "Self-Propelled Fires", "Self-propelled guns that keep up with the tanks.",
  dlc="No Compromise, No Surrender")
S(tr, "siege_artillery", "Long-Range Strike", "Missiles and long-range guns against the enemy's rear.",
  dlc="Götterdämmerung")
S(tr, "field_engineering", "Combat Engineering", "Engineers who breach, bridge and fortify under fire.")
S(tr, "val_drone_saturation", "Drone Saturation", "Thousands of cheap drones over the front: nothing moves "
  "unseen, little moves at all.", unl=["FPV teams and reconnaissance: attack and recon higher; enemy movement "
  "slower in the division's zone"])
tr = TRACK(L, "armor", "Armour")
S(tr, "armored_spearhead", "Armoured Spearhead", "Tanks massed for the breakthrough and the deep pursuit.",
  dlc="La Resistance (the game has a copy without it)", also=["armored_spearhead_no_lar"])
S(tr, "armored_infantry_support", "Armoured Infantry Support", "Tanks spread among the infantry to lead every "
  "attack.")
S(tr, "streamlined_deployment", "Rapid Deployment", "Light armour that deploys fast, by air and by road.")
S(tr, "mobile_defense", "Mobile Defence", "Armoured reserves that counter-attack every penetration.")
S(tr, "armored_cavalry", "Armoured Cavalry", "Fast armour that scouts, screens and raids.",
  dlc="No Compromise, No Surrender; La Resistance", also=["armored_cavalry_no_lar"])
S(tr, "tank_destroyer_force", "Anti-Armour Hunters", "Missile vehicles and drones that hunt tanks.",
  dlc="No Compromise, No Surrender")
S(tr, "val_mech_warfare", "Mech Warfare", "How to fight with walkers: in the rubble, on the heights, where tanks "
  "can't follow.", unl=["armies with Assault Mechs and Light Walkers: attack, breakthrough and speed in rough "
  "terrain higher"], dlc="Needs the special project Assault Mech")
tr = TRACK(L, "operations", "Operations")
S(tr, "mission_type_tactics", "Mission Command", "Commanders told what to achieve, never how.")
S(tr, "last_stand", "Desperate Defence", "Hold every town to the last, and strike back when the enemy is spent.")
S(tr, "infiltration_tactics", "Infiltration", "Small units slip through the gaps at night and strike from behind.")
S(tr, "grand_assault", "Deliberate Offensive", "Months of preparation for one overwhelming blow.")
S(tr, "deep_battle", "Deep Operations", "Strike the whole depth of the enemy at once.",
  dlc="La Resistance (the game has a copy without it)", also=["deep_battle_no_lar"])
S(tr, "guerilla_war", "Insurgency", "Fight from among the people and make the occupation cost more than it is "
  "worth.", dlc="No Compromise, No Surrender")
S(tr, "rapid_domination", "Shock and Awe", "Precision strikes and speed that paralyse the enemy's command.")
S(tr, "expeditionary_warfare", "Expeditionary Operations", "Forces built to land and fight far from home.",
  dlc="No Compromise, No Surrender")
S(tr, "dispersed_operations", "Distributed Operations", "Small, spread-out units that drones and missiles can't "
  "catch together.", dlc="Thunder at Our Gates")
S(tr, "val_spectrum_warfare", "Spectrum Warfare", "Jam, spoof and hack before every attack: the enemy fights deaf "
  "and blind.", unl=["divisions with the signals and EW company: enemy coordination and air support lower"])

# ---- naval ---------------------------------------------------------------------------------------------------
N = doctrine_folder("doc_naval", "Naval Doctrine", "naval", "frigate", "navy",
                    "How the navy fights: one grand doctrine, then a subdoctrine in each of four tracks.")
G(N, "new_fleet_in_being", "Sea Control", "Surface action groups and missile ships that command the sea by force.")
G(N, "new_convoy_raiding", "Commerce War", "Submarines, mines and drones that strangle the enemy's trade.")
G(N, "new_base_strike", "Carrier Strike Groups", "Carriers and their air wings strike from beyond the horizon.")
tr = TRACK(N, "capital_ships", "Capital Ships")
S(tr, "line_of_battle", "Surface Action Groups", "Capital ships and escorts fight as one group.")
S(tr, "battlecruiser_supremacy", "Missile Battlecruisers", "Fast heavy ships with long-range missiles.")
S(tr, "armored_raiders", "Surface Raiders", "Heavy ships that hunt alone across the oceans.")
S(tr, "coastal_defence_fleet", "Coastal Defence Fleet", "Old and new heavy ships kept close to home.",
  dlc="No Compromise, No Surrender")
S(tr, "naval_gunfire_support", "Naval Fires Support", "Capital ships that support the army ashore.",
  dlc="No Compromise, No Surrender")
S(tr, "battleship_antiair_screen", "Air-Defence Flagships", "Heavy ships as the fleet's air and missile shield.",
  dlc="No Compromise, No Surrender")
S(tr, "val_arsenal_fleet", "Arsenal Fleet", "Arsenal ships fire on targets the whole fleet finds.",
  unl=["heavy ships: attack higher when the fleet has scouts and drones"])
tr = TRACK(N, "carriers", "Carriers")
S(tr, "carrier_battlegroups", "Carrier Battle Groups", "The carrier at the centre, every escort to defend it.")
S(tr, "floating_airfields", "Floating Airfields", "Carriers that keep their air wings flying round the clock.")
S(tr, "escort_carrier_support", "Light Carrier Escorts", "Light carriers that protect convoys.",
  dlc="No Compromise, No Surrender")
S(tr, "broad_naval_support", "Generalised Support", "Carriers that support every kind of task force.",
  dlc="No Compromise, No Surrender")
S(tr, "massed_carrier_fleet", "Massed Carriers", "Many carriers together: an air force at sea.")
S(tr, "light_task_forces", "Light Task Forces", "Small, fast groups built around a light carrier.",
  dlc="No Compromise, No Surrender")
S(tr, "val_drone_carrier_ops", "Drone Carrier Operations", "Carriers flying more drones than crewed aircraft.",
  unl=["carriers: more aircraft per deck, sortie efficiency higher"])
tr = TRACK(N, "screens", "Escorts")
S(tr, "convoy_escort", "Convoy Escort", "Escorts that keep the sea lanes open.")
S(tr, "support_integrated_operations", "Integrated Operations", "Escorts fully integrated with the fleet.")
S(tr, "hunter_killers", "Hunter-Killer Groups", "Groups that seek out and destroy submarines.",
  dlc="No Compromise, No Surrender")
S(tr, "torpedo_primacy", "Missile Primacy", "Escorts that strike first with anti-ship missiles.",
  dlc="No Compromise, No Surrender")
S(tr, "anti_aircraft_cruisers", "Air-Defence Destroyers", "Escorts built to stop missiles and aircraft.",
  dlc="No Compromise, No Surrender")
S(tr, "screen_support_focus", "Escort Support", "Escorts that sustain the fleet far from home.",
  dlc="No Compromise, No Surrender")
S(tr, "jeune_ecole", "The New School", "Missile boats and drone boats against bigger fleets.")
S(tr, "patrol_boats", "Drone Boats and Patrol Craft", "Swarms of small craft and drone boats in home waters.",
  dlc="No Compromise, No Surrender")
tr = TRACK(N, "submarines", "Submarines")
S(tr, "wolfpacks", "Wolfpacks", "Submarines that hunt together, guided by satellites and drones.")
S(tr, "submarine_fleet_operations", "Fleet Operations", "Submarines working with the surface fleet.")
S(tr, "capital_hunters", "Carrier Hunters", "Submarines that go for the enemy's carriers.")
S(tr, "submarine_coastal_defense", "Coastal Denial", "Submarines and drones that close the coast.",
  dlc="No Compromise, No Surrender")
S(tr, "coastal_minelaying", "Offensive Minelaying", "Submarines that mine the enemy's harbours.",
  dlc="No Compromise, No Surrender")
S(tr, "long_range_submarines", "Long-Range Patrols", "Submarines that patrol the far oceans for months.",
  dlc="No Compromise, No Surrender")

# ---- air -----------------------------------------------------------------------------------------------------
A = doctrine_folder("doc_air", "Air Doctrine", "air", "jet", "air",
                    "How the air force fights: one grand doctrine, then a subdoctrine in each of four tracks.")
G(A, "new_strategic_destruction", "Strategic Strike", "Stealth bombers and missiles against the enemy's industry, "
  "energy and command.")
G(A, "new_battlefield_support", "Close Air Integration", "Aircraft and drones as the army's flying artillery, "
  "called down in minutes.")
G(A, "new_operational_integrity", "Integrated Air Defence", "Win and hold the skies with fighters, missiles and "
  "radar as one system.")
tr = TRACK(A, "fighter_aircraft", "Fighters")
S(tr, "air_subdoctrine_fighter_homeland_defense", "Homeland Air Defence", "Fighters and missiles that guard the "
  "home skies.")
S(tr, "air_subdoctrine_escort_fighter", "Escort and Sweep", "Fighters that clear the way for the strike packages.")
S(tr, "air_subdoctrine_fighter_bombers", "Multirole Fighters", "Fighters that strike the ground as well as fight "
  "in the air.", dlc="By Blood Alone")
S(tr, "air_subdoctrine_tactical_flexibility", "Airspace Dominance", "Air superiority won and held over the front.")
S(tr, "air_subdoctrine_dogfighting_mastery", "Within-Visual-Range Mastery", "Pilots who win the close fight when "
  "the missiles run out.")
S(tr, "air_subdoctrine_fighter_central_field", "Naval Aviation", "Carrier fighters that defend the fleet.")
S(tr, "val_loyal_wingman", "Loyal Wingman Teams", "Each fighter flies with its own drones, which scout, jam and "
  "fire for it.", unl=["fighters with drone wingmen: air attack and agility higher"])
tr = TRACK(A, "strike_aircraft", "Strike")
S(tr, "air_subdoctrine_flying_artillery", "Flying Artillery", "Strike aircraft on call over the front.")
S(tr, "air_subdoctrine_dive_bombers", "Precision Strike", "One aircraft, one target, one guided weapon.")
S(tr, "air_subdoctrine_flexible_fire_support", "Joint Fires", "Air, artillery and naval fires coordinated as one.")
S(tr, "air_subdoctrine_carrier_strikes", "Sea-to-Shore Air Power", "Carrier aircraft that strike inland.")
S(tr, "air_subdoctrine_naval_strike_tactics", "Anti-Ship Strike", "Strike aircraft that hunt fleets.")
S(tr, "air_subdoctrine_naval_torpedo_tactics", "Missile Swarm Tactics", "Many missiles from many aircraft at once.")
S(tr, "val_drone_strike", "Drone Strike Campaigns", "Armed drones hunt the enemy round the clock.",
  unl=["drone airframes: ground attack and sortie efficiency higher"])
tr = TRACK(A, "medium_aircraft", "Strike Fighters & Interceptors")
S(tr, "air_subdoctrine_bomber_interception", "Interceptor Squadrons", "Heavy interceptors against bombers and "
  "missiles.")
S(tr, "air_subdoctrine_long_range_escort", "Long-Range Escort", "Escorts with the range to go all the way.")
S(tr, "air_subdoctrine_operational_air_support", "Operational Air Support", "Strikes on the enemy's reserves and "
  "supply.")
S(tr, "air_subdoctrine_tactical_battlefield_support", "Battlefield Air Interdiction", "Strikes behind the front "
  "line.")
S(tr, "air_subdoctrine_theater_interdiction", "Theatre Interdiction", "Strikes deep into the enemy's theatre.")
S(tr, "air_subdoctrine_aerial_reconnaissance", "ISR Operations", "Surveillance aircraft and drones watching "
  "everything.", dlc="La Resistance")
tr = TRACK(A, "heavy_aircraft", "Bombers & Patrol")
S(tr, "air_subdoctrine_night_bombing", "Night Penetration Strikes", "Bombers that strike in the dark.")
S(tr, "air_subdoctrine_carpet_bombing", "Saturation Strikes", "Massed missiles and bombs on a target area.")
S(tr, "air_subdoctrine_deep_air_raids", "Deep Strike", "Bombers that reach the enemy's heartland.")
S(tr, "air_subdoctrine_flying_fortresses", "Stealth Penetration", "Stealth bombers that fly through the "
  "defences.")
S(tr, "air_subdoctrine_coastal_air_patrol", "Coastal Patrol", "Patrol aircraft that guard the coast.",
  dlc="By Blood Alone")
S(tr, "air_subdoctrine_open_ocean_air_patrol", "Ocean Surveillance", "Patrol aircraft and drones that watch the "
  "oceans.", dlc="By Blood Alone")
S(tr, "air_subdoctrine_heavy_aircraft_focus", "Multi-Role Heavy Aircraft", "Big aircraft for every mission.",
  dlc="By Blood Alone")

# ---- special forces ------------------------------------------------------------------------------------------
SF = doctrine_folder("doc_sf", "Special Forces Doctrine", "special_forces", "dagger", "army",
                     "Special operations: one grand doctrine, two tracks.",
                     dlc="Arms Against Tyranny or No Compromise, No Surrender (without them, the Special Forces "
                         "technologies in the Infantry folder)")
G(SF, "special_forces_quantity", "Mass Special Operations", "Many special operations units, trained to a high "
  "standard.")
G(SF, "special_forces_quality", "Elite Special Operations", "Few units, the very best, for the hardest missions.")
tr = TRACK(SF, "special_forces_first", "First & Second Tracks")
S(tr, "mountaineers_1", "Arctic and Ski Troops", "Special forces for snow and cold.", dlc="Arms Against Tyranny")
S(tr, "mountaineers_2", "Mountain Special Forces", "Special forces for the high mountains.",
  dlc="Arms Against Tyranny")
S(tr, "marines_1", "Marine Raiders", "Raids from the sea on ports and coasts.", dlc="Arms Against Tyranny")
S(tr, "marines_2", "Expeditionary Marines", "Marines who seize and hold a beachhead.",
  dlc="Arms Against Tyranny")
S(tr, "paratroopers_1", "Sabotage Teams", "Teams dropped to destroy what the enemy needs most.",
  dlc="Arms Against Tyranny")
S(tr, "paratroopers_2", "Airborne Assault", "Whole airborne battalions dropped together.",
  dlc="Arms Against Tyranny")
S(tr, "rangers_1", "Jaeger Traditions", "Hunters of the forest who live off the land.",
  dlc="No Compromise, No Surrender")
S(tr, "rangers_2", "Jungle Rangers", "Rangers for jungle and swamp.", dlc="No Compromise, No Surrender")
S(tr, "val_sof_drones", "Drone-Enabled Raids", "Small teams with their own drones for scouting and strikes.",
  unl=["special forces: recon and attack higher"])
SF.extra["tracks_in_game"] = 2
SF.extra["note"] = ("In the game every special forces subdoctrine can go in either of the two tracks (each one only "
                    "once), so they are listed once here.")
