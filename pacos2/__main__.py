from enum import Enum, auto
from typing import List, Tuple


Address = str
Time = int
TimeInterval = int


class Message:
    def __init__(self):
        pass

    @property
    def target(self) -> Address:
        return None

    @property
    def source(self) -> Address:
        return None


    @property
    def emission_time(self) -> Time:
        return None

    @property
    def wire_time(self) -> TimeInterval:
        return None


class PinState(Enum):
    CLOSED = auto()
    OPEN = auto()
    WAITING = auto()


class Pin:
    def __init__(self):
        pass

    @property
    def name(self) -> str:
        return None

    @property
    def state(self) -> PinState:
        return None

    @property
    def process(self, msg: Message) -> Time:
        return 0


class Actor:
    def __init__(self):
        pass

    @property
    def name(self) -> str:
        return None

    @property
    def pins(self) -> List[Pin]:
        return []


class Impulse:
    
    def generate(self) -> List[Message]:
        return []


class Engine:

    def step(self) -> TimeInterval:
        return 0

    def put(self, msg: Message):
        pass


class DiscreteEventEngine(Engine):

    def step(self) -> TimeInterval:
        return 0

    def put(self, msg: Message):
        pass


class ImpulseEngine(Engine):

    def step(self) -> TimeInterval:
        return 0

    def put(self, msg: Message):
        pass


class ParallelContext:
    def __init__(self):
        self._engines = []
        self._wave_t1 = None
        self._wave_times = []

    def transfer(self, msg: Message):
        pass

    @property
    def engine_count(self):
        return len(self._engines)

    def _step_parallel(self, engines: List[Engine]) -> List[TimeInterval]:
        return []
        
    def step(self) -> Tuple[TimeInterval, TimeInterval]:
        cand_engines = [self._engines[i] for i in range(self.engine_count)
                        if (self._wave_t1 is None or 
                            self._wave_times[i] < self._wave_t1)]
        if len(cand_engines) == 0:
            wave_t1 = max(self._wave_times)
            if wave_t1 > self._wave_t1:
                return self.step()
            else:
                return 0
        intervals = self._step_parallel(cand_engines)
        return [min(intervals), max(intervals)]


print("hello")