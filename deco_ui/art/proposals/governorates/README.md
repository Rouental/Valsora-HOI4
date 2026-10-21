# The governorates in the decisions tab: a proposal (not in the mod)

The author, 2026-10-21: "I'd like to set up a system for interacting with the governorates in the decisions tab", then
"let's start with the map ... The governorates should display the name of the governor, loyalty, the attitude of the
parliament (examples could be leal, grasping, belligerent, quarrelsome, etc. ...). I'm tempted to have further info on
the individual states within the governorates, since levy quality can vary wildly between them. ... The royal fiefs
indeed be shown and handled separately. ... Don't go with rough shapes for the map, exactly follow the game's borders."

**Version 2 (2026-10-21, night), after the author's answers** ("Probably open as a larger window"; governors appointed
by the Prince, Crépuscule's always its own Prince; loyalty from the peoples; the estates' attitudes changing at their
sessions; levy quality hidden until inspectors are sent; a "ceremonial" levy step; no world map mode): `make2.py`.

| Picture | What it shows |
|---|---|
| `governorates_window_carcarelle.png` | The window opened from the decisions tab, the loyalty view: Carcarelle selected (the Carcaraise, Defiant: the loyalty's parts listed), a governor of the Prince's court, Proud estates, two of its states' levies seen by inspectors, the rest unknown; the four peoples the author has written of under the map |
| `governorates_window_crepuscule.png` | The peoples view (every state's people, from the fief list's cultural groups): Crépuscule selected, governed by its own Prince by law |
| `governorates_window_crown.png` | The levies view (only what inspectors have seen; the Crown's own fiefs always known): the Crown's Domain selected, Rêverie's guard Ceremonial; the inspectors' reports |

**Version 1** (the first answers), `make.py`: the same in the decisions panel itself.

| Picture | What it shows |
|---|---|
| `governorates_gheso.png` (`_2x`: the panel at twice the size) | The decisions panel with Rouental's Governorates category: the realm, a governorate selected (Gheso: its governor, loyalty, estates, its eight states with their levies, manpower and vassals, one state picked and lit on the map), a tooltip on another, the actions to come greyed |
| `governorates_crown.png` (`_2x`) | The Crown's Domain selected: the eleven Royal Fiefs, held by the King, the Royal Host's divisions in them |

How they are made: `realm.py` reads the build (`build/valsora_test`: the provinces map, the states, their names and
manpower), `source/governorates_ROU.json` (each state's governorate), `nations.ROYAL_FIEFS` and the fief map's plan
(`work/fief_states/plan.npz`: the author's fiefs inside each state, the vassals), and traces the map along its pixel
edges, so every line is a state border of the game (no rough shapes); `make.py` lays the screens out with the pieces of
`../next_screens/deco.py` (the Deco UI's palette, fonts and shapes) and draws them in Chromium:

    CHROMIUM_PATH=/opt/pw-browsers/chromium python3 make.py

Placeholders, not the author's: the governors' names (version 1: a first name and the seat's fief; version 2: a fief from
elsewhere, since governors are the Prince's courtiers or the Estates General's picks), loyalty (version 2: 50, the
peoples' leanings the author gave, the estates' attitude, the governor, and chance), the estates' attitudes (the author's
four and Claude's four more: `realm.ATTITUDES`), levy quality (`realm.LEVY`, a sixth step Ceremonial), which states the
inspectors have seen, the reports. Real: the borders, the states and their names, manpower, the vassals' count, each
state's people (the fief list's cultural group of the fief it is named for; 17 states named for no listed fief take
their governorate's commonest, marked *), the Royal Fiefs, the Royal Host's stations.

In game it would be a scripted GUI on a decision category (`context_type = decision_category`, the game's own way:
`common/scripted_guis/_documentation.md`): the map as one picture a governorate (frames for the loyalty colours, picked
by a variable), each governorate's clicks caught by invisible buttons the build cuts along its state borders (assumed:
the game's buttons react on their whole rectangle), the card's texts from variables and scripted localisation.
