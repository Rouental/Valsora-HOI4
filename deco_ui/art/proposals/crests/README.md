# The crests: options (v0.8.2; the user's choices in the mod since v0.8.3)

The author (2026-10-15), on the superevent: "the guillotine logo won't be suited for all superevents. Maybe come up
with something else?"; and on the events: "The logo at the top of country / leader / long events doesn't read so well
at this size. Maybe go with a different design?"

The author's answer (2026-10-15, later): "For the event crest, I think I like the stepped keystone, but maybe lower the
diamond just a little so it's not touching the top?" (done: 12.5 px above the edge instead of 15) and "The superevent
crest being a globe is okay, but maybe raise the globe so it intersects the top of the event panel in the center, and
show the whole globe" (done in v0.8.3: the ringed newsreel globe, the author's favourite of the globes, whole, rising
across the frame's top edge in the middle).

`options.png` (`tools/proposals_crests.py`, redrawn for v0.8.3) shows each at the game's size and at twice it.

- **The superevent's crest**: since v0.8.3 **the ringed globe**, whole, across the frame's edge (`globe_ringed`, first
  in the sheet); v0.8.2's half sunburst with **Valsora rising** (the top half of the news masthead's globe) on a
  lacquer medallion is `globe`. The others: a compass star, an hourglass, a laurel
  wreath round a star, and the mockup's guillotine (before). To switch: `EMBLEM` in `scripts/superevents_deco.py`
  (one of `EMBLEMS`), then the Valsora build.
- **The event cards' crest**: a **stepped keystone with a diamond** in the mod (v0.8.3: the diamond lowered), in place of v0.7's half sunburst (its 36
  thin rays and inner ring blurred into speckle at 56 px). The others: Valsora rising in bold rays (a blob at this
  size), a fan of seven broad rays, a diamond on the edge with rules. To switch: `EV_CREST` in `tools/crests.py` (one
  of `DESIGNS`), then `tools/build_all.py` and the Valsora build.
