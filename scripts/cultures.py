"""Generic portraits, name lists and graphical cultures for our countries.

HOI4 generates leaders, generals, admirals and scientists from two sources:
  * portraits/*.txt: vanilla's lists are keyed by Earth continents (europe, asia, ...),
    which do not exist on this map, hence "Failed to generate a portrait". We write
    `continent = { name = <our continent> ... }` blocks with vanilla's own generic
    portrait sprites, plus `TAG = { ... }` blocks for countries with their own look;
  * common/names/*.txt: per-tag name lists ("Failed to generate a name" without them).
    We copy vanilla culture blocks from source/names/vanilla_names.txt under our tags.

A country takes its culture from the continent of its capital unless TAG_CULTURE says
otherwise. Portrait sprites come from vanilla 1.19.3 interface/_random_portraits.gfx
(the full list is source/names/vanilla_portrait_sprites.txt, which check_mod.py uses).
"""
import re
from pathlib import Path

NAMES_SRC = Path("source/names/vanilla_names.txt")


def _seq(base, n, start=1):
    return [f"{base}_{i}" for i in range(start, start + n)]


# portrait region -> army / navy / political (per ideology) sprite lists
REGIONS = {
    "europe": dict(
        army=_seq("GFX_Portrait_Europe_Generic_land", 5) + ["GFX_portrait_europe_generic_land_13"]
        + _seq("GFX_Portrait_Germany_Generic_land", 9) + _seq("GFX_Portrait_Britain_Generic_land", 10)
        + _seq("GFX_Portrait_Italy_Generic_land", 8),
        navy=_seq("GFX_Portrait_Europe_Generic_navy", 3) + _seq("GFX_Portrait_Germany_Generic_navy", 3)
        + _seq("GFX_Portrait_Britain_Generic_navy", 3) + _seq("GFX_Portrait_Italy_Generic_navy", 3),
        political=dict(communism=["GFX_Portrait_Europe_Generic_1"],
                       democratic=["GFX_Portrait_Europe_Generic_2"],
                       fascism=["GFX_Portrait_Europe_Generic_3"],
                       neutrality=["GFX_Portrait_Europe_Generic_3"],
                       theocracy=["GFX_Portrait_Europe_Generic_3"])),
    "france": dict(
        army=_seq("GFX_Portrait_France_Generic_land", 9),
        navy=_seq("GFX_Portrait_France_Generic_navy", 3),
        political=dict(communism=["GFX_Portrait_Europe_Generic_1"],
                       democratic=["GFX_Portrait_Europe_Generic_2"],
                       fascism=["GFX_Portrait_Europe_Generic_3"],
                       neutrality=["GFX_Portrait_Europe_Generic_3"],
                       theocracy=["GFX_Portrait_Europe_Generic_3"])),
    "mideast_africa": dict(
        army=_seq("GFX_Portrait_Arabia_Generic_land", 3) + _seq("GFX_Portrait_Africa_Generic_land", 3),
        navy=_seq("GFX_Portrait_Arabia_Generic_navy", 3) + _seq("GFX_Portrait_Africa_Generic_navy", 3),
        political=dict(communism=["GFX_Portrait_Arabia_Generic_1", "GFX_Portrait_Africa_Generic_1"],
                       democratic=["GFX_Portrait_Arabia_Generic_2", "GFX_Portrait_Africa_Generic_2"],
                       fascism=["GFX_Portrait_Arabia_Generic_3", "GFX_Portrait_Africa_Generic_3"],
                       neutrality=["GFX_Portrait_Arabia_Generic_3", "GFX_Portrait_Africa_Generic_3"],
                       theocracy=["GFX_Portrait_Arabia_Generic_3", "GFX_Portrait_Africa_Generic_3"])),
    "asia": dict(
        army=_seq("GFX_Portrait_Asia_Generic_land", 5) + _seq("GFX_Portrait_Japan_Generic_land", 9)
        + _seq("GFX_portrait_se_asia_generic_land", 3),
        navy=_seq("GFX_Portrait_Asia_Generic_navy", 3) + _seq("GFX_Portrait_Japan_Generic_navy", 3)
        + _seq("GFX_portrait_se_asia_generic_navy", 3),
        political=dict(communism=["GFX_Portrait_Asia_Generic_1"],
                       democratic=["GFX_Portrait_Asia_Generic_2"],
                       fascism=["GFX_Portrait_Asia_Generic_3"],
                       neutrality=["GFX_Portrait_Asia_Generic_3"],
                       theocracy=["GFX_Portrait_Asia_Generic_3"])),
}

