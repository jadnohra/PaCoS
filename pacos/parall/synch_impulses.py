from pacos.serial.discrete_event_ism import Impulse, de


class SynchImpulse(Impulse):
    def __init__(self, unsynch_impl: Impulse):
        self._unsynch_impl = unsynch_impl
        self._tick = 0

    def add_msg(self, msg: de.Message) -> None:
        self._engine.add_msg(msg)

    def call(self, engine: "IsmEngine") -> None:
        # This is a hack, sine we pose as an IsmEngine
        # hoping only add_msg is called by _unsynch_impl
        self._engine = engine
        self._unsynch_impl.call(self)
        self._tick = self._tick + 1