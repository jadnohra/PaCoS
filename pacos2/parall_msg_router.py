import os
import multiprocessing
from typing import Dict, Any
from .interfaces import ITopology, IMessage, IEngine


class ParallMessageRouter:
    def __init__(self, topology: ITopology):
        self._topology = topology
        self._msg_queue = multiprocessing.Queue()
        self._routing_dict = {}
    
    def set_routing_dict(self, routing_dict: Dict[Any, IEngine]):
        self._routing_dict = routing_dict

    def route(self, msg: IMessage) -> None:
        local_engine = self._routing_dict[os.getpid()]
        if msg.target.engine is None or msg.target.engine == local_engine.name:
            local_engine.put_msg(msg)
        else:
            self._msg_queue.put(msg)

    def flush(self):
        while not self._msg_queue.empty():
            msg = self._msg_queue.get()
            self._topology.engine(msg.target.engine).put_msg(msg)