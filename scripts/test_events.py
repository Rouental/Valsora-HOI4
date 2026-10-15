"""Rouental's test decisions (the author, 2026-10-15: "Give decisions to Rouental to spawn generic events of each
type / layout, and a superevent for testing. The superevent should use the clown music and placeholder anime girl
image").

A decision category, "Test Events", shown to Rouental when a player leads it: one decision per kind of event window
the game has, free and repeatable, each firing a placeholder event at once:
  - a country event, the report window most of the game's events use (title, picture, text, options);
  - a long country event with four options (the window stretches with its text; a long option takes two lines);
  - a state event, fired from Rouental's capital (the report window, the state as its subject);
  - a news event (the broadsheet), and a major news event (the broadsheet, sent to every country);
  - a leader event, about one of Rouental's generals (the window with the leader's portrait);
  - an operative event (the dossier window; an operative is created first if Rouental has none; needs La
    Résistance, so the decision shows only with it);
  - the test superevent (`superevents.py`, "rou_test": the anime picture and Entry of the Gladiators).
The texts are Claude's placeholders; no option does anything. Take the category out (`write_files`' call in
build_mod.py and its LOCALISATION) when the testing is done, like Devlon's test spirits.
"""
CATEGORY = "ROU_test_events"
NS = "valsora_test"

# id, decision, icon, how it fires (in Rouental's scope), the event, its texts (title, description, options)
EVENTS = [
    dict(n=1, decision="ROU_test_country_event", name="Test: a Country Event", icon="GFX_decision_generic_research",
         fire=f"country_event = {{ id = {NS}.1 }}",
         event=f"""country_event = {{
	id = {NS}.1
	title = {NS}.1.t
	desc = {NS}.1.desc
	picture = GFX_report_event_generic_read_write
	is_triggered_only = yes
	option = {{ name = {NS}.1.a }}
	option = {{ name = {NS}.1.b }}
}}""",
         loc=dict(t="A Test of the Country Event",
                  desc="This is a country event, the kind most of the game's events are: a title, a picture, a short "
                    "text and its options. Whichever you choose, nothing happens.",
                  a="Very good.", b="Show me another.")),
    dict(n=2, decision="ROU_test_long_event", name="Test: a Long Event, Four Options", icon="GFX_decision_generic_political_discourse",
         fire=f"country_event = {{ id = {NS}.2 }}",
         event=f"""country_event = {{
	id = {NS}.2
	title = {NS}.2.t
	desc = {NS}.2.desc
	picture = GFX_report_event_generic_conference
	is_triggered_only = yes
	option = {{ name = {NS}.2.a }}
	option = {{ name = {NS}.2.b }}
	option = {{ name = {NS}.2.c }}
	option = {{ name = {NS}.2.d }}
}}""",
         loc=dict(t="A Longer Test, With Four Options",
                  desc="The Prince's council sat for nine hours today and agreed on nothing, which the court gazette "
                    "reports as a great success. The Chancellor spoke at length on the price of bread, the Marshal on "
                    "the price of tanks, and the Archbishop on the price of both in the life to come.\\n\\nThis event "
                    "has a long text and four options, to see the window stretch with its text and the options stack "
                    "beneath it. The second option is long on purpose, to see how its plate takes two lines.",
                  a="The first option.",
                  b="A second option, a good deal longer than the others, to see how it wraps onto a second line.",
                  c="A third option.", d="And a fourth.")),
    dict(n=3, decision="ROU_test_state_event", name="Test: a State Event", icon="GFX_decision_generic_construction",
         fire=f"capital_scope = {{ state_event = {{ id = {NS}.3 }} }}",
         event=f"""state_event = {{
	id = {NS}.3
	title = {NS}.3.t
	desc = {NS}.3.desc
	picture = GFX_report_event_generic_construction_site
	is_triggered_only = yes
	option = {{ name = {NS}.3.a }}
}}""",
         loc=dict(t="A Test in [ROOT.GetName]",
                  desc="This is a state event: it happens in a state, here [ROOT.GetName], and its options act on the "
                    "state. It opens in the same window as a country event.",
                  a="Noted.")),
    dict(n=4, decision="ROU_test_news_event", name="Test: a News Event", icon="GFX_decision_generic_civil_support",
         fire=f"news_event = {{ id = {NS}.4 }}",
         event=f"""news_event = {{
	id = {NS}.4
	title = {NS}.4.t
	desc = {NS}.4.desc
	picture = GFX_news_event_generic_rally
	is_triggered_only = yes
	major = no
	option = {{ name = {NS}.4.a }}
}}""",
         loc=dict(t="Rêverie Rehearses the News",
                  desc="Our correspondent in the capital writes that the Prince's printers ran a test edition of the "
                    "evening paper today, with a headline, a picture and a column of text, to see how the news would "
                    "look. Readers are assured that nothing in it is true.",
                  a="Interesting.")),
    dict(n=5, decision="ROU_test_major_news_event", name="Test: a Major News Event", icon="GFX_decision_generic_nationalism",
         fire=f"news_event = {{ id = {NS}.5 }}",
         event=f"""news_event = {{
	id = {NS}.5
	title = {NS}.5.t
	desc = {NS}.5.desc
	picture = GFX_news_event_generic_parliament
	is_triggered_only = yes
	major = yes
	option = {{ name = {NS}.5.a }}
}}""",
         loc=dict(t="Extra! A Major Test Shakes Valsora",
                  desc="Every capital of Valsora received the same telegram this morning: a major news event, which "
                    "every country sees, not only the one it happened to. Governments from Arpino to Zwintern are "
                    "said to be studying it closely.",
                  a="Extraordinary.")),
    dict(n=6, decision="ROU_test_leader_event", name="Test: a Leader Event", icon="GFX_decision_generic_army_support",
         fire=f"random_army_leader = {{ unit_leader_event = {{ id = {NS}.6 }} }}",
         available="any_army_leader = { always = yes }",
         event=f"""unit_leader_event = {{
	id = {NS}.6
	title = {NS}.6.t
	desc = {NS}.6.desc
	is_triggered_only = yes
	option = {{ name = {NS}.6.a }}
}}""",
         loc=dict(t="A Word With the General",
                  desc="[This.GetName] reports for a test of the leader event, the window that shows a commander's "
                    "portrait beside the text.",
                  a="Dismissed.")),
    dict(n=7, decision="ROU_test_operative_event", name="Test: an Operative Event", icon="GFX_decision_generic_operation",
         fire=f"""if = {{
				limit = {{ num_of_operatives < 1 }}
				create_operative_leader = {{ bypass_recruitment = yes }}
			}}
			random_operative = {{ operative_leader_event = {{ id = {NS}.7 }} }}""",
         visible='has_dlc = "La Resistance"',
         event=f"""operative_leader_event = {{
	id = {NS}.7
	title = {NS}.7.t
	desc = {NS}.7.desc
	is_triggered_only = yes
	option = {{ name = {NS}.7.a }}
}}""",
         loc=dict(t="A Test in the Shadows",
                  desc="[This.GetName], one of our operatives, has been called in for a test of the operative event, "
                    "the window with the agent's dossier.",
                  a="Back to work.")),
]
# the superevent's decision: superevents.py's "rou_test"
SUPEREVENT = dict(decision="ROU_test_superevent", name="Test: the Superevent", icon="GFX_decision_generic_prepare_civil_war",
                  fire="valsora_superevent_rou_test = yes")


