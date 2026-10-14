"""Valsora Deco icon set: the mockup's 24 px gilt line icons (1.4-1.6 px stroke, round caps).

v0.4 tried a detailed two-tone set; the user preferred these simpler line icons, so this is the set in use.
Subjects are modern-day (Valsora is set in the present): the army is a high-cut combat helmet with an
accessory rail and night-vision mount, deployment is the NATO division symbol, air is a delta-canard jet,
convoys are a container ship. The rest are the mockup's originals.

    icon(name, size=24, color="#E3C77E", sw=1.5) -> <svg> markup
"""
ICONS = {
    "gov": '<path d="M3 9.5L12 4l9 5.5z"/><path d="M5.5 11v7M9.8 11v7M14.2 11v7M18.5 11v7M3.5 20.5h17M4.5 18.5h15"/>',
    "research": '<path d="M9 3h6M10 3v6l-5.2 9.2A1.9 1.9 0 0 0 6.5 21h11a1.9 1.9 0 0 0 1.7-2.8L14 9V3"/><path d="M7.4 15h9.2"/>',
    "diplomacy": '<rect x="3" y="6" width="18" height="12.5"/><path d="M3 6.5l9 6.5 9-6.5"/><circle cx="12" cy="16" r="2.2"/>',
    "trade": '<path d="M12 4v16M7.5 20.5h9M5 7h14"/><path d="M5 7l-2.6 6a2.6 2.6 0 0 0 5.2 0zM19 7l-2.6 6a2.6 2.6 0 0 0 5.2 0z"/>',
    "construction": '<path d="M6.5 21V3.5M3.5 21h6M6.5 4.5h14M6.5 8.5l4-4M17.5 4.5V10"/><path d="M16 11.2a1.6 1.6 0 1 0 3 .6"/>',
    "production": '<path d="M3 20.5V11l5 3v-3l5 3v-3l5 3V4.5h3v16z"/><path d="M6.5 17.5h2M11 17.5h2M15.5 17.5h2"/>',
    # recruit & deploy: NATO division symbol (framed infantry cross under "XX")
    "deploy": '<path d="M3.5 10h17v10h-17z"/><path d="M3.5 10l17 10M20.5 10l-17 10"/><path d="M8 3.5l3 4M11 3.5l-3 4M13 3.5l3 4M16 3.5l-3 4"/>',
    "logistics": '<path d="M2.5 6.5h11v9.5h-11zM13.5 10h3.8l3.2 3.2V16h-7"/><circle cx="6.5" cy="17.5" r="1.8"/><circle cx="16.8" cy="17.5" r="1.8"/>',
    "intel": '<path d="M2 12s3.6-6 10-6 10 6 10 6-3.6 6-10 6-10-6-10-6z"/><circle cx="12" cy="12" r="3"/><path d="M12 2.5v2M12 19.5v2"/>',
    "decisions": '<path d="M6 3h9l4 4v14H6z"/><path d="M15 3v4h4M9 13.5l2.2 2.2 4.3-4.6"/>',
    "officer": '<path d="M12 3l2.2 4.5 5 .7-3.6 3.5.9 5L12 14.3l-4.5 2.4.9-5-3.6-3.5 5-.7z"/><path d="M6 21h12M8 18.5h8"/>',
    # army: modern high-cut combat helmet, side view: smooth shell with the ear cut-out, accessory rail,
    # night-vision mount at the brow
    "army": ('<path d="M3.5 15.5C3.5 9 7.5 4.5 13 4.5c5 0 8 3.8 8 9.4v3.1h-3.6c-.5-2.4-1.6-3.6-3.4-3.6h-2c-1.6 0-2.6 1-3 2.1H3.5z"/>'
             '<path d="M8.6 10.8h10.6"/><path d="M3.9 9.4l3.1-.4.2 3-3 .4"/>'),
    "navy": '<circle cx="12" cy="5" r="2"/><path d="M12 7v13.5M8 10.5h8M4.5 13.5a7.5 7.5 0 0 0 15 0"/>',
    # air: delta-canard jet, top view (exactly symmetric about x = 12)
    "air": '<path d="M12 2.5 L12.9 3.4 L13.4 5.6 L13.4 10 L20.6 16.2 L20.6 17.9 L13.4 15.6 L13.1 18.6 L15.5 20.3 L15.5 21.4 L12 20.9 L8.5 21.4 L8.5 20.3 L10.9 18.6 L10.6 15.6 L3.4 17.9 L3.4 16.2 L10.6 10 L10.6 5.6 L11.1 3.4z"/><path d="M13.4 8.2l2.8 1.4M10.6 8.2l-2.8 1.4"/>',
    "pp": ('<path d="M7 19c-3-2.5-4-6.5-2.6-10.5M17 19c3-2.5 4-6.5 2.6-10.5"/><path d="M5.2 15.5l-2-.8M4.4 12l-2-1.2M4.6 8.6l-1.6-1.8'
           'M18.8 15.5l2-.8M19.6 12l2-1.2M19.4 8.6l1.6-1.8"/><path d="M12 6.5l1.4 3 3.3.3-2.5 2.2.8 3.2L12 13.5l-3 1.7.8-3.2'
           '-2.5-2.2 3.3-.3z" fill="currentColor" stroke="none"/>'),
    "stability": '<path d="M5 5.5h14M6.5 3.5h11M7.5 7.5v10.5M12 7.5v10.5M16.5 7.5v10.5M5.5 18.5h13M4 20.5h16"/>',
    "war": '<path d="M6 21V3M6 4h12l-2.4 3.5L18 11H6"/>',
    "manpower": ('<circle cx="9" cy="8" r="2.8"/><path d="M3.5 19.5a5.5 5.5 0 0 1 11 0"/><circle cx="16.5" cy="9" r="2.2"/>'
                 '<path d="M14.8 14.2a4.4 4.4 0 0 1 6.2 4.3"/>'),
    "factory": '<path d="M3 20.5V11l5 3v-3l5 3v-3l5 3V4.5h3v16z"/>',
    # convoys: container ship (stacked containers, bridge aft)
    "convoy": '<path d="M2 14.5h20l-2.6 5H4.6z"/><path d="M3.8 14.5V8.5h2.6v6M8.5 14.5v-3h11v3M10.5 11.5v-3h7v3"/>',
    "fuel": '<path d="M6 6h8.5l3.5 3.5V21H6z"/><path d="M9 6V3.5h4M9 11.5l6 6M15 11.5l-6 6"/>',
    "command": '<path d="M12 4l2 4.2 4.6.6-3.3 3.2.8 4.6L12 14.4l-4.1 2.2.8-4.6L5.4 8.8l4.6-.6z"/><path d="M5 20l7-3 7 3"/>',
    "faction": '<circle cx="12" cy="8.2" r="4.4"/><circle cx="8.2" cy="14.6" r="4.4"/><circle cx="15.8" cy="14.6" r="4.4"/>',
    "nuke": ('<circle cx="12" cy="12" r="1.6" fill="currentColor"/><ellipse cx="12" cy="12" rx="9.5" ry="3.6"/>'
             '<ellipse cx="12" cy="12" rx="9.5" ry="3.6" transform="rotate(60 12 12)"/>'
             '<ellipse cx="12" cy="12" rx="9.5" ry="3.6" transform="rotate(120 12 12)"/>'),
    "menu": '<path d="M5 7h14M5 12h14M5 17h14"/>',
    "help": '<path d="M9 9a3 3 0 1 1 4.2 2.8c-.8.4-1.2 1-1.2 1.9V15"/><circle cx="12" cy="18.6" r=".6" fill="currentColor"/>',
    "market": ('<path d="M3.5 10l1.8-5.5h13.4l1.8 5.5"/><path d="M3.5 10a2.1 2.1 0 0 0 4.2 0 2.1 2.1 0 0 0 4.3 0 '
               '2.1 2.1 0 0 0 4.2 0 2.1 2.1 0 0 0 4.3 0"/><path d="M5 12.3V20.5h14v-8.2M10 20.5v-5h4v5"/>'),
    "music": '<path d="M9 18V5.5l10-2V16"/><circle cx="6.8" cy="18" r="2.3"/><circle cx="16.8" cy="16" r="2.3"/>',
    "search": '<circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.3 15.3l5.2 5.2"/>',
}
ICONS["supply"] = ICONS["logistics"]


def icon(name, size=24, color="#E3C77E", sw=1.5):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" style="display:block;color:{color}">'
            f'{ICONS[name]}</svg>')
