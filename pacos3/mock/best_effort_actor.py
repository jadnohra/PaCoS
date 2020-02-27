import logging
from typing import List
from pacos3.address import Address
from pacos3.actor import Actor
from .procedures import NullProc, BufferProc, ProcState, Token, Time


class BestEffortActor(Actor):
    def __init__(self, name: str, out_address: Address = None):
        self._trigger_pin = NullProc('trigger', ProcState.CLOSED, 
                                     self._on_trigger)
        self._data_pin = BufferProc('data', ProcState.WAITING,
                                    self._on_data)
        super().__init__(name, [self._trigger_pin, self._data_pin])
        self._out_address = out_address
        self._triggered_count = 0
        self._state = 'INIT'
        self._health_rate = 'N/A'
        self._health_latency = 'N/A'

    @property
    def health(self) -> str:
        if self.state == 'ACTIVE':
            return '{} {}-LAT({})'.format(self.name, self._health_rate,
                                          self._health_latency)
        else:
            return '{} {}'.format(self.name, self.state)

    def _get_out_token(self, time: Time) -> Token:
        token = self._data_pin.pop_all()[0]
        self.health_latency = time - token.stamps[0].time
        return token if self._out_address else None

    def _on_data(self, _1, _2, _3) -> None:
        self.state = 'ACTIVE'
        token_count = len(self._data_pin.get_tokens())
        if token_count > 1:
            self.health_rate = 'DROPPING({})'.format(token_count - 1)
        self._data_pin.state = ProcState.CLOSED
        self._trigger_pin.state = ProcState.WAITING

    def _on_trigger(self,  _1, _2, time: Time) -> List[Token]:
        self.state = 'ACTIVE'
        token_count = len(self._data_pin.get_tokens())
        out_token = None
        if token_count == 0:
            self.health_rate = 'STARVING'
            self.health_latency = 'N/A'
        elif token_count > 0:
            out_token = self._get_out_token(time)
        self._data_pin.state = ProcState.WAITING
        self._trigger_pin.state = ProcState.CLOSED
        logging.info(self.health)
        return [out_token] if out_token else []
