import copy
import multiprocessing
import logging
from random import Random
from abc import ABC, abstractmethod
from typing import List, Any, Callable, Dict
from .time import TimeInterval, Time, StepCount
from .interfaces import (
    Address, ITokenSource, IActor, IProcedure, IProcessorAPI, ProcState, 
    CallResult, StepResult, IProcessor, Token)
from .ipc import SynchStep, SynchStepResult, SynchExit


class ProcessorConfig:
    def __init__(self, *,
                main: Callable[['Processor'], None] = None,
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
    
    def send_step(self, paused_time: TimeInterval, tokens: List[Token]) -> None:
        self._conn.send(SynchStep(paused_time, tokens)) 
        
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
        self._paused_time = 0.0
        self._flag_exit = False
        self._has_exited = False
        self._actors = []
        self._sources = []
        self._name_actor_dict = {}
        self._token_pool = []
        self._token_queue = []
        self._remote_tokens = []
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
                logging.info('stepping')
                step_result = processor.step(synch_msg.tokens, 
                                             synch_msg.paused_time)
                conn.send(SynchStepResult(step_result, processor.api.snap()))
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
        return self._paused_time + (self._step_counter / self._frequency)

    def exit(self) -> None:
        self._flag_exit = True

    @property
    def has_exited(self) -> bool:
        return self._has_exited

    def add_actor(self, actor: IActor) -> None:
        self._actors.append(actor)
        self._name_actor_dict[actor.name] = actor

    def _is_local_address(self, address: Address):
        return address.processor is None

    def _put_tokens(self, tokens: List[Token]) -> None:
        for token in tokens:
            if self._is_local_address(token.target):
                self._token_pool.append(token)
            else:
                self._remote_tokens.append(token)

    def add_source(self, source: ITokenSource) -> None:
        self._sources.append(source)

    def get_actor(self, actor_name: str) -> IActor:
        if actor_name is None and len(self._actors) >= 0:
            return self._actors[0]
        return self._name_actor_dict.get(actor_name, None)

    def get_token_proc(self, token: Token) -> IProcedure:
        actor_name = (token.target.actor if token.target.actor 
                      else token.source.actor)
        return self.get_actor(actor_name).get_procedure(token.target.proc)

    def _generate_tokens(self) -> List[Token]:
        if self._token_source_rand:
            sources = copy.copy(self._sources)
            self._token_source_rand.shuffle(sources)
        else:
            sources = reversed(self._sources)
        return sum([source.generate(self) for source in sources], [])

    def _pop_queue_token(self) -> CallResult:
        if len(self._token_queue) == 0:
            return 0
        token = self._token_queue.pop()
        return self.get_token_proc(token).call(token, self.api)

    def _is_token_proc_ready(self, token: Token):
        return self.get_token_proc(token).state != ProcState.CLOSED

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

    def step(self, incoming_tokens: List[Token]=[], 
             paused_time: TimeInterval=0.0) -> StepResult:
        self._put_tokens(incoming_tokens)
        self._put_tokens(self._generate_tokens())
        self._enqueue_ready_tokens()
        pre_step_count = self._step_counter
        if len(self._token_queue) > 0:
            proc_result = self._pop_queue_token()
            self._step_counter = self._step_counter + proc_result.step_count
            self._put_tokens(proc_result.calls)
            self._enqueue_ready_tokens()
        if self._flag_exit:
            self._has_exited = True
        tokens, self._remote_tokens = self._remote_tokens, []
        return StepResult(self._step_counter - pre_step_count, tokens)
