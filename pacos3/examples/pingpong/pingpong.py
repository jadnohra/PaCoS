import sys
from typing import List
from pacos3.interfaces import Address, Token, Time, CallMode
from pacos3.actor import Actor
from pacos3.mock.procedures import NullProc, IdentProc
from pacos3.mock.sources import SingleShotSource
from pacos3.manual_clock import ManualClock
from pacos3.processor import Processor



class PingActor(Actor):
    def __init__(self, ping_count: int):
        self._pings_left = ping_count
        pin = NullProc('trigger', notif_func = self._on_trigger)
        super().__init__('ping', [pin])

    def _on_trigger(self, _1, _2, time: Time) -> List[Token]:
        if self._pings_left > 0:
            print(self._pings_left)
            self._pings_left = self._pings_left - 1
            return [self.create_token(time)]
        return []

    def create_token(self, time: Time) -> Token:
        return Token(Address(actor='pong'), None, time)

class PongActor(Actor):
    def __init__(self):
        pin = IdentProc('trigger', Address(actor='ping'))
        super().__init__('pong', [pin])


def run():
    print('=== pingpong ===')
    processor = Processor()
    ping_actor = PingActor(3)
    processor.add_actor(ping_actor)
    processor.add_actor(PongActor())
    processor.add_source(SingleShotSource([ping_actor.create_token(0)]))
    clock = ManualClock()
    call_mode = CallMode(use_proc_state=False)
    while True:
        step_result = processor.step(clock.time, [], call_mode)
        if step_result.interval > 0:
            clock.advance(step_result.interval)
        else:
            break


if __name__ == "__main__":
    run()
