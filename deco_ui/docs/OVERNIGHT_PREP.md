# Overnight UI session: prep (written 2026-10-24)

For a Claude instance working on the **Valsora Deco UI** overnight, alone. The author: "I'm gonna set another instance
to working on the UI overnight to see what it can do." They are asleep. Nobody answers questions until morning, so
decide for yourself, keep every change easy to undo, and report in the morning. This file tells you where things
stand, what to work on, the rules, and what to hand over. The full manual is `deco_ui/CLAUDE.md`. Read it; this file
doesn't replace it.

## 1. Where things stand (2026-10-24)

- The repository's default branch is `claude/compassionate-allen-slfww9`. Everything up to 2026-10-24 is on it (latest
  commit `b316fc7`). If your session names another branch, start it from `origin/claude/compassionate-allen-slfww9`
  and push only to your own. `claude/intelligent-cray-c7ukf9` is an old branch of 2026-10-15: ignore it.
- **The Deco UI is v0.12.4** (`deco_ui/docs/VERSIONS.md`). The author last saw v0.12.2 in game (2026-10-21). v0.12.3
  (the commander pickers' foot buttons, the load window's buttons, the declare war swords) and v0.12.4 (the diplomacy
  tab's spirits inside their band) are **not seen in game yet**. Don't redo them.
- `deco_ui/tools/validate_preview.py` ends with `PROBLEMS: none` on this commit, and the Valsora build's `check_mod.py`
  passes.
- Rouental's estates and Généralités windows are the Valsora build's own (`scripts/rouental_ui.py`), not the Deco UI's.
  They are bare bones on purpose. Their zones, numbers and decisions are placeholders the author hasn't decided yet.
  **Leave them alone** unless something is plainly broken (text past its box, say), and then change only that.

## 2. Set-up (about 15 minutes)

1. `pip install -r requirements.txt` at the repository's root. Chromium is at `/opt/pw-browsers/chromium`. Never run
   `playwright install`.
2. **The game's files.** The author's private repository `Rouental/HOI4-Files` is their copy of the 1.19.3 install.
   Attach it (the `add_repo` tool: owner `Rouental`, repo `HOI4-Files`) and clone it to `/home/user/hoi4-files` as a
   sparse checkout (the full repository is too big):
   ```
   git clone --filter=blob:none --no-checkout <the URL add_repo gives> /home/user/hoi4-files
   cd /home/user/hoi4-files
   git sparse-checkout set --no-cone '/*' '!/gfx/fonts/*' '/gfx/fonts/*.fnt' '!/gfx/models/' '!/gfx/event_pictures/' '!/HOI4 Files/models/'
   git checkout
   ```
   It is Paradox's content: never copy it into the Valsora repository.
3. **Link it into `deco_ui/reference/`**, as `deco_ui/CLAUDE.md` section 3 says (the `for f in interface common ...`
   loop, `gfx`, the two `.lua` files, and `reference/valsora -> ../../build/valsora_test`).
4. **Build Valsora once:** `sh scripts/run_all.sh` at the root (3 to 5 minutes; logs in `work/logs/`; it should end
   with "all checks passed"). `deco_ui/reference/valsora` is that build, and the build keeps Valsora's own politics
   screen in `work/deco_base/`.
5. **Build the Deco UI once, unchanged:** `cd deco_ui && CHROMIUM_PATH=/opt/pw-browsers/chromium python3
   tools/build_all.py` (about 30 s). It must end with `PROBLEMS: none`, and `git status` should show nothing new. That
   is your baseline. If a texture differs only by anti-aliasing noise, `python3 tools/restore_noise.py` puts it back.

## 3. Read first

- `deco_ui/CLAUDE.md`, all of it. Above all: section 2 (how the author works and their standing preferences), section 6
  (engine facts learned in game), section 8 (`guipatch`), section 9 (pitfalls already hit) and section 12 (the pattern
  for a new screen).
- `deco_ui/docs/SCREEN_INVENTORY.md`: every game screen and how far the Deco UI changes it.
- `deco_ui/art/proposals/next_screens/README.md`: mockups of the 20 screens that are still the game's (drawn
  2026-10-17, **not in the mod**), with each screen's files, textures, hooks and a suggested order. That is your menu.

## 4. What to work on

The author asked on 2026-10-17 for "the proposed changes to all the UI screens", and v0.10 did the first eight. Carry
on from `next_screens/README.md` in its suggested order, as far as the night goes. Do a few screens well rather than
many badly; the author notices a 1 px offset.

1. **The unit counters and map icons** (`mapicons.gui`; every session). Do the counters, battles, bases and victory
   points first. **The ~450 unit type icons are icons**: draw them as a proposal only (rule 1 below).
2. **The division and ship details** (`unitview.gui`): the designers' look of v0.9 (`designer_art.py`).
3. **The commanders' trait trees** (`armytraittreewindow.gui`, `navytraittreewindow.gui`). The trait pictures stay
   the game's.
4. **The theatres** (`theatreselector.gui`; `make_insignia.py` already writes its `.gfx`: keep its insignia frames).
5. **The war overview, then the peace conference.**
6. **Operations and raids**, 7. **the right-click menu and the diplomatic message icons** (the message icons are
   icons: proposal), 8. **the end of game**, 9. **achievements, multiplayer, friends, career profile.**

For each screen, follow the pattern of v0.10 (`deco_ui/CLAUDE.md` sections 4, 7 and 12):
- an art module `tools/<screen>_art.py` with `ADDS = [(key, path, w, h, function)]`, its own key prefix, listed in
  `ART_MODULES` (`tools/art_util.py`);
