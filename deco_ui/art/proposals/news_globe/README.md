# The news masthead's globe: options (v0.8.2)

The author (2026-10-15), on v0.8.1's globe: "I'm not quite satisfied with the globe. Could you give me a few options,
including an improved version of this one and the first globe, and maybe two or three other concepts?"

`options.png` (`tools/proposals_globes.py`) shows each in the VALSORAN STANDARD masthead, at the game's size (the globe
is 60 px across) and at twice it:

1. **In the mod: this one, improved** (`globe_art.globe`): lit from the upper left (pale to deep gilt land, lacquer to
   near-black sea), a bright limb on the lit side, the graticule over the sea only and stopping short of the pole
   (where it bunched into a star), the land a little less smoothed; seen above Nonscio and Araseos, as the Valsora
   mod's world tension globe.
2. Before, v0.8.1 (`globe_flat`): flat gilt land, the graticule over sea and land, looking down on open sea.
3. The first, v0.8 (`globe_first`): every lake and channel, lit, a bright coast.
4. Concept: the newsreel globe (`globe_ringed`), girdled by a tilted gilt ring.
5. Concept: the whole world on one disc (`world_disc`), a map round the north pole, as on an emblem.
6. Concept: an engraving (`globe_engraved`): the land drawn by its coast in bright gilt.

To switch: the `GA.globe(...)` call for the masthead in `tools/gen_textures.py` (and `rim=False` to `news_masthead`
for the ringed one), then `tools/build_all.py` and the Valsora build. The superevent's crest uses the same globe.
