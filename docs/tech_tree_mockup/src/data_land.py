"""The land folders: infantry, support, artillery, armour (the tank designer's tree, No Step Back)."""
from common import folder, T

# =============================================================================================================
F = folder("infantry", "Infantry", "infantry_folder", "across", "helmet", "army",
           "Small arms and the soldier's kit, the trucks and fighting vehicles that carry them, and the specialists.")

F.section("Small arms & infantry kit", 0)
# lane 0: crew-served weapons
T(F, "support_weapons", "Crew-Served Weapons", 2025, 0, icon="mg",
  desc="General-purpose machine guns, automatic grenade launchers and 81 mm mortars in a weapons platoon for every "
       "company: the firepower a section can't carry.", req=[])
T(F, "support_weapons2", "Precision Mortar Rounds", 2038, 0, icon="mg",
  desc="Guided mortar bombs land within a few metres: a platoon's mortar now does what the battalion's guns did.")
T(F, "support_weapons3", "Remote Weapon Stations", 2040, 0, icon="mg",
  desc="Stabilised, sensor-fed mounts on every vehicle and position; the gunner aims from under armour.")
T(F, "support_weapons4", "Networked Fire Teams", 2042, 0, icon="mg",
  desc="Every weapon in the company shares one fire-control picture, and the nearest free gun takes the target.")
# lane 1: small arms, the main line
T(F, "val_inf_cw1", "Battle Rifles", 1965, 1, icon="rifle", req=[],
  desc="Full-power 7.62 mm rifles, steel helmets and a radio per platoon: the kit of every army that has not changed "
       "much since the 1960s.",
  unl=["unit: infantry battalion (moved here from infantry_weapons, so every nation can raise infantry)",
       "new equipment: infantry_equipment_cw1, Battle Rifle Kit (below infantry_equipment_0)"])
T(F, "val_inf_cw2", "Assault Rifles", 1985, 1, icon="rifle",
  desc="Intermediate-calibre assault rifles, flak vests and a light machine gun in every section: the late Cold "
       "War's infantryman.",
  unl=["new equipment: infantry_equipment_cw2, Assault Rifle Kit"])
T(F, "val_inf_m1", "Modular Rifles", 2005, 1, icon="rifle",
  desc="Rails for red-dot sights and lights, ceramic plates and night vision for the section: the kit of the long "
       "wars of the 2000s.",
  unl=["new equipment: infantry_equipment_m1, Modular Rifle Kit"])
T(F, "infantry_weapons", "Digital Soldier Kit", 2025, 1, icon="rifle",
  desc="Thermal sights, a squad radio with a map on every chest, suppressed rifles in a lighter calibre: what most "
       "armies issue today.")
T(F, "infantry_weapons1", "Integrated Soldier System", 2036, 1, icon="helmet",
  desc="A fire-control optic that ranges the target, a helmet display fed by the platoon's drones, a rifle that "
       "won't fire until the shot is good.")
T(F, "infantry_weapons2", "Shared Sight Picture", 2038, 1, icon="optics",
  desc="Every sight in the section shares what it sees; the soldier with the best angle gets the target.")
T(F, "improved_infantry_weapons", "Next-Generation Squad Weapon", 2039, 1, icon="rifle",
  desc="A new high-pressure calibre with a ballistic computer in the sight: the body armour of the 2030s stops what "
       "came before, not this.")
T(F, "improved_infantry_weapons_2", "Lightweight Armour", 2040, 1, icon="shield",
  desc="Graphene-reinforced plates at half the weight: soldiers fight longer before they tire.")
T(F, "advanced_infantry_weapons", "Augmented Soldier", 2042, 1, icon="exo",
  desc="Passive exoskeleton frames, a power pack per soldier and sights that see through smoke and foliage.")
T(F, "advanced_infantry_weapons2", "Soldier Battle Network", 2044, 1, icon="network",
  desc="The soldier becomes a node of the brigade's network: targets passed up, fires called down in seconds.")
T(F, "val_inf_2045", "Next-Generation Infantry System", 2045, 1, icon="helmet", cost=3,
  desc="Adaptive camouflage panels, an autonomous loadout and a sight tied straight to the brigade's fires: the "
       "frontier of the infantry line, costly and late.",
  unl=["new equipment: infantry_equipment_4, the line's last tier (a fifth tier of the game's infantry equipment)"])
# lane 2: anti-armour
T(F, "val_inf_at_cw", "Rocket Launchers", 1965, 2, icon="atgm", req=["val_inf_cw1"],
  desc="A reloadable rocket launcher in every section and a recoilless rifle in every company.",
  unl=["infantry: hard attack and piercing (as the game's Infantry Anti-Tank I)"])
T(F, "infantry_at", "Fire-and-Forget Missiles", 2005, 2, icon="atgm", req=["val_inf_at_cw", "val_inf_m1"],
  desc="Shoulder-fired missiles that find their own way to the tank: the gunner fires and moves.")
T(F, "infantry_at2", "Top-Attack Missiles", 2025, 2, icon="atgm",
  desc="Missiles that climb and dive on the thin roof armour, out of reach of most active protection.")
