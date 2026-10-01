"""Settings shared by the pipeline scripts."""

# Game map size. HOI4 needs both sides to be multiples of 256 and crashes above
# roughly 13.24M pixels in total; 5120x2560 = 13,107,200 is the largest 2:1 map
# under that cap (the author's canvas is 2:1 too).
MAP_W, MAP_H = 5120, 2560

# Output pixels per source (.pdn) pixel for every continent. A straight fit of the
# 14000-wide source into 5120 would be 0.366; 0.375 draws each continent a little
# larger relative to the frame than the source does, and ~28% wider than the previous
# 5632x2048 build (0.293). At 0.38 the gaps between continents drop to ~91 px.
SCALE = 0.375

# Minimum open water between two different continents, in output pixels, and the
# empty band kept along the top and bottom edges.
MIN_GAP = 100
MARGIN_Y = 70
# Land stays at least this far from the wrap seam at x = 0 (no province may cross it).
SEAM_MARGIN = 8

# Continent blocks, in the order used by work/block_full.npy. Nonscio and Araseos
# move as one block: the Aikos / Midtierre archipelago ties them together.
BLOCKS = ["WEST", "AISLADA", "SOLITAS", "YASTREOVAKIA", "USNISTAN", "ORIENTALIS"]

# HOI4 continents (map/continent.txt), in order: definition.csv uses index + 1.
CONTINENTS = ["nonscio", "araseos", "aislada", "solitas", "yastreovakia", "usnistan", "orientalis"]
# Countries: tag, name, adjective, colour. The first seven are the placeholders, one
# per continent, keyed by continent.
COUNTRIES = {
    "nonscio": ("NSC", "Nonscio", "Nonscian", (216, 84, 84)),
    "araseos": ("ARS", "Araseos", "Araseosi", (116, 152, 206)),
    "aislada": ("AIS", "Aislada", "Aisladan", (70, 170, 70)),
    "solitas": ("SLT", "Solitas", "Solitan", (214, 110, 214)),
    "yastreovakia": ("YAS", "Yastreovakia", "Yastreovakian", (96, 190, 150)),
    "usnistan": ("USN", "Usnistan", "Usnistani", (184, 172, 100)),
    "orientalis": ("ORI", "Orientalis", "Orientalian", (236, 160, 70)),
    # real countries drawn by the author (tags checked against vanilla's country_tags)
    "rouental": ("ROU", "Rouental", "Rouentaise", (54, 106, 64)),
    "seigne": ("SGN", "Seigne", "Seignois", (240, 240, 240)),
    "evriches": ("EVR", "Evriches", "Evrichois", (240, 208, 64)),
    "hollier": ("HLR", "Hollier", "Hollierois", (185, 53, 52)),
    "selgrave": ("SGV", "Selgrave", "Selgravian", (112, 16, 32)),
    "lustiana": ("LST", "Lustiana", "Lustianan", (28, 28, 28)),
    "lanzerac": ("LZC", "Lanzerac", "Lanzeracois", (168, 130, 36)),
    "guedelon": ("GDN", "Guedelon", "Guedelonnais", (7, 76, 130)),
    "cardonia": ("CRD", "Cardonia", "Cardonian", (84, 28, 120)),
    # 2026-09-30, south-west of Rouental; a placeholder nation (author), first called
    # Linterre, renamed Placeholdros on 2026-10-01
    "romanoddle": ("RMD", "Romanoddle", "Romanoddlian", (46, 139, 150)),
    "selto": ("STO", "Selto", "Seltan", (214, 120, 40)),
    "linterre": ("LNT", "Placeholdros", "Placeholdrosian", (190, 150, 200)),
    # 2026-09-30, south of Romanoddle and Selto; all Portuguese (author). Estande's
    # colour is the red of its flag (author: the green blended with Rouental); the rest are Claude's picks
    "rastava": ("RST", "Rastava", "Rastavan", (184, 160, 72)),
    "volinovia": ("VLN", "Volinovia", "Volinovian", (70, 100, 170)),
    "estande": ("ESD", "Estande", "Estandese", (153, 0, 0)),
    "coraliza": ("CRZ", "Coraliza", "Coralizan", (240, 122, 92)),
    "placeholdria": ("PLH", "Placeholdria", "Placeholdrian", (238, 196, 222)),
    # 2026-10-01, east of Estande: Illiricium (map name "Senatorial Illiricium", the
    # author's), its Bleacherist republics, and Royalist Illiricium on its island.
    # Colours and adjectives are Claude's picks; Illiricium's blue is its flag's, and its
    # Bleacherist puppets are shades of blue (author, 2026-10-01)
    "illiricium": ("ILR", "Senatorial Illiricium", "Illirician", (32, 44, 140)),
    "cotefer": ("CTF", "Côtefer", "Côteferan", (70, 150, 190)),
    "entroterra": ("ETR", "Entroterra", "Entroterran", (140, 185, 235)),
    "mezzogiorno": ("MZG", "Mezzogiorno", "Mezzogiornese", (60, 105, 190)),
    "k_illiricium": ("KIL", "Royalist Illiricium", "Illirician", (212, 178, 60)),
    # 2026-10-01, the author's, east of Selgrave and Hollier. Kurikia's navy is its
    # flag's; Fraxhemark's flag red would vanish next to Hollier, so raspberry (Claude's)
    "kurikia": ("KRK", "Kurikia", "Kurikian", (34, 62, 96)),
    "fraxhemark": ("FRX", "Fraxhemark", "Fraxhemarkish", (200, 60, 110)),
}
# The placeholder countries, one per continent, are the recommended starts in the
# bookmark; the rest are playable but not listed there.
PLACEHOLDERS = CONTINENTS

