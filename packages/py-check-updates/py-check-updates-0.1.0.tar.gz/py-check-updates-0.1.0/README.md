py-check-updates
================

[![Test](https://github.com/tueda/py-check-updates/workflows/Test/badge.svg?branch=main)](https://github.com/tueda/py-check-updates/actions?query=branch:main)
[![PyPI version](https://badge.fury.io/py/py-check-updates.svg)](https://pypi.org/project/py-check-updates/)

This is a dependency update checker to assist Python package developers.

If you are the kind of paranoid person who checks whether packages
in your dependency lists are updated once a week
and you do it manually for some technical reasons,
then this program is for you.

Currently, the program checks updates (it does not automatically update them, though) for:

- Top-level dependencies in `pyproject.toml` for [Poetry](https://python-poetry.org/)
  (see [poetry#2684](https://github.com/python-poetry/poetry/issues/2684)).
  Limited to simple versions of the form `package = "(^|~|>=)?version"`.

- Additional dependencies of hooks in `.pre-commit-config.yaml` for [pre-commit](https://pre-commit.com/)
  (see [pre-commit#1351](https://github.com/pre-commit/pre-commit/issues/1351)).
  Limited to simple Python dependencies of the form `package==version`.

Installation
------------

```bash
pip install py-check-updates
```

Usage
-----

```bash
py-check-updates
```
