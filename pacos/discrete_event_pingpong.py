from typing import List
from .discrete_event import *


class BasicPin(Pin):
    def __init__(self, actor: Actor, waiting=False, accepting=False):
        super().__init__()
        self._is_waiting = waiting
        self._is_accepting = accepting
        self._actor = actor
        self.msgs = []

    @property
    def is_waiting(self) -> bool:
        return self._is_waiting

    @property
    def actor(self) -> "Actor":
        return self._actor

    @property
    def is_accepting(self) -> bool:
        return self._is_accepting

    def accept(self, msg: Message):
        if not self._is_waiting:
            print('Dropped message!')
            return
        self.msgs.append(msg)


class PingActor(Actor):
    def __init__(self, ping_count):
        super().__init__()
        self._pings_left = ping_count
        self.in_pin = BasicPin(self, waiting=False, accepting=False)
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
                engine.add_msg(Message(self.out_pin, self.in_pin))

    def init_call(self, engine: "Engine") -> None:
        self._ping(engine, True)

    def call(self, engine: "Engine") -> None:
        self._ping(engine, False)


class PongActor(Actor):
    def __init__(self):
        super().__init__()
        self.in_pin = BasicPin(self, waiting=True, accepting=True)

    @property
    def name(self) -> str:
        return 'pong'

    @property
    def pins(self) -> List[Pin]:
        return [self.in_pin]

    def _pong(self, engine: "Engine") -> None:
        for msg in self.in_pin.msgs:
            print('pinged')
            engine.add_msg(Message(msg.payload, 'ponged'))
        self.in_pin.msgs.clear()

    def init_call(self, engine: "Engine") -> None:
        self._pong(engine)

    def call(self, engine: "Engine") -> None:
        self._pong(engine)


def run_pingpong():
    engine = Engine()
    ping = PingActor(3)
    pong = PongActor()
    ping.out_pin = pong.in_pin
    engine.add_actor(ping)
    engine.add_actor(pong)
    engine.run()
