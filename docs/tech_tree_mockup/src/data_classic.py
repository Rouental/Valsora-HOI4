"""The fallback folders, for players without the designers' DLCs: the game's classic armour, naval and air trees.

Each technology has the same subject, year and place in time as its designer counterpart (`same`), so a player
without No Step Back, Man the Guns or By Blood Alone sees the same tree with fixed equipment instead of designs.
"""
from common import folder, T, TECHS

SAME = {}   # classic id -> designer-tree id


def C(f, vid, same, year, lane, name=None, desc=None, req=None, new=False, unl=(), dlc=None, icon=None):
    tid = vid if not new else vid
    t = T(f, tid if not tid.startswith("sp_") and not tid in SKIP_IDS else "c_" + tid, name or "", year, lane,
          desc or "", req=req, unl=unl, dlc=dlc, icon=icon, replaces=None if new else vid)
    if new:
        t["replaces"] = "new"
    t["same"] = same
    SAME[t["id"]] = same
    return t


# ids that the designer folders use too (the special project follow-ups are in both forms of a folder)
SKIP_IDS = {"reinforced_wings_mothership", "miniature_fighters", "aerial_hangars"}

# ---- armour ----------------------------------------------------------------------------------------------------
F = folder("armour_classic", "Armour, classic", "armour_folder", "down", "tank", "army",
           "Without No Step Back: the same tanks as fixed equipment, no designer.", dlc="Without No Step Back",
           variant_of="armour")
F.section("Light", 0)
C(F, "basic_light_tank", "basic_light_tank_chassis", 1985, 0, req=["gwtank"])
C(F, "improved_light_tank", "improved_light_tank_chassis", 2025, 0)
C(F, "advanced_light_tank", "advanced_light_tank_chassis", 2041, 0)
C(F, "amphibious_tank", "amphibious_tank_chassis", 2025, 1, req=["improved_light_tank"], dlc="Man the Guns")
C(F, "amphibious_tank_2", "amphibious_drive", 2042, 1, name="Amphibious Light Tank II",
  desc="A faster amphibious tank, armoured against drones.", dlc="Man the Guns")
F.section("Main battle tanks", 2)
C(F, "gwtank", "gwtank_chassis", 1965, 2, req=[], name="Cold War Tanks",
  desc="Second-generation main battle tanks, the kit every army has: fixed equipment in place of the designer's "
       "chassis.")
C(F, "val_c_mbt_3gen", "val_mbt_3gen", 1985, 2, new=True,
  unl=["new equipment: medium_tank_equipment_cw2, Third-Generation MBT (fixed design)"])
C(F, "val_c_mbt_3plus", "val_mbt_3plus", 2005, 2, new=True,
  unl=["new equipment: medium_tank_equipment_m1 (fixed design)"])
C(F, "basic_medium_tank", "basic_medium_tank_chassis", 2025, 2)
C(F, "improved_medium_tank", "improved_medium_tank_chassis", 2036, 2)
C(F, "advanced_medium_tank", "advanced_medium_tank_chassis", 2042, 2)
C(F, "main_battle_tank", "main_battle_tank_chassis", 2045, 2, req=["advanced_medium_tank", "advanced_heavy_tank"])
F.section("Heavy", 3)
C(F, "basic_heavy_tank", "basic_heavy_tank_chassis", 2025, 3, req=["gwtank"])
C(F, "improved_heavy_tank", "improved_heavy_tank_chassis", 2040, 3)
C(F, "advanced_heavy_tank", "advanced_heavy_tank_chassis", 2043, 3)
C(F, "super_heavy_tank", "super_heavy_tank_chassis", 2041, 4, req=["improved_heavy_tank"])
F.section("Assault Mech", 5)
C(F, "sp_armored_lc_naval_engine_conversion_tech", "sp_armored_lc_naval_engine_conversion_tech", 2043, 5,
  req=["super_heavy_tank"])
C(F, "sp_armored_lc_transmission_improvements_tech", "sp_armored_lc_transmission_improvements_tech", 2043, 6,
  req=["super_heavy_tank"])
C(F, "sp_armored_lc_specialized_field_manuals_tech", "sp_armored_lc_specialized_field_manuals_tech", 2043, 7,
  req=["super_heavy_tank"])
C(F, "sp_armored_lc_weapon_fire_control_tech", "sp_armored_lc_weapon_fire_control_tech", 2045, 6,
  req=["c_sp_armored_lc_naval_engine_conversion_tech", "c_sp_armored_lc_transmission_improvements_tech",
       "c_sp_armored_lc_specialized_field_manuals_tech"])

