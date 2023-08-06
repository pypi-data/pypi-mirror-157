# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lyght',
 'lyght.config',
 'lyght.controllers',
 'lyght.http',
 'lyght.routes',
 'tests']

package_data = \
{'': ['*']}

install_requires = \
['click==8.0.1',
 'pydantic>=1.9.1,<2.0.0',
 'uvicorn[standard]>=0.18.2,<0.19.0',
 'uvloop>=0.16.0,<0.17.0']

extras_require = \
{'dev': ['tox>=3.20.1,<4.0.0',
         'virtualenv>=20.2.2,<21.0.0',
         'pip>=20.3.1,<21.0.0',
         'twine>=3.3.0,<4.0.0',
         'pre-commit>=2.12.0,<3.0.0',
         'toml>=0.10.2,<0.11.0',
         'bump2version>=1.0.1,<2.0.0'],
 'doc': ['mkdocs>=1.1.2,<2.0.0',
         'mkdocs-include-markdown-plugin>=1.0.0,<2.0.0',
         'mkdocs-material>=6.1.7,<7.0.0',
         'mkdocstrings>=0.15.2,<0.16.0',
         'mkdocs-autorefs>=0.2.1,<0.3.0'],
 'test': ['black>=21.5b2,<22.0',
          'isort>=5.8.0,<6.0.0',
          'flake8>=3.9.2,<4.0.0',
          'flake8-docstrings>=1.6.0,<2.0.0',
          'mypy>=0.900,<0.901',
          'pytest>=6.2.4,<7.0.0',
          'pytest-cov>=2.12.0,<3.0.0']}

setup_kwargs = {
    'name': 'lyght',
    'version': '0.3.0',
    'description': 'Lighting fast python web framework..',
    'long_description': '# light\n\n\n[![pypi](https://img.shields.io/pypi/v/light.svg)](https://pypi.org/project/light/)\n[![python](https://img.shields.io/pypi/pyversions/light.svg)](https://pypi.org/project/light/)\n[![Build Status](https://github.com/SimeonAleksov/light/actions/workflows/dev.yml/badge.svg)](https://github.com/SimeonAleksov/light/actions/workflows/dev.yml)\n[![codecov](https://codecov.io/gh/SimeonAleksov/light/branch/main/graphs/badge.svg)](https://codecov.io/github/SimeonAleksov/light)\n\n\n\nLighting fast python web framework.\n\n\n* Documentation: <https://SimeonAleksov.github.io/light>\n* GitHub: <https://github.com/SimeonAleksov/light>\n* PyPI: <https://pypi.org/project/light/>\n* Free software: MIT\n\n\n## Features\n\n* TODO\n',
    'author': 'Simeon Aleksov',
    'author_email': 'aleksov_s@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/SimeonAleksov/lyght',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
