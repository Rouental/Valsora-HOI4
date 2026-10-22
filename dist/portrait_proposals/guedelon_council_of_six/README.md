# Guedelon's Council of Six: its leader's portrait (2026-10-22)

The author: "Could you help me design a leader portrait for Guedelon, similar to Krionik's one? This is the symbol for
Guedelon's Council of 6, the executive body." The symbol is the author's (`source/portraits/gdn_council_of_six.png`:
their picture without the address of the tool it was made in, which ran under it). Guedelon's ruler is the council
now, "Council of Six" (`nations.NAMED_LEADERS`, as Krionik's Kriosaivak Council of Marshals), in place of the generated
Jacques Anthoine.

| file | what |
|---|---|
| `sheet.png` | the three, each twice the game's size and at it (156 x 210), on the Deco UI's lacquer |
| `portrait_A.png`, `seal_A.png` | **A, in the mod**: the symbol alone on the portrait's dark field, its disc 92 % of the width, as Krionik's emblem is |
| `portrait_B.png`, `seal_B.png` | B: the symbol in a lettered ring, as Krionik's emblem has one: CONSEIL DES SIX above, GUEDELON below (French, Guedelon's language in the mod), gold diamonds between, a band of darker blue between two gold rims |
| `portrait_C.png`, `seal_C.png` | C: the same ring in English, COUNCIL OF SIX |

The ring's words, colours and diamonds are Claude's; the letters are Federo, the Deco UI's. To use B or C:
`source/portraits/gdn_council_of_six.png` becomes `seal_B.png` (or C), and its crop in `nations.PORTRAITS` the one
`make.py` prints for it.

    python3 dist/portrait_proposals/guedelon_council_of_six/make.py