T(F, "val_inf_at3", "Multi-Purpose Missiles", 2039, 2, icon="atgm",
  desc="One light launcher for tanks, bunkers, helicopters and drones, its seeker chosen at the moment of firing.",
  unl=["infantry: hard attack, piercing and air attack (a new upgrade)"])
# lane 3: optics
T(F, "night_vision", "Night Vision Goggles", 1985, 3, icon="optics", req=["val_inf_cw2"],
  desc="Image-intensifier goggles for the section leaders: the night stops being the enemy's.")
T(F, "night_vision2", "Thermal Sights", 2025, 3, icon="optics",
  desc="Thermal sights on every rifle and vehicle: heat shows through dark, smoke and camouflage nets.")
T(F, "val_night_vision3", "Fused Multispectral Goggles", 2040, 3, icon="optics",
  desc="Thermal and low-light images fused in one lens, with the platoon's positions drawn over them.",
  unl=["all land units: night attack penalty smaller (a third step of the game's night vision)"])

F.section("Mobility", 4)
T(F, "tech_trucks", "Military Trucks", 1965, 4, icon="truck", req=[],
  desc="Six-wheel cargo trucks for the divisions' supply and to lift a battalion when it must move fast.")
T(F, "motorised_infantry", "Protected Mobility", 2005, 4, icon="truck",
  desc="Mine-resistant, ambush-protected vehicles carry the infantry: slower than a truck, but they arrive.")
T(F, "val_mot_hybrid", "Hybrid-Electric Trucks", 2040, 4, icon="truck",
  desc="Hybrid drive halves the fuel bill and lets a column creep silently on its batteries.",
  unl=["motorised and mechanised: fuel use lower, speed higher (a new upgrade)"])
T(F, "mechanised_infantry", "Infantry Fighting Vehicles", 1985, 5, icon="ifv", req=["tech_trucks"],
  desc="Tracked vehicles with a cannon and a missile launcher that fight beside the tanks, the squad inside.")
T(F, "mechanised_infantry2", "Modern Infantry Fighting Vehicle", 2025, 5, icon="ifv",
  desc="A heavier hull, an unmanned turret and a sensor suite that sees as far as the tank's.")
T(F, "val_mech_aps", "Active Protection for IFVs", 2036, 5, icon="shield", req=["mechanised_infantry2"],
  desc="Radar-cued launchers shoot down incoming missiles and drones before they reach the hull.",
  unl=["mechanised: defence and hardness higher (a new upgrade; with No Step Back an IFV module instead)"])
T(F, "mechanised_infantry3", "Optionally Crewed Fighting Vehicle", 2039, 5, icon="ifv", req=["mechanised_infantry2"],
  desc="It fights with a crew or without one: the vehicle drops its squad and goes forward under remote control.")
T(F, "armored_car1", "Armoured Cars", 1965, 6, icon="armcar", req=[],
  desc="Light four-wheeled armour for scouting and for police work behind the front.", dlc="La Resistance")
T(F, "armored_car2", "Wheeled Reconnaissance Vehicles", 2005, 6, icon="armcar",
  desc="Fast, quiet scout cars with a mast-mounted sensor and an anti-tank missile.", dlc="La Resistance")
T(F, "armored_car3", "Wheeled Fire-Support Vehicles", 2025, 6, icon="armcar",
  desc="Eight wheels and a 120 mm gun: a tank's punch on a road vehicle's legs.", dlc="La Resistance")
T(F, "val_ac4", "Silent Recon Vehicles", 2040, 6, icon="armcar",
  desc="Electric drive and a tethered drone: the scout car that watches without being heard.", dlc="La Resistance",
  unl=["armoured cars: recon and speed higher (a new upgrade)"])
T(F, "amphibious_mechanized_infantry", "Amphibious Combat Vehicles", 2025, 7, icon="amphib",
  req=["mechanised_infantry"], dlc="Man the Guns",
  desc="Eight-wheeled armoured vehicles that swim from ship to shore and fight inland.")
T(F, "amphibious_mechanized_infantry_2", "Amphibious Combat Vehicle II", 2041, 7, icon="amphib", dlc="Man the Guns",
  desc="Faster in the water and armoured against drones: launched from beyond the horizon.")

F.section("Specialists", 8)
T(F, "marines", "Marines", 1985, 8, icon="marine", req=["val_inf_cw1"],
  desc="Infantry trained and equipped to land from the sea and take a shore.")
T(F, "marines2", "Amphibious Raiding", 2025, 8, icon="marine",
  desc="Small boats, tiltrotors and drones: marines land where the coast isn't defended.")
T(F, "marines3", "Littoral Regiments", 2039, 8, icon="marine",
  desc="Marines who hold islands and straits with their own anti-ship missiles and air defence.")
T(F, "tech_mountaineers", "Mountain Troops", 1985, 9, icon="mountain", req=["val_inf_cw1"],
  desc="Light infantry for heights, snow and cold, who climb where vehicles can't.")
