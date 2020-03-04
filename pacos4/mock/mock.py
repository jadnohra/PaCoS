import sys
from typing import List, Any, Tuple
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
    def __init__(self, address: Address):
        self.address = address


class MockProcedureConfig:
    def __init__(self, type: str, name: str, actor_name: str, 
                 call_gen_configs: List[MockCallGenConfig],
                 timer_freq: float = None,
                 timer_freq_tolerance: float = None,
                 steps: Any = None,
                 steps_tolerance: Any = None,
                 sleep: float = None,
                 sleep_tolerance: float = None):
        self.type = type
        self.name = name
        self.actor_name = actor_name
        self.call_gen_configs = call_gen_configs
        self.timer_freq = timer_freq
        self.timer_freq_tolerance = timer_freq_tolerance
        self.steps = steps
        self.steps_tolerance = steps_tolerance
        self.sleep = sleep
        self.sleep_tolerance = sleep_tolerance


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
        self._rand = None
        self._step_count = 1
        self._step_count_tolerance = 0
        self._sleep = 0
        self._sleep_tolerance = 0
        if config.steps:
            self._step_count = int(config.steps)
        if config.steps_tolerance:
            self._step_count_tolerance = float(config.steps_tolerance)
            self.ensure_rand()
        if config.sleep:
            self._sleep = float(config.sleep)
        if config.sleep_tolerance:
            self._sleep_tolerance = float(config.sleep_tolerance)
            self.ensure_rand()

    def _jitter_step_count(self) -> 0:
        if self._step_count_tolerance == 0:
            return 0
        return self._rand.randint(-self._step_count_tolerance, 
                                  self._step_count_tolerance)

    def _jitter_sleep(self) -> 0:
        if self._sleep_tolerance == 0:
            return 0
        return self._rand.random() * self._sleep_tolerance

    def _do_sleep(self) -> None:
        if self._sleep == 0:
            return
        time.sleep(self._sleep + self._jitter_sleep())

    def call(self, arg: CallArg, __, proxor: IProcessorAPI) -> CallResult:
        logging.warning('{}.{} : {}'.format(self._actor_name, self.name, 
                                            self._call_counter))
        self._call_counter = self._call_counter + 1
        self._do_sleep()
        calls = [x.gen_call(self._call_counter, proxor)
                 for x in self._call_gens]
        step_count = self._step_count + self._jitter_step_count()
        return CallResult([x for x in calls if x is not None],
                          max(1, step_count))

    def gen_init_calls(self, proxor: IProcessorAPI) -> List[Call]:
        return []
    
    def ensure_rand(self) -> None:
        if self._rand is None:
            self._rand = random.Random()
    
    def dbg_on_exit(self, address: Address = None) -> None:
        print(str(address), self._call_counter)


class MockProcedurePeriodic(MockProcedureConnector):
    def __init__(self, config: MockProcedureConfig):
        super().__init__(config)
        self._timer_freq = float(config.timer_freq)
        self._timer_freq_tolerance = 0
        if config.timer_freq_tolerance:
            self._timer_freq_tolerance = float(config.timer_freq_tolerance)
            self.ensure_rand()
        

    def call(self, arg: CallArg, __, proxor: IProcessorAPI) -> CallResult:
        result = super().call(arg, __, proxor)
        result.calls.append(self.create_timer_call(proxor))
        return result

    def gen_init_calls(self, proxor: IProcessorAPI) -> List[Call]:
        return [self.create_timer_call(proxor, immediate=True)]

    def _jitter_call_steps(self, proxor: IProcessorAPI) -> 0:
        if self._timer_freq_tolerance == 0:
            return 0
        jitter_step_mag = int(proxor.frequency / self._timer_freq_tolerance)
        return self._rand.randint(-jitter_step_mag, jitter_step_mag)

    def create_timer_call(self, proxor: IProcessorAPI, 
                          immediate: bool = False) -> Call:
        call_step_count = int(proxor.frequency / self._timer_freq)
        if call_step_count <= 0:
             raise ValueError("Period freq {} to high for processor freq {}".
                              format(self._timer_freq, proxor.frequency)) 
        call_step_count = call_step_count + self._jitter_call_steps(proxor)
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
    for actor in actors:
        processor.add_actor(actor)
    init_calls = []
    for actor in actors:
        for proc in actor.procedures:
            init_calls.extend(proc.gen_init_calls(processor.api))
    if len(init_calls):
        processor.put_calls(init_calls)


def mock_create_board(config: MockBoardConfig, log_lvl: str = 'WARNING', 
                      profile=None) -> Board:
    processor_configs = [
        ProcessorConfig(name=x.name, main=mock_processor_main, 
                        main_args={'config': x}, 
                        log_level=(x.log_level if x.log_level else log_lvl),
                        frequency=float(x.freq))
        for x in config.processor_configs]
    return Board(processor_configs, profile_filepath=profile)


