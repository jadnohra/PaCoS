from typing import List
from pacos.serial.discrete_event_ism import IsmEngine, de
from .parall_util import get_parall_id, MPQueue


class IsmEngineParall(IsmEngine):
    def __init__(self, id: str ='ie', impulse_rand=None, synchronized=False):
        super().__init__(id=id, impulse_rand=impulse_rand,
                         synchronized=synchronized)
        self._parall_queue = MPQueue()
        self._actor_dict = {}

    def add_actor(self, actor: de.Actor):
        self.de_engine.add_actor(actor)
        actor._parall_engine = self
        self._actor_dict[actor.name] = actor

    def get_pin_address(self, pin: de.Pin) -> str:
        return '{}.{}'.format(pin.actor.name, pin.name)

    def resolve_pin_address(self, address: str) -> de.Pin:
        actor_name, pin_name = address.split('.')
        return self._actor_dict.get(actor_name, None).find_pin(pin_name)

    def add_msg(self, msg: de.Message):
        if msg.target_pin.actor._parall_engine == self:
            self._synch_msg_pool.append(msg)
        else:
            print('PARALLEL PANIC!', msg)
            engine = msg.target_pin.actor._parall_engine
            engine._parall_queue.put(msg.forward(
                                        self.get_pin_address(msg.target_pin)))

    def _get_transfer_msgs(self) -> List[de.Message]:
        remote_msgs = []
        queue = self._parall_queue
        while not queue.empty():
            msg = queue.get()
            remote_msgs.append(msg.forward(
                                self.resolve_pin_address(msg.target_pin)))
            print('YYYY', msg)
        return remote_msgs + super()._get_transfer_msgs()

    def run(self, return_on_idle=False, max_frames=20,
            print_frames=False) -> None:
        self._parall_id = get_parall_id()
        super().run(return_on_idle=False, max_frames=max_frames,
                    print_frames=print_frames)
