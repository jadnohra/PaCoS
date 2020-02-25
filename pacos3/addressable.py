import copy
from abc import ABC, abstractproperty
from typing import List
from .address import Address


class Addressable(ABC):
    def __init__(self, name: str):
        self._name = name
        self.init_address(None)

    def init_address(self, parent: "Addressable"):
        from .interfaces import IProcessor, IActor, IProcedure, Address
        if parent is not None:
            address = copy.copy(parent.address)
        else:
            address = Address(None, None, None)
        if isinstance(self, IProcessor):
            address.processor = self.name
        elif isinstance(self, IActor):
            address.actor = self.name
        elif isinstance(self, IProcedure):
            address.proc = self.name
        self._address = address

    @abstractproperty
    def name(self) -> str:
        pass

    @property
    def address(self) -> Address:
        return self._address
