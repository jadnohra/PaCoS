import sys
from .example_pingpong import run_pingpong
from .example_besteffort import run_besteffort
from .example_synch import run_synch


if '--pingpong' in sys.argv:
    run_pingpong()
if '--besteffort' in sys.argv:
    run_besteffort()
if '--synch' in sys.argv:
    run_synch()
