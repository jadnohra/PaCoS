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
        return '{}-{}-({})'.format(self.state, self.health_rate,
                                 self.health_latency)

    def call(self, engine: "Engine") -> None:
        self.state = 'ACTIVE'
        if len(self.in_trigger_pin.msgs):
            self.in_trigger_pin.msgs.clear()
            self.health_rate = 'OK'
            if len(self.in_data_pin.msgs) == 0:
                self.health_rate = 'STARVING'
            elif len(self.in_data_pin.msgs) > 1:
                self.health_rate = 'DROPPING'
                self.in_data_pin.msgs = self.in_data_pin.msgs[-1:]
            if len(self.in_data_pin.msgs) > 0:
                data_msg = self.in_data_pin.msgs[0]
                self.health_latency = engine.compare_stamps(
                                            engine.get_stamp(),
                                            data_msg.stamps[0])
                self.in_data_pin.msgs.clear()
            print('*', self.health)
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
    engine.add_impulse(timer)
    engine.add_impulse(data)
    engine.run(max_frames=5)


def run_besteffort_inverted():
    # TODO express lagging, here, always lagging, after first starvation!
    engine = IsmEngine()
    actor = BestEffortActor()
    timer = PeriodicImpulse(lambda _: Message(actor.in_trigger_pin, 'timer'),
                            0, 0)
    data = PeriodicImpulse(lambda _: Message(actor.in_data_pin, 'data'), 0, 0)
    engine.add_actor(actor)
    engine.add_impulse(data)
    engine.add_impulse(timer)
    engine.run(max_frames=5)

def run_besteffort_starving():
    engine = IsmEngine()
    actor = BestEffortActor()
    timer = PeriodicImpulse(lambda _: Message(actor.in_trigger_pin, 'timer'),
                            0, 1)
    data = PeriodicImpulse(lambda _: Message(actor.in_data_pin, 'data'), 7, 1)
    engine.add_actor(actor)
    engine.add_impulse(data)
    engine.add_impulse(timer)
    engine.run(max_frames=15)


def run_besteffort_random():
    engine = IsmEngine()
    actor = BestEffortActor()
    timer = PeriodicImpulse(lambda _: Message(actor.in_trigger_pin, 'timer'),
                            1, 1)
    data = FuzzyPeriodicImpulse(lambda _: Message(actor.in_data_pin, 'data'),
                                4, 0, 3, random.Random(0))
    engine.add_actor(actor)
    engine.add_impulse(data)
    engine.add_impulse(timer)
    engine.run(max_frames=20)


def run_besteffort():
    print('=== perfect ===')
    #run_besteffort_perfect()
    print('=== inverted ===')
    run_besteffort_inverted()
    print('=== starving ===')
    #run_besteffort_starving()
    print('=== random ===')
    #run_besteffort_random()