- textures at the game's paths, sizes and frame counts (look at the game's texture first: which frame is lit differs
  from sprite to sprite, section 9);
- a `.gui` patch (`make_<screen>.py` with `guipatch`, every element kept) only where a box must move or a text needs
  one of the mod's fonts;
- a preview beside the game's (`tools/preview_<screen>.py` → `build/preview_<screen>.png` and `_vanilla.png`);
- the step in `build_all.py`;
- `validate_preview.py` ending with `PROBLEMS: none`.

## 5. Rules (each comes from something that went wrong, or from the author's own words)

1. **No icon of the game's changes without the author's yes** (2026-10-17: "I noticed you replaced some icons that I
   didn't want you to yet"). A new or redrawn icon goes to `deco_ui/art/proposals/<name>/` with a sheet beside the
   game's. Frames, plates, backgrounds and windows of the screens you restyle may go into the mod.
2. **Never trace the game's art into the Deco style** (2026-10-21: "weird sloppy lines and missing pieces of the
   design ... it seems to keep happening"). Draw every picture by hand, measured against the elements the `.gui` puts
   on it: rims and wells whole, straight lines on whole pixels. Look at every picture at 2x before it goes in.
   `fragments.py` fails on broken gilt; a deliberate dash goes in its `KNOWN`, with a reason.
3. **Never commit Paradox's content.** `deco_ui/reference/` and `deco_ui/build/` are git-ignored. A preview that shows
   the game's art (every `_vanilla` one, and any picture with the game's icons in it) is only sent to the author, never
   committed. Proposals go in `art/proposals/` only if they hold no game art.
4. **Never delete or rename one of the game's `.gui` elements** (the engine finds them by name). Move, re-skin or hide
   them. Write every `.gui` with `GP.write_gui`: it unquotes orientations, which the game rejects on containers.
5. **The author's design language stands** (section 5 of the manual): lacquer and gilt, chamfers and steps, octagons
   and diamonds, jade for lit, line icons. Valsora is 2036, so every subject is modern (no WWII kit). Panels are opaque
   (at 97 % the map's names show through). There are no corner brackets in a chamfered corner (the author:
   "you have a lot of trouble with this particular decorative element"). Text is centred by its ink, and the game
   rounds a centred line's start up. A box too short drops its second line silently, so size for two lines. Flags are
   never scaled.
6. **Keep each screen in commits of its own**, named for it, so the author can take one out with `git revert` (v0.9's
   screens are one commit, `8dece16`, for that reason). Commit and push often: the container can be reclaimed.
7. **The bar for the zip:** after the Deco UI's build, rebuild Valsora (`sh scripts/run_all.sh`), then
   `check_mod.py` must say "all checks passed". If you change `scripts/check_mod.py`, run `scripts/mutation_test.py`
   and add a break for each new check.
8. **Say what is assumed.** You can't run the game. Anything not seen in game is "(assumed)" in the notes and goes on
   the "Things to check" list.
9. **Stay out of:** the map (`source/HOI4 Mod Map.pdn`), the Gazetteer and its site (`gh-pages`: nothing of the UI is
   on it, so don't publish it), the nations' content, `scripts/rouental_ui.py` (section 1), the larger flags ("don't
   add anything to do with it into the mod yet") and the loading screens' pictures ("kept for later").
10. **Never write a model name** in commits, code or docs. End each commit message with the attribution lines your
   session gives you.

## 6. Time savers

- `python3 tools/build_all.py gen_textures.py` skips the slow texture step; any step names can be listed.
  `gen_textures.py <prefix>` redraws only the keys with that prefix.
- Helpers working side by side each need their own `VALSORA_TEXTURE_MANIFEST=<file>` and key prefix (v0.12 was made
  so). Their textures read as stale until they're redrawn with the real manifest.
- `guilayout.py` in `art/proposals/next_screens/` already lays out each window from the game's `.gui` files. Its
  numbers (sizes, places, the boxes inside) are a head start for the real art modules.
- `medallion_check.py` fails the build if a new top-left window would sit under the flag medallion. If one does, move
  it below the medallion the way `make_mapviews.py` does.
- `changes_sheets.py` draws every picture the mod replaces beside the game's (`build/changes/`): useful for the morning
  report.

## 7. In the morning: hand-over

1. **A new version, v0.13**, written up in `deco_ui/docs/VERSIONS.md` (what each screen does, what is assumed),
   `deco_ui/valsora_deco_ui/README.txt` (its "Things to check" for the author, in game), `deco_ui/CLAUDE.md` (sections
   1 and 10, and the project map for new tools), the root `CLAUDE.md`'s Deco UI line, `docs/HISTORY.md` (an entry at
   the top) and `docs/PROBLEM_LOG.md` (every problem, its cause and its fix).
2. **The zip:** `dist/valsora_test.zip` rebuilt with "all checks passed", committed and pushed.
3. **A short report in the chat:**
   - what changed, screen by screen, with each screen's commit (to revert it);
   - the previews, sent and not committed when they show the game's art;
   - the icon proposals waiting for the author's yes;
   - what you couldn't do, and why;
   - the install steps:
     1. Delete `mod/valsora_test/` and `mod/valsora_test.mod`.
     2. Unzip `dist/valsora_test.zip` into `mod/`; it contains both.
     3. Launch with `-debug`.
   - Ask for screenshots and `error.log` of the new screens (`Documents/Paradox Interactive/Hearts of Iron IV/logs/`;
     the author's Documents sits under OneDrive).
