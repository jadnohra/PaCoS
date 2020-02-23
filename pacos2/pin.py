from .interfaces import IPin, PinState


class PinBase(IPin):
    def __init__(self, name: str, state: PinState):
        self._name = name
        self._state = state

    @property
    def name(self) -> str:
        return self._name

    @property
    def state(self) -> PinState:
        return self._state

    def __repr__(self) -> str:
        return 'Pin {} ({})'.format(self.name, self.state)