T(F, "tech_mountaineers2", "High-Altitude Warfare", 2025, 9, icon="mountain",
  desc="Acclimatised battalions with oxygen, light artillery and cargo drones for the high passes.")
T(F, "tech_mountaineers3", "Alpine Drone Support", 2039, 9, icon="mountain",
  desc="Heavy-lift drones carry guns and supplies up to the ridgelines in hours instead of days.")
T(F, "paratroopers", "Airborne Forces", 1985, 10, icon="para", req=["val_inf_cw1"],
  desc="Infantry dropped by parachute behind the front to seize bridges, airfields and crossroads.")
T(F, "paratroopers2", "Air Assault", 2025, 10, icon="para",
  desc="Helicopters land the battalion together, with its weapons, in one lift.")
T(F, "paratroopers3", "Vertical Envelopment", 2039, 10, icon="para",
  desc="Tiltrotors carry a brigade two hundred kilometres deep in a night, under their own drones' cover.")
T(F, "rangers_tech", "Rangers", 2005, 11, icon="ranger", req=["val_inf_m1"], dlc="No Compromise, No Surrender",
  desc="Light raiding infantry for long patrols in forest, jungle and marsh.")
T(F, "rangers_tech2", "Long-Range Patrols", 2025, 11, icon="ranger", dlc="No Compromise, No Surrender",
  desc="Rangers who stay behind enemy lines for weeks, fed by airdrops and hidden caches.")
T(F, "rangers_tech3", "Jungle and Swamp Mastery", 2039, 11, icon="ranger", dlc="No Compromise, No Surrender",
  desc="Waterproof sensors, light boats and silent drones: the swamp belongs to whoever learned it first.")
T(F, "tech_special_forces", "Special Operations Forces", 2025, 12, icon="dagger", req=["val_inf_m1"],
  dlc="Not with Arms Against Tyranny (its Special Forces doctrines replace this line)",
  desc="A command of its own for the hardest raids, rescues and sabotage.")
T(F, "advanced_special_forces", "Direct Action", 2036, 12, icon="dagger", dlc="Not with Arms Against Tyranny",
  desc="Raiders trained to strike command posts and launch sites far behind the front.")
T(F, "improved_special_forces", "Expanded SOF Command", 2036, 13, icon="dagger", req=["tech_special_forces"],
  dlc="Not with Arms Against Tyranny",
  desc="More special forces battalions, with the support and aircraft of their own to use them.")
T(F, "extreme_environment_training", "Arctic and Desert Warfare", 2040, 12, icon="mountain",
  dlc="Not with Arms Against Tyranny",
  desc="Training at the extremes: the special forces fight where the weather stops everyone else.")
T(F, "survival_training", "Escape and Evasion", 2040, 13, icon="ranger", dlc="Not with Arms Against Tyranny",
  desc="Teams that come home: evasion, survival and recovery under the enemy's sensors.")
T(F, "elite_forces", "Tier-One Units", 2044, 12, icon="dagger",
  req=["extreme_environment_training", "survival_training"], dlc="Not with Arms Against Tyranny",
  desc="The few units every other army studies: the best training, the best kit, the hardest jobs.")

# =============================================================================================================
F = folder("support", "Support", "support_folder", "across", "engineer", "army",
           "The companies that make a division work: engineers, drones, police, maintenance, medics, logistics, "
           "signals and electronic warfare, air defence; and the railways.")

F.section("Support equipment & companies", 0)
T(F, "tech_support", "Support Equipment", 1965, 0, icon="crate", req=[],
  desc="Radios, tools, generators and field kitchens: the equipment every support company runs on.")
T(F, "tech_engineers", "Combat Engineers", 1985, 1, icon="engineer", req=["tech_support"],
  desc="Engineers who bridge rivers, clear mines and dig in a division in a night.")
T(F, "tech_engineers2", "Mine-Clearing Systems", 2025, 1, icon="engineer",
  desc="Rocket-propelled line charges and ploughs open a lane through a minefield in minutes.")
T(F, "sp_armored_engineer_tech", "Armoured Engineer Company", 2038, 1, icon="engineer", req=["tech_engineers2"],
  dlc="Needs the special project Combat Engineering Vehicles (Götterdämmerung)",
  desc="Breaching tanks and armoured bridgelayers that work under fire.")
T(F, "tech_engineers3", "Rapid Bridging", 2042, 1, icon="engineer",
  desc="Automated bridges span a river in minutes; the crossing no longer waits for night.")
T(F, "tech_engineers4", "Robotic Breaching", 2045, 1, icon="engineer",
  desc="Uncrewed breaching vehicles lead the way through mines and obstacles; the engineers follow.")

T(F, "tech_recon", "Reconnaissance Company", 1985, 2, icon="drone", req=["tech_support"],
  desc="Light vehicles and observers ahead of the division, who find the enemy before he finds it.")
T(F, "tech_recon2", "Small Reconnaissance Drones", 2025, 2, icon="drone",
  desc="Hand-launched drones and quadcopters give every company its own eyes over the next hill.")
