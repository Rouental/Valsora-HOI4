"""Special projects (Götterdämmerung's facilities): the game's 49 renamed, and the new lines (mechs, orbital strike ...).

Each project is built at a special project facility by a scientist. Complexity is how many prototype iterations it
takes; the author wants them open to anyone but very difficult, so most projects here are a step harder than the
game's (the game's own value is kept in tree.json as vanilla.complexity).
"""
from common import folder, T

F = folder("projects", "Special Projects", "special_projects", "projects", "atom", "projects",
           "Projects at the special project facilities: anyone can run them, but they are hard, slow and dear. Four "
           "specialisations, as in the game; the nuclear one also holds space.",
           dlc="Götterdämmerung (without it: no special projects; their outputs are ordinary technologies where they "
               "can be)", kind="projects")
F.extra["specs"] = [
    {"key": "land", "name": "Land", "game": "specialization_land"},
    {"key": "naval", "name": "Naval", "game": "specialization_naval"},
    {"key": "air", "name": "Air, rockets & radar", "game": "specialization_air"},
    {"key": "strategic", "name": "Strategic: nuclear & space", "game": "specialization_nuclear",
     "note": "The game's nuclear specialisation, renamed: it also holds the new space line (a new project tag, "
             "sp_tag_space)."},
]
SPEC_LANE = {"land": 0, "naval": 1, "air": 2, "strategic": 3}
COMPLEX = ["small", "medium", "large", "insane"]


def P(spec, line, pid, name, year, complexity, desc, out, req=(), start=None, icon=None, note=None, tags=()):
    t = T(F, pid, name, year, SPEC_LANE[spec], desc, icon=icon, req=list(req), start=start, unl=out, note=note,
          size="big")
    t["spec"] = spec
    t["line"] = line
    t["complexity"] = complexity
    t["tags"] = list(tags)
    return t


# ---- land ----------------------------------------------------------------------------------------------------
P("land", "Mechs", "val_sp_exoskeleton", "Powered Exoskeletons", 2036, "medium",
  "Powered frames that let a soldier carry twice the load and march further.",
  ["infantry and special forces: soft attack, breakthrough and speed higher (equipment and unit bonuses, as the "
   "game's projects give)"], req=["infantry_weapons1"], icon="exo", tags=["sp_tag_tank"])
P("land", "Mechs", "val_sp_light_walker", "Light Walker", 2039, "large",
  "A two-legged recon and fire-support walker, at home in hills, forest and ruins where tracks are slow.",
  ["new support company: Light Walker (recon, soft attack; strong in hills, mountains, forest and cities)",
   "new equipment: light_walker_equipment_1"], req=["val_sp_exoskeleton"], icon="mech", tags=["sp_tag_tank"])
P("land", "Mechs", "sp_land_land_cruiser", "Assault Mech", 2042, "insane",
  "A heavy walker with its own chassis in the tank designer: armour, a main gun or missile pods, an AI co-pilot. "
  "Slow to build, few per army; only industrial powers can field them.",
  ["new chassis in the tank designer: mech_chassis_1 (modules: armour, main gun, missile pods, AI co-pilot)",
   "new battalion: Assault Mech", "opens the Assault Mech technologies in the Armour folder",
   "without No Step Back: the equipment itself (assault_mech_equipment_1)"],
  req=["val_sp_light_walker", "assembly_line_production"], icon="mech", tags=["sp_tag_tank"],
  note="Built on the game's Land Cruiser project, which has the same kind of output. Also needs Digital-Twin "
       "Production (industry), so only industrial powers field them.")
P("land", "Engineering", "sp_land_military_engineering_vehicles", "Combat Engineering Vehicles", 2025, "medium",
  "Breaching tanks, bridgelayers and recovery vehicles on main battle tank hulls.",
  ["opens the armoured engineer, recovery, military police and command post companies (Support folder)"],
  req=["tech_engineers"], icon="engineer", tags=["sp_tag_tank"])
