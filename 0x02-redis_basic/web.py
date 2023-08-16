#!/usr/bin/env python3
"""implementing an expiring web cache and tracker"""
import redis
import requests
r = redis.Redis()

def get_page(url: str) -> str:
    """
    Uses the requests module to obtain the HTML content of a particular URL and returns it.
    """
    # Increment and set expiration for URL access count
    if r.get(f"count:{url}"):
        r.incr(f"count:{url}")
        r.expire(f"count:{url}", 10)
    else:
        r.setex(f"count:{url}", 10, 1)

    # Check if HTML content is cached
    cached_content = r.get(url)
    if cached_content:
        return cached_content.decode("utf-8")

    # Fetch and cache HTML content
    req = requests.get(url)
    r.setex(url, 10, req.text)
    return req.text

if __name__ == "__main__":
    print(get_page('http://slowwly.robertomurray.co.uk'))
