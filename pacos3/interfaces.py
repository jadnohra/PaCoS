from abc import ABC, abstractmethod, abstractproperty
from enum import Enum, auto
from typing import List, Tuple, Any
from collections import namedtuple
from .address import Address
from .addressable import Addressable
from .proc_call import ProcCall
from .token import Token


Time = int
TimeInterval = int


class IClock(ABC):
    @abstractmethod
    def time(self) -> Time:
        pass


class ICallSource(ABC):
    @abstractmethod
    def generate(self, clock: IClock) -> List[ProcCall]:
        pass


class ProcResult:
    def __init__(self, interval: TimeInterval, calls: List[ProcCall]):
        self.interval = interval
        self.calls = calls


class ProcState(Enum):
    CLOSED = auto()
    OPEN = auto()
    WAITING = auto()


class IProcedure(Addressable):
    @abstractproperty
    def state(self) -> ProcState:
        pass

    @abstractmethod
    def execute(self, call: ProcCall) -> ProcResult:
        pass


class IActor(Addressable):
    @abstractproperty
    def procs(self) -> List[IProcedure]:
        pass

    @abstractmethod
    def get_proc(self, name: str) -> IProcedure:
        pass


class StepResult:
    def __init__(self, interval: TimeInterval, tokens: List[Token]):
        self.interval = interval
        self.tokens = tokens


class IProcessor(Addressable):
    @abstractmethod
    def step(self, clock: IClock, tokens: List[Token]) -> StepResult:
        pass