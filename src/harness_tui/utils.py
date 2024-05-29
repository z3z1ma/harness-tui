import time
from functools import lru_cache, wraps


def ttl_cache(ttl: int):
    def compute_hash():
        round(time.time() / ttl)

    def decorator(func):
        @wraps(func)
        def func_wrapper(*args, ttl_hash=None, **kwargs):
            _ = ttl_hash
            return func(*args, **kwargs)

        @wraps(func)
        @lru_cache(maxsize=10)
        def with_ttl(*args, **kwargs):
            return func_wrapper(*args, **kwargs, ttl_hash=compute_hash())

        return with_ttl

    return decorator