# Portuguese: Europe's generals, and South America's politicians with Europe's
REGIONS["iberia"] = dict(
    army=REGIONS["europe"]["army"], navy=REGIONS["europe"]["navy"],
    political={i: ["GFX_Portrait_Europe_Generic_1", "GFX_Portrait_Europe_Generic_2",
                   "GFX_Portrait_Europe_Generic_3"] + _seq("GFX_Portrait_South_America_Generic", 3)
               for i in REGIONS["europe"]["political"]})

# continent -> culture: vanilla name block, portrait region, graphical culture
CONTINENT_CULTURE = {
    "nonscio": dict(names="ENG", portraits="europe", gfx="western_european"),
    "araseos": dict(names="ITA", portraits="europe", gfx="western_european"),
    "aislada": dict(names="AST", portraits="europe", gfx="commonwealth"),
    "solitas": dict(names="SWE", portraits="europe", gfx="western_european"),
    "yastreovakia": dict(names="POL", portraits="europe", gfx="eastern_european"),
    "usnistan": dict(names="PER", portraits="mideast_africa", gfx="middle_eastern"),
    "orientalis": dict(names="JAP", portraits="asia", gfx="asian"),
}

# countries that differ from their continent (only names/portraits need giving)
_FRENCH = dict(names="FRA", portraits="france", gfx="western_european")
TAG_CULTURE = {
    # the Reibonnaise states: French for now (author, 2026-09-29)
    **{t: _FRENCH for t in ("ROU", "SGN", "EVR", "HLR", "SGV", "LST", "LZC", "GDN")},
    "LNT": _FRENCH,  # author, 2026-09-30
    # Portuguese (author, 2026-09-30): vanilla has no Iberian generic portraits
    **{t: dict(names="POR", portraits="iberia", gfx="western_european")
       for t in ("RST", "VLN", "ESD", "CRZ", "PLH")},
    # Illiricium and its republics: Italian names (Claude's guess from Mezzogiorno and
    # Entroterra; the author has not said)
    **{t: dict(names="ITA", portraits="europe", gfx="western_european")
       for t in ("ILR", "CTF", "ETR", "MZG", "KIL")},
    # Claude's guesses from the flags (2026-10-01): Kurikia's Russian-style eagle and
    # Fraxhemark's Montenegrin arms
    "KRK": dict(names="SOV", portraits="europe", gfx="eastern_european"),
    "FRX": dict(names="YUG", portraits="europe", gfx="eastern_european"),
}


def culture(tag, continent):
    return TAG_CULTURE.get(tag) or CONTINENT_CULTURE[continent]


def _portrait_body(region, indent):
    r = REGIONS[region]
    t = "\t" * indent

    def lst(items, d):
        return "".join(f'{t}{d}"{s}"\n' for s in items)
    out = [f"{t}army = {{\n{t}\tmale = {{\n", lst(r["army"], "\t\t"), f"{t}\t}}\n{t}}}\n",
           f"{t}navy = {{\n{t}\tmale = {{\n", lst(r["navy"], "\t\t"), f"{t}\t}}\n{t}}}\n",
           f"{t}political = {{\n"]
    for ideo, sprites in r["political"].items():
        out += [f"{t}\t{ideo} = {{\n{t}\t\tmale = {{\n", lst(sprites, "\t\t\t"), f"{t}\t\t}}\n{t}\t}}\n"]
    out.append(f"{t}}}\n")
    return "".join(out)


