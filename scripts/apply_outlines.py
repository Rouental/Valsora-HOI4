"""Turn outlines drawn on "HOI4 Mod Map.pdn" into states, provinces and countries.

The author draws 1-px lines on two layers:
    Borders              country borders
    Necessary Provinces  state borders inside a country (the layer name is historical)
Every patch of land enclosed by those lines becomes a state; patches over STATE_MAX px
are cut into several states that fill the same shape. Every state is cut into
provinces of about PROVINCE_AREA px, for a granular map. OWNERS names the country of
each patch by one pixel inside it; every other enclosed patch goes to DEFAULT_OWNER.

The script rewrites the Provinces, States, Countries and Strategic Regions layers of
the decoded .pdn (work/pdn_new) and saves the result as source/HOI4 Mod Map.pdn, using
the input file itself as the template. Land outside the outlines is untouched, except
that leftover slivers of cut placeholder provinces and states join a neighbour.

    python3 scripts/apply_outlines.py <input.pdn>
"""
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi
from skimage.measure import label as sklabel

from common import COUNTRIES, MAP_W as W, MAP_H as H, MIN_PROVINCE, PLACEHOLDERS
import organic
from writepdn import write_pdn

SRC = Path("work/pdn_outlines")  # the input .pdn, decoded here first
OUT = Path("source/HOI4 Mod Map.pdn")
# country borders and state lines; the author renamed them on 2026-10-01 ("Necessary
# Provinces" is now kept for province-level detail, not read here)
LINE_LAYERS = [("Necessary Borders", "Borders"), ("Necessary States",)]
OCEAN, LAKES = (8, 31, 130), (55, 90, 220)

