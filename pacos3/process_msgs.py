from typing import List
from .interfaces import IClock, StepResult, Token


class SynchStep:
     def __init__(self, clock: IClock, tokens: List[Token]):
        self.clock = clock
        self.tokens = tokens

class SynchStepResult:
    def __init__(self, result: StepResult):
        self.result = result

class SynchExit:
    def __init__(self):
        pass