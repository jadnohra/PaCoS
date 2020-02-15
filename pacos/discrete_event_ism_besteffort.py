import random
import copy
from typing import List
from .discrete_event_ism import *


class BasicPin(IsmPin):
    def __init__(self, actor: Actor, name: str, waiting=False, accepting=False):
        super().__init__()
        self._name = name
        self._is_waiting = waiting
        self._is_accepting = accepting
        self._actor = actor
        self.msgs = []

    @property
    def name(self) -> str:
        return self._name

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


class BestEffortActor(Actor):
    def __init__(self):
        super().__init__()
        self.in_data_pin = BasicPin(self, 'data', waiting=True, accepting=True)
        self.in_trigger_pin = BasicPin(self, 'trigger', waiting=True,
                                       accepting=True)
        self.triggered_count = 0

    @property
    def name(self) -> str:
        return 'be'

    @property
    def pins(self) -> List[Pin]:
        return [self.in_data_pin, self.in_trigger_pin]

    def call(self, engine: "Engine") -> None:
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


class PeriodicImpulse(Impulse):
    def __init__(self, msg: Message, period=0, first_ticks_left=0):
        self.msg = msg
        self.period = period
        self.ticks_left = first_ticks_left

    def call(self, engine: "IsmEngine"):
        if self.ticks_left <= 0:
            self.ticks_left = self.period
            engine.add_msg(copy.deepcopy(self.msg))
        else:
            self.ticks_left = self.ticks_left - 1



class RandomPeriodicImpulse(Impulse):
    def __init__(self, msg: Message, period, first_ticks_left, variance, rand):
        self.msg = msg
        self.period = period
        self.variance = variance
        self.rand = rand
        self.ticks_left = first_ticks_left

    def call(self, engine: "IsmEngine"):
        if self.ticks_left <= 0:
            variance = self.rand.randint(-self.variance, self.variance)
            self.ticks_left = self.period + variance
            engine.add_msg(copy.deepcopy(self.msg))
        else:
            self.ticks_left = self.ticks_left - 1


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
    data = RandomPeriodicImpulse(Message(actor.in_data_pin, 'data'), 4, 0, 3,
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
