

class Address:
    def __init__(self, engine: str = None, actor: str = None, pin: str = None):
        self.engine = engine
        self.actor = actor
        self.pin = pin

    def __repr__(self) -> str:
        return '{}{}{}'.format(self.engine + '.' if self.engine else '', 
                                 self.actor + '.' if self.actor else '', 
                                 self.pin if self.pin else '')