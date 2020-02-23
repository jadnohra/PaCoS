from enum import Enum, auto
from collections import namedtuple
from typing import List, Tuple, Callable, Dict


Address = List[str]
Time = int
TimeInterval = int

Stamp = namedtuple('Stamp', 'address time')

class IMessage:
    @property
    def target(self) -> Address:
        return None

    def forward(self, new_target: Address) -> None:
        pass

    @property
    def source(self) -> Address:
        return None

    def stamp(self, stamp: Stamp) -> None:
        pass

    @property
    def emission_time(self) -> Time:
        return None

    @property
    def wire_time(self) -> TimeInterval:
        return None


class PinState(Enum):
    CLOSED = auto()
    OPEN = auto()
    WAITING = auto()


class IPin:
    @property
    def name(self) -> str:
        return None

    @property
    def state(self) -> PinState:
        return None

    @property
    def process(self, msg: IMessage) -> Time:
        return 0


class IActor:
    def __init__(self):
        pass

    @property
    def name(self) -> str:
        return None

    @property
    def pins(self) -> List[IPin]:
        return []


class IImpulse:
    def generate(self) -> List[IMessage]:
        return []


class IMsgRouter:
    def route(self, msg: IMessage) -> None:
        pass


class IEngine:
    def step(self, router: IMsgRouter) -> TimeInterval:
        return 0

    def put(self, msg: IMessage) -> None:
        pass


class DiscreteEventEngine(IEngine):
    def step(self, router: IMsgRouter) -> TimeInterval:
        return 0

    def put(self, msg: IMessage) -> None:
        pass


class ImpulseEngine(IEngine):
    def step(self, router: IMsgRouter) -> TimeInterval:
        return 0

    def put(self, msg: IMessage) -> None:
        pass


class IContext:
    def step(self) -> TimeInterval:
        return None
