"""Layout of the national focus tree window (interface/nationalfocusview.gui), v0.6 styling (the FocusTree mockup).

The window opens flush under the top bar's band, like the side panels, and leaves the same notch round the flag
medallion and the decisions seal (it is drawn over the top bar). Its header: the game's "National Focus" as a small
label, the country's focus tree title and its name and sub-ideology under it (a scripted GUI attached to the focus
view), the filter chips, the search box, zoom and close at the right. The tree below keeps the game's geometry (focus
spacing, links); its background is the mockup's scale pattern inside a gilt frame.

Each focus is a medallion and a plate (the game's "bg" button): the game swaps that sprite by the focus's state
(GFX_focus_unavailable / _can_start / _current / _completed), so its picture holds both, in four looks. The focus
icon sits on the medallion and is the game's own.

national_focus_item is 165 x 128; the game centres the focus icon at (87.5, 20).
"""
import layout_panels as LPN

WIN_X = -3                             # the game's x for the window (its first 3 px are off-screen)
TOP = LPN.TOP                          # 62: flush under the band
HEAD_H = LPN.HEAD_H                    # 114: the header picture, down past the seal's bottom
TREE_Y = HEAD_H                        # the tree starts under it (vanilla: 47)
HX = LPN.hx(WIN_X)                     # 187: the header's text starts right of the notch
KICKER = dict(x=HX + 2, y=12, w=600, h=16)          # the game's own title, "National Focus", as a small label
TITLE = dict(x=HX, y=27, w=900, h=40)                # scripted: "<Adjective> Focus Tree" (title_30)
SUBTITLE = dict(x=HX + 2, y=71, w=900, h=22)         # scripted: "<full name> · <sub-ideology>" (italic_15)
CONTROLS_CY = 52                       # the right-hand controls are centred on this row
CLOSE = (-52, CONTROLS_CY - 17)        # UPPER_RIGHT, the politics screen's 34 px close diamond
FIND = (-344, CONTROLS_CY - 21)        # the search box (40 px tall)
ZOOM = (-233, CONTROLS_CY - 16)
FILTERS = (-770, CONTROLS_CY - 18)     # the filter chips (36 px)
FILTER_DROPDOWN_Y = HEAD_H - 3         # the dropdown of further filters opens under the header

# a focus: medallion and plate, one picture (the game's bg button)
ICON_C = (87.5, 20)                    # the focus icon's centre (the game's: item centre + (5, -44))
MEDALLION = 93                         # octagon behind the icon (odd, so it centres on the icon's half pixel)
BG = dict(x=9, y=-27, w=157, h=118)    # the picture: medallion centred on the icon, the plate under it
PLATE = dict(y=84, h=34)               # in the picture: the plate overlaps the medallion's foot by 9.5 px
NAME = dict(x=13, y=60, w=149, h=29)   # the focus's name on the plate: two lines of body_13 (14 px)
HALO = 150                             # the in-progress halo and the search highlight (3 frames each), centred on the icon
TREE_TILE = 192                        # the tree's pattern tile (64 x 32 scales, so 192 repeats seamlessly)
SEARCH = dict(w=232, h=40)
ZOOM_D = 30
FILTER = 36                            # filter chip (2 frames: off / on)
LEGEND = dict(w=560, h=30, x=-592, y=-66)   # LOWER_RIGHT, above the horizontal scrollbar
HEAD_TILE_B = 260                      # the header is a cornered tile: 260 px kept at each end (the notch is
HEAD_TILE_W = 2 * HEAD_TILE_B + 96     # in the left one), a 96 px middle repeated to the window's width
