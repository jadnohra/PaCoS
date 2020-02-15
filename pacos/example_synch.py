import random
from .discrete_event import Message
from .discrete_event_ism import IsmEngine
from .periodic_impulses import PeriodicImpulse, FuzzyPeriodicImpulse
from .besteffort_actor import BestEffortActor




def run_synch_unsynch():
    engine = IsmEngine()
    actor2 = BestEffortActor(name='A2')
    actor1 = BestEffortActor(name='A1', out_pin=actor2.in_data_pin)
    timer = PeriodicImpulse(lambda _: [
                                Message(actor1.in_trigger_pin, 'timer'),
                                Message(actor2.in_trigger_pin, 'timer')],
                            0, 0)
    data = PeriodicImpulse(lambda _: [Message(actor1.in_data_pin, 'data')],
                           0, 0)
    engine.add_actor(actor1)
    engine.add_actor(actor2)
    engine.add_impulse(data)
    engine.add_impulse(timer)
    engine.run(max_frames=5)


def run_synch():
    print('=== unsync ===')
    run_synch_unsynch()
