from collections import namedtuple
from itertools import islice

daysize = 24 * 60 * 60

class Event(namedtuple('BaseEvent', 'time isup')):

    def shift(self, daycount):
        return self._replace(time = self.time + daycount * daysize)

class UptimeEstimator:

    def __init__(self):
        self.events = []

    def add(self, time, isup):
        assert time.tzinfo is None
        self.events.append(Event((time.hour * 60 + time.minute) * 60 + time.second + time.microsecond / 1e6, isup))

    def uptime(self):
        timeline = sorted(self.events)
        # Each up event contributes the average of the empty periods immediately before and after it (with wraparound) to uptime:
        ring = [timeline[-1].shift(-1), *timeline, timeline[0].shift(1)]
        return sum(after.time - before.time for before, event, after in zip(ring, islice(ring, 1, None), islice(ring, 2, None)) if event.isup) / 2 / daysize * 100
