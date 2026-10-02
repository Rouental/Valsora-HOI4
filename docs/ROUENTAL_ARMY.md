# Rouental's army: a royal host and vassal levies

The author's idea (2026-10-02): Rouental is a very dysfunctional feudal state. Building
an army the normal HOI4 way should be very hard. Instead the crown starts with a
**small, superbly equipped army** and grows it with **levies from its vassals**, whose
equipment it controls much less. This note suggests how to build that in HOI4 1.19.
Built so far: the names, the Feudal Army spirit and the royal host (below); the levies
themselves are not.

## Already in the mod

- **Names.** The author's list of fiefs is `source/names/rouental_fiefs.txt`: 393 fiefs
  under 14 cultural groups. **Every fief is a vassal of the Crown** (author, 2026-10-02);
  the groups are cultural, and the governorates between vassals and Crown have no power.
  The author will give each fief its title.
  - Rouental's generated generals and admirals now carry noble names ("de Beaufort",
    "d'Aurifort") as well as ordinary French ones.
  - Division names come in two groups (`common/units/names_divisions/ROU_names_divisions.txt`):
    - **The Royal Host:** "Garde Royale", then "Ost de Rouental", "Ost de Saintiers"…
      after the royal fiefs.
    - **Vassal Levies:** "Levée de Carcarelle", "Levée de Beaufort"… after every
      vassal fief, in the list's order.

- **Feudal Army** (`ROU_feudal_army`, author 2026-10-02; placeholder icon, the anime
  picture): recruitable population −80 %, training time ×2, political power −10 %,
  stability −5 %. Its description says it opens the levies.
- **The royal host** (`history/units/ROU_1936.txt`): 2 armoured ("Division Blindée de la
  Garde": 4 medium tank + 2 mechanised), 2 mechanised and 8 motorised divisions, all at
  full equipment and 0.6 experience, with engineers, recon, AA, signals, logistics or
  maintenance, and field hospitals in support. Stationed around Rouental, Saintiers,
  Cournin, Rêverie, Charmas, Rochemont and Vendée. Rouental starts with the techs, a
  "Char Royal" tank design (both with and without No Step Back) and a stockpile.
- **Which state each fief (vassal) lies in**: `docs/ROUENTAL_FIEFS.md` and
  `source/rouental_fiefs_by_state.json`, from overlaying the fief map on the game's states.

## Recommended design (all vanilla mechanics)

1. **The royal host at game start.** An order of battle (`history/units/ROU_1936.txt`)
   with a few divisions at high experience and full, modern equipment. HOI4 does this
   for every country; ours are empty for now.

2. **Make ordinary recruitment painful.** Give Rouental a national spirit, e.g. "The
   Ban and Arrière-Ban", with modifiers such as:
   - `conscription_factor = -0.8`: very little recruitable manpower;
   - `training_time_factor = 1.0`: training takes twice as long;
   - optionally a production penalty (`production_factory_max_efficiency_factor`), so
     re-equipping is slow.

   Focuses or reforms could later soften it ("Standing Army Reform").

3. **Levies come by decision.** Add a decision category, "Call the Banners", with one
   decision per vassal or, with 393 of them, per state, calling the vassals in it. Each decision:
   - costs political power, and lowers that vassal's **loyalty** (a variable per
     vassal, shown in the decision's tooltip);
   - spawns that vassal's levy with `load_oob = "ROU_levy_<vassal>"`. The OOB file
     defines a **locked template** (`is_locked = yes`, so the player can't redesign it)
     and divisions that start under-equipped (`start_equipment_factor = 0.3`) with
     old kit, which is the "less control over equipment";
   - places the divisions in the vassal's own state (`source/rouental_fiefs_by_state.json`).

4. **Levies are temporary.** A timed decision or mission (`days_remove = 180`) sends
   them home with `delete_unit_template_and_units` (to verify in-game). Keeping them
   longer costs loyalty each month.

5. **Loyalty matters.** A vassal at low loyalty refuses the call, demands concessions
   (PP, a state, a title) or rebels. That ties straight into the civil war: the
   revolting tags could be the disloyal vassals (`docs/CIVIL_WAR_NOTES.md`).

## Levy quality (proposal, 2026-10-02; to redo per fief once the titles exist)

The first draft below gave tiers per cultural group, mistaking the groups for vassals.
Tiers belong to each fief; the groups could at most be a default.

Each levy is a `create_unit` in the vassal's state, as vanilla focuses do
(`start_experience_factor`, `start_equipment_factor`, `start_manpower_factor`), with a
template the player can't edit. Quality comes from four knobs: the template, experience,
how full its equipment is, and how many divisions come.

| Tier | Template | Experience | Equipment | Example |
|---|---|---|---|---|
| Elite | infantry + artillery, full support | 0.5 | 100 % | Reliette: a primary martial vassal |
| Good | line infantry + artillery | 0.3 | 70 % | to be chosen |
| Levy | infantry, little support | 0.1 | 40 % | to be chosen |
| Militia | small infantry brigade | 0 | 25 % | to be chosen |
| Ceremonial | one battalion | 0 | 10 % | single fiefs, e.g. Tal's "Arbalétriers de Tal" |

- How many divisions: by the vassal's title and tier.
- Ceremonial units are flavour. Tal's crossbowmen, "granted guns to fulfil the
  obligation", would be one under-strength battalion with a joke name.
- **For the author to decide**: each vassal's tier, which fiefs get their own flavour
  units, and how harsh the costs are (PP, loyalty, how long levies stay).

## Alternative: vassals as real subject countries

Each vassal could be a subject country with a custom "Vassal" autonomy, its own army and
the duty to join Rouental's wars. That models "less control" natively (the AI commands
them), but it splits Rouental into a dozen tags on the map and leaves the player with
almost no army of their own. It is better kept for the civil war.

## What's needed to build it

- Each fief's title (author, coming), then its tier and any flavour units.
- How harsh the loyalty costs should be, and how long levies serve.
