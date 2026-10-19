"""The production lines' and the trade list's own pictures, drawn by hand at the game's paths and sizes (2026-10-19, the
author's screenshots of v0.11: "The production screen doesn't have any boxes", "Trade screen has off artifacts and
lines"). v0.11 had them from make_panel_pictures.py's automatic translation of the game's pictures, which lost the
production line's boxes (the equipment's plate, the factory slots, the resource wells) and turned the scratches of the
game's metal into gilt specks along the trade rows; these replace them (make_panel_pictures.DRAWN).

Measured from the game's pictures (production_item.dds, the naval strip's third frame; the same layout):
- the header band, y 0 to 27, a well in it from x 356 to 475 (y 4 to 25);
- the equipment's plate, x 4 to 277, y 30 to 103: its priority arrows' column to x 30, its name band to y 48;
- the slots, 5 columns of 29 px from x 316 (to 460), rows y 32 to 53, 54 to 76, 77 to 99 (a naval line's strip shows 1,
  2 or 3 rows, its three frames);
- the resources' wells, x 465 to 507: y 33 to 53, 56 to 76, 80 to 100.
The trade row (3 frames of 648 x 45: the game's tan, green and grey) is a lacquer row with a gilt rim, jade when the
second frame, dim and hatched when the third; its wells are the game's elements, drawn over it.

gen_textures.py adds them (keys pl_*).
"""
G = "gfx/interface/"
RIM = "rgba(201,165,90,.55)"
FAINT = "rgba(201,165,90,.22)"
DEFS = ('<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E8CD84"/>'
        '<stop offset="1" stop-color="#8B6A2C"/></linearGradient>'
        '<linearGradient id="lac" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#18232A"/>'
        '<stop offset="1" stop-color="#0E1519"/></linearGradient>'
        '<linearGradient id="jade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2C665A"/>'
        '<stop offset="1" stop-color="#163A33"/></linearGradient>'
        '<pattern id="stripes" width="8" height="8" patternUnits="userSpaceOnUse"><rect width="1" height="8" '
        'fill="rgba(255,255,255,.025)"/></pattern>'
        '<pattern id="hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
        '<rect width="1.4" height="7" fill="rgba(201,165,90,.10)"/></pattern></defs>')

LINE = dict(w=511, h=108, header=27, header_well=(356, 4, 475, 25), plate=(4, 30, 277, 103), arrows_x=30, name_y=48,
            slots_x=316, slot_w=29, slots=5, slot_rows=((32, 53), (54, 76), (77, 99)),
            wells=(465, 507, ((33, 53), (56, 76), (80, 100))))


def svg(w, h, body):
    return f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="position:absolute;left:0;top:0">{DEFS}{body}</svg>'


def cham(x0, y0, x1, y1, c):
    return f"M{x0 + c},{y0}L{x1 - c},{y0}L{x1},{y0 + c}L{x1},{y1 - c}L{x1 - c},{y1}L{x0 + c},{y1}L{x0},{y1 - c}L{x0},{y0 + c}Z"


def well(x0, y0, x1, y1, c=3, fill="#080C0F", rim=RIM):
    return f'<path d="{cham(x0 + .5, y0 + .5, x1 - .5, y1 - .5, c)}" fill="{fill}" stroke="{rim}"/>'


