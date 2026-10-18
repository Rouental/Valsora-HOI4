"""The side panels other than the politics screen (make_panels.py), v0.5.

Each panel slides in under the top bar like the politics screen (layout_politics): its top is flush with the
band's bottom (TOP), and it leaves a notch where the flag medallion and the decisions seal hang, which show
through it (side panels are drawn over the top bar). Panel-local pixels; the notch's place in a panel depends
on where the panel sits on screen (most at x -6, the construction screen at -9, the faction pings at 0).

  header strip   y 0 .. NB: lacquer round the notch (its own picture, one per width and x), the game's title
                 moved right of the notch in gilt capitals, the close diamond, the panel's header buttons
                 beside it, a gilt rule at RULE_Y
  body           from NB down: the politics screen's body tile; the game's own boxes draw over it
  content        every other element of the panel moves down by the panel's `shift`, so it clears the seal
                 (72 for most: the game's content starts at y 40-45, the seal ends at 107)

Bottom-anchored elements stay where they are, and boxes that run to the bottom (100%%, or a negative height:
"to the parent's edge minus n") end where they did, so moving content down only makes the lists shorter.
"""
import layout_politics as LP

TOP = LP.TOP                      # 62: the band's bottom
OPEN_MS = LP.OPEN_MS              # 0: a panel opens at once from vanilla's off-screen position (layout_politics)
NB = LP.NOTCH_BOTTOM              # 106: the header strip's height (the seal's bottom)
SHIFT = 72                        # how far the game's content moves down (scratchpad survey: 62-72 needed)
HX = LP.HX                        # 190: the title's left edge (right of the notch)
TITLE_Y, TITLE_H = 16, 60         # the title box: one or two lines of title_24, centred in it
RULE_Y = LP.HEAD_RULE_Y           # 88: the rule under the title (as the politics screen)
CLOSE = (-52, 14)                 # the close diamond (UPPER_RIGHT), as the politics screen
TITLE_FONT = "valsora_deco_title_24"
TITLE_FONT_SMALL = "valsora_deco_title_18"
CONTROLS_Y = 18                   # the game's header buttons, centred on the close diamond's row


# ---------------------------------------------------------------- the notch for a panel at screen x panel_x
def notch_poly(panel_x):
    return LP.offset_poly([(x - panel_x, y - TOP) for x, y in LP._notch_poly_screen()], -LP.NOTCH_OVERLAP)


def notch_outline(d, panel_x):
    return LP.offset_poly(notch_poly(panel_x), d)


def notch_bands(panel_x):
    """the notch as rectangles (x0, y0, x1, y1), one per band of rows"""
    return [(x0, y0, x1, y1) for y0, y1, x0, x1 in LP.bands(notch_poly(panel_x))]


def blockers(width, panel_x):
    """rectangles covering the header strip beside the notch: invisible containers there catch the clicks that
    the panel's own (click-through) background no longer does"""
    out = []
    for x0, y0, x1, y1 in notch_bands(panel_x):
        if x0 > 0:
            out.append((0, y0, x0, y1))
        if x1 < width:
            out.append((x1, y0, width, y1))
    return out


