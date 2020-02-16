from typing import Callable
from .discrete_event import Message
from .discrete_event_ism import Impulse


class PeriodicImpulse(Impulse):
    def __init__(self, msgs_func: Callable[[], Message], period=0,
                 first_ticks_left=0):
        self.msgs_func = msgs_func
        self.period = period
        self.ticks_left = first_ticks_left

    def call(self, engine: "IsmEngine") -> None:
        if self.ticks_left <= 0:
            self.ticks_left = self.period
            for msg in self.msgs_func(self):
                engine.add_msg(msg)
        else:
            self.ticks_left = self.ticks_left - 1


class FuzzyPeriodicImpulse(Impulse):
    def __init__(self, msgs_func: Callable[[], Message], period,
                 first_ticks_left, variance, rand):
        self.msgs_func = msgs_func
        self.period = period
        self.variance = variance
        self.rand = rand
        self.ticks_left = first_ticks_left

    def call(self, engine: "IsmEngine") -> None:
        if self.ticks_left <= 0:
            variance = self.rand.randint(-self.variance, self.variance)
            self.ticks_left = self.period + variance
            for msg in self.msgs_func(self):
                engine.add_msg(msg)
        else:
            self.ticks_left = self.ticks_left - 1
