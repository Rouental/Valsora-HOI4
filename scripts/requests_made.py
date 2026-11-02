"""The traits and national spirits the Gazetteer's players asked for, made by Claude from their own words.

The author, 2026-11-02: "Created traits should be shown as applied to the character, unless I veto it, in which case it
should be removed." A request made here is in the game from the next build: a trait on its character, a spirit on its
nation from the start. The author's Decline on the page (the request's status "declined" in
source/gazetteer/<TAG>.json, after the next import) takes it out again; Done or Open leaves it in.

Each is keyed by the nation's tag and the request's title as the page wrote it. `modifier` is the player's list in the
game's modifiers (source/vanilla/index/modifiers.txt; their -50% is -0.5, their weekly 0.50% is 0.005), `equipment` the
ship stats the game gives only as equipment bonuses, `said` what they asked for that the game has no modifier for (kept
for the author, and on `gazetteer.py status`). A trait goes to the character the page's request names (`for`, since
2026-11-02), else to `to`: Claude's reading of the request ("ruler", "party_<ideology>", or None: made, no one's yet).
New requests show on `gazetteer.py status` until they are made here.
"""
import re
import unicodedata

ALL_SHIPS = ("capital_ship", "screen_ship", "carrier", "submarine")
SHIP_DESIGN = {f"ship_hull_{h}_design_cost_factor": -0.5 for h in ("light", "cruiser", "heavy", "carrier", "submarine")}
ALL_ADVISORS = {k: -0.5 for k in ("political_advisor_cost_factor", "theorist_cost_factor", "high_command_cost_factor",
                                  "army_chief_cost_factor", "navy_chief_cost_factor", "air_chief_cost_factor")}
ALL_LAWS = {k: -0.5 for k in ("economy_cost_factor", "mobilization_laws_cost_factor", "trade_laws_cost_factor")}

MADE = {
    # Arovannea (the Gazetteer's export of 2026-10-23 and 2026-10-29; made 2026-11-02). All four were asked for from
    # the head of state's box (the page had no other for a party leader): their characters are Claude's reading
    ("AVN", "New trait: The Jasper Snake"): dict(
        kind="trait", key="AVN_the_jasper_snake", name="The Jasper Snake", to="ruler",
        modifier=dict(stability_factor=-0.25, war_support_factor=-0.5, stability_weekly=-0.005,
                      communism_drift=0.1, democratic_drift=0.25, theocracy_drift=0.1, **ALL_ADVISORS, **ALL_LAWS)),
    ("AVN", "New trait: Ýzania"): dict(   # "(for Asaia)": the communists' leader
        kind="trait", key="AVN_yzania", name="Ýzania", to="party_communism",
        modifier=dict(party_popularity_stability_factor=0.3, surrender_limit=0.05, stability_factor=0.15,
                      war_support_factor=0.1, communism_drift=0.05, army_core_attack_factor=0.2,
                      army_core_defence_factor=0.2, army_org_factor=0.1, army_breakthrough_against_major_factor=0.1,
                      # "weekly war support from maluses (like bombings and casualties) +0.20%"
                      weekly_bombing_war_support=0.002, weekly_casualties_war_support=0.002,
                      weekly_convoys_war_support=0.002)),
    ("AVN", "New trait: Disjointed Democratic Coalition"): dict(   # "what the initial democratic/communist uprising
        kind="trait", key="AVN_disjointed_democratic_coalition",   # starts with": no such uprising in the game yet
        name="Disjointed Democratic Coalition", to=None,
        modifier=dict(army_attack_factor=-0.2, army_defence_factor=-0.2, army_speed_factor=-0.5,
                      stability_weekly=-0.005, war_support_weekly=-0.005)),
    ("AVN", "New trait: Grandmaster of the Athelian Order"): dict(   # the Holy Order's leader, Father Basnarius Adelkan
        kind="trait", key="AVN_grandmaster_of_the_athelian_order", name="Grandmaster of the Athelian Order",
        to="party_theocracy",
        modifier=dict(stability_factor=-0.1, war_support_factor=0.4, army_attack_factor=0.15, breakthrough_factor=0.15,
                      org_loss_at_low_org_factor=-0.35, theocracy_drift=0.25,
                      enemy_army_bonus_air_superiority_factor=-0.1)),
    ("AVN", "The Dying Republic"): dict(
        kind="spirit", key="AVN_the_dying_republic", name="The Dying Republic",
        modifier=dict(stability_factor=-0.5, war_support_factor=-0.5,
                      consumer_goods_expected_value=0.1,   # "NOT factor": the economy laws' own modifier
                      drift_defence_factor=-5.0, conscription_factor=-0.85, stability_weekly=-0.005,
                      war_support_weekly=-0.005, party_popularity_stability_factor=-1.0, research_speed_factor=-0.15,
                      political_power_cost=1.0)),
    ("AVN", "Navy with a Nation"): dict(
        kind="spirit", key="AVN_navy_with_a_nation", name="Navy with a Nation",
        modifier=dict(**SHIP_DESIGN, experience_gain_navy=0.2, industrial_capacity_dockyard=0.15,
                      unit_marine_design_cost_factor=-1.0, marines_special_forces_contribution_factor=-0.25,
                      army_sub_unit_marine_attack_factor=0.15, army_sub_unit_marine_defence_factor=0.15,
                      amphibious_invasion_defence=0.25, naval_coordination=0.1, navy_org_factor=0.05, positioning=0.2,
                      air_carrier_night_penalty_reduction_factor=0.25, navy_anti_air_attack_factor=0.25,
                      carrier_capacity_penalty_reduction=0.25, communism_drift=0.15, democratic_drift=0.15,
                      stability_factor=-0.05),
        # all ships' HP, light and heavy batteries, torpedoes, surface and submarine detection
        equipment={cat: dict(max_strength=0.1, lg_attack=0.15, hg_attack=0.1, torpedo_attack=0.35,
                             surface_detection=0.12, sub_detection=0.06) for cat in ALL_SHIPS},
        said=["Marine entrenchment +0.2: the game has no modifier for the marines' entrenchment alone"]),
}