# ---------------------------------------------------------------- the panels
# title: the game's title box (path below the window); header_bg: the game's header pictures (hidden);
# controls: the game's header buttons that stay in the header (path -> new position, or None to keep it);
# x, w: the panel's shown x and width (checked against the game's file); head_w: the header picture's width when
# the panel draws wider than its window (the construction screen's building list hangs out of it); shift: the
# content's offset (child_shift: per element); height: a fixed-height window's, which grows by the shift;
# attrs: other attributes to set (path -> dict; the path's first element counts as the header's and stays put)
# inner_attrs: attributes of elements inside the content, which moves down as usual
# the diplomacy panel's header and leader block (v0.11, the author, 2026-10-18: "the bar with ideology, stability, names,
# etc. should be level with the flag ... the leader's name can run off the screen if too long ... Diplomacy tab isn't
# great. Like the intel, the box isn't aligned with the flag. Focus icon isn't centered ... diplomacy should look as
# much like politics as possible ... larger portraits like Krionik's start to get cut off"). The flag's frame is the
# bar's 71 px tall (diplomacy_art.FLAG's mat) and moves to the bar's top (y -4) and the tabs' left edge (x 15); the
# names stop 4 px before the opinion box (the game's x 341 + 33), so a long one is cut with "..." where it would have
# run under it; the portrait is the game's at diplomacy_art.PORTRAIT_SCALE inside the flatter arch of its frame
# (diplomacy_art.LEADER["portrait"], the frame at the block's (13, 0))
DIPLO_NAME_W = 341 + 33 - 4 - 245
DIPLO = {"country_info>diplo_flag_frame": dict(position=(15 - 8, -4 - 1)),
         "country_info>diplo_country_flag": dict(position=(15 - 8 + 26, -4 - 1 + 11)),
         "country_info>country_name": dict(maxWidth=DIPLO_NAME_W),
         "country_info>faction>faction_name": dict(maxWidth=DIPLO_NAME_W),
         "country_info>leader_name": dict(maxWidth=DIPLO_NAME_W),
         "country_info>diplomacy_tab_top>leader_portrait": dict(position=(13 + 12, 28), scale="0.66")}

# the decisions tab's events box and rows (v0.11, decisions_art.py): the game wrote their texts in its typewriter faces,
# dark ink for the paper it drew them on; on the Deco UI's lacquer they take its light faces (elements of the file's
# own top-level windows, not of the panel)
DECISION_FONTS = {"event_header>name_text": dict(font="valsora_deco_heading_22"),
                  "event_item>name_text": dict(font="valsora_deco_body_15"),
                  "event_item>timer_text": dict(font="valsora_deco_body_15")}

