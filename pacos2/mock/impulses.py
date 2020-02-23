from typing import Callable
from ..interfaces import IMessage
from ..discr_impulse import IDiscreteImpulse, DiscreteEventEngine


class PeriodicImpulse(IDiscreteImpulse):
    def __init__(self, msgs_func: Callable[[], IMessage], period=0,
                 first_ticks_left=0):
        self.msgs_func = msgs_func
        self.period = period
        self.ticks_left = first_ticks_left

    def generate(self, engine: DiscreteEventEngine) -> None:
        if self.ticks_left <= 0:
            self.ticks_left = self.period
            for msg in self.msgs_func(self):
                engine.put_msg(msg)
        else:
            self.ticks_left = self.ticks_left - 1


class FuzzyPeriodicImpulse(IDiscreteImpulse):
    def __init__(self, msgs_func: Callable[[], IMessage], period,
                 first_ticks_left, variance, rand):
        self.msgs_func = msgs_func
        self.period = period
        self.variance = variance
        self.rand = rand
        self.ticks_left = first_ticks_left

    def generate(self, engine: DiscreteEventEngine) -> None:
        if self.ticks_left <= 0:
            variance = self.rand.randint(-self.variance, self.variance)
            self.ticks_left = self.period + variance
            for msg in self.msgs_func(self):
                engine.put_msg(msg)
        else:
            self.ticks_left = self.ticks_left - 1
