import random
from .discrete_event import Message
from .discrete_event_ism import IsmEngine
from .periodic_impulses import PeriodicImpulse, FuzzyPeriodicImpulse
from .besteffort_actor import BestEffortActor


def run_besteffort_perfect():
    engine = IsmEngine()
    actor = BestEffortActor()
    timer = PeriodicImpulse(lambda _: [Message(actor.in_trigger_pin, 'timer')],
                            0, 0)
    data = PeriodicImpulse(lambda _: [Message(actor.in_data_pin, 'data')],
                           0, 0)
    engine.add_actor(actor)
    engine.add_impulse(data)
    engine.add_impulse(timer)
    engine.run(max_frames=5)


def run_besteffort_inverted():
    engine = IsmEngine()
    actor = BestEffortActor()
    timer = PeriodicImpulse(lambda _: [Message(actor.in_trigger_pin, 'timer')],
                            0, 0)
    data = PeriodicImpulse(lambda _: [Message(actor.in_data_pin, 'data')],
                           0, 0)
    engine.add_actor(actor)
    engine.add_impulse(timer)
    engine.add_impulse(data)
    engine.run(max_frames=5)


def run_besteffort_nondet_impulse():
    engine = IsmEngine(impulse_rand = random.Random(0))
    actor = BestEffortActor()
    timer = PeriodicImpulse(lambda _: [Message(actor.in_trigger_pin, 'timer')],
                            0, 0)
    data = PeriodicImpulse(lambda _: [Message(actor.in_data_pin, 'data')],
                           0, 0)
    engine.add_actor(actor)
    engine.add_impulse(data)
    engine.add_impulse(timer)
    engine.run(max_frames=10)


def run_besteffort_starving():
    engine = IsmEngine()
    actor = BestEffortActor()
    timer = PeriodicImpulse(lambda _: [Message(actor.in_trigger_pin, 'timer')],
                            0, 0)
    data = PeriodicImpulse(lambda _: [Message(actor.in_data_pin, 'data')],
                           3, 3)
    engine.add_actor(actor)
    engine.add_impulse(data)
    engine.add_impulse(timer)
    engine.run(max_frames=10)


def run_besteffort_dropping():
    engine = IsmEngine()
    actor = BestEffortActor()
    timer = PeriodicImpulse(lambda _: [Message(actor.in_trigger_pin, 'timer')],
                            2, 0)
    data = PeriodicImpulse(lambda _: [Message(actor.in_data_pin, 'data')],
                           0, 0)
    engine.add_actor(actor)
    engine.add_impulse(data)
    engine.add_impulse(timer)
    engine.run(max_frames=10)


def run_besteffort_fuzzy():
    engine = IsmEngine(impulse_rand = random.Random(0))
    actor = BestEffortActor()
    timer = PeriodicImpulse(lambda _: [Message(actor.in_trigger_pin, 'timer')],
                            3, 0)
    data = FuzzyPeriodicImpulse(lambda _: [Message(actor.in_data_pin, 'data')],
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