T(F, "sp_helicopter_artillery_observers_tech", "Air Cavalry Troop", 2038, 2, icon="heli", req=["tech_recon2"],
  dlc="Needs the special project Tiltrotor Aircraft (Götterdämmerung)",
  desc="Scout tiltrotors and their drones scout far and fast, and spot for the guns.")
T(F, "tech_recon3", "Drone Reconnaissance Networks", 2042, 2, icon="drone",
  desc="Relays, long-endurance drones and ground sensors stitched into one live picture of the front.")
T(F, "tech_recon4", "Autonomous Scouting Swarms", 2045, 2, icon="drone",
  desc="Swarms that search a sector by themselves and report only what matters.")

T(F, "val_fpv_company", "FPV Strike Drones", 2025, 3, icon="fpv", req=["tech_recon"],
  desc="Cheap first-person-view drones with a warhead, flown by teams in every brigade: the weapon that changed the "
       "front lines of the 2020s.",
  unl=["new support company: FPV Strike Team (soft and hard attack, cheap, fragile)",
       "new equipment: fpv_drone_equipment_1, FPV Strike Drone"])
T(F, "val_fpv_fibre", "Fibre-Optic Guidance", 2036, 3, icon="fpv",
  desc="Drones steered down a spool of fibre: no signal to jam, and the target never hears them coming.",
  unl=["FPV teams: attack higher, less affected by enemy electronic warfare"])
T(F, "val_fpv_loiter", "Loitering Munitions", 2039, 3, icon="fpv",
  desc="Larger strike drones that circle for an hour and dive on whatever the operator picks.",
  unl=["FPV teams: hard attack and piercing higher"])
T(F, "val_fpv_autonomy", "Autonomous Terminal Guidance", 2042, 3, icon="fpv",
  desc="The drone finishes the attack by itself once the target is picked, even through jamming.",
  unl=["FPV teams: attack higher; enemy jamming has little effect"])
T(F, "val_fpv_swarm", "Strike Swarms", 2045, 3, icon="fpv",
  desc="Dozens of drones share one target list and attack from every side at once.",
  unl=["FPV teams: attack and breakthrough higher"])

T(F, "tech_military_police", "Military Police", 1985, 4, icon="police", req=["tech_support"],
  desc="Police for the army's own rear: traffic, prisoners and order in occupied towns.")
T(F, "tech_military_police2", "Biometric Screening", 2025, 4, icon="police",
  desc="Fingerprints and faces checked at every checkpoint: insurgents can't hide among the crowd so easily.")
T(F, "sp_armored_motorized_military_police_tech", "Motorised Military Police", 2038, 4, icon="police",
  req=["tech_military_police2"], dlc="Needs the special project Combat Engineering Vehicles (Götterdämmerung)",
  desc="Military police in light protected vehicles, fast enough to keep the supply roads open.")
T(F, "tech_military_police3", "Counter-Insurgency Networks", 2042, 4, icon="police",
  desc="Informants, surveillance and patrols tied together: resistance is found before it organises.")
T(F, "tech_military_police4", "Predictive Policing", 2045, 4, icon="police",
  desc="Pattern analysis tells the patrols where trouble will start, sometimes before it does.")

T(F, "tech_maintenance_company", "Maintenance Company", 1985, 5, icon="wrench", req=["tech_support"],
  desc="Mechanics and recovery vehicles that keep a division's equipment running.")
T(F, "tech_maintenance_company2", "Predictive Maintenance", 2025, 5, icon="wrench",
  desc="Sensors in every engine flag the failure before it happens; spares arrive before they're needed.")
T(F, "sp_armored_maintenance_tech", "Armoured Recovery Company", 2038, 5, icon="wrench",
  req=["tech_maintenance_company2"], dlc="Needs the special project Combat Engineering Vehicles (Götterdämmerung)",
  desc="Armoured recovery vehicles drag damaged tanks out of the fight and repair them close behind it.")
T(F, "tech_maintenance_company3", "Field Additive Manufacturing", 2042, 5, icon="wrench",
  desc="Printers in a container make spare parts at the front, from a file sent from the factory.")
T(F, "tech_maintenance_company4", "Autonomous Repair Robots", 2045, 5, icon="wrench",
  desc="Robots that diagnose and repair vehicles in the field, around the clock.")

T(F, "tech_field_hospital", "Field Hospital", 1985, 6, icon="medic", req=["tech_support"],
  desc="Surgeons and wards close behind the front: the wounded live and come back.")
T(F, "tech_field_hospital2", "Damage-Control Surgery", 2025, 6, icon="medic",
  desc="Surgical teams in the first hour, blood on the move: most of the wounded now survive.")
T(F, "sp_helicopter_med_evac_tech", "Air Ambulance Company", 2038, 6, icon="heli", req=["tech_field_hospital2"],
  dlc="Needs the special project Tiltrotor Aircraft (Götterdämmerung)",
  desc="Tiltrotor ambulances fly the badly wounded straight to the hospital.")
T(F, "tech_field_hospital3", "Medical Drones", 2042, 6, icon="medic",
  desc="Drones bring blood, drugs and splints to the wounded, and fly the urgent ones out.")
