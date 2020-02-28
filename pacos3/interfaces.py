from abc import ABC, abstractmethod, abstractproperty
from enum import Enum, auto
from typing import List, Tuple, Any
from collections import namedtuple
from .address import Address
from .token import Token
from .time import Time, TimeInterval


class IClock(ABC):
    @abstractmethod
    def time(self) -> Time:
        pass


class ITokenSource(ABC):
    @abstractmethod
    def generate(self, time: Time) -> List[Token]:
        pass


class CallResult:
    def __init__(self, interval: TimeInterval = 0, calls: List[Token] = []):
        self.interval = interval
        self.calls = calls


class ProcState(Enum):
    CLOSED = auto()
    OPEN = auto()


class INamed(ABC):
    @abstractproperty
    def name(self) -> str:
        pass


class IProcedure(INamed):
    @abstractproperty
    def state(self) -> ProcState:
        pass

    @abstractmethod
    def call(self, token: Token, time: Time) -> CallResult:
        pass


class IActor(INamed):
    @abstractproperty
    def procedures(self) -> List[IProcedure]:
        pass

    @abstractmethod
    def get_procedure(self, name: str) -> IProcedure:
        pass


class StepResult:
    def __init__(self, interval: TimeInterval, tokens: List[Token]):
        self.interval = interval
        self.tokens = tokens


class IProcessor(INamed):
    @abstractmethod
    def step(self, time: Time, tokens: List[Token]) -> StepResult:
        pass