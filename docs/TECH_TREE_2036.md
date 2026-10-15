# A tech tree for 2036: proposal

The author's request (2026-10-15): "a written proposal for the 2036 tech tree", and later the same night: special
projects, "for example, mechs. Or maybe an orbital kinetic bombardment weapon that acts sort of like a nuke". Nothing here
is built yet; it is a plan to react to. The questions at the end decide most of it.

## Where it stands

Valsora ships the base game's tree (1.19.3), moved a hundred years (`vanilla_parts.py`, since 2026-10-14):

- **13 technology files, about 506 dated technologies**: infantry (87 entries), support (45), artillery (33),
  armour (the classic tree and No Step Back's tank designer), naval (the classic tree and Man the Guns' ship
  designer), air (the classic tree and By Blood Alone's plane designer), electronics (42), industry (43), and
  special projects (6). Which variant a player sees depends on their DLCs.
- **Doctrines** are the 1.19 doctrine system: 4 folders (land, naval, air, special forces), 12 grand doctrines,
  14 tracks, 95 subdoctrines.
- **47 equipment archetypes**, among them some later ones the base game added with its special projects:
  helicopters, surface-to-air missiles, guided, ballistic and nuclear missiles.
- **Already 2036:** every `start_year` (so the research penalty for being ahead of time works), the tree's year
  labels, and the names with years in them ("2036 Cruiser Hull"). Equipment keeps the game's internal `year`,
  because licence costs count from 1936.

What still says the 1940s: almost every **name** ("Improved Infantry Equipment II", "Inter-War Artillery",
"Interwar Fighter", "Super-Heavy Battleship II", "Cavity Magnetron", "Polyalphabetical Ciphers"), every
**description**, every **picture** (bolt-action rifles, biplanes, battleships), the 3D **models**, the
**doctrines'** names, and a few **mechanics** that only make sense in 1936. Examples are propeller fighters giving
way to jets in the late 1940s, and battleships as the main capital ship.

## What I'd aim for

1. **Read as 2036 wherever a player looks**: names, descriptions, pictures.
2. **Keep what works**: the game's equipment and designer mechanics, its balance numbers and its AI research
   behaviour. Changing those means weeks of balancing, and the AI breaks quietly.
3. **Add the few things a modern war can't do without**: drones, electronic warfare, missiles and air defence,
   satellites and cyber.
4. **Stay inside the pipeline**: generated from tables in the repository and checked by `check_mod.py`, like the rest
   of the mod.

## Three ways to get there

| | what | effort | risk |
|---|---|---|---|
| A. Rename | new names, descriptions and pictures on the game's tree; mechanics untouched | small | it still plays like WW2 in places (battleships, the jet jump) |
| B. Rebuild | a new tree from scratch: new equipment, units, doctrines | very large | balance and AI; months |
| **C. Rename, then add** (recommended) | A first, then a short list of modern additions, each tested alone | medium, in steps | low per step |

C ships something visible quickly (step 1 alone changes how the whole game reads) and keeps every step reversible.

## The calendar

The game runs 2036 to 2049, 13 years like the base game's 1936 to 1949. The base game's tree has three layers, and
they map naturally:

| the game's years | becomes | meaning |
|---|---|---|
| 1918-1935 | **2018-2035, "Legacy"** | what nations own at the start, by how developed they are |
| 1936-1944 | **2036-2044, "Current"** | the main research of a game |
| 1945-1950 | **2045-2050, "Next generation"** | late, expensive, ahead of the time penalty until then |

Starting technology would follow **development tiers** the author assigns (the base game does this per country in
its history files):

- **Tier 1, the great powers** (Rouental? Krionik? Sarkis?): all Legacy techs, some 2036 ones.
- **Tier 2, regional powers**: most Legacy techs.
- **Tier 3, developing states**: basic infantry, trucks, older aircraft.
- **Tier 4, feudal and levy states**: Rouental's vassal levies, the Khanates, the small principalities. Basic
  infantry only, which fits Rouental's *Feudal Army* idea of a modern royal host beside medieval-style levies.

## Branch by branch: what each thing becomes

Names are suggestions in a plain modern style; the author's own names win.

**Infantry**

| the game's | 2036 |
|---|---|
| Infantry Weapons / Improved Infantry Equipment I-III | Service Rifles (Legacy) / Assault Rifles 2036 / Smart Rifles 2040 / Integrated Soldier System 2044 |
| Infantry Anti-Tank I-II | Anti-Tank Guided Missiles I-II |
| Paratroopers, Marines, Mountain Infantry, Rangers | Airborne, Marines, Mountain Troops, Special Forces (kept, renamed where needed) |
| Night vision, support weapons | Thermal optics, crew-served weapons |
| Truck, Military Motorcycle | Protected Truck (MRAP), Light Utility Vehicle |
| Mechanized | Infantry Fighting Vehicle |
| Armored Car | Wheeled Reconnaissance Vehicle |
| Towed Anti-Tank / Anti-Aircraft | ATGM Team / Short-Range Air Defence (MANPADS) |

**Support companies**: Engineers become Combat Engineers. **Recon becomes Drone Reconnaissance**. Military Police,
the Field Hospital and the Logistics and Maintenance companies keep their roles. **The Signal company becomes
Electronic Warfare** (see below). New: **Air Defence company**, using the game's SAM equipment.

**Armour** (the tank designer): Light Tank becomes Light / Airmobile Tank, Medium Tank becomes **Main Battle Tank**,
Heavy Tank becomes Heavy MBT, Modern Tank becomes **Next-Generation MBT**, and the Amphibious Tank stays. The
Super-Heavy Tank and Land Cruiser (special projects) become one-off "Heavy Assault Vehicle" projects, or go. The
designer's modules are renamed: e.g. riveted armour becomes composite armour, and radios become battle networks.

**Artillery**: Towed Artillery becomes Towed Howitzer. Rocket Artillery and Motorized Rocket become Multiple Rocket
Launcher and Wheeled Rocket Launcher. Self-propelled guns (tank designer) become self-propelled howitzers.
Super-Heavy and railway artillery become **Long-Range Fires** (a strategic rocket force), or stay as Valsora
flavour.

**Air** (the plane designer): every airframe is a jet from the start.

| the game's | 2036 |
|---|---|
| Fighter (small airframe) | Multirole Fighter: Gen 4.5 (Legacy), Gen 5 (2036), Gen 6 (2044) |
| CAS (small airframe) | Ground-Attack Aircraft / **Attack Drone** (an "unmanned" module) |
| Tactical Bomber (medium) | Strike Aircraft |
| Strategic Bomber (large) | Stealth Bomber |
| Naval Bomber | Maritime Strike / Patrol Aircraft |
| Scout plane, AEW modules | Airborne Early Warning, Recon Drone |
| Transport Plane | Strategic Airlifter |
| Helicopter (exists) | Attack and Transport Helicopters, from 2036 |
| the jet engine techs (1945-1950) | Next-generation engines (2045-2050) |

**Naval** (the ship designer):

| the game's | 2036 |
|---|---|
| Light hull (destroyer) | Frigate / Destroyer |
| Cruiser | Missile Cruiser |
| Heavy hull (battleship) | **Arsenal Ship**, or kept as battleships (a question below) |
| Carrier | Carrier, and later a Drone Carrier |
| Submarine | Diesel-Electric (SSK) / Nuclear Attack (SSN) |
| Torpedoes, guns | Anti-ship missiles, naval guns; torpedoes stay on submarines |
| Radar, sonar, fire control | Sensor suites, combat systems |
| Mines, minesweeping | Mines, unmanned mine-countermeasure vessels |
| Convoys | Container shipping |

**Electronics**: Radio becomes Battle Networks. Radar (Cavity Magnetron, Phased Array ...) becomes Integrated
Sensors. Computing Machines become Military AI and then Quantum Computing. The encryption and decryption techs
become **Cyber Defence and Cyber Offence**. Rocketry brings the game's guided and ballistic missiles forward to
2036. Nuclear research stays as it is, if Valsora has nuclear weapons.

**Industry**: Machine Tools becomes Automation and Robotics. Assembly Line / Flexible Line / Streamlined Line
become Additive Manufacturing and Smart Factories. Concentrated / Dispersed Industry become National Champions
and Distributed Manufacturing. Synthetic Oil becomes Synthetic Fuels and Biofuels. Construction and Excavation
become Modular Construction and Resource Extraction.

**Doctrines** (the 12 grand doctrines):

| the game's | 2036 |
|---|---|
| Mobile Warfare | Multi-Domain Operations |
| Superior Firepower | Precision Fires |
| Grand Battleplan | Defence in Depth |
| Mass Assault | People's War |
| Strategic Destruction | Strategic Strike |
| Battlefield Support | Close Air Integration |
| Operational Integrity | Integrated Air Defence |
| Fleet in Being | Sea Control |
| Trade Interdiction | Commerce War |
| Base Strike | Carrier Strike Groups |
| Special Forces (quantity / quality) | Special Operations (mass / elite) |

**Special projects**: see the next section.

## Special projects

The author (2026-10-15, later): "also take into account special projects. For example, mechs. Or maybe an orbital
kinetic bombardment weapon that acts sort of like a nuke."

**How the game's system works** (the Götterdämmerung DLC's; `common/special_projects/` in the game):
a country builds **special project facilities** in its states (Valsora's map already has a facility site in every land
province), assigns a **scientist** (a character with traits) to each, and runs a **project** there. A project has a
specialisation (nuclear, naval, air, land), a prototype time, a **complexity** (how many prototype iterations it
takes), a resource cost, breakthrough points, requirements, and an output: effects when it completes (equipment,
a design template, a technology, modifiers, anything a script can do). The game ships 49 projects; ours would be the
same machinery with 2036 subjects, so the scientist roster, facilities and their screens all keep working.