T(F, "tech_field_hospital4", "Regenerative Medicine", 2045, 6, icon="medic",
  desc="Synthetic blood, tissue printing and nerve repair: wounds that ended careers now heal.")

T(F, "tech_logistics_company", "Logistics Company", 1985, 7, icon="crate", req=["tech_support"],
  desc="Supply trucks and dumps of the division's own: it fights further from the railhead.")
T(F, "tech_logistics_company2", "Palletised Load Systems", 2025, 7, icon="crate",
  desc="Flat-racks and hook-lift trucks move a day's ammunition without a forklift.")
T(F, "sp_helicopter_transport_pods_tech", "Tiltrotor Lift Company", 2038, 7, icon="heli",
  req=["tech_logistics_company2"], dlc="Needs the special project Tiltrotor Aircraft (Götterdämmerung)",
  desc="Tiltrotors carry supplies over the broken roads straight to the units.")
T(F, "tech_logistics_company3", "Autonomous Convoys", 2042, 7, icon="truck",
  desc="Driverless supply trucks follow a lead vehicle night and day.")
T(F, "tech_logistics_company4", "Predictive Logistics", 2045, 7, icon="crate",
  desc="An AI plans the supply runs, and the ammunition is waiting where the fight will be.")

T(F, "tech_signal_company", "Signals Company", 1985, 8, icon="signal", req=["tech_support"],
  desc="Radio relays and command posts that keep the division's units in touch.")
T(F, "tech_signal_company2", "Electronic Warfare Company", 2025, 8, icon="jam",
  desc="The signals company gains jammers and direction-finders: it hears the enemy and blinds him.",
  note="The game's Signal Company becomes the Signals and Electronic Warfare Company here.")
T(F, "sp_armored_signal_tech", "Armoured Command Post", 2038, 8, icon="signal", req=["tech_signal_company2"],
  dlc="Needs the special project Combat Engineering Vehicles (Götterdämmerung)",
  desc="A mobile, armoured headquarters that commands on the move.")
T(F, "tech_signal_company3", "Cognitive Jamming", 2042, 8, icon="jam",
  desc="Jammers that learn the enemy's waveforms and change their attack as he changes his.")
T(F, "tech_signal_company4", "Spectrum Dominance", 2045, 8, icon="jam",
  desc="The division owns the airwaves around it: its own links stay up, the enemy's don't.")

T(F, "val_ew_jamming", "Drone Jamming", 2025, 9, icon="jam", req=["tech_signal_company"],
  desc="Portable and vehicle jammers cut drones off from their pilots.",
  unl=["divisions with the signals company: enemy drones and air support less effective (a new combat modifier)"])
T(F, "val_ew_spoofing", "Satellite Navigation Spoofing", 2036, 9, icon="jam",
  desc="False navigation signals send the enemy's drones and guided shells somewhere else.",
  unl=["enemy air and artillery attack lower against the division (a new combat modifier)"])
T(F, "val_ew_cyber", "Tactical Cyber Effects", 2040, 9, icon="cyber",
  desc="Cyber teams at brigade level break into the enemy's radios and battle networks.",
  unl=["enemy coordination and planning lower in the fight"])
T(F, "val_ew_counter", "Counter-Drone Electronic Attack", 2044, 9, icon="jam",
  desc="Electronic attack that takes over enemy drones and turns them back on their own side.",
  unl=["enemy FPV teams and drones much less effective"])

T(F, "val_ad_company", "Air Defence Company", 2025, 10, icon="aa", req=["tech_support"],
  desc="Short-range missiles, guns and radars of the division's own, against helicopters, jets and drones.",
  unl=["new support company: Air Defence Company, using the game's surface-to-air missile equipment "
       "(sam_missile_equipment_1, renamed Short-Range Air Defence Missile)"])
T(F, "val_ad_airburst", "Counter-Drone Guns", 2036, 10, icon="aa",
  desc="Programmable airburst rounds shred drones for the price of a few shells.",
  unl=["air defence company: air attack higher against drones"])
T(F, "val_ad_laser", "Laser Point Defence", 2039, 10, icon="laser",
  desc="Truck-mounted lasers burn down drones and rockets for the cost of the electricity.",
  unl=["air defence company: air attack higher; enemy air support less effective"])
T(F, "val_ad_hpm", "High-Power Microwave", 2042, 10, icon="laser",
  desc="A beam of microwaves fries the electronics of a whole swarm at once.",
  unl=["air defence company: much stronger against swarms"])

F.section("Railways", 11)
T(F, "basic_train", "Freight Rail", 1965, 11, icon="rail", req=[],
  desc="Diesel locomotives and flat cars move armies and their supply across a country.")
T(F, "armored_train", "Armoured Trains", 1985, 11, icon="rail", dlc="No Step Back",
  desc="Armoured locomotives and gun cars that guard the lines in the rear.")
T(F, "railway_gun", "Rail-Mobile Missile Battery", 2005, 11, icon="missile", req=["armored_train"],
  dlc="No Step Back",
  desc="Long-range rockets launched from trains that hide in tunnels between strikes.")
