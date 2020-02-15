from pacos.serial.discrete_event_ism import IsmEngine, de
from .parall_util import get_parall_id, MPQueue


class IsmEngineParall(IsmEngine):
    def __init__(self, id: str ='ie', impulse_rand=None, synchronized=False):
        super().__init__(id=id, impulse_rand=impulse_rand,
                         synchronized=synchronized)
        self._parall_queue = MPQueue()

    def add_actor(self, actor: de.Actor):
        self.de_engine.add_actor(actor)
        actor._parall_engine = self

    def add_msg(self, msg: de.Message):
        if msg.target_pin.actor._parall_engine == self:
            self._synch_msg_pool.append(msg)
        else:
            print('PARALLEL PANIC!', msg)
            msg.target_pin.actor._parall_engine._parall_queue.put(msg)

    def run(self, return_on_idle=False, max_frames=20,
            print_frames=False) -> None:
        self._parall_id = get_parall_id()
        super().run(return_on_idle=False, max_frames=max_frames,
                    print_frames=print_frames)
