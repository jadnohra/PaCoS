import sys
from typing import List
import logging
import argparse
from pacos3.interfaces import Address, Token, Time, ProcState, CallResult
from pacos3.procedure import Procedure
from pacos3.actor import Actor
from pacos3.mock.sources import SingleShotSource
from pacos3.manual_clock import ManualClock
from pacos3.processor import Processor, ProcessorConfig
from pacos3.wavefront_board import Board



class PingActor(Actor):
    def __init__(self, ping_count: int):
        self._pings_left = ping_count
        super().__init__('ping', [PingTriggerProc(self)])


class PingTriggerProc(Procedure):
    def __init__(self, actor: "PingActor"):
        super().__init__('trigger', ProcState.OPEN)
        self._actor = actor

    def call(self, token: Token, time: Time) -> CallResult:
        if self._actor._pings_left > 0:
            logging.warning('time: {}, pings_left: {}'
                            .format(time, self._actor._pings_left))
            self._actor._pings_left = self._actor._pings_left - 1
            return CallResult(1, [self.create_token(time)])
        return CallResult()
    
    @staticmethod
    def create_token(time: Time) -> Token:
        return Token(Address(processor='B', actor='pong'), None, time)


class PongTriggerProc(Procedure):
    def __init__(self):
        super().__init__('trigger', ProcState.OPEN)

    def call(self, token: Token, time: Time) -> CallResult:
        out_token = token.forward_target(
                                    Address(processor='A', actor='ping'), time)
        return CallResult(1, [out_token])


class PongActor(Actor):
    def __init__(self):
        super().__init__('pong', [PongTriggerProc()])


def ping_main(processor: Processor) -> None:
    processor.add_actor(PingActor(3))
    processor.add_source(SingleShotSource([PingTriggerProc.create_token(0)]))


def pong_main(processor: Processor) -> None:
    processor.add_actor(PongActor())
    

def run(log_level: str = 'WARNING'):
    print('=== pingpong-parallel ===')
    board = Board([ProcessorConfig(name='A', main=ping_main, 
                                   log_level=log_level), 
                   ProcessorConfig(name='B', main=pong_main, 
                                   log_level=log_level)])
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