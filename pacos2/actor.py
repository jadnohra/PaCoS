from .interfaces import IActor, List, IPin


class Actor(IActor):
    def __init__(self, name: str, pins: List[IPin]):
        self._name = name
        self._pins = pins
        for pin in self._pins:
            pin.init_address(self)

    @property
    def name(self) -> str:
        self._name

    @property
    def pins(self) -> List[IPin]:
        return self._pins