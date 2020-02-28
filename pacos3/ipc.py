from typing import List
from .interfaces import TimeInterval, StepResult, ProcessorStateSnapshot, Token


class SynchStep:
     def __init__(self, tokens: List[Token], paused_time: TimeInterval):
        self.tokens = tokens
        self.paused_time = paused_time

class SynchStepResult:
    def __init__(self, result: StepResult, state_snap: ProcessorStateSnapshot):
        self.result = result
        self.state_snap = state_snap

class SynchExit:
    def __init__(self):
        pass