"""Settings shared by the pipeline scripts."""

# Game map size. HOI4 needs both sides to be multiples of 256 and crashes above
# roughly 13.24M pixels in total; 5120x2560 = 13,107,200 is the largest 2:1 map
# under that cap (the author's canvas is 2:1 too).
MAP_W, MAP_H = 5120, 2560

# Output pixels per source (.pdn) pixel for every continent. A straight fit of the
# 14000-wide source into 5120 would be 0.366, so 0.37 draws each continent a little
# larger relative to the frame than the source does, and ~26% wider than the previous
# 5632x2048 build (0.293). 0.38 no longer leaves room for 100 px oceans between every
# pair of continents plus a clean wrap seam.
SCALE = 0.37

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
