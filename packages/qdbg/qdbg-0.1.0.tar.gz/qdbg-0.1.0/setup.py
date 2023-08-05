# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['qdbg']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'qdbg',
    'version': '0.1.0',
    'description': 'a quick debugging cli tool',
    'long_description': "![PyPI](https://img.shields.io/pypi/v/qdbg)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/qdbg)\n![GitHub top language](https://img.shields.io/github/languages/top/hermgerm29/qdbg)\n[![Build Status](https://scrutinizer-ci.com/g/hermgerm29/qdbg/badges/build.png?b=main)](https://scrutinizer-ci.com/g/hermgerm29/qdbg/build-status/main)\n[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/hermgerm29/qdbg/badges/quality-score.png?b=main)](https://scrutinizer-ci.com/g/hermgerm29/qdbg/?branch=main)\n[![codecov](https://codecov.io/gh/hermgerm29/qdbg/branch/main/graph/badge.svg?token=2NV84UI94K)](https://codecov.io/gh/hermgerm29/qdbg)\n![GitHub](https://img.shields.io/github/license/hermgerm29/qdbg?color=blue)\n\n\n# qdbg\nQuick debug tool - a general purpose CLI debugging utility\n\n## Introduction\n\n![qdbg-demo-gif](./assets/qdbg-demo.gif)\n\nEliminate the wasted clicks and keystrokes involved with copying your error messages into a search bar. `qdbg` does this tedious task for you (and we know you do it a lot :wink:). Simply run any command, and when your program inevitably fails, `qdbg` will automatically open a search tab for you.\n\n```bash\nqdbg <cmd>\n```\n\nIn the unlikely event that your program runs successfully, `qdbg` will stay out of your way.\n\n\n## Requirements\n\n* A developer that runs faulty programs\n* Python 3.7+\n* Linux or OSX operating system\n* A functioning web browser\n\n## Dependencies\n\n`qdbg` is implemented only using the Python3 standard library. The package does have a few developer dependencies, including [python-poetry](https://github.com/python-poetry/poetry), that are listed in `pyproject.toml`.\n\n\n## Installation\n\n### OSX / Linux (recommended)\n\n```bash\ncurl -sSL https://raw.githubusercontent.com/hermgerm29/qdbg/main/get-qdbg.py | python -\n```\n\n### Windows\n\nNot supported.\n\n### PyPI\n\n[qdbg](https://pypi.org/project/qdbg/) is available on PyPI, but the recommended install method is preferred.\n\n## Credits\n\n`qdbg`'s installation script is heavily derived from [python-poetry](https://github.com/python-poetry/poetry).\n",
    'author': 'Jimmy Herman',
    'author_email': 'jimmyherman29@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/hermgerm29/qdbg',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
