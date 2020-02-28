import os
import copy
import logging
import multiprocessing
from typing import List, Tuple, Callable, Dict, Any
from .interfaces import TimeInterval, Time, Token
from .manual_clock import ManualClock
from .processor import ProcessorConfig, Processor, ProcessorIPC


class Board:
    class ProcessState:
        def __init__(self, config: ProcessorConfig, mp_context: Any):
            self.process_ipc = Processor.mp_create(config, mp_context, False)
            self.time = -1
            self.tokens = []

    def __init__(self, processor_configs = List[ProcessorConfig]):
        mp_context = multiprocessing.get_context('spawn')
        self._proc_states = [self.ProcessState(config, mp_context) 
                             for config in processor_configs]
        self._name_idx_dict = {processor_configs[i].name: i 
                               for i in range(len(processor_configs))}
        self._wave_time = 0

    def _forward_tokens(self, tokens: List[Token]):
        for token in tokens:
            idx = self._name_idx_dict[token.target.processor]
            self._proc_states[idx].tokens.append(
                                        token.forward_processor(None))

    def _step_parall(self, proc_indices: List[int]) -> List[TimeInterval]:
        #synch_clock = ManualClock(self._wave_time)
        logging.info('{}: send take_step {}'.format(os.getpid(), proc_indices))
        for i in proc_indices:
            proc_state = self._proc_states[i]
            proc_state.process_ipc.send_step(proc_state.tokens, 0)
            proc_state.tokens = []
        for i in proc_indices:
            proc_state = self._proc_states[i]
            step_msg = proc_state.process_ipc.recv_step_result()
            self._forward_tokens(step_msg.result.tokens)
            proc_state.time = step_msg.state_snap.time

    def _is_steppable(self, proc_index: int) -> bool:
        return self._proc_states[proc_index].time < self._wave_time

    def _step(self) -> List[Time]:
        steppable_indices = [i for i in range(len(self._proc_states)) 
                             if self._is_steppable(i)]
        if len(steppable_indices) == 0:
            # No processor is behind the wave, speculatively step all
            steppable_indices = range(len(self._proc_states))
        self._step_parall(steppable_indices)
        return [proc_state.time for proc_state in self._proc_states]

    def step(self) -> TimeInterval:
        return self._step()

    def has_tokens(self) -> bool:
        return sum([len(x.tokens) for x in self._proc_states]) > 0

    def exit(self, join=True) -> None:
        for proc_state in self._proc_states:
            proc_state.process_ipc.send_exit()
            if join:
                proc_state.process_ipc.join()