import os
import copy
import logging
import multiprocessing
import statistics
import json
from typing import List, Tuple, Callable, Dict, Any
from .interfaces import TimeInterval, Time, Token, ProcessorSnapshot
from .processor import ProcessorConfig, Processor, ProcessorIPC


class Board:
    class ProcessState:
        def __init__(self, config: ProcessorConfig, mp_context: Any):
            self.process_ipc = Processor.mp_create(config, mp_context, False)
            self.tokens = []
            self.snap = ProcessorSnapshot()

    def __init__(self, processor_configs: List[ProcessorConfig], 
                 *, 
                 time_precision: TimeInterval = None,
                 freq_precision: TimeInterval = 0.1,
                 profile_filepath: str = None):
        mp_context = multiprocessing.get_context('spawn')
        if time_precision is None:
            avg_freq = statistics.mean([x.frequency 
                                        for x in processor_configs])
            self._time_precision = freq_precision * 1.0 / avg_freq
        else:
            self._time_precision = time_precision
        if profile_filepath:
            self._configure_profiles(profile_filepath, processor_configs)
        self._proc_states = [self.ProcessState(config, mp_context) 
                             for config in processor_configs]
        self._name_idx_dict = {processor_configs[i].name: i 
                               for i in range(len(processor_configs))}

    def _configure_profiles(self, filepath: str, 
                            processor_configs: List[ProcessorConfig]) -> None:
        profile_data = {}
        with open(filepath) as json_file:
            profile_data = json.load(json_file)
        name_idx_dict = {processor_configs[i].name: i 
                        for i in range(len(processor_configs))}
        for k, v in profile_data.items():
            address = k.split('.')
            processor_name = address[0]
            if processor_name in name_idx_dict:
                config = processor_configs[name_idx_dict[processor_name]]
                processor_local_address = '.'.join(address[1:])
                config.profile_dict[processor_local_address] = v
                logging.debug('Using profile: {}:{}'.format(k, v))

    def _forward_tokens(self, tokens: List[Token]):
        for token in tokens:
            idx = self._name_idx_dict[token.target.processor]
            self._proc_states[idx].tokens.append(
                                        token.forward_processor(None))

    def _step_parall(self, proc_indices: List[int]) -> List[TimeInterval]:
        logging.info('{}: send take_step {}'.format(os.getpid(), proc_indices))
        for i in proc_indices:
            proc_state = self._proc_states[i]
            proc_state.process_ipc.send_step(proc_state.tokens)
            proc_state.tokens = []
        for i in proc_indices:
            proc_state = self._proc_states[i]
            step_msg = proc_state.process_ipc.recv_step_result()
            self._forward_tokens(step_msg.board_tokens)
            proc_state.snap = step_msg.state_snap

    def _barrier_time(self) -> Time:
        return (min([x.snap.time for x in self._proc_states]) 
                + self._time_precision)

    def _is_steppable(self, proc_index: int, barrier_time: Time) -> bool:
        snap = self._proc_states[proc_index].snap
        return not snap.has_exited and snap.time <= barrier_time

    def step(self) -> List[Time]:
        barrier_time = self._barrier_time()
        steppable_indices = [i for i in range(len(self._proc_states)) 
                             if self._is_steppable(i, barrier_time)]
        self._step_parall(steppable_indices)
        return [proc_state.snap.time for proc_state in self._proc_states]

    def all_idle(self) -> bool:
        return all([not x.snap.has_work for x in self._proc_states])
    
    def any_idle(self) -> bool:
        return any([not x.snap.has_work for x in self._proc_states])

    def all_exited(self) -> bool:
        return all([x.snap.has_exited for x in self._proc_states])

    def any_exited(self) -> bool:
        return any([x.snap.has_exited for x in self._proc_states])

    def has_tokens(self) -> bool:
        return sum([len(x.tokens) for x in self._proc_states]) > 0

    def exit(self, join=True) -> None:
        for proc_state in self._proc_states:
            proc_state.process_ipc.send_exit()
            if join:
                proc_state.process_ipc.join()