def line_picture(rows=3, lit=False, tint="#12302A"):
    """a production line: the lacquer plate, the header band, the equipment's plate, the slots and the wells"""
    L = LINE
    w, h = L["w"], L["h"]
    rim = "url(#g)" if lit else RIM
    out = (f'<path d="{cham(.5, .5, w - .5, h - .5, 5)}" fill="url(#lac)" stroke="{rim}" stroke-width="{1.4 if lit else 1}"/>'
           f'<path d="{cham(.5, .5, w - .5, h - .5, 5)}" fill="url(#stripes)"/>'
           f'<path d="M1.5,{L["header"] + .5}H{w - 1.5}" stroke="{rim}"/>')
    if lit:
        out += (f'<path d="M5,1.5H{w - 5}L{w - 1.5},5V{L["header"]}H1.5V5Z" fill="url(#jade)" opacity=".75"/>'
                f'<path d="M8,3.5H{w - 8}" stroke="rgba(241,220,156,.35)"/>')
    else:
        out += f'<path d="M8,3.5H{w - 8}" stroke="rgba(241,220,156,.12)"/>'
    out += well(*L["header_well"], 3, "rgba(8,12,15,.85)")
    x0, y0, x1, y1 = L["plate"]
    out += (well(x0, y0, x1, y1, 4, tint) + f'<path d="M{x0 + 1},{L["name_y"] + .5}H{x1 - 1}" stroke="{FAINT}"/>'
            f'<path d="M{L["arrows_x"] + .5},{L["name_y"] + 1}V{y1 - 1}" stroke="{FAINT}"/>'
            f'<path d="M{x0 + 4},{y0 + 3.5}H{x1 - 4}" stroke="rgba(241,220,156,.10)"/>')
    for r in range(rows):
        ry0, ry1 = L["slot_rows"][r]
        for c in range(L["slots"]):
            sx = L["slots_x"] + c * L["slot_w"]
            out += well(sx, ry0, sx + L["slot_w"] - 1, ry1, 2, "#0A0F12", FAINT)
    wx0, wx1, wys = L["wells"]
    for wy0, wy1 in wys:
        out += well(wx0, wy0, wx1, wy1, 2)
    return svg(w, h, out)


def naval_selected():
    """the selected naval line's overlay (511 x 94): the game's lit band along the top, its rail down the right side
    (broken at y 52) and the short rule at the foot, in gilt and jade"""
    return svg(511, 94, '<path d="M2.5,2.5H508.5V22.5H2.5Z" fill="url(#jade)" stroke="url(#g)" stroke-width="1.2"/>'
                        '<path d="M6,5.5H505" stroke="rgba(241,220,156,.35)"/>'
                        '<path d="M507.5,22.5V50M507.5,55V89.5H452" fill="none" stroke="url(#g)" stroke-width="2"/>')


def trade_row(kind):
    w, h = 648, 45
    fill = {"normal": "url(#lac)", "active": "url(#jade)", "off": "#101519"}[kind]
    rim = {"normal": "url(#g)", "active": "url(#g)", "off": FAINT}[kind]
    body = (f'<path d="{cham(1.5, 3.5, w - 1.5, h - 3.5, 5)}" fill="{fill}" stroke="{rim}" stroke-width="1.2"/>'
            f'<path d="{cham(1.5, 3.5, w - 1.5, h - 3.5, 5)}" fill="url(#{"hatch" if kind == "off" else "stripes"})"/>'
            f'<path d="M8,6.5H{w - 8}" stroke="rgba(241,220,156,{.3 if kind == "active" else .14})"/>')
    return svg(w, h, body)


def frames3(*parts, w=648, h=45):
    return "".join(f'<div style="position:absolute;left:{i * w}px;top:0;width:{w}px;height:{h}px">{p}</div>'
                   for i, p in enumerate(parts))


ADDS = [
    ("pl_item", G + "production_item.dds", 511, 108, lambda: line_picture()),
    ("pl_selected", G + "production_line_selected.dds", 511, 108, lambda: line_picture(lit=True)),
    ("pl_naval_strip", G + "naval_production_item_slots_strip.dds", 1533, 108,
     lambda: frames3(*(line_picture(r, tint="#13283A") for r in (1, 2, 3)), w=511, h=108)),
    ("pl_naval_selected", G + "naval_production_line_selected.dds", 511, 94, naval_selected),
    ("pl_trade_row", G + "tradeview/country_trade_entry_bg_wide.dds", 1944, 45,
     lambda: frames3(trade_row("normal"), trade_row("active"), trade_row("off"))),
]