# Who gets the newly outlined patches. Patches already painted in a real (non-
# placeholder) country's colour were done by an earlier run and are left alone, so
# each run only needs the new countries. (x, y) = a pixel inside a patch.
#
# 2026-09-29, Rouental and neighbours: DEFAULT_OWNER "rouental"; selgrave (859, 762),
# lanzerac (853, 781), lustiana (823, 786), evriches (797, 802), hollier (845, 815),
# seigne (811, 818), guedelon (748, 871); rouental exclaves (829, 765), (798, 792),
# (823, 803) and the lake island (811, 906), which has no outline.
# 2026-09-29, Cardonia north of Rouental: every new patch, plus the islands the
# author's References layer colours Cardonian (they have no outlines): (873, 630),
# (905, 593), (920, 548), (605, 646), (598, 726), (698, 536), (618, 549), (593, 562),
# (689, 580).
# 2026-09-30, Romanoddle, Selto and Linterre south-west of Rouental: DEFAULT_OWNER
# "linterre"; the islands are the ones the author's Names layer labels RO / LT.
# Afterwards (pdn_tools.py give) five Linterre states along the Piscary coast went to
# Selto, matching the author's older drawing (Notes layer), and the island at (300, 785)
# was cut off from Romanoddle's island by reopening its strait, as Nonscio's.
# Afterwards (pdn_tools.py give) five Linterre states along the Piscary coast went to
# Selto, matching the author's older drawing (Notes layer), and the island at (300, 785)
# was cut off from Romanoddle's island by reopening its strait, as Nonscio's.
# (config was: DEFAULT_OWNER "linterre"; romanoddle (350, 1000), (323, 835), (481, 829),
# (447, 807), (438, 813), (514, 822); selto (600, 965); linterre (559, 734), (556, 760),
# (532, 802).)
# 2026-09-30, second map: Rastava, Volinovia, Placeholdria, Estande and Coraliza south of
# Romanoddle and Selto, with the islands the author's Names layer labels ES / PC / RO.
# (config was: DEFAULT_OWNER "estande"; rastava (602, 1030); volinovia (527, 1085);
# placeholdria (417, 1157), (392, 1069), (364, 1081), (384, 1091), (323, 1104), (321, 1182),
# (323, 1199), (350, 1208); estande (635, 1165), (756, 933), (780, 924), (793, 935),
# (687, 971), (747, 1006), (760, 1037), (569, 1214), (533, 1229), (599, 1227), (582, 1242),
# (602, 1262); coraliza (440, 1231); romanoddle (270, 1113), (283, 1123), (219, 1135).)
# 2026-10-01: Illiricium and its Bleacherist republics east of Estande, Royalist
# Illiricium's island, and two islets off Solitas the author labelled ROU.
# (config was: DEFAULT_OWNER "illiricium"; illiricium (841, 1084); cotefer (803, 995);
# mezzogiorno (857, 1129); entroterra (802, 1176); k_illiricium (922, 1157); rouental
# (1716, 2010), (1728, 2019).)
# 2026-10-01, later: Kurikia and Fraxhemark east of Selgrave and Hollier.
# (config was: DEFAULT_OWNER "fraxhemark"; kurikia (1135, 740); fraxhemark (1000, 990).)
# 2026-10-02: the five islands north of Kurikia the author's Names layer labels KU.
# (config was: DEFAULT_OWNER "kurikia"; kurikia (952, 509), (929, 524), (957, 545),
# (937, 576), (952, 600).)
# 2026-10-02, later: Locus, outlined inside Fraxhemark around its lake; the rest of
# Fraxhemark is left alone (LEAVE) rather than re-cut.
# (config was: DEFAULT_OWNER "locus"; locus (990, 910).)
# 2026-10-04: seven nations south of Estande, and Aislada's state lines (the author drew
# them on Necessary Provinces by mistake; moved to Necessary States). Seeds are the
# author's Names labels (AN, SS) and the islands their pointer lines end on.
# (config was: DEFAULT_OWNER "aislada", and the OWNERS_0410 below.)
# 2026-10-04, later: Wersh, Troc, Cascadia (with the islands labelled CS) in Nonscio's
# west, Sicilianzo and Danelaw between Anglost and San Sierra, Thorian inside Fraxhemark.
# (config was: DEFAULT_OWNER "cascadia"; wersh (462, 684); troc (458, 560); cascadia (299, 724),
# (515, 437), (256, 492), (198, 558), (130, 631), (217, 637), (147, 692), (302, 779),
# (425, 790), (497, 779); sicilianzo (687, 1271); danelaw (733, 1400); thorian (1105, 1046).)
# 2026-10-05, later: Terrabis-Seran, Gaellia, Kilkire-Battania and Harwick in Araseos'
# south-west, Vineta's islands (VI) and Terrabis-Seran's (TS) off it, the Garfield
# islands (GR) south of Malvekia, Devlon's islet off Fraxhemark, two islets for Thorian
# (TD) and the islets the author's Names layer now labels CS. Seeds are the islands
# the labels sit on. San Sierra's new border with Sicilianzo is done separately
# (pdn_tools.py border san_sierra 700,1290) before regroup_states.py.
# (config of 2026-10-05, later; kept for reference)
# DEFAULT_OWNER = "terrabis_seran"
# OWNERS = {
#     "terrabis_seran": [(666, 1993), (214, 1997), (211, 2013), (241, 2030), (307, 2037),
#                        (303, 2046), (336, 2051), (1200, 955)],
#     "vineta": [(345, 2060), (312, 2107), (285, 2104), (222, 2129), (283, 2116), (328, 2129),
#                (313, 2155), (273, 2146), (258, 2150), (251, 2166), (277, 2160), (281, 2195),
#                (260, 2179)],
#     "gaellia": [(673, 2192)],
#     "kilkire": [(739, 2202)],
#     "harwick": [(734, 2329)],
#     # the islands, and the tip of Danelaw's eastern peninsula the author cut off for it
#     # (the "GR" written on Necessary Borders there was moved to Necessary Names)
#     "garfield": [(890, 1434), (923, 1393), (1000, 1465), (926, 1440), (977, 1469), (935, 1461),
#                  (935, 1505)],
#     "devlon": [(1028, 1145)],
#     "thorian": [(1219, 1074), (1142, 1176)],
#     "cascadia": [(479, 403), (277, 493), (174, 511), (208, 562), (203, 564), (151, 606),
#                  (218, 605), (172, 606), (166, 624), (68, 640), (150, 659), (233, 662),
#                  (122, 708)],
#     # 2026-10-05, the author's answers: the peninsula east of Thorian is two exclaves,
#     # Terrabis-Seran's (TS, north; in its list above) and Cardonia's (CA, south)
#     "cardonia": [(1180, 980)],
# }
# 2026-10-07: twenty nations in Araseos' south and west and in Yastreovakia, Merlgould
# out of Vultuca, and islands the Names layer labels (KR, RU, PE, TP, ES = Estande, CS).
# The seeds were found from the author's labels: a name's bordered area, or the land
# nearest an island label (one seed per patch the lines enclose).
DEFAULT_OWNER = "krionik"
OWNERS_1007 = {
    "cascadia": [(523, 749)],
    "daravon": [(616, 1575)],
    "dumas": [(1323, 1907)],
    "eschland": [(596, 1630)],
    "estande": [(1076, 1686), (1108, 1762), (1215, 1658), (1240, 1689), (1240, 1799),
                (1283, 1742), (1296, 1772)],
    "gorbastan": [(2010, 551)],
    "grossloewenburg": [(122, 1688), (470, 1717)],
    "hwitland": [(489, 1617)],
    "kampf": [(1002, 2065)],
    "krionik": [(115, 1647), (131, 1648), (1935, 798), (1980, 882), (2224, 1020),
                (2296, 898), (2299, 949), (2307, 677), (2325, 705), (2330, 971),
                (2341, 735), (2355, 669), (2355, 844), (2356, 951), (2404, 769),
                (2409, 933), (2415, 632), (2421, 797), (2428, 755), (2429, 621),
                (2443, 1027), (2453, 996), (2516, 819), (2594, 734), (2651, 743),
                (2672, 798), (2683, 828), (3996, 1567)],
    "leithanien": [(362, 1541), (373, 1567), (416, 1555), (420, 1528), (426, 1550),
                   (437, 1579), (480, 1559)],
    "merlgould": [(403, 1109)],
    "ostaria": [(503, 1540)],
    "peatiktist": [(421, 1454), (638, 1644), (652, 1605), (695, 1589), (779, 1639),
                   (891, 1596), (929, 1695)],
    "russovichia": [(1973, 589), (1975, 607), (1997, 607), (1999, 592), (2056, 589)],
    "schteirmark": [(671, 2070)],
    "serentia": [(434, 1515), (515, 1495)],
    "sminishia": [(2065, 439)],
    "someriania": [(1071, 2245)],
    "terrabis_seran": [(271, 1827), (372, 1475)],
    "terreich": [(596, 2222), (632, 1670), (671, 1792), (717, 1767), (721, 1792),
                 (758, 1859), (762, 1816), (773, 1910), (776, 1871), (848, 1824),
                 (878, 1740), (918, 1902), (980, 1785), (1054, 1708)],
    "transcainia": [(392, 1440), (420, 1414)],
    "zukchiva": [(2273, 492)],
}
# 2026-10-07, later (author): the patch north of Peatiktist's exclave is Transcainia's.
# The run above left it because an old LEAVE pixel, (403, 1359), lay in it. Only this
# patch is seeded: re-seeding a finished country re-cuts it (Grossloewenburg did).
OWNERS_1007B = {"transcainia": [(420, 1414)]}
# 2026-10-08: Belekria (its west, the middle box and Tethia, which starts as part of it),
# Merigo and Zwintern, and the islands the labels name (BE, SO, KF, MA, OS, KE, DU). The
# letters were written on Necessary Borders and were moved to Necessary Names first.
OWNERS_0810 = {
    "belekria": [(1915, 337), (2070, 350), (2169, 342),
                 (1635, 274), (1470, 286), (1416, 303), (1471, 341), (1513, 357),
                 (1042, 396), (1099, 405), (1138, 408), (1149, 414), (1066, 418),
                 (1086, 423), (1211, 421), (1175, 434), (1238, 435), (1250, 435),
                 (1159, 442), (1585, 717), (1514, 732)],
    "merigo": [(305, 1818)],
    "zwintern": [(291, 1951)],
    "someriania": [(957, 2287), (985, 2312), (1007, 2308), (1090, 2310), (1049, 2329),
                   (976, 2340), (1016, 2339), (998, 2348), (1053, 2355), (1035, 2353),
                   (987, 2358), (1025, 2362)],
    "kilkire": [(963, 2315)],  # the west of the island the KF line splits
    "mahina": [(1454, 2375), (1547, 2377), (1474, 2381), (1494, 2385), (1466, 2382),
               (1473, 2389), (1606, 2394), (1590, 2395), (1579, 2399), (1565, 2399),
               (1656, 2413), (1673, 2419)],
    "ostercoirasreich": [(134, 2223), (127, 2234), (629, 2305), (591, 2444), (1186, 2380)],
    "kampf": [(1204, 2375), (1297, 2014), (1316, 2031)],
    "dumas": [(1318, 1990)],
}
# 2026-10-08, later: Ungar, the Grand Duchy the author labelled east of Merigo (it was
# left as Araseos until then: (554, 1814) in LEAVE)
OWNERS_0810B = {"ungar": [(554, 1814)]}
# 2026-10-09: Yastreovakia's north-east, all of it now outlined, with the islands its
# labels name (BK, SA, VO, BT, SK); Tenkyoku's island in Orientalis (its label sits on
# it; the peninsula beside it stays in LEAVE) and the islands labelled ES near it, which
# are Estande's. One seed per patch the lines enclose, found from the author's labels.
# West Sminishia, cut out of Sminishia by a new line, is done afterwards with
# pdn_tools.py cede (Sminishia has no state lines of its own).
OWNERS = {
    "belka": [(2356, 318), (2271, 176), (2304, 364), (2350, 376), (2383, 385), (2312, 393),
              (2361, 430), (2385, 444), (2465, 486)],
    "sanada": [(2823, 257), (3416, 145), (3393, 161), (2592, 178), (3215, 176), (3379, 183),
               (3242, 190), (3251, 200), (3318, 195), (3207, 202)],
    "kamyachyn": [(2792, 349)],
    "brethren": [(3178, 384), (3264, 430)],
    "pakitsk": [(2520, 386)],
    "volstokn": [(2845, 440), (3162, 549), (3195, 555), (3209, 596)],
    "rysny": [(3084, 438)],
    "zoluzeme": [(2795, 483)],
    "vilna": [(2880, 499)],
    "kieska": [(2746, 523)],
    "sombor": [(2697, 579)],
    "skillia": [(2821, 824), (2777, 792)],
    "tenkyoku": [(4197, 1446)],
    "estande": [(3998, 1438), (3916, 1439), (4072, 1469), (4051, 1476), (3990, 1490)],
}
OWNERS_0410 = {
    "anglost": [(528, 1283), (607, 1287), (509, 1335), (436, 1342), (506, 1363), (474, 1379),
                (516, 1386), (563, 1388), (626, 1425), (583, 1428), (654, 1430), (658, 1421),
                (555, 1468), (916, 1564), (918, 1637), (976, 1666), (823, 1535), (823, 1550)],
    "san_sierra": [(877, 1297), (897, 1184), (936, 1206), (903, 1220), (893, 1247),
                   (1099, 1230), (1134, 1228), (1052, 1243), (1107, 1248), (1051, 1252),
                   (1042, 1256), (1086, 1263), (1053, 1260), (1035, 1269), (1061, 1279),
                   (1071, 1272), (1062, 1291), (1113, 1285), (1031, 1295), (1031, 1313),
                   (1057, 1311)],
    "n_pollana": [(1001, 1322)],
    "s_pollana": [(975, 1340)],
    "guardana": [(941, 1372)],
    "dremaur": [(1110, 1325)],
    "normania": [(783, 1484)],
    "aislada": [(1954, 1163), (1793, 1320), (1905, 1174), (2051, 1140), (1852, 1297),
                (1791, 1257), (1865, 1239), (1823, 1208), (1837, 1309)],
}
# patches the lines happen to close off that are not meant as anything yet: left as they
# are (the unnamed peninsula with the bay east of Fraxhemark; 2026-10-04: the land
# between Anglost and San Sierra, the author undecided, and the land south of Anglost's
# westernmost island). The land south of Entroterra and Estande, left here from
# 2026-10-01, became San Sierra on 2026-10-04.
LEAVE = [  # (596, 2222), the bit of coast west of Gaellia, became Terreich's on 2026-10-07
         # 2026-10-07: unlabelled land the new lines close off, left as it is (south of
         # Krionik's eastern part, Orientalis north of its new line, two patches in
         # Araseos' south-west) and slivers of a few pixels; (297, 1887) is Zwintern's
         # and (554, 1814) Ungar's since 2026-10-08
         (2553, 933), (4152, 1460), (2254, 405), (487, 1531), (334, 1844),
         (1618, 1798), (2323, 1884), (1757, 1894),  # Solitas placeholder land the friend's nations left
         (847, 1402), (769, 1354),  # (403, 1359) is Transcainia's since 2026-10-07
         # Aislada, outlined on 2026-10-04 (still the placeholder's colour)
         (2016, 1235), (1853, 1370), (1869, 1216), (2089, 1205), (1887, 1334), (1830, 1288),
         (1930, 1272), (1863, 1238), (1840, 1313)]
