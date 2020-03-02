import copy
import multiprocessing
import logging
from random import Random
from abc import ABC, abstractmethod
from operator import attrgetter
from typing import List, Any, Callable, Dict
from .time import TimeInterval, Time, StepCount
from .call import CallArg, Call, CallResult
from .interfaces import (
        Address,  IActor, IProcedure, IProcessorAPI, IProcessor, Token)
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


class ProcedureProfile:
    def __init__(self, expression: str):
        pass

    def get_call_step_count(self, default_step_count: int) -> int:
        return default_step_count


class Processor(IProcessor, IProcessorAPI):
    def __init__(self, config: ProcessorConfig = ProcessorConfig(), 
                 log_pid: bool = False):
        self._name = config.name
        self._step_counter = 0
        self._frequency = config.frequency
        self._has_exited = False
        self._actors = []
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
        if config.main_func:
            config.main_func(self)


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
        return self.steps_to_time(self._step_counter)

    def exit(self, exit_result: CallResult = CallResult()) -> CallResult:
        self._has_exited = True
        return exit_result

    def put_calls(self, calls: List[Call]) -> None:
        time = self.time
        self._put_tokens([Token(call).stamp(time) for call in calls])

    def has_exited(self) -> bool:
        return self._has_exited

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
        self._token_pool = sorted(self._token_pool, 
                                  key=attrgetter('last_time'))

    def get_actor(self, actor_name: str) -> IActor:
        if actor_name is None and len(self._actors) >= 0:
            return self._actors[0]
        return self._name_actor_dict.get(actor_name, None)

    def get_proc(self, address: Address) -> IProcedure:
        return self.get_actor(address.actor).get_procedure(address.proc)
    
    def get_proc_profile(self, address: Address) -> ProcedureProfile:
        #return self.get_actor(address.actor).get_procedure(address.proc)
        pass

    def _process_call_result(self, result: CallResult, 
                             proc_profile: ProcedureProfile = None) -> None:
        step_count = (proc_profile.get_call_step_count(result.step_count)
                      if proc_profile else result.step_count)
        self._step_counter = self._step_counter + max(1, step_count)
        time = self.time
        tokens = [Token(call).stamp(time) for call in result.calls]
        self._put_tokens(tokens)

    def do_call(self, address: Address, token: Token) -> None:
        self._call_stack_proc_addr = copy.copy(address)
        result = self.get_proc(address).call(token.call.arg, token, self.api)
        self._process_call_result(result, self.get_proc_profile(address))

    def _pop_call_queue_token(self, enable_busy_wait=True) -> None:
        if len(self._token_queue) != 0:
            token = self._token_queue.pop()
            self.do_call(token.target, token)
        else:
            if enable_busy_wait:
                logging.info('busy wait')
                self._step_counter = self._step_counter + 1

    def _is_token_ready(self, token: Token) -> bool:
        time_ready = (token.call.call_time is None 
                      or token.call.call_time <= self.time)
        step_ready = (token.call.call_step is None 
                      or token.call.call_step <= self.step_count)
        return time_ready and step_ready
    
    def _get_token_ready_step(self, token: Token) -> StepCount:
        if token.call.call_step is not None:
            return token.call.call_step
        if token.call.call_time is not None:
            return self.time_to_steps(token.call.call_time)
        return 0

    def _enqueue_ready_tokens(self) -> None:
        ready_indices = [i for i, token in enumerate(self._token_pool)
                         if self._is_token_ready(token)]
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
        step_count_diff = self.time_to_steps(target_time - time)
        self._step_counter = self._step_counter + step_count_diff

    def _idle_jump_to_ready_tokens(self) -> None:
        if len(self._token_queue):
            return
        ready_tokens = [token for token in self._token_pool 
                        if self._is_token_ready(token)]
        if len(ready_tokens):
            return
        ready_steps =  [self._get_token_ready_step(token) 
                        for token in self._token_pool]
        if len(ready_steps) == 0:
            return
        jump_step = min(ready_steps)
        if jump_step > self._step_counter:
            logging.info('idle jump {} -> {}'.format(
                                                self._step_counter, jump_step))
            self._step_counter = jump_step

    def has_work(self) -> bool:
        return (len(self._token_pool) + len(self._token_queue) 
                + len(self._board_tokens)) > 0

    def step(self, board_tokens: List[Token]=[]) -> None:
        self._put_tokens(board_tokens)
        self._idle_jump_to_ready_tokens()
        self._enqueue_ready_tokens()
        self._pop_call_queue_token()
