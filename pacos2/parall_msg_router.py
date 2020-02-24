import os
import multiprocessing
from typing import Dict, Any
from .interfaces import ITopology, IMessage, IEngine, IClock


class ParallMsgRouter:
    def __init__(self, topology: ITopology, clock: IClock):
        self._topology = topology
        self._clock = clock
        self._msg_queue = multiprocessing.Queue()
        self._pid_engine_dict = {}
    
    @property
    def clock(self) -> IClock:
        return self._clock
    
    def set_routing_dict(self, routing_dict: Dict[Any, IEngine]) -> None:
        self._pid_engine_dict = routing_dict

    def route(self, msg: IMessage) -> None:
        print('XXX', self._pid_engine_dict, os.getpid())
        local_engine = self._pid_engine_dict[os.getpid()]
        if msg.target.engine is None or msg.target.engine == local_engine.name:
            print('LOCAL')
            local_engine.put_msg(msg)
        else:
            print('REMOTE')
            self._msg_queue.put(msg)

    def flush(self) -> None:
        while not self._msg_queue.empty():
            msg = self._msg_queue.get()
            print('FLUSH', msg)
            self._topology.get_engine(msg.target.engine).put_msg(msg)