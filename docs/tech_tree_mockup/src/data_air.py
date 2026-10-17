"""The air folder (By Blood Alone's plane designer): airframes, drones, weapons and engines."""
from common import folder, T

F = folder("air", "Air", "bba_air_techs_folder", "down", "jet", "air",
           "The plane designer's airframes, all jets from the start (fighters, drones, strike aircraft, bombers, "
           "airlifters), their missiles and bombs, and their engines.",
           dlc="By Blood Alone (without it: Air, classic)")

F.section("Airframes", 0)
# col 0: small airframe (fighters; also the strike, maritime, one-way attack and carrier versions of each tier)
T(F, "val_small_cw1", "Third-Generation Fighter", 1965, 0, icon="jet", req=["engines_1"],
  desc="Supersonic interceptors and fighter-bombers of the 1960s, radar and missiles bolted on: still flown by the "
       "poorest air forces.",
  unl=["new equipment: small_plane_airframe_cw1 and its versions (a tier below small_plane_airframe_0)"])
T(F, "val_small_cw2", "Fourth-Generation Fighter", 1985, 0, icon="jet",
  desc="Agile, fly-by-wire fighters with look-down radar: the F-16 and MiG-29 generation.",
  unl=["new equipment: small_plane_airframe_cw2 and its versions"])
T(F, "val_small_m1", "Generation 4.5 Fighter", 2005, 0, icon="jet",
  desc="Composite airframes, electronic radars and long-range missiles: what most air forces fly today.",
  unl=["new equipment: small_plane_airframe_m1 and its versions"])
T(F, "iw_small_airframe", "Fifth-Generation Fighter", 2025, 0, icon="jet",
  desc="Stealth, sensor fusion and internal weapons bays: today's best fighters.",
  note="Each small airframe tier also comes as a ground-attack, maritime strike, one-way attack drone and carrier "
       "version (the game's CAS, naval bomber, suicide and carrier airframes).")
T(F, "basic_small_airframe", "Sixth-Generation Fighter", 2036, 0, icon="jet",
  desc="A tailless stealth fighter that commands its own drone wingmen: the superpowers' newest.")
T(F, "improved_small_airframe", "Sixth-Generation Fighter, Block II", 2040, 0, icon="jet",
  desc="Longer range, adaptive engines and more power for sensors and lasers.")
T(F, "advanced_small_airframe", "Optionally Crewed Fighter", 2044, 0, icon="jet",
  desc="A fighter that flies with a pilot or without one, as the mission needs.")
T(F, "modern_small_airframe", "Seventh-Generation Fighter", 2045, 0, icon="jet",
  dlc="Needs the special project Adaptive-Cycle Engine (Götterdämmerung)",
  desc="Hypersonic dash, directed-energy defences and an AI pilot beside the human one.")
# col 1: drones (new)
T(F, "val_uav1", "Armed Long-Endurance Drones", 2005, 1, icon="drone_l", req=["val_small_cw2"],
  desc="Propeller drones that circle for a day and strike with small guided missiles: cheap air power for any "
       "nation.",
  unl=["new airframe: drone_airframe_1 (an uncrewed airframe: slow, long range, no pilot losses; ground attack and "
       "reconnaissance modules)"])
T(F, "val_uav2", "Jet-Powered Combat Drones", 2025, 1, icon="drone_l",
  desc="Jet drones that fly with the strike packages and go where a pilot shouldn't.",
  unl=["new airframe: drone_airframe_2"])
T(F, "val_uav3", "Collaborative Combat Aircraft", 2036, 1, icon="drone_l", req=["val_uav2", "basic_small_airframe"],
  desc="Drone wingmen flying beside sixth-generation fighters: they scout, jam and fire on the fighter's command.",
  unl=["new airframe: drone_airframe_3, the drone wingman",
       "fighters with it in their wing: air attack and agility higher (a new modifier)"])
T(F, "val_uav4", "Stealth Combat Drones", 2040, 1, icon="drone_l",
  desc="Tailless stealth drones that penetrate the enemy's air defences ahead of the crewed aircraft.",
  unl=["new airframe: drone_airframe_4"])
T(F, "val_uav5", "Autonomous Air Combat", 2044, 1, icon="drone_l",
  desc="Drones that fight air battles by themselves, faster than a pilot can think.",
  unl=["drone airframes: air attack and agility higher (a new upgrade)"])
# col 2: medium airframe (strike aircraft; heavy interceptors and AEW/ISR aircraft are its other versions)
T(F, "val_med_cw1", "Strike Bomber", 1965, 2, icon="jet_m", req=["engines_1"],
  desc="Supersonic strike aircraft built to fly low under the radar with bombs.",
  unl=["new equipment: medium_plane_airframe_cw1 and its versions"])
