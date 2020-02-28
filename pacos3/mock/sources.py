from typing import Callable, List, Any
from pacos3.interfaces import ITokenSource, Token, IProcessorState, StepCount


GenFuncType = Callable[[Any, IProcessorState], List[Token]]


class SingleShotSource(ITokenSource):
    def __init__(self, tokens: List[Token], shot_step :StepCount = 0):
        self._tokens = tokens
        self._shot_step = shot_step

    def generate(self, processor: IProcessorState) -> List[Token]:
        if processor.step_count >= self._shot_step:
            ret, self._tokens = self._tokens, []
            return ret
        return []


class PeriodicSource(ITokenSource):
    def __init__(self, gen_funcs: List[GenFuncType], 
                 step_interval :StepCount = 1,
                 first_step :StepCount = 0):
        self._gen_funcs = gen_funcs
        self._interval = step_interval
        self._next_step = first_step

    def generate(self, processor: IProcessorState) -> List[Token]:
        trigger_count = (((processor.step_count + self._interval) 
                           - self._next_step) / self._interval)
        rets = []
        while trigger_count > 0:
            rets.append(sum([x(self, processor) for x in self._gen_funcs], []))
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