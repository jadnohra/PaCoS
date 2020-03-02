import sys
from typing import List, Any
import logging
import argparse
import time
import timeit
import random
from pacos4.token import Address, Token
from pacos4.call import CallArg, Call, CallResult
from pacos4.procedure import Procedure, IProcessorAPI
from pacos4.actor import Actor
from pacos4.processor import Processor, ProcessorConfig
from pacos4.time import repr_time
from pacos4.board import Board


class SourceActor(Actor):
    def __init__(self):
        super().__init__('source', [FeedProc()])


class FeedProc(Procedure):
    def __init__(self):
        super().__init__('feed')

    def call(self, arg: CallArg, __, proxor: IProcessorAPI) -> CallResult:
        my_step_count = 1
        return CallResult(my_step_count, 
                          [Call(arg+1, Address(actor='source', proc='feed'), 
                                call_step=proxor.step_count+my_step_count+10),
                           Call(arg, Address(processor='C', actor='compute', 
                                             proc='data1'))])


class DoubleSourceActor(Actor):
    def __init__(self):
        super().__init__('source', [DoubleFeedProc()])


class DoubleFeedProc(Procedure):
    def __init__(self):
        super().__init__('feed')

    def call(self, arg: CallArg, __, proxor: IProcessorAPI) -> CallResult:
        my_step_count = random.randint(2, 8)
        return CallResult(my_step_count, 
                          [Call(None, Address(actor='source', proc='feed')),
                           Call(1, Address(processor='C', actor='compute',
                                           proc='data2'))])


class ComputeActor(Actor):
    def __init__(self):
        super().__init__('compute', [Data1Proc(self), Data2Proc(self)])
        self.accum = ''


class Data1Proc(Procedure):
    def __init__(self, actor: ComputeActor):
        super().__init__('data1')
        self._actor = actor

    def call(self, arg: CallArg, __, proxor: IProcessorAPI) -> CallResult:
        result = '{}*({})'.format(arg, self._actor.accum)
        self._actor.accum = ''
        return CallResult(1, 
                          [Call(result, Address(processor='D', actor='sink'))])


class Data2Proc(Procedure):
    def __init__(self, actor: ComputeActor):
        super().__init__('data2')
        self._actor = actor

    def call(self, arg: CallArg, __, proxor: IProcessorAPI) -> CallResult:
        if self._actor.accum:
            self._actor.accum = '{} + {}'.format(self._actor.accum, arg)
        else:
            self._actor.accum = arg
        return CallResult()


class SinkActor(Actor):
    def __init__(self):
        super().__init__('sink', [ConsumeProc()])


class ConsumeProc(Procedure):
    def __init__(self):
        super().__init__('consume')

    @staticmethod
    def check_ok(value: str) -> bool:
        if len(value.split('*')) != 2:
            return False
        a, b = value.split('*')
        if a =='0':
            return b == '()'
        op_count = len(b.split('+'))
        return  op_count >= 2 and op_count <= 3

    def call(self, arg: CallArg, __, proxor: IProcessorAPI) -> CallResult:
        value_status = 'OK' if self.check_ok(arg) else 'INVALID'
        logging.warning('Sink received value: {} : {}'.format(arg, 
                                                              value_status))
        return CallResult()
        #return proxor.exit()


def source_A_main(processor: Processor) -> None:
    processor.add_actor(SourceActor())
    processor.put_calls([Call(0, Address(actor='source'))])


def source_B_main(processor: Processor) -> None:
    processor.add_actor(DoubleSourceActor())
    processor.put_calls([Call(None, Address(actor='source'))])


def compute_main(processor: Processor) -> None:
    processor.add_actor(ComputeActor())


def sink_main(processor: Processor) -> None:
    processor.add_actor(SinkActor())

def create_board(log_lvl: str = 'WARNING') -> Board:
    processor_configs = [
        ProcessorConfig(name='A', main=source_A_main, log_level=log_lvl), 
        ProcessorConfig(name='B', main=source_B_main, log_level=log_lvl), 
        ProcessorConfig(name='C', main=compute_main, log_level=log_lvl), 
        ProcessorConfig(name='D', main=sink_main, log_level=log_lvl)
        ]
    return Board(processor_configs)


def run(log_lvl: str = 'WARNING', sim_time = 5.0):
    print('=== data-race ===')
    board = create_board(log_lvl)
    start = timeit.default_timer()
    while not board.any_exited():
        board.step()
        time.sleep(0.05)  # slow down the simulation artificially
        curr = timeit.default_timer()
        if sim_time is not None and curr - start > sim_time:
            break
    board.exit()


def description() -> str:
    return \
    """
    An implcitly time-sychronized computation.
    """


def process_args() -> Any:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--log", default='WARNING')
    parser.add_argument("--run_count", default=1, type=int)
    parser.add_argument("--sim_time", default=5, type=int)
    parser.add_argument('-h', '--help', action='help', 
                        default=argparse.SUPPRESS,
                        help=description())
    args = parser.parse_args(sys.argv[1:])
    logging.basicConfig(format='%(levelname)s:%(message)s',
                        level=logging.getLevelName(args.log.upper()))
    random.seed(time.time())
    return args


def main():
    args = process_args()
    for _ in range(args.run_count):
        run(args.log, args.sim_time)


if __name__ == "__main__":
    main()
