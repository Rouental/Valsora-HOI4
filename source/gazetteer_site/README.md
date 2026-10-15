# The Gazetteer's web site

What `scripts/gazetteer_site.py` puts beside the page (`scripts/gazetteer.html`) to make the
Gazetteer's web site, served by GitHub Pages from the `gh-pages` branch, with the atlas kept
in the author's Firebase project (`valsora-hoi4`). See `docs/GAZETTEER.md`.

- `firebase-config.json`: the project's web settings, from its console (Project settings ›
  Your apps). They are not secret: every Firebase web page carries them, and the rules are
  what protect the data.
- `firestore.rules`: the database's access rules. The author pastes them into the console
  (Firestore Database › Rules), with their Google address in place of `OWNER_EMAIL`. Change
  them here first, then paste again.
- `firebase-sdk-12.19.0.js`: the parts of Google's Firebase web SDK the page uses
  (`firebase-sdk-entry.js`), bundled into one module so the site needs no other server:
  `npm install firebase@12.19.0 esbuild` and
  `esbuild firebase-sdk-entry.js --bundle --format=esm --minify --target=es2020 --legal-comments=eof`.
  Firebase's SDK is Apache-2.0 licensed; its notices are at the end of the file.
