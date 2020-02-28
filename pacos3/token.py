from typing import List, Any
from .time import Time
from .address import Address


class Token:
    def __init__(self, target: Address, payload: Any, time: Time):
        self._target = target
        self._payload = payload
        self._stamps = [time]
    
    @property
    def payload(self) -> Any:
        return self._payload

    @property
    def target(self) -> Address:
        return self._target

    @property
    def emission_time(self) -> Time:
        return self._stamps[0].time

    @property
    def wire_time(self) -> Time:
        return self._stamps[-1].time - self._stamps[0].time

    def forward_processor(self, processor: str, time: Time) -> "Token":
        self._stamps.append(time)
        self._target.processor = processor
        return self

    def forward_actor(self, actor: str, time: Time) -> "Token":
        self._stamps.append(time)
        self._target.actor = actor
        return self

    def forward_target(self, target: Address, time: Time) -> "Token":
        self._stamps.append(time)
        self._target = target
        return self

    def __str__(self) -> str:
        return '{} -> {} @ [{}]'.format(
                            self._payload, self._target,
                            ', '.join([str(x) for x in self._stamps]))
