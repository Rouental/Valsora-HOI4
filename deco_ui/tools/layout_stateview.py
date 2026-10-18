"""Layout of the state / province panel (interface/countrystateview.gui): what opens when a province is clicked.

v0.4 follows the mockup's state panel ("Rêverie" in the Main board): owner flag and state name in the
header with the owner as a subtitle, a stats row (victory points | manpower | resources), the shared
building slots, the state buildings, then claims and (for occupied states) resistance. The province
part below keeps the game's arrangement, since several of its elements are placed by the engine
relative to it. Coordinates are state_info_window pixels; the background is drawn at (5, 5).

Zones of the background (window y):
  header       5 .. 58    owner flag, state name, owner subtitle, close
  stats        58 .. 124  victory points | manpower | resources
  shared       124 .. 252 "shared building slots" line and the grid (2 rows of 7)
  buildings    252 .. 354 state buildings (infrastructure, air base, ...) with their levels
  claims       354 .. 400 claims (left) | resistance and compliance (right, occupied states only)
  modifiers    400 .. 456 state modifiers label and icons (placed relative to the province window)
  province     456 .. 486 province name band (victory points chip at the right)
  province     486 .. 655 terrain picture, province buildings
"""
BG = dict(x=5, y=5, w=450, h=650)
X0, X1 = 20, 440

HEADER = (5, 58)
# v0.10.2: the flag, its well and the name 10 px right, clear of the panel's corner bracket (to x 25 in the window; the
# user: "In the state tab, the decorative corner in the top left is covered by the flag")
OWNERS = (30, 16)                      # owner flag(s) (the game's overlapping box)
CONTROLLER = (362, 16)                 # controller flag when occupied (and its border at -5, -4), left of close
FLAG_WELL = dict(x=26, y=12, w=50, h=34)
NAME = dict(x=88, y=12, w=266, h=24)   # state name, gilt capitals
SUBTITLE = dict(x=88, y=36, w=266, h=16)    # the game's "owner" text
CLOSE = (-36, 10)                      # UPPER_RIGHT

STATS = (58, 124)
STAT_COLS = [X0, 160, 300]             # victory points | manpower | resources
STAT_LABEL_Y, STAT_VALUE_Y = 66, 84
POP_ICON = dict(x=160, y=80, scale=0.55)
MANPOWER_X = 188
RESOURCES = dict(x=300, y=76, w=140, h=44)

SHARED = (124, 252)
SHARED_LABEL = dict(x=X0, y=132, w=300, h=14)
ENERGY = dict(x=398, y=126)
SHARED_GRID = dict(x=16, y=168, cols=7, rows=2)    # entries draw at (4, -15) inside their 61x50 slot

BUILDINGS = (252, 354)
BUILD_LABEL = dict(x=X0, y=260, w=200, h=12)
BUILD_GRID = dict(x=X0 - 4, y=278)

CLAIMS = (354, 400)
CLAIMS_TEXT = dict(x=X0, y=366, w=110, h=20)
CLAIMS_FLAGS = (130, 362)
# resistance and compliance (occupied states), two rows in the claims band's right half (v0.10.2, the user: "Compliance
# and resistance look out of place": the game's rows are 30 px apart, so compliance ran over the State Modifiers rule at
# y 400): the icons at RES_SCALE, RES_ROW px apart, each bar (87 x 19, gen_textures 'sv_res_*') beside its icon
RESISTANCE = (236, 356)
RES_SCALE, RES_ROW, RES_BAR_X = 0.7, 23, 28

MODIFIERS = (400, 456)
PROV_HEAD = (456, 486)
PROV_BODY = (486, 655)

TILE = dict(w=56, h=48)                # building entry background (state and province buildings)
SLOT = dict(x=2, y=-3, w=52, h=46)     # shared building slot well, at this offset in its entry
LEVEL = dict(w=48, h=18)
CHIP = dict(w=44, h=24)
