"""The naval folders (Man the Guns' ship designer): hulls, and the weapons and systems that go on them."""
from common import folder, T

# =============================================================================================================
F = folder("naval", "Naval", "mtgnavalfolder", "across", "frigate", "navy",
           "The ship designer's hulls, from the Cold War's gun battleship and missile battlecruiser to the arsenal "
           "ship, with the sensors and anti-submarine weapons that go with them.",
           dlc="Man the Guns (without it: Naval, classic)")

F.section("Escorts", 0)
T(F, "val_light_cw1", "Destroyer Escort", 1965, 0, icon="frigate", req=[],
  desc="Small gun-and-missile escorts built for convoy work in the 1960s, still the backbone of many coastal navies.",
  unl=["new equipment: ship_hull_light_cw1, the light hull's Cold War tier"])
T(F, "val_light_cw2", "Guided-Missile Frigate", 1985, 0, icon="frigate",
  desc="A frigate with a missile launcher, a helicopter and a towed sonar: the late Cold War's escort.",
  unl=["new equipment: ship_hull_light_cw2"])
T(F, "early_ship_hull_light", "Multi-Mission Frigate", 2025, 0, icon="frigate",
  desc="Today's frigate: vertical launch cells, a capable radar and room for drones.")
T(F, "basic_ship_hull_light", "Air-Defence Destroyer", 2036, 0, icon="frigate",
  desc="A large escort built around a powerful radar and a hundred missile cells, the fleet's shield.")
T(F, "improved_ship_hull_light", "Optionally Crewed Frigate", 2039, 0, icon="frigate",
  desc="A frigate that can sail with a crew of twenty, or none, on long patrols.")
T(F, "advanced_ship_hull_light", "Autonomous Escort", 2043, 0, icon="usv",
  desc="Uncrewed escorts that screen the fleet, hunt submarines and take the first hit.")
T(F, "smoke_generator", "Decoy Launchers", 1985, 1, icon="radar", req=["val_light_cw1"],
  desc="Chaff, flares and floating decoys that pull missiles away from the ship.")
T(F, "basic_depth_charges", "Anti-Submarine Rockets", 1965, 2, icon="torpedo", req=["val_light_cw1"],
  desc="Rocket-thrown depth bombs in a pattern ahead of the ship.")
T(F, "improved_depth_charges", "Lightweight ASW Torpedoes", 1985, 2, icon="torpedo",
  desc="Homing torpedoes fired from the deck or dropped by the ship's helicopter.")
T(F, "advanced_depth_charges", "Stand-Off ASW Missiles", 2025, 2, icon="torpedo",
  desc="A missile carries the torpedo to the submarine forty kilometres away.")
T(F, "modern_depth_charges", "ASW Drone Swarms", 2039, 2, icon="usv",
  desc="Small underwater drones that search, track and attack submarines as a pack.")
T(F, "sonar", "Hull Sonar", 1965, 3, icon="sonar", req=["val_light_cw1"],
  desc="An active sonar in the bow: the escort hears a submarine before it attacks.")
T(F, "improved_sonar", "Towed Array Sonar", 1985, 3, icon="sonar",
  desc="A long passive array towed far behind the ship, away from its own noise.")
T(F, "advanced_sonar", "Variable-Depth Sonar", 2025, 3, icon="sonar",
  desc="Sonar lowered below the layers that hide submarines from hull sets.")
T(F, "modern_sonar", "Seabed Sensor Networks", 2039, 3, icon="sonar",
  desc="Fields of sensors on the sea floor feed every ship the same picture of what moves below.")

F.section("Uncrewed vessels", 4)
T(F, "val_usv1", "Uncrewed Surface Vessels", 2025, 4, icon="usv", req=["early_ship_hull_light"],
  desc="Explosive drone boats and patrol drones: a coastal navy's cheapest way to sink a warship.",
  unl=["new hull: ship_hull_usv_1, a small uncrewed hull for the ship designer (no crew lost; screens and strike)",
       "new ship role: Uncrewed Surface Vessel"])
T(F, "val_usv2", "Large Uncrewed Surface Vessel", 2036, 4, icon="usv",
  desc="Corvette-sized drone ships carrying missile cells for the crewed fleet to fire.",
  unl=["new hull: ship_hull_usv_2"])
T(F, "val_usv3", "Drone Boat Swarms", 2039, 4, icon="usv",
  desc="Dozens of drone boats attack together and overwhelm a ship's defences.",
  unl=["uncrewed vessels: attack and evasion higher (a new upgrade)"])
