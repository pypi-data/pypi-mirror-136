# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_urlconfchecks', 'tests']

package_data = \
{'': ['*']}

extras_require = \
{':extra == "dev"': ['django>=3.2.0,<4.0.0'],
 'dev': ['tox>=3.20.1,<4.0.0',
         'virtualenv>=20.2.2,<21.0.0',
         'pip>=20.3.1,<21.0.0',
         'twine>=3.3.0,<4.0.0',
         'pre-commit>=2.12.0,<3.0.0',
         'toml>=0.10.2,<0.11.0',
         'bump2version>=1.0.1,<2.0.0'],
 'doc': ['mkdocs>=1.1.2,<2.0.0',
         'mkdocs-include-markdown-plugin>=3.2.3,<4.0.0',
         'mkdocs-material>=6.1.7,<7.0.0',
         'mkdocstrings>=0.17.0,<0.18.0',
         'mkdocs-autorefs>=0.2.1,<0.3.0'],
 'test': ['black>=21.5b2,<22.0',
          'isort>=5.8.0,<6.0.0',
          'flake8>=4.0.1,<5.0.0',
          'flake8-docstrings>=1.6.0,<2.0.0',
          'mypy>=0.931,<0.932',
          'pytest>=6.2.4,<7.0.0',
          'pytest-cov>=3.0.0,<4.0.0']}

setup_kwargs = {
    'name': 'django-urlconfchecks',
    'version': '0.2.0',
    'description': 'a python package for type checking the urls and associated views.',
    'long_description': '# django-UrlConfChecks\n\n\n[![pypi](https://img.shields.io/pypi/v/django-urlconf-checks.svg)](https://pypi.org/project/django-urlconf-checks/)\n[![python](https://img.shields.io/pypi/pyversions/django-urlconf-checks.svg)](https://pypi.org/project/django-urlconf-checks/)\n[![Build Status](https://github.com/AliSayyah/django-urlconf-checks/actions/workflows/dev.yml/badge.svg)](https://github.com/AliSayyah/django-urlconf-checks/actions/workflows/dev.yml)\n[![codecov](https://codecov.io/gh/AliSayyah/django-urlconf-checks/branch/main/graphs/badge.svg)](https://codecov.io/github/AliSayyah/django-urlconf-checks)\n\n\n\na python package for type checking the urls and associated views\n\n\n* Documentation: <https://AliSayyah.github.io/django-urlconf-checks>\n* GitHub: <https://github.com/AliSayyah/django-urlconf-checks>\n* PyPI: <https://pypi.org/project/django-urlconf-checks/>\n* Free software: MIT\n\n\n## Features\n\n* TODO\n\n## Credits\n\nThis package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [waynerv/cookiecutter-pypackage](https://github.com/waynerv/cookiecutter-pypackage) project template.\n',
    'author': 'ali sayyah',
    'author_email': 'ali.sayyah2@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/AliSayyah/django-urlconfchecks',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.7.0,<4.0',
}


setup(**setup_kwargs)
