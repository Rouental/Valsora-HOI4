# A tech tree for 2036: proposal

The author's request (2026-10-15): "a written proposal for the 2036 tech tree", and later the same night: special
projects, "for example, mechs. Or maybe an orbital kinetic bombardment weapon that acts sort of like a nuke". Nothing here
is built yet; it is a plan to react to. **The author answered its eight questions on 2026-10-16** (next section); they are
still brainstorming ("not ready to make any actual changes") and will say more about the tree's shape later, so nothing is
built until they do. Later that day they named TNO and The Fire Rises as models and the Cold War as perhaps the earliest
era (the tree's depth and the game's length, after the calendar). Where an answer changed the plan, the section concerned says so.

## The author's answers (2026-10-16)

1. **Tone: a realistic 2036.** "The time is a relatively realistic 2036. So things that are just starting to be
   developed now should be coming into full swing then. Many nations are still at the modern level, but the
   superpowers are pushing ahead by a little." What is in development or first service in the mid-2020s is in full
   service by 2036: sixth-generation fighters with drone wingmen, laser air defence, hypersonic missiles, FPV drones
   and loitering munitions everywhere, uncrewed surface and underwater vessels, AI-assisted targeting. Most nations
   field today's equipment; the superpowers a step beyond it. No retro-futurism.
2. **The tree begins where the base game's ends.** "This goes into something I'll talk about later, but my current
   idea is that the beginning of Valsora's tech tree, the equivalent of the most basic equipment, is the end of the
   base game's tech tree. So battleships only capable of mounting guns would be the first step on the tree, then maybe
   battle cruisers like the Kirov, then on to arsenal ships." The tree runs from the late 1940s' kit to the 2040s, with
   today's level well along it (the calendar below); the heavy hull is gun battleship, then missile battlecruiser, then
   arsenal ship. More to come from the author.
3. **Nuclear weapons** "exist, but in small numbers, and only for the superpowers": the superpowers start with the
   nuclear technologies and a small stockpile each; nobody else has them at the start.
4. **The superpowers**: "Krionik, Kampf, and either Fraxhemark or Sarkis". Krionik KRI (Yastreovakia, 161 states),
   the Kampfian Empire KPF (Araseos, 95), and Fraxhemark FRX (Nonscio, Rouental's continent, 141) or Sarkis SRK
   (Orientalis, the largest nation on the map, 201). Counts from the 2026-10-15 build; most of them are states Claude
   cut from outlines, so they measure land.
5. **DLCs**: "I have the DLC, and I'd like to design the mod with the hope of everyone having it, but there should be
   a fallback for lack of dlc if possible." The new things go into the designers (tank, ship, plane) and the special
   projects; the classic trees are renamed too, and get the nearest equivalent where one can be made.
6. **Drones**: "My current idea is, to have them largely as a support company, and an aircraft for larger drones.
   Maybe somewhere down the recon tree there could be a branch for offensive fpv drones or something?" (Drones,
   under "The few new things".)
7. **Special projects**: "I'm not sure yet, I'm still in the brainstorming phase, not ready to make any actual
   changes. The plan would be for anyone to be able to make them, but it would be very difficult." No great-power
   lock: high complexity, costs and industry requirements instead.
8. **The orbital strike**: "my idea, assuming it's possible, is that they are weaker than a nuke, with no radiation,
   but cannot be prevented. The window to destroy them would be a raid before they are launched, once they're in orbit
   you just have to hope they miss." (Orbital bombardment, below.)

Still open: Fraxhemark or Sarkis; whether anyone else can build nuclear weapons during the game (through the nuclear
special projects, very difficult like the rest, would fit answer 7); which nations sit below the modern level (the
tiers, under the calendar); and the author's later thoughts on the tree's shape (answer 2).

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

*Reworked after answers 1 and 2 (2026-10-16). The first version mapped the base game's years a hundred years on
(1918-1935 to 2018-2035 "Legacy", and so on); the author's tree instead begins where the base game's ends.* *Later that day the
author thought of making the Cold War the earliest era instead (the post-war row below would go), with TNO and TFR as
models: see "The tree's depth and the game's length" after the tiers.*

