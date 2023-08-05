"""Module that draws the full fretboard image for movable chords"""

import PIL.Image, PIL.ImageDraw, PIL.ImageFont
from .Instruments import *
from .Palettes import *
from .ChordData import *


class ChordNotFound(Exception):
    """Placeholder class for custom error raising"""
    pass


@dump_args
def get_fret_naming(chord_name: str):
    """This function returns on success a list of the names by which a movable chord would translate if
    the chord shape was shifted to that fret"""
    name_list = ['A#/Bb', 'B', 'C', 'C#Db', 'D', 'D#Eb', 'E', 'F', 'F#Gb', 'G', 'G#Ab',
                 'A']  # Ordered, but arbitrary start / end

    for _ in list(range(0, len(name_list))):
        if name_list[0] == chord_name:
            for _ in list(range(1, 5)):
                name_list.insert(0, name_list.pop())  # now shift it right until our root is the 5th fret
            return name_list
        else:
            name_list.append(name_list.pop(0))  # rotate list of names left until our root is the first element
    raise ChordNotFound


@dump_args
def draw_root_frets(draw: PIL.ImageDraw, instrument: Instrument, text_top_area: int, text_bottom_area: int,
                    image_height: int, palette: Palette) -> PIL.ImageDraw:
    """Add the frets to the root finder image"""
    for fret_num in list(range(1, instrument.number_of_frets)):
        fret_pos_x = (fret_num * (instrument.fret_spacing / 4)) + (
                    (instrument.top_gap / 2) + (instrument.nut_width / 2))
        draw.line((fret_pos_x, text_top_area, fret_pos_x, (image_height - text_bottom_area)), palette.fret_colour,
                  width=1)
    return draw


@dump_args
def draw_root_fret_markers(draw: PIL.ImageDraw, instrument: Instrument, text_top_area: int, text_bottom_area: int,
                           image_height: int, palette: Palette) -> PIL.ImageDraw:
    """Add the fret markers to the root finder image"""
    for fret_pos in instrument.marker_positions:
        x_pos = (instrument.margin / 2) + (instrument.nut_width / 2) + (fret_pos * (instrument.fret_spacing / 4)) - (
                    instrument.fret_spacing / 8)

        if fret_pos in instrument.double_markings:
            y_pos = text_top_area + ((image_height - text_top_area - text_bottom_area) / 3)

            draw.ellipse((x_pos - (instrument.marker_size / 3), y_pos - (instrument.marker_size / 3),
                          x_pos + (instrument.marker_size / 3), y_pos + (instrument.marker_size / 3)),
                         palette.fret_marker_colour)

            y_pos = image_height - text_bottom_area - ((image_height - text_top_area - text_bottom_area) / 3)

            draw.ellipse((x_pos - (instrument.marker_size / 3), y_pos - (instrument.marker_size / 3),
                          x_pos + (instrument.marker_size / 3), y_pos + (instrument.marker_size / 3)),
                         palette.fret_marker_colour)

        else:
            y_pos = ((image_height - text_top_area - text_bottom_area) / 2) + text_top_area
            draw.ellipse((x_pos - (instrument.marker_size / 3), y_pos - (instrument.marker_size / 3),
                          x_pos + (instrument.marker_size / 3), y_pos + (instrument.marker_size / 3)),
                         palette.fret_marker_colour)
    return draw


@dump_args
def draw_root_strings(draw: PIL.ImageDraw, instrument: Instrument, text_top_area: int, image_width: int,
                      palette: Palette) -> PIL.ImageDraw:
    """Add the strings to the root finder image"""
    for string_num in list(range(instrument.number_of_strings)):
        string_pos_x = (instrument.margin / 2) + (instrument.nut_width / 2)
        string_pos_y = text_top_area + (string_num * (instrument.string_spacing / 4)) + (
                    instrument.first_string_gap / 4)
        draw.line((string_pos_x, string_pos_y, image_width, string_pos_y), palette.string_colour,
                  width=int(instrument.string_width / 2))
    return draw


@dump_args
def draw_root_fret_naming(draw: PIL.ImageDraw, text_top_area: int, text_bottom_area: int, chord: Chord, font_path: str,
                          image_height: int) -> PIL.ImageDraw:
    """Add fret naming to the root finder image"""
    name_list = get_fret_naming(chord.root)
    name_list_evens = name_list[0::2]
    name_list_odds = name_list[1::2]
    sans16 = PIL.ImageFont.truetype(font_path, 10)
    x_pos = 0
    root_name_spacing = 38
    for root_name in name_list_odds:
        x_pos += root_name_spacing
        if len(root_name) == 1:  # shift single char chords right a bit, 4 is arbitrary
            x_pos += 4
        draw.text((x_pos, (text_top_area / 2) - 5), root_name, font=sans16, fill=(255, 255, 255))
        if len(root_name) == 1:  # undo temp shift
            x_pos -= 4

    x_pos = -10
    root_name_spacing = 36
    for root_name in name_list_evens:
        x_pos += root_name_spacing
        if len(root_name) == 1:  # shift single char chords right a bit, 4 is arbitrary
            x_pos += 4
        draw.text((x_pos, image_height - text_bottom_area + 5), root_name, font=sans16, fill=(255, 255, 255))
        if len(root_name) == 1:  # undo temp shift
            x_pos -= 4

    return draw


@dump_args
def draw_root_finder(instrument: Instrument, palette: Palette, chord: Chord, image_dimensions: [int], output_file: str) -> None:
    """Draw the smaller bitmap of the whole fretboard"""
    font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSerifCondensed-Bold.ttf'
    if not os.path.exists(font_path):
        raise FileNotFoundError

    # Create a new image
    image_width = image_dimensions[0]
    image_height = image_dimensions[1]
    image = PIL.Image.new("RGB", image_dimensions)

    text_top_area = 20
    text_bottom_area = 20

    draw = PIL.ImageDraw.Draw(image)
    # Draw the fretboard
    draw.polygon([(instrument.margin / 2, text_top_area), (image_width, text_top_area),
                  (image_width, image_height - text_bottom_area),
                  (instrument.margin / 2, image_height - text_bottom_area)], palette.fret_board_colour)

    # Draw the plastic nut
    draw.line((int(instrument.margin / 2), text_top_area, int(instrument.margin / 2), image_height - text_bottom_area),
              palette.nut_colour, width=(int(instrument.nut_width / 2)))

    draw = draw_root_frets(draw, instrument, text_top_area, text_bottom_area, image_height, palette)
    draw = draw_root_fret_markers(draw, instrument, text_top_area, text_bottom_area, image_height, palette)
    draw = draw_root_strings(draw, instrument, text_top_area, image_width, palette)
    draw_root_fret_naming(draw, text_top_area, text_bottom_area, chord, font_path, image_height)

    del draw
    # Write image to disk
    image.save(output_file, "PNG")
