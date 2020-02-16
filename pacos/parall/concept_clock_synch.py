from .parall_util import _run_parall


class ClockSynchronizer:

    def add_clock(self, t0: float) -> int:
        return 0

    def synch_start_tick(self, clock: int, tick_dt: float) -> None:
        pass


def test_pair_offset():
    def run_clock(synch: ClockSynchronizer, clock: int):
        for _ in range(5):
            synch.synch_start_tick(clock, 1)

    synch = ClockSynchronizer()
    c1 = synch.add_clock(0)
    c2 = synch.add_clock(0)
    _run_parall([[run_clock, {'synch': synch, 'clock':c1}], 
                 [run_clock, {'synch': synch, 'clock':c2}]
                 ])

