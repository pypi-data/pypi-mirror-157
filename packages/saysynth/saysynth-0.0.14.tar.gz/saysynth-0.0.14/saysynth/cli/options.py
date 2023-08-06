from itertools import count
from tokenize import group
import click

from midi_utils.constants import CHORDS
from saysynth.constants import (
    SAY_COLORS,
    SAY_EMPHASIS,
    SAY_ALL_PHONEMES,
    SAY_TUNED_VOICES,
    SAY_PHONEME_CLASSES,
    SAY_SEGMENT_MAX_DURATION,
    SAY_VOLUME_RANGE,
)


def group_options(*options):
    def wrapper(function):
        for option in reversed(options):
            function = option(function)
        return function

    return wrapper


def prepare_options_for_say(text: str, **kwargs):
    # handle some param edge cases
    rp = kwargs.get("randomize_phoneme")
    # for convenience, set the voice option to the one specified
    # in randomize phoneme.
    if rp and ":" in rp:
        kwargs["voice"] = rp.split(":")[0].strip().title()
    kwargs["text"] = text
    kwargs["use_tempfile"] = True
    return kwargs


# Duration Options

duration_opt = click.option(
    "-d",
    "--duration",
    default=1_000_000,
    type=int,
    help="The duration of the note in milliseconds.",
)

bpm_opt = click.option(
    "-db",
    "--duration-bpm",
    "duration_bpm",
    default=None,
    type=float,
    help="The bpm to use when calculating note duration. Using this option will override --duration",
)
count_opt = click.option(
    "-dc",
    "--duration-count",
    "duration_count",
    default=4,
    type=str,
    show_default=True,
    help="The note length to use when calculating note duration (eg: 1/8 or 0.123 or 3)",
)
time_sig_opt = click.option(
    "-dts",
    "--duration-time-sig",
    "duration_time_sig",
    default="4/4",
    type=str,
    show_default=True,
    help="The time signature to use when calculating note duration",
)

duration_opts = group_options(duration_opt, bpm_opt, count_opt, time_sig_opt)

# Phoneme Options

phoneme_opt = click.option(
    "-p",
    "--phoneme",
    default="m",
    help="The phoneme to use.",
    show_default=True,
    type=click.Choice(SAY_ALL_PHONEMES),
)
randomize_phoneme_opt = click.option(
    "-rp",
    "--randomize-phoneme",
    show_default=True,
    help=(
        "Randomize the phoneme for every note. "
        "If `all` is passed, all phonemes will be used. "
        "Alternatively pass a list of phonemes (eg 'm,l,n') or a voice and style, eg: Fred:drone. "
        f"Valid voices include: {', '.join(SAY_TUNED_VOICES)}. "
        f"Valid styles include: {', '.join(SAY_PHONEME_CLASSES)}."
    ),
)

phoneme_opts = group_options(
    phoneme_opt,
    randomize_phoneme_opt,
)

# Start Options


randomize_start_opt = click.option(
    "-rt",
    "--randomize-start",
    type=int,
    nargs=2,
    help="Randomize the number of milliseconds to silence to add before the say text. The first number passed in is the minimum of the range, the second is the max.",
)

start_opt = click.option(
    "-t",
    "--start",
    default=0,
    show_default=True,
    type=float,
    help="The number of milliseconds of silence to add before the say text.",
)
start_bpm_opt = click.option(
    "-tb",
    "--start-bpm",
    default=None,
    type=float,
    help="The bpm to use when calculating start time",
)
start_count_opt = click.option(
    "-tc",
    "--start-count",
    default=4,
    type=str,
    show_default=True,
    help="The note length to use when calculating start time (eg: 1/8 or 0.123 or 3)",
)
start_time_sig_opt = click.option(
    "-tts",
    "--start-time-sig",
    default="4/4",
    type=str,
    show_default=True,
    help="The time signature to use when calculating start time",
)

start_opts = group_options(
    randomize_start_opt,
    start_opt,
    start_bpm_opt,
    start_count_opt,
    start_time_sig_opt,
)


# Segment Options

randomize_segments_opt = click.option(
    "-rs",
    "--randomize-segments",
    type=lambda x: [str(s) for s in x.split(",")] if len(x) else [],
    required=False,
    default=[],
    help="Randomize every segment's 'phoneme', 'note', and/or 'velocity'. Use commas to separate multiple randomization strategies",
)

segment_duration_opt = click.option(
    "-sd",
    "--segment-duration",
    default=SAY_SEGMENT_MAX_DURATION,
    show_default=True,
    type=float,
    help="The duration an individual phoneme",
)
segment_bpm_opt = click.option(
    "-sb",
    "--segment-bpm",
    default=None,
    type=float,
    help="The bpm to use when calculating phoneme duration",
)
segment_count_opt = click.option(
    "-sc",
    "--segment-count",
    default=4,
    type=str,
    show_default=True,
    help="The note length to use when calculating phoneme duration (eg: 1/8 or 0.123 or 3)",
)
segment_time_sig_opt = click.option(
    "-sts",
    "--segment-time-sig",
    default="4/4",
    type=str,
    show_default=True,
    help="The time signature to use when calculating phoneme duration",
)

segment_opts = group_options(
    randomize_segments_opt,
    segment_duration_opt,
    segment_bpm_opt,
    segment_count_opt,
    segment_time_sig_opt,
)

# Velocity Options

