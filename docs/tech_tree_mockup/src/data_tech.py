"""The electronics and industry folders."""
from common import folder, T

# =============================================================================================================
F = folder("electronics", "Electronics", "electronics_folder", "down", "chip", "civilian",
           "Networks, radar, computing and military AI, combat systems, cyber defence and offence; fortifications; "
           "missiles and nuclear research.")

F.section("Networks & sensors", 0)
T(F, "electronic_mechanical_engineering", "Microelectronics", 1965, 0, icon="chip", req=[],
  desc="Transistors and integrated circuits: the root of every electronic system on the tree.")
T(F, "radio", "Tactical Radio Networks", 1985, 0, icon="signal",
  desc="Secure radio nets from the platoon to the corps.")
T(F, "improved_radio", "Software-Defined Radios", 2025, 0, icon="signal",
  desc="Radios that change waveform in software, carry data and resist jamming.")
T(F, "advanced_radio", "Battle Networks", 2036, 0, icon="network",
  desc="Every sensor and shooter on one network: a target seen by anyone can be hit by anyone.")
T(F, "val_radio4", "Resilient Laser Links", 2042, 0, icon="network",
  desc="Laser and satellite links that the enemy can neither jam nor overhear.",
  unl=["land units: coordination and planning higher; enemy electronic warfare less effective (a new upgrade)"])
T(F, "val_radar_cw1", "Search Radar", 1965, 1, icon="radar", req=["electronic_mechanical_engineering"],
  desc="Rotating search radars for ships, airfields and air defence.",
  unl=["radar station building; ship_radar_1-level search radar (moved here from the game's radio_detection)"])
T(F, "val_radar_cw2", "Pulse-Doppler Radar", 1985, 1, icon="radar",
  desc="Radars that pick moving targets out of the ground clutter: fighters see low fliers.",
  unl=["ship and plane radar modules: ship_radar_2, air_air_radar_1, air_ground_radar_1 (moved here from the "
       "project-gated techs, so every navy and air force has them)"])
T(F, "val_radar_m1", "AESA Radar", 2005, 1, icon="radar",
  desc="Electronically scanned arrays: many targets at once, and much harder to jam.",
  unl=["ship and plane radar modules: ship_radar_3, air_air_radar_2 (moved here)"])
T(F, "cavity_magnatron", "Gallium-Nitride Radars", 2038, 1, icon="radar",
  dlc="Needs the special project Over-the-Horizon Radar (Götterdämmerung)",
  desc="New semiconductors double a radar's range for the same size and power.")
T(F, "centimetric_radar", "Over-the-Horizon Radar", 2040, 1, icon="radar",
  dlc="Needs the special project Over-the-Horizon Radar (Götterdämmerung)",
  desc="Radars that bounce off the sky and see aircraft and ships thousands of kilometres away.")
T(F, "phased_array", "Space-Based Tracking", 2041, 1, icon="satellite",
  dlc="Needs the special project Over-the-Horizon Radar (Götterdämmerung)",
  desc="Satellites that track aircraft, ships and missiles from orbit.")
T(F, "monopulse_radar", "Cognitive Radar", 2042, 1, icon="radar",
  dlc="Needs the special project Over-the-Horizon Radar (Götterdämmerung)",
  desc="Radars that adapt their signal to each target and to each jammer.")

F.section("Computing & combat systems", 2)
T(F, "mechanical_computing", "Digital Computers", 1965, 2, icon="chip", req=["electronic_mechanical_engineering"],
  desc="Computers for fire control, bomb sights and codes.")
T(F, "computing_machine", "Networked Computing", 1985, 2, icon="chip",
  desc="Computers joined in networks: data, maps and orders move in seconds.")
T(F, "improved_computing_machine", "Military AI", 2036, 2, icon="ai",
  desc="AI that sifts the sensors, suggests targets and plans the logistics: AI-assisted targeting in full service.")
T(F, "val_ai_autonomy", "Autonomous Weapons Control", 2039, 2, icon="ai",
  desc="AI trusted to fly drones, run air defences and pick targets within the rules it is given.",
  unl=["drones, FPV teams and air defence: attack higher (a new upgrade)"])
T(F, "advanced_computing_machine", "Quantum Computing", 2042, 2, icon="quantum", req=["improved_computing_machine"],
  desc="Quantum computers for codebreaking, logistics and materials science.")
T(F, "basic_fire_control_system", "Digital Fire Control", 1985, 3, icon="radar", req=["mechanical_computing"],
  dlc="Man the Guns", desc="Digital fire control for the ship's guns and missiles.")