The tree covers about a century of equipment, of which the game's thirteen years (2036 to 2049) are the last part.
Each line keeps the base game's number of steps; its first step is renamed as the post-war kit (the base game's last)
and each later step moves forward in time:

| era | its technologies' years | for example | who has it at the start |
|---|---|---|---|
| Post-war | about 1945-1960 | gun battleships, the first jets, battle rifles: Valsora's most basic kit | everyone |
| Cold War | about 1960-1990 | missile battlecruisers (the Kirov), main battle tanks, fourth-generation fighters | all but the feudal and levy states |
| Modern | about 1990-2030 | today's: Gen 4.5 and 5 fighters, FPV drones, guided missiles everywhere | most nations |
| 2036 | about 2030-2040 | sixth-generation fighters and their drone wingmen, lasers, hypersonics | the superpowers in part; everyone's main research |
| Next generation | about 2040-2050 | arsenal ships, mechs, orbital strikes | nobody: late, costly, and penalised as ahead of its time until its year |

The years are real ones, so the game's research penalty only bites on what lies beyond the date. `check_mod.py`, which
fails on any 19xx `start_year` today, would allow technologies' years before 2036 (the game's dates and labels stay
2036).

Starting technology follows **tiers** (the base game sets it per country in its history files):

- **Superpowers**: Krionik, the Kampfian Empire, and Fraxhemark or Sarkis. The Modern era and part of 2036, the
  nuclear technologies and a few warheads (`add_nuclear_bombs`).
- **Modern**: most nations (the default for every nation the author doesn't place lower).
- **Developing**: up to the Cold War.
- **Feudal and levy states**: the post-war kit. Rouental's vassal levies fit here, beside its modern royal host (the
  host's divisions take modern equipment from Rouental's own tier).

## The tree's depth and the game's length (2026-10-16, later)

The author: "I'd like to take inspiration from the fire rises and TNO. I might make the earliest era the cold war
actually. I'm not sure how many years I want the game to last, so I'm not sure how many layers of tech there should be.
The base game starts at the second layer and has two more major advances for the infantry weapon, for example. I can't
quite remember, but I think for majors TFR/TNO starts you even farther in with less distance to go. I'm not sure what
I'll end up doing." Still brainstorming: nothing is built.

