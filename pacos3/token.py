from collections import namedtuple
from typing import List
from .proc_call import ProcCall
from .interfaces import IClock, Time, TimeInterval, Address


Stamp = namedtuple('Stamp', 'address time')

class Token:
    def __init__(self, call: ProcCall):
        self._call = call
        self._stamps = []
    
    def stamp(self, address: Address, time: Time) -> None:
        self._stamps.append(Stamp(address, time))

    @property
    def stamps(self) -> List[Stamp]:
        return self._stamps

    @property
    def emission_time(self) -> Time:
        return self._stamps[0].time

    @property
    def wire_time(self) -> TimeInterval:
        return self._stamps[-1].time - self._stamps[0].time

    def __repr__(self) -> str:
        return '{} @ [{}]'.format(
                            self._call,
                            ', '.join([str(x) for x in self._stamps]))
