from enum import Enum, auto
from typing import List


class PinState(Enum):
    CLOSED = auto()
    OPEN = auto()
    WAITING = auto()


class Pin:
    def __init__(self):
        pass

    @property
    def name(self) -> str:
        return None

    @property
    def state(self) -> PinState:
        return None


Address = str
Time = int
TimeInterval = int

class Message:
    def __init__(self):
        pass


    @property
    def target(self) -> Address:
        return None

    @property
    def source(self) -> Address:
        return None


    @property
    def emission_time(self) -> Time:
        return None


class Actor:
    def __init__(self):
        pass

    @property
    def name(self) -> str:
        return None

    @property
    def pins(self) -> List[Pin]:
        return []


class Impulse:
    
    def generate(self) -> List[Message]:
        return []


class DiscreteEventEngine:

    def step(self) -> TimeInterval:
        return 0

    def put(self, msg: Message):
        pass


class ImpulseEngine:

    def step(self) -> TimeInterval:
        return 0

    def put(self, msg: Message):
        pass


class ParallelContext:

    def step(self) -> TimeInterval:
        return 0


print("hello")