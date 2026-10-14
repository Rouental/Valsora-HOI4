"""Layout of the national focus tree window (interface/nationalfocusview.gui), v0.4 styling.

The window and its tree keep the game's geometry (focus spacing, links); this restyle changes the chrome:
a header band with the gilt title, the search box, zoom and close buttons, the filter chips, the tree
background, the name plates under the focus icons (the game swaps three plate sprites by focus state, so
those textures are replaced at their paths), a medallion behind every focus icon, the detail pop-up, and
a legend in the lower right. Focus icons are untouched.

national_focus_item is 165 x 128; the focus icon is centred at (87.5, 20) and the name plate (the "bg"
button) is drawn at PLATE's position.
"""
HEADER_H = 47                          # the tree starts at y 47
TITLE = dict(x=40, y=10, w=600, h=30)
PLATE = dict(x=7, y=40, w=160, h=34)   # name plate under each focus (unavailable / can start / completed)
NAME = dict(x=11, y=42, w=152, h=30)   # focus name, centred on the plate, up to two lines
ICON_C = (87.5, 20)                    # focus icon centre (the game's: item centre + (5, -44))
MEDALLION = 78                         # octagon behind the icon
SEARCH = dict(w=232, h=40)
ZOOM = 30
FILTER = 36                            # filter chip (2 frames: off / on)
CLOSE = (-48, 7)                       # UPPER_RIGHT
LEGEND = dict(w=580, h=30, x=-612, y=-66)   # LOWER_RIGHT, above the horizontal scrollbar
TREE_TILE = 192
