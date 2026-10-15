"""Layout of the events (interface/eventwindow.gui, v0.7.1): the option plates, shared by the texture
(gen_textures.py, 'ev_option'), make_events.py and preview_events.py.

The game draws every option the same way (one event_option_entry for all event windows): its picture at the entry's
top left, its text in the Name box. The plate is OPTION_W wide inside the game's 352 px picture, and each window's
options_grid is moved so the plate sits in the middle of the room it has (the user, 2026-10-15: the options sat
"significantly closer to the image than ... to the other side of the box. It should be centered between the two"):
- a country event: between the picture's gilt frame (its outer line at x 218.5) and the card's inner rail (576.5);
- a news event: the broadsheet's middle (its rails at 6.5 and 521.5);
- a leader event: the card's middle (580 wide);
- an operative event: under its text column (x 70-470).
"""
OPTION_W = 334              # the plate; the game's picture is 352 wide
OPTION_PAD = 10             # the text's margin inside the plate
CENTRES = {"EventWindow": (218.5 + 576.5) / 2, "EventWindow_News": (6.5 + 521.5) / 2, "EventWindow_leader": 290,
           "EventWindow_Operative": 270}


def grid_x(window):
    """options_grid's x: the plate centred on the window's centre line (to the nearest pixel)"""
    return int(CENTRES[window] - OPTION_W / 2)
