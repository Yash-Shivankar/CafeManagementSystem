"""A small fixed-window rate limiter.

Deliberately dependency-free. The default backend is in-process, which is
correct for a single uvicorn worker and for development. `RedisRateLimiter`
is the drop-in for multi-worker or multi-instance deployments — implement it
against `redis.asyncio` when you get there; the call sites do not change.
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict


class RateLimitExceeded(Exception):
    def __init__(self, retry_after: int):
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded. Retry in {retry_after}s.")


class BaseRateLimiter:
    def hit(self, key: str, limit: int, window_seconds: int) -> None:
        raise NotImplementedError

    def reset(self, key: str) -> None:
        raise NotImplementedError


class InMemoryRateLimiter(BaseRateLimiter):
    """Fixed-window counter held in process memory.

    Caveat, stated plainly: with N uvicorn workers the effective limit is
    N x `limit`, because each worker keeps its own counter. That is still a
    hard ceiling on credential stuffing, and it is a large improvement over
    the unlimited login endpoint we started with.
    """

    def __init__(self) -> None:
        self._hits: dict[str, list[float]] = defaultdict(list)
        self._lock = threading.Lock()
        self._last_purge = time.monotonic()

    def hit(self, key: str, limit: int, window_seconds: int) -> None:
        now = time.monotonic()
        cutoff = now - window_seconds

        with self._lock:
            self._purge(now, window_seconds)

            timestamps = [ts for ts in self._hits[key] if ts > cutoff]

            if len(timestamps) >= limit:
                retry_after = int(window_seconds - (now - timestamps[0])) + 1
                self._hits[key] = timestamps
                raise RateLimitExceeded(max(retry_after, 1))

            timestamps.append(now)
            self._hits[key] = timestamps

    def reset(self, key: str) -> None:
        """Clear a key — call this after a *successful* login so an honest
        user who mistyped their password twice is not punished."""
        with self._lock:
            self._hits.pop(key, None)

    def _purge(self, now: float, window_seconds: float) -> None:
        """Drop stale keys occasionally so the dict cannot grow without bound."""
        if now - self._last_purge < 60:
            return
        self._last_purge = now
        cutoff = now - window_seconds
        for key in list(self._hits):
            fresh = [ts for ts in self._hits[key] if ts > cutoff]
            if fresh:
                self._hits[key] = fresh
            else:
                del self._hits[key]


login_rate_limiter: BaseRateLimiter = InMemoryRateLimiter()
