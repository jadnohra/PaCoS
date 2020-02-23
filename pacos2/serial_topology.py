from .interfaces import (
        IMsgRouter, IMessage, IEngine, TimeInterval, ITopology, IClock)
from .serial_msg_router import SerialMsgRouter


class SerialTopology(ITopology):
    def __init__(self, clock: IClock):
        self._engines = []
        self._name_engine_dict = {}
        self._router = SerialMsgRouter(self, clock)

    def add_engine(self, engine: IEngine) -> None:
        engine.init_address(None)
        self._engines.append(engine)
        self._name_engine_dict[engine.name] = engine

    def get_engine(self, engine_name: str) -> IEngine:
        if engine_name is None and len(self._engines) >= 0:
            return self._engines[0]
        return self._name_engine_dict.get(engine_name, None)
        
    def step(self) -> TimeInterval:
        intervals = [engine.step(self._router) for engine in self._engines]
        return min(intervals)
