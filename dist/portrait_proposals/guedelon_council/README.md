# Guedelon's council: its leader's portrait

**2026-10-22, later: the Conseil des Sept.** The author: "One revision, I'm changing the logo to this and making it the
Council of Seven (in french, obviously.) Redo option B with this logo, send it to me in a format that'll work to put in
the gazeteer, and I'll do it myself so you don't have to generate a new build until i send the next gazeteer update."
The symbol, seven shields round the griffin, is the author's (`source/portraits/gdn_council_of_seven.png`: their
picture without the address of the tool it was made in); the ring is version B's, CONSEIL DES SEPT above and GUEDELON
below.

| file | what |
|---|---|
| `gazetteer_portrait.png` | **for the Gazetteer**: 468 x 630, three times HOI4's 156 x 210 and under the page's 640 px, so the page keeps it as it is; the seal 92 % of the width on the game's dark field, as Krionik's emblem; no clear pixels. The import's face finder finds no face in it (checked), so it keeps the whole picture |
| `portrait_in_game.png` | the same at 156 x 210, as the game will show it |
| `seal.png` | the seal alone, 1000 px, clear outside its rim |
| `sheet.png` | the three side by side |

The ring's words are the author's ("Council of Seven ... in french"); its colours, the Federo letters and the diamonds
between the words are Claude's. The build keeps the Council of Six and the first symbol (`nations.NAMED_LEADERS`,
`nations.PORTRAITS` `GDN_council_of_six`) until the author's next Gazetteer export, whose ruler wins over them; then
those two entries go.

    python3 dist/portrait_proposals/guedelon_council/make.py

Before it (2026-10-22): the Council of Six with the first symbol (six rings), three ways, A (the symbol alone, in the
mod), B (the ring in French) and C (in English): in the history, `dist/portrait_proposals/guedelon_council_of_six/`.
