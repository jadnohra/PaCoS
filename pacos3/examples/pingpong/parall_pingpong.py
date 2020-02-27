import sys
from typing import List
import logging
import argparse
from pacos3.interfaces import Address, Token, Time, CallMode
from pacos3.actor import Actor
from pacos3.mock.procedures import NullProc, IdentProc
from pacos3.mock.sources import SingleShotSource
from pacos3.manual_clock import ManualClock
from pacos3.processor import Processor
from pacos3.process import Process
from pacos3.wavefront_board import Board, ProcessConfig


class PingActor(Actor):
    def __init__(self, ping_count: int):
        self._pings_left = ping_count
        self._pin = NullProc('trigger', notif_func = self._on_trigger)
        super().__init__('ping', [self._pin])

    def _on_trigger(self, _1, _2, time: Time) -> List[Token]:
        if self._pings_left > 0:
            logging.warning('time: {}, pings_left: {}'.format(time, self._pings_left))
            self._pings_left = self._pings_left - 1
            return [self.create_token(time)]
        self._pin.set_processing_time(0)
        return []

    @staticmethod
    def create_token(time: Time) -> Token:
        return Token(Address(processor='B', actor='pong'), None, time)


class PongActor(Actor):
    def __init__(self):
        pin = IdentProc('trigger', Address(processor='A', actor='ping'))
        super().__init__('pong', [pin])


def ping_main(processor: Processor) -> None:
    processor.add_actor(PingActor(3))
    processor.add_source(SingleShotSource([PingActor.create_token(0)]))


def pong_main(processor: Processor) -> None:
    processor.add_actor(PongActor())
    

def run(log_level: str = 'WARNING'):
    print('=== parall-pingpong ===')
    board = Board([ProcessConfig('A', ping_main, log_level=log_level), 
                   ProcessConfig('B', pong_main, log_level=log_level)])
    while True:
        interval = board.step()
        if not board.has_tokens() and interval == 0:
            break
    board.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", default='WARNING')
    args = parser.parse_args(sys.argv[1:])
    logging.basicConfig(format='%(levelname)s:%(message)s',
                        level=logging.getLevelName(args.log.upper()))
    run(args.log)