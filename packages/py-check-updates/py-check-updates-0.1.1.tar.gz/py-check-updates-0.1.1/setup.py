# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['check_updates']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'requests>=2.28.1,<3.0.0', 'tomlkit>=0.11.0,<0.12.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=1.4']}

entry_points = \
{'console_scripts': ['py-check-updates = check_updates:main']}

setup_kwargs = {
    'name': 'py-check-updates',
    'version': '0.1.1',
    'description': 'A Python dependency update checker.',
    'long_description': 'py-check-updates\n================\n\n[![Test](https://github.com/tueda/py-check-updates/workflows/Test/badge.svg?branch=main)](https://github.com/tueda/py-check-updates/actions?query=branch:main)\n[![PyPI version](https://badge.fury.io/py/py-check-updates.svg)](https://pypi.org/project/py-check-updates/)\n[![Codecov](https://codecov.io/gh/tueda/py-check-updates/branch/main/graph/badge.svg)](https://codecov.io/gh/tueda/py-check-updates)\n[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/tueda/py-check-updates.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/tueda/py-check-updates/context:python)\n\nThis is a dependency update checker to assist Python package developers.\n\nIf you are the kind of paranoid person who checks whether packages\nin your dependency lists are updated once a week\nand you do it manually for some technical reasons,\nthen this program is for you.\n\nCurrently, the program checks updates (it does not automatically update them, though) for:\n\n- Top-level dependencies in `pyproject.toml` for [Poetry](https://python-poetry.org/)\n  (see [poetry#2684](https://github.com/python-poetry/poetry/issues/2684)).\n  Limited to simple versions of the form `package = "(^|~|>=)?version"`.\n\n- Additional dependencies of hooks in `.pre-commit-config.yaml` for [pre-commit](https://pre-commit.com/)\n  (see [pre-commit#1351](https://github.com/pre-commit/pre-commit/issues/1351)).\n  Limited to simple Python dependencies of the form `package==version`.\n\nInstallation\n------------\n\n```bash\npip install py-check-updates\n```\n\nUsage\n-----\n\n```bash\npy-check-updates\n```\n',
    'author': 'Takahiro Ueda',
    'author_email': 'takahiro.ueda@yahoo.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tueda/py-check-updates',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
