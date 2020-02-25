from .interfaces import Time, TimeInterval, IClock


class ManualClock(IClock):
    def __init__(self, t0: Time = 0):
        self._time = t0
    
    def advance(self, interval: TimeInterval) -> None:
        self._time = self._time + interval

    @property
    def time(self) -> Time:
        return self._time

    @time.setter
    def time(self, time: Time) -> None:
        self._time = time