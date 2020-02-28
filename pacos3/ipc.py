from typing import List
from .interfaces import Time, StepResult, ProcessorStateSnapshot, Token


class SynchStep:
     def __init__(self, time: Time, tokens: List[Token]):
        self.time = time
        self.tokens = tokens

class SynchStepResult:
    def __init__(self, result: StepResult, state_snap: ProcessorStateSnapshot):
        self.result = result
        self.state_snap = state_snap

class SynchExit:
    def __init__(self):
        pass