# Patches an earlier run made into a country are cut again only when OWNERS seeds them
# (a new country inside an old one): from 2026-10-04 the author's own state lines are
# kept as drawn (regroup_states.py), never re-cut into k-means pieces here.
RECUT_DONE = False
# countries whose drawn regions are their states, one per city (author, 2026-10-04: the
# Aislada lines are state borders): a patch is cut into one state around each city dot
# in it (source/city_names.json), following any line that runs part-way into it, and
# kept even when small; patches with no city are cut as usual
CITY_STATES = set()  # was {"aislada"}; the author wants one state per drawn region (regroup_states.py)
MIN_STATE = 150      # smaller patches (islets) join the nearest state of their country
ISLET_REACH = 300    # ... if within this many px; farther islets make a state of their own
STATE_MAX = 2000     # patches bigger than this become several states ...
STATE_AREA = 1300    # ... of about this size (650 until 2026-10-04: the author wants fewer states)
PROVINCE_AREA = 150  # target province size inside the outlines (placeholders: 1024)
MIN_LEFTOVER = 300  # smaller remains of a cut placeholder province join a neighbour


def code(rgb):
    rgb = rgb.astype(np.int64)
    return (rgb[..., 0] << 16) | (rgb[..., 1] << 8) | rgb[..., 2]


