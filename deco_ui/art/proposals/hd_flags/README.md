# Larger flags: a mockup (not in the mod)

The author (2026-10-15): "I'm thinking about using larger flags in the mod. We switched to the current size as the
flags looked pixelated at an increased size, but if I gave the flag files over again, it could work. I'll have to
think on it. Maybe do a mockup of how it could look, but don't add anything to do with it into the mod yet."

`mockup.png` (`tools/proposals_hd_flags.py`): the top bar's flag medallion at today's size, at 1.5 and at 2 times,
with the flag at 1:1 in each; a close-up of today's flag stretched (as the game would show it) beside one made at
the larger size; and what the game's unsmoothed scaling does to a large flag where a screen still shows it at 82 x 52.

What it would take:
- **The flag files.** 113 of the mod's 120 flags are the author's own at 490 x 311 or larger, enough for 123 x 78 or
  164 x 104. Seven exist only at 82 x 52 (Merlovich, Arvorenia, Atrocha, Hoalepa, Ponchomagnifico, Silvamar, the
  United States of Solitas: the friend's, taken from their build): their originals are needed.
- **The game's flag size.** `NDefines_Graphics.NGraphics.COUNTRY_FLAG_TEX_WIDTH / HEIGHT` (82 / 52) in a defines file
  of ours, and every large flag the build writes (`gfx/flags/*.tga`, about 200 with the per-government ones) at the
  new size. The medium (41 x 26) and small (10 x 7) flags stay.
- **Every place that shows the large flag**, re-laid to show it at 1:1 (the medallion, the diplomacy screen, the
  state panel, the country selection ...) or left showing a jagged shrunk copy. The game doesn't smooth flags either
  way, so a flag looks right only at exactly its texture's size.
- **The medallion** grows with the flag (222 px tall at 1.5x, 296 at 2x, from 148): it covers more of the map's top
  left, and the top bar's other pieces keep their places.

Untested in game: whether the game accepts flag textures this size (the define's own comment ties the flag atlas,
`COUNTRY_FLAG_TEX_MAX_SIZE`, to the number of countries), and its memory use with ~200 larger flags. A branch build
and the author's `error.log` would answer both before anything else.
