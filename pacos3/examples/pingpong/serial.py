import sys
from typing import List
import logging
import argparse
from pacos3.token import Address, Token
from pacos3.procedure import Procedure, IProcessorAPI, ProcState, CallResult
from pacos3.actor import Actor
from pacos3.mock.sources import SingleShotSource
from pacos3.processor import Processor


class PingActor(Actor):
    def __init__(self, ping_count: int):
        self._pings_left = ping_count
        super().__init__('ping', [PingTriggerProc(self)])


class PingTriggerProc(Procedure):
    def __init__(self, actor: "PingActor"):
        super().__init__('trigger', ProcState.OPEN)
        self._actor = actor

    def call(self, token: Token, proc: IProcessorAPI) -> CallResult:
        if self._actor._pings_left > 0:
            logging.warning('step: {}, pings_left: {}'
                            .format(proc.step_count, 
                                    self._actor._pings_left))
            self._actor._pings_left = self._actor._pings_left - 1
            return CallResult(1, [self.create_token()])
        proc.exit()
        return CallResult()
    
    @staticmethod
    def create_token() -> Token:
        return Token(Address(actor='pong'), None)


class PongTriggerProc(Procedure):
    def __init__(self):
        super().__init__('trigger', ProcState.OPEN)

    def call(self, token: Token, proc: IProcessorAPI) -> CallResult:
        out_token = token.forward_target(Address(actor='ping'))
        return CallResult(1, [out_token])


class PongActor(Actor):
    def __init__(self):
        super().__init__('pong', [PongTriggerProc()])


def run():
    print('=== pingpong-serial ===')
    processor = Processor()
    ping_actor = PingActor(3)
    processor.add_actor(ping_actor)
    processor.add_actor(PongActor())
    processor.add_source(SingleShotSource([PingTriggerProc.create_token()]))
    while not processor.has_exited:
        processor.step()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", default='WARNING')
    args = parser.parse_args(sys.argv[1:])
    logging.basicConfig(format='%(levelname)s: %(message)s',
                        level=logging.getLevelName(args.log.upper()))
    run()
