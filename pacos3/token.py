import copy
from typing import List, Any
from .time import Time, repr_time
from .address import Address


class Token:
    def __init__(self, target: Address, payload: Any):
        self._target = target
        self._payload = payload
        self._stamps = []
        self._stamp_addresses = []
    
    @property
    def payload(self) -> Any:
        return self._payload

    @property
    def target(self) -> Address:
        return self._target

    @property
    def emission_time(self) -> Time:
        return self._stamps[0]

    @property
    def last_time(self) -> Time:
        return self._stamps[-1]

    @property
    def wire_time(self) -> Time:
        return self._stamps[-1] - self._stamps[0]

    def stamp(self, time: Time) -> None:
        self._stamps.append(time)
        self._stamp_addresses.append(copy.copy(self._target))

    def forward_processor(self, processor: str) -> "Token":
        self._target.processor = processor
        return self

    def forward_actor(self, actor: str) -> "Token":
        self._target.actor = actor
        return self

    def forward_target(self, target: Address) -> "Token":
        self._target = target
        return self

    def __str__(self) -> str:
        return '{} -> {} @ [{}]'.format(
                            self._payload, self._target,
                            ', '.join([repr_time(x) for x in self._stamps]))
