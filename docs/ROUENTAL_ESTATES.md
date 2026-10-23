# Rouental's three estates: a plan

The author is considering (2026-10-22) replacing the three powers (Prince, Voix, Speaker; in game, bare bones, since
2026-10-21: `docs/CONTENT.md`, Rouental) with a balance of **the three estates**. Nothing of it is built; this note
keeps the author's words and what was proposed, for when it is.

## The idea, in the author's words

"One thing I'm considering for the mod is changing the balance of power from Prince - Voix - Speaker, to one based on
the three estates. Swinging too far towards the first estate results in the Voix pulling the strings behind the
curtain, swinging to the second estate could result in either Roland gaining more power, or the Lord's Vassal
decentralizing the nation even more. The third estate gaining power could result in either Tara Blanchart guiding
towards minor reform and a constitutional monarchy, or the secret communist path. Maybe promising reform then never
doing the focuses to do them results in an uprising or something.

Or maybe any time the second estate triumphs it results in the decentralization, and there's a separate "Royal
Authority" bar that represents the authority of the Prince. And then a second scale for royal influence between Roland
and Serelle. So going for the Prince's path means playing the sides off each other until you come out on top."

Claude recommended the second version (the Crown above the estates, not one of them), with one rule to tie them:
**Royal Authority grows while no estate dominates and falls while one does**, so the Prince's path is keeping the
balance on purpose. The paths it leads to:

| where the balance ends | path |
|---|---|
| the First Estate dominant: the Voix rules from behind the curtain | Accept Reality (Anserra IX) |
| the Second Estate dominant: the realm breaks into its governorates | new (below) |
| the Third Estate dominant, the reforms carried out | Polite: minor reform, a constitutional monarchy |
| the Third Estate dominant, reform promised and not carried out | an uprising; the secret communist path (Rudely, Execute the Prince) |
| Royal Authority high, the court behind Roland | Steady As She Goes |
| Royal Authority high, the court behind Serelle | Kick Out Your Brother |

The broken promise: a decision that courts the Third Estate starts a mission (a timed decision); if its reform
focuses are not done when it runs out, the uprising follows.

## The author's answers (2026-10-22)

1. **The Second Estate's path**: "It would probably be a playable path. Rouental breaking into its governorates, with
   the ability to replace governors removed. Maybe there could be a way to reabsorb them like in base game's
   decentralized Yugoslavia." (The base game's Yugoslavia releases its parts as puppets, `release_puppet`, and sets
   them to `autonomy_integrated_puppet`, a subject level that sends most of its military factories and its manpower
   to the overlord and cannot declare war; they are annexed later. That level asks for a DLC and forbids a fascist
   overlord with a fascist subject, so Rouental's would be the mod's own, as its Protectorate is.)
2. **The start**: "It would probably start 35 First Estate, 35 Second Estate, 20 Third Estate." **Tara Blanchart**:
   "It might make sense to move Tara to the Second Estate path and come up with a new Third Estate leader, as she is
   Roland's friend, and the Lady Chancellor of the Privy Council in addition to Speaker of the Estates."
3. **Roland and Serelle**: "It'd probably be best for it to matter all game, I suppose, though I'm not sure what it'd
   do. Maybe military bonuses for Serelle, diplomacy bonuses for Roland?"

## The author's answers, later the same day

1. "Yeah, that's a good idea, only the disloyal governorates break away. (Is governorates right? Maybe there's a better
   word in french.)"
2. "35/35/30 yes, she would lead the decentralized Rouental. In all paths save communist Rouental will remain the Sacred
   Principality of Rouental. Cultural and religious intertia is just too strong for anything else. I'm not sure on the
   democratic leader yet, just use a placeholder for now." (Rouental's formal name under every government but the
   communist is the Sacred Principality since then: `nations.IDEOLOGY_NAMES`.)
3. "If we can tie things to Serelle winning battles, that'd be great. But otherwise it'll mostly be through decisions. I
   like those rewards though. And no need to tie it into steady as she goes / kick out your brother. Those are both
   placeholder focuses and won't stick around. That is the idea though, which character is leading decides who comes
   out on top." (The game's `on_army_leader_won_combat` fires for a general who wins a combat: it can be tied.)

"Go ahead with the mockup": `deco_ui/art/proposals/three_estates/` (its README has what is the author's and what is
Claude's placeholder).

**Symbols, not portraits** (the author, the same day): "Instead of portraits, I think I'd prefer to use symbols for
the three estates. A golden rogacina issuant from a cauldron for the First Estate (the symbol of the faith,) three crowns
pierced by a sword for the second estate, and I don't know what the third estate could use." Drawn for the mockup
(`deco_ui/art/proposals/three_estates/symbols.py`, the rogacina traced from the author's picture); for the Third Estate
three candidates of Claude's: a beehive, a sheaf of wheat bound with a key, a mural crown with wheat. Then: "Ah,
"rogacina issuant from a cauldron" is the name of the symbol, it didn't mean to put it above an actual cauldron. Maybe
just have the symbol for the 2nd estate be three crowns arranged in a triangle. Maybe have the crowns look like a
slightly more ornamented version of this? One with a red gem, one with blue, one with green? For the third estate, I
prefer the wheat and key." So: the rogacina alone; three crowns two and one after the author's picture of a crown,
ornamented, red, blue and green; the sheaf bound with a key.

Then: "space out the three crowns a little more evenly", and "Spread the crowns out a little more I suppose ... Also, maybe make a mockup showing what it'd look like if the symbols were in the triangles, rather than off to the side." The crowns are 30 px apart now (on the 200 px drawing), and `three_estates_window_inside.png` puts each symbol inside its corner zone, the estate's name, zone and share outside it. The author: "Let's go with the symbols inside the triangle. In addition, try to come up with something besides "altar and manor." Something that fits with the alliteration of the other equivalents of it." So the symbols are inside the corners on every screen of the mockup, and the edge where the Third Estate is shut out was Altar and Arms (Claude's), with Bell and Banner and Cloister and Castle offered beside it. The author: "I'll go with Cloister and Castle." So it is **Cloister and Castle**, beside Church and Commons and Manor and Market.

## Open

- The Third Estate's champion (the author's to name), and whether the reformer and the secret communist are one person.
- The mockup's placeholders (the zones' names but Cloister and Castle, Royal Authority's numbers, the scale's bonuses, the decisions, the breaking
  line at loyalty 40).
