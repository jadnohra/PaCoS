import sys
import json
from typing import List, Any


class Stamp:
    def __init__(self):
        self._part_infos = {}

    def update(self, other: "Stamp") -> "Stamp":
        self._part_infos.update(other._part_infos)
        return self

    def add(self, id: Any, info: Any) -> "Stamp":
        self._part_infos[id] = info
        return self

    def get(self, id: Any, dflt: Any = None) -> Any:
        return self._part_infos.get(id, dflt)

    def __repr__(self):
        return json.dumps(self._part_infos)


class Message:
    def __init__(self, target_pin: "Pin", payload: Any):
        self.target_pin = target_pin
        self.payload = payload
        self.stamps = []

    def stamp(self, new_stamp: Stamp) -> None:
        self.stamps.append(new_stamp)

    def __repr__(self) -> str:
        return '{} -> {} @ [{}]'.format(
                            self.payload, self.target_pin.name,
                            ', '.join([str(x) for x in self.stamps]))


class Pin:
    def __init__(self):
        pass

    @property
    def name(self) -> str:
        return 'p_'

    @property
    def actor(self) -> "Actor":
        return None

    def accept(self, msg: Message) -> None:
        print('Ignored message!')
        pass


class Actor:
    def __init__(self):
        pass

    @property
    def name(self) -> str:
        return 'a_'

    @property
    def pins(self) -> List[Pin]:
        return []

    def init_call(self, engine: "Engine") -> None:
        return []

    def call(self, engine: "Engine") -> None:
        return None


class Engine:
    def __init__(self, id: str = 'e'):
        self._id = id
        self._actors = []
        self._msg_pool = []
        self.step = -1

    @property
    def id(self) -> str:
        return self._id

    def add_actor(self, actor: Actor):
        self._actors.append(actor)

    def add_msg(self, msg: Message):
        self._msg_pool.append(msg)

    def _pop_msg(self, stamper: Any) -> None:
        msg = self._msg_pool.pop()
        msg.stamp(stamper.get_stamp())
        msg.target_pin.accept(msg)
        msg.target_pin.actor.call(self)
        if '--log-msgs' in sys.argv:
            print('MSG:', msg)

    def _init_run(self) -> None:
        for actor in self._actors:
            actor.init_call(self)

    def get_stamp(self) -> Stamp:
        return Stamp().add(self._id, self.step)

    def run(self, max_steps=100, print_steps=False, stamper: Any = None
            ) -> None:
        self._init_run()
        self.step = 0
        while len(self._msg_pool) and (self.step < max_steps or max_steps < 0):
            if print_steps:
                print('step', self.step)
            self._pop_msg(stamper if stamper else self)
            self.step = self.step + 1
        return self.step
