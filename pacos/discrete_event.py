from typing import List, Any


class Message:
    def __init__(self, target_pin: "Pin", payload: Any):
        self.target_pin = target_pin
        self.payload = payload


class Pin:
    def __init__(self):
        pass

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
    def pins(self) -> List[Pin]:
        return []

    def init_call(self, engine: "Engine") -> None:
        return []

    def call(self, engine: "Engine") -> None:
        return None


class Engine:
    def __init__(self):
        self._actors = []
        self._msg_pool = []

    def add_actor(self, actor: Actor):
        self._actors.append(actor)

    def add_msg(self, msg: Message):
        self._msg_pool.append(msg)

    def _pop_msg(self) -> None:
        msg = self._msg_pool.pop()
        msg.target_pin.accept(msg)
        msg.target_pin.actor.call(self)

    def _init_run(self) -> None:
        for actor in self._actors:
            actor.init_call(self)

    def run(self, max_steps=100, print_steps=False) -> None:
        self._init_run()
        step = 0
        while len(self._msg_pool) and step < max_steps:
            if print_steps:
                print('step', step)
            self._pop_msg()
            step = step + 1
