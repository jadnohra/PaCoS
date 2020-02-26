import os
import multiprocessing
import logging
from abc import ABC, abstractclassmethod
from typing import List, Any, Callable
from .process_msgs import SynchStep, SynchStepResult, SynchExit
from .interfaces import IProcessor, ProcCall, TimeInterval, IClock, Token
from .manual_clock import ManualClock
from .processor import Processor


class Process(ABC):
    def __init__(self, mp_context: Any, name: str, 
                 init_func: Callable[[Processor], None],
                 processor_kwargs: Dict):
        self._name = name
        self.conn, child_conn = mp_context.Pipe()
        kwargs={'init_func': init_func, 'conn': child_conn, 
                'processor_kwargs': processor_kwargs}
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
    
    @property
    def name(self) -> str:
        return self._name

    @staticmethod
    def _process_func(name, init_func, conn, processor_kwargs):
        processor = Processor(**processor_kwargs)
        init_func(processor)
        while True:
            logging.info('{}: waiting to step'.format(os.getpid()))
            synch_msg = conn.recv()
            if isinstance(synch_msg, SynchStep):
                step_result = processor.step(synch_msg.clock, synch_msg.tokens)
                conn.send(SynchStepResult(step_result))
            else:
                break