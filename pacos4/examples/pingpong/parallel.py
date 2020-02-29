import sys
from typing import List
import logging
import argparse
from pacos4.time import Time, repr_time
from pacos4.interfaces import Address, Token, ProcState, CallResult
from pacos4.procedure import Procedure
from pacos4.actor import Actor
from pacos4.processor import Processor, ProcessorConfig, IProcessorAPI
from pacos4.board import Board



class PingActor(Actor):
    def __init__(self, ping_count: int):
        self._pings_left = ping_count
        super().__init__('ping', [PingTriggerProc(self)])


class PingTriggerProc(Procedure):
    def __init__(self, actor: "PingActor"):
        super().__init__('trigger', ProcState.OPEN)
        self._actor = actor

    def call(self, _: Token, proc: IProcessorAPI) -> CallResult:
        if self._actor._pings_left > 0:
            logging.warning('time: {}, pings_left: {}'
                            .format(repr_time(proc.time), 
                            self._actor._pings_left))
            self._actor._pings_left = self._actor._pings_left - 1
            # TODO: no permanent sources, exit when no work
            # period sources reinsert themselves when triggerd
            # no sources, just triggers
            return proc.wait(CallResult(1, [self.create_token()]))
        return proc.exit()
    
    @staticmethod
    def create_token() -> Token:
        return Token(Address(processor='B', actor='pong'), None)


class PongTriggerProc(Procedure):
    def __init__(self):
        super().__init__('trigger', ProcState.OPEN)

    def call(self, token: Token, proc: IProcessorAPI) -> CallResult:
        out_token = None
        if token is not None:
            logging.warning('time: {}, pong'.format(repr_time(proc.time)))
            out_token = token.forward_target(Address(processor='A', actor='ping'))
        return proc.wait(CallResult(1, [out_token] if out_token else []))


class PongActor(Actor):
    def __init__(self):
        super().__init__('pong', [PongTriggerProc()])


def ping_main(processor: Processor) -> List[Address]:
    processor.add_actor(PingActor(3))
    return [Address(actor='ping')]


def pong_main(processor: Processor) -> List[Address]:
    processor.add_actor(PongActor())
    return [Address(actor='pong')]
    

def run(log_level: str = 'WARNING'):
    print('=== pingpong-parallel ===')
    board = Board([ProcessorConfig(name='A', main=ping_main, 
                                   log_level=log_level), 
                   ProcessorConfig(name='B', main=pong_main, 
                                   log_level='INFO')])
    while not board.any_exited:
        board.step()
    board.exit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", default='WARNING')
    args = parser.parse_args(sys.argv[1:])
    logging.basicConfig(format='%(levelname)s:%(message)s',
                        level=logging.getLevelName(args.log.upper()))
    run(args.log)