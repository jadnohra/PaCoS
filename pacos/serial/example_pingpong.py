from typing import List
from .discrete_event import *
from .basic_pins import BasicIsmPin


class PingActor(Actor):
    def __init__(self, ping_count):
        super().__init__()
        self._pings_left = ping_count
        self.in_pin = BasicIsmPin(self, 'ping_in', waiting=False, accepting=False)
        self.out_pin = None

    @property
    def name(self) -> str:
        return 'ping'

    @property
    def pins(self) -> List[Pin]:
        return [self.in_pin]

    def _ping(self, engine: "Engine", first_time: bool) -> None:
        if self.out_pin and (first_time or len(self.in_pin.msgs)):
            if len(self.in_pin.msgs):
                for x in self.in_pin.msgs:
                    print(x.payload)
                self.in_pin.msgs.clear()
            if self._pings_left > 0:
                self._pings_left = self._pings_left - 1
                self.in_pin._is_waiting = True
                engine.push_msg(Message(self.out_pin, self.in_pin))

    def init_call(self, engine: "Engine") -> None:
        self._ping(engine, True)

    def call(self, engine: "Engine") -> None:
        self._ping(engine, False)


class PongActor(Actor):
    def __init__(self):
        super().__init__()
        self.in_pin = BasicIsmPin(self, 'pong_in', waiting=True, accepting=True)

    @property
    def name(self) -> str:
        return 'pong'

    @property
    def pins(self) -> List[Pin]:
        return [self.in_pin]

    def _pong(self, engine: "Engine") -> None:
        for msg in self.in_pin.msgs:
            print('ping')
            engine.push_msg(Message(msg.payload, 'pong'))
        self.in_pin.msgs.clear()

    def init_call(self, engine: "Engine") -> None:
        self._pong(engine)

    def call(self, engine: "Engine") -> None:
        self._pong(engine)


def run_pingpong():
    print('=== ping-pong ===')
    engine = Engine()
    ping = PingActor(3)
    pong = PongActor()
    ping.out_pin = pong.in_pin
    engine.add_actor(ping)
    engine.add_actor(pong)
    engine.run()
