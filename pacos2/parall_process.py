from abc import ABC, abstractclassmethod
import multiprocessing
import logging
from typing import List, Any, Callable
from .parall_synch_msgs import (
    SynchTakeStep, SynchStepResult, SynchMsgs, SynchExit)
from .msg_routers import MultiEngineRouter
from .interfaces import IEngine, IMultiEngine, IMessage, TimeInterval, IClock
from .manual_clock import ManualClock


class ParallProcess(ABC):
    def __init__(self):
        self.conn, child_conn = multiprocessing.Pipe()
        kwargs={'multi_engine_create_func': self.create_multi_engine,
                'conn': child_conn}
        self._process = multiprocessing.Process(target=self._process_func, 
                                                kwargs=kwargs)
        self._process.start()
    
    def join(self) -> None:
        self._process.join()
    
    def send_take_step(self, clock: IClock) -> None:
        self.conn.send(SynchTakeStep(clock)) 
        
    def send_msgs(self, msgs: List[IMessage]) -> None:
        self.conn.send(SynchMsgs(msgs))

    def send_exit(self) -> None:
        self.conn.send(SynchExit())
        
    def recv_step_result(self) -> Any:
        return self.conn.recv()
    
    @abstractclassmethod
    def create_multi_engine(cls) -> IMultiEngine:
        pass

    @staticmethod
    def _process_func(multi_engine_create_func, conn):
        multi_engine = multi_engine_create_func()
        while True:
            synch_msg = conn.recv()
            if isinstance(synch_msg, SynchTakeStep):
                multi_engine.router.clock = synch_msg.clock
                interval = multi_engine.step()
                # TODO set eng_names to None when no change
                engine_names = [x.name for x in multi_engine.engines] 
                conn.send(SynchStepResult(interval, 
                                          multi_engine.router.pop_bounced(),
                                          engine_names))
            elif isinstance(synch_msg, SynchMsgs):
                for msg in synch_msg.msgs:
                    multi_engine.router.route(msg)
            else:
                break