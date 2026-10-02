"""TNO-style superevents: a large window with a title, a picture, a quote and music.

HOI4 has no superevents of its own. This is the pattern big mods use, built only from
vanilla pieces:
  * a scripted effect per superevent (`valsora_superevent_<id> = yes`, called from a
    focus or event) sets a global flag saying which superevent is showing, then fires
    a hidden event for every human player;
  * that event sets a country flag, which makes a player_context scripted GUI window
    visible, and starts the music with `play_song` (vanilla plays its speeches so);
  * the window's texts come from scripted localisation that picks the keys of the
    superevent whose global flag is set; its picture is one icon per distinct image,
    shown by the same flags;
  * the close button clears the country flag.

To add one, append to SUPEREVENTS and call its effect from a focus or event.
"""
from pathlib import Path

import numpy as np
from PIL import Image

from imgio import write_dds

SRC = Path("source/superevents")
PIC_W, PIC_H = 840, 420

# id, title, quote, who said it, picture (in source/superevents), song
SUPEREVENTS = [
    dict(id="rou_polite",
         title="The Parasites Depart, Politely",
         quote="We thank the House of Cahun for its many years of service, and kindly ask that it "
               "vacate the palace by Tuesday. Light refreshments will be provided. Please return "
               "the crown on your way out.",
         author="Provisional Council of Rouental, Notice of Eviction",
         picture="hair_ruffle.png", song="valsora_gladiators"),
    dict(id="rou_brother",
         title="Blood Is Thinner Than Iron",
         quote="Roland always said the crown was too heavy for me. He was right. I have had it "
               "melted down into something more useful.",
         author="Serelle Cahun, Queen of the Absolute Iron Monarchy",
         picture="hair_ruffle.png", song="valsora_gladiators"),
    dict(id="rou_steady",
         title="Nothing Happens in Rouental",
         quote="The Cahuns stay. The borders stay. The price of bread stays exactly where it is. "
               "To those of you hoping for a revolution: perhaps next year.",
         author="Roland Cahun, New Year's Address",
         picture="hair_ruffle.png", song="valsora_gladiators"),
    dict(id="rou_rude",
         title="Shown the Window",
         quote="The Cahuns were shown the door. When they refused the door, they were shown the "
               "window. Rouental is now a workers' state, with one fewer window.",
         author="Red Workers' Committee of Rouental, Communique No. 1",
         picture="hair_ruffle.png", song="valsora_gladiators"),
    dict(id="rou_reality",
         title="The Veiled Throne",
         quote="Rouental asked Heaven for a firm hand. Heaven, in its wisdom, has sent a gloved "
               "one. Kneel, and you will find it gentle.",
         author="Mahaut VI, Holy Princess of Rouental",
         picture="hair_ruffle.png", song="valsora_gladiators"),
    # the Rouentaise civil war, after the Prince's execution on the communist path
    # (author's picture, quote and song, 2026-10-02; title and attribution Claude's)
    dict(id="rou_civil_war",
         title="The Rouentaise Civil War",
         quote="They promised us the Prince's death would end the old Rouental, and it did. By "
               "morning there were a hundred Rouentals, all of them armed, and all of them "
               "furious.",
         author="A Red Guard, in a letter home from Rêverie",
         picture="rou_civil_war.jpg", song="valsora_elbee"),
    dict(id="ais_explode",
         title="Merlovich Has Exploded",
         quote="Our beloved leader has become many smaller leaders, now scattered across a wide "
               "area. Every one of them is a communist.",
         author="Aisladan State Radio, Final Broadcast Before the Red One",
         picture="hair_ruffle.png", song="valsora_gladiators"),
]

# song name -> audio file in source/superevents (Ogg Vorbis, like vanilla music)
# (each the first 45 s of the author's file, faded out over the last 4 s)
SONGS = {"valsora_gladiators": "entry_of_the_gladiators.ogg",
         "valsora_elbee": "monsieur_d_elbee.ogg"}
