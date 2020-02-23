from abc import ABC, abstractmethod, abstractproperty
from enum import Enum, auto
from collections import namedtuple
from typing import List, Tuple, Callable, Dict
from .address import Address
from .addressable import Addressable


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


class IClock(ABC):
    @abstractmethod
    def time(self) -> Time:
        pass


class IMsgRouter(ABC):
    @abstractmethod
    def route(self, msg: IMessage) -> None:
        pass

    @abstractproperty
    def clock(self) -> IClock:
        pass


class PinState(Enum):
    CLOSED = auto()
    OPEN = auto()
    WAITING = auto()


class IPin(ABC, Addressable):
    def __init__(self, name: str):
        Addressable.__init__(self, name)

    @abstractproperty
    def state(self) -> PinState:
        pass

    @abstractmethod
    def process(self, msg: IMessage, router: IMsgRouter) -> Time:
        pass


class IActor(ABC, Addressable):
    def __init__(self, name: str):
        Addressable.__init__(self, name)

    @abstractproperty
    def pins(self) -> List[IPin]:
        pass

    @abstractmethod
    def get_pin(self, pin_name: str) -> IPin:
        pass


class IEngine(ABC, Addressable):
    def __init__(self, name: str):
        Addressable.__init__(self, name)

    @abstractmethod
    def step(self, router: IMsgRouter) -> TimeInterval:
        pass

    @abstractmethod
    def put_msg(self, msg: IMessage) -> None:
        pass


class ITopology(ABC):
    @abstractmethod
    def step(self) -> TimeInterval:
        pass

    @abstractmethod
    def get_engine(self, engine_name: str) -> IEngine:
        pass

    @property
    def engines(self) -> List[IEngine]:
        pass