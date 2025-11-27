import time
import requests

from config import NODE_LIVEPACKET

# LIVE-PACKET THROTTLE (max 10 POSTs / sec)
last_live_ts = 0.0
LIVE_POST_INTERVAL = 0.1  # seconds


def throttled_live_post(payload: dict):
    """
    POST to Node /api/live-packet at most 10 times/second
    (same behavior as your original code).
    """
    global last_live_ts
    now = time.time()
    if now - last_live_ts >= LIVE_POST_INTERVAL:
        try:
            requests.post(NODE_LIVEPACKET, json=payload, timeout=0.1)
            last_live_ts = now
        except Exception:
            # silently ignore errors (same as before)
            pass