SONG_TITLES = {"valsora_gladiators": "Julius Fucik - Entry of the Gladiators",
               "valsora_elbee": "Monsieur d'Elbée (Vendéen royalist song)"}
STATION = "valsora"  # music station the songs live in


def flag(se):
    return f"valsora_superevent_{se['id']}"


def effect_name(se):
    return f"valsora_superevent_{se['id']}"


def picture_sprite(pic):
    return "GFX_valsora_superevent_" + Path(pic).stem


def fit(path):
    """Crop to the window's 2:1 picture box and scale to it."""
    im = Image.open(SRC / path).convert("RGB")
    w, h = im.size
    tw = min(w, round(h * PIC_W / PIC_H))
    th = round(tw * PIC_H / PIC_W)
    x0, y0 = (w - tw) // 2, (h - th) // 2
    im = im.crop((x0, y0, x0 + tw, y0 + th)).resize((PIC_W, PIC_H), Image.LANCZOS)
    return np.dstack([np.asarray(im), np.full((PIC_H, PIC_W), 255, np.uint8)])


def background(w, h):
    """A dark, faintly textured panel with a gold double frame."""
    rng = np.random.default_rng(5)
    y = np.linspace(0, 1, h)[:, None]
    base = 24 + 10 * (1 - y) + rng.normal(0, 2.5, (h, w))
    img = np.dstack([base * 0.95, base, base * 1.12]).clip(0, 255)
    gold, dim = np.array([176, 148, 88]), np.array([120, 100, 60])
    img[:3], img[-3:], img[:, :3], img[:, -3:] = gold, gold, gold, gold
    img[7], img[-8], img[7:-7, 7], img[7:-7, -8] = dim, dim, dim, dim
    x0, y0 = 30, 62  # frame around the picture
    img[y0 - 2:y0, x0 - 2:x0 + PIC_W + 2] = gold
    img[y0 + PIC_H:y0 + PIC_H + 2, x0 - 2:x0 + PIC_W + 2] = gold
    img[y0 - 2:y0 + PIC_H + 2, x0 - 2:x0] = gold
    img[y0 - 2:y0 + PIC_H + 2, x0 + PIC_W:x0 + PIC_W + 2] = gold
    return np.dstack([img.round().astype(np.uint8), np.full((h, w), 255, np.uint8)])


def write_station_interface(write, out):
    """The radio menu entry and faceplate every music station needs (layout from the
    Music Mod Creation Tool's HOI4 template), with a cover showing the first picture."""
    cover = Image.fromarray(fit(SUPEREVENTS[0]["picture"])[..., :3]).resize((162, 130), Image.LANCZOS)
    a = np.asarray(cover).astype(float)
    frames = np.concatenate([a * 0.75, a], axis=1)  # normal, selected
    path = out / f"gfx/interface/valsora/radio_station_cover_{STATION}.dds"
    write_dds(path, np.dstack([frames.round().astype(np.uint8), np.full((130, 324), 255, np.uint8)]))
    write(f"interface/{STATION}_music_station.gfx", "spriteTypes = {\n\tspriteType = {\n"
          f'\t\tname = "GFX_radio_station_cover_{STATION}"\n'
          f'\t\ttexturefile = "gfx/interface/valsora/radio_station_cover_{STATION}.dds"\n'
          "\t\tnoOfFrames = 2\n\t}\n}\n")
    write(f"interface/{STATION}_music_station.gui", STATION_GUI.replace("STATION", STATION))


