import sys
from typing import List, Any
import logging
import argparse
import time
import timeit
import os
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
        return CallResult([Call(arg+1, Address(actor='source', proc='feed'), 
                                call_step=proxor.step_count+10),
                           Call(arg, Address(processor='C', actor='compute', 
                                             proc='data1'))])


class DoubleSourceActor(Actor):
    def __init__(self):
        super().__init__('source', [DoubleFeedProc()])


class DoubleFeedProc(Procedure):
    def __init__(self):
        super().__init__('feed')

    def call(self, arg: CallArg, __, proxor: IProcessorAPI) -> CallResult:
        return CallResult([Call(None, Address(actor='source', proc='feed')),
                           Call(1, Address(processor='C', actor='compute',
                                           proc='data2'))],
                          4)


class ComputeActor(Actor):
    def __init__(self, use_protocol: bool = False):
        super().__init__('compute', [Data1Proc(self, use_protocol), 
                                     Data2Proc(self)])
        self.accum = []


class Data1Proc(Procedure):
    def __init__(self, actor: ComputeActor, use_protocol: bool = False):
        super().__init__('data1')
        self._actor = actor
        self._use_protocol = use_protocol

    def call(self, arg: CallArg, __, proxor: IProcessorAPI) -> CallResult:
        print('ZZZ', arg)
        result = [arg, self._actor.accum]
        if self._use_protocol:
            if len (self._actor.accum) < 2:
                logging.warning('active protocol synch')
                return proxor.wait(Address(proc='data2'))
            #elif len (self._actor.accum) >= 4:
            #    logging.error('PROTOCOL ERROR')
            #    return proxor.exit()
        self._actor.accum = []
        return CallResult([Call(result, Address(processor='D', actor='sink'))])


class Data2Proc(Procedure):
    def __init__(self, actor: ComputeActor):
        super().__init__('data2')
        self._actor = actor

    def call(self, arg: CallArg, __, proxor: IProcessorAPI) -> CallResult:
        self._actor.accum.append(arg)
        return CallResult()


class SinkActor(Actor):
    def __init__(self):
        super().__init__('sink', [ConsumeProc()])


class ConsumeProc(Procedure):
    def __init__(self):
        super().__init__('consume')

    @staticmethod
    def check_data_status(arg: Any) -> str:
        if len(arg) != 2:
            return 'PANIC'
        if arg[0] == 0 and len(arg[1]) == 0:
            return 'INIT'
        if len(arg[1]) >= 2 and len(arg[1]) <= 3:
            return 'HEALTHY'
        return 'DEGRADED'

    def call(self, arg: CallArg, __, proxor: IProcessorAPI) -> CallResult:
        value_status = self.check_data_status(arg)
        logging.warning('Sink received value: {} : {}'.format(arg, 
                                                              value_status))
        return CallResult()


def source_A_main(processor: Processor) -> None:
    processor.add_actor(SourceActor())
    processor.put_calls([Call(0, Address(actor='source'))])


def source_B_main(processor: Processor) -> None:
    processor.add_actor(DoubleSourceActor())
    processor.put_calls([Call(None, Address(actor='source'))])


def compute_main(processor: Processor, use_protocol: bool) -> None:
    processor.add_actor(ComputeActor(use_protocol))


def sink_main(processor: Processor) -> None:
    processor.add_actor(SinkActor())

def create_board(log_lvl: str = 'WARNING', profile=None, 
                 use_protocol: bool = False) -> Board:
    processor_configs = [
        ProcessorConfig(name='A', main=source_A_main, log_level=log_lvl), 
        ProcessorConfig(name='B', main=source_B_main, log_level=log_lvl), 
        ProcessorConfig(name='C', main=compute_main, log_level=log_lvl,
                        main_args={'use_protocol':use_protocol}), 
        ProcessorConfig(name='D', main=sink_main, log_level=log_lvl)
        ]
    
    return Board(processor_configs, profile_filepath=profile)


def run(log_lvl: str = 'WARNING', sim_time = 5.0, profile = None,
        use_protocol: bool = False):
    print('=== best-effort-race ===')
    board = create_board(log_lvl, profile, use_protocol)
    start = timeit.default_timer()
    while not board.any_exited():
        board.step()
        time.sleep(0.03)  # slow down the simulation artificially
        curr = timeit.default_timer()
        if sim_time is not None and curr - start > sim_time:
            break
    board.exit()


def description() -> str:
    return \
    """
    An implcitly time-sychronized best-effort computation.
    """


def process_args() -> Any:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--log", default='WARNING')
    parser.add_argument("--run_count", default=1, type=int)
    parser.add_argument("--use_protocol", action='store_true')
    parser.add_argument("-p", "--profile", default=None)
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
    if args.profile is None:
        my_dir = os.path.dirname(__file__)
        args.profile = os.path.join(my_dir, 'best_effort_race_random.json')
    for _ in range(args.run_count):
        run(args.log, args.sim_time, args.profile, args.use_protocol)


if __name__ == "__main__":
    main()