T(F, "wartime_train", "Heavy-Haul Freight", 2025, 11, icon="rail", req=["basic_train"],
  desc="Longer, heavier trains and faster loading: the railway carries a corps in a few days.")

# =============================================================================================================
F = folder("artillery", "Artillery", "artillery_folder", "down", "howitzer", "army",
           "Air defence, howitzers, rocket artillery and anti-armour missiles.")

F.section("Air defence", 0)
T(F, "interwar_antiair", "Anti-Aircraft Guns", 1965, 0, icon="aa", req=["gw_artillery"],
  desc="Radar-laid automatic cannon against aircraft flying low.")
T(F, "antiair1", "Radar-Directed Fire", 1985, 0, icon="radar",
  desc="Fire-control radars lay the guns: a battery engages fast jets at night.")
T(F, "antiair2", "Short-Range Air Defence", 2005, 0, icon="aa",
  desc="Shoulder-fired and vehicle-mounted missiles guard the brigade against aircraft and helicopters.")
T(F, "antiair3", "Programmable Airburst", 2025, 0, icon="aa",
  desc="Rounds that burst where the computer says: a cloud of fragments in front of a drone or missile.")
T(F, "antiair4", "Counter-Drone Fire Control", 2036, 0, icon="radar",
  desc="Small radars and AI tracking pick drones out of the clutter and hand them to the nearest gun.")
T(F, "antiair5", "Laser Air Defence", 2039, 0, icon="laser",
  desc="High-energy lasers in the batteries: a shot costs a few dollars, and the magazine never runs out.")
T(F, "val_aa_hpm", "High-Power Microwave Defence", 2042, 0, icon="laser",
  desc="Microwave emitters that knock down a whole swarm at once.",
  unl=["anti-air equipment: air attack higher (a new upgrade)"])
T(F, "sp_shock_hardening_techniques", "Shock-Hardened Seekers", 2041, 1, icon="aa", req=["antiair2"],
  dlc="Needs the special project Smart Munitions (Götterdämmerung)",
  desc="Seekers built to survive being fired from a gun: guided rounds for every air defence cannon.")
T(F, "sp_variable_time_fuze_shells", "Smart Airburst Shells", 2042, 1, icon="aa",
  dlc="Needs the special project Smart Munitions (Götterdämmerung)",
  desc="Shells that sense their target and burst at the best moment.")

F.section("Artillery", 2)
T(F, "gw_artillery", "Towed Howitzers", 1965, 2, icon="howitzer", req=[],
  desc="105 and 122 mm howitzers towed by trucks: the guns every army has.")
T(F, "interwar_artillery", "Counter-Battery Radar", 1985, 2, icon="radar",
  desc="Radars that trace enemy shells back to their guns, which are hit before they fire again.")
T(F, "artillery1", "155 mm Long-Barrel Howitzers", 2005, 2, icon="howitzer",
  desc="Long 155 mm barrels and automatic loaders: forty kilometres and six rounds a minute.")
T(F, "artillery2", "Satellite-Guided Shells", 2025, 2, icon="howitzer",
  desc="Guided shells hit the house, not the street: one round where twenty were fired.")
T(F, "artillery3", "Extended-Range Cannon", 2036, 2, icon="howitzer",
  desc="Longer barrels and rocket-assisted shells push the guns past seventy kilometres.")
T(F, "artillery4", "Robotic Howitzers", 2039, 2, icon="howitzer",
  desc="Uncrewed howitzers fire, move and reload on their own, controlled from a vehicle behind them.")
T(F, "artillery5", "Ramjet Shells", 2043, 2, icon="howitzer",
  desc="Shells with a ramjet sustainer reach a hundred and fifty kilometres from a normal gun.")
T(F, "sp_artillery_rocket_assisted_projectiles_tech", "Base-Bleed Long-Range Rounds", 2040, 3, icon="howitzer",
  req=["artillery3"], dlc="Needs the special project Long-Range Cannon (Götterdämmerung)",
  desc="Rounds for the long-range cannon project: further, with less wear on the barrels.")
T(F, "sp_artillery_purpose_built_gun_motor_carriages_tech", "Truck-Mounted Long-Range Guns", 2040, 4, icon="truck",
  req=["artillery3"], dlc="Needs the special project Self-Propelled Long-Range Cannon (Götterdämmerung)",
  desc="The long-range cannon on a wheeled chassis that fires and drives off before the counter-fire lands.")

F.section("Rockets", 5)
T(F, "rocket_artillery", "Multiple Rocket Launchers", 1965, 5, icon="mlrs", req=["gw_artillery"],
  desc="Truck-mounted launchers that saturate a square kilometre in a minute.")
T(F, "rocket_artillery2", "Guided Rockets", 2005, 5, icon="mlrs",
  desc="Satellite-guided rockets turn area fire into precision strikes seventy kilometres away.")
T(F, "rocket_artillery3", "Precision Strike Missiles", 2025, 5, icon="missile",
  desc="Two missiles to a pod, five hundred kilometres: headquarters and depots far behind the front are in reach.")
