#!/usr/bin/env python3
"""writing strings to redis"""
import redis
from typing import Union, Callable, Optional
import uuid
import sys
from functools import wraps
Unionsbif = Union[str, bytes, int, float]


def count_calls(method: Callable) -> Callable:
    """decorator that counts no of times cache method is called"""
    key = method.__qualname__
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Wrapper method"""
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """store the history of inputs and outputs for a particular function"""
    key = method.__qualname__
    input_i = "".join([key, ":inputs"])
    output = "".join([key, ":outputs"])
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Wrapper method"""
        self._redis.rpush(input_i, str(args))
        out = method(self, *args, **kwargs)
        self._redis.rpush(output, str(out))
        return out
    return wrapper


def replay(method: Callable) -> None:
    """
    Replays the history of a function
    Args:
        method: The function to be decorated
    Returns:
        None
    """
    name = method.__qualname__
    cache = redis.Redis()
    calls = cache.get(name).decode("utf-8")
    print("{} was called {} times:".format(name, calls))
    inputs = cache.lrange(name + ":inputs", 0, -1)
    outputs = cache.lrange(name + ":outputs", 0, -1)
    for i, o in zip(inputs, outputs):
        print("{}(*{}) -> {}".format(name, i.decode('utf-8'),
                                     o.decode('utf-8')))


class Cache:
    """Cache class"""
    def __init__(self):
        """store and instance of redis clientas a private variable"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Unionsbif) -> str:
        """creates key id and stores data in redis"""
        key = str(uuid.uuid4())
        self._redis.mset({key: data})
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Unionsbif:
        """convert the data back to the desired format"""
        if fn:
            return fn(self._redis.get(key))
        return self._redis.get(key)

    def get_int(self: bytes) -> int:
        """parametrize Cache.get with the correct conversion function"""
        return int.from_bytes(self, sys.byteorder)

    def get_str(self: bytes) -> str:
        """parametrize Cache.get with the correct conversion function."""
        return self.decode("utf-8")
