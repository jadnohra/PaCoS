from typing import List
import random
from .discrete_event_ism import *


class BasicPin(IsmPin):
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


class BestEffortActor(Actor):
    def __init__(self):
        super().__init__()
        self.in_data_pin = BasicPin(self, waiting=True, accepting=True)
        self.in_trigger_pin = BasicPin(self, waiting=True, accepting=True)
        self.triggered_count = 0

    @property
    def pins(self) -> List[Pin]:
        return [self.in_data_pin, self.in_trigger_pin]

    def call(self, engine: "Engine") -> None:
        #print(len(self.in_trigger_pin.msgs), len(self.in_data_pin.msgs))
        overtriggered = len(self.in_trigger_pin.msgs) - 1
        if overtriggered > 0:
            print('overtriggered by {}'.format(overtriggered))
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
    def __init__(self, msg: Message, period=1, offset=0):
        self.msg = msg
        self.period = period
        self.ticks_left = offset + 1

    def call(self, engine: "IsmEngine"):
        self.ticks_left = self.ticks_left - 1
        if self.ticks_left <= 0:
            self.ticks_left = self.period
            engine.add_msg(self.msg)


class RandomPeriodicImpulse(Impulse):
    def __init__(self, msg: Message, period, offset, variance, rand):
        self.msg = msg
        self.period = period
        self.variance = variance
        self.rand = rand
        self.ticks_left = offset + 1

    def call(self, engine: "IsmEngine"):
        self.ticks_left = self.ticks_left - 1
        if self.ticks_left == 0:
            variance = self.rand.randint(-self.variance, self.variance)
            self.ticks_left = self.period + variance
            engine.add_msg(self.msg)


def run_besteffort_perfect():
    engine = IsmEngine()
    actor = BestEffortActor()
    timer = PeriodicImpulse(Message(actor.in_trigger_pin, 'timer'), 2, 1)
    data = PeriodicImpulse(Message(actor.in_data_pin, 'data'), 2, 0)
    engine.add_actor(actor)
    engine.add_impulse(timer)
    engine.add_impulse(data)
    engine.run(max_steps=30)


def run_besteffort_inverted():
    # TODO express lagging, here, always lagging, after first starvation!
    engine = IsmEngine()
    actor = BestEffortActor()
    timer = PeriodicImpulse(Message(actor.in_trigger_pin, 'timer'), 2, 0)
    data = PeriodicImpulse(Message(actor.in_data_pin, 'data'), 2, 1)
    engine.add_actor(actor)
    engine.add_impulse(timer)
    engine.add_impulse(data)
    engine.run(max_steps=30)


def run_besteffort_random():
    engine = IsmEngine()
    actor = BestEffortActor()
    timer = PeriodicImpulse(Message(actor.in_trigger_pin, 'timer'), 4, 1)
    data = RandomPeriodicImpulse(Message(actor.in_data_pin, 'data'), 4, 0, 2,
                                 random.Random(0))
    engine.add_actor(actor)
    engine.add_impulse(data)
    engine.add_impulse(timer)
    engine.run(max_steps=100)


def run_besteffort():
    print(' === perfect ===')
    run_besteffort_perfect()
    print(' === inverted ===')
    run_besteffort_inverted()
    print(' === random ===')
    run_besteffort_random()
