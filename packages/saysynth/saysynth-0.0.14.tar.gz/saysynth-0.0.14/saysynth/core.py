import random
from typing import Optional, List, Union, Tuple

from midi_utils import midi_to_freq, note_to_midi, midi_chord, ADSR

from .lib import midi, say
from .cli.options import prepare_options_for_say
from .utils import bpm_to_time, frange, rescale
from .constants import (
    SAY_PHONEME_SILENCE,
    SAY_SEGMENT_MAX_DURATION,
    SAY_SEGMENT_SILENCE_DURATION,
    SAY_EMPHASIS,
    SAY_PHONEME_CLASSES,
    SAY_ALL_PHONEMES,
    SAY_TUNE_TAG,
    SAY_TUNED_VOICES,
    SAY_PHONEME_VOICE_CLASSES,
    SAY_VOLUME_RANGE,
)


class Segment:
    # a segment represents an individaul part-of-speech (phoneme) in say
    # a segment can have a duration, a rate, and a sequences of pitches
    # its final state is a string for input to say
    # TODO: move randomization out of here and into the note class
    #
    def __init__(
        self,
        note: Union[int, str],
        velocity: int = 127,
        phoneme: str = "m",
        duration: Union[float, int] = SAY_SEGMENT_MAX_DURATION,
        type: str = "note",
        emphasis: Tuple[int, int] = SAY_EMPHASIS,
        volume_range: Tuple[float, float] = SAY_VOLUME_RANGE,
        duration_sig_digits: int = 4,
        **kwargs,
    ):
        self._phoneme = phoneme
        self._duration = duration
        self._emphasis = emphasis
        self.velocity = velocity
        self.note = note
        self.is_silence = type == "silence"
        self.volume_range = volume_range
        self.duration_sig_digits = duration_sig_digits

    @property
    def phoneme(self):
        return self._phoneme

    @property
    def frequency_envelope(self):
        # lookup frequency
        freq = midi_to_freq(note_to_midi(self.note))
        return f"P {freq}:0 {freq}:100"

    @property
    def duration(self):
        """
        calculate phoneme duration or pass it through
        """
        return round(
            min(self._duration, SAY_SEGMENT_MAX_DURATION), self.duration_sig_digits
        )

    @property
    def volume(self) -> str:
        """
        Translate a midi velocity value (0-127) into a pair of say volume tags, eg: "[[ volm +0.1 ]]"
        """
        return f"[[ volm {rescale(self.velocity, [0, 127], self.volume_range)} ]]"

    @property
    def emphasis(self) -> str:
        """
        Translate a midi velocity value (0-127) into a phoneme emphasis value ("", "1", or "2")
        when provided with a tuple of steps (step_1, step_2) eg: (75, 100)
        """
        if not self.velocity:
            return ""
        if self.velocity > self._emphasis[1]:
            return "2"
        if self.velocity > self._emphasis[0]:
            return "1"
        return ""

    def __str__(self):
        """ "
        Format phoneme text.
        TODO: Handle intra-note modulation?
        """
        if self.is_silence:
            return f"{self.volume} {SAY_PHONEME_SILENCE} {{D {self.duration}}}"
        return f"{self.volume} {self.emphasis}{self.phoneme} {{D {self.duration}; {self.frequency_envelope}}}"

    def __eq__(self, other):
        return str(self) == str(other)


def _get_time(at, bpm, count, time_sig):
    # start position
    if bpm:
        return bpm_to_time(bpm, count, time_sig)
    return at


