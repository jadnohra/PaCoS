from typing import Callable
from ..interfaces import IMessage, IClock, TimeInterval, Time
from ..discr_impulse import IDiscreteImpulse, DiscreteEventEngine


class PeriodicImpulse(IDiscreteImpulse):
    def __init__(self, gen_msgs_func: Callable[[], IMessage], 
                 interval :TimeInterval = 1,
                 first_time :Time = 0):
        self.gen_msgs_func = gen_msgs_func
        self.interval = interval
        self.next_time = first_time

    def generate(self, engine: DiscreteEventEngine, clock: IClock
                 ) -> TimeInterval:
        trigger_count = (((clock.time + self.interval) - self.next_time) 
                         / self.interval)
        spent_interval = 0
        while trigger_count > 0:
            for msg in self.gen_msgs_func(self, clock):
                engine.put_msg(msg)
            trigger_count = trigger_count - 1
            spent_interval = self.interval
        return spent_interval


'''
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
'''