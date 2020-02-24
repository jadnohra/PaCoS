import os
import logging
from typing import List
from .interfaces import ITopology, IMessage, IEngine, IClock


class MsgRouter:
    def __init__(self, local_topology: ITopology, clock: IClock):
        self._local_topology = local_topology
        self._clock = clock
        self._remote_msgs = []
    
    @property
    def clock(self) -> IClock:
        return self._clock
    
    @clock.setter
    def clock(self, clock: IClock) -> None:
        self._clock = clock
    
    def route(self, msg: IMessage) -> None:
        local_engine = self._local_topology.get_engine(msg.target.engine)
        if local_engine is not None:
            local_engine.put_msg(msg)
        else:
            self._remote_msgs.append(msg)

    def pop_remote_msgs(self) -> List[IMessage]:
        ret = self._remote_msgs
        self._remote_msgs = []
        return ret