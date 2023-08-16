#!/usr/bin/env python3
"""
Implements an expiring web cache and tracker
"""
from typing import Callable
from functools import wraps
import redis
import requests

redis_client = redis.Redis()


def url_count(method: Callable) -> Callable:
    """counts how many times an url is accessed"""
    @wraps(method)
    def wrapper(*args, **kwargs):
        url = args[0]
        redis_client.incr(f"count:{url}")
        cached = redis_client.get(url)  # Remove unnecessary f-string
        if cached:
            return cached.decode('utf-8')
        response = method(url)  # Fetch the page content
        redis_client.setex(url, 10, response)  # Fix setex arguments
        return response

    return wrapper


@url_count
def get_page(url: str) -> str:
    """get a page and cache value"""
    response = requests.get(url)
    return response.text


if __name__ == "__main__":
    print(get_page('http://slowwly.robertomurray.co.uk'))
