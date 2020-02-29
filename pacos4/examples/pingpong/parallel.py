import sys
from typing import List
import logging
import argparse
from pacos4.token import Address, Token
from pacos4.call import CallArg, Call, CallResult
from pacos4.procedure import Procedure, IProcessorAPI
from pacos4.actor import Actor
from pacos4.processor import Processor, ProcessorConfig
from pacos4.time import repr_time
from pacos4.board import Board


class PingActor(Actor):
    def __init__(self, ping_count: int):
        self._pings_left = ping_count
        super().__init__('ping', [PingTriggerProc(self)])


class PingTriggerProc(Procedure):
    def __init__(self, actor: "PingActor"):
        super().__init__('trigger')
        self._actor = actor

    def call(self, _, __, proxor: IProcessorAPI) -> CallResult:
        if self._actor._pings_left > 0:
            logging.warning('PING - time: {}, pings_left: {}'.format(
                            repr_time(proxor.time), self._actor._pings_left))
            self._actor._pings_left = self._actor._pings_left - 1
            return CallResult(1, [self.create_call()])
        return proxor.exit()
    
    @staticmethod
    def create_call() -> Token:
        return Call(None, Address(processor='B', actor='pong'))


class PongTriggerProc(Procedure):
    def __init__(self):
        super().__init__('trigger')

    def call(self, arg: CallArg, _,  proxor: IProcessorAPI) -> CallResult:
        logging.warning('PONG - time: {}, pong'.format(repr_time(proxor.time)))
        out_call = Call(arg, Address(processor='A', actor='ping'))
        return CallResult(1, [out_call])


class PongActor(Actor):
    def __init__(self):
        super().__init__('pong', [PongTriggerProc()])


def ping_main(processor: Processor) -> List[Address]:
    processor.add_actor(PingActor(3))
    processor.put_calls([Call(None, Address(actor='ping'))])


def pong_main(processor: Processor) -> List[Address]:
    processor.add_actor(PongActor())
    return [Address(actor='pong')]
    

def run(log_lvl: str = 'WARNING'):
    print('=== pingpong-parallel ===')
    processor_configs = [
        ProcessorConfig(name='A', main=ping_main, log_level=log_lvl), 
        ProcessorConfig(name='B', main=pong_main, log_level=log_lvl)
        ]
    board = Board(processor_configs)
    while not board.any_exited():
        board.step()
    board.exit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", default='WARNING')
    args = parser.parse_args(sys.argv[1:])
    logging.basicConfig(format='%(levelname)s:%(message)s',
                        level=logging.getLevelName(args.log.upper()))
    run(args.log)