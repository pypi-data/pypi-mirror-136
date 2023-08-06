# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['datetime_helpers']

package_data = \
{'': ['*']}

install_requires = \
['http-exceptions>=0.2.3,<0.3.0', 'importlib-metadata>=4.2.0,<5.0.0']

setup_kwargs = {
    'name': 'datetime-helpers',
    'version': '0.0.12',
    'description': 'Util for working with date and datetime objects',
    'long_description': '# datetime-helpers\n\nA handy collection of datetime utils.\n\n[![Build](https://github.com/DeveloperRSquared/datetime-helpers/actions/workflows/build.yml/badge.svg)](https://github.com/DeveloperRSquared/datetime-helpers/actions/workflows/build.yml)\n[![Publish](https://github.com/DeveloperRSquared/datetime-helpers/actions/workflows/publish.yml/badge.svg)](https://github.com/DeveloperRSquared/datetime-helpers/actions/workflows/publish.yml)\n\n[![Python 3.7+](https://img.shields.io/badge/python-3.7+-brightgreen.svg)](#datetime-helpers)\n[![PyPI - License](https://img.shields.io/pypi/l/datetime-helpers.svg)](LICENSE)\n[![PyPI - Version](https://img.shields.io/pypi/v/datetime-helpers.svg)](https://pypi.org/project/datetime-helpers)\n\n[![codecov](https://codecov.io/gh/DeveloperRSquared/datetime-helpers/branch/main/graph/badge.svg?token=UI5ZDDDXXB)](https://codecov.io/gh/DeveloperRSquared/datetime-helpers)\n[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/DeveloperRSquared/datetime-helpers/main.svg)](https://results.pre-commit.ci/latest/github/DeveloperRSquared/datetime-helpers/main)\n[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)\n\n## Install\n\nInstall and update using [pip](https://pypi.org/project/datetime-helpers/).\n\n```sh\n$ pip install -U datetime-helpers\n```\n\n## Contributing\n\nContributions are welcome via pull requests.\n\n### First time setup\n\n```sh\n$ git clone git@github.com:DeveloperRSquared/datetime-helpers.git\n$ cd datetime-helpers\n$ poetry install\n$ source .venv/bin/activate\n```\n\nTools including black, mypy etc. will run automatically if you install [pre-commit](https://pre-commit.com) using the instructions below\n\n```sh\n$ pre-commit install\n$ pre-commit run --all-files\n```\n\n### Running tests\n\n```sh\n$ poetry run pytest\n```\n\n## Links\n\n- Source Code: <https://github.com/DeveloperRSquared/datetime-helpers/>\n- PyPI Releases: <https://pypi.org/project/datetime-helpers/>\n- Issue Tracker: <https://github.com/DeveloperRSquared/datetime-helpers/issues/>\n',
    'author': 'rikhilrai',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/DeveloperRSquared/datetime-helpers',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
