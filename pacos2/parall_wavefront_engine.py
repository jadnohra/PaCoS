import os
import copy
import logging
import multiprocessing
from typing import List, Tuple, Callable, Dict, Any
from .interfaces import (
                IMsgRouter, IMessage, IEngine, TimeInterval, IClock)
from .manual_clock import ManualClock
from .msg_routers import BounceMsgRouter
from .parall_process import ParallProcess


class ParallWavefrontEngine:
    def __init__(self, mp_context: Any, 
                 process_classes = List["ParallProcessClass"]):
        self._processes = [proc_cls(mp_context) for proc_cls in process_classes]
        self._process_engine_names = [None] * len(self._processes)
        self._engine_name_index_dict = {}
        self._wave_times = [-1]*len(self._processes)
        self._wave_time = 1

    def _update_engine_names(self, proc_index: int, eng_names: List[str]
                             ) -> None:
        if eng_names is None:
            return
        self._process_engine_names = eng_names
        for name in eng_names:
            self._engine_name_index_dict[name] = proc_index

    def _step_parall(self, proc_indices: List[int]) -> List[TimeInterval]:
        def put_msg_list(msgs: List[IMessage], 
                      engine_msg_lists: Dict[str, List[IMessage]]):
            for msg in msgs:
                key = msg.target.engine
                if key not in engine_msg_lists:
                    engine_msg_lists[key] = []
                engine_msg_lists[key].append(msg)
        intervals = []
        engine_msg_lists = {}
        synch_clock = ManualClock(self._wave_time)
        logging.info('{}: send take_step {}'.format(os.getpid(), proc_indices))
        for i in proc_indices:
            self._processes[i].send_take_step(synch_clock)
        for i in proc_indices:
            step_result = self._processes[i].recv_step_result()
            intervals.append(step_result.interval)
            put_msg_list(step_result.msgs, engine_msg_lists)
            self._update_engine_names(i, step_result.engine_names)
        
        for eng_name, msgs in engine_msg_lists.items():
            proc_index = self._engine_name_index_dict.get(eng_name, None)
            self._processes[proc_index].send_msgs(msgs)

        for i, interval in enumerate(intervals):
            proc_i = proc_indices[i]
            self._wave_times[proc_i] = self._wave_times[proc_i] + interval

        return intervals

    def _is_steppable(self, proc_index: int) -> bool:
        return self._wave_times[proc_index] < self._wave_time

    def _step(self, enable_speculate=True) -> TimeInterval:
        steppable_indices = [i for i in range(len(self._processes)) 
                             if self._is_steppable(i)]
        if len(steppable_indices) == 0:
            if enable_speculate:
                wave_time = max(self._wave_times)
                if wave_time > self._wave_time:
                    self._wave_time = wave_time
                else:
                    self._wave_time = self._wave_time + 1
                return self._step(enable_speculate=False)
            else:
                return 0
        intervals = self._step_parall(steppable_indices)
        nonzero_intervals = [x for x in intervals if x > 0]
        return min(nonzero_intervals) if len(nonzero_intervals) else 0

    def step(self) -> TimeInterval:
      return self._step()

    def join(self) -> None:
        for proc in self._processes:
            proc.send_exit()
            proc.join()