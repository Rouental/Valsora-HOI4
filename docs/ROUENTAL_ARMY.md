# Rouental's army: a royal host and vassal levies

The author's idea (2026-10-02): Rouental is a very dysfunctional feudal state. Building
an army the normal HOI4 way should be very hard. Instead the crown starts with a
**small, superbly equipped army** and grows it with **levies from its vassals**, whose
equipment it controls much less. This note suggests how to build that in HOI4 1.19.
Nothing here is built yet except the names.

## Already in the mod

- **Names.** The author's list of vassals and fiefs is `source/names/rouental_fiefs.txt`:
  14 vassal groups and 393 fiefs.
  - Rouental's generated generals and admirals now carry noble names ("de Beaufort",
    "d'Aurifort") as well as ordinary French ones.
  - Division names come in two groups (`common/units/names_divisions/ROU_names_divisions.txt`):
    - **The Royal Host:** "Garde Royale", then "Ost de Rouental", "Ost de Saintiers"…
      after the royal fiefs.
    - **Vassal Levies:** "Levée de Carcarelle", "Levée de Beaufort"… after every
      vassal fief, in the list's order.

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
   decision per vassal (Carcasonnaise, Conflans, Northmarch…). Each decision:
   - costs political power, and lowers that vassal's **loyalty** (a variable per
     vassal, shown in the decision's tooltip);
   - spawns that vassal's levy with `load_oob = "ROU_levy_<vassal>"`. The OOB file
     defines a **locked template** (`is_locked = yes`, so the player can't redesign it)
     and divisions that start under-equipped (`start_equipment_factor = 0.3`) with
     old kit, which is the "less control over equipment";
   - places the divisions in the vassal's own land. That needs the province-level map
     (your detailed map) to say which states belong to which vassal.

4. **Levies are temporary.** A timed decision or mission (`days_remove = 180`) sends
   them home with `delete_unit_template_and_units` (to verify in-game). Keeping them
   longer costs loyalty each month.

5. **Loyalty matters.** A vassal at low loyalty refuses the call, demands concessions
   (PP, a state, a title) or rebels. That ties straight into the civil war: the
   revolting tags could be the disloyal vassals (`docs/CIVIL_WAR_NOTES.md`).

## Alternative: vassals as real subject countries

Each vassal could be a subject country with a custom "Vassal" autonomy, its own army and
the duty to join Rouental's wars. That models "less control" natively (the AI commands
them), but it splits Rouental into a dozen tags on the map and leaves the player with
almost no army of their own. It is better kept for the civil war.

## What's needed to build it

- Which **states** each vassal holds. The fief list is at province level, which the
  map doesn't have yet; a state-to-vassal list would be enough to start.
- The royal host's size and kit (how many divisions, of what).
- How harsh the penalty and the loyalty costs should be.