**The game's projects, in 2036** (renamed and re-pictured; mechanics kept):

| specialisation | the game's | 2036 |
|---|---|---|
| nuclear | reactor, commercial reactor, nuclear engines, atomic bomb, thermonuclear bomb, warheads | small modular reactors, naval reactors, tactical and strategic warheads, missile warheads |
| rockets | flying bomb, ballistic missiles (short, medium, long range), surface-to-air missile, rocket interceptor | cruise missiles, ballistic missiles, **hypersonic glide vehicles**, integrated air and missile defence |
| air | bouncing and earthquake bombs, intercontinental bomber, mothership aircraft, jet engines, supersonic jet, helicopter | bunker busters, **stealth bomber**, drone mothership, adaptive-cycle engines, sixth-generation fighter, tiltrotor |
| radar | radar | AESA radar, over-the-horizon radar |
| land | flamethrower tank, engineering vehicles, land cruiser, super-heavy howitzers and railway gun, stronghold network, kinetic sabot | thermobaric launcher, combat engineering vehicles, **mechs** (below), long-range fires, hardened bunker network, **railgun** |
| naval | the submarine line, nuclear torpedo, AIP engine, super-heavy and modern battleships, carriers, replenishment, proximity fuze, support ships, escort carrier | drone submarines, **arsenal ship** (or the dreadnought, question 2), supercarrier, drone carrier, fleet replenishment, smart munitions |

