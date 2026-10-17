# Valsora's 2036 tech tree: the full mockup

The author's request (2026-10-17): "a full mockup of the tech tree", **not to be added to the mod yet**. This folder is
that mockup: the whole tree as data, an interactive page that shows it in the Valsora Deco UI's style, and a picture
of every research screen as it would look in the game. Nothing here is read by the build; `scripts/`, `source/` and
`deco_ui/` are untouched.

The page is also a **private claude.ai Artifact**, https://claude.ai/artifact/4h5nttfGvLadmHfxjHiHi8 (2026-10-17): only the
author can open it until they share it. After a change, republish `index.html` to the same artifact.

It follows `docs/TECH_TREE_2036.md` and the author's answers of 2026-10-16: a realistic 2036, the tree beginning
where the base game's ends with the Cold War as its floor (the doc's latest recommendation), four great powers as the
superpowers, nuclear weapons for them alone at the start, drones as a support company, an aircraft and an FPV branch,
special projects open to anyone but very hard, mechs and the orbital strike, every DLC's designers with a fallback
without them, and "rename, then add": every technology is either one of the base game's, renamed, or marked new.

## What is here

| file | what it is |
|---|---|
| `index.html` | the interactive mockup (one self-contained page, the data inside it): folder tabs, a switch for what a Superpower, Modern, Developing or Feudal nation has at the start, the DLC switch, search, every technology's file on a click, the overview with the counts, and an in-game view of any folder |
| `tree.json` | the tree as data: every folder and technology with its 2036 name, era and year, prerequisites and exclusions, the base-game technology it replaces (with that technology's name, year, path and what it unlocks, read from the game's files) or "new", what it unlocks in game terms, its description, who starts with it, and DLC notes; the special projects and the doctrines |
| `screens/` | `01_infantry.png` to `17_air_classic.png`: each folder as a 1920 × 1080 in-game screen (a Modern nation on 1 January 2036); `00_overview.png`, the overview page; `00_contact_sheet.png`, every screen on one sheet |
| `src/` | how it is made: `data_*.py` (the tree, written by hand), `make_tree.py` (fills in the game's facts, checks, writes `tree.json`), `page.html` and `page.js` with `make_page.py` (writes `index.html`), `make_screens.py` (the pictures and the page checks) |

To rebuild, from the repository's root: `python3 docs/tech_tree_mockup/src/make_tree.py`, then `make_page.py`, then
`make_screens.py` (headless Chromium at `/opt/pw-browsers/chromium`; the fonts come from `deco_ui/source_fonts/`).
`make_tree.py` reads the author's copy of the game (`/home/user/hoi4-files`, or `HOI4_FILES`); without it, it keeps
the game's facts already in `tree.json`. It stops on any unknown id, a prerequisite that comes after its technology,
two technologies in one place, or a technology of the game's research folders left out.

## The counts

| | technologies | new | renamed from the game |
|---|---|---|---|
| the nine research folders (with the designer DLCs) | 408 | 73 | 335 |
| special projects | 61 | 12 | 49 (all of the game's) |
| the three folders without the designer DLCs | 90 | 6 | 84 |
| **all** | **559** | **91** | **468** |
| doctrines: 4 folders, 12 grand doctrines, 14 tracks | 99 subdoctrines | 8 | 91 |

Every technology in the game's twelve research folders (411, with the DLC and the classic forms) has its 2036
counterpart, and so have its 49 special projects and its 95 subdoctrines (the four `_no_lar` copies folded into their
originals).

By folder (designer forms): Infantry 53, Support 53, Artillery 31, Armour 30, Naval 51, Naval Systems 46, Air 56,
Electronics 39, Industry 49. By era, across those nine and the projects: Cold War 101, Modern 97, 2036 126, Next
generation 145. In the nine folders 143 technologies unlock equipment or units (the large cards) and 265 are upgrades.

## The calendar: the base game's 1936 is Valsora's 2036

The tree covers the Cold War to the 2040s, in four eras (the coloured bands on every screen):

| era | years | steps | who starts there |
|---|---|---|---|
| Cold War | 1960-1989 | Cold War I (1965), Cold War II (1985) | feudal and levy states have Cold War I, developing nations Cold War II |
| Modern | 1990-2030 | Modern I (2005), Modern II (2025) | most nations (the default tier) have everything up to Modern II |
| 2036 | 2031-2039 | the game's start and first years | the superpowers start with the 2036 steps |
| Next generation | 2040-2050 | big steps in 2039, 2042, 2045, upgrades between | nobody: researched in play |

**The starting era is the Cold War** (the doc's "Cold War as the floor, coarse behind and fine ahead", the TFR
pattern the author named). The first step of the heavy hull is the author's gun battleship (1965), then the missile
battlecruiser like the Kirov (1985), then the arsenal ship (2040). On every screen the dashed gilt line marks
1 January 2036 and the year labels name the steps (Cold War I, Cold War II, Modern I, Modern II, Game start); with the
start switch, what a nation has researched on day one is gold, what it can research next has a green frame.

**How the game's ids line up.** Every line keeps the base game's steps in their order, so its mechanics, balance and
AI weights carry over:

- the game's steps dated 1936 or later keep their place a hundred years on (1936 is 2036, 1939 is 2039, 1942 is 2042),
  so the thirteen years of play keep the base game's research rhythm, a big step every three years;
- the game's steps dated before 1936 (what its minor nations start with) are Modern II, today's kit, so the modern
  tier starts where the game's minors do and the superpowers where its majors do;
- new steps added below them are the older kit: Cold War I, Cold War II and Modern I on the main lines (small arms,
  main battle tanks, fighters, strike aircraft, bombers, every hull), a single Cold War floor on the others;
- a few new steps at the end keep the frontier open (a fifth infantry kit in 2045, the 2045 next-generation tank is
  the game's own modern tank).

Where the game's date would put something far too late for 2036, the line is dated by history instead and says so
in its note: trucks, towed guns, railways and support equipment are 1965 (every nation has them), infantry fighting
vehicles 1985, night vision 1985, anti-tank missiles 2005, motorised infantry 2005, the support companies' first
steps 1985 and 2025, main battle tanks from 1965. The game's research penalty only bites on what lies ahead of the
date, so the older steps cost a nation behind nothing extra.

**The tiers** (technologies researched on 1 January 2036 in the nine folders, of 408):

| tier | has | of the projects, done |
|---|---|---|
| Superpowers: Krionik, the Kampfian Empire, Sarkis, Fraxhemark | 214 | 16 (the nuclear weapons, naval reactors, nuclear submarines, the supercarrier, the missiles, orbital launch and reconnaissance satellites) |
| Modern (the default) | 175 | 2 (short-range ballistic missiles and the surface-to-air missiles the air defence company needs) |
| Developing | 89 | none |
| Feudal and levy states (Rouental's vassal levies) | 38 | none |

## Folder by folder

The pages show every technology; these are the lines that carry the tree.

**Infantry** (years across, like the game's): small arms run Battle Rifles (1965, new) · Assault Rifles (1985, new) ·
Modular Rifles (2005, new) · Digital Soldier Kit (2025, `infantry_weapons`) · Integrated Soldier System (2036,
`infantry_weapons1`) · Next-Generation Squad Weapon (2039, `improved_infantry_weapons`) · Augmented Soldier (2042,
`advanced_infantry_weapons`) · Next-Generation Infantry System (2045, new), with the game's three upgrades between
(2038, 2040, 2044). Then anti-tank missiles, thermal optics, trucks and protected mobility, IFVs (with active
protection), armoured cars, amphibious vehicles, and the specialists (marines, mountain troops, airborne, rangers,
and the special forces line that the game shows without Arms Against Tyranny).

**Support**: the seven companies as the game has them, renamed (the recon company is drone reconnaissance, the
signal company becomes signals and electronic warfare), each with its special-project company (armoured engineers,
air cavalry, air ambulance, tiltrotor lift ...). New: the **FPV strike drones** branch down the recon line (FPV
Strike Drones 2025, Fibre-Optic Guidance 2036, Loitering Munitions 2039, Autonomous Homing 2042, Strike Swarms 2045),
an **electronic warfare** line (drone jamming, satellite navigation spoofing, tactical cyber, counter-drone attack)
and the **Air Defence Company** with counter-drone guns, lasers and microwave weapons. Railways at the bottom.

**Artillery** (years down): air defence (guns 1965 to lasers 2039), howitzers (towed 1965 to robotic 2039 and ramjet
shells), rocket artillery (1965 to long-range fires and hypersonic fires), anti-armour missile teams.

**Armour** (the tank designer): Cold War Armour (1965, `gwtank_chassis`, the designer's first chassis and modules),
Third-Generation MBT (1985, new), Upgraded Third-Generation MBT (2005, new), Modernised MBT (2025,
`basic_medium_tank_chassis`), Fourth-Generation MBT (2036), Unmanned-Turret MBT (2042), Next-Generation MBT (2045,
the game's modern tank); light tanks to a robotic combat vehicle; heavy assault tanks and a siege tank; power packs
to all-electric drive; composite armour to active protection and adaptive armour; and the five technologies that
follow the **Assault Mech** project (the game's land cruiser follow-ups: power plant, leg actuators, crew training,
AI co-pilot, hypervelocity gun).

**Naval** (the ship designer's hulls): escorts (destroyer escort 1965, missile frigate 1985, then the game's light
hull from the multi-mission frigate to the autonomous escort), cruisers, **capital ships (Gun Battleship 1965 ·
Missile Battlecruiser 1985 · Large Surface Combatant 2025 · Guided-Missile Battleship 2036 · Arsenal Ship 2040 ·
Arsenal Ship II 2043)**, carriers (angled deck, supercarrier, through-deck conversions, electromagnetic catapults,
the drone carrier 2039), submarines (diesel-electric to lithium-battery and beyond; nuclear boats are special
projects), sonar and anti-submarine weapons, and a new line of **uncrewed surface vessels**.

**Naval Systems**: guns, air-defence missiles (the game's dual-purpose batteries), **anti-ship missiles** (the game's
torpedo modules on surface ships become missile launchers; submarines keep their torpedoes), new land-attack missiles
and shipboard lasers, damage control, combat systems, sealift, replenishment and mines.

**Air** (the plane designer, every airframe a jet): fighters run Third-Generation (1965, new) · Fourth-Generation
(1985, new) · Generation 4.5 (2005, new) · Fifth-Generation (2025, `iw_small_airframe`) · Sixth-Generation (2036) ·
Block II (2040) · Optionally Crewed (2044) · Seventh-Generation (2045, behind the Adaptive-Cycle Engine project).
The game's small airframe's other versions are the ground-attack, maritime strike, carrier and **one-way attack
drone** versions (the game's suicide airframe). New: **the drone airframe line** (armed long-endurance drones 2005 to
the drone wingman, Collaborative Combat Aircraft, 2036, and autonomous air combat 2044). Strike aircraft, bombers
(jet bomber, supersonic bomber, strategic bomber, stealth bomber 2036, global strike bomber), airlifters, bombs to
glide bombs, air-to-air missiles, anti-ship missiles, engines and the drone mothership line.

**Electronics**: networks (radio to battle networks and laser links), radar (search radar, pulse-Doppler and AESA as
new ordinary technologies; the game's project-gated radars become the advanced ones), computing to **Military AI**
(2036) and quantum computing, combat systems, cyber defence and offence (the game's encryption and decryption, shown
without La Resistance), fortifications, missiles, hypersonic propulsion and nuclear research.

**Industry**: four new legacy production steps (mass production 1965 to lean production 2025, the difference between
the tiers), then the game's own industry from 2036 (smart factories, collaborative robots, digital twins,
reconfigurable lines or additive mass production), National Champions or Distributed Manufacturing (exclusive,
chosen in play), construction, resource extraction, fuel and synthetics.

**Special projects** (61, four specialisations as in the game; the nuclear one renamed "Strategic: nuclear and
space"): the game's 49 renamed, most a step harder (the author: anyone can make them, but it should be very
difficult; the game's own complexity is kept in `tree.json` beside the proposed one). New: the **mech line**
(Powered Exoskeletons, Light Walker, then the Assault Mech built on the game's land cruiser project, which also needs
an industry technology so only industrial powers field them), the **orbital line** (Orbital Launch Capability,
Reconnaissance Satellites, Anti-Satellite Weapons, **Orbital Kinetic Bombardment**: weaker than a nuke, no fallout,
unstoppable once launched, the only window a Facility Strike raid on the launch site), and the hypersonic glide
vehicle, an autonomous swarm, directed-energy air defence, a naval railgun, a military AI co-pilot and a cyber
warfare command.

**Doctrines**: the 1.19 system kept, renamed (Mobile Warfare is Multi-Domain Operations, Superior Firepower Precision
Fires, Grand Battleplan Defence in Depth, Mass Assault People's War, and so on), with eight new subdoctrines: Drone
Saturation, Mech Warfare and Spectrum Warfare (land), Arsenal Fleet and Drone Carrier Operations (naval), Loyal
Wingman Teams and Drone Strike Campaigns (air), Drone-Enabled Raids (special forces). The five mastery rewards of each
subdoctrine are kept and would be renamed in a later step.

**Without the DLCs**: with the DLC switch on "Without", the page shows the game's classic armour, naval and air
folders in their 2036 form: the same subjects and years as fixed equipment (the close air support line becomes the
attack drones, as the doc suggested), with six new legacy steps (two Cold War tanks, the gun battleship and missile
battlecruiser classes, two Cold War fighters). Naval Systems has no classic form (the classic ships carry their
weapons). Without Götterdämmerung there are no special projects; their outputs would be ordinary technologies where
they can be. Technologies the game shows only with or without a DLC (rangers, armoured cars, the special forces
line, encryption) say so in their files.

## What it would take in the game

**Renaming** (468 entries): names, descriptions and the year labels, from a table like `tree.json` into
`localisation/english/replace/`; the dates by the rule above in `vanilla_parts.py`. `check_mod.py` fails today on any
19xx `start_year`; it would have to allow technology years before 2036 (the Cold War steps) while the game's dates
stay 2036's, as the doc foresaw.

**Mechanics that change on renamed technologies**: the infantry battalion moves to Battle Rifles; a few prerequisites
are re-pointed where a line is re-dated (anti-tank missiles, night vision, the specialists); the basic ship and plane
radars move from the project-gated technologies to new ordinary ones; the helicopter stays behind its project, now
the Tiltrotor project (a question below).

**New equipment** (the new steps, mostly tiers of the game's own archetypes): infantry kits `infantry_equipment_cw1`,
`_cw2`, `_m1` and `_4`; FPV drones; tank chassis `medium_tank_chassis_cw2` and `_m1` with their variants; hulls
`ship_hull_light_cw1`, `_cw2`, `ship_hull_cruiser_cw2`, `ship_hull_heavy_cw1` (guns only), `_cw2`,
`ship_hull_carrier_cw1`, `_cw2`, `ship_hull_submarine_cw1`, `_cw2`; airframes `small_plane_airframe_cw1`, `_cw2`,
`_m1`, `medium_plane_airframe_cw1`, `_cw2`, `large_plane_airframe_cw1`, `_cw2`; the light walker and the hypersonic
missile; for the classic folders, the fixed versions of the same.

**New units, hulls and airframes** (new archetypes): the FPV Strike Team and Air Defence Company (support
companies), the Light Walker (support company) and the Assault Mech (battalion and tank designer chassis); the
uncrewed surface vessel hull (three tiers, a new ship role); the drone airframe (four tiers) and the swarm airframe.

**New modules**: land-attack missile cells, laser point defence, high-energy laser and the naval railgun on ships;
the mech's modules (armour, main gun, missile pods, AI co-pilot); an IFV active protection module with No Step Back.

**New upgrades without new equipment**: combat modifiers the game already has where it has one (attack, defence,
air superiority and air support penalties, night penalties, planning, fuel), otherwise the nearest one; the
electronic warfare line's "enemy drones less effective" would be an enemy air support and recon penalty in combat.

**New systems**: a spaceport building and launch and strike decisions for the orbital line (the strike from the
game's own raid and building-damage effects, not `launch_nuke`), satellite and cyber upgrades for the intelligence
agency, the tier start techs in every country's history (and a few warheads for the four superpowers).

Pictures: every technology needs an icon and the projects a blueprint; the page draws simple line icons in the Deco
UI's style as a stand-in. 3D models later, counters meanwhile.

## What would be built first, if approved

1. **Names and descriptions** for every technology, equipment item, unit, module, project and doctrine, from
   `tree.json` into `localisation/english/replace/`, with a `check_mod.py` test that no 1940s name is left in view.
   One session; the game plays as before, but reads as 2036.
2. **The calendar and the tiers**: the dates by the rule above, `check_mod.py` allowing the Cold War years, and the
   starting technologies per tier in the countries' histories once the author has placed nations in tiers.
3. **The legacy steps** (Cold War and Modern I equipment for the developing and feudal tiers), cheap and quick.
4. **The new things one by one**, each with a balance pass: the FPV branch and the air defence company, the drone
   airframes, the uncrewed vessels, ship lasers and land-attack missiles, the electronic warfare line.
5. **Special projects**: the 49 renamed (part of step 1), then the mech line, then the orbital line.
6. **Doctrines**: the new subdoctrines and the rewards' names.
7. **Pictures** in the Deco UI's line style.

## Questions for the author

1. **The anchor.** The base game's 1936 steps are Valsora's 2036 ones, so the twelve years of play keep the game's
   own research and balance, and the Cold War and Modern I steps are new. Does that work for you, or should the game's
   first step be the Cold War one (fewer new steps, but less left to research during the game)?
2. **The floor.** The tree starts at the Cold War (the gun battleship, battle rifles, third-generation jets). Is that
   the earliest era you want, or should a post-war step come back?
3. **The game's length.** The main lines have three big steps after 2036 (2039, 2042, 2045) and a few open ones; for a
   longer game they would get more. How long should a game last?
4. **The superpowers.** All four great powers (Krionik, Kampf, Sarkis, Fraxhemark) start as superpowers, with nuclear
   weapons. Is that right now that there are four?
5. **The tiers.** Which nations are developing, and which feudal or levy states, beside Rouental's levies? And should
   the newest steps be held back by development, as in TNO, so a feudal state can't research its way to
   sixth-generation fighters?
6. **Drones.** The FPV drones are a company of their own (FPV Strike Team) beside the drone reconnaissance company.
   Would you rather the FPV branch arm the reconnaissance company itself?
7. **Helicopters.** The game puts helicopters behind a special project; here it is the Tiltrotor project. Should plain
   helicopters be an ordinary technology instead (they are old kit in 2036)?
8. **Special projects.** Most projects are a step harder than the game's. Too hard, or not hard enough?
9. **Names.** Every name here is a suggestion in a plain modern style. Do you want them plain, or with Valsoran names
   (makers, programmes, places)?
