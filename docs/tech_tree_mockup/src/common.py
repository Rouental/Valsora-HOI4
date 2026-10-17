"""Shared pieces of the 2036 tech tree mockup: the eras, the tiers, the folder and technology records.

Not part of the mod: nothing in scripts/ imports this, and nothing here writes outside docs/tech_tree_mockup/.
The data modules (data_*.py) call folder() and T() to describe the tree; make_tree.py lays it out, fills in the
base game's facts and writes tree.json.
"""

# ----- the calendar --------------------------------------------------------------------------------------------
# The base game's 1936 is Valsora's 2036 (README, "The calendar"). The four eras, by year:
ERAS = [
    # key, name, first year, last year, what it stands for
    ("cw", "Cold War", 1960, 1989, "Cold War I (1965) and Cold War II (1985): the floor of the tree, kit of the 1960s "
                                   "to the 1980s. Feudal and levy states start with Cold War I, developing nations with "
                                   "Cold War II."),
    ("modern", "Modern", 1990, 2030, "Modern I (2005) and Modern II (2025): today's kit, what most nations field. "
                                     "Modern II is what the base game gives its minor nations at the start."),
    ("y2036", "2036", 2031, 2039, "The game's first years: the superpowers start with part of it (the base game's majors "
                                  "start with its 1936 technologies), everyone else researches it first."),
    ("next", "Next generation", 2040, 2050, "Ahead of everyone: late, costly, and penalised as ahead of its time until "
                                            "its year. The base game's three-year rhythm: big steps in 2039, 2042, 2045, "
                                            "upgrades between."),
]


def era_of(year):
    for key, _name, lo, hi, _d in ERAS:
        if lo <= year <= hi:
            return key
    raise ValueError(f"no era for {year}")


# ----- who starts with what ------------------------------------------------------------------------------------
TIERS = [
    # key, name, rank, what they start with
    ("feudal", "Feudal and levy states", 0, "Cold War I: the floor of every main line (Rouental's vassal levies)."),
    ("developing", "Developing", 1, "Up to Cold War II."),
    ("modern", "Modern (default)", 2, "Up to Modern II: today's kit. Every nation the author doesn't place elsewhere."),
    ("super", "Superpowers", 3, "Modern II and part of 2036, the nuclear technologies and a few warheads: Krionik, "
                                "the Kampfian Empire, Sarkis and Fraxhemark."),
]
RANK = {k: r for k, _n, r, _d in TIERS}


def start_of(year):
    """The lowest tier that starts with a technology of this year (None: nobody)."""
    if year <= 1975:
        return "feudal"
    if year <= 1995:
        return "developing"
    if year <= 2030:
        return "modern"
    if year <= 2036:
        return "super"
    return None


# ----- the records ---------------------------------------------------------------------------------------------
FOLDERS = []          # in tab order
TECHS = []            # in the order written


class Folder:
    def __init__(self, key, name, game, orient, icon, ledger, blurb, dlc=None, variant_of=None, kind="tree"):
        self.key, self.name, self.game, self.orient, self.icon = key, name, game, orient, icon
        self.ledger, self.blurb, self.dlc, self.variant_of, self.kind = ledger, blurb, dlc, variant_of, kind
        self.sections = []        # (name, first lane)
        self.cur_section = None
        self.extra = {}           # anything else the page shows for this folder

    def section(self, name, lane):
        self.sections.append({"name": name, "lane": lane})
        self.cur_section = name
        return name


def folder(*a, **k):
    f = Folder(*a, **k)
    FOLDERS.append(f)
    return f


def T(f, tid, name, year, lane, desc, icon=None, req=None, excl=(), unl=(), size=None, start="auto", dlc=None,
      cost=None, also=(), replaces=None, note=None):
    """One technology.

    tid: the base game's id when this renames that technology, or a new id starting with val_.
    req: None for "the previous technology in the same lane", [] for none, or a list of ids.
    start: "auto" (from the year), a tier key, or None (nobody starts with it).
    also: other base-game ids folded into this one (the same technology in another DLC's form).
    replaces: the base-game id, when the new id differs from it (classic-tree mirrors use this).
    """
    t = dict(id=tid, name=name, year=year, lane=lane, desc=desc, icon=icon, req=req, excl=list(excl),
             unl=list(unl), size=size, start=start, dlc=dlc, cost=cost, also=list(also), folder=f.key,
             section=f.cur_section, note=note)
    if replaces:
        t["replaces"] = replaces
    elif tid.startswith("val_"):
        t["replaces"] = "new"
    else:
        t["replaces"] = tid
    TECHS.append(t)
    return t
