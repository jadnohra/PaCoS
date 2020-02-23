from abc import ABC, abstractmethod
from .discr_evt_engine import DiscreteEventEngine


class IDiscreteImpulse(ABC):
    @abstractmethod
    def generate(self, engine: DiscreteEventEngine) -> None:
        pass