STATION_GUI = """guiTypes = {
	containerWindowType = {
		name = "STATION_faceplate"
		position = { x = 0 y = 0 }
		size = { width = 590 height = 46 }
		iconType = {
			name = "musicplayer_header_bg"
			spriteType = "GFX_musicplayer_header_bg"
			position = { x = 0 y = 0 }
			alwaystransparent = yes
		}
		instantTextboxType = {
			name = "track_name"
			position = { x = 72 y = 20 }
			font = "hoi_18b"
			text = ""
			maxWidth = 450
			maxHeight = 25
			format = center
		}
		instantTextboxType = {
			name = "track_elapsed"
			position = { x = 124 y = 30 }
			font = "hoi_18b"
			text = "00:00"
			maxWidth = 50
			maxHeight = 25
			format = center
		}
		instantTextboxType = {
			name = "track_duration"
			position = { x = 420 y = 30 }
			font = "hoi_18b"
			text = "00:00"
			maxWidth = 50
			maxHeight = 25
			format = center
		}
		buttonType = {
			name = "prev_button"
			position = { x = 220 y = 20 }
			quadTextureSprite = "GFX_musicplayer_previous_button"
			buttonFont = "Main_14_black"
			Orientation = "LOWER_LEFT"
			clicksound = click_close
			pdx_tooltip = "MUSICPLAYER_PREV"
		}
		buttonType = {
			name = "play_button"
			position = { x = 263 y = 20 }
			quadTextureSprite = "GFX_musicplayer_play_pause_button"
			buttonFont = "Main_14_black"
			Orientation = "LOWER_LEFT"
			clicksound = click_close
		}
		buttonType = {
			name = "next_button"
			position = { x = 336 y = 20 }
			quadTextureSprite = "GFX_musicplayer_next_button"
			buttonFont = "Main_14_black"
			Orientation = "LOWER_LEFT"
			clicksound = click_close
			pdx_tooltip = "MUSICPLAYER_NEXT"
		}
		extendedScrollbarType = {
			name = "volume_slider"
			position = { x = 100 y = 45 }
			size = { width = 75 height = 18 }
			tileSize = { width = 12 height = 12 }
			maxValue = 100
			minValue = 0
			stepSize = 1
			startValue = 50
			horizontal = yes
			orientation = lower_left
			origo = lower_left
			setTrackFrameOnChange = yes
			slider = {
				name = "Slider"
				quadTextureSprite = "GFX_scroll_drager"
				position = { x = 0 y = 1 }
				pdx_tooltip = "MUSICPLAYER_ADJUST_VOL"
			}
			track = {
				name = "Track"
				quadTextureSprite = "GFX_volume_track"
				position = { x = 0 y = 3 }
				alwaystransparent = yes
				pdx_tooltip = "MUSICPLAYER_ADJUST_VOL"
			}
		}
		buttonType = {
			name = "shuffle_button"
			position = { x = 425 y = 20 }
			quadTextureSprite = "GFX_toggle_shuffle_buttons"
			buttonFont = "Main_14_black"
			Orientation = "LOWER_LEFT"
			clicksound = click_close
		}
	}
	containerWindowType = {
		name = "STATION_stations_entry"
		size = { width = 162 height = 130 }
		checkBoxType = {
			name = "select_station_button"
			position = { x = 0 y = 0 }
			quadTextureSprite = "GFX_radio_station_cover_STATION"
			clicksound = decisions_ui_button
		}
	}
}
"""


