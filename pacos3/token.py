from collections import namedtuple
from typing import List
import copy
from .proc_call import ProcCall
from .interfaces import IClock, Time, TimeInterval, Address


class Token:
    def __init__(self, call: ProcCall, time: Time):
        self._call = call
        self._target = copy.copy(call.target)
        self._stamps = [time]
    
    @property
    def call(self) -> ProcCall:
        return self._call

    @property
    def target(self) -> Address:
        return self._target

    @property
    def emission_time(self) -> Time:
        return self._stamps[0].time

    @property
    def wire_time(self) -> TimeInterval:
        return self._stamps[-1].time - self._stamps[0].time

    def forward_processor(self, time: Time) -> "Token":
        self._stamps.append(time)
        self._target.processor = None
        return self

    def __str__(self) -> str:
        return '{} @ [{}]'.format(
                            self.call,
                            ', '.join([str(x) for x in self._stamps]))