def rgb_of(c):
    return np.array([c >> 16, (c >> 8) & 255, c & 255], np.uint8)


class Colours:
    """Hands out colours not yet used on a layer."""

    def __init__(self, used, seed):
        self.used = set(int(c) for c in np.unique(used))
        self.rng = np.random.default_rng(seed)

    def new(self):
        while True:
            c = int(self.rng.integers(1, 1 << 24))
            r, g, b = c >> 16, (c >> 8) & 255, c & 255
            if c not in self.used and min(r, g, b) > 30:
                self.used.add(c)
                return c


def kmeans_split(ys, xs, k, seed=0):
    """Split pixels into k compact pieces, each one 4-connected."""
    if k <= 1:
        return np.zeros(len(ys), int)
    pts = np.stack([ys, xs], 1).astype(float)
    rng = np.random.default_rng(seed)
    # spread-out start: farthest-point seeding
    cent = [pts[rng.integers(len(pts))]]
    for _ in range(k - 1):
        d = np.min([((pts - c) ** 2).sum(1) for c in cent], 0)
        cent.append(pts[int(np.argmax(d))])
    cent = np.array(cent)
    for _ in range(30):
        a = np.argmin(((pts[:, None] - cent[None]) ** 2).sum(-1), 1)
        cent = np.array([pts[a == j].mean(0) if (a == j).any() else cent[j] for j in range(k)])
    # make every piece connected: stray bits join the piece they touch most
    y0, x0 = ys.min(), xs.min()
    grid = np.full((ys.max() - y0 + 1, xs.max() - x0 + 1), -1)
    grid[ys - y0, xs - x0] = a
    cross = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])
    for _ in range(20):
        changed = False
        for j in range(k):
            comp = sklabel(grid == j, connectivity=1)
            sizes = np.bincount(comp.ravel())[1:]
            if len(sizes) <= 1:
                continue
            keep = int(np.argmax(sizes)) + 1
            for q in range(1, len(sizes) + 1):
                if q == keep:
                    continue
                m = comp == q
                ring = ndi.binary_dilation(m, cross) & ~m & (grid >= 0) & (grid != j)
                if ring.any():
                    grid[m] = Counter(grid[ring].tolist()).most_common(1)[0][0]
                    changed = True
        if not changed:
            break
    return grid[ys - y0, xs - x0]


