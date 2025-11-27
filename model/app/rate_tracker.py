from collections import defaultdict, deque

class RateTracker:
    def __init__(self, window: float = 1.0):
        self.window = window
        self.timestamps = defaultdict(deque)

    def add(self, src_ip: str, ts: float):
        q = self.timestamps[src_ip]
        q.append(ts)
        # remove entries older than window
        while q and ts - q[0] > self.window:
            q.popleft()

    def pps(self, src_ip: str) -> float:
        q = self.timestamps[src_ip]
        return len(q) / self.window if q else 0.0


# global instance (1-second window, same as your original)
rate_tracker = RateTracker(window=1.0)