### Mechs

A **land** project line, built on the game's land cruiser project (`sp_land_land_cruiser`: an "insane" complexity
project whose output is a design template in the tank designer, or the equipment itself without No Step Back):

1. **Powered Exoskeletons** (medium complexity): infantry and special forces get soft attack, breakthrough and
   march speed (`equipment_bonus` / `unit_bonus` outputs, as the game's projects give).
2. **Light Walker** (complex): a recon and fire-support walker as a new support company: very good in hills,
   mountains, forests and cities, where tracks are slow.
3. **Assault Mech** (insane, like the land cruiser): a heavy walker as a battalion, from its own chassis in the tank
   designer (modules: armour, main gun or missile pods, an "AI co-pilot" module), slow to build, few per army.
4. **Mech Doctrine** (a subdoctrine in the land doctrine's tracks): bonuses for armies with mechs.

Each step needs the one before it; the Assault Mech also needs a high industry technology, so only industrial powers
field them. What it takes: a new equipment archetype and sub-unit (`common/units`), a chassis for the tank designer,
its counter and icon (the Deco UI's line style), names, AI templates; 3D models later, the counter meanwhile.

### Orbital bombardment

A short **space** line (a new project tag inside the nuclear or air specialisation, since the game has four fixed
specialisations), ending in a weapon that **acts like a nuke**:

1. **Orbital Launch Capability**: a spaceport (a state building) and launch decisions.
2. **Reconnaissance Satellites**: intelligence (the agency's upgrades), weather and targeting bonuses.
3. **Anti-Satellite Weapons**: lets a country blind another's satellites (a targeted decision with a cooldown).
4. **Orbital Kinetic Bombardment** ("rods from God"): tungsten rods dropped from orbit.

How the strike would work, as near to a nuke as the game allows:
- a **targeted decision** on an enemy state ("Kinetic Strike on [State]"), available at war once the project is done;
- it consumes one **rod** (a stockpile kept as a country variable, built by a production decision at a cost in
  steel, tungsten and civilian factories, or the game's own nuke stockpile, so the game's nuke counter shows it);
- it calls the game's scripted nuke, the `launch_nuke` effect, on the state's main province (to be checked against
  the game's effects documentation, not in our reference copy), so the damage is the game's: infrastructure, buildings,
  units, war support, the world's reaction and world tension;
- a long cooldown (e.g. 120 days), a world tension cost, and counters: the target's **Anti-Satellite Weapons** or
  missile defence give a chance the strike misses (scripted, with a superevent when the first strike lands);
- the kinetic strike leaves no fallout: an event may add "Kinetic devastation" in place of the game's nuclear
  modifiers, if the game's nuke modifiers can be lifted off afterwards.

### Others worth a project

- **Hypersonic missiles** (rockets): the ballistic missile line's last step; fast, hard to intercept.
- **Directed-energy air defence** (radar or rockets): anti-air and anti-drone bonuses for states and ships.
- **Autonomous swarms** (air): the attack drones' last step, a swarm "plane" that ignores pilots and losses.
- **Naval railgun** (naval): a ship module, from the kinetic sabot project.
- **Military AI** (radar or a new tag): planning speed, max planning, and the AI co-pilot module above.
- **Cyber warfare** (radar): the encryption and decryption techs' last steps, as intelligence agency upgrades.

The art: every project needs an icon and a blueprint picture in the game's facility screen; ours in the Deco UI's line
style. The scientist roster and facility screens would get the deco look with the rest of the panels.

## The few new things

Kept small on purpose. Each is one step that can ship and be tested alone.

1. **Drones.**
   - Recon drones replace the recon company. The game already has the slot, the modifiers and the AI.
   - **Loitering munitions** as a support company (soft and hard attack, cheap, fragile).
   - **Attack drones** as a plane design (small airframe with an unmanned module: cheap and short-ranged, no pilot
     losses).
2. **Electronic warfare.** The signal company becomes an EW company, plus a short tech line whose jamming lowers
   the enemy's air and drone effectiveness in a fight (combat modifiers the game already has).
3. **Air defence.** The game's SAM equipment, available from 2036, and a SHORAD support company to use it.
4. **Satellites and cyber.** As intelligence-agency upgrades and special projects, which the game already has
   systems for. No new map mechanics.

Each new unit needs its definition, icon, AI template and costs, checked like the rest.

## Pictures and models

- **Tech and equipment pictures** (about 300 in the game): the cleanest option is our own set in the Deco UI's gilt
  line style, silhouettes on lacquer, consistent with the interface. I can draw them programmatically, the way the
  Deco UI's icons are made. A modern-day mod's art is the other route, with permission (see the earlier note on
  etiquette).
- **3D models**: counters work meanwhile; models come when sourced.

## How I'd build it (each step ships on its own)

1. **Names and descriptions**: every technology, equipment item, module, unit and doctrine, from a mapping table in
   the repository (`source/tech_names.json` or similar) into `localisation/english/replace/`. `check_mod.py` would
   flag any WW2 name left in the player's view. About one session.
2. **Calendar and starting techs**: the Legacy / Current / Next labels, and the development tiers in the
   countries' histories. One session, once the author has picked tiers.
3. **Pictures** in the Deco line style. Two or three sessions.
4. **The new things** (drones, EW, air defence, satellites and cyber), one at a time, with a balance pass each.
   Two or three sessions.
5. **Special projects**: the game's 49 renamed (part of step 1), then mechs, then the orbital line, each with its
   icons, units and a balance pass. Two or three sessions.
6. **Doctrines**: names, descriptions, perhaps a few modifiers that fit a modern war. One session.
7. **Models**, when there are any.

## Questions for the author

1. **Tone**: a realistic 2036, or a Valsora-flavoured one (art deco retro-futurism, some anachronisms on purpose)?
2. **Battleships**: does Valsora still build them (kept, perhaps as "dreadnoughts"), or are they arsenal ships?
3. **Nuclear weapons**: does Valsora have them, and who has them at the start?
4. **Development tiers**: which nations are great powers, which developing, which feudal (Rouental's levies, the
   Khanates)? A list by name is enough.
5. **DLCs**: do you and your friends have No Step Back, Man the Guns and By Blood Alone? Without them the game shows
   the classic trees, so both would be renamed either way, but the new things would go into the designers.
6. **Drones**: a light touch (the three items above) or a branch of their own?
7. **Special projects**: mechs and orbital bombardment in the first round of new things, or after the renaming? Who
   may build them: anyone with the industry, or only great powers (tier 1)?
8. **The orbital strike**: as strong as a nuke (the game's devastation), or weaker and more frequent? Should a target
   be able to shoot it down (anti-satellite weapons, missile defence)?