T(F, "val_med_cw2", "Multirole Strike Aircraft", 1985, 2, icon="jet_m",
  desc="Two-seat strike aircraft with terrain-following radar and precision weapons.",
  unl=["new equipment: medium_plane_airframe_cw2 and its versions"])
T(F, "iw_medium_airframe", "Heavy Strike Fighter", 2025, 2, icon="jet_m",
  desc="Big twin-engine fighters carrying heavy loads far: today's strike aircraft.",
  note="Each medium airframe tier also comes as a heavy interceptor and an airborne early warning and reconnaissance "
       "version (the game's heavy fighter and scout plane airframes).")
T(F, "basic_medium_airframe", "Long-Range Strike Fighter", 2036, 2, icon="jet_m",
  desc="Stealthy, with the range to strike deep and the weapons bay for hypersonic missiles.")
T(F, "improved_medium_airframe", "Stealth Strike Aircraft", 2040, 2, icon="jet_m",
  desc="A strike aircraft built from the start for stealth and stand-off weapons.")
T(F, "advanced_medium_airframe", "Penetrating Strike Aircraft", 2044, 2, icon="jet_m",
  desc="It flies through the densest air defences with its own drones as decoys.")
T(F, "modern_medium_airframe", "Hypersonic Strike Aircraft", 2045, 2, icon="jet_m",
  dlc="Needs the special project Combined-Cycle Engine (Götterdämmerung)",
  desc="A strike aircraft that cruises at Mach 5: the target has no time to react.")
# col 3: large airframe (bombers; maritime patrol is its other version)
T(F, "val_large_cw1", "Jet Bomber", 1965, 3, icon="bomber", req=["engines_1"],
  desc="Big subsonic jet bombers built to carry nuclear weapons across a continent.",
  unl=["new equipment: large_plane_airframe_cw1 and its maritime patrol version"])
T(F, "val_large_cw2", "Supersonic Bomber", 1985, 3, icon="bomber",
  desc="Swing-wing bombers that dash in low and fast with cruise missiles.",
  unl=["new equipment: large_plane_airframe_cw2"])
T(F, "iw_large_airframe", "Strategic Bomber", 2025, 3, icon="bomber",
  desc="Modernised long-range bombers firing cruise missiles from far outside the enemy's defences.",
  note="Each large airframe tier also comes as a maritime patrol version (the game's patrol plane airframe).")
T(F, "basic_large_airframe", "Stealth Bomber", 2036, 3, icon="bomber",
  desc="A flying-wing bomber that reaches any target on the planet unseen.")
T(F, "improved_large_airframe", "Stealth Bomber II", 2040, 3, icon="bomber",
  desc="A larger stealth bomber with room for drones, sensors and a big weapons load.")
T(F, "advanced_large_airframe", "Global Strike Bomber", 2044, 3, icon="bomber",
  desc="A bomber that flies around the world and launches swarms of missiles and drones.")
T(F, "modern_large_airframe", "Hypersonic Bomber", 2045, 3, icon="bomber",
  dlc="Needs the special project Combined-Cycle Engine (Götterdämmerung)",
  desc="A bomber at hypersonic speed, out of reach of every interceptor.")
# col 4: transports
T(F, "bba_early_transport_plane", "Tactical Airlifter", 1965, 4, icon="cargo_air", req=[],
  desc="Four-engine turboprop transports that land on rough strips with a company and its kit.")
T(F, "bba_improved_transport_plane", "Strategic Airlifter", 2005, 4, icon="cargo_air",
  desc="Jet airlifters that carry a tank across an ocean and land it on a short runway.")
T(F, "bba_strategic_airlifter", "Next-Generation Airlifter", 2036, 4, icon="cargo_air",
  desc="Faster, longer-ranged airlifters with self-protection, and a few wide-bodied ones for whole battalions.")

F.section("Weapons", 5)
T(F, "early_bombs", "Unguided Bombs", 1965, 5, icon="bomb", req=[],
  desc="Iron bombs and racks: cheap, and only accurate against what's large.")
T(F, "armor_piercing_bombs", "Laser-Guided Bombs", 1985, 5, icon="bomb",
  desc="Bombs that follow a laser spot onto bridges, bunkers and tanks.")
T(F, "heavy_bombs", "Satellite-Guided Bombs", 2005, 5, icon="bomb",
  desc="Satellite-guided bombs dropped through cloud and smoke, by day or night.")
T(F, "val_bombs_glide", "Long-Range Glide Bombs", 2025, 5, icon="bomb",
  desc="Wing kits turn old bombs into glide weapons that fly seventy kilometres to their target.",
  unl=["plane modules: bomb racks gain range and accuracy (a new upgrade)"])
