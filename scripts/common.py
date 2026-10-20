"""Settings shared by the pipeline scripts."""

# Game map size. HOI4 needs both sides to be multiples of 256 and crashes above
# roughly 13.24M pixels in total; 5120x2560 = 13,107,200 is the largest 2:1 map
# under that cap (the author's canvas is 2:1 too).
MAP_W, MAP_H = 5120, 2560

# Output pixels per source (.pdn) pixel for every continent. A straight fit of the
# 14000-wide source into 5120 would be 0.366; 0.375 draws each continent a little
# larger relative to the frame than the source does, and ~28% wider than the previous
# 5632x2048 build (0.293). At 0.38 the gaps between continents drop to ~91 px.
SCALE = 0.375

# Minimum open water between two different continents, in output pixels, and the
# empty band kept along the top and bottom edges.
MIN_GAP = 100
MARGIN_Y = 70
# Land stays at least this far from the wrap seam at x = 0 (no province may cross it).
SEAM_MARGIN = 8

# Continent blocks, in the order used by work/block_full.npy. Nonscio and Araseos
# move as one block: the Aikos / Midtierre archipelago ties them together.
BLOCKS = ["WEST", "AISLADA", "SOLITAS", "YASTREOVAKIA", "USNISTAN", "ORIENTALIS"]

