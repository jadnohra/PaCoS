from .discrete_event import Message, Actor
from .discrete_event_ism import IsmPin


class BasicIsmPin(IsmPin):
    def __init__(self, actor: Actor, name: str, waiting=False, accepting=False):
        super().__init__()
        self._name = name
        self._is_waiting = waiting
        self._is_accepting = accepting
        self._actor = actor
        self.msgs = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_waiting(self) -> bool:
        return self._is_waiting

    @property
    def actor(self) -> "Actor":
        return self._actor

    @property
    def is_accepting(self) -> bool:
        return self._is_accepting

    def accept(self, msg: Message):
        if not self._is_waiting:
            print('Dropped message!')
            return
        self.msgs.append(msg)

    def __repr__(self) -> str:
        return self._name
