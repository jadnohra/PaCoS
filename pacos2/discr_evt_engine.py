from abc import ABC, abstractmethod
from .interfaces import (
    TimeInterval, IMessage, Stamp, IMsgRouter, Addressable, IActor, IEngine)


class IDiscreteImpulse(ABC):
    @abstractmethod
    def generate(self, engine: "DiscreteEventEngine") -> None:
        pass


class DiscreteEventEngine(IEngine):
    def __init__(self, name: str):
        Addressable.__init__(self, name)
        self._actors = []
        self._name_actor_dict = {}
        self._msgs = []
    
    def add_actor(self, actor: IActor) -> None:
        actor.init_address(self)
        self._actors.append(actor)
        
    def put_msg(self, msg: IMessage) -> None:
        self._msgs.append(msg)

    def _pop_msg(self, router: IMsgRouter) -> TimeInterval:
        msg = self._msgs.pop()
        msg.stamp(Stamp(msg.target, router.time))
        actor = self._name_actor_dict[msg.target[-2]]
        pin = actor.pin(msg.target[-1])
        return pin.process(msg, router)

    def step(self, router: IMsgRouter) -> TimeInterval:
        if len(self._msgs) == 0:
            return 0
        self._pop_msg(router)