def made_for(tag, r):
    """this request's entry in MADE, or None (titles compared in one Unicode form: a page may write Ý as Y and an accent)"""
    return MADE.get((tag, unicodedata.normalize("NFC", r.get("title") or "")))


def applied(G):
    """[(tag, request, made)] for every made request the author hasn't declined"""
    return [(tag, r, made_for(tag, r)) for tag, f in sorted(G.items()) for r in f.get("requests", [])
            if made_for(tag, r) and r.get("status") != "declined"]


def unmade(G):
    """the trait and spirit requests not made here yet (nor declined): [(tag, request)]"""
    return [(tag, r) for tag, f in sorted(G.items()) for r in f.get("requests", [])
            if r.get("kind") in ("trait", "spirit") and r.get("status") != "declined" and not made_for(tag, r)]


def owner(r, made):
    """the character a made trait goes to: the page's choice (`for`), else Claude's reading"""
    return r.get("for") or made.get("to")


def traits_of(G, tag):
    """{character: [trait keys]} of a nation: "ruler", "party_<ideology>", or a Gazetteer character's id"""
    out = {}
    for t, r, m in applied(G):
        if t == tag and m["kind"] == "trait" and owner(r, m):
            out.setdefault(owner(r, m), []).append(m["key"])
    return out


def _num(v):
    return f"{v:.4f}".rstrip("0").rstrip(".")


def _loc(s):
    """one line of localisation: paragraphs apart, line breaks kept, no double quotes"""
    paras = (re.sub(r"[ \t]*\n[ \t]*", "\\\\n", p.strip()) for p in re.split(r"\n\s*\n", s.strip()))
    return "\\n\\n".join(paras).replace('"', "'")


def spirit_text(r):
    """a spirit's description: the request's words after its list of effects (the player's story), else none"""
    paras = [p.strip() for p in re.split(r"\n\s*\n", r.get("details") or "") if p.strip()]
    story = [p for p in paras if not re.search(r"[+-]\s*\d|\d\s*%", p)]
    return "\n\n".join(story)


def files(G):
    """what the build writes for the made requests: (country leader traits, ideas, localisation lines,
    {tag: history lines}, sprite names); all empty when nothing is made"""
    traits, ideas, loc, history, sprites = [], [], [], {}, []
    for tag, r, m in applied(G):
        body = "".join(f"\t\t\t{k} = {_num(v)}\n" for k, v in m.get("modifier", {}).items())
        if m["kind"] == "trait":
            traits.append(f"\t# {tag}: {r['title']} (scripts/requests_made.py)\n\t{m['key']} = {{\n\t\trandom = no\n"
                          + body.replace("\t\t\t", "\t\t") + "\t}\n")
            loc.append(f' {m["key"]}:0 "{_loc(m["name"])}"')
        else:
            eq = "".join(f"\t\t\t\t{cat} = {{ " + " ".join(f"{k} = {_num(v)}" for k, v in stats.items()) + " }\n"
                         for cat, stats in m.get("equipment", {}).items())
            ideas.append(f"\t\t# {tag}: {r['title']} (scripts/requests_made.py)\n\t\t{m['key']} = {{\n"
                         f"\t\t\tpicture = {m['key']}\n\t\t\tallowed = {{ always = no }}\n\t\t\tremoval_cost = -1\n"
                         + (f"\t\t\tmodifier = {{\n{body.replace(chr(9) * 3, chr(9) * 4)}\t\t\t}}\n" if body else "")
                         + (f"\t\t\tequipment_bonus = {{\n{eq}\t\t\t}}\n" if eq else "") + "\t\t}\n")
            loc.append(f' {m["key"]}:0 "{_loc(m["name"])}"')
            if spirit_text(r):
                loc.append(f' {m["key"]}_desc:0 "{_loc(spirit_text(r))}"')
            history.setdefault(tag, []).append(f"add_ideas = {m['key']}")
            sprites.append(m["key"])
    trait_text = ("# The traits the Gazetteer's players asked for (scripts/requests_made.py)\nleader_traits = {\n"
                  + "".join(traits) + "}\n") if traits else ""
    idea_text = ("# The national spirits the Gazetteer's players asked for (scripts/requests_made.py)\nideas = {\n"
                 "\tcountry = {\n" + "".join(ideas) + "\t}\n}\n") if ideas else ""
    return trait_text, idea_text, loc, history, sprites