T(F, "val_usv4", "Uncrewed Missile Vessel", 2042, 4, icon="usv", req=["val_usv2"],
  desc="Large drone ships with sixty missile cells, at a fraction of a destroyer's crew and cost.",
  unl=["new hull: ship_hull_usv_3"])

F.section("Cruisers", 5)
T(F, "val_cruiser_cw2", "Guided-Missile Cruiser", 1985, 5, icon="cruiser", req=["val_light_cw1"],
  desc="Big missile cruisers of the late Cold War, built to defend carriers against bomber raids.",
  unl=["new equipment: ship_hull_cruiser_cw2"])
T(F, "early_ship_hull_cruiser", "Missile Cruiser", 2025, 5, icon="cruiser",
  desc="Today's cruiser: over a hundred missile cells and the fleet's air-defence command.")
T(F, "basic_ship_hull_cruiser", "Large Missile Cruiser", 2036, 5, icon="cruiser",
  desc="A larger hull with power to spare for lasers and the next radars.")
T(F, "improved_ship_hull_cruiser", "Directed-Energy Cruiser", 2039, 5, icon="laser",
  desc="Built around lasers and microwave weapons, with missiles for what they can't stop.")
T(F, "advanced_ship_hull_cruiser", "Next-Generation Cruiser", 2043, 5, icon="cruiser",
  desc="Integrated electric power, its own drones and a magazine that recharges.")
T(F, "basic_cruiser_armor_scheme", "Splinter Protection", 2025, 6, icon="shield", req=["early_ship_hull_cruiser"],
  desc="Kevlar and steel over the vital spaces: a near miss no longer cripples the ship.")
T(F, "basic_heavy_armor_scheme", "Compartmentalised Hulls", 2036, 6, icon="shield", req=["basic_ship_hull_heavy"],
  desc="Big ships divided so that one hit floods and burns a section, not the ship.")
T(F, "improved_heavy_armor_scheme", "Integrated Survivability", 2040, 6, icon="shield",
  desc="Armour, damage control and redundancy designed in together: the ship fights on after a missile hit.")

F.section("Capital ships", 7)
T(F, "val_heavy_cw1", "Gun Battleship", 1965, 7, icon="battleship", req=[],
  desc="The last battleships, their big guns their only weapon: the first step on Valsora's tree (the author's).",
  unl=["new equipment: ship_hull_heavy_cw1, a battleship hull that mounts guns only"])
T(F, "val_heavy_cw2", "Missile Battlecruiser", 1985, 7, icon="battleship",
  desc="Nuclear-powered giants with twenty heavy anti-ship missiles, like the Kirov (the author's second step).",
  unl=["new equipment: ship_hull_heavy_cw2 (missile cells in the heavy battery slots)"])
T(F, "early_ship_hull_heavy", "Large Surface Combatant", 2025, 7, icon="battleship",
  desc="A modernised battlecruiser, or a new hull as big as one: long-range missiles and a flagship's sensors.")
T(F, "basic_ship_hull_heavy", "Guided-Missile Battleship", 2036, 7, icon="battleship",
  desc="Hypersonic missiles, a heavy gun and the first lasers on a hull built to take hits.")
T(F, "improved_ship_hull_heavy", "Arsenal Ship", 2040, 7, icon="battleship",
  desc="Hundreds of missile cells on a simple hull, fired on targets the rest of the fleet finds (the author's "
       "third step).")
T(F, "advanced_ship_hull_heavy", "Arsenal Ship II", 2043, 7, icon="battleship",
  desc="A stealthier, faster arsenal ship with its own defensive lasers.")

F.section("Carriers", 8)
T(F, "val_carrier_cw1", "Angled-Deck Carrier", 1965, 8, icon="carrier", req=[],
  desc="A carrier from the dawn of the jet age, still flying for navies that kept one.",
  unl=["new equipment: ship_hull_carrier_cw1"])
T(F, "val_carrier_cw2", "Supercarrier", 1985, 8, icon="carrier",
  desc="A big-deck carrier with catapults and ninety aircraft: the Cold War's capital ship.",
  unl=["new equipment: ship_hull_carrier_cw2"])
T(F, "early_ship_hull_carrier", "Through-Deck Conversions", 2025, 8, icon="carrier",
  desc="Big amphibious ships and hulls converted into light carriers for jump jets and drones.")
T(F, "basic_ship_hull_carrier", "Electromagnetic-Catapult Carrier", 2036, 8, icon="carrier",
  desc="Electromagnetic catapults launch heavier aircraft and drones, and more of them, every day.")
