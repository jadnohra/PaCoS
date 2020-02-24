import os
import copy
import multiprocessing
from typing import List, Tuple, Callable, Dict
from .interfaces import (
                IMsgRouter, IMessage, IEngine, TimeInterval, IClock, ITopology)
from .msg_router import MsgRouter


class ParallWavefrontTopology(ITopology):
    def __init__(self, clock: IClock):
        self._engines = []
        self._name_engine_dict = {}
        self._wave_t1 = None
        self._wave_times = []
        # self._router = ParallMsgRouter(self, clock)

    def add_engine(self, engine: IEngine) -> None:
        engine.init_address(None)
        self._engines.append(engine)
        self._name_engine_dict[engine.name] = engine

    @property
    def engine_count(self) -> int:
        return len(self._engines)

    def _step_parall(self, engines: List[IEngine]) -> List[TimeInterval]:
        intervals = multiprocessing.Array('i', len(engines), lock=False)
        pids = multiprocessing.Array('i', len(engines), lock=False)
        pid_fill_task = multiprocessing.JoinableQueue()
        for i in range(len(engines)):
            pid_fill_task.put(None)
        
        def step_engine(router: IMsgRouter, index: int):
            pid_fill_task.get()
            pids[index] = os.getpid()
            pid_fill_task.task_done()
            pid_fill_task.join()
            local_router = copy.copy(router)
            local_router.set_routing_dict({pids[i]: engines[i]
                                           for i in range(len(processes))})
            intervals[index] = engines[index].step(local_router)
        
        funcs_kwargs = [(lambda i: step_engine(self._router, i), {'i':i}) 
                        for i in range(len(engines))]
        processes = []
        for func, kwargs in funcs_kwargs:
            p = multiprocessing.Process(target=func, kwargs=kwargs)
            processes.append(p)
            p.start()
        for p in processes:
            p.join()
        self._router.flush()
        return list(intervals)

    def get_engine(self, engine_name: str) -> IEngine:
        if engine_name is None and len(self._engines) >= 0:
            return self._engines[0]
        return self._name_engine_dict.get(engine_name, None)
        
    def step(self) -> TimeInterval:
        cand_engines = [self._engines[i] for i in range(self.engine_count)
                        if (self._wave_t1 is None or 
                            self._wave_times[i] < self._wave_t1)]
        if len(cand_engines) == 0:
            wave_t1 = max(self._wave_times)
            if wave_t1 > self._wave_t1:
                return self.step()
            else:
                return 0
        intervals = self._step_parall(cand_engines)
        nonzero_intervals = [x for x in intervals if x > 0]
        return min(nonzero_intervals) if len(nonzero_intervals) else 0
