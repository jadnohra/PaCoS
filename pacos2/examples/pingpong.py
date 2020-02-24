import sys
from typing import List
from pacos2.interfaces import IMsgRouter, Address
from pacos2.actor import Actor
from pacos2.message import Message
from pacos2.discr_evt_engine import DiscreteEventEngine
from pacos2.mock.pins import NullPin, IdentPin
from pacos2.manual_clock import ManualClock
from pacos2.discr_policies import MsgAlwaysReadyPolicy
from pacos2.serial_topology import SerialTopology
from pacos2.parall_wavefront_topology import ParallWavefrontTopology


class PingActor(Actor):
    def __init__(self, ping_count, pong_engine_name=None):
        self._pong_engine_name = pong_engine_name
        self._pings_left = ping_count
        pin = NullPin('trigger', notif_func = self._on_trigger)
        super().__init__('ping', [pin])

    def _on_trigger(self, _1, _2, router: IMsgRouter) -> None:
        if self._pings_left > 0:
            print(self._pings_left)
            self._pings_left = self._pings_left - 1
            router.route(self.create_msg())

    def create_msg(self):
        pong_actor_address = Address(engine=self._pong_engine_name, 
                                     actor='pong')
        return Message(self.address, pong_actor_address)

class PongActor(Actor):
    def __init__(self, ping_engine_name=None):
        ping_actor_address = Address(engine=ping_engine_name, actor='ping')
        pin = IdentPin('trigger', ping_actor_address)
        super().__init__('pong', [pin])


def run_serial():
    print('=== pingpong-serial ===')
    clock = ManualClock()
    topology = SerialTopology(clock)
    engine = DiscreteEventEngine(name='e', 
                                 msg_ready_policy=MsgAlwaysReadyPolicy())
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


def run_parall():
    print('=== pingpong-parall ===')
    clock = ManualClock()
    topology = ParallWavefrontTopology(clock)
    engine_a = DiscreteEventEngine(name='a', 
                                   msg_ready_policy=MsgAlwaysReadyPolicy())
    engine_b = DiscreteEventEngine(name='b', 
                                   msg_ready_policy=MsgAlwaysReadyPolicy())
    topology.add_engine(engine_a)
    topology.add_engine(engine_b)
    ping_actor = PingActor(3, pong_engine_name=engine_b.name)
    engine_a.add_actor(ping_actor)
    engine_b.add_actor(PongActor(ping_engine_name=engine_a.name))
    engine_b.put_msg(ping_actor.create_msg())
    while True:
        interval = topology.step()
        if interval > 0:
            clock.advance(interval)
        else:
            break

if __name__ == "__main__":
    if any([x in sys.argv for x in ['--all', '--serial']]):
        run_serial()
    if any([x in sys.argv for x in ['--all', '--parall']]):
        run_parall()