T(F, "improved_fire_control_system", "Integrated Combat System", 2025, 3, icon="radar", dlc="Man the Guns",
  desc="One combat system runs every sensor and weapon of the ship.")
T(F, "advanced_fire_control_system", "AI-Assisted Fire Control", 2036, 3, icon="ai", dlc="Man the Guns",
  desc="The ship's AI assigns weapons to threats faster than a crew can.")
T(F, "basic_encryption", "Network Encryption", 2025, 4, icon="cyber", req=["computing_machine"],
  dlc="Not with La Resistance (its agency upgrades do this)",
  desc="Strong encryption on every link: the enemy hears noise.")
T(F, "improved_encryption", "Zero-Trust Networks", 2040, 4, icon="cyber", dlc="Not with La Resistance",
  desc="Networks that verify every user and device: a stolen password opens nothing.")
T(F, "advanced_encryption", "Post-Quantum Cryptography", 2042, 4, icon="cyber", dlc="Not with La Resistance",
  desc="Codes that even a quantum computer can't break.")
T(F, "basic_decryption", "Signals Intelligence", 2025, 5, icon="code", req=["computing_machine"],
  dlc="Not with La Resistance (its agency upgrades do this)",
  desc="Intercepting and reading the enemy's communications.")
T(F, "improved_decryption", "Offensive Cyber Operations", 2040, 5, icon="code", dlc="Not with La Resistance",
  desc="Breaking into the enemy's networks to read them, and to turn them off.")
T(F, "advanced_decryption", "Quantum Codebreaking", 2042, 5, icon="quantum", dlc="Not with La Resistance",
  desc="Quantum computers break the codes everyone thought were safe.")

F.section("Fortifications", 6)
T(F, "basic_fortification_tech", "Field Fortifications", 1965, 6, icon="fort", req=[],
  desc="Trenches, bunkers and minefields, the defences every army can build.")
T(F, "land_fort_tech_1", "Hardened Shelters", 1985, 6, icon="fort",
  desc="Concrete shelters for aircraft, missiles and command posts.")
T(F, "land_fort_tech_2", "Deep Underground Facilities", 2040, 6, icon="fort",
  desc="Bases tunnelled deep into rock, safe from all but the heaviest weapons.")
T(F, "coastal_fort_tech_1", "Coastal Missile Batteries", 1985, 7, icon="missile", req=["basic_fortification_tech"],
  desc="Mobile anti-ship missile batteries hidden along the coast.")
T(F, "coastal_fort_tech_2", "Anti-Access Coastal Defence", 2040, 7, icon="fort",
  desc="Missiles, mines and drones that close the sea for hundreds of kilometres off the coast.")

F.section("Missiles & nuclear", 8)
T(F, "experimental_rockets", "Missile Technology", 1965, 8, icon="missile", req=[],
  desc="Rocket motors, guidance and warheads: the base of every missile project.",
  note="The game's rocket projects (cruise and ballistic missiles, interceptors) open from here, as in the game.")
T(F, "sp_rockets_improved_guidance", "Terrain-Matching Guidance", 2038, 8, icon="missile",
  dlc="Needs the special project Cruise Missile (Götterdämmerung)",
  desc="Cruise missiles that read the ground below them and can't be spoofed.")
T(F, "val_hypersonic", "Hypersonic Propulsion", 2039, 8, icon="missile", req=["experimental_rockets"],
  desc="Scramjets and glide bodies that survive Mach 5 and more: the base of the hypersonic projects.",
  unl=["opens the special project Hypersonic Glide Vehicle"])
T(F, "sp_rockets_rocket_bomber", "Air-Launched Cruise Missiles", 2044, 8, icon="missile", dlc="By Blood Alone",
  req=["sp_rockets_improved_guidance"],
  desc="Cruise missiles on aircraft pylons: bombers strike from a thousand kilometres away.")
T(F, "sp_rockets_improved_rocket_bomber", "Stealthy Stand-Off Missiles", 2045, 8, icon="missile",
  dlc="Needs the special project Cruise Missile (Götterdämmerung)",
  desc="Stealthy stand-off missiles that slip through the air defences.")
T(F, "sp_rockets_dual_chamber_rocket_engine_1", "Interceptor Missiles II", 2044, 9, icon="missile",
  req=["experimental_rockets"], dlc="Needs the special project Hit-to-Kill Interceptor (Götterdämmerung)",
  desc="Faster interceptors with two-pulse motors.")
T(F, "sp_rockets_dual_chamber_rocket_engine_2", "Exo-Atmospheric Interceptors", 2046, 9, icon="missile",
  dlc="Needs the special project Hit-to-Kill Interceptor (Götterdämmerung)",
  desc="Interceptors that destroy warheads above the atmosphere.")