PANELS = {
    "army": dict(file="countryarmyview.gui", window="countryarmyview", title="army_title", header_bg=["army_header_bg"],
                 controls={"naval_hq_open": (-171, CONTROLS_Y), "destroyed_ships_open": (-131, CONTROLS_Y),
                           "details_open": (-91, CONTROLS_Y)},
                 preview_hide=["navy_header", "navy_units", "air_header", "air_units"]),
    "construction": dict(file="countryconstructionsview.gui", window="countryconstructionsview", x=-9,
                         title="construction_title", header_bg=["production_header_bg"], head_w=700, extra_w=150,
                         controls={"count_container": (-112, 24), "minimize": None, "expand": None, "temp": None},
                         close=(98, 14), shift=74, child_shift={"possible_constructions": NB - 40},
                         preview_hide=["tutorial_glow", "expand"]),
    "decisions": dict(file="countrydecisionview.gui", window="countrydecisionview", title="decisionview_title",
                      header_bg=["production_header_bg"], toplevel_attrs=DECISION_FONTS),
    "deployment": dict(file="countrydeploymentview.gui", window="countrydeploymentview", title="deployment_title",
                       header_bg=["production_header_bg"]),
    "diplomacy": dict(file="countrydiplomacyview.gui", window="countrydiplomacyview", title="diplomacy_title",
                      header_bg=["production_header_bg"], controls={"player_info_box": (270, 62)},
                      preview_hide=["country_list", "intel_ledger_container"], inner_attrs=DIPLO),
    "intelligence": dict(file="countryintelligenceagencyview.gui", window="countryintelligenceagencyview",
                         title="intelligenceagencyview_title", header_bg=["production_header_bg"],
                         preview_hide=["before_creation_panel", "agency_crypto"]),
    "logistics": dict(file="countrylogisticsview.gui", window="countrylogisticsview", title="logistics_title",
                      header_bg=["logistics_header_bg"],
                      controls={"viewing_flag": (445, 25), "viewing_flag_border": (440, 20)}),
    "occupation": dict(file="countryoccupationview.gui", window="countryoccupationview", title="title",
                       header_bg=["header_bg"], clear=["bg_cointainer"],
                       controls={"garrison_log_open": (-138, CONTROLS_Y), "equipment_open": (-98, CONTROLS_Y)}),
    "officers": dict(file="countryofficercorpview.gui", window="countryofficercorpview", title="army_title",
                     header_bg=["army_header_bg"]),
    "production": dict(file="countryproductionlineview.gui", window="countryproductionlineview",
                       title="production_title", header_bg=["production_header_bg"]),
    "research": dict(file="countrytechnologyview.gui", window="countrytechnologyview", title="research_title",
                     header_bg=["production_header_bg"], preview_hide=["facilities"]),
    "trade": dict(file="countrytradeview.gui", window="countrytradeview", w=689, title="trade_title",
                  header_bg=["production_header_bg"]),
    "faction": dict(file="factions/countryfactionview.gui", window="countryfactionview", title="faction_title",
                    header_bg=["faction_header_bg"], shift=119,   # its banner picture starts at y -10
                    preview_hide=["tab_section_view_full_overlay_container"],
                    # v0.9.1, the user: "The name of the faction gets cut off if too long": the Association's is
                    # 323 px in the deco capitals, the game's box 300; it runs to the star box now (x 442)
                    inner_attrs={"header_section>faction_name": dict(position=(116, 60), maxWidth=326)}),
    "faction_setup": dict(file="factions/new_faction_window.gui", window="faction_setup_window",
                          title="faction_title>title", header_bg=["faction_title>faction_header_bg"],
                          close_path="faction_title>close_button", header=["faction_title"]),
    "faction_pings": dict(file="factions/faction_ping_window.gui", window="faction_ping_window", x=0, w=500,
                          height=640, title="title", title_lines=1, controls={"flag": (-104, 22)},
                          attrs={"switch": dict(position=(184, 62), maxWidth=262, maxHeight=16, format="left",
                                                font="valsora_deco_body_13")}),
    "market": dict(file="international_market/countryinternationalmarketview.gui",
                   window="countryinternationalmarketview", title="International_market_title",
                   header_bg=["production_header_bg"],
                   preview_hide=["seller_specific_tab_window", "buyer_specific_tab_window"]),
}

# windows that open beside a panel (sub-windows: equipment, lend-lease, templates ...): flush under the band too
# (the politics screen's four are moved by make_politics.py)
BESIDE = {
    "countrydeploymentview.gui": ["templatedeploymentwindow"],
    "countrydiplomacyview.gui": ["lend_lease_equipment_window", "incoming_lend_lease_equipment_window"],
    "countrylogisticsview.gui": ["logistics_info_window", "logistics_fuel_window"],
    "countryproductionlineview.gui": ["navy_repair_window", "production_equipment_window_military",
                                      "production_equipment_window", "production_deployment_window",
                                      "ship_name_list_window"],
    "countryofficercorpview.gui": ["armyhqtemplatewindow"],
    "factions/countryfactionview.gui": ["faction_list_window"],
    "detailedwindows.gui": ["shipswindow", "planeswindow"],
    "equipmentoverview.gui": ["equipment_overview_window"],
    "command_character_view.gui": ["command_character_view_window"],
}


def hx(panel_x):
    """the title's left edge: right of the notch, where the politics screen's is"""
    return LP.HX + (LP.PANEL_X - panel_x)


HEADS = sorted({(s.get("head_w", s.get("w", 550)), s.get("x", -6)) for s in PANELS.values()})
HEAD_H = NB + 8                   # the header picture: the strip, plus the notch's edge round the seal's bottom


def head_sprite(w, x):
    return f"GFX_valsora_deco_panel_head_{w}_{'m' if x < 0 else ''}{abs(x)}"


def head_texture(w, x):
    return f"gfx/interface/valsora_deco/panels/head_{w}_{'m' if x < 0 else ''}{abs(x)}.dds"
