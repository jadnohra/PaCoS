import copy
from random import Random
from abc import ABC, abstractmethod
from typing import List
from .interfaces import (
    Address, TimeInterval, ICallSource, IClock,  Addressable, IActor, 
    IProcedure, ProcState, ProcCall, ProcResult, StepResult, IProcessor, Token)


class Processor(IProcessor):
    def __init__(self, respect_proc_readiness: True, name: str = None,
                 call_queue_rand: Random = None, 
                 call_source_rand: Random = None):
        self._name = name
        self._actors = []
        self._call_sources = []
        self._name_actor_dict = {}
        self._call_pool = []
        self._call_queue = []
        self._remote_tokens = []
        self._respect_proc_readiness = respect_proc_readiness
        self._call_queue_rand = call_queue_rand
        self._call_source_rand = call_source_rand

    def name(self) -> str:
        return self._name
    
    def add_actor(self, actor: IActor) -> None:
        actor.init_address(self)
        self._actors.append(actor)
        self._name_actor_dict[actor.name] = actor

    def _is_local_address(self, address: Address):
        return address.board is None and address.processor is None

    def _put_calls(self, calls: List[ProcCall], clock: IClock) -> None:
        for call in calls:
            if self._is_local_address(call.target):
                self._call_pool.append(call)
            else:
                self._remote_tokens.append(Token(call, clock.time))

    def add_call_source(self, source: ICallSource) -> None:
        self._call_sources.append(source)

    def get_actor(self, actor_name: str) -> IActor:
        if actor_name is None and len(self._actors) >= 0:
            return self._actors[0]
        return self._name_actor_dict.get(actor_name, None)

    def get_call_proc(self, call: ProcCall) -> IProcedure:
        actor_name = (call.target.actor if call.target.actor 
                      else call.source.actor)
        return self.get_actor(actor_name).get_procedure(call.target.proc)

    def _generate_calls(self, clock: IClock) -> List[ProcCall]:
        if self._call_source_rand:
            sources = copy.copy(self._call_sources)
            self._call_source_rand.shuffle(sources)
        else:
            sources = reversed(self._call_sources)
        return sum([source.generate(clock) for source in sources], [])

    def _pop_queue_call(self) -> ProcResult:
        if len(self._call_queue) == 0:
            return 0
        call = self._call_queue.pop()
        return self.get_call_proc(call).execute(call)

    def _is_proc_ready(self, proc: IProcedure):
        return (not self._respect_proc_readiness 
                or proc.state != ProcState.CLOSED)

    def _enqueue_ready_calls(self, clock: IClock) -> None:
        ready_indices = [i for i, proc in enumerate(self._call_pool)
                         if self._is_proc_ready(proc)]
        if self._call_queue_rand is not None:
            self._call_queue_rand.shuffle(ready_indices)
        # max one message, since the pin states may change after processing it
        ready_indices = ready_indices[:1] 
        for i in ready_indices:
            self._call_queue.append(self._call_pool[i])
        for i in sorted(ready_indices, reverse=True):
            self._call_pool.pop(i)

    def step(self, clock: IClock, tokens: List[Token]) -> StepResult:
        self._put_calls([x.call for x in tokens], clock)
        self._put_calls(self._generate_calls(clock), clock)
        self._enqueue_ready_calls(clock)
        interval = 0
        while len(self._call_queue) > 0:
            proc_result = self._pop_queue_call()
            interval = interval + proc_result.interval
            self._put_calls(proc_result.calls, clock)
            self._enqueue_ready_calls(clock)
        tokens, self._remote_tokens = self._remote_tokens, []
        return StepResult(interval, tokens)
