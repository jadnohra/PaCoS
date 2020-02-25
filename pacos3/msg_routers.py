import os
import logging
from typing import List
from .interfaces import IMessage, IEngine, IMultiEngine, IClock, IMsgRouter


class BounceMsgRouter(IMsgRouter):
    def __init__(self, clock: IClock):
        self._clock = clock
        self._bounced_msgs = []
    
    @property
    def clock(self) -> IClock:
        return self._clock
    
    @clock.setter
    def clock(self, clock: IClock) -> None:
        self._clock = clock

    def route(self, msg: IMessage) -> None:
        self._bounced_msgs.append(msg)

    def pop_bounced(self) -> List[IMessage]:
        bounced, self._bounced_msgs = self._bounced_msgs, []
        return bounced


class SingleEngineRouter(BounceMsgRouter):
    def __init__(self, clock: IClock, engine: IEngine):
        super().__init__(clock)
        self._engine = engine
    
    def route(self, msg: IMessage) -> None:
        if msg.target.engine is None or msg.target.engine == self._engine.name:
            self._engine.put_msg(msg)
        else:
            super().route(msg)


class MultiEngineRouter(BounceMsgRouter):
    def __init__(self, clock: IClock, multi_engine: IMultiEngine):
        super().__init__(clock)
        self._multi_engine = multi_engine
    
    def route(self, msg: IMessage) -> None:
        engine = self._multi_engine.get_engine(msg.target.engine)
        if engine is not None:
            engine.put_msg(msg)
        else:
            super().route(msg)
