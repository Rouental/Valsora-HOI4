# The crests: options (v0.8.2)

The author (2026-10-15), on the superevent: "the guillotine logo won't be suited for all superevents. Maybe come up
with something else?"; and on the events: "The logo at the top of country / leader / long events doesn't read so well
at this size. Maybe go with a different design?"

`options.png` (`tools/proposals_crests.py`) shows each at the game's size and at twice it.

- **The superevent's crest**: the half sunburst stays; its medallion is lacquer instead of red and holds **Valsora
  rising** (the top half of the news masthead's globe) in the mod. The others: a compass star, an hourglass, a laurel
  wreath round a star, and the mockup's guillotine (before). To switch: `EMBLEM` in `scripts/superevents_deco.py`
  (one of `EMBLEMS`), then the Valsora build.
- **The event cards' crest**: a **stepped keystone with a diamond** in the mod, in place of v0.7's half sunburst (its 36
  thin rays and inner ring blurred into speckle at 56 px). The others: Valsora rising in bold rays (a blob at this
  size), a fan of seven broad rays, a diamond on the edge with rules. To switch: `EV_CREST` in `tools/crests.py` (one
  of `DESIGNS`), then `tools/build_all.py` and the Valsora build.
