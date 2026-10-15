"""Layout of the army bar (interface/leadergroups.gui, v0.7): where the game draws each piece, and the frames'
openings and plaques, so that the frames (gen_textures.py), the count boxes (make_leadergroups.py) and the preview
(preview_armybar.py) agree.

An army card: its frame at the portrait window's (-1, -12), 84 x 117, over the portrait at (8, -5) (156 x 210 at
0.39); the empty card (no commander yet) at (7, -6). An army group card: its frame at (-1, -21), 90 x 126, over the
portrait at (8, -15) (0.45); the empty card at (8, -15). The plate behind a run of cards is the game's: the army
group's piece starts it (its left edge the only soft one), each army's piece carries it on, the last army's ends it.
"""
FRAME_ARMY = (-1, -12)
FRAME_GROUP = (-1, -21)
# in frame coordinates: the arched opening (left, right, apex, where the arch meets the sides, bottom), the card's
# outline, the plaque for the division count
ARMY = dict(hole=(10, 69, 8, 21, 88), body=(2, 2, 82, 112), plaque=(6, 90, 78, 110))
GROUP = dict(hole=(10, 78, 7, 22, 99), body=(2, 2, 88, 123), plaque=(6, 101, 84, 121))
ADD_ARMY = (7, -6)
ADD_GROUP = (8, -15)
COUNT_FONT = "valsora_deco_value_17"


def count_box(spec, frame):
    """the plaque, in the portrait window's coordinates: where make_leadergroups puts the count"""
    px0, py0, px1, py1 = spec["plaque"]
    return dict(x=px0 + frame[0], y=py0 + frame[1], w=px1 - px0, h=py1 - py0)


def hole_centre(spec, frame, add):
    """the opening's centre in the empty card's own picture (the game draws that picture 1-2 px off the opening)"""
    x0, x1, top, sh, bottom = spec["hole"]
    return (x0 + x1) / 2 + frame[0] - add[0], (top + bottom) / 2 + frame[1] - add[1]


COUNT_ARMY = count_box(ARMY, FRAME_ARMY)        # x 5, y 78, 72 x 20
COUNT_GROUP = count_box(GROUP, FRAME_GROUP)     # x 5, y 80, 78 x 20