def parse_mock_config(mock_file: str) -> MockBoardConfig:
    def indent_level(line) -> int:
        i = 0
        level = 0
        while (i < len(line) and line[i:i+4] == '    '):
            level = level + 1
            i = i + 4
        return level
    def is_indent_level(level, line) -> bool:
        return indent_level(line) == level
    def parse_attr(line):
        return [x.strip() for x in line.strip().split(':')]
    def parse_tolerance(line) -> Tuple[Any, Any]:
        if '~' not in line:
            return [line, None] 
        return line.split('~')
    def parse_proc(actor_name, lines, li_ref) -> MockProcedureConfig:
        config = MockProcedureConfig(None, None, actor_name, [])
        config.name = lines[li_ref[0]].strip()
        li_ref[0] = li_ref[0] + 1
        while (li_ref[0] < len(lines)
               and is_indent_level(4, lines[li_ref[0]])):
            k, v = parse_attr(lines[li_ref[0]])
            if k == 'freq':
                v, tol = parse_tolerance(v)
                config.timer_freq = v
                config.timer_freq_tolerance = tol
            elif k == 'steps':
                v, tol = parse_tolerance(v)
                config.steps = v
                config.steps_tolerance = tol
            elif k == 'sleep':
                v, tol = parse_tolerance(v)
                config.sleep = v
                config.sleep_tolerance = tol
            else:
                setattr(config, k, v)
            li_ref[0] = li_ref[0] + 1
        return config
    def parse_actor(lines, li_ref) -> MockActorConfig:
        config = MockActorConfig(None, [])
        config.name = lines[li_ref[0]].strip()
        li_ref[0] = li_ref[0] + 1
        while (li_ref[0] < len(lines)
               and is_indent_level(3, lines[li_ref[0]])):
                config.proc_configs.append(parse_proc(config.name, 
                                                      lines, li_ref))
        return config
    def parse_processor_config(config: MockProcessorConfig, lines, li_ref
                               ) -> None:
        li_ref[0] = li_ref[0] + 1
        while is_indent_level(3, lines[li_ref[0]]):
            k, v = parse_attr(lines[li_ref[0]])
            setattr(config, k, v)
            li_ref[0] = li_ref[0] + 1
    def parse_processor(lines, li_ref) -> MockProcessorConfig:
        config = MockProcessorConfig(None, 0.0, [], None)
        config.name = lines[li_ref[0]].strip()
        li_ref[0] = li_ref[0] + 1
        while (li_ref[0] < len(lines)
               and is_indent_level(2, lines[li_ref[0]])):
            if lines[li_ref[0]].strip() == '_config':
                parse_processor_config(config, lines, li_ref)
            else:
                config.actor_configs.append(parse_actor(lines, li_ref))
        return config
    def find_proc_config(configs: List[MockProcessorConfig], address: Address
                         ) -> MockProcedureConfig:
        for config in configs:
            if config.name == address.processor:
                for actor_config in config.actor_configs:
                    if actor_config.name == address.actor:
                        for proc_config in actor_config.proc_configs:
                            if proc_config.name == address.proc:
                                return proc_config
                        break
                break
    def parse_connection(configs: List[MockProcessorConfig], line) -> None:
        left, right = [x.strip() for x in line.split('->') if len(x)]
        left_addr = Address.create_from_expression(left)
        right_addr = Address.create_from_expression(right)
        proc_config = find_proc_config(configs, left_addr)
        proc_config.call_gen_configs.append(MockCallGenConfig(right_addr))
    def parse_connections(configs: List[MockProcessorConfig], 
                          lines, li_ref) -> None:
        li_ref[0] = li_ref[0] + 1
        while (li_ref[0] < len(lines)
                and is_indent_level(2, lines[li_ref[0]])):
            parse_connection(configs, lines[li_ref[0]])
            li_ref[0] = li_ref[0] + 1
    def parse_board(lines, li) -> MockBoardConfig:
        processor_configs = []
        li_ref = [li]
        while li_ref[0] < len(lines):
            if lines[li_ref[0]].strip() == '_connections':
               parse_connections(processor_configs, lines, li_ref)
            else:
                processor_configs.append(parse_processor(lines, li_ref))
        return MockBoardConfig(processor_configs)
    def parse_root(lines, li=0) -> MockBoardConfig:
        if lines[li] == '_board':
            return parse_board(lines, li+1)
        return None

    with open(mock_file) as fi:
        lines = [x.rstrip() for x in fi.readlines() if len(x.strip())]
    return parse_root(lines)


def run(mock_file: str, parse_only: bool = False, log_lvl: str='WARNING', 
        sim_time: float = 2.0, app_time: float = 2.0, profile: str = None):
    print('=== {} ==='.format(os.path.basename(mock_file)))
    board_config = parse_mock_config(mock_file)
    if parse_only:
        import json
        print(json.dumps(board_config, default=lambda o: o.__dict__, 
                         indent=4))
        return
    board = mock_create_board(board_config, log_lvl, profile)
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
    parser.add_argument("--parse", action='store_true')
    parser.add_argument("--log", default='ERROR')
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
        run(args.file, args.parse, args.log, args.sim_time, args.app_time, 
            args.profile)


if __name__ == "__main__":
    main()
