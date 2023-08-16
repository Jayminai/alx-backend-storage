#!/usr/bin/env python3
"""
Web module
"""

import requests
import redis
from functools import wraps

class WebCache:
    """
    WebCache class for caching and tracking web pages
    """
    def __init__(self) -> None:
        """
        Initialize the WebCache instance and connect to Redis.
        """
        self._redis = redis.Redis()

    def get_page(self, url: str) -> str:
        """
        Get the HTML content of a web page using the given URL.
        Cache the result with an expiration time of 10 seconds.
        Track the number of times the URL is accessed.

        :param url: The URL of the web page.
        :type url: str
        :return: The HTML content of the web page.
        :rtype: str
        """
        count_key = f'count:{url}'
        page_content = self._redis.get(url)
        
        if page_content is None:
            response = requests.get(url)
            page_content = response.text
            self._redis.setex(url, 10, page_content)
        
        self._redis.incr(count_key)
        
        return page_content

def track_url_access(method):
    """
    A decorator to track the number of times a URL is accessed.
    """
    @wraps(method)
    def wrapper(self, url, *args, **kwargs):
        count_key = f'count:{url}'
        self._redis.incr(count_key)
        return method(self, url, *args, **kwargs)
    return wrapper

if __name__ == "__main__":
    web_cache = WebCache()

    slow_url = "http://slowwly.robertomurray.co.uk/delay/5000/url/https://www.example.com"
    page_content = web_cache.get_page(slow_url)
    print(page_content)

    page_content_cached = web_cache.get_page(slow_url)
    print(page_content_cached)

    fast_url = "https://www.example.com"
    page_content_fast = web_cache.get_page(fast_url)
    print(page_content_fast)

    @track_url_access
    def custom_get_page(self, url):
        return self.get_page(url)

    custom_page_content = custom_get_page(web_cache, slow_url)
    print(custom_page_content)
