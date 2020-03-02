from typing import Any, List
from .address import Address
from .time import Time, StepCount


CallArg = Any


class Call:
    def __init__(self, arg: CallArg, target: Address, 
                 call_time: Time = None, call_step: StepCount = None):
        self.arg = arg
        self.target = target
        self.call_time = call_time
        self.call_step = call_step

    def __str__(self) -> str:
        return '{} -> {} @ {}'.format(self.arg, self.target, self.call_time)


class CallResult:
    def __init__(self, calls: List[Call] = [], step_count: StepCount = 1):
        self.calls = calls
        self.step_count = step_count