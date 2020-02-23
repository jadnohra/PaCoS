from typing import List
from pacos2.interfaces import IMsgRouter, Address
from pacos2.actor import Actor
from pacos2.message import Message
from pacos2.discr_evt_engine import DiscreteEventEngine
from pacos2.mock.pins import NullPin, IdentPin
from pacos2.manual_clock import ManualClock
from pacos2.discr_policies import MsgAlwaysReadyPolicy
from pacos2.serial_topology import SerialTopology


class PingActor(Actor):
    def __init__(self, ping_count):
        self._pings_left = ping_count
        pin = NullPin('trigger', notif_func = self._on_trigger)
        super().__init__('ping', [pin])

    def _on_trigger(self, _1, _2, router: IMsgRouter) -> None:
        if self._pings_left > 0:
            self._pings_left = self._pings_left - 1
            router.route(self.create_msg())
        print(self._pings_left)

    def create_msg(self):
        pong_actor_address = Address(None, 'pong', None)
        return Message(self.address, pong_actor_address)

class PongActor(Actor):
    def __init__(self):
        ping_actor_address = Address(None, 'ping', None)
        pin = IdentPin('trigger', ping_actor_address)
        super().__init__('pong', [pin])


def run():
    print('=== ping-pong ===')
    clock = ManualClock()
    topology = SerialTopology(clock)
    engine = DiscreteEventEngine('e', msg_ready_policy=MsgAlwaysReadyPolicy())
    topology.add_engine(engine)
    ping_actor = PingActor(3)
    engine.add_actor(ping_actor)
    engine.add_actor(PongActor())
    engine.put_msg(ping_actor.create_msg())
    while True:
        interval = topology.step()
        if interval > 0:
            clock.advance(interval)
        else:
            break

if __name__ == "__main__":
    run()