T(F, "atomic_research", "Nuclear Research", 1965, 10, icon="nuke", req=[], start="modern",
  desc="Research reactors and nuclear physics: the gate to the nuclear projects (power, and for those who dare, "
       "weapons).",
  note="The weapons themselves are the nuclear special projects, very hard to complete; only the superpowers "
       "start with them done.")

# =============================================================================================================
F = folder("industry", "Industry", "industry_folder", "down", "factory", "civilian",
           "Production, construction, resources, fuel and the synthetics that replace what a nation can't import.")

F.section("Production", 0)
T(F, "val_ind_cw1", "Mass Production", 1965, 0, icon="factory", req=[],
  desc="Standardised parts and long production runs: the Cold War's factories.",
  unl=["factory output and production efficiency (a small part of what the modern tier has over the feudal one)"])
T(F, "val_ind_cw2", "Numerical Control", 1985, 0, icon="gear",
  desc="Computer-controlled machine tools that cut parts to any drawing.",
  unl=["production efficiency higher (a new upgrade)"])
T(F, "val_ind_m1", "Industrial Robots", 2005, 0, icon="gear",
  desc="Robot arms on the assembly lines: faster, cheaper, more precise.",
  unl=["factory output higher (a new upgrade)"])
T(F, "val_ind_m2", "Lean Production", 2025, 0, icon="gear",
  desc="Just-in-time supply chains and digital design: today's factories.",
  unl=["production efficiency cap higher (a new upgrade)"])
T(F, "basic_machine_tools", "Smart Factories", 2036, 0, icon="factory",
  desc="Every machine connected and monitored: production planned from the shop floor's own data.")
T(F, "improved_machine_tools", "Collaborative Robots", 2037, 0, icon="gear",
  desc="Robots that work beside people and change jobs in minutes.")
T(F, "advanced_machine_tools", "Lights-Out Production Cells", 2039, 0, icon="gear",
  desc="Factory cells that run unattended through the night.")
T(F, "assembly_line_production", "Digital-Twin Production", 2041, 0, icon="factory",
  desc="Each line has a digital twin that tests every change before the real one makes it.")
T(F, "flexible_line", "Reconfigurable Lines", 2043, 0, icon="factory", excl=["streamlined_line"],
  desc="Lines that switch from one weapon to another in days: production changes cost little.")
T(F, "streamlined_line", "Additive Mass Production", 2043, 1, icon="factory", req=["assembly_line_production"],
  excl=["flexible_line"],
  desc="Printers by the thousand turn out parts at scale: the most from every factory, but changes cost more.")
T(F, "val_industrial_ai", "Industrial AI", 2045, 0, icon="ai", req=["flexible_line", "streamlined_line"],
  desc="An AI runs the whole industrial base, from orders to machines: the frontier of production.",
  unl=["factory output and production efficiency higher (a new upgrade, very costly)"])
T(F, "improved_equipment_conversion", "Modular Retooling", 2037, 1, icon="gear", req=["improved_machine_tools"],
  desc="Modular tooling: converting equipment to a new variant takes less.")
T(F, "advanced_equipment_conversion", "Software-Defined Production", 2039, 1, icon="gear",
  desc="Most of a weapon's upgrade is software: conversions cost a fraction of new builds.")

F.section("Industrial policy", 2)
T(F, "concentrated_industry", "National Champions I", 2036, 2, icon="factory", req=["basic_machine_tools"],
  excl=["dispersed_industry"],
  desc="A few giant firms build most of the arms: efficient, and vulnerable to strikes on them.")
T(F, "concentrated_industry2", "National Champions II", 2037, 2, icon="factory",
  desc="State orders and finance concentrated on the champions.")
T(F, "concentrated_industry3", "National Champions III", 2039, 2, icon="factory",
  desc="The champions merge their supply chains into one.")
T(F, "concentrated_industry4", "National Champions IV", 2041, 2, icon="factory",
  desc="Gigafactories for missiles, drones and munitions.")
T(F, "concentrated_industry5", "National Champions V", 2043, 2, icon="factory",
  desc="The arsenal of the nation: a handful of plants that out-produce everyone.")
T(F, "dispersed_industry", "Distributed Manufacturing I", 2036, 3, icon="factory", req=["basic_machine_tools"],
  excl=["concentrated_industry"],
  desc="Many small firms and workshops build to shared designs: harder to hit, slower to start.")
T(F, "dispersed_industry2", "Distributed Manufacturing II", 2037, 3, icon="factory",
  desc="Open designs and printers in every town.")
