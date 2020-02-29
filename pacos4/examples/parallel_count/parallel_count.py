import sys
from typing import List, Any
import logging
import argparse
import time
import timeit
from pacos4.token import Address, Token
from pacos4.call import CallArg, Call, CallResult
from pacos4.procedure import Procedure, IProcessorAPI
from pacos4.actor import Actor
from pacos4.processor import Processor, ProcessorConfig
from pacos4.time import repr_time
from pacos4.board import Board


class CountActor(Actor):
    def __init__(self, target: Address):
        super().__init__('counter', [CountProc(target)])


class CountProc(Procedure):
    def __init__(self, target: Address):
        super().__init__('count')
        self._target = target

    def call(self, arg: CallArg, _, proxor: IProcessorAPI) -> CallResult:
        count = int(arg)
        if count >= 3:
            return proxor.exit()
        logging.warning('time: {}, count: {}'.format(
                        repr_time(proxor.time), count))
        time.sleep(0.3)
        return CallResult(1, [Call(count + 1, self._target)])


def actor_A_main(processor: Processor) -> None:
    processor.add_actor(CountActor(target=Address(processor='B')))
    processor.put_calls([Call(0, Address(actor='counter'))])


def actor_B_main(processor: Processor) -> None:
    processor.add_actor(CountActor(target=Address(processor='C')))
    processor.put_calls([Call(0, Address(actor='counter'))])


def actor_C_main(processor: Processor) -> None:
    processor.add_actor(CountActor(target=Address(processor='A')))
    processor.put_calls([Call(0, Address(actor='counter'))])


def run(log_lvl: str = 'WARNING'):
    print('=== parallel-count ===')
    processor_configs = [
        ProcessorConfig(name='A', main=actor_A_main, log_level=log_lvl), 
        ProcessorConfig(name='B', main=actor_B_main, log_level=log_lvl),
        ProcessorConfig(name='C', main=actor_C_main, log_level=log_lvl)
        ]
    board = Board(processor_configs)
    while not board.any_exited():
        board.step()
    board.exit()


def description() -> str:
    return \
    """
    The parallel-count demo does 3 parallel counts to 3, there are hence 9 
     computations taking place.
    Each computation is forced to take 0.3 sec using time.sleep.
    pacos supports true parallel processing inside the SUS and only throttles 
     parallelism when needed. 
    To show this, if a run of this script is timed, we see that the total 
     wall time is around 1 sec. Since each computation takes around 0.3 sec, 
     we conclude that parallelism is indeed not throttled.
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


if __name__ == "__main__":
    args = process_args()
    start = timeit.default_timer()
    run(args.log)
    end = timeit.default_timer()
    print('{} s. (wall time)'.format(end - start))