import sys
from typing import List, Any
import logging
import argparse
import time
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
        if self._actor._pings_left <= 0:
            return proxor.exit()
        logging.warning('PING - time: {}, pings_left: {}'.format(
                        repr_time(proxor.time), self._actor._pings_left))
        self._actor._pings_left = self._actor._pings_left - 1
        return CallResult(5, [self.create_call()])
        
    @staticmethod
    def create_call() -> Token:
        return Call(None, Address(processor='B', actor='pong'))


class PongTriggerProc(Procedure):
    def __init__(self):
        super().__init__('trigger')

    def call(self, arg: CallArg, _,  proxor: IProcessorAPI) -> CallResult:
        logging.warning('PONG - time: {}, pong'.format(repr_time(proxor.time)))
        # Note that busy waiting still happens even though the simulation
        # hardware of the pong agent is very slow (due to the sleep below)
        time.sleep(0.2)
        out_call = Call(arg, Address(processor='A', actor='ping'))
        return CallResult(1, [out_call])


class PongActor(Actor):
    def __init__(self):
        super().__init__('pong', [PongTriggerProc()])


def ping_main(processor: Processor) -> None:
    processor.add_actor(PingActor(3))
    processor.put_calls([Call(None, Address(actor='ping'))])


def pong_main(processor: Processor) -> None:
    processor.add_actor(PongActor())
    return [Address(actor='pong')]
    

def run(log_lvl: str = 'WARNING'):
    print('=== pingpong-parallel-slow_sim_hw ===')
    processor_configs = [
        ProcessorConfig(name='A', main=ping_main, log_level=log_lvl), 
        ProcessorConfig(name='B', main=pong_main, log_level='INFO')
        ]
    board = Board(processor_configs)
    while not board.any_exited():
        board.step()
    board.exit()


def description() -> str:
    return \
    """
    The pingpong protocol is race-condition free by design.
    The only challenge when running it in simulation is that the simulation 
     hardware may be different.
    On non-simulation hardware, the pong agent busy waits 4 times, 
     because the ping calculation takes 5 cycles.
    This behavior is faithfully reproduced on simulation hardware, 
     even though the pong simulation hardware is slower than the non-simulated
     one (emulated using time.sleep).
    """


def process_args() -> Any:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--log", default='WARNING')
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                        help=description())
    args = parser.parse_args(sys.argv[1:])
    logging.basicConfig(format='%(levelname)s:%(message)s',
                        level=logging.getLevelName(args.log.upper()))
    
    return args


def main():
    args = process_args()
    run(args.log)

if __name__ == "__main__":
    main()