T(F, "dispersed_industry3", "Distributed Manufacturing III", 2039, 3, icon="factory",
  desc="A supply network that routes around any broken link.")
T(F, "dispersed_industry4", "Distributed Manufacturing IV", 2041, 3, icon="factory",
  desc="Drones and munitions built in garages and schools, as in the wars of the 2020s.")
T(F, "dispersed_industry5", "Distributed Manufacturing V", 2043, 3, icon="factory",
  desc="An industry with no centre to strike.")

F.section("Construction & resources", 4)
T(F, "construction1", "Modular Construction", 2036, 4, icon="crane", req=[],
  desc="Buildings assembled from factory-made modules on site.")
T(F, "construction2", "Prefabricated Infrastructure", 2037, 4, icon="crane",
  desc="Bridges, rail and power lines from standard prefabricated parts.")
T(F, "construction3", "3D-Printed Structures", 2039, 4, icon="crane",
  desc="Concrete printers raise walls and bunkers in days.")
T(F, "construction4", "Autonomous Construction Machinery", 2041, 4, icon="crane",
  desc="Diggers, cranes and pavers that work round the clock without drivers.")
T(F, "construction5", "Robotic Construction Swarms", 2043, 4, icon="crane",
  desc="Fleets of construction robots build a factory in weeks.")
T(F, "excavation1", "Automated Mining", 2036, 5, icon="pick", req=["construction1"],
  desc="Driverless haul trucks and drills in the mines.")
T(F, "excavation2", "Deep Drilling", 2037, 5, icon="pick",
  desc="Deeper wells and shafts reach the ore and oil others can't.")
T(F, "excavation3", "Robotic Mining", 2039, 5, icon="pick",
  desc="Robots work seams too narrow and too dangerous for people.")
T(F, "excavation4", "Seabed Mining", 2041, 5, icon="pick",
  desc="Nodules and ores raised from the sea floor.")
T(F, "excavation5", "Tailings Recovery", 2043, 5, icon="pick",
  desc="Metals recovered from old mines' waste.")
T(F, "val_rare_earth", "Rare-Earth Refining", 2045, 5, icon="pick",
  desc="A refining industry of its own for the rare earths every missile and motor needs.",
  unl=["resources from mines higher (a new upgrade)"])

F.section("Fuel & synthetics", 6)
T(F, "fuel_silos", "Strategic Fuel Reserves", 2036, 6, icon="fuel", req=[],
  desc="Hardened, dispersed fuel stocks for months of war.")
T(F, "fuel_refining", "Catalytic Refining", 2036, 7, icon="fuel", req=["fuel_silos"],
  desc="More fuel from every barrel of crude.")
T(F, "fuel_refining2", "Hydrocracking", 2037, 7, icon="fuel", desc="Heavy oils cracked into jet fuel and diesel.")
T(F, "fuel_refining3", "Biorefining", 2039, 7, icon="fuel", desc="Fuel from crops and waste, made in the refinery.")
T(F, "fuel_refining4", "Synthetic Kerosene", 2041, 7, icon="fuel", desc="Jet fuel made from gas and coal.")
T(F, "fuel_refining5", "Power-to-Liquid Fuels", 2043, 7, icon="fuel",
  desc="Fuel made from electricity, water and air: no oil needed.")
T(F, "synth_oil_experiments", "Synthetic Fuels", 2036, 8, icon="oil", req=["fuel_silos"],
  desc="Plants that make fuel without crude oil: the synthetic refinery building.")
T(F, "oil_processing", "Coal-to-Liquids", 2037, 8, icon="oil", desc="Coal turned into fuel at scale.")
T(F, "improved_oil_processing", "Gas-to-Liquids", 2039, 8, icon="oil", desc="Natural gas turned into fuel.")
T(F, "advanced_oil_processing", "Algal Biofuels", 2041, 8, icon="oil", desc="Algae farms that grow fuel.")
T(F, "modern_oil_processing", "E-Fuels", 2043, 8, icon="oil", desc="Synthetic fuel made with cheap electricity.")
T(F, "rubber_processing", "Synthetic Rubber", 2037, 9, icon="tyre", req=["synth_oil_experiments"],
  desc="Rubber made in the refinery, for tyres, seals and hoses.")
T(F, "improved_rubber_processing", "Bio-Based Rubber", 2039, 9, icon="tyre", desc="Rubber from new crops and microbes.")
T(F, "advanced_rubber_processing", "Recycled Elastomers", 2041, 9, icon="tyre",
  desc="Old tyres and seals recycled into new rubber.")
T(F, "modern_rubber_processing", "Engineered Polymers", 2043, 9, icon="tyre",
  desc="Polymers designed for the job, better than natural rubber.")