P("land", "Engineering", "sp_land_flamethrower_tank", "Thermobaric Launcher", 2025, "medium",
  "A tracked launcher for thermobaric rockets, the weapon for trenches and towns.",
  ["opens Thermobaric Rocket Launcher (Armour folder): a tank designer module"], req=["gwtank_chassis"], icon="flame",
  tags=["sp_tag_tank"])
P("land", "Engineering", "sp_land_stronghold_network", "Hardened Bunker Network", 2036, "large",
  "Tunnels, hardened command posts and missile shelters under a whole region.",
  ["stronghold network building in a state (the game's)"], req=["land_fort_tech_1"], icon="fort",
  tags=["sp_tag_artillery"])
P("land", "Long-range fires", "sp_land_super_heavy_howitzer", "Long-Range Cannon", 2036, "medium",
  "A strategic cannon that fires guided shells a thousand kilometres.",
  ["new equipment: the game's super-heavy howitzer, renamed (strategic bombardment of a state)",
   "opens Base-Bleed Long-Range Rounds (Artillery folder)"], req=["artillery3"], icon="howitzer",
  tags=["sp_tag_artillery"])
P("land", "Long-range fires", "sp_land_self_propelled_super_heavy_howitzer", "Self-Propelled Long-Range Cannon",
  2039, "large", "The long-range cannon on a tracked chassis that can move between strikes.",
  ["new equipment: the game's self-propelled super-heavy howitzer, renamed",
   "opens Truck-Mounted Long-Range Guns (Artillery folder)"], req=["sp_land_super_heavy_howitzer"], icon="howitzer",
  tags=["sp_tag_artillery"])
P("land", "Long-range fires", "sp_land_super_heavy_railway_gun", "Rail-Mobile Strategic Fires", 2039, "large",
  "Heavy missiles on trains that vanish into tunnels between launches.",
  ["new equipment: the game's super-heavy railway gun, renamed"], req=["railway_gun"], icon="rail",
  tags=["sp_tag_artillery"])
P("land", "Long-range fires", "sp_land_multi_charge_large_caliber_gun", "Hypervelocity Supergun", 2042, "large",
  "A fixed supergun that throws guided projectiles at another continent: Valsora's own folly.",
  ["mega gun emplacement building (the game's)"], req=["sp_land_super_heavy_howitzer"], icon="howitzer",
  tags=["sp_tag_artillery"])
P("land", "Long-range fires", "sp_land_large_caliber_kinetic_energy_sabot", "Electromagnetic Railgun", 2042, "large",
  "Electromagnetic guns that fire solid rods at Mach 7: no explosive, no defence.",
  ["opens Kinetic Energy Missiles (Artillery folder)", "opens the Naval Railgun project"],
  req=["artillery4"], icon="laser", tags=["sp_tag_artillery"])

# ---- naval ---------------------------------------------------------------------------------------------------
P("naval", "Submarines", "sp_naval_nuclear_submarine", "Nuclear Attack Submarine", 1965, "insane",
  "A nuclear reactor drives the submarine for months under water, at speeds no diesel boat matches.",
  ["new hull: the game's nuclear submarine (nuclear_submarine)"], req=["val_sub_cw1"], start="super", icon="sub",
  tags=["sp_tag_nuclear_power", "sp_tag_submarine"])
P("naval", "Submarines", "sp_naval_nuclear_missile_submarine", "Ballistic Missile Submarine", 1985, "large",
  "Nuclear-armed ballistic missiles on a submarine nobody can find: the deterrent that survives a first strike.",
  ["new hull: the game's nuclear missile submarine (nuclear_missile_submarine)"],
  req=["sp_naval_nuclear_submarine", "sp_nuclear_warheads"], start="super", icon="sub",
  tags=["sp_tag_nuclear_warfare", "sp_tag_submarine"])
