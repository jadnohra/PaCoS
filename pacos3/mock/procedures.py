import logging
from typing import List, Callable
from pacos3.address import Address
from pacos3.interfaces import (
        IProcedure, CallMode, ProcState, Token, CallResult, Time)
from pacos3.procedure import Procedure


class NullProc(Procedure):
    def __init__(
          self, name: str, state: ProcState = ProcState.OPEN, 
          notif_func: Callable[[IProcedure, Token, Time], List[Token]] = None,
          processing_time: int = 1):
        super().__init__(name, state)
        self._notif_func = notif_func
        self._processing_time = processing_time

    def call(self, token: Token, time: Time, mode: CallMode) -> CallResult:
        if not super().should_process(token, time, mode):
            return CallResult(0, [])
        tokens = []
        if self._notif_func:
            tokens = self._notif_func(self, token, time)
        return CallResult(self._processing_time, tokens)


class IdentProc(Procedure):
    def __init__(
          self, name: str, out_address: Address, 
          state: ProcState = ProcState.OPEN, 
          notif_func: Callable[[IProcedure, Token, Time], None] = None,
          processing_time: int = 1):
        super().__init__(name, state)
        self._out_address = out_address
        self._notif_func = notif_func
        self._processing_time = processing_time

    def call(self, token: Token, time: Time, mode: CallMode) -> CallResult:
        if not super().should_process(token, time, mode):
            return CallResult(0, [])
        if self._notif_func:
            self._notif_func(self, token, time)
        return CallResult(self._processing_time, 
                          [token.forward_target(self._out_address, time)])


class BufferProc(Procedure):
    def __init__(
          self, name: str, state: ProcState = ProcState.OPEN, 
          notif_func: Callable[[IProcedure, Token, Time], List[Token]] = None,
          processing_time: int = 1):
        super().__init__(name, state)
        self._notif_func = notif_func
        self._processing_time = processing_time
        self._buffer = []

    def get_tokens(self) -> List[Token]:
        return self._buffer

    def pop_all(self) -> List[Token]:
        ret, self._buffer = self._buffer, []
        return ret

    def call(self, token: Token, time: Time, mode: CallMode) -> CallResult:
        if not super().should_process(token, time, mode):
            return 0
        if self._notif_func:
            self._notif_func(self, token, time)
        self._buffer.append(token)
        return CallResult(self._processing_time, [])