# Graphical terrain: terrain.bmp palette index -> terrain type (vanilla 1.19.3
# common/terrain/00_terrain.txt). The index's palette colour is what the Terrain layer
# of "HOI4 Mod Map.pdn" uses. Index 14 marks lakes there; the game gets 15 for both.
TERRAIN_TYPES = {0: "plains", 1: "forest", 2: "hills", 3: "desert", 4: "forest", 5: "plains",
                 6: "mountain", 7: "desert", 8: "desert", 9: "marsh", 10: "mountain",
                 11: "mountain", 12: "desert", 13: "urban", 14: "lakes", 15: "ocean",
                 16: "mountain", 17: "hills", 18: "mountain", 19: "plains", 20: "mountain",
                 21: "jungle", 22: "jungle", 27: "mountain", 31: "mountain"}
TERRAIN_OCEAN, TERRAIN_LAKE, TERRAIN_PLAINS = 15, 14, 0

# Their colours on the Continents layer of "HOI4 Mod Map.pdn".
CONT_COLOURS = [(216, 84, 84), (116, 152, 206), (70, 170, 70), (214, 110, 214),
                (96, 190, 150), (184, 172, 100), (236, 160, 70)]

# Smallest province HOI4 accepts without complaint is 8 px; 16 leaves headroom.
MIN_PROVINCE = 16
# Enclosed water smaller than this is filled in as land rather than made a lake.
MIN_LAKE = 64

# Placeholder province bricks (pixels). Map width must divide by each of them.
LAND_CELL = 32
SEA_CELL = 128
LAKE_CELL = 48
# A piece of a brick smaller than this fraction of a full brick is merged into its
# neighbour, so coastlines don't leave slivers.
MIN_FRACTION = 0.25
# HOI4 reports a province wider or taller than 1/8 of the map ("TOO LARGE BOX").
MAX_BOX = 1 / 8

# States: land provinces grouped on a grid of this many pixels (about 3x3 land bricks).
STATE_CELL = 96
# Island states with fewer provinces join the nearest state within this many pixels.
MIN_STATE_PROVINCES = 3
ISLAND_REACH = 160
# Strategic regions: states grouped on this grid; seas on their own grid.
REGION_CELL = 384
SEA_REGION_CELL = 512
MIN_SEA_REGION_PROVINCES = 4

# Mod folder name inside Documents/Paradox Interactive/Hearts of Iron IV/mod/, and the
# name the launcher shows. The folder name matches the previous test build's.
MOD_DIR_NAME = "valsora_test"
MOD_NAME = "Valsora (test map)"
