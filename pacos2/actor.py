from .interfaces import IActor, List, IPin, Addressable


class Actor(IActor):
    def __init__(self, name: str, pins: List[IPin]):
        Addressable.__init__(self, name)
        self._pins = pins

    def init_address(self, parent: Addressable):
        Addressable.init_address(self, parent)
        for pin in self._pins:
            pin.init_address(self)

    @property
    def pins(self) -> List[IPin]:
        return self._pins