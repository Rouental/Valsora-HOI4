# The Vale of Reibonne: a teaser

The author, 2026-10-22: "could you create a sort of teaser image for the Vale of Reibonne, showing the flag and leader of
each nation, maybe in front of the map?"

`vale_of_reibonne.png` (1920 x 1080): the eight nations of the second start, the Association of Reibonnaise States, on
the map as the build has them (their colours, Rouental's fief states as faint lines, the rivers, the neighbours in grey),
each one's flag pinned on its land (Rouental's on Rêverie), and a card a nation down either side: its ruler's portrait,
its flag, its name, its ruler and its formal name. Rouental and the three nearest it are on the left; the four of the
north-east, north to south, are on the right.

- The rulers are the Gazetteer's (the export of 2026-10-22) and Roland II Cahun; Guedelon's says "The Council of
  Seven", the author's word that day, where its page still says "The Council of Six"; its portrait is the Conseil des
  Sept's seal.
- Everything in it is the author's and their friends' (the map, the flags, the portraits) or the mod's own fonts (Federo
  and Josefin Sans, OFL): nothing of the base game's, so it is committed.
- The layout, the colours and the wording of the title and the footer are Claude's.

**The backdrop test** (the author, 2026-10-22: "As a test, redo the teaser, but give each leader portrait a consistent
gradient background like vanilla portraits. Or maybe just a blank background."): the same teaser with every ruler cut out
of their picture (rembg's `isnet-general-use` model, the cutouts kept in the git-ignored `work/teaser_cut/`; Guedelon's
seal is its own cutout) and put on one backdrop:
- `vale_of_reibonne_vanilla_backdrop.png`: a gradient in the colours of the base game's portraits (sampled from them,
  nothing of theirs copied): pale cream at the top, olive grey low down, a little lighter round the head;
- `vale_of_reibonne_plain_backdrop.png`: one flat slate, the cards' own colour lifted a little.

The cut keeps what stands in front of a ruler: Selgrave's microphone and the papers on her desk are still there.

After a build (`pip install rembg onnxruntime` for the backdrops; the model downloads itself the first time):

    CHROMIUM_PATH=/opt/pw-browsers/chromium python3 dist/teasers/vale_of_reibonne/make.py [photo] [vanilla] [plain]