T(F, "val_bombs_sdb", "Networked Small Bombs", 2039, 5, icon="bomb",
  desc="Small, smart bombs that share targets in flight: one aircraft hits a whole column.",
  unl=["plane modules: ground attack higher (a new upgrade)"])
T(F, "aa_lmg", "Heat-Seeking Missiles", 1965, 6, icon="aam", req=[],
  desc="Short-range missiles that home on an engine's heat.")
T(F, "aa_hmg", "Radar-Guided Missiles", 1985, 6, icon="aam",
  desc="Missiles guided by radar beyond visual range: the fight starts before the pilots see each other.")
T(F, "aa_cannon_2", "Long-Range Air-to-Air Missiles", 2025, 6, icon="aam", req=["aa_hmg"],
  desc="Ramjet missiles with a hundred-and-fifty-kilometre reach and a no-escape zone to match.")
T(F, "val_aam_ai", "AI-Guided Missiles", 2042, 6, icon="aam",
  desc="Missiles that pick the real target out of the decoys and coordinate their attack.",
  unl=["plane modules: air attack higher (a new upgrade)"])
T(F, "aa_cannon_1", "Aircraft Cannon", 1985, 7, icon="gun_air", req=["aa_lmg"],
  desc="Rotary cannon for dogfights and for strafing.")
T(F, "aa_cannon_3", "Smart Gun Pods", 2036, 7, icon="gun_air",
  desc="Gun pods with programmable rounds that shred drones and soft targets.")
T(F, "air_torpedoe_1", "Air-Launched Anti-Ship Missiles", 1985, 8, icon="missile", req=[],
  desc="Sea-skimming missiles launched by aircraft against ships.")
T(F, "air_torpedoe_2", "Long-Range Anti-Ship Missiles", 2025, 8, icon="missile",
  desc="Stealthy anti-ship missiles that find their own way to the fleet.")
T(F, "air_torpedoe_3", "Air-Launched Hypersonic Missiles", 2040, 8, icon="missile",
  desc="Hypersonic missiles from aircraft: a fleet has seconds to defend itself.")
T(F, "photo_reconnaisance", "Reconnaissance Pods", 1965, 9, icon="optics", req=[], dlc="La Resistance",
  desc="Camera and radar pods for any fighter: every air force can see the other side.")

F.section("Engines & systems", 10)
T(F, "engines_1", "Turbojets", 1965, 10, icon="engine", req=[],
  desc="Turbojet engines with afterburners: every airframe on the tree is a jet from the start.")
T(F, "engines_2", "Afterburning Turbofans", 1985, 10, icon="engine",
  desc="Turbofans with afterburners: more thrust, more range, less fuel.")
T(F, "engines_3", "Supercruise Engines", 2025, 10, icon="engine",
  desc="Engines that hold supersonic speed without the afterburner.")
T(F, "engines_4", "Advanced Turbofans", 2036, 10, icon="engine",
  desc="Hotter cores and better cooling: more power for sensors and weapons.")
T(F, "sp_centrifugal_jet_tech", "Adaptive-Cycle Engines", 2045, 10, icon="engine",
  dlc="Needs the special project Adaptive-Cycle Engine (Götterdämmerung)",
  desc="Engines that change their cycle in flight: the range of a cruiser, the speed of a fighter.")
T(F, "range_improvements", "Aerial Refuelling", 1985, 11, icon="jet", req=["engines_1"],
  desc="Tankers and conformal tanks extend every aircraft's reach.")
T(F, "survivability_studies", "Survivability Suites", 2005, 11, icon="shield",
  desc="Radar-absorbent coatings, armour for the vital parts and laser defences against missiles.")
T(F, "aircraft_construction", "Composite Airframes", 2025, 11, icon="jet",
  desc="Composite structures and modular bays: the designer's new airframe options.")
T(F, "reinforced_wings_mothership", "Drone Mothership Bays", 2042, 12, icon="drone_l",
  req=["improved_large_airframe"], dlc="Needs the special project Drone Mothership (Götterdämmerung)",
  desc="Bomber-sized aircraft that carry drones in their bays and launch them in flight.")
T(F, "miniature_fighters", "Air-Launched Drones", 2044, 12, icon="drone_l",
  dlc="Needs the special project Drone Mothership (Götterdämmerung)",
  desc="Small fighter drones launched from the mothership, then recovered for the next mission.")
T(F, "aerial_hangars", "Airborne Drone Carrier", 2046, 12, icon="drone_l",
  dlc="Needs the special project Drone Mothership (Götterdämmerung)",
  desc="A flying carrier for a whole squadron of drones, which it launches, recovers and rearms.")