class Note:
    def __init__(
        self,
        note: Union[int, str] = "A3",
        phoneme: str = "m",
        # start position
        start: Optional[int] = 0,
        start_bpm: Optional[Union[float, int]] = None,
        start_count: Union[str, float, int] = 0,
        start_time_sig: str = "4/4",
        # envelope
        velocity: int = 127,
        attack: Union[float, int] = 0,
        decay: Union[float, int] = 0,
        sustain: Union[float, int] = 1,
        release: Union[float, int] = 0,
        # length
        duration: Union[float, int] = 1000.0,
        duration_bpm: Optional[Union[float, int]] = None,
        duration_count: Union[str, float, int] = 1,
        duration_time_sig: str = "4/4",
        # segmentation
        segment_duration: int = SAY_SEGMENT_MAX_DURATION,
        segment_bpm: Optional[float] = None,
        segment_count: Optional[Union[str, float, int]] = 1.0 / 64.0,
        segment_time_sig: Optional[str] = "4/4",
        # randomization
        randomize_phoneme: Optional[str] = None,
        randomize_velocity: Optional[Tuple[int, int]] = None,
        randomize_octave: Optional[List[int]] = [],
        randomize_segments: Optional[List[str]] = [],
        randomize_start: Optional[Tuple[int, int]] = None,
        **segment_options,
    ):
        """
        Generate say text for a collection of phonemes with adsr + pitch modulation
        """

        self.segment_options = segment_options
        self.note = segment_options.pop("root", note) # root == note
        self.phoneme = phoneme

        # start position
        self.start = _get_time(start, start_bpm, start_count, start_time_sig)
        if randomize_start:
            self.start = random.choice(
                range(self.randomize_start[0], self.randomize_start[1] + 1)
            )

        # duration
        self.duration = _get_time(
            duration, duration_bpm, duration_count, duration_time_sig
        )

        # velocity
        self.velocity = velocity

        # segmentation
        self.segment_duration = min(
            SAY_SEGMENT_MAX_DURATION,
            _get_time(segment_duration, segment_bpm, segment_count, segment_time_sig),
        )
        self.segment_count = int(self.duration / self.segment_duration) + 1
        self._segments = []

        # adsr
        self.adsr = ADSR(attack, decay, sustain, release, samples=self.segment_count)

        # randomization
        self.randomize_phoneme = randomize_phoneme
        self.randomize_velocity = randomize_velocity
        self.randomize_octave = randomize_octave
        self.randomize_segments = randomize_segments
        self.randomize_start = randomize_start

    def _get_phoneme(self):
        # handle phoneme randomization
        if self.randomize_phoneme:
            if self.randomize_phoneme == "all":
                return random.choice(SAY_ALL_PHONEMES)
            elif "," in self.randomize_phoneme:
                return random.choice(
                    [c.strip() for c in self.randomize_phoneme.split(",")]
                )
            else:
                voice, style = self.randomize_phoneme.split(":")
                voice = voice.title()  # allow for lowercase
                try:
                    return random.choice(SAY_PHONEME_VOICE_CLASSES[voice][style])
                except KeyError:
                    raise ValueError(
                        f"Invalid `voice` '{voice}' or `style` '{style}'. "
                        f"`voice` must be one of: {', '.join(SAY_TUNED_VOICES)}. "
                        f"`style` must be one of: {', '.join(SAY_PHONEME_CLASSES)}"
                    )
        return self.phoneme

    def _get_note(self):
        if self.randomize_octave:
            return (random.choice(self.randomize_octave) * 12) + note_to_midi(self.note)
        return self.note

    def _get_velocity(self):
        if self.randomize_velocity:
            return random.choice(
                range(self.randomize_velocity[0], self.randomize_velocity[1] + 1)
            )
        return self.velocity

    def _get_segment(
        self,
        index=0,
        note=None,
        velocity=0,
        phoneme=None,
        duration=None,
        type="silence",
        **kwargs,
    ):
        # optionally randomize every segment.
        if "note" in self.randomize_segments and self.randomize_velocity:
            note = self._get_note()
        if "velocity" in self.randomize_segments and self.randomize_velocity:
            velocity = self._get_velocity()
        if "phoneme" in self.randomize_segments and self.randomize_phoneme:
            phoneme = self._get_phoneme()

        return Segment(
            note=note,
            type=type,
            velocity=velocity * self.adsr.get_value(index),
            phoneme=phoneme,
            duration=duration or self.segment_duration,
            **self.segment_options,
        )

    @property
    def segments(self):

        # cache segments
        if len(self._segments) > 0:
            return self._segments

        # get initial value of note + velocity + phoneme
        note = self._get_note()
        velocity = self._get_velocity()
        phoneme = self._get_phoneme()

        if self.start > 0:

            # create multiple silent phonemes which add up to the desired start position
            start_breaks = frange(0.0, self.start, SAY_SEGMENT_SILENCE_DURATION, 10)
            for index, total_start_time in enumerate(start_breaks):
                segment = self._get_segment(index, type="silence", velocity=0)
                self._segments.append(segment)

            if total_start_time < self.start:
                # add final step of silence
                self._segments.append(
                    self._get_segment(index + 1, type="silence", velocity=0)
                )

        # create multiple phonemes which add up to the phoneme_duration
        segment_breaks = frange(0.0, self.duration, self.segment_duration, 10)
        for index, total_time in enumerate(segment_breaks):
            segment = self._get_segment(index, note, velocity, phoneme, type="note")
            self._segments.append(segment)

        if total_time < self.duration and len(self._segments) < self.segment_count:
            # add final step
            self._segments.append(
                self._get_segment(
                    index + 1,
                    note,
                    velocity,
                    phoneme,
                    duration=self.duration - total_time,
                    type="note",
                )
            )
        return self._segments

    def __str__(self):
        return SAY_TUNE_TAG + "\n" + "\n".join([str(s) for s in self.segments])

    def __eq__(self, other):
        return str(self) == str(other)


