from .interfaces import TimeInterval, IMessage, IMsgRouter, IActor, IEngine



class Engine:
    def __init__(self, id: str = 'e'):
        self._id = id
        self._actors = []
        self._msgs = []
        self.step = -1

    @property
    def id(self) -> str:
        return self._id

    def add_actor(self, actor: Actor):
        self._actors.append(actor)

    def push_msg(self, msg: Message):
        self._msgs.append(msg)

    def _pop_msg(self, engine: Any) -> None:
        msg = self._msgs.pop()
        msg.stamp(engine.get_stamp())
        msg.target_pin.accept(msg)
        msg.target_pin.actor.call(engine)
        if '--log' in sys.argv:
            print('MSG:', msg)


    def _init_run(self) -> None:
        for actor in self._actors:
            actor.init_call(self)

    def get_stamp(self) -> Stamp:
        return Stamp().add(self._id, self.step)

    def run(self, max_steps=100, print_steps=False, engine: "Engine" = None
            ) -> None:
        self._init_run()
        self.step = 0
        while len(self._msgs) and (self.step < max_steps or max_steps < 0):
            if print_steps:
                print('step', self.step)
            self._pop_msg(engine if engine else self)
            self.step = self.step + 1
        return self.step



class DiscreteEventEngine(IEngine):
    def __init__(self, name: str):
        self._name = name
        self._actors = []

    @property
    def name(self) -> str:
        return self._name
    
    def add_actor(self, actor: IActor) -> None:
        actor.init_address(self)
        self._actors.append(actor)
        

    def push_msg(self, msg: Message):
        self._msgs.append(msg)

    def _pop_msg(self, engine: Any) -> None:
        msg = self._msgs.pop()
        msg.stamp(engine.get_stamp())
        msg.target_pin.accept(msg)
        msg.target_pin.actor.call(engine)
        if '--log' in sys.argv:
            print('MSG:', msg)


    def step(self, router: IMsgRouter) -> TimeInterval:
        pass

    def put(self, msg: IMessage) -> None:
        pass