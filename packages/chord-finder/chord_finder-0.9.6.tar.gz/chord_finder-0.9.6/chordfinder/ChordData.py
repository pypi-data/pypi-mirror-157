import os, sys
from typing import Optional
from .debugging import *


class ChordNotFound(Exception):
  pass


class Chord:
  """A class that holds data for a single static chord"""
  @dump_args
  def __init__(self, chord_type: str, root: str, short_name: str, long_name: str, finger_str: str, fret_str: str) -> None:
    self.chord_type = chord_type
    self.root = root
    self.short_name = short_name
    self.long_name = long_name
    self.finger_str = finger_str
    self.fret_str = fret_str


class ChordDatabase:
  """ A class which builds up lists of all known chords and presents data on them as needed """
  @dump_args
  def __init__(self, chords_csv: str) -> None:

    self.chord_list = []
    self.init_chords(chords_csv)

  @dump_args
  def init_chords(self, csv_file: str) -> None:
    """Build up an array of all the chord data from the chord data file"""
    try:
      file_obj = open(csv_file, 'r')
    except IOError:
      print("IOError opening: {0}".format(csv_file))
      sys.exit(1)
    else:
      for line in file_obj:
        if not line.startswith('#') and (line.strip()): 	# ignore comment lines and empty lines
          chord_type = line.split(',')[0]
          root = line.split(',')[1]
          short_name = line.split(',')[2]
          long_name = line.split(',')[3]
          finger_str = line.split(',')[4]
          fret_str = line.split(',')[5]
          chord_obj = Chord(chord_type, root, short_name, long_name, finger_str, fret_str)
          self.chord_list.append(chord_obj)
    file_obj.close()

  @dump_args
  def get_single_chord_obj(self, chord_type_wanted: str, chord_name_wanted: str) -> Optional[Chord]:
    """Return a single chord from the list of chords that we have"""
    for chord in self.chord_list:
      if (chord.short_name == chord_name_wanted) and (chord.chord_type == chord_type_wanted):
        return chord
    raise ChordNotFound

  @dump_args
  def get_all_chord_names(self) -> [str]:
    """Just return a list of all the chord names we know of"""
    chord_name_list = []
    for chord in self.chord_list:
      chord_name_list.append(chord.short_name)
    return chord_name_list

  @dump_args
  def get_filtered_chord_names(self, type_wanted: str, root_str: str, dim_aug_wanted: str) -> [str]:
    """Return a filtered list of chord names based upon some passed in criteria"""
    chord_name_list = []

    for chord in self.chord_list:
      filter_out = 0
      if chord.chord_type != type_wanted:
        filter_out += 1

      if (root_str != 'All') and (chord.root != root_str):
        filter_out += 1

      if (dim_aug_wanted != 'All') and (chord.long_name.find(dim_aug_wanted) == -1):
        filter_out += 1

      if filter_out == 0:
        chord_name_list.append(chord.short_name)
    return chord_name_list

  @dump_args
  def play_chord_from_obj(self, chord_obj: Chord) -> int:
    """ Play a chord using the linux sox play command from a given chord object """
    open_strings = ['E2', 'A2', 'D3', 'G3', 'B3', 'E4']
    notes = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
    fret_data = chord_obj.fret_str.split()
    chord_str = ''

    for i, fret_pos in enumerate(fret_data):
      if fret_pos == '0':
        chord_str += open_strings[i] + " "  # string is played open, so just use the string's open note
        continue
      elif fret_pos == '-1':
        continue                            # this string is not played in the chord, skip

      open_note = open_strings[i][0]
      open_octave = int(open_strings[i][1])

      for i, note in enumerate(notes):
        if note == open_note:
          base_pos = i									# where in list are we starting
          shift_pos = base_pos + int(fret_pos)			# final "position" in list (may have looped)

          if shift_pos >= len(notes):
            final_note = notes[shift_pos % len(notes)]  # allow for loop if needed
          else:
            final_note = notes[shift_pos]				# otherwise return note directly

          octave_shift = int(shift_pos / len(notes)) 	# how many octaves we gained
          final_octave = open_octave + octave_shift
          output_note = final_note + str(final_octave)
          chord_str += output_note + " "
    cmd_str = "for p in {0}; do ( play -n synth 3 pluck $p vol 0.1 >/dev/null 2>&1 &); done".format(chord_str)

    logging.debug("Command to execute with os.system() is: {}".format(cmd_str))
    rc = os.system(cmd_str)  # ToDo: Error handle on sox command not being available
    return rc
