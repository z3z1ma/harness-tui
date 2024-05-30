import time
from functools import lru_cache, wraps


def ttl_cache(seconds: int):
    """A decorator that caches the result of a function for a given time."""

    def decorator(func):
        @lru_cache(maxsize=None)
        def cached_func(*args, _ttl_time, **kwargs):
            _ = _ttl_time
            return func(*args, **kwargs)

        @wraps(func)
        def wrapper(*args, **kwargs):
            _ttl_time = round(time.time() / seconds)
            return cached_func(*args, _ttl_time=_ttl_time, **kwargs)

        return wrapper

    return decorator
