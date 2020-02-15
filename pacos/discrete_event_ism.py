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
        self.frame = -1

    def add_impulse(self, impulse: Impulse):
        self._impulses.append(impulse)

    def _call_impulses(self):
        for impulse in self._impulses:
            impulse.call(self)

    def _run_frame(self) -> None:
        return super().run(-1, False)

    def get_stamp(self) -> str:
        return '{}.{}'.format(self.frame, super().get_stamp())

    def run(self, max_frames=20, print_frames=False) -> None:
        self._init_run()
        self.frame = 0
        self._call_impulses()
        while self.frame < max_frames:
            if print_frames:
                print('frame', self.frame)
            de_steps = self._run_frame()
            if print_frames:
                print('steps', de_steps)
            self.frame = self.frame + 1
            self._call_impulses()
