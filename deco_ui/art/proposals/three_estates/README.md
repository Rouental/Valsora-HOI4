# The three estates of Rouental: a proposal (not in the mod)

In place of the three powers (`../three_powers/`, in game since 2026-10-21, bare bones). The author, 2026-10-22:
"changing the balance of power from Prince - Voix - Speaker, to one based on the three estates ... any time the second
estate triumphs it results in the decentralization, and there's a separate "Royal Authority" bar that represents the
authority of the Prince. And then a second scale for royal influence between Roland and Serelle. So going for the
Prince's path means playing the sides off each other until you come out on top." Then: only the disloyal governorates
break away; the start 35 / 35 / 30; Tara Blanchart leads the decentralized Rouental; the democratic leader a
placeholder; Serelle military bonuses, Roland diplomatic ones, tied to her battles if it can be done; "Go ahead with the
mockup." The plan and the author's words in full: `docs/ROUENTAL_ESTATES.md`.

| Picture | What it shows |
|---|---|
| `three_estates_window.png` | 1 June 2036. The politics screen with the Three Estates' button where the three powers' sits, and its window. The triangle: the First Estate (the clergy, Anserra IX) at the top, the Second (the nobility, Tara Blanchart) bottom left, the Third (the commons, their champion to be named) bottom right; the marker in the Balance of Estates. Beside it: the estates, the Crown (Royal Authority 35 and rising; whom the Court follows, Roland 62, his diplomatic bonuses), the decisions, the estates' leanings. Under the triangle the Promised Reforms running (212 days left). Divide and Rule hovered: the strongest estate gives ground |
| `three_estates_lords_realm.png` | 1 March 2037. The Second Estate at 63: the Lords' Realm. Royal Authority 12 and falling; the Court behind Serelle (her army bonuses); in place of the decisions, the realm's map with the five governorates under 40 loyalty that would break away, numbered on their seals |
| `three_estates_symbols.png` | The three estates' symbols, in place of their holders' portraits (the author: "Instead of portraits, I think I'd prefer to use symbols for the three estates. A golden rogacina issuant from a cauldron for the First Estate (the symbol of the faith,) three crowns pierced by a sword for the second estate, and I don't know what the third estate could use"): the rogacina traced from the author's picture, rising from a bronze cauldron; three gold crowns on a steel sword; for the Third Estate three candidates, a beehive (in the screens), a sheaf of wheat bound with a key, a mural crown with wheat; each at the sizes the window draws them |
| `three_estates_zones.png` | A sheet for the author: the seven zones, where each begins, what each does and where it leads; Royal Authority's bands and how it moves; what Roland and Serelle each give when they lead |

**How it reads.** The three estates' shares make 100, so the balance is one point in the triangle. An estate of 60 or
more takes Rouental down its path (the corners: the Voix Behind the Curtain, the Lords' Realm, the Commons
Ascendant); one under 15 is shut out (the edges: Altar and Manor, Church and Commons, Manor and Market); between them
is the Balance of Estates, where the Crown holds the scales. **Royal Authority** (0 to 100) is the Crown's own: it
grows a point a month while the balance holds, stays while an estate is shut out and falls two while one dominates, so
the Prince's path is keeping the estates in balance on purpose (Divide and Rule spends it to pull the strongest back).
**Whom the Court follows** is a scale between Roland and Serelle: whoever leads gets their side's bonuses, the more the
further they lead (Roland the Crown's diplomacy, Serelle its army); decisions move it, and every battle Serelle's army
wins moves it toward her. **The Promised Reforms**: Promise Reform moves the balance far toward the commons and starts a
mission; if its reform focuses are not done in time, the commons rise and the secret communist path opens.

**The author's:** the estates, the Second Estate's decentralization and Royal Authority apart from the triangle, the
Roland and Serelle scale and its sides (military for Serelle, diplomacy for Roland, her battles), only the disloyal
governorates breaking away and won back as the base game's Yugoslavia does, the start (35 / 35 / 30), Tara Blanchart
for the Second Estate, the Third Estate's leader a placeholder; Rouental the Sacred Principality on every path but the
communist one (in the mod since 2026-10-22).
**Placeholders, Claude's:** the zones' names, effects and the lines at 60 and 15; Royal Authority's start (30), bands
and monthly moves; the scale's start (Roland 60), its bonuses and how far they reach; the decisions, costs and shifts;
the breaking line (loyalty under 40); the leanings (Pious to the First Estate and Proud to the Second carried over from
the three powers; Mercantile to the Third and Leal to the Crown new); the dates and numbers on the screens.

**In game** (as planned, nothing built): the three powers' window becomes the estates' (the same triangle, marker,
trail and zones as dynamic modifiers); Royal Authority and the scale are country variables shown as bars (a frame per
step, as the governorates' loyalty bar), moved monthly by the zone (`on_monthly_ROU`); Serelle's battles by the game's
`on_army_leader_won_combat` (it fires for a general who wins a combat; capped a month); the Promised Reforms a mission
decision (`days_mission_timeout`, its `timeout_effect` the uprising); the Lords' Realm releases the governorates under
the line as subjects of a level of the mod's own (the base game's `autonomy_integrated_puppet` asks for a DLC and bars
a fascist overlord with a fascist subject), each won back by a decision.

The estates are shown by their symbols (`symbols.py`, drawn by hand as SVG: the rogacina from the author's picture;
the cauldron, the crowns and sword and the Third Estate's candidates Claude's), on a dark ground in each estate's colour,
in the corners' medallions and the estates' cards; their holders' names stay in the cards.

How they are made: `make.py` draws with the pieces of `../next_screens/deco.py` and the three powers' mockup (its
triangle and politics screen, given the estates), the realm's map from `scripts/rouental_realm.py`.

    CHROMIUM_PATH=/opt/pw-browsers/chromium python3 make.py
