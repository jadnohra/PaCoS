import copy
from random import Random
from abc import ABC, abstractmethod
from typing import List
from .interfaces import (
    Address, TimeInterval, ITokenSource, IActor, IProcedure, Time,
    ProcState, CallResult, CallMode, StepResult, IProcessor, Token)


class Processor(IProcessor):
    def __init__(self, name: str = None,
                 call_queue_rand: Random = None, 
                 call_source_rand: Random = None):
        self._name = name
        self._actors = []
        self._sources = []
        self._name_actor_dict = {}
        self._token_pool = []
        self._token_queue = []
        self._remote_tokens = []
        self._token_queue_rand = call_queue_rand
        self._token_source_rand = call_source_rand

    def name(self) -> str:
        return self._name
    
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

    def _generate_tokens(self, time: Time) -> List[Token]:
        if self._token_source_rand:
            sources = copy.copy(self._sources)
            self._token_source_rand.shuffle(sources)
        else:
            sources = reversed(self._sources)
        return sum([source.generate(time) for source in sources], [])

    def _pop_queue_token(self, time: Time, call_mode: CallMode) -> CallResult:
        if len(self._token_queue) == 0:
            return 0
        token = self._token_queue.pop()
        return self.get_token_proc(token).call(token, time, call_mode)

    def _is_token_proc_ready(self, token: Token, call_mode: CallMode):
        return (not call_mode.use_proc_state 
                or self.get_token_proc(token).state != ProcState.CLOSED)

    def _enqueue_ready_tokens(self, call_mode: CallMode) -> None:
        ready_indices = [i for i, token in enumerate(self._token_pool)
                         if self._is_token_proc_ready(token, call_mode)]
        if self._token_queue_rand is not None:
            self._token_queue_rand.shuffle(ready_indices)
        # max one message, since the pin states may change after processing it
        ready_indices = ready_indices[:1] 
        for i in ready_indices:
            self._token_queue.append(self._token_pool[i])
        for i in sorted(ready_indices, reverse=True):
            self._token_pool.pop(i)

    def step(self, time: Time, tokens: List[Token], call_mode: CallMode
             ) -> StepResult:
        self._put_tokens(tokens)
        self._put_tokens(self._generate_tokens(time))
        self._enqueue_ready_tokens(call_mode)
        interval = 0
        if len(self._token_queue) > 0:
            proc_result = self._pop_queue_token(time, call_mode)
            interval = interval + proc_result.interval
            self._put_tokens(proc_result.calls)
            self._enqueue_ready_tokens(call_mode)
        tokens, self._remote_tokens = self._remote_tokens, []
        return StepResult(interval, tokens)
