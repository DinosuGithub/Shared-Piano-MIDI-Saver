from mido import MidiFile, tick2second
import saving

use_velocities = False
START_DELAY = 10

midi_path = input('MIDI file path: ')
mid = MidiFile(midi_path, clip=True)
result_instruments = []

# Create song object to add notes to
s = saving.Song()

# Show instrument choices
instruments = list(s.user_map.values())
print('\nInstrument options:')
for instrument_i, instrument in enumerate(instruments):
	print(f'{instrument_i + 1}: {instrument}')
print()

# Get the Shared Piano instrument substitutes for each track
for track_i, track in enumerate(mid.tracks):
  track_name = None
  for message in track:
    if message.type == 'track_name':
      result_instrument = None

      track_name = message.name
      break

  substitute_i = int(input(f'Instrument for track #{track_i} ("{track_name if track_name is not None else ""}"): ')) - 1
  result_instruments.append(instruments[substitute_i])

# Ask if velocities should be used
use_velocities = input('\nUse note velocities? (y/n): ').lower() == 'y'

# Initialize variables to be updated during processing
notes = [] # To be saved in JSON format
tracks = mid.tracks
tempos = {0: 500000} # Tempos by tick number of tempo change

# Get tempos
for track_i, track in enumerate(tracks):
  ticks_elapsed = 0

  for message in track:
    ticks_elapsed += message.time

    if message.type == 'set_tempo':
      tempos[ticks_elapsed] = message.tempo

tempos = dict(sorted(tempos.items(), key=lambda item: item[0])) # Sort tempos

# Update the notes list for each track
print()
for track_i, track in enumerate(tracks):
  result_instrument = None
  if track_i < len(result_instruments):
    result_instrument = result_instruments[track_i]
  track_icon = s.user_for_instrument(result_instrument)

  ticks_elapsed = 0
  track_notes = []
  pending_notes = {}

  tempo = tempos[0]
  milestone_seconds_elapsed = 0
  milestone_seconds_elapsed_tick = 0
  milestone_ind = 0

  for message in track:
    ticks_elapsed += message.time

    # Update tempo if tick has passed a tempo change tick
    while True:
      if milestone_ind + 1 < len(tempos.keys()):
        next_tempo_tick = list(tempos.keys())[milestone_ind + 1]
        if ticks_elapsed >= next_tempo_tick:
          ticks_since_milestone = next_tempo_tick - milestone_seconds_elapsed_tick
          milestone_seconds_elapsed += tick2second(ticks_since_milestone, mid.ticks_per_beat, tempo)
          milestone_seconds_elapsed_tick = next_tempo_tick
          tempo = tempos[next_tempo_tick]
          milestone_ind += 1
        else:
          break
      else:
        break

    ticks_since_milestone = ticks_elapsed - milestone_seconds_elapsed_tick
    seconds_elapsed = milestone_seconds_elapsed + tick2second(ticks_since_milestone, mid.ticks_per_beat, tempo)
    
    # For note_on messages, we do not know the end time of the note.
    # We need to add it to a list of pending notes to be added when we get the note_off message.
    note_off = False
    if message.type == 'note_on':
      if message.velocity == 0:
        note_off = True
      else:
        pending_notes[message.note] = {
          'start_seconds': seconds_elapsed,
          'velocity': message.velocity if use_velocities else 50,
        }
    # Now we can add the note
    elif message.type == 'note_off':
      note_off = True
    if note_off:
      note_info = pending_notes[message.note]
      track_notes.append({
        'color': '#ff0000',
        'midi': message.note,
        'velocity': note_info['velocity'] / 128,
        'pitch': 0,
        'octave': 5,
        'start': note_info['start_seconds'] * 60 + START_DELAY, # 60 Shared Piano ticks every second
        'end': seconds_elapsed * 60 + START_DELAY,
        'emoji': track_icon,
        'sustained': False
      })

  notes += track_notes

  print(f'Done adding notes for track #{track_i + 1}.')

# Save the song
s.set_notes(notes)
response = s.save()

# Show the link to the saved song
print(f'\nSaved link: https://musiclab.chromeexperiments.com/Shared-Piano/saved/#{response["name"]}')