P("naval", "Submarines", "sp_naval_rocket_launching_submarine", "Cruise-Missile Submarine", 1985, "medium",
  "A submarine with dozens of cruise missiles in vertical tubes.",
  ["new hull: the game's missile submarine (rocket_submarine)"], req=["sp_rockets_flying_bomb"], start="super",
  icon="sub", tags=["sp_tag_rocket", "sp_tag_submarine"])
P("naval", "Submarines", "sp_naval_aip_engine", "Advanced AIP", 2025, "large",
  "Air-independent propulsion that keeps a conventional submarine under water for weeks.",
  ["opens Fuel-Cell AIP and Closed-Cycle Engines (Naval folder)"], req=["early_ship_hull_submarine"], icon="engine",
  tags=["sp_tag_surface_ship", "sp_tag_submarine"])
P("naval", "Submarines", "sp_naval_cruiser_submarine", "Large Patrol Submarine", 2025, "medium",
  "A large conventional submarine with the range for an ocean patrol.",
  ["new hull: the game's cruiser submarine, renamed"], req=["early_ship_hull_submarine"], icon="sub",
  tags=["sp_tag_submarine"])
P("naval", "Submarines", "sp_naval_midget_submarine", "Uncrewed Underwater Vehicles", 2025, "medium",
  "Torpedo-sized and larger underwater drones for mines, scouting and sabotage.",
  ["new hull: the game's midget submarine, renamed: an uncrewed submarine"], req=["early_ship_hull_submarine"],
  icon="usv", tags=["sp_tag_submarine"])
P("naval", "Submarines", "sp_naval_anechoic_tiles", "Acoustic Metamaterials", 2036, "medium",
  "Hull coatings that swallow sonar pulses and the boat's own noise.",
  ["submarines: visibility lower (the game's anechoic tiles)"], req=["basic_ship_hull_submarine"], icon="sub",
  tags=["sp_tag_submarine"])
P("naval", "Submarines", "sp_naval_fleet_submarine", "Extra-Large Uncrewed Submarine", 2036, "large",
  "A drone submarine the size of a bus that patrols for months without a crew.",
  ["new hull: the game's fleet submarine, renamed: a large uncrewed submarine"],
  req=["sp_naval_midget_submarine"], icon="usv", tags=["sp_tag_submarine"])
P("naval", "Submarines", "sp_naval_nuclear_torpedo", "Nuclear Torpedo", 2036, "large",
  "A nuclear-armed underwater drone with intercontinental range, a weapon of last resort.",
  ["submarine module: nuclear torpedo (the game's)"], req=["sp_naval_nuclear_submarine", "sp_nuclear_warheads"],
  icon="nuke", tags=["sp_tag_submarine", "sp_tag_nuclear_warfare"])
P("naval", "Submarines", "sp_naval_submarine_carrier", "Drone Mothership Submarine", 2039, "large",
  "A large submarine that launches and recovers underwater and aerial drones.",
  ["new hull: the game's submarine carrier, renamed"], req=["sp_naval_fleet_submarine"], icon="sub",
  tags=["sp_tag_submarine"])
P("naval", "Surface fleet", "sp_naval_modern_carrier", "Nuclear Supercarrier", 2025, "large",
  "A nuclear-powered carrier with a hundred aircraft and no need to refuel for decades.",
  ["new hull: the game's modern carrier, renamed"], req=["val_carrier_cw2"], start="super", icon="carrier",
  tags=["sp_tag_surface_ship"])
P("naval", "Surface fleet", "sp_naval_escort_carrier", "Light Drone Carrier", 2036, "medium",
  "A small, cheap carrier for drones: air power for navies that can't afford a supercarrier.",
  ["new hull: the game's escort carrier, renamed"], req=["early_ship_hull_carrier"], icon="carrier",
  tags=["sp_tag_surface_ship"])