# HOI4 continents (map/continent.txt), in order: definition.csv uses index + 1.
CONTINENTS = ["nonscio", "araseos", "aislada", "solitas", "yastreovakia", "usnistan", "orientalis"]
# Countries: tag, name, adjective, colour. The first seven are the placeholders, one
# per continent, keyed by continent.
COUNTRIES = {
    "nonscio": ("NSC", "Nonscio", "Nonscian", (216, 84, 84)),
    "araseos": ("ARS", "Araseos", "Araseosi", (116, 152, 206)),
    # Merlovich, the Aislada placeholder built out by the author's friend (2026-10-05); the
    # colour is the .pdn's paint, its map colour is nations.DISPLAY_COLOUR
    "aislada": ("AIS", "Merlovich", "Merlovian", (70, 170, 70)),
    "solitas": ("SLT", "Solitas", "Solitan", (214, 110, 214)),
    "yastreovakia": ("YAS", "Yastreovakia", "Yastreovakian", (96, 190, 150)),
    "usnistan": ("USN", "Usnistan", "Usnistani", (184, 172, 100)),
    "orientalis": ("ORI", "Orientalis", "Orientalian", (236, 160, 70)),
    # real countries drawn by the author (tags checked against vanilla's country_tags)
    "rouental": ("ROU", "Rouental", "Rouentaise", (54, 106, 64)),
    "seigne": ("SGN", "Seigne", "Seignois", (240, 240, 240)),
    "evriches": ("EVR", "Evriches", "Evrichois", (240, 208, 64)),
    "hollier": ("HLR", "Hollier", "Hollierois", (185, 53, 52)),
    "selgrave": ("SGV", "Selgrave", "Selgravian", (112, 16, 32)),
    "lustiana": ("LST", "Lustiana", "Lustianan", (28, 28, 28)),
    "lanzerac": ("LZC", "Lanzerac", "Lanzeracois", (145, 58, 106)),  # the flag's purple (dark gold until 2026-10-09)
    "guedelon": ("GDN", "Guedelon", "Guedelonnais", (7, 76, 130)),
    "cardonia": ("CRD", "Cardonia", "Cardonian", (84, 28, 120)),
    # 2026-09-30, south-west of Rouental; a placeholder nation (author), first called
    # Linterre, renamed Placeholdros on 2026-10-01
    "romanoddle": ("RMD", "Romanoddle", "Romanoddlian", (46, 139, 150)),
    "selto": ("STO", "Selto", "Seltan", (214, 120, 40)),
    "linterre": ("LNT", "Placeholdaire", "Placeholdairien", (190, 150, 200)),  # Placeholdros until 2026-10-07
    # 2026-09-30, south of Romanoddle and Selto; all Portuguese (author). Estande's
    # colour is the red of its flag (author: the green blended with Rouental); the rest are Claude's picks
    "rastava": ("RST", "Rastava", "Rastavan", (184, 160, 72)),
    "volinovia": ("VLN", "Volinovia", "Volinovian", (70, 100, 170)),
    "estande": ("ESD", "Estande", "Estandese", (153, 0, 0)),
    "coraliza": ("CRZ", "Coraliza", "Coralizan", (240, 122, 92)),
    "placeholdria": ("PLH", "Vultuca", "Vultucan", (238, 196, 222)),  # Placeholdria until 2026-10-07
    # 2026-10-01, east of Estande: Illiricium (map name "Senatorial Illiricium", the
    # author's), its Bleacherist republics, and Royalist Illiricium on its island.
    # Colours and adjectives are Claude's picks; Illiricium's blue is its flag's, and its
    # Bleacherist puppets are shades of blue (author, 2026-10-01)
    "illiricium": ("ILR", "Republican Illiricium", "Illirician", (32, 44, 140)),  # "Senatorial" until 2026-10-02
    "cotefer": ("CTF", "Côtefer", "Côteferan", (70, 150, 190)),
    "entroterra": ("ETR", "Entroterra", "Entroterran", (140, 185, 235)),
    "mezzogiorno": ("MZG", "Mezzogiorno", "Mezzogiornese", (60, 105, 190)),
    "k_illiricium": ("KIL", "Royalist Illiricium", "Illirician", (255, 255, 255)),  # white (author, 2026-10-01)
    # 2026-10-01, the author's, east of Selgrave and Hollier. Kurikia's navy is its
    # flag's; Fraxhemark's flag red would vanish next to Hollier, so raspberry (Claude's)
    "kurikia": ("KRK", "Kurikia", "Kurikian", (34, 62, 96)),
    "fraxhemark": ("FRX", "Fraxhemark", "Fraxhemarkish", (200, 60, 110)),
    # 2026-10-02: the factions of the Rouentaise civil war, which own nothing at the
    # start and are released when the Prince is executed (nations.CIVIL_WAR). Names are
    # the author's; adjectives and colours Claude's
    "brillagne": ("BRL", "Brillagne", "Brillagnais", (225, 190, 70)),
    "crepuscule": ("CRP", "Crépuscule", "Crépusculaire", (75, 72, 85)),
    "reliette": ("RLT", "Reliette", "Reliettois", (175, 45, 55)),
    "marches": ("MRC", "The Marches", "Marcher", (85, 85, 115)),
    "loyal_army": ("RLA", "HMMLA", "Rouentaise", (40, 95, 55)),  # author's map name
    "vair": ("VAI", "Vair", "Vairois", (15, 105, 150)),
    # 2026-10-02, the author's, inside Fraxhemark around its lake; colour Claude's
    "locus": ("LCF", "Locus", "Locan", (230, 100, 30)),
    "faithful": ("FTH", "The Faithful", "Faithful", (240, 190, 80)),
    # 2026-10-04, south of Estande (the author's names; colours and adjectives Claude's,
    # from the flags where there is one)
    "san_sierra": ("SSA", "San Sierra", "San Sierran", (250, 125, 40)),  # flag orange
    "anglost": ("AGL", "Anglost", "Anglostian", (22, 48, 92)),           # flag navy
    "normania": ("NRM", "Normania", "Normanian", (45, 90, 140)),         # Anglost's dominion
    "guardana": ("GRD", "Malvekia", "Malvekian", (205, 175, 70)),  # Guardana until 2026-10-05
    "n_pollana": ("NPL", "North Pollana", "Pollanan", (190, 30, 45)),
    "s_pollana": ("SPL", "South Pollana", "South Pollanan", (45, 150, 145)),
    "dremaur": ("DRM", "Dremaur", "Dremauri", (115, 5, 5)),            # flag maroon
    # 2026-10-04, later: Nonscio's west (Wersh, Troc, Cascadia), between Anglost and San
    # Sierra (Sicilianzo, Danelaw), inside Fraxhemark (Thorian); colours Claude's
    "wersh": ("WRS", "Wersh", "Wershian", (25, 35, 110)),               # dark blue (author)
    "troc": ("TRC", "Troc", "Trocian", (170, 25, 25)),                   # red (author)
    "cascadia": ("CSC", "Cascadia", "Cascadian", (15, 75, 40)),           # dark green (author)
    "sicilianzo": ("SCZ", "Sicilianzo", "Sicilianzan", (228, 228, 222)),  # white (author)
    "danelaw": ("DNL", "Danelaw", "Danelawan", (0, 106, 167)),           # Sweden's blue for now
    "thorian": ("THD", "Thorian Dynamics", "Thorian", (95, 95, 100)),
    # 2026-10-05, the author's friend's sessions: Hoalepa on two islands north-west of
    # Solitas, and five nations in the land south of Solitas (the author's paint)
    "hoalepa": ("HOA", "Hoalepa", "Hoalepan", (216, 150, 170)),
    "arvorenia": ("ARV", "Arvorenia", "Arovian", (18, 94, 42)),
    "atrocha": ("ATR", "Atrocha", "Atrochan", (225, 20, 20)),
    # removed from the map on 2026-10-13 (author: "eventually it will be readded as a
    # formable"), so it owns nothing and is left out of the mod
    "us_solitas": ("USS", "United States of Solitas", "American", (140, 60, 190)),
    # its flag's navy, a little lighter (author, 2026-10-13: green until then, too close
    # to Arvorenia's and Las Anod's)
    "silvamar": ("SVM", "Silvamar", "Silvestran", (10, 30, 140)),
    "ponchomagnifico": ("PNC", "Ponchomagnifico", "Ponchomagnifico", (255, 204, 0)),
    # 2026-10-05, later (the author's names, governments and formal names; colours and
    # adjectives Claude's, from the flags where there is one): the south-west of Araseos
    # with its islands, the Garfield islands south of Malvekia, Devlon's islet off
    # Fraxhemark
    "terrabis_seran": ("TBS", "Terrabis-Seran", "Terrabian", (140, 55, 105)),  # flag plum
    "vineta": ("VNT", "Vineta", "Vinetan", (165, 0, 25)),                       # flag red
    "harwick": ("HWK", "Harwick", "Harwicker", (215, 95, 85)),                  # Vineta's vassal
    "gaellia": ("GAE", "Gaellia", "Gaellic", (35, 130, 65)),
    "kilkire": ("KKB", "Kilkire-Foraois", "Kilkiran", (215, 135, 45)),  # author, 2026-10-05
    "garfield": ("GFR", "Garfield Republics", "Garfieldian", (45, 35, 35)),     # flag black
    "devlon": ("DVL", "Devlon", "Devlonian", (150, 160, 70)),
    # 2026-10-05, later: nations Rouental can release (nations.RELEASABLE; the author's
    # names and flags, colours from the flags, Claude's)
    "carcarelle": ("CRL", "Carcarelle", "Carcarellois", (150, 70, 130)),          # bells on plum
    "mountains": ("MTN", "Duchy of the Mountains", "Montagnard", (200, 155, 60)),  # gold chevrons
    "oriflamme": ("ORF", "Oriflamme", "Oriflammois", (205, 85, 45)),              # flame red
    "ghessone": ("GHS", "Ghessone", "Ghessonais", (60, 150, 60)),                 # green
    "riverraine": ("RVR", "Riverraine", "Riverrain", (30, 120, 120)),             # waves
    "piscary": ("PSC", "Piscary", "Piscarien", (70, 130, 190)),                   # scales
    # 2026-10-07, later (author): five more; colours from the flags (Claude's)
    "east_alliance": ("AOE", "Alliance of the East", "Eastern", (115, 145, 60)),
    "recolt": ("RCL", "Recolt", "Recoltois", (230, 180, 70)),        # wheat gold
    "sangterre": ("SGT", "Sangterre", "Sangterrois", (150, 30, 45)),  # blood drops
    "kove": ("KOV", "Kové", "Kovéen", (20, 100, 140)),                # blue
    "hevique": ("HVQ", "Hevique", "Hevicois", (190, 55, 45)),        # red
    "serie": ("SRE", "Serie", "Serien", (70, 70, 75)),               # charcoal field
    # 2026-10-09, later (author): Rouental's islets off Solitas; the flag's plum, a shade
    # off Lanzerac's, which is the same purple
    "oriental_territories": ("ORT", "Oriental Territories", "Oriental", (156, 70, 118)),
    # 2026-10-05, later: San Sierra's island state 1 (author); colour, adjective Claude's
    "holy_see": ("SEE", "Holy See", "Papal", (245, 225, 120)),                    # flag gold
    # 2026-10-07 (the author's names, governments and formal names; colours from the
    # flags where there is one, otherwise Claude's, as are the adjectives)
    "merlgould": ("MGD", "Merlgould", "Merlgouldian", (120, 150, 90)),
    "transcainia": ("TCN", "Transcainia", "Transcainian", (150, 110, 170)),
    "peatiktist": ("PTK", "Peatiktist", "Peatiktist", (90, 120, 110)),
    "serentia": ("SRN", "Serentia", "Serentian", (200, 40, 40)),                  # flag red
    "leithanien": ("LTH", "Leithanien", "Leithanian", (30, 90, 160)),             # flag blue
    "grossloewenburg": ("GLB", "Großlöwenburg", "Großlöwenburger", (235, 175, 70)),  # flag gold
    "kampf": ("KPF", "Kampfian Empire", "Kampfian", (110, 110, 60)),
    "dumas": ("DUM", "Dumas", "Dumasian", (235, 230, 200)),
    "terreich": ("TUP", "Terreich und Preußen", "Terreichisch", (60, 50, 85)),    # flag slate
    "schteirmark": ("STM", "Schteirmark", "Schteirmärkisch", (160, 90, 60)),
    "daravon": ("DRV", "Daravon", "Daravonian", (180, 20, 30)),
    "eschland": ("ESC", "Artzen", "Artzener", (205, 75, 75)),          # Eschland until 2026-10-09
    "hwitland": ("HWT", "Scealand", "Scealändisch", (150, 30, 60)),    # Hwitland until 2026-10-09
    "someriania": ("SMR", "Someriania", "Somerianian", (210, 90, 40)),
    "krionik": ("KRI", "Krionik", "Kriosnik", (60, 90, 60)),
    "gorbastan": ("GOB", "Gorbastan", "Gorbastani", (200, 160, 90)),
    "zukchiva": ("ZUK", "Zukchiva", "Zukchivan", (90, 160, 170)),
    "sminishia": ("SMN", "Sminishia", "Sminishian", (210, 110, 150)),
    # off the map since 2026-10-15 (author: "should remain in the code, but be off the map for now"); its
    # land and paint are Vilna's, so it has an unused colour from its flag
    "russovichia": ("RSV", "Russovichia", "Russovich", (153, 47, 45)),
    "ostaria": ("OST", "Ostaria", "Ostarian", (230, 200, 30)),                    # flag yellow
    # 2026-10-08 (the author's names, governments and formal names; tags, colours and
    # adjectives Claude's; Tethia's colour from its flag)
    "belekria": ("BLK", "Belekria", "Belekrian", (200, 62, 44)),
    "tethia": ("TTH", "Tethia", "Tethian", (26, 84, 178)),             # flag blue
    "merigo": ("MRG", "Merikaan", "Merikaans", (72, 150, 124)),  # Merigo until 2026-10-08, later
    "zwintern": ("ZWT", "Zwintern", "Zwinterner", (96, 104, 124)),
    "ostercoirasreich": ("OCR", "Ostercoirasreich", "Ostercoirasreicher", (186, 156, 82)),
    "mahina": ("MAH", "Mahina", "Mahinan", (84, 178, 196)),
    "ungar": ("UNG", "Ungar", "Ungarian", (150, 120, 70)),
    # 2026-10-09 (the author's names, governments and formal names; tags, colours and
    # adjectives Claude's; Belka's colour from its flag): Yastreovakia's north-east,
    # West Sminishia out of Sminishia, Skillia's island and Tenkyoku's in Orientalis
    "belka": ("BKA", "Belka", "Belkan", (40, 40, 40)),                 # flag black
    "w_sminishia": ("WSM", "West Sminishia", "West Sminishian", (176, 52, 96)),
    "sanada": ("SNA", "Sanada", "Sanadan", (166, 88, 58)),
    "kamyachyn": ("KMY", "Kamyachyn", "Kamyachynian", (96, 170, 96)),
    "volstokn": ("VSK", "Volstokn", "Volstoknian", (56, 104, 168)),
    "brethren": ("BRT", "Brethren", "Brethren", (226, 220, 236)),
    "rysny": ("RYS", "Ryśny", "Ryśnian", (190, 40, 64)),
    "pakitsk": ("PKT", "Pakitsk", "Pakitskian", (156, 148, 76)),
    "kieska": ("KSK", "Kieska", "Kieskan", (128, 84, 160)),
    "zoluzeme": ("ZLZ", "Zoluzeme", "Zoluzemian", (220, 180, 60)),
    # since 2026-10-15 (author) on Russovichia's land, with its paint (the new flag's field is crimson);
    # its old land is Placeholdgrad's
    "vilna": ("VIL", "Vilna", "Vilnian", (140, 0, 0)),
    "sombor": ("SMB", "Sombor", "Somborian", (236, 132, 52)),
    "skillia": ("SKL", "Skillia", "Skillian", (226, 74, 74)),
    "tenkyoku": ("TKY", "Tenkyoku", "Tenkyoku", (176, 22, 52)),
    # 2026-10-11 (the author's names, governments and formal names; tags, colours and
    # adjectives Claude's): Orientalis outlined, and Gorduchai's island off it
    "gorduchai": ("GOR", "Gorduchai", "Gorduchaian", (236, 224, 168)),
    "sarkis": ("SRK", "Sarkis", "Sarkisian", (104, 108, 120)),
    "wanea": ("WAN", "Wanea", "Wanean", (110, 160, 60)),
    "qingou": ("QNG", "Qinguo", "Qinguoese", (40, 120, 200)),  # "Qingou" until 2026-10-13 (author)
    "xue": ("XUE", "Xuè", "Xuè", (100, 190, 170)),
    "hulinguo": ("HLG", "Hulinguo", "Hulinguo", (240, 140, 110)),
    "assoc_cities": ("ASC", "Associated Cities", "Dahu-Jinhu", (250, 220, 120)),
    "haidao": ("HDO", "Haidao", "Haidao", (150, 220, 230)),
    "kuran": ("KRN", "Kuran", "Kurani", (128, 52, 40)),
    "daihai": ("DHI", "Daihai", "Daihai", (210, 130, 200)),
    "tsuruma": ("TSU", "Tsuruma", "Tsuruman", (230, 140, 160)),
    "charity": ("CRT", "Charity", "Charitian", (240, 210, 20)),
    "kianhua": ("KNH", "Kianhua", "Kianhuan", (150, 200, 110)),
    "red_path": ("RDP", "Red Path", "Red Path", (222, 40, 40)),
    "kaizan": ("KZN", "Kaizan", "Kaizanese", (180, 150, 220)),
    "sho": ("SHO", "Sho", "Sho", (226, 84, 120)),
    "uyizar": ("UYZ", "Uyizar", "Uyizari", (160, 120, 80)),
    "yatar": ("YTR", "Yatar", "Yatari", (120, 60, 90)),
    "myehn": ("MYH", "Myehn", "Myehnese", (30, 110, 120)),
    "plaija": ("PLJ", "Plaija", "Plaijan", (205, 70, 30)),
    "pinzahao": ("PZH", "Pinzahao", "Pinzahao", (240, 170, 200)),
    "ganden": ("GND", "Ganden", "Gandenese", (110, 80, 50)),
    "arpino": ("ARP", "Arpino", "Arpinese", (52, 150, 52)),
    "shinnokawa": ("SHN", "Shinnokawa", "Shinnokawan", (250, 90, 70)),  # added later that day
    # 2026-10-12 (the author's names, governments and formal names; tags, colours and
    # adjectives Claude's): Usnistan outlined, Orientalis' south-west (Chineasia, Felter)
    # and Sennheiser in Yastreovakia's south-west
    "cultists": ("CUL", "Cultists", "Cultist", (20, 92, 86)),
    "arcadia": ("ARC", "Arcadia", "Arcadian", (104, 104, 158)),
    "muqadasa": ("MQS", "Muqadasa Salamat", "Muqadasan", (20, 158, 98)),
    "sarza": ("SRZ", "Sarza", "Sarzan", (122, 38, 110)),
    "leviathan": ("LEV", "Leviathan", "Leviathanian", (38, 62, 122)),
    "kyras": ("KYS", "Kyras", "Kyran", (236, 146, 86)),
    "hulya": ("HLY", "Hulya", "Hulyan", (212, 212, 122)),
    "levantinin": ("LVN", "Levantinin", "Levantine", (218, 206, 188)),
    "mustawi": ("MST", "Mustawi", "Mustawi", (146, 128, 38)),
    "almohavid": ("AMH", "Almohavid", "Almohavid", (212, 20, 62)),
    "port_almohavid": ("PAM", "Port Almohavid", "Port Almohavid", (254, 188, 44)),
    "mekele": ("MKL", "Mekele", "Mekelean", (86, 20, 20)),
    "kalaistan": ("KLS", "Kalaistan", "Kalaistani", (56, 80, 32)),
    "al_radiyaa": ("RDY", "Al-Radiyaa", "Radiyaan", (38, 164, 146)),
    "al_khabid": ("KHB", "Al-Khabid", "Khabidi", (188, 92, 20)),
    "humanist": ("HMN", "Humanist State", "Humanist", (104, 86, 104)),
    "s_usnistan": ("SUS", "South Usnistan", "South Usnistani", (98, 128, 200)),
    "royabad": ("RYB", "Royabad", "Royabadi", (182, 50, 80)),
    "koronista": ("KRS", "Koronista", "Koronistani", (218, 194, 104)),
    "n_koronista": ("NKR", "North Koronista", "North Koronistani", (116, 68, 38)),
    "zanzimibia": ("ZNZ", "Zanzimibia", "Zanzimibian", (254, 146, 182)),
    "utopian": ("UTP", "Utopian Republic", "Utopian", (92, 170, 224)),
    "soloriania": ("SLN", "Soloriania", "Solorianois", (230, 218, 92)),
    "hohenzburg": ("HZB", "Hohenzburg", "Hohenzburger", (74, 98, 20)),
    "nuevo_paraiso": ("NPR", "New Paradise", "New Paradisian", (182, 122, 224)),  # Nuevo Paraíso until 2026-10-13
    "arklen": ("ARK", "Arklen", "Arklener", (92, 152, 92)),
    "isigoriya": ("ISG", "Isigoriya", "Isigoriyan", (98, 80, 62)),
    "kizimwe": ("KZW", "Kizimwe", "Kizimwean", (86, 50, 122)),
    "lafari": ("LFR", "Lafari", "Lafari", (158, 50, 32)),
    "meddacah": ("MDC", "Meddacah", "Meddacan", (38, 56, 62)),
    "khaleeya": ("KHY", "Khaleeya", "Khaleeyan", (152, 146, 194)),
    "chineasia": ("CNA", "Chineasia", "Chineasian", (194, 26, 80)),
    "sennheiser": ("SNH", "Sennheiser", "Sennheiser", (62, 80, 158)),
    "felter": ("FLT", "Felter", "Felterian", (254, 158, 62)),
    "solaria": ("SLA", "Solaria", "Solarian", (248, 230, 146)),  # on the map, named later that day
    # 2026-10-13, Solitas outlined (the author's names; tags, adjectives and colours
    # Claude's, the colours from the flags where there is one)
    "recaxa": ("REC", "Recaxa", "Recaxan", (102, 0, 153)),               # flag purple
    "surredia": ("SRD", "Surredia", "Surredian", (25, 75, 155)),         # flag blue, lighter
    "arovannea": ("AVN", "Arovannea", "Arovannean", (45, 155, 150)),
    "avesaria": ("AVE", "Avesária", "Avesárian", (135, 185, 235)),
    "abalon": ("ABL", "Abalón", "Abalonese", (215, 130, 45)),
    "texaria": ("TEX", "Texaria", "Texarian", (168, 46, 37)),            # flag red
    "gran_yucanoa": ("GYC", "Gran Yucanoa", "Yucanoan", (50, 60, 130)),  # flag navy, lighter
    "las_anod": ("LAN", "Las Anod", "Anodian", (120, 200, 90)),
    "brome": ("BRO", "Bromé", "Bromean", (150, 20, 50)),
    # 2026-10-13, later (author): the land labelled Santa Fe; gold, so it stands out from
    # Bromé's crimson and Atrocha's red beside it
    "santa_fe": ("SFE", "Santa Fe", "Santa Fean", (230, 175, 35)),
    # 2026-10-15 (author): Vilna's old land, with its old flag and ideology and its paint; the adjective
    # is Claude's
    "placeholdgrad": ("PHG", "Placeholdgrad", "Placeholdgradian", (40, 140, 90)),
    # 2026-10-17 (the author's names, painted on the Subregions layer; tags, adjectives and colours Claude's, the
    # colours from the flags where there is one): Belekria's constituent republics (Tethia, already one, above) and
    # Krionik's principalities, nations that can be released (nations.SUBREGIONS)
    "drakonogolovnik": ("DRK", "Drakonogolovnik", "Drakonogolovnikan", (95, 75, 150)),
    "staraya_belekria": ("STB", "Staraya Belekria", "Old Belekrian", (150, 35, 35)),
    "sredneestvo": ("SDE", "Sredneestvo", "Sredneestvan", (225, 160, 120)),
    "severntochka": ("SVT", "Severntochka", "Severntochkan", (110, 150, 70)),
    "serayachasy": ("SRY", "Serayachasy", "Serayachasian", (70, 150, 200)),
    "kalnsfereta": ("KLF", "Kalnsfereta", "Kalnsferetan", (200, 100, 30)),
    "belayosen": ("BLY", "Belayosen", "Belayosenian", (225, 205, 110)),
    "krasnoeporte": ("KSP", "Krasnoeporte", "Krasnoeportean", (110, 70, 55)),
    "zastava": ("ZST", "Zastava", "Zastavan", (22, 100, 180)),               # flag blue
    "crvenognjiste": ("CRV", "Crvenognjište", "Crvenognjištan", (10, 120, 110)),  # flag teal, lighter: Krionik's green
    "mylostrva": ("MYL", "Mylostrva", "Mylostrvan", (215, 170, 25)),          # flag gold: its navy is Sennheiser's blue
    # 2026-10-19, the author's Subregions and Subnames (names theirs; tags, adjectives and colours Claude's guesses, the
    # colours from the paint, softened): Krionik's other realms, the city of Sangrád, its three overseas ports
    # (Sennheiser's Sisterhood, of the same day, removed 2026-10-20: the author)
    "belska": ("BLS", "Belska", "Belskan", (212, 212, 202)),
    "koroletz": ("KRZ", "Koroletz", "Koroletzian", (78, 78, 82)),
    "targoviste": ("TGV", "Targoviste", "Targovistean", (44, 134, 214)),
    "kosavichy": ("KSV", "Kosavichy", "Kosavichian", (62, 182, 188)),
    "lagrad": ("LGR", "Lagrád", "Lagrádian", (226, 204, 122)),
    # Visokagorod, Sangrád until 2026-10-20 (author: "Rename Sangrad to Visokagorod"); its adjective Claude's guess
    "visokagorod": ("SGD", "Visokagorod", "Visokagorodian", (84, 44, 192)),
    "port_nyasha": ("PNY", "Port Nyasha", "Nyashan", (198, 42, 104)),
    "port_vostok": ("PVS", "Port Vostok", "Vostokian", (196, 198, 214)),
    "port_grazda": ("PGZ", "Port Grazda", "Grazdan", (222, 186, 44)),
    # 2026-10-19 (the author: "Xugang should start out as a vassal of Terreich"): Terreich's exclave on the eastern
    # continent, its own nation, Terreich's puppet; adjective and colour Claude's guesses (Terreich's slate, lighter)
    "xugang": ("XUG", "Xugang", "Xugangese", (118, 96, 150)),
}
# The placeholder countries, one per continent, are the recommended starts in the
# bookmark; the rest are playable but not listed there.
PLACEHOLDERS = CONTINENTS

