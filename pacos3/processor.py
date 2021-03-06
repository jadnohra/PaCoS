import copy
import multiprocessing
import logging
from random import Random
from abc import ABC, abstractmethod
from typing import List, Any, Callable, Dict
from .time import TimeInterval, Time, StepCount
from .interfaces import (
    Address, ITokenSource, IActor, IProcedure, IProcessorAPI, ProcState, 
    CallResult, IProcessor, Token)
from .ipc import SynchStep, SynchStepResult, SynchExit


class ProcessorConfig:
    def __init__(self, *,
                main: Callable[['Processor'], List[Address]] = None,
                name: str = None,
                frequency: float = 1.0*(10**9),
                call_queue_rand: Random = None, 
                call_source_rand: Random = None,
                log_level: str = 'WARNING'):
        self.main_func = main
        self.frequency = frequency
        self.name = name
        self.call_queue_rand = call_queue_rand
        self.call_source_rand = call_source_rand
        self.log_level = log_level


class ProcessorIPC:
    def __init__(self, name: str, process: multiprocessing.Process, conn: Any):
        self._name = name
        self._process = process
        self._conn = conn

    def start(self) -> None:
        self._process.start()

    def join(self) -> None:
        self._process.join()
    
    def send_step(self, board_tokens: List[Token]) -> None:
        self._conn.send(SynchStep(board_tokens)) 
        
    def send_exit(self) -> None:
        self._conn.send(SynchExit())
        
    def recv_step_result(self) -> Any:
        return self._conn.recv()
    
    @property
    def name(self) -> str:
        return self._name


