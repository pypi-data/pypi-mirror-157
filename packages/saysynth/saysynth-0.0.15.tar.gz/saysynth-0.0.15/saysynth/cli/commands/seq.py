"""
Play a sequence of commands concurrently via yaml specification
"""
import sys
from pathos.multiprocessing import ProcessingPool as Pool

import yaml
import click

from saysynth.cli.commands import chord, midi, note


TRACK_FUNCS = {
    "chord": chord.run,
    "midi": midi.run,
    "note": note.run,
}

def _run_track_func(kwargs):
    kwargs['exec'] = True
    type = kwargs.get('type', None)
    options = kwargs.get('options', {})
    if type not in TRACK_FUNCS:
        raise ValueError(f'Invalid track type: {type}. Choose from: {",".join(TRACK_FUNCS.keys())}')
    return TRACK_FUNCS.get(type)(**options)

def run(**kwargs):
    seq_config = yaml.safe_load(kwargs['seq_config'])
    tracks = seq_config.pop('tracks', [])
    return Pool(len(tracks)).map(_run_track_func, tracks)


@click.command()
@click.argument("seq_config", type=click.File(), required=True)
def cli(**kwargs):
    return run(**kwargs)