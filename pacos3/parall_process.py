import os
import multiprocessing
import logging
from abc import ABC, abstractclassmethod
from typing import List, Any, Callable
from .parall_synch_msgs import (
    SynchTakeStep, SynchStepResult, SynchMsgs, SynchExit)
from .interfaces import IProcessor, ProcCall, TimeInterval, IClock
from .manual_clock import ManualClock


class ParallProcess(ABC):
    def __init__(self, mp_context: Any):
        self.conn, child_conn = mp_context.Pipe()
        kwargs={'processor_create_func': self.create_processor,
                'conn': child_conn}
        self._process = mp_context.Process(target=self._process_func, 
                                           kwargs=kwargs)
        self._process.start()
    
    def join(self) -> None:
        self._process.join()
    
    def send_take_step(self, clock: IClock) -> None:
        self.conn.send(SynchTakeStep(clock)) 
        
    def send_proc_calls(self, msgs: List[ProcCall]) -> None:
        self.conn.send(SynchMsgs(msgs))

    def send_exit(self) -> None:
        self.conn.send(SynchExit())
        
    def recv_step_result(self) -> Any:
        return self.conn.recv()
    
    @abstractclassmethod
    def create_processor(cls) -> IProcessor:
        pass

    @staticmethod
    def _process_func(processor_create_func, conn):
        processor = processor_create_func()
        while True:
            logging.info('{}: waiting to step'.format(os.getpid()))
            synch_msg = conn.recv()
            if isinstance(synch_msg, SynchTakeStep):
                processor.router.clock = synch_msg.clock
                interval = processor.step()
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