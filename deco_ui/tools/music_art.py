"""The music player (musicplayer.gui, music_station_base.gui, music_station_classic.gui) and the top bar's music controls
in the deco style, at the game's paths and sizes (2026-10-19, the author: "Please also style the music controller and
the music player to better match the ui, and in the case of the controller popup, make it fit in better as currently it
just kinda pops in out of nowhere").

- the faceplate (musicplayer_header_bg, 594 x 121): a lacquer plate, the track's dark well in the middle of its upper
  half (the game's, x 120 to 482, where the track's name and times are written), a gilt loudspeaker in a sunburst
  either side (the game's megaphones), and the control rail under it (x 20 to 574) for the buttons and the volume;
- the buttons: previous and next (39 x 39), play / pause (2 frames of 69 x 40), the station's music and shuffle
  (3 frames of 71 x 39: the note and flag, shuffle, shuffle off), the volume's fill (75 x 16), as chamfered lacquer
  plates with gilt glyphs, the game's glyphs drawn again;
- the track list on its ivory sheet (the core skin's paper, where the typewriter text is dark): a track's rule (518 x
  30, the dotted line and the margin line at x 467 in bronze), the playing track's pointer (610 x 21, at x 501) and a
  disabled track's line through it (501 x 21);
- the controller under the top bar's music button (the game's playlist_bg strip, 228 x 42, slid in from the right): a
  tab hanging from the tray under the button, its own picture (TAB, make_topbar.py moves the window there and slides it
  down from behind the tray), its three buttons (pause / play 2 frames of 33 x 33, next 33 x 33, the player 32 x 32);
- for musicplayer.gui (make_music.py): the station box's plate (190 x 122) and its note (64 x 64), the music button's
  own note, as the top bar's.

gen_textures.py adds them (keys mu_*).
"""
from art_util import BAR_FILL, GOLD, STRIPES, bar, frames
from icons import icon

M = "gfx/interface/topbar/musicplayer/"
V = "gfx/interface/valsora_deco/"
INK = "#E3C77E"
LIT = "#F1DC9C"
BRONZE = "rgba(122,92,38,.75)"
DEFS = ('<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F1DC9C"/>'
        '<stop offset="1" stop-color="#8B6A2C"/></linearGradient></defs>')


def svg(w, h, body):
    return f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="position:absolute;left:0;top:0">{DEFS}{body}</svg>'


def cham(x0, y0, x1, y1, c):
    return f"M{x0 + c},{y0}L{x1 - c},{y0}L{x1},{y0 + c}L{x1},{y1 - c}L{x1 - c},{y1}L{x0 + c},{y1}L{x0},{y1 - c}L{x0},{y0 + c}Z"


def well(x0, y0, x1, y1, c=5, fill="#080C0F"):
    return (f'<path d="{cham(x0, y0, x1, y1, c)}" fill="{fill}" stroke="rgba(201,165,90,.55)"/>'
            f'<path d="{cham(x0 + 3, y0 + 3, x1 - 3, y1 - 3, max(1, c - 2))}" fill="none" stroke="rgba(201,165,90,.15)"/>')


def speaker(cx, cy):
    """a loudspeaker: a gilt rim round a dark cone, its rings and a lit dome, in a fan of rays"""
    rays = "".join(f'<path d="M{cx},{cy}L{cx + 46 * __import__("math").cos(a / 57.2958):.1f},'
                   f'{cy - 46 * __import__("math").sin(a / 57.2958):.1f}" stroke="rgba(227,199,126,.22)" stroke-width="2.4"/>'
                   for a in range(-10, 191, 12))
    return (f'<g clip-path="url(#top)">{rays}</g>'
            f'<circle cx="{cx}" cy="{cy}" r="19" fill="#0B1014" stroke="url(#g)" stroke-width="2"/>'
            f'<circle cx="{cx}" cy="{cy}" r="14.5" fill="#141E24" stroke="rgba(201,165,90,.5)"/>'
            f'<circle cx="{cx}" cy="{cy}" r="10" fill="none" stroke="rgba(201,165,90,.35)"/>'
            f'<circle cx="{cx}" cy="{cy}" r="5" fill="url(#g)"/>'
            f'<circle cx="{cx - 1.5}" cy="{cy - 1.5}" r="1.6" fill="#FFF6D8" opacity=".7"/>')


