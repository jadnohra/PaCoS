from abc import ABC, abstractmethod, abstractproperty
from enum import Enum, auto
from typing import List, Tuple, Any
from collections import namedtuple
from .address import Address
from .token import Token
from .time import Time, TimeInterval, StepCount
from .call import CallArg, Call, CallResult


class INamed(ABC):
    @abstractproperty
    def name(self) -> str:
        pass


class ProcessorSnapshot:
    def __init__(self, *,step_count: StepCount = 0, time: Time = 0.0, 
                 frequency: Time = 0.0, has_exited: bool = False,
                 is_waiting = False):
        self.step_count = step_count
        self.time = time
        self.frequency = frequency
        self.is_waiting = is_waiting
        self.has_exited = has_exited


class IProcessorAPI(INamed):
    @abstractproperty
    def time(self) -> Time:
        pass

    @abstractmethod
    def wait(self, wait_on_address: Address, 
             partial_result: CallResult = CallResult()) -> CallResult:
        pass

    @abstractmethod
    def exit(self, exit_result: CallResult = CallResult()) -> CallResult:
        pass

    @abstractmethod
    def put_calls(self, calls: List[Call]) -> None:
        pass

    @abstractproperty
    def step_count(self) -> StepCount:
        pass

    @abstractproperty
    def frequency(self) -> float:
        pass

    def steps_to_time(self, step_count: StepCount) -> Time:
        return step_count / self.frequency

    def time_to_steps(self, time: Time) -> StepCount:
        return StepCount(time * self.frequency)


IProcAPI = IProcessorAPI


class IProcedure(INamed):
    '''
    @abstractmethod
    def call_control(self, processor: IProcessorAPI) -> None:
        # ctrl_wait_until(a, t)
        # ctrl_wait_on(a, b)
        # ret next_ctrl_time
        # precedency ctrl model -> ctrl_wait_until(a, t) (b,t2) from actor call_control
        # once the time is reached do what?
        #   - if in synch mode -> sim_synch -> block sim
        #   - if in time model mode -> don't block sim, but we used the info not to busy wait
        # serial pingpong? 
        pass
    '''

    @abstractmethod
    def call(self, arg: CallArg, token: Token, proc: IProcAPI) -> CallResult:
        pass


class IActor(INamed):
    @abstractproperty
    def procedures(self) -> List[IProcedure]:
        pass

    @abstractmethod
    def get_procedure(self, name: str) -> IProcedure:
        pass


class IProcessor(IProcessorAPI):
    @abstractmethod
    def step(self, board_tokens: List[Token]=[]) -> None:
        pass
    
    def load_profile(self, json_object: Any) -> None:
        pass

    @abstractproperty
    def api(self) -> IProcessorAPI:
        pass

    @abstractmethod
    def is_waiting(self) -> bool:
       pass

    @abstractmethod
    def has_work(self) -> bool:
       pass

    @abstractmethod
    def has_exited(self) -> bool:
        pass

    def snap(self) -> ProcessorSnapshot:
        return ProcessorSnapshot(step_count=self.api.step_count, 
                                 time=self.api.time, 
                                 frequency=self.api.frequency, 
                                 has_exited=self.has_exited(),
                                 is_waiting=self.is_waiting())