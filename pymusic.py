"""
Play a sequence of beeps
Based on https://stackoverflow.com/a/27978895/3210924
"""
import sys
import re
from collections import namedtuple

import numpy as np
import pyaudio


if len(sys.argv) > 1:
    f = float(sys.argv[1])        # sine frequency, Hz, may be float
else:
    f = 440.0
TUNING = f
TUNING_OCTAVE = 4 # As in A4
VOLUME = 0.7 # range [0.0, 1.0]
SAMPLING_RATE = 44100 # sampling rate, Hz, must be integer
TEMPO = 100 # BPM, must be an integer
SEMITONE = 2**(1/12)

note_attributes = ['pitch', 'accidental', 'octave', 'duration']
NoteTuple = namedtuple('NoteTuple', note_attributes)

class Note():
    """Class for managing musical notes"""
    scale = {'a': 0, 'b': 2, 'c': 3, 'd': 5, 'e': 7, 'f': 8, 'g': 10}
    note_re = re.compile(r"""
            (?P<pitch>[a-gA-G])
            (?P<accidental>[b#])?
            (?P<octave>[0-8])?
            -?
            (?P<duration>[1-9][0-9]*)?
            """, re.VERBOSE)

    def __init__(self, note, tuning=TUNING, volume=VOLUME,
                 tempo=TEMPO):
        self.note = Note.parse_note(note)
        self.tuning = tuning
        self.volume = volume
        self.interval = Note.get_interval(self.note)
        self.frequency = Note.get_frequency(self.interval, tuning=tuning)
        self.tone = Note.get_tone(self.note, self.frequency)

    def __repr__(self):
        return f'{self.note}, {self.interval}'

    @classmethod
    def parse_note(cls, note_str):
        """
        Parse a note from the given string

        TODO: A lot more explanation...
        """
        m = cls.note_re.match(note_str)
        if not m:
            raise ValueError(f'{note_str} is not a valid note string')
        return NoteTuple(
            pitch=m.group('pitch'),
            accidental=['b', None, '#'].index(m.group('accidental')) - 1,
            octave=int(m.group('octave')) if m.group('octave') else TUNING_OCTAVE,
            duration=int(m.group('duration')) if m.group('duration') else 4
            )

    @classmethod
    def get_interval(cls, note):
        """Return the interval of this note from the tuning note"""
        return (cls.scale[note.pitch]
            + note.accidental
            + (12 * (note.octave - TUNING_OCTAVE)))

    @staticmethod
    def get_frequency(interval, tuning=TUNING):
        """Return the frequency of an interval"""
        return tuning * SEMITONE**interval

    @staticmethod
    def get_tone(note, frequency, volume=VOLUME):
        """
        Return the tone of the given frequency

        The output is in bytes such that it may be written directly to a
        pyaudio stream.
        """
        duration = 4 / note.duration / TEMPO * 60
        samples = np.arange(int(SAMPLING_RATE*duration))
        tone = np.sin(2 * np.pi * samples * frequency / SAMPLING_RATE)
        return (tone.astype(np.float32) * volume).tobytes()

def main():
    # for paFloat32 sample values must be in range [-1.0, 1.0]
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=SAMPLING_RATE,
                    output=True)
    # Write each of the notes to the pyaudio stream
    twinkle = ['c','c','g','g','a5','a5','g-2','f','f','e','e','d','d','c-2']
    epona = ['g-8','e-8','d-2']*2 + ['g-8','e-8','d-4','e-4','d-2']
    child_of_god = ['f#','f#-8','f#-8','g','a5','f#-2','a5','d5-3','d5-8','c#5','b5','a5-2','a5']
    song = child_of_god
    notes = b''
    for note in [Note(x) for x in song]:
        print(note)
        notes = notes + note.tone
    stream.write(notes)
    # End and close the stream
    stream.stop_stream()
    stream.close()
    # Close pyaudio
    p.terminate()

main()