HEAD = dict(w=594, h=121, well=(118, 9, 476, 61), rail=(20, 69, 574, 113), speakers=(66, 528), cy=35)


def header():
    w, h = HEAD["w"], HEAD["h"]
    x0, y0, x1, y1 = HEAD["well"]
    r0, r1, r2, r3 = HEAD["rail"]
    body = (f'<clipPath id="top"><rect x="10" y="7" width="{w - 20}" height="58"/></clipPath>'
            + "".join(speaker(cx, HEAD["cy"]) for cx in HEAD["speakers"])
            + well(x0, y0, x1, y1, 7)
            + f'<path d="M{x0 + 10},{y1 - 9}H{x1 - 10}" stroke="rgba(201,165,90,.18)"/>'
            + well(r0, r1, r2, r3, 7, "#0A1013")
            + "".join(f'<path d="M{x},{(r1 + r3) / 2 - 4}L{x + 4},{(r1 + r3) / 2}L{x},{(r1 + r3) / 2 + 4}L{x - 4},{(r1 + r3) / 2}Z" '
                      f'fill="{INK}"/>' for x in (r0 + 10, r2 - 10)))
    return (f'<div style="position:absolute;left:3px;top:3px;width:{w - 6}px;height:{h - 6}px">{bar(c=9)}</div>'
            + svg(w, h, body))


# ------------------------------------------------------------------ buttons: a chamfered plate and a gilt glyph
def plate(w, h, c, glyph, m=2.5):
    return svg(w, h, f'<path d="{cham(m, m, w - m, h - m, c)}" fill="#0F171B" stroke="url(#g)" stroke-width="1.4"/>'
                     f'<path d="{cham(m + 2.5, m + 2.5, w - m - 2.5, h - m - 2.5, max(1, c - 1.5))}" fill="none" '
                     f'stroke="rgba(241,220,156,.18)"/>{glyph}')


def tri(cx, cy, s, flip=False):
    """a play triangle s tall, its middle at (cx, cy), pointing right (left when flip)"""
    d = -1 if flip else 1
    return f'<path d="M{cx - d * s * .45},{cy - s / 2}L{cx + d * s * .5},{cy}L{cx - d * s * .45},{cy + s / 2}Z" fill="{INK}"/>'


def bars(cx, cy, s):
    return (f'<rect x="{cx - s * .4}" y="{cy - s / 2}" width="{s * .26}" height="{s}" fill="{INK}"/>'
            f'<rect x="{cx + s * .14}" y="{cy - s / 2}" width="{s * .26}" height="{s}" fill="{INK}"/>')


def skip(cx, cy, s, back=False):
    d = -1 if back else 1
    return tri(cx - d * s * .12, cy, s, back) + f'<rect x="{cx + d * s * .42 - (s * .14 if not back else 0)}" y="{cy - s / 2}" width="{s * .14}" height="{s}" fill="{INK}"/>'


def note_flag(cx, cy):
    """the station's own music: a quaver and a flag (the game's)"""
    return (f'<ellipse cx="{cx - 13}" cy="{cy + 6}" rx="3.6" ry="2.8" transform="rotate(-20 {cx - 13} {cy + 6})" fill="{INK}"/>'
            f'<path d="M{cx - 9.8},{cy + 5}V{cy - 9}Q{cx - 4},{cy - 6.5} {cx - 3.5},{cy - 1}" fill="none" stroke="{INK}" '
            'stroke-width="2" stroke-linecap="round"/>'
            f'<path d="M{cx + 4},{cy + 9}V{cy - 9}" stroke="{INK}" stroke-width="2"/>'
            f'<path d="M{cx + 5},{cy - 9}H{cx + 15}L{cx + 12},{cy - 5}L{cx + 15},{cy - 1}H{cx + 5}Z" fill="{INK}"/>')


