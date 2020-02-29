from typing import List
from .interfaces import IActor, IProcedure


class Actor(IActor):
    def __init__(self, name: str, procedures: List[IProcedure]):
        self._name = name
        self._procedures = procedures
        self._name_procedure_dict = {procedure.name:procedure 
                                     for procedure in procedures}

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def procedures(self) -> List[IProcedure]:
        return self._procedures

    def get_procedure(self, procedure_name: str) -> IProcedure:
        if procedure_name is None and len(self._procedures) >= 0:
            return self._procedures[0]
        return self._name_procedure_dict.get(procedure_name, None)