T(F, "val_rocket_loiter", "Loitering Munition Launchers", 2036, 5, icon="fpv",
  desc="Launchers that fire long-range strike drones, which search for targets by themselves.",
  unl=["rocket artillery: attack higher against armour and artillery (a new upgrade)"])
T(F, "rocket_artillery4", "Long-Range Fires", 2039, 5, icon="mlrs",
  desc="A strategic rocket force on wheels: launchers that fire a thousand kilometres and drive away.")
T(F, "val_rocket_hypersonic", "Hypersonic Fires", 2045, 5, icon="missile",
  desc="Rockets that glide at five times the speed of sound: the target has seconds of warning.",
  unl=["rocket artillery: attack and range higher; enemy air defence can't intercept them (a new upgrade)"])

F.section("Anti-armour", 6)
T(F, "interwar_antitank", "Recoilless Anti-Tank Guns", 1965, 6, icon="atgm", req=["gw_artillery"],
  desc="Recoilless rifles on jeeps and tripods: a light way to kill tanks.")
T(F, "antitank1", "Wire-Guided Missiles", 1985, 6, icon="atgm",
  desc="Missiles steered down a wire: hits at four kilometres, out of the tank's reach.")
T(F, "antitank2", "Fire-and-Forget Missile Teams", 2005, 6, icon="atgm",
  desc="Anti-tank missile teams whose missiles find their own way, so the team can hide again at once.")
T(F, "antitank3", "Top-Attack Warheads", 2025, 6, icon="atgm",
  desc="Missiles that strike the thin roof of the tank.")
T(F, "antitank4", "Tandem Warheads", 2036, 6, icon="atgm",
  desc="A first charge for the reactive armour and the active protection, a second for the hull.")
T(F, "antitank5", "Non-Line-of-Sight Missiles", 2039, 6, icon="atgm",
  desc="Missiles fired over the hill at targets the team never sees, picked out by a drone.")
T(F, "sp_advance_sabot_shells", "Kinetic Energy Missiles", 2042, 7, icon="atgm", req=["antitank4"],
  dlc="Needs the special project Electromagnetic Railgun (Götterdämmerung)",
  desc="Hypervelocity missiles with no warhead: a solid rod at Mach 6 that no armour stops.")

# =============================================================================================================
F = folder("armour", "Armour", "nsb_armour_folder", "down", "tank", "army",
           "The tank designer's chassis, engines and armour: light tanks, main battle tanks, heavy assault tanks, and "
           "what the Assault Mech project unlocks.", dlc="No Step Back (without it: Armour, classic)")

F.section("Light", 0)
T(F, "basic_light_tank_chassis", "Light Tank", 1985, 0, icon="tank_l", req=["gwtank_chassis"],
  desc="A light, air-portable tank for scouting and for armies that can't afford main battle tanks.")
T(F, "improved_light_tank_chassis", "Airmobile Light Tank", 2025, 0, icon="tank_l",
  desc="A tank light enough to fly in a transport, with a gun that still kills bunkers and older armour.")
T(F, "advanced_light_tank_chassis", "Robotic Combat Vehicle", 2041, 0, icon="ugv",
  desc="An uncrewed light chassis that scouts and fights ahead of the crewed tanks.")
T(F, "amphibious_tank_chassis", "Amphibious Light Tank", 2025, 1, icon="amphib", req=["improved_light_tank_chassis"],
  dlc="Man the Guns", desc="A light tank that swims ashore with the marines.")
T(F, "amphibious_drive", "Deep-Wading Kits", 2041, 1, icon="amphib",
  desc="Snorkels and flotation for every chassis: rivers stop being obstacles.")

F.section("Main battle tanks", 2)
T(F, "gwtank_chassis", "Cold War Armour", 1965, 2, icon="tank", req=[],
  desc="The tank designer's first chassis: second-generation main battle tanks with a 105 mm gun, and the light and "
       "heavy chassis beside them. Every army has them, the poorest still fields them.",
  note="Also unlocks the designer's first modules (turrets, suspensions, engines, armour), renamed.")
T(F, "val_mbt_3gen", "Third-Generation MBT", 1985, 2, icon="tank",
  desc="Composite armour, a 120 mm smoothbore and a thermal sight: the tanks that ended the Cold War.",
  unl=["new equipment: medium_tank_chassis_cw2 (and its tank destroyer, artillery and air defence chassis), a tier "
       "below the game's medium_tank_chassis_1"])
T(F, "val_mbt_3plus", "Upgraded Third-Generation MBT", 2005, 2, icon="tank",
  desc="Digital fire control, reactive armour and a remote weapon station on the same old hulls.",
  unl=["new equipment: medium_tank_chassis_m1 (and its variants)"])
T(F, "basic_medium_tank_chassis", "Modernised MBT", 2025, 2, icon="tank",
  desc="Today's main battle tank: hunter-killer sights, a battle management system and active protection ready.")
T(F, "improved_medium_tank_chassis", "Fourth-Generation MBT", 2036, 2, icon="tank",
  desc="A new hull built around a 130 mm gun, an autoloader and active protection: the superpowers' first.")