# ---- naval -----------------------------------------------------------------------------------------------------
F = folder("naval_classic", "Naval, classic", "naval_folder", "across", "frigate", "navy",
           "Without Man the Guns: the same ships as fixed classes (destroyers, cruisers, battleships, carriers, "
           "submarines), no designer.", dlc="Without Man the Guns", variant_of="naval")
F.section("Escorts", 0)
C(F, "early_destroyer", "early_ship_hull_light", 2025, 0, req=[])
C(F, "basic_destroyer", "basic_ship_hull_light", 2036, 0)
C(F, "improved_destroyer", "improved_ship_hull_light", 2040, 0)
C(F, "advanced_destroyer", "advanced_ship_hull_light", 2044, 0)
C(F, "early_light_cruiser", "basic_ship_hull_light", 2025, 1, req=[], name="Air-Defence Destroyer (2025)",
  desc="An escort built around its radar and missiles: the classic tree's light cruiser.")
C(F, "basic_light_cruiser", "basic_ship_hull_light", 2036, 1, name="Air-Defence Destroyer (2036)")
C(F, "improved_light_cruiser", "improved_ship_hull_cruiser", 2040, 1, name="Air-Defence Destroyer (2040)")
C(F, "advanced_light_cruiser", "advanced_ship_hull_cruiser", 2044, 1, name="Air-Defence Destroyer (2044)")
F.section("Cruisers", 2)
C(F, "early_heavy_cruiser", "early_ship_hull_cruiser", 2025, 2, req=[])
C(F, "basic_heavy_cruiser", "basic_ship_hull_cruiser", 2036, 2)
C(F, "improved_heavy_cruiser", "improved_ship_hull_cruiser", 2040, 2)
C(F, "advanced_heavy_cruiser", "advanced_ship_hull_cruiser", 2044, 2)
F.section("Capital ships", 3)
C(F, "val_c_missile_bc", "val_heavy_cw2", 1985, 3, new=True, req=["val_c_gun_battleship"],
  unl=["new equipment: battle_cruiser_cw2, Missile Battlecruiser (fixed class)"])
C(F, "early_battlecruiser", "early_ship_hull_heavy", 2025, 3, name="Missile Battlecruiser (2025)")
C(F, "basic_battlecruiser", "basic_ship_hull_heavy", 2040, 3, name="Missile Battlecruiser (2040)",
  desc="A fast heavy ship with hypersonic missiles.")
C(F, "val_c_gun_battleship", "val_heavy_cw1", 1965, 4, new=True, req=[],
  unl=["new equipment: battleship_cw1, Gun Battleship (fixed class)"])
C(F, "early_battleship", "early_ship_hull_heavy", 2025, 4)
C(F, "basic_battleship", "basic_ship_hull_heavy", 2036, 4)
C(F, "improved_battleship", "improved_ship_hull_heavy", 2040, 4)
C(F, "advanced_battleship", "advanced_ship_hull_heavy", 2044, 4)
C(F, "heavy_battleship2", "sp_naval_super_heavy_battleship", 2044, 5, req=["improved_battleship"],
  name="Dreadnought II", desc="The second Dreadnought class, after the special project's first.",
  dlc="Needs the special project Dreadnought (Götterdämmerung)")
F.section("Carriers & submarines", 6)
C(F, "early_carrier", "early_ship_hull_carrier", 2025, 6, req=[], name="Light Carrier",
  desc="A light carrier for jump jets and drones.")
C(F, "basic_carrier", "basic_ship_hull_carrier", 2036, 6)
C(F, "improved_carrier", "improved_ship_hull_carrier", 2040, 6)
C(F, "advanced_carrier", "advanced_ship_hull_carrier", 2044, 6)
C(F, "early_submarine", "early_ship_hull_submarine", 2025, 7, req=[])
C(F, "basic_submarine", "basic_ship_hull_submarine", 2036, 7)
C(F, "improved_submarine", "improved_ship_hull_submarine", 2040, 7)
C(F, "advanced_submarine", "advanced_ship_hull_submarine", 2044, 7)
F.section("Sealift", 8)
C(F, "transport", "mtg_transport", 1965, 8, req=[])
C(F, "landing_craft", "mtg_landing_craft", 1985, 8)
C(F, "tank_landing_craft", "mtg_tank_landing_craft", 2025, 8)
C(F, "sp_multi_product_supply_ships", "sp_multi_product_supply_ships", 2038, 9, req=["transport"])
C(F, "sp_standard_tenshioned_replenishment_alongside_method", "sp_standard_tenshioned_replenishment_alongside_method",
  2043, 9)

# ---- air -------------------------------------------------------------------------------------------------------
F = folder("air_classic", "Air, classic", "air_techs_folder", "down", "jet", "air",
           "Without By Blood Alone: fixed aircraft in place of the plane designer. The close air support line becomes "
           "the attack drones.", dlc="Without By Blood Alone", variant_of="air")
