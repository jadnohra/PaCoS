from .call import CallArg, CallResult
from .interfaces import IProcedure, Token, IProcAPI, IProcessorAPI


class Procedure(IProcedure):
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def call(self, arg: CallArg, token: Token, proxor: IProcAPI) -> CallResult:
        return CallResult

    def __str__(self) -> str:
        return self._name