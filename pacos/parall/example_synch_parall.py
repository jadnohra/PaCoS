import random
from pacos.serial.discrete_event import Message
from pacos.serial.periodic_impulses import PeriodicImpulse, FuzzyPeriodicImpulse
from pacos.serial.besteffort_actor import BestEffortActor, SynchronizedBestEffortActor
from .discrete_event_ism_parall import IsmEngineParall
from .parall_util import run_parall


def run_synch_unsynch():
    engine1 = IsmEngineParall(synchronized=False, id='e1')
    engine2 = IsmEngineParall(synchronized=False, id='e2')
    actor2 = BestEffortActor(name='A2')
    engine2.add_actor(actor2)
    actor1 = BestEffortActor(name='A1', out_pin=actor2.in_data_pin)
    engine1.add_actor(actor1)
    timer1 = PeriodicImpulse(lambda _: [Message(actor1.in_trigger_pin, 'timer')],
                             0, 0)
    timer2 = PeriodicImpulse(lambda _: [Message(actor2.in_trigger_pin, 'timer')],
                             0, 0)
    data = PeriodicImpulse(lambda _: [Message(actor1.in_data_pin, 'data')],
                           0, 0)
    
    engine1.add_impulse(data)
    engine1.add_impulse(timer1)
    engine2.add_impulse(timer2)
    run_parall([(engine1, {'max_frames':5}),
                 (engine2, {'max_frames':5})
                ])


def run_synch_synch():
    engine1 = IsmEngineParall(synchronized=True, id='e1')
    engine2 = IsmEngineParall(synchronized=True, id='e2')
    actor2 = BestEffortActor(name='A2')
    engine2.add_actor(actor2)
    actor1 = BestEffortActor(name='A1', out_pin=actor2.in_data_pin)
    engine1.add_actor(actor1)
    timer1 = PeriodicImpulse(lambda _: [Message(actor1.in_trigger_pin, 'timer')],
                             0, 0)
    timer2 = PeriodicImpulse(lambda _: [Message(actor2.in_trigger_pin, 'timer')],
                             0, 0)
    data = PeriodicImpulse(lambda _: [Message(actor1.in_data_pin, 'data')],
                           0, 0)
    
    engine1.add_impulse(data)
    engine1.add_impulse(timer1)
    engine2.add_impulse(timer2)
    run_parall([(engine1, {'max_frames':5}),
                 (engine2, {'max_frames':5})
                ])



def run_synch_parall():
    print('=== unsynch-parall ===')
    run_synch_unsynch()
    print('=== synch-parall ===')
    run_synch_synch()