def shuffle(cx, cy, off=False):
    g = (f'<path d="M{cx - 14},{cy - 5}H{cx - 8}C{cx - 2},{cy - 5} {cx + 1},{cy + 5} {cx + 8},{cy + 5}H{cx + 11}'
         f'M{cx - 14},{cy + 5}H{cx - 8}C{cx - 2},{cy + 5} {cx + 1},{cy - 5} {cx + 8},{cy - 5}H{cx + 11}" fill="none" '
         f'stroke="{INK}" stroke-width="2.2"/>'
         f'<path d="M{cx + 10},{cy - 9}L{cx + 15},{cy - 5}L{cx + 10},{cy - 1}Z M{cx + 10},{cy + 1}L{cx + 15},{cy + 5}L{cx + 10},{cy + 9}Z" fill="{INK}"/>')
    if off:
        g = (f'<g opacity=".55">{g}</g><path d="M{cx - 8},{cy - 9}L{cx + 8},{cy + 9}M{cx + 8},{cy - 9}L{cx - 8},{cy + 9}" '
             'stroke="#0B1014" stroke-width="5" stroke-linecap="round"/>'
             f'<path d="M{cx - 8},{cy - 9}L{cx + 8},{cy + 9}M{cx + 8},{cy - 9}L{cx - 8},{cy + 9}" stroke="#EE8C7E" '
             'stroke-width="2.6" stroke-linecap="round"/>')
    return g


def playlist(cx, cy):
    return ("".join(f'<path d="M{cx - 8},{cy - 6 + 4 * i}H{cx + (6 if i < 2 else 1)}" stroke="{INK}" stroke-width="1.8"/>'
                    for i in range(4))
            + f'<path d="M{cx + 6},{cy + 3}V{cy + 11}M{cx + 2},{cy + 7}H{cx + 10}" stroke="{LIT}" stroke-width="1.8"/>')


def volume():
    """the volume's fill: a gilt bar in its well (the game draws as much of it as the volume)"""
    return svg(75, 16, f'<path d="{cham(1.5, 3.5, 73.5, 12.5, 3)}" fill="#0B1014" stroke="rgba(201,165,90,.6)"/>'
                       '<linearGradient id="v" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F1DC9C"/>'
                       '<stop offset="1" stop-color="#9A7634"/></linearGradient>'
                       f'<path d="{cham(3.5, 5.5, 71.5, 10.5, 2)}" fill="url(#v)"/>')


# ------------------------------------------------------------------ the track list on the ivory sheet
def track_rule():
    return svg(518, 30, f'<path d="M1,27.5H513" stroke="{BRONZE}" stroke-dasharray="1.5 2.5"/>'
                        f'<path d="M467.5,0V27M469.5,0V27" stroke="rgba(122,92,38,.45)"/>')


def playing():
    return svg(610, 21, f'<path d="M502,5L512,11L502,17Z" fill="#2E6E60" stroke="#8B6A2C" stroke-linejoin="round"/>')


def disabled():
    return svg(501, 21, '<linearGradient id="d" x1="0" x2="1"><stop offset="0" stop-color="#8E2A24"/>'
                        '<stop offset=".7" stop-color="#8E2A24" stop-opacity=".8"/><stop offset="1" stop-color="#8E2A24" '
                        'stop-opacity="0"/></linearGradient><rect x="5" y="10" width="358" height="2" fill="url(#d)"/>')


