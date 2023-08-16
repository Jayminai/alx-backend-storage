#!/usr/bin/env python3
'''A module with tools for expiring request caching and tracking.
'''
import redis
import requests
from functools import wraps
from typing import Callable

redis_store = redis.Redis()
'''The module-level Redis instance.
'''

def expiring_data_cacher(method: Callable) -> Callable:
    '''Caches the output of fetched data with expiration.
    '''
    @wraps(method)
    def invoker(url) -> str:
        '''The wrapper function for caching the output with expiration.
        '''
        redis_store.incr(f'count:{url}')
        result = redis_store.get(f'result:{url}')
        if result:
            return result.decode('utf-8')
        result = method(url)
        redis_store.set(f'count:{url}', 0)
        redis_store.setex(f'result:{url}', 10, result)
        return result
    return invoker

def get_page(url: str) -> str:
    '''Returns the content of a URL after caching the request's response,
    tracking the request, and using an expiration time.
    '''
    return requests.get(url).text

# Decorate the get_page function with the expiring_data_cacher decorator
get_page = expiring_data_cacher(get_page)

# Test the decorated function
if __name__ == "__main__":
    slow_url = "http://slowwly.robertomurray.co.uk/delay/5000/url/http://www.example.com"
    print(get_page(slow_url))