class Chord:
    _notes = []

    def __init__(self, **kwargs):
        og_note = kwargs.pop("note", "A1")
        self.root = kwargs.pop("root", og_note)  # root == note
        self.note_options = kwargs
        self.midi_notes = midi_chord(root=self.root, **self.note_options)

    def get_kwargs(self, **kwargs):
        """
        get kwargs + update with new ones
        used for mapping similar kwards over different notes
        """
        d = dict(self.note_options.items())
        d.update(kwargs)
        return d

    @property
    def notes(self):
        if not len(self._notes):
            for n in self.midi_notes:
                self._notes.append(Note(**self.get_kwargs(note=n)))
        return self._notes

    def write(self, output_file):
        for note in self.notes:
            fn = ".".join(output_file.split(".")[:-1])
            ext = "txt" if "." not in output_file else output_file.split(".")[-1]
            note_output_file = f"{fn}-{note.note}.{ext}"
            with open(note_output_file, "w") as f:
                f.write(str(note))

    def play(self):
        # generate a command for each note in the chord
        commands = []
        for note in self.notes:
            cmd_kwargs = prepare_options_for_say(
                text=str(note), **self.get_kwargs(note=note.note, type="note")
            )
            commands.append(cmd_kwargs)
        say.spawn(commands)


class MidiTrack:
    def __init__(
        self,
        midi_file: str,
        loops: int = 1,
        # start position
        start: Optional[int] = 0,
        start_bpm: Optional[Union[float, int]] = None,
        start_count: Union[str, float, int] = 0,
        start_time_sig: str = "4/4",
        **kwargs,
    ):
        """
        TODO: multichannel midi
        """
        self.midi_file = midi_file
        self.loops = loops
        self.start = _get_time(start, start_bpm, start_count, start_time_sig)
        self.start_segment_count = int(self.start / SAY_SEGMENT_SILENCE_DURATION) + 1
        self.kwargs = kwargs
        self._notes = []
        self._start_segments = []

    @property
    def notes(self):
        if len(self._notes):
            return self._notes
        for _ in range(0, self.loops):
            for note in midi.process(self.midi_file):
                self.kwargs.update(note)
                self._notes.append(Note(**self.kwargs))
        return self._notes

    def _get_start_text(self):
        if not self.start:
            return ""

        # create multiple silent segments which add up to the start position
        if not len(self._start_segments):
            for _, total_time in enumerate(
                frange(0.0, self.start, SAY_SEGMENT_SILENCE_DURATION, 10)
            ):
                self._start_segments.append(
                    Segment(
                        type="silence",
                        velocity=0,
                        duration=SAY_SEGMENT_SILENCE_DURATION,
                    )
                )

            if (
                total_time < self.start
                and len(self._start_segments) < self.start_segment_count
            ):
                # add final silent step
                self._start_segments.append(
                    Segment(
                        type="silence", velocity=0, duration=self.start - total_time
                    )
                )
        return "\n".join(self._start_segments)

    def __str__(self):
        return (
            SAY_TUNE_TAG
            + "\n"
            + self._get_start_text()
            + "\n"
            + "\n".join(map(str, self.notes))
        )

    def __repr__(self):
        return f"<MidiTrack {self.midi_file}>"
