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
        return '{}-{}-{}'.format(self.state, self.health_rate,
                                 self.health_latency)

    def call(self, engine: "Engine") -> None:
        self.state = 'ACTIVE'
        if len(self.in_trigger_pin.msgs):
            self.in_trigger_pin.msgs.clear()
            self.health_rate = 'OK'
            if len(self.in_data_pin.msgs) == 0:
                self.health_rate = 'STARVING'
                return
            elif len(self.in_data_pin.msgs) > 1:
                self.health_rate = 'DROPPING'
                self.in_data_pin.msgs = self.in_data_pin.msgs[-1:]
            data_msg = self.in_data_pin.msgs[0]
            # TODO check health latency
            self.in_data_pin.msgs.clear()
        print(self.health)

    def _call(self, engine: "Engine") -> None:
        #print(len(self.in_trigger_pin.msgs), len(self.in_data_pin.msgs))
        starving = len(self.in_trigger_pin.msgs) - len(self.in_data_pin.msgs)
        if starving > 0:
            print('starving by {}'.format(starving))
        overdriven = ((len(self.in_data_pin.msgs)
                       - len(self.in_trigger_pin.msgs)) - 1)
        if overdriven > 0:
            print('overdriven by {}'.format(overdriven))
        if len(self.in_trigger_pin.msgs):
            self.in_trigger_pin.msgs.clear()
            self.in_data_pin.msgs.clear()
            self.triggered_count = self.triggered_count + 1
            #print('triggered', self.triggered_count)
        else:
            # print('not triggered', self.triggered_count)
            pass



def run_besteffort_perfect():
    engine = IsmEngine()
    actor = BestEffortActor()
    timer = PeriodicImpulse(Message(actor.in_trigger_pin, 'timer'), 0, 1)
    data = PeriodicImpulse(Message(actor.in_data_pin, 'data'), 0, 0)
    engine.add_actor(actor)
    engine.add_impulse(timer)
    engine.add_impulse(data)
    engine.run()


def run_besteffort_inverted():
    # TODO express lagging, here, always lagging, after first starvation!
    engine = IsmEngine()
    actor = BestEffortActor()
    timer = PeriodicImpulse(Message(actor.in_trigger_pin, 'timer'), 0, 0)
    data = PeriodicImpulse(Message(actor.in_data_pin, 'data'), 0, 1)
    engine.add_actor(actor)
    engine.add_impulse(timer)
    engine.add_impulse(data)
    engine.run()

def run_besteffort_starving():
    engine = IsmEngine()
    actor = BestEffortActor()
    timer = PeriodicImpulse(Message(actor.in_trigger_pin, 'timer'), 0, 1)
    data = PeriodicImpulse(Message(actor.in_data_pin, 'data'), 7, 1)
    engine.add_actor(actor)
    engine.add_impulse(data)
    engine.add_impulse(timer)
    engine.run()


def run_besteffort_random():
    engine = IsmEngine()
    actor = BestEffortActor()
    timer = PeriodicImpulse(Message(actor.in_trigger_pin, 'timer'), 1, 1)
    data = FuzzyPeriodicImpulse(Message(actor.in_data_pin, 'data'), 4, 0, 3,
                                random.Random(0))
    engine.add_actor(actor)
    engine.add_impulse(data)
    engine.add_impulse(timer)
    engine.run()


def run_besteffort():
    print('=== perfect ===')
    #run_besteffort_perfect()
    print('=== inverted ===')
    #run_besteffort_inverted()
    print('=== starving ===')
    run_besteffort_starving()
    print('=== random ===')
    #run_besteffort_random()
