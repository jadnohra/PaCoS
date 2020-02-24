from abc import ABC, abstractclassmethod
import multiprocessing
from typing import List
from .parall_synch_msgs import SynchTakeStep, SynchClock, SynchMsgs
from .parall_msg_router import ParallMsgRouter
from .interfaces import IEngine
from .manual_clock import ManualClock


class SpawnedEngineProcess(ABC):
    def __init__(self):
        proc_pipe_in, proc_pipe_out = multiprocessing.Pipe()
        kwargs={'engine_create_func': self.create_engine,
                'pipe_in': proc_pipe_in,
                'pipe_out': proc_pipe_out}
        self._process = multiprocessing.Process(target=self._process_func, 
                                                kwargs=kwargs)
        self._process.start()
    
    @abstractclassmethod
    def create_engine(cls) -> IEngine:
        pass
    
    @staticmethod
    def _process_func(engine_create_func, pipe_in, pipe_out):
        engine = engine_create_func()
        clock = ManualClock()
        router = ParallMsgRouter(clock)
        while True:
            synch_msg = pipe_in.recv()
            if isinstance(synch_msg, SynchTakeStep):
                interval = engine.step()
                pipe_out.send(interval)
                pipe_out.send(router.pop_remote_msgs())
            elif isinstance(synch_msg, SynchMsgs):
                for msg in synch_msg.msgs:
                    engine.put_msg(msg)
            elif isinstance(synch_msg, SynchClock):
                router.set_clock(synch_msg.clock)
            else:
                return