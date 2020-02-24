from typing import List
from .interfaces import IClock, IMessage


class SynchTakeStep:
    def __init__(self):
        pass

class SynchClock:
    def __init__(self, clock: IClock):
        self.clock = clock

class SynchMsgs:
    def __init__(self, msgs: List[IMessage]):
        self.msgs = msgs
