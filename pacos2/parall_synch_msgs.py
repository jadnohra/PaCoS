from typing import List
from .interfaces import IClock, IMessage, TimeInterval


class SynchTakeStep:
    def __init__(self):
        pass

class SynchStepResult:
    def __init__(self, step_interval: TimeInterval):
        self.step_interval = step_interval

class SynchClock:
    def __init__(self, clock: IClock):
        self.clock = clock

class SynchMsgs:
    def __init__(self, msgs: List[IMessage]):
        self.msgs = msgs
