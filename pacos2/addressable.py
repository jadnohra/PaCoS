import os


class Addressable:
    def init_address(self, parent: Addressable):
        name = getattr(self, 'name', '???')
        if parent is not None:
            os.path.join(parent.address, name)
        else:
            self._address = name 

    @property
    def address(self):
        return self._address

    def __repr__(self) -> str:
        return '{}'.format(self.address)