P("naval", "Surface fleet", "sp_naval_torpedo_cruiser", "Arsenal Corvette", 2036, "medium",
  "A small hull packed with missile cells: a coastal navy's arsenal ship.",
  ["new hull: the game's torpedo cruiser, renamed"], req=["early_ship_hull_cruiser"], icon="frigate",
  tags=["sp_tag_surface_ship"])
P("naval", "Surface fleet", "sp_naval_ice_carrier", "Mobile Offshore Base", 2042, "insane",
  "A floating base of joined sections: runway, harbour and depot in the middle of an ocean.",
  ["opens Modular Sea Base Sections and Floating Runways (Naval folder)"], req=["improved_ship_hull_carrier"],
  icon="carrier", tags=["sp_tag_surface_ship"])
P("naval", "Surface fleet", "sp_naval_super_heavy_battleship", "Dreadnought", 2043, "large",
  "A super-heavy arsenal battleship: the biggest warship afloat, with its own lasers and a thousand missiles.",
  ["new hull: the game's super-heavy battleship, renamed"], req=["advanced_ship_hull_heavy"], icon="battleship",
  tags=["sp_tag_surface_ship"])
P("naval", "Surface fleet", "sp_naval_modern_battleship", "Railgun Battleship", 2045, "insane",
  "A battleship built around railguns and lasers powered by a reactor.",
  ["new hull: the game's modern battleship, renamed"], req=["val_sp_naval_railgun"], icon="battleship",
  tags=["sp_tag_surface_ship"])
P("naval", "Support & weapons", "sp_naval_underway_replenishment", "Fleet Replenishment", 2025, "medium",
  "Fast combat support ships and the methods to supply a fleet at sea.",
  ["opens Fleet Replenishment Oilers and Automated Replenishment at Sea (Naval Systems)"], req=["mtg_transport"],
  icon="cargo", tags=["sp_tag_surface_ship"])
P("naval", "Support & weapons", "sp_naval_support_ships", "Fleet Support Ships", 2036, "medium",
  "Repair and support ships that keep a task force fighting far from its bases.",
  ["new equipment: the game's support and repair ships", "opens their second tiers (Naval Systems)"],
  req=["sp_naval_underway_replenishment"], icon="wrench", tags=["sp_tag_surface_ship"])
P("naval", "Support & weapons", "sp_naval_proximity_fuze", "Smart Munitions", 2036, "large",
  "Seekers and fuzes small and tough enough for gun shells.",
  ["ships: anti-air higher (the game's proximity fuze)", "opens Shock-Hardened Seekers and Smart Airburst Shells "
   "(Artillery folder)"], req=["improved_dp_light_battery"], icon="aa", tags=["sp_tag_surface_ship"])
P("naval", "Support & weapons", "val_sp_naval_railgun", "Naval Railgun", 2043, "large",
  "A railgun mount for warships, fed by their electric plants.",
  ["new ship module: naval railgun (heavy attack, long range)"],
  req=["sp_land_large_caliber_kinetic_energy_sabot"], icon="gun", tags=["sp_tag_surface_ship"])

# ---- air, rockets and radar ------------------------------------------------------------------------------------
P("air", "Aircraft", "sp_air_helicopter", "Tiltrotor Aircraft", 2025, "medium",
  "Tiltrotors with twice a helicopter's speed and range: air assault, ambulances and supply.",
  ["new equipment: the game's helicopter, renamed (attack and transport tiltrotors)",
   "opens the air cavalry, air ambulance and lift companies (Support folder)"], req=["bba_early_transport_plane"],
  icon="heli", tags=["sp_tag_aircraft", "sp_tag_helicopter"],
  note="Helicopters themselves are ordinary in 2036: the game's helicopter equipment is what this unlocks.")
P("air", "Aircraft", "sp_air_intercontinental_bomber", "Global Strike Bomber", 2039, "large",
  "A bomber with intercontinental range and room for hypersonic missiles.",
  ["new airframe design: the game's intercontinental bomber, renamed"], req=["basic_large_airframe"], icon="bomber",
  tags=["sp_tag_aircraft"])
