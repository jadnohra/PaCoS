from abc import ABC, abstractmethod
from .interfaces import TimeInterval, IClock
from .discr_evt_engine import DiscreteEventEngine


class IDiscreteImpulse(ABC):
    @abstractmethod
    def generate(self, engine: DiscreteEventEngine, clock: IClock
                 ) -> TimeInterval:
        pass