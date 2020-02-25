from abc import ABC, abstractmethod
from .interfaces import IMessage, IClock, PinState


class IMsgReadyPolicy(ABC):
    @abstractmethod
    def check(self, msg: IMessage, engine: "DiscreteEventEngine", 
              clock: IClock) -> bool:
        pass


class MsgAlwaysReadyPolicy(IMsgReadyPolicy):
     def check(self, msg: IMessage, engine: "DiscreteEventEngine", 
               clock: IClock) -> bool:
        return True


class MsgReadyPolicy(IMsgReadyPolicy):
     def check(self, msg: IMessage, engine: "DiscreteEventEngine", 
               clock: IClock) -> bool:
        return (engine.get_msg_pin(msg).state != PinState.CLOSED
                and msg.emission_time + msg.wire_time >= clock.time)
