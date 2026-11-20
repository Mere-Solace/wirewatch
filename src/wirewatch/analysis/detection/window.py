from collections import defaultdict, deque


class DistinctWindow:
    """Counts distinct values per key within the last `seconds` seconds.

    Example: key = source IP, value = destination port.
    count("10.0.0.5") answers: how many different ports did it touch recently?
    """

    def __init__(self, seconds):
        self.seconds = seconds
        self._events = defaultdict(deque)   # key -> deque of (timestamp, value)

    def add(self, key, value, ts):
        self._events[key].append((ts, value))
        self._expire(key, ts)

    def count(self, key, now):
        self._expire(key, now)
        return len({value for _, value in self._events[key]})

    def _expire(self, key, now):
        q = self._events[key]
        while q and q[0][0] < now - self.seconds:
            q.popleft()