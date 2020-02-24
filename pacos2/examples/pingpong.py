import sys
from typing import List
from pacos2.interfaces import IMsgRouter, Address, IMessage
from pacos2.actor import Actor
from pacos2.message import Message
from pacos2.discr_evt_engine import DiscreteEventEngine
from pacos2.mock.pins import NullPin, IdentPin
from pacos2.manual_clock import ManualClock
from pacos2.discr_policies import MsgAlwaysReadyPolicy
from pacos2.msg_routers import SingleEngineRouter, MultiEngineRouter


class PingActor(Actor):
    def __init__(self, ping_count):
        self._pings_left = ping_count
        pin = NullPin('trigger', notif_func = self._on_trigger)
        super().__init__('ping', [pin])

    def _on_trigger(self, _1, _2, router: IMsgRouter) -> None:
        if self._pings_left > 0:
            print(self._pings_left)
            self._pings_left = self._pings_left - 1
            router.route(self.create_msg())

    def create_msg(self) -> IMessage:
        return Message(self.address, Address(actor='pong'))

class PongActor(Actor):
    def __init__(self):
        pin = IdentPin('trigger', Address(actor='ping'))
        super().__init__('pong', [pin])


def run():
    print('=== pingpong ===')
    engine = DiscreteEventEngine(msg_ready_policy=MsgAlwaysReadyPolicy())
    ping_actor = PingActor(3)
    engine.add_actor(ping_actor)
    engine.add_actor(PongActor())
    engine.put_msg(ping_actor.create_msg())
    router = SingleEngineRouter(ManualClock(), engine)
    while True:
        interval = engine.step(router)
        if interval > 0:
            router.clock.advance(interval)
        else:
            break


if __name__ == "__main__":
    run()
