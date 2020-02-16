from typing import List
import threading
import time
from .parall_util import _run_parall


class ClockSynchronizer:
    class ClockInfo:
        def __init__(self, t0: float, t1: float):
            self.t0 = float(t0)
            self.t1 = float(t1) if t1 is not None else t1

    def __init__(self):
        self._clock_id_counter = 0
        self._clocks = {}
        self._join_matrix = []

    def add_clock(self, t0: float) -> int:
        id = self._clock_id_counter
        self._clock_id_counter = self._clock_id_counter + 1
        self._clocks[id] = self.ClockInfo(t0, None)
        return id

    def _ensure_join_entry(self, i: int, j: int) -> None:
        i = max(i, len(self._join_matrix))
        while i >= len(self._join_matrix):
            self._join_matrix.append([])
        j = max(j, len(self._join_matrix[i]))
        while j >= len(self._join_matrix[i]):
            self._join_matrix[i].append(None)

    def _release_join_entry(self, i: int, j: int) -> None:
        self._ensure_join_entry(i, j)
        if self._join_matrix[i][j] is not None:
            print('{} releasing {}'.format(j, i))
            self._join_matrix[i][j].release()
            self._join_matrix[i][j].notify_all()
            self._join_matrix[i][j] = None

    def _acquire_join_entry(self, i: int, j: int) -> None:
        self._ensure_join_entry(i, j)
        if self._join_matrix[i][j] is None:
            self._join_matrix[i][j] = threading.Condition()
            self._join_matrix[i][j].acquire()
        else:
            raise RuntimeError('PANIC!')

    def _release_dependents(self, clock: int) -> None:
        for i in range(len(self._join_matrix)):
            self._release_join_entry(i, clock)
    
    def _gather_dependencies(self, clock: int, clock_t1: float) -> List[int]:
        def is_dependent(clock: int, other_info: "ClockInfo") -> bool:
            return False  # TODO, continue here
        return [other for (other, other_info) in self._clocks.items()
                if (other != clock and is_dependent(clock, other_info))]

    def _acquire_dependencies(self, clock: int, dep_indicies: List[int]
                              ) -> None:
        for i in dep_indicies:
            self._acquire_join_entry(clock, i)

    def _wait_dependencies(self, clock: int, dep_indicies: List[int]) -> None:
        for dep in dep_indicies:
            print('{} waiting on {}'.format(clock, dep))
            self._join_matrix[clock][dep].wait()

    def synch_tick(self, clock: int, tick_dt: float) -> None:
        self._release_dependents(clock)
        clock_t1 = (self._clocks[clock].t1 if self._clocks[clock].t1 
                    else self._clocks[clock].t0)
        clock_t2 = clock_t1 + tick_dt
        deps = self._gather_dependencies(clock, clock_t2)
        self._acquire_dependencies(clock, deps)
        self._clocks[clock].t0 = clock_t1
        self._clocks[clock].t1 = clock_t2
        self._wait_dependencies(clock, deps)


def test_pair_offset():
    def run_clock(synch: ClockSynchronizer, clock: int):
        for _ in range(5):
            time.sleep(0.1 + clock*0.2)
            print('tick', clock)
            synch.synch_tick(clock, 1)

    synch = ClockSynchronizer()
    c0 = synch.add_clock(0.5)
    c1 = synch.add_clock(0)
    _run_parall([[run_clock, {'synch': synch, 'clock':c0}], 
                 [run_clock, {'synch': synch, 'clock':c1}]
                 ])

