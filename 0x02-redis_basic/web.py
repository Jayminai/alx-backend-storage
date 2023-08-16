#!/usr/bin/env python3
"""implementing an expiring web cache and tracker"""
import redis
import requests
r = redis.Redis()


def get_page(url: str) -> str:
    """uses the requests module to obtain the HTML content of a
    particular URL and returns it"""
    # r.set(f"cached:{url}", count)

    if r.get(f"count:{url}"):
        r.incr(f"count:{url}")
        r.expire(f"count:{url}", 10)
    else:
        r.setex(f"count:{url}", 10, 1)

    req = requests.get(url)
    return req.text


if __name__ == "__main__":
    print(get_page('http://slowwly.robertomurray.co.uk'))
