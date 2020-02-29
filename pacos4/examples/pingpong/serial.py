import sys
from typing import List
import logging
import argparse
from pacos4.token import Address, Token
from pacos4.call import CallArg, Call, CallResult
from pacos4.procedure import Procedure, IProcessorAPI
from pacos4.actor import Actor
from pacos4.processor import Processor


class PingActor(Actor):
    def __init__(self, ping_count: int):
        self._pings_left = ping_count
        super().__init__('ping', [PingTriggerProc(self)])


class PingTriggerProc(Procedure):
    def __init__(self, actor: "PingActor"):
        super().__init__('trigger')
        self._actor = actor

    def call(self, arg: CallArg, _, proxor: IProcessorAPI) -> CallResult:
        if self._actor._pings_left > 0:
            logging.warning('step: {}, pings_left: {}'
                            .format(proxor.step_count, 
                                    self._actor._pings_left))
            self._actor._pings_left = self._actor._pings_left - 1
            return CallResult(1, [self.create_call()])
        proxor.exit()
        return CallResult()
    
    @staticmethod
    def create_call() -> Call:
        return Call(None, Address(actor='pong'))


class PongTriggerProc(Procedure):
    def __init__(self):
        super().__init__('trigger')

    def call(self, arg: CallArg, _, __) -> CallResult:
        return CallResult(1, [Call(arg, Address(actor='ping'))])


class PongActor(Actor):
    def __init__(self):
        super().__init__('pong', [PongTriggerProc()])


def run():
    print('=== pingpong-serial ===')
    processor = Processor()
    ping_actor = PingActor(3)
    processor.add_actor(ping_actor)
    processor.add_actor(PongActor())
    processor.put_calls([PingTriggerProc.create_call()])
    while not processor.has_exited:
        processor.step()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", default='WARNING')
    args = parser.parse_args(sys.argv[1:])
    logging.basicConfig(format='%(levelname)s: %(message)s',
                        level=logging.getLevelName(args.log.upper()))
    run()
