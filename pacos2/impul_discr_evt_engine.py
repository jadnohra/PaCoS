import copy
from random import Random
from typing import List
from .discr_evt_engine import DiscreteEventEngine, IEngine, IMessage
from .discr_impulse import IDiscreteImpulse
from .interfaces import IClock, IMsgRouter, TimeInterval


class ImpulsiveDiscreteEventEngine(IEngine):
    def __init__(self, discr_engine: DiscreteEventEngine, 
                impulse_rand: Random = None):
        self._discr_engine = discr_engine
        self._impulses = []
        self._impulse_rand = impulse_rand
    
    @property
    def discr_engine(self) -> DiscreteEventEngine:
        return self._discr_engine

    def put_msg(self, msg: IMessage) -> None:
        return self._discr_engine.put_msg(msg)

    def add_impulse(self, impulse: IDiscreteImpulse) -> None:
        self._impulses.append(impulse)

    def _generate_impulses(self, clock: IClock) -> List[TimeInterval]:
        if self._impulse_rand:
            impulses = copy.copy(self._impulses)
            self._impulse_rand.shuffle(impulses)
        else:
            impulses = reversed(self._impulses)
        intervals = [impulse.generate(self._discr_engine, clock) 
                     for impulse in impulses]
        return intervals

    def step(self, router: IMsgRouter) -> TimeInterval:
        discr_step = self._discr_engine.step(router)
        if discr_step != 0:
            return discr_step
        impulse_intervals = self._generate_impulses(router.clock)
        discr_interval = self._discr_engine.step(router)
        return min(impulse_intervals + [discr_interval])