T(F, "advanced_medium_tank_chassis", "Unmanned-Turret MBT", 2042, 2, icon="tank",
  desc="The crew sits in an armoured capsule in the hull; the turret holds only the gun.")
T(F, "main_battle_tank_chassis", "Next-Generation MBT", 2045, 2, icon="tank",
  req=["advanced_medium_tank_chassis", "advanced_heavy_tank_chassis"],
  desc="Hybrid drive, a 140 mm gun, its own drones and a crew of two: the frontier of the armour line.")

F.section("Components", 3)
T(F, "engine_tech_1", "Compact Power Packs", 2025, 3, icon="engine", req=["gwtank_chassis"],
  desc="Smaller diesel power packs leave room for armour and ammunition.")
T(F, "engine_tech_2", "Hybrid-Electric Drive", 2038, 3, icon="engine",
  desc="Electric motors and batteries: silent watch, sprint power and less fuel.")
T(F, "engine_tech_3", "Silent Mobility", 2041, 3, icon="engine",
  desc="Tanks that creep up to their positions on battery power, unheard and cool to thermal sights.")
T(F, "engine_tech_4", "All-Electric Drive", 2044, 3, icon="engine",
  desc="Compact generators and in-hub motors replace the gearbox altogether.")
T(F, "armor_tech_1", "Composite Armour", 1985, 4, icon="shield", req=["gwtank_chassis"],
  desc="Layers of ceramic and steel stop shaped charges that cut through steel alone.")
T(F, "armor_tech_2", "Reactive Armour", 2025, 4, icon="shield",
  desc="Explosive tiles that break up an incoming warhead before it reaches the armour.")
T(F, "armor_tech_3", "Active Protection Systems", 2036, 4, icon="shield",
  desc="Radar-cued launchers shoot down missiles and drones in the last metres.")
T(F, "armor_tech_4", "Adaptive Armour", 2044, 4, icon="shield",
  desc="Metamaterial layers that harden where they're hit and hide the tank from thermal sights.")

F.section("Heavy", 5)
T(F, "basic_heavy_tank_chassis", "Heavy Assault Tank", 2025, 5, icon="tank_h", req=["gwtank_chassis"],
  desc="Seventy tonnes of armour for breaking fortified lines: slow, thirsty, very hard to kill.")
T(F, "improved_heavy_tank_chassis", "Heavy Assault Tank II", 2040, 5, icon="tank_h",
  desc="Heavier protection against top attack, and the room for a bigger gun.")
T(F, "advanced_heavy_tank_chassis", "Heavy Assault Tank III", 2043, 5, icon="tank_h",
  desc="The heaviest tank still practical to build: a breakthrough vehicle for the strongest defences.")
T(F, "super_heavy_tank_chassis", "Siege Tank", 2041, 6, icon="tank_h", req=["improved_heavy_tank_chassis"],
  desc="A super-heavy vehicle for fortress lines and cities: few, slow and fearsome.")
T(F, "sp_armored_advanced_flamethrower_tech", "Thermobaric Rocket Launcher", 2041, 7, icon="flame",
  req=["gwtank_chassis"], dlc="Needs the special project Thermobaric Launcher (Götterdämmerung)",
  desc="A tank chassis carrying thermobaric rockets that clear trenches and buildings.")

F.section("Assault Mech", 8)
T(F, "sp_armored_lc_naval_engine_conversion_tech", "Mech Power Plant", 2043, 8, icon="mech",
  req=["super_heavy_tank_chassis"], dlc="Needs the special project Assault Mech (Götterdämmerung)",
  desc="A compact turbine-electric plant that gives the walker the power to stride and fight.")
T(F, "sp_armored_lc_transmission_improvements_tech", "Leg Actuators", 2043, 9, icon="mech",
  req=["super_heavy_tank_chassis"], dlc="Needs the special project Assault Mech (Götterdämmerung)",
  desc="Stronger, faster actuators: the mech climbs slopes and rubble that stop tracks.")
T(F, "sp_armored_lc_specialized_field_manuals_tech", "Mech Crew Training", 2043, 10, icon="mech",
  req=["super_heavy_tank_chassis"], dlc="Needs the special project Assault Mech (Götterdämmerung)",
  desc="Crews and maintainers trained for a machine no army has fought with before.")
T(F, "sp_armored_lc_weapon_fire_control_tech", "AI Co-Pilot", 2045, 9, icon="chip",
  req=["sp_armored_lc_naval_engine_conversion_tech", "sp_armored_lc_transmission_improvements_tech",
       "sp_armored_lc_specialized_field_manuals_tech"],
  dlc="Needs the special project Assault Mech (Götterdämmerung)",
  desc="An AI that balances the mech, picks targets and fires while the pilot commands.")
T(F, "sp_armored_lc_high_impact_obliterator_cannon_tech", "Mech Hypervelocity Gun", 2045, 8, icon="mech",
  req=["sp_armored_lc_naval_engine_conversion_tech"], dlc="Needs the special project Assault Mech (Götterdämmerung)",
  desc="A hypervelocity cannon on the mech's shoulder, powered by its own plant.")