F.section("Fighters & drones", 0)
C(F, "CAS1", "val_uav1", 2036, 0, req=["early_fighter"], name="Attack Drone",
  desc="Armed drones for ground attack: the classic tree's close air support line.", icon="drone_l")
C(F, "CAS2", "val_uav2", 2040, 0, name="Attack Drone II", desc="Faster jet-powered attack drones.", icon="drone_l")
C(F, "CAS3", "val_uav4", 2044, 0, name="Attack Drone III", desc="Stealthy attack drones.", icon="drone_l")
C(F, "heavy_fighter1", "basic_medium_airframe", 2036, 1, req=["early_fighter"], name="Heavy Interceptor",
  desc="Big long-range interceptors against bombers and cruise missiles.")
C(F, "heavy_fighter2", "improved_medium_airframe", 2040, 1, name="Heavy Interceptor II")
C(F, "heavy_fighter3", "advanced_medium_airframe", 2044, 1, name="Heavy Interceptor III")
C(F, "val_c_fighter_cw1", "val_small_cw1", 1965, 2, new=True, req=[],
  unl=["new equipment: fighter_equipment_cw1, Third-Generation Fighter (fixed design)"])
C(F, "val_c_fighter_cw2", "val_small_cw2", 1985, 2, new=True,
  unl=["new equipment: fighter_equipment_cw2, Fourth-Generation Fighter (fixed design)"])
C(F, "early_fighter", "iw_small_airframe", 2025, 2)
C(F, "fighter1", "basic_small_airframe", 2036, 2)
C(F, "fighter2", "improved_small_airframe", 2040, 2)
C(F, "fighter3", "advanced_small_airframe", 2044, 2)
C(F, "jet_fighter1", "modern_small_airframe", 2045, 2)
C(F, "jet_fighter2", "sp_air_supersonic_jet", 2050, 2, name="Hypersonic Interceptor",
  desc="An interceptor at hypersonic speed.", dlc="Needs the special project Hypersonic Aircraft (Götterdämmerung)")
C(F, "early_transport_plane", "bba_early_transport_plane", 1965, 3, req=[])
C(F, "improved_transport_plane", "bba_improved_transport_plane", 2005, 3)
C(F, "strategic_airlifter", "bba_strategic_airlifter", 2036, 3)
F.section("Strike & bombers", 4)
C(F, "early_bomber", "iw_medium_airframe", 2025, 4, req=["early_fighter"])
C(F, "tactical_bomber1", "basic_medium_airframe", 2036, 4)
C(F, "tactical_bomber2", "improved_medium_airframe", 2040, 4)
C(F, "tactical_bomber3", "advanced_medium_airframe", 2044, 4)
C(F, "jet_tactical_bomber1", "modern_medium_airframe", 2045, 4)
C(F, "jet_tactical_bomber2", "modern_medium_airframe", 2050, 4, name="Hypersonic Strike Aircraft II",
  desc="The hypersonic strike aircraft's second generation.")
C(F, "naval_bomber1", "iw_small_airframe", 2036, 5, req=["early_fighter"], name="Maritime Strike Aircraft",
  desc="Fighters armed with anti-ship missiles.", icon="jet")
C(F, "naval_bomber2", "improved_small_airframe", 2040, 5, name="Maritime Strike Aircraft II", icon="jet")
C(F, "naval_bomber3", "advanced_small_airframe", 2044, 5, name="Maritime Strike Aircraft III", icon="jet")
C(F, "strategic_bomber1", "basic_large_airframe", 2036, 6, req=["early_bomber"])
C(F, "strategic_bomber2", "improved_large_airframe", 2040, 6)
C(F, "strategic_bomber3", "advanced_large_airframe", 2044, 6)
C(F, "jet_strategic_bomber1", "modern_large_airframe", 2050, 6)
C(F, "scout_plane1", "iw_medium_airframe", 2036, 7, req=["early_fighter"], name="Airborne Early Warning Aircraft",
  desc="Radar aircraft that see the whole air battle.", dlc="La Resistance", icon="radar")
C(F, "scout_plane2", "val_uav2", 2040, 7, name="Reconnaissance Drones", desc="High-flying surveillance drones.",
  dlc="La Resistance", icon="drone_l")
F.section("Special projects", 8)
C(F, "reinforced_wings_mothership", "reinforced_wings_mothership", 2042, 8, req=["strategic_bomber2"])
C(F, "miniature_fighters", "miniature_fighters", 2044, 8)
C(F, "aerial_hangars", "aerial_hangars", 2046, 8)
C(F, "sp_centrifugal_jet_tech", "sp_centrifugal_jet_tech", 2045, 9, req=["jet_fighter1"])
