import copy
from typing import List, Any
from .time import Time, repr_time
from .address import Address
from .call import Call


class Token:
    def __init__(self, call: Call):
        self._call = call
        self._stamps = []
        self._stamp_addresses = []
    
    @property
    def call(self) -> Call:
        return self._call
    
    @property
    def target(self) -> Address:
        return self._call.target

    @property
    def emission_time(self) -> Time:
        return self._stamps[0]

    @property
    def last_time(self) -> Time:
        return self._stamps[-1]

    @property
    def wire_time(self) -> Time:
        return self._stamps[-1] - self._stamps[0]

    def stamp(self, time: Time) -> "Token":
        self._stamps.append(time)
        self._stamp_addresses.append(copy.copy(self._call.target))
        return self

    def forward_processor(self, processor: str) -> "Token":
        self._call.target.processor = processor
        return self

    def forward_actor(self, actor: str) -> "Token":
        self._call.target.actor = actor
        return self

    def forward_target(self, target: Address) -> "Token":
        self._call.target = target
        return self

    def __str__(self) -> str:
        stamps_repr = ', '.join([repr_time(x) for x in self._stamps])
        return '{} [{}]'.format(str(self._call), stamps_repr)
