import copy
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
    def __init__(self, id: str ='ie', impulse_rand=None, synchronized=False):
        self._id = id
        self.de_engine = de.Engine('de')
        self._impulses = []
        self._frame = -1
        self._impulse_rand = impulse_rand
        self._synchronized = synchronized
        self._synch_msg_pool = []

    @property
    def id(self) -> str:
        return self._id

    @property
    def frame(self) -> int:
        return self._frame

    def add_actor(self, actor: de.Actor):
        self.de_engine.add_actor(actor)

    def add_msg(self, msg: de.Message):
        if self._synchronized:
            self._synch_msg_pool.append(msg)
        else:
            self.de_engine.add_msg(msg)

    def add_impulse(self, impulse: Impulse):
        self._impulses.append(impulse)

    def _call_impulses(self):
        if self._impulse_rand:
            impulses = copy.copy(self._impulses)
            self._impulse_rand.shuffle(impulses)
        else:
            impulses = reversed(self._impulses)
        for impulse in impulses:
            impulse.call(self)

    def _run_frame(self) -> None:
        if self._synchronized:
            de_steps = 0
            is_idle = False
            while not is_idle:
                is_idle = True
                new_msgs = [x for x in self._synch_msg_pool
                           if x.target_pin.is_waiting]
                if len(new_msgs):
                    is_idle = False
                    for msg in new_msgs:
                        self.de_engine.add_msg(msg)
                        self._synch_msg_pool.remove(msg)
                    de_steps = (de_steps
                                + self.de_engine.run(-1, False, engine=self))
            return de_steps
        else:
            return self.de_engine.run(-1, False, engine=self)

    def get_stamp(self) -> de.Stamp:
        return de.Stamp().add(self._id, self._frame).update(
                                                    self.de_engine.get_stamp())

    def compare_stamps(self, ref: de.Stamp, other: de.Stamp) -> int:
        return other.get(self._id) - ref.get(self._id)

    def run(self, return_on_idle=False, max_frames=20,
            print_frames=False) -> None:
        self.de_engine._init_run()
        self._frame = 0
        self._call_impulses()
        while self._frame < max_frames:
            if print_frames:
                print('frame', self._frame)
            de_steps = self._run_frame()
            if print_frames:
                print('steps', de_steps)
            if return_on_idle and de_steps == 0:
                print('IDLE')
                return
            self._frame = self._frame + 1
            self._call_impulses()
