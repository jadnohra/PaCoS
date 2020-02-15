from typing import Callable
from .discrete_event import Message
from .discrete_event_ism import Impulse


class PeriodicImpulse(Impulse):
    def __init__(self, msg_func: Callable[[], Message], period=0,
                 first_ticks_left=0):
        self.msg_func = msg_func
        self.period = period
        self.ticks_left = first_ticks_left

    def call(self, engine: "IsmEngine"):
        if self.ticks_left <= 0:
            self.ticks_left = self.period
            engine.add_msg(self.msg_func(self))
        else:
            self.ticks_left = self.ticks_left - 1



class FuzzyPeriodicImpulse(Impulse):
    def __init__(self, msg_func: Callable[[], Message], period,
                 first_ticks_left, variance, rand):
        self.msg_func = msg_func
        self.period = period
        self.variance = variance
        self.rand = rand
        self.ticks_left = first_ticks_left

    def call(self, engine: "IsmEngine"):
        if self.ticks_left <= 0:
            variance = self.rand.randint(-self.variance, self.variance)
            self.ticks_left = self.period + variance
            engine.add_msg(self.msg_func(self))
        else:
            self.ticks_left = self.ticks_left - 1
