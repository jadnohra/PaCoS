from abc import ABC, abstractmethod, abstractproperty
from enum import Enum, auto
from collections import namedtuple
from typing import List, Tuple, Callable, Dict
from .addressable import Addressable


Address = List[str]
Time = int
TimeInterval = int

Stamp = namedtuple('Stamp', 'address time')

class IMessage(ABC):
    @abstractproperty
    def target(self) -> Address:
        return None

    @abstractmethod
    def forward(self, new_target: Address) -> None:
        pass

    @abstractproperty
    def source(self) -> Address:
        return None

    @abstractmethod
    def stamp(self, stamp: Stamp) -> None:
        pass

    @abstractproperty
    def emission_time(self) -> Time:
        return None

    @abstractproperty
    def wire_time(self) -> TimeInterval:
        return None


class IMsgRouter(ABC):
    @abstractmethod
    def route(self, msg: IMessage) -> None:
        pass

    @abstractproperty
    def time(self) -> Time:
        pass


class PinState(Enum):
    CLOSED = auto()
    OPEN = auto()
    WAITING = auto()


class IPin(ABC, Addressable):
    @abstractproperty
    def name(self) -> str:
        pass

    @abstractproperty
    def state(self) -> PinState:
        pass

    @abstractmethod
    def process(self, msg: IMessage, msg_router: IMsgRouter) -> Time:
        pass


class IActor(ABC, Addressable):
    def __init__(self):
        pass

    @abstractproperty
    def name(self) -> str:
        pass

    @abstractproperty
    def pins(self) -> List[IPin]:
        pass


class IImpulse(ABC, Addressable):
    @abstractmethod
    def generate(self, router: IMsgRouter) -> None:
        pass


class IEngine(ABC, Addressable):
    @abstractmethod
    def step(self, router: IMsgRouter) -> TimeInterval:
        pass

    @abstractmethod
    def put(self, msg: IMessage) -> None:
        pass


class DiscreteEventEngine(IEngine):
    def step(self, router: IMsgRouter) -> TimeInterval:
        pass

    def put(self, msg: IMessage) -> None:
        pass


class ImpulseEngine(IEngine):
    def step(self, router: IMsgRouter) -> TimeInterval:
        pass

    def put(self, msg: IMessage) -> None:
        pass


class IContext(ABC):
    @abstractmethod
    def step(self) -> TimeInterval:
        pass
