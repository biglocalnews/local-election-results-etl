import typing

import requests


def request_json(url: str) -> typing.Dict:
    """Request the provided URL and return the JSON response as a Python dictionary."""
    r = requests.get(url)
    assert r.ok
    return r.json()