def write_files(write, out):
    """Every superevent file; returns the localisation lines."""
    pictures = sorted({se["picture"] for se in SUPEREVENTS})
    others = [flag(se) for se in SUPEREVENTS]

    # scripted effects: one per superevent
    fx = []
    for se in SUPEREVENTS:
        fx += [f"{effect_name(se)} = {{",
               *[f"\tclr_global_flag = {f}" for f in others if f != flag(se)],
               f"\tset_global_flag = {flag(se)}",
               "\tevery_country = {",
               "\t\tlimit = { is_ai = no }",
               f"\t\tcountry_event = {{ id = valsora_superevent.{SUPEREVENTS.index(se) + 1} }}",
               "\t}",
               "}", ""]
    write("common/scripted_effects/valsora_superevent_effects.txt", "\n".join(fx))

    # the hidden events that open the window for each human player and start the music
    ev = ["add_namespace = valsora_superevent", ""]
    for k, se in enumerate(SUPEREVENTS, 1):
        ev += ["country_event = {",
               f"\tid = valsora_superevent.{k}",
               "\thidden = yes",
               "\tis_triggered_only = yes",
               "\timmediate = {",
               "\t\tset_country_flag = valsora_superevent_open",
               f"\t\tplay_song = \"{se['song']}\"",
               "\t}",
               "}", ""]
    write("events/valsora_superevents.txt", "\n".join(ev))

    # texts, picked by whichever superevent flag is set
    sl = []
    for part in ("TITLE", "QUOTE", "AUTHOR"):
        sl += ["defined_text = {", f"\tname = ValsoraSuperevent{part.capitalize()}"]
        for se in SUPEREVENTS:
            sl += ["\ttext = {", f"\t\ttrigger = {{ has_global_flag = {flag(se)} }}",
                   f"\t\tlocalization_key = VAL_SE_{se['id'].upper()}_{part}", "\t}"]
        sl += ["}", ""]
    write("common/scripted_localisation/valsora_superevent_loc.txt", "\n".join(sl))

    # the window
    trig = []
    for pic in pictures:
        users = [flag(se) for se in SUPEREVENTS if se["picture"] == pic]
        trig += [f"\t\t\tvalsora_superevent_pic_{Path(pic).stem}_visible = {{",
                 "\t\t\t\tOR = {", *[f"\t\t\t\t\thas_global_flag = {f}" for f in users],
                 "\t\t\t\t}", "\t\t\t}"]
    write("common/scripted_guis/valsora_superevent_gui.txt", "\n".join([
        "scripted_gui = {",
        "\tvalsora_superevent = {",
        "\t\tcontext_type = player_context",
        '\t\twindow_name = "valsora_superevent_window"',
        "\t\tvisible = { has_country_flag = valsora_superevent_open }",
        "\t\teffects = {",
        "\t\t\tvalsora_superevent_close_click = { clr_country_flag = valsora_superevent_open }",
        "\t\t}",
        "\t\ttriggers = {", *trig, "\t\t}",
        "\t\tai_enabled = { always = no }",
        "\t}",
        "}", ""]))
    W, H = PIC_W + 60, PIC_H + 225
    icons = []
    for pic in pictures:
        icons += ["\t\ticonType = {",
                  f'\t\t\tname = "valsora_superevent_pic_{Path(pic).stem}"',
                  f'\t\t\tspriteType = "{picture_sprite(pic)}"',
                  "\t\t\tposition = { x = 30 y = 62 }",
                  "\t\t\talwaystransparent = yes",
                  "\t\t}"]
    write("interface/valsora_superevent.gui", "\n".join([
        "guiTypes = {",
        "\tcontainerWindowType = {",
        '\t\tname = "valsora_superevent_window"',
        f"\t\tposition = {{ x = {-W // 2} y = {-H // 2} }}",
        f"\t\tsize = {{ width = {W} height = {H} }}",
        "\t\tOrientation = CENTER",
        "\t\tmoveable = yes",
        "\t\tshow_sound = event_popup",
        "\t\thide_sound = menu_close_window",
        '\t\tbackground = { name = "Background" spriteType = "GFX_valsora_superevent_bg" }',
        "\t\tinstantTextBoxType = {",
        '\t\t\tname = "valsora_superevent_title"',
        "\t\t\tposition = { x = 30 y = 18 }",
        '\t\t\tfont = "hoi4_typewriter22"',
        '\t\t\ttext = "[ValsoraSupereventTitle]"',
        f"\t\t\tmaxWidth = {PIC_W}",
        "\t\t\tmaxHeight = 32",
        "\t\t\tformat = centre",
        "\t\t}",
        *icons,
        "\t\tinstantTextBoxType = {",
        '\t\t\tname = "valsora_superevent_quote"',
        f"\t\t\tposition = {{ x = 60 y = {PIC_H + 76} }}",
        '\t\t\tfont = "hoi4_typewriter16"',
        '\t\t\ttext = "[ValsoraSupereventQuote]"',
        f"\t\t\tmaxWidth = {PIC_W - 60}",
        "\t\t\tmaxHeight = 70",
        "\t\t\tformat = centre",
        "\t\t}",
        "\t\tinstantTextBoxType = {",
        '\t\t\tname = "valsora_superevent_author"',
        f"\t\t\tposition = {{ x = 60 y = {PIC_H + 146} }}",
        '\t\t\tfont = "hoi_16mbs"',
        '\t\t\ttext = "[ValsoraSupereventAuthor]"',
        f"\t\t\tmaxWidth = {PIC_W - 60}",
        "\t\t\tmaxHeight = 20",
        "\t\t\tformat = centre",
        "\t\t}",
        "\t\tbuttonType = {",
        '\t\t\tname = "valsora_superevent_close"',
        f"\t\t\tposition = {{ x = {(W - 221) // 2} y = {H - 50} }}",
        '\t\t\tspriteType = "GFX_button_221x34"',
        '\t\t\tbuttonText = "VAL_SE_CLOSE"',
        '\t\t\tbuttonFont = "hoi_18mbs"',
        "\t\t\tclicksound = click_default",
        "\t\t}",
        "\t}",
        "}", ""]))
    gfx = []
    bg = out / "gfx/interface/valsora/superevent_bg.dds"
    bg.parent.mkdir(parents=True, exist_ok=True)
    write_dds(bg, background(W, H))
    gfx.append('\tspriteType = {\n\t\tname = "GFX_valsora_superevent_bg"\n'
               '\t\ttexturefile = "gfx/interface/valsora/superevent_bg.dds"\n\t}\n')
    for pic in pictures:
        path = out / f"gfx/interface/valsora/superevent_{Path(pic).stem}.dds"
        path.parent.mkdir(parents=True, exist_ok=True)
        write_dds(path, fit(pic))
        gfx.append(f'\tspriteType = {{\n\t\tname = "{picture_sprite(pic)}"\n'
                   f'\t\ttexturefile = "gfx/interface/valsora/superevent_{Path(pic).stem}.dds"\n\t}}\n')
    write("interface/valsora_superevent.gfx", "spriteTypes = {\n" + "".join(gfx) + "}\n")

    # music: HOI4 only knows songs that belong to a music station, so the superevent
    # songs get a station of their own ("Valsora Radio" in the radio menu), where they
    # have zero chance of coming up in normal play
    st = out / "music" / STATION
    st.mkdir(parents=True, exist_ok=True)
    asset, txt = [], [f'music_station = "{STATION}"', ""]
    for name, f in SONGS.items():
        (st / f).write_bytes((SRC / f).read_bytes())
        asset.append(f'music = {{\n\tname = "{name}"\n\tfile = "{f}"\n\tvolume = 0.8\n}}\n')
        txt.append(f'music = {{\n\tsong = "{name}"\n\tchance = {{\n\t\tmodifier = {{ factor = 0 }}\n\t}}\n}}\n')
    write(f"music/{STATION}/{STATION}.asset", "".join(asset))
    write(f"music/{STATION}/{STATION}.txt", "\n".join(txt))
    write_station_interface(write, out)

    loc = [' VAL_SE_CLOSE:0 "History Marches On"', f' {STATION}_TITLE:0 "Valsora Radio"']
    loc += [f' {name}:0 "{title}"' for name, title in SONG_TITLES.items()]
    for se in SUPEREVENTS:
        key = f"VAL_SE_{se['id'].upper()}"
        # §W ... §! = white: the typewriter fonts draw dark on the dark panel
        loc += [f' {key}_TITLE:0 "§W{se["title"]}§!"', f' {key}_QUOTE:0 "§W\\"{se["quote"]}\\"§!"',
                f' {key}_AUTHOR:0 "- {se["author"]}"']
    return loc
