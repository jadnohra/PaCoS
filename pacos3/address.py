

class Address:
    def __init__(self, board: str = None, processor: str = None, 
                 actor: str = None, proc: str = None):
        self.processor = processor
        self.actor = actor
        self.proc = proc

    def __repr__(self) -> str:
        return '{}{}{}'.format(self.processor + '.' if self.processor else '', 
                                 self.actor + '.' if self.actor else '', 
                                 self.proc if self.proc else '')
