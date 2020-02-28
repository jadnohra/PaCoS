from typing import List
from .interfaces import Time, StepResult, Token


class SynchStep:
     def __init__(self, time: Time, tokens: List[Token]):
        self.time = time
        self.tokens = tokens

class SynchStepResult:
    def __init__(self, result: StepResult):
        self.result = result

class SynchExit:
    def __init__(self):
        pass