from typing import List
from .interfaces import IClock, IMessage, TimeInterval


class SynchTakeStep:
     def __init__(self, clock: IClock):
        self.clock = clock

class SynchStepResult:
    def __init__(self, step_interval: TimeInterval, 
                 msgs: List[IMessage], engine_names: List[str]):
        self.step_interval = step_interval
        self.msgs = msgs
        self.engine_names = engine_names

class SynchMsgs:
    def __init__(self, msgs: List[IMessage]):
        self.msgs = msgs