T(F, "improved_ship_hull_carrier", "Drone Carrier", 2039, 8, icon="carrier",
  desc="A carrier built for uncrewed aircraft: smaller deck crews, more aircraft, longer reach.")
T(F, "advanced_ship_hull_carrier", "Next-Generation Supercarrier", 2043, 8, icon="carrier",
  desc="A crewed and uncrewed air wing of a hundred, with laser defences and a reactor to power them.")
T(F, "sp_refined_pykrete", "Modular Sea Base Sections", 2042, 9, icon="carrier", req=["improved_ship_hull_carrier"],
  dlc="Needs the special project Mobile Offshore Base (Götterdämmerung)",
  desc="Floating sections that join into a runway and harbour far from any land.")
T(F, "sp_ice_composite_runawayas", "Floating Runways", 2044, 9, icon="carrier",
  dlc="Needs the special project Mobile Offshore Base (Götterdämmerung)",
  desc="A sea base long enough for transports and bombers: an airfield wherever the fleet needs one.")

F.section("Submarines", 10)
T(F, "val_sub_cw1", "Diesel-Electric Submarine", 1965, 10, icon="sub", req=[],
  desc="A post-war diesel boat: it must surface or snorkel to charge its batteries every day.",
  unl=["new equipment: ship_hull_submarine_cw1"])
T(F, "val_sub_cw2", "Quiet Diesel Submarine", 1985, 10, icon="sub",
  desc="A quiet, teardrop-hulled boat that is very hard to find when it lies still.",
  unl=["new equipment: ship_hull_submarine_cw2"])
T(F, "early_ship_hull_submarine", "Air-Independent Submarine", 2025, 10, icon="sub",
  desc="An air-independent plant lets the boat stay down for weeks.")
T(F, "basic_ship_hull_submarine", "Lithium-Battery Submarine", 2036, 10, icon="sub",
  desc="Lithium batteries: faster under water and longer submerged than any diesel boat before.")
T(F, "improved_ship_hull_submarine", "Long-Endurance Submarine", 2039, 10, icon="sub",
  desc="A larger boat with missile tubes and an uncrewed submarine it can launch.")
T(F, "advanced_ship_hull_submarine", "Next-Generation Submarine", 2043, 10, icon="sub",
  desc="Quieter than the sea around it, with its own drones to extend its senses.")
T(F, "basic_submarine_snorkel", "Low-Observable Masts", 2039, 11, icon="sub", req=["improved_ship_hull_submarine"],
  desc="Radar-absorbent masts and sensors: the boat looks without being seen.")
T(F, "improved_submarine_snorkel", "Pump-Jet Propulsors", 2043, 11, icon="sub",
  desc="A shrouded pump-jet in place of the propeller: faster, and quieter at speed.")
T(F, "sp_aip_engine_improved_tech", "Fuel-Cell AIP", 2039, 12, icon="engine", req=["basic_ship_hull_submarine"],
  dlc="Needs the special project Advanced AIP (Götterdämmerung)",
  desc="Hydrogen fuel cells for the air-independent plant: weeks under water at patrol speed.")
T(F, "sp_aip_engine_advanced_tech", "Closed-Cycle Engines", 2043, 12, icon="engine",
  dlc="Needs the special project Advanced AIP (Götterdämmerung)",
  desc="Closed-cycle engines that run fast and submerged for days.")

# =============================================================================================================
F = folder("naval_support", "Naval Systems", "mtgnavalsupportfolder", "across", "gun", "navy",
           "What goes on the hulls: guns, missiles and lasers, combat systems and damage control; sealift, "
           "replenishment and mines.", dlc="Man the Guns (without it, in the classic Naval folder)")

F.section("Naval guns", 0)
T(F, "basic_battery", "Naval Guns", 1965, 0, icon="gun", req=[], size="big",
  desc="Medium guns for escorts, heavy turrets for the last battleships: the ship designer's first weapons.")
T(F, "basic_light_battery", "Rapid-Fire Gun Mounts", 1985, 0, icon="gun",
  desc="Automatic 76 and 127 mm mounts that fire at aircraft, boats and the shore.")
T(F, "improved_light_battery", "Long-Range Naval Guns", 2025, 0, icon="gun",
  desc="Longer barrels and guided rounds reach a hundred kilometres inland.")
T(F, "advanced_light_battery", "Hypervelocity Gun Mounts", 2044, 0, icon="gun",
  desc="Guns firing hypervelocity projectiles: cheap rounds against missiles and drones.")
T(F, "basic_light_shell", "Guided Naval Rounds", 2005, 1, icon="gun", req=["basic_light_battery"],
  desc="Satellite-guided shells for the medium guns.")
