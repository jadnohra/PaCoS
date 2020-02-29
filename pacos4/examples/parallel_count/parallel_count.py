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
    print('=== pingpong-parallel ===')
    processor_configs = [
        ProcessorConfig(name='A', main=actor_A_main, log_level=log_lvl), 
        ProcessorConfig(name='B', main=actor_B_main, log_level=log_lvl),
        ProcessorConfig(name='C', main=actor_C_main, log_level=log_lvl)
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