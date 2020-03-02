

class Address:
    def __init__(self, board: str = None, processor: str = None, 
                 actor: str = None, proc: str = None):
        self.processor = processor
        self.actor = actor
        self.proc = proc

    @staticmethod
    def create_from_expression(expression: str) -> "Address":
        address = Address()
        parts = expression.split('.')
        if len(parts) > 0:
            address.proc = parts[-1]
        if len(parts) > 1:
            address.actor = parts[-2]
        if len(parts) > 2:
            address.processor = parts[-3]
        return address

    def equals(self, other: "Address") -> bool:
        return all([getattr(self, attr) == getattr(other, attr) for attr in 
                    ['processor', 'actor', 'proc']])

    def matches(self, filter_address: "Address") -> bool:
        return all([(getattr(filter_address, attr) is None 
                     or (getattr(self, attr) == getattr(filter_address, attr)))
                    for attr in ['processor', 'actor', 'proc']])

    def __repr__(self) -> str:
        return '{}{}{}'.format(self.processor + '.' if self.processor else '', 
                                 self.actor + '.' if self.actor else '', 
                                 self.proc if self.proc else '')
