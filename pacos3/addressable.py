import copy
from typing import List
from .address import Address

class Addressable:
    def __init__(self, name: str):
        self._name = name
        self.init_address(None)

    def init_address(self, parent: "Addressable"):
        from .interfaces import IEngine, IActor, IPin, Address
        if parent is not None:
            address = copy.copy(parent.address)
        else:
            address = Address(None, None, None)
        if isinstance(self, IEngine):
            address.engine = self.name
        elif isinstance(self, IActor):
            address.actor = self.name
        elif isinstance(self, IPin):
            address.pin = self.name
        self._address = address

    @property
    def name(self) -> str:
        return self._name

    @property
    def address(self) -> Address:
        return self._address
