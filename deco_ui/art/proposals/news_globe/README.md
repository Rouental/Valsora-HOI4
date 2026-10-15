# The news masthead's globe: options (v0.8.2; the ringed globe in the mod since v0.8.3)

The author (2026-10-15), on v0.8.1's globe: "I'm not quite satisfied with the globe. Could you give me a few options,
including an improved version of this one and the first globe, and maybe two or three other concepts?"

The author's answer (2026-10-15, later): "I think the globe I'm sending now is my current favorite of your designs",
the newsreel globe (1 below). It is in the mod since v0.8.3 (`layout_events.NEWS_GLOBE_STYLE = "ringed"`), and the
superevent's crest is the same globe, whole, across the frame's top edge.

`options.png` (`tools/proposals_globes.py`) shows each in the VALSORAN STANDARD masthead, at the game's size (the globe
is 60 px across) and at twice it (redrawn for v0.8.3 with the ringed globe first):

1. **In the mod since v0.8.3**, the author's favourite: the newsreel globe (`globe_ringed`), girdled by a tilted gilt
   ring (behind the globe at the back, over it in front).
2. v0.8.2, the v0.8.1 globe improved (`globe_art.globe`): lit from the upper left (pale to deep gilt land, lacquer to
   near-black sea), a bright limb on the lit side, the graticule over the sea only and stopping short of the pole
   (where it bunched into a star), the land a little less smoothed; seen above Nonscio and Araseos, as the Valsora
   mod's world tension globe.
3. v0.8.1 (`globe_flat`): flat gilt land, the graticule over sea and land, looking down on open sea.
4. The first, v0.8 (`globe_first`): every lake and channel, lit, a bright coast.
5. Concept: the whole world on one disc (`world_disc`), a map round the north pole, as on an emblem.
6. Concept: an engraving (`globe_engraved`): the land drawn by its coast in bright gilt.

To switch: `layout_events.NEWS_GLOBE_STYLE` ("ringed" or "lit"; another of `globe_art`'s in `layout_events.news_globe`),
then `tools/build_all.py` and the Valsora build. The superevent's crest is chosen apart (the Valsora mod's
`scripts/superevents_deco.py`, `EMBLEM`).
