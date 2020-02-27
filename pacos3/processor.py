import copy
from random import Random
from abc import ABC, abstractmethod
from typing import List
from .interfaces import (
    Address, TimeInterval, ITokenSource, IClock,  Addressable, IActor, 
    IProcedure, ProcState, CallResult, StepResult, IProcessor, Token)


class Processor(IProcessor):
    def __init__(self, respect_proc_readiness: True, name: str = None,
                 call_queue_rand: Random = None, 
                 call_source_rand: Random = None):
        self._name = name
        self._actors = []
        self._token_sources = []
        self._name_actor_dict = {}
        self._token_pool = []
        self._token_queue = []
        self._remote_tokens = []
        self._respect_proc_readiness = respect_proc_readiness
        self._token_queue_rand = call_queue_rand
        self._token_source_rand = call_source_rand

    def name(self) -> str:
        return self._name
    
    def add_actor(self, actor: IActor) -> None:
        actor.init_address(self)
        self._actors.append(actor)
        self._name_actor_dict[actor.name] = actor

    def _is_local_address(self, address: Address):
        return address.board is None and address.processor is None

    def _put_tokens(self, calls: List[Token], clock: IClock) -> None:
        for token in token:
            if self._is_local_address(token.target):
                self._token_pool.append(token)
            else:
                self._remote_tokens.append(token)

    def add_token_source(self, source: ICallSource) -> None:
        self._token_sources.append(source)

    def get_actor(self, actor_name: str) -> IActor:
        if actor_name is None and len(self._actors) >= 0:
            return self._actors[0]
        return self._name_actor_dict.get(actor_name, None)

    def get_token_proc(self, call: ProcCall) -> IProcedure:
        actor_name = (call.target.actor if call.target.actor 
                      else call.source.actor)
        return self.get_actor(actor_name).get_procedure(call.target.proc)

    def _generate_tokens(self, clock: IClock) -> List[ProcCall]:
        if self._token_source_rand:
            sources = copy.copy(self._token_sources)
            self._token_source_rand.shuffle(sources)
        else:
            sources = reversed(self._token_sources)
        return sum([source.generate(clock) for source in sources], [])

    def _pop_queue_token(self) -> CallResult:
        if len(self._token_queue) == 0:
            return 0
        call = self._token_queue.pop()
        return self.get_token_proc(call).execute(call)

    def _is_proc_ready(self, proc: IProcedure):
        return (not self._respect_proc_readiness 
                or proc.state != ProcState.CLOSED)

    def _enqueue_ready_tokens(self, clock: IClock) -> None:
        ready_indices = [i for i, proc in enumerate(self._token_pool)
                         if self._is_proc_ready(proc)]
        if self._token_queue_rand is not None:
            self._token_queue_rand.shuffle(ready_indices)
        # max one message, since the pin states may change after processing it
        ready_indices = ready_indices[:1] 
        for i in ready_indices:
            self._token_queue.append(self._token_pool[i])
        for i in sorted(ready_indices, reverse=True):
            self._token_pool.pop(i)

    def step(self, clock: IClock, tokens: List[Token]) -> StepResult:
        self._put_tokens([x.call for x in tokens], clock)
        self._put_tokens(self._generate_tokens(clock), clock)
        self._enqueue_ready_tokens(clock)
        interval = 0
        while len(self._token_queue) > 0:
            proc_result = self._pop_queue_token()
            interval = interval + proc_result.interval
            self._put_tokens(proc_result.calls, clock)
            self._enqueue_ready_tokens(clock)
        tokens, self._remote_tokens = self._remote_tokens, []
        return StepResult(interval, tokens)
