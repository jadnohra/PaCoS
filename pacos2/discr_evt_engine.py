from random import Random
from abc import ABC, abstractmethod
from .interfaces import (
    Address, TimeInterval, IMessage, Stamp, IClock, IMsgRouter, Addressable, 
    IActor, IPin, IEngine)
from .discr_policies import IMsgReadyPolicy


class DiscreteEventEngine(IEngine):
    def __init__(self, name: str, msg_ready_policy: IMsgReadyPolicy,
                 msg_queue_rand: Random = None):
        Addressable.__init__(self, name)
        self._actors = []
        self._name_actor_dict = {}
        self._msg_pool = []
        self._msg_queue = []
        self._msg_ready_policy = msg_ready_policy
        self._msg_queue_rand = msg_queue_rand
    
    def add_actor(self, actor: IActor) -> None:
        actor.init_address(self)
        self._actors.append(actor)
        
    def put_msg(self, msg: IMessage) -> None:
        self._msg_pool.append(msg)

    def resolve_pin(self, address: Address) -> IPin:
        actor = self._name_actor_dict[address[-2]]
        pin = actor.pin(address[-1])
        return pin

    def _pop_queue_msg(self, router: IMsgRouter) -> TimeInterval:
        if len(self._msg_queue) == 0:
            return 0
        msg = self._msg_queue.pop()
        msg.stamp(Stamp(msg.target, router.clock.time))
        return self.resolve_pin(msg.target).process(msg, router)

    def _enqueue_ready_msgs(self, clock: IClock) -> None:
        ready_indices = [i for i,msg in enumerate(self._msg_pool)
                         if self._msg_ready_policy.check(msg, self, clock)]
        if self._msg_queue_rand is not None:
            self._msg_queue_rand.shuffle(ready_indices)
        for i in ready_indices:
            self._msg_queue.append(self._msg_pool.pop(i))

    def step(self, router: IMsgRouter) -> TimeInterval:
        self._enqueue_ready_msgs(router.clock)
        return self._pop_queue_msg(router)
