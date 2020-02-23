import copy
from random import Random
from .discr_evt_engine import DiscreteEventEngine
from .discr_impulse import IDiscreteImpulse
from .interfaces import IMsgRouter, TimeInterval


class ImpulsiveDiscreteEventEngine(DiscreteEventEngine):
    def __init__(self, name: str, impulse_rand: Random = None):
        super().__init__(name)
        self._impulses = []
        self._impulse_rand = impulse_rand
        self._tick = -1
    
    def add_impulse(self, impulse: IDiscreteImpulse) -> None:
        self._impulses.append(impulse)

    def _generate_impulses(self) -> None:
        if self._impulse_rand:
            impulses = copy.copy(self._impulses)
            self._impulse_rand.shuffle(impulses)
        else:
            impulses = reversed(self._impulses)
        for impulse in impulses:
            impulse.generate(self)

    def step(self, router: IMsgRouter) -> TimeInterval:
        if len(self._msgs) == 0:
            self._generate_impulses()
            self._tick = self._tick + 1
            if len(self._msgs) == 0:
                return 0
        return self._pop_msg(router)