T(F, "improved_light_shell", "Hypervelocity Projectiles", 2042, 1, icon="gun",
  desc="Dart-shaped rounds at Mach 6 from an ordinary gun.")
T(F, "basic_heavy_battery", "Heavy Gun Modernisation", 1985, 2, icon="gun", req=["basic_battery"],
  desc="New fire control and powder for the big guns that remain.")
T(F, "improved_heavy_battery", "Automated Heavy Turrets", 2039, 2, icon="gun",
  desc="Heavy turrets that load and fire without a crew in the gunhouse.")
T(F, "advanced_heavy_battery", "Long-Range Naval Fires", 2044, 2, icon="gun",
  desc="A heavy gun that throws guided rounds two hundred kilometres.")
T(F, "basic_heavy_shell", "Guided Heavy Shells", 2025, 3, icon="gun", req=["basic_heavy_battery"],
  desc="Guided rounds for the heavy guns: one hit where a salvo was needed.")
T(F, "improved_heavy_shell", "Rocket-Assisted Heavy Shells", 2042, 3, icon="gun",
  desc="Rocket-boosted heavy shells for shore bombardment from far out at sea.")

F.section("Missiles & directed energy", 4)
T(F, "basic_dp_light_battery", "Vertical-Launch Air Defence", 1985, 4, icon="missile", req=["basic_battery"],
  desc="Missile cells flush with the deck, fired in any direction: the end of the gun as the fleet's defence.")
T(F, "improved_dp_light_battery", "Active-Radar Interceptors", 2025, 4, icon="missile",
  desc="Interceptors with their own radar: the ship engages many targets at once, beyond its horizon.")
T(F, "advanced_dp_light_battery", "Ballistic Missile Defence", 2039, 4, icon="missile",
  desc="Interceptors that hit ballistic missiles outside the atmosphere.")
T(F, "basic_torpedo", "Anti-Ship Missiles", 1965, 5, icon="missile", req=[], size="big",
  desc="The first anti-ship missiles. Surface ships trade their torpedoes for missile launchers; submarines keep "
       "theirs.", note="The game's torpedo modules: on surface ships they become missile launchers.")
T(F, "improved_ship_torpedo_launcher", "Sea-Skimming Missiles", 1985, 5, icon="missile",
  desc="Missiles that fly a few metres over the waves, under the target's radar.")
T(F, "magnetic_detonator", "Active Terminal Seekers", 2005, 5, icon="missile",
  desc="Seekers that pick the ship out of the decoys in the last seconds.")
T(F, "advanced_ship_torpedo_launcher", "Supersonic Anti-Ship Missiles", 2025, 5, icon="missile",
  desc="Missiles at three times the speed of sound: a defender has seconds.")
T(F, "homing_torpedo", "Hypersonic Anti-Ship Missiles", 2036, 5, icon="missile",
  desc="Missiles at Mach 8 that manoeuvre in their final dive: very hard to stop.")
T(F, "modern_ship_torpedo_launcher", "Cooperative Swarm Missiles", 2044, 5, icon="missile",
  desc="Missiles that share targets in flight and arrive together from every direction.")
T(F, "val_naval_lacm", "Land-Attack Cruise Missiles", 1985, 6, icon="missile", req=["basic_torpedo"],
  desc="Cruise missiles from the ship's cells against targets a thousand kilometres inland.",
  unl=["new ship module: land-attack missile cells (shore bombardment and strikes on coastal states)"])
T(F, "val_naval_lacm2", "Long-Range Land Attack", 2040, 6, icon="missile",
  desc="Faster, stealthier land-attack missiles with longer reach.",
  unl=["land-attack missile cells: shore bombardment higher (a new upgrade)"])
T(F, "val_naval_laser1", "Shipboard Laser Point Defence", 2036, 7, icon="laser", req=["improved_dp_light_battery"],
  desc="Lasers that burn drones and small boats out of the sky and the water.",
  unl=["new ship module: laser point defence (anti-air, small and cheap to fire)"])
T(F, "val_naval_laser2", "High-Energy Laser Weapons", 2040, 7, icon="laser",
  desc="Lasers powerful enough to destroy anti-ship missiles in flight.",
  unl=["new ship module: high-energy laser (anti-air, light attack)"])
T(F, "val_naval_hpm", "Counter-Swarm Microwave", 2043, 7, icon="laser",
  desc="A microwave weapon that knocks down a whole swarm of drones at once.",
  unl=["laser modules: anti-air higher against swarms"])

