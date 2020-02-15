import sys
from .example_pingpong import run_pingpong
from .example_besteffort import run_besteffort
from .example_synch import run_synch


run_all = '--all' in sys.argv

if run_all or '--pingpong' in sys.argv :
    run_pingpong()
if run_all or '--besteffort' in sys.argv:
    run_besteffort()
if run_all or '--synch' in sys.argv:
    run_synch()