**What the base game does** (read from the author's 1.19.3 files):

- The infantry line: Basic Infantry Equipment (1918), Infantry Equipment I (1936), an upgrade (1938), Infantry
  Equipment II (1939), an upgrade (1940), Infantry Equipment III (1942), an upgrade (1944). Majors start with the 1918
  and 1936 steps (Germany's history), minors with the 1918 one alone (Ethiopia's). So a major has two big steps and
  three small ones ahead, three years apart and one or two years apart; a minor one big step more.
- The whole tree: 506 dated technologies, 113 of them at 1936 (what a country starts with or can take at once), about
  330 between 1937 and 1945, and almost none later (a dozen to 1950). The game ends in 1949, so a major reaches the end
  of the lines it cares about about two thirds of the way through.
- Research: a technology costs 110 days (`BASE_TECH_COST`) times its cost (1.5 typically), so about 165 days in one
  slot; five slots over thirteen years is about 145 technologies at the base speed, under half of what the tree holds
  after 1936: choosing matters. Researching ahead of a technology's year costs extra for every year early
  (`BASE_YEAR_AHEAD_PENALTY_FACTOR` = 2), which is what holds a country to the calendar.

**The other mods** (researched 2026-10-16; the mods' wikis, Steam and Reddit couldn't be opened from here, so what
couldn't be read in a mod's own files is marked):

- **The Fire Rises** (starts 1 January 2020; its end date not confirmed). From a copy of its technology files on GitHub
  (`HugoRinderknecht/The_Fire_Rises`, June 2025; the copy's costs may have been edited, its years and structure are
  TFR's): the infantry tab's years are 2000, 2006, 2012, 2018, then 2021, 2024 ... 2036: **six years apart behind the
  start, three years apart ahead of it**. Small arms have six equipment tiers (2000, 2006, 2018, 2024, 2030, 2036) and
  stat upgrades between them, nine steps in all; the tree stops at 2036 (a few techs to 2044), sixteen years past the
  start. Which tiers its majors start with is not confirmed. Its startup gives AI countries it doesn't care about no
  research slots (for speed).
- **TNO** (starts 1962; the Workshop page promises "ten years or more" of content for the main factions; end date and
  small-arms tiers not confirmed: its files aren't public). From its bug tracker: technologies run to at least 1990,
  equipment is named by year ("1950 Basic Motorized Equipment"), and **higher technologies need a higher level of
  social development**: "a 1965 tech requires highest industry social development level", which holds almost everyone
  but the three Cold War superpowers back (the developers kept it so, issue #5097, 2025).
- **Millennium Dawn** (the long-running modern-day mod; confirmed from its own files, v2.0.2): one start, 2000, the game
  ending in 2100. Its tree runs 1965 to 2080 in five-year steps, about 1,400 techs; small arms are twelve tiers ten years
  apart ("Small Arms 1965" to "Small Arms 2075"), four of them before the start. The USA starts with five (to 2005, one
  past the start), Russia, Germany and China with four, Indonesia and Nigeria with two, Mali and Chad with the first
  alone. Research is slower and the calendar looser than the base game's (`BASE_TECH_COST` 250 against 110, the
  ahead-of-time penalty 1.0 against 2, tech sharing at most 10 % against 50 %), and research slots (none at the start)
  come from a country's economy (GDP and GDP per head, with factories), its speed from education and literacy.

So the author's memory is about right for TFR: its majors start in the middle of their lines (four of small arms'
nine steps lie before 2020) and the steps ahead come quicker than the ones behind. TNO holds the gap open by
development rather than by starting technologies alone. Millennium Dawn is the other way to a long game: a very long,
dated tree, slow research, and slots earned by the economy.

**What it means for Valsora:**

1. **Design the tree in generations; date it last.** How many generations a line has is a choice of content (which
   eras of equipment the game shows); how far a game gets through them is set by the years they carry, their costs and
   the ahead-of-time penalty, one table. So the game's length can wait: choosing it later re-dates the tree without
   redrawing it (the build already writes every date by rule, `vanilla_parts.py`).
2. **A rule of thumb from the base game**: a big step about every three years, a smaller one between, and the
   frontier running out about two thirds of the way through. For the superpowers that is about three big steps ahead
   in a 13-year game (2036 to 2049, today's end date), four or five in 20 years, six in 25. Or the last generation is
   left open: very costly, so a long game never runs dry.
3. **The Cold War as the floor, coarse behind and fine ahead** (TFR's pattern). With the post-war era dropped, an
   infantry line could run: Cold War I (1965, battle and assault rifles), Cold War II (1985), Modern I (2005),
   Modern II (2025), the 2036 tier (where the superpowers start), then a big step every three years with upgrades
   between (2039, 2042, 2045 ...). In a 13-year game the starts might be:

   | tier | starts with | big steps to a 2045 frontier |
   |---|---|---|
   | superpowers | 2036 | 3 |
   | modern (most nations) | Modern II (2025) | 4 |
   | developing | Cold War II (1985) | 6 |
   | feudal and levy states | Cold War I (1965) | 7 |

   Older steps cost no penalty (their years are past), so a nation behind can close the gap line by line; overall it
   stays behind, with more to research and, as a rule, fewer slots and less speed. TNO's way of keeping the tiers apart
   would fit too: the newest steps open only to nations developed enough to build them (for Valsora, a scripted
   condition on industry or a national spirit per tier), so a feudal state can't research its way to sixth-generation
   fighters however long it tries.
4. **Questions this leaves for the author:** how long a game should last (13 years like the base game and, so far,
   Valsora; TFR's tree reaches 16 years past its start; Millennium Dawn's a century, by its tree's length and slow
   research);
   how many generations each line shows (the base game's lines have four big steps); whether the nations behind should
   catch up faster (the base game's only help is technology sharing inside a sharing group, at most 50 % off a
   technology a partner has, `MAX_TECH_SHARING_BONUS`); and whether the tiers should be held apart by development,
   as TNO's are.

## Branch by branch: what each thing becomes

Names are suggestions in a plain modern style; the author's own names win.

**Infantry**

| the game's | 2036 |
|---|---|
| Infantry Weapons / Improved Infantry Equipment I-III | Battle Rifles (post-war) / Assault Rifles (Cold War) / Modular Rifles (modern) / Smart Rifles and the Integrated Soldier System (2036) |
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
| Fighter (small airframe) | Jet Fighter (post-war) to Gen 4 (Cold War), Gen 4.5 and 5 (modern), Gen 6 (2036) |
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
| Heavy hull (battleship) | Gun Battleship (the first step), then Missile Battlecruiser (like the Kirov), then **Arsenal Ship** (answer 2) |
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

How the strike would work (reworked after answer 8, 2026-10-16: "weaker than a nuke, with no radiation, but cannot be
prevented. The window to destroy them would be a raid before they are launched, once they're in orbit you just have
to hope they miss"):
- **Readied, then launched.** A rod is built (a production decision at a cost in steel, tungsten and civilian
  factories) and readied at a **launch site**: a special project facility, or a building of ours carrying the game's
  `facility` tag. Readying takes some days: that is the window.
- **Only a raid stops it.** The game's own air raid **Facility Strike** (`facility_strike` in
  `common/raids/air_raids.txt`, at war, against buildings tagged `facility`) can hit the launch site; a successful
  raid destroys the rods readied there. A paratrooper raid of our own could do the same.
- **Once launched, nothing stops it**: no interception, no anti-satellite counter. The strike is a **targeted
  decision** on an enemy state ("Kinetic Strike on [State]"), with a chance to miss (the rod lands in a neighbouring
  province, or somewhere of no use), so the target can only hope.
- **Weaker than a nuke, no fallout.** Not the game's nuke (`launch_nuke` brings its radiation and nuclear modifiers):
  a scripted strike built from the game's own effects, the one its raids use on buildings (`damage_building`) and
  those for units in a province (strength and organisation), plus the target state's infrastructure and a war support
  loss. The exact effects to be checked against the game's documentation.
- A cooldown and a world tension cost; a superevent when the first strike lands.

The line's other steps stay: launch capability, then reconnaissance satellites (intelligence and targeting). The
anti-satellite step would blind those satellites, not stop strikes.

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

1. **Drones** (the author's shape, answer 6):
   - **A drone company** (support): recon drones in place of the recon company. The game already has the slot, the
     modifiers and the AI.
   - **Offensive FPV drones, down the recon line**: a branch of its technologies that arms the drone company (soft and
     hard attack, cheap, fragile), or a second support company of FPV strike teams if one company can't carry both.
   - **Larger drones as aircraft**: a plane design with an unmanned module (long-endurance drones like the Reaper for
     ground attack and reconnaissance; for the superpowers, drone wingmen beside their sixth-generation fighters).
     Without By Blood Alone, the classic tree's close air support line, renamed.
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
2. **Calendar and starting techs**: the eras' years and labels, and the tiers in the countries' histories (with the
   superpowers' warheads). One session, once the author has placed nations in tiers.
3. **Pictures** in the Deco line style. Two or three sessions.
4. **The new things** (drones, EW, air defence, satellites and cyber), one at a time, with a balance pass each.
   Two or three sessions.
5. **Special projects**: the game's 49 renamed (part of step 1), then mechs, then the orbital line, each with its
   icons, units and a balance pass. Two or three sessions.
6. **Doctrines**: names, descriptions, perhaps a few modifiers that fit a modern war. One session.
7. **Models**, when there are any.

## Questions for the author (answered 2026-10-16)

The first version's eight questions (the tone, battleships, nuclear weapons, the tiers, DLCs, drones, special projects
and the orbital strike) are answered above, under "The author's answers"; what is still open is listed at the end of
that section.
