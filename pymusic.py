"""
Play a sequence of beeps
Based on https://stackoverflow.com/a/27978895/3210924
"""
import sys

import numpy as np
import pyaudio


if len(sys.argv) > 1:
    f = float(sys.argv[1])        # sine frequency, Hz, may be float
else:
    f = 440.0
BASE_FREQUENCY = f
VOLUME = 1.0 # range [0.0, 1.0]
SAMPLING_RATE = 44100 # sampling rate, Hz, must be integer
DURATION = 0.5 # in seconds, may be float
SEMITONE = 2**(1/12)

class Note():
    """Class for managing musical notes"""
    scale = ['a', 'b', 'c', 'd', 'e', 'f', 'g']

    def __init__(self, note, base=BASE_FREQUENCY, volume=VOLUME,
                 duration=DURATION):
        self.note = note
        self.base = base
        self.volume = volume
        self.duration = duration
        self.interval = Note.get_interval(note)
        self.frequency = Note.get_frequency(self.interval, base=base)
        self.tone = Note.get_tone(self.frequency)

    def __repr__(self):
        return f'Note(note={self.note}, volume={self.volume}, duration={self.duration})'

    @staticmethod
    def get_interval(note):
        """Return the interval of this note from the base note"""
        return Note.scale.index(note)

    @staticmethod
    def get_frequency(interval, base=BASE_FREQUENCY):
        """Return the frequency of an interval"""
        return base * SEMITONE**interval

    @staticmethod
    def get_tone(frequency, volume=VOLUME):
        """
        Return the tone of the given frequency

        The output is in bytes such that it may be written directly to a
        pyaudio stream.
        """
        samples = np.arange(int(SAMPLING_RATE*DURATION))
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
    bwah = ['c', 'f', 'f', 'c', 'g', 'g', 'f', 'f', 'c', 'c']
    for note in [Note(x) for x in bwah]:
        print(note)
        stream.write(note.tone)
    # End and close the stream
    stream.stop_stream()
    stream.close()
    # Close pyaudio
    p.terminate()

main()
