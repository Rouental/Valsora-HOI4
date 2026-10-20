# Valsora's nations: the record

Who drew, named and decided what, nation by nation, in the order the nations came. Moved out of `CLAUDE.md` on
2026-10-15 (the author: "Tidy up the notes"); `CLAUDE.md` keeps the rules for adding a nation (Decisions worth
keeping, Countries).

- Each paragraph says whose each choice was. As a rule the names, governments and formal names are the author's,
  and the tags, map colours, adjectives and cultures Claude's.
- Every country as it is built (name, full name, ideology, sub-ideology, culture, leader, states):
  `dist/countries.md` (`scripts/country_list.py`, after a build). Their flags, rulers and map colours by continent:
  `dist/nations_by_continent.png` (`scripts/nation_sheet.py`).
- The settings themselves are in the code: `COUNTRIES` in `scripts/common.py` (tag, name, adjective, map colour),
  `scripts/nations.py` (formal names, leaders, capitals, city names, puppets, releasables, popularities) and
  `scripts/cultures.py` (`TAG_CULTURE`).
- Add a dated paragraph here for every new or changed nation, newest last.

## The first nations (2026-09-29 to 2026-10-02)

Real countries the author drew: Rouental ROU, Seigne SGN, Evriches EVR, Hollier
HLR, Selgrave SGV, Lustiana LST, Lanzerac LZC, Guedelon GDN, Cardonia CRD,
Romanoddle RMD ("the Romanoddlian Federation"), Selto STO, Placeholdros LNT (a
placeholder nation, author; called Linterre until 2026-10-01, the key in
`COUNTRIES` is still `linterre`), and
(second map of 2026-09-30, all Portuguese: POR names, European portraits) Rastava
RST, Volinovia VLN, Estande ESD (flag `source/flags/ESD.png`, map colour the flag's red (153,0,0): the
green blended with Rouental),
Coraliza CRZ, Placeholdria PLH (theocratic, prophetic rule), and (2026-10-01, east of
Estande, Italian names: Claude's guess) Illiricium ILR (map name "Republican
Illiricium", "Senatorial" until 2026-10-02; flag `ILR.png`), Côtefer CTF, Entroterra ETR, Mezzogiorno MZG (the three
Bleacherist republics, shades of blue, Illiricium's puppets from the start) and
Royalist Illiricium KIL (its island; white on the map so it stands out against the
blue republics, author 2026-10-01; flag `KIL.png`, the author's original with the
transparent gaps filled with the flag's blue; a redraw at 82:52 was rejected;
Rouental guarantees its independence from the start, which replaced a
non-aggression pact), and (2026-10-01, later,
east of Selgrave and Hollier) Kurikia KRK (conservatism, flag `KRK.png`, its navy
as map colour) and Fraxhemark FRX (social democracy, capital Fraternal City; map
colour raspberry because its flag red would vanish next to Hollier; flag
`FRX.png`, the author's own, 2026-10-01). Kurikia also holds the five islands to
its north the author's Names layer labels KU (2026-10-02, four states). Kurikia's culture is Claude's
guess from its flag (SOV names, Europe portraits, eastern European gfx); Fraxhemark is
American (author): USA names, US generals and admirals, Europe politicians (vanilla
has no US generic politicians), western European gfx. Locus LCF (2026-10-02; the
Worker's Republic of Locus Felicitatis; Council Communism; 3 states around
Fraxhemark's lake; colour, culture (American, like Fraxhemark) and the stand-in
flag are Claude's): outlined inside Fraxhemark, so `apply_outlines` seeded it
(`OWNERS` now wins over a re-cut patch's old country) and left the rest of
Fraxhemark alone (`LEAVE`). The unnamed peninsula with the bay east of Fraxhemark is
outlined but left as NSC (`LEAVE`). File names are ASCII (`Cotefer`). Formal names are the
author's; Selto's "Empire of Seito-Hamborn" was read as Selto-Hamborn.
The new three's colours and adjectives are Claude's picks.

## 2026-10-04: south of Estande

2026-10-04, south of Estande (the author's names, governments and formal names;
colours and adjectives Claude's): San Sierra SSA (Council Communism, flag `SSA.png`,
capital Sanhueza, with the SS islands and the archipelago its label points to),
Anglost AGL (Constitutional Monarchy, flag `AGL.png`, with every AN island), Normania
NRM (Constitutional Monarchy, Anglost's dominion: `autonomy_dominion`), Guardana GRD
(Enlightened Absolutism), North Pollana NPL ("the Worker's State of Pollana", Party
Centralism; the north tip of S. Pollana's island), South Pollana SPL (Liberalism) and
Dremaur DRM ("the Pangolin Empire of Dremaur", Absolute Monarchy, flag `DRM.png`).
Cultures (author): SSA GRD Spanish, NPL SPL Latin American (MEX names, vanilla's South
American portraits, `southamerican` gfx), AGL NRM English, DRM Dutch (HOL names). The
land between Anglost and San Sierra is undecided (author) and stays a placeholder.

## 2026-10-04, later: Wersh, Troc, Cascadia, Sicilianzo, Danelaw, Thorian Dynamics

2026-10-04, later (the author's names, governments and formal names; colours Claude's):
in Nonscio's west Wersh WRS (Revanchism, "the Republic of Wersh"), Troc TRC
(Liberalism, flag `TRC.png`) and Cascadia CSC (Anarcho-Communism, "the United
Forests of Cascadia", with every CS island); between Anglost and San Sierra
Sicilianzo SCZ (Constitutional Monarchy, flag `SCZ.png`) and Danelaw DNL ("the
Kingdom of Danelaw-Scandinavia", Elective Monarchy; Sweden's flag drawn as a stand-in
until the author's own, 2026-10-08);
inside Fraxhemark Thorian Dynamics THD (the author's new **Megacorporation**
sub-ideology, flag `THD.png`). Cultures are Claude's guesses: DNL Swedish, SCZ
Italian, CSC and THD American, WRS TRC the continent's (English). The author wrote
"Sicilianzo" and "Danelaw" on Necessary Borders; the letters were moved to Necessary
Names. Capitals: Kurikia Markovograd, Fraxhemark Fraternal City (dots now).
Map colours by the author (2026-10-04, later): Wersh dark blue, Troc red, Cascadia
dark green, Sicilianzo white (an off-white, since Royalist Illiricium is pure white).
Kurikia also holds the island off its east coast at (1409, 925), one state (the
author's Notes layer colours it Kurikian).

## 2026-10-05: the friend's sessions (Merlovich, Hoalepa, south of Solitas)

2026-10-05, **the author's friend's two sessions**, merged from their build and
`.pdn` (no code came with them; our scripts were given the same settings and the
build matched theirs file for file, except image encodings): Aislada became
**Merlovich** ("the Federation of Merlovich", Merlovian, Liberalism: `RULING`, the
character's ideology; its leader is named "PLACEHOLDER" for now, with the author's
portrait `source/portraits/merlovich_leader.png`; Communist Merlovich keeps the emu;
flag `AIS.png`; state names and 17 more cities; more rivers). Its paint stays the
placeholder green (70,170,70); `nations.DISPLAY_COLOUR` shows #2D694F in game.
New nations: Hoalepa HOA (two islands north-west of Solitas; Constitutional
Monarchy; "the Exteriorem Kingdom of Hoalepa"; George Tupou VII the Generous;
capital Nuku'alofa; Australian names, commonwealth gfx) and, south of Solitas,
Arvorenia ARV (Constitutional Monarchy, "the United Kingdom of Éden, Santo Domingo,
and Arovia", Arovian, Portuguese, capital São Francisco), Atrocha ATR (Liberalism,
capital Corales), the United States of Solitas USS (Liberalism, American, capital
Tallahassee; removed 2026-10-13), Silvamar SVM (Liberalism, "the New Republic of Silvamar", Silvestran,
capital Marcanova) and Ponchomagnifico PNC (Strongman Rule, "the Community of
Ponchomagnifico", capital Rosas); ATR SVM PNC Spanish. Leaders' names and portraits
are in `NAMED_LEADERS`. Their flags were taken from the build at 82×52 (the
originals weren't sent). The friend also swapped some of the author's Merlovich
rivers between Major and Minor (author: fine) and split two leftover placeholder
states at Corales along the paint.

## 2026-10-05, later: Araseos' south-west, Rouental's releasables, the Holy See

2026-10-05, later (the author's names, governments, formal names and cultures; colours,
adjectives and the Welsh/Irish name lists' source Claude's): Guardana renamed
**Malvekia** (tag GRD kept); in Araseos' south-west Terrabis-Seran TBS (Social
Democracy, "the Commonwealth of Terrabis-Seran", English, flag `TBS.png`, with the TS
islands), Gaellia GAE (Absolute Monarchy, "the Kingdom of Gaellia", Irish),
Kilkire-Foraois KKB (Elective Monarchy, "the High Kingdom of Kilkire-Foraois",
Irish; the author's message said "Kilkire-Battania" at first) and
Harwick HWK (Party Centralism, "the People's Rule Over Harwick", Welsh, Vineta's
puppet), with Vineta VNT (Party Centralism, "the People's Rule Over Vineta", Welsh,
flag `VNT.png`) on the VI islands off them; the Garfield Republics GFR (Fascism, "the
United Greater Garfield Republics", Spanish, flag `GFR.png`) on the GR islands south
of Malvekia; Devlon DVL (Agrarianism, "the Free State of Devlon", American) on the
28 px islet its label sits on, off Fraxhemark. Thorian got the two islets labelled
TD, Cascadia every islet labelled CS. San Sierra's border with Sicilianzo moved west
(`pdn_tools.py border`): San Sierra took most of Sicilianzo, its state lines
continued into it; the slivers left of Sicilianzo's old states were merged
(`pdn_tools.py merge_small sicilianzo 400`), leaving it 3 states. The tip of
Danelaw's eastern peninsula, cut off by a new line and labelled GR, is Garfield's
(the "GR" was written on Necessary Borders; moved to Necessary Names).
The bit of coast Gaellia's forked west border closes off at (596, 2222) is
**another nation's, later** (author): it stays Araseos (`LEAVE`). Welsh (WLS) and Irish (IRE) names were added to
`source/names/vanilla_names.txt` from vanilla. The peninsula east of Thorian is two
**exclaves**: Terrabis-Seran's (TS, north) and Cardonia's (CA, south) (author).
San Sierra's state lines had two gaps (a pixel at (778, 1263); a line 4 px short of
the coast at (890, 1263–1266)), filled. **Rouental's releasables** (author,
2026-10-05; `nations.RELEASABLE`, cores from the start, owning nothing, so they can
be released by hand; **not** released by the civil war): the Kingdom of Carcarelle
CRL (Carcarelle, Nerié, Hyères), the Duchy of the Mountains MTN (Everlon, Tocsin,
Rolantelle, Rempart), the Oriflamme Alliance ORF (Oriflamme, Glacierre), the Free
State of Ghessone GHS, the Grand Duchy of the Riverraine RVR (Leclerc, Marais
Verte) and the Duchy of the Piscary PSC (Belleplaine-sur-Mer, Baie de Torres,
Graisivaudan); the author's flags, French culture; governments and colours are
Claude's (Absolute Monarchy, Feudalism, Oligarchy, Liberalism, Feudalism,
Feudalism). Royalist Illiricium's ruler is **Beatrice di Alqiro** (`NAMED_LEADERS`,
`source/portraits/beatrice_di_alqiro.png`). New flags for Romanoddle and South
Pollana too. The **Holy See** SEE ("the Kingdom of the Church", Theocratic,
Hierocracy; author, 2026-10-05; tag SEE by the author's choice, VAT at first) holds
San Sierra's island state 1 at (896, 1184), given with `pdn_tools.py give holy_see`;
flag `SEE.png` is the author's ("Kingdom of God" layer of the flag file; it replaced
a stand-in Claude drew); Italian culture and the pale gold colour are Claude's.

## 2026-10-07: the big update (Araseos, Yastreovakia)

**2026-10-07, the big update** (the author's names, governments and formal names;
tags, colours (from the flags where there is one), adjectives and cultures Claude's):
Placeholdros renamed **Placeholdaire**; Placeholdria became **Vultuca** PLH
(Constitutional Monarchy, "the United Kingdom of Vultuca", flag `PLH.png`); Volinovia
is "the Kingdom of Volinovia" (Enlightened Absolutism). New, in Araseos' south and
west: Merlgould MGD (the author's new **Personal Union** sub-ideology; "the Kingdom of
Merlgould" (written "Melgould"); carved out of Vultuca; Volinovia's puppet),
Transcainia TCN (Oligarchy), Peatiktist PTK (Strongman Rule, "the Constitutional
Dictatorship of Peatiktist", with the PE islands and an exclave by Transcainia),
Serentia SRN (Elective Monarchy, "the High Kingdom of Serentia", flag), Leithanien LTH
(Populism, flag; its own state lines: 7 states; cities Rostock, Litzstädt, Thielfurt,
Weißadel, Frundsstadt, Kaltsit, Veisheim), Ostaria OST (Absolute Monarchy, "the
Archcounty of Ostaria", flag), Großlöwenburg GLB (Feudalism, "the Efeuüberwuchterte
Steinsäule of Großlöwenburg", flag), the Kampfian Empire KPF (Absolute Monarchy, "the
Iron Empire of Kampf"), Dumas DUM (Holy Order, "the Order of Saint Dumas"), Terreich
und Preußen TUP (Social Democracy, "the Bundeskaiserreich of Terreich und Preußen",
flag, with the TP islands and the coast patch west of Gaellia), Schteirmark STM
(Feudalism, Terreich's puppet), Daravon DRV, Eschland ESC and Hwitland HWT (Orthodox
Marxism; Daravon leads **the Synthesist Internationale** with the other two,
`faction_template_synthesist_internationale`), Someriania SMR (Vanguardism; SOM is a
vanilla tag); in Yastreovakia: Krionik KRI (the author's new **Stratocracy**
sub-ideology, Democratic; "the Militariat State of the Kriosnika", "Regency" until
2026-10-08; ruled by the **Kriosaivak Council of Marshals**, whose portrait is the
author's round emblem of the council (`source/portraits/kri_council_of_marshals.png`,
centred on a dark field); with every KR island, the two KR islets west of Araseos
and, on its label, a region of Orientalis), Gorbastan GOB and Zukchiva ZUK
(Liberalism), Sminishia SMN (Social Democracy, "the Worker's Republic of Sminishia"),
Russovichia RSV (Council Communism, with the RU islands). The ES islands east of
Terreich are **Estande's**, and the island labelled CA (Cascadia's until then) is
**Cardonia's** (author). Cultures (Claude's guesses):
German for the new Araseos nations, French for Dumas, Portuguese for Merlgould,
Russian for Yastreovakia's. The borders of Sminishia, Gorbastan and Zukchiva were drawn
on Necessary Names, and "PE" and "(TP)" were written on Necessary Borders: moved; a
one-pixel gap south of Ostaria was closed. New flags: Illiricium's two (kingdom and
republic) replaced. Corrections the same day (author): the land north of Peatiktist's
exclave is **Transcainia's** (6 states; an old `LEAVE` pixel had kept it Araseos),
and four placeholder states changed hands with `pdn_tools.py give`: Araseos 3 →
Serentia (452, 1494), Nonscio 7 → Malvekia (1015, 1366), Nonscio 6 → San Sierra
(1006, 1239), Nonscio 3 → Kurikia (1257, 664). Leithanien's capital is Thielfurt.
Krionik's flag `KRI.png` was redrawn from the author's picture (the file didn't come
through) until 2026-10-09, when their flag file's own replaced it; its map colour stays green (the flag's maroon would merge
with Russovichia).

## 2026-10-07, later: five more Rouental releasables

2026-10-07, later: **five more Rouental releasables** (author; same rules as above):
the Alliance of the East AOE (Chirac, Serpette, Maïeul, Moelle; Oligarchy, as when it
was a civil-war country; the civil war still gives those states to Lustiana, Hollier
and Selgrave), the Principality of the Recolt RCL (La Recolt, Fleurastre, Fourier),
the Duchy of Sangterre SGT (Sangterre, Carune la Cœur), the County of Kové KOV and
the County of Hevique HVQ (Hevique, Avarre), and the Duchy of Serie SRE (Serie, Verdoyantes;
Feudalism; charcoal like its flag). Governments, adjectives and colours
Claude's. The author's `New_Mod_Flags.pdn` (490×311, HOI4's 82:52 shape; layers
"Carcaraise", "Marcher Lords", "Rouental (Authoritarian)" etc. are `import_flags`
aliases) replaced 23 flags, including Rouental's four government flags; the
Reibonne's and HMMLA's were copied from the new communist and authoritarian ones.

## 2026-10-08: Belekria, Araseos' far south-west, islets, flags

**2026-10-08** (the author's names, governments and formal names; tags, colours,
adjectives and cultures Claude's unless noted): in Yastreovakia's north **Belekria**
BLK (Vanguardism, "the Union of Belekrian Republics", 44 states, with every BE island:
five off its coast, eleven north of Nonscio, two further east), whose region
**Tethia** is one state (named "Tethia") and a releasable, the Principality of
Tethia TTH (Absolute Monarchy, Polish (author), flag `TTH.png`, colour from it); the
box west of Tethia is one state too (both drawn with state lines). In Araseos' far
south-west **Merigo** MRG (Conservatism, "the Republic of Merigo", Peatiktist's
puppet, Italian), **Zwintern** ZWT (Technocracy, "the State of Zwintern", Dutch) and
**Ungar** UNG ("the Grand Duchy of Ungar"; Feudalism is Claude's: the author named
it later the same day; Hungarian, the author's, 2026-10-09, German at first); **Ostercoirasreich** OCR (Feudalism, "the
Kaiserinnreichfedderation of Ostercoirasreich", German) on the OS islets and
**Mahina** MAH (Liberalism, "the Republic of Mahina", Australian names like Hoalepa)
on the MA islets. Islets also went to Someriania (SO), Kilkire-Foraois (the west of
the SO island, cut off by a line), Kampfian Empire (KE) and Dumas (DU). The author
wrote most of those labels on Necessary Borders: moved to Necessary Names (88 marks;
only three new lines were real). Their upload predated the Transcainia fix and the
four state transfers, so the current game layers were kept. New flags for Hevique,
Riverraine, Vair and Fraxhemark came with the flag file. Later that day (author):
Merigo renamed **Merikaan** ("the Republic of Merikaan", Merikaans; key `merigo`, tag
MRG kept) and Dutch; Mahina **Polynesian**: vanilla has no such culture, so the name
list `PLY` is our own (Hawaiian, Maori, Samoan, Tongan, Tahitian names) in
`source/names/custom_names.txt`, which `cultures.py` reads alongside the vanilla
lists; portraits are South America's generic ones (vanilla has no Pacific ones).
Then (author) Krionik, Sminishia, Gorbastan and Zukchiva became Balkan: vanilla has
several Balkan name lists, so each gets one (copied into `vanilla_names.txt` from
vanilla's `00_names.txt`): Krionik Serbian SER, Sminishia Croatian CRO, Gorbastan
Albanian ALB (the author's pick; Bulgarian first), Zukchiva Macedonian MAC.
Then a new flag file (58 layers): 18 nations got their first flag (Belekria,
Daravon, Dumas, Eschland, Gorbastan, Harwick, Hwitland, the Kampfian Empire (layer
"Kampf Empire", an `import_flags` alias), Kilkire-Foraois, Malvekia, Merikaan,
Peatiktist, Sminishia, Someriania, Transcainia, Ungar, Zukchiva, Zwintern) and
eight were replaced (Danelaw's own for the Swedish stand-in, a new Ostaria, and
Vineta, Romanoddle, Terreich, Großlöwenburg, Serentia and Leithanien redrawn at
82:52). Harwick's empty top row was filled from the row below. Map colours were
not changed to match the new flags.

## 2026-10-09: the Synthesist Internationale redrawn

**2026-10-09** (author): the Synthesist Internationale redrawn. Hwitland is renamed
**Scealand** (HWT and the key `hwitland` kept; "the Republik of Scealand",
Scealändisch) and Eschland **Artzen** (ESC, key `eschland`; "the Wyrhterrepublik of
Artzen", Artzener): the formal names follow the new names, the adjectives are
Claude's. A new line gives Scealand Eschland's land north of it (`pdn_tools.py cede
eschland hwitland 551,1582`: 2 states whole, the north slivers of 2 more joined one
of them, 3 provinces split along the line): Scealand 6 states, Artzen 5. The upload
was the author's previous file plus these edits, so its game layers predated the
2026-10-08 changes; only their own edits were taken (the Necessary Borders and Names
pixels where it differed from that previous file). New flags for Lustiana, Evriches,
Lanzerac (now purple, white and gold) and Hollier. Lanzerac's map colour followed
(author): the flag's own plum purple (145,58,106), since a bluer purple would read as
Cardonia's a few pixels north.

## 2026-10-09, later: Yastreovakia's north-east

**2026-10-09, later** (the author's names, governments and formal names; tags,
colours (Belka's from its flag), adjectives and cultures Claude's, but Volstokn's
Finnish): Yastreovakia's north-east, now all outlined, and two islands off it.
Belka BKA (Fascism, "the Most Serene State of Belka", flag `BKA.png`, black like its
flag's top band; with every BK island), West Sminishia WSM (Vanguardism, "the
Autonomous Region of Western Sminishia", Belekria's puppet; cut out of Sminishia by a
new line: `pdn_tools.py cede sminishia w_sminishia 1919,414`), Sanada SNA (the
author's new **Khanate** sub-ideology, "the United Sanadan Clans", with every SA
island), Kamyachyn KMY (Liberalism), Volstokn VSK (Enlightened Absolutism, "the Tsaral
Realm of Volstokn", with the VO islands), Brethren BRT (Synodal Rule, "the Great
Congregation of Brethren", with the BT island), Ryśny RYS (Agrarianism, "the United
Voivodes of Ryśny"), Pakitsk PKT (Strongman Rule), Kieska KSK (Oligarchy, "the
Confederated Kingdoms of Kieska"), Zoluzeme ZLZ (Absolute Monarchy), Vilna VIL (the
author's new **Radical Republicanism** sub-ideology, Democratic; "the Free Republic of
Vilna"), Sombor SMB (Lordly Republic, "the Free City of Sombor"), Skillia SKL
(Agrarian Socialism; its island south-east of Krionik and the SK islet) and, in
Orientalis, Tenkyoku TKY (Prophetic Rule, "the Remnant of Tenkyoku"; the island its
label sits on, while the peninsula beside it stays Orientalis, `LEAVE`). The islands
labelled ES south-west of Tenkyoku are Estande's (6 states). Cultures: Russian (Belka,
Pakitsk), Croatian (West Sminishia), Buryat (Sanada: vanilla's Mongolian list is 14
Chinese names, and Buryat is Mongolic), Ukrainian (Kamyachyn), German (Brethren),
Polish (Ryśny, Kieska), Latvian (Zoluzeme), Lithuanian (Vilna), Serbian (Sombor), Greek
(Skillia), Japanese (Tenkyoku); UKR, FIN, LAT, LIT, GRE and BYA were copied into
`vanilla_names.txt` from vanilla (its BLR list is part of SOV's, so it was not used).
States: Sanada 84, Volstokn 61, Belka 39, Brethren 20, Kieska 13, Pakitsk 9, Ryśny 8,
Kamyachyn 5, Skillia 4, Vilna 3, Zoluzeme 2, West Sminishia 2, Sombor 1, Tenkyoku 1
(`dist/preview_new_nations_yastreovakia_northeast.png`). Left for the author: the ES
on Orientalis' north coast at (4178, 793) had no line around it (it has since
2026-10-11), and four unlabelled islets off the new coasts stay Yastreovakia's. The same day's
flag file brought Belka's flag and redrawn Artzen and Daravon flags. Its update to
Serie's (four gold anchors in the corners) was missed at first: `import_flags.py`
called a flag unchanged under a mean difference of 3. With the new test, Krionik
also got the author's own flag in place of the redraw, and Garfield, Troc and
Terrabis-Seran the file's 82:52 copies of the same pictures (the old ones were
490×327); Rouental keeps its 1180×700 original. See-through pixels, which show as
holes in game, are now filled on import: Belka's emblem edge, a 1-px frame around
Riverraine's and Belekria's flags, a faint row in Garfield's (and, by hand, the top
row of Ponchomagnifico's, taken from the friend's build).

## 2026-10-09, later still: the Oriental Territories, Peatiktist's isles

2026-10-09, later still (author): **the Oriental Territories** ORT, a new Rouental
releasable (`nations.RELEASABLE`: Concorde et Volonté, Rouental's islets off Solitas, on
the islands north of it since 2026-10-13;
"the Oriental Territories", the author's flag `ORT.png`; Oligarchy, French culture
and the colour are Claude's, a shade off the flag's plum, which is Lanzerac's map
colour exactly). The three isles and three islets the author labelled PE in the
Midtierre, between Anglost and Normania (Nonscio's until then), are Peatiktist's: 3
states, one per isle (`apply_outlines.py`). The flag file brought 20 first flags
(Coraliza, Volinovia, Merlgould, Rastava, North Pollana, Gaellia, Schteirmark, Mahina,
Russovichia, and West Sminishia, Pakitsk, Sanada, Brethren, Ryśny, Sombor, Kamyachyn,
Kieska, Zoluzeme, Vilna, Skillia) and four redrawn ones (Estande, South Pollana,
Dremaur, Sminishia); map colours were not changed to match. Then (author) "Araseos
1", a 19 px islet off Terreich's coast and the Araseos placeholder's last land, went
to Terreich, joining its nearest state (`pdn_tools.py attach terreich 935,1862`), so
ARS is no longer in the mod; and Ungar became Hungarian (HUN names, copied into
`vanilla_names.txt` from vanilla).

## 2026-10-11: Orientalis

**2026-10-11** (the author's names, governments and formal names; tags, colours,
adjectives and cultures Claude's, but Arpino's Indian culture the author's):
**Orientalis outlined**, all but its south-west. Gorduchai GOR (Clerical Monarchism,
"the Holy Kingdom of Gorduchai", the island west of Orientalis), Sarkis SRK
(Revanchism, "the People's State of Sarkis", with the SR islets), Wanea WAN
(Agrarianism), **the Great Lake Republics** (`faction_template_great_lake_republics`):
Qingou QNG (Liberalism, "the Qingou Republics", its leader; **Qinguo**, "the Qinguo
Republics", since 2026-10-13), Xuè XUE (Conservatism;
the accent is the author's), Hulinguo HLG (Populism, "the Hulinguo Republic"), the
Associated Cities ASC ("the Associated Cities of Dahu and Jinhu", Liberalism) and
Haidao HDO ("the Associated City of Haidao", Liberalism); Kuran KRN (Vanguardism, "the
Red Mountains of Kuran"), Red Path RDP (Vanguardism, "the People's Republic of
Kianhua", the three RP patches), Kianhua KNH (Liberalism, "the United States of
Kianhua"; "Kainhua" in the author's message was a typo), Charity CRT (Absolute
Monarchy, "the Empire of Charitia", with the AC islands and the peninsula beside
Tenkyoku, which was in `LEAVE`), Kaizan KZN (Personal Union, Charity's puppet), Sho
SHO (Oligarchy, "the Kingdom of the Sho Dynasty"), Uyizar UYZ and Yatar YTR
(Khanate), Myehn MYH (Conservatism, "the Imperial Republic of Myehn"; with the 49
islands the author circled in red east of it, and an exclave on Plaija's west tip
its label sits on), Tsuruma TSU (Lordly Republic, "the Most Serene Republic of
Tsuruma", with the TS islands; the one far south of Arpino is Terrabis-Seran's since
2026-10-12: TS is its code too), Daihai DHI
(Feudalism, "the Island Principalities of Daihai", the DI islets), Plaija PLJ
(Orthodox Marxism), Pinzahao PZH (Radical Republicanism, "the Liberated Peoples of
Pinzahao"), Ganden GND (Fascism) and Arpino ARP (Enlightened Absolutism, "the United
Empire of Arpino", with the AR islands). Three bits of other countries: TP in
Kianhua (Terreich's), KR at the tip of Arpino's south (Krionik's) and the ES cape on
the north coast (Estande's, now outlined). Then (author) **Shinnokawa** SHN ("the
Empire of Shinnokawa", Absolute Monarchy): the six SH islets east of the circle, one
state. The unlabelled land (the south-west's big island and peninsula, the islands
between Krionik's and Plaija, about 125,000 px) stays Orientalis for now: the author
will fill it later. Cultures: our own Chinese list `CHN` (family name first;
vanilla's is family names only) for QNG XUE HLG ASC HDO KRN RDP KNH CRT DHI PZH;
Japanese for TSU KZN SHO SHN (Sho after Ryukyu's Shō dynasty), Korean WAN, Buryat GOR (a
lamaist Mongol monarchy, like the Bogd Khanate), Armenian SRK, Uzbek UYZ, Kazakh YTR,
Burmese MYH, our own Vietnamese `VNM` for PLJ (family name first too), our own
Tibetan `TBT` for GND, and Indian ARP (vanilla's Raj names and portraits, commonwealth
gfx); KOR ARM UZB KAZ BRM RAJ were copied into `vanilla_names.txt` from vanilla, and
its Buryat list's one name in curly quotes was given straight ones (Gorduchai's
leader showed them). The members of the Great Lake Republics and of
the Synthesist Internationale start with 40 % for their (and their leader's) ideology
(`nations.POPULARITIES`), a precaution after Lanzerac and Guedelon. States: Sarkis 198,
Arpino 109, Plaija 65, Myehn 63, Charity 56, Kianhua 53, Qingou 24, Uyizar 16, Sho 13,
Xuè 12, Yatar 7, Gorduchai, Ganden, Pinzahao, Red Path and Tsuruma 6 each, Wanea 5,
Kaizan 4, Hulinguo 3, Kuran 2, the Associated Cities, Haidao, Daihai and Shinnokawa 1
each, and one each for Terreich, Krionik and Estande: 667 in all
(`dist/preview_new_nations_orientalis.png`). Wanea's line carves a tongue of land
south-east of it out to Sarkis, as drawn. The upload predated Araseos 1's move to
Terreich, so `pdn_tools.py attach` was run again.

## 2026-10-12: Usnistan, Orientalis' south-west, Sennheiser

**2026-10-12** (the author's names, governments and formal names; tags, colours,
adjectives and cultures Claude's): **Usnistan outlined**, Orientalis' south-west and
Sennheiser. In Usnistan: the Cultists CUL (Prophetic Rule, "the Cult of the Great
Cthulu", the CU archipelago), Arcadia ARC (Conservatism, Terreich's puppet), Muqadasa
Salamat MQS (the author's new **Divine Republicanism**, Theocratic; "the Holy
Republic of Muqadasa Salamat"), Sarza SRZ (Absolute Monarchy, "the Empire of Sarza"),
Leviathan LEV (Populism), Kyras KYS (Liberalism, "the Commonwealth of Kyras", with the
RA islands and a coastal exclave by Almohavid), Hulya HLY (Conservatism, "the
Territory of Hulya", a 148 px box), Levantinin LVN (Holy Order, "the Crusader State of
Levantinin"), Mustawi MST (Strongman Rule), Almohavid AMH (Constitutional Monarchy),
Port Almohavid PAM (Lordly Republic, "the Free Port of Almohavid": the 16 px tip of
land a short line closes off), Mekele MKL (Anarcho-Communism, "the Mekele Peoples'
State"), Kalaistan KLS (Military Junta), Al-Radiyaa RDY (Conservatism), Al-Khabid KHB
(Oligarchy), the Humanist State HMN (the author's new **Humanism**, Authoritarian: "an
apartheid-style ideology placing humans as superior beings to the other races of
Valsora"), South Usnistan SUS (Conservatism), Royabad RYB and Koronista KRS (Absolute
Monarchy, sultanates), North Koronista NKR (Strongman Rule; "North Kornista" on the
map), Zanzimibia ZNZ (Social Democracy), the Utopian Republic UTP (Lordly Republic,
"the Second Utopian Republic"), Soloriania SLN (Liberalism, "the Solorianois
Confederacy"), Hohenzburg HZB (Strongman Rule, the Kampfian Empire's puppet), Nuevo
Paraíso NPR (Conservatism, the United States of Solitas' dominion), Arklen ARK
(Conservatism, "the Arklen Free State", a non-aggression pact with Ostaria), Isigoriya
ISG (Military Junta), Kizimwe KZW (Synodal Rule, "the Kizimwe Conference of Bishops"),
Lafari LFR (Council Communism, "the Worker's Republic of the Lafari"), Meddacah MDC
(Fascism, "the Meddacah River Autonomous Zone"), Khaleeya KHY (Feudalism) and Solaria
SLA (Hierocracy, "the Holy State of Solaria": on the map but not in the author's
list; named when asked); in Orientalis' south-west Chineasia CNA (Vanguardism, "the
People's Republic of Chineasia", with the CH islands as far as Krionik's island; led
by the author's **Han Leji**, `source/portraits/han_leji.png`; flag `CNA.png`) and
Felter FLT (Liberalism, with the FE islands); Sennheiser SNH (Constitutional Monarchy,
"the Sennheiser Union", labelled AK) in Yastreovakia's south-west, a `LEAVE` patch
until then. The author's "direct colonies": islets and bits of coast labelled US (the
United States of Solitas, 3 states), KR (Krionik, 3), KE (the Kampfian Empire, 1), SR
(Sarkis, 2) and KF (Kilkire-Foraois, Claude's reading, 1 islet); the islet the author
circled near Myehn's red circle joined Myehn's nearest state (`pdn_tools.py attach`).
Cultures: the continent's Persian for Kyras (Kyros is Cyrus), Sarza, Royabad,
Kalaistan, South Usnistan, the Cultists and the Humanist State; Arabic for Muqadasa
Salamat, Al-Khabid and Khaleeya (SAU names) and Mustawi, Al-Radiyaa and Meddacah
(KUW), Moroccan for both Almohavids, Turkish for Hulya and both Koronistas, Ethiopian
for Mekele and Lafari, Eritrean for Kizimwe, Nigerian for Zanzimibia, Ghanaian for
Isigoriya (with the `arabia` and `africa` portraits, the two halves of the continent's
mixed set), Greek for Arcadia, English for Leviathan and the Utopian Republic (Hobbes,
More), French for Levantinin and Soloriania, German for Hohenzburg and Sennheiser,
Dutch for Arklen (the Orange Free State) and Felter, Latin American for Nuevo
Paraíso, Italian for Solaria, Chinese for Chineasia. SAU KUW MOR TUR ETH ERI NGA GAH
were copied into `vanilla_names.txt` from vanilla; their heads of state and a few
other famous names are in `NOT_SURNAMES` (none of them was in a list already in use,
so no older leader changed). States: Chineasia 73, the Utopian Republic 68, Kyras and
Sarza 33 each, Royabad 31, Felter and Lafari 29 each, the Humanist State 23,
Sennheiser 22, the Cultists 21, Muqadasa Salamat and South Usnistan 19 each, North
Koronista 18, Arcadia 17, Levantinin 12, Mustawi 11, Almohavid and Zanzimibia 9 each,
Al-Khabid, Hohenzburg and Nuevo Paraíso 8 each, Al-Radiyaa 6, Soloriania 4,
Isigoriya, Kalaistan, Kizimwe, Koronista, Meddacah and Solaria 3 each, Arklen, Hulya,
Khaleeya, Leviathan, Mekele and Port Almohavid 1 each: 545 with the colonies'
(`dist/preview_new_nations_usnistan.png`, `..._orientalis_southwest.png`,
`..._sennheiser.png`). Left as placeholders: about 1,700 px of Usnistan islets (most
of it the three islands south of it), 300 px of islets off Orientalis and 350 px in
Yastreovakia. The CU and RA labels were drawn on Necessary Borders: moved to
Necessary Names. Then (author) ten placeholder states changed hands, named as the game
showed them: Nonscio 1 (2,696 px, the island group south of the BE islets) to
Belekria, Orientalis 4 to Ostercoirasreich, Tsuruma 6 (the TS island far south of
Arpino) to Terrabis-Seran, Yastreovakia 1 to Sarkis and Yastreovakia 3 to Volstokn,
as states of their own (`pdn_tools.py give`); the islets Usnistan 2, Nonscio 2,
Orientalis 3, Yastreovakia 2 and 4 (17-52 px, beside the Cultists', Cascadia's,
Charity's, Volstokn's and Sennheiser's land) joined their new owner's nearest state
(`attach`). Nonscio and Yastreovakia own nothing now. Left as placeholders: Usnistan
1-4 (islets beside Kyras and the Utopian Republic, and the islands south of South
Usnistan; the old Usnistan 3-5, renumbered), Orientalis 1-2 (beside Kianhua and Daihai)
and Solitas 1-20, the land between the friend's nations. Flags for Sennheiser and
Volstokn came the same day (`SNH.png`, `VSK.png`; map colours unchanged).

## 2026-10-13: Solitas

**2026-10-13** (the author's names, governments, formal names and rulers; tags,
adjectives, cultures and colours (from the flags where there is one) Claude's):
**Solitas outlined.** The upload was the 4a191cb map (after Usnistan, before the ten
transfers and the province merge) plus the author's edits, so only those were taken:
Necessary Borders, Names and Cities (Tallahassee's dot removed), Even More Reference
and a new layer, **Islands to Add**. **The United States of Solitas is removed**
("eventually it will be readded as a formable": it stays in `COUNTRIES`, owning
nothing, so it is left out of the mod); its colonies, relabelled AN (six pieces, three
states), are Anglost's (`pdn_tools.py give`), and **Nuevo Paraíso is New Paradise**
("the Dominion of New Paradise", now Anglost's dominion and English; key
`nuevo_paraiso` kept). Its land on Solitas was repainted as the placeholder's before
`apply_outlines.py`, so the new nations were cut afresh. New: Recaxa REC (Agrarianism,
"the Republic of Recaxa", Diana Zorreguieta, flag), Surredia SRD (Strongman Rule, "the
Republic of Surredia", Sunny Hurricane, flag), Arovannea AVN (Conservatism, "the
Confederative Republics of Arovannea", Estúr Illger fön Reegen; code CI, so many
pieces), Avesária AVE (the author's new **Semi-Constitutional Monarchy**, "the
Avesária Dimokratía", Nikosanis Coisan II; "Aversaria" in the author's message, the
map says Avesária), Abalón ABL (Absolute Monarchy, "the Kingdom of Abalón"), Texaria
TEX (Liberalism, "the Republic of Texaria", Iyun' Savon, flag), Gran Yucanoa GYC
(Liberalism, "the Federation of Gran Yucanoa", ruled by the General Cortes, its
parliament, flag), Las Anod LAN (Conservatism, "the United Isle of Las Anod", Michael
Ryan) and Bromé BRO (Party Centralism, "the Republic of Bromé", Jose Castañeda); the
AV patches are Arvorenia's. **Santa Fe**, labelled but not in the author's list, stayed
the placeholder (`LEAVE`) until that evening. Cultures: Latin American for Recaxa, Gran Yucanoa and Bromé,
American Surredia, German Arovannea, Greek Avesária, Spanish Abalón, Russian Texaria
(Iyun' is June), Irish Las Anod. States: Arovannea 26, Surredia 19, Recaxa 16, Gran
Yucanoa 13, Avesária 6, Abalón 5, Texaria 5, Las Anod 5, Arvorenia 2, Bromé 1
(`dist/preview_new_nations_solitas.png`). Fixes on the way: Texaria's eastern line
stopped 8 px short of the inlet south of it (closed), a "CI" was written on Necessary
Borders (moved to Names), and five slivers of a small loop of line by Abalón's coast
are Abalón's. **Rouental's eastern territories moved** (author, "to better align with
the lore"): the two islands painted on Islands to Add (27 and 45 px, north of
Arovannea) are land now (`pdn_tools.py add_land rouental`), one state named Concorde et
Volonté, so the Oriental Territories' cores follow; the old islets off Solitas' south
are Solitas' again, and their ROU label moved to the islands. The four flags were
fitted to 82:52 without stretching (scaled evenly, then plain field added inside the
stripes, or Surredia's plain sides trimmed; `dist/flags_new_20261013.png`), and added
to the author's flag file as layers (`source/New_Mod_Flags.pdn`, now kept in the repo;
`writepdn.py` adds layers on top).

## 2026-10-13, later: Santa Fe, the last placeholder states

**2026-10-13, later** (the author's names, governments and transfers; tag, colours,
adjective and culture Claude's): **Santa Fe** SFE ("the Fifth Republic of Santa Fe",
Party Centralism, Latin American, gold to stand out from Bromé's crimson and
Atrocha's red; its patch, "Solitas 3" and "4" in game, cut by `apply_outlines.py` into
7 states like its neighbours); **Bromé** is "the Grand Duchy of Bromé", a
Semi-Constitutional Monarchy (Party Centralism until then; Jose Castañeda still rules,
the author named no other); **Silvamar**'s map colour is its flag's navy, a little
lighter (10, 30, 140): its green was too close to Arvorenia's and Las Anod's. The
placeholder states the author named in game went to their neighbours: Solitas 1 (298
px) to Hoalepa and Usnistan 3 and 4 (214 and 1,432 px) to Royabad as states of their
own (`pdn_tools.py give`); Solitas 5 (the two old Rouental islets, 90 px) to Atrocha,
Orientalis 1 and 2 (38 and 95 px) to Kianhua and Daihai, and Usnistan 1 and 2 (31 and
17 px) to Kyras and the Utopian Republic, each joining its new owner's nearest state
(`attach`). Orientalis and Usnistan own nothing now. The last placeholder land,
Solitas 2, a 16 px islet off Recaxa's west coast at (1443, 1832), joined Recaxa's
nearest state afterwards (author), so Solitas is left out too
(`dist/preview_new_nations_solitas.png`). Then (author) **Qingou is renamed Qinguo**
(tag QNG and key `qingou` kept); five first flags, for Qinguo, Kianhua, Tsuruma, Myehn
and Ganden (fitted to 82:52 as below, and added to the flag file); Tsuruma's ruler is
**Akihiro Tanaka** and its capital **Kishito**, Myehn's capital **Shukumei**
(`CITY_NAMES`). Map colours were not changed to match the new flags.

## 2026-10-14: Cardonia's flag

**2026-10-14**: Cardonia's first flag (the author's: black, white and navy bands, an
owl on a compass star), fitted to 82:52 by trimming 9 px of plain band at each side
and added to the flag file (`dist/flag_cardonia_20261014.png`); its map colour stays
deep purple.

## 2026-10-15: Vilna and Placeholdgrad

**2026-10-15** (author): **Vilna moved** to Russovichia's land (its 2 states, with the RU islands), taking
its paint (140, 0, 0), dark red like Vilna's new flag (the author's: a crimson field framed by blue bars and
Stars of David, a menorah over a sword, a line in Hebrew), which came at 1280 × 841 and was fitted to 82:52
by lengthening the top and bottom bars 23 px at each end (`dist/flag_vilna_20261015.png`; in the flag file
as "Vilna", the old layer renamed "Placeholdgrad"). It keeps its formal name; then (author, the same day) it
is **Conservatism** (Radical Republicanism until then) and **Jewish**: the base game has no Jewish culture, so
its nearest, the Israeli name list (ISR, copied into `vanilla_names.txt`; it has some Arab-Israeli surnames),
with Europe portraits and eastern European gfx (Lithuanian until then). **Russovichia stays in `COUNTRIES`,
off the map** (author: "should remain in the code,
but be off the map for now"): it owns nothing, so it is left out of the mod like the United States of
Solitas, with an unused colour from its flag, (153, 47, 45). Vilna's old land (3 states) is
**Placeholdgrad** PHG, with Vilna's old flag (`PHG.png`) and Radical Republicanism, and Vilna's old green;
the adjective Placeholdgradian, Russian culture (for the "-grad") and no formal name yet are Claude's.
Since the paint moved with the names, the `.pdn` is unchanged.

## 2026-10-15, later: the Bleacherist republics' flags

**2026-10-15** (author): the first flags of **Côtefer** CTF (a yellow field, a diamond of blue, crimson, white,
black and orange bands at the hoist's top with four white flowers), **Entroterra** ETR (black, white and blue
bands, three white flowers on the white) and **Mezzogiorno** MZG (black, white and blue vertical bands, a white
flower at the hoist's top). They came as screenshots, each with a 3 px frame (cut off) and wider than 82:52,
fitted by Claude without stretching: Côtefer's plain yellow fly trimmed (1124 × 713), Entroterra's bands each made
taller with plain rows to three equal bands, the flowers centred in the white (1218 × 772), Mezzogiorno's bands
lengthened at the foot so they keep their widths and the flower its place (1252 × 794)
(`dist/flags_new_20261015.png`). Their map colours stay the three shades of blue.

## 2026-10-17: Yastreovakia redrawn, Belekria's republics, Krionik's principalities

**2026-10-17** (the author's map, names, governments and transfers; tags, adjectives, colours, cultures, formal names
of the new releasables and their governments Claude's). **Borders moved** (Necessary Borders): **Belekria** expanded
south, over Sminishia's north (5 states) and West Sminishia's old land (its "Claimed by Sminishia" note); **West
Sminishia** took Sminishia's west end (6 states, where its label moved); **Pakitsk is part of Belka** but stays
releasable (its 8 states, which the author drew, are Belka's; the erased Belka–Pakitsk line was kept as a state line
so Pakitsk's states stay its own); **Krionik shrank**: a strip north of the new line went to Belka (2,845 px) and a
piece east of it to Kieska (6,844 px, split along the line, `pdn_tools.py cede`). A bump of that piece by Sombor
(about 950 px at (2623, 603)) is on Kieska's side of the new line but painted as Crvenognjište: Kieska owns it and
Crvenognjište has a core on it (for the author to confirm). **Sminishia** has cores on its old land (the 11 states
Belekria and West Sminishia took: `nations.CORES`). **States drawn** (Necessary States): Belekria (68 states),
Krionik (132), Terreich (71), Kurikia (56), San Sierra (48), Sennheiser (16; not in the author's message, but its
lines were drawn), Gorbastan (14), Zukchiva (12), Sminishia (9), Pakitsk (8), West Sminishia (6), Hollier (3: north,
south and a small loop) and small edits in Cardonia and Placeholdaire; numbered for naming in
`dist/state_numbers_belekria.png` (with the Sminishias), `_krionik`, `_terreich`, `_kurikia`, `_san_sierra`,
`_sennheiser` and `_gorbastan_zukchiva`. **Provinces drawn** for the first time (Necessary Provinces): Seigne's two run
north and south now, and Royalist Illiricium's two island states have two each. **Two islands** the drawing had joined
to the coast by a neck ("Should be an island!") are islands again (`pdn_tools.py channel`). **Cities**: Bijelkop and
South Bijelkop (West Sminishia), Visokagorod (Zastava), Sedišta (Mylostrva) and **Vazgorod, Krionik's capital**
(Crvenognjište).

**Governments** ("so there are four great powers (those three + Fraxhemark), one for each ideology"): **Krionik** is
Monarchist, "**the Royal Confederation of the Kriosnika**" ("Confederate Kingdoms of the Kriosnika" in the first
message, corrected), still led by the Kriosaivak Council of Marshals, under the author's new sub-ideology **Regency
Council** (the description Claude's); **the Kampfian Empire** is Authoritarian, **Fascism** (Absolute Monarchy
before; still "the Iron Empire of Kampf"); **Sarkis** is Communist, **Vanguardism** (Revanchism before). Their rulers
keep their names (Max Reimer, Vahe Babaian). **Sombor is Krionik's protectorate**: the base game's protectorate is
Japan's alone, so the mod has its own level, Protectorate (`autonomy_valsora_protectorate`: freer than a puppet, half
its manpower and trade to the protector; Claude's numbers). Kampf's puppet Hohenzburg would have been refused under
an Authoritarian overlord (the base game allows no puppet of a fascist one with Death or Dishonor; Illiricium's three
had the same problem since 2026-10-01): the mod ships the puppet level without that clause.

**Releasables painted on the new Subregions layer** (names on Subnames; each with cores on the states mostly painted
in its colour, capital at the pixel in `nations.SUBREGIONS`): **Belekria's nine republics**, Drakonogolovnik DRK,
Staraya Belekria STB, Sredneestvo SDE, Severntochka SVT, Serayachasy SRY, Kalnsfereta KLF, Belayosen BLY and
Krasnoeporte KSP (new, each "the Socialist Republic of …", Vanguardism like Belekria, Russian culture, stripes in
colours of Claude's until they have flags), and Tethia (its land the whole subregion now, 8 states, not one); 5 of
Belekria's states, the strip from Sminishia, are in none. **Krionik's three principalities** (the author: "Flags are
for Krionik's constituent principalities. More will be defined as I map out the other realms"): **Zastava** ZST
(35 states, capital Visokagorod, flag blue, white and black with a crowned eagle, map colour its blue),
**Crvenognjište** CRV (51, capital Vazgorod, flag dark teal with a white sun and band, map colour its teal, lighter:
Krionik's own green is close), **Mylostrva** MYL (43, capital Sedišta, flag blue and gold with the royal arms, map
colour its gold: its navy would merge with Sennheiser's blue), each "the Principality of …", Absolute Monarchy,
Serbian like Krionik; 4 of Krionik's states are in none yet. Their rulers are generated from the base game's name
lists (Drakonogolovnik's drew Dzhugashvili, Skobelev, Brezhnev and Nikulin before Makary Pustobriko, and
Sredneestvo's Aleksandr Ostrovsky: those surnames are drawn again, `cultures.DRAW_AGAIN`). **Later that night** (the author: "Tethia and Kalnsfereta shouldn't be core provinces of Belekria"): Belekria owns
Tethia's 8 states and Kalnsfereta's 6 without a core of its own (`nations.NO_OWNER_CORE`). The flags came wider than 82:52: Crvenognjište's stripes
made taller, Zastava's and Mylostrva's plain ends shortened (Mylostrva's 1 px frame, an export edge, cut off;
`fit_flag.py` refused it, its mantle reaching the top, so by hand). And **Pakitsk** PKT, Belka's.
`dist/preview_yastreovakia_20261017.png` shows the countries and the releasables.

## 2026-10-18: the Gazetteer's first big import, more provinces, the tundra

**2026-10-18** (the author: "a number of changes have been made on the Gazetteer. Please add them to the mod, I want to
see how you handle a significant number of changes at once"; the export the author saved that morning, 21 nations with a
password, 17 with something entered). What each page brought, as the build takes it (`gazetteer.py status`): **Rouental**
its states' populations, 133 provinces' terrain, 29 cities, a river, its people (James Navy the admiral); **Terreich**
its states' names and kinds (Berlinhafen its capital), 323 provinces, cities, a party leader (Eduard von
Hohenzollern-Wolfstark, Semi-Constitutional Monarchy) and Agrarian Socialism for its communists; **Ungar** its five
governments' names (the Grand Duchy of Ungar; the Peasant's Republic, the Republic of the Ungarians, the Ungar Free
State, the Ungarian Synod), their party leaders with portraits, a flag for each of them (`UNG_<ideology>.png`) and its
colour; **Port Almohavid** (PAM) its ruler Usamah Lakhdar with a portrait and its flag; **Merlovich** "The Federation of
Merlovich" and 31 cities; **Krionik** a releasable of its own, **Formosa** FOM ("the Federal Republic of Formosa",
Stratocracy, Elena Andronikos, its one state at (4175, 1518)), and leaders for its three principalities; **Evriches,
Hollier, Lustiana, Lazacia, Seigne, Saint-Gervais** states, provinces and cities; Kurikia a city. Formosa's flag (a
dragon with a caption, 640 x 347) was fitted by hand, then (the author: "just keep the dragon on a yellow background
with the red outline, no text and no extra outlines") the dragon alone on the field's yellow with its red outline.
The culture requests (Merlovich Australian, Ungar Hungarian) were already so.

**The suggestions** on the map, 15 (`apply_suggestions.py`, each by its label): **Rouental** "Split Leclerc in Two"
(north Bicêtre, south Callentroix) and "Split Kove in Two" (west Temerre, east Kové); Riverraine (RVR) is released with
Callentroix, Bicêtre and Marais Verte, Kové (KOV) with Kové and Temerre, the first its capital (Claude's reading; the
releasables were named for the old states). **North Pollana** an islet of its own ("It can stay part of the same state,
but it's an island") and its state in two provinces. **Terreich** Reuenland-Thuringen one state; the Triftsund-Inseln
and Teuton's isles merged "very sparse", in states of two (the author: "with the isles that Terreich wanted combined, put
them into groups of two": Triftsund-Inseln is two states of that name, Teuton one), each isle a province; Rosenburg and
Terreichstadt new states round their cities. **Ungar** six states drawn on the page: Tópart (31 px), Erődítmény (63),
Megkoronázott (806), Menedék (1,791), Aranylómezők (1,530) and Szünet (1,100).

**Later that day** (the author's messages): **Sminishia** claims Belekria 64 and all of West Sminishia ("Sminishia should
also start with claims on Belekria 64 and all of western sminishia": `nations.CLAIMS`, the mod's first claims; West
Sminishia's six were already its cores), and then **Belekria 64 is West Sminishia's** ("Also, give West Sminishia
Belekria 64"; the claim stays, on West Sminishia's land). **Vilna 2 is two islands** ("Vilna 2 should be 2 islands": a neck of land at (1980, 605) joined two of its islets; `pdn_tools.py channel`). **No strait crossings** join Royalist and Republican Illiricium
or reach North Pollana (three dropped: `straits.NEVER`, `NEVER_ANY`). **Belekria 1, 4, 5, 6 and 15 are tundra** ("and
thus don't need high counts"): their 84 provinces are 27 now, ~600 px each, and the borders freed went to provinces
elsewhere. **More provinces** everywhere else (the author: "a general increase of the province count. For example,
Evriches should have at least 3 or 4 provinces"): every nation at least four where its land allows (Evriches, South
Pollana and Haidao 2 → 4, the Holy See 2 → 3, Bromé, Khaleeya and Sombor 3 → 4), every state of 240 px at least two, then
the largest provinces cut, up to 2,000 borders short of HOI4's limit; what the author drew (Royalist Illiricium's and
Seigne's provinces), Terreich's sparse isles and Merlovich are as they were.

## 2026-10-18, night: Usnistan's deserts and states

**2026-10-18, night** (the author's upload "HOI4_Mod_Map_10-18_1": "I've tried to mark out the regions that are desert /
impassible desert in Usnistan. Red is impassible desert, yellow is regular desert. I also adjusted some state and
province borders in Rouental and in Terreich, and added some rivers"). The lines that bound the desert areas are on
Necessary States, so they are the states of the nine nations they divide: **North Koronista** 9 states, **Levantinin**
8, **Mustawi** 12, **Almohavid** 10, **Al-Khabid** 5, **Al-Radiyaa** 4, **Koronista** 6, **Kalaistan** 2, **Solaria** 4
(`dist/state_numbers_usnistan_deserts.png`, numbered 1 to 60 for naming; until then "Country N"). 22 of them, mostly red,
are impassable, each tied to a passable state of its nation; the marked land is desert terrain. The **Humanist State**,
which a corner of the lines runs into, keeps its 23 states. Their map tools on the Gazetteer stay closed until the
author says (`gazetteer.finals`). **Rouental** and **Terreich**: their new state and province lines (Rouental 57
states, `dist/state_names_rouental.png`; Terreich 68, `dist/state_names_terreich.png`).

## 2026-10-19: Krionik's realms, Xugang, the Gazetteer's second big import

**2026-10-19** (the author's map upload "HOI4_Mod_Map_10-18-3" and the Gazetteer export of that morning: "Terrain,
leaders, flags, and more in Usnistan. Some provinces in Rouental. Some fixing of strategic regions"). **New
releasables from the Subregions layer** (names on Subnames, the author's; tags, adjectives, map colours, governments
and formal names Claude's guesses, for the author to change): inside Krionik and its principalities, **Belska** BLS (4
states), **Koroletz** KRZ (8), **Targoviste** TGV (3), **Kosavichy** KSV (7) and **Lagrád** LGR (6, the islands that
were Mylostrva's), each "the Principality of …", Absolute Monarchy, Serbian like Krionik; **Sangrád** SGD, the city
painted in its own colour where Zastava's capital was (a state of 70 px of its own now; Zastava's capital moved to the
middle of its land), and Krionik's three overseas ports, **Port Nyasha** PNY, **Port Vostok** PVS and **Port Grazda**
PGZ (one state each, the names its Gazetteer page gives them), each "the Free City of …", Oligarchy; and in
Sennheiser, **the Sisterhood** SIS (6 states), a Holy Order, Sennheiser's culture. Their colours come from the paint,
softened; each flies a stripe until it has a flag. **Xugang** XUG (the author: "Xugang should start out as a vassal
of Terreich"): Terreich's exclave on the eastern continent, the state its page names Xugang, is its own nation, "the
Territory of Xugang", Terreich's puppet as Stormarn and Arcadia are, Social Democracy as Terreich, the Qinguo lands'
culture (Claude's guesses). **Formosa** (Krionik's page's releasable) has cores on all eleven states the author's lines
cut New Formosa into (it was one state when the page picked it), and its flag (640 x 347) fitted by hand to 640 x 406,
plain rows of its yellow field added above and below the dragon. **The Cultists**: their new state lines (23 states,
`dist/state_numbers_cultists.png`), the striped area impassable jungle (the author: "my idea with the red and green
striped region of the Cultist territory is that it is impassible jungle"). **Ostaria**: the five states its page drew
and named (Hügelsanfte, Weizenfelder, Westmarsch, Silberkrone, Blauküste; Silberkrone "Ostaria's capital city", made
its capital). From the Gazetteer besides: Terreich's 71 states, 552 provinces' terrain, 8 cities and 35 rivers;
Levantinin, Mustawi, North Koronista, Al-Radiyaa and Port Almohavid their states, provinces, cities, people and flags
(the four flags in HOI4's shape into `source/flags/`).

**2026-10-19, later** (the author: "with the releasables in Krionik, each state should only belong to one of the
releasables. Currently you have it so that the new releasables share territory with the old ones"): Crvenognjište's
list of states on Krionik's Gazetteer page (50, saved when its ruler was set, before Belska, Koroletz, Targoviste and
Kosavichy were painted over part of it) had given it 17 of their states too; a state painted for one nation of the
Subregions layer is now that nation's alone (`build_mod.py`), so Crvenognjište holds 33, each realm only its own.
Almohavid (the author: "Almohavid 2 & 3 are combined, and Almohavid 10 is just desert rather than impassible desert"):
its 2 and 3 one impassable state, its 10 (now named Almohavid 9) passable desert.

## 2026-10-20: Rouental's fief map (a trial, not in the mod)

The author sent `Rouental_Map_TEMP_2.pdn` (8000 x 4471, 28 layers: PROVINCE Colors / Borders / Names are the fiefs,
Fief Markers the crownlands, Rough Governorates and Governorate Lines / Names the governorates, with Cities, Rivers,
Mountains, Cultures, River Basins, Conquests and a Flag Map; "Map Example" is a style reference) and asked how it would
split into states for the most granularity. Not applied: the author's new main map comes first (Rouental's internal
borders "redone almost entirely").
- **The lore** (author, 2026-10-20): the red Fief Markers are **crownlands**, "the areas currently under the direct
  control of the Sacred Prince rather than a vassal, or ceded out to a family member as an appanage". The
  **governorates** "were a failed attempt at centralization": appointed governors became "mostly powerless
  figureheads while the regional parliaments took control and ended up as just another barrier against the Prince's
  authority", except **Couronneterre**, "a group of vassals extremely loyal to and under the direct control of the
  Prince" (the central governorate).
- **The fit**: the file's Rouental is the game's at 25.84 file px to a game px (game x = 574.3 + file x / 25.84, game
  y = 746.3 + file y / 25.84; 93 % overlap with the game's outline). Its 404 fiefs average ~50 game px, half under 17,
  191 under a province's 16 px minimum; 9 are crownlands (1,182 game px), 37 lie in Couronneterre, 25 rough
  governorate areas in all.
- **The trial** (each fief a state, a smaller one merged into the neighbour it shares the most border with, crownland
  only with crownland, within its governorate; provinces of ~140 px inside; borders counted on today's map): states of
  at least 16 px, 225 states and 270 provinces (+440 borders); 30 px, 176 and 222 (+297); 50 px, 137 and 186 (+188;
  41 of them a single fief, the others 2 to 13; the crownlands 6 states of their own). Rouental today: 58 states, 129
  provinces. The fief lines would be read from the file itself, the game map keeping Rouental's outline; merged
  fiefs' names as victory points.
