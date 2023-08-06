from saysynth import Segment, Note, MidiTrack


def test_segment():
    segment = Segment(note="A3", velocity=127, duration=100)
    assert str(segment) == "[[ volm 1.0 ]] 2m {D 100; P 220:0 220:100}"


def test_note():
    note = Note(
        note="C4",
        phoneme="m",
        velocity=127,
        attack=0.1,
        decay=0.2,
        sustain=0.3,
        release=0.5,
        bpm=126,
        count=1 / 2,
        segment_bpm=126,
        segment_count=1 / 32,
    )
    assert note.segments[0] == "[[ volm 0.59 ]] m {D 59.5238; P 261.63:0 261.63:100}"
    assert note.segments[-1] == "[[ volm 0.0 ]] m {D 59.5238; P 261.63:0 261.63:100}"
