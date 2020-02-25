from .interfaces import IActor, List, IPin, Addressable


class Actor(IActor):
    def __init__(self, name: str, pins: List[IPin]):
        self._pins = pins
        self._name_pin_dict = {pin.name:pin for pin in pins}
        Addressable.__init__(self, name)

    def init_address(self, parent: Addressable):
        Addressable.init_address(self, parent)
        for pin in self._pins:
            pin.init_address(self)

    @property
    def pins(self) -> List[IPin]:
        return self._pins

    def get_pin(self, pin_name: str) -> IPin:
        if pin_name is None and len(self._pins) >= 0:
            return self._pins[0]
        return self._name_pin_dict.get(pin_name, None)