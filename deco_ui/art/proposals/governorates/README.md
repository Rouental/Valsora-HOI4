# The governorates in the decisions tab: a proposal (not in the mod)

The author, 2026-10-21: "I'd like to set up a system for interacting with the governorates in the decisions tab", then
"let's start with the map ... The governorates should display the name of the governor, loyalty, the attitude of the
parliament (examples could be leal, grasping, belligerent, quarrelsome, etc. ...). I'm tempted to have further info on
the individual states within the governorates, since levy quality can vary wildly between them. ... The royal fiefs
indeed be shown and handled separately. ... Don't go with rough shapes for the map, exactly follow the game's borders."

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

Placeholders, not the author's: the governors' names (a first name and the seat's fief), loyalty, the estates'
attitudes (the author's four and Claude's four more: `realm.ATTITUDES`), levy quality (five steps, `realm.LEVY`). Real:
the borders, the states and their names, manpower, the vassals' count, the Royal Fiefs, the Royal Host's stations.

In game it would be a scripted GUI on a decision category (`context_type = decision_category`, the game's own way:
`common/scripted_guis/_documentation.md`): the map as one picture a governorate (frames for the loyalty colours, picked
by a variable), each governorate's clicks caught by invisible buttons the build cuts along its state borders (assumed:
the game's buttons react on their whole rectangle), the card's texts from variables and scripted localisation.