# Graphical terrain: terrain.bmp palette index -> terrain type (vanilla 1.19.3
# common/terrain/00_terrain.txt). The index's palette colour is what the Terrain layer
# of "HOI4 Mod Map.pdn" uses. Index 14 marks lakes there; the game gets 15 for both.
TERRAIN_TYPES = {0: "plains", 1: "forest", 2: "hills", 3: "desert", 4: "forest", 5: "plains",
                 6: "mountain", 7: "desert", 8: "desert", 9: "marsh", 10: "mountain",
                 11: "mountain", 12: "desert", 13: "urban", 14: "lakes", 15: "ocean",
                 16: "mountain", 17: "hills", 18: "mountain", 19: "plains", 20: "mountain",
                 21: "jungle", 22: "jungle", 27: "mountain", 31: "mountain"}
TERRAIN_OCEAN, TERRAIN_LAKE, TERRAIN_PLAINS = 15, 14, 0

# Their colours on the Continents layer of "HOI4 Mod Map.pdn".
CONT_COLOURS = [(216, 84, 84), (116, 152, 206), (70, 170, 70), (214, 110, 214),
                (96, 190, 150), (184, 172, 100), (236, 160, 70)]

# Smallest province HOI4 accepts without complaint is 8 px; 16 leaves headroom.
MIN_PROVINCE = 16
# Enclosed water smaller than this is filled in as land rather than made a lake.
MIN_LAKE = 64

