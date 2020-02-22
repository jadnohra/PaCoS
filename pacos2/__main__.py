from enum import Enum, auto
from typing import List, Tuple, Callable, Dict
import multiprocessing


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


class MsgRouter:
    def route(self, msg: Message) -> None:
        pass


class Engine:
    def step(self, router: MsgRouter) -> TimeInterval:
        return 0

    def put(self, msg: Message) -> None:
        pass


class DiscreteEventEngine(Engine):
    def step(self, router: MsgRouter) -> TimeInterval:
        return 0

    def put(self, msg: Message) -> None:
        pass


class ImpulseEngine(Engine):
    def step(self, router: MsgRouter) -> TimeInterval:
        return 0

    def put(self, msg: Message) -> None:
        pass


class ParallelContext(MsgRouter):
    def __init__(self):
        self._engines = []
        self._wave_t1 = None
        self._wave_times = []
        self._parall_msg_queue = multiprocessing.Queue()

    def route(self, msg: Message) -> None:
         self._parall_msg_queue.put(msg)

    @property
    def engine_count(self) -> int:
        return len(self._engines)

    @staticmethod
    def _run_parall(funcs_kwargs: List[Tuple[Callable, Dict]]) -> None:
        processes = []
        for func, kwargs in funcs_kwargs:
            p = multiprocessing.Process(target=func, kwargs=kwargs)
            processes.append(p)
            p.start()
        for p in processes:
            p.join()

    def _step_parall(self, engines: List[Engine]) -> List[TimeInterval]:
        def step_engine(engines, out_intervals, index):
            out_intervals[index] = engines[index].step(self)
        
        intervals = [None]*len(engines)
        self._run_parall([(lambda i: step_engine(engines, intervals, i), {})
                          for i in range(len(engines))])
        return intervals

    def _process_parall_msg_queue(self) -> None:
        queue = self._parall_msg_queue
        while not queue.empty():
            queue.get()
        
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
        intervals = self._step_parall(cand_engines)
        return [min(intervals), max(intervals)]


print("hello")