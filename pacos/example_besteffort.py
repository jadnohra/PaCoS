import random
import copy
from typing import List
from .discrete_event import Actor, Pin, Message
from .discrete_event_ism import IsmEngine
from .periodic_impulses import PeriodicImpulse, FuzzyPeriodicImpulse
from .basic_pins import BasicIsmPin



class BestEffortActor(Actor):
    def __init__(self):
        super().__init__()
        self.in_data_pin = BasicIsmPin(self, 'data', waiting=True,
                                       accepting=True)
        self.in_trigger_pin = BasicIsmPin(self, 'trigger', waiting=True,
                                          accepting=True)
        self.triggered_count = 0
        self.state = 'INIT'
        self.health_rate = 'N/A'
        self.health_latency = 'N/A'

    @property
    def name(self) -> str:
        return 'be'

    @property
    def pins(self) -> List[Pin]:
        return [self.in_data_pin, self.in_trigger_pin]

    @property
    def health(self) -> str:
        if self.state == 'ACTIVE':
            return '{}-LAT({})'.format(self.health_rate, self.health_latency)
        else:
            return self.state

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
                data_msg = self.in_data_pin.msgs[0]
                self.health_latency = engine.compare_stamps(
                                            engine.get_stamp(),
                                            data_msg.stamps[0])
                self.in_data_pin.msgs.clear()
            print('*', engine.frame,  self.health)
        else:
            pass
            # print(self.health)


def run_besteffort_perfect():
    engine = IsmEngine()
    actor = BestEffortActor()
    timer = PeriodicImpulse(lambda _: Message(actor.in_trigger_pin, 'timer'),
                            0, 0)
    data = PeriodicImpulse(lambda _: Message(actor.in_data_pin, 'data'), 0, 0)
    engine.add_actor(actor)
    engine.add_impulse(data)
    engine.add_impulse(timer)
    engine.run(max_frames=5)


def run_besteffort_inverted():
    engine = IsmEngine()
    actor = BestEffortActor()
    timer = PeriodicImpulse(lambda _: Message(actor.in_trigger_pin, 'timer'),
                            0, 0)
    data = PeriodicImpulse(lambda _: Message(actor.in_data_pin, 'data'), 0, 0)
    engine.add_actor(actor)
    engine.add_impulse(timer)
    engine.add_impulse(data)
    engine.run(max_frames=5)


def run_besteffort_nondet_impulse():
    engine = IsmEngine(impulse_rand = random.Random(0))
    actor = BestEffortActor()
    timer = PeriodicImpulse(lambda _: Message(actor.in_trigger_pin, 'timer'),
                            0, 0)
    data = PeriodicImpulse(lambda _: Message(actor.in_data_pin, 'data'), 0, 0)
    engine.add_actor(actor)
    engine.add_impulse(data)
    engine.add_impulse(timer)
    engine.run(max_frames=10)


def run_besteffort_starving():
    engine = IsmEngine()
    actor = BestEffortActor()
    timer = PeriodicImpulse(lambda _: Message(actor.in_trigger_pin, 'timer'),
                            0, 0)
    data = PeriodicImpulse(lambda _: Message(actor.in_data_pin, 'data'), 3, 3)
    engine.add_actor(actor)
    engine.add_impulse(data)
    engine.add_impulse(timer)
    engine.run(max_frames=10)


def run_besteffort_dropping():
    engine = IsmEngine()
    actor = BestEffortActor()
    timer = PeriodicImpulse(lambda _: Message(actor.in_trigger_pin, 'timer'),
                            2, 0)
    data = PeriodicImpulse(lambda _: Message(actor.in_data_pin, 'data'), 0, 0)
    engine.add_actor(actor)
    engine.add_impulse(data)
    engine.add_impulse(timer)
    engine.run(max_frames=10)


def run_besteffort_fuzzy():
    engine = IsmEngine(impulse_rand = random.Random(0))
    actor = BestEffortActor()
    timer = PeriodicImpulse(lambda _: Message(actor.in_trigger_pin, 'timer'),
                            3, 0)
    data = FuzzyPeriodicImpulse(lambda _: Message(actor.in_data_pin, 'data'),
                                3, 0, 3, random.Random(0))
    engine.add_actor(actor)
    engine.add_impulse(data)
    engine.add_impulse(timer)
    engine.run(max_frames=30)


def run_besteffort():
    print('=== perfect ===')
    run_besteffort_perfect()
    print('=== inverted ===')
    run_besteffort_inverted()
    print('=== nondet-impulse ===')
    run_besteffort_nondet_impulse()
    print('=== starving ===')
    run_besteffort_starving()
    print('=== dropping ===')
    run_besteffort_dropping()
    print('=== fuzzy ===')
    run_besteffort_fuzzy()