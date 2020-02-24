from abc import ABC, abstractclassmethod
import multiprocessing
from typing import List, Any
from .parall_synch_msgs import (
    SynchTakeStep, SynchStepResult, SynchClock, SynchMsgs)
from .msg_router import MsgRouter
from .interfaces import IEngine, IMessage, TimeInterval, IClock
from .manual_clock import ManualClock


class ParallProcess(ABC):
    def __init__(self):
        self.parent_conn, self.child_conn = multiprocessing.Pipe()
        kwargs={'engine_create_func': self.create_topology,
                'parent_conn': self.parent_conn,
                'child_conn': self.child_conn}
        self._process = multiprocessing.Process(target=self._process_func, 
                                                kwargs=kwargs)
        self._process.start()
    
    def join(self) -> None:
        self._process.join()
    
    def send_take_step(self) -> None:
        self.parent_conn.send(SynchTakeStep())
        
    def send_clock(self, clock: IClock) -> None:
        self.parent_conn.send(SynchClock(clock)) 
        
    def send_msgs(self, msgs: List[IMessage]) -> None:
        self.parent_conn.send(SynchMsgs(msgs))
        
    def recv(self) -> Any:
        return self.child_conn.recv()
    
    @abstractclassmethod
    def create_topology(cls) -> IEngine:
        pass
    
    @staticmethod
    def _process_func(topology_create_func, parent_conn, child_conn):
        topology = topology_create_func()
        clock = ManualClock()
        router = MsgRouter(topology, clock)
        while True:
            synch_msg = parent_conn.recv()
            if isinstance(synch_msg, SynchTakeStep):
                interval = topology.step()
                child_conn.send(SynchStepResult(interval))
                child_conn.send(SynchMsgs(router.pop_remote_msgs()))
            elif isinstance(synch_msg, SynchMsgs):
                for msg in synch_msg.msgs:
                    router.route(msg)
            elif isinstance(synch_msg, SynchClock):
                router.clock = synch_msg.clock
            else:
                return