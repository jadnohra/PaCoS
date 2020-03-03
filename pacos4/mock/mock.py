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
from pacos4.procedure import Procedure, IProcessorAPI, IProcedure
from pacos4.actor import Actor
from pacos4.processor import Processor, ProcessorConfig
from pacos4.time import StepCount, repr_time
from pacos4.board import Board


class MockCallGenConfig:
    def __init__(self, type: str, address: Address):
        self.address = address


class MockProcedureConfig:
    def __init__(self, type: str, name: str, actor_name: str, 
                 call_gen_configs: List[MockCallGenConfig],
                 timer_freq: float = None):
        self.name = name
        self.actor_name = actor_name
        self.call_gen_configs = call_gen_configs
        self.timer_freq = timer_freq


class MockActorConfig:
    def __init__(self, name: str, proc_configs: List[MockProcedureConfig]):
        self.name = name
        self.proc_configs = proc_configs


class MockProcessorConfig:
    def __init__(self, name: str, freq: float, 
                 actor_configs: List[MockActorConfig],
                 log_level: str = None):
        self.name = name
        self.freq = freq
        self.actor_configs = actor_configs
        self.log_level = log_level


class MockBoardConfig:
    def __init__(self, processor_configs: List[MockProcessorConfig]):
        self.processor_configs = processor_configs


class MockCallGenerator:
    def __init__(self, config: MockCallGenConfig):
        self._address = config.address

    def gen_call(self, arg: CallArg, proxor: IProcessorAPI):
        return Call(arg, target=self._address)


class MockProcedureConnector(Procedure):
    def __init__(self, config: MockProcedureConfig):
        super().__init__(config.name)
        self._actor_name = config.actor_name
        self._call_counter = 0
        self._call_gens = [MockCallGenerator(x) 
                           for x in config.call_gen_configs]

    def call(self, arg: CallArg, __, proxor: IProcessorAPI) -> CallResult:
        logging.warning('{}.{} : {}'.format(self._actor_name, self.name, 
                                            self._call_counter))
        self._call_counter = self._call_counter + 1
        calls = [x.gen_call(self._call_counter, proxor)
                 for x in self._call_gens]
        return CallResult([x for x in calls if x is not None])

    def gen_init_calls(self) -> List[Call]:
        return []


class MockProcedurePeriodic(MockProcedureConnector):
    def __init__(self, config: MockProcedureConfig):
        super().__init__(config)
        self._timer_freq = config.timer_freq
        

    def call(self, arg: CallArg, __, proxor: IProcessorAPI) -> CallResult:
        result = super().call(arg, __, proxor)
        result.calls.append(self.create_timer_call(proxor))
        return result

    def gen_init_calls(self, proxor: IProcessorAPI) -> List[Call]:
        return self.create_timer_call(proxor, immediate=True)

    def create_timer_call(self, proxor: IProcessorAPI, 
                          immediate: bool = False) -> Call:
        call_step_count = max(1, int(proxor.frequency / self._timer_freq))
        call_step = (0 if immediate 
                     else (call_step_count + proxor.step_count))
        return Call(None, Address(actor=self._actor_name, proc=self.name), 
                    call_step=call_step)


def create_mock_procedure(config: MockProcedureConfig) -> IProcedure:
    if config.type == 'periodic':
        return MockProcedurePeriodic(config)
    return MockProcedureConnector(config)
    

class MockActor(Actor):
    def __init__(self, config: MockActorConfig):
        super().__init__(config.name, 
                         [create_mock_procedure(x) 
                          for x in config.proc_configs])


def mock_processor_main(processor: Processor, config: MockProcessorConfig
                        ) -> None:
    actors = [MockActor(x) for x in config.actor_configs]
    init_calls = []
    for actor in actors:
        for proc in actor.procedures:
            init_calls.extend(proc.gen_init_calls())
    if len(init_calls):
        processor.put_calls(init_calls)


def mock_create_board(config: MockBoardConfig, log_lvl: str = 'WARNING', 
                      profile=None) -> Board:
    processor_configs = [
        ProcessorConfig(name=x.name, main=mock_processor_main, 
                        main_args={'config': x}, 
                        log_level=(x.log_level if x.log_level else log_lvl),
                        frequency=x.frequency)
        for x in config.processor_configs]
    return Board(processor_configs, profile_filepath=profile)


def parse_mock_config(mock_file: str) -> MockBoardConfig:
    return None


def run(mock_file: str, log_lvl: str='WARNING', sim_time: float = 2.0, 
        app_time: float = 2.0, profile: str = None):
    print('=== {} ==='.format(os.path.basename(mock_file)))
    board = mock_create_board(parse_mock_config(mock_file), log_lvl, profile)
    start = timeit.default_timer()
    while not board.any_exited():
        proc_times = board.step()
        if min(proc_times) > app_time:
            logging.warning("Reached application time: {}".format(app_time))
            break
        # time.sleep(0.03)  # slow down the simulation artificially
        curr = timeit.default_timer()
        if sim_time is not None and curr - start > sim_time:
            logging.warning("Reached simulation time: {}".format(sim_time))
            break
    board.exit()


def process_args() -> Any:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("file")
    parser.add_argument("--log", default='WARNING')
    parser.add_argument("--run_count", default=1, type=int)
    parser.add_argument("-p", "--profile", default=None)
    parser.add_argument("--sim_time", default=2.0, type=float)
    parser.add_argument("--app_time", default=2.0, type=float)
    args = parser.parse_args(sys.argv[1:])
    logging.basicConfig(format='%(levelname)s:%(message)s',
                        level=logging.getLevelName(args.log.upper()))
    random.seed(time.time())
    return args


def main():
    args = process_args()
    for _ in range(args.run_count):
        run(args.file, args.log, args.sim_time, args.app_time, args.profile)


if __name__ == "__main__":
    main()
