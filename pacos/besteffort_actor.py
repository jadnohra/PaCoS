from typing import List
from .discrete_event import Actor, Pin, Message
from .discrete_event_ism import IsmEngine
from .basic_pins import BasicIsmPin


class BestEffortActor(Actor):
    def __init__(self, out_pin=None, name=''):
        super().__init__()
        self.in_data_pin = BasicIsmPin(self, 'data', waiting=True,
                                       accepting=True)
        self.in_trigger_pin = BasicIsmPin(self, 'trigger', waiting=True,
                                          accepting=True)
        self.out_pin = out_pin
        self._name = name
        self.triggered_count = 0
        self.state = 'INIT'
        self.health_rate = 'N/A'
        self.health_latency = 'N/A'

    @property
    def name(self) -> str:
        return self._name

    @property
    def pins(self) -> List[Pin]:
        return [self.in_data_pin, self.in_trigger_pin]

    @property
    def health(self) -> str:
        if self.state == 'ACTIVE':
            return '{} {}-LAT({})'.format(self._name, self.health_rate,
                                          self.health_latency)
        else:
            return self.state

    def _trigger(self, engine: "Engine") -> None:
        data_msg = self.in_data_pin.msgs[0]
        self.health_latency = engine.compare_stamps(
                                    engine.get_stamp(),
                                    data_msg.stamps[0])
        self.in_data_pin.msgs.clear()
        if self.out_pin:
            engine.add_msg(data_msg.forward(self.out_pin))

    def call(self, engine: "Engine") -> None:
        self.state = 'ACTIVE'
        if len(self.in_trigger_pin.msgs):
            self.in_trigger_pin.msgs.clear()
            self.health_rate = 'OK'
            if len(self.in_data_pin.msgs) == 0:
                self.health_rate = 'STARVING'
                self.health_latency = 'N/A'
            elif len(self.in_data_pin.msgs) > 1:
                self.health_rate = 'DROPPING({})'.format(
                                                len(self.in_data_pin.msgs)-1)
                self.in_data_pin.msgs = self.in_data_pin.msgs[-1:]
            if len(self.in_data_pin.msgs) > 0:
                self._trigger(engine)
            print('*', engine.frame,  self.health)
        else:
            pass
            # print(self.health)


class SynchronizedBestEffortActor(BestEffortActor):
    def __init__(self, out_pin=None, name=''):
        super().__init__(out_pin=out_pin, name=name)
        self.in_trigger_pin.is_waiting = False

    def _trigger(self, engine: "Engine") -> None:
        self.in_data_pin.is_waiting = True
        self.in_trigger_pin.is_waiting = False
        super()._trigger(engine)


    def call(self, engine: "Engine") -> None:
        if len(self.in_data_pin.msgs):
            self.in_data_pin.is_waiting = False
            self.in_trigger_pin.is_waiting = True
        super().call(engine)
