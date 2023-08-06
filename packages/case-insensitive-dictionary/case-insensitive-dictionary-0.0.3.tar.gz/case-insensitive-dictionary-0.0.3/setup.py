# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['case_insensitive_dict']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'case-insensitive-dictionary',
    'version': '0.0.3',
    'description': 'Case Insensitive Dictionary',
    'long_description': '# Case Insensitive Dict\n\nCase Insensitive Dictionary\n\n[![Publish](https://github.com/DeveloperRSquared/case-insensitive-dict/actions/workflows/publish.yml/badge.svg)](https://github.com/DeveloperRSquared/case-insensitive-dict/actions/workflows/publish.yml)\n\n[![Python 3.7+](https://img.shields.io/badge/python-3.7+-brightgreen.svg)](#case-insensitive-dict)\n[![PyPI - License](https://img.shields.io/pypi/l/case-insensitive-dictionary.svg)](LICENSE)\n[![PyPI - Version](https://img.shields.io/pypi/v/case-insensitive-dictionary.svg)](https://pypi.org/project/case-insensitive-dictionary)\n\n[![codecov](https://codecov.io/gh/DeveloperRSquared/case-insensitive-dict/branch/main/graph/badge.svg?token=45JCHX8KT9)](https://codecov.io/gh/DeveloperRSquared/case-insensitive-dict)\n[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/DeveloperRSquared/case-insensitive-dict/main.svg)](https://results.pre-commit.ci/latest/github/DeveloperRSquared/case-insensitive-dict/main)\n[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)\n\n## Install\n\nInstall and update using [pip](https://pypi.org/project/case-insensitive-dictionary/).\n\n```sh\n$ pip install -U case-insensitive-dictionary\n```\n\n## Example\n\n```py\n>>> from case_insensitive_dict import CaseInsensitiveDict\n\n>>> case_insensitive_dict = CaseInsensitiveDict[str](data={"Aa": "b"})\n>>> case_insensitive_dict.get("aa")\n\'b\'\n>>> case_insensitive_dict.get("Aa")\n\'b\'\n```\n\n## Contributing\n\nContributions are welcome via pull requests.\n\n### First time setup\n\n```sh\n$ git clone git@github.com:DeveloperRSquared/case-insensitive-dict.git\n$ cd case-insensitive-dict\n$ poetry install\n$ poetry shell\n```\n\nTools including black, mypy etc. will run automatically if you install [pre-commit](https://pre-commit.com) using the instructions below\n\n```sh\n$ pre-commit install\n$ pre-commit run --all-files\n```\n\n### Running tests\n\n```sh\n$ poetry run pytest\n```\n\n## Links\n\n- Source Code: <https://github.com/DeveloperRSquared/case-insensitive-dict/>\n- PyPI Releases: <https://pypi.org/project/case-insensitive-dictionary/>\n- Issue Tracker: <https://github.com/DeveloperRSquared/case-insensitive-dict/issues/>\n',
    'author': 'rikhilrai',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/DeveloperRSquared/case-insensitive-dict',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
