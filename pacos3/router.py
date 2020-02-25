import os
import logging
from typing import List
from .interfaces import ProcCall, IProcessor, IMultiProcessor, IClock, IRouter


class BufferingRouter(IRouter):
    def __init__(self, clock: IClock):
        self._clock = clock
        self._buffer = []
    
    @property
    def clock(self) -> IClock:
        return self._clock
    
    @clock.setter
    def clock(self, clock: IClock) -> None:
        self._clock = clock

    def route(self, call: ProcCall) -> None:
        self._buffer.append(call)

    def pop_buffered(self) -> List[ProcCall]:
        buffer, self._buffer = self._buffer, []
        return buffer


class SingleProcessorRouter(BufferingRouter):
    def __init__(self, clock: IClock, processor: IProcessor):
        super().__init__(clock)
        self._processor = processor
    
    def route(self, call: ProcCall) -> None:
        if (call.target.processor is None 
            or call.target.processor == self._processor.name):
            self._processor.put_call(call)
        else:
            super().route(call)


class MultiProcessorRouter(BufferingRouter):
    def __init__(self, clock: IClock, multi_processor: IMultiProcessor):
        super().__init__(clock)
        self._multi_processor = multi_processor
    
    def route(self, call: ProcCall) -> None:
        processor = self._multi_processor.get_engine(call.target.processor)
        if processor is not None:
            processor.put_call(call)
        else:
            super().route(call)
