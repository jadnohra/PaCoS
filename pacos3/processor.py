import copy
from random import Random
from abc import ABC, abstractmethod
from typing import List
from .interfaces import (
    Address, TimeInterval, IProcCall, ICallSource, Stamp, IClock, IRouter, 
    Addressable, IActor, IProcedure, ProcState, IProcessor)


class Processor(IProcessor):
    def __init__(self, respect_proc_readiness: True, name: str = None,
                 call_queue_rand: Random = None, 
                 call_source_rand: Random = None):
        Addressable.__init__(self, name)
        self._actors = []
        self._call_sources = []
        self._name_actor_dict = {}
        self._call_pool = []
        self._call_queue = []
        self._respect_proc_readiness = respect_proc_readiness
        self._call_queue_rand = call_queue_rand
        self._call_source_rand = call_source_rand
    
    def add_actor(self, actor: IActor) -> None:
        actor.init_address(self)
        self._actors.append(actor)
        self._name_actor_dict[actor.name] = actor
        
    def put_call(self, call: IProcCall) -> None:
        self._call_pool.append(call)

    def add_call_source(self, source: ICallSource) -> None:
        self._call_sources.append(source)

    def get_actor(self, actor_name: str) -> IActor:
        if actor_name is None and len(self._actors) >= 0:
            return self._actors[0]
        return self._name_actor_dict.get(actor_name, None)

    def get_call_proc(self, call: IProcCall) -> IProcedure:
        actor_name = (call.target.actor if call.target.actor 
                      else call.source.actor)
        return self.get_actor(actor_name).get_pin(call.target.proc)

    def _generate_calls(self, clock: IClock) -> List[IProcCall]:
        if self._call_source_rand:
            sources = copy.copy(self._call_sources)
            self._call_source_rand.shuffle(sources)
        else:
            sources = reversed(self._call_sources)
        return sum([source.generate(clock) for source in sources], [])

    def _pop_queue_call(self, router: IRouter) -> TimeInterval:
        if len(self._call_queue) == 0:
            return 0
        call = self._call_queue.pop()
        call.stamp(Stamp(call.target, router.clock.time))
        return self.get_call_proc(call).execute(call, router)

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

    def step(self, router: IRouter) -> TimeInterval:
        for call in self._generate_calls(router.clock):
            self.put_call(call)
        self._enqueue_ready_calls(router.clock)
        interval = 0
        while len(self._call_queue) > 0:
            interval = interval + self._pop_queue_call(router)
            self._enqueue_ready_calls(router.clock)
        return interval
