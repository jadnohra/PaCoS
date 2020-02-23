from typing import Callable
from ..interfaces import IImpulse, IMessage, IMsgRouter


class PeriodicImpulse(IImpulse):
    def __init__(self, msgs_func: Callable[[], IMessage], period=0,
                 first_ticks_left=0):
        self.msgs_func = msgs_func
        self.period = period
        self.ticks_left = first_ticks_left

    def generate(self, router: IMsgRouter) -> None:
        if self.ticks_left <= 0:
            self.ticks_left = self.period
            for msg in self.msgs_func(self):
                router.route(msg)
        else:
            self.ticks_left = self.ticks_left - 1


class FuzzyPeriodicImpulse(IImpulse):
    def __init__(self, msgs_func: Callable[[], IMessage], period,
                 first_ticks_left, variance, rand):
        self.msgs_func = msgs_func
        self.period = period
        self.variance = variance
        self.rand = rand
        self.ticks_left = first_ticks_left

    def generate(self, router: IMsgRouter) -> None:
        if self.ticks_left <= 0:
            variance = self.rand.randint(-self.variance, self.variance)
            self.ticks_left = self.period + variance
            for msg in self.msgs_func(self):
                router.route(msg)
        else:
            self.ticks_left = self.ticks_left - 1
