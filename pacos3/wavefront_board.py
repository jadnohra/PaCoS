import os
import copy
import logging
import multiprocessing
from typing import List, Tuple, Callable, Dict, Any
from .interfaces import TimeInterval, Time, IClock, Token, CallMode
from .manual_clock import ManualClock
from .process import Process, Processor


class ProcessConfig:
    def __init__(self, name: str, main_func: Callable[[Processor], None], *, 
                call_mode: CallMode = CallMode(use_proc_state=True), 
                processor_kwargs: Dict = {}, log_level: str = 'WARNING'):
        self.name = name
        self.main_func = main_func
        self.call_mode = call_mode
        self.processor_kwargs = processor_kwargs
        self.log_level = log_level


class Board:
    class ProcessState:
        def __init__(self, mp_context: Any, config: ProcessConfig):
            self.process = Process(mp_context, config.name, config.call_mode,
                                   config.main_func, config.processor_kwargs,
                                   config.log_level)
            self.wave_time = -1
            self.tokens = []

    def __init__(self, process_configs = List[ProcessConfig]):
        mp_context = multiprocessing.get_context('spawn')
        self._proc_states = [self.ProcessState(mp_context,x) 
                             for x in process_configs]
        self._name_idx_dict = {process_configs[i].name: i 
                               for i in range(len(process_configs))}
        self._wave_time = 1

    def _forward_tokens(self, tokens: List[Token], time: Time):
        for token in tokens:
            idx = self._name_idx_dict[token.target.processor]
            self._proc_states[idx].tokens.append(
                                        token.forward_processor(None, time))

    def _step_parall(self, proc_indices: List[int]) -> List[TimeInterval]:
        intervals = []
        synch_clock = ManualClock(self._wave_time)
        logging.info('{}: send take_step {}'.format(os.getpid(), proc_indices))
        for i in proc_indices:
            proc_state = self._proc_states[i]
            proc_state.process.send_step(synch_clock, proc_state.tokens)
        for i in proc_indices:
            proc_state = self._proc_states[i]
            step_result = proc_state.process.recv_step_result().result
            intervals.append(step_result.interval)
            self._forward_tokens(step_result.tokens, 
                                 synch_clock.time + step_result.interval)
        for i, interval in enumerate(intervals):
            proc_state = self._proc_states[proc_indices[i]]
            proc_state.wave_time = proc_state.wave_time + interval
        return intervals

    def _is_steppable(self, proc_index: int) -> bool:
        return self._proc_states[proc_index].wave_time < self._wave_time

    def _step(self, enable_speculate=True) -> TimeInterval:
        steppable_indices = [i for i in range(len(self._proc_states)) 
                             if self._is_steppable(i)]
        if len(steppable_indices) == 0:
            if enable_speculate:
                wave_time = max([x.wave_time for x in self._proc_states])
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

    def has_tokens(self) -> bool:
        return sum([len(x.tokens) for x in self._proc_states]) > 0

    def join(self) -> None:
        for proc_state in self._proc_states:
            proc_state.process.send_exit()
            proc_state.process.join()