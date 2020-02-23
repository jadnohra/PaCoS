from typing import Any
from .interfaces import Stamp, Address, IMessage, Time, TimeInterval


class Message(IMessage):
    def __init__(self, source: Address, target: Address, payload: Any,
                 emission_time: Time, wire_time: TimeInterval = 0):
        super().__init__()
        self._source = source
        self._target = target
        self._payload = payload
        self._emission_time = emission_time
        self._wire_time = wire_time
        self._stamps = []

    def __repr__(self) -> str:
        return '{} -> {} @ [{}]'.format(
                            self._payload, self._target, 
                            ', '.join([str(x) for x in self._stamps]))

    @property
    def target(self) -> Address:
        return self._target

    def forward(self, new_target: Address) -> None:
        self._target = new_target

    @property
    def source(self) -> Address:
        return self._source

    def stamp(self, new_stamp: Stamp) -> None:
        self._stamps.append(new_stamp)

    @property
    def stamps(self, new_stamp: Stamp) -> List[Stamp]:
        return self._stamps

    @property
    def emission_time(self) -> Time:
        return self._emission_time

    @property
    def wire_time(self) -> TimeInterval:
        return self._wire_time