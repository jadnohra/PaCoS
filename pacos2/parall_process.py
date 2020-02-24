from abc import ABC, abstractclassmethod
import multiprocessing
from typing import List, Any, Callable
from .parall_synch_msgs import SynchTakeStep, SynchStepResult, SynchMsgs
from .msg_routers import MultiEngineRouter
from .interfaces import IEngine, IMultiEngine, IMessage, TimeInterval, IClock
from .manual_clock import ManualClock


class ParallProcess(ABC):
    def __init__(self, multi_engine_create_func: Callable[[], IMultiEngine]):
        self.parent_conn, self.child_conn = multiprocessing.Pipe()
        kwargs={'multi_engine_create_func': multi_engine_create_func,
                'parent_conn': self.parent_conn,
                'child_conn': self.child_conn}
        self._process = multiprocessing.Process(target=self._process_func, 
                                                kwargs=kwargs)
        self._process.start()
    
    def join(self) -> None:
        self._process.join()
    
    def send_take_step(self, clock: IClock) -> None:
        self.parent_conn.send(SynchTakeStep(clock)) 
        
    def send_msgs(self, msgs: List[IMessage]) -> None:
        self.parent_conn.send(SynchMsgs(msgs))
        
    def recv_step_result(self) -> Any:
        return self.child_conn.recv()
    
    @staticmethod
    def _process_func(multi_engine_create_func, parent_conn, child_conn):
        multi_engine = multi_engine_create_func()
        clock = ManualClock()
        router = MultiEngineRouter(multi_engine, clock)
        while True:
            synch_msg = parent_conn.recv()
            if isinstance(synch_msg, SynchTakeStep):
                router.clock = synch_msg.clock
                interval = multi_engine.step()
                # TODO set eng_names to None when no change
                engine_names = [x.name for x in multi_engine.engines] 
                child_conn.send(SynchStepResult(interval, 
                                                router.pop_bounced(),
                                                engine_names))
            elif isinstance(synch_msg, SynchMsgs):
                for msg in synch_msg.msgs:
                    router.route(msg)
            else:
                return