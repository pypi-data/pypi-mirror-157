"""Routines for pypi."""

import functools

import requests


def get_latest_version(name: str) -> str:
    """Return the latest version of the given package on PyPI."""
    return _get_latest_version_impl(name.lower())


@functools.lru_cache(maxsize=None)
def _get_latest_version_impl(name: str) -> str:
    r = requests.get(f"https://pypi.org/pypi/{name}/json")
    return r.json()["info"]["version"]  # type: ignore[no-any-return]
