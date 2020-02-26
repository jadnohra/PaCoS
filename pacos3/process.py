import os
import multiprocessing
import logging
from abc import ABC, abstractclassmethod
from typing import List, Any, Callable
from .process_msgs import SynchStep, SynchStepResult, SynchExit
from .interfaces import IProcessor, ProcCall, TimeInterval, IClock, Token
from .manual_clock import ManualClock


class Process(ABC):
    def __init__(self, mp_context: Any):
        self.conn, child_conn = mp_context.Pipe()
        kwargs={'processor_create_func': self.create_processor,
                'conn': child_conn}
        self._process = mp_context.Process(target=self._process_func, 
                                           kwargs=kwargs)
        self._process.start()
    
    def join(self) -> None:
        self._process.join()
    
    def send_step(self, clock: IClock, tokens: List[Token]) -> None:
        self.conn.send(SynchStep(clock, tokens)) 
        
    def send_exit(self) -> None:
        self.conn.send(SynchExit())
        
    def recv_step_result(self) -> Any:
        return self.conn.recv()
    
    @abstractclassmethod
    def get_name(cls) -> str:
        pass

    @abstractclassmethod
    def create_processor(cls) -> IProcessor:
        pass

    @staticmethod
    def _process_func(processor_create_func, conn):
        processor = processor_create_func()
        while True:
            logging.info('{}: waiting to step'.format(os.getpid()))
            synch_msg = conn.recv()
            if isinstance(synch_msg, SynchStep):
                step_result = processor.step(synch_msg.clock, synch_msg.tokens)
                conn.send(SynchStepResult(step_result))
            else:
                break