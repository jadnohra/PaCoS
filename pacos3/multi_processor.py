from typing import List
from .interfaces import (
        IRouter, ProcCall, IProcessor, TimeInterval, IMultiProcessor, IClock)
from .routers import MultiProcessorRouter


class MultiProcessor(IMultiProcessor):
    def __init__(self, clock: IClock = None):
        self._processors = []
        self._name_processor_dict = {}
        self._router = MultiProcessorRouter(clock, self)

    @property
    def router(self) -> IRouter:
        return self._router

    def add_processor(self, processor: IProcessor) -> None:
        processor.init_address(None)
        self._processors.append(processor)
        self._name_processor_dict[processor.name] = processor

    def get_processor(self, processor_name: str) -> IProcessor:
        if processor_name is None and len(self._processors) >= 0:
            return self._processors[0]
        return self._name_processor_dict.get(processor_name, None)
    
    @property
    def processors(self) -> List[IProcessor]:
        return self._processors

    def step(self) -> TimeInterval:
        intervals = [processor.step(self._router) 
                     for processor in self._processors]
        return sum(intervals)
