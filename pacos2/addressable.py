import os


class Addressable:
    def __init__(self, name: str):
        self._name = name
        self.init_address(None)

    def init_address(self, parent: Addressable):
        if parent is not None:
            os.path.join(parent.address, self.name)
        else:
            self._address = self.name 

    @property
    def name(self) -> str:
        return self._name

    @property
    def address(self):
        return self._address

    def __repr__(self) -> str:
        return '{}'.format(self.address)