def organic_split(ys, xs, k, seed=0):
    """k pieces with natural borders: k-means picks where the pieces sit, then each grows
    from the pixel nearest its k-means centre over noise (organic.py)."""
    if k <= 1:
        return np.zeros(len(ys), int)
    a = kmeans_split(ys, xs, k, seed)
    seeds = []
    for j in range(k):
        m = a == j
        if not m.any():
            continue
        cy, cx = ys[m].mean(), xs[m].mean()
        i = np.argmin((ys[m] - cy) ** 2 + (xs[m] - cx) ** 2)
        seeds.append((ys[m][i], xs[m][i]))
    return organic.split(ys, xs, seeds, seed)


def main():
    subprocess.run([sys.executable, str(Path(__file__).parent / "readpdn.py"), sys.argv[1], str(SRC)],
                   check=True, stdout=subprocess.DEVNULL)
    names = (SRC / "layers.txt").read_text().splitlines()
    L = {nm: np.load(SRC / f"layer{k}.npy") for k, nm in enumerate(names)}
    terr = code(L["Terrain"][..., :3])
    land = (terr != code(np.array(OCEAN))) & (terr != code(np.array(LAKES)))
    lines = np.zeros((H, W), bool)
    for choices in LINE_LAYERS:
        nm = next((c for c in choices if c in L), None)
        if nm is None:
            sys.exit(f"The .pdn has no layer named {choices[0]!r}")
        lines |= L[nm][..., 3] > 0

    # ------------------------------------------------ enclosed patches -> new provinces
    cells = sklabel(land & ~lines, connectivity=1)
    size = np.bincount(cells.ravel())
    touch = np.zeros(len(size), bool)  # patches that touch a line
    near = ndi.binary_dilation(lines, np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]))
    touch[np.unique(cells[near])] = True
    touch[0] = False
    owner_of = {}
    for tag, pts in OWNERS.items():
        for x, y in pts:
            owner_of[int(cells[y, x])] = tag
    K0 = code(L["Countries"][..., :3])
    real_col = {code(np.array(COUNTRIES[c][3])): c for c in COUNTRIES if c not in PLACEHOLDERS}
    done = np.isin(K0, list(real_col)) & land
    dsum = np.bincount(cells[done], minlength=len(size))
    # the rest of the continent: the biggest patch touching a line that is not seeded,
    # left alone or done (a new country can be bigger than what remains of the placeholder)
    free = touch & (dsum * 2 < size)
    free[list(owner_of) + [int(cells[y, x]) for x, y in LEAVE]] = False
    outside = int(np.argmax(np.where(free, size, 0))) if free.any() else -1
    chosen = [i for i in np.nonzero(touch)[0] if i != outside] + \
        [i for i in owner_of if not touch[i]]
    chosen = sorted(set(chosen))
    # skip patches an earlier run already turned into a real country, unless a new line
    # cuts through one of their states: those are cut again and keep their country
    S0 = np.where(L["States"][..., 3] > 0, code(L["States"][..., :3]), -1)

    def cut_by_lines(sc):
        """True if the lines split state sc into more pieces than it has anyway
        (islets across water are fine)."""
        ys, xs = np.nonzero(S0 == sc)
        sl = np.s_[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        m = S0[sl] == sc
        whole = np.bincount(sklabel(m, connectivity=1).ravel())[1:]
        parts = np.bincount(sklabel(m & ~lines[sl], connectivity=1).ravel())[1:]
        return (parts >= 8).sum() > (whole >= 8).sum()

    before = len(chosen)
    kept, recut = [], []
    for i in chosen:
        if dsum[i] * 2 < size[i]:
            kept.append(i)
            continue
        if not RECUT_DONE and int(i) not in owner_of:
            continue
        ys, xs = np.nonzero(cells == i)
        if not any(cut_by_lines(sc) for sc in np.unique(S0[ys, xs]) if sc >= 0):
            continue
        kept.append(i)
        recut.append(i)
        # keeps its country, unless OWNERS seeds it for another (a new country outlined
        # inside an old one)
        owner_of.setdefault(int(i), real_col[Counter(K0[ys, xs].tolist()).most_common(1)[0][0]])
    chosen = kept
    print(f"{before - len(chosen)} patches were outlined by an earlier run and are kept as they are; "
          f"{len(recut)} are cut again because new lines split their states")
    leave = {int(cells[y, x]) for x, y in LEAVE}
    chosen = [i for i in chosen if int(i) not in leave]
    for i in chosen:
        if int(i) not in owner_of:
            ys, xs = np.nonzero(cells == i)
            print(f"  patch at ({int(xs.mean())}, {int(ys.mean())}), {size[i]} px: no seed, "
                  f"goes to {DEFAULT_OWNER}")
        owner_of.setdefault(int(i), DEFAULT_OWNER)
    # line pixels on land go to the nearest patch (inside or out)
    idx = ndi.distance_transform_edt(cells == 0, return_distances=False, return_indices=True)
    cells = np.where(land & (cells == 0), cells[idx[0], idx[1]], cells)
    area = np.isin(cells, chosen) & (~done | np.isin(cells, recut))
    print(f"{len(chosen)} outlined patches, {area.sum()} px, outside patch {outside}")

    P = code(L["Provinces"][..., :3])
    cut = set(np.unique(P[area]).tolist())  # placeholder provinces the outlines cut into
    pcols = Colours(P, 1)
    newP = P.copy()
    prov_owner = {}   # new province colour -> owner
    prov_state = {}   # new province colour -> (patch id, state number in the patch)
    import json
    cities = [tuple(map(int, k.split(","))) for k in
              json.loads(Path("source/city_names.json").read_text(encoding="utf-8"))]
    city_patch = set()
    for i in chosen:
        ys, xs = np.nonzero(cells == i)
        inside = [(y, x) for x, y in cities if cells[y, x] == i] if owner_of[int(i)] in CITY_STATES else []
        if inside:
            ks = len(inside)
            st = organic.split(ys, xs, inside, seed=int(i))
            city_patch.add(int(i))
        else:
            ks = max(1, round(len(ys) / STATE_AREA)) if len(ys) > STATE_MAX else 1
            st = organic_split(ys, xs, ks, seed=int(i))
        for j in range(ks):
            sy, sx = ys[st == j], xs[st == j]
            if len(sy) == 0:
                continue
            kp = min(max(1, round(len(sy) / PROVINCE_AREA)), len(sy) // MIN_PROVINCE or 1)
            parts = organic_split(sy, sx, kp, seed=int(i) * 31 + j)
            for q in range(kp):
                if not (parts == q).any():
                    continue
                c = pcols.new()
                newP[sy[parts == q], sx[parts == q]] = c
                prov_owner[c] = owner_of[int(i)]
                prov_state[c] = (int(i), j)

    # ------------------------------------------------ leftovers of cut provinces
    # Every province near the outlines must end up one connected piece of a decent
    # size: stray scraps join the neighbour they share most border with (a new
    # province prefers one of the same country), larger extra pieces of a cut
    # placeholder become provinces of their own. Repeat until nothing changes.
    ys, xs = np.nonzero(area)
    y0, y1 = max(ys.min() - 64, 0), min(ys.max() + 65, H)
    x0, x1 = max(xs.min() - 64, 0), min(xs.max() + 65, W)
    win = newP[y0:y1, x0:x1]  # a view: edits land in newP
    wland = land[y0:y1, x0:x1]
    cross = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])
    merged = split = 0
    extra = set()  # provinces made from big extra pieces below
    for _ in range(20):
        changed = False
        # each province is looked at inside its own bounding box (one more pixel each
        # way, for its ring); a box gone stale by a merge is caught on the next pass
        ucols, inv = np.unique(np.where(wland, win, -1), return_inverse=True)
        inv = inv.reshape(win.shape)
        boxes = ndi.find_objects(inv + 1)
        for k, c in enumerate(ucols):
            if c < 0 or boxes[k] is None:
                continue
            if int(c) not in prov_owner and int(c) not in cut and int(c) not in extra:
                # untouched by the outlines (2026-10-09: ones the window's edge clips
                # looked split, and 77 px of them were merged away)
                continue
            by, bx = boxes[k]
            sl = np.s_[max(by.start - 1, 0):by.stop + 1, max(bx.start - 1, 0):bx.stop + 1]
            bw, bland = win[sl], wland[sl]  # views
            m = (bw == c) & bland
            if not m.any():  # merged away earlier in this pass
                continue
            comp = sklabel(m, connectivity=1)
            sizes = np.bincount(comp.ravel())[1:]
            keep = int(np.argmax(sizes)) + 1
            new = int(c) in prov_owner
            for j, sz in enumerate(sizes, 1):
                limit = MIN_PROVINCE if new else (MIN_PROVINCE if j == keep and c not in cut else MIN_LEFTOVER)
                if j == keep and sz >= limit:
                    continue
                pm = comp == j
                if sz >= limit:  # a big extra piece: its own province
                    bw[pm] = nc = pcols.new()
                    extra.add(nc)
                    split += 1
                    changed = True
                    continue
                ring = ndi.binary_dilation(pm, cross) & ~pm & bland
                nb = Counter(v for v in bw[ring].tolist() if v != c)
                if not nb:
                    continue
                # a new province's scrap stays in its state, an old one's outside
                same_state = [v for v in nb if prov_state.get(v) == prov_state.get(int(c))]
                same_owner = [v for v in nb if prov_owner.get(v) == prov_owner.get(int(c))]
                target = max(same_state or same_owner or nb, key=lambda v: nb[v])
                bw[pm] = target
                merged += 1
                changed = True
        if not changed:
            break
    alive = set(np.unique(win).tolist())
    for c in [c for c in prov_owner if c not in alive]:  # tiny outlined patches merged away
        del prov_owner[c], prov_state[c]
    print(f"{len(cut)} placeholder provinces were cut; {merged} scraps joined a neighbour, "
          f"{split} extra pieces became provinces")

    # ------------------------------------------------ states
    S = np.where(L["States"][..., 3] > 0, code(L["States"][..., :3]), -1)
    scols = Colours(S[S >= 0], 2)
    newS = S.copy()
    # islets too small for a state of their own join the nearest state of their country
    cent = {}
    for c in prov_state:
        ys, xs = np.nonzero(win == c)
        cent[c] = (ys.mean(), xs.mean())
    patch_size = {i: int(size[i]) for i in chosen}
    for c, key in list(prov_state.items()):
        if patch_size[key[0]] >= MIN_STATE or key[0] in recut or key[0] in city_patch:  # drawn: kept
            continue
        best = min((k for k in prov_state if patch_size[prov_state[k][0]] >= MIN_STATE
                    and prov_owner[k] == prov_owner[c]),
                   key=lambda k: np.hypot(cent[k][0] - cent[c][0], cent[k][1] - cent[c][1]),
                   default=None)
        far = best is None or np.hypot(cent[best][0] - cent[c][0], cent[best][1] - cent[c][1]) > ISLET_REACH
        if not far:
            prov_state[c] = prov_state[best]
            continue
        # far from the rest of its country (Rouental's islets off Solitas): islets of
        # one country near each other share a state of their own
        for k, kk in list(prov_state.items()):
            if k != c and prov_owner[k] == prov_owner[c] and patch_size[kk[0]] < MIN_STATE and \
                    np.hypot(cent[k][0] - cent[c][0], cent[k][1] - cent[c][1]) <= ISLET_REACH:
                prov_state[c] = kk
                break
    # one state per (patch, piece), as drawn
    groups = defaultdict(list)
    for c, key in prov_state.items():
        groups[key].append(c)
    by_owner = defaultdict(list)
    state_groups = []  # (owner, [province colours])
    for key in sorted(groups):
        g = groups[key]
        state_groups.append((prov_owner[g[0]], g))
        by_owner[prov_owner[g[0]]].append(key)
    new_states = []
    for t, g in state_groups:
        sc = scols.new()
        newS[np.isin(newP, g)] = sc
        new_states.append((t, sc, g))
    newS[~land] = -1
    fresh = {sc for _, sc, _ in new_states}  # old scraps must not join these
    # old states cut in pieces: pieces away from the main one join the neighbour
    for sc in np.unique(S[area & (S >= 0)]):
        rest = (newS == sc)
        if not rest.any():
            continue
        comp = sklabel(rest, connectivity=1)
        sizes = np.bincount(comp.ravel())[1:]
        keep = int(np.argmax(sizes)) + 1
        for j in range(1, len(sizes) + 1):
            if j == keep:
                continue
            m = comp == j
            ring = ndi.binary_dilation(m) & ~m & land
            nb = Counter(v for v in newS[ring].tolist() if v >= 0 and v != sc and v not in fresh)
            if nb and sizes[j - 1] < 3000:
                newS[m] = nb.most_common(1)[0][0]
    print(f"{len(new_states)} new states: " + ", ".join(
        f"{t} {sum(1 for s in new_states if s[0] == t)}" for t in sorted(by_owner)))

    # ------------------------------------------------ countries
    K = code(L["Countries"][..., :3])
    newK = K.copy()
    for t, sc, g in new_states:
        newK[newS == sc] = code(np.array(COUNTRIES[t][3]))

    # ------------------------------------------------ strategic regions
    R = code(L["Strategic Regions"][..., :3])
    newR = R.copy()
    # every state near the outlines lies in the region most of it was in
    near_area = newS[y0:y1, x0:x1]
    for sc in np.unique(near_area[near_area >= 0]):
        m = newS == sc
        newR[m] = Counter(R[m].tolist()).most_common(1)[0][0]

    # ------------------------------------------------ write
    def put(layer, codes, mask=None):
        out = L[layer].copy()
        m = np.ones((H, W), bool) if mask is None else mask
        out[m, :3] = np.stack([codes[m] >> 16, (codes[m] >> 8) & 255, codes[m] & 255], 1)
        if mask is not None:
            out[..., 3] = np.where(mask, 255, 0)
        return out

    L["Provinces"] = put("Provinces", newP)
    L["States"] = put("States", np.maximum(newS, 0), newS >= 0)
    L["Countries"] = put("Countries", newK, L["Countries"][..., 3] > 0)
    L["Strategic Regions"] = put("Strategic Regions", newR)
    template = sys.argv[1]
    tmp = OUT.with_suffix(".tmp")
    write_pdn(template, tmp, [L[nm] for nm in names])
    shutil.move(tmp, OUT)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
