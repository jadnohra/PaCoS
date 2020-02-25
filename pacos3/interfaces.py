from abc import ABC, abstractmethod, abstractproperty
from enum import Enum, auto
from typing import List, Tuple, Any
from .address import Address
from .addressable import Addressable
from .proc_call import ProcCall

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


class IRouter(ABC):
    @abstractmethod
    def route(self, call: ProcCall) -> None:
        pass

    @abstractproperty
    def clock(self) -> IClock:
        pass


class ProcState(Enum):
    CLOSED = auto()
    OPEN = auto()
    WAITING = auto()

class IProcedure(Addressable):
    @abstractproperty
    def state(self) -> ProcState:
        pass

    # TBC, addressing, how of the resulting proc_call
    # how does a router work? router stack? buffer up (to master)?
    @abstractmethod
    def execute(self, call: ProcCall, clock: IClock
                ) -> Tuple[TimeInterval, List[ProcCall]]:
        pass


class IActor(Addressable):
    @abstractproperty
    def procs(self) -> List[IProcedure]:
        pass

    @abstractmethod
    def get_proc(self, name: str) -> IProcedure:
        pass


class IProcessor(Addressable):
    @abstractmethod
    def step(self, router: IRouter) -> TimeInterval:
        pass

    @abstractmethod
    def put_call(self, call: ProcCall) -> None:
        pass


class IMultiProcessor(IProcessor):
    @abstractmethod
    def step(self, router: IRouter) -> TimeInterval:
        pass

    @abstractmethod
    def put_call(self, call: ProcCall) -> None:
        pass

    @abstractmethod
    def get_processor(self, name: str) -> IProcessor:
        pass

    @property
    def processors(self) -> List[IProcessor]:
        pass