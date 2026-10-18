# The motto flag: "A safe haven amid the storm"

The author, 2026-10-18: "Please make a flag with the following text in calligraphic arabic on an indigo background:
ملاذٌ آمنٌ / في خضمِّ العاصفة" (*malādhun āminun / fī khiḍammi al-ʿāṣifa*, "a safe haven / amid the storm").

Not in the mod yet: the author hasn't said whose flag it is. Four of Google Fonts' Arabic hands, each in white and in
gold, on indigo (46, 39, 117), at 1640 x 1040 (82:52, the game's flag shape, twenty times over); `sheet.png` shows them
all with the game's three flag sizes beside each.

| file | hand |
|---|---|
| `ruqaa_*.png` | Aref Ruqaa: Ruq'ah, the everyday calligraphic hand (Claude's pick: the most calligraphic, and it fills the flag best) |
| `naskh_*.png` | Amiri: Naskh, the classic book hand |
| `nastaliq_*.png` | Gulzar: Nastaliq, the hanging Persian hand |
| `kufi_*.png` | Reem Kufi: Kufi, angular |

Every vowel mark of the author's text is kept (the tanwīn of both words of the first line, the shadda and kasra of
خضمِّ). `make.py` draws them again (Chromium shapes the Arabic; the fonts, SIL Open Font License, are fetched into
`work/fonts/arabic/`). Once the author names the nation and the version, the chosen file becomes `source/flags/TAG.png`
(any size; the build shrinks it) and a layer in the flag file.
