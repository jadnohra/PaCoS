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


class ProcessorSnapshot:
    def __init__(self, *,step_count: StepCount = 0, time: Time = 0.0, 
                 frequency: Time = 0.0, has_exited: bool = False):
        self.step_count = step_count
        self.time = time
        self.frequency = frequency
        self.has_exited = has_exited


class IProcessorAPI(INamed):
    @abstractproperty
    def step_count(self) -> StepCount:
        pass

    @abstractproperty
    def time(self) -> Time:
        pass

    @abstractproperty
    def frequency(self) -> float:
        pass

    @abstractproperty
    def has_exited(self) -> bool:
        pass

    @abstractmethod
    def exit(self) -> None:
        pass

    def snap(self) -> ProcessorSnapshot:
        return ProcessorSnapshot(step_count=self.step_count, time=self.time, 
                                 frequency=self.frequency, 
                                 has_exited=self.has_exited)


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
    def call(self, token: Token, processor: IProcessorAPI) -> CallResult:
        pass


class ITokenSource(ABC):
    @abstractmethod
    def generate(self, processor: IProcessorAPI) -> List[Token]:
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


class IProcessor(IProcessorAPI):
    @abstractmethod
    def step(self, board_tokens: List[Token]=[]) -> StepResult:
        pass

    @abstractproperty
    def api(self) -> IProcessorAPI:
        pass