class Processor(IProcessor, IProcessorAPI):
    def __init__(self, config: ProcessorConfig = ProcessorConfig(), 
                 log_pid: bool = False):
        self._name = config.name
        self._step_counter = 0
        self._frequency = config.frequency
        self._flag_exit = False
        self._has_exited = False
        self._actors = []
        self._sources = []
        self._name_actor_dict = {}
        self._token_pool = []
        self._token_queue = []
        self._board_tokens = []
        self._waiting_proc_addr = None
        self._token_queue_rand = config.call_queue_rand
        self._token_source_rand = config.call_source_rand
        if config.log_level:
            format = ('%(levelname)s-%(process)d: %(message)s' 
                      if log_pid else '%(levelname)s: %(message)s') 
            logging.basicConfig(format=format,
                                level=logging.getLevelName(
                                        config.log_level.upper()))
        self._init_calls = config.main_func(self) if config.main_func else []


    @staticmethod
    def mp_create(config: ProcessorConfig, mp_context: Any, 
                  create_paused = False) -> multiprocessing.Process:
        master_conn, child_conn = mp_context.Pipe()
        proc_args = {'config': config, 'conn': child_conn}
        process = mp_context.Process(target=Processor._mp_process_func, 
                                     kwargs=proc_args)
        if not create_paused:
            process.start()
        return ProcessorIPC(config.name, process, master_conn)

    @staticmethod
    def _mp_process_func(config: ProcessorConfig, conn: Any):
        processor = Processor(config, True)
        while True:
            synch_msg = conn.recv()
            if isinstance(synch_msg, SynchStep):
                logging.debug('stepping')
                processor.step(synch_msg.board_tokens)
                conn.send(SynchStepResult(processor._pop_board_tokens(), 
                                          processor.snap()))
            else:
                break

    @property
    def name(self) -> str:
        return self._name

    @property
    def api(self) -> IProcessorAPI:
        return self
    
    @property
    def step_count(self) -> StepCount:
        return self._step_counter

    @property
    def frequency(self) -> float:
        return self._frequency

    @property
    def time(self) -> Time:
        return self.steps_to_interval(self._step_counter)

    def exit(self, exit_result: CallResult = CallResult()) -> CallResult:
        self._flag_exit = True
        return exit_result

    @property
    def has_exited(self) -> bool:
        return self._has_exited

    def steps_to_interval(self, step_count: StepCount) -> TimeInterval:
        return step_count / self._frequency

    def interval_to_steps(self, time_interval: TimeInterval) -> Time:
        return time_interval * self._frequency

    def add_actor(self, actor: IActor) -> None:
        self._actors.append(actor)
        self._name_actor_dict[actor.name] = actor

    def _is_local_address(self, address: Address):
        return address.processor is None

    def _pop_board_tokens(self) -> List[Token]:
        ret, self._board_tokens = self._board_tokens, []
        return ret

    def _put_tokens(self, tokens: List[Token]) -> None:
        for token in tokens:
            if self._is_local_address(token.target):
                self._token_pool.append(token)
            else:
                self._board_tokens.append(token)

    def add_source(self, source: ITokenSource) -> None:
        self._sources.append(source)

    def get_actor(self, actor_name: str) -> IActor:
        if actor_name is None and len(self._actors) >= 0:
            return self._actors[0]
        return self._name_actor_dict.get(actor_name, None)

    def get_proc(self, address: Address) -> IProcedure:
        return self.get_actor(address.actor).get_procedure(address.proc)

    def _stamp_tokens(self, tokens: List[Token], time_diff: TimeInterval = 0
                      ) -> List[Token]:
        for call in tokens:
            call.stamp(self.time + time_diff)
        return tokens

    def _generate_tokens(self) -> List[Token]:
        if self._token_source_rand:
            sources = copy.copy(self._sources)
            self._token_source_rand.shuffle(sources)
        else:
            sources = reversed(self._sources)
        tokens = sum([source.generate(self) for source in sources], [])
        return self._stamp_tokens(tokens)

    def _process_call_result(self, result: CallResult) -> None:
        self._stamp_tokens(result.calls, 
                           self.steps_to_interval(result.step_count))
        self._step_counter = self._step_counter + result.step_count
        self._put_tokens(result.calls)
        self._enqueue_ready_tokens()
        if self._flag_exit:
            self._has_exited = True

    def wait(self, partial_result: CallResult = CallResult()) -> CallResult:
        if not self._is_proc_ready(self.get_proc(self._call_stack_proc_addr)):
            logging.error('wait issued from blocked proc, will deadlock')
        self._waiting_proc_addr = self._call_stack_proc_addr
        return partial_result

    def do_call(self, address: Address, token: Token) -> None:
        self._call_stack_proc_addr = copy.copy(address)
        result = self.get_proc(address).call(token, self.api)
        self._process_call_result(result)

    def _pop_call_queue_token(self) -> None:
        if len(self._token_queue) != 0:
            token = self._token_queue.pop()
            self.do_call(token.target, token)

    def _pop_call_init(self) -> None:
        if len(self._init_calls) != 0:
            address = self._init_calls.pop()
            self.do_call(address, None)

    def _is_proc_ready(self, proc: IProcedure) -> bool:
        return proc.state != ProcState.CLOSED

    def _is_token_proc_ready(self, token: Token) -> bool:
        return self._is_proc_ready(self.get_proc(token.target))

    def _enqueue_ready_tokens(self) -> None:
        ready_indices = [i for i, token in enumerate(self._token_pool)
                         if self._is_token_proc_ready(token)]
        if self._token_queue_rand is not None:
            self._token_queue_rand.shuffle(ready_indices)
        ready_indices = ready_indices[:1] 
        for i in ready_indices:
            self._token_queue.append(self._token_pool[i])
        for i in sorted(ready_indices, reverse=True):
            self._token_pool.pop(i)

    def _synch_time(self, target_time: Time) -> None:
        # We maybe jumping over sources -> need triggers with known time
        # + busy wait
        # + jump if nothing is skipped    
        time = self.time
        if target_time <= time:
            return
        step_count_diff = self.interval_to_steps(target_time - time)
        self._step_counter = self._step_counter + step_count_diff

    def _unblock_waiting(self) -> bool:
        if self._waiting_proc_addr is None:
            return True
        compat_token_idx = next((i for i, x in enumerate(self._token_pool)
                                 if x.target.equals(self._waiting_proc_addr)), 
                                -1) 
        if compat_token_idx == -1:
            return False
        unblock_token = self._token_pool.pop(compat_token_idx)
        self._token_queue.append(unblock_token)
        self._synch_time(unblock_token.last_time)
        self._waiting_proc_addr = None
        return True

    def step(self, board_tokens: List[Token]=[]) -> None:
        if len(self._init_calls) > 0:
            self._pop_call_init()
            return
        self._put_tokens(board_tokens)
        if not self._unblock_waiting():
            return
        self._put_tokens(self._generate_tokens())
        self._enqueue_ready_tokens()
        self._pop_call_queue_token()