P("air", "Aircraft", "sp_air_mothership_aircraft", "Drone Mothership", 2040, "medium",
  "A large aircraft that carries and launches drones in flight.",
  ["opens Drone Mothership Bays and its line (Air folder)"], req=["improved_large_airframe"], icon="drone_l",
  tags=["sp_tag_aircraft"])
P("air", "Engines", "sp_air_jet_engine", "Adaptive-Cycle Engine", 2036, "large",
  "An engine that changes its cycle in flight: range and speed at once.",
  ["opens Seventh-Generation Fighter and Adaptive-Cycle Engines (Air folder)"], req=["engines_4"], icon="engine",
  tags=["sp_tag_aircraft", "sp_tag_jet"])
P("air", "Engines", "sp_air_axial_jet_engine", "Combined-Cycle Engine", 2040, "large",
  "A turbine that becomes a ramjet at speed: aircraft that cruise at Mach 5.",
  ["opens the Hypersonic Strike Aircraft and Hypersonic Bomber (Air folder)"], req=["sp_air_jet_engine"],
  icon="engine", tags=["sp_tag_aircraft", "sp_tag_jet"])
P("air", "Engines", "sp_air_supersonic_jet", "Hypersonic Aircraft", 2045, "insane",
  "A crewed aircraft that flies at hypersonic speed: the end of the airframe line.",
  ["new airframe: the game's supersonic airframe, renamed"], req=["sp_air_axial_jet_engine"], icon="jet",
  tags=["sp_tag_aircraft", "sp_tag_jet"])
P("air", "Munitions", "sp_air_bouncing_bomb", "Bunker Buster", 2025, "medium",
  "Penetrating bombs for buried command posts.", ["plane module: the game's bouncing bomb, renamed"],
  req=["heavy_bombs"], icon="bomb", tags=["sp_tag_aircraft", "sp_tag_bomb"])
P("air", "Munitions", "sp_air_earthshaker_bomb", "Massive Ordnance Penetrator", 2036, "medium",
  "A fourteen-tonne bomb that reaches sixty metres underground.", ["plane module: the game's earthquake bomb, "
  "renamed"], req=["sp_air_bouncing_bomb"], icon="bomb", tags=["sp_tag_aircraft", "sp_tag_bomb"])
P("air", "Munitions", "val_sp_swarm", "Autonomous Swarm", 2042, "large",
  "A swarm 'aircraft': hundreds of small drones that fight as one, and ignore pilots and losses.",
  ["new airframe: swarm_airframe_1 (no pilots, losses replaced cheaply)"], req=["val_uav4", "val_ai_autonomy"],
  icon="fpv", tags=["sp_tag_aircraft"])
P("air", "Missiles", "sp_rockets_flying_bomb", "Cruise Missile", 1985, "medium",
  "Long-range cruise missiles that fly low and follow the ground to their target.",
  ["new equipment: the game's guided missiles (guided_missile_equipment)", "opens the guidance and air-launched "
   "missile technologies (Electronics)"], req=["experimental_rockets"], start="super", icon="missile",
  tags=["sp_tag_rocket", "sp_tag_guided_bomb"])
P("air", "Missiles", "sp_rockets_ground_to_air_missile", "Integrated Air and Missile Defence", 2025, "large",
  "Long-range surface-to-air missiles and the network that ties them together.",
  ["new equipment: the game's surface-to-air missiles (sam_missile_equipment; the Air Defence Company uses them)"],
  req=["experimental_rockets"], start="modern", icon="aa", tags=["sp_tag_rocket", "sp_tag_guided_bomb"],
  note="Most nations start with it done: their SHORAD companies need the equipment.")
