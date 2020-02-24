import sys
import argparse
import logging
from typing import List
from pacos2.mock.best_effort_actor import BestEffortActor
from pacos2.mock.impulses import PeriodicImpulse, IDiscreteImpulse, IClock
from pacos2.message import Message, Address
from pacos2.impul_discr_evt_engine import (
    ImpulsiveDiscreteEventEngine, DiscreteEventEngine)
from pacos2.manual_clock import ManualClock
from pacos2.discr_policies import MsgAlwaysReadyPolicy
from pacos2.msg_routers import SingleEngineRouter


def _gen_trigger_msgs(_: IDiscreteImpulse, clock: IClock) -> Message:
    return [Message(None, Address(actor='a', pin='trigger'), time=clock.time)]


def _gen_data_msgs(_: IDiscreteImpulse, clock: IClock) -> Message:
   return [Message(None, Address(actor='a', pin='data'), time=clock.time)]


def run():
    print('=== besteffort-ignore-state ===')
    engine = ImpulsiveDiscreteEventEngine(
                DiscreteEventEngine(msg_ready_policy=MsgAlwaysReadyPolicy()))
    actor = BestEffortActor('a')
    engine.discr_engine.add_actor(actor)
    engine.add_impulse(PeriodicImpulse(_gen_data_msgs))
    engine.add_impulse(PeriodicImpulse(_gen_trigger_msgs))
    router = SingleEngineRouter(ManualClock(), engine)
    for _ in range(5):
        interval = engine.step(router)
        if interval > 0:
            router.clock.advance(interval)
        else:
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", default='WARNING')
    args = parser.parse_args(sys.argv[1:])
    logging.basicConfig(format='%(levelname)s:%(message)s',
                        level=logging.getLevelName(args.log.upper()))
    run()
