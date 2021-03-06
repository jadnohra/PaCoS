import logging
from ..interfaces import Address, Addressable, PinState, IMessage, IMsgRouter
from ..actor import Actor
from .pins import NullPin, BufferPin


class BestEffortActor(Actor):
    def __init__(self, name: str = 'a', out_address: Address = None):
        self.trigger_pin = NullPin('trigger', PinState.CLOSED, 
                                    self._on_trigger)
        self.data_pin = BufferPin('data', PinState.WAITING,
                                  self._on_data)
        super().__init__(name, [self.trigger_pin, self.data_pin])
        self._out_address = out_address
        self.triggered_count = 0
        self.state = 'INIT'
        self.health_rate = 'N/A'
        self.health_latency = 'N/A'

    @property
    def health(self) -> str:
        if self.state == 'ACTIVE':
            return '{} {}-LAT({})'.format(self._name, self.health_rate,
                                          self.health_latency)
        else:
            return self.state

    def _send_out_msg(self, router: IMsgRouter) -> None:
        data_msg = self.data_pin.messages[0]
        self.health_latency = router.clock.time - data_msg.stamps[0].time
        self.data_pin.messages.clear()
        if self._out_address:
            data_msg.forward(self._out_address)
            router.route(data_msg)

    def _on_data(self,  _, msg: IMessage, router: IMsgRouter) -> None:
        self.state = 'ACTIVE'
        if len(self.data_pin.messages) > 1:
            self.health_rate = 'DROPPING({})'.format(
                                                len(self.data_pin.messages)-1)
        self.data_pin.state = PinState.CLOSED
        self.trigger_pin.state = PinState.WAITING

    def _on_trigger(self,  _, msg: IMessage, router: IMsgRouter) -> None:
        self.state = 'ACTIVE'
        self.health_rate = 'OK'
        if len(self.data_pin.messages) == 0:
            self.health_rate = 'STARVING'
            self.health_latency = 'N/A'
        if len(self.data_pin.messages) > 0:
            self._send_out_msg(router)
        self.data_pin.state = PinState.WAITING
        self.trigger_pin.state = PinState.CLOSED
        logging.info(self.health)
