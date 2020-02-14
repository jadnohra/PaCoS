from .discrete_event import *


class IsmPin(Pin):
    def __init__(self):
        super().__init__()

    @property
    def is_waiting(self) -> bool:
        return True

    @property
    def is_accepting(self) -> bool:
        return False


class Impulse:
    def call(self, engine: "IsmEngine") -> None:
        pass

class IsmEngine(Engine):
    def __init__(self):
        super().__init__()
        self._impulses = []

    def add_impulse(self, impulse: Impulse):
        self._impulses.append(impulse)

    def _call_impulses(self):
        for impulse in self._impulses:
            impulse.call(self)

    def run(self, max_steps=100, print_steps=False) -> None:
        self._init_run()
        step = 0
        self._call_impulses()
        while step < max_steps:
            if print_steps:
                print('step', step)
            if len(self._msg_pool):
                self._pop_msg()
            step = step + 1
            self._call_impulses()
