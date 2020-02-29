from typing import Any, List
from .address import Address
from .time import Time, StepCount


CallArg = Any


class Call:
    def __init__(self, arg: CallArg, target: Address, call_time: Time = 0.0):
        self.arg = arg
        self.target = target
        self.call_time = call_time

    def __str__(self) -> str:
        return '{} -> {} @ {}'.format(self.arg, self.target, self.call_time)


class CallResult:
    def __init__(self, step_count: StepCount = 0, calls: List[Call] = []):
        self.step_count = step_count
        self.calls = calls