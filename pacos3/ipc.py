from typing import List
from .interfaces import TimeInterval, StepResult, ProcessorSnapshot, Token


class SynchStep:
     def __init__(self, board_tokens: List[Token]):
        self.board_tokens = board_tokens

class SynchStepResult:
    def __init__(self, result: StepResult, state_snap: ProcessorSnapshot):
        self.result = result
        self.state_snap = state_snap

class SynchExit:
    def __init__(self):
        pass