velocity_opt = click.option(
    "-vl",
    "--velocity",
    type=int,
    show_default=True,
    default=110,
    help="The midi velocity value to use for each note.",
)
velocity_emphasis_opt = click.option(
    "-ve",
    "--velocity-emphasis",
    "emphasis",
    type=int,
    nargs=2,
    show_default=True,
    default=SAY_EMPHASIS,
    help="Two midi velocity values (between 0 and 127) at which to add emphasis to a note/segment",
)
volume_range_opt = click.option(
    "-vr",
    "--volume-range",
    type=float,
    nargs=2,
    show_default=True,
    default=SAY_VOLUME_RANGE,
    help="The min and max volumes (range: 0.0-1.0) to use when mapping from midi velocities",
)
randomize_velocity_opt = click.option(
    "-rv",
    "--randomize-velocity",
    type=int,
    nargs=2,
    help="Randomize a note's velocity by supplying a min and max midi velocity (eg: -rv 40 120)",
)

velocity_opts = group_options(
    velocity_opt,
    velocity_emphasis_opt,
    volume_range_opt,
    randomize_velocity_opt,
)


# ADSR Options

attack_opt = click.option(
    "-at",
    "--attack",
    default=0.0,
    show_default=True,
    type=float,
    help="The percentage of the duration it takes to reach the max volume of the note",
)
decay_opt = click.option(
    "-de",
    "--decay",
    default=0.0,
    type=float,
    help="The percentage of the duration it takes to reach the sustain volume of the note",
)
sustain_opt = click.option(
    "-su",
    "--sustain",
    default=1.0,
    type=float,
    show_default=True,
    help="The the sustain volume of the note",
)
release_opt = click.option(
    "-re",
    "--release",
    default=0.0,
    type=float,
    show_default=True,
    help="The percentage of the duration it takes to reach the min volume of the note",
)

adsr_opts = group_options(
    attack_opt,
    decay_opt,
    sustain_opt,
    release_opt,
)

# Say Options
exec_opt = click.option(
    "-x",
    "--exec",
    is_flag=True,
    default=False,
    help="Run the generated text through the say command.",
)

rate_opt = click.option(
    "-r", "--rate", type=int, default=70, show_default=True, help="Rate to speak at"
)
voice_opt = click.option(
    "-v",
    "--voice",
    type=click.Choice(SAY_TUNED_VOICES),
    default="Fred",
    show_default=True,
    help="Voice to use",
)
# input_file_opt = click.option(
#     '-i',
#     "--input-file",
#     type=click.File(mode = "w"),
#     help="File to read text input from"
# )
output_file_opt = click.option(
    "-ao",
    "--audio-output-file",
    type=str,
    help="File to write audio output to",
)
audio_device_opt = click.option(
    "-ad",
    "--audio-device",
    type=str,
    help="Name of the audio device to send the signal to",
)
networks_send_opt = click.option(
    "-ns", "--network-send", type=str, help="Network address to send the signal to"
)
stereo_opt = click.option(
    "-st",
    "--stereo",
    is_flag=True,
    default=False,
    help="Whether or not to generate a stereo signal",
)
sample_size_opt = click.option(
    "-ss",
    "--sample-size",
    type=int,
    default=32,
    help="Sample size of the signal (1:32)",
)
sample_rate_opt = click.option(
    "-sr",
    "--sample-rate",
    type=int,
    default=22050,
    help="Sample rate of the signal (0:22050)",
)
quality_opt = click.option(
    "-q", "--quality", type=int, default=127, help="Quality of the signal (1:127)"
)
progress_bar_opt = click.option(
    "-pg",
    "--progress",
    is_flag=True,
    default=False,
    help="Whether or not to display an interactive progress bar",
)
interactive_opt = click.option(
    "-in",
    "--interactive",
    is_flag=True,
    default=False,
    help="Whether or not to display highlighted text",
)
text_color_opt = click.option(
    "-cf",
    "--text-color",
    type=click.Choice(SAY_COLORS),
    default="white",
    help="The text color to use when displaying highlighted text",
)
bg_color_opt = click.option(
    "-cb",
    "--bg-color",
    type=click.Choice(SAY_COLORS),
    default="black",
    help="The background color to use when displaying highlighted text",
)


say_opts = group_options(
    exec_opt,
    rate_opt,
    voice_opt,
    output_file_opt,
    audio_device_opt,
    networks_send_opt,
    stereo_opt,
    sample_size_opt,
    sample_rate_opt,
    quality_opt,
    progress_bar_opt,
    interactive_opt,
    text_color_opt,
    bg_color_opt,
)

# Chord Options

chord_opt = click.option(
    "-c",
    "--chord",
    required=False,
    default="min6_9",
    type=click.Choice([c.lower() for c in CHORDS.keys()]),
    help="An optional name of a chord to build using the note as root.",
)
chord_velocities_opt = click.option(
    "-cv",
    "--chord-velocities",
    required=False,
    type=lambda x: [int(i.strip()) for i in x.split(",")] if x else [],
    help="A list of integers (eg: '50,100,127') specifying the midi velocity each note i the chord. The length of this list much match the number of notes in the chord. --volume-range anyd --velocity-steps also modify this parameter",
)
chord_inversions_opt = click.option(
    "-ci",
    "--chord-inversions",
    "inversions",
    default=[],
    required=False,
    type=lambda x: [int(i.strip()) for i in x.split(",")] if x else [],
    help="A list of integers (eg: '0,1,-1') specifying the direction and amplitude to invert each note. The length of this list much match the number of notes in the chord (post-stack).",
)
chord_stack_opt = click.option(
    "-cs",
    "--chord-stack",
    "stack",
    default=0,
    required=False,
    type=int,
    help="Stack a chord up (eg: '1' or '2') or down (eg: '-1' or '-2').",
)

chord_opts = group_options(
    chord_opt,
    chord_inversions_opt,
    chord_stack_opt,
)
