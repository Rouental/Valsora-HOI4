# The news masthead: other names

The author (2026-10-15), on v0.8's WORLD (globe) NEWS: "it still looks lopsided. I'd like it to be centered, and I
like the globe, but it's not quite there yet. Maybe you could stack it vertically? Or maybe swap to something like
"Valsoran Standard" or Clarion or Dispatch or something like that, so both words are the same length while keeping
the news theming."

The mod (v0.8.1) has **VALSORAN (globe) STANDARD**: the two words set to the same width in Federo by themselves, so
the medallion sits in the middle with the same space on either side. The globe is drawn anew: the land simplified to
what 60 px can show, flat gilt, a graticule, looking down on open sea with land round it.

`options.png` (`tools/proposals_masthead.py`) shows other names drawn by the same code. VALSORA CLARION balances
by itself too; DISPATCH and CHRONICLE need a little extra letter spacing to match their partner; WORLD NEWS needs a
lot, which is why it looked lopsided.

To switch: `NEWS_WORDS` in `tools/layout_events.py`, then `tools/build_all.py` and the Valsora build.

Stacking was tried on paper and doesn't fit: the band between the rules is 53 px high, and a globe over a line of
text needs about 90. Making the band taller would push the picture, headline and story down and shorten the story.
