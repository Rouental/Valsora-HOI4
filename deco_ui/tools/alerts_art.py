"""The top bar's alerts in the Deco style (the author, 2026-10-19: "while we can leave the icons for now, would it be
possible to make the outlines in the style of the deco ui? Gilt octagons again probably. Make sure the icons remain
centered"): the game's 70 alert pictures (47 x 42 each, the dark bevelled square baked in) drawn again as a gilt
octagon on lacquer under the game's own icons, which come from its second strip without backgrounds, each where the
game draws it in its cell; and the red, yellow and green glows round an alert (2 frames, blended: dim, lit) as
octagonal rings on the same outline. The diplomatic requests' pictures (global_diplorequest_icons) keep their own
bronze wreathed plates: their icons have no strip without them.

gen_textures.py draws ADDS (prefix al_)."""
from art_util import frames, img_tag, vanilla_frames
from PIL import Image

W, H, N = 47, 42, 70          # one alert's cell; the strip's frames
C = 9                         # the octagon's corner cut


def octagon(inset, w=W, h=H, c=C):
    i = inset
    return [(c, i), (w - c, i), (w - i, c), (w - i, h - c), (w - c, h - i), (c, h - i), (i, h - c), (i, c)]


def pts(p):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in p)


def plate():
    """one alert's plate: lacquer, a gilt rim, a hairline inside it"""
    return (f'<svg width="{W}" height="{H}" style="position:absolute;left:0;top:0">'
            '<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E8CD84"/>'
            '<stop offset="1" stop-color="#8B6A2C"/></linearGradient>'
            '<linearGradient id="f" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1C2830"/>'
            '<stop offset="1" stop-color="#0B1115"/></linearGradient></defs>'
            f'<polygon points="{pts(octagon(1.2))}" fill="url(#f)" stroke="url(#g)" stroke-width="1.6"/>'
            f'<polygon points="{pts(octagon(4.2, c=C - 1.8))}" fill="none" stroke="rgba(201,165,90,.32)" stroke-width="1"/>'
            '</svg>')


def icons():
    strip = Image.new("RGBA", (W * N, H))
    for i, f in enumerate(vanilla_frames("gfx/interface/alerts/global_alert_icons_no_backgrounds.dds", N)):
        strip.alpha_composite(f, (i * W, 0))
    return frames(W * N, H, *[plate()] * N) + img_tag(strip)


def glow(rgb):
    """the blink round an alert: frame 1 a faint ring, frame 2 the ring lit with its glow (the game blends the two)"""
    r, g, b = rgb

    def ring(a, blur, width):
        return (f'<svg width="{W}" height="{H}" style="position:absolute;left:0;top:0;overflow:visible">'
                f'<defs><filter id="b{width:.0f}" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="{blur}"/>'
                '</filter></defs>'
                f'<polygon points="{pts(octagon(1.6))}" fill="none" stroke="rgba({r},{g},{b},{a * .8})" '
                f'stroke-width="{width + 2}" filter="url(#b{width:.0f})"/>'
                f'<polygon points="{pts(octagon(1.2))}" fill="none" stroke="rgba({r},{g},{b},{a})" stroke-width="{width}"/>'
                '</svg>')
    return frames(W * 2, H, ring(.35, 1.0, 1.4), ring(1.0, 1.6, 2.0))


ADDS = [
    ("al_icons", "gfx/interface/alerts/global_alert_icons.dds", W * N, H, icons),
    ("al_glow_red", "gfx/interface/red_alert_glow.dds", W * 2, H, lambda: glow((238, 90, 70))),
    ("al_glow_yellow", "gfx/interface/yellow_alert_glow.dds", W * 2, H, lambda: glow((231, 183, 90))),
    ("al_glow_green", "gfx/interface/green_alert_glow.dds", W * 2, H, lambda: glow((120, 205, 160))),
]