def write_files(write, tag_continent, continents):
    """tag_continent: tag -> continent of its capital. Returns tag -> graphical culture."""
    # portraits: every continent, then the countries that look different
    parts = ["# Generated by scripts/cultures.py\n"]
    for c in continents:
        parts.append(f"continent = {{\n\tname = {c}\n{_portrait_body(CONTINENT_CULTURE[c]['portraits'], 1)}}}\n")
    for tag in sorted(tag_continent):
        if tag in TAG_CULTURE:
            parts.append(f"{tag} = {{\n{_portrait_body(TAG_CULTURE[tag]['portraits'], 1)}}}\n")
    write("portraits/valsora_portraits.txt", "".join(parts))

    # names: the vanilla culture block, under our tag
    src = NAMES_SRC.read_text(encoding="utf-8")
    blocks = {m.group(1): m.group(0) for m in re.finditer(r"^([A-Z]{3}) = \{.*?^\}", src, re.S | re.M)}
    out = ["# Generated by scripts/cultures.py from vanilla name lists"]
    for tag in sorted(tag_continent):
        b = blocks[culture(tag, tag_continent[tag])["names"]]
        out.append(tag + b[3:])
    write("common/names/valsora_names.txt", "\n\n".join(out) + "\n")  # UTF-8, no BOM, as vanilla
    return {tag: culture(tag, c)["gfx"] for tag, c in tag_continent.items()}


def sprites_used():
    s = set()
    for r in REGIONS.values():
        s |= set(r["army"]) | set(r["navy"])
        for v in r["political"].values():
            s |= set(v)
    return s


# famous surnames a made-up leader should not carry
NOT_SURNAMES = {"Petain", "Foch", "Joffre", "Salazar", "Napoléon", "Murat", "Davout",
                "d'Orleans", "Franchet d'Espèrey", "Churchill", "Mussolini", "Hirohito", "Tojo", "Piłsudski"}


def _tokens(block):
    return [a or b for a, b in re.findall(r'"([^"]+)"|([^\s{}"]+)', block)]


def _names(culture):
    src = NAMES_SRC.read_text(encoding="utf-8")
    b = re.search(rf"^{culture} = \{{(.*?)^\}}", src, re.S | re.M).group(1)
    male = re.search(r"male\s*=\s*\{\s*names\s*=\s*\{(.*?)\}", b, re.S).group(1)
    sur = re.search(r"surnames\s*=\s*\{(.*?)\}", b, re.S).group(1)
    return ([n for n in _tokens(male) if n not in NOT_SURNAMES],
            [n for n in _tokens(sur) if n not in NOT_SURNAMES])


def leaders(tag, continent, subtypes, ideology_of, used):
    """Characters for a country's leaders: a name from its culture's list and a generic
    portrait of its culture, per subtype. Returns (character blocks, loc lines, ids).
    Deterministic: the same tag always gets the same people."""
    import zlib
    import numpy as np
    c = culture(tag, continent)
    first, last = _names(c["names"])
    rng = np.random.default_rng(zlib.crc32(tag.encode()))
    blocks, loc, ids = [], [], []
    for sub in subtypes:
        # not TAG_<subtype>: the game reads that key as the country's name under that
        # subtype (vanilla's GER_nazism), so every country showed its leader's name
        cid = f"{tag}_leader_{sub}"
        # any politician of the culture (a single ideology's list is one or two faces)
        pool = sorted({p for v in REGIONS[c["portraits"]]["political"].values() for p in v})
        while True:  # no two leaders share a full name (`used` spans every country)
            name = f"{first[rng.integers(len(first))]} {last[rng.integers(len(last))]}"
            if name not in used:
                used.add(name)
                break
        blocks.append(f"""\t{cid} = {{
\t\tname = {cid}
\t\tportraits = {{
\t\t\tcivilian = {{
\t\t\t\tlarge = {pool[rng.integers(len(pool))]}
\t\t\t}}
\t\t}}
\t\tcountry_leader = {{
\t\t\tideology = {sub}
\t\t\texpire = "1965.1.1.1"
\t\t\tid = -1
\t\t}}
\t}}
""")
        loc.append(f' {cid}:0 "{name}"')
        ids.append(cid)
    return blocks, loc, ids
