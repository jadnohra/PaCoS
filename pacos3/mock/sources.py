from typing import Callable, List, Any
from pacos3.interfaces import ITokenSource, Token, Time, TimeInterval


GenFuncType = Callable[[Any, Time], List[Token]]


class PeriodicSource(ITokenSource):
    def __init__(self, gen_funcs: List[GenFuncType], 
                 interval :TimeInterval = 1,
                 first_time :Time = 0):
        self._gen_funcs = gen_funcs
        self._interval = interval
        self._next_time = first_time

    def generate(self, time: Time) -> List[Token]:
        trigger_count = (((time + self._interval) - self._next_time) 
                         / self._interval)
        rets = []
        while trigger_count > 0:
            rets.append(sum([x(self, time) for x in self._gen_funcs], []))
            trigger_count = trigger_count - 1
        return sum(rets, [])


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