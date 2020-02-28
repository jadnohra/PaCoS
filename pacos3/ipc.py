from typing import List
from .interfaces import TimeInterval, ProcessorSnapshot, Token


class SynchStep:
     def __init__(self, board_tokens: List[Token]):
        self.board_tokens = board_tokens

class SynchStepResult:
    def __init__(self, board_tokens: List[Token], 
                 state_snap: ProcessorSnapshot):
        self.board_tokens = board_tokens
        self.state_snap = state_snap

class SynchExit:
    def __init__(self):
        pass