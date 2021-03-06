from random import Random
from abc import ABC, abstractmethod
from .interfaces import (
    Address, TimeInterval, IMessage, Stamp, IClock, IMsgRouter, Addressable, 
    IActor, IPin, IEngine)
from .discr_policies import IMsgReadyPolicy


class DiscreteEventEngine(IEngine):
    def __init__(self, msg_ready_policy: IMsgReadyPolicy, name: str = None,
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
        self._name_actor_dict[actor.name] = actor
        
    def put_msg(self, msg: IMessage) -> None:
        self._msg_pool.append(msg)

    def get_actor(self, actor_name: str) -> IActor:
        if actor_name is None and len(self._actors) >= 0:
            return self._actors[0]
        return self._name_actor_dict.get(actor_name, None)

    def get_msg_pin(self, msg: IMessage) -> IPin:
        actor_name = msg.target.actor if msg.target.actor else msg.source.actor
        return self.get_actor(actor_name).get_pin(msg.target.pin)

    def _pop_queue_msg(self, router: IMsgRouter) -> TimeInterval:
        if len(self._msg_queue) == 0:
            return 0
        msg = self._msg_queue.pop()
        msg.stamp(Stamp(msg.target, router.clock.time))
        return self.get_msg_pin(msg).process(msg, router)

    def _enqueue_ready_msgs(self, clock: IClock) -> None:
        ready_indices = [i for i,msg in enumerate(self._msg_pool)
                         if self._msg_ready_policy.check(msg, self, clock)]
        if self._msg_queue_rand is not None:
            self._msg_queue_rand.shuffle(ready_indices)
        # max one message, since the pin states may change after processing it
        ready_indices = ready_indices[:1] 
        for i in ready_indices:
            self._msg_queue.append(self._msg_pool[i])
        for i in sorted(ready_indices, reverse=True):
            self._msg_pool.pop(i)

    def step(self, router: IMsgRouter) -> TimeInterval:
        self._enqueue_ready_msgs(router.clock)
        interval = 0
        while len(self._msg_queue) > 0:
            interval = interval + self._pop_queue_msg(router)
            self._enqueue_ready_msgs(router.clock)
        return interval
