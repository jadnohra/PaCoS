import sys
import logging
import argparse
from typing import List
from pacos2.interfaces import IMsgRouter, Address, IMessage
from pacos2.actor import Actor
from pacos2.message import Message
from pacos2.discr_evt_engine import DiscreteEventEngine
from pacos2.mock.pins import NullPin, IdentPin
from pacos2.discr_policies import MsgAlwaysReadyPolicy
from pacos2.msg_routers import MultiEngineRouter
from pacos2.multi_engine import MultiEngine, IMultiEngine
from pacos2.parall_context import create_parall_context
from pacos2.parall_process import ParallProcess
from pacos2.parall_wavefront_engine import ParallWavefrontEngine


class PingActor(Actor):
    def __init__(self, ping_count, pong_engine_name=None):
        self._pings_left = ping_count
        pin = NullPin('trigger', notif_func = self._on_trigger)
        super().__init__('ping', [pin])

    def _on_trigger(self, _1, _2, router: IMsgRouter) -> None:
        if self._pings_left > 0:
            print(self._pings_left)
            self._pings_left = self._pings_left - 1
            router.route(self.create_msg())

    def create_msg(self) -> IMessage:
        pong_actor_address = Address(engine='b', actor='pong')
        return Message(self.address, pong_actor_address)

class PongActor(Actor):
    def __init__(self, ping_engine_name=None):
        ping_actor_address = Address(engine=ping_engine_name, actor='ping')
        pin = IdentPin('trigger', ping_actor_address)
        super().__init__('pong', [pin])


class PingProcess(ParallProcess):
    @classmethod
    def create_multi_engine(cls) -> IMultiEngine:
        engine_a = DiscreteEventEngine(name='a', 
                                    msg_ready_policy=MsgAlwaysReadyPolicy())
        ping_actor = PingActor(3, pong_engine_name='b')
        engine_a.add_actor(ping_actor)
        multieng = MultiEngine()
        multieng.add_engine(engine_a)
        return multieng


class PongProcess(ParallProcess):
    @classmethod
    def create_multi_engine(cls) -> IMultiEngine:
        engine_b = DiscreteEventEngine(name='b', 
                                    msg_ready_policy=MsgAlwaysReadyPolicy())
        pong_actor = PongActor(ping_engine_name='a')
        engine_b.add_actor(pong_actor)
        engine_b.put_msg(PingActor(1).create_msg())
        multieng = MultiEngine()
        multieng.add_engine(engine_b)
        return multieng


def run():
    print('=== parall-pingpong ===')
    parall_engine = ParallWavefrontEngine(create_parall_context(),
                                          [PingProcess, PongProcess])
    while True:
        interval = parall_engine.step()
        if interval == 0:
            break
    parall_engine.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", default='WARNING')
    args = parser.parse_args(sys.argv[1:])
    logging.basicConfig(format='%(levelname)s:%(message)s',
                        level=logging.getLevelName(args.log.upper()))
    run()