P("air", "Missiles", "sp_rocket_interceptor", "Hit-to-Kill Interceptor", 2036, "large",
  "Interceptors that destroy ballistic missiles by hitting them head-on.",
  ["new equipment: the game's rocket interceptor", "opens Interceptor Missiles II (Electronics)"],
  req=["sp_rockets_ground_to_air_missile"], icon="missile", tags=["sp_tag_rocket"])
P("air", "Missiles", "val_sp_directed_energy", "Directed-Energy Air Defence", 2039, "large",
  "High-energy lasers and microwave weapons for states and ships: drones and missiles shot down for pennies.",
  ["states: anti-air higher; ships: anti-air higher; enemy drones less effective"], req=["antiair5"], icon="laser",
  tags=["sp_tag_radar"])
P("air", "Ballistic missiles", "sp_rockets_ballistic_missile", "Short-Range Ballistic Missile", 1965, "large",
  "Mobile ballistic missiles with a few hundred kilometres' range.",
  ["new equipment: the game's ballistic missiles (ballistic_missile_equipment)"], req=["experimental_rockets"],
  start="modern", icon="missile", tags=["sp_tag_rocket"])
P("air", "Ballistic missiles", "sp_rockets_medium_range_ballistic_missile", "Intermediate-Range Ballistic Missile",
  1985, "large", "Ballistic missiles that reach across a continent.", ["new equipment: the game's MRBM tier"],
  req=["sp_rockets_ballistic_missile"], start="super", icon="missile", tags=["sp_tag_rocket"])
P("air", "Ballistic missiles", "sp_rockets_long_range_ballistic_missile", "Intercontinental Ballistic Missile",
  1985, "large", "Missiles that reach any city on Valsora in half an hour.",
  ["new equipment: the game's nuclear missiles (with warheads)"], req=["sp_rockets_medium_range_ballistic_missile"],
  start="super", icon="missile", tags=["sp_tag_rocket", "sp_tag_nuclear_warfare"])
P("air", "Ballistic missiles", "val_sp_hypersonic_glide", "Hypersonic Glide Vehicle", 2039, "insane",
  "A glider launched by a ballistic missile that weaves at Mach 10: the last step of the missile line, very hard "
  "to intercept.", ["new equipment: hypersonic_missile_equipment_1 (strikes that interceptors rarely stop)"],
  req=["sp_rockets_medium_range_ballistic_missile", "val_hypersonic"], icon="missile", tags=["sp_tag_rocket"])
P("air", "Radar, AI & cyber", "sp_air_radar", "Over-the-Horizon Radar", 2036, "medium",
  "Radars that see far beyond the horizon, and the new radar technologies that follow.",
  ["opens Gallium-Nitride Radars and its line (Electronics)", "radar stations: range higher"],
  req=["val_radar_m1"], icon="radar", tags=["sp_tag_radar"],
  note="In the game this project gates all its radar technologies; here only the advanced ones, since every navy "
       "and air force has radar in 2036 (the basic radars are ordinary technologies).")
P("air", "Radar, AI & cyber", "val_sp_military_ai", "Military AI Co-Pilot", 2039, "large",
  "An AI that flies, fights and plans beside the crews.",
  ["planning speed and max planning higher", "the AI co-pilot module for the Assault Mech"],
  req=["improved_computing_machine"], icon="ai", tags=["sp_tag_radar"])
P("air", "Radar, AI & cyber", "val_sp_cyber", "Cyber Warfare Command", 2040, "large",
  "A command for cyber war, with tools that can switch off a country's grid.",
  ["intelligence agency upgrades: cyber defence and offence (the encryption and decryption techs' last steps)",
   "a targeted decision against an enemy's infrastructure"], req=["computing_machine"], icon="cyber",
  tags=["sp_tag_radar"])

