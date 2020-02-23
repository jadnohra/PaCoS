from .interfaces import IMessage, IEngine, ITopology, IClock


class SerialMsgRouter:
    def __init__(self, topology: ITopology, clock: IClock):
        self._topology = topology
        self._clock = clock
    
    def route(self, msg: IMessage) -> None:
        self._topology.get_engine(msg.target.engine).put_msg(msg)

    @property
    def clock(self) -> IClock:
        return self._clock