# Placeholder province bricks (pixels). Map width must divide by each of them.
LAND_CELL = 32
SEA_CELL = 128
LAKE_CELL = 48
# A piece of a brick smaller than this fraction of a full brick is merged into its
# neighbour, so coastlines don't leave slivers.
MIN_FRACTION = 0.25
# HOI4 reports a province wider or taller than 1/8 of the map ("TOO LARGE BOX").
MAX_BOX = 1 / 8

# States: land provinces grouped on a grid of this many pixels (about 3x3 land bricks).
STATE_CELL = 96
# Island states with fewer provinces join the nearest state within this many pixels.
MIN_STATE_PROVINCES = 3
ISLAND_REACH = 160
# Strategic regions: states grouped on this grid; seas on their own grid.
REGION_CELL = 384
SEA_REGION_CELL = 512
MIN_SEA_REGION_PROVINCES = 4

# Mod folder name inside Documents/Paradox Interactive/Hearts of Iron IV/mod/, and the
# name the launcher shows. The folder name matches the previous test build's.
MOD_DIR_NAME = "valsora_test"
MOD_NAME = "Valsora (test map)"
# Where the mod is built: build/valsora_test/ and build/valsora_test.mod. VALSORA_BUILD gives another folder, so a
# test version (scripts/build_flags15.sh) is built beside the mod instead of over it.
import os as _os
from pathlib import Path as _Path
BUILD = _Path(_os.environ.get("VALSORA_BUILD") or "build")

# The Valsora Deco UI (deco_ui/, the author's art deco interface) is part of the mod since 2026-10-14 (author:
# "simplify things to only have the one install", and they may want the game's own interface back one day).
# True: scripts/deco_ui.py copies it into the build, and the minimap and start date picture are drawn in its
# style. False: the game's own interface, Valsora's parchment minimap, and none of the Deco UI's files.
DECO_UI = True

# The size of the game's large flags (the top bar's, the diplomacy screen's ...): HOI4's 82 x 52 times FLAG_SCALE.
# A test version with larger flags (the author, 2026-10-15: "Maybe make a test version of the mod with the flag at
# 1.5?") is built with VALSORA_FLAG_SCALE=1.5 (docs/HD_FLAGS_TEST.md); the mod itself stays at 1.
FLAG_SCALE = float(_os.environ.get("VALSORA_FLAG_SCALE", "1"))
FLAG_SIZE = (round(82 * FLAG_SCALE), round(52 * FLAG_SCALE))
