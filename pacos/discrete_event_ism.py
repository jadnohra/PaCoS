from . import discrete_event as de


class IsmPin(de.Pin):
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

class IsmEngine:
    def __init__(self, id: str ='ie'):
        self._id = id
        self.de_engine = de.Engine('de')
        self._impulses = []
        self.frame = -1

    @property
    def id(self) -> str:
        return self._id

    def add_actor(self, actor: de.Actor):
        self.de_engine.add_actor(actor)

    def add_msg(self, msg: de.Message):
        self.de_engine.add_msg(msg)


    def add_impulse(self, impulse: Impulse):
        self._impulses.append(impulse)

    def _call_impulses(self):
        for impulse in self._impulses:
            impulse.call(self)

    def _run_frame(self) -> None:
        return self.de_engine.run(-1, False, stamper=self)

    def get_stamp(self) -> de.Stamp:
        return de.Stamp().add(self._id, self.frame).update(
                                                    self.de_engine.get_stamp())


    def run(self, max_frames=20, print_frames=False) -> None:
        self.de_engine._init_run()
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
