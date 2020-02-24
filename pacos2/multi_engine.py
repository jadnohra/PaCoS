from typing import List
from .interfaces import (
        IMsgRouter, IMessage, IEngine, TimeInterval, IMultiEngine, IClock)
from .msg_routers import MultiEngineRouter


class MultiEngine(IMultiEngine):
    def __init__(self, clock: IClock = None):
        self._engines = []
        self._name_engine_dict = {}
        self._router = MultiEngineRouter(clock, self)

    def add_engine(self, engine: IEngine) -> None:
        engine.init_address(None)
        self._engines.append(engine)
        self._name_engine_dict[engine.name] = engine

    def get_engine(self, engine_name: str) -> IEngine:
        if engine_name is None and len(self._engines) >= 0:
            return self._engines[0]
        return self._name_engine_dict.get(engine_name, None)
    
    @property
    def engines(self) -> List[IEngine]:
        return self._engines

    def step(self) -> TimeInterval:
        intervals = [engine.step(self._router) for engine in self._engines]
        return min(intervals)
