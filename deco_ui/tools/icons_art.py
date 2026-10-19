"""The game's icons in the Deco style, in the mod (2026-10-19, the author: "You haven't changed the icons yet, but maybe I
forgot to approve that"): the proposals of proposals_icons.py (the resources, the focus tree's filters, the production
screen's icons and add-a-line buttons, the decisions' envelopes), drawn at the game's paths, sizes and frames.
proposals_icons.py stays the place they are drawn and compared with the game's (build/proposals_icons.png); a new or
redrawn icon is a proposal there first (no icon of the game's changes without the author's yes).

gen_textures.py adds them (keys ic_*).
"""
import proposals_icons as PI

ADDS = [("ic_" + key, PI.GI + rel, w, h, (lambda w=w, h=h, art=art: PI.svg(w, h, art)))
        for key, rel, w, h, art in PI.ITEMS]
