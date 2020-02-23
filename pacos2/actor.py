from .interfaces import IActor, List, IPin, Addressable


class Actor(IActor):
    def __init__(self, name: str, pins: List[IPin]):
        Addressable.__init__(self, name)
        self._pins = pins
        self._name_pin_dict = {pin.name:pin for pin in pins}

    def init_address(self, parent: Addressable):
        Addressable.init_address(self, parent)
        for pin in self._pins:
            pin.init_address(self)

    @property
    def pins(self) -> List[IPin]:
        return self._pins

    def pin(self, pin_name: str) -> IPin:
        return self._name_pin_dict.get(pin_name, None)