# ------------------------------------------------------------------ the controller's tab under the music button
# on screen: from x 1478 (the music button's cut ends there) under the tray (its foot at y 108), 120 x 42; the buttons
# 6 px in, 4 px apart. Hidden it sits behind the tray (y 64, where the tray's picture is opaque), and slides down
TAB = dict(x=1478, y=107, hidden_y=64, w=120, h=42, buttons=((7, 4), (44, 4), (81, 5)))


def tab():
    w, h = TAB["w"], TAB["h"]
    return (f'<div style="position:absolute;inset:0;background:{GOLD};clip-path:polygon(0 0,{w}px 0,{w}px {h - 9}px,'
            f'{w - 9}px {h}px,9px {h}px,0 {h - 9}px)"></div>'
            f'<div style="position:absolute;left:1px;top:0;right:1px;bottom:1px;background:{STRIPES},{BAR_FILL};'
            f'clip-path:polygon(0 0,{w - 2}px 0,{w - 2}px {h - 9.4}px,{w - 10.4}px {h - 1}px,8.4px {h - 1}px,0 {h - 9.4}px)"></div>'
            + svg(w, h, f'<path d="M4.5,2V{h - 10.5}L10.5,{h - 4.5}H{w - 10.5}L{w - 4.5},{h - 10.5}V2" fill="none" '
                        'stroke="rgba(201,165,90,.35)"/>'))


# the station box (musicplayer.gui's radio_decoration, 190 x 122): the note in a well (make_music.py puts it at
# note_xy) and the box's title under it (title_y)
STATION = dict(well_y1=76, note=44, note_xy=(73, 20), title_y=84)


def small(glyph):
    return plate(33, 33, 6, glyph, 2)


ADDS = [
    ("mu_header", M + "musicplayer_header_bg.dds", 594, 121, header),
    ("mu_prev", M + "musicplayer_previous_button.dds", 39, 39, lambda: plate(39, 39, 8, skip(19.5, 19.5, 14, True))),
    ("mu_next", M + "musicplayer_next_button.dds", 39, 39, lambda: plate(39, 39, 8, skip(19.5, 19.5, 14))),
    ("mu_play_pause", M + "musicplayer_play_pause_button.dds", 138, 40,
     lambda: frames(138, 40, plate(69, 40, 9, tri(34.5, 20, 16)), plate(69, 40, 9, bars(34.5, 20, 16)))),
    ("mu_shuffle", M + "toggle_shuffle_buttons.dds", 213, 39,
     lambda: frames(213, 39, plate(71, 39, 9, note_flag(35.5, 19.5)), plate(71, 39, 9, shuffle(35.5, 19.5)),
                    plate(71, 39, 9, shuffle(35.5, 19.5, True)))),
    ("mu_volume", M + "music_vol_progress.dds", 75, 16, volume),
    ("mu_track_rule", M + "music_player_entry_bg.dds", 518, 30, track_rule),
    ("mu_playing", M + "selected_song.dds", 610, 21, playing),
    ("mu_disabled", M + "disabled_song.dds", 501, 21, disabled),
    ("mu_small_pause", M + "music_pause_button.dds", 66, 33,
     lambda: frames(66, 33, small(tri(16.5, 16.5, 12)), small(bars(16.5, 16.5, 12)))),
    ("mu_small_next", M + "music_next_button.dds", 33, 33, lambda: small(skip(16.5, 16.5, 11))),
    ("mu_small_player", M + "musicplayer_button.dds", 32, 32, lambda: plate(32, 32, 6, playlist(16, 15.5), 2)),
    ("mu_tab", V + "music_tab.dds", TAB["w"], TAB["h"], tab),
    ("mu_station", V + "music_station.dds", 190, 122,
     lambda: bar(c=8) + svg(190, 122, well(8, 8, 182, STATION["well_y1"], 5, "#0A1013"))),
    ("mu_note", V + "music_note.dds", STATION["note"], STATION["note"],
     lambda: f'<div style="position:absolute;inset:0">{icon("music", STATION["note"], INK, 1.4)}</div>'),
]