# ---- strategic: nuclear and space ------------------------------------------------------------------------------
P("strategic", "Nuclear power", "sp_nuclear_reactor", "Enrichment and Reactors", 1965, "large",
  "Enrichment plants and reactors that make weapons-grade material.",
  ["the game's nuclear reactor technology and building"], req=["atomic_research"], start="super", icon="nuke",
  tags=["sp_tag_nuclear_power"])
P("strategic", "Nuclear power", "sp_nuclear_engines", "Naval Reactors", 1985, "medium",
  "Reactors small enough for a submarine or a carrier.", ["ship modules: nuclear reactors (the game's)"],
  req=["sp_nuclear_reactor"], start="super", icon="nuke", tags=["sp_tag_nuclear_power"])
P("strategic", "Nuclear power", "sp_commercial_nuclear_reactor", "Small Modular Reactors", 2036, "large",
  "Factory-built reactors that power a city or a base.", ["the game's commercial reactor building"],
  req=["atomic_research"], icon="nuke", tags=["sp_tag_nuclear_power"])
P("strategic", "Nuclear weapons", "sp_nuclear_bomb", "Fission Warheads", 1965, "insane",
  "The bomb itself. Only the superpowers have it at the start; anyone else needs years of very hard work.",
  ["nuclear weapons (the game's nukes technology)"], req=["sp_nuclear_reactor"], start="super", icon="nuke",
  tags=["sp_tag_nuclear_warfare"])
P("strategic", "Nuclear weapons", "sp_thermo_nuclear_bomb", "Thermonuclear Warheads", 1965, "insane",
  "Hydrogen bombs: a hundred times the power of the first.", ["the game's thermonuclear bombs"],
  req=["sp_nuclear_bomb"], start="super", icon="nuke", tags=["sp_tag_nuclear_warfare"])
P("strategic", "Nuclear weapons", "sp_nuclear_warheads", "Missile Warheads", 1985, "large",
  "Warheads small enough for missiles, several to a missile.", ["the game's nuclear missile warheads"],
  req=["sp_thermo_nuclear_bomb"], start="super", icon="nuke", tags=["sp_tag_nuclear_warfare"])
P("strategic", "Space", "val_sp_orbital_launch", "Orbital Launch Capability", 2025, "large",
  "A spaceport and the rockets to put satellites in orbit.",
  ["spaceport building (a new state building)", "launch decisions"], req=["experimental_rockets"], start="super",
  icon="satellite", tags=["sp_tag_space"])
P("strategic", "Space", "val_sp_recon_sats", "Reconnaissance Satellites", 2036, "large",
  "Imaging and radar satellites over every enemy base.",
  ["intelligence agency upgrades; weather and targeting bonuses"], req=["val_sp_orbital_launch"], start="super",
  icon="satellite", tags=["sp_tag_space"])
P("strategic", "Space", "val_sp_asat", "Anti-Satellite Weapons", 2039, "large",
  "Missiles and lasers that blind an enemy's satellites (they don't stop a kinetic strike).",
  ["a targeted decision with a cooldown: the target loses its satellite bonuses"], req=["val_sp_recon_sats"],
  icon="satellite", tags=["sp_tag_space"])
P("strategic", "Space", "val_sp_kinetic", "Orbital Kinetic Bombardment", 2045, "insane",
  "Tungsten rods dropped from orbit: weaker than a nuke, no fallout, and once launched nothing stops them. The only "
  "defence is a raid on the launch site before they go up.",
  ["a production decision: a rod (steel, tungsten, civilian factories), readied at a launch site (a facility) for "
   "some days: the window for the enemy's Facility Strike raid",
   "a targeted decision, Kinetic Strike on [State]: buildings, units and infrastructure in the state hit, war "
   "support lost; a chance to miss; a cooldown and world tension", "a superevent when the first strike lands"],
  req=["val_sp_asat"], icon="rod", tags=["sp_tag_space"],
  note="The author's design (2026-10-16): built from the game's own raid and building-damage effects, not "
       "launch_nuke, so there is no radiation.")
