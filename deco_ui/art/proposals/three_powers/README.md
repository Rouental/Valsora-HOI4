# The three powers of Rouental as a triangle: a proposal (not in the mod)

The author, 2026-10-21, night: "Rouental lacks a defined constitution, and power tends to fluctuate between the Sacred
Prince, the Voix, and the Speaker of the Estates General", and Pious estates "will appreciate actions that push the
balance of power towards the Voix"; then: "Yes, give me a mockup of the triangle." On the first mockup: the zones "Yes,
it looks good"; the start "Probably Prince 40, Voix 35, Speaker 25. Rouental is just coming out of a long regency by
the previous Voix who had tried to cement her power, ended only once the previous Voix died and the new one assumed the
office and willingly gave up a lot of the power"; the Voix is Mahaut VI ("the leader of Brillagne / theocratic
Rouental", her portrait the mod's), the Speaker Tara Blanchart; the Southmarch's Reformed Seranists "respect the Voix
as a spiritual leader, but don't consider them self bound to her", and she "isn't fond of them".

| Picture | What it shows |
|---|---|
| `three_powers_window.png` | 1 June 2036. The politics screen with the three powers' button under the popularities, where the game's balance of power button sits, and its window open beside it. The triangle: the Prince at the top, the Voix bottom left, the Speaker bottom right, each corner's share; the marker in the middle zone with its six months' trail. Seek the Voix's Blessing hovered: the dashed arrow shows where it would move the balance, and its tooltip names the Pious estates who welcome it and the Southmarchers who look on coolly. Beside the triangle: the three powers, the decisions, the estates' leanings and the record of what moved the balance |
| `three_powers_throne_altar.png` | 1 December 2036, after two decrees, a blessing and an event: the Speaker under 15, so the zone is Throne and Altar (its effects under the triangle). The Speaker's card says the Speaker is shut out, and the Proud estates who lean to the Speaker have lost loyalty |
| `three_powers_zones.png` | A sheet for the author: the seven zones, where each begins, and what each would do |

**How it reads.** The three shares always make 100, so the balance is one point in the triangle: the nearer a corner,
the more that power holds. A power of 60 or more rules (the three corners: Sacred Majesty, Rule of the Voix, the
Estates Supreme). A power under 15 is shut out (the three strips along the edges: Throne and Altar without the Speaker,
Crown and Estates without the Voix, the Prince in Name). Everything between is the Unwritten Balance, Rouental as it
has long been, with no effects. Each zone carries its effects; each month the balance drifts a point or two on its own
("power tends to fluctuate"); decisions, events and focuses move it further. The estates of the governorates take
sides: Pious estates welcome a move toward the Voix, Leal estates toward the Prince and Proud estates toward the
Speaker (the author's, "for now. Eventually I'll go through and assign each attitude to a side on the balance").

**The author's:** the zones (kept), the start (Prince 40, Voix 35, Speaker 25), the holders (Roland II Cahun, Mahaut
VI, Tara Blanchart), the leanings (Pious to the Voix, Leal to the Prince, Proud to the Speaker, for now; every
attitude a side later), the Southmarchers' coolness toward her.
**Placeholders, Claude's:** the zones' names, their effects; the four decisions, their costs and shifts; the events in
the record (the regency's last officials retiring among them); the estates' attitudes (the
governorates' mockup's, `../governorates/realm.py`). Tara Blanchart has no portrait yet.

**In game** (as planned, nothing built): the game's own balance of power has two sides only (`common/bop`, a bar), so
the triangle would be a scripted GUI (`common/scripted_guis`): a button attached to the politics screen
(`parent_window_token = politics_tab`) opening a window of our own beside it, as the game's balance of power window
slides out. The shares are three country variables; the marker is placed by the GUI's `properties` (x and y worked out
in script from the shares); the zones are dynamic modifiers swapped in when the balance crosses a line; the drift is a
monthly on_action; the decisions are ordinary decisions in the window's list. The triangle and its zones are one
texture; the trail six small icons placed the same way as the marker.

How they are made: `make.py` lays the screens out with the pieces of `../next_screens/deco.py` (the Deco UI's palette,
fonts and shapes) and draws them in Chromium; the politics screen behind is drawn simply, not the Deco UI's own.

    CHROMIUM_PATH=/opt/pw-browsers/chromium python3 make.py
