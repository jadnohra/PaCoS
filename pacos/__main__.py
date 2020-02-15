import sys
from .serial.example_pingpong import run_pingpong
from .serial.example_besteffort import run_besteffort
from .serial.example_synch import run_synch
from .parall.example_synch_parall import run_synch_parall


run_all = '--all' in sys.argv

if run_all or '--pingpong' in sys.argv :
    run_pingpong()
if run_all or '--besteffort' in sys.argv:
    run_besteffort()
if run_all or '--synch' in sys.argv:
    run_synch()
if run_all or '--synch-parall' in sys.argv:
    run_synch_parall()
