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


class ProcessorStateSnapshot:
    def __init__(self, step_count, time, time_incl_paused, frequency):
        self.step_count = step_count
        self.time = time
        self.time_incl_paused = time_incl_paused
        self.frequency = frequency


class IProcessorState(INamed):
    @abstractproperty
    def step_count(self) -> StepCount:
        pass

    @abstractmethod
    def get_time(self, include_paused=False) -> Time:
        pass

    @abstractproperty
    def frequency(self) -> float:
        pass

    @property
    def stamp_time(self) -> Time:
        return self.get_time(True)

    def snap(self) -> ProcessorStateSnapshot:
        return ProcessorStateSnapshot(self.step_count, self.get_time(),
                                      self.get_time(True), self.frequency)


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