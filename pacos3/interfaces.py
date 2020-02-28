from abc import ABC, abstractmethod, abstractproperty
from enum import Enum, auto
from typing import List, Tuple, Any
from collections import namedtuple
from .address import Address
from .token import Token
from .time import Time, TimeInterval, StepCount


class INamed(ABC):
    @abstractproperty
    def name(self) -> str:
        pass


class IProcessorState(INamed):
    @abstractproperty
    def step_count(self) -> StepCount:
        pass

    @abstractproperty
    def frequency(self) -> float:
        pass

    @abstractmethod
    def get_time(self, including_paused=False) -> TimeInterval:
        pass


class CallResult:
    def __init__(self, step_count: StepCount = 0, calls: List[Token] = []):
        self.step_count = step_count
        self.calls = calls


class ProcState(Enum):
    CLOSED = auto()
    OPEN = auto()


class IProcedure(INamed):
    @abstractproperty
    def state(self) -> ProcState:
        pass

    @abstractmethod
    def call(self, token: Token, processor: IProcessorState) -> CallResult:
        pass


class ITokenSource(ABC):
    @abstractmethod
    def generate(self, processor: IProcessorState) -> List[Token]:
        pass


class IActor(INamed):
    @abstractproperty
    def procedures(self) -> List[IProcedure]:
        pass

    @abstractmethod
    def get_procedure(self, name: str) -> IProcedure:
        pass


class StepResult:
    def __init__(self, step_count: StepCount, tokens: List[Token]):
        self.step_count = step_count
        self.tokens = tokens


class IProcessor:
    @abstractmethod
    def step(self, incoming_tokens: List[Token]=[], 
             paused_time: TimeInterval=0.0) -> StepResult:
        pass

    @abstractmethod
    def state(self) -> IProcessorState:
        pass