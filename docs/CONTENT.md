# Nation content, ideologies, cultures and superevents

Moved out of `CLAUDE.md` word for word on 2026-10-17 (`CLAUDE.md` keeps a summary). Read this before changing `nations.py`, `ideologies.py`, `cultures.py`, `superevents.py` or a nation's content.

## Nation content (`nations.py`)

Aislada is the worked example of a built-out nation:
- **Leader.** The Great Merlovich (`AIS_merlovich`; "Merlovich" until 2026-10-04) is defined in `common/characters/AIS.txt` as a
  neutrality (`despotism`) country leader and recruited from the country history.
- **Portrait.** Referenced as a sprite (`GFX_portrait_AIS_merlovich`, declared in
  `interface/valsora_portraits.gfx`), the way vanilla does it. The image is a 156×210 DDS
  cropped from `source/merlovich_emu.png`.
- **Focus tree.** `common/national_focus/aislada.txt` is picked for AIS by
  `country = { factor = 0 modifier = { add = 10 tag = AIS } }`. It is one chain:
  1. NationStates account: +25 political power.
  2. Become Cartographer: −0.5 stability.
  3. Fucking Explode: capital state −100 manpower, communism 100%, ruling party
     communism, then `promote_character = AIS_communist_merlovich` ("Communist
     Merlovich", `marxism`, same portrait washed red by `nations.redden`) and retire
     the original.
     **`recruit_character` is ignored outside history files** (error.log: "should only
     happen in game/history files"), so both Merlovichs are recruited in the country
     history; the communist one sits as communist party leader until the focus.
- **Icons.** Vanilla icons only, checked against vanilla `interface/goals.gfx`.
- **Portraits** live in `source/portraits/` and are registered in `nations.PORTRAITS`
  (source, crop box, optional red tint). Each becomes `gfx/leaders/VAL/<name>.dds` and a
  `GFX_portrait_<name>` sprite. Transparent pixels, and a crop box reaching past the
  picture (to fit a round emblem), show `nations.PORTRAIT_BG` (dark charcoal).
- **City names**: `nations.CITY_NAMES` overrides victory point names, keyed by
  `"capital:TAG"` (e.g. Rouental's capital is "Rêverie") or
  by province id. Ids shift whenever the map is rebuilt, so prefer the capital key;
  `build_mod.py` stops if a named id is no longer a victory point.
- **Rouental (ROU)** is the country the author outlined inside Nonscio. Everything
  first built for NSC moved to it, with `NSC_` renamed `ROU_`; NSC is plain "Nonscio"
  again. `nations.IDEOLOGY_NAMES["ROU"]`: "Rouental" on the map for every government,
  with the author's formal names (2026-09-30): Monarchist "The Sacred Principality",
  Authoritarian "The Grand Principality", Theocratic "The Most Seran State",
  Democratic "The Principality" (a constitutional monarchy, since later that day), Communist
  "The People's Republic" (all "… of Rouental");
  adjective Rouentaise. (The first names, Perfect / Powerful / Boring / Shitty
  Rouental, were dropped.)
  - **Capital: Rêverie**, the one-province state the author drew at (660, 805)
    ("Rouental 27" in that build), set by `nations.CAPITALS` (tag → pixel, since state
    ids shift). Neighbours' capitals are named by `CITY_NAMES` "capital:TAG": Guedelon,
    Evriches, Argent-sur-Seigne (SGN), Grande Hollier, Lanzerac, Villerose (SGV),
    Tanière (LST).
  - Leaders are in `common/characters/ROU.txt`: **Roland II Cahun** ("Roland Cahun"
    until 2026-10-08; `despotism`, leads at start; his description, shown on his portrait,
    is the author's list of his titles: `desc` in his leader role, after `ideology`, which
    `check_mod.py` and `country_list.py` expect first) and Serelle Cahun
    (`fascism_ideology`, fascist party leader; **Serelle VI Cahun** once she rules
    Rouental by any route: `nations.REGNAL_NAMES`, renamed by `set_character_name` in the
    on_ruling_party_change on_action; HMMLA's copy keeps her name). Serelle is also
    a general from the start (corps commander, skill 4, armor officer; HMMLA's copy
    too). Polite, Steady and Accept Reality only remove her party role
    (`remove_country_leader_role`), so she stays a general; Rudely (communist) retires
    her outright (author, 2026-10-02).
  - Portraits come from `source/portraits/roland_cahun.png` and `serelle_cahun.png`.
  - `common/national_focus/rouental.txt` has four mutually exclusive focuses in one row:
    - Kick Out the Parasites (Polite): democratic, elections on, both Cahuns retired.
    - Kick Out Your Brother: fascist, Serelle promoted, Roland retired.
    - Steady As She Goes (the author's; Habsburg icon): non-aligned, Roland promoted,
      Serelle retired.
    - Kick Out the Parasites (Rudely): communist, both Cahuns retired.
      Rudely also moves the capital to Carcarelle (`set_capital`, author 2026-10-02)
      and gets Rouental cast out of the Association at once (`rudely_effects`: dismantled,
      re-formed under Hollier with the other six). The communist flag
      (`ROU_communism.png`) is the author's Liberté flag, as is the Reibonne's.
      - **Execute the Prince** (under it, x = 6, y = 1): plays superevent
        `rou_civil_war` (the author's photo `source/superevents/rou_civil_war.jpg`, the
        author's quote and song, Rafael Krux's "Epic Church Organ"), sets
        country flag `ROU_civil_war` and starts the **Rouentaise civil war**
        (author, 2026-10-02; `nations.CIVIL_WAR`, `civil_war_effects`):
        - Rouental becomes the Reibonne (cosmetic tag `ROU_REIBONNE`, "The People's
          Republic of the Reibonne", flag `ROU_REIBONNE.png`, communist maroon).
        - Lustiana takes Maïeul and Serpette, Hollier takes Chirac, Selgrave takes
          Moelle (`ANNEX`), and the
          Association becomes "The Alliance of the Vale": there is no effect to rename a
          faction, so Hollier dismantles it and founds one from
          `faction_template_alliance_of_the_vale` with the same members.
        - Seven countries that own nothing at the start are `release`d and declare war
          (`annex_everything`). They have cores on their states from the start,
          except `CIVIL_WAR_ONLY` (FTH, RLA: the author wants them to exist only
          through the war), whose cores are added by the focus just before. (An
          Alliance of the East, AOE, was dropped on 2026-10-02 for the annexations.)
          The author's plans for the war (events, rival factions) are in
          `docs/CIVIL_WAR_NOTES.md`:
          Brillagne BRL (the Holy State of Brillagne; theocratic Rouental's ruler, a
          copy `BRL_mahaut_vi`, and flag); Crépuscule CRP (Principality; Absolute
          Monarchy); Reliette RLT (Grand Duchy; Feudalism); The Marches MRC (Alliance
          of the Marcher Lords; Oligarchy); HMMLA RLA (Her Majesty's Most Loyal
          Army; map name HMMLA, the author's, 2026-10-02; Strongman Rule, `RLA_serelle_cahun`; flag the fox quarter of `ROU.png`,
          which is also `ROU_fascism.png`); Vair VAI (Duchy; Feudalism); The Faithful FTH
          (the Faithful Children of the Goddess and Her Saint; Holy Order). States
          are named in `CIVIL_WAR` (first = capital; HMMLA's holds all eleven Royal Fiefs, Rêverie first,
          `nations.ROYAL_FIEFS`, the author, 2026-10-21: "HMMLA should have all the royal fiefs"); the focus file writes
          `@STATE:<name>@`, which `nations.fill` turns into ids. Two countries may
          share a name: their country files get the tag appended.
    - Left to right: Polite, Brother, Steady, Rudely.
  - The democratic and communist parties have no defined leader, so the game generates one.
  - **Accept Reality** (x = 8) is the fifth mutually exclusive path. It makes Rouental
    theocratic under **Mahaut VI** (`theocrat`; portrait from
    `source/portraits/mahaut_vi.jpg`; recruited in history as theocratic party leader),
    retires both Cahuns and plays superevent `rou_reality`.
  - **Plans for Cardonia** (x = 11, cost 1, not exclusive) creates an `annex_everything`
    war goal on CRD. It is for testing wars without justifying.
  - **Governorates and Royal Fiefs** (the author, 2026-10-21: "They should be shown, and will eventually affect play.
    They'll hook into the levy system, with your relationship with the governorates affecting manpower in their
    provinces and the quality of their levies"; "for now they should be the strategic regions, and lines on the state
    panels ... Royal fiefs should also have a line on their state panels"): Rouental's 26 governorates
    (`source/governorates_ROU.json`, the fief map's rough patches until the author draws the Governorate Lines; 8
    named on the fief map, 20 numbered on the grouping map and named by the author, three of them one: Terres
    Séparées, the Alliance of the East's land) are its strategic regions (`scripts/governorates.py --apply`; Brillagne
    and Concorde et Volonté are in none and keep theirs), but Terres Séparées, two regions since 2026-10-21 (the
    author: "South Montvallée should encompass Hollier, Evriches, Seigne, Serpette, and Chirac. North Montvallée
    should encompass Selgrave, Lustiana, Lanzerac, Moelle, Maieul, Serieux, and Petit Selgrave"; the file's `split`),
    27 in all. A state in one reads "Governorate of X" on its panel, a Royal Fief (`nations.ROYAL_FIEFS`: Rêverie,
    "Reverie still needs to be marked as a royal fief", and the ten, all in Couronneterre) "Royal Fief · Governorate
    of Couronneterre"
    (`build_mod.state_lines`: a scripted GUI docked to the state panel, in the state's scope, its text a scripted
    localisation by state id; with the Deco UI only, which keeps the row for it).
  - **The governorates and the three powers in game, bare bones** (the author, 2026-10-21, night: "I think we should
    start to try to put the mockups into practice, to make sure everything were planning will work. Let's get them
    into the game, even if they're bare bones for now"): `scripts/rouental_ui.py`, run after `deco_ui.py` (it reads the
    build through `scripts/rouental_realm.py`, the mockups' data model, moved from `deco_ui/art/proposals/governorates/`)
    and writing into it; `scripts/rouental_preview.py` draws both windows from the build's own files with the Deco UI's
    renderer (`work/previews/`). Every name and number but the author's is the mockups' placeholder.
    - **The Governorates** decision category (a scripted GUI, `decision_category`): Open the Map of the Realm, Raise the
      Blue Guard of Brume (once: two divisions of leg infantry in Grand Brume, experience 1, equipment 30 %;
      Graisivaudan's loyalty -20, every governorate's -5, the author's "emergency measure"), Survey the Realm's Levies
      (75 PP, every 180 days: every state inspected; Proud estates -5; it keeps the category from ever emptying). The
      map is a window of its own (1330 x 846, beside the decisions panel): every governorate drawn from the build's
      state borders at 2.6 times, coloured by its loyalty band (five pictures a governorate, one shown; each a button,
      to test whether the game clicks a button by its picture's shape or its rectangle) and its seal (a button on top,
      which always works), the Royal Fiefs hatched gold, the state and governorate borders over them. The card: the
      governor and how they came (`rouental_realm.governorates`' placeholders), loyalty (a 20-frame bar, the frame set
      by a variable: `properties`), the estates' temper, the peoples, the states (a dynamic list over an array of the
      selected governorate's states, in each state's scope: its name, people, levies (Unknown until inspected; Grand
      Brume Ceremonial) and men), four actions (Send Inspectors 25 PP, Grant Privileges 50 PP, Demand Levies +5000 men,
      Summon the Estates 20 PP: the temper rolled again). Loyalty = the governorate's fixed part (peoples, governor,
      chance) + its estates' temper + what actions and the three powers have added + the zone's; each state's manpower
      follows it (a dynamic modifier, `local_manpower` = (loyalty - 50) / 200, read from a state variable).
    - **The Three Powers**: a button on the politics screen where the game's balance of power sits (the Deco UI's
      `layout_politics.BOP`), showing the zone, opening a window beside the panel: the triangle (its zones drawn with
      their names), the marker placed by the shares (`properties` x and y, worked out in script), the six months'
      trail, the lit zone, the holders' portraits (Roland II Cahun, Mahaut VI, Tara Blanchart) and shares, where the
      balance stands and what it does, the four decisions (buttons, each once in 30 days), the estates' leanings
      (loyalty since 1 January). The shares start at 40 / 35 / 25 (the author's); each month they drift a point or two
      (`on_monthly_ROU`); a zone is a national spirit (`ROU_zone_*`, placeholder effects); a move toward a power gives
      the estates who lean to it half the shift as loyalty (Pious to the Voix, Leal to the Prince, Proud to the
      Speaker; the Southmarchers lose a fifth of the Voix's gains). Rouental's Test Events category has "Test: the
      Three Powers to the Next Zone".
    - **Assumed, to see in game**: that a button reacts only on its picture's opaque part (if not, clicking inside a
      governorate may pick a neighbour; the seals work either way); `properties` x, y and frame from variables; the
      dynamic list's scope and `[This.GetName]`, `[?rou_manpower_k]` in it; a top-level scripted GUI window over the map
      and its clicks; the politics screen's button docked to `politics_tab`; a dynamic modifier read from a state
      variable; `on_monthly_ROU`.
  - **Faction.** ROU starts as leader of "The Association of Reibonnaise States",
    together with GDN, LST, EVR, HLR, SGV, LZC and SGN.
    - **Reibonnaise opinions** (author, 2026-10-02; `nations.REIBONNAISE`): +20
      `valsora_reibonnaise_ties` between them, none while either is communist, and −20
      `valsora_against_communism` towards every communist country. The scripted effect
      `valsora_reibonnaise_opinions` re-sets them on `on_startup` and every
      `on_ruling_party_change`. `common/ai_strategy/valsora_reibonnaise.txt` makes the
      AI want them as allies (alliance 200, befriend 100) while neither is communist.
    - Lanzerac and Guedelon (Lordly Republics, democratic) left the Association at
      once. Likely cause: a member needs 30 % support for the leader's ideology
      (`IDEOLOGY_JOIN_FACTION_MIN_LEVEL`) and they had 20 % monarchists. They now start
      democratic 40, monarchist 30, the rest 10 (`nations.POPULARITIES`).
    - Its template, `faction_template_reibonnaise_association` in
      `common/factions/templates/valsora_factions.txt`, uses vanilla's generic manifest,
      goal, rules and icon.
    - ROU's history does `create_faction_from_template` + `add_to_faction`, the way
      vanilla ENG does in 1.19.
- **Releasables from the Subregions layer** (2026-10-17): `nations.SUBREGIONS` (tag -> a pixel inside its painted
  part) makes Belekria's republics, Krionik's principalities, Tethia and Pakitsk releasable: cores on the states mostly
  painted in that part, the state at the pixel the capital (a patch of the same colour joins the nearest seed of it,
  so islands follow and one colour may serve two parts). `nations.RELEASABLE` (by state name) stays for Rouental's.
  `nations.CORES` (tag -> a pixel per state) gives cores on states others own (Sminishia's old land).
- **Subjects** (`nations.HISTORY`, `set_autonomy`): the game's levels, and the mod's **Protectorate**
  (`autonomy_valsora_protectorate`, `nations.PROTECTORATE`, Krionik's only: Sombor). The mod ships the game's puppet
  level without its "no fascist overlord" clause (`vanilla_parts.EDITS`): Valsora's Authoritarian overlords (Kampf,
  Illiricium) keep plain puppets. `check_mod.py` checks every autonomy level a history sets (mutation-tested).
- **Starting armies** (author, 2026-10-02): every country owning land but Rouental gets
  `history/units/<TAG>_2036.txt` (`nations.generic_oob`): "Infantry Division" (8
  infantry, 1 artillery, engineers, recon), about one per six states, 2 to 24, at the
  victory points of its states (capital first), plus the techs for them. An OOB
  division takes its men out of the country's pool (`start_manpower_factor = 1.0` did
  not stop that, in game, 2026-10-04). Until 2026-10-16 each country's history added
  the men first (`add_manpower`, 12,000 per division; Rouental 150,000); the author
  had it removed ("if you are please remove it"), so the divisions come out of the
  country's own pool. Rouental's Royal Host forms on the game's first day instead
  (`on_startup`: its own men, then `load_oob`; `nations.ROU_HOST_STARTUP`, 2026-10-20), so it
  starts full and keeps its experience. State population is 300 per map pixel (`build_mod.POP_PER_PX`; 20 until
  2026-10-04, when the whole world held 75 million and Seigne 7,000, and the pools were too small).
- **Devlon's 15 test spirits** (author, 2026-10-14: to see how the politics screen shows many
  national spirits): `nations.TEST_SPIRITS`, ideas `DVL_test_spirit_1`..`15` with vanilla's generic
  pictures and no effects, added in Devlon's history. Remove the list and its `HISTORY` entry after
  the test. `check_mod.py` checks every idea's picture exists.
- **Rouental's test decisions** (author, 2026-10-15: "Give decisions to Rouental to spawn generic events of each type /
  layout, and a superevent for testing. The superevent should use the clown music and placeholder anime girl image"):
  `test_events.py`, the category "Test Events" (`ROU_test_events`, for Rouental's player), free and repeatable, each
  firing a placeholder event (namespace `valsora_test`): a country event; a long one with four options; a state event
  (from the capital); a news event and a major one (sent to every country); a leader event (a random general of
  Rouental's: the portrait window); an operative event (an operative created first if there is none; shown only with
  La Résistance); and the test superevent (`rou_test`, "This Is Only a Test": the anime picture and Entry of the
  Gladiators). Texts are Claude's; no option does anything. Take the category out when the testing is done (the
  author will, before the first public build). Fixed after the first test (2026-10-15): the state event names
  `trigger_for = controller` (without it the game shows a state event to no one: `check_mod.py` checks it), and the
  operative decision first gives Rouental an intelligence agency (`create_intelligence_agency`) and an operative.
- **Opinion modifier names**: `valsora_reibonnaise_ties` is "Seran Ties" and
  `valsora_against_communism` "Seran Biases" (author, 2026-10-04).
- **Named generated rulers**: `nations.NAMED_LEADERS` gives a generated ruler the
  author's name and portrait: Illiricium's is **Ema Milize**
  (`source/portraits/ema_milize.png`); Krionik's is a council, the **Kriosaivak Council of
  Marshals**, with its emblem as the portrait; Leithanien's is **Helmut Shulz**
  (`helmut_shulz.png`) and Terreich's **Charlotte Gustoff** (`charlotte_gustoff.webp`,
  cropped from a photo) (author, 2026-10-08); Chineasia's is **Han Leji**
  (`han_leji.png`, author, 2026-10-12). Solitas' new rulers (2026-10-13) and Tsuruma's
  **Akihiro Tanaka** (2026-10-13, later) are named without portraits (`None`): they keep
  a generic portrait of their culture.
- **Nation names** come from `COUNTRIES` in `build_mod.py`: name and adjective feed
  `TAG`, `TAG_DEF`, `TAG_ADJ`, the per-ideology variants (`TAG_communism` etc.) and the
  continent key.

- **Rouental's names** (2026-10-02): the author's fiefs are
  `source/names/rouental_fiefs.txt` (393 fiefs under 14 headings; `cultures.fiefs`).
  **Every fief is a vassal of the Crown; the headings are cultural groups, not vassals**
  (author's correction), and the governorates between vassals and Crown have no power (2026-10-21, night: "The
  governorates still hold little power. They were designed to try to centralize the nation, but completely backfired.
  The governor remains the crown appointee, and is responsible for trying their best to reign in the unruly vassals").
  The cultural groups are Rouental's peoples, and their loyalty differs: the Carcaraise (the list's "Carcasonnaise",
  renamed Carcarelle) resent Rêverie, holding Carcarelle the true heart of Reibonne's culture; the Nataine descend
  from the Natin empire's invaders, fewer and less quarrelsome than the Carcaraise but proud, prickly and never fully
  Rouentaise; the Oscarl are "fiercely loyal and grateful for being allowed to settle in
  Rouental"; the Chatois, descendants of Natin slaves raised to lordship for helping throw the invaders back, "are ever loyal"
  (`docs/DECISIONS.md`, the governorates' screen). The others (the author, 2026-10-21, night: "The other cultures I
  remember off the top of my head"): **Vairande**, the people of Vair, "Haughty but generally loyal. A seafaring
  folk"; **Riverlander** ("Riverrain in french?"), "the most numerous of the Rouentaise culture groups, plying the
  great rivers of the nation"; **Northmarcher** ("Marchenordois"?), "A grim, serious, and disciplined people. Ever
  watching the north from their mountain strongholds"; **Southmarcher** ("Marchesudois"?), "a martial people that
  have been greatly influenced by Linterre to the south ... The home of Reformed Seranism"; **Crépusculaise**, "Not
  technically Reibonnaise, and geographically outside the Vale, though ancient ties mean they share a language. Was
  the last addition to the realm, joining through a joint marriage. Utterly loyal to their prince, though their
  loyalty to Rêverie varies"; **Piscan**, "Traders, fishermen, and sailors of the Piscary sea"; **Helvetica**,
  "Extremely isolated in their own little valley, extremely pious, generally loyal"; **Recoltaise**, "the breadbasket
  of Rouental, and generally the least divided amongst separate vassals. Proud and wealthy". Which heading of the fief
  list is which: Carcasonnaise the Carcaraise, Northmarch, Southmarch, Crépuscule, Piscan, Helvetican, Recolt, Nataine,
  Chatois and Oscarl as named; Conflans (151 fiefs, the most) Claude's guess for the Riverlanders; the Vairande's,
  the Lyrién and the Lustianaise open. Rouental's faith is Seranism, its head the Voix; power "tends to fluctuate
  between the Sacred Prince, the Voix, and the Speaker of the Estates General" (a triangle for it proposed:
  `deco_ui/art/proposals/three_powers/`). The Voix is **Mahaut VI** (the author, 2026-10-21, night: "The Voix is the
  leader of Brillagne / theocratic Rouental"), the Speaker **Tara Blanchart** (in the mod since the same night: the
  democratic party's leader, `ROU_leader_constitutional_monarchism` named in `nations.NAMED_LEADERS`, "She is the ruler
  of democratic Rouental as well"; the author's painting, `source/portraits/tara_blanchart.webp`). Rouental "is just coming out of a long
  regency by the previous Voix who had tried to cement her power, ended only once the previous Voix died and the new
  one assumed the office and willingly gave up a lot of the power" (the start: Prince 40, Voix 35, Speaker 25). The
  Southmarch's Reformed Seranists "respect the Voix as a spiritual leader, but don't consider them self bound to her.
  Likewise, the Voix isn't fond of them, as they break with many of the Faith's commandments".
  The author will give each fief its title; per-fief levies wait for that. They give
  Rouental's name list noble surnames ("de Beaufort", "d'Aurifort") and its division
  names: "The Royal Host" (Garde Royale, Ost de <royal fief>) and "Vassal Levies"
  (Levée de <fief>, numbered "%de" as vanilla requires), in
  `common/units/names_divisions/ROU_names_divisions.txt`. The levy-army design is in
  `docs/ROUENTAL_ARMY.md`. Built: the **Feudal Army** spirit (`ROU_feudal_army`:
  recruitable population −80 %, training ×2, PP −10 %, stability −5 %; anime placeholder
  icon) and the **royal host** (`nations.ROU_HOST`; 2026-10-21, the author: "except for the Oriental troops (who
  should remain motorized) and the 1e and 2e divisions (who should remain armored,) the rest of the starts units
  should be mechanized": 2 armoured, 9 mechanised and 1 motorised division, the 12th, "12e Ost des Territoires
  Orientaux", in Concorde et Volonté; full support, Elite, plus techs, a "Char Royal" tank and a stockpile).
  The levies themselves are not built: tiers and costs await the author.
  - The author's detailed fief map (`Rouental_Map_TEMP_2.pdn`, 8000×4471, decoded in
    `work/pdn_rmap`) was overlaid on the game's states (axis-aligned fit, IoU 0.885;
    game x = 0.0396 fx + 572.1, y = 0.0379 fy + 747.4). Every label was read and placed:
    `docs/ROUENTAL_FIEFS.md`, `dist/rouental_fiefs_overlay.png` and
    `source/rouental_fiefs_by_state.json` (state name → its fiefs by cultural group).
- **Flags** are `source/flags/TAG.png`, any size (HOI4 gets 82×52, 41×26 and 10×7
  32-bit TGAs, bottom-left origin). `TAG_<ideology>.png` is used only while that
  ideology rules: Rouental's banner of arms is `ROU.png` and its blue-white-gold
  tricolour is `ROU_democratic.png` (author's choice). The other seven were cropped
  from the author's flag sheet. Countries without a PNG get a placeholder stripe in
  their map colour. Flags sent in another shape are fitted to 82:52 without stretching:
  scaled evenly, then plain field added inside the stripes (or plain sides trimmed), so
  emblems keep their shape (2026-10-13, the author's wish). Vertical bands get plain rows
  above and below instead, so their widths stay (Qinguo), and a field division that must
  reach the corners is redrawn at the new width round the unchanged emblems (Ganden's
  border and mountain triangle).
- **Formal names** (`nations.FORMAL_NAMES`, e.g. "the County of Evriches") feed
  `TAG_DEF` and the per-ideology `_DEF` keys that have no `IDEOLOGY_NAMES` entry.

## Ideologies (`ideologies.py`)

The author's five ideologies. The internal keys stay vanilla's so vanilla script keeps
working; names come from `localisation/english/replace/`:
- `democratic` Democratic and `communism` Communist are unchanged.
- `fascism` is Authoritarian, coloured black (20,20,20).
- `neutrality` is Monarchist, coloured purple (128,48,168).
- `theocracy` Theocratic is **new**, coloured white (238,238,238).
- **Subtypes** (sub-ideologies) are the author's set of 2026-09-30, in
  `ideologies.SUBTYPES` (key, name, description); a renamed vanilla subtype keeps its
  key (e.g. `despotism` is "Absolute Monarchy", `leninism` "Vanguardism", `theocrat`
  "Hierocracy"). Democratic: Conservatism, Liberalism, Social Democracy, Populism,
  Agrarianism, Constitutional Monarchy. Communist: Orthodox Marxism, Vanguardism, Party
  Centralism, Council Communism, Anarcho-Communism, Agrarian Socialism. Authoritarian:
  Military Junta, Fascism, Corporatism, Strongman Rule, Technocracy, Revanchism.
  Monarchist: Absolute Monarchy, Oligarchy, Feudalism, Enlightened Absolutism, Elective
  Monarchy, Legitimism, and the author's **Personal Union** (2026-10-07, Merlgould) and
  **Khanate** (2026-10-09, Sanada) and **Semi-Constitutional Monarchy** (2026-10-13,
  Avesária, then Bromé) and **Regency Council** (2026-10-17, Krionik); Democratic also has the author's **Stratocracy**
  (2026-10-07, Krionik until 2026-10-17) and **Radical Republicanism** (2026-10-09, Vilna). Authoritarian also has the author's **Bleacherism** (Alban
  supremacy; officially a senatorial republic under a strongman): ILR CTF ETR MZG;
  KIL is Legitimism; and **Humanism** (2026-10-12, the Humanist State: humans above
  Valsora's other races, apartheid-style). Theocratic: Hierocracy, Clerical Monarchism,
  Holy Order, Synodal Rule, Prophetic Rule, and the author's **Divine Republicanism**
  (2026-10-12, Muqadasa Salamat). Vanilla's Earth-bound ones (`nazism`, `japan_militarism_ideology`
  …, `ideologies.HIDDEN`) stay defined because vanilla's characters and focus files name
  them, but are never given to generated leaders. The author wanted no more on 2026-09-30, and
  has added their own since (above).
- Subtype descriptions start with the subtype's name ("Feudalism: …"), so it shows on
  mouse-over (author). `lordly_republic` "Lordly Republic" (democratic) is the author's
  own: a republic in which the nobility and clergy retain significant power.
- **Every ruler is a set character** (author, 2026-09-30: no subtype left to chance).
  `nations.LEADERS` gives each tag its subtypes; the first leads the country, and the
  country starts under that subtype's ideology (elections on if democratic).
  `cultures.leaders` makes the characters (`common/characters/valsora_leaders.txt`,
  id `TAG_leader_<subtype>`, never `TAG_<subtype>`, which the game reads as the country's name under that subtype): a name from the culture's list (famous surnames skipped, full
  names unique map-wide; famous ones met in a list already in use, like Franco and Windsor on
  2026-10-13 (and di Savoia, Garibaldi and de Castro, seen on the nation sheet), are drawn again (`cultures.DRAW_AGAIN`), so no one else's name changes) and a generic politician portrait of the culture, seeded by
  tag. Hand-made rulers (`HAND_MADE`: ROU, AIS) keep theirs; Rouental also gets
  `ROU_leader_constitutional_monarchism` and `ROU_leader_leninism`, promoted by the Polite and Rudely
  focuses. Author's picks: CRD Enlightened Absolutism; EVR, SGN Feudalism; HLR, STO
  Absolute Monarchy; LST Elective Monarchy; SGV Oligarchy; LZC, GDN Lordly Republic;
  LNT Conservatism; RMD Social Democracy; RST Revanchism; VLN Liberalism; ESD, CRZ
  Constitutional Monarchy; PLH Prophetic Rule. The six continent placeholders were not
  chosen and default to Absolute Monarchy. Characters: Roland feudalism, Serelle
  strongman_rule, Mahaut theocrat, Communist Merlovich anarchist_communism.
  `check_mod.py` checks every country has a recruited leader of its ruling ideology
  (mutation-tested). Its party icon `GFX_ideology_theocracy_group` is
  a placeholder, `source/ideologies/theocracy_placeholder.png` (the anime picture),
  centre-cropped to 64×64. The author and a friend will draw the real icons.
- **Party list.** Vanilla's politics view fits four 16 px party rows. `interface/countrypoliticsview.gui`
  is vanilla's (`source/interface/`) with `parties_grid` rows at 13 px, so five fit;
  `check_mod.py` checks it.

How it's built:
- `common/ideologies/00_ideologies.txt` overrides vanilla. It is vanilla's file
  (`source/ideologies/`) with the colours changed and a theocracy block modelled on
  neutrality.
- Every country starts at 20% for each ideology; every `set_popularities` lists all five.
- `check_mod.py` checks that popularities name real ideologies and sum to 100, that
  every `ruling_party` / `has_government` is an ideology, and that character
  sub-ideologies exist.

**Map colours come from `common/countries/colors.txt`**, not the `color` in each
country file. Tags missing there got random colours in-game, which is why most were
wrong until the build wrote its own (`color` plus a lighter `color_ui`).

**Map colour per government** (`nations.LOOKS`) uses cosmetic tags `TAG_GOV_<IDEOLOGY>` (not `TAG_<IDEOLOGY>`: its flag would clash with `TAG_<ideology>.tga` on Windows, which ignores case; `check_mod.py` checks file names for this),
defined in `common/countries/cosmetic.txt`. An `on_ruling_party_change` on_action sets
them, or drops them for ideologies with no entry, so every route to power recolours the
country. Their flags reuse `source/flags/TAG_<ideology>.png`, and their names are
localised for every ideology. Rouental:

| Government | Map colour | Flag |
|---|---|---|
| Monarchist, Authoritarian | royal green | banner of arms |
| Democratic | tan | tricolour |
| Communist | maroon (128, 16, 16) | the author's Liberté flag (was plain maroon) |
| Theocratic | gold | sword and fleurs quarter of the banner |

## Cultures (`cultures.py`): generic portraits, names, graphical culture

Vanilla's generic portrait lists (`portraits/*.txt`) are keyed by Earth continents, which
don't exist here. That was the cause of "Failed to generate a portrait / name" and
"unknown continent europe" in error.log. So the build writes:
- **`portraits/valsora_portraits.txt`.** One `continent = { name = <ours> … }` block per
  continent, plus `TAG = { … }` blocks for countries that look different. Each block has
  army / navy / political (per ideology) lists of vanilla 1.19 generic sprites.
  `source/names/vanilla_portrait_sprites.txt` is the list of those sprites, copied from
  vanilla `interface/_random_portraits.gfx`; `check_mod.py` checks against it.
- **`common/names/valsora_names.txt`.** Each tag gets a vanilla culture's name block
  (`source/names/vanilla_names.txt`). UTF-8 without BOM, like vanilla.
- **Graphical culture** in `common/countries`.
- **Who gets what:**
  - The continent defaults (author's choices) all use Europe portraits except where
    noted: Nonscio ENG, Araseos ITA, Aislada AST (commonwealth gfx), Solitas SWE,
    Yastreovakia POL. Usnistan is PER with Arab + African portraits and middle_eastern
    gfx; Orientalis is JAP with Asian portraits and asian gfx.
  - The author's flags can come as one `.pdn` with a layer per flag
    (`import_flags.py`; 2026-10-04: its "Marchers" layer showed The Marches had been
    given the three-lozenge flag, which is its "Duchy of the Mountains"; fixed).
    2026-10-05: **the author swapped the Marches' flag to the three lozenges** after
    all ("the sword didn't read well"; the sword flag is now the file's "Spare" layer),
    and redrew Fraxhemark's.
  - Overrides are in `TAG_CULTURE`: the Reibonnaise states (ROU SGN EVR HLR SGV LST LZC
    GDN) and Placeholdros (LNT) use FRA names and France portraits (author: French for now);
    RST VLN ESD CRZ PLH use POR names (added to `source/names/vanilla_names.txt` from
    vanilla) and Europe portraits.
- **Scientists** (2026-10-14): every continent and country block also has
  `scientist = { male female }`, vanilla's generic scientist portraits
  (`interface/_scientists_portraits.gfx`: Europe's for European, French, Iberian and
  American cultures as vanilla does for North America, Arabia's and Africa's for Usnistan,
  Asia's, India's, South America's). Without them every generated scientist logged "Failed
  to generate a portrait … scientist" and then, on every save load, an empty icon (`""` and
  `"_small"`, icon_entry.cpp): 156 + 568 lines in the 2026-10-02 log. Operatives use
  vanilla's default (an unknown silhouette).
- **Vanilla's portrait files** (`00_portraits.txt`, the DLCs' `01_anniversary`, `02_tiger`,
  `03_mtg`, `027_lar` and `998_scientist_portraits.txt`) are keyed by Earth continents: 139
  error.log lines ("unknown continent europe", then an unexpected token per list). The mod
  ships a file under each name (`cultures.VANILLA_PORTRAIT_FILES`); `00_portraits.txt`
  keeps vanilla's `default` block (fallback and operative portraits). `check_mod.py` checks
  all six and the scientist lists (mutation-tested).

## Superevents (`superevents.py`)

TNO-style, built only from vanilla pieces. **Confirmed in-game** (author, 2026-09-29):
the first build showed window, picture and text, but no music and no background (both
fixed below and confirmed: music plays, background shows). Title and quote are
white via `§W…§!` in their localisation (the typewriter fonts draw dark). How they work:
- **Calling one.** `valsora_superevent_<id> = yes` (inside `hidden_effect` in a focus).
  It sets global flag `valsora_superevent_<id>`, clearing the others, and fires hidden
  event `valsora_superevent.N` for every human player.
- **The event** sets country flag `valsora_superevent_open` and does
  `play_song = "valsora_gladiators"`, the way vanilla plays its speeches.
- **The window.** A `player_context` scripted GUI (`valsora_superevent_window`) is
  visible while that flag is set. Title, quote and author come from scripted
  localisation keyed on the global flags. There is one picture icon per distinct image,
  shown via `<element>_visible` triggers. The close button's `_click` clears the flag.
- **Assets.** The music is `source/superevents/*.ogg`: the first 45 s of the author's
  MP3s with a 4 s fade, Vorbis like vanilla music (`SONGS` in `superevents.py`).
- **Songs must belong to a music station**, or `play_song` logs "Song doesnt exist" (the
  first build had only an `.asset`).
  - Layout, from the Music Mod Creation Tool's HOI4 template: `music/valsora/` holds the
    `.ogg`, `valsora.asset` (`music = { name file volume }`) and `valsora.txt`
    (`music_station = "valsora"` + `music = { song chance }`, here chance factor 0).
  - The station also needs `interface/valsora_music_station.gui` (`valsora_faceplate`
    and `valsora_stations_entry`), a 2-frame cover sprite, and loc `valsora_TITLE`
    ("Valsora Radio") plus each song key.
- **Pictures** are cropped to 2:1 and scaled to 840×420 DDS.
- **Background.** `GFX_tiled_window_transparent` is see-through (vanilla's event window
  gets its look from separate header/footer images), so the window has its own
  generated background, `superevent_bg.dds`: dark, with gold frames.
- **With the Deco UI** (`DECO_UI`, 2026-10-15; `superevents_deco.py`): the mockup's Superevent board
  (`deco_ui/art/mockups/source/Superevent.html`), drawn with numpy and Pillow. The window covers the screen: a dark
  veil over the map (a cornered tile) with faint gilt rays round the middle and the board's vignette (drawn at half
  size, scale 2), and the panel centred on it, every element a direct child of the window (the visibility triggers
  name them): one picture holds the crest, the 900 x 645 frame (lacquer, gilt border, corner brackets, the rings round
  the picture) and the now-playing tab; over it a title strip per superevent (gilt Federo capitals between stepped
  hairlines, baked, since the hairlines follow the title's width: long titles shrink to fit), the picture with gilt
  fans and arcs in its corners, a diamond on its lower edge, the quote (`valsora_deco_italic_18`, curly quotes, no
  `§W`), the attribution (`valsora_deco_section_11`), the gilt "History Marches On" button (Esc closes it too) and the
  song (`ValsoraSupereventSong`, "Valsora Radio · Rafael Krux — Epic Church Organ", `valsora_deco_label`). The
  build measures every quote, attribution and song with the Deco UI's font files and stops if one would not fit its
  box (a box too short drops lines silently). **Seen in game** (2026-10-15, the test superevent): all eight titles
  drew at once (only the pictures had visibility triggers; each title has its own since, from the superevent's
  flag), and the author asked for something other than the guillotine: the crest's medallion is lacquer and holds
  **Valsora rising** (the top half of the Deco UI's globe, `globe_art.globe`), `superevents_deco.EMBLEM`; a compass
  star, an hourglass and a laurel wreath are `EMBLEMS` too, shown in `deco_ui/art/proposals/crests/`.
- **Current set.** Eight superevents: one per Rouental leadership focus (five), the
  Rouentaise civil war (Execute the Prince; the author's soldier photo), AIS
  "Fucking Explode" and the test one, fired by Rouental's test decisions (`rou_test`, last so the others keep their
  event ids). The quotes are Claude-written except the civil war's (the
  author's); all but the civil war use the author's anime picture and Entry of the
  Gladiators. The civil war has Rafael Krux's "Epic Church Organ" (`valsora_organ`,
  `epic_church_organ.ogg`, made with the ffmpeg bundled in the `imageio_ffmpeg` Python
  package: first 45 s, 4 s fade, Vorbis 160k); it replaced "Monsieur d'Elbée", which
  the author didn't like.
- **Checks.** `check_mod.py` checks scripted effects and events that are used, songs
  and their files, scripted localisation keys, and GUI window, element, sprite and
  button-text references (mutation-tested). Since 2026-10-15 decisions count among the users of effects and events,
  our events' titles, descriptions and options and our decisions and categories must be localised (hidden events and
  never-visible decisions excepted), and a decision's short icon name (`generic_x`) must be a sprite
  (mutation-tested: 9 breaks, all caught).
- **error.log on that test** also had 128 pairs of `Icon definition "" / "_small"`
  (icon_entry.cpp) when a second game was started: scientists generated without a
  portrait, one pair per scientist on each load; fixed 2026-10-14 (see Cultures).

`check_mod.py` also checks that recruited characters exist and are localised, that portrait
sprites resolve to files, and that every focus id and prerequisite is valid and localised.