F.section("Ship systems", 8)
T(F, "damage_control_1", "Damage Control Drills", 1965, 8, icon="shield", req=[],
  desc="Firefighting and flooding drills: the crew saves the ship.")
T(F, "damage_control_2", "Automated Firefighting", 2025, 8, icon="shield",
  desc="Sensors and sprinklers that fight fire before the crew reaches it.")
T(F, "damage_control_3", "Self-Healing Hull Systems", 2039, 8, icon="shield",
  desc="Systems that reroute power and water around damage by themselves.")
T(F, "sp_improved_repair_ship", "Forward Repair Ship II", 2042, 8, icon="wrench", req=["damage_control_3"],
  dlc="Needs the special project Fleet Support Ships (Götterdämmerung)",
  desc="A repair ship that mends battle damage at sea, far from the dockyards.")
T(F, "fire_control_methods_1", "Combat Information Centre", 1965, 9, icon="radar", req=[],
  desc="One room where every sensor and weapon of the ship comes together.")
T(F, "fire_control_methods_2", "Cooperative Engagement", 2025, 9, icon="network",
  desc="Ships share their radar tracks: one ship fires on what another sees.")
T(F, "fire_control_methods_3", "AI Battle Management", 2039, 9, icon="chip",
  desc="An AI weighs every threat and every weapon of the task force in a fraction of a second.")

F.section("Sealift & mines", 10)
T(F, "mtg_transport", "Sealift", 1965, 10, icon="cargo", req=[],
  desc="Roll-on, roll-off ships and chartered freighters carry the army overseas.")
T(F, "mtg_landing_craft", "Landing Craft and Floating Piers", 1985, 10, icon="cargo",
  desc="Air-cushion landing craft and floating causeways land a force where there is no port.")
T(F, "mtg_tank_landing_craft", "Ship-to-Shore Connectors", 2025, 10, icon="cargo",
  desc="Faster connectors that land tanks from over the horizon.")
T(F, "sp_improved_support_ship", "Fleet Support Ship II", 2042, 10, icon="cargo", req=["mtg_landing_craft"],
  dlc="Needs the special project Fleet Support Ships (Götterdämmerung)",
  desc="A support ship that keeps a task force supplied and fuelled far from home.")
T(F, "sp_multi_product_supply_ships", "Fleet Replenishment Oilers", 2038, 11, icon="cargo", req=["mtg_transport"],
  dlc="Needs the special project Fleet Replenishment (Götterdämmerung)",
  desc="Fast oilers carrying fuel, food and ammunition in one hull.")
T(F, "sp_standard_tenshioned_replenishment_alongside_method", "Automated Replenishment at Sea", 2043, 11,
  icon="cargo", dlc="Needs the special project Fleet Replenishment (Götterdämmerung)",
  desc="Automated rigs pass missiles and fuel between ships in rough seas.")
T(F, "basic_naval_mines", "Influence Mines", 1965, 12, icon="mine", req=[],
  desc="Mines that fire on a ship's magnetic and acoustic signature.")
T(F, "improved_naval_mines", "Rising Mines", 1985, 12, icon="mine",
  desc="Mines on the sea floor that launch a torpedo at whatever passes above.")
T(F, "advanced_naval_mines", "Smart Mines", 2025, 12, icon="mine",
  desc="Mines that count ships, choose their target and can be switched on and off.")
T(F, "airsweep_mines_bba", "Uncrewed Mine Countermeasures", 2036, 12, icon="usv", also=["airsweep_mines"],
  dlc="By Blood Alone has a module for it (demining_coil); without it the game's Aerial Minesweeping tech",
  desc="Drone boats and underwater drones find and destroy mines while the crews stay out of the minefield.")
T(F, "degaussing", "Signature Reduction", 2025, 13, icon="shield", req=["improved_naval_mines"],
  desc="Degaussing coils and quiet machinery: the ship hides from mines and sensors.")
T(F, "airdrop_mines_bba", "Air-Dropped Smart Mines", 2040, 13, icon="mine", req=["advanced_naval_mines"],
  also=["airdrop_mines"],
  dlc="By Blood Alone has a plane module for it (airdropped_mines); without it the game's Aerial Minelaying tech",
  desc="Guided mines dropped from aircraft, gliding kilometres to their place.")
T(F, "submarine_mine_laying", "Submarine-Laid Mines", 1965, 14, icon="mine", req=["basic_naval_mines"],
  desc="Submarines lay mines in the enemy's harbours unseen.")
T(F, "improved_submarine_mine_laying", "UUV-Laid Mines", 2040, 14, icon="mine",
  desc="Uncrewed submarines lay minefields deep in the enemy's waters.")
