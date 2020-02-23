import os
import multiprocessing
from typing import List, Tuple, Callable, Dict
from .interfaces import IMsgRouter, IMessage, IEngine, TimeInterval


class ParallelWavefrontContext(IMsgRouter):
    def __init__(self):
        self._engines = []
        self._name_engine_dict = {}
        self._wave_t1 = None
        self._wave_times = []
        self._parall_msg_queue = multiprocessing.Queue()

    def route(self, msg: IMessage) -> None:
         self._parall_msg_queue.put(msg)

    @property
    def engine_count(self) -> int:
        return len(self._engines)

    @staticmethod
    def _run_parall(funcs_kwargs: List[Tuple[Callable, Dict]]) -> None:
        processes = []
        for func, kwargs in funcs_kwargs:
            p = multiprocessing.Process(target=func, kwargs=kwargs)
            processes.append(p)
            p.start()
        for p in processes:
            p.join()

    def _step_parall(self, engines: List[IEngine]) -> List[TimeInterval]:
        def step_engine(engines, out_intervals, index):
            out_intervals[index] = engines[index].step(self)
        
        intervals = [None]*len(engines)
        self._run_parall([(lambda i: step_engine(engines, intervals, i), {})
                          for i in range(len(engines))])
        self._process_parall_msg_queue()
        return intervals

    def _process_parall_msg_queue(self) -> None:
        queue = self._parall_msg_queue
        while not queue.empty():
            msg = queue.get()
            path_split = msg.target.split(os.path.sep)
            engine_name = path_split[0]
            path_remaining = os.path.sep.join(path_split[1:])
            msg.forward(path_remaining)
            self._name_engine_dict[engine_name].put(msg)
        
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
        return min(intervals)