def decision(d):
    lines = [f"\t{d['decision']} = {{", f"\t\ticon = {d['icon']}"]
    if d.get("visible"):
        lines.append(f"\t\tvisible = {{ {d['visible']} }}")
    if d.get("available"):
        lines.append(f"\t\tavailable = {{ {d['available']} }}")
    return lines + ["\t\tfire_only_once = no", "\t\tcost = 0", "\t\tcomplete_effect = {",
                    f"\t\t\t{d['fire']}", "\t\t}", "\t\tai_will_do = { base = 0 }", "\t}"]


def write_files(write):
    write("common/decisions/categories/valsora_test_events.txt", "\n".join([
        f"{CATEGORY} = {{",
        "\ticon = GFX_decision_category_generic",
        "\tpicture = GFX_decision_cat_picture_operational_planning",
        "\tallowed = { original_tag = ROU }",
        "\tvisible = { is_ai = no }",
        "\tpriority = 200",
        "}", ""]))
    body = [f"{CATEGORY} = {{"]
    for d in EVENTS + [SUPEREVENT]:
        body += decision(d)
    write("common/decisions/valsora_test_events.txt", "\n".join(body + ["}", ""]))
    write(f"events/{NS}.txt", "\n\n".join([f"add_namespace = {NS}"] + [e["event"] for e in EVENTS]) + "\n")


LOCALISATION = (
    [f' {CATEGORY}:0 "Test Events"',
     f' {CATEGORY}_desc:0 "One of each kind of event, to see how its window looks. They do nothing."']
    + [f' {d["decision"]}:0 "{d["name"]}"' for d in EVENTS + [SUPEREVENT]]
    + [f' {NS}.{e["n"]}.{k}:0 "{v}"' for e in EVENTS for k, v in e["loc"].items()])
