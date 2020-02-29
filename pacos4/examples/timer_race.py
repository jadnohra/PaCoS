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


class ComputeActor(Actor):
    def __init__(self):
        super().__init__('compute', [RecvDataProc(self), TimerSendProc(self)])
        self._value = 'UNINITIALIZED'


class RecvDataProc(Procedure):
    def __init__(self, actor: ComputeActor):
        super().__init__('recv')
        self._actor = actor

    def call(self, arg: CallArg, _, proxor: IProcessorAPI) -> CallResult:
        self._actor._value = arg
        return CallResult()


class TimerSendProc(Procedure):
    def __init__(self, actor: ComputeActor):
        super().__init__('send')
        self._actor = actor

    def call(self, arg: CallArg, _, proxor: IProcessorAPI) -> CallResult:
        return CallResult(1, [Call(self._actor._value, 
                              Address(processor='C', actor='sink'))])


class SinkActor(Actor):
    def __init__(self):
        super().__init__('sink', [SinkProc()])


class SinkProc(Procedure):
    def __init__(self):
        super().__init__('consume')

    def call(self, arg: CallArg, __, proxor: IProcessorAPI) -> CallResult:
        logging.warning('Sink received value: {}'.format(arg))
        return proxor.exit()


def source_main(processor: Processor) -> None:
    processor.put_calls([Call('OK', 
                              Address(processor='B', actor='compute'),
                              call_step=random.randint(0, 10))])


def compute_main(processor: Processor) -> None:
    processor.add_actor(ComputeActor())
    processor.put_calls([Call(None, 
                              Address(actor='compute', proc='send'),
                              call_step=5)])


def sink_main(processor: Processor) -> None:
    processor.add_actor(SinkActor())


def run(log_lvl: str = 'WARNING'):
    print('=== timer-race ===')
    processor_configs = [
        ProcessorConfig(name='A', main=source_main, log_level=log_lvl), 
        ProcessorConfig(name='B', main=compute_main, log_level=log_lvl),
        ProcessorConfig(name='C', main=sink_main, log_level=log_lvl)
        ]
    board = Board(processor_configs)
    while not board.any_exited():
        board.step()
    board.exit()


def description() -> str:
    return \
    """
    A timer race demo.
    """
    # TODO: tack-on synchronization


def process_args() -> Any:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--log", default='WARNING')
    parser.add_argument("--run_count", default=5, type=int)
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
        run(args.log)


if __name__ == "__main__":
    main()
